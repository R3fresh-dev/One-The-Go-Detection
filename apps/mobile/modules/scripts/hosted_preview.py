#!/usr/bin/env python3
"""Inspect canonical hosted guest artifacts, or explicitly upload to Appetize.

Preparation requires a clean source checkout and the local hosted-preview build
environment. Review is offline. Upload creates an initially disabled build with
authenticated permissions; credentials are read only from APPETIZE_API_TOKEN.
The manifest is integrity evidence, not signed provenance or device qualification.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import plistlib
import re
import stat
import struct
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[4]
MOBILE = ROOT / 'apps/mobile'
API = 'https://api.appetize.io/v1/apps'
BUNDLE = 'dev.r3fresh.otgd.local'
MAX_BYTES = 256 * 1024 * 1024
MAX_EXPANDED = 1024 * 1024 * 1024
PERMISSIONS = ('run', 'networkProxy', 'networkIntercept', 'debugLog', 'adbConnect', 'androidPackageManager')
BUILD_ENV = {'APP_ENV': 'local', 'EXPO_PUBLIC_HOSTED_PREVIEW': 'true', 'EXPO_NO_DOTENV': '1',
             'EXPO_PUBLIC_API_URL': 'https://unavailable.invalid',
             'EXPO_PUBLIC_OAUTH_ISSUER': 'https://unavailable.invalid',
             'EXPO_PUBLIC_OAUTH_CLIENT_ID': 'otgd-hosted-fictional'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result


def read_bounded(path, limit):
    with Path(path).open('rb') as source:
        value = source.read(limit + 1)
    if not value or len(value) > limit:
        raise ValueError('Empty or oversized artifact metadata')
    return value


def zip_entries(archive):
    entries = archive.infolist()
    names = [entry.filename for entry in entries]
    if not entries or len(entries) > 20000 or len(names) != len(set(names)) or sum(e.file_size for e in entries) > MAX_EXPANDED:
        raise ValueError('Empty, duplicate or oversized archive')
    for entry in entries:
        name = entry.filename
        if '\\' in name or '\x00' in name or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:
            raise ValueError('Unsafe archive path')
        if stat.S_ISLNK(entry.external_attr >> 16) or entry.flag_bits & 1:
            raise ValueError('Symlink or encrypted archive entry')
    return names


def read_entry(archive, name, limit):
    entry = archive.getinfo(name)
    if entry.is_dir() or entry.file_size > limit:
        raise ValueError('Artifact metadata exceeds inspection bounds')
    return archive.read(name)


def simulator_binary(data):
    """Inspect the actual ARM64 Mach-O LC_BUILD_VERSION simulator platform."""
    if len(data) < 32 or data[:4] != b'\xcf\xfa\xed\xfe':
        raise ValueError('Expected a thin ARM64 iOS Simulator executable')
    _, cpu, _, filetype, count, commands_size, _, _ = struct.unpack_from('<8I', data)
    if cpu != 0x0100000C or filetype != 2 or count > 2048 or commands_size > 128 * 1024 or 32 + commands_size > len(data):
        raise ValueError('Unsupported or truncated simulator executable')
    offset, platforms = 32, []
    for _ in range(count):
        if offset + 8 > 32 + commands_size:
            raise ValueError('Truncated Mach-O command')
        command, size = struct.unpack_from('<2I', data, offset)
        if size < 8 or offset + size > 32 + commands_size:
            raise ValueError('Invalid Mach-O command')
        if command == 0x32:
            if size < 24:
                raise ValueError('Invalid build-version command')
            platforms.append(struct.unpack_from('<I', data, offset + 8)[0])
        offset += size
    if offset != 32 + commands_size or platforms != [7]:
        raise ValueError('Executable must target only iOS Simulator')


def binary_xml(data):
    """Read bounded Android binary-XML attributes needed for local APK identity."""
    if len(data) < 8 or struct.unpack_from('<HHI', data) != (3, 8, len(data)):
        raise ValueError('Expected an Android binary manifest')
    strings, elements, position = None, [], 8
    while position < len(data):
        if position + 8 > len(data):
            raise ValueError('Truncated manifest chunk')
        kind, header, size = struct.unpack_from('<HHI', data, position)
        if header < 8 or size < header or position + size > len(data):
            raise ValueError('Invalid manifest chunk')
        chunk = data[position:position + size]
        if kind == 1:
            if strings is not None or header < 28:
                raise ValueError('Invalid manifest string pool')
            count, _, flags, start, _ = struct.unpack_from('<5I', chunk, 8)
            if count > 10000 or header + count * 4 > size or start < header + count * 4 or start >= size:
                raise ValueError('Invalid manifest string table')
            strings = []
            for i in range(count):
                offset = start + struct.unpack_from('<I', chunk, header + 4 * i)[0]
                if offset >= size:
                    raise ValueError('Invalid manifest string offset')
                if flags & 0x100:
                    def length8(at):
                        if at >= size:
                            raise ValueError('Truncated manifest string length')
                        value = chunk[at]
                        if value & 0x80:
                            if at + 1 >= size:
                                raise ValueError('Truncated manifest string length')
                            return ((value & 0x7f) << 8) | chunk[at + 1], at + 2
                        return value, at + 1
                    _, offset = length8(offset)
                    length, offset = length8(offset)
                    if offset + length >= size or chunk[offset + length] != 0:
                        raise ValueError('Unterminated manifest string')
                    strings.append(chunk[offset:offset + length].decode('utf-8'))
                else:
                    if offset + 2 > size:
                        raise ValueError('Truncated manifest UTF16 string')
                    length = struct.unpack_from('<H', chunk, offset)[0]
                    offset += 2
                    if length & 0x8000:
                        if offset + 2 > size:
                            raise ValueError('Truncated manifest UTF16 length')
                        length = ((length & 0x7fff) << 16) | struct.unpack_from('<H', chunk, offset)[0]
                        offset += 2
                    if offset + 2 * length + 2 > size or chunk[offset + 2 * length:offset + 2 * length + 2] != b'\0\0':
                        raise ValueError('Unterminated manifest UTF16 string')
                    strings.append(chunk[offset:offset + 2 * length].decode('utf-16-le'))
        elif kind == 0x102:
            if strings is None or header < 16 or header + 20 > size:
                raise ValueError('Invalid manifest element')
            _, name, attr_start, attr_size, attr_count = struct.unpack_from('<IIHHH', chunk, header)
            start = header + attr_start
            if name >= len(strings) or attr_start < 20 or attr_size < 20 or start + attr_size * attr_count > size:
                raise ValueError('Invalid manifest attributes')
            attributes = {}
            for i in range(attr_count):
                at = start + i * attr_size
                _, key, raw, typed_size, _, value_type, value = struct.unpack_from('<IIIHBBI', chunk, at)
                if key >= len(strings) or typed_size != 8 or strings[key] in attributes:
                    raise ValueError('Ambiguous manifest attribute')
                if value_type == 0x12:  # Res_value::TYPE_INT_BOOLEAN (aapt2)
                    if value not in (0, 0xffffffff):
                        raise ValueError('Noncanonical manifest boolean')
                    value = value == 0xffffffff
                    if raw != 0xffffffff and (raw >= len(strings) or strings[raw] != ('true' if value else 'false')):
                        raise ValueError('Conflicting manifest boolean text')
                elif raw != 0xffffffff or value_type == 3:
                    index = raw if raw != 0xffffffff else value
                    if index >= len(strings):
                        raise ValueError('Invalid manifest value')
                    value = strings[index]
                attributes[strings[key]] = value
            elements.append((strings[name], attributes))
        position += size
    if position != len(data):
        raise ValueError('Invalid manifest length')
    return elements


def inspect_artifact(path, platform, data=None):
    data = read_bounded(path, MAX_BYTES) if data is None else data
    if len(data) <= 0 or len(data) > MAX_BYTES:
        raise ValueError('Artifact must be nonempty and at most 256 MiB')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = zip_entries(archive)
        if platform == 'ios':
            roots = {n.split('/')[0] for n in names if not n.startswith('__MACOSX/')}
            if len(roots) != 1 or not next(iter(roots)).endswith('.app'):
                raise ValueError('Expected a single top-level simulator .app, not an IPA')
            app = next(iter(roots))
            info = plistlib.loads(read_entry(archive, app + '/Info.plist', 64 * 1024))
            executable = info.get('CFBundleExecutable', '')
            if info.get('CFBundleIdentifier') != BUNDLE or info.get('CFBundleSupportedPlatforms') != ['iPhoneSimulator'] or info.get('MinimumOSVersion') != '16.4' or info.get('OTGDHostedPreview') is not True or not re.fullmatch(r'[A-Za-z0-9_. -]{1,128}', executable):
                raise ValueError('Expected the canonical local iOS Simulator app')
            with archive.open(app + '/' + executable) as binary:
                simulator_binary(binary.read(128 * 1024 + 32))
            if archive.getinfo(app + '/main.jsbundle').file_size < 1024:
                raise ValueError('Missing standalone JavaScript bundle')
            return {'bundle_identifier': BUNDLE, 'architectures': ['arm64'], 'platform': 'ios', 'file_type': 'zip'}
        if platform != 'android':
            raise ValueError('Unsupported hosted platform')
        elements = binary_xml(read_entry(archive, 'AndroidManifest.xml', 1024 * 1024))
        manifests = [attributes for name, attributes in elements if name == 'manifest']
        applications = [attributes for name, attributes in elements if name == 'application']
        sdk_versions = [attributes for name, attributes in elements if name == 'uses-sdk']
        hosted_markers = [attributes for name, attributes in elements if name == 'meta-data' and attributes.get('name') == 'dev.r3fresh.otgd.HOSTED_PREVIEW']
        if len(manifests) != 1 or manifests[0].get('package') != BUNDLE or len(applications) != 1 or applications[0].get('debuggable', False) is not False:
            raise ValueError('Expected the nondebuggable canonical local Android app')
        if len(sdk_versions) != 1 or str(sdk_versions[0].get('minSdkVersion')) != '24' or str(sdk_versions[0].get('targetSdkVersion')) != '36':
            raise ValueError('APK differs from the reviewed Android minimum/target SDK')
        if len(hosted_markers) != 1 or hosted_markers[0].get('value') is not True:
            raise ValueError('APK does not contain the hosted guest build marker')
        if archive.getinfo('assets/index.android.bundle').file_size < 1024:
            raise ValueError('Missing standalone Android JavaScript bundle')
        for abi in ('arm64-v8a', 'x86_64'):
            libraries = [n for n in names if n.startswith('lib/' + abi + '/') and n.endswith('.so')]
            if not libraries:
                raise ValueError('Missing required Android native architecture')
            with archive.open(libraries[0]) as library:
                header = library.read(64)
            if len(header) != 64 or header[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', header, 18)[0] != (183 if abi == 'arm64-v8a' else 62):
                raise ValueError('Native ELF library differs from its claimed architecture')
        return {'bundle_identifier': BUNDLE, 'architectures': ['arm64-v8a', 'x86_64'], 'platform': 'android', 'file_type': 'apk'}


def source_inventory():
    scope = ['apps/mobile', '.github/workflows/hosted-native-preview.yml', 'scripts/verify-swift-xctest.py']
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all', '--', *scope], cwd=ROOT, text=True)
    if status.strip():
        raise ValueError('Hosted preview preparation requires a clean committed source checkout')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    paths = subprocess.check_output(['git', 'ls-files', '-z', '--', *scope], cwd=ROOT).decode().split('\0')
    inventory = [{'path': path, 'sha256': digest((ROOT/path).read_bytes())} for path in sorted(paths) if path]
    if not re.fullmatch('[0-9a-f]{40}', revision) or not inventory:
        raise ValueError('Missing exact committed source inventory')
    return revision, inventory


def prepare(path, platform, output):
    if any(os.environ.get(key) != value for key, value in BUILD_ENV.items()):
        raise ValueError('Set the complete local hosted-preview build environment; dotenv must be disabled')
    config = json.loads(subprocess.check_output(['node', 'node_modules/expo/bin/cli', 'config', '--type', 'public', '--json'], cwd=MOBILE))
    if config.get('extra', {}).get('environment') != 'local' or config.get('extra', {}).get('hostedPreview') is not True:
        raise ValueError('The canonical application did not enable its local hosted guest guard')
    revision, inventory = source_inventory()
    artifact = read_bounded(path, MAX_BYTES)
    inspection = inspect_artifact(path, platform, artifact)
    manifest = {'format': 1, 'source_revision': revision, 'source_files': inventory,
                'source_inventory_sha256': digest(canonical(inventory)), 'build_environment': BUILD_ENV,
                'hosted_preview': True, 'configuration': 'Release', 'qualification': 'fictional-guest-ui-only',
                'artifact_name': Path(path).name, 'artifact_sha256': digest(artifact),
                'artifact_bytes': len(artifact), **inspection}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def review(path, manifest_path):
    manifest = json.loads(read_bounded(manifest_path, 256 * 1024), object_pairs_hook=unique_object)
    if manifest.get('format') != 1 or type(manifest.get('format')) is not int or manifest.get('hosted_preview') is not True or manifest.get('build_environment') != BUILD_ENV or manifest.get('configuration') != 'Release' or manifest.get('qualification') != 'fictional-guest-ui-only':
        raise ValueError('Only canonical local hosted guest artifacts are accepted')
    if not re.fullmatch('[0-9a-f]{40}', str(manifest.get('source_revision', ''))):
        raise ValueError('Missing exact source revision')
    files = manifest.get('source_files')
    if not isinstance(files, list) or not files or len(files) > 2000 or digest(canonical(files)) != manifest.get('source_inventory_sha256'):
        raise ValueError('Source inventory differs from its manifest digest')
    seen = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {'path', 'sha256'} or not isinstance(entry['path'], str) or not re.fullmatch('[0-9a-f]{64}', str(entry['sha256'])):
            raise ValueError('Invalid source inventory')
        name = entry['path']
        if name in seen or '\\' in name or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:
            raise ValueError('Unsafe or duplicate source inventory path')
        seen.add(name)
    if not {'apps/mobile/App.tsx', 'apps/mobile/app.config.ts', 'apps/mobile/package-lock.json'} <= seen:
        raise ValueError('Manifest lacks canonical application sources')
    artifact = read_bounded(path, MAX_BYTES)
    inspection = inspect_artifact(path, manifest.get('platform'), artifact)
    if any(manifest.get(key) != value for key, value in inspection.items()) or manifest.get('artifact_name') != Path(path).name or type(manifest.get('artifact_bytes')) is not int or manifest['artifact_bytes'] != len(artifact) or manifest.get('artifact_sha256') != digest(artifact):
        raise ValueError('Actual artifact differs from inspected build manifest')
    return {**manifest, 'artifact': str(path)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        raise ValueError('Appetize redirects are refused to protect the API credential')


def upload(plan, token, opener=None):
    if not token or any(ord(c) < 33 or ord(c) > 126 for c in token):
        raise ValueError('Set APPETIZE_API_TOKEN through the secret manager')
    artifact = read_bounded(plan['artifact'], MAX_BYTES)
    if len(artifact) != plan['artifact_bytes'] or digest(artifact) != plan['artifact_sha256']:
        raise ValueError('Artifact changed after review')
    boundary = 'otgd-preview-' + uuid.uuid4().hex
    fields = {'platform': plan['platform'], 'fileType': plan['file_type'], 'disabled': 'true', 'timeout': '120',
              'note': 'Fictional guest preview; source ' + plan['source_revision']}
    fields.update({'appPermissions.' + permission: 'authenticated' for permission in PERMISSIONS})
    body = [f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode() for name, value in fields.items()]
    filename = 'hosted-preview.' + plan['file_type']
    body += [f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode(), artifact, f'\r\n--{boundary}--\r\n'.encode()]
    request = urllib.request.Request(API, data=b''.join(body), method='POST', headers={'X-API-KEY': token, 'Content-Type': 'multipart/form-data; boundary=' + boundary})
    try:
        with (opener or urllib.request.build_opener(NoRedirect())).open(request, timeout=180) as response:
            if response.status not in (200, 201):
                raise ValueError('Unexpected Appetize upload status')
            payload_bytes = response.read(1024 * 1024 + 1)
            if len(payload_bytes) > 1024 * 1024:
                raise ValueError('Appetize response exceeds safe bounds')
            payload = json.loads(payload_bytes, object_pairs_hook=unique_object)
    except urllib.error.HTTPError as error:
        raise ValueError('Appetize upload failed with HTTP ' + str(error.code) + '; response body omitted') from None
    except urllib.error.URLError:
        raise ValueError('Appetize is unreachable; check network and TLS trust') from None
    except (json.JSONDecodeError, UnicodeError):
        raise ValueError('Invalid Appetize response; response body omitted') from None
    build = payload.get('publicKey') if isinstance(payload, dict) else None
    if not isinstance(build, str) or not re.fullmatch('[A-Za-z0-9_-]{1,128}', build):
        raise ValueError('No valid Appetize build ID; inspect the organization dashboard')
    return {'uploaded': True, 'build_identifier': build, 'disabled_requested': True, 'permissions_requested': 'authenticated',
            'settings_verified_live': False, 'organization_launch_url': 'https://appetize.io/apps/' + plan['platform'] + '/' + urllib.parse.quote(BUNDLE, safe=''),
            'next_step': 'Sign in, verify authenticated permissions in the organization dashboard, then enable and launch the build.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'review', 'upload'])
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--platform', choices=['ios', 'android'])
    args = parser.parse_args()
    try:
        if args.mode == 'prepare':
            if not args.platform:
                raise ValueError('Preparation requires --platform')
            result = prepare(args.artifact, args.platform, args.manifest)
            result = {key: result[key] for key in ('source_revision', 'artifact_sha256', 'platform', 'artifact_name')}
        else:
            plan = review(args.artifact, args.manifest)
            result = upload(plan, os.environ.get('APPETIZE_API_TOKEN', '')) if args.mode == 'upload' else {'mode': 'review-only', 'network_requests': 0, 'source_revision': plan['source_revision'], 'artifact_sha256': plan['artifact_sha256'], 'platform': plan['platform'], 'upload_target': API, 'initially_disabled': True, 'permissions': 'authenticated'}
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError, IndexError, struct.error, zipfile.BadZipFile, plistlib.InvalidFileException, subprocess.CalledProcessError):
        # Metadata and vendor error bodies may be untrusted; never print them or credentials.
        raise SystemExit('Hosted preview rejected: artifact, manifest, build environment or upload validation failed. No credential or vendor response body is printed.') from None


if __name__ == '__main__':
    main()
