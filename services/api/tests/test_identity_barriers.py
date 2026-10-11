"""No identity reuse under secret replacement; narrow own-deletion receipts only."""
from uuid import uuid4
import pytest
from otgd.config import settings
from otgd.db import Account,Job,Revocation,SystemState,factory,now
from otgd.auth import family_hash
from otgd.identity_keys import KEY_STATE,key_descriptor
from otgd.migrate import migrate
from .conftest import headers

def test_same_label_changed_secret_cannot_reprovision_deleted_subject(client,account,monkeypatch):
    with factory().begin() as db:
        row=db.get(Account,account);row.state='deleted';row.generation=2
    monkeypatch.setattr(settings(),'tombstone_key','36'*32)
    denied=client.get('/v1/me/capabilities',headers=headers())
    assert denied.status_code==503 and denied.json()['code']=='IDENTITY_KEY_VERSION_UNAVAILABLE'
    assert client.get('/health/ready').status_code==503
    with factory()() as db:
        assert db.query(Account).count()==1
        assert db.get(Account,account).state=='deleted'
    with pytest.raises(RuntimeError,match='replacement'):migrate()

def test_missing_provenance_cannot_be_guessed_for_existing_accounts(client,account):
    with factory().begin() as db:db.delete(db.get(SystemState,KEY_STATE))
    assert client.get('/v1/me/capabilities',headers=headers()).status_code==503
    with pytest.raises(RuntimeError,match='provenance'):migrate()

def test_empty_initial_migration_records_key_once_and_replays(client, monkeypatch):
    from .journal_fixture import inject_marker
    inject_marker(monkeypatch)
    with factory().begin() as db:db.delete(db.get(SystemState,KEY_STATE))
    migrate();migrate()
    with factory()() as db:assert db.get(SystemState,KEY_STATE).body==key_descriptor()
    assert client.get('/health/ready').status_code==200

@pytest.mark.parametrize('claims',[{'auth_time':True},{'iat':True},{'exp':float(now())+900},{'auth_time':-1},{'auth_time':int(now())+1,'iat':int(now())}])
def test_signed_access_claims_have_strict_integer_time_order(client,claims):
    assert client.get('/v1/me/capabilities',headers=headers(**claims)).status_code==401

def test_deleted_identity_can_read_only_its_minimal_deletion_receipt(client,account):
    own=str(uuid4());foreign=str(uuid4());export=str(uuid4())
    with factory().begin() as db:
        a=db.get(Account,account);a.state='deleted';a.generation=2
        other=Account(id=str(uuid4()),subject_hash='f'*64,generation=1,state='active');db.add(other)
        db.add_all([
            Job(id=own,account_id=account,generation=1,kind='deletion',state='completed',body={'scope':'account'},accepted=now()-10,completed=now(),attempts=1),
            Job(id=foreign,account_id=other.id,generation=1,kind='deletion',state='completed',body={'scope':'account'},accepted=now()-10,completed=now()),
            Job(id=export,account_id=account,generation=1,kind='export',state='completed',body={'selection':{'all':True}},accepted=now()-10,expires=now()+100),
        ])
    receipt=client.get('/v1/privacy/jobs/'+own,headers=headers())
    assert receipt.status_code==200 and receipt.json()['state']=='completed' and receipt.json()['scope']=='account'
    assert set(receipt.json())=={'schema_version','job_id','kind','state','scope','data_generation','accepted_at','started_at','completed_at','expires_at','failure_code','retained_categories','policy_version','attempt_count','allowed_actions'}
    assert client.get('/v1/privacy/jobs/'+foreign,headers=headers()).status_code==404
    assert client.get('/v1/privacy/jobs/'+export,headers=headers()).status_code==403
    assert client.get('/v1/privacy/jobs/'+export+'/download',headers=headers()).status_code==403
    assert client.get('/v1/sessions',headers=headers()).status_code==403

@pytest.mark.parametrize('state',['deleting','awaiting_generation_ack','deleted'])
@pytest.mark.parametrize('generation',[1,2])
def test_locked_identity_can_logout_own_signed_family_without_opening_data_routes(client,account,state,generation):
    with factory().begin() as db:
        owner=db.get(Account,account);owner.state=state;owner.generation=2;owner.notice=None
    h=headers(gen=generation,key='locked-logout',family='owned-locked-family')
    result=client.post('/v1/auth/logout',headers=h,json={})
    assert result.status_code==200 and result.json()['remote_family_revoked'] is True
    assert client.post('/v1/auth/logout',headers=h,json={}).json()==result.json()
    assert client.get('/v1/sessions',headers=h).status_code==401
    with factory()() as db:
        assert db.get(Revocation,family_hash(account,'owned-locked-family'))
        assert not db.get(Revocation,family_hash(account,'untouched-family'))
        assert db.get(Account,account).state==state

def test_logout_cannot_select_another_token_family_or_reactivate_locked_account(client,account):
    with factory().begin() as db:
        owner=db.get(Account,account);owner.state='awaiting_generation_ack';owner.generation=2
    h=headers(gen=1,family='own-family')
    response=client.post('/v1/auth/logout',headers=h,json={'origin_jti':'another-family'})
    assert response.status_code==422 and response.json()['code']=='INVALID_LOGOUT_REQUEST'
    with factory()() as db:
        assert not db.get(Revocation,family_hash(account,'own-family'))
        assert not db.get(Revocation,family_hash(account,'another-family'))
    assert client.post('/v1/auth/logout',headers=h,json={}).status_code==200
    denied=client.post('/v1/sessions',headers=headers(gen=2,family='another-family'),json={'session_id':str(uuid4()),'mode':'synthetic'})
    assert denied.status_code==403 and denied.json()['code']=='ACCOUNT_NOT_WRITABLE'
    with factory()() as db:
        assert not db.get(Revocation,family_hash(account,'another-family'))
