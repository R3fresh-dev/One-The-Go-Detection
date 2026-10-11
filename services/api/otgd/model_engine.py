"""Bounded data-only model execution behind current independently released authority.

No weights, study approvals or clinical endpoint are supplied by this module.
Engineering fixtures prove arithmetic and refusal behavior only.
"""

from __future__ import annotations

import hashlib
import math
from copy import deepcopy
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from .canonical import canonical, digest, strict_loads
from .db import iso, now, uid
from .errors import Problem

Name = Annotated[str, Field(min_length=1, max_length=256)]
Hash = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
FEATURE_CHANNELS = {
    "profile.age_years": None,
    "profile.bmi": None,
    "eyes.baseline_diameter_mm": "pupil",
    "eyes.relative_constriction": "pupil",
    "eyes.latency_ms": "pupil",
    "cardiac.heart_rate_bpm": "cardiac_hr",
    "cardiac.ecg_rmssd_ms": "ecg",
    **{
        "task.features." + key: "task"
        for key in (
            "median_rt_ms",
            "iqr_rt_ms",
            "p90_rt_ms",
            "omission_rate",
            "wrong_go_rate",
            "no_go_error_rate",
        )
    },
    "saliva.THC": "saliva_thc",
    "saliva.THC_COOH": "saliva_thc_cooh",
    "saliva.OH11_THC": "saliva_oh11_thc",
}


def utc_timestamp(value):
    from .recovery_authority import timestamp, RecoveryBlocked

    try:
        return timestamp(value)
    except RecoveryBlocked:
        raise ValueError("Model timestamps require UTC") from None


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ProbabilityCalibration(Strict):
    calibration_id: Name
    slope: Annotated[FiniteFloat, Field(gt=0, le=1000)]
    intercept: Annotated[FiniteFloat, Field(ge=-1000, le=1000)]


class Artifact(Strict):
    schema_version: Literal["1.0.0"]
    algorithm: Literal["logistic_linear_v1"]
    input_contract_version: Literal["0.1.0"]
    feature_version: Literal["otgd.features.v1"]
    feature_names: Annotated[list[Name], Field(min_length=1, max_length=16)]
    means: list[FiniteFloat]
    scales: list[FiniteFloat]
    coefficients: list[FiniteFloat]
    intercept: FiniteFloat
    calibration: ProbabilityCalibration
    feature_limits: dict[str, list[FiniteFloat]]
    trained_at: Name

    @model_validator(mode="after")
    def dimensions(self):
        utc_timestamp(self.trained_at)
        if (
            len(set(self.feature_names)) != len(self.feature_names)
            or any(name not in FEATURE_CHANNELS for name in self.feature_names)
            or any(
                len(vector) != len(self.feature_names)
                for vector in (self.means, self.scales, self.coefficients)
            )
            or any(scale < 1e-12 for scale in self.scales)
            or set(self.feature_limits) != set(self.feature_names)
            or any(
                len(limits) != 2 or limits[0] >= limits[1]
                for limits in self.feature_limits.values()
            )
            or any(
                abs(v) > 1e6
                for v in [self.intercept, *self.means, *self.scales, *self.coefficients]
            )
        ):
            raise ValueError(
                "Unsupported, duplicated or inconsistent finite model features"
            )
        return self


class ArtifactRef(Strict):
    bucket: Name
    key: Annotated[str, Field(min_length=1, max_length=1024)]
    version_id: Annotated[str, Field(min_length=1, max_length=1024)]
    sha256: Hash
    size_bytes: Annotated[int, Field(gt=0, le=65536)]

    @model_validator(mode="after")
    def versioned(self):
        if (
            self.version_id == "null"
            or not self.key.startswith("models/")
            or ".." in self.key.split("/")
        ):
            raise ValueError("Models require a pinned version in the model namespace")
        return self


class QualityPolicy(Strict):
    policy_id: Name
    minimum_correct_go_trials: Annotated[int, Field(ge=30, le=48)]
    require_native_timing: Literal[True]
    max_baseline_age_ms: Annotated[int, Field(gt=0, le=2592000000)] | None = None


class CoUsePolicy(Strict):
    policy_id: Name
    allowed_alcohol_co_use: Annotated[
        list[Literal["reported", "not_reported"]], Field(min_length=1, max_length=2)
    ]

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.allowed_alcohol_co_use)) != len(self.allowed_alcohol_co_use):
            raise ValueError("Duplicate co-use scope")
        return self


class AssayTuple(Strict):
    analyte: Literal["THC", "THC_COOH", "OH11_THC"]
    collection_method_id: Name
    method_id: Name
    assay_basis: Literal["free", "total_after_hydrolysis"]
    concentration_basis: Literal["neat_oral_fluid", "collected_mixture"]
    correction_status: Literal["not_corrected", "laboratory_corrected"]


