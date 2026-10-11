"""Independent numerical/refusal tests, not physical or live registry approval.

These literal custody records exercise the interval validator only. The separate
HTTP tests must prove registry, signature, immutable receipt and owner admission.
No device wall time, confidence probability or sensor onset is established here.
"""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from otgd import cardiac_authority as c
from otgd.canonical import canonical, digest
from otgd.db import iso
from otgd.errors import Problem


OWNER = "11111111-1111-4111-8111-111111111111"
SESSION = "22222222-2222-4222-8222-222222222222"
OTHER_SESSION = "33333333-3333-4333-8333-333333333333"
EPOCH = 1800000000.0
EXPECTED_FLAGS = {
    "otgd_esp32_adc_v1": ["ADC_PEAK_INTERVALS_V1", "SERVER_WALL_ANCHOR_UNQUALIFIED"],
    "otgd_sparkfun_max32664_v1": ["HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED",
        "SERVER_WALL_ANCHOR_UNQUALIFIED", "SPARKFUN_SENSOR_BPM_V1"],
}


def custody(adapter="otgd_esp32_adc_v1"):
    """A deliberately fictional, structural interval without live authority."""
    flags = EXPECTED_FLAGS[adapter][:]
    snapshot = {
        "subject_ref": OWNER,
        "session_id": SESSION,
        "target_at": iso(EPOCH - 1),
        "clock_uncertainty_ms": None,
        "capture_completed_at": iso(EPOCH),
        "acquisition_span_ms": None,
        "cardiac": {
            "status": "valid", "source": "prototype_sensor", "modality": "ppg",
            "ecg_status": "not_collected", "ecg_rmssd_ms": None,
            "heart_rate_bpm": 75.0, "quality_flags": flags,
        },
    }
    body = {
        "manifest": {
            "required_channels": ["cardiac_hr"], "baseline_mode": "population",
            "max_clock_uncertainty_ms": 12000, "max_acquisition_span_ms": 12000,
            "max_delivery_delay_ms": 12000,
        },
        "cardiac_timing_policy": {
            "method": c.METHOD, "calibration_id": "fictional-interval-scope",
            "max_interval_ms": 12000, "allow_baseline_delta": False,
        },
        "quality_policy": {"max_baseline_age_ms": 10000},
    }
    evidence = {
        "schema_version": "1.0.0", "method": c.METHOD,
        "account_ref": OWNER, "data_generation": 1, "session_id": SESSION,
        "attempt_id": OTHER_SESSION, "authorization_id": OTHER_SESSION,
        "attestation_id": OTHER_SESSION, "binding_id": OTHER_SESSION,
        "boot_id": OTHER_SESSION, "device_id": "fictional-reader", "key_id": "fictional-key",
        "hardware_revision": "fictional-hardware", "firmware_version": "fictional-firmware",
        "adapter_id": adapter,
        "extractor_version": "adc_peak_intervals_v1" if adapter == "otgd_esp32_adc_v1" else "sparkfun_sensor_bpm_v1",
        "configuration_id": "fictional-config", "configuration_version": "v1",
        "issued_epoch": EPOCH, "received_epoch": EPOCH + 0.2, "target_epoch": EPOCH - 1,
        "server_utc_error_ms": 1.0, "interval_ms": 202, "acquisition_bound_ms": 1202,
        "signed_acquisition_duration_us": None if adapter == "otgd_esp32_adc_v1" else 200000,
        "maximum_monotonic_rate_error_ppm": None if adapter == "otgd_esp32_adc_v1" else 0,
        "preserved_quality_flags": flags,
    }
    for key in (
        "configuration_sha256", "configuration_submitted_sha256", "calibration_registry_sha256",
        "calibration_scope_sha256", "qualification_registry_sha256", "device_registry_sha256",
        "capture_context_sha256", "evidence_manifest_sha256", "authorization_sha256", "attestation_sha256",
    ):
        evidence[key] = "a" * 64
    evidence.update(snapshot_sha256=digest(snapshot), policy_sha256=digest(body["cardiac_timing_policy"]))
    return snapshot, body, evidence


def test_epoch_precision_uses_durable_decimal_values_and_never_rewrites_device_evidence():
    snapshot, body, evidence = custody()
    before = canonical(snapshot)
    # At this real-sized epoch, binary floating subtraction previously widened
    # one path to 203ms and another to 202ms for the same durable wire values.
    expected = c.bounds(EPOCH, EPOCH + 0.2, EPOCH - 1, 1.0, EPOCH + 0.3)
    assert expected["interval_ms"] == 202
    assert expected["acquisition_bound_ms"] == 1202
    assert expected["delivery_bound_ms"] == 302
    body["manifest"].update(max_clock_uncertainty_ms=202, max_acquisition_span_ms=1202, max_delivery_delay_ms=302)
    assert c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3) == evidence
    assert canonical(snapshot) == before
    assert snapshot["clock_uncertainty_ms"] is None


@pytest.mark.parametrize("field,value", [
    ("max_clock_uncertainty_ms", 201), ("max_acquisition_span_ms", 1201), ("max_delivery_delay_ms", 301),
])
def test_each_conservative_limit_refuses_one_millisecond_below_required_bound(field, value):
    snapshot, body, evidence = custody()
    body["manifest"][field] = value
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3)


