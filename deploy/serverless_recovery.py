"""Recover an uninitialized failed first stack without deleting retained resources.

The caller must admit the exact reviewed source before invoking this mutation.
This path is deliberately unavailable for a database or journal that has ever
been initialized. CloudFormation imports only the original retained resources;
the regular deployment subsequently creates the stopped application runtime.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import uuid
from zipfile import BadZipFile, ZipFile
import httpx

from botocore.exceptions import ClientError

from deploy.provenance import Gate, REPOSITORY, _github_json, bounded_file, bounded_json, strict_loads
from deploy.serverless_template import build_template


STACK = 'otgd-serverless-development'
RETAINED_TYPES = {
    'AWS::KMS::Key', 'AWS::SecretsManager::Secret', 'AWS::S3::Bucket',
    'AWS::DynamoDB::Table', 'AWS::Cognito::UserPool', 'AWS::Logs::LogGroup',
}
APPLICATION_IDS = {'Database', 'DatabaseWriter'} | {
    role + 'Function' for role in ('Api', 'Worker', 'Dispatcher', 'Maintenance', 'Control')
}


def _pages(client, operation, **options):
    for number, page in enumerate(client.get_paginator(operation).paginate(**options)):
        if number >= 20:
            raise Gate('Initial recovery inventory exceeded its bound')
        yield page


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
    temporary = path.with_suffix(path.suffix + '.new')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _require_tags(tags):
    actual = {entry['Key']: entry['Value'] for entry in tags}
    if actual.get('deployment') != STACK or actual.get('environment') != 'serverless-development':
        raise Gate('Initial recovery found a resource without the exact deployment ownership tags')


def _verify_retained(aws, config, logical, resource, physical):
    """Read configuration and emptiness, never secret values or object contents."""
    kind, props = resource['Type'], resource['Properties']
    if kind == 'AWS::S3::Bucket':
        expected = f"{STACK}-{config['account']}-{config['region']}-"
        if physical != props['BucketName'] or not physical.startswith(expected):
            raise Gate('Initial recovery bucket identity differs from the owned template')
        s3 = aws.client('s3')
        _require_tags(s3.get_bucket_tagging(Bucket=physical)['TagSet'])
        versions = s3.list_object_versions(Bucket=physical, MaxKeys=1)
        if versions.get('Versions') or versions.get('DeleteMarkers') or versions.get('IsTruncated'):
            raise Gate('Initial recovery requires all retained buckets, including the deletion journal, to be empty')
        uploads = s3.list_multipart_uploads(Bucket=physical, MaxUploads=1)
        if uploads.get('Uploads') or uploads.get('IsTruncated'):
            raise Gate('Initial recovery requires no outstanding retained-bucket multipart uploads')
    elif kind == 'AWS::DynamoDB::Table':
        client = aws.client('dynamodb')
        table = client.describe_table(TableName=physical)['Table']
        if physical != props['TableName'] or table.get('TableStatus') != 'ACTIVE':
            raise Gate('Initial recovery control table identity or state differs')
        _require_tags(client.list_tags_of_resource(ResourceArn=table['TableArn'])['Tags'])
        result = client.scan(TableName=physical, Select='COUNT', Limit=1, ConsistentRead=True)
        if result.get('Count', 0) or result.get('LastEvaluatedKey'):
            raise Gate('Initial recovery requires an empty runtime control table')
    elif kind == 'AWS::Cognito::UserPool':
        client = aws.client('cognito-idp')
        pool = client.describe_user_pool(UserPoolId=physical)['UserPool']
        if not physical.startswith(config['region'] + '_') or pool.get('Name') != props['UserPoolName']:
            raise Gate('Initial recovery Cognito identity differs from the owned template')
        _require_tags([{'Key': key, 'Value': value} for key, value in pool.get('UserPoolTags', {}).items()])
        if client.list_users(UserPoolId=physical, Limit=1).get('Users'):
            raise Gate('Initial recovery requires a user pool with no accounts')
    elif kind == 'AWS::SecretsManager::Secret':
        secret = aws.client('secretsmanager').describe_secret(SecretId=physical)
        if (secret.get('Name') != props['Name'] or secret.get('ARN') != physical
                or secret.get('DeletedDate') or not physical.startswith(f"arn:aws:secretsmanager:{config['region']}:{config['account']}:secret:")):
            raise Gate('Initial recovery secret identity or state differs')
        _require_tags(secret.get('Tags', []))
    elif kind == 'AWS::KMS::Key':
        client = aws.client('kms')
        key = client.describe_key(KeyId=physical)['KeyMetadata']
        if (key.get('KeyId') != physical or key.get('AWSAccountId') != config['account']
                or key.get('Description') != props['Description'] or key.get('KeyState') != 'Enabled'):
            raise Gate('Initial recovery encryption authority identity or state differs')
        tags = client.list_resource_tags(KeyId=physical)
        if tags.get('Truncated'):
            raise Gate('Initial recovery key tag inventory exceeded its bound')
        _require_tags([{'Key': tag['TagKey'], 'Value': tag['TagValue']} for tag in tags.get('Tags', [])])
    elif kind == 'AWS::Logs::LogGroup':
        client = aws.client('logs')
        groups = client.describe_log_groups(logGroupNamePrefix=physical, limit=50).get('logGroups', [])
        exact = [group for group in groups if group.get('logGroupName') == physical]
        if physical != props['LogGroupName'] or len(exact) != 1:
            raise Gate('Initial recovery log group identity differs from the owned template')
        arn = exact[0]['arn'].removesuffix(':*')
        _require_tags([{'Key': key, 'Value': value} for key, value in client.list_tags_for_resource(resourceArn=arn).get('tags', {}).items()])


def _initial_recovery_plan(aws, config, original_stack_id=None):
    """Validate the complete recovery before any mutation and retain no secrets."""
    if (config.get('environment') != 'serverless-development' or config.get('region') != 'us-east-2'
            or not re.fullmatch(r'\d{12}', config.get('account', ''))
            or not re.fullmatch(r'[0-9a-f]{40}', config.get('releaseId', ''))):
        raise Gate('Initial recovery requires the explicit reviewed serverless target')
    if aws.client('sts').get_caller_identity()['Account'] != config['account']:
        raise Gate('Initial recovery credentials do not match the selected account')
    cf = aws.client('cloudformation')
    stack = cf.describe_stacks(StackName=original_stack_id or STACK)['Stacks'][0]
    stack_tags = {tag['Key']: tag['Value'] for tag in stack.get('Tags', [])}
    if (stack.get('StackStatus') != ('DELETE_COMPLETE' if original_stack_id else 'ROLLBACK_COMPLETE')
            or stack_tags.get('deployment') != STACK or stack_tags.get('purpose') != 'serverless-development'
            or not stack.get('StackId', '').startswith(f"arn:aws:cloudformation:{config['region']}:{config['account']}:stack/{STACK}/")
            or (original_stack_id and stack.get('StackId') != original_stack_id)):
        raise Gate('Only the owned fully rolled-back first application stack can use initial recovery')
    original = cf.get_template(StackName=stack['StackId'], TemplateStage='Original')['TemplateBody']
    if isinstance(original, str):
        if len(original.encode()) > 1048576:
            raise Gate('Initial recovery original template exceeded its bound')
        original = json.loads(original)
    resources = original.get('Resources', {})
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
    if original != expected:
        raise Gate('Initial recovery original template differs from the reviewed stopped deployment')
    events = [event for page in _pages(cf, 'describe_stack_events', StackName=stack['StackId'])
              for event in page.get('StackEvents', [])]
    if len(events) > 2000:
        raise Gate('Initial recovery event history exceeded its bound')
    if any(event.get('ResourceStatus', '').startswith(('UPDATE_', 'IMPORT_')) for event in events):
        raise Gate('Initial recovery requires a first creation attempt without update or import history')
    if any(event.get('LogicalResourceId') in APPLICATION_IDS
           and event.get('ResourceStatus') == 'CREATE_COMPLETE' for event in events):
        raise Gate('Initial recovery cannot adopt a database or application function that was created before rollback')
    if not any(event.get('ResourceType') == 'AWS::CloudFormation::Stack'
               and event.get('PhysicalResourceId') == stack['StackId']
               and event.get('ResourceStatus') == 'CREATE_IN_PROGRESS' for event in events):
        raise Gate('Initial recovery requires complete history including the original stack creation event')
    rows = [row for page in _pages(cf, 'list_stack_resources', StackName=stack['StackId'])
            for row in page.get('StackResourceSummaries', [])]
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
        if (status != 'DELETE_SKIPPED' or kind not in RETAINED_TYPES or not physical
                or resource.get('DeletionPolicy') != 'Retain' or resource.get('UpdateReplacePolicy') != 'Retain'):
            raise Gate('Initial recovery found an unaccounted or non-retained surviving resource')
        imported[logical] = deepcopy(resource)
        physical_ids[logical] = physical
    if not imported or {'DataKey', 'JournalKey', 'CaptureSigningKey', 'ApplicationSecret',
                        'TombstoneSecret', 'DeletionJournal', 'RuntimeControl', 'Accounts'} - imported.keys():
        raise Gate('Initial recovery is missing required retained authority resources')
    if any(_references(resource) - imported.keys() for resource in imported.values()):
        raise Gate('Initial recovery import template references a resource that did not survive rollback')
    for logical in sorted(imported):
        _verify_retained(aws, config, logical, imported[logical], physical_ids[logical])
    rds = aws.client('rds')
    _absent(rds, 'describe_db_clusters', {'DBClusterNotFoundFault'}, DBClusterIdentifier=STACK)
    _absent(rds, 'describe_db_instances', {'DBInstanceNotFound'}, DBInstanceIdentifier=STACK + '-writer')
    functions = aws.client('lambda')
    for role in ('api', 'worker', 'dispatcher', 'maintenance', 'control'):
        _absent(functions, 'get_function', {'ResourceNotFoundException'}, FunctionName=STACK + '-' + role)
    template = {'AWSTemplateFormatVersion': '2010-09-09',
                'Description': 'Retained resources from the uninitialized first serverless deployment',
                'Resources': imported}
    body = json.dumps(template, separators=(',', ':'))
    if len(body.encode()) > 51200:
        raise Gate('Initial recovery import template exceeds the direct CloudFormation limit')
    summaries = cf.get_template_summary(TemplateBody=body).get('ResourceIdentifierSummaries', [])
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
            'import_template': template, 'import_template_sha256': hashlib.sha256(body.encode()).hexdigest(),
            'resources_to_import': [{'LogicalResourceId': logical, 'ResourceType': imported[logical]['Type'],
                'ResourceIdentifier': {identifiers[logical]: physical_ids[logical]}} for logical in sorted(imported)],
            'initial_state': {'database_absent': True, 'application_functions_absent': True,
                              'retained_buckets_empty': True, 'control_table_empty': True, 'user_pool_empty': True,
                              'initial_creation_history_verified': True, 'stack_event_count': len(events)},
            'actual_resources_deleted': False, 'application_deployment_completed': False}


def initial_recovery_plan(aws, config):
    """Inspect only the owned rolled-back first stack before detachment."""
    return _initial_recovery_plan(aws, config)


def _verify_initial_state(aws, config, evidence):
    for logical, resource in evidence['import_template']['Resources'].items():
        _verify_retained(aws, config, logical, resource, evidence['retained_physical_ids'][logical])
    rds = aws.client('rds')
    _absent(rds, 'describe_db_clusters', {'DBClusterNotFoundFault'}, DBClusterIdentifier=STACK)
    _absent(rds, 'describe_db_instances', {'DBInstanceNotFound'}, DBInstanceIdentifier=STACK + '-writer')
    for role in ('api', 'worker', 'dispatcher', 'maintenance', 'control'):
        _absent(aws.client('lambda'), 'get_function', {'ResourceNotFoundException'},
                FunctionName=STACK + '-' + role)


def _verify_imported_stack(cf, evidence, stack):
    resources = evidence['import_template']['Resources']
    rows = [row for page in _pages(cf, 'list_stack_resources', StackName=stack['StackId'])
            for row in page.get('StackResourceSummaries', [])]
    tags = {tag['Key']: tag['Value'] for tag in stack.get('Tags', [])}
    if (stack.get('StackStatus') != 'IMPORT_COMPLETE'
            or (tags and (tags.get('deployment') != STACK or tags.get('purpose') != 'serverless-development'))
            or stack.get('StackId') == evidence['original_stack_id']
            or not stack.get('StackId', '').startswith(
                f"arn:aws:cloudformation:{evidence['region']}:{evidence['account']}:stack/{STACK}/")
            or len(rows) != len(resources)
            or {row.get('LogicalResourceId'): row.get('PhysicalResourceId') for row in rows}
                != evidence['retained_physical_ids']
            or any(row.get('ResourceType') != resources.get(row.get('LogicalResourceId'), {}).get('Type')
                   # CloudFormation applies stack-level tags during import and
                   # reports those preserved resources as UPDATE_COMPLETE.
                   or row.get('ResourceStatus') not in ('IMPORT_COMPLETE', 'UPDATE_COMPLETE') for row in rows)):
        raise Gate('Initial recovery did not prove adoption of every original retained resource')
    original = cf.get_template(StackName=stack['StackId'], TemplateStage='Original')['TemplateBody']
    if isinstance(original, str):
        if len(original.encode()) > 51200:
            raise Gate('Initial recovery imported template exceeded its bound')
        original = json.loads(original)
    if original != evidence['import_template']:
        raise Gate('Initial recovery imported stack template differs from the preserved resources')


def _record_failure(evidence, phase, error):
    evidence['failed_phase'] = evidence['status']
    evidence['failure_type'] = type(error).__name__
    if isinstance(error, ClientError):
        evidence['failure_operation'] = str(error.operation_name)[:100]
        evidence['failure_code'] = str(error.response.get('Error', {}).get('Code', ''))[:100]
        evidence['failure_request_id'] = str(error.response.get('ResponseMetadata', {}).get('RequestId', ''))[:100]
    phase('blocked-recovery-inspect-protected-journal-before-retry')


def _import_retained(aws, config, evidence, phase):
    cf = aws.client('cloudformation')
    _verify_initial_state(aws, config, evidence)
    change = cf.create_change_set(StackName=STACK, ChangeSetName='initial-import-' + uuid.uuid4().hex,
        ChangeSetType='IMPORT', TemplateBody=json.dumps(evidence['import_template'], separators=(',', ':')),
        ResourcesToImport=evidence['resources_to_import'])['Id']
    evidence['import_change_set_id'] = change
    phase('import-change-set-created')
    cf.get_waiter('change_set_create_complete').wait(StackName=STACK, ChangeSetName=change,
        WaiterConfig={'Delay': 3, 'MaxAttempts': 120})
    changes = [row.get('ResourceChange', {}) for page in _pages(cf, 'describe_change_set',
        StackName=STACK, ChangeSetName=change) for row in page.get('Changes', [])]
    resources = evidence['import_template']['Resources']
    if (len(changes) != len(resources) or {row.get('LogicalResourceId') for row in changes} != resources.keys()
            or any(row.get('Action') != 'Import' or row.get('ResourceType') != resources[row['LogicalResourceId']]['Type']
                   or row.get('Replacement') in ('True', 'Conditional') for row in changes)):
        cf.delete_change_set(StackName=STACK, ChangeSetName=change)
        raise Gate('Initial recovery change set is not an import of the exact preserved resources')
    # Recheck live authority immediately before executing the reviewed import.
    _verify_initial_state(aws, config, evidence)
    cf.update_termination_protection(StackName=STACK, EnableTerminationProtection=True)
    phase('import-executing')
    cf.execute_change_set(StackName=STACK, ChangeSetName=change)
    cf.get_waiter('stack_import_complete').wait(StackName=STACK,
        WaiterConfig={'Delay': 5, 'MaxAttempts': 180})
    stack = cf.describe_stacks(StackName=STACK)['Stacks'][0]
    _verify_imported_stack(cf, evidence, stack)
    if not stack.get('EnableTerminationProtection'):
        raise Gate('Initial recovery imported stack lacks termination protection')
    evidence['recovered_stack_id'] = stack['StackId']
    phase('uninitialized-retained-resources-imported')
    return evidence


def recover_initial(aws, config, evidence_path):
    """Detach failed stack metadata, then adopt the identical retained resources."""
    path = Path(evidence_path)
    if path.exists() or not path.parent.is_dir():
        raise Gate('Use a new protected initial recovery journal in an existing deployment work directory')
    evidence = initial_recovery_plan(aws, config)
    _write(path, evidence)
    cf = aws.client('cloudformation')

    def phase(status):
        evidence['status'] = status
        _write(path, evidence)

    try:
        phase('detaching-failed-stack-metadata')
        cf.update_termination_protection(StackName=evidence['original_stack_id'], EnableTerminationProtection=False)
        cf.delete_stack(StackName=evidence['original_stack_id'])
        cf.get_waiter('stack_delete_complete').wait(StackName=evidence['original_stack_id'],
            WaiterConfig={'Delay': 5, 'MaxAttempts': 120})
        phase('failed-stack-metadata-detached')
        return _import_retained(aws, config, evidence, phase)
    except Exception as error:
        _record_failure(evidence, phase, error)
        raise


def _read_source_manifest(path, expected_sha256):
    if not isinstance(expected_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise Gate('Initial recovery resume requires the trusted artifact manifest SHA-256')
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > 262144 or info.st_mode & 0o022:
            raise Gate('Initial recovery source manifest must be a bounded protected regular file')
        raw = stream.read(262145)
    if len(raw) > 262144 or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise Gate('Initial recovery source manifest differs from the trusted artifact SHA-256')

    def closed_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Gate('Initial recovery source manifest contains duplicate JSON keys')
            result[key] = value
        return result

    try:
        evidence = json.loads(raw, object_pairs_hook=closed_pairs)
    except (ValueError, UnicodeError) as error:
        raise Gate('Initial recovery source manifest is not valid JSON evidence') from error
    if not isinstance(evidence, dict):
        raise Gate('Initial recovery source manifest must be a JSON object')
    return evidence


def _verify_source_manifest(aws, config, source):
    detached = source.get('status') == 'failed-stack-metadata-detached' or (
        source.get('status') == 'blocked-recovery-inspect-protected-journal-before-retry'
        and source.get('failed_phase') == 'failed-stack-metadata-detached')
    if (source.get('schema_version') != '1.0.0' or source.get('operation') != 'serverless-initial-recovery'
            or source.get('account') != config.get('account') or source.get('region') != config.get('region')
            or source.get('environment', 'serverless-development') != 'serverless-development'
            or source.get('stack_name') != STACK or not detached or source.get('import_change_set_id')
            or source.get('actual_resources_deleted') is not False
            or source.get('application_deployment_completed') is not False
            or not isinstance(source.get('release_id'), str)
            or not re.fullmatch(r'[0-9a-f]{40}', source['release_id'])
            or not isinstance(source.get('original_release_id'), str)
            or not re.fullmatch(r'[0-9a-f]{40}', source['original_release_id'])
            or not isinstance(source.get('import_template_sha256'), str)
            or not re.fullmatch(r'[0-9a-f]{64}', source['import_template_sha256'])
            or not isinstance(source.get('original_stack_id'), str)
            or not re.fullmatch(
                f"arn:aws:cloudformation:{re.escape(config.get('region', ''))}:{re.escape(config.get('account', ''))}"
                f":stack/{STACK}/[A-Za-z0-9-]+", source['original_stack_id'])):
        raise Gate('Initial recovery source manifest is not the exact detached first-deployment recovery')
    # The trusted journal is evidence, while deleted-stack history independently
    # establishes the original complete inventory, stopped template and absence
    # of any successfully created application runtime.
    plan = _initial_recovery_plan(aws, config, source['original_stack_id'])
    for field in ('original_stack_id', 'original_release_id', 'retained_physical_ids', 'import_template'):
        if source.get(field) != plan[field]:
            raise Gate('Initial recovery source manifest differs from the original deleted-stack ' + field)
    descriptors = source.get('resources_to_import')
    if (not isinstance(descriptors, list) or not all(isinstance(row, dict)
            and isinstance(row.get('LogicalResourceId'), str) for row in descriptors)
            or len(descriptors) != len(plan['resources_to_import'])
            or {row['LogicalResourceId']: row for row in descriptors}
                != {row['LogicalResourceId']: row for row in plan['resources_to_import']}):
        raise Gate('Initial recovery source manifest differs from the original deleted-stack import identifiers')
    # Legacy evidence hashed insertion-ordered JSON, then sorted its keys while
    # saving. The trusted whole-file digest preserves that legacy hash. Compare
    # canonical content against independent AWS history instead of requiring an
    # undocumented API ordering to reproduce the lost original serialization.
    canonical = hashlib.sha256(json.dumps(source['import_template'],
        separators=(',', ':'), sort_keys=True).encode()).hexdigest()
    authoritative = hashlib.sha256(json.dumps(plan['import_template'],
        separators=(',', ':'), sort_keys=True).encode()).hexdigest()
    if canonical != authoritative or source.get('canonical_import_template_sha256', canonical) != canonical:
        raise Gate('Initial recovery source manifest canonical template hash differs from deleted-stack history')
    initial = source.get('initial_state')
    if not isinstance(initial, dict) or any(initial.get(field) is not True for field in (
            'database_absent', 'application_functions_absent', 'retained_buckets_empty',
            'control_table_empty', 'user_pool_empty', 'initial_creation_history_verified')):
        raise Gate('Initial recovery source manifest does not prove the original uninitialized state')
    count = initial.get('stack_event_count')
    if type(count) is not int or not 1 <= count <= plan['initial_state']['stack_event_count']:
        raise Gate('Initial recovery source manifest original history count differs from deleted-stack history')
    return plan


def _resume_stack(cf):
    try:
        stacks = cf.describe_stacks(StackName=STACK)['Stacks']
    except ClientError as error:
        details = error.response.get('Error', {})
        if (details.get('Code') == 'ValidationError' and details.get('Message') in (
                f'Stack with id {STACK} does not exist', f'Stack with id {STACK} does not exist.')):
            return None
        raise
    if len(stacks) != 1:
        raise Gate('Initial recovery resume target stack inventory is ambiguous')
    return stacks[0]


def resume_initial(aws, config, evidence_path, source_manifest, source_manifest_sha256):
    """Resume detached metadata using trusted evidence and deleted-stack history.

    The caller must verify the source artifact's workflow and historic source
    admission before supplying its SHA-256. This path never deletes a stack or
    creates authority resources, and writes only a new local protected journal.
    """
    path = Path(evidence_path)
    if path.exists() or path.is_symlink() or not path.parent.is_dir():
        raise Gate('Use a new protected initial recovery journal in an existing deployment work directory')
    source = _read_source_manifest(source_manifest, source_manifest_sha256)
    plan = _verify_source_manifest(aws, config, source)
    cf = aws.client('cloudformation')
    stack = _resume_stack(cf)
    if stack:
        # An interrupted import can be admitted only after complete adoption;
        # REVIEW_IN_PROGRESS and all active/updated stacks need a separate review.
        _verify_imported_stack(cf, plan, stack)
    evidence = deepcopy(source)
    evidence.update(release_id=config['releaseId'], prior_recovery_release_id=source['release_id'],
        source_manifest_sha256=source_manifest_sha256,
        canonical_import_template_sha256=hashlib.sha256(json.dumps(source['import_template'],
            separators=(',', ':'), sort_keys=True).encode()).hexdigest(),
        status='failed-stack-metadata-detached')
    for field in ('failed_phase', 'failure_type', 'failure_operation', 'failure_code', 'failure_request_id'):
        evidence.pop(field, None)
    _write(path, evidence)

    def phase(status):
        evidence['status'] = status
        _write(path, evidence)

    try:
        if not stack:
            return _import_retained(aws, config, evidence, phase)
        _verify_initial_state(aws, config, evidence)
        if not stack.get('EnableTerminationProtection'):
            cf.update_termination_protection(StackName=stack['StackId'], EnableTerminationProtection=True)
        evidence['recovered_stack_id'] = stack['StackId']
        phase('uninitialized-retained-resources-imported')
        return evidence
    except Exception as error:
        _record_failure(evidence, phase, error)
        raise


def verify_recovery_artifact(manifest_path, artifact_proof, *, client=None):
    """Bind exact manifest bytes to a real failed trusted GitHub deployment ZIP.

    ``artifact_proof`` contains the run ID, artifact ID and downloaded ZIP path.
    Its assertions alone confer no trust: live repository metadata and the ZIP
    digest must match, and the ZIP must contain these exact manifest bytes.
    """
    if (not isinstance(artifact_proof, dict) or set(artifact_proof) != {'run_id', 'artifact_id', 'archive_path'}
            or any(type(artifact_proof.get(key)) is not int or artifact_proof[key] <= 0
                   for key in ('run_id', 'artifact_id'))):
        raise Gate('A downloaded trusted GitHub recovery artifact is required')
    if client is None:
        headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = 'Bearer ' + token
        with httpx.Client(headers=headers, timeout=15, follow_redirects=False) as owned:
            return verify_recovery_artifact(manifest_path, artifact_proof, client=owned)
    manifest_raw = bounded_file(manifest_path, 262144)
    try:
        manifest = strict_loads(manifest_raw)
    except (ValueError, TypeError):
        raise Gate('Recovery artifact manifest is not strict JSON') from None
    if not isinstance(manifest, dict):
        raise Gate('Recovery artifact manifest must be an object')
    run_id, artifact_id = artifact_proof['run_id'], artifact_proof['artifact_id']
    run = _github_json(client, f'actions/runs/{run_id}')
    workflow_id = run.get('workflow_id')
    workflow_path = '.github/workflows/deploy-serverless.yml'
    if (run.get('id') != run_id or run.get('head_sha') != manifest.get('release_id')
            or run.get('status') != 'completed' or run.get('conclusion') != 'failure'
            or run.get('path') != workflow_path or run.get('event') != 'workflow_dispatch'
            or run.get('head_branch') != 'main' or type(workflow_id) is not int or workflow_id <= 0
            or run.get('repository', {}).get('full_name') != REPOSITORY
            or run.get('head_repository', {}).get('full_name') != REPOSITORY):
        raise Gate('Recovery artifact must belong to a failed trusted-main serverless deployment')
    workflow = _github_json(client, f'actions/workflows/{workflow_id}')
    if workflow.get('id') != workflow_id or workflow.get('path') != workflow_path or workflow.get('state') != 'active':
        raise Gate('Recovery artifact does not belong to the trusted deployment workflow')
    artifact = _github_json(client, f'actions/artifacts/{artifact_id}')
    revision = manifest['release_id']
    binding = artifact.get('workflow_run', {})
    if (artifact.get('id') != artifact_id or artifact.get('expired') is not False
            or artifact.get('name') != f'serverless-deployment-{revision}-{run_id}'
            or binding.get('id') != run_id or binding.get('head_sha') != revision
            or binding.get('head_branch') != 'main' or binding.get('repository_id') != run['repository'].get('id')
            or binding.get('head_repository_id') != run['head_repository'].get('id')):
        raise Gate('Recovery archive metadata is not bound to the trusted failed run')
    archive_path = artifact_proof['archive_path']
    archive = bounded_file(archive_path, 32 * 1024 * 1024)
    digest = hashlib.sha256(archive).hexdigest()
    if artifact.get('digest') != 'sha256:' + digest:
        raise Gate('Downloaded recovery archive differs from the trusted GitHub digest')
    try:
        with ZipFile(io.BytesIO(archive)) as zipped:
            candidates = [entry for entry in zipped.infolist() if entry.filename.endswith('/initial-recovery.json')]
            if (len(candidates) != 1 or candidates[0].file_size > 262144
                    or candidates[0].filename.count('..')
                    or not candidates[0].filename.startswith('.local/deploy/serverless-development/' + revision + '/')):
                raise Gate('Recovery archive must contain one bounded deployment recovery manifest')
            if zipped.read(candidates[0]) != manifest_raw:
                raise Gate('Recovery manifest bytes differ from the trusted archived manifest')
    except (BadZipFile, OSError, RuntimeError):
        raise Gate('Trusted recovery archive cannot be read') from None
    current = _github_json(client, f'actions/runs/{run_id}')
    if any(current.get(key) != run.get(key) for key in ('id', 'run_attempt', 'head_sha', 'workflow_id', 'status', 'conclusion')):
        raise Gate('Trusted recovery run changed during evidence verification')
    return {'provider': 'github_actions', 'repository': REPOSITORY, 'workflow_path': workflow_path,
            'run_id': run_id, 'head_sha': revision, 'artifact_id': artifact_id,
            'archive_sha256': digest, 'manifest_sha256': hashlib.sha256(manifest_raw).hexdigest()}

def resume_initial_from_artifact(aws, config, manifest_path, evidence_path, *, artifact_proof):
    """Independently bind the legacy resume operation to its trusted run ZIP."""
    evidence_path = Path(evidence_path)
    if evidence_path.exists() or evidence_path.is_symlink() or not evidence_path.parent.is_dir():
        raise Gate('Use a new protected recovery journal for trusted artifact resume')
    proof = verify_recovery_artifact(manifest_path, artifact_proof)
    try:
        result = resume_initial(aws, config, evidence_path, manifest_path, proof['manifest_sha256'])
    finally:
        # Retain trusted artifact provenance with either success or failure.
        if Path(evidence_path).is_file():
            evidence = bounded_json(evidence_path, 262144)
            evidence['resumed_from'] = proof
            _write(evidence_path, evidence)
    result['resumed_from'] = proof
    return result
