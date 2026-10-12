"""Disposable SQL/S3 doubles for continuity; no shared emulator restart."""

from copy import deepcopy
from io import BytesIO
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select

from otgd.canonical import canonical
from otgd.db import Account, Base, SystemState
from otgd.journal_continuity import (
    CONTROL_KEY,
    STATE_KEY,
    JournalContinuityBlocked,
    bind_migration,
    preflight_bootstrap,
    read_establishment,
    verify_binding,
)

CONFIG = SimpleNamespace(
    environment="local", aws_region="us-east-2", journal_bucket="fictional-journal"
)
BODY = {
    "schema_version": "1.0.0",
    "environment": "local",
    "established_at": "2026-10-11T00:00:00Z",
    "minimum_retention_days": 90,
    "maximum_recovery_age_days": 35,
}


class Journal:
    def __init__(self, body=None, version="original-version"):
        self.raw = canonical(BODY if body is None else body)
        self.version = version
        self.reads = []
        self.closed = False

    def head_object(self, **args):
        raise AssertionError("Admission must read the current bytes/version atomically")

    def get_object(self, **args):
        assert args == {"Bucket": CONFIG.journal_bucket, "Key": CONTROL_KEY}
        if self.version in ("missing", "delete-marker"):
            raise RuntimeError("Current retained marker is missing")
        self.reads.append(args)
        stream = BytesIO(self.raw)
        self.stream = stream
        return {
            "VersionId": self.version,
            "ContentLength": len(self.raw),
            "Body": stream,
        }


@pytest.fixture
def connection():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with eng.begin() as conn:
        yield conn
    eng.dispose()


def test_empty_database_binds_once_then_requires_exact_version(connection):
    journal = Journal()
    assert preflight_bootstrap(connection, CONFIG, journal) is None
    receipt = bind_migration(connection, CONFIG, journal)
    assert receipt["body"] == BODY
    assert verify_binding(connection, CONFIG, journal) == receipt
    assert journal.stream.closed
    assert bind_migration(connection, CONFIG, journal) == receipt
    journal.version = "same-bytes-new-version"
    with pytest.raises(JournalContinuityBlocked, match="cannot be replaced"):
        bind_migration(connection, CONFIG, journal)
    with pytest.raises(JournalContinuityBlocked, match="do not match"):
        verify_binding(connection, CONFIG, journal)


def test_each_admission_reads_current_marker_and_refuses_removed_versions(connection):
    journal = Journal()
    bind_migration(connection, CONFIG, journal)
    for _ in range(2):
        verify_binding(connection, CONFIG, journal)
    assert len(journal.reads) == 3
    for version in ("delete-marker", "missing"):
        journal.version = version
        with pytest.raises(JournalContinuityBlocked, match="unavailable"):
            verify_binding(connection, CONFIG, journal)


def test_returned_unversioned_marker_closes_body():
    journal = Journal(version="null")
    with pytest.raises(JournalContinuityBlocked, match="version"):
        read_establishment(CONFIG, journal)
    assert journal.stream.closed


def test_http_write_rechecks_replaced_marker_after_rate_commit(client, account, monkeypatch):
    import hashlib
    from uuid import uuid4
    from otgd.config import settings
    from otgd.db import Check, RateBucket, factory
    from .conftest import headers

    cfg = settings().model_copy(update={
        "environment": "test", "independent_recovery_admission": True,
        "journal_bucket": CONFIG.journal_bucket, "aws_region": CONFIG.aws_region,
    })
    journal = Journal({**BODY, "environment": "test"})
    with factory().begin() as db:
        bind_migration(db, cfg, journal, expected_version=journal.version,
                       expected_sha256=hashlib.sha256(journal.raw).hexdigest())
    monkeypatch.setattr("otgd.config.settings", lambda: cfg)
    monkeypatch.setattr("otgd.storage.client", lambda _: journal)
    monkeypatch.setattr("otgd.recovery_authority.load_authority", lambda *_: {
        "activation": None, "plan": {"accepted": {}, "barriers": {}},
    })
    original = journal.get_object

    def replaced_at_second_admission(**kwargs):
        if len(journal.reads) == 2:
            journal.version = "same-bytes-replaced-after-rate-commit"
        return original(**kwargs)

    monkeypatch.setattr(journal, "get_object", replaced_at_second_admission)
    sid = str(uuid4())
    response = client.post("/v1/sessions", headers={
        **headers(), "X-Data-Generation": "1", "Idempotency-Key": str(uuid4()),
    }, json={"session_id": sid, "mode": "synthetic", "protocol_id": None})
    assert response.status_code == 503
    assert response.json()["code"] == "INDEPENDENT_RECOVERY_NOT_VERIFIED"
    assert len(journal.reads) == 3
    with factory()() as db:
        assert db.get(Check, sid) is None
        assert db.get(RateBucket, account + ":write") is not None


