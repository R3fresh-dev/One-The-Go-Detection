"""Maintenance-only registry authority. No participant can create an approval.

Original submissions and decision events retain their own canonical identity.
Release only changes the active pointer; it never rewrites submitted evidence.
"""

import base64
import hashlib
import re
from typing import Annotated, Literal

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from pydantic import Field, model_validator
from jsonschema.exceptions import ValidationError as SchemaError
from sqlalchemy import select, text

from .canonical import canonical, digest
from .db import Registry, RegistryEvent, RegistryVersion, iso, now, uid
from .dto import DTO, Name, SHA, UUID
from .errors import Problem
from .native_evidence import CONFIG as TASK_MATERIAL
from .model_engine import ArtifactRef, CoUsePolicy, CompatibilityPolicy, EvaluationReport, QualityPolicy
from .raw_export import RawExportAuthorization
from .participant_acquisition import ParticipantProtocol
from .vendor_evidence import SparkFunMaterial
from .cardiac_authority import CardiacTimingPolicy

Channel = Literal["saliva", "eyes", "cardiac", "ecg", "task", "alcohol"]
Version = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")]
Names = Annotated[list[Name], Field(max_length=64)]
ACCOUNTS = Annotated[list[UUID], Field(max_length=1000)]
CHANNELS = ("saliva", "eyes", "cardiac", "ecg", "task", "alcohol")
# Build inventory, not an operator-controlled switch. More adapters require code,
# protocol tests and a separately reviewed release before appearing here.
SOFTWARE_ADAPTERS = {"task": {"task_native_v1"},
    "saliva": {"reference_lab_import_v1"},
    "eyes": {"optical_roi_v1"},
    "cardiac": {"otgd_signed_reader_v1"}, "ecg": {"otgd_signed_reader_v1"}}
PHYSICAL_DRIVERS = {"cardiac": {"otgd_esp32_adc_v1", "otgd_sparkfun_max32664_v1"}, "ecg": {"otgd_esp32_adc_v1"}}
REGISTRY_LOCK = 798114232


class Submission(DTO):
    schema_version: Literal["1.0.0"] = "1.0.0"
    registry_id: Name
    version: Version
    expires_at: Annotated[float, Field(gt=0)]
    evidence_ref: Name
    evidence_sha256: SHA


class Study(Submission):
    study_id: Name
    protocol_id: Name
    name: Name
    account_refs: ACCOUNTS
    invitation_id: Name
    document_version: Name
    document_text: Annotated[str, Field(min_length=1, max_length=65536)]
    document_sha256: SHA
    retention_summary: Annotated[str, Field(min_length=1, max_length=4096)]
    channels: Annotated[dict[Channel, Name], Field(max_length=6)]
    model_id: Name | None = None

    @model_validator(mode="after")
    def document(self):
        if self.registry_id != self.study_id or len(self.document_text.encode()) > 65536:
            raise ValueError("Study identity or document bound is invalid")
        if hashlib.sha256(self.document_text.encode()).hexdigest() != self.document_sha256:
            raise ValueError("Consent document digest does not match its exact text")
        if len(set(self.account_refs)) != len(self.account_refs):
            raise ValueError("Duplicate study account")
        return self


class Device(Submission):
    device_id: Name
    key_id: Name
    public_key_spki: Annotated[str, Field(min_length=1, max_length=1024)]
    hardware_revision: Name
    firmware_version: Name
    approved_protocol_ids: Annotated[list[Name], Field(min_length=1, max_length=64)]
    account_refs: ACCOUNTS

    @model_validator(mode="after")
    def key(self):
        if self.registry_id != self.device_id + ":" + self.key_id:
            raise ValueError("Device identity must include its key version")
        try:
            key = serialization.load_der_public_key(base64.b64decode(self.public_key_spki, validate=True))
        except (ValueError, TypeError) as error:
            raise ValueError("Invalid public key") from error
        if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
            raise ValueError("Device key must be P-256")
        return self


class OpticalROI(DTO):
    x0: Annotated[float, Field(ge=0, le=1)]
    y0: Annotated[float, Field(ge=0, le=1)]
    x1: Annotated[float, Field(ge=0, le=1)]
    y1: Annotated[float, Field(ge=0, le=1)]

    @model_validator(mode="after")
    def ordered(self):
        if self.x0 >= self.x1 or self.y0 >= self.y1:
            raise ValueError("Optical region must have positive area")
        return self


class OpticalGeometryScope(DTO):
    phone_models: Annotated[list[Name], Field(min_length=1, max_length=64)]
    os_versions: Annotated[list[Name], Field(min_length=1, max_length=64)]
    native_builds: Annotated[list[Name], Field(min_length=1, max_length=64)]
    camera_id: Name
    lens_facing: Literal["front", "back"]
    capture_width: Annotated[int, Field(ge=64, le=1920)]
    capture_height: Annotated[int, Field(ge=64, le=1920)]
    expected_output_rotation_degrees: Literal[0, 90, 180, 270]
    roi: OpticalROI
    roi_sample_width: Annotated[int, Field(ge=8, le=128)]
    roi_sample_height: Annotated[int, Field(ge=8, le=128)]
    extractor_version: Literal["otgd-dark-component-v1"]
    pixel_basis: Literal["roi_sample_pixels"]
    pixels_to_mm: Annotated[float, Field(gt=0, le=100)]
    min_diameter_pixels: Annotated[float, Field(gt=0, le=1920)]
    max_diameter_pixels: Annotated[float, Field(gt=0, le=1920)]
    max_uncertainty_mm: Annotated[float, Field(gt=0, le=100)]

    @model_validator(mode="after")
    def extent(self):
        if self.min_diameter_pixels >= self.max_diameter_pixels:
            raise ValueError("Calibrated diameter range must be ordered")
        return self


class NativeTimingScope(DTO):
    phone_models: Annotated[list[Name], Field(min_length=1, max_length=64)]
    os_versions: Annotated[list[Name], Field(min_length=1, max_length=64)]
    native_builds: Annotated[list[Name], Field(min_length=1, max_length=64)]
    implementation_version: Name
    extractor_version: Name
    input_timestamp_method: Name
    presentation_evidence_method: Name
    clock_domain: Name
    bias_ms: Annotated[float, Field(ge=-1000, le=1000)]
    max_uncertainty_ms: Annotated[float, Field(gt=0, le=1000)]
    qualifying_trial_count: Annotated[int, Field(ge=30, le=1000000)]


class CardiacServerIntervalScope(DTO):
    """Reviewed HR-only interval; no claim of a measured device UTC clock."""
    device_id: Name
    key_id: Name
    hardware_revision: Name
    firmware_versions: Annotated[list[Name], Field(min_length=1, max_length=64)]
    adapter_id: Literal["otgd_esp32_adc_v1", "otgd_sparkfun_max32664_v1"]
    extractor_version: Literal["adc_peak_intervals_v1", "sparkfun_sensor_bpm_v1"]
    channel: Literal["cardiac"]
    modality: Literal["ppg"]
    configuration_id: Name
    configuration_version: Version
    configuration_submitted_sha256: SHA
    behavior: Literal["follows_current_signed_grant"]
    timing_method: Literal["server_issue_to_attestation_receipt_v1"]
    maximum_interval_ms: Annotated[int, Field(ge=100, le=120000)]
    server_utc_error_ms: Annotated[float, Field(ge=0, le=1000)]
    maximum_monotonic_rate_error_ppm: Annotated[int, Field(ge=0, le=10000)] | None

    @model_validator(mode="after")
    def driver(self):
        extractors = {"otgd_esp32_adc_v1": "adc_peak_intervals_v1",
            "otgd_sparkfun_max32664_v1": "sparkfun_sensor_bpm_v1"}
        if (self.extractor_version != extractors[self.adapter_id] or len(set(self.firmware_versions)) != len(self.firmware_versions)
            or (self.adapter_id == "otgd_sparkfun_max32664_v1") != (self.maximum_monotonic_rate_error_ppm is not None)):
            raise ValueError("Cardiac interval requires its exact supported driver/extractor and unique firmware scope")
        return self


