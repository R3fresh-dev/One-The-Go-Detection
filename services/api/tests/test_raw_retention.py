"""Optional raw authority and cleanup regressions with disposable fictional data."""

from copy import deepcopy
from types import SimpleNamespace
import hashlib
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from pydantic import ValidationError

from otgd import db as database
from otgd import raw_retention as raw
from otgd.canonical import digest, strict_loads
from otgd.db import (
    Account,
    Artifact,
    Base,
    Check,
    Record,
    Registry,
    RegistryVersion,
    iso,
)
from otgd.domain import rec_id
from otgd.dto import ArtifactRequest
from otgd.errors import Problem
from .governance_fixture import (
    approve,
    configuration,
    device,
    calibration,
    proof,
    adc_material,
)

TICK = 1791676800.0
ACCOUNT = "10000000-0000-4000-8000-000000000001"
CHECK = "20000000-0000-4000-8000-000000000001"
CONSENT = "30000000-0000-4000-8000-000000000001"
ATTEMPT = "40000000-0000-4000-8000-000000000001"
ARTIFACT = "50000000-0000-4000-8000-000000000001"
POLICY = {
    "schema_version": "1.0.0",
    "registry_id": "FICTIONAL-RAW-POLICY",
    "policy_id": "FICTIONAL-RAW-POLICY",
    "version": "v1",
    "study_id": "FICTIONAL-STUDY",
    "expires_at": TICK + 864000,
    "evidence_ref": "FICTIONAL-EVIDENCE",
    "evidence_sha256": "a" * 64,
    "purpose_id": "FICTIONAL-EYE-ECG-RESEARCH",
    "purpose_text": "Fictional optional raw research only",
    "raw_kinds": ["eye_video", "ecg_waveform"],
    "max_retention_days": 2,
    "access_roles": ["lab_report_revision"],
    "withdrawal_behavior": "delete_live_data",
    "exceptions": [],
    "raw_notice_version": "v1",
    "raw_notice_text": "FICTIONAL OPTIONAL RAW PURPOSE. No study is approved.",
    "raw_notice_sha256": hashlib.sha256(
        b"FICTIONAL OPTIONAL RAW PURPOSE. No study is approved."
    ).hexdigest(),
}


def release(db, kind, id, body):
    assert body["registry_id"] == id
    approve(db, kind, deepcopy(body))
    db.flush()


@pytest.fixture
def fixture(monkeypatch):
    monkeypatch.setattr(raw, "now", lambda: TICK)
    monkeypatch.setattr(database, "now", lambda: TICK)
    monkeypatch.setattr("otgd.operator_governance.now", lambda: TICK)
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine, expire_on_commit=False)
    with sessions.begin() as db:
        a = Account(id=ACCOUNT, subject_hash="1" * 64, generation=1, state="active")
        check = Check(
            id=CHECK,
            account_id=ACCOUNT,
            generation=1,
            state="draft",
            mode="analytical",
            study_id="FICTIONAL-STUDY",
            protocol_id="FICTIONAL-PROTOCOL",
            created=TICK - 50,
        )
        db.add_all([a, check])
        study_text = "FICTIONAL-STUDY. Software fixtures have no human-study approval."
        study = {
            "schema_version": "1.0.0",
            "registry_id": check.study_id,
            "study_id": check.study_id,
            "protocol_id": check.protocol_id,
            "version": "v1",
            "name": "Fictional raw lifecycle study",
            "evidence_ref": "FICTIONAL-EVIDENCE",
            "evidence_sha256": "e" * 64,
            "account_refs": [ACCOUNT],
            "invitation_id": "FICTIONAL-INVITATION",
            "document_version": "v1",
            "document_text": study_text,
            "document_sha256": hashlib.sha256(study_text.encode()).hexdigest(),
            "retention_summary": "Fictional separate optional raw policy",
            "channels": {"eyes": "FICTIONAL-EYE-CONFIG", "ecg": "FICTIONAL-ECG-CONFIG"},
            "expires_at": TICK + 864000,
        }
        release(db, "study", check.study_id, study)
        release(db, "retention", POLICY["policy_id"], POLICY)
        device_body = device(ACCOUNT)
        device_body["approved_protocol_ids"] = [check.protocol_id]
        release(db, "device", device_body["registry_id"], device_body)
        calibration_body = calibration()
        release(db, "calibration", calibration_body["registry_id"], calibration_body)
        for kind, channel in raw.CHANNELS.items():
            id = study["channels"][channel]
            config = configuration(
                channel,
                raw_retention_approved=True,
                **(
                    {"optical_safety_ref": "FICTIONAL-OPTICAL-SAFETY"}
                    if channel == "eyes"
                    else {
                        "device_id": device_body["device_id"],
                        "key_id": device_body["key_id"],
                        "calibration_id": calibration_body["calibration_id"],
                        "approved_hardware": [device_body["hardware_revision"]],
                        "approved_firmware": [device_body["firmware_version"]],
                    }
                ),
            )
            if channel == "eyes":
                material = strict_loads(
                    (
                        Path(__file__).resolve().parents[3]
                        / "apps/mobile/modules/eye-capture/fixtures/eye-golden-v1.json"
                    ).read_bytes()
                )["configuration"]
                config.update(
                    material=material,
                    sha256=digest(material),
                    software_adapter_id="optical_roi_v1",
                    max_duration_ms=material["duration_ms"],
                    supported_os_versions=["FICTIONAL-OS"],
                    supported_native_builds=["0.1.0:1"],
                )
            else:
                material = {
                    **adc_material("ecg"),
                    "duration_ms": 5000,
                    "raw_unit": "mV",
                    "raw_sample_limit": 500,
                    "raw_encoding": "otgd_ecg_samples_v1",
                }
                config.update(
                    material=material,
                    sha256=digest(material),
                    software_adapter_id="otgd_signed_reader_v1",
                    max_duration_ms=material["duration_ms"],
                )
            config.update(
                registry_id=id,
                configuration_id=id,
                study_id=check.study_id,
                protocol_id=check.protocol_id,
                retention_policy_id=POLICY["policy_id"],
            )
            evidence = proof(channel, config_body=config)
            release(db, "qualification", evidence["registry_id"], evidence)
            release(db, "configuration", id, config)
        consent = {
            "state": "active",
            "consent_record_id": CONSENT,
            **{
                k: study[k]
                for k in ("invitation_id", "document_version", "document_sha256")
            },
        }
        db.add(
            Record(
                id=rec_id(a, "consent", check.study_id),
                account_id=ACCOUNT,
                generation=1,
                kind="consent",
                body=consent,
                sha256=digest(consent),
                created=TICK - 100,
            )
        )
    yield SimpleNamespace(sessions=sessions, engine=engine)
    engine.dispose()


