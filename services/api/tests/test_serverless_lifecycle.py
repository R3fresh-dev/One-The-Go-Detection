"""Serverless leases and connections cover actual ASGI stream completion."""
import asyncio
import json
from types import SimpleNamespace
from unittest.mock import Mock

import boto3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import pytest

from otgd import capture_signing, config, db, recovery_authority, serverless_lifecycle as lifecycle, storage


def scope(path='/v1/stream'):
    return {'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
            'method': 'GET', 'path': path, 'raw_path': path.encode(), 'query_string': b'',
            'headers': [], 'scheme': 'https', 'server': ('api.otgd.test', 443), 'client': ('127.0.0.1', 1234)}


async def receive():
    return {'type': 'http.request', 'body': b'', 'more_body': False}


def middleware(app, events, **changes):
    def acquire(identity, deadline):
        assert len(identity) == 36 and deadline == 1900
        events.append('acquire')
    return lifecycle.ServerlessLifecycleMiddleware(app,
        config=SimpleNamespace(serverless_mode=True), acquire=acquire,
        dispose=lambda: events.append('dispose'), release=lambda identity: events.append('release'),
        clock=lambda: 1000, **changes)


def test_complete_64_mib_asgi_stream_keeps_lease_until_last_chunk_and_dispose():
    events, sent, checked = [], 0, 0
    async def app(scope, receive, send):
        nonlocal checked
        assert events == ['acquire']
        await send({'type': 'http.response.start', 'status': 200, 'headers': []})
        for index in range(1024):
            # Each delivered 64 KiB remains inside the original authentication
            # boundary. The transport wrapper cannot end the lease early.
            checked += 1
            assert 'dispose' not in events and 'release' not in events
            await send({'type': 'http.response.body', 'body': b'x' * 65536, 'more_body': index < 1023})
        events.append('stream-complete')
    async def send(message):
        nonlocal sent
        if message['type'] == 'http.response.body':
            sent += len(message['body'])
            if sent == 64 * 1024 * 1024:
                assert events[-2:] == ['dispose', 'release']
    asyncio.run(middleware(app, events)(scope(), receive, send))
    assert sent == 64 * 1024 * 1024 and checked == 1024
    assert events == ['acquire', 'stream-complete', 'dispose', 'release']


@pytest.mark.parametrize('failure', ['app', 'disconnect', 'cancel'])
def test_failed_or_cancelled_stream_closes_pool_before_releasing_lease(failure):
    events = []
    async def app(scope, receive, send):
        events.append('sql-committed')
        if failure == 'app':
            raise RuntimeError('private application detail')
        await send({'type': 'http.response.body', 'body': b'chunk', 'more_body': True})
        await send({'type': 'http.response.body', 'body': b'next-chunk', 'more_body': True})
    async def send(message):
        raise asyncio.CancelledError() if failure == 'cancel' else ConnectionError('client disconnected')
    exception = asyncio.CancelledError if failure == 'cancel' else RuntimeError if failure == 'app' else ConnectionError
    with pytest.raises(exception):
        asyncio.run(middleware(app, events)(scope(), receive, send))
    assert events == ['acquire', 'sql-committed', 'dispose', 'release']


def test_lease_acquisition_failure_denies_before_app_and_publishes_no_provider_detail():
    app = Mock()
    messages = []
    def fail(*args):
        raise RuntimeError('private table credential detail')
    wrapper = lifecycle.ServerlessLifecycleMiddleware(app, config=SimpleNamespace(serverless_mode=True),
        acquire=fail, release=Mock(), dispose=Mock())
    async def send(message):
        messages.append(message)
    asyncio.run(wrapper(scope(), receive, send))
    app.assert_not_called()
    wrapper.release.assert_not_called()
    wrapper.dispose.assert_not_called()
    assert messages[0]['status'] == 503
    assert b'private table credential detail' not in b''.join(message.get('body', b'') for message in messages)


