"""Fictional geometry-only arithmetic and authority boundaries, not camera qualification."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from otgd import model_engine as m
from otgd import domain, operator_governance
from otgd.canonical import digest
from otgd.db import iso
from otgd.errors import Problem

from . import test_model_engine
from .test_optical_evidence import fixture

model = test_model_engine.model


@pytest.fixture
def geometry(model):
    raw, projection, config = fixture(scale=True)
    snapshot, body = model["snapshot"], model["body"]
    raw.update(
        started_at=iso(m.utc_timestamp(snapshot["eyes"]["ended_at"]) - 1),
        ended_at=snapshot["eyes"]["ended_at"],
    )
    projection.update(started_at=raw["started_at"], ended_at=raw["ended_at"])
    snapshot["eyes"] = projection
    body["manifest"]["required_channels"] = ["pupil"]
    artifact = model["artifact"].model_copy(
        update={
            "feature_names": ["eyes.baseline_diameter_mm"],
            "coefficients": [1.0],
            "means": [0.4],
            "scales": [1.0],
            "feature_limits": {"eyes.baseline_diameter_mm": [0.0, 10.0]},
        }
    )
    body["manifest"]["artifact_sha256"] = digest(artifact.model_dump())
    body["artifact_ref"]["sha256"] = body["manifest"]["artifact_sha256"]
    body["evaluation_report"]["artifact_sha256"] = body["manifest"]["artifact_sha256"]
    proof = model["proof"]
    authority = proof["authority_manifest"]
    authority.update(
        model_artifact_sha256=body["manifest"]["artifact_sha256"],
        evaluation_report_sha256=digest(body["evaluation_report"]),
    )
    proof.update(
        manifest_sha256=digest(body["manifest"]),
        model_artifact_sha256=authority["model_artifact_sha256"],
        evaluation_report_sha256=authority["evaluation_report_sha256"],
        authority_sha256=digest(authority),
    )
    config["qualification_evidence_ref"] = "FICTIONAL-QUALIFICATION"
    attempt = SimpleNamespace(
        body=dict(
            status="valid",
            source="prototype_sensor",
            configuration_id=config["configuration_id"],
            configuration_hash=config["sha256"],
            component_metadata={"native_result": raw},
        )
    )
    qualification = SimpleNamespace(body={"purpose": "qualified_measurement"})
    calibration = SimpleNamespace(
        sha256="f" * 64,
        body={
            "purpose": "optical_geometry",
            "calibration_sha256": "a" * 64,
        },
    )
    return dict(
        model=model,
        raw=raw,
        config=config,
        attempt=attempt,
        qualification=qualification,
        calibration=calibration,
        artifact=artifact,
    )


def test_qualified_diameter_arithmetic_preserves_unmeasured_onset(geometry):
    model = geometry["model"]
    result = m.execute(
        model["snapshot"],
        model["body"],
        geometry["artifact"],
        model["proof"],
        optical_qualified=True,
    )
    assert result["state"] == "research_estimate"
    assert geometry["raw"]["physical_onset_verified"] is False
    assert model["snapshot"]["eyes"]["latency_ms"] is None


@pytest.mark.parametrize("feature", ["eyes.latency_ms", "eyes.relative_constriction"])
def test_geometry_never_admits_response_features(geometry, feature):
    model = geometry["model"]
    artifact = geometry["artifact"].model_copy(
        update={"feature_names": [feature], "feature_limits": {feature: [0.0, 1000.0]}}
    )
    with pytest.raises(Problem, match="OPTICAL_PHYSICAL_TIMING_QUALIFICATION_REQUIRED"):
        m.execute(
            model["snapshot"],
            model["body"],
            artifact,
            model["proof"],
            optical_qualified=True,
        )


@pytest.mark.parametrize(
    "qualified,flag", [(False, None), (True, "BLUR"), (True, "NO_MILLIMETER_GEOMETRY")]
)
def test_geometry_approval_does_not_ignore_unknown_quality_flags(
    geometry, qualified, flag
):
    model = geometry["model"]
    if flag:
        model["snapshot"]["eyes"]["quality_flags"].append(flag)
    with pytest.raises(Problem):
        m.execute(
            model["snapshot"],
            model["body"],
            geometry["artifact"],
            model["proof"],
            optical_qualified=qualified,
        )


@pytest.mark.parametrize(
    "change",
    [
        None,
        "collection_only",
        "wrong_calibration",
        "tampered_feature",
        "missing_native",
    ],
)
def test_independent_optical_validator_and_current_authority_are_required(
    geometry, monkeypatch, change
):
    # Released registry resolution is a unit fixture here; real lifecycle and
    # exact camera/configuration dependency validation have separate PG tests.
    monkeypatch.setattr(domain, "record", lambda *args: geometry["attempt"])
    monkeypatch.setattr(
        operator_governance, "capture_configuration", lambda *args: geometry["config"]
    )
    monkeypatch.setattr(
        operator_governance,
        "released_version",
        lambda db, kind, name: (
            geometry["qualification"]
            if kind == "qualification"
            else geometry["calibration"]
        ),
    )
    if change == "collection_only":
        geometry["qualification"].body["purpose"] = "measurement_collection"
    elif change == "wrong_calibration":
        geometry["calibration"].body["calibration_sha256"] = "b" * 64
    elif change == "tampered_feature":
        geometry["raw"]["features"]["baseline_diameter_mm"] += 1
    elif change == "missing_native":
        geometry["attempt"].body["component_metadata"] = {}
    model = geometry["model"]
    check = SimpleNamespace(snapshot=model["snapshot"])
    evidence = SimpleNamespace(body={"selected": {"eyes": "FICTIONAL-ATTEMPT"}})
    if change:
        with pytest.raises(Problem):
            m.optical_authority(None, None, check, model["body"], evidence)
    else:
        assert m.optical_authority(None, None, check, model["body"], evidence) == (
            True,
            "f" * 64,
        )
        assert model["snapshot"]["eyes"]["quality_flags"]


def test_nonpupil_models_do_not_consult_optical_authority(model):
    body = deepcopy(model["body"])
    body["manifest"]["required_channels"] = ["task"]
    assert m.optical_authority(None, None, None, body, None) == (False, None)