class Calibration(Submission):
    calibration_id: Name
    purpose: Literal["device", "model", "native_timing", "optical_geometry", "cardiac_server_interval"]
    native_timing: NativeTimingScope | None = None
    optical_geometry: OpticalGeometryScope | None = None
    cardiac_server_interval: CardiacServerIntervalScope | None = None
    model_id: Name | None = None
    device_id: Name | None = None
    key_id: Name | None = None
    hardware_revision: Name | None = None
    firmware_versions: Names = Field(default_factory=list)
    channels: Annotated[list[Channel], Field(max_length=6)] = Field(default_factory=list)
    calibration_sha256: SHA

    @model_validator(mode="after")
    def scope(self):
        if self.cardiac_server_interval and self.purpose != "cardiac_server_interval":
            raise ValueError("Cardiac interval evidence cannot substitute another calibration purpose")
        if self.purpose == "device" and (not all((self.device_id, self.key_id, self.hardware_revision, self.firmware_versions, self.channels)) or self.model_id or self.native_timing or self.optical_geometry):
            raise ValueError("Device calibration requires its exact hardware/firmware/channel scope")
        if self.purpose == "model" and (not self.model_id or any((self.device_id, self.key_id, self.hardware_revision, self.firmware_versions, self.channels, self.native_timing, self.optical_geometry))):
            raise ValueError("Model calibration cannot claim device qualification")
        if self.purpose == "native_timing" and (not self.native_timing or any((self.model_id, self.device_id, self.key_id, self.hardware_revision, self.firmware_versions, self.channels, self.optical_geometry))):
            raise ValueError("Native timing calibration requires only its exact reviewed phone/OS/build/timing tuple")
        if self.purpose == "optical_geometry" and (not self.optical_geometry or any((self.model_id, self.device_id, self.key_id, self.hardware_revision, self.firmware_versions, self.channels, self.native_timing))):
            raise ValueError("Optical geometry requires only its exact reviewed camera scale scope")
        if self.optical_geometry and digest(self.optical_geometry.data()) != self.calibration_sha256:
            raise ValueError("Optical scale calibration hash must cover its exact reviewed scope")
        if self.purpose == "cardiac_server_interval":
            if not self.cardiac_server_interval or any((self.model_id, self.device_id, self.key_id,
                self.hardware_revision, self.firmware_versions, self.channels, self.native_timing, self.optical_geometry)):
                raise ValueError("Cardiac interval requires only its exact reviewed HR acquisition scope")
            if digest(self.cardiac_server_interval.data()) != self.calibration_sha256:
                raise ValueError("Cardiac calibration hash must cover its exact reviewed scope")
        return self


class Retention(Submission):
    policy_id: Name
    study_id: Name
    raw_kinds: Annotated[list[Literal["eye_video", "ecg_waveform", "source_lab_report"]], Field(max_length=3)]
    max_retention_days: Annotated[int, Field(ge=1, le=3650)]
    access_roles: Annotated[list[Name], Field(min_length=1, max_length=32)]
    withdrawal_behavior: Literal["delete_live_data"]
    exceptions: Annotated[list[Name], Field(max_length=32)] = Field(default_factory=list)
    purpose_id: Name
    purpose_text: Annotated[str, Field(min_length=1, max_length=4096)]
    raw_notice_version: Name
    raw_notice_sha256: SHA
    raw_notice_text: Annotated[str, Field(min_length=1, max_length=16384)]

    @model_validator(mode="after")
    def notice_identity(self):
        if len(self.raw_notice_text.encode()) > 16384 or hashlib.sha256(self.raw_notice_text.encode()).hexdigest() != self.raw_notice_sha256:
            raise ValueError("Optional raw purpose notice must match its exact bounded text")
        if len(set(self.raw_kinds)) != len(self.raw_kinds):
            raise ValueError("Duplicate raw retention kind")
        return self


class Qualification(Submission):
    channel: Channel
    configuration_sha256: SHA
    document_sha256: SHA
    reviewed_by: Name
    approval_status: Literal["approved"]
    purpose: Literal["measurement_collection", "qualified_measurement"]
    configuration_registry_id: Name
    configuration_version: Version
    configuration_submitted_sha256: SHA


class SensorMaterial(DTO):
    schema_version: Literal["1.0.0"]
    channel: Literal["cardiac", "ecg", "alcohol"]
    modality: Literal["ppg", "ecg", "breath_alcohol"]
    protocol_version: Literal[1]
    duration_ms: Annotated[int, Field(ge=100, le=3600000)]
    sample_rate_hz: Annotated[float, Field(gt=0, le=10000)]
    raw_unit: Literal["counts", "mV", "mg/L"]
    extractor_version: Name

    @model_validator(mode="after")
    def modality_matches(self):
        if {"cardiac": "ppg", "ecg": "ecg", "alcohol": "breath_alcohol"}[self.channel] != self.modality:
            raise ValueError("Acquisition modality must match the authorized channel")
        if (self.channel == "ecg" and self.raw_unit != "mV" and getattr(self, "adapter_id", None) != "otgd_esp32_adc_v1"
            or self.channel == "alcohol" and self.raw_unit != "mg/L"):
            raise ValueError("Acquisition requires calibrated modality-specific units")
        return self


class ADCMaterial(SensorMaterial):
    adapter_id: Literal["otgd_esp32_adc_v1"]
    channel: Literal["cardiac", "ecg"]
    modality: Literal["ppg", "ecg"]
    duration_ms: Annotated[int, Field(ge=1000, le=120000)]
    end_guard_ms: Annotated[int, Field(ge=10, le=100)]
    sample_rate_hz: Annotated[int, Field(ge=20, le=1000)]
    raw_unit: Literal["counts", "mV"]
    raw_sample_limit: Annotated[int, Field(ge=0, le=1024)]
    raw_encoding: Literal["otgd_ecg_samples_v1"] | None
    extractor_version: Literal["adc_peak_intervals_v1"]
    input_gpio: Annotated[int, Field(ge=1, le=10)]
    contact_gpio: Annotated[int, Field(ge=1, le=48)]
    contact_active_high: bool
    adc_resolution_bits: Literal[12]
    attenuation_db: Literal[11]
    reference_mv: Annotated[float, Field(ge=500, le=5000)]
    gain: Annotated[float, Field(gt=0, le=100000)]
    offset_mv: Annotated[float, Field(ge=-5000, le=5000)]
    threshold_adc: Annotated[int, Field(ge=1, le=4094)]
    minimum_peak_interval_ms: Annotated[int, Field(ge=250, le=2000)]
    maximum_peak_interval_ms: Annotated[int, Field(ge=250, le=2000)]
    minimum_amplitude_adc: Annotated[int, Field(ge=1, le=4095)]

    @model_validator(mode="after")
    def pins_and_intervals(self):
        safe_contacts = {1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,21,38,39,40,41,42,47,48}
        if (self.contact_gpio not in safe_contacts or self.input_gpio == self.contact_gpio
            or self.end_guard_ms >= self.duration_ms
            or self.minimum_peak_interval_ms >= self.maximum_peak_interval_ms
            or self.duration_ms * self.sample_rate_hz / 1000 > 120000
            or self.channel == "cardiac" and self.raw_unit != "counts"
            or self.channel != "ecg" and self.raw_sample_limit != 0
            or (self.raw_sample_limit > 0) != (self.raw_encoding is not None)
            or self.raw_sample_limit > 0 and self.duration_ms * self.sample_rate_hz / 1000 > self.raw_sample_limit):
            raise ValueError("ADC pins, peak intervals and sample budget must match the reviewed hardware")
        return self


