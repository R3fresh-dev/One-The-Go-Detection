"""Delegated laboratory software only; every approval/cohort/report is fictional.

The fixture executes genuine typed three-principal registry transitions, then
seeds an internally coherent accepted collection prerequisite. Object storage is
an explicit bounded double. This is not assay qualification or a live S3 claim.
"""

from copy import deepcopy
import hashlib
import io
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from otgd import lab_handoff as lab
from otgd.canonical import digest
from otgd.db import Account, Artifact, Audit, Check, Dedup, Record, factory, iso, now, uid
from otgd.domain import NOTICE_SHA, record, save_record
from otgd.dto import CaptureAttempt, LabImport
from otgd.errors import Problem
from otgd.operator_governance import Configuration, RegistryVersion
from otgd.participant_acquisition import CollectionReceipt, CollectionRequest

from .conftest import headers
from .governance_fixture import approve, calibration, common, device, retention, study
from .helpers import session_fixture

METHOD = "FICTIONAL-DELEGATED-LAB-METHOD"
CONFIG = "fictional-reference-lab-configuration"
INSTRUMENT = "FICTIONAL-LAB-INSTRUMENT"
COLLECTOR = "fictional-collector"


@pytest.fixture
def handoff(client, account):
    operator_id = client.get("/v1/me/capabilities", headers=headers("b")).json()["account_ref"]
    assert client.post("/v1/me/acknowledgments", headers=headers("b"), json={
        "version": "v1", "sha256": NOTICE_SHA, "acknowledged_at": iso(),
    }).status_code == 200
    timestamp = iso(now() - 15)
    sample_id, session_id, attempt_id, instruction_id = uid(), uid(), uid(), uid()
    collection_id = uid()
    document = "FICTIONAL collection instructions, not an approved participant method."
    protocol = {"schema_version": "1.0.0", "kind": "reference_lab", "instruction_id": "fictional-instructions",
        "version": "v1", "text": document, "sha256": hashlib.sha256(document.encode()).hexdigest(),
        "required_confirmations": [{"id": "collection_confirmed", "text": "Fictional instruction review"}],
        "maximum_acknowledgment_age_seconds": 300,
        "maximum_collection_submission_delay_seconds": 300, "maximum_analysis_delay_seconds": 3600,
        "methods": [{"id": COLLECTOR, "version": "v1", "instructions": "Fictional collection fixture only",
            "saliva_volume_required": True, "buffer_volume_required": False, "dilution_factor_required": False,
            "dilution_definition": None, "fixed_dilution_factor": None,
            "saliva_volume_min_ml": 0.1, "saliva_volume_max_ml": 10.0,
            "buffer_volume_min_ml": None, "buffer_volume_max_ml": None, "collector_lot_required": True,
            "container_required": False, "expiry_required": False, "permitted_containers": [],
            "required_handling_events": [], "permitted_null_reasons": ["unknown", "not_applicable"]}]}
    material = {"schema_version": "1.0.0", "channel": "saliva", "source": "reference_lab",
        "collection_method_ids": [COLLECTOR], "assay_bases": ["free"],
        "concentration_bases": ["neat_oral_fluid"], "correction_statuses": ["not_corrected"]}
    config = common(CONFIG, configuration_id=CONFIG, study_id=study(account)["study_id"],
        protocol_id=study(account)["protocol_id"], channel="saliva", sha256=digest(material), material=material,
        qualification_evidence_ref="fictional-lab-qualification", retention_policy_id=retention()["policy_id"],
        max_duration_ms=150000, software_adapter_id="reference_lab_import_v1", raw_retention_approved=True,
        lab_methods={METHOD: {"calibration_ids": [calibration()["calibration_id"]], "instrument_ids": [INSTRUMENT]}},
        participant_protocol=protocol)
    config = Configuration.model_validate(config).data()
    proof = common("fictional-lab-qualification", channel="saliva", configuration_sha256=config["sha256"],
        document_sha256="2" * 64, reviewed_by="FICTIONAL independent scientist", approval_status="approved",
        purpose="measurement_collection", configuration_registry_id=CONFIG, configuration_version="v1",
        configuration_submitted_sha256=digest(config))
    study_body = study(account, {"saliva": CONFIG})
    study_body["account_refs"].append(operator_id)
    consent_id = uid()
    consent = {"state": "active", "consent_record_id": consent_id,
        **{key: study_body[key] for key in ("document_sha256", "document_version", "invitation_id")}}
    instruction = {"instruction_receipt_id": instruction_id, "session_id": session_id,
        "attempt_id": attempt_id, "configuration_id": CONFIG, "configuration_version": "v1",
        "configuration_hash": config["sha256"], "configuration_submitted_sha256": digest(config),
        "participant_protocol_sha256": digest(config["participant_protocol"]), "acknowledged_at": timestamp,
        "accepted_at": timestamp, "consent_record_id": consent_id, "confirmed": True,
        "confirmations": ["collection_confirmed"], "setup_id": None, "rest_started_at": None,
        "collection_method_id": COLLECTOR, "collection_method_version": "v1"}
    sample = {"sample_id": sample_id, "collection_method_id": COLLECTOR, "collected_at": timestamp,
        "volume_ml": 1.0, "dilution_factor": None, "status": "valid", "quality_flags": []}
    attempt = {"schema_version": "1.0.0", "session_id": session_id, "attempt_id": attempt_id,
        "component": "saliva", "record_id": sample_id, "supersedes_attempt_id": None,
        "status": "valid", "source": "reference_lab", "started_at": timestamp, "ended_at": timestamp,
        "configuration_id": CONFIG, "configuration_hash": config["sha256"], "quality_flags": [],
        "component_metadata": {"projection": {"sample": sample, "saliva": []}, "instruction_receipt": instruction,
            "collection_receipt_id": collection_id},
        "artifact_refs": [], "attestation_refs": []}
    CaptureAttempt.model_validate(attempt)
    collection_request = CollectionRequest.model_validate({"sample_id": sample_id, "attempt_id": attempt_id,
        "instruction_receipt_id": instruction_id, "collection_method_id": COLLECTOR,
        "collection_method_version": "v1", "collected_at": timestamp, "status": "valid", "quality_flags": [],
        "saliva_volume_ml": 1.0, "buffer_volume_ml": None, "dilution_factor": None,
        "collector_id": "fictional-collector-person", "collector_lot": "fictional-kit-lot",
        "container_id": None, "cartridge_lot": None, "cartridge_expiry": None,
        "missing_reasons": {key: "not_applicable" for key in ("buffer_volume_ml", "dilution_factor",
            "container_id", "cartridge_lot", "cartridge_expiry")}, "storage_handling_events": []}).data()
    attempt["component_metadata"]["collection_request_sha256"] = digest(collection_request)
    collection = {"collection_receipt_id": collection_id, "session_id": session_id,
        "request": collection_request, "state": "pending_lab", "accepted_at": timestamp,
        "authorization_id": uid(),
        "configuration_submitted_sha256": digest(config), "configuration_version": "v1",
        "participant_protocol_sha256": digest(config["participant_protocol"]), "instruction_receipt": instruction,
        "projection": {"sample": sample, "saliva": []}, "attempt": attempt,
        "attempt_revision": 1, "attempt_sha256": digest(attempt)}
    assert CollectionReceipt.model_validate(collection).data() == collection
    with factory().begin() as db:
        participant = db.get(Account, account)
        for kind, body in (("study", study_body), ("device", device(account)), ("calibration", calibration()),
            ("method", common(METHOD, method_id=METHOD, assay_bases=["free"], collection_method_ids=[COLLECTOR],
                instrument_ids=[INSTRUMENT], laboratory_ids=["FICTIONAL-LAB"])),
            ("retention", retention(purpose_id=lab.PURPOSE, access_roles=["lab_importer"])),
            ("qualification", proof), ("configuration", config),
            ("role", common(operator_id, account_ref=operator_id, roles=["lab_import"], study_ids=[study_body["study_id"]]))):
            approve(db, kind, body)
        db.add(Check(id=session_id, account_id=account, generation=1, state="draft", mode="analytical",
            study_id=study_body["study_id"], protocol_id=study_body["protocol_id"], created=now() - 30))
        save_record(db, participant, "consent", study_body["study_id"], consent)
        save_record(db, participant, "context", session_id, {"configuration_refs": [{"id": CONFIG,
            "version": "v1", "sha256": config["sha256"]}], "protocol_id": study_body["protocol_id"]}, session_id)
        save_record(db, participant, "instruction_receipt", instruction_id, instruction, session_id)
        save_record(db, participant, "attempt", attempt_id, attempt, session_id)
        save_record(db, participant, "collection", sample_id, collection, session_id)
    pdf = b"%PDF-1.7\nFICTIONAL SOFTWARE LABORATORY REPORT\n"
    request = lab.LabSourceRequest(account_ref=account, data_generation=1, study_id=study_body["study_id"],
        session_id=session_id, sample_id=sample_id, collection_attempt_id=attempt_id,
        sha256=hashlib.sha256(pdf).hexdigest(), size_bytes=len(pdf), media_type="application/pdf")
    measurement = deepcopy(session_fixture(account)["saliva"][0])
    measurement.update(measurement_id=uid(), sample_id=sample_id, collected_at=timestamp, measured_at=iso(),
        source="reference_lab", method_id=METHOD, calibration_id=calibration()["calibration_id"],
        instrument_id=INSTRUMENT, operator_ref=operator_id, assay_basis="free",
        concentration_basis="neat_oral_fluid", correction_status="not_corrected")
    return SimpleNamespace(participant=account, operator=operator_id, request=request, collection=collection,
        config=config, study=study_body, measurement=measurement, pdf=pdf)


