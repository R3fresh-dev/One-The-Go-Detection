"""Bounded ECS launch, delivery and release semantics; no live AWS claims."""
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from otgd import fargate_runtime as runtime
from otgd import serverless_control as control

ACCOUNT = "738470137867"
SOURCE = "a" * 40
TOKEN = "10000000-0000-0000-0000-000000000001"
OTHER = "10000000-0000-0000-0000-000000000002"
TASK = f"arn:aws:ecs:us-east-2:{ACCOUNT}:task/{runtime.PREFIX}/" + "b" * 32


def aws_error(code="ConditionalCheckFailedException", status=400):
    return ClientError({"Error": {"Code": code}, "ResponseMetadata": {"HTTPStatusCode": status}}, "RunTask")


class LaunchTable:
    """Evaluate token and expiry conditions atomically under a shared lock."""
    def __init__(self):
        self.item = None
        self.lock = threading.Lock()
        self.calls = []

    def put_item(self, **request):
        self.calls.append(("put", deepcopy(request)))
        assert request["ConditionExpression"] == "attribute_not_exists(PK) OR #expires <= :now"
        with self.lock:
            instant = Decimal(request["ExpressionAttributeValues"][":now"]["N"])
            if self.item and Decimal(self.item["expiresAt"]["N"]) > instant:
                raise aws_error()
            self.item = deepcopy(request["Item"])

    def update_item(self, **request):
        self.calls.append(("claim", deepcopy(request)))
        assert request["ConditionExpression"] == "#token = :token AND #expires > :now AND attribute_not_exists(#claimed)"
        with self.lock:
            values = request["ExpressionAttributeValues"]
            if (not self.item or self.item["token"] != values[":token"]
                    or "claimedAt" in self.item
                    or Decimal(self.item["expiresAt"]["N"]) <= Decimal(values[":now"]["N"])):
                raise aws_error()
            self.item["expiresAt"] = deepcopy(values[":deadline"])
            self.item["claimedAt"] = deepcopy(values[":now"])

    def get_item(self, **request):
        self.calls.append(("get", deepcopy(request)))
        assert request["ConsistentRead"] is True
        with self.lock:
            return {"Item": deepcopy(self.item)} if self.item else {}

    def delete_item(self, **request):
        self.calls.append(("release", deepcopy(request)))
        assert request["ConditionExpression"] == "#token = :token"
        with self.lock:
            if not self.item or self.item["token"] != request["ExpressionAttributeValues"][":token"]:
                raise aws_error()
            self.item = None


@pytest.fixture
def cloud(monkeypatch):
    monkeypatch.setenv("OTGD_DEPLOYMENT_ACCOUNT", ACCOUNT)
    monkeypatch.setenv("OTGD_AWS_REGION", "us-east-2")
    monkeypatch.setenv("OTGD_SERVERLESS_CONTROL_TABLE", runtime.PREFIX + "-runtime")
    monkeypatch.setenv("OTGD_ECS_CLUSTER_ARN", f"arn:aws:ecs:us-east-2:{ACCOUNT}:cluster/{runtime.PREFIX}")
    monkeypatch.setenv("OTGD_ECS_WORKER_TASK_DEFINITION_ARN", f"arn:aws:ecs:us-east-2:{ACCOUNT}:task-definition/{runtime.PREFIX}-worker:7")
    monkeypatch.setenv("OTGD_ECS_SUBNET_IDS", '["subnet-12345678", "subnet-abcdef12"]')
    monkeypatch.setenv("OTGD_ECS_SECURITY_GROUP_IDS", '["sg-12345678"]')
    monkeypatch.setenv("OTGD_FARGATE_LAUNCH_TOKEN", TOKEN)
    monkeypatch.setenv("OTGD_SOURCE_REVISION", SOURCE)
    monkeypatch.delenv("OTGD_QUEUE_URL", raising=False)
    table = LaunchTable()
    store = SimpleNamespace(client=table, table_name=runtime.PREFIX + "-runtime")
    monkeypatch.setattr(runtime, "metadata_store", lambda: store)
    monkeypatch.setattr(runtime.time, "time", lambda: 1000)
    return table, store


