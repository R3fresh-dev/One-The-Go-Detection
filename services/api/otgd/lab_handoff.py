"""Delegated laboratory custody; no participant or operator approval is seeded.

The authenticated staff actor stays separate from the participant who owns every
specimen, report and analytical record. Callers re-admit these helpers before
idempotency replay and after storage I/O. Cached staff receipts contain no health
payload or bearer upload URL.
"""

from copy import deepcopy
import base64
import hashlib
import math
from typing import Annotated, Literal

from pydantic import Field
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from . import storage
from .canonical import canonical, digest
from .config import settings
from .db import Account, Artifact, Audit, Record, iso, now, uid
from .domain import (
    NOTICE_SHA, owned_check, record, require_draft, save_record,
    validate_component, validate_measurement,
)
from .dto import CaptureAttempt, DTO, Name, SHA, UUID
from .errors import Problem
from .operator_governance import active_body, acquisition_context, capture_configuration
from .raw_retention import administrative_authority, assert_artifact_admitted, attach_retention

PURPOSE = "laboratory_collection_report"
MAX_REPORT_BYTES = 5 * 1024 * 1024
MAX_IMPORT_BYTES = 512 * 1024


class LabSourceRequest(DTO):
    account_ref: UUID
    data_generation: Annotated[int, Field(ge=1, le=9007199254740991)]
    study_id: Name
    session_id: UUID
    sample_id: UUID
    collection_attempt_id: UUID
    sha256: SHA
    size_bytes: Annotated[int, Field(gt=0, le=MAX_REPORT_BYTES)]
    media_type: Literal["application/pdf"]


def delegated_target(db, operator, session_id, study_id, account_ref, data_generation):
    """NOWAIT prevents opposing staff/subject lock order from deadlocking."""
    if (operator.state != "active" or operator.notice != NOTICE_SHA
        or operator.id == account_ref):
        raise Problem(403, "DELEGATED_LAB_OPERATOR_REQUIRED")
    if type(data_generation) is not int or not 1 <= data_generation <= 9007199254740991:
        raise Problem(403, "LAB_TARGET_SCOPE_REQUIRED")
    role = active_body(db, "role", operator.id)
    if (role.get("account_ref") != operator.id or "lab_import" not in role["roles"]
        or study_id not in role["study_ids"]):
        raise Problem(403, "LAB_IMPORT_ROLE_REQUIRED")
    try:
        target = db.scalar(select(Account).where(Account.id == account_ref)
            .with_for_update(nowait=True).execution_options(populate_existing=True))
    except OperationalError:
        raise Problem(503, "LAB_TARGET_BUSY", retryable=True) from None
    if (not target or target.state != "active" or target.generation != data_generation
        or target.notice != NOTICE_SHA):
        raise Problem(403, "LAB_TARGET_UNAVAILABLE")
    check = owned_check(db, target, session_id)
    require_draft(check)
    if check.study_id != study_id or check.mode not in ("analytical", "controlled_research"):
        raise Problem(403, "LAB_TARGET_SCOPE_MISMATCH")
    config = capture_configuration(db, target, check, "saliva")
    if (config["software_adapter_id"] != "reference_lab_import_v1"
        or not config.get("lab_methods")
        or config.get("participant_protocol", {}).get("kind") != "reference_lab"):
        raise Problem(403, "REFERENCE_LAB_COLLECTION_REQUIRED")
    acquisition_context(db, target, check, config)
    return target, check, config


def collection_record(db, target, check, sample_id, collection_attempt_id):
    row = record(db, target, "collection", sample_id)
    if (not row or row.parent_id != check.id or row.sha256 != digest(row.body)
        or row.body.get("session_id") != check.id
        or row.body.get("state") != "pending_lab"
        or row.body.get("request", {}).get("sample_id") != sample_id
        or row.body.get("request", {}).get("attempt_id") != collection_attempt_id
        or row.body.get("attempt", {}).get("attempt_id") != collection_attempt_id
        or row.body.get("attempt", {}).get("record_id") != sample_id
        or row.body.get("projection", {}).get("sample", {}).get("sample_id") != sample_id
        or row.body.get("projection", {}).get("saliva") != []):
        raise Problem(403, "OWNED_COLLECTION_RECEIPT_REQUIRED")
    from .participant_acquisition import checked_collection

    checked_collection(row)
    original = record(db, target, "attempt", collection_attempt_id)
    if (not original or original.parent_id != check.id
        or original.sha256 != digest(original.body)
        or original.body != row.body["attempt"]
        or original.revision != row.body["attempt_revision"]
        or original.sha256 != row.body["attempt_sha256"]):
        raise Problem(503, "COLLECTION_INTEGRITY_FAILED")
    abandoned = record(db, target, "collection_abandon", sample_id)
    if abandoned:
        if (abandoned.parent_id != check.id or abandoned.sha256 != digest(abandoned.body)
            or abandoned.body.get("sample_id") != sample_id
            or abandoned.body.get("collection_sha256") != row.sha256):
            raise Problem(503, "COLLECTION_ABANDONMENT_INTEGRITY")
        raise Problem(410, "LAB_ANALYSIS_ABANDONED")
    return row


