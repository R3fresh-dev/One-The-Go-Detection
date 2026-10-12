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
import uuid
from zipfile import BadZipFile, ZipFile

from botocore.exceptions import ClientError
import httpx

from deploy.provenance import Gate, REPOSITORY, _github_json, bounded_file, strict_loads
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


def initial_recovery_plan(aws, config, *, _detached_stack_id=None):
    """Validate the complete recovery before any mutation and retain no secrets."""
    if (config.get('environment') != 'serverless-development' or config.get('region') != 'us-east-2'
            or not re.fullmatch(r'\d{12}', config.get('account', ''))
            or not re.fullmatch(r'[0-9a-f]{40}', config.get('releaseId', ''))):
        raise Gate('Initial recovery requires the explicit reviewed serverless target')
    if aws.client('sts').get_caller_identity()['Account'] != config['account']:
        raise Gate('Initial recovery credentials do not match the selected account')
    cf = aws.client('cloudformation')
    stack = cf.describe_stacks(StackName=_detached_stack_id or STACK)['Stacks'][0]
    stack_tags = {tag['Key']: tag['Value'] for tag in stack.get('Tags', [])}
    expected_status = 'DELETE_COMPLETE' if _detached_stack_id else 'ROLLBACK_COMPLETE'
    if (stack.get('StackStatus') != expected_status
            or stack_tags.get('deployment') != STACK or stack_tags.get('purpose') != 'serverless-development'
            or not stack.get('StackId', '').startswith(f"arn:aws:cloudformation:{config['region']}:{config['account']}:stack/{STACK}/")):
        raise Gate('Only the owned failed first application stack can use initial recovery')
    if _detached_stack_id and stack['StackId'] != _detached_stack_id:
        raise Gate('Detached recovery history belongs to a different stack identity')
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
    legacy_body = json.dumps(template, separators=(',', ':'))
    body = json.dumps(template, separators=(',', ':'), sort_keys=True)
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
            'import_template_hash_encoding': 'canonical-json',
            'legacy_import_template_sha256': hashlib.sha256(legacy_body.encode()).hexdigest(),
            'resources_to_import': [{'LogicalResourceId': logical, 'ResourceType': imported[logical]['Type'],
                'ResourceIdentifier': {identifiers[logical]: physical_ids[logical]}} for logical in sorted(imported)],
            'initial_state': {'database_absent': True, 'application_functions_absent': True,
                              'retained_buckets_empty': True, 'control_table_empty': True, 'user_pool_empty': True,
                              'initial_creation_history_verified': True, 'stack_event_count': len(events)},
            'actual_resources_deleted': False, 'application_deployment_completed': False}


def _import_retained(aws, config, evidence, path):
    """Adopt a validated manifest; import cannot specify stack-level Tags."""
    cf = aws.client('cloudformation')

    def phase(status):
        evidence['status'] = status
        _write(path, evidence)

    try:
        # Re-read authority and emptiness after detachment, before adoption.
        for logical, resource in evidence['import_template']['Resources'].items():
            _verify_retained(aws, config, logical, resource, evidence['retained_physical_ids'][logical])
        change = cf.create_change_set(StackName=STACK, ChangeSetName='initial-import-' + uuid.uuid4().hex,
            ChangeSetType='IMPORT', TemplateBody=json.dumps(evidence['import_template'], separators=(',', ':'), sort_keys=True),
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
                       for row in changes)):
            cf.delete_change_set(StackName=STACK, ChangeSetName=change)
            raise Gate('Initial recovery change set is not an import of the exact preserved resources')
        cf.update_termination_protection(StackName=STACK, EnableTerminationProtection=True)
        phase('import-executing')
        cf.execute_change_set(StackName=STACK, ChangeSetName=change)
        cf.get_waiter('stack_import_complete').wait(StackName=STACK,
            WaiterConfig={'Delay': 5, 'MaxAttempts': 180})
        stack = cf.describe_stacks(StackName=STACK)['Stacks'][0]
        rows = [row for page in _pages(cf, 'list_stack_resources', StackName=STACK)
                for row in page.get('StackResourceSummaries', [])]
        if (stack.get('StackStatus') != 'IMPORT_COMPLETE' or not stack.get('EnableTerminationProtection')
                or len(rows) != len(resources) or {row['LogicalResourceId']: row.get('PhysicalResourceId') for row in rows}
                    != evidence['retained_physical_ids']):
            raise Gate('Initial recovery did not prove adoption of every original retained resource')
        evidence['recovered_stack_id'] = stack['StackId']
        phase('uninitialized-retained-resources-imported')
        return evidence
    except Exception as error:
        evidence['failed_phase'] = evidence['status']
        evidence['failure_type'] = type(error).__name__
        phase('blocked-recovery-inspect-protected-journal-before-retry')
        raise