def test_competing_launches_are_one_conditional_metadata_mutation(cloud):
    table, store = cloud
    with ThreadPoolExecutor(max_workers=16) as pool:
        outcomes = list(pool.map(lambda _: runtime.LaunchGuard(store).acquire(str(uuid4()), 1000), range(32)))
    assert sum(outcomes) == 1
    assert set(table.item) == {"PK", "SK", "token", "acquiredAt", "expiresAt"}
    assert table.item["SK"] == {"S": "launch"}
    assert table.item["expiresAt"] == {"N": "1300"}


def test_expired_launch_can_be_replaced_and_old_worker_cannot_release_or_claim(cloud):
    table, store = cloud
    guard = runtime.LaunchGuard(store)
    assert guard.acquire(TOKEN, 1000)
    assert guard.acquire(OTHER, 1300)
    assert guard.claim(TOKEN, 1800, 1300) is False
    guard.release(TOKEN)
    assert table.item["token"] == {"S": OTHER}
    assert guard.claim(OTHER, 2100, 1300) is True
    assert table.item["expiresAt"] == {"N": "2130"}
    guard.release(OTHER)
    assert table.item is None


def test_worker_cannot_claim_expired_token_even_without_replacement(cloud):
    _, store = cloud
    guard = runtime.LaunchGuard(store)
    guard.acquire(TOKEN, 1000)
    assert guard.claim(TOKEN, 1600, 1300) is False


def test_even_duplicate_tasks_with_same_launch_token_have_one_worker_owner(cloud):
    _, store = cloud
    guard = runtime.LaunchGuard(store)
    guard.acquire(TOKEN, 1000)
    with ThreadPoolExecutor(max_workers=8) as pool:
        claimed = list(pool.map(lambda _: guard.claim(TOKEN, 1800, 1010), range(16)))
    assert sum(claimed) == 1
    assert guard.acquire(OTHER, 1010) is False


def test_corrupt_unbounded_launch_metadata_is_not_reported_as_accepted_work(cloud):
    table, store = cloud
    guard = runtime.LaunchGuard(store)
    guard.acquire(TOKEN, 1000)
    table.item["expiresAt"] = {"N": "999999999999"}
    with pytest.raises(runtime.LaunchUnavailable):
        guard.acquire(OTHER, 1000)
    table.item["expiresAt"] = {"N": "1300"}
    table.item["token"] = {"S": "not-uuid"}
    with pytest.raises(runtime.LaunchUnavailable):
        guard.acquire(OTHER, 1000)


def test_conditional_rejection_followed_by_release_can_retry_without_false_acceptance(cloud):
    table, store = cloud
    guard = runtime.LaunchGuard(store)
    guard.acquire(TOKEN, 1000)
    read = table.get_item
    def released(**kwargs):
        table.item = None
        return read(**kwargs)
    table.get_item = released
    assert guard.acquire(OTHER, 1000) is True
    assert table.item["token"] == {"S": OTHER}


@pytest.mark.parametrize("token,deadline,instant", [("NOT-UUID", 1500, 1000), (TOKEN, 1901, 1000),
    (TOKEN, 1000, 1000), (TOKEN, float("nan"), 1000)])
def test_guard_rejects_unbounded_identity_or_deadline(cloud, token, deadline, instant):
    _, store = cloud
    with pytest.raises(ValueError):
        runtime.LaunchGuard(store).claim(token, deadline, instant)


def test_launch_is_owned_private_fargate_and_acceptance_never_reads_queue(cloud, monkeypatch):
    table, _ = cloud
    calls = []
    def run(**request):
        calls.append(request)
        return {"tasks": [{"taskArn": TASK}], "failures": []}
    monkeypatch.setattr(runtime, "metadata_client", lambda service: SimpleNamespace(run_task=run))
    assert runtime.request_worker_launch() is True
    request = calls[0]
    assert request["cluster"].endswith("cluster/" + runtime.PREFIX)
    assert request["launchType"] == "FARGATE" and request["platformVersion"] == "1.4.0"
    assert request["count"] == 1
    assert request["networkConfiguration"]["awsvpcConfiguration"] == {
        "subnets": ["subnet-12345678", "subnet-abcdef12"],
        "securityGroups": ["sg-12345678"], "assignPublicIp": "DISABLED"}
    override = request["overrides"]["containerOverrides"]
    assert override == [{"name": "worker", "environment": [{"name": "OTGD_FARGATE_LAUNCH_TOKEN", "value": request["clientToken"]}]}]
    assert table.item["token"]["S"] == request["clientToken"]
    assert runtime.request_worker_launch() is True
    assert len(calls) == 1


