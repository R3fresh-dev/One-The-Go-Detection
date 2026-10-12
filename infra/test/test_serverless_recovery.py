"""First-stack recovery contracts; these fixtures are not AWS acceptance proof."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

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
        self.created_at = datetime(2026, 10, 11, tzinfo=timezone.utc)
        self.import_template = None
        self.change_name = None
        self.change_id = None
        self.protection = True
        self.clients = {name: Mock(name=name) for name in
            ('sts', 'cloudformation', 'rds', 'lambda', 's3', 'dynamodb', 'cognito-idp', 'secretsmanager', 'kms', 'logs')}
        self.aws = SimpleNamespace(client=lambda name: self.clients[name])
        self.clients['sts'].get_caller_identity.return_value = {'Account': ACCOUNT}
        cf = self.clients['cloudformation']
        cf.describe_stacks.side_effect = lambda **kwargs: {'Stacks': [{'StackId':
            NEW_STACK if self.import_template is not None else OLD_STACK,
            'StackStatus': self.status, 'EnableTerminationProtection': self.protection,
            'Tags': [{'Key': 'deployment', 'Value': recovery.STACK},
                     {'Key': 'purpose', 'Value': 'serverless-development'}]}]}
        cf.get_template.side_effect = lambda **kwargs: {'TemplateBody': deepcopy(self.import_template if self.import_template is not None else self.template)}
        cf.get_template_summary.side_effect = self.summary
        cf.get_paginator.side_effect = self.paginator
        cf.get_waiter.side_effect = self.waiter
        def create(**kwargs):
            self.change_name = kwargs['ChangeSetName']
            self.change_id = f'arn:aws:cloudformation:{REGION}:{ACCOUNT}:changeSet/{self.change_name}/fixture-import'
            self.import_template = json.loads(kwargs['TemplateBody'])
            self.status = 'REVIEW_IN_PROGRESS'
            return {'Id': self.change_id, 'StackId': NEW_STACK}
        cf.create_change_set.side_effect = create
        cf.update_termination_protection.side_effect = lambda **kwargs: setattr(self, 'protection', kwargs['EnableTerminationProtection'])
        self.clients['rds'].describe_db_clusters.side_effect = absent('DBClusterNotFoundFault')
        self.clients['rds'].describe_db_instances.side_effect = absent('DBInstanceNotFound')
        self.clients['lambda'].get_function.side_effect = absent('ResourceNotFoundException')
        self.clients['s3'].get_bucket_tagging.return_value = {'TagSet': self.tags}
        self.clients['s3'].get_bucket_location.return_value = {'LocationConstraint': REGION}
        self.clients['s3'].get_bucket_versioning.return_value = {'Status': 'Enabled'}
        self.clients['s3'].get_public_access_block.return_value = {'PublicAccessBlockConfiguration': {
            'BlockPublicAcls': True, 'IgnorePublicAcls': True, 'BlockPublicPolicy': True, 'RestrictPublicBuckets': True}}
        def encryption(**kwargs):
            name = next(name for name, physical in self.physical.items() if physical == kwargs['Bucket'])
            expected = deepcopy(self.retained[name]['Properties']['BucketEncryption']['ServerSideEncryptionConfiguration'][0])
            default = expected['ServerSideEncryptionByDefault']
            if default['SSEAlgorithm'] == 'aws:kms':
                key = default['KMSMasterKeyID']['Fn::GetAtt'][0]
                default['KMSMasterKeyID'] = f'arn:aws:kms:{REGION}:{ACCOUNT}:key/{self.physical[key]}'
            return {'ServerSideEncryptionConfiguration': {'Rules': [{
                'ApplyServerSideEncryptionByDefault': default, **({'BucketKeyEnabled': expected['BucketKeyEnabled']} if 'BucketKeyEnabled' in expected else {})}]}}
        self.clients['s3'].get_bucket_encryption.side_effect = encryption
        self.clients['s3'].get_object_lock_configuration.return_value = {'ObjectLockConfiguration': {
            'ObjectLockEnabled': 'Enabled', 'Rule': {'DefaultRetention': {'Mode': 'COMPLIANCE', 'Days': 90}}}}
        self.clients['s3'].list_object_versions.return_value = {'Versions': [], 'DeleteMarkers': [], 'IsTruncated': False}
        self.clients['s3'].list_multipart_uploads.return_value = {'Uploads': [], 'IsTruncated': False}
        dynamo = self.clients['dynamodb']
        dynamo.describe_table.return_value = {'Table': {'TableStatus': 'ACTIVE',
            'TableName': self.physical['RuntimeControl'], 'TableArn': f'arn:aws:dynamodb:{REGION}:{ACCOUNT}:table/{self.physical["RuntimeControl"]}',
            'TableId': '00000000-0000-4000-8000-000000000001'}}
        dynamo.list_tags_of_resource.return_value = {'Tags': self.tags}
        dynamo.scan.return_value = {'Count': 0, 'ScannedCount': 0}
        cognito = self.clients['cognito-idp']
        cognito.describe_user_pool.return_value = {'UserPool': {'Name': recovery.STACK, 'Id': self.physical['Accounts'],
            'Arn': f'arn:aws:cognito-idp:{REGION}:{ACCOUNT}:userpool/{self.physical["Accounts"]}', 'CreationDate': self.created_at,
            'UserPoolTags': {tag['Key']: tag['Value'] for tag in self.tags}}}
        cognito.list_users.return_value = {'Users': []}
        secret = self.clients['secretsmanager']
        secret.describe_secret.side_effect = lambda **kwargs: {'Name': next(
            self.retained[name]['Properties']['Name'] for name, physical in self.physical.items()
            if physical == kwargs['SecretId']), 'ARN': kwargs['SecretId'], 'Tags': self.tags,
            'CreatedDate': self.created_at, 'KmsKeyId': f'arn:aws:kms:{REGION}:{ACCOUNT}:key/' + self.physical[
                'DataKey' if kwargs['SecretId'] == self.physical['ApplicationSecret'] else 'JournalKey'],
            'RotationEnabled': False, 'VersionIdsToStages': {'0' * 32: ['AWSCURRENT']}}
        kms = self.clients['kms']
        kms.describe_key.side_effect = lambda **kwargs: {'KeyMetadata': {'KeyId': kwargs['KeyId'],
            'AWSAccountId': ACCOUNT, 'Description': next(self.retained[name]['Properties']['Description']
                for name, physical in self.physical.items() if physical == kwargs['KeyId']), 'KeyState': 'Enabled',
                'Arn': f'arn:aws:kms:{REGION}:{ACCOUNT}:key/{kwargs["KeyId"]}', 'KeyManager': 'CUSTOMER', 'Origin': 'AWS_KMS',
                'KeySpec': 'ECC_NIST_P256' if kwargs['KeyId'] == self.physical['CaptureSigningKey'] else 'SYMMETRIC_DEFAULT',
                'KeyUsage': 'SIGN_VERIFY' if kwargs['KeyId'] == self.physical['CaptureSigningKey'] else 'ENCRYPT_DECRYPT',
                'CreationDate': self.created_at}}
        def policy(**kwargs):
            name = next(name for name, physical in self.physical.items() if physical == kwargs['KeyId'])
            body = deepcopy(self.retained[name]['Properties']['KeyPolicy'])
            body['Statement'][0]['Principal']['AWS'] = f'arn:aws:iam::{ACCOUNT}:root'
            return {'Policy': json.dumps(body)}
        kms.get_key_policy.side_effect = policy
        kms.list_resource_tags.return_value = {'Tags': [{'TagKey': tag['Key'], 'TagValue': tag['Value']} for tag in self.tags], 'Truncated': False}
        logs = self.clients['logs']
        logs.describe_log_groups.side_effect = lambda **kwargs: {'logGroups': [{
            'logGroupName': kwargs['logGroupNamePrefix'], 'arn': f'arn:aws:logs:{REGION}:{ACCOUNT}:log-group:' + kwargs['logGroupNamePrefix'] + ':*',
            'creationTime': 1791676800000, 'retentionInDays': 7,
            'kmsKeyId': f'arn:aws:kms:{REGION}:{ACCOUNT}:key/{self.physical["DataKey"]}'}]}
        logs.list_tags_for_resource.return_value = {'tags': {tag['Key']: tag['Value'] for tag in self.tags}}

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
            return SimpleNamespace(paginate=lambda **kwargs: [{'StackResourceSummaries':
                [{**row, 'ResourceStatus': 'IMPORT_COMPLETE'} for row in self.rows if row['LogicalResourceId'] in self.retained]
                if self.status == 'IMPORT_COMPLETE' else deepcopy(self.rows)}])
        if operation == 'describe_change_set':
            return SimpleNamespace(paginate=lambda **kwargs: [{'ChangeSetId': self.change_id, 'ChangeSetName': self.change_name,
                'StackId': NEW_STACK, 'StackName': recovery.STACK, 'Status': 'CREATE_COMPLETE', 'ExecutionStatus': 'AVAILABLE',
                'Changes': [{'ResourceChange': {
                'Action': 'Import', 'LogicalResourceId': name, 'ResourceType': value['Type'], 'PhysicalResourceId': self.physical[name]}}
                for name, value in self.retained.items()]}])
        raise AssertionError(operation)

    def waiter(self, name):
        def wait(**kwargs):
            if name == 'stack_import_complete':
                self.status = 'IMPORT_COMPLETE'
        return SimpleNamespace(wait=wait)

    def no_mutations(self, test):
        cf = self.clients['cloudformation']
        for operation in ('update_termination_protection', 'delete_stack', 'create_change_set', 'execute_change_set'):
            getattr(cf, operation).assert_not_called()
        for client in self.clients.values():
            for forbidden in ('get_secret_value', 'delete_bucket', 'delete_user_pool', 'delete_table',
                              'delete_secret', 'schedule_key_deletion', 'delete_log_group', 'get_object'):
                getattr(client, forbidden).assert_not_called()


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
            result = recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
            self.assertEqual(result['status'], 'uninitialized-retained-resources-imported')
            self.assertEqual(json.loads(path.read_text()), result)
            self.assertFalse(result['actual_resources_deleted'])
            self.assertFalse(result['application_deployment_completed'])
        cf = cloud.clients['cloudformation']
        call = cf.create_change_set.call_args.kwargs
        self.assertEqual(call['ChangeSetType'], 'IMPORT')
        self.assertEqual(json.loads(call['TemplateBody'])['Resources'], cloud.retained)
        self.assertEqual(call['ResourcesToImport'], result['resources_to_import'])
        self.assertEqual(cf.execute_change_set.call_count, 1)
        self.assertTrue(cloud.protection)
        self.assertEqual(cloud.clients['s3'].list_object_versions.call_count,
                         5 * sum(value['Type'] == 'AWS::S3::Bucket' for value in cloud.retained.values()))
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
                return SimpleNamespace(paginate=lambda **kwargs: [{'ChangeSetId': cloud.change_id, 'ChangeSetName': cloud.change_name,
                    'StackId': NEW_STACK, 'StackName': recovery.STACK, 'Status': 'CREATE_COMPLETE', 'ExecutionStatus': 'AVAILABLE',
                    'Changes': [{'ResourceChange': {
                    'Action': 'Add', 'LogicalResourceId': name, 'ResourceType': value['Type']}}
                    for name, value in cloud.retained.items()]}])
            return original_paginator(operation)
        cloud.clients['cloudformation'].get_paginator.side_effect = paginator
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-recovery.json'
            with self.assertRaisesRegex(Gate, 'change set'):
                recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
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
                recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
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
                recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
            evidence = json.loads(path.read_text())
            self.assertEqual(evidence['failed_phase'], 'import-executing')
            self.assertEqual(evidence['retained_physical_ids'], cloud.physical)

    def test_existing_journal_cannot_be_overwritten_for_an_unreviewed_resume(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-recovery.json'
            path.write_text('existing recovery evidence')
            with self.assertRaisesRegex(Gate, 'new protected'):
                recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
            self.assertEqual(path.read_text(), 'existing recovery evidence')
        cloud.no_mutations(self)

    def test_dependency_parser_handles_substitution_variables_and_escaped_pseudo_parameters(self):
        self.assertEqual(recovery._references({'Fn::Sub': ['${Arn}/* ${DataKey.Arn} ${AWS::AccountId} ${!literal}',
            {'Arn': {'Fn::GetAtt': ['DeletionJournal', 'Arn']}}], 'DependsOn': 'JournalKey'}),
            {'DeletionJournal', 'DataKey', 'JournalKey'})


class RecoveryReadmissionAndRaceTest(unittest.TestCase):
    def mutation(self, cloud, kind):
        if kind == 'versions':
            cloud.clients['s3'].list_object_versions.return_value = {'IsTruncated': False, 'Versions': [{'Key': 'fictional-raced-write'}]}
        elif kind == 'markers':
            cloud.clients['s3'].list_object_versions.return_value = {'IsTruncated': False, 'DeleteMarkers': [{'Key': 'fictional-raced-marker'}]}
        elif kind == 'multipart':
            cloud.clients['s3'].list_multipart_uploads.return_value = {'IsTruncated': False, 'Uploads': [{'Key': 'fictional-raced-upload'}]}
        elif kind == 'control':
            cloud.clients['dynamodb'].scan.return_value = {'Count': 1, 'ScannedCount': 1}
        elif kind == 'control-cursor':
            cloud.clients['dynamodb'].scan.return_value = {'Count': 0, 'ScannedCount': 0, 'LastEvaluatedKey': {'PK': {'S': 'admission'}}}
        elif kind == 'users':
            cloud.clients['cognito-idp'].list_users.return_value = {'Users': [{'Username': 'fictional-raced-account'}]}
        elif kind == 'user-cursor':
            cloud.clients['cognito-idp'].list_users.return_value = {'Users': [], 'PaginationToken': 'fictional-more-users'}
        elif kind == 'kms':
            prior = cloud.clients['kms'].describe_key.side_effect
            def changed(**kwargs):
                result = prior(**kwargs)
                result['KeyMetadata']['KeyState'] = 'PendingDeletion'
                return result
            cloud.clients['kms'].describe_key.side_effect = changed
        elif kind == 'tags':
            cloud.clients['s3'].get_bucket_tagging.return_value = {'TagSet': [
                {'Key': 'deployment', 'Value': 'foreign'}, {'Key': 'environment', 'Value': 'serverless-development'}]}
        elif kind == 'database':
            cloud.clients['rds'].describe_db_clusters.side_effect = None
            cloud.clients['rds'].describe_db_clusters.return_value = {'DBClusters': [{'DBClusterIdentifier': recovery.STACK}]}
        elif kind.startswith('function-'):
            role = kind.removeprefix('function-')
            def present(**kwargs):
                if kwargs['FunctionName'] == recovery.STACK + '-' + role:
                    return {'Configuration': {'FunctionName': kwargs['FunctionName']}}
                raise absent('ResourceNotFoundException')
            cloud.clients['lambda'].get_function.side_effect = present
        elif kind == 'table-generation':
            cloud.clients['dynamodb'].describe_table.return_value['Table']['TableId'] = '00000000-0000-4000-8000-000000000002'
        elif kind in ('secret-generation', 'secret-rotation'):
            prior = cloud.clients['secretsmanager'].describe_secret.side_effect
            def changed(**kwargs):
                result = prior(**kwargs)
                if kind == 'secret-generation':
                    result['VersionIdsToStages'] = {'1' * 32: ['AWSCURRENT']}
                else:
                    result['RotationEnabled'] = True
                return result
            cloud.clients['secretsmanager'].describe_secret.side_effect = changed
        elif kind == 'log-retention':
            prior = cloud.clients['logs'].describe_log_groups.side_effect
            def changed(**kwargs):
                result = prior(**kwargs)
                result['logGroups'][0]['retentionInDays'] = 90
                return result
            cloud.clients['logs'].describe_log_groups.side_effect = changed
        else:
            raise AssertionError(kind)

    def test_required_callback_precedes_every_mutation_and_each_rejection_aborts(self):
        for failure in (None, 1, 2, 3, 4, 5):
            cloud = FakeCloud()
            events = []
            cf = cloud.clients['cloudformation']
            for operation in ('update_termination_protection', 'delete_stack', 'create_change_set', 'execute_change_set'):
                method = getattr(cf, operation)
                original = method.side_effect
                def mutation(*args, operation=operation, original=original, method=method, **kwargs):
                    self.assertEqual(events[-1], 'gate')
                    events.append(operation)
                    return original(*args, **kwargs) if callable(original) else method.return_value
                method.side_effect = mutation
            checks = 0
            def readmission():
                nonlocal checks
                checks += 1
                events.append('gate')
                if checks == failure:
                    raise Gate('Fictional current main gate failure')
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'initial-recovery.json'
                if failure is None:
                    result = recovery.recover_initial(cloud.aws, cloud.config, path, readmission=readmission)
                    self.assertEqual(result['status'], 'uninitialized-retained-resources-imported')
                    self.assertEqual(checks, 5)
                else:
                    with self.assertRaises(Gate):
                        recovery.recover_initial(cloud.aws, cloud.config, path, readmission=readmission)
                    self.assertEqual(sum(event != 'gate' for event in events), failure - 1)
                    saved = json.loads(path.read_bytes())
                    self.assertEqual(saved['status'], 'blocked-recovery-inspect-protected-journal-before-retry')
                    self.assertEqual(saved['retained_physical_ids'], cloud.physical)

    def test_rejected_change_set_deletion_also_requires_fresh_readmission(self):
        cloud = FakeCloud()
        original = cloud.paginator
        def paginator(operation):
            page = original(operation)
            def pages(**kwargs):
                values = deepcopy(list(page.paginate(**kwargs)))
                if operation == 'describe_change_set':
                    values[0]['Changes'][0]['ResourceChange']['Action'] = 'Add'
                return values
            return SimpleNamespace(paginate=pages)
        cloud.clients['cloudformation'].get_paginator.side_effect = paginator
        calls = 0
        def readmission():
            nonlocal calls
            calls += 1
            if calls == 4:
                raise Gate('Cleanup gate also failed')
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(Gate, 'Cleanup gate'):
            recovery.recover_initial(cloud.aws, cloud.config, Path(directory) / 'recovery.json', readmission=readmission)
        cloud.clients['cloudformation'].delete_change_set.assert_not_called()
        cloud.clients['cloudformation'].execute_change_set.assert_not_called()

    def test_resource_drift_during_change_set_or_import_wait_cannot_claim_recovery(self):
        cases = ('versions', 'markers', 'multipart', 'control', 'control-cursor', 'users', 'user-cursor',
            'kms', 'tags', 'database', 'table-generation', 'secret-generation', 'secret-rotation', 'log-retention') + tuple('function-' + role for role in ('api', 'worker', 'dispatcher', 'maintenance', 'control'))
        for waiter in ('change_set_create_complete', 'stack_import_complete'):
            for kind in cases:
                cloud = FakeCloud()
                original = cloud.waiter
                def waiting(name):
                    active = original(name)
                    def wait(**kwargs):
                        active.wait(**kwargs)
                        if name == waiter:
                            self.mutation(cloud, kind)
                    return SimpleNamespace(wait=wait)
                cloud.clients['cloudformation'].get_waiter.side_effect = waiting
                with self.subTest(waiter=waiter, kind=kind), tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / 'recovery.json'
                    with self.assertRaises(Gate):
                        recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
                    evidence = json.loads(path.read_bytes())
                    self.assertEqual(evidence['status'], 'blocked-recovery-inspect-protected-journal-before-retry')
                    self.assertEqual(evidence['retained_physical_ids'], cloud.physical)
                    self.assertFalse(evidence['actual_resources_deleted'])
                    self.assertFalse(evidence['application_deployment_completed'])
                if waiter == 'change_set_create_complete':
                    cloud.clients['cloudformation'].execute_change_set.assert_not_called()
                else:
                    cloud.clients['cloudformation'].execute_change_set.assert_called_once()

    def test_writer_during_last_gate_callback_is_refused_before_execute(self):
        cloud = FakeCloud()
        calls = 0
        def readmission():
            nonlocal calls
            calls += 1
            if calls == 5:
                self.mutation(cloud, 'control')
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(Gate, 'empty runtime'):
            recovery.recover_initial(cloud.aws, cloud.config, Path(directory) / 'recovery.json', readmission=readmission)
        cloud.clients['cloudformation'].execute_change_set.assert_not_called()

    def test_explicit_completion_and_typed_empty_metadata_are_required(self):
        for service, operation, bad in (
            ('s3', 'list_object_versions', {}), ('s3', 'list_object_versions', {'IsTruncated': 0}),
            ('s3', 'list_multipart_uploads', {}), ('s3', 'list_multipart_uploads', {'IsTruncated': False, 'NextUploadIdMarker': 'more'}),
            ('dynamodb', 'scan', {}), ('dynamodb', 'scan', {'Count': False, 'ScannedCount': 0}),
            ('dynamodb', 'scan', {'Count': 0, 'ScannedCount': 1}),
            ('cognito-idp', 'list_users', {}), ('cognito-idp', 'list_users', {'Users': [], 'PaginationToken': 'more'}),
            ('kms', 'list_resource_tags', {'Tags': [], 'Truncated': False}),
        ):
            cloud = FakeCloud()
            method = getattr(cloud.clients[service], operation)
            method.side_effect = None
            method.return_value = bad
            with self.subTest(service=service, operation=operation, bad=bad), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)
        cloud = FakeCloud()
        cloud.clients['s3'].list_object_versions.return_value = {'IsTruncated': False}
        cloud.clients['s3'].list_multipart_uploads.return_value = {'IsTruncated': False}
        recovery.initial_recovery_plan(cloud.aws, cloud.config)
        for call in cloud.clients['s3'].list_object_versions.call_args_list:
            self.assertEqual(call.kwargs['ExpectedBucketOwner'], ACCOUNT)

    def test_ambiguous_tags_authority_spec_policy_and_account_links_are_refused(self):
        for kind in ('tags', 'key-spec', 'key-usage', 'key-origin', 'policy', 'secret-link', 'bucket-region', 'bucket-version', 'journal-retention', 'log-link'):
            cloud = FakeCloud()
            if kind == 'tags':
                cloud.clients['s3'].get_bucket_tagging.return_value = {'TagSet': cloud.tags + [cloud.tags[0]]}
            elif kind.startswith('key-'):
                prior = cloud.clients['kms'].describe_key.side_effect
                field, bad = {'key-spec': ('KeySpec', 'RSA_2048'), 'key-usage': ('KeyUsage', 'SIGN_VERIFY'), 'key-origin': ('Origin', 'EXTERNAL')}[kind]
                def changed(**kwargs):
                    result = prior(**kwargs)
                    result['KeyMetadata'][field] = bad
                    return result
                cloud.clients['kms'].describe_key.side_effect = changed
            elif kind == 'policy':
                cloud.clients['kms'].get_key_policy.side_effect = None
                cloud.clients['kms'].get_key_policy.return_value = {'Policy': '{"Version":"2012-10-17","Statement":[]}'}
            elif kind == 'secret-link':
                prior = cloud.clients['secretsmanager'].describe_secret.side_effect
                def changed(**kwargs):
                    result = prior(**kwargs)
                    result['KmsKeyId'] = 'arn:aws:kms:us-east-2:111111111111:key/foreign'
                    return result
                cloud.clients['secretsmanager'].describe_secret.side_effect = changed
            elif kind == 'bucket-region':
                cloud.clients['s3'].get_bucket_location.return_value = {'LocationConstraint': 'us-west-2'}
            elif kind == 'bucket-version':
                cloud.clients['s3'].get_bucket_versioning.return_value = {'Status': 'Suspended'}
            elif kind == 'journal-retention':
                cloud.clients['s3'].get_object_lock_configuration.return_value['ObjectLockConfiguration']['Rule']['DefaultRetention']['Mode'] = 'GOVERNANCE'
            else:
                prior = cloud.clients['logs'].describe_log_groups.side_effect
                def changed(**kwargs):
                    result = prior(**kwargs)
                    result['logGroups'][0]['kmsKeyId'] = 'foreign-key'
                    return result
                cloud.clients['logs'].describe_log_groups.side_effect = changed
            with self.subTest(kind=kind), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_configuration_types_precede_any_mutation(self):
        for change in ({'account': True}, {'releaseId': None}, {'region': []}):
            cloud = FakeCloud()
            cloud.config.update(change)
            with self.subTest(change=change), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_secret_version_inventory_is_bounded_unique_and_never_pending(self):
        for versions in ({}, {'short': ['AWSCURRENT']}, {'0' * 32: []}, {'0' * 32: ['AWSPENDING']},
            {'0' * 32: ['AWSCURRENT', 'AWSCURRENT']}, {'0' * 32: ['AWSCURRENT'], '1' * 32: ['AWSCURRENT']},
            {'0' * 32: ['AWSCURRENT', 'x' * 257]}):
            cloud = FakeCloud()
            prior = cloud.clients['secretsmanager'].describe_secret.side_effect
            def changed(**kwargs):
                result = prior(**kwargs)
                result['VersionIdsToStages'] = versions
                return result
            cloud.clients['secretsmanager'].describe_secret.side_effect = changed
            with self.subTest(version_count=len(versions)), self.assertRaises(Gate):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_create_and_describe_change_set_authority_is_pinned_before_execute(self):
        for kind in ('create-stack', 'create-change', 'describe-stack', 'describe-change', 'describe-status', 'import-template'):
            cloud = FakeCloud()
            if kind.startswith('create-'):
                prior = cloud.clients['cloudformation'].create_change_set.side_effect
                def changed(**kwargs):
                    result = prior(**kwargs)
                    result['StackId' if kind == 'create-stack' else 'Id'] = 'arn:aws:cloudformation:us-east-2:111111111111:stack/foreign/id'
                    return result
                cloud.clients['cloudformation'].create_change_set.side_effect = changed
            elif kind == 'import-template':
                prior = cloud.waiter
                def waiting(name):
                    active = prior(name)
                    def wait(**kwargs):
                        active.wait(**kwargs)
                        if name == 'change_set_create_complete':
                            cloud.import_template['Description'] = 'Changed by another actor'
                    return SimpleNamespace(wait=wait)
                cloud.clients['cloudformation'].get_waiter.side_effect = waiting
            else:
                prior = cloud.paginator
                def paginator(operation):
                    active = prior(operation)
                    def pages(**kwargs):
                        result = deepcopy(list(active.paginate(**kwargs)))
                        if operation == 'describe_change_set':
                            field, value = {'describe-stack': ('StackId', OLD_STACK),
                                'describe-change': ('ChangeSetId', 'another-change-set'),
                                'describe-status': ('ExecutionStatus', 'EXECUTE_COMPLETE')}[kind]
                            result[0][field] = value
                        return result
                    return SimpleNamespace(paginate=pages)
                cloud.clients['cloudformation'].get_paginator.side_effect = paginator
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'recovery.json'
                with self.assertRaises(Gate):
                    recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
                self.assertEqual(json.loads(path.read_bytes())['status'], 'blocked-recovery-inspect-protected-journal-before-retry')
            cloud.clients['cloudformation'].execute_change_set.assert_not_called()

    def test_final_adopted_stack_tags_template_type_and_status_are_exact(self):
        for kind in ('stack-tags', 'stack-id', 'template', 'resource-type', 'resource-status'):
            cloud = FakeCloud()
            if kind in ('stack-tags', 'stack-id'):
                prior = cloud.clients['cloudformation'].describe_stacks.side_effect
                def changed(**kwargs):
                    result = prior(**kwargs)
                    if cloud.status == 'IMPORT_COMPLETE':
                        if kind == 'stack-tags':
                            result['Stacks'][0]['Tags'][0]['Value'] = 'foreign'
                        else:
                            result['Stacks'][0]['StackId'] = OLD_STACK
                    return result
                cloud.clients['cloudformation'].describe_stacks.side_effect = changed
            elif kind == 'template':
                prior = cloud.waiter
                def waiting(name):
                    active = prior(name)
                    def wait(**kwargs):
                        active.wait(**kwargs)
                        if name == 'stack_import_complete':
                            cloud.import_template['Description'] = 'Different adopted template'
                    return SimpleNamespace(wait=wait)
                cloud.clients['cloudformation'].get_waiter.side_effect = waiting
            else:
                prior = cloud.paginator
                def paginator(operation):
                    active = prior(operation)
                    def pages(**kwargs):
                        result = deepcopy(list(active.paginate(**kwargs)))
                        if operation == 'list_stack_resources' and cloud.status == 'IMPORT_COMPLETE':
                            field, value = ('ResourceType', 'AWS::S3::Bucket') if kind == 'resource-type' else ('ResourceStatus', 'DELETE_COMPLETE')
                            result[0]['StackResourceSummaries'][0][field] = value
                        return result
                    return SimpleNamespace(paginate=pages)
                cloud.clients['cloudformation'].get_paginator.side_effect = paginator
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'recovery.json'
                with self.assertRaises(Gate):
                    recovery.recover_initial(cloud.aws, cloud.config, path, readmission=lambda: None)
                evidence = json.loads(path.read_bytes())
                self.assertEqual(evidence['status'], 'blocked-recovery-inspect-protected-journal-before-retry')
                self.assertEqual(evidence['retained_physical_ids'], cloud.physical)

    def test_old_handler_protocol_or_boolean_template_mutation_remains_unsupported(self):
        for kind in ('old-protocol', 'boolean-for-zero'):
            cloud = FakeCloud()
            if kind == 'old-protocol':
                cloud.template['Resources']['MaintenanceFunction']['Properties']['Environment']['Variables'].pop('OTGD_LAMBDA_HANDLER')
            else:
                cloud.template['Resources']['ApiFunction']['Properties']['ReservedConcurrentExecutions'] = False
            with self.subTest(kind=kind), self.assertRaisesRegex(Gate, 'reviewed stopped deployment'):
                recovery.initial_recovery_plan(cloud.aws, cloud.config)
            cloud.no_mutations(self)

    def test_private_directory_and_durable_parent_fsync_precede_any_mutation(self):
        cloud = FakeCloud()
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            work.chmod(0o755)
            with self.assertRaises(Gate):
                recovery.recover_initial(cloud.aws, cloud.config, work / 'recovery.json', readmission=lambda: None)
            cloud.no_mutations(self)
            work.chmod(0o700)
            fsync = os.fsync
            calls = 0
            def failed_parent(descriptor):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError('Fictional parent directory fsync failure')
                return fsync(descriptor)
            with patch.object(recovery.os, 'fsync', side_effect=failed_parent), self.assertRaises(OSError):
                recovery.recover_initial(cloud.aws, cloud.config, work / 'recovery.json', readmission=lambda: None)
            cloud.no_mutations(self)


if __name__ == '__main__':
    unittest.main()