class OpticalMaterial(DTO):
    schema_version: Literal["1.0.0"]
    channel: Literal["eyes"]
    duration_ms: Annotated[int, Field(ge=100, le=300000)]
    camera_id: Name
    stimulus_policy_id: Name
    illumination_policy_id: Name
    geometry_id: Name
    frame_rate_hz: Annotated[float, Field(gt=0, le=1000)]
    extractor_version: Name


class GeometryScale(DTO):
    calibration_id: Name
    calibration_sha256: SHA
    pixels_to_mm: Annotated[float, Field(gt=0, le=100)]
    min_diameter_pixels: Annotated[float, Field(gt=0, le=1920)]
    max_diameter_pixels: Annotated[float, Field(gt=0, le=1920)]
    max_uncertainty_mm: Annotated[float, Field(gt=0, le=100)]


class DisplayStimulus(DTO):
    baseline_gray_level: Annotated[int, Field(ge=0, le=255)]
    step_gray_level: Annotated[int, Field(ge=0, le=255)]
    onset_ms: Annotated[int, Field(ge=100, le=10000)]
    step_duration_ms: Annotated[int, Field(ge=100, le=10000)]
    display_brightness_fraction: Annotated[float, Field(gt=0, le=1)]


class OpticalResponse(DTO):
    baseline_window_ms: Annotated[int, Field(ge=100, le=10000)]
    minimum_baseline_frames: Annotated[int, Field(ge=2, le=300)]
    minimum_post_frames: Annotated[int, Field(ge=2, le=300)]
    latency_fraction_threshold: Annotated[float, Field(gt=0, le=1)]
    maximum_latency_ms: Annotated[int, Field(ge=1, le=10000)]


class ExecutableOpticalMaterial(OpticalMaterial):
    duration_ms: Annotated[int, Field(ge=100, le=10000)]
    extractor_version: Literal["otgd-dark-component-v1"]
    lens_facing: Literal["front", "back"]
    capture_width: Annotated[int, Field(ge=64, le=1920)]
    capture_height: Annotated[int, Field(ge=64, le=1920)]
    maximum_frame_gap_ms: Annotated[int, Field(ge=1, le=1000)]
    max_frames: Annotated[int, Field(ge=2, le=300)]
    roi: OpticalROI
    roi_sample_width: Annotated[int, Field(ge=8, le=128)]
    roi_sample_height: Annotated[int, Field(ge=8, le=128)]
    dark_threshold: Annotated[int, Field(ge=0, le=254)]
    min_area_fraction: Annotated[float, Field(gt=0, lt=1)]
    max_area_fraction: Annotated[float, Field(gt=0, lt=1)]
    min_roundness: Annotated[float, Field(ge=0, le=1)]
    min_contrast_delta: Annotated[int, Field(ge=1, le=255)]
    edge_margin_pixels: Annotated[int, Field(ge=1, le=16)]
    minimum_valid_frames: Annotated[int, Field(ge=2, le=300)]
    minimum_valid_frame_fraction: Annotated[float, Field(gt=0, le=1)]
    exposure_mode: Literal["automatic"]
    focus_mode: Literal["continuous_auto"]
    stimulus_mode: Literal["passive_ambient_no_modulation", "reviewed_display_step"]
    scale_basis: Literal["normalized", "millimeters"]
    geometry_scale: GeometryScale | None = None
    display_stimulus: DisplayStimulus | None = None
    response: OpticalResponse | None = None
    raw_encoding: Literal["otgd_eye_roi_v1"]
    expected_output_rotation_degrees: Literal[0, 90, 180, 270]
    expected_sensor_orientation_degrees: Literal[0, 90, 180, 270] | None = None

    @model_validator(mode="after")
    def bounded_frames(self):
        import math

        if (self.capture_width * self.capture_height > 2073600
            or self.roi_sample_width * self.roi_sample_height > 16384
            or self.min_area_fraction >= self.max_area_fraction
            or self.minimum_valid_frames > self.max_frames
            or math.ceil(self.duration_ms * self.frame_rate_hz / 1000) > self.max_frames):
            raise ValueError("Optical bounds must fit the reviewed frame and geometry budget")
        if (self.scale_basis == "millimeters") != (self.geometry_scale is not None):
            raise ValueError("Millimeter features require the reviewed scale and normalized features cannot claim it")
        if self.geometry_scale and self.geometry_scale.min_diameter_pixels >= self.geometry_scale.max_diameter_pixels:
            raise ValueError("Calibrated diameter range must be ordered")
        if (self.stimulus_mode == "reviewed_display_step") != (self.display_stimulus is not None and self.response is not None):
            raise ValueError("Display response needs explicit reviewed stimulus and extraction settings")
        if self.stimulus_mode == "passive_ambient_no_modulation" and (self.display_stimulus or self.response):
            raise ValueError("Passive collection cannot claim a modulated response")
        if self.display_stimulus and (self.display_stimulus.onset_ms + self.display_stimulus.step_duration_ms > self.duration_ms
            or self.display_stimulus.baseline_gray_level == self.display_stimulus.step_gray_level
            or self.response.baseline_window_ms > self.display_stimulus.onset_ms):
            raise ValueError("Stimulus and baseline must fit the reviewed acquisition window")
        return self


class LaboratoryMaterial(DTO):
    schema_version: Literal["1.0.0"]
    channel: Literal["saliva"]
    source: Literal["reference_lab"]
    collection_method_ids: Annotated[list[Name], Field(min_length=1, max_length=64)]
    assay_bases: Annotated[list[Literal["free", "total_after_hydrolysis"]], Field(min_length=1, max_length=2)]
    concentration_bases: Annotated[list[Literal["neat_oral_fluid", "collected_mixture"]], Field(min_length=1, max_length=2)]
    correction_statuses: Annotated[list[Literal["not_corrected", "laboratory_corrected"]], Field(min_length=1, max_length=2)]


class AnalyteLimits(DTO):
    lod_ng_ml: Annotated[float, Field(ge=0)]
    loq_ng_ml: Annotated[float, Field(ge=0)]
    upper_ng_ml: Annotated[float, Field(gt=0)]

    @model_validator(mode="after")
    def ordered(self):
        if not self.lod_ng_ml <= self.loq_ng_ml < self.upper_ng_ml:
            raise ValueError("Assay limits must be ordered and independently reviewed")
        return self


