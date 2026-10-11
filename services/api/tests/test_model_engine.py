"""Fictional engineered data tests execution gates; no trained human model."""

from copy import deepcopy
import json

import pytest

from otgd import model_engine as m
from otgd.canonical import canonical, digest
from otgd.config import ROOT
from otgd.db import iso, now
from otgd.errors import Problem


@pytest.fixture
def model():
    current = now()
    snapshot = json.loads((ROOT / "examples/synthetic_session.json").read_text())
    snapshot.update(
        mode="controlled_research",
        study_id="engineering-study",
        protocol_id="engineering-protocol",
        created_at=iso(current - 180),
        target_at=iso(current - 180),
        capture_completed_at=iso(current - 60),
        clock_uncertainty_ms=2,
        acquisition_span_ms=120000,
    )
    snapshot["device"]["hardware_revision"] = "engineering-hw"
    snapshot["profile"].update(
        source="study_measurement", recorded_at=iso(current - 200), age_years=30
    )
    snapshot["history"]["alcohol_co_use"] = "not_reported"
    for field in ("eyes", "cardiac", "task"):
        snapshot[field].update(
            source="prototype_sensor",
            quality_flags=[],
            started_at=iso(current - 180),
            ended_at=iso(current - 60),
        )
    snapshot["eyes"]["scale_basis"] = "calibrated_mm"
    snapshot["eyes"]["baseline_diameter_mm"] = 4.0
    snapshot["cardiac"]["modality"] = "ppg"
    snapshot["sample"].update(collected_at=iso(current - 170), status="valid")
    for row in snapshot["saliva"]:
        row.update(
            source="reference_lab",
            collected_at=iso(current - 170),
            measured_at=iso(current - 80)
            if row["qualifier"] != "not_measured"
            else None,
            quality_flags=[],
        )
    snapshot["baseline_ref"] = None
    manifest = json.loads(
        (ROOT / "examples/unvalidated_model_manifest.json").read_text()
    )
    manifest.update(
        model_id="engineering-model",
        lifecycle="active_research",
        endpoint_id="engineering-endpoint",
        endpoint_definition="Fictional engineering endpoint",
        feature_version="otgd.features.v1",
        artifact_sha256="a" * 64,
        allowed_protocol_ids=[snapshot["protocol_id"]],
        allowed_collection_method_ids=[snapshot["sample"]["collection_method_id"]],
        allowed_assay_ids=list(
            {r["method_id"] for r in snapshot["saliva"] if r["method_id"]}
        ),
        allowed_assay_bases=["free"],
        allowed_hardware_revisions=["engineering-hw"],
        allowed_task_versions=[snapshot["task"]["task_version"]],
        allowed_provenance=["reference_lab", "prototype_sensor"],
        calibration_id="engineering-model-calibration",
        quality_policy_id="quality",
        co_use_policy_id="co-use",
        compatibility_policy_id="compatibility",
        operating_threshold=0.5,
        population={
            "description": "Fictional engineering cohort",
            "min_age_years": 18,
            "max_age_years": 65,
        },
        max_clock_uncertainty_ms=10,
        max_acquisition_span_ms=180000,
        max_delivery_delay_ms=3600000,
        uncertainty_policy={
            "policy_id": "uncertainty",
            "method": "none",
            "lower": None,
            "upper": None,
            "rationale": "Engineering fixture only",
        },
        validation_report_uri="https://research.invalid/engineering-report",
        approval_refs=["engineering-review-1", "engineering-review-2"],
    )
    artifact = m.Artifact.model_validate(
        {
            "schema_version": "1.0.0",
            "algorithm": "logistic_linear_v1",
            "input_contract_version": "0.1.0",
            "feature_version": "otgd.features.v1",
            "feature_names": ["task.features.median_rt_ms", "saliva.THC"],
            "means": [300.0, 10.0],
            "scales": [100.0, 10.0],
            "coefficients": [1.0, 1.0],
            "intercept": 1.0,
            "calibration": {
                "calibration_id": manifest["calibration_id"],
                "slope": 1.0,
                "intercept": 0.0,
            },
            "feature_limits": {
                "task.features.median_rt_ms": [0.0, 2000.0],
                "saliva.THC": [0.0, 10000.0],
            },
            "trained_at": iso(current - 450),
        }
    )
    raw = canonical(artifact.model_dump())
    manifest["artifact_sha256"] = digest(artifact.model_dump())
    metric = {
        "total": 20,
        "valid": 18,
        "invalid": 2,
        "abstained": 1,
        "positives": 10,
        "negatives": 10,
        "sensitivity": 0.8,
        "specificity": 0.8,
        "brier": 0.1,
        "calibration_error": 0.1,
        "sensitivity_interval": [0.4, 0.95],
        "specificity_interval": [0.4, 0.95],
    }
    report = {
        "schema_version": "1.0.0",
        "artifact_sha256": manifest["artifact_sha256"],
        "dataset_sha256": "b" * 64,
        "split_plan_sha256": "c" * 64,
        "analysis_plan_sha256": "d" * 64,
        "prespecified_at": iso(current - 500),
        "locked_at": iso(current - 400),
        "evaluated_at": iso(current - 100),
        "endpoint_id": manifest["endpoint_id"],
        "operating_threshold": 0.5,
        "confirmatory": metric,
        "later_sessions": metric,
        "ablations": {
            key: metric
            for key in ("chemical_only", "app_only", "combined", "ecg_removed")
        },
        "participant_overlap": False,
        "future_predictors": False,
    }
    body = {
        "model_id": manifest["model_id"],
        "study_ids": [snapshot["study_id"]],
        "manifest": manifest,
        "artifact_ref": {
            "bucket": "engineering-model-bucket",
            "key": "models/engineering.json",
            "version_id": "pinned-1",
            "sha256": manifest["artifact_sha256"],
            "size_bytes": len(raw),
        },
        "evaluation_report": report,
        "quality_policy": {
            "policy_id": "quality",
            "minimum_correct_go_trials": 30,
            "require_native_timing": True,
        },
        "co_use_policy": {
            "policy_id": "co-use",
            "allowed_alcohol_co_use": ["not_reported"],
        },
        "compatibility_policy": {
            "policy_id": "compatibility",
            "assay_tuples": [
                {
                    **{
                        k: r[k]
                        for k in (
                            "analyte",
                            "method_id",
                            "assay_basis",
                            "concentration_basis",
                            "correction_status",
                        )
                    },
                    "collection_method_id": snapshot["sample"]["collection_method_id"],
                }
                for r in snapshot["saliva"]
                if r["method_id"]
            ],
        },
    }
    authority = {
        "schema_version": "1.0.0",
        "model_manifest": manifest,
        "model_registry_version": "v1",
        "native_timing_calibration_sha256": "9" * 64,
        **{
            key: "e" * 64
            for key in (
                "model_registry_sha256",
                "calibration_sha256",
                "quality_policy_sha256",
                "co_use_policy_sha256",
                "compatibility_policy_sha256",
                "study_approval_sha256",
                "consent_sha256",
                "registry_events_sha256",
            )
        },
        "model_artifact_sha256": manifest["artifact_sha256"],
        "evaluation_report_sha256": digest(report),
    }
    proof = {
        "schema_version": "1.0.0",
        "registry_id": manifest["model_id"],
        "registry_version": "v1",
        "manifest_sha256": digest(manifest),
        "model_artifact_sha256": manifest["artifact_sha256"],
        "evaluation_report_sha256": digest(report),
        "feature_version": artifact.feature_version,
        "feature_values_sha256": "f" * 64,
        "calibration_id": manifest["calibration_id"],
        "calibration_sha256": authority["calibration_sha256"],
        "capture_context_sha256": "a" * 64,
        "evidence_manifest_sha256": "b" * 64,
        "baseline_sha256": None,
        "authority_sha256": digest(authority),
        "endpoint_definition": manifest["endpoint_definition"],
        "population_description": manifest["population"]["description"],
        "authority_manifest": authority,
    }
    return {
        "snapshot": snapshot,
        "body": body,
        "artifact": artifact,
        "raw": raw,
        "proof": proof,
    }


