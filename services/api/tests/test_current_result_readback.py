"""HR-AUTH-007 readback regression using fictional engineering authority only.

The shared fixture uses real JWT/HTTP, governance transitions, signed acquisition
and worker execution. Its model-object bytes use an explicit storage double and
its database is unit-test SQLite; this supplies no scientific/device approval.
"""

import json
import hashlib
import io
import zipfile
from copy import deepcopy

import pytest

from otgd import model_engine
from otgd.canonical import canonical, strict_loads
from otgd.db import factory
from otgd.domain import safe_result
from otgd.errors import Problem
from otgd.operator_governance import transition
from otgd.worker import claim_job, commit_output, make_export, run_job

from .conftest import headers
from .test_cardiac_authority import cardiac, model, resolved  # noqa: F401 -- shared fixtures
from .test_api import store  # noqa: F401 -- explicit object-storage double
from .test_model_admission import admitted  # noqa: F401 -- shared typed non-HR fixture


@pytest.mark.parametrize("authority", ["model", "cardiac_interval_calibration"])
@pytest.mark.parametrize("route", ["result", "detail", "history"])
def test_retired_hr_authority_prevents_stored_numeric_readback(
    client, cardiac, authority, route, record_property,
):
    """A stored, internally valid HR result cannot bypass current admission."""
    assert run_job(cardiac.job) == "completed"
    paths = {
        "result": f"/v1/sessions/{cardiac.sid}/result",
        "detail": f"/v1/sessions/{cardiac.sid}",
        "history": "/v1/sessions",
    }

    def result_in(body):
        if route == "result":
            return body
        if route == "detail":
            return body["result"]
        return next(row for row in body["items"] if row["session_id"] == cardiac.sid)["result"]

    before = client.get(paths[route], headers=headers())
    assert before.status_code == 200, before.text
    original = deepcopy(result_in(before.json()))
    assert original["schema_version"] == "1.1.0"
    assert original["state"] == "research_estimate"
    assert isinstance(original["probability"], float)
    assert original["model_execution"]["authority_manifest"]["cardiac_authority"] is not None

    kind, identity = (
        ("model", cardiac.body["model_id"])
        if authority == "model"
        else ("calibration", cardiac.timing_id)
    )
    with factory().begin() as db:
        transition(db, kind, identity, "v1", "retire", "local:fixture-releaser",
            "Fictional readback revocation regression", 3)

    # Establish that the actual current server admission refuses this very
    # check, while its immutable stored result remains internally well formed.
    db, owner, check = resolved(cardiac)
    with db:
        assert check.state == "completed"
        assert check.result == original
        assert model_engine.validate_result(check.result) == original
        with pytest.raises(Problem) as refusal:
            model_engine.verify_current_execution(db, owner, check, check.result)

    after = client.get(paths[route], headers=headers())
    observation = {
        "fixture_kind": "FICTIONAL_ENGINEERING_ONLY",
        "authority": authority,
        "route": route,
        "path": paths[route],
        "current_admission_refusal": refusal.value.code,
        "before": {"status": before.status_code, "body": before.json()},
        "after": {"status": after.status_code, "body": after.json()},
    }
    record_property("http_observation", json.dumps(observation, sort_keys=True))
    print("HR_READBACK_OBSERVATION " + json.dumps(observation, sort_keys=True))

    # Reading never rewrites the accepted historical evidence. A refusal or a
    # safe successful response is allowed; current authority loss must remove
    # the numeric research result from every participant-facing route.
    db, _, check = resolved(cardiac)
    with db:
        assert check.result == original
    if 200 <= after.status_code < 300:
        exposed = result_in(after.json())
        assert exposed is None or (
            exposed.get("probability") is None
            and exposed.get("classification") is None
            and exposed.get("operating_threshold") is None
        ), f"{route} disclosed stored HR numeric result after {authority} retirement: {exposed}"
    else:
        assert after.status_code in (403, 409, 422), after.text


def test_current_hr_read_requires_context_but_keeps_original_result(cardiac):
    assert run_job(cardiac.job) == "completed"
    db, owner, check = resolved(cardiac)
    with db:
        original = deepcopy(check.result)
        assert safe_result(check.result, db=db, account=owner, check=check) == original
        with pytest.raises(Problem, match="MODEL_AUTHORITY_CONTEXT_REQUIRED"):
            safe_result(check.result)
        assert check.result == original


