"""Offline adversarial store-input tests using fictional cryptographic fixtures.

These tests do not enroll an Expo/store account, call AWS/EAS, qualify a native
build, or establish that an application is available from either app store.
"""

import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

import httpx
from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "services/api"))
from otgd.canonical import canonical

SPEC = importlib.util.spec_from_file_location(
    "store_inputs", ROOT / "apps/mobile/modules/scripts/store_inputs.py"
)
inputs = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = inputs
SPEC.loader.exec_module(inputs)
store = inputs.store_module()
REFUSED = (inputs.Rejected, store.Gate, ValueError, OSError, InvalidSignature, InvalidTag)


REVISION = "a" * 40
PROJECT_ID = "00000000-0000-4000-8000-000000000001"
FICTIONAL_SECRET = "fictional-store-credential-never-used-remotely"


def fictional_config(platform="android", environment="qa"):
    # Syntactically accepted destinations, used only as inert software fixture
    # strings. This suite never contacts them or claims ownership of them.
    return {
        "schema_version": "1.0.0",
        "environment": environment,
        "project_id": PROJECT_ID,
        "expo_account": "fictional-software-test",
        "api_url": "https://api.otgd-fixture.org",
        "oauth_issuer": "https://auth.otgd-fixture.org/pool",
        "oauth_client_id": "A" * 26,
        "artifact_hosts": ["builds.otgd-fixture.org"],
        "bundletool_jar": None,
        "android": {
            "upload_certificate_sha256": "b" * 64,
            "service_account_key_path": None,
        } if platform == "android" else None,
        "ios": {
            "asc_app_id": "1234567890",
            "apple_team_id": "ABCDEFGHIJ",
            "distribution_certificate_sha256": "c" * 64,
            "api_key_path": None,
            "api_key_id": "KLMNOPQRST",
            "api_issuer_id": "00000000-0000-4000-8000-000000000002",
        } if platform == "ios" else None,
    }


def signed_fixture(key, payload):
    raw = canonical(payload)
    envelope = {
        "schema_version": "1.0.0",
        "payload": payload,
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "algorithm": "Ed25519",
        "signature": base64.b64encode(key.sign(raw)).decode("ascii"),
    }
    # Deliberately noncanonical envelope whitespace and ordering. Relocation
    # must preserve these exact bytes because later submission hashes them.
    return (json.dumps(envelope, indent=3, sort_keys=False) + "\n\n").encode()


