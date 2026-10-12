"""Actual disposable LocalStack conditional-write/version-cleanup acceptance.

Creates a unique fictional bucket, never touches participant objects or restarts
the shared emulator. Missing S3 behavior fails; there is no mocked fallback.
"""

import json
from uuid import uuid4

from botocore.exceptions import ClientError

from otgd.config import settings
from otgd.raw_retention import exact_versions, purge_exact_key
from otgd.storage import client


def probe():
    s = settings()
    if s.environment != "local" or not s.aws_endpoint_url:
        raise RuntimeError("This destructive disposable probe is LocalStack-only")
    s3 = client("s3")
    bucket = "otgd-local-raw-probe-" + uuid4().hex
    created = False
    key = "fictional/raw"
    try:
        args = {"Bucket": bucket}
        if s.aws_region != "us-east-1":
            args["CreateBucketConfiguration"] = {"LocationConstraint": s.aws_region}
        s3.create_bucket(**args)
        created = True
        s3.put_bucket_versioning(Bucket=bucket, VersioningConfiguration={"Status": "Enabled"})
        original = s3.put_object(Bucket=bucket, Key=key, Body=b"FICTIONAL RAW ONLY", IfNoneMatch="*")["VersionId"]
        if not original or original == "null":
            raise RuntimeError("Actual versioned upload identity is absent")
        # Revocation retains the original version during the signed-write
        # window; verification is denied by the independently tested API gate.
        try:
            s3.put_object(Bucket=bucket, Key=key, Body=b"FICTIONAL REPLAY", IfNoneMatch="*")
        except ClientError as exc:
            if exc.response["ResponseMetadata"]["HTTPStatusCode"] != 412:
                raise
        else:
            raise RuntimeError("Conditional-write barrier did not reject replay")
        neighbor = s3.put_object(Bucket=bucket, Key=key + "-neighbor", Body=b"FICTIONAL NEIGHBOR")["VersionId"]
        s3.delete_object(Bucket=bucket, Key=key)  # Actual delete marker, not byte removal.
        if original not in exact_versions(s3, bucket, key):
            raise RuntimeError("Delete marker incorrectly hid the retained bytes")
        purge_exact_key(s3, bucket, key)
        if exact_versions(s3, bucket, key):
            raise RuntimeError("Original bytes/marker survived exact cleanup")
        response = s3.get_object(Bucket=bucket, Key=key + "-neighbor", VersionId=neighbor)
        stream = response["Body"]
        try:
            neighbor_bytes = stream.read(32)
        finally:
            stream.close()
        if neighbor_bytes != b"FICTIONAL NEIGHBOR":
            raise RuntimeError("Exact cleanup affected a neighboring key")
        late = s3.put_object(Bucket=bucket, Key=key, Body=b"FICTIONAL LATE ARRIVAL")["VersionId"]
        if late == original:
            raise RuntimeError("A late upload did not receive a distinct version")
        purge_exact_key(s3, bucket, key)
        if exact_versions(s3, bucket, key):
            raise RuntimeError("Late version survived recurring cleanup")
        return {"status": "passed", "conditional_replay_http_status": 412,
            "exact_versions_deleted": True, "delete_marker_is_not_byte_erasure": True,
            "neighbor_unchanged": True, "late_arrival_reconciled": True}
    finally:
        if created:
            # Only the unique bucket created by this invocation is eligible.
            for item in s3.get_paginator("list_object_versions").paginate(Bucket=bucket):
                for row in item.get("Versions", []) + item.get("DeleteMarkers", []):
                    s3.delete_object(Bucket=bucket, Key=row["Key"], VersionId=row["VersionId"])
            s3.delete_bucket(Bucket=bucket)


if __name__ == "__main__":
    print(json.dumps(probe(), sort_keys=True))
