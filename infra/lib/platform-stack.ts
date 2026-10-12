import {
  Stack, StackProps, Duration, RemovalPolicy, CfnOutput, Tags,
  aws_ec2 as ec2, aws_ecs as ecs, aws_ecr as ecr, aws_rds as rds,
  aws_s3 as s3, aws_sqs as sqs, aws_kms as kms, aws_iam as iam,
  aws_secretsmanager as secrets, aws_cognito as cognito,
  aws_elasticloadbalancingv2 as elb, aws_certificatemanager as acm,
  aws_logs as logs, aws_cloudwatch as cw, aws_cloudwatch_actions as actions,
  aws_sns as sns, aws_sns_subscriptions as subscriptions, aws_budgets as budgets,
  aws_route53 as route53, aws_route53_targets as targets,
  aws_cloudfront as cloudfront, aws_cloudfront_origins as origins,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { PlatformConfig } from './config';

interface ConfigProps extends StackProps { config: PlatformConfig }
function tag(scope: Construct, c: PlatformConfig) {
  for (const [key,value] of Object.entries({project:'one-the-go-detection',environment:c.environment,deployment:`otgd-${c.environment}`,owner_role:c.ownerRole,cost_center:c.costCenter})) Tags.of(scope).add(key,value);
}

export class RegistryStack extends Stack {
  readonly repository: ecr.Repository;
  constructor(scope: Construct,id: string,props: ConfigProps) {
    super(scope,id,props); tag(this,props.config);
    this.repository = new ecr.Repository(this,'Images',{
      repositoryName:`otgd-${props.config.environment}`,
      imageTagMutability:ecr.TagMutability.IMMUTABLE,
      imageScanOnPush:true,
      encryption:ecr.RepositoryEncryption.AES_256,
      removalPolicy:RemovalPolicy.RETAIN,
    });
    // No lifecycle expiration: an old referenced digest may be the rollback target.
    new CfnOutput(this,'RepositoryUri',{value:this.repository.repositoryUri});
  }
}

export class PlatformStack extends Stack {
  constructor(scope: Construct,id: string,props: ConfigProps & {repository:ecr.IRepository}) {
    super(scope,id,props);
    const c=props.config, prod=c.environment==='prod', prefix=`otgd-${c.environment}`;
    tag(this,c);
    const dataKey=new kms.Key(this,'DataKey',{enableKeyRotation:true,removalPolicy:RemovalPolicy.RETAIN,description:`${prefix} encrypted data and transport`});
    const journalKey=new kms.Key(this,'JournalKey',{enableKeyRotation:true,removalPolicy:RemovalPolicy.RETAIN,description:`${prefix} independent recovery journal; never erase with account data`});
    const captureSigningKey=new kms.Key(this,'CaptureSigningKey',{
      keySpec:kms.KeySpec.ECC_NIST_P256,keyUsage:kms.KeyUsage.SIGN_VERIFY,
      enableKeyRotation:false,removalPolicy:RemovalPolicy.RETAIN,
      alias:`alias/${prefix}-capture-grant`,description:`${prefix} server-signed physical capture grants; private key remains in KMS`,
    });
    const vpc=new ec2.Vpc(this,'Network',{
      ipAddresses:ec2.IpAddresses.cidr(c.vpcCidr),maxAzs:2,natGateways:prod?2:1,
      subnetConfiguration:[
        {name:'public',subnetType:ec2.SubnetType.PUBLIC,cidrMask:26},
        {name:'application',subnetType:ec2.SubnetType.PRIVATE_WITH_EGRESS,cidrMask:26},
        {name:'database',subnetType:ec2.SubnetType.PRIVATE_ISOLATED,cidrMask:26},
      ],
      gatewayEndpoints:{S3:{service:ec2.GatewayVpcEndpointAwsService.S3}},
    });
    const apiSg=new ec2.SecurityGroup(this,'ApiSecurityGroup',{vpc,allowAllOutbound:true,description:'Only ALB inbound; explicit NAT routes for managed AWS and issuer dependencies'});
    const workerSg=new ec2.SecurityGroup(this,'WorkerSecurityGroup',{vpc,allowAllOutbound:true,description:'No inbound worker ports'});
    const migrationSg=new ec2.SecurityGroup(this,'MigrationSecurityGroup',{vpc,allowAllOutbound:true,description:'One-off migration/recovery task'});
    const databaseSg=new ec2.SecurityGroup(this,'DatabaseSecurityGroup',{vpc,allowAllOutbound:false});
    for (const source of [apiSg,workerSg,migrationSg]) databaseSg.addIngressRule(source,ec2.Port.tcp(5432),'Only application/migration database clients');

    const databaseProps={
      engine:rds.DatabaseInstanceEngine.postgres({version:rds.PostgresEngineVersion.of(c.databaseEngineVersion,'16')}),
      instanceType:ec2.InstanceType.of(ec2.InstanceClass.T4G,prod?ec2.InstanceSize.MEDIUM:ec2.InstanceSize.SMALL),
      vpc,vpcSubnets:{subnetType:ec2.SubnetType.PRIVATE_ISOLATED},securityGroups:[databaseSg],
      allocatedStorage:20,maxAllocatedStorage:100,storageType:rds.StorageType.GP3,
      storageEncrypted:true,storageEncryptionKey:dataKey,multiAz:prod,publiclyAccessible:false,
      backupRetention:Duration.days(prod?35:7),deletionProtection:prod,
      copyTagsToSnapshot:true,
      removalPolicy:RemovalPolicy.SNAPSHOT,deleteAutomatedBackups:false,
      autoMinorVersionUpgrade:false,allowMajorVersionUpgrade:false,
      cloudwatchLogsExports:['postgresql'],cloudwatchLogsRetention:prod?logs.RetentionDays.ONE_MONTH:logs.RetentionDays.ONE_WEEK,
    };
    const database=c.databaseSnapshotIdentifier
      ?new rds.DatabaseInstanceFromSnapshot(this,'Database',{...databaseProps,allocatedStorage:undefined,snapshotIdentifier:c.databaseSnapshotIdentifier,credentials:rds.SnapshotCredentials.fromGeneratedSecret('otgd_migrator',{encryptionKey:dataKey}),removalPolicy:RemovalPolicy.RETAIN})
      :new rds.DatabaseInstance(this,'Database',{...databaseProps,databaseName:'otgd',credentials:rds.Credentials.fromGeneratedSecret('otgd_migrator',{encryptionKey:dataKey})});
    // The L2 snapshot construct defaults allocatedStorage to 100 GiB. Omit the
    // CloudFormation field so RDS inherits the verified snapshot size unchanged.
    if(c.databaseSnapshotIdentifier) (database.node.defaultChild as rds.CfnDBInstance).allocatedStorage=undefined;
    const appSecret=new secrets.Secret(this,'ApplicationDatabaseCredential',{
      encryptionKey:dataKey,
      generateSecretString:{secretStringTemplate:JSON.stringify({username:'otgd_app'}),generateStringKey:'password',passwordLength:40,excludePunctuation:true},
    });
    appSecret.applyRemovalPolicy(RemovalPolicy.RETAIN);
    const tombstoneSecret=new secrets.Secret(this,'IdentityTombstoneKey',{
      encryptionKey:journalKey,
      generateSecretString:{secretStringTemplate:JSON.stringify({key_id:'v1'}),generateStringKey:'key',passwordLength:64,excludePunctuation:true,excludeUppercase:true,excludeCharacters:'ghijklmnopqrstuvwxyz',requireEachIncludedType:false},
    });
    tombstoneSecret.applyRemovalPolicy(RemovalPolicy.RETAIN);

    const bucket=(name:string,key:kms.IKey)=>new s3.Bucket(this,name,{
      versioned:true,encryption:s3.BucketEncryption.KMS,encryptionKey:key,bucketKeyEnabled:true,
      blockPublicAccess:s3.BlockPublicAccess.BLOCK_ALL,enforceSSL:true,
      objectOwnership:s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      removalPolicy:RemovalPolicy.RETAIN,autoDeleteObjects:false,
    });
    const artifacts=bucket('Artifacts',dataKey), exports=bucket('Exports',dataKey), journal=bucket('DeletionJournal',journalKey);
    // Application assets remain private at their S3 origin; prior release
    // prefixes are retained for reviewed rollback.
    const web=new s3.Bucket(this,'WebAssets',{
      versioned:true,encryption:s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess:s3.BlockPublicAccess.BLOCK_ALL,enforceSSL:true,
      objectOwnership:s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
      removalPolicy:RemovalPolicy.RETAIN,autoDeleteObjects:false,
    });
    const webHeaders=new cloudfront.ResponseHeadersPolicy(this,'WebHeaders',{
      securityHeadersBehavior:{
        contentTypeOptions:{override:true},frameOptions:{frameOption:cloudfront.HeadersFrameOption.DENY,override:true},
        referrerPolicy:{referrerPolicy:cloudfront.HeadersReferrerPolicy.NO_REFERRER,override:true},
        strictTransportSecurity:{accessControlMaxAge:Duration.days(365),includeSubdomains:true,override:true},
        contentSecurityPolicy:{contentSecurityPolicy:`default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://${c.domain} https://${c.cognitoDomainPrefix}.auth.${c.region}.amazoncognito.com https://cognito-idp.${c.region}.amazonaws.com; object-src 'none'; base-uri 'self'; frame-ancestors 'none'`,override:true},
      },
      customHeadersBehavior:{customHeaders:[{header:'Permissions-Policy',value:'camera=(self), microphone=(), geolocation=()',override:true}]},
    });
    const navigation=new cloudfront.Function(this,'WebNavigation',{
      runtime:cloudfront.FunctionRuntime.JS_2_0,
      code:cloudfront.FunctionCode.fromInline("function handler(event) { var request = event.request; if ((request.method === 'GET' || request.method === 'HEAD') && /^\\/[a-zA-Z0-9_\\/-]*$/.test(request.uri)) request.uri = '/index.html'; return request; }"),
    });
    const distribution=new cloudfront.Distribution(this,'WebDelivery',{
      defaultRootObject:'index.html',minimumProtocolVersion:cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      ...(c.webDomain?{domainNames:[c.webDomain],certificate:acm.Certificate.fromCertificateArn(this,'WebCertificate',c.webCertificateArn!)}:{}),
      defaultBehavior:{
        origin:origins.S3BucketOrigin.withOriginAccessControl(web,{originPath:`/releases/${c.releaseId}`}),
        viewerProtocolPolicy:cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods:cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        cachePolicy:cloudfront.CachePolicy.CACHING_DISABLED,responseHeadersPolicy:webHeaders,compress:true,
        functionAssociations:[{eventType:cloudfront.FunctionEventType.VIEWER_REQUEST,function:navigation}],
      },
      // Rewrite only extensionless SPA navigation; missing assets stay errors.
    });
    const webOrigin=`https://${c.webDomain??distribution.distributionDomainName}`;
    const redirects=[...c.oauthRedirectUris,webOrigin+'/'];
    const logouts=[...c.oauthLogoutUris,webOrigin+'/'];
    artifacts.addLifecycleRule({id:'TaggedOrphansOnly',enabled:true,tagFilters:{disposition:'orphan'},expiration:Duration.days(1),noncurrentVersionExpiration:Duration.days(1)});
    artifacts.addLifecycleRule({id:'AbandonedMultipart',enabled:true,abortIncompleteMultipartUploadAfter:Duration.days(1)});
    // Access expires at 24 hours in the API. Lifecycle is a delayed safety net.
    exports.addLifecycleRule({id:'ExpiredExports',expiration:Duration.days(2),noncurrentVersionExpiration:Duration.days(1),abortIncompleteMultipartUploadAfter:Duration.days(1)});
    // Journal has no automatic expiration: pruning requires recovery-point inventory proof.

    const dlq=new sqs.Queue(this,'DeadLetterQueue',{encryption:sqs.QueueEncryption.KMS,encryptionMasterKey:dataKey,retentionPeriod:Duration.days(14),visibilityTimeout:Duration.seconds(120),enforceSSL:true});
    const queue=new sqs.Queue(this,'JobsQueue',{encryption:sqs.QueueEncryption.KMS,encryptionMasterKey:dataKey,retentionPeriod:Duration.days(4),visibilityTimeout:Duration.seconds(120),receiveMessageWaitTime:Duration.seconds(20),deadLetterQueue:{queue:dlq,maxReceiveCount:5},enforceSSL:true});

    const userPool=new cognito.UserPool(this,'Accounts',{
      userPoolName:prefix,featurePlan:cognito.FeaturePlan.LITE,selfSignUpEnabled:true,signInAliases:{email:true},autoVerify:{email:true},
      accountRecovery:cognito.AccountRecovery.EMAIL_ONLY,
      passwordPolicy:{minLength:12,requireLowercase:true,requireUppercase:true,requireDigits:true,requireSymbols:true},
      mfa:cognito.Mfa.OPTIONAL,mfaSecondFactor:{sms:false,otp:true},
      removalPolicy:RemovalPolicy.RETAIN,deletionProtection:true,
    });
    const userPoolDomain=userPool.addDomain('HostedSignIn',{cognitoDomain:{domainPrefix:c.cognitoDomainPrefix}});
    const client=userPool.addClient('MobileClient',{
      generateSecret:false,enableTokenRevocation:true,preventUserExistenceErrors:true,
      authFlows:{userSrp:true},
      accessTokenValidity:Duration.minutes(15),idTokenValidity:Duration.minutes(15),refreshTokenValidity:Duration.days(30),
      oAuth:{flows:{authorizationCodeGrant:true,implicitCodeGrant:false},scopes:[cognito.OAuthScope.OPENID,cognito.OAuthScope.EMAIL,cognito.OAuthScope.PROFILE],callbackUrls:redirects,logoutUrls:logouts},
    });
    const issuer=`https://cognito-idp.${c.region}.amazonaws.com/${userPool.userPoolId}`;
    const cluster=new ecs.Cluster(this,'Cluster',{vpc,clusterName:prefix,containerInsightsV2:ecs.ContainerInsights.DISABLED});
    const logGroup=new logs.LogGroup(this,'ApplicationLogs',{encryptionKey:dataKey,retention:prod?logs.RetentionDays.ONE_MONTH:logs.RetentionDays.ONE_WEEK,removalPolicy:RemovalPolicy.RETAIN});
    const image=ecs.ContainerImage.fromEcrRepository(props.repository,c.imageDigest);
    const environment:Record<string,string>={
      OTGD_ENVIRONMENT:c.environment,OTGD_DATABASE_HOST:database.dbInstanceEndpointAddress,
      OTGD_DATABASE_PORT:database.dbInstanceEndpointPort,OTGD_DATABASE_NAME:'otgd',OTGD_DATABASE_USER:'otgd_app',
      OTGD_DATABASE_SSLMODE:'verify-full',OTGD_DATABASE_SSLROOTCERT:'/app/infra/certs/global-bundle.pem',
      OTGD_ISSUER:issuer,OTGD_CLIENT_ID:client.userPoolClientId,OTGD_JWKS_URL:`${issuer}/.well-known/jwks.json`,
      OTGD_API_ORIGIN:`https://${c.domain}`,OTGD_IDENTITY_ORIGIN:userPoolDomain.baseUrl(),
      OTGD_OAUTH_REDIRECT_URIS:JSON.stringify(redirects),OTGD_AWS_REGION:c.region,
      OTGD_DEPLOYMENT_ACCOUNT:c.account,OTGD_SOURCE_REVISION:c.releaseId,
      OTGD_ARTIFACT_BUCKET:artifacts.bucketName,OTGD_EXPORT_BUCKET:exports.bucketName,OTGD_JOURNAL_BUCKET:journal.bucketName,
      OTGD_QUEUE_URL:queue.queueUrl,OTGD_DLQ_URL:dlq.queueUrl,OTGD_USER_POOL_ID:userPool.userPoolId,
      OTGD_TOMBSTONE_KEY_ID:'v1',OTGD_STORAGE_KMS_KEY_ID:dataKey.keyArn,OTGD_JOURNAL_KMS_KEY_ID:journalKey.keyArn,
      OTGD_RECOVERY_REQUIRED:String(c.recoveryRequired),PYTHONDONTWRITEBYTECODE:'1',PYTHONUNBUFFERED:'1',UV_NO_SYNC:'1',
    };
    const runtimeSecrets={OTGD_DATABASE_PASSWORD:ecs.Secret.fromSecretsManager(appSecret,'password'),OTGD_TOMBSTONE_KEY:ecs.Secret.fromSecretsManager(tombstoneSecret,'key')};
    const definition=(name:string,cpu:number,memory:number,command:string[],pool:number,dbMigration=false)=>{
      const task=new ecs.FargateTaskDefinition(this,`${name}Task`,{cpu,memoryLimitMiB:memory,runtimePlatform:{operatingSystemFamily:ecs.OperatingSystemFamily.LINUX,cpuArchitecture:ecs.CpuArchitecture.X86_64}});
      task.addContainer(name,{
        image,command,user:'10001',readonlyRootFilesystem:true,
        environment:{...environment,OTGD_DATABASE_POOL_SIZE:String(pool),...(dbMigration?{OTGD_DATABASE_USER:'otgd_migrator',OTGD_APP_DATABASE_USER:'otgd_app'}:{})},
        secrets:dbMigration?{...runtimeSecrets,OTGD_DATABASE_PASSWORD:ecs.Secret.fromSecretsManager(database.secret!,'password'),OTGD_APP_DATABASE_PASSWORD:ecs.Secret.fromSecretsManager(appSecret,'password')}:runtimeSecrets,
        logging:ecs.LogDrivers.awsLogs({logGroup,streamPrefix:name}),stopTimeout:Duration.seconds(120),
        linuxParameters:new ecs.LinuxParameters(this,`${name}Linux`,{initProcessEnabled:true}),
        ...(name==='worker'?{healthCheck:{
          command:['CMD','uv','run','--no-sync','python','-m','otgd.worker_health'],
          interval:Duration.seconds(10),timeout:Duration.seconds(5),retries:3,startPeriod:Duration.seconds(35),
        }}:{}),
      });
      // Private writable scratch for bounded exports; never a shared/public volume.
      task.addVolume({name:'scratch'});
      task.defaultContainer!.addMountPoints({containerPath:'/tmp',sourceVolume:'scratch',readOnly:false});
      return task;
    };
    const api=definition('api',prod?512:256,prod?1024:512,['uv','run','--no-sync','uvicorn','otgd.main:app','--host','0.0.0.0','--port','8000','--no-access-log','--limit-concurrency','100','--timeout-graceful-shutdown','100'],5);
    api.defaultContainer!.addEnvironment('OTGD_CAPTURE_SIGNING_KEY_ID',captureSigningKey.keyArn);
    api.addToTaskRolePolicy(new iam.PolicyStatement({actions:['kms:Sign','kms:GetPublicKey'],resources:[captureSigningKey.keyArn]}));
    api.defaultContainer!.addPortMappings({containerPort:8000});
    const worker=definition('worker',512,1024,['uv','run','--no-sync','python','-m','otgd.worker'],3);
    worker.addContainer('metrics',{
      image,command:['uv','run','--no-sync','python','/app/scripts/publish-metrics.py'],
      user:'10001',readonlyRootFilesystem:true,essential:true,
      environment:{...environment,OTGD_DATABASE_POOL_SIZE:'1'},secrets:runtimeSecrets,
      logging:ecs.LogDrivers.awsLogs({logGroup,streamPrefix:'metrics'}),stopTimeout:Duration.seconds(30),
    });
    const migration=definition('migration',512,1024,['uv','run','--no-sync','python','-m','otgd.migrate'],1,true);
    migration.defaultContainer!.addEnvironment('OTGD_CAPTURE_SIGNING_KEY_ID',captureSigningKey.keyArn);
    migration.addToTaskRolePolicy(new iam.PolicyStatement({actions:['kms:GetPublicKey'],resources:[captureSigningKey.keyArn]}));
    const objectPolicy=(task:ecs.FargateTaskDefinition,b:s3.Bucket,permissions:string[])=>task.addToTaskRolePolicy(new iam.PolicyStatement({actions:permissions,resources:[b.arnForObjects('*')]}));
    const listPolicy=(task:ecs.FargateTaskDefinition,b:s3.Bucket)=>task.addToTaskRolePolicy(new iam.PolicyStatement({actions:['s3:ListBucket','s3:ListBucketVersions','s3:GetBucketLocation','s3:GetBucketVersioning'],resources:[b.bucketArn]}));
    objectPolicy(api,artifacts,['s3:PutObject','s3:GetObject','s3:GetObjectVersion','s3:GetObjectTagging','s3:GetObjectVersionTagging']);
    objectPolicy(api,exports,['s3:GetObject','s3:GetObjectVersion']);
    for (const b of [artifacts,exports]) {
      objectPolicy(worker,b,['s3:PutObject','s3:GetObject','s3:GetObjectVersion','s3:DeleteObject','s3:DeleteObjectVersion','s3:PutObjectTagging','s3:PutObjectVersionTagging','s3:AbortMultipartUpload']);
      listPolicy(worker,b);
    }
    for (const task of [api,worker,migration]) {
      objectPolicy(task,journal,['s3:PutObject','s3:GetObject','s3:GetObjectVersion']);
      listPolicy(task,journal);
      dataKey.grantEncryptDecrypt(task.taskRole);journalKey.grantEncryptDecrypt(task.taskRole);
      queue.grantSendMessages(task.taskRole);
      task.addToTaskRolePolicy(new iam.PolicyStatement({actions:['cloudwatch:PutMetricData'],resources:['*'],conditions:{StringEquals:{'cloudwatch:namespace':`OTGD/${c.environment}`}}}));
    }
    for (const b of [artifacts,exports]) {listPolicy(api,b);listPolicy(migration,b);}
    migration.addToTaskRolePolicy(new iam.PolicyStatement({actions:['sqs:GetQueueAttributes','sqs:GetQueueUrl'],resources:[queue.queueArn,dlq.queueArn]}));
    queue.grantConsumeMessages(worker.taskRole);dlq.grantSendMessages(worker.taskRole);
    worker.addToTaskRolePolicy(new iam.PolicyStatement({actions:['cognito-idp:AdminDeleteUser','cognito-idp:AdminUserGlobalSignOut'],resources:[userPool.userPoolArn]}));
    // Only signed create-if-absent uploads for the participant-facing signer.
    artifacts.addToResourcePolicy(new iam.PolicyStatement({effect:iam.Effect.DENY,principals:[api.taskRole],actions:['s3:PutObject'],resources:[artifacts.arnForObjects('*')],conditions:{Null:{'s3:if-none-match':'true'}}}));
    artifacts.addToResourcePolicy(new iam.PolicyStatement({effect:iam.Effect.DENY,principals:[api.taskRole],actions:['s3:PutObject'],resources:[artifacts.arnForObjects('*')],conditions:{StringNotEquals:{'s3:if-none-match':'*'}}}));
    journal.addToResourcePolicy(new iam.PolicyStatement({effect:iam.Effect.DENY,principals:[api.taskRole,worker.taskRole,migration.taskRole],actions:['s3:DeleteObject','s3:DeleteObjectVersion'],resources:[journal.arnForObjects('*')]}));
    for (const task of [api,worker,migration]) {
      journal.addToResourcePolicy(new iam.PolicyStatement({effect:iam.Effect.DENY,principals:[task.taskRole],actions:['s3:PutObject'],resources:[journal.arnForObjects('*')],conditions:{StringNotEquals:{'s3:if-none-match':'*'}}}));
    }

    const loadBalancer=new elb.ApplicationLoadBalancer(this,'Ingress',{vpc,internetFacing:true,dropInvalidHeaderFields:true,idleTimeout:Duration.seconds(120)});
    loadBalancer.addListener('Redirect',{port:80,defaultAction:elb.ListenerAction.redirect({port:'443',protocol:'HTTPS',permanent:true})});
    const https=loadBalancer.addListener('Tls',{port:443,protocol:elb.ApplicationProtocol.HTTPS,certificates:[acm.Certificate.fromCertificateArn(this,'Certificate',c.certificateArn)],sslPolicy:elb.SslPolicy.RECOMMENDED_TLS});
    apiSg.addIngressRule(loadBalancer.connections.securityGroups[0],ec2.Port.tcp(8000),'ALB only');
    const service=new ecs.FargateService(this,'ApiService',{cluster,taskDefinition:api,desiredCount:c.activateServices?(prod?2:1):0,assignPublicIp:false,securityGroups:[apiSg],vpcSubnets:{subnetType:ec2.SubnetType.PRIVATE_WITH_EGRESS},minHealthyPercent:100,maxHealthyPercent:200,circuitBreaker:{rollback:true},healthCheckGracePeriod:Duration.seconds(90),enableExecuteCommand:false});
    const targetGroup=https.addTargets('Api',{port:8000,protocol:elb.ApplicationProtocol.HTTP,targets:[service],deregistrationDelay:Duration.seconds(100),healthCheck:{path:'/health/ready',healthyHttpCodes:'200',interval:Duration.seconds(30),timeout:Duration.seconds(5)}});
    const workerService=new ecs.FargateService(this,'WorkerService',{cluster,taskDefinition:worker,desiredCount:c.activateServices?1:0,assignPublicIp:false,securityGroups:[workerSg],vpcSubnets:{subnetType:ec2.SubnetType.PRIVATE_WITH_EGRESS},minHealthyPercent:100,maxHealthyPercent:200,circuitBreaker:{rollback:true},enableExecuteCommand:false});
    if (prod && c.activateServices) {
      const scale=service.autoScaleTaskCount({minCapacity:2,maxCapacity:4});
      scale.scaleOnCpuUtilization('Cpu',{targetUtilizationPercent:60,scaleOutCooldown:Duration.seconds(60),scaleInCooldown:Duration.minutes(5)});
      const workerScale=workerService.autoScaleTaskCount({minCapacity:1,maxCapacity:2});
      workerScale.scaleOnMetric('QueueBacklog',{metric:queue.metricApproximateNumberOfMessagesVisible(),scalingSteps:[{upper:0,change:-1},{lower:10,change:1}],adjustmentType:undefined,cooldown:Duration.minutes(2)});
    }
    if (c.hostedZoneId) {
      const zone=route53.HostedZone.fromHostedZoneAttributes(this,'Zone',{hostedZoneId:c.hostedZoneId,zoneName:c.hostedZoneName!});
      new route53.ARecord(this,'ApiDns',{zone,recordName:c.domain,target:route53.RecordTarget.fromAlias(new targets.LoadBalancerTarget(loadBalancer))});
      if(c.webDomain) new route53.CnameRecord(this,'WebDns',{zone,recordName:c.webDomain,domainName:distribution.distributionDomainName,ttl:Duration.minutes(5)});
    }

    const notifications=new sns.Topic(this,'OperationalNotifications',{masterKey:dataKey});
    dataKey.addToResourcePolicy(new iam.PolicyStatement({principals:[new iam.ServicePrincipal('cloudwatch.amazonaws.com')],actions:['kms:Decrypt','kms:GenerateDataKey*'],resources:['*'],conditions:{StringEquals:{'aws:SourceAccount':c.account},ArnLike:{'aws:SourceArn':`arn:aws:cloudwatch:${c.region}:${c.account}:alarm:*`}}}));
    notifications.addSubscription(new subscriptions.EmailSubscription(c.alarmEmail));
    const alarm=(name:string,metric:cw.IMetric,threshold:number,periods=1)=>{
      const a=new cw.Alarm(this,name,{metric,threshold,evaluationPeriods:periods,treatMissingData:cw.TreatMissingData.NOT_BREACHING,comparisonOperator:cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD});
      a.addAlarmAction(new actions.SnsAction(notifications));return a;
    };
    alarm('DeadLetterMessages',dlq.metricApproximateNumberOfMessagesVisible({period:Duration.minutes(1)}),1);
    alarm('OldSourceMessage',queue.metricApproximateAgeOfOldestMessage({period:Duration.minutes(1)}),300);
    const custom=(metricName:string)=>new cw.Metric({namespace:`OTGD/${c.environment}`,metricName,statistic:'Maximum',period:Duration.minutes(1)});
    alarm('OldOutbox',custom('OldestOutboxSeconds'),120);
    alarm('OldPrivacyJob',custom('OldestPrivacyJobSeconds'),900);
    alarm('LateCleanup',custom('CleanupOverdueCount'),1);
    alarm('PoolPressure',database.metricDatabaseConnections({period:Duration.minutes(1)}),prod?70:30,5);
    if (prod) alarm('UnhealthyTargets',targetGroup.metrics.unhealthyHostCount({period:Duration.minutes(1)}),1,5);
    const errorPercent=new cw.MathExpression({expression:'IF(requests>=20,100*errors/requests,0)',period:Duration.minutes(5),usingMetrics:{requests:loadBalancer.metrics.requestCount({period:Duration.minutes(5),statistic:'Sum'}),errors:loadBalancer.metrics.httpCodeTarget(elb.HttpCodeTarget.TARGET_5XX_COUNT,{period:Duration.minutes(5),statistic:'Sum'})}});
    alarm('ApiErrorRate',errorPercent,5);
    new budgets.CfnBudget(this,'MonthlyBudget',{
      budget:{budgetName:`${prefix}-monthly`,budgetType:'COST',timeUnit:'MONTHLY',budgetLimit:{amount:c.monthlyBudgetUsd,unit:'USD'},costFilters:{TagKeyValue:[`user:deployment$${prefix}`]}},
      notificationsWithSubscribers:[...([50,80,100] as const).map(threshold=>({notification:{comparisonOperator:'GREATER_THAN',notificationType:'ACTUAL',threshold,thresholdType:'PERCENTAGE'},subscribers:[{address:c.alarmEmail,subscriptionType:'EMAIL'}]})),{notification:{comparisonOperator:'GREATER_THAN',notificationType:'FORECASTED',threshold:100,thresholdType:'PERCENTAGE'},subscribers:[{address:c.alarmEmail,subscriptionType:'EMAIL'}]}],
    });
    const recoveryRole=new iam.Role(this,'RecoveryOperatorRole',{assumedBy:new iam.AccountPrincipal(c.account).withConditions({Bool:{'aws:MultiFactorAuthPresent':'true'}}),description:'Audited MFA operator: inspect independent journal and run bounded maintenance task'});
    journal.grantRead(recoveryRole);journalKey.grantDecrypt(recoveryRole);
    recoveryRole.addToPolicy(new iam.PolicyStatement({actions:['ecs:RunTask'],resources:[migration.taskDefinitionArn],conditions:{ArnEquals:{'ecs:cluster':cluster.clusterArn}}}));
    recoveryRole.addToPolicy(new iam.PolicyStatement({actions:['iam:PassRole'],resources:[migration.taskRole.roleArn,migration.executionRole!.roleArn],conditions:{StringEquals:{'iam:PassedToService':'ecs-tasks.amazonaws.com'}}}));
    // ECS DescribeTasks has no resource-level scope; inspection only, no secrets.
    recoveryRole.addToPolicy(new iam.PolicyStatement({actions:['ecs:DescribeTasks'],resources:['*']}));

    // No assumer identity/policy is assigned here. Account operators must grant
    // three distinct humans permission to assume their corresponding MFA role.
    // The registry CLI runs with that host's verified STS identity over an
    // approved private DB path; a generic ECS task identity is not a reviewer.
    const registryRoles={
      RegistrySubmitter:new iam.Role(this,'RegistrySubmitter',{roleName:`${prefix}-registry-submitter`,assumedBy:new iam.AccountPrincipal(c.account).withConditions({Bool:{'aws:MultiFactorAuthPresent':'true'}}),maxSessionDuration:Duration.hours(1),description:'MFA operator host: submit typed registry evidence; no runtime trust'}),
      RegistryReviewer:new iam.Role(this,'RegistryReviewer',{roleName:`${prefix}-registry-reviewer`,assumedBy:new iam.AccountPrincipal(c.account).withConditions({Bool:{'aws:MultiFactorAuthPresent':'true'}}),maxSessionDuration:Duration.hours(1),description:'Independent MFA operator host: review immutable registry evidence'}),
      RegistryReleaser:new iam.Role(this,'RegistryReleaser',{roleName:`${prefix}-registry-releaser`,assumedBy:new iam.AccountPrincipal(c.account).withConditions({Bool:{'aws:MultiFactorAuthPresent':'true'}}),maxSessionDuration:Duration.hours(1),description:'Independent MFA operator host: release or revoke reviewed registries'}),
    };
    for(const role of Object.values(registryRoles)) {
      role.addToPolicy(new iam.PolicyStatement({actions:['iam:GetRole'],resources:Object.values(registryRoles).map(value=>value.roleArn)}));
      database.secret!.grantRead(role);
      // Deliberately no ECS RunTask/PassRole, participant trust or study/model
      // auto-provisioning. Invocation retains the human's authenticated role.
    }
    registryRoles.RegistryReleaser.addToPolicy(new iam.PolicyStatement({actions:['s3:PutObject'],resources:[journal.arnForObjects('scope-resumptions/*')]}));
    registryRoles.RegistryReleaser.addToPolicy(new iam.PolicyStatement({actions:['s3:ListBucket','s3:ListBucketVersions','s3:GetBucketLocation','s3:GetBucketVersioning','s3:GetBucketObjectLockConfiguration'],resources:[journal.bucketArn]}));
    registryRoles.RegistryReleaser.addToPolicy(new iam.PolicyStatement({actions:['s3:GetObject','s3:GetObjectVersion','s3:GetObjectRetention'],resources:[journal.arnForObjects('*')]}));
    registryRoles.RegistryReleaser.addToPolicy(new iam.PolicyStatement({actions:['kms:GenerateDataKey','kms:Encrypt','kms:Decrypt'],resources:[journalKey.keyArn]}));
    // Runtime event writers cannot fabricate independently reviewed restore
    // resumption authority, even with their general journal event grants.
    journal.addToResourcePolicy(new iam.PolicyStatement({effect:iam.Effect.DENY,principals:[api.taskRole,worker.taskRole,migration.taskRole],actions:['s3:PutObject'],resources:[journal.arnForObjects('scope-resumptions/*')]}));

    const output:Record<string,string>={ApiOrigin:`https://${c.domain}`,LoadBalancerDns:loadBalancer.loadBalancerDnsName,Issuer:issuer,ClientId:client.userPoolClientId,IdentityOrigin:userPoolDomain.baseUrl(),Cluster:cluster.clusterArn,ApiService:service.serviceName,WorkerService:workerService.serviceName,MigrationTaskDefinition:migration.taskDefinitionArn,MigrationSecurityGroup:migrationSg.securityGroupId,PrivateSubnets:vpc.privateSubnets.map(x=>x.subnetId).join(','),DatabaseIdentifier:database.instanceIdentifier,DatabaseHost:database.dbInstanceEndpointAddress,DatabaseConnectionBudget:String(prod?80:40),DatabaseRecoveryOrigin:c.databaseSnapshotIdentifier??'new',RecoveryRequired:String(c.recoveryRequired),ArtifactBucket:artifacts.bucketName,ExportBucket:exports.bucketName,JournalBucket:journal.bucketName,QueueUrl:queue.queueUrl,DeadLetterQueueUrl:dlq.queueUrl,ApplicationDatabaseSecret:appSecret.secretArn,TombstoneKeySecret:tombstoneSecret.secretArn,JournalKeyArn:journalKey.keyArn,DataKeyArn:dataKey.keyArn,ImageDigest:c.imageDigest,ReleaseId:c.releaseId,RecoveryOperatorRole:recoveryRole.roleArn,LogGroup:logGroup.logGroupName};
    Object.assign(output,{WebOrigin:webOrigin,WebCallbackUri:webOrigin+'/',WebBucket:web.bucketName,WebDistributionId:distribution.distributionId,WebDistributionDomain:distribution.distributionDomainName,WebReleasePrefix:`releases/${c.releaseId}`,CaptureSigningKeyArn:captureSigningKey.keyArn});
    for(const [name,role] of Object.entries(registryRoles)) output[name]=role.roleArn;
    for (const [key,value] of Object.entries(output)) new CfnOutput(this,`Output${key}`,{value}).overrideLogicalId(key);
  }
}
