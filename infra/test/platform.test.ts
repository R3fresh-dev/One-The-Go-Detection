import test from 'node:test';
import assert from 'node:assert/strict';
import { runInNewContext } from 'node:vm';
import { App } from 'aws-cdk-lib';
import { Match, Template } from 'aws-cdk-lib/assertions';
import { PlatformConfig, validateConfig } from '../lib/config';
import { PlatformStack, RegistryStack } from '../lib/platform-stack';

const fixture=(environment:'qa'|'prod'):PlatformConfig=>({
  environment,account:'123456789012',region:'us-east-2',vpcCidr:'10.72.0.0/16',
  domain:`api.${environment}.otgd.test`,certificateArn:'arn:aws:acm:us-east-2:123456789012:certificate/11111111-2222-3333-4444-555555555555',
  cognitoDomainPrefix:`otgd-${environment}-fixture`,oauthRedirectUris:[`otgd-${environment}://oauth/callback`],oauthLogoutUris:[`otgd-${environment}://oauth/callback`],
  imageDigest:'sha256:'+'a'.repeat(64),releaseId:'fixture-commit',monthlyBudgetUsd:500,alarmEmail:'operator@otgd.test',ownerRole:'platform-operator',costCenter:'fixture-only',costEstimatePath:'fixture.json',databaseEngineVersion:'16.14',activateServices:true,recoveryRequired:false,
});

