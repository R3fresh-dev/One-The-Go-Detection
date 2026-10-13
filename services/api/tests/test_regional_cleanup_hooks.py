"""Regional erasure hook integration with durable SQL references; no live AWS."""

from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from otgd import (
    config,
    main,
    raw_export,
    raw_retention,
    replica_cleanup,
    storage,
    worker,
)
from otgd.db import Account, Base, Job
from otgd.errors import Problem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

ACCOUNT = "123456789012"
OWNER = "10000000-0000-4000-8000-000000000001"
JOB = "20000000-0000-4000-8000-000000000001"
ARTIFACT_BUCKET = f"otgd-serverless-development-{ACCOUNT}-us-east-1-artifacts"
EXPORT_BUCKET = f"otgd-serverless-development-{ACCOUNT}-us-east-1-exports"
WEST_ARTIFACT_BUCKET = f"otgd-fargate-recovery-{ACCOUNT}-us-west-2-artifacts"
WEST_EXPORT_BUCKET = f"otgd-fargate-recovery-{ACCOUNT}-us-west-2-exports"
WEST_KEY = f"arn:aws:kms:us-west-2:{ACCOUNT}:key/12345678-1234-1234-1234-123456789012"
TICK = 1_000_000.0
EXPORT_PREFIX = f"exports/{OWNER}/1/{JOB}/"


def entry(key, version="payload", marker=False):
    return {"Key": key, "VersionId": version, "DeleteMarker": marker}


class RegionalStore:
    """Versioned metadata only, recording writes across both regional clients."""

    def __init__(self, bucket, region, trace, rows=()):
        self.bucket, self.region, self.trace = bucket, region, trace
        self.rows = {}
        self.heads = {}
        self.deletes = []
        self.inventory_error = None
        self.partial_delete = False
        for row in rows:
            self.add(row)

    def add(self, row):
        identity = row["Key"], row["VersionId"]
        self.rows[identity] = deepcopy(row)
        if not row["DeleteMarker"]:
            value = {"VersionId": row["VersionId"], "ContentLength": 7,
                     "ReplicationStatus": "REPLICA" if self.region == "west" else "COMPLETED"}
            if self.region == "west":
                value.update(ServerSideEncryption="aws:kms", SSEKMSKeyId=WEST_KEY)
            self.heads[identity] = value

    def _record(self, operation, request):
        assert request["Bucket"] == self.bucket
        if self.region == "west" or operation == "head":
            assert request["ExpectedBucketOwner"] == ACCOUNT
        self.trace.append((self.region, operation, deepcopy(request)))

    def get_paginator(self, operation):
        assert operation == "list_object_versions"
        return self

    def paginate(self, **request):
        self._record("inventory", request)
        if self.inventory_error:
            raise self.inventory_error
        page = {"Versions": [], "DeleteMarkers": [], "IsTruncated": False}
        for row in self.rows.values():
            if row["Key"].startswith(request["Prefix"]):
                page["DeleteMarkers" if row["DeleteMarker"] else "Versions"].append(
                    {field: row[field] for field in ("Key", "VersionId")})
        return [page]

    def head_object(self, **request):
        self._record("head", request)
        assert "ChecksumMode" not in request
        value = self.heads.get((request["Key"], request["VersionId"]))
        if value is None:
            raise ClientError({"Error": {"Code": "NoSuchVersion"},
                               "ResponseMetadata": {"HTTPStatusCode": 404}}, "HeadObject")
        return deepcopy(value)

    def get_object(self, **request):
        raise AssertionError("Regional cleanup must never read object payloads")

    def _remove(self, objects):
        for value in objects:
            identity = value["Key"], value["VersionId"]
            self.rows.pop(identity, None)
            self.heads.pop(identity, None)

    def delete_objects(self, **request):
        self._record("delete", request)
        self.deletes.append(deepcopy(request))
        objects = request["Delete"]["Objects"]
        self._remove(objects[:1] if self.partial_delete else objects)
        return {"Errors": [{"Code": "AccessDenied"}]} if self.partial_delete else {}

    def delete_object(self, **request):
        self._record("delete", request)
        self.deletes.append(deepcopy(request))
        self._remove([request])
        return {}


