"""Deployment guards around real DTOs, source gates and ECS completion evidence."""
from contextlib import ExitStack
import ast
from copy import deepcopy
import importlib.util
import io
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import botocore.session
import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("fargate_deploy", ROOT / "deploy/fargate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ACCOUNT = "123456789012"
PREFIX = "otgd-serverless-development"
ECS = f"arn:aws:ecs:us-east-2:{ACCOUNT}:"
SOURCE = "a" * 40


class FargateDeployTest(unittest.TestCase):
    def setUp(self):
        self.config = {"environment": "fargate-development", "account": ACCOUNT,
            "region": "us-east-2", "alarmEmail": "operator@otgd.test", "monthlyBudgetUsd": 100,
            "releaseId": SOURCE, "plannedMonthlyUsers": 10,
            "costEstimatePath": "infra/costs/fargate-estimate.json"}
        self.images = {key: f"{ACCOUNT}.dkr.ecr.us-east-2.amazonaws.com/{PREFIX}@sha256:" + digit * 64
            for key, digit in (("apiImageUri", "a"), ("workerImageUri", "b"), ("uiImageUri", "c"))}
        self.out = {"ReleaseId": SOURCE, "ActivateServices": "true", "ClusterArn": ECS + "cluster/" + PREFIX,
            "ApiService": ECS + "service/" + PREFIX + "/" + PREFIX + "-api",
            "ApiTaskDefinition": ECS + "task-definition/" + PREFIX + "-api:2",
            "WorkerTaskDefinition": ECS + "task-definition/" + PREFIX + "-worker:2",
            "MaintenanceTaskDefinition": ECS + "task-definition/" + PREFIX + "-maintenance:2",
            "ApiImageUri": self.images["apiImageUri"], "WorkerImageUri": self.images["workerImageUri"],
            "UiImageUri": self.images["uiImageUri"], "TargetGroupArn": "owned-target-group",
            "DatabaseClusterIdentifier": PREFIX, "ApiOrigin": "https://api.cloudfront.net",
            "WebOrigin": "https://web.cloudfront.net", "Issuer": "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_owned",
            "ClientId": "owned-client", "CloudWatchDashboardUrl": "https://us-east-2.console.aws.amazon.com/cloudwatch/owned",
            "TaskSubnets": '["subnet-12345678","subnet-87654321"]', "TaskSecurityGroups": '["sg-12345678"]',
            "DeploymentBucket": f"{PREFIX}-{ACCOUNT}-us-east-2-deployments"}
        self.task_arn = ECS + "task/" + PREFIX + "/" + "d" * 32

    def test_plan_reconciles_official_prices_without_constructing_an_aws_session(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(self.config))
            stdout = io.StringIO()
            with patch.object(MODULE.platform, "CloudSession") as session, patch("sys.stdout", stdout):
                code = MODULE.main(["plan", "--config", str(path)])
            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertFalse(result["deployment_executed"])
            self.assertEqual(result["application_lambda_functions"], 0)
            self.assertLess(result["budget_plan"]["estimated_monthly_usd"], 100)
            self.assertLess(result["budget_plan"]["maximum_capacity_stress_monthly_usd"], 100)
            session.assert_not_called()

    def test_budget_blocks_old_cap_and_rejects_understated_always_on_service(self):
        with self.assertRaises(MODULE.Gate):
            MODULE.budget({**self.config, "monthlyBudgetUsd": 50})
        original = json.loads((ROOT / self.config["costEstimatePath"]).read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prices.json"
            for key, value in (("service_memory_gb", 0.5), ("service_desired_count", 0),
                               ("worker_memory_gb", 1), ("recurring_privacy_cleanup_interval_seconds", 3600)):
                evidence = deepcopy(original)
                evidence["selected_scenario_assumptions"][key] = value
                path.write_text(json.dumps(evidence))
                with self.subTest(key=key), self.assertRaises(MODULE.Gate):
                    MODULE.budget({**self.config, "costEstimatePath": str(path)})

    def test_selected_and_maximum_capacity_prices_both_require_reconciled_line_items(self):
        original = json.loads((ROOT / self.config["costEstimatePath"]).read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prices.json"
            for collection in ("scenarios", "configured_maximum_1_acu_stress_scenarios"):
                evidence = deepcopy(original)
                case = next(row for row in evidence[collection] if row["monthly_active_users"] == 10)
                case["items"][0]["quantity"] += 100
                path.write_text(json.dumps(evidence))
                with self.subTest(collection=collection), self.assertRaises(MODULE.Gate):
                    MODULE.budget({**self.config, "costEstimatePath": str(path)})

    def test_configuration_never_accepts_credentials_or_another_deployment_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            for override in ({"environment": "serverless-development"}, {"account": "not-account"},
                             {"region": "us-west-2"}, {"monthlyBudgetUsd": 101}, {"monthlyBudgetUsd": True},
                             {"plannedMonthlyUsers": 100}, {"releaseId": "main"},
                             {"AWS_SECRET_ACCESS_KEY": "synthetic-test-value"}):
                path.write_text(json.dumps({**self.config, **override}))
                with self.subTest(override=override), self.assertRaises(MODULE.Gate):
                    MODULE.read_config(path)

    def test_exact_source_and_gate_failure_precede_any_aws_client_access(self):
        args = SimpleNamespace(gate_evidence=Path("reviewed.json"))
        aws = Mock()
        with patch.object(MODULE.platform, "require_clean_source") as source, patch.object(
                MODULE.platform, "verify_gate_file", side_effect=MODULE.Gate("unreviewed source")) as gate:
            with self.assertRaises(MODULE.Gate):
                MODULE.deploy(args, self.config, aws, {})
        source.assert_called_once_with(SOURCE)
        gate.assert_called_once_with(args.gate_evidence, SOURCE)
        aws.client.assert_not_called()
        with self.assertRaises(MODULE.Gate):
            MODULE.deploy(SimpleNamespace(gate_evidence=None), self.config, aws, {})
        aws.client.assert_not_called()

    def test_actual_sdk_has_all_paginators_used_for_budget_and_runtime_inspection(self):
        loader = botocore.session.get_session().get_component("data_loader")
        for service, operations in {
            "budgets": ("DescribeNotificationsForBudget", "DescribeSubscribersForNotification"),
            "ecs": ("ListTasks",), "cloudformation": ("ListStackResources",),
            "sns": ("ListSubscriptionsByTopic",),
            "rds": ("DescribeDBEngineVersions", "DescribeOrderableDBInstanceOptions"),
        }.items():
            actual = loader.load_service_model(service, "paginators-1")["pagination"]
            self.assertTrue(set(operations).issubset(actual), service)

    def test_network_rejects_duplicate_invalid_and_public_network_metadata(self):
        self.assertEqual(MODULE.network(self.out)["awsvpcConfiguration"]["assignPublicIp"], "DISABLED")
        for override in ({"TaskSubnets": '["subnet-12345678","subnet-12345678"]'},
                         {"TaskSecurityGroups": '["sg-12345678","sg-12345678"]'},
                         {"TaskSubnets": '["another-account-host"]'}, {"TaskSecurityGroups": '[]'}):
            with self.subTest(override=override), self.assertRaises(MODULE.Gate):
                MODULE.network({**self.out, **override})

    def _task_definition(self, name, image, *, source=SOURCE):
        return {"networkMode": "awsvpc", "runtimePlatform": {"cpuArchitecture": "X86_64"},
                "containerDefinitions": [{"name": name, "image": MODULE.dualstack_image(image),
                    "user": "10001", "readonlyRootFilesystem": True,
                    "environment": [{"name": "OTGD_SOURCE_REVISION", "value": source}]}]}

    def test_task_definition_rejects_wrong_source_image_inventory_and_writable_root(self):
        ecs = Mock()
        aws = SimpleNamespace(client=lambda name: ecs)
        expected = {"worker": self.images["workerImageUri"]}
        valid = self._task_definition("worker", self.images["workerImageUri"])
        ecs.describe_task_definition.return_value = {"taskDefinition": valid}
        self.assertEqual(MODULE.task_definition(aws, self.config, "owned-task", expected), valid)
        invalid = []
        wrong_source = deepcopy(valid)
        wrong_source["containerDefinitions"][0]["environment"][0]["value"] = "b" * 40
        invalid.append(wrong_source)
        wrong_image = deepcopy(valid)
        wrong_image["containerDefinitions"][0]["image"] = MODULE.dualstack_image(self.images["apiImageUri"])
        invalid.append(wrong_image)
        writable = deepcopy(valid)
        writable["containerDefinitions"][0]["readonlyRootFilesystem"] = False
        invalid.append(writable)
        extra = deepcopy(valid)
        extra["containerDefinitions"].append({"name": "unreviewed"})
        invalid.append(extra)
        for row in invalid:
            ecs.describe_task_definition.return_value = {"taskDefinition": row}
            with self.subTest(row=row), self.assertRaises(MODULE.Gate):
                MODULE.task_definition(aws, self.config, "owned-task", expected)

    def _maintenance_clients(self, receipt, *, exit_code=0, digest=None):
        ecs, s3 = Mock(), Mock()
        ecs.describe_task_definition.return_value = {"taskDefinition": self._task_definition("maintenance", self.images["workerImageUri"])}
        ecs.run_task.return_value = {"tasks": [{"taskArn": self.task_arn}], "failures": []}
        ecs.describe_tasks.return_value = {"tasks": [{"taskDefinitionArn": self.out["MaintenanceTaskDefinition"],
            "lastStatus": "STOPPED", "containers": [{"name": "maintenance", "exitCode": exit_code,
                "imageDigest": digest or self.images["workerImageUri"].split("@")[1]}]}], "failures": []}
        s3.get_object.return_value = {"Body": io.BytesIO(json.dumps(receipt).encode())}
        return SimpleNamespace(client=lambda name: {"ecs": ecs, "s3": s3}[name]), ecs, s3

    def _maintenance_receipt(self):
        return {"schema_version": "1.0.0", "operation": "bootstrap", "status": "passed",
                "task_arn": self.task_arn, "source_revision": SOURCE}

    def test_maintenance_requires_actual_zero_exit_reviewed_digest_and_source_bound_receipt(self):
        aws, ecs, _ = self._maintenance_clients(self._maintenance_receipt())
        with tempfile.TemporaryDirectory() as directory:
            result = MODULE.run_maintenance(aws, {**self.config, **self.images}, self.out, "bootstrap",
                                            Path(directory), establish_new=True)
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["task_arn"], self.task_arn)
            launch = ecs.run_task.call_args.kwargs
            self.assertEqual(launch["networkConfiguration"]["awsvpcConfiguration"]["assignPublicIp"], "DISABLED")
            self.assertEqual(launch["overrides"]["containerOverrides"][0]["name"], "maintenance")
            self.assertIn("--establish-new", launch["overrides"]["containerOverrides"][0]["command"])
            self.assertTrue((Path(directory) / "bootstrap.json").is_file())
        for change in ({"source_revision": "b" * 40}, {"task_arn": ECS + "task/unowned/" + "d" * 32},
                       {"operation": "admission"}, {"status": "failed"}):
            aws, _, _ = self._maintenance_clients({**self._maintenance_receipt(), **change})
            with tempfile.TemporaryDirectory() as directory, self.subTest(change=change), self.assertRaises(MODULE.Gate):
                MODULE.run_maintenance(aws, {**self.config, **self.images}, self.out, "bootstrap", Path(directory))
        for code, digest in ((1, None), (0, "sha256:" + "f" * 64)):
            aws, _, s3 = self._maintenance_clients(self._maintenance_receipt(), exit_code=code, digest=digest)
            with tempfile.TemporaryDirectory() as directory, self.assertRaises(MODULE.Gate):
                MODULE.run_maintenance(aws, {**self.config, **self.images}, self.out, "bootstrap", Path(directory))
            s3.get_object.assert_not_called()

    def test_establish_new_is_never_forwarded_to_migration_or_admission(self):
        aws, ecs, _ = self._maintenance_clients(self._maintenance_receipt())
        with tempfile.TemporaryDirectory() as directory:
            for operation in ("migrate", "admission"):
                with self.subTest(operation=operation), self.assertRaises(MODULE.Gate):
                    MODULE.run_maintenance(aws, {**self.config, **self.images}, self.out, operation,
                                           Path(directory), establish_new=True)
        ecs.run_task.assert_not_called()

    def _actual_app_config(self):
        from otgd.domain import notice
        settings = SimpleNamespace(identity_origin="https://owned.auth.us-east-2.amazoncognito.com",
            environment="qa", maintenance=False, minimum_app_version="0.2.0", supported_app_versions=["0.2.0"],
            issuer=self.out["Issuer"], client_id=self.out["ClientId"], oauth_redirect_uris=[self.out["WebOrigin"] + "/"])
        # Execute the real endpoint body while avoiding unrelated ASGI startup
        # settings/credentials. The DTO contents are never copied into the test.
        source = ast.parse((ROOT / "services/api/otgd/main.py").read_text())
        function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "app_config")
        function.decorator_list = []
        namespace = {"settings": lambda: settings, "notice": notice}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual-app-config-endpoint", "exec"), namespace)
        return namespace["app_config"]()

    def _observation(self, app_config, *, task_definition=None, cluster=None):
        ecs, elb, rds = Mock(), Mock(), Mock()
        ecs.describe_services.return_value = {"services": [{"status": "ACTIVE", "desiredCount": 1,
            "runningCount": 1, "pendingCount": 0, "taskDefinition": self.out["ApiTaskDefinition"]}], "failures": []}
        ecs.get_paginator.return_value.paginate.return_value = [{"taskArns": [self.task_arn]}]
        images = {"api": self.images["apiImageUri"], "ui": self.images["uiImageUri"], "controller": self.images["workerImageUri"]}
        ecs.describe_tasks.return_value = {"tasks": [{"lastStatus": "RUNNING", "healthStatus": "HEALTHY",
            "taskDefinitionArn": task_definition or self.out["ApiTaskDefinition"],
            "clusterArn": cluster or self.out["ClusterArn"],
            "containers": [{"name": name, "lastStatus": "RUNNING", "imageDigest": image.split("@")[1]} for name, image in images.items()]}]}
        elb.describe_target_health.return_value = {"TargetHealthDescriptions": [{"TargetHealth": {"State": "healthy"}}]}
        rds.describe_db_clusters.return_value = {"DBClusters": [{"Status": "available", "NetworkType": "DUAL"}]}
        aws = SimpleNamespace(client=lambda name: {"ecs": ecs, "elbv2": elb, "rds": rds}[name])
        real_client = httpx.Client
        def response(request):
            return httpx.Response(200, json=app_config if request.url.path == "/v1/app-config" else {"status": "ready"})
        with ExitStack() as stack:
            stack.enter_context(patch.object(MODULE, "task_definition"))
            stack.enter_context(patch.object(MODULE, "verify_origin"))
            stack.enter_context(patch.object(MODULE, "alarm_and_budget_metadata", return_value={"alarm_states": {"owned": "OK"}}))
            stack.enter_context(patch.object(MODULE.httpx, "Client", side_effect=lambda **kwargs:
                real_client(transport=httpx.MockTransport(response), **kwargs)))
            return MODULE.observe(aws, self.config, self.out)

    def test_actual_app_config_dto_passes_auth_identity_and_rejects_wrong_client_or_old_oauth_key(self):
        actual = self._actual_app_config()
        self.assertIn("auth", actual)
        self.assertNotIn("oauth", actual)
        result = self._observation(actual)
        self.assertEqual(result["status"], "healthy")
        self.assertTrue(result["app_config_verified"])
        for change in ({"auth": {**actual["auth"], "client_id": "unowned-client"}},
                       {"environment": "prod"}, {"inference_available": True}):
            result = self._observation({**actual, **change})
            self.assertEqual(result["status"], "degraded")
            self.assertFalse(result["app_config_verified"])
        old = {**actual, "oauth": actual["auth"]}
        old.pop("auth")
        self.assertFalse(self._observation(old)["app_config_verified"])

    def test_old_generation_or_unowned_cluster_task_cannot_prove_current_release_health(self):
        config = self._actual_app_config()
        for kwargs in ({"task_definition": self.out["ApiTaskDefinition"].replace(":2", ":1")},
                       {"cluster": ECS + "cluster/company-generation"}):
            with self.subTest(kwargs=kwargs):
                result = self._observation(config, **kwargs)
                self.assertEqual(result["status"], "degraded")
                self.assertFalse(result["ecs_containers_running"])

    def test_database_admission_requires_actual_ipv6_capacity_retention_and_dns(self):
        rds = Mock()
        aws = SimpleNamespace(client=lambda name: rds)
        row = {"NetworkType": "DUAL", "Status": "available", "DBSubnetGroup": "owned-subnets",
               "Endpoint": "owned.rds.amazonaws.com", "StorageEncrypted": True, "DeletionProtection": True,
               "ServerlessV2ScalingConfiguration": {"MinCapacity": 0, "MaxCapacity": 1, "SecondsUntilAutoPause": 300}}
        rds.describe_db_clusters.return_value = {"DBClusters": [row]}
        rds.describe_db_subnet_groups.return_value = {"DBSubnetGroups": [{"SupportedNetworkTypes": ["IPV4", "DUAL"]}]}
        with patch.object(MODULE.socket, "getaddrinfo", return_value=[("actual-AAAA",)]):
            self.assertTrue(MODULE.database_network(aws, self.out)["ipv6_dns_verified"])
        for change in ({"NetworkType": "IPV4"}, {"StorageEncrypted": False}, {"DeletionProtection": False},
                       {"ServerlessV2ScalingConfiguration": {"MinCapacity": 0.5, "MaxCapacity": 1, "SecondsUntilAutoPause": 300}}):
            rds.describe_db_clusters.return_value = {"DBClusters": [{**row, **change}]}
            with self.subTest(change=change), self.assertRaises(MODULE.Gate):
                MODULE.database_network(aws, self.out)
        rds.describe_db_clusters.return_value = {"DBClusters": [row]}
        with patch.object(MODULE.socket, "getaddrinfo", side_effect=MODULE.socket.gaierror), patch.object(
                MODULE.time, "monotonic", side_effect=[0, 0, 601]), patch.object(MODULE.time, "sleep"):
            with self.assertRaises(MODULE.Gate):
                MODULE.database_network(aws, self.out)

    def test_ui_image_reuse_requires_the_exported_artifact_binding(self):
        ecr, aws = Mock(), Mock()
        aws.client.return_value = ecr
        manifest = json.dumps({"mediaType": "application/vnd.oci.image.manifest.v1+json", "config": {}, "layers": []})
        digest = "sha256:" + hashlib.sha256(manifest.encode()).hexdigest()
        ecr.describe_images.return_value = {"imageDetails": [{"imageDigest": digest}]}
        ecr.batch_get_image.return_value = {"images": [{"imageManifest": manifest}]}
        registry = {"RepositoryName": PREFIX, "RepositoryUri": self.images["uiImageUri"].split("@")[0]}
        labels = {"org.opencontainers.image.revision": SOURCE, "org.opencontainers.image.ui-sha256": "d" * 64}
        actual = {"Architecture": "amd64", "Os": "linux", "Config": {"Labels": labels}}
        with self.assertRaises(MODULE.Gate):
            MODULE.image(aws, self.config, registry, ROOT, "ui")
        aws.client.assert_not_called()
        with patch.object(MODULE.platform, "run", return_value=json.dumps([actual])):
            uri = MODULE.image(aws, self.config, registry, ROOT, "ui", binding="d" * 64)
            self.assertEqual(uri, registry["RepositoryUri"] + "@" + digest)
            self.assertEqual(ecr.describe_images.call_args.kwargs["imageIds"], [{"imageTag": "ui-" + SOURCE + "-" + "d" * 64}])
            with self.assertRaises(MODULE.Gate):
                MODULE.image(aws, self.config, registry, ROOT, "ui", binding="e" * 64)

    def test_logging_receipt_requires_owned_streams_and_actual_api_event_delivery(self):
        ecs, logs = Mock(), Mock()
        ecs.get_paginator.return_value.paginate.return_value = [{"taskArns": [self.task_arn]}]
        logs.describe_log_streams.side_effect = lambda **kw: {"logStreams": [{"logStreamName": kw["logStreamNamePrefix"]}]}
        logs.get_log_events.return_value = {"events": [{"message": "private-event-must-never-enter-receipt"}]}
        aws = SimpleNamespace(client=lambda name: {"ecs": ecs, "logs": logs}[name])
        out = {**self.out, "ApiLogGroup": "owned-api", "UiLogGroup": "owned-ui", "ControlLogGroup": "owned-controller"}
        result = MODULE.container_logs(aws, out)
        self.assertTrue(result["api_log_delivery_verified"])
        self.assertNotIn("private-event", json.dumps(result))
        logs.get_log_events.return_value = {"events": []}
        with self.assertRaises(MODULE.Gate):
            MODULE.container_logs(aws, out)
        logs.get_log_events.return_value = {"events": [{"message": "private"}]}
        logs.describe_log_streams.side_effect = lambda **kw: {"logStreams": []}
        with self.assertRaises(MODULE.Gate):
            MODULE.container_logs(aws, out)


if __name__ == "__main__":
    unittest.main()
