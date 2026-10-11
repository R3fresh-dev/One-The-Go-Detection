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
