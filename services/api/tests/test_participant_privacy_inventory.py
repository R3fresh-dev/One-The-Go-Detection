"""Export inventory regression; fictional rows and explicitly mocked object storage.

This tests custody/selection independently of the collection admission tests.
It makes no assertion of genuine instruction or laboratory approval.
"""

import io
import zipfile
from uuid import uuid4

from otgd.canonical import digest, strict_loads
from otgd.db import Account, Record, factory
from otgd.domain import rec_id
from otgd.worker import run_job

from .conftest import headers
from .helpers import upload
from .test_api import finalize, store


def test_export_preserves_all_owned_preparation_and_collection_records(
    client, account, store
):
    snapshot, _, manifest = upload(client, account)
    session_id = snapshot["session_id"]
    finalize(client, snapshot, manifest)
    foreign = client.get("/v1/me/capabilities", headers=headers("b")).json()[
        "account_ref"
    ]
    expected = {"instruction_receipts": [], "collections": [], "collection_abandons": []}
    with factory().begin() as db:
        for kind, key in (
            ("instruction_receipt", "instruction_receipts"),
            ("collection", "collections"),
            ("collection_abandon", "collection_abandons"),
        ):
            # Include earlier/unselected acknowledgments and invalid attempts,
            # not just the receipt referenced by the selected valid attempt.
            for disposition in ("earlier", "selected", "invalid"):
                identifier = str(uuid4())
                body = {"fixture_id": identifier, "fixture_disposition": disposition}
                db.add(Record(
                    id=rec_id(db.get(Account, account), kind, identifier), account_id=account,
                    generation=1, kind=kind, parent_id=session_id,
                    body=body, sha256=digest(body),
                ))
                expected[key].append(body)
            for owner, generation, parent in (
                (foreign, 1, session_id),
                (account, 0, session_id),
                (account, 1, str(uuid4())),
            ):
                identifier = str(uuid4())
                body = {"private_neighbor": identifier}
                db.add(Record(
                    id=rec_id(db.get(Account, owner), kind, identifier), account_id=owner,
                    generation=generation, kind=kind, parent_id=parent,
                    body=body, sha256=digest(body),
                ))

    response = client.post("/v1/privacy/exports", headers=headers(), json={
        "selection": {"kind": "single", "session_ids": [session_id]},
        "format": "json_zip", "include_raw": False,
    })
    assert response.status_code == 202, response.text
    job_id = response.json()["job_id"]
    assert run_job(job_id) == "completed"
    status = client.get("/v1/privacy/jobs/" + job_id, headers=headers()).json()
    response = client.get(status["download_path"], headers=headers())
    assert response.status_code == 200, response.text
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        body = strict_loads(archive.read(f"checks/{session_id}.json"))
        for key, records in expected.items():
            assert {digest(record) for record in body[key]} == {
                digest(record) for record in records
            }
        assert len(body["attempts"]) == 4

    assert client.get(status["download_path"], headers=headers("b")).status_code == 404
