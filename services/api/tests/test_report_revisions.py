"""Administrative report software tests; all laboratories/approvals are fictional.

These fixtures deliberately seed an already accepted analytical record. They are
not participant acquisition, active registry provisioning, or assay evidence.
"""

from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
import io
import zipfile

import pytest
from sqlalchemy import select, delete

from otgd import storage
from otgd.canonical import canonical, digest, strict_loads
from otgd.config import settings
from otgd.db import (
    Account,
    Artifact,
    Check,
    RateBucket,
    Record,
    Registry,
    factory,
    iso,
    now,
)
from otgd.domain import (
    measurement_result,
    rec_id,
    save_record,
    validate_component,
    validate_session,
)
from otgd.dto import CaptureAttempt
from otgd.report_revisions import (
    PURPOSE,
    load_chain,
    export_records,
    _finite_expiry,
    ensure_artifact_capacity,
)
from otgd.errors import Problem
from otgd.worker import run_job, export_manifest_bytes

from .conftest import headers
from .helpers import session_fixture
from .test_api import store as versioned_store_fixture

STUDY = "FICTIONAL-REVISION-STUDY"
PROTOCOL = "FICTIONAL-REVISION-PROTOCOL"
CONFIGURATION = "FICTIONAL-APPROVED-CONFIGURATION"
PROOF = "FICTIONAL-QUALIFICATION-EVIDENCE"
METHOD = "FICTIONAL-LAB-METHOD"
CALIBRATION = "FICTIONAL-CALIBRATION"
INSTRUMENT = "FICTIONAL-LAB-INSTRUMENT"
RETENTION = "FICTIONAL-REPORT-RETENTION"


@pytest.fixture
def store(monkeypatch):
    """Reuse the explicit unit-test double; this never contacts LocalStack/AWS."""
    return versioned_store_fixture.__wrapped__(monkeypatch)