def _collection_scope(db, target, check, config, sample_id, attempt_id):
    row = collection_record(db, target, check, sample_id, attempt_id)
    receipt = row.body
    protocol = config["participant_protocol"]
    instruction = receipt.get("instruction_receipt", {})
    accepted = record(db, target, "instruction_receipt", instruction.get("instruction_receipt_id", ""))
    consent = record(db, target, "consent", check.study_id)
    if (receipt.get("configuration_version") != config["version"]
        or receipt.get("configuration_submitted_sha256") != digest(config)
        or receipt.get("participant_protocol_sha256") != digest(protocol)
        or not accepted or accepted.parent_id != check.id
        or accepted.sha256 != digest(accepted.body) or accepted.body != instruction
        or instruction.get("attempt_id") != attempt_id
        or instruction.get("configuration_submitted_sha256") != digest(config)
        or not consent or instruction.get("consent_record_id") != consent.body.get("consent_record_id")
        or receipt["projection"]["sample"]["collection_method_id"] not in config["material"]["collection_method_ids"]):
        raise Problem(403, "CURRENT_COLLECTION_AUTHORITY_REQUIRED")
    return row


def create_source(db, operator, body):
    target, check, config = delegated_target(db, operator, body.session_id,
        body.study_id, body.account_ref, body.data_generation)
    collection = _collection_scope(db, target, check, config, body.sample_id, body.collection_attempt_id)
    from .report_revisions import ensure_artifact_capacity

    ensure_artifact_capacity(db, target.id, body.size_bytes)
    frozen = administrative_authority(db, target, check, config["retention_policy_id"],
        PURPOSE, iso(check.created), operator_role="lab_importer")
    id = uid()
    scope = {**body.data(), "operator_account_ref": operator.id, "purpose": PURPOSE,
        "artifact_kind": "source_lab_report", "consent_record_id": frozen["consent_record_id"],
        "retention_policy_id": config["retention_policy_id"],
        "configuration_id": config["configuration_id"], "configuration_version": config["version"],
        "configuration_submitted_sha256": digest(config), "collection_sha256": collection.sha256}
    artifact = Artifact(id=id, account_id=target.id, generation=target.generation,
        session_id=check.id, bucket=settings().artifact_bucket,
        key=f"quarantine/{target.id}/{target.generation}/{id}",
        sha256=body.sha256, size=body.size_bytes, media_type=body.media_type,
        kind="source_lab_report", state="quarantine", expires=now() + 300, scope=scope)
    db.add(artifact)
    attach_retention(db, artifact, frozen)
    return artifact, {"artifact_id": artifact.id, "state": "upload_pending", "expires_at": iso(artifact.expires)}


def source_target(db, operator, artifact_id):
    # This first read supplies only the target lock identity. Re-read the artifact
    # after taking that lock so a sweep/deletion cannot leave stale admission.
    original = db.get(Artifact, artifact_id)
    if not original or original.scope.get("operator_account_ref") != operator.id:
        raise Problem(404, "NOT_FOUND")
    scope = original.scope
    target, check, config = delegated_target(db, operator, original.session_id,
        scope.get("study_id"), original.account_id, original.generation)
    row = db.scalar(select(Artifact).where(Artifact.id == artifact_id)
        .with_for_update().execution_options(populate_existing=True))
    if not row:
        raise Problem(404, "NOT_FOUND")
    collection = _collection_scope(db, target, check, config,
        row.scope.get("sample_id"), row.scope.get("collection_attempt_id"))
    consent = record(db, target, "consent", check.study_id)
    if (row.account_id != target.id or row.generation != target.generation
        or row.session_id != check.id or row.kind != "source_lab_report"
        or row.media_type != "application/pdf" or not 0 < row.size <= MAX_REPORT_BYTES
        or row.scope.get("operator_account_ref") != operator.id
        or row.scope.get("purpose") != PURPOSE
        or row.scope.get("configuration_id") != config["configuration_id"]
        or row.scope.get("configuration_version") != config["version"]
        or row.scope.get("configuration_submitted_sha256") != digest(config)
        or row.scope.get("collection_sha256") != collection.sha256
        or row.scope.get("consent_record_id") != consent.body["consent_record_id"]
        or row.scope.get("retention_policy_id") != config["retention_policy_id"]):
        raise Problem(403, "LAB_REPORT_SCOPE_MISMATCH")
    assert_artifact_admitted(db, target, row)
    if row.state == "quarantine" and row.expires <= now():
        raise Problem(410, "LAB_REPORT_UPLOAD_EXPIRED")
    return target, check, row, config


