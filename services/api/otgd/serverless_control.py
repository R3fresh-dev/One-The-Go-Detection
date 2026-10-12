"""Metadata-only producer fencing for an idle, resumable SQL runtime.

A producer must acquire before opening SQL and release only after all of its
transactions finish. A reconciler takes a snapshot *before* its SQL scan, then
publishes the next deadline with an epoch compare-and-set. No application IDs,
request contents or SQL records belong in this table.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import json
import math
import os
import re
import time
from uuid import UUID, uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


MAX_INVOCATION_SECONDS = 900
LEASE_GRACE_SECONDS = 30
MAX_QUERY_PAGES = 16
MAX_LEASE_ITEMS = 512
QUERY_PAGE_SIZE = 64
MAX_ATTEMPTS = 3
MAX_EPOCH = 2**53 - 1
MAX_TIMESTAMP = 253402300799
KINDS = frozenset({"api", "worker", "maintenance"})


class ControlUnavailable(RuntimeError):
    """Fail closed: the caller must not start SQL or claim the runtime is idle."""


class ControlMetadataError(ControlUnavailable):
    """The control table contains invalid or unbounded metadata."""


@dataclass(frozen=True)
class ProducerLease:
    lease_id: str
    acquired_at: float
    expires_at: float
    kind: str = "api"


@dataclass(frozen=True)
class ControlSnapshot:
    epoch: int
    next_wake_at: float | None
    last_reconciled_at: float | None
    active_leases: tuple[ProducerLease, ...]
    observed_at: float


def _sdk_client(service):
    # The public control Lambda has no SQL credentials or application settings.
    # Its AWS_REGION and ambient execution role are sufficient for these clients.
    if os.environ.get("OTGD_SERVERLESS_CONTROL_ONLY") == "true":
        return boto3.client(
            service,
            region_name=os.environ.get("AWS_REGION", "us-east-2"),
            config=Config(
                ignore_configured_endpoint_urls=True,
                connect_timeout=5,
                read_timeout=10,
                retries={"max_attempts": 2, "mode": "standard"},
            ),
        )
    from .storage import client

    return client(service)


def _timestamp(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ControlMetadataError("Invalid control timestamp")
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ControlMetadataError("Invalid control timestamp") from None
    if not math.isfinite(result) or not 0 <= result <= MAX_TIMESTAMP:
        raise ControlMetadataError("Invalid control timestamp")
    return result


def _now(value=None):
    return _timestamp(time.time() if value is None else value)


def _uuid(value):
    if not isinstance(value, str):
        raise ControlMetadataError("Producer lease requires a UUID")
    try:
        canonical = str(UUID(value))
    except (ValueError, AttributeError):
        raise ControlMetadataError("Producer lease requires a UUID") from None
    if value != canonical:
        raise ControlMetadataError("Producer lease requires a canonical UUID")
    return value


def _n(value):
    return {"N": str(Decimal(str(value)))}


def _number(item, key, *, integer=False):
    value = item.get(key)
    if (
        not isinstance(value, dict)
        or set(value) != {"N"}
        or not isinstance(value["N"], str)
        or not 1 <= len(value["N"]) <= 64
    ):
        raise ControlMetadataError("Invalid numeric control metadata")
    try:
        number = Decimal(value["N"])
    except (InvalidOperation, TypeError, ValueError):
        raise ControlMetadataError("Invalid numeric control metadata") from None
    if not number.is_finite() or number < 0:
        raise ControlMetadataError("Invalid numeric control metadata")
    if integer:
        if number != number.to_integral_value() or number > MAX_EPOCH:
            raise ControlMetadataError("Invalid control epoch")
        return int(number)
    return _timestamp(number)


def _key(sk):
    return {"PK": {"S": "runtime"}, "SK": {"S": sk}}


def _validate_key(item, sk=None):
    if not isinstance(item, dict) or item.get("PK") != {"S": "runtime"}:
        raise ControlMetadataError("Invalid control partition")
    value = item.get("SK")
    if not isinstance(value, dict) or set(value) != {"S"} or not isinstance(value["S"], str):
        raise ControlMetadataError("Invalid control key")
    if sk is not None and value["S"] != sk:
        raise ControlMetadataError("Invalid control key")
    return value["S"]


def _read_control(item):
    if item is None:
        return (0, None, None)
    _validate_key(item, "control")
    if not set(item).issubset({"PK", "SK", "epoch", "nextWakeAt", "lastReconciledAt"}):
        raise ControlMetadataError("Unexpected control metadata")
    epoch = _number(item, "epoch", integer=True)
    wake = _number(item, "nextWakeAt") if "nextWakeAt" in item else None
    reconciled = _number(item, "lastReconciledAt") if "lastReconciledAt" in item else None
    return epoch, wake, reconciled


def _read_lease(item):
    sk = _validate_key(item)
    if (
        not sk.startswith("lease#")
        or not {"PK", "SK", "acquiredAt", "expiresAt"}.issubset(item)
        or not set(item).issubset({"PK", "SK", "acquiredAt", "expiresAt", "kind"})
    ):
        raise ControlMetadataError("Unexpected producer metadata")
    lease_id = _uuid(sk[6:])
    kind = item.get("kind", {"S": "api"})
    if not isinstance(kind, dict) or set(kind) != {"S"} or not isinstance(kind["S"], str) or kind["S"] not in KINDS:
        raise ControlMetadataError("Invalid producer kind")
    acquired = _number(item, "acquiredAt")
    expires = _number(item, "expiresAt")
    # expiresAt is an integer for DynamoDB TTL; round up to avoid early expiry.
    if expires != int(expires) or not acquired + LEASE_GRACE_SECONDS < expires <= math.ceil(acquired + MAX_INVOCATION_SECONDS + LEASE_GRACE_SECONDS):
        raise ControlMetadataError("Invalid producer expiry")
    return ProducerLease(lease_id, acquired, expires, kind["S"])


def _conflict(error):
    code = error.response.get("Error", {}).get("Code")
    return code == "TransactionConflictException" or (
        code == "TransactionCanceledException"
        and any(reason.get("Code") == "TransactionConflict" for reason in error.response.get("CancellationReasons", []))
    )


class ControlStore:
    def __init__(self, client=None, table_name=None):
        self.table_name = table_name or os.environ.get("OTGD_SERVERLESS_CONTROL_TABLE", "")
        if not isinstance(self.table_name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{3,255}", self.table_name):
            raise ControlMetadataError("A control table name is required")
        self.client = client if client is not None else _sdk_client("dynamodb")

    def acquire(self, lease_id, deadline=None, now=None, *, kind="api"):
        lease_id = _uuid(lease_id)
        if not isinstance(kind, str) or kind not in KINDS:
            raise ControlMetadataError("Invalid producer kind")
        acquired = _now(now)
        deadline = acquired + MAX_INVOCATION_SECONDS if deadline is None else _timestamp(deadline)
        if not acquired < deadline <= acquired + MAX_INVOCATION_SECONDS:
            raise ControlMetadataError("Invalid producer invocation deadline")
        expiry = math.ceil(deadline + LEASE_GRACE_SECONDS)
        _timestamp(expiry)
        lease = ProducerLease(lease_id, acquired, expiry, kind)
        transaction = [
            {"Update": {
                "TableName": self.table_name,
                "Key": _key("control"),
                "UpdateExpression": "SET #wake = :now ADD #epoch :one",
                "ConditionExpression": "attribute_not_exists(#epoch) OR (#epoch >= :zero AND #epoch < :max)",
                "ExpressionAttributeNames": {"#wake": "nextWakeAt", "#epoch": "epoch"},
                "ExpressionAttributeValues": {":now": _n(acquired), ":one": _n(1), ":zero": _n(0), ":max": _n(MAX_EPOCH)},
            }},
            {"Put": {
                "TableName": self.table_name,
                "Item": {**_key("lease#" + lease_id), "acquiredAt": _n(acquired), "expiresAt": _n(expiry), "kind": {"S": kind}},
                "ConditionExpression": "attribute_not_exists(PK)",
            }},
        ]
        for attempt in range(MAX_ATTEMPTS):
            try:
                self.client.transact_write_items(TransactItems=transaction, ClientRequestToken=lease_id)
                return lease
            except ClientError as error:
                if not _conflict(error) or attempt + 1 == MAX_ATTEMPTS:
                    raise ControlUnavailable("Producer lease acquisition failed") from error
                time.sleep(0.01 * 2**attempt)
            except BotoCoreError as error:
                raise ControlUnavailable("Producer lease acquisition failed") from error
        raise ControlUnavailable("Producer lease acquisition failed")

    def release(self, lease_id):
        lease_id = _uuid(lease_id)
        try:
            self.client.delete_item(TableName=self.table_name, Key=_key("lease#" + lease_id))
        except (ClientError, BotoCoreError) as error:
            raise ControlUnavailable("Producer lease release failed") from error

    def _control(self):
        result = self.client.get_item(TableName=self.table_name, Key=_key("control"), ConsistentRead=True)
        return _read_control(result.get("Item"))

    def _leases(self):
        leases = []
        seen_ids = set()
        seen_cursors = set()
        cursor = None
        for _ in range(MAX_QUERY_PAGES):
            request = dict(
                TableName=self.table_name,
                KeyConditionExpression="#pk = :pk AND begins_with(#sk, :prefix)",
                ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
                ExpressionAttributeValues={":pk": {"S": "runtime"}, ":prefix": {"S": "lease#"}},
                ConsistentRead=True,
                Limit=QUERY_PAGE_SIZE,
            )
            if cursor is not None:
                request["ExclusiveStartKey"] = cursor
            page = self.client.query(**request)
            items = page.get("Items", [])
            if not isinstance(items, list) or len(items) > QUERY_PAGE_SIZE or len(leases) + len(items) > MAX_LEASE_ITEMS:
                raise ControlMetadataError("Producer metadata exceeds read bound")
            for item in items:
                lease = _read_lease(item)
                if lease.lease_id in seen_ids:
                    raise ControlMetadataError("Duplicate producer metadata")
                seen_ids.add(lease.lease_id)
                leases.append(lease)
            cursor = page.get("LastEvaluatedKey")
            if not cursor:
                return leases
            sk = _validate_key(cursor)
            if set(cursor) != {"PK", "SK"} or not sk.startswith("lease#"):
                raise ControlMetadataError("Invalid producer pagination cursor")
            _uuid(sk[6:])
            if sk in seen_cursors:
                raise ControlMetadataError("Repeated producer pagination cursor")
            seen_cursors.add(sk)
        raise ControlMetadataError("Producer metadata exceeds pagination bound")

    def snapshot(self, now=None):
        observed = _now(now)
        try:
            for _ in range(MAX_ATTEMPTS):
                before = self._control()
                leases = self._leases()
                after = self._control()
                if before[0] != after[0]:
                    continue
                if any(lease.acquired_at > observed + 5 for lease in leases):
                    raise ControlMetadataError("Producer acquisition is in the future")
                return ControlSnapshot(*after, tuple(lease for lease in leases if lease.expires_at > observed), observed)
        except (ClientError, BotoCoreError) as error:
            raise ControlUnavailable("Control snapshot failed") from error
        raise ControlUnavailable("Control epoch did not stabilize")

    def mark_reconciled(self, snapshot, next_wake, now=None):
        if not isinstance(snapshot, ControlSnapshot):
            raise ControlMetadataError("A control snapshot is required")
        reconciled = _now(now)
        if reconciled < snapshot.observed_at:
            raise ControlMetadataError("Reconciliation predates its control snapshot")
        if snapshot.active_leases:
            return False
        wake = _timestamp(next_wake) if next_wake is not None else None
        names = {"#epoch": "epoch", "#wake": "nextWakeAt", "#reconciled": "lastReconciledAt"}
        values = {":epoch": _n(snapshot.epoch), ":now": _n(reconciled)}
        conditions = ["(#epoch = :epoch OR (attribute_not_exists(#epoch) AND :epoch = :zero))"]
        values[":zero"] = _n(0)
        # Also reject another reconciler's newer deadline while this SQL scan ran.
        for name, prior, placeholder in [("#wake", snapshot.next_wake_at, ":oldwake"), ("#reconciled", snapshot.last_reconciled_at, ":oldreconciled")]:
            if prior is None:
                conditions.append("attribute_not_exists(" + name + ")")
            else:
                conditions.append(name + " = " + placeholder)
                values[placeholder] = _n(prior)
        expression = "SET #epoch = :epoch, #reconciled = :now"
        if wake is None:
            expression += " REMOVE #wake"
        else:
            expression += ", #wake = :wake"
            values[":wake"] = _n(wake)
        try:
            self.client.update_item(
                TableName=self.table_name,
                Key=_key("control"),
                UpdateExpression=expression,
                ConditionExpression=" AND ".join(conditions),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
            )
            return True
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                return False
            raise ControlUnavailable("Reconciliation publication failed") from error
        except BotoCoreError as error:
            raise ControlUnavailable("Reconciliation publication failed") from error


@lru_cache
def _store(table_name):
    return ControlStore(table_name=table_name)


def control_store():
    return _store(os.environ.get("OTGD_SERVERLESS_CONTROL_TABLE", ""))


def acquire_lease(kind, lease_id, deadline=None, *, now=None):
    return control_store().acquire(lease_id, deadline, now, kind=kind)


def release_lease(lease_id):
    control_store().release(lease_id)


@contextmanager
def producer_lease(context=None, *, kind="api", lease_id=None, now=None):
    acquired = _now(now)
    deadline = acquired + MAX_INVOCATION_SECONDS
    if context is not None:
        remaining = context.get_remaining_time_in_millis()
        if isinstance(remaining, bool) or not isinstance(remaining, (int, float)) or not math.isfinite(remaining) or remaining <= 0:
            raise ControlMetadataError("Invalid remaining invocation lifetime")
        deadline = acquired + min(remaining / 1000, MAX_INVOCATION_SECONDS)
    lease_id = str(uuid4()) if lease_id is None else lease_id
    lease = acquire_lease(kind, lease_id, deadline, now=acquired)
    try:
        yield lease
    finally:
        release_lease(lease_id)


def control_handler(event, context):
    """Run outside the VPC: inspect metadata without resuming Aurora."""
    current = _now()
    snapshot = control_store().snapshot(now=current)
    due = bool(snapshot.active_leases) or (
        snapshot.next_wake_at is not None and snapshot.next_wake_at <= current
    ) or snapshot.last_reconciled_at is None or snapshot.last_reconciled_at <= current - 3600
    if not due:
        return {"status": "idle", "database_accessed": False}
    function = os.environ.get("OTGD_SERVERLESS_DISPATCH_FUNCTION_ARN", "")
    if not function or len(function) > 2048:
        raise ControlMetadataError("A dispatcher function ARN is required")
    try:
        result = _sdk_client("lambda").invoke(
            FunctionName=function,
            InvocationType="Event",
            Payload=json.dumps({"operation": "sweep"}, separators=(",", ":")).encode("ascii"),
        )
        payload = result.get("Payload")
        if payload is not None:
            payload.close()
        if result.get("StatusCode") != 202:
            raise ControlUnavailable("Dispatcher invocation was not accepted")
    except (ClientError, BotoCoreError) as error:
        raise ControlUnavailable("Dispatcher invocation failed") from error
    return {"status": "scheduled", "database_accessed": False}
