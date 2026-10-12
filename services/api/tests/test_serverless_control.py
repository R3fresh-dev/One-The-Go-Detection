"""Unit interleavings against a semantic in-memory DynamoDB test double.

These tests verify the fencing protocol; they are not live AWS acceptance.
"""

from copy import deepcopy
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from uuid import UUID

from botocore.exceptions import ClientError, EndpointConnectionError
import pytest

from otgd import serverless_control as control


LEASE_A = "10000000-0000-0000-0000-000000000001"
LEASE_B = "10000000-0000-0000-0000-000000000002"


def aws_error(code, operation="TransactWriteItems", **fields):
    return ClientError({"Error": {"Code": code}, **fields}, operation)


class MetadataTable:
    """Atomic transactions and compare-and-set under a shared lock."""

    def __init__(self, page_size=64):
        self.items = {}
        self.lock = threading.Lock()
        self.calls = []
        self.page_size = page_size
        self.failures = []
        self.after_query = None

    def transact_write_items(self, **request):
        self.calls.append(("transaction", deepcopy(request)))
        if self.failures:
            raise self.failures.pop(0)
        update, put = request["TransactItems"]
        item = deepcopy(put["Put"]["Item"])
        with self.lock:
            if item["SK"]["S"] in self.items:
                raise aws_error("TransactionCanceledException", CancellationReasons=[{"Code": "None"}, {"Code": "ConditionalCheckFailed"}])
            metadata = self.items.setdefault("control", control._key("control"))
            epoch = int(metadata.get("epoch", {"N": "0"})["N"])
            if epoch >= control.MAX_EPOCH:
                raise aws_error("TransactionCanceledException")
            metadata["epoch"] = {"N": str(epoch + 1)}
            metadata["nextWakeAt"] = deepcopy(update["Update"]["ExpressionAttributeValues"][":now"])
            self.items[item["SK"]["S"]] = item
        return {}

    def delete_item(self, **request):
        self.calls.append(("delete", deepcopy(request)))
        with self.lock:
            self.items.pop(request["Key"]["SK"]["S"], None)
        return {}

    def get_item(self, **request):
        self.calls.append(("get", deepcopy(request)))
        assert request["ConsistentRead"] is True
        with self.lock:
            item = self.items.get(request["Key"]["SK"]["S"])
            return {"Item": deepcopy(item)} if item else {}

    def query(self, **request):
        self.calls.append(("query", deepcopy(request)))
        assert request["ConsistentRead"] is True
        assert request["ExpressionAttributeValues"][":pk"] == {"S": "runtime"}
        assert request["ExpressionAttributeValues"][":prefix"] == {"S": "lease#"}
        with self.lock:
            items = [deepcopy(item) for key, item in sorted(self.items.items()) if key.startswith("lease#")]
        cursor = request.get("ExclusiveStartKey", {}).get("SK", {}).get("S", "")
        items = [item for item in items if item["SK"]["S"] > cursor]
        size = min(self.page_size, request["Limit"])
        page = {"Items": items[:size]}
        if len(items) > size:
            page["LastEvaluatedKey"] = {key: page["Items"][-1][key] for key in ("PK", "SK")}
        if self.after_query:
            self.after_query()
        return page

    def update_item(self, **request):
        self.calls.append(("update", deepcopy(request)))
        values = request["ExpressionAttributeValues"]
        with self.lock:
            metadata = self.items.get("control", {})
            if Decimal(metadata.get("epoch", {"N": "0"})["N"]) != Decimal(values[":epoch"]["N"]):
                raise aws_error("ConditionalCheckFailedException", "UpdateItem")
            for field, placeholder in [("nextWakeAt", ":oldwake"), ("lastReconciledAt", ":oldreconciled")]:
                expected = values.get(placeholder)
                if expected != metadata.get(field):
                    # DynamoDB compares numbers by value, not lexical formatting.
                    if expected is None or metadata.get(field) is None or Decimal(expected["N"]) != Decimal(metadata[field]["N"]):
                        raise aws_error("ConditionalCheckFailedException", "UpdateItem")
            metadata = self.items.setdefault("control", control._key("control"))
            metadata["epoch"] = deepcopy(values[":epoch"])
            metadata["lastReconciledAt"] = deepcopy(values[":now"])
            if ":wake" in values:
                metadata["nextWakeAt"] = deepcopy(values[":wake"])
            else:
                metadata.pop("nextWakeAt", None)
        return {}


