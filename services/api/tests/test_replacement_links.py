"""Physical replacement navigation, scope isolation and pagination regressions."""

import base64
from copy import deepcopy
from uuid import uuid4

import pytest
from sqlalchemy import inspect, select

from otgd.canonical import canonical, digest
from otgd.db import Account, Check, SystemState, engine, factory
from otgd.migrate import migrate

from .conftest import headers
from .helpers import session_fixture, upload


def seed(account, parent=None, state="completed", generation=1, created=1700000000.0):
    snapshot = session_fixture(account)
    snapshot["supersedes_session_id"] = parent
    with factory().begin() as db:
        db.add(
            Check(
                id=snapshot["session_id"],
                account_id=account,
                generation=generation,
                state=state,
                mode=snapshot["mode"],
                protocol_id=snapshot["protocol_id"],
                supersedes_id=parent,
                snapshot=snapshot,
                snapshot_sha256=digest(snapshot),
                created=created,
            )
        )
    return snapshot


def url(snapshot):
    return f"/v1/sessions/{snapshot['session_id']}/replacement-links"


def read(client, snapshot, **params):
    return client.get(url(snapshot), headers=headers(), params=params)


def test_uploaded_draft_is_unavailable_until_finalization_freezes_it(client, account):
    snapshot, _context, manifest = upload(client, account)
    assert read(client, snapshot).status_code == 409
    result = client.post(
        f"/v1/sessions/{snapshot['session_id']}/finalize",
        headers=headers(revision=2),
        json={"snapshot_sha256": digest(snapshot), "evidence_sha256": digest(manifest)},
    )
    assert result.status_code == 202, result.text
    response = read(client, snapshot)
    assert response.status_code == 200, response.text
    assert response.json() == {
        "schema_version": "1.0.0",
        "session_id": snapshot["session_id"],
        "data_generation": 1,
        "base_snapshot_sha256": digest(snapshot),
        "previous": None,
        "items": [],
        "next_cursor": None,
    }


def test_bidirectional_links_are_direct_frozen_and_bound_to_acquisition_times(client, account):
    original = seed(account)
    replacement = seed(account, original["session_id"], "processing", created=1700000040)
    descendant = seed(account, replacement["session_id"], "invalid", created=1700000070)
    seed(account, original["session_id"], "draft", created=1800000000)
    seed(account, original["session_id"], generation=2)
    first = read(client, original).json()
    assert [item["session_id"] for item in first["items"]] == [replacement["session_id"]]
    linked = read(client, replacement).json()
    assert linked["previous"] == {
        "session_id": original["session_id"],
        "created_at": original["created_at"],
        "state": "completed",
    }
    assert linked["items"] == [{
        "session_id": descendant["session_id"],
        "created_at": descendant["created_at"],
        "state": "invalid",
    }]
    assert linked["items"][0]["created_at"] != "2023-11-14T22:14:30.000Z"


def test_tied_keyset_pages_have_no_duplicates_and_ignore_newer_insert(client, account):
    original = seed(account)
    children = [seed(account, original["session_id"]) for _ in range(5)]
    expected = sorted((row["session_id"] for row in children), reverse=True)
    first = read(client, original, limit=2).json()
    assert [item["session_id"] for item in first["items"]] == expected[:2]
    assert first["next_cursor"]
    seed(account, original["session_id"], created=1800000000)
    second = read(client, original, limit=2, cursor=first["next_cursor"]).json()
    last = read(client, original, limit=2, cursor=second["next_cursor"]).json()
    assert [item["session_id"] for item in second["items"] + last["items"]] == expected[2:]
    assert last["next_cursor"] is None


def test_owner_and_retired_generation_do_not_disclose_links(client, account):
    original = seed(account)
    child = seed(account, original["session_id"])
    foreign = client.get("/v1/me/capabilities", headers=headers(sub="b")).json()["account_ref"]
    seed(foreign, original["session_id"])
    assert len(read(client, original).json()["items"]) == 1
    denied = client.get(url(original), headers=headers(sub="b"))
    assert denied.status_code == 404
    assert child["session_id"] not in denied.text
    with factory().begin() as db:
        owner = db.get(Account, account)
        owner.generation = 2
    assert read(client, original).status_code == 404


def test_cursor_is_bound_to_parent_and_generation(client, account):
    original = seed(account)
    other = seed(account)
    for _ in range(2):
        seed(account, original["session_id"])
    cursor = read(client, original, limit=1).json()["next_cursor"]
    wrong_parent = read(client, other, cursor=cursor)
    assert wrong_parent.status_code == 422
    assert wrong_parent.json()["code"] == "INVALID_CURSOR"
    wrong_generation = base64.urlsafe_b64encode(canonical({
        "scope": digest([account, 2, original["session_id"]]),
        "created": 1700000000,
        "id": str(uuid4()),
    })).decode().rstrip("=")
    assert read(client, original, cursor=wrong_generation).status_code == 422


@pytest.mark.parametrize("cursor", ["", "!", "a" * 1025, "e30", "bnVsbA", "//==", "é"])
def test_malformed_and_oversized_cursors_are_rejected(client, account, cursor):
    response = read(client, seed(account), cursor=cursor)
    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_CURSOR"


@pytest.mark.parametrize("limit", [0, -1, 101, "true"])
def test_page_bounds(client, account, limit):
    assert read(client, seed(account), limit=limit).status_code == 422


def test_corrupt_snapshot_relation_is_not_replaced_with_plausible_link(client, account):
    original = seed(account)
    child = seed(account, original["session_id"])
    with factory().begin() as db:
        row = db.get(Check, child["session_id"])
        corrupt = deepcopy(row.snapshot)
        corrupt["supersedes_session_id"] = str(uuid4())
        row.snapshot = corrupt
        row.snapshot_sha256 = digest(corrupt)
    response = read(client, original)
    assert response.status_code == 409
    assert response.json()["code"] == "REPLACEMENT_LINK_INTEGRITY"
    assert child["session_id"] not in response.text


def test_removed_predecessor_is_unavailable_without_rewriting_child(client, account):
    original = seed(account)
    child = seed(account, original["session_id"])
    with factory().begin() as db:
        db.delete(db.get(Check, original["session_id"]))
    response = read(client, child)
    assert response.status_code == 200
    assert response.json()["previous"] is None
    assert response.json()["base_snapshot_sha256"] == digest(child)


def test_numbered_replacement_index_migration_replays_without_evidence_changes(client, account, monkeypatch):
    from .journal_fixture import inject_marker
    inject_marker(monkeypatch)
    original = seed(account)
    migrate()
    migrate()
    with factory()() as db:
        assert db.get(Check, original["session_id"]).snapshot == original
        stamp = db.scalar(select(SystemState).where(SystemState.key == "migration:002_replacement_navigation"))
        assert stamp.body["migration"] == 2
    index = next(item for item in inspect(engine()).get_indexes("checks") if item["name"] == "ix_checks_owner_replacement_page")
    assert index["column_names"] == ["account_id", "generation", "supersedes_id", "created", "id"]
