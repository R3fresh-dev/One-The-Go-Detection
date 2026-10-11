"""Deterministic interleavings; the same cases also execute against CI PostgreSQL."""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from otgd import main, storage, worker
from otgd.canonical import strict_loads
from otgd.db import Account, Artifact, Job, Outbox, factory, now
from .conftest import headers
from .helpers import upload


def test_deletion_between_authorization_passes_refreshes_account(
    client, account, monkeypatch
):
    original = main.authenticate
    calls = 0

    def racing_authenticate(db, authorization, receipt=False):
        nonlocal calls
        calls += 1
        if calls == 2:
            with factory().begin() as other:
                row = other.get(Account, account)
                row.generation = 2
                row.state = "deleting"
        return original(db, authorization, receipt)

    monkeypatch.setattr(main, "authenticate", racing_authenticate)
    response = client.post(
        "/v1/sessions",
        headers=headers(),
        json={"session_id": str(uuid4()), "mode": "synthetic"},
    )
    assert response.status_code == 410, response.text
    assert response.json()["code"] == "DATA_GENERATION_RETIRED"


def test_waiting_worker_refreshes_job_after_other_claim(client, account, monkeypatch):
    job_id = str(uuid4())
    with factory().begin() as db:
        db.add(
            Job(
                id=job_id,
                account_id=account,
                generation=1,
                kind="result",
                state="pending",
                body={"session_id": str(uuid4())},
            )
        )
    original = Session.scalar
    injected = False
    competing = []

    def interleaved_scalar(session, statement, *args, **kwargs):
        nonlocal injected
        descriptions = getattr(statement, "column_descriptions", [])
        if not injected and descriptions and descriptions[0].get("entity") is Account:
            # Outer claimant has cached Job.pending, but has not acquired its account lock.
            injected = True
            competing.append(worker.claim_job(job_id))
        return original(session, statement, *args, **kwargs)

    monkeypatch.setattr(Session, "scalar", interleaved_scalar)
    waiting = worker.claim_job(job_id)
    assert competing[0] is not None and competing[0].fence == 1
    assert waiting is None
    with factory()() as db:
        job = db.get(Job, job_id)
        assert (job.fence, job.attempts, job.state) == (1, 1, "running")


def test_terminal_outbox_rows_cannot_starve_eligible_job(client, account, monkeypatch):
    eligible = str(uuid4())
    with factory().begin() as db:
        for i in range(27):
            job_id = eligible if i == 26 else str(uuid4())
            db.add(
                Job(
                    id=job_id,
                    account_id=account,
                    generation=1,
                    kind="result",
                    state="pending" if i == 26 else "failed",
                    body={},
                )
            )
            db.flush()
            db.add(Outbox(job_id=job_id, available=now() - 1000 + i))
    sent = []

    class Sqs:
        def send_message(self, **kwargs):
            sent.append(strict_loads(kwargs["MessageBody"])["job_id"])

    monkeypatch.setattr(storage, "client", lambda *args, **kwargs: Sqs())
    worker.dispatch_once()
    assert sent == [eligible]


def test_unmanaged_expired_artifact_is_denied_before_storage_verification(
    client, account, monkeypatch
):
    snapshot, _, _ = upload(client, account)
    artifact_id = str(uuid4())
    with factory().begin() as db:
        db.add(
            Artifact(
                id=artifact_id,
                account_id=account,
                generation=1,
                session_id=snapshot["session_id"],
                bucket="test",
                key="quarantine/fixture",
                sha256="a" * 64,
                size=12,
                media_type="application/pdf",
                kind="source_lab_report",
                state="quarantine",
                expires=now() - 3600,
                scope={},
            )
        )

    def verify_then_cleanup(_artifact):
        raise AssertionError("Unmanaged raw data must never reach storage verification")

    monkeypatch.setattr(storage, "verify_artifact", verify_then_cleanup)
    response = client.post(
        f"/v1/artifact-uploads/{artifact_id}/complete",
        headers=headers(),
        json={"sha256": "a" * 64, "size_bytes": 12, "media_type": "application/pdf"},
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "RAW_RETENTION_WINDOW_CLOSED"
    with factory()() as db:
        artifact = db.get(Artifact, artifact_id)
        assert artifact.state == "quarantine" and artifact.version_id is None
