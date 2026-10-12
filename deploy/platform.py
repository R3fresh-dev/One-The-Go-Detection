#!/usr/bin/env python3
"""Explicit, bounded deployment operations. No action executes merely on import.

Use the API's locked uv environment. AWS credentials come from the normal SDK
provider chain; secrets are injected into ECS, never read into shell arguments.
"""
from __future__ import annotations
from pathlib import Path
import sys

# Direct file execution puts deploy/ first, where platform.py would shadow the
# standard library module imported by uuid and the AWS SDK.
ROOT=Path(__file__).resolve().parents[1]
sys.path[:]=[entry for entry in sys.path if Path(entry).resolve()!=ROOT/'deploy']
sys.path.insert(0,str(ROOT/'services'/'api'))
sys.path.insert(0,str(ROOT))

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import tarfile
import time
from datetime import datetime, timezone

INFRA=ROOT/'infra'
import boto3
from botocore.config import Config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from otgd.canonical import canonical,strict_loads
from deploy.provenance import (Gate, bounded_json, sha256, validate_gate_binding,
    verify_gate_file, verify_signed_record, validate_qa_approval, verify_qa_approval)


def deployment_environment():
    # LocalStack endpoints must never redirect cloud account proofs or mutations.
    env={key:value for key,value in os.environ.items() if key!='AWS_ENDPOINT_URL' and not key.startswith('AWS_ENDPOINT_URL_')}
    env['AWS_IGNORE_CONFIGURED_ENDPOINT_URLS']='true'
    return env


def run(args,*,cwd=ROOT,capture=False,input=None):
    return subprocess.run(args,cwd=cwd,text=True,check=True,capture_output=capture,input=input,env=deployment_environment()).stdout


def read_config(path,registry=False):
    if not (INFRA/'node_modules').exists():raise Gate('Run npm ci in infra first')
    return json.loads(run(['node','--import','tsx','bin/validate.ts',str(path.resolve()),*(['--registry'] if registry else [])],cwd=INFRA,capture=True))


class CloudSession:
    """Use AWS credential providers while ignoring local/profile service endpoints."""
    def __init__(self,region,profile):
        self._session=boto3.Session(region_name=region,profile_name=profile)

    def client(self,service,**options):
        if 'endpoint_url' in options:raise Gate('Cloud deployment clients cannot override AWS service endpoints')
        guarded=Config(ignore_configured_endpoint_urls=True)
        supplied=options.pop('config',None)
        options['config']=supplied.merge(guarded) if supplied else guarded
        return self._session.client(service,**options)


def session(c,profile=None):return CloudSession(c['region'],profile)


