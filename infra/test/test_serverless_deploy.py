"""Serverless admission and orchestration contracts; no AWS acceptance claims."""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError

from deploy import serverless, serverless_template
from deploy.provenance import Gate
from scripts import serverless_runtime

REVISION = 'a' * 40
URI = '738470137867.dkr.ecr.us-east-2.amazonaws.com/otgd-serverless-development'


def config():
    return {'environment': 'serverless-development', 'account': '738470137867',
            'region': 'us-east-2', 'alarmEmail': 'operator@otgd.test',
            'monthlyBudgetUsd': 50, 'releaseId': REVISION,
            'plannedMonthlyUsers': 10, 'costEstimatePath': 'estimate.json'}


def price_evidence():
    return {'region': 'us-east-2', 'deployment_profile': 'serverless-development',
            'checked_at': datetime.now(timezone.utc).isoformat(), 'unverified_rates': [],
            'selected_scenario_assumptions': {'configured_max_acu': 1, 'average_active_acu': 0.5,
                'recurring_privacy_cleanup_interval_seconds': 900, 'retained_privacy_cleanup_included': True},
            'configured_maximum_1_acu_stress_scenarios': [{'monthly_active_users': 10, 'total_monthly_usd': 40}],
            'rates': {'fixture': {'usd': 2.5, 'unit': 'units', 'sku': 'fictional-unit-test',
                'rate_code': 'fictional-unit-test-rate',
                'source': 'https://pricing.us-east-1.amazonaws.com/unit-test-fixture'}},
            'scenarios': [{'monthly_active_users': 10, 'total_monthly_usd': 25,
                'scheduled_sql_interval_seconds': 900, 'active_database_acu_pricing_basis': 0.5,
                'items': [{'rate': 'fixture', 'quantity': 10, 'monthly_usd': 25}]}]}