def test_signed_sdk_duration_respects_exact_reviewed_rate_limit_not_a_rounded_millisecond():
    snapshot, body, evidence = custody("otgd_sparkfun_max32664_v1")
    # Exact 202000us custody upper window, with reviewed maximum 10000ppm:
    # 204020 device us / 1.01 = 202000 physical us. Equality is admitted.
    evidence.update(signed_acquisition_duration_us=204020, maximum_monotonic_rate_error_ppm=10000)
    c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3)
    evidence["signed_acquisition_duration_us"] += 1
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3)

    # This real epoch's wire receipt is exactly .200001 after issue. Outward
    # integer-ms width is 203, but exact duration upper bound is 202001us.
    evidence.update(received_epoch=EPOCH + 0.200001, interval_ms=203,
        acquisition_bound_ms=1203, maximum_monotonic_rate_error_ppm=0,
        signed_acquisition_duration_us=202001)
    c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3)
    evidence["signed_acquisition_duration_us"] = 202002
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3)


@pytest.mark.parametrize("adapter,duration,rate", [
    ("otgd_esp32_adc_v1", 200000, None),
    ("otgd_esp32_adc_v1", None, 0),
    ("otgd_esp32_adc_v1", 200000, 10000),
    ("otgd_sparkfun_max32664_v1", None, 0),
    ("otgd_sparkfun_max32664_v1", 200000, None),
    ("otgd_sparkfun_max32664_v1", 200000, 10001),
    ("otgd_sparkfun_max32664_v1", 200000, True),
    ("otgd_sparkfun_max32664_v1", True, 0),
])
def test_unsigned_adc_or_missing_unreviewed_sdk_clock_cannot_supply_signed_duration(adapter, duration, rate):
    snapshot, body, evidence = custody(adapter)
    evidence.update(signed_acquisition_duration_us=duration, maximum_monotonic_rate_error_ppm=rate)
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3)


@pytest.mark.parametrize("adapter", ["otgd_esp32_adc_v1", "otgd_sparkfun_max32664_v1"])
@pytest.mark.parametrize("fault", ["CONTACT_LOST", "ADC_SATURATED", "SAMPLE_DROPS",
    "PPG_IO_OR_VERSION_ERROR", "PPG_CAPTURE_OVERRUN", "UNKNOWN_FIRMWARE_FAULT"])
def test_matching_rehashed_snapshot_and_companion_never_whitelist_a_device_fault(adapter, fault):
    snapshot, body, evidence = custody(adapter)
    # Preserve and rehash the fault, so refusal cannot merely come from a stale
    # digest. Timing authority permits only the exact descriptive flag set.
    snapshot["cardiac"]["quality_flags"][0] = fault
    evidence["preserved_quality_flags"] = snapshot["cardiac"]["quality_flags"][:]
    evidence["snapshot_sha256"] = digest(snapshot)
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 0.3)


def test_fresh_client_end_time_and_baseline_mode_cannot_hide_an_old_delivery():
    snapshot, body, evidence = custody()
    snapshot["capture_completed_at"] = iso(EPOCH + 600)
    evidence["snapshot_sha256"] = digest(snapshot)
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, body, evidence, evaluated_epoch=EPOCH + 600)
    # Historical validation deliberately bypasses only delivery age; it still
    # applies the original full interval and acquisition-span bounds.
    assert c.validate_interval(snapshot, body, evidence, baseline=True, evaluated_epoch=EPOCH + 600) == evidence
    evidence["interval_ms"] = 1
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, body, evidence, baseline=True, evaluated_epoch=EPOCH + 600)


def test_baseline_age_uses_oldest_possible_observation_and_both_utc_margins():
    snapshot, body, current = custody()
    body["manifest"]["baseline_mode"] = "personalized"
    body["cardiac_timing_policy"]["allow_baseline_delta"] = True
    current["policy_sha256"] = digest(body["cardiac_timing_policy"])
    baseline = deepcopy(current)
    baseline.update(session_id=OTHER_SESSION, snapshot_sha256="b" * 64,
        issued_epoch=EPOCH - 10, received_epoch=EPOCH - 9.8, target_epoch=EPOCH - 11)
    # Current target is epoch-1, oldest possible prior observation epoch-10-.001:
    # upper current target epoch-1+.001 gives the independently literal 9002ms.
    body["quality_policy"]["max_baseline_age_ms"] = 9002
    c.validate_baseline(snapshot, body, current, baseline)
    body["quality_policy"]["max_baseline_age_ms"] = 9001
    with pytest.raises(Problem, match="BASELINE_NOT_COMPATIBLE"):
        c.validate_baseline(snapshot, body, current, baseline)


def test_baseline_interval_touching_current_target_uncertainty_is_not_prior():
    snapshot, body, current = custody()
    body["manifest"]["baseline_mode"] = "personalized"
    body["cardiac_timing_policy"]["allow_baseline_delta"] = True
    current["policy_sha256"] = digest(body["cardiac_timing_policy"])
    baseline = deepcopy(current)
    baseline.update(session_id=OTHER_SESSION, snapshot_sha256="b" * 64,
        target_epoch=EPOCH - 3, issued_epoch=EPOCH - 2, received_epoch=EPOCH - 1.002,
        interval_ms=1000, acquisition_bound_ms=2000)
    with pytest.raises(Problem, match="BASELINE_NOT_COMPATIBLE"):
        c.validate_baseline(snapshot, body, current, baseline)


@pytest.mark.parametrize("channels,features", [
    (["cardiac_hr", "ecg"], ["cardiac.heart_rate_bpm"]),
    (["cardiac_hr"], ["cardiac.heart_rate_bpm", "cardiac.ecg_rmssd_ms"]),
    (["cardiac_hr"], ["cardiac.heart_rate_bpm", "profile.age_years"]),
])
def test_interval_exception_cannot_extend_to_another_channel_or_artifact_feature(channels, features):
    _, body, _ = custody()
    body["manifest"]["required_channels"] = channels
    with pytest.raises(Problem, match="CARDIAC_HR_ONLY_SCOPE_REQUIRED"):
        c.validate_features(body, SimpleNamespace(feature_names=features))
