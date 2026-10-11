"""Admission must reject stale restored databases despite their active flags.

The transport fixture models pinned S3 versions and actual retention responses;
these tests establish refusal/admission logic, not live AWS Object Lock behavior.
"""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from otgd import recovery_authority as r
from otgd.canonical import canonical, digest
from otgd.config import settings
from otgd.db import Account, Base, Job, SystemState, iso, now
from otgd.errors import Problem
from otgd.identity_keys import key_descriptor

ACCOUNT = "10000000-0000-4000-8000-000000000001"
JOB = "20000000-0000-4000-8000-000000000001"
RECOVERY = "30000000-0000-4000-8000-000000000001"
SUBJECT = "c" * 64


class Journal:
    def __init__(self, cfg, instant):
        self.cfg, self.instant, self.objects = cfg, instant, {}
        self.markers, self.replaced = [], False
        self.versioning, self.mode = "Enabled", "COMPLIANCE"
        self.lock_mode, self.lock_days, self.encryption = "COMPLIANCE", 90, "aws:kms"
        self.until = datetime.fromtimestamp(instant, timezone.utc) + timedelta(days=91)

    def add(self, key, value):
        raw = canonical(value)
        self.objects[key] = {
            "key": key,
            "version_id": "version-" + str(len(self.objects) + 1),
            "raw": raw,
        }
        return {k: self.objects[key][k] for k in ("key", "version_id")} | {
            "sha256": digest(value)
        }

    def get_bucket_versioning(self, **_):
        return {"Status": self.versioning}

    def get_object_lock_configuration(self, **_):
        return {
            "ObjectLockConfiguration": {
                "ObjectLockEnabled": "Enabled",
                "Rule": {
                    "DefaultRetention": {"Mode": self.lock_mode, "Days": self.lock_days}
                },
            }
        }

    def get_paginator(self, name):
        assert name == "list_object_versions"
        return self

    def paginate(self, Bucket, Prefix):
        assert Bucket == self.cfg.journal_bucket
        values = [
            {"Key": key, "VersionId": v["version_id"], "IsLatest": True}
            for key, v in self.objects.items()
            if key.startswith(Prefix)
        ]
        if self.replaced and values:
            values.append({**values[0], "VersionId": "old-version", "IsLatest": False})
        return [
            {
                "Versions": values,
                "DeleteMarkers": [
                    v for v in self.markers if v["Key"].startswith(Prefix)
                ],
            }
        ]

    def head_object(self, Bucket, Key, VersionId):
        assert (
            Bucket == self.cfg.journal_bucket
            and VersionId == self.objects[Key]["version_id"]
        )
        return {
            "VersionId": VersionId,
            "ServerSideEncryption": self.encryption,
            "SSEKMSKeyId": self.cfg.journal_kms_key_id,
            "LastModified": datetime.fromtimestamp(self.instant - 3600, timezone.utc),
        }

    def get_object_retention(self, **_):
        return {"Retention": {"Mode": self.mode, "RetainUntilDate": self.until}}

    def get_object(self, Bucket, Key, VersionId):
        import io

        data = self.read(Bucket, Key, VersionId, r.MANIFEST_LIMIT)
        return {
            "Body": io.BytesIO(data),
            "ContentLength": len(data),
            "VersionId": VersionId,
        }

    def read(self, bucket, key, version, limit):
        assert (
            bucket == self.cfg.journal_bucket
            and version == self.objects[key]["version_id"]
        )
        raw = self.objects[key]["raw"]
        if len(raw) > limit:
            raise RuntimeError("limit")
        return raw


