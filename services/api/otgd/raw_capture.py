"""Authenticate bounded raw codecs against accepted owned acquisition evidence."""

import math
from typing import Annotated, Literal

from pydantic import Field, ValidationError
from botocore.exceptions import BotoCoreError, ClientError

from .canonical import canonical, digest, strict_loads
from .db import iso
from .domain import record, verify_signature
from .dto import Attestation, AttestationEnvelope, DTO
from .errors import Problem

ECG_MAGIC = b"OTGD-ECG-SAMPLES-v1\n"
CODEC_LIMITS = {"eye_video": 5 * 1024 * 1024, "ecg_waveform": 256 * 1024}


class Observation(DTO):
    monotonic_us: Annotated[int, Field(ge=0, le=9007199254740991)]
    value: Annotated[int, Field(ge=-2147483648, le=2147483647)]


class Samples(DTO):
    schema_version: Literal["1.0.0"]
    channel: Literal["ecg"]
    first_sample_index: Annotated[int, Field(ge=0, le=1024)]
    sample_rate_hz: Annotated[int, Field(ge=20, le=1000)]
    acquisition_started_monotonic_us: Annotated[int, Field(ge=0, le=9007199254740991)]
    acquisition_ended_monotonic_us: Annotated[int, Field(ge=0, le=9007199254740991)]
    units: Literal["uV"]
    contact: Literal["good", "poor", "lost", "unknown"]
    dropped_before: Annotated[int, Field(ge=0, le=1024)]
    samples: Annotated[list[Observation], Field(min_length=1, max_length=64)]


class Chunk(DTO):
    envelope: AttestationEnvelope
    signature: Annotated[str, Field(min_length=1, max_length=256)]
    normalized_payload: Samples


class ECGRecording(Attestation):
    schema_version: Literal["1.0.0"]
    sample_chunks: Annotated[list[Chunk], Field(min_length=1, max_length=64)]


def codec_limit(kind):
    if kind not in CODEC_LIMITS:
        raise Problem(403, "RAW_CODEC_UNIMPLEMENTED")
    return CODEC_LIMITS[kind]


def read_raw_version(artifact, version):
    """The provider response must confirm the requested immutable version."""
    import hashlib
    from .storage import client

    limit = codec_limit(artifact.kind)
    if not version or version == "null" or not 0 < artifact.size <= limit:
        raise Problem(503, "RAW_STORAGE_INVALID")
    body = None
    try:
        obj = client("s3").get_object(
            Bucket=artifact.bucket, Key=artifact.key, VersionId=version
        )
        body = obj["Body"]
        if (
            obj.get("VersionId") != version
            or type(obj.get("ContentLength")) is not int
            or obj["ContentLength"] != artifact.size
            or obj.get("ContentType") != artifact.media_type
        ):
            raise Problem(503, "RAW_STORAGE_INVALID")
        raw = body.read(artifact.size + 1)
        if (
            not isinstance(raw, bytes)
            or len(raw) != artifact.size
            or hashlib.sha256(raw).hexdigest() != artifact.sha256
        ):
            raise Problem(422, "ARTIFACT_MISMATCH")
        return raw
    except (BotoCoreError, ClientError, OSError):
        raise Problem(503, "RAW_STORAGE_UNAVAILABLE", retryable=True) from None
    except (KeyError, TypeError, AttributeError):
        raise Problem(503, "RAW_STORAGE_INVALID") from None
    finally:
        if body is not None and callable(getattr(body, "close", None)):
            body.close()


