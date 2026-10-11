# Build the protected reader SDK

This build-only project compiles the actual signed-reader sketch and real ADC driver with ESP-IDF NVS encryption, Secure Boot V2 and release-mode flash encryption. The stock Nano SDK cannot enable the protected identity branch. This project addresses that software build gap; it does not automatically provision keys, flash a device, burn eFuses or qualify body-connected hardware.

## Exact sources and tool environment

[sources.json](sources.json) pins official immutable ESP-IDF4.4.7, Arduino-ESP322.0.17 (whose official CMake matrix supports IDF4.4.x) and ArduinoJson7.4.2 commits. These pins are a compatibility baseline; release security review of the vendor SDK remains required. The ordinary Arduino Nano target continues using its separately pinned2.0.18-arduino.5 package. The secure target is ESP32-S3 with raw GPIO numbering; it does not replace Arduino pin numbers implicitly.

Use Python 3.12 and Git. The official pinned IDF tool manifest recommends CMake 3.23.1, Ninja 1.10.2 and Xtensa ESP32-S3 GCC 8.4.0 esp2021r2-patch5; CI installs those exact checked versions. Local compilation also passed with the separately cached CMake 3.22.1 and the same official compiler. The IDF source's tool installer validates its official checksum manifest. Cached matching compiler/CMake executables may instead be placed on PATH. `requirements.lock` records exact SHA256-pinned Python build dependencies resolved from this immutable SDK's requirements; install it into a private build venv.

```sh
python firmware/tools/secure_reader_build.py prepare --cache /tmp/otgd-secure-sdk
python -m venv /tmp/otgd-secure-sdk/python
/tmp/otgd-secure-sdk/python/bin/pip install --require-hashes \
  -r firmware/secure_reader/requirements.lock
export IDF_PATH=/tmp/otgd-secure-sdk/esp-idf
export IDF_TOOLS_PATH=/tmp/otgd-secure-sdk/tools
/tmp/otgd-secure-sdk/python/bin/python "$IDF_PATH/tools/idf_tools.py" \
  install xtensa-esp32s3-elf cmake ninja
```

Add the installed versioned tool executable directories to PATH as reported by the official installer, or run its export command in your shell. Keep source/cache/build output outside the repository. Preparing verifies actual HEAD, official origin, clean tracked files and exact recursive Git submodule identities; changed or incomplete caches fail.

## Build with an explicit signing key

An authorized release operator supplies their own RSA3072 Secure Boot V2 signing PEM (exponent65537), owned by the current user, private0600, regular/nonlinked and at most16KiB. The helper refuses symlinks, FIFOs, world/group access, hardlinked files and wrong algorithms. It never generates a production identity or boot key. A CI qualification job may explicitly create an ephemeral fictional build-signing key; that binary remains unprovisioned and is unsuitable for a deployed reader identity.

```sh
/tmp/otgd-secure-sdk/python/bin/python firmware/tools/secure_reader_build.py build \
  --cache /tmp/otgd-secure-sdk \
  --output /tmp/otgd-secure-reader-build \
  --boot-signing-key /secure/operator/reader-secure-boot.pem
```

The helper invokes the real IDF build without a shell command, copies the admitted key into an exclusive0600 temporary build file, and removes that temporary key on success or failure. It verifies the generated sdkconfig retains the target and all security controls. Missing real application/bootloader/partition binaries fail. `build-manifest.json` records source pins, actual reader/SDK configuration file hashes and binary hashes/lengths, explicitly `flashed=false` and `physical_qualification=false`. The manifest is unsigned build metadata and does not establish hardware attestation.

The source [partitions.csv](partitions.csv) defines a16MiB ESP32-S3 research-reader image. `otgd_nvs_keys` is marked flash-encrypted and `otgd_identity` is accessed only through encrypted NVS initialization. GPIO/front-end/calibration material is never inferred from the board variant. GPIO admissibility and any changes to boot/flash partitions require hardware-specific operator review.

## Offline provisioning and release prerequisites

The organization must independently provision the device's P256 PKCS8 signing key, approved device/key/hardware/firmware identifiers, the approved server P256 public SPKI and signer label, encrypted NVS XTS keys, a unique per-device six-digit BLE passkey and exact ADC configuration/calibration material. Supply the pairing passkey on a controlled physical per-device label; never print it in logs or use a shared default. BLE requires Secure Connections with MITM bonding and encrypted-MITM GATT/CCCD permissions before any command or health notification. Runtime `ProtectedSigner` verifies actual secure-boot and flash-encryption hardware state, the encrypted key partition and P256 curve. It supplies no plaintext, phone key, auto-generated identity or fallback. Public-key approval and device key custody remain separate from compiling a binary.

Boot/flash encryption eFuses and permanent download restrictions are hardware operations requiring a reviewed manufacturing/provisioning plan. This helper exposes no flash/burn/provision command. Actual protected hardware startup, key secrecy, correct Nano GPIO wiring, isolated ECG front-end/electrical safety, contact behavior, calibration, clock bounds, BLE peer privacy and physiological extraction still require physical qualification. Unknown saliva/alcohol/assay instruments require their actual documented vendor driver.

Portable tests cover key/source/security-config refusal, JCS/domain fidelity, actual-used ADC scheduling and connection isolation. The ordinary board compile covers the default sketch; only a successful security-enabled IDF compile covers the protected NVS code branch. Record each result separately and require fresh exact-source CI before merge.


The actual local protected build passed on 2026-10-11 with the documented pinned sources and a temporary fictional RSA3072 build-signing key. Its generated manifest is in the external build output, never a production key/provisioning record. CI repeats this branch as `native / protected-reader`; the ordinary stock board build is a separate gate. Physical pairing/security, electrical safety, calibration, protected key provisioning and scientific validation remain external release evidence.