@pytest.fixture
def journal(monkeypatch):
    instant = now()
    cfg = settings().model_copy(
        update={
            "environment": "qa",
            "deployment_account": "123456789012",
            "source_revision": "d" * 40,
            "journal_kms_key_id": "arn:aws:kms:us-east-2:123456789012:key/journal",
        }
    )
    s3 = Journal(cfg, instant)
    control = s3.add(
        "control/established.json",
        {
            "schema_version": "1.0.0",
            "environment": "qa",
            "established_at": iso(instant - 3600),
            "minimum_retention_days": 90,
            "maximum_recovery_age_days": 35,
        },
    )
    accepted = {
        "schema_version": "1.0.0",
        "event_type": "deletion_accepted",
        "event_id": JOB,
        "job_id": JOB,
        "account_ref": ACCOUNT,
        "retired_generation": 1,
        "new_generation": 2,
        "scope": "account",
        "policy_version": "privacy-v1",
        "accepted_at": iso(instant - 120),
        "subject_ref_hmac": SUBJECT,
        "hmac_key_id": key_descriptor(cfg)["key_id"],
    }
    receipt = s3.add(f"events/{JOB}/accepted.json", accepted)
    completion = {
        "schema_version": "1.0.0",
        "event_type": "deletion_completed",
        "job_id": JOB,
        "account_ref": ACCOUNT,
        "retired_generation": 1,
        "scope": "account",
        "completed_at": iso(instant - 60),
    }
    s3.add(f"events/{JOB}/completed.json", completion)
    monkeypatch.setattr(r, "authority_client", lambda: s3)
    monkeypatch.setattr(r, "versioned_read", s3.read)
    return SimpleNamespace(
        cfg=cfg,
        instant=instant,
        s3=s3,
        control=control,
        accepted=accepted,
        receipt=receipt,
    )


def activation(journal):
    j = journal
    events = [
        {k: v[k] for k in ("key", "version_id")}
        | {"sha256": r.hashlib.sha256(v["raw"]).hexdigest()}
        for key, v in sorted(j.s3.objects.items())
        if key.startswith("events/")
    ]
    manifest = {
        "schema_version": "1.0.0",
        "event_type": "DeletionWatermark",
        "watermark_id": RECOVERY,
        "environment": "qa",
        "backup_created_at": iso(j.instant - 1800),
        "inventory_at": iso(j.instant),
        "event_count": len(events),
        "events": events,
        "inventory_sha256": digest(events),
    }
    watermark = j.s3.add(f"watermarks/{RECOVERY}.json", manifest)
    body = {
        "schema_version": "1.0.0",
        "event_type": "RecoveryActivation",
        "recovery_id": RECOVERY,
        "environment": "qa",
        "account": j.cfg.deployment_account,
        "region": j.cfg.aws_region,
        "source_revision": j.cfg.source_revision,
        "backup_created_at": manifest["backup_created_at"],
        "control": j.control,
        "watermark": watermark,
        "inventory_sha256": manifest["inventory_sha256"],
        "activated_at": iso(j.instant),
        "authentication_cutoff": int(j.instant),
        "scopes_suspended": True,
    }
    receipt = j.s3.add(f"recovery/{RECOVERY}.json", body)
    return body, receipt


def database(j, restored=False, recovery=None):
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    db = Session(eng)
    db.add(
        Account(
            id=ACCOUNT,
            subject_hash=SUBJECT,
            generation=1 if restored else 2,
            state="active" if restored else "deleted",
        )
    )
    if not restored:
        db.add(
            Job(
                id=JOB,
                account_id=ACCOUNT,
                generation=1,
                kind="deletion",
                state="completed",
                body={"scope": "account", "journal_receipt": j.receipt},
                journal_accepted=True,
            )
        )
    if recovery:
        body, receipt = recovery
        db.add(
            SystemState(
                key="recovery",
                body={
                    "verified": True,
                    "recovery_id": body["recovery_id"],
                    "journal_activation": receipt,
                    "authentication_cutoff": body["authentication_cutoff"],
                    "inventory_sha256": body["inventory_sha256"],
                    "scopes_suspended": True,
                },
            )
        )
    db.commit()
    return db


def test_retained_deletion_blocks_restored_active_database_even_without_restore_flag(
    journal,
):
    authority = r.load_authority(journal.cfg, journal.instant)
    with database(journal, restored=True) as db:
        with pytest.raises(r.RecoveryBlocked, match="accepted deletion"):
            r.verify_database_authority(db, authority, False)
    with database(journal) as db:
        assert r.verify_database_authority(db, authority, False) == 0


def test_recovery_claim_requires_latest_independent_activation_and_suspension(journal):
    act = activation(journal)
    authority = r.load_authority(journal.cfg, journal.instant)
    with database(journal) as db:
        with pytest.raises(r.RecoveryBlocked, match="recovery activation"):
            r.verify_database_authority(db, authority, False)
    with database(journal, recovery=act) as db:
        assert (
            r.verify_database_authority(db, authority, True)
            == act[0]["authentication_cutoff"]
        )
        state = db.get(SystemState, "recovery")
        original = deepcopy(state.body)
        for field, bad in [
            ("scopes_suspended", False),
            ("verified", False),
            ("recovery_id", "old"),
            ("inventory_sha256", "0" * 64),
            ("authentication_cutoff", 0),
            ("journal_activation", {}),
        ]:
            state.body = {**original, field: bad}
            with pytest.raises(r.RecoveryBlocked):
                r.verify_database_authority(db, authority, False)