def test_engineering_gate_and_finite_math_are_executable(model):
    assert m.validate_registry_model(model["body"]) == model["body"]
    artifact = m.load_artifact(
        model["raw"], model["body"]["artifact_ref"], model["body"]["manifest"]
    )
    result = m.execute(
        model["snapshot"],
        model["body"],
        artifact,
        model["proof"],
        timing_qualified=True,
    )
    assert (
        result["schema_version"] == "1.1.0" and result["state"] == "research_estimate"
    )
    assert 0 <= result["probability"] <= 1
    assert result["input_sha256"] == digest(model["snapshot"])
    assert result["target_at"] == model["snapshot"]["target_at"]
    assert m.validate_result(result) == result


def test_uncertainty_abstains_before_classification(model):
    model["body"]["manifest"]["uncertainty_policy"].update(
        method="probability_band", lower=0.0, upper=1.0
    )
    authority = model["proof"]["authority_manifest"]
    model["proof"].update(
        manifest_sha256=digest(model["body"]["manifest"]),
        authority_sha256=digest(authority),
    )
    result = m.execute(
        model["snapshot"],
        model["body"],
        model["artifact"],
        model["proof"],
        timing_qualified=True,
    )
    assert result["state"] == "inconclusive"
    assert (
        result["probability"] is None
        and result["classification"] is None
        and result["operating_threshold"] is None
    )
    assert result["reason_codes"] == ["UNCERTAINTY_ABSTENTION"]