class CompatibilityPolicy(Strict):
    policy_id: Name
    assay_tuples: Annotated[list[AssayTuple], Field(max_length=256)]

    @model_validator(mode="after")
    def unique(self):
        hashes = [digest(row.model_dump()) for row in self.assay_tuples]
        if len(set(hashes)) != len(hashes):
            raise ValueError("Duplicate approved assay tuple")
        return self


class Metrics(Strict):
    total: Annotated[int, Field(ge=1)]
    valid: Annotated[int, Field(ge=0)]
    invalid: Annotated[int, Field(ge=0)]
    abstained: Annotated[int, Field(ge=0)]
    positives: Annotated[int, Field(ge=1)]
    negatives: Annotated[int, Field(ge=1)]
    sensitivity: Annotated[FiniteFloat, Field(ge=0, le=1)]
    specificity: Annotated[FiniteFloat, Field(ge=0, le=1)]
    brier: Annotated[FiniteFloat, Field(ge=0, le=1)]
    calibration_error: Annotated[FiniteFloat, Field(ge=0, le=1)]
    sensitivity_interval: list[FiniteFloat]
    specificity_interval: list[FiniteFloat]

    @model_validator(mode="after")
    def denominators(self):
        if (
            self.valid + self.invalid != self.total
            or self.positives + self.negatives != self.total
            or self.abstained > self.valid
        ):
            raise ValueError("Evaluation denominators omit invalid or abstaining rows")
        if any(
            len(v) != 2 or not 0 <= v[0] <= v[1] <= 1
            for v in (self.sensitivity_interval, self.specificity_interval)
        ):
            raise ValueError("Invalid prespecified uncertainty interval")
        return self


class EvaluationReport(Strict):
    schema_version: Literal["1.0.0"]
    artifact_sha256: Hash
    dataset_sha256: Hash
    split_plan_sha256: Hash
    analysis_plan_sha256: Hash
    prespecified_at: Name
    locked_at: Name
    evaluated_at: Name
    endpoint_id: Name
    operating_threshold: Annotated[FiniteFloat, Field(gt=0, lt=1)]
    confirmatory: Metrics
    later_sessions: Metrics
    ablations: dict[str, Metrics]
    participant_overlap: Literal[False]
    future_predictors: Literal[False]

    @model_validator(mode="after")
    def locked(self):
        if (
            not utc_timestamp(self.prespecified_at)
            <= utc_timestamp(self.locked_at)
            <= utc_timestamp(self.evaluated_at)
        ):
            raise ValueError(
                "Analysis/threshold must be frozen before confirmatory evaluation"
            )
        if set(self.ablations) != {
            "chemical_only",
            "app_only",
            "combined",
            "ecg_removed",
        }:
            raise ValueError("All matched-split ablations are required")
        if any(
            row.total != self.confirmatory.total
            or row.positives != self.confirmatory.positives
            for row in self.ablations.values()
        ):
            raise ValueError("Ablation denominators must use identical frozen rows")
        return self


def validate_registry_model(body):
    """Called before independent review; well-formed data is not authorization."""
    from .domain import validate_manifest

    manifest = body["manifest"]
    from jsonschema.exceptions import ValidationError

    try:
        validate_manifest(manifest)
    except (ValidationError, ValueError):
        raise ValueError("Model scientific manifest is invalid") from None
    ref = ArtifactRef.model_validate(body["artifact_ref"])
    quality = QualityPolicy.model_validate(body["quality_policy"])
    co_use = CoUsePolicy.model_validate(body["co_use_policy"])
    compatibility = CompatibilityPolicy.model_validate(body["compatibility_policy"])
    report = EvaluationReport.model_validate(body["evaluation_report"])
    if (
        manifest["lifecycle"] != "active_research"
        or ref.sha256 != manifest["artifact_sha256"]
        or report.artifact_sha256 != ref.sha256
        or report.endpoint_id != manifest["endpoint_id"]
        or report.operating_threshold != manifest["operating_threshold"]
        or quality.policy_id != manifest["quality_policy_id"]
        or co_use.policy_id != manifest["co_use_policy_id"]
        or compatibility.policy_id != manifest["compatibility_policy_id"]
        or utc_timestamp(report.evaluated_at) > now()
        or manifest["feature_version"] != "otgd.features.v1"
    ):
        raise ValueError("Model, frozen evaluation and policy identities differ")
    if (
        manifest["baseline_mode"] == "personalized"
        and quality.max_baseline_age_ms is None
    ):
        raise ValueError(
            "Personalized inference requires an explicit bounded baseline age"
        )
    return body


