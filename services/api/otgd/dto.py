from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator

from .canonical import canonical


def valid_utc(value):
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


UUID = Annotated[
    str,
    Field(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
    ),
]
SHA = Annotated[str, Field(pattern="^[a-f0-9]{64}$")]
UTC = Annotated[
    str,
    Field(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"),
    AfterValidator(valid_utc),
]
Name = Annotated[str, Field(min_length=1, max_length=256)]
Source = Literal["simulated", "prototype_sensor", "reference_lab", "validated_sensor"]


class DTO(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)

    def data(self):
        return self.model_dump(mode="json")


class ReplacementLink(DTO):
    session_id: UUID
    created_at: UTC
    state: Literal["processing", "completed", "invalid"]


class ReplacementLinks(DTO):
    schema_version: Literal["1.0.0"] = "1.0.0"
    session_id: UUID
    data_generation: Annotated[int, Field(ge=1, le=9007199254740991)]
    base_snapshot_sha256: SHA
    previous: ReplacementLink | None
    items: Annotated[list[ReplacementLink], Field(max_length=100)]
    next_cursor: Annotated[str, Field(min_length=1, max_length=1024)] | None


class Profile(DTO):
    age_years: Annotated[int, Field(ge=18, le=125)] | None = None
    height_cm: Annotated[float, Field(gt=0, le=300)] | None = None
    weight_kg: Annotated[float, Field(gt=0, le=500)] | None = None
    bmi: Annotated[float, Field(ge=0)] | None = None
    recorded_at: UTC
    source: Literal["self_report", "study_measurement", "synthetic"] = "self_report"

    @model_validator(mode="after")
    def bmi_consistent(self):
        expected = (
            self.weight_kg / (self.height_cm / 100) ** 2
            if self.weight_kg and self.height_cm
            else None
        )
        if (expected is None) != (self.bmi is None) or (
            expected is not None and abs(expected - self.bmi) > 0.01
        ):
            raise ValueError("BMI must match canonical height and weight")
        return self


class History(DTO):
    use_frequency: Literal[
        "never", "occasional", "frequent", "daily", "unknown", "declined"
    ] = "unknown"
    route: Literal["inhaled", "oral", "other", "unknown", "declined"] = "unknown"
    time_since_use_min: Annotated[float, Field(ge=0)] | None = None
    recent_exercise: bool | None = None
    sleep_hours: Annotated[float, Field(ge=0, le=24)] | None = None
    alcohol_co_use: Literal["reported", "not_reported", "unknown", "declined"] = (
        "unknown"
    )


class SelfReport(DTO):
    last_use_status: Literal["known", "unknown", "declined"]
    last_use_at: UTC | None
    confirmed_at: UTC

    @model_validator(mode="after")
    def coherent(self):
        if (self.last_use_status == "known") != (self.last_use_at is not None):
            raise ValueError("Last-use status and time disagree")
        return self


class ProfileWrite(DTO):
    profile: Profile
    history: History
    context: SelfReport | None = None


class Acknowledgment(DTO):
    version: Name
    sha256: SHA
    acknowledged_at: UTC


class Confirm(DTO):
    confirmation: Literal[True]


class CreateCheck(DTO):
    session_id: UUID
    mode: Literal["synthetic", "analytical", "controlled_research"]
    protocol_id: Name | None = None
    study_id: Name | None = None
    supersedes_session_id: UUID | None = None


class ConfigurationRef(DTO):
    id: Name
    version: Name
    sha256: SHA
    scope: Name


class DeviceAssociation(DTO):
    device_id: Name
    binding_id: UUID | None = None
    boot_id: Name
    hardware_revision: Name
    firmware_version: Name
    clock_evidence_ref: Name | None = None


class CaptureContext(DTO):
    schema_version: Literal["1.0.0"]
    session_id: UUID
    context_confirmed_at: UTC
    profile_version_id: UUID | None
    profile_snapshot_sha256: SHA
    history_snapshot_sha256: SHA
    protocol_id: Name | None
    configuration_refs: Annotated[list[ConfigurationRef], Field(max_length=16)]
    baseline_refs: Annotated[list[Name], Field(max_length=8)]
    device_associations: Annotated[list[DeviceAssociation], Field(max_length=8)]
    self_report_context: SelfReport | None = None


class CaptureAttempt(DTO):
    schema_version: Literal["1.0.0"]
    session_id: UUID
    attempt_id: UUID
    component: Literal["saliva", "eyes", "cardiac", "task", "alcohol"]
    record_id: UUID
    supersedes_attempt_id: UUID | None
    status: Literal["started", "valid", "invalid", "canceled", "not_collected"]
    source: Source
    started_at: UTC | None
    ended_at: UTC | None
    configuration_id: Name | None
    configuration_hash: SHA | None
    quality_flags: Annotated[list[Name], Field(max_length=64)]
    component_metadata: dict
    artifact_refs: Annotated[list[UUID], Field(max_length=16)] = []
    attestation_refs: Annotated[list[UUID], Field(max_length=16)] = []

    @model_validator(mode="after")
    def bounded(self):
        if len(canonical(self.data())) > 512 * 1024:
            raise ValueError("Attempt exceeds bound")
        if self.status == "not_collected" and (self.started_at or self.ended_at):
            raise ValueError("Absent acquisition has no time")
        if self.status in ("invalid", "canceled") and not self.quality_flags:
            raise ValueError("Failed acquisition needs a reason")
        return self


class AttemptHash(DTO):
    attempt_id: UUID
    sha256: SHA


class Selection(DTO):
    saliva: UUID | None
    eyes: UUID | None
    cardiac: UUID | None
    task: UUID | None
    alcohol: UUID | None


class EvidenceManifest(DTO):
    schema_version: Literal["1.0.0"]
    session_id: UUID
    context_sha256: SHA
    attempts: Annotated[list[AttemptHash], Field(max_length=128)]
    selected: Selection

    @model_validator(mode="after")
    def unique(self):
        if len({v.attempt_id for v in self.attempts}) != len(self.attempts):
            raise ValueError("Duplicate attempt")
        return self


class Finalize(DTO):
    snapshot_sha256: SHA
    evidence_sha256: SHA


class ExportSelection(DTO):
    kind: Literal["single", "selected", "all"]
    session_ids: Annotated[list[UUID], Field(max_length=500)]

    @model_validator(mode="after")
    def coherent(self):
        n = len(self.session_ids)
        if (
            len(set(self.session_ids)) != n
            or (self.kind == "single" and n != 1)
            or (self.kind == "selected" and n < 1)
            or (self.kind == "all" and n)
        ):
            raise ValueError("Invalid export selection")
        return self


class RawExportScope(DTO):
    authorization_id: Name
    authorization_version: Name
    authorization_sha256: SHA
    export_notice_version: Name
    export_notice_sha256: SHA
    acknowledged_at: UTC
    confirmed: Literal[True]
    artifact_ids: Annotated[list[UUID], Field(min_length=1, max_length=128)]

    @field_validator("confirmed", mode="before")
    @classmethod
    def explicit_confirmation(cls, value):
        if value is not True:
            raise ValueError("An explicit raw export confirmation is required")
        return value

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.artifact_ids)) != len(self.artifact_ids):
            raise ValueError("Duplicate raw artifact selection")
        return self


