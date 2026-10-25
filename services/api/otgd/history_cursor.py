"""Bounded session-history positions bound to the existing identity key.

Domain separation follows existing raw-payload HMAC references. No independent
cursor secret, environment fallback or new protected configuration is introduced.
The caller must also resolve the exact current owned database boundary.
"""

import base64
import hashlib
import hmac
import math
import re
from uuid import UUID

from .canonical import canonical, digest, strict_loads
from .errors import Problem
from .identity_keys import key_descriptor

DOMAIN = b"OTGD session history cursor v1\x00"
SORT = "created_at DESC,session_id DESC"


def scope(account, config):
    return digest(
        [
            "session-history-v1",
            config.environment,
            config.issuer,
            account.id,
            account.generation,
            SORT,
        ]
    )


def authenticator(position, config):
    key_descriptor(config)  # The established identity key must exist; no fallback.
    return hmac.new(
        bytes.fromhex(config.tombstone_key),
        DOMAIN + canonical(position),
        hashlib.sha256,
    ).hexdigest()


def encode_cursor(account, boundary, config):
    position = {
        "version": 1,
        "scope": scope(account, config),
        "created": boundary.created,
        "id": boundary.id,
    }
    return (
        base64.urlsafe_b64encode(
            canonical({**position, "mac": authenticator(position, config)})
        )
        .decode()
        .rstrip("=")
    )


def decode_cursor(cursor, account, config):
    try:
        if not isinstance(cursor, str) or not re.fullmatch(
            r"[A-Za-z0-9_-]{1,1024}", cursor
        ):
            raise ValueError()
        raw = base64.b64decode(
            cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True
        )
        if base64.urlsafe_b64encode(raw).decode().rstrip("=") != cursor:
            raise ValueError()
        value = strict_loads(raw)
        if (
            not isinstance(value, dict)
            or set(value) != {"version", "scope", "created", "id", "mac"}
            or type(value["version"]) is not int
            or value["version"] != 1
            or value["scope"] != scope(account, config)
            or type(value["created"]) not in (int, float)
            or not math.isfinite(value["created"])
            or not 0 < value["created"] <= 9007199254740991
            or not isinstance(value["id"], str)
            or len(value["id"]) != 36
            or str(UUID(value["id"])) != value["id"]
            or not isinstance(value["mac"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", value["mac"])
            or canonical(value) != raw
        ):
            raise ValueError()
        position = {key: item for key, item in value.items() if key != "mac"}
        if not hmac.compare_digest(value["mac"], authenticator(position, config)):
            raise ValueError()
        return value["created"], value["id"]
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise Problem(422, "INVALID_CURSOR") from None
