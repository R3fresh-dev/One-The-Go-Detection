"""Actual typed lifecycle and HTTP worker admission with fictional evidence.

The captured timing fixture and its operator reviews are engineered test data;
the S3 byte response is a unit transport fixture, not hardware/scientific proof.
"""

from copy import deepcopy
from datetime import datetime
import json

import pytest

from otgd import model_engine as m
from otgd.canonical import canonical, digest
from otgd.config import ROOT, settings
from otgd.db import Account, Check, SystemState, factory, iso, now
from otgd.domain import record
from otgd.errors import Problem
from otgd.operator_governance import transition

from .conftest import headers
from .governance_fixture import (
    approve,
    common,
    configuration,
    proof,
    retention,
    study,
    STUDY,
    PROTOCOL,
)
from . import test_model_engine

model = test_model_engine.model


def shift_times(value, delta):
    if isinstance(value, dict):
        return {k: shift_times(v, delta) for k, v in value.items()}
    if isinstance(value, list):
        return [shift_times(v, delta) for v in value]
    if isinstance(value, str) and value.endswith("Z") and "T" in value:
        try:
            return iso((datetime.fromisoformat(value) + delta).timestamp())
        except ValueError:
            pass
    return value


@pytest.fixture
def admitted(client, account, model, monkeypatch, request):
    bundle = json.loads(
        (ROOT / "apps/mobile/testfixtures/native-check-contract.json").read_text()
    )
    delta = datetime.fromisoformat(iso(now() - 30)) - datetime.fromisoformat(
        bundle["snapshot"]["capture_completed_at"]
    )
    bundle = shift_times(bundle, delta)
    snapshot = bundle["snapshot"]
    snapshot.update(
        subject_ref=account,
        mode="controlled_research",
        study_id=STUDY,
        protocol_id=PROTOCOL,
        clock_uncertainty_ms=2.0,
    )
    snapshot["profile"].update(age_years=30, recorded_at=snapshot["created_at"])
    snapshot["history"]["alcohol_co_use"] = "not_reported"
    attempt = bundle["attempts"][0]
    attempt["component_metadata"].pop("contract_fixture", None)
    native = attempt["component_metadata"]["native_result"]
    native["timing"]["simulator"] = False
    config = configuration(supported_phone_models=[native["timing"]["deviceModel"]])
    qualification = proof(config_body=config)
    qualification["purpose"] = "qualified_measurement"
    body = deepcopy(model["body"])
    manifest = body["manifest"]
    manifest.update(
        required_channels=["task"],
        allowed_protocol_ids=[PROTOCOL],
        allowed_hardware_revisions=[snapshot["device"]["hardware_revision"]],
    )
    body["study_ids"] = [STUDY]
    artifact = model["artifact"].model_copy(
        update={
            "feature_names": ["task.features.median_rt_ms"],
            "means": [300.0],
            "scales": [100.0],
            "coefficients": [1.0],
            "feature_limits": {"task.features.median_rt_ms": [0.0, 2000.0]},
        }
    )
    raw = canonical(artifact.model_dump())
    manifest["artifact_sha256"] = digest(artifact.model_dump())
    body["artifact_ref"].update(
        bucket=settings().artifact_bucket,
        sha256=manifest["artifact_sha256"],
        size_bytes=len(raw),
    )
    body["evaluation_report"]["artifact_sha256"] = manifest["artifact_sha256"]
    timing_id = "fictional-qualified-phone-timing"
    body = common(manifest["model_id"], **body, native_timing_calibration_id=timing_id)
    doc = study(account)
    doc["model_id"] = manifest["model_id"]
    timing = native["timing"]
    timing_body = common(
        timing_id,
        calibration_id=timing_id,
        purpose="native_timing",
        calibration_sha256="9" * 64,
        native_timing={
            "phone_models": [timing["deviceModel"]],
            "os_versions": [timing["osVersion"]],
            "native_builds": [timing["nativeBuild"]],
            "implementation_version": native["implementationVersion"],
            "extractor_version": native["extractorVersion"],
            "input_timestamp_method": timing["inputTimestampMethod"],
            "presentation_evidence_method": timing["presentationEvidenceMethod"],
            "clock_domain": timing["clockDomain"],
            "bias_ms": 2.0,
            "max_uncertainty_ms": 2.0,
            "qualifying_trial_count": 100,
        },
    )
    optical = getattr(request, "param", None) == "optical"
    extra_approvals = []
    if optical:
        from .test_optical_evidence import fixture as optical_fixture
        from otgd.operator_governance import Configuration, OpticalGeometryScope

        native, projection, optical_config = optical_fixture(scale=True)
        material = optical_config["material"]
        geometry = OpticalGeometryScope.model_validate(
            {
                **{
                    key: material[key]
                    for key in (
                        "camera_id",
                        "lens_facing",
                        "capture_width",
                        "capture_height",
                        "expected_output_rotation_degrees",
                        "roi",
                        "roi_sample_width",
                        "roi_sample_height",
                        "extractor_version",
                    )
                },
                **{
                    key: material["geometry_scale"][key]
                    for key in (
                        "pixels_to_mm",
                        "min_diameter_pixels",
                        "max_diameter_pixels",
                        "max_uncertainty_mm",
                    )
                },
                "phone_models": [native["camera"]["phone_model"]],
                "os_versions": [native["camera"]["os_version"]],
                "native_builds": [native["camera"]["native_build"]],
                "pixel_basis": "roi_sample_pixels",
            }
        ).data()
        material["geometry_scale"]["calibration_sha256"] = digest(geometry)
        config = Configuration.model_validate(
            configuration(
                "eyes",
                material=material,
                sha256=digest(material),
                software_adapter_id="optical_roi_v1",
                max_duration_ms=material["duration_ms"],
                supported_phone_models=geometry["phone_models"],
                supported_os_versions=geometry["os_versions"],
                supported_native_builds=geometry["native_builds"],
                optical_safety_ref="FICTIONAL-OPTICAL-SAFETY-NO-HUMAN-APPROVAL",
            )
        ).data()
        qualification = proof("eyes", config_body=config)
        qualification["purpose"] = "qualified_measurement"
        geometry_id = material["geometry_scale"]["calibration_id"]
        extra_approvals = [
            (
                "calibration",
                common(
                    geometry_id,
                    calibration_id=geometry_id,
                    purpose="optical_geometry",
                    optical_geometry=geometry,
                    calibration_sha256=digest(geometry),
                ),
            )
        ]
        end = datetime.fromisoformat(snapshot["capture_completed_at"]).timestamp()
        native.update(
            started_at=iso(end - 1),
            ended_at=iso(end),
            configuration_sha256=config["sha256"],
            run_id=attempt["record_id"],
        )
        projection.update(
            started_at=native["started_at"],
            ended_at=native["ended_at"],
            capture_config_id=config["configuration_id"],
        )
        snapshot["eyes"] = projection
        snapshot["task"] = {
            **snapshot["task"],
            "status": "not_collected",
            "started_at": None,
            "ended_at": None,
            "quality_flags": [],
            "practice_trials": 0,
            "scored_trials": 0,
            "go_trials": 0,
            "no_go_trials": 0,
            "valid_correct_go_trials": 0,
            "features": {key: None for key in snapshot["task"]["features"]},
        }
        snapshot["acquisition_span_ms"] = 1000
        attempt.update(
            component="eyes",
            source="prototype_sensor",
            started_at=native["started_at"],
            ended_at=native["ended_at"],
            configuration_hash=config["sha256"],
            quality_flags=projection["quality_flags"],
            component_metadata={"native_result": native, "projection": projection},
        )
        doc["channels"] = {"eyes": config["configuration_id"]}
        manifest["required_channels"] = ["pupil"]
        artifact = artifact.model_copy(
            update={
                "feature_names": ["eyes.baseline_diameter_mm"],
                "coefficients": [1.0],
                "means": [0.4],
                "scales": [1.0],
                "feature_limits": {"eyes.baseline_diameter_mm": [0.0, 10.0]},
            }
        )
        raw = canonical(artifact.model_dump())
        manifest["artifact_sha256"] = digest(artifact.model_dump())
        body["artifact_ref"].update(
            sha256=manifest["artifact_sha256"], size_bytes=len(raw)
        )
        body["evaluation_report"]["artifact_sha256"] = manifest["artifact_sha256"]
    with factory().begin() as db:
        for kind, value in [
            ("study", doc),
            ("retention", retention()),
            *extra_approvals,
            ("qualification", qualification),
            ("configuration", config),
            (
                "calibration",
                common(
                    manifest["calibration_id"],
                    calibration_id=manifest["calibration_id"],
                    purpose="model",
                    model_id=manifest["model_id"],
                    calibration_sha256=digest(artifact.calibration.model_dump()),
                ),
            ),
            ("calibration", timing_body),
            ("model", body),
        ]:
            approve(db, kind, value)
    response = client.post(
        f"/v1/studies/{STUDY}/consents",
        headers=headers(),
        json={
            **{
                k: doc[k]
                for k in ("invitation_id", "document_version", "document_sha256")
            },
            "accepted": True,
            "acknowledged_at": iso(),
        },
    )
    assert response.status_code == 201, response.text
    context = bundle["context"]
    context.update(
        protocol_id=PROTOCOL,
        profile_snapshot_sha256=digest(snapshot["profile"]),
        history_snapshot_sha256=digest(snapshot["history"]),
    )
    context["configuration_refs"][0].update(
        id=config["configuration_id"],
        version=config["version"],
        sha256=config["sha256"],
    )
    attempt["configuration_id"] = config["configuration_id"]
    evidence = bundle["manifest"]
    evidence["context_sha256"] = digest(context)
    evidence["attempts"][0]["sha256"] = digest(attempt)
    if optical:
        evidence["selected"]["task"] = None
        evidence["selected"]["eyes"] = attempt["attempt_id"]
    sid = snapshot["session_id"]

    def send(method, path, body, revision=None):
        result = client.request(
            method, path, headers=headers(revision=revision), json=body
        )
        assert result.status_code in (200, 201, 202), (
            path,
            result.status_code,
            result.text,
        )
        return result

    send(
        "POST",
        "/v1/sessions",
        {
            k: snapshot[k]
            for k in (
                "session_id",
                "mode",
                "protocol_id",
                "study_id",
                "supersedes_session_id",
            )
        },
    )
    send("PUT", f"/v1/sessions/{sid}/context", context, 0)
    started = {
        **attempt,
        "status": "started",
        "ended_at": None,
        "quality_flags": [],
        "component_metadata": {},
    }
    send("PUT", f"/v1/sessions/{sid}/attempts/{attempt['attempt_id']}", started, 0)
    # The host ledger represents a completed 112-second fictional native run.
    # Reproduce its server start time explicitly without a simulator bypass.
    with monkeypatch.context() as clock:
        clock.setattr(
            "otgd.main.now",
            lambda: datetime.fromisoformat(attempt["started_at"]).timestamp(),
        )
        grant = send(
            "POST",
            f"/v1/sessions/{sid}/capture-authorizations",
            {
                "attempt_id": attempt["attempt_id"],
                "channel": "eyes" if optical else "task",
                "binding_id": None,
                "device_id": None,
                "configuration_id": config["configuration_id"],
                "configuration_hash": config["sha256"],
            },
        ).json()
        send(
            "POST",
            f"/v1/sessions/{sid}/capture-authorizations/{grant['authorization_id']}/start",
            {
                "attempt_id": attempt["attempt_id"],
                "device_boot_id": native["run_id"]
                if optical
                else "fictional-phone-run",
            },
        )
    if optical:
        native["authorization_id"] = grant["authorization_id"]
        evidence["attempts"][0]["sha256"] = digest(attempt)
    send("PUT", f"/v1/sessions/{sid}/attempts/{attempt['attempt_id']}", attempt, 1)
    send("PUT", f"/v1/sessions/{sid}/snapshot", snapshot, 1)
    send("PUT", f"/v1/sessions/{sid}/evidence-manifest", evidence, 0)
    receipt = send(
        "POST",
        f"/v1/sessions/{sid}/finalize",
        {"snapshot_sha256": digest(snapshot), "evidence_sha256": digest(evidence)},
        2,
    ).json()
    monkeypatch.setattr(
        "otgd.storage.versioned_read", lambda bucket, key, version, limit: raw
    )
    return {
        "account": account,
        "sid": sid,
        "job": receipt["job_id"],
        "model_id": manifest["model_id"],
        "timing_id": timing_id,
        "raw": raw,
        "optical_geometry_id": geometry_id if optical else None,
    }


