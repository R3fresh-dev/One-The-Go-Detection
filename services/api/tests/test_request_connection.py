"""Request-local pool ownership; actual PG proofs use only a new owned schema."""
from uuid import uuid4

import pytest
from otgd import auth, main
from otgd.db import Account, Base, Check, RateBucket, Revocation, SystemState, engine
from otgd.errors import Problem
from otgd.identity_keys import KEY_STATE, key_descriptor
from sqlalchemy import event, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema
from starlette.requests import Request

from .conftest import KEY, headers


def request(subject="a"):
    values = headers(sub=subject)
    return Request({"type": "http", "method": "POST", "path": "/v1/sessions",
                    "headers": [(k.lower().encode(), v.encode()) for k, v in values.items()]})


def test_one_checkout_two_fresh_sessions_and_two_actual_signature_checks(client, account, monkeypatch):
    pool, checkout, checkin, sessions, connections, verified = engine().pool, [], [], [], [], []
    original, verify = main.authenticate, auth.verifier.verify
    def authenticate(db, authorization, receipt=False):
        result = original(db, authorization, receipt)
        sessions.append(db)
        connections.append(db.connection().connection.dbapi_connection)
        return result
    monkeypatch.setattr(main, "authenticate", authenticate)
    def verify_signature(value):
        verified.append(value)
        return verify(value)
    monkeypatch.setattr(auth.verifier, "verify", verify_signature)
    def checked_out(*args): checkout.append(args[0])
    def checked_in(*args): checkin.append(args[0])
    event.listen(pool, "checkout", checked_out); event.listen(pool, "checkin", checked_in)
    try:
        result = client.post("/v1/sessions", headers=headers(), json={"session_id": str(uuid4()), "mode": "synthetic"})
    finally:
        event.remove(pool, "checkout", checked_out); event.remove(pool, "checkin", checked_in)
    assert result.status_code == 201
    assert len(sessions) == 2 and sessions[0] is not sessions[1]
    assert len(verified) == 2 and verified[0] == verified[1]
    assert len(checkout) == len(checkin) == 1 and checkout[0] is checkin[0]
    assert connections[0] is connections[1]
    if hasattr(pool, "checkedout"):
        assert pool.checkedout() == 0


def test_invalid_signature_never_checks_out_sql(client):
    pool, checkout = engine().pool, []
    def checked_out(*args): checkout.append(args[0])
    event.listen(pool, "checkout", checked_out)
    try:
        h = headers(); h["Authorization"] = "Bearer invalid.signature"
        result = client.post("/v1/sessions", headers=h, json={"session_id": str(uuid4()), "mode": "synthetic"})
    finally:
        event.remove(pool, "checkout", checked_out)
    assert result.status_code == 401 and not checkout


@pytest.fixture
def postgres_namespace(monkeypatch):
    """No resets: create/drop only our unique schema in the disposable CI DB."""
    import os
    import time
    eng = engine()
    if (os.environ.get("OTGD_DISPOSABLE_DATABASE") != "true" or eng.dialect.name != "postgresql"
            or eng.url.database != "otgd_ci" or eng.url.host not in {"localhost", "127.0.0.1", "postgres"}):
        pytest.fail("Actual loopback disposable otgd_ci PostgreSQL is required")
    schema = "request_connection_" + uuid4().hex
    with eng.begin() as connection:
        connection.execute(CreateSchema(schema))
        Base.metadata.create_all(connection.execution_options(schema_translate_map={None: schema}))
    isolated = eng.execution_options(schema_translate_map={None: schema})
    sessions = sessionmaker(bind=isolated, expire_on_commit=False)
    subject, account = "connection-" + uuid4().hex, str(uuid4())
    try:
        with sessions.begin() as db:
            db.add(SystemState(key=KEY_STATE, body=key_descriptor()))
            db.add(SystemState(key="recovery", body={"verified": True, "authentication_cutoff": 0}))
            db.add(Account(id=account, subject_hash=auth.subject_hash({"sub": subject}), generation=1, state="active", notice="original"))
        monkeypatch.setattr(main, "factory", lambda: sessions)
        monkeypatch.setattr(auth.verifier, "keys", {"test": KEY.public_key()})
        monkeypatch.setattr(auth.verifier, "expires", time.monotonic() + 3600)
        yield sessions, subject, account
    finally:
        with eng.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))