@pytest.fixture
def laboratory(client, account, store):
    snapshot = session_fixture(account)
    snapshot.update(mode="analytical", study_id=STUDY, protocol_id=PROTOCOL)
    snapshot["profile"]["source"] = "study_measurement"
    for channel in ("eyes", "cardiac", "task"):
        snapshot[channel]["source"] = "prototype_sensor"
    snapshot["cardiac"].update(
        modality="ppg",
        sample_rate_hz=100.0,
        acquisition_config_id="FICTIONAL_ACCEPTED_PPG",
    )
    # This fixture exercises laboratory report administration, not a native
    # reaction task. Preserve absence instead of inventing native timing proof.
    snapshot["task"].update(
        status="not_collected",
        source="prototype_sensor",
        started_at=None,
        ended_at=None,
        practice_trials=0,
        scored_trials=0,
        go_trials=0,
        no_go_trials=0,
        valid_correct_go_trials=0,
        features={key: None for key in snapshot["task"]["features"]},
        events_artifact_id=None,
    )
    starts = [snapshot["sample"]["collected_at"]] + [
        snapshot[key]["started_at"] for key in ("eyes", "cardiac")
    ]
    ends = [snapshot["sample"]["collected_at"]] + [
        snapshot[key]["ended_at"] for key in ("eyes", "cardiac")
    ]
    def instant(value):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    snapshot["acquisition_span_ms"] = (
        max(map(instant, ends)) - min(map(instant, starts))
    ).total_seconds() * 1000
    for reading in snapshot["saliva"]:
        reading["source"] = "reference_lab"
        if reading["qualifier"] != "not_measured":
            reading.update(
                method_id=METHOD, calibration_id=CALIBRATION, instrument_id=INSTRUMENT
            )
    validate_session(snapshot)
    session_id = snapshot["session_id"]
    consent_id, artifact_id = str(uuid4()), str(uuid4())
    scope = {
        "study_id": STUDY,
        "session_id": session_id,
        "consent_record_id": consent_id,
        "retention_policy_id": RETENTION,
        "artifact_kind": "source_lab_report",
        "purpose": PURPOSE,
    }
    pdf = b"%PDF-1.7\nFICTIONAL TEST LABORATORY REPORT ONLY\n"
    key = f"quarantine/{account}/1/{artifact_id}"
    version = store.put(settings().artifact_bucket, key, pdf, "application/pdf")
    context = {
        "schema_version": "1.0.0",
        "session_id": session_id,
        "context_confirmed_at": snapshot["created_at"],
        "profile_version_id": None,
        "profile_snapshot_sha256": digest(snapshot["profile"]),
        "history_snapshot_sha256": digest(snapshot["history"]),
        "protocol_id": PROTOCOL,
        "configuration_refs": [],
        "baseline_refs": [],
        "device_associations": [],
        "self_report_context": None,
    }
    attempts = []
    for component in ("saliva", "eyes", "cardiac", "task"):
        projection = (
            {"sample": snapshot["sample"], "saliva": snapshot["saliva"]}
            if component == "saliva"
            else snapshot[component]
        )
        attempts.append(
            {
                "schema_version": "1.0.0",
                "session_id": session_id,
                "attempt_id": str(uuid4()),
                "component": component,
                "record_id": snapshot["sample"]["sample_id"]
                if component == "saliva"
                else snapshot["task"]["task_id"]
                if component == "task"
                else str(uuid4()),
                "supersedes_attempt_id": None,
                "status": "valid" if component == "saliva" else projection["status"],
                "source": "reference_lab"
                if component == "saliva"
                else projection["source"],
                "started_at": snapshot["sample"]["collected_at"]
                if component == "saliva"
                else projection["started_at"],
                "ended_at": snapshot["sample"]["collected_at"]
                if component == "saliva"
                else projection["ended_at"],
                "configuration_id": CONFIGURATION
                if component == "saliva"
                else projection["acquisition_config_id"]
                if component == "cardiac"
                else None
                if component == "task"
                else "FICTIONAL_ACCEPTED_" + component,
                "configuration_hash": None
                if component == "task"
                else "2" * 64,
                "quality_flags": [],
                "component_metadata": {
                    "projection": projection,
                    **({"modality": "ppg"} if component == "cardiac" else {}),
                },
                "artifact_refs": [],
                "attestation_refs": [],
            }
        )
    # Already-accepted fictional evidence still has to be internally coherent;
    # seeding is not a reason to bypass component or strict DTO validation.
    for attempt in attempts:
        CaptureAttempt.model_validate(attempt)
        validate_component(attempt)
    manifest = {
        "schema_version": "1.0.0",
        "session_id": session_id,
        "context_sha256": digest(context),
        "attempts": [
            {"attempt_id": x["attempt_id"], "sha256": digest(x)} for x in attempts
        ],
        "selected": {
            **{x["component"]: x["attempt_id"] for x in attempts},
            "alcohol": None,
        },
    }
    with factory().begin() as db:
        a = db.get(Account, account)
        check = Check(
            id=session_id,
            account_id=account,
            generation=1,
            state="completed",
            revision=7,
            mode="analytical",
            study_id=STUDY,
            protocol_id=PROTOCOL,
            snapshot=snapshot,
            snapshot_sha256=digest(snapshot),
            evidence_sha256=digest(manifest),
        )
        check.result = measurement_result(check)
        db.add(check)
        save_record(db, a, "context", session_id, context, session_id)
        for attempt in attempts:
            save_record(db, a, "attempt", attempt["attempt_id"], attempt, session_id)
        save_record(db, a, "manifest", session_id, manifest, session_id)
        save_record(
            db,
            a,
            "consent",
            STUDY,
            {
                "state": "active",
                "document_sha256": "1" * 64,
                "consent_record_id": consent_id,
            },
        )
        records = {
            ("study", STUDY): {
                "account_refs": [account],
                "channels": {"saliva": CONFIGURATION},
                "document_sha256": "1" * 64,
            },
            ("configuration", CONFIGURATION): {
                "configuration_id": CONFIGURATION,
                "channel": "saliva",
                "study_id": STUDY,
                "protocol_id": PROTOCOL,
                "qualification_evidence_ref": PROOF,
                "sha256": "2" * 64,
                "retention_policy_id": RETENTION,
                "expires_at": now() + 86400,
                "raw_retention_approved": True,
                "lab_methods": {
                    METHOD: {
                        "calibration_ids": [CALIBRATION],
                        "instrument_ids": [INSTRUMENT],
                    }
                },
            },
            ("qualification", PROOF): {
                "approval_status": "approved",
                "configuration_sha256": "2" * 64,
                "channel": "saliva",
                "document_sha256": "3" * 64,
                "reviewed_by": "FICTIONAL_REVIEWER",
                "expires_at": now() + 86400,
            },
            ("role", account): {
                "roles": ["lab_report_revision"],
                "study_ids": [STUDY],
                "expires_at": now() + 86400,
            },
        }
        for (kind, ident), body in records.items():
            db.add(Registry(id=kind + ":" + ident, kind=kind, body=body, active=True))
        db.add(
            Artifact(
                id=artifact_id,
                account_id=account,
                generation=1,
                session_id=session_id,
                bucket=settings().artifact_bucket,
                key=key,
                version_id=version,
                sha256=__import__("hashlib").sha256(pdf).hexdigest(),
                size=len(pdf),
                media_type="application/pdf",
                kind="source_lab_report",
                state="verified",
                expires=now() - 400,
                scope=scope,
            )
        )
    return SimpleNamespace(
        account=account,
        session_id=session_id,
        snapshot=snapshot,
        artifact_id=artifact_id,
        consent_id=consent_id,
        scope=scope,
        source_version=version,
        store=store,
    )


def body_for(lab, predecessor=None, kind="correction"):
    reading = deepcopy(lab.snapshot["saliva"][0])
    reading.update(
        measurement_id=str(uuid4()),
        value_ng_ml=6.0,
        measured_at=iso(now() - 30),
        original_report={"value": 6000.0, "unit": "pg/mL", "qualifier": "quantified"},
    )
    return {
        "schema_version": "1.0.0",
        "revision_id": str(uuid4()),
        "study_id": STUDY,
        "sample_id": lab.snapshot["sample"]["sample_id"],
        "base_snapshot_sha256": digest(lab.snapshot),
        "expected_previous_revision_id": predecessor["revision_id"]
        if predecessor
        else None,
        "expected_previous_revision_sha256": predecessor["revision_sha256"]
        if predecessor
        else None,
        "kind": kind,
        "reason_code": "CORRECTED_LABORATORY_REPORT"
        if kind == "correction"
        else "SPECIMEN_REANALYSIS",
        "reported_at": iso(now() - 10),
        "source_report_artifact_id": lab.artifact_id,
        "replacement_measurements": [reading],
    }


def post(client, lab, body=None, key=None, **claims):
    return client.post(
        f"/v1/research/sessions/{lab.session_id}/report-revisions",
        headers=headers(key=key, **claims),
        json=body or body_for(lab),
    )


