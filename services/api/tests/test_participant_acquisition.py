"""Independent participant-flow probes using real fictional registry decisions.

No fixture here provisions human approvals or bypasses released authority. The
HTTP client exercises application transactions; storage/hardware are not used.
"""

import base64
import hashlib
from copy import deepcopy
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from otgd.canonical import canonical, digest
from otgd.capture_signing import DOMAIN
from otgd.db import Account, Artifact, Check, Dedup, Record, factory, iso, now
from otgd.domain import NOTICE_SHA, record
from otgd.errors import Problem
from otgd.operator_governance import (
    active_body,
    software_supported,
    submit,
    transition,
)
from otgd.participant_acquisition import (
    CardiacProtocol,
    LaboratoryProtocol,
    require_completed_collections,
)
from pydantic import ValidationError
from sqlalchemy import select

from .conftest import headers
from .governance_fixture import (
    CALIBRATION,
    PROTOCOL,
    STUDY,
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

COLLECTION_METHOD = "FICTIONAL-PARTICIPANT-COLLECTION"
ASSAY_METHOD = "FICTIONAL-INDEPENDENT-LABORATORY-METHOD"
INSTRUMENT = "FICTIONAL-LABORATORY-INSTRUMENT"
CONFIGURATION = "fictional-participant-lab-config"


def write_review_fixture(section, value):
    """Opt-in actual HTTP responses; never an application provisioning seed."""
    import json
    import os
    from pathlib import Path
    if os.environ.get("OTGD_WRITE_PARTICIPANT_FIXTURE") != "1":
        return
    path = Path("/tmp/otgd-participant-acquisition.json")
    result = json.loads(path.read_text()) if path.exists() else {}
    result.update(fixture_scope="FICTIONAL SOFTWARE TEST HTTP RESPONSES; NO HUMAN OR ASSAY APPROVAL; PDF STORAGE DOUBLE")
    result[section] = value
    path.write_text(json.dumps(result, indent=2) + "\n")


def laboratory_protocol():
    text = "FICTIONAL collection instructions for software tests. No human or assay approval."
    return {
        "schema_version": "1.0.0", "kind": "reference_lab",
        "instruction_id": "FICTIONAL-LAB-INSTRUCTIONS", "version": "v1",
        "text": text, "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "maximum_acknowledgment_age_seconds": 120,
        "maximum_collection_submission_delay_seconds": 300,
        "maximum_analysis_delay_seconds": 86400,
        "required_confirmations": [{"id": "method_reviewed", "text": "I reviewed this fictional procedure."}],
        "methods": [{
            "id": COLLECTION_METHOD, "version": "v1",
            "instructions": "FICTIONAL buffered specimen procedure; not for participant use.",
            "saliva_volume_required": True, "buffer_volume_required": True,
            "dilution_factor_required": True,
            "dilution_definition": "total_mixture_over_saliva", "fixed_dilution_factor": None,
            "saliva_volume_min_ml": 0.5, "saliva_volume_max_ml": 2.0,
            "buffer_volume_min_ml": 0.0, "buffer_volume_max_ml": 2.0,
            "collector_lot_required": True, "container_required": True,
            "expiry_required": True, "permitted_containers": ["FICTIONAL-CONTAINER"],
            "required_handling_events": ["sealed"],
            "permitted_null_reasons": ["unknown", "not_applicable"],
        }],
    }


def cardiac_protocol():
    text = "FICTIONAL bench-only cardiac preparation; never human electrical safety evidence."
    return {
        "schema_version": "1.0.0", "kind": "cardiac",
        "instruction_id": "FICTIONAL-CARDIAC-INSTRUCTIONS", "version": "v1",
        "text": text, "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "maximum_acknowledgment_age_seconds": 60,
        "operating_scope": "engineering_bench",
        "operating_state_verifier": "participant_declaration_only",
        "rest_duration_seconds": 300,
        "posture_instruction": "FICTIONAL bench position.",
        "activity_instruction": "FICTIONAL fixed bench state.",
        "contact_instruction": "FICTIONAL bench contact only.",
        "isolation_instruction": "No human connection is authorized.",
        "required_confirmations": [{"id": value, "text": "FICTIONAL declared compliance only."}
            for value in ("rest_completed", "posture_confirmed", "activity_confirmed", "contact_confirmed", "isolation_confirmed")],
        "permitted_setups": [{"id": "FICTIONAL-BENCH", "description": "Engineering fixture only.",
            "power_state": "FICTIONAL-BATTERY", "charging_state": "not_charging",
            "cable_state": "disconnected", "contact_or_lead_configuration": "bench_fixture"}],
    }


@pytest.fixture
def collection_scope(client, account, request):
    material = {"schema_version": "1.0.0", "channel": "saliva", "source": "reference_lab",
        "collection_method_ids": [COLLECTION_METHOD], "assay_bases": ["free"],
        "concentration_bases": ["collected_mixture"], "correction_statuses": ["not_corrected"]}
    protocol = laboratory_protocol()
    adjustments = getattr(request, "param", {})
    protocol["methods"][0].update(adjustments.get("method_changes", {}))
    protocol.update(adjustments.get("protocol_changes", {}))
    operator = None
    if adjustments.get("staff"):
        operator = client.get("/v1/me/capabilities", headers=headers(sub="staff")).json()["account_ref"]
        acknowledged = client.post("/v1/me/acknowledgments", headers=headers(sub="staff"), json={
            "version": "v1", "sha256": NOTICE_SHA, "acknowledged_at": iso()})
        assert acknowledged.status_code == 200, acknowledged.text
    value = configuration("saliva", registry_id=CONFIGURATION, configuration_id=CONFIGURATION,
        material=material, sha256=digest(material), max_duration_ms=600000,
        software_adapter_id="reference_lab_import_v1",
        lab_methods={ASSAY_METHOD: {"calibration_ids": [CALIBRATION], "instrument_ids": [INSTRUMENT]}},
        participant_protocol=protocol)
    chosen_study = study(account, {"saliva": CONFIGURATION})
    if operator:
        chosen_study["account_refs"].append(operator)
    policy = retention()
    if operator:
        from otgd.lab_handoff import PURPOSE
        policy.update(purpose_id=PURPOSE, access_roles=["lab_importer"])
    with factory().begin() as db:
        for kind, body in (
            ("study", chosen_study), ("retention", policy),
            ("device", device(account)), ("calibration", calibration()),
            ("method", common(ASSAY_METHOD, method_id=ASSAY_METHOD,
                assay_bases=["free"], collection_method_ids=[COLLECTION_METHOD],
                instrument_ids=[INSTRUMENT], laboratory_ids=["FICTIONAL-LAB"])),
            ("qualification", proof("saliva", value)), ("configuration", value),
        ):
            approve(db, kind, body)
        if operator:
            approve(db, "role", common(operator, account_ref=operator,
                roles=["lab_import"], study_ids=[STUDY]))
        config = deepcopy(active_body(db, "configuration", CONFIGURATION))
    accepted = client.post(f"/v1/studies/{STUDY}/consents", headers=headers(), json={
        **{key: chosen_study[key] for key in ("invitation_id", "document_version", "document_sha256")},
        "accepted": True, "acknowledged_at": iso(),
    })
    assert accepted.status_code == 201, accepted.text
    sid = str(uuid4())
    created = client.post("/v1/sessions", headers=headers(), json={"session_id": sid,
        "mode": "controlled_research", "study_id": STUDY, "protocol_id": PROTOCOL})
    assert created.status_code == 201, created.text
    frozen = session_fixture(account)
    frozen["profile"]["source"] = "study_measurement"
    frozen.update(session_id=sid, mode="controlled_research", study_id=STUDY, protocol_id=PROTOCOL,
        created_at=iso(), target_at=iso())
    frozen["target_at"] = frozen["created_at"]
    context = {"schema_version": "1.0.0", "session_id": sid, "context_confirmed_at": iso(),
        "profile_version_id": None, "profile_snapshot_sha256": digest(frozen["profile"]),
        "history_snapshot_sha256": digest(frozen["history"]), "protocol_id": PROTOCOL,
        "configuration_refs": [{"id": CONFIGURATION, "version": "v1", "sha256": config["sha256"],
            "scope": "measurement_collection"}], "baseline_refs": [], "device_associations": [],
        "self_report_context": None}
    context["context_confirmed_at"] = frozen["created_at"]
    saved = client.put(f"/v1/sessions/{sid}/context", headers=headers(revision=0), json=context)
    assert saved.status_code == 200, saved.text
    return {"account": account, "session_id": sid, "config": config,
        "consent": accepted.json(), "context": context, "frozen": frozen, "operator": operator}


def start_collection(client, scope, supersedes=None, sample_id=None):
    sid, aid, sample = scope["session_id"], str(uuid4()), sample_id or str(uuid4())
    config = scope["config"]
    attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid,
        "component": "saliva", "record_id": sample, "supersedes_attempt_id": supersedes,
        "status": "started", "source": "reference_lab", "started_at": iso(), "ended_at": None,
        "configuration_id": CONFIGURATION, "configuration_hash": config["sha256"],
        "quality_flags": [], "component_metadata": {}, "artifact_refs": [], "attestation_refs": []}
    saved = client.put(f"/v1/sessions/{sid}/attempts/{aid}", headers=headers(revision=0), json=attempt)
    assert saved.status_code == 200, saved.text
    ack = {"attempt_id": aid, "configuration_id": CONFIGURATION,
        "configuration_version": config["version"], "configuration_hash": config["sha256"],
        "configuration_submitted_sha256": digest(config),
        "participant_protocol_sha256": digest(config["participant_protocol"]),
        "acknowledged_at": iso(), "confirmed": True, "confirmations": ["method_reviewed"],
        "setup_id": None, "rest_started_at": None,
        "collection_method_id": COLLECTION_METHOD, "collection_method_version": "v1"}
    return {**scope, "attempt": attempt, "attempt_id": aid, "sample_id": sample, "ack": ack}


