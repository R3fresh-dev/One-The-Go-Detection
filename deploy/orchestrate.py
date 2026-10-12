"""One command per environment, with real release admission at every stage."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:]=[entry for entry in sys.path if Path(entry).resolve()!=ROOT/'deploy']
sys.path.insert(0,str(ROOT))

import argparse
import contextlib
import hashlib
import json
import os
import subprocess
import time
import uuid

from deploy import platform, web_artifact
from deploy.provenance import Gate, bounded_json, verify_qa_approval


def parser(environment):
    p=argparse.ArgumentParser(description=f'Deploy reviewed infrastructure, API/worker and web UI to AWS {environment}')
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--gate-evidence',type=Path)
    p.add_argument('--trusted-public-key',type=Path)
    p.add_argument('--signing-key',type=Path)
    p.add_argument('--release',type=Path,help='Reuse a signed service release; QA otherwise builds, production otherwise promotes')
    p.add_argument('--qa-evidence',type=Path)
    p.add_argument('--source-config',type=Path);p.add_argument('--source-release',type=Path);p.add_argument('--source-profile')
    p.add_argument('--source-web-release',type=Path);p.add_argument('--source-web-artifact',type=Path)
    p.add_argument('--profile',help='Normal AWS SDK profile for the target account')
    p.add_argument('--work-dir',type=Path,default=ROOT/'.local/deploy'/environment)
    p.add_argument('--establish-new',action='store_true',help='Only for the first empty environment; creates journal continuity')
    p.add_argument('--backup-created-at',help='Reviewed UTC snapshot point; required for recovery deployments')
    p.add_argument('--plan',action='store_true',help='Validate inputs and print stages without credentials, builds, or AWS writes')
    return p


def steps(environment,provided_release=False,recovery=False):
    stages=['preflight','cdk-bootstrap','registry']
    stages+=[] if provided_release else ['build' if environment=='qa' else 'promote']
    return stages+['quiesce-existing','deploy-stopped','bootstrap','migrate']+(['restore'] if recovery else [])+['build-signed-web','verify-admission','activate','worker-progress-health','publish-web','verify-public-access']


def invoke(operation,config,args,**extra):
    command=[sys.executable,str(ROOT/'deploy/platform.py'),operation,'--config',str(config)]
    for name in ('release','trusted_public_key','gate_evidence','qa_evidence'):
        value=getattr(args,name,None)
        if value:command+=['--'+name.replace('_','-'),str(value)]
    for name,value in extra.items():
        if value is True:command+=['--'+name.replace('_','-')]
        elif value is not None and value is not False:command+=['--'+name.replace('_','-'),str(value)]
    subprocess.run(command,cwd=ROOT,check=True,env=platform.deployment_environment())


@contextlib.contextmanager
def target_profile(profile):
    previous=os.environ.get('AWS_PROFILE')
    if profile:os.environ['AWS_PROFILE']=profile
    try:yield
    finally:
        if previous is None:os.environ.pop('AWS_PROFILE',None)
        else:os.environ['AWS_PROFILE']=previous


class StageJournal:
    """Credential-free operator recovery evidence, never an inferred rollback."""
    def __init__(self,work,c):
        self.work=work;self.path=work/'deployment-state.json'
        self.state={'schema_version':'1.0.0','environment':c['environment'],'account':c['account'],'region':c['region'],
            'release_id':c['releaseId'],'status':'running','current_stage':None,'completed_stages':[],
            'completed_receipts':{},'rollback_executed':False}
        self.persist()

    def persist(self):
        receipts={}
        for name in ('bootstrap.json','migration.json','restore.json','admission.json','service-release.json','web-release.json','deployment.json'):
            path=self.work/name
            if path.is_file():receipts[name]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        self.state['completed_receipts']=receipts
        raw=json.dumps(self.state,indent=2).encode()
        if len(raw)>65_536:raise Gate('Deployment stage journal exceeds its bounded size')
        temporary=self.path.with_suffix('.json.new')
        fd=os.open(temporary,os.O_CREAT|os.O_WRONLY|os.O_TRUNC|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as stream:os.fchmod(stream.fileno(),0o600);stream.write(raw)
        os.replace(temporary,self.path)

    def call(self,name,function,*args,**kwargs):
        self.state['current_stage']=name;self.persist()
        result=function(*args,**kwargs)
        self.state['completed_stages'].append(name);self.persist()
        return result

    def __enter__(self):return self

    def __exit__(self,kind,error,traceback):
        if error is not None:
            self.state.update(status='failed',failed_stage=self.state['current_stage'],failure_type=kind.__name__)
        self.persist()
        if error is not None:print('Recovery state: '+str(self.path)+'; inspect completed stages before retry. No rollback is inferred.',file=sys.stderr)
        return False

    def finish(self):
        self.state.update(status='public_transport_verified',current_stage=None);self.persist()


def admit_source_web(args,c):
    if not all((args.source_config,args.source_release,args.source_web_release,args.source_web_artifact,args.qa_evidence)):
        raise Gate('Production requires the tested QA config/service/web records, archive and signed QA approval')
    source_c=platform.read_config(args.source_config)
    if source_c['environment']!='qa' or source_c['account']==c['account'] or source_c['releaseId']!=c['releaseId']:
        raise Gate('Production must preserve the reviewed source from a separate QA account')
    source=platform.verify_release(args.source_release,args.trusted_public_key,source_c)
    expected={'account':source_c['account'],'region':source_c['region'],'image_digest':source['image_digest'],'release_id':source['release_id'],
        'qa_release_sha256':hashlib.sha256(args.source_release.read_bytes()).hexdigest(),'gate_provenance_sha256':source['gate_provenance_sha256']}
    approval=verify_qa_approval(args.qa_evidence,args.trusted_public_key,expected)
    web,files=web_artifact.verify(args.source_web_release,args.source_web_artifact,args.trusted_public_key,source_c,args.source_release,source)
    digest=hashlib.sha256(args.source_web_release.read_bytes()).hexdigest()
    if 'web_customer_access' not in approval['passed_gates'] or approval['evidence_refs'].get('web_customer_access')!='sha256:'+digest:
        raise Gate('Signed QA approval must explicitly bind the tested web release envelope')
    results=approval['evidence_refs'].get('web_customer_access_results')
    if not isinstance(results,str) or not results.startswith(('https://','s3://')) or results==approval['evidence_refs']['web_customer_access']:
        raise Gate('Signed QA approval must separately reference actual protected authenticated browser acceptance results')
    return source_c,source,web,digest


def worker_health(aws,out):
    ecs=aws.client('ecs');deadline=time.monotonic()+600
    while time.monotonic()<deadline:
        ids=ecs.list_tasks(cluster=out['Cluster'],serviceName=out['WorkerService'],desiredStatus='RUNNING')['taskArns']
        if ids:
            rows=ecs.describe_tasks(cluster=out['Cluster'],tasks=ids)
            if not rows.get('failures') and len(rows['tasks'])==len(ids) and all(task.get('lastStatus')=='RUNNING' and any(container.get('name')=='worker' and container.get('healthStatus')=='HEALTHY' for container in task.get('containers',[])) for task in rows['tasks']):return
        time.sleep(10)
    raise Gate('Actual ECS worker progress health did not become healthy within ten minutes')


def deployment(args,environment):
    c=platform.read_config(args.config,registry=True)
    if c['environment']!=environment:raise Gate('This wrapper only deploys its named environment')
    if args.establish_new and c['recoveryRequired']:raise Gate('Recovery cannot establish a new empty deletion journal')
    if c['recoveryRequired'] and not args.backup_created_at:raise Gate('Recovery deployment requires the actual reviewed backup-created-at point')
    if args.plan:
        return {'environment':environment,'stages':steps(environment,bool(args.release),c['recoveryRequired']),
            'deployment_executed':False,'web_custom_domain':c.get('webDomain'),'missing_live_inputs':['AWS account credentials','signed exact-revision gate evidence','release authority','actual cloud acceptance']}
    if not all((args.gate_evidence,args.trusted_public_key,args.signing_key)):raise Gate('Supply live gate evidence and the independently trusted release authority')
    platform.require_clean_source(c['releaseId'])
    platform.require_trusted_signer(args.signing_key,args.trusted_public_key)
    platform.verify_gate_file(args.gate_evidence,c['releaseId'])
    qa_web_digest=None
    if environment=='prod':
        source_c,source,source_web,qa_web_digest=admit_source_web(args,c)
        c={**c,'imageDigest':source['image_digest']}
    work=args.work_dir.resolve()/c['releaseId']/uuid.uuid4().hex
    if work.is_relative_to(ROOT) and subprocess.run(['git','check-ignore','--quiet',str(work)],cwd=ROOT).returncode!=0:
        raise Gate('Deployment work directory inside the checkout must be ignored; use .local/deploy')
    work.mkdir(parents=True,exist_ok=True)
    stopped=work/'stopped.local.json';active=work/'active.local.json'
    stopped.write_text(json.dumps({**c,'activateServices':False},indent=2)+'\n')
    with target_profile(args.profile),StageJournal(work,c) as journal:
        aws=journal.call('preflight',platform.preflight,c,registry=True)
        journal.call('cdk-bootstrap',platform.run,['npm','exec','--','cdk','bootstrap','aws://'+c['account']+'/'+c['region']],cwd=platform.INFRA)
        journal.call('registry',invoke,'registry',stopped,args)
        if not args.release:
            args.release=work/'service-release.json'
            if environment=='qa':journal.call('build',invoke,'build',stopped,args,signing_key=args.signing_key,output=args.release)
            else:journal.call('promote',invoke,'promote',stopped,args,source_config=args.source_config,source_release=args.source_release,source_profile=args.source_profile,signing_key=args.signing_key,output=args.release)
        raw=bounded_json(args.release)
        c={**c,'imageDigest':raw['payload']['image_digest']}
        stopped.write_text(json.dumps({**c,'activateServices':False},indent=2)+'\n')
        active.write_text(json.dumps({**c,'activateServices':True},indent=2)+'\n')
        service=journal.call('release-admission',platform.require_release,args,c,aws)
        def prior_stack():
            try:return platform.stack_outputs(aws,c)
            except Exception as error:
                # Only an actually absent stack means a first deployment.
                if not (hasattr(error,'response') and error.response.get('Error',{}).get('Code')=='ValidationError' and 'does not exist' in error.response['Error'].get('Message','')):raise
                return None
        old=journal.call('inspect-prior-stack',prior_stack)
        if old:journal.call('quiesce-existing',platform.quiesce,aws,old)
        journal.call('deploy-stopped',invoke,'deploy-stopped',stopped,args)
        bootstrap=work/'bootstrap.json';migration=work/'migration.json';recovery=work/'restore.json'
        journal.call('bootstrap',invoke,'bootstrap',stopped,args,output=bootstrap,establish_new=args.establish_new)
        journal.call('migrate',invoke,'migrate',stopped,args,output=migration)
        if c['recoveryRequired']:journal.call('restore',invoke,'restore',stopped,args,output=recovery,backup_created_at=args.backup_created_at)
        out=journal.call('inspect-stopped-stack',platform.stack_outputs,aws,c)
        archive=work/'web.zip';web_record=work/'web-release.json'
        web=journal.call('build-signed-web',web_artifact.build,platform,args,c,out,service,archive,web_record)
        if environment=='prod':
            source_c,source,source_web,digest=journal.call('qa-web-readmission',admit_source_web,args,c)
            if web['package_lock_sha256']!=source_web['package_lock_sha256']:raise Gate('Production web dependencies differ from the tested QA source')
        admission=work/'admission.json'
        journal.call('verify-admission',invoke,'verify-admission',stopped,args,output=admission)
        journal.call('activate',invoke,'activate',active,args,output=migration,recovery_receipt=recovery if c['recoveryRequired'] else None,admission_receipt=admission)
        out=journal.call('inspect-active-stack',platform.stack_outputs,aws,c)
        journal.call('worker-progress-health',worker_health,aws,out)
        journal.call('publication-release-admission',platform.require_release,args,c,aws)
        web,files=journal.call('publication-web-admission',web_artifact.verify,web_record,archive,args.trusted_public_key,c,args.release,service,out,qa_web_release_sha256=qa_web_digest)
        publication=journal.call('publish-web',web_artifact.publish,aws,out,web,files)
        public=journal.call('verify-public-access',web_artifact.verify_access,out,web,files)
        receipt={'schema_version':'1.0.0','operation':'one-shot-deploy','status':'public_transport_verified','environment':environment,
            'account':c['account'],'region':c['region'],'release_id':c['releaseId'],'image_digest':c['imageDigest'],
            'service_release':str(args.release),'web_release':str(web_record),'web_artifact':str(archive),'web_origin':out['WebOrigin'],
            'cloudwatch_dashboard_name':out.get('CloudWatchDashboardName'),'cloudwatch_dashboard_url':out.get('CloudWatchDashboardUrl'),
            'migration_receipt':str(migration),'admission_receipt':str(admission),'publication':publication,'public_checks':public,'worker_progress_health':'passed','cloud_operational_acceptance':'not_inferred'}
        journal.call('write-access-receipt',platform.write_receipt,work/'deployment.json',receipt)
        journal.finish()
        return receipt


def entrypoint(environment,argv=None):
    try:
        result=deployment(parser(environment).parse_args(argv),environment)
        print(json.dumps(result,indent=2));return 0
    except Exception as error:
        message=str(error) if isinstance(error,Gate) else type(error).__name__+'; inspect the protected stage logs'
        print('BLOCKED: '+message,file=sys.stderr);return 2