@pytest.mark.parametrize("result", [{"failures": [{"reason": "capacity"}], "tasks": []},
    {"tasks": []}, {"tasks": [{"taskArn": "arn:aws:ecs:us-east-2:111111111111:task/unowned/" + "b" * 32}]},
    {"tasks": [{"taskArn": TASK}, {"taskArn": TASK}]}])
def test_nonaccepted_launch_releases_guard_and_raises(cloud, monkeypatch, result):
    table, _ = cloud
    monkeypatch.setattr(runtime, "metadata_client", lambda service: SimpleNamespace(run_task=lambda **kwargs: result))
    with pytest.raises(runtime.LaunchUnavailable):
        runtime.request_worker_launch()
    assert table.item is None


@pytest.mark.parametrize("error,retained", [(aws_error("AccessDeniedException", 403), False),
    (aws_error("InternalException", 500), True), (EndpointConnectionError(endpoint_url="https://ecs.us-east-2.api.aws"), True)])
def test_ambiguous_launch_retains_short_guard_while_definite_rejection_releases(cloud, monkeypatch, error, retained):
    table, _ = cloud
    def failed(**kwargs):
        raise error
    monkeypatch.setattr(runtime, "metadata_client", lambda service: SimpleNamespace(run_task=failed))
    with pytest.raises(runtime.LaunchUnavailable):
        runtime.request_worker_launch()
    assert (table.item is not None) is retained


@pytest.mark.parametrize("name,value", [("OTGD_DEPLOYMENT_ACCOUNT", "11111111111"),
    ("OTGD_AWS_REGION", "us-east-1"), ("OTGD_ECS_CLUSTER_ARN", f"arn:aws:ecs:us-east-2:{ACCOUNT}:cluster/company-generation-qa"),
    ("OTGD_ECS_WORKER_TASK_DEFINITION_ARN", f"arn:aws:ecs:us-east-2:{ACCOUNT}:task-definition/other-worker:1"),
    ("OTGD_ECS_SUBNET_IDS", "subnet-12345678"), ("OTGD_ECS_SUBNET_IDS", '["subnet-12345678","subnet-12345678"]'),
    ("OTGD_ECS_SECURITY_GROUP_IDS", '[]')])
def test_unowned_or_malformed_targets_fail_before_any_aws_mutation(cloud, monkeypatch, name, value):
    table, _ = cloud
    monkeypatch.setenv(name, value)
    monkeypatch.setattr(runtime, "metadata_client", lambda service: pytest.fail("Invalid targets cannot reach AWS"))
    with pytest.raises(ValueError):
        runtime.request_worker_launch()
    assert not table.calls


def test_idle_controller_reads_no_settings_secrets_or_sql(cloud, monkeypatch):
    from otgd import config, db, serverless_lifecycle
    _, store = cloud
    store.snapshot = lambda **kwargs: control.ControlSnapshot(1, 2000, 900, (), 1000)
    monkeypatch.setattr(config, "settings", lambda: pytest.fail("Controller cannot construct application Settings"))
    monkeypatch.setattr(serverless_lifecycle, "load_runtime_secrets", lambda **kwargs: pytest.fail("Controller cannot read secrets"))
    monkeypatch.setattr(db, "factory", lambda: pytest.fail("Controller cannot connect to SQL"))
    monkeypatch.setattr(runtime, "request_worker_launch", lambda: pytest.fail("Idle controller cannot launch work"))
    assert runtime.controller_tick(1000) == {"status": "idle", "database_accessed": False}


@pytest.mark.parametrize("snapshot", [control.ControlSnapshot(1, 1000, 900, (), 1000),
    control.ControlSnapshot(1, 2000, None, (), 1000), control.ControlSnapshot(1, 9000, 0, (), 3600),
    control.ControlSnapshot(1, 2000, 900, (control.ProducerLease(TOKEN, 1000, 1900),), 1000)])
def test_due_or_unknown_metadata_and_hourly_safety_launch_without_sql(cloud, monkeypatch, snapshot):
    _, store = cloud
    store.snapshot = lambda **kwargs: snapshot
    launches = []
    monkeypatch.setattr(runtime, "request_worker_launch", lambda: launches.append(True) or True)
    assert runtime.controller_tick(snapshot.observed_at)["status"] == "scheduled"
    assert launches == [True]


