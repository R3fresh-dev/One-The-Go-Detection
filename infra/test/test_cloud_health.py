"""Health observations must fail closed on incomplete AWS responses."""
import copy
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

import httpx

from deploy import health
from deploy.provenance import Gate

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)


def fixture():
    c = {'environment': 'qa', 'account': '123456789012', 'region': 'us-east-2',
         'domain': 'api.qa.otgd.test', 'releaseId': 'a' * 40, 'imageDigest': 'sha256:' + 'b' * 64}
    cluster = 'arn:aws:ecs:us-east-2:123456789012:cluster/otgd-qa'
    out = {'Cluster': cluster, 'ApiService': 'api-service', 'WorkerService': 'worker-service',
           'DatabaseIdentifier': 'database-id', 'ReleaseId': c['releaseId'],
           'ImageDigest': c['imageDigest'], 'ApiOrigin': 'https://' + c['domain'],
           'CloudWatchDashboardName': 'otgd-qa-health',
           'CloudWatchDashboardUrl': 'https://us-east-2.console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=otgd-qa-health'}
    clients = {name: Mock(name=name) for name in ('sts', 'ecs', 'rds', 'cloudformation', 'cloudwatch')}
    clients['sts'].get_caller_identity.return_value = {'Account': c['account']}
    clients['cloudformation'].describe_stacks.return_value = {'Stacks': [{
        'StackStatus': 'UPDATE_COMPLETE',
        'Outputs': [{'OutputKey': key, 'OutputValue': value} for key, value in out.items()]}]}
    services, tasks, definitions = [], {}, {}
    image = f"{c['account']}.dkr.ecr.{c['region']}.amazonaws.com/otgd-qa@{c['imageDigest']}"
    for kind in ('api', 'worker'):
        name = out['ApiService' if kind == 'api' else 'WorkerService']
        arn = f'arn:aws:ecs:us-east-2:123456789012:task-definition/{kind}:1'
        task_id = cluster.replace(':cluster/', ':task/') + '/' + kind
        services.append({'serviceName': name, 'clusterArn': cluster, 'status': 'ACTIVE',
                         'desiredCount': 1, 'runningCount': 1, 'pendingCount': 0,
                         'taskDefinition': arn, 'deployments': [{'status': 'PRIMARY',
                             'rolloutState': 'COMPLETED', 'taskDefinition': arn}]})
        container_names = [kind] + (['metrics'] if kind == 'worker' else [])
        definitions[arn] = {'taskDefinitionArn': arn, 'containerDefinitions': [
            {'name': container, 'image': image, 'essential': True,
             **({'healthCheck': {'command': ['CMD', 'worker-health']}} if container == 'worker' else {})}
            for container in container_names]}
        tasks[name] = [{'taskArn': task_id, 'clusterArn': cluster, 'group': 'service:' + name,
                        'taskDefinitionArn': arn, 'desiredStatus': 'RUNNING', 'lastStatus': 'RUNNING',
                        'healthStatus': 'HEALTHY' if kind == 'worker' else 'UNKNOWN', 'containers': [
                            {'name': container, 'lastStatus': 'RUNNING', 'imageDigest': c['imageDigest'],
                             'healthStatus': 'HEALTHY' if container == 'worker' else 'UNKNOWN'}
                            for container in container_names]}]
    clients['ecs'].describe_services.return_value = {'services': services, 'failures': []}
    clients['ecs'].describe_task_definition.side_effect = lambda **kw: {'taskDefinition': definitions[kw['taskDefinition']]}
    clients['ecs'].get_paginator.return_value.paginate.side_effect = lambda **kw: [
        {'taskArns': [task['taskArn'] for task in tasks[kw['serviceName']]]}]
    clients['ecs'].describe_tasks.side_effect = lambda **kw: {
        'tasks': [task for rows in tasks.values() for task in rows if task['taskArn'] in kw['tasks']]}
    clients['rds'].describe_db_instances.return_value = {'DBInstances': [
        {'DBInstanceIdentifier': out['DatabaseIdentifier'], 'DBInstanceStatus': 'available'}]}
    clients['cloudformation'].get_paginator.return_value.paginate.return_value = [
        {'StackResourceSummaries': [{'ResourceType': 'AWS::CloudWatch::Alarm', 'PhysicalResourceId': 'first-alarm'}]},
        {'StackResourceSummaries': [{'ResourceType': 'AWS::CloudWatch::Alarm', 'PhysicalResourceId': 'second-alarm'}]}]
    clients['cloudwatch'].get_paginator.return_value.paginate.return_value = [
        {'MetricAlarms': [{'AlarmName': 'first-alarm', 'StateValue': 'OK'}]},
        {'MetricAlarms': [{'AlarmName': 'second-alarm', 'StateValue': 'OK'}]}]
    clients['cloudwatch'].get_metric_data.return_value = {'MetricDataResults': [
        {'Id': 'm' + str(i), 'StatusCode': 'Complete', 'Timestamps': [NOW - timedelta(seconds=60)], 'Values': [0.0]}
        for i in range(3)]}
    clients['cloudwatch'].get_dashboard.return_value = {'DashboardBody': json.dumps({'widgets': [{'type': 'metric'}]})}
    aws = Mock()
    aws.client.side_effect = lambda name, **kw: clients[name]
    return c, out, clients, aws, services, tasks, definitions


