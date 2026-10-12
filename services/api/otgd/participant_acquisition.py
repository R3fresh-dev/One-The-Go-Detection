"""Owned approved instructions and specimen custody, never participant assays."""

import hashlib
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from .canonical import digest
from .db import iso, now, uid
from .dto import CaptureAttempt, DTO, Name, SHA, UTC, UUID
from .errors import Problem

Text = Annotated[str, Field(min_length=1, max_length=8192)]


class Confirmation(DTO):
    id: Annotated[str, Field(pattern="^[a-z][a-z0-9_]{0,63}$")]
    text: Annotated[str, Field(min_length=1, max_length=1024)]


class Setup(DTO):
    id: Name
    description: Annotated[str, Field(min_length=1, max_length=2048)]
    power_state: Name
    charging_state: Name
    cable_state: Name
    contact_or_lead_configuration: Name


class InstructionDocument(DTO):
    schema_version: Literal["1.0.0"]
    instruction_id: Name
    version: Name
    text: Text
    sha256: SHA
    required_confirmations: Annotated[list[Confirmation], Field(min_length=1, max_length=8)]
    maximum_acknowledgment_age_seconds: Annotated[int, Field(ge=1, le=300)]

    @model_validator(mode="after")
    def content(self):
        if len(self.text.encode()) > 16384 or hashlib.sha256(self.text.encode()).hexdigest() != self.sha256:
            raise ValueError("Instruction text must match its exact bounded UTF-8 digest")
        ids = [item.id for item in self.required_confirmations]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate required confirmation")
        return self


class CardiacProtocol(InstructionDocument):
    kind: Literal["cardiac"]
    operating_scope: Literal["engineering_bench", "human_participant"]
    operating_state_verifier: Literal["participant_declaration_only", "device_attested_v1"]
    rest_duration_seconds: Annotated[int, Field(ge=0, le=3600)]
    posture_instruction: Annotated[str, Field(min_length=1, max_length=2048)]
    activity_instruction: Annotated[str, Field(min_length=1, max_length=2048)]
    contact_instruction: Annotated[str, Field(min_length=1, max_length=2048)]
    isolation_instruction: Annotated[str, Field(min_length=1, max_length=2048)]
    permitted_setups: Annotated[list[Setup], Field(min_length=1, max_length=16)]

    @model_validator(mode="after")
    def setup_identity(self):
        if len({item.id for item in self.permitted_setups}) != len(self.permitted_setups):
            raise ValueError("Duplicate permitted whole-system setup")
        if not {"rest_completed", "posture_confirmed", "activity_confirmed", "contact_confirmed", "isolation_confirmed"}.issubset({item.id for item in self.required_confirmations}):
            raise ValueError("Cardiac instructions require exact rest/posture/activity/contact/isolation confirmations")
        return self


class CollectionMethod(DTO):
    id: Name
    version: Name
    instructions: Annotated[str, Field(min_length=1, max_length=4096)]
    saliva_volume_required: bool
    buffer_volume_required: bool
    dilution_factor_required: bool
    dilution_definition: Literal["total_mixture_over_saliva", "undiluted", "fixed_factor"] | None
    fixed_dilution_factor: Annotated[float, Field(ge=1, le=100000)] | None
    saliva_volume_min_ml: Annotated[float, Field(ge=0, le=100)] | None
    saliva_volume_max_ml: Annotated[float, Field(gt=0, le=100)] | None
    buffer_volume_min_ml: Annotated[float, Field(ge=0, le=100)] | None
    buffer_volume_max_ml: Annotated[float, Field(gt=0, le=100)] | None
    collector_lot_required: bool
    container_required: bool
    expiry_required: bool
    permitted_containers: Annotated[list[Name], Field(max_length=32)]
    required_handling_events: Annotated[list[Name], Field(max_length=16)]
    permitted_null_reasons: Annotated[list[Literal["unknown", "declined", "not_applicable"]], Field(min_length=1, max_length=3)]

    @model_validator(mode="after")
    def coherent(self):
        for low, high in ((self.saliva_volume_min_ml, self.saliva_volume_max_ml), (self.buffer_volume_min_ml, self.buffer_volume_max_ml)):
            if (low is None) != (high is None) or low is not None and low > high:
                raise ValueError("Collection quantity limits must be complete and ordered")
        if (self.dilution_definition == "fixed_factor") != (self.fixed_dilution_factor is not None):
            raise ValueError("Fixed dilution convention needs its exact approved factor")
        if self.dilution_factor_required and self.dilution_definition is None:
            raise ValueError("A dilution factor requires its approved convention")
        for items in (self.permitted_containers, self.required_handling_events, self.permitted_null_reasons):
            if len(items) != len(set(items)):
                raise ValueError("Duplicate collection rule identity")
        if self.container_required and not self.permitted_containers:
            raise ValueError("Required container needs an approved inventory")
        return self