def create(fixture):
    with factory().begin() as db:
        artifact, receipt = lab.create_source(db, db.get(Account, fixture.operator), fixture.request)
        id = artifact.id
    return id, receipt


def settle(fixture):
    id, _ = create(fixture)
    with factory().begin() as db:
        row = db.get(Artifact, id)
        receipt = lab.accept_source(db, db.get(Account, fixture.operator), id, "fictional-pinned-v1",
            fingerprint=lab.source_fingerprint(row))
        assert receipt == {"artifact_id": id, "state": "verified"}
    return id


def import_body(fixture, source):
    return LabImport(**{key: fixture.request.data()[key] for key in (
        "account_ref", "data_generation", "study_id", "session_id", "sample_id", "collection_attempt_id")},
        source_report_artifact_id=source, measurements=[deepcopy(fixture.measurement)])


def test_distinct_operator_creates_subject_owned_source_and_import(handoff):
    source = settle(handoff)
    with factory().begin() as db:
        receipt = lab.import_measurements(db, db.get(Account, handoff.operator), import_body(handoff, source))
        assert set(receipt) == {"import_id", "analysis_attempt_id", "state"}
        participant = db.get(Account, handoff.participant)
        imported = record(db, participant, "lab_import", receipt["import_id"])
        analysis = record(db, participant, "attempt", receipt["analysis_attempt_id"])
        assert imported.account_id == analysis.account_id == handoff.participant
        assert imported.body["operator_account_ref"] == handoff.operator
        assert imported.body["source_report"]["version_id"] == "fictional-pinned-v1"
        assert analysis.body["supersedes_attempt_id"] == handoff.request.collection_attempt_id
        assert analysis.body["component_metadata"]["projection"]["saliva"] == [handoff.measurement]
        assert record(db, participant, "collection", handoff.request.sample_id).body == handoff.collection
        assert db.get(Check, handoff.request.session_id).snapshot is None
        audits = list(db.scalars(select(Audit).where(Audit.action.like("delegated_lab_import%"))))
        assert {row.account_id for row in audits} == {handoff.operator, handoff.participant}


