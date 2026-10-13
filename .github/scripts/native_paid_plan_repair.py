"""Reviewed operations-only desired PAID repair. Never retries a native mutation.

The fsynced local intent must be published as a protected GitHub artifact BEFORE
the execute phase. Workflow/history admission prevents another runner consuming
a fresh intent. Missing plan records are not guaranteed repairable by AWS.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import stat
import subprocess
import sys
import zipfile

ACCOUNT = '738470137867'
CREATED = datetime.fromisoformat('2026-10-12T04:19:39.889000+00:00')
SOURCE = '0844868aa543af4ab75ac5065ad48cf807b86bb3'
TREE = '1afe65b4d2a6ba3a4c541c9ecf7bc61f287ee908'
REPOSITORY = 'R3fresh-dev/One-The-Go-Detection'
BRANCH = 'work-aws-regional-diagnostic'
WORKFLOW = '.github/workflows/aws-serverless-observer.yml'
INTENT_PREFIX = 'paid-plan-request-intent-' + ACCOUNT + '-'
SOURCE_ADMISSION_SHA = '4fd6338af3972342e682ce9fb77439b33f7c6087b857d04aecd6f48efe75074c'
GLOBAL_ENDPOINT = 'https://freetier.us-east-1.api.aws'
GATE = {'source_revision': SOURCE, 'source_tree': TREE, 'gate_run_id': 38350430258,
        'gate_attempt': 1, 'gate_artifact_id': 11790454913, 'raw_aggregate_bytes': 393,
        'raw_aggregate_sha256': '9338903893d1bb1d82097cca4ea7a59cd81579d1f85cb853310c981592a2d165'}


class Blocked(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise Blocked(reason)


def strict_json(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'Duplicate JSON keys')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(Blocked('Nonfinite JSON')))


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def utc():
    return datetime.now(timezone.utc).isoformat()


def timestamp(value):
    require(isinstance(value, str), 'Timestamp must be an aware ISO string')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.tzinfo is not None, 'Timestamp must include timezone')
    return parsed.astimezone(timezone.utc)


def secure_directory(path):
    metadata = path.lstat()
    require(stat.S_ISDIR(metadata.st_mode) and metadata.st_uid == os.getuid()
            and not metadata.st_mode & 0o077, 'Private owned directory required')


def private_file(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                and before.st_uid == os.getuid() and not before.st_mode & 0o077
                and before.st_size <= 16384, 'Private bounded regular file required')
        raw = os.read(descriptor, 16385)
        after, named = os.fstat(descriptor), path.lstat()
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns,
                                  value.st_ctime_ns, value.st_mode, value.st_uid, value.st_nlink)
        require(identity(before) == identity(after) == identity(named)
                and len(raw) == before.st_size, 'File changed during read')
        return raw
    finally:
        os.close(descriptor)


def write_once(path, value):
    raw = encoded(value)
    require(len(raw) <= 16384, 'Intent/receipt exceeds bound')
    # O_EXCL remains spent after a partial write, fsync failure or crash. Never unlink.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(descriptor)
    finally:
        os.close(descriptor)
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


def command(args, *, binary=False):
    result = subprocess.run(args, capture_output=True, text=not binary, timeout=30)
    require(result.returncode == 0, 'Authenticated bounded command unavailable')
    raw = result.stdout if binary else result.stdout.encode()
    require(len(raw) <= 1048576, 'Command response exceeds bound')
    return result.stdout


def api(path):
    value = strict_json(command(['gh', 'api', f'repos/{REPOSITORY}/{path}'.rstrip('/')]))
    require(isinstance(value, dict), 'GitHub response must be an object')
    return value


def environment():
    commit = os.environ.get('REVIEWED_OPERATIONAL_COMMIT', '')
    require(re.fullmatch(r'[0-9a-f]{40}', commit) and os.environ.get('GITHUB_SHA') == commit,
            'Reviewed operational commit differs')
    run = os.environ.get('GITHUB_RUN_ID', '')
    require(re.fullmatch(r'[1-9][0-9]*', run) and os.environ.get('GITHUB_RUN_ATTEMPT') == '1',
            'Only the original reviewed run attempt is allowed')
    require(os.environ.get('GH_REPO') == REPOSITORY
            and os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
            and os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH,
            'Reviewed repository/dispatch branch differs')
    return {'operational_commit': commit, 'run_id': int(run), 'run_attempt': 1}


def operation_admission(binding, *, published=False):
    run = api(f"actions/runs/{binding['run_id']}")
    require(run.get('id') == binding['run_id'] and run.get('run_attempt') == 1
            and run.get('path') == WORKFLOW and run.get('head_sha') == binding['operational_commit']
            and run.get('head_branch') == BRANCH and run.get('event') == 'workflow_dispatch'
            and run.get('status') == 'in_progress'
            and run.get('repository', {}).get('full_name') == REPOSITORY
            and run.get('head_repository', {}).get('full_name') == REPOSITORY,
            'Live reviewed repair run differs')
    workflow = api(f"actions/workflows/{run['workflow_id']}")
    require(workflow.get('path') == WORKFLOW and workflow.get('state') == 'active',
            'Repair workflow differs')
    history = api(f"actions/workflows/{run['workflow_id']}/runs?per_page=100&page=1")
    rows = history.get('workflow_runs', [])
    history_total = history.get('total_count', 1001)
    require(type(history_total) is int and 0 <= history_total <= 1000,
            'Registered observer history exceeds reviewed bound')
    for page in range(2, (history_total + 99) // 100 + 1):
        part = api(f"actions/workflows/{run['workflow_id']}/runs?per_page=100&page={page}")
        require(part.get('total_count') == history_total, 'Observer run history changed during scan')
        rows.extend(part.get('workflow_runs', []))
    require(len(rows) == history_total and len({row.get('id') for row in rows}) == history_total,
            'Observer run history is incomplete or changed')
    # Earlier read-only observer runs use other reviewed operational commits.
    # A second run of THIS repair commit, including failed/cancelled preparation,
    # consumes this one authorized dispatch. Never delete history to bypass it.
    repair_runs = [row for row in rows if row.get('head_sha') == binding['operational_commit']
                   and row.get('head_branch') == BRANCH and row.get('path') == WORKFLOW
                   and row.get('event') == 'workflow_dispatch']
    require(len(repair_runs) == 1 and repair_runs[0].get('id') == binding['run_id']
            and repair_runs[0].get('run_attempt') == 1,
            'Prior repair-commit run: read-only verification only')
    inventory = api('actions/artifacts?per_page=100&page=1')
    total = inventory.get('total_count', 1001)
    require(type(total) is int and 0 <= total <= 1000, 'Repository artifact history exceeds reviewed bound')
    artifacts = list(inventory.get('artifacts', []))
    for page in range(2, (total + 99) // 100 + 1):
        part = api(f'actions/artifacts?per_page=100&page={page}')
        require(part.get('total_count') == total, 'Repository artifact inventory changed during scan')
        artifacts.extend(part.get('artifacts', []))
    require(len(artifacts) == total and len({row.get('id') for row in artifacts}) == total,
            'Repository artifact inventory is incomplete or changed')
    prior = [row for row in artifacts
             if str(row.get('name', '')).startswith(INTENT_PREFIX)]
    expected = INTENT_PREFIX + str(binding['run_id']) + '-1'
    require(len(prior) == (1 if published else 0)
            and (not published or prior[0].get('name') == expected),
            'Prior or ambiguous account request intent: read-only verification only')
    return prior[0] if published else None


def source_admission(path):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_ADMISSION_SHA,
            'Corrected source admission bytes differ')
    # Exact original diagnostic admission: fresh main/latest14/raw393 ZIP/source.
    runpy.run_path(str(path), run_name='__main__')


def live_binding(clients):
    require(clients['sts'].get_caller_identity().get('Account') == ACCOUNT, 'STS account differs')
    info = clients['account'].get_account_information()  # own account; no AccountId argument
    created = info.get('AccountCreatedDate')
    require(info.get('AccountId') == ACCOUNT and info.get('AccountState') == 'ACTIVE'
            and isinstance(created, datetime) and created.tzinfo is not None
            and created.astimezone(timezone.utc) == CREATED, 'Live account/state/creation differs')


def plan(clients):
    from botocore.exceptions import ClientError
    try:
        value = clients['freetier'].get_account_plan_state()
    except ClientError as error:
        details = error.response.get('Error', {})
        require(details.get('Code') == 'ResourceNotFoundException'
                and details.get('Message') == 'Missing data for account: ' + ACCOUNT
                and error.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 400,
                'Plan read failed outside the observed missing-record contract')
        return {'state': 'MISSING_RECORD', 'native_error_code': 'ResourceNotFoundException'}
    require(value.get('accountId') == ACCOUNT, 'Native plan account differs')
    if value.get('accountPlanType') == 'PAID' and value.get('accountPlanStatus') == 'ACTIVE':
        return {'state': 'PAID_ACTIVE'}
    require(value.get('accountPlanType') == 'FREE' and value.get('accountPlanStatus') == 'ACTIVE',
            'Unrecognized/non-active native plan state')
    return {'state': 'FREE_ACTIVE'}


def published_intent(binding, local):
    row = operation_admission(binding, published=True)
    require(row.get('expired') is False and row.get('workflow_run', {}).get('id') == binding['run_id']
            and row.get('workflow_run', {}).get('head_sha') == binding['operational_commit']
            and type(row.get('id')) is int and row['id'] > 0
            and type(row.get('size_in_bytes')) is int and 0 < row['size_in_bytes'] <= 16384
            and re.fullmatch(r'sha256:[0-9a-f]{64}', row.get('digest', '')),
            'Published intent artifact binding differs')
    jobs = api(f"actions/runs/{binding['run_id']}/attempts/1/jobs?per_page=100")
    require(jobs.get('total_count') == 1 and len(jobs.get('jobs', [])) == 1,
            'Repair job is ambiguous')
    job = jobs['jobs'][0]
    steps = [step for step in job.get('steps', []) if step.get('name') == 'Prepare exact account intent']
    require(job.get('run_id') == binding['run_id'] and job.get('run_attempt') == 1
            and job.get('head_sha') == binding['operational_commit'] and len(steps) == 1
            and steps[0].get('conclusion') == 'success'
            and timestamp(steps[0].get('started_at')) <= timestamp(steps[0].get('completed_at'))
            <= timestamp(row.get('created_at')) <= timestamp(utc()),
            'Intent is not bound to this successful preparation step')
    raw = command(['gh', 'api', f"repos/{REPOSITORY}/actions/artifacts/{row['id']}/zip"], binary=True)
    require(len(raw) == row['size_in_bytes']
            and hashlib.sha256(raw).hexdigest() == row['digest'].removeprefix('sha256:'),
            'Published raw intent ZIP digest differs')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = archive.infolist()
        require(len(members) == 1 and members[0].filename == 'intent.json'
                and not members[0].is_dir() and members[0].file_size <= 16384
                and ((members[0].external_attr >> 16) & 0o170000) in (0, stat.S_IFREG)
                and not members[0].flag_bits & 1 and archive.read(members[0]) == local,
                'Published intent bytes/member differ')
    after = api(f"actions/artifacts/{row['id']}")
    require(all(after.get(key) == row.get(key) for key in
                ('id', 'name', 'expired', 'digest', 'size_in_bytes', 'created_at', 'workflow_run')),
            'Published intent changed after download')
    operation_admission(binding, published=True)
    return {'artifact_id': row['id'], 'raw_zip_sha256': row['digest'].removeprefix('sha256:')}


def prepare(clients, directory, binding):
    secure_directory(directory)
    live_binding(clients)
    current = plan(clients)
    if current['state'] == 'PAID_ACTIVE':
        write_once(directory / 'receipt.json', {**GATE, **binding, 'account': ACCOUNT,
                   'account_created_at': CREATED.isoformat(), 'verified_at': utc(),
                   'native_paid_active_verified': True, 'upgrade_transport_attempts': 0})
        return False
    write_once(directory / 'intent.json', {**GATE, **binding, 'account': ACCOUNT,
               'account_created_at': CREATED.isoformat(), 'observed_plan': current,
               'operation': 'UpgradeAccountPlan', 'parameters': {'accountPlanType': 'PAID'},
               'max_transport_attempts': 1, 'created_at': utc()})
    return True


class SendGuard:
    def __init__(self, directory):
        self.directory, self.count = directory, 0

    def __call__(self, request, **unused):
        require(self.count == 0, 'Second Upgrade transport blocked')
        require(request.url in (GLOBAL_ENDPOINT, GLOBAL_ENDPOINT + '/')
                and request.method == 'POST'
                and strict_json(request.body) == {'accountPlanType': 'PAID'},
                'Native Upgrade endpoint/method/body differs')
        self.count += 1
        # Fsync BEFORE the transport boundary; a crash may consume the intent
        # without delivery, but cannot authorize a replacement request.
        write_once(self.directory / 'transport-started.json', {
            'account': ACCOUNT, 'operation': 'UpgradeAccountPlan',
            'accountPlanType': 'PAID', 'started_at': utc(), 'transport_attempt': 1})


def execute(clients, directory, binding, *, admit_source, admit_published):
    secure_directory(directory)
    raw = private_file(directory / 'intent.json')
    intent = strict_json(raw)
    require(all(intent.get(key) == value for key, value in {**GATE, **binding,
                'account': ACCOUNT, 'account_created_at': CREATED.isoformat(),
                'operation': 'UpgradeAccountPlan', 'parameters': {'accountPlanType': 'PAID'},
                'max_transport_attempts': 1}.items()), 'Exact intent binding differs')
    require(intent.get('observed_plan', {}).get('state') in ('MISSING_RECORD', 'FREE_ACTIVE'),
            'Intent initial plan state differs')
    require(not any((directory / name).exists() for name in
                    ('execution-started.json', 'transport-started.json', 'upgrade-outcome.json')),
            'Spent intent: read-only verification only')
    artifact = admit_published(binding, raw)
    admit_source()
    live_binding(clients)
    current = plan(clients)
    guard = SendGuard(directory)
    error = None
    if current['state'] != 'PAID_ACTIVE':
        write_once(directory / 'execution-started.json', {
            'account': ACCOUNT, 'operation': 'UpgradeAccountPlan', 'accountPlanType': 'PAID',
            'intent_sha256': hashlib.sha256(raw).hexdigest(), 'started_at': utc()})
        clients['freetier'].meta.events.register_first('before-send.freetier.UpgradeAccountPlan', guard)
        try:
            response = clients['freetier'].upgrade_account_plan(accountPlanType='PAID')
            require(guard.count == 1, 'Native SDK did not cross the single guarded transport')
            require(response.get('accountId') == ACCOUNT and response.get('accountPlanType') == 'PAID'
                    and response.get('accountPlanStatus') == 'ACTIVE', 'Native Upgrade response differs')
        except Exception as caught:
            # Preserve only class/code/status/request ID. Never print provider
            # messages, authentication headers, credentials or an environment.
            details = getattr(caught, 'response', None) or {}
            metadata = details.get('ResponseMetadata', {})
            error = {'exception_type': type(caught).__name__,
                     'native_error_code': details.get('Error', {}).get('Code'),
                     'http_status_code': metadata.get('HTTPStatusCode'),
                     'request_id': metadata.get('RequestId')}
            write_once(directory / 'upgrade-outcome.json', {'upgrade_response_verified': False,
                       'transport_attempts': guard.count, 'error': error, 'observed_at': utc()})
        else:
            write_once(directory / 'upgrade-outcome.json', {'upgrade_response_verified': True,
                       'transport_attempts': guard.count, 'observed_at': utc()})
    # A lost response can be resolved only by fresh read-only native verification.
    # No retry, no exception-to-PAID substitution, no automatic deployment dispatch.
    live_binding(clients)
    final = plan(clients)
    require(final['state'] == 'PAID_ACTIVE', 'Fresh same-account PAID/ACTIVE remains unverified; stop')
    require(error is None or error['exception_type'] != 'Blocked', 'Native Upgrade contract mismatch; stop')
    write_once(directory / 'receipt.json', {**GATE, **binding, 'account': ACCOUNT,
               'account_created_at': CREATED.isoformat(), 'intent_sha256': hashlib.sha256(raw).hexdigest(),
               'published_intent': artifact, 'native_paid_active_verified': True,
               'verified_at': utc(), 'upgrade_transport_attempts': guard.count,
               'upgrade_error_resolved_by_fresh_native_read': error is not None})


def native_clients():
    import boto3
    from botocore.config import Config
    require(boto3.__version__ == '1.43.111', 'Qualified locked SDK version differs')
    source = boto3.Session(region_name='us-east-1')
    credentials = source.get_credentials()
    require(credentials is not None, 'Native credentials unavailable')
    frozen = credentials.get_frozen_credentials()
    # One fixed credential identity for every read and the implicit-account write.
    session = boto3.Session(aws_access_key_id=frozen.access_key,
                            aws_secret_access_key=frozen.secret_key,
                            aws_session_token=frozen.token, region_name='us-east-1')
    config = Config(ignore_configured_endpoint_urls=True, use_fips_endpoint=False,
                    retries={'total_max_attempts': 1, 'mode': 'standard'},
                    connect_timeout=3, read_timeout=8)
    clients = {name: session.client(name, config=config) for name in ('sts', 'account', 'freetier')}
    context = {}
    endpoint, _, _ = clients['freetier']._resolve_endpoint_ruleset(
        clients['freetier'].meta.service_model.operation_model('UpgradeAccountPlan'),
        {'accountPlanType': 'PAID'}, context)
    require(endpoint == GLOBAL_ENDPOINT and context.get('signing', {}).get('region') == 'us-east-1'
            and context.get('signing', {}).get('signing_name') == 'freetier',
            'Qualified native global endpoint/signing differs')
    return clients


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('prepare', 'execute', 'admit-operation'))
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--source-admission', type=Path)
    args = parser.parse_args()
    binding = environment()
    if args.phase == 'admit-operation':
        operation_admission(binding)
        return
    require(args.directory is not None and args.source_admission is not None, 'Protected paths required')
    if args.phase == 'prepare':
        operation_admission(binding)
        needed = prepare(native_clients(), args.directory, binding)
        output = os.environ.get('GITHUB_OUTPUT')
        require(output is not None, 'Workflow output path unavailable')
        with open(output, 'a') as stream:
            stream.write('upgrade_needed=' + str(needed).lower() + '\n')
        print(json.dumps({'operation': 'prepare-paid-plan-intent', 'upgrade_needed': needed,
                          'aws_mutations': 0, 'native_paid_active_verified': not needed}))
    else:
        execute(native_clients(), args.directory, binding,
                admit_source=lambda: source_admission(args.source_admission), admit_published=published_intent)
        print(json.dumps({'operation': 'desired-paid-native-verification',
                          'native_paid_active_verified': True, 'automatic_deployment_retry': False}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # No exception text/traceback: SDK errors can contain provider/user input.
        print(json.dumps({'operation': 'desired-paid-repair-blocked',
                          'error_class': type(error).__name__, 'automatic_retry': False}), file=sys.stderr)
        raise SystemExit(1)
