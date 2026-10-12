"""Bounded Lambda adapters for the existing durable SQL/SQS worker.

Imports stay lazy: the outside-VPC controller needs neither database settings
nor runtime secrets. DynamoDB holds only wake hints and invocation lease metadata;
SQL, immutable S3 versions and the independent journal remain authoritative.
"""
from __future__ import annotations

import math
import json
import os
from functools import lru_cache
import time
from uuid import UUID, uuid4


ACKNOWLEDGED = frozenset({"completed", "terminal", "deferred"})
SAFETY_SECONDS = 3600


def invocation_deadline(context, *, now=None):
    instant = time.time() if now is None else now
    remaining = context.get_remaining_time_in_millis()
    if type(remaining) is not int or not 0 < remaining <= 900_000:
        raise ValueError("A current bounded Lambda deadline is required")
    return instant + remaining / 1000


def dispose_database():
    from .db import engine

    if engine.cache_info().currsize:
        engine().dispose()


@lru_cache(maxsize=1)
def metric_collector():
    import runpy
    from .config import ROOT

    return runpy.run_path(str(ROOT / "scripts/publish-metrics.py"))["collect"]


def emit_operational_metrics(db=None):
    """CloudWatch EMF at a work boundary; idle control never touches SQL."""
    from .config import settings

    instant = time.time()
    if db is None:
        from .db import factory

        with factory()() as connection:
            metrics = metric_collector()(connection, instant)
    else:
        metrics = metric_collector()(db, instant)
    namespace = settings().serverless_metrics_namespace
    if namespace != "OTGD/serverless-development" or {row["MetricName"] for row in metrics} != {
        "OldestOutboxSeconds", "OldestPrivacyJobSeconds", "CleanupOverdueCount"
    } or any(not math.isfinite(row["Value"]) or row["Value"] < 0 for row in metrics):
        raise RuntimeError("Invalid aggregate operational metrics")
    body = {"_aws": {"Timestamp": int(instant * 1000), "CloudWatchMetrics": [{
        "Namespace": namespace, "Dimensions": [[]],
        "Metrics": [{"Name": row["MetricName"], "Unit": row["Unit"]} for row in metrics]}]},
        **{row["MetricName"]: row["Value"] for row in metrics}}
    print(json.dumps(body, allow_nan=False, separators=(",", ":")), flush=True)


def sqs_handler(event, context):
    """Return partial failures; a normal worker return is not blanket ACK."""
    from .canonical import strict_loads

    records = event.get("Records") if isinstance(event, dict) else None
    if not isinstance(records, list) or not 0 < len(records) <= 10:
        raise ValueError("A bounded SQS batch is required")
    identifiers = [row.get("messageId") if isinstance(row, dict) else None for row in records]
    if any(not isinstance(value, str) or not 0 < len(value) <= 128 for value in identifiers) or len(set(identifiers)) != len(identifiers):
        raise ValueError("Every SQS delivery requires its unique message identity")
    failed, jobs = [], []
    for row, identifier in zip(records, identifiers):
        try:
            if row.get("eventSource") != "aws:sqs" or not isinstance(row.get("receiptHandle"), str) or not row["receiptHandle"]:
                raise ValueError()
            raw = row.get("body")
            if not isinstance(raw, str) or len(raw.encode()) > 8192:
                raise ValueError()
            body = strict_loads(raw)
            if not isinstance(body, dict) or set(body) != {"schema_version", "job_id"} or body["schema_version"] != "1.0.0" or str(UUID(body["job_id"])) != body["job_id"]:
                raise ValueError()
            jobs.append((identifier, body["job_id"], row["receiptHandle"]))
        except (ValueError, KeyError, TypeError, AttributeError):
            failed.append(identifier)
    if not jobs:
        return {"batchItemFailures": [{"itemIdentifier": value} for value in failed]}
    from .serverless_control import acquire_lease, release_lease

    lease = str(uuid4())
    try:
        acquire_lease("worker", lease, invocation_deadline(context))
    except Exception:
        return {"batchItemFailures": [{"itemIdentifier": value} for value in identifiers]}
    try:
        from .worker import run_job

        for identifier, job_id, receipt in jobs:
            try:
                if context.get_remaining_time_in_millis() < 1000:
                    raise TimeoutError("Invocation budget exhausted")
                result = run_job(job_id, receipt, heartbeat_join_timeout=None)
                if result not in ACKNOWLEDGED:
                    failed.append(identifier)
            except Exception:
                failed.append(identifier)
        emit_operational_metrics()
    finally:
        # All run_job transactions and heartbeat threads have finished before
        # the control plane can decide this invocation is no longer a producer.
        dispose_database()
        release_lease(lease)
    return {"batchItemFailures": [{"itemIdentifier": value} for value in failed]}