@pytest.mark.parametrize(
    "field,bad",
    [
        ("algorithm", "pickle"),
        ("feature_names", ["outcome.label"]),
        ("scales", [0.0, 1.0]),
        ("coefficients", [float("nan"), 1.0]),
        ("means", [1.0]),
        ("feature_limits", {}),
        ("trained_at", "yesterday"),
    ],
)
def test_executable_unknown_future_and_nonfinite_artifacts_fail(model, field, bad):
    value = {**model["artifact"].model_dump(), field: bad}
    with pytest.raises(ValueError):
        m.Artifact.model_validate(value)


@pytest.mark.parametrize(
    "change", ["bytes", "size", "version", "calibration", "features", "noncanonical"]
)
def test_artifact_pinning_is_required(model, change):
    raw, ref, manifest = (
        model["raw"],
        deepcopy(model["body"]["artifact_ref"]),
        deepcopy(model["body"]["manifest"]),
    )
    if change == "bytes":
        raw += b" "
    elif change == "size":
        ref["size_bytes"] += 1
    elif change == "version":
        ref["version_id"] = "null"
        with pytest.raises(ValueError):
            m.ArtifactRef.model_validate(ref)
        return
    elif change == "calibration":
        manifest["calibration_id"] = "foreign"
    elif change == "features":
        manifest["required_channels"] = ["pupil"]
    else:
        raw = b" " + raw
        ref.update(size_bytes=len(raw), sha256=m.hashlib.sha256(raw).hexdigest())
        manifest["artifact_sha256"] = ref["sha256"]
    with pytest.raises(Problem):
        m.load_artifact(raw, ref, manifest)


@pytest.mark.parametrize(
    "change",
    [
        "synthetic",
        "study",
        "protocol",
        "hardware",
        "age",
        "co_use",
        "clock",
        "span",
        "delay",
        "status",
        "provenance",
        "quality",
        "timing",
        "task_version",
        "trial_count",
        "assay_tuple",
        "censored",
        "duplicate",
    ],
)
def test_every_acquisition_gate_has_rejection(model, change):
    s, b = model["snapshot"], model["body"]
    if change == "synthetic":
        s["mode"] = "synthetic"
    elif change == "study":
        s["study_id"] = "foreign"
    elif change == "protocol":
        s["protocol_id"] = "foreign"
    elif change == "hardware":
        s["device"]["hardware_revision"] = "foreign"
    elif change == "age":
        s["profile"]["age_years"] = 17
    elif change == "co_use":
        s["history"]["alcohol_co_use"] = "unknown"
    elif change == "clock":
        s["clock_uncertainty_ms"] = 11
    elif change == "span":
        s["acquisition_span_ms"] = 180001
    elif change == "delay":
        b["manifest"]["max_delivery_delay_ms"] = 1
    elif change == "status":
        s["task"]["status"] = "not_collected"
    elif change == "provenance":
        s["task"]["source"] = "simulated"
    elif change == "quality":
        s["task"]["quality_flags"] = ["interrupted"]
    elif change == "timing":
        with pytest.raises(Problem):
            m.scope_check(s, b, False)
        return
    elif change == "task_version":
        b["manifest"]["allowed_task_versions"] = ["other"]
    elif change == "trial_count":
        s["task"]["valid_correct_go_trials"] = 29
    elif change == "assay_tuple":
        b["compatibility_policy"]["assay_tuples"] = []
    elif change == "censored":
        s["saliva"][0].update(qualifier="below_loq", value_ng_ml=None)
    else:
        s["saliva"].append(deepcopy(s["saliva"][0]))
    from jsonschema.exceptions import ValidationError

    with pytest.raises((Problem, ValidationError)):
        m.scope_check(s, b, True)