def preference(**changes):
    return raw.RawPreferences.model_validate(
        {
            "consent_record_id": CONSENT,
            "policy_id": POLICY["policy_id"],
            "policy_version": "v1",
            "policy_sha256": digest(POLICY),
            "raw_notice_version": "v1",
            "raw_notice_sha256": POLICY["raw_notice_sha256"],
            "acknowledged_at": iso(TICK),
            "choices": {
                "eye_video": {"record": True, "upload": True},
                "ecg_waveform": {"record": False, "upload": False},
            },
            **changes,
        }
    )


def consent_and_attempt(db, *, kind="eye_video", **preference_changes):
    a, check = db.get(Account, ACCOUNT), db.get(Check, CHECK)
    status = raw.set_preferences(
        db, a, check.study_id, preference(**preference_changes)
    )
    study = raw.active_body(db, "study", check.study_id)
    config = raw.active_body(db, "configuration", study["channels"][raw.CHANNELS[kind]])
    body = {
        "component": "eyes" if kind == "eye_video" else "cardiac",
        "started_at": iso(TICK + 1),
        "status": "started",
        "configuration_id": config["configuration_id"],
        "configuration_hash": config["sha256"],
        "component_metadata": {"modality": "ecg"} if kind == "ecg_waveform" else {},
    }
    db.add(
        Record(
            id=rec_id(a, "attempt", ATTEMPT),
            account_id=ACCOUNT,
            generation=1,
            kind="attempt",
            parent_id=CHECK,
            body=body,
            sha256=digest(body),
            created=TICK + 1,
        )
    )
    db.flush()
    request = ArtifactRequest(
        study_id=check.study_id,
        session_id=CHECK,
        consent_record_id=CONSENT,
        retention_policy_id=POLICY["policy_id"],
        artifact_kind=kind,
        sha256="d" * 64,
        size_bytes=128,
        media_type="application/octet-stream",
        raw_consent_record_id=status["receipt_id"],
        attempt_id=ATTEMPT,
        capture_started_at=body["started_at"],
    )
    return a, check, request


def attach(db, a, check, request, *, id=ARTIFACT):
    study = raw.active_body(db, "study", check.study_id)
    config = raw.active_body(
        db, "configuration", study["channels"][raw.CHANNELS[request.artifact_kind]]
    )
    authority = raw.admit_artifact(db, a, check, request, config)
    artifact = Artifact(
        id=id,
        account_id=ACCOUNT,
        generation=1,
        session_id=CHECK,
        bucket="fictional-raw-bucket",
        key="quarantine/fictional/" + id,
        sha256=request.sha256,
        size=128,
        media_type=request.media_type,
        kind=request.artifact_kind,
        state="quarantine",
        expires=TICK + 300,
        scope=request.data(),
    )
    db.add(artifact)
    row = raw.attach_retention(db, artifact, authority)
    db.flush()
    return artifact, row


