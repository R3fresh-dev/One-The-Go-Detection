"""Offline native preview artifact and credential-boundary regression checks."""
import importlib.util
import json
from pathlib import Path
import plistlib
import stat
import struct
import tempfile
import unittest
import warnings
from unittest.mock import patch
import urllib.error
import zipfile


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('hosted_preview', ROOT/'apps/mobile/modules/scripts/hosted_preview.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


def macho(platform=7, cpu=0x0100000c):
    return struct.pack('<8I', 0xfeedfacf, cpu, 0, 2, 1, 24, 0, 0) + struct.pack('<6I', 0x32, 24, platform, 0, 0, 0)


def elf(cpu):
    header = bytearray(64)
    header[:6] = b'\x7fELF\x02\x01'
    struct.pack_into('<H', header, 18, cpu)
    return bytes(header)


def android_manifest(package=preview.BUNDLE, debuggable=False, hosted=True):
    # Android ResourceTypes.h string-pool/start-element wire fixture, independent
    # of the actual Expo build. Real APK execution remains a separate CI check.
    strings = ['manifest', 'package', package, 'application', 'debuggable', 'uses-sdk', 'minSdkVersion', 'targetSdkVersion', 'meta-data', 'name', 'value', 'dev.r3fresh.otgd.HOSTED_PREVIEW']
    encoded, offsets = b'', []
    for value in strings:
        offsets.append(len(encoded))
        data = value.encode()
        encoded += bytes([len(value), len(data)]) + data + b'\0'
    start = 28 + len(strings) * 4
    pool = struct.pack('<HHI5I', 1, 28, start + len(encoded), len(strings), 0, 0x100, start, 0)
    pool += struct.pack('<'+'I'*len(strings), *offsets) + encoded
    def element(name, attributes):
        return (struct.pack('<HHIII', 0x102, 16, 36+20*len(attributes), 1, 0xffffffff)
                + struct.pack('<II6H', 0xffffffff, name, 20, 20, len(attributes), 0, 0, 0)
                + b''.join(struct.pack('<IIIHBBI', 0xffffffff, attribute, raw, 8, 0, dtype, value) for attribute, raw, dtype, value in attributes))
    body = pool + element(0, [(1, 2, 3, 2)]) + element(3, [(4, 0xffffffff, 0x12, int(debuggable))]) + element(5, [(6, 0xffffffff, 0x10, 24), (7, 0xffffffff, 0x10, 36)])
    if hosted:
        body += element(8, [(9, 11, 3, 11), (10, 0xffffffff, 0x12, 1)])
    return struct.pack('<HHI', 3, 8, 8 + len(body)) + body


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)

    def ios(self, **changes):
        info = {'CFBundleIdentifier': preview.BUNDLE, 'CFBundleSupportedPlatforms': ['iPhoneSimulator'], 'CFBundleExecutable': 'OneTheGo', 'MinimumOSVersion': '16.4', 'OTGDHostedPreview': True}
        info.update(changes.pop('info', {}))
        entries = {'OneTheGo.app/Info.plist': plistlib.dumps(info), 'OneTheGo.app/OneTheGo': macho(), 'OneTheGo.app/main.jsbundle': b'j'*1024}
        entries.update(changes)
        return self.archive('guest.zip', entries)

    def android(self, **changes):
        entries = {'AndroidManifest.xml': android_manifest(), 'assets/index.android.bundle': b'j'*1024,
                   'lib/arm64-v8a/libapp.so': elf(183), 'lib/x86_64/libapp.so': elf(62)}
        entries.update(changes)
        return self.archive('guest.apk', entries)

    def archive(self, name, entries):
        path = self.base/name
        with zipfile.ZipFile(path, 'w') as archive:
            for entry, data in entries.items():
                if data is not None:
                    archive.writestr(entry, data)
        return path

    def manifest(self, path, platform='ios'):
        files = [{'path': value, 'sha256': 'a'*64} for value in ['apps/mobile/App.tsx', 'apps/mobile/app.config.ts', 'apps/mobile/package-lock.json']]
        result = {'format': 1, 'hosted_preview': True, 'build_environment': preview.BUILD_ENV,
                  'source_revision': 'a'*40, 'source_files': files, 'source_inventory_sha256': preview.digest(preview.canonical(files)),
                  'configuration': 'Release', 'qualification': 'fictional-guest-ui-only',
                  'artifact_name': path.name, 'artifact_bytes': path.stat().st_size, 'artifact_sha256': preview.digest(path.read_bytes()),
                  **preview.inspect_artifact(path, platform)}
        manifest = self.base/'manifest.json'
        manifest.write_text(json.dumps(result))
        return manifest, result

    def test_ios_and_android_bundles_are_inspected(self):
        for platform, path in [('ios', self.ios()), ('android', self.android())]:
            with self.subTest(platform=platform):
                manifest, _ = self.manifest(path, platform)
                self.assertEqual(preview.review(path, manifest)['platform'], platform)

    def test_ios_device_prod_platform_and_missing_bundle_are_rejected(self):
        variants = [dict(info={'CFBundleIdentifier': 'dev.r3fresh.otgd'}), dict(info={'CFBundleSupportedPlatforms': ['iPhoneOS']}), dict(info={'MinimumOSVersion': '15.0'}), dict(info={'OTGDHostedPreview': False}),
                    {'OneTheGo.app/OneTheGo': macho(platform=2)}, {'OneTheGo.app/OneTheGo': macho(cpu=0x01000007)},
                    {'OneTheGo.app/OneTheGo': macho()[:40]}, {'OneTheGo.app/main.jsbundle': None}]
        for change in variants:
            with self.subTest(change=change), self.assertRaises((ValueError, KeyError)):
                preview.inspect_artifact(self.ios(**change), 'ios')

    def test_android_prod_debug_manifest_truncation_and_abi_mismatch_are_rejected(self):
        variants = [{'AndroidManifest.xml': android_manifest('dev.r3fresh.otgd')}, {'AndroidManifest.xml': android_manifest(debuggable=True)}, {'AndroidManifest.xml': android_manifest(hosted=False)},
                    {'AndroidManifest.xml': android_manifest()[:40]}, {'lib/x86_64/libapp.so': None},
                    {'lib/x86_64/libapp.so': elf(183)}, {'assets/index.android.bundle': b''}]
        for change in variants:
            with self.subTest(change=change), self.assertRaises((ValueError, KeyError)):
                preview.inspect_artifact(self.android(**change), 'android')

    def test_unsafe_paths_duplicates_symlinks_and_expansion_limits_are_rejected(self):
        for name in ['../escape', '/escape', 'OneTheGo.app/../escape', 'OneTheGo.app\\escape']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                preview.inspect_artifact(self.ios(**{name: b'x'}), 'ios')
        path = self.ios()
        with zipfile.ZipFile(path, 'a') as archive:
            entry = zipfile.ZipInfo('OneTheGo.app/link')
            entry.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(entry, b'outside')
        with self.assertRaises(ValueError):
            preview.inspect_artifact(path, 'ios')
        with patch.object(preview, 'MAX_EXPANDED', 8), self.assertRaises(ValueError):
            preview.inspect_artifact(self.ios(), 'ios')
        with patch.object(preview, 'MAX_BYTES', 8), self.assertRaises(ValueError):
            preview.inspect_artifact(self.ios(), 'ios')
        path = self.ios()
        with warnings.catch_warnings(), zipfile.ZipFile(path, 'a') as archive:
            warnings.simplefilter('ignore', UserWarning)
            archive.writestr('OneTheGo.app/main.jsbundle', b'j'*1024)
        with self.assertRaises(ValueError):
            preview.inspect_artifact(path, 'ios')

    def test_manifest_rehash_and_false_source_claims_are_rejected(self):
        path = self.ios()
        manifest, good = self.manifest(path)
        changes = [{'artifact_sha256': 'b'*64}, {'source_inventory_sha256': 'b'*64}, {'source_revision': 'main'},
                   {'hosted_preview': False}, {'format': True}, {'build_environment': {**preview.BUILD_ENV, 'APP_ENV': 'prod'}},
                   {'bundle_identifier': 'dev.r3fresh.otgd'}, {'source_files': []}]
        for change in changes:
            manifest.write_text(json.dumps({**good, **change}))
            with self.subTest(change=change), self.assertRaises(ValueError):
                preview.review(path, manifest)
        for name in ['../secret', '/secret', 'apps/mobile/App.tsx']:
            files = good['source_files'] + [{'path': name, 'sha256': 'a'*64}]
            manifest.write_text(json.dumps({**good, 'source_files': files, 'source_inventory_sha256': preview.digest(preview.canonical(files))}))
            with self.subTest(name=name), self.assertRaises(ValueError):
                preview.review(path, manifest)

    def test_prepare_requires_guarded_environment_clean_source_and_actual_expo_flag(self):
        with patch.dict(preview.os.environ, {}, clear=True), self.assertRaises(ValueError):
            preview.prepare(self.ios(), 'ios', self.base/'manifest.json')
        with patch.dict(preview.os.environ, preview.BUILD_ENV, clear=True):
            with patch.object(preview.subprocess, 'check_output', return_value=b'{"extra":{"environment":"local","hostedPreview":false}}'), self.assertRaises(ValueError):
                preview.prepare(self.ios(), 'ios', self.base/'manifest.json')
        with patch.object(preview.subprocess, 'check_output', return_value=' M apps/mobile/App.tsx\n'), self.assertRaises(ValueError):
            preview.source_inventory()

    def test_default_review_does_not_read_token_or_call_vendor(self):
        path = self.ios()
        manifest, _ = self.manifest(path)
        with patch.object(preview.urllib.request, 'build_opener', side_effect=AssertionError('No remote calls')):
            self.assertEqual(preview.review(path, manifest)['artifact_name'], path.name)

    def test_upload_exact_bytes_authentication_disabled_permissions_and_safe_response(self):
        path = self.android()
        manifest, _ = self.manifest(path, 'android')
        plan = preview.review(path, manifest)
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, count): return b'{"publicKey":"build-123"}'
        class Opener:
            request = None
            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return Response()
        opener = Opener()
        response = preview.upload(plan, 'private-token', opener)
        self.assertEqual(opener.request.full_url, preview.API)
        self.assertEqual(opener.request.get_header('X-api-key'), 'private-token')
        self.assertIn(path.read_bytes(), opener.request.data)
        self.assertIn(b'name="disabled"\r\n\r\ntrue', opener.request.data)
        for permission in preview.PERMISSIONS:
            self.assertIn(('name="appPermissions.'+permission+'"\r\n\r\nauthenticated').encode(), opener.request.data)
        self.assertFalse(response['settings_verified_live'])
        self.assertNotIn('private-token', json.dumps(response))
        self.assertNotIn('/app/build-123', json.dumps(response))

    def test_upload_missing_token_changed_artifact_redirect_and_vendor_body_do_not_escape(self):
        path = self.ios()
        manifest, _ = self.manifest(path)
        plan = preview.review(path, manifest)
        for token in ['', 'token\nsecret', 'token secret']:
            with self.subTest(token=token), self.assertRaises(ValueError):
                preview.upload(plan, token)
        with self.assertRaises(ValueError):
            preview.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.invalid')
        class FailedOpener:
            def open(self, request, timeout):
                raise urllib.error.HTTPError(preview.API, 403, 'secret response body', {}, None)
        with self.assertRaises(ValueError) as error:
            preview.upload(plan, 'private-token', FailedOpener())
        self.assertNotIn('secret response body', str(error.exception))
        self.assertNotIn('private-token', str(error.exception))
        with patch.object(preview, 'MAX_BYTES', path.stat().st_size - 1), self.assertRaises(ValueError):
            preview.upload(plan, 'private-token', FailedOpener())
        with patch.object(preview, 'MAX_BYTES', 8), patch.object(Path, 'read_bytes', side_effect=AssertionError('Unbounded read forbidden')), self.assertRaises(ValueError):
            preview.upload(plan, 'private-token', FailedOpener())
        path.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            preview.upload(plan, 'private-token', FailedOpener())


if __name__ == '__main__':
    unittest.main()