class SalivaReaderMaterial(LaboratoryMaterial):
    source: Literal["prototype_sensor"]
    modality: Literal["saliva_reader"]
    protocol_version: Literal[1]
    duration_ms: Annotated[int, Field(ge=100, le=120000)]
    raw_unit: Literal["ng/mL"]
    extractor_version: Name
    method_ids: Annotated[list[Name], Field(min_length=1, max_length=16)]
    analyte_limits: Annotated[dict[Literal["THC", "OH11_THC", "THC_COOH"], AnalyteLimits], Field(min_length=1, max_length=3)]


class LabMethod(DTO):
    calibration_ids: Annotated[list[Name], Field(min_length=1, max_length=32)]
    instrument_ids: Annotated[list[Name], Field(min_length=1, max_length=32)]


class Method(Submission):
    method_id: Name
    assay_bases: Annotated[list[Literal["free", "total_after_hydrolysis"]], Field(min_length=1, max_length=2)]
    collection_method_ids: Annotated[list[Name], Field(min_length=1, max_length=64)]
    instrument_ids: Annotated[list[Name], Field(min_length=1, max_length=32)]
    laboratory_ids: Annotated[list[Name], Field(min_length=1, max_length=64)]


class Role(Submission):
    account_ref: UUID
    roles: Annotated[list[Literal["lab_import", "lab_report_revision"]], Field(min_length=1, max_length=2)]
    study_ids: Annotated[list[Name], Field(min_length=1, max_length=64)]


def inline_material_schema(schema):
    """Embedded material schemas must not reference another model's $defs root."""
    value = schema.model_json_schema()
    definitions = value.pop("$defs", {})
    def expand(part):
        if isinstance(part, dict):
            if "$ref" in part and part["$ref"].startswith("#/$defs/"):
                return expand(definitions[part["$ref"].split("/")[-1]])
            return {key: expand(child) for key, child in part.items()}
        if isinstance(part, list):
            return [expand(child) for child in part]
        return part
    return expand(value)




class Configuration(Submission):
    configuration_id: Name
    study_id: Name
    protocol_id: Name
    channel: Channel
    sha256: SHA
    material: dict = Field(json_schema_extra={"oneOf": [
        {"const": TASK_MATERIAL},
        inline_material_schema(SensorMaterial), inline_material_schema(ADCMaterial), inline_material_schema(SparkFunMaterial), inline_material_schema(OpticalMaterial), inline_material_schema(ExecutableOpticalMaterial), inline_material_schema(LaboratoryMaterial), inline_material_schema(SalivaReaderMaterial),
    ]})
    qualification_evidence_ref: Name
    retention_policy_id: Name
    max_duration_ms: Annotated[int, Field(ge=100, le=3600000)]
    software_adapter_id: Name
    raw_retention_approved: bool = False
    device_id: Name | None = None
    key_id: Name | None = None
    calibration_id: Name | None = None
    approved_hardware: Names = Field(default_factory=list)
    approved_firmware: Names = Field(default_factory=list)
    supported_phone_models: Names = Field(default_factory=list)
    supported_os_versions: Names = Field(default_factory=list)
    supported_native_builds: Names = Field(default_factory=list)
    optical_safety_ref: Name | None = None
    lab_methods: Annotated[dict[Name, LabMethod], Field(max_length=16)] = Field(default_factory=dict)
    participant_protocol: ParticipantProtocol | None = None

    @model_validator(mode="after")
    def identity(self):
        if self.configuration_id != self.registry_id:
            raise ValueError("Configuration identity mismatch")
        if self.channel == "task":
            from .native_evidence import CONFIG
            if self.material != CONFIG:
                raise ValueError("This task release only implements the exact frozen native configuration")
        else:
            schema = (ExecutableOpticalMaterial if self.software_adapter_id == "optical_roi_v1" else OpticalMaterial) if self.channel == "eyes" else LaboratoryMaterial if self.channel == "saliva" and self.lab_methods else SalivaReaderMaterial if self.channel == "saliva" else ADCMaterial if self.material.get("adapter_id") == "otgd_esp32_adc_v1" else SparkFunMaterial if self.material.get("adapter_id") == "otgd_sparkfun_max32664_v1" else SensorMaterial
            parsed = schema.model_validate(self.material)
            if parsed.channel != self.channel:
                raise ValueError("Configuration material channel mismatch")
            if hasattr(parsed, "duration_ms") and parsed.duration_ms != self.max_duration_ms:
                raise ValueError("Grant duration must match its approved acquisition material")
        if digest(self.material) != self.sha256:
            raise ValueError("Scientific configuration digest must cover its actual typed material")
        if self.channel in ("task", "eyes"):
            if not self.supported_phone_models:
                raise ValueError("Phone configuration requires an explicit supported inventory")
            if self.channel == "eyes" and not self.optical_safety_ref:
                raise ValueError("Optical safety evidence is required")
            if self.software_adapter_id == "optical_roi_v1" and not all((self.supported_os_versions, self.supported_native_builds)):
                raise ValueError("Executable optical capture requires reviewed OS and native build inventories")
        elif self.channel != "saliva" or not self.lab_methods:
            if not all((self.device_id, self.key_id, self.calibration_id, self.approved_hardware, self.approved_firmware)):
                raise ValueError("Sensor configuration requires device, calibration and compatibility limits")
        if self.raw_retention_approved and not self.retention_policy_id:
            raise ValueError("Raw collection requires a retention policy")
        if self.channel in ("cardiac", "ecg") and (self.participant_protocol is None or self.participant_protocol.kind != "cardiac"):
            raise ValueError("Physical cardiac configuration requires reviewed participant instructions")
        if self.software_adapter_id == "reference_lab_import_v1":
            if self.participant_protocol is None or self.participant_protocol.kind != "reference_lab":
                raise ValueError("Reference laboratory collection requires reviewed participant instructions")
            if set(item.id for item in self.participant_protocol.methods) != set(self.material["collection_method_ids"]):
                raise ValueError("Participant collection methods must match approved laboratory material")
        if self.participant_protocol and len(canonical(self.participant_protocol.data())) > 32768:
            raise ValueError("Participant instruction protocol exceeds its bound")
        return self


class Model(Submission):
    model_id: Name
    study_ids: Annotated[list[Name], Field(min_length=1, max_length=64)]
    manifest: dict
    artifact_ref: ArtifactRef
    evaluation_report: EvaluationReport
    quality_policy: QualityPolicy
    co_use_policy: CoUsePolicy
    compatibility_policy: CompatibilityPolicy
    native_timing_calibration_id: Name | None = None
    cardiac_timing_policy: CardiacTimingPolicy | None = None

    @model_validator(mode="after")
    def validated_manifest(self):
        from .domain import validate_schema

        validate_schema(self.manifest, "model_manifest.schema.json")
        if self.registry_id != self.model_id or self.manifest["model_id"] != self.model_id:
            raise ValueError("Model identity mismatch")
        if self.manifest["lifecycle"] != "active_research":
            raise ValueError("Only a fully specified research manifest can be submitted for approval")
        required = ("artifact_sha256", "endpoint_id", "endpoint_definition", "calibration_id", "quality_policy_id", "co_use_policy_id", "validation_report_uri", "compatibility_policy_id")
        if any(not self.manifest.get(k) for k in required) or not self.manifest.get("approval_refs"):
            raise ValueError("Model qualification material is incomplete")
        if not self.manifest.get("allowed_protocol_ids") or self.manifest.get("operating_threshold") is None:
            raise ValueError("Model scope and operating threshold must be explicit")
        from .model_engine import validate_registry_model
        validate_registry_model(self.data())
        if "task" in self.manifest["required_channels"] and not self.native_timing_calibration_id:
            raise ValueError("Task models require independently reviewed native timing calibration")
        if self.cardiac_timing_policy:
            if self.manifest["required_channels"] != ["cardiac_hr"]:
                raise ValueError("Server cardiac interval policy supports heart-rate-only models")
            if ((self.manifest["baseline_mode"] == "personalized") != self.cardiac_timing_policy.allow_baseline_delta
                or self.cardiac_timing_policy.max_interval_ms > self.manifest["max_clock_uncertainty_ms"]):
                raise ValueError("Cardiac interval and personalized baseline must stay within reviewed model scope")
        return self


