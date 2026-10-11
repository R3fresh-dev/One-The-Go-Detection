#!/usr/bin/env python3
"""Audited one-job replay under the maintenance role; never bulk-redrive a queue."""
import argparse
import json
from pathlib import Path
import re
import sys
from uuid import UUID
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'services'/'api'))
from sqlalchemy import select
from otgd.canonical import digest,strict_loads
from otgd.config import settings
from otgd.db import Account,Audit,Job,Outbox,SystemState,factory,iso,now
from otgd.storage import versioned_read


def replay(job_id,replay_id,reason_code,operator_ref):
    if str(UUID(job_id))!=job_id or str(UUID(replay_id))!=replay_id:raise ValueError('Canonical job and replay UUIDs are required')
    if not re.fullmatch(r'[A-Z0-9_]{3,80}',reason_code) or not re.fullmatch(r'[A-Za-z0-9:/_.@-]{3,256}',operator_ref):raise ValueError('Supply a bounded reason code and accountable operator reference; no free-form health text')
    cfg=settings()
    with factory().begin() as db:
        recorded=db.get(SystemState,'replay:'+replay_id)
        request={'job_id':job_id,'reason_code':reason_code,'operator_ref':operator_ref}
        if recorded:
            if any(recorded.body.get(k)!=v for k,v in request.items()):raise ValueError('Replay ID was already bound to another operation')
            return {'status':'already_accepted','job_id':job_id,'replay_id':replay_id}
        peek=db.get(Job,job_id)
        if not peek or peek.kind not in ('result','export','deletion'):raise ValueError('Unknown replayable job')
        account=db.scalar(select(Account).where(Account.id==peek.account_id).with_for_update())
        job=db.scalar(select(Job).where(Job.id==job_id).with_for_update().execution_options(populate_existing=True))
        if not account or job.state!='failed' or (job.lease_until and job.lease_until>now()):raise ValueError('Only a failed unleased job can start a new bounded replay cycle')
        if job.kind=='deletion':
            if not job.journal_accepted or account.generation<=job.generation or account.state!='deleting':raise ValueError('Deletion no longer matches its accepted barrier')
            if job.body.get('scope')=='account' and not job.body.get('provider_sub'):raise ValueError('Independent identity reconciliation is required before replay')
            receipt=job.body.get('journal_receipt',{});event=strict_loads(versioned_read(cfg.journal_bucket,'events/'+job_id+'/accepted.json',receipt.get('version_id'),8192))
            if digest(event)!=receipt.get('sha256') or event.get('job_id')!=job.id or event.get('account_ref')!=account.id or event.get('retired_generation')!=job.generation or event.get('scope')!=job.body.get('scope') or event.get('subject_ref_hmac')!=account.subject_hash:raise ValueError('Accepted journal evidence does not authorize this replay')
        elif account.state!='active' or account.generation!=job.generation or (job.expires and job.expires<=now()):raise ValueError('Retired, expired or inactive source work cannot be replayed')
        job.fence+=1;job.attempts=0;job.lease_until=None;job.state='pending';job.failure=None
        job.body={**job.body,'last_operator_replay_id':replay_id}
        outbox=db.scalar(select(Outbox).where(Outbox.job_id==job.id))
        if outbox is None:db.add(Outbox(job_id=job.id,published=None,available=now()))
        else:outbox.published=None;outbox.available=now();outbox.lease_until=None
        db.add(SystemState(key='replay:'+replay_id,body={**request,'accepted_at':iso(),'fencing_token':job.fence}))
        db.add(Audit(account_id=account.id,generation=job.generation,action='operator:job_replay:'+reason_code,request_id=replay_id))
    return {'status':'accepted','job_id':job_id,'replay_id':replay_id,'max_attempts':5,'source_authority_rechecked_by_worker':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['job-id','replay-id','reason-code','operator-ref']:parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    try:result=replay(args.job_id,args.replay_id,args.reason_code,args.operator_ref)
    except ValueError as error:print(json.dumps({'status':'blocked','reason':str(error)}),file=sys.stderr);return 2
    except Exception as error:print(json.dumps({'status':'blocked','reason':'DEPENDENCY_OR_AUTHORITY_FAILURE','error_type':type(error).__name__}),file=sys.stderr);return 2
    print(json.dumps(result));return 0

if __name__=='__main__':raise SystemExit(main())
