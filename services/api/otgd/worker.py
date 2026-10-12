"""SQS delivery + transactional outbox. External work never holds the account lock."""

import hashlib
import io
import json
import logging
import signal
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from botocore.exceptions import ClientError
from sqlalchemy import delete, select

from . import storage
from .canonical import canonical, strict_loads
from .config import settings
from .db import (
    Account,
    Artifact,
    Check,
    Dedup,
    Job,
    Outbox,
    Record,
    factory,
    iso,
    now,
)
from .domain import safe_result, verify_evidence
from .errors import Problem
from .recovery_authority import require_authority
from .worker_health import WorkerHealth

stop = threading.Event()


class LeaseLost(Exception):
    pass


class Deferred(Exception):
    def __init__(self, until):
        self.until = until


@dataclass(frozen=True)
class Claim:
    id: str
    account_id: str
    generation: int
    kind: str
    fence: int
    started: float
    body: dict


def authorized(account, job):
    return account is not None and (
        (
            job.kind == "deletion"
            and account.generation > job.generation
            and account.state in ("deleting", "deleted", "awaiting_generation_ack")
        )
        or (account.generation == job.generation and account.state == "active")
    )


def claim_job(job_id):
    with factory().begin() as db:
        hint = db.get(Job, job_id)
        if not hint:
            return None
        if hint.kind != "deletion":
            require_authority(db)
        account = db.scalar(
            select(Account)
            .where(Account.id == hint.account_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        job = db.scalar(
            select(Job)
            .where(Job.id == job_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if job.state not in ("pending", "running") or (
            job.state == "running" and (job.lease_until or 0) > now()
        ):
            return None
        if not authorized(account, job):
            job.state = "failed"
            job.failure = "DATA_GENERATION_RETIRED"
            return None
        if job.kind == "deletion" and not job.journal_accepted:
            return None
        if job.attempts >= 5:
            job.state = "failed"
            job.failure = "ATTEMPT_LIMIT_EXCEEDED"
            return None
        job.state = "running"
        job.fence += 1
        job.attempts += 1
        job.lease_until = now() + 120
        job.started = now()
        return Claim(
            job.id,
            job.account_id,
            job.generation,
            job.kind,
            job.fence,
            job.started,
            job.body,
        )


def current(db, claim, *, enforce_export=True):
    account = db.scalar(
        select(Account)
        .where(Account.id == claim.account_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    job = db.scalar(
        select(Job)
        .where(Job.id == claim.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if (
        not job
        or job.state != "running"
        or job.fence != claim.fence
        or (job.lease_until or 0) <= now()
        or now() - claim.started > 900
        or not authorized(account, job)
    ):
        raise LeaseLost()
    if job.kind != "deletion":
        require_authority(db)
    if job.kind == "export" and enforce_export:
        from .raw_export import validate_job

        validate_job(db, account, job)
    return account, job


def heartbeat(claim, receipt, done, lost, health=None, channel=None):
    while not done.wait(30):
        try:
            with factory().begin() as db:
                a, j = current(db, claim)
                j.lease_until = now() + 120
            if receipt:
                storage.client("sqs").change_message_visibility(
                    QueueUrl=settings().queue_url,
                    ReceiptHandle=receipt,
                    VisibilityTimeout=settings().serverless_queue_visibility,
                )
            if health is not None:
                health.success(channel)
        except Exception:
            if health is not None:
                health.failure(channel)
            lost.set()
            return


def export_manifest_bytes(files, manifest, *, max_bytes=50 * 1024 * 1024):
    """Final allocation budget includes the manifest, which can exceed one record."""
    data = canonical(manifest)
    if (
        not 0 < max_bytes <= 50 * 1024 * 1024
        or len(files) + 1 > 65_000
        or sum(len(value) for value in files.values()) + len(data) > max_bytes
    ):
        raise Problem(413, "EXPORT_TOO_LARGE")
    return data


def make_export(claim):
    from .main import detail, evidence
    from .report_revisions import export_records
    from .raw_export import archive_bytes, read_sources

    files = {}
    total = 0
    with factory()() as db:
        a, j = current(db, claim)
        if j.expires <= now():
            raise Problem(410, "EXPORT_EXPIRED")
        archive_limit = archive_bytes(j)
        total_limit = (
            j.body["raw_export"]["authorization"]["max_uncompressed_bytes"]
            if j.body.get("include_raw")
            else 50 * 1024 * 1024
        )
        # The transaction only takes a bounded consistent data snapshot; no S3 call here.
        for sid in claim.body["session_ids"]:
            row = db.get(Check, sid)
            if not row or row.account_id != a.id or row.generation != a.generation:
                raise Problem(410, "DATA_GENERATION_RETIRED")
            safe_result(row.result)
            bundle = {**detail(row), **evidence(db, a, row)}
            if claim.body.get("include_raw"):
                bundle["raw_artifacts_omitted_reason"] = (
                    "UNSELECTED_RAW_ARTIFACTS_OMITTED"
                )
            heads = claim.body.get("report_revision_heads", {})
            head = heads.get(sid, {"revision_id": None, "revision_sha256": None})
            revision_index, revision_files = export_records(db, a, row, head)
            bundle["report_revision_index"] = revision_index
            for path, data in revision_files.items():
                total += len(data)
                if total > 50 * 1024 * 1024 or path in files:
                    raise Problem(413, "EXPORT_TOO_LARGE")
                files[path] = data
            raw = canonical(bundle)
            total += len(raw)
            if len(raw) > 512 * 1024 or total > 50 * 1024 * 1024:
                raise Problem(413, "EXPORT_TOO_LARGE")
            files[f"checks/{sid}.json"] = raw
        profiles = []
        for vid in claim.body.get("profile_version_ids", []):
            profile = db.get(Record, a.id + ":profile_version:" + vid)
            if not profile or profile.generation != a.generation:
                raise Problem(410, "DATA_GENERATION_RETIRED")
            profiles.append(profile.body)
        current_profile = next(
            (
                p
                for p in profiles
                if p["profile_version_id"]
                == claim.body.get("current_profile_version_id")
            ),
            None,
        )
        files["profile.json"] = canonical(
            {
                "schema_version": "1.0.0",
                "selection_kind": claim.body["selection"]["kind"],
                "current": current_profile,
                "versions": profiles,
            }
        )
        total += len(files["profile.json"])
        if (
            len(files["profile.json"]) > 512 * 1024
            or total > 50 * 1024 * 1024
            or len(files) + 1 > 65_000
        ):
            raise Problem(413, "EXPORT_TOO_LARGE")
        manifest = {
            "schema_version": "1.0.0",
            "canonicalization": "RFC8785",
            "job_id": j.id,
            "selection": claim.body["selection"],
            "session_ids": claim.body["session_ids"],
            "created_at": iso(),
            "expires_at": iso(j.expires),
            "omitted_categories": ["raw_artifacts"],
            "files": [
                {
                    "path": p,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "size_bytes": len(raw),
                }
                for p, raw in files.items()
            ],
        }
        db.commit()
    raw_files, raw_scope = read_sources(claim, factory(), current)
    if raw_scope is not None:
        if set(raw_files) & set(files):
            raise Problem(503, "RAW_EXPORT_INTEGRITY_FAILURE")
        files.update(raw_files)
        manifest["raw_export"] = raw_scope
        manifest["omitted_categories"] = [
            "unselected_raw_artifacts",
            "source_lab_reports",
        ]
        manifest["files"] = [
            {
                "path": path,
                "sha256": hashlib.sha256(value).hexdigest(),
                "size_bytes": len(value),
            }
            for path, value in files.items()
        ]
    # Archive metadata can span many small records; its bytes still consume the
    # same total limit. Each actual structured evidence/profile file is bounded above.
    files["manifest.json"] = export_manifest_bytes(
        files, manifest, max_bytes=total_limit
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, data in files.items():
            archive.writestr(path, data)
    data = buffer.getvalue()
    if len(data) > archive_limit:
        raise Problem(413, "EXPORT_TOO_LARGE")
    key = f"exports/{claim.account_id}/{claim.generation}/{claim.id}/{claim.fence}.zip"
    version = storage.put_versioned(
        settings().export_bucket, key, data, "application/zip"
    )
    return {
        "key": key,
        "version_id": version,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "manifest": manifest,
    }


def delete_data_external(claim):
    with factory()() as db:
        a, j = current(db, claim)
        artifacts = list(
            db.scalars(
                select(Artifact).where(
                    Artifact.account_id == a.id, Artifact.generation == claim.generation
                )
            )
        )
        waiting = [x.expires + 60 for x in artifacts if x.expires + 60 > now()]
        if waiting:
            raise Deferred(min(waiting))
        # Keep minimal cleanup references durable for repeated late-arrival reconciliation.
        db.commit()
    for artifact in artifacts:
        storage.delete_versions(artifact.bucket, artifact.key)
    storage.delete_versions(
        settings().artifact_bucket, f"quarantine/{claim.account_id}/{claim.generation}/"
    )
    storage.delete_versions(
        settings().export_bucket, f"exports/{claim.account_id}/{claim.generation}/"
    )
    if claim.body["scope"] == "account" and not claim.body.get("provider_sub"):
        raise Problem(403, "IDENTITY_RECONCILIATION_REQUIRED")
    if claim.body["scope"] == "account" and settings().environment in ("qa", "prod"):
        try:
            storage.client("cognito-idp").admin_delete_user(
                UserPoolId=settings().user_pool_id, Username=claim.body["provider_sub"]
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "UserNotFoundException":
                raise
    return {"external_cleanup_at": iso()}


def execute_claim(claim):
    if claim.kind == "export":
        return make_export(claim)
    if claim.kind == "deletion":
        return delete_data_external(claim)
    if claim.kind == "result":
        with factory()() as db:
            a, j = current(db, claim)
            row = db.get(Check, claim.body["session_id"])
            if not row or row.account_id != a.id or row.generation != a.generation:
                raise LeaseLost()
            verify_evidence(db, a, row)
            from .model_engine import result_for_check

            return result_for_check(db, a, row)
    raise Problem(422, "UNSUPPORTED_JOB_KIND")


def commit_output(claim, output):
    with factory().begin() as db:
        a, j = current(db, claim)
        if claim.kind == "result":
            check = db.get(Check, claim.body["session_id"])
            verify_evidence(db, a, check)
            if check.state != "processing":
                raise LeaseLost()
            from .model_engine import verify_current_execution

            verify_current_execution(db, a, check, output)
            safe_result(output)
            check.result = output
            check.state = "invalid" if output["state"] == "invalid" else "completed"
        elif claim.kind == "export":
            if j.expires <= now():
                raise Problem(410, "EXPORT_EXPIRED")
            from .raw_export import validate_output

            validate_output(db, a, j, output)
            for sid in claim.body["session_ids"]:
                check = db.get(Check, sid)
                if (
                    not check
                    or check.account_id != a.id
                    or check.generation != a.generation
                ):
                    raise LeaseLost()
                safe_result(check.result)
                if check.study_id:
                    consent = db.scalar(
                        select(Record).where(
                            Record.account_id == a.id,
                            Record.generation == a.generation,
                            Record.kind == "consent",
                            Record.id == a.id + ":consent:" + check.study_id,
                        )
                    )
                    if not consent or consent.body["state"] != "active":
                        raise Problem(403, "CAPABILITY_DENIED")
        elif claim.kind == "deletion":
            if claim.body["scope"] == "account" and settings().environment == "local":
                from .local_oauth_state import disable_local_identity

                disable_local_identity(db, claim.body["provider_sub"], settings())
            # Erase health rows and response bodies. Retain minimal tombstone, audit/receipt and cleanup keys.
            db.execute(
                delete(Record).where(
                    Record.account_id == a.id, Record.generation == claim.generation
                )
            )
            for artifact in db.scalars(
                select(Artifact).where(
                    Artifact.account_id == a.id, Artifact.generation == claim.generation
                )
            ):
                artifact.state = "purged"
                artifact.sha256 = "0" * 64
                artifact.scope = {}
                artifact.size = 0
                artifact.version_id = None
            db.execute(
                delete(Check).where(
                    Check.account_id == a.id, Check.generation == claim.generation
                )
            )
            for d in db.scalars(
                select(Dedup).where(
                    Dedup.account_id == a.id, Dedup.generation == claim.generation
                )
            ):
                if d.route not in ("/v1/privacy/deletion-requests", "/v1/auth/logout"):
                    d.body = None
                    d.headers = {}
            for other in db.scalars(
                select(Job).where(
                    Job.account_id == a.id,
                    Job.generation == claim.generation,
                    Job.id != j.id,
                )
            ):
                other.body = {}
                other.output = None
                other.state = "failed"
                other.failure = "DATA_GENERATION_RETIRED"
                other.lease_until = None
            a.state = (
                "deleted"
                if claim.body["scope"] == "account"
                else "awaiting_generation_ack"
            )
            a.notice = None
            j.body = {k: v for k, v in j.body.items() if k != "provider_sub"}
        j.output = output
        j.state = "completed"
        j.completed = now()
        j.lease_until = None


def fail_claim(claim, error):
    with factory().begin() as db:
        try:
            # Recording failure is allowed for the original active lease even
            # when current raw-export authority has been withdrawn.
            a, j = current(db, claim, enforce_export=False)
        except LeaseLost:
            return
        if isinstance(error, Deferred):
            j.state = "pending"
            j.attempts = max(0, j.attempts - 1)
            j.lease_until = None
            outbox = db.scalar(select(Outbox).where(Outbox.job_id == j.id))
            outbox.published = None
            outbox.available = error.until
            outbox.lease_until = None
            return
        j.failure = error.code if isinstance(error, Problem) else "DEPENDENCY_FAILED"
        terminal = isinstance(error, Problem) and error.status in (
            403,
            409,
            410,
            413,
            422,
        )
        j.state = "failed" if j.attempts >= 5 or terminal else "pending"
        j.lease_until = None
        outbox = db.scalar(select(Outbox).where(Outbox.job_id == j.id))
        if outbox:
            outbox.published = None
            outbox.available = now() + min(300, 2**j.attempts)
            outbox.lease_until = None


def run_job(job_id, receipt=None, health=None, channel=None, *, heartbeat_join_timeout=1):
    claim = claim_job(job_id)
    if not claim:
        with factory()() as db:
            job = db.get(Job, job_id)
            return (
                "terminal"
                if not job or job.state in ("completed", "expired")
                else "busy"
            )
    done = threading.Event()
    lost = threading.Event()
    thread = threading.Thread(
        target=heartbeat,
        args=(claim, receipt, done, lost, health, channel),
        daemon=True,
    )
    thread.start()
    try:
        output = execute_claim(claim)
        if lost.is_set():
            raise LeaseLost()
        if claim.kind == "deletion":
            # Terminal external evidence is durable before publishing terminal database state.
            with factory()() as db:
                current(db, claim)
            event = {
                "schema_version": "1.0.0",
                "event_type": "deletion_completed",
                "job_id": claim.id,
                "account_ref": claim.account_id,
                "retired_generation": claim.generation,
                "scope": claim.body["scope"],
                "completed_at": output["external_cleanup_at"],
                "fencing_token": claim.fence,
            }
            path = "events/" + claim.id + "/completed.json"
            try:
                version = storage.put_versioned(
                    settings().journal_bucket, path, canonical(event), conditional=True
                )
                if storage.versioned_read(
                    settings().journal_bucket, path, version, 8192
                ) != canonical(event):
                    raise Problem(503, "JOURNAL_VERIFICATION_FAILED")
            except Problem as problem:
                if problem.code != "IMMUTABLE_OBJECT_CONFLICT":
                    raise
                head = storage.client("s3").head_object(
                    Bucket=settings().journal_bucket, Key=path
                )
                existing = strict_loads(
                    storage.versioned_read(
                        settings().journal_bucket, path, head.get("VersionId"), 8192
                    )
                )
                for key in (
                    "schema_version",
                    "event_type",
                    "job_id",
                    "account_ref",
                    "retired_generation",
                    "scope",
                ):
                    if existing.get(key) != event[key]:
                        raise Problem(409, "JOURNAL_SCOPE_CONFLICT")
                if existing.get("fencing_token", 0) > claim.fence:
                    raise LeaseLost()
                # A previous completed external cleanup for this same accepted generation is replayable;
                # this claimant has also repeated cleanup and must still win the DB fence below.
        commit_output(claim, output)
        return "completed"
    except LeaseLost:
        return "lease_lost"
    except Exception as error:
        fail_claim(claim, error)
        return "deferred" if isinstance(error, Deferred) else "failed"
    finally:
        done.set()
        # Lambda must not return while a heartbeat still owns SQL or SQS work.
        # Its adapter passes None, joining the actual thread before releasing
        # its independent producer lease. Continuous workers retain their bound.
        thread.join(timeout=heartbeat_join_timeout)


def dispatch_once():
    candidates = []
    with factory().begin() as db:
        # Expired jobs are requeued even when an earlier duplicate delivery was acknowledged.
        for job in db.scalars(
            select(Job)
            .where(Job.state == "running", Job.lease_until < now())
            .with_for_update(skip_locked=True)
            .execution_options(populate_existing=True)
            .limit(25)
        ):
            outbox = db.scalar(select(Outbox).where(Outbox.job_id == job.id))
            if outbox:
                outbox.published = None
                outbox.available = now()
        rows = list(
            db.scalars(
                select(Outbox)
                .join(Job, Outbox.job_id == Job.id)
                .where(
                    Job.state.in_(("pending", "running")),
                    (Job.kind != "deletion") | Job.journal_accepted.is_(True),
                    Outbox.published.is_(None),
                    Outbox.available <= now(),
                    (Outbox.lease_until.is_(None)) | (Outbox.lease_until < now()),
                )
                .order_by(Outbox.available, Outbox.id)
                .with_for_update(of=Outbox, skip_locked=True)
                .execution_options(populate_existing=True)
                .limit(25)
            )
        )
        for row in rows:
            job = db.get(Job, row.job_id)
            if (
                not job
                or job.state not in ("pending", "running")
                or (job.kind == "deletion" and not job.journal_accepted)
            ):
                continue
            row.lease_until = now() + 120
            candidates.append((row.id, row.job_id, row.lease_until))
    for id, jobid, lease in candidates:
        storage.client("sqs").send_message(
            QueueUrl=settings().queue_url,
            MessageBody=json.dumps({"schema_version": "1.0.0", "job_id": jobid}),
        )
        with factory().begin() as db:
            row = db.get(Outbox, id)
            if row and row.lease_until == lease:
                row.published = now()
                row.lease_until = None


def cleanup_once():
    # Claim oldest due rows before external work. Failed rows cannot monopolize a page.
    # References remain durable to catch late completion of previously admitted uploads.
    from .raw_retention import RawRetention, cleanup_raw_once

    tick = now()
    with factory().begin() as db:
        artifacts = list(
            db.scalars(
                select(Artifact)
                .where(
                    Artifact.expires < tick - 60,
                    Artifact.state.in_(["quarantine", "cleanup_pending", "purged"]),
                    Artifact.cleanup_next_at <= tick,
                    ~Artifact.id.in_(select(RawRetention.artifact_id)),
                )
                .order_by(Artifact.cleanup_next_at, Artifact.id)
                .with_for_update(skip_locked=True)
                .execution_options(populate_existing=True)
                .limit(100)
            )
        )
        expired = list(
            db.scalars(
                select(Job)
                .where(
                    Job.kind == "export",
                    Job.expires < tick,
                    Job.state != "expired",
                    Job.cleanup_next_at <= tick,
                )
                .order_by(Job.cleanup_next_at, Job.id)
                .with_for_update(skip_locked=True)
                .execution_options(populate_existing=True)
                .limit(100)
            )
        )
        completed_deletions = list(
            db.scalars(
                select(Job)
                .where(
                    Job.kind == "deletion",
                    Job.state == "completed",
                    Job.cleanup_next_at <= tick,
                )
                .order_by(Job.cleanup_next_at, Job.id)
                .with_for_update(skip_locked=True)
                .execution_options(populate_existing=True)
                .limit(100)
            )
        )
        for row in artifacts:
            if row.state in ("quarantine", "cleanup_pending"):
                row.state = "cleanup_pending"
        for row in artifacts + expired + completed_deletions:
            row.cleanup_next_at = tick + 900
    raw_cleanup = cleanup_raw_once(factory(), storage.client("s3"), tick=tick)
    from .raw_export import cleanup_once as cleanup_raw_exports

    export_cleanup = cleanup_raw_exports(factory(), storage.client("s3"), tick=tick)
    failures = raw_cleanup["failures"] + export_cleanup["failures"]
    for item in artifacts:
        try:
            storage.delete_versions(item.bucket, item.key)
            with factory().begin() as db:
                row = db.get(Artifact, item.id)
                if row:
                    row.cleanup_last_success = now()
                    if row.state in ("quarantine", "cleanup_pending"):
                        row.state = "purged"
                        row.size = 0
                        row.scope = {}
                        row.sha256 = "0" * 64
        except Exception:
            failures += 1
    for job in completed_deletions:
        try:
            storage.delete_versions(
                settings().artifact_bucket,
                f"quarantine/{job.account_id}/{job.generation}/",
            )
            storage.delete_versions(
                settings().export_bucket, f"exports/{job.account_id}/{job.generation}/"
            )
            with factory().begin() as db:
                row = db.get(Job, job.id)
                if row:
                    row.cleanup_last_success = now()
        except Exception:
            failures += 1
    for job in expired:
        try:
            storage.delete_versions(
                settings().export_bucket,
                f"exports/{job.account_id}/{job.generation}/{job.id}/",
            )
            with factory().begin() as db:
                row = db.get(Job, job.id)
                if row:
                    row.output = None
                    row.state = "expired"
                    row.cleanup_last_success = now()
        except Exception:
            failures += 1
    if failures:
        logging.getLogger("otgd.worker").warning(
            "cleanup_dependency_failures count=%d", failures
        )
    return {
        "attempted": len(artifacts)
        + len(expired)
        + len(completed_deletions)
        + raw_cleanup["processed"]
        + export_cleanup["processed"],
        "failed": failures,
    }


def consume(health=None, channel=None):
    while not stop.is_set():
        try:
            messages = (
                storage.client("sqs")
                .receive_message(
                    QueueUrl=settings().queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=20,
                    VisibilityTimeout=120,
                )
                .get("Messages", [])
            )
            if health is not None:
                health.success(channel)
            for msg in messages:
                try:
                    body = strict_loads(msg["Body"])
                    if (
                        set(body) != {"schema_version", "job_id"}
                        or body["schema_version"] != "1.0.0"
                    ):
                        raise ValueError()
                    result = run_job(
                        body["job_id"], msg["ReceiptHandle"], health, channel
                    )
                    if result in ("completed", "terminal", "deferred"):
                        storage.client("sqs").delete_message(
                            QueueUrl=settings().queue_url,
                            ReceiptHandle=msg["ReceiptHandle"],
                        )
                except (ValueError, KeyError):
                    logging.getLogger("otgd.worker").warning(
                        "invalid_queue_delivery"
                    )  # No message bodies.
        except Exception:
            if health is not None:
                health.failure(channel)
            logging.getLogger("otgd.worker").warning("queue_dependency_failed")
            stop.wait(2)


def main():
    s = settings()
    if not s.queue_url or not s.dlq_url:
        raise RuntimeError(
            "SQS source and DLQ URLs are required; no in-process cloud fallback"
        )
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    next_cleanup = 0
    health = WorkerHealth()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(consume, health, f"consumer-{index}") for index in range(2)
        ]
        while not stop.is_set():
            try:
                dispatch_once()
                health.success("dispatcher")
                if now() >= next_cleanup:
                    outcome = cleanup_once()
                    if outcome["failed"]:
                        health.failure("cleanup")
                    else:
                        health.success("cleanup")
                    next_cleanup = now() + 15
            except Exception:
                health.failure("dispatcher")
                logging.getLogger("otgd.worker").warning("dispatcher_dependency_failed")
            stop.wait(1)
        for f in futures:
            f.result()


if __name__ == "__main__":
    main()
