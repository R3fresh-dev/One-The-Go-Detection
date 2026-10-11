"""Versioned one-off migration. Runtime application identity cannot run DDL."""

from sqlalchemy import text

from .config import settings
from .db import Base, engine


def migrate():
    s = settings()
    eng = engine()
    with eng.begin() as connection:
        postgres = connection.dialect.name == "postgresql"
        if postgres:
            connection.execute(text("SET LOCAL lock_timeout = '5s'"))
            connection.execute(text("SET LOCAL statement_timeout = '60s'"))
            if not connection.scalar(
                text("SELECT pg_try_advisory_xact_lock(798114231)")
            ):
                raise RuntimeError("Another migration owns the advisory lock")
        # Additive baseline v1. Subsequent versions must use separate numbered migrations.
        Base.metadata.create_all(connection)
        if postgres:
            connection.execute(
                text("ALTER TABLE system_state ALTER COLUMN key TYPE varchar(128)")
            )
            for table in ("artifacts", "jobs"):
                connection.execute(
                    text(
                        f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS cleanup_next_at DOUBLE PRECISION NOT NULL DEFAULT 0"
                    )
                )
                connection.execute(
                    text(
                        f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS cleanup_last_success DOUBLE PRECISION"
                    )
                )
                connection.execute(
                    text(
                        f"CREATE INDEX IF NOT EXISTS ix_{table}_cleanup_next_at ON {table}(cleanup_next_at)"
                    )
                )
        existing = connection.execute(
            text("SELECT body FROM system_state WHERE key='schema_version'")
        ).scalar()
        if existing and existing.get("version") != 1:
            raise RuntimeError("Unsupported database version; do not downgrade")
        import json

        if not existing:
            connection.execute(
                text("INSERT INTO system_state (key,body) VALUES (:key,:body)"),
                {"key": "schema_version", "body": json.dumps({"version": 1})},
            )
        if postgres and s.app_database_password:
            from psycopg import sql

            raw = connection.connection.driver_connection
            with raw.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM pg_roles WHERE rolname=%s", (s.app_database_user,)
                )
                command = "ALTER ROLE" if cursor.fetchone() else "CREATE ROLE"
                cursor.execute(
                    sql.SQL(
                        command
                        + " {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD {}"
                    ).format(
                        sql.Identifier(s.app_database_user),
                        sql.Literal(s.app_database_password),
                    )
                )
                cursor.execute(
                    sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                        sql.Identifier(s.database_name),
                        sql.Identifier(s.app_database_user),
                    )
                )
                cursor.execute(
                    sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                        sql.Identifier(s.app_database_user)
                    )
                )
                cursor.execute(
                    sql.SQL(
                        "GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO {}"
                    ).format(sql.Identifier(s.app_database_user))
                )
                cursor.execute(
                    sql.SQL(
                        "GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO {}"
                    ).format(sql.Identifier(s.app_database_user))
                )
                # Application can read but cannot manufacture qualification, trust anchors, or recovery evidence.
                cursor.execute(
                    sql.SQL(
                        "REVOKE INSERT,UPDATE,DELETE ON operator_registry,system_state FROM {}"
                    ).format(sql.Identifier(s.app_database_user))
                )
                cursor.execute(
                    sql.SQL("REVOKE UPDATE,DELETE ON audit FROM {}").format(
                        sql.Identifier(s.app_database_user)
                    )
                )
                cursor.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
    print("Schema v1 ready; no clinical configuration or model was provisioned.")


if __name__ == "__main__":
    migrate()
