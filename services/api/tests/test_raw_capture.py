"""Fictional signed ADC values verify software custody, never sensor validity."""

import base64
import hashlib
import io
import os
from copy import deepcopy
from types import SimpleNamespace
from urllib.parse import urlsplit
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from otgd import raw_capture as raw
from otgd.canonical import canonical, digest
from otgd.db import Artifact, factory, iso, now
from otgd.domain import record
from otgd.errors import Problem

from .conftest import headers
from .governance_fixture import (
    CALIBRATION,
    DEVICE,
    KEY,
    POLICY,
    PROTOCOL,
    STUDY,
    adc_material,
    acknowledge_cardiac,
    approve,
    calibration,
    configuration,
    device,
    proof,
    retention,
    study,
)
from .test_operator_governance import consent


def signed(key, envelope, payload):
    envelope = {**envelope, "payload_sha256": digest(payload)}
    return {
        "envelope": envelope,
        "normalized_payload": payload,
        "signature": base64.b64encode(
            key.sign(
                b"OTGD-CAPTURE-v1\n" + canonical(envelope), ec.ECDSA(hashes.SHA256())
            )
        ).decode(),
    }


def fixture():
    private = ec.generate_private_key(ec.SECP256R1())
    material = {
        **adc_material("ecg"),
        "duration_ms": 1000,
        "sample_rate_hz": 20,
        "raw_unit": "mV",
        "raw_sample_limit": 20,
        "raw_encoding": "otgd_ecg_samples_v1",
    }
    config = {"material": material, "sha256": digest(material), "channel": "ecg"}
    scope = {
        "environment": "test",
        "owner_ref": str(uuid4()),
        "data_generation": 1,
        "session_id": str(uuid4()),
    }
    envelope = {
        **scope,
        "schema_version": "1.0.0",
        "attempt_id": str(uuid4()),
        "authorization_id": str(uuid4()),
        "binding_id": str(uuid4()),
        "device_id": DEVICE,
        "key_id": KEY,
        "boot_id": str(uuid4()),
        "sequence": 2,
        "configuration_hash": config["sha256"],
    }
    payload = {
        "schema_version": "1.0.0",
        "channel": "ecg",
        "first_sample_index": 0,
        "sample_rate_hz": 20,
        "units": "uV",
        "contact": "good",
        "dropped_before": 0,
        "acquisition_started_monotonic_us": 1000000,
        "acquisition_ended_monotonic_us": 1900000,
        "samples": [
            {"monotonic_us": 1000000, "value": 100},
            {"monotonic_us": 1050000, "value": -120},
        ],
    }
    projection = {"status": "invalid", "source": "prototype_sensor", "modality": "ecg"}
    final = {
        "attestation_id": str(uuid4()),
        **signed(private, {**envelope, "sequence": 3}, projection),
    }
    value = {
        "schema_version": "1.0.0",
        **final,
        "sample_chunks": [signed(private, envelope, payload)],
    }
    attempt = {
        "attempt_id": envelope["attempt_id"],
        "attestation_refs": [final["attestation_id"]],
        "component_metadata": {"projection": projection},
    }
    permission = {"record": True}
    authority = {
        "state": "started",
        "authorization_id": envelope["authorization_id"],
        "binding_id": envelope["binding_id"],
        "device_id": DEVICE,
        "device_boot_id": envelope["boot_id"],
        "configuration_submitted_sha256": digest(config),
        "raw_recording_permission": permission,
        "server_start": {"grant": {"raw_recording_permission": permission}},
    }
    key = {
        "key_id": KEY,
        "public_key_spki": base64.b64encode(
            private.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        ).decode(),
    }
    return SimpleNamespace(
        private=private,
        config=config,
        scope=scope,
        value=value,
        attempt=attempt,
        authority=authority,
        accepted=final,
        key=key,
    )


def encoded(value):
    return raw.ECG_MAGIC + canonical(value)


