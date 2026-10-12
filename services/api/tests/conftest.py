import os
import time

os.environ["OTGD_ENVIRONMENT"] = "test"
os.environ.setdefault("OTGD_DATABASE_URL", "sqlite://")
os.environ["OTGD_TOMBSTONE_KEY"] = "35" * 32
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient
from otgd.db import Base, engine, factory, SystemState
from otgd.main import app
from otgd.auth import verifier
from otgd.config import settings

KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def capture_signer(tmp_path, monkeypatch):
    """Explicit ephemeral software-test signing authority; never a runtime fallback."""
    key = ec.generate_private_key(ec.SECP256R1())
    path = tmp_path / "fictional-capture-signing-key.pem"
    path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    path.chmod(0o600)
    monkeypatch.setenv("OTGD_CAPTURE_SIGNING_PRIVATE_KEY_FILE", str(path))
    settings.cache_clear()
    yield key
    settings.cache_clear()


@pytest.fixture
def client():
    eng = engine()
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    with factory().begin() as db:
        db.add(SystemState(key="schema_version", body={"version": 1}))
        from otgd.identity_keys import KEY_STATE,key_descriptor
        db.add(SystemState(key=KEY_STATE,body=key_descriptor()))
        from otgd.capture_signing import bind_signing_key
        bind_signing_key(db)
    verifier.keys = {"test": KEY.public_key()}
    verifier.expires = time.monotonic() + 3600
    with TestClient(app) as client:
        yield client


def token(sub="a", family=None, **overrides):
    from otgd.db import now

    issued = int(now())
    claims = {
        "iss": settings().issuer,
        "sub": sub,
        "client_id": settings().client_id,
        "token_use": "access",
        "origin_jti": family or "family-" + sub,
        "jti": "token-" + sub,
        "iat": issued,
        "exp": issued + 900,
        "auth_time": issued,
        **overrides,
    }
    return jwt.encode(claims, KEY, algorithm="RS256", headers={"kid": "test"})


def headers(sub="a", gen=1, key=None, revision=None, **claims):
    from uuid import uuid4

    h = {
        "Authorization": "Bearer " + token(sub, **claims),
        "X-Data-Generation": str(gen),
        "Idempotency-Key": key or str(uuid4()),
    }
    if revision is not None:
        h["If-Match"] = '"' + str(revision) + '"'
    return h


@pytest.fixture
def account(client):
    from otgd.domain import NOTICE_SHA
    from otgd.db import iso

    h = headers()
    a = client.get("/v1/me/capabilities", headers=h).json()["account_ref"]
    assert (
        client.post(
            "/v1/me/acknowledgments",
            headers=h,
            json={"version": "v1", "sha256": NOTICE_SHA, "acknowledged_at": iso()},
        ).status_code
        == 200
    )
    return a
