"""Unit evidence for recovery barriers; these are not S3/PostgreSQL integration claims."""
import importlib.util
import os
import pathlib
import unittest
os.environ['OTGD_ENVIRONMENT']='test'
os.environ['OTGD_DATABASE_URL']='sqlite://'
os.environ['OTGD_TOMBSTONE_KEY']='a'*64
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('restore',ROOT/'scripts'/'restore-journal.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from otgd.db import Account,Base,Check,Job,Record,Registry,SystemState

ACCOUNT='10000000-0000-4000-8000-000000000001'
JOB='20000000-0000-4000-8000-000000000001'
SUBJECT='c'*64


def acceptance(scope='all_data',**values):
    return {'schema_version':'1.0.0','event_type':'deletion_accepted','event_id':JOB,'job_id':JOB,'account_ref':ACCOUNT,'retired_generation':1,'new_generation':2,'scope':scope,'policy_version':'privacy-v1','accepted_at':'2026-10-01T12:00:00.000Z','subject_ref_hmac':SUBJECT,'hmac_key_id':'v1',**values}


def row(event):
    tail='accepted' if event['event_type']=='deletion_accepted' else 'completed'
    return {'key':f"events/{event['job_id']}/{tail}.json",'version_id':'pinned-v1','sha256':r.digest(event),'event':event}


def completion(scope='all_data'):
    return {'schema_version':'1.0.0','event_type':'deletion_completed','job_id':JOB,'account_ref':ACCOUNT,'retired_generation':1,'scope':scope,'completed_at':'2026-10-01T12:10:00.000Z'}


class RecoveryTest(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite://');Base.metadata.create_all(self.engine)

    def test_valid_canonical_event_and_missing_hmac_key(self):
        event=acceptance();raw=r.canonical(event);key=row(event)['key']
        self.assertEqual(r.validate_event(key,raw,{'v1'},r.timestamp('2026-10-02T00:00:00Z')),event)
        with self.assertRaises(r.RecoveryBlocked):r.validate_event(key,raw,{'v2'},r.timestamp('2026-10-02T00:00:00Z'))
        with self.assertRaises(r.RecoveryBlocked):r.validate_event(key,b' '+raw,{'v1'},r.timestamp('2026-10-02T00:00:00Z'))

    def test_complete_before_acceptance_and_subject_collision_fail(self):
        with self.assertRaises(r.RecoveryBlocked):r.build_plan([row(completion())])
        another=acceptance(job_id='20000000-0000-4000-8000-000000000002',event_id='20000000-0000-4000-8000-000000000002',account_ref='10000000-0000-4000-8000-000000000002')
        with self.assertRaises(r.RecoveryBlocked):r.build_plan([row(acceptance()),row(another)])

    def test_backup_predating_account_restores_original_id_and_generation(self):
        plan=r.build_plan([row(acceptance()),row(completion())])
        with Session(self.engine) as db,db.begin():
            db.add(Registry(id='old-trust',kind='qualification',body={'old':True},active=True));db.flush()
            r.apply_plan(db,plan,'recovery-fixture')
            account=db.get(Account,ACCOUNT)
            self.assertEqual((account.generation,account.state),(2,'awaiting_generation_ack'))
            barrier=db.get(SystemState,'subject:'+SUBJECT)
            self.assertEqual(barrier.body['account_ref'],ACCOUNT)
            self.assertFalse(db.get(Registry,'old-trust').active)
            self.assertEqual(db.get(Job,JOB).state,'completed')

    def test_pending_account_cleanup_without_provider_is_blocked(self):
        plan=r.build_plan([row(acceptance('account'))])
        with Session(self.engine) as db,db.begin():
            unresolved=r.apply_plan(db,plan,'recovery-fixture')
            self.assertEqual(unresolved,[JOB])
            self.assertEqual(db.get(Account,ACCOUNT).state,'deleting')
            self.assertEqual(db.get(Job,JOB).failure,'IDENTITY_RECONCILIATION_REQUIRED')

    def test_completed_barrier_scrubs_restored_health_data(self):
        plan=r.build_plan([row(acceptance('account')),row(completion('account'))])
        with Session(self.engine) as db,db.begin():
            db.add(Account(id=ACCOUNT,subject_hash=SUBJECT,generation=1,state='active'));db.flush()
            db.add(Record(id='old-record',account_id=ACCOUNT,generation=1,kind='profile',body={'private':'fixture'},sha256='d'*64))
            db.add(Check(id='30000000-0000-4000-8000-000000000001',account_id=ACCOUNT,generation=1,mode='test',state='completed',snapshot={'private':'fixture'}));db.flush()
            r.apply_plan(db,plan,'recovery-fixture')
            self.assertEqual(db.get(Account,ACCOUNT).state,'deleted')
            self.assertEqual(list(db.scalars(select(Record))),[])
            self.assertEqual(list(db.scalars(select(Check))),[])

    def test_inconsistent_existing_account_fails(self):
        with Session(self.engine) as db,db.begin():
            db.add(Account(id=ACCOUNT,subject_hash='b'*64,generation=1,state='active'));db.flush()
            with self.assertRaises(r.RecoveryBlocked):r.apply_plan(db,r.build_plan([row(acceptance())]),'fixture')

    def test_deletion_marker_and_replacement_fail(self):
        class Pages:
            def __init__(self,pages):self.pages=pages
            def paginate(self,**kwargs):return self.pages
        class S3:
            def __init__(self,pages):self.pages=pages
            def get_paginator(self,name):return Pages(self.pages)
        for pages in [[{'DeleteMarkers':[{'Key':'events/x'}]}],[{'Versions':[{'Key':'events/x','VersionId':'1','IsLatest':True},{'Key':'events/x','VersionId':'2','IsLatest':False}]}]]:
            with self.assertRaises(r.RecoveryBlocked):r.inventory(S3(pages),'bucket','events/')

if __name__=='__main__':unittest.main()
