"""Fictional reviewed timing scopes exercise authority, not human qualification."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from otgd import operator_governance as g
from otgd.canonical import digest
from otgd.db import factory
from otgd.errors import Problem
from .governance_fixture import (STUDY, PROTOCOL, DEVICE, KEY, CALIBRATION, common,
    approve, configuration, adc_material, study, retention, device, calibration, proof)
from . import test_model_engine


@pytest.fixture
def engineered_model():
    return test_model_engine.model.__wrapped__()


def scope_for(config):
    return {"device_id": DEVICE, "key_id": KEY, "hardware_revision": "fixture-hw",
        "firmware_versions": ["fixture-fw"], "adapter_id": "otgd_esp32_adc_v1",
        "extractor_version": "adc_peak_intervals_v1", "channel": "cardiac", "modality": "ppg",
        "configuration_id": config["configuration_id"], "configuration_version": config["version"],
        "configuration_submitted_sha256": digest(config), "behavior": "follows_current_signed_grant",
        "timing_method": "server_issue_to_attestation_receipt_v1", "maximum_interval_ms": 20000,
        "server_utc_error_ms": 25.0, "maximum_monotonic_rate_error_ppm": None}


def calibration_for(scope):
    return common("fictional-cardiac-interval", calibration_id="fictional-cardiac-interval",
        purpose="cardiac_server_interval", cardiac_server_interval=scope, calibration_sha256=digest(scope))


def approved_config(db, account, *, qualified=True):
    material = adc_material()
    config = configuration("cardiac", material=material, sha256=digest(material), max_duration_ms=15000,
        software_adapter_id="otgd_signed_reader_v1", device_id=DEVICE, key_id=KEY, calibration_id=CALIBRATION,
        approved_hardware=["fixture-hw"], approved_firmware=["fixture-fw"])
    q = proof("cardiac", config)
    if qualified:
        q["purpose"] = "qualified_measurement"
    for kind, body in (("study", study(account, {"cardiac": config["registry_id"]})), ("retention", retention()),
        ("device", device(account)), ("calibration", calibration()), ("qualification", q), ("configuration", config)):
        approve(db, kind, body)
    return g.active_body(db, "configuration", config["registry_id"])


def model_for(engineered_model, scope):
    body = deepcopy(engineered_model["body"])
    body["study_ids"] = [STUDY]
    body["manifest"].update(required_channels=["cardiac_hr"], baseline_mode="population",
        allowed_protocol_ids=[PROTOCOL], max_clock_uncertainty_ms=20000)
    body["cardiac_timing_policy"] = {"method": "server_issue_to_attestation_receipt_v1",
        "calibration_id": "fictional-cardiac-interval", "max_interval_ms": scope["maximum_interval_ms"],
        "allow_baseline_delta": False}
    body["evaluation_report"].update(analysis_scope="cardiac_hr_only",
        ablations={"cardiac_hr_only": deepcopy(body["evaluation_report"]["confirmatory"])},
        cardiac_evidence={"cardiac_timing_policy_sha256": digest(body["cardiac_timing_policy"]),
            **{key: "e" * 64 for key in ("calibration_registry_sha256", "calibration_scope_sha256",
                "qualification_registry_sha256", "device_registry_sha256", "configuration_submitted_sha256", "evidence_manifest_sha256")}})
    return common(body["model_id"], **body)


@pytest.mark.parametrize("change", [{"channel": "ecg"}, {"modality": "ecg"},
    {"extractor_version": "sparkfun_sensor_bpm_v1"}, {"firmware_versions": ["fixture-fw", "fixture-fw"]},
    {"behavior": "participant_checkbox"}, {"server_utc_error_ms": float("nan")},
    {"server_utc_error_ms": -1.0}, {"maximum_interval_ms": 120001}])
def test_interval_scope_refuses_unimplemented_or_ambiguous_authority(change):
    with pytest.raises(ValidationError):
        g.CardiacServerIntervalScope.model_validate({**scope_for({"configuration_id": "fixture", "version": "v1"}), **change})


def test_calibration_scope_digest_and_purpose_are_distinct(client, account):
    with factory().begin() as db:
        config = approved_config(db, account)
        scope = scope_for(config)
        value = g.validate_submission("calibration", calibration_for(scope))
        assert value["calibration_sha256"] == digest(value["cardiac_server_interval"])
        approve(db, "calibration", value)
        with pytest.raises(ValueError):
            g.validate_submission("calibration", {**value, "calibration_sha256": "f" * 64})
        with pytest.raises(ValueError):
            g.validate_submission("calibration", {**value, "purpose": "device"})
        with pytest.raises(ValueError):
            g.validate_submission("calibration", {**value, "model_id": "not-device-qualification"})


@pytest.mark.parametrize("change", [{"configuration_submitted_sha256": "f" * 64},
    {"configuration_version": "v2"}, {"key_id": "other-key"}, {"hardware_revision": "other-hw"},
    {"firmware_versions": ["other-fw"]}])
def test_separate_release_checks_exact_current_configuration_tuple(client, account, change):
    with factory().begin() as db:
        config = approved_config(db, account)
        value = g.validate_submission("calibration", calibration_for({**scope_for(config), **change}))
        with pytest.raises(Problem, match="CARDIAC_INTERVAL_SCOPE_MISMATCH"):
            g.validate_dependencies(db, "calibration", value)


def test_collection_only_proof_cannot_qualify_server_interval(client, account):
    with factory().begin() as db:
        config = approved_config(db, account, qualified=False)
        with pytest.raises(Problem, match="CARDIAC_INTERVAL_SCOPE_MISMATCH"):
            g.validate_dependencies(db, "calibration", calibration_for(scope_for(config)))


def test_hr_only_model_policy_release_and_retirement_recheck(client, account, engineered_model):
    with factory().begin() as db:
        config = approved_config(db, account)
        scope = scope_for(config)
        approve(db, "calibration", calibration_for(scope))
        body = model_for(engineered_model, scope)
        body["evaluation_report"]["cardiac_evidence"].update(
            calibration_registry_sha256=digest(g.active_body(db, "calibration", "fictional-cardiac-interval")),
            calibration_scope_sha256=digest(scope), qualification_registry_sha256=digest(g.active_body(db, "qualification", config["qualification_evidence_ref"])),
            device_registry_sha256=digest(g.active_body(db, "device", DEVICE + ":" + KEY)), configuration_submitted_sha256=digest(config))
        mid = body["manifest"]["calibration_id"]
        approve(db, "calibration", common(mid, calibration_id=mid, purpose="model",
            model_id=body["model_id"], calibration_sha256="c" * 64))
        approved = g.Model.model_validate(body).data()
        approve(db, "model", approved)
        assert g.active_body(db, "model", approved["model_id"])["cardiac_timing_policy"]["allow_baseline_delta"] is False
        for field in ("calibration_registry_sha256", "calibration_scope_sha256", "qualification_registry_sha256",
            "device_registry_sha256", "configuration_submitted_sha256"):
            changed = deepcopy(approved)
            changed["evaluation_report"]["cardiac_evidence"][field] = "f" * 64
            with pytest.raises(Problem, match="CARDIAC_EVALUATION_SCOPE_MISMATCH"):
                g.validate_dependencies(db, "model", changed)
        g.transition(db, "configuration", config["registry_id"], config["version"], "retire",
            "local:independent-releaser", "Fictional configuration retirement", 3)
        db.flush()
        with pytest.raises(Problem, match="APPROVED_REGISTRY_VERSION_REQUIRED"):
            g.validate_dependencies(db, "model", approved)


@pytest.mark.parametrize("change", [{"max_interval_ms": 20001}, {"allow_baseline_delta": True}])
def test_model_bounds_and_personalized_permission_cannot_be_inferred(engineered_model, change):
    body = model_for(engineered_model, scope_for({"configuration_id": "fixture", "version": "v1"}))
    body["cardiac_timing_policy"].update(change)
    with pytest.raises(ValueError):
        g.Model.model_validate(body)


def test_required_channel_scope_is_heart_rate_only(engineered_model):
    body = model_for(engineered_model, scope_for({"configuration_id": "fixture", "version": "v1"}))
    body["manifest"]["required_channels"] = ["cardiac_hr", "pupil"]
    with pytest.raises(ValueError):
        g.Model.model_validate(body)


def test_additive_scope_fields_preserve_prior_submission_identity(engineered_model):
    legacy_calibration = g.validate_submission("calibration", calibration())
    assert "cardiac_server_interval" not in legacy_calibration
    assert g.validate_submission("calibration", legacy_calibration) == legacy_calibration
    body = model_for(engineered_model, scope_for({"configuration_id": "fixture", "version": "v1"}))
    body.pop("cardiac_timing_policy")
    body["evaluation_report"] = deepcopy(engineered_model["body"]["evaluation_report"])
    legacy_model = g.validate_submission("model", body)
    assert "cardiac_timing_policy" not in legacy_model
    assert "analysis_scope" not in legacy_model["evaluation_report"]
    assert "cardiac_evidence" not in legacy_model["evaluation_report"]
    assert g.validate_submission("model", legacy_model) == legacy_model


def test_legacy_released_model_remains_readable_at_original_submitted_sha(client, account, engineered_model):
    with factory().begin() as db:
        config = approved_config(db, account)
        body = model_for(engineered_model, scope_for(config))
        body.pop("cardiac_timing_policy")
        body["evaluation_report"] = deepcopy(engineered_model["body"]["evaluation_report"])
        legacy = g.validate_submission("model", body)
        mid = legacy["manifest"]["calibration_id"]
        approve(db, "calibration", common(mid, calibration_id=mid, purpose="model",
            model_id=legacy["model_id"], calibration_sha256="c" * 64))
        receipt = approve(db, "model", legacy)
        row = g.released_version(db, "model", legacy["model_id"])
        assert row.body == legacy and row.sha256 == digest(legacy) == receipt["submitted_sha256"]
        assert "analysis_scope" not in row.body["evaluation_report"]
        assert "cardiac_timing_policy" not in row.body
