"""Offline deployment drain, receipt and gate-ordering regression tests.

Provider responses are deterministic test doubles. These checks do not prove
AWS acceptance, DynamoDB transaction isolation or PostgreSQL qualification.
"""

from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from deploy import serverless, serverless_template
from deploy.provenance import Gate, REPOSITORY, REQUIRED_JOBS, WORKFLOW_PATH, validate_gate_binding
from otgd import serverless_control as control


REVISION = "a" * 40
OWNER = "00000000-0000-4000-8000-000000000001"
NONCE = "00000000-0000-4000-8000-00000000000a"
FOREIGN = "00000000-0000-4000-8000-000000000003"
TOKEN = {"owner_id": OWNER, "generation": 7, "source_revision": REVISION}
ACCOUNT = "123456789012"
REGION = "us-east-2"
URI = f"{ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/fictional-serverless"


def configuration():
    return {
        "environment": "serverless-development", "account": ACCOUNT,
        "region": REGION, "releaseId": REVISION, "alarmEmail": "operator@fixture.test",
        "monthlyBudgetUsd": 50, "plannedMonthlyUsers": 10, "costEstimatePath": "fictional.json",
        "apiImageUri": URI + "@sha256:" + "b" * 64,
        "workerImageUri": URI + "@sha256:" + "c" * 64,
    }


def outputs():
    return {
        "AdmissionProtocolVersion": "1", "RuntimeControlTable": "fictional-control",
        "ControlSchedule": "fictional-schedule", "WorkerMapping": "fictional-mapping",
        "ApiFunction": "fictional-api", "WorkerFunction": "fictional-worker",
        "DispatcherFunction": "fictional-dispatcher", "ControlFunction": "fictional-controller",
        "MaintenanceFunction": "fictional-maintenance",
        "MaintenanceFunctionArn": f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:fictional-maintenance",
        "MaintenanceRoleArn": f"arn:aws:iam::{ACCOUNT}:role/fictional-maintenance",
        "WebOrigin": "https://web.fixture.test", "ApiOrigin": "https://api.fixture.test",
        "CloudWatchDashboardUrl": "https://dashboard.fixture.test",
    }


class Clock:
    def __init__(self):
        self.current = 0
        self.sleeps = []

    def monotonic(self):
        return self.current

    def sleep(self, duration):
        self.sleeps.append(duration)
        self.current += duration