def test_non_hr_historical_result_retains_context_free_validation(model):
    result = model_engine.execute(model["snapshot"], model["body"], model["artifact"],
        model["proof"], timing_qualified=True)
    original = deepcopy(result)
    assert "cardiac_authority" not in result["model_execution"]["authority_manifest"]
    assert result["state"] == "research_estimate"
    assert safe_result(result) == original
    assert result == original


@pytest.mark.parametrize("kind", ["cardiac", "admitted"])
def test_current_numeric_research_export_preserves_exact_result_and_linked_evidence(
    client, store, request, monkeypatch, kind, record_property,
):
    from otgd import storage

    value = request.getfixturevalue(kind)
    sid, job = (value.sid, value.job) if kind == "cardiac" else (value["sid"], value["job"])
    assert run_job(job) == "completed"
    # Match the actual mobile GET transport: writes require generation, reads
    # use the authenticated owner and current server account generation.
    authorization_only = {"Authorization": headers()["Authorization"]}
    current = client.get(f"/v1/sessions/{sid}/result", headers=authorization_only)
    assert current.status_code == 200, current.text
    original = current.json()
    assert original["schema_version"] == "1.1.0" and original["state"] == "research_estimate"
    assert isinstance(original["probability"], float)
    detail = client.get(f"/v1/sessions/{sid}", headers=authorization_only)
    assert detail.status_code == 200, detail.text
    monkeypatch.setattr(storage, "versioned_read", store.read)
    response = client.post("/v1/privacy/exports", headers=headers(), json={
        "selection": {"kind": "single", "session_ids": [sid]},
        "format": "json_zip", "include_raw": False})
    record_property("numeric_export_acceptance", json.dumps({
        "fixture_kind": "FICTIONAL_ENGINEERING_ONLY", "model_scope": kind,
        "current_result_http": current.status_code, "current_result": original,
        "export_http": response.status_code, "export_body": response.json()}, sort_keys=True))
    assert response.status_code == 202, response.text
    assert run_job(response.json()["job_id"]) == "completed"
    archive_response = client.get(
        f"/v1/privacy/jobs/{response.json()['job_id']}/download", headers=authorization_only)
    assert archive_response.status_code == 200, archive_response.text
    with zipfile.ZipFile(io.BytesIO(archive_response.content)) as archive:
        path = f"checks/{sid}.json"
        raw = archive.read(path)
        exported = strict_loads(raw)
        manifest = strict_loads(archive.read("manifest.json"))
        assert exported["result"] == original
        for field in ("snapshot", "context", "manifest", "attempts", "instruction_receipts",
            "collections", "collection_abandons", "alcohol"):
            assert exported[field] == detail.json()[field], field
        assert exported["report_revision_index"]["items"] == []
        assert exported["report_revision_index"]["session_id"] == sid
        assert manifest["session_ids"] == [sid]
        entry = next(item for item in manifest["files"] if item["path"] == path)
        assert entry["sha256"] == hashlib.sha256(raw).hexdigest()
        assert entry["size_bytes"] == len(raw)
        assert not any(name.startswith("report-revisions/") for name in archive.namelist())
    record_property("numeric_export_archive", json.dumps({
        "download_http": archive_response.status_code,
        "archive_sha256": hashlib.sha256(archive_response.content).hexdigest(),
        "exported_result": exported["result"], "linked_record_fields": sorted(exported),
        "revision_index": exported["report_revision_index"]}, sort_keys=True))


def test_numeric_export_does_not_grant_administrative_revision_eligibility(cardiac):
    from otgd.report_revisions import _base, freeze_head

    assert run_job(cardiac.job) == "completed"
    db, owner, check = resolved(cardiac)
    with db:
        original = deepcopy(check.result)
        assert freeze_head(db, owner, check) == {"revision_id": None, "revision_sha256": None}
        with pytest.raises(Problem, match="REPORT_REVISION_INTEGRITY"):
            _base(db, owner, check)
        assert check.result == original


