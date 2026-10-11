import hashlib
import io
import zipfile
from copy import deepcopy
from uuid import uuid4
import pytest
from otgd.canonical import digest, strict_loads
from otgd.db import Account, Check, Job, SystemState, factory, iso, now
from otgd.dto import Alcohol
from otgd.errors import Problem
from otgd import storage
from otgd.worker import run_job, claim_job, commit_output, LeaseLost
from .conftest import headers
from .helpers import upload


class MockVersionedStorage:
    """Explicit unit-test mock; not LocalStack or AWS evidence."""

    def __init__(self):
        self.objects = {}
        self.version = 0

    def put(self, bucket, key, data, media="application/json", conditional=False):
        existing = [
            v for v, (b, k, _) in self.objects.items() if (b, k) == (bucket, key)
        ]
        if conditional and existing:
            v = existing[-1]
            if self.objects[v][2] != data:
                raise Problem(409, "IMMUTABLE_OBJECT_CONFLICT")
            return v
        self.version += 1
        v = str(self.version)
        self.objects[v] = (bucket, key, data)
        return v

    def read(self, bucket, key, version, limit):
        b, k, data = self.objects[version]
        assert (b, k) == (bucket, key)
        assert len(data) <= limit
        return data

    def delete(self, bucket, prefix):
        ids = [
            v
            for v, (b, k, _) in self.objects.items()
            if b == bucket and k.startswith(prefix)
        ]
        for v in ids:
            del self.objects[v]
        return len(ids)

    def get_object(self, **kwargs):
        data = self.read(
            kwargs["Bucket"], kwargs["Key"], kwargs["VersionId"], 64 * 1024 * 1024
        )
        return {"ContentLength": len(data), "Body": io.BytesIO(data),
                "VersionId": kwargs["VersionId"], "ContentType": "application/zip"}


@pytest.fixture
def store(monkeypatch):
    m = MockVersionedStorage()
    monkeypatch.setattr(storage, "put_versioned", m.put)
    monkeypatch.setattr(storage, "versioned_read", m.read)
    monkeypatch.setattr(storage, "delete_versions", m.delete)
    monkeypatch.setattr(storage, "client", lambda *_args, **_kw: m)
    return m


def finalize(client, s, m):
    r = client.post(
        f"/v1/sessions/{s['session_id']}/finalize",
        headers=headers(revision=2),
        json={"snapshot_sha256": digest(s), "evidence_sha256": digest(m)},
    )
    assert r.status_code == 202, r.text
    assert run_job(r.json()["job_id"]) == "completed"
    return r.json()


def test_health_and_compile_time_inference(client):
    assert client.get("/health/ready").json()["status"] == "ready"
    assert client.get("/v1/app-config").json()["inference_available"] is False
    assert client.get("/v1/app-config").json()["contract_versions"]["research_result"] == ["1.1.0"]
    assert client.get("/v1/app-config").json()["contract_versions"]["scientific"] == ["0.1.0"]


@pytest.mark.parametrize(
    "claims",
    [
        {"token_use": "id"},
        {"client_id": "wrong"},
        {"iss": "http://wrong"},
        {"exp": 1},
        {"nbf": 9999999999},
    ],
)
def test_invalid_access_tokens(client, claims):
    assert (
        client.get("/v1/me/capabilities", headers=headers(**claims)).status_code == 401
    )


def test_notice_exact_text_hash(client):
    c = client.get("/v1/app-config").json()
    n = client.get(c["notice"]["content_path"]).json()
    assert (
        hashlib.sha256(n["text"].encode()).hexdigest()
        == n["sha256"]
        == c["notice"]["sha256"]
    )


def test_no_write_without_current_notice(client):
    client.get("/v1/me/capabilities", headers=headers())
    r = client.post(
        "/v1/sessions",
        headers=headers(),
        json={"session_id": str(uuid4()), "mode": "synthetic"},
    )
    assert r.status_code == 403


def test_duplicate_json_key_rejected_before_binding(client, account):
    r = client.post(
        "/v1/sessions",
        headers={**headers(), "Content-Type": "application/json"},
        content='{"mode":"synthetic","mode":"analytical"}',
    )
    assert r.status_code == 422