for (const env of ['qa','prod'] as const) {
  test(`${env}: synthesized network, identity, storage and queue boundaries`,()=>{
    const app=new App();const c=fixture(env);
    const registry=new RegistryStack(app,`${env}-registry`,{config:c,env:{account:c.account,region:c.region}});
    const stack=new PlatformStack(app,`${env}-platform`,{config:c,repository:registry.repository,env:{account:c.account,region:c.region}});
    const t=Template.fromStack(stack);
    t.resourceCountIs('AWS::EC2::NatGateway',env==='prod'?2:1);
    t.resourceCountIs('AWS::S3::Bucket',4);
    for(const bucket of Object.values(t.findResources('AWS::S3::Bucket')) as any[]) {
      assert.equal(bucket.Properties.VersioningConfiguration.Status,'Enabled');
      assert.equal(bucket.Properties.PublicAccessBlockConfiguration.BlockPublicPolicy,true);
      assert.ok(bucket.Properties.BucketEncryption);
      assert.equal(bucket.DeletionPolicy,'Retain');
    }
    t.hasResourceProperties('AWS::RDS::DBInstance',{PubliclyAccessible:false,StorageEncrypted:true,MultiAZ:env==='prod',BackupRetentionPeriod:env==='prod'?35:7,AutoMinorVersionUpgrade:false,MasterUsername:'otgd_migrator'});
    t.hasResourceProperties('AWS::SQS::Queue',{VisibilityTimeout:120,MessageRetentionPeriod:345600,ReceiveMessageWaitTimeSeconds:20,RedrivePolicy:Match.objectLike({maxReceiveCount:5})});
    t.hasResourceProperties('AWS::SQS::Queue',{VisibilityTimeout:120,MessageRetentionPeriod:1209600});
    t.hasResourceProperties('AWS::Cognito::UserPoolClient',{GenerateSecret:false,EnableTokenRevocation:true,AllowedOAuthFlows:['code'],PreventUserExistenceErrors:'ENABLED'});
    for(const service of Object.values(t.findResources('AWS::ECS::Service')) as any[]) {
      assert.equal(service.Properties.NetworkConfiguration.AwsvpcConfiguration.AssignPublicIp,'DISABLED');
      assert.equal(service.Properties.DeploymentConfiguration.MaximumPercent,200);
    }
    // Inspect the real worker definition and its service, rather than accepting
    // a health command on an unrelated task or the metrics sidecar.
    const tasks=t.findResources('AWS::ECS::TaskDefinition') as Record<string,any>;
    const workerTasks=Object.entries(tasks).filter(([,task])=>task.Properties.ContainerDefinitions.some((container:any)=>container.Name==='worker'));
    assert.equal(workerTasks.length,1);
    const [workerTaskId,workerTask]=workerTasks[0];
    const worker=workerTask.Properties.ContainerDefinitions.find((container:any)=>container.Name==='worker');
    assert.deepEqual(worker.HealthCheck,{
      Command:['CMD','uv','run','--no-sync','python','-m','otgd.worker_health'],
      Interval:10,Timeout:5,Retries:3,StartPeriod:35,
    });
    assert.equal(worker.User,'10001');
    assert.equal(worker.Essential,true);
    assert.equal(worker.ReadonlyRootFilesystem,true);
    assert.ok(worker.MountPoints.some((mount:any)=>mount.ContainerPath==='/tmp' && mount.SourceVolume==='scratch' && mount.ReadOnly===false));
    assert.ok(workerTask.Properties.Volumes.some((volume:any)=>volume.Name==='scratch'));
    const signingKeys=Object.entries(t.findResources('AWS::KMS::Key')).filter(([,key]:any)=>key.Properties.KeyUsage==='SIGN_VERIFY') as [string,any][];
    assert.equal(signingKeys.length,1);
    const [signingKeyId,signingKey]=signingKeys[0];
    assert.equal(signingKey.Properties.KeySpec,'ECC_NIST_P256');
    assert.equal(signingKey.Properties.EnableKeyRotation,false);assert.equal(signingKey.DeletionPolicy,'Retain');
    t.hasResourceProperties('AWS::KMS::Alias',{AliasName:`alias/otgd-${env}-capture-grant`,TargetKeyId:{'Fn::GetAtt':[signingKeyId,'Arn']}});
    const apiTask=Object.values(tasks).find((task:any)=>task.Properties.ContainerDefinitions.some((container:any)=>container.Name==='api')) as any;
    const apiContainer=apiTask.Properties.ContainerDefinitions.find((container:any)=>container.Name==='api');
    assert.deepEqual(apiContainer.Environment.find((entry:any)=>entry.Name==='OTGD_CAPTURE_SIGNING_KEY_ID').Value,{'Fn::GetAtt':[signingKeyId,'Arn']});
    assert.equal(worker.Environment.find((entry:any)=>entry.Name==='OTGD_CAPTURE_SIGNING_KEY_ID'),undefined);
    const apiRoleId=apiTask.Properties.TaskRoleArn['Fn::GetAtt'][0];
    const workerRoleId=workerTask.Properties.TaskRoleArn['Fn::GetAtt'][0];
    const roleStatements=(roleId:string)=>(Object.values(t.findResources('AWS::IAM::Policy')) as any[]).filter(policy=>policy.Properties.Roles.some((ref:any)=>ref.Ref===roleId)).flatMap(policy=>policy.Properties.PolicyDocument.Statement);
    const signingGrants=roleStatements(apiRoleId).filter(statement=>(Array.isArray(statement.Action)?statement.Action:[statement.Action]).includes('kms:Sign'));
    assert.equal(signingGrants.length,1);
    assert.deepEqual(signingGrants[0].Action,['kms:Sign','kms:GetPublicKey']);
    assert.deepEqual(signingGrants[0].Resource,{'Fn::GetAtt':[signingKeyId,'Arn']});
    assert.ok(roleStatements(workerRoleId).every(statement=>!(Array.isArray(statement.Action)?statement.Action:[statement.Action]).some((action:string)=>['kms:Sign','kms:*'].includes(action))));
    const maintenanceTask=Object.values(tasks).find((task:any)=>task.Properties.ContainerDefinitions.some((container:any)=>container.Name==='migration')) as any;
    const maintenanceContainer=maintenanceTask.Properties.ContainerDefinitions.find((container:any)=>container.Name==='migration');
    assert.deepEqual(maintenanceContainer.Environment.find((entry:any)=>entry.Name==='OTGD_CAPTURE_SIGNING_KEY_ID').Value,{'Fn::GetAtt':[signingKeyId,'Arn']});
    const maintenanceStatements=roleStatements(maintenanceTask.Properties.TaskRoleArn['Fn::GetAtt'][0]);
    assert.ok(maintenanceStatements.some(statement=>statement.Action==='kms:GetPublicKey' && JSON.stringify(statement.Resource).includes(signingKeyId)));
    assert.ok(maintenanceStatements.every(statement=>!(Array.isArray(statement.Action)?statement.Action:[statement.Action]).some((action:string)=>['kms:Sign','kms:*'].includes(action))));
    assert.deepEqual(t.toJSON().Outputs.CaptureSigningKeyArn.Value,{'Fn::GetAtt':[signingKeyId,'Arn']});
    const workerServices=Object.values(t.findResources('AWS::ECS::Service')).filter((service:any)=>service.Properties.TaskDefinition.Ref===workerTaskId) as any[];
    assert.equal(workerServices.length,1);
    assert.deepEqual(workerServices[0].Properties.DeploymentConfiguration.DeploymentCircuitBreaker,{Enable:true,Rollback:true});
    t.hasResourceProperties('AWS::CloudFront::OriginAccessControl',{OriginAccessControlConfig:Match.objectLike({OriginAccessControlOriginType:'s3',SigningBehavior:'always',SigningProtocol:'sigv4'})});
    t.hasResourceProperties('AWS::CloudFront::Distribution',{DistributionConfig:Match.objectLike({DefaultRootObject:'index.html',DefaultCacheBehavior:Match.objectLike({ViewerProtocolPolicy:'redirect-to-https',AllowedMethods:['GET','HEAD','OPTIONS'],FunctionAssociations:Match.arrayWith([Match.objectLike({EventType:'viewer-request'})])}),Origins:Match.arrayWith([Match.objectLike({OriginPath:`/releases/${c.releaseId}`,OriginAccessControlId:Match.anyValue()})])})});
    const webBucket=Object.entries(t.findResources('AWS::S3::Bucket')).find(([id])=>id.startsWith('WebAssets'))![1] as any;
    assert.equal(webBucket.Properties.WebsiteConfiguration,undefined);
    const webPolicy=Object.entries(t.findResources('AWS::S3::BucketPolicy')).find(([id])=>id.startsWith('WebAssets'))![1] as any;
    assert.ok(webPolicy.Properties.PolicyDocument.Statement.some((statement:any)=>statement.Effect==='Allow' && statement.Principal?.Service==='cloudfront.amazonaws.com' && statement.Condition?.StringEquals?.['AWS:SourceArn']));
    const webFunction=Object.values(t.findResources('AWS::CloudFront::Function'))[0] as any;
    const handler=runInNewContext(webFunction.Properties.FunctionCode+'; handler');
    for(const path of ['/','/history','/checks/one']) assert.equal(handler({request:{method:'GET',uri:path}}).uri,'/index.html');
    for(const path of ['/missing.js','/_expo/static/js/web/missing.js','/image.png']) assert.equal(handler({request:{method:'GET',uri:path}}).uri,path);
    assert.equal(handler({request:{method:'POST',uri:'/history'}}).uri,'/history');
    const body=JSON.stringify(t.toJSON());
    assert.ok(body.includes('s3:if-none-match'));
    assert.ok(body.includes('s3:DeleteObjectVersion'));
    assert.ok(body.includes('OTGD_JOURNAL_KMS_KEY_ID'));
    assert.ok(body.includes('OTGD_APP_DATABASE_PASSWORD'));
    assert.ok(!body.includes('OTGD_AWS_ENDPOINT_URL'));
    assert.ok(!body.includes('LOCALSTACK_AUTH_TOKEN'));
    assert.ok(!body.includes('"Action":"*"'));
    assert.ok(body.includes('OTGD_DEPLOYMENT_ACCOUNT') && body.includes('OTGD_SOURCE_REVISION'));
    assert.ok(body.includes("object-src 'none'") && body.includes("script-src 'self'"));
    const roles=t.findResources('AWS::IAM::Role') as Record<string,any>;
    const registryRoles=Object.entries(roles).filter(([,role])=>role.Properties.RoleName?.startsWith(`otgd-${env}-registry-`));
    assert.equal(registryRoles.length,3);
    assert.deepEqual(registryRoles.map(([,role])=>role.Properties.RoleName).sort(),['releaser','reviewer','submitter'].map(name=>`otgd-${env}-registry-${name}`));
    for(const [roleId,role] of registryRoles) {
      assert.equal(role.Properties.MaxSessionDuration,3600);
      const trust=role.Properties.AssumeRolePolicyDocument.Statement;
      assert.equal(trust.length,1);assert.equal(trust[0].Condition.Bool['aws:MultiFactorAuthPresent'],'true');
      assert.equal(trust[0].Principal.Service,undefined);
      assert.ok(JSON.stringify(trust[0].Principal.AWS).includes(c.account));
      const policies=Object.values(t.findResources('AWS::IAM::Policy')).filter((policy:any)=>policy.Properties.Roles.some((ref:any)=>ref.Ref===roleId)) as any[];
      const statements=policies.flatMap(policy=>policy.Properties.PolicyDocument.Statement);
      assert.ok(statements.some(statement=>(Array.isArray(statement.Action)?statement.Action:[statement.Action]).includes('iam:GetRole')));
      assert.ok(statements.every(statement=>!(Array.isArray(statement.Action)?statement.Action:[statement.Action]).some((action:string)=>['ecs:RunTask','iam:PassRole','sts:AssumeRole'].includes(action))));
      const writes=statements.filter(statement=>(Array.isArray(statement.Action)?statement.Action:[statement.Action]).includes('s3:PutObject'));
      assert.equal(writes.length,role.Properties.RoleName.endsWith('-releaser')?1:0);
      if(writes.length) {
        assert.ok(JSON.stringify(writes[0].Resource).includes('scope-resumptions/*'));
        const encryption=statements.find(statement=>JSON.stringify(statement.Action)===JSON.stringify(['kms:GenerateDataKey','kms:Encrypt','kms:Decrypt']));
        assert.ok(encryption && JSON.stringify(encryption.Resource).includes('JournalKey'));
        assert.ok(statements.some(statement=>(Array.isArray(statement.Action)?statement.Action:[statement.Action]).includes('s3:GetObjectRetention') && JSON.stringify(statement.Resource).includes('DeletionJournal')));
      }
    }
    t.hasResourceProperties('AWS::ElasticLoadBalancingV2::Listener',{Port:443,Protocol:'HTTPS'});
    t.hasResourceProperties('AWS::Logs::LogGroup',{RetentionInDays:env==='prod'?30:7,KmsKeyId:Match.anyValue()});
    t.resourceCountIs('AWS::Budgets::Budget',1);
    // Two additional production alarms drive queue step scaling.
    t.resourceCountIs('AWS::CloudWatch::Alarm',env==='prod'?10:7);
    t.hasResourceProperties('AWS::Budgets::Budget',{Budget:Match.objectLike({CostFilters:{TagKeyValue:[`user:deployment$otgd-${env}`]}})});
    t.hasResourceProperties('AWS::Cognito::UserPool',{UserPoolTier:'LITE'});
    for(const rule of Object.values(t.findResources('AWS::EC2::SecurityGroupIngress')) as any[]) {
      if(rule.Properties.ToPort===5432) assert.ok(!rule.Properties.CidrIp && rule.Properties.SourceSecurityGroupId);
    }
    // The journal's KMS key must differ from the artifact/export key.
    const buckets=t.findResources('AWS::S3::Bucket') as Record<string,any>;
    const journal=Object.entries(buckets).find(([id])=>id.startsWith('DeletionJournal'))![1];
    const artifact=Object.entries(buckets).find(([id])=>id.startsWith('Artifacts'))![1];
    assert.notDeepEqual(journal.Properties.BucketEncryption,artifact.Properties.BucketEncryption);
    const policy=Object.entries(t.findResources('AWS::S3::BucketPolicy')).find(([id])=>id.startsWith('DeletionJournal'))![1] as any;
    assert.ok(policy.Properties.PolicyDocument.Statement.some((s:any)=>s.Effect==='Deny' && (Array.isArray(s.Action)?s.Action:[s.Action]).includes('s3:DeleteObjectVersion')));
    const resumptionDeny=policy.Properties.PolicyDocument.Statement.find((s:any)=>s.Effect==='Deny' && (Array.isArray(s.Action)?s.Action:[s.Action]).includes('s3:PutObject') && JSON.stringify(s.Resource).includes('scope-resumptions/*'));
    assert.ok(resumptionDeny);
    assert.ok(JSON.stringify(resumptionDeny.Principal.AWS).includes(apiRoleId) && JSON.stringify(resumptionDeny.Principal.AWS).includes(workerRoleId) && JSON.stringify(resumptionDeny.Principal.AWS).includes('migrationTaskTaskRole'));
  });
}

