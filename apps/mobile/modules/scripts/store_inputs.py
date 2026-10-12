#!/usr/bin/env python3
"""Private fixed-path inputs and encrypted receipts for manual store Actions.

No cloud/store operation runs on import. Only ciphertext may become a public
Actions artifact. Genuine keys, source/store authority and accounts are external.
"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
import zipfile

REPOSITORY = 'R3fresh-dev/One-The-Go-Detection'
MAX_BUNDLE = 48 * 1024
MAX_RECORD = 65536
MAX_ENVELOPE = 512 * 1024
MAX_DOWNLOAD = 1024 * 1024
ENCRYPTED_NAME = 'store-receipts.json.enc'
FIELDS = {'schema_version', 'store_config', 'backend_config', 'backend_release', 'gate_evidence',
          'trusted_public_key', 'release_signing_key', 'platform_credentials', 'qa_approval'}
NAMES = {'config.json', 'backend-config.json', 'backend-release.json', 'gate-evidence.json',
         'trusted-public.pem', 'release-private.pem', 'google-service-account.json', 'apple-api-key.p8',
         'qa-approval.json', 'build-receipt.json', 'submission-receipt.json', 'output-receipt.json',
         'output-receipt.json.intent.json', 'arguments.json', 'scope.json', 'bundletool.jar', ENCRYPTED_NAME}
UUID = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}')
SHA = re.compile(r'[0-9a-f]{40}')


class Rejected(ValueError):
    pass


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def json_object(raw, limit=MAX_BUNDLE):
    if isinstance(raw, str):
        raw = raw.encode('utf-8')
    if not isinstance(raw, bytes) or not 0 < len(raw) <= limit:
        raise Rejected('Input size')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Rejected('Duplicate field')
            result[key] = value
        return result
    def invalid(_):
        raise Rejected('Nonfinite input')
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    def tree(item, depth=0):
        if depth > 24:
            raise Rejected('Input depth')
        if isinstance(item, dict):
            if len(item) > 256:
                raise Rejected('Object bound')
            for child in item.values():
                tree(child, depth + 1)
        elif isinstance(item, list):
            if len(item) > 512:
                raise Rejected('Array bound')
            for child in item:
                tree(child, depth + 1)
        elif isinstance(item, float) and not math.isfinite(item):
            raise Rejected('Nonfinite input')
        elif type(item) is int and abs(item) > 9007199254740991:
            raise Rejected('Unsafe integer')
    tree(value)
    if not isinstance(value, dict):
        raise Rejected('Object required')
    return value


def private_read(path, limit=MAX_RECORD):
    path = Path(path)
    if not path.is_absolute() or path.resolve(strict=True) != path:
        raise Rejected('Canonical private file selector required')
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(descriptor)
        valid_file(before, limit)
        raw = os.read(descriptor, limit + 1)
        after, named = os.fstat(descriptor), path.lstat()
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if len(raw) != before.st_size or any(getattr(before, key) != getattr(after, key) or
            getattr(after, key) != getattr(named, key) for key in fields):
            raise Rejected('Changed private file')
        return raw
    finally:
        os.close(descriptor)


def valid_file(metadata, limit):
    if (not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid()
        or metadata.st_mode & 0o077 or metadata.st_nlink != 1 or not 0 < metadata.st_size <= limit):
        raise Rejected('Private regular file required')


def runner_directory(path):
    path = Path(path)
    if not path.is_absolute() or path.resolve(strict=True) != path or any(ord(c) < 32 for c in str(path)):
        raise Rejected('Canonical runner directory required')
    metadata = path.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid() or metadata.st_mode & 0o022:
        raise Rejected('Owned runner directory required')
    return path


def new_directory(runner_temp):
    parent = runner_directory(runner_temp)
    name = 'otgd-store-' + secrets.token_hex(16)
    descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.mkdir(name, 0o700, dir_fd=descriptor)
        created = parent/name
        if parent.lstat().st_ino != os.fstat(descriptor).st_ino:
            raise Rejected('Runner directory replaced')
        return created
    finally:
        os.close(descriptor)


def put(directory, name, raw):
    if name not in NAMES or not isinstance(raw, bytes) or not raw:
        raise Rejected('Fixed nonempty file required')
    directory = Path(directory)
    if directory.resolve(strict=True) != directory:
        raise Rejected('Linked staging directory refused')
    metadata = directory.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o700:
        raise Rejected('Private staging directory required')
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        output = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=descriptor)
        with os.fdopen(output, 'wb') as target:
            target.write(raw)
    finally:
        os.close(descriptor)
    return Path(directory)/name


def scope_directory(directory, runner_temp):
    directory, parent = Path(directory), runner_directory(runner_temp)
    if directory.parent != parent or not re.fullmatch(r'otgd-store-[0-9a-f]{32}', directory.name):
        raise Rejected('Owned scope required')
    metadata = directory.lstat()
    if (not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid()
        or stat.S_IMODE(metadata.st_mode) != 0o700 or directory.resolve(strict=True) != directory):
        raise Rejected('Private scope required')
    return directory


def scope(directory, runner_temp):
    directory = scope_directory(directory, runner_temp)
    result = json_object(private_read(directory/'scope.json'))
    header = metadata(result.get('source_revision', ''), result.get('environment'), result.get('platform'))
    if set(result) != {*header, 'operation'} or any(result[name] != value for name, value in header.items()) or result['operation'] not in ('plan', 'build', 'submit', 'status', 'pack'):
        raise Rejected('Private scope metadata differs')
    return result


def store_module():
    module = sys.modules.get('store_release')
    if module is None:
        spec = importlib.util.spec_from_file_location('store_release', Path(__file__).with_name('store_release.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module


def key_bytes(key):
    if not isinstance(key, str):
        raise Rejected('External receipt key required')
    raw = base64.b64decode(key, validate=True)
    if len(raw) != 32 or base64.b64encode(raw).decode() != key:
        raise Rejected('Canonical external AES key required')
    return raw


def verified_record_bytes(raw, public_pem):
    """Verify original signed bytes before staging any reconciliation secret."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    helper = store_module()
    record = json_object(raw, MAX_RECORD)
    if (set(record) != {'schema_version', 'payload', 'payload_sha256', 'algorithm', 'signature'}
        or record['schema_version'] != '1.0.0' or record['algorithm'] != 'Ed25519'
        or not isinstance(record['payload'], dict) or record['payload_sha256'] != helper.sha256(record['payload'])
        or not isinstance(public_pem, str) or not 0 < len(public_pem.encode()) <= 8192):
        raise Rejected('Original signed reconciliation evidence required')
    public = serialization.load_pem_public_key(public_pem.encode())
    if not isinstance(public, Ed25519PublicKey):
        raise Rejected('Independent Ed25519 authority required')
    public.verify(base64.b64decode(record['signature'], validate=True), helper.cloud.canonical(record['payload']))
    return record['payload']