def accepted(client, lab, body=None, key=None):
    response = post(client, lab, body, key)
    assert response.status_code == 201, response.text
    return response.json()


def mutate_registry(kind, ident, change):
    with factory().begin() as db:
        value = db.get(Registry, kind + ":" + ident)
        body = deepcopy(value.body)
        change(body)
        value.body = body


def test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units(
    client, laboratory
):
    lab = laboratory
    with factory()() as db:
        original = db.get(Check, lab.session_id)
        before = canonical(
            {
                "snapshot": original.snapshot,
                "result": original.result,
                "revision": original.revision,
                "snapshot_sha256": original.snapshot_sha256,
                "evidence_sha256": original.evidence_sha256,
            }
        )
    first = accepted(client, lab)
    assert (
        first["descriptor"]["report"]["source_report"]["version_id"]
        == lab.source_version
    )
    assert first["revision_sha256"] == digest(first["descriptor"])
    assert first["result_sha256"] == digest(first["result"])
    assert (
        first["result"]["probability"] is None
        and first["result"]["inference_available"] is False
    )
    readings = {x["analyte"]: x for x in first["effective_measurements"]}
    assert readings["THC"]["value_ng_ml"] == 6
    assert readings["THC"]["original_report"] == {
        "value": 6000,
        "unit": "pg/mL",
        "qualifier": "quantified",
    }
    assert readings["THC_COOH"] == lab.snapshot["saliva"][1]
    second = accepted(client, lab, body_for(lab, first, "reanalysis"))
    assert second["sequence"] == 2
    assert second["result"]["replaces_result_id"] == first["result"]["result_id"]
    assert second["result"]["target_at"] == lab.snapshot["target_at"]
    assert (
        second["descriptor"]["report"]["replacement_measurements"][0]["measured_at"]
        > lab.snapshot["capture_completed_at"]
    )
    with factory()() as db:
        original = db.get(Check, lab.session_id)
        after = canonical(
            {
                "snapshot": original.snapshot,
                "result": original.result,
                "revision": original.revision,
                "snapshot_sha256": original.snapshot_sha256,
                "evidence_sha256": original.evidence_sha256,
            }
        )
    assert before == after
    listed = client.get(
        f"/v1/sessions/{lab.session_id}/report-revisions", headers=headers()
    ).json()
    assert listed["items"][0]["next_revision_id"] == second["revision_id"]
    assert listed["items"][1]["previous_revision_id"] == first["revision_id"]
    detail = client.get(
        f"/v1/sessions/{lab.session_id}/report-revisions/{first['revision_id']}",
        headers=headers(),
    )
    assert (
        detail.json()["revision"] == first
        and detail.json()["next_revision_id"] == second["revision_id"]
    )


@pytest.mark.parametrize("state", ["invalid", "inconclusive"])
def test_valid_chemistry_cannot_promote_an_invalid_or_inconclusive_base(
    client, laboratory, state
):
    with factory().begin() as db:
        check = db.get(Check, laboratory.session_id)
        check.result = {**check.result, "state": state}
    result = accepted(client, laboratory)
    assert result["result"]["state"] == state


def test_not_measured_withdrawal_preserves_null_analytical_identity_and_unchanged_analytes(
    client, laboratory
):
    body = body_for(laboratory)
    reading = body["replacement_measurements"][0]
    reading.update(
        qualifier="not_measured",
        value_ng_ml=None,
        measured_at=None,
        method_id=None,
        calibration_id=None,
        instrument_id=None,
        original_report={"value": None, "unit": "ng/mL", "qualifier": "not_measured"},
    )
    value = accepted(client, laboratory, body)
    changed = value["descriptor"]["report"]["replacement_measurements"][0]
    assert all(
        changed[key] is None
        for key in (
            "value_ng_ml",
            "method_id",
            "calibration_id",
            "instrument_id",
            "measured_at",
        )
    )
    assert value["descriptor"]["report"]["authorization"]["approved_lab_methods"] == {}
    assert len(value["effective_measurements"]) == 3
    assert (
        client.get(
            f"/v1/sessions/{laboratory.session_id}/report-revisions", headers=headers()
        ).status_code
        == 200
    )


def test_invalid_analytical_report_makes_companion_invalid_without_changing_base(
    client, laboratory
):
    body = body_for(laboratory)
    reading = body["replacement_measurements"][0]
    reading.update(
        qualifier="invalid",
        value_ng_ml=None,
        quality_flags=["FICTIONAL_LAB_RETRACTION"],
        original_report={"value": None, "unit": "ng/mL", "qualifier": "invalid"},
    )
    result = accepted(client, laboratory, body)
    assert result["result"]["state"] == "invalid"
    assert "INVALID_ANALYTICAL_REPORT" in result["result"]["reason_codes"]
    with factory()() as db:
        assert (
            db.get(Check, laboratory.session_id).result["state"] == "measurement_only"
        )


def test_idempotency_stable_identity_and_predecessor_conflicts_do_not_branch(
    client, laboratory
):
    body = body_for(laboratory)
    first = accepted(client, laboratory, body, "report-idempotency")
    assert accepted(client, laboratory, body, "report-idempotency") == first
    assert accepted(client, laboratory, body, "new-key-same-revision") == first
    changed = deepcopy(body)
    changed["replacement_measurements"][0].update(
        value_ng_ml=7,
        original_report={"value": 7000, "unit": "pg/mL", "qualifier": "quantified"},
    )
    assert post(client, laboratory, changed, "report-idempotency").status_code == 409
    assert post(client, laboratory, changed, "changed-stable-id").status_code == 409
    response = post(client, laboratory, body_for(laboratory))
    assert (
        response.status_code == 409
        and response.json()["code"] == "REPORT_REVISION_CONFLICT"
    )