def load_artifact(raw, ref, manifest):
    if (
        not isinstance(raw, bytes)
        or len(raw) != ref["size_bytes"]
        or len(raw) > 65536
        or hashlib.sha256(raw).hexdigest() != ref["sha256"]
        or ref["sha256"] != manifest["artifact_sha256"]
    ):
        raise Problem(422, "MODEL_ARTIFACT_MISMATCH")
    try:
        value = strict_loads(raw)
        if canonical(value) != raw:
            raise ValueError("Noncanonical artifact")
        artifact = Artifact.model_validate(value)
        if (
            artifact.feature_version != manifest["feature_version"]
            or artifact.input_contract_version != manifest["input_contract_version"]
            or artifact.calibration.calibration_id != manifest["calibration_id"]
            or any(
                channel is not None and channel not in manifest["required_channels"]
                for channel in (FEATURE_CHANNELS[k] for k in artifact.feature_names)
            )
        ):
            raise ValueError("Artifact feature/calibration scope mismatch")
        return artifact
    except (ValueError, TypeError, KeyError):
        raise Problem(422, "MODEL_ARTIFACT_UNSUPPORTED") from None


def feature_values(snapshot, artifact, baseline=None):
    from .recovery_authority import timestamp

    if timestamp(snapshot["profile"]["recorded_at"]) > timestamp(snapshot["target_at"]):
        raise Problem(422, "FUTURE_PREDICTOR")
    if baseline is not None and (
        baseline["subject_ref"] != snapshot["subject_ref"]
        or baseline["protocol_id"] != snapshot["protocol_id"]
        or baseline["study_id"] != snapshot["study_id"]
        or timestamp(baseline["capture_completed_at"])
        >= timestamp(snapshot["target_at"])
    ):
        raise Problem(422, "BASELINE_NOT_COMPATIBLE")
    result = []
    for name in artifact.feature_names:
        if name.startswith("saliva."):
            analyte = name.split(".")[1]
            rows = [r for r in snapshot["saliva"] if r["analyte"] == analyte]
            if len(rows) != 1 or rows[0]["qualifier"] != "quantified":
                raise Problem(422, "MISSING_REQUIRED_CHANNEL")
            value = rows[0]["value_ng_ml"]
        else:
            value = snapshot
            for segment in name.split("."):
                value = value[segment]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise Problem(422, "MISSING_REQUIRED_CHANNEL")
        if baseline is not None:
            single = artifact.model_copy(update={"feature_names": [name]})
            value -= feature_values(baseline, single)[0]
        low, high = artifact.feature_limits[name]
        if not low <= value <= high:
            raise Problem(422, "OUTSIDE_SCOPE")
        result.append(float(value))
    return result


def sigmoid(value):
    if not math.isfinite(value):
        raise Problem(422, "NONFINITE_MODEL_SCORE")
    return (
        1 / (1 + math.exp(-value))
        if value >= 0
        else math.exp(value) / (1 + math.exp(value))
    )


def score(artifact, values):
    if len(values) != len(artifact.feature_names):
        raise Problem(422, "MODEL_FEATURE_MISMATCH")
    try:
        terms = [
            w * (v - m) / s
            for w, v, m, s in zip(
                artifact.coefficients, values, artifact.means, artifact.scales
            )
        ]
        if any(not math.isfinite(v) for v in terms):
            raise ValueError("Nonfinite predictor contribution")
        linear = artifact.intercept + math.fsum(terms)
        return sigmoid(
            artifact.calibration.slope * linear + artifact.calibration.intercept
        )
    except (ArithmeticError, ValueError, TypeError):
        raise Problem(422, "NONFINITE_MODEL_SCORE") from None


