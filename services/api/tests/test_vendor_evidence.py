"""Synthetic vendor DTOs exercise custody only, never physiology or approvals."""
from copy import deepcopy
import pytest
from pydantic import ValidationError
from otgd.errors import Problem
from otgd.vendor_evidence import SDK_COMMIT, SparkFunMaterial, PPGEvidence, validate_ppg


def material():
    return {"schema_version": "1.0.0", "channel": "cardiac", "modality": "ppg", "adapter_id": "otgd_sparkfun_max32664_v1",
        "protocol_version": 1, "duration_ms": 3000, "end_guard_ms": 100, "poll_interval_ms": 50,
        "i2c_timeout_ms": 10, "i2c_address": 85, "bus_frequency_hz": 100000, "sda_gpio": 11,
        "scl_gpio": 12, "reset_gpio": 5, "mfio_gpio": 6, "algorithm_mode": 1,
        "sdk_commit": SDK_COMMIT, "sdk_version": "1.1", "extractor_version": "sparkfun_sensor_bpm_v1",
        "warmup_ms": 1000, "max_no_data_ms": 500, "minimum_valid_samples": 2, "minimum_confidence": 80,
        "minimum_heart_rate_bpm": 40, "maximum_heart_rate_bpm": 200,
        "hub_firmware_major": 1, "hub_firmware_minor": 2, "hub_firmware_revision": 3}


def evidence():
    return {"schema_version": "1.0.0", "adapter_id": "otgd_sparkfun_max32664_v1", "sdk_commit": SDK_COMMIT,
        "sdk_version": "1.1", "algorithm_mode": 1, "hub_firmware": {"major": 1, "minor": 2, "revision": 3},
        "configured_sensor_rate_hz": 100, "actual_sensor_cadence_hz": None, "host_poll_interval_ms": 50,
        "sample_timestamp_source": "host_i2c_receive_unqualified_sensor_time",
        "acquisition_started_monotonic_us": 1000000, "acquisition_ended_monotonic_us": 3900000,
        "observed_samples": 2, "valid_samples": 2, "invalid_samples": 0, "missed_poll_intervals": 0,
        "fifo_empty_polls": 0, "fifo_backlog_peak": 2, "sensor_dropped_samples": None,
        "last_observation": {"sequence": 1, "host_received_monotonic_us": 3850000, "heart_rate_bpm": 75,
            "confidence_percent": 90, "finger_status": 3, "extended_status": None}}


def projection():
    return {"status": "valid", "source": "prototype_sensor", "modality": "ppg", "heart_rate_bpm": 75.0,
        "ecg_rmssd_ms": None, "ecg_status": "not_collected", "sample_rate_hz": None, "raw_artifact_id": None,
        "quality_flags": ["SERVER_WALL_ANCHOR_UNQUALIFIED", "SPARKFUN_SENSOR_BPM_V1", "HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED"]}


def test_exact_typed_vendor_material_and_latest_vendor_observation_are_verified():
    assert SparkFunMaterial.model_validate(material()).data() == material()
    assert validate_ppg(projection(), evidence(), material()) == evidence()
    assert evidence()["actual_sensor_cadence_hz"] is None
    with pytest.raises(Problem, match="VENDOR_MEASUREMENT_INVALID"):
        validate_ppg({**projection(), "heart_rate_bpm": 74.0}, evidence(), material())


@pytest.mark.parametrize("changes", [{"i2c_address": 86}, {"sda_gpio": 10}, {"sdk_commit": "a" * 40},
    {"i2c_timeout_ms": 21}, {"warmup_ms": 3000}, {"max_no_data_ms": 49},
    {"minimum_heart_rate_bpm": 200}, {"minimum_valid_samples": 257}, {"duration_ms": 60001}])
def test_unimplemented_pin_sdk_or_duration_settings_are_rejected(changes):
    with pytest.raises(ValidationError):
        SparkFunMaterial.model_validate({**material(), **changes})


@pytest.mark.parametrize("changes", [{"valid_samples": 1}, {"invalid_samples": 1}, {"missed_poll_intervals": 1},
    {"acquisition_ended_monotonic_us": 4000001}, {"algorithm_mode": 2}, {"host_poll_interval_ms": 100},
    {"hub_firmware": {"major": 9, "minor": 2, "revision": 3}}, {"configured_sensor_rate_hz": None},
    {"observed_samples": 3}, {"actual_sensor_cadence_hz": 100}, {"sensor_dropped_samples": 0}])
def test_signed_counts_do_not_bypass_actual_configuration_or_quality(changes):
    with pytest.raises(Problem):
        validate_ppg(projection(), {**evidence(), **changes}, material())


