"""Lambda delivery decisions and due SQL work; no live AWS acceptance claims."""
from contextlib import contextmanager
import json
from types import SimpleNamespace

import pytest

from otgd import serverless_control as control, serverless_worker as adapter, worker
from otgd.db import Artifact, Job, Outbox, factory, uid

REAL_EMIT_METRICS = adapter.emit_operational_metrics


class Context:
    def get_remaining_time_in_millis(self):
        return 180_000


def delivery(body=None, **overrides):
    return {"messageId": uid(), "eventSource": "aws:sqs", "receiptHandle": "fictional-receipt",
            "body": json.dumps(body or {"schema_version": "1.0.0", "job_id": uid()}), **overrides}


@pytest.fixture(autouse=True)
def metrics_boundary(monkeypatch):
    monkeypatch.setattr(adapter, "emit_operational_metrics", lambda db=None: None)


@pytest.mark.parametrize("result,ack", [("completed", True), ("terminal", True), ("deferred", True),
                                        ("failed", False), ("busy", False), ("lease_lost", False)])
def test_only_durable_worker_outcomes_ack_and_lease_released_after_joined_sql(monkeypatch, result, ack):
    events = []
    monkeypatch.setattr(control, "acquire_lease", lambda kind, identity, deadline: events.append("acquired"))
    monkeypatch.setattr(control, "release_lease", lambda identity: events.append("released"))
    monkeypatch.setattr(adapter, "dispose_database", lambda: events.append("disposed"))

    def execute(identity, receipt, *, heartbeat_join_timeout):
        assert events == ["acquired"] and heartbeat_join_timeout is None
        assert receipt == "fictional-receipt"
        events.append("committed-and-joined")
        return result

    monkeypatch.setattr(worker, "run_job", execute)
    row = delivery()
    response = adapter.sqs_handler({"Records": [row]}, Context())
    assert response["batchItemFailures"] == ([] if ack else [{"itemIdentifier": row["messageId"]}])
    assert events == ["acquired", "committed-and-joined", "disposed", "released"]


def test_acquisition_failure_does_not_call_sql_worker(monkeypatch):
    def unavailable(*args):
        raise control.ControlUnavailable()

    monkeypatch.setattr(control, "acquire_lease", unavailable)
    monkeypatch.setattr(worker, "run_job", lambda *args, **kwargs: pytest.fail("SQL cannot run before metadata acquisition"))
    rows = [delivery(), delivery()]
    assert adapter.sqs_handler({"Records": rows}, Context())["batchItemFailures"] == [
        {"itemIdentifier": row["messageId"]} for row in rows]


@pytest.mark.parametrize("change", [{"body": "not-json"}, {"body": "x" * 8193}, {"eventSource": "other"},
                                   {"receiptHandle": ""}, {"body": json.dumps({"schema_version": "1.0.0", "job_id": "not-uuid"})}])
def test_malformed_delivery_never_acquires_a_producer_lease(monkeypatch, change):
    monkeypatch.setattr(control, "acquire_lease", lambda *args: pytest.fail("Malformed delivery cannot touch SQL"))
    row = delivery(**change)
    assert adapter.sqs_handler({"Records": [row]}, Context())["batchItemFailures"] == [{"itemIdentifier": row["messageId"]}]


def test_deadline_validation_and_worker_exception_return_failures(monkeypatch):
    assert adapter.invocation_deadline(Context(), now=100) == 280
    for value in (0, True, 900001, "180000"):
        with pytest.raises(ValueError):
            adapter.invocation_deadline(SimpleNamespace(get_remaining_time_in_millis=lambda: value), now=100)
    monkeypatch.setattr(control, "acquire_lease", lambda *args: None)
    monkeypatch.setattr(control, "release_lease", lambda *args: None)
    monkeypatch.setattr(adapter, "dispose_database", lambda: None)
    def fail(*args, **kwargs):
        raise ConnectionError("fictional dependency outage")
    monkeypatch.setattr(worker, "run_job", fail)
    row = delivery()
    assert adapter.sqs_handler({"Records": [row]}, Context())["batchItemFailures"] == [{"itemIdentifier": row["messageId"]}]


def job(account, kind="export", **changes):
    return Job(id=uid(), account_id=account, generation=1, kind=kind, state="pending",
               body={"include_raw": False}, accepted=1000, cleanup_next_at=0, **changes)


def test_next_wake_uses_real_sql_outbox_deferral_leases_and_deletion_admission(client, account):
    with factory().begin() as db:
        first = job(account)
        blocked = job(account, "deletion", journal_accepted=False)
        db.add_all([first, blocked]); db.flush()
        db.add_all([Outbox(job_id=first.id, available=1300, lease_until=1400),
                    Outbox(job_id=blocked.id, available=0)])
        assert adapter.next_wake_at(db, 1000) == 1400
        blocked.journal_accepted = True
        db.flush()
        assert adapter.next_wake_at(db, 1000) == 1000