def seed_verified_native_receipt(db, account, artifact):
    """Explicit accepted-record fixture; codec execution is tested independently."""
    from .test_optical_evidence import fixture as native_fixture
    from otgd.raw_capture import verification_receipt

    lifetime = db.get(raw.RawRetention, artifact.id)
    config = raw.active_body(
        db, "configuration", lifetime.authority["configuration_id"]
    )
    attempt = raw.record(db, account, "attempt", lifetime.authority["attempt_id"])
    native, projection, _ = native_fixture()
    native.update(
        started_at=attempt.body["started_at"],
        ended_at=iso(raw.timestamp(attempt.body["started_at"]) + 1),
        configuration_sha256=config["sha256"],
    )
    projection.update(
        started_at=native["started_at"],
        ended_at=native["ended_at"],
        capture_config_id=config["configuration_id"],
    )
    attempt.body = {
        **attempt.body,
        "schema_version": "1.0.0",
        "session_id": artifact.session_id,
        "attempt_id": lifetime.authority["attempt_id"],
        "supersedes_attempt_id": None,
        "quality_flags": native["quality_flags"],
        "artifact_refs": [],
        "attestation_refs": [],
        "source": "prototype_sensor",
        "status": "valid",
        "record_id": native["run_id"],
        "ended_at": native["ended_at"],
        "component_metadata": {"native_result": native, "projection": projection},
    }
    attempt.sha256 = digest(attempt.body)
    body = verification_receipt(
        artifact,
        config,
        artifact.version_id,
        {"codec": "otgd_eye_roi_v1", "evidence_sha256": digest(native)},
    )
    raw._put_record(db, account, "raw_verification", artifact.id, body)
    receipt = raw.record(db, account, "raw_verification", artifact.id)
    receipt.parent_id = artifact.session_id
    db.flush()
    return receipt


class VersionedStore:
    """Unit double models conditional PUTs and actual version/delete marker identities."""

    def __init__(self):
        self.objects = {}
        self.deleted = []
        self.fail = False

    def put(self, key, version):
        if self.objects.get(key):
            return 412
        self.objects[key] = [version]
        return 200

    def get_paginator(self, name):
        assert name == "list_object_versions"
        return self

    def paginate(self, **args):
        yield {
            "Versions": [
                {"Key": key, "VersionId": version}
                for key, versions in self.objects.items()
                for version in versions
                if key.startswith(args["Prefix"]) and not version.startswith("marker")
            ],
            "DeleteMarkers": [
                {"Key": key, "VersionId": version}
                for key, versions in self.objects.items()
                for version in versions
                if key.startswith(args["Prefix"]) and version.startswith("marker")
            ],
        }

    def delete_object(self, **args):
        if self.fail:
            raise RuntimeError("Fictional dependency failure")
        self.deleted.append(args)
        versions = self.objects.get(args["Key"], [])
        if args["VersionId"] in versions:
            versions.remove(args["VersionId"])


def test_raw_defaults_separate_receipt_and_exact_public_policy(fixture):
    with fixture.sessions.begin() as db:
        a = db.get(Account, ACCOUNT)
        initial = raw.raw_status(db, a, "FICTIONAL-STUDY")
        assert initial["choices"] == raw.off() and initial["receipt_id"] is None
        assert initial["policy"]["sha256"] == digest(initial["policy"]["content"])
        assert (
            initial["policy"]["raw_notice"]["sha256"]
            == hashlib.sha256(
                initial["policy"]["raw_notice"]["content"].encode()
            ).hexdigest()
        )
        accepted = raw.set_preferences(db, a, "FICTIONAL-STUDY", preference())
        assert accepted["choices"]["eye_video"] == {"record": True, "upload": True}
        assert (
            db.get(Record, rec_id(a, "consent", "FICTIONAL-STUDY")).body[
                "consent_record_id"
            ]
            == CONSENT
        )
        assert (
            db.get(Record, rec_id(a, "raw_consent_receipt", accepted["receipt_id"]))
            is not None
        )


def test_actual_status_matches_mobile_cross_language_fixture(fixture, monkeypatch):
    monkeypatch.setattr(raw, "uid", lambda: "60000000-0000-4000-8000-000000000001")
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        attach(db, a, check, request)
        expected = strict_loads(
            (
                Path(__file__).resolve().parents[3]
                / "apps/mobile/testfixtures/backend-raw-recordings.json"
            ).read_bytes()
        )
        assert raw.raw_status(db, a, check.study_id) == expected


