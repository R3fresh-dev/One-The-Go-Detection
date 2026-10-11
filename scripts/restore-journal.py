#!/usr/bin/env python3
"""Reconcile an isolated restored database against the independent S3 journal.

Run in the locked API image with the migration role, after stopping ALL API and
worker tasks. The command never enables services. A failure leaves recovery
unverified. Real S3/PostgreSQL execution is a separate, recorded acceptance gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'services' / 'api'))
from sqlalchemy import delete, select, text, update
from otgd.canonical import canonical, digest, strict_loads
from otgd.config import settings
from otgd.db import Account, Artifact, Check, Dedup, Job, Outbox, Record, Registry, SystemState, factory, iso, now
from otgd.storage import client, put_versioned, versioned_read

EVENT_LIMIT = 8192
INVENTORY_LIMIT = 100000
MANIFEST_LIMIT = 64 * 1024 * 1024
HEX = re.compile(r'^[0-9a-f]{64}$')


class RecoveryBlocked(RuntimeError):
    pass


def timestamp(value):
    if not isinstance(value, str):
        raise RecoveryBlocked('Missing UTC timestamp')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
            raise ValueError()
        return parsed.timestamp()
    except (ValueError, AttributeError):
        raise RecoveryBlocked('Invalid UTC timestamp') from None


def uuid_text(value):
    try:
        if str(UUID(value)) != value:
            raise ValueError()
    except (ValueError, AttributeError, TypeError):
        raise RecoveryBlocked('Invalid journal identifier') from None
    return value


def positive_integer(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise RecoveryBlocked('Invalid journal generation')
    return value


def validate_event(key, raw, available_key_ids, server_time):
    if len(raw) > EVENT_LIMIT:
        raise RecoveryBlocked('Oversized journal event')
    event = strict_loads(raw)
    if not isinstance(event, dict) or canonical(event) != raw or event.get('schema_version') != '1.0.0':
        raise RecoveryBlocked('Unsupported or noncanonical journal event')
    job = uuid_text(event.get('job_id'))
    uuid_text(event.get('account_ref'))
    positive_integer(event.get('retired_generation'))
    if event.get('scope') not in ('all_data', 'account'):
        raise RecoveryBlocked('Unsupported deletion scope')
    if event.get('event_type') == 'deletion_accepted':
        required = {'schema_version','event_type','event_id','job_id','account_ref','retired_generation','new_generation','scope','policy_version','accepted_at','subject_ref_hmac','hmac_key_id'}
        if set(event) != required or event['event_id'] != job or key != f'events/{job}/accepted.json':
            raise RecoveryBlocked('Acceptance key/schema mismatch')
        if positive_integer(event['new_generation']) != event['retired_generation'] + 1:
            raise RecoveryBlocked('Nonconsecutive deletion generation')
        if not HEX.fullmatch(event['subject_ref_hmac']) or event['hmac_key_id'] not in available_key_ids:
            raise RecoveryBlocked('Missing required identity tombstone key or invalid subject reference')
        if event['policy_version'] != 'privacy-v1':
            raise RecoveryBlocked('Unsupported receipt policy; reconcile before recovery')
        instant = timestamp(event['accepted_at'])
    elif event.get('event_type') == 'deletion_completed':
        required = {'schema_version','event_type','job_id','account_ref','retired_generation','scope','completed_at'}
        if not required.issubset(event) or set(event) - required - {'event_id','fencing_token','disposition','retained_categories'}:
            raise RecoveryBlocked('Unsupported completion schema')
        if key != f'events/{job}/completed.json':
            raise RecoveryBlocked('Completion key mismatch')
        if 'event_id' in event and event['event_id'] != job:
            raise RecoveryBlocked('Completion event mismatch')
        if 'fencing_token' in event:positive_integer(event['fencing_token'])
        if event.get('retained_categories'):
            raise RecoveryBlocked('Retention exceptions require an approved restore handler')
        instant = timestamp(event['completed_at'])
    else:
        raise RecoveryBlocked('Unsupported event type')
    if instant > server_time + 60:
        raise RecoveryBlocked('Journal event is in the future')
    return event


def inventory(s3, bucket, prefix, max_items=INVENTORY_LIMIT):
    """List all versions; deleted, replaced or unversioned evidence is invalid."""
    entries = []
    keys = set()
    paginator = s3.get_paginator('list_object_versions')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if page.get('DeleteMarkers'):
            raise RecoveryBlocked('A protected journal prefix contains deletion markers')
        for row in page.get('Versions', []):
            key, version = row['Key'], row.get('VersionId')
            if not version or version == 'null' or key in keys or not row.get('IsLatest'):
                raise RecoveryBlocked('Journal contains replaced or unversioned evidence')
            keys.add(key)
            entries.append({'key':key, 'version_id':version})
            if len(entries) > max_items:
                raise RecoveryBlocked('Journal inventory exceeds the reviewed recovery bound')
    return sorted(entries, key=lambda x:(x['key'],x['version_id']))


def read_inventory(bucket, entries, available_keys, server_time):
    def read_one(row):
        raw = versioned_read(bucket, row['key'], row['version_id'], EVENT_LIMIT)
        event = validate_event(row['key'], raw, available_keys, server_time)
        return {**row,'sha256':hashlib.sha256(raw).hexdigest(),'event':event}
    result=[]
    # Bound pending futures instead of enqueuing the entire 100k-event inventory.
    with ThreadPoolExecutor(max_workers=8) as executor:
        for start in range(0,len(entries),1000):result.extend(executor.map(read_one,entries[start:start+1000]))
    return result


def build_plan(rows):
    accepted, completed, subjects, account_subjects = {}, {}, {}, {}
    for row in rows:
        event = row['event']; target = accepted if event['event_type'] == 'deletion_accepted' else completed
        if event['job_id'] in target:
            raise RecoveryBlocked('Duplicate logical journal event')
        target[event['job_id']] = row
    if set(completed) - set(accepted):
        raise RecoveryBlocked('Completion is missing its acceptance evidence')
    for job_id, row in accepted.items():
        event = row['event']; subject = event['subject_ref_hmac']; account = event['account_ref']
        prior_subject = account_subjects.setdefault(account, subject)
        if prior_subject != subject:
            raise RecoveryBlocked('Account maps to conflicting subject references')
        state = subjects.setdefault(subject, {'account_ref':account,'events':[]})
        if state['account_ref'] != account:
            raise RecoveryBlocked('Subject maps to multiple account references')
        state['events'].append(row)
        if job_id in completed:
            terminal = completed[job_id]['event']
            for field in ['account_ref','retired_generation','scope']:
                if terminal[field] != event[field]:
                    raise RecoveryBlocked('Completion conflicts with acceptance')
            if timestamp(terminal['completed_at']) < timestamp(event['accepted_at']):
                raise RecoveryBlocked('Completion predates acceptance')
    barriers = {}
    for subject, state in subjects.items():
        events = sorted(state['events'],key=lambda row:row['event']['retired_generation'])
        generations = set(); deleted = False
        for row in events:
            event = row['event']
            if event['retired_generation'] in generations or deleted:
                raise RecoveryBlocked('Conflicting generation history or post-account-deletion writes')
            generations.add(event['retired_generation'])
            deleted = event['scope'] == 'account'
        latest = events[-1]['event']
        done = latest['job_id'] in completed
        barriers[subject] = {'account_ref':state['account_ref'], 'generation':latest['new_generation'],
            'state':('deleted' if latest['scope']=='account' else 'awaiting_generation_ack') if done else 'deleting'}
    return {'accepted':accepted,'completed':completed,'barriers':barriers}


def scrub_generation(db, account_id, generation, deletion_id):
    """Restoring a backup must not restore previously deleted health JSON."""
    db.execute(delete(Record).where(Record.account_id==account_id, Record.generation==generation))
    db.execute(delete(Check).where(Check.account_id==account_id, Check.generation==generation))
    for artifact in db.scalars(select(Artifact).where(Artifact.account_id==account_id,Artifact.generation==generation)):
        artifact.state='purged';artifact.scope={};artifact.sha256='0'*64;artifact.size=0;artifact.version_id=None
    for receipt in db.scalars(select(Dedup).where(Dedup.account_id==account_id,Dedup.generation==generation)):
        if receipt.route not in ('/v1/privacy/deletion-requests','/v1/auth/logout'):
            receipt.body=None;receipt.headers={}
    for other in db.scalars(select(Job).where(Job.account_id==account_id,Job.generation==generation,Job.id!=deletion_id,Job.kind!='deletion')):
        other.body={};other.output=None;other.state='failed';other.failure='DATA_GENERATION_RETIRED';other.lease_until=None


def apply_plan(db, plan, recovery_id):
    unresolved_identity = []
    for subject, barrier in plan['barriers'].items():
        account = db.get(Account, barrier['account_ref'])
        matched = db.scalar(select(Account).where(Account.subject_hash==subject))
        if (account and account.subject_hash!=subject) or (matched and matched.id!=barrier['account_ref']):
            raise RecoveryBlocked('Restored account/subject identity conflicts with the journal')
        # All retained journal records are replayed, not only records dated after the snapshot.
        # A DB ahead of this supposedly authoritative journal may indicate missing evidence.
        if account and account.generation > barrier['generation']:
            raise RecoveryBlocked('Database generation exceeds authoritative journal; reconcile missing evidence')
        if account is None:
            account=Account(id=barrier['account_ref'],subject_hash=subject,generation=barrier['generation'],state=barrier['state'])
            db.add(account);db.flush()
        else:
            account.generation=barrier['generation'];account.state=barrier['state'];account.notice=None
        db.merge(SystemState(key='subject:'+subject,body={**barrier,'recovery_id':recovery_id}))
    for job_id, row in plan['accepted'].items():
        event=row['event'];job=db.get(Job,job_id);terminal=plan['completed'].get(job_id)
        if job and (job.account_id!=event['account_ref'] or job.generation!=event['retired_generation'] or job.kind!='deletion' or job.body.get('scope')!=event['scope']):
            raise RecoveryBlocked('Restored deletion job conflicts with independent evidence')
        if job is None:
            job=Job(id=job_id,account_id=event['account_ref'],generation=event['retired_generation'],kind='deletion',state='pending',body={'scope':event['scope'],'accepted_at':event['accepted_at']},accepted=timestamp(event['accepted_at']),fence=0,attempts=0)
            db.add(job);db.flush()
        body={**job.body,'journal_receipt':{'key':row['key'],'version_id':row['version_id'],'sha256':row['sha256']},'recovery_id':recovery_id}
        job.journal_accepted=True;job.lease_until=None;job.fence+=1
        if terminal:
            body.pop('provider_sub',None)
            job.state='completed';job.completed=timestamp(terminal['event']['completed_at']);job.failure=None
            job.output={'scope':event['scope'],'external_cleanup_at':terminal['event']['completed_at'],'recovered_journal_receipt':{'key':terminal['key'],'version_id':terminal['version_id'],'sha256':terminal['sha256']}}
            scrub_generation(db,event['account_ref'],event['retired_generation'],job_id)
        else:
            job.state='pending';job.completed=None;job.output=None;job.attempts=0
            if event['scope']=='account' and not body.get('provider_sub'):
                # A keyed digest cannot be reversed into the provider subject.
                job.state='failed';job.failure='IDENTITY_RECONCILIATION_REQUIRED';unresolved_identity.append(job_id)
            else:
                job.failure=None
            outbox=db.scalar(select(Outbox).where(Outbox.job_id==job_id))
            if outbox is None: db.add(Outbox(job_id=job_id,published=None,available=now()))
            else: outbox.published=None;outbox.available=now();outbox.lease_until=None
        job.body=body
    db.execute(update(Registry).values(active=False))
    return unresolved_identity


def verified_write(bucket,key,body,limit=MANIFEST_LIMIT):
    raw=canonical(body)
    if len(raw)>limit: raise RecoveryBlocked('Recovery manifest exceeds bound')
    version=put_versioned(bucket,key,raw,conditional=True)
    if versioned_read(bucket,key,version,limit)!=raw: raise RecoveryBlocked('Recovery receipt verification failed')
    return {'key':key,'version_id':version,'sha256':hashlib.sha256(raw).hexdigest()}


def recover(backup_created_at, confirm_quiesced):
    if not confirm_quiesced: raise RecoveryBlocked('Stop all API/worker tasks and explicitly confirm quiescence')
    cfg=settings();time_now=now();backup=timestamp(backup_created_at)
    if cfg.environment not in ('local','qa','prod') or not cfg.recovery_required:
        raise RecoveryBlocked('Fixed environment and OTGD_RECOVERY_REQUIRED=true are mandatory')
    if backup>time_now or time_now-backup>35*86400:
        raise RecoveryBlocked('Recovery point must be no older than 35 days and not in the future')
    # Commit the denial state first. Any subsequent validation error keeps readiness closed.
    recovery_id=str(uuid4())
    with factory().begin() as db:
        db.merge(SystemState(key='recovery',body={'verified':False,'recovery_id':recovery_id,'scopes_suspended':True}))
    s3=client('s3');bucket=cfg.journal_bucket
    if s3.get_bucket_versioning(Bucket=bucket).get('Status')!='Enabled': raise RecoveryBlocked('Journal versioning is not enabled')
    controls=inventory(s3,bucket,'control/',10)
    if len(controls)!=1 or controls[0]['key']!='control/established.json': raise RecoveryBlocked('Missing/ambiguous journal continuity evidence')
    control=strict_loads(versioned_read(bucket,controls[0]['key'],controls[0]['version_id'],EVENT_LIMIT))
    if control.get('schema_version')!='1.0.0' or control.get('environment')!=cfg.environment or control.get('minimum_retention_days',0)<90 or control.get('maximum_recovery_age_days')!=35 or timestamp(control.get('established_at'))>backup:
        raise RecoveryBlocked('Journal does not prove the required post-backup interval/90-day retention policy')
    first=inventory(s3,bucket,'events/')
    rows=read_inventory(bucket,first,{cfg.tombstone_key_id},time_now)
    second=inventory(s3,bucket,'events/')
    if first!=second: raise RecoveryBlocked('Journal changed during recovery; writers must remain paused')
    # Reading pinned versions again verifies content, not merely matching list results.
    again=read_inventory(bucket,second,{cfg.tombstone_key_id},time_now)
    if rows!=again: raise RecoveryBlocked('Repeated versioned inventory differs')
    plan=build_plan(rows)
    prior_cutoff=0
    for row in inventory(s3,bucket,'recovery/',10000):
        old_raw=versioned_read(bucket,row['key'],row['version_id'],EVENT_LIMIT);old=strict_loads(old_raw)
        if canonical(old)!=old_raw or old.get('schema_version')!='1.0.0' or old.get('environment')!=cfg.environment or old.get('event_type')!='RecoveryActivation' or type(old.get('authentication_cutoff')) is not int or old['authentication_cutoff']<0 or row['key']!='recovery/'+uuid_text(old.get('recovery_id'))+'.json':
            raise RecoveryBlocked('Invalid prior recovery activation')
        prior_cutoff=max(prior_cutoff,old['authentication_cutoff'])
    manifest={'schema_version':'1.0.0','event_type':'DeletionWatermark','watermark_id':recovery_id,'environment':cfg.environment,'backup_created_at':backup_created_at,'inventory_at':iso(),'event_count':len(rows),'events':[{k:r[k] for k in ('key','version_id','sha256')} for r in rows]}
    manifest['inventory_sha256']=digest(manifest['events'])
    watermark=verified_write(bucket,f'watermarks/{recovery_id}.json',manifest)
    # The transaction is bounded by the inventory limit; API/worker services remain stopped.
    with factory().begin() as db:
        if db.bind.dialect.name=='postgresql':
            db.execute(text("SET LOCAL lock_timeout = '5s'"))
            db.execute(text("SET LOCAL statement_timeout = '15min'"))
            if not db.scalar(text('SELECT pg_try_advisory_xact_lock(798114232)')): raise RecoveryBlocked('Another recovery owns the database lock')
        unresolved=apply_plan(db,plan,recovery_id)
        cutoff=max(prior_cutoff,math.ceil(now()))
        activation={'schema_version':'1.0.0','event_type':'RecoveryActivation','recovery_id':recovery_id,'environment':cfg.environment,'watermark':watermark,'inventory_sha256':manifest['inventory_sha256'],'activated_at':iso(),'authentication_cutoff':cutoff,'scopes_suspended':True}
        receipt=verified_write(bucket,f'recovery/{recovery_id}.json',activation,EVENT_LIMIT)
        db.merge(SystemState(key='recovery',body={'verified':True,'recovery_id':recovery_id,'authentication_cutoff':cutoff,'scopes_suspended':True,'journal_watermark':watermark,'journal_activation':receipt,'inventory_sha256':manifest['inventory_sha256'],'account_barriers':len(plan['barriers']),'identity_reconciliation_jobs':unresolved}))
    # No subject hashes or health records are printed to operator logs.
    return {'status':'reconciled_services_still_stopped','recovery_id':recovery_id,'watermark':watermark,'activation':receipt,'event_count':len(rows),'account_barriers':len(plan['barriers']),'pending_identity_reconciliations':len(unresolved),'authentication_cutoff':cutoff,'scopes_suspended':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup-created-at',required=True,help='Actual RDS recovery point timestamp, UTC')
    parser.add_argument('--confirm-quiesced',action='store_true')
    args=parser.parse_args()
    try: result=recover(args.backup_created_at,args.confirm_quiesced)
    except RecoveryBlocked as error: print(json.dumps({'status':'blocked','reason':str(error)}),file=sys.stderr);return 2
    except Exception as error:
        # SDK/SQL exception text can contain identity or connection data.
        print(json.dumps({'status':'blocked','reason':'DEPENDENCY_OR_SCHEMA_FAILURE','error_type':type(error).__name__}),file=sys.stderr);return 2
    print(json.dumps(result));return 0

if __name__=='__main__': raise SystemExit(main())
