"""Current online acquisition authority signed by a separately pinned P256 key."""

import base64
import hashlib
import os
import re
import stat
from typing import Annotated, Literal

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from pydantic import Field, model_validator
from sqlalchemy import select

from .canonical import canonical
from .config import settings
from .db import SystemState
from .dto import DTO, Name, SHA, UTC, UUID
from .errors import Problem

DOMAIN = "OTGD capture grant v1\u0000"
KEY_STATE = "capture_signing_key"


class RawRecordingPermission(DTO):
    record: Literal[True]
    upload: bool
    receipt_id: UUID
    policy_id: Name
    policy_version: Name
    policy_sha256: SHA
    raw_notice_version: Name
    raw_notice_sha256: SHA


class StartGrant(DTO):
    schema_version: Literal["1.0.0"]
    environment: Literal["local", "qa", "prod", "test"]
    owner_ref: UUID
    data_generation: Annotated[int, Field(ge=1, le=9007199254740991)]
    session_id: UUID
    attempt_id: UUID
    authorization_id: UUID
    binding_id: UUID | None
    device_id: Name | None
    device_key_id: Name | None
    boot_id: Name | None
    channel: Literal["saliva", "eyes", "cardiac", "ecg", "task", "alcohol"]
    configuration_max_duration_ms: Annotated[int, Field(ge=100, le=3600000)]
    configuration_id: Name
    configuration_hash: SHA
    configuration_submitted_sha256: SHA
    configuration_version: Name
    capture_context_sha256: SHA
    issued_at: UTC
    expires_at: UTC
    device_nonce: Name | None
    nonce: UUID
    raw_recording_permission: RawRecordingPermission | None
    participant_protocol_sha256: SHA | None
    instruction_receipt_id: UUID | None

    @model_validator(mode="after")
    def raw_channel(self):
        if ((self.participant_protocol_sha256 is None) != (self.instruction_receipt_id is None)
            or self.channel in ("cardiac", "ecg") and self.instruction_receipt_id is None):
            raise ValueError("Preparation hash and receipt must be present together for cardiac acquisition")
        if self.raw_recording_permission is not None and self.channel not in ("eyes", "ecg"):
            raise ValueError("Raw recording is allowed only for the approved optical or ECG channel")
        return self


def local_key(cfg):
    path = cfg.capture_signing_private_key_file
    descriptor = None
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
        metadata = os.fstat(descriptor)
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077
            or metadata.st_uid != os.geteuid() or metadata.st_nlink != 1
            or not 1 <= metadata.st_size <= 8192):
            raise ValueError()
        raw = os.read(descriptor, 8193)
        after = os.fstat(descriptor)
        fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns", "st_mode", "st_uid", "st_nlink")
        if len(raw) != metadata.st_size or any(getattr(metadata, field) != getattr(after, field) for field in fields):
            raise ValueError()
        key = serialization.load_pem_private_key(raw, password=None)
        if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(key.curve, ec.SECP256R1):
            raise ValueError()
        return key
    except (OSError, ValueError, TypeError, UnsupportedAlgorithm):
        raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def cloud_key(cfg):
    partition = "aws-cn" if cfg.aws_region.startswith("cn-") else "aws-us-gov" if cfg.aws_region.startswith("us-gov-") else "aws"
    key_id = cfg.capture_signing_key_id or ""
    expected = r"arn:" + partition + r":kms:" + re.escape(cfg.aws_region) + ":" + re.escape(cfg.deployment_account or "") + r":key/[0-9a-f-]{36}"
    if not re.fullmatch(expected, key_id):
        raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE")
    suffix = "amazonaws.com.cn" if partition == "aws-cn" else "amazonaws.com"
    try:
        serverless = bool(getattr(cfg, "serverless_mode", False))
        client = boto3.client("kms", region_name=cfg.aws_region,
            endpoint_url="https://kms." + cfg.aws_region + (".api.aws" if serverless else "." + suffix),
            config=Config(ignore_configured_endpoint_urls=True, use_dualstack_endpoint=serverless,
                connect_timeout=3, read_timeout=5,
                retries={"max_attempts": 1, "mode": "standard"}))
        material = client.get_public_key(KeyId=key_id)
    except (BotoCoreError, ClientError):
        raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE", retryable=True) from None
    if not isinstance(material, dict):
        raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE")
    if (material.get("KeyId") != key_id or material.get("KeySpec") != "ECC_NIST_P256"
        or material.get("KeyUsage") != "SIGN_VERIFY"
        or "ECDSA_SHA_256" not in material.get("SigningAlgorithms", [])):
        raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE")
    try:
        raw_public = material["PublicKey"]
        if not isinstance(raw_public, bytes) or not 1 <= len(raw_public) <= 512:
            raise ValueError()
        public = serialization.load_der_public_key(raw_public)
    except (ValueError, KeyError, TypeError, UnsupportedAlgorithm):
        raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE") from None
    if not isinstance(public, ec.EllipticCurvePublicKey) or not isinstance(public.curve, ec.SECP256R1):
        raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE")
    return client, public