class ServerlessAdmissionTest(unittest.TestCase):
    def test_plan_reconciles_evidence_without_selecting_aws_or_building(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'estimate.json').write_text(json.dumps(price_evidence()))
            path = root / 'config.json'
            path.write_text(json.dumps(config()))
            output = io.StringIO()
            with patch.object(serverless, 'ROOT', root), patch.object(serverless.platform, 'CloudSession') as aws, \
                    patch.object(serverless.platform, 'run') as run, patch('sys.stdout', output):
                self.assertEqual(serverless.main(['plan', '--config', str(path)]), 0)
            aws.assert_not_called()
            run.assert_not_called()
            plan = json.loads(output.getvalue())
            self.assertFalse(plan['deployment_executed'])
            self.assertEqual(plan['budget_plan']['estimated_monthly_usd'], 25)
            self.assertFalse(plan['budget_plan']['budget_is_a_spending_cap'])
            self.assertEqual(plan['budget_plan']['planning_assumptions']['configured_max_acu'], 1)
            self.assertEqual(plan['budget_plan']['planning_assumptions']['average_active_acu'], 0.5)
            self.assertEqual(plan['budget_plan']['maximum_capacity_stress_monthly_usd'], 40)

    def test_unsupported_target_or_non_explicit_configuration_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            for change in ({'environment': 'prod'}, {'region': 'us-west-2'}, {'account': 'invalid'},
                           {'releaseId': 'abc'}, {'monthlyBudgetUsd': 50.01}, {'monthlyBudgetUsd': True},
                           {'plannedMonthlyUsers': True}, {'plannedMonthlyUsers': 100},
                           {'alarmEmail': 'invalid'}, {'unexpected': 'ignored'}):
                path.write_text(json.dumps({**config(), **change}))
                with self.subTest(change=change), self.assertRaises(Gate):
                    serverless.read_config(path)

    def test_price_identity_age_arithmetic_and_budget_are_admission_requirements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'estimate.json'
            cases = []
            for key, value in (('region', 'us-west-2'), ('deployment_profile', 'different'),
                               ('unverified_rates', ['missing']),
                               ('checked_at', '2020-01-01T00:00:00Z'),
                               ('checked_at', (datetime.now(timezone.utc) + timedelta(days=2)).isoformat())):
                evidence = price_evidence()
                evidence[key] = value
                cases.append(evidence)
            for field, value in (('quantity', -1), ('monthly_usd', 24.99), ('rate', 'missing')):
                evidence = price_evidence()
                evidence['scenarios'][0]['items'][0][field] = value
                cases.append(evidence)
            for field, value in (('source', 'https://untrusted.invalid/price'), ('sku', ''), ('usd', -1)):
                evidence = price_evidence()
                evidence['rates']['fixture'][field] = value
                cases.append(evidence)
            evidence = price_evidence()
            evidence['scenarios'][0]['total_monthly_usd'] = 25.01
            cases.append(evidence)
            evidence = price_evidence()
            evidence['scenarios'].append(evidence['scenarios'][0])
            cases.append(evidence)
            for field in ('rates', 'scenarios', 'items'):
                evidence = price_evidence()
                if field == 'items':
                    evidence['scenarios'][0]['items'] = []
                else:
                    evidence[field] = {} if field == 'rates' else []
                cases.append(evidence)
            for index, evidence in enumerate(cases):
                path.write_text(json.dumps(evidence))
                with self.subTest(index=index), patch.object(serverless, 'ROOT', root), self.assertRaises(Gate):
                    serverless.budget(config())
            path.write_text(json.dumps(price_evidence()))
            with patch.object(serverless, 'ROOT', root), self.assertRaisesRegex(Gate, 'budget'):
                serverless.budget({**config(), 'monthlyBudgetUsd': 24.99})

    def test_capacity_and_retained_cleanup_assumptions_must_match_selected_scenario(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'estimate.json'
            cases = []
            for key, value in (('configured_max_acu', 0.5), ('average_active_acu', 1),
                               ('recurring_privacy_cleanup_interval_seconds', 3600),
                               ('retained_privacy_cleanup_included', False)):
                evidence = price_evidence()
                evidence['selected_scenario_assumptions'][key] = value
                cases.append(evidence)
            evidence = price_evidence()
            evidence.pop('selected_scenario_assumptions')
            cases.append(evidence)
            for key, value in (('scheduled_sql_interval_seconds', 3600), ('active_database_acu_pricing_basis', 1)):
                evidence = price_evidence()
                evidence['scenarios'][0][key] = value
                cases.append(evidence)
            for index, evidence in enumerate(cases):
                path.write_text(json.dumps(evidence))
                with self.subTest(index=index), patch.object(serverless, 'ROOT', root), self.assertRaisesRegex(Gate, 'retained privacy cleanup'):
                    serverless.budget(config())

    def test_provider_error_output_is_not_disclosed_by_the_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'estimate.json').write_text(json.dumps(price_evidence()))
            path = root / 'config.json'
            path.write_text(json.dumps(config()))
            output = io.StringIO()
            with patch.object(serverless, 'ROOT', root), \
                    patch.object(serverless.platform, 'CloudSession', side_effect=RuntimeError('fictional-sensitive-provider-value')), \
                    patch('sys.stderr', output):
                self.assertEqual(serverless.main(['deploy', '--config', str(path)]), 2)
            result = json.loads(output.getvalue())
            self.assertTrue(result['mutations_may_have_executed'])
            self.assertNotIn('fictional-sensitive-provider-value', output.getvalue())

    def test_missing_or_failed_gate_evidence_precedes_every_aws_operation(self):
        aws = Mock()
        args = SimpleNamespace(gate_evidence=None, establish_new=False)
        with patch.object(serverless.platform, 'require_clean_source') as clean, \
                patch.object(serverless.platform, 'verify_gate_file') as verify:
            with self.assertRaises(Gate):
                serverless.deploy(args, config(), aws, {})
        clean.assert_not_called()
        verify.assert_not_called()
        aws.client.assert_not_called()
        args.gate_evidence = Path('fixture-gates.json')
        with patch.object(serverless.platform, 'require_clean_source'), \
                patch.object(serverless.platform, 'verify_gate_file', side_effect=Gate('Current gates failed')):
            with self.assertRaisesRegex(Gate, 'Current gates failed'):
                serverless.deploy(args, config(), aws, {})
        aws.client.assert_not_called()


