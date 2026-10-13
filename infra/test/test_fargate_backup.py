"""Regional backup contracts; SDK-shaped fixtures are not live restore proof."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

from botocore import xform_name
from botocore.exceptions import ClientError
import botocore.session
from botocore.validate import validate_parameters

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from deploy import fargate_backup as backup
from deploy.provenance import Gate


ACCOUNT = '123456789012'
KEY_ID = '12345678-1234-1234-1234-123456789abc'
KEY = f'arn:aws:kms:us-west-2:{ACCOUNT}:key/{KEY_ID}'
VAULT = f'arn:aws:backup:us-west-2:{ACCOUNT}:backup-vault:otgd-fargate-development-us-west-2'
CLUSTER = f'arn:aws:rds:us-east-1:{ACCOUNT}:cluster:otgd-serverless-development'
ROLE = f'arn:aws:iam::{ACCOUNT}:role/otgd-fargate-development-us-east-1-backup'
STACK_ID = f'arn:aws:cloudformation:us-west-2:{ACCOUNT}:stack/{backup.RECOVERY_STACK}/fixture'
NOW = datetime(2026, 10, 13, tzinfo=timezone.utc)
TOMBSTONE = f'arn:aws:secretsmanager:us-east-1:{ACCOUNT}:secret:{backup.STACK}-tombstone-fixture'
SOURCE_KEY = f'arn:aws:kms:us-east-1:{ACCOUNT}:key/87654321-1234-1234-1234-123456789abc'
SOURCE_VAULT = f'arn:aws:backup:us-east-1:{ACCOUNT}:backup-vault:{backup.vault_name("us-east-1")}'
SOURCE_POINT = f'arn:aws:rds:us-east-1:{ACCOUNT}:cluster-snapshot:awsbackup:source-fixture'
DESTINATION_POINT = f'arn:aws:rds:us-west-2:{ACCOUNT}:cluster-snapshot:awsbackup:copy-fixture'


def configuration():
    return {'environment': 'fargate-development', 'account': ACCOUNT,
            'region': 'us-east-1', 'backupRegion': 'us-west-2', 'monthlyBudgetUsd': 100}


def source_template(c, *, registry=False):
    """Representative source resources isolate the backup extension contract."""
    resources = {logical: {'Type': 'AWS::S3::Bucket', 'Properties': {
        'BucketName': backup.primary_bucket(c, logical), 'VersioningConfiguration': {'Status': 'Enabled'}}}
        for logical in (('DeploymentAssets',) if registry else tuple(backup.BUCKETS)[:-1])}
    if not registry:
        resources.update({'Database': {'Type': 'AWS::RDS::DBCluster', 'Properties': {
            'DBClusterIdentifier': backup.STACK}}, 'DataKey': {'Type': 'AWS::KMS::Key', 'Properties': {}},
            'TombstoneSecret': {'Type': 'AWS::SecretsManager::Secret', 'Properties': {}},
            **{logical: {'Type': 'AWS::IAM::Role', 'Properties': {'Policies': []}}
               for logical in ('WorkerRole', 'MaintenanceRole')}})
    return {'AWSTemplateFormatVersion': '2010-09-09', 'Resources': resources,
            'Outputs': {'ExistingOutput': {'Value': 'preserved'}}}


class SDKClient:
    """Accept only actual SDK method names and validated request fields."""
    session = botocore.session.get_session()
    models = {}

    def __init__(self, service):
        if service not in self.models:
            self.models[service] = self.session.get_service_model(service)
        self.model = self.models[service]
        self.methods = {xform_name(name): name for name in self.model.operation_names}
        self.responses = {}
        self.calls = []

    def __getattr__(self, method):
        if method not in self.methods:
            raise AssertionError(f'{self.model.service_name} has no SDK method {method}')
        operation = self.model.operation_model(self.methods[method])

        def call(**parameters):
            if operation.input_shape is not None:
                validate_parameters(parameters, operation.input_shape)
            elif parameters:
                raise AssertionError('Unexpected operation parameters')
            self.calls.append((method, deepcopy(parameters)))
            if method not in self.responses:
                raise AssertionError(f'Unexpected AWS operation {method}')
            response = self.responses[method]
            result = deepcopy(response(**parameters) if callable(response) else response)
            # GetTemplate's real botocore handler decodes its modeled string
            # into an object before the caller receives it.
            if operation.output_shape is not None and method != 'get_template':
                modeled = deepcopy(result)
                if method == 'get_role' and isinstance(modeled.get('Role', {}).get('AssumeRolePolicyDocument'), dict):
                    # IAM's botocore policy decoder likewise returns an object.
                    modeled['Role']['AssumeRolePolicyDocument'] = json.dumps(modeled['Role']['AssumeRolePolicyDocument'])
                validate_parameters(modeled, operation.output_shape)
            return result
        return call

    def get_paginator(self, method):
        if method not in self.methods:
            raise AssertionError(f'Unknown paginator operation {method}')
        operation = getattr(self, method)
        return SimpleNamespace(paginate=lambda **kwargs: iter([operation(**kwargs)]))


class RecoveryCloud:
    def __init__(self, c):
        self.config = c
        self.clients = {(service, region): SDKClient(service) for service, region in (
            ('sts', 'us-west-2'), ('kms', 'us-west-2'), ('s3', 'us-west-2'),
            ('backup', 'us-west-2'), ('backup', 'us-east-1'), ('cloudformation', 'us-west-2'),
            ('s3', 'us-east-1'), ('secretsmanager', 'us-east-1'))}
        self.requested_clients = []
        self.outputs = {'RecoveryKeyArn': KEY, 'RecoveryVaultArn': VAULT,
            'RecoveryVaultName': backup.vault_name('us-west-2'),
            **{'Replica' + logical + 'Bucket': backup.replica_bucket(c, logical) for logical in backup.BUCKETS}}
        self.client('sts', region_name='us-west-2').responses['get_caller_identity'] = {'Account': ACCOUNT}
        self.client('kms', region_name='us-west-2').responses['describe_key'] = {'KeyMetadata': {
            'Arn': KEY, 'KeyId': KEY_ID, 'AWSAccountId': ACCOUNT, 'KeyState': 'Enabled', 'Enabled': True,
            'KeyManager': 'CUSTOMER', 'KeySpec': 'SYMMETRIC_DEFAULT', 'KeyUsage': 'ENCRYPT_DECRYPT',
            'MultiRegion': False}}
        self.client('backup', region_name='us-west-2').responses['describe_backup_vault'] = {
            'BackupVaultName': backup.vault_name('us-west-2'), 'BackupVaultArn': VAULT, 'EncryptionKeyArn': KEY}
        s3 = self.client('s3', region_name='us-west-2')
        s3.responses.update(get_bucket_location={'LocationConstraint': 'us-west-2'},
            get_bucket_versioning={'Status': 'Enabled'}, get_public_access_block={
                'PublicAccessBlockConfiguration': {'BlockPublicAcls': True, 'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True, 'RestrictPublicBuckets': True}},
            get_bucket_encryption={'ServerSideEncryptionConfiguration': {'Rules': [{
                'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'aws:kms', 'KMSMasterKeyID': KEY},
                'BucketKeyEnabled': True}]}}, get_object_lock_configuration={
                'ObjectLockConfiguration': {'ObjectLockEnabled': 'Enabled',
                    'Rule': {'DefaultRetention': {'Mode': 'COMPLIANCE', 'Days': 90}}}})
        cf = self.client('cloudformation', region_name='us-west-2')
        self.destination = backup.build_destination_template(c)
        physical = {logical: (row.get('Properties', {}).get('BucketName')
            or (KEY_ID if logical == 'RecoveryKey' else 'alias/' + backup.RECOVERY_STACK
                if logical == 'RecoveryKeyAlias' else backup.vault_name('us-west-2')
                if logical == 'RecoveryVault' else logical))
            for logical, row in self.destination['Resources'].items()}
        cf.responses.update(describe_stacks={'Stacks': [{'StackId': STACK_ID,
            'StackName': backup.RECOVERY_STACK, 'StackStatus': 'CREATE_COMPLETE',
            'CreationTime': NOW, 'EnableTerminationProtection': True, 'Outputs': [
                {'OutputKey': key, 'OutputValue': value} for key, value in self.outputs.items()]}]},
            get_template={'TemplateBody': deepcopy(self.destination)},
            list_stack_resources={'StackResourceSummaries': [
                {'LogicalResourceId': logical, 'ResourceType': row['Type'],
                 'PhysicalResourceId': physical[logical], 'ResourceStatus': 'CREATE_COMPLETE',
                 'LastUpdatedTimestamp': NOW}
                for logical, row in self.destination['Resources'].items()]})
        primary = self.client('backup', region_name='us-east-1')
        primary.responses.update(get_backup_plan={'BackupPlan': {'BackupPlanName': 'owned-plan', 'Rules': [{
            'RuleName': 'DailyEncryptedOregonCopy', 'TargetBackupVaultName': backup.vault_name('us-east-1'),
            'ScheduleExpression': 'cron(0 6 * * ? *)', 'StartWindowMinutes': 60,
            'CompletionWindowMinutes': 360, 'EnableContinuousBackup': False,
            'Lifecycle': {'DeleteAfterDays': 2}, 'CopyActions': [{
                'DestinationBackupVaultArn': VAULT, 'Lifecycle': {'DeleteAfterDays': 7}}]}]}},
            list_backup_selections={'BackupSelectionsList': [{'SelectionId': 'selection-owned'}]},
            get_backup_selection={'BackupSelection': {'SelectionName': 'ExactVirginiaDatabase',
                'IamRoleArn': ROLE, 'Resources': [CLUSTER]}}, list_copy_jobs={'CopyJobs': []})
        source_s3 = self.client('s3', region_name='us-east-1')
        self.replications = {}
        self.versions = {}
        self.source_markers = {}
        self.replica_markers = {}
        self.source_heads = {}
        self.replica_heads = {}
        for logical in backup.BUCKETS:
            bucket = backup.primary_bucket(c, logical)
            self.replications[bucket] = {'Role': f'arn:aws:iam::{ACCOUNT}:role/{backup.replication_role_name()}',
                'Rules': [{'ID': 'ColdOregonVersions', 'Priority': 1, 'Status': 'Enabled',
                    'Filter': {'Prefix': ''}, 'DeleteMarkerReplication': {'Status': 'Enabled'},
                    'SourceSelectionCriteria': {'SseKmsEncryptedObjects': {'Status': 'Enabled'}},
                    'Destination': {'Bucket': 'arn:aws:s3:::' + backup.replica_bucket(c, logical),
                        'StorageClass': 'STANDARD', 'EncryptionConfiguration': {'ReplicaKmsKeyID': KEY}}}]}
            self.versions[bucket] = []
            self.source_markers[bucket] = []
            self.replica_markers[backup.replica_bucket(c, logical)] = []
        source_s3.responses.update(get_bucket_location={},
            get_bucket_versioning={'Status': 'Enabled'},
            get_bucket_replication=lambda **kwargs: {'ReplicationConfiguration': self.replications[kwargs['Bucket']]},
            list_object_versions=lambda **kwargs: {'Versions': self.versions[kwargs['Bucket']],
                'DeleteMarkers': self.source_markers[kwargs['Bucket']]},
            head_object=self.source_head)
        s3.responses['head_object'] = lambda **kwargs: self.replica_heads[kwargs['Bucket'], kwargs['Key'], kwargs['VersionId']]
        s3.responses['list_object_versions'] = lambda **kwargs: {'DeleteMarkers': self.replica_markers[kwargs['Bucket']]}
        self.client('secretsmanager', region_name='us-east-1').responses['describe_secret'] = {
            'ARN': TOMBSTONE, 'ReplicationStatus': [{'Region': 'us-west-2', 'KmsKeyId': KEY, 'Status': 'InSync'}]}
        self.requested_clients.clear()

    def client(self, service, *, region_name):
        self.requested_clients.append((service, region_name))
        if region_name not in ('us-east-1', 'us-west-2') or (service, region_name) not in self.clients:
            raise AssertionError(f'Unexpected regional AWS client {(service, region_name)}')
        return self.clients[service, region_name]

    def copy_job(self, state='COMPLETED', *, identifier='copy-owned'):
        return {'CopyJobId': identifier, 'ResourceArn': CLUSTER,
            'DestinationBackupVaultArn': VAULT, 'State': state,
            'CreationDate': NOW, 'CompletionDate': NOW}

    def source_head(self, **parameters):
        bucket, key = parameters['Bucket'], parameters['Key']
        version = parameters.get('VersionId')
        if version is None:
            matching = [head for (name, object_key, _), head in self.source_heads.items()
                        if name == bucket and object_key == key]
            if len(matching) != 1:
                raise ClientError({'Error': {'Code': '404', 'Message': 'Fixture witness absent'}}, 'HeadObject')
            return matching[0]
        return self.source_heads[bucket, key, version]

    def add_version(self, logical, *, state='COMPLETED', control=False):
        bucket = backup.primary_bucket(self.config, logical)
        key, version = logical.lower() + '/fixture', logical.lower() + '-version'
        if control:
            key = 'control/established.json'
        self.versions[bucket].append({'Key': key, 'VersionId': version})
        head = {'VersionId': version, 'ReplicationStatus': state, 'ContentLength': 123,
                'ChecksumSHA256': 'unit-test-checksum'}
        if logical in ('WebAssets', 'DeploymentAssets'):
            head['ServerSideEncryption'] = 'AES256'
        else:
            head.update(ServerSideEncryption='aws:kms', SSEKMSKeyId=SOURCE_KEY)
        if state is None:
            head.pop('ReplicationStatus')
        if logical == 'DeletionJournal':
            head.update(ObjectLockMode='COMPLIANCE', ObjectLockRetainUntilDate=NOW)
        self.source_heads[bucket, key, version] = head
        destination = backup.replica_bucket(self.config, logical)
        replica = {**head, 'ReplicationStatus': 'REPLICA'}
        if logical not in ('WebAssets', 'DeploymentAssets'):
            replica['SSEKMSKeyId'] = KEY
        self.replica_heads[destination, key, version] = replica
        return (bucket, key, version), (destination, key, version)

    def primary_outputs(self):
        return {'RegionalBackupPlanId': 'plan-owned', 'TombstoneSecret': TOMBSTONE}

    def assert_read_only(self, test):
        for client in self.clients.values():
            for method, _ in client.calls:
                test.assertTrue(method.startswith(('get_', 'describe_', 'list_', 'head_')), method)
                test.assertNotIn(method, ('get_object', 'get_secret_value'))
        test.assertNotIn('us-east-2', {region for _, region in self.requested_clients})


class InitialCopyCloud(RecoveryCloud):
    """Allow only the two explicitly scoped backup/copy mutations offline."""
    def __init__(self, c):
        self.mutation_configs = []
        super().__init__(c)
        self.clients.update({('rds', region): SDKClient('rds') for region in ('us-east-1', 'us-west-2')})
        self.clients['iam', None] = SDKClient('iam')
        self.source_cluster = {'DBClusterArn': CLUSTER, 'DBClusterIdentifier': backup.STACK,
            'DbClusterResourceId': 'cluster-original', 'ClusterCreateTime': NOW, 'Status': 'available',
            'Engine': 'aurora-postgresql', 'EngineVersion': '16.3', 'EngineMode': 'provisioned',
            'DeletionProtection': True, 'StorageEncrypted': True, 'KmsKeyId': SOURCE_KEY}
        self.source_snapshot = {'DBClusterSnapshotArn': SOURCE_POINT, 'Status': 'available',
            'DbClusterResourceId': self.source_cluster['DbClusterResourceId'], 'ClusterCreateTime': NOW,
            'Engine': 'aurora-postgresql', 'EngineVersion': '16.3', 'EngineMode': 'provisioned',
            'StorageEncrypted': True, 'KmsKeyId': SOURCE_KEY}
        self.destination_snapshot = {**self.source_snapshot, 'DBClusterSnapshotArn': DESTINATION_POINT,
                                     'KmsKeyId': KEY, 'SourceDBClusterSnapshotArn': SOURCE_POINT}
        self.client('rds', region_name='us-east-1').responses.update(
            describe_db_clusters=lambda **kwargs: {'DBClusters': [self.source_cluster]},
            describe_db_cluster_snapshots=lambda **kwargs: {'DBClusterSnapshots': [self.source_snapshot]},
            list_tags_for_resource=lambda **kwargs: {
                'TagList': [{'Key': key, 'Value': value} for key, value in self.backup_tags.items()]})
        self.client('rds', region_name='us-west-2').responses['describe_db_cluster_snapshots'] = lambda **kwargs: {
            'DBClusterSnapshots': [self.destination_snapshot]}
        self.client('iam').responses['get_role'] = {'Role': {'Path': '/',
            'RoleName': backup.backup_role_name(), 'RoleId': 'AROA12345678901234567', 'Arn': ROLE,
            'CreateDate': NOW, 'AssumeRolePolicyDocument': backup.extend_source_template(
                source_template(c), c, recovery_key_arn=KEY)['Resources']['RegionalBackupRole'][
                    'Properties']['AssumeRolePolicyDocument']}}
        primary = self.client('backup', region_name='us-east-1')
        primary.responses['describe_backup_vault'] = {'BackupVaultName': backup.vault_name('us-east-1'),
            'BackupVaultArn': SOURCE_VAULT, 'EncryptionKeyArn': SOURCE_KEY}
        self.backup_tokens = {}
        self.copy_tokens = {}
        self.backup_created_at = None
        self.copy_created_at = None
        self.backup_overrides = {}
        self.copy_overrides = {}
        self.backup_tags = {}
        self.lose_backup_response = False
        self.lose_copy_response = False
        primary.responses.update(start_backup_job=self.start_backup, start_copy_job=self.start_copy,
            describe_backup_job=lambda **kwargs: self.backup_job(),
            describe_copy_job=lambda **kwargs: {'CopyJob': self.copy_job_metadata()},
            describe_recovery_point={'RecoveryPointArn': SOURCE_POINT, 'ResourceArn': CLUSTER,
                'BackupVaultArn': SOURCE_VAULT, 'Status': 'COMPLETED', 'IsEncrypted': True,
                'EncryptionKeyArn': SOURCE_KEY, 'Lifecycle': {'DeleteAfterDays': 2}})
        self.client('backup', region_name='us-west-2').responses['describe_recovery_point'] = {
            'RecoveryPointArn': DESTINATION_POINT, 'ResourceArn': CLUSTER, 'BackupVaultArn': VAULT,
            'Status': 'COMPLETED', 'IsEncrypted': True, 'EncryptionKeyArn': KEY,
            'Lifecycle': {'DeleteAfterDays': 7}}
        self.requested_clients.clear()

    def client(self, service, *, region_name=None, config=None):
        if config is not None:
            self.mutation_configs.append(config)
        if service == 'iam' and region_name is None:
            self.requested_clients.append((service, None))
            return self.clients[service, None]
        return super().client(service, region_name=region_name)

    def primary_outputs(self):
        return {**super().primary_outputs(), 'DataKeyArn': SOURCE_KEY, 'RegionalBackupRoleArn': ROLE}

    def start_backup(self, **parameters):
        token = parameters['IdempotencyToken']
        if token not in self.backup_tokens:
            self.backup_tokens[token] = 'backup-job-owned'
            self.backup_created_at = datetime.now(timezone.utc)
            self.backup_tags = deepcopy(parameters['RecoveryPointTags'])
            self.clients['backup', 'us-east-1'].responses['describe_recovery_point']['CreationDate'] = self.backup_created_at
        if self.lose_backup_response:
            self.lose_backup_response = False
            raise TimeoutError('Unit-test backup response lost after creation')
        return {'BackupJobId': self.backup_tokens[token], 'RecoveryPointArn': SOURCE_POINT,
                'CreationDate': self.backup_created_at}

    def start_copy(self, **parameters):
        token = parameters['IdempotencyToken']
        if token not in self.copy_tokens:
            self.copy_tokens[token] = 'copy-job-owned'
            self.copy_created_at = datetime.now(timezone.utc)
            self.clients['backup', 'us-west-2'].responses['describe_recovery_point']['CreationDate'] = self.copy_created_at
        if self.lose_copy_response:
            self.lose_copy_response = False
            raise TimeoutError('Unit-test copy response lost after creation')
        return {'CopyJobId': self.copy_tokens[token], 'CreationDate': self.copy_created_at}

    def backup_job(self):
        return {'BackupJobId': 'backup-job-owned', 'AccountId': ACCOUNT, 'ResourceArn': CLUSTER,
            'IamRoleArn': ROLE, 'BackupVaultArn': SOURCE_VAULT, 'ResourceType': 'Aurora',
            'State': 'COMPLETED', 'CreationDate': self.backup_created_at, 'RecoveryPointArn': SOURCE_POINT,
            **self.backup_overrides}

    def copy_job_metadata(self):
        return {'CopyJobId': 'copy-job-owned', 'AccountId': ACCOUNT, 'ResourceArn': CLUSTER,
            'IamRoleArn': ROLE, 'ResourceType': 'Aurora', 'State': 'COMPLETED',
            'SourceRecoveryPointArn': SOURCE_POINT, 'SourceBackupVaultArn': SOURCE_VAULT,
            'DestinationRecoveryPointArn': DESTINATION_POINT, 'DestinationBackupVaultArn': VAULT,
            'CreationDate': self.copy_created_at, **self.copy_overrides}

    def assert_only_backup_copy_mutations(self, test):
        for client in self.clients.values():
            for method, _ in client.calls:
                test.assertTrue(method.startswith(('get_', 'describe_', 'list_', 'head_'))
                                or method in ('start_backup_job', 'start_copy_job'), method)
                test.assertNotIn(method, ('get_object', 'get_secret_value'))
        for config in self.mutation_configs:
            test.assertEqual(config.retries['total_max_attempts'], 1)


class FargateBackupTemplateTest(unittest.TestCase):
    def setUp(self):
        self.config = configuration()

    def test_every_entrypoint_rejects_foreign_regions_accounts_and_ohio_enrollment(self):
        bad = ({'region': 'us-east-2'}, {'backupRegion': 'us-east-2'}, {'backupRegion': 'us-west-1'},
               {'backupRegion': None}, {'environment': 'serverless-development'}, {'account': '12345678901'})
        for override in bad:
            c = {**self.config, **override}
            with self.subTest(override=override):
                for action in (lambda: backup.build_destination_template(c),
                               lambda: backup.extend_source_template({'Resources': {}}, c),
                               lambda: backup.replica_bucket(c, 'Artifacts'),
                               lambda: backup.primary_bucket(c, 'Artifacts')):
                    with self.assertRaises(Gate):
                        action()
        with self.assertRaises(Gate):
            backup.vault_name('us-east-2')

    def test_destination_has_only_retained_storage_keys_policies_and_vault(self):
        template = backup.build_destination_template(self.config)
        resources = template['Resources']
        self.assertEqual(len(resources), 13)
        self.assertEqual({row['Type'] for row in resources.values()}, {
            'AWS::KMS::Key', 'AWS::KMS::Alias', 'AWS::Backup::BackupVault',
            'AWS::S3::Bucket', 'AWS::S3::BucketPolicy'})
        self.assertEqual(sum(row['Type'] == 'AWS::S3::Bucket' for row in resources.values()), 5)
        for logical in ('RecoveryKey', 'RecoveryKeyAlias', 'RecoveryVault', *('Replica' + name for name in backup.BUCKETS)):
            self.assertEqual(resources[logical]['DeletionPolicy'], 'Retain')
            self.assertEqual(resources[logical]['UpdateReplacePolicy'], 'Retain')
        self.assertNotIn('us-east-2', json.dumps(template))
        self.assertNotIn('AWS::RDS::DBCluster', json.dumps(template))

    def test_all_five_destination_buckets_are_private_versioned_and_encrypted(self):
        resources = backup.build_destination_template(self.config)['Resources']
        for logical in backup.BUCKETS:
            props = resources['Replica' + logical]['Properties']
            self.assertEqual(props['BucketName'], backup.replica_bucket(self.config, logical))
            self.assertEqual(props['VersioningConfiguration'], {'Status': 'Enabled'})
            self.assertEqual(props['OwnershipControls']['Rules'], [{'ObjectOwnership': 'BucketOwnerEnforced'}])
            self.assertTrue(all(props['PublicAccessBlockConfiguration'].values()))
            encryption = props['BucketEncryption']['ServerSideEncryptionConfiguration']
            self.assertEqual(encryption, [{'BucketKeyEnabled': True, 'ServerSideEncryptionByDefault': {
                'SSEAlgorithm': 'aws:kms', 'KMSMasterKeyID': {'Fn::GetAtt': ['RecoveryKey', 'Arn']}}}])
            policy = resources['Replica' + logical + 'Policy']['Properties']['PolicyDocument']['Statement']
            self.assertTrue(any(row.get('Effect') == 'Deny' and
                row.get('Condition') == {'Bool': {'aws:SecureTransport': 'false'}} for row in policy))

    def test_journal_copies_keep_ninety_day_compliance_without_expiry(self):
        resources = backup.build_destination_template(self.config)['Resources']
        journal = resources['ReplicaDeletionJournal']['Properties']
        self.assertEqual(journal['ObjectLockConfiguration'], {'ObjectLockEnabled': 'Enabled',
            'Rule': {'DefaultRetention': {'Mode': 'COMPLIANCE', 'Days': 90}}})
        self.assertTrue(journal['ObjectLockEnabled'])
        self.assertNotIn('LifecycleConfiguration', journal)
        statements = resources['ReplicaDeletionJournalPolicy']['Properties']['PolicyDocument']['Statement']
        self.assertTrue(any(row.get('Effect') == 'Deny' and
            set(row.get('Action', [])) == {'s3:DeleteObject', 's3:DeleteObjectVersion'} for row in statements))
        expiry = resources['ReplicaExports']['Properties']['LifecycleConfiguration']['Rules'][0]
        self.assertEqual(expiry['ExpirationInDays'], 2)
        self.assertEqual(expiry['NoncurrentVersionExpiration'], {'NoncurrentDays': 1})

    def test_registry_and_platform_extensions_do_not_mutate_inputs_and_copy_every_bucket(self):
        for registry in (True, False):
            original = source_template(self.config, registry=registry)
            preserved = deepcopy(original)
            result = backup.extend_source_template(original, self.config, recovery_key_arn=KEY)
            self.assertEqual(original, preserved)
            self.assertEqual(result['Outputs']['ExistingOutput'], {'Value': 'preserved'})
            for logical in ('DeploymentAssets',) if registry else tuple(backup.BUCKETS)[:-1]:
                rule = result['Resources'][logical]['Properties']['ReplicationConfiguration']['Rules'][0]
                self.assertEqual(rule['Status'], 'Enabled')
                self.assertEqual(rule['DeleteMarkerReplication'], {'Status': 'Enabled'})
                self.assertEqual(rule['SourceSelectionCriteria'], {'SseKmsEncryptedObjects': {'Status': 'Enabled'}})
                self.assertEqual(rule['Destination'], {'Bucket': 'arn:aws:s3:::' + backup.replica_bucket(self.config, logical),
                    'StorageClass': 'STANDARD', 'EncryptionConfiguration': {'ReplicaKmsKeyID': KEY}})
            if registry:
                self.assertNotIn('RegionalBackupPlan', result['Resources'])
                self.assertNotIn('Database', result['Resources'])

    def test_replication_role_kms_access_is_confined_to_exact_bucket_contexts(self):
        result = backup.extend_source_template(source_template(self.config, registry=True), self.config, recovery_key_arn=KEY)
        role = result['Resources']['RegionalReplicationRole']['Properties']
        statements = role['Policies'][0]['PolicyDocument']['Statement']
        grants = [row for row in statements if any(action.startswith('kms:') for action in row['Action'])]
        self.assertEqual(len(grants), 2)
        for region, kind in (('us-east-1', backup.primary_bucket), ('us-west-2', backup.replica_bucket)):
            grant = next(row for row in grants if row['Condition']['StringEquals']['kms:ViaService'] == f's3.{region}.amazonaws.com')
            contexts = set(grant['Condition']['StringLike']['kms:EncryptionContext:aws:s3:arn'])
            buckets = {'arn:aws:s3:::' + kind(self.config, logical) for logical in backup.BUCKETS}
            self.assertEqual(contexts, buckets | {arn + '/*' for arn in buckets})
        self.assertEqual(grants[-1]['Resource'], KEY)
        self.assertNotIn('us-east-2', json.dumps(role))

    def test_database_schedule_copies_only_exact_primary_cluster_with_two_seven_day_retention(self):
        result = backup.extend_source_template(source_template(self.config), self.config, recovery_key_arn=KEY)
        rule = result['Resources']['RegionalBackupPlan']['Properties']['BackupPlan']['BackupPlanRule'][0]
        self.assertEqual(rule['TargetBackupVault'], {'Ref': 'PrimaryBackupVault'})
        self.assertNotIn('TargetBackupVaultName', rule)
        self.assertEqual(rule['Lifecycle'], {'DeleteAfterDays': 2})
        self.assertEqual(rule['CopyActions'], [{'DestinationBackupVaultArn': VAULT, 'Lifecycle': {'DeleteAfterDays': 7}}])
        self.assertFalse(rule['EnableContinuousBackup'])
        self.assertGreaterEqual(rule['StartWindowMinutes'], 60)
        selection = result['Resources']['RegionalBackupSelection']['Properties']['BackupSelection']
        self.assertEqual(selection, {'SelectionName': 'ExactVirginiaDatabase', 'IamRoleArn': ROLE, 'Resources': [CLUSTER]})
        self.assertNotIn('MoveToColdStorageAfterDays', json.dumps(result))
        self.assertNotIn('us-east-2', json.dumps(result))

    def test_plan_uses_key_parameter_and_actual_deploy_uses_exact_verified_uuid_arn(self):
        source = source_template(self.config)
        planned = backup.extend_source_template(source, self.config)
        deployed = backup.extend_source_template(source, self.config, recovery_key_arn=KEY)
        self.assertIn('RecoveryKeyArn', planned['Parameters'])
        self.assertEqual(planned['Outputs']['RecoveryKeyArn']['Value'], {'Ref': 'RecoveryKeyArn'})
        self.assertEqual(deployed['Outputs']['RecoveryKeyArn']['Value'], KEY)
        self.assertNotIn('RecoveryKeyArn', deployed.get('Parameters', {}))
        for invalid in (KEY.replace('us-west-2', 'us-east-2'), KEY.replace(ACCOUNT, '999999999999'),
                        f'arn:aws:kms:us-west-2:{ACCOUNT}:alias/recovery',
                        f'arn:aws:kms:us-west-2:{ACCOUNT}:key/' + '-' * 36, {'Ref': 'UnverifiedKey'}):
            with self.subTest(key=invalid), self.assertRaises(Gate):
                backup.extend_source_template(source, self.config, recovery_key_arn=invalid)

    def test_privacy_erasure_roles_exclude_journal_and_secret_has_only_west_replica(self):
        result = backup.extend_source_template(source_template(self.config), self.config, recovery_key_arn=KEY)
        self.assertEqual(result['Resources']['TombstoneSecret']['Properties']['ReplicaRegions'], [
            {'Region': 'us-west-2', 'KmsKeyId': KEY}])
        for logical in ('WorkerRole', 'MaintenanceRole'):
            policy = next(row for row in result['Resources'][logical]['Properties']['Policies']
                          if row['PolicyName'] == 'ReplicaPrivacyErasure')
            objects = policy['PolicyDocument']['Statement'][1]
            self.assertEqual(set(objects['Action']), {'s3:GetObjectVersion', 's3:DeleteObjectVersion'})
            self.assertEqual(set(objects['Resource']), {'arn:aws:s3:::' + backup.replica_bucket(self.config, name) + '/*'
                                                      for name in ('Artifacts', 'Exports')})
            self.assertNotIn('journal', json.dumps(policy))
        role = result['Resources']['RegionalBackupRole']['Properties']
        self.assertNotIn('AWSBackupServiceRolePolicyForRestores', json.dumps(role))

    def test_extension_rejects_foreign_bucket_names_before_installing_replication(self):
        for logical in backup.BUCKETS:
            source = source_template(self.config, registry=logical == 'DeploymentAssets')
            source['Resources'][logical]['Properties']['BucketName'] = backup.primary_bucket(self.config, logical).replace('us-east-1', 'us-east-2')
            with self.subTest(logical=logical), self.assertRaises(Gate):
                backup.extend_source_template(source, self.config, recovery_key_arn=KEY)


class FargateBackupVerificationTest(unittest.TestCase):
    def setUp(self):
        self.config = configuration()
        self.cloud = RecoveryCloud(self.config)

    def test_destination_verifies_sdk_shaped_reads_without_claiming_restore_or_standby(self):
        result = backup.verify_destination(self.cloud, self.config, self.cloud.outputs)
        self.assertTrue(result['backup_region_verified'])
        self.assertEqual(result['RecoveryKeyArn'], KEY)
        self.assertFalse(result['standby_compute_configured'])
        self.assertFalse(result['restore_executed'])
        self.assertFalse(result['regional_activation_supported'])
        s3 = self.cloud.clients['s3', 'us-west-2']
        self.assertEqual(sum(method == 'get_public_access_block' for method, _ in s3.calls), 5)
        self.cloud.assert_read_only(self)

    def test_destination_rejects_unverified_outputs_and_wrong_account_before_use(self):
        for changes in ({'RecoveryKeyArn': None}, {'RecoveryKeyArn': {'Ref': 'RecoveryKeyArn'}},
                        {'RecoveryKeyArn': KEY.replace('us-west-2', 'us-east-1')},
                        {'RecoveryVaultArn': VAULT.replace(ACCOUNT, '999999999999')},
                        {'ReplicaArtifactsBucket': 'foreign-bucket'}):
            with self.subTest(changes=changes), self.assertRaises(Gate):
                backup.verify_destination(self.cloud, self.config, {**self.cloud.outputs, **changes})
        self.cloud.clients['sts', 'us-west-2'].responses['get_caller_identity']['Account'] = '999999999999'
        with self.assertRaises(Gate):
            backup.verify_destination(self.cloud, self.config, self.cloud.outputs)
        self.cloud.assert_read_only(self)

    def test_destination_rejects_foreign_disabled_asymmetric_or_multiregion_key(self):
        for field, value in (('Arn', KEY.replace(ACCOUNT, '999999999999')), ('AWSAccountId', '999999999999'),
                             ('KeyState', 'PendingDeletion'), ('Enabled', False), ('KeyManager', 'AWS'),
                             ('KeySpec', 'RSA_2048'), ('KeyUsage', 'SIGN_VERIFY'), ('MultiRegion', True)):
            cloud = RecoveryCloud(self.config)
            cloud.clients['kms', 'us-west-2'].responses['describe_key']['KeyMetadata'][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.verify_destination(cloud, self.config, cloud.outputs)
            cloud.assert_read_only(self)

    def test_destination_rejects_wrong_vault_or_vault_key(self):
        for field, value in (('BackupVaultArn', VAULT.replace('us-west-2', 'us-east-2')),
                             ('EncryptionKeyArn', KEY.replace(KEY_ID, '87654321-1234-1234-1234-123456789abc'))):
            cloud = RecoveryCloud(self.config)
            cloud.clients['backup', 'us-west-2'].responses['describe_backup_vault'][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.verify_destination(cloud, self.config, cloud.outputs)

    def test_destination_requires_exact_protected_stable_cloudformation_stack_and_outputs(self):
        for field, value in (('StackId', STACK_ID.replace('us-west-2', 'us-east-2')),
                             ('StackStatus', 'UPDATE_IN_PROGRESS'), ('EnableTerminationProtection', False),
                             ('Outputs', [{'OutputKey': 'RecoveryKeyArn', 'OutputValue': KEY}])):
            cloud = RecoveryCloud(self.config)
            cloud.clients['cloudformation', 'us-west-2'].responses['describe_stacks']['Stacks'][0][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.verify_destination(cloud, self.config, cloud.outputs)

    def test_destination_rejects_template_drift_extra_compute_and_lost_retention(self):
        for kind in ('key', 'compute', 'retention'):
            cloud = RecoveryCloud(self.config)
            template = cloud.clients['cloudformation', 'us-west-2'].responses['get_template']['TemplateBody']
            if kind == 'key':
                template['Resources']['RecoveryKey']['Properties']['EnableKeyRotation'] = True
            elif kind == 'compute':
                template['Resources']['Standby'] = {'Type': 'AWS::ECS::Service', 'Properties': {}}
            else:
                template['Resources']['ReplicaDeletionJournal']['DeletionPolicy'] = 'Delete'
            with self.subTest(kind=kind), self.assertRaises(Gate):
                backup.verify_destination(cloud, self.config, cloud.outputs)

    def test_destination_accepts_sdk_template_json_object_order_without_weakening_content(self):
        cf = self.cloud.clients['cloudformation', 'us-west-2']
        cf.responses['get_template']['TemplateBody'] = json.dumps(self.cloud.destination, sort_keys=True)
        result = backup.verify_destination(self.cloud, self.config, self.cloud.outputs)
        self.assertTrue(result['backup_region_verified'])

    def test_destination_rejects_wrong_extra_incomplete_or_unbounded_resource_inventory(self):
        for kind in ('type', 'extra', 'status', 'pagination', 'missing'):
            cloud = RecoveryCloud(self.config)
            inventory = cloud.clients['cloudformation', 'us-west-2'].responses['list_stack_resources']
            rows = inventory['StackResourceSummaries']
            if kind == 'type':
                rows[0]['ResourceType'] = 'AWS::EC2::Instance'
            elif kind == 'extra':
                rows.append({**rows[0], 'LogicalResourceId': 'Extra', 'ResourceType': 'AWS::ECS::Service'})
            elif kind == 'status':
                rows[0]['ResourceStatus'] = 'CREATE_IN_PROGRESS'
            elif kind == 'pagination':
                inventory['NextToken'] = 'uninspected-resources'
            else:
                rows.pop()
            with self.subTest(kind=kind), self.assertRaises(Gate):
                backup.verify_destination(cloud, self.config, cloud.outputs)

    def test_destination_rejects_wrong_region_unversioned_public_or_unencrypted_bucket(self):
        mutations = [('get_bucket_location', 'LocationConstraint', 'us-east-2'),
            ('get_bucket_versioning', 'Status', 'Suspended'),
            ('get_public_access_block', 'PublicAccessBlockConfiguration', {}),
            ('get_bucket_encryption', 'ServerSideEncryptionConfiguration', {'Rules': []})]
        for method, field, value in mutations:
            cloud = RecoveryCloud(self.config)
            cloud.clients['s3', 'us-west-2'].responses[method][field] = value
            with self.subTest(method=method), self.assertRaises(Gate):
                backup.verify_destination(cloud, self.config, cloud.outputs)
            cloud.assert_read_only(self)

    def test_destination_rejects_lost_journal_compliance_or_shortened_retention(self):
        for mode, days in (('GOVERNANCE', 90), ('COMPLIANCE', 89)):
            cloud = RecoveryCloud(self.config)
            cloud.clients['s3', 'us-west-2'].responses['get_object_lock_configuration'][
                'ObjectLockConfiguration']['Rule']['DefaultRetention'] = {'Mode': mode, 'Days': days}
            with self.subTest(mode=mode, days=days), self.assertRaises(Gate):
                backup.verify_destination(cloud, self.config, cloud.outputs)

    def test_observer_distinguishes_configuration_pending_and_completed_copy_jobs(self):
        cases = ([], [self.cloud.copy_job('CREATED')], [self.cloud.copy_job('RUNNING')],
                 [self.cloud.copy_job('FAILED')], [self.cloud.copy_job('COMPLETED'),
                    self.cloud.copy_job('RUNNING', identifier='pending'),
                    self.cloud.copy_job('COMPLETED', identifier='second')])
        for jobs in cases:
            cloud = RecoveryCloud(self.config)
            cloud.clients['backup', 'us-east-1'].responses['list_copy_jobs']['CopyJobs'] = jobs
            result = backup.observe_database_copies(cloud, self.config, {'RegionalBackupPlanId': 'plan-owned'}, cloud.outputs)
            completed = [job['CopyJobId'] for job in jobs if job['State'] == 'COMPLETED']
            with self.subTest(states=[job['State'] for job in jobs]):
                self.assertEqual(result['completed_database_copy_count'], len(completed))
                self.assertEqual(result['completed_database_copy_ids'], completed)
                self.assertEqual(result['status'], 'database_copy_completed' if completed else 'configured_database_copy_not_yet_observed')
                self.assertFalse(result['restore_executed'])
                self.assertFalse(result['regional_activation_supported'])
                self.assertTrue(result['primary_authority_must_remain_retained'])
            cloud.assert_read_only(self)

    def test_observer_rejects_changed_source_rule_and_cold_or_pitr_copy_claim(self):
        for field, value in (('TargetBackupVaultName', 'foreign'), ('ScheduleExpression', 'cron(0 6 * * ? 2099)'),
                             ('Lifecycle', {'DeleteAfterDays': 1}), ('EnableContinuousBackup', True),
                             ('CopyActions', [{'DestinationBackupVaultArn': VAULT,
                               'Lifecycle': {'DeleteAfterDays': 97, 'MoveToColdStorageAfterDays': 7}}])):
            cloud = RecoveryCloud(self.config)
            cloud.clients['backup', 'us-east-1'].responses['get_backup_plan']['BackupPlan']['Rules'][0][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.observe_database_copies(cloud, self.config, {'RegionalBackupPlanId': 'plan-owned'}, cloud.outputs)

    def test_observer_rejects_extra_or_ohio_selections_and_wrong_role(self):
        overrides = ({'Resources': [CLUSTER, CLUSTER.replace('us-east-1', 'us-east-2')]},
                     {'Resources': [CLUSTER.replace('us-east-1', 'us-east-2')]},
                     {'IamRoleArn': ROLE.replace(ACCOUNT, '999999999999')},
                     {'ListOfTags': [{'ConditionType': 'STRINGEQUALS', 'ConditionKey': 'environment', 'ConditionValue': 'development'}]},
                     {'Conditions': {'StringEquals': [{'ConditionKey': 'aws:ResourceTag/project', 'ConditionValue': 'otgd'}]}},
                     {'NotResources': [CLUSTER]})
        for override in overrides:
            cloud = RecoveryCloud(self.config)
            cloud.clients['backup', 'us-east-1'].responses['get_backup_selection']['BackupSelection'].update(override)
            with self.subTest(override=override), self.assertRaises(Gate):
                backup.observe_database_copies(cloud, self.config, {'RegionalBackupPlanId': 'plan-owned'}, cloud.outputs)
        self.cloud.clients['backup', 'us-east-1'].responses['list_backup_selections']['BackupSelectionsList'].append({'SelectionId': 'foreign'})
        with self.assertRaises(Gate):
            backup.observe_database_copies(self.cloud, self.config, {'RegionalBackupPlanId': 'plan-owned'}, self.cloud.outputs)

    def test_observer_blocks_foreign_copy_targets_and_unbounded_inventory(self):
        for kind in ('resource', 'destination', 'pagination', 'excessive'):
            cloud = RecoveryCloud(self.config)
            response = cloud.clients['backup', 'us-east-1'].responses['list_copy_jobs']
            response['CopyJobs'] = [cloud.copy_job()]
            if kind == 'resource':
                response['CopyJobs'][0]['ResourceArn'] = CLUSTER.replace('us-east-1', 'us-east-2')
            elif kind == 'destination':
                response['CopyJobs'][0]['DestinationBackupVaultArn'] = VAULT.replace('us-west-2', 'us-east-2')
            elif kind == 'pagination':
                response['NextToken'] = 'uninspected-copies'
            else:
                response['CopyJobs'] *= 101
            with self.subTest(kind=kind), self.assertRaises(Gate):
                backup.observe_database_copies(cloud, self.config, {'RegionalBackupPlanId': 'plan-owned'}, cloud.outputs)

    def test_registry_verifies_replication_before_release_evidence_write(self):
        registry = {'DeploymentBucket': backup.primary_bucket(self.config, 'DeploymentAssets'),
                    'ReplicationRoleArn': f'arn:aws:iam::{ACCOUNT}:role/{backup.replication_role_name()}'}
        result = backup.verify_registry_configuration(self.cloud, self.config, registry, self.cloud.outputs)
        self.assertTrue(result['registry_replication_verified'])
        self.assertFalse(result['restore_executed'])
        calls = self.cloud.clients['s3', 'us-east-1'].calls
        self.assertEqual({parameters['Bucket'] for _, parameters in calls}, {registry['DeploymentBucket']})
        self.assertTrue(all(parameters.get('ExpectedBucketOwner') == ACCOUNT for _, parameters in calls))
        self.cloud.assert_read_only(self)

    def test_registry_rejects_ohio_bucket_wrong_role_and_disabled_replication(self):
        valid = {'DeploymentBucket': backup.primary_bucket(self.config, 'DeploymentAssets'),
                 'ReplicationRoleArn': f'arn:aws:iam::{ACCOUNT}:role/{backup.replication_role_name()}'}
        for field, value in (('DeploymentBucket', valid['DeploymentBucket'].replace('us-east-1', 'us-east-2')),
                             ('ReplicationRoleArn', valid['ReplicationRoleArn'].replace(ACCOUNT, '999999999999'))):
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.verify_registry_configuration(self.cloud, self.config, {**valid, field: value}, self.cloud.outputs)
        self.cloud.replications[valid['DeploymentBucket']]['Rules'][0]['Status'] = 'Disabled'
        with self.assertRaises(Gate):
            backup.verify_registry_configuration(self.cloud, self.config, valid, self.cloud.outputs)

    def test_full_observation_requires_database_s3_versions_and_secret_completion_together(self):
        for copies, versions, synchronized in ((False, True, True), (True, False, True),
                                             (True, True, False), (True, True, True)):
            cloud = RecoveryCloud(self.config)
            if copies:
                cloud.clients['backup', 'us-east-1'].responses['list_copy_jobs']['CopyJobs'] = [cloud.copy_job()]
            if versions:
                for logical in backup.BUCKETS:
                    cloud.add_version(logical, control=logical == 'DeletionJournal')
            if not synchronized:
                cloud.clients['secretsmanager', 'us-east-1'].responses['describe_secret']['ReplicationStatus'][0]['Status'] = 'InProgress'
            result = backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
            with self.subTest(copies=copies, versions=versions, synchronized=synchronized):
                self.assertEqual(result['status'], 'regional_copies_verified' if copies and versions and synchronized else 'configured_copies_pending')
                self.assertEqual(result['s3_source_version_count'], 5 if versions else 0)
                self.assertEqual(result['s3_replica_verified_version_count'], 5 if versions else 0)
                self.assertEqual(result['secret_replica_in_sync'], synchronized)
                self.assertFalse(result['restore_executed'])
                self.assertFalse(result['regional_activation_supported'])
            cloud.assert_read_only(self)

    def test_pending_failed_or_missing_source_metadata_does_not_claim_verified_replica(self):
        for state in ('PENDING', 'FAILED', None):
            cloud = RecoveryCloud(self.config)
            cloud.add_version('Artifacts', state=state)
            result = backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
            with self.subTest(state=state):
                self.assertEqual(result['s3_source_version_count'], 1)
                self.assertEqual(result['s3_replica_verified_version_count'], 0)
                self.assertEqual(result['s3_replication_pending_count'], 1)
                self.assertEqual(result['status'], 'configured_copies_pending')
            self.assertFalse(any(method == 'head_object' for method, _ in cloud.clients['s3', 'us-west-2'].calls))

    def test_missing_destination_version_stays_pending_and_access_denial_propagates(self):
        for code in ('NoSuchVersion', 'AccessDenied'):
            cloud = RecoveryCloud(self.config)
            cloud.add_version('Artifacts')
            def missing(**kwargs):
                raise ClientError({'Error': {'Code': code, 'Message': 'Fixture only'}}, 'HeadObject')
            cloud.clients['s3', 'us-west-2'].responses['head_object'] = missing
            if code == 'AccessDenied':
                with self.assertRaises(ClientError):
                    backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
            else:
                result = backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
                self.assertEqual(result['s3_replication_pending_count'], 1)
                self.assertEqual(result['s3_replica_verified_version_count'], 0)

    def test_full_observation_rejects_replica_version_encryption_length_and_checksum_drift(self):
        for field, value in (('VersionId', 'different-version'), ('ReplicationStatus', 'COMPLETED'),
                             ('ContentLength', 124), ('ServerSideEncryption', 'AES256'),
                             ('SSEKMSKeyId', KEY.replace('us-west-2', 'us-east-2')),
                             ('ChecksumSHA256', 'different-content')):
            cloud = RecoveryCloud(self.config)
            _, destination = cloud.add_version('Artifacts')
            cloud.replica_heads[destination][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)

    def test_full_observation_preserves_exact_journal_retention_and_tombstone_replica_target(self):
        for field, value in (('ObjectLockMode', 'GOVERNANCE'),
                             ('ObjectLockRetainUntilDate', datetime(2026, 10, 14, tzinfo=timezone.utc))):
            cloud = RecoveryCloud(self.config)
            _, destination = cloud.add_version('DeletionJournal')
            cloud.replica_heads[destination][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
        for field, value in (('Region', 'us-east-2'), ('KmsKeyId', KEY.replace(ACCOUNT, '999999999999'))):
            cloud = RecoveryCloud(self.config)
            cloud.clients['secretsmanager', 'us-east-1'].responses['describe_secret']['ReplicationStatus'][0][field] = value
            with self.subTest(field=field), self.assertRaises(Gate):
                backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)

    def test_full_observation_rejects_null_source_versions_and_extra_replication_rules(self):
        cloud = RecoveryCloud(self.config)
        cloud.versions[backup.primary_bucket(self.config, 'Artifacts')] = [{'Key': 'object', 'VersionId': 'null'}]
        with self.assertRaises(Gate):
            backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
        cloud = RecoveryCloud(self.config)
        rules = cloud.replications[backup.primary_bucket(self.config, 'Exports')]['Rules']
        rules.append(deepcopy(rules[0]))
        with self.assertRaises(Gate):
            backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)

    def test_delete_marker_copy_presence_is_required_without_reducing_verified_payload_count(self):
        for replicated in (True, False):
            cloud = RecoveryCloud(self.config)
            cloud.clients['backup', 'us-east-1'].responses['list_copy_jobs']['CopyJobs'] = [cloud.copy_job()]
            cloud.add_version('DeletionJournal', control=True)
            bucket = backup.primary_bucket(self.config, 'Artifacts')
            marker = {'Key': 'deleted/object', 'VersionId': 'deletion-marker-version'}
            cloud.source_markers[bucket] = [marker]
            if replicated:
                cloud.replica_markers[backup.replica_bucket(self.config, 'Artifacts')] = [marker]
            result = backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
            with self.subTest(replicated=replicated):
                self.assertEqual(result['s3_source_delete_marker_count'], 1)
                self.assertEqual(result['s3_replica_verified_version_count'], 1)
                self.assertEqual(result['s3_replication_pending_count'], 0 if replicated else 1)
                self.assertEqual(result['status'], 'regional_copies_verified' if replicated else 'configured_copies_pending')

    def test_arbitrary_completed_journal_version_does_not_substitute_for_establishment_witness(self):
        cloud = RecoveryCloud(self.config)
        cloud.clients['backup', 'us-east-1'].responses['list_copy_jobs']['CopyJobs'] = [cloud.copy_job()]
        cloud.add_version('DeletionJournal')
        result = backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)
        self.assertFalse(result['journal_control_replica_witness_verified'])
        self.assertEqual(result['s3_replica_verified_version_count'], 1)
        self.assertEqual(result['status'], 'configured_copies_pending')

    def test_publication_aes256_and_privacy_kms_versions_have_distinct_encryption_contracts(self):
        for logical, encryption, key in (('WebAssets', 'aws:kms', KEY),
                                        ('DeploymentAssets', 'aws:kms', KEY),
                                        ('Artifacts', 'AES256', None), ('Exports', 'AES256', None),
                                        ('DeletionJournal', 'AES256', None)):
            cloud = RecoveryCloud(self.config)
            source, destination = cloud.add_version(logical)
            for inventory, identifier in ((cloud.source_heads, source), (cloud.replica_heads, destination)):
                inventory[identifier]['ServerSideEncryption'] = encryption
                if key:
                    inventory[identifier]['SSEKMSKeyId'] = key
                else:
                    inventory[identifier].pop('SSEKMSKeyId', None)
            with self.subTest(logical=logical), self.assertRaises(Gate):
                backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)

    def test_current_establishment_version_must_remain_unchanged_after_replica_head(self):
        cloud = RecoveryCloud(self.config)
        cloud.add_version('DeletionJournal', control=True)
        original = cloud.source_head
        latest_reads = 0
        def changed(**parameters):
            nonlocal latest_reads
            result = original(**parameters)
            if parameters['Key'] == 'control/established.json' and 'VersionId' not in parameters:
                latest_reads += 1
                if latest_reads == 2:
                    result = {**result, 'VersionId': 'new-establishment-version'}
            return result
        cloud.clients['s3', 'us-east-1'].responses['head_object'] = changed
        with self.assertRaisesRegex(Gate, 'establishment changed'):
            backup.verify_configuration_and_copies(cloud, self.config, cloud.primary_outputs(), cloud.outputs)


class FargateInitialBackupCopyTest(unittest.TestCase):
    def setUp(self):
        self.config = {**configuration(), 'releaseId': 'a' * 40}
        self.cloud = InitialCopyCloud(self.config)

    def run_copy(self, cloud, path):
        return backup.ensure_initial_database_copy(cloud, self.config, cloud.primary_outputs(), cloud.outputs, path)

    def test_initial_copy_uses_scoped_sdk_mutations_and_keeps_database_identity_without_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-copy.json'
            result = self.run_copy(self.cloud, path)
            self.assertEqual(result['status'], 'initial-database-copy-verified')
            self.assertTrue(result['backup_copy_verified'])
            self.assertFalse(result['restore_executed'])
            self.assertFalse(result['regional_activation_supported'])
            self.assertEqual(result['database_resource_id'], 'cluster-original')
            self.assertEqual(result['source_recovery_point_arn'], SOURCE_POINT)
            self.assertEqual(result['destination_recovery_point_arn'], DESTINATION_POINT)
            self.assertEqual(json.loads(path.read_text()), result)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        calls = self.cloud.clients['backup', 'us-east-1'].calls
        mutations = [(method, parameters) for method, parameters in calls if method.startswith('start_')]
        self.assertEqual([method for method, _ in mutations], ['start_backup_job', 'start_copy_job'])
        self.assertEqual(mutations[0][1]['ResourceArn'], CLUSTER)
        self.assertEqual(mutations[0][1]['Lifecycle'], {'DeleteAfterDays': 2})
        self.assertEqual(mutations[1][1]['RecoveryPointArn'], SOURCE_POINT)
        self.assertEqual(mutations[1][1]['DestinationBackupVaultArn'], VAULT)
        self.assertEqual(mutations[1][1]['Lifecycle'], {'DeleteAfterDays': 7})
        tags = [(method, parameters) for method, parameters in self.cloud.clients['rds', 'us-east-1'].calls
                if method == 'list_tags_for_resource']
        self.assertEqual(tags, [('list_tags_for_resource', {'ResourceName': SOURCE_POINT})])
        self.assertNotIn('list_tags', [method for method, _ in calls])
        self.cloud.assert_only_backup_copy_mutations(self)

    def test_same_journal_resume_reuses_completed_jobs_without_additional_mutations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-copy.json'
            first = self.run_copy(self.cloud, path)
            second = self.run_copy(self.cloud, path)
            self.assertEqual(first['backup_job_id'], second['backup_job_id'])
            self.assertEqual(first['copy_job_id'], second['copy_job_id'])
        starts = [method for method, _ in self.cloud.clients['backup', 'us-east-1'].calls if method.startswith('start_')]
        self.assertEqual(starts, ['start_backup_job', 'start_copy_job'])

    def test_lost_backup_or_copy_response_retries_same_token_and_creates_no_duplicate_job(self):
        for boundary in ('backup', 'copy'):
            cloud = InitialCopyCloud(self.config)
            setattr(cloud, 'lose_' + boundary + '_response', True)
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'initial-copy.json'
                with self.assertRaises(TimeoutError):
                    self.run_copy(cloud, path)
                failed = json.loads(path.read_text())
                self.assertEqual(failed['status'], 'blocked-initial-copy-inspect-protected-journal-before-retry')
                self.assertEqual(failed['failed_phase'], boundary + '-requesting')
                result = self.run_copy(cloud, path)
                self.assertTrue(result['backup_copy_verified'])
                self.assertEqual(len(cloud.backup_tokens), 1)
                self.assertEqual(len(cloud.copy_tokens), 1)
                calls = [parameters['IdempotencyToken'] for method, parameters in cloud.clients['backup', 'us-east-1'].calls
                         if method == 'start_' + boundary + '_job']
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[0], calls[1])
            cloud.assert_only_backup_copy_mutations(self)

    def test_lost_response_retry_in_new_work_directory_reconciles_old_release_bound_job(self):
        self.cloud.lose_backup_response = True
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / 'lost-response.json'
            with self.assertRaises(TimeoutError):
                self.run_copy(self.cloud, first)
            previous = first.read_bytes()
            retry = Path(directory) / 'new-invocation.json'
            result = self.run_copy(self.cloud, retry)
            self.assertTrue(result['backup_copy_verified'])
            self.assertEqual(len(self.cloud.backup_tokens), 1)
            self.assertEqual(len(self.cloud.copy_tokens), 1)
            self.assertEqual(first.read_bytes(), previous)
            self.assertLess(self.cloud.backup_created_at, datetime.fromisoformat(result['started_at']))

    def test_existing_journal_token_tampering_is_rejected_without_repeating_mutations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-copy.json'
            self.run_copy(self.cloud, path)
            evidence = json.loads(path.read_text())
            evidence['copy_idempotency_token'] = 'copy-' + 'f' * 40
            path.write_text(json.dumps(evidence))
            with self.assertRaisesRegex(Gate, 'deterministic operation'):
                self.run_copy(self.cloud, path)
        starts = [method for method, _ in self.cloud.clients['backup', 'us-east-1'].calls if method.startswith('start_')]
        self.assertEqual(starts, ['start_backup_job', 'start_copy_job'])

    def test_backup_point_tags_must_bind_release_and_immutable_database_identity(self):
        for field in ('deployment', 'source_revision', 'initial_copy_binding'):
            cloud = InitialCopyCloud(self.config)
            cloud.clients['rds', 'us-east-1'].responses['list_tags_for_resource'] = lambda **kwargs: {
                'TagList': [{'Key': key, 'Value': value} for key, value in {
                    **cloud.backup_tags, field: 'foreign'}.items()]}
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(Gate, 'admitted release and request'):
                    self.run_copy(cloud, Path(directory) / 'initial-copy.json')
            self.assertFalse(any(method == 'start_copy_job' for method, _ in cloud.clients['backup', 'us-east-1'].calls))

    def test_native_snapshot_tags_reject_duplicate_and_incomplete_rows_before_copy(self):
        for rows in ([{'Key': 'deployment', 'Value': backup.STACK}] * 2,
                     [{'Key': 'deployment'}], [{'Value': backup.STACK}]):
            cloud = InitialCopyCloud(self.config)
            cloud.clients['rds', 'us-east-1'].responses['list_tags_for_resource'] = {'TagList': rows}
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(Gate, 'native recovery point tags are ambiguous'):
                    self.run_copy(cloud, Path(directory) / 'initial-copy.json')
            self.assertFalse(any(method == 'start_copy_job' for method, _ in cloud.clients['backup', 'us-east-1'].calls))

    def test_backup_role_rejects_foreign_arn_and_relaxed_assume_role_policy(self):
        for kind in ('arn', 'principal', 'source-account'):
            cloud = InitialCopyCloud(self.config)
            role = cloud.clients['iam', None].responses['get_role']['Role']
            if kind == 'arn':
                role['Arn'] = ROLE.replace(ACCOUNT, '999999999999')
            elif kind == 'principal':
                role['AssumeRolePolicyDocument']['Statement'][0]['Principal'] = {'Service': 'ecs-tasks.amazonaws.com'}
            else:
                role['AssumeRolePolicyDocument']['Statement'][0]['Condition']['StringEquals']['aws:SourceAccount'] = '999999999999'
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(Gate, 'scheduled service role'):
                    self.run_copy(cloud, Path(directory) / 'initial-copy.json')
            self.assertFalse(any(method.startswith('start_') for method, _ in cloud.clients['backup', 'us-east-1'].calls))

    def test_wrong_cluster_protection_status_or_key_blocks_before_backup(self):
        for field, value in (('Status', 'stopped'), ('DeletionProtection', False),
                             ('StorageEncrypted', False), ('KmsKeyId', KEY),
                             ('DBClusterArn', CLUSTER.replace('us-east-1', 'us-east-2')),
                             ('PendingModifiedValues', {'EngineVersion': '16.4'})):
            cloud = InitialCopyCloud(self.config)
            cloud.source_cluster[field] = value
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(Gate):
                    self.run_copy(cloud, Path(directory) / 'initial-copy.json')
            self.assertFalse(any(method.startswith('start_') for method, _ in cloud.clients['backup', 'us-east-1'].calls))

    def test_failed_or_foreign_backup_job_blocks_copy_and_records_failure(self):
        for field, value in (('State', 'FAILED'), ('AccountId', '999999999999'),
                             ('ResourceArn', CLUSTER.replace('us-east-1', 'us-east-2')),
                             ('BackupVaultArn', VAULT), ('IamRoleArn', ROLE.replace(ACCOUNT, '999999999999'))):
            cloud = InitialCopyCloud(self.config)
            cloud.backup_overrides[field] = value
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'initial-copy.json'
                with self.assertRaises(Gate):
                    self.run_copy(cloud, path)
                self.assertFalse(json.loads(path.read_text()).get('backup_copy_verified', False))
            self.assertFalse(any(method == 'start_copy_job' for method, _ in cloud.clients['backup', 'us-east-1'].calls))

    def test_wrong_source_snapshot_uid_or_destination_snapshot_key_never_passes(self):
        for side, field, value in (('source', 'DbClusterResourceId', 'cluster-replaced'),
                                   ('source', 'ClusterCreateTime', datetime(2026, 10, 14, tzinfo=timezone.utc)),
                                   ('destination', 'KmsKeyId', SOURCE_KEY),
                                   ('destination', 'EngineVersion', '16.4'),
                                   ('destination', 'DBClusterSnapshotArn', SOURCE_POINT),
                                   ('destination', 'SourceDBClusterSnapshotArn', DESTINATION_POINT)):
            cloud = InitialCopyCloud(self.config)
            getattr(cloud, side + '_snapshot')[field] = value
            with self.subTest(side=side, field=field), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(Gate):
                    self.run_copy(cloud, Path(directory) / 'initial-copy.json')
            cloud.assert_only_backup_copy_mutations(self)

    def test_source_snapshot_requires_uid_but_copied_optional_uid_requires_matching_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            for field in ('DbClusterResourceId', 'ClusterCreateTime', 'EngineMode'):
                self.cloud.destination_snapshot.pop(field)
            result = self.run_copy(self.cloud, Path(directory) / 'copy.json')
            self.assertTrue(result['backup_copy_verified'])
        cloud = InitialCopyCloud(self.config)
        cloud.source_snapshot.pop('DbClusterResourceId')
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(Gate):
            self.run_copy(cloud, Path(directory) / 'copy.json')

    def test_copy_job_and_final_recovery_point_must_match_exact_region_vault_lifecycle_and_key(self):
        for kind in ('copy-resource', 'copy-vault', 'point-lifecycle', 'point-key', 'point-status'):
            cloud = InitialCopyCloud(self.config)
            if kind == 'copy-resource':
                cloud.copy_overrides['ResourceArn'] = CLUSTER.replace('us-east-1', 'us-east-2')
            elif kind == 'copy-vault':
                cloud.copy_overrides['DestinationBackupVaultArn'] = SOURCE_VAULT
            else:
                response = cloud.clients['backup', 'us-west-2'].responses['describe_recovery_point']
                response.update({'point-lifecycle': {'Lifecycle': {'DeleteAfterDays': 30}},
                                 'point-key': {'EncryptionKeyArn': SOURCE_KEY},
                                 'point-status': {'Status': 'EXPIRED'}}[kind])
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(Gate):
                    self.run_copy(cloud, Path(directory) / 'initial-copy.json')

    def test_changed_original_cluster_uid_after_copy_blocks_receipt(self):
        cloud = self.cloud
        calls = 0
        def cluster(**parameters):
            nonlocal calls
            calls += 1
            row = deepcopy(cloud.source_cluster)
            if calls > 1:
                row['DbClusterResourceId'] = 'cluster-replaced'
            return {'DBClusters': [row]}
        cloud.clients['rds', 'us-east-1'].responses['describe_db_clusters'] = cluster
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'initial-copy.json'
            with self.assertRaisesRegex(Gate, 'source database authority'):
                self.run_copy(cloud, path)
            self.assertFalse(json.loads(path.read_text()).get('backup_copy_verified', False))

    def test_foreign_existing_journal_and_symlink_block_before_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'foreign.json'
            original.write_text(json.dumps({'account': '999999999999'}))
            original.chmod(0o600)
            with self.assertRaises(Gate):
                self.run_copy(self.cloud, original)
            link = Path(directory) / 'linked.json'
            link.symlink_to(original)
            with self.assertRaises(Gate):
                self.run_copy(self.cloud, link)
        self.assertFalse(any(method.startswith('start_') for method, _ in self.cloud.clients['backup', 'us-east-1'].calls))


if __name__ == '__main__':
    unittest.main()
