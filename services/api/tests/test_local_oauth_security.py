"""Fictional issuer HTTP/DB security boundaries, separate from cloud Cognito."""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
from threading import Barrier, Event
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi.testclient import TestClient
import jwt
import pytest
from sqlalchemy import select, text

from otgd import auth, local_oauth_state, worker
from otgd.db import Account, Job, OAuthRecord, engine, factory, iso, now, uid
from .test_local_identity import (
    authorization,
    exchange,
    issuer as issuer,
    refresh,
    select_account,
)


def choice(api, module, ident, account="fixture_a", origin=None):
    headers = (
        {"Origin": module.s.identity_origin.rstrip("/")} if origin is None else origin
    )
    return api.post(
        "/oauth2/authorize",
        headers=headers,
        data={"authorization_id": ident, "account": account},
    )


def enable_local_api(module, monkeypatch):
    monkeypatch.setattr(auth, "settings", lambda: module.s)
    monkeypatch.setattr(auth.verifier, "keys", {"local-v1": module.key().public_key()})
    monkeypatch.setattr(auth.verifier, "expires", time.monotonic() + 3600)


def test_chooser_requires_exact_origin_and_originating_http_only_browser_session(
    issuer,
):
    api, module = issuer
    page, _ = authorization(api, module)
    assert (
        "HttpOnly" in page.headers["set-cookie"]
        and "SameSite=lax" in page.headers["set-cookie"]
    )
    ident = re.search(r'name="authorization_id" value="([^"]+)"', page.text).group(1)
    for headers in [{}, {"Origin": "null"}, {"Origin": "https://attacker.invalid"}]:
        assert choice(api, module, ident, origin=headers).status_code == 400
    with TestClient(module.app, follow_redirects=False) as outsider:
        assert choice(outsider, module, ident).status_code == 400
        authorization(outsider, module)
        assert choice(outsider, module, ident).status_code == 400
    assert choice(api, module, ident).status_code == 303
    assert choice(api, module, ident).status_code == 400


@pytest.mark.parametrize(
    "variant",
    [
        "symlink",
        "fifo",
        "public",
        "oversize",
        "ec",
        "weak_rsa",
        "hardlink",
        "foreign_owner",
    ],
)
def test_local_signing_key_reads_reject_unsafe_files_and_algorithms(
    issuer, tmp_path, monkeypatch, variant
):
    _, module = issuer
    module.key()
    original = Path(module.s.local_signing_key_path)
    candidate = tmp_path / "candidate.pem"
    if variant == "symlink":
        candidate.symlink_to(original)
    elif variant == "fifo":
        os.mkfifo(candidate, 0o600)
    elif variant == "hardlink":
        os.link(original, candidate)
    else:
        if variant in ["ec", "weak_rsa"]:
            private = (
                ec.generate_private_key(ec.SECP256R1())
                if variant == "ec"
                else rsa.generate_private_key(public_exponent=65537, key_size=1024)
            )
            data = private.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        else:
            data = (
                b"x" * (module.MAX_KEY_BYTES + 1)
                if variant == "oversize"
                else original.read_bytes()
            )
        candidate.write_bytes(data)
        candidate.chmod(0o644 if variant == "public" else 0o600)
    if variant == "foreign_owner":
        actual_uid = os.geteuid()
        monkeypatch.setattr(module.os, "geteuid", lambda: actual_uid + 1)
    monkeypatch.setattr(module.s, "local_signing_key_path", str(candidate))
    with pytest.raises((OSError, RuntimeError, ValueError)):
        module.key()


def test_refresh_rotation_has_fixed_absolute_family_deadline(issuer, monkeypatch):
    api, module = issuer
    clock = [now()]
    monkeypatch.setattr(module, "now", lambda: clock[0])
    monkeypatch.setattr(local_oauth_state, "now", lambda: clock[0])
    code, verifier, _ = select_account(api, module)
    first = exchange(api, module, code, verifier).json()
    with factory()() as db:
        deadline = db.get(OAuthRecord, module.sha(first["refresh_token"])).expires
    assert deadline == clock[0] + local_oauth_state.FAMILY_SECONDS
    clock[0] += 86400
    rotated = refresh(api, module, first["refresh_token"])
    assert rotated.status_code == 200
    with factory()() as db:
        assert (
            db.get(OAuthRecord, module.sha(rotated.json()["refresh_token"])).expires
            == deadline
        )
    clock[0] = deadline
    assert refresh(api, module, rotated.json()["refresh_token"]).status_code == 400