def acknowledge_and_start(client, run):
    sid = run["session_id"]
    ack_headers = headers()
    receipt = client.post(f"/v1/sessions/{sid}/instruction-acknowledgments", headers=ack_headers, json=run["ack"])
    assert receipt.status_code == 201, receipt.text
    grant_body = {"attempt_id": run["attempt_id"], "channel": "saliva", "binding_id": None,
        "device_id": None, "configuration_id": CONFIGURATION,
        "configuration_hash": run["config"]["sha256"], "raw_recording_kind": None,
        "instruction_receipt_id": receipt.json()["instruction_receipt_id"]}
    grant = client.post(f"/v1/sessions/{sid}/capture-authorizations", headers=headers(), json=grant_body)
    assert grant.status_code == 201, grant.text
    started = client.post(f"/v1/sessions/{sid}/capture-authorizations/{grant.json()['authorization_id']}/start",
        headers=headers(), json={"attempt_id": run["attempt_id"], "device_boot_id": None, "device_nonce": None})
    assert started.status_code == 200, started.text
    return {**run, "receipt": receipt.json(), "ack_headers": ack_headers,
        "grant_body": grant_body, "grant": grant.json(), "start": started.json()}


def collection_body(run, **changes):
    collected = iso()
    value = {"attempt_id": run["attempt_id"], "sample_id": run["sample_id"],
        "instruction_receipt_id": run["receipt"]["instruction_receipt_id"],
        "collection_method_id": COLLECTION_METHOD, "collection_method_version": "v1",
        "collected_at": collected, "status": "valid", "quality_flags": [],
        "saliva_volume_ml": 1.0, "buffer_volume_ml": 1.0, "dilution_factor": 2.0,
        "collector_id": "FICTIONAL-COLLECTOR", "collector_lot": "FICTIONAL-KIT-LOT",
        "container_id": "FICTIONAL-CONTAINER", "cartridge_lot": None,
        "cartridge_expiry": iso(now() + 3600),
        "missing_reasons": {"cartridge_lot": "not_applicable"},
        "storage_handling_events": [{"event": "sealed", "occurred_at": collected,
            "temperature_c": None, "duration_min": None}]}
    value.update(changes)
    return value


