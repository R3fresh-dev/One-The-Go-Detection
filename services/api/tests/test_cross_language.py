"""These fixtures are fictional host/JS records, not physiological acquisitions."""

from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from otgd.canonical import digest, strict_loads
from otgd.config import ROOT
from otgd.errors import Problem
from otgd.native_evidence import validate_native
from otgd.synthetic_evidence import synthetic_values, validate_synthetic


def transport_fixture(channel):
    return strict_loads(
        (
            ROOT / f"contracts/application/fixtures/synthetic-transport-{channel}.json"
        ).read_text()
    )


def transport_attempt(raw):
    a = {
        "source": "simulated",
        "status": "valid",
        "session_id": raw["context"]["sessionId"],
        "attempt_id": raw["context"]["attemptId"],
        "record_id": raw["context"]["captureId"],
        "component": "saliva" if raw["channel"] == "saliva" else "cardiac",
        "configuration_id": raw["fixtureId"],
        "configuration_hash": digest(
            {"fixture": raw["fixtureId"], "channel": raw["channel"]}
        ),
        "ended_at": raw["endedAt"],
    }
    if raw["channel"] == "saliva":
        names = {
            "delta9_thc": "THC",
            "11_hydroxy_thc": "OH11_THC",
            "thc_cooh": "THC_COOH",
        }
        p = {
            "sample": {"collected_at": raw["startedAt"]},
            "saliva": [
                {
                    "analyte": names[x["analyte"]],
                    "qualifier": x["qualifier"],
                    "value_ng_ml": x["value"],
                    "collected_at": raw["startedAt"],
                    "measured_at": raw["endedAt"],
                    "instrument_id": raw["association"]["deviceId"],
                    "limits": {
                        "lod_ng_ml": x["lod"],
                        "loq_ng_ml": x["loq"],
                        "upper_ng_ml": x["uloq"],
                    },
                }
                for x in synthetic_values("saliva")["analytes"]
            ],
        }
    else:
        p = {
            "modality": raw["channel"],
            "heart_rate_bpm": 72,
            "started_at": raw["startedAt"],
            "ended_at": raw["endedAt"],
            "ecg_rmssd_ms": None,
            "sample_rate_hz": 50 if raw["channel"] == "ecg" else None,
        }
    return a, p


@pytest.mark.parametrize("channel", ["ppg", "ecg", "saliva"])
def test_actual_javascript_simulator_hash_clock_transcript(channel):
    raw = transport_fixture(channel)
    a, p = transport_attempt(raw)
    validate_synthetic(raw, a, p)


@pytest.mark.parametrize(
    "tamper", ["hash", "source", "identity", "clock", "projection", "transcript"]
)
def test_simulator_tampering_and_cross_scope_rejected(tamper):
    raw = transport_fixture("ecg")
    a, p = transport_attempt(raw)
    if tamper == "hash":
        raw["association"]["deviceId"] = "modified"
    if tamper == "source":
        a["source"] = "validated_sensor"
    if tamper == "identity":
        a["attempt_id"] = str(uuid4())
    if tamper == "clock":
        raw["clockEvidence"]["offset_ms"] += 1
        raw["evidenceSha256"] = digest(
            {k: v for k, v in raw.items() if k != "evidenceSha256"}
        )
    if tamper == "projection":
        p["heart_rate_bpm"] += 1
    if tamper == "transcript":
        raw["messages"][1]["payload"]["request_message_id"] = str(uuid4())
        raw["evidenceSha256"] = digest(
            {k: v for k, v in raw.items() if k != "evidenceSha256"}
        )
    with pytest.raises(Problem):
        validate_synthetic(raw, a, p)