@pytest.fixture
def regional_clients(monkeypatch):
    cfg = SimpleNamespace(
        aws_region="us-east-1", deployment_account=ACCOUNT,
        artifact_bucket=ARTIFACT_BUCKET, export_bucket=EXPORT_BUCKET,
        journal_bucket=ARTIFACT_BUCKET.replace("artifacts", "journal"),
        backup_region="us-west-2", backup_artifact_bucket=WEST_ARTIFACT_BUCKET,
        backup_export_bucket=WEST_EXPORT_BUCKET, backup_kms_key_id=WEST_KEY,
    )
    for module in (config, replica_cleanup, storage, worker):
        monkeypatch.setattr(module, "settings", lambda: cfg)

    def create(bucket, rows):
        trace = []
        west_bucket = WEST_ARTIFACT_BUCKET if bucket == ARTIFACT_BUCKET else WEST_EXPORT_BUCKET
        source = RegionalStore(bucket, "east", trace, rows)
        destination = RegionalStore(west_bucket, "west", trace, rows)
        monkeypatch.setattr(storage, "client", lambda service: source)

        def west_client(service, **request):
            assert service == "s3" and request["region_name"] == "us-west-2"
            assert "endpoint_url" not in request
            return destination

        monkeypatch.setattr(replica_cleanup.boto3, "client", west_client)
        return source, destination, trace

    return create


def hook(name, source, key):
    if name == "storage":
        return storage.delete_versions(source.bucket, key)
    if name == "raw-export":
        return raw_export.delete_versions_for_prefix(source, key)
    return raw_retention.purge_exact_key(source, source.bucket, key)


@pytest.mark.parametrize("name", ["storage", "raw-export", "raw-retention"])
@pytest.mark.parametrize("failure", ["PENDING", "FAILED", "west-outage", "partial-west-delete"])
def test_replica_preparation_failure_prevents_every_primary_permanent_delete(regional_clients, name, failure):
    bucket = EXPORT_BUCKET if name == "raw-export" else ARTIFACT_BUCKET
    key = "revoked/artifact" if name == "raw-retention" else "revoked/"
    object_key = key if name == "raw-retention" else key + "object"
    rows = [entry(object_key), entry(object_key, "marker", True)]
    source, destination, trace = regional_clients(bucket, rows)
    if failure in ("PENDING", "FAILED"):
        source.heads[(object_key, "payload")]["ReplicationStatus"] = failure
    elif failure == "west-outage":
        destination.inventory_error = EndpointConnectionError(endpoint_url="https://fictional-west-s3")
    else:
        destination.partial_delete = True

    with pytest.raises(Problem) as blocked:
        hook(name, source, key)

    assert blocked.value.status == 503 and blocked.value.retryable
    assert source.rows == {(row["Key"], row["VersionId"]): row for row in rows}
    assert not source.deletes
    assert any(region == "east" and operation == "head" for region, operation, _ in trace)
    if failure in ("PENDING", "FAILED"):
        assert not destination.deletes
    elif failure == "partial-west-delete":
        assert destination.deletes and len(destination.rows) == 1


@pytest.mark.parametrize("name", ["storage", "raw-export", "raw-retention"])
def test_hooks_complete_replica_erasure_and_empty_verification_before_primary_delete(regional_clients, name):
    bucket = EXPORT_BUCKET if name == "raw-export" else ARTIFACT_BUCKET
    key = "revoked/artifact" if name == "raw-retention" else "revoked/"
    object_key = key if name == "raw-retention" else key + "object"
    source, destination, trace = regional_clients(bucket, [entry(object_key), entry(object_key, "marker", True)])

    hook(name, source, key)

    assert not source.rows and not destination.rows
    first_primary_delete = next(i for i, (region, operation, _) in enumerate(trace)
                                if region == "east" and operation == "delete")
    assert trace[first_primary_delete - 1][:2] == ("west", "inventory")
    assert all(i < first_primary_delete for i, (region, operation, _) in enumerate(trace)
               if region == "west" and operation == "delete")


def test_raw_artifact_exact_scope_preserves_replica_and_primary_prefix_neighbors(regional_clients, monkeypatch):
    key = "quarantine/retired/raw-artifact"
    owned = [entry(key), entry(key, "marker", True)]
    neighbors = [entry(key + "-neighbor", "sibling"), entry(key + "/neighbor", "sibling-marker", True)]
    source, destination, _ = regional_clients(ARTIFACT_BUCKET, owned + neighbors)
    calls = []
    actual_prepare = replica_cleanup.prepare_delete

    def observed_prepare(*args, **options):
        calls.append((deepcopy(args[3]), dict(options)))
        return actual_prepare(*args, **options)

    monkeypatch.setattr(replica_cleanup, "prepare_delete", observed_prepare)
    raw_retention.purge_exact_key(source, ARTIFACT_BUCKET, key)

    assert calls == [(owned, {"exact_key": True})]
    expected = {(row["Key"], row["VersionId"]): row for row in neighbors}
    assert source.rows == destination.rows == expected
    assert {item["Key"] for request in destination.deletes for item in request["Delete"]["Objects"]} == {key}
    assert {request["Key"] for request in source.deletes} == {key}