def test_protocol_requires_exact_bounded_content_complete_setup_and_method_rules():
    lab, cardiac = laboratory_protocol(), cardiac_protocol()
    assert LaboratoryProtocol.model_validate(lab).data() == lab
    assert CardiacProtocol.model_validate(cardiac).data() == cardiac
    cases = []
    bad = deepcopy(lab); bad["text"] += " Unreviewed addition."; cases.append((LaboratoryProtocol, bad))
    bad = deepcopy(lab); bad["required_confirmations"] *= 2; cases.append((LaboratoryProtocol, bad))
    bad = deepcopy(lab); bad["methods"][0]["permitted_containers"] *= 2; cases.append((LaboratoryProtocol, bad))
    bad = deepcopy(lab); bad["methods"][0]["permitted_null_reasons"] = ["fabricated"]; cases.append((LaboratoryProtocol, bad))
    bad = deepcopy(lab); bad["methods"][0]["buffer_volume_min_ml"] = 3.0; cases.append((LaboratoryProtocol, bad))
    bad = deepcopy(lab); bad["methods"][0]["dilution_definition"] = None; cases.append((LaboratoryProtocol, bad))
    bad = deepcopy(cardiac); del bad["permitted_setups"][0]["power_state"]; cases.append((CardiacProtocol, bad))
    bad = deepcopy(cardiac); bad["permitted_setups"] *= 2; cases.append((CardiacProtocol, bad))
    bad = deepcopy(cardiac); bad["required_confirmations"].pop(); cases.append((CardiacProtocol, bad))
    bad = deepcopy(cardiac); bad["maximum_acknowledgment_age_seconds"] = 301; cases.append((CardiacProtocol, bad))
    bad = deepcopy(lab); bad["text"] = "€" * 8192; bad["sha256"] = hashlib.sha256(bad["text"].encode()).hexdigest(); cases.append((LaboratoryProtocol, bad))
    for model, body in cases:
        with pytest.raises(ValidationError):
            model.model_validate(body)


def test_positive_collection_without_ble_is_owned_immutable_and_pending(collection_scope, client, capture_signer):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    assert run["grant"]["binding_id"] is None and run["grant"]["device_id"] is None
    assert run["grant"]["instruction_receipt"] == run["receipt"]
    assert run["start"]["server_start"]["grant"]["instruction_receipt_id"] == run["receipt"]["instruction_receipt_id"]
    signed = run["start"]["server_start"]
    capture_signer.public_key().verify(base64.b64decode(signed["signature"]),
        DOMAIN.encode() + canonical(signed["grant"]), ec.ECDSA(hashes.SHA256()))
    body, h = collection_body(run), headers()
    path = f"/v1/sessions/{run['session_id']}/collections"
    accepted = client.post(path, headers=h, json=body)
    assert accepted.status_code == 201, accepted.text
    receipt = accepted.json()
    assert receipt["request"] == body and receipt["state"] == "pending_lab"
    assert receipt["projection"]["saliva"] == []
    assert receipt["projection"]["sample"]["collected_at"] == body["collected_at"]
    assert receipt["configuration_submitted_sha256"] == digest(run["config"])
    retry = client.post(path, headers=h, json=body)
    assert retry.status_code == 201 and retry.json() == receipt
    conflict = client.post(path, headers=h, json={**body, "saliva_volume_ml": 1.5})
    assert conflict.status_code == 409 and conflict.json()["code"] == "IDEMPOTENCY_CONFLICT"
    replacement = client.post(path, headers=headers(), json={**body, "saliva_volume_ml": 1.5})
    assert replacement.status_code == 409
    status = client.get(path + "/" + run["sample_id"], headers=headers())
    assert status.status_code == 200 and status.json()["imports"] == []
    assert status.json()["state"] == "pending_lab"
    with factory()() as db:
        owner = db.get(Account, run["account"])
        stored = record(db, owner, "collection", run["sample_id"])
        assert stored.parent_id == run["session_id"] and stored.sha256 == digest(stored.body)
        assert record(db, owner, "attempt", run["attempt_id"]).body == receipt["attempt"]
        with pytest.raises(Problem) as denied:
            require_completed_collections(db, owner, db.get(Check, run["session_id"]))
        assert denied.value.code == "LAB_ANALYSIS_PENDING"