def test_participant_raw_status_excludes_same_study_administrative_report(fixture):
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        attach(db, a, check, request)
        report_id = "50000000-0000-4000-8000-000000000099"
        report = Artifact(
            id=report_id,
            account_id=ACCOUNT,
            generation=1,
            session_id=CHECK,
            bucket="fictional-administrative",
            key="fictional/report",
            sha256="f" * 64,
            size=10,
            media_type="application/pdf",
            kind="source_lab_report",
            state="quarantine",
            expires=TICK + 300,
            scope={"study_id": check.study_id},
        )
        db.add(report)
        db.flush()
        db.add(
            raw.RawRetention(
                artifact_id=report_id,
                account_id=ACCOUNT,
                generation=1,
                study_id=check.study_id,
                kind="source_lab_report",
                bucket=report.bucket,
                key=report.key,
                authority={"separate_administrative_purpose": True},
                retained_until=TICK + 86400,
                state="retained",
                cleanup_next_at=0,
            )
        )
        db.flush()
        assert [
            item["artifact_kind"]
            for item in raw.raw_status(db, a, check.study_id)["artifacts"]
        ] == ["eye_video"]


@pytest.mark.parametrize(
    "changes",
    [
        {"policy_sha256": "0" * 64},
        {"policy_version": "v2"},
        {"raw_notice_sha256": "0" * 64},
        {"raw_notice_version": "v2"},
        {"consent_record_id": ATTEMPT},
        {"acknowledged_at": iso(TICK + 6)},
        {"acknowledged_at": iso(TICK - 86401)},
    ],
)
def test_stale_or_unreviewed_preferences_never_grant(fixture, changes):
    with fixture.sessions.begin() as db:
        with pytest.raises(Problem):
            raw.set_preferences(
                db, db.get(Account, ACCOUNT), "FICTIONAL-STUDY", preference(**changes)
            )


def test_upload_without_record_and_duplicate_revoke_are_invalid():
    with pytest.raises(ValidationError):
        raw.RawChoice(record=False, upload=True)
    with pytest.raises(ValidationError):
        raw.RawRevocation(confirmation=True, artifact_kinds=["eye_video", "eye_video"])


@pytest.mark.parametrize(
    "change",
    [
        "no_receipt",
        "no_attempt",
        "wrong_start",
        "foreign_attempt",
        "wrong_component",
        "wrong_configuration",
        "wrong_configuration_hash",
        "no_upload",
        "revoked_study",
        "exceptions",
        "expired_policy",
        "tampered_policy",
    ],
)
def test_acquisition_requires_live_exact_optional_authority(fixture, change):
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        config = raw.active_body(
            db,
            "configuration",
            raw.active_body(db, "study", check.study_id)["channels"]["eyes"],
        )
        if change == "no_receipt":
            request.raw_consent_record_id = None
        elif change == "no_attempt":
            request.attempt_id = None
        elif change == "wrong_start":
            request.capture_started_at = iso(TICK + 2)
        elif change in (
            "foreign_attempt",
            "wrong_component",
            "wrong_configuration",
            "wrong_configuration_hash",
        ):
            attempt = db.get(Record, rec_id(a, "attempt", ATTEMPT))
            if change == "foreign_attempt":
                attempt.parent_id = CONSENT
            elif change == "wrong_component":
                attempt.body = {**attempt.body, "component": "task"}
            elif change == "wrong_configuration":
                attempt.body = {
                    **attempt.body,
                    "configuration_id": "FICTIONAL-WRONG-CONFIGURATION",
                }
            else:
                attempt.body = {**attempt.body, "configuration_hash": "0" * 64}
            attempt.sha256 = digest(attempt.body)
        elif change == "no_upload":
            pointer = db.get(Record, rec_id(a, "raw_preference", check.study_id))
            pointer.body = {**pointer.body, "choices": raw.off()}
            pointer.sha256 = digest(pointer.body)
        elif change == "revoked_study":
            db.get(Registry, "study:" + check.study_id).active = False
        else:
            version = db.scalar(
                select(RegistryVersion).where(RegistryVersion.kind == "retention")
            )
            policy = {**version.body}
            policy.update(
                {"exceptions": ["undefined-legal-hold"]}
                if change == "exceptions"
                else {"expires_at": TICK - 1}
                if change == "expired_policy"
                else {"purpose_text": "changed"}
            )
            version.body = policy
            if change != "tampered_policy":
                version.sha256 = digest(policy)
                db.get(Registry, version.registry_key).body = policy
        with pytest.raises(Problem):
            raw.admit_artifact(
                db,
                a,
                check,
                request,
                config,
            )


