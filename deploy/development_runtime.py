"""Build a repeatable single-host development runtime; perform no cloud calls.

This package keeps the existing cloud application's journal and admission checks.
It does not create registry approvals or authorize promotion to QA/production.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import ipaddress
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shlex
import tarfile

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_VERSION = '2.39.4'
COMPOSE_SHA256 = '7af95166a730b87e172d4fc9aefea8725d3c6c7327d59149267b452114ddb7d4'
RUNTIME_DIRECTORY = '/opt/otgd-development'
DATA_DIRECTORY = '/var/lib/otgd-development'


def _identity(config):
    if not re.fullmatch(r'[0-9]{12}', str(config.get('account', ''))):
        raise ValueError('An actual AWS account is required')
    if config.get('region') != 'us-east-2':
        raise ValueError('This development runtime is reviewed for Ohio')
    if not re.fullmatch(r'[0-9a-f]{40}', str(config.get('releaseId', ''))):
        raise ValueError('An immutable full source revision is required')


def _https_origin(value):
    if not isinstance(value, str) or not re.fullmatch(r'https://[a-z0-9][a-z0-9.-]+(?::443)?', value):
        raise ValueError('An actual HTTPS origin is required')
    return value


def runtime_environment(config, outputs):
    """Resolve actual infrastructure outputs into the unmodified cloud settings."""
    _identity(config)
    api = _https_origin(outputs['ApiOrigin'])
    web = _https_origin(outputs['WebOrigin'])
    identity = _https_origin(outputs['IdentityOrigin'])
    issuer = outputs['Issuer']
    prefix = f"https://cognito-idp.{config['region']}.amazonaws.com/"
    if not isinstance(issuer, str) or not issuer.startswith(prefix) or '/' in issuer[len(prefix):]:
        raise ValueError('Actual regional Cognito issuer is required')
    pool = outputs.get('UserPoolId') or issuer[len(prefix):]
    if not pool or issuer != prefix + pool:
        raise ValueError('Cognito user pool must match the issuer')
    keys = [outputs[name] for name in ('DataKeyArn', 'JournalKeyArn', 'CaptureSigningKeyArn')]
    kms_prefix = f"arn:aws:kms:{config['region']}:{config['account']}:key/"
    if len(set(keys)) != 3 or any(not str(key).startswith(kms_prefix) for key in keys):
        raise ValueError('Separate same-account data, journal and capture KMS keys are required')
    environment = {
        # Existing cloud Settings accepts qa/prod. Infrastructure remains explicitly
        # development, with no qualification or promotion implied by this value.
        'OTGD_ENVIRONMENT': 'qa',
        'OTGD_DATABASE_HOST': 'postgres', 'OTGD_DATABASE_PORT': '5432',
        'OTGD_DATABASE_NAME': 'otgd', 'OTGD_DATABASE_USER': 'otgd_app',
        'OTGD_DATABASE_SSLMODE': 'verify-full',
        'OTGD_DATABASE_SSLROOTCERT': '/run/otgd-tls/ca.crt',
        'OTGD_DATABASE_POOL_SIZE': '3', 'OTGD_APP_DATABASE_USER': 'otgd_app',
        'OTGD_ISSUER': issuer, 'OTGD_CLIENT_ID': outputs['ClientId'],
        'OTGD_JWKS_URL': issuer + '/.well-known/jwks.json',
        'OTGD_API_ORIGIN': api, 'OTGD_IDENTITY_ORIGIN': identity,
        'OTGD_OAUTH_REDIRECT_URIS': json.dumps(['otgd-qa://oauth/callback', web + '/']),
        'OTGD_USER_POOL_ID': pool, 'OTGD_AWS_REGION': config['region'],
        'OTGD_DEPLOYMENT_ACCOUNT': config['account'], 'OTGD_SOURCE_REVISION': config['releaseId'],
        'OTGD_ARTIFACT_BUCKET': outputs['ArtifactBucket'], 'OTGD_EXPORT_BUCKET': outputs['ExportBucket'],
        'OTGD_JOURNAL_BUCKET': outputs['JournalBucket'], 'OTGD_QUEUE_URL': outputs['QueueUrl'],
        'OTGD_DLQ_URL': outputs['DeadLetterQueueUrl'], 'OTGD_TOMBSTONE_KEY_ID': 'v1',
        'OTGD_STORAGE_KMS_KEY_ID': outputs['DataKeyArn'], 'OTGD_JOURNAL_KMS_KEY_ID': outputs['JournalKeyArn'],
        'OTGD_CAPTURE_SIGNING_KEY_ID': outputs['CaptureSigningKeyArn'],
        'OTGD_RECOVERY_REQUIRED': 'false', 'OTGD_INDEPENDENT_RECOVERY_ADMISSION': 'true',
        'AWS_DEFAULT_REGION': config['region'], 'AWS_EC2_METADATA_DISABLED': 'false',
        'AWS_IGNORE_CONFIGURED_ENDPOINT_URLS': 'true',
        'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUNBUFFERED': '1', 'UV_NO_SYNC': '1',
        'NO_PROXY': 'localhost,127.0.0.1,postgres,169.254.169.254',
        'no_proxy': 'localhost,127.0.0.1,postgres,169.254.169.254',
    }
    for key, value in environment.items():
        if not isinstance(value, str) or not value or '\n' in value or '\r' in value:
            raise ValueError('A concrete bounded runtime setting is required: ' + key)
    return environment


def compose_spec(config, outputs, service_image=None):
    """Return JSON-compatible Compose without passwords or static AWS credentials."""
    env = runtime_environment(config, outputs)
    private_ip = str(ipaddress.ip_address(outputs['EC2PrimaryPrivateIp']))
    if not ipaddress.ip_address(private_ip).is_private:
        raise ValueError('API must bind the EC2 private origin address')
    image = service_image or 'otgd-dev:' + config['releaseId']
    if not re.fullmatch(r'otgd-dev:[0-9a-f]{40}', image):
        raise ValueError('Local image must carry the exact reviewed source revision')
    lock = json.loads((ROOT / 'infra/images.lock.json').read_text())['images']['postgres']
    postgres_image = f"{lock['repository']}:{lock['tag']}@{lock['digest']}"
    logging = {'driver': 'awslogs', 'options': {
        'awslogs-region': config['region'], 'awslogs-group': outputs['LogGroup'],
        'awslogs-create-group': 'false', 'mode': 'non-blocking', 'max-buffer-size': '4m'}}

    def log(name):
        return {'driver': logging['driver'], 'options': {**logging['options'],
                'awslogs-stream': name + '-' + config['releaseId']}}

    def runtime(name, command, memory):
        return {'image': image, 'init': True, 'user': '10001:10001', 'read_only': True,
                'tmpfs': ['/tmp:size=134217728,mode=1777'], 'cap_drop': ['ALL'],
                'security_opt': ['no-new-privileges:true'], 'stop_grace_period': '120s',
                'env_file': ['./app.env'], 'environment': env, 'command': command,
                'volumes': [DATA_DIRECTORY + '/tls/ca.crt:/run/otgd-tls/ca.crt:ro'],
                'mem_limit': memory, 'logging': log(name), 'restart': 'on-failure:5',
                'depends_on': {'postgres': {'condition': 'service_healthy'}}}

    postgres = {'image': postgres_image, 'env_file': ['./postgres.env'],
                'environment': {'POSTGRES_DB': 'otgd', 'POSTGRES_USER': 'otgd_migrator'},
                'volumes': [DATA_DIRECTORY + '/postgres:/var/lib/postgresql/data',
                            DATA_DIRECTORY + '/tls:/run/otgd-tls:ro'],
                'command': ['postgres', '-c', 'ssl=on', '-c', 'ssl_cert_file=/run/otgd-tls/server.crt',
                            '-c', 'ssl_key_file=/run/otgd-tls/server.key', '-c', 'ssl_min_protocol_version=TLSv1.2',
                            '-c', 'max_connections=40', '-c', 'shared_buffers=128MB'],
                'mem_limit': '1024m', 'restart': 'unless-stopped', 'logging': log('postgres'),
                'healthcheck': {'test': ['CMD-SHELL', 'pg_isready -U otgd_migrator -d otgd'],
                                'interval': '5s', 'timeout': '3s', 'retries': 30}}
    api = runtime('api', ['uv', 'run', '--no-sync', 'uvicorn', 'otgd.main:app', '--host', '0.0.0.0',
                         '--port', '8000', '--no-access-log', '--limit-concurrency', '100',
                         '--timeout-graceful-shutdown', '100'], '768m')
    api['ports'] = [private_ip + ':8000:8000']
    api['healthcheck'] = {'test': ['CMD', 'python', '-c',
        "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/ready',timeout=4)"],
        'interval': '10s', 'timeout': '5s', 'retries': 20, 'start_period': '30s'}
    worker = runtime('worker', ['uv', 'run', '--no-sync', 'python', '-m', 'otgd.worker'], '1024m')
    worker['healthcheck'] = {'test': ['CMD', 'uv', 'run', '--no-sync', 'python', '-m', 'otgd.worker_health'],
                           'interval': '10s', 'timeout': '5s', 'retries': 3, 'start_period': '35s'}
    metrics = runtime('metrics', ['uv', 'run', '--no-sync', 'python', '/app/scripts/publish-metrics.py'], '256m')
    metrics['environment'] = {**env, 'OTGD_DATABASE_POOL_SIZE': '1'}
    maintenance = runtime('maintenance', ['uv', 'run', '--no-sync', 'python', '-m', 'otgd.migrate'], '1024m')
    maintenance.update(profiles=['maintenance'], restart='no', env_file=['./maintenance.env'])
    maintenance['environment'] = {**env, 'OTGD_DATABASE_USER': 'otgd_migrator', 'OTGD_DATABASE_POOL_SIZE': '1'}
    return {'name': 'otgd-development', 'services': {
        'postgres': postgres, 'api': api, 'worker': worker, 'metrics': metrics, 'maintenance': maintenance}}


# Runs only on the EC2 host, never while generating or importing the package.
HOST_RUNNER = r'''#!/usr/bin/env python3
"""Protected development startup, maintenance and nightly backup."""
import base64
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import posixpath
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path('/opt/otgd-development')
DATA = Path('/var/lib/otgd-development')
CONFIG = json.loads((ROOT / 'runtime.json').read_text())
STAGES = []

def invoke(command, timeout=600, binary=False):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith('AWS_ENDPOINT_URL') and key not in (
               'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_PROFILE')}
    env.update(AWS_IGNORE_CONFIGURED_ENDPOINT_URLS='true', AWS_CONFIG_FILE='/dev/null',
               AWS_SHARED_CREDENTIALS_FILE='/dev/null', AWS_EC2_METADATA_DISABLED='false')
    result = subprocess.run(command, cwd=ROOT, env=env, check=True, capture_output=True,
                            timeout=timeout, text=not binary)
    return result.stdout

def aws(*arguments):
    raw = invoke(['aws', *arguments, '--region', CONFIG['region'], '--output', 'json',
                  '--cli-connect-timeout', '5', '--cli-read-timeout', '20'], timeout=90)
    return json.loads(raw) if raw.strip() else {}

def compose(*arguments, timeout=600):
    return invoke(['docker', 'compose', '-f', str(ROOT / 'compose.json'), *arguments], timeout=timeout)

def private_write(path, raw):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(raw)

def state(status, **extra):
    body = {'schema_version': '1.0.0', 'deployment': 'development', 'status': status,
            'account': CONFIG['account'], 'region': CONFIG['region'],
            'release_id': CONFIG['release_id'], 'source_sha256': CONFIG['source_sha256'],
            'observed_at': datetime.now(timezone.utc).isoformat(), 'completed_stages': list(STAGES),
            'qa_approval': 'not_executed', 'promotion_eligible': False, **extra}
    private_write(DATA / 'deployment-state.json', json.dumps(body, indent=2) + '\n')
    return body

def stage(name, operation):
    state('running', current_stage=name)
    result = operation()
    STAGES.append(name)
    state('running', current_stage=name)
    return result

def secrets():
    identity = aws('sts', 'get-caller-identity')
    if identity['Account'] != CONFIG['account']:
        raise RuntimeError('Account mismatch')
    response = aws('secretsmanager', 'get-secret-value', '--secret-id', CONFIG['secret_arn'])
    raw = response['SecretString']
    if len(raw) > 8192:
        raise RuntimeError('Oversized runtime secret')
    seed = json.loads(raw).get('seed', '')
    if len(seed) != 64 or any(character not in '0123456789abcdef' for character in seed):
        raise RuntimeError('Invalid runtime seed')
    def derive(label):
        return hashlib.sha256(bytes.fromhex(seed) + b'\0otgd-development:' + label.encode()).hexdigest()
    migration, app, tombstone = [derive(label) for label in (
        'migration-password', 'app-password', 'tombstone-key')]
    private_write(ROOT / 'postgres.env', 'POSTGRES_PASSWORD=' + migration + '\n')
    private_write(ROOT / 'app.env', 'OTGD_DATABASE_PASSWORD=' + app + '\nOTGD_TOMBSTONE_KEY=' + tombstone + '\n')
    private_write(ROOT / 'maintenance.env', 'OTGD_DATABASE_PASSWORD=' + migration +
                  '\nOTGD_APP_DATABASE_PASSWORD=' + app + '\nOTGD_TOMBSTONE_KEY=' + tombstone + '\n')

def tls():
    directory = DATA / 'tls'
    directory.mkdir(mode=0o755, exist_ok=True)
    names = ['ca.key', 'ca.crt', 'server.key', 'server.crt']
    existing = [bool((directory / name).exists()) for name in names]
    if any(existing) and not all(existing):
        raise RuntimeError('Partial retained TLS material requires operator recovery')
    if not any(existing):
        invoke(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:3072', '-out', str(directory / 'ca.key')])
        invoke(['openssl', 'req', '-x509', '-new', '-key', str(directory / 'ca.key'), '-sha256', '-days', '3650',
                '-subj', '/CN=OTGD development database CA', '-out', str(directory / 'ca.crt')])
        invoke(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:3072', '-out', str(directory / 'server.key')])
        invoke(['openssl', 'req', '-new', '-key', str(directory / 'server.key'), '-subj', '/CN=postgres',
                '-out', str(directory / 'server.csr')])
        private_write(directory / 'server.ext', 'subjectAltName=DNS:postgres\nextendedKeyUsage=serverAuth\n')
        invoke(['openssl', 'x509', '-req', '-in', str(directory / 'server.csr'), '-CA', str(directory / 'ca.crt'),
                '-CAkey', str(directory / 'ca.key'), '-CAcreateserial', '-days', '825', '-sha256',
                '-extfile', str(directory / 'server.ext'), '-out', str(directory / 'server.crt')])
        (directory / 'server.csr').unlink()
        (directory / 'server.ext').unlink()
    invoke(['openssl', 'verify', '-CAfile', str(directory / 'ca.crt'), '-verify_hostname', 'postgres',
            str(directory / 'server.crt')])
    invoke(['openssl', 'x509', '-checkend', '604800', '-noout', '-in', str(directory / 'server.crt')])
    os.chmod(directory / 'ca.key', 0o600)
    os.chmod(directory / 'server.key', 0o400)
    os.chown(directory / 'server.key', 999, 999)
    for name in ('ca.crt', 'server.crt'):
        os.chmod(directory / name, 0o444)

def build():
    archive = ROOT / 'source.archive'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != CONFIG['source_sha256']:
        raise RuntimeError('Source digest mismatch')
    source = ROOT / 'source'
    if source.exists():
        # This directory contains only disposable verified build input, never DB.
        shutil.rmtree(source)
    source.mkdir(mode=0o700)
    with tarfile.open(archive) as bundle:
        if bundle.pax_headers.get('comment') != CONFIG['release_id']:
            raise RuntimeError('Archive source revision mismatch')
        total = 0
        members = bundle.getmembers()
        regular = {member.name for member in members if member.isfile()}
        for member in members:
            path = Path(member.name)
            total += member.size
            if path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir() or member.issym()) or total > 536870912:
                raise RuntimeError('Unsafe source archive')
            if member.issym():
                target = posixpath.normpath(posixpath.join(posixpath.dirname(member.name), member.linkname))
                if (Path(member.linkname).is_absolute() or target.startswith('../') or target not in regular or
                        any(other.name.startswith(member.name + '/') for other in members)):
                    raise RuntimeError('Unsafe source symlink')
        bundle.extractall(source, members=members)
    invoke(['docker', 'build', '--pull', '--platform', 'linux/amd64', '--label',
            'org.opencontainers.image.revision=' + CONFIG['release_id'], '-f',
            str(source / 'infra/local/service.Dockerfile'), '--tag', CONFIG['service_image'], str(source)], timeout=1800)
    image = json.loads(invoke(['docker', 'image', 'inspect', CONFIG['service_image']]))[0]
    if image['Config']['Labels'].get('org.opencontainers.image.revision') != CONFIG['release_id']:
        raise RuntimeError('Image source label mismatch')
    private_write(DATA / 'image.json', json.dumps({'image_id': image['Id'],
        'release_id': CONFIG['release_id'], 'source_sha256': CONFIG['source_sha256']}) + '\n')

def maintenance(operation):
    commands = {
        'journal': ['uv', 'run', '--no-sync', 'python', '/app/infra/local/bootstrap_resources.py', '--verify-cloud'],
        'migration': ['uv', 'run', '--no-sync', 'python', '-m', 'otgd.migrate'],
        'admission': ['uv', 'run', '--no-sync', 'python', '-m', 'otgd.recovery_authority'],
    }
    command = commands[operation]
    sentinel = DATA / 'journal-established.json'
    if operation == 'journal' and CONFIG['establish_new'] and not sentinel.exists():
        command = command + ['--establish-new']
    compose('run', '--rm', '-T', 'maintenance', *command, timeout=900)
    # A checked actual exit is retained; command output and stderr stay protected.
    private_write(DATA / (operation + '.json'), json.dumps({'operation': operation,
        'exit_code': 0, 'release_id': CONFIG['release_id'], 'completed_at': datetime.now(timezone.utc).isoformat()}) + '\n')
    if operation == 'journal':
        private_write(sentinel, json.dumps({'verified': True, 'release_id': CONFIG['release_id']}) + '\n')

def observe():
    rows = [json.loads(line) for line in compose('ps', '--format', 'json').splitlines() if line]
    observed = {row['Service']: row for row in rows if row.get('Service') in ('postgres', 'api', 'worker', 'metrics')}
    if set(observed) != {'postgres', 'api', 'worker', 'metrics'}:
        raise RuntimeError('Missing runtime container')
    for name, row in observed.items():
        if row.get('State') != 'running' or (name != 'metrics' and row.get('Health') != 'healthy'):
            raise RuntimeError('Unhealthy runtime container')
    deadline = time.monotonic() + 300
    metric_names = ('OldestOutboxSeconds', 'OldestPrivacyJobSeconds', 'CleanupOverdueCount')
    while time.monotonic() < deadline:
        instant = datetime.now(timezone.utc)
        fresh = True
        for metric in metric_names:
            points = aws('cloudwatch', 'get-metric-statistics', '--namespace', 'OTGD/qa',
                '--metric-name', metric, '--start-time', (instant - timedelta(minutes=3)).isoformat(),
                '--end-time', instant.isoformat(), '--period', '60', '--statistics', 'Maximum')['Datapoints']
            fresh = fresh and bool(points)
        if fresh:
            return {'docker_health': 'passed', 'worker_progress_health': 'passed', 'metrics_freshness': 'passed'}
        time.sleep(10)
    raise RuntimeError('Operational metrics did not become fresh')

def start():
    stage('fetch-runtime-secrets', secrets)
    compose('stop', 'api', 'worker', 'metrics', timeout=180)
    stage('verify-source-build-image', build)
    stage('verify-retained-database-tls', tls)
    (DATA / 'postgres').mkdir(mode=0o700, exist_ok=True)
    stage('start-database', lambda: compose('up', '-d', '--wait', '--wait-timeout', '180', 'postgres', timeout=240))
    stage('verify-journal', lambda: maintenance('journal'))
    stage('migrate', lambda: maintenance('migration'))
    stage('verify-independent-admission', lambda: maintenance('admission'))
    stage('activate-runtime', lambda: compose('up', '-d', '--wait', '--wait-timeout', '240', 'api', 'worker', 'metrics', timeout=300))
    evidence = stage('verify-runtime-health', observe)
    return state('runtime_healthy', **evidence)

def backup():
    directory = DATA / 'backup'
    directory.mkdir(mode=0o700, exist_ok=True)
    output = directory / 'database.dump'
    # POSTGRES_PASSWORD stays inside the container; no password argument or log.
    with output.open('wb') as stream:
        result = subprocess.run(['docker', 'compose', '-f', str(ROOT / 'compose.json'), 'exec', '-T',
            'postgres', 'sh', '-c', 'PGPASSWORD="$POSTGRES_PASSWORD" exec pg_dump -U otgd_migrator -d otgd -Fc'],
            cwd=ROOT, stdout=stream, stderr=subprocess.PIPE, timeout=900)
    os.chmod(output, 0o600)
    if result.returncode != 0 or output.stat().st_size == 0:
        raise RuntimeError('Database backup failed')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    key = 'backups/otgd-development/' + stamp + '.dump'
    if aws('s3api', 'get-bucket-versioning', '--bucket', CONFIG['backup_bucket']).get('Status') != 'Enabled':
        raise RuntimeError('Backup bucket versioning is required')
    digest = hashlib.sha256(output.read_bytes()).digest()
    uploaded = aws('s3api', 'put-object', '--bucket', CONFIG['backup_bucket'], '--key', key,
        '--body', str(output), '--server-side-encryption', 'AES256',
        '--checksum-sha256', base64.b64encode(digest).decode())
    version = uploaded.get('VersionId')
    if not version or version == 'null':
        raise RuntimeError('Backup upload did not retain an actual S3 version')
    private_write(DATA / 'backup-state.json', json.dumps({'status': 'uploaded', 'bucket': CONFIG['backup_bucket'],
        'key': key, 'version_id': version, 'sha256': digest.hex(), 'created_at': stamp}) + '\n')
    return {'operation': 'development-backup', 'status': 'uploaded', 'key': key, 'version_id': version}

def host_metrics():
    memory = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in ('MemTotal', 'MemAvailable'):
            memory[key] = int(value.strip().split()[0])
    memory_used = 100 * (1 - memory['MemAvailable'] / memory['MemTotal'])
    disk = os.statvfs(DATA)
    disk_used = 100 * (1 - disk.f_bavail / disk.f_blocks)
    metrics = [{'MetricName': name, 'Value': value, 'Unit': 'Percent',
                'Dimensions': [{'Name': 'InstanceId', 'Value': CONFIG['instance_id']}]}
               for name, value in (('MemoryUsedPercent', memory_used), ('DiskUsedPercent', disk_used))]
    aws('cloudwatch', 'put-metric-data', '--namespace', 'OTGD/development', '--metric-data', json.dumps(metrics))
    return {'operation': 'development-host-metrics', 'status': 'published'}

def main():
    DATA.mkdir(mode=0o700, exist_ok=True)
    descriptor = os.open(DATA / 'runtime.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            command = sys.argv[1] if len(sys.argv) > 1 else 'start'
            result = (start() if command == 'start' else backup() if command == 'backup' else
                      observe() if command == 'health' else host_metrics() if command == 'host-metrics' else None)
            if result is None:
                raise RuntimeError('Unsupported runtime operation')
            print(json.dumps(result))
            return 0
        except Exception as error:
            # Captured secret/API/Docker output is intentionally not forwarded.
            failure = (state('failed', error_type=type(error).__name__, rollback_executed=False)
                       if command == 'start' else {'operation': command, 'status': 'failed',
                                                  'error_type': type(error).__name__})
            print(json.dumps(failure))
            return 2

if __name__ == '__main__':
    raise SystemExit(main())
'''


def runtime_files(config, outputs, source_sha256, establish_new=False):
    if not re.fullmatch(r'[0-9a-f]{64}', str(source_sha256)):
        raise ValueError('A verified source archive digest is required')
    spec = compose_spec(config, outputs)
    secret = outputs['RuntimeSecretArn']
    if not str(secret).startswith(f"arn:aws:secretsmanager:{config['region']}:{config['account']}:secret:"):
        raise ValueError('Runtime secret must belong to the selected account and region')
    backup_bucket = outputs.get('DeploymentBucket') or outputs.get('RuntimeAssetBucket')
    if not isinstance(backup_bucket, str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]', backup_bucket):
        raise ValueError('The private versioned deployment bucket is required for backups')
    runtime = {'account': config['account'], 'region': config['region'], 'release_id': config['releaseId'],
               'source_sha256': source_sha256, 'service_image': 'otgd-dev:' + config['releaseId'],
               'secret_arn': secret, 'establish_new': bool(establish_new), 'backup_bucket': backup_bucket,
               'instance_id': outputs['InstanceId']}
    if not re.fullmatch(r'i-[0-9a-f]{8,17}', str(runtime['instance_id'])):
        raise ValueError('The actual instance ID is required for host metrics')
    service = f'''[Unit]
Description=On-The-Go Detection development runtime
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
UMask=0077
WorkingDirectory={RUNTIME_DIRECTORY}
ExecStart=/usr/bin/python3 {RUNTIME_DIRECTORY}/runtime.py start
ExecStop=/usr/bin/docker compose -f {RUNTIME_DIRECTORY}/compose.json stop
TimeoutStartSec=3600
TimeoutStopSec=180

[Install]
WantedBy=multi-user.target
'''
    backup_service = f'''[Unit]
Description=Protected development PostgreSQL backup to versioned S3
After=otgd-development.service
Requires=otgd-development.service

[Service]
Type=oneshot
UMask=0077
WorkingDirectory={RUNTIME_DIRECTORY}
ExecStart=/usr/bin/python3 {RUNTIME_DIRECTORY}/runtime.py backup
TimeoutStartSec=1200
'''
    timer = '''[Unit]
Description=Nightly development PostgreSQL backup

[Timer]
OnCalendar=*-*-* 04:00:00 UTC
RandomizedDelaySec=900
Persistent=true

[Install]
WantedBy=timers.target
'''
    host_service = f'''[Unit]
Description=Development host memory and disk metrics
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
UMask=0077
WorkingDirectory={RUNTIME_DIRECTORY}
ExecStart=/usr/bin/python3 {RUNTIME_DIRECTORY}/runtime.py host-metrics
TimeoutStartSec=120
'''
    host_timer = '''[Unit]
Description=Publish development host memory and disk metrics every five minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
'''
    return {'compose.json': (json.dumps(spec, sort_keys=True, indent=2) + '\n').encode(),
            'runtime.json': (json.dumps(runtime, sort_keys=True, indent=2) + '\n').encode(),
            'runtime.py': HOST_RUNNER.encode(), 'otgd-development.service': service.encode(),
            'otgd-development-backup.service': backup_service.encode(),
            'otgd-development-backup.timer': timer.encode(),
            'otgd-development-host-metrics.service': host_service.encode(),
            'otgd-development-host-metrics.timer': host_timer.encode()}


def package_runtime(destination, config, outputs, source_archive, establish_new=False):
    """Package reviewed source and host instructions with stable hashes/metadata."""
    source = Path(source_archive).read_bytes()
    if len(source) > 67_108_864:
        raise ValueError('Source archive exceeds the development package bound')
    with tarfile.open(fileobj=io.BytesIO(source), mode='r:*') as archive:
        if archive.pax_headers.get('comment') != config.get('releaseId'):
            raise ValueError('Archive must identify the exact reviewed Git revision')
        members = archive.getmembers()
        regular = {member.name for member in members if member.isfile()}
        names = set()
        total = 0
        for member in members:
            path = PurePosixPath(member.name)
            total += member.size
            if (path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir() or member.issym()) or
                    '.git' in path.parts or '.local' in path.parts or member.name.endswith('.local.json') or
                    member.name in names or total > 536_870_912):
                raise ValueError('Source archive contains unsafe or local material')
            if member.issym():
                target = posixpath.normpath(posixpath.join(posixpath.dirname(member.name), member.linkname))
                if (PurePosixPath(member.linkname).is_absolute() or target.startswith('../') or target not in regular or
                        any(other.name.startswith(member.name + '/') for other in members)):
                    raise ValueError('Source archive contains an unsafe symlink')
            names.add(member.name)
        for required in ('services/api/pyproject.toml', 'services/api/uv.lock', 'infra/local/service.Dockerfile'):
            if required not in names:
                raise ValueError('Source archive is missing a required locked service input')
    source_sha256 = hashlib.sha256(source).hexdigest()
    files = runtime_files(config, outputs, source_sha256, establish_new)
    files['source.archive'] = source
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb', filename='', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w') as archive:
            for name, raw in sorted(files.items()):
                info = tarfile.TarInfo(name)
                info.size = len(raw)
                info.mode = 0o700 if name == 'runtime.py' else 0o600
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ''
                archive.addfile(info, io.BytesIO(raw))
    artifact = buffer.getvalue()
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(artifact)
    path.chmod(0o600)
    return {'path': str(path), 'sha256': hashlib.sha256(artifact).hexdigest(),
            'source_sha256': source_sha256, 'size_bytes': len(artifact),
            'source_revision': config['releaseId'], 'service_image': 'otgd-dev:' + config['releaseId']}


def startup_script(region, account, bucket, key, sha256, volume_device=None):
    """Return a protected repeatable SSM command; download and verify before start."""
    if region != 'us-east-2' or not re.fullmatch(r'[0-9]{12}', str(account)):
        raise ValueError('The actual Ohio account is required')
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]', str(bucket)):
        raise ValueError('A concrete private package bucket is required')
    if not isinstance(key, str) or not key or len(key) > 1024 or '..' in PurePosixPath(key).parts:
        raise ValueError('A bounded immutable package key is required')
    if not re.fullmatch(r'[0-9a-f]{64}', str(sha256)):
        raise ValueError('A trusted runtime package digest is required')
    if volume_device is not None:
        raise ValueError('This baseline preserves database data on the retained root EBS volume')
    q = shlex.quote
    return f'''#!/bin/bash
set -euo pipefail
umask 077
test "$(uname -m)" = x86_64
dnf install -y docker awscli-2 openssl python3 >/dev/null
systemctl enable --now docker >/dev/null
install -d -m 0700 {RUNTIME_DIRECTORY} {DATA_DIRECTORY}
if systemctl cat otgd-development.service >/dev/null 2>&1; then
  systemctl stop otgd-development.service
fi
install -d -m 0755 /usr/local/lib/docker/cli-plugins
if ! test -f /usr/local/lib/docker/cli-plugins/docker-compose || ! echo '{COMPOSE_SHA256}  /usr/local/lib/docker/cli-plugins/docker-compose' | sha256sum --check --status; then
  curl --fail --silent --show-error --location --max-time 120 https://github.com/docker/compose/releases/download/v{COMPOSE_VERSION}/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose.new
  echo '{COMPOSE_SHA256}  /usr/local/lib/docker/cli-plugins/docker-compose.new' | sha256sum --check --status
  chmod 0755 /usr/local/lib/docker/cli-plugins/docker-compose.new
  mv /usr/local/lib/docker/cli-plugins/docker-compose.new /usr/local/lib/docker/cli-plugins/docker-compose
fi
AWS_IGNORE_CONFIGURED_ENDPOINT_URLS=true aws s3api get-object --region {q(region)} --bucket {q(bucket)} --key {q(key)} {RUNTIME_DIRECTORY}/runtime.tgz >/dev/null
echo '{sha256}  {RUNTIME_DIRECTORY}/runtime.tgz' | sha256sum --check --status
python3 - <<'PY'
from pathlib import Path
import tarfile
root = Path('{RUNTIME_DIRECTORY}')
allowed = {{'compose.json', 'runtime.json', 'runtime.py', 'source.archive', 'otgd-development.service', 'otgd-development-backup.service', 'otgd-development-backup.timer', 'otgd-development-host-metrics.service', 'otgd-development-host-metrics.timer'}}
with tarfile.open(root / 'runtime.tgz') as archive:
    members = archive.getmembers()
    if len(members) != len(allowed) or {{member.name for member in members}} != allowed or any(not member.isfile() for member in members):
        raise RuntimeError('Unsafe runtime package')
    archive.extractall(root, members=members)
PY
install -m 0644 {RUNTIME_DIRECTORY}/otgd-development.service /etc/systemd/system/otgd-development.service
install -m 0644 {RUNTIME_DIRECTORY}/otgd-development-backup.service /etc/systemd/system/otgd-development-backup.service
install -m 0644 {RUNTIME_DIRECTORY}/otgd-development-backup.timer /etc/systemd/system/otgd-development-backup.timer
install -m 0644 {RUNTIME_DIRECTORY}/otgd-development-host-metrics.service /etc/systemd/system/otgd-development-host-metrics.service
install -m 0644 {RUNTIME_DIRECTORY}/otgd-development-host-metrics.timer /etc/systemd/system/otgd-development-host-metrics.timer
systemctl daemon-reload
systemctl enable otgd-development.service >/dev/null
systemctl restart otgd-development.service
python3 {RUNTIME_DIRECTORY}/runtime.py backup
systemctl enable --now otgd-development-backup.timer >/dev/null
python3 {RUNTIME_DIRECTORY}/runtime.py host-metrics
systemctl enable --now otgd-development-host-metrics.timer >/dev/null
python3 {RUNTIME_DIRECTORY}/runtime.py health
'''