@pytest.mark.parametrize("change,expected", [
    ({"participant_protocol_sha256": "9" * 64}, "PARTICIPANT_PROTOCOL_CHANGED"),
    ({"configuration_submitted_sha256": "9" * 64}, "PARTICIPANT_PROTOCOL_CHANGED"),
    ({"configuration_version": "v2"}, "PARTICIPANT_PROTOCOL_CHANGED"),
    ({"confirmations": []}, "VALIDATION_FAILED"),
    ({"confirmations": ["method_reviewed", "method_reviewed"]}, "REQUIRED_INSTRUCTION_CONFIRMATIONS"),
    ({"collection_method_version": "v2"}, "COLLECTION_METHOD_NOT_APPROVED"),
    ({"setup_id": "FICTIONAL-BENCH"}, "PREPARATION_SCOPE_MISMATCH"),
    ({"confirmed": 1}, "VALIDATION_FAILED"),
])
def test_acknowledgment_cannot_substitute_scope_or_synthetic_confirmation(collection_scope, client, change, expected):
    run = start_collection(client, collection_scope)
    response = client.post(f"/v1/sessions/{run['session_id']}/instruction-acknowledgments",
        headers=headers(), json={**run["ack"], **change})
    assert response.status_code in (403, 422), response.text
    assert response.json()["code"] == expected
    with factory()() as db:
        assert db.scalar(select(Record.id).where(Record.kind == "instruction_receipt")) is None


@pytest.mark.parametrize("change,expected", [
    ({"sample_id": "22222222-2222-4222-8222-222222222222"}, "STARTED_COLLECTION_ATTEMPT_REQUIRED"),
    ({"collection_method_version": "v2"}, "COLLECTION_METHOD_MISMATCH"),
    ({"saliva_volume_ml": 0.1}, "COLLECTION_QUANTITY_OUTSIDE_APPROVAL"),
    ({"dilution_factor": 999.0}, "COLLECTION_DILUTION_INCONSISTENT"),
    ({"saliva_volume_ml": None, "missing_reasons": {"cartridge_lot": "not_applicable", "saliva_volume_ml": "unknown"}}, "REQUIRED_COLLECTION_VALUE_UNKNOWN"),
    ({"container_id": "UNAPPROVED-CONTAINER"}, "COLLECTION_SUPPLIES_INVALID"),
    ({"storage_handling_events": []}, "COLLECTION_HANDLING_REQUIRED"),
    ({"missing_reasons": {"cartridge_lot": "invented"}}, "VALIDATION_FAILED"),
    ({"missing_reasons": {"cartridge_lot": "declined"}}, "COLLECTION_REASON_NOT_APPROVED"),
    ({"THC_ng_ml": 8.0}, "VALIDATION_FAILED"),
    ({"laboratory_id": "SELF-DECLARED"}, "VALIDATION_FAILED"),
    ({"saliva_volume_ml": -1.0}, "VALIDATION_FAILED"),
])
def test_collection_rejects_forged_analytical_authority_and_invalid_metadata(collection_scope, client, change, expected):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    response = client.post(f"/v1/sessions/{run['session_id']}/collections", headers=headers(),
        json=collection_body(run, **change))
    assert response.status_code in (409, 422), response.text
    assert response.json()["code"] == expected
    with factory()() as db:
        owner = db.get(Account, run["account"])
        assert record(db, owner, "collection", run["sample_id"]) is None
        assert record(db, owner, "attempt", run["attempt_id"]).body["status"] == "started"


def test_instruction_receipt_expiry_uses_declared_time_and_replay_does_not_restore_authority(collection_scope, client, monkeypatch):
    run = start_collection(client, collection_scope)
    h = headers()
    path = f"/v1/sessions/{run['session_id']}/instruction-acknowledgments"
    accepted = client.post(path, headers=h, json=run["ack"])
    assert accepted.status_code == 201, accepted.text
    tick = now() + 121
    monkeypatch.setattr("otgd.participant_acquisition.now", lambda: tick)
    # Same-key response stays historical; it confers no start permission.
    replay = client.post(path, headers=h, json=run["ack"])
    assert replay.status_code == 201 and replay.json() == accepted.json()
    denied = client.post(f"/v1/sessions/{run['session_id']}/capture-authorizations", headers=headers(), json={
        "attempt_id": run["attempt_id"], "channel": "saliva", "binding_id": None, "device_id": None,
        "configuration_id": CONFIGURATION, "configuration_hash": run["config"]["sha256"],
        "instruction_receipt_id": accepted.json()["instruction_receipt_id"], "raw_recording_kind": None})
    assert denied.status_code == 403 and denied.json()["code"] == "INSTRUCTION_ACKNOWLEDGMENT_EXPIRED"