def preflight(c,registry=False,profile=None):
    aws=session(c,profile)
    if aws.client('sts').get_caller_identity()['Account']!=c['account']:raise Gate('AWS credential account differs from the deployment configuration')
    certificate=aws.client('acm').describe_certificate(CertificateArn=c['certificateArn'])['Certificate']
    domains=certificate.get('SubjectAlternativeNames',[])
    def covers(name):return name==c['domain'] or (name.startswith('*.') and c['domain'].split('.',1)[1:]==[name[2:]])
    if certificate['Status']!='ISSUED' or not any(covers(x) for x in domains):raise Gate('ACM certificate is not issued for the configured API domain')
    if c.get('webDomain'):
        web_certificate=aws.client('acm',region_name='us-east-1').describe_certificate(CertificateArn=c['webCertificateArn'])['Certificate']
        web_name=c['webDomain']
        if web_certificate.get('Status')!='ISSUED' or not any(name==web_name or (name.startswith('*.') and web_name.split('.',1)[1:]==[name[2:]]) for name in web_certificate.get('SubjectAlternativeNames',[])):
            raise Gate('CloudFront ACM certificate is not issued for the configured web domain')
    versions=aws.client('rds').describe_db_engine_versions(Engine='postgres',EngineVersion=c['databaseEngineVersion'],IncludeAll=False)['DBEngineVersions']
    if not any(v['EngineVersion']==c['databaseEngineVersion'] and v.get('Status')=='available' for v in versions):raise Gate('Chosen PostgreSQL minor is unavailable in this region')
    options=aws.client('rds').describe_orderable_db_instance_options(Engine='postgres',EngineVersion=c['databaseEngineVersion'],DBInstanceClass='db.t4g.medium' if c['environment']=='prod' else 'db.t4g.small')['OrderableDBInstanceOptions']
    if not options or (c['environment']=='prod' and not any(x.get('MultiAZCapable') for x in options)):raise Gate('Chosen RDS capacity is unavailable')
    if c.get('hostedZoneId'):
        zone=aws.client('route53').get_hosted_zone(Id=c['hostedZoneId'])['HostedZone']
        if zone['Name'].rstrip('.')!=c['hostedZoneName'] or zone.get('Config',{}).get('PrivateZone'):raise Gate('Hosted zone does not match the configured public zone')
    if c.get('databaseSnapshotIdentifier'):
        snapshot=aws.client('rds').describe_db_snapshots(DBSnapshotIdentifier=c['databaseSnapshotIdentifier'])['DBSnapshots'][0]
        age=datetime.now(timezone.utc)-snapshot.get('OriginalSnapshotCreateTime',snapshot['SnapshotCreateTime'])
        if snapshot['Status']!='available' or snapshot['Engine']!='postgres' or snapshot['EngineVersion']!=c['databaseEngineVersion'] or snapshot.get('MasterUsername')!='otgd_migrator' or not snapshot.get('Encrypted') or snapshot['AllocatedStorage']>100 or not 0<=age.total_seconds()<=35*86400:raise Gate('Snapshot does not satisfy reviewed recovery age, encryption, schema or capacity bounds')
        tags={x['Key']:x['Value'] for x in aws.client('rds').list_tags_for_resource(ResourceName=snapshot['DBSnapshotArn'])['TagList']}
        if tags.get('deployment')!='otgd-'+c['environment']:raise Gate('Snapshot does not belong to this environment')
        current=stack_outputs(aws,c)
        if snapshot.get('KmsKeyId')!=current.get('DataKeyArn'):raise Gate('Snapshot encryption key differs from this retained environment data key')
    if not registry:
        detail=aws.client('ecr').describe_images(repositoryName='otgd-'+c['environment'],imageIds=[{'imageDigest':c['imageDigest']}])['imageDetails']
        if len(detail)!=1 or detail[0]['imageDigest']!=c['imageDigest']:raise Gate('Immutable release digest is absent')
    return aws


def stack_outputs(aws,c):
    stack=aws.client('cloudformation').describe_stacks(StackName='otgd-'+c['environment']+'-platform')['Stacks'][0]
    if stack['StackStatus'] not in ('CREATE_COMPLETE','UPDATE_COMPLETE','UPDATE_ROLLBACK_COMPLETE'):raise Gate('Platform stack is not stable')
    return {x['OutputKey']:x['OutputValue'] for x in stack.get('Outputs',[])}


def cdk(path,c,verb,registry=False):
    stack='otgd-'+c['environment']+('-registry' if registry else '-platform')
    args=['npm','exec','--','cdk',verb,stack,'-c','config='+str(path.resolve())]
    if registry:args+=['-c','phase=registry']
    # CDK keeps its own IAM-change review prompt for an actual operator deployment.
    if verb=='deploy':args+=['--require-approval','broadening']
    run(args,cwd=INFRA)


def services_stopped(aws,out):
    rows=aws.client('ecs').describe_services(cluster=out['Cluster'],services=[out['ApiService'],out['WorkerService']])
    if rows.get('failures') or any(x['desiredCount'] or x['runningCount'] or x['pendingCount'] for x in rows['services']):raise Gate('Every API and worker task must be stopped before this operation')


def task(aws,out,command,extra_environment=None):
    ecs=aws.client('ecs')
    response=ecs.run_task(cluster=out['Cluster'],taskDefinition=out['MigrationTaskDefinition'],launchType='FARGATE',count=1,
        startedBy='otgd-reviewed-maintenance',networkConfiguration={'awsvpcConfiguration':{'subnets':out['PrivateSubnets'].split(','),'securityGroups':[out['MigrationSecurityGroup']],'assignPublicIp':'DISABLED'}},
        overrides={'containerOverrides':[{'name':'migration','command':command,'environment':[{'name':k,'value':v} for k,v in (extra_environment or {}).items()]}]})
    if response.get('failures') or len(response.get('tasks',[]))!=1:raise Gate('Maintenance task failed admission')
    arn=response['tasks'][0]['taskArn'];deadline=time.monotonic()+900
    while time.monotonic()<deadline:
        row=ecs.describe_tasks(cluster=out['Cluster'],tasks=[arn])['tasks'][0]
        if row['lastStatus']=='STOPPED':
            if any(x.get('exitCode')!=0 for x in row.get('containers',[])):raise Gate('Maintenance task failed; inspect protected application logs by task ID '+arn)
            return arn
        time.sleep(10)
    ecs.stop_task(cluster=out['Cluster'],task=arn,reason='Reviewed maintenance task exceeded 15-minute bound')
    raise Gate('Maintenance deadline exceeded; services stay stopped')