SCHEMAS = {"study": Study, "device": Device, "calibration": Calibration, "retention": Retention, "qualification": Qualification, "configuration": Configuration, "model": Model, "method": Method, "role": Role, "raw_export": RawExportAuthorization}


def validate_submission(kind, body):
    schema = SCHEMAS.get(kind)
    if schema is None:
        raise ValueError("Unsupported registry kind")
    if len(canonical(body)) > 262144:
        raise ValueError("Registry submission exceeds 256 KiB")
    value = schema.model_validate(body).data()
    # Additive optional scopes do not rewrite the submitted identity of existing
    # versions. Explicit new fields remain part of their full submitted hash.
    optional_addition = {"calibration": "cardiac_server_interval", "model": "cardiac_timing_policy"}.get(kind)
    if optional_addition and optional_addition not in body:
        value.pop(optional_addition, None)
    if kind == "model":
        for field in ("analysis_scope", "cardiac_evidence"):
            if field not in body["evaluation_report"]:
                value["evaluation_report"].pop(field, None)
    if value["expires_at"] <= now():
        raise ValueError("Expired registry material cannot be submitted or released")
    id_field = {"calibration": "calibration_id", "retention": "policy_id", "method": "method_id", "role": "account_ref", "raw_export": "authorization_id"}.get(kind)
    if id_field and value[id_field] != value["registry_id"]:
        raise ValueError("Registry identity mismatch")
    return value


def authority_lock(db, exclusive=False):
    """Consistent outer lock avoids participant/reference/retirement lock inversion."""
    if db.bind.dialect.name == "postgresql":
        function = "pg_advisory_xact_lock" if exclusive else "pg_advisory_xact_lock_shared"
        db.execute(text(f"SELECT {function}(:key)"), {"key": REGISTRY_LOCK})


def released_version(db, kind, registry_id, *, required=True):
    authority_lock(db)
    row = db.scalar(select(RegistryVersion).where(
        RegistryVersion.registry_key == kind + ":" + registry_id,
        RegistryVersion.state == "active",
    ).execution_options(populate_existing=True))
    if row is None or row.body.get("expires_at", 0) <= now() or row.sha256 != digest(row.body):
        if required:
            raise Problem(403, "APPROVED_REGISTRY_VERSION_REQUIRED")
        return None
    try:
        if validate_submission(kind, row.body) != row.body or row.body["registry_id"] != registry_id:
            raise ValueError("Unnormalized registry content")
    except (ValueError, KeyError, TypeError, SchemaError):
        raise Problem(403, "REGISTRY_INTEGRITY_FAILURE") from None
    decisions = list(db.scalars(select(RegistryEvent).where(RegistryEvent.version_id == row.id)
        .order_by(RegistryEvent.revision).limit(4)))
    if (len(decisions) != 3 or [x.state for x in decisions] != ["submitted", "approved", "active"]
        or [x.revision for x in decisions] != [1, 2, 3] or row.revision != 3
        or len({x.principal for x in decisions}) != 3
        or decisions[0].principal != row.submitted_by
        or any(x.submitted_sha256 != row.sha256 for x in decisions)):
        raise Problem(403, "REGISTRY_APPROVAL_HISTORY_INVALID")
    pointer = db.get(Registry, row.registry_key)
    if not pointer or not pointer.active or digest(pointer.body) != row.sha256:
        raise Problem(403, "REGISTRY_INTEGRITY_FAILURE")
    return row


def active_body(db, kind, registry_id):
    return released_version(db, kind, registry_id).body


def cardiac_interval_configuration(db, scope):
    """Resolve every independent authority behind a reviewed HR interval."""
    config = active_body(db, "configuration", scope["configuration_id"])
    material = config["material"]
    if (config["version"] != scope["configuration_version"] or digest(config) != scope["configuration_submitted_sha256"]
        or config["channel"] != "cardiac" or config["device_id"] != scope["device_id"]
        or config["key_id"] != scope["key_id"] or material.get("modality") != "ppg"
        or material.get("adapter_id") != scope["adapter_id"] or material.get("extractor_version") != scope["extractor_version"]
        or not software_supported(config) or scope["hardware_revision"] not in config["approved_hardware"]
        or not set(scope["firmware_versions"]).issubset(config["approved_firmware"])):
        raise Problem(403, "CARDIAC_INTERVAL_SCOPE_MISMATCH")
    validate_dependencies(db, "configuration", config)
    study = active_body(db, "study", config["study_id"])
    device = active_body(db, "device", scope["device_id"] + ":" + scope["key_id"])
    proof = active_body(db, "qualification", config["qualification_evidence_ref"])
    if (study["channels"].get("cardiac") != config["configuration_id"]
        or device["hardware_revision"] != scope["hardware_revision"]
        or device["firmware_version"] not in scope["firmware_versions"]
        or proof["purpose"] != "qualified_measurement"):
        raise Problem(403, "CARDIAC_INTERVAL_SCOPE_MISMATCH")
    return config