class ServerlessDrainTests(unittest.TestCase):
    def fixture(self, *, active=()):
        events = []
        functions, schedules, dynamodb = Mock(), Mock(), Mock()
        functions.get_event_source_mapping.return_value = {"State": "Disabled"}
        functions.update_event_source_mapping.side_effect = lambda **kwargs: events.append("mapping-stop")
        functions.put_function_concurrency.side_effect = lambda **kwargs: events.append("stop-" + kwargs["FunctionName"])
        schedules.disable_rule.side_effect = lambda **kwargs: events.append("schedule-stop")
        aws = Mock()
        aws.client.side_effect = lambda name, **kwargs: {"lambda": functions, "events": schedules, "dynamodb": dynamodb}[name]
        store = Mock()
        store.close_admission.side_effect = lambda owner: events.append("closed") or dict(TOKEN)
        store.require_closed.side_effect = lambda ownership: events.append("ownership-checked") or deepcopy(ownership)
        store.snapshot.side_effect = lambda: events.append("snapshot") or SimpleNamespace(active_leases=active)
        return aws, functions, schedules, dynamodb, store, events

    def run_drain(self, aws, store, **options):
        clock = Clock()
        with patch.object(control, "ControlStore", return_value=store) as constructor, \
                patch.object(serverless.time, "monotonic", side_effect=clock.monotonic), \
                patch.object(serverless.time, "sleep", side_effect=clock.sleep):
            value = serverless.drain(aws, outputs(), source_revision=REVISION, owner_id=OWNER, **options)
        return value, clock, constructor

    def test_atomic_admission_close_precedes_empty_snapshot_and_late_producer(self):
        aws, functions, schedules, dynamodb, store, events = self.fixture()
        denied = []
        def late_producer(**kwargs):
            self.assertIn("closed", events, "Producer could enter SQL before the durable admission fence")
            denied.append("late-producer-denied")
            events.append("schedule-stop")
        schedules.disable_rule.side_effect = late_producer
        result, clock, constructor = self.run_drain(aws, store)
        constructor.assert_called_once_with(client=dynamodb, table_name="fictional-control", source_revision=REVISION)
        store.close_admission.assert_called_once_with(OWNER)
        self.assertEqual(denied, ["late-producer-denied"])
        self.assertLess(events.index("closed"), events.index("snapshot"))
        self.assertLess(events.index("closed"), events.index("mapping-stop"))
        self.assertEqual(result, {"services_stopped": True, "producer_leases_drained": True, "ownership": TOKEN})
        self.assertEqual(clock.sleeps, [])
        self.assertGreaterEqual(store.require_closed.call_count, 2)
        for call in store.require_closed.call_args_list:
            self.assertEqual(call.args, (TOKEN,))
        store.reopen_admission.assert_not_called()

    def test_already_admitted_producer_is_drained_after_release_without_reopening(self):
        aws, _, _, _, store, events = self.fixture()
        active = SimpleNamespace(lease_id=FOREIGN)
        snapshots = iter((SimpleNamespace(active_leases=(active,)), SimpleNamespace(active_leases=())))
        store.snapshot.side_effect = lambda: events.append("snapshot") or next(snapshots)
        result, clock, _ = self.run_drain(aws, store)
        self.assertTrue(result["producer_leases_drained"])
        self.assertEqual(store.snapshot.call_count, 2)
        self.assertEqual(clock.sleeps, [10])
        self.assertGreaterEqual(store.require_closed.call_count, 4)
        store.reopen_admission.assert_not_called()

    def test_empty_snapshot_cannot_override_changed_owner_or_generation(self):
        for error in ("closed owner changed", "closed generation changed", "closed source changed"):
            aws, _, _, _, store, _ = self.fixture()
            store.require_closed.side_effect = [None, control.ControlUnavailable(error)]
            with self.subTest(error=error), self.assertRaises((Gate, control.ControlUnavailable)):
                self.run_drain(aws, store)
            store.reopen_admission.assert_not_called()

    def test_active_lease_timeout_fails_closed_and_preserves_stopped_functions(self):
        aws, functions, schedules, _, store, _ = self.fixture(active=(SimpleNamespace(lease_id=FOREIGN),))
        with self.assertRaises((Gate, control.ControlUnavailable)):
            self.run_drain(aws, store)
        schedules.disable_rule.assert_called_once()
        stopped = {call.kwargs["FunctionName"]: call.kwargs["ReservedConcurrentExecutions"]
            for call in functions.put_function_concurrency.call_args_list}
        self.assertEqual(stopped, {outputs()[key]: 0 for key in ("ApiFunction", "WorkerFunction", "DispatcherFunction", "ControlFunction")})
        self.assertGreater(store.snapshot.call_count, 1)
        store.reopen_admission.assert_not_called()

    def test_mapping_timeout_cannot_start_source_schema_or_reopen(self):
        aws, functions, _, _, store, _ = self.fixture()
        functions.get_event_source_mapping.return_value = {"State": "Disabling"}
        with self.assertRaises((Gate, control.ControlUnavailable)):
            self.run_drain(aws, store)
        functions.put_function_concurrency.assert_not_called()
        store.snapshot.assert_not_called()
        store.reopen_admission.assert_not_called()

    def test_control_outage_and_old_protocol_refuse_admission_claims(self):
        aws, functions, schedules, _, store, _ = self.fixture()
        store.close_admission.side_effect = control.ControlUnavailable("fictional metadata outage")
        with self.assertRaises((Gate, control.ControlUnavailable)):
            self.run_drain(aws, store)
        functions.update_event_source_mapping.assert_not_called()
        schedules.disable_rule.assert_not_called()
        for version in (None, "0", 1, True):
            prior = outputs()
            prior["AdmissionProtocolVersion"] = version
            with self.subTest(version=version), patch.object(control, "ControlStore") as constructor, self.assertRaises(Gate):
                serverless.drain(aws, prior, source_revision=REVISION, owner_id=OWNER)
            constructor.assert_not_called()

    def test_close_callback_runs_after_ownership_check_before_any_shutdown_even_on_timeout(self):
        aws, _, _, _, store, events = self.fixture(active=(SimpleNamespace(lease_id=FOREIGN),))
        persisted = []
        def on_closed(ownership):
            self.assertEqual(ownership, TOKEN)
            self.assertIn("ownership-checked", events)
            self.assertNotIn("schedule-stop", events)
            self.assertNotIn("mapping-stop", events)
            persisted.append(deepcopy(ownership))
            events.append("ownership-persisted")
        with self.assertRaises(Gate):
            self.run_drain(aws, store, on_closed=on_closed)
        self.assertEqual(persisted, [TOKEN])
        self.assertLess(events.index("ownership-persisted"), events.index("schedule-stop"))
        store.reopen_admission.assert_not_called()

    def test_resumed_drain_reuses_exact_owner_and_generation_without_reclosing(self):
        aws, _, _, _, store, _ = self.fixture()
        result, _, _ = self.run_drain(aws, store, ownership=dict(TOKEN))
        self.assertEqual(result["ownership"], TOKEN)
        store.close_admission.assert_not_called()
        self.assertGreaterEqual(store.require_closed.call_count, 3)
        for call in store.require_closed.call_args_list:
            self.assertEqual(call.args, (TOKEN,))

    def test_stale_resume_token_cannot_be_upgraded_or_stop_sources(self):
        aws, functions, schedules, _, store, _ = self.fixture()
        store.require_closed.side_effect = control.ControlUnavailable("Saved generation is no longer current")
        with self.assertRaises(control.ControlUnavailable):
            self.run_drain(aws, store, ownership=dict(TOKEN))
        store.close_admission.assert_not_called()
        schedules.disable_rule.assert_not_called()
        functions.update_event_source_mapping.assert_not_called()
        functions.put_function_concurrency.assert_not_called()


class ServerlessMaintenanceReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="otgd-maintenance-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)

    def function(self):
        return {
            "Code": {"ResolvedImageUri": configuration()["workerImageUri"]},
            "Configuration": {
                "FunctionArn": outputs()["MaintenanceFunctionArn"],
                "Role": outputs()["MaintenanceRoleArn"],
                "ImageConfigResponse": {"ImageConfig": {"Command": ["otgd.serverless_worker.maintenance_handler"]}},
                "Environment": {"Variables": {
                    "OTGD_SOURCE_REVISION": REVISION, "OTGD_DEPLOYMENT_ACCOUNT": ACCOUNT,
                    "OTGD_AWS_REGION": REGION, "OTGD_ENVIRONMENT": "qa",
                    "OTGD_SERVERLESS_DEPLOYMENT_PROFILE": "serverless-development",
                    "OTGD_SERVERLESS_ROLE": "maintenance", "OTGD_LAMBDA_MAINTENANCE_ROLE": "maintenance",
                    "OTGD_SERVERLESS_MODE": "true", "OTGD_DATABASE_USER": "otgd_migrator",
                    "OTGD_LAMBDA_HANDLER": "otgd.serverless_worker.maintenance_handler",
                }},
            },
        }

    def fixture(self, operation="admission", *, body_change=None, raw_body=None, response_change=None, function_change=None):
        functions = Mock()
        actual = self.function()
        if function_change:
            function_change(actual)
        functions.get_function.return_value = actual
        streams, events = [], []
        def invoke(**kwargs):
            event = json.loads(kwargs["Payload"])
            events.append(event)
            body = {"operation": operation,
                "status": {"bootstrap": "bootstrap_verified", "migrate": "migrated", "admission": "admission_verified"}[operation],
                "request_nonce": event["request_nonce"], "deployment_profile": "serverless-development",
                "maintenance_role": "maintenance", "account": ACCOUNT, "region": REGION,
                "source_revision": REVISION, "ownership": dict(TOKEN)}
            if body_change:
                body.update(body_change)
            stream = io.BytesIO(raw_body if raw_body is not None else json.dumps(body).encode())
            streams.append(stream)
            response = {"Payload": stream, "StatusCode": 200,
                "ResponseMetadata": {"RequestId": FOREIGN}}
            if response_change:
                response.update(response_change)
            return response
        functions.invoke.side_effect = invoke
        aws = Mock()
        aws.client.return_value = functions
        return aws, functions, streams, events

    def invoke(self, aws, operation="admission", *, _store=None, **extra):
        closed_store = Mock() if _store is None else _store
        with patch.object(serverless.uuid, "uuid4", return_value=UUID(NONCE)), \
                patch.object(serverless, "control_store", return_value=closed_store):
            return serverless.invoke_maintenance(aws, configuration(), outputs(), operation,
                self.work, ownership=dict(TOKEN), **extra)

    def test_exact_runtime_receipt_is_required_and_stream_is_closed(self):
        for operation in ("bootstrap", "migrate", "admission"):
            aws, functions, streams, events = self.fixture(operation)
            extra = {"establish_new": False} if operation == "bootstrap" else {}
            receipt = self.invoke(aws, operation, **extra)
            self.assertEqual(events, [{"operation": operation, "request_nonce": NONCE, "ownership": TOKEN, **extra}])
            self.assertTrue(streams[0].closed)
            self.assertEqual(receipt["result"]["request_nonce"], NONCE)
            self.assertEqual(receipt["result"]["ownership"], TOKEN)
            self.assertEqual(receipt["image_uri"], configuration()["workerImageUri"])
            filename = "migration.json" if operation == "migrate" else operation + ".json"
            saved = json.loads((self.work / filename).read_bytes())
            self.assertEqual(saved, receipt)
            functions.invoke.assert_called_once()

    def test_wrong_operation_status_nonce_owner_generation_source_or_role_cannot_publish(self):
        changes = [
            {"operation": "migrate"}, {"status": "passed"}, {"status": "migrated"},
            {"request_nonce": FOREIGN}, {"request_nonce": NONCE.upper()},
            {"deployment_profile": "qa"}, {"maintenance_role": "dispatcher"},
            {"account": "999999999999"}, {"region": "us-west-2"}, {"source_revision": "b" * 40},
            {"ownership": {**TOKEN, "owner_id": FOREIGN}}, {"ownership": {**TOKEN, "generation": 8}},
            {"ownership": {**TOKEN, "generation": 7.0}},
            {"ownership": {**TOKEN, "source_revision": "b" * 40}}, {"unexpected": "extra"},
        ]
        for change in changes:
            aws, _, streams, _ = self.fixture(body_change=change)
            with self.subTest(change=change), self.assertRaises(Gate):
                self.invoke(aws)
            self.assertTrue(streams[0].closed)
            self.assertEqual(list(self.work.iterdir()), [])

    def test_duplicate_nonfinite_incomplete_oversize_or_failed_response_cannot_publish(self):
        for raw in (b'{"status":"passed","status":"admission_verified"}', b'{"status":NaN}', b'[]', b'{}', b'x' * 65537):
            aws, _, streams, _ = self.fixture(raw_body=raw)
            with self.subTest(raw_size=len(raw)), self.assertRaises((Gate, ValueError)):
                self.invoke(aws)
            self.assertTrue(streams[0].closed)
            self.assertEqual(list(self.work.iterdir()), [])
        for change in ({"FunctionError": "Unhandled"}, {"StatusCode": 202}):
            aws, _, streams, _ = self.fixture(response_change=change)
            with self.subTest(change=change), self.assertRaises(Gate):
                self.invoke(aws)
            self.assertTrue(streams[0].closed)

    def test_actual_function_image_iam_role_sql_role_and_source_are_independently_scoped(self):
        mutations = [
            lambda value: value["Code"].update(ResolvedImageUri=configuration()["apiImageUri"]),
            lambda value: value["Configuration"].update(FunctionArn="arn:aws:lambda:us-east-2:999999999999:function:other"),
            lambda value: value["Configuration"].update(Role=f"arn:aws:iam::{ACCOUNT}:role/dispatcher"),
        ]
        for field, wrong in (("OTGD_SOURCE_REVISION", "b" * 40), ("OTGD_DEPLOYMENT_ACCOUNT", "999999999999"),
            ("OTGD_AWS_REGION", "us-west-2"), ("OTGD_ENVIRONMENT", "prod"),
            ("OTGD_SERVERLESS_DEPLOYMENT_PROFILE", "qa"), ("OTGD_SERVERLESS_ROLE", "dispatcher"),
            ("OTGD_LAMBDA_MAINTENANCE_ROLE", "app"), ("OTGD_SERVERLESS_MODE", "false"),
            ("OTGD_DATABASE_USER", "otgd_app"), ("OTGD_LAMBDA_HANDLER", "otgd.serverless_worker.sqs_handler")):
            mutations.append(lambda value, field=field, wrong=wrong: value["Configuration"]["Environment"]["Variables"].update({field: wrong}))
        for index, mutation in enumerate(mutations):
            aws, functions, _, _ = self.fixture(function_change=mutation)
            with self.subTest(mutation=index), self.assertRaises(Gate):
                self.invoke(aws)
            functions.invoke.assert_not_called()
            self.assertEqual(list(self.work.iterdir()), [])

    def test_missing_wrong_empty_or_failed_image_command_cannot_invoke_maintenance(self):
        mutations = [
            lambda value: value["Configuration"].pop("ImageConfigResponse"),
            lambda value: value["Configuration"]["ImageConfigResponse"].update(ImageConfig={}),
            lambda value: value["Configuration"]["ImageConfigResponse"]["ImageConfig"].update(Command=[]),
            lambda value: value["Configuration"]["ImageConfigResponse"]["ImageConfig"].update(Command=["otgd.serverless_worker.dispatch_handler"]),
            lambda value: value["Configuration"]["ImageConfigResponse"].update(Error={"ErrorCode": "InvalidImage", "Message": "fictional provider error"}),
            lambda value: value["Configuration"]["ImageConfigResponse"].update(Error={}),
            lambda value: value["Configuration"]["ImageConfigResponse"].update(Error=None),
            lambda value: value["Configuration"]["ImageConfigResponse"]["ImageConfig"].update(EntryPoint=["python", "-m", "another.handler"]),
            lambda value: value["Configuration"]["ImageConfigResponse"]["ImageConfig"].update(WorkingDirectory="/tmp/another-source"),
        ]
        for index, mutation in enumerate(mutations):
            aws, functions, _, _ = self.fixture(function_change=mutation)
            with self.subTest(mutation=index), self.assertRaises(Gate):
                self.invoke(aws)
            functions.invoke.assert_not_called()
            self.assertEqual(list(self.work.iterdir()), [])

    def test_actual_migration_receipt_is_inventoried_by_real_stage_journal(self):
        aws, _, streams, _ = self.fixture("migrate")
        with serverless.StageJournal(self.work, configuration()) as journal:
            receipt = journal.call("migrate", self.invoke, aws, "migrate")
        self.assertTrue(streams[0].closed)
        migration = self.work / "migration.json"
        self.assertTrue(migration.is_file())
        self.assertFalse((self.work / "migrate.json").exists())
        self.assertEqual(json.loads(migration.read_bytes()), receipt)
        state = json.loads((self.work / "deployment-state.json").read_bytes())
        self.assertEqual(state["completed_receipts"]["migration.json"], {
            "path": str(migration), "sha256": hashlib.sha256(migration.read_bytes()).hexdigest(),
        })

    def test_ownership_must_still_match_after_runtime_returns_completion(self):
        aws, _, streams, _ = self.fixture()
        store = Mock()
        store.require_closed.side_effect = [None, control.ControlUnavailable("closed owner or generation changed")]
        with self.assertRaises((Gate, control.ControlUnavailable)):
            self.invoke(aws, _store=store)
        self.assertTrue(streams[0].closed)
        self.assertEqual(list(self.work.iterdir()), [])
        store.reopen_admission.assert_not_called()

    def test_input_operation_ownership_and_bootstrap_choices_are_closed_before_invocation(self):
        cases = [
            ("admission", {}),
            ("admission", {"ownership": {**TOKEN, "generation": 7.0}}),
            ("admission", {"ownership": {**TOKEN, "owner_id": "not-a-uuid"}}),
            ("admission", {"ownership": {**TOKEN, "source_revision": "b" * 40}}),
            ("admission", {"ownership": TOKEN, "request_nonce": FOREIGN}),
            ("bootstrap", {"ownership": TOKEN, "establish_new": 1}),
            ("publish", {"ownership": TOKEN}),
        ]
        for operation, options in cases:
            aws = Mock()
            with self.subTest(operation=operation, fields=list(options)), patch.object(serverless, "control_store") as store, self.assertRaises(Gate):
                serverless.invoke_maintenance(aws, configuration(), outputs(), operation, self.work, **options)
            store.assert_not_called()
            aws.client.assert_not_called()


