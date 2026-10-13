"""Cold, version-preserving recovery copies for the fresh Virginia deployment.

Oregon contains storage, keys and recovery points, never standby compute. These
copies do not authorize a different journal location or regional activation.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from pathlib import Path
import time

from botocore.config import Config
from botocore.exceptions import ClientError

from deploy.provenance import Gate, bounded_file, strict_loads


PRIMARY_REGION = 'us-east-1'
RECOVERY_REGION = 'us-west-2'
STACK = 'otgd-serverless-development'
RECOVERY_STACK = 'otgd-fargate-development-us-west-2-recovery'
BUCKETS = {'Artifacts': 'artifacts', 'Exports': 'exports', 'DeletionJournal': 'journal',
           'WebAssets': 'web', 'DeploymentAssets': 'deployments'}
KEY_PATTERN = (r'arn:aws:kms:us-west-2:{account}:key/[0-9a-f]{{8}}-'
               r'[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}')


def _validate(c):
    if (c.get('environment') != 'fargate-development' or c.get('region') != PRIMARY_REGION
            or c.get('backupRegion') != RECOVERY_REGION
            or not re.fullmatch(r'[0-9]{12}', str(c.get('account', '')))):
        raise Gate('Cold recovery requires the reviewed same-account Virginia/Oregon configuration')


def replica_bucket(c, logical):
    _validate(c)
    return f'otgd-fargate-recovery-{c["account"]}-{RECOVERY_REGION}-{BUCKETS[logical]}'


def primary_bucket(c, logical):
    _validate(c)
    return f'{STACK}-{c["account"]}-{PRIMARY_REGION}-{BUCKETS[logical]}'


def vault_name(region):
    if region not in (PRIMARY_REGION, RECOVERY_REGION):
        raise Gate('Backup vault region is outside the reviewed pair')
    return 'otgd-fargate-development-' + region


def replication_role_name():
    return 'otgd-fargate-development-us-east-1-replication'


def backup_role_name():
    return 'otgd-fargate-development-us-east-1-backup'


def _tags(c):
    return [{'Key': 'project', 'Value': 'one-the-go-detection'},
            {'Key': 'environment', 'Value': 'fargate-development'},
            {'Key': 'deployment', 'Value': STACK}, {'Key': 'owner_role', 'Value': 'platform-operator'},
            {'Key': 'purpose', 'Value': 'cold-regional-recovery'}]


def _bucket_arn(name):
    return 'arn:aws:s3:::' + name


def _vault_arn(c, region):
    return f'arn:aws:backup:{region}:{c["account"]}:backup-vault:{vault_name(region)}'


def _key(c, arn):
    if arn is None:
        return {'Ref': 'RecoveryKeyArn'}
    if not isinstance(arn, str) or not re.fullmatch(KEY_PATTERN.format(account=c['account']), arn):
        raise Gate('Cold recovery key must be the verified Oregon customer key ARN')
    return arn


def build_destination_template(c):
    """Build the separately deployed, retained Oregon storage stack."""
    _validate(c)
    account, tags = c['account'], _tags(c)
    key = {'Fn::GetAtt': ['RecoveryKey', 'Arn']}
    resources = {
        'RecoveryKey': {'Type': 'AWS::KMS::Key', 'DeletionPolicy': 'Retain', 'UpdateReplacePolicy': 'Retain',
            'Properties': {'Description': 'Encrypted Oregon recovery copies; no standby compute',
                'EnableKeyRotation': False, 'KeyPolicy': {'Version': '2012-10-17', 'Statement': [{
                    'Sid': 'AccountAdministration', 'Effect': 'Allow',
                    'Principal': {'AWS': f'arn:aws:iam::{account}:root'},
                    'Action': 'kms:*', 'Resource': '*'}]}, 'Tags': tags}},
        'RecoveryKeyAlias': {'Type': 'AWS::KMS::Alias', 'DeletionPolicy': 'Retain', 'UpdateReplacePolicy': 'Retain',
            'Properties': {'AliasName': 'alias/' + RECOVERY_STACK, 'TargetKeyId': {'Ref': 'RecoveryKey'}}},
        'RecoveryVault': {'Type': 'AWS::Backup::BackupVault', 'DeletionPolicy': 'Retain',
            'UpdateReplacePolicy': 'Retain', 'Properties': {'BackupVaultName': vault_name(RECOVERY_REGION),
                'EncryptionKeyArn': key, 'BackupVaultTags': {t['Key']: t['Value'] for t in tags},
                'AccessPolicy': {'Version': '2012-10-17', 'Statement': [{
                    'Effect': 'Allow', 'Principal': {'AWS': f'arn:aws:iam::{account}:root'},
                    'Action': ['backup:CopyIntoBackupVault'], 'Resource': _vault_arn(c, RECOVERY_REGION),
                    'Condition': {'ArnEquals': {'aws:PrincipalArn':
                        f'arn:aws:iam::{account}:role/{backup_role_name()}'}}}]}}},
    }
    outputs = {'RecoveryKeyArn': {'Value': key},
               'RecoveryVaultArn': {'Value': {'Fn::GetAtt': ['RecoveryVault', 'BackupVaultArn']}},
               'RecoveryVaultName': {'Value': {'Ref': 'RecoveryVault'}}}
    for logical in BUCKETS:
        name = replica_bucket(c, logical)
        properties = {'BucketName': name, 'VersioningConfiguration': {'Status': 'Enabled'},
            'OwnershipControls': {'Rules': [{'ObjectOwnership': 'BucketOwnerEnforced'}]},
            'PublicAccessBlockConfiguration': {'BlockPublicAcls': True, 'IgnorePublicAcls': True,
                'BlockPublicPolicy': True, 'RestrictPublicBuckets': True},
            'BucketEncryption': {'ServerSideEncryptionConfiguration': [{
                'BucketKeyEnabled': True, 'ServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms', 'KMSMasterKeyID': key}}]}, 'Tags': tags}
        if logical == 'DeletionJournal':
            properties.update(ObjectLockEnabled=True, ObjectLockConfiguration={'ObjectLockEnabled': 'Enabled',
                'Rule': {'DefaultRetention': {'Mode': 'COMPLIANCE', 'Days': 90}}})
        if logical == 'Exports':
            properties['LifecycleConfiguration'] = {'Rules': [{'Id': 'ExpiredExports', 'Status': 'Enabled',
                'ExpirationInDays': 2, 'NoncurrentVersionExpiration': {'NoncurrentDays': 1},
                'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 1}}]}
        resources['Replica' + logical] = {'Type': 'AWS::S3::Bucket', 'Properties': properties,
            'DeletionPolicy': 'Retain', 'UpdateReplacePolicy': 'Retain'}
        statements = [{'Effect': 'Deny', 'Principal': '*', 'Action': 's3:*',
            'Resource': [_bucket_arn(name), _bucket_arn(name) + '/*'],
            'Condition': {'Bool': {'aws:SecureTransport': 'false'}}}]
        if logical == 'DeletionJournal':
            statements.append({'Effect': 'Deny', 'Principal': '*',
                'Action': ['s3:DeleteObject', 's3:DeleteObjectVersion'], 'Resource': _bucket_arn(name) + '/*'})
        resources['Replica' + logical + 'Policy'] = {'Type': 'AWS::S3::BucketPolicy',
            'Properties': {'Bucket': {'Ref': 'Replica' + logical},
                'PolicyDocument': {'Version': '2012-10-17', 'Statement': statements}}}
        outputs['Replica' + logical + 'Bucket'] = {'Value': {'Ref': 'Replica' + logical}}
    return {'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'Retained Oregon recovery storage; no running standby services',
        'Resources': resources, 'Outputs': outputs}


def extend_source_template(template, c, *, recovery_key_arn=None):
    """Add the reviewed registry/platform replication and database backup graph.

    A plan may leave RecoveryKeyArn as a parameter. Actual deployment supplies
    the key obtained from live verification of the separate Oregon stack.
    """
    _validate(c)
    result = deepcopy(template)
    resources, outputs = result['Resources'], result.setdefault('Outputs', {})
    account, tags, key = c['account'], _tags(c), _key(c, recovery_key_arn)
    if recovery_key_arn is None:
        result.setdefault('Parameters', {})['RecoveryKeyArn'] = {'Type': 'String',
            'AllowedPattern': KEY_PATTERN.format(account=account),
            'Description': 'Verified customer managed key ARN from the Oregon recovery stack'}
    role_arn = f'arn:aws:iam::{account}:role/{replication_role_name()}'
    # Registry precedes the platform and owns the shared replication role. Its
    # encryption context restricts decryption to these exact source buckets.
    if 'DeploymentAssets' in resources:
        primary_arns = [_bucket_arn(primary_bucket(c, name)) for name in BUCKETS]
        replica_arns = [_bucket_arn(replica_bucket(c, name)) for name in BUCKETS]
        resources['RegionalReplicationRole'] = {'Type': 'AWS::IAM::Role', 'DeletionPolicy': 'Retain',
            'UpdateReplacePolicy': 'Retain', 'Properties': {'RoleName': replication_role_name(),
                'AssumeRolePolicyDocument': {'Version': '2012-10-17', 'Statement': [{
                    'Effect': 'Allow', 'Principal': {'Service': 's3.amazonaws.com'}, 'Action': 'sts:AssumeRole',
                    'Condition': {'StringEquals': {'aws:SourceAccount': account},
                                  'ArnLike': {'aws:SourceArn': primary_arns}}}]},
                'Policies': [{'PolicyName': 'ExactRegionalCopies', 'PolicyDocument': {'Version': '2012-10-17',
                    'Statement': [
                        {'Effect': 'Allow', 'Action': ['s3:GetReplicationConfiguration', 's3:ListBucket'],
                         'Resource': primary_arns},
                        {'Effect': 'Allow', 'Action': ['s3:GetObjectVersionForReplication',
                            's3:GetObjectVersionAcl', 's3:GetObjectVersionTagging', 's3:GetObjectRetention',
                            's3:GetObjectLegalHold'], 'Resource': [arn + '/*' for arn in primary_arns]},
                        {'Effect': 'Allow', 'Action': ['s3:ReplicateObject', 's3:ReplicateDelete',
                            's3:ReplicateTags'], 'Resource': [arn + '/*' for arn in replica_arns]},
                        {'Effect': 'Allow', 'Action': ['kms:Decrypt'], 'Resource':
                            f'arn:aws:kms:{PRIMARY_REGION}:{account}:key/*', 'Condition': {
                                'StringEquals': {'kms:ViaService': f's3.{PRIMARY_REGION}.amazonaws.com'},
                                'StringLike': {'kms:EncryptionContext:aws:s3:arn':
                                    primary_arns + [arn + '/*' for arn in primary_arns]}}},
                        {'Effect': 'Allow', 'Action': ['kms:Encrypt', 'kms:Decrypt', 'kms:GenerateDataKey'],
                         'Resource': key, 'Condition': {
                            'StringEquals': {'kms:ViaService': f's3.{RECOVERY_REGION}.amazonaws.com'},
                            'StringLike': {'kms:EncryptionContext:aws:s3:arn':
                                replica_arns + [arn + '/*' for arn in replica_arns]}}},
                    ]}}], 'Tags': tags}}
        outputs['ReplicationRoleArn'] = {'Value': {'Fn::GetAtt': ['RegionalReplicationRole', 'Arn']}}
    for logical in BUCKETS:
        if logical not in resources:
            continue
        resource = resources[logical]
        if resource.get('Type') != 'AWS::S3::Bucket' or resource['Properties'].get('BucketName') != primary_bucket(c, logical):
            raise Gate('Regional copying requires the exact named primary buckets')
        resource['Properties']['ReplicationConfiguration'] = {'Role': role_arn,
            'Rules': [{'Id': 'ColdOregonVersions', 'Priority': 1, 'Status': 'Enabled', 'Filter': {'Prefix': ''},
                'DeleteMarkerReplication': {'Status': 'Enabled'},
                'SourceSelectionCriteria': {'SseKmsEncryptedObjects': {'Status': 'Enabled'}},
                'Destination': {'Bucket': _bucket_arn(replica_bucket(c, logical)),
                    'StorageClass': 'STANDARD', 'EncryptionConfiguration': {'ReplicaKmsKeyID': key}}}]}
        if logical in ('Artifacts', 'Exports'):
            # Lifecycle permanent deletion cannot wait for replication. The
            # retained worker references enforce expiry and erase both regions.
            resource['Properties']['LifecycleConfiguration'] = {'Rules': [{
                'Id': 'AbandonedMultipart', 'Status': 'Enabled',
                'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 1}}]}
        if logical == 'DeploymentAssets':
            resource['DependsOn'] = 'RegionalReplicationRole'
    if 'Database' not in resources:
        return result
    cluster_arn = f'arn:aws:rds:{PRIMARY_REGION}:{account}:cluster:{STACK}'
    backup_role_arn = f'arn:aws:iam::{account}:role/{backup_role_name()}'
    resources['RegionalBackupRole'] = {'Type': 'AWS::IAM::Role', 'DeletionPolicy': 'Retain',
        'UpdateReplacePolicy': 'Retain', 'Properties': {'RoleName': backup_role_name(),
            'AssumeRolePolicyDocument': {'Version': '2012-10-17', 'Statement': [{
                'Effect': 'Allow', 'Principal': {'Service': 'backup.amazonaws.com'}, 'Action': 'sts:AssumeRole',
                'Condition': {'StringEquals': {'aws:SourceAccount': account},
                    'ArnLike': {'aws:SourceArn': f'arn:aws:backup:{PRIMARY_REGION}:{account}:*'}}}]},
            'ManagedPolicyArns': ['arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup'],
            'Policies': [{'PolicyName': 'RegionalVaultEncryption', 'PolicyDocument': {'Version': '2012-10-17',
                'Statement': [{'Effect': 'Allow', 'Action': ['kms:Decrypt', 'kms:Encrypt', 'kms:GenerateDataKey',
                    'kms:DescribeKey'], 'Resource': [{'Fn::GetAtt': ['DataKey', 'Arn']}, key]},
                    {'Effect': 'Allow', 'Action': ['kms:CreateGrant'],
                     'Resource': [{'Fn::GetAtt': ['DataKey', 'Arn']}, key],
                     'Condition': {'Bool': {'kms:GrantIsForAWSResource': 'true'}}},
                    {'Effect': 'Allow', 'Action': ['backup:CopyFromBackupVault', 'backup:CopyIntoBackupVault'],
                     'Resource': [_vault_arn(c, PRIMARY_REGION), _vault_arn(c, RECOVERY_REGION)]}]}}], 'Tags': tags}}
    resources['PrimaryBackupVault'] = {'Type': 'AWS::Backup::BackupVault', 'DeletionPolicy': 'Retain',
        'UpdateReplacePolicy': 'Retain', 'Properties': {'BackupVaultName': vault_name(PRIMARY_REGION),
            'EncryptionKeyArn': {'Fn::GetAtt': ['DataKey', 'Arn']},
            'BackupVaultTags': {t['Key']: t['Value'] for t in tags}}}
    resources['RegionalBackupPlan'] = {'Type': 'AWS::Backup::BackupPlan', 'Properties': {
        'BackupPlan': {'BackupPlanName': 'otgd-fargate-development-us-east-1', 'BackupPlanRule': [{
            'RuleName': 'DailyEncryptedOregonCopy', 'TargetBackupVault': {'Ref': 'PrimaryBackupVault'},
            'ScheduleExpression': 'cron(0 6 * * ? *)', 'StartWindowMinutes': 60,
            'CompletionWindowMinutes': 360, 'EnableContinuousBackup': False,
            'Lifecycle': {'DeleteAfterDays': 2}, 'CopyActions': [{
                'DestinationBackupVaultArn': _vault_arn(c, RECOVERY_REGION),
                'Lifecycle': {'DeleteAfterDays': 7}}]}]},
        'BackupPlanTags': {t['Key']: t['Value'] for t in tags}}}
    resources['RegionalBackupSelection'] = {'Type': 'AWS::Backup::BackupSelection', 'Properties': {
        'BackupPlanId': {'Ref': 'RegionalBackupPlan'}, 'BackupSelection': {
            'SelectionName': 'ExactVirginiaDatabase', 'IamRoleArn': backup_role_arn, 'Resources': [cluster_arn]}},
        'DependsOn': 'RegionalBackupRole'}
    resources['TombstoneSecret']['Properties']['ReplicaRegions'] = [{'Region': RECOVERY_REGION, 'KmsKeyId': key}]
    replicas = [_bucket_arn(replica_bucket(c, name)) for name in ('Artifacts', 'Exports')]
    for logical in ('WorkerRole', 'MaintenanceRole'):
        resources[logical]['Properties']['Policies'].append({'PolicyName': 'ReplicaPrivacyErasure',
            'PolicyDocument': {'Version': '2012-10-17', 'Statement': [
                {'Effect': 'Allow', 'Action': ['s3:ListBucket', 's3:ListBucketVersions', 's3:GetBucketLocation'],
                 'Resource': replicas},
                {'Effect': 'Allow', 'Action': ['s3:GetObjectVersion', 's3:DeleteObjectVersion'],
                 'Resource': [arn + '/*' for arn in replicas]}]}})
    for name, value in {'PrimaryBackupVaultName': {'Ref': 'PrimaryBackupVault'},
        'RegionalBackupPlanId': {'Ref': 'RegionalBackupPlan'}, 'RegionalBackupRoleArn': backup_role_arn,
        'RecoveryVaultArn': _vault_arn(c, RECOVERY_REGION), 'RecoveryKeyArn': key,
        'BackupRegion': RECOVERY_REGION,
        **{'Replica' + name + 'Bucket': replica_bucket(c, name) for name in BUCKETS}}.items():
        outputs[name] = {'Value': value}
    return result


def _one(response, field):
    rows = response.get(field, [])
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise Gate('Cold recovery metadata is ambiguous')
    return rows[0]


def verify_destination(aws, c, outputs):
    """Verify actual Oregon storage/encryption without reading application data."""
    _validate(c)
    key = _key(c, outputs.get('RecoveryKeyArn'))
    if not isinstance(key, str) or outputs.get('RecoveryVaultArn') != _vault_arn(c, RECOVERY_REGION):
        raise Gate('Cold recovery outputs do not bind the exact vault and actual key')
    if aws.client('sts', region_name=RECOVERY_REGION).get_caller_identity().get('Account') != c['account']:
        raise Gate('Cold recovery account differs from the primary account')
    cf = aws.client('cloudformation', region_name=RECOVERY_REGION)
    stack = _one(cf.describe_stacks(StackName=RECOVERY_STACK), 'Stacks')
    if (not str(stack.get('StackId', '')).startswith(
            f'arn:aws:cloudformation:{RECOVERY_REGION}:{c["account"]}:stack/{RECOVERY_STACK}/')
            or stack.get('StackStatus') not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE')
            or stack.get('EnableTerminationProtection') is not True
            or {row['OutputKey']: row['OutputValue'] for row in stack.get('Outputs', [])} != outputs):
        raise Gate('Cold recovery outputs must come from its exact protected stable stack')
    template = cf.get_template(StackName=stack['StackId'], TemplateStage='Original')['TemplateBody']
    if isinstance(template, str):
        from deploy.provenance import strict_loads
        template = strict_loads(template)
    if json.dumps(template, sort_keys=True, separators=(',', ':')) != json.dumps(
            build_destination_template(c), sort_keys=True, separators=(',', ':')):
        raise Gate('Cold recovery stack template differs from the storage-only plan')
    inventory = cf.list_stack_resources(StackName=stack['StackId'])
    rows = inventory.get('StackResourceSummaries', [])
    expected = build_destination_template(c)['Resources']
    if (inventory.get('NextToken') or len(rows) != len(expected)
            or {row.get('LogicalResourceId'): row.get('ResourceType') for row in rows} !=
                {name: resource['Type'] for name, resource in expected.items()}
            or any(row.get('ResourceStatus') not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE') for row in rows)):
        raise Gate('Cold recovery inventory differs from its exact storage-only graph')
    kms = aws.client('kms', region_name=RECOVERY_REGION)
    metadata = kms.describe_key(KeyId=key).get('KeyMetadata', {})
    if (metadata.get('Arn') != key or metadata.get('AWSAccountId') != c['account']
            or metadata.get('KeyState') != 'Enabled' or metadata.get('Enabled') is not True
            or metadata.get('KeyManager') != 'CUSTOMER' or metadata.get('KeySpec') != 'SYMMETRIC_DEFAULT'
            or metadata.get('KeyUsage') != 'ENCRYPT_DECRYPT' or metadata.get('MultiRegion') is not False):
        raise Gate('Cold recovery encryption key is unavailable or differs')
    vault = aws.client('backup', region_name=RECOVERY_REGION).describe_backup_vault(
        BackupVaultName=vault_name(RECOVERY_REGION))
    if (vault.get('BackupVaultArn') != _vault_arn(c, RECOVERY_REGION)
            or vault.get('EncryptionKeyArn') != key):
        raise Gate('Cold recovery vault encryption differs')
    s3 = aws.client('s3', region_name=RECOVERY_REGION)
    for logical in BUCKETS:
        bucket = replica_bucket(c, logical)
        if outputs.get('Replica' + logical + 'Bucket') != bucket:
            raise Gate('Cold recovery bucket outputs differ')
        owner = {'Bucket': bucket, 'ExpectedBucketOwner': c['account']}
        if (s3.get_bucket_location(**owner).get('LocationConstraint') != RECOVERY_REGION
                or s3.get_bucket_versioning(**owner).get('Status') != 'Enabled'
                or s3.get_public_access_block(**owner).get('PublicAccessBlockConfiguration') !=
                   {'BlockPublicAcls': True, 'IgnorePublicAcls': True, 'BlockPublicPolicy': True, 'RestrictPublicBuckets': True}):
            raise Gate('Cold recovery buckets must be private versioned Oregon storage')
        encryption = s3.get_bucket_encryption(**owner).get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
        if (len(encryption) != 1 or encryption[0].get('ApplyServerSideEncryptionByDefault') !=
                {'SSEAlgorithm': 'aws:kms', 'KMSMasterKeyID': key} or encryption[0].get('BucketKeyEnabled') is not True):
            raise Gate('Cold recovery bucket encryption differs from the verified key')
        if logical == 'DeletionJournal':
            lock = s3.get_object_lock_configuration(**owner).get('ObjectLockConfiguration', {})
            if lock != {'ObjectLockEnabled': 'Enabled',
                       'Rule': {'DefaultRetention': {'Mode': 'COMPLIANCE', 'Days': 90}}}:
                raise Gate('Cold recovery journal requires retained compliance protection')
    return {**outputs, 'backup_region_verified': True, 'standby_compute_configured': False,
            'restore_executed': False, 'regional_activation_supported': False}


def _verify_source_bucket(s3, c, logical, key):
    options = {'Bucket': primary_bucket(c, logical), 'ExpectedBucketOwner': c['account']}
    if (s3.get_bucket_location(**options).get('LocationConstraint') not in (None, PRIMARY_REGION)
            or s3.get_bucket_versioning(**options).get('Status') != 'Enabled'):
        raise Gate('Regional replication source must be the owned versioned Virginia bucket')
    configuration = s3.get_bucket_replication(**options).get('ReplicationConfiguration', {})
    rules = configuration.get('Rules', [])
    if (configuration.get('Role') != f'arn:aws:iam::{c["account"]}:role/{replication_role_name()}'
            or len(rules) != 1):
        raise Gate('Regional replication must use its exact registry role and one destination')
    rule = rules[0]
    destination = rule.get('Destination', {})
    if (rule.get('ID') != 'ColdOregonVersions' or rule.get('Priority') != 1 or rule.get('Status') != 'Enabled'
            or rule.get('Filter') != {'Prefix': ''} or rule.get('DeleteMarkerReplication') != {'Status': 'Enabled'}
            or rule.get('SourceSelectionCriteria', {}).get('SseKmsEncryptedObjects') != {'Status': 'Enabled'}
            or destination.get('Bucket') != _bucket_arn(replica_bucket(c, logical))
            or destination.get('StorageClass') != 'STANDARD'
            or destination.get('EncryptionConfiguration') != {'ReplicaKmsKeyID': key}):
        raise Gate('Regional replication version, encryption or destination binding differs')


def verify_registry_configuration(aws, c, registry_outputs, recovery_outputs):
    """Verify registry replication before the first release-evidence write."""
    destination = verify_destination(aws, c, recovery_outputs)
    if (registry_outputs.get('DeploymentBucket') != primary_bucket(c, 'DeploymentAssets')
            or registry_outputs.get('ReplicationRoleArn') !=
                f'arn:aws:iam::{c["account"]}:role/{replication_role_name()}'):
        raise Gate('Registry copying must use the exact Virginia bucket and replication role')
    _verify_source_bucket(aws.client('s3', region_name=PRIMARY_REGION), c, 'DeploymentAssets',
        destination['RecoveryKeyArn'])
    return {'registry_replication_verified': True, 'backup_region': RECOVERY_REGION,
            'recovery_key_arn': destination['RecoveryKeyArn'], 'restore_executed': False}


def observe_database_copies(aws, c, outputs, recovery_outputs):
    """Distinguish verified configuration from actual completed database copies."""
    destination = verify_destination(aws, c, recovery_outputs)
    backup = aws.client('backup', region_name=PRIMARY_REGION)
    plan_id = outputs.get('RegionalBackupPlanId')
    if not isinstance(plan_id, str) or not plan_id:
        raise Gate('Primary backup plan identifier is required')
    plan = backup.get_backup_plan(BackupPlanId=plan_id).get('BackupPlan', {})
    rules = plan.get('Rules', [])
    if (len(rules) != 1 or rules[0].get('TargetBackupVaultName') != vault_name(PRIMARY_REGION)
            or rules[0].get('ScheduleExpression') != 'cron(0 6 * * ? *)'
            or rules[0].get('Lifecycle') != {'DeleteAfterDays': 2}
            or rules[0].get('CopyActions') != [{'DestinationBackupVaultArn': _vault_arn(c, RECOVERY_REGION),
                                             'Lifecycle': {'DeleteAfterDays': 7}}]
            or rules[0].get('EnableContinuousBackup', False) is not False):
        raise Gate('Primary backup schedule or copy lifecycle differs')
    cluster = f'arn:aws:rds:{PRIMARY_REGION}:{c["account"]}:cluster:{STACK}'
    inventory = backup.list_backup_selections(BackupPlanId=plan_id, MaxResults=100)
    selections = inventory.get('BackupSelectionsList', [])
    if inventory.get('NextToken') or len(selections) != 1 or not isinstance(selections[0].get('SelectionId'), str):
        raise Gate('Primary backup selection is ambiguous')
    selection = backup.get_backup_selection(BackupPlanId=plan_id,
        SelectionId=selections[0]['SelectionId']).get('BackupSelection', {})
    if (selection.get('Resources') != [cluster] or selection.get('NotResources')
            or selection.get('ListOfTags') or any(selection.get('Conditions', {}).values())
            or selection.get('IamRoleArn') != f'arn:aws:iam::{c["account"]}:role/{backup_role_name()}'):
        raise Gate('Backup selection must include only the exact Virginia database')
    response = backup.list_copy_jobs(ByResourceArn=cluster, ByDestinationVaultArn=_vault_arn(c, RECOVERY_REGION),
        MaxResults=100)
    if response.get('NextToken'):
        raise Gate('Database copy inventory exceeds the bounded initial verification')
    jobs = response.get('CopyJobs', [])
    if len(jobs) > 100 or any(job.get('ResourceArn') != cluster
            or job.get('DestinationBackupVaultArn') != _vault_arn(c, RECOVERY_REGION) for job in jobs):
        raise Gate('Database copy job target differs')
    completed = [job for job in jobs if job.get('State') == 'COMPLETED']
    return {'schema_version': '1.0.0', 'operation': 'cold-regional-backup-observation',
        'account': c['account'], 'primary_region': PRIMARY_REGION, 'backup_region': RECOVERY_REGION,
        'status': 'database_copy_completed' if completed else 'configured_database_copy_not_yet_observed',
        'completed_database_copy_count': len(completed),
        'completed_database_copy_ids': [job['CopyJobId'] for job in completed],
        'restore_executed': False, 'regional_activation_supported': False,
        'primary_authority_must_remain_retained': True, 'standby_compute_configured': False,
        'recovery_key_arn': destination['RecoveryKeyArn'],
        'observed_at': datetime.now(timezone.utc).isoformat()}


def verify_configuration_and_copies(aws, c, primary_outputs, recovery_outputs):
    """Record observed copies separately from configuration and restore claims."""
    observation = observe_database_copies(aws, c, primary_outputs, recovery_outputs)
    key = recovery_outputs['RecoveryKeyArn']
    source = aws.client('s3', region_name=PRIMARY_REGION)
    destination = aws.client('s3', region_name=RECOVERY_REGION)
    versions, payload_pending, marker_pending, markers = 0, 0, 0, 0
    for logical in BUCKETS:
        _verify_source_bucket(source, c, logical, key)
        options = {'Bucket': primary_bucket(c, logical), 'ExpectedBucketOwner': c['account']}
        source_markers = []
        for number, page in enumerate(source.get_paginator('list_object_versions').paginate(**options)):
            if number >= 20:
                raise Gate('Regional copy inventory exceeds its bound')
            for row in page.get('Versions', []):
                versions += 1
                if versions > 10000 or not isinstance(row.get('VersionId'), str) or row['VersionId'] == 'null':
                    raise Gate('Regional copying requires a bounded exact version inventory')
                head = source.head_object(**options, Key=row['Key'], VersionId=row['VersionId'])
                if head.get('ReplicationStatus') in (None, 'PENDING', 'FAILED'):
                    payload_pending += 1
                    continue
                if head.get('ReplicationStatus') != 'COMPLETED' or head.get('VersionId') != row['VersionId']:
                    raise Gate('Regional source replication metadata is ambiguous')
                try:
                    copy = destination.head_object(Bucket=replica_bucket(c, logical), ExpectedBucketOwner=c['account'],
                        Key=row['Key'], VersionId=row['VersionId'])
                except ClientError as error:
                    if error.response.get('Error', {}).get('Code') in ('404', 'NoSuchKey', 'NoSuchVersion', 'NotFound'):
                        payload_pending += 1
                        continue
                    raise
                encryption_matches = (
                    head.get('ServerSideEncryption') == copy.get('ServerSideEncryption') == 'AES256'
                    and not head.get('SSEKMSKeyId') and not copy.get('SSEKMSKeyId')
                    if logical in ('WebAssets', 'DeploymentAssets') else
                    head.get('ServerSideEncryption') == copy.get('ServerSideEncryption') == 'aws:kms'
                    and copy.get('SSEKMSKeyId') == key)
                if (copy.get('VersionId') != row['VersionId'] or copy.get('ReplicationStatus') != 'REPLICA'
                        or copy.get('ContentLength') != head.get('ContentLength')
                        or not encryption_matches
                        or (head.get('ChecksumSHA256') is not None and copy.get('ChecksumSHA256') is not None
                            and head['ChecksumSHA256'] != copy['ChecksumSHA256'])):
                    raise Gate('Regional replica version, encryption or metadata differs')
                if logical == 'DeletionJournal' and (copy.get('ObjectLockMode') != 'COMPLIANCE'
                        or copy.get('ObjectLockRetainUntilDate') != head.get('ObjectLockRetainUntilDate')):
                    raise Gate('Regional journal replica retention differs from the retained source')
            source_markers += [(row['Key'], row['VersionId']) for row in page.get('DeleteMarkers', [])]
            if len(source_markers) > 10000:
                raise Gate('Regional delete-marker inventory exceeds its bound')
        if source_markers:
            replica_markers = set()
            for number, page in enumerate(destination.get_paginator('list_object_versions').paginate(
                    Bucket=replica_bucket(c, logical), ExpectedBucketOwner=c['account'])):
                if number >= 20:
                    raise Gate('Regional replica marker inventory exceeds its bound')
                replica_markers.update((row['Key'], row['VersionId']) for row in page.get('DeleteMarkers', []))
                if len(replica_markers) > 10000:
                    raise Gate('Regional replica marker inventory exceeds its bound')
            markers += len(source_markers)
            marker_pending += len(set(source_markers) - replica_markers)
    secrets = aws.client('secretsmanager', region_name=PRIMARY_REGION)
    secret_arn = primary_outputs.get('TombstoneSecret')
    if not isinstance(secret_arn, str) or not secret_arn.startswith(
            f'arn:aws:secretsmanager:{PRIMARY_REGION}:{c["account"]}:secret:{STACK}-tombstone-'):
        raise Gate('Regional secret copy must preserve the original tombstone secret identity')
    metadata = secrets.describe_secret(SecretId=secret_arn)
    replicas = metadata.get('ReplicationStatus', [])
    if (len(replicas) != 1 or replicas[0].get('Region') != RECOVERY_REGION
            or replicas[0].get('KmsKeyId') != key):
        raise Gate('Regional tombstone key copy target differs')
    in_sync = replicas[0].get('Status') == 'InSync'
    witness = False
    witness_version = None
    try:
        control = source.head_object(Bucket=primary_bucket(c, 'DeletionJournal'), ExpectedBucketOwner=c['account'],
            Key='control/established.json')
        version = control.get('VersionId')
        if version and version != 'null' and control.get('ReplicationStatus') == 'COMPLETED':
            replica = destination.head_object(Bucket=replica_bucket(c, 'DeletionJournal'),
                ExpectedBucketOwner=c['account'], Key='control/established.json', VersionId=version)
            witness = (replica.get('VersionId') == version and replica.get('ReplicationStatus') == 'REPLICA'
                and replica.get('ContentLength') == control.get('ContentLength')
                and control.get('ServerSideEncryption') == replica.get('ServerSideEncryption') == 'aws:kms'
                and replica.get('SSEKMSKeyId') == key and replica.get('ObjectLockMode') == 'COMPLIANCE'
                and replica.get('ObjectLockRetainUntilDate') == control.get('ObjectLockRetainUntilDate'))
            if not witness:
                raise Gate('Regional journal establishment witness differs')
            current = source.head_object(Bucket=primary_bucket(c, 'DeletionJournal'),
                ExpectedBucketOwner=c['account'], Key='control/established.json')
            if current.get('VersionId') != version:
                raise Gate('Regional journal establishment changed during copy verification')
            witness_version = version
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') not in ('404', 'NoSuchKey', 'NoSuchVersion', 'NotFound'):
            raise
    pending = payload_pending + marker_pending
    observation.update(status='regional_copies_verified' if observation['completed_database_copy_count']
        and versions and not pending and in_sync and witness else 'configured_copies_pending',
        s3_source_version_count=versions, s3_replica_verified_version_count=versions-payload_pending,
        s3_replication_pending_count=pending, secret_replica_in_sync=in_sync,
        s3_source_delete_marker_count=markers, journal_control_replica_witness_verified=witness,
        journal_control_replica_version_id=witness_version,
        primary_authority_must_remain_retained=True)
    return observation


def _utc(value):
    try:
        result = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
            raise ValueError
        return result
    except (AttributeError, ValueError, TypeError):
        raise Gate('Initial recovery point metadata must have bounded UTC timestamps') from None


def _snapshot(aws, c, arn, region, key, cluster, source_point=None):
    if not isinstance(arn, str) or not arn.startswith(f'arn:aws:rds:{region}:{c["account"]}:cluster-snapshot:'):
        raise Gate('Initial recovery point must be the exact regional Aurora snapshot ARN')
    row = _one(aws.client('rds', region_name=region).describe_db_cluster_snapshots(
        DBClusterSnapshotIdentifier=arn), 'DBClusterSnapshots')
    copied = source_point is not None
    if (row.get('DBClusterSnapshotArn') != arn or row.get('Status') != 'available'
            or (not copied or row.get('DbClusterResourceId') is not None)
                and row.get('DbClusterResourceId') != cluster['DbClusterResourceId']
            or (not copied or row.get('ClusterCreateTime') is not None)
                and _utc(row.get('ClusterCreateTime')) != _utc(cluster['ClusterCreateTime'])
            or row.get('Engine') != 'aurora-postgresql' or row.get('EngineVersion') != cluster['EngineVersion']
            or (row.get('EngineMode') is not None and row.get('EngineMode') != 'provisioned')
            or row.get('StorageEncrypted') is not True or row.get('KmsKeyId') != key
            or copied and row.get('SourceDBClusterSnapshotArn') != source_point):
        raise Gate('Initial recovery point changed database identity or encryption')
    return row


def ensure_initial_database_copy(aws, c, primary_outputs, recovery_outputs, evidence_path):
    """Create/reconcile one release-bound backup and copy, never restore compute.

    Each mutation uses a deterministic idempotency token and one transport
    attempt. Lost responses remain recorded intents, safe to reconcile using
    the same token on a later explicitly admitted invocation.
    """
    _validate(c)
    if not re.fullmatch(r'[0-9a-f]{40}', str(c.get('releaseId', ''))):
        raise Gate('Initial copy requires the admitted immutable release')
    observe_database_copies(aws, c, primary_outputs, recovery_outputs)
    key = primary_outputs.get('DataKeyArn')
    arn = f'arn:aws:rds:{PRIMARY_REGION}:{c["account"]}:cluster:{STACK}'
    role = f'arn:aws:iam::{c["account"]}:role/{backup_role_name()}'
    if primary_outputs.get('RegionalBackupRoleArn') != role or not isinstance(key, str) or not key.startswith(
            f'arn:aws:kms:{PRIMARY_REGION}:{c["account"]}:key/'):
        raise Gate('Initial backup role or source key differs')
    source_rds = aws.client('rds', region_name=PRIMARY_REGION)
    cluster = _one(source_rds.describe_db_clusters(DBClusterIdentifier=STACK), 'DBClusters')
    if (cluster.get('DBClusterArn') != arn or cluster.get('DBClusterIdentifier') != STACK
            or cluster.get('Status') != 'available' or cluster.get('Engine') != 'aurora-postgresql'
            or cluster.get('EngineMode') != 'provisioned' or cluster.get('DeletionProtection') is not True
            or cluster.get('StorageEncrypted') is not True or cluster.get('KmsKeyId') != key
            or cluster.get('PendingModifiedValues') or not str(cluster.get('DbClusterResourceId', '')).startswith('cluster-')):
        raise Gate('Initial backup requires the exact available protected Virginia cluster')
    backup = aws.client('backup', region_name=PRIMARY_REGION)
    vault = backup.describe_backup_vault(BackupVaultName=vault_name(PRIMARY_REGION))
    if vault.get('BackupVaultArn') != _vault_arn(c, PRIMARY_REGION) or vault.get('EncryptionKeyArn') != key:
        raise Gate('Initial source vault differs from the database encryption authority')
    actor = aws.client('iam').get_role(RoleName=backup_role_name()).get('Role', {})
    trust = {'Version': '2012-10-17', 'Statement': [{
        'Effect': 'Allow', 'Principal': {'Service': 'backup.amazonaws.com'}, 'Action': 'sts:AssumeRole',
        'Condition': {'StringEquals': {'aws:SourceAccount': c['account']},
            'ArnLike': {'aws:SourceArn': f'arn:aws:backup:{PRIMARY_REGION}:{c["account"]}:*'}}}]}
    if actor.get('Arn') != role or actor.get('AssumeRolePolicyDocument') != trust:
        raise Gate('Initial backup role is not the exact scheduled service role')
    identity = {'schema_version': '1.0.0', 'operation': 'initial-regional-database-copy',
        'account': c['account'], 'release_id': c['releaseId'], 'primary_region': PRIMARY_REGION,
        'backup_region': RECOVERY_REGION, 'resource_arn': arn, 'database_resource_id': cluster['DbClusterResourceId'],
        'database_created_at': _utc(cluster['ClusterCreateTime']).isoformat(), 'source_key_arn': key,
        'destination_key_arn': recovery_outputs['RecoveryKeyArn'], 'backup_role_arn': role,
        'source_vault_arn': _vault_arn(c, PRIMARY_REGION), 'destination_vault_arn': _vault_arn(c, RECOVERY_REGION)}
    binding = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    token = binding[:40]
    path = Path(evidence_path)
    if not path.parent.is_dir() or path.is_symlink():
        raise Gate('Initial copy requires a protected existing journal directory')
    if path.exists():
        evidence = strict_loads(bounded_file(path, 262144, private=True))
        if not isinstance(evidence, dict) or any(evidence.get(field) != value for field, value in identity.items()):
            raise Gate('Initial copy journal differs from its immutable resource and source binding')
        if (evidence.get('restore_executed') is not False
                or evidence.get('backup_idempotency_token') not in (None, 'backup-' + token)
                or evidence.get('copy_idempotency_token') not in (None, 'copy-' + token)):
            raise Gate('Initial copy journal intent differs from its deterministic operation')
    else:
        evidence = {**identity, 'started_at': datetime.now(timezone.utc).isoformat(), 'restore_executed': False}
    from deploy.serverless_recovery import _write
    mutation = aws.client('backup', region_name=PRIMARY_REGION,
        config=Config(retries={'total_max_attempts': 1, 'mode': 'standard'}, connect_timeout=5, read_timeout=30))

    def phase(value):
        evidence['status'] = value
        _write(path, evidence)

    def wait_job(operation, identifier, field, expected, allowed):
        deadline = time.monotonic() + 1200
        while time.monotonic() < deadline:
            response = getattr(backup, operation)(**{field: identifier})
            job = response['CopyJob'] if operation == 'describe_copy_job' else response
            if any(job.get(name) != value for name, value in expected.items()):
                raise Gate('Initial backup/copy job authority or scope differs')
            # A newly admitted retry gets a new work directory. The same token
            # may return a job from a prior invocation, whose scope and release
            # are independently bound by its recovery-point tags below.
            if not (_utc(cluster['ClusterCreateTime']) - timedelta(seconds=60)
                    <= _utc(job.get('CreationDate')) <= datetime.now(timezone.utc) + timedelta(seconds=60)):
                raise Gate('Initial backup/copy job creation is outside its source database lifetime')
            if job.get('State') == 'COMPLETED':
                return job
            if job.get('State') not in allowed:
                raise Gate('Initial backup/copy job did not complete successfully')
            time.sleep(15)
        raise Gate('Initial backup/copy verification timed out; inspect the protected journal')

    def verify_point(client, point, region, expected_key, days, created):
        row = client.describe_recovery_point(BackupVaultName=vault_name(region), RecoveryPointArn=point)
        if (row.get('RecoveryPointArn') != point or row.get('ResourceArn') != arn
                or row.get('BackupVaultArn') != _vault_arn(c, region)
                or row.get('Status') not in ('AVAILABLE', 'COMPLETED') or row.get('IsEncrypted') is not True
                or row.get('EncryptionKeyArn') != expected_key
                or row.get('Lifecycle') != {'DeleteAfterDays': days}
                or not _utc(created) - timedelta(seconds=60) <= _utc(row.get('CreationDate'))
                    <= datetime.now(timezone.utc) + timedelta(seconds=60)):
            raise Gate('Initial recovery point scope, encryption, lifetime or availability differs')
        return row

    try:
        if not evidence.get('backup_job_id'):
            evidence['backup_idempotency_token'] = 'backup-' + token
            phase('backup-requesting')
            response = mutation.start_backup_job(BackupVaultName=vault_name(PRIMARY_REGION), ResourceArn=arn,
                IamRoleArn=role, IdempotencyToken=evidence['backup_idempotency_token'],
                Lifecycle={'DeleteAfterDays': 2}, StartWindowMinutes=60, CompleteWindowMinutes=360,
                RecoveryPointTags={'deployment': STACK, 'source_revision': c['releaseId'],
                    'initial_copy_binding': binding})
            evidence['backup_job_id'] = response['BackupJobId']
            phase('backup-requested')
        original = wait_job('describe_backup_job', evidence['backup_job_id'], 'BackupJobId',
            {'BackupJobId': evidence['backup_job_id'], 'AccountId': c['account'], 'ResourceArn': arn,
             'IamRoleArn': role, 'BackupVaultArn': _vault_arn(c, PRIMARY_REGION), 'ResourceType': 'Aurora'},
            {'CREATED', 'PENDING', 'RUNNING'})
        evidence['backup_job_created_at'] = _utc(original['CreationDate']).isoformat()
        source_point = original['RecoveryPointArn']
        _snapshot(aws, c, source_point, PRIMARY_REGION, key, cluster)
        verify_point(backup, source_point, PRIMARY_REGION, key, 2, original['CreationDate'])
        tag_rows = source_rds.list_tags_for_resource(ResourceName=source_point).get('TagList', [])
        if (not isinstance(tag_rows, list)
                or any(not isinstance(row, dict) or set(row) != {'Key', 'Value'}
                    or not isinstance(row['Key'], str) or not isinstance(row['Value'], str) for row in tag_rows)
                or len({row['Key'] for row in tag_rows}) != len(tag_rows)):
            raise Gate('Initial native recovery point tags are ambiguous')
        tags = {row['Key']: row['Value'] for row in tag_rows}
        if any(tags.get(name) != value for name, value in {
                'deployment': STACK, 'source_revision': c['releaseId'], 'initial_copy_binding': binding}.items()):
            raise Gate('Initial recovery point is not bound to its exact admitted release and request')
        if evidence.get('source_recovery_point_arn') not in (None, source_point):
            raise Gate('Initial source recovery point differs from the prior journal')
        evidence['source_recovery_point_arn'] = source_point
        phase('backup-completed-verified')
        if not evidence.get('copy_job_id'):
            evidence['copy_idempotency_token'] = 'copy-' + token
            phase('copy-requesting')
            response = mutation.start_copy_job(RecoveryPointArn=source_point,
                SourceBackupVaultName=vault_name(PRIMARY_REGION), DestinationBackupVaultArn=_vault_arn(c, RECOVERY_REGION),
                IamRoleArn=role, IdempotencyToken=evidence['copy_idempotency_token'], Lifecycle={'DeleteAfterDays': 7})
            evidence['copy_job_id'] = response['CopyJobId']
            phase('copy-requested')
        copied = wait_job('describe_copy_job', evidence['copy_job_id'], 'CopyJobId',
            {'CopyJobId': evidence['copy_job_id'], 'AccountId': c['account'], 'ResourceArn': arn,
             'SourceRecoveryPointArn': source_point, 'SourceBackupVaultArn': _vault_arn(c, PRIMARY_REGION),
             'DestinationBackupVaultArn': _vault_arn(c, RECOVERY_REGION), 'IamRoleArn': role, 'ResourceType': 'Aurora'},
            {'CREATED', 'RUNNING'})
        evidence['copy_job_created_at'] = _utc(copied['CreationDate']).isoformat()
        target_point = copied['DestinationRecoveryPointArn']
        _snapshot(aws, c, target_point, RECOVERY_REGION, recovery_outputs['RecoveryKeyArn'], cluster, source_point)
        verify_point(aws.client('backup', region_name=RECOVERY_REGION), target_point, RECOVERY_REGION,
            recovery_outputs['RecoveryKeyArn'], 7, copied['CreationDate'])
        current = _one(source_rds.describe_db_clusters(DBClusterIdentifier=STACK), 'DBClusters')
        if (current.get('DbClusterResourceId') != cluster['DbClusterResourceId']
                or _utc(current.get('ClusterCreateTime')) != _utc(cluster['ClusterCreateTime'])
                or current.get('KmsKeyId') != key):
            raise Gate('Initial backup changed its original source database authority')
        evidence.update(destination_recovery_point_arn=target_point,
            completed_at=datetime.now(timezone.utc).isoformat(), backup_copy_verified=True,
            restore_executed=False, regional_activation_supported=False)
        phase('initial-database-copy-verified')
        return evidence
    except Exception as error:
        evidence['failed_phase'] = evidence.get('status')
        evidence['failure_type'] = type(error).__name__
        evidence['backup_copy_verified'] = False
        phase('blocked-initial-copy-inspect-protected-journal-before-retry')
        raise
