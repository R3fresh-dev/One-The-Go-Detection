"""Real local participant collection, delegated PDF custody and queued result gate.

Run inside the retained Compose project's maintenance container.  This creates
UUID-namespaced FICTIONAL SOFTWARE records under two dedicated fictional OAuth
identities. It never deletes data, changes existing studies, replaces a journal,
calls a worker directly, mocks storage, or grants scientific/human approval.
The staff role preserves its existing study scopes and fails at the 64-scope cap.
"""

import argparse
import base64
import hashlib
import json
import time
from copy import deepcopy
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import select, text as sql_text

from app_flow import signin
from otgd.canonical import digest, strict_loads
from otgd.config import ROOT, settings
from otgd.db import Artifact, Job, Registry, factory, iso, now
from otgd.lab_handoff import PURPOSE
from otgd.local_oauth_state import lock_account
from otgd.operator_cli import require_maintenance_db
from otgd.operator_governance import Configuration, released_version, submit, transition
from otgd.storage import client as aws_client

API = "http://api:8000"
SCOPE = "FICTIONAL SOFTWARE LOCAL ACCEPTANCE ONLY; NO HUMAN OR ASSAY APPROVAL"


def local_origin(value, hosts, port):
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname not in hosts
        or parsed.port != port or parsed.username or parsed.password
        or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise RuntimeError("Participant probe requires exact local service origins")


def admit(cfg):
    if cfg.environment != "local" or cfg.database_url is not None:
        raise RuntimeError("Participant probe requires local real PostgreSQL")
    local_origin(cfg.api_origin, {"localhost", "127.0.0.1", "::1"}, 8000)
    local_origin(cfg.identity_origin, {"localhost", "127.0.0.1", "::1"}, 8081)
    local_origin(cfg.issuer, {"localhost", "127.0.0.1", "::1"}, 8081)
    local_origin(cfg.aws_endpoint_url or "", {"localstack"}, 4566)
    local_origin(cfg.s3_public_endpoint_url or "", {"localhost", "127.0.0.1", "::1"}, 4566)
    for queue in (cfg.queue_url, cfg.dlq_url):
        parsed = urlsplit(queue)
        if (parsed.scheme != "http" or parsed.hostname != "localstack" or parsed.port != 4566
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or not parsed.path.startswith("/queue/" + cfg.aws_region + "/000000000000/otgd-local-")):
            raise RuntimeError("Participant probe cannot use a cloud queue")
    if cfg.database_host != "postgres" or cfg.database_port != 5432 or cfg.database_name != "otgd":
        raise RuntimeError("Participant probe cannot target another database")
    with factory()() as db:
        if db.bind.dialect.name != "postgresql":
            raise RuntimeError("Participant probe cannot substitute SQLite")
        require_maintenance_db(db, cfg)


def common(identity, **fields):
    return {"schema_version": "1.0.0", "registry_id": identity, "version": "v1",
        "expires_at": now() + 86400, "evidence_ref": "FICTIONAL-LOCAL-PARTICIPANT-PROBE",
        "evidence_sha256": hashlib.sha256(SCOPE.encode()).hexdigest(), **fields}


def released(db, kind, body, namespace):
    # Three deliberately distinct local engineering principals execute the real
    # immutable registry workflow. These are never AWS/scientific identities.
    created = submit(db, kind, body, "local:probe-submitter-" + namespace)
    transition(db, kind, body["registry_id"], body["version"], "approve",
        "local:probe-reviewer-" + namespace, SCOPE, created["revision"])
    db.flush()
    transition(db, kind, body["registry_id"], body["version"], "release",
        "local:probe-releaser-" + namespace, SCOPE, 2)
    db.flush()


