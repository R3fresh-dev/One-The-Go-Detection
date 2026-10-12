"""ECS task adapters around the canonical durable SQL and SQS operations.

The resident controller reads only DynamoDB metadata and queue attributes. A
conditional, expiring launch token bounds worker concurrency; accepting RunTask
never acknowledges an SQS delivery. Workers retain the existing SQL fencing,
immutable journal, heartbeat and deferred-outbox behavior.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import signal
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener
from uuid import UUID, uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

PREFIX = "otgd-serverless-development"
STARTUP_SECONDS = 300
TASK_SECONDS = 900
TASK_SOFT_SECONDS = 840
LEASE_GRACE_SECONDS = 30
MAX_DELIVERIES = 100
HEALTH_FILE = Path("/tmp/otgd-controller-health.json")


class LaunchUnavailable(RuntimeError):
    """A bounded worker could not be scheduled safely."""


class TaskDeadlineExceeded(TimeoutError):
    """Leave time to close SQL, join heartbeats and release metadata fences."""


def _uuid(value):
    if not isinstance(value, str):
        raise TypeError("A canonical launch token is required")
    try:
        canonical = str(UUID(value))
    except (ValueError, AttributeError):
        raise ValueError("A canonical launch token is required") from None
    if canonical != value:
        raise ValueError("A canonical launch token is required")
    return value


def _metadata_identity():
    account = os.environ.get("OTGD_DEPLOYMENT_ACCOUNT", "")
    region = os.environ.get("OTGD_AWS_REGION", os.environ.get("AWS_REGION", ""))
    if not re.fullmatch(r"[0-9]{12}", account) or region != "us-east-2":
        raise ValueError("The reviewed Ohio deployment identity is required")
    return account, region


def metadata_client(service):
    """No Settings, SQL or secret resolution in the resident controller."""
    _, region = _metadata_identity()
    if service not in {"dynamodb", "ecs", "sqs", "s3"}:
        raise ValueError("Unsupported task control service")
    return boto3.client(service, region_name=region,
        config=Config(ignore_configured_endpoint_urls=True,
            use_dualstack_endpoint=True, connect_timeout=5, read_timeout=15,
            retries={"max_attempts": 2, "mode": "standard"},
            s3={"addressing_style": "path"}))


def metadata_store():
    from .serverless_control import ControlStore
    return ControlStore(client=metadata_client("dynamodb"))


def _network_list(name, pattern, maximum):
    raw = os.environ.get(name, "")
    if len(raw) > 1024:
        raise ValueError("Task network metadata exceeds its bound")
    try:
        values = json.loads(raw)
    except (ValueError, TypeError):
        raise ValueError("Task network metadata must be a JSON list") from None
    if (not isinstance(values, list) or not 1 <= len(values) <= maximum
            or any(not isinstance(value, str) or not re.fullmatch(pattern, value) for value in values)
            or len(set(values)) != len(values)):
        raise ValueError("Invalid task network metadata")
    return values


def launch_configuration():
    account, region = _metadata_identity()
    cluster = os.environ.get("OTGD_ECS_CLUSTER_ARN", "")
    task = os.environ.get("OTGD_ECS_WORKER_TASK_DEFINITION_ARN", "")
    prefix = f"arn:aws:ecs:{region}:{account}:"
    if cluster != prefix + "cluster/" + PREFIX or not re.fullmatch(
            re.escape(prefix + "task-definition/" + PREFIX + "-worker:") + r"[1-9][0-9]*", task):
        raise ValueError("Worker launch must target the owned ECS cluster and task family")
    subnets = _network_list("OTGD_ECS_SUBNET_IDS", r"subnet-(?:[0-9a-f]{8}|[0-9a-f]{17})", 16)
    groups = _network_list("OTGD_ECS_SECURITY_GROUP_IDS", r"sg-(?:[0-9a-f]{8}|[0-9a-f]{17})", 5)
    return cluster, task, subnets, groups


def _launch_key():
    return {"PK": {"S": "runtime"}, "SK": {"S": "launch"}}


def _conditional(error):
    return error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException"


class LaunchGuard:
    def __init__(self, store=None):
        self.store = metadata_store() if store is None else store

    def acquire(self, token, instant):
        token = _uuid(token)
        if not math.isfinite(instant) or instant < 0:
            raise ValueError("A finite launch time is required")
        for _ in range(3):
            try:
                self.store.client.put_item(TableName=self.store.table_name,
                    Item={**_launch_key(), "token": {"S": token},
                        "acquiredAt": {"N": str(instant)},
                        "expiresAt": {"N": str(math.ceil(instant + STARTUP_SECONDS))}},
                    ConditionExpression="attribute_not_exists(PK) OR #expires <= :now",
                    ExpressionAttributeNames={"#expires": "expiresAt"},
                    ExpressionAttributeValues={":now": {"N": str(instant)}})
                return True
            except ClientError as error:
                if not _conditional(error):
                    raise LaunchUnavailable("Worker launch guard acquisition failed") from error
            except BotoCoreError as error:
                raise LaunchUnavailable("Worker launch guard acquisition failed") from error
            # A conditional rejection is success only when it represents a
            # valid, bounded owner. Corrupt metadata cannot indefinitely hide
            # a failed launch behind an apparently successful API response.
            from .serverless_control import ControlMetadataError, _number
            try:
                item = self.store.client.get_item(TableName=self.store.table_name,
                    Key=_launch_key(), ConsistentRead=True).get("Item")
                if item is None:
                    continue
                if (not {"PK", "SK", "token", "acquiredAt", "expiresAt"}.issubset(item)
                        or not set(item).issubset({"PK", "SK", "token", "acquiredAt", "expiresAt", "claimedAt"})
                        or any(item.get(key) != value for key, value in _launch_key().items())):
                    raise ValueError("Invalid launch metadata")
                _uuid(item.get("token", {}).get("S"))
                acquired = _number(item, "acquiredAt")
                expires = _number(item, "expiresAt")
                if (acquired > instant + 5 or expires != int(expires)
                        or not acquired < expires <= acquired + STARTUP_SECONDS + TASK_SECONDS + LEASE_GRACE_SECONDS):
                    raise ValueError("Invalid launch expiry")
                if "claimedAt" in item:
                    claimed = _number(item, "claimedAt")
                    if (not acquired <= claimed <= acquired + STARTUP_SECONDS
                            or claimed > instant + 5
                            or expires > claimed + TASK_SECONDS + LEASE_GRACE_SECONDS):
                        raise ValueError("Invalid claimed launch expiry")
                elif expires > math.ceil(acquired + STARTUP_SECONDS):
                    raise ValueError("Unclaimed launch exceeds its startup bound")
                if expires > instant:
                    return False
            except (ClientError, BotoCoreError, ControlMetadataError, ValueError, TypeError, AttributeError) as error:
                raise LaunchUnavailable("Existing launch guard is unavailable") from error
        raise LaunchUnavailable("Worker launch guard did not stabilize")

    def claim(self, token, deadline, instant=None):
        token = _uuid(token)
        instant = time.time() if instant is None else instant
        if (not math.isfinite(instant) or not math.isfinite(deadline)
                or not 0 <= instant < deadline <= instant + TASK_SECONDS):
            raise ValueError("A current bounded worker deadline is required")
        try:
            self.store.client.update_item(TableName=self.store.table_name, Key=_launch_key(),
                UpdateExpression="SET #expires = :deadline, #claimed = :now",
                ConditionExpression="#token = :token AND #expires > :now AND attribute_not_exists(#claimed)",
                ExpressionAttributeNames={"#token": "token", "#expires": "expiresAt", "#claimed": "claimedAt"},
                ExpressionAttributeValues={":token": {"S": token}, ":now": {"N": str(instant)},
                    ":deadline": {"N": str(math.ceil(deadline + LEASE_GRACE_SECONDS))}})
            return True
        except ClientError as error:
            if _conditional(error):
                return False
            raise LaunchUnavailable("Worker launch guard claim failed") from error
        except BotoCoreError as error:
            raise LaunchUnavailable("Worker launch guard claim failed") from error

    def release(self, token):
        token = _uuid(token)
        try:
            self.store.client.delete_item(TableName=self.store.table_name, Key=_launch_key(),
                ConditionExpression="#token = :token",
                ExpressionAttributeNames={"#token": "token"},
                ExpressionAttributeValues={":token": {"S": token}})
        except ClientError as error:
            if not _conditional(error):
                raise LaunchUnavailable("Worker launch guard release failed") from error
        except BotoCoreError as error:
            raise LaunchUnavailable("Worker launch guard release failed") from error


def request_worker_launch():
    """Return True for accepted or already-bounded work; never ACK a message."""
    cluster, task, subnets, groups = launch_configuration()
    guard = LaunchGuard()
    token = str(uuid4())
    if not guard.acquire(token, time.time()):
        return True
    try:
        response = metadata_client("ecs").run_task(cluster=cluster, taskDefinition=task,
            launchType="FARGATE", platformVersion="1.4.0", count=1,
            clientToken=token, startedBy="otgd-controller",
            networkConfiguration={"awsvpcConfiguration": {
                "subnets": subnets, "securityGroups": groups, "assignPublicIp": "DISABLED"}},
            overrides={"containerOverrides": [{"name": "worker", "environment": [
                {"name": "OTGD_FARGATE_LAUNCH_TOKEN", "value": token}]}]})
    except ClientError as error:
        # An explicit 4xx rejection did not accept work. Transport errors and
        # server errors can be ambiguous: leave the short token to bound retry.
        status = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)
        if 400 <= status < 500:
            guard.release(token)
        raise LaunchUnavailable("ECS worker launch was unavailable") from error
    except BotoCoreError as error:
        raise LaunchUnavailable("ECS worker launch outcome is unknown") from error
    tasks = response.get("tasks", [])
    account, region = _metadata_identity()
    valid = (isinstance(tasks, list) and len(tasks) == 1 and isinstance(tasks[0], dict)
        and re.fullmatch(re.escape(f"arn:aws:ecs:{region}:{account}:task/{PREFIX}/")
            + r"[0-9a-f]{32}", tasks[0].get("taskArn", "")))
    if response.get("failures") or not valid:
        guard.release(token)
        raise LaunchUnavailable("ECS did not accept the owned bounded worker")
    return True


def controller_tick(instant=None):
    """A one-minute metadata check cannot resume Aurora."""
    from .serverless_worker import SAFETY_SECONDS
    instant = time.time() if instant is None else instant
    snapshot = metadata_store().snapshot(now=instant)
    due = (bool(snapshot.active_leases)
        or snapshot.next_wake_at is not None and snapshot.next_wake_at <= instant
        or snapshot.last_reconciled_at is None
        or snapshot.last_reconciled_at <= instant - SAFETY_SECONDS)
    queue = os.environ.get("OTGD_QUEUE_URL", "")
    if queue:
        account, region = _metadata_identity()
        if not re.fullmatch(re.escape(f"https://sqs.{region}.amazonaws.com/{account}/")
                + re.escape(PREFIX) + r"[-A-Za-z0-9_]{1,80}", queue):
            raise ValueError("Controller queue must be owned by this deployment")
        attributes = metadata_client("sqs").get_queue_attributes(QueueUrl=queue,
            AttributeNames=["ApproximateNumberOfMessages"]).get("Attributes", {})
        visible = attributes.get("ApproximateNumberOfMessages")
        if not isinstance(visible, str) or not re.fullmatch(r"[0-9]{1,10}", visible):
            raise ValueError("Controller queue attributes are invalid")
        due = due or int(visible) > 0
    if due:
        request_worker_launch()
    return {"status": "scheduled" if due else "idle", "database_accessed": False}


def _write_health(status):
    temporary = HEALTH_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps({"time": time.time(), "status": status}, separators=(",", ":")))
    temporary.replace(HEALTH_FILE)


def controller_loop(stop=None):
    stop = threading.Event() if stop is None else stop
    while not stop.is_set():
        try:
            result = controller_tick()
            _write_health(result["status"])
        except Exception:  # noqa: BLE001 -- controller boundary emits no dependency contents
            # Leave the last successful heartbeat stale so ECS can replace a
            # persistently unhealthy controller. Never print application data.
            print("fargate_controller_dependency_failed", flush=True)
        stop.wait(60)


@dataclass(frozen=True)
class TaskContext:
    deadline: float

    def get_remaining_time_in_millis(self):
        return max(0, min(900_000, int((self.deadline - time.time()) * 1000)))


def _delivery(message):
    from .canonical import strict_loads
    if not isinstance(message, dict):
        raise TypeError("Invalid queue delivery")
    receipt, raw = message.get("ReceiptHandle"), message.get("Body")
    if (not isinstance(receipt, str) or not 0 < len(receipt) <= 4096
            or not isinstance(raw, str) or len(raw.encode()) > 8192):
        raise ValueError("Invalid queue delivery")
    body = strict_loads(raw)
    if (not isinstance(body, dict) or set(body) != {"schema_version", "job_id"}
            or body["schema_version"] != "1.0.0"):
        raise ValueError("Invalid queue body")
    return _uuid(body["job_id"]), receipt


def worker_task(context=None, *, stop=None):
    """Fence SQL for the task and join canonical heartbeats before releasing it."""
    from . import serverless_worker as adapter
    from .config import settings
    from .db import factory
    from .storage import client
    from .worker import cleanup_once, dispatch_once, run_job

    context = TaskContext(time.time() + TASK_SOFT_SECONDS) if context is None else context
    token = _uuid(os.environ.get("OTGD_FARGATE_LAUNCH_TOKEN", ""))
    store = metadata_store()
    guard = LaunchGuard(store)
    deadline = adapter.invocation_deadline(context)
    if not guard.claim(token, deadline):
        return {"status": "stale_launch", "database_accessed": False}
    lease = str(uuid4())
    acquired = False
    next_wake = None
    baseline = None
    other_producer = True
    acknowledged = 0
    try:
        before = store.snapshot()
        store.acquire(lease, deadline, kind="worker")
        acquired = True
        baseline = store.snapshot()
        other_producer = bool(before.active_leases) or any(
            row.lease_id != lease for row in baseline.active_leases)
        dispatch_once()
        outcome = cleanup_once()
        if outcome["failed"]:
            raise RuntimeError("Cleanup dependency failures require retry")
        cfg = settings()
        queue = client("sqs")
        for _ in range(MAX_DELIVERIES):
            remaining = context.get_remaining_time_in_millis()
            if remaining < 60_000 or stop is not None and stop.is_set():
                break
            messages = queue.receive_message(QueueUrl=cfg.queue_url, MaxNumberOfMessages=1,
                WaitTimeSeconds=min(20, remaining // 1000),
                VisibilityTimeout=cfg.serverless_queue_visibility).get("Messages", [])
            if not isinstance(messages, list) or len(messages) > 1:
                raise RuntimeError("Queue response exceeds the reviewed batch bound")
            if not messages:
                break
            try:
                job, receipt = _delivery(messages[0])
            except (ValueError, KeyError, TypeError, AttributeError):
                print("invalid_queue_delivery", flush=True)
                continue
            # This joins the real heartbeat, including any in-flight SQL/SQS,
            # before returning. Only durable terminal or deferred state is ACKed.
            result = run_job(job, receipt, heartbeat_join_timeout=None)
            if result in adapter.ACKNOWLEDGED:
                queue.delete_message(QueueUrl=cfg.queue_url, ReceiptHandle=receipt)
                acknowledged += 1
            dispatch_once()
        if context.get_remaining_time_in_millis() >= 1000:
            with factory()() as db:
                next_wake = adapter.next_wake_at(db, time.time())
                adapter.emit_operational_metrics(db)
    finally:
        if acquired:
            # If closing SQL fails, retain both fences until their bounded expiry.
            adapter.dispose_database()
            store.release(lease)
        guard.release(token)
    quiet = False
    if next_wake is not None:
        after = store.snapshot()
        if not other_producer and after.epoch == baseline.epoch and not after.active_leases:
            quiet = store.mark_reconciled(after, next_wake)
    return {"status": "passed", "acknowledged": acknowledged,
            "quiet_marked": quiet, "next_wake_at": next_wake}


def _task_arn():
    """Read AWS-injected link-local task identity without the session proxy."""
    raw = os.environ.get("ECS_CONTAINER_METADATA_URI_V4", "")
    parsed = urlparse(raw)
    if (parsed.scheme != "http" or parsed.hostname not in {"169.254.170.2", "fd00:ec2::23"}
            or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment
            or not re.fullmatch(r"/v4/[A-Za-z0-9-]{1,256}", parsed.path)):
        raise ValueError("An AWS task metadata endpoint is required")
    opener = build_opener(ProxyHandler({}))
    with opener.open(Request(raw + "/task"), timeout=3) as response:
        body = response.read(65537)
    if len(body) > 65536:
        raise ValueError("Task metadata exceeds its bound")
    value = json.loads(body).get("TaskARN")
    account, region = _metadata_identity()
    if not isinstance(value, str) or not re.fullmatch(
            re.escape(f"arn:aws:ecs:{region}:{account}:task/{PREFIX}/") + r"[0-9a-f]{32}", value):
        raise ValueError("Task identity is not owned by this deployment")
    return value


def _receipt_configuration():
    account, _ = _metadata_identity()
    source = os.environ.get("OTGD_SOURCE_REVISION", "")
    bucket = os.environ.get("OTGD_FARGATE_RECEIPT_BUCKET", "")
    key = os.environ.get("OTGD_FARGATE_RECEIPT_KEY", "")
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        raise ValueError("An immutable task source revision is required")
    if bucket != f"{PREFIX}-{account}-us-east-2-deployments":
        raise ValueError("The owned private deployment receipt bucket is required")
    if not re.fullmatch(re.escape("receipts/" + source + "/")
            + r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json", key):
        raise ValueError("A source-bound immutable receipt key is required")
    return source, bucket, key


def maintenance_task(operation, *, establish_new=False, context=None):
    """Admin-role task exposes only explicit release operations and safe receipts."""
    from .serverless_worker import maintenance_handler
    if operation not in {"bootstrap", "migrate", "admission"} or type(establish_new) is not bool:
        raise ValueError("An explicit reviewed maintenance operation is required")
    if establish_new and operation != "bootstrap":
        raise ValueError("New journal establishment is only a bootstrap operation")
    source, bucket, key = _receipt_configuration()
    task = _task_arn()
    context = TaskContext(time.time() + TASK_SOFT_SECONDS) if context is None else context
    event = {"operation": operation}
    if operation == "bootstrap":
        event["establish_new"] = establish_new
    receipt = {"schema_version": "1.0.0", "source_revision": source,
               "operation": operation, "task_arn": task, "status": "failed"}
    try:
        result = maintenance_handler(event, context)
        if result != {"operation": operation, "status": "passed"}:
            raise RuntimeError("Maintenance did not return its explicit success result")
        receipt["status"] = "passed"
    except Exception as error:
        receipt["reason"] = type(error).__name__
        _write_receipt(bucket, key, receipt)
        raise
    _write_receipt(bucket, key, receipt)
    return receipt


def _write_receipt(bucket, key, receipt):
    from .canonical import canonical
    metadata_client("s3").put_object(Bucket=bucket, Key=key, Body=canonical(receipt),
        ContentType="application/json", ServerSideEncryption="AES256", IfNoneMatch="*")


@contextmanager
def bounded_process():
    """Soft cancellation has a cleanup window; hard termination closes all sockets."""
    def exhausted(signum, frame):
        raise TaskDeadlineExceeded("Fargate operation reached its cleanup deadline")

    old = signal.signal(signal.SIGALRM, exhausted)
    signal.alarm(TASK_SOFT_SECONDS)
    hard = threading.Timer(TASK_SOFT_SECONDS + LEASE_GRACE_SECONDS, lambda: os._exit(124))
    hard.daemon = True
    hard.start()
    try:
        yield TaskContext(time.time() + TASK_SOFT_SECONDS)
    finally:
        signal.alarm(0)
        hard.cancel()
        signal.signal(signal.SIGALRM, old)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bounded ECS worker and release operations")
    parser.add_argument("mode", choices=("controller", "worker", "maintenance", "admin"))
    parser.add_argument("--operation", choices=("bootstrap", "migrate", "admission"))
    parser.add_argument("--establish-new", action="store_true")
    args = parser.parse_args(argv)
    if args.mode in ("controller", "worker") and (args.operation or args.establish_new):
        parser.error("Application tasks cannot run administrative release operations")
    if args.mode in ("maintenance", "admin") and not args.operation:
        parser.error("An explicit maintenance operation is required")
    stop = threading.Event()
    def stopped(signum, frame):
        stop.set()
    signal.signal(signal.SIGTERM, stopped)
    signal.signal(signal.SIGINT, stopped)
    try:
        if args.mode == "controller":
            controller_loop(stop)
        else:
            with bounded_process() as context:
                if args.mode == "worker":
                    worker_task(context, stop=stop)
                else:
                    maintenance_task(args.operation, establish_new=args.establish_new, context=context)
    except Exception:  # noqa: BLE001 -- process boundary returns a sanitized nonzero exit
        print("fargate_task_failed", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
