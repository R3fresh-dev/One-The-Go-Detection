"""Fictional software release fixtures; no Expo, Apple, Google or AWS mutations."""

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import os
import plistlib
import stat
import struct
import subprocess
import sys
import tarfile
import time
import zipfile
from copy import deepcopy
from datetime import timedelta
from pathlib import Path

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "store_release", ROOT / "apps/mobile/modules/scripts/store_release.py"
)
store = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = store
SPEC.loader.exec_module(store)

PROJECT = "11111111-1111-4111-8111-111111111111"
BUILD = "22222222-2222-4222-8222-222222222222"
SUBMISSION = "33333333-3333-4333-8333-333333333333"
REVISION = "a" * 40


@pytest.fixture
def config(tmp_path):
    google, apple = tmp_path / "google.json", tmp_path / "apple.p8"
    google.write_text("FICTIONAL TEST ONLY NOT A SERVICE ACCOUNT")
    apple.write_text("FICTIONAL TEST ONLY NOT AN APPLE KEY")
    google.chmod(0o600)
    apple.chmod(0o600)
    return {
        "schema_version": "1.0.0",
        "environment": "prod",
        "project_id": PROJECT,
        "expo_account": "fictional-engineering",
        "api_url": "https://api.engineering-research.org",
        "oauth_issuer": "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_ENGINEERING",
        "oauth_origin": "https://hosted.engineering-research.org",
        "oauth_web_callback_uri": "https://web.engineering-research.org/",
        "oauth_client_id": "fictionalclientwithoutreservedword".replace(
            "fictional", "unit"
        ),
        "artifact_hosts": ["artifacts.engineering-research.org"],
        "bundletool_jar": str(tmp_path / "bundletool.jar"),
        "android": {
            "upload_certificate_sha256": "b" * 64,
            "service_account_key_path": str(google),
        },
        "ios": {
            "asc_app_id": "1234567890",
            "apple_team_id": "UNITTEAM01",
            "distribution_certificate_sha256": "c" * 64,
            "api_key_path": str(apple),
            "api_key_id": "UNITKEY001",
            "api_issuer_id": PROJECT,
        },
    }


def resolved(config, platform):
    return {
        "buildProfile": {
            "distribution": "store",
            "developmentClient": False,
            "environment": "preview" if config["environment"] == "qa" else "production",
            "env": {"EXPO_PUBLIC_HOSTED_PREVIEW": "false"},
            **(
                {"buildType": "app-bundle"}
                if platform == "android"
                else {"simulator": False}
            ),
        },
        "appConfig": {
            "slug": store.SLUG,
            "android": {"package": store.identity(config)},
            "ios": {"bundleIdentifier": store.identity(config)},
            "extra": {
                "environment": config["environment"],
                "hostedPreview": False,
                "eas": {"projectId": config["project_id"]},
                "apiUrl": config["api_url"],
                "issuer": config["oauth_issuer"],
                "clientId": config["oauth_client_id"],
                "oauthOrigin": config["oauth_origin"],
                "webCallbackUri": config["oauth_web_callback_uri"],
                "redirectUris": ["otgd" + ("-qa" if config["environment"] == "qa" else "") + "://oauth/callback", config["oauth_web_callback_uri"]],
                "redirectUri": "otgd"
                + ("-qa" if config["environment"] == "qa" else "")
                + "://oauth/callback",
            },
        },
    }


def built(config, platform):
    return {
        "id": BUILD,
        "status": "FINISHED",
        "platform": platform.upper(),
        "distribution": "STORE",
        "buildProfile": store.profile(config),
        "appIdentifier": store.identity(config),
        "appVersion": "0.2.0",
        "appBuildVersion": "42",
        "gitCommitHash": REVISION,
        "isForIosSimulator": False,
        "expirationDate": (store.now() + timedelta(days=14))
        .isoformat()
        .replace("+00:00", "Z"),
        "app": {
            "id": PROJECT,
            "slug": store.SLUG,
            "ownerAccount": {"name": config["expo_account"]},
        },
        "artifacts": {
            "applicationArchiveUrl": "https://artifacts.engineering-research.org/private-signed-url?token=TEST_ONLY"
        },
    }


def submitted(config, platform):
    result = {
        "id": SUBMISSION,
        "status": "FINISHED",
        "platform": platform.upper(),
        "app": built(config, platform)["app"],
        "submittedBuild": built(config, platform),
    }
    result["androidConfig" if platform == "android" else "iosConfig"] = (
        {
            "track": "internal" if config["environment"] == "qa" else "production",
            "releaseStatus": "DRAFT",
        }
        if platform == "android"
        else {"ascAppIdentifier": config["ios"]["asc_app_id"]}
    )
    return result


def write_config(config, tmp_path):
    path = tmp_path / "release.json"
    path.write_text(json.dumps(config))
    return path


def test_plan_is_pure_and_profiles_cannot_publish_automatically(
    config, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        store,
        "source_revision",
        lambda: pytest.fail("plan must not inspect source/network"),
    )
    monkeypatch.setattr(
        store, "Eas", lambda *a: pytest.fail("plan must not launch an external tool")
    )
    monkeypatch.setattr(
        store,
        "private_file",
        lambda *a: pytest.fail("plan must not open credential files"),
    )
    result = store.execute(
        argparse.Namespace(
            action="plan", config=write_config(config, tmp_path), platform="android"
        )
    )
    assert (
        result["action"] == "plan_only"
        and result["required_gates"] == 13
        and result["public_release"] is False
    )
    profiles = json.loads((ROOT / "apps/mobile/eas.json").read_text())
    assert profiles["cli"] == {
        "version": store.EAS_VERSION,
        "appVersionSource": "remote",
        "requireCommit": True,
    }
    for name, environment in (("qa-store", "qa"), ("production", "prod")):
        p = profiles["build"][name]
        assert (
            p["distribution"] == "store"
            and p["android"]["buildType"] == "app-bundle"
            and p["ios"]["simulator"] is False
        )
        assert (
            p["autoIncrement"] is True
            and p["env"]["EXPO_PUBLIC_HOSTED_PREVIEW"] == "false"
            and p["env"]["APP_ENV"] == environment
        )
        assert profiles["submit"][name]["android"]["releaseStatus"] == "draft"
        assert profiles["submit"][name]["android"]["changesNotSentForReview"] is True
    assert profiles["build"]["qa"]["distribution"] == "internal"


