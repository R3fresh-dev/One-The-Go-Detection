"""Erase observed CRR copies before deleting their primary object versions.

An empty destination inventory proves only the state observed by this call.
Callers must retain cleanup references and repeat sweeps for later replicas,
including when the primary prefix has become empty. Never use this for journal
authority or infer durable erasure from replication timing.
"""

import re

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from .config import settings
from .errors import Problem

MAX_PAGES = 20
MAX_VERSIONS = 10000
BACKUP_FIELDS = (
    "backup_region", "backup_artifact_bucket", "backup_export_bucket", "backup_kms_key_id"
)


def _blocked(code="REPLICA_CLEANUP_INCOMPLETE"):
    return Problem(503, code, retryable=True)


def _target(cfg, bucket):
    values = [getattr(cfg, field, None) for field in BACKUP_FIELDS]
    if all(value is None for value in values):
        return None
    account = getattr(cfg, "deployment_account", None)
    if (any(not isinstance(value, str) or not value for value in values)
            or not isinstance(account, str) or not re.fullmatch(r"[0-9]{12}", account)
            or getattr(cfg, "aws_region", None) != "us-east-1" or values[0] != "us-west-2"):
        raise _blocked("REPLICA_CLEANUP_CONFIGURATION_INVALID")
    expected = [f"otgd-fargate-recovery-{account}-us-west-2-{suffix}" for suffix in ("artifacts", "exports")]
    key = rf"arn:aws:kms:us-west-2:{account}:key/(?:[0-9a-f]{{8}}-(?:[0-9a-f]{{4}}-){{3}}[0-9a-f]{{12}}|mrk-[0-9a-f]{{32}})"
    if values[1:3] != expected or not re.fullmatch(key, values[3]):
        raise _blocked("REPLICA_CLEANUP_CONFIGURATION_INVALID")
    sources = [getattr(cfg, field, None) for field in ("artifact_bucket", "export_bucket")]
    for source, suffix in zip(sources, ("artifacts", "exports")):
        if (not isinstance(source, str) or not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", source)
                or not source.endswith(f"-{account}-us-east-1-{suffix}")):
            raise _blocked("REPLICA_CLEANUP_CONFIGURATION_INVALID")
    if bucket == getattr(cfg, "journal_bucket", None) or bucket not in sources:
        raise _blocked("REPLICA_CLEANUP_FORBIDDEN")
    return expected[sources.index(bucket)], account, values[3]


def _entries(rows, prefix, *, exact_key=False):
    if (not isinstance(prefix, str) or not prefix or "\x00" in prefix
            or len(prefix.encode()) > 1024 or not isinstance(rows, list) or len(rows) > MAX_VERSIONS
            or type(exact_key) is not bool):
        raise _blocked()
    seen = set()
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {"Key", "VersionId", "DeleteMarker"}
                or not isinstance(row["Key"], str) or not row["Key"].startswith(prefix)
                or (exact_key and row["Key"] != prefix)
                or not isinstance(row["VersionId"], str) or not row["VersionId"]
                or row["VersionId"] == "null" or len(row["VersionId"]) > 1024
                or type(row["DeleteMarker"]) is not bool):
            raise _blocked()
        identity = row["Key"], row["VersionId"]
        if identity in seen:
            raise _blocked()
        seen.add(identity)
    return rows


def _inventory(s3, bucket, prefix, account, *, exact_key=False):
    rows = []
    truncated = False
    for number, page in enumerate(s3.get_paginator("list_object_versions").paginate(
            Bucket=bucket, Prefix=prefix, ExpectedBucketOwner=account), 1):
        if number > MAX_PAGES or not isinstance(page, dict):
            raise _blocked()
        truncated = page.get("IsTruncated", False)
        if type(truncated) is not bool or (number == MAX_PAGES and truncated):
            raise _blocked()
        for field, marker in (("Versions", False), ("DeleteMarkers", True)):
            values = page.get(field, [])
            if not isinstance(values, list):
                raise _blocked()
            for value in values:
                if not isinstance(value, dict):
                    raise _blocked()
                rows.append({"Key": value.get("Key"), "VersionId": value.get("VersionId"), "DeleteMarker": marker})
                if len(rows) > MAX_VERSIONS:
                    raise _blocked()
    if truncated:
        raise _blocked()
    rows = _entries(rows, prefix)
    return [row for row in rows if row["Key"] == prefix] if exact_key else rows