def reconciliation_preflight(value, package, key, revision, environment, platform, candidate, submission_id):
    if not UUID.fullmatch(submission_id) or package is None:
        raise Rejected('Fresh browser submission is unavailable without a durable fence')
    header, receipts = decrypt_receipts(package, key, environment, platform)
    if header['source_revision'] != revision or receipts['submission_intent'] is None or receipts['submission_receipt'] is not None:
        raise Rejected('Only exact original pending-intent reconciliation is supported')
    build = verified_record_bytes(receipts['build_receipt'], value['trusted_public_key'])
    pending = verified_record_bytes(receipts['submission_intent'], value['trusted_public_key'])
    config_sha = store_module().config_digest(value['store_config'])
    if (build.get('purpose') != 'mobile-store-build' or build.get('environment') != environment or build.get('platform') != platform
        or build.get('source_revision') != revision or build.get('config_sha256') != config_sha
        or build.get('build', {}).get('id') != candidate or build.get('public_release') is not False
        or pending.get('purpose') != 'mobile-store-submission-intent' or pending.get('source_revision') != revision
        or pending.get('platform') != platform or pending.get('config_sha256') != config_sha or pending.get('build_id') != candidate
        or pending.get('build_receipt_sha256') != hashlib.sha256(receipts['build_receipt']).hexdigest()):
        raise Rejected('Foreign reconciliation request refused')


