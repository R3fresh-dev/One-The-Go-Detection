"""Validate fictional inputs and emit a measurement-only result. No model exists here."""

from datetime import datetime, timezone
import json

from spec_validation import ROOT, read_json, snapshot_hash, validate_demo_result, validate_manifest, validate_session


def build_demo_result(session, manifest):
    validate_session(session)
    validate_manifest(manifest)
    if session["mode"] != "synthetic" or manifest["lifecycle"] != "unvalidated":
        raise ValueError("Demo accepts only synthetic sessions and an unvalidated placeholder")
    if session["profile"]["source"] != "synthetic":
        raise ValueError("Demo profile provenance must be synthetic")
    sources = [x["source"] for x in session["saliva"]]
    sources += [session[k]["source"] for k in ("eyes", "cardiac", "task")]
    if any(value != "simulated" for value in sources):
        raise ValueError("No real participant measurements are permitted in this demo")
    result = {
        "schema_version": "0.1.0",
        "result_id": "55555555-5555-4555-8555-555555555555",
        "session_id": session["session_id"],
        "state": "measurement_only",
        "target_at": session["target_at"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "model_id": manifest["model_id"],
        "model_lifecycle": "unvalidated",
        "endpoint_id": None,
        "probability": None,
        "classification": None,
        "operating_threshold": None,
        "uncertainty_policy_id": None,
        "reason_codes": ["SIMULATED_INPUT", "MODEL_UNVALIDATED", "DEMO_ONLY"],
        "input_sha256": snapshot_hash(session),
        "provenance_summary": ["simulated"],
        "replaces_result_id": None,
    }
    validate_demo_result(session, result)
    return result


if __name__ == "__main__":
    session = read_json(ROOT / "examples/synthetic_session.json")
    manifest = read_json(ROOT / "examples/unvalidated_model_manifest.json")
    print(json.dumps(build_demo_result(session, manifest), indent=2, allow_nan=False))