def provision(cfg, subject, staff, namespace, *, staff_subject="local-participant_probe_staff"):
    ids = {key: "fictional-probe-" + namespace + "-" + key for key in (
        "study", "protocol", "policy", "config", "qualification", "collection", "method",
        "instrument", "device", "key", "calibration")}
    text = SCOPE + ". Fictional collection instructions: use the software fixture only."
    protocol = {"schema_version": "1.0.0", "kind": "reference_lab",
        "instruction_id": "fictional-instructions-" + namespace, "version": "v1",
        "text": text, "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "maximum_acknowledgment_age_seconds": 120,
        "maximum_collection_submission_delay_seconds": 300,
        "maximum_analysis_delay_seconds": 86400,
        "required_confirmations": [{"id": "method_reviewed", "text": "I reviewed this fictional procedure."}],
        "methods": [{"id": ids["collection"], "version": "v1", "instructions": SCOPE,
            "saliva_volume_required": True, "buffer_volume_required": True,
            "dilution_factor_required": True, "dilution_definition": "total_mixture_over_saliva",
            "fixed_dilution_factor": None, "saliva_volume_min_ml": 0.5, "saliva_volume_max_ml": 2.0,
            "buffer_volume_min_ml": 0.0, "buffer_volume_max_ml": 2.0,
            "collector_lot_required": True, "container_required": True, "expiry_required": True,
            "permitted_containers": ["FICTIONAL-CONTAINER"], "required_handling_events": ["sealed"],
            "permitted_null_reasons": ["unknown", "not_applicable"]}]}
    material = {"schema_version": "1.0.0", "channel": "saliva", "source": "reference_lab",
        "collection_method_ids": [ids["collection"]], "assay_bases": ["free"],
        "concentration_bases": ["collected_mixture"], "correction_statuses": ["not_corrected"]}
    config = Configuration.model_validate(common(ids["config"], configuration_id=ids["config"],
        study_id=ids["study"], protocol_id=ids["protocol"], channel="saliva", sha256=digest(material),
        material=material, qualification_evidence_ref=ids["qualification"], retention_policy_id=ids["policy"],
        max_duration_ms=600000, software_adapter_id="reference_lab_import_v1",
        lab_methods={ids["method"]: {"calibration_ids": [ids["calibration"]],
            "instrument_ids": [ids["instrument"]]}}, participant_protocol=protocol)).data()
    study_text = SCOPE + ". This is not a real approved study."
    study = common(ids["study"], study_id=ids["study"], protocol_id=ids["protocol"],
        name="Fictional local participant software probe", account_refs=[subject, staff],
        invitation_id="fictional-invitation-" + namespace, document_version="v1",
        document_text=study_text, document_sha256=hashlib.sha256(study_text.encode()).hexdigest(),
        retention_summary=SCOPE, channels={"saliva": ids["config"]})
    notice = SCOPE + ". Fictional source PDF retained by the software fixture."
    retention = common(ids["policy"], policy_id=ids["policy"], study_id=ids["study"],
        raw_kinds=["source_lab_report"], max_retention_days=30, access_roles=["lab_importer"],
        withdrawal_behavior="delete_live_data", exceptions=[], purpose_id=PURPOSE,
        purpose_text=SCOPE, raw_notice_version="v1", raw_notice_text=notice,
        raw_notice_sha256=hashlib.sha256(notice.encode()).hexdigest())
    private = ec.generate_private_key(ec.SECP256R1())
    public = private.public_key().public_bytes(serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo)
    device = common(ids["device"] + ":" + ids["key"], device_id=ids["device"], key_id=ids["key"],
        public_key_spki=base64.b64encode(public).decode(), hardware_revision="fictional-fixture",
        firmware_version="fictional-fixture", approved_protocol_ids=[ids["protocol"]], account_refs=[subject])
    calibration = common(ids["calibration"], calibration_id=ids["calibration"], purpose="device",
        device_id=ids["device"], key_id=ids["key"], hardware_revision="fictional-fixture",
        firmware_versions=["fictional-fixture"], channels=["saliva"], calibration_sha256="3" * 64)
    method = common(ids["method"], method_id=ids["method"], assay_bases=["free"],
        collection_method_ids=[ids["collection"]], instrument_ids=[ids["instrument"]],
        laboratory_ids=["fictional-software-laboratory"])
    proof = common(ids["qualification"], channel="saliva", configuration_sha256=config["sha256"],
        document_sha256="2" * 64, reviewed_by="Fictional independent software reviewer",
        approval_status="approved", purpose="measurement_collection", configuration_registry_id=ids["config"],
        configuration_version="v1", configuration_submitted_sha256=digest(config))
    with factory().begin() as db:
        require_maintenance_db(db, cfg)
        db.execute(sql_text("SET LOCAL lock_timeout = '2s'"))
        # Match runtime Account→registry ordering. This account comes only from
        # the dedicated staff OAuth identity; no unrelated role is maintained.
        locked_staff = lock_account(db, staff_subject, cfg)
        if not locked_staff or locked_staff.id != staff or locked_staff.state != "active":
            raise RuntimeError("Dedicated fictional staff account is unavailable")
        for kind, value in (("study", study), ("retention", retention), ("device", device),
            ("calibration", calibration), ("method", method), ("qualification", proof), ("configuration", config)):
            released(db, kind, value, namespace)
        pointer = db.get(Registry, "role:" + staff)
        prior = released_version(db, "role", staff, required=False) if pointer else None
        old = prior.body if prior else None
        # Preserve every still-current scope. Only unavailable/expired scopes
        # are omitted in this new version; old roles/studies remain untouched.
        prior_studies = [identity for identity in old["study_ids"]
            if released_version(db, "study", identity, required=False)] if old else []
        if len(prior_studies) >= 64:
            raise RuntimeError("Dedicated fictional staff role reached its preserved 64-study cap")
        role = common(staff, account_ref=staff, roles=list(old["roles"]) if old else ["lab_import"],
            study_ids=prior_studies + [ids["study"]])
        role["version"] = "probe-" + namespace
        released(db, "role", role, namespace)
    return ids, config, study, {"preserved_current_staff_scopes": len(prior_studies),
        "omitted_unavailable_staff_scopes": len(old["study_ids"]) - len(prior_studies) if old else 0}


