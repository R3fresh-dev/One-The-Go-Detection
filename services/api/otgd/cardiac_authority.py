"""Conservative server custody intervals for separately qualified HR-only models.

No device UTC, waveform cadence or physical onset is reconstructed. The signed
projection stays unchanged. External independent qualification of the protected
reader's fresh-grant behavior and the server UTC error is still required.
"""

import base64
import hashlib
import math
from decimal import ROUND_CEILING, Decimal
from typing import Annotated, Literal

from pydantic import Field, FiniteFloat, ValidationError

from .canonical import digest
from .db import SystemState, iso, now
from .domain import record, verify_signature
from .dto import DTO, SHA, UUID, Name
from .errors import Problem

METHOD = "server_issue_to_attestation_receipt_v1"
FLAGS = {
    "otgd_esp32_adc_v1": {"SERVER_WALL_ANCHOR_UNQUALIFIED", "ADC_PEAK_INTERVALS_V1"},
    "otgd_sparkfun_max32664_v1": {"SERVER_WALL_ANCHOR_UNQUALIFIED", "SPARKFUN_SENSOR_BPM_V1",
        "HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED"},
}
EXTRACTORS = {
    "otgd_esp32_adc_v1": "adc_peak_intervals_v1",
    "otgd_sparkfun_max32664_v1": "sparkfun_sensor_bpm_v1",
}


class CardiacTimingPolicy(DTO):
    method: Literal["server_issue_to_attestation_receipt_v1"]
    calibration_id: Name
    max_interval_ms: Annotated[int, Field(ge=100, le=120000)]
    allow_baseline_delta: bool


class IntervalEvidence(DTO):
    schema_version: Literal["1.0.0"]
    method: Literal["server_issue_to_attestation_receipt_v1"]
    account_ref: UUID
    data_generation: Annotated[int, Field(ge=1, le=9007199254740991)]
    session_id: UUID
    attempt_id: UUID
    authorization_id: UUID
    attestation_id: UUID
    binding_id: UUID
    boot_id: Name
    device_id: Name
    key_id: Name
    hardware_revision: Name
    firmware_version: Name
    adapter_id: Literal["otgd_esp32_adc_v1", "otgd_sparkfun_max32664_v1"]
    extractor_version: Literal["adc_peak_intervals_v1", "sparkfun_sensor_bpm_v1"]
    configuration_id: Name
    configuration_version: Name
    configuration_sha256: SHA
    configuration_submitted_sha256: SHA
    calibration_registry_sha256: SHA
    calibration_scope_sha256: SHA
    qualification_registry_sha256: SHA
    device_registry_sha256: SHA
    policy_sha256: SHA
    snapshot_sha256: SHA
    capture_context_sha256: SHA
    evidence_manifest_sha256: SHA
    authorization_sha256: SHA
    attestation_sha256: SHA
    issued_epoch: Annotated[FiniteFloat, Field(gt=0)]
    received_epoch: Annotated[FiniteFloat, Field(gt=0)]
    target_epoch: Annotated[FiniteFloat, Field(gt=0)]
    server_utc_error_ms: Annotated[FiniteFloat, Field(ge=0, le=1000)]
    signed_acquisition_duration_us: Annotated[int, Field(gt=0, le=60000000)] | None
    maximum_monotonic_rate_error_ppm: Annotated[int, Field(ge=0, le=10000)] | None
    interval_ms: Annotated[int, Field(gt=0, le=120000)]
    acquisition_bound_ms: Annotated[int, Field(gt=0, le=3600000)]
    preserved_quality_flags: Annotated[list[Name], Field(min_length=2, max_length=3)]


class CardiacAuthority(DTO):
    schema_version: Literal["1.0.0"]
    policy: CardiacTimingPolicy
    policy_sha256: SHA
    calibration_registry_sha256: SHA
    current: IntervalEvidence
    baseline: IntervalEvidence | None