@pytest.fixture
def metadata():
    return MetadataTable()


@pytest.fixture
def store(metadata):
    return control.ControlStore(metadata, "test-control")


def test_producer_uses_atomic_epoch_and_lease_and_release_keeps_wake(store, metadata):
    lease = store.acquire(LEASE_A, deadline=150, now=100, kind="worker")
    assert lease == control.ProducerLease(LEASE_A, 100, 180, "worker")
    transaction = metadata.calls[0][1]
    assert transaction["ClientRequestToken"] == LEASE_A
    assert len(transaction["TransactItems"]) == 2
    assert metadata.items["control"]["epoch"] == {"N": "1"}
    assert store.snapshot(now=100).active_leases == (lease,)
    store.release(LEASE_A)
    store.release(LEASE_A)
    snapshot = store.snapshot(now=101)
    assert snapshot.epoch == 1 and snapshot.next_wake_at == 100
    assert not snapshot.active_leases


def test_crashed_producer_expires_after_absolute_lambda_deadline(store):
    lease = store.acquire(LEASE_A, now=100.25)
    assert lease.expires_at == 1031
    assert lease.expires_at >= 100.25 + 900 + 30
    assert store.snapshot(now=1030.9).active_leases == (lease,)
    assert not store.snapshot(now=1031).active_leases


@pytest.mark.parametrize("deadline", [100, 99, 1001, float("nan"), float("inf"), True, "110"])
def test_invocation_deadline_is_bounded_before_any_aws_call(store, metadata, deadline):
    with pytest.raises(control.ControlMetadataError):
        store.acquire(LEASE_A, deadline=deadline, now=100)
    assert not metadata.calls


def test_release_removes_only_its_own_producer(store):
    store.acquire(LEASE_A, now=100)
    survivor = store.acquire(LEASE_B, now=100)
    store.release(LEASE_A)
    assert store.snapshot(now=101).active_leases == (survivor,)


def test_producer_started_and_committed_during_sql_snapshot_rejects_quiet(store):
    before_sql = store.snapshot(now=100)
    store.acquire(LEASE_A, now=101)
    store.release(LEASE_A)
    assert not store.mark_reconciled(before_sql, None, now=102)
    assert store.snapshot(now=102).next_wake_at == 101


def test_simultaneous_producer_and_quiet_publication_preserve_immediate_wake(store):
    before_sql = store.snapshot(now=100)
    barrier = threading.Barrier(2)

    def produce():
        barrier.wait()
        store.acquire(LEASE_A, now=101)
        store.release(LEASE_A)

    def reconcile():
        barrier.wait()
        return store.mark_reconciled(before_sql, None, now=101)

    with ThreadPoolExecutor(max_workers=2) as executor:
        producer = executor.submit(produce)
        reconciler = executor.submit(reconcile)
        producer.result()
        reconciler.result()
    snapshot = store.snapshot(now=102)
    assert snapshot.epoch == 1 and snapshot.next_wake_at == 101


def test_active_leases_prevent_quiet_without_writing(store, metadata):
    store.acquire(LEASE_A, now=100)
    snapshot = store.snapshot(now=101)
    count = len(metadata.calls)
    assert not store.mark_reconciled(snapshot, None, now=102)
    assert len(metadata.calls) == count


def test_quiet_can_initialize_control_and_stale_maintenance_cannot_overwrite(store):
    initial = store.snapshot(now=100)
    assert store.mark_reconciled(initial, 150, now=101)
    assert not store.mark_reconciled(initial, None, now=102)
    current = store.snapshot(now=102)
    assert current.next_wake_at == 150 and current.last_reconciled_at == 101
    assert store.mark_reconciled(current, None, now=103)
    assert store.snapshot(now=104).next_wake_at is None