def validate(f, value=None):
    return raw.validate_ecg(
        encoded(value or f.value),
        f.attempt,
        f.config,
        f.authority,
        f.accepted,
        f.key,
        f.scope,
    )


def test_original_device_signatures_and_signed_clock_bounds_verify_without_creating_health_values():
    f = fixture()
    result = validate(f)
    assert result["codec"] == "otgd_ecg_samples_v1" and result[
        "evidence_sha256"
    ] == digest(f.accepted)
    assert (
        result["sequences"][0]["payload_sha256"]
        == f.value["sample_chunks"][0]["envelope"]["payload_sha256"]
    )
    assert "samples" not in result and "probability" not in result


def test_genuinely_signed_sample_at_the_end_of_acquisition_is_rejected():
    f = fixture()
    value = deepcopy(f.value)
    chunk = value["sample_chunks"][0]
    chunk["normalized_payload"]["samples"][-1]["monotonic_us"] = chunk[
        "normalized_payload"
    ]["acquisition_ended_monotonic_us"]
    value["sample_chunks"][0] = signed(
        f.private, chunk["envelope"], chunk["normalized_payload"]
    )
    with pytest.raises(Problem, match="RAW_SAMPLE_CLOCK_INVALID"):
        validate(f, value)


@pytest.mark.parametrize(
    "change",
    [
        {"VersionId": "foreign-version"},
        {"VersionId": "null"},
        {"ContentLength": 1},
        {"ContentLength": True},
        {"ContentType": "text/plain"},
    ],
)
def test_storage_must_confirm_the_exact_version_even_with_identical_payload_bytes(
    monkeypatch, change
):
    from otgd import storage

    data = encoded(fixture().value)
    artifact = SimpleNamespace(
        kind="ecg_waveform",
        size=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        media_type="application/octet-stream",
        bucket="fictional",
        key="fictional",
    )
    stream = io.BytesIO(data)

    class Store:
        def get_object(self, **request):
            assert request["VersionId"] == "original-version"
            return {
                "VersionId": "original-version",
                "ContentLength": len(data),
                "ContentType": artifact.media_type,
                "Body": stream,
                **change,
            }

    monkeypatch.setattr(storage, "client", lambda *args: Store())
    with pytest.raises(Problem, match="RAW_STORAGE_INVALID"):
        raw.read_raw_version(artifact, "original-version")
    assert stream.closed


def test_storage_failure_and_malformed_body_are_controlled_without_publication(
    monkeypatch,
):
    from botocore.exceptions import EndpointConnectionError
    from otgd import storage

    data = b"fictional"
    artifact = SimpleNamespace(
        kind="ecg_waveform",
        size=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        media_type="application/octet-stream",
        bucket="fictional",
        key="fictional",
    )

    class Unavailable:
        def get_object(self, **request):
            raise EndpointConnectionError(endpoint_url="https://fictional.invalid")

    monkeypatch.setattr(storage, "client", lambda *args: Unavailable())
    with pytest.raises(Problem) as denied:
        raw.read_raw_version(artifact, "original")
    assert denied.value.code == "RAW_STORAGE_UNAVAILABLE" and denied.value.retryable

    class Malformed:
        def get_object(self, **request):
            return {
                "VersionId": "original",
                "ContentLength": len(data),
                "ContentType": artifact.media_type,
                "Body": 42,
            }

    monkeypatch.setattr(storage, "client", lambda *args: Malformed())
    with pytest.raises(Problem, match="RAW_STORAGE_INVALID"):
        raw.read_raw_version(artifact, "original")