class ExportRequest(DTO):
    selection: ExportSelection
    format: Literal["json_zip"]
    include_raw: bool
    raw_scope: RawExportScope | None = None

    @model_validator(mode="after")
    def separate_raw_scope(self):
        if self.include_raw != (self.raw_scope is not None):
            raise ValueError("Raw inclusion requires its separate exact confirmed scope")
        return self


class DeleteRequest(Confirm):
    scope: Literal["all_data", "account"]


class ArtifactRequest(DTO):
    study_id: Name
    session_id: UUID
    consent_record_id: UUID
    retention_policy_id: Name
    artifact_kind: Literal["eye_video", "ecg_waveform", "source_lab_report"]
    sha256: SHA
    size_bytes: Annotated[int, Field(gt=0, le=64 * 1024 * 1024)]
    media_type: Literal["video/mp4", "application/octet-stream", "application/pdf"]
    # Participant raw capture requires an immutable optional-purpose receipt
    # and owned acquisition; administrative report uploads use their own route.
    raw_consent_record_id: UUID | None = None
    attempt_id: UUID | None = None
    capture_started_at: UTC | None = None


class CompleteArtifact(DTO):
    sha256: SHA
    size_bytes: Annotated[int, Field(gt=0, le=64 * 1024 * 1024)]
    media_type: Literal["video/mp4", "application/octet-stream", "application/pdf"]