def test_epoch_recheck_retries_snapshot_when_producer_arrives_during_query(store, metadata):
    calls = []

    def interleave():
        calls.append(True)
        if len(calls) == 1:
            store.acquire(LEASE_A, now=100)

    metadata.after_query = interleave
    snapshot = store.snapshot(now=100)
    assert snapshot.epoch == 1 and len(snapshot.active_leases) == 1
    assert len(calls) == 2


def test_never_stable_epoch_fails_closed_with_bounded_reads(store, metadata):
    index = [1]

    def interleave():
        store.acquire(str(UUID(int=index[0])), now=100)
        index[0] += 1

    metadata.after_query = interleave
    with pytest.raises(control.ControlUnavailable, match="stabilize"):
        store.snapshot(now=100)
    assert sum(name == "query" for name, _ in metadata.calls) == control.MAX_ATTEMPTS


def test_paginated_snapshot_includes_active_lease_on_last_page(store, metadata):
    metadata.page_size = 1
    store.acquire(LEASE_A, deadline=101, now=100)
    active = store.acquire(LEASE_B, deadline=200, now=100)
    snapshot = store.snapshot(now=132)
    assert snapshot.active_leases == (active,)
    queries = [request for name, request in metadata.calls if name == "query"]
    assert len(queries) == 2 and "ExclusiveStartKey" in queries[1]


def test_metadata_pagination_limit_fails_closed(store, metadata, monkeypatch):
    monkeypatch.setattr(control, "MAX_QUERY_PAGES", 1)
    metadata.page_size = 1
    store.acquire(LEASE_A, now=100)
    store.acquire(LEASE_B, now=100)
    with pytest.raises(control.ControlMetadataError, match="pagination"):
        store.snapshot(now=101)


def test_repeated_pagination_cursor_and_excessive_record_count_fail_closed(store, metadata, monkeypatch):
    store.acquire(LEASE_A, now=100)
    original = metadata.query

    def repeated(**request):
        page = original(**request)
        page["Items"] = []
        page["LastEvaluatedKey"] = control._key("lease#" + LEASE_A)
        return page

    monkeypatch.setattr(metadata, "query", repeated)
    with pytest.raises(control.ControlMetadataError, match="Repeated"):
        store.snapshot(now=101)
    monkeypatch.setattr(metadata, "query", original)
    monkeypatch.setattr(control, "MAX_LEASE_ITEMS", 0)
    with pytest.raises(control.ControlMetadataError, match="read bound"):
        store.snapshot(now=101)


@pytest.mark.parametrize("changes", [
    {"request": {"S": "forbidden application metadata"}},
    {"expiresAt": {"N": "10000"}},
    {"expiresAt": {"N": "NaN"}},
    {"expiresAt": {"N": "100.2"}},
    {"kind": {"S": "unknown"}},
    {"PK": {"S": "other"}},
    {"SK": {"S": "lease#account-123"}},
    {"acquiredAt": {"S": "100"}},
    {"acquiredAt": {"N": "-1"}},
])
def test_malformed_producer_metadata_fails_closed(store, metadata, changes):
    store.acquire(LEASE_A, now=100)
    metadata.items["lease#" + LEASE_A].update(changes)
    with pytest.raises(control.ControlMetadataError):
        store.snapshot(now=101)


@pytest.mark.parametrize("changes", [
    {"epoch": {"N": "1.5"}},
    {"epoch": {"N": str(control.MAX_EPOCH + 1)}},
    {"epoch": {"N": "Infinity"}},
    {"nextWakeAt": {"N": "-1"}},
    {"lastReconciledAt": {"N": "1e999"}},
    {"application_id": {"S": "forbidden"}},
])
def test_malformed_control_metadata_fails_closed(store, metadata, changes):
    store.acquire(LEASE_A, now=100)
    metadata.items["control"].update(changes)
    with pytest.raises(control.ControlMetadataError):
        store.snapshot(now=101)


