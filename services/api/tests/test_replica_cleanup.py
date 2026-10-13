"""CRR erasure ordering and bounded, repeated cleanup; no live AWS claims."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from otgd import replica_cleanup as cleanup
from otgd.errors import Problem

ACCOUNT = "123456789012"
PRIMARY = f"otgd-serverless-development-{ACCOUNT}-us-east-1-artifacts"
DESTINATION = f"otgd-fargate-recovery-{ACCOUNT}-us-west-2-artifacts"
KEY = f"arn:aws:kms:us-west-2:{ACCOUNT}:key/12345678-1234-1234-1234-123456789012"
PREFIX = "retired-generation/"


def config(**changes):
    return SimpleNamespace(**{
        "aws_region": "us-east-1", "deployment_account": ACCOUNT,
        "artifact_bucket": PRIMARY, "export_bucket": PRIMARY.replace("artifacts", "exports"),
        "journal_bucket": PRIMARY.replace("artifacts", "journal"), "backup_region": "us-west-2",
        "backup_artifact_bucket": DESTINATION, "backup_export_bucket": DESTINATION.replace("artifacts", "exports"),
        "backup_kms_key_id": KEY, **changes})


def row(version="v1", key=PREFIX + "object", marker=False):
    return {"Key": key, "VersionId": version, "DeleteMarker": marker}


def head(version="v1", status="COMPLETED", **changes):
    return {"VersionId": version, "ReplicationStatus": status, "ContentLength": 7,
            "ETag": '"source-etag"', **changes}


def missing(code="404", http=404):
    return ClientError({"Error": {"Code": code}, "ResponseMetadata": {"HTTPStatusCode": http}}, "HeadObject")


class Source:
    def __init__(self, versions=()):
        self.heads = {(item["Key"], item["VersionId"]): head(item["VersionId"])
                      for item in versions if not item["DeleteMarker"]}
        self.calls = []

    def head_object(self, **request):
        self.calls.append(request)
        assert request["ExpectedBucketOwner"] == ACCOUNT
        assert "ChecksumMode" not in request
        value = self.heads.get((request["Key"], request["VersionId"]))
        if isinstance(value, Exception):
            raise value
        if value is None:
            raise missing()
        return deepcopy(value)

    def get_object(self, **request):
        raise AssertionError("Cleanup must never read payload data")

    def delete_objects(self, **request):
        raise AssertionError("The helper must not delete primary versions")


class Destination(Source):
    def __init__(self, versions=()):
        super().__init__(versions)
        self.versions = {(item["Key"], item["VersionId"]): deepcopy(item) for item in versions}
        for value in self.heads.values():
            value.update(ReplicationStatus="REPLICA", ServerSideEncryption="aws:kms", SSEKMSKeyId=KEY)
        self.inventories = []
        self.deletes = []
        self.pages = None
        self.delete_error = False
        self.after_delete = None
        self.prefix = PREFIX

    def get_paginator(self, operation):
        assert operation == "list_object_versions"
        return self

    def paginate(self, **request):
        self.inventories.append(request)
        assert request == {"Bucket": DESTINATION, "Prefix": self.prefix, "ExpectedBucketOwner": ACCOUNT}
        if isinstance(self.pages, Exception):
            raise self.pages
        if self.pages is not None:
            return deepcopy(self.pages)
        page = {"Versions": [], "DeleteMarkers": [], "IsTruncated": False}
        for value in self.versions.values():
            page["DeleteMarkers" if value["DeleteMarker"] else "Versions"].append(
                {field: value[field] for field in ("Key", "VersionId")})
        return [page]

    def delete_objects(self, **request):
        self.deletes.append(request)
        assert request["Bucket"] == DESTINATION and request["ExpectedBucketOwner"] == ACCOUNT
        assert request["Delete"]["Quiet"] is True
        values = request["Delete"]["Objects"]
        for value in values[:1] if self.delete_error else values:
            identity = value["Key"], value["VersionId"]
            self.versions.pop(identity, None)
            self.heads.pop(identity, None)
        if self.delete_error:
            return {"Errors": [{"Code": "AccessDenied"}]}
        if self.after_delete:
            self.after_delete(self)
        return {}

    def add(self, item):
        identity = item["Key"], item["VersionId"]
        self.versions[identity] = item
        if not item["DeleteMarker"]:
            self.heads[identity] = head(item["VersionId"], "REPLICA", ServerSideEncryption="aws:kms", SSEKMSKeyId=KEY)


def invoke(source, destination, versions, **changes):
    return cleanup.prepare_delete(source, PRIMARY, PREFIX, versions, cfg=config(**changes), destination_s3=destination)


def blocked(call):
    with pytest.raises(Problem) as failure:
        call()
    assert failure.value.status == 503 and failure.value.retryable


@pytest.mark.parametrize("status", ["PENDING", "FAILED", None, "UNKNOWN", "REPLICA"])
def test_every_source_payload_completes_before_any_destination_write(status):
    versions = [row("ready"), row("waiting")]
    source, destination = Source(versions), Destination(versions)
    source.heads[(PREFIX + "object", "waiting")]["ReplicationStatus"] = status
    blocked(lambda: invoke(source, destination, versions))
    assert not destination.calls and not destination.inventories and not destination.deletes


def test_matching_replica_versions_and_all_markers_are_deleted_before_primary_can_proceed():
    versions = [row("v1"), row("marker", marker=True)]
    source, destination = Source(versions), Destination(versions + [row("older")])
    assert invoke(source, destination, versions) == 3
    assert len(source.calls) == 1
    assert not destination.versions and len(destination.inventories) == 2
    assert {item["VersionId"] for item in destination.deletes[0]["Delete"]["Objects"]} == {"v1", "marker", "older"}


def test_different_encryption_etag_does_not_replace_native_replication_identity_check():
    versions = [row()]
    source, destination = Source(versions), Destination(versions)
    destination.heads[(PREFIX + "object", "v1")]["ETag"] = '"different-encryption-etag"'
    assert invoke(source, destination, versions) == 1


@pytest.mark.parametrize("field,value", [("VersionId", "other"), ("ReplicationStatus", "COMPLETED"),
    ("ContentLength", 8), ("SSEKMSKeyId", KEY.replace(ACCOUNT, "000000000000")), ("ServerSideEncryption", "AES256")])
def test_mismatched_destination_identity_status_length_or_key_prevents_all_deletion(field, value):
    versions = [row()]
    source, destination = Source(versions), Destination(versions)
    destination.heads[(PREFIX + "object", "v1")][field] = value
    blocked(lambda: invoke(source, destination, versions))
    assert not destination.deletes


def test_optional_checksums_are_compared_without_requesting_payload_or_kms_checksum_mode():
    versions = [row()]
    source, destination = Source(versions), Destination(versions)
    source.heads[(PREFIX + "object", "v1")]["ChecksumSHA256"] = "same"
    destination.heads[(PREFIX + "object", "v1")]["ChecksumSHA256"] = "different"
    blocked(lambda: invoke(source, destination, versions))
    assert not destination.deletes
    destination.heads[(PREFIX + "object", "v1")]["ChecksumSHA256"] = "same"
    assert invoke(source, destination, versions) == 1


def test_partial_destination_delete_is_not_success_and_completed_missing_replica_allows_retry():
    versions = [row("v1"), row("v2")]
    source, destination = Source(versions), Destination(versions)
    destination.delete_error = True
    blocked(lambda: invoke(source, destination, versions))
    assert len(destination.versions) == 1
    destination.delete_error = False
    assert invoke(source, destination, versions) == 1
    assert not destination.versions


def test_later_replicas_and_markers_are_erased_by_retained_reference_sweeps_after_source_is_empty():
    versions = [row()]
    source, destination = Source(versions), Destination(versions)
    assert invoke(source, destination, versions) == 1
    source.heads.clear()
    destination.add(row("late-version"))
    destination.add(row("late-marker", marker=True))
    assert invoke(source, destination, []) == 2
    assert not destination.versions


def test_exact_key_cleanup_preserves_neighbor_payload_and_markers_while_erasing_owned_versions():
    exact = PREFIX + "object"
    versions = [row("owned", exact)]
    neighbor = row("neighbor", exact + "-neighbor")
    neighbor_marker = row("neighbor-marker", exact + "-neighbor", marker=True)
    source, destination = Source(versions), Destination(versions + [neighbor, neighbor_marker])
    destination.prefix = exact
    assert cleanup.prepare_delete(source, PRIMARY, exact, versions, cfg=config(),
                                  destination_s3=destination, exact_key=True) == 1
    assert set(destination.versions) == {(neighbor["Key"], neighbor["VersionId"]),
                                        (neighbor_marker["Key"], neighbor_marker["VersionId"])}
    assert destination.deletes[0]["Delete"]["Objects"] == [{"Key": exact, "VersionId": "owned"}]
    assert all(request["Key"] == exact for request in destination.calls)


def test_exact_key_cleanup_rejects_source_neighbors_and_destination_out_of_prefix_rows():
    exact = PREFIX + "object"
    source, destination = Source(), Destination()
    destination.prefix = exact
    blocked(lambda: cleanup.prepare_delete(source, PRIMARY, exact, [row("neighbor", exact + "-neighbor")],
        cfg=config(), destination_s3=destination, exact_key=True))
    assert not source.calls and not destination.inventories
    destination.pages = [{"Versions": [{"Key": "foreign", "VersionId": "v1"}]}]
    blocked(lambda: cleanup.prepare_delete(source, PRIMARY, exact, [],
        cfg=config(), destination_s3=destination, exact_key=True))
    assert not destination.deletes


def test_replica_arriving_during_final_inventory_blocks_success_until_another_sweep():
    versions = [row()]
    source, destination = Source(versions), Destination(versions)
    destination.after_delete = lambda target: target.add(row("late-version"))
    blocked(lambda: invoke(source, destination, versions))
    assert (PREFIX + "object", "late-version") in destination.versions
    destination.after_delete = None
    assert invoke(source, destination, versions) == 1


@pytest.mark.parametrize("error", [missing("NoSuchBucket"), missing("AccessDenied", 403),
    EndpointConnectionError(endpoint_url="https://s3.dualstack.us-west-2.amazonaws.com")])
def test_region_outage_missing_bucket_and_denied_head_never_report_cleanup_success(error):
    versions = [row()]
    source, destination = Source(versions), Destination(versions)
    destination.heads[(PREFIX + "object", "v1")] = error
    blocked(lambda: invoke(source, destination, versions))
    assert not destination.deletes


def test_completed_source_with_exact_missing_destination_version_is_retryable_success():
    versions = [row()]
    assert invoke(Source(versions), Destination(), versions) == 0
    blocked(lambda: invoke(Source(), Destination(), versions))


def test_pinned_version_appearing_after_missing_head_is_revalidated_before_any_write():
    versions = [row()]
    source, destination = Source(versions), Destination()
    original = destination.head_object
    def first_missing(**request):
        destination.head_object = original
        destination.add(versions[0])
        destination.heads[(PREFIX + "object", "v1")]["SSEKMSKeyId"] = "different-key"
        raise missing()
    destination.head_object = first_missing
    blocked(lambda: invoke(source, destination, versions))
    assert not destination.deletes


def test_marker_only_cleanup_uses_no_payload_heads_and_makes_no_future_closure_claim():
    versions = [row("marker", marker=True)]
    source, destination = Source(versions), Destination(versions)
    assert invoke(source, destination, versions) == 1
    assert not source.calls and not destination.calls
    destination.add(row("late-after-marker"))
    assert invoke(source, destination, []) == 1


@pytest.mark.parametrize("changes", [{"backup_region": None}, {"backup_export_bucket": None},
    {"backup_region": "us-east-2"}, {"aws_region": "us-east-2"}, {"deployment_account": "000000000000"},
    {"backup_artifact_bucket": "foreign"}, {"backup_kms_key_id": KEY.replace("us-west-2", "us-east-1")},
    {"backup_kms_key_id": "alias/backup"}, {"artifact_bucket": "foreign"}])
def test_partial_foreign_or_malformed_backup_tuple_fails_before_storage_access(changes):
    source, destination = Source(), Destination()
    blocked(lambda: invoke(source, destination, [], **changes))
    assert not source.calls and not destination.calls and not destination.inventories and not destination.deletes


def test_journal_is_always_forbidden_when_replica_cleanup_is_configured():
    cfg = config()
    blocked(lambda: cleanup.prepare_delete(Source(), cfg.journal_bucket, "events/", [], cfg=cfg, destination_s3=Destination()))


@pytest.mark.parametrize("region", ["us-east-2", "us-east-1"])
def test_absent_backup_tuple_leaves_legacy_and_local_cleanup_unchanged(region):
    cfg = SimpleNamespace(aws_region=region)
    source, destination = Mock(), Mock()
    assert cleanup.prepare_delete(source, "local", "owned/", [], cfg=cfg, destination_s3=destination) == 0
    assert not source.mock_calls and not destination.mock_calls


@pytest.mark.parametrize("versions", [[row(None)], [row("null")], [row(), row()], [row(key="foreign/key")],
    [{"Key": PREFIX + "object", "VersionId": "v1", "DeleteMarker": 1}],
    [{"Key": PREFIX + "object", "VersionId": "v1"}]])
def test_malformed_duplicate_or_out_of_prefix_source_inventory_blocks_all_storage_access(versions):
    source, destination = Mock(), Mock()
    blocked(lambda: invoke(source, destination, versions))
    assert not source.mock_calls and not destination.mock_calls


def test_source_and_destination_inventory_bounds_fail_before_writes():
    versions = [row(str(number)) for number in range(cleanup.MAX_VERSIONS + 1)]
    source, destination = Mock(), Destination()
    blocked(lambda: invoke(source, destination, versions))
    assert not source.mock_calls and not destination.deletes
    destination.pages = [{"Versions": [{"Key": item["Key"], "VersionId": item["VersionId"]} for item in versions]}]
    blocked(lambda: invoke(Source(), destination, []))
    assert not destination.deletes
    destination.pages = [{"IsTruncated": True} for _ in range(cleanup.MAX_PAGES)]
    blocked(lambda: invoke(Source(), destination, []))
    assert not destination.deletes


@pytest.mark.parametrize("entries", [[{"Key": "foreign", "VersionId": "v1"}],
    [{"Key": PREFIX + "object", "VersionId": "null"}],
    [{"Key": PREFIX + "object", "VersionId": "v1"}] * 2])
def test_destination_inventory_is_validated_before_any_delete(entries):
    destination = Destination()
    destination.pages = [{"Versions": entries}]
    blocked(lambda: invoke(Source(), destination, []))
    assert not destination.deletes


def test_destination_versions_are_deleted_in_bounded_batches():
    destination = Destination([row(str(number)) for number in range(1001)])
    assert invoke(Source(), destination, []) == 1001
    assert [len(request["Delete"]["Objects"]) for request in destination.deletes] == [1000, 1]


def test_west_client_ignores_endpoint_overrides_and_has_bounded_standard_retries(monkeypatch):
    versions = [row()]
    source, destination = Source(versions), Destination(versions)
    constructor = Mock(return_value=destination)
    monkeypatch.setattr(cleanup.boto3, "client", constructor)
    assert cleanup.prepare_delete(source, PRIMARY, PREFIX, versions, cfg=config()) == 1
    assert constructor.call_args.args == ("s3",)
    options = constructor.call_args.kwargs
    assert options["region_name"] == "us-west-2" and "endpoint_url" not in options
    sdk = options["config"]
    assert sdk.ignore_configured_endpoint_urls and sdk.use_dualstack_endpoint
    assert sdk.connect_timeout == 5 and sdk.read_timeout == 30
    assert sdk.retries == {"mode": "standard", "total_max_attempts": 3}
