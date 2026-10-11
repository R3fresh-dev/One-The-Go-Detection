"""Rebuild explicit fictional API fixtures for the mobile contract reader.

Run from the repository root with the API project's development dependencies:
uv run --project services/api python services/api/tests/generate_report_revision_fixtures.py

This creates an isolated in-memory test database and replaces storage with the
named test double. It cannot provision a cloud registry or collect a sample.
"""

import io
import json
import os
from pathlib import Path
import sys
import zipfile

os.environ["OTGD_ENVIRONMENT"] = "test"
os.environ["OTGD_DATABASE_URL"] = "sqlite://"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from tests.conftest import client as client_fixture, account as account_fixture, headers
from tests.test_report_revisions import (
    laboratory as laboratory_fixture,
    body_for,
    accepted,
)
from tests.test_api import store as store_fixture
from otgd.worker import run_job
from otgd.canonical import digest, strict_loads


def main():
    monkeypatch = pytest.MonkeyPatch()
    store = store_fixture.__wrapped__(monkeypatch)
    generator = client_fixture.__wrapped__()
    client = next(generator)
    try:
        account = account_fixture.__wrapped__(client)
        laboratory = laboratory_fixture.__wrapped__(client, account, store)
        first_request = body_for(laboratory)
        first = accepted(client, laboratory, first_request)
        second_request = body_for(laboratory, first, "reanalysis")
        second = accepted(client, laboratory, second_request)
        session_path = f"/v1/sessions/{laboratory.session_id}"
        base = client.get(session_path, headers=headers()).json()
        listing = client.get(
            session_path + "/report-revisions", headers=headers()
        ).json()
        details = [
            client.get(
                session_path + "/report-revisions/" + value["revision_id"],
                headers=headers(),
            ).json()
            for value in (first, second)
        ]
        selection = {"kind": "single", "session_ids": [laboratory.session_id]}
        exported = client.post(
            "/v1/privacy/exports",
            headers=headers(),
            json={
                "selection": selection,
                "format": "json_zip",
                "include_raw": False,
            },
        )
        assert exported.status_code == 202, exported.text
        job = exported.json()["job_id"]
        assert run_job(job) == "completed"
        archive = client.get(f"/v1/privacy/jobs/{job}/download", headers=headers())
        assert archive.status_code == 200, archive.text
        with zipfile.ZipFile(io.BytesIO(archive.content)) as zipped:
            files = {
                path: strict_loads(zipped.read(path)) for path in zipped.namelist()
            }
        document = {
            "fixture_notice": "Entirely fictional software fixture; no actual laboratory, approval, participant sample, or clinical validation.",
            "schema_version": "1.0.0",
            "account_ref": account,
            "session_id": laboratory.session_id,
            "data_generation": 1,
            "base": base,
            "requests": [first_request, second_request],
            "companions": [first, second],
            "list": listing,
            "details": details,
            "export": {
                "selection": selection,
                "manifest_sha256": digest(files["manifest.json"]),
                "files": files,
            },
        }
        destination = Path(__file__).parent / "fixtures"
        destination.mkdir(exist_ok=True)
        (destination / "report-revision-wire.json").write_text(
            json.dumps(document, indent=2) + "\n"
        )
        (destination / "report-revision-export.zip").write_bytes(archive.content)
        print(
            json.dumps(
                {
                    "revisions": len(listing["items"]),
                    "archive_bytes": len(archive.content),
                    "fixture": str(destination / "report-revision-wire.json"),
                }
            )
        )
    finally:
        generator.close()
        monkeypatch.undo()


if __name__ == "__main__":
    main()