def test_config_retirement_and_withdrawal_after_acknowledgment_refuse_fresh_start(collection_scope, client):
    run = start_collection(client, collection_scope)
    accepted = client.post(f"/v1/sessions/{run['session_id']}/instruction-acknowledgments",
        headers=headers(), json=run["ack"])
    assert accepted.status_code == 201, accepted.text
    withdrawn = client.post(f"/v1/studies/{STUDY}/withdrawals", headers=headers(), json={"confirmation": True})
    assert withdrawn.status_code == 200, withdrawn.text
    request = {"attempt_id": run["attempt_id"], "channel": "saliva", "binding_id": None,
        "device_id": None, "configuration_id": CONFIGURATION,
        "configuration_hash": run["config"]["sha256"], "instruction_receipt_id": accepted.json()["instruction_receipt_id"]}
    denied = client.post(f"/v1/sessions/{run['session_id']}/capture-authorizations", headers=headers(), json=request)
    assert denied.status_code == 403, denied.text
    with factory().begin() as db:
        transition(db, "configuration", CONFIGURATION, "v1", "retire", "local:fixture-releaser", "Fictional authority withdrawn", 3)
    denied = client.post(f"/v1/sessions/{run['session_id']}/instruction-acknowledgments", headers=headers(), json=run["ack"])
    assert denied.status_code == 403, denied.text


def test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample(collection_scope, client):
    first = acknowledge_and_start(client, start_collection(client, collection_scope))
    body = collection_body(first, status="invalid", quality_flags=["INSUFFICIENT_SPECIMEN"],
        saliva_volume_ml=None, missing_reasons={"cartridge_lot": "not_applicable", "saliva_volume_ml": "unknown"})
    response = client.post(f"/v1/sessions/{first['session_id']}/collections", headers=headers(), json=body)
    assert response.status_code == 201, response.text
    assert response.json()["state"] == "invalid_collection"
    second = acknowledge_and_start(client, start_collection(client, collection_scope, first["attempt_id"]))
    assert second["sample_id"] != first["sample_id"] and second["receipt"] != first["receipt"]
    accepted = client.post(f"/v1/sessions/{second['session_id']}/collections", headers=headers(), json=collection_body(second))
    assert accepted.status_code == 201, accepted.text
    with factory()() as db:
        owner = db.get(Account, first["account"])
        original = record(db, owner, "collection", first["sample_id"])
        replacement = record(db, owner, "collection", second["sample_id"])
        assert original.body == response.json()
        assert replacement.body["attempt"]["supersedes_attempt_id"] == first["attempt_id"]
        assert original.body["projection"]["sample"]["volume_ml"] is None


def test_foreign_account_and_retired_generation_cannot_record_or_read_collection(collection_scope, client):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    other = client.get("/v1/me/capabilities", headers=headers(sub="other")).json()["account_ref"]
    assert other != run["account"]
    assert client.post("/v1/me/acknowledgments", headers=headers(sub="other"), json={
        "version": "v1", "sha256": NOTICE_SHA, "acknowledged_at": iso()}).status_code == 200
    path = f"/v1/sessions/{run['session_id']}/collections"
    denied = client.post(path, headers=headers(sub="other"), json=collection_body(run))
    assert denied.status_code == 404, denied.text
    denied = client.post(path, headers=headers(gen=2), json=collection_body(run))
    assert denied.status_code == 410 and denied.json()["code"] == "DATA_GENERATION_RETIRED"
    assert client.get(path + "/" + run["sample_id"], headers=headers(sub="other")).status_code == 404


def test_human_ecg_state_verification_is_unavailable_even_when_declared_verified():
    from .governance_fixture import adc_material
    for verifier in ("participant_declaration_only", "device_attested_v1"):
        protocol = {**cardiac_protocol(), "operating_scope": "human_participant", "operating_state_verifier": verifier}
        config = {"channel": "ecg", "software_adapter_id": "otgd_signed_reader_v1",
            "participant_protocol": protocol, "material": {**adc_material("ecg"), "raw_unit": "mV"}}
        assert not software_supported(config)


@pytest.mark.parametrize("collection_scope,factor,buffer", [
    ({"method_changes": {"dilution_definition": "undiluted", "fixed_dilution_factor": None}}, 1.0, 0.0),
    ({"method_changes": {"dilution_definition": "fixed_factor", "fixed_dilution_factor": 3.0}}, 3.0, 1.0),
], indirect=["collection_scope"])
def test_each_supported_dilution_convention_preserves_its_approved_meaning(collection_scope, client, factor, buffer):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    body = collection_body(run, dilution_factor=factor, buffer_volume_ml=buffer)
    accepted = client.post(f"/v1/sessions/{run['session_id']}/collections", headers=headers(), json=body)
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["request"]["dilution_factor"] == factor
    assert accepted.json()["request"]["buffer_volume_ml"] == buffer


@pytest.mark.parametrize("collection_scope", [{"method_changes": {
    "dilution_definition": "undiluted", "fixed_dilution_factor": None,
}}], indirect=True)
def test_undiluted_method_rejects_known_nonzero_buffer_even_when_factor_is_one(collection_scope, client):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    response = client.post(f"/v1/sessions/{run['session_id']}/collections", headers=headers(),
        json=collection_body(run, dilution_factor=1.0, buffer_volume_ml=1.0))
    assert response.status_code == 422 and response.json()["code"] == "COLLECTION_DILUTION_INCONSISTENT"
    with factory()() as db:
        assert not list(db.scalars(select(Record).where(Record.kind == "collection")))