def test_acquire_retries_only_transaction_conflicts_with_same_idempotency_token(store, metadata, monkeypatch):
    metadata.failures = [aws_error("TransactionConflictException"), aws_error("TransactionCanceledException", CancellationReasons=[{"Code": "TransactionConflict"}])]
    sleeps = []
    monkeypatch.setattr(control.time, "sleep", sleeps.append)
    store.acquire(LEASE_A, now=100)
    transactions = [request for name, request in metadata.calls if name == "transaction"]
    assert len(transactions) == 3 and transactions[0] == transactions[1] == transactions[2]
    assert sleeps == [0.01, 0.02]
    assert store.snapshot(now=101).epoch == 1


@pytest.mark.parametrize("failure", [aws_error("AccessDeniedException"), EndpointConnectionError(endpoint_url="https://dynamodb.example")])
def test_acquire_failure_prevents_sql_body_and_does_not_release(store, metadata, monkeypatch, failure):
    metadata.failures = [failure]
    monkeypatch.setattr(control, "control_store", lambda: store)
    sql_calls = []
    with pytest.raises(control.ControlUnavailable):
        with control.producer_lease(now=100, lease_id=LEASE_A):
            sql_calls.append("SQL")
    assert not sql_calls
    assert not any(name == "delete" for name, _ in metadata.calls)


def test_context_deadline_and_release_on_body_failure(store, monkeypatch):
    monkeypatch.setattr(control, "control_store", lambda: store)

    class Context:
        def get_remaining_time_in_millis(self):
            return 1250

    with pytest.raises(RuntimeError, match="SQL failed"):
        with control.producer_lease(Context(), now=100, lease_id=LEASE_A, kind="worker") as lease:
            assert lease.expires_at == 132
            raise RuntimeError("SQL failed")
    assert not store.snapshot(now=101).active_leases


@pytest.mark.parametrize("value", ["patient-id", LEASE_A.upper(), "", None])
def test_invalid_lease_ids_are_rejected(store, metadata, value):
    # UUID_A contains digits only; uppercase is unchanged and valid.
    if value == LEASE_A:
        value = "ABCDEFAB-0000-0000-0000-000000000001"
    with pytest.raises(control.ControlMetadataError):
        store.acquire(value, now=100)
    assert not metadata.calls


def test_control_only_client_never_loads_application_settings(monkeypatch):
    from otgd import config, storage

    monkeypatch.setenv("OTGD_SERVERLESS_CONTROL_ONLY", "true")
    monkeypatch.setenv("AWS_REGION", "us-east-2")
    monkeypatch.setattr(config, "settings", lambda: pytest.fail("Control-only loaded settings"))
    monkeypatch.setattr(storage, "client", lambda *args: pytest.fail("Control-only used application client"))
    calls = []
    client = object()

    def boto_client(service, **kwargs):
        calls.append((service, kwargs))
        return client

    monkeypatch.setattr(control.boto3, "client", boto_client)
    assert control.ControlStore(table_name="test-control").client is client
    assert calls[0][0] == "dynamodb"
    assert calls[0][1]["config"].ignore_configured_endpoint_urls is True
    assert calls[0][1]["config"].read_timeout == 10
    assert set(calls[0][1]) == {"region_name", "config"}


def test_control_only_import_does_not_import_sql_or_runtime_settings():
    script = """
import sys
from otgd.serverless_control import control_handler
assert not {'otgd.db', 'otgd.worker', 'otgd.main', 'otgd.config', 'otgd.storage'}.intersection(sys.modules)
"""
    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        env={**os.environ, "PYTHONPATH": str(Path(control.__file__).parents[1]), "OTGD_SERVERLESS_CONTROL_ONLY": "true"},
        capture_output=True,
        timeout=10,
    )