def test_spent_refresh_revokes_entire_family_before_first_api_account_use(
    issuer, client, monkeypatch
):
    api, module = issuer
    enable_local_api(module, monkeypatch)
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    rotated = refresh(api, module, initial["refresh_token"]).json()
    assert refresh(api, module, initial["refresh_token"]).status_code == 400
    assert refresh(api, module, rotated["refresh_token"]).status_code == 400
    for token in [initial["access_token"], rotated["access_token"]]:
        assert (
            client.get(
                "/v1/me/capabilities", headers={"Authorization": "Bearer " + token}
            ).status_code
            == 401
        )
    with factory()() as db:
        assert list(db.scalars(select(Account))) == []


def test_api_logout_blocks_refresh_but_retains_exact_own_logout_receipt(
    issuer, client, monkeypatch
):
    api, module = issuer
    enable_local_api(module, monkeypatch)
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    headers = {
        "Authorization": "Bearer " + initial["access_token"],
        "X-Data-Generation": "1",
        "Idempotency-Key": "local-logout-receipt",
    }
    assert client.get("/v1/me/capabilities", headers=headers).status_code == 200
    receipt = client.post("/v1/auth/logout", headers=headers, json={})
    assert receipt.status_code == 200
    assert refresh(api, module, initial["refresh_token"]).status_code == 400
    assert client.get("/v1/me/capabilities", headers=headers).status_code == 401
    assert (
        client.post("/v1/auth/logout", headers=headers, json={}).json()
        == receipt.json()
    )


def test_unknown_or_cross_subject_local_family_cannot_provision_an_account(
    issuer, client, monkeypatch
):
    api, module = issuer
    enable_local_api(module, monkeypatch)
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    claims = jwt.decode(initial["access_token"], options={"verify_signature": False})
    for change in [{"origin_jti": "unknown-family"}, {"sub": "local-fixture_b"}]:
        altered = jwt.encode(
            {**claims, **change},
            module.key(),
            algorithm="RS256",
            headers={"kid": "local-v1"},
        )
        assert (
            client.get(
                "/v1/me/capabilities", headers={"Authorization": "Bearer " + altered}
            ).status_code
            == 401
        )
    with factory()() as db:
        assert list(db.scalars(select(Account))) == []


@pytest.mark.parametrize(
    "scope,disabled,state",
    [("account", True, "deleted"), ("all_data", False, "awaiting_generation_ack")],
)
def test_identity_disablement_is_atomic_with_account_deletion_and_not_all_data(
    issuer, client, monkeypatch, scope, disabled, state
):
    api, module = issuer
    enable_local_api(module, monkeypatch)
    monkeypatch.setattr(worker, "settings", lambda: module.s)
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    account_id = client.get(
        "/v1/me/capabilities",
        headers={"Authorization": "Bearer " + initial["access_token"]},
    ).json()["account_ref"]
    body = {"scope": scope, "provider_sub": "local-fixture_a"}
    started = now()
    with factory().begin() as db:
        account = db.get(Account, account_id)
        account.generation, account.state = 2, "deleting"
        job = Job(
            id=uid(),
            account_id=account_id,
            generation=1,
            kind="deletion",
            state="running",
            body=body,
            fence=1,
            attempts=1,
            started=started,
            lease_until=started + 120,
            journal_accepted=True,
        )
        db.add(job)
        ident = job.id
    claim = worker.Claim(ident, account_id, 1, "deletion", 1, started, body)
    worker.commit_output(claim, {"external_cleanup_at": iso()})
    with factory()() as db:
        assert db.get(Account, account_id).state == state
        identity = db.get(OAuthRecord, "identity-" + module.sha("local-fixture_a"))
        assert identity.consumed is disabled
        assert db.get(Job, ident).state == "completed"
    page, _ = authorization(api, module)
    ident = re.search(r'name="authorization_id" value="([^"]+)"', page.text).group(1)
    assert choice(api, module, ident).status_code == (400 if disabled else 303)
    assert refresh(api, module, initial["refresh_token"]).status_code == (
        400 if disabled else 200
    )


