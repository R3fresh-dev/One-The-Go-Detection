"""Real PostgreSQL trigger enforcement; explicitly disposable database only."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from otgd.db import Account, engine, factory, uid
from otgd.domain import save_record
from otgd.participant_migration import (IMMUTABLE_KINDS, migration_005_participant_acquisition,
    migration_006_cardiac_interval_anchors)


@pytest.mark.postgres
def test_receipt_update_is_denied_in_postgres_without_blocking_privacy_deletion(client, account):
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    with engine().begin() as connection:
        migration_005_participant_acquisition(connection)
        migration_005_participant_acquisition(connection)
    for kind in IMMUTABLE_KINDS:
        with factory().begin() as db:
            owner = db.get(Account, account)
            row = save_record(db, owner, kind, uid(), {"fixture": "immutable-software-receipt"})
            db.flush()
            identity = row.id
        with factory()() as db:
            with pytest.raises(DBAPIError) as failure:
                db.execute(text("UPDATE records SET body='{}' WHERE id=:id"), {"id": identity})
            assert failure.value.orig.sqlstate == "42501"
            db.rollback()
        with factory().begin() as db:
            assert db.scalar(text("SELECT body FROM records WHERE id=:id"), {"id": identity}) == {"fixture": "immutable-software-receipt"}
            db.execute(text("DELETE FROM records WHERE id=:id"), {"id": identity})
            assert db.scalar(text("SELECT id FROM records WHERE id=:id"), {"id": identity}) is None


@pytest.mark.postgres
def test_sample_identity_collisions_are_atomic_across_different_subjects(client, account):
    from sqlalchemy.exc import IntegrityError
    from otgd.db import Record
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    with engine().begin() as connection:
        migration_005_participant_acquisition(connection)
    sample = uid()
    with factory().begin() as db:
        owner = db.get(Account, account)
        save_record(db, owner, "collection", uid(), {"request": {"sample_id": sample}})
        other = Account(id=uid(), subject_hash="a" * 64, generation=1, state="active")
        db.add(other)
        other_id = other.id
    with factory()() as db:
        with pytest.raises(IntegrityError) as collision:
            save_record(db, db.get(Account, other_id), "collection", uid(), {"request": {"sample_id": sample}})
            db.flush()
        assert collision.value.orig.sqlstate == "23505"
        db.rollback()
    with factory()() as db:
        rows = list(db.query(Record).filter(Record.kind == "collection"))
        assert len(rows) == 1 and rows[0].account_id == account


@pytest.mark.postgres
def test_signed_issue_and_attestation_receipt_anchors_cannot_be_rewritten(client, account):
    from otgd.canonical import digest
    from otgd.db import Record
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    with engine().begin() as connection:
        migration_005_participant_acquisition(connection)
        migration_006_cardiac_interval_anchors(connection)
        migration_006_cardiac_interval_anchors(connection)
    with factory().begin() as db:
        owner = db.get(Account, account)
        attestation = save_record(db, owner, "attestation", uid(), {"fixture": "signed-custody-evidence"})
        authorization = save_record(db, owner, "authorization", uid(), {"state": "issued", "scope": "unchanged"})
        db.flush()
        attestation_id, authorization_id = attestation.id, authorization.id
    for identity, sql in ((attestation_id, "created=created-100"), (attestation_id, "body='{}'"),
        (authorization_id, "created=created-100"), (authorization_id, "body='{}'")):
        with factory()() as db:
            with pytest.raises(DBAPIError) as denied:
                db.execute(text(f"UPDATE records SET {sql} WHERE id=:id"), {"id": identity})
            assert denied.value.orig.sqlstate == "42501"
            db.rollback()
    with factory().begin() as db:
        row = db.get(Record, authorization_id)
        row.body = {**row.body, "state": "started", "device_boot_id": None,
            "server_started_at": "2026-10-11T00:00:00Z", "server_started_epoch": 1791676800.0,
            "server_start": {"domain": "OTGD capture grant v1\0", "fixture": "signature checked separately by application"}}
        row.sha256 = digest(row.body)
    for sql in ("created=created+1", "body='{}'", "sha256='fake'", "revision=revision+1"):
        with factory()() as db:
            with pytest.raises(DBAPIError) as denied:
                db.execute(text(f"UPDATE records SET {sql} WHERE id=:id"), {"id": authorization_id})
            assert denied.value.orig.sqlstate == "42501"
            db.rollback()
    with factory().begin() as db:
        db.execute(text("DELETE FROM records WHERE id IN (:attestation,:authorization)"),
            {"attestation": attestation_id, "authorization": authorization_id})


@pytest.mark.postgres
def test_released_authority_reads_need_no_registry_update_privilege(client, account):
    from sqlalchemy.orm import Session
    from otgd.domain import registry
    from otgd.operator_governance import active_body
    from .governance_fixture import approve, study, STUDY
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    role = "otgd_readonly_test_" + uid().replace("-", "")
    with factory().begin() as db:
        approve(db, "study", study(account))
    with engine().begin() as connection:
        connection.execute(text(f'CREATE ROLE "{role}" NOLOGIN'))
        connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{role}"'))
        connection.execute(text(f'GRANT SELECT ON operator_registry,operator_registry_versions,operator_registry_events TO "{role}"'))
    try:
        with engine().connect() as connection, connection.begin():
            connection.execute(text(f'SET LOCAL ROLE "{role}"'))
            with Session(bind=connection) as db:
                assert active_body(db, "study", STUDY)["study_id"] == STUDY
                assert registry(db, "study", STUDY)["study_id"] == STUDY
            assert connection.scalar(text("SELECT has_table_privilege(current_user,'operator_registry','UPDATE')")) is False
        with engine().begin() as connection:
            connection.execute(text(f'SET LOCAL ROLE "{role}"'))
            with pytest.raises(DBAPIError) as denied:
                connection.execute(text("UPDATE operator_registry SET active=false WHERE false"))
            assert denied.value.orig.sqlstate == "42501"
    finally:
        with engine().begin() as connection:
            connection.execute(text(f'DROP OWNED BY "{role}"'))
            connection.execute(text(f'DROP ROLE "{role}"'))


@pytest.mark.postgres
def test_comparison_escape_does_not_conflate_literal_backslash_with_nul(client, account):
    from otgd.canonical import digest
    from otgd.db import Record
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    with engine().begin() as connection:
        migration_006_cardiac_interval_anchors(connection)
    with factory().begin() as db:
        row = save_record(db, db.get(Account, account), "authorization", uid(),
            {"state": "issued", "scope": "literal\\u0000", "declared": "actual\0value"})
        db.flush()
        identity = row.id
    started = {"state": "started", "scope": "literal\\u0000", "declared": "actual\0value",
        "server_start": {"domain": "OTGD capture grant v1\0"}}
    with factory()() as db:
        row = db.get(Record, identity)
        row.body = {**started, "scope": "literal\0"}
        row.sha256 = digest(row.body)
        with pytest.raises(DBAPIError) as denied:
            db.flush()
        assert denied.value.orig.sqlstate == "42501"
        db.rollback()
    with factory().begin() as db:
        row = db.get(Record, identity)
        row.body, row.sha256 = started, digest(started)
    with factory()() as db:
        assert db.get(Record, identity).body == started


# Import the independently reviewed fixture; it executes the real three-role
# release lifecycle under labeled fictional actors and creates no cloud object.
from .test_lab_handoff import import_body, settle  # noqa: E402
from . import test_lab_handoff  # noqa: E402


@pytest.fixture
def handoff(client, account):
    return test_lab_handoff.handoff.__wrapped__(client, account)


@pytest.mark.postgres
def test_delegated_operator_nowait_does_not_deadlock_a_subject_transaction(client, handoff):
    import time
    from sqlalchemy import select
    from otgd import lab_handoff
    from otgd.errors import Problem
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    with factory()() as subject_db:
        subject_db.scalar(select(Account).where(Account.id == handoff.participant).with_for_update())
        began = time.monotonic()
        with factory()() as operator_db:
            with pytest.raises(Problem, match="LAB_TARGET_BUSY") as busy:
                lab_handoff.delegated_target(operator_db, operator_db.get(Account, handoff.operator),
                    handoff.request.session_id, handoff.request.study_id, handoff.participant, 1)
            assert busy.value.status == 503 and busy.value.retryable
        assert time.monotonic() - began < 2.0
        subject_db.rollback()
    with factory()() as db:
        target, _, _ = lab_handoff.delegated_target(db, db.get(Account, handoff.operator),
            handoff.request.session_id, handoff.request.study_id, handoff.participant, 1)
        assert target.id == handoff.participant


@pytest.mark.postgres
def test_abandonment_serializes_against_delegated_import_and_cannot_reopen(client, handoff):
    from sqlalchemy import select
    from otgd import lab_handoff
    from otgd.db import Check
    from otgd.errors import Problem
    from otgd.participant_acquisition import CollectionAbandonment, abandon_collection
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    report = settle(handoff)
    body = import_body(handoff, report)
    with factory()() as subject_db:
        target = subject_db.scalar(select(Account).where(Account.id == handoff.participant).with_for_update())
        receipt = abandon_collection(subject_db, target, subject_db.get(Check, handoff.request.session_id),
            handoff.request.sample_id, CollectionAbandonment(confirmation=True, reason="USER_CANCELED"))
        assert receipt["state"] == "analysis_canceled"
        subject_db.flush()
        with factory()() as operator_db:
            with pytest.raises(Problem, match="LAB_TARGET_BUSY"):
                lab_handoff.import_measurements(operator_db, operator_db.get(Account, handoff.operator), body)
        subject_db.commit()
    with factory()() as db:
        with pytest.raises(Problem, match="LAB_ANALYSIS_ABANDONED"):
            lab_handoff.import_measurements(db, db.get(Account, handoff.operator), body)