@pytest.mark.parametrize("changes", [{"finger_status": 0}, {"confidence_percent": 79}, {"confidence_percent": 255},
    {"heart_rate_bpm": 300}, {"host_received_monotonic_us": 3900000}, {"host_received_monotonic_us": 1000000},
    {"sequence": 2}, {"ir_count": 123}])
def test_contact_vendor_bounds_and_no_raw_count_persistence(changes):
    raw = evidence()
    raw["last_observation"] = {**raw["last_observation"], **changes}
    with pytest.raises(Problem):
        validate_ppg(projection(), raw, material())


def test_invalid_preconfiguration_and_actual_version_failure_remain_truthful():
    raw = {**evidence(), "hub_firmware": None, "configured_sensor_rate_hz": None,
        "acquisition_ended_monotonic_us": 1000000, "observed_samples": 0, "valid_samples": 0,
        "last_observation": None}
    invalid = {**projection(), "status": "invalid", "heart_rate_bpm": None}
    assert validate_ppg(invalid, raw, material()) == raw
    raw = deepcopy(evidence())
    raw["hub_firmware"]["major"] = 9
    raw["last_observation"]["confidence_percent"] = 255
    raw["last_observation"]["extended_status"] = -128
    assert PPGEvidence.model_validate(raw).last_observation.extended_status == -128
    assert validate_ppg(invalid, raw, material()) == raw
    with pytest.raises(Problem, match="INVALID_VENDOR_HEART_RATE"):
        validate_ppg({**invalid, "heart_rate_bpm": 75}, raw, material())


def test_actual_production_cpp_factory_fixture_has_no_raw_counts_and_matches_typed_semantics():
    import json
    from otgd.config import ROOT
    value = json.loads((ROOT / "firmware/tests/fixtures/sparkfun-ppg-result-v1.json").read_text())
    config = {**material(), "duration_ms": 5000, "minimum_confidence": 90,
        "max_no_data_ms": 1000, "hub_firmware_major": 10, "hub_firmware_minor": 1,
        "hub_firmware_revision": 0}
    assert validate_ppg(value["projection"], value["ppg_evidence"], config) == value["ppg_evidence"]
    assert value["projection"]["heart_rate_bpm"] == 75
    assert "ir_count" not in value["ppg_evidence"]["last_observation"]
    assert value["ppg_evidence"]["actual_sensor_cadence_hz"] is None
    # A mean of 73 and 75 is not the selected latest vendor output.
    with pytest.raises(Problem, match="VENDOR_MEASUREMENT_INVALID"):
        validate_ppg({**value["projection"], "heart_rate_bpm": 74}, value["ppg_evidence"], config)


