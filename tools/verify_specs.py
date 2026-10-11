"""Exercise specification contracts and concrete failure cases using fictional data.

These checks do not validate sensors, predictive performance, or a production service.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError
from openapi_spec_validator import validate as validate_openapi
from openapi_spec_validator.readers import read_from_filename

from run_demo import build_demo_result
from spec_validation import (
    ROOT, read_json, timestamp, validate_demo_result, validate_manifest,
    validate_measurement, validate_schema, validate_session, validate_telemetry,
)


def changed(value, path, replacement):
    result = deepcopy(value)
    target = result
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    return result


def must_reject(action):
    try:
        action()
    except (ValidationError, ValueError):
        return
    raise AssertionError("Invalid input was accepted")


def recompute_span(session):
    points = []
    if session["sample"]["collected_at"] is not None:
        points.append(timestamp(session["sample"]["collected_at"]))
    for name in ("eyes", "cardiac", "task"):
        for field in ("started_at", "ended_at"):
            raw = session[name][field]
            if raw is not None:
                points.append(timestamp(raw))
    session["acquisition_span_ms"] = (
        (max(points) - min(points)).total_seconds() * 1000 if points else None
    )


def no_acquisition(session):
    value = deepcopy(session)
    value["sample"].update(status="not_collected", collected_at=None,
                           volume_ml=None, dilution_factor=None)
    value["saliva"] = []
    for name in ("eyes", "cardiac", "task"):
        value[name].update(status="not_collected", started_at=None, ended_at=None)
    for key in ("baseline_diameter_mm", "relative_constriction", "latency_ms",
                "frame_rate_hz", "raw_artifact_id"):
        value["eyes"][key] = None
    for key in ("heart_rate_bpm", "ecg_rmssd_ms", "sample_rate_hz", "raw_artifact_id"):
        value["cardiac"][key] = None
    value["cardiac"]["ecg_status"] = "not_collected"
    for key in ("practice_trials", "scored_trials", "go_trials", "no_go_trials",
                "valid_correct_go_trials"):
        value["task"][key] = 0
    value["task"]["features"] = {key: None for key in value["task"]["features"]}
    value["task"]["events_artifact_id"] = None
    recompute_span(value)
    return value


def check_document_links():
    count = 0
    for path in ROOT.rglob("*.md"):
        if any(part.startswith(".") or part in {"node_modules", "cdk.out", "dist", "build", "coverage"} for part in path.relative_to(ROOT).parts):
            continue
        for match in re.finditer(r"\[[^\]]*\]\((?:<([^>\n]+)>|([^\s)]+))(?:\s+[^)]*)?\)", path.read_text()):
            target = match.group(1) or match.group(2)
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                raise AssertionError(f"Broken local link: {path.relative_to(ROOT)} -> {target}")
            count += 1
    if count == 0:
        raise AssertionError("No documentation links were checked")


def check_requirement_identifiers():
    text = (ROOT / "specs/FULL_SPECIFICATION.md").read_text()
    identifiers = re.findall(r"^\|\s*([A-Z]+-\d{3})\s*\|", text, re.MULTILINE)
    if len(identifiers) < 50:
        raise AssertionError("Normative requirement register unexpectedly missing")
    if len(identifiers) != len(set(identifiers)):
        raise AssertionError("Duplicate normative requirement identifier")


def check_python_syntax():
    for path in (ROOT / "tools").glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))


def check_openapi():
    spec, base_uri = read_from_filename(str(ROOT / "contracts/openapi.yaml"))
    validate_openapi(spec, base_uri=base_uri)
    if len(spec["paths"]) != 8:
        raise AssertionError("Unexpected endpoint inventory")


def main():
    session = read_json(ROOT / "examples/synthetic_session.json")
    manifest = read_json(ROOT / "examples/unvalidated_model_manifest.json")
    pg_measurement = read_json(ROOT / "examples/measurement_pg_converted.json")
    telemetry = [json.loads(line) for line in
                 (ROOT / "examples/synthetic_telemetry.ndjson").read_text().splitlines()]
    result = build_demo_result(session, manifest)
    checks = []

    def accept(name, action):
        checks.append((name, action))

    def reject(name, action):
        checks.append((name, lambda: must_reject(action)))

    def all_schemas():
        paths = list((ROOT / "contracts").glob("*.schema.json"))
        if len(paths) != 5:
            raise AssertionError("Unexpected schema inventory")
        for path in paths:
            Draft202012Validator.check_schema(read_json(path))

    accept("Five JSON Schema documents are structurally valid", all_schemas)
    accept("Completed fictional session passes schema and semantic checks", lambda: validate_session(session))
    accept("Unvalidated manifest remains a valid non-executable placeholder", lambda: validate_manifest(manifest))
    accept("Fictional pg/mL report converts correctly to ng/mL", lambda: validate_measurement(pg_measurement))
    accept("Synthetic demo emits a linked measurement-only result", lambda: validate_demo_result(session, result))
    accept("Synthetic telemetry fixture preserves sequence and clock order", lambda: validate_telemetry(telemetry))
    accept("Missing acquisitions can be recorded without invented measurements", lambda: validate_session(no_acquisition(session)))

    no_saliva = deepcopy(session)
    no_saliva["sample"].update(status="not_collected", collected_at=None,
                              volume_ml=None, dilution_factor=None)
    no_saliva["saliva"] = []
    recompute_span(no_saliva)
    accept("Skipped saliva collection permits an empty analyte list", lambda: validate_session(no_saliva))

    mixed = changed(session["saliva"][0], ["concentration_basis"], "collected_mixture")
    mixed["correction_status"] = "laboratory_corrected"
    accept("Matrix and laboratory correction metadata survive units-only import", lambda: validate_measurement(mixed))

    reject("A censored BLQ value cannot become numeric zero",
           lambda: validate_measurement(changed(session["saliva"][1], ["value_ng_ml"], 0)))
    reject("Incorrect canonical concentration units are rejected",
           lambda: validate_measurement(changed(pg_measurement, ["unit"], "pg/mL")))
    reject("A thousandfold unit-conversion error is rejected",
           lambda: validate_measurement(changed(pg_measurement, ["value_ng_ml"], 75)))
    reject("Quantified results outside the assay range are rejected",
           lambda: validate_measurement(changed(session["saliva"][0], ["value_ng_ml"], 1000)))
    reject("Unrun analytes cannot carry a fabricated analysis timestamp",
           lambda: validate_measurement(changed(session["saliva"][2], ["measured_at"], session["created_at"])))
    reject("Reversed analytical limits are rejected",
           lambda: validate_measurement(changed(pg_measurement, ["limits", "lod_ng_ml"], 1000)))
    reject("Unknown concentration-matrix vocabulary is rejected",
           lambda: validate_measurement(changed(pg_measurement, ["concentration_basis"], "blood")))
    reject("A measurement from another sample is rejected",
           lambda: validate_session(changed(session, ["saliva", 0, "sample_id"], "99999999-9999-4999-8999-999999999999")))
    reject("An absent sample cannot retain its old measurement list",
           lambda: validate_session(changed(session, ["sample", "status"], "not_collected")))
    reject("Inconsistent BMI is rejected",
           lambda: validate_session(changed(session, ["profile", "bmi"], 99)))
    reject("Nonfinite numeric input is rejected",
           lambda: validate_session(changed(session, ["cardiac", "heart_rate_bpm"], float("nan"))))
    false_scale = changed(session, ["eyes", "scale_basis"], "unscaled")
    false_scale["eyes"]["baseline_diameter_mm"] = 4
    reject("Uncalibrated eye pixels cannot be labeled millimeters",
           lambda: validate_session(false_scale))
    reject("An absent ECG cannot contain ECG-derived variability",
           lambda: validate_session(changed(session, ["cardiac", "ecg_rmssd_ms"], 30)))
    false_ecg = changed(session, ["cardiac", "modality"], "ppg")
    false_ecg["cardiac"].update(ecg_status="valid", ecg_rmssd_ms=30)
    reject("A PPG capture cannot claim ECG-derived features", lambda: validate_session(false_ecg))
    reject("A completed task must match its declared trial configuration",
           lambda: validate_session(changed(session, ["task", "scored_trials"], 59)))
    reject("A nonsynthetic profile is refused by the local demo",
           lambda: build_demo_result(changed(session, ["profile", "source"], "self_report"), manifest))
    reject("A nonsimulated assay is refused by the local demo",
           lambda: build_demo_result(changed(session, ["saliva", 0, "source"], "reference_lab"), manifest))
    reject("Unresolved model fields cannot be promoted to active research",
           lambda: validate_manifest(changed(manifest, ["lifecycle"], "active_research")))
    reject("Measurement-only output cannot include a probability",
           lambda: validate_schema(changed(result, ["probability"], 0.5), "result.schema.json"))

    # Arbitrary numbers exercise rejection branches; these are not model outputs.
    research_shape = deepcopy(result)
    research_shape.update(state="research_estimate", endpoint_id="structural-test",
                          probability=0.8, classification="above_threshold",
                          operating_threshold=0.5, uncertainty_policy_id="structural-test",
                          provenance_summary=["prototype_sensor"])
    reject("Research output cannot reference an unvalidated model",
           lambda: validate_schema(research_shape, "result.schema.json"))
    simulated_research = deepcopy(research_shape)
    simulated_research.update(model_lifecycle="active_research", provenance_summary=["simulated"])
    reject("Research output cannot claim simulated evidence",
           lambda: validate_schema(simulated_research, "result.schema.json"))
    reject("A result tied to another input digest is rejected",
           lambda: validate_demo_result(session, changed(result, ["input_sha256"], "0" * 64)))
    reject("Acquisition after capture completion is rejected",
           lambda: validate_session(changed(session, ["task", "ended_at"], "2026-10-11T18:00:00Z")))
    reject("An understated acquisition span is rejected",
           lambda: validate_session(changed(session, ["acquisition_span_ms"], 1)))
    invalid_eyes = changed(session, ["eyes", "status"], "invalid")
    invalid_eyes["eyes"]["quality_flags"] = []
    reject("Invalid captures require a reason", lambda: validate_session(invalid_eyes))
    reject("Telemetry gaps are rejected",
           lambda: validate_telemetry(changed(telemetry, [1, "seq"], 3)))
    reject("Telemetry clock resets are rejected",
           lambda: validate_telemetry(changed(telemetry, [1, "monotonic_ms"], 0)))
    reject("Telemetry from different devices cannot be merged",
           lambda: validate_telemetry(changed(telemetry, [1, "device_id"], "synthetic-nano-002")))
    accept("OpenAPI 3.1 validates with its external local schema references", check_openapi)
    accept("Local Markdown document links resolve", check_document_links)
    accept("Normative requirement identifiers are present and unique", check_requirement_identifiers)
    accept("Python starter and verifier files parse", check_python_syntax)

    for name, action in checks:
        try:
            action()
        except Exception:
            print(f"FAIL: {name}")
            raise
        print(f"PASS: {name}")
    print(f"\n{len(checks)} checks passed. No hardware or clinical performance was evaluated.")


if __name__ == "__main__":
    main()
