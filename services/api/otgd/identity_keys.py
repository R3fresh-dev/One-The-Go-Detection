"""Immutable secret identity checked before HMAC-based account admission.

Replacing a key while retaining its deployment label must fail closed. Rotation
requires a separately implemented retained-keyring and journal reconciliation;
the current application does not reinterpret existing pseudonymous identities.
"""
import hashlib
from .config import settings
from .db import SystemState
from .errors import Problem

KEY_STATE='identity_tombstone_key'

def key_descriptor(config=None):
    config=config or settings()
    try:
        key=bytes.fromhex(config.tombstone_key)
        if len(key)!=32 or not isinstance(config.tombstone_key_id,str) or not 1<=len(config.tombstone_key_id)<=63:
            raise ValueError()
    except (TypeError,ValueError):
        raise Problem(503,'IDENTITY_KEY_UNAVAILABLE',retryable=True) from None
    fingerprint=hashlib.sha256(key).hexdigest()
    return {'schema_version':'1.0.0','key_id':config.tombstone_key_id+':'+fingerprint}

def require_key(db):
    descriptor=key_descriptor()
    recorded=db.get(SystemState,KEY_STATE)
    if not recorded or recorded.body!=descriptor:
        raise Problem(503,'IDENTITY_KEY_VERSION_UNAVAILABLE',retryable=True)
    return descriptor
