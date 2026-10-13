"""Infrastructure contracts covering ownership, transport and staged admission."""
import importlib.util
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("fargate_template", ROOT / "deploy/fargate_template.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FargateTemplateTest(unittest.TestCase):
    def setUp(self):
        self.config = {"environment": "fargate-development", "account": "123456789012",
            "region": "us-east-2", "releaseId": "a" * 40, "alarmEmail": "operator@otgd.test",
            "monthlyBudgetUsd": 100, "cloudFrontPrefixListId": "pl-12345678"}
        for key, digest in (("apiImageUri", "a"), ("workerImageUri", "b"), ("uiImageUri", "c")):
            self.config[key] = "123456789012.dkr.ecr.us-east-2.amazonaws.com/otgd-serverless-development@sha256:" + digest * 64
        self.template = MODULE.build_template(self.config)
        self.resources = self.template["Resources"]

    def properties(self, name):
        return self.resources[name]["Properties"]

    def east_configuration(self):
        config = {**self.config, 'region': 'us-east-1', 'backupRegion': 'us-west-2',
            'availabilityZones': [{'name': 'us-east-1f', 'id': 'use1-az1'},
                                  {'name': 'us-east-1b', 'id': 'use1-az2'}]}
        for name in ('apiImageUri', 'workerImageUri', 'uiImageUri'):
            config[name] = config[name].replace('us-east-2', 'us-east-1')
        return config

    def test_east1_preserves_verified_physical_zones_and_backup_binding_across_all_renders(self):
        config = self.east_configuration()
        key = 'arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789abc'
        for changes in ({'activateServices': False}, {'activateServices': False, 'uiImageUri': config['apiImageUri']},
                        {'activateServices': True}, {'releaseId': 'b' * 40}):
            with self.subTest(changes=changes):
                template = MODULE.build_template({**config, **changes}, recovery_key_arn=key)
                resources = template['Resources']
                for name, zone in (('PrivateA', 'us-east-1f'), ('TaskA', 'us-east-1f'),
                                   ('PrivateB', 'us-east-1b'), ('TaskB', 'us-east-1b'),
                                   ('DatabaseWriter', 'us-east-1f')):
                    self.assertEqual(resources[name]['Properties']['AvailabilityZone'], zone)
                self.assertEqual(json.loads(template['Outputs']['AvailabilityZones']['Value']), config['availabilityZones'])
                self.assertNotIn('RecoveryKeyArn', template.get('Parameters', {}))
                for task, container in (('ApiTaskDefinition', 'api'), ('WorkerTaskDefinition', 'worker'),
                                        ('MaintenanceTaskDefinition', 'maintenance')):
                    row = next(row for row in resources[task]['Properties']['ContainerDefinitions'] if row['Name'] == container)
                    env = self.environment(row)
                    self.assertEqual(env['OTGD_AWS_REGION'], 'us-east-1')
                    self.assertEqual(env['OTGD_BACKUP_REGION'], 'us-west-2')
                    self.assertEqual(env['OTGD_BACKUP_KMS_KEY_ID'], key)
                    self.assertEqual(env['OTGD_BACKUP_ARTIFACT_BUCKET'], 'otgd-fargate-recovery-123456789012-us-west-2-artifacts')
                    self.assertEqual(env['OTGD_BACKUP_EXPORT_BUCKET'], 'otgd-fargate-recovery-123456789012-us-west-2-exports')
                    self.assertIn('.dkr-ecr.us-east-1.on.aws/', row['Image'])
                controller = next(row for row in resources['ApiTaskDefinition']['Properties']['ContainerDefinitions']
                                  if row['Name'] == 'controller')
                self.assertFalse(any(name.startswith('OTGD_BACKUP_') for name in self.environment(controller)))
                for role in ('WorkerRole', 'MaintenanceRole'):
                    policy = next(p for p in resources[role]['Properties']['Policies'] if p['PolicyName'] == 'ReplicaPrivacyErasure')
                    self.assertNotIn('journal', json.dumps(policy))
                    self.assertNotIn('kms:Decrypt', json.dumps(policy))

    def test_east1_registry_replication_precedes_application_and_plans_bind_an_explicit_key_parameter(self):
        config = self.east_configuration()
        key = 'arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789abc'
        registry = MODULE.build_template(config, 'registry', recovery_key_arn=key)
        self.assertIn('RegionalReplicationRole', registry['Resources'])
        self.assertEqual(registry['Resources']['DeploymentAssets']['Properties']['ReplicationConfiguration']['Rules'][0]
                         ['Destination']['EncryptionConfiguration']['ReplicaKmsKeyID'], key)
        platform = MODULE.build_template(config)
        self.assertIn('RecoveryKeyArn', platform['Parameters'])
        for name in ('Artifacts', 'Exports', 'DeletionJournal', 'WebAssets'):
            self.assertIn('ReplicationConfiguration', platform['Resources'][name]['Properties'])
        self.assertNotIn('RegionalReplicationRole', platform['Resources'])
        self.assertNotIn('RegionalBackupPlan', registry['Resources'])

    def test_east1_cannot_use_unsupported_physical_zone_or_ohio_authority_overrides(self):
        config = self.east_configuration()
        for zones in (None, ['us-east-1a', 'us-east-1b'],
                      [{'name': 'us-east-1f', 'id': 'use1-az3'}, config['availabilityZones'][1]],
                      [config['availabilityZones'][0]] * 2):
            with self.subTest(zones=zones), self.assertRaises(ValueError):
                MODULE.build_template({**config, 'availabilityZones': zones})
        with self.assertRaises(ValueError):
            MODULE.build_template(config, preserved_private_b_resource=self.resources['PrivateB'])
        with self.assertRaises(ValueError):
            MODULE.build_template({**config, 'region': 'us-west-2'})
        with self.assertRaises(ValueError):
            MODULE.build_template(self.config, recovery_key_arn='arn:aws:kms:us-west-2:123456789012:key/' + 'a' * 36)

    def test_managed_repair_resource_is_preserved_in_every_application_render(self):
        resource = deepcopy(self.resources['PrivateB'])
        resource.pop('DependsOn')
        resource['Properties'].update(VpcId='vpc-12345678', AvailabilityZone='us-east-2b',
                                      Ipv6CidrBlock='2001:db8:1234:5601::/64')
        original = deepcopy(resource)
        for changes in ({'activateServices': False}, {'activateServices': False, 'uiImageUri': self.config['apiImageUri']},
                        {'activateServices': True}, {'activateServices': False, 'releaseId': 'b' * 40}):
            with self.subTest(changes=changes):
                result = MODULE.build_template({**self.config, **changes}, preserved_private_b_resource=resource)
                self.assertEqual(result['Resources']['PrivateB'], original)
                self.assertNotIn('DependsOn', result['Resources']['PrivateB'])
                result['Resources']['PrivateB']['Properties']['VpcId'] = 'mutated-result'
                self.assertEqual(resource, original)

    def test_repair_render_rejects_intrinsics_foreign_geometry_and_nonretained_resources(self):
        valid = {'Type': 'AWS::EC2::Subnet', 'DeletionPolicy': 'Retain', 'UpdateReplacePolicy': 'Retain',
                 'Properties': {'VpcId': 'vpc-12345678', 'AvailabilityZone': 'us-east-2b',
                     'CidrBlock': '10.76.1.0/24', 'Ipv6CidrBlock': '2001:db8:1234:5601::/64',
                     'AssignIpv6AddressOnCreation': True, 'MapPublicIpOnLaunch': False,
                     'Tags': deepcopy(self.resources['PrivateB']['Properties']['Tags'])}}
        invalid = []
        for field, value in (('VpcId', {'Ref': 'Network'}), ('AvailabilityZone', 'us-west-2b'),
                             ('CidrBlock', '10.76.2.0/24'), ('Ipv6CidrBlock', '2001:db8::/56'),
                             ('MapPublicIpOnLaunch', True), ('AssignIpv6AddressOnCreation', False)):
            item = deepcopy(valid); item['Properties'][field] = value; invalid.append(item)
        invalid += [{**valid, 'DependsOn': 'NetworkIpv6'}, {**valid, 'DeletionPolicy': 'Delete'}]
        for resource in invalid:
            with self.subTest(resource=resource), self.assertRaises(ValueError):
                MODULE.build_template(self.config, preserved_private_b_resource=resource)
        with self.assertRaises(ValueError):
            MODULE.build_template(self.config, 'registry', preserved_private_b_resource=valid)

    def statements(self, name):
        return self.properties(name)["Policies"][0]["PolicyDocument"]["Statement"]

    def containers(self, task):
        return {row["Name"]: row for row in self.properties(task)["ContainerDefinitions"]}

    @staticmethod
    def environment(container):
        return {row["Name"]: row["Value"] for row in container["Environment"]}

    def test_retained_authority_is_identical_to_the_original_reviewed_resources(self):
        prior = MODULE.original_template({**self.config, "monthlyBudgetUsd": 50})["Resources"]
        self.assertEqual(len(MODULE.RETAINED_AUTHORITY), 15)
        for name in MODULE.RETAINED_AUTHORITY:
            self.assertEqual(self.resources[name], prior[name], name)
            self.assertEqual(self.resources[name]["DeletionPolicy"], "Retain")
            self.assertEqual(self.resources[name]["UpdateReplacePolicy"], "Retain")
        journal = self.properties("DeletionJournal")
        self.assertEqual(journal["ObjectLockConfiguration"]["Rule"]["DefaultRetention"],
                         {"Mode": "COMPLIANCE", "Days": 90})
        self.assertNotIn("LifecycleConfiguration", journal)

    def test_database_transition_preserves_existing_security_group_identities(self):
        prior = MODULE.original_template({**self.config, "monthlyBudgetUsd": 50})["Resources"]
        for active in (False, True):
            resources = MODULE.build_template({**self.config, "activateServices": active})["Resources"]
            self.assertEqual(resources["LambdaSecurityGroup"], prior["LambdaSecurityGroup"])
            database = resources["DatabaseSecurityGroup"]
            for field in ("GroupDescription", "VpcId"):
                self.assertEqual(database["Properties"][field], prior["DatabaseSecurityGroup"]["Properties"][field])
            self.assertEqual(database["Properties"]["SecurityGroupIngress"], [{
                "IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432,
                "SourceSecurityGroupId": {"Ref": "TaskSecurityGroup"}}])
            self.assertEqual(database["DeletionPolicy"], "Retain")
            self.assertEqual(database["UpdateReplacePolicy"], "Retain")

    def test_only_fargate_compute_and_private_dualstack_ingress_are_created(self):
        kinds = [row["Type"] for row in self.resources.values()]
        self.assertEqual(kinds.count("AWS::ECS::Service"), 1)
        self.assertEqual(kinds.count("AWS::ECS::TaskDefinition"), 3)
        self.assertEqual(kinds.count("AWS::ElasticLoadBalancingV2::LoadBalancer"), 1)
        for kind in kinds:
            self.assertFalse(kind.startswith(("AWS::Lambda::", "AWS::ApiGateway")))
            self.assertNotIn(kind, ("AWS::EC2::Instance", "AWS::EC2::NatGateway", "AWS::EC2::VPCEndpoint"))
        self.assertEqual(self.properties("Ingress")["Scheme"], "internal")
        self.assertEqual(self.properties("Ingress")["IpAddressType"], "dualstack")
        self.assertEqual(self.properties("IngressTargets")["IpAddressType"], "ipv6")
        self.assertEqual(self.properties("IngressTargets")["TargetType"], "ip")

    def test_tasks_use_ipv6_only_subnets_and_have_no_public_ipv4_or_nat_route(self):
        cidrs = []
        for name in ("TaskA", "TaskB"):
            subnet = self.properties(name)
            self.assertTrue(subnet["Ipv6Native"] and subnet["AssignIpv6AddressOnCreation"])
            self.assertFalse(subnet["MapPublicIpOnLaunch"])
            self.assertNotIn("CidrBlock", subnet)
            cidrs.append(subnet["Ipv6CidrBlock"]["Fn::Select"][0])
            route = self.properties(name + "Ipv6Route")
            self.assertEqual(route["DestinationIpv6CidrBlock"], "::/0")
            self.assertEqual(route["EgressOnlyInternetGatewayId"], {"Ref": "Ipv6Egress"})
        self.assertEqual(cidrs, [2, 3])
        network = self.properties("ApiService")["NetworkConfiguration"]["AwsvpcConfiguration"]
        self.assertEqual(network["AssignPublicIp"], "DISABLED")
        self.assertEqual(network["Subnets"], [{"Ref": "TaskA"}, {"Ref": "TaskB"}])
        self.assertEqual(self.properties("ApiService")["PlatformVersion"], "1.4.0")
        self.assertFalse(self.properties("ApiService")["EnableExecuteCommand"])
        self.assertEqual(self.properties("IngressSecurityGroup")["SecurityGroupIngress"], [{
            "IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080,
            "SourcePrefixListId": "pl-12345678"}])
        for group in ("TaskSecurityGroup", "IngressSecurityGroup"):
            self.assertFalse(any(row.get("CidrIp") == "0.0.0.0/0" or row.get("CidrIpv6") == "::/0"
                                 for row in self.properties(group)["SecurityGroupIngress"]))

    def test_database_has_ipv6_access_without_weakened_pause_or_tls_contract(self):
        database = self.properties("Database")
        self.assertEqual(database["NetworkType"], "DUAL")
        self.assertEqual(database["ServerlessV2ScalingConfiguration"],
                         {"MinCapacity": 0, "MaxCapacity": 1, "SecondsUntilAutoPause": 300})
        self.assertTrue(database["StorageEncrypted"] and database["DeletionProtection"])
        self.assertEqual(self.properties("DatabaseParameters")["Parameters"], {"rds.force_ssl": "1"})
        self.assertFalse(self.properties("DatabaseWriter")["PubliclyAccessible"])
        self.assertEqual(self.properties("DatabaseSecurityGroup")["SecurityGroupIngress"], [{
            "IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432,
            "SourceSecurityGroupId": {"Ref": "TaskSecurityGroup"}}])
        for task in ("ApiTaskDefinition", "WorkerTaskDefinition", "MaintenanceTaskDefinition"):
            name = {"ApiTaskDefinition": "api", "WorkerTaskDefinition": "worker", "MaintenanceTaskDefinition": "maintenance"}[task]
            env = self.environment(self.containers(task)[name])
            self.assertEqual(env["OTGD_DATABASE_SSLMODE"], "verify-full")
            self.assertNotIn("OTGD_DATABASE_PASSWORD", env)

    def test_ui_api_and_controller_share_one_service_but_jobs_are_bounded_tasks(self):
        service = self.properties("ApiService")
        self.assertEqual(service["DesiredCount"], 0)
        self.assertEqual(service["TaskDefinition"], {"Ref": "ApiTaskDefinition"})
        self.assertEqual(service["LoadBalancers"], [{"ContainerName": "ui", "ContainerPort": 8080,
                                                   "TargetGroupArn": {"Ref": "IngressTargets"}}])
        main = self.properties("ApiTaskDefinition")
        self.assertEqual((main["Cpu"], main["Memory"]), ("256", "1024"))
        containers = self.containers("ApiTaskDefinition")
        self.assertEqual(set(containers), {"api", "ui", "controller"})
        self.assertEqual(containers["ui"]["DependsOn"], [{"ContainerName": "api", "Condition": "HEALTHY"}])
        self.assertIn("/health/live", " ".join(containers["api"]["HealthCheck"]["Command"]))
        heartbeat = containers["controller"]["HealthCheck"]
        self.assertIn("/tmp/otgd-controller-health.json", " ".join(heartbeat["Command"]))
        self.assertIn("<=150", " ".join(heartbeat["Command"]))
        self.assertIn("st_size<=256", " ".join(heartbeat["Command"]))
        self.assertEqual(self.properties("IngressTargets")["HealthCheckPath"], "/health/live")
        for task, memory in (("WorkerTaskDefinition", "2048"), ("MaintenanceTaskDefinition", "1024")):
            self.assertEqual(self.properties(task)["Cpu"], "512")
            self.assertEqual(self.properties(task)["Memory"], memory)
            self.assertEqual(len(self.containers(task)), 1)
        active = MODULE.build_template({**self.config, "activateServices": True})
        self.assertEqual(active["Resources"]["ApiService"]["Properties"]["DesiredCount"], 1)
        self.assertEqual(self.template["Outputs"]["ActivateServices"]["Value"], "false")
        self.assertEqual(active["Outputs"]["ActivateServices"]["Value"], "true")

    def test_generated_https_origins_use_private_alb_and_preserve_streaming_paths(self):
        self.assertIn("InternetGatewayAttachment", self.resources["VpcOrigin"]["DependsOn"])
        endpoint = self.properties("VpcOrigin")["VpcOriginEndpointConfig"]
        self.assertEqual(endpoint["Arn"], {"Ref": "Ingress"})
        self.assertEqual(endpoint["OriginProtocolPolicy"], "http-only")
        self.assertEqual(endpoint["HTTPPort"], 8080)
        attributes = {row["Key"]: row["Value"] for row in self.properties("Ingress")["LoadBalancerAttributes"]}
        self.assertEqual(attributes["idle_timeout.timeout_seconds"], "900")
        for name in ("ApiDelivery", "WebDelivery"):
            delivery = self.properties(name)["DistributionConfig"]
            self.assertEqual(delivery["ViewerCertificate"], {"CloudFrontDefaultCertificate": True})
            origin = delivery["Origins"][0]
            self.assertEqual(origin["DomainName"], {"Fn::GetAtt": ["Ingress", "DNSName"]})
            self.assertEqual(origin["VpcOriginConfig"]["VpcOriginId"], {"Ref": "VpcOrigin"})
            self.assertEqual(origin["VpcOriginConfig"]["OriginReadTimeout"], 60)
            self.assertNotIn("OriginPath", origin)
            self.assertNotIn("S3OriginConfig", origin)
            self.assertNotIn("ResponseCompletionTimeout", origin)
            behavior = delivery["DefaultCacheBehavior"]
            self.assertEqual(behavior["CachePolicyId"], "4135ea2d-6df8-44a3-9df3-4b5a84be39ad")
            self.assertEqual(behavior["OriginRequestPolicyId"], "b689b0a8-53d0-40ab-baf2-68738e2966ac")
            self.assertEqual(set(behavior["AllowedMethods"]), {"GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"})

    def test_owned_immutable_images_use_ecr_dualstack_endpoints_at_runtime(self):
        for task in ("ApiTaskDefinition", "WorkerTaskDefinition", "MaintenanceTaskDefinition"):
            self.assertEqual(self.properties(task)["RuntimePlatform"],
                             {"OperatingSystemFamily": "LINUX", "CpuArchitecture": "X86_64"})
            for row in self.containers(task).values():
                self.assertRegex(row["Image"], r"^123456789012\.dkr-ecr\.us-east-2\.on\.aws/otgd-serverless-development@sha256:[0-9a-f]{64}$")
                self.assertTrue(row["ReadonlyRootFilesystem"] and row["Essential"])
                self.assertEqual(row["User"], "10001")
                self.assertNotIn("awslogs-endpoint", row["LogConfiguration"]["Options"])
                self.assertNotIn("Secrets", row)
                self.assertEqual(self.environment(row)["OTGD_SOURCE_REVISION"], self.config["releaseId"])
        registry = MODULE.build_template(self.config, "registry")
        images = registry["Resources"]["Images"]
        self.assertEqual(images["Properties"]["ImageTagMutability"], "IMMUTABLE")
        self.assertNotIn("RepositoryPolicyText", images["Properties"])
        self.assertNotIn("LifecyclePolicy", images["Properties"])
        self.assertEqual(images["DeletionPolicy"], "Retain")

    def test_only_api_role_can_launch_worker_and_cannot_pass_maintenance_role(self):
        for role in ("ApiRole", "WorkerRole", "MaintenanceRole", "ExecutionRole"):
            trust = self.properties(role)["AssumeRolePolicyDocument"]["Statement"][0]
            self.assertEqual(trust["Principal"], {"Service": "ecs-tasks.amazonaws.com"})
            self.assertEqual(trust["Condition"]["StringEquals"], {"aws:SourceAccount": "123456789012"})
            self.assertFalse(any(action.startswith(("lambda:", "ec2:")) for row in self.statements(role) for action in row["Action"]))
        allowed = self.statements("ApiRole")
        run = next(row for row in allowed if "ecs:RunTask" in row["Action"])
        self.assertEqual(run["Resource"], {"Ref": "WorkerTaskDefinition"})
        self.assertEqual(run["Condition"], {"ArnEquals": {"ecs:cluster": {"Fn::GetAtt": ["Cluster", "Arn"]}}})
        roles = next(row for row in allowed if "iam:PassRole" in row["Action"])
        self.assertEqual(roles["Resource"], [{"Fn::GetAtt": ["WorkerRole", "Arn"]}, {"Fn::GetAtt": ["ExecutionRole", "Arn"]}])
        for role in ("ApiRole", "WorkerRole"):
            self.assertNotIn("MasterUserSecret.SecretArn", json.dumps(self.statements(role)))
        for role in ("WorkerRole", "MaintenanceRole"):
            self.assertFalse(any("ecs:RunTask" in row["Action"] or "iam:PassRole" in row["Action"] for row in self.statements(role)))
        self.assertIn("MasterUserSecret.SecretArn", json.dumps(self.statements("MaintenanceRole")))
        receipts = [row for row in self.statements("MaintenanceRole") if row.get("Condition", {}).get("StringEquals", {}).get("s3:if-none-match") == "*"]
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["Resource"], "arn:aws:s3:::otgd-serverless-development-123456789012-us-east-2-deployments/receipts/" + "a" * 40 + "/*")
        self.assertEqual(receipts[0]["Action"], ["s3:PutObject"])
        for role in ("ApiRole", "WorkerRole", "ExecutionRole"):
            self.assertNotIn("/receipts/", json.dumps(self.statements(role)))
        self.assertNotIn("secretsmanager:GetSecretValue", json.dumps(self.statements("ExecutionRole")))

    def test_controller_never_receives_sql_or_application_secret_configuration(self):
        main = self.containers("ApiTaskDefinition")
        controller = self.environment(main["controller"])
        self.assertEqual(controller["OTGD_SERVERLESS_CONTROL_ONLY"], "true")
        self.assertEqual(controller["OTGD_SERVERLESS_EXECUTOR"], "ecs")
        self.assertEqual(controller["OTGD_ECS_WORKER_TASK_DEFINITION_ARN"], {"Ref": "WorkerTaskDefinition"})
        self.assertFalse(any("DATABASE" in key or "SECRET" in key or "TOMBSTONE" in key or "BUCKET" in key for key in controller))
        worker = self.environment(self.containers("WorkerTaskDefinition")["worker"])
        admin = self.environment(self.containers("MaintenanceTaskDefinition")["maintenance"])
        self.assertNotIn("OTGD_ECS_WORKER_TASK_DEFINITION_ARN", worker)
        self.assertNotIn("OTGD_ECS_WORKER_TASK_DEFINITION_ARN", admin)
        self.assertEqual(worker["OTGD_DATABASE_SECRET_ARN"], {"Ref": "ApplicationSecret"})
        self.assertEqual(admin["OTGD_DATABASE_SECRET_ARN"], {"Fn::GetAtt": ["Database", "MasterUserSecret.SecretArn"]})
        self.assertEqual(admin["OTGD_APP_DATABASE_SECRET_ARN"], {"Ref": "ApplicationSecret"})

    def test_actual_sql_metrics_and_native_health_have_ten_alarms_and_approved_budget(self):
        alarms = [row["Properties"] for row in self.resources.values() if row["Type"] == "AWS::CloudWatch::Alarm"]
        self.assertEqual(len(alarms), 10)
        custom = [row for row in alarms if row["Namespace"] == MODULE.NAMESPACE]
        self.assertEqual({row["MetricName"] for row in custom},
                         {"OldestOutboxSeconds", "OldestPrivacyJobSeconds", "CleanupOverdueCount"})
        self.assertTrue(all(row["TreatMissingData"] == "notBreaching" for row in alarms))
        body, bindings = self.properties("HealthDashboard")["DashboardBody"]["Fn::Sub"]
        for token in bindings:
            body = body.replace("${" + token + "}", "owned-resource")
        dashboard = json.loads(body)
        metrics = [metric for widget in dashboard["widgets"] if widget["type"] == "metric" for metric in widget["properties"]["metrics"]]
        self.assertTrue({"AWS/ECS", "AWS/ApplicationELB", "AWS/RDS", "AWS/SQS", "AWS/CloudFront", MODULE.NAMESPACE}.issubset({metric[0] for metric in metrics}))
        self.assertNotIn("AWS/Lambda", {metric[0] for metric in metrics})
        self.assertEqual(self.properties("MonthlyBudget")["Budget"]["BudgetLimit"], {"Amount": 100, "Unit": "USD"})
        notices = self.properties("MonthlyBudget")["NotificationsWithSubscribers"]
        self.assertEqual([(row["Notification"]["NotificationType"], row["Notification"]["Threshold"]) for row in notices],
                         [("ACTUAL", 50), ("ACTUAL", 80), ("ACTUAL", 100), ("FORECASTED", 100)])
        self.assertTrue(all(row["Subscribers"] == [{"Address": "operator@otgd.test", "SubscriptionType": "EMAIL"}] for row in notices))

    def test_browser_upload_and_journal_policies_remain_scoped_to_actual_authority(self):
        cors = self.properties("Artifacts")["CorsConfiguration"]["CorsRules"]
        self.assertEqual(len(cors), 1)
        self.assertEqual(cors[0]["AllowedOrigins"], [{"Fn::Sub": "https://${WebDelivery.DomainName}"}])
        self.assertEqual(cors[0]["AllowedMethods"], ["PUT"])
        origin = self.template["Outputs"]["ArtifactUploadOrigin"]["Value"]
        self.assertEqual(origin, "https://s3.dualstack.us-east-2.amazonaws.com/otgd-serverless-development-123456789012-us-east-2-artifacts/")
        csp = self.properties("WebHeaders")["ResponseHeadersPolicyConfig"]["SecurityHeadersConfig"]["ContentSecurityPolicy"]["ContentSecurityPolicy"]["Fn::Sub"]
        self.assertIn(origin, csp)
        policy = self.properties("DeletionJournalPolicy")["PolicyDocument"]["Statement"]
        deny = next(row for row in policy if row["Action"] == ["s3:DeleteObject", "s3:DeleteObjectVersion"])
        self.assertEqual(deny["Principal"]["AWS"], [{"Fn::GetAtt": [role + "Role", "Arn"]} for role in ("Api", "Worker", "Maintenance")])
        self.assertTrue(any(row["Effect"] == "Deny" and "scope-resumptions/*" in json.dumps(row) for row in policy))
        self.assertFalse(any(row["Effect"] == "Allow" for row in self.properties("WebAssetsPolicy")["PolicyDocument"]["Statement"]))

    def test_template_references_are_present_and_dependency_graph_has_no_cycle(self):
        graph = {name: set() for name in self.resources}

        def visit(value, found):
            if isinstance(value, dict):
                if "Ref" in value:
                    found.add(value["Ref"])
                if "Fn::GetAtt" in value:
                    found.add(value["Fn::GetAtt"][0])
                if "Fn::Sub" in value:
                    substitution = value["Fn::Sub"]
                    text = substitution if isinstance(substitution, str) else substitution[0]
                    bindings = {} if isinstance(substitution, str) else substitution[1]
                    for token in re.findall(r"\$\{([^}]+)\}", text):
                        if token not in bindings and not token.startswith("!"):
                            found.add(token.split(".")[0])
                for item in value.values():
                    visit(item, found)
            elif isinstance(value, list):
                for item in value:
                    visit(item, found)

        for name, resource in self.resources.items():
            visit(resource.get("Properties", {}), graph[name])
            dependencies = resource.get("DependsOn", [])
            graph[name].update([dependencies] if isinstance(dependencies, str) else dependencies)
            for target in graph[name]:
                self.assertTrue(target in graph or target.startswith("AWS::"), (name, target))
            graph[name] = {target for target in graph[name] if target in graph}
        complete, visiting = set(), set()

        def acyclic(name):
            self.assertNotIn(name, visiting, "CloudFormation dependency cycle")
            if name in complete:
                return
            visiting.add(name)
            for target in graph[name]:
                acyclic(target)
            visiting.remove(name)
            complete.add(name)

        for name in graph:
            acyclic(name)
        output_refs = set()
        visit(self.template["Outputs"], output_refs)
        self.assertTrue(all(name in graph or name.startswith("AWS::") for name in output_refs))
        self.assertLessEqual(len(json.dumps(self.template).encode()), 1048576)

    def test_configuration_rejects_wrong_account_images_prefix_region_budget_and_activation(self):
        bad = [{"account": "not-account"}, {"region": "us-west-2"}, {"releaseId": "main"},
            {"environment": "qa"}, {"prefix": "another-project"}, {"monthlyBudgetUsd": 101},
            {"cloudFrontPrefixListId": ""}, {"cloudFrontPrefixListId": "unreviewed-list"},
            {"monthlyBudgetUsd": float("nan")}, {"monthlyBudgetUsd": True}, {"activateServices": "true"},
            {"uiImageUri": self.config["uiImageUri"].replace("123456789012", "999999999999")},
            {"apiImageUri": self.config["apiImageUri"].replace("@sha256:" + "a" * 64, ":latest")},
            {"workerImageUri": self.config["workerImageUri"].replace("otgd-serverless-development", "company-generation-api")}]
        for override in bad:
            with self.subTest(override=override), self.assertRaises(ValueError):
                MODULE.build_template({**self.config, **override})


if __name__ == "__main__":
    unittest.main()