class Actor:
    def __init__(self, http, token):
        self.http, self.token, self.generation = http, token, 1
        caps = self.request("GET", "/v1/me/capabilities")
        self.account, self.generation = caps["account_ref"], caps["data_generation"]
        if caps["account_state"] != "active":
            raise RuntimeError("Dedicated fictional identity is not active; existing data was preserved")

    def request(self, method, path, body=None, revision=None, status=(200, 201, 202), key=None, with_status=False, timeout=None):
        headers = {"Authorization": "Bearer " + self.token, "X-Data-Generation": str(self.generation),
            "Idempotency-Key": key or str(uuid4())}
        if revision is not None:
            headers["If-Match"] = '"' + str(revision) + '"'
        request_options = {} if timeout is None else {"timeout": timeout}
        response = self.http.request(method, API + path, headers=headers, json=body, **request_options)
        if response.status_code not in status:
            # Tokens, bearer URLs, PDF bodies and health payloads never enter logs.
            try:
                code = response.json().get("code", "UNEXPECTED_HTTP_STATUS")
            except ValueError:
                code = "UNEXPECTED_HTTP_STATUS"
            raise AssertionError(f"Participant probe {method} {path}: HTTP {response.status_code} {code}")
        value = response.json()
        return (response.status_code, value) if with_status else value


def put_signed_pdf(http, cfg, ticket, pdf, expected):
    parsed = urlsplit(ticket["upload_url"])
    origin = urlsplit(cfg.s3_public_endpoint_url)
    if (parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc) or parsed.fragment or parsed.username or parsed.password:
        raise RuntimeError("Signed source upload escaped the configured local origin")
    # Route to the same Compose S3 service while preserving the signed Host and
    # exact path/query. A URL pointing at localhost inside this container would
    # otherwise target the container itself; changing its signed Host is invalid.
    route = urlunsplit(("http", "localstack:4566", parsed.path, parsed.query, ""))
    headers = {**ticket["required_headers"], "Host": parsed.netloc}
    response = http.put(route, headers=headers, content=pdf)
    if response.status_code != expected:
        raise AssertionError(f"Actual signed PDF upload expected {expected}, received {response.status_code}")