test('first deployment keeps API and worker stopped until bootstrap/migration',()=>{
  const app=new App(),c={...fixture('qa'),activateServices:false};
  const registry=new RegistryStack(app,'boot-registry',{config:c});
  const t=Template.fromStack(new PlatformStack(app,'boot-platform',{config:c,repository:registry.repository,env:{account:c.account,region:c.region}}));
  for(const service of Object.values(t.findResources('AWS::ECS::Service')) as any[]) assert.equal(service.Properties.DesiredCount,0);
});

test('snapshot restore preserves storage size and retained dependencies with recovery denied until verified',()=>{
  const app=new App(),c={...fixture('prod'),activateServices:false,recoveryRequired:true,databaseSnapshotIdentifier:'arn:aws:rds:us-east-2:123456789012:snapshot:otgd-verified-recovery'};
  const registry=new RegistryStack(app,'restore-registry',{config:c});
  const t=Template.fromStack(new PlatformStack(app,'restore-platform',{config:c,repository:registry.repository,env:{account:c.account,region:c.region}}));
  t.hasResourceProperties('AWS::RDS::DBInstance',{DBSnapshotIdentifier:c.databaseSnapshotIdentifier,PubliclyAccessible:false});
  const db=Object.values(t.findResources('AWS::RDS::DBInstance'))[0] as any;
  assert.equal(db.Properties.AllocatedStorage,undefined);
  assert.equal(db.UpdateReplacePolicy,'Retain');
  for(const service of Object.values(t.findResources('AWS::ECS::Service')) as any[]) assert.equal(service.Properties.DesiredCount,0);
  assert.ok(JSON.stringify(t.toJSON()).includes('OTGD_DATABASE_SSLMODE'));
});

