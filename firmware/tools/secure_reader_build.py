#!/usr/bin/env python3
"""Build-only protected SDK entry. Never flashes, provisions or burns eFuses."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "secure_reader"
PINS = json.loads((PROJECT / "sources.json").read_text())
REQUIRED = (
    "CONFIG_NVS_ENCRYPTION=y",
    "CONFIG_SECURE_BOOT_V2_ENABLED=y",
    "CONFIG_SECURE_FLASH_ENC_ENABLED=y",
    "CONFIG_SECURE_FLASH_ENCRYPTION_MODE_RELEASE=y",
    "CONFIG_BT_BLE_42_FEATURES_SUPPORTED=y",
    "CONFIG_BT_SMP_ENABLE=y",
    "CONFIG_ARDUHAL_LOG_DEFAULT_LEVEL_ERROR=y",
)


def command(
    args: list[str], *, cwd: Path | None = None, env: dict | None = None
) -> str:
    return subprocess.run(
        args, cwd=cwd, env=env, check=True, text=True, stdout=subprocess.PIPE
    ).stdout.rstrip("\n")


def checkout(cache: Path, name: str) -> Path:
    pin = PINS["repositories"][name]
    revision = pin["revision"]
    if (
        not re.fullmatch("[0-9a-f]{40}", revision)
        or pin["url"]
        != {
            "esp-idf": "https://github.com/espressif/esp-idf.git",
            "arduino": "https://github.com/espressif/arduino-esp32.git",
            "ArduinoJson": "https://github.com/bblanchon/ArduinoJson.git",
        }[name]
    ):
        raise ValueError("Invalid immutable official source pin")
    target = cache / name
    if target.is_symlink():
        raise ValueError("Source cache must not be a symlink")
    if not target.exists():
        target.mkdir()
        command(["git", "init", "--quiet"], cwd=target)
        command(["git", "remote", "add", "origin", pin["url"]], cwd=target)
        command(["git", "fetch", "--depth", "1", "origin", revision], cwd=target)
        command(["git", "checkout", "--detach", revision], cwd=target)
        if name == "esp-idf":
            command(
                ["git", "submodule", "update", "--init", "--recursive", "--depth", "1"],
                cwd=target,
            )
    if (
        command(["git", "rev-parse", "HEAD"], cwd=target) != revision
        or command(["git", "remote", "get-url", "origin"], cwd=target) != pin["url"]
        or command(["git", "status", "--porcelain", "--untracked-files=no"], cwd=target)
    ):
        raise ValueError("Source revision/origin/cleanliness verification failed")
    if name == "esp-idf":
        rows = command(
            ["git", "submodule", "status", "--recursive"], cwd=target
        ).splitlines()
        if not rows or any(row[0] != " " for row in rows):
            raise ValueError("Uninitialized or changed immutable SDK submodule")
    return target


def private_key(path: Path) -> bytes:
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) & 0o077
            or info.st_nlink != 1
            or info.st_size > 16384
        ):
            raise ValueError(
                "Boot signing key must be a private owned bounded regular file"
            )
        data = os.read(fd, 16385)
        if not data or len(data) > 16384:
            raise ValueError("Boot signing key size invalid")
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        key = load_pem_private_key(data, None)
        if (
            not isinstance(key, rsa.RSAPrivateKey)
            or key.key_size != 3072
            or key.public_key().public_numbers().e != 65537
        ):
            raise ValueError("ESP32-S3 Secure Boot V2 requires RSA3072 / exponent65537")
        return data
    finally:
        os.close(fd)


def validate_config(path: Path) -> None:
    config = set(path.read_text().splitlines())
    if (
        any(value not in config for value in REQUIRED)
        or 'CONFIG_IDF_TARGET="esp32s3"' not in config
    ):
        raise ValueError("Security-enabled ESP32-S3 configuration was not retained")


def build(cache: Path, output: Path, signing: Path) -> dict:
    if (
        output.is_symlink()
        or cache.is_symlink()
        or output.resolve() == PROJECT.resolve()
    ):
        raise ValueError("Use separate regular cache/output directories")
    cache.mkdir(parents=True, exist_ok=True)
    sources = {name: checkout(cache, name) for name in PINS["repositories"]}
    output.mkdir(parents=True, exist_ok=True)
    (output / "build-manifest.json").unlink(missing_ok=True)
    key = output / ".secure-boot-signing.pem"
    fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(private_key(signing))
        override = output / "sdkconfig.security"
        # json escaping is Kconfig escaping here, never a shell command.
        override.write_text(
            "CONFIG_SECURE_BOOT_SIGNING_KEY=" + json.dumps(str(key.resolve())) + "\n"
        )
        config = output / "sdkconfig"
        if config.is_symlink():
            raise ValueError("Generated sdkconfig must not be symlinked")
        config.unlink(missing_ok=True)
        env = {
            **os.environ,
            "IDF_PATH": str(sources["esp-idf"]),
            "IDF_TARGET": "esp32s3",
            "IDF_COMPONENT_MANAGER": "0",
            "IDF_TOOLS_PATH": os.environ.get("IDF_TOOLS_PATH", str(cache / "tools")),
            "IDF_COMPONENT_CACHE_PATH": str(cache / "component-cache"),
        }
        subprocess.run(
            [
                sys.executable,
                str(sources["esp-idf"] / "tools/idf.py"),
                "-C",
                str(PROJECT),
                "-B",
                str(output),
                "-D",
                "SDKCONFIG=" + str(config),
                "-D",
                "SDKCONFIG_DEFAULTS="
                + str(PROJECT / "sdkconfig.defaults")
                + ";"
                + str(override),
                "-D",
                "OTGD_ARDUINO_COMPONENT=" + str(sources["arduino"]),
                "-D",
                "OTGD_ARDUINO_JSON=" + str(sources["ArduinoJson"]),
                "build",
            ],
            env=env,
            check=True,
        )
        validate_config(config)
        artifacts = {}
        for relative in (
            "otgd_secure_reader.bin",
            "bootloader/bootloader.bin",
            "partition_table/partition-table.bin",
        ):
            artifact = output / relative
            if (
                artifact.is_symlink()
                or not artifact.is_file()
                or artifact.stat().st_size < 32
            ):
                raise ValueError("Actual compiled binary missing")
            artifacts[relative] = {
                "bytes": artifact.stat().st_size,
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            }
        source_files = {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in (ROOT / "nano_esp32_signed_reader", PROJECT)
            for path in sorted(folder.rglob("*"))
            if path.is_file()
            and path.suffix
            in (".h", ".cpp", ".ino", ".txt", ".csv", ".json", ".defaults", ".lock")
        }
        manifest = {
            "source_sha256": source_files,
            "schema_version": "1.0.0",
            "purpose": "unprovisioned build qualification only",
            "source_pins": PINS,
            "artifacts": artifacts,
            "flashed": False,
            "physical_qualification": False,
        }
        (output / "build-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        return manifest
    finally:
        key.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "build"))
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--boot-signing-key", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        args.cache.mkdir(parents=True, exist_ok=True)
        print(
            json.dumps(
                {
                    name: str(checkout(args.cache, name))
                    for name in PINS["repositories"]
                },
                indent=2,
            )
        )
    else:
        if args.output is None or args.boot_signing_key is None:
            parser.error("build requires --output and --boot-signing-key")
        print(
            json.dumps(build(args.cache, args.output, args.boot_signing_key), indent=2)
        )


if __name__ == "__main__":
    main()