def test_retained_database_never_automatically_adopts_journal(connection, monkeypatch):
    connection.execute(
        Account.__table__.insert().values(
            id="account", subject_hash="a" * 64, generation=1, state="active"
        )
    )
    journal = Journal()
    with pytest.raises(JournalContinuityBlocked, match="administrator"):
        preflight_bootstrap(connection, CONFIG, journal)
    with pytest.raises(JournalContinuityBlocked, match="automatically"):
        bind_migration(connection, CONFIG, journal)
    receipt = read_establishment(CONFIG, journal)["binding"]
    monkeypatch.setenv("OTGD_JOURNAL_ESTABLISHMENT_VERSION_ID", receipt["version_id"])
    monkeypatch.setenv("OTGD_JOURNAL_ESTABLISHMENT_SHA256", receipt["sha256"])
    preflight_bootstrap(connection, CONFIG, journal)
    assert (
        connection.scalar(select(SystemState.body).where(SystemState.key == STATE_KEY))
        is None
    )
    bind_migration(connection, CONFIG, journal)
    journal.version = "missing"
    with pytest.raises(JournalContinuityBlocked, match="unavailable"):
        preflight_bootstrap(connection, CONFIG, journal)


@pytest.mark.parametrize(
    "changes",
    [
        {"environment": "prod"},
        {"schema_version": "2.0.0"},
        {"minimum_retention_days": True},
        {"minimum_retention_days": 89},
        {"maximum_recovery_age_days": 36},
        {"established_at": "2026-10-11T00:00:00"},
        {"established_at": "invalid"},
    ],
)
def test_malformed_control_is_closed(changes):
    with pytest.raises(JournalContinuityBlocked):
        read_establishment(CONFIG, Journal({**deepcopy(BODY), **changes}))


@pytest.mark.parametrize("version", [None, "", "null", "x" * 1025])
def test_unversioned_marker_rejected(version):
    with pytest.raises(JournalContinuityBlocked):
        read_establishment(CONFIG, Journal(version=version))


def test_bounded_noncanonical_and_corrupt_controls_are_closed():
    journal = Journal()
    journal.raw += b" "
    with pytest.raises(JournalContinuityBlocked):
        read_establishment(CONFIG, journal)
    journal.raw = b"x" * 8193
    with pytest.raises(JournalContinuityBlocked):
        read_establishment(CONFIG, journal)
    assert journal.stream.closed


def test_unbound_runtime_and_wrong_independent_receipt_are_closed(connection):
    with pytest.raises(JournalContinuityBlocked, match="no independently"):
        verify_binding(connection, CONFIG, Journal())
    for args in (
        {"expected_version": "original-version"},
        {"expected_version": "wrong", "expected_sha256": "a" * 64},
        {"expected_sha256": "bad"},
    ):
        with pytest.raises(JournalContinuityBlocked):
            bind_migration(connection, CONFIG, Journal(), **args)


def test_pre_schema_database_does_not_manufacture_a_binding():
    eng = create_engine("sqlite://")
    with eng.connect() as connection:
        assert preflight_bootstrap(connection, CONFIG, Journal()) is None
    eng.dispose()