def source_ticket(artifact):
    """Derive a bearer only after admission; replay cannot extend its write TTL."""
    seconds = min(300, math.floor(artifact.expires - now()))
    if artifact.state != "quarantine" or seconds <= 0:
        raise Problem(410, "LAB_REPORT_UPLOAD_EXPIRED")
    checksum = base64.b64encode(bytes.fromhex(artifact.sha256)).decode()
    params = dict(Bucket=artifact.bucket, Key=artifact.key, ContentLength=artifact.size,
        ContentType=artifact.media_type, ChecksumSHA256=checksum, IfNoneMatch="*", **storage.encryption())
    url = storage.client("s3", public=True).generate_presigned_url("put_object",
        Params=params, ExpiresIn=seconds, HttpMethod="PUT")
    headers = {"Content-Length": str(artifact.size), "Content-Type": artifact.media_type,
        "x-amz-checksum-sha256": checksum, "If-None-Match": "*",
        "x-amz-server-side-encryption": params["ServerSideEncryption"]}
    if "SSEKMSKeyId" in params:
        headers["x-amz-server-side-encryption-aws-kms-key-id"] = params["SSEKMSKeyId"]
    return {"artifact_id": artifact.id, "method": "PUT", "upload_url": url,
        "required_headers": headers, "expires_in_seconds": seconds, "expires_at": iso(artifact.expires)}


def source_fingerprint(row):
    return digest([row.id, row.account_id, row.generation, row.session_id, row.bucket,
        row.key, row.sha256, row.size, row.media_type, row.expires, row.scope])


def verify_source(artifact):
    """Call without subject/registry locks, then re-admit before accepting."""
    if not 0 < artifact.size <= MAX_REPORT_BYTES:
        raise Problem(413, "LIMIT_EXCEEDED")
    s3 = storage.client("s3")
    version = artifact.version_id if artifact.state == "verified" else s3.head_object(
        Bucket=artifact.bucket, Key=artifact.key).get("VersionId")
    if not isinstance(version, str) or not 1 <= len(version) <= 1024 or version == "null":
        raise Problem(503, "VERSIONING_REQUIRED")
    obj = s3.get_object(Bucket=artifact.bucket, Key=artifact.key, VersionId=version)
    try:
        if (obj.get("VersionId") != version or obj.get("ContentLength") != artifact.size
            or obj.get("ContentType") != "application/pdf"):
            raise Problem(422, "ARTIFACT_MISMATCH")
        data = obj["Body"].read(artifact.size + 1)
    finally:
        obj["Body"].close()
    if len(data) != artifact.size or hashlib.sha256(data).hexdigest() != artifact.sha256:
        raise Problem(422, "ARTIFACT_MISMATCH")
    if not data.startswith(b"%PDF-"):
        raise Problem(422, "MEDIA_MISMATCH")
    return version


def accept_source(db, operator, artifact_id, version, *, fingerprint):
    _, _, row, _ = source_target(db, operator, artifact_id)
    if not isinstance(version, str) or not 1 <= len(version) <= 1024 or version == "null":
        raise Problem(503, "VERSIONING_REQUIRED")
    if (fingerprint != source_fingerprint(row)
        or row.state == "verified" and row.version_id != version):
        raise Problem(409, "IMMUTABLE_ARTIFACT")
    row.version_id, row.state = version, "verified"
    return {"artifact_id": row.id, "state": "verified"}


