"""Actual signed local HTTP and queued-result latency gate, fictional records only."""
import argparse
import concurrent.futures
import copy
import json
from pathlib import Path
import sys
import time
from uuid import uuid4
import httpx

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from infra.local.app_flow import signin
from otgd.config import settings
from otgd.canonical import digest,strict_loads
from otgd.db import iso


def summarize(durations,count,concurrency,seconds):
    if not durations or len(durations)!=count*10:raise AssertionError('Every workflow must complete all ten measured writes')
    ordered=sorted(durations)
    result={'workflows':count,'concurrency':concurrency,'requests':len(ordered),'p95_ms':ordered[int((len(ordered)-1)*.95)],'p99_ms':ordered[int((len(ordered)-1)*.99)],'seconds':seconds,'result_deadline_seconds':15}
    if result['p95_ms']>=1000 or result['p99_ms']>=2000:raise AssertionError('Local API latency budget exceeded: '+json.dumps(result))
    return result


def run(count=40,concurrency=20):
    cfg=settings()
    if cfg.environment!='local' or not cfg.aws_endpoint_url:raise RuntimeError('This gate requires real local dependencies and fictional identities')
    if type(count)is not int or type(concurrency)is not int or not 1<=concurrency<=20 or not concurrency<=count<=500:raise ValueError('Invalid bounded workflow count/concurrency')
    fixture=strict_loads((ROOT/'examples/synthetic_session.json').read_bytes())
    def account(index):
        http=httpx.Client(timeout=15,trust_env=False,follow_redirects=False)
        token=signin(http,cfg,f'perf_{index+1:02d}')
        headers={'Authorization':'Bearer '+token}
        cap=http.get('http://api:8000/v1/me/capabilities',headers=headers);cap.raise_for_status();caps=cap.json()
        if caps['account_state']!='active':raise AssertionError('Performance fixture must be an active disposable workspace')
        headers['X-Data-Generation']=str(caps['data_generation'])
        config=http.get('http://api:8000/v1/app-config');config.raise_for_status()
        acknowledged=http.post('http://api:8000/v1/me/acknowledgments',headers={**headers,'Idempotency-Key':str(uuid4())},json={'version':config.json()['notice']['version'],'sha256':config.json()['notice']['sha256'],'acknowledged_at':iso()});acknowledged.raise_for_status()
        return http,headers,caps['account_ref']
    # Establish normal PKCE sessions before measuring application requests.
    identities=[]
    try:
        for i in range(concurrency):identities.append(account(i))
        def workflows(index):
            http,headers,account_ref=identities[index];durations=[]
            for _ in range(index,count,concurrency):
                sid=str(uuid4());snapshot=copy.deepcopy(fixture);snapshot.update(session_id=sid,subject_ref=account_ref,target_at=snapshot['created_at'])
                def send(method,path,body,revision=None,key=None):
                    hs={**headers,'Idempotency-Key':key or str(uuid4())}
                    if revision is not None:hs['If-Match']='"'+str(revision)+'"'
                    started=time.perf_counter();response=http.request(method,'http://api:8000'+path,headers=hs,json=body);durations.append((time.perf_counter()-started)*1000)
                    if response.status_code not in (200,201,202):raise AssertionError(f'Workflow write HTTP {response.status_code}')
                    return response
                send('POST','/v1/sessions',{'session_id':sid,'mode':snapshot['mode'],'protocol_id':snapshot['protocol_id']})
                send('PUT',f'/v1/sessions/{sid}/snapshot',snapshot,1)
                context={'schema_version':'1.0.0','session_id':sid,'context_confirmed_at':snapshot['created_at'],'profile_version_id':None,'profile_snapshot_sha256':digest(snapshot['profile']),'history_snapshot_sha256':digest(snapshot['history']),'protocol_id':None,'configuration_refs':[],'baseline_refs':[],'device_associations':[]}
                send('PUT',f'/v1/sessions/{sid}/context',context,0)
                attempts=[];selected={k:None for k in ['saliva','eyes','cardiac','task','alcohol']}
                for component in ['saliva','eyes','cardiac','task']:
                    aid=str(uuid4());projection={'sample':snapshot['sample'],'saliva':snapshot['saliva']} if component=='saliva' else snapshot[component]
                    recordid=snapshot['sample']['sample_id'] if component=='saliva' else snapshot['task']['task_id'] if component=='task' else str(uuid4())
                    first=snapshot['sample']['collected_at'] if component=='saliva' else projection['started_at'];last=first if component=='saliva' else projection['ended_at']
                    attempt={'schema_version':'1.0.0','session_id':sid,'attempt_id':aid,'component':component,'record_id':recordid,'supersedes_attempt_id':None,'status':'valid','source':'simulated','started_at':first,'ended_at':last,'configuration_id':None,'configuration_hash':None,'quality_flags':[],'component_metadata':{'projection':projection},'artifact_refs':[],'attestation_refs':[]}
                    send('PUT',f'/v1/sessions/{sid}/attempts/{aid}',attempt,0);attempts.append({'attempt_id':aid,'sha256':digest(attempt)});selected[component]=aid
                manifest={'schema_version':'1.0.0','session_id':sid,'context_sha256':digest(context),'attempts':attempts,'selected':selected}
                send('PUT',f'/v1/sessions/{sid}/evidence-manifest',manifest,0)
                finalize_key=str(uuid4());finalize_body={'snapshot_sha256':digest(snapshot),'evidence_sha256':digest(manifest)}
                accepted=send('POST',f'/v1/sessions/{sid}/finalize',finalize_body,2,finalize_key)
                replay=send('POST',f'/v1/sessions/{sid}/finalize',finalize_body,2,finalize_key)
                if replay.json()!=accepted.json():raise AssertionError('Finalize replay changed the accepted receipt')
                # Idempotent replay exercises the same finalized receipt.
                deadline=time.monotonic()+15;delay=.1
                while time.monotonic()<deadline:
                    response=http.get(f'http://api:8000/v1/sessions/{sid}/result',headers=headers)
                    if response.status_code==200:
                        result=response.json()
                        if result['state']!='measurement_only' or result['probability']is not None:raise AssertionError('Invalid measurement-only result')
                        break
                    if response.status_code!=202:raise AssertionError(f'Result poll HTTP {response.status_code}')
                    time.sleep(min(delay,max(0,deadline-time.monotonic())));delay=min(.8,delay*2)
                else:raise AssertionError('Actual SQS result exceeded fifteen seconds')
            return durations
        started=time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:durations=[v for result in pool.map(workflows,range(concurrency)) for v in result]
        result=summarize(durations,count,concurrency,time.perf_counter()-started)
        print(json.dumps(result));return result
    finally:
        for http,_,_ in identities:http.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--count',type=int,default=40);parser.add_argument('--concurrency',type=int,default=20);args=parser.parse_args();run(args.count,args.concurrency)