test('deployment input validation rejects placeholders, tags, unsafe callbacks and missing budgets',()=>{
  assert.equal(validateConfig(fixture('qa')).region,'us-east-2');
  for(const invalid of [
    {...fixture('qa'),environment:'local'}, {...fixture('qa'),monthlyBudgetUsd:0},
    {...fixture('qa'),imageDigest:'latest'}, {...fixture('qa'),account:'YOUR_ACCOUNT'},
    {...fixture('qa'),oauthRedirectUris:['http://localhost/callback']},
    {...fixture('qa'),oauthRedirectUris:['otgd-local://oauth/callback']},
    {...fixture('qa'),recoveryRequired:'true'}, {...fixture('qa'),databaseEngineVersion:'latest'},
    {...fixture('qa'),unexpected:'ignored'},
    {...fixture('qa'),hostedZoneId:'Z1234'},
    {...fixture('qa'),webDomain:'app.otgd.test'},
    {...fixture('qa'),webDomain:'app.otgd.test',webCertificateArn:'arn:aws:acm:us-east-2:123456789012:certificate/wrong-region'},
    {...fixture('qa'),webDomain:fixture('qa').domain,webCertificateArn:'arn:aws:acm:us-east-1:123456789012:certificate/fixture'},
  ]) assert.throws(()=>validateConfig(invalid));
});