def pack(config_path, build_receipt_path, intent_path, trusted_public_path, environment, platform,
         revision, runner_temp, key, *, submission_receipt_path=None):
    """Package existing operator-held proof only; no SDK/cloud/store call."""
    metadata(revision, environment, platform)
    helper = store_module()
    config_raw = private_read(config_path)
    configuration = helper.read_config(Path(config_path))
    if encode(configuration) != encode(json_object(config_raw, MAX_RECORD)) or config_raw != private_read(config_path):
        raise Rejected('Operator configuration changed')
    if configuration['environment'] != environment or configuration[platform] is None:
        raise Rejected('Operator configuration scope differs')
    public = private_read(trusted_public_path, 8192).decode()
    build_raw, intent_raw = private_read(build_receipt_path), private_read(intent_path)
    build, pending = verified_record_bytes(build_raw, public), verified_record_bytes(intent_raw, public)
    configuration_sha = helper.config_digest(configuration)
    candidate = build.get('build', {}).get('id', '')
    if (not UUID.fullmatch(candidate) or build.get('purpose') != 'mobile-store-build' or build.get('environment') != environment
        or build.get('source_revision') != revision or build.get('platform') != platform
        or build.get('config_sha256') != configuration_sha or build.get('public_release') is not False
        or pending.get('purpose') != 'mobile-store-submission-intent' or pending.get('source_revision') != revision
        or pending.get('platform') != platform or pending.get('config_sha256') != configuration_sha or pending.get('build_id') != candidate
        or pending.get('build_receipt_sha256') != hashlib.sha256(build_raw).hexdigest()):
        raise Rejected('Operator original build/intent proof differs')
    receipts = {'build_receipt': build_raw, 'submission_intent': intent_raw, 'submission_receipt': None}
    if submission_receipt_path is not None:
        submitted_raw = private_read(submission_receipt_path)
        submitted = verified_record_bytes(submitted_raw, public)
        if (submitted.get('purpose') != 'mobile-store-submission' or submitted.get('source_revision') != revision
            or submitted.get('platform') != platform or submitted.get('config_sha256') != configuration_sha
            or submitted.get('build_id') != candidate or submitted.get('public_release') is not False
            or submitted.get('build_receipt_sha256') != hashlib.sha256(build_raw).hexdigest()
            or submitted.get('submission_intent_sha256') != hashlib.sha256(intent_raw).hexdigest()
            or not UUID.fullmatch(submitted.get('submission_id', ''))):
            raise Rejected('Operator submitted outcome proof differs')
        receipts['submission_receipt'] = submitted_raw
    encrypted = encrypt_receipts(receipts, key, revision, environment, platform)
    # An environment secret cannot carry an oversized package; do not silently
    # drop proof fields to fit GitHub's 48KiB per-secret limit.
    if len(encrypted) > MAX_BUNDLE:
        raise Rejected('Protected receipt package exceeds the secret input bound')
    directory = new_directory(runner_temp)
    try:
        put(directory, 'scope.json', encode({**metadata(revision, environment, platform), 'operation': 'pack'}))
        return put(directory, ENCRYPTED_NAME, encrypted)
    except BaseException:
        cleanup(directory, runner_temp)
        raise


def metadata(revision, environment, platform):
    if not SHA.fullmatch(revision) or environment not in ('qa', 'prod') or platform not in ('android', 'ios'):
        raise Rejected('Receipt scope required')
    return {'schema_version': '1.0.0', 'repository': REPOSITORY, 'source_revision': revision,
            'environment': environment, 'platform': platform}


def encrypt_receipts(receipts, key, revision, environment, platform):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    header = metadata(revision, environment, platform)
    if set(receipts) != {'build_receipt', 'submission_receipt', 'submission_intent'} or not receipts['build_receipt']:
        raise Rejected('Exact receipt inventory required')
    for raw in receipts.values():
        if raw is not None:
            json_object(raw, MAX_RECORD)
    nonce = secrets.token_bytes(12)
    body = encode({name: base64.b64encode(raw).decode() if raw is not None else None for name, raw in receipts.items()})
    ciphertext = AESGCM(key_bytes(key)).encrypt(nonce, body, encode(header))
    result = encode({**header, 'nonce': base64.b64encode(nonce).decode(), 'ciphertext': base64.b64encode(ciphertext).decode()})
    if len(result) > MAX_ENVELOPE:
        raise Rejected('Encrypted receipt bound')
    return result