class ServerlessPublicAdmissionTests(unittest.TestCase):
    def source(self, root):
        source = root / "fictional-source.tar"
        with tarfile.open(source, "w") as archive:
            raw = b'{"fixture":"offline export command seam"}'
            entry = tarfile.TarInfo("apps/mobile/package.json")
            entry.size = len(raw)
            archive.addfile(entry, io.BytesIO(raw))
        return source

    def fixture(self, root):
        out = {**outputs(), "WebBucket": "fictional-private-web", "WebDistributionId": "fictional-distribution",
            "Issuer": "https://issuer.fixture.test/pool", "ClientId": "A" * 26}
        commands = []
        def export(command, *, cwd, env, check):
            self.assertTrue(check)
            commands.append((command, env))
            if command[:3] == ["npm", "run", "export:web"]:
                dist = cwd / "dist"
                dist.mkdir()
                (dist / "index.html").write_bytes(b'<script src="app.js"></script>')
                (dist / "app.js").write_bytes(b'console.log("fictional offline public export");')
        clients = {"cloudfront": Mock(), "s3": Mock()}
        clients["cloudfront"].create_invalidation.return_value = {"Invalidation": {"Id": "fixture-invalidation"}}
        aws = Mock()
        aws.client.side_effect = lambda name: clients[name]
        return aws, out, export, commands, clients

    def test_public_assets_publish_before_index_and_do_not_probe_closed_api(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.source(root)
            aws, out, export, commands, clients = self.fixture(root)
            published = []
            sensitive = {"AWS_SECRET_ACCESS_KEY": "fictional-private-aws", "GH_ADMIN_TOKEN": "fictional-private-github",
                "EXPO_TOKEN": "fictional-private-expo", "OTGD_DATABASE_URL": "fictional-private-database"}
            with patch.dict(os.environ, sensitive), patch.object(serverless.subprocess, "run", side_effect=export), \
                    patch.object(serverless.web_artifact, "verify_distribution") as distribution, \
                    patch.object(serverless.web_artifact, "put_immutable", side_effect=lambda *args: published.append(args)), \
                    patch.object(serverless.web_artifact, "verify_access") as access:
                manifest = serverless.build_and_publish_web(aws, configuration(), out, source, root)
            self.assertEqual([command for command, _ in commands], [["npm", "ci"], ["npm", "run", "export:web", "--", "--clear"]])
            for _, environment in commands:
                for key in sensitive:
                    self.assertNotIn(key, environment)
                self.assertEqual(environment["EXPO_PUBLIC_SERVERLESS"], "true")
                self.assertEqual(environment["EXPO_PUBLIC_API_URL"], out["ApiOrigin"])
            prefix = "releases/" + REVISION + "/"
            self.assertEqual([entry[2] for entry in published], [prefix + "app.js", prefix + "index.html"])
            distribution.assert_called_once_with(aws, out, prefix.rstrip("/"), REGION)
            access.assert_not_called()
            clients["cloudfront"].create_invalidation.assert_called_once()
            files = serverless.web_artifact.contents(root / "web.zip", manifest)
            with patch.object(serverless.web_artifact, "verify_access", return_value={"passed": True}) as access:
                self.assertEqual(serverless.verify_published_web(out, manifest, root), {"passed": True})
            access.assert_called_once_with(out, {}, files, timeout=120)

    def test_unreviewed_distribution_blocks_public_asset_writes_and_invalidation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            aws, out, export, _, clients = self.fixture(root)
            with patch.object(serverless.subprocess, "run", side_effect=export), \
                    patch.object(serverless.web_artifact, "verify_distribution", side_effect=Gate("Distribution scope changed")), \
                    patch.object(serverless.web_artifact, "put_immutable") as publish, self.assertRaises(Gate):
                serverless.build_and_publish_web(aws, configuration(), out, self.source(root), root)
            publish.assert_not_called()
            clients["cloudfront"].create_invalidation.assert_not_called()

    def test_closed_or_foreign_source_health_cannot_probe_api_or_claim_ready(self):
        aws, store = Mock(), Mock()
        store.require_open.side_effect = control.ControlUnavailable("Runtime is atomically closed")
        out = {**outputs(), "ReleaseId": REVISION}
        with patch.object(serverless, "control_store", return_value=store), \
                patch.object(serverless.httpx, "Client") as http, self.assertRaises(control.ControlUnavailable):
            serverless.observe(aws, configuration(), out)
        http.assert_not_called()
        aws.client.assert_not_called()
        with patch.object(serverless, "control_store") as selection, self.assertRaises(Gate):
            serverless.observe(aws, configuration(), {**out, "ReleaseId": "b" * 40})
        selection.assert_not_called()


class ServerlessStageGateTests(unittest.TestCase):
    FRESH_STAGES = (
        "serverless-registry", "build-immutable-lambda-images", "deploy-stopped",
        "close-new-admission", "bootstrap", "migrate", "admission", "activate",
        "publish-web", "reopen-admission",
    )
    EXISTING_STAGES = (
        "serverless-registry", "build-immutable-lambda-images", "drain-existing-runtime",
        "deploy-stopped", "bootstrap", "migrate", "admission", "activate",
        "publish-web", "reopen-admission",
    )

    def proof(self):
        proof = {
            "provider": "github_actions", "repository": REPOSITORY,
            "workflow_path": WORKFLOW_PATH, "workflow_id": 17, "run_id": 23,
            "run_attempt": 1, "head_sha": REVISION,
            "run_url": f"https://github.com/{REPOSITORY}/actions/runs/23",
            "event": "push", "head_branch": "main",
            "jobs": {name: index for index, name in enumerate(sorted(REQUIRED_JOBS), 1)},
        }
        # Exercise the genuine closed provenance schema. This is a fictional
        # provider response for caller ordering, never live gate evidence.
        validate_gate_binding(proof, REVISION)
        return proof

    def lifecycle(self, root, *, existing=False, fail_stage=None, changed_attempt=False,
                  drain_failure=False, resumed_token=None):
        events = []
        proof = self.proof()
        aws, store = Mock(), Mock()
        out = outputs()
        current = configuration()
        token = dict(TOKEN) if resumed_token is None else deepcopy(resumed_token)
        resume_path = None
        if resumed_token is not None:
            resume_path = root / "explicit-resume.json"
            serverless.write_owned_receipt(resume_path, {
                "schema_version": "1.0.0", "source_revision": REVISION, "account": ACCOUNT,
                "region": REGION, "control_table": out["RuntimeControlTable"], "ownership": token,
            })
        def stage():
            paths = list(root.glob(".local/deploy/serverless-development/**/deployment-state.json"))
            return json.loads(paths[0].read_bytes())["current_stage"] if paths else "initial"
        def verify(path, revision):
            self.assertEqual(path, Path("fictional-gates.json"))
            self.assertEqual(revision, REVISION)
            name = stage()
            events.append(("gate", name))
            if name == fail_stage:
                if changed_attempt:
                    return {**deepcopy(proof), "run_attempt": 2}
                raise Gate("Fictional current required gate rejection")
            return deepcopy(proof)
        def effect(name, result=None):
            self.assertEqual(stage(), name)
            self.assertEqual(events[-1], ("gate", name + "-gate-readmission"),
                "A mutation reached the provider without a fresh immediately preceding gate check")
            events.append(("mutation", name))
            return result
        def build_template(c, phase="platform"):
            return {"phase": phase, "active": c.get("activateServices", False)}
        def stack(aws, name, template, *arguments):
            if template["phase"] == "registry":
                return effect("serverless-registry", {"RepositoryUri": URI, "DeploymentBucket": "fictional-private-assets"})
            return effect("activate" if template["active"] else "deploy-stopped", out)
        def drain(aws, out, **options):
            self.assertEqual(options["source_revision"], REVISION)
            self.assertEqual(options["owner_id"], token["owner_id"])
            self.assertEqual(options["ownership"], resumed_token)
            result = effect("drain-existing-runtime", {"services_stopped": True,
                "producer_leases_drained": True, "ownership": deepcopy(token)})
            options["on_closed"](deepcopy(token))
            if drain_failure:
                raise Gate("Fictional active producer lease timeout after atomic close")
            return result
        def maintenance(aws, c, out, operation, work, **options):
            self.assertEqual(options["ownership"], token)
            if operation == "bootstrap":
                self.assertIs(options["establish_new"], False)
            return effect(operation, {"completed_at": datetime.now(timezone.utc).isoformat()})
        def close(owner):
            self.assertEqual(owner, OWNER)
            return effect("close-new-admission", deepcopy(token))
        store.close_admission.side_effect = close
        store.require_closed.side_effect = lambda ownership: deepcopy(ownership)
        store.reopen_admission.side_effect = lambda ownership: effect("reopen-admission")
        def public_access(*arguments):
            self.assertEqual(events[-1], ("mutation", "reopen-admission"))
            events.append(("public-verification", "after-reopen"))
            return {"passed": True}
        with ExitStack() as patches:
            patches.enter_context(patch.object(serverless, "ROOT", root))
            patches.enter_context(patch.object(serverless.uuid, "uuid4", return_value=UUID(OWNER)))
            patches.enter_context(patch.object(serverless.platform, "require_clean_source"))
            patches.enter_context(patch.object(serverless, "verify_serverless_gates", side_effect=verify))
            patches.enter_context(patch.object(serverless, "stable_stack", return_value=out if existing else None))
            patches.enter_context(patch.object(serverless, "preflight", return_value=current))
            patches.enter_context(patch.object(serverless_template, "build_template", side_effect=build_template))
            patches.enter_context(patch.object(serverless, "deploy_stack", side_effect=stack))
            patches.enter_context(patch.object(serverless.platform, "run"))
            patches.enter_context(patch.object(serverless, "build_images",
                side_effect=lambda *arguments: effect("build-immutable-lambda-images", current)))
            patches.enter_context(patch.object(serverless, "drain", side_effect=drain))
            patches.enter_context(patch.object(serverless, "control_store", return_value=store))
            patches.enter_context(patch.object(serverless, "invoke_maintenance", side_effect=maintenance))
            patches.enter_context(patch.object(serverless, "build_and_publish_web",
                side_effect=lambda *arguments: effect("publish-web", {"fictional_manifest": True})))
            patches.enter_context(patch.object(serverless, "verify_published_web", side_effect=public_access))
            patches.enter_context(patch.object(serverless, "observe", return_value={"status": "healthy"}))
            patches.enter_context(patch("sys.stderr", new_callable=io.StringIO))
            args = SimpleNamespace(gate_evidence=Path("fictional-gates.json"), establish_new=False, resume_owner=resume_path)
            if fail_stage or drain_failure:
                with self.assertRaises(Gate):
                    serverless.deploy(args, current, aws, {"estimated_monthly_usd": 25})
                receipt = None
            else:
                receipt = serverless.deploy(args, current, aws, {"estimated_monthly_usd": 25})
        states = list(root.glob(".local/deploy/serverless-development/**/deployment-state.json"))
        self.assertEqual(len(states), 1)
        return receipt, events, json.loads(states[0].read_bytes()), store

    def test_every_cloud_mutation_group_has_fresh_exact_source_required_gates(self):
        for existing in (False, True):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as directory:
                receipt, events, state, store = self.lifecycle(Path(directory), existing=existing)
            expected = self.EXISTING_STAGES if existing else self.FRESH_STAGES
            self.assertEqual([stage for kind, stage in events if kind == "mutation"], list(expected))
            self.assertEqual(receipt["status"], "serverless_transport_and_health_verified")
            self.assertFalse(receipt["production_promotion_eligible"])
            self.assertEqual(events[-1], ("public-verification", "after-reopen"))
            self.assertFalse(state["rollback_executed"])
            store.reopen_admission.assert_called_once_with(TOKEN)
            for call in store.require_closed.call_args_list:
                self.assertEqual(call.args, (TOKEN,))

    def test_current_required_gate_failure_blocks_each_stage_and_every_later_effect(self):
        cases = [(name, False) for name in self.FRESH_STAGES] + [("drain-existing-runtime", True)]
        for failed, existing in cases:
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as directory:
                _, events, state, store = self.lifecycle(Path(directory), existing=existing,
                    fail_stage=failed + "-gate-readmission")
            stages = self.EXISTING_STAGES if existing else self.FRESH_STAGES
            self.assertEqual([stage for kind, stage in events if kind == "mutation"], list(stages[:stages.index(failed)]))
            self.assertEqual(state["status"], "failed")
            self.assertEqual(state["failed_stage"], failed + "-gate-readmission")
            self.assertFalse(state["rollback_executed"])
            self.assertNotIn(("public-verification", "after-reopen"), events)
            store.reopen_admission.assert_not_called()

    def test_newer_gate_attempt_cannot_replace_the_admitted_run_mid_deployment(self):
        with tempfile.TemporaryDirectory() as directory:
            _, events, state, store = self.lifecycle(Path(directory), fail_stage="bootstrap-gate-readmission", changed_attempt=True)
        self.assertNotIn(("mutation", "bootstrap"), events)
        self.assertNotIn(("mutation", "activate"), events)
        self.assertEqual(state["failed_stage"], "bootstrap-gate-readmission")
        store.reopen_admission.assert_not_called()

    def test_final_activation_readmission_failure_preserves_closed_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            _, events, state, store = self.lifecycle(Path(directory), fail_stage="gate-readmission")
        self.assertIn(("mutation", "admission"), events)
        self.assertNotIn(("mutation", "activate"), events)
        self.assertEqual(state["failed_stage"], "gate-readmission")
        store.reopen_admission.assert_not_called()

    def test_drain_timeout_still_persists_private_full_closure_before_stopped_stack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, events, state, store = self.lifecycle(root, existing=True, drain_failure=True)
            paths = list(root.glob(".local/deploy/serverless-development/**/admission-closure.json"))
            self.assertEqual(len(paths), 1)
            closure = paths[0]
            self.assertEqual(closure.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(closure.read_bytes()), {
                "schema_version": "1.0.0", "source_revision": REVISION, "account": ACCOUNT,
                "region": REGION, "control_table": outputs()["RuntimeControlTable"], "ownership": TOKEN,
            })
        self.assertEqual(state["failed_stage"], "drain-existing-runtime")
        self.assertNotIn(("mutation", "deploy-stopped"), events)
        store.reopen_admission.assert_not_called()

    def test_explicit_resume_preserves_saved_owner_and_generation_through_reopening(self):
        saved = {**TOKEN, "owner_id": FOREIGN, "generation": 11}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, events, _, store = self.lifecycle(root, existing=True, resumed_token=saved)
            closure = next(root.glob(".local/deploy/serverless-development/**/admission-closure.json"))
            self.assertEqual(json.loads(closure.read_bytes())["ownership"], saved)
        self.assertIn(("mutation", "drain-existing-runtime"), events)
        store.close_admission.assert_not_called()
        store.reopen_admission.assert_called_once_with(saved)
        for call in store.require_closed.call_args_list:
            self.assertEqual(call.args, (saved,))


class ServerlessResumeOwnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="otgd-resume-owner-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.path = self.work / "admission-closure.json"
        self.record = {
            "schema_version": "1.0.0", "source_revision": REVISION, "account": ACCOUNT,
            "region": REGION, "control_table": outputs()["RuntimeControlTable"], "ownership": dict(TOKEN),
        }
        self.path.write_bytes(json.dumps(self.record).encode())
        self.path.chmod(0o600)

    def test_private_exact_scope_requires_live_matching_closed_ownership(self):
        original = self.path.read_bytes()
        aws, store = Mock(), Mock()
        store.require_closed.return_value = dict(TOKEN)
        with patch.object(serverless, "control_store", return_value=store) as factory:
            result = serverless.validate_resume_owner(aws, configuration(), outputs(), self.path)
        self.assertEqual(result, TOKEN)
        factory.assert_called_once_with(aws, outputs(), REVISION)
        store.require_closed.assert_called_once_with(TOKEN)
        store.close_admission.assert_not_called()
        store.reopen_admission.assert_not_called()
        self.assertEqual(self.path.read_bytes(), original)

    def test_wrong_source_account_region_table_schema_or_typed_generation_cannot_resume(self):
        cases = [
            {**self.record, "schema_version": "2.0.0"}, {**self.record, "source_revision": "b" * 40},
            {**self.record, "account": "999999999999"}, {**self.record, "region": "us-west-2"},
            {**self.record, "control_table": "another-control-table"}, {**self.record, "unexpected": "field"},
            {key: value for key, value in self.record.items() if key != "schema_version"},
            {**self.record, "ownership": {**TOKEN, "generation": True}},
            {**self.record, "ownership": {**TOKEN, "generation": 7.0}},
            {**self.record, "ownership": {**TOKEN, "generation": 0}},
            {**self.record, "ownership": {**TOKEN, "source_revision": "b" * 40}},
            {**self.record, "ownership": {**TOKEN, "unexpected": "field"}},
        ]
        for index, record in enumerate(cases):
            self.path.write_bytes(json.dumps(record).encode())
            with self.subTest(case=index), patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
                serverless.validate_resume_owner(Mock(), configuration(), outputs(), self.path)
            factory.assert_not_called()
        for prior in (None, {}, {**outputs(), "AdmissionProtocolVersion": "0"}):
            with self.subTest(prior=bool(prior)), patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
                serverless.validate_resume_owner(Mock(), configuration(), prior, self.path)
            factory.assert_not_called()

    def test_linked_shared_owner_or_oversize_proof_is_refused_before_control_reads(self):
        linked = self.work / "symlink-closure.json"
        linked.symlink_to(self.path)
        with patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
            serverless.validate_resume_owner(Mock(), configuration(), outputs(), linked)
        factory.assert_not_called()
        hard = self.work / "hard-closure.json"
        os.link(self.path, hard)
        with patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
            serverless.validate_resume_owner(Mock(), configuration(), outputs(), self.path)
        factory.assert_not_called()
        hard.unlink()
        self.path.chmod(0o644)
        with patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
            serverless.validate_resume_owner(Mock(), configuration(), outputs(), self.path)
        factory.assert_not_called()
        self.path.chmod(0o600)
        with patch.object(os, "getuid", return_value=os.getuid() + 1), patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
            serverless.validate_resume_owner(Mock(), configuration(), outputs(), self.path)
        factory.assert_not_called()
        for raw in (b'x' * 65537, b'{"schema_version":"1.0.0","schema_version":"2.0.0"}', b'{"ownership":NaN}', b'[]'):
            self.path.write_bytes(raw)
            with self.subTest(size=len(raw)), patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
                serverless.validate_resume_owner(Mock(), configuration(), outputs(), self.path)
            factory.assert_not_called()

    def test_changed_live_owner_generation_or_open_state_is_never_reclosed(self):
        for reason in ("different closed owner", "different closed generation", "admission is open"):
            store = Mock()
            store.require_closed.side_effect = control.ControlUnavailable(reason)
            with self.subTest(reason=reason), patch.object(serverless, "control_store", return_value=store), self.assertRaises(control.ControlUnavailable):
                serverless.validate_resume_owner(Mock(), configuration(), outputs(), self.path)
            store.close_admission.assert_not_called()
            store.reopen_admission.assert_not_called()

    def test_invalid_resume_precedes_registry_images_and_every_cloud_mutation(self):
        self.path.write_bytes(json.dumps({**self.record, "ownership": {**TOKEN, "generation": 7.0}}).encode())
        args = SimpleNamespace(gate_evidence=Path("fictional-gates.json"), establish_new=False, resume_owner=self.path)
        with patch.object(serverless, "ROOT", self.work), \
                patch.object(serverless.platform, "require_clean_source"), \
                patch.object(serverless, "verify_serverless_gates", return_value=ServerlessStageGateTests().proof()), \
                patch.object(serverless, "stable_stack", return_value=outputs()), \
                patch.object(serverless, "preflight", return_value=configuration()), \
                patch.object(serverless, "deploy_stack") as stack, \
                patch.object(serverless, "build_images") as images, \
                patch.object(serverless.platform, "run") as command, \
                patch.object(serverless, "control_store") as factory, self.assertRaises(Gate):
            serverless.deploy(args, configuration(), Mock(), {"estimated_monthly_usd": 25})
        stack.assert_not_called()
        images.assert_not_called()
        command.assert_not_called()
        factory.assert_not_called()
        self.assertFalse((self.work / ".local").exists())

    def test_owned_persistence_is_private_immutable_and_idempotent_for_exact_wire(self):
        target = self.work / "fresh-closure.json"
        serverless.write_owned_receipt(target, self.record)
        original = target.read_bytes()
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        serverless.write_owned_receipt(target, self.record)
        self.assertEqual(target.read_bytes(), original)
        with self.assertRaises(Gate):
            serverless.write_owned_receipt(target, {**self.record, "ownership": {**TOKEN, "generation": 8}})
        self.assertEqual(target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
