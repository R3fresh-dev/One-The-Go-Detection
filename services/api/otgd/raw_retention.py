"""Separate optional-purpose receipts and frozen, version-exact raw retention.

Study acceptance never implies raw consent. Upload-ticket expiration is not a
retention deadline. All lifetimes are frozen before storage admission, and the
maintenance sweep continues to reconcile purged keys for late PUT versions.
"""

import hashlib
import hmac
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, model_validator
from sqlalchemy import Float, ForeignKey, Integer, JSON, String, func, select, text
from sqlalchemy.orm import Mapped, mapped_column

from .canonical import canonical, digest
from .config import settings
from .db import Account, Artifact, Base, Record, iso, now, uid
from .domain import rec_id, record
from .dto import DTO, Name, SHA, UTC, UUID
from .errors import Problem
from .operator_governance import active_body, raw_recording_supported

RAW_KINDS = ("eye_video", "ecg_waveform")
CHANNELS = {"eye_video": "eyes", "ecg_waveform": "ecg"}


class RawRetention(Base):
    __tablename__ = "raw_retention"
    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("artifacts.id"), primary_key=True
    )
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    generation: Mapped[int] = mapped_column(Integer)
    study_id: Mapped[str] = mapped_column(String(256))
    kind: Mapped[str] = mapped_column(String(32))
    # Independently preserve these references even after artifact metadata purge.
    bucket: Mapped[str] = mapped_column(String(128))
    key: Mapped[str] = mapped_column(String(300))
    authority: Mapped[dict] = mapped_column(JSON)
    retained_until: Mapped[float] = mapped_column(Float, index=True)
    state: Mapped[str] = mapped_column(String(24), default="retained", index=True)
    cleanup_next_at: Mapped[float] = mapped_column(Float, default=0, index=True)
    cleanup_completed_at: Mapped[float | None] = mapped_column(Float, nullable=True)


class RawUploadTicket(Base):
    """Append-only authority for renewed bearer write windows, never raw lifetime."""

    __tablename__ = "raw_upload_tickets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("raw_retention.artifact_id"), index=True
    )
    issued_at: Mapped[float] = mapped_column(Float)
    expires_at: Mapped[float] = mapped_column(Float)


def admitted_write_deadline(db, row):
    renewed = db.scalar(
        select(func.max(RawUploadTicket.expires_at)).where(
            RawUploadTicket.artifact_id == row.artifact_id
        )
    )
    return max(row.authority["upload_expires_at"], renewed or 0)


def renew_ticket_authority(db, account, artifact):
    # The same retention-row lock serializes renewal with cleanup claims.
    row = assert_artifact_admitted(db, account, artifact)
    if artifact.state != "quarantine":
        raise Problem(409, "RAW_ARTIFACT_ALREADY_SETTLED")
    issued = now()
    if row.retained_until <= issued + 360:
        raise Problem(403, "RAW_RETENTION_WINDOW_CLOSED")
    if (
        db.scalar(
            select(func.count())
            .select_from(RawUploadTicket)
            .where(RawUploadTicket.artifact_id == artifact.id)
        )
        >= 100
    ):
        raise Problem(429, "RAW_TICKET_RENEWAL_LIMIT")
    deadline = issued + 300
    db.add(
        RawUploadTicket(artifact_id=artifact.id, issued_at=issued, expires_at=deadline)
    )
    artifact.expires = deadline
    row.cleanup_next_at = min(row.cleanup_next_at, issued)
    db.flush()
    return row


class RawChoice(DTO):
    record: bool
    upload: bool

    @model_validator(mode="after")
    def recording_first(self):
        if self.upload and not self.record:
            raise ValueError("Upload requires explicit recording consent")
        return self


class RawChoices(DTO):
    eye_video: RawChoice
    ecg_waveform: RawChoice


class RawPreferences(DTO):
    consent_record_id: UUID
    policy_id: Name
    policy_version: Name
    policy_sha256: SHA
    raw_notice_version: Name
    raw_notice_sha256: SHA
    acknowledged_at: UTC
    choices: RawChoices


class RawRevocation(DTO):
    confirmation: Literal[True]
    artifact_kinds: Annotated[
        list[Literal["eye_video", "ecg_waveform"]], Field(min_length=1, max_length=2)
    ]

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.artifact_kinds)) != len(self.artifact_kinds):
            raise ValueError("Duplicate raw kind")
        return self


def timestamp(text):
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
            raise ValueError()
        return parsed.timestamp()
    except (ValueError, AttributeError, TypeError):
        raise Problem(422, "RAW_CAPTURE_CLOCK_INVALID") from None


def off():
    return {kind: {"record": False, "upload": False} for kind in RAW_KINDS}


def payload_reference(account_id, generation, kind, sha256):
    key = settings().tombstone_key
    if len(key) != 64:
        raise Problem(503, "RAW_METADATA_KEY_UNAVAILABLE")
    return hmac.new(
        bytes.fromhex(key),
        canonical(["raw-payload-v1", account_id, generation, kind, sha256]),
        hashlib.sha256,
    ).hexdigest()