def test_dispose_failure_keeps_metadata_lease_conservatively_visible():
    events = []
    async def app(scope, receive, send):
        events.append('complete')
    def fail():
        events.append('dispose-failed')
        raise RuntimeError('pool unavailable')
    release = Mock()
    wrapper = lifecycle.ServerlessLifecycleMiddleware(app, config=SimpleNamespace(serverless_mode=True),
        acquire=lambda *args: events.append('acquire'), dispose=fail, release=release)
    with pytest.raises(RuntimeError):
        asyncio.run(wrapper(scope(), receive, Mock()))
    release.assert_not_called()
    assert events == ['acquire', 'complete', 'dispose-failed']


@pytest.mark.parametrize('path,enabled,type_', [('/health/live', True, 'http'), ('/v1/me', False, 'http'),
                                             ('/', True, 'lifespan')])
def test_legacy_mode_lwa_live_probe_and_non_http_do_not_open_database_or_acquire(path, enabled, type_):
    events = []
    async def app(scope, receive, send):
        events.append('app')
    acquire, dispose, release = Mock(), Mock(), Mock()
    wrapper = lifecycle.ServerlessLifecycleMiddleware(app, config=SimpleNamespace(serverless_mode=enabled),
        acquire=acquire, dispose=dispose, release=release)
    request_scope = scope(path)
    request_scope['type'] = type_
    asyncio.run(wrapper(request_scope, receive, Mock()))
    assert events == ['app']
    acquire.assert_not_called()
    dispose.assert_not_called()
    release.assert_not_called()


def test_dispose_database_never_instantiates_a_missing_engine(monkeypatch):
    engine = Mock()
    engine.cache_info.return_value = SimpleNamespace(currsize=0)
    monkeypatch.setattr(db, 'engine', engine)
    lifecycle.dispose_database()
    engine.assert_not_called()
    engine.cache_info.return_value = SimpleNamespace(currsize=1)
    lifecycle.dispose_database()
    engine.return_value.dispose.assert_called_once_with()


def secret_environment(monkeypatch, *, maintenance=False, region='us-east-2', executor='lambda'):
    monkeypatch.setattr(lifecycle, '_secret_binding', None)
    monkeypatch.setenv('OTGD_SERVERLESS_MODE', 'true')
    monkeypatch.setenv('OTGD_AWS_REGION', region)
    monkeypatch.setenv('OTGD_SERVERLESS_EXECUTOR', executor)
    monkeypatch.setenv('OTGD_DEPLOYMENT_ACCOUNT', '123456789012')
    prefix = f'arn:aws:secretsmanager:{region}:123456789012:secret:'
    monkeypatch.setenv('OTGD_DATABASE_SECRET_ARN', prefix + ('admin' if maintenance else 'app'))
    monkeypatch.setenv('OTGD_TOMBSTONE_SECRET_ARN', prefix + 'tombstone')
    monkeypatch.setenv('OTGD_DATABASE_USER', 'otgd_migrator' if maintenance else 'otgd_app')
    monkeypatch.setenv('OTGD_APP_DATABASE_USER', 'otgd_app')
    if maintenance:
        monkeypatch.setenv('OTGD_APP_DATABASE_SECRET_ARN', prefix + 'app')
    else:
        monkeypatch.delenv('OTGD_APP_DATABASE_SECRET_ARN', raising=False)
    for name in ('OTGD_DATABASE_PASSWORD', 'OTGD_APP_DATABASE_PASSWORD', 'OTGD_TOMBSTONE_KEY'):
        import os
        monkeypatch.setenv(name, os.environ.get(name, ''))
        monkeypatch.delenv(name, raising=False)
    return prefix