@pytest.mark.parametrize("field", ["oauth_origin", "oauth_web_callback_uri"])
def test_current_mobile_config_requires_independent_oauth_pins(config, tmp_path, field):
    changed = deepcopy(config)
    changed.pop(field, None)
    with pytest.raises(store.Gate):
        store.read_config(write_config(changed, tmp_path))


@pytest.mark.parametrize(
    "field,value",
    [
        ("environment", "local"),
        ("project_id", "not-a-project"),
        ("api_url", "https://unavailable.invalid"),
        ("api_url", "http://api.engineering-research.org"),
        ("api_url", "https://user:secret@api.engineering-research.org"),
        ("oauth_client_id", "otgd-local"),
        ("oauth_origin", "https://hosted.engineering-research.org/oauth2/token"),
        ("oauth_origin", "https://hosted.engineering-research.org/?override=1"),
        ("oauth_origin", "https://hosted.engineering-research.org#override"),
        ("oauth_origin", "https://user@hosted.engineering-research.org"),
        ("oauth_origin", "https://hosted.engineering-research.org:443"),
        ("oauth_web_callback_uri", "https://web.engineering-research.org/extra"),
        ("oauth_web_callback_uri", "https://web.engineering-research.org/?override=1"),
        ("oauth_web_callback_uri", "https://web.engineering-research.org/#override"),
        ("oauth_web_callback_uri", "https://user@web.engineering-research.org/"),
        ("artifact_hosts", ["*.amazonaws.com"]),
        ("extra_field", True),
    ],
)
def test_release_config_rejects_local_guest_or_ambiguous_targets(
    config, tmp_path, field, value
):
    config[field] = value
    with pytest.raises(store.Gate):
        store.read_config(write_config(config, tmp_path))


def test_selected_platform_only_and_private_files_are_bounded(config, tmp_path):
    config["ios"] = None
    assert store.read_config(write_config(config, tmp_path))["ios"] is None
    secret = Path(config["android"]["service_account_key_path"])
    assert store.private_file(secret) == secret
    copy = store.stage_credential(secret, tmp_path)
    assert copy.read_bytes() == secret.read_bytes() and copy.stat().st_mode & 0o077 == 0
    copy.unlink()
    secret.chmod(0o644)
    with pytest.raises(store.Gate):
        store.private_file(secret)
    secret.chmod(0o600)
    alias = tmp_path / "alias"
    alias.symlink_to(secret)
    with pytest.raises(store.Gate):
        store.stage_credential(alias, tmp_path)


def test_tool_environment_preserves_transport_but_never_builds_with_service_secrets(
    config, monkeypatch
):
    for name in (
        "AWS_SECRET_ACCESS_KEY",
        "GH_ADMIN_TOKEN",
        "OTGD_DATABASE_URL",
        "APPETIZE_API_TOKEN",
        "NODE_OPTIONS",
        "EXPO_TOKEN",
        "npm_config_registry",
    ):
        monkeypatch.setenv(name, "TEST_ONLY_MUST_NOT_ENTER_PUBLIC_BUILD")
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy:8080")
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", "/trusted/public-ca.pem")
    env = store.build_environment(config)
    assert (
        env["HTTPS_PROXY"] == "http://proxy:8080"
        and env["NODE_EXTRA_CA_CERTS"] == "/trusted/public-ca.pem"
    )
    assert env["npm_config_registry"] == "https://registry.npmjs.org"
    assert not any(
        name in env
        for name in (
            "AWS_SECRET_ACCESS_KEY",
            "GH_ADMIN_TOKEN",
            "OTGD_DATABASE_URL",
            "APPETIZE_API_TOKEN",
            "NODE_OPTIONS",
            "EXPO_TOKEN",
        )
    )


