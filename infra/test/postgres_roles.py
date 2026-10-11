"""Real role checks on an explicitly disposable database and owned S3 journal.

The application test process leaves temporary trust anchors behind. This
separate migration check starts an empty otgd_ci schema, establishes its own
versioned journal and private test signer, and removes only those test resources.
It never substitutes storage doubles or relaxes production migration custody.
"""

import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import boto3
from botocore.config import Config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from psycopg import sql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

from otgd import storage
from otgd.canonical import canonical
from otgd.config import settings
from otgd.db import Base, iso
from otgd.journal_continuity import CONTROL_KEY, verify_binding
from otgd.migrate import migrate

LOOPBACK = {"localhost", "127.0.0.1", "::1"}


def disposable_target(cfg, environ=None):
    environ = os.environ if environ is None else environ
    if cfg.environment != "test" or environ.get("OTGD_DISPOSABLE_DATABASE") != "true":
        raise RuntimeError("Explicit disposable test database is required")
    url = make_url(cfg.db_url())
    if (
        url.get_backend_name() != "postgresql"
        or url.database != "otgd_ci"
        or cfg.database_name != "otgd_ci"
        or url.host not in LOOPBACK
        or url.query
    ):
        raise RuntimeError("Dedicated loopback PostgreSQL integration database required")
    if (
        not cfg.app_database_password
        or not re.fullmatch(r"otgd_app_ci(?:_[a-z0-9]{1,16})?", cfg.app_database_user)
        or cfg.app_database_user == url.username
    ):
        raise RuntimeError("An explicitly named disposable runtime role is required")
    endpoint = environ.get("OTGD_LIVE_S3_ENDPOINT", "")
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in LOOPBACK
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError("Explicit loopback LocalStack S3 endpoint is required")
    return url, endpoint


@contextmanager
def environment(values):
    prior = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        settings.cache_clear()
        storage.client.cache_clear()
        yield
    finally:
        for key, value in prior.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        settings.cache_clear()
        storage.client.cache_clear()


def cleanup_bucket(client, bucket):
    for page in client.get_paginator("list_object_versions").paginate(Bucket=bucket):
        objects = [
            {"Key": item["Key"], "VersionId": item["VersionId"]}
            for field in ("Versions", "DeleteMarkers")
            for item in page.get(field, [])
        ]
        if objects:
            removed = client.delete_objects(
                Bucket=bucket, Delete={"Objects": objects, "Quiet": True}
            )
            if removed.get("Errors"):
                raise RuntimeError("Disposable journal version cleanup failed")
    client.delete_bucket(Bucket=bucket)


def assert_runtime_permissions(cfg, url):
    app = create_engine(
        url.set(username=cfg.app_database_user, password=cfg.app_database_password),
        pool_size=1, max_overflow=0,
    )
    try:
        with app.connect() as connection:
            assert connection.execute(text("SELECT count(*) FROM system_state")).scalar() >= 3
            verify_binding(connection)
        from otgd.domain import registry
        from otgd.operator_governance import active_body
        with Session(app) as db:
            assert registry(db, "study", "fictional-role-check-study")["name"] == "Fictional permission check"
            assert active_body(db, "study", "fictional-role-check-study")["version"] == "v1"
        statements = [
            "CREATE TABLE forbidden_runtime_ddl (id integer)",
            "INSERT INTO operator_registry (id,kind,body,active) VALUES ('forbidden','qualification','{}',true)",
            "INSERT INTO system_state (key,body) VALUES ('forbidden','{}')",
            "UPDATE operator_registry_versions SET state='active' WHERE false",
            "UPDATE operator_registry_events SET reason='forbidden' WHERE false",
            "UPDATE raw_upload_tickets SET expires_at=0 WHERE false",
            "DELETE FROM raw_upload_tickets WHERE false",
            "UPDATE audit SET action='forbidden' WHERE false",
            "DELETE FROM audit WHERE false",
        ]
        for statement in statements:
            try:
                with app.begin() as connection:
                    connection.execute(text(statement))
            except DBAPIError as error:
                if getattr(error.orig, "sqlstate", None) != "42501":
                    raise
            else:
                raise RuntimeError("Runtime role unexpectedly has protected write permission")
    finally:
        app.dispose()


