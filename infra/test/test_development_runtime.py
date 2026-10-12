"""Development packaging and host lifecycle refuse unsafe/incomplete inputs."""
import ast
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import Mock

from deploy import development_runtime as runtime


def fixture():
    config = {'account': '123456789012', 'region': 'us-east-2', 'releaseId': 'a' * 40,
              'monthlyBudgetUsd': 50, 'alarmEmail': 'operator@otgd.test'}
    outputs = {'ApiOrigin': 'https://api123.cloudfront.net', 'WebOrigin': 'https://web123.cloudfront.net',
               'IdentityOrigin': 'https://otgd-development.auth.us-east-2.amazoncognito.com',
               'Issuer': 'https://cognito-idp.us-east-2.amazonaws.com/us-east-2_pool',
               'UserPoolId': 'us-east-2_pool', 'ClientId': 'client-id', 'ArtifactBucket': 'dev-artifacts',
               'ExportBucket': 'dev-exports', 'JournalBucket': 'dev-journal',
               'QueueUrl': 'https://sqs.us-east-2.amazonaws.com/123456789012/dev-jobs',
               'DeadLetterQueueUrl': 'https://sqs.us-east-2.amazonaws.com/123456789012/dev-dlq',
               'EC2PrimaryPrivateIp': '10.74.1.25', 'LogGroup': '/otgd-development/application',
               'RuntimeSecretArn': 'arn:aws:secretsmanager:us-east-2:123456789012:secret:runtime-abcdef',
               'DeploymentBucket': 'dev-deployment-assets', 'InstanceId': 'i-0123456789abcdef0'}
    for index, name in enumerate(('DataKeyArn', 'JournalKeyArn', 'CaptureSigningKeyArn')):
        outputs[name] = 'arn:aws:kms:us-east-2:123456789012:key/' + str(index) * 8 + '-1234-1234-1234-123456789abc'
    return config, outputs


def source_archive(path, extra=None):
    with tarfile.open(path, 'w', pax_headers={'comment': 'a' * 40}) as bundle:
        for name in ('services/api/pyproject.toml', 'services/api/uv.lock', 'infra/local/service.Dockerfile'):
            raw = b'locked-reviewed-input\n'
            member = tarfile.TarInfo(name)
            member.size = len(raw)
            bundle.addfile(member, io.BytesIO(raw))
        if extra is not None:
            if isinstance(extra, str):
                extra = tarfile.TarInfo(extra)
            bundle.addfile(extra)


def host_functions(names, namespace):
    """Load only selected generated functions; never execute its host entrypoint."""
    tree = ast.parse(runtime.HOST_RUNNER)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<generated-host-functions>', 'exec'), namespace)
    return namespace


