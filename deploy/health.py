#!/usr/bin/env python3
"""Read deployed health without changing AWS resources or admitting a release."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:] = [entry for entry in sys.path if Path(entry).resolve() != ROOT / 'deploy']
sys.path.insert(0, str(ROOT))

import argparse
from datetime import datetime, timedelta, timezone
import json
import math

from botocore.config import Config
import httpx

from deploy import platform
from deploy.provenance import Gate

REQUEST_CONFIG = Config(connect_timeout=5, read_timeout=10,
                        retries={'mode': 'standard', 'total_max_attempts': 2})
METRICS = ('OldestOutboxSeconds', 'OldestPrivacyJobSeconds', 'CleanupOverdueCount')


class BoundedSession:
    """Preserve CloudSession endpoint protection and bound every SDK request."""
    def __init__(self, aws):
        self.aws = aws

    def client(self, service, **options):
        options['config'] = options.get('config', Config()).merge(REQUEST_CONFIG)
        return self.aws.client(service, **options)


def pages(client, operation, **options):
    for index, page in enumerate(client.get_paginator(operation).paginate(**options)):
        if index >= 20:
            raise Gate('Health pagination exceeded its supported bound')
        yield page


def service_health(ecs, out, c):
    expected = {out['ApiService']: 'api', out['WorkerService']: 'worker'}
    if len(expected) != 2:
        raise Gate('Stack must identify two distinct ECS services')
    response = ecs.describe_services(cluster=out['Cluster'], services=list(expected))
    services = response.get('services', [])
    if (response.get('failures') or len(services) != 2 or
            {row.get('serviceName') for row in services} != set(expected)):
        raise Gate('AWS did not return both exact ECS services')
    observed = {}
    for row in services:
        name = row['serviceName']
        kind = expected[name]
        counts = [row.get(key) for key in ('desiredCount', 'runningCount', 'pendingCount')]
        if (any(type(value) is not int or value < 0 for value in counts) or
                row.get('clusterArn') != out['Cluster'] or row.get('status') != 'ACTIVE'):
            raise Gate('ECS service identity, status or counts are invalid')
        desired, running, pending = counts
        observed[kind] = {'desired': desired, 'running': running, 'pending': pending,
                          'status': 'healthy', 'tasks': []}
        if desired == 0:
            observed[kind]['status'] = 'stopped' if running == pending == 0 else 'degraded'
            continue
        if running != desired or pending != 0:
            observed[kind]['status'] = 'degraded'
        primary = [item for item in row.get('deployments', []) if item.get('status') == 'PRIMARY']
        if (len(primary) != 1 or primary[0].get('rolloutState') != 'COMPLETED' or
                primary[0].get('taskDefinition') != row.get('taskDefinition')):
            observed[kind]['status'] = 'degraded'
        definition = ecs.describe_task_definition(taskDefinition=row['taskDefinition'])['taskDefinition']
        if definition.get('taskDefinitionArn') != row['taskDefinition']:
            raise Gate('ECS returned a different task definition')
        containers = definition.get('containerDefinitions', [])
        essential = {item['name']: item for item in containers if item.get('essential', True)}
        required = {'api'} if kind == 'api' else {'worker', 'metrics'}
        image = f"{c['account']}.dkr.ecr.{c['region']}.amazonaws.com/otgd-{c['environment']}@{c['imageDigest']}"
        if not required.issubset(essential) or any(item.get('image') != image for item in essential.values()):
            raise Gate('Essential ECS containers differ from the configured release')
        ids = []
        for page in pages(ecs, 'list_tasks', cluster=out['Cluster'], serviceName=name,
                          desiredStatus='RUNNING', PaginationConfig={'PageSize': 100}):
            ids.extend(page.get('taskArns', []))
            if len(ids) > 1000:
                raise Gate('Task count exceeded the supported health bound')
        if len(set(ids)) != len(ids):
            raise Gate('ECS task pagination returned duplicate identities')
        if len(ids) != desired:
            observed[kind]['status'] = 'degraded'
        tasks = []
        for start in range(0, len(ids), 100):
            result = ecs.describe_tasks(cluster=out['Cluster'], tasks=ids[start:start + 100])
            if result.get('failures'):
                raise Gate('An ECS task could not be described')
            tasks.extend(result.get('tasks', []))
        if len(tasks) != len(ids) or {task.get('taskArn') for task in tasks} != set(ids):
            raise Gate('AWS did not return every exact ECS task')
        for task in tasks:
            healthy = (task.get('clusterArn') == out['Cluster'] and
                       task.get('group') == 'service:' + name and
                       task.get('taskDefinitionArn') == row['taskDefinition'] and
                       task.get('lastStatus') == task.get('desiredStatus') == 'RUNNING')
            actual = task.get('containers', [])
            names = [item.get('name') for item in actual]
            if len(set(names)) != len(names) or not set(essential).issubset(names):
                healthy = False
            container_results = {}
            for container in actual:
                container_name = container.get('name')
                if container_name not in essential:
                    continue
                needs_health = 'healthCheck' in essential[container_name] or container_name == 'worker'
                passed = (container.get('lastStatus') == 'RUNNING' and
                          container.get('imageDigest') == c['imageDigest'] and
                          (not needs_health or container.get('healthStatus') == 'HEALTHY'))
                healthy = healthy and passed
                container_results[container_name] = {
                    'status': 'healthy' if passed else 'degraded',
                    'health_check': container.get('healthStatus', 'UNKNOWN') if needs_health else 'not_configured',
                }
            if kind == 'worker' and task.get('healthStatus') != 'HEALTHY':
                healthy = False
            observed[kind]['tasks'].append({'status': 'healthy' if healthy else 'degraded',
                                           'containers': container_results})
            if not healthy:
                observed[kind]['status'] = 'degraded'
    status = 'healthy' if all(row['status'] == 'healthy' for row in observed.values()) else 'degraded'
    if all(row['status'] == 'stopped' for row in observed.values()):
        status = 'stopped'
    return {'status': status, 'services': observed}


def database_health(rds, out):
    result = rds.describe_db_instances(DBInstanceIdentifier=out['DatabaseIdentifier'])
    rows = result.get('DBInstances', [])
    if len(rows) != 1 or rows[0].get('DBInstanceIdentifier') != out['DatabaseIdentifier']:
        raise Gate('AWS did not return the exact deployed database')
    status = rows[0].get('DBInstanceStatus')
    return {'status': 'healthy' if status == 'available' else 'degraded', 'database_state': status}


def alarm_health(cf, cw, c):
    names = []
    for page in pages(cf, 'list_stack_resources', StackName='otgd-' + c['environment'] + '-platform'):
        names.extend(item['PhysicalResourceId'] for item in page.get('StackResourceSummaries', [])
                     if item.get('ResourceType') == 'AWS::CloudWatch::Alarm' and item.get('PhysicalResourceId'))
        if len(names) > 1000:
            raise Gate('Alarm count exceeded the supported health bound')
    if not names or len(set(names)) != len(names):
        raise Gate('The stack does not expose an unambiguous alarm set')
    rows = []
    for start in range(0, len(names), 100):
        for page in pages(cw, 'describe_alarms', AlarmNames=names[start:start + 100],
                          AlarmTypes=['MetricAlarm'], PaginationConfig={'PageSize': 100}):
            rows.extend(page.get('MetricAlarms', []))
    if len(rows) != len(names) or {row.get('AlarmName') for row in rows} != set(names):
        raise Gate('AWS did not return every exact stack alarm')
    states = {row['AlarmName']: row.get('StateValue') for row in rows}
    if any(state not in ('OK', 'ALARM', 'INSUFFICIENT_DATA') for state in states.values()):
        raise Gate('A stack alarm has an unknown state')
    status = 'healthy'
    if 'ALARM' in states.values():
        status = 'degraded'
    elif 'INSUFFICIENT_DATA' in states.values():
        status = 'insufficient_data'
    return {'status': status, 'states': states}


def metrics_health(cw, c, instant):
    queries = [{'Id': 'm' + str(index), 'MetricStat': {
        'Metric': {'Namespace': 'OTGD/' + c['environment'], 'MetricName': name},
        'Period': 60, 'Stat': 'Maximum'}, 'ReturnData': True} for index, name in enumerate(METRICS)]
    result = cw.get_metric_data(MetricDataQueries=queries, StartTime=instant - timedelta(minutes=5),
                               EndTime=instant, ScanBy='TimestampDescending', MaxDatapoints=30)
    rows = result.get('MetricDataResults', [])
    if (result.get('NextToken') or len(rows) != len(METRICS) or
            {row.get('Id') for row in rows} != {'m0', 'm1', 'm2'}):
        raise Gate('AWS did not return all bounded operational metric results')
    samples = {}
    healthy = True
    for row in rows:
        name = METRICS[int(row['Id'][1:])]
        timestamps, values = row.get('Timestamps', []), row.get('Values', [])
        fresh = row.get('StatusCode') == 'Complete' and len(timestamps) == len(values) and bool(values)
        observation = {'status': 'insufficient_data'}
        if fresh:
            index = max(range(len(timestamps)), key=lambda i: timestamps[i])
            point, value = timestamps[index], values[index]
            fresh = (isinstance(point, datetime) and point.tzinfo is not None and
                     -60 <= (instant - point).total_seconds() <= 180 and
                     type(value) in (int, float) and math.isfinite(value) and value >= 0)
            if fresh:
                observation = {'status': 'healthy', 'value': value,
                               'sampled_at': point.astimezone(timezone.utc).isoformat()}
        samples[name] = observation
        healthy = healthy and fresh
    return {'status': 'healthy' if healthy else 'insufficient_data', 'metrics': samples,
            'maximum_sample_age_seconds': 180}


def dashboard_health(cw, out):
    name = out.get('CloudWatchDashboardName')
    url = out.get('CloudWatchDashboardUrl')
    if not name or not url:
        raise Gate('Deployed stack is missing CloudWatch dashboard outputs')
    raw = cw.get_dashboard(DashboardName=name).get('DashboardBody', '')
    if not isinstance(raw, str) or len(raw.encode()) > 1_048_576:
        raise Gate('CloudWatch dashboard body exceeds the supported bound')
    body = json.loads(raw)
    if not isinstance(body, dict) or not isinstance(body.get('widgets'), list) or not body['widgets']:
        raise Gate('CloudWatch dashboard has no health widgets')
    return {'status': 'healthy', 'name': name, 'url': url, 'widget_count': len(body['widgets'])}


def public_health(c, out, client=None):
    origin = 'https://' + c['domain']
    if out.get('ApiOrigin') != origin:
        raise Gate('Public API origin differs from the validated configuration')
    def probe(http):
        with http.stream('GET', origin + '/health/ready', follow_redirects=False, timeout=10) as response:
            raw = bytearray()
            for chunk in response.iter_bytes():
                raw.extend(chunk)
                if len(raw) > 65_536:
                    raise Gate('Public readiness response exceeds the supported bound')
            status = response.status_code
            ready = False
            if status == 200:
                body = json.loads(raw)
                ready = isinstance(body, dict) and body.get('status') == 'ready'
            return {'status': 'healthy' if ready else 'degraded', 'http_status': status}
    if client is not None:
        return probe(client)
    with httpx.Client(timeout=10, follow_redirects=False) as http:
        return probe(http)


def health(c, profile=None, *, skip_public=False, aws=None, instant=None, http_client=None):
    instant = instant or datetime.now(timezone.utc)
    aws = BoundedSession(aws or platform.session(c, profile))
    if aws.client('sts').get_caller_identity().get('Account') != c['account']:
        raise Gate('AWS credential account differs from the deployment configuration')
    out = platform.stack_outputs(aws, c)
    if out.get('ReleaseId') != c['releaseId'] or out.get('ImageDigest') != c['imageDigest']:
        raise Gate('Stable stack outputs differ from the configured release')
    checks = {}
    operations = {
        'services': lambda: service_health(aws.client('ecs'), out, c),
        'database': lambda: database_health(aws.client('rds'), out),
        'alarms': lambda: alarm_health(aws.client('cloudformation'), aws.client('cloudwatch'), c),
        'metrics': lambda: metrics_health(aws.client('cloudwatch'), c, instant),
        'dashboard': lambda: dashboard_health(aws.client('cloudwatch'), out),
    }
    if not skip_public:
        operations['public_api'] = lambda: public_health(c, out, http_client)
    for name, operation in operations.items():
        try:
            checks[name] = operation()
        except Exception as error:
            checks[name] = {'status': 'blocked', 'error_type': type(error).__name__}
    if skip_public:
        checks['public_api'] = {'status': 'not_executed'}
    status = 'healthy' if all(checks[name]['status'] == 'healthy' for name in operations) else 'degraded'
    if checks['services']['status'] == 'stopped':
        status = 'stopped'
    return {'schema_version': '1.0.0', 'operation': 'cloud-health', 'status': status,
            'environment': c['environment'], 'account': c['account'], 'region': c['region'],
            'release_id': c['releaseId'], 'observed_at': instant.isoformat(), 'checks': checks,
            'deployment_executed': False, 'aws_writes_executed': False,
            'qa_acceptance': 'not_executed', 'scope': 'cloud_only' if skip_public else 'cloud_and_public_api'}


def entrypoint(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--profile', help='Normal AWS SDK profile for the target account')
    parser.add_argument('--skip-public', action='store_true', help='Check AWS only; explicitly omit public readiness')
    args = parser.parse_args(argv)
    try:
        report = health(platform.read_config(args.config), args.profile, skip_public=args.skip_public)
    except Exception as error:
        report = {'schema_version': '1.0.0', 'operation': 'cloud-health', 'status': 'blocked',
                  'error_type': type(error).__name__, 'deployment_executed': False,
                  'aws_writes_executed': False, 'qa_acceptance': 'not_executed'}
        if isinstance(error, Gate):
            report['reason'] = str(error)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'healthy' else 2


if __name__ == '__main__':
    raise SystemExit(entrypoint())
