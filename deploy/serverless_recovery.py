"""Recover an uninitialized failed first stack without deleting retained resources.

The caller must admit the exact reviewed source before invoking this mutation.
This path is deliberately unavailable for a database or journal that has ever
been initialized. CloudFormation imports only the original retained resources;
the regular deployment subsequently creates the stopped application runtime.
"""
from __future__ import annotations

from copy import deepcopy
import ast
from datetime import datetime, timezone
import hashlib
import ipaddress
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import uuid
from zipfile import BadZipFile, ZipFile
import httpx

from botocore.exceptions import ClientError

from deploy.provenance import (
    Gate, REPOSITORY, REQUIRED_JOBS, WORKFLOW_PATH, _github_json,
    bounded_file, bounded_json, strict_loads,
)
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


def _historical_template_config(config, resources):
    """Reconstruct historical inputs from independently fetched template metadata."""
    tags = {row['Key']: row['Value'] for row in resources['DataKey']['Properties']['Tags']}
    return {**config,
        'releaseId': resources['ApiFunction']['Properties']['Environment']['Variables']['OTGD_SOURCE_REVISION'],
        'apiImageUri': resources['ApiFunction']['Properties']['Code']['ImageUri'],
        'workerImageUri': resources['WorkerFunction']['Properties']['Code']['ImageUri'],
        'databaseEngineVersion': resources['Database']['Properties']['EngineVersion'],
        'monthlyBudgetUsd': resources['MonthlyBudget']['Properties']['Budget']['BudgetLimit']['Amount'],
        'alarmEmail': resources['Notifications']['Properties']['Subscription'][0]['Endpoint'],
        'ownerRole': tags['owner_role'], 'costCenter': tags['cost_center'], 'activateServices': False}


def _initial_recovery_plan(aws, config, original_stack_id=None, *, template_builder=None,
                           require_database_absent=True):
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
        old_config = _historical_template_config(config, resources)
        expected = (template_builder or build_template)(old_config)
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
    if require_database_absent:
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
    # Botocore returns nested OrderedDict values; their equality treats object
    # key order as meaningful even when the complete JSON content is identical.
    actual_body = json.dumps(original, separators=(',', ':'), sort_keys=True)
    expected_body = json.dumps(evidence['import_template'], separators=(',', ':'), sort_keys=True)
    if actual_body != expected_body:
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


def _verify_source_manifest(aws, config, source, *, template_builder=None, require_database_absent=True):
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
    plan = _initial_recovery_plan(aws, config, source['original_stack_id'],
        template_builder=template_builder, require_database_absent=require_database_absent)
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


# A failed stopped-platform update can leave this exact database dependency
# graph behind. Its writer was retained without remaining in the old template.
DATABASE_IMPORT_IDS = {
    'Network': ('AWS::EC2::VPC', ('VpcId',)),
    'NetworkIpv6': ('AWS::EC2::VPCCidrBlock', ('Id', 'VpcId')),
    'PrivateA': ('AWS::EC2::Subnet', ('SubnetId',)),
    'LambdaSecurityGroup': ('AWS::EC2::SecurityGroup', ('Id',)),
    'DatabaseSecurityGroup': ('AWS::EC2::SecurityGroup', ('Id',)),
    'DatabaseParameters': ('AWS::RDS::DBClusterParameterGroup', ('DBClusterParameterGroupName',)),
    'DatabaseSubnets': ('AWS::RDS::DBSubnetGroup', ('DBSubnetGroupName',)),
    'Database': ('AWS::RDS::DBCluster', ('DBClusterIdentifier',)),
    'DatabaseWriter': ('AWS::RDS::DBInstance', ('DBInstanceIdentifier',)),
}
CONTINUATION_FIELDS = {
    'schema_version', 'operation', 'account', 'region', 'stack_name', 'failed_run_id',
    'failed_run_attempt', 'failed_release_id', 'artifact_sha256', 'failed_run_started_at',
    'failed_run_completed_at', 'original_recovery_raw', 'adoption_raw',
    'deployment_state_raw', 'gate_admission_raw', 'serverless_plan_raw',
}


def _utc_time(value):
    if not isinstance(value, (str, datetime)):
        raise Gate('Uninitialized continuation requires bounded UTC creation history')
    try:
        result = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
            raise ValueError
        return result
    except (ValueError, AttributeError):
        raise Gate('Uninitialized continuation creation history is not UTC') from None