@pytest.mark.parametrize(
    "mutation",
    [
        "scope",
        "signature",
        "sequence",
        "hash",
        "extra",
        "missing_clock",
        "clock",
        "outside",
        "index",
        "rate",
        "overflow",
        "unsafe",
    ],
)
def test_phone_changes_do_not_authenticate_raw_device_samples(mutation):
    f = fixture()
    value = deepcopy(f.value)
    chunk = value["sample_chunks"][0]
    p = chunk["normalized_payload"]
    if mutation == "scope":
        chunk["envelope"]["owner_ref"] = str(uuid4())
    elif mutation == "signature":
        chunk["signature"] = f.accepted["signature"]
    elif mutation == "sequence":
        chunk["envelope"]["sequence"] = f.accepted["envelope"]["sequence"]
    elif mutation == "hash":
        chunk["envelope"]["payload_sha256"] = "f" * 64
    elif mutation == "extra":
        p["invented"] = True
    elif mutation == "missing_clock":
        del p["acquisition_ended_monotonic_us"]
    elif mutation == "clock":
        p["acquisition_ended_monotonic_us"] = 3000000
    elif mutation == "outside":
        p["samples"][0]["monotonic_us"] = 999999
    elif mutation == "index":
        p["first_sample_index"] = 1
    elif mutation == "rate":
        p["sample_rate_hz"] = 21
    elif mutation == "overflow":
        p["samples"] *= 33
    elif mutation == "unsafe":
        p["samples"][0]["value"] = 9007199254740992
    # Re-sign semantic violations to prove scope/clock/bounds validation is
    # independent of mere cryptographic signature validity.
    if mutation in {"clock", "outside", "index", "rate", "overflow"}:
        value["sample_chunks"][0] = signed(f.private, chunk["envelope"], p)
    with pytest.raises((Problem, ValueError)):
        validate(f, value)


@pytest.mark.parametrize(
    "raw_bytes",
    [
        b"wrong codec",
        raw.ECG_MAGIC + b"{}",
        raw.ECG_MAGIC + b'{"a":1,"a":2}',
        raw.ECG_MAGIC + b"{",
        raw.ECG_MAGIC + b"[]",
        b"x" * (256 * 1024 + 1),
    ],
)
def test_malformed_noncanonical_or_oversized_raw_stays_unverified(raw_bytes):
    f = fixture()
    with pytest.raises(Problem, match="RAW_CODEC_INVALID"):
        raw.validate_ecg(
            raw_bytes, f.attempt, f.config, f.authority, f.accepted, f.key, f.scope
        )


def test_relabeling_terminal_evidence_or_revoking_signed_record_authority_fails():
    f = fixture()
    value = deepcopy(f.value)
    value["attestation_id"] = str(uuid4())
    with pytest.raises(Problem, match="RAW_TERMINAL_EVIDENCE_MISMATCH"):
        validate(f, value)
    f.authority["raw_recording_permission"] = None
    with pytest.raises(Problem, match="SIGNED_RAW_START_REQUIRED"):
        validate(f)
    f = fixture()
    f.config["material"]["raw_unit"] = "counts"
    with pytest.raises(Problem, match="RAW_CODEC_UNIMPLEMENTED"):
        validate(f)


def test_signed_chunk_monotonic_ranges_sequence_and_explicit_drops_are_consistent():
    f = fixture()
    value = deepcopy(f.value)
    previous = value["sample_chunks"][0]
    second = deepcopy(previous["normalized_payload"])
    second.update(
        first_sample_index=3,
        dropped_before=1,
        samples=[{"monotonic_us": 1150000, "value": 200}],
    )
    value["sample_chunks"].append(
        signed(f.private, {**previous["envelope"], "sequence": 2}, second)
    )
    value["sample_chunks"][0] = signed(
        f.private,
        {**previous["envelope"], "sequence": 1},
        previous["normalized_payload"],
    )
    assert len(validate(f, value)["sequences"]) == 2
    second["acquisition_ended_monotonic_us"] -= 1
    value["sample_chunks"][1] = signed(
        f.private, {**previous["envelope"], "sequence": 2}, second
    )
    with pytest.raises(Problem, match="RAW_SAMPLE_CLOCK_INVALID"):
        validate(f, value)


