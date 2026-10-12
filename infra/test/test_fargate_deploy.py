"""Deployment guards around real DTOs, source gates and ECS completion evidence."""
from contextlib import ExitStack
import ast
from copy import deepcopy
from datetime import datetime, timezone
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

    def _continuation_args(self, **changes):
        return SimpleNamespace(**{"gate_evidence": Path("reviewed.json"), "establish_new": True,
            "continue_uninitialized": Path("continuation.json"), "continue_uninitialized_sha256": "d" * 64,
            "recovery_manifest": None, "recovery_archive": None, "recovery_run_id": None,
            "recovery_artifact_id": None, **changes})

    def test_continuation_cli_rejects_incomplete_conflicting_and_nondeploy_flags_before_config_or_aws(self):
        bundle = ["--continue-uninitialized", "continuation.json", "--continue-uninitialized-sha256", "d" * 64]
        legacy = ["--recovery-manifest", "original.json", "--recovery-archive", "artifact.zip",
                  "--recovery-run-id", "123", "--recovery-artifact-id", "456"]
        invalid = [("deploy", ["--continue-uninitialized", "continuation.json", "--establish-new"]),
                   ("deploy", ["--continue-uninitialized-sha256", "d" * 64, "--establish-new"]),
                   ("deploy", bundle),
                   ("deploy", ["--continue-uninitialized", "continuation.json",
                               "--continue-uninitialized-sha256", "invalid", "--establish-new"]),
                   ("deploy", [*legacy, "--establish-new", *bundle])]
        invalid += [("deploy", [*bundle, "--establish-new", *legacy[index:index + 2]])
                    for index in range(0, len(legacy), 2)]
        invalid += [(operation, [*options, "--establish-new"])
                    for operation in ("plan", "health") for options in (bundle, legacy)]
        for operation, options in invalid:
            with self.subTest(operation=operation, options=options), \
                    patch.object(MODULE, "read_config") as read, \
                    patch.object(MODULE.platform, "CloudSession") as session, patch("sys.stderr", io.StringIO()):
                self.assertEqual(MODULE.main([operation, "--config", "not-read.json", *options]), 2)
            read.assert_not_called()
            session.assert_not_called()

    def test_direct_continuation_admits_source_then_rejects_invalid_options_before_aws(self):
        invalid = [{"continue_uninitialized": None}, {"continue_uninitialized_sha256": None},
                   {"continue_uninitialized_sha256": "invalid"}, {"establish_new": False}]
        invalid += [{field: value} for field, value in (("recovery_manifest", Path("original.json")),
                    ("recovery_archive", Path("artifact.zip")), ("recovery_run_id", 123),
                    ("recovery_artifact_id", 456))]
        for changes in invalid:
            aws, args = Mock(), self._continuation_args(**changes)
            with self.subTest(changes=changes), \
                    patch.object(MODULE.platform, "require_clean_source") as clean, \
                    patch.object(MODULE.platform, "verify_gate_file") as gates, \
                    patch("deploy.serverless_recovery.uninitialized_continuation_plan") as plan, \
                    patch.object(MODULE, "preflight") as preflight, self.assertRaises(MODULE.Gate):
                MODULE.deploy(args, self.config, aws, {})
            clean.assert_called_once_with(SOURCE)
            gates.assert_called_once_with(args.gate_evidence, SOURCE)
            plan.assert_not_called()
            preflight.assert_not_called()
            aws.client.assert_not_called()

    def test_failed_source_gates_prevent_continuation_inventory_and_preflight(self):
        for failing in ("require_clean_source", "verify_gate_file"):
            aws = Mock()
            with self.subTest(failing=failing), \
                    patch.object(MODULE.platform, "require_clean_source") as clean, \
                    patch.object(MODULE.platform, "verify_gate_file") as gates, \
                    patch("deploy.serverless_recovery.uninitialized_continuation_plan") as plan, \
                    patch.object(MODULE, "preflight") as preflight:
                (clean if failing == "require_clean_source" else gates).side_effect = MODULE.Gate("Source not admitted")
                with self.assertRaisesRegex(MODULE.Gate, "Source not admitted"):
                    MODULE.deploy(self._continuation_args(), self.config, aws, {})
            plan.assert_not_called()
            preflight.assert_not_called()
            aws.client.assert_not_called()

    def test_authority_normalization_preserves_fargate_configuration_and_budget(self):
        original = deepcopy(self.config)
        authority = MODULE.authority_config(self.config)
        self.assertEqual(authority, {**original, "environment": "serverless-development", "monthlyBudgetUsd": 50})
        self.assertEqual(self.config, original)
        self.assertEqual(self.config["monthlyBudgetUsd"], 100)

    def _retained_engine_cloud(self, versions, options=None):
        sts, plans, rds, ec2 = Mock(), Mock(), Mock(), Mock()
        sts.get_caller_identity.return_value = {"Account": ACCOUNT}
        plans.get_account_plan_state.return_value = {
            "accountId": ACCOUNT, "accountPlanType": "PAID", "accountPlanStatus": "ACTIVE"}
        engines, capacity = Mock(), Mock()
        engines.paginate.return_value = [{"DBEngineVersions": versions}]
        capacity.paginate.return_value = [{"OrderableDBInstanceOptions":
            [{"SupportedNetworkTypes": ["IPV4", "DUAL"]}] if options is None else options}]
        rds.get_paginator.side_effect = lambda operation: {
            "describe_db_engine_versions": engines, "describe_orderable_db_instance_options": capacity}[operation]
        ec2.describe_managed_prefix_lists.return_value = {"PrefixLists": [{"PrefixListId": "pl-12345678"}]}
        aws = Mock()
        aws.client.side_effect = lambda name: {"sts": sts, "freetier": plans, "rds": rds, "ec2": ec2}[name]
        return aws, rds, capacity

    def test_continuation_pins_retained_engine_and_keeps_fargate_budget_when_newer_version_is_available(self):
        versions = [{"Status": "available", "EngineVersion": version,
                     "ServerlessV2FeaturesSupport": {"MinCapacity": 0}} for version in ("16.15", "16.16")]
        aws, rds, capacity = self._retained_engine_cloud(versions)
        with patch.object(MODULE, "stable_stack", return_value=None):
            result = MODULE.preflight(aws, self.config, None, "16.15")
        self.assertEqual(result["databaseEngineVersion"], "16.15")
        self.assertEqual(result["monthlyBudgetUsd"], 100)
        self.assertEqual(result["environment"], "fargate-development")
        rds.describe_db_clusters.assert_not_called()
        capacity.paginate.assert_called_once_with(Engine="aurora-postgresql", EngineVersion="16.15",
                                                  DBInstanceClass="db.serverless")

    def test_retained_engine_cannot_fall_forward_when_unavailable_ambiguous_or_without_dual_stack_capacity(self):
        retained = {"Status": "available", "EngineVersion": "16.15",
                    "ServerlessV2FeaturesSupport": {"MinCapacity": 0}}
        newer = {**retained, "EngineVersion": "16.16"}
        invalid = [([newer], None), ([{**retained, "Status": "deprecated"}, newer], None),
                   ([{**retained, "ServerlessV2FeaturesSupport": {"MinCapacity": 0.5}}, newer], None),
                   ([retained, retained, newer], None), ([retained, newer], []),
                   ([retained, newer], [{"SupportedNetworkTypes": ["IPV4"]}])]
        for versions, options in invalid:
            aws, rds, capacity = self._retained_engine_cloud(versions, options)
            with self.subTest(versions=versions, options=options), \
                    patch.object(MODULE, "stable_stack", return_value=None), self.assertRaises(MODULE.Gate):
                MODULE.preflight(aws, self.config, None, "16.15")
            self.assertNotIn("ec2", [call.args[0] for call in aws.client.call_args_list])
            if capacity.paginate.called:
                self.assertEqual(capacity.paginate.call_args.kwargs["EngineVersion"], "16.15")

    def _run_continuation_lifecycle(self, root, *, fail_verification=None):
        events, template_configs, maintenance_options = [], [], {}
        aws, cloudfront = Mock(), Mock()
        aws.client.return_value = cloudfront
        cloudfront.create_invalidation.return_value = {"Invalidation": {"Id": "owned-invalidation"}}
        args = self._continuation_args()
        plan = {"database_engine_version": "16.15", "already_adopted": False}
        adopted = {**plan, "already_adopted": True}
        out = {**self.out, "WebDistributionId": "owned-web", "ApiDistributionId": "owned-api"}

        def planned(*arguments):
            events.append("plan")
            return plan

        def preflighted(aws, current, prior, version):
            events.append("preflight")
            return {**current, "databaseEngineVersion": version, "cloudFrontPrefixListId": "pl-12345678"}

        def continued(*arguments):
            events.append("continue")
            return adopted

        def template(current, phase="platform"):
            template_configs.append(deepcopy(current))
            return {"phase": phase, "active": current.get("activateServices", False)}

        def deployed(aws, name, current, *arguments):
            if current["phase"] == "registry":
                events.append("registry")
                return {"DeploymentBucket": self.out["DeploymentBucket"]}
            phase = "activate" if current["active"] else "stopped"
            events.append(phase)
            return {**out, "ActivateServices": str(current["active"]).lower()}

        def images(aws, current, *arguments):
            events.append("images")
            return {**current, **self.images}

        def ui(aws, current, *arguments):
            events.append("ui")
            return {**current, "uiArtifactBinding": "e" * 64}, {"index.html": b"reviewed-ui"}

        def verified(*arguments):
            number = sum(event.startswith("verify-database-") for event in events) + 1
            events.append("verify-database-" + str(number))
            if number == fail_verification:
                raise MODULE.Gate("Retained database changed")

        def maintained(aws, current, outputs, operation, work, **extra):
            events.append(operation)
            maintenance_options[operation] = extra
            self.assertEqual(current["monthlyBudgetUsd"], 100)
            return {"completed_at": datetime.now(timezone.utc).isoformat()}

        with ExitStack() as stack:
            stack.enter_context(patch.object(MODULE, "ROOT", root))
            stack.enter_context(patch.object(MODULE.platform, "require_clean_source",
                side_effect=lambda *args: events.append("admit-source")))
            stack.enter_context(patch.object(MODULE.platform, "verify_gate_file",
                side_effect=lambda *args: events.append("admit-gates")))
            planning = stack.enter_context(patch("deploy.serverless_recovery.uninitialized_continuation_plan", side_effect=planned))
            preflight = stack.enter_context(patch.object(MODULE, "preflight", side_effect=preflighted))
            continuation = stack.enter_context(patch("deploy.serverless_recovery.continue_uninitialized", side_effect=continued))
            database = stack.enter_context(patch("deploy.serverless_recovery.verify_continued_database", side_effect=verified))
            stable = stack.enter_context(patch.object(MODULE, "stable_stack"))
            drain = stack.enter_context(patch.object(MODULE, "drain"))
            stack.enter_context(patch("deploy.fargate_template.build_template", side_effect=template))
            stack.enter_context(patch.object(MODULE, "deploy_stack", side_effect=deployed))
            stack.enter_context(patch.object(MODULE, "archive_source"))
            stack.enter_context(patch.object(MODULE, "build_images", side_effect=images))
            stack.enter_context(patch.object(MODULE, "build_ui", side_effect=ui))
            network = stack.enter_context(patch.object(MODULE, "database_network", return_value={}))
            stack.enter_context(patch.object(MODULE, "run_maintenance", side_effect=maintained))
            stack.enter_context(patch.object(MODULE, "verify_origin"))
            stack.enter_context(patch.object(MODULE.web_artifact, "verify_access", return_value={"passed": True}))
            stack.enter_context(patch.object(MODULE, "verify_upload_access", return_value={"upload_verified": True}))
            stack.enter_context(patch.object(MODULE, "observe", return_value={"status": "healthy"}))
            stack.enter_context(patch.object(MODULE, "container_logs", return_value={"api_log_delivery_verified": True}))
            if fail_verification:
                with self.assertRaisesRegex(MODULE.Gate, "Retained database changed"), patch("sys.stderr", io.StringIO()):
                    MODULE.deploy(args, self.config, aws, {"budget_usd": 100})
                receipt = None
            else:
                receipt = MODULE.deploy(args, self.config, aws, {"budget_usd": 100})
        states = list(root.glob(".local/deploy/fargate-development/**/deployment-state.json"))
        self.assertEqual(len(states), 1)
        state = json.loads(states[0].read_text())
        return receipt, events, maintenance_options, state, template_configs, {
            "planning": planning, "preflight": preflight, "continuation": continuation,
            "database": database, "stable": stable, "drain": drain, "network": network,
            "aws": aws, "args": args, "adopted": adopted}

    def test_continuation_verifies_both_stopped_updates_before_bootstrap_without_changing_fargate_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt, events, options, state, configs, calls = self._run_continuation_lifecycle(Path(directory))
        self.assertEqual(events[:6], ["admit-source", "admit-gates", "plan", "preflight", "continue", "registry"])
        self.assertLess(events.index("stopped"), events.index("verify-database-1"))
        self.assertLess(events.index("verify-database-1"), events.index("ui"))
        self.assertLess(events.index("ui"), events.index("verify-database-2"))
        self.assertLess(events.index("verify-database-2"), events.index("bootstrap"))
        self.assertLess(events.index("admission"), events.index("activate"))
        calls["planning"].assert_called_once_with(calls["aws"], MODULE.authority_config(self.config),
            calls["args"].continue_uninitialized, calls["args"].continue_uninitialized_sha256)
        calls["preflight"].assert_called_once_with(calls["aws"], self.config, None, "16.15")
        continued = calls["continuation"].call_args.args
        self.assertEqual(continued[1]["databaseEngineVersion"], "16.15")
        self.assertEqual(continued[1]["environment"], "serverless-development")
        self.assertEqual(continued[1]["monthlyBudgetUsd"], 50)
        self.assertEqual(continued[2].name, "uninitialized-continuation.json")
        self.assertEqual(continued[3:], (calls["args"].continue_uninitialized,
                                       calls["args"].continue_uninitialized_sha256))
        self.assertEqual(calls["database"].call_count, 2)
        for call in calls["database"].call_args_list:
            self.assertEqual(call.args[1]["environment"], "serverless-development")
            self.assertEqual(call.args[1]["monthlyBudgetUsd"], 50)
            self.assertEqual(call.args[1]["databaseEngineVersion"], "16.15")
            self.assertEqual(call.args[2]["ActivateServices"], "false")
            self.assertIs(call.args[3], calls["adopted"])
        self.assertTrue(all(current["environment"] == "fargate-development"
                            and current["monthlyBudgetUsd"] == 100 for current in configs))
        self.assertEqual(self.config["monthlyBudgetUsd"], 100)
        calls["stable"].assert_not_called()
        calls["drain"].assert_not_called()
        self.assertEqual(options, {"bootstrap": {"establish_new": True}, "migrate": {}, "admission": {}})
        stages = state["completed_stages"]
        self.assertEqual(stages[0], "continue-uninitialized-retained-resources")
        self.assertLess(stages.index("deploy-stopped"), stages.index("verify-continued-database-stopped"))
        self.assertLess(stages.index("bind-stopped-ui-image"), stages.index("verify-continued-database-ui"))
        self.assertLess(stages.index("verify-continued-database-ui"), stages.index("bootstrap"))
        self.assertEqual(receipt["status"], "fargate_transport_and_health_verified")
        self.assertEqual(receipt["budget_plan"]["budget_usd"], 100)

    def test_either_stopped_database_verification_failure_blocks_bootstrap_migration_and_activation(self):
        for number, failed_stage in ((1, "verify-continued-database-stopped"), (2, "verify-continued-database-ui")):
            with self.subTest(number=number), tempfile.TemporaryDirectory() as directory:
                receipt, events, options, state, configs, calls = self._run_continuation_lifecycle(
                    Path(directory), fail_verification=number)
            self.assertIsNone(receipt)
            self.assertEqual(options, {})
            self.assertNotIn("bootstrap", events)
            self.assertNotIn("migrate", events)
            self.assertNotIn("activate", events)
            calls["network"].assert_not_called()
            calls["aws"].client.assert_not_called()
            self.assertEqual(calls["database"].call_count, number)
            self.assertEqual(state["status"], "failed")
            self.assertEqual(state["failed_stage"], failed_stage)
            self.assertNotIn(failed_stage, state["completed_stages"])
            self.assertFalse(state["rollback_executed"])
            if number == 1:
                self.assertNotIn("ui", events)
            else:
                self.assertIn("verify-continued-database-stopped", state["completed_stages"])
                self.assertIn("bind-stopped-ui-image", state["completed_stages"])

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
        with patch.object(MODULE.platform, "run", return_value=json.dumps([actual])), patch.object(MODULE, "build_command"):
            uri = MODULE.image(aws, self.config, registry, ROOT, "ui", binding="d" * 64)
            self.assertEqual(uri, registry["RepositoryUri"] + "@" + digest)
            self.assertEqual(ecr.describe_images.call_args.kwargs["imageIds"], [{"imageTag": "ui-" + SOURCE + "-" + "d" * 64}])
            with self.assertRaises(MODULE.Gate):
                MODULE.image(aws, self.config, registry, ROOT, "ui", binding="e" * 64)

    def test_real_subprocess_progress_cannot_contaminate_the_json_receipt_stream(self):
        stdout = io.StringIO()
        with tempfile.TemporaryFile(mode='w+') as logs, patch('sys.stdout', stdout), patch('sys.stderr', logs):
            MODULE.build_command([sys.executable, '-c', "import sys; print('build-progress'); print('diagnostic-progress',file=sys.stderr)"])
            logs.seek(0)
            actual = logs.read()
        self.assertEqual(stdout.getvalue(), '')
        self.assertIn('build-progress', actual)
        self.assertIn('diagnostic-progress', actual)

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
