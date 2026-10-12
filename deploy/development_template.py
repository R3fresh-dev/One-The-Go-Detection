"""CloudFormation for an explicitly single-host development deployment.

This preserves real AWS identity, queues and independent encrypted journal, but
does not claim managed-QA availability or container-level IAM isolation. CloudFront
VPC origins supply AWS HTTPS hostnames without a paid ALB or owned domain.
"""
from __future__ import annotations

import json
import re


def ref(name):
    return {"Ref": name}


def att(name, attribute):
    return {"Fn::GetAtt": [name, attribute]}


def sub(value, variables=None):
    return {"Fn::Sub": [value, variables]} if variables else {"Fn::Sub": value}


def build_template(config):
    """Build JSON-serializable resources; no SDK calls, credentials or mutations."""
    account, region = config["account"], config["region"]
    revision, email = config["releaseId"], config["alarmEmail"]
    budget = config["monthlyBudgetUsd"]
    prefix = config.get("prefix", "otgd-development")
    if not re.fullmatch(r"\d{12}", account) or region != "us-east-2":
        raise ValueError("Development deployment requires a real AWS account and reviewed us-east-2 region")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Development source revision must be an immutable full Git SHA")
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,39}", prefix):
        raise ValueError("Invalid development resource prefix")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("Set the actual alarm recipient")
    if isinstance(budget, bool) or not isinstance(budget, (float, int)) or not 0 < budget <= 50:
        raise ValueError("Development budget must be positive and at most USD 50")
    tags = [{"Key": k, "Value": v} for k, v in {
        "project": "one-the-go-detection", "environment": "development",
        "deployment": prefix, "owner_role": config.get("ownerRole", "platform-operator"),
        "cost_center": config.get("costCenter", "development"),
    }.items()]
    resources = {}

    def resource(name, kind, properties, **attributes):
        resources[name] = {"Type": kind, "Properties": properties, **attributes}

    def retained(name, kind, properties):
        resource(name, kind, properties, DeletionPolicy="Retain", UpdateReplacePolicy="Retain")

    resource("Network", "AWS::EC2::VPC", {"CidrBlock": "10.74.0.0/16", "EnableDnsSupport": True, "EnableDnsHostnames": True, "Tags": tags})
    resource("InternetGateway", "AWS::EC2::InternetGateway", {"Tags": tags})
    resource("InternetAttachment", "AWS::EC2::VPCGatewayAttachment", {"VpcId": ref("Network"), "InternetGatewayId": ref("InternetGateway")})
    zone = {"Fn::Select": [0, {"Fn::GetAZs": ""}]}
    for name, cidr, public in [("PublicSubnet", "10.74.0.0/24", True), ("PrivateSubnet", "10.74.1.0/24", False)]:
        resource(name, "AWS::EC2::Subnet", {"VpcId": ref("Network"), "CidrBlock": cidr, "AvailabilityZone": zone, "MapPublicIpOnLaunch": public, "Tags": tags})
        route = name + "Routes"
        resource(route, "AWS::EC2::RouteTable", {"VpcId": ref("Network"), "Tags": tags})
        resource(name + "RouteAssociation", "AWS::EC2::SubnetRouteTableAssociation", {"SubnetId": ref(name), "RouteTableId": ref(route)})
    resource("PublicInternetRoute", "AWS::EC2::Route", {"RouteTableId": ref("PublicSubnetRoutes"), "DestinationCidrBlock": "0.0.0.0/0", "GatewayId": ref("InternetGateway")}, DependsOn="InternetAttachment")
    resource("S3Endpoint", "AWS::EC2::VPCEndpoint", {"VpcId": ref("Network"), "ServiceName": sub("com.amazonaws.${AWS::Region}.s3"), "VpcEndpointType": "Gateway", "RouteTableIds": [ref("PrivateSubnetRoutes")]})
    web_egress = [{"IpProtocol": "tcp", "FromPort": p, "ToPort": p, "CidrIp": "0.0.0.0/0"} for p in [80, 443]]
    resource("AppSecurityGroup", "AWS::EC2::SecurityGroup", {"VpcId": ref("Network"), "GroupDescription": "CloudFront VPC origin only; deployment attaches AWS-managed origin security group", "SecurityGroupEgress": web_egress, "Tags": tags})
    resource("NatSecurityGroup", "AWS::EC2::SecurityGroup", {"VpcId": ref("Network"), "GroupDescription": "Private application web egress only; no SSH", "SecurityGroupIngress": [{"IpProtocol": "tcp", "FromPort": p, "ToPort": p, "CidrIp": "10.74.1.0/24"} for p in [80, 443]], "SecurityGroupEgress": web_egress, "Tags": tags})

    root_key_statement = {"Sid": "AccountAdministration", "Effect": "Allow", "Principal": {"AWS": sub("arn:${AWS::Partition}:iam::${AWS::AccountId}:root")}, "Action": "kms:*", "Resource": "*"}
    for name in ["DataKey", "JournalKey"]:
        statements = [root_key_statement]
        if name == "DataKey":
            statements = statements + [{"Effect": "Allow", "Principal": {"Service": f"logs.{region}.amazonaws.com"}, "Action": ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey"], "Resource": "*", "Condition": {"ArnEquals": {"kms:EncryptionContext:aws:logs:arn": sub("arn:${AWS::Partition}:logs:${AWS::Region}:${AWS::AccountId}:log-group:" + prefix)}}}, {"Effect": "Allow", "Principal": {"Service": "cloudwatch.amazonaws.com"}, "Action": ["kms:Decrypt", "kms:GenerateDataKey*"], "Resource": "*", "Condition": {"StringEquals": {"aws:SourceAccount": account}, "ArnLike": {"aws:SourceArn": f"arn:aws:cloudwatch:{region}:{account}:alarm:*"}}}]
        retained(name, "AWS::KMS::Key", {"EnableKeyRotation": True, "Description": prefix + " " + name, "KeyPolicy": {"Version": "2012-10-17", "Statement": statements}, "Tags": tags})
    retained("CaptureSigningKey", "AWS::KMS::Key", {"KeySpec": "ECC_NIST_P256", "KeyUsage": "SIGN_VERIFY", "EnableKeyRotation": False, "Description": prefix + " capture signing", "KeyPolicy": {"Version": "2012-10-17", "Statement": [root_key_statement]}, "Tags": tags})
    retained("RuntimeSecret", "AWS::SecretsManager::Secret", {"Name": prefix + "-runtime", "KmsKeyId": att("DataKey", "Arn"), "GenerateSecretString": {"SecretStringTemplate": "{}", "GenerateStringKey": "seed", "PasswordLength": 64, "ExcludePunctuation": True, "ExcludeUppercase": True, "ExcludeCharacters": "ghijklmnopqrstuvwxyz", "RequireEachIncludedType": False}, "Tags": tags})
    resource("ApplicationLogs", "AWS::Logs::LogGroup", {"LogGroupName": prefix, "RetentionInDays": 7, "KmsKeyId": att("DataKey", "Arn"), "Tags": tags}, DeletionPolicy="Retain", UpdateReplacePolicy="Retain")

    for name, suffix, key in [("Artifacts", "artifacts", "DataKey"), ("Exports", "exports", "DataKey"), ("DeletionJournal", "journal", "JournalKey"), ("WebAssets", "web", None), ("DeploymentAssets", "deployment", None)]:
        properties = {"BucketName": f"{prefix}-{account}-{region}-{suffix}", "VersioningConfiguration": {"Status": "Enabled"}, "PublicAccessBlockConfiguration": {"BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True}, "OwnershipControls": {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}, "BucketEncryption": {"ServerSideEncryptionConfiguration": [{"BucketKeyEnabled": True, "ServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": att(key, "Arn")}}] if key else [{"ServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}, "Tags": tags}
        if name == "DeletionJournal":
            properties["ObjectLockEnabled"] = True
            properties["ObjectLockConfiguration"] = {"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Days": 90}}}
        if name == "Exports":
            properties["LifecycleConfiguration"] = {"Rules": [{"Id": "ExpiredExports", "Status": "Enabled", "ExpirationInDays": 2, "NoncurrentVersionExpiration": {"NoncurrentDays": 1}, "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}}]}
        if name == "DeploymentAssets":
            properties["LifecycleConfiguration"] = {"Rules": [{"Id": "BoundedDatabaseBackups", "Status": "Enabled", "Prefix": "backups/" + prefix + "/", "ExpirationInDays": 7, "NoncurrentVersionExpiration": {"NoncurrentDays": 7}, "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}}]}
        retained(name, "AWS::S3::Bucket", properties)
    for name, retention in [("DeadLetterQueue", 1209600), ("JobsQueue", 345600)]:
        properties = {"VisibilityTimeout": 120, "MessageRetentionPeriod": retention, "KmsMasterKeyId": att("DataKey", "Arn"), "Tags": tags}
        if name == "JobsQueue":
            properties.update(ReceiveMessageWaitTimeSeconds=20, RedrivePolicy={"deadLetterTargetArn": att("DeadLetterQueue", "Arn"), "maxReceiveCount": 5})
        resource(name, "AWS::SQS::Queue", properties)
    resource("QueueTransportPolicy", "AWS::SQS::QueuePolicy", {"Queues": [ref("JobsQueue"), ref("DeadLetterQueue")], "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Deny", "Principal": "*", "Action": "sqs:*", "Resource": [att("JobsQueue", "Arn"), att("DeadLetterQueue", "Arn")], "Condition": {"Bool": {"aws:SecureTransport": "false"}}}]}})
    retained("Accounts", "AWS::Cognito::UserPool", {"UserPoolName": prefix, "UserPoolTier": "LITE", "UsernameAttributes": ["email"], "AutoVerifiedAttributes": ["email"], "AccountRecoverySetting": {"RecoveryMechanisms": [{"Name": "verified_email", "Priority": 1}]}, "Policies": {"PasswordPolicy": {"MinimumLength": 12, "RequireLowercase": True, "RequireUppercase": True, "RequireNumbers": True, "RequireSymbols": True}}, "MfaConfiguration": "OPTIONAL", "EnabledMfas": ["SOFTWARE_TOKEN_MFA"], "DeletionProtection": "ACTIVE", "UserPoolTags": {tag["Key"]: tag["Value"] for tag in tags}})
    domain_prefix = prefix + "-" + account
    resource("HostedSignIn", "AWS::Cognito::UserPoolDomain", {"Domain": domain_prefix, "UserPoolId": ref("Accounts")})

    bucket_objects = [sub("${Arn}/*", {"Arn": att(name, "Arn")}) for name in ["Artifacts", "Exports"]]
    journal_objects = sub("${Arn}/*", {"Arn": att("DeletionJournal", "Arn")})
    policy_statements = [
        {"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectTagging", "s3:GetObjectVersionTagging", "s3:PutObject", "s3:PutObjectTagging", "s3:PutObjectVersionTagging", "s3:DeleteObject", "s3:DeleteObjectVersion", "s3:AbortMultipartUpload"], "Resource": bucket_objects},
        {"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectRetention", "s3:PutObject"], "Resource": journal_objects},
        {"Effect": "Allow", "Action": ["s3:ListBucket", "s3:ListBucketVersions", "s3:GetBucketLocation", "s3:GetBucketVersioning", "s3:GetBucketObjectLockConfiguration"], "Resource": [att(name, "Arn") for name in ["Artifacts", "Exports", "DeletionJournal", "DeploymentAssets"]]},
        {"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion"], "Resource": [sub("${Arn}/releases/*", {"Arn": att("DeploymentAssets", "Arn")}), sub("${Arn}/runtime/*", {"Arn": att("DeploymentAssets", "Arn")})]},
        {"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": sub("${Arn}/backups/" + prefix + "/*", {"Arn": att("DeploymentAssets", "Arn")})},
        {"Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"], "Resource": ref("RuntimeSecret")},
        {"Effect": "Allow", "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"], "Resource": [att("DataKey", "Arn"), att("JournalKey", "Arn")]},
        {"Effect": "Allow", "Action": ["kms:Sign", "kms:GetPublicKey"], "Resource": att("CaptureSigningKey", "Arn")},
        {"Effect": "Allow", "Action": ["sqs:SendMessage", "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:ChangeMessageVisibility", "sqs:GetQueueAttributes", "sqs:GetQueueUrl"], "Resource": [att("JobsQueue", "Arn"), att("DeadLetterQueue", "Arn")]},
        {"Effect": "Allow", "Action": ["cognito-idp:AdminDeleteUser", "cognito-idp:AdminUserGlobalSignOut"], "Resource": att("Accounts", "Arn")},
        {"Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"], "Resource": sub("arn:${AWS::Partition}:logs:${AWS::Region}:${AWS::AccountId}:log-group:" + prefix + ":*")},
        {"Effect": "Allow", "Action": ["cloudwatch:PutMetricData"], "Resource": "*", "Condition": {"StringEquals": {"cloudwatch:namespace": ["OTGD/qa", "OTGD/development"]}}},
        {"Effect": "Allow", "Action": ["cloudwatch:GetMetricStatistics"], "Resource": "*"},
    ]
    assume_ec2 = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}
    ssm_core = sub("arn:${AWS::Partition}:iam::aws:policy/AmazonSSMManagedInstanceCore")
    resource("AppRole", "AWS::IAM::Role", {"AssumeRolePolicyDocument": assume_ec2, "ManagedPolicyArns": [ssm_core], "Policies": [{"PolicyName": "SingleHostDevelopmentRuntime", "PolicyDocument": {"Version": "2012-10-17", "Statement": policy_statements}}], "Tags": tags})
    resource("NatRole", "AWS::IAM::Role", {"AssumeRolePolicyDocument": assume_ec2, "ManagedPolicyArns": [ssm_core], "Tags": tags})
    for name in ["App", "Nat"]:
        resource(name + "Profile", "AWS::IAM::InstanceProfile", {"Roles": [ref(name + "Role")]})
    for duty in ["submitter", "reviewer", "releaser"]:
        name = "Registry" + duty.title()
        statements = [{"Effect": "Allow", "Action": "iam:GetRole", "Resource": [f"arn:aws:iam::{account}:role/otgd-qa-registry-{value}" for value in ["submitter", "reviewer", "releaser"]]}]
        if duty == "releaser":
            statements += [{"Effect": "Allow", "Action": "s3:PutObject", "Resource": sub("${Arn}/scope-resumptions/*", {"Arn": att("DeletionJournal", "Arn")})}, {"Effect": "Allow", "Action": ["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectRetention"], "Resource": journal_objects}, {"Effect": "Allow", "Action": ["s3:ListBucket", "s3:ListBucketVersions", "s3:GetBucketVersioning", "s3:GetBucketObjectLockConfiguration"], "Resource": att("DeletionJournal", "Arn")}, {"Effect": "Allow", "Action": ["kms:GenerateDataKey", "kms:Encrypt", "kms:Decrypt"], "Resource": att("JournalKey", "Arn")}]
        resource(name, "AWS::IAM::Role", {"RoleName": "otgd-qa-registry-" + duty, "MaxSessionDuration": 3600, "AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{account}:root"}, "Action": "sts:AssumeRole", "Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}}]}, "Policies": [{"PolicyName": "IndependentRegistryOperator", "PolicyDocument": {"Version": "2012-10-17", "Statement": statements}}], "Tags": tags})
    for name in ["Artifacts", "Exports", "DeletionJournal", "DeploymentAssets"]:
        statements = [{"Effect": "Deny", "Principal": "*", "Action": "s3:*", "Resource": [att(name, "Arn"), sub("${Arn}/*", {"Arn": att(name, "Arn")})], "Condition": {"Bool": {"aws:SecureTransport": "false"}}}]
        if name == "DeletionJournal":
            statements += [{"Effect": "Deny", "Principal": {"AWS": att("AppRole", "Arn")}, "Action": ["s3:DeleteObject", "s3:DeleteObjectVersion"], "Resource": journal_objects}, {"Effect": "Deny", "Principal": {"AWS": att("AppRole", "Arn")}, "Action": "s3:PutObject", "Resource": sub("${Arn}/scope-resumptions/*", {"Arn": att(name, "Arn")})}, {"Effect": "Deny", "Principal": {"AWS": att("AppRole", "Arn")}, "Action": "s3:PutObject", "Resource": journal_objects, "Condition": {"Null": {"s3:if-none-match": "true"}}}, {"Effect": "Deny", "Principal": {"AWS": att("AppRole", "Arn")}, "Action": "s3:PutObject", "Resource": journal_objects, "Condition": {"StringNotEquals": {"s3:if-none-match": "*"}}}]
        resource(name + "Policy", "AWS::S3::BucketPolicy", {"Bucket": ref(name), "PolicyDocument": {"Version": "2012-10-17", "Statement": statements}})

    nat_boot = """#!/bin/bash
set -euo pipefail
for attempt in $(seq 1 30); do
  if dnf install -y iptables-services; then break; fi
  sleep 10
done
command -v iptables
printf 'net.ipv4.ip_forward=1\\n' >/etc/sysctl.d/70-otgd-nat.conf
sysctl --system
DEVICE=$(ip -4 route show default | awk 'NR==1 {print $5}')
test -n "$DEVICE"
iptables -t nat -A POSTROUTING -o "$DEVICE" -j MASQUERADE
iptables -A FORWARD -i "$DEVICE" -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -s 10.74.1.0/24 -p tcp -m multiport --dports 80,443 -j ACCEPT
iptables-save >/etc/sysconfig/iptables
systemctl enable iptables
systemctl enable --now amazon-ssm-agent
"""
    resource("NatInstance", "AWS::EC2::Instance", {"InstanceType": "t4g.nano", "Monitoring": False, "ImageId": "{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64}}", "IamInstanceProfile": ref("NatProfile"), "SourceDestCheck": False, "CreditSpecification": {"CPUCredits": "standard"}, "MetadataOptions": {"HttpTokens": "required", "HttpEndpoint": "enabled", "HttpPutResponseHopLimit": 1}, "NetworkInterfaces": [{"DeviceIndex": "0", "AssociatePublicIpAddress": False, "DeleteOnTermination": True, "SubnetId": ref("PublicSubnet"), "GroupSet": [ref("NatSecurityGroup")]}], "BlockDeviceMappings": [{"DeviceName": "/dev/xvda", "Ebs": {"VolumeSize": 8, "VolumeType": "gp3", "Encrypted": True, "DeleteOnTermination": True}}], "UserData": {"Fn::Base64": nat_boot}, "Tags": tags}, DependsOn="PublicInternetRoute")
    resource("NatAddress", "AWS::EC2::EIP", {"Domain": "vpc", "Tags": tags}, DependsOn="InternetAttachment")
    resource("NatAddressAssociation", "AWS::EC2::EIPAssociation", {"InstanceId": ref("NatInstance"), "AllocationId": att("NatAddress", "AllocationId")})
    resource("PrivateInternetRoute", "AWS::EC2::Route", {"RouteTableId": ref("PrivateSubnetRoutes"), "DestinationCidrBlock": "0.0.0.0/0", "InstanceId": ref("NatInstance")}, DependsOn="NatAddressAssociation")
    app_boot = """#!/bin/bash
set -euo pipefail
for attempt in $(seq 1 30); do
  if dnf install -y docker awscli-2 python3 openssl; then break; fi
  sleep 10
done
command -v docker
systemctl enable --now docker amazon-ssm-agent
"""
    resource("AppInstance", "AWS::EC2::Instance", {"InstanceType": "t3a.medium", "Monitoring": False, "ImageId": "{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64}}", "IamInstanceProfile": ref("AppProfile"), "CreditSpecification": {"CPUCredits": "standard"}, "MetadataOptions": {"HttpTokens": "required", "HttpEndpoint": "enabled", "HttpPutResponseHopLimit": 2}, "NetworkInterfaces": [{"DeviceIndex": "0", "AssociatePublicIpAddress": False, "DeleteOnTermination": True, "SubnetId": ref("PrivateSubnet"), "GroupSet": [ref("AppSecurityGroup")]}], "BlockDeviceMappings": [{"DeviceName": "/dev/xvda", "Ebs": {"VolumeSize": 30, "VolumeType": "gp3", "Encrypted": True, "KmsKeyId": att("DataKey", "Arn"), "DeleteOnTermination": False}}], "UserData": {"Fn::Base64": app_boot}, "Tags": tags}, DependsOn="PrivateInternetRoute")
    resource("ApiVpcOrigin", "AWS::CloudFront::VpcOrigin", {"VpcOriginEndpointConfig": {"Name": prefix + "-api", "Arn": sub("arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:instance/${AppInstance}"), "HTTPPort": 8000, "HTTPSPort": 443, "OriginProtocolPolicy": "http-only"}, "Tags": tags})
    resource("ApiHeaders", "AWS::CloudFront::ResponseHeadersPolicy", {"ResponseHeadersPolicyConfig": {"Name": prefix + "-api-headers", "SecurityHeadersConfig": {"ContentTypeOptions": {"Override": True}, "FrameOptions": {"FrameOption": "DENY", "Override": True}, "ReferrerPolicy": {"ReferrerPolicy": "no-referrer", "Override": True}, "StrictTransportSecurity": {"AccessControlMaxAgeSec": 31536000, "IncludeSubdomains": True, "Override": True}}, "CustomHeadersConfig": {"Items": [{"Header": "Cache-Control", "Value": "private, no-store", "Override": True}]}}})
    resource("ApiDelivery", "AWS::CloudFront::Distribution", {"DistributionConfig": {"Enabled": True, "HttpVersion": "http2", "IPV6Enabled": True, "PriceClass": "PriceClass_100", "ViewerCertificate": {"CloudFrontDefaultCertificate": True}, "Origins": [{"Id": "api", "DomainName": att("AppInstance", "PrivateDnsName"), "VpcOriginConfig": {"VpcOriginId": att("ApiVpcOrigin", "Id"), "OriginReadTimeout": 60, "OriginKeepaliveTimeout": 5}}], "DefaultCacheBehavior": {"TargetOriginId": "api", "ViewerProtocolPolicy": "redirect-to-https", "AllowedMethods": ["GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"], "CachedMethods": ["GET", "HEAD"], "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", "OriginRequestPolicyId": "b689b0a8-53d0-40ab-baf2-68738e2966ac", "ResponseHeadersPolicyId": ref("ApiHeaders"), "Compress": False}}, "Tags": tags})
    resource("WebOriginAccess", "AWS::CloudFront::OriginAccessControl", {"OriginAccessControlConfig": {"Name": prefix + "-web", "OriginAccessControlOriginType": "s3", "SigningBehavior": "always", "SigningProtocol": "sigv4"}})
    resource("WebNavigation", "AWS::CloudFront::Function", {"Name": prefix + "-navigation", "AutoPublish": True, "FunctionConfig": {"Comment": "Extensionless web navigation only", "Runtime": "cloudfront-js-2.0"}, "FunctionCode": "function handler(event) { var request = event.request; if ((request.method === 'GET' || request.method === 'HEAD') && /^\\/[a-zA-Z0-9_\\/-]*$/.test(request.uri)) request.uri = '/index.html'; return request; }"})
    csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://${ApiDelivery.DomainName} https://" + domain_prefix + ".auth." + region + ".amazoncognito.com https://cognito-idp." + region + ".amazonaws.com; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    resource("WebHeaders", "AWS::CloudFront::ResponseHeadersPolicy", {"ResponseHeadersPolicyConfig": {"Name": prefix + "-web-headers", "SecurityHeadersConfig": {"ContentTypeOptions": {"Override": True}, "FrameOptions": {"FrameOption": "DENY", "Override": True}, "ReferrerPolicy": {"ReferrerPolicy": "no-referrer", "Override": True}, "StrictTransportSecurity": {"AccessControlMaxAgeSec": 31536000, "IncludeSubdomains": True, "Override": True}, "ContentSecurityPolicy": {"ContentSecurityPolicy": sub(csp), "Override": True}}, "CustomHeadersConfig": {"Items": [{"Header": "Permissions-Policy", "Value": "camera=(self), microphone=(), geolocation=()", "Override": True}]}}})
    resource("WebDelivery", "AWS::CloudFront::Distribution", {"DistributionConfig": {"Enabled": True, "DefaultRootObject": "index.html", "HttpVersion": "http2", "IPV6Enabled": True, "PriceClass": "PriceClass_100", "ViewerCertificate": {"CloudFrontDefaultCertificate": True}, "Origins": [{"Id": "web", "DomainName": att("WebAssets", "RegionalDomainName"), "OriginPath": "/releases/" + revision, "OriginAccessControlId": ref("WebOriginAccess"), "S3OriginConfig": {"OriginAccessIdentity": ""}}], "DefaultCacheBehavior": {"TargetOriginId": "web", "ViewerProtocolPolicy": "redirect-to-https", "AllowedMethods": ["GET", "HEAD", "OPTIONS"], "CachedMethods": ["GET", "HEAD"], "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", "ResponseHeadersPolicyId": ref("WebHeaders"), "Compress": True, "FunctionAssociations": [{"EventType": "viewer-request", "FunctionARN": att("WebNavigation", "FunctionARN")}] }}, "Tags": tags})
    resource("WebAssetsPolicy", "AWS::S3::BucketPolicy", {"Bucket": ref("WebAssets"), "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Deny", "Principal": "*", "Action": "s3:*", "Resource": [att("WebAssets", "Arn"), sub("${Arn}/*", {"Arn": att("WebAssets", "Arn")})], "Condition": {"Bool": {"aws:SecureTransport": "false"}}}, {"Effect": "Allow", "Principal": {"Service": "cloudfront.amazonaws.com"}, "Action": "s3:GetObject", "Resource": sub("${Arn}/*", {"Arn": att("WebAssets", "Arn")}), "Condition": {"StringEquals": {"AWS:SourceArn": sub("arn:${AWS::Partition}:cloudfront::${AWS::AccountId}:distribution/${WebDelivery}")}}}]}})
    resource("MobileClient", "AWS::Cognito::UserPoolClient", {"UserPoolId": ref("Accounts"), "GenerateSecret": False, "EnableTokenRevocation": True, "PreventUserExistenceErrors": "ENABLED", "ExplicitAuthFlows": ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"], "AllowedOAuthFlowsUserPoolClient": True, "AllowedOAuthFlows": ["code"], "AllowedOAuthScopes": ["openid", "email", "profile"], "SupportedIdentityProviders": ["COGNITO"], "CallbackURLs": ["otgd-qa://oauth/callback", sub("https://${WebDelivery.DomainName}/")], "LogoutURLs": ["otgd-qa://oauth/callback", sub("https://${WebDelivery.DomainName}/")], "AccessTokenValidity": 15, "IdTokenValidity": 15, "RefreshTokenValidity": 30, "TokenValidityUnits": {"AccessToken": "minutes", "IdToken": "minutes", "RefreshToken": "days"}})

    resource("Notifications", "AWS::SNS::Topic", {"KmsMasterKeyId": att("DataKey", "Arn"), "Subscription": [{"Protocol": "email", "Endpoint": email}], "Tags": tags})
    resource("NotificationPolicy", "AWS::SNS::TopicPolicy", {"Topics": [ref("Notifications")], "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "cloudwatch.amazonaws.com"}, "Action": "sns:Publish", "Resource": ref("Notifications"), "Condition": {"StringEquals": {"aws:SourceAccount": account}, "ArnLike": {"aws:SourceArn": f"arn:aws:cloudwatch:{region}:{account}:alarm:*"}}}]}})
    alarm_ids = []
    for name, metric, namespace, threshold in [("DeadLetters", "ApproximateNumberOfMessagesVisible", "AWS/SQS", 1), ("OldSourceMessage", "ApproximateAgeOfOldestMessage", "AWS/SQS", 300), ("OldOutbox", "OldestOutboxSeconds", "OTGD/qa", 120), ("OldPrivacyJob", "OldestPrivacyJobSeconds", "OTGD/qa", 900), ("OverdueCleanup", "CleanupOverdueCount", "OTGD/qa", 1), ("InstanceHealth", "StatusCheckFailed", "AWS/EC2", 1), ("NatInstanceHealth", "StatusCheckFailed", "AWS/EC2", 1), ("HostMemoryPressure", "MemoryUsedPercent", "OTGD/development", 90), ("HostDiskPressure", "DiskUsedPercent", "OTGD/development", 85)]:
        properties = {"AlarmName": prefix + "-" + name, "Namespace": namespace, "MetricName": metric, "Statistic": "Maximum", "Period": 60, "EvaluationPeriods": 2, "Threshold": threshold, "ComparisonOperator": "GreaterThanOrEqualToThreshold", "TreatMissingData": "notBreaching", "AlarmActions": [ref("Notifications")]}
        if namespace == "AWS/SQS":
            properties["Dimensions"] = [{"Name": "QueueName", "Value": att("DeadLetterQueue" if name == "DeadLetters" else "JobsQueue", "QueueName")}]
        if namespace == "AWS/EC2":
            properties["Dimensions"] = [{"Name": "InstanceId", "Value": ref("NatInstance" if name == "NatInstanceHealth" else "AppInstance")}]
        if namespace == "OTGD/development":
            properties.update(Period=300, Dimensions=[{"Name": "InstanceId", "Value": ref("AppInstance")}])
        resource(name, "AWS::CloudWatch::Alarm", properties)
        alarm_ids.append(name)
    resource("MissingWorkerMetrics", "AWS::CloudWatch::Alarm", {"AlarmName": prefix + "-MissingWorkerMetrics", "AlarmDescription": "No aggregate worker publication for five minutes, including idle zero values; inspect app host, worker progress and database", "Namespace": "OTGD/qa", "MetricName": "OldestOutboxSeconds", "Statistic": "Maximum", "Period": 60, "EvaluationPeriods": 5, "Threshold": 0, "ComparisonOperator": "LessThanThreshold", "TreatMissingData": "breaching", "AlarmActions": [ref("Notifications")]})
    alarm_ids.append("MissingWorkerMetrics")
    widgets = [{"type": "text", "width": 24, "height": 3, "x": 0, "y": 0, "properties": {"markdown": "# Single-host development health\nPrivate EC2 API/worker/PostgreSQL, real AWS services, CloudFront HTTPS. This is not managed QA availability. Aggregate runtime metrics use OTGD/qa; do not operate another QA deployment in this account/region concurrently. Empty graphs do not establish health. Confirm the SNS email subscription."}}, {"type": "alarm", "width": 24, "height": 3, "x": 0, "y": 3, "properties": {"title": "Development alarms", "alarms": [att(name, "Arn") for name in alarm_ids]}}]
    graphs = [
        ("Host CPU and status", [["AWS/EC2", "CPUUtilization", "InstanceId", ref("AppInstance")], ["AWS/EC2", "StatusCheckFailed", "InstanceId", ref("AppInstance")], ["AWS/EC2", "StatusCheckFailed", "InstanceId", ref("NatInstance")]]),
        ("Queues and dead letters", [["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", att("JobsQueue", "QueueName")], ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", att("DeadLetterQueue", "QueueName")], ["AWS/SQS", "ApproximateNumberOfMessagesNotVisible", "QueueName", att("JobsQueue", "QueueName")]]),
        ("Outbox and privacy job age (seconds)", [["OTGD/qa", "OldestOutboxSeconds"], ["OTGD/qa", "OldestPrivacyJobSeconds"], ["AWS/SQS", "ApproximateAgeOfOldestMessage", "QueueName", att("JobsQueue", "QueueName")]]),
        ("Overdue cleanup count", [["OTGD/qa", "CleanupOverdueCount"]]),
        ("Host memory and disk usage %", [["OTGD/development", "MemoryUsedPercent", "InstanceId", ref("AppInstance")], ["OTGD/development", "DiskUsedPercent", "InstanceId", ref("AppInstance")]]),
        ("API requests and errors", [["AWS/CloudFront", metric, "DistributionId", ref("ApiDelivery"), "Region", "Global", {"stat": "Sum" if metric == "Requests" else "Average"}] for metric in ["Requests", "5xxErrorRate", "4xxErrorRate"]]),
        ("Web requests and errors", [["AWS/CloudFront", metric, "DistributionId", ref("WebDelivery"), "Region", "Global", {"stat": "Sum" if metric == "Requests" else "Average"}] for metric in ["Requests", "5xxErrorRate", "4xxErrorRate"]]),
    ]
    for index, (title, metrics) in enumerate(graphs):
        widgets.append({"type": "metric", "width": 12, "height": 6, "x": 12 * (index % 2), "y": 6 + 6 * (index // 2), "properties": {"title": title, "view": "timeSeries", "region": "us-east-1" if index >= 5 else region, "stat": "Maximum", "period": 300 if index == 4 else 60, "metrics": metrics}})
    # DashboardBody is a CloudFormation string. Replace JSON intrinsic objects
    # with Fn::Sub tokens, keeping tokens quoted in the embedded dashboard JSON.
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
    resource("HealthDashboard", "AWS::CloudWatch::Dashboard", {"DashboardName": prefix + "-health", "DashboardBody": sub(body, bindings)})
    resource("MonthlyBudget", "AWS::Budgets::Budget", {"Budget": {"BudgetName": prefix + "-monthly", "BudgetType": "COST", "TimeUnit": "MONTHLY", "BudgetLimit": {"Amount": budget, "Unit": "USD"}}, "NotificationsWithSubscribers": [{"Notification": {"ComparisonOperator": "GREATER_THAN", "NotificationType": kind, "Threshold": threshold, "ThresholdType": "PERCENTAGE"}, "Subscribers": [{"Address": email, "SubscriptionType": "EMAIL"}]} for kind, threshold in [("ACTUAL", 50), ("ACTUAL", 80), ("ACTUAL", 100), ("FORECASTED", 100)]]})
    values = {
        "ApiOrigin": sub("https://${ApiDelivery.DomainName}"), "WebOrigin": sub("https://${WebDelivery.DomainName}"),
        "WebCallbackUri": sub("https://${WebDelivery.DomainName}/"), "WebBucket": ref("WebAssets"),
        "WebDistributionId": ref("WebDelivery"), "WebDistributionDomain": att("WebDelivery", "DomainName"),
        "WebReleasePrefix": "releases/" + revision, "ApiDistributionId": ref("ApiDelivery"),
        "ApiVpcOriginId": att("ApiVpcOrigin", "Id"), "InstanceId": ref("AppInstance"), "NatInstanceId": ref("NatInstance"),
        "EC2PrimaryPrivateIp": att("AppInstance", "PrivateIp"), "AppSecurityGroup": ref("AppSecurityGroup"), "ApplicationSecurityGroupId": ref("AppSecurityGroup"), "VpcId": ref("Network"),
        "DeploymentBucket": ref("DeploymentAssets"), "RuntimeSecretArn": ref("RuntimeSecret"),
        "ArtifactBucket": ref("Artifacts"), "ExportBucket": ref("Exports"), "JournalBucket": ref("DeletionJournal"),
        "QueueUrl": ref("JobsQueue"), "DeadLetterQueueUrl": ref("DeadLetterQueue"),
        "Issuer": sub("https://cognito-idp.${AWS::Region}.amazonaws.com/${Accounts}"), "ClientId": ref("MobileClient"),
        "IdentityOrigin": f"https://{domain_prefix}.auth.{region}.amazoncognito.com", "UserPoolId": ref("Accounts"),
        "DataKeyArn": att("DataKey", "Arn"), "JournalKeyArn": att("JournalKey", "Arn"),
        "CaptureSigningKeyArn": att("CaptureSigningKey", "Arn"), "CloudWatchDashboardName": prefix + "-health",
        "CloudWatchDashboardUrl": f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#dashboards/dashboard/{prefix}-health",
        "LogGroup": ref("ApplicationLogs"), "ReleaseId": revision,
    }
    for duty in ["Submitter", "Reviewer", "Releaser"]:
        values["Registry" + duty] = att("Registry" + duty, "Arn")
    return {"AWSTemplateFormatVersion": "2010-09-09", "Description": "On-The-Go Detection single-host development; independent AWS journal; AWS-generated HTTPS hosts; no managed-QA availability claim", "Resources": resources, "Outputs": {key: {"Value": value} for key, value in values.items()}}
