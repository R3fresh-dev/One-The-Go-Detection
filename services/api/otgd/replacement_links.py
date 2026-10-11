"""Bounded direct physical-replacement navigation; never rewrites evidence."""

import base64
import math
import re
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select

from .canonical import canonical, digest, strict_loads
from .db import Check
from .dto import ReplacementLink, ReplacementLinks
from .errors import Problem

FROZEN_STATES = ("processing", "completed", "invalid")


def _summary(row, account):
    snapshot = row.snapshot
    if (
        row.account_id != account.id
        or row.generation != account.generation
        or row.state not in FROZEN_STATES
        or not isinstance(snapshot, dict)
        or not row.snapshot_sha256
        or snapshot.get("session_id") != row.id
        or snapshot.get("subject_ref") != account.id
        or snapshot.get("supersedes_session_id") != row.supersedes_id
        or row.supersedes_id == row.id
        or snapshot.get("created_at") != snapshot.get("target_at")
        or digest(snapshot) != row.snapshot_sha256
    ):
        raise Problem(409, "REPLACEMENT_LINK_INTEGRITY")
    try:
        return ReplacementLink(
            session_id=row.id, created_at=snapshot.get("created_at"), state=row.state
        )
    except ValidationError:
        raise Problem(409, "REPLACEMENT_LINK_INTEGRITY") from None


def _position(cursor, scope):
    try:
        if not isinstance(cursor, str) or not re.fullmatch(
            r"[A-Za-z0-9_-]{1,1024}", cursor
        ):
            raise ValueError()
        decoded = base64.b64decode(
            cursor + "=" * ((4 - len(cursor) % 4) % 4), altchars=b"-_", validate=True
        )
        value = strict_loads(decoded)
        if (
            not isinstance(value, dict)
            or set(value) != {"scope", "created", "id"}
            or value["scope"] != scope
            or type(value["created"]) not in (int, float)
            or not math.isfinite(value["created"])
            or not 0 < value["created"] <= 9007199254740991
            or not isinstance(value["id"], str)
            or len(value["id"]) != 36
        ):
            raise ValueError()
        UUID(value["id"])
        return value["created"], value["id"]
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise Problem(422, "INVALID_CURSOR") from None


def replacement_links_view(db, account, base, cursor=None, limit=20):
    if type(limit) is not int or not 1 <= limit <= 100:
        raise Problem(422, "VALIDATION_FAILED")
    # Snapshot PUT remains mutable in draft. Presence alone is insufficient.
    if base.state == "draft":
        raise Problem(409, "SNAPSHOT_NOT_AVAILABLE")
    _summary(base, account)
    scope = digest([account.id, account.generation, base.id])
    query = select(Check).where(
        Check.account_id == account.id,
        Check.generation == account.generation,
        Check.supersedes_id == base.id,
        Check.state.in_(FROZEN_STATES),
    )
    if cursor is not None:
        created, identity = _position(cursor, scope)
        query = query.where(
            (Check.created < created)
            | ((Check.created == created) & (Check.id < identity))
        )
    candidates = list(
        db.scalars(
            query.order_by(Check.created.desc(), Check.id.desc()).limit(limit + 1)
        )
    )
    more = len(candidates) > limit
    rows = candidates[:limit]
    # Verify the lookahead too: it may establish that another page exists.
    summaries = [_summary(row, account) for row in candidates]
    previous = None
    if base.supersedes_id:
        predecessor = db.scalar(
            select(Check).where(
                Check.id == base.supersedes_id,
                Check.account_id == account.id,
                Check.generation == account.generation,
                Check.state.in_(FROZEN_STATES),
            )
        )
        if predecessor is not None:
            previous = _summary(predecessor, account)
            if predecessor.supersedes_id == base.id:
                raise Problem(409, "REPLACEMENT_LINK_INTEGRITY")
    next_cursor = (
        base64.urlsafe_b64encode(
            canonical(
                {"scope": scope, "created": rows[-1].created, "id": rows[-1].id}
            )
        ).decode().rstrip("=")
        if more
        else None
    )
    return ReplacementLinks(
        session_id=base.id,
        data_generation=account.generation,
        base_snapshot_sha256=base.snapshot_sha256,
        previous=previous,
        items=summaries[:limit],
        next_cursor=next_cursor,
    ).data()
