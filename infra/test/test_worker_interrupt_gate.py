"""Canonical invocation guard checks; no live database/resource setup here."""

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(__file__).parents[1] / "local/worker_interrupt_gate.py"
SPEC = importlib.util.spec_from_file_location("interrupt_gate", SOURCE)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def config(**changes):
    values = {
        "environment": "local",
        "serverless_mode": False,
        "database_host": "postgres",
        "database_port": 5432,
        "database_name": "otgd",
        "database_user": "otgd_migrator",
        "aws_endpoint_url": "http://localstack:4566",
        "aws_region": "us-east-2",
        "db_url": lambda: (
            "postgresql+psycopg://otgd_migrator:fictional@postgres:5432/otgd"
        ),
        "artifact_bucket": "otgd-local-artifacts",
        "export_bucket": "otgd-local-exports",
        "journal_bucket": "otgd-local-deletion-journal",
        "queue_url": "http://localstack:4566/queue/us-east-2/000000000000/otgd-local-jobs",
        "dlq_url": "http://localstack:4566/queue/us-east-2/000000000000/otgd-local-dlq",
    }
    values.update(changes)
    return SimpleNamespace(**values)


class CanonicalGuardTest(unittest.TestCase):
    def test_only_exact_canonical_migration_configuration_and_project_admitted(self):
        gate.validate_invocation(config(), "otgd-local", True)
        for changes in (
            {"environment": "test"},
            {"environment": "prod"},
            {"database_user": "otgd_app"},
            {"database_host": "remote"},
            {"database_name": "otgd_ci"},
            {"serverless_mode": True},
            {"aws_endpoint_url": "http://localhost:4566"},
            {"export_bucket": "foreign"},
            {
                "db_url": lambda: (
                    "postgresql+psycopg://otgd_migrator:x@postgres/otgd?host=remote"
                )
            },
        ):
            with self.subTest(changes=changes), self.assertRaises(RuntimeError):
                gate.validate_invocation(config(**changes), "otgd-local", True)
        for project, confirmed in [("otgd-other", True), ("otgd-local", False)]:
            with self.assertRaises(RuntimeError):
                gate.validate_invocation(config(), project, confirmed)

    def test_per_run_targets_never_reference_canonical_database_role_or_buckets(self):
        values = gate.fixture_environment(
            config(),
            "0123456789abcdef",
            "random-app-password",
            "f" * 64,
            Path("/tmp/otgd-worker-probe-0123456789abcdef/capture-key.pem"),
        )
        self.assertEqual(
            values["OTGD_DATABASE_NAME"], "otgd_worker_probe_0123456789abcdef"
        )
        self.assertEqual(
            values["OTGD_APP_DATABASE_USER"], "otgd_worker_probe_app_0123456789abcdef"
        )
        self.assertNotEqual(values["OTGD_EXPORT_BUCKET"], "otgd-local-exports")
        self.assertEqual(values["OTGD_DISPOSABLE_DATABASE"], "true")
        self.assertEqual(values["OTGD_DATABASE_POOL_SIZE"], "1")
        with self.assertRaises(RuntimeError):
            gate.fixture_environment(
                config(), "canonical", "x", "f" * 64, Path("/tmp/key")
            )