def test_regular_client_uses_shared_storage_sdk(monkeypatch):
    from otgd import storage

    monkeypatch.delenv("OTGD_SERVERLESS_CONTROL_ONLY", raising=False)
    client = object()
    calls = []
    monkeypatch.setattr(storage, "client", lambda service: calls.append(service) or client)
    assert control.ControlStore(table_name="test-control").client is client
    assert calls == ["dynamodb"]


@pytest.mark.parametrize("wake, reconciled, lease, expected", [
    (None, 99, False, "idle"),
    (101, 99, False, "idle"),
    (100, 99, False, "scheduled"),
    (None, None, False, "scheduled"),
    (None, 0, False, "scheduled"),
    (None, 99, True, "scheduled"),
])
def test_control_handler_only_reads_metadata_and_invokes_due_work(monkeypatch, wake, reconciled, lease, expected):
    current = 4000 if reconciled == 0 else 100
    snapshot = control.ControlSnapshot(1, wake, reconciled, (control.ProducerLease(LEASE_A, 99, 999),) if lease else (), current)
    reads = []

    class ReadOnlyStore:
        def snapshot(self, now):
            reads.append(now)
            return snapshot

    invokes = []
    payload = io.BytesIO()

    class Lambda:
        def invoke(self, **request):
            invokes.append(request)
            return {"StatusCode": 202, "Payload": payload}

    monkeypatch.setattr(control, "_now", lambda value=None: current)
    monkeypatch.setattr(control, "control_store", ReadOnlyStore)
    monkeypatch.setattr(control, "_sdk_client", lambda service: Lambda() if service == "lambda" else pytest.fail("unexpected service"))
    monkeypatch.setenv("OTGD_SERVERLESS_DISPATCH_FUNCTION_ARN", "arn:aws:lambda:us-east-2:123456789012:function:test-dispatch")
    assert control.control_handler({}, None) == {"status": expected, "database_accessed": False}
    assert reads == [current]
    assert len(invokes) == (expected == "scheduled")
    if invokes:
        assert invokes[0]["FunctionName"] == "arn:aws:lambda:us-east-2:123456789012:function:test-dispatch"
        assert invokes[0]["InvocationType"] == "Event"
        assert json.loads(invokes[0]["Payload"]) == {"operation": "sweep"}
        assert payload.closed


def test_control_handler_rejects_unaccepted_invoke_and_metadata_failure(monkeypatch):
    class Store:
        def snapshot(self, now):
            return control.ControlSnapshot(0, None, None, (), now)

    class Lambda:
        def invoke(self, **request):
            return {"StatusCode": 200}

    monkeypatch.setattr(control, "control_store", Store)
    monkeypatch.setattr(control, "_sdk_client", lambda service: Lambda())
    monkeypatch.setenv("OTGD_SERVERLESS_DISPATCH_FUNCTION_ARN", "arn:aws:lambda:us-east-2:123456789012:function:test-dispatch")
    with pytest.raises(control.ControlUnavailable, match="not accepted"):
        control.control_handler({}, None)

    class BrokenStore:
        def snapshot(self, now):
            raise control.ControlUnavailable("metadata unavailable")

    monkeypatch.setattr(control, "control_store", BrokenStore)
    with pytest.raises(control.ControlUnavailable, match="metadata unavailable"):
        control.control_handler({}, None)


def test_control_handler_requires_dispatcher_and_does_not_invoke_admin_maintenance(monkeypatch):
    class Store:
        def snapshot(self, now):
            return control.ControlSnapshot(0, None, None, (), now)

    monkeypatch.setattr(control, "control_store", Store)
    monkeypatch.delenv("OTGD_SERVERLESS_DISPATCH_FUNCTION_ARN", raising=False)
    monkeypatch.setenv("OTGD_SERVERLESS_MAINTENANCE_FUNCTION", "admin-must-not-be-invoked")
    monkeypatch.setattr(control, "_sdk_client", lambda service: pytest.fail("must not invoke admin maintenance"))
    with pytest.raises(control.ControlMetadataError, match="dispatcher function ARN"):
        control.control_handler({}, None)
