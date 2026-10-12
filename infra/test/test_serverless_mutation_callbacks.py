"""Offline regressions for admission immediately before provider mutations.

These are caller seam checks, not live AWS or GitHub gate qualification.
"""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from deploy import serverless, serverless_recovery
from deploy.provenance import Gate
from infra.test import test_serverless_drain as fixtures


class MutationCallbackTests(unittest.TestCase):
    def test_each_quiescence_mutation_rechecks_admission_and_failure_stops_later_writes(self):
        expected = ["close", "schedule", "mapping"] + [
            "stop-" + fixtures.outputs()[key]
            for key in ("ApiFunction", "WorkerFunction", "DispatcherFunction", "ControlFunction")
        ]
        for failure in range(1, 8):
            composer = fixtures.ServerlessDrainTests()
            aws, functions, schedules, _, store, _ = composer.fixture()
            executed, checks = [], []
            state = {"closed": False}
            def mutation(name):
                self.assertEqual(len(checks), len(executed) + 1,
                    "Each mutation needs its own fresh admission check")
                executed.append(name)
            def close(owner):
                self.assertEqual(owner, fixtures.OWNER)
                mutation("close")
                state["closed"] = True
                return dict(fixtures.TOKEN)
            store.close_admission.side_effect = close
            schedules.disable_rule.side_effect = lambda **kwargs: mutation("schedule")
            functions.update_event_source_mapping.side_effect = lambda **kwargs: mutation("mapping")
            functions.put_function_concurrency.side_effect = lambda **kwargs: mutation("stop-" + kwargs["FunctionName"])
            def readmission():
                checks.append("admitted")
                if len(checks) == failure:
                    raise Gate("Fictional current main gate changed")
            with self.subTest(boundary=failure), patch.object(serverless, "control_store", return_value=store), self.assertRaises(Gate):
                serverless.drain(aws, fixtures.outputs(), source_revision=fixtures.REVISION,
                    owner_id=fixtures.OWNER, readmission=readmission)
            self.assertEqual(executed, expected[:failure - 1])
            self.assertEqual(len(checks), failure)
            self.assertEqual(state["closed"], failure > 1)
            store.reopen_admission.assert_not_called()
            store.snapshot.assert_not_called()
            self.assertTrue(all(call.kwargs["ReservedConcurrentExecutions"] == 0
                for call in functions.put_function_concurrency.call_args_list))

    def test_main_change_during_function_lookup_is_rechecked_before_lambda_invoke(self):
        composer = fixtures.ServerlessMaintenanceReceiptTests()
        composer.setUp()
        self.addCleanup(composer.doCleanups)
        aws, functions, _, _ = composer.fixture()
        state = {"head": fixtures.REVISION}
        expected = composer.function()
        def slow_lookup(**kwargs):
            state["head"] = "b" * 40
            return expected
        functions.get_function.side_effect = slow_lookup
        checks = []
        def readmission():
            checks.append(state["head"])
            if state["head"] != fixtures.REVISION:
                raise Gate("Main changed during the protected function lookup")
        with patch.object(serverless, "control_store", return_value=Mock()), self.assertRaises(Gate):
            serverless.invoke_maintenance(aws, fixtures.configuration(), fixtures.outputs(),
                "admission", composer.work, ownership=dict(fixtures.TOKEN), readmission=readmission)
        functions.get_function.assert_called_once()
        self.assertEqual(checks, ["b" * 40])
        functions.invoke.assert_not_called()
        self.assertEqual(list(composer.work.iterdir()), [])

    def test_all_mutating_helpers_reject_missing_callback_before_sdk_or_local_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            operations = {
                "stack": lambda aws: serverless.deploy_stack(aws, serverless.STACK, {"Resources": {}},
                    fixtures.configuration(), readmission=None),
                "images": lambda aws: serverless.build_images(aws, fixtures.configuration(),
                    {"RepositoryUri": fixtures.URI}, work / "missing-source.tar", readmission=None),
                "web": lambda aws: serverless.build_and_publish_web(aws, fixtures.configuration(),
                    fixtures.outputs(), work / "missing-source.tar", work, readmission=None),
                "drain": lambda aws: serverless.drain(aws, fixtures.outputs(), source_revision=fixtures.REVISION,
                    owner_id=fixtures.OWNER, readmission=None),
                "maintenance": lambda aws: serverless.invoke_maintenance(aws, fixtures.configuration(),
                    fixtures.outputs(), "admission", work, ownership=dict(fixtures.TOKEN), readmission=None),
                "recovery": lambda aws: serverless_recovery.recover_initial(aws, fixtures.configuration(),
                    work / "recovery.json", readmission=None),
            }
            for name, operation in operations.items():
                aws = Mock()
                with self.subTest(helper=name), patch.object(serverless.platform, "run") as commands, \
                        patch.object(serverless.subprocess, "run") as build, self.assertRaises(Gate):
                    operation(aws)
                aws.client.assert_not_called()
                commands.assert_not_called()
                build.assert_not_called()
                self.assertEqual(list(work.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
