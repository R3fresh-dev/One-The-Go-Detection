import base64, json, time
from uuid import uuid4
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from otgd.config import ROOT, Settings
from otgd.canonical import canonical, digest, strict_loads
from otgd.db import (
    Account,
    Artifact,
    Check,
    Dedup,
    Job,
    Record,
    Registry,
    factory,
    engine,
    now,
    iso,
)
from otgd.errors import Problem
from otgd.domain import verify_signature
from otgd.native_evidence import schedule, CONFIG_SHA
from otgd.worker import claim_job, commit_output, LeaseLost
from otgd.storage import versioned_read
from .conftest import headers
from .helpers import upload
from .test_api import store, finalize


@pytest.mark.parametrize(
    "fixture",
    strict_loads((ROOT / "contracts/application/canonical-golden.json").read_text())[
        "valid"
    ],
)
def test_jcs_literal_goldens(fixture):
    assert canonical(fixture["value"]).decode() == fixture["canonical_utf8"]
    assert digest(fixture["value"]) == fixture["sha256"]


@pytest.mark.parametrize(
    "raw",
    strict_loads((ROOT / "contracts/application/canonical-golden.json").read_text())[
        "invalid_json"
    ],
)
def test_jcs_rejects_ambiguous_input(raw):
    with pytest.raises((ValueError, UnicodeError)):
        strict_loads(raw)


@pytest.mark.parametrize(
    "fixture",
    strict_loads(
        (
            ROOT
            / "openspec/changes/production-mobile-platform/fixtures/reaction-task-golden-v1.json"
        ).read_text()
    )["schedules"],
)
def test_native_schedule_is_independently_reproducible(fixture):
    actual = schedule(fixture["schedule"]["seed"])
    assert actual == fixture["schedule"]
    assert digest(actual) == fixture["schedule_sha256"]


def test_p256_domain_separation_and_payload_binding():
    key = ec.generate_private_key(ec.SECP256R1())
    public = base64.b64encode(
        key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    ).decode()
    body = {"value": 12.5, "owner": "a"}
    signature = base64.b64encode(
        key.sign(b"OTGD-BIND-v1\n" + canonical(body), ec.ECDSA(hashes.SHA256()))
    ).decode()
    verify_signature(public, signature, "OTGD-BIND-v1\n", body)
    with pytest.raises(Problem):
        verify_signature(public, signature, "OTGD-CAPTURE-v1\n", body)
    with pytest.raises(Problem):
        verify_signature(
            public, signature, "OTGD-BIND-v1\n", {"value": 12.5, "owner": "b"}
        )
    with pytest.raises(Problem):
        verify_signature(public, signature + "?", "OTGD-BIND-v1\n", body)


def test_binding_challenge_is_single_use_and_owner_scoped(client, account):
    key = ec.generate_private_key(ec.SECP256R1())
    public = base64.b64encode(
        key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    ).decode()
    with factory().begin() as db:
        db.add(
            Registry(
                id="device:fixture-device:key1",
                kind="device",
                active=True,
                body={
                    "account_refs": [account],
                    "public_key_spki": public,
                    "hardware_revision": "test",
                    "firmware_version": "test",
                },
            )
        )
    r = client.post(
        "/v1/device-bindings/challenges",
        headers=headers(),
        json={"device_id": "fixture-device", "key_id": "key1"},
    )
    assert r.status_code == 201
    transcript = r.json()["transcript"]
    signature = base64.b64encode(
        key.sign(b"OTGD-BIND-v1\n" + canonical(transcript), ec.ECDSA(hashes.SHA256()))
    ).decode()
    body = {"challenge_id": r.json()["challenge_id"], "signature": signature}
    h = headers(key="bind-fixture")
    bound = client.post("/v1/device-bindings", headers=h, json=body)
    assert bound.status_code == 201
    assert (
        client.post("/v1/device-bindings", headers=h, json=body).json() == bound.json()
    )
    assert (
        client.post("/v1/device-bindings", headers=headers(), json=body).status_code
        == 409
    )
    assert client.get("/v1/device-bindings", headers=headers("b")).json()["items"] == []
    assert (
        client.delete(
            "/v1/device-bindings/" + bound.json()["binding_id"], headers=headers()
        ).status_code
        == 200
    )
    assert (
        client.get("/v1/device-bindings", headers=headers()).json()["items"][0]["state"]
        == "revoked"
    )


@pytest.mark.parametrize("version", [None, "", "null"])
def test_unversioned_object_is_never_accepted(version):
    with pytest.raises(Problem):
        versioned_read("bucket", "key", version, 128)