@pytest.mark.parametrize('maintenance', [False, True])
@pytest.mark.parametrize('region,executor', [('us-east-2','lambda'),('us-east-2','ecs'),('us-east-1','ecs')])
def test_secret_references_load_atomically_before_settings_and_are_role_separated(monkeypatch, maintenance, capsys, region, executor):
    prefix = secret_environment(monkeypatch, maintenance=maintenance, region=region, executor=executor)
    client = Mock()
    values = {
        prefix + 'app': {'username': 'otgd_app', 'password': 'app-fictional-password'},
        prefix + 'admin': {'username': 'otgd_migrator', 'password': 'admin-fictional-password'},
        prefix + 'tombstone': {'key': 'c' * 64},
    }
    client.get_secret_value.side_effect = lambda **kwargs: {'SecretString': json.dumps(values[kwargs['SecretId']])}
    create = Mock(return_value=client)
    monkeypatch.setattr(lifecycle.boto3, 'client', create)
    lifecycle.load_runtime_secrets()
    import os
    assert os.environ['OTGD_DATABASE_PASSWORD'] == ('admin' if maintenance else 'app') + '-fictional-password'
    assert os.environ['OTGD_TOMBSTONE_KEY'] == 'c' * 64
    if maintenance:
        assert os.environ['OTGD_APP_DATABASE_PASSWORD'] == 'app-fictional-password'
    else:
        assert 'OTGD_APP_DATABASE_PASSWORD' not in os.environ
    call = create.call_args
    assert call.kwargs['endpoint_url'] == f'https://secretsmanager.{region}.amazonaws.com'
    assert call.kwargs['config'].use_dualstack_endpoint is False
    assert call.kwargs['config'].ignore_configured_endpoint_urls is True
    assert capsys.readouterr() == ('', '')
    count = client.get_secret_value.call_count
    lifecycle.load_runtime_secrets()
    assert client.get_secret_value.call_count == count


@pytest.mark.parametrize('region,executor', [('us-east-1','lambda'),('us-west-2','ecs'),('us-east-1','other')])
def test_secret_loader_rejects_unreviewed_region_executor_before_provider_access(monkeypatch, region, executor):
    secret_environment(monkeypatch,region=region,executor=executor)
    create=Mock()
    monkeypatch.setattr(lifecycle.boto3,'client',create)
    with pytest.raises(RuntimeError,match='secret initialization'):
        lifecycle.load_runtime_secrets()
    create.assert_not_called()


@pytest.mark.parametrize('failure', ['foreign-account', 'malformed', 'wrong-user', 'bad-key', 'provider'])
def test_failed_secret_initialization_does_not_publish_partial_password_or_secret_error(monkeypatch, failure):
    prefix = secret_environment(monkeypatch)
    values = [{'username': 'otgd_app', 'password': 'fictional-private-password'}, {'key': 'c' * 64}]
    if failure == 'foreign-account':
        monkeypatch.setenv('OTGD_DATABASE_SECRET_ARN', prefix.replace('123456789012', '987654321098') + 'app')
    elif failure == 'wrong-user':
        values[0]['username'] = 'untrusted-admin'
    elif failure == 'bad-key':
        values[1]['key'] = 'invalid-private-key'
    client = Mock()
    client.get_secret_value.side_effect = ([{'SecretString': json.dumps(value)} for value in values]
        if failure not in ('provider', 'malformed') else RuntimeError('fictional-private-password')
        if failure == 'provider' else [{'SecretString': '{invalid-private-json'}])
    monkeypatch.setattr(lifecycle.boto3, 'client', Mock(return_value=client))
    with pytest.raises(RuntimeError) as caught:
        lifecycle.load_runtime_secrets()
    assert str(caught.value) == 'Serverless runtime secret initialization is unavailable'
    import os
    assert 'OTGD_DATABASE_PASSWORD' not in os.environ
    assert 'OTGD_TOMBSTONE_KEY' not in os.environ


def test_legacy_secret_initialization_is_action_free(monkeypatch):
    monkeypatch.setenv('OTGD_SERVERLESS_MODE', 'false')
    create = Mock()
    monkeypatch.setattr(lifecycle.boto3, 'client', create)
    lifecycle.load_runtime_secrets()
    create.assert_not_called()


