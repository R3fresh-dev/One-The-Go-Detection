"""Side-effect-free Fargate development infrastructure with retained authority.

The original serverless builder supplies the independently reviewed data,
identity and immutable-journal resources. Their logical IDs, names, properties
and tags remain unchanged so recovery can import the existing resources.
Only execution, ingress and monitoring change to ECS Fargate.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
import re

from deploy.serverless_template import att, build_template as original_template, ref, sub

PREFIX = "otgd-serverless-development"
NAMESPACE = "OTGD/serverless-development"
RETAINED_AUTHORITY = frozenset({
    "Accounts", "ApiLogs", "ApplicationSecret", "CaptureSigningKey", "ControlLogs",
    "DataKey", "DeletionJournal", "DispatcherLogs", "Exports", "JournalKey",
    "MaintenanceLogs", "RuntimeControl", "TombstoneSecret", "WebAssets", "WorkerLogs",
})


def _configuration(config, phase):
    if config.get("environment") != "fargate-development" or config.get("prefix", PREFIX) != PREFIX:
        raise ValueError("Fargate development must preserve the owned initial resource prefix")
    budget = config.get("monthlyBudgetUsd")
    if (isinstance(budget, bool) or not isinstance(budget, (int, float))
            or not math.isfinite(budget) or not 0 < budget <= 100):
        raise ValueError("The approved Fargate development budget is at most USD 100")
    if phase not in ("registry", "platform"):
        raise ValueError("Unknown Fargate deployment phase")
    account, region = config.get("account", ""), config.get("region", "")
    if not re.fullmatch(r"[0-9]{12}", account) or region != "us-east-2":
        raise ValueError("Fargate development requires its actual Ohio account")
    if not re.fullmatch(r"[0-9a-f]{40}", config.get("releaseId", "")):
        raise ValueError("Fargate deployment requires an immutable full source SHA")
    if phase == "platform":
        if not re.fullmatch(r"pl-[0-9a-f]{8,17}", config.get("cloudFrontPrefixListId", "")):
            raise ValueError("Set the actual regional CloudFront origin-facing managed prefix list")
        for key in ("apiImageUri", "workerImageUri", "uiImageUri"):
            expected = re.escape(f"{account}.dkr.ecr.{region}.amazonaws.com/{PREFIX}@sha256:")
            if not re.fullmatch(expected + r"[0-9a-f]{64}", config.get(key, "")):
                raise ValueError(f"{key} must identify an owned immutable image digest")


def _dualstack_image(uri):
    return uri.replace(".dkr.ecr.us-east-2.amazonaws.com/", ".dkr-ecr.us-east-2.on.aws/")


def build_template(config, phase="platform"):
    """Build registry, stopped platform, or admitted active platform resources."""
    _configuration(config, phase)
    # This is construction reuse, not the cost admission result: the Fargate
    # CLI independently admits the actual approved budget and workload model.
    base = original_template({**config, "monthlyBudgetUsd": min(config["monthlyBudgetUsd"], 50)}, phase)
    base["Description"] = "On-The-Go Detection ECS Fargate development deployment"
    if phase == "registry":
        base["Resources"]["Images"]["Properties"].pop("RepositoryPolicyText", None)
        return base

    resources = base["Resources"]
    outputs = base["Outputs"]
    account, region, revision = config["account"], config["region"], config["releaseId"]
    active = config.get("activateServices", False)
    tags = deepcopy(resources["Network"]["Properties"]["Tags"])
    original_common = deepcopy(resources["ApiFunction"]["Properties"]["Environment"]["Variables"])

    def resource(name, kind, properties, **options):
        resources[name] = {"Type": kind, "Properties": properties, **options}

    def output(name, value):
        outputs[name] = {"Value": value}

    for name in list(resources):
        kind = resources[name]["Type"]
        if (kind.startswith("AWS::Lambda::") or kind.startswith("AWS::ApiGateway")
                or kind == "AWS::CloudFront::Function" or kind == "AWS::CloudWatch::Alarm"
                or name in {"ControlSchedule", "ControlRole", "DatabaseEgress",
                            "S3Endpoint", "WebOriginAccess", "HealthDashboard"}):
            del resources[name]
    for name in list(outputs):
        if ("Function" in name or name in {"RestApiId", "WorkerMapping", "ControlSchedule"}):
            del outputs[name]

    # CloudFront VPC origins require an attached IGW, but private origin routes
    # never use it. Tasks use only IPv6 and an egress-only gateway.
    resource("InternetGateway", "AWS::EC2::InternetGateway", {"Tags": tags})
    resource("InternetGatewayAttachment", "AWS::EC2::VPCGatewayAttachment", {
        "VpcId": ref("Network"), "InternetGatewayId": ref("InternetGateway")})
    for index, name in enumerate(("TaskA", "TaskB"), start=2):
        cidr = {"Fn::Select": [index, {"Fn::Cidr": [{"Fn::Select": [0, att("Network", "Ipv6CidrBlocks")]}, 4, 64]}]}
        resource(name, "AWS::EC2::Subnet", {
            "VpcId": ref("Network"), "AvailabilityZone": {"Fn::Select": [index - 2, {"Fn::GetAZs": ""}]},
            "Ipv6Native": True, "Ipv6CidrBlock": cidr, "AssignIpv6AddressOnCreation": True,
            "MapPublicIpOnLaunch": False, "Tags": tags}, DependsOn="NetworkIpv6")
        resource(name + "Routes", "AWS::EC2::RouteTable", {"VpcId": ref("Network"), "Tags": tags})
        resource(name + "Association", "AWS::EC2::SubnetRouteTableAssociation", {
            "SubnetId": ref(name), "RouteTableId": ref(name + "Routes")})
        resource(name + "Ipv6Route", "AWS::EC2::Route", {
            "RouteTableId": ref(name + "Routes"), "DestinationIpv6CidrBlock": "::/0",
            "EgressOnlyInternetGatewayId": ref("Ipv6Egress")})
    resource("IngressSecurityGroup", "AWS::EC2::SecurityGroup", {
        "VpcId": ref("Network"), "GroupDescription": "Private CloudFront VPC origin ingress only",
        "SecurityGroupIngress": [{"IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080,
                                  "SourcePrefixListId": config["cloudFrontPrefixListId"]}],
        "SecurityGroupEgress": [{"IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080,
                                 "CidrIpv6": {"Fn::Select": [0, att("Network", "Ipv6CidrBlocks")]}}], "Tags": tags})
    resource("TaskSecurityGroup", "AWS::EC2::SecurityGroup", {
        "VpcId": ref("Network"), "GroupDescription": "Fargate: private origin ingress and IPv6 HTTPS egress",
        "SecurityGroupIngress": [{"IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080,
                                  "SourceSecurityGroupId": ref("IngressSecurityGroup")}],
        "SecurityGroupEgress": [{"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "CidrIpv6": "::/0"}],
        "Tags": tags})
    # Its description is immutable; update grants without replacing the
    # existing database group. Keep the unused legacy group as a survivor.
    resources["DatabaseSecurityGroup"]["Properties"].update(
        SecurityGroupIngress=[{"IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432,
                               "SourceSecurityGroupId": ref("TaskSecurityGroup")}])
    resource("DatabaseEgress", "AWS::EC2::SecurityGroupEgress", {
        "GroupId": ref("TaskSecurityGroup"), "IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432,
        "DestinationSecurityGroupId": ref("DatabaseSecurityGroup")})
    resources["Database"]["Properties"]["NetworkType"] = "DUAL"

    resource("Cluster", "AWS::ECS::Cluster", {"ClusterName": PREFIX,
        "ClusterSettings": [{"Name": "containerInsights", "Value": "disabled"}], "Tags": tags})
    resource("Ingress", "AWS::ElasticLoadBalancingV2::LoadBalancer", {
        "Name": "otgd-development-ingress", "Type": "application", "Scheme": "internal",
        "IpAddressType": "dualstack", "Subnets": [ref("PrivateA"), ref("PrivateB")],
        "SecurityGroups": [ref("IngressSecurityGroup")], "Tags": tags,
        "LoadBalancerAttributes": [{"Key": "idle_timeout.timeout_seconds", "Value": "900"},
                                   {"Key": "routing.http.drop_invalid_header_fields.enabled", "Value": "true"}]})
    resource("IngressTargets", "AWS::ElasticLoadBalancingV2::TargetGroup", {
        "VpcId": ref("Network"), "TargetType": "ip", "IpAddressType": "ipv6", "Protocol": "HTTP",
        "Port": 8080, "HealthCheckProtocol": "HTTP", "HealthCheckPath": "/health/live",
        "HealthCheckIntervalSeconds": 30, "HealthCheckTimeoutSeconds": 5,
        "HealthyThresholdCount": 2, "UnhealthyThresholdCount": 3, "Matcher": {"HttpCode": "200"},
        "TargetGroupAttributes": [{"Key": "deregistration_delay.timeout_seconds", "Value": "120"}], "Tags": tags})
    resource("IngressListener", "AWS::ElasticLoadBalancingV2::Listener", {
        "LoadBalancerArn": ref("Ingress"), "Protocol": "HTTP", "Port": 8080,
        "DefaultActions": [{"Type": "forward", "TargetGroupArn": ref("IngressTargets")}]})
    resource("VpcOrigin", "AWS::CloudFront::VpcOrigin", {"VpcOriginEndpointConfig": {
        "Name": PREFIX + "-ingress", "Arn": ref("Ingress"), "HTTPPort": 8080,
        "HTTPSPort": 443, "OriginProtocolPolicy": "http-only", "OriginSSLProtocols": ["TLSv1.2"]}},
        DependsOn=["InternetGatewayAttachment", "IngressListener"])
    for name, target, compress in (("ApiDelivery", "api", False), ("WebDelivery", "web", True)):
        delivery = resources[name]["Properties"]["DistributionConfig"]
        delivery.pop("DefaultRootObject", None)
        delivery["Origins"] = [{"Id": target, "DomainName": att("Ingress", "DNSName"),
                                "VpcOriginConfig": {"VpcOriginId": ref("VpcOrigin"),
                                                    "OriginReadTimeout": 60, "OriginKeepaliveTimeout": 5}}]
        behavior = delivery["DefaultCacheBehavior"]
        behavior.update(TargetOriginId=target, Compress=compress,
            AllowedMethods=["GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"],
            CachedMethods=["GET", "HEAD"], OriginRequestPolicyId="b689b0a8-53d0-40ab-baf2-68738e2966ac")
        behavior.pop("FunctionAssociations", None)
    # WebAssets remains a retained release evidence bucket. No public delivery
    # reads it; actual UI bytes are served by the admitted Fargate image.
    resources["WebAssetsPolicy"]["Properties"]["PolicyDocument"]["Statement"] = [
        row for row in resources["WebAssetsPolicy"]["Properties"]["PolicyDocument"]["Statement"]
        if row["Effect"] == "Deny"]

    assume = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow",
        "Principal": {"Service": "ecs-tasks.amazonaws.com"}, "Action": "sts:AssumeRole",
        "Condition": {"StringEquals": {"aws:SourceAccount": account},
                      "ArnLike": {"aws:SourceArn": f"arn:aws:ecs:{region}:{account}:*"}}}]}
    for role in ("Api", "Worker", "Maintenance"):
        props = resources[role + "Role"]["Properties"]
        props["AssumeRolePolicyDocument"] = deepcopy(assume)
        statements = props["Policies"][0]["PolicyDocument"]["Statement"]
        statements[:] = [row for row in statements if not any(
            action.startswith(("lambda:", "ec2:")) for action in row["Action"])]
        props["Policies"][0]["PolicyName"] = "ScopedFargateExecution"
    logs = [sub("${Arn}:*", {"Arn": att(name + "Logs", "Arn")}) for name in
            ("Api", "Worker", "Dispatcher", "Maintenance", "Control")]
    resource("UiLogs", "AWS::Logs::LogGroup", {"LogGroupName": "/" + PREFIX + "/ui",
        "RetentionInDays": 7, "KmsKeyId": att("DataKey", "Arn"), "Tags": tags})
    logs.append(sub("${Arn}:*", {"Arn": att("UiLogs", "Arn")}))
    resource("ExecutionRole", "AWS::IAM::Role", {"AssumeRolePolicyDocument": deepcopy(assume),
        "Policies": [{"PolicyName": "PullOwnedImagesAndWriteOwnedLogs", "PolicyDocument": {
            "Version": "2012-10-17", "Statement": [
                {"Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*"},
                {"Effect": "Allow", "Action": ["ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage"],
                 "Resource": f"arn:aws:ecr:{region}:{account}:repository/{PREFIX}"},
                {"Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"], "Resource": logs},
            ]}}], "Tags": tags})
    api_statements = resources["ApiRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
    api_statements += [
        {"Effect": "Allow", "Action": ["ecs:RunTask"], "Resource": ref("WorkerTaskDefinition"),
         "Condition": {"ArnEquals": {"ecs:cluster": att("Cluster", "Arn")}}},
        {"Effect": "Allow", "Action": ["iam:PassRole"],
         "Resource": [att("WorkerRole", "Arn"), att("ExecutionRole", "Arn")],
         "Condition": {"StringEquals": {"iam:PassedToService": "ecs-tasks.amazonaws.com"}}},
    ]
    deployment_bucket = f"{PREFIX}-{account}-{region}-deployments"
    resources["MaintenanceRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"].append({
        "Effect": "Allow", "Action": ["s3:PutObject"],
        "Resource": f"arn:aws:s3:::{deployment_bucket}/receipts/{revision}/*",
        "Condition": {"StringEquals": {"s3:x-amz-server-side-encryption": "AES256",
                                       "s3:if-none-match": "*"}}})

    task_subnets = sub('["${TaskA}","${TaskB}"]')
    task_groups = sub('["${TaskSecurityGroup}"]')
    for key in list(original_common):
        if key.startswith("AWS_LWA_") or key in {"PORT", "OTGD_SERVERLESS_DISPATCH_FUNCTION_ARN"}:
            original_common.pop(key)
    original_common.update(OTGD_SERVERLESS_EXECUTOR="ecs", OTGD_ECS_CLUSTER_ARN=att("Cluster", "Arn"),
                          OTGD_ECS_SUBNET_IDS=task_subnets, OTGD_ECS_SECURITY_GROUP_IDS=task_groups)
    original_common["OTGD_CAPTURE_SIGNING_KEY_ID"] = att("CaptureSigningKey", "Arn")

    def container(name, image, command, environment, group, *, port=None):
        value = {"Name": name, "Image": _dualstack_image(image), "Essential": True,
            "User": "10001", "ReadonlyRootFilesystem": True, "Command": command,
            "Environment": [{"Name": key, "Value": value} for key, value in sorted(environment.items())],
            "LogConfiguration": {"LogDriver": "awslogs", "Options": {"awslogs-group": ref(group),
                "awslogs-region": region, "awslogs-stream-prefix": name}},
            "StopTimeout": 120, "LinuxParameters": {"InitProcessEnabled": True},
            "MountPoints": [{"ContainerPath": "/tmp", "SourceVolume": name + "-scratch", "ReadOnly": False}]}
        if port is not None:
            value["PortMappings"] = [{"ContainerPort": port, "Protocol": "tcp"}]
        return value

    def task(name, family, cpu, memory, role, containers):
        resource(name, "AWS::ECS::TaskDefinition", {"Family": PREFIX + "-" + family,
            "Cpu": str(cpu), "Memory": str(memory), "NetworkMode": "awsvpc",
            "RequiresCompatibilities": ["FARGATE"], "RuntimePlatform": {
                "OperatingSystemFamily": "LINUX", "CpuArchitecture": "X86_64"},
            "ExecutionRoleArn": att("ExecutionRole", "Arn"), "TaskRoleArn": att(role + "Role", "Arn"),
            "ContainerDefinitions": containers,
            "Volumes": [{"Name": row["Name"] + "-scratch"} for row in containers], "Tags": tags})

    uv = ["/usr/local/bin/uv", "run", "--no-sync"]
    worker_env = {**original_common, "OTGD_DATABASE_POOL_SIZE": "1"}
    task("WorkerTaskDefinition", "worker", 512, 2048, "Worker", [container("worker",
        config["workerImageUri"], uv + ["python", "-m", "otgd.fargate_runtime", "worker"], worker_env, "WorkerLogs")])
    admin_env = {**original_common, "OTGD_DATABASE_USER": "otgd_migrator",
        "OTGD_APP_DATABASE_USER": "otgd_app", "OTGD_APP_DATABASE_SECRET_ARN": ref("ApplicationSecret"),
        "OTGD_DATABASE_SECRET_ARN": att("Database", "MasterUserSecret.SecretArn"), "OTGD_DATABASE_POOL_SIZE": "1"}
    task("MaintenanceTaskDefinition", "maintenance", 512, 1024, "Maintenance", [container("maintenance",
        config["workerImageUri"], uv + ["python", "-m", "otgd.fargate_runtime", "maintenance"], admin_env, "MaintenanceLogs")])
    api_env = {**original_common, "OTGD_DATABASE_POOL_SIZE": "1",
               "OTGD_ECS_WORKER_TASK_DEFINITION_ARN": ref("WorkerTaskDefinition")}
    api_container = container("api", config["apiImageUri"], uv + ["uvicorn", "otgd.main:app",
        "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--limit-concurrency", "100",
        "--timeout-graceful-shutdown", "100"], api_env, "ApiLogs", port=8000)
    api_container["HealthCheck"] = {"Command": ["CMD", "/opt/venv/bin/python", "-c",
        "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3).read()"],
        "Interval": 30, "Timeout": 5, "Retries": 3, "StartPeriod": 60}
    controller_env = {key: value for key, value in api_env.items() if key in {
        "OTGD_SERVERLESS_CONTROL_TABLE", "OTGD_ECS_CLUSTER_ARN", "OTGD_ECS_WORKER_TASK_DEFINITION_ARN",
        "OTGD_ECS_SUBNET_IDS", "OTGD_ECS_SECURITY_GROUP_IDS", "OTGD_DEPLOYMENT_ACCOUNT",
        "OTGD_AWS_REGION", "OTGD_SOURCE_REVISION", "OTGD_QUEUE_URL", "OTGD_DLQ_URL"}}
    controller_env.update(OTGD_SERVERLESS_CONTROL_ONLY="true", OTGD_SERVERLESS_EXECUTOR="ecs",
                          PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1", UV_NO_SYNC="1")
    controller = container("controller", config["workerImageUri"],
        uv + ["python", "-m", "otgd.fargate_runtime", "controller"], controller_env, "ControlLogs")
    controller["HealthCheck"] = {"Command": ["CMD", "/opt/venv/bin/python", "-c",
        "import json,time; from pathlib import Path; p=Path('/tmp/otgd-controller-health.json'); "
        "assert p.stat().st_size<=256; v=json.loads(p.read_bytes()); "
        "assert type(v.get('time')) in (int,float) and 0<=time.time()-v['time']<=150 "
        "and v.get('status') in ('idle','scheduled')"],
        "Interval": 30, "Timeout": 5, "Retries": 3, "StartPeriod": 90}
    ui = container("ui", config["uiImageUri"], ["nginx", "-g", "daemon off;"],
        {"OTGD_SOURCE_REVISION": revision}, "UiLogs", port=8080)
    ui["DependsOn"] = [{"ContainerName": "api", "Condition": "HEALTHY"}]
    task("ApiTaskDefinition", "api", 256, 1024, "Api", [api_container, ui, controller])
    resource("ApiService", "AWS::ECS::Service", {
        "ServiceName": PREFIX + "-api", "Cluster": ref("Cluster"), "TaskDefinition": ref("ApiTaskDefinition"),
        "LaunchType": "FARGATE", "PlatformVersion": "1.4.0", "DesiredCount": 1 if active else 0,
        "EnableExecuteCommand": False, "HealthCheckGracePeriodSeconds": 90,
        "DeploymentConfiguration": {"MinimumHealthyPercent": 100, "MaximumPercent": 200,
                                    "DeploymentCircuitBreaker": {"Enable": True, "Rollback": True}},
        "NetworkConfiguration": {"AwsvpcConfiguration": {"AssignPublicIp": "DISABLED",
            "Subnets": [ref("TaskA"), ref("TaskB")], "SecurityGroups": [ref("TaskSecurityGroup")]}},
        "LoadBalancers": [{"ContainerName": "ui", "ContainerPort": 8080, "TargetGroupArn": ref("IngressTargets")}],
        "Tags": tags, "PropagateTags": "SERVICE", "EnableECSManagedTags": True},
        DependsOn=["IngressListener", "TaskAIpv6Route", "TaskBIpv6Route", "DatabaseWriter"])

    alarm_specs = [
        ("HighServiceCpu", "CPUUtilization", "AWS/ECS", 90, [{"Name": "ClusterName", "Value": ref("Cluster")}, {"Name": "ServiceName", "Value": PREFIX + "-api"}], "Maximum"),
        ("HighServiceMemory", "MemoryUtilization", "AWS/ECS", 90, [{"Name": "ClusterName", "Value": ref("Cluster")}, {"Name": "ServiceName", "Value": PREFIX + "-api"}], "Maximum"),
        ("UnhealthyIngress", "UnHealthyHostCount", "AWS/ApplicationELB", 1, [{"Name": "LoadBalancer", "Value": att("Ingress", "LoadBalancerFullName")}, {"Name": "TargetGroup", "Value": att("IngressTargets", "TargetGroupFullName")}], "Maximum"),
        ("ApiTargetErrors", "HTTPCode_Target_5XX_Count", "AWS/ApplicationELB", 5, [{"Name": "LoadBalancer", "Value": att("Ingress", "LoadBalancerFullName")}], "Sum"),
        ("DatabaseConnectionPressure", "DatabaseConnections", "AWS/RDS", 20, [{"Name": "DBInstanceIdentifier", "Value": PREFIX + "-writer"}], "Maximum"),
        ("DeadLetters", "ApproximateNumberOfMessagesVisible", "AWS/SQS", 1, [{"Name": "QueueName", "Value": att("DeadLetterQueue", "QueueName")}], "Maximum"),
        ("OldSourceMessage", "ApproximateAgeOfOldestMessage", "AWS/SQS", 300, [{"Name": "QueueName", "Value": att("JobsQueue", "QueueName")}], "Maximum"),
        ("OldOutbox", "OldestOutboxSeconds", NAMESPACE, 120, [], "Maximum"),
        ("OldPrivacyJob", "OldestPrivacyJobSeconds", NAMESPACE, 900, [], "Maximum"),
        ("OverdueCleanup", "CleanupOverdueCount", NAMESPACE, 1, [], "Maximum"),
    ]
    for name, metric, namespace, threshold, dimensions, statistic in alarm_specs:
        resource(name, "AWS::CloudWatch::Alarm", {"AlarmName": PREFIX + "-" + name,
            "Namespace": namespace, "MetricName": metric, "Dimensions": dimensions,
            "Statistic": statistic, "Period": 60, "EvaluationPeriods": 1, "Threshold": threshold,
            "ComparisonOperator": "GreaterThanOrEqualToThreshold", "TreatMissingData": "notBreaching",
            "AlarmActions": [ref("Notifications")]})
    widgets = [{"type": "text", "x": 0, "y": 0, "width": 24, "height": 3,
        "properties": {"markdown": "# Fargate development system health\nUI, API and metadata controller run in one Fargate service. Jobs and maintenance run in bounded Fargate tasks. Aurora pauses between work; SQL metrics publish during work. Confirm SNS email delivery and inspect deployment receipts."}},
        {"type": "alarm", "x": 0, "y": 3, "width": 24, "height": 3,
         "properties": {"title": "System alarms", "alarms": [att(row[0], "Arn") for row in alarm_specs]}}]
    graphs = [
        ("Fargate service CPU and memory", [["AWS/ECS", metric, "ClusterName", ref("Cluster"), "ServiceName", PREFIX + "-api"] for metric in ("CPUUtilization", "MemoryUtilization")]),
        ("Ingress health and response time", [["AWS/ApplicationELB", "HealthyHostCount", "LoadBalancer", att("Ingress", "LoadBalancerFullName"), "TargetGroup", att("IngressTargets", "TargetGroupFullName")], ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", att("Ingress", "LoadBalancerFullName"), {"stat": "p95"}]]),
        ("Aurora capacity and connections", [["AWS/RDS", metric, "DBInstanceIdentifier", PREFIX + "-writer"] for metric in ("ServerlessDatabaseCapacity", "DatabaseConnections", "CPUUtilization")]),
        ("Queue backlog and age", [["AWS/SQS", metric, "QueueName", att("JobsQueue", "QueueName")] for metric in ("ApproximateNumberOfMessagesVisible", "ApproximateAgeOfOldestMessage")]),
        ("Actual SQL privacy and outbox age", [[NAMESPACE, "OldestOutboxSeconds"], [NAMESPACE, "OldestPrivacyJobSeconds"], [NAMESPACE, "CleanupOverdueCount"]]),
        ("API delivery requests and errors", [["AWS/CloudFront", metric, "DistributionId", ref("ApiDelivery"), "Region", "Global"] for metric in ("Requests", "5xxErrorRate")]),
        ("UI delivery requests and errors", [["AWS/CloudFront", metric, "DistributionId", ref("WebDelivery"), "Region", "Global"] for metric in ("Requests", "5xxErrorRate")]),
    ]
    for index, (title, metrics) in enumerate(graphs):
        widgets.append({"type": "metric", "x": 12 * (index % 2), "y": 6 + 6 * (index // 2),
            "width": 12, "height": 6, "properties": {"title": title, "view": "timeSeries",
                "region": "us-east-1" if index >= 5 else region, "stat": "Maximum", "period": 60, "metrics": metrics}})
    bindings = {}

    def bind(value):
        if isinstance(value, dict) and ("Ref" in value or "Fn::GetAtt" in value):
            token = "DashboardToken" + str(len(bindings))
            bindings[token] = value
            return "${" + token + "}"
        if isinstance(value, dict):
            return {key: bind(item) for key, item in value.items()}
        if isinstance(value, list):
            return [bind(item) for item in value]
        return value

    resource("HealthDashboard", "AWS::CloudWatch::Dashboard", {"DashboardName": PREFIX + "-health",
        "DashboardBody": sub(json.dumps(bind({"start": "-PT6H", "widgets": widgets}), separators=(",", ":")), bindings)})
    resources["MonthlyBudget"]["Properties"]["Budget"]["BudgetLimit"]["Amount"] = config["monthlyBudgetUsd"]
    for name, value in {
        "Cluster": att("Cluster", "Arn"), "ClusterArn": att("Cluster", "Arn"), "ApiService": ref("ApiService"),
        "ApiTaskDefinition": ref("ApiTaskDefinition"), "WorkerTaskDefinition": ref("WorkerTaskDefinition"),
        "MaintenanceTaskDefinition": ref("MaintenanceTaskDefinition"), "MigrationTaskDefinition": ref("MaintenanceTaskDefinition"),
        "ApiTaskRoleArn": att("ApiRole", "Arn"), "WorkerTaskRoleArn": att("WorkerRole", "Arn"),
        "MaintenanceTaskRoleArn": att("MaintenanceRole", "Arn"), "ExecutionRoleArn": att("ExecutionRole", "Arn"),
        "TaskSubnets": task_subnets, "TaskSecurityGroups": task_groups,
        "VpcOriginId": ref("VpcOrigin"), "LoadBalancerArn": ref("Ingress"),
        "LoadBalancerDns": att("Ingress", "DNSName"), "TargetGroupArn": ref("IngressTargets"),
        "ApiImageUri": config["apiImageUri"], "WorkerImageUri": config["workerImageUri"], "UiImageUri": config["uiImageUri"],
        "UiLogGroup": ref("UiLogs"), "MonthlyBudgetName": PREFIX + "-monthly", "AlertTopicArn": ref("Notifications"),
        "DeploymentBucket": deployment_bucket,
        "ActivateServices": str(active).lower(),
    }.items():
        output(name, value)
    return base
