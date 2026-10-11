"""Real local RSA/PKCE/refresh protocol with fictional accounts and isolated DB."""
import base64
import hashlib
import importlib
import re
from urllib.parse import parse_qs,urlsplit
import jwt
import pytest
from fastapi.testclient import TestClient
from otgd import config
from otgd.config import Settings
from otgd.db import OAuthRecord,factory,now

@pytest.fixture
def issuer(client,tmp_path,monkeypatch):
    base=config.settings()
    local=Settings(environment='local',database_url=base.database_url,
        tombstone_key='35'*32,local_signing_key_path=str(tmp_path/'identity-key.pem'))
    monkeypatch.setattr(config,'settings',lambda:local)
    module=importlib.import_module('otgd.local_identity')
    monkeypatch.setattr(module,'s',local)
    with TestClient(module.app,follow_redirects=False) as api:yield api,module

def challenge(verifier):
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')

def authorization(api,module,**overrides):
    verifier='a'*64
    params={'client_id':module.s.client_id,'redirect_uri':module.s.oauth_redirect_uris[0],
        'response_type':'code','state':'state-with-actual-minimum-entropy','code_challenge':challenge(verifier),'code_challenge_method':'S256',**overrides}
    reply=api.get('/oauth2/authorize',params=params)
    return reply,verifier

def select_account(api,module,account='fixture_a'):
    page,verifier=authorization(api,module)
    assert page.status_code==200
    ident=re.search(r'name="authorization_id" value="([^"]+)"',page.text).group(1)
    response=api.post('/oauth2/authorize',data={'authorization_id':ident,'account':account})
    assert response.status_code==303
    params=parse_qs(urlsplit(response.headers['location']).query)
    assert params['state']==['state-with-actual-minimum-entropy']
    return params['code'][0],verifier,ident

def exchange(api,module,code,verifier,**extra):
    return api.post('/oauth2/token',data={'grant_type':'authorization_code','client_id':module.s.client_id,'redirect_uri':module.s.oauth_redirect_uris[0],'code':code,'code_verifier':verifier,**extra})

def refresh(api,module,value,**extra):
    return api.post('/oauth2/token',data={'grant_type':'refresh_token','client_id':module.s.client_id,'refresh_token':value,**extra})

def test_discovery_jwks_and_issuer_bound_access_token(issuer):
    api,module=issuer
    assert api.get('/health/live').json()['fictional_identity'] is True
    discovery=api.get('/.well-known/openid-configuration').json()
    assert discovery['code_challenge_methods_supported']==['S256']
    assert discovery['issuer']==module.s.issuer
    jwk=api.get('/.well-known/jwks.json').json()['keys'][0]
    assert jwk['alg']=='RS256' and jwk['use']=='sig'
    code,verifier,_=select_account(api,module)
    reply=exchange(api,module,code,verifier);assert reply.status_code==200
    claims=jwt.decode(reply.json()['access_token'],jwt.PyJWK.from_dict(jwk).key,algorithms=['RS256'],issuer=module.s.issuer,options={'verify_aud':False})
    assert claims['sub']=='local-fixture_a' and claims['client_id']==module.s.client_id and claims['token_use']=='access'
    assert claims['exp']-claims['iat']==900 and claims['auth_time']<=claims['iat']
    assert module.key().public_key().public_numbers()==module.key().public_key().public_numbers()
    assert (module.key().key_size>=2048)
    assert reply.headers['cache-control']=='no-store'
    assert "frame-ancestors 'none'" in reply.headers['content-security-policy']

@pytest.mark.parametrize('overrides',[{'client_id':'foreign'},{'redirect_uri':'https://attacker.invalid'},{'response_type':'token'},{'code_challenge_method':'plain'},{'code_challenge':'short'},{'state':'short'}])
def test_authorization_rejects_unapproved_callback_client_and_weak_pkce(issuer,overrides):
    api,module=issuer
    reply,_=authorization(api,module,**overrides)
    assert reply.status_code==400 and reply.json()['error']=='invalid_request'

def test_codes_are_single_use_and_wrong_verifier_does_not_consume_them(issuer):
    api,module=issuer;code,verifier,ident=select_account(api,module)
    assert api.post('/oauth2/authorize',data={'authorization_id':ident,'account':'fixture_a'}).status_code==400
    assert exchange(api,module,code,'b'*64).status_code==400
    assert exchange(api,module,code,verifier,redirect_uri='https://attacker.invalid').status_code==400
    assert exchange(api,module,code,verifier).status_code==200
    assert exchange(api,module,code,verifier).status_code==400

def test_only_named_accounts_and_unexpired_authorizations_are_accepted(issuer):
    api,module=issuer;page,_=authorization(api,module)
    ident=re.search(r'name="authorization_id" value="([^"]+)"',page.text).group(1)
    assert api.post('/oauth2/authorize',data={'authorization_id':ident,'account':'arbitrary-human'}).status_code==400
    with factory().begin() as db:db.get(OAuthRecord,module.sha(ident)).expires=now()-1
    assert api.post('/oauth2/authorize',data={'authorization_id':ident,'account':'fixture_b'}).status_code==400
    assert api.post('/oauth2/authorize',data={'authorization_id':'unknown','account':'fixture_a'}).status_code==400

def test_refresh_rotation_preserves_auth_time_and_family_and_revocation_blocks_new_tokens(issuer):
    api,module=issuer;code,verifier,_=select_account(api,module,'fixture_b')
    initial=exchange(api,module,code,verifier).json()
    rotated=refresh(api,module,initial['refresh_token']);assert rotated.status_code==200
    assert refresh(api,module,initial['refresh_token']).status_code==400
    first=jwt.decode(initial['access_token'],options={'verify_signature':False})
    next_claims=jwt.decode(rotated.json()['access_token'],options={'verify_signature':False})
    assert first['origin_jti']==next_claims['origin_jti'] and first['auth_time']==next_claims['auth_time']
    assert first['jti']!=next_claims['jti'] and next_claims['sub']=='local-fixture_b'
    assert api.post('/oauth2/revoke',data={'client_id':'foreign','token':rotated.json()['refresh_token']}).status_code==400
    assert api.post('/oauth2/revoke',data={'client_id':module.s.client_id,'token':rotated.json()['refresh_token']}).status_code==200
    assert api.post('/oauth2/revoke',data={'client_id':module.s.client_id,'token':rotated.json()['refresh_token']}).status_code==200
    assert refresh(api,module,rotated.json()['refresh_token']).status_code==400
    assert api.post('/oauth2/revoke',data={'client_id':module.s.client_id,'token':'nonexistent'}).status_code==200

def test_grant_errors_expiry_and_logout_redirect_allowlist(issuer):
    api,module=issuer;code,verifier,_=select_account(api,module)
    assert exchange(api,module,code,verifier,client_id='foreign').json()['error']=='invalid_client'
    assert exchange(api,module,code,verifier,grant_type='password').json()['error']=='unsupported_grant_type'
    assert exchange(api,module,'missing',verifier).status_code==400
    with factory().begin() as db:db.get(OAuthRecord,module.sha(code)).expires=now()-1
    assert exchange(api,module,code,verifier).status_code==400
    assert api.get('/logout',params={'client_id':module.s.client_id,'logout_uri':module.s.oauth_redirect_uris[0]}).status_code==303
    assert api.get('/logout',params={'client_id':module.s.client_id,'logout_uri':'https://attacker.invalid'}).status_code==200