class CloudHealthTests(unittest.TestCase):
    def test_complete_stack_checks_pass_and_all_aws_methods_are_read_only(self):
        c, out, clients, aws, *_ = fixture()
        report = health.health(c, aws=aws, skip_public=True, instant=NOW)
        self.assertEqual(report['status'], 'healthy')
        self.assertFalse(report['aws_writes_executed'])
        self.assertEqual(report['qa_acceptance'], 'not_executed')
        self.assertEqual(report['checks']['public_api']['status'], 'not_executed')
        self.assertEqual(report['checks']['services']['services']['worker']['tasks'][0]['containers']['metrics']['health_check'], 'not_configured')
        allowed = {'get_caller_identity', 'describe_stacks', 'describe_services', 'describe_task_definition',
                   'describe_tasks', 'describe_db_instances', 'get_dashboard', 'get_metric_data', 'get_paginator'}
        for client in clients.values():
            for call in client.method_calls:
                self.assertIn(call[0].split('.')[0], allowed)
        args = clients['cloudwatch'].get_paginator.return_value.paginate.call_args.kwargs
        self.assertEqual(args['AlarmNames'], ['first-alarm', 'second-alarm'])
        self.assertEqual(args['AlarmTypes'], ['MetricAlarm'])
        for call in aws.client.call_args_list:
            config = call.kwargs['config']
            self.assertEqual(config.connect_timeout, 5)
            self.assertEqual(config.read_timeout, 10)
            self.assertEqual(config.retries['total_max_attempts'], 2)

    def test_wrong_account_or_release_blocks_before_operational_reads(self):
        c, out, clients, aws, *_ = fixture()
        clients['sts'].get_caller_identity.return_value = {'Account': '987654321098'}
        with self.assertRaises(Gate):
            health.health(c, aws=aws, skip_public=True, instant=NOW)
        clients['cloudformation'].describe_stacks.assert_not_called()
        clients['sts'].get_caller_identity.return_value = {'Account': c['account']}
        with self.assertRaises(Gate):
            health.health({**c, 'releaseId': 'd' * 40}, aws=aws, skip_public=True, instant=NOW)
        clients['ecs'].describe_services.assert_not_called()

    def test_missing_duplicate_failed_or_foreign_service_responses_cannot_pass(self):
        for variation in ('missing', 'duplicate', 'failure', 'foreign'):
            with self.subTest(variation=variation):
                c, out, clients, aws, services, *_ = fixture()
                if variation == 'missing':
                    clients['ecs'].describe_services.return_value['services'] = services[:1]
                elif variation == 'duplicate':
                    clients['ecs'].describe_services.return_value['services'] = [services[0], services[0]]
                elif variation == 'failure':
                    clients['ecs'].describe_services.return_value['failures'] = [{'reason': 'MISSING'}]
                else:
                    services[0]['clusterArn'] = 'foreign-cluster'
                report = health.health(c, aws=aws, skip_public=True, instant=NOW)
                self.assertEqual(report['status'], 'degraded')
                self.assertEqual(report['checks']['services']['status'], 'blocked')

    def test_stopped_services_are_explicitly_stopped(self):
        c, out, clients, aws, services, *_ = fixture()
        for service in services:
            service.update(desiredCount=0, runningCount=0, pendingCount=0)
        report = health.health(c, aws=aws, skip_public=True, instant=NOW)
        self.assertEqual(report['status'], 'stopped')
        clients['ecs'].describe_task_definition.assert_not_called()

    def test_stalled_worker_missing_metrics_wrong_digest_and_unstable_rollout_fail(self):
        for variation in ('worker_health', 'missing_metrics', 'digest', 'rollout', 'missing_task'):
            with self.subTest(variation=variation):
                c, out, clients, aws, services, tasks, *_ = fixture()
                worker = tasks[out['WorkerService']][0]
                if variation == 'worker_health':
                    worker['containers'][0]['healthStatus'] = 'UNKNOWN'
                elif variation == 'missing_metrics':
                    worker['containers'].pop()
                elif variation == 'digest':
                    worker['containers'][1]['imageDigest'] = 'sha256:' + 'c' * 64
                elif variation == 'rollout':
                    services[0]['deployments'][0]['rolloutState'] = 'IN_PROGRESS'
                else:
                    clients['ecs'].describe_tasks.side_effect = lambda **kw: {'tasks': []}
                self.assertEqual(health.health(c, aws=aws, skip_public=True, instant=NOW)['status'], 'degraded')

    def test_task_listing_uses_all_pages_and_rejects_missing_or_duplicate_descriptions(self):
        c, out, clients, aws, services, tasks, *_ = fixture()
        api = tasks[out['ApiService']]
        another = copy.deepcopy(api[0])
        another['taskArn'] += '-second'
        api.append(another)
        services[0].update(desiredCount=2, runningCount=2)
        clients['ecs'].get_paginator.return_value.paginate.side_effect = lambda **kw: [
            {'taskArns': [task['taskArn']]} for task in tasks[kw['serviceName']]]
        self.assertEqual(health.health(c, aws=aws, skip_public=True, instant=NOW)['status'], 'healthy')
        clients['ecs'].describe_tasks.side_effect = lambda **kw: {'tasks': [api[0], api[0]]}
        self.assertEqual(health.health(c, aws=aws, skip_public=True, instant=NOW)['status'], 'degraded')

    def test_missing_stale_partial_or_future_metrics_are_insufficient_data(self):
        for variation in ('empty', 'stale', 'partial', 'future', 'missing', 'pagination'):
            with self.subTest(variation=variation):
                c, out, clients, aws, *_ = fixture()
                result = clients['cloudwatch'].get_metric_data.return_value
                row = result['MetricDataResults'][0]
                if variation == 'empty':
                    row.update(Timestamps=[], Values=[])
                elif variation == 'stale':
                    row['Timestamps'] = [NOW - timedelta(seconds=181)]
                elif variation == 'partial':
                    row['StatusCode'] = 'PartialData'
                elif variation == 'future':
                    row['Timestamps'] = [NOW + timedelta(seconds=61)]
                elif variation == 'missing':
                    result['MetricDataResults'].pop()
                else:
                    result['NextToken'] = 'additional-unread-results'
                report = health.health(c, aws=aws, skip_public=True, instant=NOW)
                self.assertEqual(report['status'], 'degraded')
                expected = 'blocked' if variation in ('missing', 'pagination') else 'insufficient_data'
                self.assertEqual(report['checks']['metrics']['status'], expected)

    def test_missing_alarm_alarm_state_and_insufficient_data_cannot_report_healthy(self):
        for state in ('missing', 'ALARM', 'INSUFFICIENT_DATA'):
            with self.subTest(state=state):
                c, out, clients, aws, *_ = fixture()
                pages = clients['cloudwatch'].get_paginator.return_value.paginate.return_value
                if state == 'missing':
                    pages.pop()
                else:
                    pages[0]['MetricAlarms'][0]['StateValue'] = state
                report = health.health(c, aws=aws, skip_public=True, instant=NOW)
                self.assertEqual(report['status'], 'degraded')
                self.assertEqual(report['checks']['alarms']['status'],
                                 'blocked' if state == 'missing' else 'insufficient_data' if state == 'INSUFFICIENT_DATA' else 'degraded')

    def test_database_or_missing_dashboard_is_degraded(self):
        c, out, clients, aws, *_ = fixture()
        clients['rds'].describe_db_instances.return_value['DBInstances'][0]['DBInstanceStatus'] = 'rebooting'
        clients['cloudwatch'].get_dashboard.return_value = {'DashboardBody': '{}'}
        report = health.health(c, aws=aws, skip_public=True, instant=NOW)
        self.assertEqual(report['checks']['database']['status'], 'degraded')
        self.assertEqual(report['checks']['dashboard']['status'], 'blocked')
        self.assertEqual(report['status'], 'degraded')

    def test_public_probe_preserves_tls_origin_and_never_follows_redirects(self):
        c, out, *_ = fixture()
        requests = []
        def respond(request):
            requests.append(str(request.url))
            return httpx.Response(302, headers={'location': 'https://foreign.test/ready'})
        with httpx.Client(transport=httpx.MockTransport(respond)) as client:
            result = health.public_health(c, out, client)
        self.assertEqual(result, {'status': 'degraded', 'http_status': 302})
        self.assertEqual(requests, ['https://' + c['domain'] + '/health/ready'])
        with self.assertRaises(Gate):
            health.public_health(c, {**out, 'ApiOrigin': 'http://localhost:8000'})
        for status, body, expected in [(200, {'status': 'ready'}, 'healthy'),
                                       (200, {'status': 'starting'}, 'degraded'),
                                       (503, {'status': 'ready'}, 'degraded')]:
            with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, json=body))) as client:
                self.assertEqual(health.public_health(c, out, client)['status'], expected)

    def test_sdk_error_messages_and_credentials_never_enter_json_output(self):
        c, out, clients, aws, *_ = fixture()
        clients['rds'].describe_db_instances.side_effect = RuntimeError('private password secret-value')
        report = health.health(c, aws=aws, skip_public=True, instant=NOW)
        self.assertNotIn('secret-value', json.dumps(report))
        self.assertEqual(report['checks']['database'], {'status': 'blocked', 'error_type': 'RuntimeError'})
        with patch.object(health.platform, 'read_config', return_value=c), patch.object(health, 'health', return_value=report), patch('sys.stdout', new_callable=io.StringIO) as stdout:
            self.assertEqual(health.entrypoint(['--config', '/ignored/config.json']), 2)
            self.assertEqual(json.loads(stdout.getvalue())['status'], 'degraded')

    def test_file_entrypoint_help_does_not_require_credentials_or_shadow_platform(self):
        result = subprocess.run([sys.executable, str(ROOT / 'deploy/health.py'), '--help'],
                                cwd=ROOT / 'deploy', capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--config', result.stdout)
        self.assertIn('--skip-public', result.stdout)


if __name__ == '__main__':
    unittest.main()