class LaboratoryProtocol(InstructionDocument):
    kind: Literal["reference_lab"]
    methods: Annotated[list[CollectionMethod], Field(min_length=1, max_length=16)]
    maximum_collection_submission_delay_seconds: Annotated[int, Field(ge=1, le=3600)]
    maximum_analysis_delay_seconds: Annotated[int, Field(ge=1, le=604800)]

    @model_validator(mode="after")
    def method_identity(self):
        if len({item.id for item in self.methods}) != len(self.methods):
            raise ValueError("Duplicate approved collection method")
        return self


ParticipantProtocol = Annotated[CardiacProtocol | LaboratoryProtocol, Field(discriminator="kind")]


class InstructionAcknowledgment(DTO):
    attempt_id: UUID
    configuration_id: Name
    configuration_version: Name
    configuration_hash: SHA
    configuration_submitted_sha256: SHA
    participant_protocol_sha256: SHA
    acknowledged_at: UTC
    confirmed: Literal[True]
    confirmations: Annotated[list[Name], Field(min_length=1, max_length=8)]
    setup_id: Name | None
    rest_started_at: UTC | None
    collection_method_id: Name | None
    collection_method_version: Name | None

    @field_validator("confirmed", mode="before")
    @classmethod
    def explicit_confirmation(cls, value):
        if value is not True:
            raise ValueError("Explicit confirmation is required")
        return value


class InstructionReceipt(InstructionAcknowledgment):
    instruction_receipt_id: UUID
    session_id: UUID
    consent_record_id: UUID
    accepted_at: UTC


class HandlingEvent(DTO):
    event: Name
    occurred_at: UTC
    temperature_c: Annotated[float, Field(ge=-273.15, le=100)] | None
    duration_min: Annotated[float, Field(ge=0, le=525600)] | None


class CollectionRequest(DTO):
    attempt_id: UUID
    sample_id: UUID
    instruction_receipt_id: UUID
    collection_method_id: Name
    collection_method_version: Name
    collected_at: UTC
    status: Literal["valid", "invalid"]
    quality_flags: Annotated[list[Name], Field(max_length=64)]
    saliva_volume_ml: Annotated[float, Field(gt=0, le=100)] | None
    buffer_volume_ml: Annotated[float, Field(ge=0, le=100)] | None
    dilution_factor: Annotated[float, Field(gt=0, le=100000)] | None
    collector_id: Name | None
    collector_lot: Name | None
    container_id: Name | None
    cartridge_lot: Name | None
    cartridge_expiry: UTC | None
    missing_reasons: Annotated[dict[Literal["saliva_volume_ml", "buffer_volume_ml", "dilution_factor", "collector_id", "collector_lot", "container_id", "cartridge_lot", "cartridge_expiry"], Literal["unknown", "declined", "not_applicable"]], Field(max_length=8)]
    storage_handling_events: Annotated[list[HandlingEvent], Field(max_length=64)]

    @model_validator(mode="after")
    def explicit_unknowns(self):
        fields = ("saliva_volume_ml", "buffer_volume_ml", "dilution_factor", "collector_id", "collector_lot", "container_id", "cartridge_lot", "cartridge_expiry")
        if set(self.missing_reasons) != {key for key in fields if getattr(self, key) is None}:
            raise ValueError("Missing collection quantities and identities need exact null reasons")
        if self.status == "invalid" and not self.quality_flags:
            raise ValueError("Invalid collection needs an explicit reason")
        return self


