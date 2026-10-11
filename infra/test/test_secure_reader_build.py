import importlib.util
import os
import subprocess
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "otgd_secure_reader_build", ROOT / "firmware/tools/secure_reader_build.py"
)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def key_file(path, key):
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)
    return path


def test_only_private_rsa3072_build_key_is_admitted(tmp_path):
    path = key_file(
        tmp_path / "build.pem",
        rsa.generate_private_key(public_exponent=65537, key_size=3072),
    )
    assert helper.private_key(path) == path.read_bytes()
    path.chmod(0o644)
    with pytest.raises(ValueError):
        helper.private_key(path)
    path.chmod(0o600)
    symlink = tmp_path / "link.pem"
    symlink.symlink_to(path)
    with pytest.raises(OSError):
        helper.private_key(symlink)
    os.link(path, tmp_path / "second.pem")
    with pytest.raises(ValueError):
        helper.private_key(path)


@pytest.mark.parametrize("kind", ["wrong-rsa", "ec", "large", "fifo"])
def test_build_key_rejects_wrong_algorithm_size_and_non_regular_file(tmp_path, kind):
    path = tmp_path / "key"
    if kind == "wrong-rsa":
        key_file(path, rsa.generate_private_key(public_exponent=65537, key_size=2048))
    elif kind == "ec":
        key_file(path, ec.generate_private_key(ec.SECP256R1()))
    elif kind == "large":
        path.write_bytes(b"x" * 16385)
        path.chmod(0o600)
    else:
        os.mkfifo(path, 0o600)
    with pytest.raises(ValueError):
        helper.private_key(path)


def test_security_config_must_retain_every_enforced_security_option(tmp_path):
    config = tmp_path / "sdkconfig"
    rows = [*helper.REQUIRED, 'CONFIG_IDF_TARGET="esp32s3"']
    config.write_text("\n".join(rows))
    helper.validate_config(config)
    for missing in rows:
        config.write_text("\n".join(row for row in rows if row != missing))
        with pytest.raises(ValueError):
            helper.validate_config(config)


def test_checkout_verifies_actual_git_revision_origin_and_changes(
    tmp_path, monkeypatch
):
    repo = tmp_path / "arduino"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Software test"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "fixture@example.invalid"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "remote",
            "add",
            "origin",
            "https://github.com/espressif/arduino-esp32.git",
        ],
        check=True,
    )
    tracked = repo / "tracked.txt"
    tracked.write_text("fixture only\n")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "--quiet", "-m", "Fixture"], check=True
    )
    revision = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    monkeypatch.setitem(helper.PINS["repositories"]["arduino"], "revision", revision)
    assert helper.checkout(tmp_path, "arduino") == repo
    tracked.write_text("changed\n")
    with pytest.raises(ValueError):
        helper.checkout(tmp_path, "arduino")
    tracked.write_text("fixture only\n")
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "remote",
            "set-url",
            "origin",
            "https://example.invalid/foreign.git",
        ],
        check=True,
    )
    with pytest.raises(ValueError):
        helper.checkout(tmp_path, "arduino")


def test_actual_submodule_status_prefix_is_preserved_and_uninitialized_modules_fail(
    tmp_path, monkeypatch
):
    child = tmp_path / "fixture-child"
    repo = tmp_path / "esp-idf"
    for folder in (child, repo):
        subprocess.run(["git", "init", "--quiet", str(folder)], check=True)
        subprocess.run(
            ["git", "-C", str(folder), "config", "user.name", "Software test"],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(folder),
                "config",
                "user.email",
                "fixture@example.invalid",
            ],
            check=True,
        )
    (child / "fixture.txt").write_text("no vendor source or runtime key\n")
    subprocess.run(["git", "-C", str(child), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(child), "commit", "--quiet", "-m", "Fixture child"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "remote",
            "add",
            "origin",
            "https://github.com/espressif/esp-idf.git",
        ],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "protocol.file.allow=always",
            "-C",
            str(repo),
            "submodule",
            "add",
            "--quiet",
            str(child),
            "libs/child",
        ],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "--quiet", "-m", "Fixture parent"],
        check=True,
    )
    revision = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    monkeypatch.setitem(helper.PINS["repositories"]["esp-idf"], "revision", revision)
    assert helper.command(
        ["git", "submodule", "status", "--recursive"], cwd=repo
    ).startswith(" ")
    assert helper.checkout(tmp_path, "esp-idf") == repo
    subprocess.run(
        ["git", "-C", str(repo), "submodule", "deinit", "--force", "--all"],
        check=True,
        stdout=subprocess.PIPE,
    )
    with pytest.raises(ValueError, match="submodule"):
        helper.checkout(tmp_path, "esp-idf")
