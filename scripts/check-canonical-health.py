#!/usr/bin/env python3
"""Require actual Docker health and successful canonical initialization jobs.

Only filtered state is read. Container environment and healthcheck log output
are deliberately excluded from the report because they can contain secrets.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNNING = frozenset({'postgres', 'localstack', 'identity', 'api', 'worker'})
COMPLETED = frozenset({'resource-init', 'migrate'})
FORMAT = '''{"id":{{json .Id}},"project":{{json (index .Config.Labels "com.docker.compose.project")}},"service":{{json (index .Config.Labels "com.docker.compose.service")}},"oneoff":{{json (index .Config.Labels "com.docker.compose.oneoff")}},"state":{{json .State.Status}},"running":{{json .State.Running}},"exit_code":{{json .State.ExitCode}},"health":{{with (index .State "Health")}}{{json (index . "Status")}}{{else}}null{{end}}}'''


class HealthFailure(RuntimeError):
    pass


def validate(rows, project='otgd-local'):
    if not isinstance(rows, list): raise HealthFailure('INVALID_DOCKER_STATE')
    indexed = {}
    for row in rows:
        if row.get('project') != project or row.get('oneoff', '').lower() != 'false':
            raise HealthFailure('UNEXPECTED_CONTAINER_SCOPE')
        service = row.get('service')
        if service not in RUNNING | COMPLETED or service in indexed:
            raise HealthFailure('MISSING_OR_DUPLICATE_SERVICE')
        indexed[service] = row
    if set(indexed) != RUNNING | COMPLETED: raise HealthFailure('REQUIRED_SERVICE_MISSING')
    for service in RUNNING:
        row = indexed[service]
        if row.get('state') != 'running' or row.get('running') is not True or row.get('health') != 'healthy':
            raise HealthFailure('SERVICE_NOT_HEALTHY:' + service)
    for service in COMPLETED:
        row = indexed[service]
        if row.get('state') != 'exited' or row.get('running') is not False or type(row.get('exit_code')) is not int or row['exit_code'] != 0:
            raise HealthFailure('INITIALIZATION_NOT_COMPLETED:' + service)
    return {'status': 'passed', 'project': project,
            'healthy_services': sorted(RUNNING), 'successful_initializers': sorted(COMPLETED)}


def inspect(project='otgd-local', *, licensed=False, run=subprocess.run):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,62}', project): raise HealthFailure('INVALID_PROJECT')
    compose = ['docker', 'compose', '--project-name', project, '--env-file', str(ROOT / 'infra/local/.env'),
               '-f', str(ROOT / 'infra/local/compose.yml')]
    if licensed: compose += ['-f', str(ROOT / 'infra/local/compose.localstack-licensed.yml')]
    try:
        result = run(compose + ['ps', '--all', '--quiet'], check=True, capture_output=True, text=True, timeout=30)
        identifiers = result.stdout.split()
        if len(identifiers) != len(RUNNING | COMPLETED) or any(not re.fullmatch('[0-9a-f]{12,64}', v) for v in identifiers):
            raise HealthFailure('REQUIRED_CONTAINER_INVENTORY_MISSING')
        state = run(['docker', 'inspect', '--format', FORMAT, *identifiers], check=True, capture_output=True, text=True, timeout=30)
        rows = [json.loads(line) for line in state.stdout.splitlines() if line.strip()]
        return validate(rows, project)
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        raise HealthFailure('DOCKER_STATE_UNAVAILABLE') from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-name', default='otgd-local')
    parser.add_argument('--licensed-localstack', action='store_true')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(inspect(args.project_name, licensed=args.licensed_localstack), sort_keys=True))
        return 0
    except HealthFailure as error:
        print(json.dumps({'status': 'failed', 'reason': str(error)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