def _continuation_bundle(path, expected_hash, config):
    if not isinstance(expected_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_hash):
        raise Gate('Uninitialized continuation requires the authenticated protected bundle SHA-256')
    raw = bounded_file(Path(path), 8 * 1024 * 1024, private=True)
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise Gate('Uninitialized continuation bundle differs from its authenticated SHA-256')
    try:
        bundle = strict_loads(raw)
        if not isinstance(bundle, dict) or set(bundle) != CONTINUATION_FIELDS:
            raise ValueError
        records = {}
        for field in ('original_recovery_raw', 'adoption_raw', 'deployment_state_raw',
                      'gate_admission_raw', 'serverless_plan_raw'):
            value = bundle[field]
            if not isinstance(value, str) or not 0 < len(value.encode()) <= 262144:
                raise ValueError
            records[field] = strict_loads(value)
            if not isinstance(records[field], dict):
                raise ValueError
    except (ValueError, TypeError, KeyError):
        raise Gate('Uninitialized continuation requires the exact bounded strict-JSON evidence bundle') from None
    if (bundle['schema_version'] != '1.0.0' or bundle['operation'] != 'serverless-uninitialized-continuation'
            or bundle['account'] != config.get('account') or bundle['region'] != config.get('region')
            or bundle['stack_name'] != STACK
            or type(bundle['failed_run_id']) is not int or bundle['failed_run_id'] <= 0
            or type(bundle['failed_run_attempt']) is not int or bundle['failed_run_attempt'] <= 0
            or not re.fullmatch(r'[0-9a-f]{40}', str(bundle['failed_release_id']))
            or not re.fullmatch(r'[0-9a-f]{64}', str(bundle['artifact_sha256']))):
        raise Gate('Uninitialized continuation source and target binding differs')
    started, completed = _utc_time(bundle['failed_run_started_at']), _utc_time(bundle['failed_run_completed_at'])
    if started > completed or completed > datetime.now(timezone.utc):
        raise Gate('Uninitialized continuation failed-run history interval differs')
    original, adoption, state, gate, plan = (records[field] for field in (
        'original_recovery_raw', 'adoption_raw', 'deployment_state_raw', 'gate_admission_raw', 'serverless_plan_raw'))
    expected_stages = ['resume-initial-retained-resources', 'serverless-registry',
                       'exact-source-archive', 'build-immutable-lambda-images']
    if (state.get('schema_version') != '1.0.0' or state.get('environment') != 'serverless-development'
            or state.get('account') != config['account'] or state.get('region') != config['region']
            or state.get('release_id') != bundle['failed_release_id'] or state.get('status') != 'failed'
            or state.get('failed_stage') != 'deploy-stopped' or state.get('current_stage') != 'deploy-stopped'
            or state.get('completed_stages') != expected_stages or state.get('completed_receipts') != {}
            or state.get('rollback_executed') is not False):
        raise Gate('Uninitialized continuation must precede the first bootstrap, migration and admission')
    if (gate.get('provider') != 'github_actions' or gate.get('repository') != REPOSITORY
            or gate.get('workflow_path') != WORKFLOW_PATH or gate.get('head_sha') != bundle['failed_release_id']
            or gate.get('event') != 'push' or gate.get('head_branch') != 'main'
            or not isinstance(gate.get('jobs'), dict) or gate['jobs'].keys() != REQUIRED_JOBS
            or any(type(value) is not int or value <= 0 for value in gate['jobs'].values())
            or plan.get('environment') != 'serverless-development' or plan.get('account') != config['account']
            or plan.get('region') != config['region'] or plan.get('deployment_executed') is not False):
        raise Gate('Uninitialized continuation does not bind the historical admitted main deployment')
    if (adoption.get('schema_version') != '1.0.0' or adoption.get('operation') != 'serverless-initial-recovery'
            or adoption.get('account') != config['account'] or adoption.get('region') != config['region']
            or adoption.get('stack_name') != STACK or adoption.get('release_id') != bundle['failed_release_id']
            or adoption.get('status') != 'uninitialized-retained-resources-imported'
            or adoption.get('actual_resources_deleted') is not False
            or adoption.get('application_deployment_completed') is not False
            or adoption.get('source_manifest_sha256') != hashlib.sha256(bundle['original_recovery_raw'].encode()).hexdigest()
            or not isinstance(adoption.get('recovered_stack_id'), str)
            or not re.fullmatch(f"arn:aws:cloudformation:{config['region']}:{config['account']}:stack/{STACK}/[A-Za-z0-9-]+",
                                adoption['recovered_stack_id'])):
        raise Gate('Uninitialized continuation does not preserve the successful original authority adoption')
    for field in ('original_stack_id', 'original_release_id', 'retained_physical_ids', 'import_template',
                  'import_template_sha256', 'resources_to_import'):
        if adoption.get(field) != original.get(field):
            raise Gate('Uninitialized continuation original authority evidence changed')
    return bundle, original, adoption


