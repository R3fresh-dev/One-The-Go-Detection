"""Actual owned HTTP keyset pagination; SQLite account fixture, no cloud claim."""

import base64
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from otgd.canonical import digest
from otgd.config import settings
from otgd.db import Account, Check, factory

from .conftest import headers
from .helpers import upload


def seed(owner, *, count=5, generation=1):
    identities = [str(uuid4()) for _ in range(count)]
    with factory().begin() as db:
        db.add_all(
            Check(
                id=identity,
                account_id=owner,
                generation=generation,
                mode="synthetic",
                created=1700000000,
                state="draft",
            )
            for identity in identities
        )
    return sorted(identities, reverse=True)


def page(client, *, subject="a", generation=1, **params):
    return client.get(
        "/v1/sessions", headers=headers(sub=subject, gen=generation), params=params
    )


def decoded(cursor):
    return json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))


def denied(response):
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INVALID_CURSOR"
    assert "items" not in response.json()


def test_history_cursor_cannot_be_replayed_for_a_foreign_owner(client, account):
    seed(account)
    cursor = page(client, limit=2).json()["next_cursor"]
    foreign = client.get("/v1/me/capabilities", headers=headers(sub="b")).json()[
        "account_ref"
    ]
    expected = seed(foreign, count=2)
    denied(page(client, subject="b", cursor=cursor))
    assert [
        row["session_id"] for row in page(client, subject="b").json()["items"]
    ] == expected


def test_retired_generation_cursor_is_not_an_admitted_current_boundary(client, account):
    seed(account)
    cursor = page(client, limit=2).json()["next_cursor"]
    with factory().begin() as db:
        db.get(Account, account).generation = 2
    expected = seed(account, count=2, generation=2)
    denied(page(client, generation=2, cursor=cursor))
    assert [
        row["session_id"] for row in page(client, generation=2).json()["items"]
    ] == expected


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", "ffffffff-ffff-4fff-8fff-ffffffffffff"),
        ("created", 1699999999),
        ("created", True),
        ("created", "1700000000"),
        ("created", 0),
        ("created", -1),
        ("created", 9007199254740992),
        ("scope", "0" * 64),
        ("mac", "0" * 64),
        ("id", "not-a-uuid"),
    ],
)
def test_forged_position_scope_or_authenticator_is_refused(
    client, account, field, value
):
    seed(account)
    payload = decoded(page(client, limit=2).json()["next_cursor"])
    payload[field] = value
    # json.dumps deliberately permits the unsafe integer test that JCS refuses.
    cursor = (
        base64.urlsafe_b64encode(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        )
        .decode()
        .rstrip("=")
    )
    denied(page(client, cursor=cursor))


@pytest.mark.parametrize(
    "cursor",
    [
        "",
        "!",
        "a" * 1025,
        "e30",
        "bnVsbA",
        "//==",
        "é",
        base64.urlsafe_b64encode(b'{"id":"x","created":NaN}').decode().rstrip("="),
        base64.urlsafe_b64encode(b'{"id":"x","created":Infinity}').decode().rstrip("="),
        base64.urlsafe_b64encode(b'{"id":"x","created":1,"created":2}')
        .decode()
        .rstrip("="),
    ],
)
def test_history_cursor_strict_bounded_parser_refuses_malformed_input(
    client, account, cursor
):
    seed(account, count=1)
    denied(page(client, cursor=cursor))


def test_cursor_environment_and_sort_are_bound_even_with_authentic_mac(
    client, account, monkeypatch
):
    from otgd import history_cursor

    seed(account)
    with factory()() as db:
        owner = db.get(Account, account)
        boundary = db.query(Check).filter_by(account_id=account).first()
        cursor = history_cursor.encode_cursor(
            owner, boundary, settings().model_copy(update={"environment": "local"})
        )
        with monkeypatch.context() as changed_sort:
            changed_sort.setattr(
                history_cursor, "SORT", "created_at ASC,session_id ASC"
            )
            differently_sorted = history_cursor.encode_cursor(
                owner, boundary, settings()
            )
    denied(page(client, cursor=cursor))
    denied(page(client, cursor=differently_sorted))


def test_cursor_authenticator_has_no_missing_key_fallback(client, account):
    from otgd.errors import Problem
    from otgd.history_cursor import encode_cursor

    seed(account, count=1)
    with factory()() as db:
        owner = db.get(Account, account)
        boundary = db.query(Check).filter_by(account_id=account).first()
        with pytest.raises(Problem, match="IDENTITY_KEY_UNAVAILABLE"):
            encode_cursor(
                owner, boundary, settings().model_copy(update={"tombstone_key": ""})
            )


@pytest.mark.parametrize(
    "change",
    [
        "deleted",
        "changed_timestamp",
        "nonexistent_signed",
        "foreign_signed",
        "retired_boundary",
    ],
)
def test_signed_cursor_still_requires_an_actual_unchanged_owned_boundary(
    client, account, change
):
    from otgd.history_cursor import encode_cursor

    seed(account)
    cursor = page(client, limit=2).json()["next_cursor"]
    payload = decoded(cursor)
    with factory().begin() as db:
        owner = db.get(Account, account)
        boundary = db.get(Check, payload["id"])
        if change == "deleted":
            db.delete(boundary)
        elif change == "changed_timestamp":
            boundary.created += 1
        elif change == "nonexistent_signed":
            cursor = encode_cursor(
                owner,
                SimpleNamespace(id=str(uuid4()), created=boundary.created),
                settings(),
            )
        elif change == "retired_boundary":
            boundary.generation += 1
        else:
            foreign = Account(id=str(uuid4()), subject_hash="a" * 64)
            db.add(foreign)
            db.flush()
            boundary.account_id = foreign.id
    denied(page(client, cursor=cursor))


def test_new_finalized_check_does_not_shift_existing_tied_pages_and_appears_on_refresh(
    client, account
):
    expected = seed(account)
    first = page(client, limit=2)
    assert first.status_code == 200, first.text
    first = first.json()
    assert [row["session_id"] for row in first["items"]] == expected[:2]
    snapshot, _, manifest = upload(client, account)
    finalized = client.post(
        f"/v1/sessions/{snapshot['session_id']}/finalize",
        headers=headers(revision=2),
        json={
            "snapshot_sha256": digest(snapshot),
            "evidence_sha256": digest(manifest),
        },
    )
    assert finalized.status_code == 202, finalized.text
    second = page(client, limit=2, cursor=first["next_cursor"])
    assert second.status_code == 200, second.text
    second = second.json()
    last = page(client, limit=2, cursor=second["next_cursor"])
    assert last.status_code == 200, last.text
    all_ids = [
        row["session_id"]
        for row in first["items"] + second["items"] + last.json()["items"]
    ]
    assert all_ids == expected and len(all_ids) == len(set(all_ids))
    assert last.json()["next_cursor"] is None
    refreshed = page(client).json()["items"]
    assert (
        refreshed[0]["session_id"] == snapshot["session_id"]
        and refreshed[0]["state"] == "processing"
    )
    assert [row["session_id"] for row in refreshed[1:]] == expected