def test_visible_queue_can_wake_without_sql_and_account_is_bound(cloud, monkeypatch):
    _, store = cloud
    store.snapshot = lambda **kwargs: control.ControlSnapshot(1, 2000, 900, (), 1000)
    monkeypatch.setenv("OTGD_QUEUE_URL", f"https://sqs.us-east-2.amazonaws.com/{ACCOUNT}/{runtime.PREFIX}-jobs")
    reads, launches = [], []
    def attributes(**kwargs):
        reads.append(kwargs)
        return {"Attributes": {"ApproximateNumberOfMessages": "1"}}
    monkeypatch.setattr(runtime, "metadata_client", lambda service: SimpleNamespace(get_queue_attributes=attributes))
    monkeypatch.setattr(runtime, "request_worker_launch", lambda: launches.append(True) or True)
    assert runtime.controller_tick(1000)["status"] == "scheduled"
    assert reads[0]["AttributeNames"] == ["ApproximateNumberOfMessages"] and launches == [True]
    monkeypatch.setenv("OTGD_QUEUE_URL", "https://sqs.us-east-2.amazonaws.com/111111111111/other")
    with pytest.raises(ValueError):
        runtime.controller_tick(1000)


def worker_fixture(cloud, monkeypatch, *, outcome="completed", previous=False, race=False, remaining=180000):
    from otgd import config, db, storage, worker
    from otgd import serverless_worker as adapter
    table, store = cloud
    runtime.LaunchGuard(store).acquire(TOKEN, 1000)
    events = []
    own = []
    prior = control.ProducerLease(OTHER, 900, 1800) if previous else None
    def snapshot():
        if not own:
            return control.ControlSnapshot(1, 1000, 0, (prior,) if prior else (), 1000)
        active = (control.ProducerLease(own[0], 1000, 1900, "worker"),) if "released" not in events else ()
        epoch = 3 if race and "disposed" in events else 2
        return control.ControlSnapshot(epoch, 1000, 0, active, 1000)
    store.snapshot = snapshot
    store.acquire = lambda identity, deadline, **kwargs: (own.append(identity), events.append("acquired"))
    store.release = lambda identity: events.append("released")
    store.mark_reconciled = lambda *args: events.append("quiet") or True
    monkeypatch.setattr(adapter, "dispose_database", lambda: events.append("disposed"))
    monkeypatch.setattr(adapter, "next_wake_at", lambda db, instant: 1900)
    monkeypatch.setattr(adapter, "emit_operational_metrics", lambda db: events.append("metrics"))
    monkeypatch.setattr(worker, "dispatch_once", lambda: events.append("dispatch"))
    monkeypatch.setattr(worker, "cleanup_once", lambda: events.append("cleanup") or {"failed": 0})
    monkeypatch.setattr(config, "settings", lambda: SimpleNamespace(queue_url="fictional", serverless_queue_visibility=1200))
    def run(identity, receipt, *, heartbeat_join_timeout):
        assert heartbeat_join_timeout is None and receipt == "fictional-receipt"
        assert "acquired" in events and "released" not in events
        events.append("job-committed-heartbeat-joined")
        return outcome
    monkeypatch.setattr(worker, "run_job", run)
    messages = iter([[{"ReceiptHandle": "fictional-receipt", "Body": json.dumps({"schema_version": "1.0.0", "job_id": TOKEN})}], []])
    def receive(**kwargs):
        assert kwargs["VisibilityTimeout"] == 1200 and kwargs["MaxNumberOfMessages"] == 1
        return {"Messages": next(messages)}
    queue = SimpleNamespace(receive_message=receive, delete_message=lambda **kwargs: events.append("ack"))
    monkeypatch.setattr(storage, "client", lambda service: queue)
    @contextmanager
    def opened():
        assert "acquired" in events and "released" not in events
        yield object()
    monkeypatch.setattr(db, "factory", lambda: opened)
    context = SimpleNamespace(get_remaining_time_in_millis=lambda: remaining)
    return table, store, events, queue, context


@pytest.mark.parametrize("outcome,ack", [("completed", True), ("terminal", True), ("deferred", True),
    ("failed", False), ("busy", False), ("lease_lost", False)])
