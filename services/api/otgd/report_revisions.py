"""Immutable, operator-authorized laboratory report companions.

These records revise a report about an existing specimen. They never replace the
captured session, alter its evidence manifest, or run an intoxication model.
"""

from __future__ import annotations

import math
from copy import deepcopy
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Request
from jsonschema.exceptions import ValidationError as SchemaError
from pydantic import Field, ValidationError, model_validator
from sqlalchemy import func, select

from . import storage
from .auth import recent
from .canonical import canonical, digest
from .config import settings
from .db import Artifact, Record, iso, now, uid
from .domain import (
    NOTICE_SHA,
    owned_check,
    qualification,
    rec_id,
    record,
    registry,
    safe_result,
    save_record,
    validate_measurement,
    validate_session,
)
from .dto import DTO, SHA, UTC, UUID, ArtifactRequest, CompleteArtifact, Name, Source
from .errors import Problem

router = APIRouter(tags=["administrative-report-revisions"])
PURPOSE = "administrative_report_revision"
MAX_REVISIONS = 20
MAX_RECORD_BYTES = 512 * 1024
MAX_INDEX_BYTES = 16 * 1024
MAX_REPORT_BYTES = 8 * 1024 * 1024
ANALYTES = ("OH11_THC", "THC", "THC_COOH")
REASONS = {
    "correction": "CORRECTED_LABORATORY_REPORT",
    "reanalysis": "SPECIMEN_REANALYSIS",
}


class ReportRevisionRequest(DTO):
    schema_version: Literal["1.0.0"]
    revision_id: UUID
    study_id: Name
    sample_id: UUID
    base_snapshot_sha256: SHA
    expected_previous_revision_id: UUID | None
    expected_previous_revision_sha256: SHA | None
    kind: Literal["correction", "reanalysis"]
    reason_code: Literal["CORRECTED_LABORATORY_REPORT", "SPECIMEN_REANALYSIS"]
    reported_at: UTC
    source_report_artifact_id: UUID
    replacement_measurements: Annotated[list[dict], Field(min_length=1, max_length=3)]

    @model_validator(mode="after")
    def coherent(self):
        if (self.expected_previous_revision_id is None) != (
            self.expected_previous_revision_sha256 is None
        ) or REASONS[self.kind] != self.reason_code:
            raise ValueError("Report revision identity is inconsistent")
        return self


class MethodApproval(DTO):
    calibration_ids: Annotated[list[Name], Field(min_length=1, max_length=32)]
    instrument_ids: Annotated[list[Name], Field(min_length=1, max_length=32)]

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.calibration_ids)) != len(self.calibration_ids) or len(
            set(self.instrument_ids)
        ) != len(self.instrument_ids):
            raise ValueError("Duplicate laboratory approval identity")
        return self


class ReportAuthorization(DTO):
    operator_account_ref: UUID
    study_id: Name
    protocol_id: Name
    configuration_id: Name
    configuration_sha256: SHA
    consent_record_id: UUID
    retention_policy_id: Name
    approved_lab_methods: Annotated[dict[Name, MethodApproval], Field(max_length=3)]


class VerifiedReport(DTO):
    artifact_id: UUID
    version_id: Annotated[str, Field(min_length=1, max_length=1024)]
    sha256: SHA
    media_type: Literal["application/pdf"]
    size_bytes: Annotated[int, Field(gt=0, le=MAX_REPORT_BYTES)]

    @model_validator(mode="after")
    def versioned(self):
        if self.version_id == "null":
            raise ValueError("A versioned report is required")
        return self


class ReportContent(DTO):
    kind: Literal["correction", "reanalysis"]
    reason_code: Literal["CORRECTED_LABORATORY_REPORT", "SPECIMEN_REANALYSIS"]
    reported_at: UTC
    replacement_measurements: Annotated[list[dict], Field(min_length=1, max_length=3)]
    source_report: VerifiedReport
    authorization: ReportAuthorization


class ReportDescriptor(DTO):
    schema_version: Literal["1.0.0"]
    revision_id: UUID
    session_id: UUID
    data_generation: Annotated[int, Field(gt=0, le=9007199254740991)]
    base_snapshot_sha256: SHA
    base_evidence_sha256: SHA
    previous_revision_id: UUID | None
    previous_revision_sha256: SHA | None
    original_target_at: UTC
    original_collected_at: UTC
    original_capture_completed_at: UTC
    report: ReportContent


class ReportRevisionResult(DTO):
    schema_version: Literal["1.0.0"]
    result_kind: Literal["administrative_report_result"]
    result_id: UUID
    session_id: UUID
    revision_id: UUID
    revision_sha256: SHA
    base_snapshot_sha256: SHA
    target_at: UTC
    evaluated_at: UTC
    state: Literal["measurement_only", "invalid", "inconclusive"]
    reason_codes: list[Name]
    provenance_summary: Annotated[list[Source], Field(min_length=1, max_length=4)]
    replaces_result_id: UUID
    inference_available: Literal[False]
    probability: None
    classification: None
    model_id: None


