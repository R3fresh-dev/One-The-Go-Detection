from copy import deepcopy
from uuid import uuid4

from .conftest import headers
from .helpers import session_fixture


def cardiac_attempt(session, modality, status="valid"):
    projection = deepcopy(session["cardiac"])
    projection["modality"] = modality
    if modality == "ecg":
        projection.update(ecg_status="valid", sample_rate_hz=250.0)
    metadata = {"modality": modality}
    if status != "started":
        metadata["projection"] = projection
    return {
        "schema_version": "1.0.0",
        "session_id": session["session_id"],
        "attempt_id": str(uuid4()),
        "component": "cardiac",
        "record_id": str(uuid4()),
        "supersedes_attempt_id": None,
        "status": status,
        "source": "simulated",
        "started_at": projection["started_at"],
        "ended_at": None if status == "started" else projection["ended_at"],
        "configuration_id": None,
        "configuration_hash": None,
        "quality_flags": [],
        "component_metadata": metadata,
        "artifact_refs": [],
        "attestation_refs": [],
    }


def register(client, account):
    session = session_fixture(account)
    response = client.post(
        "/v1/sessions",
        headers=headers(),
        json={
            "session_id": session["session_id"],
            "mode": "synthetic",
            "protocol_id": None,
        },
    )
    assert response.status_code == 201, response.text
    return session


def write(client, attempt, revision=0):
    return client.put(
        f"/v1/sessions/{attempt['session_id']}/attempts/{attempt['attempt_id']}",
        headers=headers(revision=revision),
        json=attempt,
    )


def test_one_valid_cardiac_attempt_per_modality_allows_alternative_without_retake(
    client, account
):
    session = register(client, account)
    for modality in ("ppg", "ecg"):
        result = write(client, cardiac_attempt(session, modality))
        assert result.status_code == 200, result.text
    for modality in ("ppg", "ecg"):
        for status in ("valid", "started"):
            result = write(client, cardiac_attempt(session, modality, status))
            assert result.status_code == 409, result.text
            assert result.json()["code"] == "VALID_CARDIAC_MODALITY_ALREADY_EXISTS"


def test_started_cardiac_modality_cannot_change_on_terminal_evidence(client, account):
    session = register(client, account)
    started = cardiac_attempt(session, "ppg", "started")
    assert write(client, started).status_code == 200
    completed = cardiac_attempt(session, "ecg")
    completed.update(attempt_id=started["attempt_id"], record_id=started["record_id"])
    result = write(client, completed, 1)
    assert result.status_code == 409, result.text
    assert result.json()["code"] == "ATTEMPT_IDENTITY_CONFLICT"


def test_cardiac_metadata_must_match_projection_and_start_requires_modality(
    client, account
):
    session = register(client, account)
    mismatched = cardiac_attempt(session, "ppg")
    mismatched["component_metadata"]["modality"] = "ecg"
    result = write(client, mismatched)
    assert result.status_code == 422, result.text
    assert result.json()["code"] == "CARDIAC_MODALITY_MISMATCH"
    unpinned = cardiac_attempt(session, "ppg", "started")
    unpinned["component_metadata"] = {}
    result = write(client, unpinned)
    assert result.status_code == 422, result.text
    assert result.json()["code"] == "CARDIAC_MODALITY_REQUIRED"
