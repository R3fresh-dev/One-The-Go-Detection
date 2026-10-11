"""Exact approved-version consent, historical receipts and operator retirement."""
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import uuid4

import pytest
from sqlalchemy import select, text, update

from otgd import main
from otgd.canonical import digest
from otgd.db import Account, Check, Record, Registry, engine, factory, iso, now
from otgd.domain import qualification, record
from otgd.errors import Problem
from .conftest import headers

STUDY = "fictional-consent-software-test-with-name-longer-than-a-session-uuid"


def document(account, version="v1", invitation="invitation-1", text="Fictional test document"):
    return {
        "study_id": STUDY, "account_refs": [account], "name": "Fictional software fixture",
        "invitation_id": invitation, "document_version": version,
        "document_sha256": hashlib.sha256(text.encode()).hexdigest(), "document_text": text,
        "retention_summary": "Software fixture only; no real study approval",
    }


def approve(value):
    with factory().begin() as db:
        db.merge(Registry(id="study:" + STUDY, kind="study", active=True, body=value))


def acceptance(value, **overrides):
    return {k: value[k] for k in ("invitation_id", "document_version", "document_sha256")} | {
        "accepted": True, "acknowledged_at": iso(), **overrides,
    }


def submit(client, value, h=None):
    return client.post(f"/v1/studies/{STUDY}/consents", headers=h or headers(), json=value)


def test_updated_document_has_new_immutable_receipt_and_replay_keeps_current_pointer(client, account):
    initial = document(account)
    approve(initial)
    h = headers(key="accepted-initial-version")
    body = acceptance(initial)
    first = submit(client, body, h)
    assert first.status_code == 201, first.text
    receipt = first.json()
    assert receipt["acknowledged_at"] == body["acknowledged_at"] and receipt["accepted_at"]
    assert submit(client, acceptance(initial)).status_code == 409
    updated = document(account, "v2", text="New fictional reviewed document")
    approve(updated)
    assert submit(client, body).status_code == 403
    second = submit(client, acceptance(updated))
    assert second.status_code == 201, second.text
    assert second.json()["consent_record_id"] != receipt["consent_record_id"]
    assert submit(client, body, h).json() == receipt
    with factory()() as db:
        owner = db.get(Account, account)
        pointer = record(db, owner, "consent", STUDY)
        assert pointer.body == second.json() and pointer.revision == 2
        old = record(db, owner, "consent_receipt", receipt["consent_record_id"])
        assert old.body == receipt and old.sha256 == digest(receipt)
        assert record(db, owner, "consent_receipt", second.json()["consent_record_id"]).body == second.json()
    assert client.get("/v1/me/studies", headers=headers()).json()["items"][0]["consent"] == second.json()


def test_same_text_new_version_or_invitation_requires_current_exact_consent(client, account):
    original = document(account)
    approve(original)
    assert submit(client, acceptance(original)).status_code == 201
    for changed in (document(account, version="v2"), document(account, version="v2", invitation="invitation-2")):
        approve(changed)
        with factory()() as db:
            owner = db.get(Account, account)
            with pytest.raises(Problem) as denied:
                qualification(db, owner, Check(id=str(uuid4()), study_id=STUDY), "task")
            assert denied.value.code == "CURRENT_CONSENT_REQUIRED"
        assert submit(client, acceptance(changed)).status_code == 201


def test_withdrawal_does_not_rewrite_original_acceptance_receipt(client, account):
    first_doc = document(account)
    approve(first_doc)
    accepted = submit(client, acceptance(first_doc)).json()
    assert client.post(f"/v1/studies/{STUDY}/withdrawals", headers=headers(), json={"confirmation": True}).status_code == 200
    assert submit(client, acceptance(first_doc)).status_code == 409
    new_document_same_invitation = document(account, version="v2", text="Changed fictional document")
    approve(new_document_same_invitation)
    denied = submit(client, acceptance(new_document_same_invitation))
    assert denied.status_code == 403 and denied.json()["code"] == "STUDY_REINVITATION_REQUIRED"
    with factory()() as db:
        owner = db.get(Account, account)
        assert record(db, owner, "consent", STUDY).body["state"] == "withdrawn"
        assert record(db, owner, "consent_receipt", accepted["consent_record_id"]).body == accepted
    reinvited = document(account, version="v2", invitation="coordinator-new-invitation", text="Changed fictional document")
    approve(reinvited)
    assert submit(client, acceptance(reinvited)).status_code == 201


@pytest.mark.parametrize("invalid", [{"acknowledged_at": iso(now()+60)}, {"acknowledged_at": "1969-01-01T00:00:00.000Z"}, {"accepted": False}])
def test_future_negative_or_unconfirmed_acknowledgment_is_rejected(client, account, invalid):
    value = document(account)
    approve(value)
    assert submit(client, acceptance(value, **invalid)).status_code == 422
    with factory()() as db:
        assert not db.scalar(select(Record).where(Record.kind == "consent_receipt"))


def test_queued_confirmation_keeps_actual_past_time_if_approved_document_remains_current(client, account):
    value = document(account)
    approve(value)
    past = iso(now()-86400)
    response = submit(client, acceptance(value, acknowledged_at=past))
    assert response.status_code == 201 and response.json()["acknowledged_at"] == past
    assert submit(client, acceptance(value), headers("foreign")).status_code == 403


@pytest.mark.postgres
def test_actual_postgresql_consent_commit_serializes_operator_retirement(client, account, monkeypatch):
    if engine().dialect.name != "postgresql":
        pytest.skip("Actual PostgreSQL required for registry row-lock evidence")
    value = document(account)
    approve(value)
    acquired, release, retiring = Event(), Event(), Event()
    retirement_pid = []
    original = main.save_record

    def pause_after_registry_lock(db, owner, kind, key, data, **options):
        if kind == "consent":
            acquired.set()
            assert release.wait(3), "Test request never released"
        return original(db, owner, kind, key, data, **options)

    def retire():
        with factory().begin() as db:
            retirement_pid.append(db.scalar(text("SELECT pg_backend_pid()")))
            retiring.set()
            db.execute(update(Registry).where(Registry.id == "study:"+STUDY).values(active=False))

    monkeypatch.setattr(main, "save_record", pause_after_registry_lock)
    with ThreadPoolExecutor(max_workers=2) as pool:
        request = pool.submit(submit, client, acceptance(value))
        assert acquired.wait(3)
        retirement = pool.submit(retire)
        assert retiring.wait(3)
        try:
            deadline = time.monotonic() + 1
            observed_wait = False
            while time.monotonic() < deadline:
                with factory()() as db:
                    observed_wait = db.scalar(text("SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE pid=:pid AND wait_event_type='Lock')"), {"pid": retirement_pid[0]})
                if observed_wait:
                    break
                time.sleep(.01)
            assert observed_wait and not retirement.done(), "Operator retirement must wait for accepted consent transaction"
        finally:
            release.set()
        assert request.result(timeout=5).status_code == 201
        retirement.result(timeout=5)
    assert submit(client, acceptance(value)).status_code == 403
