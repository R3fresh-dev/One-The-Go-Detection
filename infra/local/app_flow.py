"""Real local OAuth/HTTP/outbox/SQS/worker/export/deletion flow, fictional only.

This test uses the actual local issuer's named engineering account. It may erase
that account's fictional workspace; run only in a disposable local project/CI.
It does not create clinical qualification or use a direct worker fallback.
"""
import base64
import argparse
import hashlib
import html
import io
import json
import re
import secrets
import time
import zipfile
from urllib.parse import parse_qs,urlparse
from uuid import uuid4
import httpx
from otgd.config import settings,ROOT
from otgd.canonical import canonical,digest,strict_loads
from otgd.db import iso


def signin(http,cfg,account):
    verifier=secrets.token_urlsafe(48);state=secrets.token_urlsafe(24)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    start=http.get('http://identity:8081/oauth2/authorize',params={'client_id':cfg.client_id,'redirect_uri':'otgd-local://oauth/callback','response_type':'code','state':state,'code_challenge':challenge,'code_challenge_method':'S256'})
    start.raise_for_status();match=re.search(r'name="authorization_id" value="([^"]+)"',start.text)
    if not match:raise AssertionError('Fictional issuer did not provide authorization form')
    choice=http.post('http://identity:8081/oauth2/authorize',data={'authorization_id':html.unescape(match[1]),'account':account})
    if choice.status_code!=303:raise AssertionError('Fictional authorization failed')
    redirect=parse_qs(urlparse(choice.headers['location']).query)
    if redirect['state']!=[state]:raise AssertionError('OAuth state differs')
    token=http.post('http://identity:8081/oauth2/token',data={'grant_type':'authorization_code','client_id':cfg.client_id,'code':redirect['code'][0],'code_verifier':verifier,'redirect_uri':'otgd-local://oauth/callback'})
    token.raise_for_status()
    return token.json()['access_token']


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--confirm-fictional-workspace',action='store_true');args=parser.parse_args()
    if not args.confirm_fictional_workspace:raise RuntimeError('Confirm this is a disposable fictional local workspace')
    cfg=settings()
    if cfg.environment!='local':raise RuntimeError('This flow is local-only and uses fictional accounts')
    with httpx.Client(timeout=15,follow_redirects=False) as http:
        token=signin(http,cfg,'fixture_a');generation=1
        def request(method,path,body=None,revision=None,status=(200,201,202),key=None):
            headers={'Authorization':'Bearer '+token,'X-Data-Generation':str(generation),'Idempotency-Key':key or str(uuid4())}
            if revision is not None:headers['If-Match']='"'+str(revision)+'"'
            response=http.request(method,'http://api:8000'+path,headers=headers,json=body)
            if response.status_code not in status:raise AssertionError(f'{method} {path}: HTTP {response.status_code}')
            return response
        caps=request('GET','/v1/me/capabilities').json();account=caps['account_ref'];generation=caps['data_generation']
        if caps['account_state']=='awaiting_generation_ack':request('POST','/v1/me/data-generation/acknowledgments',{'confirmation':True})
        config=http.get('http://api:8000/v1/app-config').json()
        if config['inference_available'] is not False:raise AssertionError('Inference must remain unavailable')
        request('POST','/v1/me/acknowledgments',{'version':'v1','sha256':config['notice']['sha256'],'acknowledged_at':iso()})
        snapshot=strict_loads((ROOT/'examples/synthetic_session.json').read_bytes());sid=str(uuid4())
        snapshot.update(session_id=sid,subject_ref=account,target_at=snapshot['created_at'])
        request('POST','/v1/sessions',{'session_id':sid,'mode':snapshot['mode'],'protocol_id':snapshot['protocol_id']})
        request('PUT',f'/v1/sessions/{sid}/snapshot',snapshot,1)
        context={'schema_version':'1.0.0','session_id':sid,'context_confirmed_at':snapshot['created_at'],'profile_version_id':None,'profile_snapshot_sha256':digest(snapshot['profile']),'history_snapshot_sha256':digest(snapshot['history']),'protocol_id':None,'configuration_refs':[],'baseline_refs':[],'device_associations':[]}
        request('PUT',f'/v1/sessions/{sid}/context',context,0)
        attempts=[];selected={k:None for k in ['saliva','eyes','cardiac','task','alcohol']}
        for component in ['saliva','eyes','cardiac','task']:
            attempt_id=str(uuid4());projection={'sample':snapshot['sample'],'saliva':snapshot['saliva']} if component=='saliva' else snapshot[component]
            record_id=snapshot['sample']['sample_id'] if component=='saliva' else snapshot['task']['task_id'] if component=='task' else str(uuid4())
            first=snapshot['sample']['collected_at'] if component=='saliva' else projection['started_at'];last=first if component=='saliva' else projection['ended_at']
            attempt={'schema_version':'1.0.0','session_id':sid,'attempt_id':attempt_id,'component':component,'record_id':record_id,'supersedes_attempt_id':None,'status':'valid','source':'simulated','started_at':first,'ended_at':last,'configuration_id':None,'configuration_hash':None,'quality_flags':[],'component_metadata':{'projection':projection},'artifact_refs':[],'attestation_refs':[]}
            request('PUT',f'/v1/sessions/{sid}/attempts/{attempt_id}',attempt,0)
            attempts.append({'attempt_id':attempt_id,'sha256':digest(attempt)});selected[component]=attempt_id
        manifest={'schema_version':'1.0.0','session_id':sid,'context_sha256':digest(context),'attempts':attempts,'selected':selected}
        request('PUT',f'/v1/sessions/{sid}/evidence-manifest',manifest,0)
        accepted=request('POST',f'/v1/sessions/{sid}/finalize',{'snapshot_sha256':digest(snapshot),'evidence_sha256':digest(manifest)},2).json()
        def wait_job(job_id):
            deadline=time.monotonic()+90
            while time.monotonic()<deadline:
                result=request('GET','/v1/privacy/jobs/'+job_id).json()
                if result['state'] in ('completed','partially_retained'):return result
                if result['state'] in ('failed','expired'):raise AssertionError('Asynchronous job failed')
                time.sleep(1)
            raise AssertionError('Actual worker did not complete within 90 seconds')
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            response=request('GET',f'/v1/sessions/{sid}/result')
            if response.status_code==200:break
            time.sleep(2)
        else:raise AssertionError('Actual result worker did not complete within 90 seconds')
        measured=response.json()
        if measured['state']!='measurement_only' or measured['probability'] is not None:raise AssertionError('Synthetic evidence produced an invalid inference state')
        other=signin(http,cfg,'fixture_b')
        outsider=http.get(f'http://api:8000/v1/sessions/{sid}',headers={'Authorization':'Bearer '+other})
        if outsider.status_code!=404:raise AssertionError('Cross-account session admission was not concealed')
        # Export and deletion endpoints use the actual service, journal and workers.
        export=request('POST','/v1/privacy/exports',{'selection':{'kind':'single','session_ids':[sid]},'format':'json_zip','include_raw':False}).json();wait_job(export['job_id'])
        download=request('GET',f"/v1/privacy/jobs/{export['job_id']}/download")
        with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
            if not archive.namelist():raise AssertionError('Export is empty')
        deletion=request('POST','/v1/privacy/deletion-requests',{'scope':'all_data','confirmation':True}).json()
        generation+=1;wait_job(deletion['job_id'])
        request('GET',f'/v1/sessions/{sid}',status=(403,404,410))
        request('GET',f"/v1/privacy/jobs/{export['job_id']}/download",status=(403,404,410))
    print(json.dumps({'status':'passed','fictional_identity':True,'actual_oauth_pkce':True,'actual_http_and_sqs_worker':True,'authenticated_export':True,'versioned_deletion_journal':True,'cross_account_denial':True,'inference_available':False}))

if __name__=='__main__':main()