@pytest.mark.parametrize("change", ["self", "target_deleted", "generation", "notice", "study", "role", "config", "consent", "abandon"])
def test_current_target_and_genuine_operator_authority_required(handoff, change):
    request = handoff.request.model_copy(deep=True)
    with factory().begin() as db:
        participant = db.get(Account, handoff.participant)
        if change == "self": request.account_ref = handoff.operator
        elif change == "target_deleted": participant.state = "deleted"
        elif change == "generation": participant.generation = 2
        elif change == "notice": participant.notice = None
        elif change == "study": request.study_id = "foreign-study"
        elif change == "role":
            for row in db.scalars(select(RegistryVersion).where(RegistryVersion.registry_key == "role:" + handoff.operator)):
                row.state = "revoked"
        elif change == "config":
            for row in db.scalars(select(RegistryVersion).where(RegistryVersion.registry_key == "configuration:" + CONFIG)):
                row.state = "retired"
        elif change == "consent":
            row = record(db, participant, "consent", handoff.request.study_id)
            row.body = {**row.body, "state": "withdrawn"}
        elif change == "abandon":
            save_record(db, participant, "collection_abandon", request.sample_id,
                {"sample_id": request.sample_id, "collection_sha256": digest(handoff.collection)}, request.session_id)
        db.flush()
        with pytest.raises(Problem):
            lab.create_source(db, db.get(Account, handoff.operator), request)
        assert db.scalar(select(Artifact.id)) is None