class ServerlessCloudFormationTest(unittest.TestCase):
    def test_every_retained_data_or_authority_replacement_is_rejected(self):
        retained = ('AWS::RDS::DBCluster', 'AWS::RDS::DBInstance', 'AWS::KMS::Key',
                    'AWS::S3::Bucket', 'AWS::SecretsManager::Secret',
                    'AWS::Cognito::UserPool', 'AWS::DynamoDB::Table')
        for resource in retained:
            for change in ({'Action': 'Remove'}, {'Action': 'Modify', 'Replacement': 'True'},
                           {'Action': 'Modify', 'Replacement': 'Conditional'}):
                with self.subTest(resource=resource, change=change), self.assertRaises(Gate):
                    serverless.admit_changes([{'ResourceChange': {'ResourceType': resource, **change}}])
            serverless.admit_changes([{'ResourceChange': {'ResourceType': resource,
                                      'Action': 'Modify', 'Replacement': 'False'}}])

    def cloud(self, changes):
        cf = Mock()
        cf.create_change_set.return_value = {'Id': 'change-fixture'}
        cf.get_paginator.return_value.paginate.return_value = [{'Changes': changes}]
        aws = Mock()
        aws.client.return_value = cf
        return aws, cf

    def test_rejected_changes_are_deleted_before_execution_or_protection_updates(self):
        aws, cf = self.cloud([{'ResourceChange': {'ResourceType': 'AWS::S3::Bucket',
                                                'Action': 'Modify', 'Replacement': 'Conditional'}}])
        with patch.object(serverless, 'stable_stack', return_value={'Retained': 'fixture'}):
            with self.assertRaises(Gate):
                serverless.deploy_stack(aws, serverless.STACK, {'Resources': {}}, config())
        cf.delete_change_set.assert_called_once()
        cf.execute_change_set.assert_not_called()
        cf.update_termination_protection.assert_not_called()

    def test_accepted_update_uses_changeset_and_preserves_termination_protection(self):
        aws, cf = self.cloud([{'ResourceChange': {'ResourceType': 'AWS::Lambda::Function',
                                                'Action': 'Modify', 'Replacement': 'False'}}])
        with patch.object(serverless, 'stable_stack', side_effect=[{'Retained': 'fixture'}, {'ReleaseId': REVISION}]):
            self.assertEqual(serverless.deploy_stack(aws, serverless.STACK, {'Resources': {}}, config()),
                             {'ReleaseId': REVISION})
        self.assertEqual(cf.create_change_set.call_args.kwargs['ChangeSetType'], 'UPDATE')
        cf.update_termination_protection.assert_called_once_with(StackName=serverless.STACK,
                                                                EnableTerminationProtection=True)
        cf.execute_change_set.assert_called_once_with(ChangeSetName='change-fixture', StackName=serverless.STACK)

    def test_large_template_requires_private_bucket_before_creating_changeset(self):
        aws, cf = self.cloud([])
        with patch.object(serverless, 'stable_stack', return_value=None):
            with self.assertRaisesRegex(Gate, 'private template bucket'):
                serverless.deploy_stack(aws, serverless.STACK, {'Description': 'x' * 60_000}, config())
        cf.create_change_set.assert_not_called()

    def test_zero_capacity_supported_version_is_selected_before_deployment(self):
        aws = Mock()
        sts, rds, functions = Mock(), Mock(), Mock()
        aws.client.side_effect = lambda name: {'sts': sts, 'rds': rds, 'lambda': functions}[name]
        sts.get_caller_identity.return_value = {'Account': config()['account']}
        functions.get_account_settings.return_value = {'AccountLimit': {
            'ConcurrentExecutions': 107, 'UnreservedConcurrentExecutions': 107}}
        rds.get_paginator.return_value.paginate.return_value = [{'DBEngineVersions': [
            {'Status': 'available', 'EngineVersion': '16.8', 'ServerlessV2FeaturesSupport': {'MinCapacity': 0}},
            {'Status': 'available', 'EngineVersion': '16.11', 'ServerlessV2FeaturesSupport': {'MinCapacity': 0.5}},
            {'Status': 'available', 'EngineVersion': '17.2', 'ServerlessV2FeaturesSupport': {'MinCapacity': 0}},
        ]}]
        rds.describe_orderable_db_instance_options.return_value = {'OrderableDBInstanceOptions': [{}]}
        with patch.object(serverless, 'stable_stack', return_value=None):
            selected = serverless.preflight(aws, config(), None)
        self.assertEqual(selected['databaseEngineVersion'], '16.8')
        rds.describe_orderable_db_instance_options.assert_called_once_with(
            Engine='aurora-postgresql', EngineVersion='16.8', DBInstanceClass='db.serverless')

    def test_insufficient_lambda_quota_blocks_before_database_provisioning(self):
        for limits in ({'ConcurrentExecutions': 100, 'UnreservedConcurrentExecutions': 100},
                       {'ConcurrentExecutions': 1000, 'UnreservedConcurrentExecutions': 106}):
            sts, functions = Mock(), Mock()
            sts.get_caller_identity.return_value = {'Account': config()['account']}
            functions.get_account_settings.return_value = {'AccountLimit': limits}
            aws = Mock()
            aws.client.side_effect = lambda name: {'sts': sts, 'lambda': functions}[name]
            with self.subTest(limits=limits), patch.object(serverless, 'stable_stack', return_value=None):
                with self.assertRaisesRegex(Gate, 'regional concurrency quota'):
                    serverless.preflight(aws, config(), None)