def test_retention_frozen_before_completion_and_same_bytes_cannot_extend(
    fixture, monkeypatch
):
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        artifact, ledger = attach(db, a, check, request)
        due = ledger.retained_until
        assert due == TICK + 1 + 2 * 86400
        assert raw.assert_artifact_admitted(db, a, artifact).retained_until == due
        artifact.version_id, artifact.state = "verified-original-version", "verified"
        seed_verified_native_receipt(db, a, artifact)
        monkeypatch.setattr(raw, "now", lambda: TICK + 200)
        assert raw.assert_artifact_admitted(db, a, artifact).retained_until == due
        with pytest.raises(Problem, match="RAW_RETENTION_ALREADY_FROZEN"):
            raw.attach_retention(db, artifact, ledger.authority)
        # Even after the original payload hash is cleared during purge, its
        # frozen hash prevents a new ticket from extending the same bytes.
        artifact.sha256 = "0" * 64
        attempt = db.get(Record, rec_id(a, "attempt", ATTEMPT))
        attempt.body = {**attempt.body, "started_at": iso(TICK + 200)}
        attempt.sha256 = digest(attempt.body)
        attempt.created = TICK + 200
        request.capture_started_at = iso(TICK + 200)
        config = raw.active_body(
            db,
            "configuration",
            raw.active_body(db, "study", check.study_id)["channels"]["eyes"],
        )
        authority = raw.admit_artifact(
            db,
            a,
            check,
            request,
            config,
        )
        assert authority["retained_until"] == due


def test_revocation_keeps_conditional_write_barrier_until_ticket_deadline(fixture):
    store = VersionedStore()
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        artifact, ledger = attach(db, a, check, request)
        key = artifact.key
        assert store.put(key, "first-put") == 200
        response = raw.revoke_raw(
            db,
            a,
            check.study_id,
            raw.RawRevocation(confirmation=True, artifact_kinds=["eye_video"]),
        )
        assert response["revocations"][0]["state"] == "cleanup_pending"
        with pytest.raises(Problem):
            raw.assert_artifact_admitted(db, a, artifact)
    assert raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 1) == {
        "processed": 0,
        "failures": 0,
    }
    assert store.put(key, "replay-before-expiry") == 412
    assert store.deleted == []
    assert raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 360) == {
        "processed": 1,
        "failures": 0,
    }
    with fixture.sessions() as db:
        status = raw.raw_status(db, db.get(Account, ACCOUNT), "FICTIONAL-STUDY")
        assert status["revocations"][0]["state"] == "completed"
        assert status["artifacts"][0]["upload_state"] == "purged"
    # A late already-started PUT is reconciled using the retained exact key.
    store.objects[key] = ["late-in-flight-put"]
    assert (
        raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 1260)["processed"]
        == 1
    )
    assert not store.objects[key]


def test_exact_versions_delete_markers_and_neighbor_keys(fixture):
    store = VersionedStore()
    store.objects = {
        "raw/id": ["old", "new", "marker-deleted"],
        "raw/id-neighbor": ["untouched"],
    }
    raw.purge_exact_key(store, "fictional", "raw/id")
    assert store.objects["raw/id"] == [] and store.objects["raw/id-neighbor"] == [
        "untouched"
    ]
    assert {x["VersionId"] for x in store.deleted} == {"old", "new", "marker-deleted"}
    store.objects["raw/id"] = ["null"]
    with pytest.raises(RuntimeError, match="versioned"):
        raw.purge_exact_key(store, "fictional", "raw/id")


@pytest.mark.parametrize(
    "change",
    [
        "withdrawal",
        "account_generation",
        "policy_revocation",
        "configuration_revocation",
        "expiry",
    ],
)
def test_cleanup_purges_verified_data_after_authority_loss(fixture, change):
    store = VersionedStore()
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        artifact, ledger = attach(db, a, check, request)
        artifact.state = "verified"
        artifact.version_id = "original"
        store.objects[artifact.key] = ["original", "overwritten-version"]
        if change == "withdrawal":
            consent = db.get(Record, rec_id(a, "consent", check.study_id))
            consent.body = {**consent.body, "state": "withdrawn"}
        elif change == "account_generation":
            a.generation = 2
        elif change == "policy_revocation":
            db.get(Registry, "retention:" + POLICY["policy_id"]).active = False
        elif change == "configuration_revocation":
            db.get(
                Registry, "configuration:" + ledger.authority["configuration_id"]
            ).active = False
        else:
            ledger.retained_until = (
                TICK + 359
            )  # SQLite fixture; PG rejects runtime deadline edits.
    outcome = raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 360)
    assert outcome == {"processed": 1, "failures": 0}
    with fixture.sessions() as db:
        assert db.get(raw.RawRetention, ARTIFACT).state == "purged"


