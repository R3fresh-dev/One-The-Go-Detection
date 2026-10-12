"""Fresh three-principal scope closure and retained seal logic, not live WORM."""

from copy import deepcopy
import io

import pytest

from otgd import recovery_scopes as r
from otgd.canonical import canonical, digest
from otgd.db import Account, SystemState, factory, iso, now
from otgd.domain import save_record
from otgd.errors import Problem
from .governance_fixture import approve, study, STUDY


class Retained:
    def __init__(self):
        self.values = {}
        self.replaced = False

    def put(self, bucket, key, raw, **kwargs):
        assert kwargs["conditional"] is True
        self.values[key] = raw
        return "pinned-software-version"

    def get_paginator(self, name):
        assert name == "list_object_versions"
        return self

    def paginate(self, **kwargs):
        rows = [
            {"Key": key, "VersionId": "pinned-software-version", "IsLatest": True}
            for key in self.values
            if key.startswith(kwargs["Prefix"])
        ]
        if self.replaced and rows:
            rows.append({**rows[0], "VersionId": "overwritten", "IsLatest": False})
        return [{"Versions": rows}]

    def get_object(self, **kwargs):
        assert kwargs["VersionId"] == "pinned-software-version"
        raw = self.values[kwargs["Key"]]
        return {
            "VersionId": kwargs["VersionId"],
            "ContentLength": len(raw),
            "Body": io.BytesIO(raw),
        }


@pytest.fixture
def resumed(client, account, monkeypatch):
    s3 = Retained()
    monkeypatch.setattr(r, "authority_client", lambda: s3)
    monkeypatch.setattr(r, "require_authority", lambda db: 0)
    monkeypatch.setattr("otgd.storage.put_versioned", s3.put)
    cutoff = now() - 20
    state = {
        "verified": True,
        "scopes_suspended": True,
        "recovery_id": "fictional-recovery",
        "authentication_cutoff": cutoff,
        "journal_activation": {
            "key": "recovery/fictional.json",
            "version_id": "original",
            "sha256": "a" * 64,
        },
    }
    with factory().begin() as db:
        doc = study(account)
        doc["channels"] = {}
        approve(db, "study", doc)
        db.add(SystemState(key="recovery", body=state))
        save_record(
            db,
            db.get(Account, account),
            "consent",
            STUDY,
            {
                "state": "active",
                "accepted_at": iso(),
                "invitation_id": doc["invitation_id"],
                "document_version": doc["document_version"],
                "document_sha256": doc["document_sha256"],
            },
        )
    return account, s3, state


def test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent(
    resumed,
):
    account, s3, state = resumed
    with factory().begin() as db:
        with pytest.raises(Problem):
            r.require_study_scope(db, STUDY, db.get(Account, account))
        receipt = r.seal_study(db, STUDY, "local:fixture-releaser")
        assert receipt["global_scopes_suspended"] is True
        r.require_study_scope(db, STUDY, db.get(Account, account))
        assert db.get(SystemState, "recovery").body["scopes_suspended"] is True
        with pytest.raises(Problem):
            r.require_study_scope(db, "another-study")
        key = receipt["seal"]["key"]
        assert canonical(__import__("json").loads(s3.values[key])) == s3.values[key]


@pytest.mark.parametrize(
    "change",
    [
        "stale_approval",
        "stale_consent",
        "database_bool",
        "foreign_recovery",
        "scope_hash",
        "foreign_account",
        "latest_scope",
        "overwrite",
        "deleted_seal",
    ],
)
def test_no_stale_or_mutated_authority_reopens_study(resumed, change):
    account, s3, state = resumed
    with factory().begin() as db:
        receipt = r.seal_study(db, STUDY, "local:fixture-releaser")
        key = receipt["seal"]["key"]
        body = __import__("json").loads(s3.values[key])
        if change == "stale_approval":
            db.get(SystemState, "recovery").body = {
                **state,
                "authentication_cutoff": now() + 1,
            }
        elif change == "stale_consent":
            row = db.get(
                __import__("otgd.db", fromlist=["Record"]).Record,
                account + ":consent:" + STUDY,
            )
            row.body = {
                **row.body,
                "accepted_at": iso(state["authentication_cutoff"] - 1),
            }
        elif change == "database_bool":
            db.get(SystemState, "recovery").body = {**state, "scopes_suspended": False}
        elif change == "foreign_recovery":
            body["recovery_id"] = "other"
        elif change == "scope_hash":
            body["references_sha256"] = "0" * 64
        elif change == "foreign_account":
            body["account"] = "other"
        elif change == "latest_scope":
            body = deepcopy(body)
            body.update(seal_id="later", sealed_at=iso(now() + 1), references=[])
            body["references_sha256"] = digest([])
            s3.values[r.prefix(state["recovery_id"], STUDY) + "later.json"] = canonical(
                body
            )
        elif change == "overwrite":
            s3.replaced = True
        else:
            s3.values.clear()
        if change in ("foreign_recovery", "scope_hash", "foreign_account"):
            s3.values[key] = canonical(body)
        with pytest.raises(Problem) as denied:
            r.require_study_scope(db, STUDY, db.get(Account, account))
        assert denied.value.code == "RECOVERED_SCOPE_SUSPENDED"


def test_unrestored_database_needs_no_seal_and_false_claim_cannot_seal(client, account):
    with factory().begin() as db:
        r.require_study_scope(db, STUDY)
        db.add(SystemState(key="recovery", body={"verified": False}))
        with pytest.raises(Problem) as denied:
            r.seal_study(db, STUDY, "local:fixture")
        assert denied.value.code == "RECOVERY_NOT_SUSPENDED"