def scope_check(
    snapshot, body, timing_qualified=False, *, baseline=False, optical_qualified=False
):
    from .domain import validate_session
    from .recovery_authority import timestamp

    try:
        validate_session(snapshot)
    except ValueError:
        raise Problem(422, "INVALID_ACQUISITION") from None
    manifest = body["manifest"]
    if (
        snapshot["mode"] != "controlled_research"
        or snapshot["study_id"] not in body["study_ids"]
    ):
        raise Problem(403, "STUDY_UNAUTHORIZED")
    if (
        snapshot["protocol_id"] not in manifest["allowed_protocol_ids"]
        or snapshot["device"]["hardware_revision"]
        not in manifest["allowed_hardware_revisions"]
    ):
        raise Problem(403, "OUTSIDE_SCOPE")
    age = snapshot["profile"]["age_years"]
    if (
        age is None
        or not manifest["population"]["min_age_years"]
        <= age
        <= manifest["population"]["max_age_years"]
    ):
        raise Problem(403, "OUTSIDE_SCOPE")
    if (
        snapshot["history"]["alcohol_co_use"]
        not in body["co_use_policy"]["allowed_alcohol_co_use"]
    ):
        raise Problem(403, "OUTSIDE_SCOPE")
    if (
        snapshot["clock_uncertainty_ms"] is None
        or snapshot["clock_uncertainty_ms"] > manifest["max_clock_uncertainty_ms"]
        or snapshot["acquisition_span_ms"] is None
        or snapshot["acquisition_span_ms"] > manifest["max_acquisition_span_ms"]
        or timestamp(snapshot["capture_completed_at"]) > timestamp(iso())
        or (
            not baseline
            and (timestamp(iso()) - timestamp(snapshot["capture_completed_at"])) * 1000
            > manifest["max_delivery_delay_ms"]
        )
    ):
        raise Problem(422, "TIMING_UNCERTAIN")
    mapping = {
        "pupil": "eyes",
        "cardiac_hr": "cardiac",
        "ecg": "cardiac",
        "task": "task",
    }
    for channel in manifest["required_channels"]:
        if channel in mapping:
            component = snapshot[mapping[channel]]
            allowed_flags = (
                {"uncalibrated", "UNCALIBRATED_TIMING"}
                if channel == "task" and timing_qualified
                else set()
            )
            if channel == "pupil" and optical_qualified:
                # These flags describe unqualified stimulus timing. Independent
                # geometry/extractor authority permits diameter only, never a
                # physiological response or physical onset assertion.
                allowed_flags = {
                    "PHYSICAL_ONSET_UNMEASURED",
                    "UNQUALIFIED_OPTICAL_EXTRACTOR",
                    "UNCALIBRATED_CAMERA_RESPONSE",
                    "NO_APPROVED_STIMULUS",
                }
            if (
                component["status"] != "valid"
                or component["source"] not in manifest["allowed_provenance"]
                or set(component["quality_flags"]) - allowed_flags
            ):
                raise Problem(422, "INVALID_ACQUISITION")
            if channel == "ecg" and (
                component["modality"] != "ecg" or component["ecg_status"] != "valid"
            ):
                raise Problem(422, "MISSING_REQUIRED_CHANNEL")
            if channel == "pupil" and component["scale_basis"] != "calibrated_mm":
                raise Problem(422, "INCOMPATIBLE_METHOD")
            if channel == "task" and (
                component["task_version"] not in manifest["allowed_task_versions"]
                or component["valid_correct_go_trials"]
                < body["quality_policy"]["minimum_correct_go_trials"]
                or not timing_qualified
            ):
                raise Problem(422, "TIMING_UNCERTAIN")
        else:
            analyte = {
                "saliva_thc": "THC",
                "saliva_thc_cooh": "THC_COOH",
                "saliva_oh11_thc": "OH11_THC",
            }[channel]
            matches = [v for v in snapshot["saliva"] if v["analyte"] == analyte]
            if (
                len(matches) != 1
                or matches[0]["qualifier"] != "quantified"
                or snapshot["sample"]["status"] != "valid"
            ):
                raise Problem(422, "MISSING_REQUIRED_CHANNEL")
            row = matches[0]
            allowed = body["compatibility_policy"]["assay_tuples"]
            actual = {
                k: row[k]
                for k in (
                    "analyte",
                    "method_id",
                    "assay_basis",
                    "concentration_basis",
                    "correction_status",
                )
            }
            actual["collection_method_id"] = snapshot["sample"]["collection_method_id"]
            if (
                actual not in allowed
                or row["source"] not in manifest["allowed_provenance"]
                or row["quality_flags"]
                or row["method_id"] not in manifest["allowed_assay_ids"]
                or actual["collection_method_id"]
                not in manifest["allowed_collection_method_ids"]
                or row["assay_basis"] not in manifest["allowed_assay_bases"]
            ):
                raise Problem(422, "INCOMPATIBLE_METHOD")


def execute(
    snapshot,
    body,
    artifact,
    proof,
    *,
    baseline=None,
    timing_qualified=False,
    timing_bias_ms=0.0,
    optical_qualified=False,
):
    """Internal arithmetic only. Server admission supplies frozen authority/proof."""
    validate_registry_model(body)
    pupil_features = {
        name for name in artifact.feature_names if name.startswith("eyes.")
    }
    if optical_qualified and pupil_features - {"eyes.baseline_diameter_mm"}:
        raise Problem(403, "OPTICAL_PHYSICAL_TIMING_QUALIFICATION_REQUIRED")
    scope_check(snapshot, body, timing_qualified, optical_qualified=optical_qualified)
    if (body["manifest"]["baseline_mode"] == "personalized") != (baseline is not None):
        raise Problem(422, "BASELINE_NOT_COMPATIBLE")
    if baseline is not None:
        scope_check(
            baseline,
            body,
            timing_qualified,
            baseline=True,
            optical_qualified=optical_qualified,
        )
        if (
            utc_timestamp(snapshot["target_at"])
            - utc_timestamp(baseline["capture_completed_at"])
        ) * 1000 > body["quality_policy"]["max_baseline_age_ms"]:
            raise Problem(422, "BASELINE_NOT_COMPATIBLE")

    def corrected(value):
        value = deepcopy(value)
        for field in ("median_rt_ms", "p90_rt_ms"):
            observed = value["task"]["features"][field]
            if observed is not None:
                value["task"]["features"][field] = observed - timing_bias_ms
        return value

    values = feature_values(
        corrected(snapshot), artifact, corrected(baseline) if baseline else None
    )
    probability = score(artifact, values)
    manifest, policy = body["manifest"], body["manifest"]["uncertainty_policy"]
    abstain = (
        policy["method"] == "probability_band"
        and policy["lower"] <= probability <= policy["upper"]
    )
    proof = {
        **proof,
        "feature_values_sha256": digest(values),
        "baseline_sha256": digest(baseline) if baseline else None,
    }
    result = {
        "schema_version": "1.1.0",
        "result_id": uid(),
        "session_id": snapshot["session_id"],
        "state": "inconclusive" if abstain else "research_estimate",
        "target_at": snapshot["target_at"],
        "evaluated_at": iso(),
        "model_id": manifest["model_id"],
        "model_lifecycle": "active_research",
        "endpoint_id": manifest["endpoint_id"],
        "probability": None if abstain else probability,
        "classification": None
        if abstain
        else (
            "above_threshold"
            if probability >= manifest["operating_threshold"]
            else "below_threshold"
        ),
        "operating_threshold": None if abstain else manifest["operating_threshold"],
        "uncertainty_policy_id": policy["policy_id"],
        "reason_codes": ["UNCERTAINTY_ABSTENTION"] if abstain else [],
        "input_sha256": digest(snapshot),
        "provenance_summary": sorted(
            {snapshot[k]["source"] for k in ("eyes", "cardiac", "task")}
            | {r["source"] for r in snapshot["saliva"]}
        ),
        "replaces_result_id": None,
        "model_execution": proof,
    }
    validate_result(result)
    return result