class ServerlessImageTest(unittest.TestCase):
    def source(self, path):
        with tarfile.open(path, 'w') as archive:
            raw = b'FROM fixture\n'
            entry = tarfile.TarInfo('deploy/serverless.Dockerfile')
            entry.size = len(raw)
            archive.addfile(entry, io.BytesIO(raw))

    def cloud(self, *, corrupt_manifest=False):
        manifest = json.dumps({'schemaVersion': 2, 'mediaType': 'application/vnd.oci.image.manifest.v1+json',
                               'config': {'digest': 'sha256:' + 'b' * 64}, 'layers': []})
        digest = 'sha256:' + hashlib.sha256(manifest.encode()).hexdigest()
        ecr = Mock()
        ecr.get_authorization_token.return_value = {'authorizationData': [
            {'authorizationToken': base64.b64encode(b'AWS:fictional-ecr-unit-token').decode()}]}
        ecr.describe_images.return_value = {'imageDetails': [{'imageDigest': digest}]}
        ecr.batch_get_image.return_value = {'images': [{'imageManifest': manifest + (' ' if corrupt_manifest else '')}]}
        aws = Mock()
        aws.client.return_value = ecr
        return aws, ecr, digest

    def test_builds_both_reviewed_linux_images_and_sends_ecr_password_only_to_stdin(self):
        aws, ecr, digest = self.cloud()
        seen = set()
        def describe(**kwargs):
            tag = kwargs['imageIds'][0]['imageTag']
            if tag not in seen:
                seen.add(tag)
                raise ClientError({'Error': {'Code': 'ImageNotFoundException'}}, 'DescribeImages')
            return {'imageDetails': [{'imageDigest': digest}]}
        ecr.describe_images.side_effect = describe
        def run(command, **kwargs):
            if command[:3] == ['docker', 'image', 'inspect']:
                return json.dumps([{'Architecture': 'amd64', 'Os': 'linux',
                    'Config': {'Labels': {'org.opencontainers.image.revision': REVISION}}}])
            return ''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.tar'
            self.source(source)
            with patch.object(serverless.platform, 'run', side_effect=run) as called:
                result = serverless.build_images(aws, config(), {'RepositoryUri': URI}, source)
        self.assertEqual(result['apiImageUri'], URI + '@' + digest)
        self.assertEqual(result['workerImageUri'], URI + '@' + digest)
        login = called.call_args_list[0]
        self.assertIn('--password-stdin', login.args[0])
        self.assertEqual(login.kwargs['input'], 'fictional-ecr-unit-token')
        self.assertNotIn('fictional-ecr-unit-token', ' '.join(login.args[0]))
        builds = [call.args[0] for call in called.call_args_list if call.args[0][:3] == ['docker', 'buildx', 'build']]
        self.assertEqual({command[command.index('--target') + 1] for command in builds}, {'api', 'worker'})
        for command in builds:
            self.assertIn('linux/amd64', command)
            self.assertIn('--provenance=false', command)
            self.assertIn('org.opencontainers.image.revision=' + REVISION, command)
            self.assertIn('--push', command)

    def test_reused_image_still_requires_actual_platform_and_exact_source(self):
        for actual in ({'Architecture': 'arm64', 'Os': 'linux', 'Config': {'Labels': {'org.opencontainers.image.revision': REVISION}}},
                       {'Architecture': 'amd64', 'Os': 'linux', 'Config': {'Labels': {'org.opencontainers.image.revision': 'b' * 40}}}):
            aws, _, _ = self.cloud()
            with self.subTest(actual=actual), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / 'source.tar'
                self.source(source)
                with patch.object(serverless.platform, 'run', side_effect=lambda command, **kwargs:
                                  json.dumps([actual]) if command[:3] == ['docker', 'image', 'inspect'] else ''):
                    with self.assertRaisesRegex(Gate, 'platform or source'):
                        serverless.build_images(aws, config(), {'RepositoryUri': URI}, source)

    def test_manifest_bytes_must_match_the_actual_ecr_digest(self):
        aws, _, _ = self.cloud(corrupt_manifest=True)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.tar'
            self.source(source)
            with patch.object(serverless.platform, 'run') as run:
                with self.assertRaisesRegex(Gate, 'immutable digest'):
                    serverless.build_images(aws, config(), {'RepositoryUri': URI}, source)
        self.assertEqual(run.call_count, 1)