def _historical_builder(revision):
    """Load only the bounded builder from the independently admitted main SHA.

    The protected bundle is admitted by the caller's historical GitHub gates.
    This is repository source, never executable content from the JSON evidence.
    """
    root = Path(__file__).resolve().parents[1]
    try:
        name = revision + ':deploy/serverless_template.py'
        size = subprocess.run(['git', 'cat-file', '-s', name], cwd=root, capture_output=True,
            check=True, timeout=10).stdout
        if not 0 < int(size) <= 262144:
            raise ValueError
        source = subprocess.run(['git', 'show', name], cwd=root, capture_output=True,
            check=True, timeout=10).stdout
        if len(source) != int(size):
            raise ValueError
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Import) and all(alias.name in {'json', 'math', 're'} for alias in node.names):
                continue
            if (isinstance(node, ast.ImportFrom) and node.module == '__future__' and node.level == 0
                    and all(alias.name == 'annotations' and alias.asname is None for alias in node.names)):
                continue
            if isinstance(node, ast.FunctionDef) or (isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
                continue
            raise ValueError
        namespace = {'__name__': '_admitted_historical_serverless_template'}
        exec(compile(tree, name, 'exec'), namespace)
        return namespace['build_template']
    except (ValueError, KeyError, SyntaxError, subprocess.SubprocessError):
        raise Gate('The admitted historical main template builder is unavailable or unsupported') from None


def _template_body(cf, stack_id):
    value = cf.get_template(StackName=stack_id, TemplateStage='Original')['TemplateBody']
    if isinstance(value, str):
        if len(value.encode()) > 1048576:
            raise Gate('Uninitialized continuation template inventory exceeded its bound')
        value = strict_loads(value)
    if not isinstance(value, dict):
        raise Gate('Uninitialized continuation requires a JSON template object')
    return value


def _body_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _one(response, key):
    rows = response.get(key, [])
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise Gate('Uninitialized continuation found an ambiguous live resource inventory')
    return rows[0]


def _resource_tags(client, arn):
    _require_tags(client.list_tags_for_resource(ResourceName=arn).get('TagList', []))


def _history_for_continuation(cf, bundle, stack_id, failed_template):
    events = [event for page in _pages(cf, 'describe_stack_events', StackName=stack_id)
              for event in page.get('StackEvents', [])]
    if len(events) > 2000:
        raise Gate('Uninitialized continuation event history exceeded its bound')
    start, end = _utc_time(bundle['failed_run_started_at']), _utc_time(bundle['failed_run_completed_at'])
    updates = [event for event in events if event.get('ResourceType') == 'AWS::CloudFormation::Stack'
               and event.get('PhysicalResourceId') == stack_id and event.get('ResourceStatus') == 'UPDATE_IN_PROGRESS']
    if len(updates) != 1 or not start <= _utc_time(updates[0].get('Timestamp')) <= end:
        raise Gate('Uninitialized continuation stack update does not bind the failed run interval')
    if any(event.get('LogicalResourceId') in APPLICATION_IDS - {'Database', 'DatabaseWriter', 'ControlFunction'}
           and event.get('ResourceStatus') == 'CREATE_COMPLETE' for event in events):
        raise Gate('Uninitialized continuation cannot adopt a previously created application function')
    controls = [event for event in events if event.get('LogicalResourceId') == 'ControlFunction'
                and event.get('ResourceStatus') == 'CREATE_COMPLETE']
    if controls:
        deleted = [event for event in events if event.get('LogicalResourceId') == 'ControlFunction'
                   and event.get('ResourceStatus') == 'DELETE_COMPLETE'
                   and event.get('ResourceType') == 'AWS::Lambda::Function'
                   and event.get('PhysicalResourceId') == STACK + '-control'
                   and start <= _utc_time(event.get('Timestamp')) <= end]
        if (len(controls) != 1 or controls[0].get('ResourceType') != 'AWS::Lambda::Function'
                or controls[0].get('PhysicalResourceId') != STACK + '-control'
                or not start <= _utc_time(controls[0].get('Timestamp')) <= end or len(deleted) != 1
                or _utc_time(deleted[0]['Timestamp']) < _utc_time(controls[0]['Timestamp'])
                or failed_template['Resources']['ControlFunction']['Properties'].get('ReservedConcurrentExecutions') != 0
                or failed_template['Resources']['ControlSchedule']['Properties'].get('State') != 'DISABLED'):
            raise Gate('Uninitialized continuation control function was not the exact stopped and deleted first control')
    physical = {}
    for logical in DATABASE_IMPORT_IDS.keys() - {'DatabaseWriter'}:
        matching = [event for event in events if event.get('LogicalResourceId') == logical
                    and event.get('ResourceStatus') == 'CREATE_COMPLETE']
        if (len(matching) != 1 or matching[0].get('ResourceType') != DATABASE_IMPORT_IDS[logical][0]
                or not isinstance(matching[0].get('PhysicalResourceId'), str)
                or not matching[0]['PhysicalResourceId']
                or not start <= _utc_time(matching[0].get('Timestamp')) <= end):
            raise Gate('Uninitialized continuation lacks exact failed-run creation history for ' + logical)
        physical[logical] = matching[0]['PhysicalResourceId']
    writer = [event for event in events if event.get('LogicalResourceId') == 'DatabaseWriter'
              and event.get('ResourceStatus') == 'DELETE_SKIPPED']
    missing = [event for event in events if event.get('LogicalResourceId') == 'PrivateB'
               and event.get('ResourceType') == 'AWS::EC2::Subnet'
               and event.get('ResourceStatus') == 'DELETE_COMPLETE'
               and start <= _utc_time(event.get('Timestamp')) <= end]
    if (len(writer) != 1 or writer[0].get('ResourceType') != 'AWS::RDS::DBInstance'
            or writer[0].get('PhysicalResourceId') != STACK + '-writer'
            or not start <= _utc_time(writer[0].get('Timestamp')) <= end
            or len(missing) != 1 or not isinstance(missing[0].get('PhysicalResourceId'), str)
            or not missing[0]['PhysicalResourceId']):
        raise Gate('Uninitialized continuation requires the exact retained writer and deleted second subnet history')
    physical['DatabaseWriter'] = writer[0]['PhysicalResourceId']
    return physical, missing[0]['PhysicalResourceId']


def _absent_stack_binding(cf, stack_id, logical):
    """Require precise missing metadata; this does not prove resource absence."""
    try:
        cf.describe_stack_resource(StackName=stack_id, LogicalResourceId=logical)
    except ClientError as error:
        details = error.response.get('Error', {})
        message = details.get('Message', '')
        if (details.get('Code') != 'ValidationError' or not isinstance(message, str)
                or not re.search(r'\b' + re.escape(logical) + r'\b', message)
                or not any(text in message for text in ('does not exist', 'does not contain'))):
            raise
    else:
        raise Gate('Uninitialized continuation found ambiguous current metadata for ' + logical)


def _security_rules(rows):
    result = set()
    for row in rows:
        protocol, first, last = row.get('IpProtocol'), row.get('FromPort'), row.get('ToPort')
        for field, key in (('IpRanges', 'CidrIp'), ('Ipv6Ranges', 'CidrIpv6'), ('UserIdGroupPairs', 'GroupId')):
            for target in row.get(field, []):
                result.add((protocol, first, last, field, target.get(key)))
        if row.get('PrefixListIds'):
            raise Gate('Uninitialized continuation found an unexpected security-group prefix-list grant')
    return result


def _database_snapshot(aws, config, bundle, physical, deleted_subnet):
    """Read only metadata and configuration, never credentials or SQL contents."""
    rds, ec2 = aws.client('rds'), aws.client('ec2')
    cluster = _one(rds.describe_db_clusters(DBClusterIdentifier=STACK), 'DBClusters')
    writer = _one(rds.describe_db_instances(DBInstanceIdentifier=STACK + '-writer'), 'DBInstances')
    key_arn = f"arn:aws:kms:{config['region']}:{config['account']}:key/{physical['DataKey']}"
    expected_cluster_arn = f"arn:aws:rds:{config['region']}:{config['account']}:cluster:{STACK}"
    expected_writer_arn = f"arn:aws:rds:{config['region']}:{config['account']}:db:{STACK}-writer"
    members = cluster.get('DBClusterMembers', [])
    secret = cluster.get('MasterUserSecret', {})
    scaling = cluster.get('ServerlessV2ScalingConfiguration', {})
    if (cluster.get('DBClusterIdentifier') != physical['Database'] or physical['Database'] != STACK
            or writer.get('DBInstanceIdentifier') != physical['DatabaseWriter']
            or physical['DatabaseWriter'] != STACK + '-writer'
            or cluster.get('DBClusterArn') != expected_cluster_arn
            or writer.get('DBInstanceArn') != expected_writer_arn
            or cluster.get('Status') != 'available' or writer.get('DBInstanceStatus') != 'available'
            or cluster.get('Engine') != 'aurora-postgresql' or writer.get('Engine') != 'aurora-postgresql'
            or not re.fullmatch(r'16\.\d+', str(cluster.get('EngineVersion', '')))
            or writer.get('EngineVersion') != cluster.get('EngineVersion')
            or cluster.get('DatabaseName') != 'otgd' or cluster.get('MasterUsername') != 'otgd_migrator'
            or writer.get('DBInstanceClass') != 'db.serverless'
            or writer.get('DBClusterIdentifier') != STACK or writer.get('PubliclyAccessible') is not False
            or writer.get('AutoMinorVersionUpgrade') is not False
            or cluster.get('PendingModifiedValues', {}) or writer.get('PendingModifiedValues', {})
            or cluster.get('StorageEncrypted') is not True or writer.get('StorageEncrypted') is not True
            or cluster.get('KmsKeyId') != key_arn or writer.get('KmsKeyId') != key_arn
            or cluster.get('DeletionProtection') is not True or cluster.get('BackupRetentionPeriod') != 7
            or len(members) != 1 or members[0].get('DBInstanceIdentifier') != STACK + '-writer'
            or members[0].get('IsClusterWriter') is not True
            or members[0].get('DBClusterParameterGroupStatus') != 'in-sync'
            or secret.get('SecretStatus') != 'active' or secret.get('KmsKeyId') != key_arn
            or not str(secret.get('SecretArn', '')).startswith(
                f"arn:aws:secretsmanager:{config['region']}:{config['account']}:secret:rds!cluster-")
            or scaling != {'MinCapacity': 0, 'MaxCapacity': 1, 'SecondsUntilAutoPause': 300}
            or cluster.get('DBClusterParameterGroup') != physical['DatabaseParameters']
            or cluster.get('DBSubnetGroup') != physical['DatabaseSubnets']
            or not str(cluster.get('DbClusterResourceId', '')).startswith('cluster-')
            or not str(writer.get('DbiResourceId', '')).startswith('db-')):
        raise Gate('Uninitialized continuation database identity, protection or configuration differs')
    start, end = _utc_time(bundle['failed_run_started_at']), _utc_time(bundle['failed_run_completed_at'])
    for value in (cluster.get('ClusterCreateTime'), writer.get('InstanceCreateTime')):
        if not start <= _utc_time(value) <= end:
            raise Gate('Uninitialized continuation database creation is outside the failed run')
    _require_tags(cluster.get('TagList', []))
    _require_tags(writer.get('TagList', []))
    group = _one(rds.describe_db_subnet_groups(DBSubnetGroupName=physical['DatabaseSubnets']), 'DBSubnetGroups')
    writer_group = writer.get('DBSubnetGroup', {})
    subnets = group.get('Subnets', [])
    subnet_ids = [row.get('SubnetIdentifier') for row in subnets]
    if (group.get('DBSubnetGroupName') != physical['DatabaseSubnets'] or group.get('SubnetGroupStatus') != 'Complete'
            or group.get('VpcId') != physical['Network'] or len(subnets) != 2
            or set(subnet_ids) != {physical['PrivateA'], deleted_subnet}
            or any(row.get('SubnetStatus') != 'Active' for row in subnets)
            or writer_group.get('DBSubnetGroupName') != physical['DatabaseSubnets']
            or writer_group.get('VpcId') != physical['Network']
            or {row.get('SubnetIdentifier') for row in writer_group.get('Subnets', [])} != set(subnet_ids)
            or cluster.get('VpcSecurityGroups') != [{'VpcSecurityGroupId': physical['DatabaseSecurityGroup'], 'Status': 'active'}]):
        raise Gate('Uninitialized continuation database dependency identities differ')
    _resource_tags(rds, group['DBSubnetGroupArn'])
    parameters = _one(rds.describe_db_cluster_parameter_groups(
        DBClusterParameterGroupName=physical['DatabaseParameters']), 'DBClusterParameterGroups')
    if (parameters.get('DBClusterParameterGroupName') != physical['DatabaseParameters']
            or parameters.get('DBParameterGroupFamily') != 'aurora-postgresql16'
            or parameters.get('Description') != 'Verified PostgreSQL TLS required'):
        raise Gate('Uninitialized continuation parameter group identity differs')
    _resource_tags(rds, parameters['DBClusterParameterGroupArn'])
    values = [row for page in _pages(rds, 'describe_db_cluster_parameters',
        DBClusterParameterGroupName=physical['DatabaseParameters'], Source='user') for row in page.get('Parameters', [])]
    if {row.get('ParameterName'): row.get('ParameterValue') for row in values} != {'rds.force_ssl': '1'} or len(values) != 1:
        raise Gate('Uninitialized continuation database TLS parameters differ')
    vpc = _one(ec2.describe_vpcs(VpcIds=[physical['Network']]), 'Vpcs')
    subnet = _one(ec2.describe_subnets(SubnetIds=[physical['PrivateA']]), 'Subnets')
    if (vpc.get('VpcId') != physical['Network'] or vpc.get('State') != 'available'
            or vpc.get('IsDefault') is not False or vpc.get('CidrBlock') != '10.76.0.0/16'
            or subnet.get('SubnetId') != physical['PrivateA'] or subnet.get('VpcId') != physical['Network']
            or subnet.get('State') != 'available' or subnet.get('CidrBlock') != '10.76.0.0/24'
            or subnet.get('MapPublicIpOnLaunch') is not False or subnet.get('AssignIpv6AddressOnCreation') is not True):
        raise Gate('Uninitialized continuation retained network configuration differs')
    _require_tags(vpc.get('Tags', []))
    _require_tags(subnet.get('Tags', []))
    for attribute in ('enableDnsSupport', 'enableDnsHostnames'):
        response = ec2.describe_vpc_attribute(VpcId=physical['Network'], Attribute=attribute)
        name = attribute[0].upper() + attribute[1:]
        if response.get('VpcId') != physical['Network'] or response.get(name, {}).get('Value') is not True:
            raise Gate('Uninitialized continuation retained VPC DNS differs')
    ipv6 = vpc.get('Ipv6CidrBlockAssociationSet', [])
    if (len(ipv6) != 1 or ipv6[0].get('AssociationId') != physical['NetworkIpv6']
            or ipv6[0].get('Ipv6CidrBlockState', {}).get('State') != 'associated'
            or ipv6[0].get('Ipv6Pool') != 'Amazon' or ipv6[0].get('NetworkBorderGroup') != config['region']):
        raise Gate('Uninitialized continuation retained IPv6 association differs')
    try:
        network = ipaddress.IPv6Network(ipv6[0]['Ipv6CidrBlock'])
        expected_subnet = str(next(network.subnets(new_prefix=64)))
    except (KeyError, ValueError):
        raise Gate('Uninitialized continuation retained IPv6 range differs') from None
    associations = subnet.get('Ipv6CidrBlockAssociationSet', [])
    if (network.prefixlen != 56 or len(associations) != 1
            or associations[0].get('Ipv6CidrBlock') != expected_subnet
            or associations[0].get('Ipv6CidrBlockState', {}).get('State') != 'associated'):
        raise Gate('Uninitialized continuation retained subnet IPv6 range differs')
    _absent(ec2, 'describe_subnets', {'InvalidSubnetID.NotFound'}, SubnetIds=[deleted_subnet])
    groups = ec2.describe_security_groups(GroupIds=[physical['DatabaseSecurityGroup'], physical['LambdaSecurityGroup']]).get('SecurityGroups', [])
    if len(groups) != 2 or {row.get('GroupId') for row in groups} != {physical['DatabaseSecurityGroup'], physical['LambdaSecurityGroup']}:
        raise Gate('Uninitialized continuation security group inventory differs')
    https = {('tcp', 443, 443, 'IpRanges', '0.0.0.0/0'), ('tcp', 443, 443, 'Ipv6Ranges', '::/0')}
    private_db = ('tcp', 5432, 5432, 'UserIdGroupPairs', physical['DatabaseSecurityGroup'])
    for row in groups:
        if row.get('VpcId') != physical['Network'] or row.get('OwnerId') != config['account']:
            raise Gate('Uninitialized continuation security group ownership differs')
        _require_tags(row.get('Tags', []))
        ingress, egress = _security_rules(row.get('IpPermissions', [])), _security_rules(row.get('IpPermissionsEgress', []))
        if row['GroupId'] == physical['DatabaseSecurityGroup']:
            valid = (ingress == {('tcp', 5432, 5432, 'UserIdGroupPairs', physical['LambdaSecurityGroup'])}
                     and egress == {('tcp', 5432, 5432, 'IpRanges', '127.0.0.1/32')})
        else:
            valid = not ingress and egress in (https, https | {private_db})
        if not valid:
            raise Gate('Uninitialized continuation security group grants differ')
    return {'cluster_resource_id': cluster['DbClusterResourceId'], 'writer_resource_id': writer['DbiResourceId'],
        'cluster_created_at': _utc_time(cluster['ClusterCreateTime']).isoformat(),
        'writer_created_at': _utc_time(writer['InstanceCreateTime']).isoformat(),
        'engine_version': cluster['EngineVersion'], 'master_secret_arn': secret['SecretArn'],
        'subnet_ids': sorted(subnet_ids), 'vpc_ipv6_range': str(network),
        'subnet_availability_zone': subnet['AvailabilityZone']}


def _continuation_imports(cf, template, physical):
    summaries = cf.get_template_summary(TemplateBody=json.dumps(template, separators=(',', ':'))).get('ResourceIdentifierSummaries', [])
    found = {}
    for row in summaries:
        for logical in row.get('LogicalResourceIds', []):
            if logical not in template['Resources']:
                raise Gate('Uninitialized continuation import summary includes an unknown resource')
            if logical not in DATABASE_IMPORT_IDS:
                continue
            kind, properties = DATABASE_IMPORT_IDS[logical]
            # CloudFormation reports composite alternatives as comma-separated
            # property names. AWS CDK's importer splits these into map keys.
            keys = row.get('ResourceIdentifiers', [])
            if (logical in found or row.get('ResourceType') != kind or len(keys) != 1
                    or not isinstance(keys[0], str) or tuple(keys[0].split(',')) != properties):
                raise Gate('Uninitialized continuation import identifiers differ from the reviewed schema')
            found[logical] = {'LogicalResourceId': logical, 'ResourceType': kind,
                'ResourceIdentifier': {key: physical['Network'] if logical == 'NetworkIpv6' and key == 'VpcId'
                                       else physical[logical] for key in properties}}
    if found.keys() != DATABASE_IMPORT_IDS.keys():
        raise Gate('CloudFormation did not identify every surviving database dependency for import')
    return [found[name] for name in sorted(found)]


def _failed_images(aws, config, revision):
    client = aws.client('ecr')
    uri = f"{config['account']}.dkr.ecr.{config['region']}.amazonaws.com/{STACK}"
    repository = _one(client.describe_repositories(repositoryNames=[STACK]), 'repositories')
    if (repository.get('repositoryUri') != uri or repository.get('repositoryName') != STACK
            or repository.get('registryId') != config['account'] or repository.get('imageTagMutability') != 'IMMUTABLE'):
        raise Gate('Uninitialized continuation image repository identity differs')
    _require_tags(client.list_tags_for_resource(resourceArn=repository['repositoryArn']).get('tags', []))
    result = {}
    for role in ('api', 'worker'):
        tag = role + '-' + revision
        row = _one(client.describe_images(repositoryName=STACK, imageIds=[{'imageTag': tag}]), 'imageDetails')
        digest = row.get('imageDigest', '')
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', digest) or tag not in row.get('imageTags', []):
            raise Gate('Uninitialized continuation lacks the immutable failed-source image')
        response = client.batch_get_image(repositoryName=STACK, imageIds=[{'imageDigest': digest}])
        image = _one(response, 'images')
        raw = image.get('imageManifest', '')
        if response.get('failures') or not isinstance(raw, str) or len(raw.encode()) > 262144:
            raise Gate('Uninitialized continuation image manifest is ambiguous or excessive')
        manifest = strict_loads(raw)
        if (hashlib.sha256(raw.encode()).hexdigest() != digest.removeprefix('sha256:')
                or manifest.get('mediaType') not in ('application/vnd.docker.distribution.manifest.v2+json',
                                                    'application/vnd.oci.image.manifest.v1+json')
                or 'manifests' in manifest):
            raise Gate('Uninitialized continuation image digest or platform manifest differs')
        result[role + 'ImageUri'] = uri + '@' + digest
    return result


def uninitialized_continuation_plan(aws, config, source_bundle, source_bundle_sha256):
    """Prove a specific failed first stopped deployment without mutating AWS."""
    bundle, original, adoption = _continuation_bundle(source_bundle, source_bundle_sha256, config)
    builder = _historical_builder(bundle['failed_release_id'])
    # Historical main source preserves the exact full old template admission;
    # current queue/retention fixes must not be mistaken for historic drift.
    old = _verify_source_manifest(aws, config, original, template_builder=builder, require_database_absent=False)
    cf = aws.client('cloudformation')
    stack = _one(cf.describe_stacks(StackName=STACK), 'Stacks')
    tags = {row['Key']: row['Value'] for row in stack.get('Tags', [])}
    if (stack.get('StackId') != adoption['recovered_stack_id']
            or stack.get('StackStatus') not in ('UPDATE_ROLLBACK_COMPLETE', 'IMPORT_COMPLETE')
            or stack.get('EnableTerminationProtection') is not True
            or (tags and (tags.get('deployment') != STACK or tags.get('purpose') != 'serverless-development'))):
        raise Gate('Uninitialized continuation requires the exact stable protected failed application stack')
    rows = [row for page in _pages(cf, 'list_stack_resources', StackName=stack['StackId'])
            for row in page.get('StackResourceSummaries', [])]
    imported = stack['StackStatus'] == 'IMPORT_COMPLETE'
    original_ids = old['retained_physical_ids'].keys()
    allowed_ids = original_ids | (DATABASE_IMPORT_IDS.keys() if imported
                  else DATABASE_IMPORT_IDS.keys() - {'DatabaseWriter'})
    actual_ids = {row.get('LogicalResourceId') for row in rows}
    statuses = ('IMPORT_COMPLETE', 'UPDATE_COMPLETE') if imported else ('CREATE_COMPLETE', 'UPDATE_COMPLETE')
    if (len(rows) != len(actual_ids) or not original_ids <= actual_ids or not actual_ids <= allowed_ids
            or (imported and actual_ids != allowed_ids)
            or any(row.get('ResourceStatus') not in statuses for row in rows)):
        raise Gate('Uninitialized continuation surviving inventory differs from the exact reviewed graph')
    bindings = {row['LogicalResourceId']: row.get('PhysicalResourceId') for row in rows}
    for row in rows:
        logical = row['LogicalResourceId']
        kind = old['import_template']['Resources'][logical]['Type'] if logical in old['retained_physical_ids'] else DATABASE_IMPORT_IDS[logical][0]
        if (row.get('ResourceType') != kind or not isinstance(bindings[logical], str) or not bindings[logical]
                or (logical in original_ids and bindings[logical] != old['retained_physical_ids'][logical])):
            raise Gate('Uninitialized continuation changed a surviving resource type or physical identity')
    images = _failed_images(aws, config, bundle['failed_release_id'])
    cluster_preview = _one(aws.client('rds').describe_db_clusters(DBClusterIdentifier=STACK), 'DBClusters')
    historical_config = _historical_template_config(config,
        _template_body(cf, old['original_stack_id'])['Resources'])
    # The authenticated historical workflow/stage prefix proves stopped-mode
    # construction from its admitted source. Current budget/runtime settings do
    # not retroactively change that historical template.
    failed_template = builder({**historical_config, **images, 'releaseId': bundle['failed_release_id'],
        'databaseEngineVersion': cluster_preview.get('EngineVersion'), 'activateServices': False})
    source_physical, deleted_subnet = _history_for_continuation(cf, bundle, stack['StackId'], failed_template)
    physical = {**old['retained_physical_ids'], **source_physical}
    managed_import_bindings = {logical: bindings[logical] for logical in sorted(actual_ids - original_ids)}
    if any(physical[logical] != bindings[logical] for logical in actual_ids):
        raise Gate('Uninitialized continuation current bindings differ from their exact source creation identities')
    if not imported:
        for logical in sorted(DATABASE_IMPORT_IDS.keys() - actual_ids):
            _absent_stack_binding(cf, stack['StackId'], logical)
    snapshot = _database_snapshot(aws, config, bundle, physical, deleted_subnet)
    if snapshot['engine_version'] != cluster_preview.get('EngineVersion'):
        raise Gate('Uninitialized continuation database version changed during inventory')
    candidate = deepcopy(old['import_template'])
    for logical, (kind, _) in DATABASE_IMPORT_IDS.items():
        resource = deepcopy(failed_template['Resources'][logical])
        if resource['Type'] != kind:
            raise Gate('Uninitialized continuation historical resource graph differs')
        resource.update(DeletionPolicy='Retain', UpdateReplacePolicy='Retain')
        if logical == 'DatabaseSubnets':
            resource['Properties']['SubnetIds'] = [physical['PrivateA'], deleted_subnet]
        candidate['Resources'][logical] = resource
    if any(_references(resource) - candidate['Resources'].keys() for resource in candidate['Resources'].values()):
        raise Gate('Uninitialized continuation import graph has an unresolved dependency')
    body = json.dumps(candidate, separators=(',', ':'))
    if len(body.encode()) > 51200:
        raise Gate('Uninitialized continuation candidate exceeds the direct template limit')
    actual = _template_body(cf, stack['StackId'])
    if _body_hash(actual) != _body_hash(candidate if imported else old['import_template']):
        raise Gate('Uninitialized continuation current stack template differs from the exact admitted phase')
    requests = _continuation_imports(cf, candidate, physical)
    return {'schema_version': '1.0.0', 'operation': 'serverless-uninitialized-continuation',
        'status': 'validated', 'account': config['account'], 'region': config['region'],
        'release_id': config['releaseId'], 'failed_release_id': bundle['failed_release_id'],
        'failed_run_id': bundle['failed_run_id'], 'failed_run_attempt': bundle['failed_run_attempt'],
        'artifact_sha256': bundle['artifact_sha256'], 'source_bundle_sha256': source_bundle_sha256,
        'stack_name': STACK, 'stack_id': stack['StackId'], 'original_stack_id': old['original_stack_id'],
        'original_retained_physical_ids': old['retained_physical_ids'], 'retained_physical_ids': physical,
        'managed_import_bindings': managed_import_bindings,
        'deleted_subnet_id': deleted_subnet, 'database_snapshot': snapshot,
        'database_engine_version': snapshot['engine_version'], 'already_adopted': imported,
        'import_template': candidate, 'canonical_import_template_sha256': _body_hash(candidate),
        'resources_to_import': requests, 'actual_resources_deleted': False,
        'journal_established': False, 'application_deployment_completed': False}


def _same_continuation(before, after, *, check_bindings=False):
    for field in ('stack_id', 'retained_physical_ids', 'database_snapshot', 'canonical_import_template_sha256'):
        if before[field] != after[field]:
            raise Gate('Uninitialized continuation authority or configuration changed before execution')
    if check_bindings and before['managed_import_bindings'] != after['managed_import_bindings']:
        raise Gate('Uninitialized continuation resource bindings changed before execution')


def continue_uninitialized(aws, config, evidence_path, source_bundle, source_bundle_sha256):
    """Adopt exact survivors, without deleting resources or creating an anchor."""
    path = Path(evidence_path)
    if path.exists() or path.is_symlink() or not path.parent.is_dir():
        raise Gate('Uninitialized continuation requires a new protected phase journal')
    evidence = uninitialized_continuation_plan(aws, config, source_bundle, source_bundle_sha256)
    _write(path, evidence)

    def phase(status):
        evidence['status'] = status
        _write(path, evidence)

    try:
        if not evidence['already_adopted']:
            cf = aws.client('cloudformation')
            phase('surviving-database-import-requesting')
            change = cf.create_change_set(StackName=evidence['stack_id'],
                ChangeSetName='uninitialized-import-' + uuid.uuid4().hex, ChangeSetType='IMPORT',
                TemplateBody=json.dumps(evidence['import_template'], separators=(',', ':')),
                ResourcesToImport=evidence['resources_to_import'])['Id']
            evidence['import_change_set_id'] = change
            phase('surviving-database-import-created')
            cf.get_waiter('change_set_create_complete').wait(StackName=evidence['stack_id'], ChangeSetName=change,
                WaiterConfig={'Delay': 3, 'MaxAttempts': 120})
            changes = [row.get('ResourceChange', {}) for page in _pages(cf, 'describe_change_set',
                StackName=evidence['stack_id'], ChangeSetName=change) for row in page.get('Changes', [])]
            expected = DATABASE_IMPORT_IDS.keys()
            if (len(changes) != len(expected) or {row.get('LogicalResourceId') for row in changes} != expected
                    or any(row.get('Action') != 'Import'
                           or row.get('ResourceType') != DATABASE_IMPORT_IDS[row['LogicalResourceId']][0]
                           or row.get('Replacement') in ('True', 'Conditional')
                           or (row.get('PhysicalResourceId') and row['PhysicalResourceId']
                               != evidence['retained_physical_ids'][row['LogicalResourceId']]) for row in changes)):
                raise Gate('Uninitialized continuation change set is not exactly nine preserved-resource imports')
            _same_continuation(evidence, uninitialized_continuation_plan(
                aws, config, source_bundle, source_bundle_sha256), check_bindings=True)
            phase('surviving-database-import-executing')
            cf.execute_change_set(StackName=evidence['stack_id'], ChangeSetName=change)
            cf.get_waiter('stack_import_complete').wait(StackName=evidence['stack_id'],
                WaiterConfig={'Delay': 5, 'MaxAttempts': 180})
        after = uninitialized_continuation_plan(aws, config, source_bundle, source_bundle_sha256)
        _same_continuation(evidence, after)
        if not after['already_adopted']:
            raise Gate('Uninitialized continuation did not prove complete survivor adoption')
        evidence['already_adopted'] = True
        evidence['managed_import_bindings'] = after['managed_import_bindings']
        phase('retained-uninitialized-database-adopted')
        return evidence
    except Exception as error:
        _record_failure(evidence, phase, error)
        raise


def verify_continued_database(aws, config, outputs, evidence):
    """After stopped deployment, prove that no survivor or database was replaced."""
    cf = aws.client('cloudformation')
    stack = _one(cf.describe_stacks(StackName=STACK), 'Stacks')
    rows = [row for page in _pages(cf, 'list_stack_resources', StackName=stack['StackId'])
            for row in page.get('StackResourceSummaries', [])]
    actual = {row['LogicalResourceId']: row.get('PhysicalResourceId') for row in rows}
    if (stack.get('StackId') != evidence['stack_id'] or stack.get('StackStatus') != 'UPDATE_COMPLETE'
            or stack.get('EnableTerminationProtection') is not True or len(actual) != len(rows)
            or any(actual.get(logical) != physical for logical, physical in evidence['retained_physical_ids'].items())
            or any(row.get('ResourceType') != evidence['import_template']['Resources'][row['LogicalResourceId']]['Type']
                   or row.get('ResourceStatus') not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE', 'IMPORT_COMPLETE')
                   for row in rows if row['LogicalResourceId'] in evidence['retained_physical_ids'])
            or outputs.get('ReleaseId') != config['releaseId'] or outputs.get('ActivateServices') != 'false'):
        raise Gate('Stopped continuation replaced a survivor or differs from the selected source')
    cluster = _one(aws.client('rds').describe_db_clusters(DBClusterIdentifier=STACK), 'DBClusters')
    writer = _one(aws.client('rds').describe_db_instances(DBInstanceIdentifier=STACK + '-writer'), 'DBInstances')
    prior = evidence['database_snapshot']
    physical = evidence['retained_physical_ids']
    key_arn = f"arn:aws:kms:{config['region']}:{config['account']}:key/{physical['DataKey']}"
    if (cluster.get('DbClusterResourceId') != prior['cluster_resource_id']
            or writer.get('DbiResourceId') != prior['writer_resource_id']
            or _utc_time(cluster.get('ClusterCreateTime')).isoformat() != prior['cluster_created_at']
            or _utc_time(writer.get('InstanceCreateTime')).isoformat() != prior['writer_created_at']
            or cluster.get('MasterUserSecret', {}).get('SecretArn') != prior['master_secret_arn']
            or cluster.get('MasterUserSecret', {}).get('SecretStatus') != 'active'
            or cluster.get('EngineVersion') != prior['engine_version'] or writer.get('EngineVersion') != prior['engine_version']
            or cluster.get('Status') != 'available' or writer.get('DBInstanceStatus') != 'available'
            or cluster.get('PendingModifiedValues', {}) or writer.get('PendingModifiedValues', {})
            or cluster.get('DeletionProtection') is not True or cluster.get('BackupRetentionPeriod') != 7
            or cluster.get('StorageEncrypted') is not True or writer.get('StorageEncrypted') is not True
            or cluster.get('KmsKeyId') != key_arn or writer.get('KmsKeyId') != key_arn
            or writer.get('PubliclyAccessible') is not False or writer.get('DBClusterIdentifier') != physical['Database']
            or cluster.get('DBClusterParameterGroup') != physical['DatabaseParameters']
            or cluster.get('DBSubnetGroup') != physical['DatabaseSubnets']
            or writer.get('DBSubnetGroup', {}).get('DBSubnetGroupName') != physical['DatabaseSubnets']
            or writer.get('DBSubnetGroup', {}).get('VpcId') != physical['Network']):
        raise Gate('Stopped continuation changed the retained database authority')
    return {'retained_database_identity_verified': True, 'first_anchor_still_requires_empty_sql': True}


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