class DevelopmentRuntimeTests(unittest.TestCase):
    def test_runtime_uses_actual_cloud_settings_and_verified_database_tls(self):
        config, outputs = fixture()
        env = runtime.runtime_environment(config, outputs)
        self.assertEqual(env['OTGD_ENVIRONMENT'], 'qa')
        self.assertEqual(env['OTGD_API_ORIGIN'], outputs['ApiOrigin'])
        self.assertEqual(env['OTGD_DATABASE_SSLMODE'], 'verify-full')
        self.assertEqual(env['OTGD_DATABASE_SSLROOTCERT'], '/run/otgd-tls/ca.crt')
        self.assertEqual(json.loads(env['OTGD_OAUTH_REDIRECT_URIS']),
                         ['otgd-qa://oauth/callback', outputs['WebOrigin'] + '/'])
        self.assertNotIn('AWS_ACCESS_KEY_ID', env)
        self.assertNotIn('OTGD_DATABASE_PASSWORD', env)
        self.assertNotIn('OTGD_AWS_ENDPOINT_URL', env)
        # Verify compatibility with the existing backend validator, without AWS.
        from otgd.config import Settings
        values = {key.removeprefix('OTGD_').lower(): value for key, value in env.items() if key.startswith('OTGD_')}
        values['oauth_redirect_uris'] = json.loads(values['oauth_redirect_uris'])
        values.update(tombstone_key='b' * 64, database_password='c' * 64)
        settings = Settings(**values)
        self.assertEqual(settings.database_host, 'postgres')
        self.assertEqual(settings.deployment_account, config['account'])

    def test_compose_keeps_database_private_and_prevents_reboot_before_admission(self):
        config, outputs = fixture()
        services = runtime.compose_spec(config, outputs)['services']
        self.assertEqual(set(services), {'postgres', 'api', 'worker', 'metrics', 'maintenance'})
        self.assertEqual(services['api']['ports'], ['10.74.1.25:8000:8000'])
        self.assertNotIn('ports', services['postgres'])
        self.assertIn('@sha256:', services['postgres']['image'])
        self.assertIn('ssl=on', services['postgres']['command'])
        for name in ('api', 'worker', 'metrics'):
            self.assertEqual(services[name]['restart'], 'on-failure:5')
            self.assertTrue(services[name]['read_only'])
        self.assertEqual(services['maintenance']['profiles'], ['maintenance'])
        self.assertEqual(services['maintenance']['environment']['OTGD_DATABASE_USER'], 'otgd_migrator')

    def test_wrong_region_revision_tls_origin_key_account_and_private_ip_refuse(self):
        config, outputs = fixture()
        for changed in ({**config, 'region': 'us-west-2'}, {**config, 'releaseId': 'main'}):
            with self.assertRaises(ValueError):
                runtime.compose_spec(changed, outputs)
        for field, value in (('ApiOrigin', 'http://localhost:8000'),
                             ('JournalKeyArn', outputs['DataKeyArn']),
                             ('CaptureSigningKeyArn', outputs['CaptureSigningKeyArn'].replace(config['account'], '987654321098')),
                             ('EC2PrimaryPrivateIp', '8.8.8.8')):
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.compose_spec(config, {**outputs, field: value})

    def test_package_is_deterministic_bounded_and_contains_no_secret_envfiles(self):
        config, outputs = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / 'source.tar'
            source_archive(source)
            first = runtime.package_runtime(directory / 'first.tgz', config, outputs, source, establish_new=True)
            second = runtime.package_runtime(directory / 'second.tgz', config, outputs, source, establish_new=True)
            self.assertEqual(first['sha256'], second['sha256'])
            self.assertEqual(first['source_sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
            with tarfile.open(first['path']) as bundle:
                self.assertNotIn('app.env', bundle.getnames())
                self.assertNotIn('postgres.env', bundle.getnames())
                manifest = json.load(bundle.extractfile('runtime.json'))
                self.assertTrue(manifest['establish_new'])
                self.assertNotIn('seed', manifest)
                self.assertEqual(manifest['secret_arn'], outputs['RuntimeSecretArn'])
                compile(bundle.extractfile('runtime.py').read(), '<host-runner>', 'exec')
            self.assertEqual(os.stat(first['path']).st_mode & 0o777, 0o600)

    def test_archive_traversal_symlinks_and_local_configuration_refuse(self):
        config, outputs = fixture()
        symlink = tarfile.TarInfo('services/api/link')
        symlink.type, symlink.linkname = tarfile.SYMTYPE, '/etc/shadow'
        for extra in ('../../outside', '.local/private.pem', 'infra/config/qa.local.json', symlink):
            with self.subTest(extra=str(extra)), tempfile.TemporaryDirectory() as temporary:
                source = Path(temporary) / 'source.tar'
                source_archive(source, extra)
                with self.assertRaises(ValueError):
                    runtime.package_runtime(Path(temporary) / 'runtime.tgz', config, outputs, source)

    def test_safe_tracked_file_symlink_passes_but_archive_revision_mismatch_refuses(self):
        config, outputs = fixture()
        symlink = tarfile.TarInfo('services/api/copy.lock')
        symlink.type, symlink.linkname = tarfile.SYMTYPE, 'uv.lock'
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'source.tar'
            source_archive(source, symlink)
            runtime.package_runtime(Path(temporary) / 'runtime.tgz', config, outputs, source)
            with self.assertRaises(ValueError):
                runtime.package_runtime(Path(temporary) / 'other.tgz',
                                        {**config, 'releaseId': 'e' * 40}, outputs, source)

    def test_startup_is_valid_shell_and_requires_trusted_package_hash(self):
        script = runtime.startup_script('us-east-2', '123456789012', 'dev-deployment-assets',
                                        "runtime/a'quoted.tar.gz", 'c' * 64)
        result = subprocess.run(['bash', '-n'], input=script, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(runtime.COMPOSE_SHA256, script)
        self.assertIn('sha256sum --check --status', script)
        self.assertNotIn('set -x', script)
        self.assertNotIn('--no-verify-ssl', script)
        self.assertIn('systemctl stop otgd-development.service', script)
        self.assertNotIn('docker compose down', script)
        with self.assertRaises(ValueError):
            runtime.startup_script('us-east-2', '123456789012', 'dev-deployment-assets', 'runtime/file', 'untrusted')

    def test_generated_host_aws_accepts_empty_success_without_fabricating_get_results(self):
        namespace = host_functions({'aws'}, {'json': json, 'CONFIG': {'region': 'us-east-2'},
                                            'invoke': Mock(return_value='')})
        self.assertEqual(namespace['aws']('cloudwatch', 'put-metric-data'), {})
        namespace['invoke'].return_value = '{"Account":"123456789012"}'
        self.assertEqual(namespace['aws']('sts', 'get-caller-identity')['Account'], '123456789012')

    def test_host_fetches_separate_derived_secrets_before_first_compose_call(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            events = []
            namespace = host_functions({'private_write', 'secrets', 'start'}, {
                'os': os, 'json': json, 'hashlib': hashlib, 'ROOT': root, 'DATA': root,
                'CONFIG': {'account': '123456789012', 'secret_arn': 'secret-id'},
                'aws': Mock(side_effect=[{'Account': '123456789012'}, {'SecretString': json.dumps({'seed': 'd' * 64})}]),
                'stage': lambda name, operation: (events.append(name), operation())[1],
                'compose': lambda *args, **kw: events.append('compose-' + args[0]),
                'build': lambda: None, 'tls': lambda: None, 'maintenance': lambda op: None,
                'observe': lambda: {}, 'state': lambda *args, **kw: {'status': args[0]}})
            namespace['start']()
            self.assertEqual(events[0], 'fetch-runtime-secrets')
            self.assertEqual(events[1], 'compose-stop')
            for name in ('postgres.env', 'app.env', 'maintenance.env'):
                self.assertEqual((root / name).stat().st_mode & 0o777, 0o600)
            app = (root / 'app.env').read_text().splitlines()
            self.assertNotEqual(app[0].split('=')[1], app[1].split('=')[1])
            self.assertNotIn('d' * 64, '\n'.join(path.read_text() for path in root.glob('*.env')))
            self.assertLess(events.index('verify-independent-admission'), events.index('activate-runtime'))

    def test_retained_journal_sentinel_prevents_establish_new_on_repeat(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary)
            compose = Mock(return_value='')
            namespace = host_functions({'maintenance'}, {
                'DATA': data, 'CONFIG': {'establish_new': True, 'release_id': 'a' * 40},
                'compose': compose, 'json': json, 'datetime': datetime, 'timezone': timezone,
                'private_write': lambda path, raw: Path(path).write_text(raw)})
            namespace['maintenance']('journal')
            self.assertIn('--establish-new', compose.call_args.args)
            namespace['maintenance']('journal')
            self.assertNotIn('--establish-new', compose.call_args.args)
            namespace['maintenance']('admission')
            self.assertEqual(compose.call_args.args[-1], 'otgd.recovery_authority')

    def test_host_metric_values_use_real_memory_disk_and_correct_dimensions(self):
        with tempfile.TemporaryDirectory() as temporary:
            aws = Mock(return_value={})
            namespace = host_functions({'host_metrics'}, {'Path': Path, 'os': os, 'json': json,
                'DATA': Path(temporary), 'CONFIG': {'instance_id': 'i-0123456789abcdef0'}, 'aws': aws})
            self.assertEqual(namespace['host_metrics']()['status'], 'published')
            args = aws.call_args.args
            self.assertEqual(args[:4], ('cloudwatch', 'put-metric-data', '--namespace', 'OTGD/development'))
            metrics = json.loads(args[-1])
            self.assertEqual({row['MetricName'] for row in metrics}, {'MemoryUsedPercent', 'DiskUsedPercent'})
            for row in metrics:
                self.assertGreaterEqual(row['Value'], 0)
                self.assertLessEqual(row['Value'], 100)
                self.assertEqual(row['Dimensions'], [{'Name': 'InstanceId', 'Value': 'i-0123456789abcdef0'}])

    def test_backup_requires_versioning_and_actual_retained_checksum_upload(self):
        for versioning, version in (('Enabled', 'retained-version'), ('Suspended', 'retained-version'), ('Enabled', 'null')):
            with self.subTest(versioning=versioning, version=version), tempfile.TemporaryDirectory() as temporary:
                data = Path(temporary)
                process = Mock()
                def dump(command, **options):
                    options['stdout'].write(b'PGDMPfictional-test-only')
                    return Mock(returncode=0)
                process.run.side_effect = dump
                process.PIPE = subprocess.PIPE
                aws = Mock(side_effect=[{'Status': versioning}, {'VersionId': version}])
                namespace = host_functions({'backup'}, {'DATA': data, 'ROOT': data, 'CONFIG': {'backup_bucket': 'dev-deployment-assets'},
                    'subprocess': process, 'aws': aws, 'os': os, 'datetime': datetime, 'timezone': timezone,
                    'json': json, 'base64': base64, 'hashlib': hashlib,
                    'private_write': lambda path, raw: Path(path).write_text(raw)})
                if versioning == 'Enabled' and version != 'null':
                    result = namespace['backup']()
                    self.assertEqual(result['version_id'], version)
                    self.assertIn('--checksum-sha256', aws.call_args.args)
                    self.assertEqual(json.loads((data / 'backup-state.json').read_text())['version_id'], version)
                    self.assertNotIn('fictional-test-only', json.dumps(result))
                else:
                    with self.assertRaises(RuntimeError):
                        namespace['backup']()
                    self.assertFalse((data / 'backup-state.json').exists())


if __name__ == '__main__':
    unittest.main()