def validate_dependencies(db, kind, body):
    """No implicit creation/review of a referenced approval, device or policy."""
    if kind == "configuration":
        study = active_body(db, "study", body["study_id"])
        policy = active_body(db, "retention", body["retention_policy_id"])
        proof = active_body(db, "qualification", body["qualification_evidence_ref"])
        if study["protocol_id"] != body["protocol_id"] or policy["study_id"] != body["study_id"]:
            raise Problem(403, "REGISTRY_SCOPE_MISMATCH")
        if (proof["channel"] != body["channel"] or proof["configuration_sha256"] != body["sha256"]
            or proof["configuration_registry_id"] != body["registry_id"]
            or proof["configuration_version"] != body["version"]
            or proof["configuration_submitted_sha256"] != digest(body)):
            raise Problem(403, "QUALIFICATION_CONFIGURATION_MISMATCH")
        if body.get("device_id"):
            device = active_body(db, "device", body["device_id"] + ":" + body["key_id"])
            calibration = active_body(db, "calibration", body["calibration_id"])
            if (calibration["purpose"] != "device" or body["protocol_id"] not in device["approved_protocol_ids"]
                or device["hardware_revision"] not in body["approved_hardware"]
                or device["firmware_version"] not in body["approved_firmware"]
                or calibration["device_id"] != device["device_id"]
                or calibration["key_id"] != device["key_id"]
                or calibration["hardware_revision"] != device["hardware_revision"]
                or device["firmware_version"] not in calibration["firmware_versions"]
                or body["channel"] not in calibration["channels"]):
                raise Problem(403, "DEVICE_CALIBRATION_MISMATCH")
        if body["channel"] == "eyes" and body["software_adapter_id"] == "optical_roi_v1":
            material = body["material"]
            scale = material.get("geometry_scale")
            if scale:
                calibration = active_body(db, "calibration", scale["calibration_id"])
                geometry = calibration.get("optical_geometry")
                if (calibration["purpose"] != "optical_geometry" or not geometry
                    or calibration["calibration_sha256"] != scale["calibration_sha256"]
                    or any(material[key] != geometry[key] for key in (
                        "camera_id", "lens_facing", "capture_width", "capture_height",
                        "expected_output_rotation_degrees", "roi", "roi_sample_width", "roi_sample_height", "extractor_version"))
                    or any(scale[key] != geometry[key] for key in (
                        "pixels_to_mm", "min_diameter_pixels", "max_diameter_pixels", "max_uncertainty_mm"))
                    or not set(body["supported_phone_models"]).issubset(geometry["phone_models"])
                    or not set(body["supported_os_versions"]).issubset(geometry["os_versions"])
                    or not set(body["supported_native_builds"]).issubset(geometry["native_builds"])):
                    raise Problem(403, "OPTICAL_GEOMETRY_CALIBRATION_MISMATCH")
        for method in body.get("lab_methods", {}).values():
            for calibration_id in method["calibration_ids"]:
                active_body(db, "calibration", calibration_id)
        for method_id, approval in body.get("lab_methods", {}).items():
            method = active_body(db, "method", method_id)
            if any(id not in method["instrument_ids"] for id in approval["instrument_ids"]):
                raise Problem(403, "METHOD_INSTRUMENT_MISMATCH")
        if body["channel"] == "saliva" and not body.get("lab_methods"):
            material = body["material"]
            for method_id in material["method_ids"]:
                method = active_body(db, "method", method_id)
                if (not set(material["collection_method_ids"]).issubset(method["collection_method_ids"])
                    or not set(material["assay_bases"]).issubset(method["assay_bases"])):
                    raise Problem(403, "METHOD_ASSAY_SCOPE_MISMATCH")
    elif kind == "retention":
        active_body(db, "study", body["study_id"])
    elif kind == "calibration":
        if body["purpose"] == "device":
            device = active_body(db, "device", body["device_id"] + ":" + body["key_id"])
            if device["hardware_revision"] != body["hardware_revision"] or device["firmware_version"] not in body["firmware_versions"]:
                raise Problem(403, "DEVICE_CALIBRATION_MISMATCH")
        elif body["purpose"] == "cardiac_server_interval":
            cardiac_interval_configuration(db, body["cardiac_server_interval"])
    elif kind == "model":
        calibration = active_body(db, "calibration", body["manifest"]["calibration_id"])
        if calibration["purpose"] != "model" or calibration["model_id"] != body["model_id"]:
            raise Problem(403, "MODEL_CALIBRATION_MISMATCH")
        if body.get("native_timing_calibration_id"):
            timing = active_body(db, "calibration", body["native_timing_calibration_id"])
            if timing["purpose"] != "native_timing":
                raise Problem(403, "NATIVE_TIMING_CALIBRATION_REQUIRED")
        cardiac_config = None
        if body.get("cardiac_timing_policy"):
            policy = body["cardiac_timing_policy"]
            timing = active_body(db, "calibration", policy["calibration_id"])
            if (timing["purpose"] != "cardiac_server_interval" or not timing.get("cardiac_server_interval")
                or policy["max_interval_ms"] > timing["cardiac_server_interval"]["maximum_interval_ms"]):
                raise Problem(403, "CARDIAC_INTERVAL_CALIBRATION_REQUIRED")
            cardiac_config = cardiac_interval_configuration(db, timing["cardiac_server_interval"])
            report = body["evaluation_report"].get("cardiac_evidence")
            cardiac_scope = timing["cardiac_server_interval"]
            qualification = active_body(db, "qualification", cardiac_config["qualification_evidence_ref"])
            device = active_body(db, "device", cardiac_scope["device_id"] + ":" + cardiac_scope["key_id"])
            if not report or any(report[key] != expected for key, expected in (
                ("cardiac_timing_policy_sha256", digest(policy)),
                ("calibration_registry_sha256", digest(timing)),
                ("calibration_scope_sha256", digest(cardiac_scope)),
                ("qualification_registry_sha256", digest(qualification)),
                ("device_registry_sha256", digest(device)),
                ("configuration_submitted_sha256", digest(cardiac_config)))):
                raise Problem(403, "CARDIAC_EVALUATION_SCOPE_MISMATCH")
        for study_id in body["study_ids"]:
            study = active_body(db, "study", study_id)
            if study["protocol_id"] not in body["manifest"]["allowed_protocol_ids"]:
                raise Problem(403, "MODEL_PROTOCOL_MISMATCH")
            if cardiac_config is not None and (study["study_id"] != cardiac_config["study_id"]
                or study["channels"].get("cardiac") != cardiac_config["configuration_id"]):
                raise Problem(403, "CARDIAC_INTERVAL_SCOPE_MISMATCH")
    elif kind == "role":
        from .db import Account
        if db.get(Account, body["account_ref"]) is None:
            raise Problem(403, "ROLE_ACCOUNT_UNKNOWN")
        for study_id in body["study_ids"]:
            study = active_body(db, "study", study_id)
            if body["account_ref"] not in study["account_refs"]:
                raise Problem(403, "ROLE_STUDY_MEMBERSHIP_REQUIRED")
    elif kind == "raw_export":
        from .raw_export import validate_dependencies as validate_raw_export_dependencies
        validate_raw_export_dependencies(db, body)


def event(db, row, previous, principal, reason, request_id):
    db.add(RegistryEvent(version_id=row.id, revision=row.revision, previous_state=previous,
        state=row.state, principal=principal, reason=reason, submitted_sha256=row.sha256,
        request_id=request_id))


def submit(db, kind, body, principal, *, request_id=None):
    value = validate_submission(kind, body)
    authority_lock(db, exclusive=True)
    key = kind + ":" + value["registry_id"]
    id = digest([key, value["version"]])
    if db.get(RegistryVersion, id):
        raise Problem(409, "REGISTRY_VERSION_EXISTS")
    pointer = db.get(Registry, key)
    if not pointer:
        db.add(Registry(id=key, kind=kind, body={}, active=False))
    row = RegistryVersion(id=id, registry_key=key, version=value["version"], kind=kind,
        body=value, sha256=digest(value), submitted_by=principal, submitted_at=now(),
        state="submitted", revision=1)
    db.add(row)
    db.flush()
    event(db, row, None, principal, "Submitted immutable evidence", request_id or uid())
    return view(row)