class BindChallenge(DTO):
    device_id: Name
    key_id: Name


class Binding(DTO):
    challenge_id: UUID
    signature: Annotated[str, Field(max_length=256)]


class CaptureAuthorization(DTO):
    attempt_id: UUID
    channel: Literal["saliva", "eyes", "cardiac", "ecg", "task", "alcohol"]
    binding_id: UUID | None
    device_id: Name | None
    configuration_id: Name
    configuration_hash: SHA
    raw_recording_kind: Literal["eye_video", "ecg_waveform"] | None = None
    instruction_receipt_id: UUID | None = None


class StartAuthorization(DTO):
    attempt_id: UUID
    device_boot_id: Name | None
    device_nonce: Name | None = None


class AttestationEnvelope(DTO):
    schema_version: Literal["1.0.0"]
    environment: Literal["local", "qa", "prod", "test"]
    owner_ref: UUID
    data_generation: Annotated[int, Field(gt=0)]
    session_id: UUID
    attempt_id: UUID
    authorization_id: UUID
    binding_id: UUID
    device_id: Name
    key_id: Name
    boot_id: Name
    sequence: Annotated[int, Field(ge=0, le=9007199254740991)]
    configuration_hash: SHA
    payload_sha256: SHA


class Attestation(DTO):
    attestation_id: UUID
    envelope: AttestationEnvelope
    signature: Annotated[str, Field(max_length=256)]
    normalized_payload: dict


class Consent(DTO):
    invitation_id: Name
    document_version: Name
    document_sha256: SHA
    accepted: Literal[True]
    acknowledged_at: UTC


class Withdrawal(DTO):
    confirmation: Literal[True]


class AlcoholLimits(DTO):
    lod_mg_l: Annotated[float, Field(ge=0)] | None
    loq_mg_l: Annotated[float, Field(ge=0)] | None
    upper_mg_l: Annotated[float, Field(ge=0)] | None


class Alcohol(DTO):
    schema_version: Literal["1.0.0"]
    measurement_id: UUID
    session_id: UUID
    collected_at: UTC | None
    measured_at: UTC | None
    source: Source
    qualifier: Literal[
        "quantified",
        "not_measured",
        "invalid",
        "below_loq",
        "above_range",
        "not_detected",
    ]
    value_mg_l: Annotated[float, Field(ge=0)] | None
    unit: Literal["mg/L"]
    limits: AlcoholLimits
    method_id: Name | None
    calibration_id: Name | None
    device_id: Name | None
    boot_id: Name | None
    configuration_hash: SHA | None
    quality_flags: Annotated[list[Name], Field(max_length=64)]

    @model_validator(mode="after")
    def coherent(self):
        known = [
            v
            for v in (
                self.limits.lod_mg_l,
                self.limits.loq_mg_l,
                self.limits.upper_mg_l,
            )
            if v is not None
        ]
        if known != sorted(known):
            raise ValueError("Alcohol limits are out of order")
        if self.qualifier == "quantified":
            if (
                self.value_mg_l is None
                or self.collected_at is None
                or self.measured_at is None
                or self.limits.loq_mg_l is None
                or self.limits.upper_mg_l is None
                or not self.limits.loq_mg_l <= self.value_mg_l <= self.limits.upper_mg_l
            ):
                raise ValueError("Quantified alcohol needs timing and in-range value")
        elif self.value_mg_l is not None:
            raise ValueError("Censored alcohol must remain null")
        if self.qualifier == "not_measured" and self.measured_at is not None:
            raise ValueError("Unrun alcohol has no analysis time")
        if self.source == "validated_sensor" and not all(
            (
                self.calibration_id,
                self.method_id,
                self.device_id,
                self.boot_id,
                self.configuration_hash,
            )
        ):
            raise ValueError("Qualified alcohol requires provenance")
        if (
            self.collected_at
            and self.measured_at
            and self.measured_at < self.collected_at
        ):
            raise ValueError("Analysis predates collection")
        return self


class LabImport(DTO):
    account_ref: UUID | None = None
    data_generation: Annotated[int, Field(ge=1, le=9007199254740991)] | None = None
    sample_id: UUID | None = None
    collection_attempt_id: UUID | None = None
    study_id: Name
    session_id: UUID
    source_report_artifact_id: UUID
    measurements: Annotated[list[dict], Field(max_length=16)]
