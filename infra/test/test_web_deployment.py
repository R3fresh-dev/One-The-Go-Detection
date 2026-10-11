"""Deployment admission/failure unit tests; fixtures are not AWS acceptance."""
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import Mock, patch
import zipfile

from botocore.exceptions import ClientError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import httpx
from deploy import orchestrate, platform, register_cname, web_artifact as web
from deploy.provenance import Gate, sha256


class WebArtifactTest(unittest.TestCase):
    def test_browser_build_environment_retains_transport_settings_without_deploy_credentials(self):
        runtime={'environment':'qa','api_url':'https://api.qa.otgd.test','issuer':'https://cognito-idp.us-east-2.amazonaws.com/pool','client_id':'public-client'}
        secrets={key:'fixture-secret' for key in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN','AWS_PROFILE','AWS_CONFIG_FILE',
            'GH_TOKEN','GITHUB_TOKEN','OTGD_DATABASE_URL','OPENAI_API_KEY','CUSTOM_SERVICE_TOKEN','SERVICE_PASSWORD','SSH_AUTH_SOCK','EAS_TOKEN','APPETIZE_API_TOKEN')}
        transport={'HTTPS_PROXY':'http://proxy.test:80','NODE_EXTRA_CA_CERTS':'/approved/ca.pem','npm_config_registry':'https://registry.npmjs.org','PATH':'/usr/bin'}
        with patch.dict(os.environ,{**secrets,**transport,'EXPO_PUBLIC_API_URL':'https://foreign.test','EXPO_PUBLIC_HOSTED_PREVIEW':'true','NODE_OPTIONS':'--require /untrusted.js'},clear=True):
            environment=web.build_environment(runtime)
        self.assertFalse(set(secrets)&set(environment))
        for key,value in transport.items():self.assertEqual(environment[key],value)
        self.assertEqual(environment['EXPO_PUBLIC_APP_ENV'],'qa');self.assertEqual(environment['APP_ENV'],'qa')
        self.assertEqual(environment['EXPO_PUBLIC_API_URL'],runtime['api_url'])
        self.assertEqual(environment['EXPO_PUBLIC_HOSTED_PREVIEW'],'false');self.assertNotIn('NODE_OPTIONS',environment)

    def test_each_signed_environment_export_rebuilds_stale_hosted_metro_cache(self):
        # Model the observed non-environment-keyed Metro cache. This exercises
        # the actual deployer build orchestration, packaging and signature;
        # the subprocess double is not real Expo or AWS acceptance evidence.
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            _,_,_,base,service,service_payload,public,_,_,out=self.fixture(root)
            reviewed=root/'reviewed/apps/mobile';reviewed.mkdir(parents=True)
            (reviewed/'package-lock.json').write_text('{"name":"fictional-reviewed-fixture","lockfileVersion":3}')
            (reviewed/'package.json').write_text('{"scripts":{"export:web":"expo export --platform web"}}')
            cached={'EXPO_PUBLIC_APP_ENV':'local','EXPO_PUBLIC_API_URL':'http://127.0.0.1:8000','EXPO_PUBLIC_HOSTED_PREVIEW':'true'}
            exports=[]
            def archive(command):
                self.assertEqual(command[:3],['git','archive','--format=tar'])
                with tarfile.open(command[4],'w') as output:output.add(root/'reviewed/apps',arcname='apps')
            def subprocess_run(command,*,cwd,env,check):
                self.assertTrue(check)
                if command==['npm','ci']:return
                exports.append(command)
                if '--clear' in command:
                    cached.clear();cached.update({key:value for key,value in env.items() if key.startswith('EXPO_PUBLIC_')})
                dist=cwd/'dist';dist.mkdir()
                (dist/'index.html').write_text('<script src="app.js" defer></script>')
                (dist/'app.js').write_text(json.dumps(cached,sort_keys=True))
            with patch.object(platform,'require_clean_source') as clean,patch.object(platform,'require_release',return_value=service_payload),patch.object(platform,'run',side_effect=archive),patch.object(web.subprocess,'run',side_effect=subprocess_run):
                qa_record=None
                for environment in ('qa','prod'):
                    config={**base,'environment':environment,'domain':'api.'+environment+'.otgd.test'}
                    outputs={**out,'ApiOrigin':'https://'+config['domain']}
                    args=Mock(release=service,signing_key=root/'private.pem',trusted_public_key=public,source_web_release=qa_record)
                    artifact=root/(environment+'-web.zip');record=root/(environment+'-web-release.json')
                    payload=web.build(platform,args,config,outputs,service_payload,artifact,record)
                    with zipfile.ZipFile(artifact) as output:runtime=json.loads(output.read('app.js'))
                    self.assertEqual(runtime['EXPO_PUBLIC_APP_ENV'],environment)
                    self.assertEqual(runtime['EXPO_PUBLIC_API_URL'],outputs['ApiOrigin'])
                    self.assertEqual(runtime['EXPO_PUBLIC_OAUTH_ISSUER'],outputs['Issuer'])
                    self.assertEqual(runtime['EXPO_PUBLIC_HOSTED_PREVIEW'],'false')
                    verified,_=web.verify(record,artifact,public,config,service,service_payload,outputs,
                        qa_web_release_sha256=hashlib.sha256(qa_record.read_bytes()).hexdigest() if qa_record else None)
                    self.assertEqual(verified,payload)
                    if environment=='qa':qa_record=record
                self.assertEqual(clean.call_count,4)
            self.assertEqual(exports,[['npm','run','export:web','--','--clear']]*2)

    def fixture(self,root):
        directory=root/'dist';directory.mkdir();(directory/'index.html').write_text('<script src="app.js" defer></script>');(directory/'app.js').write_text('console.log("measurement-only")')
        archive=root/'web.zip';manifest=web.package(directory,archive)
        key=Ed25519PrivateKey.generate();private=root/'private.pem';public=root/'public.pem'
        private.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));private.chmod(0o600)
        public.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
        c={'environment':'qa','account':'123456789012','region':'us-east-2','releaseId':'c'*40,'imageDigest':'sha256:'+'a'*64,'domain':'api.qa.otgd.test'}
        service=root/'service.json';service.write_text('signed-service-fixture');service_payload={'gate_provenance_sha256':'f'*64}
        runtime={'environment':'qa','api_url':'https://'+c['domain'],'issuer':'https://cognito-idp.us-east-2.amazonaws.com/pool','client_id':'public-client','web_origin':'https://d123.cloudfront.net','callback_uri':'https://d123.cloudfront.net/'}
        body={'schema_version':'1.0.0','purpose':'web-release','environment':c['environment'],'account':c['account'],'region':c['region'],'release_id':c['releaseId'],'image_digest':c['imageDigest'],
            'service_release_sha256':hashlib.sha256(service.read_bytes()).hexdigest(),'gate_provenance_sha256':service_payload['gate_provenance_sha256'],
            'runtime':runtime,'runtime_sha256':sha256(runtime),'package_lock_sha256':'d'*64,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
            'manifest':manifest,'manifest_sha256':sha256(manifest),'release_prefix':'releases/'+c['releaseId'],'inference_available':False}
        record=root/'web-release.json';platform.sign_release(body,record,private)
        out={'ApiOrigin':runtime['api_url'],'Issuer':runtime['issuer'],'ClientId':runtime['client_id'],'WebOrigin':runtime['web_origin'],'WebCallbackUri':runtime['callback_uri'],
             'WebReleasePrefix':body['release_prefix'],'ReleaseId':c['releaseId'],'ImageDigest':c['imageDigest'],'WebBucket':'private-assets','WebDistributionId':'D123','WebDistributionDomain':'d123.cloudfront.net'}
        return directory,archive,manifest,c,service,service_payload,public,record,body,out

    def test_signature_source_environment_runtime_and_archive_bytes_are_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory,archive,manifest,c,service,service_payload,public,record,body,out=self.fixture(Path(tmp))
            payload,files=web.verify(record,archive,public,c,service,service_payload,out)
            self.assertEqual(set(files),{'index.html','app.js'})
            for change in ({'releaseId':'e'*40},{'account':'987654321098'},{'environment':'prod'},{'imageDigest':'sha256:'+'b'*64}):
                with self.subTest(change=change),self.assertRaises(Gate):web.verify(record,archive,public,{**c,**change},service,service_payload,out)
            with self.assertRaises(Gate):web.verify(record,archive,public,c,service,service_payload,{**out,'ClientId':'foreign-client'})
            with zipfile.ZipFile(archive,'a') as output:output.writestr('injected.js','tampered')
            with self.assertRaises(Gate):web.verify(record,archive,public,c,service,service_payload,out)

    def test_public_asset_types_paths_symlinks_and_duplicate_zip_entries_are_rejected(self):
        for name in ('../outside.js','/root.js','foo\\bar.js','secret.env','app.js.map','nested//app.js'):
            with self.subTest(name=name),self.assertRaises(Gate):web.file_record(name,b'fixture')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);directory=root/'dist';directory.mkdir();(directory/'index.html').symlink_to('/etc/hosts')
            with self.assertRaises(Gate):web.package(directory,root/'unsafe.zip')
        with tempfile.TemporaryDirectory() as tmp:
            directory,archive,manifest,*_=self.fixture(Path(tmp))
            with zipfile.ZipFile(archive,'a') as output:output.writestr('index.html','different')
            with self.assertRaises(Gate):web.contents(archive,manifest)

    def test_publish_checks_actual_private_origin_and_commits_entrypoint_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory,archive,manifest,c,service,service_payload,public,record,body,out=self.fixture(Path(tmp))
            files=web.contents(archive,manifest);stored={};order=[]
            s3=Mock();cf=Mock();aws=Mock();aws.client.side_effect=lambda kind:s3 if kind=='s3' else cf
            cf.get_distribution.return_value={'Distribution':{'Status':'Deployed','DomainName':out['WebDistributionDomain'],'DistributionConfig':{'DefaultCacheBehavior':{'TargetOriginId':'web','ViewerProtocolPolicy':'redirect-to-https'},'Origins':{'Items':[{'Id':'web','DomainName':'private-assets.s3.us-east-2.amazonaws.com','OriginAccessControlId':'OAC1','OriginPath':'/'+body['release_prefix']}]}}}}
            cf.create_invalidation.return_value={'Invalidation':{'Id':'I123'}}
            def put(**kwargs):stored[kwargs['Key']]=kwargs['Body'];order.append(kwargs['Key']);self.assertEqual(kwargs['IfNoneMatch'],'*')
            s3.put_object.side_effect=put;s3.get_object.side_effect=lambda **kwargs:{'Body':io.BytesIO(stored[kwargs['Key']])}
            web.publish(aws,out,body,files)
            self.assertTrue(order[-1].endswith('/index.html'));cf.get_waiter.return_value.wait.assert_called_once()
            cf.get_distribution.return_value['Distribution']['DistributionConfig']['Origins']['Items'][0]['OriginAccessControlId']=''
            s3.put_object.reset_mock()
            with self.assertRaises(Gate):web.publish(aws,out,body,files)
            s3.put_object.assert_not_called()

    def test_conflicting_immutable_object_and_asset_upload_failure_block_entrypoint(self):
        s3=Mock();s3.put_object.side_effect=ClientError({'Error':{'Code':'PreconditionFailed'}},'PutObject');s3.get_object.return_value={'Body':io.BytesIO(b'wrong')}
        with self.assertRaises(Gate):web.put_immutable(s3,'private','release/app.js',b'reviewed','application/javascript')
        with tempfile.TemporaryDirectory() as tmp:
            *_,body,out=self.fixture(Path(tmp));s3=Mock();cf=Mock();aws=Mock();aws.client.side_effect=lambda kind:s3 if kind=='s3' else cf
            cf.get_distribution.return_value={'Distribution':{'Status':'Deployed','DomainName':out['WebDistributionDomain'],'DistributionConfig':{'DefaultCacheBehavior':{'TargetOriginId':'web','ViewerProtocolPolicy':'redirect-to-https'},'Origins':{'Items':[{'Id':'web','DomainName':'private-assets.s3.us-east-2.amazonaws.com','OriginAccessControlId':'OAC1','OriginPath':'/'+body['release_prefix']}]}}}}
            s3.put_object.side_effect=RuntimeError('dependency outage')
            with self.assertRaises(RuntimeError):web.publish(aws,out,body,{'index.html':b'index','app.js':b'app'})
            self.assertTrue(s3.put_object.call_args.kwargs['Key'].endswith('/app.js'));cf.create_invalidation.assert_not_called()

    def test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance(self):
        out={'WebOrigin':'https://web.otgd.test','ApiOrigin':'https://api.otgd.test'};files={'index.html':b'entry','app.js':b'javascript'}
        def respond(request):
            path=request.url.path
            if path in ('/','/index.html','/history'):return httpx.Response(200,content=b'entry',headers={'x-content-type-options':'nosniff','x-frame-options':'DENY','strict-transport-security':'max-age=31536000','content-security-policy':"object-src 'none'"})
            if path=='/app.js':return httpx.Response(200,content=b'javascript')
            if path=='/health/ready':return httpx.Response(200,content=b'{}')
            return httpx.Response(404)
        client=httpx.Client(transport=httpx.MockTransport(respond))
        with patch.object(web.httpx,'Client',return_value=client):
            result=web.verify_access(out,{},files)
        self.assertEqual(result['authenticated_customer_acceptance'],'not_executed')