def current_consent(db, account, study_id):
    study = active_body(db, "study", study_id)
    consent = record(db, account, "consent", study_id)
    if (
        account.state != "active"
        or account.id not in study.get("account_refs", [])
        or not consent
        or consent.body.get("state") != "active"
        or not consent.body.get("consent_record_id")
        or any(
            consent.body.get(key) != study.get(key)
            for key in ("invitation_id", "document_version", "document_sha256")
        )
    ):
        raise Problem(403, "CURRENT_CONSENT_REQUIRED")
    return study, consent


def approved_policy(db, study_id, policy_id):
    policy = active_body(db, "retention", policy_id)
    if (
        policy.get("study_id") != study_id
        or policy.get("policy_id") != policy_id
        or not policy.get("purpose_id")
        or not policy.get("purpose_text")
        or not policy.get("access_roles")
        or policy.get("withdrawal_behavior") != "delete_live_data"
        or type(policy.get("max_retention_days")) is not int
        or not 1 <= policy["max_retention_days"] <= 3650
        or policy.get("exceptions")
        or not policy.get("raw_notice_text")
        or not policy.get("raw_notice_version")
        or hashlib.sha256(policy["raw_notice_text"].encode()).hexdigest()
        != policy.get("raw_notice_sha256")
    ):
        raise Problem(403, "RAW_RETENTION_POLICY_UNAVAILABLE")
    return policy


def study_policy(db, study, study_id):
    policies = set()
    allowed = set()
    for kind, channel in CHANNELS.items():
        config_id = study.get("channels", {}).get(channel)
        if not config_id:
            continue
        config = active_body(db, "configuration", config_id)
        if (
            config.get("study_id") == study_id
            and config.get("channel") == channel
            and config.get("raw_retention_approved") is True
        ):
            policies.add(config.get("retention_policy_id"))
            if raw_recording_supported(config, kind):
                allowed.add(kind)
    if len(policies) != 1 or None in policies:
        raise Problem(403, "RAW_RETENTION_POLICY_UNAVAILABLE")
    policy = approved_policy(db, study_id, policies.pop())
    return policy, allowed.intersection(policy.get("raw_kinds", []))


def _put_record(db, account, kind, key, body, *, pointer=False):
    id = rec_id(account, kind, key)
    row = db.get(Record, id)
    if row and not pointer:
        raise Problem(409, "IMMUTABLE_RAW_RECEIPT_EXISTS")
    if row:
        row.generation = account.generation
        row.body = body
        row.sha256 = digest(body)
        row.revision += 1
        row.created = now()
    else:
        row = Record(
            id=id,
            account_id=account.id,
            generation=account.generation,
            kind=kind,
            body=body,
            sha256=digest(body),
            created=now(),
        )
        db.add(row)
    return row


def _preference(db, account, study_id):
    row = record(db, account, "raw_preference", study_id)
    if row and row.sha256 != digest(row.body):
        raise Problem(403, "RAW_AUTHORITY_INTEGRITY_FAILURE")
    return row


def _policy_view(policy):
    return {
        "policy_id": policy["policy_id"],
        "version": policy["version"],
        "sha256": digest(policy),
        "content": policy,
        "purpose_id": policy["purpose_id"],
        "purpose": policy["purpose_text"],
        "raw_kinds": policy["raw_kinds"],
        "max_retention_days": policy["max_retention_days"],
        "expires_at": iso(policy["expires_at"]),
        "access_roles": policy["access_roles"],
        "withdrawal_behavior": policy["withdrawal_behavior"],
        "exceptions": policy["exceptions"],
        "retention_basis": "first_owned_acquisition_start",
        "raw_notice": {
            "version": policy["raw_notice_version"],
            "sha256": policy["raw_notice_sha256"],
            "content": policy["raw_notice_text"],
        },
    }


