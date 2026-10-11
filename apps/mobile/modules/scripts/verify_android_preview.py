#!/usr/bin/env python3
"""Inspect a built local preview APK; never substitute this for Gradle execution."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile


def main() -> None:
    project = Path(__file__).resolve().parents[2]
    if os.environ.get("APP_ENV") != "local":
        raise SystemExit("Local preview verification requires APP_ENV=local")
    artifacts = list((project / "android/app/build/outputs/apk/release").glob("*.apk"))
    if len(artifacts) != 1:
        raise SystemExit("Expected exactly one built local preview Release APK")
    apk = artifacts[0]
    sdk = Path(os.environ.get("ANDROID_HOME", os.environ.get("ANDROID_SDK_ROOT", "/usr/local/lib/android/sdk")))
    build_tools = sdk / "build-tools/36.0.0"
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SystemExit("Duplicate APK archive entry")
        if "assets/index.android.bundle" not in names or archive.getinfo("assets/index.android.bundle").file_size == 0:
            raise SystemExit("Missing embedded JavaScript/Hermes bundle; this is not a standalone preview")
        for architecture in ("arm64-v8a", "x86_64"):
            if not any(name.startswith(f"lib/{architecture}/") and name.endswith(".so") for name in names):
                raise SystemExit(f"Missing native libraries for {architecture}")
    manifest = subprocess.run([str(build_tools / "aapt2"), "dump", "badging", str(apk)], check=True, text=True, capture_output=True).stdout
    if not re.search(r"^package: name='dev\.r3fresh\.otgd\.local' ", manifest, re.MULTILINE):
        raise SystemExit("The APK does not have the required local application identifier")
    if re.search(r"^application-debuggable", manifest, re.MULTILINE):
        raise SystemExit("The embedded preview variant must not be Android-debuggable")
    # The public generated debug key is intentional for local previews. Verify the
    # APK's actual signer matches that exact generated key rather than accepting an
    # arbitrary certificate whose human-readable name happens to say Android Debug.
    with tempfile.TemporaryDirectory(prefix="otgd-local-preview-") as temp:
        certificate = Path(temp) / "development.der"
        subprocess.run(["keytool", "-exportcert", "-keystore", str(project / "android/app/debug.keystore"), "-storepass", "android", "-alias", "androiddebugkey", "-file", str(certificate)], check=True, capture_output=True)
        expected_sha = hashlib.sha256(certificate.read_bytes()).hexdigest()
    signature = subprocess.run([str(build_tools / "apksigner"), "verify", "--verbose", "--print-certs", str(apk)], check=True, text=True, capture_output=True).stdout
    signers = re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]+)$", signature, re.MULTILINE)
    if signers != [expected_sha]:
        raise SystemExit("APK signer does not match the generated local development key")
    output = project / "native-build/otgd-local-preview.apk"
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(apk, output)
    print(f"Inspected actual local preview APK: {output.name}; bytes={output.stat().st_size}; sha256={hashlib.sha256(output.read_bytes()).hexdigest()}")
    print("Embedded bundle and both native architectures present. Generated development signer verified. No Play signing or device execution is claimed.")


if __name__ == "__main__":
    main()