def test_worker_acks_only_durable_outcomes_after_join_and_releases_after_sql(cloud, monkeypatch, outcome, ack):
    table, _, events, _, context = worker_fixture(cloud, monkeypatch, outcome=outcome)
    result = runtime.worker_task(context)
    assert result["acknowledged"] == int(ack)
    assert ("ack" in events) is ack
    if ack:
        assert events.index("job-committed-heartbeat-joined") < events.index("ack")
    assert events.index("disposed") < events.index("released") < events.index("quiet")
    assert table.item is None


@pytest.mark.parametrize("previous,race", [(True, False), (False, True)])
def test_worker_cannot_mark_quiet_when_another_producer_commits_during_scan(cloud, monkeypatch, previous, race):
    _, _, events, _, context = worker_fixture(cloud, monkeypatch, previous=previous, race=race)
    assert runtime.worker_task(context)["quiet_marked"] is False
    assert "quiet" not in events


def test_failed_heartbeat_or_job_does_not_ack_and_still_closes_sql(cloud, monkeypatch):
    from otgd import worker
    table, _, events, _, context = worker_fixture(cloud, monkeypatch)
    def fail(*args, **kwargs):
        raise ConnectionError("fictional application data must not be printed")
    monkeypatch.setattr(worker, "run_job", fail)
    with pytest.raises(ConnectionError):
        runtime.worker_task(context)
    assert "ack" not in events and events[-2:] == ["disposed", "released"]
    assert table.item is None


def test_low_deadline_prevents_receiving_new_work_but_reconciles_cleanup(cloud, monkeypatch):
    _, _, events, queue, context = worker_fixture(cloud, monkeypatch, remaining=59999)
    queue.receive_message = lambda **kwargs: pytest.fail("Cannot start work in cleanup margin")
    result = runtime.worker_task(context)
    assert result["acknowledged"] == 0 and "cleanup" in events


def test_stale_worker_has_no_sql_or_settings_side_effect(cloud, monkeypatch):
    from otgd import config, worker
    _, store = cloud
    runtime.LaunchGuard(store).acquire(OTHER, 1000)
    monkeypatch.setattr(config, "settings", lambda: pytest.fail("Stale worker cannot resolve SQL settings"))
    monkeypatch.setattr(worker, "dispatch_once", lambda: pytest.fail("Stale worker cannot touch SQL"))
    assert runtime.worker_task(SimpleNamespace(get_remaining_time_in_millis=lambda: 180000)) == {
        "status": "stale_launch", "database_accessed": False}


def test_pool_cleanup_failure_retains_both_fences(cloud, monkeypatch):
    from otgd import serverless_worker as adapter
    table, _, events, _, context = worker_fixture(cloud, monkeypatch)
    def failed():
        raise ConnectionError("Pool is still live")
    monkeypatch.setattr(adapter, "dispose_database", failed)
    with pytest.raises(ConnectionError):
        runtime.worker_task(context)
    assert "released" not in events and table.item is not None


@pytest.mark.parametrize("raw", ["bad-json", json.dumps({"schema_version": "1.0.0", "job_id": "bad"}),
    json.dumps({"schema_version": "1.0.0", "job_id": TOKEN, "application_payload": "not allowed"})])
def test_invalid_delivery_is_never_executed_or_acknowledged(cloud, monkeypatch, raw):
    from otgd import worker
    _, _, events, queue, context = worker_fixture(cloud, monkeypatch)
    messages = iter([[{"ReceiptHandle": "fictional-receipt", "Body": raw}], []])
    queue.receive_message = lambda **kwargs: {"Messages": next(messages)}
    monkeypatch.setattr(worker, "run_job", lambda *args, **kwargs: pytest.fail("Malformed message cannot execute"))
    assert runtime.worker_task(context)["acknowledged"] == 0
    assert "ack" not in events


def test_retained_completed_privacy_cleanup_stays_fifteen_minutes(client, account):
    from otgd.db import Job, factory
    from otgd.serverless_worker import next_wake_at
    with factory().begin() as db:
        db.add(Job(id=TOKEN, account_id=account, generation=1, kind="deletion", state="completed",
            body={"scope": "all"}, accepted=1000, cleanup_next_at=1900, journal_accepted=True))
        db.flush()
        assert next_wake_at(db, 1000) == 1900