def validate_result(value):
    from .domain import validate_schema

    validate_schema(value, "research/ResearchResult.schema.json")
    if "simulated" in value["provenance_summary"]:
        raise Problem(422, "SIMULATED_INPUT")
    proof = value["model_execution"]
    authority, manifest = (
        proof["authority_manifest"],
        proof["authority_manifest"]["model_manifest"],
    )
    if (
        digest(authority) != proof["authority_sha256"]
        or digest(manifest) != proof["manifest_sha256"]
        or manifest["model_id"] != value["model_id"]
        or manifest["lifecycle"] != "active_research"
        or manifest["endpoint_id"] != value["endpoint_id"]
        or manifest["artifact_sha256"] != proof["model_artifact_sha256"]
        or authority["model_artifact_sha256"] != proof["model_artifact_sha256"]
        or authority["evaluation_report_sha256"] != proof["evaluation_report_sha256"]
        or authority["calibration_sha256"] != proof["calibration_sha256"]
        or authority["model_registry_version"] != proof["registry_version"]
        or manifest["calibration_id"] != proof["calibration_id"]
        or manifest["feature_version"] != proof["feature_version"]
        or manifest["endpoint_definition"] != proof["endpoint_definition"]
        or manifest["population"]["description"] != proof["population_description"]
        or (
            value["state"] == "research_estimate"
            and manifest["operating_threshold"] != value["operating_threshold"]
        )
    ):
        raise Problem(422, "MODEL_EXECUTION_PROOF_MISMATCH")
    policy = manifest["uncertainty_policy"]
    if (
        proof["registry_id"] != manifest["model_id"]
        or value["uncertainty_policy_id"] != policy["policy_id"]
        or (manifest["baseline_mode"] == "personalized")
        != (proof["baseline_sha256"] is not None)
    ):
        raise Problem(422, "MODEL_EXECUTION_PROOF_MISMATCH")
    if value["state"] == "research_estimate":
        probability = value["probability"]
        classification = (
            "above_threshold"
            if probability >= manifest["operating_threshold"]
            else "below_threshold"
        )
        if (
            value["classification"] != classification
            or value["reason_codes"]
            or policy["method"] == "probability_band"
            and policy["lower"] <= probability <= policy["upper"]
        ):
            raise Problem(422, "MODEL_EXECUTION_PROOF_MISMATCH")
    elif policy["method"] != "probability_band" or value["reason_codes"] != [
        "UNCERTAINTY_ABSTENTION"
    ]:
        raise Problem(422, "MODEL_EXECUTION_PROOF_MISMATCH")
    return value


