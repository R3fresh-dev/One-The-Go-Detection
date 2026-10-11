"""Fictional keys qualify signing software, never a physical device or study."""

import base64
from types import SimpleNamespace
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, utils
from botocore.exceptions import ClientError, EndpointConnectionError

from otgd import capture_signing as signing
from otgd.canonical import canonical
from otgd.config import settings
from otgd.db import SystemState, engine, factory, iso, now
from otgd.errors import Problem


def grant(**changes):
    return {
        "schema_version": "1.0.0", "environment": "test", "owner_ref": str(uuid4()),
        "data_generation": 1, "session_id": str(uuid4()), "attempt_id": str(uuid4()),
        "authorization_id": str(uuid4()), "binding_id": str(uuid4()),
        "device_id": "FICTIONAL-READER", "device_key_id": "FICTIONAL-KEY",
        "boot_id": "FICTIONAL-BOOT", "configuration_id": "FICTIONAL-CONFIG",
        "channel": "cardiac", "configuration_max_duration_ms": 15000,
        "configuration_hash": "a" * 64, "configuration_submitted_sha256": "b" * 64,
        "configuration_version": "v1", "capture_context_sha256": "c" * 64,
        "issued_at": iso(), "expires_at": iso(now() + 60),
        "device_nonce": "FICTIONAL-DEVICE-NONCE", "nonce": str(uuid4()),
        "raw_recording_permission": None, "participant_protocol_sha256": "d" * 64,
        "instruction_receipt_id": str(uuid4()), **changes,
    }


def test_local_signed_start_is_exact_domain_bound_and_anchor_is_not_replaced(client, capture_signer):
    with factory().begin() as db:
        body = grant()
        token = signing.sign_start(db, body)
        assert token["grant"] == body and token["domain"] == signing.DOMAIN
        assert token["key_id"].startswith("local-capture-v1:")
        signature = base64.b64decode(token["signature"], validate=True)
        capture_signer.public_key().verify(signature,
            signing.DOMAIN.encode() + canonical(body), ec.ECDSA(hashes.SHA256()))
        with pytest.raises(InvalidSignature):
            capture_signer.public_key().verify(signature,
                signing.DOMAIN.encode() + canonical({**body, "device_nonce": "different"}), ec.ECDSA(hashes.SHA256()))
        assert signing.bind_signing_key(db) == signing.require_signing_key(db)
        original = db.get(SystemState, signing.KEY_STATE)
        original.body = {**original.body, "public_key_sha256": "9" * 64}
        db.flush()
        with pytest.raises(Problem, match="CAPTURE_SIGNING_KEY_CHANGED"):
            signing.sign_start(db, body)


def test_signed_raw_recording_choice_is_not_an_unsigned_start_hint(client, capture_signer):
    from pydantic import ValidationError
    from otgd.domain import validate_schema

    permission = {"record": True, "upload": False, "receipt_id": str(uuid4()),
        "policy_id": "fictional-recording-policy", "policy_version": "v1",
        "policy_sha256": "d" * 64, "raw_notice_version": "v1", "raw_notice_sha256": "e" * 64}
    with factory()() as db:
        token = signing.sign_start(db, grant(channel="eyes", raw_recording_permission=permission))
        validate_schema(token, "application/ServerStartToken.schema.json")
        assert token["grant"]["raw_recording_permission"] == permission
        tampered = {**token["grant"], "raw_recording_permission": {**permission, "upload": True}}
        with pytest.raises(InvalidSignature):
            capture_signer.public_key().verify(base64.b64decode(token["signature"]),
                signing.DOMAIN.encode() + canonical(tampered), ec.ECDSA(hashes.SHA256()))
        with pytest.raises(ValidationError):
            signing.StartGrant.model_validate(grant(channel="cardiac", raw_recording_permission=permission))


def test_missing_anchor_cannot_sign_and_connection_binding_is_idempotent(client):
    with factory().begin() as db:
        db.delete(db.get(SystemState, signing.KEY_STATE))
    with factory()() as db:
        with pytest.raises(Problem, match="CAPTURE_SIGNING_KEY_NOT_BOUND"):
            signing.sign_start(db, grant())
    with engine().begin() as connection:
        first = signing.bind_signing_key(connection)
        assert signing.bind_signing_key(connection) == first


@pytest.mark.parametrize("defect", ["missing", "symlink", "fifo", "permissions", "oversized", "rsa", "hardlink", "replacement"])
def test_local_private_key_custody_and_retained_identity_fail_closed(client, tmp_path, defect):
    import os
    from pathlib import Path

    path = Path(settings().capture_signing_private_key_file)
    if defect == "missing":
        path.unlink()
    elif defect == "fifo":
        path.unlink()
        os.mkfifo(path, 0o600)
    elif defect == "symlink":
        original = tmp_path / "original.pem"
        path.rename(original)
        path.symlink_to(original)
    elif defect == "permissions":
        path.chmod(0o644)
    elif defect == "oversized":
        path.write_bytes(b"x" * 8193)
    elif defect == "hardlink":
        os.link(path, tmp_path / "second-link.pem")
    else:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048) if defect == "rsa" else ec.generate_private_key(ec.SECP256R1())
        path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    with factory()() as db:
        with pytest.raises(Problem) as denied:
            signing.require_signing_key(db)
        assert denied.value.code == ("CAPTURE_SIGNING_KEY_CHANGED" if defect == "replacement" else "CAPTURE_SIGNING_KEY_UNAVAILABLE")


