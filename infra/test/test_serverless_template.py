import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("serverless_template", ROOT / "deploy/serverless_template.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ServerlessTemplateTest(unittest.TestCase):
    def setUp(self):
        prefix = "otgd-serverless-development"
        self.config = {"account": "123456789012", "region": "us-east-2", "releaseId": "a" * 40,
                       "alarmEmail": "operator@otgd.test", "monthlyBudgetUsd": 50,
                       "apiImageUri": f"123456789012.dkr.ecr.us-east-2.amazonaws.com/{prefix}@sha256:" + "a" * 64,
                       "workerImageUri": f"123456789012.dkr.ecr.us-east-2.amazonaws.com/{prefix}@sha256:" + "b" * 64}
        self.template = MODULE.build_template(self.config)
        self.resources = self.template["Resources"]

    def properties(self, name):
        return self.resources[name]["Properties"]

    def statements(self, role):
        return self.properties(role + "Role")["Policies"][0]["PolicyDocument"]["Statement"]

    def test_registry_is_retained_immutable_and_supplies_private_large_template_storage(self):
        registry = MODULE.build_template({key: value for key, value in self.config.items() if "ImageUri" not in key}, "registry")
        images = registry["Resources"]["Images"]
        self.assertEqual(images["DeletionPolicy"], "Retain")
        self.assertEqual(images["Properties"]["ImageTagMutability"], "IMMUTABLE")
        self.assertTrue(images["Properties"]["ImageScanningConfiguration"]["ScanOnPush"])
        self.assertNotIn("LifecyclePolicy", images["Properties"])
        policy = images["Properties"]["RepositoryPolicyText"]["Statement"][0]
        self.assertEqual(policy["Principal"], {"Service": "lambda.amazonaws.com"})
        self.assertIn("function:otgd-serverless-development-*", policy["Condition"]["ArnLike"]["aws:SourceArn"])
        deployment = registry["Resources"]["DeploymentAssets"]
        self.assertEqual(deployment["DeletionPolicy"], "Retain")
        self.assertTrue(all(deployment["Properties"]["PublicAccessBlockConfiguration"].values()))
        self.assertEqual(deployment["Properties"]["VersioningConfiguration"]["Status"], "Enabled")
        self.assertEqual(registry["Outputs"]["TemplateBucket"]["Value"], {"Ref": "DeploymentAssets"})
        self.assertLessEqual(len(json.dumps(registry, separators=(",", ":")).encode()), 51200)
        self.assertLessEqual(len(json.dumps(self.template, separators=(",", ":")).encode()), 1048576)

    def test_only_serverless_compute_and_free_network_routes_are_provisioned(self):
        kinds = [value["Type"] for value in self.resources.values()]
        self.assertEqual(kinds.count("AWS::Lambda::Function"), 5)
        for excluded in ["AWS::EC2::Instance", "AWS::EC2::NatGateway", "AWS::ECS::Service", "AWS::ECS::TaskDefinition", "AWS::Lambda::Url", "AWS::ApiGatewayV2::Api", "AWS::ElasticLoadBalancingV2::LoadBalancer"]:
            self.assertNotIn(excluded, kinds)
        self.assertEqual(kinds.count("AWS::EC2::EgressOnlyInternetGateway"), 1)
        for endpoint in [value["Properties"] for value in self.resources.values() if value["Type"] == "AWS::EC2::VPCEndpoint"]:
            self.assertEqual(endpoint["VpcEndpointType"], "Gateway")
        for name in ["PrivateA", "PrivateB"]:
            self.assertFalse(self.properties(name)["MapPublicIpOnLaunch"])
            self.assertTrue(self.properties(name)["AssignIpv6AddressOnCreation"])
            self.assertIn("Ipv6CidrBlock", self.properties(name))
            self.assertEqual(self.properties(name + "Ipv6Route")["DestinationIpv6CidrBlock"], "::/0")
            self.assertEqual(self.properties(name + "Ipv6Route")["EgressOnlyInternetGatewayId"], {"Ref": "Ipv6Egress"})
        for role in ["Api", "Worker", "Dispatcher", "Maintenance"]:
            vpc = self.properties(role + "Function")["VpcConfig"]
            self.assertTrue(vpc["Ipv6AllowedForDualStack"])
            self.assertEqual(vpc["SubnetIds"], [{"Ref": "PrivateA"}, {"Ref": "PrivateB"}])
        self.assertNotIn("VpcConfig", self.properties("ControlFunction"))
        ingress = self.properties("DatabaseSecurityGroup")["SecurityGroupIngress"]
        self.assertEqual(ingress, [{"IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432, "SourceSecurityGroupId": {"Ref": "LambdaSecurityGroup"}}])

    def test_postgresql_can_pause_and_secrets_have_separate_administrative_boundary(self):
        database = self.properties("Database")
        self.assertEqual(database["Engine"], "aurora-postgresql")
        self.assertEqual(database["ServerlessV2ScalingConfiguration"], {"MinCapacity": 0, "MaxCapacity": 1, "SecondsUntilAutoPause": 300})
        self.assertTrue(database["ManageMasterUserPassword"])
        self.assertNotIn("MasterUserPassword", database)
        self.assertTrue(database["StorageEncrypted"] and database["DeletionProtection"])
        self.assertEqual(self.properties("DatabaseWriter")["DBInstanceClass"], "db.serverless")
        self.assertFalse(self.properties("DatabaseWriter")["PubliclyAccessible"])
        app = self.properties("ApplicationSecret")["GenerateSecretString"]
        self.assertEqual(json.loads(app["SecretStringTemplate"]), {"username": "otgd_app"})
        self.assertEqual(app["GenerateStringKey"], "password")
        tombstone = self.properties("TombstoneSecret")["GenerateSecretString"]
        self.assertEqual((tombstone["GenerateStringKey"], tombstone["PasswordLength"]), ("key", 64))
        for role in ["Api", "Worker", "Dispatcher"]:
            env = self.properties(role + "Function")["Environment"]["Variables"]
            self.assertEqual(env["OTGD_DATABASE_SECRET_ARN"], {"Ref": "ApplicationSecret"})
            self.assertNotIn("OTGD_APP_DATABASE_SECRET_ARN", env)
            self.assertNotIn("OTGD_DATABASE_PASSWORD", env)
        admin = self.properties("MaintenanceFunction")["Environment"]["Variables"]
        self.assertEqual(admin["OTGD_DATABASE_SECRET_ARN"], {"Fn::GetAtt": ["Database", "MasterUserSecret.SecretArn"]})
        self.assertEqual(admin["OTGD_APP_DATABASE_SECRET_ARN"], {"Ref": "ApplicationSecret"})

    def test_api_streaming_has_generated_https_hostname_and_passes_auth_headers(self):
        api = self.properties("RestApi")
        self.assertEqual(api["EndpointConfiguration"], {"Types": ["REGIONAL"]})
        for name in ["ApiRootMethod", "ApiProxyMethod"]:
            integration = self.properties(name)["Integration"]
            self.assertEqual(integration["Type"], "AWS_PROXY")
            self.assertEqual(integration["ResponseTransferMode"], "STREAM")
            self.assertEqual(integration["TimeoutInMillis"], 900000)
            self.assertIn("/2021-11-15/", integration["Uri"])
            self.assertTrue(integration["Uri"].endswith("/response-streaming-invocations"))
        cloudfront = self.properties("ApiDelivery")["DistributionConfig"]
        self.assertEqual(cloudfront["ViewerCertificate"], {"CloudFrontDefaultCertificate": True})
        origin = cloudfront["Origins"][0]
        self.assertEqual(origin["OriginPath"], "/serverless")
        self.assertEqual(origin["CustomOriginConfig"]["OriginProtocolPolicy"], "https-only")
        self.assertEqual(origin["DomainName"], {"Fn::Sub": "${RestApi}.execute-api.${AWS::Region}.amazonaws.com"})
        behavior = cloudfront["DefaultCacheBehavior"]
        self.assertEqual(behavior["CachePolicyId"], "4135ea2d-6df8-44a3-9df3-4b5a84be39ad")
        self.assertEqual(behavior["OriginRequestPolicyId"], "b689b0a8-53d0-40ab-baf2-68738e2966ac")
        api_env = self.properties("ApiFunction")["Environment"]["Variables"]
        self.assertEqual(api_env["AWS_LWA_INVOKE_MODE"], "response_stream")
        self.assertEqual(api_env["AWS_LWA_READINESS_CHECK_PATH"], "/health/live")
        self.assertEqual(self.properties("ApiFunction")["Timeout"], 900)
        self.assertNotIn("ImageConfig", self.properties("ApiFunction"))
        for role, handler in [("Worker", "sqs_handler"), ("Dispatcher", "dispatch_handler"), ("Maintenance", "maintenance_handler"), ("Control", "control_handler")]:
            self.assertEqual(self.properties(role + "Function")["ImageConfig"]["Command"], ["otgd.serverless_worker." + handler])
        self.assertEqual(self.template["Outputs"]["DatabaseClusterIdentifier"]["Value"], {"Ref": "Database"})
        self.assertEqual(self.template["Outputs"]["MaintenanceFunction"]["Value"], {"Ref": "MaintenanceFunction"})
        self.assertEqual(self.template["Outputs"]["ApiImageUri"]["Value"], self.config["apiImageUri"])
        self.assertEqual(self.template["Outputs"]["WorkerImageUri"]["Value"], self.config["workerImageUri"])
        self.assertEqual(self.template["Outputs"]["WorkerFunctionArn"]["Value"], {"Fn::GetAtt": ["WorkerFunction", "Arn"]})

    def test_staged_activation_cannot_receive_api_jobs_or_scheduled_sql_before_admission(self):
        for role in ["Api", "Worker", "Dispatcher", "Control"]:
            self.assertEqual(self.properties(role + "Function")["ReservedConcurrentExecutions"], 0)
        self.assertEqual(self.properties("MaintenanceFunction")["ReservedConcurrentExecutions"], 1)
        self.assertFalse(self.properties("WorkerMapping")["Enabled"])
        self.assertNotIn("ScalingConfig", self.properties("WorkerMapping"))
        self.assertEqual(self.properties("ControlSchedule")["State"], "DISABLED")
        active = MODULE.build_template({**self.config, "activateServices": True})["Resources"]
        self.assertTrue(active["WorkerMapping"]["Properties"]["Enabled"])
        self.assertEqual(active["ControlSchedule"]["Properties"]["State"], "ENABLED")
        self.assertEqual([active[role + "Function"]["Properties"]["ReservedConcurrentExecutions"] for role in ["Api", "Worker", "Dispatcher", "Maintenance", "Control"]], [2, 2, 1, 1, 1])
        self.assertEqual(self.properties("WorkerMapping")["FunctionResponseTypes"], ["ReportBatchItemFailures"])
        self.assertEqual(self.properties("WorkerMapping")["BatchSize"], 1)
        self.assertEqual(active["WorkerMapping"]["Properties"]["ScalingConfig"]["MaximumConcurrency"], 2)
        self.assertGreaterEqual(self.properties("JobsQueue")["VisibilityTimeout"], 6 * self.properties("WorkerFunction")["Timeout"])
        self.assertEqual(self.properties("JobsQueue")["RedrivePolicy"]["maxReceiveCount"], 5)

    def test_queue_resource_policies_use_one_resource_per_statement_and_deny_plaintext_for_both_queues(self):
        for active in (False, True):
            resources = MODULE.build_template({**self.config, "activateServices": active})["Resources"]
            queues = {name for name, resource in resources.items() if resource["Type"] == "AWS::SQS::Queue"}
            policies = [resource["Properties"] for resource in resources.values()
                        if resource["Type"] == "AWS::SQS::QueuePolicy"]
            attached, denied = set(), []
            for policy in policies:
                targets = {queue["Ref"] for queue in policy["Queues"]}
                attached |= targets
                for statement in policy["PolicyDocument"]["Statement"]:
                    resource = statement["Resource"]
                    # SetQueueAttributes rejects a statement naming more than
                    # one resource even when the document is attached to both.
                    identities = resource if isinstance(resource, list) else [resource]
                    self.assertEqual(len(identities), 1, "AWS SQS requires one resource per statement")
                    identity = identities[0]
                    self.assertEqual(set(identity), {"Fn::GetAtt"})
                    queue, attribute = identity["Fn::GetAtt"]
                    self.assertIn(queue, targets)
                    self.assertEqual(attribute, "Arn")
                    self.assertEqual(statement["Effect"], "Deny")
                    self.assertEqual(statement["Principal"], "*")
                    self.assertEqual(statement["Action"], "sqs:*")
                    self.assertEqual(statement["Condition"], {"Bool": {"aws:SecureTransport": "false"}})
                    denied.append(queue)
            with self.subTest(active=active):
                self.assertEqual(attached, queues)
                self.assertCountEqual(denied, queues)

    def test_redeployment_explicitly_restores_controller_concurrency_after_sdk_drain(self):
        # The CLI drains actual controller concurrency to zero. CloudFormation
        # must then see a property transition when reopening, rather than an
        # unchanged 1 -> 1 template that can preserve the manually drained zero.
        before = MODULE.build_template({**self.config, "activateServices": True})["Resources"]
        stopped = MODULE.build_template({**self.config, "activateServices": False})["Resources"]
        reopened = MODULE.build_template({**self.config, "activateServices": True})["Resources"]
        counts = [stage["ControlFunction"]["Properties"]["ReservedConcurrentExecutions"]
                  for stage in [before, stopped, reopened]]
        self.assertEqual(counts, [1, 0, 1])
        self.assertEqual(stopped["ControlSchedule"]["Properties"]["State"], "DISABLED")
        self.assertEqual(reopened["ControlSchedule"]["Properties"]["State"], "ENABLED")
        self.assertTrue(all(stage["MaintenanceFunction"]["Properties"]["ReservedConcurrentExecutions"] == 1
                            for stage in [before, stopped, reopened]))

    def test_control_and_api_can_invoke_only_app_privileged_dispatcher(self):
        dispatcher = self.template["Outputs"]["DispatcherFunctionArn"]["Value"]
        admin_secret = {"Fn::GetAtt": ["Database", "MasterUserSecret.SecretArn"]}
        for role in ["Api", "Worker", "Control"]:
            grants = [row for row in self.statements(role) if row["Effect"] == "Allow" and "lambda:InvokeFunction" in row["Action"]]
            self.assertEqual(len(grants), 1)
            self.assertEqual(grants[0]["Resource"], dispatcher)
            self.assertNotIn("MasterUserSecret.SecretArn", json.dumps(self.statements(role)))
        control = self.statements("Control")
        self.assertFalse(any(any(action.startswith(prefix) for action in row["Action"] for prefix in ["s3:", "secretsmanager:", "kms:", "ec2:", "cognito-idp:"]) for row in control))
        control_env = self.properties("ControlFunction")["Environment"]["Variables"]
        self.assertNotIn("OTGD_DATABASE_HOST", control_env)
        self.assertNotIn("OTGD_DATABASE_SECRET_ARN", control_env)
        self.assertEqual(control_env["OTGD_SERVERLESS_CONTROL_ONLY"], "true")
        self.assertEqual(self.properties("DispatcherFunction")["Role"], {"Fn::GetAtt": ["WorkerRole", "Arn"]})
        self.assertEqual(self.properties("DispatcherFunction")["Environment"]["Variables"]["OTGD_LAMBDA_MAINTENANCE_ROLE"], "dispatcher")
        self.assertEqual(self.properties("MaintenanceFunction")["Environment"]["Variables"]["OTGD_LAMBDA_MAINTENANCE_ROLE"], "maintenance")
        maintenance = next(row for row in self.statements("Maintenance") if "secretsmanager:GetSecretValue" in row["Action"])
        self.assertIn(admin_secret, maintenance["Resource"])
        self.assertFalse(any("kms:Sign" in row["Action"] for role in ["Worker", "Maintenance", "Control"] for row in self.statements(role)))
        denial = next(row for row in self.statements("Worker") if row["Effect"] == "Deny" and "ec2:CreateNetworkInterface" in row["Action"])
        self.assertIn(dispatcher, denial["Condition"]["ArnEquals"]["lambda:SourceFunctionArn"])

    def test_independent_immutable_journal_and_conditional_api_uploads(self):
        journal = self.properties("DeletionJournal")
        self.assertTrue(journal["ObjectLockEnabled"])
        self.assertEqual(journal["ObjectLockConfiguration"]["Rule"]["DefaultRetention"], {"Mode": "COMPLIANCE", "Days": 90})
        self.assertNotIn("LifecycleConfiguration", journal)
        for name in ["DataKey", "JournalKey", "CaptureSigningKey", "ApplicationSecret", "TombstoneSecret", "Artifacts", "Exports", "DeletionJournal", "WebAssets", "RuntimeControl"]:
            self.assertEqual(self.resources[name]["DeletionPolicy"], "Retain")
        self.assertNotEqual(self.properties("Artifacts")["BucketEncryption"], journal["BucketEncryption"])
        policy = self.properties("DeletionJournalPolicy")["PolicyDocument"]["Statement"]
        deletion = next(row for row in policy if row["Action"] == ["s3:DeleteObject", "s3:DeleteObjectVersion"])
        self.assertEqual(deletion["Effect"], "Deny")
        self.assertEqual(deletion["Principal"]["AWS"], [{"Fn::GetAtt": [role + "Role", "Arn"]} for role in ["Api", "Worker", "Maintenance"]])
        self.assertTrue(any(row["Effect"] == "Deny" and "scope-resumptions/*" in json.dumps(row) for row in policy))
        api = self.properties("ArtifactsPolicy")["PolicyDocument"]["Statement"]
        conditional = next(row for row in api if row.get("Condition") == {"Null": {"s3:if-none-match": "true"}})
        self.assertEqual(conditional["Principal"]["AWS"], [{"Fn::GetAtt": ["ApiRole", "Arn"]}])

    def test_web_artifact_contract_and_native_monitoring_do_not_force_idle_database_queries(self):
        web = self.properties("WebDelivery")["DistributionConfig"]
        origin = web["Origins"][0]
        self.assertEqual((origin["Id"], origin["OriginPath"]), ("web", "/releases/" + self.config["releaseId"]))
        self.assertEqual(origin["OriginAccessControlId"], {"Ref": "WebOriginAccess"})
        self.assertEqual(web["DefaultCacheBehavior"]["TargetOriginId"], "web")
        oauth = self.properties("MobileClient")
        self.assertEqual(oauth["AllowedOAuthFlows"], ["code"])
        self.assertIn({"Fn::Sub": "https://${WebDelivery.DomainName}/"}, oauth["CallbackURLs"])
        alarms = [row["Properties"] for row in self.resources.values() if row["Type"] == "AWS::CloudWatch::Alarm"]
        self.assertEqual(len(alarms), 10)
        sql_metrics = [row for row in alarms if row["Namespace"] == "OTGD/serverless-development"]
        self.assertEqual({row["MetricName"] for row in sql_metrics}, {"OldestOutboxSeconds", "OldestPrivacyJobSeconds", "CleanupOverdueCount"})
        self.assertTrue(all(row["TreatMissingData"] == "notBreaching" for row in sql_metrics))
        body, bindings = self.properties("HealthDashboard")["DashboardBody"]["Fn::Sub"]
        for token, binding in bindings.items():
            body = body.replace("${" + token + "}", "bound-" + (binding.get("Ref") or "-".join(binding["Fn::GetAtt"])))
        widgets = json.loads(body)["widgets"]
        metrics = [metric for widget in widgets if widget["type"] == "metric" for metric in widget["properties"]["metrics"]]
        namespaces = {metric[0] for metric in metrics}
        self.assertTrue({"AWS/Lambda", "AWS/RDS", "AWS/SQS", "AWS/CloudFront", "OTGD/serverless-development"}.issubset(namespaces))
        self.assertNotIn("AWS/EC2", namespaces)
        self.assertNotIn("OTGD/qa", namespaces)
        self.assertTrue(all("Global" in metric for metric in metrics if metric[0] == "AWS/CloudFront"))
        self.assertEqual(self.properties("ControlSchedule")["ScheduleExpression"], "rate(1 minute)")
        self.assertEqual(self.properties("RuntimeControl")["BillingMode"], "PAY_PER_REQUEST")
        self.assertEqual(self.properties("RuntimeControl")["KeySchema"], [{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}])
        self.assertEqual(self.properties("RuntimeControl")["TimeToLiveSpecification"], {"AttributeName": "expiresAt", "Enabled": True})
        for role in ["Api", "Worker", "Maintenance", "Control"]:
            grant = next(row for row in self.statements(role) if "dynamodb:PutItem" in row["Action"])
            self.assertEqual(grant["Condition"], {"ForAllValues:StringEquals": {"dynamodb:LeadingKeys": ["runtime"]}})
        budget = self.properties("MonthlyBudget")["Budget"]
        self.assertNotIn("CostFilters", budget)

    def test_browser_upload_cors_and_csp_allow_only_deployed_web_and_artifact_bucket(self):
        artifact = self.properties("Artifacts")
        rules = artifact["CorsConfiguration"]["CorsRules"]
        self.assertEqual(len(rules), 1)
        rule = rules[0]
        self.assertEqual(rule["AllowedOrigins"], [{"Fn::Sub": "https://${WebDelivery.DomainName}"}])
        self.assertEqual(rule["AllowedMethods"], ["PUT"])
        self.assertEqual(set(rule["AllowedHeaders"]), {"Content-Type", "If-None-Match", "x-amz-checksum-sha256",
                          "x-amz-server-side-encryption", "x-amz-server-side-encryption-aws-kms-key-id"})
        self.assertEqual(set(rule["ExposedHeaders"]), {"ETag", "x-amz-version-id", "x-amz-checksum-sha256"})
        self.assertEqual(rule["MaxAge"], 300)
        self.assertNotIn("Content-Length", rule["AllowedHeaders"])
        expected = "https://s3.dualstack.us-east-2.amazonaws.com/" + artifact["BucketName"] + "/"
        self.assertEqual(self.template["Outputs"]["ArtifactUploadOrigin"]["Value"], expected)
        csp = self.properties("WebHeaders")["ResponseHeadersPolicyConfig"]["SecurityHeadersConfig"]["ContentSecurityPolicy"]["ContentSecurityPolicy"]["Fn::Sub"]
        connect = next(directive for directive in csp.split(";") if directive.strip().startswith("connect-src "))
        self.assertIn(expected, connect.split())
        self.assertNotIn("https://s3.dualstack.us-east-2.amazonaws.com", connect.split())
        self.assertNotIn("${Artifacts}", csp)
        self.assertNotIn("${Artifacts.", csp)
        for name in ["Exports", "DeletionJournal", "WebAssets"]:
            self.assertNotIn("CorsConfiguration", self.properties(name))
        # These private buckets remain protected; browser CORS grants no public
        # object access and the API signer still requires conditional creation.
        self.assertTrue(all(artifact["PublicAccessBlockConfiguration"].values()))
        self.assertTrue(any(row.get("Condition") == {"Null": {"s3:if-none-match": "true"}}
                            for row in self.properties("ArtifactsPolicy")["PolicyDocument"]["Statement"]))

    def test_all_implicit_and_explicit_resource_dependencies_are_acyclic(self):
        names = set(self.resources)

        def references(value):
            found = set()
            if isinstance(value, dict):
                if value.get("Ref") in names:
                    found.add(value["Ref"])
                if value.get("Fn::GetAtt") and value["Fn::GetAtt"][0] in names:
                    found.add(value["Fn::GetAtt"][0])
                if "Fn::Sub" in value:
                    expression = value["Fn::Sub"]
                    text = expression[0] if isinstance(expression, list) else expression
                    found |= {token.split(".")[0] for token in re.findall(r"\$\{([^}]+)\}", text) if token.split(".")[0] in names}
                for child in value.values():
                    found |= references(child)
            elif isinstance(value, list):
                for child in value:
                    found |= references(child)
            return found

        graph = {}
        for name, value in self.resources.items():
            explicit = value.get("DependsOn", [])
            graph[name] = references(value) | set([explicit] if isinstance(explicit, str) else explicit)
        visited, pending = set(), set()

        def visit(name):
            self.assertNotIn(name, pending, "CloudFormation dependency cycle")
            if name in visited:
                return
            pending.add(name)
            for child in graph[name]:
                visit(child)
            pending.remove(name)
            visited.add(name)

        for name in names:
            visit(name)

    def test_unsafe_deployment_inputs_fail_before_cloud_calls(self):
        for change in [{"account": "YOUR_ACCOUNT"}, {"region": "us-west-2"}, {"releaseId": "main"}, {"alarmEmail": "operator"},
                       {"monthlyBudgetUsd": 0}, {"monthlyBudgetUsd": 51}, {"monthlyBudgetUsd": True}, {"monthlyBudgetUsd": float("nan")},
                       {"prefix": "invalid/name"}, {"activateServices": "true"}, {"databaseEngineVersion": "16.2"},
                       {"apiImageUri": self.config["apiImageUri"].split("@")[0] + ":latest"},
                       {"workerImageUri": self.config["workerImageUri"].replace("123456789012", "987654321098")}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                MODULE.build_template({**self.config, **change})


if __name__ == "__main__":
    unittest.main()