@pytest.mark.parametrize("platform", ["android", "ios"])
def test_exact_cloud_metadata_and_embedded_public_origins_bind_store_build(
    config, platform
):
    value = resolved(config, platform)
    assert store.verify_eas_config(value, config, platform)
    store.verify_embedded_config(value["appConfig"], config)
    for location, field, bad in [
        ("extra", "hostedPreview", True),
        ("extra", "environment", "local"),
        ("extra", "apiUrl", "https://unavailable.invalid"),
    ]:
        altered = deepcopy(value)
        altered["appConfig"][location][field] = bad
        with pytest.raises(store.Gate):
            store.verify_eas_config(altered, config, platform)
        with pytest.raises(store.Gate):
            store.verify_embedded_config(altered["appConfig"], config)
    actual = built(config, platform)
    assert store.verify_build(actual, config, platform, REVISION)["id"] == BUILD
    for field, bad in [
        ("status", "IN_PROGRESS"),
        ("distribution", "INTERNAL"),
        ("gitCommitHash", "b" * 40),
        ("isForIosSimulator", True),
        ("appIdentifier", "dev.r3fresh.otgd.local"),
        ("appBuildVersion", "1.5"),
    ]:
        altered = {**actual, field: bad}
        with pytest.raises(store.Gate):
            store.verify_build(altered, config, platform, REVISION)
    actual["app"]["ownerAccount"]["name"] = "foreign-account"
    with pytest.raises(store.Gate):
        store.verify_build(actual, config, platform, REVISION)
    expired = built(config, platform)
    expired["expirationDate"] = (
        (store.now() - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    )
    with pytest.raises(store.Gate):
        store.verify_build(expired, config, platform, REVISION)
    assert (
        store.verify_build(expired, config, platform, REVISION, allow_expired=True)[
            "id"
        ]
        == BUILD
    )


def test_download_redirects_are_credential_free_bound_and_do_not_record_signed_urls(
    config, tmp_path
):
    calls = []

    def handler(request):
        calls.append(request)
        assert (
            "authorization" not in request.headers and "cookie" not in request.headers
        )
        if request.url.path == "/redirect":
            return httpx.Response(302, headers={"Location": "/bytes?private=TEST_ONLY"})
        return httpx.Response(200, content=b"fictional archive bytes")

    with httpx.Client(
        transport=httpx.MockTransport(handler), follow_redirects=False
    ) as client:
        record = store.download_artifact(
            "https://artifacts.engineering-research.org/redirect",
            config,
            tmp_path / "application",
            client=client,
        )
    assert record == {
        "sha256": hashlib.sha256(b"fictional archive bytes").hexdigest(),
        "size_bytes": 23,
    }
    assert len(calls) == 2 and "url" not in record
    with (
        httpx.Client(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(
                    302, headers={"Location": "https://foreign.cloud.org/steal"}
                )
            )
        ) as client,
        pytest.raises(store.Gate),
    ):
        store.download_artifact(
            "https://artifacts.engineering-research.org/redirect",
            config,
            tmp_path / "foreign",
            client=client,
        )
    assert not (tmp_path / "foreign").exists()


def android_manifest(config):
    return f'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{store.identity(config)}" android:versionName="0.2.0" android:versionCode="42"><uses-sdk android:minSdkVersion="24" android:targetSdkVersion="36"/><application android:debuggable="false" android:usesCleartextTraffic="false"/></manifest>'.encode()


def test_actual_manifest_policy_rejects_guest_debug_cleartext_sdk_and_path_traversal(
    config,
):
    raw = android_manifest(config)
    store.verify_android_manifest(raw, config, built(config, "android"))
    for altered in [
        raw.replace(b'debuggable="false"', b'debuggable="true"'),
        raw.replace(b'Traffic="false"', b'Traffic="true"'),
        raw.replace(b'Version="36"', b'Version="35"'),
        raw.replace(b"dev.r3fresh.otgd", b"dev.r3fresh.otgd.local"),
        raw.replace(
            b"/></manifest>",
            b'><meta-data android:name="dev.r3fresh.otgd.HOSTED_PREVIEW" android:value="true"/></application></manifest>',
        ),
    ]:
        with pytest.raises((store.Gate, store.ET.ParseError)):
            store.verify_android_manifest(altered, config, built(config, "android"))
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("../escape", b"x")
    with (
        zipfile.ZipFile(io.BytesIO(output.getvalue())) as archive,
        pytest.raises(store.Gate),
    ):
        store.archive_entries(archive)


def test_actual_submission_receipt_never_means_public_store_availability(config):
    for platform in ("android", "ios"):
        value = submitted(config, platform)
        result = store.verify_submission(value, config, platform, BUILD)
        assert (
            result["public_release"] is False
            and result["store_availability"] == "not_verified"
        )
        altered = deepcopy(value)
        altered["submittedBuild"]["id"] = SUBMISSION
        with pytest.raises(store.Gate):
            store.verify_submission(altered, config, platform, BUILD)
    value = submitted(config, "android")
    for field, bad in [
        ("releaseStatus", "COMPLETED"),
        ("rollout", 1),
        ("track", "internal"),
    ]:
        altered = deepcopy(value)
        altered["androidConfig"][field] = bad
        with pytest.raises(store.Gate):
            store.verify_submission(altered, config, "android", BUILD)


