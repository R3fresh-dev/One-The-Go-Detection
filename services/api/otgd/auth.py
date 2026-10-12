import hashlib
import hmac
import threading
import time
from dataclasses import dataclass, field
from types import MappingProxyType

import httpx
import jwt
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from .canonical import canonical
from .config import settings
from .db import Account, Revocation, SystemState, now, uid
from .errors import Problem


class Verifier:
    def __init__(self):
        self.keys = {}
        self.expires = 0
        self.last_refresh = 0
        self.lock = threading.Lock()

    def verify(self, token):
        s = settings()
        try:
            head = jwt.get_unverified_header(token)
            if (
                head.get("alg") != "RS256"
                or not isinstance(head.get("kid"), str)
                or len(head["kid"]) > 128
            ):
                raise ValueError()
            with self.lock:
                current = time.monotonic()
                if current >= self.expires or head["kid"] not in self.keys:
                    if current - self.last_refresh < 10:
                        raise ValueError("JWKS refresh bound")
                    self.last_refresh = current
                    r = httpx.get(s.jwks_url, timeout=5, follow_redirects=False)
                    if r.status_code != 200 or len(r.content) > 65536:
                        raise ValueError()
                    keys = r.json().get("keys", [])
                    if len(keys) > 16:
                        raise ValueError()
                    self.keys = {
                        k["kid"]: jwt.PyJWK.from_dict(k).key
                        for k in keys
                        if k.get("kty") == "RSA"
                        and k.get("alg", "RS256") == "RS256"
                        and k.get("use", "sig") == "sig"
                    }
                    self.expires = current + 300
                key = self.keys[head["kid"]]
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=s.issuer,
                options={
                    "verify_aud": False,
                    "require": [
                        "exp",
                        "iat",
                        "iss",
                        "sub",
                        "client_id",
                        "token_use",
                        "jti",
                        "origin_jti",
                        "auth_time",
                    ],
                },
            )
            if claims["token_use"] != "access" or claims["client_id"] != s.client_id:
                raise ValueError()
            for field in ["sub", "origin_jti", "jti"]:
                if (
                    not isinstance(claims[field], str)
                    or not 1 <= len(claims[field]) <= 128
                ):
                    raise ValueError()
            if (
                any(type(claims[field]) is not int for field in ('iat','exp','auth_time'))
                or claims['auth_time']<0 or claims['auth_time']>claims['iat']
                or claims['exp']<=claims['iat']
                or claims["auth_time"] > now() + 5
            ):
                raise ValueError()
            return claims
        except (jwt.PyJWTError, ValueError, KeyError, TypeError, httpx.HTTPError):
            raise Problem(401, "AUTH_REQUIRED") from None


verifier = Verifier()


@dataclass(frozen=True)
class _VerifiedAuthorization:
    """Request-local signature proof, never constructed from HTTP JSON."""
    claims: MappingProxyType = field(repr=False)


def _verify_authorization(authorization):
    if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        raise Problem(401, "AUTH_REQUIRED")
    return _VerifiedAuthorization(MappingProxyType(verifier.verify(authorization[7:])))


def subject_hash(claims):
    s = settings()
    from .identity_keys import key_descriptor
    key_descriptor(s)
    key = bytes.fromhex(s.tombstone_key)
    return hmac.new(
        key, canonical([s.issuer, claims["sub"]]), hashlib.sha256
    ).hexdigest()


def family_hash(account_id, family):
    return hashlib.sha256(canonical([account_id, family])).hexdigest()


def authenticate(db, authorization, receipt=False):
    verified = authorization if isinstance(authorization, _VerifiedAuthorization) else _verify_authorization(authorization)
    claims = dict(verified.claims)
    from .identity_keys import require_key
    require_key(db)
    subject = subject_hash(claims)
    from .recovery_authority import require_authority
    independent_cutoff = require_authority(db)
    if claims["auth_time"] < independent_cutoff:
        raise Problem(401, "FRESH_SIGN_IN_REQUIRED")
    recovery = db.get(SystemState, "recovery")
    if settings().recovery_required and (
        not recovery or not recovery.body.get("verified")
    ):
        raise Problem(503, "RECOVERY_NOT_VERIFIED", retryable=True)
    if recovery and claims["auth_time"] < recovery.body.get("authentication_cutoff", 0):
        raise Problem(401, "FRESH_SIGN_IN_REQUIRED")
    issuer_revoked = False
    if settings().environment == 'local':
        from .local_oauth_state import family_status
        admitted, issuer_revoked = family_status(db, claims['origin_jti'], claims['sub'])
        if not admitted or (issuer_revoked and not receipt):
            raise Problem(401, 'AUTH_REQUIRED')
    account = db.scalar(
        select(Account)
        .where(Account.subject_hash == subject)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if settings().environment == 'local':
        from .local_oauth_state import family_status, lock_identity
        # Existing accounts are locked before their identity. For a subject
        # without an account, serialize issuance/provisioning on its identity
        # before inserting; an absent SQL row cannot provide a row lock.
        identity = lock_identity(db, claims['sub'])
        admitted, issuer_revoked = family_status(db, claims['origin_jti'], claims['sub'])
        if (identity.consumed and (not receipt or account is None)) or not admitted or (issuer_revoked and not receipt):
            raise Problem(401, 'AUTH_REQUIRED')
    if account is None:
        restored = db.get(SystemState, "subject:" + subject)
        if restored:
            data = restored.body
            values = dict(
                id=data["account_ref"],
                subject_hash=subject,
                generation=data["generation"],
                state=data["state"],
            )
        else:
            values = dict(id=uid(), subject_hash=subject, generation=1, state="active")
        insert = pg_insert if db.bind.dialect.name == "postgresql" else sqlite_insert
        db.execute(
            insert(Account)
            .values(**values)
            .on_conflict_do_nothing(index_elements=["subject_hash"])
        )
        account = db.scalar(
            select(Account)
            .where(Account.subject_hash == subject)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    revoked = db.get(Revocation, family_hash(account.id, claims["origin_jti"])) or issuer_revoked
    if revoked and not receipt:
        raise Problem(401, "AUTH_REQUIRED")
    if account.state == "deleted" and not receipt:
        raise Problem(403, "ACCOUNT_DELETED")
    return account, claims, bool(revoked)


def recent(claims):
    if not 0<=now() - claims["auth_time"]<=300:
        raise Problem(401, "REAUTHENTICATION_REQUIRED")