def policy_for(body):
    policy = CardiacTimingPolicy.model_validate(body["cardiac_timing_policy"])
    if (body["manifest"]["required_channels"] != ["cardiac_hr"]
        or policy.allow_baseline_delta != (body["manifest"]["baseline_mode"] == "personalized")):
        raise Problem(403, "CARDIAC_HR_ONLY_SCOPE_REQUIRED")
    return policy


def validate_features(body, artifact):
    policy_for(body)
    if artifact.feature_names != ["cardiac.heart_rate_bpm"]:
        raise Problem(403, "CARDIAC_HR_ONLY_SCOPE_REQUIRED")


def bounds(issued, received, target, error_ms, evaluated):
    """Exact decimal arithmetic over the durable wire values; round outwards."""
    issue, receipt, origin, error, current = (Decimal(str(v))
        for v in (issued, received, target, error_ms, evaluated))
    lower, upper = issue - error / 1000, receipt + error / 1000
    def ceiling(value):
        return int(value.to_integral_value(rounding=ROUND_CEILING))
    return {"lower": lower, "upper": upper,
        "interval_ms": ceiling((receipt - issue) * 1000 + 2 * error),
        "acquisition_bound_ms": ceiling((receipt - origin) * 1000 + 2 * error),
        "delivery_bound_ms": ceiling((current - issue) * 1000 + 2 * error)}


def validate_signed_duration(item, calculated):
    """SDK ticks need reviewed rate error; unsigned ADC transport is unusable."""
    duration, rate = item.signed_acquisition_duration_us, item.maximum_monotonic_rate_error_ppm
    if item.adapter_id == "otgd_esp32_adc_v1":
        if duration is not None or rate is not None:
            raise ValueError()
        return
    if duration is None or rate is None:
        raise ValueError()
    # Compare exact endpoints rather than their rounded integer upper bound.
    server_window_us = (calculated["upper"] - calculated["lower"]) * 1000000
    if Decimal(duration) * 1000000 > server_window_us * (1000000 + Decimal(rate)):
        raise ValueError()


def validate_interval(snapshot, body, evidence, *, baseline=False, evaluated_epoch=None):
    """Recompute numerical gates without rewriting any original snapshot field."""
    from .model_engine import utc_timestamp

    try:
        item = IntervalEvidence.model_validate(evidence)
        policy = policy_for(body)
        evaluated = now() if evaluated_epoch is None else evaluated_epoch
        if not math.isfinite(evaluated):
            raise ValueError()
        target = utc_timestamp(snapshot["target_at"])
        calculated = bounds(item.issued_epoch, item.received_epoch, target, item.server_utc_error_ms, evaluated)
        validate_signed_duration(item, calculated)
        width, span, delivery = (calculated[k] for k in ("interval_ms", "acquisition_bound_ms", "delivery_bound_ms"))
        expected = FLAGS[item.adapter_id]
        component = snapshot["cardiac"]
        if (item.snapshot_sha256 != digest(snapshot) or item.session_id != snapshot["session_id"]
            or item.account_ref != snapshot["subject_ref"] or item.policy_sha256 != digest(policy.data())
            or item.target_epoch != target
            or not target <= item.issued_epoch < item.received_epoch <= evaluated
            or item.interval_ms != width or item.acquisition_bound_ms != span
            or width > policy.max_interval_ms or width > body["manifest"]["max_clock_uncertainty_ms"]
            or span > body["manifest"]["max_acquisition_span_ms"]
            or not baseline and delivery > body["manifest"]["max_delivery_delay_ms"]
            or component["status"] != "valid" or component["source"] != "prototype_sensor"
            or component["modality"] != "ppg" or component["ecg_status"] != "not_collected"
            or component["ecg_rmssd_ms"] is not None
            or item.extractor_version != EXTRACTORS[item.adapter_id]
            or len(component["quality_flags"]) != len(expected)
            or set(component["quality_flags"]) != expected
            or item.preserved_quality_flags != component["quality_flags"]):
            raise ValueError()
        return item.data()
    except (ValidationError, ValueError, KeyError, TypeError, OverflowError):
        raise Problem(422, "CARDIAC_SERVER_INTERVAL_INVALID") from None