def _measurements(db, operator, config, sample, readings):
    if not 1 <= len(readings) <= 3:
        raise Problem(422, "LAB_MEASUREMENTS_REQUIRED")
    seen, ids = set(), set()
    material = config["material"]
    for value in readings:
        validate_measurement(value)
        if (value["source"] != "reference_lab" or value["sample_id"] != sample["sample_id"]
            or value["collected_at"] != sample["collected_at"]):
            raise Problem(422, "LAB_SAMPLE_MISMATCH")
        if value["measurement_id"] in ids or value["analyte"] in seen:
            raise Problem(409, "LAB_MEASUREMENT_CONFLICT")
        ids.add(value["measurement_id"])
        seen.add(value["analyte"])
        if value["qualifier"] == "not_measured":
            continue
        if sample["status"] != "valid" and value["qualifier"] != "invalid":
            raise Problem(422, "INVALID_COLLECTION_FOR_ANALYSIS")
        approval = config["lab_methods"].get(value["method_id"])
        if (not approval or value["calibration_id"] not in approval["calibration_ids"]
            or value["instrument_id"] not in approval["instrument_ids"]
            or value["operator_ref"] != operator.id):
            raise Problem(403, "LAB_METHOD_SCOPE_MISMATCH")
        method = active_body(db, "method", value["method_id"])
        active_body(db, "calibration", value["calibration_id"])
        if (sample["collection_method_id"] not in method["collection_method_ids"]
            or value["instrument_id"] not in method["instrument_ids"]
            or value["assay_basis"] != "unspecified" and value["assay_basis"] not in method["assay_bases"]
            or any(value[key] != "unspecified" and value[key] not in material[allowed]
                for key, allowed in (("assay_basis", "assay_bases"),
                    ("concentration_basis", "concentration_bases"), ("correction_status", "correction_statuses")))):
            raise Problem(403, "LAB_METHOD_SCOPE_MISMATCH")
        from .participant_acquisition import epoch
        collected, measured = epoch(sample["collected_at"]), epoch(value["measured_at"])
        if (not collected <= measured <= now() + 5
            or measured - collected > config["participant_protocol"]["maximum_analysis_delay_seconds"]):
            raise Problem(422, "LAB_ANALYSIS_TIME_INVALID")


def import_scope(db, operator, body):
    """Run before replay as well as new import; a receipt is not new authority."""
    target, check, config = delegated_target(db, operator, body.session_id,
        body.study_id, body.account_ref, body.data_generation)
    collection = _collection_scope(db, target, check, config, body.sample_id, body.collection_attempt_id)
    artifact_target, _, report, _ = source_target(db, operator, body.source_report_artifact_id)
    if (artifact_target.id != target.id or report.scope["sample_id"] != body.sample_id
        or report.scope["collection_attempt_id"] != body.collection_attempt_id
        or report.state != "verified" or not report.version_id or report.version_id == "null"):
        raise Problem(403, "VERIFIED_REPORT_REQUIRED")
    _measurements(db, operator, config, collection.body["projection"]["sample"], body.measurements)
    return target, check, config, collection, report


def import_measurements(db, operator, body):
    target, check, config, collection, report = import_scope(db, operator, body)
    if db.scalar(select(Record.id).where(Record.account_id == target.id,
        Record.generation == target.generation, Record.kind == "lab_import",
        Record.parent_id == check.id,
        Record.body["collection_attempt_id"].as_string() == body.collection_attempt_id).limit(1)):
        raise Problem(409, "LAB_IMPORT_ALREADY_ACCEPTED")
    sample = collection.body["projection"]["sample"]
    id, analysis_id = uid(), uid()
    attempt = deepcopy(collection.body["attempt"])
    attempt.update(attempt_id=analysis_id, supersedes_attempt_id=body.collection_attempt_id,
        status=sample["status"],
        source="reference_lab")
    attempt["component_metadata"].update(projection={"sample": deepcopy(sample), "saliva": deepcopy(body.measurements)},
        lab_import_id=id, collection_attempt_id=body.collection_attempt_id,
        collection_receipt_id=collection.body["collection_receipt_id"])
    attempt["artifact_refs"] = [report.id]
    if attempt["status"] == "invalid" and not attempt["quality_flags"]:
        attempt["quality_flags"] = ["LABORATORY_ANALYSIS_INVALID"]
    CaptureAttempt.model_validate(attempt)
    validate_component(attempt)
    value = {**body.data(), "import_id": id, "operator_account_ref": operator.id,
        "accepted_at": iso(), "configuration_submitted_sha256": digest(config),
        "collection_receipt_id": collection.body["collection_receipt_id"],
        "source_report": {"artifact_id": report.id, "version_id": report.version_id,
            "sha256": report.sha256, "size_bytes": report.size, "media_type": report.media_type},
        "analysis_attempt_id": analysis_id}
    if len(canonical(value)) > MAX_IMPORT_BYTES or len(canonical(attempt)) > MAX_IMPORT_BYTES:
        raise Problem(413, "LIMIT_EXCEEDED")
    save_record(db, target, "lab_import", id, value, check.id)
    save_record(db, target, "attempt", analysis_id, attempt, check.id)
    db.add(Audit(account_id=operator.id, generation=operator.generation,
        action=f"delegated_lab_import:{target.id}:{id}", request_id=uid()))
    db.add(Audit(account_id=target.id, generation=target.generation,
        action=f"delegated_lab_import_by:{operator.id}:{id}", request_id=uid()))
    return {"import_id": id, "analysis_attempt_id": analysis_id, "state": "verified_import"}
