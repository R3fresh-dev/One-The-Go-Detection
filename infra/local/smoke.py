"""Actual service probe. No mocks and no cloud execution permitted."""
import base64
import hashlib
import json
from uuid import uuid4
import httpx
from botocore.exceptions import ClientError
from otgd.config import settings
from otgd.storage import client, versioned_read


def main():
    s=settings()
    if s.environment!='local' or not s.aws_endpoint_url: raise RuntimeError('This probe requires the local Compose services')
    httpx.get('http://api:8000/health/ready',timeout=10,trust_env=False).raise_for_status()
    jwks=httpx.get('http://identity:8081/.well-known/jwks.json',timeout=10,trust_env=False);jwks.raise_for_status()
    if not jwks.json().get('keys'): raise RuntimeError('The real local issuer has no signing key')
    s3=client('s3');sqs=client('sqs');ident=str(uuid4())
    key='verification/'+ident+'.json';payload=b'{"synthetic":true}'
    for bucket in [s.artifact_bucket,s.export_bucket,s.journal_bucket]:
        if s3.get_bucket_versioning(Bucket=bucket).get('Status')!='Enabled': raise AssertionError('Bucket versioning missing')
    params=dict(Bucket=s.artifact_bucket,Key=key,Body=payload,ContentLength=len(payload),ContentType='application/json',ChecksumSHA256=base64.b64encode(hashlib.sha256(payload).digest()).decode(),IfNoneMatch='*')
    version=s3.put_object(**params)['VersionId']
    try:
        if versioned_read(s.artifact_bucket,key,version,100)!=payload: raise AssertionError('Pinned bytes differ')
        try: s3.put_object(**params)
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode']!=412: raise
        else: raise AssertionError('Conditional PUT replay was not rejected')
        # Private probe queue avoids consuming real application jobs.
        q=sqs.create_queue(QueueName='otgd-probe-'+ident,Attributes={'VisibilityTimeout':'120','ReceiveMessageWaitTimeSeconds':'1','MessageRetentionPeriod':'60'})['QueueUrl']
        try:
            sqs.send_message(QueueUrl=q,MessageBody=json.dumps({'schema_version':'1.0.0','probe':ident}))
            got=sqs.receive_message(QueueUrl=q,WaitTimeSeconds=1,MaxNumberOfMessages=1).get('Messages',[])
            if len(got)!=1 or json.loads(got[0]['Body'])['probe']!=ident: raise AssertionError('Real SQS round trip failed')
            sqs.change_message_visibility(QueueUrl=q,ReceiptHandle=got[0]['ReceiptHandle'],VisibilityTimeout=120)
            sqs.delete_message(QueueUrl=q,ReceiptHandle=got[0]['ReceiptHandle'])
            if sqs.receive_message(QueueUrl=q,WaitTimeSeconds=1).get('Messages'): raise AssertionError('Acknowledged probe remains visible')
        finally: sqs.delete_queue(QueueUrl=q)
    finally: s3.delete_object(Bucket=s.artifact_bucket,Key=key,VersionId=version)
    print(json.dumps({'status':'passed','backend_readiness':True,'local_issuer_jwks':True,'versioned_s3_bytes':True,'conditional_replay_412':True,'sqs_receive_extend_delete':True,'scope':'transport probe; authenticated application flow is a separate API integration suite'}))


if __name__=='__main__': main()