def test_cloud_signer_pins_actual_kms_public_material_and_digest_operation(client, monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    spki = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    key_id = "arn:aws:kms:us-east-2:123456789012:key/00000000-0000-4000-8000-000000000001"
    cfg = SimpleNamespace(environment="qa", aws_region="us-east-2", deployment_account="123456789012", capture_signing_key_id=key_id)
    calls = []

    class KMS:
        def get_public_key(self, **request):
            assert request == {"KeyId": key_id}
            return {"KeyId": key_id, "KeySpec": "ECC_NIST_P256", "KeyUsage": "SIGN_VERIFY",
                "SigningAlgorithms": ["ECDSA_SHA_256"], "PublicKey": spki}
        def sign(self, **request):
            assert request["KeyId"] == key_id and request["MessageType"] == "DIGEST"
            assert request["SigningAlgorithm"] == "ECDSA_SHA_256" and len(request["Message"]) == 32
            return {"KeyId": key_id, "SigningAlgorithm": "ECDSA_SHA_256",
                "Signature": key.sign(request["Message"], ec.ECDSA(utils.Prehashed(hashes.SHA256())))}

    def client_factory(service, **options):
        calls.append(options)
        assert service == "kms" and options["endpoint_url"] == "https://kms.us-east-2.amazonaws.com"
        assert options["config"].ignore_configured_endpoint_urls is True
        return KMS()

    monkeypatch.setattr(signing, "settings", lambda: cfg)
    monkeypatch.setattr(signing.boto3, "client", client_factory)
    with factory().begin() as db:
        db.delete(db.get(SystemState, signing.KEY_STATE))
        db.flush()
        signing.bind_signing_key(db)
        signed = signing.sign_start(db, grant(environment="qa"))
        assert signed["key_id"] == key_id and len(calls) == 2
        key.public_key().verify(base64.b64decode(signed["signature"]),
            signing.DOMAIN.encode() + canonical(signed["grant"]), ec.ECDSA(hashes.SHA256()))
        with pytest.raises(Problem, match="CAPTURE_SIGNING_SCOPE_MISMATCH"):
            signing.sign_start(db, grant(environment="test"))


def test_cloud_key_cannot_reference_other_account_or_alias(monkeypatch):
    cfg = SimpleNamespace(environment="qa", aws_region="us-east-2", deployment_account="123456789012",
        capture_signing_key_id="arn:aws:kms:us-east-2:999999999999:alias/unverified")
    monkeypatch.setattr(signing.boto3, "client", lambda *a, **kw: pytest.fail("Invalid authority must be rejected before network"))
    with pytest.raises(Problem, match="CAPTURE_SIGNING_KEY_UNAVAILABLE"):
        signing.cloud_key(cfg)


@pytest.mark.parametrize("stage", ["connect", "public", "sign", "missing_signature", "invalid_signature"])
def test_cloud_signing_provider_failures_are_controlled_retryable_and_publish_no_authority(client, monkeypatch, stage):
    key = ec.generate_private_key(ec.SECP256R1())
    spki = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    key_id = "arn:aws:kms:us-east-2:123456789012:key/00000000-0000-4000-8000-000000000001"
    cfg = SimpleNamespace(environment="qa", aws_region="us-east-2", deployment_account="123456789012", capture_signing_key_id=key_id)

    class KMS:
        def get_public_key(self, **request):
            if stage == "public":
                raise ClientError({"Error": {"Code": "AccessDeniedException", "Message": "private provider details"}}, "GetPublicKey")
            return {"KeyId": key_id, "KeySpec": "ECC_NIST_P256", "KeyUsage": "SIGN_VERIFY",
                "SigningAlgorithms": ["ECDSA_SHA_256"], "PublicKey": spki}

        def sign(self, **request):
            if stage == "sign":
                raise EndpointConnectionError(endpoint_url="https://private.invalid")
            return {"KeyId": key_id, "SigningAlgorithm": "ECDSA_SHA_256",
                **({} if stage == "missing_signature" else {"Signature": b"not-a-DER-signature"})}

    def provider(*args, **options):
        if stage == "connect":
            raise EndpointConnectionError(endpoint_url="https://private.invalid")
        return KMS()

    monkeypatch.setattr(signing, "settings", lambda: cfg)
    monkeypatch.setattr(signing.boto3, "client", provider)
    with factory().begin() as db:
        db.delete(db.get(SystemState, signing.KEY_STATE))
        db.flush()
        if stage not in {"connect", "public"}:
            signing.bind_signing_key(db)
        with pytest.raises(Problem) as denied:
            signing.sign_start(db, grant(environment="qa"))
        assert denied.value.status == 503
        assert denied.value.retryable is True
        assert denied.value.code == ("CAPTURE_SIGNING_KEY_UNAVAILABLE" if stage in {"connect", "public"} else "CAPTURE_SIGNING_FAILED")