def resolved(value):
    db = factory()()
    account = db.get(Account, value["account"])
    check = db.get(Check, value["sid"])
    return db, account, check


def test_http_native_evidence_real_registry_lifecycle_worker_and_research_read(
    client, admitted
):
    from otgd.worker import run_job

    db, account, check = resolved(admitted)
    with db:
        authority = m.execution_authority(db, account, check)
        m.scope_check(check.snapshot, authority["body"], authority["timing_qualified"])
    assert run_job(admitted["job"]) == "completed"
    response = client.get(f"/v1/sessions/{admitted['sid']}", headers=headers())
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    assert (
        result["schema_version"] == "1.1.0" and result["state"] == "research_estimate"
    )
    assert result["model_execution"]["authority_manifest"][
        "native_timing_calibration_sha256"
    ]
    assert m.validate_result(result) == result
    capabilities = client.get("/v1/me/capabilities", headers=headers()).json()
    assert capabilities["model_execution_supported"] is True
    assert capabilities["inference_available"] is True


@pytest.mark.parametrize("admitted", ["optical"], indirect=True)
def test_http_optical_geometry_real_lifecycle_worker_and_read(client, admitted):
    from otgd.worker import run_job

    db, owner, check = resolved(admitted)
    with db:
        authority = m.execution_authority(db, owner, check)
        assert authority["optical_qualified"] is True
        assert check.snapshot["eyes"]["latency_ms"] is None
        assert "PHYSICAL_ONSET_UNMEASURED" in check.snapshot["eyes"]["quality_flags"]
    assert run_job(admitted["job"]) == "completed"
    response = client.get(f"/v1/sessions/{admitted['sid']}", headers=headers())
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    assert (
        result["schema_version"] == "1.1.0" and result["state"] == "research_estimate"
    )
    assert m.validate_result(result) == result