class CnameTest(unittest.TestCase):
    def fixture(self):
        c={'webDomain':'app.qa.otgd.test','hostedZoneName':'otgd.test','webCertificateArn':'arn:aws:acm:us-east-1:123456789012:certificate/fixture'}
        out={'WebDistributionId':'D1','WebDistributionDomain':'d1.cloudfront.net','WebOrigin':'https://'+c['webDomain'],'ReleaseId':'c'*40}
        r53=Mock();r53.get_hosted_zone.return_value={'HostedZone':{'Name':'otgd.test.','Config':{'PrivateZone':False}}};r53.list_resource_record_sets.return_value={'ResourceRecordSets':[]};r53.change_resource_record_sets.return_value={'ChangeInfo':{'Id':'C1'}}
        cf=Mock();cf.get_distribution.return_value={'Distribution':{'Status':'Deployed','DomainName':'d1.cloudfront.net','DistributionConfig':{'Aliases':{'Items':[c['webDomain']]},'ViewerCertificate':{'ACMCertificateArn':c['webCertificateArn']}}}}
        acm=Mock();acm.describe_certificate.return_value={'Certificate':{'Status':'ISSUED','SubjectAlternativeNames':[c['webDomain']]}}
        aws=Mock();aws.client.side_effect=lambda service,**kwargs:{'route53':r53,'cloudfront':cf,'acm':acm}[service]
        return c,out,r53,cf,acm,aws

    def test_plan_has_no_dns_mutation_and_apply_waits_for_actual_change(self):
        c,out,r53,cf,acm,aws=self.fixture();result=register_cname.change(aws,c,out,'Z1')
        self.assertFalse(result['applied']);r53.change_resource_record_sets.assert_not_called()
        result=register_cname.change(aws,c,out,'Z1',apply=True)
        self.assertTrue(result['applied']);self.assertEqual(result['record']['ResourceRecords'],[{'Value':'d1.cloudfront.net'}]);r53.get_waiter.return_value.wait.assert_called_once()

    def test_equivalent_existing_dns_case_and_trailing_dot_are_idempotent(self):
        c,out,r53,cf,acm,aws=self.fixture()
        r53.list_resource_record_sets.return_value={'ResourceRecordSets':[{'Name':'APP.QA.OTGD.TEST.','Type':'CNAME','ResourceRecords':[{'Value':'D1.CLOUDFRONT.NET.'}]}]}
        self.assertFalse(register_cname.change(aws,c,out,'Z1')['applied'])

    def test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed(self):
        for mutate in ('apex','foreign','private','tls','alias','distribution','existing'):
            c,out,r53,cf,acm,aws=self.fixture()
            if mutate=='apex':c['webDomain']='otgd.test'
            elif mutate=='foreign':r53.get_hosted_zone.return_value['HostedZone']['Name']='foreign.test.'
            elif mutate=='private':r53.get_hosted_zone.return_value['HostedZone']['Config']['PrivateZone']=True
            elif mutate=='tls':acm.describe_certificate.return_value['Certificate']['Status']='PENDING_VALIDATION'
            elif mutate=='alias':cf.get_distribution.return_value['Distribution']['DistributionConfig']['Aliases']['Items']=[]
            elif mutate=='distribution':cf.get_distribution.return_value['Distribution']['DomainName']='attacker.cloudfront.net'
            else:r53.list_resource_record_sets.return_value={'ResourceRecordSets':[{'Name':c['webDomain']+'.','Type':'CNAME','ResourceRecords':[{'Value':'foreign.cloudfront.net'}]}]}
            with self.subTest(mutate=mutate),self.assertRaises(Gate):register_cname.change(aws,c,out,'Z1',apply=True)
            r53.change_resource_record_sets.assert_not_called()