def test_maintenance_receipt_binds_actual_task_and_exact_source_without_result_contents(cloud, monkeypatch):
    from otgd import serverless_worker as adapter
    monkeypatch.setenv("OTGD_FARGATE_RECEIPT_BUCKET", f"{runtime.PREFIX}-{ACCOUNT}-us-east-2-deployments")
    monkeypatch.setenv("OTGD_FARGATE_RECEIPT_KEY", f"receipts/{SOURCE}/{TOKEN}.json")
    monkeypatch.setattr(runtime, "_task_arn", lambda: TASK)
    observed = []
    def maintenance(event, context):
        observed.append(event)
        return {"status": "passed", "operation": event["operation"]}
    monkeypatch.setattr(adapter, "maintenance_handler", maintenance)
    monkeypatch.setattr(runtime, "_write_receipt", lambda bucket, key, receipt: observed.append(dict(receipt)))
    result = runtime.maintenance_task("bootstrap", establish_new=True)
    assert observed[0] == {"operation": "bootstrap", "establish_new": True}
    assert result == {"schema_version": "1.0.0", "source_revision": SOURCE,
        "operation": "bootstrap", "task_arn": TASK, "status": "passed"}
    assert observed[1] == result


def test_admin_failure_receipt_contains_only_exception_type_and_task_exits_failure(cloud, monkeypatch):
    from otgd import serverless_worker as adapter
    monkeypatch.setenv("OTGD_FARGATE_RECEIPT_BUCKET", f"{runtime.PREFIX}-{ACCOUNT}-us-east-2-deployments")
    monkeypatch.setenv("OTGD_FARGATE_RECEIPT_KEY", f"receipts/{SOURCE}/{TOKEN}.json")
    monkeypatch.setattr(runtime, "_task_arn", lambda: TASK)
    def failed(*args):
        raise RuntimeError("fictional confidential database password")
    monkeypatch.setattr(adapter, "maintenance_handler", failed)
    receipts = []
    monkeypatch.setattr(runtime, "_write_receipt", lambda bucket, key, receipt: receipts.append(dict(receipt)))
    with pytest.raises(RuntimeError):
        runtime.maintenance_task("migrate")
    assert receipts[0]["status"] == "failed" and receipts[0]["reason"] == "RuntimeError"
    assert "password" not in json.dumps(receipts)


@pytest.mark.parametrize("operation,establish", [("sweep", False), ("dispatch", False), ("migrate", True), ("admission", 1)])
def test_admin_routes_are_explicit_and_journal_establishment_cannot_escape_bootstrap(cloud, operation, establish):
    with pytest.raises(ValueError):
        runtime.maintenance_task(operation, establish_new=establish)


def test_unbound_receipt_source_or_bucket_fails_before_admin_execution(cloud, monkeypatch):
    from otgd import serverless_worker as adapter
    monkeypatch.setattr(adapter, "maintenance_handler", lambda *args: pytest.fail("Unbound receipt cannot run admin work"))
    monkeypatch.setenv("OTGD_FARGATE_RECEIPT_BUCKET", "company-generation-deployments-" + ACCOUNT)
    monkeypatch.setenv("OTGD_FARGATE_RECEIPT_KEY", f"receipts/{SOURCE}/{TOKEN}.json")
    with pytest.raises(ValueError):
        runtime.maintenance_task("migrate")


def test_metadata_endpoint_rejects_external_or_untrusted_urls_before_network(cloud, monkeypatch):
    monkeypatch.setattr(runtime, "build_opener", lambda *args: pytest.fail("Untrusted metadata URI cannot reach network"))
    for value in ["https://169.254.170.2/v4/a", "http://example.com/v4/a", "http://169.254.170.2:80/v4/a",
                  "http://user@169.254.170.2/v4/a", "http://169.254.170.2/v4/a?other=true"]:
        monkeypatch.setenv("ECS_CONTAINER_METADATA_URI_V4", value)
        with pytest.raises(ValueError):
            runtime._task_arn()


def test_worker_cli_cannot_route_admin_operation():
    with pytest.raises(SystemExit) as caught:
        runtime.main(["worker", "--operation", "bootstrap"])
    assert caught.value.code == 2