def native_fixture():
    raw = strict_loads(
        (
            ROOT
            / "apps/mobile/modules/reaction-task/fixtures/native-result-valid-contract-fixture.json"
        ).read_text()
    )
    names = {
        "median_rt_ms": "medianRtMs",
        "iqr_rt_ms": "iqrRtMs",
        "p90_rt_ms": "p90RtMs",
        "omission_rate": "omissionRate",
        "wrong_go_rate": "wrongGoRate",
        "no_go_error_rate": "noGoErrorRate",
    }
    p = {
        "status": raw["status"],
        "source": "prototype_sensor",
        "task_id": raw["runId"],
        "started_at": raw["startedAt"],
        "ended_at": raw["endedAt"],
        "config_sha256": raw["configurationSha256"],
        "features": {k: raw["features"][v] for k, v in names.items()},
        "practice_trials": 6,
        "scored_trials": 60,
        "go_trials": 48,
        "no_go_trials": 12,
        "valid_correct_go_trials": 48,
    }
    return raw, p


def test_host_generated_native_contract_fixture_against_independent_server_scoring():
    raw, p = native_fixture()
    validate_native(raw, p)


def test_configured_task_attempt_cannot_diverge_from_its_stimulus_hash():
    from otgd.domain import validate_component

    bundle = strict_loads(
        (ROOT / "apps/mobile/testfixtures/native-check-contract.json").read_text()
    )
    attempt = next(item for item in bundle["attempts"] if item["component"] == "task")
    validate_component(attempt)
    attempt["configuration_hash"] = "f" * 64
    with pytest.raises(Problem):
        validate_component(attempt)


@pytest.mark.parametrize("elapsed_in_window", [999, 1000])
def test_canceled_native_response_preserves_completed_window_count(elapsed_in_window):
    """Fictional terminal fixture follows the unchanged Kotlin/Swift count rule."""
    raw, projection = native_fixture()
    selected = next(
        trial for trial in raw["trialEvents"]
        if trial["phase"] == "scored" and trial["stimulus"] != "no_go"
    )
    duration = selected["onsetMs"] + elapsed_in_window
    raw["status"] = projection["status"] = "invalid"
    raw["features"] = None
    projection["features"] = {key: None for key in projection["features"]}
    raw["qualityFlags"].append("USER_CANCELED")
    raw["durationMs"] = duration
    raw["nativeEndMs"] = raw["nativeStartMs"] + duration
    ended = datetime.fromisoformat(raw["startedAt"]) + timedelta(milliseconds=duration)
    raw["endedAt"] = projection["ended_at"] = ended.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    raw["timing"]["observedEndedAt"] = raw["endedAt"]
    raw["timing"]["terminalCutoffMs"] = duration
    raw["inputEvents"] = [
        event for event in raw["inputEvents"]
        if event["nativeTimestampMs"] <= duration
    ]
    for trial in raw["trialEvents"]:
        if trial["index"] <= selected["index"]:
            continue
        trial["presented"] = False
        trial["outcome"] = "unresolved"
        for key in (
            "frameTimestampMs", "callbackTimestampMs", "onsetMs", "onsetLatenessMs",
            "selectedInputSequence", "responseTimeMs", "correctGoRtMs",
        ):
            trial[key] = None
    scored = [
        trial for trial in raw["trialEvents"]
        if trial["phase"] == "scored" and trial["presented"]
    ]
    completed = len(scored) - (1 if elapsed_in_window < 1000 else 0)
    raw["counts"] = {
        "presentedPractice": 6,
        "presentedScored": len(scored),
        "presentedGo": sum(trial["stimulus"] != "no_go" for trial in scored),
        "presentedNoGo": sum(trial["stimulus"] == "no_go" for trial in scored),
        "completedScored": completed,
        "correctGo": sum(trial["outcome"] == "correct" for trial in scored),
        "omissions": 0,
        "wrongGo": 0,
        "noGoErrors": 0,
        "correctWithholds": sum(trial["outcome"] == "correct_withhold" for trial in scored),
    }
    for name, field in (
        ("practice_trials", "presentedPractice"), ("scored_trials", "presentedScored"),
        ("go_trials", "presentedGo"), ("no_go_trials", "presentedNoGo"),
        ("valid_correct_go_trials", "correctGo"),
    ):
        projection[name] = raw["counts"][field]
    assert selected["outcome"] == "correct"
    validate_native(raw, projection)
    raw["counts"]["completedScored"] += 1
    with pytest.raises(Problem):
        validate_native(raw, projection)


