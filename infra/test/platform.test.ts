import test from 'node:test';
import assert from 'node:assert/strict';
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
    t.resourceCountIs('AWS::S3::Bucket',3);
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
    const body=JSON.stringify(t.toJSON());
    assert.ok(body.includes('s3:if-none-match'));
    assert.ok(body.includes('s3:DeleteObjectVersion'));
    assert.ok(body.includes('OTGD_JOURNAL_KMS_KEY_ID'));
    assert.ok(body.includes('OTGD_APP_DATABASE_PASSWORD'));
    assert.ok(!body.includes('OTGD_AWS_ENDPOINT_URL'));
    assert.ok(!body.includes('LOCALSTACK_AUTH_TOKEN'));
    assert.ok(!body.includes('"Action":"*"'));
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
  ]) assert.throws(()=>validateConfig(invalid));
});