@pytest.mark.parametrize("corruption", ["missing", "parent", "revision", "body"])
def test_status_requires_preserved_original_attempt_not_only_a_valid_collection_digest(collection_scope, client, corruption):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    response = client.post(f"/v1/sessions/{run['session_id']}/collections", headers=headers(), json=collection_body(run))
    assert response.status_code == 201, response.text
    # An independent inconsistent stored-record probe. No authority is faked,
    # no PostgreSQL immutable trigger is disabled, and no write route is added.
    with factory().begin() as db:
        original = record(db, db.get(Account, run["account"]), "attempt", run["attempt_id"])
        if corruption == "missing":
            db.delete(original)
        elif corruption == "parent":
            original.parent_id = str(uuid4())
        elif corruption == "revision":
            original.revision += 1
        else:
            original.body = {**original.body, "record_id": str(uuid4())}
            original.sha256 = digest(original.body)
    denied = client.get(f"/v1/sessions/{run['session_id']}/collections/{run['sample_id']}", headers=headers())
    assert denied.status_code == 503 and denied.json()["code"] == "COLLECTION_INTEGRITY_FAILED"


@pytest.mark.parametrize("scenario,expected", [
    ("expired_supply", "COLLECTION_SUPPLIES_INVALID"),
    ("future_collection", "COLLECTION_TIME_INVALID"),
    ("before_start", "CAPTURE_TIME_OUTSIDE_AUTHORIZATION"),
    ("handling_before_collection", "COLLECTION_HANDLING_INVALID"),
    ("handling_after_now", "COLLECTION_HANDLING_INVALID"),
    ("duplicate_handling", "COLLECTION_HANDLING_INVALID"),
    ("unapproved_handling", "COLLECTION_HANDLING_NOT_APPROVED"),
])
def test_collection_chronology_and_handling_are_actual_events_not_form_progress(collection_scope, client, scenario, expected):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    body = collection_body(run)
    if scenario == "expired_supply":
        body["cartridge_expiry"] = iso(now() - 1)
    elif scenario == "future_collection":
        body["collected_at"] = iso(now() + 30)
    elif scenario == "before_start":
        body["collected_at"] = iso(now() - 10)
        body["storage_handling_events"][0]["occurred_at"] = body["collected_at"]
    elif scenario == "handling_before_collection":
        body["storage_handling_events"][0]["occurred_at"] = iso(now() - 10)
    elif scenario == "handling_after_now":
        body["storage_handling_events"][0]["occurred_at"] = iso(now() + 30)
    elif scenario == "duplicate_handling":
        body["storage_handling_events"] *= 2
    elif scenario == "unapproved_handling":
        body["storage_handling_events"][0]["event"] = "UNAPPROVED-EVENT"
    response = client.post(f"/v1/sessions/{run['session_id']}/collections", headers=headers(), json=body)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == expected


def test_same_material_digest_cannot_approve_changed_participant_instructions(collection_scope):
    old = collection_scope["config"]
    new = deepcopy(old)
    new["version"] = "v2"
    new["participant_protocol"]["text"] += " NEW unqualified collection steps."
    new["participant_protocol"]["sha256"] = hashlib.sha256(new["participant_protocol"]["text"].encode()).hexdigest()
    assert new["sha256"] == old["sha256"] and digest(new) != digest(old)
    with factory().begin() as db:
        submitted = submit(db, "configuration", new, "local:fixture-submitter")
        transition(db, "configuration", CONFIGURATION, "v2", "approve", "local:fixture-reviewer",
            "Fictional review; old proof does not cover new instructions", submitted["revision"])
        db.flush()
        with pytest.raises(Problem) as denied:
            transition(db, "configuration", CONFIGURATION, "v2", "release", "local:fixture-releaser",
                "Cannot inherit old qualification", 2)
        assert denied.value.code == "QUALIFICATION_CONFIGURATION_MISMATCH"
        assert active_body(db, "configuration", CONFIGURATION) == old


def test_acknowledgment_time_cannot_be_rebased_onto_new_server_acceptance(collection_scope, client):
    run = start_collection(client, collection_scope)
    for tick in (now() - 121, now() + 10):
        denied = client.post(f"/v1/sessions/{run['session_id']}/instruction-acknowledgments",
            headers=headers(), json={**run["ack"], "acknowledged_at": iso(tick)})
        assert denied.status_code == 422 and denied.json()["code"] == "ACKNOWLEDGMENT_TIME_INVALID"


def test_foreign_attempt_receipt_and_missing_receipt_do_not_create_collection_start(collection_scope, client):
    first, second = (start_collection(client, collection_scope) for _ in range(2))
    accepted = client.post(f"/v1/sessions/{first['session_id']}/instruction-acknowledgments",
        headers=headers(), json=first["ack"])
    assert accepted.status_code == 201, accepted.text
    for receipt_id in (None, str(uuid4()), accepted.json()["instruction_receipt_id"]):
        denied = client.post(f"/v1/sessions/{second['session_id']}/capture-authorizations",
            headers=headers(), json={"attempt_id": second["attempt_id"], "channel": "saliva",
                "configuration_id": CONFIGURATION, "configuration_hash": second["config"]["sha256"],
                "binding_id": None, "device_id": None, "instruction_receipt_id": receipt_id})
        assert denied.status_code == 403 and denied.json()["code"] == "CURRENT_INSTRUCTION_ACKNOWLEDGMENT_REQUIRED"