@pytest.mark.parametrize(
    "tamper",
    ["hidden_stream", "count", "response", "input_type", "calibration", "geometry"],
)
def test_native_contract_tampering_rejected(tamper):
    raw, p = native_fixture()
    if tamper == "hidden_stream":
        raw["timing"]["deviceModel"] = {"raw_values": [1, 2, 3]}
    if tamper == "count":
        raw["counts"]["completedScored"] = 59
    if tamper == "response":
        next(t for t in raw["trialEvents"] if t["outcome"] == "correct")[
            "correctGoRtMs"
        ] += 1
    if tamper == "input_type":
        raw["inputEvents"][0]["nativeSequence"] = 0.5
    if tamper == "calibration":
        raw["timing"]["physicalOnsetVerified"] = True
    if tamper == "geometry":
        raw["timing"]["viewWidthPoints"] = 200
    with pytest.raises(Problem):
        validate_native(raw, p)


@pytest.mark.parametrize(
    "filename", ["fictional-check-contract.json", "native-check-contract.json"]
)
def test_mobile_generated_bundle_upload_finalize_and_read(client, account, filename):
    from otgd.worker import run_job
    from .conftest import headers

    paths = list((ROOT / "apps/mobile/testfixtures").glob("*.json"))
    source = next((p for p in paths if p.name == filename), None)
    assert source is not None, [p.name for p in paths]
    bundle = strict_loads(source.read_text())
    # Only the test owner reference is remapped; all companion digests stay as the app emitted them.
    assert digest(bundle["snapshot"]) == bundle["snapshot_sha256"]
    assert digest(bundle["manifest"]) == bundle["evidence_sha256"]
    snapshot = deepcopy(bundle["snapshot"])
    snapshot["subject_ref"] = account
    sid = snapshot["session_id"]

    def send(method, path, body, revision=None):
        response = client.request(
            method, path, headers=headers(revision=revision), json=body
        )
        assert response.status_code in (200, 201, 202), (
            path,
            response.status_code,
            response.text,
        )
        return response

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
    send("PUT", f"/v1/sessions/{sid}/context", bundle["context"], 0)
    for attempt in bundle["attempts"]:
        assert digest(attempt) == next(
            ref["sha256"]
            for ref in bundle["manifest"]["attempts"]
            if ref["attempt_id"] == attempt["attempt_id"]
        )
        send("PUT", f"/v1/sessions/{sid}/attempts/{attempt['attempt_id']}", attempt, 0)
    if bundle["alcohol"] is not None:
        send("POST", f"/v1/sessions/{sid}/alcohol", bundle["alcohol"])
    send("PUT", f"/v1/sessions/{sid}/snapshot", snapshot, 1)
    send("PUT", f"/v1/sessions/{sid}/evidence-manifest", bundle["manifest"], 0)
    receipt = send(
        "POST",
        f"/v1/sessions/{sid}/finalize",
        {
            "snapshot_sha256": digest(snapshot),
            "evidence_sha256": bundle["evidence_sha256"],
        },
        2,
    )
    assert run_job(receipt.json()["job_id"]) == "completed"
    result = client.get(f"/v1/sessions/{sid}", headers=headers())
    assert result.status_code == 200, result.text
    returned = result.json()
    assert returned["snapshot"] == snapshot
    assert returned["context"] == bundle["context"]
    assert sorted(returned["attempts"], key=lambda a: a["attempt_id"]) == sorted(
        bundle["attempts"], key=lambda a: a["attempt_id"]
    )
    assert returned["result"]["state"] == "measurement_only"
    assert returned["result"]["model_id"] is None
    assert returned["result"]["probability"] is None
    assert returned["result"]["input_sha256"] == digest(snapshot)
