import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("development_template", ROOT / "deploy/development_template.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DevelopmentTemplateTest(unittest.TestCase):
    def setUp(self):
        self.config = {"account": "123456789012", "region": "us-east-2", "releaseId": "a" * 40,
                       "alarmEmail": "operator@otgd.test", "monthlyBudgetUsd": 50}
        self.template = MODULE.build_template(self.config)
        self.resources = self.template["Resources"]

    def properties(self, name):
        return self.resources[name]["Properties"]

    def test_private_origin_has_explicit_small_nat_path_and_no_alb_or_gateway_fees(self):
        kinds = [value["Type"] for value in self.resources.values()]
        self.assertEqual(kinds.count("AWS::EC2::Instance"), 2)
        self.assertNotIn("AWS::EC2::NatGateway", kinds)
        self.assertFalse(any("LoadBalancing" in value or "ApiGateway" in value or "RDS" in value for value in kinds))
        app, nat = self.properties("AppInstance"), self.properties("NatInstance")
        self.assertEqual(app["InstanceType"], "t3a.medium")
        self.assertEqual(nat["InstanceType"], "t4g.nano")
        self.assertFalse(nat["SourceDestCheck"])
        self.assertEqual(app["NetworkInterfaces"][0]["SubnetId"], {"Ref": "PrivateSubnet"})
        self.assertFalse(app["NetworkInterfaces"][0]["AssociatePublicIpAddress"])
        self.assertFalse(self.properties("PrivateSubnet")["MapPublicIpOnLaunch"])
        self.assertEqual(self.properties("PrivateInternetRoute")["InstanceId"], {"Ref": "NatInstance"})
        self.assertEqual(self.properties("PublicInternetRoute")["GatewayId"], {"Ref": "InternetGateway"})
        self.assertEqual(self.properties("NatAddressAssociation")["InstanceId"], {"Ref": "NatInstance"})
        for host in [app, nat]:
            self.assertFalse(host["Monitoring"])
            self.assertEqual(host["MetadataOptions"]["HttpTokens"], "required")
            self.assertEqual(host["CreditSpecification"], {"CPUCredits": "standard"})
            self.assertTrue(host["BlockDeviceMappings"][0]["Ebs"]["Encrypted"])
        self.assertFalse(app["BlockDeviceMappings"][0]["Ebs"]["DeleteOnTermination"])
        self.assertNotIn("SecurityGroupIngress", self.properties("AppSecurityGroup"))
        for rule in self.properties("NatSecurityGroup")["SecurityGroupIngress"]:
            self.assertEqual(rule["CidrIp"], "10.74.1.0/24")
            self.assertIn(rule["FromPort"], [80, 443])
            self.assertEqual(rule["ToPort"], rule["FromPort"])
        script = nat["UserData"]["Fn::Base64"]
        for required in ["net.ipv4.ip_forward=1", "MASQUERADE", "iptables-save", "systemctl enable iptables"]:
            self.assertIn(required, script)
        self.assertIn("seq 1 30", script)
        self.assertIn("command -v iptables", script)
        self.assertEqual(self.template["Outputs"]["ApplicationSecurityGroupId"]["Value"], {"Ref": "AppSecurityGroup"})

    def test_generated_https_api_uses_private_origin_and_preserves_authenticated_streaming(self):
        endpoint = self.properties("ApiVpcOrigin")["VpcOriginEndpointConfig"]
        self.assertEqual(endpoint["HTTPPort"], 8000)
        self.assertEqual(endpoint["OriginProtocolPolicy"], "http-only")
        self.assertIn("${AppInstance}", endpoint["Arn"]["Fn::Sub"])
        distribution = self.properties("ApiDelivery")["DistributionConfig"]
        self.assertEqual(distribution["ViewerCertificate"], {"CloudFrontDefaultCertificate": True})
        self.assertNotIn("Aliases", distribution)
        self.assertEqual(distribution["Origins"][0]["DomainName"], {"Fn::GetAtt": ["AppInstance", "PrivateDnsName"]})
        self.assertEqual(distribution["Origins"][0]["VpcOriginConfig"]["VpcOriginId"], {"Fn::GetAtt": ["ApiVpcOrigin", "Id"]})
        behavior = distribution["DefaultCacheBehavior"]
        self.assertEqual(behavior["ViewerProtocolPolicy"], "redirect-to-https")
        self.assertEqual(set(behavior["AllowedMethods"]), {"GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"})
        self.assertEqual(behavior["CachePolicyId"], "4135ea2d-6df8-44a3-9df3-4b5a84be39ad")
        # AWS's AllViewerExceptHostHeader policy forwards Authorization, current
        # generation/idempotency headers and query strings to the authenticated API.
        self.assertEqual(behavior["OriginRequestPolicyId"], "b689b0a8-53d0-40ab-baf2-68738e2966ac")
        self.assertEqual(self.template["Outputs"]["ApiOrigin"]["Value"], {"Fn::Sub": "https://${ApiDelivery.DomainName}"})

    def test_independent_journal_and_runtime_seed_remain_private_and_retained(self):
        for name in ["DataKey", "JournalKey", "CaptureSigningKey", "RuntimeSecret", "Artifacts", "Exports", "DeletionJournal", "WebAssets", "DeploymentAssets"]:
            self.assertEqual(self.resources[name]["DeletionPolicy"], "Retain")
            self.assertEqual(self.resources[name]["UpdateReplacePolicy"], "Retain")
        buckets = [name for name, value in self.resources.items() if value["Type"] == "AWS::S3::Bucket"]
        self.assertEqual(len(buckets), 5)
        for name in buckets:
            properties = self.properties(name)
            self.assertEqual(properties["VersioningConfiguration"]["Status"], "Enabled")
            self.assertTrue(all(properties["PublicAccessBlockConfiguration"].values()))
        self.assertTrue(self.properties("DeletionJournal")["ObjectLockEnabled"])
        self.assertEqual(self.properties("DeletionJournal")["ObjectLockConfiguration"]["Rule"]["DefaultRetention"], {"Mode": "COMPLIANCE", "Days": 90})
        data = self.properties("Artifacts")["BucketEncryption"]
        journal = self.properties("DeletionJournal")["BucketEncryption"]
        self.assertNotEqual(data, journal)
        self.assertNotIn("LifecycleConfiguration", self.properties("DeletionJournal"))
        statements = self.properties("DeletionJournalPolicy")["PolicyDocument"]["Statement"]
        self.assertTrue(any(row.get("Principal") == {"AWS": {"Fn::GetAtt": ["AppRole", "Arn"]}}
                            and row["Action"] == ["s3:DeleteObject", "s3:DeleteObjectVersion"] and row["Effect"] == "Deny" for row in statements))
        self.assertTrue(any(row.get("Effect") == "Deny" and "scope-resumptions/*" in json.dumps(row) for row in statements))
        self.assertTrue(any(row.get("Condition") == {"Null": {"s3:if-none-match": "true"}} for row in statements))
        for row in statements:
            if "s3:if-none-match" in json.dumps(row):
                self.assertEqual(row["Resource"], {"Fn::Sub": ["${Arn}/*", {"Arn": {"Fn::GetAtt": ["DeletionJournal", "Arn"]}}]})
        seed = self.properties("RuntimeSecret")["GenerateSecretString"]
        self.assertEqual(seed["GenerateStringKey"], "seed")
        self.assertEqual(seed["PasswordLength"], 64)
        self.assertTrue(seed["ExcludePunctuation"] and seed["ExcludeUppercase"])
        self.assertEqual(seed["ExcludeCharacters"], "ghijklmnopqrstuvwxyz")
        signing = self.properties("CaptureSigningKey")
        self.assertEqual(signing["KeySpec"], "ECC_NIST_P256")
        self.assertEqual(signing["KeyUsage"], "SIGN_VERIFY")
        backup_rules = self.properties("DeploymentAssets")["LifecycleConfiguration"]["Rules"]
        self.assertEqual(backup_rules[0]["Prefix"], "backups/otgd-development/")
        self.assertEqual(backup_rules[0]["ExpirationInDays"], 7)
        self.assertEqual(backup_rules[0]["NoncurrentVersionExpiration"]["NoncurrentDays"], 7)
        permissions = self.properties("AppRole")["Policies"][0]["PolicyDocument"]["Statement"]
        self.assertTrue(any("s3:GetObjectRetention" in row["Action"] and row["Resource"] == {"Fn::Sub": ["${Arn}/*", {"Arn": {"Fn::GetAtt": ["DeletionJournal", "Arn"]}}]} for row in permissions))
        self.assertTrue(any(row["Action"] == ["s3:GetObject", "s3:GetObjectVersion"] and "${Arn}/runtime/*" in json.dumps(row) for row in permissions))
        self.assertTrue(any(row["Action"] == ["s3:PutObject"] and "${Arn}/backups/otgd-development/*" in json.dumps(row) for row in permissions))

    def test_web_publishing_and_cognito_callbacks_bind_same_aws_generated_domain(self):
        web = self.properties("WebDelivery")["DistributionConfig"]
        origin = web["Origins"][0]
        self.assertEqual(origin["Id"], "web")
        self.assertEqual(origin["OriginPath"], "/releases/" + self.config["releaseId"])
        self.assertEqual(origin["OriginAccessControlId"], {"Ref": "WebOriginAccess"})
        self.assertEqual(web["DefaultCacheBehavior"]["TargetOriginId"], "web")
        self.assertEqual(self.template["Outputs"]["WebReleasePrefix"]["Value"], "releases/" + self.config["releaseId"])
        oauth = self.properties("MobileClient")
        self.assertFalse(oauth["GenerateSecret"])
        self.assertEqual(oauth["AllowedOAuthFlows"], ["code"])
        self.assertIn({"Fn::Sub": "https://${WebDelivery.DomainName}/"}, oauth["CallbackURLs"])
        self.assertIn({"Fn::Sub": "https://${WebDelivery.DomainName}/"}, oauth["LogoutURLs"])
        policy = self.properties("WebAssetsPolicy")["PolicyDocument"]["Statement"]
        allow = next(row for row in policy if row["Effect"] == "Allow")
        self.assertEqual(allow["Principal"], {"Service": "cloudfront.amazonaws.com"})
        self.assertIn("${WebDelivery}", allow["Condition"]["StringEquals"]["AWS:SourceArn"]["Fn::Sub"])

    def test_health_uses_only_published_metrics_with_missing_worker_detection(self):
        alarms = [row for row in self.resources.values() if row["Type"] == "AWS::CloudWatch::Alarm"]
        self.assertEqual(len(alarms), 10)
        missing = self.properties("MissingWorkerMetrics")
        self.assertEqual(missing["Namespace"], "OTGD/qa")
        self.assertEqual(missing["MetricName"], "OldestOutboxSeconds")
        self.assertEqual(missing["TreatMissingData"], "breaching")
        self.assertEqual(missing["ComparisonOperator"], "LessThanThreshold")
        self.assertEqual((missing["Threshold"], missing["Period"], missing["EvaluationPeriods"]), (0, 60, 5))
        for name in ["HostMemoryPressure", "HostDiskPressure"]:
            properties = self.properties(name)
            self.assertEqual(properties["Namespace"], "OTGD/development")
            self.assertEqual(properties["Dimensions"], [{"Name": "InstanceId", "Value": {"Ref": "AppInstance"}}])
            self.assertEqual(properties["Period"], 300)
        body, tokens = self.properties("HealthDashboard")["DashboardBody"]["Fn::Sub"]
        for name, binding in tokens.items():
            body = body.replace("${" + name + "}", "bound-" + (binding.get("Ref") or "-".join(binding["Fn::GetAtt"])))
        widgets = json.loads(body)["widgets"]
        self.assertEqual(len(next(row for row in widgets if row["type"] == "alarm")["properties"]["alarms"]), 10)
        for row in widgets:
            if row["type"] == "metric" and any(metric[0] == "AWS/CloudFront" for metric in row["properties"]["metrics"]):
                self.assertEqual(row["properties"]["region"], "us-east-1")
                self.assertTrue(all("Global" in metric for metric in row["properties"]["metrics"]))
        permissions = self.properties("AppRole")["Policies"][0]["PolicyDocument"]["Statement"]
        metric_grant = next(row for row in permissions if row["Action"] == ["cloudwatch:PutMetricData"])
        self.assertEqual(metric_grant["Condition"]["StringEquals"]["cloudwatch:namespace"], ["OTGD/qa", "OTGD/development"])
        self.assertFalse(any("ecs:*" in json.dumps(row) or '"Action": "*"' in json.dumps(row) for row in permissions))
        budget = self.properties("MonthlyBudget")["Budget"]
        self.assertNotIn("CostFilters", budget)
        self.assertEqual(budget["BudgetLimit"], {"Amount": 50, "Unit": "USD"})
        sns_publish = self.properties("NotificationPolicy")["PolicyDocument"]["Statement"][0]
        self.assertEqual(sns_publish["Principal"], {"Service": "cloudwatch.amazonaws.com"})
        self.assertEqual(sns_publish["Condition"]["StringEquals"]["aws:SourceAccount"], self.config["account"])

    def test_resource_dependencies_have_no_cycles_and_template_fits_inline_api(self):
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
            depends = value.get("DependsOn", [])
            if isinstance(depends, str):
                depends = [depends]
            graph[name] = references(value) | set(depends)
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
        self.assertLessEqual(len(json.dumps(self.template, separators=(",", ":")).encode()), 51200)

    def test_invalid_inputs_fail_before_cloud_mutation(self):
        for change in [{"account": "YOUR_ACCOUNT"}, {"region": "us-west-2"}, {"releaseId": "main"},
                       {"alarmEmail": "operator"}, {"monthlyBudgetUsd": 0}, {"monthlyBudgetUsd": 51},
                       {"monthlyBudgetUsd": True}, {"prefix": "invalid/name"}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                MODULE.build_template({**self.config, **change})


if __name__ == "__main__":
    unittest.main()