def test_failed_delete_and_crash_after_delete_are_retryable(fixture):
    store = VersionedStore()
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        artifact, _ = attach(db, a, check, request)
        store.objects[artifact.key] = ["original"]
        raw.revoke_raw(
            db,
            a,
            check.study_id,
            raw.RawRevocation(confirmation=True, artifact_kinds=["eye_video"]),
        )
    store.fail = True
    assert (
        raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 360)["failures"] == 1
    )
    with fixture.sessions() as db:
        assert db.get(raw.RawRetention, ARTIFACT).state == "cleanup_pending"
    store.fail = False
    # Model crash after successful external deletion before its SQL settlement.
    raw.purge_exact_key(
        store, "fictional-raw-bucket", "quarantine/fictional/" + ARTIFACT
    )
    assert (
        raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 1260)["failures"] == 0
    )
    with fixture.sessions() as db:
        assert db.get(raw.RawRetention, ARTIFACT).state == "purged"


def test_purge_compacts_payload_metadata_and_generation_erasure_removes_fingerprint(
    fixture,
):
    store = VersionedStore()
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        artifact, ledger = attach(db, a, check, request)
        original_fingerprint = ledger.authority["payload_ref_hmac"]
        raw.revoke_raw(
            db,
            a,
            check.study_id,
            raw.RawRevocation(confirmation=True, artifact_kinds=["eye_video"]),
        )
    raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 360)
    with fixture.sessions.begin() as db:
        row = db.get(raw.RawRetention, ARTIFACT)
        assert row.authority == {
            "compaction": "payload_purged",
            "upload_expires_at": TICK + 300,
            "payload_ref_hmac": original_fingerprint,
        }
        assert row.kind == "eye_video" and row.study_id == "FICTIONAL-STUDY"
        db.get(Account, ACCOUNT).generation = 2
    raw.cleanup_raw_once(fixture.sessions, store, tick=TICK + 1260)
    with fixture.sessions() as db:
        row = db.get(raw.RawRetention, ARTIFACT)
        assert row.authority == {
            "compaction": "generation_retired",
            "upload_expires_at": TICK + 300,
        }
        assert (
            row.kind == "raw_cleanup_reference" and row.study_id == "retired-generation"
        )
        assert row.key.endswith(ARTIFACT) and row.account_id == ACCOUNT


def test_preference_off_also_retires_admitted_tickets(fixture):
    with fixture.sessions.begin() as db:
        a, check, request = consent_and_attempt(db)
        artifact, _ = attach(db, a, check, request)
        status = raw.set_preferences(
            db, a, check.study_id, preference(choices=raw.off())
        )
        assert (
            status["choices"] == raw.off()
            and status["revocations"][0]["state"] == "cleanup_pending"
        )
        with pytest.raises(Problem):
            raw.assert_artifact_admitted(db, a, artifact)


def test_start_permission_is_fresh_separate_from_upload_and_revoked_immediately(
    fixture,
):
    with fixture.sessions.begin() as db:
        a, check = db.get(Account, ACCOUNT), db.get(Check, CHECK)
        config = raw.active_body(db, "configuration", "FICTIONAL-EYE-CONFIG")
        with pytest.raises(Problem, match="OPTIONAL_RAW_CONSENT_REQUIRED"):
            raw.raw_start_permission(db, a, check, config, "eye_video")
        choices = raw.off()
        choices["eye_video"]["record"] = True
        status = raw.set_preferences(db, a, check.study_id, preference(choices=choices))
        permission = raw.raw_start_permission(db, a, check, config, "eye_video")
        assert permission["record"] is True and permission["upload"] is False
        assert permission["receipt_id"] == status["receipt_id"]
        with pytest.raises(Problem, match="RAW_KIND_UNAVAILABLE"):
            raw.raw_start_permission(db, a, check, config, "ecg_waveform")
        raw.revoke_raw(
            db,
            a,
            check.study_id,
            raw.RawRevocation(confirmation=True, artifact_kinds=["eye_video"]),
        )
        with pytest.raises(Problem, match="OPTIONAL_RAW_CONSENT_REQUIRED"):
            raw.raw_start_permission(db, a, check, config, "eye_video")


def test_preserving_migration_does_not_manufacture_historical_consent(fixture):
    with fixture.sessions.begin() as db:
        db.add(
            Artifact(
                id=ARTIFACT,
                account_id=ACCOUNT,
                generation=1,
                session_id=CHECK,
                bucket="fictional",
                key="legacy/" + ARTIFACT,
                sha256="f" * 64,
                size=42,
                media_type="video/mp4",
                kind="eye_video",
                state="verified",
                expires=TICK - 10,
                scope={"study_id": "FICTIONAL-STUDY"},
            )
        )
    with fixture.engine.begin() as connection:
        raw.migration_004_raw_retention(connection)
        raw.migration_004_raw_retention(connection)
    with fixture.sessions() as db:
        assert db.get(Artifact, ARTIFACT).state == "verified"
        row = db.get(raw.RawRetention, ARTIFACT)
        assert (
            row.authority["legacy_unqualified"] is True
            and row.state == "cleanup_pending"
        )
        assert row.retained_until == TICK - 10