def _owned_record(db, account, kind, id, session_id):
    value = record(db, account, kind, id)
    if not value or value.parent_id != session_id or value.sha256 != digest(value.body):
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED")
    return value


def resolve(db, account, check, body, manifest):
    """Current released authority + reverified original signed custody evidence."""
    if body.get("cardiac_timing_policy") is None:
        return None
    from .capture_signing import DOMAIN, KEY_STATE, StartGrant
    from .config import settings
    from .domain import NOTICE_SHA
    from .dto import Attestation
    from .model_engine import utc_timestamp
    from .operator_governance import (
        CardiacServerIntervalScope,
        acquisition_context,
        capture_binding_context,
        capture_configuration,
        released_version,
        started_capture,
    )

    policy = policy_for(body)
    if (account.state != "active" or account.notice != NOTICE_SHA
        or account.generation != check.generation or check.mode != "controlled_research"):
        raise Problem(403, "STUDY_UNAUTHORIZED")
    selected = manifest.body.get("selected", {}).get("cardiac")
    attempt = _owned_record(db, account, "attempt", selected or "", check.id)
    projection = attempt.body.get("component_metadata", {}).get("projection")
    if projection != check.snapshot["cardiac"] or attempt.body.get("status") != "valid":
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED")
    config = capture_configuration(db, account, check, "cardiac",
        attempt.body["configuration_id"], attempt.body["configuration_hash"])
    context = acquisition_context(db, account, check, config)
    calibration = released_version(db, "calibration", policy.calibration_id)
    if calibration.body["purpose"] != "cardiac_server_interval":
        raise Problem(403, "CARDIAC_TIMING_QUALIFICATION_REQUIRED")
    scope = CardiacServerIntervalScope.model_validate(calibration.body["cardiac_server_interval"]).data()
    device = released_version(db, "device", config["device_id"] + ":" + config["key_id"])
    qualification = released_version(db, "qualification", config["qualification_evidence_ref"])
    material = config["material"]
    if (calibration.body["calibration_sha256"] != digest(scope)
        or qualification.body["purpose"] != "qualified_measurement"
        or any(scope[key] != actual for key, actual in (
            ("device_id", device.body["device_id"]), ("key_id", device.body["key_id"]),
            ("hardware_revision", device.body["hardware_revision"]),
            ("adapter_id", material.get("adapter_id")), ("extractor_version", material["extractor_version"]),
            ("configuration_id", config["configuration_id"]), ("configuration_version", config["version"]),
            ("configuration_submitted_sha256", digest(config)), ("channel", "cardiac"), ("modality", "ppg"),
            ("behavior", "follows_current_signed_grant"), ("timing_method", METHOD)))
        or device.body["firmware_version"] not in scope["firmware_versions"]
        or policy.max_interval_ms > scope["maximum_interval_ms"]):
        raise Problem(403, "CARDIAC_TIMING_QUALIFICATION_REQUIRED")
    report_evidence = body["evaluation_report"].get("cardiac_evidence")
    if (body["evaluation_report"].get("analysis_scope") != "cardiac_hr_only" or not report_evidence
        or any(report_evidence.get(key) != actual for key, actual in (
            ("cardiac_timing_policy_sha256", digest(policy.data())),
            ("calibration_registry_sha256", calibration.sha256), ("calibration_scope_sha256", digest(scope)),
            ("qualification_registry_sha256", qualification.sha256), ("device_registry_sha256", device.sha256),
            ("configuration_submitted_sha256", digest(config))))):
        raise Problem(403, "CARDIAC_EVALUATION_SCOPE_MISMATCH")
    authorization = started_capture(db, account, check, attempt.body, config)
    if authorization.sha256 != digest(authorization.body):
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED")
    value = authorization.body
    token = value.get("server_start", {})
    anchor = db.get(SystemState, KEY_STATE)
    try:
        grant = StartGrant.model_validate(token["grant"]).data()
        if (not anchor or token["domain"] != DOMAIN or token["key_id"] != anchor.body["key_id"]
            or anchor.body["environment"] != grant["environment"]
            or hashlib.sha256(base64.b64decode(anchor.body["public_key_spki"], validate=True)).hexdigest()
                != anchor.body["public_key_sha256"]):
            raise ValueError()
        verify_signature(anchor.body["public_key_spki"], token["signature"], DOMAIN, grant)
        if (iso(value["server_started_epoch"]) != grant["issued_at"]
            or value["server_started_at"] != grant["issued_at"]
            or utc_timestamp(grant["expires_at"]) - utc_timestamp(grant["issued_at"]) != 60
            or any(grant[key] != actual for key, actual in (
                ("owner_ref", account.id), ("data_generation", account.generation), ("session_id", check.id),
                ("attempt_id", attempt.body["attempt_id"]), ("authorization_id", value["authorization_id"]),
                ("device_id", device.body["device_id"]), ("device_key_id", device.body["key_id"]),
                ("boot_id", value["device_boot_id"]), ("binding_id", value["binding_id"]),
                ("configuration_id", config["configuration_id"]), ("configuration_hash", config["sha256"]),
                ("configuration_submitted_sha256", digest(config)), ("configuration_version", config["version"]),
                ("capture_context_sha256", context.sha256), ("channel", "cardiac"),
                ("environment", settings().environment), ("configuration_max_duration_ms", config["max_duration_ms"]),
                ("raw_recording_permission", value.get("raw_recording_permission")),
                ("participant_protocol_sha256", value.get("participant_protocol_sha256")),
                ("instruction_receipt_id", value.get("instruction_receipt_id"))))):
            raise ValueError()
    except (ValidationError, ValueError, KeyError, TypeError):
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED") from None
    binding = record(db, account, "binding", grant["binding_id"])
    if (not binding or binding.sha256 != digest(binding.body) or binding.body.get("state") != "active"
        or any(binding.body.get(key) != device.body[key] for key in (
            "device_id", "key_id", "hardware_revision", "firmware_version"))):
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED")
    capture_binding_context(context, binding, grant["boot_id"])
    refs = attempt.body.get("attestation_refs", [])
    if len(refs) != 1:
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED")
    attestation = _owned_record(db, account, "attestation", refs[0], check.id)
    try:
        attested = Attestation.model_validate(attestation.body).data()
    except ValidationError:
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED") from None
    envelope = attested["envelope"]
    expected_payload = projection
    signed_duration = None
    if material["adapter_id"] == "otgd_sparkfun_max32664_v1":
        from .vendor_evidence import validate_ppg
        raw = attempt.body["component_metadata"].get("ppg_evidence")
        validate_ppg(projection, raw, material)
        expected_payload = {"projection": projection, "ppg_evidence": raw}
        signed_duration = raw["acquisition_ended_monotonic_us"] - raw["acquisition_started_monotonic_us"]
    if (attested["attestation_id"] != refs[0]
        or attested["normalized_payload"] != expected_payload
        or envelope["payload_sha256"] != digest(expected_payload)
        or any(envelope[key] != actual for key, actual in (
            ("environment", grant["environment"]), ("owner_ref", account.id),
            ("data_generation", account.generation), ("session_id", check.id),
            ("attempt_id", attempt.body["attempt_id"]), ("authorization_id", grant["authorization_id"]),
            ("binding_id", grant["binding_id"]), ("device_id", device.body["device_id"]),
            ("key_id", device.body["key_id"]), ("boot_id", grant["boot_id"]),
            ("configuration_hash", config["sha256"])))):
        raise Problem(403, "CARDIAC_CAPTURE_PROOF_REQUIRED")
    verify_signature(device.body["public_key_spki"], attested["signature"], "OTGD-CAPTURE-v1\n", envelope)
    issue, receipt = utc_timestamp(grant["issued_at"]), attestation.created
    target = utc_timestamp(check.snapshot["target_at"])
    calculated = bounds(issue, receipt, target, scope["server_utc_error_ms"], now())
    evidence = {"schema_version": "1.0.0", "method": METHOD, "account_ref": account.id,
        "data_generation": account.generation, "session_id": check.id, "attempt_id": attempt.body["attempt_id"],
        "authorization_id": grant["authorization_id"], "attestation_id": refs[0], "binding_id": grant["binding_id"],
        "boot_id": grant["boot_id"], "device_id": device.body["device_id"], "key_id": device.body["key_id"],
        "hardware_revision": device.body["hardware_revision"], "firmware_version": device.body["firmware_version"],
        "adapter_id": material["adapter_id"], "extractor_version": material["extractor_version"],
        "configuration_id": config["configuration_id"], "configuration_version": config["version"],
        "configuration_sha256": config["sha256"], "configuration_submitted_sha256": digest(config),
        "calibration_registry_sha256": calibration.sha256, "calibration_scope_sha256": digest(scope),
        "qualification_registry_sha256": qualification.sha256, "device_registry_sha256": device.sha256,
        "policy_sha256": digest(policy.data()), "snapshot_sha256": digest(check.snapshot),
        "capture_context_sha256": context.sha256, "evidence_manifest_sha256": manifest.sha256,
        "authorization_sha256": authorization.sha256, "attestation_sha256": attestation.sha256,
        "issued_epoch": issue, "received_epoch": receipt, "target_epoch": target,
        "server_utc_error_ms": scope["server_utc_error_ms"],
        "signed_acquisition_duration_us": signed_duration,
        "maximum_monotonic_rate_error_ppm": scope["maximum_monotonic_rate_error_ppm"],
        "interval_ms": calculated["interval_ms"], "acquisition_bound_ms": calculated["acquisition_bound_ms"],
        "preserved_quality_flags": projection["quality_flags"]}
    # Historical baselines bypass only delivery freshness, never interval/scope.
    return validate_interval(check.snapshot, body, evidence, baseline=True)