def run_role_check(original, url, endpoint):
    bucket = "otgd-role-ci-journal-" + uuid4().hex
    role = "otgd_app_ci_" + uuid4().hex[:12]
    local = boto3.Session(
        aws_access_key_id="testing", aws_secret_access_key="testing",
        region_name=original.aws_region,
    )
    client = local.client(
        "s3", endpoint_url=endpoint,
        config=Config(
            ignore_configured_endpoint_urls=True, signature_version="s3v4",
            s3={"addressing_style": "path"}, connect_timeout=5, read_timeout=10,
            retries={"max_attempts": 1},
        ),
    )
    admin = create_engine(url, pool_size=1, max_overflow=0)
    bucket_created = database_owned = False
    try:
        params = {"Bucket": bucket}
        if original.aws_region != "us-east-1":
            params["CreateBucketConfiguration"] = {"LocationConstraint": original.aws_region}
        client.create_bucket(**params)
        bucket_created = True
        client.put_bucket_versioning(
            Bucket=bucket, VersioningConfiguration={"Status": "Enabled"}
        )
        marker = canonical({
            "schema_version": "1.0.0", "environment": "test",
            "established_at": iso(), "minimum_retention_days": 90,
            "maximum_recovery_age_days": 35,
        })
        result = client.put_object(
            Bucket=bucket, Key=CONTROL_KEY, Body=marker, ContentLength=len(marker),
            ContentType="application/json", ServerSideEncryption="AES256",
            IfNoneMatch="*",
        )
        version = result.get("VersionId")
        if not version or version == "null":
            raise RuntimeError("Actual versioned journal establishment is required")
        with tempfile.TemporaryDirectory(prefix="otgd-role-ci-") as directory:
            path = Path(directory) / "capture-signing.pem"
            private = ec.generate_private_key(ec.SECP256R1())
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as file:
                file.write(private.private_bytes(
                    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                ))
            with environment({
                "OTGD_JOURNAL_BUCKET": bucket,
                "OTGD_AWS_ENDPOINT_URL": endpoint,
                "OTGD_JOURNAL_KMS_KEY_ID": None,
                "OTGD_JOURNAL_ESTABLISHMENT_VERSION_ID": version,
                "OTGD_JOURNAL_ESTABLISHMENT_SHA256": hashlib.sha256(marker).hexdigest(),
                "OTGD_CAPTURE_SIGNING_PRIVATE_KEY_FILE": str(path),
                "OTGD_CAPTURE_SIGNING_KEY_ID": None,
                "OTGD_APP_DATABASE_USER": role,
            }):
                # Only the explicitly disposable otgd_ci schema is reset.
                # Production trust anchors are never rebound or adopted.
                database_owned = True
                Base.metadata.drop_all(admin)
                migrate()
                migrate()
                from otgd.db import now
                from otgd.operator_governance import submit, transition
                document = "Fictional SQL permission check only, no enrolled participant or research approval."
                body = {"schema_version": "1.0.0", "registry_id": "fictional-role-check-study",
                    "version": "v1", "expires_at": now() + 3600,
                    "evidence_ref": "fictional-permission-test", "evidence_sha256": "1" * 64,
                    "study_id": "fictional-role-check-study", "protocol_id": "fictional-role-check-protocol",
                    "name": "Fictional permission check", "account_refs": [], "invitation_id": "fictional-invitation",
                    "document_version": "v1", "document_text": document,
                    "document_sha256": hashlib.sha256(document.encode()).hexdigest(),
                    "retention_summary": "Fictional disposable role check", "channels": {}}
                with Session(admin) as db, db.begin():
                    submit(db, "study", body, "local:permission-submitter")
                    transition(db, "study", body["registry_id"], "v1", "approve",
                        "local:permission-reviewer", "Fictional SQL read authorization", 1)
                    db.flush()
                    transition(db, "study", body["registry_id"], "v1", "release",
                        "local:permission-releaser", "Fictional independent SQL permission check", 2)
                cfg = settings()
                with admin.connect() as connection:
                    width = connection.execute(text(
                        "SELECT character_maximum_length FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name='system_state' AND column_name='key'"
                    )).scalar()
                    assert width >= 72, "The subject HMAC lookup key is 72 characters"
                    proof = verify_binding(connection)
                    assert proof["binding"]["version_id"] == version
                    assert proof["binding"]["sha256"] == hashlib.sha256(marker).hexdigest()
                assert_runtime_permissions(cfg, url)
                print(json.dumps({
                    "status": "passed", "database": "actual_postgresql",
                    "journal": "actual_versioned_localstack", "migration_runs": 2,
                    "runtime_ddl": "denied", "authority_write": "denied",
                    "audit_update_delete": "denied", "ticket_update_delete": "denied",
                    "released_registry_read": "admitted_without_update_permission",
                }))
    finally:
        # Do not retain SQL anchors pointing at a removed disposable journal.
        try:
            if database_owned:
                Base.metadata.drop_all(admin)
                with admin.begin() as connection:
                    raw = connection.connection.driver_connection
                    with raw.cursor() as cursor:
                        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,))
                        if cursor.fetchone():
                            cursor.execute(sql.SQL("DROP OWNED BY {}").format(sql.Identifier(role)))
                            cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))
        finally:
            admin.dispose()
            if bucket_created:
                cleanup_bucket(client, bucket)


def main():
    cfg = settings()
    url, endpoint = disposable_target(cfg)
    # Only fictional credentials with an explicitly validated loopback endpoint.
    with environment({
        "AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SESSION_TOKEN": None, "AWS_PROFILE": None, "AWS_DEFAULT_PROFILE": None,
    }):
        run_role_check(cfg, url, endpoint)


if __name__ == "__main__":
    main()