def private_key(path):
    if os.name!='nt' and path.stat().st_mode & 0o077:raise Gate('Release private key must be readable by its owner only')
    key=serialization.load_pem_private_key(path.read_bytes(),password=None)
    if not isinstance(key,Ed25519PrivateKey):raise Gate('Expected an Ed25519 signing key')
    return key


def require_trusted_signer(private_path,public_path):
    if not public_path:raise Gate('Supply an independently trusted --trusted-public-key before signing')
    trusted=serialization.load_pem_public_key(public_path.read_bytes())
    actual=private_key(private_path).public_key()
    if (not isinstance(trusted,Ed25519PublicKey) or
        trusted.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)!=actual.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)):
        raise Gate('Signing key does not match the independently trusted release authority')


def sign_release(body,path,key_path):
    raw=canonical(body);signature=private_key(key_path).sign(raw)
    output={'schema_version':'1.0.0','payload':body,'payload_sha256':hashlib.sha256(raw).hexdigest(),'algorithm':'Ed25519','signature':base64.b64encode(signature).decode()}
    if path.exists():raise Gate('A signed release record is immutable; choose a new path')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(output,f,indent=2);f.write('\n')


def verify_release(path,public_path,c):
    payload=verify_signed_record(path,public_path)
    if payload.get('environment')!=c['environment'] or payload.get('account')!=c['account'] or payload.get('region')!=c['region'] or payload.get('image_digest')!=c['imageDigest'] or payload.get('release_id')!=c['releaseId']:raise Gate('Signed release does not bind this environment/account/digest')
    if payload.get('database_schema')!=1 or payload.get('inference_available') is not False:raise Gate('Unsupported schema or inference release')
    if payload.get('oci_revision')!=c['releaseId'] or not re.fullmatch(r'sha256:[0-9a-f]{64}',payload.get('image_config_digest','')):raise Gate('Release lacks verified immutable image source/config binding')
    if payload.get('gate_provenance_sha256')!=validate_gate_binding(payload.get('gate_provenance'),c['releaseId']):raise Gate('Release gate provenance hash differs from the signed receipt')
    if c['environment']=='prod' and any(not re.fullmatch(r'[0-9a-f]{64}',payload.get(k,'')) for k in ['promoted_from_release_sha256','qa_evidence_sha256']):raise Gate('Production requires a signed promotion from the tested QA digest')
    if c['environment']=='prod':
        source=payload.get('qa_source')
        if (not isinstance(source,dict) or set(source)!={'account','region','image_digest','release_id','qa_release_sha256','gate_provenance_sha256'}
            or not re.fullmatch(r'[0-9]{12}',source.get('account','')) or source['account']==c['account']
            or source.get('image_digest')!=c['imageDigest'] or source.get('release_id')!=c['releaseId']
            or source.get('qa_release_sha256')!=payload['promoted_from_release_sha256']
            or source.get('gate_provenance_sha256')!=payload['gate_provenance_sha256']):raise Gate('Production QA source binding is absent or invalid')
    return payload


def require_release(args,c,aws=None):
    if not args.release or not args.trusted_public_key:raise Gate('Supply --release and independently trusted --trusted-public-key')
    payload=verify_release(args.release,args.trusted_public_key,c)
    proof=verify_gate_file(args.gate_evidence,c['releaseId'])
    if sha256(proof)!=payload['gate_provenance_sha256']:raise Gate('Live latest-attempt GitHub evidence differs from the signed release receipt')
    if c['environment']=='prod':
        verify_qa_approval(args.qa_evidence,args.trusted_public_key,payload['qa_source'])
        if hashlib.sha256(args.qa_evidence.read_bytes()).hexdigest()!=payload['qa_evidence_sha256']:raise Gate('QA approval differs from the signed production promotion')
    if aws is not None:verify_release_image(aws,c,payload)
    return payload