def build_authority(body, current, baseline=None):
    if current is None:
        return None
    policy = policy_for(body)
    value = CardiacAuthority(schema_version="1.0.0", policy=policy,
        policy_sha256=digest(policy.data()), calibration_registry_sha256=current["calibration_registry_sha256"],
        current=IntervalEvidence.model_validate(current),
        baseline=IntervalEvidence.model_validate(baseline) if baseline is not None else None)
    if baseline is not None:
        same = ("account_ref", "data_generation", "device_id", "key_id", "hardware_revision", "firmware_version",
            "adapter_id", "extractor_version", "configuration_id", "configuration_version",
            "configuration_submitted_sha256", "calibration_registry_sha256", "calibration_scope_sha256",
            "qualification_registry_sha256", "device_registry_sha256", "policy_sha256", "server_utc_error_ms")
        same += ("maximum_monotonic_rate_error_ppm",)
        if not policy.allow_baseline_delta or any(current[key] != baseline[key] for key in same):
            raise Problem(422, "BASELINE_NOT_COMPATIBLE")
    elif policy.allow_baseline_delta:
        raise Problem(422, "BASELINE_NOT_COMPATIBLE")
    return value.data()


def validate_baseline(snapshot, body, current, baseline):
    """Use the oldest possible baseline observation and latest current target."""
    from .model_engine import utc_timestamp

    build_authority(body, current, baseline)
    if baseline is None:
        raise Problem(422, "BASELINE_NOT_COMPATIBLE")
    current_target = Decimal(str(utc_timestamp(snapshot["target_at"])))
    error = Decimal(str(current["server_utc_error_ms"])) / 1000
    earlier = bounds(baseline["issued_epoch"], baseline["received_epoch"],
        baseline["target_epoch"], baseline["server_utc_error_ms"], now())
    maximum = body["quality_policy"].get("max_baseline_age_ms")
    if (earlier["upper"] >= current_target - error or maximum is None
        or (current_target + error - earlier["lower"]) * 1000 > maximum):
        raise Problem(422, "BASELINE_NOT_COMPATIBLE")