@pytest.mark.parametrize("revocation", ["role", "consent", "retention", "protocol"])
def test_current_authority_is_checked_before_mutation_replay_but_owned_history_remains(
    client, laboratory, revocation
):
    body = body_for(laboratory)
    first = accepted(client, laboratory, body, "revoked-replay")
    if revocation == "role":
        mutate_registry("role", laboratory.account, lambda x: x.update(roles=[]))
    elif revocation == "consent":
        with factory().begin() as db:
            row = db.get(Record, laboratory.account + ":consent:" + STUDY)
            row.body = {**row.body, "state": "withdrawn"}
    elif revocation == "retention":
        mutate_registry(
            "configuration",
            CONFIGURATION,
            lambda x: x.update(raw_retention_approved=False),
        )
    else:
        mutate_registry(
            "configuration",
            CONFIGURATION,
            lambda x: x.update(protocol_id="UNRELATED_PROTOCOL"),
        )
    assert post(client, laboratory, body, "revoked-replay").status_code == 403
    read = client.get(
        f"/v1/sessions/{laboratory.session_id}/report-revisions/{first['revision_id']}",
        headers=headers(),
    )
    assert read.status_code == 200


@pytest.mark.parametrize(
    "change",
    [
        {"roles": "lab_report_revision"},
        {"roles": ["lab_report_revision"] * 17},
        {"study_ids": ["x" * 257]},
        {"expires_at": True},
        {"expires_at": 0},
    ],
)
def test_malformed_or_expired_role_registry_fails_closed(client, laboratory, change):
    mutate_registry("role", laboratory.account, lambda x: x.update(change))
    response = post(client, laboratory)
    assert (
        response.status_code == 403
        and response.json()["code"] == "LAB_REPORT_REVISION_ROLE_REQUIRED"
    )


@pytest.mark.parametrize(
    "methods",
    [
        None,
        {},
        {"M" * 257: {"calibration_ids": [CALIBRATION], "instrument_ids": [INSTRUMENT]}},
        {
            METHOD: {
                "calibration_ids": [CALIBRATION] * 33,
                "instrument_ids": [INSTRUMENT],
            }
        },
        {METHOD: {"calibration_ids": [CALIBRATION], "instrument_ids": []}},
    ],
)
def test_missing_or_malformed_method_mapping_is_not_invented(
    client, laboratory, methods
):
    mutate_registry(
        "configuration", CONFIGURATION, lambda x: x.update(lab_methods=methods)
    )
    response = post(client, laboratory)
    assert (
        response.status_code == 403
        and response.json()["code"] == "REPORT_METHOD_UNAVAILABLE"
    )


def test_expiry_rejects_nonfinite_booleans_and_text():
    assert all(
        not _finite_expiry(value)
        for value in (float("nan"), float("inf"), True, "never", None)
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("method_id", "UNKNOWN"),
        ("calibration_id", "UNKNOWN"),
        ("instrument_id", "UNKNOWN"),
    ],
)
def test_report_analytical_identity_must_match_current_approved_method(
    client, laboratory, field, value
):
    body = body_for(laboratory)
    body["replacement_measurements"][0][field] = value
    assert post(client, laboratory, body).status_code == 403


@pytest.mark.parametrize(
    "fault", ["sample", "collection", "measurement_id", "units", "null_value", "future"]
)
def test_sample_identity_units_nulls_and_future_clock_bounds(client, laboratory, fault):
    body = body_for(laboratory)
    reading = body["replacement_measurements"][0]
    if fault == "sample":
        body["sample_id"] = str(uuid4())
    elif fault == "collection":
        reading["collected_at"] = "2026-10-10T18:00:11Z"
    elif fault == "measurement_id":
        reading["measurement_id"] = laboratory.snapshot["saliva"][0]["measurement_id"]
    elif fault == "units":
        reading["original_report"]["value"] = 6001
    elif fault == "null_value":
        reading["qualifier"] = "below_loq"
    else:
        body["reported_at"] = iso(now() + 61)
    response = post(client, laboratory, body)
    assert response.status_code in (409, 422), response.text


@pytest.mark.parametrize(
    "fault",
    ["foreign_owner", "missing_version", "null_version", "cleanup", "wrong_session"],
)
def test_verified_report_is_owned_version_pinned_and_not_retired(
    client, laboratory, fault
):
    if fault == "foreign_owner":
        owner = client.get("/v1/me/capabilities", headers=headers("b")).json()[
            "account_ref"
        ]
    with factory().begin() as db:
        artifact = db.get(Artifact, laboratory.artifact_id)
        if fault == "foreign_owner":
            artifact.account_id = owner
        elif fault == "missing_version":
            artifact.version_id = None
        elif fault == "null_version":
            artifact.version_id = "null"
        elif fault == "cleanup":
            artifact.state = "cleanup_pending"
        else:
            artifact.session_id = str(uuid4())
    assert post(client, laboratory).status_code in (403, 404, 410)


