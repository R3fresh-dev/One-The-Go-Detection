"""First-stack recovery contracts; these fixtures are not AWS acceptance proof."""
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

from botocore.exceptions import ClientError
from botocore.handlers import json_decode_template_body

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
            if value.get('DeletionPolicy') == 'Retain' and value['Type'] in recovery.RETAINED_TYPES
            and name not in ('Artifacts', 'DatabaseWriter')}
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
                              'create_key', 'create_secret', 'create_bucket', 'create_table', 'create_user_pool',
                              'modify_db_subnet_group', 'delete_db_cluster', 'delete_db_instance'):
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

    def test_completed_import_accepts_aws_normalized_resource_status_without_relaxing_inventory(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            source_path, source = cloud.detached_manifest(directory)
            cloud.status = 'IMPORT_COMPLETE'
            cloud.import_tags = []
            cloud.protection = True
            original_paginator = cloud.paginator
            def paginator(operation):
                original = original_paginator(operation)
                def paginate(**kwargs):
                    pages = deepcopy(list(original.paginate(**kwargs)))
                    if operation == 'list_stack_resources' and kwargs['StackName'] == NEW_STACK:
                        for row in pages[0]['StackResourceSummaries']:
                            row['ResourceStatus'] = 'UPDATE_COMPLETE'
                    return pages
                return SimpleNamespace(paginate=paginate)
            cloud.clients['cloudformation'].get_paginator.side_effect = paginator
            destination = Path(directory) / 'normalized-import.json'
            result = recovery.resume_initial(cloud.aws, cloud.config, destination, source_path,
                hashlib.sha256(source_path.read_bytes()).hexdigest())
            self.assertEqual(result['retained_physical_ids'], cloud.physical)
            cloud.clients['cloudformation'].create_change_set.assert_not_called()
            cloud.clients['cloudformation'].execute_change_set.assert_not_called()

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

    def test_sdk_ordered_templates_preserve_fresh_import_and_existing_stack_resume(self):
        for mode in ('fresh', 'resume'):
            cloud = FakeCloud()
            cloud.import_resource_status = 'UPDATE_COMPLETE'
            original_response = cloud.clients['cloudformation'].get_template.side_effect

            def sdk_response(**kwargs):
                response = original_response(**kwargs)
                # GetTemplate's real botocore handler decodes both templates
                # into nested OrderedDicts. The saved import has sorted keys,
                # while the original stopped template follows builder order.
                response['TemplateBody'] = json.dumps(response['TemplateBody'],
                    sort_keys=kwargs['StackName'] == NEW_STACK)
                json_decode_template_body(response)
                return response

            cloud.clients['cloudformation'].get_template.side_effect = sdk_response
            plan = recovery.initial_recovery_plan(cloud.aws, cloud.config)
            actual = sdk_response(StackName=NEW_STACK)['TemplateBody']
            expected = plan['import_template']
            self.assertIsInstance(actual['Resources']['DataKey'], OrderedDict)
            self.assertIsInstance(expected['Resources']['DataKey'], OrderedDict)
            self.assertNotEqual(actual['Resources']['DataKey'], expected['Resources']['DataKey'])
            self.assertEqual(json.dumps(actual, sort_keys=True), json.dumps(expected, sort_keys=True))
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                if mode == 'fresh':
                    result = recovery.recover_initial(cloud.aws, cloud.config, Path(directory) / 'initial.json')
                else:
                    source_path, _ = cloud.detached_manifest(directory)
                    cloud.status = 'IMPORT_COMPLETE'
                    result = recovery.resume_initial(cloud.aws, cloud.config, Path(directory) / 'resumed.json',
                        source_path, hashlib.sha256(source_path.read_bytes()).hexdigest())
                self.assertEqual(result['status'], 'uninitialized-retained-resources-imported')
                self.assertEqual(result['retained_physical_ids'], cloud.physical)
            if mode == 'resume':
                cloud.no_mutations(self)

    def test_canonical_import_template_still_rejects_changed_values_lists_types_and_policies(self):
        for kind in ('property', 'list', 'boolean-value', 'boolean-type', 'retention', 'resource-type'):
            cloud = FakeCloud()
            original_response = cloud.clients['cloudformation'].get_template.side_effect

            def sdk_response(**kwargs):
                response = original_response(**kwargs)
                if kwargs['StackName'] == NEW_STACK:
                    key = response['TemplateBody']['Resources']['DataKey']
                    if kind == 'property':
                        key['Properties']['Description'] = 'changed authority'
                    elif kind == 'list':
                        key['Properties']['KeyPolicy']['Statement'].reverse()
                    elif kind == 'boolean-value':
                        key['Properties']['EnableKeyRotation'] = False
                    elif kind == 'boolean-type':
                        # Python equality accepts True == 1; canonical JSON
                        # keeps scalar types distinct as well as exact values.
                        key['Properties']['EnableKeyRotation'] = 1
                    elif kind == 'retention':
                        key['DeletionPolicy'] = 'Delete'
                    else:
                        key['Type'] = 'AWS::KMS::Alias'
                response['TemplateBody'] = json.dumps(response['TemplateBody'],
                    sort_keys=kwargs['StackName'] == NEW_STACK)
                json_decode_template_body(response)
                return response

            cloud.clients['cloudformation'].get_template.side_effect = sdk_response
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                source_path, _ = cloud.detached_manifest(directory)
                cloud.status = 'IMPORT_COMPLETE'
                destination = Path(directory) / 'resumed.json'
                with self.assertRaisesRegex(Gate, 'imported stack template differs'):
                    recovery.resume_initial(cloud.aws, cloud.config, destination, source_path,
                        hashlib.sha256(source_path.read_bytes()).hexdigest())
                self.assertFalse(destination.exists())
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


class ContinuationCloud(FakeCloud):
    """The observed 15-authority/8-tracked/1-detached-writer boundary."""
    def __init__(self, directory):
        super().__init__()
        source_path, source = self.detached_manifest(directory)
        self.failed_release = self.config['releaseId']
        adoption = {**source, 'release_id': self.failed_release,
            'status': 'uninitialized-retained-resources-imported', 'recovered_stack_id': NEW_STACK,
            'source_manifest_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest()}
        self.bundle = {'schema_version': '1.0.0', 'operation': 'serverless-uninitialized-continuation',
            'account': ACCOUNT, 'region': REGION, 'stack_name': recovery.STACK,
            'failed_run_id': 123, 'failed_run_attempt': 1, 'failed_release_id': self.failed_release,
            'artifact_sha256': 'e' * 64, 'failed_run_started_at': '2020-01-01T00:00:00Z',
            'failed_run_completed_at': '2020-01-01T01:00:00Z',
            'original_recovery_raw': source_path.read_text(), 'adoption_raw': json.dumps(adoption),
            'deployment_state_raw': json.dumps({'schema_version': '1.0.0',
                'environment': 'serverless-development', 'account': ACCOUNT, 'region': REGION,
                'release_id': self.failed_release, 'status': 'failed', 'current_stage': 'deploy-stopped',
                'failed_stage': 'deploy-stopped', 'completed_stages': [
                    'resume-initial-retained-resources', 'serverless-registry',
                    'exact-source-archive', 'build-immutable-lambda-images'],
                'completed_receipts': {}, 'rollback_executed': False}),
            'gate_admission_raw': json.dumps({'provider': 'github_actions', 'repository': recovery.REPOSITORY,
                'workflow_path': recovery.WORKFLOW_PATH, 'head_sha': self.failed_release,
                'event': 'push', 'head_branch': 'main',
                'jobs': {name: index + 1 for index, name in enumerate(sorted(recovery.REQUIRED_JOBS))}}),
            'serverless_plan_raw': json.dumps({'environment': 'serverless-development',
                'account': ACCOUNT, 'region': REGION, 'deployment_executed': False})}
        self.bundle_path = Path(directory) / 'continuation-source.json'
        self.config['releaseId'] = 'd' * 40
        self.status = 'UPDATE_ROLLBACK_COMPLETE'
        self.current_template = deepcopy(source['import_template'])
        self.graph = {**self.physical, 'Database': recovery.STACK,
            'DatabaseWriter': recovery.STACK + '-writer', 'DatabaseParameters': 'parameters-fixture',
            'DatabaseSubnets': 'subnet-group-fixture', 'Network': 'vpc-fixture',
            'NetworkIpv6': 'vpc-cidr-assoc-fixture', 'PrivateA': 'subnet-a-fixture',
            'DatabaseSecurityGroup': 'sg-database-fixture', 'LambdaSecurityGroup': 'sg-lambda-fixture'}
        self.deleted_subnet = 'subnet-b-deleted'
        self.current_rows = [{'LogicalResourceId': name, 'ResourceType': resource['Type'],
            'PhysicalResourceId': self.graph[name], 'ResourceStatus': 'UPDATE_COMPLETE'}
            for name, resource in self.retained.items()]
        self.current_rows += [{'LogicalResourceId': name, 'ResourceType': kind,
            'PhysicalResourceId': self.graph[name], 'ResourceStatus': 'CREATE_COMPLETE'}
            for name, (kind, _) in recovery.DATABASE_IMPORT_IDS.items() if name != 'DatabaseWriter']
        self.current_events = [{'LogicalResourceId': recovery.STACK, 'ResourceType': 'AWS::CloudFormation::Stack',
            'PhysicalResourceId': NEW_STACK, 'ResourceStatus': 'UPDATE_IN_PROGRESS', 'Timestamp': '2020-01-01T00:01:00Z'}]
        self.current_events += [{'LogicalResourceId': name, 'ResourceType': kind,
            'PhysicalResourceId': self.graph[name], 'ResourceStatus': 'CREATE_COMPLETE',
            'Timestamp': '2020-01-01T00:02:00Z'}
            for name, (kind, _) in recovery.DATABASE_IMPORT_IDS.items() if name != 'DatabaseWriter']
        self.current_events += [{'LogicalResourceId': 'DatabaseWriter', 'ResourceType': 'AWS::RDS::DBInstance',
            'PhysicalResourceId': self.graph['DatabaseWriter'], 'ResourceStatus': 'DELETE_SKIPPED',
            'Timestamp': '2020-01-01T00:04:00Z'},
            {'LogicalResourceId': 'PrivateB', 'ResourceType': 'AWS::EC2::Subnet',
             'PhysicalResourceId': self.deleted_subnet, 'ResourceStatus': 'DELETE_COMPLETE',
             'Timestamp': '2020-01-01T00:04:00Z'}]
        # The real failed stopped deployment did create its concurrency-zero
        # control Lambda, and then deleted it. Other application Lambdas did not.
        for status, timestamp in [('CREATE_COMPLETE', '00:02:00'), ('DELETE_COMPLETE', '00:04:00')]:
            self.current_events.append({'LogicalResourceId': 'ControlFunction', 'ResourceType': 'AWS::Lambda::Function',
                'PhysicalResourceId': recovery.STACK + '-control', 'ResourceStatus': status,
                'Timestamp': '2020-01-01T' + timestamp + 'Z'})
        self.changes = [{'ResourceChange': {'Action': 'Import', 'LogicalResourceId': name,
            'ResourceType': kind}} for name, (kind, _) in recovery.DATABASE_IMPORT_IDS.items()]
        cf = self.clients['cloudformation']
        cf.get_template.side_effect = lambda **kwargs: {'TemplateBody': deepcopy(
            self.template if kwargs['StackName'] == OLD_STACK else self.current_template)}
        cf.get_template_summary.side_effect = self.continuation_summary
        cf.get_paginator.side_effect = self.continuation_paginator
        cf.get_waiter.side_effect = self.continuation_waiter
        cf.describe_stack_resource.side_effect = self.describe_current_resource
        self.clients['ec2'] = Mock(name='ec2')
        self.clients['ecr'] = Mock(name='ecr')
        self.configure_database()
        self.configure_images()

    def write_bundle(self):
        recovery._write(self.bundle_path, self.bundle)
        return self.bundle_path, hashlib.sha256(self.bundle_path.read_bytes()).hexdigest()

    def describe_current_resource(self, **kwargs):
        logical = kwargs['LogicalResourceId']
        matches = [row for row in self.current_rows if row['LogicalResourceId'] == logical]
        if not matches:
            raise ClientError({'Error': {'Code': 'ValidationError',
                'Message': 'Stack does not contain resource ' + logical}}, 'DescribeStackResource')
        if len(matches) != 1:
            raise AssertionError('Ambiguous fixture resource ' + logical)
        return {'StackResourceDetail': deepcopy(matches[0])}

    def continuation_summary(self, **kwargs):
        resources = json.loads(kwargs['TemplateBody'])['Resources']
        old = {'AWS::KMS::Key': 'KeyId', 'AWS::SecretsManager::Secret': 'Id',
            'AWS::S3::Bucket': 'BucketName', 'AWS::DynamoDB::Table': 'TableName',
            'AWS::Cognito::UserPool': 'UserPoolId', 'AWS::Logs::LogGroup': 'LogGroupName',
            'AWS::EC2::Subnet': 'SubnetId'}
        return {'ResourceIdentifierSummaries': [{'ResourceType': resource['Type'],
            'LogicalResourceIds': [name], 'ResourceIdentifiers': [','.join(recovery.DATABASE_IMPORT_IDS[name][1])
                if name in recovery.DATABASE_IMPORT_IDS else old[resource['Type']]]}
            for name, resource in resources.items()]}

    def continuation_paginator(self, operation):
        if operation in ('describe_stack_events', 'list_stack_resources'):
            def paginate(**kwargs):
                original = kwargs['StackName'] == OLD_STACK
                key = 'StackEvents' if operation == 'describe_stack_events' else 'StackResourceSummaries'
                rows = (self.events if original else self.current_events) if key == 'StackEvents' else (
                    self.rows if original else self.current_rows)
                return [{key: rows}]
            return SimpleNamespace(paginate=paginate)
        if operation == 'describe_change_set':
            return SimpleNamespace(paginate=lambda **kwargs: [{'Changes': self.changes}])
        raise AssertionError(operation)

    def continuation_waiter(self, name):
        def wait(**kwargs):
            if name == 'stack_import_complete':
                self.adopt(json.loads(self.clients['cloudformation'].create_change_set.call_args.kwargs['TemplateBody']))
        return SimpleNamespace(wait=wait)

    def adopt(self, template):
        self.status = 'IMPORT_COMPLETE'
        self.current_template = deepcopy(template)
        self.current_rows = [{'LogicalResourceId': name, 'ResourceType': resource['Type'],
            'PhysicalResourceId': self.graph[name], 'ResourceStatus': 'UPDATE_COMPLETE'}
            for name, resource in template['Resources'].items()]

    def configure_images(self):
        ecr = self.clients['ecr']
        uri = f'{ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/{recovery.STACK}'
        ecr.describe_repositories.return_value = {'repositories': [{'repositoryName': recovery.STACK,
            'repositoryUri': uri, 'registryId': ACCOUNT, 'imageTagMutability': 'IMMUTABLE', 'repositoryArn': 'repo-arn'}]}
        ecr.list_tags_for_resource.return_value = {'tags': self.tags}
        manifests = {role: json.dumps({'mediaType': 'application/vnd.oci.image.manifest.v1+json',
            'schemaVersion': 2, 'config': {'digest': role}}) for role in ('api', 'worker')}
        digests = {role: 'sha256:' + hashlib.sha256(raw.encode()).hexdigest() for role, raw in manifests.items()}
        ecr.describe_images.side_effect = lambda **kwargs: {'imageDetails': [{'imageTags': [kwargs['imageIds'][0]['imageTag']],
            'imageDigest': digests[kwargs['imageIds'][0]['imageTag'].split('-')[0]]}]}
        ecr.batch_get_image.side_effect = lambda **kwargs: {'images': [{'imageManifest': next(
            manifests[role] for role in manifests if digests[role] == kwargs['imageIds'][0]['imageDigest'])}]}

    def configure_database(self):
        p, rds, ec2 = self.graph, self.clients['rds'], self.clients['ec2']
        key = f'arn:aws:kms:{REGION}:{ACCOUNT}:key/{p["DataKey"]}'
        self.cluster = {'DBClusterIdentifier': p['Database'], 'DBClusterArn': f'arn:aws:rds:{REGION}:{ACCOUNT}:cluster:{p["Database"]}',
            'Status': 'available', 'Engine': 'aurora-postgresql', 'EngineVersion': '16.15', 'DatabaseName': 'otgd',
            'MasterUsername': 'otgd_migrator', 'StorageEncrypted': True, 'KmsKeyId': key, 'DeletionProtection': True,
            'BackupRetentionPeriod': 7, 'DBClusterMembers': [{'DBInstanceIdentifier': p['DatabaseWriter'],
                'IsClusterWriter': True, 'DBClusterParameterGroupStatus': 'in-sync'}],
            'MasterUserSecret': {'SecretStatus': 'active', 'KmsKeyId': key,
                'SecretArn': f'arn:aws:secretsmanager:{REGION}:{ACCOUNT}:secret:rds!cluster-fixture'},
            'ServerlessV2ScalingConfiguration': {'MinCapacity': 0, 'MaxCapacity': 1, 'SecondsUntilAutoPause': 300},
            'DBClusterParameterGroup': p['DatabaseParameters'], 'DBSubnetGroup': p['DatabaseSubnets'],
            'DbClusterResourceId': 'cluster-unique-fixture', 'ClusterCreateTime': '2020-01-01T00:02:00Z',
            'VpcSecurityGroups': [{'VpcSecurityGroupId': p['DatabaseSecurityGroup'], 'Status': 'active'}], 'TagList': self.tags}
        group = {'DBSubnetGroupName': p['DatabaseSubnets'],
            'DBSubnetGroupArn': f'arn:aws:rds:{REGION}:{ACCOUNT}:subgrp:{p["DatabaseSubnets"]}',
            'SubnetGroupStatus': 'Complete', 'VpcId': p['Network'], 'Subnets': [
                {'SubnetIdentifier': item, 'SubnetStatus': 'Active', 'SubnetAvailabilityZone': {'Name': REGION + zone}}
                for item, zone in ((p['PrivateA'], 'a'), (self.deleted_subnet, 'b'))]}
        self.subnet_group = group
        self.writer = {'DBInstanceIdentifier': p['DatabaseWriter'], 'DBInstanceArn': f'arn:aws:rds:{REGION}:{ACCOUNT}:db:{p["DatabaseWriter"]}',
            'DBInstanceStatus': 'available', 'Engine': 'aurora-postgresql', 'EngineVersion': '16.15',
            'DBInstanceClass': 'db.serverless', 'DBClusterIdentifier': p['Database'], 'PubliclyAccessible': False,
            'AvailabilityZone': REGION + 'a',
            'AutoMinorVersionUpgrade': False, 'StorageEncrypted': True, 'KmsKeyId': key,
            'DbiResourceId': 'db-unique-fixture', 'InstanceCreateTime': '2020-01-01T00:05:00Z',
            'DBSubnetGroup': group, 'TagList': self.tags}
        rds.describe_db_clusters.side_effect = lambda **kwargs: {'DBClusters': [self.cluster]}
        rds.describe_db_instances.side_effect = lambda **kwargs: {'DBInstances': [self.writer]}
        rds.describe_db_subnet_groups.return_value = {'DBSubnetGroups': [group]}
        rds.describe_db_cluster_parameter_groups.return_value = {'DBClusterParameterGroups': [{
            'DBClusterParameterGroupName': p['DatabaseParameters'], 'DBParameterGroupFamily': 'aurora-postgresql16',
            'Description': 'Verified PostgreSQL TLS required', 'DBClusterParameterGroupArn': 'parameters-arn'}]}
        rds.list_tags_for_resource.return_value = {'TagList': self.tags}
        rds.get_paginator.return_value = SimpleNamespace(paginate=lambda **kwargs: [{'Parameters': [
            {'ParameterName': 'rds.force_ssl', 'ParameterValue': '1'}]}])
        self.vpc = {'VpcId': p['Network'], 'State': 'available', 'IsDefault': False, 'CidrBlock': '10.76.0.0/16',
            'Tags': self.tags, 'Ipv6CidrBlockAssociationSet': [{'AssociationId': p['NetworkIpv6'],
                'Ipv6CidrBlockState': {'State': 'associated'}, 'Ipv6Pool': 'Amazon', 'NetworkBorderGroup': REGION,
                'Ipv6CidrBlock': '2600:1f16:1d94:dd00::/56'}]}
        self.subnet = {'SubnetId': p['PrivateA'], 'VpcId': p['Network'], 'State': 'available',
            'CidrBlock': '10.76.0.0/24', 'MapPublicIpOnLaunch': False, 'AssignIpv6AddressOnCreation': True,
            'AvailabilityZone': REGION + 'a', 'Tags': self.tags, 'Ipv6CidrBlockAssociationSet': [
                {'Ipv6CidrBlock': '2600:1f16:1d94:dd00::/64', 'Ipv6CidrBlockState': {'State': 'associated'}}]}
        ec2.describe_vpcs.side_effect = lambda **kwargs: {'Vpcs': [self.vpc]}
        self.live_subnets = [self.subnet]
        def subnets(**kwargs):
            if kwargs.get('SubnetIds') == [self.deleted_subnet]:
                raise absent('InvalidSubnetID.NotFound')
            if 'SubnetIds' in kwargs:
                found = [row for row in self.live_subnets if row['SubnetId'] in kwargs['SubnetIds']]
                if len(found) != len(kwargs['SubnetIds']):
                    raise absent('InvalidSubnetID.NotFound')
                return {'Subnets': found}
            return {'Subnets': self.live_subnets}
        ec2.describe_subnets.side_effect = subnets
        ec2.describe_vpc_attribute.side_effect = lambda **kwargs: {'VpcId': p['Network'],
            kwargs['Attribute'][0].upper() + kwargs['Attribute'][1:]: {'Value': True}}
        def rule(port, field, value):
            key = {'IpRanges': 'CidrIp', 'Ipv6Ranges': 'CidrIpv6', 'UserIdGroupPairs': 'GroupId'}[field]
            return {'IpProtocol': 'tcp', 'FromPort': port, 'ToPort': port, field: [{key: value}]}
        self.groups = [{'GroupId': p['DatabaseSecurityGroup'], 'VpcId': p['Network'], 'OwnerId': ACCOUNT, 'Tags': self.tags,
            'IpPermissions': [rule(5432, 'UserIdGroupPairs', p['LambdaSecurityGroup'])],
            'IpPermissionsEgress': [rule(5432, 'IpRanges', '127.0.0.1/32')]},
            {'GroupId': p['LambdaSecurityGroup'], 'VpcId': p['Network'], 'OwnerId': ACCOUNT, 'Tags': self.tags,
             'IpPermissions': [], 'IpPermissionsEgress': [rule(443, 'IpRanges', '0.0.0.0/0'), rule(443, 'Ipv6Ranges', '::/0')]}]
        ec2.describe_security_groups.side_effect = lambda **kwargs: {'SecurityGroups': self.groups}


class RepairContinuationCloud(ContinuationCloud):
    """An authenticated failed import with its original database still intact."""
    def __init__(self, directory):
        super().__init__(directory)
        self.current_rows = [row for row in self.current_rows if row['LogicalResourceId'] in self.physical]
        source, digest = self.write_bundle()
        raw = source.read_text()
        with patch.object(recovery, '_historical_builder', return_value=build_template):
            previous = recovery.uninitialized_continuation_plan(self.aws, self.config, source, digest)
        self.previous_release = self.config['releaseId']
        previous.update(status='blocked-recovery-inspect-protected-journal-before-retry',
            failed_phase='surviving-database-import-executing',
            failure_type='WaiterError', import_change_set_id=
                f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:changeSet/uninitialized-import-previous/failed-fixture')
        self.bundle['previous_recovery'] = {
            'run_id': 456, 'run_attempt': 1, 'release_id': self.previous_release, 'artifact_sha256': 'f' * 64,
            'run_started_at': '2020-01-01T01:10:00Z', 'run_completed_at': '2020-01-01T01:20:00Z',
            'source_bundle_raw': raw, 'continuation_raw': json.dumps(previous),
            'deployment_state_raw': json.dumps({'schema_version': '1.0.0',
                'environment': 'fargate-development', 'account': ACCOUNT, 'region': REGION,
                'release_id': self.previous_release, 'status': 'failed',
                'current_stage': 'continue-uninitialized-retained-resources',
                'failed_stage': 'continue-uninitialized-retained-resources',
                'completed_stages': [], 'completed_receipts': {}, 'rollback_executed': False})}
        self.config['releaseId'] = 'e' * 40
        self.status = 'IMPORT_ROLLBACK_COMPLETE'
        self.current_rows = [row for row in self.current_rows if row['LogicalResourceId'] in self.physical]
        self.current_events += [{'LogicalResourceId': recovery.STACK, 'ResourceType': 'AWS::CloudFormation::Stack',
            'PhysicalResourceId': NEW_STACK, 'ResourceStatus': status, 'Timestamp': timestamp}
            for status, timestamp in (('IMPORT_IN_PROGRESS', '2020-01-01T01:11:00Z'),
                                       ('IMPORT_ROLLBACK_COMPLETE', '2020-01-01T01:19:00Z'))]
        self.repaired_subnet_id = 'subnet-b-repaired'
        self.update_changes = [{'ResourceChange': {'Action': 'Add', 'LogicalResourceId': 'PrivateB',
            'ResourceType': 'AWS::EC2::Subnet'}}]
        cf = self.clients['cloudformation']
        cf.create_change_set.side_effect = lambda **kwargs: {'Id':
            f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:changeSet/{kwargs["ChangeSetType"].lower()}/fixture'}
        self.clients['rds'].modify_db_subnet_group.side_effect = self.modify_membership

    def write_bundle(self):
        # Source packets may include previous source packets; their separate
        # bounded input size is larger than the individual phase receipt limit.
        self.bundle_path.write_text(json.dumps(self.bundle, indent=2, sort_keys=True) + '\n')
        self.bundle_path.chmod(0o600)
        return self.bundle_path, hashlib.sha256(self.bundle_path.read_bytes()).hexdigest()

    def seal_failed_attempt(self, journal, started_at, completed_at):
        self.bundle['previous_recovery'] = {
            'run_id': 789, 'run_attempt': 1, 'release_id': self.config['releaseId'], 'artifact_sha256': 'a' * 64,
            'run_started_at': started_at.isoformat(), 'run_completed_at': completed_at.isoformat(),
            'source_bundle_raw': self.bundle_path.read_text(), 'continuation_raw': json.dumps(journal),
            'deployment_state_raw': json.dumps({'schema_version': '1.0.0',
                'environment': 'fargate-development', 'account': ACCOUNT, 'region': REGION,
                'release_id': self.config['releaseId'], 'status': 'failed',
                'current_stage': 'continue-uninitialized-retained-resources',
                'failed_stage': 'continue-uninitialized-retained-resources',
                'completed_stages': [], 'completed_receipts': {}, 'rollback_executed': False})}
        self.config['releaseId'] = 'f' * 40

    def continuation_paginator(self, operation):
        if operation == 'describe_change_set':
            def paginate(**kwargs):
                request = self.clients['cloudformation'].create_change_set.call_args.kwargs
                return [{'Changes': self.update_changes if request['ChangeSetType'] == 'UPDATE' else self.changes}]
            return SimpleNamespace(paginate=paginate)
        return super().continuation_paginator(operation)

    def continuation_waiter(self, name):
        if name == 'stack_import_complete':
            actual = super().continuation_waiter(name)
            def imported(**kwargs):
                request = self.clients['cloudformation'].execute_change_set.call_args.kwargs
                assert request['ChangeSetName'] == f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:changeSet/import/fixture'
                actual.wait(**kwargs)
            return SimpleNamespace(wait=imported)
        if name != 'stack_update_complete':
            return super().continuation_waiter(name)
        def wait(**kwargs):
            cf = self.clients['cloudformation']
            request = cf.create_change_set.call_args.kwargs
            assert cf.execute_change_set.call_args.kwargs['ChangeSetName'] == (
                f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:changeSet/update/fixture')
            template = json.loads(request['TemplateBody'])
            resource = template['Resources']['PrivateB']
            props = resource['Properties']
            self.current_template = deepcopy(template)
            self.status = 'UPDATE_COMPLETE'
            self.graph['PrivateB'] = self.repaired_subnet_id
            self.current_rows.append({'LogicalResourceId': 'PrivateB', 'ResourceType': 'AWS::EC2::Subnet',
                'PhysicalResourceId': self.repaired_subnet_id, 'ResourceStatus': 'CREATE_COMPLETE'})
            self.live_subnets.append({'SubnetId': self.repaired_subnet_id, 'VpcId': props['VpcId'],
                'OwnerId': ACCOUNT,
                'State': 'available', 'CidrBlock': props['CidrBlock'], 'MapPublicIpOnLaunch': props['MapPublicIpOnLaunch'],
                'AssignIpv6AddressOnCreation': props['AssignIpv6AddressOnCreation'],
                'AvailabilityZone': props['AvailabilityZone'], 'Tags': deepcopy(props['Tags']) + [
                    {'Key': 'aws:cloudformation:stack-id', 'Value': NEW_STACK},
                    {'Key': 'aws:cloudformation:logical-id', 'Value': 'PrivateB'}],
                'Ipv6CidrBlockAssociationSet': [{'Ipv6CidrBlock': props['Ipv6CidrBlock'],
                    'Ipv6CidrBlockState': {'State': 'associated'}}]})
            token = cf.execute_change_set.call_args.kwargs['ClientRequestToken']
            timestamp = datetime.now(timezone.utc)
            self.current_events += [{'LogicalResourceId': logical, 'ResourceType': kind, 'PhysicalResourceId': physical,
                'ResourceStatus': status, 'Timestamp': timestamp, 'ClientRequestToken': token}
                for logical, kind, physical, status in ((recovery.STACK, 'AWS::CloudFormation::Stack', NEW_STACK, 'UPDATE_IN_PROGRESS'),
                    ('PrivateB', 'AWS::EC2::Subnet', self.repaired_subnet_id, 'CREATE_COMPLETE'))]
        return SimpleNamespace(wait=wait)

    def adopt(self, template):
        previous = {row['LogicalResourceId']: deepcopy(row) for row in self.current_rows}
        super().adopt(template)
        for row in self.current_rows:
            logical = row['LogicalResourceId']
            if logical in recovery.DATABASE_IMPORT_IDS:
                row['ResourceStatus'] = 'IMPORT_COMPLETE'
            else:
                row['ResourceStatus'] = previous[logical]['ResourceStatus']

    def modify_membership(self, **kwargs):
        self.subnet_group['Subnets'] = [{'SubnetIdentifier': identifier, 'SubnetStatus': 'Active',
            'SubnetAvailabilityZone': {'Name': next(row['AvailabilityZone'] for row in self.live_subnets
                                                   if row['SubnetId'] == identifier)}}
            for identifier in kwargs['SubnetIds']]
        return {'DBSubnetGroup': self.subnet_group}


class SubnetRepairContinuationTest(unittest.TestCase):
    def plan(self, cloud):
        source, digest = cloud.write_bundle()
        with patch.object(recovery, '_historical_builder', return_value=build_template):
            return recovery.uninitialized_continuation_plan(cloud.aws, cloud.config, source, digest)

    def run_repair(self, cloud, directory):
        source, digest = cloud.write_bundle()
        journal = Path(directory) / 'repaired.json'
        with patch.object(recovery, '_historical_builder', return_value=build_template):
            result = recovery.continue_uninitialized(cloud.aws, cloud.config, journal, source, digest)
        return result, json.loads(journal.read_text())

    def expected_subnet(self, cloud):
        return {'Type': 'AWS::EC2::Subnet', 'DeletionPolicy': 'Retain', 'UpdateReplacePolicy': 'Retain',
            'Properties': {'VpcId': cloud.graph['Network'], 'AvailabilityZone': REGION + 'b',
                'CidrBlock': '10.76.1.0/24', 'Ipv6CidrBlock': '2600:1f16:1d94:dd01::/64',
                'AssignIpv6AddressOnCreation': True, 'MapPublicIpOnLaunch': False,
                'Tags': cloud.template['Resources']['PrivateB']['Properties']['Tags']}}

    def test_authenticated_repair_adds_only_missing_private_subnet_then_preserves_database_and_imports_nine(self):
        with tempfile.TemporaryDirectory() as directory:
            cloud = RepairContinuationCloud(directory)
            original_ids = deepcopy(cloud.graph)
            original_template = deepcopy(cloud.current_template)
            original_group_arn = cloud.subnet_group['DBSubnetGroupArn']
            original_cluster = deepcopy(cloud.cluster)
            original_writer = deepcopy(cloud.writer)
            self.plan(cloud)
            cloud.no_mutations(self)
            result, journal = self.run_repair(cloud, directory)
            cf, rds = cloud.clients['cloudformation'], cloud.clients['rds']
            requests = [call.kwargs for call in cf.create_change_set.call_args_list]
            self.assertEqual([request['ChangeSetType'] for request in requests], ['UPDATE', 'IMPORT'])
            update = json.loads(requests[0]['TemplateBody'])
            self.assertEqual(set(update['Resources']), set(original_template['Resources']) | {'PrivateB'})
            self.assertEqual({name: update['Resources'][name] for name in original_template['Resources']},
                             original_template['Resources'])
            self.assertEqual(update['Resources']['PrivateB'], self.expected_subnet(cloud))
            self.assertTrue(all('Tags' not in request for request in requests))
            self.assertEqual({item['LogicalResourceId'] for item in requests[1]['ResourcesToImport']},
                             recovery.DATABASE_IMPORT_IDS.keys())
            self.assertEqual(len(cloud.current_rows), 25)
            actual = {row['LogicalResourceId']: row['PhysicalResourceId'] for row in cloud.current_rows}
            self.assertEqual({name: actual[name] for name in original_ids}, original_ids)
            self.assertEqual(actual['PrivateB'], cloud.repaired_subnet_id)
            rds.modify_db_subnet_group.assert_called_once_with(DBSubnetGroupName=original_ids['DatabaseSubnets'],
                SubnetIds=[original_ids['PrivateA'], cloud.repaired_subnet_id])
            self.assertEqual(cloud.subnet_group['DBSubnetGroupArn'], original_group_arn)
            for key in ('DBClusterArn', 'DbClusterResourceId', 'EngineVersion', 'KmsKeyId', 'MasterUserSecret',
                        'StorageEncrypted', 'DeletionProtection', 'Status', 'DBSubnetGroup'):
                self.assertEqual(cloud.cluster[key], original_cluster[key])
            for key in ('DBInstanceArn', 'DbiResourceId', 'EngineVersion', 'KmsKeyId', 'PubliclyAccessible',
                        'DBInstanceStatus', 'AvailabilityZone', 'DBClusterIdentifier'):
                self.assertEqual(cloud.writer[key], original_writer[key])
            self.assertEqual(result['repaired_private_b_resource'], self.expected_subnet(cloud))
            self.assertEqual(result['repaired_private_b_physical_id'], cloud.repaired_subnet_id)
            self.assertEqual(journal['repaired_private_b_physical_id'], cloud.repaired_subnet_id)
            self.assertTrue(journal['private_b_change_set_id'].startswith(f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:changeSet/'))
            self.assertTrue(journal['private_b_client_request_token'])
            self.assertTrue(journal['private_b_requested_at'])
            self.assertEqual(cf.execute_change_set.call_args_list[0].kwargs['ClientRequestToken'],
                             journal['private_b_client_request_token'])
            self.assertEqual([call.kwargs['ChangeSetName'] for call in cf.execute_change_set.call_args_list],
                             [journal['private_b_change_set_id'], journal['import_change_set_id']])
            self.assertTrue(result['already_adopted'])
            self.assertFalse(result['journal_established'])
            self.assertFalse(result['actual_resources_deleted'])
            cf.delete_stack.assert_not_called()
            rds.delete_db_cluster.assert_not_called()
            rds.delete_db_instance.assert_not_called()
            cloud.clients['secretsmanager'].get_secret_value.assert_not_called()

    def test_completed_import_accepts_only_preexisting_private_b_create_complete_and_preserves_strict_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            cloud = RepairContinuationCloud(directory)
            evidence, journal = self.run_repair(cloud, directory)
            source, digest = cloud.write_bundle()
            rows = {row['LogicalResourceId']: row for row in cloud.current_rows}
            self.assertEqual(len(rows), 25)
            self.assertEqual(rows['PrivateB']['ResourceStatus'], 'CREATE_COMPLETE')
            self.assertTrue(all(rows[name]['ResourceStatus'] == 'IMPORT_COMPLETE'
                                for name in recovery.DATABASE_IMPORT_IDS))
            self.assertTrue(all(rows[name]['ResourceStatus'] == 'UPDATE_COMPLETE' for name in cloud.physical))
            with patch.object(recovery, '_historical_builder', return_value=build_template):
                final = recovery._repair_plan_refresh(cloud.aws, cloud.config, source, digest, evidence)
                self.assertTrue(final['already_adopted'])
                self.assertEqual(final['repair_state'], 'adopted')
                self.assertEqual(final['repaired_private_b_physical_id'], cloud.repaired_subnet_id)
                for logical in evidence['retained_physical_ids']:
                    original = rows[logical]['ResourceStatus']
                    rows[logical]['ResourceStatus'] = 'CREATE_COMPLETE'
                    with self.subTest(logical=logical), self.assertRaises(Gate):
                        recovery._repair_plan_refresh(cloud.aws, cloud.config, source, digest, evidence)
                    rows[logical]['ResourceStatus'] = original
                for status in ('CREATE_IN_PROGRESS', 'CREATE_FAILED', 'DELETE_SKIPPED', 'UPDATE_IN_PROGRESS',
                               'IMPORT_IN_PROGRESS', 'DELETE_COMPLETE'):
                    rows['PrivateB']['ResourceStatus'] = status
                    with self.subTest(private_b_status=status), self.assertRaises(Gate):
                        recovery._repair_plan_refresh(cloud.aws, cloud.config, source, digest, evidence)
                rows['PrivateB']['ResourceStatus'] = 'CREATE_COMPLETE'
                rows['PrivateB']['PhysicalResourceId'] = 'different-managed-subnet'
                with self.assertRaises(Gate):
                    recovery._repair_plan_refresh(cloud.aws, cloud.config, source, digest, evidence)
                rows['PrivateB']['PhysicalResourceId'] = cloud.repaired_subnet_id
                event = next(event for event in cloud.current_events if event.get('LogicalResourceId') == 'PrivateB'
                             and event.get('ResourceStatus') == 'CREATE_COMPLETE')
                event['ClientRequestToken'] = 'different-request'
                with self.assertRaises(Gate):
                    recovery._repair_plan_refresh(cloud.aws, cloud.config, source, digest, evidence)
            self.assertEqual(cloud.clients['cloudformation'].create_change_set.call_count, 2)
            self.assertEqual(cloud.clients['cloudformation'].execute_change_set.call_count, 2)
            cloud.clients['rds'].modify_db_subnet_group.assert_called_once()

    def test_import_rollback_requires_authenticated_previous_packet_and_zero_completed_stages(self):
        for mode in ('missing-packet', 'unknown-packet-field', 'source-sha', 'prior-phase',
                     'completed-stage', 'completed-receipt', 'rollback-inferred', 'different-authority'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = RepairContinuationCloud(directory)
                packet = cloud.bundle['previous_recovery']
                if mode == 'missing-packet':
                    del cloud.bundle['previous_recovery']
                elif mode == 'unknown-packet-field':
                    packet['unexpected'] = 'field'
                elif mode in ('source-sha', 'prior-phase', 'different-authority'):
                    record = json.loads(packet['continuation_raw'])
                    if mode == 'source-sha':
                        record['source_bundle_sha256'] = '0' * 64
                    elif mode == 'prior-phase':
                        record['failed_phase'] = 'private-b-add-executing'
                    else:
                        record['database_snapshot']['cluster_resource_id'] = 'cluster-other-authority'
                    packet['continuation_raw'] = json.dumps(record)
                else:
                    state = json.loads(packet['deployment_state_raw'])
                    if mode == 'completed-stage':
                        state['completed_stages'] = ['bootstrap']
                    elif mode == 'completed-receipt':
                        state['completed_receipts'] = {'bootstrap.json': {'sha256': 'a' * 64}}
                    else:
                        state['rollback_executed'] = True
                    packet['deployment_state_raw'] = json.dumps(state)
                with self.assertRaises(Gate):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_private_subnet_update_rejects_any_other_change_before_execution_or_rds_membership_change(self):
        for mode in ('Modify', 'Remove', 'replacement', 'wrong-type', 'extra-resource', 'duplicate'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = RepairContinuationCloud(directory)
                change = cloud.update_changes[0]['ResourceChange']
                if mode in ('Modify', 'Remove'):
                    change['Action'] = mode
                elif mode == 'replacement':
                    change['Replacement'] = 'True'
                elif mode == 'wrong-type':
                    change['ResourceType'] = 'AWS::RDS::DBCluster'
                elif mode == 'extra-resource':
                    cloud.update_changes.append({'ResourceChange': {'Action': 'Add',
                        'LogicalResourceId': 'Other', 'ResourceType': 'AWS::EC2::Subnet'}})
                else:
                    cloud.update_changes.append(deepcopy(cloud.update_changes[0]))
                with self.assertRaises(Gate):
                    self.run_repair(cloud, directory)
                cloud.clients['cloudformation'].execute_change_set.assert_not_called()
                cloud.clients['rds'].modify_db_subnet_group.assert_not_called()

    def test_ambiguous_or_foreign_subnet_geometry_and_wrong_database_zone_block_before_update(self):
        for mode in ('existing-ipv4', 'existing-ipv6', 'wrong-old-zone', 'writer-zone', 'group-arn'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = RepairContinuationCloud(directory)
                if mode in ('existing-ipv4', 'existing-ipv6'):
                    other = deepcopy(cloud.subnet)
                    other['SubnetId'] = 'subnet-unclaimed'
                    other['CidrBlock'] = '10.76.1.0/24' if mode == 'existing-ipv4' else '10.76.9.0/24'
                    if mode == 'existing-ipv6':
                        other['Ipv6CidrBlockAssociationSet'][0]['Ipv6CidrBlock'] = '2600:1f16:1d94:dd01::/64'
                    cloud.live_subnets.append(other)
                elif mode == 'wrong-old-zone':
                    cloud.subnet_group['Subnets'][1]['SubnetAvailabilityZone']['Name'] = REGION + 'a'
                elif mode == 'writer-zone':
                    cloud.writer['AvailabilityZone'] = REGION + 'b'
                else:
                    cloud.subnet_group['DBSubnetGroupArn'] = f'arn:aws:rds:{REGION}:000000000000:subgrp:foreign'
                with self.assertRaises(Gate):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_preserved_subnet_update_requires_token_bound_history_and_exact_private_geometry(self):
        for mode in ('missing-token', 'wrong-token', 'public-subnet', 'wrong-zone', 'wrong-ipv6',
                     'changed-authority', 'journal-written', 'owner-id', 'stack-tag', 'logical-tag', 'duplicate-update'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = RepairContinuationCloud(directory)
                original = cloud.continuation_waiter
                def waiter(name):
                    actual = original(name)
                    def wait(**kwargs):
                        actual.wait(**kwargs)
                        if name != 'stack_update_complete':
                            return
                        if mode in ('missing-token', 'wrong-token'):
                            for event in cloud.current_events:
                                if event.get('PhysicalResourceId') == cloud.repaired_subnet_id:
                                    if mode == 'missing-token':
                                        event.pop('ClientRequestToken')
                                    else:
                                        event['ClientRequestToken'] = 'different-request'
                        elif mode == 'changed-authority':
                            cloud.cluster['DbClusterResourceId'] = 'cluster-other-authority'
                        elif mode == 'journal-written':
                            cloud.clients['s3'].list_object_versions.return_value = {
                                'Versions': [{'Key': 'unexpected-first-anchor'}]}
                        elif mode == 'duplicate-update':
                            cloud.current_events.append(deepcopy(next(event for event in cloud.current_events
                                if event.get('ResourceStatus') == 'UPDATE_IN_PROGRESS' and event.get('ClientRequestToken'))))
                        else:
                            subnet = next(row for row in cloud.live_subnets if row['SubnetId'] == cloud.repaired_subnet_id)
                            if mode == 'public-subnet':
                                subnet['MapPublicIpOnLaunch'] = True
                            elif mode == 'wrong-zone':
                                subnet['AvailabilityZone'] = REGION + 'a'
                            elif mode == 'owner-id':
                                subnet['OwnerId'] = '000000000000'
                            elif mode in ('stack-tag', 'logical-tag'):
                                key = 'aws:cloudformation:stack-id' if mode == 'stack-tag' else 'aws:cloudformation:logical-id'
                                next(tag for tag in subnet['Tags'] if tag['Key'] == key)['Value'] = 'different-owner'
                            else:
                                subnet['Ipv6CidrBlockAssociationSet'][0]['Ipv6CidrBlock'] = '2600:1f16:1d94:dd02::/64'
                    return SimpleNamespace(wait=wait)
                cloud.clients['cloudformation'].get_waiter.side_effect = waiter
                with self.assertRaises(Gate):
                    self.run_repair(cloud, directory)
                cloud.clients['rds'].modify_db_subnet_group.assert_not_called()
                self.assertEqual(cloud.clients['cloudformation'].execute_change_set.call_count, 1)

    def test_membership_change_cannot_change_group_or_database_authority_before_import(self):
        for mode in ('group-arn', 'cluster-id', 'writer-id', 'master-secret', 'encryption-key', 'engine'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = RepairContinuationCloud(directory)
                original = cloud.modify_membership
                def modify(**kwargs):
                    response = original(**kwargs)
                    if mode == 'group-arn':
                        cloud.subnet_group['DBSubnetGroupArn'] = 'different-group-arn'
                    elif mode == 'cluster-id':
                        cloud.cluster['DbClusterResourceId'] = 'cluster-other-authority'
                    elif mode == 'writer-id':
                        cloud.writer['DbiResourceId'] = 'db-other-authority'
                    elif mode == 'master-secret':
                        cloud.cluster['MasterUserSecret']['SecretArn'] = f'arn:aws:secretsmanager:{REGION}:{ACCOUNT}:secret:rds!cluster-other'
                    elif mode == 'encryption-key':
                        cloud.cluster['KmsKeyId'] = 'different-key'
                    else:
                        cloud.cluster['EngineVersion'] = '16.16'
                    return response
                cloud.clients['rds'].modify_db_subnet_group.side_effect = modify
                with self.assertRaises(Gate):
                    self.run_repair(cloud, directory)
                requests = [call.kwargs for call in cloud.clients['cloudformation'].create_change_set.call_args_list]
                self.assertEqual([request['ChangeSetType'] for request in requests], ['UPDATE'])
                cloud.clients['cloudformation'].delete_stack.assert_not_called()

    def test_authenticated_restart_uses_existing_subnet_binding_or_completed_import_without_duplicate_add(self):
        for boundary in ('T16', 'group-converged', 'T25'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                cloud = RepairContinuationCloud(directory)
                started = datetime.now(timezone.utc)
                cf, rds = cloud.clients['cloudformation'], cloud.clients['rds']
                create_change_set = cf.create_change_set.side_effect
                if boundary == 'T16':
                    rds.modify_db_subnet_group.side_effect = absent('AccessDenied')
                elif boundary == 'group-converged':
                    def create(**kwargs):
                        if kwargs['ChangeSetType'] == 'IMPORT':
                            raise absent('AccessDenied')
                        return create_change_set(**kwargs)
                    cf.create_change_set.side_effect = create
                else:
                    original = cloud.continuation_waiter
                    def waiter(name):
                        actual = original(name)
                        def wait(**kwargs):
                            actual.wait(**kwargs)
                            if name == 'stack_import_complete':
                                raise RuntimeError('Unit-test wait lost completion response')
                        return SimpleNamespace(wait=wait)
                    cf.get_waiter.side_effect = waiter
                with self.assertRaises((ClientError, RuntimeError)):
                    self.run_repair(cloud, directory)
                completed = datetime.now(timezone.utc)
                failed = json.loads((Path(directory) / 'repaired.json').read_text())
                self.assertFalse(failed['journal_established'])
                self.assertEqual(len(cloud.current_rows), 25 if boundary == 'T25' else 16)
                if boundary == 'group-converged':
                    self.assertEqual(failed['failed_phase'], 'surviving-database-import-requesting')
                    self.assertEqual({row['SubnetIdentifier'] for row in cloud.subnet_group['Subnets']},
                                     {cloud.graph['PrivateA'], cloud.repaired_subnet_id})
                cloud.seal_failed_attempt(failed, started, completed)
                rds.modify_db_subnet_group.side_effect = cloud.modify_membership
                cf.get_waiter.side_effect = cloud.continuation_waiter
                cf.create_change_set.side_effect = create_change_set
                update_count = sum(call.kwargs['ChangeSetType'] == 'UPDATE' for call in cf.create_change_set.call_args_list)
                imports_before = sum(call.kwargs['ChangeSetType'] == 'IMPORT' for call in cf.create_change_set.call_args_list)
                membership_before = rds.modify_db_subnet_group.call_count
                source, digest = cloud.write_bundle()
                with patch.object(recovery, '_historical_builder', return_value=build_template):
                    result = recovery.continue_uninitialized(cloud.aws, cloud.config,
                        Path(directory) / 'restarted.json', source, digest)
                self.assertEqual(sum(call.kwargs['ChangeSetType'] == 'UPDATE' for call in cf.create_change_set.call_args_list),
                                 update_count)
                self.assertEqual(sum(call.kwargs['ChangeSetType'] == 'IMPORT' for call in cf.create_change_set.call_args_list),
                                 imports_before + (0 if boundary == 'T25' else 1))
                self.assertEqual(rds.modify_db_subnet_group.call_count, membership_before + (1 if boundary == 'T16' else 0))
                self.assertEqual(len(cloud.current_rows), 25)
                self.assertEqual({item['LogicalResourceId'] for item in cf.create_change_set.call_args.kwargs['ResourcesToImport']},
                                 recovery.DATABASE_IMPORT_IDS.keys())
                self.assertEqual(result['repaired_private_b_physical_id'], cloud.repaired_subnet_id)
                self.assertTrue(result['already_adopted'])
                self.assertFalse(result['journal_established'])

    def test_sealed_resume_cannot_extend_old_request_window_during_current_refresh(self):
        for status in ('UPDATE_IN_PROGRESS', 'CREATE_COMPLETE'):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                cloud = RepairContinuationCloud(directory)
                started = datetime.now(timezone.utc)
                cloud.clients['rds'].modify_db_subnet_group.side_effect = absent('AccessDenied')
                with self.assertRaises(ClientError):
                    self.run_repair(cloud, directory)
                completed = datetime.now(timezone.utc)
                failed = json.loads((Path(directory) / 'repaired.json').read_text())
                cloud.seal_failed_attempt(failed, started, completed)
                source, digest = cloud.write_bundle()
                with patch.object(recovery, '_historical_builder', return_value=build_template):
                    resumed = recovery.uninitialized_continuation_plan(cloud.aws, cloud.config, source, digest)
                    self.assertEqual(resumed['private_b_requested_at'], failed['private_b_requested_at'])
                    token = failed['private_b_client_request_token']
                    event = next(event for event in cloud.current_events if event.get('ClientRequestToken') == token
                                 and event.get('ResourceStatus') == status)
                    event['Timestamp'] = completed + timedelta(microseconds=1)
                    self.assertLess(event['Timestamp'], datetime.now(timezone.utc))
                    with self.assertRaises(Gate):
                        recovery._repair_plan_refresh(cloud.aws, cloud.config, source, digest, resumed)
                    with self.assertRaises(Gate):
                        recovery.uninitialized_continuation_plan(cloud.aws, cloud.config, source, digest)
                self.assertEqual(cloud.clients['cloudformation'].execute_change_set.call_count, 1)
                self.assertEqual(cloud.clients['rds'].modify_db_subnet_group.call_count, 1)


class UninitializedContinuationTest(unittest.TestCase):
    def plan(self, cloud):
        path, digest = cloud.write_bundle()
        with patch.object(recovery, '_historical_builder', return_value=build_template) as builder:
            result = recovery.uninitialized_continuation_plan(cloud.aws, cloud.config, path, digest)
            builder.assert_called_once_with(cloud.failed_release)
        return result

    def test_read_only_plan_preserves_observed_graph_and_composite_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            cloud = ContinuationCloud(directory)
            # Historic reconstruction remains exact when current desired budget changes.
            cloud.config['monthlyBudgetUsd'] = 100
            result = self.plan(cloud)
            self.assertEqual(result['retained_physical_ids'], cloud.graph)
            self.assertEqual(len(result['import_template']['Resources']), 24)
            self.assertEqual(result['database_engine_version'], '16.15')
            self.assertEqual(result['import_template']['Resources']['DatabaseSubnets']['Properties']['SubnetIds'],
                [cloud.graph['PrivateA'], cloud.deleted_subnet])
            ipv6 = next(row for row in result['resources_to_import'] if row['LogicalResourceId'] == 'NetworkIpv6')
            self.assertEqual(ipv6['ResourceIdentifier'], {'Id': cloud.graph['NetworkIpv6'], 'VpcId': cloud.graph['Network']})
            self.assertEqual(len(result['resources_to_import']), 9)
            self.assertEqual(result['managed_import_bindings'], {
                name: cloud.graph[name] for name in recovery.DATABASE_IMPORT_IDS if name != 'DatabaseWriter'})
            self.assertFalse(result['journal_established'])
            cloud.no_mutations(self)

    def test_detached_database_and_subnet_group_or_all_targets_still_import_the_full_live_graph(self):
        for detached in ({'Database', 'DatabaseSubnets'},
                         {'Database', 'DatabaseSubnets', 'DatabaseParameters'},
                         recovery.DATABASE_IMPORT_IDS.keys() - {'DatabaseWriter'}):
            with self.subTest(detached=detached), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                cloud.current_rows = [row for row in cloud.current_rows if row['LogicalResourceId'] not in detached]
                self.assertEqual(len(cloud.current_rows), 23 - len(detached))
                before = self.plan(cloud)
                expected_bindings = {name: cloud.graph[name] for name in recovery.DATABASE_IMPORT_IDS
                                     if name not in detached | {'DatabaseWriter'}}
                self.assertEqual(before['managed_import_bindings'], expected_bindings)
                self.assertEqual(before['retained_physical_ids'], cloud.graph)
                self.assertEqual(len(before['resources_to_import']), 9)
                cloud.no_mutations(self)
                source, digest = cloud.write_bundle()
                original_bytes = source.read_bytes()
                cf = cloud.clients['cloudformation']
                journal = Path(directory) / 'continued.json'
                with patch.object(recovery, '_historical_builder', return_value=build_template):
                    after = recovery.continue_uninitialized(cloud.aws, cloud.config,
                        journal, source, digest)
                self.assertEqual(len(cloud.current_rows), 24)
                self.assertEqual(after['retained_physical_ids'], cloud.graph)
                self.assertEqual(after['managed_import_bindings'], {
                    name: cloud.graph[name] for name in recovery.DATABASE_IMPORT_IDS})
                self.assertEqual(json.loads(journal.read_text())['managed_import_bindings'], after['managed_import_bindings'])
                self.assertEqual(after['database_snapshot'], before['database_snapshot'])
                self.assertEqual(after['canonical_import_template_sha256'], before['canonical_import_template_sha256'])
                self.assertEqual(source.read_bytes(), original_bytes)
                self.assertEqual({row['LogicalResourceId'] for row in cf.create_change_set.call_args.kwargs['ResourcesToImport']},
                                 recovery.DATABASE_IMPORT_IDS.keys())
                cf.execute_change_set.assert_called_once()
                cf.delete_stack.assert_not_called()
                self.assertFalse(after['journal_established'])

    def test_missing_cloudformation_binding_requires_precise_absence_for_that_logical_id(self):
        invalid = [('AccessDeniedException', 'Stack does not contain resource Database'),
                   ('ValidationError', 'Stack does not contain resource DatabaseSubnets'),
                   ('ValidationError', 'Stack does not contain resource DatabaseWriter'),
                   ('ValidationError', 'Stack does not exist'),
                   ('ValidationError', 'Database request is malformed')]
        for code, message in invalid:
            with self.subTest(code=code, message=message), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                cloud.current_rows = [row for row in cloud.current_rows if row['LogicalResourceId'] != 'Database']
                original = cloud.describe_current_resource
                def describe(**kwargs):
                    if kwargs['LogicalResourceId'] == 'Database':
                        raise ClientError({'Error': {'Code': code, 'Message': message}}, 'DescribeStackResource')
                    return original(**kwargs)
                cloud.clients['cloudformation'].describe_stack_resource.side_effect = describe
                with self.assertRaises(ClientError):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_resource_omitted_from_inventory_but_still_bound_to_stack_is_not_detached(self):
        with tempfile.TemporaryDirectory() as directory:
            cloud = ContinuationCloud(directory)
            database = next(row for row in cloud.current_rows if row['LogicalResourceId'] == 'Database')
            cloud.current_rows.remove(database)
            original = cloud.describe_current_resource
            cloud.clients['cloudformation'].describe_stack_resource.side_effect = lambda **kwargs: (
                {'StackResourceDetail': deepcopy(database)} if kwargs['LogicalResourceId'] == 'Database'
                else original(**kwargs))
            with self.assertRaises(Gate):
                self.plan(cloud)
            cloud.no_mutations(self)

    def test_detached_targets_must_still_exist_in_rds_and_ec2(self):
        missing = [('rds', 'describe_db_clusters', 'DBClusterNotFoundFault'),
                   ('rds', 'describe_db_instances', 'DBInstanceNotFound'),
                   ('rds', 'describe_db_subnet_groups', 'DBSubnetGroupNotFoundFault'),
                   ('rds', 'describe_db_cluster_parameter_groups', 'DBParameterGroupNotFound'),
                   ('ec2', 'describe_vpcs', 'InvalidVpcID.NotFound'),
                   ('ec2', 'describe_subnets', 'InvalidSubnetID.NotFound'),
                   ('ec2', 'describe_security_groups', 'InvalidGroup.NotFound')]
        for service, operation, code in missing:
            with self.subTest(service=service, operation=operation), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                cloud.current_rows = [row for row in cloud.current_rows if row['LogicalResourceId'] in cloud.physical]
                getattr(cloud.clients[service], operation).side_effect = absent(code)
                with self.assertRaises(ClientError):
                    self.plan(cloud)
                cloud.no_mutations(self)
        with tempfile.TemporaryDirectory() as directory:
            cloud = ContinuationCloud(directory)
            cloud.current_rows = [row for row in cloud.current_rows if row['LogicalResourceId'] in cloud.physical]
            cloud.vpc['Ipv6CidrBlockAssociationSet'] = []
            with self.assertRaises(Gate):
                self.plan(cloud)
            cloud.no_mutations(self)

    def test_each_target_requires_one_exact_failed_run_creation_event_even_when_all_are_detached(self):
        logical_ids = recovery.DATABASE_IMPORT_IDS.keys() - {'DatabaseWriter'}
        for logical in logical_ids:
            for mode in ('missing', 'duplicate', 'conflicting', 'wrong-type', 'outside-run', 'empty-id'):
                with self.subTest(logical=logical, mode=mode), tempfile.TemporaryDirectory() as directory:
                    cloud = ContinuationCloud(directory)
                    cloud.current_rows = [row for row in cloud.current_rows if row['LogicalResourceId'] in cloud.physical]
                    created = next(row for row in cloud.current_events if row['LogicalResourceId'] == logical
                                   and row['ResourceStatus'] == 'CREATE_COMPLETE')
                    if mode == 'missing':
                        cloud.current_events.remove(created)
                    elif mode in ('duplicate', 'conflicting'):
                        other = deepcopy(created)
                        if mode == 'conflicting':
                            other['PhysicalResourceId'] = 'different-source-identity'
                        cloud.current_events.append(other)
                    else:
                        field, value = {'wrong-type': ('ResourceType', 'AWS::S3::Bucket'),
                            'outside-run': ('Timestamp', '2019-01-01T00:02:00Z'),
                            'empty-id': ('PhysicalResourceId', '')}[mode]
                        created[field] = value
                    with self.assertRaises(Gate):
                        self.plan(cloud)
                    cloud.no_mutations(self)

    def test_detached_writer_requires_exact_unique_skipped_history_in_failed_run(self):
        for mode in ('missing', 'duplicate', 'wrong-name', 'wrong-type', 'outside-run'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                event = next(row for row in cloud.current_events if row['LogicalResourceId'] == 'DatabaseWriter')
                if mode == 'missing':
                    cloud.current_events.remove(event)
                elif mode == 'duplicate':
                    cloud.current_events.append(deepcopy(event))
                else:
                    field, value = {'wrong-name': ('PhysicalResourceId', 'different-writer'),
                        'wrong-type': ('ResourceType', 'AWS::RDS::DBCluster'),
                        'outside-run': ('Timestamp', '2019-01-01T00:04:00Z')}[mode]
                    event[field] = value
                with self.assertRaises(Gate):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_subset_inventory_still_requires_all_original_authorities_and_exact_source_bindings(self):
        for mode in ('original-missing', 'unexplained', 'duplicate-original', 'duplicate-target',
                     'target-source-id', 'target-type', 'target-status', 'writer-bound'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                target = next(row for row in cloud.current_rows if row['LogicalResourceId'] == 'Database')
                if mode == 'original-missing':
                    cloud.current_rows.pop(0)
                elif mode == 'unexplained':
                    cloud.current_rows.append({'LogicalResourceId': 'Unexplained', 'ResourceType': 'AWS::SQS::Queue',
                        'ResourceStatus': 'CREATE_COMPLETE', 'PhysicalResourceId': 'unexplained-queue'})
                elif mode == 'duplicate-original':
                    cloud.current_rows.append(deepcopy(cloud.current_rows[0]))
                elif mode == 'duplicate-target':
                    cloud.current_rows.append(deepcopy(target))
                elif mode == 'writer-bound':
                    cloud.current_rows.append({'LogicalResourceId': 'DatabaseWriter', 'ResourceType': 'AWS::RDS::DBInstance',
                        'ResourceStatus': 'CREATE_COMPLETE', 'PhysicalResourceId': cloud.graph['DatabaseWriter']})
                else:
                    field, value = {'target-source-id': ('PhysicalResourceId', 'different-source-identity'),
                        'target-type': ('ResourceType', 'AWS::RDS::DBInstance'),
                        'target-status': ('ResourceStatus', 'DELETE_FAILED')}[mode]
                    target[field] = value
                with self.assertRaises(Gate):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_completed_import_requires_all_twenty_four_resources(self):
        for missing in ('Database', 'DatabaseSubnets', 'DatabaseWriter', 'DataKey'):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                cloud.adopt(self.plan(cloud)['import_template'])
                cloud.current_rows = [row for row in cloud.current_rows if row['LogicalResourceId'] != missing]
                with self.assertRaises(Gate):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_binding_inventory_change_before_execution_blocks_import_even_with_unchanged_live_graph(self):
        for mode in ('detach', 'reattach'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                target = next(row for row in cloud.current_rows if row['LogicalResourceId'] == 'Database')
                if mode == 'reattach':
                    cloud.current_rows.remove(target)
                path, digest = cloud.write_bundle()
                def create(**kwargs):
                    if mode == 'detach':
                        cloud.current_rows.remove(target)
                    else:
                        cloud.current_rows.append(target)
                    return {'Id': 'fixture-import-change'}
                cf = cloud.clients['cloudformation']
                cf.create_change_set.side_effect = create
                evidence_path = Path(directory) / 'blocked.json'
                with self.assertRaises(Gate), patch.object(recovery, '_historical_builder', return_value=build_template):
                    recovery.continue_uninitialized(cloud.aws, cloud.config, evidence_path, path, digest)
                cf.execute_change_set.assert_not_called()
                cf.delete_stack.assert_not_called()
                evidence = json.loads(evidence_path.read_text())
                self.assertFalse(evidence['journal_established'])
                self.assertEqual(evidence['managed_import_bindings'].get('Database'),
                                 cloud.graph['Database'] if mode == 'detach' else None)

    def test_import_journal_and_existing_import_resume_preserve_every_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            cloud = ContinuationCloud(directory)
            source, digest = cloud.write_bundle()
            before = source.read_bytes()
            journal = Path(directory) / 'continued.json'
            def requesting(**kwargs):
                saved = json.loads(journal.read_text())
                self.assertEqual(saved['status'], 'surviving-database-import-requesting')
                self.assertEqual(saved['retained_physical_ids'], cloud.graph)
                self.assertEqual(journal.stat().st_mode & 0o777, 0o600)
                self.assertEqual(kwargs['ChangeSetType'], 'IMPORT')
                self.assertNotIn('Tags', kwargs)
                return {'Id': 'fixture-import-change'}
            cf = cloud.clients['cloudformation']
            cf.create_change_set.side_effect = requesting
            with patch.object(recovery, '_historical_builder', return_value=build_template):
                result = recovery.continue_uninitialized(cloud.aws, cloud.config, journal, source, digest)
                resumed = recovery.continue_uninitialized(cloud.aws, cloud.config,
                    Path(directory) / 'resumed.json', source, digest)
            self.assertEqual(result['status'], 'retained-uninitialized-database-adopted')
            self.assertEqual(resumed['retained_physical_ids'], cloud.graph)
            self.assertTrue(resumed['already_adopted'])
            self.assertEqual(source.read_bytes(), before)
            cf.create_change_set.assert_called_once()
            cf.execute_change_set.assert_called_once()
            cf.delete_stack.assert_not_called()
            cf.update_termination_protection.assert_not_called()
            for logical in recovery.DATABASE_IMPORT_IDS:
                self.assertEqual(result['import_template']['Resources'][logical]['DeletionPolicy'], 'Retain')
            cloud.clients['secretsmanager'].get_secret_value.assert_not_called()

    def test_invalid_bundle_never_reaches_cloud(self):
        changes = [('account', '000000000000'), ('failed_run_id', True), ('failed_run_attempt', 0),
            ('artifact_sha256', 'bad'), ('failed_run_completed_at', '2020-01-01T01:00:00'),
            ('failed_run_started_at', '2020-01-02T00:00:00Z'), ('unexpected', 'field')]
        for field, value in changes:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                cloud.bundle[field] = value
                path, digest = cloud.write_bundle()
                for client in cloud.clients.values():
                    client.reset_mock()
                with self.assertRaises(Gate):
                    recovery.uninitialized_continuation_plan(cloud.aws, cloud.config, path, digest)
                for client in cloud.clients.values():
                    self.assertEqual(client.mock_calls, [])

    def test_bundle_hash_and_first_bootstrap_boundary_fail_closed(self):
        for mode in ('wrong-hash', 'bootstrap-stage', 'bootstrap-receipt', 'gate-source', 'adoption-source'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                if mode in ('bootstrap-stage', 'bootstrap-receipt'):
                    state = json.loads(cloud.bundle['deployment_state_raw'])
                    if mode == 'bootstrap-stage':
                        state['completed_stages'].append('bootstrap')
                    else:
                        state['completed_receipts'] = {'bootstrap': {'ok': True}}
                    cloud.bundle['deployment_state_raw'] = json.dumps(state)
                elif mode in ('gate-source', 'adoption-source'):
                    field = 'gate_admission_raw' if mode == 'gate-source' else 'adoption_raw'
                    record = json.loads(cloud.bundle[field])
                    record['head_sha' if mode == 'gate-source' else 'source_manifest_sha256'] = 'f' * 64
                    cloud.bundle[field] = json.dumps(record)
                path, digest = cloud.write_bundle()
                with self.assertRaises(Gate), patch.object(recovery, '_historical_builder') as builder:
                    recovery.uninitialized_continuation_plan(cloud.aws, cloud.config, path,
                        '0' * 64 if mode == 'wrong-hash' else digest)
                builder.assert_not_called()
                cloud.no_mutations(self)

    def test_live_drift_absence_history_and_unstable_stack_block_before_import(self):
        mutations = {
            'cleanup': lambda c: setattr(c, 'status', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS'),
            'extra-resource': lambda c: c.current_rows.append(dict(c.current_rows[0])),
            'authority-id': lambda c: c.current_rows[0].update(PhysicalResourceId='changed'),
            'runtime-live': lambda c: setattr(c.clients['lambda'].get_function, 'side_effect', None),
            'journal-written': lambda c: c.clients['s3'].list_object_versions.configure_mock(
                return_value={'Versions': [{'Key': 'first-anchor'}]}),
            'pending-database': lambda c: c.cluster.update(PendingModifiedValues={'EngineVersion': '16.16'}),
            'pending-writer': lambda c: c.writer.update(PendingModifiedValues={'DBInstanceClass': 'other'}),
            'unapplied-tls': lambda c: c.cluster['DBClusterMembers'][0].update(DBClusterParameterGroupStatus='pending-reboot'),
            'wrong-key': lambda c: c.cluster.update(KmsKeyId='different'),
            'outside-run': lambda c: c.writer.update(InstanceCreateTime='2019-01-01T00:00:00Z'),
            'public-writer': lambda c: c.writer.update(PubliclyAccessible=True),
            'unexpected-rule': lambda c: c.groups[1]['IpPermissions'].append({'IpProtocol': '-1',
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}),
            'other-function-created': lambda c: c.current_events.append({'LogicalResourceId': 'ApiFunction',
                'ResourceStatus': 'CREATE_COMPLETE'}),
            'control-never-deleted': lambda c: setattr(c, 'current_events', [row for row in c.current_events
                if row.get('LogicalResourceId') != 'ControlFunction' or row.get('ResourceStatus') != 'DELETE_COMPLETE']),
            'unbound-update': lambda c: c.current_events[0].update(Timestamp='2019-01-01T00:00:00Z'),
            'actual-template-drift': lambda c: c.current_template['Resources']['DataKey']['Properties'].update(Enabled=False),
        }
        for mode, mutate in mutations.items():
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                mutate(cloud)
                with self.assertRaises(Gate):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_imported_writer_identity_and_complete_status_remain_authoritative(self):
        for mode in ('writer-id', 'create-status', 'template-drift'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                cloud.adopt(self.plan(cloud)['import_template'])
                if mode == 'writer-id':
                    next(row for row in cloud.current_rows if row['LogicalResourceId'] == 'DatabaseWriter').update(
                        PhysicalResourceId='different-existing-writer')
                elif mode == 'create-status':
                    cloud.current_rows[0]['ResourceStatus'] = 'CREATE_COMPLETE'
                else:
                    cloud.current_template['Resources']['Database']['DeletionPolicy'] = 'Snapshot'
                with self.assertRaises(Gate):
                    self.plan(cloud)
                cloud.no_mutations(self)

    def test_schema_or_change_set_add_modify_remove_never_executes(self):
        for mode in ('composite-alternative', 'missing-identifier', 'Add', 'Modify', 'Remove', 'replacement'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                cf = cloud.clients['cloudformation']
                if mode in ('composite-alternative', 'missing-identifier'):
                    original = cloud.continuation_summary
                    def summary(**kwargs):
                        result = original(**kwargs)
                        if 'DatabaseWriter' in json.loads(kwargs['TemplateBody'])['Resources']:
                            if mode == 'missing-identifier':
                                result['ResourceIdentifierSummaries'] = [row for row in result['ResourceIdentifierSummaries']
                                    if row['LogicalResourceIds'] != ['NetworkIpv6']]
                            else:
                                next(row for row in result['ResourceIdentifierSummaries']
                                    if row['LogicalResourceIds'] == ['NetworkIpv6'])['ResourceIdentifiers'] = ['Id', 'VpcId']
                        return result
                    cf.get_template_summary.side_effect = summary
                elif mode == 'replacement':
                    cloud.changes[0]['ResourceChange']['Replacement'] = 'True'
                else:
                    cloud.changes[0]['ResourceChange']['Action'] = mode
                path, digest = cloud.write_bundle()
                with self.assertRaises(Gate), patch.object(recovery, '_historical_builder', return_value=build_template):
                    recovery.continue_uninitialized(cloud.aws, cloud.config, Path(directory) / 'blocked.json', path, digest)
                cf.execute_change_set.assert_not_called()
                cf.delete_stack.assert_not_called()

    def test_cloudformation_ownership_rejection_has_protected_journal_and_no_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            cloud = ContinuationCloud(directory)
            path, digest = cloud.write_bundle()
            cf = cloud.clients['cloudformation']
            cf.create_change_set.side_effect = ClientError({'Error': {'Code': 'ValidationError',
                'Message': 'Resource already managed'}}, 'CreateChangeSet')
            evidence_path = Path(directory) / 'blocked.json'
            with self.assertRaises(ClientError), patch.object(recovery, '_historical_builder', return_value=build_template):
                recovery.continue_uninitialized(cloud.aws, cloud.config, evidence_path, path, digest)
            evidence = json.loads(evidence_path.read_text())
            self.assertEqual(evidence['failed_phase'], 'surviving-database-import-requesting')
            self.assertEqual(evidence['failure_operation'], 'CreateChangeSet')
            self.assertEqual(evidence['retained_physical_ids'], cloud.graph)
            self.assertFalse(evidence['journal_established'])
            self.assertNotIn('failure_message', evidence)
            cf.execute_change_set.assert_not_called()
            cf.delete_stack.assert_not_called()

    def test_changed_authority_before_execution_or_after_import_blocks_first_anchor(self):
        for phase in ('before-execution', 'after-import'):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as directory:
                cloud = ContinuationCloud(directory)
                path, digest = cloud.write_bundle()
                cf = cloud.clients['cloudformation']
                if phase == 'before-execution':
                    def create(**kwargs):
                        cloud.cluster['DbClusterResourceId'] = 'cluster-other-authority'
                        return {'Id': 'fixture-import-change'}
                    cf.create_change_set.side_effect = create
                else:
                    original_waiter = cloud.continuation_waiter
                    def waiter(name):
                        original = original_waiter(name)
                        def wait(**kwargs):
                            original.wait(**kwargs)
                            if name == 'stack_import_complete':
                                cloud.writer['DbiResourceId'] = 'db-other-authority'
                        return SimpleNamespace(wait=wait)
                    cf.get_waiter.side_effect = waiter
                evidence_path = Path(directory) / 'blocked.json'
                with self.assertRaises(Gate), patch.object(recovery, '_historical_builder', return_value=build_template):
                    recovery.continue_uninitialized(cloud.aws, cloud.config, evidence_path, path, digest)
                evidence = json.loads(evidence_path.read_text())
                self.assertFalse(evidence['journal_established'])
                self.assertFalse(evidence['actual_resources_deleted'])
                self.assertEqual(evidence['database_snapshot']['cluster_resource_id'], 'cluster-unique-fixture')
                if phase == 'before-execution':
                    cf.execute_change_set.assert_not_called()
                else:
                    cf.execute_change_set.assert_called_once()
                cf.delete_stack.assert_not_called()

    def test_post_stopped_verification_allows_in_place_runtime_change_but_never_db_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            cloud = ContinuationCloud(directory)
            evidence = self.plan(cloud)
            cloud.adopt(evidence['import_template'])
            cloud.status = 'UPDATE_COMPLETE'
            cloud.cluster['NetworkType'] = 'DUAL'
            outputs = {'ReleaseId': cloud.config['releaseId'], 'ActivateServices': 'false'}
            result = recovery.verify_continued_database(cloud.aws, cloud.config, outputs, evidence)
            self.assertTrue(result['first_anchor_still_requires_empty_sql'])
            for field in ('DbClusterResourceId', 'EngineVersion', 'MasterUserSecret'):
                original = deepcopy(cloud.cluster[field])
                cloud.cluster[field] = {'SecretArn': 'new-secret'} if field == 'MasterUserSecret' else 'different'
                with self.subTest(field=field), self.assertRaises(Gate):
                    recovery.verify_continued_database(cloud.aws, cloud.config, outputs, evidence)
                cloud.cluster[field] = original

    def test_historical_builder_supports_real_future_import_and_rejects_other_top_level_code(self):
        # Use repository source, including the real future import that originally
        # blocked f916 admission; historical source is never read from bundle JSON.
        source = Path(recovery.__file__).with_name('serverless_template.py').read_bytes()
        results = [SimpleNamespace(stdout=str(len(source)).encode()), SimpleNamespace(stdout=source)]
        with patch.object(recovery.subprocess, 'run', side_effect=results) as git:
            builder = recovery._historical_builder('f91674be10db91ededa853fad205868e717f668f')
        cloud = FakeCloud()
        self.assertEqual(builder({**cloud.config,
            'apiImageUri': cloud.template['Resources']['ApiFunction']['Properties']['Code']['ImageUri'],
            'workerImageUri': cloud.template['Resources']['WorkerFunction']['Properties']['Code']['ImageUri']}),
            build_template({**cloud.config,
                'apiImageUri': cloud.template['Resources']['ApiFunction']['Properties']['Code']['ImageUri'],
                'workerImageUri': cloud.template['Resources']['WorkerFunction']['Properties']['Code']['ImageUri']}))
        self.assertIn('f91674be10db91ededa853fad205868e717f668f:deploy/serverless_template.py', git.call_args.args[0])
        for malicious in (b'import os\ndef build_template(config): return {}',
                          b'from pathlib import Path\ndef build_template(config): return {}',
                          b'open("should-not-exist", "w")\ndef build_template(config): return {}'):
            with self.subTest(source=malicious), patch.object(recovery.subprocess, 'run', side_effect=[
                    SimpleNamespace(stdout=str(len(malicious)).encode()), SimpleNamespace(stdout=malicious)]), self.assertRaises(Gate):
                recovery._historical_builder('f' * 40)


if __name__ == '__main__':
    unittest.main()


class ResumeFixture:
    """Bind unit-test archive bytes to independently supplied provider metadata."""
    def __init__(self, directory, *, legacy=False):
        self.cloud = FakeCloud()
        self.manifest = recovery.initial_recovery_plan(self.cloud.aws, self.cloud.config)
        if legacy:
            self.manifest.pop('canonical_import_template_sha256', None)
        self.manifest.update(status='blocked-recovery-inspect-protected-journal-before-retry',
                             failed_phase='failed-stack-metadata-detached', failure_type='ClientError')
        self.directory = Path(directory)
        self.path = self.directory / 'original-recovery.json'
        self.archive = self.directory / 'trusted-fixture.zip'
        self.output = self.directory / 'resumed-recovery.json'
        self.proof = {'run_id': 12, 'artifact_id': 9, 'archive_path': str(self.archive)}
        repository = {'id': 42, 'full_name': recovery.REPOSITORY}
        self.run = {'id': 12, 'head_sha': self.manifest['release_id'], 'status': 'completed',
            'conclusion': 'failure', 'path': '.github/workflows/deploy-serverless.yml',
            'workflow_id': 77, 'run_attempt': 1, 'event': 'workflow_dispatch',
            'head_branch': 'main', 'repository': repository, 'head_repository': repository}
        self.workflow = {'id': 77, 'path': '.github/workflows/deploy-serverless.yml', 'state': 'active'}
        self.artifact = {'id': 9, 'expired': False,
            'name': f'serverless-deployment-{self.manifest["release_id"]}-12',
            'workflow_run': {'id': 12, 'head_sha': self.manifest['release_id'], 'head_branch': 'main',
                             'repository_id': 42, 'head_repository_id': 42}}
        self.write_archive()
        self.cloud.status = 'DELETE_COMPLETE'
        original = self.cloud.clients['cloudformation'].describe_stacks.side_effect
        def detached(**kwargs):
            if kwargs['StackName'] == recovery.STACK and self.cloud.status != 'IMPORT_COMPLETE':
                raise ClientError({'Error': {'Code': 'ValidationError',
                    'Message': 'Stack with id otgd-serverless-development does not exist'}}, 'DescribeStacks')
            return original(**kwargs)
        self.cloud.clients['cloudformation'].describe_stacks.side_effect = detached

    def write_archive(self, *, extra_entries=None, manifest_bytes=None):
        raw = (json.dumps(self.manifest, sort_keys=True, indent=2) + '\n').encode()
        self.path.write_bytes(raw)
        name = f'.local/deploy/serverless-development/{self.manifest["release_id"]}/fixture/initial-recovery.json'
        with ZipFile(self.archive, 'w') as zipped:
            zipped.writestr(name, raw if manifest_bytes is None else manifest_bytes)
            for entry, value in (extra_entries or {}).items():
                zipped.writestr(entry, value)
        self.artifact['digest'] = 'sha256:' + hashlib.sha256(self.archive.read_bytes()).hexdigest()

    def github_json(self, client, path, **params):
        return deepcopy({'actions/runs/12': self.run, 'actions/workflows/77': self.workflow,
                         'actions/artifacts/9': self.artifact}[path])

class TrustedRecoveryArtifactTest(unittest.TestCase):
    def test_artifact_wrapper_preserves_reviewed_resume_and_provenance_without_overwriting(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            path, source = cloud.detached_manifest(directory)
            destination = Path(directory) / 'artifact-resumed.json'
            proof = {'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'artifact_id': 9}
            with patch.object(recovery, 'verify_recovery_artifact', return_value=proof) as verify:
                result = recovery.resume_initial_from_artifact(cloud.aws, cloud.config, path,
                    destination, artifact_proof={'run_id': 12, 'artifact_id': 9, 'archive_path': 'fixture.zip'})
                self.assertEqual(result['resumed_from'], proof)
                self.assertEqual(result['retained_physical_ids'], cloud.physical)
                self.assertEqual(result['release_id'], 'c' * 40)
                self.assertEqual(json.loads(destination.read_text()), result)
                verify.assert_called_once()
            cf = cloud.clients['cloudformation']
            cf.delete_stack.assert_not_called()
            self.assertNotIn('Tags', cf.create_change_set.call_args.kwargs)
            original = destination.read_bytes()
            with patch.object(recovery, 'verify_recovery_artifact') as verify, self.assertRaises(Gate):
                recovery.resume_initial_from_artifact(cloud.aws, cloud.config, path, destination,
                    artifact_proof={'run_id': 12, 'artifact_id': 9, 'archive_path': 'fixture.zip'})
            verify.assert_not_called()
            self.assertEqual(destination.read_bytes(), original)

    def test_artifact_verifier_binds_real_metadata_archive_and_exact_manifest_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = ResumeFixture(directory)
            with patch.object(recovery, '_github_json', side_effect=fixture.github_json) as github:
                result = recovery.verify_recovery_artifact(fixture.path, fixture.proof, client=object())
            self.assertEqual(result['manifest_sha256'], hashlib.sha256(fixture.path.read_bytes()).hexdigest())
            self.assertEqual(result['archive_sha256'], fixture.artifact['digest'][7:])
            self.assertEqual([call.args[1] for call in github.call_args_list], [
                'actions/runs/12', 'actions/workflows/77', 'actions/artifacts/9', 'actions/runs/12'])
            fixture.cloud.no_mutations(self)

    def test_artifact_run_must_be_failed_main_manual_workflow_in_this_repository(self):
        for field, value in (('conclusion', 'success'), ('event', 'pull_request'), ('head_branch', 'feature'),
                             ('head_sha', 'c' * 40), ('path', '.github/workflows/other.yml'),
                             ('repository', {'id': 42, 'full_name': 'untrusted/repository'})):
            with tempfile.TemporaryDirectory() as directory:
                fixture = ResumeFixture(directory)
                fixture.run[field] = value
                with self.subTest(field=field), patch.object(recovery, '_github_json', side_effect=fixture.github_json), \
                        self.assertRaises(Gate):
                    recovery.verify_recovery_artifact(fixture.path, fixture.proof, client=object())
                fixture.cloud.no_mutations(self)

    def test_archive_digest_manifest_bytes_metadata_and_manifest_count_are_required(self):
        for kind in ('digest', 'manifest', 'metadata', 'duplicate'):
            with tempfile.TemporaryDirectory() as directory:
                fixture = ResumeFixture(directory)
                if kind == 'digest':
                    fixture.artifact['digest'] = 'sha256:' + '0' * 64
                elif kind == 'manifest':
                    fixture.write_archive(manifest_bytes=b'fictional altered manifest')
                elif kind == 'metadata':
                    fixture.artifact['workflow_run']['id'] = 99
                else:
                    fixture.write_archive(extra_entries={
                        f'.local/deploy/serverless-development/{fixture.manifest["release_id"]}/duplicate/initial-recovery.json': b'{}'})
                with self.subTest(kind=kind), patch.object(recovery, '_github_json', side_effect=fixture.github_json), \
                        self.assertRaises(Gate):
                    recovery.verify_recovery_artifact(fixture.path, fixture.proof, client=object())
                fixture.cloud.no_mutations(self)

    def test_run_rerun_race_is_rejected_before_aws_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = ResumeFixture(directory)
            reads = 0
            def changed(client, path, **params):
                nonlocal reads
                result = fixture.github_json(client, path, **params)
                if path == 'actions/runs/12':
                    reads += 1
                    if reads > 1:
                        result['run_attempt'] = 2
                return result
            with patch.object(recovery, '_github_json', side_effect=changed), self.assertRaisesRegex(Gate, 'changed'):
                recovery.resume_initial_from_artifact(fixture.cloud.aws, fixture.cloud.config, fixture.path,
                    fixture.output, artifact_proof=fixture.proof)
            fixture.cloud.no_mutations(self)
