"""Idempotent real LocalStack setup, or verification of already-provisioned AWS.

No fallback emulator exists. Run from the API's locked Python environment.
"""
import argparse
import json
from datetime import datetime, timezone
from otgd.config import settings
from otgd.storage import client, put_versioned, versioned_read
from otgd.canonical import canonical, strict_loads
from botocore.exceptions import ClientError


def initialize(cloud=False,establish_new=False):
    s=settings(); s3=client('s3'); sqs=client('sqs')
    if cloud != (s.environment in ('qa','prod')):
        raise RuntimeError('Explicit cloud verification must match the fixed environment')
    # This must precede even bucket creation: a retained SQL database cannot
    # adopt a fresh emulator journal after its independent evidence is lost.
    from otgd.db import engine
    from otgd.journal_continuity import preflight_bootstrap
    with engine().connect() as connection:
        retained = preflight_bootstrap(connection, s, s3)
    for name in [s.artifact_bucket,s.export_bucket,s.journal_bucket]:
        try: s3.head_bucket(Bucket=name)
        except ClientError as e:
            if cloud or e.response['ResponseMetadata']['HTTPStatusCode'] not in (404,): raise
            args={'Bucket':name}
            if s.aws_region!='us-east-1': args['CreateBucketConfiguration']={'LocationConstraint':s.aws_region}
            s3.create_bucket(**args)
        if not cloud:
            s3.put_bucket_versioning(Bucket=name,VersioningConfiguration={'Status':'Enabled'})
            s3.put_public_access_block(Bucket=name,PublicAccessBlockConfiguration={k:True for k in ['BlockPublicAcls','IgnorePublicAcls','BlockPublicPolicy','RestrictPublicBuckets']})
            s3.put_bucket_encryption(Bucket=name,ServerSideEncryptionConfiguration={'Rules':[{'ApplyServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]})
        if s3.get_bucket_versioning(Bucket=name).get('Status')!='Enabled': raise RuntimeError('Versioning is required')
    if not cloud:
        dlq=sqs.create_queue(QueueName='otgd-local-dlq',Attributes={'VisibilityTimeout':'120','MessageRetentionPeriod':'1209600','SqsManagedSseEnabled':'true'})['QueueUrl']
        arn=sqs.get_queue_attributes(QueueUrl=dlq,AttributeNames=['QueueArn'])['Attributes']['QueueArn']
        queue=sqs.create_queue(QueueName='otgd-local-jobs',Attributes={'VisibilityTimeout':'120','ReceiveMessageWaitTimeSeconds':'20','MessageRetentionPeriod':'345600','SqsManagedSseEnabled':'true','RedrivePolicy':json.dumps({'deadLetterTargetArn':arn,'maxReceiveCount':5})})['QueueUrl']
        if queue!=s.queue_url or dlq!=s.dlq_url: raise RuntimeError('Configured internal queue URL differs from actual LocalStack URL; fix origins before starting')
    attrs=sqs.get_queue_attributes(QueueUrl=s.queue_url,AttributeNames=['All'])['Attributes']
    if int(attrs['VisibilityTimeout'])!=s.serverless_queue_visibility or int(json.loads(attrs['RedrivePolicy'])['maxReceiveCount'])!=5: raise RuntimeError('Queue policy differs from reviewed contract')
    key='control/established.json'
    try:
        head=s3.head_object(Bucket=s.journal_bucket,Key=key)
        established=strict_loads(versioned_read(s.journal_bucket,key,head.get('VersionId'),8192))
        if established.get('environment')!=s.environment or established.get('minimum_retention_days')!=90: raise RuntimeError('Journal continuity configuration mismatch')
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode']!=404: raise
        if retained or (cloud and not establish_new): raise RuntimeError('Missing journal continuity evidence; only a confirmed empty first deployment may establish a new journal')
        established={'schema_version':'1.0.0','environment':s.environment,'established_at':datetime.now(timezone.utc).isoformat(),'minimum_retention_days':90,'maximum_recovery_age_days':35}
        raw=canonical(established); version=put_versioned(s.journal_bucket,key,raw,conditional=True)
        if versioned_read(s.journal_bucket,key,version,8192)!=raw: raise RuntimeError('Journal establishment verification failed')
    print(json.dumps({'status':'verified','environment':s.environment,'buckets':3,'visibility_seconds':s.serverless_queue_visibility,'max_receive_count':5,'journal_established_at':established['established_at']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--verify-cloud',action='store_true');p.add_argument('--establish-new',action='store_true',help='Only for the first empty cloud deployment, before any admissions');a=p.parse_args();initialize(a.verify_cloud,a.establish_new)