class CollectionReceipt(DTO):
    collection_receipt_id: UUID
    session_id: UUID
    request: CollectionRequest
    state: Literal["pending_lab", "invalid_collection"]
    accepted_at: UTC
    authorization_id: UUID
    configuration_submitted_sha256: SHA
    configuration_version: Name
    participant_protocol_sha256: SHA
    instruction_receipt: InstructionReceipt
    projection: dict
    attempt: CaptureAttempt
    attempt_revision: Annotated[int, Field(ge=1, le=128)]
    attempt_sha256: SHA

    @model_validator(mode="after")
    def lineage(self):
        if (self.attempt_sha256 != digest(self.attempt.data())
            or self.attempt.session_id != self.session_id or self.attempt.attempt_id != self.request.attempt_id
            or self.attempt.record_id != self.request.sample_id or self.attempt.component != "saliva"
            or self.attempt.component_metadata.get("projection") != self.projection
            or self.attempt.component_metadata.get("instruction_receipt") != self.instruction_receipt.data()
            or self.attempt.component_metadata.get("collection_request_sha256") != digest(self.request.data())
            or self.projection.get("saliva") != []):
            raise ValueError("Immutable collection evidence does not match its receipt")
        return self


def checked_collection(row):
    from pydantic import ValidationError
    try:
        if not row or row.sha256 != digest(row.body):
            raise ValueError()
        return CollectionReceipt.model_validate(row.body)
    except (ValidationError, ValueError, TypeError, KeyError):
        raise Problem(503, "COLLECTION_INTEGRITY_FAILED") from None


