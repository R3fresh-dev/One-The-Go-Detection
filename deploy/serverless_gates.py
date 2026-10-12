"""Current-main and newest-run admission for the development-only deployer."""
from __future__ import annotations

import os
import re

import httpx

from deploy import platform
from deploy.provenance import Gate, REPOSITORY, WORKFLOW_PATH, trusted_branch
from otgd.canonical import strict_loads


def select_latest_gate(revision, fetch):
    if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise Gate('Serverless admission requires an immutable source revision')
    runs, seen = [], set()
    total = None
    scanned = 0
    for page in range(1, 11):
        response = fetch(f'repos/{REPOSITORY}/actions/workflows/merge-gate.yml/runs',
                         head_sha=revision, per_page=100, page=page)
        batch = response.get('workflow_runs')
        count = response.get('total_count')
        if (not isinstance(batch, list) or len(batch) > 100 or type(count) is not int
                or not 0 <= count <= 1000 or (total is not None and count != total)):
            raise Gate('GitHub workflow inventory is malformed or exceeds its supported bounds')
        total = count
        for run in batch:
            if not isinstance(run, dict) or type(run.get('id')) is not int or run['id'] <= 0 or run['id'] in seen:
                raise Gate('GitHub workflow identity is malformed or repeated')
            seen.add(run['id'])
            if (run.get('head_sha') == revision and run.get('path') == WORKFLOW_PATH
                    and trusted_branch(run.get('event'), run.get('head_branch'))
                    and isinstance(run.get('repository'), dict) and run['repository'].get('full_name') == REPOSITORY
                    and isinstance(run.get('head_repository'), dict) and run['head_repository'].get('full_name') == REPOSITORY):
                runs.append(run)
        scanned += len(batch)
        if scanned > total:
            raise Gate('GitHub workflow inventory changed during pagination')
        if len(batch) < 100 or scanned == total:
            if scanned != total:
                raise Gate('Complete newest-run inventory is required')
            break
    else:
        raise Gate('GitHub workflow inventory exceeds its supported bounds')
    if not runs:
        raise Gate('No trusted exact-source Required application gates run exists')
    latest = max(runs, key=lambda run: run['id'])
    if latest.get('status') != 'completed' or latest.get('conclusion') != 'success':
        raise Gate('The latest trusted exact-source gate run must finish successfully')
    return latest['id']


def _read(client, route, **params):
    try:
        response = client.get('https://api.github.com/' + route, params=params)
        if response.status_code != 200 or len(response.content) > 2_097_152:
            raise Gate('Authorized bounded GitHub admission metadata is unavailable')
        result = strict_loads(response.content)
        if not isinstance(result, dict):
            raise Gate('GitHub admission metadata is malformed')
        return result
    except (httpx.HTTPError, TypeError, ValueError):
        raise Gate('GitHub admission metadata cannot be verified') from None


def _current_main(revision, fetch):
    repository = fetch(f'repos/{REPOSITORY}')
    current = fetch(f'repos/{REPOSITORY}/git/ref/heads/main')
    if (repository.get('full_name') != REPOSITORY or repository.get('default_branch') != 'main'
            or not isinstance(current.get('object'), dict) or current['object'].get('sha') != revision
            or current['object'].get('type') != 'commit'):
        raise Gate('Serverless mutation requires the current default main revision')


def verify_serverless_gates(path, revision, *, client=None):
    if client is None:
        headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN') or os.getenv('GH_ADMIN_TOKEN')
        if token:
            headers['Authorization'] = 'Bearer ' + token
        with httpx.Client(headers=headers, timeout=15, follow_redirects=False) as owned:
            return verify_serverless_gates(path, revision, client=owned)
    fetch = lambda route, **params: _read(client, route, **params)
    _current_main(revision, fetch)
    latest = select_latest_gate(revision, fetch)
    proof = platform.verify_gate_file(path, revision, client=client)
    if proof.get('run_id') != latest:
        raise Gate('Selected evidence does not belong to the newest trusted exact-source run')
    # Close the observable newer-run/main-ref window while full job proof loads.
    if select_latest_gate(revision, fetch) != latest:
        raise Gate('The newest trusted exact-source run changed during admission')
    _current_main(revision, fetch)
    return proof