class ServerlessLifecycleTest(unittest.TestCase):
    def run_lifecycle(self, root, *, readmission_failed=False, existing=False):
        c = {**config(), 'apiImageUri': URI + '@sha256:' + 'b' * 64,
             'workerImageUri': URI + '@sha256:' + 'c' * 64}
        out = {'WebOrigin': 'https://web.fixture.test', 'ApiOrigin': 'https://api.fixture.test',
               'CloudWatchDashboardUrl': 'https://dashboard.fixture.test'}
        events = []
        def build_template(current, phase='platform'):
            return {'phase': phase, 'active': current.get('activateServices', False)}
        def stack(aws, name, template, *args):
            events.append('stack-' + ('registry' if template['phase'] == 'registry' else str(template['active'])))
            return {'RepositoryUri': URI, 'DeploymentBucket': 'fixture-private-assets'} if template['phase'] == 'registry' else out
        def maintain(aws, c, out, operation, work, **extra):
            events.append(operation)
            return {'completed_at': datetime.now(timezone.utc).isoformat()}
        verify = Mock(side_effect=[{}, Gate('Readmission failed')] if readmission_failed else [{}, {}])
        with patch.object(serverless, 'ROOT', root), patch.object(serverless.platform, 'require_clean_source'), \
                patch.object(serverless.platform, 'verify_gate_file', verify), \
                patch.object(serverless, 'stable_stack', return_value=out if existing else None), \
                patch.object(serverless, 'preflight', return_value=c), \
                patch.object(serverless_template, 'build_template', side_effect=build_template), \
                patch.object(serverless, 'deploy_stack', side_effect=stack), \
                patch.object(serverless.platform, 'run'), patch.object(serverless, 'build_images', return_value=c), \
                patch.object(serverless, 'drain', side_effect=lambda *args: events.append('drain')), \
                patch.object(serverless, 'invoke_maintenance', side_effect=maintain), \
                patch.object(serverless, 'build_and_publish_web', return_value={'passed': True}), \
                patch.object(serverless, 'observe', return_value={'status': 'healthy'}):
            args = SimpleNamespace(gate_evidence=Path('fixture-gates.json'), establish_new=False)
            if readmission_failed:
                with self.assertRaisesRegex(Gate, 'Readmission failed'):
                    serverless.deploy(args, c, Mock(), {'estimated_monthly_usd': 25})
                receipt = None
            else:
                receipt = serverless.deploy(args, c, Mock(), {'estimated_monthly_usd': 25})
        return receipt, events

    def test_fresh_runtime_bootstraps_and_migrates_stopped_before_activation(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt, events = self.run_lifecycle(Path(directory))
            self.assertEqual(events, ['stack-registry', 'stack-False', 'bootstrap', 'migrate', 'admission', 'stack-True'])
            self.assertEqual(receipt['status'], 'serverless_transport_and_health_verified')
            self.assertFalse(receipt['production_promotion_eligible'])
            self.assertEqual(receipt['backup_restore'], 'not_executed')
            self.assertEqual(receipt['alarm_delivery'], 'not_executed')
            self.assertEqual(len(list(Path(directory).glob('.local/deploy/serverless-development/**/deployment.json'))), 1)

    def test_existing_runtime_drains_before_schema_or_source_update(self):
        with tempfile.TemporaryDirectory() as directory:
            _, events = self.run_lifecycle(Path(directory), existing=True)
        self.assertLess(events.index('drain'), events.index('stack-False'))
        self.assertLess(events.index('stack-False'), events.index('migrate'))

    def test_failed_gate_readmission_preserves_stopped_runtime_and_recovery_journal(self):
        with tempfile.TemporaryDirectory() as directory:
            _, events = self.run_lifecycle(Path(directory), readmission_failed=True)
            self.assertNotIn('stack-True', events)
            states = list(Path(directory).glob('.local/deploy/serverless-development/**/deployment-state.json'))
            self.assertEqual(len(states), 1)
            state = json.loads(states[0].read_text())
            self.assertEqual(state['status'], 'failed')
            self.assertEqual(state['failed_stage'], 'gate-readmission')
            self.assertFalse(state['rollback_executed'])


class ServerlessHealthTest(unittest.TestCase):
    def fixture(self):
        c = config()
        out = {'ReleaseId': REVISION, 'ApiFunction': 'api', 'WorkerFunction': 'worker',
               'DispatcherFunction': 'dispatch', 'MaintenanceFunction': 'maintenance', 'ControlFunction': 'control',
               'ApiImageUri': URI + '@sha256:' + 'b' * 64, 'WorkerImageUri': URI + '@sha256:' + 'c' * 64,
               'WorkerMapping': 'mapping-fixture', 'WorkerFunctionArn': 'arn:fixture:worker',
               'ControlSchedule': 'schedule-fixture', 'DatabaseClusterIdentifier': 'database-fixture',
               'CloudWatchDashboardName': 'dashboard-fixture', 'CloudWatchDashboardUrl': 'https://dashboard.fixture.test',
               'ApiOrigin': 'https://api.fixture.test', 'WebOrigin': 'https://web.fixture.test'}
        clients = {name: Mock() for name in ('lambda', 'events', 'cloudwatch', 'cloudformation', 'rds')}
        functions = clients['lambda']
        functions.get_function_configuration.return_value = {'State': 'Active', 'LastUpdateStatus': 'Successful',
            'Environment': {'Variables': {'OTGD_SOURCE_REVISION': REVISION}}}
        functions.get_function.side_effect = lambda **kw: {'Code': {
            'ResolvedImageUri': out['ApiImageUri'] if kw['FunctionName'] == 'api' else out['WorkerImageUri']}}
        functions.get_function_concurrency.return_value = {'ReservedConcurrentExecutions': 1}
        functions.get_event_source_mapping.return_value = {'State': 'Enabled', 'FunctionArn': out['WorkerFunctionArn']}
        clients['events'].describe_rule.return_value = {'State': 'ENABLED'}
        clients['cloudwatch'].get_dashboard.return_value = {'DashboardBody': json.dumps({'widgets': [{'type': 'text'}]})}
        clients['cloudwatch'].describe_alarms.return_value = {'MetricAlarms': [{'AlarmName': 'alarm-fixture', 'StateValue': 'OK'}]}
        clients['cloudformation'].get_paginator.return_value.paginate.return_value = [{'StackResourceSummaries': [
            {'ResourceType': 'AWS::CloudWatch::Alarm', 'PhysicalResourceId': 'alarm-fixture'}]}]
        clients['rds'].describe_db_clusters.return_value = {'DBClusters': [{'Status': 'available'}]}
        aws = Mock()
        aws.client.side_effect = lambda name: clients[name]
        return c, out, aws, clients

    def observe(self, c, out, aws):
        with patch.object(serverless.httpx, 'Client') as http:
            http.return_value.__enter__.return_value.get.return_value.status_code = 200
            return serverless.observe(aws, c, out)

    def test_health_requires_actual_runtime_invocation_admission(self):
        for failure in ('mapping', 'schedule', 'concurrency', 'image', 'source'):
            c, out, aws, clients = self.fixture()
            if failure == 'mapping':
                clients['lambda'].get_event_source_mapping.return_value['State'] = 'Disabled'
            elif failure == 'schedule':
                clients['events'].describe_rule.return_value['State'] = 'DISABLED'
            elif failure == 'concurrency':
                clients['lambda'].get_function_concurrency.return_value = {'ReservedConcurrentExecutions': 0}
            elif failure == 'image':
                clients['lambda'].get_function.side_effect = lambda **kw: {'Code': {'ResolvedImageUri': 'wrong-image'}}
            else:
                clients['lambda'].get_function_configuration.return_value['Environment']['Variables']['OTGD_SOURCE_REVISION'] = 'b' * 40
            with self.subTest(failure=failure):
                self.assertEqual(self.observe(c, out, aws)['status'], 'degraded')

    def test_empty_dashboard_or_missing_alarm_inventory_cannot_establish_health(self):
        c, out, aws, clients = self.fixture()
        clients['cloudwatch'].get_dashboard.return_value = {'DashboardBody': '{"widgets":[]}'}
        with self.assertRaisesRegex(Gate, 'actual serverless dashboard'):
            self.observe(c, out, aws)
        c, out, aws, clients = self.fixture()
        clients['cloudwatch'].describe_alarms.return_value = {'MetricAlarms': []}
        with self.assertRaisesRegex(Gate, 'every configured alarm'):
            self.observe(c, out, aws)

    def test_positive_health_retains_separate_alarm_delivery_and_restore_limits(self):
        c, out, aws, _ = self.fixture()
        snapshot = self.observe(c, out, aws)
        self.assertEqual(snapshot['status'], 'healthy')
        self.assertTrue(snapshot['worker_mapping_enabled'])
        self.assertTrue(snapshot['control_schedule_enabled'])
        self.assertEqual(snapshot['alarm_delivery'], 'not_executed')
        self.assertEqual(snapshot['backup_restore'], 'not_executed')


class ServerlessRuntimeHttpTest(unittest.TestCase):
    def exchange(self, event, handler):
        captured = {}
        class RuntimeFixture(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Lambda-Runtime-Aws-Request-Id', 'fixture-request')
                self.send_header('Lambda-Runtime-Deadline-Ms', str(int((time.time() + 60) * 1000)))
                self.end_headers()
                self.wfile.write(json.dumps(event).encode())
            def do_POST(self):
                captured['path'] = self.path
                captured['body'] = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.send_response(202)
                self.end_headers()
            def log_message(self, format, *args):
                pass
        with ThreadingHTTPServer(('127.0.0.1', 0), RuntimeFixture) as http:
            thread = threading.Thread(target=http.serve_forever, kwargs={'poll_interval': 0.05}, daemon=True)
            thread.start()
            try:
                serverless_runtime.exchange(f'127.0.0.1:{http.server_port}', handler)
            finally:
                http.shutdown()
                thread.join(timeout=2)
        return captured

    def test_actual_runtime_http_exchange_preserves_partial_sqs_failure_response(self):
        def handler(event, context):
            self.assertEqual(context.aws_request_id, 'fixture-request')
            self.assertGreater(context.get_remaining_time_in_millis(), 0)
            self.assertEqual(event['Records'][0]['messageId'], 'message-fixture')
            return {'batchItemFailures': [{'itemIdentifier': 'message-fixture'}]}
        captured = self.exchange({'Records': [{'messageId': 'message-fixture'}]}, handler)
        self.assertTrue(captured['path'].endswith('/fixture-request/response'))
        self.assertEqual(captured['body'], {'batchItemFailures': [{'itemIdentifier': 'message-fixture'}]})

    def test_runtime_error_sends_type_without_event_or_exception_secret(self):
        def handler(event, context):
            raise ValueError('fictional-sensitive-exception')
        captured = self.exchange({'private': 'fictional-sensitive-event'}, handler)
        self.assertTrue(captured['path'].endswith('/fixture-request/error'))
        self.assertEqual(captured['body']['errorType'], 'ValueError')
        self.assertNotIn('fictional-sensitive', json.dumps(captured['body']))

    def test_runtime_clears_trace_from_previous_invocation_when_header_is_absent(self):
        def handler(event, context):
            self.assertNotIn('_X_AMZN_TRACE_ID', os.environ)
            return {'status': 'passed'}
        with patch.dict(os.environ, {'_X_AMZN_TRACE_ID': 'fictional-prior-trace'}):
            captured = self.exchange({}, handler)
        self.assertTrue(captured['path'].endswith('/fixture-request/response'))

    def test_non_object_runtime_event_is_rejected_before_handler_execution(self):
        handler = Mock()
        captured = self.exchange([], handler)
        handler.assert_not_called()
        self.assertTrue(captured['path'].endswith('/fixture-request/error'))
        self.assertEqual(captured['body']['errorType'], 'ValueError')


if __name__ == '__main__':
    unittest.main()