def test_running_claim_wakes_at_fence_lease_expiry_and_empty_db_only_safety(client, account):
    with factory().begin() as db:
        assert adapter.next_wake_at(db, 1000) == 4600
        current = job(account)
        current.state, current.lease_until = "running", 1120
        db.add(current); db.flush()
        assert adapter.next_wake_at(db, 1000) == 1120


def test_cleanup_wake_honors_ticket_margin_and_expired_export_real_predicates(client, account):
    with factory().begin() as db:
        artifact = Artifact(id=uid(), account_id=account, generation=1, session_id=uid(),
            bucket="fictional", key="fixture", version_id="fixture", sha256="1" * 64,
            size=1, media_type="application/pdf", kind="lab_report", state="quarantine",
            expires=1100, scope={}, cleanup_next_at=1300)
        db.add(artifact); db.flush()
        assert adapter.next_wake_at(db, 1000) == 1300
        expired = job(account, expires=1200)
        db.add(expired); db.flush()
        assert adapter.next_wake_at(db, 1000) == 1200
        expired.state = "expired"; db.flush()
        assert adapter.next_wake_at(db, 1000) == 1300


def snapshot(epoch=1, active=()):
    return control.ControlSnapshot(epoch, 1000, 0, active, 1000)


@pytest.mark.parametrize("concurrent", ["new-epoch", "previous-active"])
def test_sweep_cannot_mark_quiet_when_producer_commits_and_releases_during_sql(monkeypatch, concurrent):
    active = control.ProducerLease(uid(), 1000, 1930)
    before = snapshot(active=(active,) if concurrent == "previous-active" else ())
    after = snapshot(epoch=2 if concurrent == "new-epoch" else 1)
    states = iter([before, after])
    store = SimpleNamespace(snapshot=lambda: next(states),
                            mark_reconciled=lambda *args: pytest.fail("A raced SQL view cannot mark quiet"))
    monkeypatch.setattr(control, "control_store", lambda: store)
    monkeypatch.setattr(adapter, "next_wake_at", lambda *args: 4600)
    monkeypatch.setattr(adapter.time, "time", lambda: 1000)
    monkeypatch.setattr(adapter, "dispose_database", lambda: None)
    from otgd import db as database
    @contextmanager
    def opened():
        yield object()
    monkeypatch.setattr(database, "factory", lambda: opened)
    assert adapter.sweep(Context())["quiet_marked"] is False


def test_sweep_due_work_reconciles_after_own_lease_release(monkeypatch):
    events = []
    states = iter([snapshot(), snapshot(epoch=2), snapshot(epoch=2)])
    store = SimpleNamespace(snapshot=lambda: next(states),
        acquire=lambda *args, **kwargs: events.append("acquired"),
        release=lambda *args: events.append("released"),
        mark_reconciled=lambda *args: events.append("quiet") or True)
    monkeypatch.setattr(control, "control_store", lambda: store)
    due = iter([1000, 1500])
    monkeypatch.setattr(adapter, "next_wake_at", lambda *args: next(due))
    monkeypatch.setattr(adapter.time, "time", lambda: 1000)
    monkeypatch.setattr(adapter, "dispose_database", lambda: events.append("disposed"))
    monkeypatch.setattr(worker, "dispatch_once", lambda: events.append("dispatch"))
    monkeypatch.setattr(worker, "cleanup_once", lambda: events.append("cleanup") or {"attempted": 1, "failed": 0})
    from otgd import db as database
    @contextmanager
    def opened():
        yield object()
    monkeypatch.setattr(database, "factory", lambda: opened)
    result = adapter.sweep(Context())
    assert result["quiet_marked"] is True and result["next_wake_at"] == 1500
    assert events == ["acquired", "dispatch", "cleanup", "disposed", "released", "quiet"]


def test_sqs_heartbeat_preserves_sql_lease_and_extends_lambda_visibility(monkeypatch):
    values = []
    job_row = SimpleNamespace(lease_until=0)
    @contextmanager
    def opened():
        yield object()
    monkeypatch.setattr(worker, "factory", lambda: SimpleNamespace(begin=opened))
    monkeypatch.setattr(worker, "current", lambda *args: (object(), job_row))
    monkeypatch.setattr(worker, "now", lambda: 1000)
    monkeypatch.setattr(worker, "settings", lambda: SimpleNamespace(queue_url="fictional", serverless_queue_visibility=1200))
    monkeypatch.setattr(worker.storage, "client", lambda service: SimpleNamespace(change_message_visibility=lambda **kwargs: values.append(kwargs)))
    waits = iter([False, True])
    done = SimpleNamespace(wait=lambda timeout: next(waits))
    lost = SimpleNamespace(set=lambda: pytest.fail("Healthy heartbeat cannot lose its lease"))
    worker.heartbeat(object(), "fictional-receipt", done, lost)
    assert job_row.lease_until == 1120 and values[0]["VisibilityTimeout"] == 1200