def capture_authority(db, account, check, body, manifest):
    from .domain import record
    from .operator_governance import capture_configuration, released_version

    timing_qualified = False
    timing_bias_ms = 0.0
    timing_sha256 = None
    selected = manifest.body["selected"]
    for channel in body["manifest"]["required_channels"]:
        mapped = (
            "saliva"
            if channel.startswith("saliva_")
            else {
                "pupil": "eyes",
                "cardiac_hr": "cardiac",
                "ecg": "cardiac",
                "task": "task",
            }[channel]
        )
        attempt = (
            record(db, account, "attempt", selected.get(mapped))
            if selected.get(mapped)
            else None
        )
        if (
            not attempt
            or attempt.body["source"] == "simulated"
            or attempt.body["status"] != "valid"
        ):
            raise Problem(422, "INVALID_ACQUISITION")
        config = capture_configuration(
            db,
            account,
            check,
            "ecg" if channel == "ecg" else mapped,
            attempt.body["configuration_id"],
            attempt.body["configuration_hash"],
        )
        if (
            released_version(
                db, "qualification", config["qualification_evidence_ref"]
            ).body["purpose"]
            != "qualified_measurement"
        ):
            raise Problem(403, "MEASUREMENT_QUALIFICATION_REQUIRED")
        if channel == "task":
            native = attempt.body["component_metadata"].get("native_result", {})
            timing = native.get("timing", {})
            timing_id = body.get("native_timing_calibration_id")
            if not timing_id:
                raise Problem(403, "PHONE_TIMING_QUALIFICATION_REQUIRED")
            timing_row = released_version(db, "calibration", timing_id)
            qualified = timing_row.body
            required = qualified.get("native_timing", {})
            if (
                qualified["purpose"] != "native_timing"
                or timing.get("simulator") is not False
                or timing.get("deviceModel") not in required.get("phone_models", [])
                or timing.get("osVersion") not in required.get("os_versions", [])
                or timing.get("nativeBuild") not in required.get("native_builds", [])
                or any(
                    timing.get(actual) != required.get(expected)
                    for actual, expected in (
                        ("clockDomain", "clock_domain"),
                        ("inputTimestampMethod", "input_timestamp_method"),
                        ("presentationEvidenceMethod", "presentation_evidence_method"),
                    )
                )
                or native.get("implementationVersion")
                != required.get("implementation_version")
                or native.get("extractorVersion") != required.get("extractor_version")
                or required.get("max_uncertainty_ms", math.inf)
                > body["manifest"]["max_clock_uncertainty_ms"]
                or released_version(
                    db, "qualification", config["qualification_evidence_ref"]
                ).body["purpose"]
                != "qualified_measurement"
            ):
                raise Problem(403, "PHONE_TIMING_QUALIFICATION_REQUIRED")
            timing_qualified = True
            timing_bias_ms = required["bias_ms"]
            timing_sha256 = timing_row.sha256
    return timing_qualified, timing_bias_ms, timing_sha256


def optical_authority(db, account, check, body, evidence):
    """Current independent geometry/extractor scope, without stimulus authority."""
    if "pupil" not in body["manifest"]["required_channels"]:
        return False, None
    from .domain import record
    from .operator_governance import capture_configuration, released_version
    from .optical_evidence import validate_optical

    selected = evidence.body["selected"].get("eyes")
    attempt = record(db, account, "attempt", selected) if selected else None
    if (
        not attempt
        or attempt.body["status"] != "valid"
        or attempt.body["source"] != "prototype_sensor"
    ):
        raise Problem(422, "INVALID_ACQUISITION")
    config = capture_configuration(
        db,
        account,
        check,
        "eyes",
        attempt.body["configuration_id"],
        attempt.body["configuration_hash"],
    )
    if config["software_adapter_id"] != "optical_roi_v1":
        return False, None
    scale = config["material"].get("geometry_scale")
    if (
        not scale
        or released_version(
            db, "qualification", config["qualification_evidence_ref"]
        ).body["purpose"]
        != "qualified_measurement"
    ):
        raise Problem(403, "OPTICAL_GEOMETRY_QUALIFICATION_REQUIRED")
    calibration = released_version(db, "calibration", scale["calibration_id"])
    if (
        calibration.body["purpose"] != "optical_geometry"
        or calibration.body["calibration_sha256"] != scale["calibration_sha256"]
    ):
        raise Problem(403, "OPTICAL_GEOMETRY_QUALIFICATION_REQUIRED")
    raw = attempt.body["component_metadata"].get("native_result")
    if not isinstance(raw, dict):
        raise Problem(422, "OPTICAL_EVIDENCE_INVALID")
    validated = validate_optical(raw, check.snapshot["eyes"], config)
    if (
        validated["calibration_status"] != "geometry_only"
        or validated["baseline_diameter_mm"] is None
    ):
        raise Problem(403, "OPTICAL_GEOMETRY_QUALIFICATION_REQUIRED")
    # The exact scale digest is already frozen in the configuration material
    # referenced by the captured context and evidence manifest.
    return True, calibration.sha256