def test_owner_and_recent_auth_are_required_and_unknown_fields_never_echo(
    client, laboratory
):
    response = post(client, laboratory, auth_time=int(now()) - 301)
    assert (
        response.status_code == 401
        and response.json()["code"] == "REAUTHENTICATION_REQUIRED"
    )
    body = body_for(laboratory)
    response = client.post(
        f"/v1/research/sessions/{laboratory.session_id}/report-revisions",
        headers=headers("b"),
        json=body,
    )
    assert response.status_code in (403, 404)
    body["classification"] = "PRIVATE_UNSUPPORTED_CLASSIFICATION"
    response = post(client, laboratory, body)
    assert (
        response.status_code == 422
        and "PRIVATE_UNSUPPORTED_CLASSIFICATION" not in response.text
    )


def test_uncollected_specimen_is_refused_but_collected_empty_report_accepts_later_analysis(
    client, laboratory
):
    with factory().begin() as db:
        check = db.get(Check, laboratory.session_id)
        snapshot = deepcopy(check.snapshot)
        snapshot["saliva"] = []
        check.snapshot = snapshot
        check.snapshot_sha256 = digest(snapshot)
        check.result = {**check.result, "input_sha256": check.snapshot_sha256}
    body = body_for(laboratory)
    body["base_snapshot_sha256"] = digest(snapshot)
    value = accepted(client, laboratory, body)
    assert len(value["effective_measurements"]) == 1
    with factory().begin() as db:
        check = db.get(Check, laboratory.session_id)
        snapshot = deepcopy(check.snapshot)
        snapshot["sample"].update(
            status="not_collected",
            collected_at=None,
            volume_ml=None,
            dilution_factor=None,
        )
        check.snapshot = snapshot
        check.snapshot_sha256 = digest(snapshot)
        check.result = {**check.result, "input_sha256": check.snapshot_sha256}
    assert post(client, laboratory).status_code == 422


@pytest.mark.parametrize(
    "corruption", ["descriptor", "result", "missing_result", "sequence", "previous"]
)
def test_corrupt_or_incomplete_revision_chain_fails_closed(
    client, laboratory, corruption
):
    value = accepted(client, laboratory)
    with factory().begin() as db:
        a = db.get(Account, laboratory.account)
        row = db.get(Record, rec_id(a, "report_revision", value["revision_id"]))
        result = db.get(
            Record, rec_id(a, "result_revision", value["result"]["result_id"])
        )
        if corruption == "missing_result":
            db.delete(result)
        elif corruption == "sequence":
            row.revision = 2
        elif corruption == "result":
            result.body = {**result.body, "state": "invalid"}
        else:
            data = deepcopy(row.body)
            if corruption == "descriptor":
                data["companion"]["descriptor"]["original_target_at"] = iso()
            else:
                data["companion"]["descriptor"]["previous_revision_id"] = value[
                    "revision_id"
                ]
            row.body = data
            row.sha256 = digest(
                data
            )  # Even a repaired outer storage digest cannot repair lineage.
    response = client.get(
        f"/v1/sessions/{laboratory.session_id}/report-revisions", headers=headers()
    )
    assert (
        response.status_code == 503
        and response.json()["code"] == "REPORT_REVISION_INTEGRITY"
    )


def test_self_consistent_hashes_do_not_admit_a_schema_invalid_original(
    client, laboratory
):
    with factory().begin() as db:
        check = db.get(Check, laboratory.session_id)
        snapshot = deepcopy(check.snapshot)
        snapshot["cardiac"]["modality"] = (
            "simulated"  # Contradicts prototype_sensor source.
        )
        check.snapshot, check.snapshot_sha256 = snapshot, digest(snapshot)
        check.result = {**check.result, "input_sha256": check.snapshot_sha256}
    response = post(client, laboratory)
    assert (
        response.status_code == 503
        and response.json()["code"] == "REPORT_REVISION_INTEGRITY"
    )
    with factory()() as db:
        assert (
            list(db.scalars(select(Record).where(Record.kind == "report_revision")))
            == []
        )


def test_revision_count_and_per_record_bounds_refuse_without_truncating(
    client, laboratory
):
    value = None
    for _ in range(20):
        with factory().begin() as db:
            db.execute(
                delete(RateBucket).where(RateBucket.id == laboratory.account + ":write")
            )
        value = accepted(client, laboratory, body_for(laboratory, value))
    response = post(client, laboratory, body_for(laboratory, value))
    assert (
        response.status_code == 413
        and response.json()["code"] == "REPORT_REVISION_LIMIT"
    )


def test_large_structured_revision_is_rejected_before_persisting_result(
    client, laboratory
):
    body = body_for(laboratory)
    body["replacement_measurements"][0]["quality_flags"] = ["F" * 200] * 1400
    response = post(client, laboratory, body)
    assert (
        response.status_code == 413
        and response.json()["code"] == "REPORT_REVISION_LIMIT"
    )
    with factory()() as db:
        assert (
            list(db.scalars(select(Record).where(Record.kind == "report_revision")))
            == []
        )


def test_saliva_free_finalized_check_lists_no_revisions_and_preserves_null_collection(
    client, laboratory
):
    with factory().begin() as db:
        check = db.get(Check, laboratory.session_id)
        snapshot = deepcopy(check.snapshot)
        snapshot["sample"].update(
            status="not_collected",
            collected_at=None,
            volume_ml=None,
            dilution_factor=None,
        )
        snapshot["saliva"] = []
        check.snapshot, check.snapshot_sha256 = snapshot, digest(snapshot)
        check.result = {**check.result, "input_sha256": check.snapshot_sha256}
    response = client.get(
        f"/v1/sessions/{laboratory.session_id}/report-revisions", headers=headers()
    )
    assert response.status_code == 200, response.text
    assert response.json()["original_collected_at"] is None
    assert (
        response.json()["latest_revision_id"] is None and response.json()["items"] == []
    )