def test_administrative_reports_require_their_own_approved_purpose(fixture):
    with fixture.sessions.begin() as db:
        a, check = db.get(Account, ACCOUNT), db.get(Check, CHECK)
        policy = {
            **POLICY,
            "version": "v2",
            "raw_kinds": ["source_lab_report"],
            "purpose_id": "administrative_report_revision",
        }
        release(db, "retention", policy["policy_id"], policy)
        for purpose, role in [
            ("other", "lab_report_revision"),
            (policy["purpose_id"], "participant"),
        ]:
            with pytest.raises(Problem):
                raw.administrative_authority(
                    db,
                    a,
                    check,
                    policy["policy_id"],
                    purpose,
                    iso(check.created),
                    operator_role=role,
                )
        authority = raw.administrative_authority(
            db,
            a,
            check,
            policy["policy_id"],
            policy["purpose_id"],
            iso(check.created),
            operator_role="lab_report_revision",
        )
        assert authority["retained_until"] == check.created + 2 * 86400


@pytest.mark.postgres
def test_actual_postgres_immutable_lifetime_and_one_way_compaction(client, account):
    if database.engine().dialect.name != "postgresql":
        pytest.fail(
            "This marked live check requires the actual disposable PostgreSQL gate"
        )
    artifact_id = database.uid()
    tick = database.now()
    upload_expires = tick - 400
    fingerprint = raw.payload_reference(account, 1, "eye_video", "d" * 64)
    original = {
        "upload_expires_at": upload_expires,
        "artifact_sha256": "d" * 64,
        "payload_ref_hmac": fingerprint,
        "consent_record_id": CONSENT,
        "attempt_id": ATTEMPT,
    }
    with database.factory().begin() as db:
        artifact = Artifact(
            id=artifact_id,
            account_id=account,
            generation=1,
            session_id=CHECK,
            bucket="fictional-pg-trigger",
            key="fictional/" + artifact_id,
            sha256="d" * 64,
            size=128,
            media_type="video/mp4",
            kind="eye_video",
            state="verified",
            expires=upload_expires,
            scope={"study_id": "FICTIONAL-PG-TRIGGER"},
        )
        db.add(artifact)
        db.flush()
        db.add(
            raw.RawRetention(
                artifact_id=artifact_id,
                account_id=account,
                generation=1,
                study_id="FICTIONAL-PG-TRIGGER",
                kind="eye_video",
                bucket=artifact.bucket,
                key=artifact.key,
                authority=original,
                retained_until=tick + 86400,
                state="retained",
                cleanup_next_at=0,
            )
        )
    with database.engine().begin() as connection:
        raw.migration_004_raw_retention(connection)
    with pytest.raises(IntegrityError, match="immutable"):
        with database.factory().begin() as db:
            db.get(raw.RawRetention, artifact_id).retained_until = tick + 86401
    with database.factory().begin() as db:
        row = db.get(raw.RawRetention, artifact_id)
        row.state = "purged"
        row.authority = {
            "compaction": "payload_purged",
            "upload_expires_at": upload_expires,
            "payload_ref_hmac": fingerprint,
        }
    with pytest.raises(IntegrityError, match="compaction"):
        with database.factory().begin() as db:
            db.get(raw.RawRetention, artifact_id).authority = original
    with database.factory().begin() as db:
        db.get(Account, account).generation = 2
        row = db.get(raw.RawRetention, artifact_id)
        row.authority = {
            "compaction": "generation_retired",
            "upload_expires_at": upload_expires,
        }
        row.study_id = "retired-generation"
        row.kind = "raw_cleanup_reference"
    with pytest.raises(IntegrityError, match="immutable"):
        with database.factory().begin() as db:
            db.delete(db.get(raw.RawRetention, artifact_id))


def test_renewal_appends_write_deadline_without_extending_retention(
    fixture, monkeypatch
):
    with fixture.sessions.begin() as db:
        a, request, config = consent_and_attempt(db)
        artifact, row = attach(db, a, request, config)
        original = row.retained_until
        origin = row.authority["upload_expires_at"]
        monkeypatch.setattr(raw, "now", lambda: TICK + 400)
        raw.renew_ticket_authority(db, a, artifact)
        assert artifact.expires == TICK + 700
        assert row.authority["upload_expires_at"] == origin
        assert row.retained_until == original
        assert raw.admitted_write_deadline(db, row) == TICK + 700
        assert raw.assert_artifact_admitted(db, a, artifact) == row
        row.state = "cleanup_pending"
        with pytest.raises(Problem, match="RAW_RETENTION_WINDOW_CLOSED"):
            raw.renew_ticket_authority(db, a, artifact)