@pytest.mark.parametrize("field", ["sample_id", "collection_attempt_id", "session_id"])
def test_foreign_specimen_attempt_and_check_refused(handoff, field):
    request = handoff.request.model_copy(update={field: uid()})
    with factory().begin() as db:
        with pytest.raises(Problem):
            lab.create_source(db, db.get(Account, handoff.operator), request)


@pytest.mark.parametrize("change", ["missing_revision", "boolean_revision", "missing_authorization",
    "missing_original", "altered_original", "original_revision"])
def test_collection_requires_typed_receipt_and_preserved_original_attempt(handoff, change):
    with factory().begin() as db:
        owner = db.get(Account, handoff.participant)
        collection = record(db, owner, "collection", handoff.request.sample_id)
        original = record(db, owner, "attempt", handoff.request.collection_attempt_id)
        if change == "missing_original":
            db.delete(original)
        elif change == "altered_original":
            original.body = {**original.body, "quality_flags": ["ALTERED_AFTER_COLLECTION"]}
            original.sha256 = digest(original.body)
        elif change == "original_revision":
            original.revision += 1
        else:
            body = deepcopy(collection.body)
            if change == "missing_revision": body.pop("attempt_revision")
            elif change == "boolean_revision": body["attempt_revision"] = True
            else: body.pop("authorization_id")
            collection.body, collection.sha256 = body, digest(body)
        db.flush()
        with pytest.raises(Problem, match="COLLECTION_INTEGRITY_FAILED"):
            lab.create_source(db, db.get(Account, handoff.operator), handoff.request)
        assert db.scalar(select(Artifact.id)) is None


