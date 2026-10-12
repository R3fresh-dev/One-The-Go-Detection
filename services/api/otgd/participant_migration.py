"""Preserving v5: specimen and preparation receipts cannot be rewritten."""
from sqlalchemy import select, text
from .db import SystemState


IMMUTABLE_KINDS = ("instruction_receipt", "collection", "collection_abandon", "lab_import")


def migration_005_participant_acquisition(connection):
    key = "migration_005_participant_acquisition"
    if connection.scalar(select(SystemState.body).where(SystemState.key == key)):
        return
    if connection.dialect.name == "postgresql":
        connection.execute(text("""
            CREATE OR REPLACE FUNCTION otgd_immutable_participant_receipt() RETURNS trigger
            LANGUAGE plpgsql AS $$ BEGIN
                IF OLD.kind IN ('instruction_receipt','collection','collection_abandon','lab_import')
                   OR NEW.kind IN ('instruction_receipt','collection','collection_abandon','lab_import') THEN
                    RAISE EXCEPTION 'Immutable participant receipt cannot be rewritten' USING ERRCODE='42501';
                END IF;
                RETURN NEW;
            END $$
        """))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_unique_collection_sample ON records ((body->'request'->>'sample_id')) WHERE kind='collection'"))
        connection.execute(text("DROP TRIGGER IF EXISTS otgd_immutable_participant_receipt ON records"))
        connection.execute(text("""
            CREATE TRIGGER otgd_immutable_participant_receipt BEFORE UPDATE ON records
            FOR EACH ROW EXECUTE FUNCTION otgd_immutable_participant_receipt()
        """))
    connection.execute(SystemState.__table__.insert().values(key=key, body={"version": 5}))


def install_capture_anchor_guard(connection):
    """Install the final comparison-only guard without rewriting any record."""
    if connection.dialect.name == "postgresql":
        connection.execute(text("""
            CREATE OR REPLACE FUNCTION otgd_immutable_capture_anchor() RETURNS trigger
            LANGUAGE plpgsql AS $$
            DECLARE old_safe jsonb; new_safe jsonb;
            BEGIN
                IF OLD.kind = 'attestation' OR NEW.kind = 'attestation' THEN
                    RAISE EXCEPTION 'Immutable device attestation cannot be rewritten' USING ERRCODE='42501';
                END IF;
                IF OLD.kind = 'authorization' OR NEW.kind = 'authorization' THEN
                    -- Escaped NUL is valid JSON and occurs in the signed domain,
                    -- but PostgreSQL JSON processing cannot decode it. This
                    -- injective comparison-only escape widens literal backslashes
                    -- before mapping NUL; stored bytes/signatures never change.
                    old_safe := regexp_replace(replace(OLD.body::text, repeat(chr(92),2), repeat(chr(92),4)),
                        '(?<!'||repeat(chr(92),2)||')'||repeat(chr(92),2)||'u0000', repeat(chr(92),4)||'u0000','g')::jsonb;
                    new_safe := regexp_replace(replace(NEW.body::text, repeat(chr(92),2), repeat(chr(92),4)),
                        '(?<!'||repeat(chr(92),2)||')'||repeat(chr(92),2)||'u0000', repeat(chr(92),4)||'u0000','g')::jsonb;
                    IF OLD.kind <> 'authorization' OR NEW.kind <> 'authorization'
                       OR old_safe->>'state' IS DISTINCT FROM 'issued' OR new_safe->>'state' IS DISTINCT FROM 'started'
                       OR NEW.id IS DISTINCT FROM OLD.id
                       OR NEW.account_id IS DISTINCT FROM OLD.account_id
                       OR NEW.generation IS DISTINCT FROM OLD.generation
                       OR NEW.parent_id IS DISTINCT FROM OLD.parent_id
                       OR NEW.created IS DISTINCT FROM OLD.created
                       OR NEW.revision IS DISTINCT FROM OLD.revision
                       OR (new_safe - ARRAY['state','device_boot_id','server_started_at','server_started_epoch','server_start'])
                           IS DISTINCT FROM (old_safe - 'state') THEN
                        RAISE EXCEPTION 'Immutable capture authorization anchor cannot be rewritten' USING ERRCODE='42501';
                    END IF;
                END IF;
                RETURN NEW;
            END $$
        """))
        connection.execute(text("DROP TRIGGER IF EXISTS otgd_immutable_capture_anchor ON records"))
        connection.execute(text("""
            CREATE TRIGGER otgd_immutable_capture_anchor BEFORE UPDATE ON records
            FOR EACH ROW EXECUTE FUNCTION otgd_immutable_capture_anchor()
        """))


def migration_006_cardiac_interval_anchors(connection):
    """Preserve signed issue and original receipt times against SQL rewriting."""
    key = "migration_006_cardiac_interval_anchors"
    if connection.scalar(select(SystemState.body).where(SystemState.key == key)):
        return
    install_capture_anchor_guard(connection)
    connection.execute(SystemState.__table__.insert().values(key=key, body={"version": 6}))


def migration_007_capture_guard_unicode(connection):
    """Upgrade existing v6 guards; all prior anchors and migration history remain."""
    key = "migration_007_capture_guard_unicode"
    expected = {"version": 7, "comparison": "injective-escaped-nul-v1"}
    existing = connection.scalar(select(SystemState.body).where(SystemState.key == key))
    if existing is not None:
        if existing != expected:
            raise RuntimeError("Capture guard migration identity conflict")
        return
    if connection.scalar(select(SystemState.body).where(SystemState.key == "migration_006_cardiac_interval_anchors")) != {"version": 6}:
        raise RuntimeError("Capture guard upgrade requires original migration 006")
    install_capture_anchor_guard(connection)
    connection.execute(SystemState.__table__.insert().values(key=key, body=expected))