def test_renewal_denies_changed_choice_settled_state_and_short_horizon(fixture):
    with fixture.sessions.begin() as db:
        a, request, config = consent_and_attempt(db)
        artifact, row = attach(db, a, request, config)
        artifact.state = "verified"
        artifact.version_id = "fictional-existing-version"
        seed_verified_native_receipt(db, a, artifact)
        with pytest.raises(Problem, match="RAW_ARTIFACT_ALREADY_SETTLED"):
            raw.renew_ticket_authority(db, a, artifact)
        artifact.state = "quarantine"
        row.retained_until = TICK + 360
        with pytest.raises(Problem, match="RAW_RETENTION_WINDOW_CLOSED"):
            raw.renew_ticket_authority(db, a, artifact)
        row.retained_until = TICK + 1000
        raw.revoke_raw(
            db,
            a,
            "FICTIONAL-STUDY",
            raw.RawRevocation(confirmation=True, artifact_kinds=["eye_video"]),
        )
        with pytest.raises(Problem, match="RAW_RETENTION_WINDOW_CLOSED"):
            raw.renew_ticket_authority(db, a, artifact)


def test_released_policy_does_not_enable_an_unimplemented_raw_codec(fixture):
    with fixture.sessions.begin() as db:
        account, check, request = consent_and_attempt(db)
        previous = raw.active_body(db, "configuration", "FICTIONAL-EYE-CONFIG")
        # A legitimate later configuration can preserve the retention approval
        # while selecting a research adapter with no implemented raw codec.
        material = {
            k: previous["material"][k]
            for k in (
                "schema_version",
                "channel",
                "duration_ms",
                "camera_id",
                "stimulus_policy_id",
                "illumination_policy_id",
                "geometry_id",
                "frame_rate_hz",
                "extractor_version",
            )
        }
        changed = {
            **previous,
            "version": "v2",
            "software_adapter_id": "unimplemented-eyes",
            "material": material,
            "sha256": digest(material),
        }
        qualified = {**proof("eyes", config_body=changed), "version": "v2"}
        release(db, "qualification", qualified["registry_id"], qualified)
        release(db, "configuration", changed["registry_id"], changed)
        config = raw.active_body(db, "configuration", changed["registry_id"])
        status = raw.raw_status(db, account, check.study_id)
        assert status["policy"] is not None
        assert status["availability"]["eye_video"] == {
            "record_allowed": False,
            "upload_allowed": False,
            "reasons": ["RAW_CODEC_UNIMPLEMENTED"],
        }
        assert status["availability"]["ecg_waveform"]["record_allowed"] is True
        for action in (
            lambda: raw.raw_start_permission(db, account, check, config, "eye_video"),
            lambda: raw.admit_artifact(db, account, check, request, config),
        ):
            with pytest.raises(Problem) as error:
                action()
            assert error.value.code == "RAW_CODEC_UNIMPLEMENTED"
        with pytest.raises(Problem) as error:
            raw.set_preferences(db, account, check.study_id, preference())
        assert error.value.code == "RAW_KIND_UNAVAILABLE"


def test_verified_raw_requires_exact_owned_codec_receipt_and_accepted_native_evidence(
    fixture,
):
    with fixture.sessions.begin() as db:
        account, check, request = consent_and_attempt(db)
        artifact, lifetime = attach(db, account, check, request)
        artifact.state = "verified"
        artifact.version_id = "fictional-actual-version"
        with pytest.raises(Problem) as error:
            raw.assert_artifact_admitted(db, account, artifact)
        assert error.value.code == "AUTHENTICATED_RAW_VERIFICATION_REQUIRED"
        receipt = seed_verified_native_receipt(db, account, artifact)
        assert raw.assert_artifact_admitted(db, account, artifact) is lifetime
        for field, changed in (
            ("version_id", "other-version"),
            ("sha256", "f" * 64),
            ("attempt_id", "40000000-0000-4000-8000-000000000099"),
            ("configuration_submitted_sha256", "f" * 64),
            ("evidence_sha256", "f" * 64),
            ("codec", "otgd_ecg_samples_v1"),
        ):
            original = receipt.body
            receipt.body = {**original, field: changed}
            receipt.sha256 = digest(receipt.body)
            with pytest.raises(Problem) as error:
                raw.assert_artifact_admitted(db, account, artifact)
            assert error.value.code == "AUTHENTICATED_RAW_VERIFICATION_REQUIRED"
            receipt.body = original
            receipt.sha256 = digest(original)