def archive_fixture(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, contents in entries:
            if isinstance(name, zipfile.ZipInfo):
                archive.writestr(name, contents)
            else:
                archive.writestr(name, contents)
    return output.getvalue()


class StoreInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.google_private = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        ).decode("ascii")

    def setUp(self):
        previous_umask = os.umask(0o077)
        os.umask(previous_umask)
        self.addCleanup(os.umask, previous_umask)
        self.temporary = tempfile.TemporaryDirectory(prefix="otgd-store-input-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.runner = Path(self.temporary.name)
        self.runner.chmod(0o700)
        self.signer = Ed25519PrivateKey.generate()
        self.private = self.signer.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode("ascii")
        self.public = self.signer.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("ascii")
        self.apple_private = ec.generate_private_key(ec.SECP256R1()).private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        ).decode("ascii")
        self.receipt_key = base64.b64encode(bytes(range(32))).decode("ascii")
        self.build_id = "00000000-0000-4000-8000-000000000003"
        self.submission_id = "00000000-0000-4000-8000-000000000004"

    def bundle(self, platform="android", environment="qa"):
        return {
            "schema_version": "1.0.0",
            "store_config": fictional_config(platform, environment),
            "backend_config": {
                "environment": environment,
                "account": "123456789012",
                "region": "us-east-2",
                "releaseId": REVISION,
            },
            "backend_release": {"fixture": "signed backend validation happens in release helper"},
            "gate_evidence": {"fixture": "live gate validation happens in release helper"},
            "trusted_public_key": self.public,
            "release_signing_key": self.private,
            "platform_credentials": {
                "platform": platform,
                "content": {
                    "type": "service_account",
                    "client_email": "fictional@otgd-fixture.iam.gserviceaccount.com",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "private_key": self.google_private,
                } if platform == "android" else self.apple_private,
            },
            "qa_approval": {"fixture": "independent QA validation happens in release helper"},
        }

    def build_receipt(self, platform="android", environment="qa", revision=REVISION, **changes):
        payload = {
            "purpose": "mobile-store-build",
            "platform": platform,
            "environment": environment,
            "source_revision": revision,
            "config_sha256": store.config_digest(fictional_config(platform, environment)),
            "build": {"id": self.build_id},
            "public_release": False,
        }
        payload.update(changes)
        return signed_fixture(self.signer, payload)

    def receipts(self, **changes):
        value = {
            "build_receipt": self.build_receipt(),
            "submission_receipt": None,
            "submission_intent": None,
        }
        value.update(changes)
        return value

    def related_receipt(self, receipt_purpose, build=None, revision=REVISION, platform="android", environment="qa", **changes):
        build = self.build_receipt(platform, environment, revision) if build is None else build
        payload = {
            "purpose": receipt_purpose,
            "source_revision": revision,
            "environment": environment,
            "platform": platform,
            "config_sha256": store.config_digest(fictional_config(platform, environment)),
            "build_receipt_sha256": hashlib.sha256(build).hexdigest(),
            "build_id": self.build_id,
            "submission_id": self.submission_id,
            "public_release": False,
        }
        payload.update(changes)
        return signed_fixture(self.signer, payload)

    def pending_arguments(self, platform="android", environment="qa", revision=REVISION):
        build = self.build_receipt(platform, environment, revision)
        intent = self.related_receipt("mobile-store-submission-intent", build=build,
            revision=revision, platform=platform, environment=environment)
        package = inputs.encrypt_receipts(self.receipts(build_receipt=build, submission_intent=intent),
            self.receipt_key, revision, environment, platform)
        return {"candidate_build_id": self.build_id, "submission_id": self.submission_id,
            "receipt_package": package, "receipt_key": self.receipt_key,
            "role_arn": "arn:aws:iam::123456789012:role/fixture"}

    def pack_sources(self, platform="android", environment="qa", completed=False):
        config = fictional_config(platform, environment)
        config["bundletool_jar"] = str(self.runner / "operator-bundletool.jar")
        field = "service_account_key_path" if platform == "android" else "api_key_path"
        config[platform][field] = str(self.runner / "operator-store-key")
        build = self.build_receipt(platform, environment)
        intent = self.related_receipt("mobile-store-submission-intent", build=build,
            platform=platform, environment=environment)
        content = {"config": inputs.encode(config), "build": build, "intent": intent,
            "public": self.public.encode()}
        if completed:
            content["submission"] = self.related_receipt("mobile-store-submission", build=build,
                platform=platform, environment=environment,
                submission_intent_sha256=hashlib.sha256(intent).hexdigest())
        paths = {}
        for name, raw in content.items():
            path = self.runner / ("operator-" + name + ".input")
            path.write_bytes(raw)
            path.chmod(0o600)
            paths[name] = path
        return paths

    def pack(self, sources, environment="qa", platform="android", revision=REVISION, key=None):
        return inputs.pack(sources["config"], sources["build"], sources["intent"], sources["public"],
            environment, platform, revision, self.runner, self.receipt_key if key is None else key,
            submission_receipt_path=sources.get("submission"))

    def package(self, *, platform="android", environment="qa", revision=REVISION, **changes):
        return inputs.encrypt_receipts(
            self.receipts(build_receipt=self.build_receipt(platform, environment, revision), **changes),
            self.receipt_key, revision, environment, platform,
        )

    def prepare(self, operation="plan", platform="android", environment="qa", bundle=None, **kwargs):
        return inputs.prepare(
            json.dumps(self.bundle(platform, environment) if bundle is None else bundle),
            operation, platform, environment, REVISION, self.runner, **kwargs,
        )

    def owned_scope(self, operation="plan"):
        directory = inputs.new_directory(self.runner)
        inputs.put(directory, "scope.json", inputs.encode({
            **inputs.metadata(REVISION, "qa", "android"), "operation": operation,
        }))
        return directory

    def assert_clean_refusal(self, callback):
        previous = set(self.runner.iterdir())
        with self.assertRaises(REFUSED):
            callback()
        self.assertEqual(set(self.runner.iterdir()), previous, "Rejected inputs left private staging files")

    def test_json_rejects_duplicate_fields_nonfinite_and_unsafe_numbers(self):
        self.assertEqual(inputs.json_object(b'{"ok":[true,null,2.5]}'), {"ok": [True, None, 2.5]})
        for raw in (
            b'{"a":1,"a":2}', b'{"outer":{"a":1,"a":2}}',
            b'{"a":NaN}', b'{"a":Infinity}', b'{"a":-Infinity}',
            b'{"a":1e999}', b'{"a":9007199254740992}',
            b'{"a":-9007199254740992}', b'[]', b'null', b'"string"', b'', b'\xff',
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                inputs.json_object(raw)
        self.assertEqual(inputs.json_object('{"maximum":9007199254740991}')["maximum"], 9007199254740991)

    def test_json_size_depth_and_container_bounds(self):
        self.assertEqual(inputs.json_object(b'{}', limit=2), {})
        for raw, limit in ((b'{} ', 2), (b'{}', 1), (bytearray(b'{}'), 16), (None, 16)):
            with self.subTest(raw=raw), self.assertRaises(inputs.Rejected):
                inputs.json_object(raw, limit)
        for value in (
            {"values": [0] * 513}, {str(i): 0 for i in range(257)},
        ):
            with self.subTest(shape=type(value)), self.assertRaises(inputs.Rejected):
                inputs.json_object(json.dumps(value))
        nested = 1
        for _ in range(26):
            nested = {"next": nested}
        with self.assertRaises(inputs.Rejected):
            inputs.json_object(json.dumps(nested))
        with self.assertRaises(ValueError):
            inputs.encode({"value": float("nan")})

    def test_bundle_is_closed_and_scope_selectors_are_explicit(self):
        original = self.bundle()
        variations = [
            {**original, "unknown": FICTIONAL_SECRET},
            {k: v for k, v in original.items() if k != "qa_approval"},
            {**original, "schema_version": True},
            {**original, "store_config": None},
            {**original, "store_config": {**original["store_config"], "environment": "prod"}},
            {**original, "store_config": {**original["store_config"], "android": None}},
        ]
        for value in variations:
            with self.subTest(change=list(value)):
                self.assert_clean_refusal(lambda: self.prepare(bundle=value))
        for kwargs in (
            {"operation": "publish"}, {"platform": "web"},
            {"environment": "local"}, {"candidate_build_id": self.build_id},
            {"submission_id": self.submission_id}, {"receipt_package": b'{}'},
        ):
            with self.subTest(arguments=kwargs):
                self.assert_clean_refusal(lambda: self.prepare(**kwargs))

    def test_external_paths_and_invalid_store_config_leave_no_staging(self):
        for path_field in ("bundletool_jar", "service_account_key_path"):
            value = self.bundle()
            if path_field == "bundletool_jar":
                value["store_config"][path_field] = "/tmp/operator-file"
            else:
                value["store_config"]["android"][path_field] = "../../operator-file"
            with self.subTest(field=path_field):
                self.assert_clean_refusal(lambda: self.prepare(bundle=value))
        for change in (
            {"api_url": "http://localhost:8000"}, {"extra": "ignored"},
            {"oauth_client_id": "placeholder"}, {"project_id": "not-a-uuid"},
        ):
            value = self.bundle()
            value["store_config"].update(change)
            with self.subTest(change=change):
                self.assert_clean_refusal(lambda: self.prepare(bundle=value))
        value = self.bundle("ios")
        value["store_config"]["ios"]["api_key_path"] = "/tmp/operator-key.p8"
        self.assert_clean_refusal(lambda: self.prepare(platform="ios", bundle=value))

    def test_plan_stages_no_private_credentials_and_keeps_outputs_private(self):
        result = self.prepare()
        directory = Path(result["directory"])
        self.assertEqual(result["account"], "")
        self.assertEqual(result["region"], "")
        self.assertEqual(result["role_arn"], "")
        self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)
        self.assertEqual({path.name for path in directory.iterdir()}, {"scope.json", "config.json", "arguments.json"})
        for path in directory.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertNotIn(self.private.encode(), path.read_bytes())
            self.assertNotIn(FICTIONAL_SECRET.encode(), path.read_bytes())
        config = store.read_config(directory / "config.json")
        self.assertEqual(config["android"]["service_account_key_path"], str(directory / "google-service-account.json"))
        self.assertEqual(config["bundletool_jar"], str(directory / "bundletool.jar"))
        inputs.cleanup(directory, self.runner)
        self.assertFalse(directory.exists())

    def test_private_reads_refuse_links_special_files_owner_permissions_and_limits(self):
        private = self.runner / "private.json"
        private.write_bytes(b'{"secret":"fictional"}')
        private.chmod(0o600)
        self.assertEqual(inputs.private_read(private), private.read_bytes())
        symbolic = self.runner / "symlink.json"
        symbolic.symlink_to(private)
        with self.assertRaises(REFUSED):
            inputs.private_read(symbolic)
        hard = self.runner / "hardlink.json"
        os.link(private, hard)
        with self.assertRaises(inputs.Rejected):
            inputs.private_read(private)
        hard.unlink()
        private.chmod(0o644)
        with self.assertRaises(inputs.Rejected):
            inputs.private_read(private)
        private.chmod(0o600)
        with patch.object(inputs.os, "getuid", return_value=os.getuid() + 1), self.assertRaises(inputs.Rejected):
            inputs.private_read(private)
        with patch.object(inputs.os, "read") as read, self.assertRaises(inputs.Rejected):
            inputs.private_read(private, 1)
        read.assert_not_called()
        fifo = self.runner / "fifo.json"
        os.mkfifo(fifo, 0o600)
        with self.assertRaises(inputs.Rejected):
            inputs.private_read(fifo)
        with self.assertRaises(inputs.Rejected):
            inputs.private_read(self.runner)
        private.write_bytes(b'')
        with self.assertRaises(inputs.Rejected):
            inputs.private_read(private)

    def test_private_input_changes_during_read_are_refused(self):
        path = self.runner / "private.json"
        path.write_bytes(b'{"private":"fixture"}')
        path.chmod(0o600)
        read = os.read
        def change_mode(descriptor, size):
            raw = read(descriptor, size)
            path.chmod(0o644)
            return raw
        with patch.object(inputs.os, "read", side_effect=change_mode), self.assertRaises(inputs.Rejected):
            inputs.private_read(path)

    def test_runner_and_scope_refuse_noncanonical_symlink_and_shared_directories(self):
        link = self.runner / "runner-link"
        link.symlink_to(self.runner, target_is_directory=True)
        for path in (link, Path("relative"), self.runner / ".." / self.runner.name):
            with self.subTest(path=path), self.assertRaises(REFUSED):
                inputs.new_directory(path)
        self.runner.chmod(0o777)
        with self.assertRaises(inputs.Rejected):
            inputs.new_directory(self.runner)
        self.runner.chmod(0o700)
        directory = self.owned_scope()
        self.assertEqual(inputs.scope(directory, self.runner)["operation"], "plan")
        directory.chmod(0o750)
        with self.assertRaises(inputs.Rejected):
            inputs.scope(directory, self.runner)
        directory.chmod(0o700)
        with self.assertRaises(inputs.Rejected):
            inputs.scope(self.runner, self.runner)
        inputs.cleanup(directory, self.runner)

    def test_fixed_paths_never_traverse_or_overwrite_existing_operator_files(self):
        directory = self.owned_scope()
        outside = self.runner / "operator-file"
        outside.write_bytes(b'operator-owned')
        for name in ("../operator-file", "/tmp/operator-file", "private.pem", "nested/config.json"):
            with self.subTest(name=name), self.assertRaises(inputs.Rejected):
                inputs.put(directory, name, b'fictional')
        inputs.put(directory, "config.json", b'{"fictional":true}')
        with self.assertRaises(REFUSED):
            inputs.put(directory, "config.json", b'overwrite')
        (directory / "trusted-public.pem").symlink_to(outside)
        with self.assertRaises(REFUSED):
            inputs.put(directory, "trusted-public.pem", b'overwrite')
        self.assertEqual(outside.read_bytes(), b'operator-owned')
        with self.assertRaises(inputs.Rejected):
            inputs.put(directory, "backend-config.json", b'')
        with self.assertRaises(inputs.Rejected):
            inputs.put(directory, "backend-config.json", "string")
        (directory / "trusted-public.pem").unlink()
        inputs.cleanup(directory, self.runner)

    def test_cleanup_refuses_foreign_entries_and_links_before_any_deletion(self):
        for variant in ("unknown", "symlink", "hardlink"):
            directory = self.owned_scope()
            original = (directory / "scope.json").read_bytes()
            outside = self.runner / (variant + "-operator.json")
            outside.write_bytes(b'operator-owned')
            outside.chmod(0o600)
            name = "unknown.json" if variant == "unknown" else "config.json"
            path = directory / name
            if variant == "symlink":
                path.symlink_to(outside)
            elif variant == "hardlink":
                os.link(outside, path)
            else:
                path.write_bytes(b'unknown')
                path.chmod(0o600)
            with self.subTest(variant=variant), self.assertRaises(inputs.Rejected):
                inputs.cleanup(directory, self.runner)
            self.assertEqual((directory / "scope.json").read_bytes(), original)
            self.assertEqual(outside.read_bytes(), b'operator-owned')
            path.unlink()
            inputs.cleanup(directory, self.runner)

    def test_failed_initial_scope_write_removes_only_new_owned_directory(self):
        original = inputs.put
        def failed_scope(directory, name, raw):
            if name == "scope.json":
                raise OSError("fictional initial write failure")
            return original(directory, name, raw)
        with patch.object(inputs, "put", side_effect=failed_scope):
            self.assert_clean_refusal(lambda: self.prepare())

    def test_directory_replacement_and_foreign_scope_metadata_are_refused(self):
        directory = self.owned_scope()
        linked = self.runner / "linked-staging"
        linked.symlink_to(directory, target_is_directory=True)
        with self.assertRaises(inputs.Rejected):
            inputs.put(linked, "config.json", b'{}')
        directory.chmod(0o755)
        with self.assertRaises(inputs.Rejected):
            inputs.put(directory, "config.json", b'{}')
        directory.chmod(0o700)
        original = inputs.json_object(inputs.private_read(directory / "scope.json"))
        for changes in ({"repository": "attacker/repository"}, {"operation": "publish"}, {"extra": "field"}):
            (directory / "scope.json").write_bytes(inputs.encode({**original, **changes}))
            with self.subTest(changes=changes), self.assertRaises(inputs.Rejected):
                inputs.scope(directory, self.runner)
        (directory / "scope.json").write_bytes(inputs.encode(original))
        inputs.cleanup(directory, self.runner)

    def test_build_stages_selected_signer_and_backend_scope_without_store_credentials(self):
        result = self.prepare("build", role_arn="arn:aws:iam::123456789012:role/fictional-release", receipt_key=self.receipt_key)
        directory = Path(result["directory"])
        self.assertEqual(result["account"], "123456789012")
        self.assertEqual(result["region"], "us-east-2")
        self.assertFalse((directory / "google-service-account.json").exists())
        self.assertFalse((directory / "apple-api-key.p8").exists())
        store.cloud.require_trusted_signer(directory / "release-private.pem", directory / "trusted-public.pem")
        self.assertEqual(inputs.private_read(directory / "release-private.pem"), self.private.encode())
        arguments = inputs.json_object(inputs.private_read(directory / "arguments.json"))["arguments"]
        self.assertIn("--backend-release", arguments)
        self.assertIn("--gate-evidence", arguments)
        self.assertIn("--signing-key", arguments)
        self.assertNotIn(self.private, arguments)
        inputs.cleanup(directory, self.runner)

    def test_build_refuses_wrong_aws_scope_and_mismatched_signing_authority(self):
        changes = [
            {"environment": "prod"}, {"releaseId": "b" * 40}, {"account": "123"},
            {"region": "localstack"},
        ]
        for change in changes:
            value = self.bundle()
            value["backend_config"].update(change)
            with self.subTest(change=change):
                self.assert_clean_refusal(lambda: self.prepare("build", bundle=value,
                    role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key))
        for role in ("", "arn:aws:iam::999999999999:role/fixture", "arn:aws-cn:iam::123456789012:role/fixture", "arn:aws:iam::123456789012:user/fixture"):
            with self.subTest(role=role):
                self.assert_clean_refusal(lambda: self.prepare("build", role_arn=role, receipt_key=self.receipt_key))
        value = self.bundle()
        other = Ed25519PrivateKey.generate()
        value["trusted_public_key"] = other.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.assert_clean_refusal(lambda: self.prepare("build", bundle=value,
            role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key))
        for field in ("backend_config", "backend_release", "gate_evidence", "release_signing_key", "trusted_public_key"):
            value = self.bundle()
            value[field] = None
            with self.subTest(field=field):
                self.assert_clean_refusal(lambda: self.prepare("build", bundle=value,
                    role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key))

    def test_prod_requires_qa_approval_and_matching_partition(self):
        value = self.bundle(environment="prod")
        value["qa_approval"] = None
        self.assert_clean_refusal(lambda: self.prepare("build", environment="prod", bundle=value,
            role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key))
        value = self.bundle(environment="prod")
        result = self.prepare("build", environment="prod", bundle=value,
            role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key)
        directory = Path(result["directory"])
        self.assertEqual(inputs.json_object(inputs.private_read(directory / "qa-approval.json")), value["qa_approval"])
        inputs.cleanup(directory, self.runner)
        for region, partition in (("cn-north-1", "aws-cn"), ("us-gov-west-1", "aws-us-gov")):
            value = self.bundle()
            value["backend_config"]["region"] = region
            result = self.prepare("build", bundle=value,
                role_arn=f"arn:{partition}:iam::123456789012:role/fixture", receipt_key=self.receipt_key)
            self.assertEqual(result["region"], region)
            inputs.cleanup(Path(result["directory"]), self.runner)

    def test_aead_roundtrip_preserves_exact_signed_receipt_and_intent_bytes(self):
        intent = signed_fixture(self.signer, {"purpose": "mobile-store-submission-intent", "fixture": "original bytes"})
        submission = signed_fixture(self.signer, {"purpose": "mobile-store-submission", "fixture": "original bytes"})
        original = self.receipts(submission_receipt=submission, submission_intent=intent)
        blob = inputs.encrypt_receipts(original, self.receipt_key, REVISION, "qa", "android")
        header, recovered = inputs.decrypt_receipts(blob, self.receipt_key, "qa", "android")
        self.assertEqual(header, inputs.metadata(REVISION, "qa", "android"))
        self.assertEqual(recovered, original)
        self.assertNotIn(b'mobile-store-build', blob)
        self.assertNotIn(self.private.encode(), blob)
        directory = self.owned_scope()
        inputs.put(directory, "trusted-public.pem", self.public.encode())
        inputs.put(directory, "build-receipt.json", recovered["build_receipt"])
        self.assertEqual(store.verify_signed_record(directory / "build-receipt.json", directory / "trusted-public.pem")["build"]["id"], self.build_id)
        inputs.cleanup(directory, self.runner)

    def test_aead_refuses_wrong_key_scope_metadata_nonce_and_ciphertext(self):
        blob = self.package()
        wrong_key = base64.b64encode(b'z' * 32).decode()
        for key, environment, platform in ((wrong_key, "qa", "android"), (self.receipt_key, "prod", "android"), (self.receipt_key, "qa", "ios")):
            with self.subTest(scope=(environment, platform)), self.assertRaises(REFUSED):
                inputs.decrypt_receipts(blob, key, environment, platform)
        envelope = inputs.json_object(blob)
        mutations = [
            {"repository": "attacker/repository"}, {"schema_version": "2.0.0"},
            {"source_revision": "b" * 40}, {"unknown": "field"},
            {"nonce": base64.b64encode(b'1' * 11).decode()},
            {"nonce": "invalid-base64"}, {"ciphertext": base64.b64encode(b'1' * 16).decode()},
        ]
        cipher = bytearray(base64.b64decode(envelope["ciphertext"]))
        cipher[-1] ^= 1
        mutations.append({"ciphertext": base64.b64encode(cipher).decode()})
        for change in mutations:
            with self.subTest(change=list(change)), self.assertRaises(REFUSED):
                inputs.decrypt_receipts(inputs.encode({**envelope, **change}), self.receipt_key, "qa", "android")

    def test_aead_requires_bounded_exact_inventory_and_canonical_external_key(self):
        for key in (None, "", "not-base64", base64.b64encode(b'x' * 31).decode(), self.receipt_key + "\n"):
            with self.subTest(key_type=type(key).__name__), self.assertRaises(ValueError):
                inputs.key_bytes(key)
        for value in (
            {"build_receipt": self.build_receipt()},
            self.receipts(build_receipt=None), self.receipts(build_receipt=b'[]'),
            self.receipts(build_receipt=b'{"a":NaN}'),
            self.receipts(build_receipt=b'{"x":"' + b'x' * inputs.MAX_RECORD + b'"}'),
        ):
            with self.subTest(fields=list(value)), self.assertRaises(ValueError):
                inputs.encrypt_receipts(value, self.receipt_key, REVISION, "qa", "android")
        with patch.object(inputs, "MAX_ENVELOPE", 1), self.assertRaises(inputs.Rejected):
            self.package()
        for revision, environment, platform in (("main", "qa", "android"), (REVISION, "local", "android"), (REVISION, "qa", "web")):
            with self.subTest(scope=(revision, environment, platform)), self.assertRaises(inputs.Rejected):
                inputs.metadata(revision, environment, platform)

    def test_authenticated_plaintext_still_requires_exact_receipt_inventory(self):
        header = inputs.metadata(REVISION, "qa", "android")
        nonce = b'1' * 12
        plaintexts = [
            {"build_receipt": None, "submission_receipt": None, "submission_intent": None},
            {"build_receipt": base64.b64encode(self.build_receipt()).decode()},
            {"build_receipt": "!", "submission_receipt": None, "submission_intent": None},
            {"build_receipt": base64.b64encode(b'[]').decode(), "submission_receipt": None, "submission_intent": None},
        ]
        for body in plaintexts:
            ciphertext = AESGCM(bytes(range(32))).encrypt(nonce, inputs.encode(body), inputs.encode(header))
            blob = inputs.encode({**header, "nonce": base64.b64encode(nonce).decode(), "ciphertext": base64.b64encode(ciphertext).decode()})
            with self.subTest(body=list(body)), self.assertRaises(ValueError):
                inputs.decrypt_receipts(blob, self.receipt_key, "qa", "android")

    def test_status_preserves_original_receipts_without_staging_private_credentials(self):
        original = self.build_receipt(revision="b" * 40)
        submission = self.related_receipt("mobile-store-submission", build=original, revision="b" * 40)
        package = inputs.encrypt_receipts(self.receipts(build_receipt=original, submission_receipt=submission), self.receipt_key, "b" * 40, "qa", "android")
        result = self.prepare("status", candidate_build_id=self.build_id, receipt_package=package, receipt_key=self.receipt_key)
        directory = Path(result["directory"])
        self.assertEqual(inputs.private_read(directory / "build-receipt.json"), original)
        self.assertEqual(inputs.private_read(directory / "submission-receipt.json"), submission)
        self.assertEqual({path.name for path in directory.iterdir()}, {
            "scope.json", "config.json", "arguments.json", "trusted-public.pem", "build-receipt.json", "submission-receipt.json",
        })
        self.assertEqual(result["account"], "")
        self.assertFalse((directory / "release-private.pem").exists())
        self.assertFalse((directory / "google-service-account.json").exists())
        with self.assertRaises(inputs.Rejected):
            inputs.seal(directory, self.runner, self.receipt_key)
        inputs.cleanup(directory, self.runner)

    def test_signed_child_receipts_bind_original_build_bytes_and_logical_configuration(self):
        for purpose, field, operation in (
            ("mobile-store-submission", "submission_receipt", "status"),
            ("mobile-store-submission-intent", "submission_intent", "submit"),
        ):
            mutations = [
                {"purpose": "web-release"}, {"platform": "ios"},
                {"source_revision": "b" * 40}, {"config_sha256": "d" * 64},
                {"build_receipt_sha256": hashlib.sha256(self.build_receipt().rstrip()).hexdigest()},
            ]
            if operation == "submit":
                mutations.append({"build_id": self.submission_id})
            for changes in mutations:
                package = self.package(**{field: self.related_receipt(purpose, **changes)})
                arguments = {"candidate_build_id": self.build_id, "receipt_package": package,
                    "receipt_key": self.receipt_key, "submission_id": self.submission_id}
                if operation == "submit":
                    arguments["role_arn"] = "arn:aws:iam::123456789012:role/fixture"
                with self.subTest(purpose=purpose, changes=changes):
                    self.assert_clean_refusal(lambda: self.prepare(operation, **arguments))

    def test_candidate_receipt_scope_signer_and_submission_reuse_are_checked(self):
        for changes in (
            {"purpose": "web-release"}, {"platform": "ios"},
            {"environment": "prod"}, {"source_revision": "b" * 40},
            {"build": {"id": self.submission_id}},
        ):
            package = inputs.encrypt_receipts(self.receipts(build_receipt=self.build_receipt(**changes)), self.receipt_key, REVISION, "qa", "android")
            with self.subTest(changes=changes):
                self.assert_clean_refusal(lambda: self.prepare("status", candidate_build_id=self.build_id,
                    receipt_package=package, receipt_key=self.receipt_key))
        for candidate in ("", "not-a-uuid", self.submission_id):
            with self.subTest(candidate=candidate):
                self.assert_clean_refusal(lambda: self.prepare("status", candidate_build_id=candidate,
                    receipt_package=self.package(), receipt_key=self.receipt_key))
        value = self.bundle()
        value["trusted_public_key"] = Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.assert_clean_refusal(lambda: self.prepare("status", bundle=value, candidate_build_id=self.build_id,
            receipt_package=self.package(), receipt_key=self.receipt_key))
        completed = self.package(submission_receipt=signed_fixture(self.signer, {"purpose": "mobile-store-submission"}))
        self.assert_clean_refusal(lambda: self.prepare("submit", candidate_build_id=self.build_id,
            receipt_package=completed, receipt_key=self.receipt_key, role_arn="arn:aws:iam::123456789012:role/fixture"))
        old = self.package(revision="b" * 40)
        self.assert_clean_refusal(lambda: self.prepare("submit", candidate_build_id=self.build_id,
            receipt_package=old, receipt_key=self.receipt_key, role_arn="arn:aws:iam::123456789012:role/fixture"))

    def test_submit_stages_only_selected_platform_credential(self):
        for platform in ("android", "ios"):
            result = self.prepare("submit", platform=platform, **self.pending_arguments(platform))
            directory = Path(result["directory"])
            selected = "google-service-account.json" if platform == "android" else "apple-api-key.p8"
            other = "apple-api-key.p8" if platform == "android" else "google-service-account.json"
            self.assertTrue((directory / selected).is_file())
            self.assertFalse((directory / other).exists())
            self.assertEqual(stat.S_IMODE((directory / selected).stat().st_mode), 0o600)
            if platform == "ios":
                self.assertEqual(inputs.private_read(directory / selected), self.apple_private.encode())
            else:
                self.assertEqual(inputs.json_object(inputs.private_read(directory / selected))["private_key"], self.google_private)
            inputs.cleanup(directory, self.runner)

    def test_submit_reconciliation_requires_original_intent_and_exact_identifier(self):
        intent = self.related_receipt("mobile-store-submission-intent")
        package = self.package(submission_intent=intent)
        defaults = {"candidate_build_id": self.build_id, "receipt_package": package,
            "receipt_key": self.receipt_key, "role_arn": "arn:aws:iam::123456789012:role/fixture"}
        self.assert_clean_refusal(lambda: self.prepare("submit", **defaults))
        self.assert_clean_refusal(lambda: self.prepare("submit", submission_id="malformed", **defaults))
        result = self.prepare("submit", submission_id=self.submission_id, **defaults)
        directory = Path(result["directory"])
        self.assertEqual(inputs.private_read(directory / "output-receipt.json.intent.json"), intent)
        arguments = inputs.json_object(inputs.private_read(directory / "arguments.json"))["arguments"]
        self.assertEqual(arguments[arguments.index("--submission-id") + 1], self.submission_id)
        inputs.cleanup(directory, self.runner)
        self.assert_clean_refusal(lambda: self.prepare("submit", candidate_build_id=self.build_id,
            submission_id=self.submission_id, receipt_package=self.package(), receipt_key=self.receipt_key,
            role_arn="arn:aws:iam::123456789012:role/fixture"))

    def test_browser_submit_cannot_stage_or_authorize_a_fresh_submission(self):
        pending = self.pending_arguments()
        variations = [
            {**pending, "submission_id": ""},
            {**pending, "receipt_package": self.package()},
            {**pending, "submission_id": "", "receipt_package": self.package()},
        ]
        for arguments in variations:
            with self.subTest(has_identifier=bool(arguments["submission_id"])), patch.object(inputs, "new_directory") as created, patch.object(inputs.subprocess, "run") as command, patch.object(httpx, "Client") as network:
                self.assert_clean_refusal(lambda: self.prepare("submit", **arguments))
            created.assert_not_called()
            command.assert_not_called()
            network.assert_not_called()

    def test_reconciliation_signature_authority_is_verified_before_staging(self):
        raw = self.related_receipt("mobile-store-submission-intent")
        altered = json.loads(raw)
        altered["payload"]["build_receipt_sha256"] = "d" * 64
        wrong_signer = Ed25519PrivateKey.generate()
        p256_public = ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        for public, intent in (
            (self.public, inputs.encode(altered)),
            (self.public, signed_fixture(wrong_signer, json.loads(raw)["payload"])),
            (p256_public, raw),
        ):
            value = self.bundle()
            value["trusted_public_key"] = public
            arguments = self.pending_arguments()
            arguments["receipt_package"] = self.package(submission_intent=intent)
            with self.subTest(public_kind="Ed25519" if public == self.public else "P256"), patch.object(inputs, "new_directory") as created:
                self.assert_clean_refusal(lambda: self.prepare("submit", bundle=value, **arguments))
            created.assert_not_called()
        for changes in ({"build_receipt_sha256": "d" * 64}, {"build_id": self.submission_id},
            {"config_sha256": "e" * 64}, {"source_revision": "b" * 40}):
            arguments = self.pending_arguments()
            invalid = self.related_receipt("mobile-store-submission-intent", **changes)
            arguments["receipt_package"] = self.package(submission_intent=invalid)
            with self.subTest(changes=changes), patch.object(inputs, "new_directory") as created:
                self.assert_clean_refusal(lambda: self.prepare("submit", **arguments))
            created.assert_not_called()

    def test_platform_credentials_reject_wrong_scope_unknown_wrappers_and_bad_content(self):
        for credential in (
            None, {"platform": "ios", "content": self.private},
            {"platform": "android", "content": {}, "path": "/tmp/operator"},
            {"platform": "android", "content": {"type": "service_account", "client_email": "fixture@elsewhere.org", "token_uri": "https://oauth2.googleapis.com/token", "private_key": self.private}},
            {"platform": "android", "content": {"type": "service_account", "client_email": "fixture@project.iam.gserviceaccount.com", "token_uri": "https://attacker.org/token", "private_key": self.private}},
        ):
            value = self.bundle()
            value["platform_credentials"] = credential
            with self.subTest(credential_type=type(credential).__name__):
                self.assert_clean_refusal(lambda: self.prepare("submit", bundle=value, **self.pending_arguments()))
        value = self.bundle("ios")
        value["platform_credentials"]["content"] = "not a PEM key"
        self.assert_clean_refusal(lambda: self.prepare("submit", platform="ios", bundle=value,
            **self.pending_arguments("ios")))

    def test_public_artifact_allows_one_bounded_ciphertext_entry_only(self):
        blob = self.package()
        good = archive_fixture([(inputs.ENCRYPTED_NAME, blob)])
        self.assertEqual(inputs.artifact_payload(good), blob)
        for entries in (
            [], [("../" + inputs.ENCRYPTED_NAME, blob)], [("/" + inputs.ENCRYPTED_NAME, blob)],
            [(inputs.ENCRYPTED_NAME + "/", blob)], [("build-receipt.json", self.build_receipt())],
            [(inputs.ENCRYPTED_NAME, blob), ("release-private.pem", self.private)],
            [(inputs.ENCRYPTED_NAME, b'')], [(inputs.ENCRYPTED_NAME, b'x' * (inputs.MAX_ENVELOPE + 1))],
        ):
            with self.subTest(names=[str(name) for name, _ in entries]), self.assertRaises(REFUSED):
                inputs.artifact_payload(archive_fixture(entries))
        symbolic = zipfile.ZipInfo(inputs.ENCRYPTED_NAME)
        symbolic.create_system = 3
        symbolic.external_attr = (stat.S_IFLNK | 0o600) << 16
        with self.assertRaises(inputs.Rejected):
            inputs.artifact_payload(archive_fixture([(symbolic, b'outside')]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            duplicate = archive_fixture([(inputs.ENCRYPTED_NAME, blob), (inputs.ENCRYPTED_NAME, blob)])
        with self.assertRaises(inputs.Rejected):
            inputs.artifact_payload(duplicate)
        for raw in ("not bytes", b'x' * (inputs.MAX_DOWNLOAD + 1), b'not a zip'):
            with self.subTest(type=type(raw)), self.assertRaises((inputs.Rejected, zipfile.BadZipFile)):
                inputs.artifact_payload(raw)

    def artifact_client(self, *, metadata_change=None, location=None, package=None, metadata_status=200, archive_status=200):
        package = self.package() if package is None else package
        archive = archive_fixture([(inputs.ENCRYPTED_NAME, package)])
        requests = []
        value = {"id": 23, "expired": False, "size_in_bytes": len(archive),
            "workflow_run": {"head_sha": REVISION, "head_branch": "main", "id": 47},
            "name": f"store-receipts-qa-android-{REVISION}-47"}
        if metadata_change:
            value.update(metadata_change)
        location = location or "https://fictional.blob.core.windows.net/receipt.zip?signature=fictional"
        def response(request):
            requests.append(request)
            if request.url.host == "api.github.com":
                if request.url.path.endswith("/zip"):
                    return httpx.Response(302, headers={"location": location})
                return httpx.Response(metadata_status, json=value)
            return httpx.Response(archive_status, content=archive)
        return httpx.Client(transport=httpx.MockTransport(response), follow_redirects=False), requests

    def test_artifact_download_auth_is_sent_only_to_github_and_bytes_are_bounded(self):
        # MockTransport exercises the actual HTTP header/redirect code offline;
        # this is not a live GitHub artifact or a dependency qualification.
        client, requests = self.artifact_client()
        with client:
            blob = inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android", client=client)
        self.assertEqual(inputs.decrypt_receipts(blob, self.receipt_key, "qa", "android")[1]["build_receipt"], self.build_receipt())
        self.assertEqual(len(requests), 3)
        for request in requests[:2]:
            self.assertEqual(request.headers["authorization"], "Bearer " + FICTIONAL_SECRET)
        self.assertNotIn("authorization", requests[-1].headers)
        self.assertNotIn(FICTIONAL_SECRET, str(requests[-1].url))
        client, _ = self.artifact_client()
        with client, patch.object(inputs, "MAX_DOWNLOAD", 1), self.assertRaises(inputs.Rejected):
            inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android", client=client)

    def test_artifact_metadata_and_redirect_targets_cannot_change_scope_or_leak_token(self):
        for change in (
            {"id": True}, {"id": 24}, {"expired": True}, {"size_in_bytes": True},
            {"size_in_bytes": inputs.MAX_DOWNLOAD + 1}, {"name": "another-artifact"},
            {"workflow_run": {"head_sha": REVISION, "head_branch": "branch", "id": 47}},
            {"workflow_run": {"head_sha": "main", "head_branch": "main", "id": 47}},
        ):
            client, requests = self.artifact_client(metadata_change=change)
            with self.subTest(change=change), client, self.assertRaises(inputs.Rejected):
                inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android", client=client)
            self.assertEqual(len(requests), 1)
        for location in (
            "http://fictional.blob.core.windows.net/archive", "https://attacker.org/archive",
            "https://user:password@fictional.blob.core.windows.net/archive",
            "https://fictional.blob.core.windows.net:444/archive", "https://fictional.blob.core.windows.net/archive#fragment",
            "https://blob.core.windows.net.attacker.org/archive",
        ):
            client, requests = self.artifact_client(location=location)
            with self.subTest(location=location), client, self.assertRaises(inputs.Rejected):
                inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android", client=client)
            self.assertEqual(len(requests), 2)
        for artifact_id, token in (("0", FICTIONAL_SECRET), ("../23", FICTIONAL_SECRET), ("23", ""), ("23", "token\n")):
            client, requests = self.artifact_client()
            with self.subTest(artifact_id=artifact_id), client, self.assertRaises(inputs.Rejected):
                inputs.download_receipts(artifact_id, token, "qa", "android", client=client)
            self.assertEqual(requests, [])

    def test_artifact_errors_and_foreign_ciphertext_revision_are_refused(self):
        for arguments in ({"metadata_status": 403}, {"archive_status": 404}, {"package": self.package(revision="b" * 40)}):
            client, _ = self.artifact_client(**arguments)
            with self.subTest(arguments=list(arguments)), client, self.assertRaises(inputs.Rejected):
                inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android", client=client)

    def test_streamed_metadata_and_assets_are_bounded_before_accumulation(self):
        with self.assertRaises(inputs.Rejected):
            inputs.response_bytes(httpx.Response(200, content=b'x' * 11), 10)
        self.assertEqual(inputs.response_bytes(httpx.Response(200, content=b'1234567890'), 10), b'1234567890')
        client, _ = self.artifact_client()
        with client, patch.object(inputs, "MAX_RECORD", 1), self.assertRaises(inputs.Rejected):
            inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android", client=client)
        def direct_archive(request):
            if request.url.path.endswith("/zip"):
                return httpx.Response(200, content=b'direct archive refused')
            return httpx.Response(200, json={"id": 23, "expired": False, "size_in_bytes": 1,
                "workflow_run": {"head_sha": REVISION, "head_branch": "main", "id": 47},
                "name": f"store-receipts-qa-android-{REVISION}-47"})
        with httpx.Client(transport=httpx.MockTransport(direct_archive)) as client, self.assertRaises(inputs.Rejected):
            inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android", client=client)
        client, _ = self.artifact_client()
        with patch.object(httpx, "Client", return_value=client):
            blob = inputs.download_receipts("23", FICTIONAL_SECRET, "qa", "android")
            self.assertEqual(inputs.decrypt_receipts(blob, self.receipt_key, "qa", "android")[1]["build_receipt"], self.build_receipt())
        self.assertTrue(client.is_closed)

    def test_seal_verifies_original_signed_output_and_keeps_bytes(self):
        result = self.prepare("build", role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key)
        directory = Path(result["directory"])
        self.assertIsNone(inputs.seal(directory, self.runner, self.receipt_key))
        raw = self.build_receipt()
        inputs.put(directory, "output-receipt.json", raw)
        sealed = inputs.seal(directory, self.runner, self.receipt_key)
        self.assertEqual(sealed.name, inputs.ENCRYPTED_NAME)
        recovered = inputs.decrypt_receipts(inputs.private_read(sealed, inputs.MAX_ENVELOPE), self.receipt_key, "qa", "android")[1]
        self.assertEqual(recovered["build_receipt"], raw)
        self.assertIsNone(recovered["submission_receipt"])
        self.assertEqual(stat.S_IMODE(sealed.stat().st_mode), 0o600)
        with self.assertRaises(REFUSED):
            inputs.seal(directory, self.runner, self.receipt_key)
        inputs.cleanup(directory, self.runner)

    def test_seal_refuses_tampered_wrong_scope_or_public_release_outputs(self):
        for changes in ({"purpose": "web-release"}, {"source_revision": "b" * 40}, {"platform": "ios"},
            {"public_release": True}, {"environment": "prod"}, {"config_sha256": "d" * 64}):
            result = self.prepare("build", role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key)
            directory = Path(result["directory"])
            inputs.put(directory, "output-receipt.json", self.build_receipt(**changes))
            with self.subTest(changes=changes), self.assertRaises(REFUSED):
                inputs.seal(directory, self.runner, self.receipt_key)
            self.assertFalse((directory / inputs.ENCRYPTED_NAME).exists())
            inputs.cleanup(directory, self.runner)
        result = self.prepare("build", role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key)
        directory = Path(result["directory"])
        envelope = json.loads(self.build_receipt())
        envelope["payload"]["build"]["id"] = self.submission_id
        inputs.put(directory, "output-receipt.json", inputs.encode(envelope))
        with self.assertRaises(REFUSED):
            inputs.seal(directory, self.runner, self.receipt_key)
        inputs.cleanup(directory, self.runner)

    def test_seal_preserves_pending_submission_intent_and_completed_submission(self):
        for completed in (False, True):
            original = self.build_receipt()
            result = self.prepare("submit", **self.pending_arguments())
            directory = Path(result["directory"])
            intent = inputs.private_read(directory / "output-receipt.json.intent.json")
            if completed:
                raw = self.related_receipt("mobile-store-submission", build=original,
                    submission_intent_sha256=hashlib.sha256(intent).hexdigest())
                inputs.put(directory, "output-receipt.json", raw)
            sealed = inputs.seal(directory, self.runner, self.receipt_key)
            recovered = inputs.decrypt_receipts(inputs.private_read(sealed, inputs.MAX_ENVELOPE), self.receipt_key, "qa", "android")[1]
            self.assertEqual(recovered["build_receipt"], original)
            self.assertEqual(recovered["submission_intent"], intent)
            if completed:
                self.assertEqual(recovered["submission_receipt"], raw)
            else:
                self.assertIsNone(recovered["submission_receipt"])
            inputs.cleanup(directory, self.runner)

    def test_seal_refuses_signed_child_output_for_foreign_build_or_intent(self):
        for changes in (
            {"build_receipt_sha256": "d" * 64}, {"build_id": self.submission_id},
            {"submission_intent_sha256": "e" * 64},
        ):
            result = self.prepare("submit", **self.pending_arguments())
            directory = Path(result["directory"])
            intent = inputs.private_read(directory / "output-receipt.json.intent.json")
            output = self.related_receipt("mobile-store-submission",
                **{"submission_intent_sha256": hashlib.sha256(intent).hexdigest(), **changes})
            inputs.put(directory, "output-receipt.json", output)
            with self.subTest(changes=changes), self.assertRaises(inputs.Rejected):
                inputs.seal(directory, self.runner, self.receipt_key)
            self.assertFalse((directory / inputs.ENCRYPTED_NAME).exists())
            inputs.cleanup(directory, self.runner)
        for operation, changes in (("build", {}), ("submit", {"build_receipt_sha256": "f" * 64})):
            arguments = {"receipt_key": self.receipt_key, "role_arn": "arn:aws:iam::123456789012:role/fixture"}
            if operation == "submit":
                arguments = self.pending_arguments()
            result = self.prepare(operation, **arguments)
            directory = Path(result["directory"])
            raw = self.related_receipt("mobile-store-submission-intent", **changes)
            if operation == "submit":
                (directory / "output-receipt.json.intent.json").write_bytes(raw)
            else:
                inputs.put(directory, "output-receipt.json.intent.json", raw)
            with self.subTest(operation=operation), self.assertRaises(inputs.Rejected):
                inputs.seal(directory, self.runner, self.receipt_key)
            inputs.cleanup(directory, self.runner)

    def test_run_invokes_selected_helper_without_shell_or_secret_arguments(self):
        result = self.prepare()
        directory = Path(result["directory"])
        expected = inputs.json_object(inputs.private_read(directory / "arguments.json"))["arguments"]
        with patch.object(inputs.subprocess, "run") as command:
            inputs.run(directory, self.runner)
        command.assert_called_once_with([sys.executable, str(ROOT / "apps/mobile/modules/scripts/store_release.py"), *expected], check=True)
        args = inputs.json_object(inputs.private_read(directory / "arguments.json"))
        args["arguments"][0] = "submit"
        (directory / "arguments.json").write_bytes(inputs.encode(args))
        with patch.object(inputs.subprocess, "run") as command, self.assertRaises(inputs.Rejected):
            inputs.run(directory, self.runner)
        command.assert_not_called()
        inputs.cleanup(directory, self.runner)

    def test_run_rejects_duplicate_unknown_foreign_and_unscoped_arguments(self):
        result = self.prepare()
        directory = Path(result["directory"])
        original = inputs.json_object(inputs.private_read(directory / "arguments.json"))["arguments"]
        for arguments in (
            original + ["--config", str(directory / "config.json")],
            original + ["--aws-profile", "attacker"],
            original + ["--receipt", "/tmp/operator-receipt.json"],
            original + ["--submission-id", self.submission_id],
            ["plan", "--config", str(directory / "config.json"), "--platform", "ios"],
            ["plan", "--platform", "android"], [], ["plan", 1, 2],
        ):
            (directory / "arguments.json").write_bytes(inputs.encode({"arguments": arguments}))
            with self.subTest(arguments=arguments), patch.object(inputs.subprocess, "run") as command, self.assertRaises(inputs.Rejected):
                inputs.run(directory, self.runner)
            command.assert_not_called()
        inputs.cleanup(directory, self.runner)

    def test_run_cannot_remove_reconciliation_guards_to_launch_a_fresh_submit(self):
        for mutation in ("missing_identifier", "missing_intent", "signed_foreign_build"):
            result = self.prepare("submit", **self.pending_arguments())
            directory = Path(result["directory"])
            if mutation == "missing_intent":
                (directory / "output-receipt.json.intent.json").unlink()
            elif mutation == "missing_identifier":
                args = inputs.json_object(inputs.private_read(directory / "arguments.json"))
                position = args["arguments"].index("--submission-id")
                del args["arguments"][position:position + 2]
                (directory / "arguments.json").write_bytes(inputs.encode(args))
            else:
                (directory / "output-receipt.json.intent.json").write_bytes(
                    self.related_receipt("mobile-store-submission-intent", build_receipt_sha256="d" * 64))
            with self.subTest(mutation=mutation), patch.object(inputs.subprocess, "run") as command, self.assertRaises(REFUSED):
                inputs.run(directory, self.runner)
            command.assert_not_called()
            inputs.cleanup(directory, self.runner)
        result = self.prepare("submit", **self.pending_arguments())
        directory = Path(result["directory"])
        with patch.object(inputs.subprocess, "run") as command:
            inputs.run(directory, self.runner)
        command.assert_called_once()
        inputs.cleanup(directory, self.runner)

    def test_cli_outputs_reveal_no_secret_material_and_cleanup_is_explicit(self):
        output = self.runner / "github-output"
        output.write_text("")
        variables = {"RUNNER_TEMP": str(self.runner), "STORE_RELEASE_INPUTS": json.dumps(self.bundle()),
            "GITHUB_OUTPUT": str(output), "STORE_RECEIPT_KEY": self.receipt_key}
        with patch.dict(os.environ, variables, clear=True), patch("sys.stdout", new_callable=io.StringIO) as stdout:
            result = inputs.main(["prepare", "--operation", "plan", "--platform", "android", "--environment", "qa", "--revision", REVISION])
        self.assertEqual(result, 0)
        self.assertNotIn(self.private, stdout.getvalue())
        self.assertNotIn(self.receipt_key, stdout.getvalue())
        text = output.read_text()
        self.assertNotIn(self.private, text)
        directory = next(self.runner.glob("otgd-store-*"))
        with patch.dict(os.environ, variables, clear=True), patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(inputs.main(["cleanup", "--directory", str(directory)]), 0)
        self.assertFalse(directory.exists())
        with patch.dict(os.environ, {"RUNNER_TEMP": str(self.runner), "STORE_RELEASE_INPUTS": FICTIONAL_SECRET}, clear=True), patch("sys.stderr", new_callable=io.StringIO) as stderr:
            result = inputs.main(["prepare", "--operation", "plan", "--platform", "android", "--environment", "qa", "--revision", REVISION])
        self.assertEqual(result, 1)
        self.assertNotIn(FICTIONAL_SECRET, stderr.getvalue())

    def test_cli_run_seal_and_symlinked_output_boundaries(self):
        result = self.prepare("build", role_arn="arn:aws:iam::123456789012:role/fixture", receipt_key=self.receipt_key)
        directory = Path(result["directory"])
        variables = {"RUNNER_TEMP": str(self.runner), "STORE_RECEIPT_KEY": self.receipt_key}
        with patch.dict(os.environ, variables, clear=True), patch("sys.stdout", new_callable=io.StringIO), patch.object(inputs.subprocess, "run") as command:
            self.assertEqual(inputs.main(["run", "--directory", str(directory)]), 0)
        command.assert_called_once()
        with patch.dict(os.environ, variables, clear=True), patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(inputs.main(["seal", "--directory", str(directory)]), 0)
        inputs.put(directory, "output-receipt.json", self.build_receipt())
        output = self.runner / "github-output"
        output.write_bytes(b'')
        variables["GITHUB_OUTPUT"] = str(output)
        with patch.dict(os.environ, variables, clear=True), patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(inputs.main(["seal", "--directory", str(directory)]), 0)
        self.assertIn("sealed=true", output.read_text())
        self.assertNotIn(self.private, output.read_text())
        inputs.cleanup(directory, self.runner)
        target = self.runner / "operator-output"
        target.write_bytes(b'operator-owned')
        linked = self.runner / "symlink-output"
        linked.symlink_to(target)
        hardlinked = self.runner / "hardlinked-output"
        os.link(target, hardlinked)
        variables.update({"STORE_RELEASE_INPUTS": json.dumps(self.bundle()),
            "STORE_AWS_ROLE_ARN": "arn:aws:iam::123456789012:role/fixture"})
        for refused_output in (linked, hardlinked, self.runner / "missing-output"):
            variables["GITHUB_OUTPUT"] = str(refused_output)
            with self.subTest(output_name=refused_output.name), patch.dict(os.environ, variables, clear=True), patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(inputs.main(["prepare", "--operation", "build", "--platform", "android", "--environment", "qa", "--revision", REVISION]), 1)
            self.assertEqual(target.read_bytes(), b'operator-owned')
            self.assertEqual(list(self.runner.glob("otgd-store-*")), [], "Output failure left a private signing key staged")

    def test_fifo_output_is_refused_without_waiting_for_a_writer(self):
        fifo = self.runner / "output-fifo"
        os.mkfifo(fifo, 0o600)
        environment = {"RUNNER_TEMP": str(self.runner), "STORE_RELEASE_INPUTS": json.dumps(self.bundle()),
            "STORE_RECEIPT_KEY": self.receipt_key, "STORE_AWS_ROLE_ARN": "arn:aws:iam::123456789012:role/fixture",
            "GITHUB_OUTPUT": str(fifo), "AWS_EC2_METADATA_DISABLED": "true"}
        result = subprocess.run([sys.executable, str(ROOT / "apps/mobile/modules/scripts/store_inputs.py"),
            "prepare", "--operation", "build", "--platform", "android", "--environment", "qa", "--revision", REVISION],
            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(self.private, result.stderr)
        self.assertEqual(list(self.runner.glob("otgd-store-*")), [])

    def test_pack_preserves_inputs_and_writes_only_private_scope_and_ciphertext(self):
        for platform in ("android", "ios"):
            sources = self.pack_sources(platform)
            snapshots = {name: (path.read_bytes(), path.stat().st_mode, path.stat().st_ino)
                for name, path in sources.items()}
            with patch.object(inputs.subprocess, "run") as command, patch.object(httpx, "Client") as network:
                target = self.pack(sources, platform=platform)
            command.assert_not_called()
            network.assert_not_called()
            self.assertEqual(target.name, inputs.ENCRYPTED_NAME)
            self.assertEqual({p.name for p in target.parent.iterdir()}, {"scope.json", inputs.ENCRYPTED_NAME})
            self.assertEqual(stat.S_IMODE(target.parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            self.assertEqual(inputs.scope(target.parent, self.runner)["operation"], "pack")
            header, receipts = inputs.decrypt_receipts(inputs.private_read(target, inputs.MAX_BUNDLE),
                self.receipt_key, "qa", platform)
            self.assertEqual(header["source_revision"], REVISION)
            self.assertEqual(receipts["build_receipt"], snapshots["build"][0])
            self.assertEqual(receipts["submission_intent"], snapshots["intent"][0])
            self.assertIsNone(receipts["submission_receipt"])
            for name, path in sources.items():
                self.assertEqual((path.read_bytes(), path.stat().st_mode, path.stat().st_ino), snapshots[name])
            self.assertNotIn(snapshots["build"][0], target.read_bytes())
            self.assertNotIn(snapshots["intent"][0], target.read_bytes())
            self.assertNotIn(self.private.encode(), target.read_bytes())
            inputs.cleanup(target.parent, self.runner)

    def test_pack_completed_outcome_preserves_original_byte_chain_for_status(self):
        sources = self.pack_sources(completed=True)
        target = self.pack(sources)
        blob = inputs.private_read(target, inputs.MAX_BUNDLE)
        result = self.prepare("status", candidate_build_id=self.build_id, submission_id=self.submission_id,
            receipt_package=blob, receipt_key=self.receipt_key)
        directory = Path(result["directory"])
        self.assertEqual(inputs.private_read(directory / "build-receipt.json"), sources["build"].read_bytes())
        self.assertEqual(inputs.private_read(directory / "submission-receipt.json"), sources["submission"].read_bytes())
        inputs.cleanup(directory, self.runner)
        inputs.cleanup(target.parent, self.runner)

    def test_pack_refuses_foreign_scope_config_signer_and_changed_receipt_bytes_before_staging(self):
        sources = self.pack_sources()
        original = {name: path.read_bytes() for name, path in sources.items()}
        variants = [
            ("config", inputs.encode({**inputs.json_object(original["config"]), "oauth_client_id": "B" * 26})),
            ("build", self.build_receipt(source_revision="b" * 40)),
            ("build", self.build_receipt(environment="prod")),
            ("build", self.build_receipt(platform="ios")),
            ("build", self.build_receipt(public_release=True)),
            ("build", original["build"].rstrip()),
            ("intent", self.related_receipt("mobile-store-submission-intent", build_id=self.submission_id)),
            ("intent", self.related_receipt("mobile-store-submission-intent", build_receipt_sha256="d" * 64)),
            ("public", Ed25519PrivateKey.generate().public_key().public_bytes(
                serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)),
        ]
        for field, raw in variants:
            sources[field].write_bytes(raw)
            with self.subTest(field=field), patch.object(inputs, "new_directory") as created:
                self.assert_clean_refusal(lambda: self.pack(sources))
            created.assert_not_called()
            sources[field].write_bytes(original[field])
        for parameters in ({"environment": "prod"}, {"platform": "ios"}, {"revision": "b" * 40}, {"key": "bad-key"}):
            with self.subTest(parameters=parameters), patch.object(inputs, "new_directory") as created:
                self.assert_clean_refusal(lambda: self.pack(sources, **parameters))
            created.assert_not_called()

    def test_pack_refuses_missing_linked_public_or_readable_private_inputs(self):
        sources = self.pack_sources()
        original = sources["intent"].read_bytes()
        sources["intent"].unlink()
        with patch.object(inputs, "new_directory") as created:
            self.assert_clean_refusal(lambda: self.pack(sources))
        created.assert_not_called()
        sources["intent"].write_bytes(original)
        sources["intent"].chmod(0o600)
        for field in ("config", "build", "intent", "public"):
            sources[field].chmod(0o644)
            with self.subTest(field=field), patch.object(inputs, "new_directory") as created:
                self.assert_clean_refusal(lambda: self.pack(sources))
            created.assert_not_called()
            sources[field].chmod(0o600)
        link = self.runner / "operator-public-link"
        link.symlink_to(sources["public"])
        with patch.object(inputs, "new_directory") as created:
            self.assert_clean_refusal(lambda: self.pack({**sources, "public": link}))
        created.assert_not_called()

    def test_pack_rejects_completed_outcome_for_different_build_or_original_intent(self):
        sources = self.pack_sources(completed=True)
        for changes in ({"submission_intent_sha256": "d" * 64}, {"build_receipt_sha256": "e" * 64},
            {"build_id": self.submission_id}, {"submission_id": "not-a-provider-uuid"}, {"public_release": True}):
            raw = self.related_receipt("mobile-store-submission", build=sources["build"].read_bytes(),
                **{"submission_intent_sha256": hashlib.sha256(sources["intent"].read_bytes()).hexdigest(), **changes})
            sources["submission"].write_bytes(raw)
            with self.subTest(changes=changes), patch.object(inputs, "new_directory") as created:
                self.assert_clean_refusal(lambda: self.pack(sources))
            created.assert_not_called()

    def test_pack_detects_config_changes_and_oversize_secret_without_dropping_proof(self):
        sources = self.pack_sources()
        read_config = store.read_config
        def changed_config(path):
            config = read_config(path)
            sources["config"].write_bytes(inputs.encode({**config, "oauth_client_id": "B" * 26}))
            return config
        with patch.object(store, "read_config", side_effect=changed_config), patch.object(inputs, "new_directory") as created:
            self.assert_clean_refusal(lambda: self.pack(sources))
        created.assert_not_called()
        sources = self.pack_sources()
        build = self.build_receipt(fixture_padding="x" * 40000)
        intent = self.related_receipt("mobile-store-submission-intent", build=build)
        sources["build"].write_bytes(build)
        sources["intent"].write_bytes(intent)
        with patch.object(inputs, "new_directory") as created:
            self.assert_clean_refusal(lambda: self.pack(sources))
        created.assert_not_called()
        self.assertEqual(sources["build"].read_bytes(), build)
        self.assertEqual(sources["intent"].read_bytes(), intent)

    def test_cli_pack_to_protected_ciphertext_reconciliation_preserves_inner_bytes(self):
        sources = self.pack_sources()
        variables = {"RUNNER_TEMP": str(self.runner), "STORE_RECEIPT_KEY": self.receipt_key}
        arguments = ["pack", "--config", str(sources["config"]), "--build-receipt", str(sources["build"]),
            "--submission-intent", str(sources["intent"]), "--trusted-public-key", str(sources["public"]),
            "--environment", "qa", "--platform", "android", "--revision", REVISION]
        with patch.dict(os.environ, variables, clear=True), patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(inputs.main(arguments), 0)
        pack_directory = next(self.runner.glob("otgd-store-*"))
        encrypted = inputs.private_read(pack_directory / inputs.ENCRYPTED_NAME, inputs.MAX_BUNDLE)
        self.assertNotIn(sources["build"].read_text(), stdout.getvalue())
        self.assertNotIn(self.receipt_key, stdout.getvalue())
        output = self.runner / "github-output"
        output.write_bytes(b'')
        variables.update({"STORE_RECEIPT_PACKAGE": encrypted.decode("utf-8"),
            "STORE_RELEASE_INPUTS": json.dumps(self.bundle()), "GITHUB_OUTPUT": str(output),
            "STORE_AWS_ROLE_ARN": "arn:aws:iam::123456789012:role/fixture"})
        with patch.dict(os.environ, variables, clear=True), patch("sys.stdout", new_callable=io.StringIO), patch.object(inputs, "download_receipts") as download:
            self.assertEqual(inputs.main(["prepare", "--operation", "submit", "--platform", "android",
                "--environment", "qa", "--revision", REVISION, "--candidate-build-id", self.build_id,
                "--submission-id", self.submission_id]), 0)
        download.assert_not_called()
        directory = next(p for p in self.runner.glob("otgd-store-*") if p != pack_directory)
        self.assertEqual(inputs.private_read(directory / "build-receipt.json"), sources["build"].read_bytes())
        self.assertEqual(inputs.private_read(directory / "output-receipt.json.intent.json"), sources["intent"].read_bytes())
        self.assertNotIn(encrypted.decode(), output.read_text())
        inputs.cleanup(directory, self.runner)
        inputs.cleanup(pack_directory, self.runner)

    def test_protected_package_refuses_artifact_conflicts_invalid_json_and_oversize_before_staging(self):
        variables = {"RUNNER_TEMP": str(self.runner), "STORE_RECEIPT_KEY": self.receipt_key,
            "STORE_RELEASE_INPUTS": json.dumps(self.bundle()), "STORE_AWS_ROLE_ARN": "arn:aws:iam::123456789012:role/fixture"}
        base = ["prepare", "--operation", "submit", "--platform", "android", "--environment", "qa",
            "--revision", REVISION, "--candidate-build-id", self.build_id, "--submission-id", self.submission_id]
        for protected, extra in ((self.package().decode(), ["--receipt-artifact-id", "23"]),
            ('{"nonce":"first","nonce":"second"}', []), ('{"value":NaN}', []),
            ("x" * (inputs.MAX_BUNDLE + 1), [])):
            variables["STORE_RECEIPT_PACKAGE"] = protected
            with self.subTest(has_artifact=bool(extra)), patch.dict(os.environ, variables, clear=True), patch.object(inputs, "download_receipts") as download, patch.object(inputs, "new_directory") as created, patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(inputs.main([*base, *extra]), 1)
            download.assert_not_called()
            created.assert_not_called()
            self.assertEqual(list(self.runner.glob("otgd-store-*")), [])


if __name__ == "__main__":
    unittest.main()