def test_tampered_collection_cannot_appear_as_analytical_evidence_or_finish(collection_scope, client):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    path = f"/v1/sessions/{run['session_id']}/collections"
    accepted = client.post(path, headers=headers(), json=collection_body(run))
    assert accepted.status_code == 201, accepted.text
    with factory().begin() as db:
        row = record(db, db.get(Account, run["account"]), "collection", run["sample_id"])
        row.body = {**row.body, "state": "analysis_available"}
        assert row.sha256 != digest(row.body)
    denied = client.get(path + "/" + run["sample_id"], headers=headers())
    assert denied.status_code == 503 and denied.json()["code"] == "COLLECTION_INTEGRITY_FAILED"
    with factory()() as db:
        with pytest.raises(Problem) as failed:
            require_completed_collections(db, db.get(Account, run["account"]), db.get(Check, run["session_id"]))
        assert failed.value.code == "COLLECTION_INTEGRITY_FAILED"


def test_pending_sample_blocks_finalization_until_explicit_cancellation_without_erasing_history(collection_scope, client):
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    path = f"/v1/sessions/{run['session_id']}"
    collected = client.post(path + "/collections", headers=headers(), json=collection_body(run))
    assert collected.status_code == 201, collected.text
    pending = client.post(path + "/finalize", headers=headers(revision=1), json={
        "snapshot_sha256": "a" * 64, "evidence_sha256": "b" * 64})
    assert pending.status_code == 409 and pending.json()["code"] == "LAB_ANALYSIS_PENDING"
    original = collected.json()
    h = headers()
    request = {"confirmation": True, "reason": "PARTICIPANT_DECLINED"}
    canceled = client.post(path + f"/collections/{run['sample_id']}/abandon", headers=h, json=request)
    assert canceled.status_code == 201, canceled.text
    replay = client.post(path + f"/collections/{run['sample_id']}/abandon", headers=h, json=request)
    assert replay.status_code == 201 and replay.json() == canceled.json()
    status = client.get(path + f"/collections/{run['sample_id']}", headers=headers())
    assert status.status_code == 200 and status.json()["state"] == "analysis_canceled"
    assert status.json()["request"] == original["request"]
    assert status.json()["attempt"] == original["attempt"]
    assert status.json()["projection"] == original["projection"]
    assert status.json()["projection"]["sample"]["status"] == "valid"
    assert status.json()["projection"]["saliva"] == []
    write_review_fixture("abandon_flow", {"configuration": run["config"], "context": run["context"],
        "ack_request": run["ack"], "instruction_receipt": run["receipt"], "authorization": run["grant"],
        "start": run["start"], "collection_request": original["request"], "collection_receipt": original,
        "abandon_request": request, "abandon_receipt": canceled.json(), "abandon_status": status.json()})
    with factory()() as db:
        owner = db.get(Account, run["account"])
        assert record(db, owner, "collection", run["sample_id"]).body == original
        require_completed_collections(db, owner, db.get(Check, run["session_id"]))


