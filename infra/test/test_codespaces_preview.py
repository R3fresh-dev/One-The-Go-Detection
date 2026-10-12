"""Execute the real preview hooks against disposable Git/HTTP fixtures.

These tests need Node and Git, but neither npm dependencies nor a Codespace.
Real guest bundle behavior is checked separately by browser acceptance tests.
"""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest


SOURCE = Path(__file__).resolve().parents[2]


@contextmanager
def server(reply):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, headers, body = reply(self.path)
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # Expected when the bounded reader rejects a response.

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=lambda: httpd.serve_forever(poll_interval=0.01), daemon=True
    )
    thread.start()
    try:
        yield httpd.server_port
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


class CodespacesPreviewTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="otgd-preview-test-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        scripts = self.root / ".devcontainer"
        scripts.mkdir()
        for name in ("preview-state.mjs", "prepare-preview.sh", "start-preview.sh"):
            shutil.copyfile(SOURCE / ".devcontainer" / name, scripts / name)
        self.dist = self.root / "apps/mobile/dist-preview"
        self.dist.mkdir(parents=True)
        (self.root / "apps/mobile/App.tsx").write_text("// fictional source fixture\n")
        (self.root / ".gitignore").write_text(".local/\napps/mobile/dist-preview/\n")
        (self.dist / "index.html").write_text("<!doctype html><p>Fictional guest</p>\n")
        self.manifest = {
            "schema_version": "1.0.0",
            "environment": "local",
            "fictional_guest_only": True,
            "account_services": False,
            "sensor_permissions": False,
            "raw_recording": False,
            "uploads": False,
            "inference_available": False,
            "persistence": "browser_memory_only",
            "build_environment": {
                "APP_ENV": "local",
                "EXPO_PUBLIC_APP_ENV": "local",
                "EXPO_PUBLIC_HOSTED_PREVIEW": "true",
                "EXPO_NO_DOTENV": "1",
                "EXPO_PUBLIC_API_URL": "https://unavailable.invalid",
                "EXPO_PUBLIC_OAUTH_ISSUER": "https://unavailable.invalid",
                "EXPO_PUBLIC_OAUTH_CLIENT_ID": "otgd-hosted-fictional",
            },
        }
        (self.dist / "preview-manifest.json").write_text(json.dumps(self.manifest))
        self.git("init", "-q")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Preview Fixture",
            "-c",
            "user.email=preview@invalid.test",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "fictional fixture",
        )
        self.helper("prepare", expected=0)

    def git(self, *args):
        subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def run_command(self, args, expected, extra_env=None):
        result = subprocess.run(
            args,
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=5,
            env={**os.environ, **(extra_env or {})},
        )
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def helper(self, *args, expected):
        return self.run_command(
            ["node", ".devcontainer/preview-state.mjs", *args],
            expected,
        )

    def guest_reply(self, path):
        name = "index.html" if path == "/" else path.removeprefix("/")
        return 200, {}, (self.dist / name).read_bytes()

    def test_current_export_is_accepted_and_repeat_start_reuses_only_matching_guest(
        self,
    ):
        self.helper("check", expected=0)
        with server(self.guest_reply) as port:
            self.helper("ready", str(port), expected=0)
            self.run_command(
                ["bash", ".devcontainer/start-preview.sh"],
                0,
                {"OTGD_PREVIEW_PORT": str(port)},
            )
            self.helper("ready", str(port), expected=0)
            # Reusing this fixture must not start or record another process.
            self.assertFalse(
                (self.root / ".local/codespaces-preview/server.pid").exists()
            )

    def test_changed_export_tracked_source_and_new_source_require_repreparation(self):
        receipt = self.root / ".local/codespaces-preview/prepared.json"
        for path in (
            self.dist / "index.html",
            self.root / "apps/mobile/App.tsx",
            receipt,
        ):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                if path == receipt:
                    value = json.loads(original)
                    value["source_fingerprint"] = "0" * 64
                    path.write_text(json.dumps(value))
                else:
                    path.write_bytes(original + b"\nchanged bytes\n")
                self.assertIn("changed", self.helper("check", expected=2).stderr)
                path.write_bytes(original)
                self.helper("check", expected=0)
        new_source = self.root / "apps/mobile/new-guest-source.ts"
        new_source.write_text("// new untracked source\n")
        self.assertIn("changed", self.helper("check", expected=2).stderr)
        self.helper("prepare", expected=0)
        self.helper("check", expected=0)

    def test_non_guest_marker_cannot_be_prepared_or_admitted(self):
        self.manifest["fictional_guest_only"] = False
        (self.dist / "preview-manifest.json").write_text(json.dumps(self.manifest))
        self.assertIn("fictional guest", self.helper("prepare", expected=2).stderr)
        self.assertIn("fictional guest", self.helper("check", expected=2).stderr)

    def test_generic_http_200_is_not_reused_or_stopped_by_startup(self):
        with server(lambda _: (200, {}, b"ordinary page")) as port:
            self.helper("ready", str(port), expected=2)
            result = self.run_command(
                ["bash", ".devcontainer/start-preview.sh"],
                1,
                {"OTGD_PREVIEW_PORT": str(port)},
            )
            self.assertIn("unexpected content", result.stderr)
            self.helper("ready", str(port), expected=2)
            self.assertFalse(
                (self.root / ".local/codespaces-preview/server.pid").exists()
            )

    def test_redirect_fails_without_requesting_the_target(self):
        calls = {"origin": 0, "target": 0}

        def target(_):
            calls["target"] += 1
            return 200, {}, b"redirect target"

        with server(target) as target_port:

            def origin(_):
                calls["origin"] += 1
                return 302, {"Location": f"http://127.0.0.1:{target_port}/target"}, b""

            with server(origin) as origin_port:
                self.helper("ready", str(origin_port), expected=2)
        self.assertEqual(calls, {"origin": 1, "target": 0})

    def test_probe_body_is_bounded_before_digest_comparison(self):
        with server(lambda _: (200, {}, b"x" * 16385)) as port:
            result = self.helper("ready", str(port), expected=2)
            self.assertIn("oversized", result.stderr)


if __name__ == "__main__":
    unittest.main()