def setup_owned_ecg(client, account, monkeypatch):
    from otgd import operator_governance as g

    monkeypatch.setitem(g.SOFTWARE_ADAPTERS, "ecg", {"otgd_signed_reader_v1"})
    monkeypatch.setitem(g.PHYSICAL_DRIVERS, "ecg", {"otgd_esp32_adc_v1"})
    f = fixture()
    private = f.private
    material = f.config["material"]
    body = configuration(
        "ecg",
        material=material,
        sha256=digest(material),
        max_duration_ms=1000,
        software_adapter_id="otgd_signed_reader_v1",
        raw_retention_approved=True,
        device_id=DEVICE,
        key_id=KEY,
        calibration_id=CALIBRATION,
        approved_hardware=["fixture-hw"],
        approved_firmware=["fixture-fw"],
    )
    with factory().begin() as db:
        for kind, item in (
            ("study", study(account, {"ecg": body["registry_id"]})),
            ("retention", retention()),
            ("device", device(account, private)),
            ("calibration", calibration()),
            ("qualification", proof("ecg", body)),
            ("configuration", body),
        ):
            approve(db, kind, item)
        config = g.active_body(db, "configuration", body["registry_id"])
        policy = g.active_body(db, "retention", POLICY)
    receipt = consent(client, study(account))
    pref = client.post(
        f"/v1/studies/{STUDY}/raw-recording-preferences",
        headers=headers(),
        json={
            "consent_record_id": receipt["consent_record_id"],
            "policy_id": POLICY,
            "policy_version": "v1",
            "policy_sha256": digest(policy),
            "raw_notice_version": policy["raw_notice_version"],
            "raw_notice_sha256": policy["raw_notice_sha256"],
            "acknowledged_at": iso(),
            "choices": {
                "eye_video": {"record": False, "upload": False},
                "ecg_waveform": {"record": True, "upload": True},
            },
        },
    )
    assert pref.status_code == 201, pref.text
    challenge = client.post(
        "/v1/device-bindings/challenges",
        headers=headers(),
        json={"device_id": DEVICE, "key_id": KEY},
    ).json()
    sig = base64.b64encode(
        private.sign(
            b"OTGD-BIND-v1\n" + canonical(challenge["transcript"]),
            ec.ECDSA(hashes.SHA256()),
        )
    ).decode()
    binding = client.post(
        "/v1/device-bindings",
        headers=headers(),
        json={"challenge_id": challenge["challenge_id"], "signature": sig},
    ).json()
    sid, aid, rid = (str(uuid4()) for _ in range(3))
    boot = str(uuid4())
    assert (
        client.post(
            "/v1/sessions",
            headers=headers(),
            json={
                "session_id": sid,
                "mode": "controlled_research",
                "study_id": STUDY,
                "protocol_id": PROTOCOL,
            },
        ).status_code
        == 201
    )
    context = {
        "schema_version": "1.0.0",
        "session_id": sid,
        "context_confirmed_at": iso(),
        "profile_version_id": None,
        "profile_snapshot_sha256": "a" * 64,
        "history_snapshot_sha256": "b" * 64,
        "protocol_id": PROTOCOL,
        "configuration_refs": [
            {
                "id": config["registry_id"],
                "version": "v1",
                "sha256": config["sha256"],
                "scope": "measurement_collection",
            }
        ],
        "baseline_refs": [],
        "self_report_context": None,
        "device_associations": [
            {
                **{
                    k: binding[k]
                    for k in (
                        "binding_id",
                        "device_id",
                        "hardware_revision",
                        "firmware_version",
                    )
                },
                "boot_id": boot,
                "clock_evidence_ref": None,
            }
        ],
    }
    assert (
        client.put(
            f"/v1/sessions/{sid}/context", headers=headers(revision=0), json=context
        ).status_code
        == 200
    )
    attempt = {
        "schema_version": "1.0.0",
        "session_id": sid,
        "attempt_id": aid,
        "component": "cardiac",
        "record_id": rid,
        "supersedes_attempt_id": None,
        "status": "started",
        "source": "prototype_sensor",
        "started_at": iso(),
        "ended_at": None,
        "configuration_id": config["registry_id"],
        "configuration_hash": config["sha256"],
        "quality_flags": [],
        "component_metadata": {"modality": "ecg"},
        "artifact_refs": [],
        "attestation_refs": [],
    }
    assert (
        client.put(
            f"/v1/sessions/{sid}/attempts/{aid}",
            headers=headers(revision=0),
            json=attempt,
        ).status_code
        == 200
    )
    from otgd.operator_governance import active_body
    with factory()() as db:
        approved_config = active_body(db, "configuration", config["registry_id"])
    instruction = acknowledge_cardiac(client, sid, attempt, approved_config)
    grant = client.post(
        f"/v1/sessions/{sid}/capture-authorizations",
        headers=headers(),
        json={
            "attempt_id": aid,
            "channel": "ecg",
            "binding_id": binding["binding_id"],
            "device_id": DEVICE,
            "configuration_id": config["registry_id"],
            "configuration_hash": config["sha256"],
            "raw_recording_kind": "ecg_waveform",
            "instruction_receipt_id": instruction["instruction_receipt_id"],
        },
    ).json()
    start = client.post(
        f"/v1/sessions/{sid}/capture-authorizations/{grant['authorization_id']}/start",
        headers=headers(),
        json={
            "attempt_id": aid,
            "device_boot_id": boot,
            "device_nonce": base64.urlsafe_b64encode(b"N" * 32).decode().rstrip("="),
        },
    )
    assert start.status_code == 200, start.text
    began = start.json()["server_started_at"]
    ended = iso(now() + 0.9)
    attid = str(uuid4())
    projection = {
        "status": "invalid",
        "source": "prototype_sensor",
        "started_at": began,
        "ended_at": ended,
        "quality_flags": ["ADC_SIGNAL_INVALID"],
        "acquisition_config_id": config["registry_id"],
        "modality": "ecg",
        "sample_rate_hz": 20.0,
        "heart_rate_bpm": None,
        "ecg_rmssd_ms": None,
        "ecg_status": "invalid",
        "raw_artifact_id": None,
    }
    terminal = {
        **attempt,
        "status": "invalid",
        "started_at": began,
        "ended_at": ended,
        "quality_flags": projection["quality_flags"],
        "component_metadata": {
            "modality": "ecg",
            "armed_at": attempt["started_at"],
            "instruction_receipt": instruction,
            "projection": projection,
        },
        "attestation_refs": [attid],
    }
    accepted = client.put(
        f"/v1/sessions/{sid}/attempts/{aid}", headers=headers(revision=1), json=terminal
    )
    assert accepted.status_code == 200, accepted.text
    env = {
        **f.value["envelope"],
        "owner_ref": account,
        "session_id": sid,
        "attempt_id": aid,
        "authorization_id": grant["authorization_id"],
        "binding_id": binding["binding_id"],
        "boot_id": boot,
        "configuration_hash": config["sha256"],
        "sequence": 3,
    }
    final = {"attestation_id": attid, **signed(private, env, projection)}
    att = client.post(f"/v1/sessions/{sid}/attestations", headers=headers(), json=final)
    assert att.status_code == 201, att.text
    chunk = signed(
        private,
        {**env, "sequence": 1},
        f.value["sample_chunks"][0]["normalized_payload"],
    )
    bytes_ = encoded({"schema_version": "1.0.0", **final, "sample_chunks": [chunk]})
    with factory()() as db:
        from otgd.db import Account

        a = db.get(Account, account)
        pointer = record(db, a, "raw_preference", STUDY).body
    return SimpleNamespace(
        raw=bytes_,
        sid=sid,
        aid=aid,
        began=began,
        receipt=receipt,
        pointer=pointer,
        config=config,
    )