def raw_status(db, account, study_id, artifact_cursor=None):
    policy = None
    allowed = set()
    consent_id = None
    reason = "RAW_RETENTION_POLICY_UNAVAILABLE"
    try:
        study, consent = current_consent(db, account, study_id)
        consent_id = consent.body["consent_record_id"]
        policy, allowed = study_policy(db, study, study_id)
    except Problem as exc:
        reason = exc.code
    pointer = _preference(db, account, study_id)
    current = bool(
        policy
        and pointer
        and pointer.body.get("policy_sha256") == digest(policy)
        and pointer.body.get("consent_record_id") == consent_id
    )
    receipt = (
        record(db, account, "raw_consent_receipt", pointer.body["receipt_id"])
        if current
        else None
    )
    if current and (not receipt or receipt.sha256 != digest(receipt.body)):
        raise Problem(403, "RAW_AUTHORITY_INTEGRITY_FAILURE")
    receipt_fields = (
        "receipt_id",
        "consent_record_id",
        "policy_id",
        "policy_version",
        "policy_sha256",
        "raw_notice_version",
        "raw_notice_sha256",
        "acknowledged_at",
        "accepted_at",
        "choices",
    )
    query = select(RawRetention).where(
        RawRetention.account_id == account.id,
        RawRetention.generation == account.generation,
        RawRetention.study_id == study_id,
        RawRetention.kind.in_(RAW_KINDS),
    )
    if artifact_cursor is not None:
        query = query.where(RawRetention.artifact_id > artifact_cursor)
    rows = list(db.scalars(query.order_by(RawRetention.artifact_id).limit(501)))
    has_more_artifacts = len(rows) > 500
    rows = rows[:500]
    revocations = list(
        db.scalars(
            select(Record)
            .where(
                Record.account_id == account.id,
                Record.generation == account.generation,
                Record.kind == "raw_revocation",
                Record.body["study_id"].as_string() == study_id,
            )
            .order_by(Record.created.desc())
            .limit(100)
        )
    )
    return {
        "study_id": study_id,
        "consent_record_id": consent_id,
        "receipt_id": pointer.body["receipt_id"] if current else None,
        "preference_receipt": {key: receipt.body[key] for key in receipt_fields}
        if current
        else None,
        "choices": pointer.body["choices"] if current else off(),
        "policy": _policy_view(policy) if policy else None,
        "availability": {
            kind: {
                "record_allowed": kind in allowed,
                "upload_allowed": kind in allowed,
                "reasons": []
                if kind in allowed
                else ["RAW_CODEC_UNIMPLEMENTED" if policy else reason],
            }
            for kind in RAW_KINDS
        },
        "has_more_artifacts": has_more_artifacts,
        "next_artifact_cursor": rows[-1].artifact_id if has_more_artifacts else None,
        "artifacts": [
            {
                "artifact_id": r.artifact_id,
                "artifact_kind": r.kind,
                "state": r.state,
                "upload_state": db.get(Artifact, r.artifact_id).state,
                "retention_due_at": iso(r.retained_until),
                "cleanup_completed_at": iso(r.cleanup_completed_at)
                if r.cleanup_completed_at
                else None,
            }
            for r in rows
        ],
        "revocations": [
            {
                "receipt_id": r.body["receipt_id"],
                "artifact_kinds": r.body["artifact_kinds"],
                "accepted_at": r.body["accepted_at"],
                "state": "cleanup_pending"
                if db.scalar(
                    select(func.count())
                    .select_from(RawRetention)
                    .where(
                        RawRetention.account_id == account.id,
                        RawRetention.generation == account.generation,
                        RawRetention.artifact_id.in_(r.body["artifact_ids"]),
                        RawRetention.state != "purged",
                    )
                )
                else "completed",
            }
            for r in revocations
            if r.body["study_id"] == study_id
        ],
    }


def _retire(db, account, study_id, kinds):
    ids = []
    rows = db.scalars(
        select(RawRetention)
        .where(
            RawRetention.account_id == account.id,
            RawRetention.generation == account.generation,
            RawRetention.study_id == study_id,
            RawRetention.kind.in_(kinds),
            RawRetention.state != "purged",
        )
        .with_for_update()
    )
    for row in rows:
        ids.append(row.artifact_id)
        row.state = "cleanup_pending"
        row.cleanup_next_at = 0
        artifact = db.get(Artifact, row.artifact_id)
        if artifact:
            artifact.state = "cleanup_pending"
    return ids


def set_preferences(db, account, study_id, body):
    study, consent = current_consent(db, account, study_id)
    policy, allowed = study_policy(db, study, study_id)
    if (
        body.consent_record_id != consent.body["consent_record_id"]
        or body.policy_id != policy["policy_id"]
        or body.policy_version != policy["version"]
        or body.policy_sha256 != digest(policy)
        or body.raw_notice_version != policy["raw_notice_version"]
        or body.raw_notice_sha256 != policy["raw_notice_sha256"]
    ):
        raise Problem(409, "RAW_PURPOSE_REVIEW_REQUIRED")
    ack = timestamp(body.acknowledged_at)
    if ack > now() + 5 or ack < now() - 86400:
        raise Problem(422, "RAW_ACKNOWLEDGMENT_CLOCK_INVALID")
    choices = body.choices.data()
    if any(
        (choices[k]["record"] or choices[k]["upload"]) and k not in allowed
        for k in RAW_KINDS
    ):
        raise Problem(403, "RAW_KIND_UNAVAILABLE")
    prior = _preference(db, account, study_id)
    if prior:
        disabled = [
            k
            for k in RAW_KINDS
            if any(prior.body["choices"][k].values()) and not all(choices[k].values())
        ]
        if disabled:
            revoke_raw(
                db,
                account,
                study_id,
                RawRevocation(confirmation=True, artifact_kinds=disabled),
                status=False,
            )
    receipt_id = uid()
    value = {
        **body.data(),
        "receipt_id": receipt_id,
        "study_id": study_id,
        "accepted_at": iso(),
        "purpose_id": policy["purpose_id"],
        "choices": choices,
    }
    _put_record(db, account, "raw_consent_receipt", receipt_id, value)
    _put_record(db, account, "raw_preference", study_id, value, pointer=True)
    db.flush()
    return raw_status(db, account, study_id)


