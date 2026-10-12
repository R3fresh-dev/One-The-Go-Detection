#!/usr/bin/env python3
"""Read-only AWS identity check before filling out a deployment configuration.

Credentials stay in the normal SDK provider chain. Only the confirmed account,
principal ARN and selected region are returned; this does not prove deploy rights.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:] = [entry for entry in sys.path if Path(entry).resolve() != ROOT / 'deploy']
sys.path.insert(0, str(ROOT))

import argparse
import contextlib
import json
import os
import re

from botocore.config import Config
from deploy.platform import CloudSession
from deploy.provenance import Gate, bounded_json


@contextlib.contextmanager
def identity_selection(alias):
    """Select one configured managed AWS identity without reading credentials."""
    if not alias:
        yield None
        return
    manifest_path = os.environ.get('OIC_MANIFEST_PATH')
    if not manifest_path:
        raise Gate('No managed identity manifest is configured; connect the AWS identity first')
    manifest = bounded_json(Path(manifest_path))
    if manifest.get('version') != 1 or not isinstance(manifest.get('connections'), list):
        raise Gate('Unsupported managed identity manifest; version 1 connections are required')
    matches = [row for row in manifest['connections'] if isinstance(row, dict)
               and row.get('alias') == alias and row.get('provider_kind') == 'aws']
    if len(matches) != 1:
        raise Gate('The requested AWS identity alias is not uniquely configured')
    config_file = matches[0].get('config_file')
    if not isinstance(config_file, str) or not config_file or not Path(config_file).is_file():
        raise Gate('The selected AWS identity is missing its configured SDK profile file')
    previous = {key: os.environ.get(key) for key in ('AWS_PROFILE', 'AWS_CONFIG_FILE')}
    os.environ.update(AWS_PROFILE=alias, AWS_CONFIG_FILE=config_file)
    try:
        yield alias
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def check(account, region, profile=None, identity=None):
    if not re.fullmatch(r'\d{12}', account):
        raise Gate('Supply the target twelve-digit AWS account ID')
    if not re.fullmatch(r'[a-z]{2}-[a-z]+-\d', region):
        raise Gate('Supply the target AWS region')
    if profile and identity:
        raise Gate('Select either --profile or --identity')
    with identity_selection(identity) as selected:
        aws = CloudSession(region, selected or profile)
        client = aws.client('sts', config=Config(connect_timeout=5, read_timeout=10,
                            retries={'mode': 'standard', 'total_max_attempts': 2}))
        try:
            caller = client.get_caller_identity()
        finally:
            client.close()
    if caller.get('Account') != account:
        raise Gate('AWS credential account differs from the requested deployment account')
    arn = caller.get('Arn', '')
    if not arn.startswith(f'arn:aws:') or f':{account}:' not in arn:
        raise Gate('AWS did not return a valid target-account principal ARN')
    return {'status': 'identity_verified', 'account': account, 'region': region,
            'principal_arn': arn, 'deployment_executed': False,
            'deployment_permissions_verified': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--account', required=True)
    parser.add_argument('--region', required=True)
    selectors = parser.add_mutually_exclusive_group()
    selectors.add_argument('--profile', help='Existing AWS SDK/SSO profile')
    selectors.add_argument('--identity', help='AWS alias in the managed identity manifest')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(check(args.account, args.region, args.profile, args.identity), indent=2))
        return 0
    except Exception as error:
        # SDK/provider exception text can contain credential-provider output.
        message = str(error) if isinstance(error, Gate) else type(error).__name__
        print(json.dumps({'status': 'blocked', 'reason': message,
                          'deployment_executed': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