def test_http_sdk_wrapper_is_owned_prepared_and_signature_bound(client, account, monkeypatch):
    import base64
    import json
    from uuid import uuid4
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from otgd.canonical import canonical, digest
    from otgd.config import ROOT
    from otgd.db import factory, iso, engine
    from otgd import operator_governance as governance
    from .conftest import headers
    from .governance_fixture import (STUDY, PROTOCOL, DEVICE, KEY, CALIBRATION, approve,
        configuration, study, retention, device, calibration, proof, acknowledge_cardiac)
    from .test_operator_governance import consent

    if engine().dialect.name == "postgresql":
        from otgd.participant_migration import migration_006_cardiac_interval_anchors
        with engine().begin() as connection:
            migration_006_cardiac_interval_anchors(connection)
    monkeypatch.setitem(governance.PHYSICAL_DRIVERS, "cardiac", {"otgd_sparkfun_max32664_v1"})
    private = ec.generate_private_key(ec.SECP256R1())
    config_material = {**material(), "duration_ms": 5000, "minimum_confidence": 90,
        "max_no_data_ms": 1000, "hub_firmware_major": 10, "hub_firmware_minor": 1, "hub_firmware_revision": 0}
    config = configuration("cardiac", material=config_material, sha256=digest(config_material), max_duration_ms=5000,
        software_adapter_id="otgd_signed_reader_v1", device_id=DEVICE, key_id=KEY, calibration_id=CALIBRATION,
        approved_hardware=["fixture-hw"], approved_firmware=["fixture-fw"])
    with factory().begin() as db:
        for kind, body in (("study", study(account, {"cardiac": config["registry_id"]})), ("retention", retention()),
            ("device", device(account, private)), ("calibration", calibration()),
            ("qualification", proof("cardiac", config)), ("configuration", config)):
            approve(db, kind, body)
        config = governance.active_body(db, "configuration", config["registry_id"])
    consent(client, study(account))
    challenge = client.post("/v1/device-bindings/challenges", headers=headers(), json={"device_id": DEVICE, "key_id": KEY}).json()
    signature = base64.b64encode(private.sign(b"OTGD-BIND-v1\n" + canonical(challenge["transcript"]), ec.ECDSA(hashes.SHA256()))).decode()
    binding = client.post("/v1/device-bindings", headers=headers(), json={"challenge_id": challenge["challenge_id"], "signature": signature}).json()
    sid, aid, rid, attid, boot = [str(uuid4()) for _ in range(5)]
    assert client.post("/v1/sessions", headers=headers(), json={"session_id": sid, "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL}).status_code == 201
    context = {"schema_version": "1.0.0", "session_id": sid, "context_confirmed_at": iso(), "profile_version_id": None,
        "profile_snapshot_sha256": "a" * 64, "history_snapshot_sha256": "b" * 64, "protocol_id": PROTOCOL,
        "configuration_refs": [{"id": config["configuration_id"], "version": "v1", "sha256": config["sha256"], "scope": "measurement_collection"}],
        "baseline_refs": [], "device_associations": [{**{key: binding[key] for key in ("binding_id", "device_id", "hardware_revision", "firmware_version")}, "boot_id": boot, "clock_evidence_ref": None}]}
    assert client.put(f"/v1/sessions/{sid}/context", headers=headers(revision=0), json=context).status_code == 200
    attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid, "record_id": rid, "component": "cardiac",
        "supersedes_attempt_id": None, "status": "started", "source": "prototype_sensor", "started_at": iso(), "ended_at": None,
        "configuration_id": config["configuration_id"], "configuration_hash": config["sha256"], "quality_flags": [],
        "component_metadata": {"modality": "ppg"}, "artifact_refs": [], "attestation_refs": []}
    assert client.put(f"/v1/sessions/{sid}/attempts/{aid}", headers=headers(revision=0), json=attempt).status_code == 200
    instructions = acknowledge_cardiac(client, sid, attempt, config)
    authorization = client.post(f"/v1/sessions/{sid}/capture-authorizations", headers=headers(), json={"attempt_id": aid,
        "channel": "cardiac", "binding_id": binding["binding_id"], "device_id": DEVICE, "configuration_id": config["configuration_id"],
        "configuration_hash": config["sha256"], "instruction_receipt_id": instructions["instruction_receipt_id"]}).json()
    start_response = client.post(f"/v1/sessions/{sid}/capture-authorizations/{authorization['authorization_id']}/start", headers=headers(), json={
        "attempt_id": aid, "device_boot_id": boot, "device_nonce": base64.urlsafe_b64encode(b"S" * 32).decode().rstrip("=")})
    assert start_response.status_code == 200, start_response.text
    started = start_response.json()
    value = json.loads((ROOT / "firmware/tests/fixtures/sparkfun-ppg-result-v1.json").read_text())
    value["projection"].update(acquisition_config_id=config["configuration_id"], started_at=started["server_started_at"], ended_at=started["server_started_at"])
    terminal = {**attempt, "status": "valid", "started_at": started["server_started_at"], "ended_at": started["server_started_at"],
        "quality_flags": value["projection"]["quality_flags"], "attestation_refs": [attid], "component_metadata": {
            "modality": "ppg", "armed_at": attempt["started_at"], "instruction_receipt": instructions, **value}}
    response = client.put(f"/v1/sessions/{sid}/attempts/{aid}", headers=headers(revision=1), json=terminal)
    assert response.status_code == 200, response.text
    envelope = {"schema_version": "1.0.0", "environment": "test", "owner_ref": account, "data_generation": 1,
        "session_id": sid, "attempt_id": aid, "authorization_id": authorization["authorization_id"], "binding_id": binding["binding_id"],
        "device_id": DEVICE, "key_id": KEY, "boot_id": boot, "sequence": 1, "configuration_hash": config["sha256"], "payload_sha256": digest(value)}
    signature = base64.b64encode(private.sign(b"OTGD-CAPTURE-v1\n" + canonical(envelope), ec.ECDSA(hashes.SHA256()))).decode()
    attestation = {"attestation_id": attid, "envelope": envelope, "signature": signature, "normalized_payload": value}
    forged = deepcopy(attestation)
    forged["normalized_payload"]["ppg_evidence"]["last_observation"]["confidence_percent"] = 99
    assert client.post(f"/v1/sessions/{sid}/attestations", headers=headers(), json=forged).status_code == 422
    accepted = client.post(f"/v1/sessions/{sid}/attestations", headers=headers(), json=attestation)
    assert accepted.status_code == 201, accepted.text
