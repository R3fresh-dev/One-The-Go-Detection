"""Local fictional issuer state; safe to import without starting its ASGI app.

Lock order is application Account, fictional identity, family, then grant. Family
deadlines never slide. Identity disablement is durable and is not expired by the
bounded cleanup of transient OAuth records. This module is never a cloud issuer.
"""

import hashlib
import hmac

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from .canonical import canonical
from .db import Account, OAuthRecord, Revocation, now

FICTIONAL_ACCOUNTS = (
    "fixture_a",
    "fixture_b",
    "participant_probe_subject",
    "participant_probe_staff",
    *(f"perf_{i:02d}" for i in range(1, 21)),
)
FAMILY_SECONDS = 30 * 86400
ACCESS_SECONDS = 900


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def family_id(family):
    return "family-state-" + sha(family)


def lock_account(db, subject, config):
    hashed = hmac.new(
        bytes.fromhex(config.tombstone_key),
        canonical([config.issuer, subject]),
        hashlib.sha256,
    ).hexdigest()
    return db.scalar(
        select(Account)
        .where(Account.subject_hash == hashed)
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def lock_identity(db, subject):
    if subject not in {"local-" + account for account in FICTIONAL_ACCOUNTS}:
        raise ValueError("Only named fictional local identities are supported")
    ident = "identity-" + sha(subject)
    locked = (
        select(OAuthRecord)
        .where(OAuthRecord.id == ident)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    existing = db.scalar(locked)
    if existing is not None:
        return existing
    insert = pg_insert if db.bind.dialect.name == "postgresql" else sqlite_insert
    db.execute(
        insert(OAuthRecord)
        .values(
            id=ident,
            kind="identity",
            body={"sub": subject},
            expires=32503680000.0,
            consumed=False,
        )
        .on_conflict_do_nothing(index_elements=["id"])
    )
    return db.scalar(locked)


def lock_family(db, family):
    return db.scalar(
        select(OAuthRecord)
        .where(OAuthRecord.id == family_id(family))
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def revoke_family(db, family, account=None):
    row = lock_family(db, family)
    if row:
        row.consumed = True
    if account is not None:
        ident = hashlib.sha256(canonical([account.id, family])).hexdigest()
        insert = pg_insert if db.bind.dialect.name == "postgresql" else sqlite_insert
        db.execute(
            insert(Revocation)
            .values(id=ident, account_id=account.id)
            .on_conflict_do_nothing(index_elements=["id"])
        )


def family_status(db, family, subject):
    row = db.get(OAuthRecord, family_id(family), populate_existing=True)
    return row is not None and row.kind == "family" and row.body.get(
        "sub"
    ) == subject and row.expires > now(), bool(row and row.consumed)


def disable_local_identity(db, subject, config):
    """Called inside the account deletion commit while its Account lock is held."""
    if config.environment != "local":
        raise ValueError("Fictional identity disablement is local-only")
    row = lock_identity(db, subject)
    row.consumed = True


def cleanup_expired(db, timestamp=None, limit=128):
    if type(limit) is not int or not 1 <= limit <= 128:
        raise ValueError("OAuth cleanup is bounded to at most 128 rows")
    timestamp = now() if timestamp is None else timestamp
    ids = list(
        db.scalars(
            select(OAuthRecord.id)
            .where(
                OAuthRecord.kind.in_(
                    ["authorization", "code", "refresh", "family", "revoked"]
                ),
                OAuthRecord.expires <= timestamp,
            )
            .order_by(OAuthRecord.expires, OAuthRecord.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
    )
    if ids:
        db.execute(delete(OAuthRecord).where(OAuthRecord.id.in_(ids)))
    return len(ids)