def probe():
    cfg = settings()
    admit(cfg)
    namespace = uuid4().hex[:16]
    with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as http:
        subject = Actor(http, signin(http, cfg, "participant_probe_subject"))
        staff = Actor(http, signin(http, cfg, "participant_probe_staff"))
        if subject.account == staff.account:
            raise AssertionError("Staff and participant must be independently authenticated")
        app = http.get(API + "/v1/app-config")
        app.raise_for_status()
        for actor in (subject, staff):
            actor.request("POST", "/v1/me/acknowledgments", {"version": "v1",
                "sha256": app.json()["notice"]["sha256"], "acknowledged_at": iso()})
        ids, config, study, role_maintenance = provision(cfg, subject.account, staff.account, namespace)
        subject.request("POST", "/v1/studies/" + ids["study"] + "/consents", {
            **{key: study[key] for key in ("invitation_id", "document_version", "document_sha256")},
            "accepted": True, "acknowledged_at": iso()})
        sid, aid, sample = (str(uuid4()) for _ in range(3))
        base = "/v1/sessions/" + sid
        subject.request("POST", "/v1/sessions", {"session_id": sid, "mode": "controlled_research",
            "study_id": ids["study"], "protocol_id": ids["protocol"]})
        snapshot = strict_loads((ROOT / "examples/synthetic_session.json").read_bytes())
        snapshot.update(session_id=sid, subject_ref=subject.account, mode="controlled_research",
            study_id=ids["study"], protocol_id=ids["protocol"], created_at=iso())
        snapshot["target_at"] = snapshot["created_at"]
        snapshot["profile"]["source"] = "study_measurement"
        context = {"schema_version": "1.0.0", "session_id": sid, "context_confirmed_at": snapshot["created_at"],
            "profile_version_id": None, "profile_snapshot_sha256": digest(snapshot["profile"]),
            "history_snapshot_sha256": digest(snapshot["history"]), "protocol_id": ids["protocol"],
            "configuration_refs": [{"id": ids["config"], "version": "v1", "sha256": config["sha256"],
                "scope": "measurement_collection"}], "baseline_refs": [], "device_associations": [],
            "self_report_context": None}
        subject.request("PUT", base + "/context", context, revision=0)
        attempt = {"schema_version": "1.0.0", "session_id": sid, "attempt_id": aid,
            "component": "saliva", "record_id": sample, "supersedes_attempt_id": None,
            "status": "started", "source": "reference_lab", "started_at": iso(), "ended_at": None,
            "configuration_id": ids["config"], "configuration_hash": config["sha256"],
            "quality_flags": [], "component_metadata": {}, "artifact_refs": [], "attestation_refs": []}
        subject.request("PUT", base + "/attempts/" + aid, attempt, revision=0)
        ack = {"attempt_id": aid, "configuration_id": ids["config"], "configuration_version": "v1",
            "configuration_hash": config["sha256"], "configuration_submitted_sha256": digest(config),
            "participant_protocol_sha256": digest(config["participant_protocol"]), "acknowledged_at": iso(),
            "confirmed": True, "confirmations": ["method_reviewed"], "setup_id": None,
            "rest_started_at": None, "collection_method_id": ids["collection"], "collection_method_version": "v1"}
        receipt = subject.request("POST", base + "/instruction-acknowledgments", ack)
        grant = subject.request("POST", base + "/capture-authorizations", {"attempt_id": aid,
            "channel": "saliva", "binding_id": None, "device_id": None, "configuration_id": ids["config"],
            "configuration_hash": config["sha256"], "raw_recording_kind": None,
            "instruction_receipt_id": receipt["instruction_receipt_id"]})
        if grant["binding_id"] is not None or grant["device_id"] is not None or grant["instruction_receipt"] != receipt:
            raise AssertionError("Reference-lab collection invented BLE or changed preparation authority")
        subject.request("POST", base + "/capture-authorizations/" + grant["authorization_id"] + "/start",
            {"attempt_id": aid, "device_boot_id": None, "device_nonce": None})
        collected_at = iso()
        collected = subject.request("POST", base + "/collections", {"attempt_id": aid, "sample_id": sample,
            "instruction_receipt_id": receipt["instruction_receipt_id"], "collection_method_id": ids["collection"],
            "collection_method_version": "v1", "collected_at": collected_at, "status": "valid", "quality_flags": [],
            "saliva_volume_ml": 1.0, "buffer_volume_ml": 1.0, "dilution_factor": 2.0,
            "collector_id": "FICTIONAL-COLLECTOR", "collector_lot": "FICTIONAL-LOT",
            "container_id": "FICTIONAL-CONTAINER", "cartridge_lot": None, "cartridge_expiry": iso(now() + 3600),
            "missing_reasons": {"cartridge_lot": "not_applicable"}, "storage_handling_events": [{
                "event": "sealed", "occurred_at": collected_at, "temperature_c": None, "duration_min": None}]})
        collection_path = base + "/collections/" + sample
        pending = subject.request("GET", collection_path)
        if pending["state"] != "pending_lab" or pending["projection"]["saliva"] != []:
            raise AssertionError("Collection fabricated analytes or lost pending analysis")
        blocked = subject.request("POST", base + "/finalize", {"snapshot_sha256": "a" * 64,
            "evidence_sha256": "b" * 64}, revision=1, status=(409,))
        if blocked["code"] != "LAB_ANALYSIS_PENDING":
            raise AssertionError("Pending analysis did not block finalization")
        pdf = ("%PDF-1.7\n" + SCOPE + "\n" + namespace + "\n").encode()
        source = {"account_ref": subject.account, "data_generation": subject.generation,
            "study_id": ids["study"], "session_id": sid, "sample_id": sample,
            "collection_attempt_id": aid, "sha256": hashlib.sha256(pdf).hexdigest(),
            "size_bytes": len(pdf), "media_type": "application/pdf"}
        denied = subject.request("POST", "/v1/research/lab-source-artifact-uploads", source, status=(403,))
        if denied["code"] != "DELEGATED_LAB_OPERATOR_REQUIRED":
            raise AssertionError("Participant could enter delegated report custody")
        ticket = staff.request("POST", "/v1/research/lab-source-artifact-uploads", source)
        put_signed_pdf(http, cfg, ticket, pdf, 200)
        put_signed_pdf(http, cfg, ticket, pdf, 412)
        staff.request("POST", "/v1/research/lab-source-artifact-uploads/" + ticket["artifact_id"] + "/complete",
            {key: source[key] for key in ("sha256", "size_bytes", "media_type")})
        with factory()() as db:
            artifact = db.scalar(select(Artifact).where(Artifact.id == ticket["artifact_id"]))
            if (artifact.account_id != subject.account or artifact.generation != subject.generation
                or artifact.state != "verified" or not artifact.version_id or artifact.version_id == "null"):
                raise AssertionError("Live report custody did not pin an owned S3 version")
            obj = aws_client("s3").get_object(Bucket=artifact.bucket, Key=artifact.key, VersionId=artifact.version_id)
            try:
                if obj["Body"].read(len(pdf) + 1) != pdf or obj.get("VersionId") != artifact.version_id:
                    raise AssertionError("Live exact-version report bytes differ")
            finally:
                obj["Body"].close()
        measurement = deepcopy(snapshot["saliva"][0])
        measurement.update(measurement_id=str(uuid4()), sample_id=sample, collected_at=collected_at,
            measured_at=iso(), source="reference_lab", method_id=ids["method"], calibration_id=ids["calibration"],
            instrument_id=ids["instrument"], operator_ref=staff.account, concentration_basis="collected_mixture")
        body = {key: source[key] for key in ("account_ref", "data_generation", "study_id",
            "session_id", "sample_id", "collection_attempt_id")}
        body.update(source_report_artifact_id=ticket["artifact_id"], measurements=[measurement])
        import_key = str(uuid4())
        imported = staff.request("POST", "/v1/research/lab-imports", body, key=import_key)
        if staff.request("POST", "/v1/research/lab-imports", body, key=import_key) != imported:
            raise AssertionError("Accepted import did not reconcile exact-key replay")
        if set(imported) != {"import_id", "analysis_attempt_id", "state"}:
            raise AssertionError("Staff import receipt persisted health payload")
        current = subject.request("GET", collection_path)
        if (current["state"] != "analysis_available" or current["collection_attempt"] != collected["attempt"]
            or current["attempt"]["attempt_id"] != imported["analysis_attempt_id"]
            or current["attempt"]["supersedes_attempt_id"] != aid
            or current["attempt_sha256"] != digest(current["attempt"])
            or current["imports"][0]["measurements"] != [measurement]):
            raise AssertionError("Participant refresh lost immutable collection/analysis lineage")
        evidence = subject.request("GET", base + "/evidence")
        if evidence["instruction_receipts"] != [receipt] or evidence["collections"] != [collected]:
            raise AssertionError("Current evidence omitted exact instruction or collection receipt")
        snapshot["device"] = {key: "unavailable" for key in snapshot["device"]}
        snapshot["sample"], snapshot["saliva"] = current["projection"]["sample"], [measurement]
        for component in ("eyes", "cardiac", "task"):
            snapshot[component].update(status="not_collected", source="prototype_sensor", started_at=None, ended_at=None)
        snapshot["eyes"].update(frame_rate_hz=None, baseline_diameter_mm=None, relative_constriction=None, latency_ms=None)
        snapshot["cardiac"].update(modality="ppg", heart_rate_bpm=None)
        snapshot["task"].update(practice_trials=0, scored_trials=0, go_trials=0, no_go_trials=0, valid_correct_go_trials=0,
            features={key: None for key in snapshot["task"]["features"]})
        snapshot.update(acquisition_span_ms=0.0, capture_completed_at=iso())
        subject.request("PUT", base + "/snapshot", snapshot, revision=1)
        manifest = {"schema_version": "1.0.0", "session_id": sid, "context_sha256": digest(context),
            "attempts": [{"attempt_id": item["attempt_id"], "sha256": digest(item)} for item in evidence["attempts"]],
            "selected": {"saliva": imported["analysis_attempt_id"], "eyes": None, "cardiac": None, "task": None, "alcohol": None}}
        subject.request("PUT", base + "/evidence-manifest", manifest, revision=0)
        queued = subject.request("POST", base + "/finalize", {"snapshot_sha256": digest(snapshot),
            "evidence_sha256": digest(manifest)}, revision=2)
        if queued["session_id"] != sid or queued["state"] != "processing":
            raise AssertionError("Finalization changed the owned session or processing receipt")
        deadline = time.monotonic() + 60
        while (remaining := deadline - time.monotonic()) > 0:
            status, result = subject.request("GET", base + "/result", status=(200, 202), with_status=True,
                timeout=min(15, remaining))
            if time.monotonic() > deadline:
                raise AssertionError("Actual SQS participant result worker exceeded 60 seconds")
            if status == 200:
                break
            if result != {"session_id": sid, "state": "processing"}:
                raise AssertionError("Pending result changed the owned session or processing state")
            time.sleep(min(0.25, max(0, deadline - time.monotonic())))
        else:
            raise AssertionError("Actual SQS participant result worker exceeded 60 seconds")
        if result["probability"] is not None or result["state"] != "inconclusive" or result["reason_codes"] != ["STUDY_UNAUTHORIZED"]:
            raise AssertionError("Fictional unmodeled study produced a numerical research estimate")
        with factory().begin() as db:
            job = db.get(Job, queued["job_id"])
            if (job is None or job.account_id != subject.account or job.generation != subject.generation
                or job.kind != "result" or job.body != {"session_id": sid} or job.state != "completed"
                or job.completed is None or job.output != result):
                raise AssertionError("Actual queued result did not retain its owned completed job")
    return {"status": "passed", "fixture_scope": SCOPE, **role_maintenance, "actual_oauth_pkce": True,
        "actual_postgresql_registry_three_principals": True, "reference_lab_without_ble": True,
        "immutable_instruction_collection_analysis": True, "pending_blocks_finalization": True,
        "participant_lab_custody_denied": True, "actual_presigned_pdf_put": True,
        "conditional_replay_http_status": 412, "actual_s3_version_verified": True,
        "distinct_staff_import_and_replay": True, "actual_sqs_worker_completed": True,
        "inference_available": False, "existing_data_deleted": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-fictional-workspace", action="store_true")
    args = parser.parse_args()
    if not args.confirm_fictional_workspace:
        raise RuntimeError("Explicit fictional local acceptance flag is required")
    print(json.dumps(probe(), sort_keys=True))