def test_expired_cleanup_is_bounded_and_never_expires_disabled_identity(issuer):
    _, module = issuer
    timestamp = now()
    with factory().begin() as db:
        db.add_all(
            [
                OAuthRecord(
                    id=module.sha("expired-" + str(i)),
                    kind="authorization",
                    body={},
                    expires=timestamp - 10,
                )
                for i in range(140)
            ]
        )
        db.add(
            OAuthRecord(
                id="disabled",
                kind="identity",
                body={"sub": "local-fixture_a"},
                expires=0,
                consumed=True,
            )
        )
        db.add(
            OAuthRecord(
                id="active", kind="authorization", body={}, expires=timestamp + 300
            )
        )
    with factory().begin() as db:
        assert local_oauth_state.cleanup_expired(db, timestamp=timestamp) == 128
        assert (
            len(
                list(
                    db.scalars(
                        select(OAuthRecord).where(
                            OAuthRecord.kind == "authorization",
                            OAuthRecord.expires < timestamp,
                        )
                    )
                )
            )
            == 12
        )
        assert db.get(OAuthRecord, "disabled").consumed is True
        assert db.get(OAuthRecord, "active")
        for limit in [0, 129, True]:
            with pytest.raises(ValueError):
                local_oauth_state.cleanup_expired(db, limit=limit)


def test_local_identity_disablement_rolls_back_if_account_deletion_commit_fails(
    issuer, client, monkeypatch
):
    api, module = issuer
    enable_local_api(module, monkeypatch)
    monkeypatch.setattr(worker, "settings", lambda: module.s)
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    account_id = client.get(
        "/v1/me/capabilities",
        headers={"Authorization": "Bearer " + initial["access_token"]},
    ).json()["account_ref"]
    body, started = {"scope": "account", "provider_sub": "local-fixture_a"}, now()
    with factory().begin() as db:
        account = db.get(Account, account_id)
        account.generation, account.state = 2, "deleting"
        job = Job(
            id=uid(),
            account_id=account_id,
            generation=1,
            kind="deletion",
            state="running",
            body=body,
            fence=1,
            attempts=1,
            started=started,
            lease_until=started + 120,
            journal_accepted=True,
        )
        db.add(job)
        ident = job.id
    original = local_oauth_state.disable_local_identity

    def fail_after_disable(db, subject, config):
        original(db, subject, config)
        raise RuntimeError("Injected failure before deletion transaction commits")

    monkeypatch.setattr(local_oauth_state, "disable_local_identity", fail_after_disable)
    with pytest.raises(RuntimeError, match="Injected failure"):
        worker.commit_output(
            worker.Claim(ident, account_id, 1, "deletion", 1, started, body),
            {"external_cleanup_at": iso()},
        )
    with factory()() as db:
        assert db.get(Account, account_id).state == "deleting"
        assert (
            db.get(OAuthRecord, "identity-" + module.sha("local-fixture_a")).consumed
            is False
        )
        assert db.get(Job, ident).state == "running"
    assert refresh(api, module, initial["refresh_token"]).status_code == 200


@pytest.mark.postgres
def test_postgres_simultaneous_refresh_reuse_revokes_the_winning_rotation(issuer):
    assert engine().dialect.name == "postgresql", (
        "Actual PostgreSQL is required for this marked gate"
    )
    api, module = issuer
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    barrier = Barrier(2)

    def rotate():
        barrier.wait(timeout=5)
        return refresh(api, module, initial["refresh_token"])

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [
            future.result(timeout=10)
            for future in [pool.submit(rotate), pool.submit(rotate)]
        ]
    assert sorted(reply.status_code for reply in results) == [200, 400]
    winner = next(reply.json() for reply in results if reply.status_code == 200)
    assert refresh(api, module, winner["refresh_token"]).status_code == 400
    family = jwt.decode(initial["access_token"], options={"verify_signature": False})[
        "origin_jti"
    ]
    with factory()() as db:
        assert db.get(OAuthRecord, local_oauth_state.family_id(family)).consumed is True