def decrypt_receipts(blob, key, environment, platform):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    envelope = json_object(blob, MAX_ENVELOPE)
    header = metadata(envelope.get('source_revision', ''), environment, platform)
    if set(envelope) != {*header, 'nonce', 'ciphertext'} or any(envelope[name] != value for name, value in header.items()):
        raise Rejected('Foreign encrypted receipt')
    nonce = base64.b64decode(envelope['nonce'], validate=True)
    ciphertext = base64.b64decode(envelope['ciphertext'], validate=True)
    if len(nonce) != 12 or len(ciphertext) < 17:
        raise Rejected('Invalid encrypted receipt')
    body = json_object(AESGCM(key_bytes(key)).decrypt(nonce, ciphertext, encode(header)), MAX_ENVELOPE)
    if set(body) != {'build_receipt', 'submission_receipt', 'submission_intent'} or body['build_receipt'] is None:
        raise Rejected('Receipt inventory required')
    values = {name: base64.b64decode(raw, validate=True) if raw is not None else None for name, raw in body.items()}
    for raw in values.values():
        if raw is not None:
            json_object(raw, MAX_RECORD)
    return header, values


def artifact_payload(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_DOWNLOAD:
        raise Rejected('Artifact download bound')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if (len(entries) != 1 or entries[0].filename != ENCRYPTED_NAME or entries[0].is_dir()
            or entries[0].flag_bits & 1 or stat.S_ISLNK(entries[0].external_attr >> 16)
            or not 0 < entries[0].file_size <= MAX_ENVELOPE):
            raise Rejected('Only fixed encrypted receipt artifact accepted')
        return archive.read(ENCRYPTED_NAME)


def response_bytes(response, limit):
    raw = bytearray()
    for part in response.iter_bytes(chunk_size=65536):
        if len(raw) + len(part) > limit:
            raise Rejected('Response download bound')
        raw.extend(part)
    return bytes(raw)


def download_receipts(artifact_id, token, environment, platform, *, client=None):
    import httpx
    if (not re.fullmatch(r'[1-9][0-9]{0,15}', str(artifact_id)) or int(artifact_id) > 9007199254740991
        or not isinstance(token, str) or not token or any(c.isspace() for c in token)):
        raise Rejected('Protected artifact selector required')
    own_client = client is None
    client = client or httpx.Client(timeout=30, follow_redirects=False)
    try:
        base = f'https://api.github.com/repos/{REPOSITORY}/actions/artifacts/{artifact_id}'
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        with client.stream('GET', base, headers=headers) as response:
            if response.status_code != 200:
                raise Rejected('Artifact metadata unavailable')
            value = json_object(response_bytes(response, MAX_RECORD), MAX_RECORD)
        run = value.get('workflow_run', {})
        revision = run.get('head_sha', '')
        if (type(value.get('id')) is not int or str(value['id']) != str(artifact_id) or value.get('expired') is not False
            or type(value.get('size_in_bytes')) is not int or not 0 < value['size_in_bytes'] <= MAX_DOWNLOAD
            or not SHA.fullmatch(revision) or run.get('head_branch') != 'main' or type(run.get('id')) is not int or not 0 < run['id'] <= 9007199254740991
            or value.get('name') != f'store-receipts-{environment}-{platform}-{revision}-{run["id"]}'):
            raise Rejected('Artifact metadata scope mismatch')
        with client.stream('GET', base + '/zip', headers=headers) as response:
            if response.status_code != 302:
                raise Rejected('Expected GitHub artifact redirect')
            location = response.headers.get('location', '')
        from urllib.parse import urlsplit
        parsed = urlsplit(location)
        if (parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port not in (None, 443)
            or not parsed.hostname or not any(parsed.hostname.endswith(suffix) for suffix in ('.blob.core.windows.net', '.actions.githubusercontent.com'))
            or parsed.fragment or len(location) > 8192):
            raise Rejected('Artifact destination refused')
        # Never forward the repository bearer credential to signed asset URLs.
        with client.stream('GET', location, headers={}) as response:
            if response.status_code != 200:
                raise Rejected('Artifact unavailable')
            raw = response_bytes(response, MAX_DOWNLOAD)
        blob = artifact_payload(raw)
        if json_object(blob, MAX_ENVELOPE).get('source_revision') != revision:
            raise Rejected('Artifact revision mismatch')
        return blob
    finally:
        if own_client:
            client.close()


def prepare(raw, operation, platform, environment, revision, runner_temp, *, role_arn='', candidate_build_id='',
            submission_id='', receipt_package=None, receipt_key=None):
    metadata(revision, environment, platform)
    if operation not in ('plan', 'build', 'submit', 'status'):
        raise Rejected('Operation required')
    value = json_object(raw)
    if set(value) != FIELDS or value['schema_version'] != '1.0.0' or not isinstance(value['store_config'], dict):
        raise Rejected('Closed protected input bundle required')
    config = json.loads(json.dumps(value['store_config']))
    if config.get('environment') != environment or config.get(platform) is None:
        raise Rejected('Selected store scope required')
    if operation == 'submit':
        # The browser runner is ephemeral. It may reconcile an already observed
        # provider UUID, never launch an initial upload with an undurable intent.
        reconciliation_preflight(value, receipt_package, receipt_key, revision, environment, platform, candidate_build_id, submission_id)
    if operation in ('status', 'submit'):
        if not UUID.fullmatch(candidate_build_id) or receipt_package is None:
            raise Rejected('Exact candidate receipt required')
    elif candidate_build_id or submission_id or receipt_package is not None:
        raise Rejected('Unexpected candidate selector')
    if submission_id and (operation not in ('submit', 'status') or not UUID.fullmatch(submission_id)):
        raise Rejected('Exact submission reconciliation required')
    account = region = ''
    if operation in ('build', 'submit'):
        key_bytes(receipt_key)
        if not all(isinstance(value[name], dict) for name in ('backend_config', 'backend_release', 'gate_evidence')):
            raise Rejected('Actual backend and gate inputs required')
        backend = value['backend_config']
        account, region = backend.get('account', ''), backend.get('region', '')
        if not isinstance(account, str) or not isinstance(region, str):
            raise Rejected('AWS account and region required')
        partition = 'aws-cn' if region.startswith('cn-') else 'aws-us-gov' if region.startswith('us-gov-') else 'aws'
        if (backend.get('environment') != environment or backend.get('releaseId') != revision
            or not re.fullmatch(r'[0-9]{12}', account) or not re.fullmatch(r'[a-z]{2}(?:-[a-z]+)+-[1-9][0-9]*', region)
            or not re.fullmatch(r'arn:' + partition + r':iam::' + account + r':role/[A-Za-z0-9+=,.@_/-]{1,512}', role_arn)
            or environment == 'prod' and not isinstance(value['qa_approval'], dict)):
            raise Rejected('Current intended AWS scope required')
    directory = new_directory(runner_temp)
    try:
        put(directory, 'scope.json', encode({**metadata(revision, environment, platform), 'operation': operation}))
        # External selectors must be null: only these owned fixed paths exist.
        if config.get('bundletool_jar') is not None:
            raise Rejected('External tool selector refused')
        config['bundletool_jar'] = str(directory/'bundletool.jar')
        for selected, field, name in (('android', 'service_account_key_path', 'google-service-account.json'), ('ios', 'api_key_path', 'apple-api-key.p8')):
            if config.get(selected) is not None:
                if config[selected].get(field) is not None:
                    raise Rejected('External credential selector refused')
                config[selected][field] = str(directory/name)
        put(directory, 'config.json', encode(config))
        helper = store_module()
        helper.read_config(directory/'config.json')
        arguments = [operation, '--config', str(directory/'config.json'), '--platform', platform]
        if operation != 'plan':
            public = value['trusted_public_key']
            if not isinstance(public, str) or not 0 < len(public.encode()) <= 8192:
                raise Rejected('External public authority required')
            put(directory, 'trusted-public.pem', public.encode())
            arguments += ['--trusted-public-key', str(directory/'trusted-public.pem')]
        if operation in ('status', 'submit'):
            header, receipts = decrypt_receipts(receipt_package, receipt_key, environment, platform)
            if operation == 'submit' and header['source_revision'] != revision:
                raise Rejected('Candidate belongs to another source')
            put(directory, 'build-receipt.json', receipts['build_receipt'])
            saved = helper.verify_signed_record(directory/'build-receipt.json', directory/'trusted-public.pem')
            if (saved.get('purpose') != 'mobile-store-build' or saved.get('platform') != platform
                or saved.get('source_revision') != header['source_revision'] or saved.get('environment') != environment
                or saved.get('config_sha256') != helper.config_digest(config)
                or saved.get('build', {}).get('id') != candidate_build_id):
                raise Rejected('Candidate receipt differs')
            arguments += ['--receipt', str(directory/'build-receipt.json')]
            if receipts['submission_receipt'] is not None:
                if operation == 'submit':
                    raise Rejected('Completed submission requires status, never resubmission')
                put(directory, 'submission-receipt.json', receipts['submission_receipt'])
                submitted = helper.verify_signed_record(directory/'submission-receipt.json', directory/'trusted-public.pem')
                if (submitted.get('purpose') != 'mobile-store-submission' or submitted.get('platform') != platform
                    or submitted.get('source_revision') != header['source_revision'] or submitted.get('config_sha256') != saved['config_sha256']
                    or submitted.get('build_receipt_sha256') != hashlib.sha256(receipts['build_receipt']).hexdigest()
                    or submission_id and submitted.get('submission_id') != submission_id):
                    raise Rejected('Submission receipt differs')
                arguments += ['--submission-receipt', str(directory/'submission-receipt.json')]
            if receipts['submission_intent'] is not None and operation == 'submit':
                if not submission_id:
                    raise Rejected('Pending submission requires exact reconciliation')
                put(directory, 'output-receipt.json.intent.json', receipts['submission_intent'])
                pending = helper.verify_signed_record(directory/'output-receipt.json.intent.json', directory/'trusted-public.pem')
                if (pending.get('purpose') != 'mobile-store-submission-intent' or pending.get('platform') != platform
                    or pending.get('source_revision') != revision or pending.get('config_sha256') != saved['config_sha256']
                    or pending.get('build_receipt_sha256') != hashlib.sha256(receipts['build_receipt']).hexdigest()
                    or pending.get('build_id') != candidate_build_id):
                    raise Rejected('Original intent differs')
                arguments += ['--submission-id', submission_id]
            elif submission_id and (operation == 'submit' or receipts['submission_receipt'] is None):
                raise Rejected('Reconciliation requires original intent')
        if operation in ('build', 'submit'):
            for name, filename in (('backend_config', 'backend-config.json'), ('backend_release', 'backend-release.json'), ('gate_evidence', 'gate-evidence.json')):
                put(directory, filename, encode(value[name]))
                arguments += ['--' + name.replace('_', '-'), str(directory/filename)]
            private = value['release_signing_key']
            if not isinstance(private, str) or not 0 < len(private.encode()) <= 8192:
                raise Rejected('External private release authority required')
            put(directory, 'release-private.pem', private.encode())
            helper.cloud.require_trusted_signer(directory/'release-private.pem', directory/'trusted-public.pem')
            arguments += ['--signing-key', str(directory/'release-private.pem'), '--output', str(directory/'output-receipt.json')]
            if environment == 'prod':
                put(directory, 'qa-approval.json', encode(value['qa_approval']))
                arguments += ['--qa-evidence', str(directory/'qa-approval.json')]
            if operation == 'submit':
                credential = value['platform_credentials']
                if not isinstance(credential, dict) or set(credential) != {'platform', 'content'} or credential['platform'] != platform:
                    raise Rejected('Selected platform credential required')
                if platform == 'android':
                    content = credential['content']
                    if (not isinstance(content, dict) or content.get('type') != 'service_account'
                        or content.get('token_uri') not in ('https://oauth2.googleapis.com/token', 'https://accounts.google.com/o/oauth2/token')
                        or not re.fullmatch(r'[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.iam\.gserviceaccount\.com', str(content.get('client_email', '')))
                        or not isinstance(content.get('private_key'), str)):
                        raise Rejected('Google service account credential required')
                    put(directory, 'google-service-account.json', encode(content))
                else:
                    content = credential['content']
                    if not isinstance(content, str) or '-----BEGIN PRIVATE KEY-----' not in content or len(content.encode()) > 65536:
                        raise Rejected('Apple API key required')
                    put(directory, 'apple-api-key.p8', content.encode())
        put(directory, 'arguments.json', encode({'arguments': arguments}))
        return {'directory': str(directory), 'account': account, 'region': region, 'role_arn': role_arn if account else ''}
    except BaseException:
        cleanup(directory, runner_temp)
        raise


def run(directory, runner_temp):
    saved = scope(directory, runner_temp)
    args = json_object(private_read(Path(directory)/'arguments.json'))
    arguments = args.get('arguments')
    if (set(args) != {'arguments'} or not isinstance(arguments, list) or not arguments
        or not all(isinstance(item, str) for item in arguments) or arguments[0] != saved['operation'] or len(arguments) % 2 != 1):
        raise Rejected('Owned argument inventory required')
    selectors = {'--config': 'config.json', '--backend-config': 'backend-config.json', '--backend-release': 'backend-release.json',
        '--gate-evidence': 'gate-evidence.json', '--trusted-public-key': 'trusted-public.pem', '--signing-key': 'release-private.pem',
        '--qa-evidence': 'qa-approval.json', '--receipt': 'build-receipt.json', '--submission-receipt': 'submission-receipt.json', '--output': 'output-receipt.json'}
    flags = dict(zip(arguments[1::2], arguments[2::2]))
    if len(flags) * 2 + 1 != len(arguments) or set(flags) - {*selectors, '--platform', '--submission-id'} or flags.get('--platform') != saved['platform'] or '--config' not in flags:
        raise Rejected('Fixed argument selectors required')
    for flag, value in flags.items():
        if flag in selectors and value != str(Path(directory)/selectors[flag]):
            raise Rejected('Foreign argument path')
        if flag == '--submission-id' and (saved['operation'] != 'submit' or not UUID.fullmatch(value)):
            raise Rejected('Foreign submission selector')
    if saved['operation'] == 'submit':
        if '--submission-id' not in flags or '--receipt' not in flags or '--trusted-public-key' not in flags:
            raise Rejected('Fresh browser submission is unavailable')
        pending = private_read(Path(directory)/'output-receipt.json.intent.json')
        original = private_read(Path(directory)/'build-receipt.json')
        public = private_read(Path(directory)/'trusted-public.pem', 8192).decode()
        record = verified_record_bytes(pending, public)
        build = verified_record_bytes(original, public)
        if record.get('purpose') != 'mobile-store-submission-intent' or record.get('build_id') != build.get('build', {}).get('id') or record.get('build_receipt_sha256') != hashlib.sha256(original).hexdigest():
            raise Rejected('Original reconciliation intent changed')
    os.umask(0o077)
    subprocess.run([sys.executable, str(Path(__file__).with_name('store_release.py')), *args['arguments']], check=True)


def seal(directory, runner_temp, key):
    saved = scope(directory, runner_temp)
    if saved['operation'] not in ('build', 'submit'):
        raise Rejected('Only mutation receipts are sealed')
    directory = Path(directory)
    helper = store_module()
    configuration = helper.read_config(directory/'config.json')
    configuration_sha = helper.config_digest(configuration)
    output, intent = directory/'output-receipt.json', directory/'output-receipt.json.intent.json'
    receipts = {'build_receipt': None, 'submission_receipt': None, 'submission_intent': None}
    if saved['operation'] == 'submit':
        receipts['build_receipt'] = private_read(directory/'build-receipt.json')
        built = helper.verify_signed_record(directory/'build-receipt.json', directory/'trusted-public.pem')
        if (built.get('purpose') != 'mobile-store-build' or built.get('source_revision') != saved['source_revision']
            or built.get('platform') != saved['platform'] or built.get('environment') != saved['environment']
            or built.get('config_sha256') != configuration_sha or built.get('public_release') is not False):
            raise Rejected('Original build receipt scope differs')
    if output.exists():
        value = helper.verify_signed_record(output, directory/'trusted-public.pem')
        purpose = 'mobile-store-build' if saved['operation'] == 'build' else 'mobile-store-submission'
        if (value.get('purpose') != purpose or value.get('source_revision') != saved['source_revision'] or value.get('platform') != saved['platform']
            or value.get('config_sha256') != configuration_sha or value.get('public_release') is not False
            or saved['operation'] == 'build' and value.get('environment') != saved['environment']):
            raise Rejected('Owned signed output receipt required')
        if saved['operation'] == 'submit' and (value.get('build_receipt_sha256') != hashlib.sha256(receipts['build_receipt']).hexdigest()
            or value.get('build_id') != built['build']['id']):
            raise Rejected('Submission output differs from original build')
        receipts['build_receipt' if saved['operation'] == 'build' else 'submission_receipt'] = private_read(output)
    if intent.exists():
        value = helper.verify_signed_record(intent, directory/'trusted-public.pem')
        if (saved['operation'] != 'submit' or value.get('purpose') != 'mobile-store-submission-intent'
            or value.get('source_revision') != saved['source_revision'] or value.get('platform') != saved['platform']
            or value.get('config_sha256') != configuration_sha or value.get('build_id') != built['build']['id']
            or value.get('build_receipt_sha256') != hashlib.sha256(receipts['build_receipt']).hexdigest()):
            raise Rejected('Owned signed intent required')
        receipts['submission_intent'] = private_read(intent)
        if receipts['submission_receipt'] is not None:
            submitted = json_object(receipts['submission_receipt'], MAX_RECORD)['payload']
            if submitted.get('submission_intent_sha256') != hashlib.sha256(receipts['submission_intent']).hexdigest():
                raise Rejected('Submission output differs from original intent')
    elif receipts['submission_receipt'] is not None:
        raise Rejected('Submission output requires original signed intent')
    if receipts['build_receipt'] is None or saved['operation'] == 'submit' and receipts['submission_receipt'] is None and receipts['submission_intent'] is None:
        return None
    return put(directory, ENCRYPTED_NAME, encrypt_receipts(receipts, key, saved['source_revision'], saved['environment'], saved['platform']))


def cleanup(directory, runner_temp):
    directory = scope_directory(directory, runner_temp)
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        names = os.listdir(descriptor)
        if any(name not in NAMES for name in names):
            raise Rejected('Unexpected private scope entry')
        for name in names:
            valid_file(os.stat(name, dir_fd=descriptor, follow_symlinks=False), MAX_DOWNLOAD * 512)
        for name in names:
            os.unlink(name, dir_fd=descriptor)
    finally:
        os.close(descriptor)
    directory.rmdir()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run', 'seal', 'cleanup', 'pack'))
    parser.add_argument('--operation', choices=('plan', 'build', 'submit', 'status'))
    parser.add_argument('--platform', choices=('android', 'ios'))
    parser.add_argument('--environment', choices=('qa', 'prod'))
    parser.add_argument('--revision')
    parser.add_argument('--candidate-build-id', default='')
    parser.add_argument('--submission-id', default='')
    parser.add_argument('--receipt-artifact-id', default='')
    parser.add_argument('--directory', type=Path)
    for name in ('config', 'build-receipt', 'submission-intent', 'trusted-public-key', 'submission-receipt'):
        parser.add_argument('--' + name, type=Path)
    args = parser.parse_args(argv)
    prepared = None
    try:
        parent = os.environ['RUNNER_TEMP']
        result = {}
        if args.action == 'prepare':
            if args.operation == 'submit' and not UUID.fullmatch(args.submission_id):
                raise Rejected('Fresh browser submission is unavailable')
            protected_package = os.environ.get('STORE_RECEIPT_PACKAGE', '')
            if args.receipt_artifact_id and protected_package:
                raise Rejected('Choose one exact receipt handoff')
            if protected_package:
                package = encode(json_object(protected_package, MAX_BUNDLE))
            else:
                package = download_receipts(args.receipt_artifact_id, os.environ.get('GITHUB_TOKEN', ''), args.environment, args.platform) if args.receipt_artifact_id else None
            result = prepare(os.environ.get('STORE_RELEASE_INPUTS', ''), args.operation, args.platform, args.environment,
                args.revision, parent, role_arn=os.environ.get('STORE_AWS_ROLE_ARN', ''), candidate_build_id=args.candidate_build_id,
                submission_id=args.submission_id, receipt_package=package, receipt_key=os.environ.get('STORE_RECEIPT_KEY'))
            prepared = result['directory']
        elif args.action == 'run':
            run(args.directory, parent)
        elif args.action == 'seal':
            sealed = seal(args.directory, parent, os.environ.get('STORE_RECEIPT_KEY'))
            result = {'sealed': 'true' if sealed else 'false', 'encrypted_artifact': str(sealed) if sealed else ''}
        elif args.action == 'pack':
            target = pack(args.config, args.build_receipt, args.submission_intent, args.trusted_public_key,
                args.environment, args.platform, args.revision, parent, os.environ.get('STORE_RECEIPT_KEY'),
                submission_receipt_path=args.submission_receipt)
            print('Encrypted operator receipt package: ' + str(target))
        else:
            cleanup(args.directory, parent)
        if result and os.environ.get('GITHUB_OUTPUT'):
            descriptor = os.open(os.environ['GITHUB_OUTPUT'], os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW | os.O_NONBLOCK)
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid() or metadata.st_nlink != 1:
                os.close(descriptor)
                raise Rejected('Owned runner output required')
            with os.fdopen(descriptor, 'a') as output:
                for name, value in result.items():
                    if '\n' in value or '\r' in value:
                        raise Rejected('Output encoding refused')
                    output.write(name + '=' + value + '\n')
        print('Protected store inputs completed; no secret or receipt contents are logged.')
        return 0
    except Exception:
        if prepared is not None:
            try:
                cleanup(prepared, os.environ['RUNNER_TEMP'])
            except Exception:
                pass  # Refuse unsafe replacement; ephemeral-runner disposal remains necessary.
        print('Store inputs refused: genuine protected scope, bounded files or authenticated receipt validation failed.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
