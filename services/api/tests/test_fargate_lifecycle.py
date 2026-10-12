"""ECS HTTP leases and connection closure; AWS admission is tested separately."""
import asyncio
import json
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from otgd import config, db
from otgd import serverless_lifecycle as lifecycle
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def cloud_values():
    account='123456789012'
    return {'environment':'qa','deployment_account':account,'source_revision':'a'*40,
        'serverless_mode':True,'serverless_executor':'ecs','serverless_control_table':'otgd-serverless-development-control',
        'serverless_queue_visibility':1200,'database_sslmode':'verify-full','database_sslrootcert':'/approved/rds-ca.pem',
        'issuer':'https://cognito-idp.us-east-2.amazonaws.com/pool','jwks_url':'https://cognito-idp.us-east-2.amazonaws.com/pool/keys',
        'api_origin':'https://api.otgd.test','identity_origin':'https://identity.auth.us-east-2.amazoncognito.com',
        'journal_kms_key_id':'journal-key','storage_kms_key_id':'data-key','tombstone_key':'f'*64,
        'user_pool_id':'pool','queue_url':'https://sqs.us-east-2.amazonaws.com/'+account+'/jobs',
        'dlq_url':'https://sqs.us-east-2.amazonaws.com/'+account+'/dlq',
        'ecs_cluster_arn':'arn:aws:ecs:us-east-2:'+account+':cluster/otgd-serverless-development',
        'ecs_worker_task_definition_arn':'arn:aws:ecs:us-east-2:'+account+':task-definition/otgd-serverless-development-worker:7',
        'ecs_subnet_ids':['subnet-0123456789abcdef0','subnet-1123456789abcdef0'],
        'ecs_security_group_ids':['sg-0123456789abcdef0']}


def request(path='/v1/export', method='GET'):
    return {'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':method,
        'path':path,'raw_path':path.encode(),'query_string':b'','headers':[],'scheme':'https',
        'server':('api.otgd.test',443),'client':('127.0.0.1',1234)}


async def receive():
    return {'type':'http.request','body':b'','more_body':False}


def test_ecs_configuration_reads_json_network_and_needs_no_lambda_target(monkeypatch):
    values=cloud_values()
    for name in ('ecs_subnet_ids','ecs_security_group_ids'):
        monkeypatch.setenv('OTGD_'+name.upper(),json.dumps(values.pop(name)))
    actual=config.Settings(**values)
    assert actual.serverless_executor=='ecs' and actual.serverless_dispatch_function_arn is None
    assert len(actual.ecs_subnet_ids)==2 and len(actual.ecs_security_group_ids)==1
    # Workers/admin maintenance receive no launch target, avoiding both a
    # self-referencing task definition and unnecessary launch authority.
    minimal={key:value for key,value in values.items() if not key.startswith('ecs_')}
    assert config.Settings(**minimal).ecs_worker_task_definition_arn is None


@pytest.mark.parametrize('field,value',[
    ('serverless_executor','other'),('serverless_mode',False),
    ('ecs_cluster_arn','arn:aws:ecs:us-east-2:987654321098:cluster/otgd-serverless-development'),
    ('ecs_cluster_arn','arn:aws:ecs:us-west-2:123456789012:cluster/otgd-serverless-development'),
    ('ecs_cluster_arn','arn:aws:ecs:us-east-2:123456789012:cluster/foreign'),
    ('ecs_cluster_arn','arn:aws:ecs:us-east-2:123456789012:cluster/otgd-serverless-development-neighbor'),
    ('ecs_worker_task_definition_arn','arn:aws:ecs:us-east-2:987654321098:task-definition/otgd-serverless-development-worker:7'),
    ('ecs_worker_task_definition_arn','arn:aws:ecs:us-west-2:123456789012:task-definition/otgd-serverless-development-worker:7'),
    ('ecs_worker_task_definition_arn','arn:aws:ecs:us-east-2:123456789012:task-definition/otgd-serverless-development-maintenance:7'),
    ('ecs_worker_task_definition_arn','arn:aws:ecs:us-east-2:123456789012:task-definition/otgd-serverless-development-worker'),
    ('ecs_worker_task_definition_arn','arn:aws:ecs:us-east-2:123456789012:task-definition/otgd-serverless-development-worker:*'),
    ('ecs_worker_task_definition_arn','arn:aws:ecs:us-east-2:123456789012:task-definition/otgd-serverless-development-worker:0'),
    ('ecs_subnet_ids',['subnet-0123456789abcdef0']*2),
    ('ecs_subnet_ids',['subnet-'+format(index,'017x') for index in range(17)]),
    ('ecs_subnet_ids',['subnet-123456789']),('ecs_subnet_ids',['sg-0123456789abcdef0']),
    ('ecs_security_group_ids',['sg-0123456789abcdef0']*2),
    ('ecs_security_group_ids',['sg-'+format(index,'017x') for index in range(6)]),
    ('ecs_security_group_ids',['sg-ABCDEF12']),('ecs_security_group_ids',['sg-01234567; command']),
])
def test_ecs_configuration_rejects_foreign_targets_and_unbounded_network(field,value):
    with pytest.raises(ValueError):
        config.Settings(**{**cloud_values(),field:value})


