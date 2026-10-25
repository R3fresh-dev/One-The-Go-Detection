"""Probe guard/protocol tests; these do not establish worker recovery."""

import importlib.util
import multiprocessing
import os
import signal
import unittest
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(__file__).parents[1] / "local/worker_interrupt_probe.py"
SPEC = importlib.util.spec_from_file_location("interrupt_probe", SOURCE)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)
NS = "otgd-worker-probe-0123456789abcdef"


def configuration(**changes):
    values = {
        "environment": "local",
        "db_url": lambda: (
            "postgresql+psycopg://fixture:fictional@localhost/otgd_worker_probe_0123456789abcdef"
        ),
        "database_name": "otgd_worker_probe_0123456789abcdef",
        "aws_endpoint_url": "http://localhost:4566",
        "queue_url": f"http://localhost:4566/queue/us-east-2/000000000000/{NS}-jobs",
        "dlq_url": f"http://localhost:4566/queue/us-east-2/000000000000/{NS}-dlq",
        "artifact_bucket": NS + "-artifacts",
        "export_bucket": NS + "-exports",
        "journal_bucket": NS + "-journal",
        "serverless_queue_visibility": 120,
        "serverless_mode": False,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def barrier_child(connection):
    probe.Barriers(connection, "after_claim", "job").hit("after_claim", fence=1)


class TargetTest(unittest.TestCase):
    def test_result_fixture_keeps_explicit_simulated_provenance_and_digest_lineage(
        self,
    ):
        value = probe.result_fixture("10000000-0000-4000-8000-000000000001")
        from otgd.canonical import digest

        self.assertEqual(value["snapshot"]["mode"], "synthetic")
        self.assertEqual(value["snapshot"]["profile"]["source"], "synthetic")
        self.assertEqual(value["manifest"]["context_sha256"], digest(value["context"]))
        self.assertEqual(
            value["context"]["profile_snapshot_sha256"],
            digest(value["snapshot"]["profile"]),
        )
        self.assertEqual(
            {item["sha256"] for item in value["manifest"]["attempts"]},
            {digest(item) for item in value["attempts"]},
        )
        self.assertTrue(
            all(item["source"] == "simulated" for item in value["attempts"])
        )

    def test_exact_disposable_local_namespace_only(self):
        env = {"OTGD_DISPOSABLE_DATABASE": "true"}
        self.assertEqual(
            probe.validate_target(configuration(), NS, True, env).database,
            "otgd_worker_probe_0123456789abcdef",
        )
        for changes in (
            {"environment": "test"},
            {"environment": "prod"},
            {"database_name": "otgd"},
            {"db_url": lambda: "postgresql+psycopg://x:y@localhost/otgd"},
            {
                "db_url": lambda: (
                    "postgresql+psycopg://x:y@localhost/otgd_worker_probe_0123456789abcdef?host=remote"
                )
            },
            {
                "db_url": lambda: (
                    "postgresql+psycopg://x:y@production/otgd_worker_probe_0123456789abcdef"
                )
            },
            {"aws_endpoint_url": "https://s3.amazonaws.com"},
            {"aws_endpoint_url": "http://localhost:4566/?host=remote"},
            {
                "queue_url": "http://localhost:4566/queue/us-east-2/000000000000/otgd-local-jobs"
            },
            {"queue_url": f"http://remote:4566/{NS}-jobs"},
            {"queue_url": f"http://localhost:4566/foreign/{NS}-jobs"},
            {"export_bucket": "otgd-local-exports"},
            {"journal_bucket": NS + "-exports"},
            {"serverless_queue_visibility": 1},
            {"serverless_mode": True},
        ):
            with self.subTest(changes=changes), self.assertRaises(RuntimeError):
                probe.validate_target(configuration(**changes), NS, True, env)
        for namespace, confirmed, environ in (
            (NS, False, env),
            (NS, True, {}),
            ("otgd-local", True, env),
        ):
            with self.assertRaises(RuntimeError):
                probe.validate_target(configuration(), namespace, confirmed, environ)

    def test_barrier_requires_matching_owned_pid_stage_and_job(self):
        event = {
            "protocol": 1,
            "pid": 123,
            "stage": "after_claim",
            "job_id": "job",
            "fence": 1,
        }
        probe.validate_event(event, 123, "after_claim", "job")
        for field, value in [
            ("pid", 124),
            ("stage", "after_commit"),
            ("job_id", "other"),
            ("protocol", 2),
        ]:
            with self.assertRaises(RuntimeError):
                probe.validate_event({**event, field: value}, 123, "after_claim", "job")

    def test_actual_owned_child_blocks_and_only_parent_can_release(self):
        parent, child = multiprocessing.Pipe()
        process = multiprocessing.Process(target=barrier_child, args=(child,))
        process.start()
        try:
            self.assertTrue(parent.poll(5))
            event = parent.recv()
            probe.validate_event(event, process.pid, "after_claim", "job")
            self.assertTrue(process.is_alive())
            parent.send({"release": "after_claim"})
            process.join(5)
            self.assertEqual(process.exitcode, 0)
        finally:
            if process.is_alive():
                os.kill(process.pid, signal.SIGKILL)
                process.join(5)
            parent.close()
            child.close()

    def test_receipts_are_one_way_fingerprints(self):
        self.assertEqual(len(probe.receipt_ref("SECRET-RECEIPT")), 64)
        self.assertNotIn("SECRET", probe.receipt_ref("SECRET-RECEIPT"))