def test_ticket_minimal_receipt_and_remaining_original_deadline(handoff, monkeypatch):
    id, receipt = create(handoff)
    assert set(receipt) == {"artifact_id", "state", "expires_at"}
    calls = []
    s3 = SimpleNamespace(generate_presigned_url=lambda operation, **kwargs: calls.append((operation, kwargs)) or "https://fixture.invalid/upload")
    monkeypatch.setattr(lab.storage, "client", lambda *args, **kwargs: s3)
    with factory().begin() as db:
        target, _, row, _ = lab.source_target(db, db.get(Account, handoff.operator), id)
        assert target.id == handoff.participant
        row.expires = now() + 12.8
        ticket = lab.source_ticket(row)
        assert 11 <= ticket["expires_in_seconds"] <= 12
        assert calls[-1][1]["ExpiresIn"] == ticket["expires_in_seconds"]
        assert calls[-1][1]["Params"]["IfNoneMatch"] == "*"
        row.expires = now() - 1
        with pytest.raises(Problem, match="LAB_REPORT_UPLOAD_EXPIRED"):
            lab.source_ticket(row)


@pytest.mark.parametrize("change", ["version", "length", "media", "digest", "pdf", "oversize"])
def test_exact_version_pdf_read_rejects_storage_substitution(handoff, monkeypatch, change):
    data = handoff.pdf
    artifact = SimpleNamespace(size=len(data), sha256=hashlib.sha256(data).hexdigest(), state="quarantine",
        version_id=None, bucket="fictional-bucket", key="fictional-key")
    content_type, version, length = "application/pdf", "fictional-v1", len(data)
    if change == "version": version = "foreign-version"
    elif change == "length": length += 1
    elif change == "media": content_type = "application/octet-stream"
    elif change == "digest": artifact.sha256 = "f" * 64
    elif change == "pdf":
        data = b"unapproved bytes"; artifact.size = length = len(data); artifact.sha256 = hashlib.sha256(data).hexdigest()
    elif change == "oversize": artifact.size = lab.MAX_REPORT_BYTES + 1
    stream = io.BytesIO(data)
    s3 = SimpleNamespace(head_object=lambda **kwargs: {"VersionId": "fictional-v1"},
        get_object=lambda **kwargs: {"VersionId": version, "ContentLength": length, "ContentType": content_type, "Body": stream})
    monkeypatch.setattr(lab.storage, "client", lambda *args, **kwargs: s3)
    with pytest.raises(Problem): lab.verify_source(artifact)
    if change != "oversize": assert stream.closed


def test_bounded_exact_read_and_post_read_subject_revocation(handoff, monkeypatch):
    id, _ = create(handoff)
    with factory().begin() as db:
        _, _, detached, _ = lab.source_target(db, db.get(Account, handoff.operator), id)
        fingerprint = lab.source_fingerprint(detached)
    stream = io.BytesIO(handoff.pdf)
    s3 = SimpleNamespace(head_object=lambda **kwargs: {"VersionId": "fictional-v1"},
        get_object=lambda **kwargs: {"VersionId": "fictional-v1", "ContentLength": len(handoff.pdf), "ContentType": "application/pdf", "Body": stream})
    monkeypatch.setattr(lab.storage, "client", lambda *args, **kwargs: s3)
    assert lab.verify_source(detached) == "fictional-v1"
    assert stream.closed
    with factory().begin() as db:
        db.get(Account, handoff.participant).state = "deleting"
    with factory().begin() as db:
        with pytest.raises(Problem): lab.accept_source(db, db.get(Account, handoff.operator), id, "fictional-v1", fingerprint=fingerprint)
        assert db.get(Artifact, id).state == "quarantine"