def test_ecs_postgresql_engine_uses_nullpool_without_queuepool_arguments(monkeypatch):
    cfg=config.Settings(**cloud_values()).model_copy(update={'database_url':'postgresql+psycopg://fictional@postgres/otgd'})
    monkeypatch.setattr(db,'settings',lambda:cfg)
    created=Mock()
    monkeypatch.setattr(db,'create_engine',created)
    db.engine.__wrapped__()
    options=created.call_args.kwargs
    assert options['poolclass'] is NullPool
    assert not {'pool_size','pool_timeout','max_overflow'}&set(options)
    assert options['connect_args']=={'connect_timeout':45,'sslmode':'verify-full','sslrootcert':'/approved/rds-ca.pem'}


def test_nullpool_closes_real_connections_after_commit_and_rollback(tmp_path):
    # Real SQLite DBAPI connections establish SQLAlchemy's NullPool behavior;
    # this is not substituted for the separate PostgreSQL live gate.
    engine=create_engine('sqlite:///'+str(tmp_path/'connections.sqlite'),poolclass=NullPool)
    sessions=sessionmaker(bind=engine)
    events=[]
    event.listen(engine,'connect',lambda connection,record:events.append('connect'))
    event.listen(engine,'close',lambda connection,record:events.append('close'))
    for abort in (False,True):
        try:
            with sessions.begin() as session:
                assert session.execute(text('SELECT 1')).scalar_one()==1
                if abort:
                    raise RuntimeError('rollback')
        except RuntimeError:
            assert abort
        assert events==['connect','close']*(2 if abort else 1)
    engine.dispose()


@pytest.mark.parametrize('accepted',[True,False])
def test_ecs_dispatch_uses_only_guarded_task_launch(monkeypatch,accepted):
    launcher=Mock(return_value=accepted)
    monkeypatch.setitem(sys.modules,'otgd.fargate_runtime',SimpleNamespace(request_worker_launch=launcher))
    monkeypatch.setattr(config,'settings',lambda:SimpleNamespace(serverless_executor='ecs'))
    from otgd import storage
    aws=Mock(side_effect=AssertionError('API lifecycle must not invoke Lambda for ECS'))
    monkeypatch.setattr(storage,'client',aws)
    if accepted:
        lifecycle.kick_dispatcher()
    else:
        with pytest.raises(RuntimeError,match='not accepted'):
            lifecycle.kick_dispatcher()
    launcher.assert_called_once_with()
    aws.assert_not_called()


def test_ecs_launch_refusal_preserves_committed_work_and_releases_lease_before_503(tmp_path):
    events,messages=[],[]
    engine=create_engine('sqlite:///'+str(tmp_path/'committed.sqlite'),poolclass=NullPool)
    with engine.begin() as connection:
        connection.execute(text('CREATE TABLE durable_jobs (id INTEGER PRIMARY KEY)'))
    async def app(scope,receive,send):
        with engine.begin() as connection:
            connection.execute(text('INSERT INTO durable_jobs (id) VALUES (1)'))
        events.append('committed')
        await send({'type':'http.response.start','status':202,'headers':[]})
        pytest.fail('Launch refusal must stop the success response')
    def launch():
        assert events[-1]=='committed'
        events.append('launch-refused')
        raise RuntimeError('private ECS provider detail')
    async def send(message):
        assert events[-1]=='released'
        messages.append(message)
    dispose=Mock()
    wrapper=lifecycle.ServerlessLifecycleMiddleware(app,config=SimpleNamespace(serverless_mode=True,serverless_executor='ecs'),
        acquire=lambda *args:events.append('acquired'),release=lambda identity:events.append('released'),dispose=dispose,kick=launch)
    asyncio.run(wrapper(request(method='POST'),receive,send))
    assert events==['acquired','committed','launch-refused','released']
    assert messages[0]['status']==503
    assert b'private ECS provider detail' not in b''.join(message.get('body',b'') for message in messages)
    dispose.assert_not_called()
    with engine.begin() as connection:
        assert connection.execute(text('SELECT COUNT(*) FROM durable_jobs')).scalar_one()==1
    engine.dispose()