def next_wake_at(db, instant):
    """Earliest eligible operation using the canonical worker predicates."""
    from sqlalchemy import case, func, select
    from .db import Artifact, Job, Outbox
    from .raw_retention import RawRetention

    candidates = [instant + SAFETY_SECONDS]

    def later(left, right):
        return case((left >= right, left), else_=right)

    def minimum(query):
        value = db.scalar(query)
        if value is not None:
            if not isinstance(value, (float, int)) or not math.isfinite(value):
                raise RuntimeError("Invalid due-work timestamp")
            candidates.append(float(value))

    # An unexpired dispatcher claim is not immediately eligible; its durable
    # lease expiry remains a wake deadline even when the SQS send was interrupted.
    minimum(select(func.min(later(Outbox.available, func.coalesce(Outbox.lease_until, 0)))).join(Job, Outbox.job_id == Job.id).where(
        Job.state.in_(("pending", "running")),
        (Job.kind != "deletion") | Job.journal_accepted.is_(True),
        Outbox.published.is_(None)))
    minimum(select(func.min(Job.lease_until)).where(Job.state == "running", Job.lease_until.is_not(None)))
    minimum(select(func.min(later(Artifact.expires + 60, Artifact.cleanup_next_at))).where(
        Artifact.state.in_(("quarantine", "cleanup_pending", "purged")),
        ~Artifact.id.in_(select(RawRetention.artifact_id))))
    minimum(select(func.min(later(Job.expires, Job.cleanup_next_at))).where(
        Job.kind == "export", Job.state != "expired", Job.expires.is_not(None)))
    minimum(select(func.min(Job.cleanup_next_at)).where(Job.kind == "deletion", Job.state == "completed"))
    minimum(select(func.min(RawRetention.cleanup_next_at)))
    minimum(select(func.min(Job.cleanup_next_at)).where(Job.kind == "export", Job.body["include_raw"].as_boolean().is_(True)))
    # Scheduler checks once per minute. Round up rather than scheduling before
    # strict timestamp comparisons become eligible in the canonical worker.
    return max(instant, math.ceil(min(candidates)))


def sweep(context):
    """Reconcile due work, then mark quiet only after a stable producer epoch."""
    from .serverless_control import control_store

    store = control_store()
    before = store.snapshot()
    baseline = before
    had_producer = bool(before.active_leases)
    owned = None
    next_wake = None
    outcome = {"attempted": 0, "failed": 0}
    try:
        from .db import factory

        instant = time.time()
        with factory()() as db:
            next_wake = next_wake_at(db, instant)
        if next_wake <= instant:
            candidate = str(uuid4())
            store.acquire(candidate, invocation_deadline(context), kind="maintenance")
            owned = candidate
            baseline = store.snapshot()
            had_producer = had_producer or any(row.lease_id != owned for row in baseline.active_leases)
            from .worker import cleanup_once, dispatch_once

            dispatch_once()
            outcome = cleanup_once()
            if outcome["failed"]:
                raise RuntimeError("Cleanup dependency failures require retry")
            with factory()() as db:
                next_wake = next_wake_at(db, time.time())
                emit_operational_metrics(db)
        else:
            emit_operational_metrics()
    finally:
        dispose_database()
        if owned is not None:
            store.release(owned)
    after = store.snapshot()
    quiet = False
    # A producer active before SQL may commit after our read and disappear
    # without another epoch increment. Its initial lease evidence forbids quiet.
    if not had_producer and after.epoch == baseline.epoch and not after.active_leases:
        quiet = store.mark_reconciled(after, next_wake)
    return {"operation": "sweep", "status": "passed", "quiet_marked": quiet,
            "next_wake_at": next_wake, "cleanup": outcome}


def maintenance_handler(event, context):
    if not isinstance(event, dict) or event.get("operation") not in ("bootstrap", "migrate", "admission"):
        raise ValueError("An explicit maintenance operation is required")
    operation = event["operation"]
    refresh_admin_credentials()
    from .serverless_control import acquire_lease, release_lease

    lease = str(uuid4())
    acquire_lease("maintenance", lease, invocation_deadline(context))
    try:
        if operation == "bootstrap":
            establish = event.get("establish_new", False)
            if type(establish) is not bool:
                raise ValueError("Journal establishment must be explicit")
            import runpy
            from .config import ROOT

            initialize = runpy.run_path(str(ROOT / "infra/local/bootstrap_resources.py"))["initialize"]
            initialize(cloud=True, establish_new=establish)
        elif operation == "migrate":
            from .migrate import migrate

            migrate()
        else:
            from .db import factory
            from .recovery_authority import require_authority

            with factory()() as db:
                require_authority(db)
        return {"operation": operation, "status": "passed"}
    finally:
        dispose_database()
        release_lease(lease)


def refresh_admin_credentials():
    """Aurora's rotating master secret must not outlive a warm invocation."""
    if os.environ.get("OTGD_SERVERLESS_MODE", "").strip().lower() not in ("true", "1", "yes", "on"):
        return
    from .serverless_lifecycle import load_runtime_secrets

    load_runtime_secrets(force=True)
    from .config import settings
    from .db import engine, factory

    if engine.cache_info().currsize:
        engine().dispose()
    factory.cache_clear()
    engine.cache_clear()
    settings.cache_clear()


def control_handler(event, context):
    from .serverless_control import control_handler as controller

    return controller(event, context)


def dispatch_handler(event, context):
    """App-role dispatcher exposes no bootstrap, migration or admission route."""
    if not isinstance(event, dict) or event not in ({"operation": "dispatch"}, {"operation": "sweep"}):
        raise ValueError("An explicit dispatcher operation is required")
    if event["operation"] == "sweep":
        return sweep(context)
    from .serverless_control import acquire_lease, release_lease

    lease = str(uuid4())
    acquire_lease("maintenance", lease, invocation_deadline(context))
    try:
        from .worker import dispatch_once

        dispatch_once()
        emit_operational_metrics()
        return {"operation": "dispatch", "status": "passed"}
    finally:
        dispose_database()
        release_lease(lease)