def epoch(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def acknowledge_instructions(db, account, check, body):
    from .domain import record, save_record
    from .operator_governance import acquisition_context, capture_configuration

    attempt = record(db, account, "attempt", body.attempt_id)
    if not attempt or attempt.parent_id != check.id or attempt.body["status"] != "started":
        raise Problem(409, "STARTED_ATTEMPT_REQUIRED")
    channel = "ecg" if attempt.body["component"] == "cardiac" and attempt.body["component_metadata"].get("modality") == "ecg" else attempt.body["component"]
    config = capture_configuration(db, account, check, channel, body.configuration_id, body.configuration_hash)
    acquisition_context(db, account, check, config)
    protocol = config.get("participant_protocol")
    if not protocol or (body.configuration_version, body.configuration_submitted_sha256, body.participant_protocol_sha256) != (config["version"], digest(config), digest(protocol)):
        raise Problem(403, "PARTICIPANT_PROTOCOL_CHANGED")
    if attempt.body["configuration_id"] != config["configuration_id"] or attempt.body["configuration_hash"] != config["sha256"]:
        raise Problem(403, "CAPTURE_SCOPE_MISMATCH")
    required = [item["id"] for item in protocol["required_confirmations"]]
    if len(set(body.confirmations)) != len(body.confirmations) or set(body.confirmations) != set(required):
        raise Problem(422, "REQUIRED_INSTRUCTION_CONFIRMATIONS")
    acknowledged = epoch(body.acknowledged_at)
    if not max(now() - protocol["maximum_acknowledgment_age_seconds"], attempt.created - 5) <= acknowledged <= now() + 5:
        raise Problem(422, "ACKNOWLEDGMENT_TIME_INVALID")
    if protocol["kind"] == "cardiac":
        if (body.collection_method_id is not None or body.collection_method_version is not None
            or body.setup_id not in {item["id"] for item in protocol["permitted_setups"]}
            or body.rest_started_at is None
            or not max(epoch(attempt.body["started_at"]) - 5, acknowledged - protocol["rest_duration_seconds"] - 300) <= epoch(body.rest_started_at) <= acknowledged - protocol["rest_duration_seconds"]):
            raise Problem(422, "PREPARATION_NOT_CONFIRMED")
    else:
        if body.setup_id is not None or body.rest_started_at is not None:
            raise Problem(422, "PREPARATION_SCOPE_MISMATCH")
        if not any(item["id"] == body.collection_method_id and item["version"] == body.collection_method_version for item in protocol["methods"]):
            raise Problem(422, "COLLECTION_METHOD_NOT_APPROVED")
    from sqlalchemy import select, func
    from .db import Record
    count = db.scalar(select(func.count()).select_from(Record).where(Record.account_id == account.id,
        Record.generation == account.generation, Record.parent_id == check.id, Record.kind == "instruction_receipt"))
    per_attempt = db.scalar(select(func.count()).select_from(Record).where(Record.account_id == account.id,
        Record.generation == account.generation, Record.parent_id == check.id, Record.kind == "instruction_receipt",
        Record.body["attempt_id"].as_string() == body.attempt_id))
    if count >= 128 or per_attempt >= 8:
        raise Problem(413, "INSTRUCTION_RECEIPT_LIMIT")
    consent = record(db, account, "consent", check.study_id)
    value = {"instruction_receipt_id": uid(), "session_id": check.id, **body.data(),
        "consent_record_id": consent.body["consent_record_id"], "accepted_at": iso()}
    save_record(db, account, "instruction_receipt", value["instruction_receipt_id"], value, check.id)
    return value


def instruction_receipt(db, account, check, attempt, config, receipt_id, *, fresh=True):
    from .domain import record

    protocol = config.get("participant_protocol")
    if not protocol:
        if config["channel"] in ("cardiac", "ecg") or config["software_adapter_id"] == "reference_lab_import_v1":
            raise Problem(403, "PARTICIPANT_PROTOCOL_REQUIRED")
        if receipt_id is not None:
            raise Problem(422, "PREPARATION_SCOPE_MISMATCH")
        return None
    row = record(db, account, "instruction_receipt", receipt_id or "")
    consent = record(db, account, "consent", check.study_id)
    if (not row or row.parent_id != check.id or row.sha256 != digest(row.body)
        or row.body["attempt_id"] != attempt["attempt_id"]
        or row.body["configuration_id"] != config["configuration_id"]
        or row.body["configuration_version"] != config["version"]
        or row.body["configuration_hash"] != config["sha256"]
        or row.body["configuration_submitted_sha256"] != digest(config)
        or row.body["participant_protocol_sha256"] != digest(protocol)
        or not consent or row.body["consent_record_id"] != consent.body.get("consent_record_id")):
        raise Problem(403, "CURRENT_INSTRUCTION_ACKNOWLEDGMENT_REQUIRED")
    if fresh and now() - min(row.created, epoch(row.body["acknowledged_at"])) > protocol["maximum_acknowledgment_age_seconds"]:
        raise Problem(403, "INSTRUCTION_ACKNOWLEDGMENT_EXPIRED")
    return row


def validate_instruction_evidence(db, account, check, attempt, config, authorization):
    row = instruction_receipt(db, account, check, attempt, config, authorization.body.get("instruction_receipt_id"), fresh=False)
    if row is not None and attempt["component_metadata"].get("instruction_receipt") != row.body:
        raise Problem(422, "INSTRUCTION_EVIDENCE_MISMATCH")
    if row is not None and authorization.body["server_started_epoch"] - min(row.created, epoch(row.body["acknowledged_at"])) > config["participant_protocol"]["maximum_acknowledgment_age_seconds"]:
        raise Problem(403, "INSTRUCTION_ACKNOWLEDGMENT_EXPIRED")
    return row


def accept_collection(db, account, check, body):
    from sqlalchemy import select
    from .db import Record
    from .domain import record, save_record, validate_component
    from .operator_governance import capture_configuration, started_capture

    old = record(db, account, "attempt", body.attempt_id)
    if (not old or old.parent_id != check.id or old.body["status"] != "started"
        or old.body["component"] != "saliva" or old.body["record_id"] != body.sample_id):
        raise Problem(409, "STARTED_COLLECTION_ATTEMPT_REQUIRED")
    config = capture_configuration(db, account, check, "saliva", old.body["configuration_id"], old.body["configuration_hash"])
    if config["software_adapter_id"] != "reference_lab_import_v1":
        raise Problem(403, "REFERENCE_LAB_COLLECTION_REQUIRED")
    if record(db, account, "collection", body.sample_id) or db.scalar(select(Record.id).where(
        Record.kind == "collection", Record.body["request"]["sample_id"].as_string() == body.sample_id).limit(1)):
        raise Problem(409, "SAMPLE_ID_ALREADY_ALLOCATED")
    receipt = instruction_receipt(db, account, check, old.body, config, body.instruction_receipt_id, fresh=False)
    if (body.collection_method_id, body.collection_method_version) != (receipt.body["collection_method_id"], receipt.body["collection_method_version"]):
        raise Problem(422, "COLLECTION_METHOD_MISMATCH")
    protocol = config["participant_protocol"]
    method = next(item for item in protocol["methods"] if item["id"] == body.collection_method_id)
    if (set(body.missing_reasons.values()) - set(method["permitted_null_reasons"])
        or len(set(body.quality_flags)) != len(body.quality_flags)):
        raise Problem(422, "COLLECTION_REASON_NOT_APPROVED")
    collected = epoch(body.collected_at)
    if collected > now() + 5 or now() - collected > protocol["maximum_collection_submission_delay_seconds"]:
        raise Problem(422, "COLLECTION_TIME_INVALID")
    events = body.storage_handling_events
    if len({item.event for item in events}) != len(events) or any(not collected <= epoch(item.occurred_at) <= now() + 5 for item in events):
        raise Problem(422, "COLLECTION_HANDLING_INVALID")
    if set(item.event for item in events) - set(method["required_handling_events"]):
        raise Problem(422, "COLLECTION_HANDLING_NOT_APPROVED")
    if body.status == "valid":
        for field, required in (("saliva_volume_ml", method["saliva_volume_required"]),
            ("buffer_volume_ml", method["buffer_volume_required"]), ("dilution_factor", method["dilution_factor_required"]),
            ("collector_lot", method["collector_lot_required"]), ("container_id", method["container_required"]),
            ("cartridge_expiry", method["expiry_required"])):
            if required and getattr(body, field) is None:
                raise Problem(422, "REQUIRED_COLLECTION_VALUE_UNKNOWN")
        for field, low, high in (("saliva_volume_ml", "saliva_volume_min_ml", "saliva_volume_max_ml"),
            ("buffer_volume_ml", "buffer_volume_min_ml", "buffer_volume_max_ml")):
            value = getattr(body, field)
            if value is not None and method[low] is not None and not method[low] <= value <= method[high]:
                raise Problem(422, "COLLECTION_QUANTITY_OUTSIDE_APPROVAL")
        if (body.container_id is not None and body.container_id not in method["permitted_containers"]
            or body.cartridge_expiry is not None and epoch(body.cartridge_expiry) <= collected):
            raise Problem(422, "COLLECTION_SUPPLIES_INVALID")
        if body.dilution_factor is not None:
            definition = method["dilution_definition"]
            expected = (body.saliva_volume_ml + body.buffer_volume_ml) / body.saliva_volume_ml if definition == "total_mixture_over_saliva" and body.saliva_volume_ml is not None and body.buffer_volume_ml is not None else 1.0 if definition == "undiluted" else method["fixed_dilution_factor"] if definition == "fixed_factor" else None
            if definition == "undiluted" and body.buffer_volume_ml not in (None, 0.0):
                raise Problem(422, "COLLECTION_DILUTION_INCONSISTENT")
            if expected is None or abs(body.dilution_factor - expected) > max(1e-8, abs(expected) * 1e-6):
                raise Problem(422, "COLLECTION_DILUTION_INCONSISTENT")
        if {item.event for item in events} != set(method["required_handling_events"]):
            raise Problem(422, "COLLECTION_HANDLING_REQUIRED")
    sample = {"sample_id": body.sample_id, "collection_method_id": body.collection_method_id,
        "collected_at": body.collected_at, "volume_ml": body.saliva_volume_ml,
        "dilution_factor": body.dilution_factor, "status": body.status, "quality_flags": body.quality_flags}
    projection = {"sample": sample, "saliva": []}
    terminal = {**old.body, "status": body.status, "source": "reference_lab",
        "started_at": body.collected_at, "ended_at": body.collected_at,
        "quality_flags": body.quality_flags, "component_metadata": {
            "armed_at": old.body["started_at"], "projection": projection,
            "instruction_receipt": receipt.body, "collection_request_sha256": digest(body.data())}}
    authorization = started_capture(db, account, check, terminal, config)
    if authorization.body.get("instruction_receipt_id") != body.instruction_receipt_id:
        raise Problem(403, "INSTRUCTION_AUTHORIZATION_MISMATCH")
    value = {"collection_receipt_id": uid(), "session_id": check.id, "request": body.data(),
        "state": "pending_lab" if body.status == "valid" else "invalid_collection",
        "accepted_at": iso(), "authorization_id": authorization.body["authorization_id"],
        "configuration_submitted_sha256": digest(config), "configuration_version": config["version"],
        "participant_protocol_sha256": digest(protocol), "instruction_receipt": receipt.body,
        "projection": projection, "attempt": terminal}
    terminal["component_metadata"]["collection_receipt_id"] = value["collection_receipt_id"]
    validate_component(terminal)
    old.body = terminal
    old.sha256 = digest(terminal)
    old.revision += 1
    value["attempt_revision"], value["attempt_sha256"] = old.revision, old.sha256
    # The receipt contains the complete immutable declared specimen metadata.
    CollectionReceipt.model_validate(value)
    save_record(db, account, "collection", body.sample_id, value, check.id)
    return value


def collection_status(db, account, check, sample_id):
    from sqlalchemy import select
    from .db import Record
    from .domain import record
    row = record(db, account, "collection", sample_id)
    if not row or row.parent_id != check.id:
        raise Problem(404, "NOT_FOUND")
    checked_collection(row)
    original = record(db, account, "attempt", row.body["request"]["attempt_id"])
    if (not original or original.parent_id != check.id or original.body != row.body["attempt"]
        or original.sha256 != row.body["attempt_sha256"] or original.revision != row.body["attempt_revision"]
        or original.sha256 != digest(original.body)):
        raise Problem(503, "COLLECTION_INTEGRITY_FAILED")
    imports = list(db.scalars(select(Record).where(Record.account_id == account.id,
        Record.generation == account.generation, Record.parent_id == check.id,
        Record.kind == "lab_import", Record.body["sample_id"].as_string() == sample_id).limit(2)))
    if row.sha256 != digest(row.body) or len(imports) > 1:
        raise Problem(503, "COLLECTION_INTEGRITY_FAILED")
    for item in imports:
        accepted = record(db, account, "attempt", item.body.get("analysis_attempt_id", ""))
        if (item.sha256 != digest(item.body) or item.body.get("collection_receipt_id") != row.body["collection_receipt_id"]
            or item.body.get("collection_attempt_id") != row.body["request"]["attempt_id"]
            or item.body.get("account_ref") != account.id or item.body.get("data_generation") != account.generation
            or item.body.get("session_id") != check.id or item.body.get("sample_id") != sample_id
            or item.body.get("configuration_submitted_sha256") != row.body["configuration_submitted_sha256"]
            or not accepted or accepted.sha256 != digest(accepted.body) or accepted.parent_id != check.id
            or accepted.body.get("session_id") != check.id or accepted.body.get("record_id") != sample_id
            or accepted.body.get("component") != "saliva" or accepted.body.get("source") != "reference_lab"
            or accepted.body.get("supersedes_attempt_id") != original.body["attempt_id"]
            or accepted.body.get("configuration_id") != original.body["configuration_id"]
            or accepted.body.get("configuration_hash") != original.body["configuration_hash"]
            or accepted.body.get("component_metadata", {}).get("lab_import_id") != item.body.get("import_id")
            or accepted.body.get("component_metadata", {}).get("projection") != {"sample": row.body["projection"]["sample"], "saliva": item.body.get("measurements")}):
            raise Problem(503, "COLLECTION_INTEGRITY_FAILED")
    abandonment = record(db, account, "collection_abandon", sample_id)
    if abandonment and (abandonment.sha256 != digest(abandonment.body) or abandonment.body.get("collection_sha256") != row.sha256):
        raise Problem(503, "COLLECTION_INTEGRITY_FAILED")
    current = record(db, account, "attempt", imports[0].body["analysis_attempt_id"] if imports else row.body["request"]["attempt_id"])
    if not current or current.sha256 != digest(current.body):
        raise Problem(503, "COLLECTION_INTEGRITY_FAILED")
    return {**row.body, "collection_attempt": row.body["attempt"],
        "collection_attempt_revision": row.body["attempt_revision"], "collection_attempt_sha256": row.body["attempt_sha256"],
        "attempt": current.body, "attempt_revision": current.revision, "attempt_sha256": current.sha256,
        "abandonment": abandonment.body if abandonment else None,
        "state": "analysis_available" if imports else "analysis_canceled" if abandonment else row.body["state"],
        "imports": [{"import_id": item.body["import_id"], "measurements": item.body["measurements"],
            "attempt": record(db, account, "attempt", item.body["analysis_attempt_id"]).body,
            "attempt_revision": record(db, account, "attempt", item.body["analysis_attempt_id"]).revision,
            "attempt_sha256": record(db, account, "attempt", item.body["analysis_attempt_id"]).sha256,
            "source_report_artifact_id": item.body["source_report_artifact_id"]} for item in imports]}


def require_completed_collections(db, account, check):
    from sqlalchemy import select
    from .db import Record
    rows = list(db.scalars(select(Record).where(Record.account_id == account.id,
        Record.generation == account.generation, Record.parent_id == check.id,
        Record.kind == "collection").limit(129)))
    if len(rows) > 128:
        raise Problem(413, "LIMIT_EXCEEDED")
    for row in rows:
        collection_status(db, account, check, row.body["request"]["sample_id"])
        from .domain import record
        if row.body["state"] == "pending_lab" and not record(db, account, "collection_abandon", row.body["request"]["sample_id"]) and not db.scalar(select(Record.id).where(
            Record.account_id == account.id, Record.generation == account.generation,
            Record.parent_id == check.id, Record.kind == "lab_import",
            Record.body["sample_id"].as_string() == row.body["request"]["sample_id"]).limit(1)):
            raise Problem(409, "LAB_ANALYSIS_PENDING")


class CollectionAbandonment(DTO):
    confirmation: Literal[True]
    reason: Literal["USER_CANCELED", "PARTICIPANT_DECLINED", "SPECIMEN_UNAVAILABLE"]

    @field_validator("confirmation", mode="before")
    @classmethod
    def confirmed(cls, value):
        if value is not True:
            raise ValueError("Explicit cancellation confirmation is required")
        return value


def abandon_collection(db, account, check, sample_id, body):
    from .domain import record, save_record
    from .operator_governance import capture_configuration
    row = record(db, account, "collection", sample_id)
    if not row or row.parent_id != check.id or row.sha256 != digest(row.body):
        raise Problem(404, "NOT_FOUND")
    checked_collection(row)
    config = capture_configuration(db, account, check, "saliva", row.body["attempt"]["configuration_id"], row.body["attempt"]["configuration_hash"])
    status = collection_status(db, account, check, sample_id)
    if status["state"] != "pending_lab":
        raise Problem(409, "COLLECTION_ANALYSIS_NOT_PENDING")
    if record(db, account, "collection_abandon", sample_id):
        raise Problem(409, "COLLECTION_ANALYSIS_ALREADY_CANCELED")
    value = {"abandonment_id": uid(), "session_id": check.id, "sample_id": sample_id,
        "collection_receipt_id": row.body["collection_receipt_id"], "collection_sha256": row.sha256,
        "configuration_submitted_sha256": digest(config), "accepted_at": iso(), **body.data(),
        "state": "analysis_canceled"}
    save_record(db, account, "collection_abandon", sample_id, value, check.id)
    return {**value, "collection": row.body}


def validate_abandoned_collection(db, account, check, attempt, config):
    from .domain import record
    sample_id = attempt["record_id"]
    row, abandon = record(db, account, "collection", sample_id), record(db, account, "collection_abandon", sample_id)
    if (not row or not abandon or row.parent_id != check.id or abandon.parent_id != check.id
        or row.sha256 != digest(row.body) or abandon.sha256 != digest(abandon.body)
        or abandon.body["collection_sha256"] != row.sha256
        or abandon.body["configuration_submitted_sha256"] != digest(config)
        or row.body["configuration_submitted_sha256"] != digest(config)
        or row.body["attempt"] != attempt or row.body["projection"]["saliva"] != []):
        raise Problem(403, "AUTHORIZED_COLLECTION_ABANDONMENT_REQUIRED")
    return row