def image_config_digest(aws,c):
    response=aws.client('ecr').batch_get_image(repositoryName='otgd-'+c['environment'],imageIds=[{'imageDigest':c['imageDigest']}],
        acceptedMediaTypes=['application/vnd.docker.distribution.manifest.v2+json','application/vnd.oci.image.manifest.v1+json'])
    images=response.get('images',[])
    if response.get('failures') or len(images)!=1 or images[0].get('imageId',{}).get('imageDigest')!=c['imageDigest']:raise Gate('Pinned image manifest is unavailable')
    raw=images[0].get('imageManifest')
    if not isinstance(raw,str) or len(raw.encode())>1_048_576 or 'sha256:'+hashlib.sha256(raw.encode()).hexdigest()!=c['imageDigest']:raise Gate('Registry manifest differs from its immutable digest')
    manifest=strict_loads(raw)
    if (manifest.get('schemaVersion')!=2 or manifest.get('mediaType') not in ('application/vnd.docker.distribution.manifest.v2+json','application/vnd.oci.image.manifest.v1+json')
        or not isinstance(manifest.get('config'),dict) or not re.fullmatch(r'sha256:[0-9a-f]{64}',manifest['config'].get('digest',''))):raise Gate('Release requires a pinned single-platform image manifest/config')
    return manifest['config']['digest']


def verify_release_image(aws,c,payload):
    if image_config_digest(aws,c)!=payload['image_config_digest']:raise Gate('Actual image configuration differs from the signed source-bound release')


def verify_container_source(repo,digest,revision,config_digest):
    reference=repo+'@'+digest
    run(['docker','pull',reference])
    value=strict_loads(run(['docker','image','inspect','--format','{"id":{{json .Id}},"labels":{{json .Config.Labels}},"repo_digests":{{json .RepoDigests}}}',reference],capture=True))
    if (not isinstance(value,dict) or value.get('id')!=config_digest or
        not isinstance(value.get('labels'),dict) or value['labels'].get('org.opencontainers.image.revision')!=revision or
        not isinstance(value.get('repo_digests'),list) or reference not in value['repo_digests']):raise Gate('Actual image config/revision differs from the reviewed source and pinned digest')


def require_clean_source(revision):
    if run(['git','rev-parse','HEAD'],capture=True).strip()!=revision or run(['git','status','--porcelain'],capture=True).strip():raise Gate('The reviewed release checkout changed during build')


def login(aws,c):
    if not shutil.which('docker'):raise Gate('Docker is unavailable; image build/promotion is unexecuted')
    auth=aws.client('ecr').get_authorization_token(registryIds=[c['account']])['authorizationData'][0]
    username,password=base64.b64decode(auth['authorizationToken']).decode().split(':',1)
    registry=auth['proxyEndpoint'].removeprefix('https://')
    # Docker stores this token in the caller's credential helper; never argv/logs.
    run(['docker','login','--username',username,'--password-stdin',registry],input=password,capture=True)
    return registry+'/otgd-'+c['environment']


def quiesce(aws,out):
    autoscale=aws.client('application-autoscaling')
    cluster_name=out['Cluster'].split('/')[-1]
    for name in [out['ApiService'],out['WorkerService']]:
        resource='service/'+cluster_name+'/'+name
        targets=autoscale.describe_scalable_targets(ServiceNamespace='ecs',ResourceIds=[resource],ScalableDimension='ecs:service:DesiredCount')['ScalableTargets']
        if targets:autoscale.register_scalable_target(ServiceNamespace='ecs',ResourceId=resource,ScalableDimension='ecs:service:DesiredCount',MinCapacity=0,MaxCapacity=targets[0]['MaxCapacity'],SuspendedState={'DynamicScalingInSuspended':True,'DynamicScalingOutSuspended':True,'ScheduledScalingSuspended':True})
        aws.client('ecs').update_service(cluster=out['Cluster'],service=name,desiredCount=0)
    deadline=time.monotonic()+600
    while time.monotonic()<deadline:
        try:services_stopped(aws,out);return
        except Gate:time.sleep(10)
    raise Gate('Services did not drain within ten minutes; do not restore')


def write_receipt(path,body):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(body,f,indent=2);f.write('\n')