@pytest.mark.parametrize("companion_kind", ["report_revision", "result_revision"])
def test_numeric_export_never_ignores_existing_ineligible_companions(client, cardiac, companion_kind):
    from otgd.db import Record, uid

    assert run_job(cardiac.job) == "completed"
    with factory().begin() as db:
        db.add(Record(id=uid(), account_id=cardiac.account, generation=1,
            kind=companion_kind, parent_id=cardiac.sid,
            body={"fictional_invalid_companion": True}, sha256="f" * 64))
    response = client.post("/v1/privacy/exports", headers=headers(), json=export_body(cardiac))
    assert response.status_code == 503, response.text
    assert response.json()["code"] == "REPORT_REVISION_INTEGRITY"


def test_legacy_shaped_numeric_result_remains_unexportable(client, cardiac):
    assert run_job(cardiac.job) == "completed"
    db, _, check = resolved(cardiac)
    with db:
        check.result = {**check.result, "schema_version": "0.1.0"}
        db.commit()
    response = client.post("/v1/privacy/exports", headers=headers(), json=export_body(cardiac))
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "UNSUPPORTED_RESEARCH_RESULT"


def export_body(cardiac):
    return {"selection": {"kind": "single", "session_ids": [cardiac.sid]},
        "format": "json_zip", "include_raw": False}


def retire_model(cardiac):
    with factory().begin() as db:
        transition(db, "model", cardiac.body["model_id"], "v1", "retire",
            "local:fixture-releaser", "Fictional export revocation regression", 3)


def test_retired_hr_export_request_rechecks_before_export_work(client, cardiac):
    assert run_job(cardiac.job) == "completed"
    retire_model(cardiac)
    response = client.post("/v1/privacy/exports", headers=headers(), json=export_body(cardiac))
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "APPROVED_REGISTRY_VERSION_REQUIRED"


@pytest.fixture
def abstained_cardiac(model, request):
    # Retain the supported uncertainty-abstention outcome alongside the numeric
    # positive path; both preserve their original result and current HR gates.
    model["body"]["manifest"]["uncertainty_policy"].update(
        method="probability_band", lower=0.0, upper=1.0)
    return request.getfixturevalue("cardiac")


@pytest.mark.parametrize("stage", ["build", "commit", "download"])
@pytest.mark.parametrize("result_kind", ["numeric", "abstained"])
def test_hr_export_rechecks_current_authority_at_each_boundary(
    client, store, monkeypatch, request, stage, result_kind,
):
    from otgd import storage
    from otgd.db import Job

    value = request.getfixturevalue("cardiac" if result_kind == "numeric" else "abstained_cardiac")
    # The export-store fixture replaces versioned_read after the capture fixture
    # is resolved. Supply its exact bounded model bytes for the result job, then
    # switch to the versioned archive double for export work below.
    monkeypatch.setattr(storage, "versioned_read", lambda *_: canonical(value.artifact.model_dump()))
    assert run_job(value.job) == "completed"
    current = client.get(f"/v1/sessions/{value.sid}/result", headers=headers())
    assert current.status_code == 200 and current.json()["state"] == (
        "research_estimate" if result_kind == "numeric" else "inconclusive")
    monkeypatch.setattr(storage, "versioned_read", store.read)
    response = client.post("/v1/privacy/exports", headers=headers(), json=export_body(value))
    assert response.status_code == 202, response.text
    job_id = response.json()["job_id"]
    if stage == "build":
        retire_model(value)
        assert run_job(job_id) == "failed"
        assert store.objects == {}
    elif stage == "commit":
        claim = claim_job(job_id)
        output = make_export(claim)
        retire_model(value)
        with pytest.raises(Problem, match="APPROVED_REGISTRY_VERSION_REQUIRED"):
            commit_output(claim, output)
        with factory()() as db:
            job = db.get(Job, job_id)
            assert job.state != "completed" and job.output is None
    else:
        assert run_job(job_id) == "completed"
        path = f"/v1/privacy/jobs/{job_id}/download"
        active = client.get(path, headers=headers())
        assert active.status_code == 200 and active.content[:2] == b"PK"
        retire_model(value)
        reads = []
        def observed_storage(*args, **kwargs):
            reads.append((args, kwargs))
            return store
        monkeypatch.setattr(storage, "client", observed_storage)
        refused = client.get(path, headers=headers())
        assert refused.status_code == 403, refused.text
        assert refused.json()["code"] == "APPROVED_REGISTRY_VERSION_REQUIRED"
        assert reads == []