def test_maintenance_force_refresh_observes_rotated_admin_secret_without_output(monkeypatch, capsys):
    prefix = secret_environment(monkeypatch, maintenance=True)
    values = {prefix + 'admin': {'username': 'otgd_migrator', 'password': 'initial-admin-password'},
              prefix + 'app': {'username': 'otgd_app', 'password': 'stable-app-password'},
              prefix + 'tombstone': {'key': 'c' * 64}}
    client = Mock()
    client.get_secret_value.side_effect = lambda **kwargs: {'SecretString': json.dumps(values[kwargs['SecretId']])}
    monkeypatch.setattr(lifecycle.boto3, 'client', Mock(return_value=client))
    lifecycle.load_runtime_secrets()
    values[prefix + 'admin']['password'] = 'rotated-admin-password'
    import os
    lifecycle.load_runtime_secrets()
    assert os.environ['OTGD_DATABASE_PASSWORD'] == 'initial-admin-password'
    lifecycle.load_runtime_secrets(force=True)
    assert os.environ['OTGD_DATABASE_PASSWORD'] == 'rotated-admin-password'
    assert client.get_secret_value.call_count == 6
    assert capsys.readouterr() == ('', '')


@pytest.mark.parametrize('enabled,timeout', [(False, 5), (True, 45)])
def test_postgres_connection_timeout_tolerates_resume_only_in_serverless_mode(monkeypatch, enabled, timeout):
    cfg = config.settings().model_copy(update={'database_url': 'postgresql+psycopg://fictional@postgres/otgd',
        'serverless_mode': enabled, 'database_sslmode': 'verify-full', 'database_sslrootcert': '/approved/ca.pem',
        'database_pool_size': 1})
    create = Mock()
    monkeypatch.setattr(db, 'settings', lambda: cfg)
    monkeypatch.setattr(db, 'create_engine', create)
    db.engine.__wrapped__()
    options = create.call_args.kwargs
    assert options['connect_args']['connect_timeout'] == timeout
    assert options['connect_args']['sslmode'] == 'verify-full'
    assert options['pool_size'] == 1 and options['max_overflow'] == 0


def test_service_specific_ipv6_endpoints_preserve_legacy_and_endpoint_guards(monkeypatch):
    session = boto3.Session(aws_access_key_id='fictional', aws_secret_access_key='fictional', region_name='us-east-2')
    monkeypatch.setenv('AWS_ENDPOINT_URL', 'https://untrusted.invalid')
    monkeypatch.setenv('AWS_USE_DUALSTACK_ENDPOINT', 'true')
    supplied = {}
    def create(service, **kwargs):
        supplied[service] = kwargs['config']
        return session.client(service, **kwargs)
    monkeypatch.setattr(storage.boto3, 'client', create)
    expected = {'s3': 's3.dualstack.us-east-2.amazonaws.com', 'sqs': 'sqs.us-east-2.api.aws',
                'kms': 'kms.us-east-2.api.aws', 'cloudwatch': 'monitoring.us-east-2.api.aws',
                'sts': 'sts.us-east-2.api.aws', 'lambda': 'lambda.us-east-2.api.aws',
                'dynamodb': 'dynamodb.us-east-2.api.aws', 'secretsmanager': 'secretsmanager.us-east-2.amazonaws.com',
                'cognito-idp': 'cognito-idp.us-east-2.amazonaws.com'}
    cfg = config.settings().model_copy(update={'serverless_mode': True, 'aws_endpoint_url': None,
                                              's3_public_endpoint_url': None})
    monkeypatch.setattr(storage, 'settings', lambda: cfg)
    storage.client.cache_clear()
    try:
        for service, host in expected.items():
            client = storage.client(service)
            assert client.meta.endpoint_url == 'https://' + host
            assert supplied[service].ignore_configured_endpoint_urls is True
        monkeypatch.setattr(storage, 'settings', lambda: cfg.model_copy(update={'serverless_mode': False}))
        storage.client.cache_clear()
        assert storage.client('s3').meta.endpoint_url == 'https://s3.us-east-2.amazonaws.com'
    finally:
        storage.client.cache_clear()


