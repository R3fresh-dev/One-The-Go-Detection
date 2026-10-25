"""One canonical local/CI worker interruption invocation in the migrate image.

Run only with the exact otgd-local Compose migration service. Provision a new
database and dedicated resources; never drop, reset, restart or adopt a fixture.
The report remains on the explicitly mounted reports directory. Fixture signing
keys are ephemeral files in this disposable one-off container's /tmp.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from worker_interrupt_probe import prepare_fixture, require, run_probe, validate_target


def validate_invocation(cfg, project, confirmed):
    from sqlalchemy.engine import make_url

    url = make_url(cfg.db_url())
    require(
        confirmed
        and project == "otgd-local"
        and cfg.environment == "local"
        and not cfg.serverless_mode
        and cfg.database_host == "postgres"
        and cfg.database_port == 5432
        and cfg.database_name == "otgd"
        and cfg.database_user == "otgd_migrator"
        and url.drivername == "postgresql+psycopg"
        and url.host == "postgres"
        and url.port == 5432
        and url.database == "otgd"
        and url.username == "otgd_migrator"
        and not url.query
        and cfg.aws_endpoint_url == "http://localstack:4566"
        and cfg.aws_region == "us-east-2"
        and cfg.artifact_bucket == "otgd-local-artifacts"
        and cfg.export_bucket == "otgd-local-exports"
        and cfg.journal_bucket == "otgd-local-deletion-journal"
        and cfg.queue_url
        == "http://localstack:4566/queue/us-east-2/000000000000/otgd-local-jobs"
        and cfg.dlq_url
        == "http://localstack:4566/queue/us-east-2/000000000000/otgd-local-dlq",
        "Exact fictional otgd-local Compose migration configuration and confirmation required",
    )
    return url


def fixture_environment(cfg, suffix, password, tombstone, signer):
    require(
        re.fullmatch(r"[0-9a-f]{16}", suffix),
        "Fresh 16-hex fixture identifier required",
    )
    namespace = "otgd-worker-probe-" + suffix
    prefix = (
        cfg.aws_endpoint_url + "/queue/" + cfg.aws_region + "/000000000000/" + namespace
    )
    return {
        "OTGD_DATABASE_URL": "",
        "OTGD_DATABASE_NAME": "otgd_worker_probe_" + suffix,
        "OTGD_DATABASE_POOL_SIZE": "1",
        "OTGD_APP_DATABASE_USER": "otgd_worker_probe_app_" + suffix,
        "OTGD_APP_DATABASE_PASSWORD": password,
        "OTGD_TOMBSTONE_KEY": tombstone,
        "OTGD_TOMBSTONE_KEY_ID": "fictional-worker-probe",
        "OTGD_CAPTURE_SIGNING_PRIVATE_KEY_FILE": str(signer),
        "OTGD_CAPTURE_SIGNING_KEY_ID": "fictional-worker-probe-" + suffix,
        "OTGD_DISPOSABLE_DATABASE": "true",
        "OTGD_WORKER_PROBE_NAMESPACE": namespace,
        "OTGD_ARTIFACT_BUCKET": namespace + "-artifacts",
        "OTGD_EXPORT_BUCKET": namespace + "-exports",
        "OTGD_JOURNAL_BUCKET": namespace + "-journal",
        "OTGD_QUEUE_URL": prefix + "-jobs",
        "OTGD_DLQ_URL": prefix + "-dlq",
        # Never import independent canonical establishment receipts into this journal.
        "OTGD_JOURNAL_ESTABLISHMENT_VERSION_ID": "",
        "OTGD_JOURNAL_ESTABLISHMENT_SHA256": "",
    }


def reset_connections():
    from otgd import storage
    from otgd.config import settings
    from otgd.db import engine, factory

    if engine.cache_info().currsize:
        engine().dispose()
    factory.cache_clear()
    engine.cache_clear()
    storage.client.cache_clear()
    settings.cache_clear()


def create_database(url, database, role):
    import psycopg
    from psycopg import sql

    with psycopg.connect(
        url.set(drivername="postgresql").render_as_string(hide_password=False),
        autocommit=True,
        connect_timeout=5,
    ) as db:
        require(
            db.execute("SELECT current_database(),current_user").fetchone()
            == ("otgd", "otgd_migrator"),
            "Actual local migration connection mismatch",
        )
        require(
            db.execute(
                "SELECT 1 FROM pg_database WHERE datname=%s", (database,)
            ).fetchone()
            is None,
            "Database exists; no adoption/reset permitted",
        )
        require(
            db.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)).fetchone()
            is None,
            "Runtime role exists; no alteration/adoption permitted",
        )
        db.execute(
            sql.SQL("CREATE DATABASE {} OWNER {}").format(
                sql.Identifier(database), sql.Identifier("otgd_migrator")
            )
        )


def check_runtime_role(cfg):
    from otgd.db import factory
    from sqlalchemy import text

    with factory()() as db:
        row = db.execute(
            text(
                "SELECT current_user,rolsuper,rolcreatedb,rolcreaterole,rolreplication "
                "FROM pg_roles WHERE rolname=current_user"
            )
        ).one()
        require(
            row[0] == cfg.database_user and not any(row[1:]),
            "Probe worker role must be restricted",
        )
        for table in (
            "system_state",
            "operator_registry",
            "operator_registry_versions",
            "operator_registry_events",
        ):
            require(
                not db.scalar(
                    text("SELECT has_table_privilege(current_user,:table,'UPDATE')"),
                    {"table": table},
                ),
                "Probe worker can alter a protected authority table",
            )
        require(
            not db.scalar(
                text("SELECT has_schema_privilege(current_user,'public','CREATE')")
            ),
            "Probe runtime can modify schema",
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-fictional-workspace", action="store_true")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from otgd.config import settings

    cfg = settings()
    url = validate_invocation(cfg, args.project_name, args.confirm_fictional_workspace)
    require(
        args.output.is_absolute()
        and args.output.parent.is_dir()
        and not args.output.exists(),
        "An absent absolute output path in an existing mounted reports directory is required",
    )
    # Establish output ownership before any resource mutation.
    with args.output.open("x") as out:
        out.write(
            json.dumps(
                {"status": "preparing", "project": "otgd-local", "fictional": True}
            )
            + "\n"
        )
    suffix = secrets.token_hex(8)
    root = Path("/tmp") / ("otgd-worker-probe-" + suffix)
    root.mkdir(mode=0o700)
    signer = root / "capture-key.pem"
    with signer.open("xb") as out:
        out.write(
            ec.generate_private_key(ec.SECP256R1()).private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
    signer.chmod(0o600)
    values = fixture_environment(
        cfg, suffix, secrets.token_hex(32), secrets.token_hex(32), signer
    )
    database, role = values["OTGD_DATABASE_NAME"], values["OTGD_APP_DATABASE_USER"]
    namespace = values["OTGD_WORKER_PROBE_NAMESPACE"]
    args.output.write_text(
        json.dumps(
            {
                "status": "preparing",
                "project": "otgd-local",
                "fictional": True,
                "namespace": namespace,
                "database": database,
                "runtime_role": role,
            }
        )
        + "\n"
    )
    create_database(url, database, role)
    os.environ.update(values)
    # Empty URL is deliberately removed, so component host/name config is used.
    os.environ.pop("OTGD_DATABASE_URL", None)
    reset_connections()
    fixture = settings()
    validate_target(fixture, namespace, True)
    prepare_fixture(fixture, namespace)
    os.environ["OTGD_DATABASE_USER"] = role
    os.environ["OTGD_DATABASE_PASSWORD"] = values["OTGD_APP_DATABASE_PASSWORD"]
    os.environ.pop("OTGD_APP_DATABASE_PASSWORD", None)
    reset_connections()
    runtime = settings()
    validate_target(runtime, namespace, True)
    check_runtime_role(runtime)
    print(
        json.dumps(
            {
                "status": "running",
                "namespace": namespace,
                "database": database,
                "runtime_role": role,
                "output": str(args.output),
            }
        ),
        flush=True,
    )
    report = run_probe(runtime, namespace, args.output)
    print(
        json.dumps({"status": report["status"], "output": str(args.output)}), flush=True
    )


if __name__ == "__main__":
    main()