@pytest.mark.parametrize("change", ["sample", "time", "future", "analysis_delay", "operator", "method", "source", "duplicate"])
def test_import_rejects_forged_or_incompatible_analytical_evidence(handoff, change):
    source = settle(handoff)
    body = import_body(handoff, source)
    value = body.measurements[0]
    if change == "sample": value["sample_id"] = uid()
    elif change == "time": value["collected_at"] = iso(now() - 20)
    elif change == "future": value["measured_at"] = iso(now() + 60)
    elif change == "analysis_delay":
        # A pure chronology check with a different fictional approved bound;
        # this does not mutate or bypass the production release registry.
        value["measured_at"] = iso(now() - 2)
        handoff.config["participant_protocol"]["maximum_analysis_delay_seconds"] = 1
        with factory().begin() as db:
            with pytest.raises(Problem): lab._measurements(db, db.get(Account, handoff.operator), handoff.config,
                handoff.collection["projection"]["sample"], body.measurements)
        return
    elif change == "operator": value["operator_ref"] = handoff.participant
    elif change == "method": value["method_id"] = "foreign-method"
    elif change == "source": value["source"] = "simulated"
    elif change == "duplicate": body.measurements.append(deepcopy(value))
    with factory().begin() as db:
        with pytest.raises((Problem, ValueError)): lab.import_measurements(db, db.get(Account, handoff.operator), body)
        assert db.scalar(select(Record.id).where(Record.kind == "lab_import")) is None


def test_duplicate_import_and_abandoned_handoff_never_reopen(handoff):
    source = settle(handoff)
    body = import_body(handoff, source)
    with factory().begin() as db:
        lab.import_measurements(db, db.get(Account, handoff.operator), body)
    with factory().begin() as db:
        with pytest.raises(Problem, match="LAB_IMPORT_ALREADY_ACCEPTED"):
            lab.import_measurements(db, db.get(Account, handoff.operator), body)
    with factory().begin() as db:
        target = db.get(Account, handoff.participant)
        save_record(db, target, "collection_abandon", body.sample_id,
            {"sample_id": body.sample_id, "collection_sha256": digest(handoff.collection)}, body.session_id)
    with factory().begin() as db:
        with pytest.raises(Problem, match="LAB_ANALYSIS_ABANDONED"):
            lab.source_target(db, db.get(Account, handoff.operator), source)


@pytest.mark.parametrize("change", [{"data_generation": True}, {"data_generation": 0},
    {"size_bytes": lab.MAX_REPORT_BYTES + 1}, {"media_type": "application/json"}, {"probability": 0.2}])
def test_strict_bounded_report_request(handoff, change):
    with pytest.raises(ValidationError): lab.LabSourceRequest.model_validate({**handoff.request.data(), **change})


class ReportStore:
    """Versioned bounded storage double, never AWS/LocalStack execution."""
    def __init__(self, data):
        self.data = data
        self.ticket_calls = []
        self.on_read = None

    def generate_presigned_url(self, operation, **kwargs):
        self.ticket_calls.append((operation, kwargs))
        return "https://fictional.invalid/report-upload"

    def head_object(self, **kwargs):
        return {"VersionId": "fictional-version-1"}

    def get_object(self, **kwargs):
        owner = self
        class Body(io.BytesIO):
            def read(self, size=-1):
                if owner.on_read:
                    callback, owner.on_read = owner.on_read, None
                    callback()
                return super().read(size)
        assert kwargs["VersionId"] == "fictional-version-1"
        return {"VersionId": "fictional-version-1", "ContentLength": len(self.data),
            "ContentType": "application/pdf", "Body": Body(self.data)}


def http_source(client, handoff, monkeypatch):
    store = ReportStore(handoff.pdf)
    monkeypatch.setattr(lab.storage, "client", lambda *args, **kwargs: store)
    request_headers = headers("b", key="fictional-delegated-source-ticket")
    response = client.post("/v1/research/lab-source-artifact-uploads", headers=request_headers,
        json=handoff.request.data())
    assert response.status_code == 201, response.text
    return store, response.json(), request_headers


