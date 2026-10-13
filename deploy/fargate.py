#!/usr/bin/env python3
"""Deploy reviewed On-The-Go UI, API, jobs and maintenance to ECS Fargate."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:] = [p for p in sys.path if Path(p).resolve() != ROOT / 'deploy']
sys.path.insert(0, str(ROOT))

import argparse
import base64
from datetime import datetime, timezone
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import ipaddress
import json
import math
import os
import re
import socket
import subprocess
import tarfile
import tempfile
import time
import uuid

from botocore.exceptions import ClientError
import httpx

from deploy import platform, web_artifact
from deploy.check_access import identity_selection
from deploy.orchestrate import StageJournal
from deploy.provenance import FARGATE_REQUIRED_JOBS, Gate, bounded_json, sha256, strict_loads
from deploy.serverless import STACK, pages, stable_stack, deploy_stack, verify_upload_access

FIELDS = {'environment', 'account', 'region', 'alarmEmail', 'monthlyBudgetUsd', 'releaseId',
          'plannedMonthlyUsers', 'costEstimatePath'}
PROFILE = 'fargate-development'


def read_config(path):
    c = bounded_json(path)
    if (set(c) != FIELDS or c.get('environment') != PROFILE
            or not re.fullmatch(r'\d{12}', c.get('account', '')) or c.get('region') != 'us-east-2'
            or not re.fullmatch(r'[0-9a-f]{40}', c.get('releaseId', ''))
            or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', c.get('alarmEmail', ''))
            or type(c.get('monthlyBudgetUsd')) not in (int, float)
            or not math.isfinite(c['monthlyBudgetUsd']) or not 0 < c['monthlyBudgetUsd'] <= 100
            or type(c.get('plannedMonthlyUsers')) is not int or c['plannedMonthlyUsers'] not in (0, 10)):
        raise Gate('Supply the reviewed Fargate development account, Ohio region, source, email and budget')
    return c


def budget(c):
    path = Path(c['costEstimatePath'])
    path = path if path.is_absolute() else ROOT / path
    evidence = bounded_json(path, 262144)
    if (evidence.get('region') != c['region'] or evidence.get('deployment_profile') != PROFILE
            or evidence.get('unverified_rates') != [] or not evidence.get('rates')):
        raise Gate('Verified matching Fargate pricing evidence is required')
    checked = datetime.fromisoformat(evidence['checked_at'].replace('Z', '+00:00'))
    checked = checked if checked.tzinfo else checked.replace(tzinfo=timezone.utc)
    if not -86400 <= (datetime.now(timezone.utc) - checked).total_seconds() <= 31 * 86400:
        raise Gate('Refresh the Fargate pricing evidence')
    assumptions = evidence.get('selected_scenario_assumptions', {})
    required = {'configured_min_acu': 0, 'configured_max_acu': 1, 'average_active_acu': 0.5,
                'service_vcpu': 0.25, 'service_memory_gb': 1, 'service_desired_count': 1,
                'worker_vcpu': 0.5, 'worker_memory_gb': 2, 'worker_charged_seconds': 180,
                'recurring_privacy_cleanup_interval_seconds': 900, 'retained_privacy_cleanup_included': True}
    if any(assumptions.get(k) != value for k, value in required.items()):
        raise Gate('Fargate pricing must preserve private database capacity and retained privacy cleanup')
    cases = [row for row in evidence.get('scenarios', []) if row.get('monthly_active_users') == c['plannedMonthlyUsers']]
    if len(cases) != 1 or not cases[0].get('items'):
        raise Gate('One reconciled Fargate workload case is required')
    def reconcile(case):
        if not case.get('items') or type(case.get('total_monthly_usd')) not in (int, float):
            raise Gate('Every Fargate workload requires finite reconciled cost lines')
        total = Decimal('0')
        for item in case['items']:
            rate = evidence['rates'].get(item.get('rate'), {})
            values = [item.get('quantity'), item.get('monthly_usd'), rate.get('usd')]
            if (any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values)
                    or not all(isinstance(rate.get(k), str) and rate[k] for k in ('unit', 'source', 'sku', 'rate_code'))
                    or not rate['source'].startswith('https://pricing.us-east-1.amazonaws.com/')
                    or item['rate'].startswith('lambda')):
                raise Gate('Every Fargate line requires finite official price evidence')
            amount = (Decimal(str(item['quantity'])) * Decimal(str(rate['usd']))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            if amount != Decimal(str(item['monthly_usd'])):
                raise Gate('Fargate price arithmetic does not reconcile')
            total += amount
        if not math.isfinite(case['total_monthly_usd']) or total != Decimal(str(case['total_monthly_usd'])):
            raise Gate('Fargate workload total does not reconcile')
        return total
    total = reconcile(cases[0])
    stress = [row for row in evidence.get('configured_maximum_1_acu_stress_scenarios', [])
              if row.get('monthly_active_users') == c['plannedMonthlyUsers']]
    if (total > Decimal(str(c['monthlyBudgetUsd'])) or len(stress) != 1
            or reconcile(stress[0]) > Decimal(str(c['monthlyBudgetUsd']))):
        raise Gate('The reviewed Fargate workload or supported-capacity stress case exceeds the approved budget')
    return {'estimated_monthly_usd': float(total), 'maximum_capacity_stress_monthly_usd': stress[0]['total_monthly_usd'],
            'budget_usd': c['monthlyBudgetUsd'], 'planned_monthly_users': c['plannedMonthlyUsers'],
            'planning_assumptions': assumptions, 'price_evidence_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'budget_is_a_spending_cap': False}


def preflight(aws, c, prior, retained_engine_version=None):
    if aws.client('sts').get_caller_identity()['Account'] != c['account']:
        raise Gate('AWS credentials do not match the selected account')
    plan = aws.client('freetier').get_account_plan_state()
    if (plan.get('accountId') != c['account'] or plan.get('accountPlanType') != 'PAID'
            or plan.get('accountPlanStatus') != 'ACTIVE'):
        raise Gate('An active AWS Paid Plan is required for the private Aurora deployment')
    if stable_stack(aws, 'otgd-qa-platform', absent_ok=True):
        raise Gate('Select a separate development account from the managed QA authority')
    rds = aws.client('rds')
    if prior and prior.get('DatabaseClusterIdentifier'):
        row = rds.describe_db_clusters(DBClusterIdentifier=prior['DatabaseClusterIdentifier'])['DBClusters']
        if len(row) != 1:
            raise Gate('Retained database is unavailable')
        version = row[0]['EngineVersion']
    else:
        versions = [r for page in pages(rds, 'describe_db_engine_versions', Engine='aurora-postgresql')
                    for r in page['DBEngineVersions'] if r.get('Status') == 'available'
                    and re.fullmatch(r'16\.\d+', r.get('EngineVersion', ''))
                    and r.get('ServerlessV2FeaturesSupport', {}).get('MinCapacity') == 0]
        if not versions:
            raise Gate('Aurora PostgreSQL 16 with zero-capacity auto-pause is unavailable')
        if retained_engine_version is not None:
            matches = [row for row in versions if row['EngineVersion'] == retained_engine_version]
            if len(matches) != 1:
                raise Gate('The retained Aurora engine version no longer matches reviewed available capacity')
            version = retained_engine_version
        else:
            version = max(versions, key=lambda r: int(r['EngineVersion'].split('.')[1]))['EngineVersion']
    if retained_engine_version is not None and version != retained_engine_version:
        raise Gate('The retained Aurora engine version differs from the continuation proof')
    options = [r for page in pages(rds, 'describe_orderable_db_instance_options', Engine='aurora-postgresql',
               EngineVersion=version, DBInstanceClass='db.serverless') for r in page['OrderableDBInstanceOptions']]
    if not options or not any('DUAL' in r.get('SupportedNetworkTypes', []) for r in options):
        raise Gate('The selected private Aurora serverless version must support dual-stack networking')
    prefix_lists = aws.client('ec2').describe_managed_prefix_lists(Filters=[{
        'Name': 'prefix-list-name', 'Values': ['com.amazonaws.global.cloudfront.origin-facing']}])['PrefixLists']
    if len(prefix_lists) != 1 or not re.fullmatch(r'pl-[0-9a-f]{8,17}', prefix_lists[0]['PrefixListId']):
        raise Gate('The actual regional CloudFront origin-facing prefix list is unavailable')
    return {**c, 'databaseEngineVersion': version, 'cloudFrontPrefixListId': prefix_lists[0]['PrefixListId']}


def archive_source(c, path):
    platform.run(['git', 'archive', '--format=tar', '--output', str(path), c['releaseId']])


def build_command(args, *, cwd=ROOT, input=None, env=None):
    """Keep subprocess progress out of the machine-readable deployment receipt."""
    subprocess.run(args, cwd=cwd, text=True, check=True, input=input,
                   stdout=sys.stderr, stderr=sys.stderr,
                   env=platform.deployment_environment() if env is None else env)


def image(aws, c, registry, context, target, *, binding=None):
    if target not in ('api', 'worker', 'ui') or (target == 'ui' and not re.fullmatch(r'[0-9a-f]{64}', binding or '')):
        raise Gate('A UI image requires the exact exported artifact binding')
    ecr = aws.client('ecr')
    uri, name = registry['RepositoryUri'], registry['RepositoryName']
    tag = target + '-' + c['releaseId']
    if target == 'ui':
        tag += '-' + binding
    try:
        details = ecr.describe_images(repositoryName=name, imageIds=[{'imageTag': tag}])['imageDetails']
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') != 'ImageNotFoundException':
            raise
        command = ['docker', 'buildx', 'build', '--platform', 'linux/amd64', '--provenance=false', '--sbom=false',
                   '--label', 'org.opencontainers.image.revision=' + c['releaseId'],
                   '--file', str(context / 'deploy/fargate.Dockerfile'), '--target', target,
                   '--tag', uri + ':' + tag, '--push']
        if target == 'ui':
            command += ['--label', 'org.opencontainers.image.ui-sha256=' + binding]
        certificate = os.environ.get('CODEX_PROXY_CERT')
        if certificate:
            command += ['--secret', 'id=proxy_ca,src=' + certificate]
        build_command(command + [str(context)])
        details = ecr.describe_images(repositoryName=name, imageIds=[{'imageTag': tag}])['imageDetails']
    if len(details) != 1 or not re.fullmatch(r'sha256:[0-9a-f]{64}', details[0]['imageDigest']):
        raise Gate('ECR did not report one immutable image digest')
    digest = details[0]['imageDigest']
    rows = ecr.batch_get_image(repositoryName=name, imageIds=[{'imageDigest': digest}])
    if rows.get('failures') or len(rows.get('images', [])) != 1:
        raise Gate('ECR cannot prove the immutable image manifest')
    raw = rows['images'][0]['imageManifest']
    manifest = json.loads(raw)
    if (hashlib.sha256(raw.encode()).hexdigest() != digest.split(':')[1]
            or manifest.get('mediaType') not in ('application/vnd.oci.image.manifest.v1+json',
                                               'application/vnd.docker.distribution.manifest.v2+json')
            or 'manifests' in manifest):
        raise Gate('The immutable Fargate image must be a verified single Linux/amd64 manifest')
    immutable = uri + '@' + digest
    build_command(['docker', 'pull', '--platform', 'linux/amd64', immutable])
    actual = json.loads(platform.run(['docker', 'image', 'inspect', immutable], capture=True))[0]
    if (actual.get('Architecture') != 'amd64' or actual.get('Os') != 'linux'
            or actual.get('Config', {}).get('Labels', {}).get('org.opencontainers.image.revision') != c['releaseId']
            or (target == 'ui' and actual.get('Config', {}).get('Labels', {}).get('org.opencontainers.image.ui-sha256') != binding)):
        raise Gate('Actual container platform or source differs from this reviewed release')
    return immutable


def build_images(aws, c, registry, source):
    token = aws.client('ecr').get_authorization_token()['authorizationData'][0]['authorizationToken']
    username, password = base64.b64decode(token).decode().split(':', 1)
    build_command(['docker', 'login', '--username', username, '--password-stdin', registry['RepositoryUri'].split('/')[0]], input=password)
    with tempfile.TemporaryDirectory(prefix='otgd-fargate-build-') as directory:
        context = Path(directory)
        with tarfile.open(source) as archive:
            archive.extractall(context, filter='data')
        api = image(aws, c, registry, context, 'api')
        worker = image(aws, c, registry, context, 'worker')
    return {**c, 'apiImageUri': api, 'workerImageUri': worker, 'uiImageUri': api}


def build_ui(aws, c, registry, out, source, work):
    with tempfile.TemporaryDirectory(prefix='otgd-fargate-ui-') as directory:
        context = Path(directory)
        with tarfile.open(source) as archive:
            archive.extractall(context, filter='data')
        env = web_artifact.build_environment({'environment': 'qa', 'api_url': out['ApiOrigin'],
                                               'issuer': out['Issuer'], 'client_id': out['ClientId']})
        env['EXPO_PUBLIC_SERVERLESS'] = 'true'
        mobile = context / 'apps/mobile'
        build_command(['npm', 'ci'], cwd=mobile, env=env)
        build_command(['npm', 'run', 'export:web'], cwd=mobile, env=env)
        manifest = web_artifact.package(mobile / 'dist', work / 'web.zip')
        files = web_artifact.contents(work / 'web.zip', manifest)
        web = context / 'fargate-web'
        web.mkdir()
        for name, data in files.items():
            path = web / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        binding = hashlib.sha256(json.dumps({name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
                                            sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        ui = image(aws, c, registry, context, 'ui', binding=binding)
    platform.write_receipt(work / 'web-manifest.json', manifest)
    return {**c, 'uiImageUri': ui, 'uiArtifactBinding': binding}, files


def network(out):
    subnets = json.loads(out['TaskSubnets'])
    groups = json.loads(out['TaskSecurityGroups'])
    if (not isinstance(subnets, list) or not 1 <= len(subnets) <= 16 or len(subnets) != len(set(subnets))
            or any(not isinstance(v, str) or not re.fullmatch(r'subnet-[0-9a-f]{8,17}', v) for v in subnets)
            or not isinstance(groups, list) or not 1 <= len(groups) <= 5 or len(groups) != len(set(groups))
            or any(not isinstance(v, str) or not re.fullmatch(r'sg-[0-9a-f]{8,17}', v) for v in groups)):
        raise Gate('Fargate requires bounded distinct actual subnet and security group IDs')
    return {'awsvpcConfiguration': {'subnets': subnets, 'securityGroups': groups, 'assignPublicIp': 'DISABLED'}}


def drain(aws, out):
    ecs = aws.client('ecs')
    ecs.update_service(cluster=out['ClusterArn'], service=out['ApiService'], desiredCount=0)
    deadline = time.monotonic() + 960
    from otgd.serverless_control import ControlStore
    control = ControlStore(client=aws.client('dynamodb'), table_name=out['RuntimeControlTable'])
    while time.monotonic() < deadline:
        services = ecs.describe_services(cluster=out['ClusterArn'], services=[out['ApiService']])
        rows = services.get('services', [])
        tasks = [arn for page in pages(ecs, 'list_tasks', cluster=out['ClusterArn'], desiredStatus='RUNNING')
                 for arn in page.get('taskArns', [])]
        if (not services.get('failures') and len(rows) == 1 and rows[0]['runningCount'] == rows[0]['pendingCount'] == 0
                and not tasks and not control.snapshot().active_leases):
            return {'services_stopped': True, 'producer_leases_drained': True}
        time.sleep(10)
    raise Gate('Owned runtime or producer leases did not drain; preserve stopped services before retry')


def dualstack_image(uri):
    return uri.replace('.dkr.ecr.us-east-2.amazonaws.com/', '.dkr-ecr.us-east-2.on.aws/')


def task_definition(aws, c, arn, expected_images):
    row = aws.client('ecs').describe_task_definition(taskDefinition=arn)['taskDefinition']
    containers = {v['name']: v for v in row['containerDefinitions']}
    if (row.get('networkMode') != 'awsvpc' or row.get('runtimePlatform', {}).get('cpuArchitecture') != 'X86_64'
            or set(containers) != set(expected_images)):
        raise Gate('Actual task definition differs from the reviewed Fargate container inventory')
    for name, expected in expected_images.items():
        env = {v['name']: v['value'] for v in containers[name].get('environment', [])}
        if (containers[name]['image'] != dualstack_image(expected) or containers[name].get('user') != '10001'
                or not containers[name].get('readonlyRootFilesystem')
                or (name != 'ui' and env.get('OTGD_SOURCE_REVISION') != c['releaseId'])):
            raise Gate('Actual task image, source, user or filesystem differs from this release')
    return row


def run_maintenance(aws, c, out, operation, work, *, establish_new=False):
    if operation not in ('bootstrap', 'migrate', 'admission'):
        raise Gate('Unsupported deployment maintenance operation')
    task_definition(aws, c, out['MaintenanceTaskDefinition'], {'maintenance': c['workerImageUri']})
    receipt_key = f"receipts/{c['releaseId']}/{uuid.uuid4()}.json"
    command = ['/usr/local/bin/uv', 'run', '--no-sync', 'python', '-m', 'otgd.fargate_runtime',
               'maintenance', '--operation', operation]
    if establish_new:
        if operation != 'bootstrap':
            raise Gate('Only bootstrap may establish a first empty journal')
        command.append('--establish-new')
    ecs = aws.client('ecs')
    response = ecs.run_task(cluster=out['ClusterArn'], taskDefinition=out['MaintenanceTaskDefinition'],
        launchType='FARGATE', platformVersion='1.4.0', count=1, networkConfiguration=network(out),
        enableExecuteCommand=False, clientToken=str(uuid.uuid4()),
        overrides={'containerOverrides': [{'name': 'maintenance', 'command': command, 'environment': [
            {'name': 'OTGD_FARGATE_RECEIPT_BUCKET', 'value': out['DeploymentBucket']},
            {'name': 'OTGD_FARGATE_RECEIPT_KEY', 'value': receipt_key}]}]})
    if response.get('failures') or len(response.get('tasks', [])) != 1:
        raise Gate('ECS did not accept exactly one reviewed maintenance task')
    arn = response['tasks'][0]['taskArn']
    ecs.get_waiter('tasks_stopped').wait(cluster=out['ClusterArn'], tasks=[arn],
                                       WaiterConfig={'Delay': 10, 'MaxAttempts': 120})
    actual = ecs.describe_tasks(cluster=out['ClusterArn'], tasks=[arn])
    if actual.get('failures') or len(actual.get('tasks', [])) != 1:
        raise Gate('ECS cannot prove the maintenance task state')
    row = actual['tasks'][0]
    containers = row.get('containers', [])
    if (row.get('taskDefinitionArn') != out['MaintenanceTaskDefinition'] or row.get('lastStatus') != 'STOPPED'
            or len(containers) != 1 or containers[0].get('name') != 'maintenance'
            or containers[0].get('exitCode') != 0
            or containers[0].get('imageDigest') != c['workerImageUri'].split('@')[1]):
        raise Gate('Actual maintenance task failed or did not run the reviewed image')
    obj = aws.client('s3').get_object(Bucket=out['DeploymentBucket'], Key=receipt_key)
    stream = obj['Body']
    try:
        raw = stream.read(65537)
    finally:
        stream.close()
    if len(raw) > 65536:
        raise Gate('Maintenance receipt exceeds its bound')
    body = json.loads(raw)
    if (not isinstance(body, dict) or body.get('status') != 'passed' or body.get('operation') != operation
            or body.get('source_revision') != c['releaseId'] or body.get('task_arn') != arn):
        raise Gate('Maintenance receipt does not bind actual task, operation and source completion')
    receipt = {'schema_version': '1.0.0', 'operation': operation, 'status': 'passed', 'task_arn': arn,
               'task_definition_arn': out['MaintenanceTaskDefinition'], 'image_uri': c['workerImageUri'],
               'account': c['account'], 'region': c['region'], 'release_id': c['releaseId'],
               'completed_at': datetime.now(timezone.utc).isoformat(), 'result': body}
    platform.write_receipt(work / ('migration.json' if operation == 'migrate' else operation + '.json'), receipt)
    return receipt


def verify_origin(aws, out):
    cf = aws.client('cloudfront')
    lb = aws.client('elbv2').describe_load_balancers(LoadBalancerArns=[out['LoadBalancerArn']])['LoadBalancers']
    if len(lb) != 1 or lb[0].get('Scheme') != 'internal' or lb[0].get('IpAddressType') != 'dualstack':
        raise Gate('The actual web/API origin must remain an internal dual-stack ALB')
    row = cf.get_vpc_origin(Id=out['VpcOriginId'])['VpcOrigin']
    endpoint = row.get('VpcOriginEndpointConfig', {})
    if row.get('Status') != 'Deployed' or endpoint.get('Arn') != out['LoadBalancerArn']:
        raise Gate('CloudFront did not deploy the exact private ECS origin')
    for key in ('WebDistributionId', 'ApiDistributionId'):
        response = cf.get_distribution_config(Id=out[key])['DistributionConfig']
        origins = response.get('Origins', {}).get('Items', [])
        if (not response.get('Enabled') or len(origins) != 1
                or origins[0].get('DomainName') != lb[0]['DNSName']
                or origins[0].get('VpcOriginConfig', {}).get('VpcOriginId') != out['VpcOriginId']
                or response['DefaultCacheBehavior'].get('ViewerProtocolPolicy') != 'redirect-to-https'):
            raise Gate('The actual distribution differs from the private Fargate origin')


def database_network(aws, out):
    """Require actual private IPv6 database reachability before SQL maintenance."""
    rds = aws.client('rds')
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        rows = rds.describe_db_clusters(DBClusterIdentifier=out['DatabaseClusterIdentifier'])['DBClusters']
        if len(rows) != 1:
            raise Gate('The owned database is missing or ambiguous')
        row = rows[0]
        scaling = row.get('ServerlessV2ScalingConfiguration', {})
        if (row.get('NetworkType') != 'DUAL' or scaling.get('MinCapacity') != 0
                or scaling.get('MaxCapacity') != 1 or scaling.get('SecondsUntilAutoPause') != 300
                or not row.get('StorageEncrypted') or not row.get('DeletionProtection')):
            raise Gate('Actual database networking, capacity or retention differs from the reviewed platform')
        groups = rds.describe_db_subnet_groups(DBSubnetGroupName=row['DBSubnetGroup'])['DBSubnetGroups']
        if len(groups) != 1 or 'DUAL' not in groups[0].get('SupportedNetworkTypes', []):
            raise Gate('Actual private database subnets do not support IPv6')
        try:
            addresses = socket.getaddrinfo(row['Endpoint'], 5432, family=socket.AF_INET6, type=socket.SOCK_STREAM)
        except socket.gaierror:
            addresses = []
        if row.get('Status') == 'available' and addresses:
            return {'private_database_dualstack': True, 'ipv6_dns_verified': True,
                    'database_cluster': out['DatabaseClusterIdentifier']}
        time.sleep(10)
    raise Gate('The private dual-stack database did not become available with IPv6 DNS')


def alarm_and_budget_metadata(aws, c, out):
    inventory = [r for page in pages(aws.client('cloudformation'), 'list_stack_resources', StackName=STACK)
                 for r in page.get('StackResourceSummaries', [])]
    names = [r['PhysicalResourceId'] for r in inventory if r['ResourceType'] == 'AWS::CloudWatch::Alarm']
    if len(names) != 10 or sum(r['ResourceType'] == 'AWS::CloudWatch::Dashboard' for r in inventory) != 1:
        raise Gate('The actual Fargate dashboard and ten-alarm inventory is incomplete')
    cw = aws.client('cloudwatch')
    alarms = cw.describe_alarms(AlarmNames=names)['MetricAlarms']
    if ({a['AlarmName'] for a in alarms} != set(names)
            or any(not a.get('ActionsEnabled') or a.get('AlarmActions') != [out['AlertTopicArn']] for a in alarms)):
        raise Gate('Every actual health alarm must notify the owned alert topic')
    dashboard = json.loads(cw.get_dashboard(DashboardName=out['CloudWatchDashboardName'])['DashboardBody'])
    if not dashboard.get('widgets'):
        raise Gate('The actual CloudWatch dashboard is empty')
    budgets = aws.client('budgets')
    row = budgets.describe_budget(AccountId=c['account'], BudgetName=out['MonthlyBudgetName'])['Budget']
    if (row.get('TimeUnit') != 'MONTHLY' or row.get('BudgetLimit', {}).get('Unit') != 'USD'
            or Decimal(row['BudgetLimit']['Amount']) != Decimal(str(c['monthlyBudgetUsd']))):
        raise Gate('The actual monthly budget differs from the approved amount')
    notifications = [r for page in pages(budgets, 'describe_notifications_for_budget', AccountId=c['account'],
                                        BudgetName=out['MonthlyBudgetName']) for r in page.get('Notifications', [])]
    if len(notifications) != 4:
        raise Gate('Actual budget notifications are incomplete')
    for notification in notifications:
        subscribers = [r for page in pages(budgets, 'describe_subscribers_for_notification', AccountId=c['account'],
                    BudgetName=out['MonthlyBudgetName'], Notification=notification) for r in page.get('Subscribers', [])]
        if subscribers != [{'SubscriptionType': 'EMAIL', 'Address': c['alarmEmail']}]:
            raise Gate('Actual budget alerts differ from the configured email destination')
    subscriptions = [r for page in pages(aws.client('sns'), 'list_subscriptions_by_topic', TopicArn=out['AlertTopicArn'])
                     for r in page.get('Subscriptions', []) if r.get('Protocol') == 'email' and r.get('Endpoint') == c['alarmEmail']]
    if len(subscriptions) != 1:
        raise Gate('The configured alarm email subscription is missing or ambiguous')
    return {'alarm_states': {a['AlarmName']: a['StateValue'] for a in alarms},
            'dashboard_verified': True, 'monthly_budget_usd': c['monthlyBudgetUsd'],
            'budget_email_configured': True,
            'alarm_email_subscription': 'pending_confirmation' if subscriptions[0]['SubscriptionArn'] == 'PendingConfirmation' else 'confirmed',
            'alarm_delivery': 'not_executed'}


def container_logs(aws, out):
    """Prove native Fargate logging using stream metadata and an event count."""
    ecs = aws.client('ecs')
    arns = [arn for page in pages(ecs, 'list_tasks', cluster=out['ClusterArn'],
            serviceName=out['ApiService'].rsplit('/', 1)[-1], desiredStatus='RUNNING') for arn in page['taskArns']]
    if len(arns) != 1:
        raise Gate('Exactly one admitted running task is required to verify logging')
    task_id = arns[0].rsplit('/', 1)[-1]
    if not re.fullmatch(r'[0-9a-f]{32}', task_id):
        raise Gate('The actual ECS task identity is unsupported')
    logs = aws.client('logs')
    for name, key in (('api', 'ApiLogGroup'), ('ui', 'UiLogGroup'), ('controller', 'ControlLogGroup')):
        stream = name + '/' + name + '/' + task_id
        rows = logs.describe_log_streams(logGroupName=out[key], logStreamNamePrefix=stream, limit=2)['logStreams']
        if len(rows) != 1 or rows[0].get('logStreamName') != stream:
            raise Gate('The actual container log stream is missing or ambiguous')
        if name == 'api':
            events = logs.get_log_events(logGroupName=out[key], logStreamName=stream, startFromHead=True, limit=1)['events']
            if not events:
                raise Gate('Actual API log delivery has not been observed')
    return {'ecs_log_streams_verified': True, 'api_log_delivery_verified': True}


def observe(aws, c, out):
    if out.get('ReleaseId') != c['releaseId'] or out.get('ActivateServices') != 'true':
        raise Gate('Health target differs from the admitted active source')
    task_definition(aws, c, out['ApiTaskDefinition'], {'api': out['ApiImageUri'], 'ui': out['UiImageUri'], 'controller': out['WorkerImageUri']})
    task_definition(aws, c, out['WorkerTaskDefinition'], {'worker': out['WorkerImageUri']})
    task_definition(aws, c, out['MaintenanceTaskDefinition'], {'maintenance': out['WorkerImageUri']})
    ecs = aws.client('ecs')
    service = ecs.describe_services(cluster=out['ClusterArn'], services=[out['ApiService']])
    rows = service.get('services', [])
    stable = (not service.get('failures') and len(rows) == 1 and rows[0].get('status') == 'ACTIVE'
              and rows[0].get('desiredCount') == rows[0].get('runningCount') == 1
              and rows[0].get('pendingCount') == 0 and rows[0].get('taskDefinition') == out['ApiTaskDefinition'])
    arns = [arn for page in pages(ecs, 'list_tasks', cluster=out['ClusterArn'],
            serviceName=out['ApiService'].rsplit('/', 1)[-1], desiredStatus='RUNNING') for arn in page['taskArns']]
    tasks = ecs.describe_tasks(cluster=out['ClusterArn'], tasks=arns) if arns else {'tasks': []}
    expected = {'api': out['ApiImageUri'], 'ui': out['UiImageUri'], 'controller': out['WorkerImageUri']}
    actual = tasks.get('tasks', [])
    runtime = (not tasks.get('failures') and len(actual) == 1 and actual[0].get('lastStatus') == 'RUNNING'
               and actual[0].get('taskDefinitionArn') == out['ApiTaskDefinition']
               and actual[0].get('clusterArn') == out['ClusterArn']
               and actual[0].get('healthStatus') == 'HEALTHY'
               and {r['name'] for r in actual[0].get('containers', [])} == set(expected)
               and all(r.get('lastStatus') == 'RUNNING' and r.get('imageDigest') == expected[r['name']].split('@')[1]
                       for r in actual[0].get('containers', [])))
    target = aws.client('elbv2').describe_target_health(TargetGroupArn=out['TargetGroupArn'])['TargetHealthDescriptions']
    ingress = len(target) == 1 and target[0]['TargetHealth']['State'] == 'healthy'
    verify_origin(aws, out)
    health = alarm_and_budget_metadata(aws, c, out)
    database = aws.client('rds').describe_db_clusters(DBClusterIdentifier=out['DatabaseClusterIdentifier'])['DBClusters']
    db = (len(database) == 1 and database[0]['Status'] == 'available' and database[0].get('NetworkType') == 'DUAL')
    with httpx.Client(timeout=120, follow_redirects=False) as http:
        api = http.get(out['ApiOrigin'] + '/health/ready').status_code == 200
        web = http.get(out['WebOrigin'] + '/').status_code == 200
        config = http.get(out['ApiOrigin'] + '/v1/app-config')
        settings = config.json() if config.status_code == 200 else {}
        config_ok = (settings.get('auth', {}).get('issuer') == out['Issuer']
                     and settings.get('auth', {}).get('client_id') == out['ClientId']
                     and settings.get('environment') == 'qa' and settings.get('inference_available') is False)
    healthy = stable and runtime and ingress and db and api and web and config_ok and all(v == 'OK' for v in health['alarm_states'].values())
    return {'status': 'healthy' if healthy else 'degraded', 'observed_at': datetime.now(timezone.utc).isoformat(),
            'account': c['account'], 'region': c['region'], 'release_id': c['releaseId'],
            'ecs_service_stable': stable, 'ecs_containers_running': runtime, 'private_ingress_healthy': ingress,
            'database_available': db, 'api_ready': api, 'web_ready': web, 'app_config_verified': config_ok,
            **health, 'dashboard_url': out['CloudWatchDashboardUrl'], 'backup_restore': 'not_executed'}


def authority_config(c):
    """Use the unchanged legacy authority names without changing Fargate budget."""
    return {**c, 'environment': 'serverless-development', 'monthlyBudgetUsd': 50}


def preserved_private_b(aws, c, continuation=None):
    """Bind literal repair properties to the managed stack and live geometry."""
    from deploy.fargate_template import validate_private_b_resource
    cf = aws.client('cloudformation')
    stacks = cf.describe_stacks(StackName=STACK).get('Stacks', [])
    if len(stacks) != 1:
        raise Gate('PrivateB preservation requires one owned managed stack')
    stack = stacks[0]
    stack_id = stack.get('StackId', '')
    if (not stack_id.startswith(f"arn:aws:cloudformation:{c['region']}:{c['account']}:stack/{STACK}/")
            or stack.get('EnableTerminationProtection') is not True
            or stack.get('StackStatus') not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE', 'IMPORT_COMPLETE')):
        raise Gate('PrivateB preservation requires the exact stable protected stack')
    body = cf.get_template(StackName=stack_id, TemplateStage='Original')['TemplateBody']
    if isinstance(body, str):
        if len(body.encode()) > 1048576:
            raise Gate('PrivateB template exceeded its bound')
        body = strict_loads(body)
    if not isinstance(body, dict) or not isinstance(body.get('Resources'), dict):
        raise Gate('PrivateB preservation requires the current managed template')
    resource = body['Resources'].get('PrivateB')
    expected = continuation.get('repaired_private_b_resource') if continuation is not None else None
    repaired_id = continuation.get('repaired_private_b_physical_id') if continuation is not None else None
    if continuation is not None and bool(expected) != bool(repaired_id):
        raise Gate('Adopted continuation has incomplete PrivateB repair proof')
    if resource is None:
        if expected is not None:
            raise Gate('Adopted continuation lacks its repaired PrivateB')
        return None
    properties = resource.get('Properties', {}) if isinstance(resource, dict) else {}
    if not isinstance(properties, dict):
        raise Gate('PrivateB preservation requires a resource properties object')
    if not isinstance(properties.get('VpcId'), str):
        if expected is not None:
            raise Gate('Adopted continuation lacks literal PrivateB properties')
        return None
    if continuation is not None and expected is None:
        raise Gate('Literal PrivateB is absent from the proved continuation repair')
    # An initial import without PrivateB needs no override. An untagged stack
    # with a repaired subnet is admitted only by the freshly reproved core.
    if stack.get('Tags') or continuation is None:
        _private_subnet_tags(stack.get('Tags', []), stack=True)
    try:
        resource = validate_private_b_resource(resource, c['region'])
    except ValueError as error:
        raise Gate(str(error)) from None
    physical = {}
    for logical, kind in (('Network', 'AWS::EC2::VPC'), ('PrivateA', 'AWS::EC2::Subnet'), ('PrivateB', 'AWS::EC2::Subnet')):
        row = cf.describe_stack_resource(StackName=stack_id, LogicalResourceId=logical)['StackResourceDetail']
        identifier = row.get('PhysicalResourceId')
        pattern = r'vpc-[0-9a-f]{8,17}' if logical == 'Network' else r'subnet-[0-9a-f]{8,17}'
        if (row.get('StackId') != stack_id or row.get('LogicalResourceId') != logical or row.get('ResourceType') != kind
                or row.get('ResourceStatus') not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE', 'IMPORT_COMPLETE')
                or not isinstance(identifier, str) or not re.fullmatch(pattern, identifier)):
            raise Gate('PrivateB preservation found a different managed network binding')
        physical[logical] = identifier
    if continuation is not None:
        if (continuation.get('status') != 'retained-uninitialized-database-adopted'
                or continuation.get('already_adopted') is not True
                or any(continuation.get(key) != c[key] for key in ('account', 'region'))
                or continuation.get('release_id') != c['releaseId'] or continuation.get('stack_id') != stack_id
                or continuation.get('import_template') != body
                or expected != resource or continuation.get('repaired_private_b_physical_id') != physical['PrivateB']
                or any(continuation.get('retained_physical_ids', {}).get(key) != physical[key] for key in ('Network', 'PrivateA'))):
            raise Gate('PrivateB preservation differs from the proved adopted continuation')
    ec2 = aws.client('ec2')
    vpcs = ec2.describe_vpcs(VpcIds=[physical['Network']]).get('Vpcs', [])
    subnets = ec2.describe_subnets(SubnetIds=[physical['PrivateA'], physical['PrivateB']]).get('Subnets', [])
    if len(vpcs) != 1 or len(subnets) != 2 or {row.get('SubnetId') for row in subnets} != {physical['PrivateA'], physical['PrivateB']}:
        raise Gate('PrivateB preservation found an ambiguous live network inventory')
    vpc = vpcs[0]
    if (vpc.get('VpcId') != physical['Network'] or properties['VpcId'] != physical['Network']
            or vpc.get('OwnerId') != c['account'] or vpc.get('State') != 'available'
            or vpc.get('IsDefault') is not False or vpc.get('CidrBlock') != '10.76.0.0/16'):
        raise Gate('PrivateB preservation differs from the owned live VPC')
    _private_subnet_tags(vpc.get('Tags', []))
    associations = vpc.get('Ipv6CidrBlockAssociationSet', [])
    try:
        network = ipaddress.IPv6Network(associations[0]['Ipv6CidrBlock'])
        ranges = list(network.subnets(new_prefix=64)) if network.prefixlen == 56 else []
    except (IndexError, KeyError, TypeError, ValueError):
        raise Gate('PrivateB preservation lacks the reviewed live IPv6 range') from None
    if (len(associations) != 1 or len(ranges) != 256
            or associations[0].get('Ipv6CidrBlockState', {}).get('State') != 'associated'
            or associations[0].get('Ipv6Pool') != 'Amazon' or associations[0].get('NetworkBorderGroup') != c['region']
            or properties['Ipv6CidrBlock'] != str(ranges[1])):
        raise Gate('PrivateB preservation differs from the owned IPv6 geometry')
    zones = []
    for index, logical in enumerate(('PrivateA', 'PrivateB')):
        row = next(row for row in subnets if row['SubnetId'] == physical[logical])
        ipv6 = row.get('Ipv6CidrBlockAssociationSet', [])
        if (row.get('VpcId') != physical['Network'] or row.get('OwnerId') != c['account']
                or row.get('State') != 'available' or row.get('CidrBlock') != f'10.76.{index}.0/24'
                or row.get('MapPublicIpOnLaunch') is not False or row.get('AssignIpv6AddressOnCreation') is not True
                or len(ipv6) != 1 or ipv6[0].get('Ipv6CidrBlock') != str(ranges[index])
                or ipv6[0].get('Ipv6CidrBlockState', {}).get('State') != 'associated'
                or not isinstance(row.get('AvailabilityZone'), str)
                or not re.fullmatch(re.escape(c['region']) + r'[a-z]', row['AvailabilityZone'])
                or (logical == 'PrivateB' and row['AvailabilityZone'] != properties['AvailabilityZone'])):
            raise Gate('PrivateB preservation differs from the live private subnet configuration')
        zones.append(row['AvailabilityZone'])
        _private_subnet_tags(row.get('Tags', []))
    if zones[0] == zones[1]:
        raise Gate('PrivateB preservation requires the two reviewed database zones')
    return deepcopy(resource)


def _private_subnet_tags(rows, *, stack=False):
    from deploy.fargate_template import PRIVATE_SUBNET_TAGS
    expected = {'deployment': STACK, 'purpose': 'serverless-development'} if stack else PRIVATE_SUBNET_TAGS
    if (not isinstance(rows, list) or any(not isinstance(row, dict) or set(row) != {'Key', 'Value'}
            or not isinstance(row['Key'], str) or not isinstance(row['Value'], str) for row in rows)
            or len({row['Key'] for row in rows}) != len(rows)):
        raise Gate('PrivateB preservation requires the exact owned resource tags')
    actual = {row['Key']: row['Value'] for row in rows if not row['Key'].startswith('aws:')}
    allowed = (expected,) if stack else (expected, {**expected, 'purpose': 'serverless-development'})
    if actual not in allowed:
        raise Gate('PrivateB preservation requires the exact owned resource tags')


def verify_adopted_continuation(aws, c, evidence, source_bundle, digest):
    """Reprove the entire adopted graph before using its literal subnet."""
    from deploy.serverless_recovery import uninitialized_continuation_plan
    repair_fields = ('repaired_private_b_resource', 'repaired_private_b_physical_id')
    has_repair = any(evidence.get(key) is not None for key in repair_fields)
    if has_repair and (not all(evidence.get(key) for key in repair_fields)
            or evidence.get('status') != 'retained-uninitialized-database-adopted'
            or evidence.get('already_adopted') is not True
            or any(evidence.get(key) != c[field] for key, field in (
                ('account', 'account'), ('region', 'region'), ('release_id', 'releaseId')))
            or evidence.get('source_bundle_sha256') != digest):
        raise Gate('Adopted continuation lacks the exact completed repair receipt')
    options = {'_repair_evidence': evidence} if has_repair else {}
    current = uninitialized_continuation_plan(aws, authority_config(c), source_bundle, digest, **options)
    fields = ('stack_id', 'retained_physical_ids', 'database_snapshot', 'canonical_import_template_sha256', 'source_bundle_sha256',
              'artifact_sha256', 'failed_run_id', 'failed_run_attempt', 'failed_release_id', 'account', 'region', 'release_id')
    if any(current.get(key) is not None or evidence.get(key) is not None for key in repair_fields):
        fields += repair_fields
    if (current.get('already_adopted') is not True or evidence.get('already_adopted') is not True
            or any(key not in current or key not in evidence or current[key] != evidence[key] for key in fields)
            or bool(current.get(repair_fields[0])) != bool(current.get(repair_fields[1]))):
        raise Gate('Adopted continuation changed before binding the repaired subnet')
    return {'retained_graph_reverified': True, 'repaired_private_b_physical_id': current.get('repaired_private_b_physical_id')}


def _recovery_options(args, operation=None):
    continuing = getattr(args, 'continue_uninitialized', None)
    digest = getattr(args, 'continue_uninitialized_sha256', None)
    recovery = [getattr(args, name, None) for name in (
        'recovery_manifest', 'recovery_archive', 'recovery_run_id', 'recovery_artifact_id')]
    if (bool(continuing) != bool(digest)
            or (continuing and (not args.establish_new or any(recovery)
                or (operation is not None and operation != 'deploy')
                or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)))):
        raise Gate('Uninitialized continuation requires deploy, explicit establishment and the protected bundle/hash only')
    if any(recovery) and (not all(recovery) or not args.establish_new
            or (operation is not None and operation != 'deploy')):
        raise Gate('Trusted initial recovery requires all inputs and explicit first-empty initialization')
    return continuing, digest, recovery


def deploy(args, c, aws, price):
    if not args.gate_evidence:
        raise Gate('Passing exact-source GitHub gate evidence is required')
    platform.require_clean_source(c['releaseId'])
    platform.verify_gate_file(args.gate_evidence, c['releaseId'], required_jobs=FARGATE_REQUIRED_JOBS)
    from deploy.fargate_template import build_template
    continuing, continuation_hash, recovery = _recovery_options(args)
    continuation = None
    if continuing:
        from deploy.serverless_recovery import uninitialized_continuation_plan
        continuation = uninitialized_continuation_plan(aws, authority_config(c), continuing, continuation_hash)
    prior = None if continuing else stable_stack(aws, STACK, absent_ok=True)
    c = preflight(aws, c, prior, continuation['database_engine_version']) if continuation else preflight(aws, c, prior)
    if prior is not None and args.establish_new and not all(recovery):
        raise Gate('An existing deployment cannot establish a new empty deletion journal')
    work = ROOT / '.local/deploy/fargate-development' / c['releaseId'] / uuid.uuid4().hex
    work.mkdir(parents=True, mode=0o700)
    with StageJournal(work, c) as journal:
        private_b = None
        if continuing:
            from deploy.serverless_recovery import continue_uninitialized
            continuation = journal.call('continue-uninitialized-retained-resources', continue_uninitialized,
                aws, authority_config(c), work / 'uninitialized-continuation.json', continuing, continuation_hash)
            journal.call('verify-adopted-continuation-before-render', verify_adopted_continuation,
                aws, c, continuation, continuing, continuation_hash)
        if all(recovery):
            from deploy.serverless_recovery import resume_initial_from_artifact
            journal.call('resume-preserved-initial-import', resume_initial_from_artifact, aws,
                authority_config(c),
                args.recovery_manifest, work / 'initial-resume.json', artifact_proof={
                    'run_id': args.recovery_run_id, 'artifact_id': args.recovery_artifact_id, 'archive_path': args.recovery_archive})
            # Only the helper can admit an already completed, still empty
            # fifteen-resource import. It refuses active or updated platforms.
            prior = stable_stack(aws, STACK)
        if continuation is not None or prior is not None:
            private_b = journal.call('verify-preserved-private-subnet', preserved_private_b, aws, c, continuation)
        registry = journal.call('fargate-registry', deploy_stack, aws, STACK + '-registry', build_template(c, 'registry'), c)
        source = work / 'source.tar'
        journal.call('exact-source-archive', archive_source, c, source)
        c = journal.call('build-reviewed-api-worker-images', build_images, aws, c, registry, source)
        if prior:
            journal.call('drain-existing-runtime', drain, aws, prior)
        out = journal.call('deploy-stopped', deploy_stack, aws, STACK, build_template({**c, 'activateServices': False}, preserved_private_b_resource=private_b), c, registry['DeploymentBucket'])
        if continuation:
            from deploy.serverless_recovery import verify_continued_database
            journal.call('verify-continued-database-stopped', verify_continued_database,
                aws, authority_config(c), out, continuation)
        c, files = journal.call('build-reviewed-ui-image', build_ui, aws, c, registry, out, source, work)
        out = journal.call('bind-stopped-ui-image', deploy_stack, aws, STACK, build_template({**c, 'activateServices': False}, preserved_private_b_resource=private_b), c, registry['DeploymentBucket'])
        if continuation:
            journal.call('verify-continued-database-ui', verify_continued_database,
                aws, authority_config(c), out, continuation)
        journal.call('verify-private-database-network', database_network, aws, out)
        journal.call('bootstrap', run_maintenance, aws, c, out, 'bootstrap', work, establish_new=args.establish_new)
        journal.call('migrate', run_maintenance, aws, c, out, 'migrate', work)
        admission = journal.call('admission', run_maintenance, aws, c, out, 'admission', work)
        journal.call('source-readmission', platform.require_clean_source, c['releaseId'])
        journal.call('gate-readmission', platform.verify_gate_file, args.gate_evidence, c['releaseId'],
            required_jobs=FARGATE_REQUIRED_JOBS)
        if (datetime.now(timezone.utc) - datetime.fromisoformat(admission['completed_at'])).total_seconds() > 900:
            raise Gate('Independent admission is stale before activation')
        out = journal.call('activate-fargate-service', deploy_stack, aws, STACK, build_template({**c, 'activateServices': True}, preserved_private_b_resource=private_b), c, registry['DeploymentBucket'])
        verify_origin(aws, out)
        cf = aws.client('cloudfront')
        for key in ('WebDistributionId', 'ApiDistributionId'):
            invalidation = cf.create_invalidation(DistributionId=out[key], InvalidationBatch={
                'Paths': {'Quantity': 1, 'Items': ['/*']}, 'CallerReference': 'fargate-' + c['releaseId']})['Invalidation']['Id']
            cf.get_waiter('invalidation_completed').wait(DistributionId=out[key], Id=invalidation,
                                                       WaiterConfig={'Delay': 15, 'MaxAttempts': 60})
        public = journal.call('verify-ui-container-bytes-and-headers', web_artifact.verify_access, out, {}, files, timeout=120)
        upload = journal.call('verify-browser-upload-authority', verify_upload_access, aws, c, out)
        deadline = time.monotonic() + 600
        snapshot = None
        while time.monotonic() < deadline:
            snapshot = journal.call('actual-fargate-health', observe, aws, c, out)
            if snapshot['status'] == 'healthy':
                break
            time.sleep(30)
        if not snapshot or snapshot['status'] != 'healthy':
            raise Gate('Actual Fargate health did not stabilize; inspect protected stage evidence')
        snapshot.update(journal.call('verify-actual-container-logging', container_logs, aws, out))
        receipt = {'schema_version': '1.0.0', 'operation': 'fargate-deploy', 'status': 'fargate_transport_and_health_verified',
            'environment': PROFILE, 'account': c['account'], 'region': c['region'], 'release_id': c['releaseId'],
            'web_origin': out['WebOrigin'], 'api_origin': out['ApiOrigin'], 'cloudwatch_dashboard_url': out['CloudWatchDashboardUrl'],
            'images': {k: c[k] for k in ('apiImageUri', 'workerImageUri', 'uiImageUri')},
            'ui_artifact_binding': c['uiArtifactBinding'],
            'public_checks': {**public, **upload}, 'health': snapshot, 'budget_plan': price,
            'production_promotion_eligible': False, 'authenticated_customer_acceptance': 'not_executed',
            'alarm_delivery': 'not_executed', 'backup_restore': 'not_executed'}
        journal.call('write-deployment-receipt', platform.write_receipt, work / 'deployment.json', receipt)
        journal.finish()
        return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('plan', 'deploy', 'health'))
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--profile')
    parser.add_argument('--identity')
    parser.add_argument('--gate-evidence', type=Path)
    parser.add_argument('--establish-new', action='store_true')
    parser.add_argument('--recovery-manifest', type=Path)
    parser.add_argument('--recovery-archive', type=Path)
    parser.add_argument('--recovery-run-id', type=int)
    parser.add_argument('--recovery-artifact-id', type=int)
    parser.add_argument('--continue-uninitialized', type=Path,
                        help='Continue the authenticated stopped deployment before first initialization')
    parser.add_argument('--continue-uninitialized-sha256',
                        help='Independently authenticated SHA-256 of the protected continuation bundle')
    args = parser.parse_args(argv)
    try:
        if args.profile and args.identity:
            raise Gate('Choose one existing AWS profile or configured identity')
        _recovery_options(args, args.operation)
        c = read_config(args.config)
        price = budget(c)
        if args.operation == 'plan':
            result = {'environment': PROFILE, 'account': c['account'], 'region': c['region'],
                'deployment_executed': False, 'budget_plan': price,
                'architecture': 'ECS Fargate UI/API/controller and bounded jobs/maintenance, private Aurora, CloudFront VPC origin and CloudWatch',
                'application_lambda_functions': 0, 'public_ipv4_addresses': 0, 'nat_gateways': 0,
                'database_idle_capacity': 0, 'database_maximum_capacity_acus': 1,
                'credential_route': 'GitHub secrets ACCESS_KEY_ID and SECRET_ACCESS_KEY'}
        else:
            with identity_selection(args.identity) as selected:
                aws = platform.CloudSession(c['region'], selected or args.profile)
                result = deploy(args, c, aws, price) if args.operation == 'deploy' else observe(aws, c, stable_stack(aws, STACK))
        print(json.dumps(result, indent=2))
        return 2 if result.get('status') == 'degraded' else 0
    except Exception as error:
        reason = str(error) if isinstance(error, Gate) else type(error).__name__ + '; inspect protected stage evidence'
        print(json.dumps({'status': 'blocked', 'reason': reason, 'deployment_completed': False,
                          'mutations_may_have_executed': args.operation == 'deploy'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