def test_independent_journal_client_keeps_its_deadline_with_ipv6(monkeypatch):
    cfg = config.settings().model_copy(update={'serverless_mode': True, 'environment': 'qa', 'aws_endpoint_url': None})
    monkeypatch.setattr(config, 'settings', lambda: cfg)
    create = Mock()
    monkeypatch.setattr(boto3, 'client', create)
    recovery_authority.authority_client.cache_clear()
    try:
        recovery_authority.authority_client()
        options = create.call_args.kwargs['config']
        assert options.use_dualstack_endpoint is True
        assert options.ignore_configured_endpoint_urls is True
        assert options.connect_timeout == options.read_timeout == 1
        assert options.retries['max_attempts'] == 0
    finally:
        recovery_authority.authority_client.cache_clear()


def test_serverless_capture_signer_keeps_real_material_checks_on_ipv6(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    key_id = 'arn:aws:kms:us-east-2:123456789012:key/00000000-0000-4000-8000-000000000001'
    cfg = SimpleNamespace(serverless_mode=True, aws_region='us-east-2', deployment_account='123456789012',
                          capture_signing_key_id=key_id)
    client = Mock()
    client.get_public_key.return_value = {'KeyId': key_id, 'KeySpec': 'ECC_NIST_P256', 'KeyUsage': 'SIGN_VERIFY',
        'SigningAlgorithms': ['ECDSA_SHA_256'], 'PublicKey': key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)}
    create = Mock(return_value=client)
    monkeypatch.setattr(capture_signing.boto3, 'client', create)
    capture_signing.cloud_key(cfg)
    assert create.call_args.kwargs['endpoint_url'] == 'https://kms.us-east-2.api.aws'
    assert create.call_args.kwargs['config'].ignore_configured_endpoint_urls is True
    assert create.call_args.kwargs['config'].use_dualstack_endpoint is True


@pytest.mark.parametrize('method,status,kicked', [('POST', 202, True), ('PATCH', 200, True),
    ('PUT', 200, True), ('DELETE', 204, True), ('POST', 422, False), ('GET', 200, False)])
def test_only_successful_mutations_kick_private_dispatch_before_http_start(method, status, kicked):
    events = []
    async def app(scope, receive, send):
        events.append('sql-committed')
        await send({'type': 'http.response.start', 'status': status, 'headers': []})
        await send({'type': 'http.response.body', 'body': b'{}' if status != 204 else b'', 'more_body': False})
    async def send(message):
        if message['type'] == 'http.response.start':
            events.append('http-start')
    wrapper = middleware(app, events, kick=lambda: events.append('kick-accepted'))
    request = scope()
    request['method'] = method
    asyncio.run(wrapper(request, receive, send))
    assert ('kick-accepted' in events) is kicked
    assert events.index('sql-committed') < events.index('http-start')
    if kicked:
        assert events.index('kick-accepted') < events.index('http-start')
    if status == 204:
        assert events.index('release') < events.index('http-start')


def test_dispatch_failure_retains_committed_work_and_returns_retryable_error_after_cleanup():
    events, messages = [], []
    async def app(scope, receive, send):
        events.append('sql-committed')
        await send({'type': 'http.response.start', 'status': 202, 'headers': []})
        await send({'type': 'http.response.body', 'body': b'{"job_id":"private-id"}', 'more_body': False})
    def kick():
        raise RuntimeError('private provider detail')
    async def send(message):
        assert events[-2:] == ['dispose', 'release']
        messages.append(message)
    request = scope()
    request['method'] = 'POST'
    asyncio.run(middleware(app, events, kick=kick)(request, receive, send))
    assert messages[0]['status'] == 503
    assert events == ['acquire', 'sql-committed', 'dispose', 'release']
    body = b''.join(message.get('body', b'') for message in messages)
    assert b'private-id' not in body and b'private provider detail' not in body