def validate_result_companion(value):
    """Offline proof consistency, not a substitute for live registry admission."""
    try:
        authority = value["model_execution"]["authority_manifest"]
        if "cardiac_authority" not in authority:
            return
        companion = CardiacAuthority.model_validate(authority["cardiac_authority"]).data()
        current = companion["current"]
        body = {"manifest": authority["model_manifest"], "cardiac_timing_policy": companion["policy"]}
        policy = policy_for(body)
        from .model_engine import utc_timestamp
        target, evaluated = utc_timestamp(value["target_at"]), utc_timestamp(value["evaluated_at"])
        computed = bounds(current["issued_epoch"], current["received_epoch"], target,
            current["server_utc_error_ms"], evaluated)
        validate_signed_duration(IntervalEvidence.model_validate(current), computed)
        if (companion["policy_sha256"] != digest(policy.data())
            or current["policy_sha256"] != companion["policy_sha256"]
            or current["calibration_registry_sha256"] != companion["calibration_registry_sha256"]
            or current["snapshot_sha256"] != value["input_sha256"]
            or current["session_id"] != value["session_id"] or current["target_epoch"] != target
            or current["capture_context_sha256"] != value["model_execution"]["capture_context_sha256"]
            or current["evidence_manifest_sha256"] != value["model_execution"]["evidence_manifest_sha256"]
            or current["extractor_version"] != EXTRACTORS[current["adapter_id"]]
            or not target <= current["issued_epoch"] < current["received_epoch"] <= evaluated
            or current["interval_ms"] != computed["interval_ms"]
            or current["acquisition_bound_ms"] != computed["acquisition_bound_ms"]
            or current["interval_ms"] > min(policy.max_interval_ms, body["manifest"]["max_clock_uncertainty_ms"])
            or current["acquisition_bound_ms"] > body["manifest"]["max_acquisition_span_ms"]
            or computed["delivery_bound_ms"] > body["manifest"]["max_delivery_delay_ms"]
            or len(current["preserved_quality_flags"]) != len(FLAGS[current["adapter_id"]])
            or set(current["preserved_quality_flags"]) != FLAGS[current["adapter_id"]]):
            raise ValueError()
        build_authority(body, current, companion["baseline"])
        baseline = companion["baseline"]
        if baseline is not None:
            if baseline["snapshot_sha256"] != value["model_execution"]["baseline_sha256"]:
                raise ValueError()
            previous = bounds(baseline["issued_epoch"], baseline["received_epoch"], baseline["target_epoch"],
                baseline["server_utc_error_ms"], evaluated)
            validate_signed_duration(IntervalEvidence.model_validate(baseline), previous)
            if (baseline["interval_ms"] != previous["interval_ms"]
                or baseline["acquisition_bound_ms"] != previous["acquisition_bound_ms"]
                or baseline["interval_ms"] > min(policy.max_interval_ms, body["manifest"]["max_clock_uncertainty_ms"])
                or baseline["acquisition_bound_ms"] > body["manifest"]["max_acquisition_span_ms"]
                or not baseline["target_epoch"] <= baseline["issued_epoch"] < baseline["received_epoch"] <= evaluated
                or previous["upper"] >= Decimal(str(target)) - Decimal(str(current["server_utc_error_ms"])) / 1000):
                raise ValueError()
    except (ValidationError, ValueError, KeyError, TypeError, OverflowError):
        raise Problem(422, "MODEL_EXECUTION_PROOF_MISMATCH") from None
