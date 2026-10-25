#!/usr/bin/env python3
"""Build, inspect and deliberately submit exact signed mobile store artifacts.

Use the locked services/api Python environment. No action executes on import.
No signing identity, store entry, approval or public rollout is invented here.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import plistlib
import re
import signal
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[4]
MOBILE = ROOT / "apps/mobile"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "services/api"))
import httpx
from cryptography.hazmat.primitives.serialization import Encoding, pkcs7
from otgd.canonical import strict_loads

from deploy import platform as cloud
from deploy.provenance import Gate, bounded_json, sha256, verify_signed_record

EAS_VERSION = "24.12.1"
EAS_INTEGRITY = "sha512-yLjpZbTkPRobwZUc+APRLVNcVvxiLO1f4UCaLB0rw5BiSnM1NTgsUikl9WTQXsnXxT/3J8iuRbo7JDJFmEm9HQ=="
BUNDLETOOL_VERSION = "1.18.3"
BUNDLETOOL_SHA256 = "a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29"
SLUG = "one-the-go-detection"
MAX_ARCHIVE = 512 * 1024 * 1024
MAX_EXPANDED = 1024 * 1024 * 1024
COMMAND_MAX_OUTPUT = 4 * 1024 * 1024
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SHA = re.compile(r"^[0-9a-f]{64}$")


def now():
    return datetime.now(UTC)


def utc(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", value
    ):
        raise Gate("An explicit UTC timestamp is required")
    return datetime.fromisoformat(value)


def identity(config):
    return "dev.r3fresh.otgd" + (".qa" if config["environment"] == "qa" else "")


def profile(config):
    return "qa-store" if config["environment"] == "qa" else "production"


def config_digest(config):
    logical = json.loads(json.dumps(config))
    logical["bundletool_jar"] = {
        "role": "official_bundletool",
        "version": BUNDLETOOL_VERSION,
        "sha256": BUNDLETOOL_SHA256,
    }
    if logical["android"]:
        logical["android"]["service_account_key_path"] = (
            "external_google_play_service_account"
        )
    if logical["ios"]:
        logical["ios"]["api_key_path"] = "external_app_store_connect_api_key"
    return sha256(logical)


def submission_digest(settings):
    logical = json.loads(json.dumps(settings))
    if "android" in logical:
        logical["android"]["serviceAccountKeyPath"] = (
            "external_google_play_service_account"
        )
    if "ios" in logical:
        logical["ios"]["ascApiKeyPath"] = "external_app_store_connect_api_key"
    return sha256(logical)


def safe_url(value, *, origin=False):
    from urllib.parse import urlsplit

    if not isinstance(value, str) or len(value) > 8192:
        raise Gate("A bounded HTTPS destination is required")
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
        or not re.fullmatch(r"[a-z0-9.-]+", host)
        or "." not in host
        or re.fullmatch(r"[0-9.]+", host)
        or any(
            part in host.split(".")
            for part in (
                "localhost",
                "localstack",
                "example",
                "invalid",
                "test",
                "local",
            )
        )
        or host.endswith((".internal", ".localhost"))
        or (origin and (parsed.path not in ("", "/") or parsed.query))
    ):
        raise Gate(
            "Local, fictional, credentialed or non-HTTPS destinations cannot serve a store release"
        )
    return parsed


def read_config(path):
    value = bounded_json(path)
    fields = {
        "schema_version",
        "environment",
        "project_id",
        "expo_account",
        "api_url",
        "oauth_issuer",
        "oauth_client_id",
        "oauth_origin",
        "oauth_web_callback_uri",
        "artifact_hosts",
        "bundletool_jar",
        "android",
        "ios",
    }
    if (
        set(value) != fields
        or value["schema_version"] != "1.0.0"
        or value["environment"] not in ("qa", "prod")
    ):
        raise Gate("Unsupported mobile release configuration")
    if not UUID.fullmatch(str(value["project_id"])) or not re.fullmatch(
        r"[a-z0-9][a-z0-9_-]{1,63}", str(value["expo_account"])
    ):
        raise Gate("Supply the actual Expo project UUID and accountable account slug")
    safe_url(value["api_url"], origin=True)
    safe_url(value["oauth_issuer"])
    origin = safe_url(value["oauth_origin"], origin=True)
    callback = safe_url(value["oauth_web_callback_uri"], origin=True)
    if value["oauth_origin"] != "https://" + origin.hostname or value["oauth_web_callback_uri"] != "https://" + callback.hostname + "/":
        raise Gate("Supply exact admitted IdentityOrigin and WebCallbackUri outputs")
    if not re.fullmatch(
        r"[A-Za-z0-9]{8,128}", str(value["oauth_client_id"])
    ) or re.search(
        r"local|example|placeholder|fictional", value["oauth_client_id"], re.IGNORECASE
    ):
        raise Gate("Supply the actual environment's public Cognito client")
    hosts = value["artifact_hosts"]
    if (
        not isinstance(hosts, list)
        or not 1 <= len(hosts) <= 8
        or len(set(hosts)) != len(hosts)
    ):
        raise Gate("Specify exact operator-approved EAS artifact HTTPS hostnames")
    for host in hosts:
        if safe_url("https://" + str(host)).hostname != host:
            raise Gate("Artifact hostname allowlist is not exact")
    android, ios = value["android"], value["ios"]
    if android is not None and (
        not isinstance(android, dict)
        or set(android) != {"upload_certificate_sha256", "service_account_key_path"}
        or not SHA.fullmatch(str(android["upload_certificate_sha256"]))
        or not isinstance(value["bundletool_jar"], str)
        or not Path(value["bundletool_jar"]).is_absolute()
    ):
        raise Gate(
            "Supply actual Android upload identity and the pinned bundletool file selector"
        )
    if ios is not None and (
        not isinstance(ios, dict)
        or set(ios)
        != {
            "asc_app_id",
            "apple_team_id",
            "distribution_certificate_sha256",
            "api_key_path",
            "api_key_id",
            "api_issuer_id",
        }
        or not re.fullmatch(r"[0-9]{6,20}", str(ios["asc_app_id"]))
        or not re.fullmatch(r"[A-Z0-9]{10}", str(ios["apple_team_id"]))
        or not SHA.fullmatch(str(ios["distribution_certificate_sha256"]))
        or not re.fullmatch(r"[A-Z0-9]{10}", str(ios["api_key_id"]))
        or not UUID.fullmatch(str(ios["api_issuer_id"]))
    ):
        raise Gate(
            "Supply actual store app/team/key identifiers and independently trusted signer fingerprints"
        )
    for item in ([android["service_account_key_path"]] if android else []) + (
        [ios["api_key_path"]] if ios else []
    ):
        if (
            not isinstance(item, str)
            or not Path(item).is_absolute()
            or any(ord(c) < 32 for c in item)
        ):
            raise Gate("Store credential file selectors must be absolute private paths")
    return value


def source_revision(root=ROOT):
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        raise Gate(
            "Store release requires a clean committed tracked source; preserved untracked files will not be copied"
        )
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise Gate("Expected a full committed source revision")
    return revision


def private_file(path):
    path = Path(path)
    try:
        metadata = path.lstat()
    except OSError:
        raise Gate("Store credential file is unavailable") from None
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or not 0 < metadata.st_size <= 65536
        or (
            os.name != "nt"
            and (metadata.st_mode & 0o077 or metadata.st_uid != os.getuid())
        )
        or path.resolve().is_relative_to(ROOT)
    ):
        raise Gate(
            "Store credentials must be owner-only regular files outside the checkout, never symlinks"
        )
    return path


def command(args, *, cwd, env, json_result=False):
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        if os.name != "posix":
            raise Gate("Bounded store tool execution requires a POSIX operator host")
        process = subprocess.Popen(
            args, cwd=cwd, env=env, stdout=output, stderr=errors, start_new_session=True
        )
        deadline = time.monotonic() + 14400
        try:
            while process.poll() is None:
                if (
                    time.monotonic() > deadline
                    or os.fstat(output.fileno()).st_size
                    + os.fstat(errors.fileno()).st_size
                    > COMMAND_MAX_OUTPUT
                ):
                    raise Gate(
                        "Pinned tool exceeded its bounded output/time limit; external outcome may be unknown"
                    )
                time.sleep(0.1)
            if (
                time.monotonic() > deadline
                or os.fstat(output.fileno()).st_size + os.fstat(errors.fileno()).st_size
                > COMMAND_MAX_OUTPUT
            ):
                raise Gate(
                    "Pinned tool finished outside its bounded output/time limit; external outcome may be unknown"
                )
            output.seek(0)
            errors.seek(0)
            stdout, stderr = (
                output.read(2 * 1024 * 1024 + 1),
                errors.read(2 * 1024 * 1024 + 1),
            )
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=30)
    if (
        process.returncode
        or len(stdout) > 2 * 1024 * 1024
        or len(stderr) > 2 * 1024 * 1024
        or b"Failed to pull env variables" in stderr
    ):
        raise Gate(
            "The pinned tool failed or could not verify cloud environment configuration; inspect its protected operator logs"
        )
    if json_result:
        try:
            return strict_loads(stdout)
        except (ValueError, TypeError):
            raise Gate("Pinned tool returned malformed JSON") from None
    return stdout.decode("utf-8", errors="strict")


def build_environment(config):
    # Keep the existing proxy/CA and operator Expo authentication, remove values
    # that can relabel a binary or introduce another environment's public client.
    allowed = {
        "PATH",
        "HOME",
        "USER",
        "USERNAME",
        "LOGNAME",
        "SystemRoot",
        "COMSPEC",
        "TMPDIR",
        "TMP",
        "TEMP",
        "LANG",
        "TERM",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "NODE_EXTRA_CA_CERTS",
        "REQUESTS_CA_BUNDLE",
        "CURL_CA_BUNDLE",
        "npm_config_cache",
        "NPM_CONFIG_CACHE",
    }
    env = {k: v for k, v in os.environ.items() if k in allowed or k.startswith("LC_")}
    env.update(
        APP_ENV=config["environment"],
        EXPO_PUBLIC_APP_ENV=config["environment"],
        EXPO_PUBLIC_HOSTED_PREVIEW="false",
        EXPO_NO_DOTENV="1",
        EXPO_NO_TELEMETRY="1",
        DISABLE_EAS_ANALYTICS="1",
        EAS_PROJECT_ID=config["project_id"],
        npm_config_registry="https://registry.npmjs.org",
        EXPO_PUBLIC_API_URL=config["api_url"],
        EXPO_PUBLIC_OAUTH_ISSUER=config["oauth_issuer"],
        EXPO_PUBLIC_OAUTH_CLIENT_ID=config["oauth_client_id"],
        EXPO_PUBLIC_OAUTH_ORIGIN=config["oauth_origin"],
        EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI=config["oauth_web_callback_uri"],
    )
    return env


class Eas:
    def __init__(self, cwd, config):
        self.cwd, self.env = cwd, build_environment(config)
        if not os.environ.get("EXPO_TOKEN"):
            raise Gate(
                "Set genuine EXPO_TOKEN for the authorized Expo account; no build is launched"
            )
        self.env["EXPO_TOKEN"] = os.environ["EXPO_TOKEN"]
        manifest = verify_eas_package()
        toolchain = cwd / "distribution/eas-toolchain"
        lock = bounded_json(toolchain / "package-lock.json", limit=2 * 1024 * 1024)
        if (
            lock.get("packages", {}).get("node_modules/eas-cli", {}).get("integrity")
            != EAS_INTEGRITY
        ):
            raise Gate(
                "The committed CLI toolchain lock does not pin the verified official package"
            )
        command(
            ["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
            cwd=toolchain,
            env=build_environment(config),
        )
        installed = toolchain / "node_modules/eas-cli"
        verify_cli_tree(installed, manifest)
        self.prefix = ["node", str(installed / "bin/run")]
        version = self.run(["--version"])
        if not re.search(r"\beas-cli/" + re.escape(EAS_VERSION) + r"\b", version):
            raise Gate("Unexpected EAS CLI version")

    def run(self, args, json_result=False):
        return command(
            self.prefix + args, cwd=self.cwd, env=self.env, json_result=json_result
        )

    def verify_project(self, config):
        text = re.sub(r"\x1b\[[0-9;]*m", "", self.run(["project:info"]))
        name = re.findall(r"^fullName\s+(@[^\s]+)\s*$", text, re.MULTILINE)
        ids = re.findall(r"^ID\s+([0-9a-f-]{36})\s*$", text, re.MULTILINE)
        if name != ["@" + config["expo_account"] + "/" + SLUG] or ids != [
            config["project_id"]
        ]:
            raise Gate(
                "Actual authenticated Expo project/account differs from the exact approved target before mutation"
            )

    def verify_environment(self, config):
        environment = "preview" if config["environment"] == "qa" else "production"
        for name, expected in (
            ("EXPO_PUBLIC_API_URL", config["api_url"]),
            ("EXPO_PUBLIC_OAUTH_ISSUER", config["oauth_issuer"]),
            ("EXPO_PUBLIC_OAUTH_CLIENT_ID", config["oauth_client_id"]),
            ("EXPO_PUBLIC_OAUTH_ORIGIN", config["oauth_origin"]),
            ("EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI", config["oauth_web_callback_uri"]),
        ):
            value = self.run(
                [
                    "env:get",
                    environment,
                    "--variable-name",
                    name,
                    "--scope",
                    "project",
                    "--format",
                    "short",
                    "--non-interactive",
                ]
            )
            value = re.sub(r"\x1b\[[0-9;]*m", "", value).strip()
            if value != name + "=" + expected:
                raise Gate(
                    "The actual project-scoped EAS public environment is absent or differs from the deployed target"
                )


def verify_eas_package():
    import base64

    with httpx.Client(timeout=30, follow_redirects=False) as client:
        raw = bytearray()
        with client.stream(
            "GET", "https://registry.npmjs.org/eas-cli/" + EAS_VERSION
        ) as response:
            if response.status_code != 200:
                raise Gate("Pinned official EAS package metadata is unavailable")
            for part in response.iter_bytes():
                raw.extend(part)
                if len(raw) > 262144:
                    raise Gate("Pinned official EAS package metadata is unavailable")
        metadata = strict_loads(raw)
        url = "https://registry.npmjs.org/eas-cli/-/eas-cli-" + EAS_VERSION + ".tgz"
        if (
            metadata.get("version") != EAS_VERSION
            or metadata.get("dist", {}).get("integrity") != EAS_INTEGRITY
            or metadata["dist"].get("tarball") != url
        ):
            raise Gate("Official EAS package integrity differs from the reviewed pin")
        total, checksum, payload = 0, hashlib.sha512(), bytearray()
        with client.stream("GET", url) as archive:
            if archive.status_code != 200:
                raise Gate("Pinned EAS archive is unavailable")
            for part in archive.iter_bytes():
                total += len(part)
                if total > 16 * 1024 * 1024:
                    raise Gate("Pinned EAS archive exceeds its verification bound")
                checksum.update(part)
                payload.extend(part)
        if "sha512-" + base64.b64encode(checksum.digest()).decode() != EAS_INTEGRITY:
            raise Gate("Pinned EAS archive failed cryptographic integrity verification")
    manifest = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as source:
        entries = source.getmembers()
        if len(entries) > 5000 or sum(item.size for item in entries) > 64 * 1024 * 1024:
            raise Gate("Pinned CLI archive exceeds its supported unpacked inventory")
        for item in entries:
            path = PurePosixPath(item.name)
            if (
                path.parts[0] != "package"
                or ".." in path.parts
                or item.issym()
                or item.islnk()
            ):
                raise Gate("Pinned CLI package contains unsafe executable source paths")
            if not item.isfile():
                continue
            name = "/".join(path.parts[1:])
            if not name or name in manifest:
                raise Gate("Pinned CLI source inventory contains duplicates")
            content = source.extractfile(item).read()
            manifest[name] = {
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
    if "bin/run" not in manifest or "package.json" not in manifest:
        raise Gate(
            "Pinned CLI archive does not contain its expected entrypoint/package"
        )
    return manifest


def verify_cli_tree(directory, manifest):
    for name, expected in manifest.items():
        path = directory / name
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_size != expected["size_bytes"]
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]
        ):
            raise Gate(
                "Installed CLI executable source differs from the verified official package archive"
            )


def verify_eas_config(value, config, platform):
    if not isinstance(value, dict) or set(value) != {"buildProfile", "appConfig"}:
        raise Gate("Expected the pinned CLI's exact configuration envelope")
    p, app = value["buildProfile"], value["appConfig"]
    extra = app.get("extra", {})
    if (
        p.get("distribution") != "store"
        or p.get("developmentClient", False)
        or p.get("environment")
        != ("preview" if config["environment"] == "qa" else "production")
        or extra.get("environment") != config["environment"]
        or extra.get("hostedPreview") is not False
        or extra.get("eas", {}).get("projectId") != config["project_id"]
        or extra.get("apiUrl") != config["api_url"]
        or extra.get("issuer") != config["oauth_issuer"]
        or extra.get("clientId") != config["oauth_client_id"]
        or extra.get("oauthOrigin") != config["oauth_origin"]
        or extra.get("webCallbackUri") != config["oauth_web_callback_uri"]
        or extra.get("redirectUris") != ["otgd" + ("-qa" if config["environment"] == "qa" else "") + "://oauth/callback", config["oauth_web_callback_uri"]]
        or app.get("slug") != SLUG
        or (
            platform == "android"
            and (
                p.get("buildType") != "app-bundle"
                or app.get("android", {}).get("package") != identity(config)
            )
        )
        or (
            platform == "ios"
            and (
                p.get("simulator", False)
                or app.get("ios", {}).get("bundleIdentifier") != identity(config)
            )
        )
    ):
        raise Gate(
            "Actual EAS configuration differs from this exact environment/project/store target"
        )
    if p.get("env", {}).get("EXPO_PUBLIC_HOSTED_PREVIEW") != "false":
        raise Gate(
            "The selected store profile must explicitly disable fictional hosted mode"
        )
    logical = json.loads(json.dumps(value))
    logical["appConfig"].pop("_internal", None)
    return sha256(logical)


def verify_build(
    value, config, platform, revision, build_id=None, *, allow_expired=False
):
    app = value.get("app", {}) if isinstance(value, dict) else {}
    if (
        not isinstance(value, dict)
        or not UUID.fullmatch(str(value.get("id")))
        or (build_id and value["id"] != build_id)
        or value.get("status") != "FINISHED"
        or value.get("platform") != platform.upper()
        or value.get("distribution") != "STORE"
        or value.get("buildProfile") != profile(config)
        or value.get("appIdentifier") != identity(config)
        or value.get("gitCommitHash") != revision
        or value.get("isForIosSimulator", False)
        or app.get("id") != config["project_id"]
        or app.get("slug") != SLUG
        or app.get("ownerAccount", {}).get("name") != config["expo_account"]
        or not re.fullmatch(r"[1-9][0-9]{0,9}", str(value.get("appBuildVersion")))
        or not isinstance(value.get("appVersion"), str)
        or (
            not allow_expired
            and value.get("expirationDate")
            and utc(value["expirationDate"]) <= now()
        )
    ):
        raise Gate("EAS build is not the finished exact-source signed store target")
    return {
        key: value[key]
        for key in (
            "id",
            "platform",
            "distribution",
            "buildProfile",
            "appIdentifier",
            "appVersion",
            "appBuildVersion",
            "gitCommitHash",
        )
    }


def download_artifact(url, config, target, *, client=None):
    if client is None:
        with httpx.Client(
            timeout=60,
            follow_redirects=False,
            headers={"Accept": "application/octet-stream"},
        ) as owned:
            return download_artifact(url, config, target, client=owned)
    current, total = url, 0
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        for _ in range(5):
            if safe_url(current).hostname not in config["artifact_hosts"]:
                raise Gate(
                    "EAS artifact destination is outside the explicit operator-approved hostname list"
                )
            with client.stream("GET", current) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    from urllib.parse import urljoin

                    current = urljoin(current, response.headers.get("location", ""))
                    continue
                if response.status_code != 200:
                    raise Gate("The exact EAS artifact cannot be downloaded")
                checksum = hashlib.sha256()
                descriptor = os.open(
                    target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
                with os.fdopen(descriptor, "wb") as output:
                    for part in response.iter_bytes():
                        total += len(part)
                        if total > MAX_ARCHIVE:
                            raise Gate(
                                "Store artifact exceeds the bounded 512 MiB archive limit"
                            )
                        output.write(part)
                        checksum.update(part)
                if not total:
                    raise Gate("Store artifact is empty")
                return {"sha256": checksum.hexdigest(), "size_bytes": total}
        raise Gate("Too many artifact redirects")
    except Exception:
        target.unlink(missing_ok=True)
        raise


def archive_entries(archive):
    entries = archive.infolist()
    names = [e.filename for e in entries]
    if (
        not 1 <= len(entries) <= 20000
        or len(names) != len(set(names))
        or sum(e.file_size for e in entries) > MAX_EXPANDED
    ):
        raise Gate("Duplicate or oversized store archive")
    for entry in entries:
        name = entry.filename
        if (
            "\\" in name
            or "\x00" in name
            or PurePosixPath(name).is_absolute()
            or ".." in PurePosixPath(name).parts
            or stat.S_ISLNK(entry.external_attr >> 16)
            or entry.flag_bits & 1
        ):
            raise Gate("Unsafe store archive entry")
    return names


def inspect_android(path, config, metadata):
    with zipfile.ZipFile(path) as archive:
        names = archive_entries(archive)
        if (
            "BundleConfig.pb" not in names
            or "base/manifest/AndroidManifest.xml" not in names
            or "base/assets/app.config" not in names
            or not any(
                n.startswith("base/assets/") and n.endswith(".bundle") for n in names
            )
        ):
            raise Gate(
                "Expected a signed Android App Bundle with embedded JavaScript, never a development APK"
            )
        if archive.getinfo("base/assets/app.config").file_size > 1048576:
            raise Gate("Embedded public runtime configuration exceeds its bound")
        verify_embedded_config(
            strict_loads(archive.read("base/assets/app.config")), config
        )
        signature_names = [
            n for n in names if re.fullmatch(r"META-INF/[^/]+\.(RSA|EC|DSA)", n)
        ]
        if (
            len(signature_names) != 1
            or archive.getinfo(signature_names[0]).file_size > 131072
        ):
            raise Gate("Expected exactly one bounded AAB upload signature")
        certificates = pkcs7.load_der_pkcs7_certificates(
            archive.read(signature_names[0])
        )
        if (
            len(certificates) != 1
            or hashlib.sha256(certificates[0].public_bytes(Encoding.DER)).hexdigest()
            != config["android"]["upload_certificate_sha256"]
        ):
            raise Gate(
                "AAB upload signer differs from the independently trusted certificate"
            )
    with tempfile.TemporaryDirectory(prefix="otgd-upload-trust-") as directory:
        certificate_path = Path(directory) / "trusted-upload.pem"
        certificate_path.write_bytes(certificates[0].public_bytes(Encoding.PEM))
        trust_store = Path(directory) / "public-trust.p12"
        # This password protects only a temporary public-certificate trust store.
        # No private signing material is generated or read here.
        password = "public-certificate-trust-only"
        subprocess.run(
            [
                "keytool",
                "-importcert",
                "-noprompt",
                "-alias",
                "approved-upload",
                "-file",
                str(certificate_path),
                "-keystore",
                str(trust_store),
                "-storepass",
                password,
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
        result = subprocess.run(
            [
                "java",
                "-Duser.language=en",
                "--module",
                "jdk.jartool/sun.security.tools.jarsigner.Main",
                "-verify",
                "-strict",
                "-keystore",
                str(trust_store),
                "-storepass",
                password,
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode or "jar verified." not in result.stdout:
            raise Gate(
                "Android App Bundle cryptographic signature verification failed or contains unsigned entries"
            )
    tool = Path(config["bundletool_jar"])
    if (
        not tool.is_file()
        or tool.is_symlink()
        or tool.stat().st_size > 64 * 1024 * 1024
        or hashlib.sha256(tool.read_bytes()).hexdigest() != BUNDLETOOL_SHA256
    ):
        raise Gate(
            "Supply the integrity-verified official bundletool "
            + BUNDLETOOL_VERSION
            + " JAR"
        )
    manifest = subprocess.check_output(
        [
            "java",
            "-jar",
            str(tool),
            "dump",
            "manifest",
            "--bundle=" + str(path),
            "--module=base",
        ],
        timeout=120,
    )
    verify_android_manifest(manifest, config, metadata)
    # The Java certificate is an upload identity; Google Play App Signing uses
    # its separate distribution key. EAS metadata pins the exact application ID.
    return {
        "format": "aab",
        "signer_sha256": config["android"]["upload_certificate_sha256"],
        "signature_verification": "jdk_jarsigner_strict_with_pinned_trust",
        "distribution_signer": "google_play_app_signing_external",
    }


def verify_embedded_config(app, config):
    extra = app.get("extra", {}) if isinstance(app, dict) else {}
    redirect = (
        "otgd" + ("-qa" if config["environment"] == "qa" else "") + "://oauth/callback"
    )
    if (
        extra.get("environment") != config["environment"]
        or extra.get("hostedPreview") is not False
        or extra.get("apiUrl") != config["api_url"]
        or extra.get("issuer") != config["oauth_issuer"]
        or extra.get("clientId") != config["oauth_client_id"]
        or extra.get("oauthOrigin") != config["oauth_origin"]
        or extra.get("webCallbackUri") != config["oauth_web_callback_uri"]
        or extra.get("redirectUris") != ["otgd" + ("-qa" if config["environment"] == "qa" else "") + "://oauth/callback", config["oauth_web_callback_uri"]]
        or extra.get("redirectUri") != redirect
        or extra.get("eas", {}).get("projectId") != config["project_id"]
        or app.get("slug") != SLUG
        or app.get("android", {}).get("package") != identity(config)
        or app.get("ios", {}).get("bundleIdentifier") != identity(config)
    ):
        raise Gate(
            "Actual embedded native public configuration differs from the admitted store target"
        )


def verify_android_manifest(raw, config, metadata):
    if len(raw) > 1048576 or b"<!DOCTYPE" in raw or b"<!ENTITY" in raw:
        raise Gate("Unbounded or entity-bearing store manifest")
    manifest = ET.fromstring(raw)
    android = "{http://schemas.android.com/apk/res/android}"
    application = manifest.find("application")
    sdk = manifest.find("uses-sdk")
    if (
        manifest.tag != "manifest"
        or manifest.get("package") != identity(config)
        or manifest.get(android + "versionName") != metadata["appVersion"]
        or manifest.get(android + "versionCode") != metadata["appBuildVersion"]
        or application is None
        or sdk is None
        or application.get(android + "debuggable", "false") != "false"
        or application.get(android + "testOnly", "false") != "false"
        or application.get(android + "usesCleartextTraffic", "false") != "false"
        or int(sdk.get(android + "targetSdkVersion", "0")) != 36
        or int(sdk.get(android + "minSdkVersion", "0")) != 24
        or any(
            m.get(android + "name") == "dev.r3fresh.otgd.HOSTED_PREVIEW"
            and m.get(android + "value") != "false"
            for m in application.findall("meta-data")
        )
    ):
        raise Gate(
            "AAB manifest is a local, debug, fictional or unsupported store target"
        )


def inspect_ios(path, config, metadata):
    if sys.platform != "darwin":
        raise Gate(
            "Device IPA signature and provisioning verification requires macOS/Xcode; no simulator substitution"
        )
    with zipfile.ZipFile(path) as archive:
        names = archive_entries(archive)
        plist_names = [
            n for n in names if re.fullmatch(r"Payload/[^/]+\.app/Info.plist", n)
        ]
        if len(plist_names) != 1 or archive.getinfo(plist_names[0]).file_size > 1048576:
            raise Gate("Expected one bounded device application in the IPA")
        info = plistlib.loads(archive.read(plist_names[0]))
        prefix = plist_names[0][: -len("Info.plist")]
        executable = prefix + str(info.get("CFBundleExecutable", ""))
        if (
            info.get("CFBundleIdentifier") != identity(config)
            or info.get("CFBundleShortVersionString") != metadata["appVersion"]
            or info.get("CFBundleVersion") != metadata["appBuildVersion"]
            or not re.fullmatch(
                r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", str(info.get("MinimumOSVersion", ""))
            )
            or tuple(
                int(x) for x in str(info.get("MinimumOSVersion", "0.0")).split(".")[:2]
            )
            < (16, 4)
            or info.get("DTPlatformName") != "iphoneos"
            or info.get("OTGDHostedPreview", False)
            or executable not in names
            or prefix + "main.jsbundle" not in names
            or prefix + "embedded.mobileprovision" not in names
        ):
            raise Gate("IPA is not the protected real-device store application")
        data = archive.read(executable)
        if len(data) < 32 or data[:4] != b"\xcf\xfa\xed\xfe":
            raise Gate("Expected a thin ARM64 device executable")
        _, cpu, _, kind, count, size, _, _ = struct.unpack_from("<8I", data)
        offset, platforms = 32, []
        if (
            cpu != 0x0100000C
            or kind != 2
            or count > 2048
            or size > 131072
            or 32 + size > len(data)
        ):
            raise Gate("Unsupported device executable")
        for _ in range(count):
            if offset + 8 > 32 + size:
                raise Gate("Truncated device build command")
            code, length = struct.unpack_from("<2I", data, offset)
            if length < 8 or offset + length > 32 + size:
                raise Gate("Invalid device build command")
            if code == 0x32:
                if length < 24:
                    raise Gate("Truncated device platform command")
                platforms.append(struct.unpack_from("<I", data, offset + 8)[0])
            offset += length
        if offset != 32 + size or platforms != [2]:
            raise Gate("Store IPA must target iOS device, never Simulator")
        embedded = [
            n
            for n in names
            if n.startswith(prefix) and n.endswith("EXConstants.bundle/app.config")
        ]
        if len(embedded) != 1 or archive.getinfo(embedded[0]).file_size > 1048576:
            raise Gate(
                "IPA lacks one bounded actual embedded Expo public configuration"
            )
        verify_embedded_config(strict_loads(archive.read(embedded[0])), config)
        with tempfile.TemporaryDirectory(prefix="otgd-store-ipa-") as directory:
            archive.extractall(directory)
            app = Path(directory) / prefix
            subprocess.run(
                ["codesign", "--verify", "--deep", "--strict", str(app)],
                check=True,
                capture_output=True,
                timeout=120,
            )
            entitlements = plistlib.loads(
                subprocess.check_output(
                    ["codesign", "-d", "--entitlements", "-", str(app)],
                    stderr=subprocess.DEVNULL,
                    timeout=60,
                )
            )
            provision = plistlib.loads(
                subprocess.check_output(
                    [
                        "security",
                        "cms",
                        "-D",
                        "-i",
                        str(app / "embedded.mobileprovision"),
                    ],
                    timeout=60,
                )
            )
            team = config["ios"]["apple_team_id"]
            expiration = provision.get("ExpirationDate")
            if (
                entitlements.get("get-task-allow", False) is not False
                or entitlements.get("application-identifier")
                != team + "." + identity(config)
                or provision.get("TeamIdentifier") != [team]
                or provision.get("ProvisionedDevices")
                or provision.get("ProvisionsAllDevices")
                or not isinstance(expiration, datetime)
                or expiration.replace(tzinfo=UTC) <= now()
            ):
                raise Gate(
                    "IPA has debug/ad-hoc/enterprise or expired provisioning rather than App Store identity"
                )
            stem = Path(directory) / "signer"
            subprocess.run(
                ["codesign", "-d", "--extract-certificates", str(stem), str(app)],
                check=True,
                capture_output=True,
                timeout=60,
            )
            certificate = Path(str(stem) + "0").read_bytes()
            if hashlib.sha256(certificate).hexdigest() != config["ios"][
                "distribution_certificate_sha256"
            ] or certificate not in provision.get("DeveloperCertificates", []):
                raise Gate(
                    "IPA signer differs from the independently trusted Apple Distribution certificate"
                )
    return {
        "format": "ipa",
        "signer_sha256": config["ios"]["distribution_certificate_sha256"],
        "signature_verification": "codesign_and_app_store_provisioning",
    }


def verify_backend(args, config, revision):
    c = cloud.read_config(args.backend_config)
    if c["environment"] != config["environment"] or c["releaseId"] != revision:
        raise Gate(
            "Backend and mobile must use the same reviewed source and target environment"
        )
    aws = cloud.session(c, args.aws_profile)
    if aws.client("sts").get_caller_identity()["Account"] != c["account"]:
        raise Gate("AWS identity does not match the actual target account")
    release = cloud.require_release(
        argparse.Namespace(
            release=args.backend_release,
            trusted_public_key=args.trusted_public_key,
            gate_evidence=args.gate_evidence,
            qa_evidence=args.qa_evidence,
        ),
        c,
        aws,
    )
    out = cloud.stack_outputs(aws, c)
    if (
        out.get("ReleaseId") != revision
        or out.get("ImageDigest") != c["imageDigest"]
        or out.get("ApiOrigin") != config["api_url"]
        or out.get("Issuer") != config["oauth_issuer"]
        or out.get("ClientId") != config["oauth_client_id"]
        or out.get("IdentityOrigin") != config["oauth_origin"]
        or out.get("WebCallbackUri") != config["oauth_web_callback_uri"]
    ):
        raise Gate(
            "Deployed backend identity/source differs from the store binary configuration"
        )
    ecs = aws.client("ecs")
    services = ecs.describe_services(
        cluster=out["Cluster"], services=[out["ApiService"], out["WorkerService"]]
    )
    if services.get("failures") or len(services.get("services", [])) != 2:
        raise Gate("The target API/worker services are unavailable")
    for service in services["services"]:
        if (
            service.get("status") != "ACTIVE"
            or service.get("desiredCount", 0) < 1
            or service.get("runningCount") != service["desiredCount"]
            or service.get("pendingCount")
        ):
            raise Gate(
                "The target services must be running and stable before store build/submission"
            )
        deployments = service.get("deployments", [])
        if (
            len(deployments) != 1
            or deployments[0].get("status") != "PRIMARY"
            or deployments[0].get("rolloutState") != "COMPLETED"
        ):
            raise Gate(
                "Store release requires a completed backend rollout, not desired configuration alone"
            )
        definition = ecs.describe_task_definition(
            taskDefinition=service["taskDefinition"]
        )["taskDefinition"]
        if any(
            not item["image"].endswith("@" + c["imageDigest"])
            for item in definition["containerDefinitions"]
            if item.get("essential", True)
        ):
            raise Gate(
                "Running service task definition differs from the signed target image"
            )
        listing = ecs.list_tasks(
            cluster=out["Cluster"],
            serviceName=service["serviceName"],
            desiredStatus="RUNNING",
            maxResults=100,
        )
        arns = listing.get("taskArns", [])
        if (
            listing.get("nextToken")
            or len(arns) != service["desiredCount"]
            or not 1 <= len(arns) <= 100
        ):
            raise Gate(
                "Actual backend tasks do not match the bounded stable service inventory"
            )
        running = ecs.describe_tasks(cluster=out["Cluster"], tasks=arns)
        if (
            running.get("failures")
            or len(running.get("tasks", [])) != len(arns)
            or any(
                task.get("taskDefinitionArn") != service["taskDefinition"]
                or task.get("lastStatus") != "RUNNING"
                or not task.get("containers")
                or any(
                    container.get("imageDigest") != c["imageDigest"]
                    for container in task["containers"]
                )
                for task in running.get("tasks", [])
            )
        ):
            raise Gate(
                "Actual running backend task/image differs from the independently signed source release"
            )
    with httpx.Client(timeout=15, follow_redirects=False) as client:
        ready = client.get(config["api_url"] + "/health/ready")
        response = client.get(config["api_url"] + "/v1/app-config")
        if (
            ready.status_code != 200
            or response.status_code != 200
            or len(response.content) > 65536
        ):
            raise Gate("Actual target API readiness/configuration is unavailable")
        app = strict_loads(response.content)
    redirect = (
        "otgd" + ("-qa" if config["environment"] == "qa" else "") + "://oauth/callback"
    )
    if (
        app.get("environment") != config["environment"]
        or app.get("maintenance") is not False
        or app.get("inference_available") is not False
        or app.get("auth", {}).get("issuer") != config["oauth_issuer"]
        or app.get("auth", {}).get("client_id") != config["oauth_client_id"]
        or app.get("auth", {}).get("authorization_endpoint") != config["oauth_origin"] + "/oauth2/authorize"
        or app.get("auth", {}).get("token_endpoint") != config["oauth_origin"] + "/oauth2/token"
        or app.get("auth", {}).get("revocation_endpoint") != config["oauth_origin"] + "/oauth2/revoke"
        or app.get("auth", {}).get("logout_endpoint") != config["oauth_origin"] + "/logout"
        or sorted(app.get("auth", {}).get("redirect_uris", [])) != sorted([redirect, config["oauth_web_callback_uri"]])
    ):
        raise Gate(
            "Live backend admission/auth identity does not support this exact native store application"
        )
    return {
        "release_sha256": hashlib.sha256(args.backend_release.read_bytes()).hexdigest(),
        "gate_provenance_sha256": release["gate_provenance_sha256"],
        "api_config_sha256": sha256(app),
    }


def isolated_source(revision, directory):
    source = Path(directory) / "source"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", "--no-checkout", str(ROOT), str(source)],
        check=True,
        capture_output=True,
        timeout=120,
    )
    subprocess.run(
        ["git", "checkout", "--detach", revision],
        cwd=source,
        check=True,
        capture_output=True,
        timeout=120,
    )
    if source_revision(source) != revision:
        raise Gate("Build copy does not match the reviewed committed source")
    return source / "apps/mobile"


def submission_profile(config, platform):
    if platform == "android":
        private_file(config["android"]["service_account_key_path"])
        return {
            "android": {
                "serviceAccountKeyPath": config["android"]["service_account_key_path"],
                "applicationId": identity(config),
                "track": "internal" if config["environment"] == "qa" else "production",
                "releaseStatus": "draft",
                "changesNotSentForReview": True,
            }
        }
    private_file(config["ios"]["api_key_path"])
    return {
        "ios": {
            "ascAppId": config["ios"]["asc_app_id"],
            "appleTeamId": config["ios"]["apple_team_id"],
            "bundleIdentifier": identity(config),
            "ascApiKeyPath": config["ios"]["api_key_path"],
            "ascApiKeyId": config["ios"]["api_key_id"],
            "ascApiKeyIssuerId": config["ios"]["api_issuer_id"],
        }
    }


def stage_credential(path, directory):
    """Copy one explicitly selected private file without following a replaced link."""
    path = private_file(path)
    descriptor = os.open(
        path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    )
    raw = bytearray()
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size > 65536
            or (
                os.name != "nt"
                and (before.st_mode & 0o077 or before.st_uid != os.getuid())
            )
        ):
            raise Gate("Store credential file changed before its protected read")
        while len(raw) <= 65536:
            part = os.read(descriptor, 4096)
            if not part:
                break
            raw.extend(part)
        after = os.fstat(descriptor)
        named = path.lstat()

        def version(s):
            return (
                s.st_dev,
                s.st_ino,
                s.st_size,
                s.st_mode,
                s.st_mtime_ns,
                s.st_ctime_ns,
                s.st_nlink,
                s.st_uid,
            )

        if (
            version(before) != version(after)
            or version(after) != version(named)
            or len(raw) != before.st_size
        ):
            raise Gate("Store credential selector changed during its bounded read")
        target = Path(directory) / ("submission-key" + path.suffix)
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
        return target
    finally:
        os.close(descriptor)
        raw[:] = b"\x00" * len(raw)


def verify_submission(value, config, platform, build_id):
    app = value.get("app", {}) if isinstance(value, dict) else {}
    if (
        not isinstance(value, dict)
        or not UUID.fullmatch(str(value.get("id")))
        or value.get("status") != "FINISHED"
        or value.get("platform") != platform.upper()
        or app.get("id") != config["project_id"]
        or app.get("slug") != SLUG
        or app.get("ownerAccount", {}).get("name") != config["expo_account"]
        or value.get("submittedBuild", {}).get("id") != build_id
        or (
            platform == "android"
            and (
                value.get("androidConfig", {}).get("track")
                != ("internal" if config["environment"] == "qa" else "production")
                or value.get("androidConfig", {}).get("releaseStatus") != "DRAFT"
                or value.get("androidConfig", {}).get("rollout") is not None
            )
        )
        or (
            platform == "ios"
            and str(value.get("iosConfig", {}).get("ascAppIdentifier"))
            != config["ios"]["asc_app_id"]
        )
    ):
        raise Gate(
            "Actual submission does not match this exact nonpublic store target/build"
        )
    return {
        "submission_id": value["id"],
        "eas_status": "FINISHED",
        "build_id": build_id,
        "store_availability": "not_verified",
        "public_release": False,
        "next_step": "App Store Connect processing and deliberate tester/review release"
        if platform == "ios"
        else "Play Console draft review and deliberate test/release publication",
    }


def receipt(args, config, revision):
    value = verify_signed_record(args.receipt, args.trusted_public_key)
    if (
        value.get("purpose") != "mobile-store-build"
        or value.get("source_revision") != revision
        or value.get("config_sha256") != config_digest(config)
        or value.get("platform") != args.platform
        or utc(value.get("expires_at")) <= now()
        or utc(value.get("created_at")) > now()
        or utc(value["expires_at"]) - utc(value["created_at"]) > timedelta(days=7)
    ):
        raise Gate(
            "Signed mobile build receipt is expired or belongs to another source/configuration/platform"
        )
    return value


def preserve_submission_intent(body, path, key_path):
    """Commit the sole pending-upload fence before a provider can see a request."""
    raw = cloud.canonical(body)
    output = {
        "schema_version": "1.0.0",
        "payload": body,
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "algorithm": "Ed25519",
        "signature": base64.b64encode(cloud.private_key(key_path).sign(raw)).decode(),
    }
    directory = None
    try:
        directory = os.open(
            path.parent,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
        )
        parent = os.fstat(directory)
        if parent.st_uid != os.getuid() or parent.st_mode & 0o022:
            raise Gate("Pending intents require existing protected operator storage")
        descriptor = os.open(
            path.name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o600,
            dir_fd=directory,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(output, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(directory)
        named = os.stat(path.parent, follow_symlinks=False)
        opened = os.fstat(directory)
        if (named.st_dev, named.st_ino) != (opened.st_dev, opened.st_ino):
            raise Gate("The pending-intent directory changed before submission")
    except OSError:
        # Keep any created fence. Its uncertain durability cannot authorize an
        # upload, and a later retry must reconcile rather than create a request.
        raise Gate(
            "The signed submission intent could not be durably preserved"
        ) from None
    finally:
        if directory is not None:
            os.close(directory)


def execute(args):
    config = read_config(args.config)
    if config[args.platform] is None:
        raise Gate(
            "Configure genuine store identifiers for the deliberately selected platform; the other platform may remain null"
        )
    if args.action == "plan":
        return {
            "action": "plan_only",
            "environment": config["environment"],
            "profile": profile(config),
            "application_id": identity(config),
            "eas_cli": EAS_VERSION,
            "genuine_signing_inputs_required": True,
            "required_gates": 13,
            "public_release": False,
            "credentials_present": {"expo_token": bool(os.environ.get("EXPO_TOKEN"))},
            "store_availability": "not_verified",
        }
    if args.action == "status":
        if not args.receipt or not args.trusted_public_key:
            raise Gate(
                "Supply the exact signed build receipt and independently trusted public key"
            )
        saved = verify_signed_record(args.receipt, args.trusted_public_key)
        if (
            saved.get("purpose") != "mobile-store-build"
            or saved.get("config_sha256") != config_digest(config)
            or saved.get("platform") != args.platform
        ):
            raise Gate("Status receipt belongs to another configuration/platform")
        eas = Eas(MOBILE, config)
        eas.verify_project(config)
        built = eas.run(["build:view", saved["build"]["id"], "--json"], True)
        metadata = verify_build(
            built,
            config,
            args.platform,
            saved["source_revision"],
            saved["build"]["id"],
            allow_expired=True,
        )
        if metadata != saved["build"]:
            raise Gate("Actual build metadata differs from the signed build receipt")
        result = {
            "action": "status_only",
            "build_id": metadata["id"],
            "eas_build_status": "FINISHED",
            "receipt_current": utc(saved["expires_at"]) > now(),
            "store_availability": "not_verified",
            "public_release": False,
        }
        if args.submission_receipt:
            submitted = verify_signed_record(
                args.submission_receipt, args.trusted_public_key
            )
            if (
                submitted.get("purpose") != "mobile-store-submission"
                or submitted.get("config_sha256") != config_digest(config)
                or submitted.get("build_receipt_sha256")
                != hashlib.sha256(args.receipt.read_bytes()).hexdigest()
            ):
                raise Gate(
                    "Submission status receipt belongs to another exact signed build"
                )
            actual = eas.run(
                ["submit:view", submitted["submission_id"], "--json"], True
            )
            result.update(
                verify_submission(actual, config, args.platform, metadata["id"])
            )
            result["eas_submission_status"] = result.pop("eas_status")
        return result
    revision = source_revision()
    for field in (
        "backend_config",
        "backend_release",
        "gate_evidence",
        "trusted_public_key",
        "output",
    ):
        if not getattr(args, field):
            raise Gate(
                "Supply backend/configuration/live-gate/trust inputs and an immutable output receipt"
            )
    backend = verify_backend(args, config, revision)
    if not args.signing_key:
        raise Gate("Supply the genuine independently trusted release signing authority")
    cloud.require_trusted_signer(args.signing_key, args.trusted_public_key)
    if args.output.exists():
        raise Gate("Output receipt is immutable; choose a new path")
    with tempfile.TemporaryDirectory(prefix="otgd-store-release-") as directory:
        cwd = isolated_source(revision, directory)
        env = build_environment(config)
        command(["npm", "ci"], cwd=cwd, env=env)
        eas = Eas(cwd, config)
        eas.verify_project(config)
        eas.verify_environment(config)
        resolved = eas.run(
            [
                "config",
                "--platform",
                args.platform,
                "--profile",
                profile(config),
                "--json",
                "--non-interactive",
            ],
            True,
        )
        resolved_sha = verify_eas_config(resolved, config, args.platform)
        if args.action == "build":
            rows = eas.run(
                [
                    "build",
                    "--platform",
                    args.platform,
                    "--profile",
                    profile(config),
                    "--json",
                    "--non-interactive",
                    "--freeze-credentials",
                    "--wait",
                ],
                True,
            )
            if not isinstance(rows, list) or len(rows) != 1:
                raise Gate("Expected one deliberately selected store build")
            built = eas.run(["build:view", rows[0]["id"], "--json"], True)
            metadata = verify_build(
                built, config, args.platform, revision, rows[0]["id"]
            )
            artifact = Path(directory) / (
                "application.aab" if args.platform == "android" else "application.ipa"
            )
            content = download_artifact(
                built.get("artifacts", {}).get("applicationArchiveUrl"),
                config,
                artifact,
            )
            inspection = (
                inspect_android(artifact, config, metadata)
                if args.platform == "android"
                else inspect_ios(artifact, config, metadata)
            )
            eas.verify_environment(config)
            if (
                source_revision() != revision
                or verify_backend(args, config, revision) != backend
            ):
                raise Gate(
                    "Source or release/gate/backend authority changed during the cloud build"
                )
            created = now()
            payload = {
                "schema_version": "1.0.0",
                "purpose": "mobile-store-build",
                "source_revision": revision,
                "config_sha256": config_digest(config),
                "eas_config_sha256": resolved_sha,
                "platform": args.platform,
                "environment": config["environment"],
                "profile": profile(config),
                "project_id": config["project_id"],
                "eas_cli_version": EAS_VERSION,
                "build": metadata,
                "artifact": {**content, **inspection},
                "backend": backend,
                "created_at": created.isoformat().replace("+00:00", "Z"),
                "expires_at": (created + timedelta(days=7))
                .isoformat()
                .replace("+00:00", "Z"),
                "store_availability": "not_submitted",
                "public_release": False,
            }
        else:
            if not args.receipt:
                raise Gate(
                    "Supply the exact signed mobile build receipt; --latest is never selected"
                )
            saved = receipt(args, config, revision)
            built = eas.run(["build:view", saved["build"]["id"], "--json"], True)
            if (
                verify_build(
                    built, config, args.platform, revision, saved["build"]["id"]
                )
                != saved["build"]
                or saved["backend"] != backend
                or saved["eas_config_sha256"] != resolved_sha
            ):
                raise Gate(
                    "The exact signed binary or its release configuration/authority changed"
                )
            artifact = Path(directory) / (
                "application.aab" if args.platform == "android" else "application.ipa"
            )
            if download_artifact(
                built.get("artifacts", {}).get("applicationArchiveUrl"),
                config,
                artifact,
            ) != {k: saved["artifact"][k] for k in ("sha256", "size_bytes")}:
                raise Gate("Store artifact bytes differ from the signed build receipt")
            inspected = (
                inspect_android(artifact, config, saved["build"])
                if args.platform == "android"
                else inspect_ios(artifact, config, saved["build"])
            )
            if any(saved["artifact"].get(k) != v for k, v in inspected.items()):
                raise Gate("Store signer verification differs from the signed receipt")
            settings = json.loads((cwd / "eas.json").read_text())
            submit_config = submission_profile(config, args.platform)
            cli_submit_config = json.loads(json.dumps(submit_config))
            selector = (
                "serviceAccountKeyPath"
                if args.platform == "android"
                else "ascApiKeyPath"
            )
            cli_submit_config[args.platform][selector] = str(
                stage_credential(submit_config[args.platform][selector], directory)
            )
            settings["submit"][profile(config)] = cli_submit_config
            (cwd / "eas.json").write_text(json.dumps(settings))
            if (
                verify_backend(args, config, revision) != backend
                or source_revision() != revision
            ):
                raise Gate("Release authority changed before submission")
            eas.verify_environment(config)
            intent_path = Path(str(args.output) + ".intent.json")
            request = {
                "schema_version": "1.0.0",
                "purpose": "mobile-store-submission-intent",
                "source_revision": revision,
                "config_sha256": config_digest(config),
                "platform": args.platform,
                "build_id": saved["build"]["id"],
                "build_receipt_sha256": hashlib.sha256(
                    args.receipt.read_bytes()
                ).hexdigest(),
                "submission_config_sha256": submission_digest(submit_config),
            }
            if intent_path.exists():
                pending = verify_signed_record(intent_path, args.trusted_public_key)
                if {k: pending.get(k) for k in request} != request or not utc(
                    pending["created_at"]
                ) <= now() < utc(pending["expires_at"]):
                    raise Gate(
                        "Pending store intent belongs to another or expired immutable request"
                    )
                if not args.submission_id:
                    raise Gate(
                        "An earlier store submission may have been accepted. Reconcile its exact EAS submission UUID; no new request is launched"
                    )
                submission_id = args.submission_id
            else:
                if args.submission_id:
                    raise Gate(
                        "A submission UUID cannot replace a missing original signed intent"
                    )
                created = now()
                preserve_submission_intent(
                    {
                        **request,
                        "created_at": created.isoformat().replace("+00:00", "Z"),
                        "expires_at": (created + timedelta(days=7))
                        .isoformat()
                        .replace("+00:00", "Z"),
                    },
                    intent_path,
                    args.signing_key,
                )
                text = eas.run(
                    [
                        "submit",
                        "--platform",
                        args.platform,
                        "--profile",
                        profile(config),
                        "--id",
                        saved["build"]["id"],
                        "--non-interactive",
                        "--wait",
                        "--no-auto-testflight-setup",
                    ]
                )
                links = re.findall(
                    r"https://expo\.dev/accounts/"
                    + re.escape(config["expo_account"])
                    + r"/projects/"
                    + SLUG
                    + r"/submissions/([0-9a-f-]{36})",
                    re.sub(r"\x1b\[[0-9;]*m", "", text),
                )
                if len(set(links)) != 1:
                    raise Gate(
                        "Submission response lacks an unambiguous exact EAS submission receipt; reconcile in Expo before retry"
                    )
                submission_id = links[0]
            if not UUID.fullmatch(str(submission_id)):
                raise Gate("Expected the exact EAS submission UUID")
            actual = eas.run(["submit:view", submission_id, "--json"], True)
            accepted = verify_submission(
                actual, config, args.platform, saved["build"]["id"]
            )
            payload = {
                "schema_version": "1.0.0",
                "purpose": "mobile-store-submission",
                "source_revision": revision,
                "config_sha256": config_digest(config),
                "build_receipt_sha256": hashlib.sha256(
                    args.receipt.read_bytes()
                ).hexdigest(),
                "submission_config_sha256": submission_digest(submit_config),
                "backend": backend,
                "submission_intent_sha256": hashlib.sha256(
                    intent_path.read_bytes()
                ).hexdigest(),
                "created_at": now().isoformat().replace("+00:00", "Z"),
                **accepted,
            }
        cloud.sign_release(payload, args.output, args.signing_key)
        return {
            "receipt": str(args.output),
            "purpose": payload["purpose"],
            "store_availability": payload["store_availability"],
            "public_release": False,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "build", "submit", "status"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--platform", required=True, choices=("android", "ios"))
    for field in (
        "backend-config",
        "backend-release",
        "gate-evidence",
        "trusted-public-key",
        "qa-evidence",
        "signing-key",
        "output",
        "receipt",
        "submission-receipt",
    ):
        parser.add_argument("--" + field, type=Path)
    parser.add_argument("--aws-profile")
    parser.add_argument("--submission-id")
    try:
        print(json.dumps(execute(parser.parse_args()), indent=2))
    except (
        Gate,
        OSError,
        ValueError,
        subprocess.SubprocessError,
        httpx.HTTPError,
    ) as error:
        print(
            "Store release blocked: "
            + (
                str(error)
                if isinstance(error, Gate)
                else "required tool, transport or artifact verification failed"
            ),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