class OrchestrationTest(unittest.TestCase):
    def config(self):return {'environment':'qa','account':'123456789012','region':'us-east-2','releaseId':'c'*40,'imageDigest':'sha256:'+'a'*64,'recoveryRequired':False,'activateServices':False}

    def test_offline_plan_never_calls_aws_docker_build_or_release_signing(self):
        args=orchestrate.parser('qa').parse_args(['--config','fixture.json','--plan'])
        with patch.object(platform,'read_config',return_value=self.config()),patch.object(platform,'preflight') as aws,patch.object(platform,'run') as run,patch.object(web,'build') as build:
            result=orchestrate.deployment(args,'qa')
        self.assertFalse(result['deployment_executed']);self.assertLess(result['stages'].index('migrate'),result['stages'].index('activate'));aws.assert_not_called();run.assert_not_called();build.assert_not_called()

    def test_wrong_environment_and_unapproved_production_fail_before_aws(self):
        args=orchestrate.parser('prod').parse_args(['--config','fixture.json'])
        with patch.object(platform,'read_config',return_value=self.config()),patch.object(platform,'preflight') as aws:
            with self.assertRaises(Gate):orchestrate.deployment(args,'prod')
        aws.assert_not_called()
        with patch.object(platform,'read_config',return_value={**self.config(),'environment':'prod'}),patch.object(platform,'preflight') as aws:
            with self.assertRaises(Gate):orchestrate.admit_source_web(args,{**self.config(),'environment':'prod'})
        aws.assert_not_called()

    def test_failed_migration_never_activates_or_uploads_web(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);release=root/'release.json';release.write_text(json.dumps({'payload':{'image_digest':self.config()['imageDigest']}}))
            args=orchestrate.parser('qa').parse_args(['--config','fixture.json','--release',str(release),'--work-dir',str(root/'attempts'),'--gate-evidence','gates.json','--trusted-public-key','public.pem','--signing-key','private.pem'])
            calls=[]
            def stage(operation,*a,**kw):
                calls.append(operation)
                if operation=='migrate':raise RuntimeError('actual migration failed')
            absent=ClientError({'Error':{'Code':'ValidationError','Message':'Stack does not exist'}},'DescribeStacks')
            with patch.object(platform,'read_config',return_value=self.config()),patch.object(platform,'require_clean_source'),patch.object(platform,'require_trusted_signer'),patch.object(platform,'verify_gate_file'),patch.object(platform,'preflight'),patch.object(platform,'run'),patch.object(platform,'require_release',return_value={}),patch.object(platform,'stack_outputs',side_effect=absent),patch.object(orchestrate,'invoke',side_effect=stage),patch.object(web,'publish') as publish,patch.object(web,'build') as build:
                with self.assertRaises(RuntimeError):orchestrate.deployment(args,'qa')
            self.assertEqual(calls,['registry','deploy-stopped','bootstrap','migrate']);publish.assert_not_called();build.assert_not_called()

    def test_running_process_without_worker_progress_never_qualifies(self):
        ecs=Mock();ecs.list_tasks.return_value={'taskArns':['task1']};ecs.describe_tasks.return_value={'tasks':[{'lastStatus':'RUNNING','containers':[{'name':'worker','healthStatus':'UNKNOWN'}]}]};aws=Mock();aws.client.return_value=ecs
        with patch.object(orchestrate.time,'monotonic',side_effect=[0,0,601]),patch.object(orchestrate.time,'sleep'):
            with self.assertRaises(Gate):orchestrate.worker_health(aws,{'Cluster':'cluster','WorkerService':'worker'})

    def test_partial_failures_journal_completed_stages_without_inferred_rollback(self):
        for failed_stage in ('quiesce-existing','build-signed-web','verify-admission','activate','publish-web'):
            with self.subTest(stage=failed_stage),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);release=root/'release.json';release.write_text(json.dumps({'payload':{'image_digest':self.config()['imageDigest']}}))
                args=orchestrate.parser('qa').parse_args(['--config','fixture.json','--release',str(release),'--work-dir',str(root/'attempts'),'--gate-evidence','gates.json','--trusted-public-key','public.pem','--signing-key','private.pem'])
                out={'WebOrigin':'https://web.otgd.test'}
                def stage(operation,*a,**kw):
                    if operation==failed_stage:raise RuntimeError('fixture stage failure')
                    if operation in ('bootstrap','migrate','verify-admission'):kw['output'].write_text(json.dumps({'operation':operation,'status':'fixture_success'}))
                def fail_quiesce(*a):
                    if failed_stage=='quiesce-existing':raise RuntimeError('fixture quiesce failure')
                with patch.object(platform,'read_config',return_value=self.config()),patch.object(platform,'require_clean_source'),patch.object(platform,'require_trusted_signer'),patch.object(platform,'verify_gate_file'),patch.object(platform,'preflight'),patch.object(platform,'run'),patch.object(platform,'require_release',return_value={}),patch.object(platform,'stack_outputs',return_value=out),patch.object(platform,'quiesce',side_effect=fail_quiesce),patch.object(orchestrate,'invoke',side_effect=stage),patch.object(orchestrate,'worker_health'),patch.object(web,'build',side_effect=RuntimeError('fixture build failure') if failed_stage=='build-signed-web' else None,return_value={}),patch.object(web,'verify',return_value=({},{})),patch.object(web,'publish',side_effect=RuntimeError('fixture upload failure') if failed_stage=='publish-web' else None,return_value={}),patch.object(web,'verify_access',return_value={}):
                    with self.assertRaises(RuntimeError):orchestrate.deployment(args,'qa')
                journal_path=next((root/'attempts').rglob('deployment-state.json'));journal=json.loads(journal_path.read_text())
                self.assertEqual(journal['failed_stage'],failed_stage);self.assertEqual(journal['failure_type'],'RuntimeError');self.assertFalse(journal['rollback_executed'])
                self.assertNotIn(failed_stage,journal['completed_stages']);self.assertEqual(journal_path.stat().st_mode&0o777,0o600)
                if failed_stage!='quiesce-existing':self.assertIn('migration.json',journal['completed_receipts']);self.assertIn('migrate',journal['completed_stages'])
                if failed_stage in ('activate','publish-web'):
                    self.assertIn('admission.json',journal['completed_receipts']);self.assertIn('verify-admission',journal['completed_stages'])
                    admission=journal_path.parent/'admission.json'
                    self.assertEqual(journal['completed_receipts']['admission.json']['sha256'],hashlib.sha256(admission.read_bytes()).hexdigest())
                self.assertFalse((journal_path.parent/'deployment.json').exists())

    def test_production_requires_results_reference_separate_from_artifact_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);service=root/'service.json';service.write_text('signed service fixture');web_record=root/'web.json';web_record.write_text('signed web fixture')
            args=orchestrate.parser('prod').parse_args(['--config','prod.json','--source-config','qa.json','--source-release',str(service),'--source-web-release',str(web_record),'--source-web-artifact','web.zip','--qa-evidence','qa-approved.json','--trusted-public-key','public.pem'])
            source_c=self.config();target={**self.config(),'environment':'prod','account':'987654321098'}
            source={'image_digest':source_c['imageDigest'],'release_id':source_c['releaseId'],'gate_provenance_sha256':'d'*64}
            approval={'passed_gates':['web_customer_access'],'evidence_refs':{'web_customer_access':'sha256:'+hashlib.sha256(web_record.read_bytes()).hexdigest()}}
            with patch.object(platform,'read_config',return_value=source_c),patch.object(platform,'verify_release',return_value=source),patch.object(orchestrate,'verify_qa_approval',return_value=approval),patch.object(web,'verify',return_value=({},{})):
                with self.assertRaises(Gate):orchestrate.admit_source_web(args,target)
                approval['evidence_refs']['web_customer_access_results']='https://protected.otgd.test/qa/browser-results'
                self.assertEqual(orchestrate.admit_source_web(args,target)[1],source)


class ScratchSourceTest(unittest.TestCase):
    def test_fargate_copied_volume_has_initialized_nonroot_writable_permissions(self):
        root=Path(__file__).resolve().parents[2]
        dockerfile=(root/'infra/local/service.Dockerfile').read_text()
        initialization='install -d -m 1777 -o 10001 -g 10001 /tmp'
        self.assertIn(initialization,dockerfile)
        self.assertLess(dockerfile.index(initialization),dockerfile.index('VOLUME ["/tmp"]'))
        self.assertLess(dockerfile.index('VOLUME ["/tmp"]'),dockerfile.index('USER 10001'))
        stack=(root/'infra/lib/platform-stack.ts').read_text()
        self.assertIn("containerPath:'/tmp',sourceVolume:'scratch',readOnly:false",stack)
        self.assertIn("user:'10001',readonlyRootFilesystem:true",stack)
        compose=(root/'infra/local/compose.yml').read_text()
        self.assertIn('/tmp:size=134217728,mode=1777',compose)


if __name__=='__main__':unittest.main()
