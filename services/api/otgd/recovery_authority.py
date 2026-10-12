"""Independent, retained deletion-journal validation shared by restore and admission.

No database flag can turn off cloud admission. Each check reads actual retained
versions; failures preserve the existing database and refuse participant access.
"""

from __future__ import annotations
import hashlib
import re
import time
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uuid import UUID
from .canonical import canonical, digest, strict_loads
from .storage import versioned_read

EVENT_LIMIT = 8192
INVENTORY_LIMIT = 100000
MANIFEST_LIMIT = 64 * 1024 * 1024
HEX = re.compile(r"^[0-9a-f]{64}$")


class RecoveryBlocked(RuntimeError):
    pass


def timestamp(value):
    if not isinstance(value, str):
        raise RecoveryBlocked("Missing UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
            raise ValueError()
        return parsed.timestamp()
    except (ValueError, AttributeError):
        raise RecoveryBlocked("Invalid UTC timestamp") from None


def uuid_text(value):
    try:
        if str(UUID(value)) != value:
            raise ValueError()
    except (ValueError, AttributeError, TypeError):
        raise RecoveryBlocked("Invalid journal identifier") from None
    return value


def positive_integer(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise RecoveryBlocked("Invalid journal generation")
    return value


def validate_event(key, raw, available_key_ids, server_time):
    if len(raw) > EVENT_LIMIT:
        raise RecoveryBlocked("Oversized journal event")
    event = strict_loads(raw)
    if (
        not isinstance(event, dict)
        or canonical(event) != raw
        or event.get("schema_version") != "1.0.0"
    ):
        raise RecoveryBlocked("Unsupported or noncanonical journal event")
    job = uuid_text(event.get("job_id"))
    uuid_text(event.get("account_ref"))
    positive_integer(event.get("retired_generation"))
    if event.get("scope") not in ("all_data", "account"):
        raise RecoveryBlocked("Unsupported deletion scope")
    if event.get("event_type") == "deletion_accepted":
        required = {
            "schema_version",
            "event_type",
            "event_id",
            "job_id",
            "account_ref",
            "retired_generation",
            "new_generation",
            "scope",
            "policy_version",
            "accepted_at",
            "subject_ref_hmac",
            "hmac_key_id",
        }
        if (
            set(event) != required
            or event["event_id"] != job
            or key != f"events/{job}/accepted.json"
        ):
            raise RecoveryBlocked("Acceptance key/schema mismatch")
        if positive_integer(event["new_generation"]) != event["retired_generation"] + 1:
            raise RecoveryBlocked("Nonconsecutive deletion generation")
        if (
            not HEX.fullmatch(event["subject_ref_hmac"])
            or event["hmac_key_id"] not in available_key_ids
        ):
            raise RecoveryBlocked(
                "Missing required identity tombstone key or invalid subject reference"
            )
        if event["policy_version"] != "privacy-v1":
            raise RecoveryBlocked(
                "Unsupported receipt policy; reconcile before recovery"
            )
        instant = timestamp(event["accepted_at"])
    elif event.get("event_type") == "deletion_completed":
        required = {
            "schema_version",
            "event_type",
            "job_id",
            "account_ref",
            "retired_generation",
            "scope",
            "completed_at",
        }
        if not required.issubset(event) or set(event) - required - {
            "event_id",
            "fencing_token",
            "disposition",
            "retained_categories",
        }:
            raise RecoveryBlocked("Unsupported completion schema")
        if key != f"events/{job}/completed.json":
            raise RecoveryBlocked("Completion key mismatch")
        if "event_id" in event and event["event_id"] != job:
            raise RecoveryBlocked("Completion event mismatch")
        if "fencing_token" in event:
            positive_integer(event["fencing_token"])
        if event.get("retained_categories"):
            raise RecoveryBlocked(
                "Retention exceptions require an approved restore handler"
            )
        instant = timestamp(event["completed_at"])
    else:
        raise RecoveryBlocked("Unsupported event type")
    if instant > server_time + 60:
        raise RecoveryBlocked("Journal event is in the future")
    return event


def check_deadline(deadline):
    if deadline is not None and time.monotonic() >= deadline:
        raise RecoveryBlocked("Independent authority verification deadline exceeded")


@lru_cache(maxsize=1)
def authority_client():
    """Admission cannot inherit the general client's long retry budget."""
    import boto3
    from botocore.config import Config
    from .config import settings

    cfg = settings()
    return boto3.client(
        "s3",
        region_name=cfg.aws_region,
        endpoint_url=cfg.aws_endpoint_url
        if cfg.environment in ("local", "test")
        else None,
        config=Config(
            signature_version="s3v4",
            connect_timeout=1,
            read_timeout=1,
            ignore_configured_endpoint_urls=True,
            retries={"max_attempts": 0},
            s3={"addressing_style": "path"},
        ),
    )


def bounded_version_read(s3, bucket, key, version, limit, deadline):
    check_deadline(deadline)
    if not version or version == "null":
        raise RecoveryBlocked("Pinned authority version is required")
    result = s3.get_object(Bucket=bucket, Key=key, VersionId=version)
    try:
        if (
            result.get("VersionId") != version
            or result.get("ContentLength", limit + 1) > limit
        ):
            raise RecoveryBlocked("Authority version identity or byte bound failed")
        raw = result["Body"].read(limit + 1)
    finally:
        result["Body"].close()
    check_deadline(deadline)
    if len(raw) > limit:
        raise RecoveryBlocked("Authority byte bound failed")
    return raw


def inventory(s3, bucket, prefix, max_items=INVENTORY_LIMIT, deadline=None):
    """List all versions; deleted, replaced or unversioned evidence is invalid."""
    entries = []
    keys = set()
    paginator = s3.get_paginator("list_object_versions")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        check_deadline(deadline)
        if page.get("DeleteMarkers"):
            raise RecoveryBlocked(
                "A protected journal prefix contains deletion markers"
            )
        for row in page.get("Versions", []):
            key, version = row["Key"], row.get("VersionId")
            if (
                not version
                or version == "null"
                or key in keys
                or not row.get("IsLatest")
            ):
                raise RecoveryBlocked(
                    "Journal contains replaced or unversioned evidence"
                )
            keys.add(key)
            entries.append({"key": key, "version_id": version})
            if len(entries) > max_items:
                raise RecoveryBlocked(
                    "Journal inventory exceeds the reviewed recovery bound"
                )
    return sorted(entries, key=lambda x: (x["key"], x["version_id"]))


def read_inventory(
    bucket, entries, available_keys, server_time, reader=None, deadline=None
):
    def read_one(row):
        check_deadline(deadline)
        raw = (reader or versioned_read)(
            bucket, row["key"], row["version_id"], EVENT_LIMIT
        )
        event = validate_event(row["key"], raw, available_keys, server_time)
        return {**row, "sha256": hashlib.sha256(raw).hexdigest(), "event": event}

    result = []
    # Bound pending futures instead of enqueuing the entire 100k-event inventory.
    with ThreadPoolExecutor(max_workers=8) as executor:
        for start in range(0, len(entries), 1000):
            result.extend(executor.map(read_one, entries[start : start + 1000]))
    return result


def build_plan(rows):
    accepted, completed, subjects, account_subjects = {}, {}, {}, {}
    for row in rows:
        event = row["event"]
        target = accepted if event["event_type"] == "deletion_accepted" else completed
        if event["job_id"] in target:
            raise RecoveryBlocked("Duplicate logical journal event")
        target[event["job_id"]] = row
    if set(completed) - set(accepted):
        raise RecoveryBlocked("Completion is missing its acceptance evidence")
    for job_id, row in accepted.items():
        event = row["event"]
        subject = event["subject_ref_hmac"]
        account = event["account_ref"]
        prior_subject = account_subjects.setdefault(account, subject)
        if prior_subject != subject:
            raise RecoveryBlocked("Account maps to conflicting subject references")
        state = subjects.setdefault(subject, {"account_ref": account, "events": []})
        if state["account_ref"] != account:
            raise RecoveryBlocked("Subject maps to multiple account references")
        state["events"].append(row)
        if job_id in completed:
            terminal = completed[job_id]["event"]
            for field in ["account_ref", "retired_generation", "scope"]:
                if terminal[field] != event[field]:
                    raise RecoveryBlocked("Completion conflicts with acceptance")
            if timestamp(terminal["completed_at"]) < timestamp(event["accepted_at"]):
                raise RecoveryBlocked("Completion predates acceptance")
    barriers = {}
    for subject, state in subjects.items():
        events = sorted(
            state["events"], key=lambda row: row["event"]["retired_generation"]
        )
        generations = set()
        deleted = False
        for row in events:
            event = row["event"]
            if event["retired_generation"] != len(generations) + 1 or deleted:
                raise RecoveryBlocked(
                    "Conflicting generation history or post-account-deletion writes"
                )
            generations.add(event["retired_generation"])
            deleted = event["scope"] == "account"
        latest = events[-1]["event"]
        done = latest["job_id"] in completed
        barriers[subject] = {
            "account_ref": state["account_ref"],
            "generation": latest["new_generation"],
            "state": (
                "deleted" if latest["scope"] == "account" else "awaiting_generation_ack"
            )
            if done
            else "deleting",
        }
    return {"accepted": accepted, "completed": completed, "barriers": barriers}


def retained_version(s3, cfg, row, server_time, deadline=None):
    """Verify actual S3 retention, encryption and pinned identity in cloud."""
    if cfg.environment not in ("qa", "prod"):
        return
    check_deadline(deadline)
    from datetime import timedelta

    head = s3.head_object(
        Bucket=cfg.journal_bucket, Key=row["key"], VersionId=row["version_id"]
    )
    retention = s3.get_object_retention(
        Bucket=cfg.journal_bucket, Key=row["key"], VersionId=row["version_id"]
    ).get("Retention", {})
    until, modified = retention.get("RetainUntilDate"), head.get("LastModified")
    if (
        head.get("VersionId") != row["version_id"]
        or head.get("ServerSideEncryption") != "aws:kms"
        or head.get("SSEKMSKeyId") != cfg.journal_kms_key_id
        or retention.get("Mode") != "COMPLIANCE"
        or not isinstance(until, datetime)
        or not isinstance(modified, datetime)
        or until.tzinfo is None
        or modified.tzinfo is None
        or until < modified + timedelta(days=90)
        or until.timestamp() <= server_time
    ):
        raise RecoveryBlocked(
            "Independent journal version is not retained and encrypted by the reviewed policy"
        )


def retained_inventory(
    s3, cfg, prefix, server_time, max_items=INVENTORY_LIMIT, deadline=None
):
    rows = inventory(s3, cfg.journal_bucket, prefix, max_items, deadline)
    for row in rows:
        retained_version(s3, cfg, row, server_time, deadline)
    return rows


def load_authority(cfg, server_time):
    """Read independent control, all deletion events and recovery activations.

    Inventory limits are hard refusal bounds, never truncation. The maintenance
    path must archive/extend retained evidence before these bounds are reached.
    """
    deadline = time.monotonic() + 10
    s3, bucket = authority_client(), cfg.journal_bucket
    def read(bucket, key, version, limit):
        return bounded_version_read(s3,bucket,key,version,limit,deadline)
    if s3.get_bucket_versioning(Bucket=bucket).get("Status") != "Enabled":
        raise RecoveryBlocked("Independent journal versioning is required")
    if cfg.environment in ("qa", "prod"):
        lock = s3.get_object_lock_configuration(Bucket=bucket).get(
            "ObjectLockConfiguration", {}
        )
        rule = lock.get("Rule", {}).get("DefaultRetention", {})
        if (
            lock.get("ObjectLockEnabled") != "Enabled"
            or rule.get("Mode") != "COMPLIANCE"
            or type(rule.get("Days")) is not int
            or rule["Days"] < 90
        ):
            raise RecoveryBlocked(
                "Independent journal requires actual COMPLIANCE Object Lock"
            )
    controls = retained_inventory(s3, cfg, "control/", server_time, 10, deadline)
    if len(controls) != 1 or controls[0]["key"] != "control/established.json":
        raise RecoveryBlocked("Missing or ambiguous independent journal continuity")
    control_row = controls[0]
    raw = read(bucket, control_row["key"], control_row["version_id"], EVENT_LIMIT)
    control = strict_loads(raw)
    if (
        not isinstance(control, dict)
        or canonical(control) != raw
        or control.get("schema_version") != "1.0.0"
        or control.get("environment") != cfg.environment
        or control.get("minimum_retention_days") != 90
        or control.get("maximum_recovery_age_days") != 35
        or timestamp(control.get("established_at")) > server_time
    ):
        raise RecoveryBlocked("Independent journal control policy mismatch")
    control_receipt = {**control_row, "sha256": hashlib.sha256(raw).hexdigest()}
    from .identity_keys import key_descriptor

    first = retained_inventory(s3, cfg, "events/", server_time, deadline=deadline)
    rows = read_inventory(
        bucket, first, {key_descriptor(cfg)["key_id"]}, server_time, read, deadline
    )
    if first != inventory(s3, bucket, "events/", deadline=deadline):
        raise RecoveryBlocked(
            "Journal changed during admission; retry against a stable authority"
        )
    plan = build_plan(rows)
    activations = []
    for entry in retained_inventory(s3, cfg, "recovery/", server_time, 10000, deadline):
        raw = read(bucket, entry["key"], entry["version_id"], EVENT_LIMIT)
        body = strict_loads(raw)
        required = {
            "schema_version",
            "event_type",
            "recovery_id",
            "environment",
            "account",
            "region",
            "source_revision",
            "backup_created_at",
            "control",
            "watermark",
            "inventory_sha256",
            "activated_at",
            "authentication_cutoff",
            "scopes_suspended",
        }
        if (
            not isinstance(body, dict)
            or set(body) != required
            or canonical(body) != raw
            or body["schema_version"] != "1.0.0"
            or body["event_type"] != "RecoveryActivation"
            or entry["key"] != "recovery/" + uuid_text(body["recovery_id"]) + ".json"
            or body["environment"] != cfg.environment
            or body["account"] != cfg.deployment_account
            or body["region"] != cfg.aws_region
            or not re.fullmatch(r"[0-9a-f]{40}", body.get("source_revision") or "")
            or body["control"] != control_receipt
            or type(body["authentication_cutoff"]) is not int
            or not 0
            <= body["authentication_cutoff"]
            <= timestamp(body["activated_at"]) + 60
            or body["scopes_suspended"] is not True
            or timestamp(body["activated_at"]) > server_time + 60
            or timestamp(body["backup_created_at"]) > timestamp(body["activated_at"])
            or not HEX.fullmatch(body.get("inventory_sha256") or "")
        ):
            raise RecoveryBlocked(
                "Unknown, foreign or invalid independent recovery activation"
            )
        watermark = body["watermark"]
        if (
            not isinstance(watermark, dict)
            or set(watermark) != {"key", "version_id", "sha256"}
            or watermark["key"] != f"watermarks/{body['recovery_id']}.json"
            or not HEX.fullmatch(watermark.get("sha256") or "")
        ):
            raise RecoveryBlocked("Invalid retained recovery watermark reference")
        retained_version(s3, cfg, watermark, server_time, deadline)
        watermark_raw = read(
            bucket, watermark["key"], watermark["version_id"], MANIFEST_LIMIT
        )
        manifest = strict_loads(watermark_raw)
        event_receipts = manifest.get("events") if isinstance(manifest, dict) else None
        if (
            hashlib.sha256(watermark_raw).hexdigest() != watermark["sha256"]
            or canonical(manifest) != watermark_raw
            or manifest.get("watermark_id") != body["recovery_id"]
            or manifest.get("environment") != cfg.environment
            or manifest.get("backup_created_at") != body["backup_created_at"]
            or manifest.get("inventory_sha256") != body["inventory_sha256"]
            or not isinstance(event_receipts, list)
            or manifest.get("event_count") != len(event_receipts)
            or digest(event_receipts) != body["inventory_sha256"]
        ):
            raise RecoveryBlocked("Retained recovery watermark content mismatch")
        actual = {
            r["key"]: {k: r[k] for k in ("key", "version_id", "sha256")} for r in rows
        }
        if any(
            not isinstance(r, dict) or r != actual.get(r.get("key"))
            for r in event_receipts
        ):
            raise RecoveryBlocked(
                "Accepted deletion evidence disappeared after recovery"
            )
        activations.append(
            {
                "body": body,
                "receipt": {**entry, "sha256": hashlib.sha256(raw).hexdigest()},
            }
        )
    activations.sort(
        key=lambda r: (r["body"]["authentication_cutoff"], r["body"]["activated_at"])
    )
    if any(
        a["body"]["authentication_cutoff"] >= b["body"]["authentication_cutoff"]
        for a, b in zip(activations, activations[1:])
    ):
        raise RecoveryBlocked("Ambiguous independent recovery authority order")
    check_deadline(deadline)
    return {
        "control": control_receipt,
        "plan": plan,
        "activation": activations[-1] if activations else None,
        "deadline": deadline,
    }


def verify_database_authority(db, authority, recovery_required=False):
    """A restored active database cannot override a retained deletion barrier."""
    from .db import Account, Job, SystemState

    activation, plan = authority["activation"], authority["plan"]
    recovery = db.get(SystemState, "recovery")
    if activation:
        body, receipt = activation["body"], activation["receipt"]
        if (
            not recovery
            or recovery.body.get("verified") is not True
            or recovery.body.get("recovery_id") != body["recovery_id"]
            or recovery.body.get("journal_activation") != receipt
            or recovery.body.get("authentication_cutoff")
            != body["authentication_cutoff"]
            or recovery.body.get("inventory_sha256") != body["inventory_sha256"]
            or recovery.body.get("scopes_suspended") is not True
        ):
            raise RecoveryBlocked(
                "Database is behind the independently retained recovery activation"
            )
    elif recovery_required or (recovery and recovery.body.get("verified")):
        raise RecoveryBlocked("Database recovery claim has no independent activation")
    for job_id, row in plan["accepted"].items():
        check_deadline(authority.get("deadline"))
        event, job = row["event"], db.get(Job, job_id)
        receipt = job.body.get("journal_receipt", {}) if job else {}
        if (
            not job
            or job.kind != "deletion"
            or not job.journal_accepted
            or job.account_id != event["account_ref"]
            or job.generation != event["retired_generation"]
            or job.body.get("scope") != event["scope"]
            or receipt.get("version_id") != row["version_id"]
            or receipt.get("sha256") != row["sha256"]
        ):
            raise RecoveryBlocked(
                "Database is missing an independently accepted deletion"
            )
    for subject, barrier in plan["barriers"].items():
        check_deadline(authority.get("deadline"))
        account = db.get(Account, barrier["account_ref"])
        if (
            not account
            or account.subject_hash != subject
            or account.generation != barrier["generation"]
            or (barrier["state"] == "deleted" and account.state != "deleted")
            or (barrier["state"] == "deleting" and account.state != "deleting")
        ):
            raise RecoveryBlocked(
                "Restored subject or generation conflicts with retained deletion evidence"
            )
    return activation["body"]["authentication_cutoff"] if activation else 0


def require_authority(db):
    from .config import settings
    from .db import now
    from .errors import Problem

    cfg = settings()
    if cfg.environment == "test" and not cfg.independent_recovery_admission:
        return 0
    try:
        from .journal_continuity import verify_binding

        verify_binding(db, cfg)
        if cfg.environment == "local" and not cfg.independent_recovery_admission:
            return 0
        return verify_database_authority(
            db, load_authority(cfg, now()), cfg.recovery_required
        )
    except Exception:
        # SDK errors may contain identifiers. Fail closed without logging content.
        raise Problem(
            503, "INDEPENDENT_RECOVERY_NOT_VERIFIED", retryable=True
        ) from None


def main():
    """Maintenance pre-activation check; zero exit requires actual authority."""
    import json
    from .db import factory
    from .config import settings

    with factory()() as db:
        require_authority(db)
    print(
        json.dumps(
            {
                "status": "admission_verified",
                "environment": settings().environment,
                "services_enabled": False,
            }
        )
    )


if __name__ == "__main__":
    main()