class ReportRevisionCompanion(DTO):
    schema_version: Literal["1.0.0"]
    record_type: Literal["administrative_report_revision"]
    revision_id: UUID
    session_id: UUID
    data_generation: Annotated[int, Field(gt=0, le=9007199254740991)]
    sequence: Annotated[int, Field(ge=1, le=MAX_REVISIONS)]
    accepted_at: UTC
    descriptor: ReportDescriptor
    revision_sha256: SHA
    effective_measurements: Annotated[list[dict], Field(max_length=3)]
    result: ReportRevisionResult
    result_sha256: SHA


class ReportRevisionSummary(DTO):
    revision_id: UUID
    revision_sha256: SHA
    sequence: Annotated[int, Field(ge=1, le=MAX_REVISIONS)]
    kind: Literal["correction", "reanalysis"]
    reported_at: UTC
    accepted_at: UTC
    previous_revision_id: UUID | None
    next_revision_id: UUID | None
    result_id: UUID
    result_state: Literal["measurement_only", "invalid", "inconclusive"]


class ReportRevisionList(DTO):
    schema_version: Literal["1.0.0"]
    session_id: UUID
    data_generation: Annotated[int, Field(gt=0, le=9007199254740991)]
    base_snapshot_sha256: SHA
    base_result_id: UUID
    original_target_at: UTC
    original_collected_at: UTC | None
    original_capture_completed_at: UTC
    latest_revision_id: UUID | None
    items: Annotated[list[ReportRevisionSummary], Field(max_length=MAX_REVISIONS)]


class ReportRevisionDetail(DTO):
    schema_version: Literal["1.0.0"]
    session_id: UUID
    data_generation: Annotated[int, Field(gt=0, le=9007199254740991)]
    revision: ReportRevisionCompanion
    previous_revision_id: UUID | None
    next_revision_id: UUID | None


class ReportRevisionIndexItem(DTO):
    revision_id: UUID
    sequence: Annotated[int, Field(ge=1, le=MAX_REVISIONS)]
    revision_sha256: SHA
    result_id: UUID
    result_sha256: SHA
    path: Annotated[str, Field(min_length=1, max_length=128)]
    sha256: SHA
    size_bytes: Annotated[int, Field(gt=0, le=MAX_RECORD_BYTES)]


class ReportRevisionIndex(DTO):
    schema_version: Literal["1.0.0"]
    session_id: UUID
    data_generation: Annotated[int, Field(gt=0, le=9007199254740991)]
    base_snapshot_sha256: SHA
    items: Annotated[list[ReportRevisionIndexItem], Field(max_length=MAX_REVISIONS)]


