"""Fictional signed-reader tests; no physiological or timing approval is supplied.

The HTTP fixture executes genuine independent registry transitions, binding,
instruction/start custody, P256 attestation and finalization. Values and instant
acquisition are engineered fixtures; physical clock/reader qualification stays
external. Storage model bytes are an explicit bounded unit double.
"""

import base64
from copy import deepcopy
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from otgd import cardiac_authority as c
from otgd import model_engine as m
from otgd.canonical import canonical, digest
from otgd.config import settings
from otgd.db import Account, Check, factory, iso, now, uid
from otgd.domain import record
from otgd.errors import Problem
from otgd.operator_governance import SCHEMAS, Configuration, active_body, transition

from .conftest import headers
from .governance_fixture import (
    CALIBRATION,
    DEVICE,
    KEY,
    PROTOCOL,
    STUDY,
    acknowledge_cardiac,
    adc_material,
    approve,
    calibration,
    common,
    configuration,
    device,
    proof,
    retention,
    study,
)
from .helpers import session_fixture
from .test_model_engine import model as model  # noqa: PLC0414 -- shared pytest fixture


@pytest.fixture
def cardiac(client, account, model, capture_signer, monkeypatch):
    private = ec.generate_private_key(ec.SECP256R1())
    material = adc_material()
    config = Configuration.model_validate(configuration("cardiac", material=material,
        sha256=digest(material), max_duration_ms=material["duration_ms"], software_adapter_id="otgd_signed_reader_v1",
        device_id=DEVICE, key_id=KEY, calibration_id=CALIBRATION,
        approved_hardware=["fixture-hw"], approved_firmware=["fixture-fw"])).data()
    qualified = proof("cardiac", config)
    qualified["purpose"] = "qualified_measurement"
    body = deepcopy(model["body"])
    body["manifest"].update(required_channels=["cardiac_hr"], allowed_protocol_ids=[PROTOCOL],
        allowed_hardware_revisions=["fixture-hw"], max_clock_uncertainty_ms=60000,
        max_acquisition_span_ms=180000, max_delivery_delay_ms=3600000)
    artifact = model["artifact"].model_copy(update={"feature_names": ["cardiac.heart_rate_bpm"],
        "means": [70.0], "scales": [10.0], "coefficients": [1.0],
        "feature_limits": {"cardiac.heart_rate_bpm": [0.0, 300.0]}})
    raw = canonical(artifact.model_dump())
    body["manifest"]["artifact_sha256"] = digest(artifact.model_dump())
    body["artifact_ref"].update(bucket=settings().artifact_bucket,
        sha256=body["manifest"]["artifact_sha256"], size_bytes=len(raw))
    body["evaluation_report"]["artifact_sha256"] = body["manifest"]["artifact_sha256"]
    timing_id = "fictional-server-cardiac-interval"
    body["study_ids"] = [STUDY]
    body["cardiac_timing_policy"] = {"method": c.METHOD, "calibration_id": timing_id,
        "max_interval_ms": 60000, "allow_baseline_delta": False}
    body = common(body["model_id"], **body)
    scope = {"device_id": DEVICE, "key_id": KEY, "hardware_revision": "fixture-hw",
        "firmware_versions": ["fixture-fw"], "adapter_id": material["adapter_id"],
        "extractor_version": material["extractor_version"], "channel": "cardiac", "modality": "ppg",
        "configuration_id": config["configuration_id"], "configuration_version": config["version"],
        "configuration_submitted_sha256": digest(config), "behavior": "follows_current_signed_grant",
        "timing_method": c.METHOD, "maximum_interval_ms": 60000, "server_utc_error_ms": 2.0,
        "maximum_monotonic_rate_error_ppm": None}
    doc = study(account, {"cardiac": config["configuration_id"]})
    doc["model_id"] = body["model_id"]
    device_value = SCHEMAS["device"].model_validate(device(account, private)).data()
    qualified = SCHEMAS["qualification"].model_validate(qualified).data()
    timing = SCHEMAS["calibration"].model_validate(common(timing_id, calibration_id=timing_id, purpose="cardiac_server_interval",
        cardiac_server_interval=scope, calibration_sha256=digest(scope))).data()
    body["evaluation_report"].update(analysis_scope="cardiac_hr_only", ablations={
        "cardiac_hr_only": deepcopy(body["evaluation_report"]["confirmatory"])}, cardiac_evidence={
        "cardiac_timing_policy_sha256": digest(body["cardiac_timing_policy"]),
        "calibration_registry_sha256": digest(timing), "calibration_scope_sha256": digest(scope),
        "qualification_registry_sha256": digest(qualified), "device_registry_sha256": digest(device_value),
        "configuration_submitted_sha256": digest(config), "evidence_manifest_sha256": "e" * 64})
    with factory().begin() as db:
        for kind, value in (("study", doc), ("retention", retention()), ("device", device_value),
            ("calibration", calibration()), ("qualification", qualified), ("configuration", config),
            ("calibration", timing),
            ("calibration", common(body["manifest"]["calibration_id"], calibration_id=body["manifest"]["calibration_id"],
                purpose="model", model_id=body["model_id"], calibration_sha256=digest(artifact.calibration.model_dump()))),
            ("model", body)):
            approve(db, kind, value)
        body = deepcopy(active_body(db, "model", body["model_id"]))
    def send(method, path, value, revision=None):
        response = client.request(method, path, headers=headers(revision=revision), json=value)
        assert response.status_code in (200, 201, 202), (path, response.status_code, response.text)
        return response.json()
    send("POST", f"/v1/studies/{STUDY}/consents", {**{key: doc[key] for key in (
        "invitation_id", "document_version", "document_sha256")}, "accepted": True, "acknowledged_at": iso()})
    challenge = send("POST", "/v1/device-bindings/challenges", {"device_id": DEVICE, "key_id": KEY})
    signature = base64.b64encode(private.sign(b"OTGD-BIND-v1\n" + canonical(challenge["transcript"]), ec.ECDSA(hashes.SHA256()))).decode()
    binding = send("POST", "/v1/device-bindings", {"challenge_id": challenge["challenge_id"], "signature": signature})
    capture = capture_session(client, send, account, config, private, binding)
    monkeypatch.setattr("otgd.storage.versioned_read", lambda bucket, key, version, limit: raw)
    return SimpleNamespace(**vars(capture), body=body, artifact=artifact, config=config,
        timing_id=timing_id, server_private=capture_signer, send=send, binding=binding)


