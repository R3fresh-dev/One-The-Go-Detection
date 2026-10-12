"""Recover an uninitialized failed first stack without deleting retained resources.

The caller must admit the exact reviewed source before invoking this mutation.
This path is deliberately unavailable for a database or journal that has ever
been initialized. CloudFormation imports only the original retained resources;
the regular deployment subsequently creates the stopped application runtime.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

from botocore.exceptions import ClientError

from deploy.provenance import Gate
from deploy.serverless_template import build_template
from otgd.canonical import canonical, strict_loads


STACK = 'otgd-serverless-development'
RETAINED_TYPES = {
    'AWS::KMS::Key', 'AWS::SecretsManager::Secret', 'AWS::S3::Bucket',
    'AWS::DynamoDB::Table', 'AWS::Cognito::UserPool', 'AWS::Logs::LogGroup',
}
APPLICATION_IDS = {'Database', 'DatabaseWriter'} | {
    role + 'Function' for role in ('Api', 'Worker', 'Dispatcher', 'Maintenance', 'Control')
}


def _object(value, label):
    if not isinstance(value, dict):
        raise Gate('Initial recovery requires explicit ' + label + ' metadata')
    return value


def _list(value, limit, label):
    if not isinstance(value, list) or len(value) > limit:
        raise Gate('Initial recovery requires bounded ' + label + ' metadata')
    return value


def _tags(tags):
    entries = _list(tags, 50, 'ownership tags')
    result = {}
    for entry in entries:
        entry = _object(entry, 'ownership tag')
        key, value = entry.get('Key'), entry.get('Value')
        if (not isinstance(key, str) or not 0 < len(key) <= 128 or key in result
                or not isinstance(value, str) or len(value) > 256):
            raise Gate('Initial recovery ownership tags are invalid or ambiguous')
        result[key] = value
    return result


def _stack_id(value, config):
    prefix = f"arn:aws:cloudformation:{config['region']}:{config['account']}:stack/{STACK}/"
    if not isinstance(value, str) or not value.startswith(prefix) or not re.fullmatch(r'[A-Za-z0-9-]{1,128}', value[len(prefix):]):
        raise Gate('Initial recovery stack authority differs from the selected account')
    return value


def _resolved(value, config, physical_ids):
    if isinstance(value, list):
        return [_resolved(item, config, physical_ids) for item in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {'Fn::GetAtt'}:
        name, attribute = value['Fn::GetAtt']
        if attribute != 'Arn' or name not in ('DataKey', 'JournalKey', 'CaptureSigningKey'):
            raise Gate('Initial recovery authority link cannot be resolved exactly')
        return f"arn:aws:kms:{config['region']}:{config['account']}:key/{physical_ids[name]}"
    if set(value) == {'Fn::Sub'}:
        expression = value['Fn::Sub']
        if not isinstance(expression, str):
            raise Gate('Initial recovery authority substitution cannot be resolved exactly')
        variables = {'AWS::Partition': 'aws', 'AWS::Region': config['region'], 'AWS::AccountId': config['account']}
        for key, item in variables.items():
            expression = expression.replace('${' + key + '}', item)
        if '${' in expression:
            raise Gate('Initial recovery authority substitution cannot be resolved exactly')
        return expression
    return {key: _resolved(item, config, physical_ids) for key, item in value.items()}


def _creation(value):
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise Gate('Initial recovery resource generation metadata is unavailable')
    return value.isoformat()


def _template(value):
    if isinstance(value, str):
        if len(value.encode()) > 1048576:
            raise Gate('Initial recovery template exceeded its bound')
        value = strict_loads(value)
    value = _object(value, 'reviewed template')
    if len(canonical(value)) > 1048576:
        raise Gate('Initial recovery template exceeded its bound')
    return value


def _uuid(value):
    try:
        if not isinstance(value, str) or str(uuid.UUID(value)) != value:
            raise ValueError()
    except (ValueError, AttributeError):
        raise Gate('Initial recovery generation identity is not canonical') from None
    return value


def _pages(client, operation, **options):
    for number, page in enumerate(client.get_paginator(operation).paginate(**options)):
        if number >= 20:
            raise Gate('Initial recovery inventory exceeded its bound')
        yield _object(page, 'inventory page')


def _absent(client, operation, codes, **options):
    try:
        getattr(client, operation)(**options)
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') in codes:
            return
        raise
    raise Gate('Initial recovery requires absent application functions and database')


def _references(value):
    """Collect template dependencies, including Fn::Sub without false locals."""
    result = set()
    if isinstance(value, list):
        for item in value:
            result |= _references(item)
    elif isinstance(value, dict):
        if 'Ref' in value:
            result.add(value['Ref'])
        if 'Fn::GetAtt' in value:
            target = value['Fn::GetAtt']
            result.add(target[0] if isinstance(target, list) else target.split('.')[0])
        if 'Fn::Sub' in value:
            expression = value['Fn::Sub']
            text, variables = (expression, {}) if isinstance(expression, str) else expression
            for variable in re.findall(r'\$\{([^}]+)\}', text):
                if not variable.startswith('!') and variable not in variables:
                    result.add(variable.split('.')[0])
            result |= _references(variables)
        for key, item in value.items():
            if key not in ('Ref', 'Fn::GetAtt', 'Fn::Sub'):
                result |= _references(item)
        depends = value.get('DependsOn', [])
        result.update([depends] if isinstance(depends, str) else depends)
    return {item for item in result if not item.startswith('AWS::')}


def _write(path, evidence):
    raw = (json.dumps(evidence, indent=2, sort_keys=True) + '\n').encode()
    if len(raw) > 262144:
        raise Gate('Initial recovery evidence exceeded its bound')
    temporary = path.with_name(path.name + '.new-' + uuid.uuid4().hex)
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _require_tags(tags):
    actual = _tags(tags)
    if actual.get('deployment') != STACK or actual.get('environment') != 'serverless-development':
        raise Gate('Initial recovery found a resource without the exact deployment ownership tags')


def _verify_retained(aws, config, logical, resource, physical, physical_ids):
    """Read configuration and emptiness, never secret values or object contents."""
    kind, props = resource['Type'], resource['Properties']
    if kind == 'AWS::S3::Bucket':
        expected = f"{STACK}-{config['account']}-{config['region']}-"
        if physical != props['BucketName'] or not physical.startswith(expected):
            raise Gate('Initial recovery bucket identity differs from the owned template')
        s3 = aws.client('s3')
        selected = {'Bucket': physical, 'ExpectedBucketOwner': config['account']}
        _require_tags(_object(s3.get_bucket_tagging(**selected), 'bucket tags').get('TagSet'))
        if _object(s3.get_bucket_location(**selected), 'bucket region').get('LocationConstraint') != config['region']:
            raise Gate('Initial recovery retained bucket region differs')
        if _object(s3.get_bucket_versioning(**selected), 'bucket versioning').get('Status') != 'Enabled':
            raise Gate('Initial recovery requires the reviewed retained bucket versioning')
        actual = _object(s3.get_public_access_block(**selected), 'bucket access').get('PublicAccessBlockConfiguration')
        if canonical(actual) != canonical(props['PublicAccessBlockConfiguration']):
            raise Gate('Initial recovery retained bucket public access differs')
        encryption = _object(s3.get_bucket_encryption(**selected), 'bucket encryption').get('ServerSideEncryptionConfiguration')
        rules = _list(_object(encryption, 'bucket encryption').get('Rules'), 1, 'bucket encryption rules')
        expected_rules = _resolved(props['BucketEncryption']['ServerSideEncryptionConfiguration'], config, physical_ids)
        if len(rules) != 1 or rules[0].get('ApplyServerSideEncryptionByDefault') != expected_rules[0]['ServerSideEncryptionByDefault'] or rules[0].get('BucketKeyEnabled', False) != expected_rules[0].get('BucketKeyEnabled', False):
            raise Gate('Initial recovery retained bucket encryption authority differs')
        if props.get('ObjectLockEnabled') and _object(s3.get_object_lock_configuration(**selected), 'journal retention').get('ObjectLockConfiguration') != props['ObjectLockConfiguration']:
            raise Gate('Initial recovery retained deletion journal retention differs')
        versions = _object(s3.list_object_versions(**selected, MaxKeys=1), 'bucket versions')
        if (versions.get('IsTruncated') is not False or any(versions.get(key) for key in ('NextKeyMarker', 'NextVersionIdMarker'))
                or _list(versions.get('Versions', []), 1, 'bucket versions') or _list(versions.get('DeleteMarkers', []), 1, 'bucket deletion markers')):
            raise Gate('Initial recovery requires all retained buckets, including the deletion journal, to be empty')
        uploads = _object(s3.list_multipart_uploads(**selected, MaxUploads=1), 'multipart inventory')
        if (uploads.get('IsTruncated') is not False or any(uploads.get(key) for key in ('NextKeyMarker', 'NextUploadIdMarker'))
                or _list(uploads.get('Uploads', []), 1, 'multipart uploads')):
            raise Gate('Initial recovery requires no outstanding retained-bucket multipart uploads')
        return {'owner': config['account']}
    elif kind == 'AWS::DynamoDB::Table':
        client = aws.client('dynamodb')
        table = _object(_object(client.describe_table(TableName=physical), 'control table').get('Table'), 'control table')
        arn = f"arn:aws:dynamodb:{config['region']}:{config['account']}:table/{physical}"
        if (physical != props['TableName'] or table.get('TableName') != physical or table.get('TableStatus') != 'ACTIVE'
                or table.get('TableArn') != arn or _uuid(table.get('TableId')) != table['TableId']):
            raise Gate('Initial recovery control table identity or state differs')
        tags = _object(client.list_tags_of_resource(ResourceArn=arn), 'control tags')
        if tags.get('NextToken'):
            raise Gate('Initial recovery control tags exceed the complete inventory')
        _require_tags(tags.get('Tags'))
        result = _object(client.scan(TableName=physical, Select='COUNT', Limit=1, ConsistentRead=True), 'control scan')
        if (type(result.get('Count')) is not int or result['Count'] != 0 or type(result.get('ScannedCount')) is not int
                or result['ScannedCount'] != 0 or result.get('LastEvaluatedKey')):
            raise Gate('Initial recovery requires an empty runtime control table')
        return {'table_id': table['TableId']}
    elif kind == 'AWS::Cognito::UserPool':
        client = aws.client('cognito-idp')
        pool = _object(_object(client.describe_user_pool(UserPoolId=physical), 'user pool').get('UserPool'), 'user pool')
        if (not re.fullmatch(re.escape(config['region']) + r'_[A-Za-z0-9]{1,55}', physical)
                or pool.get('Id') != physical or pool.get('Arn') != f"arn:aws:cognito-idp:{config['region']}:{config['account']}:userpool/{physical}"
                or pool.get('Name') != props['UserPoolName']):
            raise Gate('Initial recovery Cognito identity differs from the owned template')
        _require_tags([{'Key': key, 'Value': value} for key, value in _object(pool.get('UserPoolTags'), 'user pool tags').items()])
        users = _object(client.list_users(UserPoolId=physical, Limit=1), 'user pool inventory')
        if _list(users.get('Users'), 1, 'user accounts') or users.get('PaginationToken'):
            raise Gate('Initial recovery requires a user pool with no accounts')
        return {'created_at': _creation(pool.get('CreationDate'))}
    elif kind == 'AWS::SecretsManager::Secret':
        secret = _object(aws.client('secretsmanager').describe_secret(SecretId=physical), 'secret authority')
        if (secret.get('Name') != props['Name'] or secret.get('ARN') != physical
                or secret.get('DeletedDate') or not physical.startswith(f"arn:aws:secretsmanager:{config['region']}:{config['account']}:secret:")):
            raise Gate('Initial recovery secret identity or state differs')
        if secret.get('KmsKeyId') != _resolved(props['KmsKeyId'], config, physical_ids):
            raise Gate('Initial recovery secret encryption authority differs')
        if secret.get('RotationEnabled', False) is not False:
            raise Gate('Initial recovery generated authority must not have enabled rotation')
        versions = _object(secret.get('VersionIdsToStages'), 'secret versions')
        if not 1 <= len(versions) <= 20:
            raise Gate('Initial recovery secret version inventory exceeds its bound')
        normalized = {}
        for version, stages in versions.items():
            if not isinstance(version, str) or not re.fullmatch(r'[A-Za-z0-9-]{32,64}', version):
                raise Gate('Initial recovery secret version identity is invalid')
            stages = _list(stages, 20, 'secret version stages')
            if (not stages or any(not isinstance(stage, str) or not 1 <= len(stage) <= 256 for stage in stages)
                    or len(stages) != len(set(stages)) or 'AWSPENDING' in stages):
                raise Gate('Initial recovery secret version stages are ambiguous or pending')
            normalized[version] = sorted(stages)
        if sum('AWSCURRENT' in stages for stages in normalized.values()) != 1:
            raise Gate('Initial recovery requires one exact current secret generation')
        _require_tags(secret.get('Tags'))
        return {'created_at': _creation(secret.get('CreatedDate')), 'versions': normalized}
    elif kind == 'AWS::KMS::Key':
        client = aws.client('kms')
        key = _object(_object(client.describe_key(KeyId=physical), 'key authority').get('KeyMetadata'), 'key authority')
        if (key.get('KeyId') != physical or key.get('AWSAccountId') != config['account']
                or key.get('Description') != props['Description'] or key.get('KeyState') != 'Enabled'
                or key.get('Arn') != f"arn:aws:kms:{config['region']}:{config['account']}:key/{physical}"
                or key.get('KeyManager') != 'CUSTOMER' or key.get('Origin') != 'AWS_KMS'
                or key.get('KeySpec') != props.get('KeySpec', 'SYMMETRIC_DEFAULT')
                or key.get('KeyUsage') != props.get('KeyUsage', 'ENCRYPT_DECRYPT')):
            raise Gate('Initial recovery encryption authority identity or state differs')
        policy = _object(client.get_key_policy(KeyId=physical, PolicyName='default'), 'key policy').get('Policy')
        if not isinstance(policy, str) or len(policy.encode()) > 65536 or canonical(strict_loads(policy)) != canonical(_resolved(props['KeyPolicy'], config, physical_ids)):
            raise Gate('Initial recovery encryption key policy differs from the reviewed authority')
        tags = _object(client.list_resource_tags(KeyId=physical), 'key tags')
        if tags.get('Truncated') is not False or tags.get('NextMarker'):
            raise Gate('Initial recovery key tag inventory exceeded its bound')
        _require_tags([{'Key': tag.get('TagKey'), 'Value': tag.get('TagValue')} for tag in _list(tags.get('Tags'), 50, 'key tags')])
        return {'created_at': _creation(key.get('CreationDate'))}
    elif kind == 'AWS::Logs::LogGroup':
        client = aws.client('logs')
        response = _object(client.describe_log_groups(logGroupNamePrefix=physical, limit=50), 'log inventory')
        if response.get('nextToken'):
            raise Gate('Initial recovery log group inventory exceeds its bound')
        groups = _list(response.get('logGroups'), 50, 'log groups')
        exact = [group for group in groups if group.get('logGroupName') == physical]
        if physical != props['LogGroupName'] or len(exact) != 1:
            raise Gate('Initial recovery log group identity differs from the owned template')
        expected_arn = f"arn:aws:logs:{config['region']}:{config['account']}:log-group:{physical}"
        if exact[0].get('arn') not in (expected_arn, expected_arn + ':*') or exact[0].get('kmsKeyId') != _resolved(props['KmsKeyId'], config, physical_ids):
            raise Gate('Initial recovery log group authority differs')
        if type(exact[0].get('retentionInDays')) is not int or exact[0]['retentionInDays'] != props['RetentionInDays']:
            raise Gate('Initial recovery log retention differs from the reviewed template')
        arn = expected_arn
        _require_tags([{'Key': key, 'Value': value} for key, value in _object(_object(client.list_tags_for_resource(resourceArn=arn), 'log tags').get('tags'), 'log tags').items()])
        created = exact[0].get('creationTime')
        if type(created) is not int or not 0 < created <= 9007199254740991:
            raise Gate('Initial recovery log resource generation is unavailable')
        return {'created_at_ms': created}
    raise Gate('Initial recovery retained resource type is unsupported')


def _verify_initial_state(aws, config, evidence):
    identity = _object(aws.client('sts').get_caller_identity(), 'caller identity')
    if identity.get('Account') != config['account']:
        raise Gate('Initial recovery credentials do not match the selected account')
    generations = {}
    for logical, resource in evidence['import_template']['Resources'].items():
        generations[logical] = _verify_retained(aws, config, logical, resource,
            evidence['retained_physical_ids'][logical], evidence['retained_physical_ids'])
    if evidence.get('retained_generations') is not None and generations != evidence['retained_generations']:
        raise Gate('Initial recovery retained resource generation changed')
    rds = aws.client('rds')
    _absent(rds, 'describe_db_clusters', {'DBClusterNotFoundFault'}, DBClusterIdentifier=STACK)
    _absent(rds, 'describe_db_instances', {'DBInstanceNotFound'}, DBInstanceIdentifier=STACK + '-writer')
    functions = aws.client('lambda')
    for role in ('api', 'worker', 'dispatcher', 'maintenance', 'control'):
        _absent(functions, 'get_function', {'ResourceNotFoundException'}, FunctionName=STACK + '-' + role)
    return generations


def initial_recovery_plan(aws, config):
    """Validate the complete recovery before any mutation and retain no secrets."""
    if (not isinstance(config, dict) or config.get('environment') != 'serverless-development' or config.get('region') != 'us-east-2'
            or not isinstance(config.get('account'), str) or not re.fullmatch(r'[0-9]{12}', config['account'])
            or not isinstance(config.get('releaseId'), str) or not re.fullmatch(r'[0-9a-f]{40}', config['releaseId'])):
        raise Gate('Initial recovery requires the explicit reviewed serverless target')
    if _object(aws.client('sts').get_caller_identity(), 'caller identity').get('Account') != config['account']:
        raise Gate('Initial recovery credentials do not match the selected account')
    cf = aws.client('cloudformation')
    stacks = _list(_object(cf.describe_stacks(StackName=STACK), 'original stack').get('Stacks'), 1, 'original stacks')
    if len(stacks) != 1:
        raise Gate('Initial recovery requires one original stack')
    stack = _object(stacks[0], 'original stack')
    stack_tags = _tags(stack.get('Tags'))
    if (stack.get('StackStatus') != 'ROLLBACK_COMPLETE'
            or stack_tags.get('deployment') != STACK or stack_tags.get('purpose') != 'serverless-development'
            or _stack_id(stack.get('StackId'), config) != stack['StackId']):
        raise Gate('Only the owned fully rolled-back first application stack can use initial recovery')
    original = cf.get_template(StackName=stack['StackId'], TemplateStage='Original')['TemplateBody']
    if isinstance(original, str):
        if len(original.encode()) > 1048576:
            raise Gate('Initial recovery original template exceeded its bound')
        original = strict_loads(original)
    original = _object(original, 'original template')
    if len(canonical(original)) > 1048576:
        raise Gate('Initial recovery original template exceeded its bound')
    resources = _object(original.get('Resources'), 'original resources')
    try:
        old_config = {**config,
            'releaseId': resources['ApiFunction']['Properties']['Environment']['Variables']['OTGD_SOURCE_REVISION'],
            'apiImageUri': resources['ApiFunction']['Properties']['Code']['ImageUri'],
            'workerImageUri': resources['WorkerFunction']['Properties']['Code']['ImageUri'],
            'databaseEngineVersion': resources['Database']['Properties']['EngineVersion'],
            'activateServices': False}
        expected = build_template(old_config)
    except (KeyError, TypeError, ValueError) as error:
        raise Gate('Initial recovery original template is not the reviewed stopped serverless application') from error
    if canonical(original) != canonical(expected):
        raise Gate('Initial recovery original template differs from the reviewed stopped deployment')
    events = [event for page in _pages(cf, 'describe_stack_events', StackName=stack['StackId'])
              for event in _list(page.get('StackEvents'), 2000, 'stack events')]
    if len(events) > 2000:
        raise Gate('Initial recovery event history exceeded its bound')
    if any(not isinstance(event, dict) or not isinstance(event.get('ResourceStatus'), str) for event in events):
        raise Gate('Initial recovery stack event metadata is incomplete')
    if any(event['ResourceStatus'].startswith(('UPDATE_', 'IMPORT_')) for event in events):
        raise Gate('Initial recovery requires a first creation attempt without update or import history')
    if any(event.get('LogicalResourceId') in APPLICATION_IDS
           and event.get('ResourceStatus') == 'CREATE_COMPLETE' for event in events):
        raise Gate('Initial recovery cannot adopt a database or application function that was created before rollback')
    if not any(event.get('ResourceType') == 'AWS::CloudFormation::Stack'
               and event.get('PhysicalResourceId') == stack['StackId']
               and event.get('ResourceStatus') == 'CREATE_IN_PROGRESS' for event in events):
        raise Gate('Initial recovery requires complete history including the original stack creation event')
    rows = [row for page in _pages(cf, 'list_stack_resources', StackName=stack['StackId'])
            for row in _list(page.get('StackResourceSummaries'), 200, 'stack resources')]
    if len(rows) > 200 or len({row['LogicalResourceId'] for row in rows}) != len(rows):
        raise Gate('Initial recovery resource inventory is ambiguous or excessive')
    imported = {}
    physical_ids = {}
    for row in rows:
        logical, kind, status = row['LogicalResourceId'], row['ResourceType'], row['ResourceStatus']
        if logical not in resources or kind != resources[logical]['Type']:
            raise Gate('Initial recovery resource inventory differs from its original template')
        if logical in APPLICATION_IDS and status != 'DELETE_COMPLETE':
            raise Gate('Initial recovery cannot adopt a stack that created an application function or database')
        if status == 'DELETE_COMPLETE':
            continue
        resource = resources[logical]
        physical = row.get('PhysicalResourceId')
        if (status != 'DELETE_SKIPPED' or kind not in RETAINED_TYPES or not isinstance(physical, str) or not 0 < len(physical) <= 2048
                or resource.get('DeletionPolicy') != 'Retain' or resource.get('UpdateReplacePolicy') != 'Retain'):
            raise Gate('Initial recovery found an unaccounted or non-retained surviving resource')
        imported[logical] = deepcopy(resource)
        physical_ids[logical] = physical
    if not imported or {'DataKey', 'JournalKey', 'CaptureSigningKey', 'ApplicationSecret',
                        'TombstoneSecret', 'DeletionJournal', 'RuntimeControl', 'Accounts'} - imported.keys():
        raise Gate('Initial recovery is missing required retained authority resources')
    if any(_references(resource) - imported.keys() for resource in imported.values()):
        raise Gate('Initial recovery import template references a resource that did not survive rollback')
    template = {'AWSTemplateFormatVersion': '2010-09-09',
                'Description': 'Retained resources from the uninitialized first serverless deployment',
                'Resources': imported}
    body = json.dumps(template, separators=(',', ':'))
    if len(body.encode()) > 51200:
        raise Gate('Initial recovery import template exceeds the direct CloudFormation limit')
    generations = _verify_initial_state(aws, config, {'import_template': template, 'retained_physical_ids': physical_ids})
    summaries = _list(_object(cf.get_template_summary(TemplateBody=body), 'import identifiers').get('ResourceIdentifierSummaries'), 200, 'import identifiers')
    identifiers = {}
    for summary in summaries:
        keys = summary.get('ResourceIdentifiers', [])
        if len(keys) != 1 or not isinstance(keys[0], str):
            raise Gate('Initial recovery requires one unambiguous CloudFormation import identifier')
        for logical in summary.get('LogicalResourceIds', []):
            if logical not in imported or logical in identifiers or summary.get('ResourceType') != imported[logical]['Type']:
                raise Gate('Initial recovery import identifier inventory differs from the retained resources')
            identifiers[logical] = keys[0]
    if identifiers.keys() != imported.keys():
        raise Gate('CloudFormation did not identify every retained resource for import')
    return {'schema_version': '1.0.0', 'operation': 'serverless-initial-recovery',
            'status': 'validated', 'account': config['account'], 'region': config['region'],
            'release_id': config['releaseId'], 'stack_name': STACK, 'original_stack_id': stack['StackId'],
            'original_release_id': old_config['releaseId'], 'retained_physical_ids': physical_ids,
            'original_template_sha256': hashlib.sha256(canonical(original)).hexdigest(),
            'original_stack_tags': stack_tags, 'retained_generations': generations,
            'import_template': template, 'import_template_sha256': hashlib.sha256(body.encode()).hexdigest(),
            'resources_to_import': [{'LogicalResourceId': logical, 'ResourceType': imported[logical]['Type'],
                'ResourceIdentifier': {identifiers[logical]: physical_ids[logical]}} for logical in sorted(imported)],
            'initial_state': {'database_absent': True, 'application_functions_absent': True,
                              'retained_buckets_empty': True, 'control_table_empty': True, 'user_pool_empty': True,
                              'initial_creation_history_verified': True, 'stack_event_count': len(events)},
            'actual_resources_deleted': False, 'application_deployment_completed': False}


def recover_initial(aws, config, evidence_path, *, readmission):
    """Detach failed stack metadata, then adopt the identical retained resources."""
    path = Path(evidence_path)
    if not callable(readmission):
        raise Gate('Initial recovery requires live exact-source gate readmission')
    if path.exists() or path.is_symlink() or not path.is_absolute() or path.parent.resolve(strict=True) != path.parent:
        raise Gate('Use a new protected initial recovery journal in an existing deployment work directory')
    parent = path.parent.lstat()
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) != 0o700:
        raise Gate('Initial recovery requires an owned private deployment work directory')
    evidence = initial_recovery_plan(aws, config)
    _write(path, evidence)
    cf = aws.client('cloudformation')

    def phase(status):
        evidence['status'] = status
        _write(path, evidence)

    def mutate(operation, *, precondition=None, **options):
        readmission()
        if precondition is not None:
            precondition()
        return getattr(cf, operation)(**options)

    def imported_stack(expected_status, *, protected):
        rows = _list(_object(cf.describe_stacks(StackName=evidence['recovered_stack_id']), 'import stack').get('Stacks'), 1, 'import stacks')
        if len(rows) != 1:
            raise Gate('Initial recovery import stack inventory is ambiguous')
        stack = _object(rows[0], 'import stack')
        if (stack.get('StackId') != evidence['recovered_stack_id'] or stack.get('StackStatus') != expected_status
                or type(stack.get('EnableTerminationProtection')) is not bool
                or protected and stack['EnableTerminationProtection'] is not True
                or _tags(stack.get('Tags')) != evidence['original_stack_tags']):
            raise Gate('Initial recovery import stack ownership, state or protection differs')
        return stack

    try:
        phase('detaching-failed-stack-metadata')
        mutate('update_termination_protection', StackName=evidence['original_stack_id'], EnableTerminationProtection=False)
        mutate('delete_stack', StackName=evidence['original_stack_id'])
        cf.get_waiter('stack_delete_complete').wait(StackName=evidence['original_stack_id'],
            WaiterConfig={'Delay': 5, 'MaxAttempts': 120})
        phase('failed-stack-metadata-detached')
        # Re-read authority and emptiness after detachment, before adoption.
        _verify_initial_state(aws, config, evidence)
        change_name = 'initial-import-' + uuid.uuid4().hex
        created = _object(mutate('create_change_set', StackName=STACK, ChangeSetName=change_name,
            ChangeSetType='IMPORT', TemplateBody=json.dumps(evidence['import_template'], separators=(',', ':')),
            ResourcesToImport=evidence['resources_to_import'],
            Tags=[{'Key': key, 'Value': value} for key, value in sorted(evidence['original_stack_tags'].items())]), 'import creation')
        change = created.get('Id')
        if not isinstance(change, str) or not re.fullmatch(f"arn:aws:cloudformation:{re.escape(config['region'])}:{config['account']}:changeSet/{change_name}/[A-Za-z0-9-]{{1,128}}", change):
            raise Gate('Initial recovery change set authority differs')
        evidence['recovered_stack_id'] = _stack_id(created.get('StackId'), config)
        if evidence['recovered_stack_id'] == evidence['original_stack_id']:
            raise Gate('Initial recovery did not create a distinct adoption stack')
        evidence['import_change_set_id'] = change
        phase('import-change-set-created')
        cf.get_waiter('change_set_create_complete').wait(StackName=evidence['recovered_stack_id'], ChangeSetName=change,
            WaiterConfig={'Delay': 3, 'MaxAttempts': 120})
        changes = []
        for page in _pages(cf, 'describe_change_set', StackName=evidence['recovered_stack_id'], ChangeSetName=change):
            if (page.get('ChangeSetId') != change or page.get('ChangeSetName') != change_name
                    or page.get('StackId') != evidence['recovered_stack_id'] or page.get('StackName') != STACK
                    or page.get('Status') != 'CREATE_COMPLETE' or page.get('ExecutionStatus') != 'AVAILABLE'):
                raise Gate('Initial recovery change set metadata differs from the requested adoption')
            changes.extend(_object(_object(row, 'import change').get('ResourceChange'), 'import resource change') for row in _list(page.get('Changes'), 200, 'import changes'))
            if len(changes) > 200:
                raise Gate('Initial recovery change set exceeded its bound')
        resources = evidence['import_template']['Resources']
        if (len(changes) != len(resources) or {row.get('LogicalResourceId') for row in changes} != resources.keys()
                or any(not isinstance(row, dict) or row.get('Action') != 'Import' or row.get('ResourceType') != resources[row['LogicalResourceId']]['Type']
                       or row.get('PhysicalResourceId') != evidence['retained_physical_ids'][row['LogicalResourceId']]
                       for row in changes)):
            mutate('delete_change_set', StackName=evidence['recovered_stack_id'], ChangeSetName=change)
            raise Gate('Initial recovery change set is not an import of the exact preserved resources')
        submitted = _template(_object(cf.get_template(StackName=evidence['recovered_stack_id'], ChangeSetName=change, TemplateStage='Original'), 'import template').get('TemplateBody'))
        if canonical(submitted) != canonical(evidence['import_template']):
            raise Gate('Initial recovery requested import template changed')
        imported_stack('REVIEW_IN_PROGRESS', protected=False)
        _verify_initial_state(aws, config, evidence)
        mutate('update_termination_protection', StackName=evidence['recovered_stack_id'], EnableTerminationProtection=True)
        phase('import-executing')
        mutate('execute_change_set', precondition=lambda: _verify_initial_state(aws, config, evidence),
               StackName=evidence['recovered_stack_id'], ChangeSetName=change)
        cf.get_waiter('stack_import_complete').wait(StackName=evidence['recovered_stack_id'],
            WaiterConfig={'Delay': 5, 'MaxAttempts': 180})
        stack = imported_stack('IMPORT_COMPLETE', protected=True)
        rows = [row for page in _pages(cf, 'list_stack_resources', StackName=evidence['recovered_stack_id'])
                for row in _list(page.get('StackResourceSummaries'), 200, 'adopted resources')]
        if (stack.get('StackStatus') != 'IMPORT_COMPLETE' or not stack.get('EnableTerminationProtection')
                or len(rows) != len(resources) or {row['LogicalResourceId']: row.get('PhysicalResourceId') for row in rows}
                    != evidence['retained_physical_ids']
                or any(row.get('ResourceType') != resources[row['LogicalResourceId']]['Type'] or row.get('ResourceStatus') != 'IMPORT_COMPLETE' for row in rows)):
            raise Gate('Initial recovery did not prove adoption of every original retained resource')
        adopted = _template(_object(cf.get_template(StackName=evidence['recovered_stack_id'], TemplateStage='Original'), 'adopted template').get('TemplateBody'))
        if canonical(adopted) != canonical(evidence['import_template']):
            raise Gate('Initial recovery adopted template differs from the exact preserved resources')
        _verify_initial_state(aws, config, evidence)
        phase('uninitialized-retained-resources-imported')
        return evidence
    except Exception as error:
        evidence['failed_phase'] = evidence['status']
        evidence['failure_type'] = type(error).__name__
        phase('blocked-recovery-inspect-protected-journal-before-retry')
        raise