@pytest.mark.postgres
def test_postgres_family_admission_is_rechecked_after_delayed_preprovision_read(
    issuer, client, monkeypatch
):
    assert engine().dialect.name == "postgresql", (
        "Actual PostgreSQL is required for this marked gate"
    )
    api, module = issuer
    enable_local_api(module, monkeypatch)
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    read, release = Event(), Event()
    original = local_oauth_state.family_status
    calls = []

    def pause_read(db, family, subject):
        result = original(db, family, subject)
        calls.append(result)
        if len(calls) == 1:
            read.set()
            assert release.wait(5), (
                "Test never released the preprovision admission read"
            )
        return result

    monkeypatch.setattr(local_oauth_state, "family_status", pause_read)
    with ThreadPoolExecutor(max_workers=1) as pool:
        request = pool.submit(
            client.get,
            "/v1/me/capabilities",
            headers={"Authorization": "Bearer " + initial["access_token"]},
        )
        assert read.wait(5)
        try:
            assert refresh(api, module, initial["refresh_token"]).status_code == 200
            assert refresh(api, module, initial["refresh_token"]).status_code == 400
        finally:
            release.set()
        assert request.result(timeout=10).status_code == 401
    assert calls[:2] == [(True, False), (True, True)]
    with factory()() as db:
        assert list(db.scalars(select(Account))) == []


@pytest.mark.postgres
def test_postgres_refresh_waits_for_atomic_account_and_issuer_deletion(
    issuer, client, monkeypatch
):
    assert engine().dialect.name == "postgresql", (
        "Actual PostgreSQL is required for this marked gate"
    )
    api, module = issuer
    enable_local_api(module, monkeypatch)
    monkeypatch.setattr(worker, "settings", lambda: module.s)
    code, verifier, _ = select_account(api, module)
    initial = exchange(api, module, code, verifier).json()
    account_id = client.get(
        "/v1/me/capabilities",
        headers={"Authorization": "Bearer " + initial["access_token"]},
    ).json()["account_ref"]
    body, started = {"scope": "account", "provider_sub": "local-fixture_a"}, now()
    with factory().begin() as db:
        account = db.get(Account, account_id)
        account.generation, account.state = 2, "deleting"
        job = Job(
            id=uid(),
            account_id=account_id,
            generation=1,
            kind="deletion",
            state="running",
            body=body,
            fence=1,
            attempts=1,
            started=started,
            lease_until=started + 120,
            journal_accepted=True,
        )
        db.add(job)
        ident = job.id
    claim = worker.Claim(ident, account_id, 1, "deletion", 1, started, body)
    disabled, release, refreshing = Event(), Event(), Event()
    original_disable, original_lock = (
        local_oauth_state.disable_local_identity,
        module.lock_account,
    )
    refresh_pid = []

    def pause_deletion(db, subject, config):
        original_disable(db, subject, config)
        disabled.set()
        assert release.wait(5), "Test never released account deletion"

    def observe_refresh_lock(db, subject, config):
        refresh_pid.append(db.scalar(text("SELECT pg_backend_pid()")))
        refreshing.set()
        return original_lock(db, subject, config)

    monkeypatch.setattr(local_oauth_state, "disable_local_identity", pause_deletion)
    monkeypatch.setattr(module, "lock_account", observe_refresh_lock)
    with ThreadPoolExecutor(max_workers=2) as pool:
        deletion = pool.submit(
            worker.commit_output, claim, {"external_cleanup_at": iso()}
        )
        assert disabled.wait(5)
        request = pool.submit(refresh, api, module, initial["refresh_token"])
        assert refreshing.wait(5)
        try:
            deadline, observed_wait = time.monotonic() + 2, False
            while time.monotonic() < deadline:
                with factory()() as db:
                    observed_wait = db.scalar(
                        text(
                            "SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE pid=:pid AND wait_event_type='Lock')"
                        ),
                        {"pid": refresh_pid[0]},
                    )
                if observed_wait:
                    break
            assert observed_wait and not request.done(), (
                "Actual refresh did not block on the deletion transaction"
            )
        finally:
            release.set()
        deletion.result(timeout=10)
        assert request.result(timeout=10).status_code == 400
    with factory()() as db:
        assert db.get(Account, account_id).state == "deleted"
        assert (
            db.get(OAuthRecord, "identity-" + module.sha("local-fixture_a")).consumed
            is True
        )
