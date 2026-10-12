"""Development budget/account/admission boundaries; no AWS acceptance claims."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from deploy import development
from deploy.provenance import Gate


class DevelopmentCliTest(unittest.TestCase):
    def config(self, root):
        estimate = root / 'estimate.json'
        estimate.write_text(json.dumps({'region': 'us-east-2', 'checked_at': datetime.now(timezone.utc).isoformat(),
            'deployment_profile': 'development-single-node', 'unverified_rates': [],
            'rates': {'fixture': {'usd': .01, 'unit': 'hours', 'source': 'https://pricing.us-east-1.amazonaws.com/fixture',
                                  'sku': 'fixture-only', 'rate_code': 'fixture-only'}},
            'scenarios': [{'monthly_active_users': 10, 'total_monthly_usd': 48.9,
                          'items': [{'quantity': 4890, 'rate': 'fixture', 'monthly_usd': 48.9}]}]}))
        c = {'environment': 'development', 'account': '738470137867', 'region': 'us-east-2',
             'alarmEmail': 'operator@otgd.test', 'monthlyBudgetUsd': 50,
             'releaseId': 'a' * 40, 'plannedMonthlyUsers': 10, 'costEstimatePath': str(estimate)}
        path = root / 'development.json'
        path.write_text(json.dumps(c))
        return c, path, estimate

    def test_plan_verifies_budget_without_aws_access_or_source_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, path, _ = self.config(Path(temporary))
            out = io.StringIO()
            with patch.object(development.platform, 'CloudSession') as aws, patch('sys.stdout', out):
                self.assertEqual(development.main(['plan', '--config', str(path)]), 0)
            aws.assert_not_called()
            result = json.loads(out.getvalue())
            self.assertFalse(result['deployment_executed'])
            self.assertEqual(result['budget_plan']['estimated_monthly_usd'], 48.9)
            self.assertFalse(result['budget_plan']['budget_is_a_spending_cap'])

    def test_above_budget_incomplete_foreign_or_stale_prices_block(self):
        with tempfile.TemporaryDirectory() as temporary:
            c, _, path = self.config(Path(temporary))
            base = json.loads(path.read_text())
            changes = [dict(scenarios=[{'monthly_active_users': 10, 'total_monthly_usd': 50.01}]),
                       dict(region='us-west-2'), dict(unverified_rates=['ec2']), dict(checked_at='2020-01-01')]
            for change in changes:
                with self.subTest(change=change):
                    path.write_text(json.dumps({**base, **change}))
                    with self.assertRaises(Gate):
                        development.budget_plan(c)

    def test_missing_or_failed_exact_source_gates_stop_before_cloud_mutations(self):
        # Import optional generators only after admission, so absence of evidence
        # does not require constructing paid infrastructure at all.
        with tempfile.TemporaryDirectory() as temporary:
            c, _, _ = self.config(Path(temporary))
            args = Mock(gate_evidence=None)
            with patch.object(development.platform, 'require_clean_source') as clean, patch.object(development, 'stack_deploy') as mutate:
                with self.assertRaises(Gate):
                    development.deploy(args, c, Mock(), {})
            clean.assert_not_called()
            mutate.assert_not_called()
            args.gate_evidence = Path('gate-fixture.json')
            with patch.object(development.platform, 'require_clean_source'), patch.object(development.platform, 'verify_gate_file', side_effect=Gate('Failed current CI')), patch.object(development, 'stack_deploy') as mutate:
                with self.assertRaisesRegex(Gate, 'Failed current CI'):
                    development.deploy(args, c, Mock(), {})
            mutate.assert_not_called()

    def test_invalid_target_inputs_do_not_select_another_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            c, path, _ = self.config(Path(temporary))
            for change in ({'environment': 'prod'}, {'region': 'us-west-2'}, {'monthlyBudgetUsd': 130},
                           {'plannedMonthlyUsers': 100}, {'account': 'wrong'}, {'unexpected': 'ignored'}):
                path.write_text(json.dumps({**c, **change}))
                with self.subTest(change=change), self.assertRaises(Gate):
                    development.read_config(path)

    def test_failure_reports_possible_partial_mutations_without_raw_provider_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, path, _ = self.config(Path(temporary))
            err = io.StringIO()
            with patch.object(development.platform, 'CloudSession', side_effect=RuntimeError('secret-provider-output')), patch('sys.stderr', err):
                self.assertEqual(development.main(['deploy', '--config', str(path)]), 2)
            result = json.loads(err.getvalue())
            self.assertTrue(result['mutations_may_have_executed'])
            self.assertFalse(result['deployment_completed'])
            self.assertNotIn('secret-provider-output', err.getvalue())

    def test_replacement_or_removal_of_database_host_and_journal_are_rejected(self):
        for kind, action, replacement in [('AWS::EC2::Instance', 'Modify', 'True'),
                ('AWS::CloudFront::VpcOrigin', 'Modify', 'Conditional'),
                ('AWS::S3::Bucket', 'Remove', 'False'), ('AWS::KMS::Key', 'Modify', 'True')]:
            with self.subTest(kind=kind), self.assertRaises(Gate):
                development.admit_changes([{'ResourceChange': {'ResourceType': kind,
                    'Action': action, 'Replacement': replacement}}])
        development.admit_changes([{'ResourceChange': {'ResourceType': 'AWS::EC2::Instance',
            'Action': 'Add', 'Replacement': 'False'}}])
        development.admit_changes([{'ResourceChange': {'ResourceType': 'AWS::CloudFront::Distribution',
            'Action': 'Modify', 'Replacement': 'False'}}])

    def test_updates_pin_existing_ami_and_never_resolve_latest(self):
        ec2, ssm, aws = Mock(), Mock(), Mock()
        aws.client.side_effect = lambda name: {'ec2': ec2, 'ssm': ssm}[name]
        prior = {'InstanceId': 'i-1234567890abcdef0', 'NatInstanceId': 'i-234567890abcdef01'}
        images = {prior['InstanceId']: ('ami-1234567890abcdef0', 'x86_64'),
                  prior['NatInstanceId']: ('ami-234567890abcdef01', 'arm64')}
        ec2.describe_instances.side_effect = lambda **options: {'Reservations': [{'Instances': [
            {'InstanceId': options['InstanceIds'][0], 'ImageId': images[options['InstanceIds'][0]][0], 'State': {'Name': 'running'}}]}]}
        ec2.describe_images.side_effect = lambda **options: {'Images': [{'ImageId': options['ImageIds'][0],
            'Architecture': next(value[1] for value in images.values() if value[0] == options['ImageIds'][0]),
            'State': 'available', 'RootDeviceType': 'ebs'}]}
        template = {'Resources': {'AppInstance': {'Properties': {}}, 'NatInstance': {'Properties': {}}}}
        development.preserve_images(aws, template, prior)
        ssm.get_parameter.assert_not_called()
        self.assertEqual(template['Resources']['AppInstance']['Properties']['ImageId'], images[prior['InstanceId']][0])
        self.assertEqual(template['Resources']['NatInstance']['Properties']['ImageId'], images[prior['NatInstanceId']][0])

    def test_development_publication_checks_origin_and_writes_entrypoint_last(self):
        c = {'releaseId': 'a' * 40}
        out = {'ReleaseId': c['releaseId'], 'WebReleasePrefix': 'releases/' + c['releaseId'],
               'WebDistributionId': 'D1', 'WebDistributionDomain': 'd1.cloudfront.net', 'WebBucket': 'private-web'}
        cf, s3, aws = Mock(), Mock(), Mock()
        aws.client.side_effect = lambda name: {'cloudfront': cf, 's3': s3}[name]
        distribution = {'Status': 'Deployed', 'DomainName': out['WebDistributionDomain'],
            'DistributionConfig': {'DefaultCacheBehavior': {'TargetOriginId': 'web', 'ViewerProtocolPolicy': 'redirect-to-https'},
                'Origins': {'Items': [{'Id': 'web', 'DomainName': 'private-web.s3.us-east-2.amazonaws.com',
                    'OriginPath': '/' + out['WebReleasePrefix'], 'OriginAccessControlId': 'OAC1'}]}}}
        cf.get_distribution.return_value = {'Distribution': distribution}
        cf.create_invalidation.return_value = {'Invalidation': {'Id': 'I1'}}
        stored, order = {}, []
        def put(**options):
            stored[options['Key']] = options['Body']
            order.append(options['Key'])
            self.assertEqual(options['IfNoneMatch'], '*')
        s3.put_object.side_effect = put
        s3.get_object.side_effect = lambda **options: {'Body': io.BytesIO(stored[options['Key']])}
        result = development.publish_web(aws, c, out, {'files': []}, {'index.html': b'index', 'app.js': b'app'})
        self.assertTrue(order[-1].endswith('/index.html'))
        self.assertFalse(result['production_promotion_eligible'])
        distribution['DistributionConfig']['Origins']['Items'][0]['OriginAccessControlId'] = ''
        s3.put_object.reset_mock()
        with self.assertRaises(Gate):
            development.publish_web(aws, c, out, {'files': []}, {'index.html': b'index'})
        s3.put_object.assert_not_called()


if __name__ == '__main__':
    unittest.main()