@pytest.mark.parametrize("value", ["NaN", "Infinity", "9007199254740992"])
def test_nonportable_numbers_rejected(client, account, value):
    r = client.post(
        "/v1/sessions",
        headers={**headers(), "Content-Type": "application/json"},
        content='{"bad":' + value + "}",
    )
    assert r.status_code == 422


def test_unknown_fields_not_echoed(client, account):
    r = client.post(
        "/v1/sessions",
        headers=headers(),
        json={
            "session_id": str(uuid4()),
            "mode": "synthetic",
            "health_secret": "do not echo",
        },
    )
    assert r.status_code == 422 and "do not echo" not in r.text


def test_profile_initial_missing_stale_etag_and_replay(client, account):
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
    assert (
        client.patch("/v1/me/profile", headers=headers(), json=body).status_code == 428
    )
    h = headers(key="profile-write", revision=0)
    r = client.patch("/v1/me/profile", headers=h, json=body)
    assert r.status_code == 200
    replay = client.patch("/v1/me/profile", headers=h, json=body)
    assert replay.json() == r.json()
    assert (
        client.patch(
            "/v1/me/profile", headers=headers(revision=0), json=body
        ).status_code
        == 412
    )
    changed = deepcopy(body)
    changed["profile"]["age_years"] = 26
    assert client.patch("/v1/me/profile", headers=h, json=changed).status_code == 409


def test_end_to_end_measurement_only_and_owner_isolation(client, account):
    s, c, m = upload(client, account)
    finalize(client, s, m)
    r = client.get(f"/v1/sessions/{s['session_id']}/result", headers=headers())
    assert r.status_code == 200 and r.json()["probability"] is None
    assert r.json()["state"] == "measurement_only" and r.headers[
        "x-evidence-sha256"
    ] == digest(m)
    assert (
        client.get(f"/v1/sessions/{s['session_id']}", headers=headers("b")).status_code
        == 404
    )
    assert client.get("/v1/sessions", headers=headers("b")).json()["items"] == []


def test_finalized_records_reject_rewrites(client, account):
    s, c, m = upload(client, account)
    finalize(client, s, m)
    r = client.put(
        f"/v1/sessions/{s['session_id']}/snapshot", headers=headers(revision=3), json=s
    )
    assert r.status_code == 409


def test_manifest_does_not_omit_failed_lineage(client, account):
    s, c, m = upload(client, account)
    m["attempts"] = m["attempts"][:-1]
    assert (
        client.put(
            f"/v1/sessions/{s['session_id']}/evidence-manifest",
            headers=headers(revision=1),
            json=m,
        ).status_code
        == 200
    )
    r = client.post(
        f"/v1/sessions/{s['session_id']}/finalize",
        headers=headers(revision=2),
        json={"snapshot_sha256": digest(s), "evidence_sha256": digest(m)},
    )
    assert r.status_code == 422 and r.json()["code"] == "ATTEMPT_LINEAGE_INCOMPLETE"


def test_context_tamper_blocks_finalization(client, account):
    s, c, m = upload(client, account)
    altered = deepcopy(s)
    altered["history"]["recent_exercise"] = True
    assert (
        client.put(
            f"/v1/sessions/{s['session_id']}/snapshot",
            headers=headers(revision=2),
            json=altered,
        ).status_code
        == 200
    )
    r = client.post(
        f"/v1/sessions/{s['session_id']}/finalize",
        headers=headers(revision=3),
        json={"snapshot_sha256": digest(altered), "evidence_sha256": digest(m)},
    )
    assert r.status_code == 422


def test_logout_minimal_receipt_replay_and_new_family(client, account):
    h = headers(key="logout-intent")
    first = client.post("/v1/auth/logout", headers=h, json={})
    assert first.status_code == 200
    assert client.get("/v1/sessions", headers=h).status_code == 401
    assert client.post("/v1/auth/logout", headers=h, json={}).json() == first.json()
    assert (
        client.post("/v1/auth/logout", headers=h, json={"different": True}).status_code
        == 409
    )
    assert (
        client.get("/v1/sessions", headers=headers(family="fresh-family")).status_code
        == 200
    )


