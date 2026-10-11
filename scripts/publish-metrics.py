#!/usr/bin/env python3
"""Publish aggregate queue/privacy health; never identity or measurement labels.

One connection per sidecar, zero overflow, one request per minute. CloudWatch
alarms use Maximum across duplicate rolling-deployment publishers. Three failed
publishes exit nonzero so the essential sidecar restarts with its worker task.
"""
import argparse
import json
import signal
import sys
import threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'services'/'api'))
from sqlalchemy import func, select
from otgd.config import settings
from otgd.db import Artifact, Job, Outbox, factory, now
from otgd.storage import client

stop=threading.Event()


def collect(db,instant):
    oldest_outbox=db.scalar(select(func.min(Outbox.available)).join(Job,Outbox.job_id==Job.id).where(Outbox.published.is_(None),Outbox.available<=instant,Job.state.in_(['pending','running'])))
    oldest_privacy=db.scalar(select(func.min(Job.accepted)).where(Job.kind=='deletion',Job.state.in_(['pending','running','failed'])))
    late_artifacts=db.scalar(select(func.count()).select_from(Artifact).where(Artifact.state.in_(['quarantine','cleanup_pending','purged']),func.coalesce(Artifact.cleanup_last_success,Artifact.expires)<instant-86400)) or 0
    late_exports=db.scalar(select(func.count()).select_from(Job).where(Job.kind=='export',Job.expires<instant-86400,Job.output.is_not(None))) or 0
    late_deletions=db.scalar(select(func.count()).select_from(Job).where(Job.kind=='deletion',Job.state=='completed',func.coalesce(Job.cleanup_last_success,Job.completed)<instant-86400)) or 0
    return [
        {'MetricName':'OldestOutboxSeconds','Value':max(0,instant-oldest_outbox) if oldest_outbox is not None else 0,'Unit':'Seconds'},
        {'MetricName':'OldestPrivacyJobSeconds','Value':max(0,instant-oldest_privacy) if oldest_privacy is not None else 0,'Unit':'Seconds'},
        {'MetricName':'CleanupOverdueCount','Value':late_artifacts+late_exports+late_deletions,'Unit':'Count'},
    ]


def publish():
    cfg=settings()
    with factory()() as db: metrics=collect(db,now())
    if cfg.environment=='local':
        print(json.dumps({'event':'operational_metrics','metrics':metrics}),flush=True)
    elif cfg.environment in ('qa','prod'):
        client('cloudwatch').put_metric_data(Namespace='OTGD/'+cfg.environment,MetricData=metrics)
    else: raise RuntimeError('Metrics process requires a fixed runnable environment')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--once',action='store_true');args=parser.parse_args()
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda *_:stop.set())
    failures=0
    while not stop.is_set():
        try:publish();failures=0
        except Exception as error:
            failures+=1
            print(json.dumps({'event':'metrics_publish_failed','error_type':type(error).__name__,'consecutive_failures':failures}),flush=True)
            if args.once or failures>=3:return 1
        if args.once:return 0
        stop.wait(60)
    return 0

if __name__=='__main__':raise SystemExit(main())