@pytest.mark.parametrize(
    "change",
    [
        "versioning",
        "lock_mode",
        "lock_days",
        "mode",
        "until",
        "encryption",
        "missing_control",
        "replacement",
        "marker",
    ],
)
def test_actual_retention_and_continuity_are_mandatory(journal, change):
    j = journal
    if change == "missing_control":
        del j.s3.objects["control/established.json"]
    elif change == "replacement":
        j.s3.replaced = True
    elif change == "marker":
        j.s3.markers = [{"Key": "events/" + JOB + "/accepted.json"}]
    else:
        bad = {
            "versioning": "Suspended",
            "lock_mode": "GOVERNANCE",
            "lock_days": 35,
            "mode": "GOVERNANCE",
            "until": datetime.fromtimestamp(j.instant - 1, timezone.utc),
            "encryption": "AES256",
        }[change]
        setattr(j.s3, change, bad)
    with pytest.raises(r.RecoveryBlocked):
        r.load_authority(j.cfg, j.instant)


@pytest.mark.parametrize(
    "field,bad",
    [
        ("account", "987654321012"),
        ("region", "eu-west-1"),
        ("source_revision", "tag"),
        ("scopes_suspended", False),
        ("authentication_cutoff", 2**50),
        ("control", {}),
        ("inventory_sha256", "0" * 64),
        ("watermark", {}),
    ],
)
def test_foreign_or_unbound_activation_is_rejected(journal, field, bad):
    body, _ = activation(journal)
    journal.s3.objects[f"recovery/{RECOVERY}.json"]["raw"] = canonical(
        {**body, field: bad}
    )
    with pytest.raises(r.RecoveryBlocked):
        r.load_authority(journal.cfg, journal.instant)


def test_deleted_generation_cannot_be_restored_or_changed_after_receipt(journal):
    authority = r.load_authority(journal.cfg, journal.instant)
    with database(journal) as db:
        account = db.get(Account, ACCOUNT)
        for values in [
            {"state": "active"},
            {"generation": 1},
            {"generation": 3},
            {"subject_hash": "b" * 64},
        ]:
            account.state, account.generation, account.subject_hash = (
                "deleted",
                2,
                SUBJECT,
            )
            for field, value in values.items():
                setattr(account, field, value)
            with pytest.raises(r.RecoveryBlocked, match="subject or generation"):
                r.verify_database_authority(db, authority)


def test_generation_holes_and_unknown_identity_keys_are_rejected(journal):
    j = journal
    value = {**j.accepted, "retired_generation": 2, "new_generation": 3}
    j.s3.objects[f"events/{JOB}/accepted.json"]["raw"] = canonical(value)
    with pytest.raises(r.RecoveryBlocked):
        r.load_authority(j.cfg, j.instant)
    j.s3.objects[f"events/{JOB}/accepted.json"]["raw"] = canonical(
        {**j.accepted, "hmac_key_id": "unknown"}
    )
    with pytest.raises(r.RecoveryBlocked, match="identity tombstone key"):
        r.load_authority(j.cfg, j.instant)


def test_cloud_dependency_failure_is_refusal_and_local_opt_in_is_explicit(
    journal, monkeypatch
):
    monkeypatch.setattr("otgd.config.settings", lambda: journal.cfg)
    monkeypatch.setattr(
        r,
        "load_authority",
        lambda *_: (_ for _ in ()).throw(ConnectionError("private dependency details")),
    )
    with database(journal, restored=True) as db:
        with pytest.raises(Problem) as error:
            r.require_authority(db)
        assert error.value.code == "INDEPENDENT_RECOVERY_NOT_VERIFIED"
        assert "private dependency" not in str(error.value)
    monkeypatch.setattr(
        "otgd.config.settings",
        lambda: journal.cfg.model_copy(
            update={"environment": "local", "independent_recovery_admission": False}
        ),
    )
    monkeypatch.setattr("otgd.journal_continuity.verify_binding", lambda *_: None)
    assert r.require_authority(None) == 0


