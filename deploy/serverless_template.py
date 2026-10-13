"""Build the AWS serverless deployment without credentials or SDK side effects.

PostgreSQL remains private and authoritative. A small DynamoDB control table
contains scheduling metadata, while Lambda, SQS and scheduled control replace
resident API/worker processes. PostgreSQL can pause between work periods.
"""
from __future__ import annotations

import json
import math
import re


def ref(name):
    return {"Ref": name}


def att(name, attribute):
    return {"Fn::GetAtt": [name, attribute]}


def sub(value, variables=None):
    return {"Fn::Sub": [value, variables]} if variables else {"Fn::Sub": value}


def regional_global_name(name, region):
    """Account-global names cannot collide with retained Ohio resources."""
    if region not in ("us-east-1", "us-east-2"):
        raise ValueError("Global names require a reviewed primary region")
    return name + ("-us-east-1" if region == "us-east-1" else "")


def build_template(config, phase="platform", *, regional_fargate=False):
    """Return CloudFormation JSON for registry or stopped/active platform phases."""
    if type(regional_fargate) is not bool:
        raise ValueError("Regional Fargate construction must be explicitly selected")
    if regional_fargate:
        if (config.get("environment") != "fargate-development"
                or config.get("region") != "us-east-1" or config.get("backupRegion") != "us-west-2"
                or config.get("prefix", "otgd-serverless-development") != "otgd-serverless-development"):
            raise ValueError("Regional Fargate construction requires East 1 with West 2 backups")
        config = {key: value for key, value in config.items() if key != "backupRegion"}
    elif "backupRegion" in config:
        raise ValueError("Backup settings require explicit regional Fargate construction")
    account, region = config["account"], config["region"]
    revision, email = config["releaseId"], config["alarmEmail"]
    budget = config["monthlyBudgetUsd"]
    prefix = config.get("prefix", "otgd-serverless-development")
    active = config.get("activateServices", False)
    if not re.fullmatch(r"[0-9]{12}", account) or region != ("us-east-1" if regional_fargate else "us-east-2"):
        raise ValueError("Set the actual account and reviewed us-east-2 region")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("releaseId must be an immutable full source SHA")
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,27}", prefix):
        raise ValueError("Invalid serverless resource prefix")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("Set the actual alarm recipient")
    if isinstance(budget, bool) or not isinstance(budget, (float, int)) or not math.isfinite(budget) or not 0 < budget <= 50:
        raise ValueError("The reviewed serverless budget must be positive and at most USD 50")
    if not isinstance(active, bool) or phase not in ("registry", "platform"):
        raise ValueError("Invalid activation flag or deployment phase")
    tags = [{"Key": key, "Value": value} for key, value in {
        "project": "one-the-go-detection", "environment": "serverless-development",
        "deployment": prefix, "owner_role": config.get("ownerRole", "platform-operator"),
        "cost_center": config.get("costCenter", "serverless-development"),
    }.items()]
    dashboard_name = regional_global_name(prefix + "-health", region)
    registry_names = {duty: regional_global_name("otgd-qa-registry-" + duty, region)
                      for duty in ("submitter", "reviewer", "releaser")}
    resources = {}

    def resource(name, kind, properties, **options):
        resources[name] = {"Type": kind, "Properties": properties, **options}

    def retained(name, kind, properties):
        resource(name, kind, properties, DeletionPolicy="Retain", UpdateReplacePolicy="Retain")

    def output(values):
        return {"AWSTemplateFormatVersion": "2010-09-09", "Description": "On-The-Go Detection AWS serverless deployment", "Resources": resources, "Outputs": {key: {"Value": value} for key, value in values.items()}}

    if phase == "registry":
        retained("Images", "AWS::ECR::Repository", {
            "RepositoryName": prefix, "ImageTagMutability": "IMMUTABLE",
            "ImageScanningConfiguration": {"ScanOnPush": True},
            "EncryptionConfiguration": {"EncryptionType": "AES256"}, "Tags": tags,
            "RepositoryPolicyText": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"], "Condition": {"ArnLike": {"aws:SourceArn": f"arn:aws:lambda:{region}:{account}:function:{prefix}-*"}}}]},
        })
        retained("DeploymentAssets", "AWS::S3::Bucket", {"BucketName": f"{prefix}-{account}-{region}-deployments", "VersioningConfiguration": {"Status": "Enabled"}, "PublicAccessBlockConfiguration": {"BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True}, "OwnershipControls": {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}, "BucketEncryption": {"ServerSideEncryptionConfiguration": [{"ServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}, "Tags": tags})
        resource("DeploymentAssetsPolicy", "AWS::S3::BucketPolicy", {"Bucket": ref("DeploymentAssets"), "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Deny", "Principal": "*", "Action": "s3:*", "Resource": [att("DeploymentAssets", "Arn"), sub("${Arn}/*", {"Arn": att("DeploymentAssets", "Arn")})], "Condition": {"Bool": {"aws:SecureTransport": "false"}}}]}})
        return output({"RepositoryName": ref("Images"), "RepositoryUri": att("Images", "RepositoryUri"), "RepositoryArn": att("Images", "Arn"), "DeploymentBucket": ref("DeploymentAssets"), "TemplateBucket": ref("DeploymentAssets")})
    images = {}
    for role, setting in [("Api", "apiImageUri"), ("Worker", "workerImageUri")]:
        value = config.get(setting, "")
        if not re.fullmatch(re.escape(f"{account}.dkr.ecr.{region}.amazonaws.com/{prefix}@sha256:") + r"[0-9a-f]{64}", value):
            raise ValueError(f"{setting} must reference the selected account/region immutable registry digest")
        images[role] = value
    engine = config.get("databaseEngineVersion", "16.11")
    if not re.fullmatch(r"16\.\d+", engine) or int(engine.split(".")[1]) < 3:
        raise ValueError("Select an available Aurora PostgreSQL 16.3+ minor with min-zero support")
    artifact_upload_origin = f"https://s3.dualstack.{region}.amazonaws.com/{prefix}-{account}-{region}-artifacts/"

    resource("Network", "AWS::EC2::VPC", {"CidrBlock": "10.76.0.0/16", "EnableDnsSupport": True, "EnableDnsHostnames": True, "Tags": tags})
    resource("NetworkIpv6", "AWS::EC2::VPCCidrBlock", {"VpcId": ref("Network"), "AmazonProvidedIpv6CidrBlock": True})
    resource("Ipv6Egress", "AWS::EC2::EgressOnlyInternetGateway", {"VpcId": ref("Network")})
    for index, name in enumerate(["PrivateA", "PrivateB"]):
        cidr = {"Fn::Select": [index, {"Fn::Cidr": [{"Fn::Select": [0, att("Network", "Ipv6CidrBlocks")]}, 2, 64]}]}
        resource(name, "AWS::EC2::Subnet", {"VpcId": ref("Network"), "AvailabilityZone": {"Fn::Select": [index, {"Fn::GetAZs": ""}]}, "CidrBlock": f"10.76.{index}.0/24", "Ipv6CidrBlock": cidr, "AssignIpv6AddressOnCreation": True, "MapPublicIpOnLaunch": False, "Tags": tags}, DependsOn="NetworkIpv6")
        resource(name + "Routes", "AWS::EC2::RouteTable", {"VpcId": ref("Network"), "Tags": tags})
        resource(name + "Association", "AWS::EC2::SubnetRouteTableAssociation", {"SubnetId": ref(name), "RouteTableId": ref(name + "Routes")})
        resource(name + "Ipv6Route", "AWS::EC2::Route", {"RouteTableId": ref(name + "Routes"), "DestinationIpv6CidrBlock": "::/0", "EgressOnlyInternetGatewayId": ref("Ipv6Egress")})
    resource("S3Endpoint", "AWS::EC2::VPCEndpoint", {"VpcId": ref("Network"), "ServiceName": sub("com.amazonaws.${AWS::Region}.s3"), "VpcEndpointType": "Gateway", "RouteTableIds": [ref("PrivateARoutes"), ref("PrivateBRoutes")]})
    resource("LambdaSecurityGroup", "AWS::EC2::SecurityGroup", {"VpcId": ref("Network"), "GroupDescription": "Lambda: private PostgreSQL and HTTPS IPv6 AWS service access", "SecurityGroupEgress": [{"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "CidrIpv6": "::/0"}, {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "CidrIp": "0.0.0.0/0"}], "Tags": tags})
    resource("DatabaseSecurityGroup", "AWS::EC2::SecurityGroup", {"VpcId": ref("Network"), "GroupDescription": "Only Lambda clients reach private PostgreSQL", "SecurityGroupIngress": [{"IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432, "SourceSecurityGroupId": ref("LambdaSecurityGroup")}], "SecurityGroupEgress": [{"IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432, "CidrIp": "127.0.0.1/32"}], "Tags": tags})
    resource("DatabaseEgress", "AWS::EC2::SecurityGroupEgress", {"GroupId": ref("LambdaSecurityGroup"), "IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432, "DestinationSecurityGroupId": ref("DatabaseSecurityGroup")})
    root_grant = {"Effect": "Allow", "Principal": {"AWS": sub("arn:${AWS::Partition}:iam::${AWS::AccountId}:root")}, "Action": "kms:*", "Resource": "*"}
    for name in ["DataKey", "JournalKey", "CaptureSigningKey"]:
        statements = [root_grant]
        if name == "DataKey":
            statements += [{"Effect": "Allow", "Principal": {"Service": f"logs.{region}.amazonaws.com"}, "Action": ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey"], "Resource": "*", "Condition": {"ArnLike": {"kms:EncryptionContext:aws:logs:arn": f"arn:aws:logs:{region}:{account}:log-group:/{prefix}/*"}}}, {"Effect": "Allow", "Principal": {"Service": "cloudwatch.amazonaws.com"}, "Action": ["kms:Decrypt", "kms:GenerateDataKey*"], "Resource": "*", "Condition": {"StringEquals": {"aws:SourceAccount": account}, "ArnLike": {"aws:SourceArn": f"arn:aws:cloudwatch:{region}:{account}:alarm:*"}}}]
        props = {"EnableKeyRotation": name != "CaptureSigningKey", "KeyPolicy": {"Version": "2012-10-17", "Statement": statements}, "Description": prefix + " " + name, "Tags": tags}
        if name == "CaptureSigningKey":
            props.update(KeySpec="ECC_NIST_P256", KeyUsage="SIGN_VERIFY")
        retained(name, "AWS::KMS::Key", props)
    retained("ApplicationSecret", "AWS::SecretsManager::Secret", {"Name": prefix + "-database-app", "KmsKeyId": att("DataKey", "Arn"), "GenerateSecretString": {"SecretStringTemplate": json.dumps({"username": "otgd_app"}), "GenerateStringKey": "password", "PasswordLength": 40, "ExcludePunctuation": True}, "Tags": tags})
    retained("TombstoneSecret", "AWS::SecretsManager::Secret", {"Name": prefix + "-tombstone", "KmsKeyId": att("JournalKey", "Arn"), "GenerateSecretString": {"SecretStringTemplate": json.dumps({"key_id": "v1"}), "GenerateStringKey": "key", "PasswordLength": 64, "ExcludePunctuation": True, "ExcludeUppercase": True, "ExcludeCharacters": "ghijklmnopqrstuvwxyz", "RequireEachIncludedType": False}, "Tags": tags})
    resource("DatabaseSubnets", "AWS::RDS::DBSubnetGroup", {"DBSubnetGroupDescription": "Two private database zones", "SubnetIds": [ref("PrivateA"), ref("PrivateB")], "Tags": tags})
    resource("DatabaseParameters", "AWS::RDS::DBClusterParameterGroup", {"Description": "Verified PostgreSQL TLS required", "Family": "aurora-postgresql16", "Parameters": {"rds.force_ssl": "1"}, "Tags": tags})
    resource("Database", "AWS::RDS::DBCluster", {"DBClusterIdentifier": prefix, "Engine": "aurora-postgresql", "EngineVersion": engine, "EngineMode": "provisioned", "DatabaseName": "otgd", "MasterUsername": "otgd_migrator", "ManageMasterUserPassword": True, "MasterUserSecret": {"KmsKeyId": att("DataKey", "Arn")}, "StorageEncrypted": True, "KmsKeyId": att("DataKey", "Arn"), "DBSubnetGroupName": ref("DatabaseSubnets"), "DBClusterParameterGroupName": ref("DatabaseParameters"), "VpcSecurityGroupIds": [ref("DatabaseSecurityGroup")], "BackupRetentionPeriod": 7, "CopyTagsToSnapshot": True, "DeletionProtection": True, "ServerlessV2ScalingConfiguration": {"MinCapacity": 0, "MaxCapacity": 1, "SecondsUntilAutoPause": 300}, "Tags": tags}, DeletionPolicy="Snapshot", UpdateReplacePolicy="Snapshot")
    resource("DatabaseWriter", "AWS::RDS::DBInstance", {"DBInstanceIdentifier": prefix + "-writer", "DBClusterIdentifier": ref("Database"), "DBInstanceClass": "db.serverless", "Engine": "aurora-postgresql", "PubliclyAccessible": False, "AutoMinorVersionUpgrade": False, "Tags": tags}, DeletionPolicy="Retain", UpdateReplacePolicy="Retain")
    for name, suffix, key in [("Artifacts", "artifacts", "DataKey"), ("Exports", "exports", "DataKey"), ("DeletionJournal", "journal", "JournalKey"), ("WebAssets", "web", None)]:
        props = {"BucketName": f"{prefix}-{account}-{region}-{suffix}", "VersioningConfiguration": {"Status": "Enabled"}, "PublicAccessBlockConfiguration": {"BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True}, "OwnershipControls": {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}, "BucketEncryption": {"ServerSideEncryptionConfiguration": [{"BucketKeyEnabled": True, "ServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": att(key, "Arn")}}] if key else [{"ServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}, "Tags": tags}
        if name == "DeletionJournal":
            props.update(ObjectLockEnabled=True, ObjectLockConfiguration={"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Days": 90}}})
        if name == "Exports":
            props["LifecycleConfiguration"] = {"Rules": [{"Id": "ExpiredExports", "Status": "Enabled", "ExpirationInDays": 2, "NoncurrentVersionExpiration": {"NoncurrentDays": 1}, "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}}]}
        if name == "Artifacts":
            props["LifecycleConfiguration"] = {"Rules": [{"Id": "TaggedOrphans", "Status": "Enabled", "TagFilters": [{"Key": "disposition", "Value": "orphan"}], "ExpirationInDays": 1, "NoncurrentVersionExpiration": {"NoncurrentDays": 1}}, {"Id": "AbandonedMultipart", "Status": "Enabled", "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}}]}
            props["CorsConfiguration"] = {"CorsRules": [{"AllowedOrigins": [sub("https://${WebDelivery.DomainName}")], "AllowedMethods": ["PUT"], "AllowedHeaders": ["Content-Type", "If-None-Match", "x-amz-checksum-sha256", "x-amz-server-side-encryption", "x-amz-server-side-encryption-aws-kms-key-id"], "ExposedHeaders": ["ETag", "x-amz-version-id", "x-amz-checksum-sha256"], "MaxAge": 300}]}
        retained(name, "AWS::S3::Bucket", props)
    for name, retention in [("DeadLetterQueue", 1209600), ("JobsQueue", 345600)]:
        props = {"VisibilityTimeout": 1200, "MessageRetentionPeriod": retention, "KmsMasterKeyId": att("DataKey", "Arn"), "Tags": tags}
        if name == "JobsQueue":
            props.update(ReceiveMessageWaitTimeSeconds=20, RedrivePolicy={"deadLetterTargetArn": att("DeadLetterQueue", "Arn"), "maxReceiveCount": 5})
        resource(name, "AWS::SQS::Queue", props)
    resource("QueueTransport", "AWS::SQS::QueuePolicy", {"Queues": [ref("JobsQueue"), ref("DeadLetterQueue")], "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Deny", "Principal": "*", "Action": "sqs:*", "Resource": att(name, "Arn"), "Condition": {"Bool": {"aws:SecureTransport": "false"}}} for name in ["JobsQueue", "DeadLetterQueue"]]}})
    retained("RuntimeControl", "AWS::DynamoDB::Table", {"TableName": prefix + "-control", "BillingMode": "PAY_PER_REQUEST", "AttributeDefinitions": [{"AttributeName": "PK", "AttributeType": "S"}, {"AttributeName": "SK", "AttributeType": "S"}], "KeySchema": [{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}], "TimeToLiveSpecification": {"AttributeName": "expiresAt", "Enabled": True}, "SSESpecification": {"SSEEnabled": True}, "PointInTimeRecoverySpecification": {"PointInTimeRecoveryEnabled": True}, "Tags": tags})
    retained("Accounts", "AWS::Cognito::UserPool", {"UserPoolName": prefix, "UserPoolTier": "LITE", "UsernameAttributes": ["email"], "AutoVerifiedAttributes": ["email"], "AccountRecoverySetting": {"RecoveryMechanisms": [{"Name": "verified_email", "Priority": 1}]}, "Policies": {"PasswordPolicy": {"MinimumLength": 12, "RequireLowercase": True, "RequireUppercase": True, "RequireNumbers": True, "RequireSymbols": True}}, "MfaConfiguration": "OPTIONAL", "EnabledMfas": ["SOFTWARE_TOKEN_MFA"], "DeletionProtection": "ACTIVE", "UserPoolTags": {tag["Key"]: tag["Value"] for tag in tags}})
    login_prefix = prefix + "-" + account
    resource("HostedSignIn", "AWS::Cognito::UserPoolDomain", {"Domain": login_prefix, "UserPoolId": ref("Accounts")})
    for role in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"]:
        resource(role + "Logs", "AWS::Logs::LogGroup", {"LogGroupName": f"/{prefix}/{role.lower()}", "RetentionInDays": 7, "KmsKeyId": att("DataKey", "Arn"), "Tags": tags}, DeletionPolicy="Retain", UpdateReplacePolicy="Retain")

    journal_objects = sub("${Arn}/*", {"Arn": att("DeletionJournal", "Arn")})
    artifact_objects = sub("${Arn}/*", {"Arn": att("Artifacts", "Arn")})
    export_objects = sub("${Arn}/*", {"Arn": att("Exports", "Arn")})
    master_secret = att("Database", "MasterUserSecret.SecretArn")
    function_names = {name: prefix + "-" + name.lower() for name in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"]}
    dispatcher_arn = f"arn:aws:lambda:{region}:{account}:function:{function_names['Dispatcher']}"
    network_actions = ["ec2:CreateNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DescribeSubnets", "ec2:DeleteNetworkInterface", "ec2:AssignPrivateIpAddresses", "ec2:UnassignPrivateIpAddresses"]
    for role in ["Api", "Worker", "Maintenance", "Control"]:
        log_arns = [sub("${Arn}:*", {"Arn": att(role + "Logs", "Arn")})]
        if role == "Worker":
            log_arns.append(sub("${Arn}:*", {"Arn": att("DispatcherLogs", "Arn")}))
        statements = [{"Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"], "Resource": log_arns}, {"Effect": "Allow", "Action": ["cloudwatch:PutMetricData"], "Resource": "*", "Condition": {"StringEquals": {"cloudwatch:namespace": "OTGD/serverless-development"}}}, {"Effect": "Allow", "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:Query"], "Resource": att("RuntimeControl", "Arn"), "Condition": {"ForAllValues:StringEquals": {"dynamodb:LeadingKeys": ["runtime"]}}}]
        if role in ["Api", "Worker", "Control"]:
            statements += [{"Effect": "Allow", "Action": ["lambda:InvokeFunction"], "Resource": dispatcher_arn}]
        if role == "Control":
            pass
        else:
            source_functions = [f"arn:aws:lambda:{region}:{account}:function:{function_names[role]}"]
            if role == "Worker":
                source_functions.append(dispatcher_arn)
            statements += [{"Effect": "Allow", "Action": network_actions, "Resource": "*"}, {"Effect": "Deny", "Action": network_actions, "Resource": "*", "Condition": {"ArnEquals": {"lambda:SourceFunctionArn": source_functions}}}, {"Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"], "Resource": [ref("ApplicationSecret"), ref("TombstoneSecret")] + ([master_secret] if role == "Maintenance" else [])}, {"Effect": "Allow", "Action": ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey", "kms:DescribeKey"], "Resource": [att("DataKey", "Arn"), att("JournalKey", "Arn")]}, {"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectRetention", "s3:PutObject"], "Resource": journal_objects}, {"Effect": "Allow", "Action": ["s3:ListBucket", "s3:ListBucketVersions", "s3:GetBucketLocation", "s3:GetBucketVersioning", "s3:GetBucketObjectLockConfiguration"], "Resource": [att(name, "Arn") for name in ["Artifacts", "Exports", "DeletionJournal"]]}, {"Effect": "Allow", "Action": ["sqs:SendMessage", "sqs:GetQueueAttributes", "sqs:GetQueueUrl"], "Resource": [att("JobsQueue", "Arn"), att("DeadLetterQueue", "Arn")]}]
            if role == "Api":
                statements += [{"Effect": "Allow", "Action": ["s3:PutObject", "s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectTagging", "s3:GetObjectVersionTagging"], "Resource": artifact_objects}, {"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion"], "Resource": export_objects}, {"Effect": "Allow", "Action": ["kms:Sign", "kms:GetPublicKey"], "Resource": att("CaptureSigningKey", "Arn")}]
            if role in ["Worker", "Maintenance"]:
                statements += [{"Effect": "Allow", "Action": ["s3:PutObject", "s3:GetObject", "s3:GetObjectVersion", "s3:DeleteObject", "s3:DeleteObjectVersion", "s3:PutObjectTagging", "s3:PutObjectVersionTagging", "s3:AbortMultipartUpload"], "Resource": [artifact_objects, export_objects]}, {"Effect": "Allow", "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:ChangeMessageVisibility"], "Resource": att("JobsQueue", "Arn")}, {"Effect": "Allow", "Action": ["cognito-idp:AdminDeleteUser", "cognito-idp:AdminUserGlobalSignOut"], "Resource": att("Accounts", "Arn")}]
            if role == "Maintenance":
                statements += [{"Effect": "Allow", "Action": ["kms:GetPublicKey"], "Resource": att("CaptureSigningKey", "Arn")}, {"Effect": "Allow", "Action": ["iam:GetRole"], "Resource": [f"arn:aws:iam::{account}:role/{registry_names[duty]}" for duty in ["submitter", "reviewer", "releaser"]]}]
        resource(role + "Role", "AWS::IAM::Role", {"AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}, "Policies": [{"PolicyName": "ScopedServerlessExecution", "PolicyDocument": {"Version": "2012-10-17", "Statement": statements}}], "Tags": tags})
    for duty in ["submitter", "reviewer", "releaser"]:
        statements = [{"Effect": "Allow", "Action": ["iam:GetRole"], "Resource": [f"arn:aws:iam::{account}:role/{registry_names[name]}" for name in ["submitter", "reviewer", "releaser"]]}]
        if duty == "releaser":
            statements += [{"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": sub("${Arn}/scope-resumptions/*", {"Arn": att("DeletionJournal", "Arn")})}, {"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectRetention"], "Resource": journal_objects}, {"Effect": "Allow", "Action": ["s3:ListBucket", "s3:ListBucketVersions", "s3:GetBucketVersioning", "s3:GetBucketObjectLockConfiguration"], "Resource": att("DeletionJournal", "Arn")}, {"Effect": "Allow", "Action": ["kms:GenerateDataKey", "kms:Encrypt", "kms:Decrypt"], "Resource": att("JournalKey", "Arn")}]
        resource("Registry" + duty.title(), "AWS::IAM::Role", {"RoleName": registry_names[duty], "MaxSessionDuration": 3600, "AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{account}:root"}, "Action": "sts:AssumeRole", "Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}}]}, "Policies": [{"PolicyName": "IndependentRegistryOperator", "PolicyDocument": {"Version": "2012-10-17", "Statement": statements}}], "Tags": tags})
    common = {
        "OTGD_ENVIRONMENT": "qa", "OTGD_SERVERLESS_MODE": "true", "OTGD_SERVERLESS_CONTROL_TABLE": ref("RuntimeControl"), "OTGD_SERVERLESS_DISPATCH_FUNCTION_ARN": dispatcher_arn, "OTGD_SERVERLESS_QUEUE_VISIBILITY": "1200",
        "OTGD_DATABASE_HOST": att("Database", "Endpoint.Address"), "OTGD_DATABASE_PORT": "5432", "OTGD_DATABASE_NAME": "otgd", "OTGD_DATABASE_USER": "otgd_app",
        "OTGD_DATABASE_SECRET_ARN": ref("ApplicationSecret"), "OTGD_TOMBSTONE_SECRET_ARN": ref("TombstoneSecret"), "OTGD_DATABASE_POOL_SIZE": "1",
        "OTGD_DATABASE_SSLMODE": "verify-full", "OTGD_DATABASE_SSLROOTCERT": "/app/infra/certs/global-bundle.pem",
        "OTGD_DEPLOYMENT_ACCOUNT": account, "OTGD_SOURCE_REVISION": revision, "OTGD_AWS_REGION": region,
        "OTGD_ARTIFACT_BUCKET": ref("Artifacts"), "OTGD_EXPORT_BUCKET": ref("Exports"), "OTGD_JOURNAL_BUCKET": ref("DeletionJournal"),
        "OTGD_QUEUE_URL": ref("JobsQueue"), "OTGD_DLQ_URL": ref("DeadLetterQueue"), "OTGD_USER_POOL_ID": ref("Accounts"), "OTGD_TOMBSTONE_KEY_ID": "v1",
        "OTGD_STORAGE_KMS_KEY_ID": att("DataKey", "Arn"), "OTGD_JOURNAL_KMS_KEY_ID": att("JournalKey", "Arn"),
        "OTGD_RECOVERY_REQUIRED": "false", "OTGD_SERVERLESS_METRICS_NAMESPACE": "OTGD/serverless-development", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1", "UV_NO_SYNC": "1", "AWS_EC2_METADATA_DISABLED": "true",
        "OTGD_ISSUER": sub("https://cognito-idp.${AWS::Region}.amazonaws.com/${Accounts}"), "OTGD_JWKS_URL": sub("https://cognito-idp.${AWS::Region}.amazonaws.com/${Accounts}/.well-known/jwks.json"),
        "OTGD_CLIENT_ID": ref("MobileClient"), "OTGD_IDENTITY_ORIGIN": f"https://{login_prefix}.auth.{region}.amazoncognito.com",
    }
    # Function metadata references avoid a Lambda -> API Gateway -> Lambda cycle.
    common["OTGD_API_ORIGIN"] = sub("https://${ApiDelivery.DomainName}")
    common["OTGD_OAUTH_REDIRECT_URIS"] = sub('["otgd-qa://oauth/callback","https://${WebDelivery.DomainName}/"]')
    # Create the HTTP resources before Lambda functions; function ARNs in their
    # integration/permission policies are literal names, not resource references.
    resource("RestApi", "AWS::ApiGateway::RestApi", {"Name": prefix, "EndpointConfiguration": {"Types": ["REGIONAL"]}, "DisableExecuteApiEndpoint": False, "Tags": tags})
    resource("ApiProxy", "AWS::ApiGateway::Resource", {"RestApiId": ref("RestApi"), "ParentId": att("RestApi", "RootResourceId"), "PathPart": "{proxy+}"})
    # STREAM supports a 15-minute response without a buffered-mode timeout
    # quota increase. This also allows a paused database to resume before the
    # authenticated handler can determine its response status and headers.
    integration = {"Type": "AWS_PROXY", "IntegrationHttpMethod": "POST", "ResponseTransferMode": "STREAM", "TimeoutInMillis": 900000, "Uri": f"arn:aws:apigateway:{region}:lambda:path/2021-11-15/functions/arn:aws:lambda:{region}:{account}:function:{function_names['Api']}/response-streaming-invocations"}
    resource("ApiRootMethod", "AWS::ApiGateway::Method", {"RestApiId": ref("RestApi"), "ResourceId": att("RestApi", "RootResourceId"), "HttpMethod": "ANY", "AuthorizationType": "NONE", "Integration": integration}, DependsOn="ApiFunction")
    resource("ApiProxyMethod", "AWS::ApiGateway::Method", {"RestApiId": ref("RestApi"), "ResourceId": ref("ApiProxy"), "HttpMethod": "ANY", "AuthorizationType": "NONE", "Integration": integration}, DependsOn="ApiFunction")
    resource("ApiDeployment", "AWS::ApiGateway::Deployment", {"RestApiId": ref("RestApi"), "Description": revision}, DependsOn=["ApiRootMethod", "ApiProxyMethod"])
    resource("ApiStage", "AWS::ApiGateway::Stage", {"RestApiId": ref("RestApi"), "DeploymentId": ref("ApiDeployment"), "StageName": "serverless", "MethodSettings": [{"ResourcePath": "/*", "HttpMethod": "*", "ThrottlingRateLimit": 5, "ThrottlingBurstLimit": 10, "DataTraceEnabled": False}], "Tags": tags})
    resource("ApiHeaders", "AWS::CloudFront::ResponseHeadersPolicy", {"ResponseHeadersPolicyConfig": {"Name": regional_global_name(prefix + "-api", region), "SecurityHeadersConfig": {"ContentTypeOptions": {"Override": True}, "FrameOptions": {"FrameOption": "DENY", "Override": True}, "ReferrerPolicy": {"ReferrerPolicy": "no-referrer", "Override": True}, "StrictTransportSecurity": {"AccessControlMaxAgeSec": 31536000, "IncludeSubdomains": True, "Override": True}}, "CustomHeadersConfig": {"Items": [{"Header": "Cache-Control", "Value": "private, no-store", "Override": True}]}}})
    resource("ApiDelivery", "AWS::CloudFront::Distribution", {"DistributionConfig": {"Enabled": True, "HttpVersion": "http2", "IPV6Enabled": True, "PriceClass": "PriceClass_100", "ViewerCertificate": {"CloudFrontDefaultCertificate": True}, "Origins": [{"Id": "api", "DomainName": sub("${RestApi}.execute-api.${AWS::Region}.amazonaws.com"), "OriginPath": "/serverless", "CustomOriginConfig": {"OriginProtocolPolicy": "https-only", "HTTPSPort": 443, "OriginSSLProtocols": ["TLSv1.2"], "OriginReadTimeout": 60, "OriginKeepaliveTimeout": 5}}], "DefaultCacheBehavior": {"TargetOriginId": "api", "ViewerProtocolPolicy": "redirect-to-https", "AllowedMethods": ["GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"], "CachedMethods": ["GET", "HEAD"], "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", "OriginRequestPolicyId": "b689b0a8-53d0-40ab-baf2-68738e2966ac", "ResponseHeadersPolicyId": ref("ApiHeaders"), "Compress": False}}, "Tags": tags})
    resource("WebOriginAccess", "AWS::CloudFront::OriginAccessControl", {"OriginAccessControlConfig": {"Name": regional_global_name(prefix + "-web", region), "OriginAccessControlOriginType": "s3", "SigningBehavior": "always", "SigningProtocol": "sigv4"}})
    resource("WebNavigation", "AWS::CloudFront::Function", {"Name": regional_global_name(prefix + "-navigation", region), "AutoPublish": True, "FunctionConfig": {"Comment": "Extensionless web navigation only", "Runtime": "cloudfront-js-2.0"}, "FunctionCode": "function handler(event) { var request = event.request; if ((request.method === 'GET' || request.method === 'HEAD') && /^\\/[a-zA-Z0-9_\\/-]*$/.test(request.uri)) request.uri = '/index.html'; return request; }"})
    # Use the deterministic bucket path here: referencing Artifacts would cycle
    # WebDelivery -> WebHeaders -> Artifacts CORS -> WebDelivery.
    csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://${ApiDelivery.DomainName} https://" + login_prefix + ".auth." + region + ".amazoncognito.com https://cognito-idp." + region + ".amazonaws.com " + artifact_upload_origin + "; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    resource("WebHeaders", "AWS::CloudFront::ResponseHeadersPolicy", {"ResponseHeadersPolicyConfig": {"Name": regional_global_name(prefix + "-web", region), "SecurityHeadersConfig": {"ContentTypeOptions": {"Override": True}, "FrameOptions": {"FrameOption": "DENY", "Override": True}, "ReferrerPolicy": {"ReferrerPolicy": "no-referrer", "Override": True}, "StrictTransportSecurity": {"AccessControlMaxAgeSec": 31536000, "IncludeSubdomains": True, "Override": True}, "ContentSecurityPolicy": {"ContentSecurityPolicy": sub(csp), "Override": True}}, "CustomHeadersConfig": {"Items": [{"Header": "Permissions-Policy", "Value": "camera=(self), microphone=(), geolocation=()", "Override": True}]}}})
    resource("WebDelivery", "AWS::CloudFront::Distribution", {"DistributionConfig": {"Enabled": True, "DefaultRootObject": "index.html", "HttpVersion": "http2", "IPV6Enabled": True, "PriceClass": "PriceClass_100", "ViewerCertificate": {"CloudFrontDefaultCertificate": True}, "Origins": [{"Id": "web", "DomainName": att("WebAssets", "RegionalDomainName"), "OriginPath": "/releases/" + revision, "OriginAccessControlId": ref("WebOriginAccess"), "S3OriginConfig": {"OriginAccessIdentity": ""}}], "DefaultCacheBehavior": {"TargetOriginId": "web", "ViewerProtocolPolicy": "redirect-to-https", "AllowedMethods": ["GET", "HEAD", "OPTIONS"], "CachedMethods": ["GET", "HEAD"], "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", "ResponseHeadersPolicyId": ref("WebHeaders"), "Compress": True, "FunctionAssociations": [{"EventType": "viewer-request", "FunctionARN": att("WebNavigation", "FunctionARN")}] }}, "Tags": tags})
    resource("MobileClient", "AWS::Cognito::UserPoolClient", {"UserPoolId": ref("Accounts"), "GenerateSecret": False, "EnableTokenRevocation": True, "PreventUserExistenceErrors": "ENABLED", "ExplicitAuthFlows": ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"], "AllowedOAuthFlowsUserPoolClient": True, "AllowedOAuthFlows": ["code"], "AllowedOAuthScopes": ["openid", "email", "profile"], "SupportedIdentityProviders": ["COGNITO"], "CallbackURLs": ["otgd-qa://oauth/callback", sub("https://${WebDelivery.DomainName}/")], "LogoutURLs": ["otgd-qa://oauth/callback", sub("https://${WebDelivery.DomainName}/")], "AccessTokenValidity": 15, "IdTokenValidity": 15, "RefreshTokenValidity": 30, "TokenValidityUnits": {"AccessToken": "minutes", "IdToken": "minutes", "RefreshToken": "days"}})
    for role, memory, timeout, concurrency in [("Api", 1024, 900, 2), ("Worker", 2048, 180, 2), ("Dispatcher", 512, 180, 1), ("Maintenance", 512, 900, 1), ("Control", 128, 30, 1)]:
        environment = dict(common)
        environment["OTGD_SERVERLESS_ROLE"] = role.lower()
        if role == "Api":
            environment.update(OTGD_CAPTURE_SIGNING_KEY_ID=att("CaptureSigningKey", "Arn"), AWS_LWA_INVOKE_MODE="response_stream", AWS_LWA_READINESS_CHECK_PATH="/health/live", AWS_LWA_PORT="8000")
        if role == "Maintenance":
            environment.update(OTGD_DATABASE_USER="otgd_migrator", OTGD_DATABASE_SECRET_ARN=master_secret, OTGD_APP_DATABASE_USER="otgd_app", OTGD_APP_DATABASE_SECRET_ARN=ref("ApplicationSecret"), OTGD_CAPTURE_SIGNING_KEY_ID=att("CaptureSigningKey", "Arn"), OTGD_LAMBDA_MAINTENANCE_ROLE="maintenance")
        if role == "Dispatcher":
            environment["OTGD_LAMBDA_MAINTENANCE_ROLE"] = "dispatcher"
        if role == "Control":
            environment = {"OTGD_SERVERLESS_MODE": "true", "OTGD_SERVERLESS_CONTROL_ONLY": "true", "OTGD_SERVERLESS_ROLE": "control", "OTGD_SERVERLESS_CONTROL_TABLE": ref("RuntimeControl"), "OTGD_SERVERLESS_DISPATCH_FUNCTION_ARN": dispatcher_arn, "OTGD_SERVERLESS_METRICS_NAMESPACE": "OTGD/serverless-development", "OTGD_AWS_REGION": region, "OTGD_SOURCE_REVISION": revision, "PYTHONUNBUFFERED": "1", "UV_NO_SYNC": "1", "AWS_EC2_METADATA_DISABLED": "true"}
        execution_role = "Worker" if role == "Dispatcher" else role
        properties = {"FunctionName": function_names[role], "Role": att(execution_role + "Role", "Arn"), "PackageType": "Image", "Code": {"ImageUri": images["Api" if role == "Api" else "Worker"]}, "Architectures": ["x86_64"], "MemorySize": memory, "Timeout": timeout, "ReservedConcurrentExecutions": concurrency if role == "Maintenance" or active else 0, "EphemeralStorage": {"Size": 512}, "LoggingConfig": {"LogGroup": ref(role + "Logs")}, "Environment": {"Variables": environment}, "Tags": tags}
        if role != "Api":
            handler = {"Worker": "sqs_handler", "Dispatcher": "dispatch_handler", "Maintenance": "maintenance_handler", "Control": "control_handler"}[role]
            properties["ImageConfig"] = {"Command": ["otgd.serverless_worker." + handler]}
            environment["OTGD_LAMBDA_HANDLER"] = "otgd.serverless_worker." + handler
        if role != "Control":
            properties["VpcConfig"] = {"SubnetIds": [ref("PrivateA"), ref("PrivateB")], "SecurityGroupIds": [ref("LambdaSecurityGroup")], "Ipv6AllowedForDualStack": True}
        options = {"DependsOn": ["DatabaseWriter", "PrivateAIpv6Route", "PrivateBIpv6Route"]} if role != "Control" else {}
        resource(role + "Function", "AWS::Lambda::Function", properties, **options)
    resource("ApiPermission", "AWS::Lambda::Permission", {"FunctionName": ref("ApiFunction"), "Action": "lambda:InvokeFunction", "Principal": "apigateway.amazonaws.com", "SourceAccount": account, "SourceArn": sub("arn:${AWS::Partition}:execute-api:${AWS::Region}:${AWS::AccountId}:${RestApi}/*/*/*")})
    mapping = {"FunctionName": ref("WorkerFunction"), "EventSourceArn": att("JobsQueue", "Arn"), "BatchSize": 1, "Enabled": active, "FunctionResponseTypes": ["ReportBatchItemFailures"]}
    if active:
        mapping["ScalingConfig"] = {"MaximumConcurrency": 2}
    resource("WorkerMapping", "AWS::Lambda::EventSourceMapping", mapping)
    resource("ControlSchedule", "AWS::Events::Rule", {"Name": prefix + "-control", "ScheduleExpression": "rate(1 minute)", "State": "ENABLED" if active else "DISABLED", "Targets": [{"Id": "control", "Arn": att("ControlFunction", "Arn")} ]})
    resource("ControlSchedulePermission", "AWS::Lambda::Permission", {"FunctionName": ref("ControlFunction"), "Action": "lambda:InvokeFunction", "Principal": "events.amazonaws.com", "SourceAccount": account, "SourceArn": att("ControlSchedule", "Arn")})
    runtime_principals = [att(role + "Role", "Arn") for role in ["Api", "Worker", "Maintenance"]]
    for name in ["Artifacts", "Exports", "DeletionJournal", "WebAssets"]:
        objects = sub("${Arn}/*", {"Arn": att(name, "Arn")})
        statements = [{"Effect": "Deny", "Principal": "*", "Action": "s3:*", "Resource": [att(name, "Arn"), objects], "Condition": {"Bool": {"aws:SecureTransport": "false"}}}]
        if name == "WebAssets":
            statements += [{"Effect": "Allow", "Principal": {"Service": "cloudfront.amazonaws.com"}, "Action": "s3:GetObject", "Resource": objects, "Condition": {"StringEquals": {"AWS:SourceArn": sub("arn:${AWS::Partition}:cloudfront::${AWS::AccountId}:distribution/${WebDelivery}")}}}]
        if name == "DeletionJournal":
            statements += [{"Effect": "Deny", "Principal": {"AWS": runtime_principals}, "Action": ["s3:DeleteObject", "s3:DeleteObjectVersion"], "Resource": objects}, {"Effect": "Deny", "Principal": {"AWS": runtime_principals}, "Action": "s3:PutObject", "Resource": sub("${Arn}/scope-resumptions/*", {"Arn": att(name, "Arn")})}]
        if name in ["DeletionJournal", "Artifacts"]:
            principals = runtime_principals if name == "DeletionJournal" else [att("ApiRole", "Arn")]
            statements += [{"Effect": "Deny", "Principal": {"AWS": principals}, "Action": "s3:PutObject", "Resource": objects, "Condition": {"Null": {"s3:if-none-match": "true"}}}, {"Effect": "Deny", "Principal": {"AWS": principals}, "Action": "s3:PutObject", "Resource": objects, "Condition": {"StringNotEquals": {"s3:if-none-match": "*"}}}]
        resource(name + "Policy", "AWS::S3::BucketPolicy", {"Bucket": ref(name), "PolicyDocument": {"Version": "2012-10-17", "Statement": statements}})

    resource("Notifications", "AWS::SNS::Topic", {"KmsMasterKeyId": att("DataKey", "Arn"), "Subscription": [{"Protocol": "email", "Endpoint": email}], "Tags": tags})
    resource("NotificationPolicy", "AWS::SNS::TopicPolicy", {"Topics": [ref("Notifications")], "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "cloudwatch.amazonaws.com"}, "Action": "sns:Publish", "Resource": ref("Notifications"), "Condition": {"StringEquals": {"aws:SourceAccount": account}, "ArnLike": {"aws:SourceArn": f"arn:aws:cloudwatch:{region}:{account}:alarm:*"}}}]}})
    alarm_names = []
    for name, metric, namespace, threshold, dimensions in [
        *[(role + "Errors", "Errors", "AWS/Lambda", 1, [{"Name": "FunctionName", "Value": function_names[role]}]) for role in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"]],
        ("DeadLetters", "ApproximateNumberOfMessagesVisible", "AWS/SQS", 1, [{"Name": "QueueName", "Value": att("DeadLetterQueue", "QueueName")}]),
        ("OldSourceMessage", "ApproximateAgeOfOldestMessage", "AWS/SQS", 300, [{"Name": "QueueName", "Value": att("JobsQueue", "QueueName")}]),
        ("OldOutbox", "OldestOutboxSeconds", "OTGD/serverless-development", 120, []),
        ("OldPrivacyJob", "OldestPrivacyJobSeconds", "OTGD/serverless-development", 900, []),
        ("OverdueCleanup", "CleanupOverdueCount", "OTGD/serverless-development", 1, []),
    ]:
        resource(name, "AWS::CloudWatch::Alarm", {"AlarmName": prefix + "-" + name, "Namespace": namespace, "MetricName": metric, "Dimensions": dimensions, "Statistic": "Sum" if namespace == "AWS/Lambda" else "Maximum", "Period": 60, "EvaluationPeriods": 1, "Threshold": threshold, "ComparisonOperator": "GreaterThanOrEqualToThreshold", "TreatMissingData": "notBreaching", "AlarmActions": [ref("Notifications")]})
        alarm_names.append(name)
    widgets = [{"type": "text", "width": 24, "height": 3, "x": 0, "y": 0, "properties": {"markdown": "# AWS serverless system health\nLambda API/workers, private Aurora PostgreSQL (0–1 ACU) and event-driven dispatch. Aurora may pause while idle. Operational SQL metrics publish only during actual work; missing values at idle are expected. Native Lambda errors/throttles and queue age remain monitored. Confirm SNS email delivery and use deployment receipts for release verification."}}, {"type": "alarm", "width": 24, "height": 3, "x": 0, "y": 3, "properties": {"title": "Serverless alarms", "alarms": [att(name, "Arn") for name in alarm_names]}}]
    graphs = [
        ("Lambda errors and throttles", [["AWS/Lambda", metric, "FunctionName", function_names[role], {"stat": "Sum"}] for role in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"] for metric in ["Errors", "Throttles"]]),
        ("Lambda p95 duration (milliseconds)", [["AWS/Lambda", "Duration", "FunctionName", function_names[role], {"stat": "p95"}] for role in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"]]),
        ("Lambda concurrency", [["AWS/Lambda", "ConcurrentExecutions", "FunctionName", function_names[role]] for role in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"]]),
        ("Aurora capacity and connections", [["AWS/RDS", metric, "DBInstanceIdentifier", prefix + "-writer"] for metric in ["ServerlessDatabaseCapacity", "DatabaseConnections", "CPUUtilization"]]),
        ("Aurora stored bytes and I/O", [["AWS/RDS", metric, "DBClusterIdentifier", prefix, {"stat": "Sum" if metric.endswith("IOPs") else "Maximum"}] for metric in ["VolumeBytesUsed", "VolumeReadIOPs", "VolumeWriteIOPs"]]),
        ("Queues and dead letters", [["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", att("JobsQueue", "QueueName")], ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", att("DeadLetterQueue", "QueueName")], ["AWS/SQS", "ApproximateAgeOfOldestMessage", "QueueName", att("JobsQueue", "QueueName")]]),
        ("Actual outbox/privacy job age (seconds)", [["OTGD/serverless-development", "OldestOutboxSeconds"], ["OTGD/serverless-development", "OldestPrivacyJobSeconds"]]),
        ("Actual overdue cleanup count", [["OTGD/serverless-development", "CleanupOverdueCount"]]),
        ("API requests and 5xx", [["AWS/CloudFront", metric, "DistributionId", ref("ApiDelivery"), "Region", "Global", {"stat": "Sum" if metric == "Requests" else "Average"}] for metric in ["Requests", "5xxErrorRate"]]),
        ("Web requests and 5xx", [["AWS/CloudFront", metric, "DistributionId", ref("WebDelivery"), "Region", "Global", {"stat": "Sum" if metric == "Requests" else "Average"}] for metric in ["Requests", "5xxErrorRate"]]),
    ]
    for index, (title, metrics) in enumerate(graphs):
        widgets.append({"type": "metric", "width": 12, "height": 6, "x": 12 * (index % 2), "y": 6 + 6 * (index // 2), "properties": {"title": title, "view": "timeSeries", "region": "us-east-1" if index >= 8 else region, "stat": "Maximum", "period": 60, "metrics": metrics}})
    bindings = {}

    def dashboard_values(value):
        if isinstance(value, dict) and ("Ref" in value or "Fn::GetAtt" in value):
            token = "DashboardToken" + str(len(bindings))
            bindings[token] = value
            return "${" + token + "}"
        if isinstance(value, dict):
            return {key: dashboard_values(item) for key, item in value.items()}
        if isinstance(value, list):
            return [dashboard_values(item) for item in value]
        return value

    body = json.dumps(dashboard_values({"start": "-PT6H", "periodOverride": "inherit", "widgets": widgets}), separators=(",", ":"))
    resource("HealthDashboard", "AWS::CloudWatch::Dashboard", {"DashboardName": dashboard_name, "DashboardBody": sub(body, bindings)})
    resource("MonthlyBudget", "AWS::Budgets::Budget", {"Budget": {"BudgetName": regional_global_name(prefix + "-monthly", region), "BudgetType": "COST", "TimeUnit": "MONTHLY", "BudgetLimit": {"Amount": budget, "Unit": "USD"}}, "NotificationsWithSubscribers": [{"Notification": {"ComparisonOperator": "GREATER_THAN", "NotificationType": kind, "Threshold": threshold, "ThresholdType": "PERCENTAGE"}, "Subscribers": [{"Address": email, "SubscriptionType": "EMAIL"}]} for kind, threshold in [("ACTUAL", 50), ("ACTUAL", 80), ("ACTUAL", 100), ("FORECASTED", 100)]]})
    if regional_fargate:
        resources["MonthlyBudget"]["Properties"]["Budget"]["CostFilters"] = {
            "TagKeyValue": ["user:project$one-the-go-detection"]}
    values = {
        "ApiOrigin": sub("https://${ApiDelivery.DomainName}"), "WebOrigin": sub("https://${WebDelivery.DomainName}"), "WebCallbackUri": sub("https://${WebDelivery.DomainName}/"),
        "WebBucket": ref("WebAssets"), "WebDistributionId": ref("WebDelivery"), "WebDistributionDomain": att("WebDelivery", "DomainName"), "WebReleasePrefix": "releases/" + revision,
        "ApiDistributionId": ref("ApiDelivery"), "RestApiId": ref("RestApi"), "DbClusterIdentifier": ref("Database"), "DatabaseClusterIdentifier": ref("Database"), "DbHost": att("Database", "Endpoint.Address"), "DatabaseHost": att("Database", "Endpoint.Address"),
        "MigrationFunction": ref("MaintenanceFunction"), "MaintenanceFunction": ref("MaintenanceFunction"), "WorkerFunction": ref("WorkerFunction"), "ApiFunction": ref("ApiFunction"), "ControlFunction": ref("ControlFunction"), "DispatcherFunction": ref("DispatcherFunction"), "DispatcherFunctionArn": dispatcher_arn,
        "ApiImageUri": images["Api"], "WorkerImageUri": images["Worker"], "WorkerFunctionArn": att("WorkerFunction", "Arn"),
        "WorkerMapping": ref("WorkerMapping"), "ControlSchedule": ref("ControlSchedule"), "RuntimeControlTable": ref("RuntimeControl"),
        "Issuer": common["OTGD_ISSUER"], "ClientId": ref("MobileClient"), "IdentityOrigin": common["OTGD_IDENTITY_ORIGIN"], "UserPoolId": ref("Accounts"),
        "ArtifactBucket": ref("Artifacts"), "ArtifactUploadOrigin": artifact_upload_origin, "ExportBucket": ref("Exports"), "JournalBucket": ref("DeletionJournal"), "QueueUrl": ref("JobsQueue"), "DeadLetterQueueUrl": ref("DeadLetterQueue"),
        "DataKeyArn": att("DataKey", "Arn"), "JournalKeyArn": att("JournalKey", "Arn"), "CaptureSigningKeyArn": att("CaptureSigningKey", "Arn"),
        "AppDbSecret": ref("ApplicationSecret"), "TombstoneSecret": ref("TombstoneSecret"), "AdminDbSecret": master_secret,
        "CloudWatchDashboardName": dashboard_name, "CloudWatchDashboardUrl": f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#dashboards/dashboard/{dashboard_name}",
        "ReleaseId": revision, "DatabaseIdentifier": prefix + "-writer", "ActivateServices": str(active).lower(),
    }
    for role in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"]:
        values[role + "LogGroup"] = ref(role + "Logs")
    values["LogGroup"] = ref("ApiLogs")
    for duty in ["Submitter", "Reviewer", "Releaser"]:
        values["Registry" + duty] = att("Registry" + duty, "Arn")
    # A retained writer still needs its VPC, subnets and database configuration
    # after rollback. Keep that dependency graph available for reviewed recovery.
    for name in ["Network", "NetworkIpv6", "PrivateA", "PrivateB", "LambdaSecurityGroup",
                 "DatabaseSecurityGroup", "DatabaseSubnets", "DatabaseParameters", "DatabaseWriter"]:
        resources[name].update(DeletionPolicy="Retain", UpdateReplacePolicy="Retain")
    return output(values)