def test_old_generation_cannot_commit_queued_result_after_delete(
    client, account, store
):
    s, c, m = upload(client, account)
    accepted = client.post(
        f"/v1/sessions/{s['session_id']}/finalize",
        headers=headers(revision=2),
        json={"snapshot_sha256": digest(s), "evidence_sha256": digest(m)},
    )
    claim = claim_job(accepted.json()["job_id"])
    assert claim
    deletion = client.post(
        "/v1/privacy/deletion-requests",
        headers=headers(),
        json={"scope": "all_data", "confirmation": True},
    )
    assert deletion.status_code == 202
    with pytest.raises(LeaseLost):
        commit_output(claim, {})
    assert (
        client.put(
            f"/v1/sessions/{s['session_id']}/snapshot",
            headers=headers(revision=3),
            json=s,
        ).status_code
        == 410
    )


def test_export_resume_headers_cannot_bypass_authentication(client):
    r = client.get(
        "/v1/privacy/jobs/" + str(uuid4()) + "/download",
        headers={"Range": "bytes=0-10"},
    )
    assert r.status_code == 401


def test_empty_export_still_contains_frozen_profile(client, account, store):
    from otgd.worker import run_job
    import zipfile, io

    body = {
        "profile": {
            "age_years": 25,
            "height_cm": 180.0,
            "weight_kg": 81.0,
            "bmi": 25.0,
            "recorded_at": iso(),
            "source": "self_report",
        },
        "history": {
            "use_frequency": "unknown",
            "route": "unknown",
            "time_since_use_min": None,
            "recent_exercise": None,
            "sleep_hours": None,
            "alcohol_co_use": "unknown",
        },
        "context": None,
    }
    saved = client.patch("/v1/me/profile", headers=headers(revision=0), json=body)
    assert saved.status_code == 200
    result = client.post(
        "/v1/privacy/exports",
        headers=headers(),
        json={
            "selection": {"kind": "all", "session_ids": []},
            "format": "json_zip",
            "include_raw": False,
        },
    )
    assert result.status_code == 202
    body["profile"]["age_years"] = 26
    assert (
        client.patch(
            "/v1/me/profile", headers=headers(revision=1), json=body
        ).status_code
        == 200
    )
    assert run_job(result.json()["job_id"]) == "completed"
    data = client.get(
        "/v1/privacy/jobs/" + result.json()["job_id"] + "/download", headers=headers()
    )
    with zipfile.ZipFile(io.BytesIO(data.content)) as z:
        profile = strict_loads(z.read("profile.json"))
        assert profile["current"]["profile"]["age_years"] == 25
        assert len(profile["versions"]) == 1


@pytest.mark.postgres
def test_postgres_concurrent_identical_creation_is_one_mutation(client, account):
    if engine().dialect.name != "postgresql":
        pytest.skip("Actual PostgreSQL required; SQLite does not verify row locks")
    id = str(uuid4())
    h = headers(key="parallel-create")
    body = {"session_id": id, "mode": "synthetic"}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda _: client.post("/v1/sessions", headers=h, json=body), range(2)
            )
        )
    assert [r.status_code for r in results] == [201, 201]
    assert results[0].json() == results[1].json()
    from sqlalchemy import select, func

    with factory()() as db:
        assert (
            db.scalar(select(func.count()).select_from(Check).where(Check.id == id))
            == 1
        )


def test_excessive_json_depth_rejected_as_validation(client):
    response = client.post(
        "/v1/sessions",
        headers={"Content-Type": "application/json"},
        content="[" * 1100 + "0" + "]" * 1100,
    )
    assert response.status_code == 422


def test_cors_only_explicit_registered_browser_origin(client):
    headers = {
        "Origin": "http://localhost:8082",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,idempotency-key",
    }
    response = client.options("/v1/sessions", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8082"
    rejected = client.options(
        "/v1/sessions", headers={**headers, "Origin": "https://unregistered.example"}
    )
    assert rejected.status_code == 400
    assert "access-control-allow-origin" not in rejected.headers


def test_maintenance_and_version_gate_new_writes_preserve_privacy_read(
    client, account, monkeypatch
):
    from uuid import uuid4
    from otgd.config import settings
    from .conftest import headers

    cfg = settings()
    monkeypatch.setattr(cfg, "maintenance", True)
    assert client.get("/v1/app-config").json()["maintenance"] is True
    response = client.post(
        "/v1/sessions",
        headers=headers(),
        json={"session_id": str(uuid4()), "mode": "synthetic"},
    )
    assert (
        response.status_code == 503 and response.json()["code"] == "SERVICE_MAINTENANCE"
    )
    assert client.get("/v1/me/profile", headers=headers()).status_code == 200
    monkeypatch.setattr(cfg, "maintenance", False)
    response = client.post(
        "/v1/sessions",
        headers={**headers(), "X-App-Version": "0.1.0"},
        json={"session_id": str(uuid4()), "mode": "synthetic"},
    )
    assert response.status_code == 426 and response.json()["code"] == "UPDATE_REQUIRED"
    assert (
        client.post(
            "/v1/sessions",
            headers={**headers(), "X-App-Version": "0.2.0"},
            json={"session_id": str(uuid4()), "mode": "synthetic"},
        ).status_code
        == 201
    )