def validate_ecg(raw, attempt, config, authority, accepted, key, scope):
    """Each immutable sample payload and its device clock bounds must be signed."""
    if (
        not isinstance(raw, bytes)
        or not 0 < len(raw) <= CODEC_LIMITS["ecg_waveform"]
        or not raw.startswith(ECG_MAGIC)
    ):
        raise Problem(422, "RAW_CODEC_INVALID")
    try:
        value = strict_loads(raw[len(ECG_MAGIC) :])
        parsed = ECGRecording.model_validate(value).data()
        if raw[len(ECG_MAGIC) :] != canonical(value) or parsed != value:
            raise ValueError()
    except (ValueError, TypeError, ValidationError, UnicodeError):
        raise Problem(422, "RAW_CODEC_INVALID") from None
    material = config["material"]
    if (
        config["channel"] != "ecg"
        or material.get("adapter_id") != "otgd_esp32_adc_v1"
        or material.get("raw_unit") != "mV"
        or material.get("raw_encoding") != "otgd_ecg_samples_v1"
        or not 0 < material.get("raw_sample_limit", 0) <= 1024
    ):
        raise Problem(403, "RAW_CODEC_UNIMPLEMENTED")
    final = {
        key: value[key]
        for key in ("attestation_id", "envelope", "signature", "normalized_payload")
    }
    if (
        final != accepted
        or value["attestation_id"] not in attempt["attestation_refs"]
        or value["normalized_payload"]
        != attempt["component_metadata"].get("projection")
    ):
        raise Problem(422, "RAW_TERMINAL_EVIDENCE_MISMATCH")
    envelope = value["envelope"]
    expected = {
        **scope,
        "schema_version": "1.0.0",
        "attempt_id": attempt["attempt_id"],
        "authorization_id": authority["authorization_id"],
        "binding_id": authority["binding_id"],
        "device_id": authority["device_id"],
        "key_id": key["key_id"],
        "boot_id": authority["device_boot_id"],
        "configuration_hash": config["sha256"],
    }
    if any(envelope.get(k) != v for k, v in expected.items()):
        raise Problem(403, "RAW_CAPTURE_SCOPE_MISMATCH")
    permission = (
        authority.get("server_start", {})
        .get("grant", {})
        .get("raw_recording_permission")
    )
    if (
        authority.get("state") != "started"
        or not permission
        or permission.get("record") is not True
        or permission != authority.get("raw_recording_permission")
        or authority.get("configuration_submitted_sha256") != digest(config)
    ):
        raise Problem(403, "SIGNED_RAW_START_REQUIRED")
    if envelope["payload_sha256"] != digest(value["normalized_payload"]):
        raise Problem(422, "RAW_SIGNED_PAYLOAD_MISMATCH")
    verify_signature(
        key["public_key_spki"], value["signature"], "OTGD-CAPTURE-v1\n", envelope
    )
    index, count, sequence, monotonic, anchors = 0, 0, -1, -1, None
    receipts = []
    budget = min(
        material["raw_sample_limit"],
        math.ceil(material["sample_rate_hz"] * material["duration_ms"] / 1000),
    )
    for chunk in value["sample_chunks"]:
        e, p = chunk["envelope"], chunk["normalized_payload"]
        if any(e.get(k) != v for k, v in expected.items()):
            raise Problem(403, "RAW_CAPTURE_SCOPE_MISMATCH")
        if not sequence < e["sequence"] < envelope["sequence"] or e[
            "payload_sha256"
        ] != digest(p):
            raise Problem(422, "RAW_SAMPLE_SEQUENCE_INVALID")
        bounds = (
            p["acquisition_started_monotonic_us"],
            p["acquisition_ended_monotonic_us"],
        )
        if (
            bounds[1] <= bounds[0]
            or bounds[1] - bounds[0] > material["duration_ms"] * 1000
            or (anchors is not None and bounds != anchors)
        ):
            raise Problem(422, "RAW_SAMPLE_CLOCK_INVALID")
        if (
            p["sample_rate_hz"] != material["sample_rate_hz"]
            or p["first_sample_index"] != index + p["dropped_before"]
            or p["first_sample_index"] + len(p["samples"]) > budget
        ):
            raise Problem(422, "RAW_SAMPLE_BOUNDS_INVALID")
        for sample in p["samples"]:
            at = sample["monotonic_us"]
            if at <= monotonic or not bounds[0] <= at < bounds[1]:
                raise Problem(422, "RAW_SAMPLE_CLOCK_INVALID")
            monotonic = at
        verify_signature(
            key["public_key_spki"], chunk["signature"], "OTGD-CAPTURE-v1\n", e
        )
        count += len(p["samples"])
        index = p["first_sample_index"] + len(p["samples"])
        sequence, anchors = e["sequence"], bounds
        receipts.append(
            {
                "sequence_id": digest(
                    [e["device_id"], e["key_id"], e["boot_id"], e["sequence"]]
                ),
                "payload_sha256": e["payload_sha256"],
            }
        )
    if count > budget:
        raise Problem(422, "RAW_SAMPLE_BOUNDS_INVALID")
    return {
        "codec": "otgd_ecg_samples_v1",
        "evidence_sha256": digest(final),
        "sequences": receipts,
    }


