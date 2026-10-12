"""Per-study reapproval after restore; no database-only suspension override.

The independently retained seal binds fresh three-principal registry decisions.
The global recovery barrier remains suspended for every unsealed study.
"""

import hashlib
import re
import time

from sqlalchemy import select

from .canonical import canonical, digest, strict_loads
from .config import settings
from .db import RegistryEvent, SystemState, iso, now, uid
from .errors import Problem
from .operator_governance import released_version, validate_dependencies
from .recovery_authority import (
    RecoveryBlocked,
    authority_client,
    bounded_version_read,
    inventory,
    retained_version,
    timestamp,
    require_authority,
)


def references(db, study_id, cutoff):
    """Exact dependency closure; every approval must follow recovery activation."""
    refs = {}

    def visit(kind, id):
        key = kind + ":" + id
        if key in refs:
            return
        if len(refs) >= 256:
            raise Problem(413, "RECOVERY_SCOPE_LIMIT")
        row = released_version(db, kind, id)
        decisions = list(
            db.scalars(
                select(RegistryEvent)
                .where(RegistryEvent.version_id == row.id)
                .order_by(RegistryEvent.revision)
            )
        )
        if row.submitted_at <= cutoff or any(
            event.created <= cutoff for event in decisions
        ):
            raise Problem(403, "FRESH_RECOVERY_REAPPROVAL_REQUIRED")
        refs[key] = {
            "kind": kind,
            "registry_id": id,
            "version": row.version,
            "sha256": row.sha256,
            "decisions_sha256": digest(
                [
                    {
                        "revision": x.revision,
                        "principal": x.principal,
                        "state": x.state,
                        "sha256": x.submitted_sha256,
                        "created_at": iso(x.created),
                    }
                    for x in decisions
                ]
            ),
        }
        body = row.body
        validate_dependencies(db, kind, body)
        if kind == "study":
            for config in body["channels"].values():
                visit("configuration", config)
            if body.get("model_id"):
                visit("model", body["model_id"])
        elif kind == "configuration":
            visit("study", body["study_id"])
            visit("qualification", body["qualification_evidence_ref"])
            visit("retention", body["retention_policy_id"])
            if body.get("device_id"):
                visit("device", body["device_id"] + ":" + body["key_id"])
                visit("calibration", body["calibration_id"])
            for method, policy in body.get("lab_methods", {}).items():
                visit("method", method)
                for calibration in policy["calibration_ids"]:
                    visit("calibration", calibration)
        elif kind == "model":
            visit("calibration", body["manifest"]["calibration_id"])
            if body.get("native_timing_calibration_id"):
                visit("calibration", body["native_timing_calibration_id"])
        elif kind == "calibration" and body["purpose"] == "device":
            visit("device", body["device_id"] + ":" + body["key_id"])

    visit("study", study_id)
    if len(refs) > 256:
        raise Problem(413, "RECOVERY_SCOPE_LIMIT")
    return [refs[key] for key in sorted(refs)]


def prefix(recovery_id, study_id):
    return (
        "scope-resumptions/"
        + recovery_id
        + "/"
        + hashlib.sha256(study_id.encode()).hexdigest()
        + "/"
    )


def seal_study(db, study_id, principal):
    from .storage import put_versioned

    cfg = settings()
    require_authority(db)
    state = db.get(SystemState, "recovery")
    if (
        not state
        or not state.body.get("verified")
        or state.body.get("scopes_suspended") is not True
    ):
        raise Problem(409, "RECOVERY_NOT_SUSPENDED")
    body = state.body
    refs = references(db, study_id, body["authentication_cutoff"])
    seal = {
        "schema_version": "1.0.0",
        "event_type": "RecoveredStudyReapproval",
        "seal_id": uid(),
        "environment": cfg.environment,
        "account": cfg.deployment_account,
        "region": cfg.aws_region,
        "source_revision": cfg.source_revision,
        "recovery_id": body["recovery_id"],
        "recovery_activation": body["journal_activation"],
        "study_id": study_id,
        "references": refs,
        "references_sha256": digest(refs),
        "sealed_at": iso(),
        "sealed_by": principal,
    }
    key = prefix(body["recovery_id"], study_id) + seal["seal_id"] + ".json"
    raw = canonical(seal)
    version = put_versioned(cfg.journal_bucket, key, raw, conditional=True)
    s3 = authority_client()
    receipt = {"key": key, "version_id": version, "sha256": digest(seal)}
    deadline = time.monotonic() + 10
    retained_version(s3, cfg, receipt, now(), deadline)
    if (
        bounded_version_read(s3, cfg.journal_bucket, key, version, 262144, deadline)
        != raw
    ):
        raise Problem(503, "RECOVERY_SCOPE_SEAL_NOT_VERIFIED")
    return {"study_id": study_id, "seal": receipt, "global_scopes_suspended": True}


def require_study_scope(db, study_id, account=None):
    state = db.get(SystemState, "recovery")
    if not state:
        return
    if state.body.get("scopes_suspended") is not True:
        raise Problem(403, "RECOVERED_SCOPE_SUSPENDED")
    try:
        cfg = settings()
        body = state.body
        if not body.get("verified") or not body.get("journal_activation"):
            raise RecoveryBlocked("Missing activation")
        refs = references(db, study_id, body["authentication_cutoff"])
        s3 = authority_client()
        deadline = time.monotonic() + 10
        entries = inventory(
            s3, cfg.journal_bucket, prefix(body["recovery_id"], study_id), 100, deadline
        )
        seals = []
        required = {
            "schema_version",
            "event_type",
            "seal_id",
            "environment",
            "account",
            "region",
            "source_revision",
            "recovery_id",
            "recovery_activation",
            "study_id",
            "references",
            "references_sha256",
            "sealed_at",
            "sealed_by",
        }
        for row in entries:
            retained_version(s3, cfg, row, now(), deadline)
            raw = bounded_version_read(
                s3, cfg.journal_bucket, row["key"], row["version_id"], 262144, deadline
            )
            seal = strict_loads(raw)
            if (
                set(seal) != required
                or canonical(seal) != raw
                or seal["schema_version"] != "1.0.0"
                or seal["event_type"] != "RecoveredStudyReapproval"
                or row["key"]
                != prefix(body["recovery_id"], study_id) + seal["seal_id"] + ".json"
                or seal["environment"] != cfg.environment
                or seal["account"] != cfg.deployment_account
                or seal["region"] != cfg.aws_region
                or cfg.environment in ("qa", "prod")
                and not re.fullmatch("[0-9a-f]{40}", seal["source_revision"] or "")
                or seal["recovery_id"] != body["recovery_id"]
                or seal["recovery_activation"] != body["journal_activation"]
                or seal["study_id"] != study_id
                or digest(seal["references"]) != seal["references_sha256"]
                or timestamp(seal["sealed_at"]) <= body["authentication_cutoff"]
                or timestamp(seal["sealed_at"]) > now() + 5
                or not isinstance(seal["sealed_by"], str)
                or not seal["sealed_by"]
            ):
                raise RecoveryBlocked("Invalid reapproval seal")
            seals.append(seal)
        if not seals or max(seals, key=lambda x: x["sealed_at"])["references"] != refs:
            raise RecoveryBlocked("Current scope not sealed")
        if account is not None:
            from .domain import record

            consent = record(db, account, "consent", study_id)
            if (
                not consent
                or timestamp(consent.body.get("accepted_at", ""))
                <= body["authentication_cutoff"]
            ):
                raise RecoveryBlocked("Fresh participant consent required")
    except Exception:
        raise Problem(403, "RECOVERED_SCOPE_SUSPENDED") from None
