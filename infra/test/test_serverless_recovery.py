"""First-stack recovery contracts; these fixtures are not AWS acceptance proof."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from botocore.exceptions import ClientError

from deploy import serverless_recovery as recovery
from deploy.serverless_template import build_template
from deploy.provenance import Gate


ACCOUNT = '738470137867'
REGION = 'us-east-2'
OLD_STACK = f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:stack/{recovery.STACK}/original'
NEW_STACK = f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:stack/{recovery.STACK}/imported'


def absent(code):
    return ClientError({'Error': {'Code': code, 'Message': 'Unit-test resource is absent'}}, 'ReadOnlyUnitTest')


class FakeCloud:
    """A stateful CloudFormation inventory to test ordering and retained IDs."""
    def __init__(self):
        self.config = {'environment': 'serverless-development', 'account': ACCOUNT,
            'region': REGION, 'releaseId': 'a' * 40, 'alarmEmail': 'operator@otgd.test',
            'monthlyBudgetUsd': 50, 'plannedMonthlyUsers': 10, 'costEstimatePath': 'unused'}
        image = f'{ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/{recovery.STACK}@sha256:'
        self.template = build_template({**self.config, 'releaseId': 'b' * 40,
            'apiImageUri': image + 'a' * 64, 'workerImageUri': image + 'b' * 64})
        self.retained = {name: value for name, value in self.template['Resources'].items()
            if value.get('DeletionPolicy') == 'Retain' and name not in ('Artifacts', 'DatabaseWriter')}
        self.physical = {}
        for name, value in self.retained.items():
            props = value['Properties']
            if value['Type'] == 'AWS::S3::Bucket':
                physical = props['BucketName']
            elif value['Type'] == 'AWS::DynamoDB::Table':
                physical = props['TableName']
            elif value['Type'] == 'AWS::Logs::LogGroup':
                physical = props['LogGroupName']
            elif value['Type'] == 'AWS::SecretsManager::Secret':
                physical = f'arn:aws:secretsmanager:{REGION}:{ACCOUNT}:secret:{props["Name"]}-fixture'
            elif value['Type'] == 'AWS::Cognito::UserPool':
                physical = REGION + '_fixture'
            else:
                physical = name + '-key-id'
            self.physical[name] = physical
        self.rows = [{'LogicalResourceId': name, 'ResourceType': value['Type'],
            'ResourceStatus': 'DELETE_SKIPPED' if name in self.retained else 'DELETE_COMPLETE',
            'PhysicalResourceId': self.physical.get(name, name + '-deleted')}
            for name, value in self.template['Resources'].items()]
        self.events = [
            {'LogicalResourceId': recovery.STACK, 'ResourceType': 'AWS::CloudFormation::Stack',
             'PhysicalResourceId': OLD_STACK, 'ResourceStatus': 'ROLLBACK_COMPLETE'},
            {'LogicalResourceId': 'Database', 'ResourceType': 'AWS::RDS::DBCluster',
             'ResourceStatus': 'CREATE_FAILED'},
            {'LogicalResourceId': recovery.STACK, 'ResourceType': 'AWS::CloudFormation::Stack',
             'PhysicalResourceId': OLD_STACK, 'ResourceStatus': 'CREATE_IN_PROGRESS'},
        ]
        self.tags = [{'Key': 'deployment', 'Value': recovery.STACK},
                     {'Key': 'environment', 'Value': 'serverless-development'}]
        self.status = 'ROLLBACK_COMPLETE'
        self.original_deleted = False
        self.import_tags = []
        self.import_resource_status = 'IMPORT_COMPLETE'
        self.protection = True
        self.clients = {name: Mock(name=name) for name in
            ('sts', 'cloudformation', 'rds', 'lambda', 's3', 'dynamodb', 'cognito-idp', 'secretsmanager', 'kms', 'logs')}
        self.aws = SimpleNamespace(client=lambda name: self.clients[name])
        self.clients['sts'].get_caller_identity.return_value = {'Account': ACCOUNT}
        cf = self.clients['cloudformation']
        cf.describe_stacks.side_effect = self.describe_stacks
        cf.get_template.side_effect = lambda **kwargs: {'TemplateBody': deepcopy(
            {'AWSTemplateFormatVersion': '2010-09-09',
             'Description': 'Retained resources from the uninitialized first serverless deployment',
             'Resources': self.retained} if kwargs['StackName'] == NEW_STACK else self.template)}
        cf.get_template_summary.side_effect = self.summary
        cf.get_paginator.side_effect = self.paginator
        cf.get_waiter.side_effect = self.waiter
        cf.create_change_set.return_value = {'Id': 'fixture-import-change'}
        cf.update_termination_protection.side_effect = lambda **kwargs: setattr(self, 'protection', kwargs['EnableTerminationProtection'])
        self.clients['rds'].describe_db_clusters.side_effect = absent('DBClusterNotFoundFault')
        self.clients['rds'].describe_db_instances.side_effect = absent('DBInstanceNotFound')
        self.clients['lambda'].get_function.side_effect = absent('ResourceNotFoundException')
        self.clients['s3'].get_bucket_tagging.return_value = {'TagSet': self.tags}
        self.clients['s3'].list_object_versions.return_value = {'Versions': [], 'DeleteMarkers': [], 'IsTruncated': False}
        self.clients['s3'].list_multipart_uploads.return_value = {'Uploads': [], 'IsTruncated': False}
        dynamo = self.clients['dynamodb']
        dynamo.describe_table.return_value = {'Table': {'TableStatus': 'ACTIVE', 'TableArn': 'fixture-table-arn'}}
        dynamo.list_tags_of_resource.return_value = {'Tags': self.tags}
        dynamo.scan.return_value = {'Count': 0}
        cognito = self.clients['cognito-idp']
        cognito.describe_user_pool.return_value = {'UserPool': {'Name': recovery.STACK,
            'UserPoolTags': {tag['Key']: tag['Value'] for tag in self.tags}}}
        cognito.list_users.return_value = {'Users': []}
        secret = self.clients['secretsmanager']
        secret.describe_secret.side_effect = lambda **kwargs: {'Name': next(
            self.retained[name]['Properties']['Name'] for name, physical in self.physical.items()
            if physical == kwargs['SecretId']), 'ARN': kwargs['SecretId'], 'Tags': self.tags}
        kms = self.clients['kms']
        kms.describe_key.side_effect = lambda **kwargs: {'KeyMetadata': {'KeyId': kwargs['KeyId'],
            'AWSAccountId': ACCOUNT, 'Description': next(self.retained[name]['Properties']['Description']
                for name, physical in self.physical.items() if physical == kwargs['KeyId']), 'KeyState': 'Enabled'}}
        kms.list_resource_tags.return_value = {'Tags': [{'TagKey': tag['Key'], 'TagValue': tag['Value']} for tag in self.tags]}
        logs = self.clients['logs']
        logs.describe_log_groups.side_effect = lambda **kwargs: {'logGroups': [{
            'logGroupName': kwargs['logGroupNamePrefix'], 'arn': 'arn:fixture:logs:' + kwargs['logGroupNamePrefix'] + ':*'}]}
        logs.list_tags_for_resource.return_value = {'tags': {tag['Key']: tag['Value'] for tag in self.tags}}

    def describe_stacks(self, **kwargs):
        archived = kwargs['StackName'] == OLD_STACK
        if not archived and self.status == 'ABSENT':
            raise ClientError({'Error': {'Code': 'ValidationError',
                'Message': f'Stack with id {recovery.STACK} does not exist'}}, 'DescribeStacks')
        return {'Stacks': [{'StackId': OLD_STACK if archived or not self.original_deleted else NEW_STACK,
            'StackStatus': 'DELETE_COMPLETE' if archived and self.original_deleted else self.status,
            'EnableTerminationProtection': self.protection,
            'Tags': [{'Key': 'deployment', 'Value': recovery.STACK},
                     {'Key': 'purpose', 'Value': 'serverless-development'}]
                    if archived or not self.original_deleted else self.import_tags}]}

    def summary(self, **kwargs):
        resources = json.loads(kwargs['TemplateBody'])['Resources']
        keys = {'AWS::KMS::Key': 'KeyId', 'AWS::SecretsManager::Secret': 'Id',
                'AWS::S3::Bucket': 'BucketName', 'AWS::DynamoDB::Table': 'TableName',
                'AWS::Cognito::UserPool': 'UserPoolId', 'AWS::Logs::LogGroup': 'LogGroupName'}
        return {'ResourceIdentifierSummaries': [{'ResourceType': value['Type'],
            'LogicalResourceIds': [name], 'ResourceIdentifiers': [keys[value['Type']]]}
            for name, value in resources.items()]}

    def paginator(self, operation):
        if operation == 'describe_stack_events':
            return SimpleNamespace(paginate=lambda **kwargs: [{'StackEvents': self.events}])
        if operation == 'list_stack_resources':
            def paginate(**kwargs):
                if kwargs['StackName'] == NEW_STACK:
                    rows = [{**row, 'ResourceStatus': self.import_resource_status} for row in self.rows
                            if row['LogicalResourceId'] in self.retained]
                else:
                    rows = self.rows
                return [{'StackResourceSummaries': rows}]
            return SimpleNamespace(paginate=paginate)
        if operation == 'describe_change_set':
            return SimpleNamespace(paginate=lambda **kwargs: [{'Changes': [{'ResourceChange': {
                'Action': 'Import', 'LogicalResourceId': name, 'ResourceType': value['Type']}}
                for name, value in self.retained.items()]}])
        raise AssertionError(operation)

    def waiter(self, name):
        def wait(**kwargs):
            if name == 'stack_delete_complete':
                self.original_deleted = True
                self.status = 'ABSENT'
            elif name == 'stack_import_complete':
                self.status = 'IMPORT_COMPLETE'
        return SimpleNamespace(wait=wait)

    def no_mutations(self, test):
        cf = self.clients['cloudformation']
        for operation in ('update_termination_protection', 'delete_stack', 'create_change_set', 'execute_change_set'):
            getattr(cf, operation).assert_not_called()
        for client in self.clients.values():
            for forbidden in ('get_secret_value', 'delete_bucket', 'delete_user_pool', 'delete_table',
                              'delete_secret', 'schedule_key_deletion', 'delete_log_group', 'get_object',
                              'create_key', 'create_secret', 'create_bucket', 'create_table', 'create_user_pool'):
                getattr(client, forbidden).assert_not_called()

    def detached_manifest(self, directory):
        source = recovery.initial_recovery_plan(self.aws, self.config)
        source.update(status='blocked-recovery-inspect-protected-journal-before-retry',
                      failed_phase='failed-stack-metadata-detached', failure_type='ClientError')
        self.original_deleted = True
        self.status = 'ABSENT'
        self.events.insert(0, {'LogicalResourceId': recovery.STACK,
            'ResourceType': 'AWS::CloudFormation::Stack', 'PhysicalResourceId': OLD_STACK,
            'ResourceStatus': 'DELETE_COMPLETE'})
        path = Path(directory) / 'source.json'
        recovery._write(path, source)
        self.config['releaseId'] = 'c' * 40
        return path, source


class InitialRecoveryTest(unittest.TestCase):
    def test_read_only_plan_has_closed_original_properties_and_real_identifier_summary(self):
        cloud = FakeCloud()
        result = recovery.initial_recovery_plan(cloud.aws, cloud.config)
        self.assertEqual(result['original_release_id'], 'b' * 40)
        self.assertEqual(result['retained_physical_ids'], cloud.physical)
        self.assertEqual(result['import_template']['Resources'], cloud.retained)
        self.assertNotIn('Outputs', result['import_template'])
        self.assertEqual({item['LogicalResourceId'] for item in result['resources_to_import']}, cloud.retained.keys())
        cloud.no_mutations(self)

    def test_success_preserves_every_physical_identity_and_writes_journal_before_stack_deletion(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-recovery.json'
            def deletion(**kwargs):
                evidence = json.loads(path.read_text())
                self.assertEqual(evidence['retained_physical_ids'], cloud.physical)
                self.assertEqual(evidence['status'], 'detaching-failed-stack-metadata')
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(kwargs['StackName'], OLD_STACK)
            cloud.clients['cloudformation'].delete_stack.side_effect = deletion
            result = recovery.recover_initial(cloud.aws, cloud.config, path)
            self.assertEqual(result['status'], 'uninitialized-retained-resources-imported')
            self.assertEqual(json.loads(path.read_text()), result)
            self.assertFalse(result['actual_resources_deleted'])
            self.assertFalse(result['application_deployment_completed'])
        cf = cloud.clients['cloudformation']
        call = cf.create_change_set.call_args.kwargs
        self.assertEqual(call['ChangeSetType'], 'IMPORT')
        self.assertNotIn('Tags', call)
        self.assertEqual(json.loads(call['TemplateBody'])['Resources'], cloud.retained)
        self.assertEqual(call['ResourcesToImport'], result['resources_to_import'])
        self.assertEqual(cf.execute_change_set.call_count, 1)
        self.assertTrue(cloud.protection)
        self.assertEqual(cloud.clients['s3'].list_object_versions.call_count,
                         3 * sum(value['Type'] == 'AWS::S3::Bucket' for value in cloud.retained.values()))
        for client in cloud.clients.values():
            for forbidden in ('delete_bucket', 'delete_secret', 'delete_user_pool', 'delete_table',
                              'schedule_key_deletion', 'get_secret_value', 'get_object'):
                getattr(client, forbidden).assert_not_called()

    def test_wrong_account_region_or_stack_state_block_all_mutations(self):
        for kind in ('account', 'region', 'stable', 'ongoing'):
            cloud = FakeCloud()
            if kind == 'account':
                cloud.clients['sts'].get_caller_identity.return_value = {'Account': '111111111111'}
            elif kind == 'region':
                cloud.config['region'] = 'us-west-2'
            elif kind == 'stable':
                cloud.status = 'UPDATE_ROLLBACK_COMPLETE'
            else:
                cloud.status = 'ROLLBACK_IN_PROGRESS'
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_database_function_created_or_actual_runtime_present_blocks(self):
        for kind in ('database-event', 'function-event', 'database-live', 'function-live'):
            cloud = FakeCloud()
            if kind.endswith('event'):
                logical = 'Database' if kind.startswith('database') else 'ApiFunction'
                next(row for row in cloud.rows if row['LogicalResourceId'] == logical)['ResourceStatus'] = 'CREATE_COMPLETE'
            elif kind.startswith('database'):
                cloud.clients['rds'].describe_db_clusters.side_effect = None
                cloud.clients['rds'].describe_db_clusters.return_value = {'DBClusters': []}
            else:
                cloud.clients['lambda'].get_function.side_effect = None
                cloud.clients['lambda'].get_function.return_value = {'Configuration': {}}
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_successful_database_or_function_creation_followed_by_rollback_blocks(self):
        for logical in sorted(recovery.APPLICATION_IDS):
            cloud = FakeCloud()
            self.assertEqual(next(row for row in cloud.rows if row['LogicalResourceId'] == logical)
                             ['ResourceStatus'], 'DELETE_COMPLETE')
            cloud.events.insert(1, {'LogicalResourceId': logical,
                'ResourceType': cloud.template['Resources'][logical]['Type'], 'ResourceStatus': 'CREATE_COMPLETE'})
            with self.subTest(logical=logical), self.assertRaisesRegex(Gate, 'created before rollback'):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_missing_initial_event_or_update_import_history_blocks(self):
        for kind in ('missing', 'wrong-stack', 'update', 'import'):
            cloud = FakeCloud()
            if kind == 'missing':
                cloud.events.pop()
            elif kind == 'wrong-stack':
                cloud.events[-1]['PhysicalResourceId'] = NEW_STACK
            else:
                cloud.events.insert(0, {'LogicalResourceId': 'DataKey',
                    'ResourceType': 'AWS::KMS::Key',
                    'ResourceStatus': 'UPDATE_COMPLETE' if kind == 'update' else 'IMPORT_COMPLETE'})
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_complete_event_pagination_is_required_and_bound_failures_block(self):
        cloud = FakeCloud()
        original_paginator = cloud.paginator
        def paginator(operation):
            if operation == 'describe_stack_events':
                # An initial event in a later page must be read, while a creation
                # on another later page must still block despite DELETE_COMPLETE.
                return SimpleNamespace(paginate=lambda **kwargs: [
                    {'StackEvents': cloud.events[:2]}, {'StackEvents': cloud.events[2:]},
                    {'StackEvents': [{'LogicalResourceId': 'Database', 'ResourceStatus': 'CREATE_COMPLETE'}]}])
            return original_paginator(operation)
        cloud.clients['cloudformation'].get_paginator.side_effect = paginator
        with self.assertRaisesRegex(Gate, 'created before rollback'):
            recovery.initial_recovery_plan(cloud.aws, cloud.config)
        cloud.no_mutations(self)

        cloud = FakeCloud()
        original_paginator = cloud.paginator
        def excessive(operation):
            if operation == 'describe_stack_events':
                return SimpleNamespace(paginate=lambda **kwargs: [{'StackEvents': cloud.events}] * 21)
            return original_paginator(operation)
        cloud.clients['cloudformation'].get_paginator.side_effect = excessive
        with self.assertRaisesRegex(Gate, 'bound'):
            recovery.initial_recovery_plan(cloud.aws, cloud.config)
        cloud.no_mutations(self)

        cloud = FakeCloud()
        original_paginator = cloud.paginator
        def denied(operation):
            if operation == 'describe_stack_events':
                def pages(**kwargs):
                    yield {'StackEvents': cloud.events}
                    raise absent('AccessDenied')
                return SimpleNamespace(paginate=pages)
            return original_paginator(operation)
        cloud.clients['cloudformation'].get_paginator.side_effect = denied
        with self.assertRaises(ClientError):
            recovery.initial_recovery_plan(cloud.aws, cloud.config)
        cloud.no_mutations(self)

    def test_journal_versions_deleted_markers_users_or_control_rows_block_before_deletion(self):
        for kind in ('versions', 'delete-markers', 'multipart', 'users', 'control', 'control-pagination'):
            cloud = FakeCloud()
            if kind in ('versions', 'delete-markers'):
                cloud.clients['s3'].list_object_versions.return_value = {
                    'Versions' if kind == 'versions' else 'DeleteMarkers': [{'Key': 'fictional-existing-authority'}]}
            elif kind == 'multipart':
                cloud.clients['s3'].list_multipart_uploads.return_value = {'Uploads': [{'Key': 'fictional-unfinished-write'}]}
            elif kind == 'users':
                cloud.clients['cognito-idp'].list_users.return_value = {'Users': [{'Username': 'fictional-private-name'}]}
            else:
                cloud.clients['dynamodb'].scan.return_value = {'Count': 1} if kind == 'control' else {
                    'Count': 0, 'LastEvaluatedKey': {'PK': {'S': 'fictional'}}}
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_original_active_template_unknown_survivor_or_open_dependency_blocks(self):
        for kind in ('active', 'survivor', 'dependency', 'open-reference'):
            cloud = FakeCloud()
            if kind == 'active':
                cloud.template['Resources']['ApiFunction']['Properties']['ReservedConcurrentExecutions'] = 2
            elif kind == 'survivor':
                next(row for row in cloud.rows if row['LogicalResourceId'] == 'Network')['ResourceStatus'] = 'DELETE_FAILED'
            elif kind == 'open-reference':
                # Artifact CORS references WebDelivery, which did not survive.
                artifacts = cloud.template['Resources']['Artifacts']
                cloud.retained['Artifacts'] = artifacts
                cloud.physical['Artifacts'] = artifacts['Properties']['BucketName']
                row = next(row for row in cloud.rows if row['LogicalResourceId'] == 'Artifacts')
                row.update(ResourceStatus='DELETE_SKIPPED', PhysicalResourceId=cloud.physical['Artifacts'])
            else:
                next(row for row in cloud.rows if row['LogicalResourceId'] == 'DataKey')['ResourceStatus'] = 'DELETE_COMPLETE'
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_actual_resource_ownership_and_authority_state_must_match(self):
        for kind in ('tags', 'key-state', 'secret-identity', 'pool-identity', 'log-identity'):
            cloud = FakeCloud()
            if kind == 'tags':
                cloud.clients['s3'].get_bucket_tagging.return_value = {'TagSet': [
                    {'Key': 'deployment', 'Value': 'another-deployment'}]}
            elif kind == 'key-state':
                cloud.clients['kms'].describe_key.side_effect = None
                cloud.clients['kms'].describe_key.return_value = {'KeyMetadata': {
                    'KeyId': cloud.physical['CaptureSigningKey'], 'AWSAccountId': ACCOUNT,
                    'Description': cloud.retained['CaptureSigningKey']['Properties']['Description'],
                    'KeyState': 'PendingDeletion'}}
            elif kind == 'secret-identity':
                cloud.clients['secretsmanager'].describe_secret.side_effect = None
                cloud.clients['secretsmanager'].describe_secret.return_value = {
                    'Name': 'unrelated', 'ARN': cloud.physical['ApplicationSecret'], 'Tags': cloud.tags}
            elif kind == 'pool-identity':
                cloud.clients['cognito-idp'].describe_user_pool.return_value['UserPool']['Name'] = 'unrelated'
            else:
                cloud.clients['logs'].describe_log_groups.side_effect = None
                cloud.clients['logs'].describe_log_groups.return_value = {'logGroups': []}
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_import_identifiers_must_cover_every_exact_logical_resource(self):
        for kind in ('missing', 'ambiguous', 'duplicate'):
            cloud = FakeCloud()
            rows = cloud.summary(TemplateBody=json.dumps({'Resources': cloud.retained}))['ResourceIdentifierSummaries']
            if kind == 'missing':
                rows.pop()
            elif kind == 'ambiguous':
                rows[0]['ResourceIdentifiers'].append('UnreviewedAlternative')
            else:
                rows.append(deepcopy(rows[0]))
            cloud.clients['cloudformation'].get_template_summary.side_effect = None
            cloud.clients['cloudformation'].get_template_summary.return_value = {'ResourceIdentifierSummaries': rows}
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_aws_read_denial_is_not_misclassified_as_absent_application(self):
        cloud = FakeCloud()
        cloud.clients['rds'].describe_db_clusters.side_effect = absent('AccessDenied')
        with self.assertRaises(ClientError):
            recovery.initial_recovery_plan(cloud.aws, cloud.config)
        cloud.no_mutations(self)

    def test_changed_import_action_blocks_execution_and_preserves_failure_journal(self):
        cloud = FakeCloud()
        original_paginator = cloud.paginator
        def paginator(operation):
            if operation == 'describe_change_set':
                return SimpleNamespace(paginate=lambda **kwargs: [{'Changes': [{'ResourceChange': {
                    'Action': 'Add', 'LogicalResourceId': name, 'ResourceType': value['Type']}}
                    for name, value in cloud.retained.items()]}])
            return original_paginator(operation)
        cloud.clients['cloudformation'].get_paginator.side_effect = paginator
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-recovery.json'
            with self.assertRaisesRegex(Gate, 'change set'):
                recovery.recover_initial(cloud.aws, cloud.config, path)
            evidence = json.loads(path.read_text())
            self.assertEqual(evidence['status'], 'blocked-recovery-inspect-protected-journal-before-retry')
            self.assertEqual(evidence['failed_phase'], 'import-change-set-created')
            self.assertEqual(evidence['retained_physical_ids'], cloud.physical)
        cloud.clients['cloudformation'].execute_change_set.assert_not_called()
        cloud.clients['cloudformation'].delete_change_set.assert_called_once()

    def test_resource_change_after_metadata_detachment_blocks_import(self):
        cloud = FakeCloud()
        def changed(**kwargs):
            cloud.clients['s3'].list_object_versions.return_value = {'Versions': [{'Key': 'fictional-raced-write'}]}
        cloud.clients['cloudformation'].delete_stack.side_effect = changed
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-recovery.json'
            with self.assertRaisesRegex(Gate, 'empty'):
                recovery.recover_initial(cloud.aws, cloud.config, path)
            evidence = json.loads(path.read_text())
            self.assertEqual(evidence['failed_phase'], 'failed-stack-metadata-detached')
        cloud.clients['cloudformation'].create_change_set.assert_not_called()

    def test_import_completion_with_changed_physical_identity_is_not_reported_as_recovered(self):
        cloud = FakeCloud()
        original_paginator = cloud.paginator
        def paginator(operation):
            original = original_paginator(operation)
            def paginate(**kwargs):
                pages = deepcopy(list(original.paginate(**kwargs)))
                if operation == 'list_stack_resources' and cloud.status == 'IMPORT_COMPLETE':
                    pages[0]['StackResourceSummaries'][0]['PhysicalResourceId'] = 'unexpected-replacement'
                return pages
            return SimpleNamespace(paginate=paginate)
        cloud.clients['cloudformation'].get_paginator.side_effect = paginator
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-recovery.json'
            with self.assertRaisesRegex(Gate, 'adoption'):
                recovery.recover_initial(cloud.aws, cloud.config, path)
            evidence = json.loads(path.read_text())
            self.assertEqual(evidence['failed_phase'], 'import-executing')
            self.assertEqual(evidence['retained_physical_ids'], cloud.physical)

    def test_existing_journal_cannot_be_overwritten_for_an_unreviewed_resume(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-recovery.json'
            path.write_text('existing recovery evidence')
            with self.assertRaisesRegex(Gate, 'new protected'):
                recovery.recover_initial(cloud.aws, cloud.config, path)
            self.assertEqual(path.read_text(), 'existing recovery evidence')
        cloud.no_mutations(self)

    def test_detached_resume_preserves_source_and_every_identity_without_deleting_metadata(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            source_path, source = cloud.detached_manifest(directory)
            original_bytes = source_path.read_bytes()
            digest = hashlib.sha256(original_bytes).hexdigest()
            destination = Path(directory) / 'resumed.json'
            result = recovery.resume_initial(cloud.aws, cloud.config, destination, source_path, digest)
            self.assertEqual(result['status'], 'uninitialized-retained-resources-imported')
            self.assertEqual(result['retained_physical_ids'], cloud.physical)
            self.assertEqual(result['original_stack_id'], OLD_STACK)
            self.assertEqual(result['original_release_id'], 'b' * 40)
            self.assertEqual(result['prior_recovery_release_id'], 'a' * 40)
            self.assertEqual(result['release_id'], 'c' * 40)
            self.assertEqual(result['import_template_sha256'], source['import_template_sha256'])
            self.assertEqual(result['source_manifest_sha256'], digest)
            self.assertEqual(result['canonical_import_template_sha256'], hashlib.sha256(json.dumps(
                source['import_template'], sort_keys=True, separators=(',', ':')).encode()).hexdigest())
            self.assertEqual(source_path.read_bytes(), original_bytes)
            self.assertEqual(json.loads(destination.read_text()), result)
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
        cf = cloud.clients['cloudformation']
        cf.delete_stack.assert_not_called()
        self.assertNotIn('Tags', cf.create_change_set.call_args.kwargs)
        self.assertEqual(cf.create_change_set.call_args.kwargs['ResourcesToImport'], source['resources_to_import'])
        self.assertEqual(cf.update_termination_protection.call_count, 1)
        for client in cloud.clients.values():
            for forbidden in ('create_key', 'create_secret', 'create_bucket', 'create_table', 'create_user_pool',
                              'delete_bucket', 'delete_secret', 'delete_table', 'delete_user_pool',
                              'schedule_key_deletion', 'get_secret_value', 'get_object'):
                getattr(client, forbidden).assert_not_called()

    def test_resume_canonical_comparison_accepts_changed_aws_and_descriptor_order(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            source_path, source = cloud.detached_manifest(directory)
            cloud.rows.reverse()
            source['resources_to_import'].reverse()
            recovery._write(source_path, source)
            # The legacy digest differs from reconstruction because AWS order
            # changed. Canonical content and independently verified IDs match.
            reconstructed = recovery._initial_recovery_plan(cloud.aws, cloud.config, OLD_STACK)
            self.assertNotEqual(reconstructed['import_template_sha256'], source['import_template_sha256'])
            result = recovery.resume_initial(cloud.aws, cloud.config, Path(directory) / 'resumed.json',
                source_path, hashlib.sha256(source_path.read_bytes()).hexdigest())
            self.assertEqual(result['retained_physical_ids'], cloud.physical)

    def test_resume_hash_file_protection_and_json_ambiguity_block_all_mutations(self):
        for kind in ('hash', 'hash-format', 'writable', 'duplicate', 'too-large', 'symlink'):
            cloud = FakeCloud()
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                source_path, source = cloud.detached_manifest(directory)
                if kind == 'writable':
                    source_path.chmod(0o666)
                elif kind == 'duplicate':
                    source_path.write_text('{"status":"one","status":"two"}')
                elif kind == 'too-large':
                    source_path.write_text(' ' * 262145)
                elif kind == 'symlink':
                    target = Path(directory) / 'link.json'
                    target.symlink_to(source_path)
                    source_path = target
                digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
                if kind == 'hash':
                    digest = '0' * 64
                elif kind == 'hash-format':
                    digest = 'invalid'
                destination = Path(directory) / 'resumed.json'
                with self.assertRaises((Gate, OSError)):
                    recovery.resume_initial(cloud.aws, cloud.config, destination, source_path, digest)
                self.assertFalse(destination.exists())
                cloud.no_mutations(self)

    def test_resume_manifest_binding_or_authoritative_history_changes_block(self):
        kinds = ('account', 'region', 'environment', 'stack', 'source-release', 'original-release',
                 'phase', 'import-change', 'deleted-resources', 'legacy-hash', 'canonical-hash',
                 'physical', 'type', 'properties', 'identifier', 'descriptor-duplicate',
                 'history-app-created', 'history-missing', 'original-not-deleted')
        for kind in kinds:
            cloud = FakeCloud()
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                source_path, source = cloud.detached_manifest(directory)
                if kind == 'account':
                    source['account'] = '111111111111'
                elif kind == 'region':
                    source['region'] = 'us-west-2'
                elif kind == 'environment':
                    source['environment'] = 'production'
                elif kind == 'stack':
                    source['stack_name'] = 'other'
                elif kind == 'source-release':
                    source['release_id'] = 'not-a-reviewed-revision'
                elif kind == 'original-release':
                    source['original_release_id'] = 'd' * 40
                elif kind == 'phase':
                    source['failed_phase'] = 'detaching-failed-stack-metadata'
                elif kind == 'import-change':
                    source['import_change_set_id'] = 'unreviewed-change'
                elif kind == 'deleted-resources':
                    source['actual_resources_deleted'] = True
                elif kind == 'legacy-hash':
                    source['import_template_sha256'] = 'invalid'
                elif kind == 'canonical-hash':
                    source['canonical_import_template_sha256'] = '0' * 64
                elif kind == 'physical':
                    source['retained_physical_ids']['JournalKey'] = 'other-authority'
                elif kind == 'type':
                    source['import_template']['Resources']['JournalKey']['Type'] = 'AWS::KMS::Alias'
                elif kind == 'properties':
                    source['import_template']['Resources']['JournalKey']['Properties']['Description'] = 'changed'
                elif kind == 'identifier':
                    source['resources_to_import'][0]['ResourceIdentifier'] = {'WrongIdentifier': 'other'}
                elif kind == 'descriptor-duplicate':
                    source['resources_to_import'][0] = deepcopy(source['resources_to_import'][1])
                elif kind == 'history-app-created':
                    cloud.events.insert(0, {'LogicalResourceId': 'ApiFunction', 'ResourceStatus': 'CREATE_COMPLETE'})
                elif kind == 'history-missing':
                    cloud.events.pop()
                else:
                    cloud.original_deleted = False
                recovery._write(source_path, source)
                destination = Path(directory) / 'resumed.json'
                with self.assertRaises(Gate):
                    recovery.resume_initial(cloud.aws, cloud.config, destination, source_path,
                        hashlib.sha256(source_path.read_bytes()).hexdigest())
                self.assertFalse(destination.exists())
                cloud.no_mutations(self)

    def test_resume_requires_unchanged_live_initial_state_and_successful_original_reads(self):
        for kind in ('journal', 'users', 'control', 'database', 'function', 'key', 'history-denied', 'absence-denied'):
            cloud = FakeCloud()
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                source_path, _ = cloud.detached_manifest(directory)
                if kind == 'journal':
                    cloud.clients['s3'].list_object_versions.return_value = {'DeleteMarkers': [{'Key': 'initialized'}]}
                elif kind == 'users':
                    cloud.clients['cognito-idp'].list_users.return_value = {'Users': [{'Username': 'initialized'}]}
                elif kind == 'control':
                    cloud.clients['dynamodb'].scan.return_value = {'Count': 1}
                elif kind in ('database', 'function'):
                    target = cloud.clients['rds'].describe_db_clusters if kind == 'database' else cloud.clients['lambda'].get_function
                    target.side_effect = None
                    target.return_value = {}
                elif kind == 'key':
                    cloud.clients['kms'].describe_key.side_effect = absent('AccessDenied')
                elif kind == 'history-denied':
                    cloud.clients['cloudformation'].get_template.side_effect = absent('AccessDenied')
                else:
                    original = cloud.describe_stacks
                    def denied(**kwargs):
                        if kwargs['StackName'] == recovery.STACK:
                            raise absent('AccessDenied')
                        return original(**kwargs)
                    cloud.clients['cloudformation'].describe_stacks.side_effect = denied
                destination = Path(directory) / 'resumed.json'
                with self.assertRaises((Gate, ClientError)):
                    recovery.resume_initial(cloud.aws, cloud.config, destination, source_path,
                        hashlib.sha256(source_path.read_bytes()).hexdigest())
                self.assertFalse(destination.exists())
                cloud.no_mutations(self)

    def test_resume_admits_exact_untagged_import_complete_and_restores_protection(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            source_path, _ = cloud.detached_manifest(directory)
            cloud.status = 'IMPORT_COMPLETE'
            cloud.protection = False
            result = recovery.resume_initial(cloud.aws, cloud.config, Path(directory) / 'resumed.json',
                source_path, hashlib.sha256(source_path.read_bytes()).hexdigest())
            self.assertEqual(result['recovered_stack_id'], NEW_STACK)
            self.assertTrue(cloud.protection)
        cf = cloud.clients['cloudformation']
        cf.create_change_set.assert_not_called()
        cf.execute_change_set.assert_not_called()
        cf.delete_stack.assert_not_called()
        cf.update_termination_protection.assert_called_once_with(StackName=NEW_STACK, EnableTerminationProtection=True)

    def test_import_tag_application_update_complete_rows_preserve_exact_resources_and_resume(self):
        # Real AWS import38279993813 finished at stackIMPORT_COMPLETE while its
        # retained rows became UPDATE_COMPLETE after automatic tag application.
        cloud = FakeCloud()
        cloud.import_resource_status = 'UPDATE_COMPLETE'
        with tempfile.TemporaryDirectory() as directory:
            initial = recovery.recover_initial(cloud.aws, cloud.config, Path(directory) / 'initial.json')
            self.assertEqual(initial['status'], 'uninitialized-retained-resources-imported')
            self.assertEqual(initial['retained_physical_ids'], cloud.physical)
        cloud = FakeCloud()
        cloud.import_resource_status = 'UPDATE_COMPLETE'
        with tempfile.TemporaryDirectory() as directory:
            source_path, _ = cloud.detached_manifest(directory)
            cloud.status = 'IMPORT_COMPLETE'
            resumed = recovery.resume_initial(cloud.aws, cloud.config, Path(directory) / 'resumed.json',
                source_path, hashlib.sha256(source_path.read_bytes()).hexdigest())
            self.assertEqual(resumed['status'], 'uninitialized-retained-resources-imported')
            self.assertEqual(resumed['retained_physical_ids'], cloud.physical)
        cloud.no_mutations(self)

    def test_import_completion_blocks_nonfinal_or_unexpected_retained_resource_statuses(self):
        for status in ('CREATE_COMPLETE', 'IMPORT_IN_PROGRESS', 'IMPORT_FAILED', 'UPDATE_IN_PROGRESS',
                       'UPDATE_FAILED', 'DELETE_COMPLETE', 'DELETE_SKIPPED'):
            cloud = FakeCloud()
            cloud.import_resource_status = status
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                source_path, _ = cloud.detached_manifest(directory)
                cloud.status = 'IMPORT_COMPLETE'
                destination = Path(directory) / 'resumed.json'
                with self.assertRaisesRegex(Gate, 'adoption'):
                    recovery.resume_initial(cloud.aws, cloud.config, destination, source_path,
                        hashlib.sha256(source_path.read_bytes()).hexdigest())
                self.assertFalse(destination.exists())
            cloud.no_mutations(self)

    def test_resume_blocks_other_stack_states_and_changed_imported_inventory(self):
        for kind in ('REVIEW_IN_PROGRESS', 'IMPORT_IN_PROGRESS', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE',
                     'tags', 'physical', 'type', 'template'):
            cloud = FakeCloud()
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                source_path, _ = cloud.detached_manifest(directory)
                cloud.status = kind if kind.isupper() else 'IMPORT_COMPLETE'
                if kind == 'tags':
                    cloud.import_tags = [{'Key': 'deployment', 'Value': 'other'}]
                elif kind in ('physical', 'type'):
                    original_paginator = cloud.paginator
                    def paginator(operation):
                        original = original_paginator(operation)
                        def paginate(**kwargs):
                            pages = deepcopy(list(original.paginate(**kwargs)))
                            if operation == 'list_stack_resources' and kwargs['StackName'] == NEW_STACK:
                                pages[0]['StackResourceSummaries'][0][
                                    'PhysicalResourceId' if kind == 'physical' else 'ResourceType'] = 'changed'
                            return pages
                        return SimpleNamespace(paginate=paginate)
                    cloud.clients['cloudformation'].get_paginator.side_effect = paginator
                elif kind == 'template':
                    original_template = cloud.clients['cloudformation'].get_template.side_effect
                    def template(**kwargs):
                        result = original_template(**kwargs)
                        if kwargs['StackName'] == NEW_STACK:
                            result['TemplateBody']['Description'] = 'unreviewed'
                        return result
                    cloud.clients['cloudformation'].get_template.side_effect = template
                destination = Path(directory) / 'resumed.json'
                with self.assertRaises(Gate):
                    recovery.resume_initial(cloud.aws, cloud.config, destination, source_path,
                        hashlib.sha256(source_path.read_bytes()).hexdigest())
                self.assertFalse(destination.exists())
                cloud.no_mutations(self)

    def test_resume_import_error_preserves_source_and_records_bounded_aws_diagnostic(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            source_path, _ = cloud.detached_manifest(directory)
            original_bytes = source_path.read_bytes()
            cloud.clients['cloudformation'].create_change_set.side_effect = ClientError({
                'Error': {'Code': 'ValidationException', 'Message': 'fictional AWS import rejection'},
                'ResponseMetadata': {'RequestId': 'fixture-request'}}, 'CreateChangeSet')
            destination = Path(directory) / 'resumed.json'
            with self.assertRaises(ClientError):
                recovery.resume_initial(cloud.aws, cloud.config, destination, source_path,
                    hashlib.sha256(original_bytes).hexdigest())
            evidence = json.loads(destination.read_text())
            self.assertEqual(evidence['failed_phase'], 'failed-stack-metadata-detached')
            self.assertEqual(evidence['failure_operation'], 'CreateChangeSet')
            self.assertEqual(evidence['failure_code'], 'ValidationException')
            self.assertEqual(evidence['failure_request_id'], 'fixture-request')
            self.assertNotIn('failure_message', evidence)
            self.assertEqual(source_path.read_bytes(), original_bytes)
            self.assertEqual(evidence['retained_physical_ids'], cloud.physical)
        cloud.clients['cloudformation'].delete_stack.assert_not_called()
        cloud.clients['cloudformation'].execute_change_set.assert_not_called()

    def test_dependency_parser_handles_substitution_variables_and_escaped_pseudo_parameters(self):
        self.assertEqual(recovery._references({'Fn::Sub': ['${Arn}/* ${DataKey.Arn} ${AWS::AccountId} ${!literal}',
            {'Arn': {'Fn::GetAtt': ['DeletionJournal', 'Arn']}}], 'DependsOn': 'JournalKey'}),
            {'DeletionJournal', 'DataKey', 'JournalKey'})


if __name__ == '__main__':
    unittest.main()
