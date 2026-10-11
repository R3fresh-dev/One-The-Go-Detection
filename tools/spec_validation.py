"""Local contract checks, not a production authorization or inference service."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    def invalid_constant(value):
        raise ValueError(f"Non-JSON numeric constant: {value}")

    return json.loads(path.read_text(), parse_constant=invalid_constant)


def finite_numbers(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Nonfinite numeric value")
    if isinstance(value, dict):
        for child in value.values():
            finite_numbers(child)
    elif isinstance(value, list):
        for child in value:
            finite_numbers(child)


def timestamp(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError("UTC timestamp must end in Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def validate_schema(value, filename: str):
    documents = [read_json(p) for p in (ROOT / "contracts").glob("*.schema.json")]
    registry = Registry().with_resources(
        (doc["$id"], Resource.from_contents(doc)) for doc in documents
    )
    document = read_json(ROOT / "contracts" / filename)
    Draft202012Validator.check_schema(document)
    finite_numbers(value)
    Draft202012Validator(
        document, registry=registry, format_checker=FormatChecker()
    ).validate(value)


def validate_measurement(value):
    validate_schema(value, "measurement.schema.json")
    if value["measured_at"] is not None and timestamp(value["measured_at"]) < timestamp(value["collected_at"]):
        raise ValueError("Analysis predates sample collection")
    limits = value["limits"]
    ordered = [limits[k] for k in ("lod_ng_ml", "loq_ng_ml", "upper_ng_ml")]
    known = [x for x in ordered if x is not None]
    if known != sorted(known):
        raise ValueError("Analytical limits are out of order")
    if value["qualifier"] == "quantified":
        amount = value["value_ng_ml"]
        if not limits["loq_ng_ml"] <= amount <= limits["upper_ng_ml"]:
            raise ValueError("Quantified value lies outside quantification range")
        original = value["original_report"]
        if original["value"] is None:
            raise ValueError("Quantified original value missing")
        converted = original["value"] / (1000 if original["unit"] == "pg/mL" else 1)
        if not math.isclose(converted, amount, rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError("Original and canonical concentrations disagree")


def validate_session(value):
    validate_schema(value, "session.schema.json")
    start = timestamp(value["created_at"])
    target = timestamp(value["target_at"])
    final = timestamp(value["capture_completed_at"])
    if not start <= target <= final:
        raise ValueError("Session timestamp order is invalid")
    collected_at = value["sample"]["collected_at"]
    collected = timestamp(collected_at) if collected_at is not None else None
    if collected is not None and not start <= collected <= final:
        raise ValueError("Sample collection outside session")
    if collected is None and value["saliva"]:
        raise ValueError("Analyte records require an actual collection time")
    analytes = set()
    for reading in value["saliva"]:
        validate_measurement(reading)
        if reading["sample_id"] != value["sample"]["sample_id"]:
            raise ValueError("Measurement belongs to a different sample")
        if reading["collected_at"] != value["sample"]["collected_at"]:
            raise ValueError("Measurement and sample collection times differ")
        if reading["analyte"] in analytes:
            raise ValueError("Duplicate selected analyte in finalized snapshot")
        analytes.add(reading["analyte"])
    ends = [collected] if collected is not None else []
    beginnings = [collected] if collected is not None else []
    for key in ("eyes", "cardiac", "task"):
        component = value[key]
        if component["status"] == "not_collected":
            continue
        if component["started_at"] is None or component["ended_at"] is None:
            if component["status"] == "invalid" and component["quality_flags"]:
                continue
            raise ValueError(f"Missing capture timing: {key}")
        first, last = timestamp(component["started_at"]), timestamp(component["ended_at"])
        if not start <= first <= last <= final:
            raise ValueError(f"Invalid component timing: {key}")
        if component["status"] != "not_collected":
            beginnings.append(first)
            ends.append(last)
        if component["status"] == "invalid" and not component["quality_flags"]:
            raise ValueError(f"Invalid component needs a reason: {key}")
    if ends:
        observed_span = (max(ends) - min(beginnings)).total_seconds() * 1000
        if value["acquisition_span_ms"] is None or not math.isclose(
            value["acquisition_span_ms"], observed_span, abs_tol=1
        ):
            raise ValueError("Acquisition span does not match component timestamps")
    elif value["acquisition_span_ms"] is not None:
        raise ValueError("No observed acquisition: span must be null")
    task = value["task"]
    if task["go_trials"] + task["no_go_trials"] != task["scored_trials"]:
        raise ValueError("Task trial counts do not add up")
    if task["valid_correct_go_trials"] > task["go_trials"]:
        raise ValueError("Correct go count exceeds performed go trials")
    profile = value["profile"]
    height, weight, bmi = (profile[k] for k in ("height_cm", "weight_kg", "bmi"))
    if bmi is not None:
        if height is None or weight is None or height <= 0 or weight <= 0:
            raise ValueError("BMI requires positive height and weight")
        if not math.isclose(bmi, weight / (height / 100) ** 2, abs_tol=0.01):
            raise ValueError("BMI differs from recorded height and weight")


def validate_manifest(value):
    validate_schema(value, "model_manifest.schema.json")
    bounds = value["population"]
    low, high = bounds["min_age_years"], bounds["max_age_years"]
    if low is not None and high is not None and low > high:
        raise ValueError("Population age bounds reversed")
    policy = value["uncertainty_policy"]
    if policy["method"] == "probability_band":
        if not policy["lower"] < policy["upper"]:
            raise ValueError("Abstention bounds must be ordered")
        threshold = value["operating_threshold"]
        if threshold is not None and not policy["lower"] <= threshold <= policy["upper"]:
            raise ValueError("Classification threshold is outside abstention band")
    elif policy["lower"] is not None or policy["upper"] is not None:
        raise ValueError("Non-band policy cannot supply band boundaries")


def snapshot_hash(value) -> str:
    """RFC 8785 SHA-256 shared with the mobile and service contracts."""
    import rfc8785
    serialized = rfc8785.dumps(value)
    return hashlib.sha256(serialized).hexdigest()


def validate_demo_result(session, result):
    validate_schema(result, "result.schema.json")
    if session["mode"] != "synthetic" or result["state"] != "measurement_only":
        raise ValueError("The supplied demonstration only handles synthetic measurement-only data")
    if result["session_id"] != session["session_id"]:
        raise ValueError("Result session mismatch")
    if result["input_sha256"] != snapshot_hash(session):
        raise ValueError("Input digest mismatch")
    if result["target_at"] != session["target_at"]:
        raise ValueError("Result target time mismatch")
    if timestamp(result["evaluated_at"]) < timestamp(session["capture_completed_at"]):
        raise ValueError("Result evaluation predates capture completion")
    if result["provenance_summary"] != ["simulated"]:
        raise ValueError("Demonstration provenance must remain simulated")


def validate_telemetry(lines):
    previous = None
    count = 0
    for item in lines:
        validate_schema(item, "telemetry.schema.json")
        if previous is not None:
            if item["device_id"] != previous["device_id"]:
                raise ValueError("Mixed device identities in one telemetry capture")
            if item["seq"] != previous["seq"] + 1:
                raise ValueError("Telemetry sequence gap/reset: start a fresh receiver capture")
            if item["monotonic_ms"] <= previous["monotonic_ms"]:
                raise ValueError("Telemetry clock reset/rollover: start a fresh receiver capture")
        previous, count = item, count + 1
    if count == 0:
        raise ValueError("Empty telemetry capture")
    return count
