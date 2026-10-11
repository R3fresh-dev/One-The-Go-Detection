#!/usr/bin/env python3
"""Explicit, bounded deployment operations. No action executes merely on import.

Use the API's locked uv environment. AWS credentials come from the normal SDK
provider chain; secrets are injected into ECS, never read into shell arguments.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
INFRA=ROOT/'infra'
sys.path.insert(0,str(ROOT/'services'/'api'))
import boto3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from otgd.canonical import canonical,strict_loads


class Gate(RuntimeError):pass


def run(args,*,cwd=ROOT,capture=False,input=None):
    return subprocess.run(args,cwd=cwd,text=True,check=True,capture_output=capture,input=input).stdout


def read_config(path,registry=False):
    if not (INFRA/'node_modules').exists():raise Gate('Run npm ci in infra first')
    return json.loads(run(['node','--import','tsx','bin/validate.ts',str(path.resolve()),*(['--registry'] if registry else [])],cwd=INFRA,capture=True))


def session(c,profile=None):return boto3.Session(region_name=c['region'],profile_name=profile)


def preflight(c,registry=False,profile=None):
    aws=session(c,profile)
    if aws.client('sts').get_caller_identity()['Account']!=c['account']:raise Gate('AWS credential account differs from the deployment configuration')
    certificate=aws.client('acm').describe_certificate(CertificateArn=c['certificateArn'])['Certificate']
    domains=certificate.get('SubjectAlternativeNames',[])
    def covers(name):return name==c['domain'] or (name.startswith('*.') and c['domain'].split('.',1)[1:]==[name[2:]])
    if certificate['Status']!='ISSUED' or not any(covers(x) for x in domains):raise Gate('ACM certificate is not issued for the configured API domain')
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


def sign_release(body,path,key_path):
    raw=canonical(body);signature=private_key(key_path).sign(raw)
    output={'schema_version':'1.0.0','payload':body,'payload_sha256':hashlib.sha256(raw).hexdigest(),'algorithm':'Ed25519','signature':base64.b64encode(signature).decode()}
    if path.exists():raise Gate('A signed release record is immutable; choose a new path')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(output,f,indent=2);f.write('\n')


def verify_release(path,public_path,c):
    envelope=strict_loads(path.read_bytes());payload=envelope['payload'];raw=canonical(payload)
    if envelope.get('schema_version')!='1.0.0' or envelope.get('algorithm')!='Ed25519' or envelope.get('payload_sha256')!=hashlib.sha256(raw).hexdigest():raise Gate('Invalid release envelope')
    public=serialization.load_pem_public_key(public_path.read_bytes())
    if not isinstance(public,Ed25519PublicKey):raise Gate('Expected trusted Ed25519 release key')
    public.verify(base64.b64decode(envelope['signature'],validate=True),raw)
    if payload.get('environment')!=c['environment'] or payload.get('account')!=c['account'] or payload.get('region')!=c['region'] or payload.get('image_digest')!=c['imageDigest'] or payload.get('release_id')!=c['releaseId']:raise Gate('Signed release does not bind this environment/account/digest')
    if payload.get('database_schema')!=1 or payload.get('inference_available') is not False:raise Gate('Unsupported schema or inference release')
    if c['environment']=='prod' and any(not re.fullmatch(r'[0-9a-f]{64}',payload.get(k,'')) for k in ['promoted_from_release_sha256','qa_evidence_sha256']):raise Gate('Production requires a signed promotion from the tested QA digest')
    return payload


def require_release(args,c):
    if not args.release or not args.trusted_public_key:raise Gate('Supply --release and independently trusted --trusted-public-key')
    return verify_release(args.release,args.trusted_public_key,c)


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
    receipt=strict_loads(path.read_bytes())
    if receipt.get('operation')!=operation or receipt.get('status')!='passed' or receipt.get('image_digest')!=c['imageDigest'] or receipt.get('environment')!=c['environment']:raise Gate('Maintenance receipt does not match this release')
    result=aws.client('ecs').describe_tasks(cluster=out['Cluster'],tasks=[receipt['task_arn']])
    if result.get('failures') or len(result.get('tasks',[]))!=1:raise Gate('Maintenance task is no longer verifiable; rerun the bounded maintenance operation')
    completed=result['tasks'][0]
    if completed['lastStatus']!='STOPPED' or any(x.get('exitCode')!=0 for x in completed['containers']):raise Gate('Maintenance task did not complete successfully')
    definition=aws.client('ecs').describe_task_definition(taskDefinition=completed['taskDefinitionArn'])['taskDefinition']
    image=next(x['image'] for x in definition['containerDefinitions'] if x['name']=='migration')
    if not image.endswith('@'+c['imageDigest']):raise Gate('Maintenance executed a different image')
    command=next(x['command'] for x in completed['overrides']['containerOverrides'] if x['name']=='migration')
    expected='otgd.migrate' if operation=='migrate' else '/app/scripts/restore-journal.py'
    if expected not in command:raise Gate('Maintenance receipt refers to another operation')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['validate','preflight','synth','registry','build','promote','deploy-stopped','bootstrap','migrate','activate','quiesce','restore','replay','qa-destroy'])
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--release',type=Path);p.add_argument('--trusted-public-key',type=Path);p.add_argument('--signing-key',type=Path)
    p.add_argument('--source-config',type=Path);p.add_argument('--source-release',type=Path);p.add_argument('--source-profile')
    p.add_argument('--qa-evidence',type=Path);p.add_argument('--recovery-receipt',type=Path)
    p.add_argument('--job-id');p.add_argument('--replay-id');p.add_argument('--reason-code');p.add_argument('--operator-ref')
    p.add_argument('--output',type=Path);p.add_argument('--backup-created-at');p.add_argument('--establish-new',action='store_true')
    p.add_argument('--confirm-qa-destroy',action='store_true')
    a=p.parse_args();registry=a.operation in ('registry','build');c=read_config(a.config,registry)
    if a.operation=='validate':print(json.dumps({'status':'valid','environment':c['environment'],'deployment_executed':False}));return
    if a.operation=='synth':cdk(a.config,c,'synth');return
    aws=preflight(c,registry or a.operation=='promote')
    if a.operation=='preflight':print(json.dumps({'status':'preflight_passed','environment':c['environment'],'deployment_executed':False}));return
    if a.operation=='registry':cdk(a.config,c,'deploy',True);return
    if a.operation=='build':
        if c['environment']!='qa':raise Gate('Build in QA and promote the exact tested digest to production')
        if not a.output or not a.signing_key:raise Gate('Build requires signed --output and protected --signing-key')
        if a.output.exists():raise Gate('Release output already exists; signed records are immutable')
        if run(['git','status','--porcelain'],capture=True).strip():raise Gate('Commit the reviewed source before release build')
        source=run(['git','rev-parse','HEAD'],capture=True).strip()
        if source!=c['releaseId']:raise Gate('releaseId must equal the checked-out reviewed Git commit')
        repo=login(aws,c);tag=repo+':'+source
        run(['docker','buildx','build','--platform','linux/amd64','--provenance=false','--sbom=false','--file','infra/local/service.Dockerfile','--tag',tag,'--push','.'])
        detail=aws.client('ecr').describe_images(repositoryName='otgd-'+c['environment'],imageIds=[{'imageTag':source}])['imageDetails'][0]
        body={'schema_version':'1.0.0','environment':c['environment'],'account':c['account'],'region':c['region'],'repository':repo,'image_digest':detail['imageDigest'],'release_id':source,'database_schema':1,'inference_available':False,'created_at':datetime.now(timezone.utc).isoformat(),'source_image_lock_sha256':hashlib.sha256((INFRA/'images.lock.json').read_bytes()).hexdigest()}
        sign_release(body,a.output,a.signing_key);print(json.dumps({'status':'image_pushed_and_manifest_signed','image_digest':detail['imageDigest'],'release_record':str(a.output)}));return
    if a.operation=='promote':
        if c['environment']!='prod' or not a.source_config or not a.source_release or not a.signing_key or not a.output or not a.trusted_public_key:raise Gate('Promotion requires a QA source, signed records and trusted key')
        source_c=read_config(a.source_config)
        if source_c['environment']!='qa':raise Gate('Only tested QA images can promote to production')
        source=verify_release(a.source_release,a.trusted_public_key,source_c)
        if source['image_digest']!=c['imageDigest'] or source['release_id']!=c['releaseId']:raise Gate('Promotion must preserve the exact tested digest and source commit')
        if not a.qa_evidence:raise Gate('Promotion requires the actual QA validation evidence file')
        evidence=strict_loads(a.qa_evidence.read_bytes())
        required_gates={'private_network','conditional_upload','worker_kill_matrix','deletion_restore','authenticated_export','alarm_delivery'}
        if evidence.get('environment')!='qa' or evidence.get('image_digest')!=c['imageDigest'] or evidence.get('status')!='passed' or not required_gates.issubset(evidence.get('passed_gates',[])):raise Gate('QA evidence is incomplete or does not cover this exact image')
        if a.output.exists():raise Gate('Release output already exists; signed records are immutable')
        source_aws=preflight(source_c,profile=a.source_profile);source_repo=login(source_aws,source_c);target_repo=login(aws,c)
        run(['docker','pull',source_repo+'@'+c['imageDigest']]);run(['docker','tag',source_repo+'@'+c['imageDigest'],target_repo+':'+c['releaseId']]);run(['docker','push',target_repo+':'+c['releaseId']])
        target=aws.client('ecr').describe_images(repositoryName='otgd-prod',imageIds=[{'imageTag':c['releaseId']}])['imageDetails'][0]
        if target['imageDigest']!=c['imageDigest']:raise Gate('Registry copy changed the manifest digest; production remains blocked')
        body={**source,'environment':'prod','account':c['account'],'region':c['region'],'repository':target_repo,'promoted_from_release_sha256':hashlib.sha256(a.source_release.read_bytes()).hexdigest(),'qa_evidence_sha256':hashlib.sha256(a.qa_evidence.read_bytes()).hexdigest(),'created_at':datetime.now(timezone.utc).isoformat()}
        sign_release(body,a.output,a.signing_key);return
    if a.operation=='deploy-stopped':
        require_release(a,c)
        if c['activateServices']:raise Gate('Set activateServices=false for bootstrap or maintenance deployment')
        cdk(a.config,c,'deploy');return
    out=stack_outputs(aws,c)
    if a.operation=='quiesce':quiesce(aws,out);print('API and worker services drained; autoscaling suspended.');return
    if a.operation in ('bootstrap','migrate','restore','replay') and (out.get('ImageDigest')!=c['imageDigest'] or out.get('ReleaseId')!=c['releaseId']):raise Gate('Deploy the reviewed maintenance image stopped before executing its operations')
    if a.operation=='replay':
        require_release(a,c)
        values={'job-id':a.job_id,'replay-id':a.replay_id,'reason-code':a.reason_code,'operator-ref':a.operator_ref}
        if not all(values.values()) or not a.output or a.output.exists():raise Gate('Replay requires a job UUID, new replay UUID, reason code, operator reference and new output receipt')
        command=['uv','run','--no-sync','python','/app/scripts/replay-job.py']
        for k,v in values.items():command+=['--'+k,v]
        arn=task(aws,out,command)
        write_receipt(a.output,{'schema_version':'1.0.0','operation':'replay','environment':c['environment'],'image_digest':c['imageDigest'],'job_id':a.job_id,'replay_id':a.replay_id,'task_arn':arn,'status':'passed','finished_at':datetime.now(timezone.utc).isoformat()});return
    if a.operation in ('bootstrap','migrate','restore'):
        require_release(a,c);services_stopped(aws,out)
        if not a.output or a.output.exists():raise Gate('Supply a new --output path before executing maintenance')
        if a.operation=='bootstrap':command=['uv','run','--no-sync','python','/app/infra/local/bootstrap_resources.py','--verify-cloud',*(['--establish-new'] if a.establish_new else [])]
        elif a.operation=='migrate':command=['uv','run','--no-sync','python','-m','otgd.migrate']
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
        write_receipt(a.output,{'schema_version':'1.0.0','operation':a.operation,'environment':c['environment'],'image_digest':c['imageDigest'],'release_id':c['releaseId'],'task_arn':arn,'status':'passed','finished_at':datetime.now(timezone.utc).isoformat()});print(json.dumps({'status':'maintenance_passed','task_arn':arn,'services_still_stopped':True}));return
    if a.operation=='activate':
        require_release(a,c)
        if not c['activateServices']:raise Gate('Activation requires an explicitly reviewed activateServices=true configuration')
        verify_maintenance(aws,out,a.output,c,'migrate')
        if c['recoveryRequired']:verify_maintenance(aws,out,a.recovery_receipt,c,'restore')
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