def validate_raw_artifact(db, account, artifact, config, raw):
    """Called only after exact version/hash verification, again under commit locks."""
    from .config import settings
    from .operator_governance import active_body, qualified_binding, started_capture
    from .raw_retention import RawRetention
    from .domain import owned_check

    if len(raw) > codec_limit(artifact.kind):
        raise Problem(413, "RAW_CODEC_LIMIT_EXCEEDED")
    lifetime = db.get(RawRetention, artifact.id)
    if not lifetime:
        raise Problem(403, "RAW_AUTHORITY_INTEGRITY_FAILURE")
    attempt = record(db, account, "attempt", lifetime.authority["attempt_id"])
    check = owned_check(db, account, artifact.session_id)
    if (
        not attempt
        or attempt.parent_id != check.id
        or attempt.sha256 != digest(attempt.body)
        or attempt.body["status"] not in ("valid", "invalid")
        or attempt.body["source"] != "prototype_sensor"
    ):
        raise Problem(403, "ACCEPTED_RAW_ACQUISITION_REQUIRED")
    authority = started_capture(db, account, check, attempt.body, config)
    permission = authority.body.get("raw_recording_permission")
    if (
        not permission
        or not permission["record"]
        or not permission["upload"]
        or permission["receipt_id"] != lifetime.authority["raw_consent_record_id"]
    ):
        raise Problem(403, "SIGNED_RAW_UPLOAD_REQUIRED")
    if artifact.kind == "eye_video":
        from .optical_evidence import validate_roi_artifact

        validate_roi_artifact(raw, attempt.body, config)
        return {
            "codec": "otgd_eye_roi_v1",
            "evidence_sha256": digest(
                attempt.body["component_metadata"]["native_result"]
            ),
            "sequences": [],
        }
    try:
        decoded = (
            strict_loads(raw[len(ECG_MAGIC) :]) if raw.startswith(ECG_MAGIC) else None
        )
        final_id = decoded.get("attestation_id") if isinstance(decoded, dict) else None
    except (ValueError, UnicodeError, TypeError):
        raise Problem(422, "RAW_CODEC_INVALID") from None
    accepted = (
        record(db, account, "attestation", final_id)
        if isinstance(final_id, str)
        else None
    )
    if (
        not accepted
        or accepted.parent_id != check.id
        or accepted.sha256 != digest(accepted.body)
    ):
        raise Problem(403, "ACCEPTED_DEVICE_ATTESTATION_REQUIRED")
    key = active_body(
        db,
        "device",
        authority.body["device_id"] + ":" + accepted.body["envelope"]["key_id"],
    )
    binding = record(db, account, "binding", authority.body["binding_id"])
    qualified_binding(db, account, config, binding)
    return validate_ecg(
        raw,
        attempt.body,
        config,
        authority.body,
        accepted.body,
        key,
        {
            "environment": settings().environment,
            "owner_ref": account.id,
            "data_generation": account.generation,
            "session_id": check.id,
        },
    )


def verification_receipt(artifact, config, version, evidence):
    return {
        "schema_version": "1.0.0",
        "artifact_id": artifact.id,
        "version_id": version,
        "sha256": artifact.sha256,
        "codec": evidence["codec"],
        "attempt_id": artifact.scope["attempt_id"],
        "configuration_id": config["configuration_id"],
        "configuration_sha256": config["sha256"],
        "configuration_submitted_sha256": digest(config),
        "evidence_sha256": evidence["evidence_sha256"],
        "verified_at": iso(),
    }
