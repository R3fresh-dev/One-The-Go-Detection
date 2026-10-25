"""Real-process PostgreSQL/LocalStack crash probe, restricted to a fresh fixture.

PM creates the empty database first. --prepare-fixture provisions only the exact
dedicated names in the supplied configuration; normal runs never reset anything.
Production 120s leases/visibility, 30s heartbeat and five-receive redrive remain
unchanged. All barriers wrap real calls, and all SDK/SQL calls reach real services.
Unit protocol tests are separate from this acceptance run. No participant authority
or scientific validity is created by these fictional software fixtures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import re
import signal
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

MARKER = "fictional_worker_interrupt_fixture_v1"
STAGES = ("before_claim", "after_claim", "after_write", "after_commit", "before_delete")
LOCAL = {"localhost", "127.0.0.1", "::1", "postgres", "localstack"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def local_http(value):
    p = urlsplit(value or "")
    require(
        p.scheme == "http"
        and p.hostname in LOCAL
        and p.port == 4566
        and not p.username
        and not p.password
        and not p.query
        and not p.fragment,
        "Explicit local LocalStack endpoint required",
    )
    return p


def validate_target(cfg, namespace, confirmed, environ=None):
    from sqlalchemy.engine import make_url

    env = os.environ if environ is None else environ
    require(
        confirmed and env.get("OTGD_DISPOSABLE_DATABASE") == "true",
        "Explicit fictional/disposable confirmation required",
    )
    require(
        re.fullmatch(r"otgd-worker-probe-[0-9a-f]{16}", namespace or ""),
        "Unique exact worker fixture namespace required",
    )
    suffix = namespace.removeprefix("otgd-worker-probe-")
    url = make_url(cfg.db_url())
    require(
        cfg.environment == "local"
        and not cfg.serverless_mode
        and url.drivername == "postgresql+psycopg"
        and url.host in LOCAL
        and not url.query
        and url.database == "otgd_worker_probe_" + suffix
        and cfg.database_name == url.database,
        "Separate explicitly disposable local PostgreSQL database required",
    )
    endpoint = local_http(cfg.aws_endpoint_url)
    require(endpoint.path in ("", "/"), "Endpoint must have no path")
    for attr, tail in [("queue_url", "jobs"), ("dlq_url", "dlq")]:
        queue = local_http(getattr(cfg, attr))
        # Both LocalStack standard account paths and its reviewed queue endpoint.
        require(
            queue.hostname == endpoint.hostname
            and re.fullmatch(
                r"/(?:queue/[a-z0-9-]+/)?000000000000/"
                + re.escape(namespace + "-" + tail),
                queue.path,
            ),
            "Queue is outside exact dedicated fixture",
        )
    for attr, tail in [
        ("artifact_bucket", "artifacts"),
        ("export_bucket", "exports"),
        ("journal_bucket", "journal"),
    ]:
        require(
            getattr(cfg, attr) == namespace + "-" + tail,
            "Bucket is outside exact dedicated fixture",
        )
    require(
        cfg.serverless_queue_visibility == 120,
        "Production visibility must remain 120 seconds",
    )
    return url


def receipt_ref(receipt):
    return hashlib.sha256(receipt.encode()).hexdigest()


def source_manifest():
    from otgd import worker
    from otgd.config import ROOT

    files = [Path(__file__), Path(__file__).with_name("worker_interrupt_gate.py")]
    files.extend(Path(worker.__file__).parent.rglob("*.py"))
    files.extend((ROOT / "contracts").rglob("*.json"))
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(set(files))
        if path.is_file()
    }


class EvidenceEvents(list):
    """Durably record each observed barrier before the next action."""

    persist = None

    def append(self, event):
        super().append(event)
        if self.persist is not None:
            self.persist()
        print(
            json.dumps(
                {
                    "worker_probe_event": {
                        key: event[key]
                        for key in ("pid", "job_id", "stage", "action")
                        if key in event
                    }
                }
            ),
            flush=True,
        )


def validate_event(event, pid, stage, job_id):
    require(
        isinstance(event, dict)
        and event.get("protocol") == 1
        and event.get("pid") == pid
        and event.get("stage") == stage
        and event.get("job_id") == job_id,
        "Unexpected child barrier identity",
    )


class Barriers:
    def __init__(self, connection, pause, job_id):
        self.connection, self.pause, self.job_id = connection, pause, job_id
        self.lock = threading.Lock()
        self.paused = False

    def hit(self, stage, **values):
        with self.lock:
            self.connection.send(
                dict(
                    protocol=1,
                    pid=os.getpid(),
                    job_id=self.job_id,
                    stage=stage,
                    **values,
                )
            )
            if stage == self.pause and not self.paused:
                self.paused = True
                require(self.connection.poll(240), "Parent release deadline exceeded")
                require(
                    self.connection.recv() == {"release": stage},
                    "Invalid parent release",
                )


def fixture_identity(cfg, namespace):
    from sqlalchemy.engine import make_url

    return {
        "namespace": namespace,
        "database": make_url(cfg.db_url()).database,
        "artifact_bucket": cfg.artifact_bucket,
        "export_bucket": cfg.export_bucket,
        "journal_bucket": cfg.journal_bucket,
        "queue_url": cfg.queue_url,
        "dlq_url": cfg.dlq_url,
        "fictional": True,
        "protocol": 1,
    }


def prepare_fixture(cfg, namespace):
    """Only PM invokes this after creating the separately named empty database."""
    from botocore.exceptions import ClientError
    from otgd import storage
    from otgd.canonical import canonical
    from otgd.db import SystemState, engine, factory, iso
    from otgd.migrate import migrate
    from sqlalchemy import inspect

    s3, sqs = storage.client("s3"), storage.client("sqs")
    with engine().connect() as db:
        require(
            not inspect(db).get_table_names(), "Fixture database must be entirely empty"
        )
    for bucket in [cfg.artifact_bucket, cfg.export_bucket, cfg.journal_bucket]:
        try:
            s3.head_bucket(Bucket=bucket)
        except ClientError as error:
            require(
                error.response["ResponseMetadata"]["HTTPStatusCode"] == 404,
                "Cannot prove fixture bucket absent",
            )
        else:
            raise RuntimeError("Fixture bucket already exists; never adopt it")
    for tail in ("jobs", "dlq"):
        try:
            sqs.get_queue_url(QueueName=namespace + "-" + tail)
        except ClientError as error:
            require(
                error.response["Error"]["Code"]
                in ("AWS.SimpleQueueService.NonExistentQueue", "QueueDoesNotExist"),
                "Cannot prove fixture queue absent",
            )
        else:
            raise RuntimeError("Fixture queue already exists; never adopt it")
    for bucket in [cfg.artifact_bucket, cfg.export_bucket, cfg.journal_bucket]:
        args = {"Bucket": bucket}
        if cfg.aws_region != "us-east-1":
            args["CreateBucketConfiguration"] = {"LocationConstraint": cfg.aws_region}
        s3.create_bucket(**args)
        s3.put_bucket_versioning(
            Bucket=bucket, VersioningConfiguration={"Status": "Enabled"}
        )
        s3.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                key: True
                for key in (
                    "BlockPublicAcls",
                    "IgnorePublicAcls",
                    "BlockPublicPolicy",
                    "RestrictPublicBuckets",
                )
            },
        )
        s3.put_bucket_encryption(
            Bucket=bucket,
            ServerSideEncryptionConfiguration={
                "Rules": [
                    {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
                ]
            },
        )
    dlq = sqs.create_queue(
        QueueName=namespace + "-dlq",
        Attributes={
            "VisibilityTimeout": "120",
            "MessageRetentionPeriod": "1209600",
            "SqsManagedSseEnabled": "true",
        },
    )["QueueUrl"]
    arn = sqs.get_queue_attributes(QueueUrl=dlq, AttributeNames=["QueueArn"])[
        "Attributes"
    ]["QueueArn"]
    source = sqs.create_queue(
        QueueName=namespace + "-jobs",
        Attributes={
            "VisibilityTimeout": "120",
            "ReceiveMessageWaitTimeSeconds": "20",
            "MessageRetentionPeriod": "345600",
            "SqsManagedSseEnabled": "true",
            "RedrivePolicy": json.dumps(
                {"deadLetterTargetArn": arn, "maxReceiveCount": 5}
            ),
        },
    )["QueueUrl"]
    require(
        (local_http(source).path, local_http(dlq).path)
        == (local_http(cfg.queue_url).path, local_http(cfg.dlq_url).path),
        "Actual LocalStack queue identities differ from configured fixture",
    )
    storage.put_versioned(
        cfg.journal_bucket,
        "control/established.json",
        canonical(
            {
                "schema_version": "1.0.0",
                "environment": "local",
                "established_at": iso(),
                "minimum_retention_days": 90,
                "maximum_recovery_age_days": 35,
            }
        ),
        conditional=True,
    )
    migrate()
    with factory().begin() as db:
        db.add(SystemState(key=MARKER, body=fixture_identity(cfg, namespace)))
    return dict(status="prepared", **fixture_identity(cfg, namespace))


def check_fixture(cfg, namespace):
    from otgd import storage
    from otgd.db import Account, SystemState, factory
    from otgd.journal_continuity import verify_binding
    from sqlalchemy import select, text

    with factory()() as db:
        marker = db.get(SystemState, MARKER)
        require(
            marker is not None and marker.body == fixture_identity(cfg, namespace),
            "Fixture marker mismatch",
        )
        require(
            db.scalar(text("SELECT current_database()")) == cfg.database_name,
            "Connected database mismatch",
        )
        require(
            db.scalar(select(Account.id).limit(1)) is None,
            "Probe requires a fresh unused fixture; never reset it",
        )
        verify_binding(db, cfg)
    sqs = storage.client("sqs")
    attrs = sqs.get_queue_attributes(QueueUrl=cfg.queue_url, AttributeNames=["All"])[
        "Attributes"
    ]
    dlq = sqs.get_queue_attributes(QueueUrl=cfg.dlq_url, AttributeNames=["All"])[
        "Attributes"
    ]
    redrive = json.loads(attrs["RedrivePolicy"])
    require(
        int(attrs["VisibilityTimeout"]) == 120
        and int(attrs["ReceiveMessageWaitTimeSeconds"]) == 20
        and int(attrs["MessageRetentionPeriod"]) == 345600
        and int(redrive["maxReceiveCount"]) == 5
        and redrive["deadLetterTargetArn"] == dlq["QueueArn"]
        and int(dlq["MessageRetentionPeriod"]) == 1209600,
        "Fixture queue contract mismatch",
    )
    require(
        all(
            int(attrs.get(key, 0)) == 0
            for key in (
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
                "ApproximateNumberOfMessagesDelayed",
            )
        ),
        "Fixture queue is not fresh",
    )
    for bucket in [cfg.artifact_bucket, cfg.export_bucket, cfg.journal_bucket]:
        require(
            storage.client("s3").get_bucket_versioning(Bucket=bucket).get("Status")
            == "Enabled",
            "Fixture bucket must retain immutable versions",
        )


def child_worker(connection, pause, job_id):
    """Wrap boundaries only; every work/authority/SQL/SDK decision is production."""
    try:
        from otgd import storage, worker

        b = Barriers(connection, pause, job_id)
        original_claim, original_commit = worker.claim_job, worker.commit_output
        original_put, original_client, original_run = (
            storage.put_versioned,
            storage.client,
            worker.run_job,
        )

        def claim(id):
            if id == job_id:
                b.hit("before_claim")
            value = original_claim(id)
            if value and id == job_id:
                b.hit(
                    "after_claim",
                    fence=value.fence,
                    generation=value.generation,
                    started=value.started,
                )
            return value

        def put(bucket, key, data, *args, **kwargs):
            owned = "/" + job_id + "/" in key
            if owned:
                b.hit("before_write", key=key)
            version = original_put(bucket, key, data, *args, **kwargs)
            if owned:
                b.hit(
                    "after_write",
                    key=key,
                    version_id=version,
                    sha256=hashlib.sha256(data).hexdigest(),
                )
            return version

        def commit(value, output):
            original_commit(value, output)
            if value.id == job_id:
                b.hit(
                    "after_commit",
                    fence=value.fence,
                    generation=value.generation,
                    output=output,
                )

        class SqsCalls:
            def __init__(self, delegate):
                self.delegate = delegate
                self.owned_receipts = set()

            def __getattr__(self, key):
                return getattr(self.delegate, key)

            def receive_message(self, **kwargs):
                result = self.delegate.receive_message(**kwargs)
                for message in result.get("Messages", []):
                    try:
                        if json.loads(message["Body"]).get("job_id") == job_id:
                            self.owned_receipts.add(message["ReceiptHandle"])
                    except (ValueError, AttributeError):
                        pass
                return result

            def delete_message(self, **kwargs):
                if kwargs["ReceiptHandle"] not in self.owned_receipts:
                    return self.delegate.delete_message(**kwargs)
                b.hit(
                    "before_delete", receipt_sha256=receipt_ref(kwargs["ReceiptHandle"])
                )
                value = self.delegate.delete_message(**kwargs)
                b.hit(
                    "after_delete", receipt_sha256=receipt_ref(kwargs["ReceiptHandle"])
                )
                worker.stop.set()
                return value

        sqs = SqsCalls(original_client("sqs"))

        def client(service):
            return sqs if service == "sqs" else original_client(service)

        def run(id, *args, **kwargs):
            outcome = original_run(id, *args, **kwargs)
            if id == job_id:
                b.hit("run_returned", outcome=outcome)
                if outcome not in ("completed", "terminal", "deferred", "busy"):
                    worker.stop.set()
            return outcome

        worker.claim_job, worker.commit_output = claim, commit
        storage.put_versioned, storage.client, worker.run_job = put, client, run
        worker.main()
        b.hit("exited")
    except Exception as error:  # noqa: BLE001 - report only class across process boundary
        # Exception strings can contain credentials. Preserve only the class.
        connection.send(
            {
                "protocol": 1,
                "pid": os.getpid(),
                "job_id": job_id,
                "stage": "error",
                "error_type": type(error).__name__,
            }
        )
        raise SystemExit(1) from None
    finally:
        connection.close()


class OwnedChild:
    def __init__(self, stage, job_id, events):
        ctx = multiprocessing.get_context("spawn")
        self.pipe, child = ctx.Pipe()
        self.process = ctx.Process(target=child_worker, args=(child, stage, job_id))
        self.job_id, self.events = job_id, events
        self.process.start()
        child.close()
        self.suspended = False

    def await_stage(self, stage, timeout=170):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.pipe.poll(min(1, max(0, deadline - time.monotonic()))):
                try:
                    event = self.pipe.recv()
                except EOFError:
                    break
                validate_event(event, self.process.pid, event.get("stage"), self.job_id)
                self.events.append(event)
                require(
                    event["stage"] != "error",
                    "Owned worker failed; inspect redacted event",
                )
                if event["stage"] == stage:
                    return event
            elif not self.process.is_alive():
                break
        raise RuntimeError("Owned child barrier deadline exceeded: " + stage)

    def release(self, stage):
        require(self.process.is_alive(), "Cannot release exited child")
        self.pipe.send({"release": stage})

    def send_signal(self, value):
        # No caller-supplied PID or process-name matching is accepted.
        require(
            self.process.pid is not None and self.process.is_alive(),
            "Owned child already exited",
        )
        os.kill(self.process.pid, value)
        self.events.append(
            {
                "action": signal.Signals(value).name,
                "pid": self.process.pid,
                "job_id": self.job_id,
            }
        )
        self.suspended = value == signal.SIGSTOP

    def close(self):
        if self.process.is_alive():
            self.send_signal(signal.SIGKILL)
        self.process.join(5)
        require(not self.process.is_alive(), "Owned child did not terminate")
        self.pipe.close()

    def finish(self, timeout=30):
        self.await_stage("exited", timeout)
        self.process.join(5)
        require(self.process.exitcode == 0, "Replacement child did not exit cleanly")


def result_fixture(owner):
    """Same synthetic evidence contract as API fixtures, without auth doubles."""
    from otgd.canonical import digest, strict_loads
    from otgd.config import ROOT

    snapshot = strict_loads((ROOT / "examples/synthetic_session.json").read_bytes())
    snapshot["session_id"] = str(uuid4())
    snapshot["subject_ref"] = owner
    snapshot["target_at"] = snapshot["created_at"]
    sid = snapshot["session_id"]
    context = {
        "schema_version": "1.0.0",
        "session_id": sid,
        "context_confirmed_at": snapshot["target_at"],
        "profile_version_id": None,
        "profile_snapshot_sha256": digest(snapshot["profile"]),
        "history_snapshot_sha256": digest(snapshot["history"]),
        "protocol_id": None,
        "configuration_refs": [],
        "baseline_refs": [],
        "device_associations": [],
    }
    attempts = []
    selected = {key: None for key in ("saliva", "eyes", "cardiac", "task", "alcohol")}
    for component in ("saliva", "eyes", "cardiac", "task"):
        projection = (
            {"sample": snapshot["sample"], "saliva": snapshot["saliva"]}
            if component == "saliva"
            else snapshot[component]
        )
        first = (
            snapshot["sample"]["collected_at"]
            if component == "saliva"
            else projection["started_at"]
        )
        id = str(uuid4())
        attempts.append(
            {
                "schema_version": "1.0.0",
                "session_id": sid,
                "attempt_id": id,
                "component": component,
                "record_id": snapshot["sample"]["sample_id"]
                if component == "saliva"
                else snapshot["task"]["task_id"]
                if component == "task"
                else str(uuid4()),
                "supersedes_attempt_id": None,
                "status": "valid",
                "source": "simulated",
                "started_at": first,
                "ended_at": first if component == "saliva" else projection["ended_at"],
                "configuration_id": None,
                "configuration_hash": None,
                "quality_flags": [],
                "component_metadata": {"projection": projection},
                "artifact_refs": [],
                "attestation_refs": [],
            }
        )
        selected[component] = id
    manifest = {
        "schema_version": "1.0.0",
        "session_id": sid,
        "context_sha256": digest(context),
        "attempts": [
            {"attempt_id": item["attempt_id"], "sha256": digest(item)}
            for item in attempts
        ],
        "selected": selected,
    }
    return {
        "snapshot": snapshot,
        "context": context,
        "attempts": attempts,
        "manifest": manifest,
    }


def seed_job(label, *, ttl=3600, kind="export"):
    from otgd.canonical import digest
    from otgd.db import Account, Check, Job, Outbox, factory, now

    owner, id = str(uuid4()), str(uuid4())
    with factory().begin() as db:
        account = Account(
            id=owner,
            subject_hash=digest({"fictional_worker_probe": label, "id": owner}),
        )
        db.add(account)
        db.flush()
        body = {
            "selection": {"kind": "all"},
            "include_raw": False,
            "session_ids": [],
            "profile_version_ids": [],
            "current_profile_version_id": None,
            "report_revision_heads": {},
        }
        if kind == "result":
            from otgd.domain import save_record, verify_evidence

            fixture = result_fixture(owner)
            snap = fixture["snapshot"]
            row = Check(
                id=snap["session_id"],
                account_id=owner,
                generation=1,
                state="processing",
                mode="synthetic",
                snapshot=snap,
                snapshot_sha256=digest(snap),
                evidence_sha256=digest(fixture["manifest"]),
            )
            db.add(row)
            save_record(db, account, "context", row.id, fixture["context"])
            save_record(db, account, "manifest", row.id, fixture["manifest"])
            for attempt in fixture["attempts"]:
                save_record(
                    db,
                    account,
                    "attempt",
                    attempt["attempt_id"],
                    attempt,
                    parent=row.id,
                )
            db.flush()
            verify_evidence(db, account, row)
            body = {"session_id": row.id}
        db.add(
            Job(
                id=id,
                account_id=owner,
                generation=1,
                kind=kind,
                body=body,
                expires=now() + ttl,
            )
        )
        db.flush()
        db.add(Outbox(job_id=id))
    return id, owner


def snapshot(id):
    from otgd.db import Job, Outbox, factory
    from sqlalchemy import select

    with factory()() as db:
        job = db.get(Job, id)
        outbox = db.scalar(select(Outbox).where(Outbox.job_id == id))
        require(job is not None and outbox is not None, "Lost durable job/outbox")
        return {
            "job_id": id,
            "outbox_id": outbox.id,
            "published": outbox.published,
            "state": job.state,
            "fence": job.fence,
            "attempts": job.attempts,
            "generation": job.generation,
            "lease_until": job.lease_until,
            "completed": job.completed,
            "output": job.output,
            "expires": job.expires,
            "failure": job.failure,
        }


def verify_output(id, *, kind="export"):
    import io
    import zipfile

    from otgd import storage
    from otgd.config import settings

    value = snapshot(id)
    output = value["output"]
    require(
        value["state"] == "completed" and value["completed"] and output,
        "Missing committed output",
    )
    if kind == "result":
        from otgd.db import Check, Job, factory
        from otgd.domain import safe_result

        with factory()() as db:
            check = db.get(Check, db.get(Job, id).body["session_id"])
            require(
                check.state == "completed" and check.result == output,
                "Check/result job commit was not atomic",
            )
            safe_result(output)
        require(
            output["state"] == "measurement_only"
            and output["probability"] is None
            and output["classification"] is None
            and "SIMULATED_INPUT" in output["reason_codes"],
            "Synthetic result lost measurement-only provenance",
        )
        return value
    require(
        output["key"].endswith("/" + str(value["fence"]) + ".zip")
        and output.get("version_id") not in (None, "null", ""),
        "Output is not pinned to winning fence/version",
    )
    data = storage.versioned_read(
        settings().export_bucket, output["key"], output["version_id"], 64 * 1024 * 1024
    )
    require(
        len(data) == output["size_bytes"]
        and hashlib.sha256(data).hexdigest() == output["sha256"],
        "Version-pinned output integrity failure",
    )
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        require(
            manifest["job_id"] == id and manifest == output["manifest"],
            "Foreign/mismatched archive",
        )
    return value


def no_early_delete(child):
    require(
        not any(
            e.get("stage") == "after_delete"
            for e in child.events
            if e.get("pid") == child.process.pid
        ),
        "Queue acknowledged before recorded kill barrier",
    )


def kill_case(stage, events, *, kind="export"):
    from otgd import worker

    id, _ = seed_job(stage, kind=kind)
    worker.dispatch_once()
    before = snapshot(id)
    require(before["published"] is not None, "Outbox publication absent")
    child = OwnedChild(stage, id, events)
    replacement = None
    try:
        barrier = child.await_stage(stage)
        at_kill = snapshot(id)
        no_early_delete(child)
        child.send_signal(signal.SIGKILL)
        child.process.join(5)
        require(
            child.process.exitcode == -signal.SIGKILL, "Actual SIGKILL not observed"
        )
        killed_at = time.monotonic()
        replacement = OwnedChild(None, id, events)
        replacement.await_stage("after_delete", 170)
        replacement.finish()
        recovered = verify_output(id, kind=kind)
        require(
            recovered["outbox_id"] == before["outbox_id"],
            "Recovery replaced durable event",
        )
        expected = 2 if stage in ("after_claim", "after_write") else 1
        require(
            recovered["fence"] == expected and recovered["attempts"] == expected,
            "Unexpected duplicate execution/claim count",
        )
        if stage in ("after_commit", "before_delete"):
            require(
                recovered["output"] == at_kill["output"]
                and recovered["completed"] == at_kill["completed"],
                "Terminal redelivery recomputed or recommitted output",
            )
        elapsed = time.monotonic() - killed_at
        require(elapsed >= 110, "Production visibility/lease was bypassed")
        return {
            "stage": stage,
            "kind": kind,
            "pid": child.process.pid,
            "replacement_pid": replacement.process.pid,
            "barrier": barrier,
            "at_kill": at_kill,
            "recovered": recovered,
            "recovery_seconds": round(elapsed, 3),
        }
    finally:
        child.close()
        if replacement:
            replacement.close()


def term_case(events):
    from otgd import worker

    id, _ = seed_job("sigterm")
    worker.dispatch_once()
    child = OwnedChild("after_claim", id, events)
    try:
        child.await_stage("after_claim")
        begin = time.monotonic()
        child.send_signal(signal.SIGTERM)
        child.release("after_claim")
        child.await_stage("after_delete", 30)
        child.finish(30)
        elapsed = time.monotonic() - begin
        require(elapsed < 30, "SIGTERM exceeded observed bounded stop window")
        return {
            "signal": "SIGTERM",
            "pid": child.process.pid,
            "stop_seconds": round(elapsed, 3),
            "result": verify_output(id),
        }
    finally:
        child.close()


def stale_case(events, *, retire=False):
    """SIGSTOP stops real heartbeat; no lease clock/fence/time is patched."""
    from otgd import storage, worker
    from otgd.config import settings
    from otgd.db import Account, factory, now

    id, owner = seed_job(
        "retired-late-write" if retire else "stale-late-write", ttl=190
    )
    worker.dispatch_once()
    child = OwnedChild("before_write", id, events)
    replacement = None
    try:
        child.await_stage("before_write")
        child.send_signal(signal.SIGSTOP)
        original = snapshot(id)
        if retire:
            # A real transaction changes current generation during downtime.
            with factory().begin() as db:
                account = db.get(Account, owner)
                account.generation += 1
                account.state = "deleting"
        replacement = OwnedChild(None, id, events)
        if retire:
            # claim_job checks current generation before any external output.
            deadline = time.monotonic() + 165
            while snapshot(id)["state"] != "failed" and time.monotonic() < deadline:
                time.sleep(1)
            require(
                snapshot(id)["failure"] == "DATA_GENERATION_RETIRED",
                "Retired generation admitted",
            )
            replacement.send_signal(signal.SIGTERM)
        else:
            replacement.await_stage("after_delete", 165)
            replacement.finish()
            winner = verify_output(id)
            require(
                winner["fence"] > original["fence"],
                "Replacement did not change real fence",
            )
        child.send_signal(signal.SIGCONT)
        child.release("before_write")
        late = child.await_stage("after_write", 20)
        returned = child.await_stage("run_returned", 20)
        require(returned["outcome"] == "lease_lost", "Stale late output committed")
        after = snapshot(id)
        if retire:
            require(
                after["output"] is None and after["state"] == "failed",
                "Retired output published",
            )
        else:
            require(
                after["output"] == winner["output"]
                and after["completed"] == winner["completed"],
                "Stale commit changed winning result",
            )
        # Ownership-bounded recurring cleanup at the job's genuine expiry.
        # There is no artificial update of expires/lease/current clock.
        while now() <= after["expires"]:
            time.sleep(min(1, after["expires"] - now() + 0.01))
        neighbor = f"exports/{owner}/1/{uuid4()}/neighbor"
        version = storage.put_versioned(
            settings().export_bucket, neighbor, b"FICTIONAL NEIGHBOR"
        )
        cleanup = worker.cleanup_once()
        require(cleanup["failed"] == 0, "Real recurring cleanup failed")
        versions = storage.client("s3").list_object_versions(
            Bucket=settings().export_bucket, Prefix=f"exports/{owner}/1/{id}/"
        )
        require(
            not versions.get("Versions") and not versions.get("DeleteMarkers"),
            "Owned late outputs survived expiry cleanup",
        )
        require(
            storage.versioned_read(settings().export_bucket, neighbor, version, 1024)
            == b"FICTIONAL NEIGHBOR",
            "Cleanup erased a neighboring job",
        )
        return {
            "retired": retire,
            "original": original,
            "after_late_commit": after,
            "late_output": late,
            "cleanup": cleanup,
            "neighbor_version": version,
            "cleanup_boundary": "actual job expiry, not immediate orphan removal",
        }
    finally:
        child.close()
        if replacement:
            replacement.close()


def budget_case(events):
    """Actual malformed durable work failures + actual five-receive redrive."""
    from otgd import storage, worker
    from otgd.config import settings
    from otgd.db import Job, factory, now

    id, _ = seed_job("real-failed-claim-budget")
    # Malformed persisted fixture exercises the actual exporter exception path.
    # No SDK/SQL function or exception result is substituted by the harness.
    with factory().begin() as db:
        job = db.get(Job, id)
        job.body = {key: value for key, value in job.body.items() if key != "selection"}
    counts = []
    for attempt in range(5):
        # Call due claims only after real configured exponential backoff.
        if attempt:
            time.sleep(min(300, 2 ** counts[-1]["attempts"]))
        require(
            worker.run_job(id) == "failed",
            "Malformed durable fixture unexpectedly succeeded",
        )
        counts.append(snapshot(id))
    require(
        counts[-1]["state"] == "failed"
        and counts[-1]["attempts"] == 5
        and counts[-1]["failure"] == "DEPENDENCY_FAILED"
        and worker.claim_job(id) is None,
        "Logical five-claim budget was reset",
    )
    # Real SQS poison message: six actual 120-second receives drive redrive.
    sqs = storage.client("sqs")
    cfg = settings()
    poison = {"fictional_worker_probe_poison": str(uuid4())}
    sent = sqs.send_message(QueueUrl=cfg.queue_url, MessageBody=json.dumps(poison))
    receives = []
    deadline = time.monotonic() + 700
    while time.monotonic() < deadline:
        dead = sqs.receive_message(
            QueueUrl=cfg.dlq_url, MaxNumberOfMessages=1, WaitTimeSeconds=1
        ).get("Messages", [])
        if dead:
            message = dead[0]
            if message["MessageId"] != sent["MessageId"]:
                body = json.loads(message["Body"])
                require(
                    set(body) == {"schema_version", "job_id"}
                    and snapshot(body["job_id"])["state"]
                    in ("failed", "expired", "completed"),
                    "Unexpected DLQ identity",
                )
                events.append(
                    {
                        "stage": "other_terminal_dlq",
                        "message_id": message["MessageId"],
                        "job_id": body["job_id"],
                        "receipt_sha256": receipt_ref(message["ReceiptHandle"]),
                    }
                )
                continue
            require(json.loads(message["Body"]) == poison, "Unexpected DLQ body")
            require(
                len(receives) == 5, "Queue redrive budget differs from five receives"
            )
            return {
                "logical_attempts": counts,
                "dlq_message_id": message["MessageId"],
                "receives": receives,
            }
        messages = sqs.receive_message(
            QueueUrl=cfg.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
            VisibilityTimeout=120,
            MessageSystemAttributeNames=["ApproximateReceiveCount"],
        ).get("Messages", [])
        for message in messages:
            # Never delete or change visibility to accelerate redrive.
            if message["MessageId"] != sent["MessageId"]:
                body = json.loads(message["Body"])
                # Drain only a terminal delivery through the real run_job path.
                require(
                    set(body) == {"schema_version", "job_id"}
                    and body["schema_version"] == "1.0.0",
                    "Unexpected residual fixture queue delivery",
                )
                outcome = worker.run_job(body["job_id"])
                require(
                    snapshot(body["job_id"])["state"]
                    in ("completed", "failed", "expired"),
                    "Nonterminal leftover fixture delivery",
                )
                if outcome == "terminal":
                    sqs.delete_message(
                        QueueUrl=cfg.queue_url, ReceiptHandle=message["ReceiptHandle"]
                    )
                else:
                    require(
                        outcome == "busy", "Unexpected terminal failure disposition"
                    )
                continue
            receives.append(
                {
                    "receipt_sha256": receipt_ref(message["ReceiptHandle"]),
                    "receive_count": int(
                        message["Attributes"]["ApproximateReceiveCount"]
                    ),
                    "observed_at": now(),
                }
            )
            require(
                receives[-1]["receive_count"] == len(receives),
                "Unexpected receive counter",
            )
    raise RuntimeError("Actual production-policy DLQ redrive deadline exceeded")


def run_probe(cfg, namespace, output):
    check_fixture(cfg, namespace)
    events = EvidenceEvents()
    report = {
        "status": "running",
        "fictional": True,
        "fixture": fixture_identity(cfg, namespace),
        "stages": [],
        "events": events,
        "source_manifest_before": source_manifest(),
        "runtime_database_role": cfg.database_user,
        "scope": {
            "export": "structured fictional export",
            "result": "synthetic measurement-only result",
            "retirement": "real transaction retires account generation during stopped worker",
            "cleanup": "actual job expiry; no immediate orphan erasure assertion",
            "not_exercised": [
                "raw-export authority revocation",
                "900-second work deadline",
                "HTTP privacy deletion lifecycle",
                "cloud/native/scientific qualification",
            ],
        },
        "limits": {
            "visibility_seconds": 120,
            "lease_seconds": 120,
            "heartbeat_seconds": 30,
            "max_claims": 5,
            "max_receives": 5,
            "attempt_deadline_seconds": 900,
        },
    }

    def save():
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    events.persist = save
    save()
    try:
        for stage in STAGES:
            report["stages"].append(kill_case(stage, events))
            save()
        report["result_stages"] = []
        for stage in ("after_claim", "after_commit"):
            report["result_stages"].append(kill_case(stage, events, kind="result"))
            save()
        report["sigterm"] = term_case(events)
        save()
        report["stale_write"] = stale_case(events)
        save()
        report["retired_write"] = stale_case(events, retire=True)
        save()
        report["budgets"] = budget_case(events)
        save()
        report["source_manifest_after"] = source_manifest()
        require(
            report["source_manifest_before"] == report["source_manifest_after"],
            "Executed Python/contract source changed during live matrix",
        )
        report["status"] = "passed"
    except BaseException as error:
        report["status"] = "failed"
        report["error_type"] = type(error).__name__
        save()
        raise
    save()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-fictional-workspace", action="store_true")
    parser.add_argument(
        "--fixture-namespace", default=os.environ.get("OTGD_WORKER_PROBE_NAMESPACE")
    )
    parser.add_argument(
        "--prepare-fixture",
        action="store_true",
        help="PM-only explicit setup of empty separately created DB",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("reports/worker-interrupt.json")
    )
    args = parser.parse_args()
    from otgd.config import settings

    cfg = settings()
    validate_target(cfg, args.fixture_namespace, args.confirm_fictional_workspace)
    if args.prepare_fixture:
        print(json.dumps(prepare_fixture(cfg, args.fixture_namespace), sort_keys=True))
    else:
        require(
            args.output.parent.is_dir(), "Evidence output directory must already exist"
        )
        result = run_probe(cfg, args.fixture_namespace, args.output)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "output": str(args.output),
                    "fixture": args.fixture_namespace,
                }
            )
        )


if __name__ == "__main__":
    main()