@pytest.mark.parametrize('status,method,headers', [(204, 'GET', []), (304, 'GET', []),
                                                 (200, 'HEAD', []), (200, 'GET', [(b'content-length', b'0')])])
def test_empty_response_cannot_complete_before_database_and_lease_cleanup(status, method, headers):
    events = []
    async def app(scope, receive, send):
        await send({'type': 'http.response.start', 'status': status, 'headers': headers})
        assert events == ['acquire']
        await send({'type': 'http.response.body', 'body': b'', 'more_body': False})
    async def send(message):
        assert events == ['acquire', 'dispose', 'release']
    request = scope()
    request['method'] = method
    asyncio.run(middleware(app, events)(request, receive, send))


@pytest.mark.parametrize('status', [202, 200])
def test_dispatch_invocation_requires_actual_async_acceptance(monkeypatch, status):
    arn = 'arn:aws:lambda:us-east-2:123456789012:function:otgd-serverless-dispatcher'
    monkeypatch.setattr(config, 'settings', lambda: SimpleNamespace(serverless_dispatch_function_arn=arn))
    client = Mock()
    client.invoke.return_value = {'StatusCode': status}
    monkeypatch.setattr(storage, 'client', lambda service: client if service == 'lambda' else pytest.fail('Wrong service'))
    if status == 202:
        lifecycle.kick_dispatcher()
    else:
        with pytest.raises(RuntimeError, match='not accepted'):
            lifecycle.kick_dispatcher()
    assert client.invoke.call_args.kwargs == {'FunctionName': arn, 'InvocationType': 'Event',
                                             'Payload': b'{"operation":"dispatch"}'}


def test_serverless_configuration_requires_real_control_resume_and_queue_bounds():
    values = {'environment': 'qa', 'deployment_account': '123456789012', 'source_revision': 'a' * 40,
        'serverless_mode': True, 'serverless_control_table': 'otgd-serverless-control',
        'serverless_queue_visibility': 1200, 'database_sslmode': 'verify-full',
        'database_sslrootcert': '/approved/rds-ca.pem', 'database_pool_size': 1,
        'issuer': 'https://cognito-idp.us-east-2.amazonaws.com/pool', 'jwks_url': 'https://cognito-idp.us-east-2.amazonaws.com/pool/keys',
        'api_origin': 'https://api.execute-api.us-east-2.amazonaws.com', 'identity_origin': 'https://identity.auth.us-east-2.amazoncognito.com',
        'journal_kms_key_id': 'journal-key', 'storage_kms_key_id': 'data-key', 'tombstone_key': 'f' * 64,
        'user_pool_id': 'pool', 'queue_url': 'https://sqs.us-east-2.amazonaws.com/account/jobs',
        'dlq_url': 'https://sqs.us-east-2.amazonaws.com/account/dlq'}
    accepted = config.Settings(**values)
    assert accepted.serverless_database_connect_timeout == 45
    for change in ({'serverless_control_table': None}, {'serverless_queue_visibility': 119},
                   {'serverless_database_connect_timeout': 5}, {'aws_region': 'us-west-2'},
                   {'serverless_dispatch_function_arn': 'arn:aws:lambda:us-east-2:987654321098:function:foreign'}):
        with pytest.raises(ValueError):
            config.Settings(**{**values, **change})
    with pytest.raises(ValueError):
        config.Settings(serverless_queue_visibility=1200, environment='test')


def test_serverless_settings_validation_cannot_dump_loaded_password_values(monkeypatch):
    monkeypatch.setenv('OTGD_SERVERLESS_MODE', 'true')
    monkeypatch.setattr(lifecycle, 'load_runtime_secrets', lambda: None)
    monkeypatch.setattr(config, 'Settings', Mock(side_effect=ValueError('private-loaded-password')))
    config.settings.cache_clear()
    try:
        with pytest.raises(RuntimeError) as caught:
            config.settings()
        assert str(caught.value) == 'Serverless runtime configuration is unavailable'
        assert caught.value.__suppress_context__ is True
    finally:
        config.settings.cache_clear()
