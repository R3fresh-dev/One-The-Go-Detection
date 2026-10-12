import base64
import hashlib
from functools import lru_cache

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from .canonical import canonical
from .config import settings
from .errors import Problem


@lru_cache
def client(service, public=False):
    s = settings()
    endpoint = s.s3_public_endpoint_url if public else s.aws_endpoint_url
    return boto3.client(
        service,
        region_name=s.aws_region,
        endpoint_url=endpoint,
        config=Config(
            signature_version="s3v4" if service == "s3" else "v4",
            ignore_configured_endpoint_urls=True,
            use_dualstack_endpoint=bool(getattr(s, "serverless_mode", False) and service in (
                "s3", "sqs", "kms", "cloudwatch", "sts", "lambda", "dynamodb")),
            connect_timeout=5,
            read_timeout=30,
            retries={"max_attempts": 3, "mode": "standard"},
            s3={"addressing_style": "path"},
        ),
    )


def encryption(bucket=None):
    s = settings()
    key = s.journal_kms_key_id if bucket == s.journal_bucket else s.storage_kms_key_id
    return (
        {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": key}
        if key
        else {"ServerSideEncryption": "AES256"}
    )


def versioned_read(bucket, key, version, limit):
    if not version or version == "null":
        raise Problem(503, "VERSIONING_REQUIRED")
    obj = client("s3").get_object(Bucket=bucket, Key=key, VersionId=version)
    if obj["ContentLength"] > limit:
        obj["Body"].close()
        raise Problem(413, "LIMIT_EXCEEDED")
    try:
        data = obj["Body"].read(limit + 1)
    finally:
        obj["Body"].close()
    if len(data) > limit:
        raise Problem(413, "LIMIT_EXCEEDED")
    return data


def put_versioned(bucket, key, data, media="application/json", conditional=False):
    params = dict(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentLength=len(data),
        ContentType=media,
        ChecksumSHA256=base64.b64encode(hashlib.sha256(data).digest()).decode(),
        **encryption(bucket),
    )
    if conditional:
        params["IfNoneMatch"] = "*"
    try:
        res = client("s3").put_object(**params)
    except ClientError as e:
        if e.response["ResponseMetadata"]["HTTPStatusCode"] != 412:
            raise
        res = client("s3").head_object(Bucket=bucket, Key=key)
        if versioned_read(bucket, key, res.get("VersionId"), len(data)) != data:
            raise Problem(409, "IMMUTABLE_OBJECT_CONFLICT")
    version = res.get("VersionId")
    if not version or version == "null":
        raise Problem(503, "VERSIONING_REQUIRED")
    return version


def upload_ticket(artifact):
    checksum = base64.b64encode(bytes.fromhex(artifact.sha256)).decode()
    params = dict(
        Bucket=artifact.bucket,
        Key=artifact.key,
        ContentLength=artifact.size,
        ContentType=artifact.media_type,
        ChecksumSHA256=checksum,
        IfNoneMatch="*",
        **encryption(),
    )
    url = client("s3", public=True).generate_presigned_url(
        "put_object", Params=params, ExpiresIn=300, HttpMethod="PUT"
    )
    headers = {
        "Content-Length": str(artifact.size),
        "Content-Type": artifact.media_type,
        "x-amz-checksum-sha256": checksum,
        "If-None-Match": "*",
        "x-amz-server-side-encryption": params["ServerSideEncryption"],
    }
    if "SSEKMSKeyId" in params:
        headers["x-amz-server-side-encryption-aws-kms-key-id"] = params["SSEKMSKeyId"]
    return {
        "artifact_id": artifact.id,
        "method": "PUT",
        "upload_url": url,
        "required_headers": headers,
        "expires_in_seconds": 300,
    }


def verify_artifact(artifact):
    head = client("s3").head_object(Bucket=artifact.bucket, Key=artifact.key)
    version = head.get("VersionId")
    data = versioned_read(artifact.bucket, artifact.key, version, artifact.size)
    if (
        len(data) != artifact.size
        or hashlib.sha256(data).hexdigest() != artifact.sha256
        or head.get("ContentType") != artifact.media_type
    ):
        raise Problem(422, "ARTIFACT_MISMATCH")
    if artifact.media_type == "application/pdf" and not data.startswith(b"%PDF-"):
        raise Problem(422, "MEDIA_MISMATCH")
    if artifact.media_type == "video/mp4" and (len(data) < 12 or data[4:8] != b"ftyp"):
        raise Problem(422, "MEDIA_MISMATCH")
    return version


def delete_versions(bucket, prefix):
    """Every version and marker, retaining durable DB references until successful."""
    removed = 0
    for page in (
        client("s3")
        .get_paginator("list_object_versions")
        .paginate(Bucket=bucket, Prefix=prefix)
    ):
        keys = [
            {"Key": v["Key"], "VersionId": v["VersionId"]}
            for field in ("Versions", "DeleteMarkers")
            for v in page.get(field, [])
            if v["Key"].startswith(prefix)
        ]
        for i in range(0, len(keys), 1000):
            result = client("s3").delete_objects(
                Bucket=bucket, Delete={"Objects": keys[i : i + 1000], "Quiet": True}
            )
            if result.get("Errors"):
                raise Problem(503, "OBJECT_CLEANUP_INCOMPLETE", retryable=True)
            removed += len(keys[i : i + 1000])
    return removed


def journal_accept(job, account, claims_subject=None):
    from .identity_keys import key_descriptor
    body = {
        "schema_version": "1.0.0",
        "event_type": "deletion_accepted",
        "event_id": job.id,
        "job_id": job.id,
        "account_ref": account.id,
        "retired_generation": job.generation,
        "new_generation": account.generation,
        "scope": job.body["scope"],
        "policy_version": "privacy-v1",
        "accepted_at": job.body["accepted_at"],
        "subject_ref_hmac": account.subject_hash,
        "hmac_key_id": key_descriptor()['key_id'],
    }
    raw = canonical(body)
    version = put_versioned(
        settings().journal_bucket,
        "events/" + job.id + "/accepted.json",
        raw,
        conditional=True,
    )
    if (
        versioned_read(
            settings().journal_bucket,
            "events/" + job.id + "/accepted.json",
            version,
            8192,
        )
        != raw
    ):
        raise Problem(503, "JOURNAL_VERIFICATION_FAILED")
    return {"version_id": version, "sha256": hashlib.sha256(raw).hexdigest()}