def transition(db, kind, registry_id, version, action, principal, reason, expected_revision, *, request_id=None):
    if not isinstance(reason, str) or not 1 <= len(reason) <= 1024 or not reason.strip():
        raise ValueError("A bounded nonempty decision reason is required")
    authority_lock(db, exclusive=True)
    key = kind + ":" + registry_id
    pointer = db.scalar(select(Registry).where(Registry.id == key).with_for_update())
    row = db.scalar(select(RegistryVersion).where(RegistryVersion.id == digest([key, version])).with_for_update())
    if not row or not pointer:
        raise Problem(404, "REGISTRY_VERSION_NOT_FOUND")
    if row.revision != expected_revision:
        raise Problem(412, "REGISTRY_REVISION_CONFLICT", revision=row.revision)
    target = {"approve": "approved", "release": "active", "retire": "retired", "revoke": "revoked"}.get(action)
    allowed = {"approve": ("submitted",), "release": ("approved",), "retire": ("active",), "revoke": ("submitted", "approved", "active")}
    if target is None or row.state not in allowed[action]:
        raise Problem(409, "REGISTRY_STATE_CONFLICT")
    if action in ("approve", "release"):
        if principal == row.submitted_by:
            raise Problem(403, "INDEPENDENT_REVIEW_REQUIRED")
        validate_submission(row.kind, row.body)
        if action == "release":
            approval = db.scalar(select(RegistryEvent).where(RegistryEvent.version_id == row.id, RegistryEvent.state == "approved"))
            if not approval or approval.submitted_sha256 != row.sha256:
                raise Problem(403, "APPROVAL_EVIDENCE_MISSING")
            if principal == approval.principal:
                raise Problem(403, "INDEPENDENT_RELEASE_REQUIRED")
            validate_dependencies(db, row.kind, row.body)
            previous = db.scalar(select(RegistryVersion).where(RegistryVersion.registry_key == key, RegistryVersion.state == "active").with_for_update())
            if previous:
                previous.state = "retired"
                previous.revision += 1
                event(db, previous, "active", principal, "Superseded by approved version " + version, request_id or uid())
            pointer.body = row.body
            pointer.active = True
    previous_state = row.state
    row.state = target
    row.revision += 1
    if previous_state == "active" and target in ("revoked", "retired"):
        pointer.active = False
    event(db, row, previous_state, principal, reason, request_id or uid())
    return view(row)


def view(row):
    return {"version_id": row.id, "registry_key": row.registry_key, "version": row.version,
        "state": row.state, "revision": row.revision, "submitted_sha256": row.sha256,
        "submitted_by": row.submitted_by, "submitted_at": iso(row.submitted_at),
        "expires_at": iso(row.body["expires_at"]), "expired": row.body["expires_at"] <= now(),
        "effective_state": "expired" if row.body["expires_at"] <= now() and row.state == "active" else row.state,
        "submitted_body": row.body}


def history(db, kind, registry_id, *, limit=100):
    rows = list(db.scalars(select(RegistryVersion).where(RegistryVersion.registry_key == kind + ":" + registry_id).order_by(RegistryVersion.submitted_at.desc(), RegistryVersion.id).limit(limit + 1)))
    if len(rows) > limit:
        raise Problem(413, "REGISTRY_HISTORY_LIMIT")
    result = []
    for row in rows:
        decisions = list(db.scalars(select(RegistryEvent).where(RegistryEvent.version_id == row.id).order_by(RegistryEvent.revision)))
        result.append({**view(row), "decisions": [{"revision": x.revision, "previous_state": x.previous_state, "state": x.state, "principal": x.principal, "reason": x.reason, "submitted_sha256": x.submitted_sha256, "request_id": x.request_id, "created_at": iso(x.created)} for x in decisions]})
    return {"items": result}


def qualified_binding(db, account, config, binding=None):
    """Check current signed binding and complete calibration tuple, never UUID possession."""
    from .db import Record

    if not config.get("device_id"):
        return None
    device = active_body(db, "device", config["device_id"] + ":" + config["key_id"])
    if account.id not in device["account_refs"]:
        raise Problem(403, "DEVICE_ACCOUNT_NOT_AUTHORIZED")
    validate_dependencies(db, "configuration", config)
    if binding is None:
        candidates = list(db.scalars(select(Record).where(Record.account_id == account.id,
            Record.generation == account.generation, Record.kind == "binding").limit(101)))
        if len(candidates) > 100:
            raise Problem(403, "DEVICE_BINDING_LIMIT")
    else:
        candidates = [binding]
    for row in candidates:
        body = row.body
        if (row.account_id == account.id and row.generation == account.generation
            and body.get("state") == "active" and body.get("device_id") == device["device_id"]
            and body.get("key_id") == device["key_id"]
            and body.get("hardware_revision") == device["hardware_revision"]
            and body.get("firmware_version") == device["firmware_version"]):
            return row
    raise Problem(403, "DEVICE_BINDING_REQUIRED")


def capture_configuration(db, account, check, channel, configuration_id=None, configuration_hash=None):
    from .domain import qualification

    config = qualification(db, account, check, channel, configuration_id, configuration_hash)
    released_version(db, "study", check.study_id)
    released_version(db, "configuration", config["registry_id"])
    validate_dependencies(db, "configuration", config)
    qualified_binding(db, account, config)
    if channel == "ecg" and (config.get("participant_protocol") or {}).get("operating_scope") == "human_participant":
        raise Problem(403, "OPERATING_STATE_VERIFIER_UNIMPLEMENTED")
    if not software_supported(config):
        raise Problem(403, "HUMAN_ADAPTER_UNIMPLEMENTED")
    return config


def software_supported(config):
    channel, adapter = config["channel"], config["software_adapter_id"]
    if adapter not in SOFTWARE_ADAPTERS.get(channel, set()):
        return False
    if (channel in ("cardiac", "ecg") or adapter == "reference_lab_import_v1") and not config.get("participant_protocol"):
        return False
    if channel == "ecg" and (config.get("participant_protocol") or {}).get("operating_scope") == "human_participant":
        # Current acquisition hardware has no independently observed USB,
        # charging or cable-state verifier. Participant declarations cannot
        # manufacture the whole-system electrical gate.
        return False
    if adapter == "otgd_signed_reader_v1":
        # A wire decoder cannot manufacture an instrument acquisition driver.
        material = config["material"]
        if material.get("adapter_id") == "otgd_esp32_adc_v1" and channel == "ecg" and material.get("raw_unit") != "mV":
            return False
        return material.get("adapter_id") in PHYSICAL_DRIVERS.get(channel, set())
    return True


def raw_recording_supported(config, kind):
    material = config["material"]
    if kind == "eye_video":
        return (config["channel"] == "eyes" and config["software_adapter_id"] == "optical_roi_v1"
            and material.get("raw_encoding") == "otgd_eye_roi_v1")
    if kind == "ecg_waveform":
        return (config["channel"] == "ecg" and config["software_adapter_id"] == "otgd_signed_reader_v1"
            and material.get("adapter_id") == "otgd_esp32_adc_v1"
            and material.get("raw_unit") == "mV"
            and material.get("raw_encoding") == "otgd_ecg_samples_v1"
            and 0 < material.get("raw_sample_limit", 0) <= 1024)
    return False


def acquisition_context(db, account, check, config):
    from .domain import record

    context = record(db, account, "context", check.id)
    if not context or context.sha256 != digest(context.body):
        raise Problem(403, "FROZEN_CAPTURE_CONTEXT_REQUIRED")
    references = context.body.get("configuration_refs", [])
    if not any(ref.get("id") == config["configuration_id"]
        and ref.get("version") == config["version"] and ref.get("sha256") == config["sha256"]
        for ref in references):
        raise Problem(403, "CONFIGURATION_CONTEXT_MISMATCH")
    if context.body.get("protocol_id") != check.protocol_id:
        raise Problem(403, "CONFIGURATION_CONTEXT_MISMATCH")
    return context


def capture_binding_context(context, binding, boot_id=None):
    """A fresh reader start cannot change the frozen device association or boot."""
    for reference in context.body.get("device_associations", []):
        if (reference.get("binding_id") == binding.body["binding_id"]
            and all(reference.get(key) == binding.body.get(key) for key in (
                "device_id", "hardware_revision", "firmware_version"))
            and (boot_id is None or reference.get("boot_id") == boot_id)):
            return reference
    raise Problem(403, "DEVICE_CONTEXT_MISMATCH")