def execution_authority(db, account, check):
    """Resolve actual released records and owner evidence; no request approval flags."""
    from sqlalchemy import select
    from .config import settings
    from .db import Check, RegistryEvent, SystemState
    from .domain import NOTICE_SHA, record, verify_evidence
    from .operator_governance import released_version, validate_dependencies

    if (
        account.state != "active"
        or account.generation != check.generation
        or account.notice != NOTICE_SHA
        or check.mode != "controlled_research"
    ):
        raise Problem(403, "STUDY_UNAUTHORIZED")
    recovery = db.get(SystemState, "recovery")
    if recovery:
        from .recovery_scopes import require_study_scope

        require_study_scope(db, check.study_id, account)
    study = released_version(db, "study", check.study_id)
    if (
        account.id not in study.body["account_refs"]
        or study.body["protocol_id"] != check.protocol_id
        or not study.body.get("model_id")
    ):
        raise Problem(403, "STUDY_UNAUTHORIZED")
    consent = record(db, account, "consent", check.study_id)
    if (
        not consent
        or consent.body.get("state") != "active"
        or any(
            consent.body.get(k) != study.body[k]
            for k in ("invitation_id", "document_version", "document_sha256")
        )
    ):
        raise Problem(403, "CURRENT_CONSENT_REQUIRED")
    model = released_version(db, "model", study.body["model_id"])
    body = model.body
    validate_registry_model(body)
    validate_dependencies(db, "model", body)
    if check.study_id not in body["study_ids"]:
        raise Problem(403, "STUDY_UNAUTHORIZED")
    context, manifest = verify_evidence(db, account, check)
    calibration = released_version(
        db, "calibration", body["manifest"]["calibration_id"]
    )
    timing_qualified, timing_bias_ms, timing_sha256 = capture_authority(
        db, account, check, body, manifest
    )
    optical_qualified, optical_sha256 = optical_authority(
        db, account, check, body, manifest
    )
    baseline = None
    if body["manifest"]["baseline_mode"] == "personalized":
        original = (
            db.get(Check, check.snapshot["baseline_ref"])
            if check.snapshot.get("baseline_ref")
            else None
        )
        if (
            not original
            or original.account_id != account.id
            or original.generation != account.generation
            or original.state != "completed"
            or not original.snapshot
        ):
            raise Problem(422, "BASELINE_NOT_COMPATIBLE")
        _, baseline_manifest = verify_evidence(db, account, original)
        baseline_timing, _, baseline_timing_sha = capture_authority(
            db, account, original, body, baseline_manifest
        )
        baseline_optical, baseline_optical_sha = optical_authority(
            db, account, original, body, baseline_manifest
        )
        if (
            baseline_timing_sha != timing_sha256
            or baseline_optical_sha != optical_sha256
        ):
            raise Problem(422, "BASELINE_NOT_COMPATIBLE")
        scope_check(
            original.snapshot,
            body,
            baseline_timing,
            baseline=True,
            optical_qualified=baseline_optical,
        )
        baseline = original.snapshot
    ref = ArtifactRef.model_validate(body["artifact_ref"]).model_dump()
    if ref["bucket"] != settings().artifact_bucket:
        raise Problem(403, "MODEL_ARTIFACT_SCOPE_MISMATCH")
    decisions = list(
        db.scalars(
            select(RegistryEvent)
            .where(RegistryEvent.version_id == model.id)
            .order_by(RegistryEvent.revision)
        )
    )
    authority = {
        "schema_version": "1.0.0",
        "model_manifest": body["manifest"],
        "model_registry_version": model.version,
        "model_registry_sha256": model.sha256,
        "model_artifact_sha256": ref["sha256"],
        "evaluation_report_sha256": digest(body["evaluation_report"]),
        "calibration_sha256": calibration.sha256,
        "native_timing_calibration_sha256": timing_sha256,
        "quality_policy_sha256": digest(body["quality_policy"]),
        "co_use_policy_sha256": digest(body["co_use_policy"]),
        "compatibility_policy_sha256": digest(body["compatibility_policy"]),
        "study_approval_sha256": study.sha256,
        "consent_sha256": consent.sha256,
        "registry_events_sha256": digest(
            [
                {
                    "revision": r.revision,
                    "state": r.state,
                    "principal": r.principal,
                    "sha256": r.submitted_sha256,
                }
                for r in decisions
            ]
        ),
    }
    proof = {
        "schema_version": "1.0.0",
        "registry_id": body["model_id"],
        "registry_version": model.version,
        "manifest_sha256": digest(body["manifest"]),
        "model_artifact_sha256": ref["sha256"],
        "evaluation_report_sha256": digest(body["evaluation_report"]),
        "feature_version": body["manifest"]["feature_version"],
        "feature_values_sha256": "0" * 64,
        "calibration_id": body["manifest"]["calibration_id"],
        "calibration_sha256": calibration.sha256,
        "capture_context_sha256": context.sha256,
        "evidence_manifest_sha256": manifest.sha256,
        "baseline_sha256": digest(baseline) if baseline else None,
        "authority_sha256": digest(authority),
        "endpoint_definition": body["manifest"]["endpoint_definition"],
        "population_description": body["manifest"]["population"]["description"],
        "authority_manifest": authority,
    }
    return {
        "body": body,
        "ref": ref,
        "proof": proof,
        "baseline": baseline,
        "timing_qualified": timing_qualified,
        "timing_bias_ms": timing_bias_ms,
        "optical_qualified": optical_qualified,
        "calibration": calibration.body,
    }