@pytest.mark.parametrize("collection_scope", [{"staff": True}], indirect=True)
def test_actual_http_collection_staff_report_import_refresh_and_finalize(collection_scope, client, monkeypatch):
    """Full HTTP custody and finalization; the PDF object store is a named double."""
    import io

    from otgd import storage
    from otgd.worker import run_job

    class ExplicitPDFStorageDouble:
        def __init__(self):
            self.objects = {}
            self.signed = []

        def generate_presigned_url(self, operation, **kwargs):
            self.signed.append((operation, kwargs))
            return "https://fictional-storage.invalid/explicit-unit-test-only"

        def head_object(self, **kwargs):
            value = self.objects[(kwargs["Bucket"], kwargs["Key"])]
            return {"VersionId": value["version"]}

        def get_object(self, **kwargs):
            value = self.objects[(kwargs["Bucket"], kwargs["Key"])]
            assert kwargs["VersionId"] == value["version"]
            return {"VersionId": value["version"], "ContentLength": len(value["bytes"]),
                "ContentType": "application/pdf", "Body": io.BytesIO(value["bytes"])}

    store = ExplicitPDFStorageDouble()
    monkeypatch.setattr(storage, "client", lambda *_args, **_kwargs: store)
    run = acknowledge_and_start(client, start_collection(client, collection_scope))
    collected = client.post(f"/v1/sessions/{run['session_id']}/collections", headers=headers(), json=collection_body(run))
    assert collected.status_code == 201, collected.text
    pending_status = client.get(f"/v1/sessions/{run['session_id']}/collections/{run['sample_id']}", headers=headers())
    assert pending_status.status_code == 200 and pending_status.json()["state"] == "pending_lab"
    pdf = b"%PDF-1.7\nFICTIONAL INDEPENDENT SOFTWARE TEST REPORT; NO ASSAY APPROVAL\n"
    request = {"account_ref": run["account"], "data_generation": 1, "study_id": STUDY,
        "session_id": run["session_id"], "sample_id": run["sample_id"],
        "collection_attempt_id": run["attempt_id"], "sha256": hashlib.sha256(pdf).hexdigest(),
        "size_bytes": len(pdf), "media_type": "application/pdf"}
    h = headers(sub="staff")
    ticket = client.post("/v1/research/lab-source-artifact-uploads", headers=h, json=request)
    assert ticket.status_code == 201, ticket.text
    artifact_id = ticket.json()["artifact_id"]
    with factory()() as db:
        row = db.get(Artifact, artifact_id)
        assert row.account_id == run["account"] and row.generation == 1
        store.objects[(row.bucket, row.key)] = {"version": "fictional-pdf-version-1", "bytes": pdf}
        cached = list(db.scalars(select(Dedup).where(Dedup.account_id == run["operator"])))
        assert all("upload_url" not in str(value.body) and "FICTIONAL INDEPENDENT" not in str(value.body) for value in cached)
    completion = client.post(f"/v1/research/lab-source-artifact-uploads/{artifact_id}/complete",
        headers=headers(sub="staff"), json={key: request[key] for key in ("sha256", "size_bytes", "media_type")})
    assert completion.status_code == 200, completion.text
    measurement = deepcopy(run["frozen"]["saliva"][0])
    measurement.update(measurement_id=str(uuid4()), sample_id=run["sample_id"],
        collected_at=collected.json()["request"]["collected_at"], measured_at=iso(), source="reference_lab",
        method_id=ASSAY_METHOD, calibration_id=CALIBRATION, instrument_id=INSTRUMENT,
        operator_ref=run["operator"], concentration_basis="collected_mixture")
    imported_body = {key: request[key] for key in ("account_ref", "data_generation", "study_id", "session_id", "sample_id", "collection_attempt_id")}
    imported_body.update(source_report_artifact_id=artifact_id, measurements=[measurement])
    importer_headers = headers(sub="staff")
    imported = client.post("/v1/research/lab-imports", headers=importer_headers, json=imported_body)
    assert imported.status_code == 201, imported.text
    assert set(imported.json()) == {"import_id", "analysis_attempt_id", "state"}
    refreshed = client.get(f"/v1/sessions/{run['session_id']}/collections/{run['sample_id']}", headers=headers())
    assert refreshed.status_code == 200, refreshed.text
    value = refreshed.json()
    assert value["state"] == "analysis_available" and value["imports"][0]["measurements"] == [measurement]
    assert value["projection"]["sample"]["collected_at"] == measurement["collected_at"]
    assert value["attempt"]["attempt_id"] == imported.json()["analysis_attempt_id"]
    assert value["attempt"]["supersedes_attempt_id"] == run["attempt_id"]
    evidence = client.get(f"/v1/sessions/{run['session_id']}/evidence", headers=headers())
    assert evidence.status_code == 200, evidence.text
    assert evidence.json()["collections"] == [collected.json()]
    assert evidence.json()["instruction_receipts"] == [run["receipt"]]
    snapshot = deepcopy(run["frozen"])
    snapshot["device"] = {key: "unavailable" for key in snapshot["device"]}
    snapshot["sample"], snapshot["saliva"] = value["projection"]["sample"], [measurement]
    for component in ("eyes", "cardiac", "task"):
        snapshot[component].update(status="not_collected", source="prototype_sensor", started_at=None, ended_at=None)
    snapshot["eyes"].update(frame_rate_hz=None, baseline_diameter_mm=None, relative_constriction=None, latency_ms=None)
    snapshot["cardiac"].update(modality="ppg", heart_rate_bpm=None)
    snapshot["task"].update(practice_trials=0, scored_trials=0, go_trials=0, no_go_trials=0, valid_correct_go_trials=0,
        features={key: None for key in snapshot["task"]["features"]})
    snapshot.update(acquisition_span_ms=0.0, capture_completed_at=iso())
    saved = client.put(f"/v1/sessions/{run['session_id']}/snapshot", headers=headers(revision=1), json=snapshot)
    assert saved.status_code == 200, saved.text
    attempts = evidence.json()["attempts"]
    manifest = {"schema_version": "1.0.0", "session_id": run["session_id"],
        "context_sha256": digest(run["context"]),
        "attempts": [{"attempt_id": item["attempt_id"], "sha256": digest(item)} for item in attempts],
        "selected": {"saliva": value["attempt"]["attempt_id"], "eyes": None, "cardiac": None, "task": None, "alcohol": None}}
    published = client.put(f"/v1/sessions/{run['session_id']}/evidence-manifest", headers=headers(revision=0), json=manifest)
    assert published.status_code == 200, published.text
    final = client.post(f"/v1/sessions/{run['session_id']}/finalize", headers=headers(revision=2), json={
        "snapshot_sha256": digest(snapshot), "evidence_sha256": digest(manifest)})
    assert final.status_code == 202, final.text
    pending_result = client.get(f"/v1/sessions/{run['session_id']}/result", headers=headers())
    assert pending_result.status_code == 202
    assert pending_result.json() == {"session_id": run["session_id"], "state": "processing"}
    write_review_fixture("import_flow", {"configuration": run["config"], "context": run["context"],
        "capabilities": client.get("/v1/me/capabilities", headers=headers()).json(),
        "ack_request": run["ack"], "instruction_receipt": run["receipt"], "authorization": run["grant"],
        "start": run["start"], "collection_request": collected.json()["request"],
        "collection_receipt": collected.json(), "pending_status": pending_status.json(),
        "import_request": imported_body, "import_receipt": imported.json(), "import_status": value,
        "evidence": evidence.json(), "frozen_snapshot": snapshot, "manifest": manifest})
    assert run_job(final.json()["job_id"]) == "completed"
    result = client.get(f"/v1/sessions/{run['session_id']}/result", headers=headers())
    assert result.status_code == 200 and result.json()["probability"] is None
    assert result.json()["state"] == "inconclusive"
    # This fictional study deliberately has no released model_id.  Its actual
    # research authority therefore permits custody, not a numerical estimate.
    assert result.json()["reason_codes"] == ["STUDY_UNAUTHORIZED"]