def test_context_remaining_is_bounded_and_expires(cloud, monkeypatch):
    assert runtime.TaskContext(1900).get_remaining_time_in_millis() == 900000
    assert runtime.TaskContext(1000).get_remaining_time_in_millis() == 0
    assert runtime.TaskContext(999).get_remaining_time_in_millis() == 0


def test_metadata_sdk_uses_actual_dualstack_endpoints_and_no_application_settings(cloud, monkeypatch):
    import boto3
    from otgd import config
    monkeypatch.setattr(config, "settings", lambda: pytest.fail("Metadata SDK cannot construct Settings"))
    constructor = boto3.client
    observed = []
    def build(service, **kwargs):
        observed.append(kwargs["config"])
        return constructor(service, aws_access_key_id="fictional", aws_secret_access_key="fictional", **kwargs)
    monkeypatch.setattr(runtime.boto3, "client", build)
    for service, hostname in [("ecs", "ecs.us-east-2.api.aws"),
                              ("dynamodb", "dynamodb.us-east-2.api.aws"),
                              ("sqs", "sqs.us-east-2.api.aws"),
                              ("s3", "s3.dualstack.us-east-2.amazonaws.com")]:
        client = runtime.metadata_client(service)
        assert client.meta.endpoint_url == "https://" + hostname
        assert observed[-1].ignore_configured_endpoint_urls is True
    with pytest.raises(ValueError):
        runtime.metadata_client("secretsmanager")


def test_east1_metadata_and_receipts_bind_actual_region_without_allowing_backup_as_primary(cloud,monkeypatch):
    import boto3
    monkeypatch.setenv('OTGD_AWS_REGION','us-east-1')
    monkeypatch.setenv('OTGD_ECS_CLUSTER_ARN',f'arn:aws:ecs:us-east-1:{ACCOUNT}:cluster/{runtime.PREFIX}')
    monkeypatch.setenv('OTGD_ECS_WORKER_TASK_DEFINITION_ARN',f'arn:aws:ecs:us-east-1:{ACCOUNT}:task-definition/{runtime.PREFIX}-worker:7')
    assert runtime.launch_configuration()[0].startswith('arn:aws:ecs:us-east-1:')
    constructor=boto3.client
    monkeypatch.setattr(runtime.boto3,'client',lambda service,**kwargs:constructor(service,
        aws_access_key_id='fictional',aws_secret_access_key='fictional',**kwargs))
    assert runtime.metadata_client('ecs').meta.endpoint_url=='https://ecs.us-east-1.api.aws'
    key=f'receipts/{SOURCE}/00000000-0000-4000-8000-000000000001.json'
    monkeypatch.setenv('OTGD_FARGATE_RECEIPT_KEY',key)
    monkeypatch.setenv('OTGD_FARGATE_RECEIPT_BUCKET',f'{runtime.PREFIX}-{ACCOUNT}-us-east-1-deployments')
    assert runtime._receipt_configuration()==(SOURCE,f'{runtime.PREFIX}-{ACCOUNT}-us-east-1-deployments',key)
    monkeypatch.setenv('OTGD_FARGATE_RECEIPT_BUCKET',f'{runtime.PREFIX}-{ACCOUNT}-us-east-2-deployments')
    with pytest.raises(ValueError):runtime._receipt_configuration()
    monkeypatch.setenv('OTGD_AWS_REGION','us-west-2')
    with pytest.raises(ValueError):runtime._metadata_identity()


def test_successful_task_metadata_is_link_local_bounded_and_matches_owned_task(cloud, monkeypatch):
    monkeypatch.setenv("ECS_CONTAINER_METADATA_URI_V4", "http://169.254.170.2/v4/fictional-container")
    requests = []
    @contextmanager
    def opened(request, timeout):
        requests.append((request.full_url, timeout))
        yield SimpleNamespace(read=lambda maximum: json.dumps({"TaskARN": TASK}).encode())
    monkeypatch.setattr(runtime, "build_opener", lambda *args: SimpleNamespace(open=opened))
    assert runtime._task_arn() == TASK
    assert requests == [("http://169.254.170.2/v4/fictional-container/task", 3)]