def verify_maintenance(aws,out,path,c,operation):
    if not path or not path.exists():raise Gate('Supply the successful '+operation+' receipt')
    receipt=bounded_json(path)
    if (operation not in ('migrate','restore','verify-admission') or receipt.get('operation')!=operation or receipt.get('status')!='passed'
        or receipt.get('image_digest')!=c['imageDigest'] or receipt.get('environment')!=c['environment']
        or receipt.get('release_id')!=c['releaseId'] or receipt.get('account')!=c['account'] or receipt.get('region')!=c['region']
        or not isinstance(receipt.get('task_arn'),str)):raise Gate('Maintenance receipt does not match this release/account/region')
    result=aws.client('ecs').describe_tasks(cluster=out['Cluster'],tasks=[receipt['task_arn']])
    if result.get('failures') or len(result.get('tasks',[]))!=1:raise Gate('Maintenance task is no longer verifiable; rerun the bounded maintenance operation')
    completed=result['tasks'][0]
    containers=completed.get('containers',[])
    if (completed.get('lastStatus')!='STOPPED' or completed.get('taskArn')!=receipt['task_arn']
        or completed.get('clusterArn')!=out['Cluster'] or completed.get('taskDefinitionArn')!=out['MigrationTaskDefinition']
        or completed.get('startedBy')!='otgd-reviewed-maintenance' or len(containers)!=1
        or containers[0].get('name')!='migration' or type(containers[0].get('exitCode')) is not int or containers[0]['exitCode']!=0):raise Gate('Exact deployed maintenance task did not complete successfully')
    definition=aws.client('ecs').describe_task_definition(taskDefinition=completed['taskDefinitionArn'])['taskDefinition']
    definitions=definition.get('containerDefinitions',[])
    dns='amazonaws.com.cn' if c['region'].startswith('cn-') else 'amazonaws.com'
    expected_image=f"{c['account']}.dkr.ecr.{c['region']}.{dns}/otgd-{c['environment']}@{c['imageDigest']}"
    if (definition.get('taskDefinitionArn')!=out['MigrationTaskDefinition'] or len(definitions)!=1
        or definitions[0].get('name')!='migration' or definitions[0].get('image')!=expected_image):raise Gate('Maintenance executed a different task definition or image')
    overrides=completed.get('overrides')
    if not isinstance(overrides,dict) or set(overrides)!={'containerOverrides'} or len(overrides['containerOverrides'])!=1:raise Gate('Unexpected maintenance task/role/resource overrides')
    override=overrides['containerOverrides'][0]
    if not isinstance(override,dict) or not {'name','command'}.issubset(override) or set(override)-{'name','command','environment'} or override['name']!='migration':raise Gate('Unexpected maintenance container overrides')
    expected=['uv','run','--no-sync','python','-m','otgd.migrate'];environment=[]
    if operation=='verify-admission':
        expected=['uv','run','--no-sync','python','-m','otgd.recovery_authority']
        stopped=completed.get('stoppedAt')
        try:finished=datetime.fromisoformat(receipt.get('finished_at','').replace('Z','+00:00'))
        except (ValueError,TypeError):raise Gate('Admission receipt needs its actual UTC completion time') from None
        now=datetime.now(timezone.utc)
        if (not isinstance(stopped,datetime) or stopped.tzinfo is None or finished.tzinfo is None or finished.utcoffset().total_seconds()!=0 or
            not 0<=(now-stopped).total_seconds()<=900 or not 0<=(now-finished).total_seconds()<=900 or abs((finished-stopped).total_seconds())>60):
            raise Gate('Independent journal admission task must be fresh and bound to actual ECS completion')
    if operation=='restore':
        timestamp=receipt.get('backup_created_at')
        if not c.get('recoveryRequired') or not isinstance(timestamp,str):raise Gate('Restore receipt requires the reviewed recovery point')
        try:point=datetime.fromisoformat(timestamp.replace('Z','+00:00'))
        except ValueError:raise Gate('Invalid restore recovery timestamp') from None
        if point.tzinfo is None or point.utcoffset().total_seconds()!=0 or point>datetime.now(timezone.utc):raise Gate('Restore recovery timestamp must be a past UTC point')
        if c.get('databaseSnapshotIdentifier'):
            snapshot=aws.client('rds').describe_db_snapshots(DBSnapshotIdentifier=c['databaseSnapshotIdentifier'])['DBSnapshots'][0]
            actual=snapshot.get('OriginalSnapshotCreateTime',snapshot['SnapshotCreateTime'])
            if abs((point-actual).total_seconds())>1:raise Gate('Restore receipt differs from the selected actual snapshot point')
        expected=['uv','run','--no-sync','python','/app/scripts/restore-journal.py','--backup-created-at',timestamp,'--confirm-quiesced']
        environment=[{'name':'OTGD_RECOVERY_REQUIRED','value':'true'}]
    if override['command']!=expected or override.get('environment',[])!=environment:raise Gate('Maintenance command/environment does not match the exact reviewed operation')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['validate','preflight','synth','registry','build','approve-qa','promote','deploy-stopped','bootstrap','migrate','verify-admission','activate','quiesce','restore','replay','qa-destroy'])
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--release',type=Path);p.add_argument('--trusted-public-key',type=Path);p.add_argument('--signing-key',type=Path)
    p.add_argument('--source-config',type=Path);p.add_argument('--source-release',type=Path);p.add_argument('--source-profile')
    p.add_argument('--qa-evidence',type=Path);p.add_argument('--recovery-receipt',type=Path)
    p.add_argument('--admission-receipt',type=Path,help='Fresh exact-task independent journal admission verification')
    p.add_argument('--gate-evidence',type=Path,help='Exact-revision merge-gate artifact; its GitHub run and latest jobs are verified live')
    p.add_argument('--job-id');p.add_argument('--replay-id');p.add_argument('--reason-code');p.add_argument('--operator-ref')
    p.add_argument('--output',type=Path);p.add_argument('--backup-created-at');p.add_argument('--establish-new',action='store_true')
    p.add_argument('--confirm-qa-destroy',action='store_true')
    a=p.parse_args();registry=a.operation in ('registry','build');c=read_config(a.config,registry)
    if a.operation=='validate':print(json.dumps({'status':'valid','environment':c['environment'],'deployment_executed':False}));return
    if a.operation=='synth':cdk(a.config,c,'synth');return
    if a.operation=='approve-qa':
        if c['environment']!='qa' or not a.qa_evidence or not a.signing_key or not a.output:raise Gate('QA approval requires reviewed probe evidence, protected signing key and new output')
        source=require_release(a,c)
        expected={'account':c['account'],'region':c['region'],'image_digest':source['image_digest'],'release_id':source['release_id'],
            'qa_release_sha256':hashlib.sha256(a.release.read_bytes()).hexdigest(),'gate_provenance_sha256':source['gate_provenance_sha256']}
        approval=validate_qa_approval(bounded_json(a.qa_evidence),expected)
        require_trusted_signer(a.signing_key,a.trusted_public_key)
        sign_release(approval,a.output,a.signing_key)
        verify_qa_approval(a.output,a.trusted_public_key,expected)
        print(json.dumps({'status':'qa_operator_approval_signed','checks_executed':False,'approval_record':str(a.output)}));return
    aws=preflight(c,registry or a.operation=='promote')
    if a.operation=='preflight':print(json.dumps({'status':'preflight_passed','environment':c['environment'],'deployment_executed':False}));return
    if a.operation=='registry':cdk(a.config,c,'deploy',True);return
    if a.operation=='build':
        if c['environment']!='qa':raise Gate('Build in QA and promote the exact tested digest to production')
        if not a.output or not a.signing_key or not a.trusted_public_key:raise Gate('Build requires signed --output, protected --signing-key and independently trusted --trusted-public-key')
        if a.output.exists():raise Gate('Release output already exists; signed records are immutable')
        if run(['git','status','--porcelain'],capture=True).strip():raise Gate('Commit the reviewed source before release build')
        source=run(['git','rev-parse','HEAD'],capture=True).strip()
        if source!=c['releaseId']:raise Gate('releaseId must equal the checked-out reviewed Git commit')
        proof=verify_gate_file(a.gate_evidence,source)
        require_trusted_signer(a.signing_key,a.trusted_public_key)
        repo=login(aws,c);tag=repo+':'+source
        # Archive the immutable Git object: ignored/untracked files or concurrent
        # workspace edits can never become release build input.
        with tempfile.TemporaryDirectory(prefix='otgd-release-context-') as temporary:
            archive=Path(temporary)/'source.tar';context=Path(temporary)/'source';context.mkdir()
            run(['git','archive','--format=tar','--output',str(archive),source])
            with tarfile.open(archive) as packed:packed.extractall(context,filter='data')
            source_lock_hash=hashlib.sha256((context/'infra/images.lock.json').read_bytes()).hexdigest()
            run(['docker','buildx','build','--platform','linux/amd64','--provenance=false','--sbom=false','--label','org.opencontainers.image.revision='+source,'--file',str(context/'infra/local/service.Dockerfile'),'--tag',tag,'--push',str(context)])
        detail=aws.client('ecr').describe_images(repositoryName='otgd-'+c['environment'],imageIds=[{'imageTag':source}])['imageDetails'][0]
        image_c={**c,'imageDigest':detail['imageDigest']};config_digest=image_config_digest(aws,image_c)
        verify_container_source(repo,detail['imageDigest'],source,config_digest)
        require_clean_source(source)
        if sha256(verify_gate_file(a.gate_evidence,source))!=sha256(proof):raise Gate('GitHub gate run changed during image build; no release approval is signed')
        body={'schema_version':'1.0.0','environment':c['environment'],'account':c['account'],'region':c['region'],'repository':repo,'image_digest':detail['imageDigest'],'release_id':source,'database_schema':1,'inference_available':False,'created_at':datetime.now(timezone.utc).isoformat(),'source_image_lock_sha256':source_lock_hash,'gate_provenance':proof,'gate_provenance_sha256':sha256(proof),'oci_revision':source,'image_config_digest':config_digest}
        sign_release(body,a.output,a.signing_key);print(json.dumps({'status':'image_pushed_and_manifest_signed','image_digest':detail['imageDigest'],'release_record':str(a.output)}));return
    if a.operation=='promote':
        if c['environment']!='prod' or not a.source_config or not a.source_release or not a.signing_key or not a.output or not a.trusted_public_key:raise Gate('Promotion requires a QA source, signed records and trusted key')
        source_c=read_config(a.source_config)
        if source_c['environment']!='qa':raise Gate('Only tested QA images can promote to production')
        source=verify_release(a.source_release,a.trusted_public_key,source_c)
        if source['image_digest']!=c['imageDigest'] or source['release_id']!=c['releaseId']:raise Gate('Promotion must preserve the exact tested digest and source commit')
        proof=verify_gate_file(a.gate_evidence,c['releaseId'])
        if sha256(proof)!=source['gate_provenance_sha256']:raise Gate('Latest GitHub run does not match the signed QA release')
        expected={'account':source_c['account'],'region':source_c['region'],'image_digest':source['image_digest'],'release_id':source['release_id'],
            'qa_release_sha256':hashlib.sha256(a.source_release.read_bytes()).hexdigest(),'gate_provenance_sha256':source['gate_provenance_sha256']}
        if source_c['account']==c['account']:raise Gate('QA and production must use separate accounts')
        verify_qa_approval(a.qa_evidence,a.trusted_public_key,expected)
        require_trusted_signer(a.signing_key,a.trusted_public_key)
        if a.output.exists():raise Gate('Release output already exists; signed records are immutable')
        source_aws=preflight(source_c,profile=a.source_profile);source_repo=login(source_aws,source_c);target_repo=login(aws,c)
        verify_release_image(source_aws,source_c,source)
        verify_container_source(source_repo,c['imageDigest'],c['releaseId'],source['image_config_digest'])
        run(['docker','tag',source_repo+'@'+c['imageDigest'],target_repo+':'+c['releaseId']]);run(['docker','push',target_repo+':'+c['releaseId']])
        target=aws.client('ecr').describe_images(repositoryName='otgd-prod',imageIds=[{'imageTag':c['releaseId']}])['imageDetails'][0]
        if target['imageDigest']!=c['imageDigest']:raise Gate('Registry copy changed the manifest digest; production remains blocked')
        verify_release_image(aws,c,source)
        if sha256(verify_gate_file(a.gate_evidence,c['releaseId']))!=source['gate_provenance_sha256']:raise Gate('GitHub evidence changed during promotion; production approval remains blocked')
        verify_qa_approval(a.qa_evidence,a.trusted_public_key,expected)
        body={**source,'environment':'prod','account':c['account'],'region':c['region'],'repository':target_repo,'promoted_from_release_sha256':expected['qa_release_sha256'],'qa_evidence_sha256':hashlib.sha256(a.qa_evidence.read_bytes()).hexdigest(),'qa_source':expected,'created_at':datetime.now(timezone.utc).isoformat()}
        sign_release(body,a.output,a.signing_key);return
    if a.operation=='deploy-stopped':
        require_release(a,c,aws)
        if c['activateServices']:raise Gate('Set activateServices=false for bootstrap or maintenance deployment')
        cdk(a.config,c,'deploy');return
    out=stack_outputs(aws,c)
    if a.operation=='quiesce':quiesce(aws,out);print('API and worker services drained; autoscaling suspended.');return
    if a.operation in ('bootstrap','migrate','restore','verify-admission','replay') and (out.get('ImageDigest')!=c['imageDigest'] or out.get('ReleaseId')!=c['releaseId']):raise Gate('Deploy the reviewed maintenance image stopped before executing its operations')
    if a.operation=='replay':
        require_release(a,c,aws)
        values={'job-id':a.job_id,'replay-id':a.replay_id,'reason-code':a.reason_code,'operator-ref':a.operator_ref}
        if not all(values.values()) or not a.output or a.output.exists():raise Gate('Replay requires a job UUID, new replay UUID, reason code, operator reference and new output receipt')
        command=['uv','run','--no-sync','python','/app/scripts/replay-job.py']
        for k,v in values.items():command+=['--'+k,v]
        arn=task(aws,out,command)
        write_receipt(a.output,{'schema_version':'1.0.0','operation':'replay','environment':c['environment'],'account':c['account'],'region':c['region'],'release_id':c['releaseId'],'image_digest':c['imageDigest'],'job_id':a.job_id,'replay_id':a.replay_id,'task_arn':arn,'status':'passed','finished_at':datetime.now(timezone.utc).isoformat()});return
    if a.operation in ('bootstrap','migrate','restore','verify-admission'):
        require_release(a,c,aws);services_stopped(aws,out)
        if not a.output or a.output.exists():raise Gate('Supply a new --output path before executing maintenance')
        if a.operation=='bootstrap':command=['uv','run','--no-sync','python','/app/infra/local/bootstrap_resources.py','--verify-cloud',*(['--establish-new'] if a.establish_new else [])]
        elif a.operation=='migrate':command=['uv','run','--no-sync','python','-m','otgd.migrate']
        elif a.operation=='verify-admission':command=['uv','run','--no-sync','python','-m','otgd.recovery_authority']
        else:
            if not c['recoveryRequired'] or not a.backup_created_at:raise Gate('Restore needs recoveryRequired=true and actual backup timestamp')
            if out.get('RecoveryRequired')!='true' or out.get('DatabaseRecoveryOrigin')!=c.get('databaseSnapshotIdentifier','new'):raise Gate('Deployed database/recovery gate does not match the reviewed restore configuration')
            if c.get('databaseSnapshotIdentifier'):
                snapshot=aws.client('rds').describe_db_snapshots(DBSnapshotIdentifier=c['databaseSnapshotIdentifier'])['DBSnapshots'][0]
                expected=snapshot.get('OriginalSnapshotCreateTime',snapshot['SnapshotCreateTime'])
                supplied=datetime.fromisoformat(a.backup_created_at.replace('Z','+00:00'))
                if supplied.tzinfo is None or abs((supplied-expected).total_seconds())>1:raise Gate('Recovery timestamp differs from the actual selected snapshot recovery point')
            command=['uv','run','--no-sync','python','/app/scripts/restore-journal.py','--backup-created-at',a.backup_created_at,'--confirm-quiesced']
        arn=task(aws,out,command,{'OTGD_RECOVERY_REQUIRED':'true'} if a.operation=='restore' else None)
        write_receipt(a.output,{'schema_version':'1.0.0','operation':a.operation,'environment':c['environment'],'account':c['account'],'region':c['region'],'image_digest':c['imageDigest'],'release_id':c['releaseId'],'task_arn':arn,'backup_created_at':a.backup_created_at if a.operation=='restore' else None,'status':'passed','finished_at':datetime.now(timezone.utc).isoformat()});print(json.dumps({'status':'maintenance_passed','task_arn':arn,'services_still_stopped':True}));return
    if a.operation=='activate':
        require_release(a,c,aws)
        if not c['activateServices']:raise Gate('Activation requires an explicitly reviewed activateServices=true configuration')
        verify_maintenance(aws,out,a.output,c,'migrate')
        if c['recoveryRequired']:verify_maintenance(aws,out,a.recovery_receipt,c,'restore')
        verify_maintenance(aws,out,a.admission_receipt,c,'verify-admission')
        require_release(a,c,aws)
        cdk(a.config,c,'deploy')
        aws.client('ecs').get_waiter('services_stable').wait(cluster=out['Cluster'],services=[out['ApiService'],out['WorkerService']],WaiterConfig={'Delay':15,'MaxAttempts':40})
        print('Service rollout is stable. Complete protected endpoint, queue and alarm-delivery probes before participant access.');return
    if a.operation=='qa-destroy':
        if c['environment']!='qa' or not a.confirm_qa_destroy:raise Gate('Only QA can be destroyed here, with --confirm-qa-destroy')
        services_stopped(aws,out);cdk(a.config,c,'destroy');return

if __name__=='__main__':
    try:main()
    except Gate as error:print('BLOCKED: '+str(error),file=sys.stderr);raise SystemExit(2)
    except Exception as error:
        print('BLOCKED: dependency/action failed ('+type(error).__name__+'); inspect the command-specific protected logs. No success is inferred.',file=sys.stderr);raise SystemExit(2)
