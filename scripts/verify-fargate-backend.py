#!/usr/bin/env python3
"""Build and exercise the actual Fargate backend images without AWS access.

Uses the immutable checked-out Git revision, ordinary container commands, a
read-only root and ECS-like named /tmp volumes. --network none prevents runtime
AWS calls. The offline SQLite instance must remain unready until its authority
is initialized; live and public configuration must still work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
import time
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
UV = ['/usr/local/bin/uv', 'run', '--no-sync']
API_COMMAND = UV + ['uvicorn', 'otgd.main:app', '--host', '0.0.0.0', '--port', '8000',
    '--no-access-log', '--limit-concurrency', '100', '--timeout-graceful-shutdown', '100']
WORKER_COMMAND = UV + ['python', '-m', 'otgd.fargate_runtime', 'worker']


def command(arguments, *, timeout=180, check=True):
    environment = dict(os.environ)
    for name in ('DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH'):
        environment.pop(name, None)
    completed = subprocess.run(arguments, cwd=ROOT, env=environment, text=True,
        capture_output=True, timeout=timeout)
    if check and completed.returncode:
        raise RuntimeError('Container verification command failed: ' + ' '.join(arguments[:4]) +
            '\n' + completed.stdout[-3000:] + completed.stderr[-3000:])
    return completed


def docker(*arguments, **options):
    return command(['docker', '--host=unix:///var/run/docker.sock', *arguments], **options)


def image_field(image, expression):
    return json.loads(docker('image', 'inspect', '--format', '{{json ' + expression + '}}', image).stdout)


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision')
    parser.add_argument('--report', type=Path, default=ROOT / 'reports/fargate-backend.json')
    args = parser.parse_args()
    revision = command(['git', 'rev-parse', 'HEAD']).stdout.strip()
    require(re.fullmatch(r'[0-9a-f]{40}', revision) is not None, 'A full immutable source revision is required')
    require(args.revision is None or args.revision == revision, 'Requested source differs from the actual checkout')
    command(['git', 'diff', '--quiet', 'HEAD', '--'])
    docker('info', '--format', '{{.ServerVersion}}')
    identifier = uuid4().hex
    images = {}
    containers = []
    volumes = []
    evidence = {'source_revision': revision, 'status': 'started', 'aws_operations_executed': False,
                'runtime_network': 'none', 'images': {}, 'checks': []}

    def volume():
        name = 'otgd-fargate-backend-scratch-' + uuid4().hex
        volumes.append(name)
        return ['--mount', 'type=volume,src=' + name + ',dst=/tmp']

    def run_offline(image, script):
        name = 'otgd-fargate-backend-probe-' + uuid4().hex
        containers.append(name)
        result = docker('run', '--rm', '--name', name, '--network', 'none', '--read-only',
            *volume(), '--entrypoint', '/opt/venv/bin/python', image, '-c', script)
        return json.loads(result.stdout)

    work = ROOT / 'work'
    work.mkdir(exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='otgd-fargate-backend-', dir=work) as temporary:
            scratch = Path(temporary)
            archive = scratch / 'source.tar'
            context = scratch / 'context'
            context.mkdir()
            command(['git', 'archive', '--format=tar', '--output=' + str(archive), revision])
            with tarfile.open(archive) as source:
                source.extractall(context, filter='data')
            bundle_manifest = json.loads((context / 'infra/certs/manifest.json').read_text())
            runtime_sha = hashlib.sha256((context / 'services/api/otgd/fargate_runtime.py').read_bytes()).hexdigest()
            build_options = []
            certificate = os.environ.get('CODEX_PROXY_CERT')
            if certificate:
                require(Path(certificate).is_file(), 'Configured Docker proxy CA file is unavailable')
                build_options = ['--secret', 'id=proxy_ca,src=' + certificate]
            for target, expected_command in (('api', API_COMMAND), ('worker', WORKER_COMMAND)):
                image = 'otgd-fargate-backend-verification:' + identifier + '-' + target
                images[target] = image
                docker('buildx', 'build', '--load', '--platform', 'linux/amd64',
                    '--provenance=false', '--sbom=false', '--file', str(context / 'deploy/fargate.Dockerfile'),
                    '--target', target, '--tag', image,
                    '--label', 'org.opencontainers.image.revision=' + revision,
                    *build_options, str(context), timeout=900)
                require(image_field(image, '.Os') == 'linux' and image_field(image, '.Architecture') == 'amd64',
                        'Backend image does not target the actual Linux AMD64 Fargate platform')
                require(image_field(image, '.Config.User') == '10001', 'Backend image must run as UID 10001')
                require(image_field(image, '.Config.Entrypoint') in (None, []),
                        'Backend image inherits an unexpected entrypoint')
                require(image_field(image, '.Config.Cmd') == expected_command,
                        'Backend default command differs from the actual ordinary process contract')
                require(image_field(image, '(index .Config.Labels "org.opencontainers.image.revision")') == revision,
                        'Backend image revision label does not match the archived source')
                require('/tmp' in image_field(image, '.Config.Volumes'), 'Backend image lacks its ECS scratch-volume directive')
                probe = r'''
import hashlib, importlib, json, os
from pathlib import Path
import tempfile
root = Path('/app')
assert os.getuid() == 10001
assert Path('/tmp').stat().st_mode & 0o7777 == 0o1777
if Path('/tmp/uv-cache').exists():
    assert Path('/tmp/uv-cache').stat().st_uid == 10001
with tempfile.TemporaryFile(dir='/tmp') as scratch:
    scratch.write(b'disposable-offline-verification')
for name in ('contracts/application/openapi.json', 'tools', 'examples', 'infra/local',
             'openspec/changes/production-mobile-platform/fixtures'):
    assert (root / name).exists(), name
fixtures = root / 'openspec/changes/production-mobile-platform/fixtures'
assert any(path.is_file() for path in fixtures.rglob('*'))
module = importlib.import_module('otgd.fargate_runtime')
assert callable(module.main)
assert not Path('/opt/extensions/lambda-adapter').exists()
assert 'AWS_LAMBDA_RUNTIME_API' not in os.environ
bundle = root / 'infra/certs/global-bundle.pem'
print(json.dumps({'uid': os.getuid(), 'scratch_writable': True,
    'required_fixtures_present': True, 'lambda_adapter_absent': True,
    'rds_bundle_bytes': bundle.stat().st_size,
    'rds_bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
    'fargate_runtime_sha256': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()}))
'''
                actual = run_offline(image, probe)
                require(actual['rds_bundle_sha256'] == bundle_manifest['sha256']
                        and actual['rds_bundle_bytes'] == bundle_manifest['bytes'],
                        'Backend image RDS CA trust bundle differs from the reviewed manifest')
                require(actual['fargate_runtime_sha256'] == runtime_sha,
                        'Backend image does not contain the current reviewed Fargate runtime')
                evidence['images'][target] = {'image_id': image_field(image, '.Id'), 'source_revision': revision,
                                             'default_command': expected_command, 'packaging': actual}
            evidence['checks'].append('actual_api_and_worker_images_built_and_inspected')
            worker = 'otgd-fargate-worker-help-' + uuid4().hex
            containers.append(worker)
            help_result = docker('run', '--rm', '--name', worker, '--network', 'none', '--read-only',
                *volume(), '--entrypoint', '', images['worker'],
                *UV, 'python', '-m', 'otgd.fargate_runtime', '--help')
            require(all(mode in help_result.stdout for mode in ('controller', 'worker', 'maintenance')),
                    'Actual Fargate worker help does not expose its bounded process modes')
            evidence['checks'].append('full_worker_process_command_executed_offline')
            api = 'otgd-fargate-api-verification-' + uuid4().hex
            containers.append(api)
            docker('run', '--detach', '--name', api, '--network', 'none', '--read-only', *volume(),
                '--env', 'OTGD_ENVIRONMENT=test', '--env', 'OTGD_DATABASE_URL=sqlite://',
                '--env', 'AWS_EC2_METADATA_DISABLED=true', images['api'])
            http_probe = r'''
import json
from urllib.request import ProxyHandler, build_opener
opener = build_opener(ProxyHandler({}))
with opener.open('http://127.0.0.1:8000/health/live', timeout=3) as response:
    assert response.status == 200 and json.loads(response.read()) == {'status': 'alive'}
with opener.open('http://127.0.0.1:8000/v1/app-config', timeout=3) as response:
    config = json.loads(response.read())
    assert response.status == 200 and config['environment'] == 'test'
    assert config['schema_version'] == '1.0.0'
from urllib.error import HTTPError
try:
    opener.open('http://127.0.0.1:8000/health/ready', timeout=3)
except HTTPError as error:
    assert error.code == 503
else:
    raise AssertionError('Uninitialized offline database must not claim readiness')
print(json.dumps({'live_status': 200, 'app_config_status': 200,
    'uninitialized_readiness_status': 503, 'database_readiness_verified': False}))
'''
            deadline = time.monotonic() + 45
            while True:
                result = docker('exec', api, '/opt/venv/bin/python', '-c', http_probe, check=False, timeout=15)
                if result.returncode == 0:
                    evidence['api_http'] = json.loads(result.stdout)
                    break
                require(time.monotonic() < deadline, 'Actual read-only offline Fargate API failed its localhost HTTP checks')
                time.sleep(0.2)
            require(docker('exec', api, 'id', '-u').stdout.strip() == '10001', 'API process runs with unexpected privileges')
            require(json.loads(docker('inspect', '--format', '{{json .HostConfig.ReadonlyRootfs}}', api).stdout) is True,
                    'API container does not have an actual read-only root filesystem')
            require(json.loads(docker('inspect', '--format', '{{json .HostConfig.NetworkMode}}', api).stdout) == 'none',
                    'Offline backend verification unexpectedly has network access')
            evidence['checks'].append('actual_api_live_config_and_fail_closed_readiness_over_localhost')
            evidence['status'] = 'actual_fargate_backend_containers_verified'
    except Exception as error:
        evidence['status'] = 'blocked'
        evidence['failure_type'] = type(error).__name__
        raise
    finally:
        for container in containers:
            docker('rm', '--force', '--volumes', container, check=False)
        for name in volumes:
            docker('volume', 'rm', name, check=False)
        for image in images.values():
            docker('image', 'rm', image, check=False)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    print('Actual Fargate API and worker image checks passed; evidence: ' + str(args.report))


if __name__ == '__main__':
    main()
