#!/usr/bin/env python3
"""Repeatable AWS serverless deployment with exact-source and budget admission."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:] = [p for p in sys.path if Path(p).resolve() != ROOT / 'deploy']
sys.path.insert(0, str(ROOT))

import argparse
import base64
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
import os
import re
import subprocess
import tarfile
import tempfile
import time
from urllib.parse import quote
import uuid

from botocore.config import Config
from botocore.exceptions import ClientError
import httpx
from deploy import platform, web_artifact
from deploy.check_access import identity_selection
from deploy.orchestrate import StageJournal
from deploy.provenance import Gate, bounded_json, sha256

STACK = 'otgd-serverless-development'
FIELDS = {'environment', 'account', 'region', 'alarmEmail', 'monthlyBudgetUsd', 'releaseId',
          'plannedMonthlyUsers', 'costEstimatePath'}


def read_config(path):
    c = bounded_json(path)
    if set(c) != FIELDS or c['environment'] != 'serverless-development':
        raise Gate('Use the explicit serverless development configuration')
    if not re.fullmatch(r'\d{12}', c['account']) or c['region'] != 'us-east-2':
        raise Gate('Supply the actual account and reviewed Ohio region')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', c['alarmEmail']):
        raise Gate('Supply the actual alert destination')
    if not re.fullmatch(r'[0-9a-f]{40}', c['releaseId']):
        raise Gate('Supply the complete reviewed commit')
    if type(c['monthlyBudgetUsd']) not in (int, float) or not 0 < c['monthlyBudgetUsd'] <= 50:
        raise Gate('The selected serverless budget must be positive and at most $50')
    if type(c['plannedMonthlyUsers']) is not int or c['plannedMonthlyUsers'] not in (0, 10):
        raise Gate('Use the reviewed 0 or 10 user planning case')
    return c


def budget(c):
    path = Path(c['costEstimatePath'])
    if not path.is_absolute():
        path = ROOT / path
    evidence = bounded_json(path, 262144)
    if (evidence.get('region') != c['region'] or evidence.get('deployment_profile') != c['environment']
            or evidence.get('unverified_rates') != [] or not evidence.get('rates')):
        raise Gate('Verified matching serverless price evidence is required')
    checked = datetime.fromisoformat(evidence['checked_at'].replace('Z', '+00:00'))
    if checked.tzinfo is None:
        checked = checked.replace(tzinfo=timezone.utc)
    if not -86400 <= (datetime.now(timezone.utc) - checked).total_seconds() <= 31 * 86400:
        raise Gate('Refresh serverless pricing evidence')
    cases = [r for r in evidence['scenarios'] if r['monthly_active_users'] == c['plannedMonthlyUsers']]
    if len(cases) != 1 or not cases[0].get('items'):
        raise Gate('One reconciled serverless workload case is required')
    assumptions = evidence.get('selected_scenario_assumptions', {})
    if (assumptions.get('configured_max_acu') != 1 or assumptions.get('average_active_acu') != 0.5
            or assumptions.get('recurring_privacy_cleanup_interval_seconds') != 900
            or assumptions.get('retained_privacy_cleanup_included') is not True
            or cases[0].get('scheduled_sql_interval_seconds') != 900
            or cases[0].get('active_database_acu_pricing_basis') != 0.5):
        raise Gate('The serverless estimate must include retained privacy cleanup and distinguish average from maximum capacity')
    total = Decimal('0')
    for item in cases[0]['items']:
        rate = evidence['rates'].get(item.get('rate'), {})
        numbers = [item.get('quantity'), item.get('monthly_usd'), rate.get('usd')]
        if (any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in numbers)
                or not all(isinstance(rate.get(k), str) and rate[k] for k in ('unit', 'source', 'sku', 'rate_code'))
                or not rate['source'].startswith('https://pricing.us-east-1.amazonaws.com/')):
            raise Gate('Every price requires finite official rate evidence')
        cost = (Decimal(str(item['quantity'])) * Decimal(str(rate['usd']))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        if cost != Decimal(str(item['monthly_usd'])):
            raise Gate('Serverless line-item arithmetic does not reconcile')
        total += cost
    if total != Decimal(str(cases[0]['total_monthly_usd'])) or total > Decimal(str(c['monthlyBudgetUsd'])):
        raise Gate('The reconciled serverless workload exceeds the selected budget')
    return {'estimated_monthly_usd': float(total), 'budget_usd': c['monthlyBudgetUsd'],
            'planned_monthly_users': c['plannedMonthlyUsers'], 'price_evidence_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'planning_assumptions': assumptions,
            'maximum_capacity_stress_monthly_usd': next(r['total_monthly_usd'] for r in evidence['configured_maximum_1_acu_stress_scenarios']
                if r['monthly_active_users'] == c['plannedMonthlyUsers']),
            'budget_is_a_spending_cap': False}


def pages(client, operation, **options):
    for index, page in enumerate(client.get_paginator(operation).paginate(**options)):
        if index >= 20:
            raise Gate('Cloud pagination exceeded its bound')
        yield page


def stable_stack(aws, name, absent_ok=False):
    cf = aws.client('cloudformation')
    try:
        row = cf.describe_stacks(StackName=name)['Stacks'][0]
    except ClientError as error:
        info = error.response.get('Error', {})
        if absent_ok and info.get('Code') == 'ValidationError' and 'does not exist' in info.get('Message', ''):
            return None
        raise
    status = row['StackStatus']
    if status in ('CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS'):
        cf.get_waiter('stack_create_complete' if status == 'CREATE_IN_PROGRESS' else 'stack_update_complete').wait(
            StackName=name, WaiterConfig={'Delay': 15, 'MaxAttempts': 240})
        row = cf.describe_stacks(StackName=name)['Stacks'][0]
    if row['StackStatus'] not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'):
        raise Gate('Existing stack requires recovery before another deployment')
    return {r['OutputKey']: r['OutputValue'] for r in row.get('Outputs', [])}


def admit_changes(changes):
    protected = {'AWS::RDS::DBCluster', 'AWS::RDS::DBInstance', 'AWS::KMS::Key',
                 'AWS::S3::Bucket', 'AWS::SecretsManager::Secret', 'AWS::Cognito::UserPool', 'AWS::DynamoDB::Table'}
    for entry in changes:
        r = entry.get('ResourceChange', {})
        if r.get('ResourceType') in protected and (r.get('Action') == 'Remove' or r.get('Replacement') in ('True', 'Conditional')):
            raise Gate('This update would replace retained data or authority; use a reviewed recovery process')


def deploy_stack(aws, name, template, c, template_bucket=None):
    cf = aws.client('cloudformation')
    prior = stable_stack(aws, name, absent_ok=True)
    raw = json.dumps(template, separators=(',', ':')).encode()
    request = {'StackName': name, 'ChangeSetName': 'serverless-' + uuid.uuid4().hex,
               'ChangeSetType': 'UPDATE' if prior else 'CREATE', 'Capabilities': ['CAPABILITY_NAMED_IAM'],
               'Tags': [{'Key': 'deployment', 'Value': STACK}, {'Key': 'purpose', 'Value': 'serverless-development'}]}
    if len(raw) <= 51200:
        request['TemplateBody'] = raw.decode()
    else:
        if not template_bucket:
            raise Gate('A private template bucket is required for the complete serverless stack')
        digest = hashlib.sha256(raw).hexdigest()
        key = 'templates/' + c['releaseId'] + '/' + digest + '.json'
        web_artifact.put_immutable(aws.client('s3'), template_bucket, key, raw, 'application/json')
        request['TemplateURL'] = f"https://{template_bucket}.s3.{c['region']}.amazonaws.com/{quote(key)}"
    change = cf.create_change_set(**request)['Id']
    try:
        cf.get_waiter('change_set_create_complete').wait(ChangeSetName=change, StackName=name,
            WaiterConfig={'Delay': 3, 'MaxAttempts': 200})
    except Exception:
        status = cf.describe_change_set(ChangeSetName=change, StackName=name)
        if status.get('Status') == 'FAILED' and "didn't contain changes" in status.get('StatusReason', ''):
            cf.delete_change_set(ChangeSetName=change, StackName=name)
            return stable_stack(aws, name)
        raise
    changes = [entry for page in pages(cf, 'describe_change_set', ChangeSetName=change, StackName=name)
               for entry in page.get('Changes', [])]
    try:
        admit_changes(changes)
    except Gate:
        cf.delete_change_set(ChangeSetName=change, StackName=name)
        raise
    cf.update_termination_protection(StackName=name, EnableTerminationProtection=True)
    cf.execute_change_set(ChangeSetName=change, StackName=name)
    cf.get_waiter('stack_update_complete' if prior else 'stack_create_complete').wait(
        StackName=name, WaiterConfig={'Delay': 15, 'MaxAttempts': 240})
    return stable_stack(aws, name)


def preflight(aws, c, prior):
    if aws.client('sts').get_caller_identity()['Account'] != c['account']:
        raise Gate('AWS credentials do not match the selected account')
    if stable_stack(aws, 'otgd-qa-platform', absent_ok=True):
        raise Gate('Managed QA already uses this account/region authority; select a separate development account')
    functions = aws.client('lambda')
    limits = functions.get_account_settings()['AccountLimit']
    existing = sum(functions.get_function_concurrency(FunctionName=prior[key]).get('ReservedConcurrentExecutions', 0)
                   for key in ('ApiFunction', 'WorkerFunction', 'DispatcherFunction', 'MaintenanceFunction', 'ControlFunction')) if prior else 0
    if (limits.get('ConcurrentExecutions', 0) < 107
            or limits.get('UnreservedConcurrentExecutions', 0) < 100 + max(0, 7 - existing)):
        raise Gate('Lambda needs 7 reserved executions plus the required 100 unreserved; increase the regional concurrency quota before deployment')
    rds = aws.client('rds')
    if prior:
        rows = rds.describe_db_clusters(DBClusterIdentifier=prior['DatabaseClusterIdentifier'])['DBClusters']
        if len(rows) != 1:
            raise Gate('Retained serverless database is unavailable')
        version = rows[0]['EngineVersion']
    else:
        versions = [row for page in pages(rds, 'describe_db_engine_versions', Engine='aurora-postgresql')
                    for row in page['DBEngineVersions'] if row.get('Status') == 'available'
                    and re.fullmatch(r'16\.\d+', row.get('EngineVersion', ''))
                    and row.get('ServerlessV2FeaturesSupport', {}).get('MinCapacity') == 0]
        if not versions:
            raise Gate('Aurora PostgreSQL 16 with zero-capacity auto-pause is unavailable')
        version = max(versions, key=lambda row: int(row['EngineVersion'].split('.')[1]))['EngineVersion']
    orderable = rds.describe_orderable_db_instance_options(Engine='aurora-postgresql',
        EngineVersion=version, DBInstanceClass='db.serverless')['OrderableDBInstanceOptions']
    if not orderable:
        raise Gate('The pinned Aurora version has no serverless capacity in Ohio')
    return {**c, 'databaseEngineVersion': version}


def build_images(aws, c, registry, source):
    ecr = aws.client('ecr')
    uri = registry['RepositoryUri']
    name = uri.rsplit('/', 1)[1]
    auth = ecr.get_authorization_token()['authorizationData'][0]
    username, password = base64.b64decode(auth['authorizationToken']).decode().split(':', 1)
    platform.run(['docker', 'login', '--username', username, '--password-stdin', uri.split('/')[0]], input=password)
    result = {}
    with tempfile.TemporaryDirectory(prefix='otgd-serverless-build-') as directory:
        context = Path(directory)
        with tarfile.open(source) as archive:
            archive.extractall(context, filter='data')
        for target in ('api', 'worker'):
            tag = target + '-' + c['releaseId']
            try:
                details = ecr.describe_images(repositoryName=name, imageIds=[{'imageTag': tag}])['imageDetails']
            except ClientError as error:
                if error.response.get('Error', {}).get('Code') != 'ImageNotFoundException':
                    raise
                command = ['docker', 'buildx', 'build', '--platform', 'linux/amd64', '--provenance=false',
                    '--sbom=false', '--label', 'org.opencontainers.image.revision=' + c['releaseId'],
                    '--file', str(context / 'deploy/serverless.Dockerfile'), '--target', target,
                    '--tag', uri + ':' + tag, '--push']
                cert = os.environ.get('CODEX_PROXY_CERT')
                if cert:
                    command += ['--secret', 'id=proxy_ca,src=' + cert]
                platform.run(command + [str(context)])
                details = ecr.describe_images(repositoryName=name, imageIds=[{'imageTag': tag}])['imageDetails']
            if len(details) != 1 or not re.fullmatch(r'sha256:[0-9a-f]{64}', details[0]['imageDigest']):
                raise Gate('A verified immutable container digest is required')
            digest = details[0]['imageDigest']
            response = ecr.batch_get_image(repositoryName=name, imageIds=[{'imageDigest': digest}])
            images = response.get('images', [])
            if response.get('failures') or len(images) != 1:
                raise Gate('ECR cannot prove the immutable release manifest')
            manifest = json.loads(images[0]['imageManifest'])
            if hashlib.sha256(images[0]['imageManifest'].encode()).hexdigest() != digest.split(':', 1)[1]:
                raise Gate('The retrieved ECR manifest does not match its immutable digest')
            if manifest.get('mediaType') not in ('application/vnd.docker.distribution.manifest.v2+json',
                    'application/vnd.oci.image.manifest.v1+json') or 'manifests' in manifest:
                raise Gate('Lambda requires one Linux/amd64 image manifest')
            immutable = uri + '@' + digest
            platform.run(['docker', 'pull', '--platform', 'linux/amd64', immutable])
            actual = json.loads(platform.run(['docker', 'image', 'inspect', immutable], capture=True))[0]
            if (actual.get('Architecture') != 'amd64' or actual.get('Os') != 'linux'
                    or actual.get('Config', {}).get('Labels', {}).get('org.opencontainers.image.revision') != c['releaseId']):
                raise Gate('Actual Lambda image platform or source label differs from this release')
            result[target + 'ImageUri'] = immutable
    return {**c, **result}


def drain(aws, out):
    """Stop admission and wait for actual producer leases before changing code/schema."""
    client = aws.client('lambda')
    aws.client('events').disable_rule(Name=out['ControlSchedule'])
    client.update_event_source_mapping(UUID=out['WorkerMapping'], Enabled=False, ScalingConfig={})
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        if client.get_event_source_mapping(UUID=out['WorkerMapping'])['State'] == 'Disabled':
            break
        time.sleep(5)
    else:
        raise Gate('The SQS mapping did not stop; no source or schema update is allowed')
    for key in ('ApiFunction', 'WorkerFunction', 'DispatcherFunction', 'ControlFunction'):
        client.put_function_concurrency(FunctionName=out[key], ReservedConcurrentExecutions=0)
    from otgd.serverless_control import ControlStore
    store = ControlStore(client=aws.client('dynamodb'), table_name=out['RuntimeControlTable'])
    deadline = time.monotonic() + 960
    while time.monotonic() < deadline:
        if not store.snapshot().active_leases:
            return {'services_stopped': True, 'producer_leases_drained': True}
        time.sleep(10)
    raise Gate('Actual producer leases remain active; preserve stopped services and inspect before retry')


def invoke_maintenance(aws, c, out, operation, work, **extra):
    name = out['MaintenanceFunction']
    client = aws.client('lambda', config=Config(connect_timeout=5, read_timeout=960,
        retries={'mode': 'standard', 'total_max_attempts': 1}))
    actual = client.get_function(FunctionName=name)
    if actual['Code'].get('ResolvedImageUri') != c['workerImageUri']:
        raise Gate('Maintenance function differs from the actual reviewed worker image')
    event = {'operation': operation, **extra}
    result = client.invoke(FunctionName=name, InvocationType='RequestResponse', Payload=json.dumps(event).encode())
    stream = result['Payload']
    try:
        raw = stream.read(65537)
    finally:
        stream.close()
    if result.get('FunctionError') or result.get('StatusCode') != 200 or len(raw) > 65536:
        raise Gate('Maintenance failed; inspect protected Lambda logs')
    body = json.loads(raw)
    if not isinstance(body, dict) or body.get('status') not in ('passed', 'verified', 'completed', 'admission_verified', 'migrated', 'bootstrap_verified'):
        raise Gate('Maintenance did not return verified completion evidence')
    receipt = {'schema_version': '1.0.0', 'operation': operation, 'status': 'passed',
        'function_arn': actual['Configuration']['FunctionArn'], 'image_uri': c['workerImageUri'],
        'request_id': result['ResponseMetadata']['RequestId'], 'release_id': c['releaseId'],
        'account': c['account'], 'region': c['region'], 'completed_at': datetime.now(timezone.utc).isoformat(),
        'result': body}
    platform.write_receipt(work / (operation + '.json'), receipt)
    return receipt


def build_and_publish_web(aws, c, out, source, work):
    with tempfile.TemporaryDirectory(prefix='otgd-serverless-web-') as temporary:
        context = Path(temporary)
        with tarfile.open(source) as archive:
            archive.extractall(context, filter='data')
        runtime = {'environment': 'qa', 'api_url': out['ApiOrigin'], 'issuer': out['Issuer'], 'client_id': out['ClientId']}
        env = web_artifact.build_environment(runtime)
        env['EXPO_PUBLIC_SERVERLESS'] = 'true'
        mobile = context / 'apps/mobile'
        subprocess.run(['npm', 'ci'], cwd=mobile, env=env, check=True)
        subprocess.run(['npm', 'run', 'export:web', '--', '--clear'], cwd=mobile, env=env, check=True)
        manifest = web_artifact.package(mobile / 'dist', work / 'web.zip')
    files = web_artifact.contents(work / 'web.zip', manifest)
    cf = aws.client('cloudfront')
    prefix = 'releases/' + c['releaseId']
    web_artifact.verify_distribution(aws, out, prefix, c['region'])
    s3 = aws.client('s3')
    for name in sorted(files, key=lambda name: (name == 'index.html', name)):
        record = web_artifact.file_record(name, files[name])
        web_artifact.put_immutable(s3, out['WebBucket'], prefix + '/' + name, files[name], record['content_type'])
    invalidation = cf.create_invalidation(DistributionId=out['WebDistributionId'],
        InvalidationBatch={'Paths': {'Quantity': 1, 'Items': ['/*']}, 'CallerReference': 'serverless-' + sha256(manifest)})['Invalidation']['Id']
    cf.get_waiter('invalidation_completed').wait(DistributionId=out['WebDistributionId'], Id=invalidation,
        WaiterConfig={'Delay': 20, 'MaxAttempts': 45})
    return web_artifact.verify_access(out, {}, files, timeout=120)


def observe(aws, c, out):
    if out.get('ReleaseId') != c['releaseId']:
        raise Gate('Health target differs from the selected source')
    client = aws.client('lambda')
    functions = {}
    for key in ('ApiFunction', 'WorkerFunction', 'DispatcherFunction', 'MaintenanceFunction', 'ControlFunction'):
        row = client.get_function_configuration(FunctionName=out[key])
        expected = out['ApiImageUri'] if key == 'ApiFunction' else out['WorkerImageUri']
        image = client.get_function(FunctionName=out[key])['Code'].get('ResolvedImageUri')
        concurrency = client.get_function_concurrency(FunctionName=out[key]).get('ReservedConcurrentExecutions', 0)
        functions[key] = (row.get('State') == 'Active' and row.get('LastUpdateStatus') == 'Successful'
                          and image == expected and concurrency > 0
                          and row.get('Environment', {}).get('Variables', {}).get('OTGD_SOURCE_REVISION') == c['releaseId'])
    mapping = client.get_event_source_mapping(UUID=out['WorkerMapping'])
    mapping_ok = mapping.get('State') == 'Enabled' and mapping.get('FunctionArn') == out['WorkerFunctionArn']
    schedule = aws.client('events').describe_rule(Name=out['ControlSchedule'])
    schedule_ok = schedule.get('State') == 'ENABLED'
    cw = aws.client('cloudwatch')
    dashboard = cw.get_dashboard(DashboardName=out['CloudWatchDashboardName'])
    if not json.loads(dashboard['DashboardBody']).get('widgets'):
        raise Gate('CloudWatch has no actual serverless dashboard')
    alarm_names = [row['PhysicalResourceId'] for page in pages(aws.client('cloudformation'), 'list_stack_resources', StackName=STACK)
        for row in page.get('StackResourceSummaries', []) if row.get('ResourceType') == 'AWS::CloudWatch::Alarm']
    if not alarm_names or len(alarm_names) > 100:
        raise Gate('The serverless alarm inventory is incomplete')
    alarms = cw.describe_alarms(AlarmNames=alarm_names)['MetricAlarms']
    if {a['AlarmName'] for a in alarms} != set(alarm_names):
        raise Gate('CloudWatch did not report every configured alarm')
    states = {a['AlarmName']: a['StateValue'] for a in alarms}
    database = aws.client('rds').describe_db_clusters(DBClusterIdentifier=out['DatabaseClusterIdentifier'])['DBClusters']
    db_ok = len(database) == 1 and database[0]['Status'] == 'available'
    with httpx.Client(timeout=120, follow_redirects=False) as http:
        api_ok = http.get(out['ApiOrigin'] + '/health/ready').status_code == 200
        web_ok = http.get(out['WebOrigin'] + '/').status_code == 200
    healthy = (all(functions.values()) and mapping_ok and schedule_ok and db_ok and api_ok and web_ok
               and all(v == 'OK' for v in states.values()))
    return {'status': 'healthy' if healthy else 'degraded', 'observed_at': datetime.now(timezone.utc).isoformat(),
        'account': c['account'], 'region': c['region'], 'release_id': c['releaseId'], 'functions': functions,
        'database_available': db_ok, 'api_ready': api_ok, 'web_ready': web_ok, 'alarms': states,
        'worker_mapping_enabled': mapping_ok, 'control_schedule_enabled': schedule_ok,
        'dashboard_url': out['CloudWatchDashboardUrl'], 'alarm_delivery': 'not_executed', 'backup_restore': 'not_executed'}


def deploy(args, c, aws, price):
    if not args.gate_evidence:
        raise Gate('Passing exact-source GitHub gate evidence is required')
    platform.require_clean_source(c['releaseId'])
    platform.verify_gate_file(args.gate_evidence, c['releaseId'])
    from deploy.serverless_template import build_template
    prior = stable_stack(aws, STACK, absent_ok=True)
    c = preflight(aws, c, prior)
    if prior and args.establish_new:
        raise Gate('A retained deployment cannot establish a new empty journal')
    work = ROOT / '.local/deploy/serverless-development' / c['releaseId'] / uuid.uuid4().hex
    work.mkdir(parents=True, mode=0o700)
    with StageJournal(work, c) as journal:
        registry = journal.call('serverless-registry', deploy_stack, aws, STACK + '-registry', build_template(c, phase='registry'), c)
        source = work / 'source.tar'
        journal.call('exact-source-archive', platform.run, ['git', 'archive', '--format=tar', '--output', str(source), c['releaseId']])
        c = journal.call('build-immutable-lambda-images', build_images, aws, c, registry, source)
        platform.write_receipt(work / 'images.json', {'source_revision': c['releaseId'], 'api_image_uri': c['apiImageUri'], 'worker_image_uri': c['workerImageUri']})
        if prior:
            journal.call('drain-existing-runtime', drain, aws, prior)
        out = journal.call('deploy-stopped', deploy_stack, aws, STACK, build_template({**c, 'activateServices': False}), c, registry['DeploymentBucket'])
        journal.call('bootstrap', invoke_maintenance, aws, c, out, 'bootstrap', work, establish_new=args.establish_new)
        journal.call('migrate', invoke_maintenance, aws, c, out, 'migrate', work)
        admission = journal.call('admission', invoke_maintenance, aws, c, out, 'admission', work)
        journal.call('source-readmission', platform.require_clean_source, c['releaseId'])
        journal.call('gate-readmission', platform.verify_gate_file, args.gate_evidence, c['releaseId'])
        if (datetime.now(timezone.utc) - datetime.fromisoformat(admission['completed_at'])).total_seconds() > 900:
            raise Gate('Independent admission is stale before activation')
        out = journal.call('activate', deploy_stack, aws, STACK, build_template({**c, 'activateServices': True}), c, registry['DeploymentBucket'])
        public = journal.call('publish-and-verify-web', build_and_publish_web, aws, c, out, source, work)
        deadline = time.monotonic() + 600
        snapshot = None
        while time.monotonic() < deadline:
            snapshot = journal.call('serverless-health', observe, aws, c, out)
            if snapshot['status'] == 'healthy':
                break
            time.sleep(30)
        if not snapshot or snapshot['status'] != 'healthy':
            raise Gate('Actual serverless health did not stabilize; inspect protected stage evidence')
        receipt = {'schema_version': '1.0.0', 'operation': 'serverless-deploy',
            'status': 'serverless_transport_and_health_verified', 'environment': c['environment'],
            'account': c['account'], 'region': c['region'], 'release_id': c['releaseId'],
            'web_origin': out['WebOrigin'], 'api_origin': out['ApiOrigin'],
            'cloudwatch_dashboard_url': out['CloudWatchDashboardUrl'], 'public_checks': public,
            'health': snapshot, 'budget_plan': price, 'production_promotion_eligible': False,
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
    args = parser.parse_args(argv)
    try:
        if args.profile and args.identity:
            raise Gate('Choose one AWS identity selector')
        c = read_config(args.config)
        price = budget(c)
        if args.operation == 'plan':
            result = {'environment': c['environment'], 'deployment_executed': False,
                'account': c['account'], 'region': c['region'], 'budget_plan': price,
                'architecture': 'Lambda API/workers, Aurora Serverless PostgreSQL, Cognito, SQS, S3/CloudFront, DynamoDB runtime control and CloudWatch',
                'database_idle_capacity': 0, 'database_maximum_capacity_acus': 1,
                'credential_route': 'GitHub repository secrets ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY',
                'remaining_live_checks': ['Exact main CI', 'AWS IPv6 routing and streaming', 'Actual health and alarm delivery', 'Backup restore']}
        else:
            with identity_selection(args.identity) as selected:
                aws = platform.CloudSession(c['region'], selected or args.profile)
                if aws.client('sts').get_caller_identity()['Account'] != c['account']:
                    raise Gate('AWS credentials do not match the selected account')
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
