"""Actual preserving PostgreSQL upgrade from the deployed preliminary v6 guard."""
import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from otgd.canonical import digest
from otgd.db import Account, Record, SystemState, engine, factory, uid
from otgd.domain import save_record
from otgd.participant_migration import migration_007_capture_guard_unicode


# This is the preliminary installed v6 comparison. It rejects a real token's
# escaped NUL while attempting to parse the NEW JSON, before the intended checks.
LEGACY_GUARD = """
CREATE OR REPLACE FUNCTION otgd_immutable_capture_anchor() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    IF OLD.kind = 'attestation' OR NEW.kind = 'attestation' THEN
        RAISE EXCEPTION 'Immutable device attestation cannot be rewritten' USING ERRCODE='42501';
    END IF;
    IF OLD.kind = 'authorization' OR NEW.kind = 'authorization' THEN
        IF OLD.kind <> 'authorization' OR NEW.kind <> 'authorization'
           OR OLD.body->>'state' IS DISTINCT FROM 'issued' OR NEW.body->>'state' IS DISTINCT FROM 'started'
           OR NEW.id IS DISTINCT FROM OLD.id OR NEW.account_id IS DISTINCT FROM OLD.account_id
           OR NEW.generation IS DISTINCT FROM OLD.generation OR NEW.parent_id IS DISTINCT FROM OLD.parent_id
           OR NEW.created IS DISTINCT FROM OLD.created OR NEW.revision IS DISTINCT FROM OLD.revision
           OR (SELECT COALESCE(json_object_agg(e.key,e.value ORDER BY e.key)::text,'{}')
               FROM json_each(NEW.body) e WHERE e.key NOT IN
                   ('state','device_boot_id','server_started_at','server_started_epoch','server_start'))
               IS DISTINCT FROM (SELECT COALESCE(json_object_agg(e.key,e.value ORDER BY e.key)::text,'{}')
                   FROM json_each(OLD.body) e WHERE e.key <> 'state') THEN
            RAISE EXCEPTION 'Immutable capture authorization anchor cannot be rewritten' USING ERRCODE='42501';
        END IF;
    END IF;
    RETURN NEW;
END $$
"""


def snapshot(db):
    return [(row.id, row.account_id, row.generation, row.parent_id, row.created, row.revision,
        row.sha256, row.body) for row in db.scalars(select(Record).order_by(Record.id))]


@pytest.mark.postgres
def test_legacy_guard_upgrade_preserves_signed_anchors_grants_and_migration_history(client, account):
    assert engine().dialect.name == "postgresql", "Mandatory live gate requires real PostgreSQL"
    role = "otgd_guard_upgrade_" + uid().replace("-", "")
    with engine().begin() as connection:
        connection.execute(text(LEGACY_GUARD))
        connection.execute(text("DROP TRIGGER IF EXISTS otgd_immutable_capture_anchor ON records"))
        connection.execute(text("CREATE TRIGGER otgd_immutable_capture_anchor BEFORE UPDATE ON records FOR EACH ROW EXECUTE FUNCTION otgd_immutable_capture_anchor()"))
        connection.execute(SystemState.__table__.insert().values(key="migration_006_cardiac_interval_anchors", body={"version": 6}))
        connection.execute(text(f'CREATE ROLE "{role}" NOLOGIN'))
        connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{role}"'))
        connection.execute(text(f'GRANT SELECT,INSERT,UPDATE,DELETE ON records TO "{role}"'))
        connection.execute(text(f'GRANT SELECT ON operator_registry,operator_registry_versions,operator_registry_events TO "{role}"'))
        connection.execute(text(f'GRANT EXECUTE ON FUNCTION otgd_immutable_capture_anchor() TO "{role}"'))
    try:
        with factory().begin() as db:
            owner = db.get(Account, account)
            existing = save_record(db, owner, "authorization", uid(), {"state": "started",
                "server_start": {"domain": "OTGD capture grant v1\0"}, "scope": "unaltered"})
            attestation = save_record(db, owner, "attestation", uid(), {"signed": "unaltered"})
            pending = save_record(db, owner, "authorization", uid(), {"state": "issued", "scope": "literal\\u0000"})
            db.flush()
            existing_id, attestation_id, pending_id = existing.id, attestation.id, pending.id
            original = snapshot(db)
        started = {"state": "started", "scope": "literal\\u0000",
            "server_start": {"domain": "OTGD capture grant v1\0"}}
        with factory()() as db:
            pending = db.get(Record, pending_id)
            pending.body, pending.sha256 = started, digest(started)
            with pytest.raises(DBAPIError) as legacy_failure:
                db.flush()
            assert legacy_failure.value.orig.sqlstate == "22P05"
            db.rollback()
        with engine().begin() as connection:
            grants = list(connection.execute(text("SELECT relname,relacl::text FROM pg_class WHERE relnamespace='public'::regnamespace ORDER BY relname")))
            function_grants = connection.scalar(text("SELECT proacl::text FROM pg_proc WHERE pronamespace='public'::regnamespace AND proname='otgd_immutable_capture_anchor'"))
            migration_007_capture_guard_unicode(connection)
            migration_007_capture_guard_unicode(connection)
            assert list(connection.execute(text("SELECT relname,relacl::text FROM pg_class WHERE relnamespace='public'::regnamespace ORDER BY relname"))) == grants
            assert connection.scalar(text("SELECT proacl::text FROM pg_proc WHERE pronamespace='public'::regnamespace AND proname='otgd_immutable_capture_anchor'")) == function_grants
            assert connection.scalar(select(SystemState.body).where(SystemState.key == "migration_006_cardiac_interval_anchors")) == {"version": 6}
            assert connection.scalar(select(SystemState.body).where(SystemState.key == "migration_007_capture_guard_unicode"))["version"] == 7
        with factory()() as db:
            assert snapshot(db) == original
        for identity in (existing_id, attestation_id):
            with factory()() as db:
                with pytest.raises(DBAPIError) as denial:
                    db.execute(text("UPDATE records SET created=created+1 WHERE id=:id"), {"id": identity})
                assert denial.value.orig.sqlstate == "42501"
                db.rollback()
        with factory()() as db:
            pending = db.get(Record, pending_id)
            pending.body = {**started, "scope": "literal\0"}
            pending.sha256 = digest(pending.body)
            with pytest.raises(DBAPIError) as changed_scope:
                db.flush()
            assert changed_scope.value.orig.sqlstate == "42501"
            db.rollback()
        with factory().begin() as db:
            pending = db.get(Record, pending_id)
            pending.body, pending.sha256 = started, digest(started)
        with factory()() as db:
            assert db.get(Record, pending_id).body == started
            for original_row in original:
                row = db.get(Record, original_row[0])
                assert row.created == original_row[4]
        with engine().begin() as connection:
            assert connection.scalar(text("SELECT has_table_privilege(:role,'operator_registry','UPDATE')"), {"role": role}) is False
            assert connection.scalar(text("SELECT has_table_privilege(:role,'records','DELETE')"), {"role": role}) is True
    finally:
        with engine().begin() as connection:
            connection.execute(text(f'DROP OWNED BY "{role}"'))
            connection.execute(text(f'DROP ROLE "{role}"'))


def test_guard_upgrade_without_original_marker_fails_closed(client):
    with engine().begin() as connection:
        with pytest.raises(RuntimeError, match="original migration 006"):
            migration_007_capture_guard_unicode(connection)