def revoke_raw(db, account, study_id, body, *, status=True):
    pointer = _preference(db, account, study_id)
    choices = {
        k: dict(v) for k, v in (pointer.body["choices"] if pointer else off()).items()
    }
    for kind in body.artifact_kinds:
        choices[kind] = {"record": False, "upload": False}
    receipt = uid()
    value = {
        "receipt_id": receipt,
        "study_id": study_id,
        "artifact_kinds": body.artifact_kinds,
        "accepted_at": iso(),
        "artifact_ids": _retire(db, account, study_id, body.artifact_kinds),
    }
    _put_record(db, account, "raw_revocation", receipt, value)
    if pointer:
        _put_record(
            db,
            account,
            "raw_preference",
            study_id,
            {**pointer.body, "choices": choices},
            pointer=True,
        )
    db.flush()
    return (
        {**raw_status(db, account, study_id), "accepted_receipt_id": receipt}
        if status
        else value
    )


def raw_start_permission(db, account, check, config, kind):
    """Resolve recording consent before native capture, independently of tickets."""
    if (
        kind not in RAW_KINDS
        or CHANNELS[kind] != config.get("channel")
        or config.get("raw_retention_approved") is not True
    ):
        raise Problem(403, "RAW_KIND_UNAVAILABLE")
    if not raw_recording_supported(config, kind):
        raise Problem(403, "RAW_CODEC_UNIMPLEMENTED")
    _, consent = current_consent(db, account, check.study_id)
    policy = approved_policy(db, check.study_id, config.get("retention_policy_id"))
    pointer = _preference(db, account, check.study_id)
    if (
        kind not in policy["raw_kinds"]
        or not pointer
        or pointer.body["consent_record_id"] != consent.body["consent_record_id"]
        or pointer.body["policy_sha256"] != digest(policy)
        or pointer.body["choices"][kind]["record"] is not True
    ):
        raise Problem(403, "OPTIONAL_RAW_CONSENT_REQUIRED")
    receipt = record(db, account, "raw_consent_receipt", pointer.body["receipt_id"])
    if not receipt or receipt.sha256 != digest(receipt.body):
        raise Problem(403, "RAW_AUTHORITY_INTEGRITY_FAILURE")
    return {
        "record": True,
        "upload": pointer.body["choices"][kind]["upload"],
        "receipt_id": receipt.body["receipt_id"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["version"],
        "policy_sha256": digest(policy),
        "raw_notice_version": policy["raw_notice_version"],
        "raw_notice_sha256": policy["raw_notice_sha256"],
    }


def admit_artifact(db, account, check, body, config):
    if body.artifact_kind not in RAW_KINDS:
        raise Problem(403, "ADMINISTRATIVE_RAW_ROUTE_REQUIRED")
    if not raw_recording_supported(config, body.artifact_kind):
        raise Problem(403, "RAW_CODEC_UNIMPLEMENTED")
    if (
        db.scalar(
            select(func.count())
            .select_from(RawRetention)
            .where(
                RawRetention.account_id == account.id, RawRetention.state != "purged"
            )
        )
        >= 100
    ):
        raise Problem(
            429, "RAW_RECORDING_LIMIT_EXCEEDED", headers={"Retry-After": "60"}
        )
    _, consent = current_consent(db, account, check.study_id)
    policy = approved_policy(db, check.study_id, body.retention_policy_id)
    pointer = _preference(db, account, check.study_id)
    if (
        not config.get("raw_retention_approved")
        or config.get("study_id") != check.study_id
        or config.get("channel") != CHANNELS[body.artifact_kind]
        or config.get("retention_policy_id") != body.retention_policy_id
        or body.artifact_kind not in policy["raw_kinds"]
        or not pointer
        or body.consent_record_id != consent.body["consent_record_id"]
        or pointer.body.get("consent_record_id") != body.consent_record_id
        or pointer.body.get("policy_sha256") != digest(policy)
        or pointer.body.get("receipt_id") != body.raw_consent_record_id
        or not all(pointer.body["choices"][body.artifact_kind].values())
    ):
        raise Problem(403, "OPTIONAL_RAW_CONSENT_REQUIRED")
    receipt = record(db, account, "raw_consent_receipt", body.raw_consent_record_id)
    attempt = (
        record(db, account, "attempt", body.attempt_id) if body.attempt_id else None
    )
    if (
        not receipt
        or receipt.sha256 != digest(receipt.body)
        or not attempt
        or attempt.sha256 != digest(attempt.body)
        or attempt.parent_id != check.id
        or attempt.body.get("component")
        != ("eyes" if body.artifact_kind == "eye_video" else "cardiac")
        or (
            body.artifact_kind == "ecg_waveform"
            and (
                attempt.body.get("component_metadata", {}).get("modality")
                or attempt.body.get("component_metadata", {})
                .get("projection", {})
                .get("modality")
            )
            != "ecg"
        )
        or attempt.body.get("started_at") != body.capture_started_at
        or attempt.body.get("configuration_id") != config.get("configuration_id")
        or attempt.body.get("configuration_hash") != config.get("sha256")
        or attempt.body.get("status") not in ("started", "valid", "invalid")
    ):
        raise Problem(403, "OWNED_RAW_ACQUISITION_REQUIRED")
    started = timestamp(body.capture_started_at)
    if (
        started > now() + 5
        or started < receipt.created - 5
        or attempt.created < receipt.created
    ):
        raise Problem(422, "RAW_CAPTURE_CLOCK_INVALID")
    # Choose the earlier independently observed owned start; a client clock
    # cannot extend retention, and later terminal updates/retries cannot reset it.
    acquired = min(started, attempt.created)
    due = acquired + policy["max_retention_days"] * 86400
    fingerprint = payload_reference(
        account.id, account.generation, body.artifact_kind, body.sha256
    )
    prior = db.scalars(
        select(RawRetention).where(
            RawRetention.account_id == account.id,
            RawRetention.generation == account.generation,
            RawRetention.kind == body.artifact_kind,
            RawRetention.authority["payload_ref_hmac"].as_string() == fingerprint,
        )
    )
    for row in prior:
        due = min(due, row.retained_until)
    if due <= now() + 360:
        raise Problem(403, "RAW_RETENTION_WINDOW_CLOSED")
    return {
        "policy_id": policy["policy_id"],
        "policy_version": policy["version"],
        "policy_sha256": digest(policy),
        "purpose_id": policy["purpose_id"],
        "raw_notice_sha256": policy["raw_notice_sha256"],
        "consent_record_id": body.consent_record_id,
        "raw_consent_record_id": body.raw_consent_record_id,
        "attempt_id": body.attempt_id,
        "configuration_id": config["configuration_id"],
        "configuration_sha256": config["sha256"],
        "configuration_submitted_sha256": digest(config),
        "acquired_at": iso(acquired),
        "retained_until": due,
        "access_roles": policy["access_roles"],
        "withdrawal_behavior": policy["withdrawal_behavior"],
        "exceptions": [],
    }


def administrative_authority(
    db, account, check, policy_id, purpose, acquired_at, *, operator_role
):
    _, consent = current_consent(db, account, check.study_id)
    policy = approved_policy(db, check.study_id, policy_id)
    if (
        purpose != policy["purpose_id"]
        or "source_lab_report" not in policy["raw_kinds"]
        or operator_role not in policy["access_roles"]
        or operator_role
        not in ("lab_importer", "study_operator", "lab_report_revision")
    ):
        raise Problem(403, "ADMINISTRATIVE_RAW_PURPOSE_REQUIRED")
    acquired = timestamp(acquired_at)
    if acquired > now() + 5 or abs(acquired - check.created) > 0.001:
        raise Problem(422, "RAW_CAPTURE_CLOCK_INVALID")
    acquired = min(acquired, check.created)
    due = acquired + policy["max_retention_days"] * 86400
    if due <= now() + 360:
        raise Problem(403, "RAW_RETENTION_WINDOW_CLOSED")
    return {
        "policy_id": policy_id,
        "policy_version": policy["version"],
        "policy_sha256": digest(policy),
        "purpose_id": purpose,
        "operator_role": operator_role,
        "acquired_at": iso(acquired),
        "consent_record_id": consent.body["consent_record_id"],
        "retained_until": due,
        "access_roles": policy["access_roles"],
        "withdrawal_behavior": policy["withdrawal_behavior"],
        "exceptions": [],
    }


def attach_retention(db, artifact, authority):
    if db.get(RawRetention, artifact.id):
        raise Problem(409, "RAW_RETENTION_ALREADY_FROZEN")
    row = RawRetention(
        artifact_id=artifact.id,
        account_id=artifact.account_id,
        generation=artifact.generation,
        study_id=artifact.scope["study_id"],
        kind=artifact.kind,
        bucket=artifact.bucket,
        key=artifact.key,
        authority={
            **authority,
            "upload_expires_at": artifact.expires,
            "artifact_sha256": artifact.sha256,
            "payload_ref_hmac": payload_reference(
                artifact.account_id, artifact.generation, artifact.kind, artifact.sha256
            ),
        },
        retained_until=authority["retained_until"],
        state="retained",
        cleanup_next_at=0,
    )
    db.add(row)
    return row


def assert_artifact_admitted(db, account, artifact):
    row = db.scalar(
        select(RawRetention)
        .where(RawRetention.artifact_id == artifact.id)
        .with_for_update()
    )
    if (
        not row
        or row.account_id != account.id
        or row.generation != account.generation
        or account.state != "active"
        or artifact.state not in ("quarantine", "verified")
        or row.state != "retained"
        or row.retained_until <= now()
    ):
        raise Problem(403, "RAW_RETENTION_WINDOW_CLOSED")
    if (
        artifact.bucket != row.bucket
        or artifact.key != row.key
        or artifact.expires != admitted_write_deadline(db, row)
        or artifact.sha256 != row.authority.get("artifact_sha256")
    ):
        raise Problem(403, "RAW_AUTHORITY_INTEGRITY_FAILURE")
    policy = approved_policy(db, row.study_id, row.authority["policy_id"])
    if digest(policy) != row.authority["policy_sha256"]:
        raise Problem(403, "RAW_PURPOSE_REVIEW_REQUIRED")
    _, consent = current_consent(db, account, row.study_id)
    if consent.body["consent_record_id"] != row.authority["consent_record_id"]:
        raise Problem(403, "CURRENT_CONSENT_REQUIRED")
    if row.kind in RAW_KINDS:
        config = active_body(db, "configuration", row.authority["configuration_id"])
        if digest(config) != row.authority["configuration_submitted_sha256"]:
            raise Problem(403, "RAW_CONFIGURATION_REVIEW_REQUIRED")
        if artifact.state == "verified":
            receipt = record(db, account, "raw_verification", artifact.id)
            attempt = record(db, account, "attempt", row.authority["attempt_id"])
            expected = {
                "schema_version": "1.0.0",
                "artifact_id": artifact.id,
                "version_id": artifact.version_id,
                "sha256": artifact.sha256,
                "codec": config["material"].get("raw_encoding"),
                "attempt_id": row.authority["attempt_id"],
                "configuration_id": config["configuration_id"],
                "configuration_sha256": config["sha256"],
                "configuration_submitted_sha256": digest(config),
            }
            if (
                not receipt
                or receipt.parent_id != artifact.session_id
                or receipt.sha256 != digest(receipt.body)
                or set(receipt.body) != {*expected, "evidence_sha256", "verified_at"}
                or not artifact.version_id
                or artifact.version_id == "null"
                or any(
                    receipt.body.get(key) != value for key, value in expected.items()
                )
                or not attempt
                or attempt.parent_id != artifact.session_id
                or attempt.sha256 != digest(attempt.body)
                or attempt.body.get("source") != "prototype_sensor"
                or attempt.body.get("status") not in ("valid", "invalid")
                or attempt.body.get("configuration_id") != config["configuration_id"]
                or attempt.body.get("configuration_hash") != config["sha256"]
                or artifact.scope.get("attempt_id") != row.authority["attempt_id"]
            ):
                raise Problem(403, "AUTHENTICATED_RAW_VERIFICATION_REQUIRED")
            evidence = receipt.body.get("evidence_sha256")
            if row.kind == "eye_video":
                actual = attempt.body.get("component_metadata", {}).get("native_result")
                if (
                    not isinstance(actual, dict)
                    or evidence != digest(actual)
                    or attempt.body.get("status") != "valid"
                    or actual.get("run_id") != attempt.body.get("record_id")
                    or actual.get("configuration_sha256") != config["sha256"]
                    or actual.get("started_at") != attempt.body.get("started_at")
                    or actual.get("ended_at") != attempt.body.get("ended_at")
                ):
                    raise Problem(403, "AUTHENTICATED_RAW_VERIFICATION_REQUIRED")
            else:
                refs = attempt.body.get("attestation_refs", [])
                if not isinstance(refs, list) or not 1 <= len(refs) <= 64:
                    raise Problem(403, "AUTHENTICATED_RAW_VERIFICATION_REQUIRED")
                matched = False
                for ref in refs:
                    accepted = (
                        record(db, account, "attestation", ref)
                        if isinstance(ref, str)
                        else None
                    )
                    if (
                        accepted
                        and accepted.parent_id == artifact.session_id
                        and accepted.sha256 == digest(accepted.body)
                        and evidence == digest(accepted.body)
                    ):
                        matched = True
                        break
                if not matched:
                    raise Problem(403, "AUTHENTICATED_RAW_VERIFICATION_REQUIRED")
            if timestamp(receipt.body["verified_at"]) > now() + 5:
                raise Problem(403, "AUTHENTICATED_RAW_VERIFICATION_REQUIRED")
        pointer = _preference(db, account, row.study_id)
        if (
            not pointer
            or consent.body["consent_record_id"] != row.authority["consent_record_id"]
            or pointer.body["receipt_id"] != row.authority["raw_consent_record_id"]
            or not all(pointer.body["choices"][row.kind].values())
        ):
            raise Problem(403, "OPTIONAL_RAW_CONSENT_REQUIRED")
    return row


def _exact_version_rows(s3, bucket, key):
    rows = []
    for page in s3.get_paginator("list_object_versions").paginate(
        Bucket=bucket, Prefix=key
    ):
        for item in page.get("Versions", []) + page.get("DeleteMarkers", []):
            if item["Key"] != key:
                continue
            version = item.get("VersionId")
            if not isinstance(version, str) or not version or version == "null":
                raise RuntimeError("Raw cleanup requires exact versioned storage")
            rows.append({"Key": key, "VersionId": version,
                         "DeleteMarker": item in page.get("DeleteMarkers", [])})
            if len(rows) > 10000:
                raise RuntimeError(
                    "Raw version inventory exceeds its bounded cleanup contract"
                )
    return rows


def exact_versions(s3, bucket, key):
    return [row["VersionId"] for row in _exact_version_rows(s3, bucket, key)]


def purge_exact_key(s3, bucket, key):
    from .replica_cleanup import prepare_delete
    rows = _exact_version_rows(s3, bucket, key)
    prepare_delete(s3, bucket, key, rows, exact_key=True)
    for row in rows:
        s3.delete_object(Bucket=bucket, Key=key, VersionId=row['VersionId'])
    if exact_versions(s3, bucket, key):
        raise RuntimeError("Raw versions remain after cleanup; retry required")


def cleanup_raw_once(session_factory, s3, *, tick=None):
    tick = now() if tick is None else tick
    ids = []
    with session_factory.begin() as db:
        rows = db.scalars(
            select(RawRetention)
            .where(RawRetention.cleanup_next_at <= tick)
            .order_by(RawRetention.cleanup_next_at, RawRetention.artifact_id)
            .with_for_update(skip_locked=True)
            .limit(100)
        )
        for row in rows:
            account = db.get(Account, row.account_id)
            expired = (
                row.retained_until <= tick
                or not account
                or account.generation != row.generation
                or account.state != "active"
            )
            artifact = db.get(Artifact, row.artifact_id)
            expired = (
                expired
                or not artifact
                or artifact.state in ("cleanup_pending", "purged")
                or (artifact.state == "quarantine" and artifact.expires < tick - 60)
            )
            try:
                if row.authority.get("legacy_unqualified") or row.authority.get(
                    "compaction"
                ):
                    raise Problem(403, "LEGACY_RAW_AUTHORITY_UNAVAILABLE")
                policy = approved_policy(db, row.study_id, row.authority["policy_id"])
                expired = expired or digest(policy) != row.authority["policy_sha256"]
                _, consent = (
                    current_consent(db, account, row.study_id)
                    if account
                    else (None, None)
                )
                expired = (
                    expired
                    or not consent
                    or consent.body["consent_record_id"]
                    != row.authority["consent_record_id"]
                )
                if row.kind in RAW_KINDS:
                    config = active_body(
                        db, "configuration", row.authority["configuration_id"]
                    )
                    expired = (
                        expired
                        or digest(config)
                        != row.authority["configuration_submitted_sha256"]
                    )
                    pointer = (
                        _preference(db, account, row.study_id) if account else None
                    )
                    expired = (
                        expired
                        or not pointer
                        or not consent
                        or pointer.body["receipt_id"]
                        != row.authority["raw_consent_record_id"]
                        or not all(pointer.body["choices"][row.kind].values())
                    )
            except Problem:
                expired = True
            row.cleanup_next_at = tick + (
                900 if expired or row.state != "retained" else 60
            )
            if expired or row.state != "retained":
                if row.state != "purged":
                    row.state = "cleanup_pending"
                # Retain the current conditional-write barrier while its URL
                # remains usable. Authority is revoked now; bytes are removed
                # only after the frozen ticket deadline + completion margin.
                write_deadline = admitted_write_deadline(db, row) + 60
                if tick >= write_deadline:
                    ids.append((row.artifact_id, row.bucket, row.key))
                else:
                    row.cleanup_next_at = write_deadline
    failures = 0
    for id, bucket, key in ids:
        try:
            purge_exact_key(s3, bucket, key)
            with session_factory.begin() as db:
                row = db.get(RawRetention, id)
                if row:
                    row.state = "purged"
                    if row.cleanup_completed_at is None:
                        row.cleanup_completed_at = now()
                    account = db.get(Account, row.account_id)
                    retired = (
                        not account
                        or account.generation != row.generation
                        or account.state == "deleted"
                    )
                    compact = {
                        "compaction": "generation_retired"
                        if retired
                        else "payload_purged",
                        "upload_expires_at": row.authority["upload_expires_at"],
                    }
                    if not retired:
                        compact["payload_ref_hmac"] = row.authority.get(
                            "payload_ref_hmac"
                        )
                    row.authority = compact
                    if retired:
                        row.study_id = "retired-generation"
                        row.kind = "raw_cleanup_reference"
                    artifact = db.get(Artifact, id)
                    if artifact:
                        artifact.state = "purged"
                        artifact.version_id = None
                        artifact.size = 0
                        artifact.scope = {}
                        artifact.sha256 = "0" * 64
        except Exception:
            failures += 1
    return {"processed": len(ids), "failures": failures}


def migration_004_raw_retention(connection):
    """Add a lifecycle table without rewriting v1 evidence or granting old raw authority."""
    from .db import SystemState

    key = "migration:004_raw_retention"
    expected = {"migration": 4, "table": "raw_retention", "evidence_rewritten": False}
    prior = connection.scalar(select(SystemState.body).where(SystemState.key == key))
    if prior is not None and prior != expected:
        raise RuntimeError("Raw-retention migration identity conflict")
    RawRetention.__table__.create(connection, checkfirst=True)
    RawUploadTicket.__table__.create(connection, checkfirst=True)
    # Historical raw rows have no optional-purpose/independent retention proof.
    # Preserve the artifact row and v1 evidence while scheduling fail-closed
    # cleanup; do not manufacture consent or a new approved lifetime.
    missing = connection.execute(
        select(Artifact.__table__).where(
            Artifact.kind.in_([*RAW_KINDS, "source_lab_report"]),
            ~Artifact.id.in_(select(RawRetention.artifact_id)),
        )
    )
    for artifact in missing.mappings():
        connection.execute(
            RawRetention.__table__.insert().values(
                artifact_id=artifact["id"],
                account_id=artifact["account_id"],
                generation=artifact["generation"],
                study_id=artifact["scope"].get("study_id", "legacy-unqualified"),
                kind=artifact["kind"],
                bucket=artifact["bucket"],
                key=artifact["key"],
                authority={
                    "legacy_unqualified": True,
                    "upload_expires_at": artifact["expires"],
                    "payload_ref_hmac": payload_reference(
                        artifact["account_id"],
                        artifact["generation"],
                        artifact["kind"],
                        artifact["sha256"],
                    ),
                },
                retained_until=artifact["expires"],
                state="cleanup_pending",
                cleanup_next_at=0,
            )
        )
    if connection.dialect.name == "postgresql":
        connection.execute(
            text("""CREATE OR REPLACE FUNCTION otgd_raw_ticket_immutable() RETURNS trigger
          LANGUAGE plpgsql AS $$ BEGIN
            RAISE EXCEPTION 'Raw ticket deadlines are append-only' USING ERRCODE='23514';
          END $$""")
        )
        connection.execute(
            text("DROP TRIGGER IF EXISTS raw_ticket_immutable ON raw_upload_tickets")
        )
        connection.execute(
            text(
                "CREATE TRIGGER raw_ticket_immutable BEFORE UPDATE OR DELETE ON raw_upload_tickets FOR EACH ROW EXECUTE FUNCTION otgd_raw_ticket_immutable()"
            )
        )
        connection.execute(
            text("""CREATE OR REPLACE FUNCTION otgd_raw_retention_immutable() RETURNS trigger
            LANGUAGE plpgsql AS $$ BEGIN
              IF TG_OP = 'DELETE' OR NEW.artifact_id IS DISTINCT FROM OLD.artifact_id
                OR NEW.account_id IS DISTINCT FROM OLD.account_id OR NEW.generation IS DISTINCT FROM OLD.generation
                OR NEW.bucket IS DISTINCT FROM OLD.bucket OR NEW.key IS DISTINCT FROM OLD.key
                OR NEW.retained_until IS DISTINCT FROM OLD.retained_until THEN
                RAISE EXCEPTION 'Raw authority and lifetime are immutable' USING ERRCODE='23514';
              END IF;
              IF NEW.authority::jsonb IS DISTINCT FROM OLD.authority::jsonb
                OR NEW.study_id IS DISTINCT FROM OLD.study_id OR NEW.kind IS DISTINCT FROM OLD.kind THEN
                IF NEW.state <> 'purged' OR OLD.authority->>'compaction' = 'generation_retired' THEN
                  RAISE EXCEPTION 'Raw metadata compaction is one-way after purge' USING ERRCODE='23514';
                END IF;
                IF NEW.authority::jsonb = jsonb_build_object('compaction', 'payload_purged',
                    'upload_expires_at', OLD.authority->'upload_expires_at', 'payload_ref_hmac', OLD.authority->'payload_ref_hmac')
                  AND OLD.authority->>'compaction' IS DISTINCT FROM 'payload_purged'
                  AND NEW.study_id = OLD.study_id AND NEW.kind = OLD.kind THEN
                  RETURN NEW;
                END IF;
                IF NEW.authority::jsonb = jsonb_build_object('compaction', 'generation_retired',
                    'upload_expires_at', OLD.authority->'upload_expires_at')
                  AND NEW.study_id = 'retired-generation' AND NEW.kind = 'raw_cleanup_reference'
                  AND EXISTS(SELECT 1 FROM accounts WHERE id=OLD.account_id
                    AND (generation <> OLD.generation OR state='deleted')) THEN
                  RETURN NEW;
                END IF;
                RAISE EXCEPTION 'Raw metadata compaction differs from its bounded contract' USING ERRCODE='23514';
              END IF;
              RETURN NEW;
            END $$""")
        )
        connection.execute(
            text("DROP TRIGGER IF EXISTS raw_retention_immutable ON raw_retention")
        )
        connection.execute(
            text(
                "CREATE TRIGGER raw_retention_immutable BEFORE UPDATE OR DELETE ON raw_retention FOR EACH ROW EXECUTE FUNCTION otgd_raw_retention_immutable()"
            )
        )
        connection.execute(
            text("""CREATE OR REPLACE FUNCTION otgd_raw_receipt_immutable() RETURNS trigger
            LANGUAGE plpgsql AS $$ BEGIN
              IF OLD.kind IN ('raw_consent_receipt', 'raw_revocation') THEN
                RAISE EXCEPTION 'Raw consent and revocation receipts are immutable' USING ERRCODE='23514';
              END IF;
              RETURN NEW;
            END $$""")
        )
        connection.execute(
            text("DROP TRIGGER IF EXISTS raw_receipt_immutable ON records")
        )
        connection.execute(
            text(
                "CREATE TRIGGER raw_receipt_immutable BEFORE UPDATE ON records FOR EACH ROW EXECUTE FUNCTION otgd_raw_receipt_immutable()"
            )
        )
    if prior is None:
        connection.execute(
            SystemState.__table__.insert().values(key=key, body=expected)
        )