def test_export_scope_and_authenticated_download(client, account, store):
    s, c, m = upload(client, account)
    finalize(client, s, m)
    h = headers(key="export-key")
    body = {
        "selection": {"kind": "single", "session_ids": [s["session_id"]]},
        "format": "json_zip",
        "include_raw": False,
    }
    r = client.post("/v1/privacy/exports", headers=h, json=body)
    assert r.status_code == 202, r.text
    id = r.json()["job_id"]
    assert run_job(id) == "completed"
    status = client.get("/v1/privacy/jobs/" + id, headers=headers()).json()
    path = status["download_path"]
    assert client.get(path).status_code == 401
    assert client.get(path, headers=headers("b")).status_code == 404
    data = client.get(path, headers=headers())
    assert data.status_code == 200
    with zipfile.ZipFile(io.BytesIO(data.content)) as z:
        assert set(z.namelist()) == {
            f"checks/{s['session_id']}.json",
            "manifest.json",
            "profile.json",
        }
        record = strict_loads(z.read(f"checks/{s['session_id']}.json"))
        assert len(record["attempts"]) == 4
    assert (
        client.get(path, headers={**headers(), "Range": "bytes=0-100"}).status_code
        == 416
    )
    with factory().begin() as db:
        db.get(Job, id).expires = now() - 1
    assert client.get(path, headers=headers()).status_code == 410
    replay = client.post("/v1/privacy/exports", headers=h, json=body)
    assert replay.json()["job_id"] == id and replay.json()["state"] == "expired"


def test_deletion_barrier_survives_journal_failure_and_same_key_resumes(
    client, account, store, monkeypatch
):
    s, c, m = upload(client, account)
    finalize(client, s, m)
    original = storage.journal_accept

    def fail(*args):
        raise Problem(503, "JOURNAL_UNAVAILABLE")

    monkeypatch.setattr(storage, "journal_accept", fail)
    h = headers(key="delete-once")
    body = {"scope": "all_data", "confirmation": True}
    first = client.post("/v1/privacy/deletion-requests", headers=h, json=body)
    assert first.status_code == 503
    with factory()() as db:
        a = db.get(Account, account)
        assert a.generation == 2 and a.state == "deleting"
    monkeypatch.setattr(storage, "journal_accept", original)
    accepted = client.post("/v1/privacy/deletion-requests", headers=h, json=body)
    assert accepted.status_code == 202
    id = accepted.json()["job_id"]
    assert run_job(id) == "completed"
    with factory()() as db:
        assert not db.get(Check, s["session_id"])
        assert db.get(Account, account).state == "awaiting_generation_ack"
    assert (
        client.post(
            "/v1/me/data-generation/acknowledgments",
            headers=headers(gen=2),
            json={"confirmation": True},
        ).status_code
        == 200
    )
    old = client.post(
        "/v1/sessions",
        headers=headers(),
        json={"session_id": str(uuid4()), "mode": "synthetic"},
    )
    assert old.status_code == 410
    assert (
        client.post("/v1/privacy/deletion-requests", headers=h, json=body).json()[
            "job_id"
        ]
        == id
    )


def test_reauthentication_required_for_sensitive_jobs(client, account):
    r = client.post(
        "/v1/privacy/deletion-requests",
        headers=headers(auth_time=int(now()) - 301),
        json={"scope": "all_data", "confirmation": True},
    )
    assert r.status_code == 401


def test_recovery_cutoff_uses_auth_time_not_refresh_issue_time(client, account):
    with factory().begin() as db:
        db.add(
            SystemState(
                key="recovery",
                body={
                    "verified": True,
                    "authentication_cutoff": int(now()),
                    "scopes_suspended": True,
                },
            )
        )
    assert (
        client.get(
            "/v1/me/capabilities",
            headers=headers(auth_time=int(now()) - 10, iat=int(now())),
        ).status_code
        == 401
    )