@pytest.mark.postgres
@pytest.mark.parametrize("failure", ["phase_two", "family", "identity", "recovery", "generation", "handler", "commit", "cancellation", "rate_commit"])
def test_actual_pg_rate_commit_is_visible_and_connection_returns_on_every_failure(postgres_namespace, monkeypatch, failure):
    sessions, subject, account = postgres_namespace
    original, calls, primary, observations = main.authenticate, [], [], []
    class Cancelled(BaseException): pass
    def authenticate(db, authorization, receipt=False):
        if calls:
            # A genuinely distinct PostgreSQL connection sees the first root
            # transaction's commit before second-phase authorization begins.
            with sessions() as observer:
                bucket = observer.get(RateBucket, account + ":write")
                observations.append(bucket.tokens)
                assert bucket.tokens == 19
                assert observer.connection().connection.dbapi_connection is not primary[0]
            if failure in {"phase_two", "family", "identity", "recovery", "generation"}:
                with sessions.begin() as writer:
                    if failure == "phase_two":
                        writer.get(Account, account).state = "deleting"
                    elif failure == "family":
                        writer.add(Revocation(id=auth.family_hash(account, "family-" + subject), account_id=account))
                    elif failure == "identity":
                        writer.get(SystemState, KEY_STATE).body = {"schema_version": "1.0.0", "key_id": "changed-key"}
                    elif failure == "generation":
                        writer.get(Account, account).generation = 2
                    else:
                        import time
                        writer.get(SystemState, "recovery").body = {"verified": True, "authentication_cutoff": int(time.time()) + 60}
        result = original(db, authorization, receipt)
        calls.append(db)
        primary.append(db.connection().connection.dbapi_connection)
        return result
    monkeypatch.setattr(main, "authenticate", authenticate)
    def reject_commit(db):
        if failure == "rate_commit" and any(isinstance(row, RateBucket) for row in db.new):
            raise Problem(503, "RATE_COMMIT_FAILED")
        if failure == "commit" and db.dirty:
            raise Problem(503, "SECOND_COMMIT_FAILED")
    event.listen(Session, "before_commit", reject_commit)
    try:
        expected = Cancelled if failure == "cancellation" else Problem
        req = request(subject)
        req.state.json_value = {}
        with pytest.raises(expected) as denied:
            with main.access(req) as (db, owner, claims, revoked):
                if failure == "generation": main.operation(req, db, owner, claims, revoked)
                owner.notice = "rolled-back"
                if failure == "handler": raise Problem(409, "HANDLER_DENIED")
                if failure == "cancellation": raise Cancelled()
    finally:
        event.remove(Session, "before_commit", reject_commit)
    if failure == "generation":
        assert denied.value.code == "DATA_GENERATION_RETIRED"
    assert engine().pool.checkedout() == 0
    with sessions() as observer:
        row = observer.get(Account, account)
        assert row.notice == "original"
        bucket = observer.get(RateBucket, account + ":write")
        if failure == "rate_commit":
            assert bucket is None and not observations
        else:
            assert bucket.tokens == 19 and observations == [19]
        assert observer.scalar(select(Check).where(Check.account_id == account)) is None
    if len(primary) == 2:
        assert primary[0] is primary[1] and calls[0] is not calls[1]


@pytest.mark.postgres
def test_actual_pg_concurrent_signed_requests_preserve_rate_and_exclusive_pool_ownership(postgres_namespace, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier, Lock

    from fastapi.testclient import TestClient

    sessions, subject, account = postgres_namespace
    with sessions.begin() as db:
        db.get(Account, account).notice = main.NOTICE_SHA
    monkeypatch.setattr(main, "now", lambda: 1000)
    original, phases, held, maximum, lock = main.authenticate, {}, set(), [], Lock()
    def authenticate(db, authorization, receipt=False):
        result = original(db, authorization, receipt)
        with lock:
            phases.setdefault(result[1]["jti"], []).append((db, db.connection().connection.dbapi_connection))
        return result
    monkeypatch.setattr(main, "authenticate", authenticate)
    def checkout(connection, *args):
        with lock:
            assert id(connection) not in held
            held.add(id(connection)); maximum.append(len(held))
    def checkin(connection, *args):
        with lock:
            assert id(connection) in held
            held.remove(id(connection))
    pool = engine().pool
    event.listen(pool, "checkout", checkout); event.listen(pool, "checkin", checkin)
    barrier, ids = Barrier(8), [str(uuid4()) for _ in range(8)]
    try:
        with TestClient(main.app) as http:
            def submit(session_id):
                h = headers(sub=subject, jti="request-" + session_id)
                barrier.wait(timeout=5)
                return http.post("/v1/sessions", headers=h, json={"session_id": session_id, "mode": "synthetic"})
            with ThreadPoolExecutor(max_workers=8) as executor:
                results = list(executor.map(submit, ids))
        assert all(result.status_code == 201 for result in results)
        assert not held and pool.checkedout() == 0 and 1 < max(maximum) <= 5
    finally:
        event.remove(pool, "checkout", checkout); event.remove(pool, "checkin", checkin)
    assert len(phases) == 8
    for pair in phases.values():
        assert len(pair) == 2 and pair[0][0] is not pair[1][0] and pair[0][1] is pair[1][1]
    with sessions() as observer:
        assert observer.get(RateBucket, account + ":write").tokens == 12
        assert set(observer.scalars(select(Check.id).where(Check.account_id == account))) == set(ids)