def test_concurrent_ecs_64_mib_streams_close_each_readmission_without_global_disposal(tmp_path):
    engine=create_engine('sqlite:///'+str(tmp_path/'streams.sqlite'),poolclass=NullPool)
    sessions=sessionmaker(bind=engine)
    opened,closed=0,0
    def connected(connection,record):
        nonlocal opened
        opened+=1
    def disconnected(connection,record):
        nonlocal closed
        closed+=1
    event.listen(engine,'connect',connected)
    event.listen(engine,'close',disconnected)
    active=set()
    release_count=[]
    checks={'/first':0,'/second':0}
    sent={'/first':0,'/second':0}
    dispose=Mock()
    async def run():
        first_paused,second_done=asyncio.Event(),asyncio.Event()
        async def app(scope,receive,send):
            path=scope['path']
            if path=='/second':
                await first_paused.wait()
            await send({'type':'http.response.start','status':200,'headers':[]})
            for index in range(1024):
                # Match export readmission: authenticate in a transaction,
                # commit/close before disclosing each bounded 64 KiB chunk.
                with sessions.begin() as session:
                    assert session.execute(text('SELECT 1')).scalar_one()==1
                checks[path]+=1
                assert opened==closed
                await send({'type':'http.response.body','body':b'x'*65536,'more_body':index<1023})
                if path=='/first' and index==1:
                    first_paused.set()
                    await second_done.wait()
        def acquire(identity,deadline):
            active.add(identity)
        def release(identity):
            assert opened==closed
            active.remove(identity)
            release_count.append(len(active))
        wrapper=lifecycle.ServerlessLifecycleMiddleware(app,config=SimpleNamespace(serverless_mode=True,serverless_executor='ecs'),
            acquire=acquire,release=release,dispose=dispose)
        async def one(path):
            async def send(message):
                if message['type']=='http.response.body':
                    sent[path]+=len(message['body'])
                    if not message.get('more_body',False) and path=='/second':
                        assert len(active)==1  # Completing one stream keeps the other lease.
                        second_done.set()
            await wrapper(request(path),receive,send)
        await asyncio.gather(one('/first'),one('/second'))
    asyncio.run(run())
    assert checks=={'/first':1024,'/second':1024}
    assert sent=={'/first':64*1024*1024,'/second':64*1024*1024}
    assert opened==closed==2048 and active==set() and release_count==[1,0]
    dispose.assert_not_called()
    engine.dispose()


@pytest.mark.parametrize('failure',[RuntimeError,asyncio.CancelledError])
def test_ecs_cancelled_or_failed_request_releases_lease_after_session_close(tmp_path,failure):
    engine=create_engine('sqlite:///'+str(tmp_path/'failed.sqlite'),poolclass=NullPool)
    sessions=sessionmaker(bind=engine)
    events=[]
    event.listen(engine,'close',lambda connection,record:events.append('connection-closed'))
    async def app(scope,receive,send):
        with sessions.begin() as session:
            session.execute(text('SELECT 1'))
            raise failure()
    dispose=Mock()
    wrapper=lifecycle.ServerlessLifecycleMiddleware(app,config=SimpleNamespace(serverless_mode=True,serverless_executor='ecs'),
        acquire=lambda *args:events.append('acquired'),release=lambda identity:events.append('released'),dispose=dispose)
    with pytest.raises(failure):
        asyncio.run(wrapper(request(),receive,Mock()))
    assert events==['acquired','connection-closed','released']
    dispose.assert_not_called()
    engine.dispose()