def recover_initial(aws, config, evidence_path):
    """Detach failed stack metadata, then adopt the identical retained resources."""
    path = Path(evidence_path)
    if path.exists() or not path.parent.is_dir():
        raise Gate('Use a new protected initial recovery journal in an existing deployment work directory')
    evidence = initial_recovery_plan(aws, config)
    _write(path, evidence)
    cf = aws.client('cloudformation')
    try:
        evidence['status'] = 'detaching-failed-stack-metadata'
        _write(path, evidence)
        cf.update_termination_protection(StackName=evidence['original_stack_id'], EnableTerminationProtection=False)
        cf.delete_stack(StackName=evidence['original_stack_id'])
        cf.get_waiter('stack_delete_complete').wait(StackName=evidence['original_stack_id'],
            WaiterConfig={'Delay': 5, 'MaxAttempts': 120})
        evidence['status'] = 'failed-stack-metadata-detached'
        _write(path, evidence)
    except Exception as error:
        evidence.update(failed_phase=evidence['status'], failure_type=type(error).__name__,
                        status='blocked-recovery-inspect-protected-journal-before-retry')
        _write(path, evidence)
        raise
    return _import_retained(aws, config, evidence, path)


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


def resume_initial(aws, config, manifest_path, evidence_path, *, artifact_proof):
    """Import preserved initial resources from a trusted interrupted-run manifest.

    The caller must first admit its current exact reviewed source. This helper
    independently verifies the failed deployment artifact and revalidates the
    deleted stack's original template, full creation history and live resources.
    It accepts only an absent current stack; no stack metadata is deleted again.
    Deleted-stack history must still be available from CloudFormation (90 days).
    """
    path = Path(evidence_path)
    if path.exists() or not path.parent.is_dir():
        raise Gate('Use a new protected initial recovery journal in an existing deployment work directory')
    proof = verify_recovery_artifact(manifest_path, artifact_proof)
    manifest_raw = bounded_file(manifest_path, 262144)
    if hashlib.sha256(manifest_raw).hexdigest() != proof['manifest_sha256']:
        raise Gate('Trusted recovery manifest changed after artifact verification')
    try:
        manifest = strict_loads(manifest_raw)
    except (ValueError, TypeError):
        raise Gate('Recovery manifest is not strict JSON') from None
    if not isinstance(manifest, dict):
        raise Gate('Recovery manifest must be an object')
    if (manifest.get('schema_version') != '1.0.0' or manifest.get('operation') != 'serverless-initial-recovery'
            or manifest.get('status') != 'blocked-recovery-inspect-protected-journal-before-retry'
            or manifest.get('failed_phase') != 'failed-stack-metadata-detached'
            or manifest.get('account') != config.get('account') or manifest.get('region') != config.get('region')
            or manifest.get('stack_name') != STACK or manifest.get('actual_resources_deleted') is not False
            or manifest.get('application_deployment_completed') is not False
            or 'import_change_set_id' in manifest or 'recovered_stack_id' in manifest):
        raise Gate('Resume accepts only the trusted uninitialized post-detachment failure manifest')
    old_stack_id = manifest.get('original_stack_id', '')
    if not isinstance(old_stack_id, str) or not old_stack_id.startswith(
            f"arn:aws:cloudformation:{config.get('region')}:{config.get('account')}:stack/{STACK}/"):
        raise Gate('Recovery manifest does not identify the original owned stack')
    if aws.client('sts').get_caller_identity()['Account'] != config['account']:
        raise Gate('Initial recovery credentials do not match the selected account')
    cf = aws.client('cloudformation')
    try:
        cf.describe_stacks(StackName=STACK)
    except ClientError as error:
        info = error.response.get('Error', {})
        if info.get('Code') != 'ValidationError' or 'does not exist' not in info.get('Message', ''):
            raise
    else:
        raise Gate('Initial recovery resume requires an absent current application stack')
    # Reconstruct rather than trust the saved template, ownership, identifiers,
    # empty-state assertions or legacy order-sensitive hash.
    evidence = initial_recovery_plan(aws, config, _detached_stack_id=old_stack_id)
    for key in ('original_release_id', 'original_stack_id', 'import_template',
                'retained_physical_ids', 'resources_to_import'):
        if manifest.get(key) != evidence[key]:
            raise Gate('Recovery manifest differs from the original reviewed retained resources')
    hash_encoding = manifest.get('import_template_hash_encoding')
    expected_hash = evidence['import_template_sha256'] if hash_encoding == 'canonical-json' else evidence['legacy_import_template_sha256']
    if hash_encoding not in (None, 'canonical-json') or manifest.get('import_template_sha256') != expected_hash:
        raise Gate('Recovery manifest import template hash cannot be verified')
    empty = manifest.get('initial_state', {})
    if not isinstance(empty, dict) or any(empty.get(key) is not True for key in (
            'database_absent', 'application_functions_absent', 'retained_buckets_empty',
            'control_table_empty', 'user_pool_empty', 'initial_creation_history_verified')):
        raise Gate('Trusted recovery manifest does not establish the required empty initial state')
    evidence.update(status='failed-stack-metadata-detached', operation='serverless-initial-recovery-resume',
                    resumed_from=proof, resumed_from_release_id=manifest['release_id'])
    _write(path, evidence)
    return _import_retained(aws, config, evidence, path)