@pytest.fixture
def flow(config, tmp_path, monkeypatch):
    events, faults = [], {}
    key = Ed25519PrivateKey.generate()
    private, public = tmp_path / "release.key", tmp_path / "release.pub"
    private.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    private.chmod(0o600)
    public.write_bytes(
        key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    cwd = tmp_path / "isolated-app"
    cwd.mkdir()
    settings = json.loads((ROOT / "apps/mobile/eas.json").read_text())
    (cwd / "eas.json").write_text(json.dumps(settings))
    monkeypatch.setattr(store, "source_revision", lambda: REVISION)
    monkeypatch.setattr(store, "isolated_source", lambda *a: cwd)

    def backend(*a):
        events.append("backend")
        if faults.get("backend"):
            raise store.Gate("actual backend authority unavailable")
        return {
            "release_sha256": "1" * 64,
            "gate_provenance_sha256": "2" * 64,
            "api_config_sha256": "3" * 64,
        }

    monkeypatch.setattr(store, "verify_backend", backend)

    def public_command(args, **kwargs):
        assert args == ["npm", "ci"] and "EXPO_TOKEN" not in kwargs["env"]
        events.append("npm-ci-public")

    monkeypatch.setattr(store, "command", public_command)

    class FakeEas:
        def __init__(self, *a):
            pass

        def verify_environment(self, c):
            events.append("remote-public-config")

        def verify_project(self, c):
            events.append("actual-project-owner")

        def run(self, args, json_result=False):
            events.append(args)
            platform = options.platform
            if args[0] == "config":
                return resolved(config, platform)
            if args[0] == "build":
                assert "--latest" not in args and "--freeze-credentials" in args
                return [built(config, platform)]
            if args[0] == "build:view":
                return built(config, platform)
            if args[0] == "submit":
                assert (
                    args[args.index("--id") + 1] == BUILD
                    and "--latest" not in args
                    and "--json" not in args
                )
                assert "--no-auto-testflight-setup" in args
                if faults.pop("unknown", False):
                    raise store.Gate("accepted external request response lost")
                return f"Submission details: https://expo.dev/accounts/{config['expo_account']}/projects/{store.SLUG}/submissions/{SUBMISSION}"
            if args[0] == "submit:view":
                return submitted(config, platform)
            pytest.fail(str(args))

    monkeypatch.setattr(store, "Eas", FakeEas)
    monkeypatch.setattr(
        store,
        "download_artifact",
        lambda *a, **k: {"sha256": "4" * 64, "size_bytes": 100},
    )
    monkeypatch.setattr(
        store,
        "inspect_android",
        lambda *a: {"format": "aab", "signer_sha256": "b" * 64},
    )
    monkeypatch.setattr(
        store, "inspect_ios", lambda *a: {"format": "ipa", "signer_sha256": "c" * 64}
    )
    options = argparse.Namespace(
        action="build",
        config=write_config(config, tmp_path),
        platform="android",
        backend_config=tmp_path / "backend.json",
        backend_release=tmp_path / "backend-release.json",
        gate_evidence=tmp_path / "gates.json",
        trusted_public_key=public,
        qa_evidence=tmp_path / "qa.json",
        signing_key=private,
        output=tmp_path / "build-receipt.json",
        receipt=None,
        aws_profile=None,
        submission_id=None,
        submission_receipt=None,
    )
    return options, events, faults


@pytest.mark.parametrize("platform", ["android", "ios"])
def test_exact_build_inspection_then_explicit_draft_submission_and_status_have_signed_distinct_receipts(
    flow, config, platform
):
    args, events, _ = flow
    args.platform = platform
    result = store.execute(args)
    assert (
        result["purpose"] == "mobile-store-build"
        and result["store_availability"] == "not_submitted"
    )
    build_path = args.output
    args.action, args.receipt, args.output = (
        "submit",
        build_path,
        build_path.parent / "submission-receipt.json",
    )
    result = store.execute(args)
    assert (
        result["public_release"] is False
        and result["store_availability"] == "not_verified"
    )
    assert any(isinstance(e, list) and e[0] == "submit:view" for e in events)
    intent = store.verify_signed_record(
        Path(str(args.output) + ".intent.json"), args.trusted_public_key
    )
    assert intent["build_id"] == BUILD and intent["platform"] == platform
    args.action, args.submission_receipt = "status", args.output
    result = store.execute(args)
    assert (
        result["eas_submission_status"] == "FINISHED"
        and result["store_availability"] == "not_verified"
    )


def test_lost_submission_response_persists_exact_intent_and_reconciles_without_second_upload(
    flow,
):
    args, events, faults = flow
    store.execute(args)
    args.action, args.receipt, args.output = (
        "submit",
        args.output,
        args.output.parent / "submit.json",
    )
    faults["unknown"] = True
    with pytest.raises(store.Gate, match="response lost"):
        store.execute(args)
    intent_path = Path(str(args.output) + ".intent.json")
    assert intent_path.exists() and not args.output.exists()
    original = intent_path.read_bytes()
    with pytest.raises(store.Gate, match="earlier store submission"):
        store.execute(args)
    args.submission_id = SUBMISSION
    store.execute(args)
    assert intent_path.read_bytes() == original
    assert len([e for e in events if isinstance(e, list) and e[0] == "submit"]) == 1


def test_submission_persists_signed_owner_only_fence_before_provider_call(
    flow, monkeypatch
):
    args, events, _ = flow
    store.execute(args)
    args.action, args.receipt, args.output = (
        "submit",
        args.output,
        args.output.parent / "durable-submission.json",
    )
    intent_path = Path(str(args.output) + ".intent.json")
    real_fsync = os.fsync

    def observe_sync(descriptor):
        metadata = os.fstat(descriptor)
        boundary = (
            "intent-directory-fsync"
            if stat.S_ISDIR(metadata.st_mode)
            else "intent-file-fsync"
        )
        events.append(boundary)
        assert not any(isinstance(e, list) and e[0] == "submit" for e in events)
        assert (
            store.verify_signed_record(intent_path, args.trusted_public_key)["build_id"]
            == BUILD
        )
        assert stat.S_IMODE(intent_path.stat().st_mode) == 0o600
        real_fsync(descriptor)

    monkeypatch.setattr(store.os, "fsync", observe_sync)
    store.execute(args)
    file_index = events.index("intent-file-fsync")
    directory_index = events.index("intent-directory-fsync")
    submit_index = next(
        i for i, e in enumerate(events) if isinstance(e, list) and e[0] == "submit"
    )
    assert file_index < directory_index < submit_index


@pytest.mark.parametrize("failure", ["file", "directory"])
def test_fsync_failure_leaves_fence_and_never_launches_store_upload(
    flow, monkeypatch, failure
):
    args, events, _ = flow
    store.execute(args)
    args.action, args.receipt, args.output = (
        "submit",
        args.output,
        args.output.parent / "uncommitted-submission.json",
    )
    real_fsync = os.fsync

    def fail_sync(descriptor):
        boundary = "directory" if stat.S_ISDIR(os.fstat(descriptor).st_mode) else "file"
        if boundary == failure:
            raise OSError("fictional storage barrier failure")
        real_fsync(descriptor)

    monkeypatch.setattr(store.os, "fsync", fail_sync)
    with pytest.raises(store.Gate, match="durably preserved"):
        store.execute(args)
    assert not any(isinstance(e, list) and e[0] == "submit" for e in events)
    assert Path(str(args.output) + ".intent.json").exists() and not args.output.exists()
    with pytest.raises(store.Gate, match="earlier store submission"):
        store.execute(args)


def test_remote_runner_selectors_move_without_relabeling_signed_public_release_scope(
    flow, config, tmp_path
):
    args, _, _ = flow
    store.execute(args)
    original_digest = store.config_digest(config)
    original_profile_digest = store.submission_digest(
        store.submission_profile(config, "android")
    )
    relocated = tmp_path / "different-runner-private-directory"
    relocated.mkdir(mode=0o700)
    for section, selector in (
        ("android", "service_account_key_path"),
        ("ios", "api_key_path"),
    ):
        old = Path(config[section][selector])
        changed = relocated / old.name
        changed.write_bytes(old.read_bytes())
        changed.chmod(0o600)
        config[section][selector] = str(changed)
    config["bundletool_jar"] = str(relocated / "bundletool.jar")
    assert store.config_digest(config) == original_digest
    assert (
        store.submission_digest(store.submission_profile(config, "android"))
        == original_profile_digest
    )
    args.config.write_text(json.dumps(config))
    args.action, args.receipt, args.output = (
        "submit",
        args.output,
        tmp_path / "relocated-submission.json",
    )
    assert store.execute(args)["purpose"] == "mobile-store-submission"
    foreign = deepcopy(config)
    foreign["android"]["upload_certificate_sha256"] = "d" * 64
    assert store.config_digest(foreign) != original_digest


def test_no_backend_release_no_new_store_job_and_immutable_output_refuses_reuse(flow):
    args, events, faults = flow
    faults["backend"] = True
    with pytest.raises(store.Gate):
        store.execute(args)
    assert not any(isinstance(e, list) and e[0] == "build" for e in events)
    faults["backend"] = False
    store.execute(args)
    with pytest.raises(store.Gate, match="immutable"):
        store.execute(args)


def test_subprocess_contract_bounds_output_and_rejects_unknown_json_or_environment_pull(
    config, tmp_path
):
    env = store.build_environment(config)
    assert store.command(
        [sys.executable, "-c", 'print("{\\"ok\\":true}")'],
        cwd=tmp_path,
        env=env,
        json_result=True,
    ) == {"ok": True}
    assert (
        store.command(
            [sys.executable, "-c", 'print("plain")'], cwd=tmp_path, env=env
        ).strip()
        == "plain"
    )
    for script in [
        'print("not JSON")',
        'print("{\\"a\\":1,\\"a\\":2}")',
        "raise SystemExit(2)",
        'import sys;sys.stderr.write("Failed to pull env variables")',
        'print("x"*2100000)',
    ]:
        with pytest.raises(store.Gate):
            store.command(
                [sys.executable, "-c", script], cwd=tmp_path, env=env, json_result=True
            )


def test_pinned_tool_package_integrity_and_actual_public_eas_variable_scope(
    config, tmp_path, monkeypatch
):
    files = {
        "bin/run": b"FICTIONAL CLI EXECUTION BOUNDARY",
        "package.json": b'{"name":"eas-cli"}',
    }
    packed = io.BytesIO()
    with tarfile.open(fileobj=packed, mode="w:gz") as output:
        for name, content in files.items():
            item = tarfile.TarInfo("package/" + name)
            item.size = len(content)
            output.addfile(item, io.BytesIO(content))
    archive = packed.getvalue()
    expected = "sha512-" + base64.b64encode(hashlib.sha512(archive).digest()).decode()
    monkeypatch.setattr(store, "EAS_INTEGRITY", expected)
    old_client = httpx.Client
    corrupt = [False]

    def handler(request):
        if request.url.path.endswith(".tgz"):
            return httpx.Response(
                200, content=archive + (b"changed" if corrupt[0] else b"")
            )
        return httpx.Response(
            200,
            json={
                "version": store.EAS_VERSION,
                "dist": {
                    "integrity": expected,
                    "tarball": "https://registry.npmjs.org/eas-cli/-/eas-cli-"
                    + store.EAS_VERSION
                    + ".tgz",
                },
            },
        )

    monkeypatch.setattr(
        store.httpx,
        "Client",
        lambda **kwargs: old_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    manifest = store.verify_eas_package()
    corrupt[0] = True
    with pytest.raises(store.Gate, match="integrity verification"):
        store.verify_eas_package()
    monkeypatch.delenv("EXPO_TOKEN", raising=False)
    with pytest.raises(store.Gate, match="EXPO_TOKEN"):
        store.Eas(tmp_path, config)
    monkeypatch.setenv("EXPO_TOKEN", "TEST_ONLY_AUTH_BOUNDARY")
    monkeypatch.setattr(store, "verify_eas_package", lambda: manifest)
    tool = tmp_path / "distribution/eas-toolchain"
    tool.mkdir(parents=True)
    (tool / "package-lock.json").write_text(
        json.dumps({"packages": {"node_modules/eas-cli": {"integrity": expected}}})
    )
    seen = []

    def run_tool(args, **kw):
        seen.append((args, kw))
        if args[0] == "npm":
            assert "EXPO_TOKEN" not in kw["env"]
            for name, content in files.items():
                path = tool / "node_modules/eas-cli" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            return ""
        assert args[:2] == ["node", str(tool / "node_modules/eas-cli/bin/run")]
        assert kw["env"]["EXPO_TOKEN"] == "TEST_ONLY_AUTH_BOUNDARY"
        if args[-1] == "--version":
            return "eas-cli/" + store.EAS_VERSION + " linux-x64 node-v24"
        if args[-1] == "project:info":
            return f"fullName  @{config['expo_account']}/{store.SLUG}\nID        {PROJECT}\n"
        name = args[args.index("--variable-name") + 1]
        return (
            name
            + "="
            + {
                "EXPO_PUBLIC_API_URL": config["api_url"],
                "EXPO_PUBLIC_OAUTH_ISSUER": config["oauth_issuer"],
                "EXPO_PUBLIC_OAUTH_CLIENT_ID": config["oauth_client_id"],
                "EXPO_PUBLIC_OAUTH_ORIGIN": config["oauth_origin"],
                "EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI": config["oauth_web_callback_uri"],
            }[name]
        )

    monkeypatch.setattr(store, "command", run_tool)
    eas = store.Eas(tmp_path, config)
    eas.verify_project(config)
    eas.verify_environment(config)
    assert len(seen) == 8
    assert all(
        "--scope" not in command or command[command.index("--scope") + 1] == "project"
        for command, _ in seen
    )
    monkeypatch.setattr(eas, "run", lambda *args: "")
    with pytest.raises(store.Gate, match="absent"):
        eas.verify_environment(config)
    with pytest.raises(store.Gate, match="project/account"):
        eas.verify_project(config)
    (tool / "node_modules/eas-cli/bin/run").write_bytes(b"altered installed CLI")
    with pytest.raises(store.Gate, match="executable source"):
        store.verify_cli_tree(tool / "node_modules/eas-cli", manifest)


def test_owned_tool_process_group_stops_spawned_child_on_bounded_failure(
    config, tmp_path, monkeypatch
):
    marker, ready = tmp_path / "child-side-effect", tmp_path / "child-ready"
    child = f"import pathlib,time;pathlib.Path({str(ready)!r}).touch();time.sleep(0.8);pathlib.Path({str(marker)!r}).touch()"
    parent = f"import subprocess,sys,time,pathlib;subprocess.Popen([sys.executable,'-c',{child!r}]);p=pathlib.Path({str(ready)!r});\nwhile not p.exists(): time.sleep(0.01)\nprint('x'*8192,flush=True);time.sleep(30)"
    monkeypatch.setattr(store, "COMMAND_MAX_OUTPUT", 4096)
    with pytest.raises(store.Gate, match="bounded output/time"):
        store.command(
            [sys.executable, "-c", parent],
            cwd=tmp_path,
            env=store.build_environment(config),
        )
    time.sleep(1)
    assert ready.exists() and not marker.exists()


def test_owned_child_is_stopped_even_when_tool_parent_exits_before_cleanup(
    config, tmp_path
):
    marker, ready = tmp_path / "orphan-effect", tmp_path / "orphan-ready"
    child = f"import pathlib,time;pathlib.Path({str(ready)!r}).touch();time.sleep(0.8);pathlib.Path({str(marker)!r}).touch()"
    parent = f"import subprocess,sys,time,pathlib;subprocess.Popen([sys.executable,'-c',{child!r}]);p=pathlib.Path({str(ready)!r});\nwhile not p.exists(): time.sleep(0.01)\nprint('completed',flush=True)"
    assert (
        store.command(
            [sys.executable, "-c", parent],
            cwd=tmp_path,
            env=store.build_environment(config),
        ).strip()
        == "completed"
    )
    time.sleep(1)
    assert ready.exists() and not marker.exists()


def test_completed_parent_is_still_rejected_after_original_monotonic_deadline(
    config, tmp_path, monkeypatch
):
    class FinishedProcess:
        pid = 99999999
        returncode = 0

        def poll(self):
            return 0

        def wait(self, **kwargs):
            return 0

    ticks = iter([0, 14401])
    signals = []
    monkeypatch.setattr(store.subprocess, "Popen", lambda *a, **kw: FinishedProcess())
    monkeypatch.setattr(store.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(store.os, "killpg", lambda *a: signals.append(a))
    with pytest.raises(store.Gate, match="finished outside"):
        store.command(
            ["fictional-finished-tool"],
            cwd=tmp_path,
            env=store.build_environment(config),
        )
    assert signals == [(FinishedProcess.pid, store.signal.SIGKILL)]


def test_clean_isolated_source_preserves_exact_git_revision_and_excludes_untracked_files(
    tmp_path, monkeypatch
):
    original = tmp_path / "canonical"
    (original / "apps/mobile").mkdir(parents=True)
    (original / "apps/mobile/eas.json").write_text("{}")
    subprocess.run(["git", "init", str(original)], check=True, capture_output=True)
    subprocess.run(["git", "add", "apps/mobile/eas.json"], cwd=original, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fictional unit",
            "-c",
            "user.email=unit@invalid",
            "commit",
            "-m",
            "fictional unit source",
        ],
        cwd=original,
        check=True,
        capture_output=True,
    )
    revision = store.source_revision(original)
    (original / "preserved-legacy-untracked.txt").write_text(
        "must never enter EAS upload"
    )
    monkeypatch.setattr(store, "ROOT", original)
    copy = store.isolated_source(revision, tmp_path / "stage")
    assert (
        store.source_revision(copy.parents[1]) == revision
        and not (copy.parents[1] / "preserved-legacy-untracked.txt").exists()
    )
    (original / "apps/mobile/eas.json").write_text('{"modified":true}')
    with pytest.raises(store.Gate, match="clean committed"):
        store.source_revision(original)


def test_android_signed_jar_integrity_and_trusted_upload_certificate_reject_changed_bytes(
    config, tmp_path, monkeypatch
):
    # A real cryptographically signed JAR software fixture, not an installable
    # Android app. Bundletool's native manifest extraction is the explicit boundary.
    path = tmp_path / "fixture.aab"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("BundleConfig.pb", b"FICTIONAL SOFTWARE FIXTURE")
        archive.writestr(
            "base/manifest/AndroidManifest.xml", b"FIXTURE SDK EXTRACTION BOUNDARY"
        )
        archive.writestr(
            "base/assets/app.config",
            json.dumps(resolved(config, "android")["appConfig"]),
        )
        archive.writestr(
            "base/assets/index.android.bundle",
            b"FICTIONAL BUNDLE NOT A NATIVE APPLICATION",
        )
    keystore = tmp_path / "upload.p12"
    password = "fictional-unit-password"
    subprocess.run(
        [
            "keytool",
            "-genkeypair",
            "-alias",
            "fixture",
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            "1",
            "-dname",
            "CN=Fictional Software Fixture",
            "-keystore",
            str(keystore),
            "-storepass",
            password,
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "java",
            "--module",
            "jdk.jartool/sun.security.tools.jarsigner.Main",
            "-keystore",
            str(keystore),
            "-storepass",
            password,
            str(path),
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    certificate = subprocess.check_output(
        [
            "keytool",
            "-exportcert",
            "-alias",
            "fixture",
            "-keystore",
            str(keystore),
            "-storepass",
            password,
        ],
        stderr=subprocess.DEVNULL,
    )
    config["android"]["upload_certificate_sha256"] = hashlib.sha256(
        certificate
    ).hexdigest()
    tool = Path(config["bundletool_jar"])
    tool.write_bytes(b"UNIT FIXTURE ONLY NOT BUNDLETOOL")
    monkeypatch.setattr(
        store, "BUNDLETOOL_SHA256", hashlib.sha256(tool.read_bytes()).hexdigest()
    )
    original_output = subprocess.check_output
    monkeypatch.setattr(
        store.subprocess,
        "check_output",
        lambda args, **kw: (
            android_manifest(config)
            if args[0] == "java"
            else original_output(args, **kw)
        ),
    )
    assert (
        store.inspect_android(path, config, built(config, "android"))["signer_sha256"]
        == hashlib.sha256(certificate).hexdigest()
    )
    config["android"]["upload_certificate_sha256"] = "f" * 64
    with pytest.raises(store.Gate, match="signer"):
        store.inspect_android(path, config, built(config, "android"))
    config["android"]["upload_certificate_sha256"] = hashlib.sha256(
        certificate
    ).hexdigest()
    replaced = tmp_path / "altered.aab"
    with zipfile.ZipFile(path) as old, zipfile.ZipFile(replaced, "w") as changed:
        for entry in old.infolist():
            changed.writestr(
                entry.filename,
                b"changed binary"
                if entry.filename.endswith(".bundle")
                else old.read(entry.filename),
            )
    with pytest.raises(store.Gate, match="signature verification"):
        store.inspect_android(replaced, config, built(config, "android"))
    with zipfile.ZipFile(path, "a") as unsigned:
        unsigned.writestr("base/assets/added-unsigned.bin", b"must not be admitted")
    with pytest.raises(store.Gate, match="unsigned entries"):
        store.inspect_android(path, config, built(config, "android"))


def test_ios_fixture_checks_actual_platform_identity_provisioning_and_runtime_tuple(
    config, tmp_path, monkeypatch
):
    # codesign/security are macOS-only boundaries. The bounded device envelope
    # parser runs here without claiming an actually signed or installable IPA.
    certificate = b"FICTIONAL CODE SIGNER CERTIFICATE BOUNDARY"
    config["ios"]["distribution_certificate_sha256"] = hashlib.sha256(
        certificate
    ).hexdigest()
    path = tmp_path / "fixture.ipa"
    prefix = "Payload/Fictional.app/"
    info = {
        "CFBundleIdentifier": store.identity(config),
        "DTPlatformName": "iphoneos",
        "CFBundleExecutable": "Fictional",
        "CFBundleVersion": "42",
        "CFBundleShortVersionString": "0.2.0",
        "MinimumOSVersion": "16.4",
    }
    executable = struct.pack(
        "<8I", 0xFEEDFACF, 0x0100000C, 0, 2, 1, 24, 0, 0
    ) + struct.pack("<6I", 0x32, 24, 2, 0, 0, 0)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(prefix + "Info.plist", plistlib.dumps(info))
        archive.writestr(prefix + "Fictional", executable)
        archive.writestr(prefix + "main.jsbundle", b"FICTIONAL NATIVE BOUNDARY")
        archive.writestr(
            prefix + "embedded.mobileprovision", b"TEST ONLY NATIVE SECURITY BOUNDARY"
        )
        archive.writestr(
            prefix + "EXConstants.bundle/app.config",
            json.dumps(resolved(config, "ios")["appConfig"]),
        )
    monkeypatch.setattr(store.sys, "platform", "darwin")
    flags = {"debug": False, "ad_hoc": False}

    def native_output(args, **kw):
        if args[0] == "codesign":
            return plistlib.dumps(
                {
                    "application-identifier": config["ios"]["apple_team_id"]
                    + "."
                    + store.identity(config),
                    "get-task-allow": flags["debug"],
                }
            )
        return plistlib.dumps(
            {
                "TeamIdentifier": [config["ios"]["apple_team_id"]],
                "ExpirationDate": store.now().replace(tzinfo=None) + timedelta(days=1),
                "DeveloperCertificates": [certificate],
                **(
                    {"ProvisionedDevices": ["fictional-device"]}
                    if flags["ad_hoc"]
                    else {}
                ),
            }
        )

    def native_run(args, **kw):
        if "--extract-certificates" in args:
            Path(args[args.index("--extract-certificates") + 1] + "0").write_bytes(
                certificate
            )
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(store.subprocess, "run", native_run)
    monkeypatch.setattr(store.subprocess, "check_output", native_output)
    assert store.inspect_ios(path, config, built(config, "ios"))["format"] == "ipa"
    flags["debug"] = True
    with pytest.raises(store.Gate, match="debug/ad-hoc"):
        store.inspect_ios(path, config, built(config, "ios"))
    flags["debug"], flags["ad_hoc"] = False, True
    with pytest.raises(store.Gate, match="debug/ad-hoc"):
        store.inspect_ios(path, config, built(config, "ios"))
    monkeypatch.setattr(store.sys, "platform", "linux")
    with pytest.raises(store.Gate, match="requires macOS"):
        store.inspect_ios(path, config, built(config, "ios"))


def test_backend_admission_rechecks_signed_release_actual_running_image_and_live_native_callback(
    config, tmp_path, monkeypatch
):
    c = {
        "environment": "prod",
        "releaseId": REVISION,
        "account": "111111111111",
        "region": "us-east-2",
        "imageDigest": "sha256:" + "d" * 64,
    }
    out = {
        "ReleaseId": REVISION,
        "ImageDigest": c["imageDigest"],
        "ApiOrigin": config["api_url"],
        "Issuer": config["oauth_issuer"],
        "ClientId": config["oauth_client_id"],
        "IdentityOrigin": config["oauth_origin"],
        "WebCallbackUri": config["oauth_web_callback_uri"],
        "Cluster": "unit-cluster",
        "ApiService": "api",
        "WorkerService": "worker",
    }
    faults = {"rollout": False, "image": False, "callback": False, "endpoint": False}

    class Client:
        def get_caller_identity(self):
            return {"Account": c["account"]}

        def describe_services(self, **kw):
            return {
                "services": [
                    {
                        "serviceName": name,
                        "status": "ACTIVE",
                        "desiredCount": 1,
                        "runningCount": 1,
                        "pendingCount": 0,
                        "taskDefinition": name,
                        "deployments": [
                            {
                                "status": "PRIMARY",
                                "rolloutState": "IN_PROGRESS"
                                if faults["rollout"]
                                else "COMPLETED",
                            }
                        ],
                    }
                    for name in ("api", "worker")
                ]
            }

        def describe_task_definition(self, **kw):
            return {
                "taskDefinition": {
                    "containerDefinitions": [{"image": "unit-ecr@" + c["imageDigest"]}]
                }
            }

        def list_tasks(self, **kw):
            return {"taskArns": [kw["serviceName"]]}

        def describe_tasks(self, **kw):
            return {
                "tasks": [
                    {
                        "taskDefinitionArn": kw["tasks"][0],
                        "lastStatus": "RUNNING",
                        "containers": [
                            {
                                "imageDigest": "sha256:" + "e" * 64
                                if faults["image"]
                                else c["imageDigest"]
                            }
                        ],
                    }
                ]
            }

    class AWS:
        def client(self, name):
            return Client()

    monkeypatch.setattr(store.cloud, "read_config", lambda *a: c)
    monkeypatch.setattr(store.cloud, "session", lambda *a: AWS())
    authority = []

    def trusted_release(args, actual, aws):
        authority.append(args)
        assert (
            args.qa_evidence is not None
            and args.gate_evidence is not None
            and actual == c
        )
        return {"gate_provenance_sha256": "1" * 64}

    monkeypatch.setattr(store.cloud, "require_release", trusted_release)
    monkeypatch.setattr(store.cloud, "stack_outputs", lambda *a: out)
    old_client = httpx.Client

    def handler(request):
        if request.url.path == "/health/ready":
            return httpx.Response(200, json={"state": "ready"})
        return httpx.Response(
            200,
            json={
                "environment": "prod",
                "maintenance": False,
                "inference_available": False,
                "auth": {
                    "issuer": config["oauth_issuer"],
                    "client_id": config["oauth_client_id"],
                    "authorization_endpoint": config["oauth_origin"] + "/oauth2/authorize",
                    "token_endpoint": ("https://foreign.invalid" if faults["endpoint"] else config["oauth_origin"]) + "/oauth2/token",
                    "revocation_endpoint": config["oauth_origin"] + "/oauth2/revoke",
                    "logout_endpoint": config["oauth_origin"] + "/logout",
                    "redirect_uris": [
                        "otgd-prod://oauth/callback"
                        if faults["callback"]
                        else "otgd://oauth/callback",
                        config["oauth_web_callback_uri"],
                    ],
                },
            },
        )

    monkeypatch.setattr(
        store.httpx,
        "Client",
        lambda **kw: old_client(transport=httpx.MockTransport(handler), **kw),
    )
    backend = tmp_path / "signed-backend.json"
    backend.write_text("FICTIONAL SIGNED AUTHORITY BOUNDARY")
    args = argparse.Namespace(
        backend_config=tmp_path / "config.json",
        backend_release=backend,
        trusted_public_key=tmp_path / "public",
        gate_evidence=tmp_path / "gates",
        qa_evidence=tmp_path / "signed-qa",
        aws_profile=None,
    )
    assert (
        store.verify_backend(args, config, REVISION)["gate_provenance_sha256"]
        == "1" * 64
    )
    assert len(authority) == 1
    for fault in faults:
        faults[fault] = True
        with pytest.raises(store.Gate):
            store.verify_backend(args, config, REVISION)
        faults[fault] = False