def _head(s3, bucket, row, account):
    return s3.head_object(Bucket=bucket, Key=row["Key"], VersionId=row["VersionId"], ExpectedBucketOwner=account)


def _payload(head, version, status, key=None):
    if (not isinstance(head, dict) or head.get("VersionId") != version
            or head.get("ReplicationStatus") != status or head.get("DeleteMarker")
            or type(head.get("ContentLength")) is not int or head["ContentLength"] < 0
            or (key is not None and (head.get("ServerSideEncryption") != "aws:kms" or head.get("SSEKMSKeyId") != key))):
        raise _blocked()


def _missing_version(error):
    return (error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404
            and error.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NoSuchVersion", "NotFound"))


def _replica(s3, bucket, row, account, key, sources):
    identity = row["Key"], row["VersionId"]
    source = sources.get(identity)
    try:
        head = _head(s3, bucket, row, account)
    except ClientError as error:
        # A previous attempt may have erased this replica before losing its
        # response. Only an exact missing-version response for a source whose
        # COMPLETED status was verified above permits that retry.
        if source is not None and _missing_version(error):
            return False
        raise
    _payload(head, row["VersionId"], "REPLICA", key)
    if source is not None:
        if head["ContentLength"] != source["ContentLength"]:
            raise _blocked()
        if (head.get("ChecksumSHA256") is not None and source.get("ChecksumSHA256") is not None
                and head["ChecksumSHA256"] != source["ChecksumSHA256"]):
            raise _blocked()
    return True


def _destination_client():
    return boto3.client("s3", region_name="us-west-2", config=Config(
        signature_version="s3v4", ignore_configured_endpoint_urls=True,
        use_dualstack_endpoint=True, connect_timeout=5, read_timeout=30,
        retries={"mode": "standard", "total_max_attempts": 3},
        s3={"addressing_style": "path", "use_accelerate_endpoint": False},
    ))


def prepare_delete(source_s3, bucket, prefix, versions, *, cfg=None, destination_s3=None, exact_key=False):
    """Delete verified destination versions; return an observed removal count.

    Every source payload must be natively COMPLETED before any destination write.
    The caller deletes primary versions only after this returns, and must keep
    durable references for future sweeps. No object payload is read or logged.
    Delete markers have no payload and cannot recreate health data; delayed
    markers are handled by those same durable sweeps, without marker HEAD/405
    requests or an assumption about their replication deadline.
    """
    try:
        cfg = cfg if cfg is not None else settings()
        target = _target(cfg, bucket)
        if target is None:
            return 0
        destination, account, key = target
        versions = _entries(versions, prefix, exact_key=exact_key)
        sources = {}
        for row in versions:
            if row["DeleteMarker"]:
                continue
            head = _head(source_s3, bucket, row, account)
            _payload(head, row["VersionId"], "COMPLETED")
            sources[row["Key"], row["VersionId"]] = head
        s3 = destination_s3 if destination_s3 is not None else _destination_client()
        # Verify the pinned destination even if its version is missing from a
        # stale or partial inventory. Missing is accepted only after COMPLETED.
        verified = {identity for identity in sources if _replica(
            s3, destination, {"Key": identity[0], "VersionId": identity[1]}, account, key, sources)}
        observed = _inventory(s3, destination, prefix, account, exact_key=exact_key)
        for row in observed:
            if not row["DeleteMarker"] and (row["Key"], row["VersionId"]) not in verified:
                _replica(s3, destination, row, account, key, sources)
        removed = 0
        for offset in range(0, len(observed), 1000):
            objects = [{field: row[field] for field in ("Key", "VersionId")} for row in observed[offset:offset + 1000]]
            result = s3.delete_objects(Bucket=destination, ExpectedBucketOwner=account,
                Delete={"Objects": objects, "Quiet": True})
            if not isinstance(result, dict) or result.get("Errors"):
                raise _blocked()
            removed += len(objects)
        if _inventory(s3, destination, prefix, account, exact_key=exact_key):
            raise _blocked()
        return removed
    except Problem:
        raise
    except (BotoCoreError, ClientError, AttributeError, KeyError, TypeError, ValueError):
        raise _blocked() from None