def test_over_capacity_corrupted_store_is_rejected_by_bounded_chain_inventory(
    client, laboratory
):
    with factory().begin() as db:
        account = db.get(Account, laboratory.account)
        for index in range(41):
            save_record(
                db,
                account,
                "report_revision",
                str(uuid4()),
                {"invalid_fixture": True},
                laboratory.session_id,
                index + 1,
            )
    response = client.get(
        f"/v1/sessions/{laboratory.session_id}/report-revisions", headers=headers()
    )
    assert (
        response.status_code == 503
        and response.json()["code"] == "REPORT_REVISION_INTEGRITY"
    )


def quota_artifact(db, lab, size, state="verified"):
    artifact_id = str(uuid4())
    row = Artifact(
        id=artifact_id,
        account_id=lab.account,
        generation=1,
        session_id=lab.session_id,
        bucket=settings().artifact_bucket,
        key=f"quarantine/{lab.account}/1/{artifact_id}",
        version_id="FICTIONAL_VERSION",
        sha256="a" * 64,
        size=size,
        media_type="video/mp4",
        kind="eye_video",
        state=state,
        expires=now() - 400,
        scope={},
    )
    db.add(row)
    return row


def test_quota_exact_byte_boundary_and_purged_cleanup_release(client, laboratory):
    with factory().begin() as db:
        db.get(Artifact, laboratory.artifact_id).state = "purged"
        for _ in range(15):
            quota_artifact(db, laboratory, 64 * 1024 * 1024)
        last = quota_artifact(db, laboratory, 56 * 1024 * 1024)
        db.flush()
        assert ensure_artifact_capacity(db, laboratory.account, 8 * 1024 * 1024) is None
        with pytest.raises(Problem) as caught:
            ensure_artifact_capacity(db, laboratory.account, 8 * 1024 * 1024 + 1)
        assert caught.value.code == "LIMIT_EXCEEDED"
        last.state = "cleanup_pending"
        db.flush()
        with pytest.raises(Problem):
            ensure_artifact_capacity(db, laboratory.account, 8 * 1024 * 1024 + 1)
        last.state = "purged"
        db.flush()
        assert (
            ensure_artifact_capacity(db, laboratory.account, 64 * 1024 * 1024) is None
        )


def test_pending_quota_counts_cleanup_claims_and_releases_only_after_purge(
    client, laboratory
):
    with factory().begin() as db:
        rows = [
            quota_artifact(db, laboratory, 1, state)
            for state in ("quarantine", "cleanup_pending", "quarantine")
        ]
        db.flush()
        with pytest.raises(Problem):
            ensure_artifact_capacity(db, laboratory.account, 1)
        rows[1].state = "purged"
        db.flush()
        assert ensure_artifact_capacity(db, laboratory.account, 1) is None


def test_pending_byte_bound_is_inclusive_and_never_ignores_cleanup_pending(
    client, laboratory
):
    with factory().begin() as db:
        quota_artifact(db, laboratory, 64 * 1024 * 1024, "cleanup_pending")
        quota_artifact(db, laboratory, 56 * 1024 * 1024, "quarantine")
        db.flush()
        assert ensure_artifact_capacity(db, laboratory.account, 8 * 1024 * 1024) is None
        with pytest.raises(Problem):
            ensure_artifact_capacity(db, laboratory.account, 8 * 1024 * 1024 + 1)


def completion_body(lab):
    with factory()() as db:
        row = db.get(Artifact, lab.artifact_id)
        return {
            "sha256": row.sha256,
            "size_bytes": row.size,
            "media_type": row.media_type,
        }


def completion_path(lab):
    return f"/v1/research/sessions/{lab.session_id}/report-artifact-uploads/{lab.artifact_id}/complete"


def test_report_completion_and_generic_capture_purpose_are_separate(
    client, laboratory, monkeypatch
):
    body = completion_body(laboratory)
    monkeypatch.setattr(
        storage,
        "verify_artifact",
        lambda _: pytest.fail("Verified replay must not read a new current version"),
    )
    assert (
        client.post(
            completion_path(laboratory),
            headers=headers(key="complete-report"),
            json=body,
        ).status_code
        == 200
    )
    assert (
        client.post(
            completion_path(laboratory),
            headers=headers(key="complete-report"),
            json=body,
        ).status_code
        == 200
    )
    generic = client.post(
        f"/v1/artifact-uploads/{laboratory.artifact_id}/complete",
        headers=headers(),
        json=body,
    )
    assert (
        generic.status_code == 403
        and generic.json()["code"] == "ARTIFACT_PURPOSE_MISMATCH"
    )
    mutate_registry("role", laboratory.account, lambda x: x.update(roles=[]))
    assert (
        client.post(
            completion_path(laboratory),
            headers=headers(key="complete-report"),
            json=body,
        ).status_code
        == 403
    )


def test_fresh_report_completion_verifies_pdf_bytes_and_pins_the_exact_version(
    client, laboratory, monkeypatch
):
    with factory().begin() as db:
        row = db.get(Artifact, laboratory.artifact_id)
        row.state, row.version_id = "quarantine", None
    body = completion_body(laboratory)
    seen = []

    def head_object(**args):
        seen.append(args)
        return {
            "VersionId": laboratory.source_version,
            "ContentType": "application/pdf",
        }

    monkeypatch.setattr(laboratory.store, "head_object", head_object, raising=False)
    response = client.post(completion_path(laboratory), headers=headers(), json=body)
    assert response.status_code == 200, response.text
    assert response.json()["version_id"] == laboratory.source_version and len(seen) == 1
    with factory()() as db:
        row = db.get(Artifact, laboratory.artifact_id)
        assert row.state == "verified" and row.version_id == laboratory.source_version


