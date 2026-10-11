"""Numbered, additive migrations compatible with the v1 evidence schema."""

from sqlalchemy import inspect, select

from .db import Check, SystemState


def migration_002_replacement_navigation(connection):
    """Index-only migration; no evidence row or v1 serialization is rewritten."""
    name = "ix_checks_owner_replacement_page"
    columns = ["account_id", "generation", "supersedes_id", "created", "id"]
    key = "migration:002_replacement_navigation"
    expected = {"migration": 2, "index": name, "columns": columns}
    existing = connection.scalar(
        select(SystemState.body).where(SystemState.key == key)
    )
    if existing is not None and existing != expected:
        raise RuntimeError("Replacement-navigation migration identity conflict")
    index = next(index for index in Check.__table__.indexes if index.name == name)
    index.create(connection, checkfirst=True)
    observed = next(
        item for item in inspect(connection).get_indexes("checks") if item["name"] == name
    )
    if observed["column_names"] != columns or observed["unique"]:
        raise RuntimeError("Replacement-navigation index definition mismatch")
    if existing is None:
        connection.execute(
            SystemState.__table__.insert().values(key=key, body=expected)
        )


def migration_003_operator_governance(connection):
    """Add authority history without accepting or rewriting any prior approval."""
    from sqlalchemy import text
    from .db import RegistryEvent, RegistryVersion

    key = "migration:003_operator_governance"
    expected = {"migration": 3, "tables": ["operator_registry_versions", "operator_registry_events"],
        "content_identity": "rfc8785-sha256", "independent_principals": 3}
    existing = connection.scalar(select(SystemState.body).where(SystemState.key == key))
    if existing is not None and existing != expected:
        raise RuntimeError("Operator-governance migration identity conflict")
    RegistryVersion.__table__.create(connection, checkfirst=True)
    RegistryEvent.__table__.create(connection, checkfirst=True)
    if connection.dialect.name == "postgresql":
        connection.execute(text("""CREATE OR REPLACE FUNCTION otgd_registry_immutable() RETURNS trigger
            LANGUAGE plpgsql AS $$ BEGIN
              IF TG_TABLE_NAME = 'operator_registry_events' THEN
                RAISE EXCEPTION 'Registry decision events are append-only' USING ERRCODE='23514';
              END IF;
              IF TG_OP = 'DELETE' OR NEW.id IS DISTINCT FROM OLD.id
                OR NEW.registry_key IS DISTINCT FROM OLD.registry_key
                OR NEW.version IS DISTINCT FROM OLD.version OR NEW.kind IS DISTINCT FROM OLD.kind
                OR NEW.body::jsonb IS DISTINCT FROM OLD.body::jsonb
                OR NEW.sha256 IS DISTINCT FROM OLD.sha256
                OR NEW.submitted_by IS DISTINCT FROM OLD.submitted_by
                OR NEW.submitted_at IS DISTINCT FROM OLD.submitted_at THEN
                RAISE EXCEPTION 'Submitted registry content is immutable' USING ERRCODE='23514';
              END IF;
              RETURN NEW;
            END $$"""))
        for table in ("operator_registry_versions", "operator_registry_events"):
            connection.execute(text(f"DROP TRIGGER IF EXISTS registry_immutable ON {table}"))
            connection.execute(text(f"CREATE TRIGGER registry_immutable BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION otgd_registry_immutable()"))
    if existing is None:
        connection.execute(SystemState.__table__.insert().values(key=key, body=expected))