@pytest.mark.parametrize("forged", [False, True])
def test_http_raw_completion_authenticates_device_chunks_and_keeps_forgery_quarantined(
    client, account, monkeypatch, forged
):
    from otgd import storage

    f = setup_owned_ecg(client, account, monkeypatch)
    data = f.raw
    if forged:
        from otgd.canonical import strict_loads

        value = strict_loads(data[len(raw.ECG_MAGIC) :])
        value["sample_chunks"][0]["normalized_payload"]["samples"][0]["value"] += 1
        data = encoded(value)  # A fresh matching file hash is not a device signature.
    monkeypatch.setattr(
        storage,
        "upload_ticket",
        lambda a: {
            "artifact_id": a.id,
            "method": "PUT",
            "upload_url": "https://fictional.invalid",
            "required_headers": {},
        },
    )
    ticket = client.post(
        "/v1/artifact-uploads",
        headers=headers(),
        json={
            "session_id": f.sid,
            "study_id": STUDY,
            "artifact_kind": "ecg_waveform",
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
            "media_type": "application/octet-stream",
            "consent_record_id": f.receipt["consent_record_id"],
            "retention_policy_id": POLICY,
            "raw_consent_record_id": f.pointer["receipt_id"],
            "attempt_id": f.aid,
            "capture_started_at": f.began,
        },
    )
    assert ticket.status_code == 201, ticket.text
    aid = ticket.json()["artifact_id"]
    monkeypatch.setattr(storage, "verify_artifact", lambda a: "fictional-version")

    class Store:
        def get_object(self, **request):
            return {
                "VersionId": request["VersionId"],
                "ContentLength": len(data),
                "ContentType": "application/octet-stream",
                "Body": io.BytesIO(data),
            }

    monkeypatch.setattr(storage, "client", lambda *args: Store())
    response = client.post(
        f"/v1/artifact-uploads/{aid}/complete",
        headers=headers(),
        json={
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
            "media_type": "application/octet-stream",
        },
    )
    assert response.status_code == (422 if forged else 200), response.text
    with factory()() as db:
        row = db.get(Artifact, aid)
        assert row.state == ("quarantine" if forged else "verified")
        from otgd.db import Account

        evidence = record(db, db.get(Account, account), "raw_verification", aid)
        assert (evidence is None) == forged
        if evidence:
            assert (
                evidence.body["version_id"] == "fictional-version"
                and evidence.body["codec"] == "otgd_ecg_samples_v1"
            )