@pytest.mark.parametrize(
    "race", ["role", "consent", "generation", "cleanup", "immutable"]
)
def test_completion_reauthorizes_after_external_storage_and_cannot_resurrect_cleanup(
    client, laboratory, monkeypatch, race
):
    with factory().begin() as db:
        row = db.get(Artifact, laboratory.artifact_id)
        row.state, row.version_id = "quarantine", None
    body = completion_body(laboratory)

    def verify(_):
        with factory().begin() as db:
            if race == "role":
                db.get(Registry, "role:" + laboratory.account).active = False
            elif race == "consent":
                row = db.get(Record, laboratory.account + ":consent:" + STUDY)
                row.body = {**row.body, "state": "withdrawn"}
            elif race == "generation":
                db.get(Account, laboratory.account).generation = 2
            elif race == "cleanup":
                db.get(Artifact, laboratory.artifact_id).state = "cleanup_pending"
            else:
                db.get(Artifact, laboratory.artifact_id).key += "/changed"
        return laboratory.source_version

    monkeypatch.setattr(storage, "verify_artifact", verify)
    response = client.post(completion_path(laboratory), headers=headers(), json=body)
    assert response.status_code in (403, 409, 410), response.text
    with factory()() as db:
        assert db.get(Artifact, laboratory.artifact_id).state != "verified"


def test_ticket_pins_administrative_purpose_and_rejects_quota_and_wrong_media(
    client, laboratory, monkeypatch
):
    def ticket(row):
        return {
            "artifact_id": row.id,
            "method": "PUT",
            "upload_url": "http://fictional.invalid/upload",
            "required_headers": {"If-None-Match": "*"},
            "expires_in_seconds": 300,
        }

    monkeypatch.setattr(storage, "upload_ticket", ticket)
    body = {
        **completion_body(laboratory),
        "study_id": STUDY,
        "session_id": laboratory.session_id,
        "consent_record_id": laboratory.consent_id,
        "retention_policy_id": RETENTION,
        "artifact_kind": "source_lab_report",
    }
    path = f"/v1/research/sessions/{laboratory.session_id}/report-artifact-uploads"
    for index in range(3):
        response = client.post(path, headers=headers(key=f"ticket-{index}"), json=body)
        assert response.status_code == 201, response.text
        with factory()() as db:
            row = db.get(Artifact, response.json()["artifact_id"])
            assert row.scope["purpose"] == PURPOSE and 295 < row.expires - now() <= 300
    assert client.post(path, headers=headers(), json=body).status_code == 429
    assert (
        client.post(path, headers=headers(key="ticket-0"), json=body).status_code == 201
    )
    assert (
        client.post(
            path, headers=headers(), json={**body, "media_type": "video/mp4"}
        ).status_code
        == 403
    )


def test_export_freezes_report_head_and_uses_separate_bounded_hash_indexed_files(
    client, laboratory
):
    first = accepted(client, laboratory)
    exported = client.post(
        "/v1/privacy/exports",
        headers=headers(),
        json={
            "selection": {"kind": "single", "session_ids": [laboratory.session_id]},
            "format": "json_zip",
            "include_raw": False,
        },
    )
    assert exported.status_code == 202, exported.text
    second = accepted(client, laboratory, body_for(laboratory, first))
    job_id = exported.json()["job_id"]
    assert run_job(job_id) == "completed"
    download = client.get(f"/v1/privacy/jobs/{job_id}/download", headers=headers())
    assert download.status_code == 200, download.text
    with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
        report_paths = [
            x for x in archive.namelist() if x.startswith("report-revisions/")
        ]
        assert report_paths == [
            f"report-revisions/{laboratory.session_id}/{first['revision_id']}.json"
        ]
        assert all(second["revision_id"] not in path for path in archive.namelist())
        check = strict_loads(archive.read(f"checks/{laboratory.session_id}.json"))
        index = check["report_revision_index"]
        assert len(canonical(index)) <= 16 * 1024 and len(index["items"]) == 1
        item = index["items"][0]
        raw = archive.read(item["path"])
        assert len(raw) == item["size_bytes"] <= 512 * 1024
        assert digest(strict_loads(raw)) == item["sha256"]
        assert strict_loads(raw) == first
        assert check["snapshot"] == laboratory.snapshot
        assert not any(x.endswith(".pdf") for x in archive.namelist())
        manifest = strict_loads(archive.read("manifest.json"))
        assert (
            next(x for x in manifest["files"] if x["path"] == item["path"])["sha256"]
            == item["sha256"]
        )


def test_legacy_empty_export_head_does_not_pick_up_new_reports(client, laboratory):
    accepted(client, laboratory)
    with factory()() as db:
        account = db.get(Account, laboratory.account)
        check = db.get(Check, laboratory.session_id)
        index, files = export_records(
            db, account, check, {"revision_id": None, "revision_sha256": None}
        )
        assert index["items"] == [] and files == {}