def test_actual_http_delegated_ticket_completion_import_and_minimal_dedup(client, handoff, monkeypatch):
    store, ticket, source_headers = http_source(client, handoff, monkeypatch)
    source = ticket["artifact_id"]
    replay = client.post("/v1/research/lab-source-artifact-uploads", headers=source_headers, json=handoff.request.data())
    assert replay.status_code == 201 and replay.json()["artifact_id"] == source
    assert replay.json()["expires_at"] == ticket["expires_at"]
    assert store.ticket_calls[-1][1]["ExpiresIn"] <= store.ticket_calls[0][1]["ExpiresIn"]
    complete = client.post(f"/v1/research/lab-source-artifact-uploads/{source}/complete", headers=headers("b"),
        json={key: handoff.request.data()[key] for key in ("sha256", "size_bytes", "media_type")})
    assert complete.status_code == 200, complete.text
    body = import_body(handoff, source).data()
    import_headers = headers("b", key="fictional-delegated-import")
    imported = client.post("/v1/research/lab-imports", headers=import_headers, json=body)
    assert imported.status_code == 201, imported.text
    repeat = client.post("/v1/research/lab-imports", headers=import_headers, json=body)
    assert repeat.status_code == 201 and repeat.json() == imported.json()
    status = client.get(f"/v1/sessions/{body['session_id']}/collections/{body['sample_id']}", headers=headers())
    assert status.status_code == 200, status.text
    assert status.json()["state"] == "analysis_available"
    assert status.json()["attempt"]["attempt_id"] == imported.json()["analysis_attempt_id"]
    with factory().begin() as db:
        artifact = db.get(Artifact, source)
        assert artifact.account_id == handoff.participant
        assert artifact.version_id == "fictional-version-1"
        for row in db.scalars(select(Dedup).where(Dedup.account_id == handoff.operator,
            Dedup.route.like("%/research/lab%"))):
            assert not ({"measurements", "upload_url", "required_headers", "account_ref", "sample_id"} & set(row.body))
            assert handoff.pdf.decode() not in str(row.body)
    with factory().begin() as db:
        target = db.get(Account, handoff.participant)
        consent = record(db, target, "consent", body["study_id"])
        consent.body = {**consent.body, "state": "withdrawn"}
        consent.sha256 = digest(consent.body)
    denied = client.post("/v1/research/lab-imports", headers=import_headers, json=body)
    assert denied.status_code == 403, denied.text
    denied_ticket = client.post("/v1/research/lab-source-artifact-uploads", headers=source_headers,
        json=handoff.request.data())
    assert denied_ticket.status_code == 403, denied_ticket.text


def test_http_storage_read_revocation_never_publishes_report(client, handoff, monkeypatch):
    store, ticket, _ = http_source(client, handoff, monkeypatch)
    def revoke():
        with factory().begin() as db:
            db.get(Account, handoff.participant).state = "deleting"
    store.on_read = revoke
    response = client.post(f"/v1/research/lab-source-artifact-uploads/{ticket['artifact_id']}/complete",
        headers=headers("b"), json={key: handoff.request.data()[key] for key in ("sha256", "size_bytes", "media_type")})
    assert response.status_code == 403, response.text
    with factory().begin() as db:
        row = db.get(Artifact, ticket["artifact_id"])
        assert row.state == "quarantine" and row.version_id is None


def test_http_abandonment_denies_same_key_import_replay(client, handoff, monkeypatch):
    _, ticket, _ = http_source(client, handoff, monkeypatch)
    source = ticket["artifact_id"]
    response = client.post(f"/v1/research/lab-source-artifact-uploads/{source}/complete", headers=headers("b"),
        json={key: handoff.request.data()[key] for key in ("sha256", "size_bytes", "media_type")})
    assert response.status_code == 200, response.text
    body = import_body(handoff, source).data()
    h = headers("b", key="fictional-before-abandonment")
    assert client.post("/v1/research/lab-imports", headers=h, json=body).status_code == 201
    with factory().begin() as db:
        target = db.get(Account, handoff.participant)
        save_record(db, target, "collection_abandon", body["sample_id"],
            {"sample_id": body["sample_id"], "collection_sha256": digest(handoff.collection)}, body["session_id"])
    response = client.post("/v1/research/lab-imports", headers=h, json=body)
    assert response.status_code == 410, response.text