@pytest.fixture
def cleanup_database(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(worker, "factory", lambda: sessions)
    with sessions.begin() as db:
        db.add(Account(id=OWNER, subject_hash="a" * 64, generation=1))
    yield sessions
    engine.dispose()


def expired_export(sessions, *, state="completed", output=None):
    with sessions.begin() as db:
        db.add(Job(id=JOB, account_id=OWNER, generation=1, kind="export", state=state,
                   body={"include_raw": False}, output=output, accepted=TICK - 100,
                   expires=TICK - 1, cleanup_next_at=0))


def test_worker_retains_failed_expired_export_for_regional_retry_without_primary_deletion(
    regional_clients, cleanup_database, monkeypatch,
):
    expired_export(cleanup_database, output={"bucket": EXPORT_BUCKET, "key": EXPORT_PREFIX + "archive.zip"})
    source, destination, _ = regional_clients(EXPORT_BUCKET, [entry(EXPORT_PREFIX + "archive.zip")])
    source.heads[(EXPORT_PREFIX + "archive.zip", "payload")]["ReplicationStatus"] = "PENDING"
    monkeypatch.setattr(worker, "now", lambda: TICK)
    monkeypatch.setattr(main, "now", lambda: TICK)

    @contextmanager
    def owner_access(request):
        # Authentication is a separate boundary; exercise the actual download
        # admission against this disposable owner's persisted expired export.
        with cleanup_database() as db:
            yield db, db.get(Account, OWNER), None, None

    monkeypatch.setattr(main, "access", owner_access)

    assert worker.cleanup_once() == {"attempted": 1, "failed": 1}
    assert not source.deletes and not destination.deletes
    with cleanup_database() as db:
        row = db.get(Job, JOB)
        public = main.job_view(row)
        assert public["state"] == "expired" and "download_path" not in public
        assert row.cleanup_next_at == TICK + 900 and row.cleanup_last_success is None
    with pytest.raises(Problem) as denied:
        main.privacy_download(Request({"type": "http", "headers": []}), JOB)
    assert denied.value.status == 410 and denied.value.code == "EXPORT_EXPIRED"
    assert source.rows  # Unreplicated bytes remain private while cleanup retries.
    assert worker.cleanup_once() == {"attempted": 0, "failed": 0}

    source.heads[(EXPORT_PREFIX + "archive.zip", "payload")]["ReplicationStatus"] = "COMPLETED"
    monkeypatch.setattr(worker, "now", lambda: TICK + 901)
    assert worker.cleanup_once() == {"attempted": 1, "failed": 0}
    assert not source.rows and not destination.rows
    with cleanup_database() as db:
        assert db.get(Job, JOB).cleanup_last_success == TICK + 901


def test_worker_repeats_standard_export_erasure_after_expiry_for_late_replicas_and_markers(
    regional_clients, cleanup_database, monkeypatch,
):
    expired_export(cleanup_database, output={"bucket": EXPORT_BUCKET, "key": EXPORT_PREFIX + "archive.zip"})
    source, destination, trace = regional_clients(EXPORT_BUCKET, [entry(EXPORT_PREFIX + "archive.zip")])

    for tick in (TICK, TICK + 901, TICK + 10_000_000):
        if tick > TICK:
            destination.add(entry(EXPORT_PREFIX + "archive.zip", f"late-payload-{tick}"))
            destination.add(entry(EXPORT_PREFIX + "archive.zip", f"late-marker-{tick}", True))
            assert not source.rows
        monkeypatch.setattr(worker, "now", lambda current=tick: current)
        assert worker.cleanup_once() == {"attempted": 1, "failed": 0}
        assert not source.rows and not destination.rows
        with cleanup_database() as db:
            row = db.get(Job, JOB)
            assert row.state == "expired" and row.output is None
            assert row.body == {"include_raw": False}
            assert row.cleanup_last_success == tick and row.cleanup_next_at == tick + 900

    assert len(source.deletes) == 1
    assert len(destination.deletes) == 3
    assert all(request["Prefix"] == EXPORT_PREFIX for _, operation, request in trace if operation == "inventory")
