"""Bind retained SQL state to an independently versioned journal establishment.

Runtime identities can only read this anchor. An existing database never adopts
a replacement journal, including when a disposable emulator loses its objects.
"""

import hashlib
import os
import re
from datetime import datetime

from sqlalchemy import inspect, select

from .canonical import canonical, strict_loads
from .config import settings
from .db import Account, SystemState

STATE_KEY = "journal_establishment"
CONTROL_KEY = "control/established.json"
LIMIT = 8192


class JournalContinuityBlocked(RuntimeError):
    pass


def _version(value):
    if not isinstance(value, str) or not value or value == "null" or len(value) > 1024:
        raise JournalContinuityBlocked("A retained journal version is required")
    return value


def read_establishment(config=None, storage_client=None):
    """Read current bytes and version atomically, without caching admission."""
    s = config or settings()
    if storage_client is None:
        from .storage import client

        storage_client = client("s3")
    try:
        response = storage_client.get_object(
            Bucket=s.journal_bucket, Key=CONTROL_KEY
        )
        stream = response["Body"]
        try:
            # A current GET returns one atomic object/version pair. A prior HEAD
            # followed by a pinned GET could accept an old version if the current
            # marker changed between calls. Every admission still reads S3 anew.
            version = _version(response.get("VersionId"))
            if response.get("ContentLength", LIMIT + 1) > LIMIT:
                raise JournalContinuityBlocked(
                    "Journal establishment exceeds its bound"
                )
            raw = stream.read(LIMIT + 1)
        finally:
            stream.close()
        if len(raw) > LIMIT:
            raise JournalContinuityBlocked("Journal establishment exceeds its bound")
        body = strict_loads(raw)
        if (
            not isinstance(body, dict)
            or canonical(body) != raw
            or body.get("schema_version") != "1.0.0"
            or body.get("environment") != s.environment
            or type(body.get("minimum_retention_days")) is not int
            or body["minimum_retention_days"] != 90
            or type(body.get("maximum_recovery_age_days")) is not int
            or body["maximum_recovery_age_days"] != 35
        ):
            raise JournalContinuityBlocked(
                "Journal establishment configuration mismatch"
            )
        instant = datetime.fromisoformat(body["established_at"].replace("Z", "+00:00"))
        if instant.tzinfo is None or instant.utcoffset().total_seconds() != 0:
            raise ValueError("Not UTC")
    except JournalContinuityBlocked:
        raise
    except Exception:
        raise JournalContinuityBlocked(
            "Independent journal establishment is unavailable"
        ) from None
    binding = {
        "schema_version": "1.0.0",
        "environment": s.environment,
        "aws_region": s.aws_region,
        "journal_bucket": s.journal_bucket,
        "control_key": CONTROL_KEY,
        "version_id": version,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    return {"binding": binding, "body": body}


def database_binding(db):
    return db.scalar(select(SystemState.body).where(SystemState.key == STATE_KEY))


def verify_binding(db, config=None, storage_client=None):
    """Mandatory admission check; missing SQL/S3 anchor is a closed barrier."""
    expected = database_binding(db)
    if not isinstance(expected, dict):
        raise JournalContinuityBlocked(
            "Database has no independently established journal binding"
        )
    observed = read_establishment(config, storage_client)
    if expected != observed["binding"]:
        raise JournalContinuityBlocked(
            "Retained database and journal identity do not match"
        )
    return observed


def has_retained_accounts(connection):
    if "accounts" not in inspect(connection).get_table_names():
        return False
    return connection.scalar(select(Account.id).limit(1)) is not None


def preflight_bootstrap(connection, config=None, storage_client=None):
    """Run before creating *any* missing bucket/control in resource initialization."""
    tables = inspect(connection).get_table_names()
    if "system_state" in tables and database_binding(connection) is not None:
        return verify_binding(connection, config, storage_client)
    if has_retained_accounts(connection):
        observed = read_establishment(config, storage_client)
        if (
            os.environ.get("OTGD_JOURNAL_ESTABLISHMENT_VERSION_ID")
            != observed["binding"]["version_id"]
            or os.environ.get("OTGD_JOURNAL_ESTABLISHMENT_SHA256")
            != observed["binding"]["sha256"]
        ):
            raise JournalContinuityBlocked(
                "Existing unbound database requires an independently verified administrator migration"
            )
        return observed
    return None


def bind_migration(
    connection,
    config=None,
    storage_client=None,
    *,
    expected_version=None,
    expected_sha256=None,
):
    """Only migration/admin connection calls this; no runtime binding creation."""
    prior = database_binding(connection)
    observed = read_establishment(config, storage_client)
    if prior is not None:
        if prior != observed["binding"]:
            raise JournalContinuityBlocked(
                "Existing journal binding cannot be replaced"
            )
        return observed
    version = (
        expected_version
        or os.environ.get("OTGD_JOURNAL_ESTABLISHMENT_VERSION_ID")
        or None
    )
    sha = expected_sha256 or os.environ.get("OTGD_JOURNAL_ESTABLISHMENT_SHA256") or None
    if version is not None or sha is not None:
        if (
            not version
            or not isinstance(sha, str)
            or not re.fullmatch(r"[0-9a-f]{64}", sha)
        ):
            raise JournalContinuityBlocked(
                "Both independent establishment version and digest are required"
            )
        if (
            version != observed["binding"]["version_id"]
            or sha != observed["binding"]["sha256"]
        ):
            raise JournalContinuityBlocked(
                "Independently supplied journal receipt does not match"
            )
    elif has_retained_accounts(connection):
        raise JournalContinuityBlocked(
            "Existing database cannot automatically adopt a journal"
        )
    connection.execute(
        SystemState.__table__.insert().values(key=STATE_KEY, body=observed["binding"])
    )
    return observed
