"""Production authority behavior using visibly fictional software evidence."""

import base64
from copy import deepcopy
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from otgd.canonical import digest
from otgd.config import settings
from otgd.db import Account, Registry, RegistryEvent, RegistryVersion, factory, iso, now
from otgd.domain import record, save_record
from otgd.errors import Problem
from otgd.operator_governance import (
    active_body, capture_configuration, channel_capabilities, history, qualified_binding,
    released_version, submit, transition, validate_dependencies, validate_submission, validate_optical_attempt,
)
from otgd.operator_cli import cloud_client, execute, main, parser, principal, require_maintenance_db

from .conftest import headers
from .governance_fixture import (
    CALIBRATION, CONFIGURATION, DEVICE, KEY, POLICY, PROTOCOL, STUDY,
    approve, approve_task, calibration, common, configuration, device, proof, retention, study,
)


def failure(code, callable, *args, **kwargs):
    with pytest.raises(Problem) as denied:
        callable(*args, **kwargs)
    assert denied.value.code == code


def consent(client, value):
    response = client.post(f"/v1/studies/{STUDY}/consents", headers=headers(), json={
        **{k: value[k] for k in ("invitation_id", "document_version", "document_sha256")},
        "accepted": True, "acknowledged_at": iso(),
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_immutable_submission_three_principals_lifecycle_history_and_revision(client, account):
    value = study(account)
    with factory().begin() as db:
        first = submit(db, "study", value, "local:alice")
        failure("REGISTRY_VERSION_EXISTS", submit, db, "study", value, "local:alice")
        failure("INDEPENDENT_REVIEW_REQUIRED", transition, db, "study", STUDY, "v1", "approve", "local:alice", "review", 1)
        failure("REGISTRY_REVISION_CONFLICT", transition, db, "study", STUDY, "v1", "approve", "local:bob", "review", 9)
        failure("REGISTRY_STATE_CONFLICT", transition, db, "study", STUDY, "v1", "release", "local:carol", "release", 1)
        transition(db, "study", STUDY, "v1", "approve", "local:bob", "reviewed exact evidence", 1)
        db.flush()
        failure("INDEPENDENT_RELEASE_REQUIRED", transition, db, "study", STUDY, "v1", "release", "local:bob", "release", 2)
        transition(db, "study", STUDY, "v1", "release", "local:carol", "authorized release", 2)
        db.flush()
        stored = released_version(db, "study", STUDY)
        assert stored.sha256 == first["submitted_sha256"] == digest(stored.body)
        newer = {**value, "version": "v2", "invitation_id": "fictional-new-invitation"}
        approve(db, "study", newer)
        db.flush()
        original = db.get(RegistryVersion, first["version_id"])
        assert original.state == "retired" and original.body == first["submitted_body"]
        result = history(db, "study", STUDY)
        assert len(result["items"]) == 2 and len(result["items"][1]["decisions"]) == 4
        assert active_body(db, "study", STUDY)["version"] == "v2"
        failure("REGISTRY_STATE_CONFLICT", transition, db, "study", STUDY, "v1", "retire", "local:carol", "retire", 4)
        transition(db, "study", STUDY, "v2", "revoke", "local:bob", "approval withdrawn", 3)
        db.flush()
        failure("APPROVED_REGISTRY_VERSION_REQUIRED", released_version, db, "study", STUDY)
        failure("REGISTRY_VERSION_NOT_FOUND", transition, db, "study", "missing", "v1", "approve", "local:bob", "review", 1)
        with pytest.raises(ValueError):
            transition(db, "study", STUDY, "v2", "retire", "local:bob", " ", 4)


def test_pending_expired_corrupt_and_unbounded_history_never_authorize(client, account):
    with factory().begin() as db:
        submit(db, "study", study(account), "local:alice")
        assert released_version(db, "study", STUDY, required=False) is None
        failure("REGISTRY_HISTORY_LIMIT", history, db, "study", STUDY, limit=0)
        transition(db, "study", STUDY, "v1", "approve", "local:bob", "review", 1)
        db.flush()
        transition(db, "study", STUDY, "v1", "release", "local:carol", "release", 2)
        db.flush()
        row = released_version(db, "study", STUDY)
        db.get(Registry, "study:" + STUDY).body = {**row.body, "document_text": "tampered"}
        db.flush()
        failure("REGISTRY_INTEGRITY_FAILURE", released_version, db, "study", STUDY)


def test_changed_scope_cannot_reuse_scientific_hash_or_old_qualification(client, account):
    with factory().begin() as db:
        approve_task(db, account)
        old = active_body(db, "configuration", CONFIGURATION)
        changed = {**old, "version": "v2", "max_duration_ms": old["max_duration_ms"] + 1000}
        assert changed["sha256"] == old["sha256"]  # frozen scientific task identity
        submit(db, "configuration", changed, "local:alice")
        transition(db, "configuration", CONFIGURATION, "v2", "approve", "local:bob", "review new duration", 1)
        db.flush()
        failure("QUALIFICATION_CONFIGURATION_MISMATCH", transition, db, "configuration", CONFIGURATION, "v2", "release", "local:carol", "release", 2)
        assert active_body(db, "configuration", CONFIGURATION) == old
    with pytest.raises(ValueError):
        validate_submission("configuration", {**configuration(), "sha256": "9" * 64})
    changed_material = deepcopy(configuration())
    changed_material["material"]["configuration_id"] = "unimplemented-task"
    with pytest.raises(ValueError):
        validate_submission("configuration", changed_material)


def test_missing_decisions_and_expiry_fail_closed_with_preserved_history(client, account, monkeypatch):
    with factory().begin() as db:
        approve_task(db, account)
        current = released_version(db, "study", STUDY)
        end = current.body["expires_at"]
    monkeypatch.setattr("otgd.operator_governance.now", lambda: end + 1)
    with factory()() as db:
        assert history(db, "study", STUDY)["items"][0]["effective_state"] == "expired"
        assert released_version(db, "study", STUDY, required=False) is None
    monkeypatch.undo()
    with factory().begin() as db:
        row = released_version(db, "study", STUDY)
        event = db.scalar(select(RegistryEvent).where(RegistryEvent.version_id == row.id, RegistryEvent.state == "approved"))
        db.delete(event)
        db.flush()
        failure("REGISTRY_APPROVAL_HISTORY_INVALID", released_version, db, "study", STUDY)


@pytest.mark.parametrize("kind,change", [
    ("study", {"document_sha256": "9" * 64}), ("study", {"study_id": "different"}),
    ("study", {"account_refs": ["invalid-uuid"]}), ("study", {"expires_at": float("nan")}),
    ("study", {"unexpected": "arbitrary"}), ("study", {"version": "../invalid"}),
    ("study", {"document_text": "é" * 40000}),
    ("retention", {"raw_notice_sha256": "9" * 64}),
    ("retention", {"raw_kinds": ["eye_video", "eye_video"]}),
    ("retention", {"max_retention_days": 3651}),
    ("retention", {"policy_id": "wrong-id"}),
])
def test_strict_bounded_typed_submission_rejects_bad_material(client, account, kind, change):
    value = study(account) if kind == "study" else retention()
    with pytest.raises(ValueError):
        validate_submission(kind, {**value, **change})


def test_invalid_key_calibration_and_configuration_scopes(client, account):
    with pytest.raises(ValueError):
        validate_submission("unsupported", {})
    with pytest.raises(ValueError):
        validate_submission("study", {**study(account), "expires_at": now()-1})
    with pytest.raises(ValueError):
        validate_submission("study", {**study(account), "account_refs": [account, account]})
    for key in ("not-base64", base64.b64encode(rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)).decode()):
        with pytest.raises(ValueError):
            validate_submission("device", {**device(account), "public_key_spki": key})
    with pytest.raises(ValueError):
        validate_submission("device", {**device(account), "registry_id": "different"})
    for fields in ({"model_id": "not-device"}, {"channels": []}, {"purpose": "model"}):
        with pytest.raises(ValueError):
            validate_submission("calibration", {**calibration(), **fields})
    for config in (configuration("cardiac"), {**configuration(), "supported_phone_models": []},
        {**configuration(), "configuration_id": "different"}, configuration("eyes")):
        with pytest.raises(ValueError):
            validate_submission("configuration", config)
    validate_submission("calibration", common("model-cal", calibration_id="model-cal", purpose="model", model_id="fictional-model", calibration_sha256="2" * 64))
    with pytest.raises(ValueError):
        validate_submission("study", {**study(account), "document_text": "x" * 262144})


def test_release_rechecks_exact_dependencies_not_approval_strings(client, account):
    with factory().begin() as db:
        approve(db, "study", study(account))
        approve(db, "retention", retention())
        approve(db, "qualification", proof())
        bad = {**configuration(), "protocol_id": "unapproved-protocol"}
        submit(db, "configuration", bad, "local:alice")
        transition(db, "configuration", CONFIGURATION, "v1", "approve", "local:bob", "review", 1)
        db.flush()
        failure("REGISTRY_SCOPE_MISMATCH", transition, db, "configuration", CONFIGURATION, "v1", "release", "local:carol", "release", 2)
        failure("QUALIFICATION_CONFIGURATION_MISMATCH", validate_dependencies, db, "configuration", {**configuration(), "sha256": "7" * 64})
        transition(db, "retention", POLICY, "v1", "retire", "local:carol", "policy expired", 3)
        db.flush()
        failure("APPROVED_REGISTRY_VERSION_REQUIRED", validate_dependencies, db, "configuration", configuration())


def test_capabilities_change_with_consent_revision_notice_expiry_and_revoke(client, account):
    with factory().begin() as db:
        approve_task(db, account)
    initial = client.get("/v1/me/capabilities", headers=headers()).json()
    assert initial["channels"]["task"]["reason_codes"] == ["CAPABILITY_DENIED"]
    assert not initial["channels"]["cardiac"]["available"]
    consent(client, study(account))
    enabled = client.get("/v1/me/capabilities", headers=headers()).json()
    assert enabled["channels"]["task"]["available"] and enabled["channels"]["task"]["authorization_available"]
    assert enabled["channels"]["task"]["configurations"][0]["configuration_id"] == CONFIGURATION
    assert not enabled["inference_available"]
    with factory().begin() as db:
        owner = db.get(Account, account)
        owner.notice = None
        assert channel_capabilities(db, owner)["task"]["reason_codes"] == ["NOTICE_ACK_REQUIRED"]
        owner.state = "deleting"
        assert channel_capabilities(db, owner)["task"]["reason_codes"] == ["ACCOUNT_NOT_ACTIVE"]
        owner.state = "active"
        from otgd.domain import NOTICE_SHA
        owner.notice = NOTICE_SHA
        old = record(db, owner, "consent", STUDY)
        old.body = {**old.body, "document_version": "old"}
        db.flush()
        assert channel_capabilities(db, owner)["task"]["reason_codes"] == ["CURRENT_CONSENT_REQUIRED"]
    with factory().begin() as db:
        transition(db, "configuration", CONFIGURATION, "v1", "revoke", "local:carol", "fixture qualification withdrawn", 3)
    assert not client.get("/v1/me/capabilities", headers=headers()).json()["channels"]["task"]["available"]


def test_real_session_start_requires_current_approved_study_and_exact_protocol(client, account):
    from uuid import uuid4
    with factory().begin() as db:
        approve_task(db, account)
    payload = {"session_id": str(uuid4()), "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL}
    assert client.post("/v1/sessions", headers=headers(), json=payload).status_code == 403
    consent(client, study(account))
    assert client.post("/v1/sessions", headers=headers(), json=payload).status_code == 201
    assert client.post("/v1/sessions", headers=headers(), json={**payload, "session_id": str(uuid4()), "protocol_id": "wrong"}).status_code == 403
    with factory().begin() as db:
        db.get(Registry, "study:" + STUDY).active = False
    assert client.post("/v1/sessions", headers=headers(), json={**payload, "session_id": str(uuid4())}).status_code == 403


def test_online_task_start_is_signed_and_old_grant_cannot_survive_envelope_renewal(client, account, capture_signer):
    import base64
    import json
    import os
    from uuid import uuid4
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from otgd.capture_signing import DOMAIN
    from otgd.canonical import canonical
    from otgd.config import ROOT

    with factory().begin() as db:
        approve_task(db, account)
    consent(client, study(account))
    sid, aid, rid = (str(uuid4()) for _ in range(3))
    created = client.post("/v1/sessions", headers=headers(), json={
        "session_id": sid, "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL})
    assert created.status_code == 201, created.text
    with factory()() as db:
        config = deepcopy(active_body(db, "configuration", CONFIGURATION))
    context = {"schema_version": "1.0.0", "session_id": sid, "context_confirmed_at": iso(),
        "profile_version_id": None, "profile_snapshot_sha256": "a" * 64,
        "history_snapshot_sha256": "b" * 64, "protocol_id": PROTOCOL,
        "configuration_refs": [{"id": CONFIGURATION, "version": "v1", "sha256": config["sha256"], "scope": "measurement_collection"}],
        "baseline_refs": [], "device_associations": [], "self_report_context": None}
    assert client.put(f"/v1/sessions/{sid}/context", headers=headers(revision=0), json=context).status_code == 200
    attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid,
        "component": "task", "record_id": rid, "supersedes_attempt_id": None,
        "status": "started", "source": "prototype_sensor", "started_at": iso(), "ended_at": None,
        "configuration_id": CONFIGURATION, "configuration_hash": config["sha256"],
        "quality_flags": [], "component_metadata": {}, "artifact_refs": [], "attestation_refs": []}
    assert client.put(f"/v1/sessions/{sid}/attempts/{aid}", headers=headers(revision=0), json=attempt).status_code == 200
    request = {"attempt_id": aid, "channel": "task", "binding_id": None, "device_id": None,
        "configuration_id": CONFIGURATION, "configuration_hash": config["sha256"]}
    granted = client.post(f"/v1/sessions/{sid}/capture-authorizations", headers=headers(), json=request)
    assert granted.status_code == 201, granted.text
    authority = granted.json()
    assert authority["configuration_submitted_sha256"] == digest(config)
    assert authority["capture_context_sha256"] == digest(context)
    started = client.post(f"/v1/sessions/{sid}/capture-authorizations/{authority['authorization_id']}/start",
        headers=headers(), json={"attempt_id": aid, "device_boot_id": None, "device_nonce": None})
    assert started.status_code == 200, started.text
    token = started.json()["server_start"]
    capture_signer.public_key().verify(base64.b64decode(token["signature"]),
        DOMAIN.encode() + canonical(token["grant"]), ec.ECDSA(hashes.SHA256()))
    assert token["grant"]["channel"] == "task" and token["grant"]["configuration_max_duration_ms"] == config["max_duration_ms"]
    if os.environ.get("OTGD_WRITE_CAPTURE_FIXTURE") == "1":
        fixture = {"fixture_scope": "FICTIONAL-SOFTWARE-APPROVAL-NOT-PHYSICAL-QUALIFICATION",
            "authorization": authority, "start": started.json(), "context": context,
            "server_public_key_spki": base64.b64encode(capture_signer.public_key().public_bytes(
                serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)).decode()}
        (ROOT / "apps/mobile/testfixtures/backend-capture-authorization.json").write_text(json.dumps(fixture, indent=2) + "\n")
    second = client.post(f"/v1/sessions/{sid}/capture-authorizations", headers=headers(), json=request).json()
    with factory().begin() as db:
        changed = {**config, "version": "v2", "max_duration_ms": config["max_duration_ms"] + 1000,
            "qualification_evidence_ref": "fictional-new-task-proof"}
        evidence = proof(config_body=changed)
        evidence["registry_id"] = changed["qualification_evidence_ref"]
        approve(db, "qualification", evidence)
        approve(db, "configuration", changed)
    denied = client.post(f"/v1/sessions/{sid}/capture-authorizations/{second['authorization_id']}/start",
        headers=headers(), json={"attempt_id": aid, "device_boot_id": "FICTIONAL-PHONE-BOOT"})
    assert denied.status_code == 403 and denied.json()["code"] == "CONFIGURATION_APPROVAL_CHANGED"


def test_optical_evidence_cannot_relabel_a_different_authorized_attempt_or_acquisition_clock():
    from .test_optical_evidence import fixture

    raw, projection, config = fixture()
    attempt = {"attempt_id": "33333333-3333-4333-8333-333333333333",
        "record_id": raw["run_id"], "started_at": raw["started_at"], "ended_at": raw["ended_at"],
        "component_metadata": {"native_result": raw, "projection": projection}}
    authority = SimpleNamespace(body={"authorization_id": raw["authorization_id"]})
    validated = validate_optical_attempt(None, None, None, attempt, config, authority)
    assert validated["physical_onset_verified"] is False and validated["model_eligible"] is False
    for changed in ({"run_id": "44444444-4444-4444-8444-444444444444"},
        {"authorization_id": "55555555-5555-4555-8555-555555555555"},
        {"started_at": "2026-10-11T00:00:00.001Z"}, {"ended_at": "2026-10-11T00:00:02Z"}):
        forged = {**attempt, "component_metadata": {"native_result": {**raw, **changed}, "projection": projection}}
        failure("OPTICAL_CAPTURE_IDENTITY_MISMATCH", validate_optical_attempt, None, None, None, forged, config, authority)


def test_prestart_invalid_optical_attempt_retains_arm_lineage_without_invented_camera_evidence(client, account):
    from uuid import uuid4
    with factory().begin() as db:
        approve_task(db, account)
    consent(client, study(account))
    sid, aid, rid = (str(uuid4()) for _ in range(3))
    response = client.post("/v1/sessions", headers=headers(), json={
        "session_id": sid, "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL})
    assert response.status_code == 201
    attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid,
        "component": "eyes", "record_id": rid, "supersedes_attempt_id": None,
        "status": "started", "source": "prototype_sensor", "started_at": iso(), "ended_at": None,
        "configuration_id": "fictional-requested-camera-config", "configuration_hash": "c" * 64, "quality_flags": [],
        "component_metadata": {}, "artifact_refs": [], "attestation_refs": []}
    path = f"/v1/sessions/{sid}/attempts/{aid}"
    assert client.put(path, headers=headers(revision=0), json=attempt).status_code == 200
    projection = {"status": "invalid", "source": "prototype_sensor", "started_at": None, "ended_at": None,
        "quality_flags": ["CAMERA_UNSUPPORTED_BEFORE_ACQUISITION"], "capture_config_id": "fictional-requested-camera-config",
        "camera_id": "fictional-requested-camera", "frame_rate_hz": None, "scale_basis": "unscaled",
        "baseline_diameter_mm": None, "relative_constriction": None, "latency_ms": None, "raw_artifact_id": None}
    terminal = {**attempt, "status": "invalid", "started_at": None, "quality_flags": projection["quality_flags"],
        "component_metadata": {"armed_at": attempt["started_at"], "native_result": None, "projection": projection}}
    forged = deepcopy(terminal)
    forged["component_metadata"]["projection"]["relative_constriction"] = 0.3
    denied = client.put(path, headers=headers(revision=1), json=forged)
    assert denied.status_code == 422 and denied.json()["code"] == "INVALID_OPTICAL_FEATURES"
    accepted = client.put(path, headers=headers(revision=1), json=terminal)
    assert accepted.status_code == 200, accepted.text
    with factory()() as db:
        owner = db.get(Account, account)
        persisted = record(db, owner, "attempt", aid).body
        assert persisted["component_metadata"]["native_result"] is None
        assert persisted["started_at"] is None and persisted["ended_at"] is None
        assert persisted["component_metadata"]["armed_at"] == attempt["started_at"]


def test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot(client, account, capture_signer, monkeypatch):
    import json
    import os
    from uuid import uuid4
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from otgd.capture_signing import DOMAIN
    from otgd.canonical import canonical
    from otgd.config import ROOT
    from otgd import operator_governance as governance
    from .governance_fixture import adc_material, acknowledge_cardiac

    # A hypothetical shipped-driver inventory exercises authority software only;
    # this scoped test override neither provisions hardware nor changes release inventory.
    monkeypatch.setitem(governance.SOFTWARE_ADAPTERS, "cardiac", {"otgd_signed_reader_v1"})
    monkeypatch.setitem(governance.PHYSICAL_DRIVERS, "cardiac", {"otgd_esp32_adc_v1"})
    device_private = ec.generate_private_key(ec.SECP256R1())
    material = adc_material()
    value = configuration("cardiac", material=material, sha256=digest(material), max_duration_ms=material["duration_ms"],
        software_adapter_id="otgd_signed_reader_v1", device_id=DEVICE, key_id=KEY,
        calibration_id=CALIBRATION, approved_hardware=["fixture-hw"], approved_firmware=["1.0.0"])
    with factory().begin() as db:
        for kind, body in (("study", study(account, {"cardiac": value["registry_id"]})),
            ("retention", retention()), ("device", {**device(account, device_private), "firmware_version": "1.0.0"}),
            ("calibration", {**calibration(), "firmware_versions": ["1.0.0"]}), ("qualification", proof("cardiac", config_body=value)),
            ("configuration", value)):
            approve(db, kind, body)
        config = deepcopy(active_body(db, "configuration", value["registry_id"]))
    consent(client, study(account))
    challenge = client.post("/v1/device-bindings/challenges", headers=headers(), json={"device_id": DEVICE, "key_id": KEY})
    assert challenge.status_code == 201, challenge.text
    signature = base64.b64encode(device_private.sign(b"OTGD-BIND-v1\n" + canonical(challenge.json()["transcript"]), ec.ECDSA(hashes.SHA256()))).decode()
    bound = client.post("/v1/device-bindings", headers=headers(), json={"challenge_id": challenge.json()["challenge_id"], "signature": signature})
    assert bound.status_code == 201, bound.text
    sid, aid, rid = (str(uuid4()) for _ in range(3))
    created = client.post("/v1/sessions", headers=headers(), json={
        "session_id": sid, "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL})
    assert created.status_code == 201, created.text
    context = {"schema_version": "1.0.0", "session_id": sid, "context_confirmed_at": iso(),
        "profile_version_id": None, "profile_snapshot_sha256": "a" * 64, "history_snapshot_sha256": "b" * 64,
        "protocol_id": PROTOCOL, "configuration_refs": [{"id": value["registry_id"], "version": "v1", "sha256": config["sha256"], "scope": "measurement_collection"}],
        "baseline_refs": [], "self_report_context": None, "device_associations": [{
            **{key: bound.json()[key] for key in ("binding_id", "device_id", "hardware_revision", "firmware_version")},
            "boot_id": "77777777-7777-4777-8777-777777777777", "clock_evidence_ref": None}]}
    assert client.put(f"/v1/sessions/{sid}/context", headers=headers(revision=0), json=context).status_code == 200
    attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid, "component": "cardiac", "record_id": rid,
        "supersedes_attempt_id": None, "status": "started", "source": "prototype_sensor", "started_at": iso(), "ended_at": None,
        "configuration_id": config["configuration_id"], "configuration_hash": config["sha256"], "quality_flags": [],
        "component_metadata": {"modality": "ppg"}, "artifact_refs": [], "attestation_refs": []}
    assert client.put(f"/v1/sessions/{sid}/attempts/{aid}", headers=headers(revision=0), json=attempt).status_code == 200
    instruction = acknowledge_cardiac(client, sid, attempt, config)
    granted = client.post(f"/v1/sessions/{sid}/capture-authorizations", headers=headers(), json={
        "instruction_receipt_id": instruction["instruction_receipt_id"],
        "attempt_id": aid, "channel": "cardiac", "binding_id": bound.json()["binding_id"], "device_id": DEVICE,
        "configuration_id": config["configuration_id"], "configuration_hash": config["sha256"]})
    assert granted.status_code == 201, granted.text
    path = f"/v1/sessions/{sid}/capture-authorizations/{granted.json()['authorization_id']}/start"
    payload = {"attempt_id": aid, "device_boot_id": "77777777-7777-4777-8777-777777777777",
        "device_nonce": base64.urlsafe_b64encode(b"B" * 32).decode().rstrip("=")}
    wrong_boot = client.post(path, headers=headers(), json={**payload, "device_boot_id": "88888888-8888-4888-8888-888888888888"})
    assert wrong_boot.status_code == 403 and wrong_boot.json()["code"] == "DEVICE_CONTEXT_MISMATCH"
    no_nonce = client.post(path, headers=headers(), json={**payload, "device_nonce": None})
    assert no_nonce.status_code == 403
    started = client.post(path, headers=headers(), json=payload)
    assert started.status_code == 200, started.text
    token = started.json()["server_start"]
    capture_signer.public_key().verify(base64.b64decode(token["signature"]), DOMAIN.encode() + canonical(token["grant"]), ec.ECDSA(hashes.SHA256()))
    assert token["grant"]["binding_id"] == bound.json()["binding_id"]
    assert token["grant"]["device_nonce"] == payload["device_nonce"] and token["grant"]["boot_id"] == payload["device_boot_id"]
    assert token["grant"]["raw_recording_permission"] is None
    if os.environ.get("OTGD_WRITE_CAPTURE_FIXTURE") == "1":
        fixture = {"fixture_scope": "FICTIONAL-SERVER-AND-READER-KEYS-FOR-PROTOCOL-TESTS-NOT-PHYSICAL-QUALIFICATION",
            "authorization": granted.json(), "start": started.json(), "context": context,
            "server_public_key_spki": base64.b64encode(capture_signer.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)).decode()}
        (ROOT / "apps/mobile/testfixtures/backend-reader-capture-authorization.json").write_text(json.dumps(fixture, indent=2) + "\n")


def test_typed_adc_material_retains_counts_and_rejects_unreviewed_pins_units_or_unbounded_deadlines():
    from pydantic import ValidationError
    from otgd.operator_governance import ADCMaterial

    material = {"schema_version": "1.0.0", "channel": "cardiac", "modality": "ppg",
        "adapter_id": "otgd_esp32_adc_v1", "protocol_version": 1, "duration_ms": 15000,
        "end_guard_ms": 50, "sample_rate_hz": 100, "raw_unit": "counts",
        "raw_sample_limit": 0, "raw_encoding": None,
        "extractor_version": "adc_peak_intervals_v1", "input_gpio": 1, "contact_gpio": 4,
        "contact_active_high": True, "adc_resolution_bits": 12, "attenuation_db": 11,
        "reference_mv": 3300.0, "gain": 1.0, "offset_mv": 0.0, "threshold_adc": 2048,
        "minimum_peak_interval_ms": 250, "maximum_peak_interval_ms": 2000, "minimum_amplitude_adc": 100}
    assert ADCMaterial.model_validate(material).data() == material
    assert ADCMaterial.model_validate({**material, "channel": "ecg", "modality": "ecg"}).raw_unit == "counts"
    for changed in ({"contact_gpio": 1}, {"contact_gpio": 3}, {"sample_rate_hz": 1001},
        {"end_guard_ms": 101}, {"duration_ms": 999}, {"sample_rate_hz": 100.0},
        {"sample_rate_hz": 19}, {"reference_mv": 499}, {"gain": 100001},
        {"raw_unit": "mV"}, {"minimum_peak_interval_ms": 2000}, {"modality": "ecg"}):
        with pytest.raises(ValidationError):
            ADCMaterial.model_validate({**material, **changed})
    config = configuration("cardiac", material=material, sha256=digest(material), max_duration_ms=15000,
        software_adapter_id="otgd_signed_reader_v1", device_id=DEVICE, key_id=KEY,
        calibration_id=CALIBRATION, approved_hardware=["fixture-hw"], approved_firmware=["fixture-fw"])
    value = validate_submission("configuration", config)
    assert value["sha256"] == digest(material)
    with pytest.raises(ValueError):
        validate_submission("configuration", {**config, "material": {**material, "gain": 2.0}})


def test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec(monkeypatch):
    from pydantic import ValidationError
    from otgd import operator_governance as governance
    from .governance_fixture import adc_material, acknowledge_cardiac

    generic = configuration("cardiac", software_adapter_id="otgd_signed_reader_v1")
    monkeypatch.setitem(governance.SOFTWARE_ADAPTERS, "cardiac", {"otgd_signed_reader_v1"})
    assert not governance.software_supported(generic)
    monkeypatch.setitem(governance.PHYSICAL_DRIVERS, "cardiac", {"otgd_esp32_adc_v1"})
    assert not governance.software_supported(generic)
    adc = {**generic, "material": adc_material()}
    assert governance.software_supported(adc)
    assert not governance.raw_recording_supported(adc, "ecg_waveform")
    waveform = {**adc_material("ecg"), "duration_ms": 1000, "sample_rate_hz": 20,
        "raw_unit": "mV", "raw_sample_limit": 20, "raw_encoding": "otgd_ecg_samples_v1"}
    assert governance.ADCMaterial.model_validate(waveform).raw_sample_limit == 20
    assert governance.raw_recording_supported({**adc, "channel": "ecg", "material": waveform}, "ecg_waveform")
    assert not governance.software_supported({**adc, "channel": "ecg", "material": {**waveform, "raw_unit": "counts"}})
    assert not governance.raw_recording_supported({**adc, "channel": "ecg", "material": {**waveform, "raw_unit": "counts"}}, "ecg_waveform")
    for changed in ({"raw_sample_limit": 0}, {"raw_encoding": None}, {"sample_rate_hz": 1000},
        {"channel": "cardiac", "modality": "ppg"}):
        with pytest.raises(ValidationError):
            governance.ADCMaterial.model_validate({**waveform, **changed})


def test_current_raw_permission_is_signed_and_old_preference_replay_cannot_restart_after_revocation(client, account, monkeypatch):
    from uuid import uuid4
    from otgd import operator_governance as governance
    from .test_optical_evidence import fixture as optical_fixture

    # Explicit hypothetical build inventory exercises authority without claiming
    # a real approved camera, phone or independently measured optical evidence.
    monkeypatch.setitem(governance.SOFTWARE_ADAPTERS, "eyes", {"optical_roi_v1"})
    _, _, optical = optical_fixture()
    config = validate_submission("configuration", configuration("eyes", material=optical["material"],
        sha256=optical["sha256"], max_duration_ms=optical["material"]["duration_ms"],
        software_adapter_id="optical_roi_v1", supported_phone_models=optical["supported_phone_models"],
        supported_os_versions=optical["supported_os_versions"], supported_native_builds=optical["supported_native_builds"],
        optical_safety_ref="FICTIONAL-OPTICAL-SAFETY-NOT-HUMAN-APPROVAL", raw_retention_approved=True))
    policy = retention(raw_kinds=["eye_video"])
    with factory().begin() as db:
        for kind, value in (("study", study(account, {"eyes": config["registry_id"]})),
            ("retention", policy), ("qualification", proof("eyes", config)), ("configuration", config)):
            approve(db, kind, value)
    accepted_consent = consent(client, study(account))
    preferences = {"consent_record_id": accepted_consent["consent_record_id"],
        "policy_id": POLICY, "policy_version": "v1", "policy_sha256": digest(policy),
        "raw_notice_version": policy["raw_notice_version"], "raw_notice_sha256": policy["raw_notice_sha256"],
        "acknowledged_at": iso(), "choices": {"eye_video": {"record": True, "upload": False},
            "ecg_waveform": {"record": False, "upload": False}}}
    preference_headers = headers()
    preference_path = f"/v1/studies/{STUDY}/raw-recording-preferences"
    initial = client.post(preference_path, headers=preference_headers, json=preferences)
    assert initial.status_code == 201, initial.text
    sid, aid, rid = (str(uuid4()) for _ in range(3))
    assert client.post("/v1/sessions", headers=headers(), json={"session_id": sid,
        "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL}).status_code == 201
    context = {"schema_version": "1.0.0", "session_id": sid, "context_confirmed_at": iso(),
        "profile_version_id": None, "profile_snapshot_sha256": "a" * 64, "history_snapshot_sha256": "b" * 64,
        "protocol_id": PROTOCOL, "configuration_refs": [{"id": config["registry_id"], "version": "v1",
            "sha256": config["sha256"], "scope": "measurement_collection"}],
        "baseline_refs": [], "device_associations": [], "self_report_context": None}
    assert client.put(f"/v1/sessions/{sid}/context", headers=headers(revision=0), json=context).status_code == 200
    attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid, "component": "eyes",
        "record_id": rid, "supersedes_attempt_id": None, "status": "started", "source": "prototype_sensor",
        "started_at": iso(), "ended_at": None, "configuration_id": config["registry_id"],
        "configuration_hash": config["sha256"], "quality_flags": [], "component_metadata": {},
        "artifact_refs": [], "attestation_refs": []}
    assert client.put(f"/v1/sessions/{sid}/attempts/{aid}", headers=headers(revision=0), json=attempt).status_code == 200
    payload = {"attempt_id": aid, "channel": "eyes", "binding_id": None, "device_id": None,
        "configuration_id": config["registry_id"], "configuration_hash": config["sha256"], "raw_recording_kind": "eye_video"}
    path = f"/v1/sessions/{sid}/capture-authorizations"
    one = client.post(path, headers=headers(), json=payload)
    two = client.post(path, headers=headers(), json=payload)
    assert one.status_code == two.status_code == 201, (one.text, two.text)
    start_body = {"attempt_id": aid, "device_boot_id": None, "device_nonce": None}
    started = client.post(path + "/" + one.json()["authorization_id"] + "/start", headers=headers(), json=start_body)
    assert started.status_code == 200, started.text
    permission = started.json()["server_start"]["grant"]["raw_recording_permission"]
    assert permission == one.json()["raw_recording_permission"] and permission["record"] and not permission["upload"]
    revoked = client.post(f"/v1/studies/{STUDY}/raw-recording-revocations", headers=headers(),
        json={"confirmation": True, "artifact_kinds": ["eye_video"]})
    assert revoked.status_code == 200, revoked.text
    replay = client.post(preference_path, headers=preference_headers, json=preferences)
    assert replay.status_code == 201 and replay.json() == initial.json()
    denied = client.post(path + "/" + two.json()["authorization_id"] + "/start", headers=headers(), json=start_body)
    assert denied.status_code == 403 and denied.json()["code"] == "OPTIONAL_RAW_CONSENT_REQUIRED"
    current = client.get(f"/v1/studies/{STUDY}/raw-recordings", headers=headers()).json()
    assert current["choices"]["eye_video"] == {"record": False, "upload": False}


def test_current_device_calibration_binding_and_software_inventory(client, account):
    config = configuration("cardiac", device_id=DEVICE, key_id=KEY, calibration_id=CALIBRATION,
        approved_hardware=["fixture-hw"], approved_firmware=["fixture-fw"])
    config = validate_submission("configuration", config)
    with factory().begin() as db:
        approve(db, "study", study(account, {"cardiac": config["registry_id"]}))
        approve(db, "retention", retention())
        approve(db, "qualification", proof("cardiac", config_body=config))
        approve(db, "device", device(account))
        approve(db, "calibration", calibration())
        approve(db, "configuration", config)
        owner = db.get(Account, account)
        failure("DEVICE_BINDING_REQUIRED", qualified_binding, db, owner, config)
        body = {"binding_id": "fixture-binding", "device_id": DEVICE, "key_id": KEY,
            "hardware_revision": "fixture-hw", "firmware_version": "fixture-fw", "state": "active"}
        binding = save_record(db, owner, "binding", "fixture-binding", body)
        db.flush()
        assert qualified_binding(db, owner, config).id == binding.id
        binding.body = {**body, "firmware_version": "wrong"}
        db.flush()
        failure("DEVICE_BINDING_REQUIRED", qualified_binding, db, owner, config, binding)
        binding.body = body
    consent(client, study(account))
    value = client.get("/v1/me/capabilities", headers=headers()).json()["channels"]["cardiac"]
    assert value["authorization_available"] and not value["available"]
    assert value["reason_codes"] == ["HUMAN_ADAPTER_UNIMPLEMENTED"]
    with factory().begin() as db:
        from otgd.db import Check
        owner = db.get(Account, account)
        failure("HUMAN_ADAPTER_UNIMPLEMENTED", capture_configuration, db, owner, Check(study_id=STUDY, protocol_id=PROTOCOL), "cardiac")
        for changed in ({"approved_hardware": ["wrong"]}, {"approved_firmware": ["wrong"]}, {"calibration_id": "missing"}):
            with pytest.raises(Problem):
                validate_dependencies(db, "configuration", {**config, **changed})


def test_cli_dry_run_apply_history_and_authenticated_cloud_principal(client, account, tmp_path, capsys):
    path = tmp_path / "study.json"
    import json
    path.write_text(json.dumps(study(account)))
    args = parser().parse_args(["--local-principal", "local:alice", "submit", "study", str(path)])
    result = execute(args)
    assert result["mode"] == "dry_run"
    with factory()() as db:
        assert db.scalar(select(RegistryVersion.id)) is None
    args.apply = True
    assert execute(args)["mode"] == "applied"
    for who, command, revision in (("bob", "approve", "1"), ("carol", "release", "2")):
        arguments = parser().parse_args(["--apply", "--local-principal", "local:" + who, command, "study", STUDY, "v1", "--if-revision", revision, "--reason", "Fictional test"])
        assert execute(arguments)["result"]["revision"] == int(revision) + 1
    assert main(["--local-principal", "local:alice", "history", "study", STUDY]) == 0
    assert '"submitted_body"' in capsys.readouterr().out
    assert main(["--local-principal", "local:alice", "submit", "study", str(path)]) == 1
    assert "REGISTRY_VERSION_EXISTS" in capsys.readouterr().out
    with pytest.raises(ValueError):
        principal(settings())
    cloud = SimpleNamespace(environment="qa", aws_region="us-east-2", deployment_account="123456789012")
    arn = "arn:aws:iam::123456789012:role/operator-reviewer"
    sts = SimpleNamespace(get_caller_identity=lambda: {"Account": "123456789012", "Arn": "arn:aws:sts::123456789012:assumed-role/operator-reviewer/fresh-session", "UserId": "AROAFIXTUREROLE:fresh-session"})
    iam = SimpleNamespace(get_role=lambda **kwargs: {"Role": {"Arn": arn, "RoleId": "AROAFIXTUREROLE"}})
    assert principal(cloud, expected_account="123456789012", expected_role_arn=arn, sts=sts, iam=iam) == arn
    with pytest.raises(ValueError, match="configured deployment account"):
        principal(SimpleNamespace(environment="qa", aws_region="us-east-2", deployment_account="999999999999"),
            expected_account="123456789012", expected_role_arn=arn, sts=sts, iam=iam)
    with pytest.raises(ValueError, match="configured deployment partition"):
        principal(cloud, expected_account="123456789012", expected_role_arn=arn.replace("arn:aws:", "arn:aws-us-gov:"), sts=sts, iam=iam)
    for options in ({}, {"local_principal": "local:alice"}, {"expected_account": "123456789012", "expected_role_arn": "arn:aws:iam::999999999999:role/operator-reviewer"}, {"expected_account": "123456789012", "expected_role_arn": "arn:aws:iam::123456789012:role/different"}):
        with pytest.raises(ValueError):
            principal(cloud, sts=sts, iam=iam, **options)
    for path in ("submitter", "reviewer", "releaser"):
        with pytest.raises(ValueError):
            principal(cloud, expected_account="123456789012", expected_role_arn="arn:aws:iam::123456789012:role/" + path + "/operator-reviewer", sts=sts, iam=iam)
    with pytest.raises(ValueError):
        principal(settings(), local_principal="local:alice", expected_account="123456789012")
    fake = SimpleNamespace(bind=SimpleNamespace(dialect=SimpleNamespace(name="postgresql")), execute=lambda _: SimpleNamespace(one=lambda: (settings().app_database_user, True)))
    with pytest.raises(ValueError):
        require_maintenance_db(fake, settings())
    with pytest.raises(ValueError):
        require_maintenance_db(SimpleNamespace(bind=SimpleNamespace(dialect=SimpleNamespace(name="sqlite"))), cloud)


def test_cloud_identity_ignores_ambient_sdk_service_endpoints(monkeypatch):
    import boto3

    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_PROFILE", raising=False)
    for variable in ("AWS_ENDPOINT_URL", "AWS_ENDPOINT_URL_STS", "AWS_ENDPOINT_URL_IAM"):
        monkeypatch.setenv(variable, "https://fictional.invalid")
    # Literal software-only credentials avoid invoking any credential provider or network.
    session = boto3.Session(aws_access_key_id="fictional", aws_secret_access_key="fictional", region_name="us-east-2")
    supplied = []
    def configured_client(service, **options):
        supplied.append(options["config"])
        return session.client(service, **options)
    monkeypatch.setattr("otgd.operator_cli.boto3.client", configured_client)
    for region, suffix in (("us-east-2", "amazonaws.com"), ("cn-north-1", "amazonaws.com.cn")):
        sts = cloud_client("sts", SimpleNamespace(aws_region=region))
        assert sts.meta.endpoint_url == "https://sts." + region + "." + suffix
    assert cloud_client("iam", SimpleNamespace(aws_region="us-east-2")).meta.endpoint_url == "https://iam.amazonaws.com"
    assert all(config.ignore_configured_endpoint_urls is True for config in supplied)


def test_cli_dependency_errors_are_bounded_and_do_not_expose_paths(client, tmp_path, capsys):
    secret_path = tmp_path / "missing-private-maintenance-path.json"
    assert main(["--local-principal", "local:alice", "submit", "study", str(secret_path)]) == 1
    output = capsys.readouterr().out
    assert "OPERATOR_DEPENDENCY_UNAVAILABLE" in output and str(secret_path) not in output


@pytest.mark.postgres
def test_actual_postgresql_retirement_waits_for_current_reference_acceptance_transaction(client, account):
    from concurrent.futures import ThreadPoolExecutor
    from queue import Queue
    from threading import Event
    from time import monotonic
    from otgd.db import engine

    assert engine().dialect.name == "postgresql", "Live gate must provide actual PostgreSQL"
    with factory().begin() as db:
        approve_task(db, account)
    pid_queue = Queue()
    accepted = Event()

    def retire():
        with factory().begin() as db:
            pid_queue.put(db.scalar(text("SELECT pg_backend_pid()")))
            result = transition(db, "configuration", CONFIGURATION, "v1", "retire",
                "local:fixture-releaser", "Fictional retirement concurrency test", 3)
            assert accepted.is_set(), "Retirement cannot commit before the accepted authority read releases its transaction"
            return result

    with ThreadPoolExecutor(max_workers=1) as executor:
        with factory().begin() as db:
            active = active_body(db, "configuration", CONFIGURATION)
            assert active["configuration_id"] == CONFIGURATION
            pending = executor.submit(retire)
            pid = pid_queue.get(timeout=3)
            deadline = monotonic() + 3
            waiting = False
            while monotonic() < deadline:
                with engine().connect() as observer:
                    state = observer.execute(text("SELECT wait_event_type, wait_event FROM pg_stat_activity WHERE pid = :pid"), {"pid": pid}).one()
                if state == ("Lock", "advisory"):
                    waiting = True
                    break
                accepted.wait(0.01)
            assert waiting and not pending.done(), "Actual PostgreSQL must show the exclusive retirement blocked on authority's shared transaction lock"
            accepted.set()
        assert pending.result(timeout=3)["state"] == "retired"
    with factory()() as db:
        failure("APPROVED_REGISTRY_VERSION_REQUIRED", active_body, db, "configuration", CONFIGURATION)


@pytest.mark.postgres
def test_actual_postgresql_preserves_registry_content_and_append_only_decisions(client, account):
    from otgd.db import engine
    from otgd.schema_migrations import migration_003_operator_governance
    assert engine().dialect.name == "postgresql", "Live gate must provide actual PostgreSQL"
    with engine().begin() as connection:
        migration_003_operator_governance(connection)
        migration_003_operator_governance(connection)
    with factory().begin() as db:
        approve(db, "study", study(account))
    for statement in ("UPDATE operator_registry_versions SET body='{}'", "UPDATE operator_registry_versions SET submitted_by='other'", "DELETE FROM operator_registry_versions", "UPDATE operator_registry_events SET reason='changed'", "DELETE FROM operator_registry_events"):
        with pytest.raises(IntegrityError):
            with engine().begin() as connection:
                connection.execute(text(statement))
    with factory()() as db:
        assert len(history(db, "study", STUDY)["items"][0]["decisions"]) == 3
