"""Actual HTTP verification of the production Fargate nginx image.

The UI image runs as UID 10001 with a read-only root filesystem. A disposable
HTTP fixture shares its network namespace, exactly as the colocated API does
in an awsvpc Fargate task. Missing Docker or failed builds are failures, never
skips. Only containers and the temporary image created by this suite are removed.
"""
from __future__ import annotations

import http.client
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
PYTHON_IMAGE = "python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258"
MAX_BODY = 64 * 1024 * 1024
INDEX = b"<!doctype html><html><body>otgd-nginx-verification-index</body></html>"
UPSTREAM = r'''
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time

class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *args):
        pass
    def reply(self, status, body, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-OTGD-Upstream', 'fixture')
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
    def do_GET(self):
        if self.path.startswith('/v1/stream'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
            self.wfile.write(b'5\r\nfirst\r\n')
            self.wfile.flush()
            time.sleep(1.5)
            self.wfile.write(b'6\r\nsecond\r\n0\r\n\r\n')
            self.wfile.flush()
            return
        body = json.dumps({'path': self.path,
            'authorization': self.headers.get('Authorization'),
            'host': self.headers.get('Host'),
            'forwarded_proto': self.headers.get('X-Forwarded-Proto')}).encode()
        self.reply(200, body)
    def do_POST(self):
        if self.path == '/v1/reject-before-upload':
            self.rfile.read(1)
            self.close_connection = True
            self.reply(401, b'authorization-required', 'text/plain')
            return
        remaining = int(self.headers.get('Content-Length', '0'))
        received = 0
        while remaining:
            chunk = self.rfile.read(min(65536, remaining))
            if not chunk:
                break
            received += len(chunk)
            remaining -= len(chunk)
        self.reply(200 if remaining == 0 else 400,
            json.dumps({'received': received}).encode())

ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
'''