def test_feature_missingness_and_temporal_baseline_gates(model):
    s, a = model["snapshot"], model["artifact"]
    values = m.feature_values(s, a)
    assert len(values) == 2
    old = deepcopy(s)
    old.update(target_at=iso(now() - 600), capture_completed_at=iso(now() - 500))
    old["profile"]["recorded_at"] = iso(now() - 700)
    assert m.feature_values(s, a, old) == [0.0, 0.0]
    for change in ("subject", "future", "profile", "missing", "range", "censored"):
        baseline = deepcopy(old)
        current = deepcopy(s)
        if change == "subject":
            baseline["subject_ref"] = "foreign"
        elif change == "future":
            baseline["capture_completed_at"] = s["target_at"]
        elif change == "profile":
            current["profile"]["recorded_at"] = iso(now() + 1)
        elif change == "missing":
            current["task"]["features"]["median_rt_ms"] = None
        elif change == "range":
            current["task"]["features"]["median_rt_ms"] = 3001
        else:
            current["saliva"][0]["qualifier"] = "below_loq"
        with pytest.raises(Problem):
            m.feature_values(current, a, baseline)


def test_training_evaluation_policy_and_result_proof_are_bound(model):
    b = model["body"]
    for key in (
        "artifact_ref",
        "quality_policy",
        "co_use_policy",
        "compatibility_policy",
    ):
        changed = deepcopy(b)
        if key == "artifact_ref":
            changed[key]["sha256"] = "0" * 64
        else:
            changed[key]["policy_id"] = "foreign"
        with pytest.raises(ValueError):
            m.validate_registry_model(changed)
    for change in ("denominator", "ablation", "chronology", "threshold", "artifact"):
        changed = deepcopy(b)
        if change == "denominator":
            changed["evaluation_report"]["confirmatory"]["invalid"] = 0
        elif change == "ablation":
            del changed["evaluation_report"]["ablations"]["ecg_removed"]
        elif change == "chronology":
            changed["evaluation_report"]["prespecified_at"] = iso(now() + 100)
        elif change == "threshold":
            changed["evaluation_report"]["operating_threshold"] = 0.6
        else:
            changed["evaluation_report"]["artifact_sha256"] = "0" * 64
        with pytest.raises(ValueError):
            m.validate_registry_model(changed)
    result = m.execute(
        model["snapshot"], b, model["artifact"], model["proof"], timing_qualified=True
    )
    for field, value in [
        ("authority_sha256", "0" * 64),
        ("manifest_sha256", "0" * 64),
        ("model_artifact_sha256", "0" * 64),
        ("registry_version", "v2"),
        ("endpoint_definition", "foreign"),
    ]:
        changed = deepcopy(result)
        changed["model_execution"][field] = value
        with pytest.raises(Problem):
            m.validate_result(changed)


def test_stable_sigmoid_and_dimension_refusal(model):
    assert m.sigmoid(10000) == 1 and m.sigmoid(-10000) == 0
    with pytest.raises(Problem):
        m.sigmoid(float("nan"))
    with pytest.raises(Problem):
        m.score(model["artifact"], [])
    with pytest.raises(Problem):
        m.execute(
            model["snapshot"],
            model["body"],
            model["artifact"],
            model["proof"],
            baseline=model["snapshot"],
            timing_qualified=True,
        )


def test_reversed_abstention_and_underflow_scales_fail_before_execution(model):
    body = deepcopy(model["body"])
    body["manifest"]["uncertainty_policy"].update(
        method="probability_band", lower=0.9, upper=0.1
    )
    with pytest.raises(ValueError):
        m.validate_registry_model(body)
    artifact = model["artifact"].model_dump()
    artifact["scales"] = [5e-324, 5e-324]
    with pytest.raises(ValueError):
        m.Artifact.model_validate(artifact)
    huge = model["artifact"].model_copy(
        update={"coefficients": [1e6, -1e6], "scales": [1e-12, 1e-12]}
    )
    with pytest.raises(Problem) as error:
        m.score(huge, [1e308, 1e308])
    assert error.value.code == "NONFINITE_MODEL_SCORE"


def test_result_policy_classification_registry_and_baseline_cannot_be_relabelled(model):
    result = m.execute(
        model["snapshot"],
        model["body"],
        model["artifact"],
        model["proof"],
        timing_qualified=True,
    )
    for field, bad in [
        ("classification", "below_threshold"),
        ("uncertainty_policy_id", "foreign-policy"),
    ]:
        changed = deepcopy(result)
        changed[field] = bad
        with pytest.raises(Problem):
            m.validate_result(changed)
    for field, bad in [("registry_id", "foreign-model"), ("baseline_sha256", "a" * 64)]:
        changed = deepcopy(result)
        changed["model_execution"][field] = bad
        with pytest.raises(Problem):
            m.validate_result(changed)