def _epoch(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _finite_expiry(value):
    return type(value) in (int, float) and math.isfinite(value) and value > now()


def _names(value, maximum, width):
    return (
        isinstance(value, list)
        and len(value) <= maximum
        and all(isinstance(v, str) and 1 <= len(v) <= width for v in value)
        and len(value) == len(set(value))
    )


def _integrity():
    raise Problem(503, "REPORT_REVISION_INTEGRITY")


def _validated_base(db, account, check):
    if (
        check.state not in ("completed", "invalid")
        or not check.snapshot
        or not check.result
        or not check.snapshot_sha256
        or not check.evidence_sha256
    ):
        raise Problem(409, "BASE_RESULT_NOT_FINALIZED")
    snapshot = check.snapshot
    try:
        validate_session(snapshot)
        result = safe_result(check.result, db=db, account=account, check=check)
        manifest = record(db, account, "manifest", check.id)
        if (
            snapshot["session_id"] != check.id
            or snapshot["subject_ref"] != account.id
            or snapshot["mode"] != check.mode
            or snapshot["study_id"] != check.study_id
            or snapshot["protocol_id"] != check.protocol_id
            or digest(snapshot) != check.snapshot_sha256
            or result["session_id"] != check.id
            or result["input_sha256"] != check.snapshot_sha256
            or result["target_at"] != snapshot["target_at"]
            or not manifest
            or manifest.sha256 != check.evidence_sha256
            or digest(manifest.body) != check.evidence_sha256
            or manifest.body["session_id"] != check.id
        ):
            _integrity()
    except (KeyError, TypeError, ValueError, ValidationError, SchemaError):
        _integrity()
    return snapshot


def _base(db, account, check):
    snapshot = _validated_base(db, account, check)
    if check.result["state"] not in ("measurement_only", "invalid", "inconclusive"):
        _integrity()
    return snapshot


def _authorize(request, db, account, claims, session_id):
    """This is deliberately before any administrative idempotency replay."""
    from .main import generation

    if generation(request) != account.generation:
        raise Problem(410, "DATA_GENERATION_RETIRED")
    if account.state != "active":
        raise Problem(403, "ACCOUNT_NOT_WRITABLE")
    if account.notice != NOTICE_SHA:
        raise Problem(403, "NOTICE_ACKNOWLEDGMENT_REQUIRED")
    recent(claims)
    check = owned_check(db, account, session_id)
    snapshot = _base(db, account, check)
    if check.mode == "synthetic" or any(
        reading["source"] == "simulated" for reading in snapshot["saliva"]
    ):
        raise Problem(403, "SYNTHETIC_REPORT_REVISION_UNAVAILABLE")
    if (
        snapshot["sample"]["status"] == "not_collected"
        or snapshot["sample"]["collected_at"] is None
    ):
        raise Problem(422, "REPORT_SAMPLE_MISMATCH")
    try:
        role = registry(db, "role", account.id)
    except Problem:
        raise Problem(403, "LAB_REPORT_REVISION_ROLE_REQUIRED") from None
    if (
        not isinstance(role, dict)
        or not _names(role.get("roles"), 16, 64)
        or not _names(role.get("study_ids"), 64, 256)
        or "lab_report_revision" not in role["roles"]
        or check.study_id not in role["study_ids"]
        or not _finite_expiry(role.get("expires_at"))
    ):
        raise Problem(403, "LAB_REPORT_REVISION_ROLE_REQUIRED")
    try:
        study = registry(db, "study", check.study_id)
        configuration_id = study["channels"]["saliva"]
        if (
            not isinstance(configuration_id, str)
            or not 1 <= len(configuration_id) <= 256
        ):
            raise ValueError()
        config = registry(db, "configuration", configuration_id)
        proof = registry(db, "qualification", config["qualification_evidence_ref"])
        if not _finite_expiry(config.get("expires_at")) or not _finite_expiry(
            proof.get("expires_at")
        ):
            raise ValueError()
        config = qualification(db, account, check, "saliva", configuration_id)
        if not check.protocol_id or config.get("protocol_id") != check.protocol_id:
            raise Problem(403, "CONFIGURATION_MISMATCH")
        consent = record(db, account, "consent", check.study_id)
        authority = ReportAuthorization(
            operator_account_ref=account.id,
            study_id=check.study_id,
            protocol_id=check.protocol_id,
            configuration_id=configuration_id,
            configuration_sha256=config["sha256"],
            consent_record_id=consent.body["consent_record_id"],
            retention_policy_id=config["retention_policy_id"],
            approved_lab_methods={},
        ).data()
        methods = config.get("lab_methods")
        if (
            not isinstance(methods, dict)
            or not 1 <= len(methods) <= 16
            or any(not isinstance(k, str) or not 1 <= len(k) <= 256 for k in methods)
        ):
            raise Problem(403, "REPORT_METHOD_UNAVAILABLE")
        methods = {
            key: MethodApproval.model_validate(value).data()
            for key, value in methods.items()
        }
        if config.get("raw_retention_approved") is not True:
            raise Problem(403, "RAW_RETENTION_UNAVAILABLE")
    except (KeyError, TypeError, ValueError, ValidationError, AttributeError):
        raise Problem(403, "REPORT_METHOD_UNAVAILABLE") from None
    return check, authority, methods


def _artifact(
    db, account, check, artifact_id, authority, *, purpose=False, verified=False
):
    row = db.scalar(
        select(Artifact)
        .where(Artifact.id == artifact_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if (
        not row
        or row.account_id != account.id
        or row.generation != account.generation
        or row.session_id != check.id
    ):
        raise Problem(404, "NOT_FOUND")
    if row.state not in ("quarantine", "verified"):
        raise Problem(410, "ARTIFACT_RETIRED")
    if (
        row.kind != "source_lab_report"
        or row.media_type != "application/pdf"
        or not 0 < row.size <= MAX_REPORT_BYTES
        or not isinstance(row.scope, dict)
        or row.scope.get("study_id") != check.study_id
        or row.scope.get("session_id") != check.id
        or row.scope.get("consent_record_id") != authority["consent_record_id"]
        or row.scope.get("retention_policy_id") != authority["retention_policy_id"]
        or (purpose and row.scope.get("purpose") != PURPOSE)
    ):
        raise Problem(403, "VERIFIED_REPORT_REQUIRED")
    if (verified and row.state != "verified") or (
        row.state == "verified"
        and (
            not isinstance(row.version_id, str)
            or not 1 <= len(row.version_id) <= 1024
            or row.version_id == "null"
        )
    ):
        raise Problem(403, "VERIFIED_REPORT_REQUIRED")
    from .raw_retention import assert_artifact_admitted

    assert_artifact_admitted(db, account, row)
    return row


def _ticket_fingerprint(row):
    return digest(
        [
            row.id,
            row.account_id,
            row.generation,
            row.session_id,
            row.bucket,
            row.key,
            row.kind,
            row.sha256,
            row.size,
            row.media_type,
            row.expires,
            row.scope,
        ]
    )


def _complete_matches(row, body):
    if (body.sha256, body.size_bytes, body.media_type) != (
        row.sha256,
        row.size,
        row.media_type,
    ):
        raise Problem(422, "ARTIFACT_MISMATCH")


def ensure_artifact_capacity(db, account_id, additional_bytes):
    """Bounded aggregate admission; durable purged receipts consume no quota."""
    pending = Artifact.state.in_(["quarantine", "cleanup_pending"])
    count, pending_bytes, live_bytes = db.execute(
        select(
            func.count(Artifact.id).filter(pending),
            func.coalesce(func.sum(Artifact.size).filter(pending), 0),
            func.coalesce(
                func.sum(Artifact.size).filter(Artifact.state != "purged"), 0
            ),
        ).where(Artifact.account_id == account_id)
    ).one()
    if (
        count >= 3
        or pending_bytes + additional_bytes > 128 * 1024 * 1024
        or live_bytes + additional_bytes > 1024**3
    ):
        raise Problem(429, "LIMIT_EXCEEDED", headers={"Retry-After": "60"})


def _replay_if_present(request, db, account, claims, revoked):
    """No unfinished dedup record is committed before external verification."""
    from .db import Dedup
    from .main import answer, operation

    key = request.headers.get("idempotency-key", "")
    if not 1 <= len(key) <= 128 or any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise Problem(422, "IDEMPOTENCY_KEY_REQUIRED")
    identity = digest(
        [account.id, request.method, request.url.path, account.generation, key, ""]
    )
    if db.get(Dedup, identity) is None:
        return None
    entry, replay = operation(request, db, account, claims, revoked)
    if not replay:
        _integrity()
    return answer(entry)


@router.post(
    "/v1/research/sessions/{session_id}/report-artifact-uploads", status_code=201
)
def report_artifact_upload(request: Request, session_id: UUID, body: ArtifactRequest):
    from .main import access, answer, operation

    with access(request, allow_inactive=True) as (db, account, claims, revoked):
        check, authority, _ = _authorize(request, db, account, claims, session_id)
        if (
            body.session_id != check.id
            or body.study_id != check.study_id
            or body.artifact_kind != "source_lab_report"
            or body.media_type != "application/pdf"
            or body.consent_record_id != authority["consent_record_id"]
            or body.retention_policy_id != authority["retention_policy_id"]
        ):
            raise Problem(403, "RAW_RETENTION_UNAVAILABLE")
        entry, replay = operation(request, db, account, claims, revoked)
        if replay:
            return answer(entry)
        if body.size_bytes > MAX_REPORT_BYTES:
            raise Problem(413, "LIMIT_EXCEEDED")
        ensure_artifact_capacity(db, account.id, body.size_bytes)
        artifact_id = uid()
        row = Artifact(
            id=artifact_id,
            account_id=account.id,
            generation=account.generation,
            session_id=check.id,
            bucket=settings().artifact_bucket,
            key=f"quarantine/{account.id}/{account.generation}/{artifact_id}",
            sha256=body.sha256,
            size=body.size_bytes,
            media_type=body.media_type,
            kind="source_lab_report",
            expires=now() + 300,
            scope={**body.data(), "purpose": PURPOSE},
        )
        from .raw_retention import administrative_authority, attach_retention

        frozen = administrative_authority(db, account, check, body.retention_policy_id,
            PURPOSE, iso(check.created), operator_role="lab_report_revision")
        db.add(row)
        attach_retention(db, row, frozen)
        ticket = storage.upload_ticket(row)
        ticket["expires_at"] = iso(row.expires)
        return answer(entry, ticket, 201)


@router.post(
    "/v1/research/sessions/{session_id}/report-artifact-uploads/{artifact_id}/complete"
)
def report_artifact_complete(
    request: Request, session_id: UUID, artifact_id: UUID, body: CompleteArtifact
):
    from .main import access, answer, operation

    with access(request, allow_inactive=True) as (db, account, claims, revoked):
        check, authority, _ = _authorize(request, db, account, claims, session_id)
        row = _artifact(db, account, check, artifact_id, authority, purpose=True)
        replay = _replay_if_present(request, db, account, claims, revoked)
        if replay is not None:
            return replay
        _complete_matches(row, body)
        fingerprint = _ticket_fingerprint(row)
        detached = row
    version = (
        detached.version_id
        if detached.state == "verified"
        else storage.verify_artifact(detached)
    )
    if not isinstance(version, str) or not version or version == "null":
        raise Problem(403, "VERIFIED_REPORT_REQUIRED")
    with access(request, allow_inactive=True) as (db, account, claims, revoked):
        check, authority, _ = _authorize(request, db, account, claims, session_id)
        row = _artifact(db, account, check, artifact_id, authority, purpose=True)
        entry, replay = operation(request, db, account, claims, revoked)
        if replay:
            return answer(entry)
        _complete_matches(row, body)
        if _ticket_fingerprint(row) != fingerprint:
            raise Problem(409, "IMMUTABLE_ARTIFACT")
        if row.state == "verified" and row.version_id != version:
            raise Problem(409, "IMMUTABLE_ARTIFACT")
        row.version_id = version
        row.state = "verified"
        return answer(
            entry,
            {
                "artifact_id": row.id,
                "state": "verified",
                "sha256": row.sha256,
                "size_bytes": row.size,
                "version_id": version,
            },
        )


def _validate_replacements(snapshot, request, methods, prior_ids, *, current_time=None):
    sample = snapshot["sample"]
    if (
        request.sample_id != sample["sample_id"]
        or request.base_snapshot_sha256 != digest(snapshot)
        or sample["status"] == "not_collected"
        or sample["collected_at"] is None
    ):
        raise Problem(422, "REPORT_SAMPLE_MISMATCH")
    reported = _epoch(request.reported_at)
    if reported < _epoch(sample["collected_at"]) or (
        current_time is not None and reported > current_time + 60
    ):
        raise Problem(422, "REPORT_TIME_INVALID")
    seen_analytes, seen_ids, used = set(), set(), {}
    for reading in request.replacement_measurements:
        validate_measurement(reading)
        if (
            reading["source"] != "reference_lab"
            or reading["sample_id"] != sample["sample_id"]
            or reading["collected_at"] != sample["collected_at"]
        ):
            raise Problem(422, "REPORT_SAMPLE_MISMATCH")
        if reading["analyte"] in seen_analytes or reading["measurement_id"] in (
            prior_ids | seen_ids
        ):
            raise Problem(409, "REPORT_MEASUREMENT_CONFLICT")
        seen_analytes.add(reading["analyte"])
        seen_ids.add(reading["measurement_id"])
        if reading["qualifier"] == "not_measured":
            # Canonical validation requires null analytical identities/time/value.
            continue
        approval = methods.get(reading["method_id"])
        if (
            approval is None
            or reading["calibration_id"] not in approval["calibration_ids"]
            or reading["instrument_id"] not in approval["instrument_ids"]
        ):
            raise Problem(403, "REPORT_METHOD_UNAVAILABLE")
        if reading["measured_at"] is None or not (
            _epoch(sample["collected_at"]) <= _epoch(reading["measured_at"]) <= reported
        ):
            raise Problem(422, "REPORT_TIME_INVALID")
        used[reading["method_id"]] = {
            "calibration_ids": sorted(approval["calibration_ids"]),
            "instrument_ids": sorted(approval["instrument_ids"]),
        }
    return used


def _effective(previous, changed):
    by_analyte = {row["analyte"]: deepcopy(row) for row in previous}
    for row in changed:
        by_analyte[row["analyte"]] = deepcopy(row)
    return [by_analyte[key] for key in ANALYTES if key in by_analyte]


def _result(check, descriptor, revision_sha, effective, previous_result, result_id, at):
    invalid_report = any(row["qualifier"] == "invalid" for row in effective)
    state = (
        "invalid"
        if check.result["state"] == "invalid" or invalid_report
        else "inconclusive"
        if check.result["state"] == "inconclusive"
        else "measurement_only"
    )
    return ReportRevisionResult(
        schema_version="1.0.0",
        result_kind="administrative_report_result",
        result_id=result_id,
        session_id=check.id,
        revision_id=descriptor["revision_id"],
        revision_sha256=revision_sha,
        base_snapshot_sha256=check.snapshot_sha256,
        target_at=check.snapshot["target_at"],
        evaluated_at=at,
        state=state,
        reason_codes=sorted(
            set(
                check.result["reason_codes"]
                + [descriptor["report"]["reason_code"]]
                + (["INVALID_ANALYTICAL_REPORT"] if invalid_report else [])
            )
        ),
        provenance_summary=sorted(
            set(
                [row["source"] for row in effective]
                + [check.snapshot[k]["source"] for k in ("eyes", "cardiac", "task")]
            )
        ),
        replaces_result_id=previous_result,
        inference_available=False,
        probability=None,
        classification=None,
        model_id=None,
    ).data()


def _request_from_descriptor(snapshot, descriptor):
    report = descriptor["report"]
    return ReportRevisionRequest(
        schema_version="1.0.0",
        revision_id=descriptor["revision_id"],
        study_id=report["authorization"]["study_id"],
        sample_id=snapshot["sample"]["sample_id"],
        base_snapshot_sha256=descriptor["base_snapshot_sha256"],
        expected_previous_revision_id=descriptor["previous_revision_id"],
        expected_previous_revision_sha256=descriptor["previous_revision_sha256"],
        kind=report["kind"],
        reason_code=report["reason_code"],
        reported_at=report["reported_at"],
        source_report_artifact_id=report["source_report"]["artifact_id"],
        replacement_measurements=report["replacement_measurements"],
    )


def load_chain(db, account, check):
    """Validate stored companions without consulting mutable operator permissions."""
    snapshot = _base(db, account, check)
    rows = list(
        db.scalars(
            select(Record)
            .where(
                Record.account_id == account.id,
                Record.generation == account.generation,
                Record.parent_id == check.id,
                Record.kind.in_(["report_revision", "result_revision"]),
            )
            .order_by(Record.revision, Record.id)
            .limit(2 * MAX_REVISIONS + 1)
        )
    )
    if len(rows) > 2 * MAX_REVISIONS:
        _integrity()
    reports = [row for row in rows if row.kind == "report_revision"]
    results = {row.id: row for row in rows if row.kind == "result_revision"}
    if len(reports) > MAX_REVISIONS or len(results) != len(reports):
        _integrity()
    chain, previous_id, previous_sha = [], None, None
    previous_result = check.result["result_id"]
    effective = _effective(snapshot["saliva"], [])
    prior_ids = {row["measurement_id"] for row in snapshot["saliva"]}
    seen_results = set()
    try:
        for sequence, row in enumerate(reports, 1):
            if (
                not isinstance(row.body, dict)
                or set(row.body) != {"companion", "request_sha256"}
                or digest(row.body) != row.sha256
                or len(canonical(row.body)) > MAX_RECORD_BYTES
                or row.revision != sequence
            ):
                _integrity()
            companion = ReportRevisionCompanion.model_validate(
                row.body["companion"]
            ).data()
            descriptor = companion["descriptor"]
            authorization = descriptor["report"]["authorization"]
            if (
                row.id != rec_id(account, "report_revision", companion["revision_id"])
                or companion["sequence"] != sequence
                or companion["session_id"] != check.id
                or companion["data_generation"] != account.generation
                or descriptor["revision_id"] != companion["revision_id"]
                or descriptor["session_id"] != check.id
                or descriptor["data_generation"] != account.generation
                or descriptor["base_snapshot_sha256"] != check.snapshot_sha256
                or descriptor["base_evidence_sha256"] != check.evidence_sha256
                or descriptor["original_target_at"] != snapshot["target_at"]
                or descriptor["original_collected_at"]
                != snapshot["sample"]["collected_at"]
                or descriptor["original_capture_completed_at"]
                != snapshot["capture_completed_at"]
                or descriptor["previous_revision_id"] != previous_id
                or descriptor["previous_revision_sha256"] != previous_sha
                or digest(descriptor) != companion["revision_sha256"]
                or authorization["operator_account_ref"] != account.id
                or authorization["study_id"] != check.study_id
                or authorization["protocol_id"] != check.protocol_id
            ):
                _integrity()
            request = _request_from_descriptor(snapshot, descriptor)
            if digest(request.data()) != row.body["request_sha256"]:
                _integrity()
            used = _validate_replacements(
                snapshot, request, authorization["approved_lab_methods"], prior_ids
            )
            if used != authorization["approved_lab_methods"]:
                _integrity()
            effective = _effective(effective, request.replacement_measurements)
            result = companion["result"]
            expected_result = _result(
                check,
                descriptor,
                companion["revision_sha256"],
                effective,
                previous_result,
                result["result_id"],
                result["evaluated_at"],
            )
            result_key = rec_id(account, "result_revision", result["result_id"])
            persisted_result = results.get(result_key)
            if (
                companion["effective_measurements"] != effective
                or result != expected_result
                or result["evaluated_at"] != companion["accepted_at"]
                or result_key in seen_results
                or not persisted_result
                or persisted_result.revision != sequence
                or persisted_result.body != result
                or persisted_result.sha256 != digest(result)
                or companion["result_sha256"] != digest(result)
            ):
                _integrity()
            seen_results.add(result_key)
            chain.append(companion)
            previous_id, previous_sha = (
                companion["revision_id"],
                companion["revision_sha256"],
            )
            previous_result = result["result_id"]
            prior_ids.update(
                reading["measurement_id"]
                for reading in request.replacement_measurements
            )
    except Problem as error:
        if error.code == "REPORT_REVISION_INTEGRITY":
            raise
        _integrity()
    except Exception:
        # Corrupted health records never reach a raw exception or partial view.
        _integrity()
    return chain


def freeze_head(db, account, check):
    # Ordinary export can include an admitted numeric result without granting
    # administrative revision eligibility. Existing companions still require
    # the full, narrower chain validator, including orphan result companions.
    _validated_base(db, account, check)
    companion = db.scalar(
        select(Record.id).where(
            Record.account_id == account.id,
            Record.generation == account.generation,
            Record.parent_id == check.id,
            Record.kind.in_(["report_revision", "result_revision"]),
        ).limit(1)
    )
    if companion is None:
        return {"revision_id": None, "revision_sha256": None}
    chain = load_chain(db, account, check)
    return {
        "revision_id": chain[-1]["revision_id"] if chain else None,
        "revision_sha256": chain[-1]["revision_sha256"] if chain else None,
    }


def export_records(db, account, check, head):
    if not isinstance(head, dict) or set(head) != {"revision_id", "revision_sha256"}:
        _integrity()
    if (head["revision_id"] is None) != (head["revision_sha256"] is None):
        _integrity()
    chain = []
    if head["revision_id"] is not None:
        current = load_chain(db, account, check)
        for value in current:
            chain.append(value)
            if value["revision_id"] == head["revision_id"]:
                if value["revision_sha256"] != head["revision_sha256"]:
                    _integrity()
                break
        else:
            _integrity()
    files, items = {}, []
    for value in chain:
        path = f"report-revisions/{check.id}/{value['revision_id']}.json"
        raw = canonical(value)
        if len(raw) > MAX_RECORD_BYTES:
            raise Problem(413, "EXPORT_TOO_LARGE")
        files[path] = raw
        items.append(
            {
                "revision_id": value["revision_id"],
                "sequence": value["sequence"],
                "revision_sha256": value["revision_sha256"],
                "result_id": value["result"]["result_id"],
                "result_sha256": value["result_sha256"],
                "path": path,
                "sha256": digest(value),
                "size_bytes": len(raw),
            }
        )
    index = ReportRevisionIndex(
        schema_version="1.0.0",
        session_id=check.id,
        data_generation=account.generation,
        base_snapshot_sha256=check.snapshot_sha256,
        items=items,
    ).data()
    if len(canonical(index)) > MAX_INDEX_BYTES:
        raise Problem(413, "EXPORT_TOO_LARGE")
    return index, files


@router.post(
    "/v1/research/sessions/{session_id}/report-revisions",
    status_code=201,
    response_model=ReportRevisionCompanion,
)
def report_revision_create(
    request: Request, session_id: UUID, body: ReportRevisionRequest
):
    from .main import access, answer, operation

    with access(request, allow_inactive=True) as (db, account, claims, revoked):
        check, authority, methods = _authorize(request, db, account, claims, session_id)
        if body.study_id != check.study_id:
            raise Problem(403, "CAPABILITY_DENIED")
        artifact = _artifact(
            db, account, check, body.source_report_artifact_id, authority, verified=True
        )
        # Validate current authority even for a retained same-key or stable-ID replay.
        used = _validate_replacements(
            check.snapshot, body, methods, set(), current_time=now()
        )
        entry, replay = operation(request, db, account, claims, revoked)
        if replay:
            return answer(entry)
        chain = load_chain(db, account, check)
        request_sha = digest(body.data())
        existing = record(db, account, "report_revision", body.revision_id)
        if existing:
            if (
                existing.parent_id != check.id
                or existing.body.get("request_sha256") != request_sha
            ):
                raise Problem(409, "REPORT_REVISION_CONFLICT")
            match = next(
                (x for x in chain if x["revision_id"] == body.revision_id), None
            )
            if not match:
                _integrity()
            return answer(entry, match, 201)
        latest = chain[-1] if chain else None
        if (
            body.expected_previous_revision_id,
            body.expected_previous_revision_sha256,
        ) != (
            latest["revision_id"] if latest else None,
            latest["revision_sha256"] if latest else None,
        ):
            raise Problem(409, "REPORT_REVISION_CONFLICT", revision=len(chain))
        if len(chain) >= MAX_REVISIONS:
            raise Problem(413, "REPORT_REVISION_LIMIT")
        prior_ids = {x["measurement_id"] for x in check.snapshot["saliva"]}
        for previous in chain:
            prior_ids.update(
                x["measurement_id"]
                for x in previous["descriptor"]["report"]["replacement_measurements"]
            )
        _validate_replacements(
            check.snapshot, body, methods, prior_ids, current_time=now()
        )
        authority["approved_lab_methods"] = used
        descriptor = ReportDescriptor(
            schema_version="1.0.0",
            revision_id=body.revision_id,
            session_id=check.id,
            data_generation=account.generation,
            base_snapshot_sha256=check.snapshot_sha256,
            base_evidence_sha256=check.evidence_sha256,
            previous_revision_id=body.expected_previous_revision_id,
            previous_revision_sha256=body.expected_previous_revision_sha256,
            original_target_at=check.snapshot["target_at"],
            original_collected_at=check.snapshot["sample"]["collected_at"],
            original_capture_completed_at=check.snapshot["capture_completed_at"],
            report={
                "kind": body.kind,
                "reason_code": body.reason_code,
                "reported_at": body.reported_at,
                "replacement_measurements": body.replacement_measurements,
                "source_report": {
                    "artifact_id": artifact.id,
                    "version_id": artifact.version_id,
                    "sha256": artifact.sha256,
                    "media_type": artifact.media_type,
                    "size_bytes": artifact.size,
                },
                "authorization": authority,
            },
        ).data()
        revision_sha = digest(descriptor)
        effective = _effective(
            latest["effective_measurements"] if latest else check.snapshot["saliva"],
            body.replacement_measurements,
        )
        accepted = iso()
        result = _result(
            check,
            descriptor,
            revision_sha,
            effective,
            latest["result"]["result_id"] if latest else check.result["result_id"],
            uid(),
            accepted,
        )
        companion = ReportRevisionCompanion(
            schema_version="1.0.0",
            record_type="administrative_report_revision",
            revision_id=body.revision_id,
            session_id=check.id,
            data_generation=account.generation,
            sequence=len(chain) + 1,
            accepted_at=accepted,
            descriptor=descriptor,
            revision_sha256=revision_sha,
            effective_measurements=effective,
            result=result,
            result_sha256=digest(result),
        ).data()
        stored = {"companion": companion, "request_sha256": request_sha}
        if len(canonical(stored)) > MAX_RECORD_BYTES:
            raise Problem(413, "REPORT_REVISION_LIMIT")
        save_record(
            db,
            account,
            "report_revision",
            body.revision_id,
            stored,
            check.id,
            len(chain) + 1,
        )
        save_record(
            db,
            account,
            "result_revision",
            result["result_id"],
            result,
            check.id,
            len(chain) + 1,
        )
        return answer(entry, companion, 201)


@router.get(
    "/v1/sessions/{session_id}/report-revisions", response_model=ReportRevisionList
)
def report_revision_list(request: Request, session_id: UUID):
    from .main import access

    with access(request) as (db, account, claims, revoked):
        check = owned_check(db, account, session_id)
        chain = load_chain(db, account, check)
        return {
            "schema_version": "1.0.0",
            "session_id": check.id,
            "data_generation": account.generation,
            "base_snapshot_sha256": check.snapshot_sha256,
            "base_result_id": check.result["result_id"],
            "original_target_at": check.snapshot["target_at"],
            "original_collected_at": check.snapshot["sample"]["collected_at"],
            "original_capture_completed_at": check.snapshot["capture_completed_at"],
            "latest_revision_id": chain[-1]["revision_id"] if chain else None,
            "items": [
                {
                    "revision_id": x["revision_id"],
                    "revision_sha256": x["revision_sha256"],
                    "sequence": x["sequence"],
                    "kind": x["descriptor"]["report"]["kind"],
                    "reported_at": x["descriptor"]["report"]["reported_at"],
                    "accepted_at": x["accepted_at"],
                    "previous_revision_id": chain[i - 1]["revision_id"] if i else None,
                    "next_revision_id": chain[i + 1]["revision_id"]
                    if i + 1 < len(chain)
                    else None,
                    "result_id": x["result"]["result_id"],
                    "result_state": x["result"]["state"],
                }
                for i, x in enumerate(chain)
            ],
        }


@router.get(
    "/v1/sessions/{session_id}/report-revisions/{revision_id}",
    response_model=ReportRevisionDetail,
)
def report_revision_detail(request: Request, session_id: UUID, revision_id: UUID):
    from .main import access

    with access(request) as (db, account, claims, revoked):
        check = owned_check(db, account, session_id)
        chain = load_chain(db, account, check)
        for i, value in enumerate(chain):
            if value["revision_id"] == revision_id:
                return {
                    "schema_version": "1.0.0",
                    "session_id": check.id,
                    "data_generation": account.generation,
                    "revision": value,
                    "previous_revision_id": chain[i - 1]["revision_id"] if i else None,
                    "next_revision_id": chain[i + 1]["revision_id"]
                    if i + 1 < len(chain)
                    else None,
                }
        raise Problem(404, "NOT_FOUND")