def test_database_only_verified_recovery_is_not_authority(journal):
    with database(journal, recovery=activation(journal)) as db:
        empty = {"activation": None, "plan": {"accepted": {}, "barriers": {}}}
        with pytest.raises(r.RecoveryBlocked, match="no independent activation"):
            r.verify_database_authority(db, empty)


def test_real_aws_clients_ignore_ambient_endpoints_without_network(monkeypatch):
    import boto3
    from otgd import storage

    cfg = settings().model_copy(
        update={
            "environment": "qa",
            "aws_endpoint_url": None,
            "s3_public_endpoint_url": None,
        }
    )
    monkeypatch.setenv("AWS_ENDPOINT_URL", "https://fictional.invalid")
    monkeypatch.setenv("AWS_ENDPOINT_URL_S3", "https://fictional.invalid")
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_PROFILE", raising=False)
    session = boto3.Session(
        aws_access_key_id="fictional",
        aws_secret_access_key="fictional",
        region_name=cfg.aws_region,
    )
    supplied = []

    def create(service, **kwargs):
        supplied.append(kwargs["config"])
        return session.client(service, **kwargs)

    monkeypatch.setattr(boto3, "client", create)
    monkeypatch.setattr("otgd.config.settings", lambda: cfg)
    monkeypatch.setattr(storage, "settings", lambda: cfg)
    r.authority_client.cache_clear()
    storage.client.cache_clear()
    try:
        for sdk in (r.authority_client(), storage.client("s3")):
            assert sdk.meta.endpoint_url.endswith(".amazonaws.com")
        assert len(supplied) == 2 and all(
            config.ignore_configured_endpoint_urls is True for config in supplied
        )
    finally:
        r.authority_client.cache_clear()
        storage.client.cache_clear()


def test_running_http_readiness_and_new_account_refuse_lost_local_marker(
    client, monkeypatch
):
    from otgd.db import factory
    from .conftest import headers

    cfg = settings().model_copy(
        update={"environment": "local", "independent_recovery_admission": False}
    )
    monkeypatch.setattr("otgd.config.settings", lambda: cfg)

    def lost(*_):
        raise RuntimeError("Fictional missing retained control version")

    monkeypatch.setattr("otgd.journal_continuity.verify_binding", lost)
    assert client.get("/health/ready").status_code == 503
    response = client.get(
        "/v1/me/capabilities", headers=headers(sub="new-after-marker-loss")
    )
    assert (
        response.status_code == 503
        and response.json()["code"] == "INDEPENDENT_RECOVERY_NOT_VERIFIED"
    )
    with factory()() as db:
        assert db.query(Account).count() == 0


def test_worker_claim_and_commit_refuse_retained_activation_missing_in_database(
    client, journal, monkeypatch
):
    from otgd.db import factory, Check
    from otgd import worker

    activation(journal)
    monkeypatch.setattr("otgd.config.settings", lambda: journal.cfg)
    monkeypatch.setattr("otgd.journal_continuity.verify_binding", lambda *_: None)
    with factory().begin() as db:
        db.add(Account(id=ACCOUNT, subject_hash=SUBJECT, generation=1, state="active"))
        db.add(
            Check(
                id="40000000-0000-4000-8000-000000000001",
                account_id=ACCOUNT,
                generation=1,
                mode="controlled_research",
                state="processing",
            )
        )
        db.add(
            Job(
                id=JOB,
                account_id=ACCOUNT,
                generation=1,
                kind="result",
                state="pending",
                body={"session_id": "40000000-0000-4000-8000-000000000001"},
            )
        )
    with pytest.raises(Problem) as denied:
        worker.claim_job(JOB)
    assert denied.value.code == "INDEPENDENT_RECOVERY_NOT_VERIFIED"
    with factory().begin() as db:
        job = db.get(Job, JOB)
        assert job.state == "pending" and job.fence == 0
        job.state = "running"
        job.fence = 1
        job.lease_until = now() + 120
        job.started = now()
    claim = worker.Claim(
        JOB,
        ACCOUNT,
        1,
        "result",
        1,
        now(),
        {"session_id": "40000000-0000-4000-8000-000000000001"},
    )
    with pytest.raises(Problem):
        worker.execute_claim(claim)
    with pytest.raises(Problem):
        worker.commit_output(claim, {})
    with factory()() as db:
        assert db.get(Check, claim.body["session_id"]).result is None