def test_preaccount_restore_generation_applies_before_provision(client):
    from otgd.auth import subject_hash

    subject = subject_hash({"sub": "restored"})
    account_id = str(uuid4())
    with factory().begin() as db:
        db.add(
            SystemState(
                key="subject:" + subject,
                body={
                    "account_ref": account_id,
                    "generation": 4,
                    "state": "awaiting_generation_ack",
                },
            )
        )
    r = client.get("/v1/me/capabilities", headers=headers("restored"))
    assert r.json()["account_ref"] == account_id and r.json()["data_generation"] == 4


def test_unprovisioned_device_and_human_capture_unavailable(client, account):
    assert (
        client.post(
            "/v1/device-bindings/challenges",
            headers=headers(),
            json={"device_id": "advertised-name", "key_id": "fake"},
        ).status_code
        == 403
    )
    assert not any(
        c["available"]
        for c in client.get("/v1/me/capabilities", headers=headers())
        .json()["channels"]
        .values()
    )


def test_current_research_estimate_rejected_from_history(client, account):
    s, c, m = upload(client, account)
    finalize(client, s, m)
    with factory().begin() as db:
        row = db.get(Check, s["session_id"])
        r = deepcopy(row.result)
        r["state"] = "research_estimate"
        row.result = r
    result = client.get(f"/v1/sessions/{s['session_id']}", headers=headers())
    assert result.status_code == 422


def test_worker_fence_rejects_late_commit(client, account):
    s, c, m = upload(client, account)
    r = client.post(
        f"/v1/sessions/{s['session_id']}/finalize",
        headers=headers(revision=2),
        json={"snapshot_sha256": digest(s), "evidence_sha256": digest(m)},
    )
    claim = claim_job(r.json()["job_id"])
    assert claim
    with factory().begin() as db:
        db.get(Job, claim.id).fence += 1
    with pytest.raises(LeaseLost):
        commit_output(claim, {})


@pytest.mark.parametrize(
    "qualifier", ["below_loq", "above_range", "not_detected", "not_measured", "invalid"]
)
def test_alcohol_censoring_is_null(qualifier):
    data = {
        "schema_version": "1.0.0",
        "measurement_id": str(uuid4()),
        "session_id": str(uuid4()),
        "collected_at": None,
        "measured_at": None,
        "source": "simulated",
        "qualifier": qualifier,
        "value_mg_l": None,
        "unit": "mg/L",
        "limits": {"lod_mg_l": None, "loq_mg_l": None, "upper_mg_l": None},
        "method_id": None,
        "calibration_id": None,
        "device_id": None,
        "boot_id": None,
        "configuration_hash": None,
        "quality_flags": ["UNAVAILABLE"],
    }
    assert Alcohol.model_validate(data).value_mg_l is None
    data["value_mg_l"] = 0
    with pytest.raises(ValueError):
        Alcohol.model_validate(data)


def test_cleanup_pages_progress_after_failure_and_beyond_first_hundred(
    client, account, store, monkeypatch
):
    from otgd.db import Artifact
    from otgd.worker import cleanup_once

    with factory().begin() as db:
        for i in range(105):
            db.add(
                Artifact(
                    id=f"00000000-0000-4000-8000-{i:012d}",
                    account_id=account,
                    generation=1,
                    session_id=str(uuid4()),
                    bucket="test-artifacts",
                    key=f"quarantine/fixture/{i}",
                    sha256="0" * 64,
                    size=0,
                    media_type="application/octet-stream",
                    kind="ecg_waveform",
                    state="purged",
                    expires=now() - 3600,
                    scope={},
                )
            )
    attempted = []

    def deletion(bucket, key):
        attempted.append(key)
        if key == "quarantine/fixture/0":
            raise RuntimeError("injected unavailable object")
        return 0

    monkeypatch.setattr(storage, "delete_versions", deletion)
    assert cleanup_once() == {"attempted": 100, "failed": 1}
    assert cleanup_once() == {"attempted": 5, "failed": 0}
    assert len(set(attempted)) == 105
    assert cleanup_once() == {"attempted": 0, "failed": 0}