test('optional web custom domain uses us-east-1 TLS and a subdomain CNAME to this distribution',()=>{
  const c={...fixture('qa'),hostedZoneId:'Z123456',hostedZoneName:'otgd.test',webDomain:'app.qa.otgd.test',webCertificateArn:'arn:aws:acm:us-east-1:123456789012:certificate/11111111-2222-3333-4444-555555555555'};
  validateConfig(c);
  const app=new App(),registry=new RegistryStack(app,'web-registry',{config:c});
  const t=Template.fromStack(new PlatformStack(app,'web-platform',{config:c,repository:registry.repository,env:{account:c.account,region:c.region}}));
  t.hasResourceProperties('AWS::CloudFront::Distribution',{DistributionConfig:Match.objectLike({Aliases:[c.webDomain],ViewerCertificate:Match.objectLike({AcmCertificateArn:c.webCertificateArn,MinimumProtocolVersion:'TLSv1.2_2021',SslSupportMethod:'sni-only'})})});
  const distributionId=Object.keys(t.findResources('AWS::CloudFront::Distribution'))[0];
  t.hasResourceProperties('AWS::Route53::RecordSet',{Type:'CNAME',Name:c.webDomain+'.',TTL:'300',ResourceRecords:[{'Fn::GetAtt':[distributionId,'DomainName']}]});
  t.hasResourceProperties('AWS::Cognito::UserPoolClient',{CallbackURLs:Match.arrayWith(['https://'+c.webDomain+'/']),LogoutURLs:Match.arrayWith(['https://'+c.webDomain+'/'])});
  for(const bad of [{...c,webDomain:'otgd.test'},{...c,webDomain:'foreign.test'},{...c,webCertificateArn:'arn:aws:acm:us-east-1:987654321098:certificate/foreign'}]) assert.throws(()=>validateConfig(bad));
});