@pytest.mark.parametrize("admitted", ["optical"], indirect=True)
def test_optical_geometry_retirement_between_compute_and_commit_refuses_result(
    admitted,
):
    db, owner, check = resolved(admitted)
    with db:
        output = m.result_for_check(db, owner, check)
        assert output["state"] == "research_estimate"
    with factory().begin() as db:
        transition(
            db,
            "calibration",
            admitted["optical_geometry_id"],
            "v1",
            "retire",
            "local:fixture-releaser",
            "Fictional geometry withdrawn",
            3,
        )
    db, owner, check = resolved(admitted)
    with db, pytest.raises(Problem):
        m.verify_current_execution(db, owner, check, output)


@pytest.mark.parametrize(
    "change",
    [
        "notice",
        "generation",
        "consent",
        "recovery",
        "simulator",
        "os",
        "qualification",
        "calibration",
        "artifact",
        "training_time",
    ],
)
def test_current_authority_or_bytes_refusal_returns_no_score(
    client, admitted, change, monkeypatch
):
    if change in ("artifact", "training_time"):
        if change == "artifact":
            monkeypatch.setattr("otgd.storage.versioned_read", lambda *_: b"changed")
        else:
            monkeypatch.setattr(
                m,
                "load_artifact",
                lambda *args: m.Artifact.model_validate(
                    {**json.loads(admitted["raw"]), "trained_at": iso()}
                ),
            )
    with factory().begin() as db:
        account = db.get(Account, admitted["account"])
        check = db.get(Check, admitted["sid"])
        if change == "notice":
            account.notice = "changed"
        elif change == "generation":
            check.generation += 1
        elif change == "consent":
            row = record(db, account, "consent", STUDY)
            row.body = {**row.body, "state": "withdrawn"}
        elif change == "recovery":
            db.add(SystemState(key="recovery", body={"scopes_suspended": True}))
        elif change in ("simulator", "os"):
            evidence = record(db, account, "manifest", check.id)
            row = record(db, account, "attempt", evidence.body["selected"]["task"])
            body = deepcopy(row.body)
            body["component_metadata"]["native_result"]["timing"][
                "simulator" if change == "simulator" else "osVersion"
            ] = True if change == "simulator" else "foreign"
            row.body = body
            row.sha256 = digest(body)
            doc = deepcopy(evidence.body)
            doc["attempts"][0]["sha256"] = row.sha256
            evidence.body = doc
            evidence.sha256 = digest(doc)
        elif change in ("qualification", "calibration"):
            kind, id = (
                ("calibration", admitted["timing_id"])
                if change == "calibration"
                else ("qualification", "fictional-governance-qualification-task")
            )
            transition(
                db,
                kind,
                id,
                "v1",
                "revoke",
                "local:fixture-reviewer",
                "Fictional revocation regression",
                3,
            )
    db, account, check = resolved(admitted)
    with db:
        result = m.result_for_check(db, account, check)
        assert result["schema_version"] == "0.1.0" and result["state"] == "inconclusive"
        assert result["probability"] is None and result["model_id"] is None