def validate_reader_start_identity(boot_id, device_nonce):
    from uuid import UUID as ParsedUUID
    try:
        if str(ParsedUUID(boot_id)) != boot_id or not re.fullmatch(r"[A-Za-z0-9_-]{43}", device_nonce):
            raise ValueError()
        decoded = base64.urlsafe_b64decode(device_nonce + "=")
        if len(decoded) != 32 or base64.urlsafe_b64encode(decoded).decode().rstrip("=") != device_nonce:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise Problem(403, "READER_START_IDENTITY_INVALID") from None


def validate_reader_projection(db, config, projection):
    """Signed vendor data must still match the independently approved method scope."""
    material = config["material"]
    if config["channel"] in ("cardiac", "ecg"):
        if projection.get("modality") != material["modality"] or (
            config["channel"] == "ecg" and projection.get("sample_rate_hz") != material["sample_rate_hz"]):
            raise Problem(422, "READER_CONFIGURATION_MISMATCH")
    elif config["channel"] == "saliva" and not config["lab_methods"]:
        sample = projection["sample"]
        if sample["collection_method_id"] not in material["collection_method_ids"]:
            raise Problem(422, "READER_CONFIGURATION_MISMATCH")
        for measurement in projection["saliva"]:
            if measurement["qualifier"] == "not_measured":
                continue
            limits = material["analyte_limits"].get(measurement["analyte"])
            method = active_body(db, "method", measurement["method_id"])
            if (measurement["method_id"] not in material["method_ids"]
                or measurement["assay_basis"] not in material["assay_bases"]
                or measurement["concentration_basis"] not in material["concentration_bases"]
                or measurement["correction_status"] not in material["correction_statuses"]
                or measurement["calibration_id"] != config["calibration_id"]
                or measurement["instrument_id"] not in method["instrument_ids"]
                or limits != measurement["limits"]):
                raise Problem(422, "READER_CONFIGURATION_MISMATCH")


def started_capture(db, account, check, attempt, config):
    """Acquired real evidence must settle under the exact online start authority."""
    from .db import Record

    context = acquisition_context(db, account, check, config)
    authorizations = list(db.scalars(select(Record).where(
        Record.account_id == account.id, Record.generation == account.generation,
        Record.parent_id == check.id, Record.kind == "authorization").limit(129)))
    if len(authorizations) > 128:
        raise Problem(403, "CAPTURE_AUTHORIZATION_LIMIT")
    for row in authorizations:
        body = row.body
        if (body.get("attempt_id") == attempt["attempt_id"] and body.get("state") == "started"
            and body.get("configuration_id") == config["configuration_id"]
            and body.get("configuration_version") == config["version"]
            and body.get("configuration_hash") == config["sha256"]
            and body.get("configuration_submitted_sha256") == digest(config)
            and body.get("capture_context_sha256") == context.sha256):
            from datetime import datetime
            try:
                start = datetime.fromisoformat(attempt["started_at"].replace("Z", "+00:00")).timestamp()
                end = datetime.fromisoformat(attempt["ended_at"].replace("Z", "+00:00")).timestamp()
                if (start < body["server_started_epoch"] - 2 or end < start
                    or end > body["server_started_epoch"] + config["max_duration_ms"] / 1000 + 2):
                    raise ValueError()
            except (ValueError, TypeError, KeyError):
                raise Problem(422, "CAPTURE_TIME_OUTSIDE_AUTHORIZATION") from None
            from .participant_acquisition import validate_instruction_evidence
            validate_instruction_evidence(db, account, check, attempt, config, row)
            return row
    raise Problem(403, "FRESH_CAPTURE_START_REQUIRED")


def validate_optical_attempt(db, account, check, attempt, config, authorization=None):
    """Bind independently recomputed optical evidence to the accepted online run."""
    from .optical_evidence import validate_optical

    raw = attempt["component_metadata"].get("native_result")
    if not isinstance(raw, dict):
        raise Problem(422, "OPTICAL_EVIDENCE_REQUIRED")
    authorization = authorization or started_capture(db, account, check, attempt, config)
    if (raw.get("run_id") != attempt["record_id"]
        or raw.get("authorization_id") != authorization.body["authorization_id"]
        or raw.get("started_at") != attempt["started_at"]
        or raw.get("ended_at") != attempt["ended_at"]):
        raise Problem(422, "OPTICAL_CAPTURE_IDENTITY_MISMATCH")
    return validate_optical(raw, attempt["component_metadata"]["projection"], config)


def channel_capabilities(db, account):
    from .db import Check
    from .domain import NOTICE_SHA, qualification

    results = {channel: {"available": False, "authorization_available": False,
        "software_available": channel in SOFTWARE_ADAPTERS, "reason_codes": [], "configurations": []}
        for channel in CHANNELS}
    if account.state != "active" or account.notice != NOTICE_SHA:
        reason = "ACCOUNT_NOT_ACTIVE" if account.state != "active" else "NOTICE_ACK_REQUIRED"
        for value in results.values():
            value["reason_codes"] = [reason]
        return results
    authority_lock(db)
    studies = list(db.scalars(select(RegistryVersion).where(RegistryVersion.kind == "study",
        RegistryVersion.state == "active").order_by(RegistryVersion.id).limit(101)))
    if len(studies) > 100:
        for value in results.values():
            value["reason_codes"] = ["STUDY_CAPABILITY_LIMIT"]
        return results
    for submitted in studies:
        study = submitted.body
        if account.id not in study["account_refs"]:
            continue
        for channel in CHANNELS:
            config_id = study["channels"].get(channel)
            if not config_id:
                continue
            value = results[channel]
            try:
                active_body(db, "study", study["study_id"])
                version = released_version(db, "configuration", config_id)
                config = qualification(db, account, Check(study_id=study["study_id"], protocol_id=study["protocol_id"]), channel, config_id)
                validate_dependencies(db, "configuration", config)
                qualified_binding(db, account, config)
                value["authorization_available"] = True
                adapter = config["software_adapter_id"]
                if channel == "ecg" and (config.get("participant_protocol") or {}).get("operating_scope") == "human_participant":
                    raise Problem(403, "OPERATING_STATE_VERIFIER_UNIMPLEMENTED")
                if not software_supported(config):
                    raise Problem(403, "HUMAN_ADAPTER_UNIMPLEMENTED")
                value["available"] = True
                value["configurations"].append({"study_id": study["study_id"], "protocol_id": study["protocol_id"],
                    "configuration_id": config_id, "configuration_hash": config["sha256"],
                    "configuration_version": version.version, "submitted_sha256": version.sha256,
                    "expires_at": iso(min(config["expires_at"], study["expires_at"])),
                    "supported_phone_models": config["supported_phone_models"],
                    "supported_os_versions": config["supported_os_versions"],
                    "supported_native_builds": config["supported_native_builds"],
                    "software_adapter_id": adapter,
                    "participant_protocol": config.get("participant_protocol"),
                    "participant_protocol_sha256": digest(config["participant_protocol"]) if config.get("participant_protocol") else None})
            except Problem as error:
                value["reason_codes"].append(error.code)
    for value in results.values():
        value["reason_codes"] = [] if value["available"] else sorted(set(value["reason_codes"])) or ["NO_QUALIFIED_CONFIGURATION"]
    return results