def test_task_metadata_rejects_oversized_or_unowned_task(cloud, monkeypatch):
    monkeypatch.setenv("ECS_CONTAINER_METADATA_URI_V4", "http://169.254.170.2/v4/fictional-container")
    for body in [b"x" * 65537, json.dumps({"TaskARN": TASK.replace(ACCOUNT, "111111111111")}).encode()]:
        @contextmanager
        def opened(request, timeout, body=body):
            yield SimpleNamespace(read=lambda maximum: body)
        monkeypatch.setattr(runtime, "build_opener", lambda *args: SimpleNamespace(open=opened))
        with pytest.raises(ValueError):
            runtime._task_arn()


def test_receipt_is_conditional_private_encrypted_and_contains_no_admin_output(cloud, monkeypatch):
    writes = []
    monkeypatch.setattr(runtime, "metadata_client", lambda service: SimpleNamespace(put_object=lambda **kwargs: writes.append(kwargs)))
    receipt = {"source_revision": SOURCE, "operation": "admission", "status": "passed", "task_arn": TASK}
    runtime._write_receipt("fictional-deployment-bucket", "receipts/fictional.json", receipt)
    assert writes[0]["IfNoneMatch"] == "*" and writes[0]["ServerSideEncryption"] == "AES256"
    assert writes[0]["ContentType"] == "application/json"
    assert json.loads(writes[0]["Body"]) == receipt


def test_controller_health_tracks_success_only_and_loop_retries_sanitized_failure(cloud, monkeypatch, tmp_path, capsys):
    health = tmp_path / "health.json"
    monkeypatch.setattr(runtime, "HEALTH_FILE", health)
    states = iter([RuntimeError("fictional private dependency contents"), {"status": "idle"}])
    def tick():
        outcome = next(states)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome
    monkeypatch.setattr(runtime, "controller_tick", tick)
    stop = threading.Event()
    waits = []
    def wait(seconds):
        waits.append(seconds)
        if len(waits) == 2:
            stop.set()
    monkeypatch.setattr(stop, "wait", wait)
    runtime.controller_loop(stop)
    assert json.loads(health.read_text()) == {"time": 1000, "status": "idle"}
    assert waits == [60, 60]
    assert capsys.readouterr().out == "fargate_controller_dependency_failed\n"


def test_process_budget_reserves_cleanup_and_cancels_watchdog_on_completion(cloud, monkeypatch):
    events, handler = [], []
    def registered(number, callback):
        handler.append(callback)
        return "previous-handler"
    monkeypatch.setattr(runtime.signal, "signal", registered)
    monkeypatch.setattr(runtime.signal, "alarm", lambda value: events.append(("alarm", value)))
    monkeypatch.setattr(runtime.threading, "Timer", lambda seconds, callback: SimpleNamespace(
        start=lambda: events.append(("hard-start", seconds)),
        cancel=lambda: events.append(("hard-cancel", seconds)), daemon=False))
    with runtime.bounded_process() as context:
        assert context.deadline == 1840
        with pytest.raises(runtime.TaskDeadlineExceeded):
            handler[0](runtime.signal.SIGALRM, None)
    assert events == [("alarm", 840), ("hard-start", 870), ("alarm", 0), ("hard-cancel", 870)]
    assert handler[-1] == "previous-handler"


@pytest.mark.parametrize("mode", ["worker", "controller", "admin"])
def test_cli_runs_only_selected_task_mode_and_sanitizes_failure(cloud, monkeypatch, mode, capsys):
    @contextmanager
    def bounded():
        yield SimpleNamespace(deadline=1840)
    monkeypatch.setattr(runtime, "bounded_process", bounded)
    monkeypatch.setattr(runtime.signal, "signal", lambda *args: None)
    calls = []
    monkeypatch.setattr(runtime, "worker_task", lambda context, **kwargs: calls.append("worker"))
    monkeypatch.setattr(runtime, "controller_loop", lambda stop: calls.append("controller"))
    monkeypatch.setattr(runtime, "maintenance_task", lambda *args, **kwargs: calls.append("admin"))
    args = [mode, "--operation", "migrate"] if mode == "admin" else [mode]
    assert runtime.main(args) == 0 and calls == [mode]
    def failed(*args, **kwargs):
        raise RuntimeError("fictional private output")
    monkeypatch.setattr(runtime, "worker_task", failed)
    assert runtime.main(["worker"]) == 1
    assert capsys.readouterr().out == "fargate_task_failed\n"