@pytest.mark.postgres
@pytest.mark.localstack
@pytest.mark.parametrize("forged", [False, True])
def test_live_versioned_upload_authenticates_original_ecg_samples(
    client, account, monkeypatch, forged
):
    """Actual HTTP/S3 custody of fictional signatures; no sensor qualification."""
    import boto3
    import httpx
    from botocore.config import Config
    from otgd import storage
    from otgd.canonical import strict_loads
    from otgd.config import settings
    from otgd.db import Account

    assert factory().kw["bind"].dialect.name == "postgresql", (
        "This mandatory live case requires the disposable PostgreSQL test database"
    )
    endpoint = os.environ.get("OTGD_LIVE_S3_ENDPOINT")
    assert endpoint, "OTGD_LIVE_S3_ENDPOINT is required; live dependencies cannot skip"
    parsed = urlsplit(endpoint)
    assert (
        parsed.scheme == "http"
        and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        and parsed.username is None
        and parsed.password is None
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
    ), "Disposable live S3 tests must target the explicit loopback LocalStack endpoint"
    region = settings().aws_region
    # This client has only explicit fictional credentials and a loopback target;
    # an ambient cloud profile must not redirect or prevent the disposable test.
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_PROFILE", raising=False)
    local = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name=region,
    )
    store = local.client(
        "s3",
        endpoint_url=endpoint,
        region_name=region,
        config=Config(
            signature_version="s3v4",
            ignore_configured_endpoint_urls=True,
            s3={"addressing_style": "path"},
            connect_timeout=5,
            read_timeout=10,
            retries={"max_attempts": 1, "mode": "standard"},
        ),
    )
    bucket = "otgd-raw-codec-ci-" + uuid4().hex
    params = {"Bucket": bucket}
    if region != "us-east-1":
        params["CreateBucketConfiguration"] = {"LocationConstraint": region}
    store.create_bucket(**params)
    try:
        store.put_bucket_versioning(
            Bucket=bucket, VersioningConfiguration={"Status": "Enabled"}
        )
        monkeypatch.setenv("OTGD_ARTIFACT_BUCKET", bucket)
        settings.cache_clear()

        def actual_s3(service, public=False):
            assert service == "s3"
            return store

        monkeypatch.setattr(storage, "client", actual_s3)
        f = setup_owned_ecg(client, account, monkeypatch)
        data = f.raw
        if forged:
            value = strict_loads(data[len(raw.ECG_MAGIC) :])
            value["sample_chunks"][0]["normalized_payload"]["samples"][0]["value"] += 1
            data = encoded(value)
        ticket = client.post(
            "/v1/artifact-uploads",
            headers=headers(),
            json={
                "session_id": f.sid,
                "study_id": STUDY,
                "artifact_kind": "ecg_waveform",
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
                "media_type": "application/octet-stream",
                "consent_record_id": f.receipt["consent_record_id"],
                "retention_policy_id": POLICY,
                "raw_consent_record_id": f.pointer["receipt_id"],
                "attempt_id": f.aid,
                "capture_started_at": f.began,
            },
        )
        assert ticket.status_code == 201, ticket.text
        upload = ticket.json()
        sent = httpx.put(
            upload["upload_url"],
            content=data,
            headers=upload["required_headers"],
            timeout=10,
            trust_env=False,
        )
        assert sent.status_code == 200, sent.text
        artifact_id = upload["artifact_id"]
        with factory()() as db:
            artifact = db.get(Artifact, artifact_id)
            assert artifact.bucket == bucket and artifact.state == "quarantine"
            key = artifact.key
        stored = store.head_object(Bucket=bucket, Key=key)
        version = stored.get("VersionId")
        assert version and version != "null"
        assert stored["ContentLength"] == len(data)
        completed = client.post(
            f"/v1/artifact-uploads/{artifact_id}/complete",
            headers=headers(),
            json={
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
                "media_type": "application/octet-stream",
            },
        )
        assert completed.status_code == (422 if forged else 200), completed.text
        with factory()() as db:
            artifact = db.get(Artifact, artifact_id)
            assert artifact.state == ("quarantine" if forged else "verified")
            evidence = record(
                db, db.get(Account, account), "raw_verification", artifact_id
            )
            assert (evidence is None) == forged
            if evidence:
                assert artifact.version_id == version
                assert evidence.body["version_id"] == version
                assert evidence.body["sha256"] == hashlib.sha256(data).hexdigest()
                assert evidence.body["codec"] == "otgd_ecg_samples_v1"
    finally:
        # Only this UUID-named disposable bucket is inventoried and removed.
        for page in store.get_paginator("list_object_versions").paginate(Bucket=bucket):
            objects = [
                {"Key": item["Key"], "VersionId": item["VersionId"]}
                for category in ("Versions", "DeleteMarkers")
                for item in page.get(category, [])
            ]
            if objects:
                removed = store.delete_objects(
                    Bucket=bucket, Delete={"Objects": objects, "Quiet": True}
                )
                assert not removed.get("Errors"), removed
        store.delete_bucket(Bucket=bucket)
        settings.cache_clear()