class FargateContainerTests(unittest.TestCase):
    """Exercise nginx itself rather than a mock configuration parser."""

    @classmethod
    def docker(cls, *arguments, check=True, timeout=180):
        environment = dict(os.environ)
        for name in ('DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH'):
            environment.pop(name, None)
        completed = subprocess.run(['docker', '--host=unix:///var/run/docker.sock', *arguments],
            cwd=ROOT, env=environment, text=True, capture_output=True, timeout=timeout)
        if check and completed.returncode:
            raise AssertionError('Docker verification command failed: ' +
                ' '.join(arguments[:3]) + '\n' + completed.stdout[-3000:] + completed.stderr[-3000:])
        return completed.stdout.strip()

    @classmethod
    def setUpClass(cls):
        cls.backend = cls.ui = None
        cls.scratch_volume = None
        cls.owned_image = None
        cls.temporary = None
        try:
            cls.docker('info', '--format', '{{.ServerVersion}}')
            work = ROOT / 'work'
            work.mkdir(exist_ok=True)
            cls.temporary = tempfile.TemporaryDirectory(prefix='otgd-fargate-container-', dir=work)
            context = Path(cls.temporary.name)
            deploy = context / 'deploy'
            deploy.mkdir()
            for name in ('fargate.Dockerfile', 'fargate-nginx.conf'):
                shutil.copyfile(ROOT / 'deploy' / name, deploy / name)
            web = context / 'fargate-web'
            web.mkdir(mode=0o755)
            web.chmod(0o755)
            (web / 'index.html').write_bytes(INDEX)
            (web / 'app.js').write_text('globalThis.otgdStaticFixture = true;\n')
            (web / '.env').write_text('DISPOSABLE_FIXTURE_ONLY=true\n')
            for path in web.iterdir():
                path.chmod(0o644)
            supplied_image = os.environ.get('OTGD_FARGATE_CONTAINER_UI_IMAGE')
            if supplied_image:
                cls.image = supplied_image
            else:
                cls.image = 'otgd-fargate-ui-verification:' + uuid4().hex
                cls.owned_image = cls.image
                cls.docker('build', '--platform', 'linux/amd64', '--target', 'ui',
                    '--file', str(deploy / 'fargate.Dockerfile'), '--tag', cls.image, str(context), timeout=300)
            fixture = context / 'upstream.py'
            fixture.write_text(UPSTREAM)
            fixture.chmod(0o644)
            python_image = os.environ.get('OTGD_FARGATE_CONTAINER_PYTHON_IMAGE', PYTHON_IMAGE)
            cls.backend = 'otgd-fargate-upstream-verification-' + uuid4().hex
            cls.docker('run', '--detach', '--name', cls.backend, '--platform', 'linux/amd64',
                '--sysctl', 'net.ipv6.conf.all.disable_ipv6=0',
                '--sysctl', 'net.ipv6.conf.default.disable_ipv6=0',
                '--publish', '127.0.0.1::8080', '--mount', f'type=bind,src={fixture},dst=/tmp/upstream.py,readonly',
                '--entrypoint', '/usr/local/bin/python', python_image, '/tmp/upstream.py')
            if cls.docker('inspect', '--format', '{{.State.Running}}', cls.backend) != 'true':
                raise AssertionError('Disposable upstream exited: ' + cls.docker('logs', cls.backend)[-2000:])
            cls.ui = 'otgd-fargate-ui-verification-' + uuid4().hex
            cls.scratch_volume = 'otgd-fargate-ui-scratch-verification-' + uuid4().hex
            cls.docker('run', '--detach', '--name', cls.ui, '--platform', 'linux/amd64',
                '--network', 'container:' + cls.backend, '--read-only',
                '--mount', f'type=volume,src={cls.scratch_volume},dst=/tmp',
                '--mount', f'type=bind,src={web},dst=/usr/share/nginx/html,readonly', cls.image)
            ports = json.loads(cls.docker('inspect', '--format', '{{json .NetworkSettings.Ports}}', cls.backend))
            cls.port = int(ports['8080/tcp'][0]['HostPort'])
            deadline = time.monotonic() + 30
            while True:
                try:
                    status, _, body = cls.request('/health/live')
                    if status == 200 and json.loads(body)['path'] == '/health/live':
                        break
                except (OSError, ValueError, http.client.HTTPException):
                    pass
                if time.monotonic() >= deadline:
                    raise AssertionError('Read-only non-root nginx did not become ready: ' +
                        cls.docker('logs', cls.ui)[-2000:])
                time.sleep(0.1)
        except BaseException:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        for container in (cls.ui, cls.backend):
            if container:
                cls.docker('rm', '--force', '--volumes', container, check=False)
        if cls.scratch_volume:
            cls.docker('volume', 'rm', cls.scratch_volume, check=False)
        if cls.owned_image:
            cls.docker('image', 'rm', cls.owned_image, check=False)
        if cls.temporary:
            cls.temporary.cleanup()

    @classmethod
    def request(cls, path, *, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', cls.port, timeout=5)
        try:
            connection.request('GET', path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_actual_nonroot_readonly_runtime_and_direct_entrypoint(self):
        self.assertEqual(self.docker('exec', self.ui, 'id', '-u'), '10001')
        self.assertEqual(self.docker('inspect', '--format', '{{.HostConfig.ReadonlyRootfs}}', self.ui), 'true')
        self.assertEqual(self.docker('exec', self.ui, 'stat', '-c', '%a', '/tmp'), '1777')
        self.docker('exec', self.ui, 'touch', '/tmp/uid-10001-can-write')
        volumes = json.loads(self.docker('image', 'inspect', '--format', '{{json .Config.Volumes}}', self.image))
        self.assertIn('/tmp', volumes)
        entrypoint = json.loads(self.docker('image', 'inspect', '--format', '{{json .Config.Entrypoint}}', self.image))
        self.assertIn(entrypoint, (None, []))
        self.assertEqual(json.loads(self.docker('image', 'inspect', '--format', '{{json .Config.Cmd}}', self.image)),
            ['nginx', '-g', 'daemon off;'])

    def test_static_index_and_browser_security_headers(self):
        status, headers, body = self.request('/')
        self.assertEqual((status, body), (200, INDEX))
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(headers['X-Frame-Options'], 'DENY')
        self.assertEqual(headers['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(headers['Server'], 'nginx')
        self.assertIn('no-cache', headers['Cache-Control'])

    def test_ipv6_listener_serves_the_ui(self):
        script = "import http.client; c=http.client.HTTPConnection('::1',8080,timeout=3); c.request('GET','/'); r=c.getresponse(); assert r.status==200; print(r.read().decode()); c.close()"
        self.assertEqual(self.docker('exec', self.backend, '/usr/local/bin/python', '-c', script), INDEX.decode())

    def test_extensionless_spa_route(self):
        status, _, body = self.request('/sessions/new?tab=privacy')
        self.assertEqual((status, body), (200, INDEX))

    def test_existing_javascript_has_real_asset_body_and_mime_type(self):
        status, headers, body = self.request('/app.js')
        self.assertEqual(status, 200)
        self.assertIn(headers['Content-Type'], ('application/javascript', 'text/javascript'))
        self.assertEqual(body, b'globalThis.otgdStaticFixture = true;\n')

    def test_missing_assets_never_return_spa_html(self):
        for path in ('/missing.js', '/static/missing.css', '/missing.js.map', '/missing.wasm'):
            with self.subTest(path=path):
                status, _, body = self.request(path)
                self.assertEqual(status, 404)
                self.assertNotEqual(body, INDEX)

    def test_dotfiles_are_not_served(self):
        status, _, body = self.request('/.env')
        self.assertEqual(status, 404)
        self.assertNotIn(b'DISPOSABLE_FIXTURE_ONLY', body)

    def test_api_path_query_authorization_and_public_origin_headers_are_preserved(self):
        path = '/v1/raw/export.json?format=csv&ticket=disposable'
        status, headers, body = self.request(path, headers={'Authorization': 'Bearer disposable-fixture',
            'Host': 'app.example.invalid', 'X-Forwarded-Proto': 'https'})
        self.assertEqual(status, 200)
        self.assertEqual(headers['X-OTGD-Upstream'], 'fixture')
        self.assertEqual(json.loads(body), {'path': path, 'authorization': 'Bearer disposable-fixture',
            'host': 'app.example.invalid', 'forwarded_proto': 'https'})

    def test_exact_api_and_health_prefixes_reach_upstream(self):
        for path in ('/v1', '/health', '/health/live', '/health/ready'):
            with self.subTest(path=path):
                status, _, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertEqual(json.loads(body)['path'], path)

    def test_first_stream_chunk_arrives_before_upstream_completion(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        try:
            started = time.monotonic()
            connection.request('GET', '/v1/stream')
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(5), b'first')
            self.assertLess(time.monotonic() - started, 1.0, 'nginx buffered the live response')
            self.assertEqual(response.read(), b'second')
            self.assertGreaterEqual(time.monotonic() - started, 1.4)
        finally:
            connection.close()

    def test_early_authorization_rejection_does_not_wait_for_complete_upload(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        try:
            connection.putrequest('POST', '/v1/reject-before-upload')
            connection.putheader('Content-Length', str(MAX_BODY))
            connection.endheaders()
            connection.send(b'x')
            response = connection.getresponse()
            self.assertEqual((response.status, response.read()), (401, b'authorization-required'))
        finally:
            connection.close()

    def test_exact_64_mib_upload_passes_to_api(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=15)
        try:
            connection.putrequest('POST', '/v1/upload')
            connection.putheader('Content-Length', str(MAX_BODY))
            connection.endheaders()
            chunk = b'x' * (1024 * 1024)
            for _ in range(64):
                connection.send(chunk)
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read()), {'received': MAX_BODY})
        finally:
            connection.close()

    def test_upload_above_64_mib_fails_before_sending_body(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        try:
            connection.putrequest('POST', '/v1/upload')
            connection.putheader('Content-Length', str(MAX_BODY + 1))
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, 413)
            response.read()
        finally:
            connection.close()


if __name__ == '__main__':
    unittest.main()