def result_for_check(db, account, check):
    from .domain import measurement_result
    from .storage import versioned_read

    if check.mode != "controlled_research":
        return measurement_result(check)
    try:
        resolved = execution_authority(db, account, check)
        artifact = load_artifact(
            versioned_read(
                resolved["ref"]["bucket"],
                resolved["ref"]["key"],
                resolved["ref"]["version_id"],
                65536,
            ),
            resolved["ref"],
            resolved["body"]["manifest"],
        )
        if utc_timestamp(artifact.trained_at) > utc_timestamp(
            resolved["body"]["evaluation_report"]["locked_at"]
        ):
            raise Problem(403, "MODEL_ANALYSIS_NOT_LOCKED")
        if (
            digest(artifact.calibration.model_dump())
            != resolved["calibration"]["calibration_sha256"]
        ):
            raise Problem(403, "MODEL_CALIBRATION_MISMATCH")
        return execute(
            check.snapshot,
            resolved["body"],
            artifact,
            resolved["proof"],
            baseline=resolved["baseline"],
            timing_qualified=resolved["timing_qualified"],
            timing_bias_ms=resolved["timing_bias_ms"],
            optical_qualified=resolved["optical_qualified"],
        )
    except Problem as error:
        result = measurement_result(check)
        result["state"] = "inconclusive"
        known = {
            "STUDY_UNAUTHORIZED",
            "OUTSIDE_SCOPE",
            "TIMING_UNCERTAIN",
            "INVALID_ACQUISITION",
            "MISSING_REQUIRED_CHANNEL",
            "INCOMPATIBLE_METHOD",
        }
        result["reason_codes"] = [
            error.code if error.code in known else "MODEL_UNAVAILABLE"
        ]
        return result


def verify_current_execution(db, account, check, output):
    if output.get("schema_version") != "1.1.0":
        return
    validate_result(output)
    resolved = execution_authority(db, account, check)
    if (
        resolved["proof"]["authority_sha256"]
        != output["model_execution"]["authority_sha256"]
        or resolved["proof"]["capture_context_sha256"]
        != output["model_execution"]["capture_context_sha256"]
        or resolved["proof"]["evidence_manifest_sha256"]
        != output["model_execution"]["evidence_manifest_sha256"]
        or digest(check.snapshot) != output["input_sha256"]
    ):
        raise Problem(403, "MODEL_AUTHORITY_CHANGED")


def model_capabilities(db, account):
    from .domain import NOTICE_SHA, record
    from .operator_governance import (
        released_version,
        validate_dependencies,
        channel_capabilities,
    )
    from sqlalchemy import select
    from .db import RegistryVersion

    result = {
        "model_execution_supported": True,
        "inference_available": False,
        "reason_codes": ["MODEL_UNAVAILABLE"],
    }
    if account.state != "active" or account.notice != NOTICE_SHA:
        result["reason_codes"] = [
            "ACCOUNT_NOT_ACTIVE" if account.state != "active" else "NOTICE_ACK_REQUIRED"
        ]
        return result
    for row in db.scalars(
        select(RegistryVersion)
        .where(RegistryVersion.kind == "study", RegistryVersion.state == "active")
        .limit(65)
    ):
        study = row.body
        if account.id not in study["account_refs"] or not study.get("model_id"):
            continue
        try:
            released_version(db, "study", study["registry_id"])
            consent = record(db, account, "consent", study["registry_id"])
            if (
                not consent
                or consent.body.get("state") != "active"
                or any(
                    consent.body.get(k) != study[k]
                    for k in ("invitation_id", "document_version", "document_sha256")
                )
            ):
                continue
            model = released_version(db, "model", study["model_id"])
            validate_registry_model(model.body)
            validate_dependencies(db, "model", model.body)
            if study["registry_id"] in model.body["study_ids"]:
                channels = channel_capabilities(db, account)
                mapping = {
                    "pupil": "eyes",
                    "cardiac_hr": "cardiac",
                    "ecg": "ecg",
                    "task": "task",
                    "saliva_thc": "saliva",
                    "saliva_thc_cooh": "saliva",
                    "saliva_oh11_thc": "saliva",
                }
                required = {
                    mapping[key] for key in model.body["manifest"]["required_channels"]
                }
                if all(channels[key]["available"] for key in required):
                    for channel in required:
                        config_id = study["channels"].get(channel)
                        config = (
                            released_version(db, "configuration", config_id).body
                            if config_id
                            else None
                        )
                        if (
                            not config
                            or released_version(
                                db,
                                "qualification",
                                config["qualification_evidence_ref"],
                            ).body["purpose"]
                            != "qualified_measurement"
                        ):
                            raise Problem(403, "MEASUREMENT_QUALIFICATION_REQUIRED")
                    result["inference_available"] = True
                    result["reason_codes"] = []
                    return result
                result["reason_codes"] = ["QUALIFIED_ACQUISITION_REQUIRED"]
        except (Problem, ValueError, KeyError):
            continue
    return result