def signer(cfg=None):
    cfg = cfg or settings()
    if cfg.environment in ("qa", "prod"):
        key, public = cloud_key(cfg)
        key_id = cfg.capture_signing_key_id
    else:
        key = local_key(cfg)
        public = key.public_key()
        key_id = None
    spki = public.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    fingerprint = hashlib.sha256(spki).hexdigest()
    descriptor = {"schema_version": "1.0.0", "environment": cfg.environment,
        "key_id": key_id or "local-capture-v1:" + fingerprint,
        "public_key_sha256": fingerprint, "public_key_spki": base64.b64encode(spki).decode()}
    return key, public, descriptor


def check_anchor(db, descriptor):
    original = db.scalar(select(SystemState.body).where(SystemState.key == KEY_STATE))
    if original is None:
        raise Problem(503, "CAPTURE_SIGNING_KEY_NOT_BOUND")
    if original != descriptor:
        raise Problem(503, "CAPTURE_SIGNING_KEY_CHANGED")
    return original


def bind_signing_key(db):
    """Maintenance-only first binding; works with Session or migration Connection."""
    _, _, descriptor = signer()
    existing = db.scalar(select(SystemState.body).where(SystemState.key == KEY_STATE))
    if existing is None:
        db.execute(SystemState.__table__.insert().values(key=KEY_STATE, body=descriptor))
    elif existing != descriptor:
        raise Problem(503, "CAPTURE_SIGNING_KEY_CHANGED")
    return descriptor


def require_signing_key(db):
    _, _, descriptor = signer()
    return check_anchor(db, descriptor)


def sign_start(db, grant):
    grant = StartGrant.model_validate(grant).data()
    cfg = settings()
    if grant["environment"] != cfg.environment:
        raise Problem(503, "CAPTURE_SIGNING_SCOPE_MISMATCH")
    key, public, descriptor = signer(cfg)
    check_anchor(db, descriptor)
    raw = DOMAIN.encode() + canonical(grant)
    if cfg.environment in ("qa", "prod"):
        try:
            result = key.sign(KeyId=cfg.capture_signing_key_id,
                Message=hashlib.sha256(raw).digest(), MessageType="DIGEST", SigningAlgorithm="ECDSA_SHA_256")
        except (BotoCoreError, ClientError):
            raise Problem(503, "CAPTURE_SIGNING_FAILED", retryable=True) from None
        if (not isinstance(result, dict) or result.get("KeyId") != cfg.capture_signing_key_id
            or result.get("SigningAlgorithm") != "ECDSA_SHA_256"):
            raise Problem(503, "CAPTURE_SIGNING_KEY_UNAVAILABLE")
        signature = result.get("Signature")
    else:
        signature = key.sign(raw, ec.ECDSA(hashes.SHA256()))
    # A faulty signing provider cannot publish an unverifiable start authority.
    try:
        if not isinstance(signature, bytes) or not 8 <= len(signature) <= 128:
            raise ValueError()
        public.verify(signature, raw, ec.ECDSA(hashes.SHA256()))
    except (InvalidSignature, ValueError, TypeError):
        raise Problem(503, "CAPTURE_SIGNING_FAILED", retryable=True) from None
    return {"grant": grant, "signature": base64.b64encode(signature).decode(),
        "key_id": descriptor["key_id"], "domain": DOMAIN}