def test_dispatcher_rejects_admin_operations_and_fences_before_publishing(monkeypatch):
    events = []
    monkeypatch.setattr(control, "acquire_lease", lambda *args: events.append("acquired"))
    monkeypatch.setattr(control, "release_lease", lambda *args: events.append("released"))
    monkeypatch.setattr(adapter, "dispose_database", lambda: events.append("disposed"))
    monkeypatch.setattr(worker, "dispatch_once", lambda: events.append("published"))
    for payload in ({"operation": "migrate"}, {"operation": "bootstrap"}, {"operation": "dispatch", "extra": True}):
        with pytest.raises(ValueError):
            adapter.dispatch_handler(payload, Context())
    assert events == []
    assert adapter.dispatch_handler({"operation": "dispatch"}, Context())["status"] == "passed"
    assert events == ["acquired", "published", "disposed", "released"]


def test_dispatcher_sweep_stays_app_role_and_admin_handler_rejects_schedules(monkeypatch):
    monkeypatch.setattr(adapter, "sweep", lambda context: {"status": "passed", "operation": "sweep"})
    assert adapter.dispatch_handler({"operation": "sweep"}, Context())["status"] == "passed"
    for operation in ("dispatch", "sweep"):
        with pytest.raises(ValueError):
            adapter.maintenance_handler({"operation": operation}, Context())


@pytest.mark.parametrize("operation", ["bootstrap", "migrate", "admission"])
def test_admin_maintenance_closes_sql_before_lease_release(client, monkeypatch, operation):
    events = []
    monkeypatch.setattr(control, "acquire_lease", lambda *args: events.append("acquired"))
    monkeypatch.setattr(control, "release_lease", lambda *args: events.append("released"))
    monkeypatch.setattr(adapter, "dispose_database", lambda: events.append("disposed"))
    if operation == "bootstrap":
        import runpy
        def initialize(*, cloud, establish_new):
            assert cloud is True and establish_new is False
            events.append("verified")
        monkeypatch.setattr(runpy, "run_path", lambda *args: {"initialize": initialize})
    elif operation == "migrate":
        import otgd.migrate
        monkeypatch.setattr(otgd.migrate, "migrate", lambda: events.append("verified"))
    else:
        import otgd.recovery_authority
        monkeypatch.setattr(otgd.recovery_authority, "require_authority", lambda db: events.append("verified"))
    assert adapter.maintenance_handler({"operation": operation}, Context()) == {"status": "passed", "operation": operation}
    assert events == ["acquired", "verified", "disposed", "released"]


def test_emf_contains_actual_sql_ages_and_no_identity_dimensions(client, account, monkeypatch, capsys):
    monkeypatch.setattr(adapter.time, "time", lambda: 2000)
    with factory().begin() as db:
        export = job(account)
        deletion = job(account, "deletion")
        db.add_all([export, deletion]); db.flush()
        db.add(Outbox(job_id=export.id, available=1500)); db.flush()
        REAL_EMIT_METRICS(db)
    body = json.loads(capsys.readouterr().out)
    assert body["OldestOutboxSeconds"] == 500
    assert body["OldestPrivacyJobSeconds"] == 1000
    assert body["CleanupOverdueCount"] == 0
    declaration = body["_aws"]["CloudWatchMetrics"][0]
    assert declaration["Namespace"] == "OTGD/serverless-development"
    assert declaration["Dimensions"] == [[]]
    assert set(body) == {"_aws", "OldestOutboxSeconds", "OldestPrivacyJobSeconds", "CleanupOverdueCount"}


def test_control_adapter_has_no_sql_side_effects(monkeypatch):
    monkeypatch.setattr(control, "control_handler", lambda event, context: {"status": "idle", "database_accessed": False})
    monkeypatch.setattr(adapter, "dispose_database", lambda: pytest.fail("Idle outside-VPC control cannot open or dispose SQL"))
    assert adapter.control_handler({}, Context()) == {"status": "idle", "database_accessed": False}


def test_admin_refresh_observes_rotating_secret_before_any_new_connection(monkeypatch):
    from otgd import db as database, config, serverless_lifecycle
    events = []
    monkeypatch.setenv("OTGD_SERVERLESS_MODE", "true")
    monkeypatch.setattr(serverless_lifecycle, "load_runtime_secrets", lambda *, force: events.append(("hydrate", force)))
    engine = lambda: SimpleNamespace(dispose=lambda: events.append("disposed"))
    engine.cache_info = lambda: SimpleNamespace(currsize=1)
    engine.cache_clear = lambda: events.append("engine-cleared")
    factory = lambda: pytest.fail("Refresh cannot open SQL")
    factory.cache_clear = lambda: events.append("factory-cleared")
    settings = lambda: pytest.fail("Refresh cannot construct settings before clearing the old cache")
    settings.cache_clear = lambda: events.append("settings-cleared")
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "factory", factory)
    monkeypatch.setattr(config, "settings", settings)
    adapter.refresh_admin_credentials()
    assert events == [("hydrate", True), "disposed", "factory-cleared", "engine-cleared", "settings-cleared"]