def capture_session(client, send, account, config, private, binding, *, baseline_ref=None):
    material = config["material"]
    sid, aid, rid, attid, boot = (uid() for _ in range(5))
    snapshot = session_fixture(account)
    target = iso(now() - 1 if baseline_ref is None else now())
    snapshot.update(session_id=sid, mode="controlled_research", study_id=STUDY, protocol_id=PROTOCOL,
        created_at=target, target_at=target, clock_uncertainty_ms=None, baseline_ref=baseline_ref)
    snapshot["profile"].update(source="study_measurement", recorded_at=target, age_years=30)
    snapshot["history"]["alcohol_co_use"] = "not_reported"
    snapshot["device"].update(device_id=DEVICE, hardware_revision="fixture-hw", firmware_version="fixture-fw")
    snapshot["sample"].update(status="not_collected", collected_at=None, volume_ml=None, dilution_factor=None)
    snapshot["saliva"] = []
    for field in ("eyes", "task"):
        snapshot[field].update(status="not_collected", source="prototype_sensor", quality_flags=[], started_at=None, ended_at=None)
    snapshot["eyes"].update(frame_rate_hz=None, baseline_diameter_mm=None, relative_constriction=None, latency_ms=None)
    snapshot["task"].update(practice_trials=0, scored_trials=0, go_trials=0, no_go_trials=0, valid_correct_go_trials=0,
        features={key: None for key in snapshot["task"]["features"]})
    send("POST", "/v1/sessions", {"session_id": sid, "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL})
    context = {"schema_version": "1.0.0", "session_id": sid, "context_confirmed_at": target,
        "profile_version_id": None, "profile_snapshot_sha256": digest(snapshot["profile"]),
        "history_snapshot_sha256": digest(snapshot["history"]), "protocol_id": PROTOCOL,
        "configuration_refs": [{"id": config["configuration_id"], "version": "v1", "sha256": config["sha256"], "scope": "measurement_collection"}],
        "baseline_refs": [baseline_ref] if baseline_ref else [], "device_associations": [{**{key: binding[key] for key in (
            "binding_id", "device_id", "hardware_revision", "firmware_version")}, "boot_id": boot, "clock_evidence_ref": None}]}
    send("PUT", f"/v1/sessions/{sid}/context", context, 0)
    attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid, "record_id": rid, "component": "cardiac",
        "supersedes_attempt_id": None, "status": "started", "source": "prototype_sensor", "started_at": iso(), "ended_at": None,
        "configuration_id": config["configuration_id"], "configuration_hash": config["sha256"], "quality_flags": [],
        "component_metadata": {"modality": "ppg"}, "artifact_refs": [], "attestation_refs": []}
    send("PUT", f"/v1/sessions/{sid}/attempts/{aid}", attempt, 0)
    instructions = acknowledge_cardiac(client, sid, attempt, config)
    authorization = send("POST", f"/v1/sessions/{sid}/capture-authorizations", {"attempt_id": aid,
        "channel": "cardiac", "binding_id": binding["binding_id"], "device_id": DEVICE,
        "configuration_id": config["configuration_id"], "configuration_hash": config["sha256"],
        "instruction_receipt_id": instructions["instruction_receipt_id"]})
    started = send("POST", f"/v1/sessions/{sid}/capture-authorizations/{authorization['authorization_id']}/start", {
        "attempt_id": aid, "device_boot_id": boot, "device_nonce": base64.urlsafe_b64encode(b"F" * 32).decode().rstrip("=")})
    timestamp = started["server_started_at"]
    projection = {**snapshot["cardiac"], "source": "prototype_sensor", "status": "valid", "started_at": timestamp,
        "ended_at": timestamp, "modality": "ppg", "heart_rate_bpm": 75.0, "ecg_rmssd_ms": None,
        "ecg_status": "not_collected", "sample_rate_hz": 100.0, "raw_artifact_id": None,
        "acquisition_config_id": config["configuration_id"], "quality_flags": sorted(c.FLAGS[material["adapter_id"]])}
    attempt.update(status="valid", started_at=timestamp, ended_at=timestamp,
        quality_flags=projection["quality_flags"], attestation_refs=[attid], component_metadata={
            "modality": "ppg", "armed_at": attempt["started_at"], "projection": projection, "instruction_receipt": instructions})
    send("PUT", f"/v1/sessions/{sid}/attempts/{aid}", attempt, 1)
    envelope = {"schema_version": "1.0.0", "environment": "test", "owner_ref": account, "data_generation": 1,
        "session_id": sid, "attempt_id": aid, "authorization_id": authorization["authorization_id"],
        "binding_id": binding["binding_id"], "device_id": DEVICE, "key_id": KEY, "boot_id": boot,
        "sequence": 1, "configuration_hash": config["sha256"], "payload_sha256": digest(projection)}
    signature = base64.b64encode(private.sign(b"OTGD-CAPTURE-v1\n" + canonical(envelope), ec.ECDSA(hashes.SHA256()))).decode()
    send("POST", f"/v1/sessions/{sid}/attestations", {"attestation_id": attid, "envelope": envelope,
        "signature": signature, "normalized_payload": projection})
    snapshot["cardiac"] = projection
    snapshot.update(capture_completed_at=timestamp, acquisition_span_ms=0.0)
    from spec_validation import validate_session
    validate_session(snapshot)
    send("PUT", f"/v1/sessions/{sid}/snapshot", snapshot, 1)
    evidence = {"schema_version": "1.0.0", "session_id": sid, "context_sha256": digest(context),
        "attempts": [{"attempt_id": aid, "sha256": digest(attempt)}],
        "selected": {"saliva": None, "eyes": None, "cardiac": aid, "task": None, "alcohol": None}}
    send("PUT", f"/v1/sessions/{sid}/evidence-manifest", evidence, 0)
    final = send("POST", f"/v1/sessions/{sid}/finalize", {"snapshot_sha256": digest(snapshot),
        "evidence_sha256": digest(evidence)}, 2)
    return SimpleNamespace(account=account, sid=sid, aid=aid, attid=attid, authorization_id=authorization["authorization_id"],
        snapshot=snapshot, context=context, evidence=evidence, job=final["job_id"], private=private)


def resolved(value):
    db = factory()()
    return db, db.get(Account, value.account), db.get(Check, value.sid)


def test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot(client, cardiac):
    from otgd.worker import run_job

    db, owner, check = resolved(cardiac)
    with db:
        admitted = m.execution_authority(db, owner, check)
        interval = admitted["cardiac_timing"]
        assert interval["interval_ms"] >= 4  # includes both reviewed UTC margins
        assert interval["preserved_quality_flags"] == cardiac.snapshot["cardiac"]["quality_flags"]
        assert check.snapshot["clock_uncertainty_ms"] is None
        result = m.result_for_check(db, owner, check)
        assert result["state"] == "research_estimate", result
    assert run_job(cardiac.job) == "completed"
    response = client.get(f"/v1/sessions/{cardiac.sid}/result", headers=headers())
    assert response.status_code == 200, response.text
    value = response.json()
    assert value["state"] == "research_estimate" and value["schema_version"] == "1.1.0", value
    assert value["input_sha256"] == digest(cardiac.snapshot)
    authority = value["model_execution"]["authority_manifest"]["cardiac_authority"]
    assert authority["baseline"] is None
    assert authority["current"]["snapshot_sha256"] == value["input_sha256"]
    assert m.validate_result(value) == value
    import os
    from pathlib import Path
    if os.environ.get("OTGD_CARDIAC_FIXTURE_PATH"):
        owned = client.get(f"/v1/sessions/{cardiac.sid}", headers=headers())
        evidence = client.get(f"/v1/sessions/{cardiac.sid}/evidence", headers=headers())
        assert owned.status_code == evidence.status_code == 200
        with factory()() as db:
            generation = db.get(Account, cardiac.account).generation
        Path(os.environ["OTGD_CARDIAC_FIXTURE_PATH"]).write_bytes(canonical({
            "fixture_kind": "FICTIONAL_ENGINEERING_ONLY", "snapshot": cardiac.snapshot,
            "result": value, "context": cardiac.context, "evidence_manifest": cardiac.evidence,
            "generation": generation, "owned_session": owned.json(), "owned_evidence": evidence.json()}))


@pytest.mark.parametrize("kind,id", [("calibration", "fictional-server-cardiac-interval"),
    ("configuration", "fictional-cardiac-configuration"), ("qualification", "fictional-governance-qualification-cardiac"),
    ("device", DEVICE + ":" + KEY)])
def test_retired_current_authority_never_promotes_old_capture(cardiac, kind, id):
    with factory().begin() as db:
        transition(db, kind, id, "v1", "retire", "local:fixture-releaser", "Fictional retirement", 3)
    db, owner, check = resolved(cardiac)
    with db, pytest.raises(Problem):
        m.execution_authority(db, owner, check)


@pytest.mark.parametrize("change", ["unknown_flag", "missing_flag", "ecg", "rmssd", "width", "span", "snapshot", "future"])
def test_unsigned_timing_or_channel_changes_cannot_qualify(cardiac, change):
    db, owner, check = resolved(cardiac)
    with db:
        admitted = m.execution_authority(db, owner, check)
    snapshot, interval = deepcopy(cardiac.snapshot), deepcopy(admitted["cardiac_timing"])
    if change == "unknown_flag": snapshot["cardiac"]["quality_flags"].append("CONTACT_LOST")
    elif change == "missing_flag": snapshot["cardiac"]["quality_flags"].pop()
    elif change == "ecg": snapshot["cardiac"]["modality"] = "ecg"
    elif change == "rmssd": snapshot["cardiac"]["ecg_rmssd_ms"] = 20.0
    elif change == "width": interval["interval_ms"] -= 1
    elif change == "span": interval["acquisition_bound_ms"] -= 1
    elif change == "snapshot": snapshot["cardiac"]["heart_rate_bpm"] = 120.0
    else: interval["received_epoch"] = now() + 10
    with pytest.raises(Problem, match="CARDIAC_SERVER_INTERVAL_INVALID"):
        c.validate_interval(snapshot, cardiac.body, interval)


def test_shared_exact_interval_arithmetic_nonzero_margin_and_inclusive_boundary(cardiac):
    db, owner, check = resolved(cardiac)
    with db:
        interval = m.execution_authority(db, owner, check)["cardiac_timing"]
    snapshot, body = deepcopy(cardiac.snapshot), deepcopy(cardiac.body)
    issue = 1800000000.0
    target = issue - 1
    snapshot.update(target_at=iso(target), created_at=iso(target))
    interval.update(issued_epoch=issue, received_epoch=issue + 5, target_epoch=target,
        server_utc_error_ms=2.0, snapshot_sha256=digest(snapshot), interval_ms=5004, acquisition_bound_ms=6004)
    body["cardiac_timing_policy"]["max_interval_ms"] = 5004
    body["manifest"]["max_clock_uncertainty_ms"] = 5004
    body["manifest"]["max_acquisition_span_ms"] = 6004
    body["manifest"]["max_delivery_delay_ms"] = 10004
    interval["policy_sha256"] = digest(body["cardiac_timing_policy"])
    assert c.validate_interval(snapshot, body, interval, evaluated_epoch=issue + 10) == interval
    body["manifest"]["max_clock_uncertainty_ms"] = 5003
    with pytest.raises(Problem): c.validate_interval(snapshot, body, interval, evaluated_epoch=issue + 10)


@pytest.mark.parametrize("changes", [{"feature_names": ["cardiac.ecg_rmssd_ms"]},
    {"feature_names": ["profile.age_years", "cardiac.heart_rate_bpm"]}])
def test_actual_artifact_not_just_required_channels_is_hr_only(cardiac, changes):
    with pytest.raises(Problem, match="CARDIAC_HR_ONLY_SCOPE_REQUIRED"):
        c.validate_features(cardiac.body, cardiac.artifact.model_copy(update=changes))


def test_baseline_requires_independent_original_interval_same_scope_and_conservative_age(cardiac):
    db, owner, check = resolved(cardiac)
    with db:
        current = m.execution_authority(db, owner, check)["cardiac_timing"]
    body = deepcopy(cardiac.body)
    body["manifest"]["baseline_mode"] = "personalized"
    body["quality_policy"]["max_baseline_age_ms"] = 10000
    body["cardiac_timing_policy"]["allow_baseline_delta"] = True
    current["policy_sha256"] = digest(body["cardiac_timing_policy"])
    baseline = deepcopy(current)
    baseline.update(session_id=uid(), issued_epoch=current["target_epoch"] - 5,
        received_epoch=current["target_epoch"] - 4, target_epoch=current["target_epoch"] - 6,
        interval_ms=1004, acquisition_bound_ms=2004, snapshot_sha256="a" * 64)
    assert c.build_authority(body, current, baseline)["baseline"] == baseline
    c.validate_baseline(cardiac.snapshot, body, current, baseline)
    for key, value in (("device_id", "other-device"), ("calibration_registry_sha256", "0" * 64),
        ("configuration_submitted_sha256", "0" * 64)):
        bad = {**baseline, key: value}
        with pytest.raises(Problem): c.build_authority(body, current, bad)
    baseline["issued_epoch"] -= 10
    with pytest.raises(Problem): c.validate_baseline(cardiac.snapshot, body, current, baseline)
    baseline["issued_epoch"] += 10
    baseline["received_epoch"] = current["target_epoch"]
    with pytest.raises(Problem): c.validate_baseline(cardiac.snapshot, body, current, baseline)


@pytest.mark.parametrize("change", ["server_signature", "server_issued_at", "server_scope", "anchor",
    "device_signature", "device_payload", "device_scope", "binding", "duplicate_attestation", "projection"])
def test_rehashed_custody_records_still_require_original_signatures_and_exact_scope(cardiac, change):
    from otgd.capture_signing import KEY_STATE
    from otgd.db import SystemState
    db, owner, check = resolved(cardiac)
    with db:
        auth = record(db, owner, "authorization", cardiac.authorization_id)
        attestation = record(db, owner, "attestation", cardiac.attid)
        attempt = record(db, owner, "attempt", cardiac.aid)
        if change.startswith("server_"):
            value = deepcopy(auth.body)
            if change == "server_signature": value["server_start"]["signature"] = base64.b64encode(b"x" * 64).decode()
            elif change == "server_issued_at": value["server_start"]["grant"]["issued_at"] = iso(now() - 10)
            else: value["server_start"]["grant"]["owner_ref"] = uid()
            auth.body, auth.sha256 = value, digest(value)
        elif change.startswith("device_"):
            value = deepcopy(attestation.body)
            if change == "device_signature": value["signature"] = base64.b64encode(b"x" * 64).decode()
            elif change == "device_payload": value["normalized_payload"]["heart_rate_bpm"] = 100.0
            else: value["envelope"]["boot_id"] = uid()
            attestation.body, attestation.sha256 = value, digest(value)
        elif change == "anchor":
            anchor = db.get(SystemState, KEY_STATE)
            anchor.body = {**anchor.body, "public_key_sha256": "f" * 64}
        elif change == "binding":
            binding = record(db, owner, "binding", auth.body["binding_id"])
            binding.body = {**binding.body, "state": "revoked"}
            binding.sha256 = digest(binding.body)
        else:
            value = deepcopy(attempt.body)
            if change == "duplicate_attestation": value["attestation_refs"] *= 2
            else: value["component_metadata"]["projection"]["heart_rate_bpm"] = 101.0
            attempt.body, attempt.sha256 = value, digest(value)
        db.flush()
        manifest = record(db, owner, "manifest", cardiac.sid)
        with pytest.raises(Problem): c.resolve(db, owner, check, cardiac.body, manifest)


def test_signed_sdk_duration_uses_reviewed_rate_error_and_exact_unrounded_custody_bound(cardiac):
    db, owner, check = resolved(cardiac)
    with db: value = m.execution_authority(db, owner, check)["cardiac_timing"]
    item = c.IntervalEvidence.model_validate({**value, "adapter_id": "otgd_sparkfun_max32664_v1",
        "extractor_version": "sparkfun_sensor_bpm_v1", "preserved_quality_flags": sorted(c.FLAGS["otgd_sparkfun_max32664_v1"]),
        "signed_acquisition_duration_us": 1001000, "maximum_monotonic_rate_error_ppm": 1000})
    calculated = c.bounds(1800000000.0, 1800000001.0, 1799999999.0, 0, 1800000002.0)
    c.validate_signed_duration(item, calculated)
    with pytest.raises(ValueError): c.validate_signed_duration(item.model_copy(update={"signed_acquisition_duration_us": 1001001}), calculated)
    with pytest.raises(ValueError): c.validate_signed_duration(item.model_copy(update={"maximum_monotonic_rate_error_ppm": None}), calculated)
    with pytest.raises(ValueError): c.validate_signed_duration(item.model_copy(update={"signed_acquisition_duration_us": None}), calculated)
    with pytest.raises(ValueError): c.validate_signed_duration(c.IntervalEvidence.model_validate({**value,
        "signed_acquisition_duration_us": 1}), calculated)


@pytest.mark.parametrize("change", ["legacy_scope", "fake_ablations", "missing_evidence", "wrong_policy", "denominator"])
def test_hr_report_cannot_claim_unmeasured_chemical_or_ecg_comparisons(cardiac, change):
    body = deepcopy(cardiac.body)
    report = body["evaluation_report"]
    if change == "legacy_scope": report["analysis_scope"] = "combined_channels"
    elif change == "fake_ablations": report["ablations"]["chemical_only"] = deepcopy(report["confirmatory"])
    elif change == "missing_evidence": report["cardiac_evidence"] = None
    elif change == "wrong_policy": report["cardiac_evidence"]["cardiac_timing_policy_sha256"] = "a" * 64
    else:
        report["ablations"]["cardiac_hr_only"].update(total=3, valid=3, invalid=0, positives=1, negatives=2)
    with pytest.raises(ValueError): m.validate_registry_model(body)


@pytest.mark.parametrize("key", ["calibration_registry_sha256", "calibration_scope_sha256",
    "qualification_registry_sha256", "device_registry_sha256", "configuration_submitted_sha256"])
def test_training_evidence_refs_cannot_qualify_different_current_reader(cardiac, key):
    db, owner, check = resolved(cardiac)
    body = deepcopy(cardiac.body)
    body["evaluation_report"]["cardiac_evidence"][key] = "f" * 64
    with db, pytest.raises(Problem, match="CARDIAC_EVALUATION_SCOPE_MISMATCH"):
        c.resolve(db, owner, check, body, record(db, owner, "manifest", cardiac.sid))


def test_publication_rechecks_original_delivery_age_instead_of_old_evaluation_time(cardiac, monkeypatch):
    db, owner, check = resolved(cardiac)
    with db:
        value = m.result_for_check(db, owner, check)
        assert value["state"] == "research_estimate"
        issued = value["model_execution"]["authority_manifest"]["cardiac_authority"]["current"]["issued_epoch"]
        monkeypatch.setattr(c, "now", lambda: issued + 3601)
        with pytest.raises(Problem): m.verify_current_execution(db, owner, check, value)


def test_personalized_http_capture_resolves_its_own_original_baseline_and_rejects_changed_signature(cardiac, client):
    from otgd.db import RateBucket
    from otgd.worker import run_job
    from sqlalchemy import delete

    assert run_job(cardiac.job) == "completed"
    body = deepcopy(cardiac.body)
    body["version"] = "v2"
    body["manifest"]["baseline_mode"] = "personalized"
    body["quality_policy"]["max_baseline_age_ms"] = 20000
    body["cardiac_timing_policy"]["allow_baseline_delta"] = True
    body["evaluation_report"]["cardiac_evidence"]["cardiac_timing_policy_sha256"] = digest(body["cardiac_timing_policy"])
    with factory().begin() as db:
        approve(db, "model", body)
        # Two instant fictional captures intentionally omit physical wait/rest;
        # allow the second HTTP journey without weakening runtime rate policy.
        db.execute(delete(RateBucket).where(RateBucket.id == cardiac.account + ":write"))
    followup = capture_session(client, cardiac.send, cardiac.account, cardiac.config, cardiac.private,
        cardiac.binding, baseline_ref=cardiac.sid)
    assert run_job(followup.job) == "completed"
    response = client.get(f"/v1/sessions/{followup.sid}/result", headers=headers())
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["state"] == "research_estimate", result
    proof = result["model_execution"]
    companion = proof["authority_manifest"]["cardiac_authority"]
    assert proof["feature_values_sha256"] == digest([0.0])
    assert companion["baseline"]["session_id"] == cardiac.sid
    assert companion["baseline"]["attestation_id"] == cardiac.attid
    assert companion["baseline"]["authorization_id"] != companion["current"]["authorization_id"]
    assert companion["baseline"]["received_epoch"] < companion["current"]["issued_epoch"]
    db, owner, check = resolved(followup)
    with db:
        m.verify_current_execution(db, owner, check, result)
        attestation = record(db, owner, "attestation", cardiac.attid)
        attestation.body = {**attestation.body, "signature": base64.b64encode(b"x" * 64).decode()}
        attestation.sha256 = digest(attestation.body)
        db.flush()
        with pytest.raises(Problem): m.verify_current_execution(db, owner, check, result)