def test_model_retirement_and_consent_change_between_compute_and_commit(
    client, admitted
):
    from otgd.worker import claim_job, execute_claim, commit_output

    claim = claim_job(admitted["job"])
    output = execute_claim(claim)
    assert output["schema_version"] == "1.1.0"
    with factory().begin() as db:
        transition(
            db,
            "model",
            admitted["model_id"],
            "v1",
            "revoke",
            "local:fixture-reviewer",
            "Fictional study stopped",
            3,
        )
    with pytest.raises(Problem):
        commit_output(claim, output)
    with factory()() as db:
        assert db.get(Check, admitted["sid"]).result is None


def test_baseline_bounds_and_bias_are_applied_to_frozen_features(model):
    body = model["body"]
    body["manifest"]["baseline_mode"] = "personalized"
    with pytest.raises(ValueError, match="baseline age"):
        m.validate_registry_model(body)
    body["quality_policy"]["max_baseline_age_ms"] = 1000
    baseline = deepcopy(model["snapshot"])
    baseline.update(
        created_at=iso(now() - 1000),
        target_at=iso(now() - 1000),
        capture_completed_at=iso(now() - 880),
    )
    baseline["profile"]["recorded_at"] = iso(now() - 1100)
    baseline["sample"]["collected_at"] = iso(now() - 990)
    for component in ("eyes", "cardiac", "task"):
        baseline[component].update(
            started_at=iso(now() - 1000), ended_at=iso(now() - 880)
        )
    for row in baseline["saliva"]:
        row.update(
            collected_at=baseline["sample"]["collected_at"],
            measured_at=iso(now() - 900)
            if row["qualifier"] != "not_measured"
            else None,
        )
    with pytest.raises(Problem) as error:
        m.execute(
            model["snapshot"],
            body,
            model["artifact"],
            model["proof"],
            baseline=baseline,
            timing_qualified=True,
        )
    assert error.value.code == "BASELINE_NOT_COMPATIBLE"
    body["manifest"]["baseline_mode"] = "population"
    body["quality_policy"]["max_baseline_age_ms"] = None
    output = m.execute(
        model["snapshot"],
        body,
        model["artifact"],
        model["proof"],
        timing_qualified=True,
        timing_bias_ms=2.0,
    )
    expected = m.feature_values(model["snapshot"], model["artifact"])
    expected[0] -= 2.0
    assert output["model_execution"]["feature_values_sha256"] == digest(expected)
