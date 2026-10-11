from copy import deepcopy
from uuid import uuid4
from otgd.config import ROOT
from otgd.canonical import strict_loads, digest
from .conftest import headers


def session_fixture(account):
    s = strict_loads((ROOT / "examples/synthetic_session.json").read_text())
    s["session_id"] = str(uuid4())
    s["subject_ref"] = account
    s["target_at"] = s["created_at"]
    return s


def upload(client, account):
    s = session_fixture(account)
    sid = s["session_id"]

    def send(method, path, body, rev=None):
        r = client.request(method, path, headers=headers(revision=rev), json=body)
        assert r.status_code in (200, 201, 202), (path, r.status_code, r.text)
        return r

    send(
        "POST",
        "/v1/sessions",
        {"session_id": sid, "mode": s["mode"], "protocol_id": s["protocol_id"]},
    )
    send("PUT", f"/v1/sessions/{sid}/snapshot", s, 1)
    context = {
        "schema_version": "1.0.0",
        "session_id": sid,
        "context_confirmed_at": s["created_at"],
        "profile_version_id": None,
        "profile_snapshot_sha256": digest(s["profile"]),
        "history_snapshot_sha256": digest(s["history"]),
        "protocol_id": None,
        "configuration_refs": [],
        "baseline_refs": [],
        "device_associations": [],
    }
    send("PUT", f"/v1/sessions/{sid}/context", context, 0)
    attempts = []
    selection = {
        "saliva": None,
        "eyes": None,
        "cardiac": None,
        "task": None,
        "alcohol": None,
    }
    for component in ["saliva", "eyes", "cardiac", "task"]:
        id = str(uuid4())
        p = (
            {"sample": s["sample"], "saliva": s["saliva"]}
            if component == "saliva"
            else s[component]
        )
        recordid = (
            s["sample"]["sample_id"]
            if component == "saliva"
            else (s["task"]["task_id"] if component == "task" else str(uuid4()))
        )
        first = (
            s["sample"]["collected_at"] if component == "saliva" else p["started_at"]
        )
        last = first if component == "saliva" else p["ended_at"]
        attempt = {
            "schema_version": "1.0.0",
            "session_id": sid,
            "attempt_id": id,
            "component": component,
            "record_id": recordid,
            "supersedes_attempt_id": None,
            "status": "valid",
            "source": "simulated",
            "started_at": first,
            "ended_at": last,
            "configuration_id": None,
            "configuration_hash": None,
            "quality_flags": [],
            "component_metadata": {"projection": p},
            "artifact_refs": [],
            "attestation_refs": [],
        }
        send("PUT", f"/v1/sessions/{sid}/attempts/{id}", attempt, 0)
        attempts.append({"attempt_id": id, "sha256": digest(attempt)})
        selection[component] = id
    manifest = {
        "schema_version": "1.0.0",
        "session_id": sid,
        "context_sha256": digest(context),
        "attempts": attempts,
        "selected": selection,
    }
    send("PUT", f"/v1/sessions/{sid}/evidence-manifest", manifest, 0)
    return s, context, manifest