def test_archive_budget_includes_manifest_bytes_without_a_manifest_record_cap():
    size = 512 * 1024
    empty = canonical({"fictional_padding": ""})
    block = canonical({"fictional_padding": "X" * (size - len(empty))})
    assert len(block) == size
    paths = [f"checks/{uuid4()}.json" for _ in range(100)]
    files = {path: block for path in paths[:99]}
    manifest = {
        "schema_version": "1.0.0",
        "files": [
            {
                "path": path,
                "sha256": __import__("hashlib").sha256(block).hexdigest(),
                "size_bytes": size,
            }
            for path in files
        ],
    }
    assert len(export_manifest_bytes(files, manifest)) > 0
    files[paths[99]] = block  # Records alone now occupy exactly 50 MiB.
    manifest["files"].append(
        {"path": paths[99], "sha256": digest({}), "size_bytes": size}
    )
    with pytest.raises(Problem) as caught:
        export_manifest_bytes(files, manifest)
    assert caught.value.code == "EXPORT_TOO_LARGE"
    large_metadata = {"fixture_metadata": "X" * (512 * 1024 + 1)}
    assert len(export_manifest_bytes({}, large_metadata)) > 512 * 1024


def test_combined_check_record_over_512k_refuses_whole_export_before_object_write(
    client, laboratory
):
    with factory().begin() as db:
        check = db.get(Check, laboratory.session_id)
        snapshot = deepcopy(check.snapshot)
        snapshot["eyes"]["quality_flags"] = ["FICTIONAL_" + "X" * 190] * 1400
        check.snapshot, check.snapshot_sha256 = snapshot, digest(snapshot)
        check.result = {**check.result, "input_sha256": check.snapshot_sha256}
        manifest = db.get(
            Record, laboratory.account + ":manifest:" + laboratory.session_id
        )
        manifest_body = deepcopy(manifest.body)
        for row in db.scalars(
            select(Record).where(
                Record.parent_id == laboratory.session_id, Record.kind == "attempt"
            )
        ):
            if row.body["component"] == "eyes":
                attempt = deepcopy(row.body)
                attempt["component_metadata"]["projection"] = snapshot["eyes"]
                row.body, row.sha256 = attempt, digest(attempt)
                assert len(canonical(attempt)) < 512 * 1024
                for ref in manifest_body["attempts"]:
                    if ref["attempt_id"] == attempt["attempt_id"]:
                        ref["sha256"] = row.sha256
        manifest.body, manifest.sha256 = manifest_body, digest(manifest_body)
        check.evidence_sha256 = manifest.sha256
        assert len(canonical(snapshot)) < 512 * 1024
    response = client.post(
        "/v1/privacy/exports",
        headers=headers(),
        json={
            "selection": {"kind": "single", "session_ids": [laboratory.session_id]},
            "format": "json_zip",
            "include_raw": False,
        },
    )
    assert response.status_code == 202, response.text
    assert run_job(response.json()["job_id"]) == "failed"
    assert not any(
        key.startswith("exports/") for _, key, _ in laboratory.store.objects.values()
    )


def test_profile_history_file_over_512k_refuses_whole_export(client, laboratory):
    with factory().begin() as db:
        account = db.get(Account, laboratory.account)
        for _ in range(1200):
            ident = str(uuid4())
            save_record(
                db,
                account,
                "profile_version",
                ident,
                {
                    "profile_version_id": ident,
                    "profile": laboratory.snapshot["profile"],
                    "history": laboratory.snapshot["history"],
                    "context": {
                        "last_use_status": "unknown",
                        "last_use_at": None,
                        "confirmed_at": laboratory.snapshot["target_at"],
                    },
                },
            )
    response = client.post(
        "/v1/privacy/exports",
        headers=headers(),
        json={
            "selection": {"kind": "all", "session_ids": []},
            "format": "json_zip",
            "include_raw": False,
        },
    )
    assert response.status_code == 202, response.text
    assert run_job(response.json()["job_id"]) == "failed"
    assert not any(
        key.startswith("exports/") for _, key, _ in laboratory.store.objects.values()
    )


def test_deletion_retires_revisions_and_scrubs_both_record_kinds(client, laboratory):
    first = accepted(client, laboratory)
    body = body_for(laboratory, first)
    response = client.post(
        "/v1/privacy/deletion-requests",
        headers=headers(),
        json={"scope": "all_data", "confirmation": True},
    )
    assert response.status_code == 202, response.text
    assert post(client, laboratory, body).status_code in (403, 410)
    assert client.get(
        f"/v1/sessions/{laboratory.session_id}/report-revisions", headers=headers()
    ).status_code in (403, 404)
    assert run_job(response.json()["job_id"]) == "completed"
    with factory()() as db:
        assert (
            list(
                db.scalars(
                    select(Record).where(
                        Record.account_id == laboratory.account,
                        Record.kind.in_(["report_revision", "result_revision"]),
                    )
                )
            )
            == []
        )


def test_actual_postgresql_concurrent_revisions_cannot_branch(client, laboratory):
    from otgd.db import engine

    if engine().dialect.name != "postgresql":
        pytest.skip(
            "Requires actual PostgreSQL row locks; SQLite is not concurrency evidence"
        )
    from concurrent.futures import ThreadPoolExecutor

    left, right = body_for(laboratory), body_for(laboratory)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda body: post(client, laboratory, body).status_code, [left, right]
            )
        )
    assert sorted(results) == [201, 409]
    with factory()() as db:
        assert (
            len(
                load_chain(
                    db,
                    db.get(Account, laboratory.account),
                    db.get(Check, laboratory.session_id),
                )
            )
            == 1
        )
