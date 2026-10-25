# Firmware baseline verification — otgd-20261025-0555

Status: **PASS for the declared baseline firmware software checks**: portable host suites, both actual stock Nano ESP32 builds and the actual protected ESP-IDF build passed. The temporary workspace resource blocker was resolved before the protected build. This report is baseline verification evidence, not final per-spec signoff or release approval.

Role/identity: Factory firmware/toolchain verification specialist, /root/firmware_validation, assigned OpenAI gpt-6.1-sol/high. Candidate supplied by PM: `0844868aa543af4ab75ac5065ad48cf807b86bb3`, branch `factory/one-the-go-detection-20261025`. No source edits or repository Git operations performed. correction_round=0; recovery_attempts=0.

Read AGENTS.md; pinned Factory SKILL.md and communication/evidence references; run/inventory and D-001–004; .github/workflows/native-build.yml; firmware guides/source pins/requirements/CMake/helper. D-001 v1 AFFECTED (measurement/provenance/research/scientific and no-flash boundaries); D-002–004 v1 NOT_AFFECTED for the isolated firmware verification scope. Actual impact acknowledgments sent to PM before checks. PM explicitly allowed pinned dependency helper Git operations only under /tmp.

## Executed checks

All UTC timestamps below are 2026-10-25. Raw exact commands, start/end timestamps and exits: `/tmp/otgd-firmware-verification/results.jsonl`; each record identifies its corresponding raw log. Detailed contemporaneous draft: `/tmp/otgd-firmware-verification/firmware-validation-draft.md`.

| Check | UTC interval | Exit | Observed result |
|---|---|---:|---|
| Protocol core and acquisition scheduler/extractor C++17 suites, -Wall -Wextra -Werror, acquisition -pthread | 06:01:37.512–06:01:39.211 | 0 | PASS |
| Pinned ArduinoJson/SparkFun host suite + byte-exact fixture cmp; signed reader JCS/domain/bounds; OpenSSL P256 server-grant suite | 06:02:19.011–06:02:22.879 | 0 | PASS |
| Nano ESP32 simulator actual arduino:esp32:nano_nora compile, warnings all | 06:02:35.805–06:02:55.947 | 0 | PASS; 956,533 program bytes; 75,068 static global bytes |
| Signed-reader same board compile, warnings all, /tmp output | 06:03:52.758–06:03:57.259 | 0 | PASS; 1,064,753 program bytes; 76,948 static global bytes |
| Protected helper immutable source preparation, origin/HEAD/cleanliness/recursive submodule verification | 06:02:00.423–06:04:34.330 | 0 | PASS |
| Private Python 3.12 protected requirements.lock install with --require-hashes | 06:03:21.523–06:03:25.331 | 0 | PASS |
| Official checked Xtensa/CMake/Ninja installation | 06:03:46.350–06:03:51.624 | 0 | PASS |
| Actual protected security-enabled ESP-IDF compile | 2026-10-25T06:09:17.719761+00:00–2026-10-25T06:10:08.377773+00:00 | 0 | PASS; actual encrypted NVS, secure boot, release flash encryption and authenticated BLE branch |

Portable outputs confirm strict CRC/JSON/Unicode/duplicates/framing/replay/timeouts; actual ADC contact/timestamps/calibration/bounds/drops/cutoff/origin transition/expiry negatives; pinned SDK I2C/mode1/mode2/short/error/stale reads and production-core deadlines/contact/quality/cancel checks; JCS numeric/string fixtures and NUL-domain isolation; protected-SPKI signature and scope/expiry/mutation negatives. Host fixtures are software evidence only.

## Sources, dependencies and artifacts

Full pre-check source SHA256 manifest: `/tmp/otgd-firmware-verification/source-before.json`. It covers firmware sources/config/docs/tests plus native-build.yml and AGENTS.md. All 56 pre-check source hashes match after all builds; protected helper also verified its reader/config/attribution source manifest unchanged before/after compilation. The offline fictional grant HTTP fixture SHA256 was separately recorded. Recheck hashes before carrying evidence to a later candidate. Simulator artifacts: `firmware/build/nano_esp32/`; signed-reader artifacts: `/tmp/otgd-firmware-verification/build/signed_reader/`. All stock/protected artifacts were independently hashed and lengths verified; see durable artifact tables below and final-evidence.json. Protected outputs are /tmp/otgd-firmware-protected-build. Both temporary fictional signing-key files were verified absent after build completion.

Pinned versions match CI: Arduino CLI 1.5.1; arduino:esp32@2.0.18-arduino.5; ArduinoJson 7.4.2; pyserial 3.5. CLI archive SHA256 `28a8e119c498a25607821c36cb2dc49e8463941b261a0d99091baa7bc692dd2b`; board archive `03596062ab1745bf7847d09900e2aebfc1f49cf123d47ba8a57d652e110cda5c`; ArduinoJson archive `5848dbc2a2eca7eb469710f64106195e90e6788a2365859f88c491214a108230`. These match CI/official indices; exact index records are `board-source.json` and `library-source.json` under the evidence directory. CLI archive paths/links/ELF, board build recipes/hooks, Python wheel metadata/paths/hooks and reedsolo source setup were inspected. No source/version substitution or security bypass used.

Protected immutable source pins: ESP-IDF `38eeba213aa695aabfd6d89aa9f5078dbe5a94c3` (4.4.7), Arduino `5e19e086c43d0fa5e5a596497ff8f11a0a43f6c2` (2.0.17), ArduinoJson `733bc4ee82630c88c0a619a883cd3a206efae977` (7.4.2). Helper also verifies selected SparkFun source/attribution at `91575258e5e2c47f0f4b8ec97b651381671f4637` (1.1). Protected exact tools: GCC ESP32-S3 esp-2021r2-patch5-8.4.0; CMake 3.23.1; Ninja 1.10.2. Recomputed archive checksums match official pinned tools.json in `/tmp/otgd-firmware-verification/secure-toolchain-checksums.json`. Hash-locked Python distribution inspection: `python-download-inspection.json`. Wheel-only resolution failed for reedsolo 1.5.4; inspected exact hash-locked source install passed. Host: Linux x86_64 glibc 2.41, Python 3.12.14, g++ 14.2.0; CI host is Ubuntu 24.04.

Arduino CLI explicit config data/user/download dirs, proxy and XDG_CACHE_HOME are under /tmp; HOME was never changed. Initial read-only home/cache and direct-network errors were resolved with ordinary explicit paths/proxy. First signed-reader build failed copying output into the full workspace; repeat changed only output-dir and passed. Logs retain failures and successes. No approval denial occurred.

## Blocker and remaining prerequisites

At approximately 06:03 UTC, /workspace overlay reached 32 GiB/100% with zero free; /tmp still had over 5 GiB free. Original signed-reader output failed `mkdir firmware/build/signed_reader: no space left on device`. Then new exec_command shells, including workdir=/tmp, failed before execution with `bwrap: Can't create file /workspace/.git: No space left on device` (exit 1). **Action:** launch actual protected SDK build and final source/artifact hashing. **Target:** /tmp/otgd-firmware-secure-sdk and /tmp protected output. **State:** RESOLVED: later shell startup succeeded with /workspace 2.0 GiB and /tmp 4.3 GiB free; the actual protected build then ran successfully. No denied action or uncertain execution remains. PM alerted immediately. Existing prepare session finished successfully. Shared Docker/app data/volumes and other workers' files were preserved.

No flash/eFuse/provisioning, physical BLE pairing/radio/privacy testing, body-connected acquisition, electrical safety, calibration/sensor qualification, clinical validation, participant authorization or fitness-to-drive inference occurred. Future alcohol remains the separately qualified calibrated fuel-cell breath-alcohol channel in mg/L; unknown instrument drivers are not validated. Independent scientific approvals remain required. These scoped software results do not satisfy project-wide coverage, unrelated API/app/native/live-dependency/release gates, or final exact-candidate CI requirements.


## Final verification evidence

Recorded 2026-10-25T06:10:39.350269+00:00. All selected checks returned zero on their final executions; no firmware software failure remains in the declared scope. No implementation was changed. ESP-IDF embedded application version is `33901a1-dirty`, derived from the current checkpoint/document-working-tree state; complete firmware source hashes below bind the build to the unchanged supplied implementation baseline. This does not assert the entire checkout still has baseline HEAD.

Generated security configuration retained:

```text
CONFIG_NVS_ENCRYPTION=y
CONFIG_SECURE_BOOT_V2_ENABLED=y
CONFIG_SECURE_FLASH_ENC_ENABLED=y
CONFIG_SECURE_FLASH_ENCRYPTION_MODE_RELEASE=y
CONFIG_BT_BLE_42_FEATURES_SUPPORTED=y
CONFIG_BT_SMP_ENABLE=y
CONFIG_ARDUHAL_LOG_DEFAULT_LEVEL_ERROR=y
CONFIG_IDF_TARGET="esp32s3"
```

The temporary fictional RSA3072 key was used only for an unprovisioned software build. No production identity/key was supplied. `build-manifest.json` is unsigned build metadata, not physical attestation.

### Exact executed commands and outcomes

**portable** — 2026-10-25T06:01:37.511707+00:00 to 2026-10-25T06:01:39.211034+00:00; exit 0; 1.699s. Log SHA256 `5cbaaaa2591cc16482a758796fecc93c803183c76e7be014cc00e8c6dfa8b941` at `/tmp/otgd-firmware-verification/portable.log`.

```json
[
  "bash",
  "-euo",
  "pipefail",
  "-c",
  "g++ -std=c++17 -Wall -Wextra -Werror firmware/tests/protocol_core_test.cpp -o /tmp/otgd-firmware-verification/otgd-protocol-test\n/tmp/otgd-firmware-verification/otgd-protocol-test\ng++ -std=c++17 -Wall -Wextra -Werror -pthread firmware/tests/signed_reader_acquisition_test.cpp -o /tmp/otgd-firmware-verification/otgd-reader-acquisition-test\n/tmp/otgd-firmware-verification/otgd-reader-acquisition-test"
]
```

**arduino-index** — 2026-10-25T06:01:41.825131+00:00 to 2026-10-25T06:01:41.927910+00:00; exit 1; 0.103s. Log SHA256 `e69fa3849ffecbf6754c7fda1da84e2bdaba068c1076930a0ac976ff0df1bdf4` at `/tmp/otgd-firmware-verification/arduino-index.log`.

```json
[
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "core",
  "update-index"
]
```

**arduino-index-proxy** — 2026-10-25T06:01:52.837932+00:00 to 2026-10-25T06:01:57.871893+00:00; exit 0; 5.034s. Log SHA256 `a00c3070ba1aff1e9861503059cf4576dbd17dfeadd151b764c3f97207754c8f` at `/tmp/otgd-firmware-verification/arduino-index-proxy.log`.

```json
[
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "core",
  "update-index"
]
```

**arduino-json-install** — 2026-10-25T06:02:06.584854+00:00 to 2026-10-25T06:02:07.308201+00:00; exit 0; 0.723s. Log SHA256 `3cb8ac79d0cf8410d298c10e56a8659e84e7a60a994eb7771f6d4600661afb33` at `/tmp/otgd-firmware-verification/arduino-json-install.log`.

```json
[
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "lib",
  "install",
  "ArduinoJson@7.4.2"
]
```

**arduino-core-install** — 2026-10-25T06:02:05.356147+00:00 to 2026-10-25T06:02:18.429821+00:00; exit 0; 13.074s. Log SHA256 `0ff6a88bdd78502df159802e8028e00f9aa73d596ab42fd1bb03a6b6e9403d71` at `/tmp/otgd-firmware-verification/arduino-core-install.log`.

```json
[
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "core",
  "install",
  "arduino:esp32@2.0.18-arduino.5"
]
```

**pyserial-install** — 2026-10-25T06:02:18.696544+00:00 to 2026-10-25T06:02:18.982715+00:00; exit 0; 0.286s. Log SHA256 `d4a7ec097b73a5802e6d17600a6ee2f4414bf71d58e5f961c75effd39b948863` at `/tmp/otgd-firmware-verification/pyserial-install.log`.

```json
[
  "/tmp/otgd-firmware-verification/python/bin/pip",
  "install",
  "--no-index",
  "--find-links",
  "/tmp/otgd-firmware-verification/wheels",
  "pyserial==3.5"
]
```

**arduinojson-host** — 2026-10-25T06:02:19.010819+00:00 to 2026-10-25T06:02:22.879167+00:00; exit 0; 3.868s. Log SHA256 `3665b4df03281df20275eea945377d58f04900bd52c54f04cf0335676d4777db` at `/tmp/otgd-firmware-verification/arduinojson-host.log`.

```json
[
  "bash",
  "-euo",
  "pipefail",
  "-c",
  "g++ -std=c++17 -Wall -Wextra -Werror -I firmware/tests/sparkfun_fake -I/tmp/otgd-firmware-verification/arduino-user/libraries/ArduinoJson/src firmware/tests/sparkfun_ppg_test.cpp firmware/nano_esp32_signed_reader/SparkFunBioSensor.cpp firmware/nano_esp32_signed_reader/RyuDouble.cpp -o /tmp/otgd-firmware-verification/otgd-sparkfun-ppg-test\n/tmp/otgd-firmware-verification/otgd-sparkfun-ppg-test /tmp/otgd-firmware-verification/sparkfun-ppg-result-v1.json\ncmp /tmp/otgd-firmware-verification/sparkfun-ppg-result-v1.json firmware/tests/fixtures/sparkfun-ppg-result-v1.json\ng++ -std=c++17 -Wall -Wextra -Werror -I/tmp/otgd-firmware-verification/arduino-user/libraries/ArduinoJson/src firmware/tests/signed_reader_core_test.cpp firmware/nano_esp32_signed_reader/RyuDouble.cpp -o /tmp/otgd-firmware-verification/otgd-signed-reader-test\n/tmp/otgd-firmware-verification/otgd-signed-reader-test\ng++ -std=c++17 -Wall -Wextra -Werror -I/tmp/otgd-firmware-verification/arduino-user/libraries/ArduinoJson/src firmware/tests/signed_reader_grant_test.cpp firmware/nano_esp32_signed_reader/RyuDouble.cpp -lcrypto -o /tmp/otgd-firmware-verification/otgd-reader-grant-test\n/tmp/otgd-firmware-verification/otgd-reader-grant-test"
]
```

**nano-simulator-compile** — 2026-10-25T06:02:29.514654+00:00 to 2026-10-25T06:02:29.766770+00:00; exit 1; 0.252s. Log SHA256 `79fd885c3416defe333a7e9364b4a35f5de1b03cba08d83418edc5edf7d61dbb` at `/tmp/otgd-firmware-verification/nano-simulator-compile.log`.

```json
[
  "env",
  "PATH=/tmp/otgd-firmware-verification/python/bin:/usr/bin:/bin",
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "compile",
  "--fqbn",
  "arduino:esp32:nano_nora",
  "--warnings",
  "all",
  "--output-dir",
  "firmware/build/nano_esp32",
  "firmware/nano_esp32_ble_simulator"
]
```

**secure-python-download** — 2026-10-25T06:02:44.283647+00:00 to 2026-10-25T06:02:49.373624+00:00; exit 1; 5.090s. Log SHA256 `1a07668473a4a88d622ee9834e0516f884b1e419f1269ce2dd15bbb40bce5fc5` at `/tmp/otgd-firmware-verification/secure-python-download.log`.

```json
[
  "/tmp/otgd-firmware-verification/python/bin/pip",
  "download",
  "--require-hashes",
  "--only-binary=:all:",
  "-r",
  "firmware/secure_reader/requirements.lock",
  "--dest",
  "/tmp/otgd-firmware-verification/secure-wheels"
]
```

**nano-simulator-compile-cache** — 2026-10-25T06:02:35.804585+00:00 to 2026-10-25T06:02:55.946971+00:00; exit 0; 20.142s. Log SHA256 `552f970e78220b28e314a14badae1baa851f227e6ea701aa7fc5632f39288c14` at `/tmp/otgd-firmware-verification/nano-simulator-compile-cache.log`.

```json
[
  "env",
  "XDG_CACHE_HOME=/tmp/otgd-firmware-verification/cache",
  "PATH=/tmp/otgd-firmware-verification/python/bin:/usr/bin:/bin",
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "compile",
  "--fqbn",
  "arduino:esp32:nano_nora",
  "--warnings",
  "all",
  "--output-dir",
  "firmware/build/nano_esp32",
  "firmware/nano_esp32_ble_simulator"
]
```

**secure-python-download-sdist** — 2026-10-25T06:03:03.113468+00:00 to 2026-10-25T06:03:08.065953+00:00; exit 0; 4.952s. Log SHA256 `b64e65dc811d6e2d61488267b5df9ae48d8537e9952f1743ae497918941f7ab2` at `/tmp/otgd-firmware-verification/secure-python-download-sdist.log`.

```json
[
  "/tmp/otgd-firmware-verification/python/bin/pip",
  "download",
  "--require-hashes",
  "-r",
  "firmware/secure_reader/requirements.lock",
  "--dest",
  "/tmp/otgd-firmware-verification/secure-wheels"
]
```

**secure-python-install** — 2026-10-25T06:03:21.523236+00:00 to 2026-10-25T06:03:25.331484+00:00; exit 0; 3.808s. Log SHA256 `62cbce3266f326fef0c0e898e3868e761a1b4c888f2e0c31fa6038b21bbf8569` at `/tmp/otgd-firmware-verification/secure-python-install.log`.

```json
[
  "/tmp/otgd-firmware-secure-sdk/python/bin/pip",
  "install",
  "--no-index",
  "--find-links",
  "/tmp/otgd-firmware-verification/secure-wheels",
  "--require-hashes",
  "-r",
  "firmware/secure_reader/requirements.lock"
]
```

**signed-reader-compile** — 2026-10-25T06:03:20.923946+00:00 to 2026-10-25T06:03:40.217394+00:00; exit 1; 19.293s. Log SHA256 `621898401620fd34f3069cad63526e939fc1454c9e177dffdaea41ef55e0088a` at `/tmp/otgd-firmware-verification/signed-reader-compile.log`.

```json
[
  "env",
  "XDG_CACHE_HOME=/tmp/otgd-firmware-verification/cache",
  "PATH=/tmp/otgd-firmware-verification/python/bin:/usr/bin:/bin",
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "compile",
  "--fqbn",
  "arduino:esp32:nano_nora",
  "--warnings",
  "all",
  "--output-dir",
  "firmware/build/signed_reader",
  "firmware/nano_esp32_signed_reader"
]
```

**secure-toolchain-install** — 2026-10-25T06:03:46.350278+00:00 to 2026-10-25T06:03:51.624197+00:00; exit 0; 5.274s. Log SHA256 `e5bf93c7e96300d45807d45a86c786fbfee9f07569240f3075252de6aef9c681` at `/tmp/otgd-firmware-verification/secure-toolchain-install.log`.

```json
[
  "env",
  "IDF_PATH=/tmp/otgd-firmware-secure-sdk/esp-idf",
  "IDF_TOOLS_PATH=/tmp/otgd-firmware-secure-sdk/tools",
  "/tmp/otgd-firmware-secure-sdk/python/bin/python",
  "/tmp/otgd-firmware-secure-sdk/esp-idf/tools/idf_tools.py",
  "--non-interactive",
  "install",
  "xtensa-esp32s3-elf",
  "cmake",
  "ninja"
]
```

**signed-reader-compile-tmp** — 2026-10-25T06:03:52.757756+00:00 to 2026-10-25T06:03:57.259439+00:00; exit 0; 4.502s. Log SHA256 `6d97a4850fd40704b86dd066581228c619921f2996a8bb6debfcb2919a1eb9ea` at `/tmp/otgd-firmware-verification/signed-reader-compile-tmp.log`.

```json
[
  "env",
  "XDG_CACHE_HOME=/tmp/otgd-firmware-verification/cache",
  "PATH=/tmp/otgd-firmware-verification/python/bin:/usr/bin:/bin",
  "/tmp/otgd-firmware-verification/cli/arduino-cli",
  "--config-file",
  "/tmp/otgd-firmware-verification/arduino-cli.yaml",
  "compile",
  "--fqbn",
  "arduino:esp32:nano_nora",
  "--warnings",
  "all",
  "--output-dir",
  "/tmp/otgd-firmware-verification/build/signed_reader",
  "firmware/nano_esp32_signed_reader"
]
```

**secure-prepare** — 2026-10-25T06:02:00.422734+00:00 to 2026-10-25T06:04:34.330272+00:00; exit 0; 153.908s. Log SHA256 `108b4b75a0ea5b66b4283eb516be465963f68f3c18553ed56a3f55e2a268f8ac` at `/tmp/otgd-firmware-verification/secure-prepare.log`.

```json
[
  "python3",
  "firmware/tools/secure_reader_build.py",
  "prepare",
  "--cache",
  "/tmp/otgd-firmware-secure-sdk"
]
```

**protected-reader-build** — 2026-10-25T06:09:17.719761+00:00 to 2026-10-25T06:10:08.377773+00:00; exit 0; 50.658s. Log SHA256 `4e1c304e408015e9a3fba9bf42ca57b0f7218c787e1c7624b26fddb379ecb2a1` at `/tmp/otgd-firmware-verification/protected-reader-build.log`.

```json
[
  "bash",
  "-euo",
  "pipefail",
  "-c",
  "export IDF_PATH=/tmp/otgd-firmware-secure-sdk/esp-idf\nexport IDF_TOOLS_PATH=/tmp/otgd-firmware-secure-sdk/tools\nexport PATH=/tmp/otgd-firmware-secure-sdk/python/bin:$IDF_TOOLS_PATH/tools/xtensa-esp32s3-elf/esp-2021r2-patch5-8.4.0/xtensa-esp32s3-elf/bin:$IDF_TOOLS_PATH/tools/cmake/3.23.1/bin:$IDF_TOOLS_PATH/tools/ninja/1.10.2:$PATH\notgd_ci_key=/tmp/otgd-firmware-verification/fictional-secure-boot.pem\ntrap 'rm -f \"$otgd_ci_key\"' EXIT\numask 077\nopenssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out \"$otgd_ci_key\" 2>/dev/null\n/tmp/otgd-firmware-secure-sdk/python/bin/python firmware/tools/secure_reader_build.py build --cache /tmp/otgd-firmware-secure-sdk --output /tmp/otgd-firmware-protected-build --boot-signing-key \"$otgd_ci_key\""
]
```

### Artifact hashes

| Artifact | Bytes | SHA256 |
|---|---:|---|
| `/workspace/One-The-Go-Detection/firmware/build/nano_esp32/nano_esp32_ble_simulator.ino.bin` | 956896 | `e4f979e8377db8d70ef6f8011c337ed0112b642d96336d8a6019fa443730a4a8` |
| `/workspace/One-The-Go-Detection/firmware/build/nano_esp32/nano_esp32_ble_simulator.ino.bootloader.bin` | 15104 | `2a71d69b471e20c2bac7fb469f3c6a807b3ebee780e348e5889db0da849ca363` |
| `/workspace/One-The-Go-Detection/firmware/build/nano_esp32/nano_esp32_ble_simulator.ino.elf` | 20891904 | `99dbd72e270e105c79c8d494dcaf9762946caf54e3a289e22388308d864d162a` |
| `/workspace/One-The-Go-Detection/firmware/build/nano_esp32/nano_esp32_ble_simulator.ino.map` | 18492410 | `e505124e8010278e8fcf0e9183517996bd4ca39f45c27a9c94f1aa502704f7f7` |
| `/workspace/One-The-Go-Detection/firmware/build/nano_esp32/nano_esp32_ble_simulator.ino.partitions.bin` | 3072 | `a8ed437803d579ea4db97d60e6b2eac9fc8a8ffadf6cfdcd2493130b17144e40` |
| `/tmp/otgd-firmware-verification/build/signed_reader/nano_esp32_signed_reader.ino.bin` | 1065120 | `f53c6551748bbd4f06ee39b12497dc161597ef1fbcf11fbe289ce95e7f5b05b0` |
| `/tmp/otgd-firmware-verification/build/signed_reader/nano_esp32_signed_reader.ino.bootloader.bin` | 15104 | `2a71d69b471e20c2bac7fb469f3c6a807b3ebee780e348e5889db0da849ca363` |
| `/tmp/otgd-firmware-verification/build/signed_reader/nano_esp32_signed_reader.ino.elf` | 23194044 | `dc5c9673f813c3eded867f09d15e6e30c4f6e472d9fd3b7616b57eda7303663c` |
| `/tmp/otgd-firmware-verification/build/signed_reader/nano_esp32_signed_reader.ino.map` | 19441692 | `64859537ab375eab3e7656caf8abe1d41c77ac33b10f3e552d31540de9cf90ef` |
| `/tmp/otgd-firmware-verification/build/signed_reader/nano_esp32_signed_reader.ino.partitions.bin` | 3072 | `a8ed437803d579ea4db97d60e6b2eac9fc8a8ffadf6cfdcd2493130b17144e40` |
| `/tmp/otgd-firmware-protected-build/otgd_secure_reader.bin` | 1183744 | `4fabb3ea5bffd5456437a6da753b15408b9294f0b054e01cd5d588c93d29b9a0` |
| `/tmp/otgd-firmware-protected-build/bootloader/bootloader.bin` | 45056 | `f9e4400a4f81ee429131ff9aacfbb54ebd736abf205c2f1cfabc2ebbd9bd3d4c` |
| `/tmp/otgd-firmware-protected-build/partition_table/partition-table.bin` | 3072 | `228505854a2e8fa3d1fe92c7d4d24fdb5d085ede08c0604a50f619f317e977d7` |

### Source manifest

All following 56 files matched the pre-check snapshot after all builds. The supplemental fictional HTTP fixture hash was recorded separately at 2026-10-25T06:09:56.664974+00:00.

| File | SHA256 |
|---|---|
| `.github/workflows/native-build.yml` | `174eff9eefce12f322cb00a0883ea653c1eaa422cf47e2e56488b685f0d26fcd` |
| `AGENTS.md` | `92a015f16480dae34990dca4a58f5d8085ce3ed651e40819f6b3260562d4bfd8` |
| `firmware/README.md` | `0e13d816b665c1fdc1694853393873a6939f41988b2d6ba07b4c3a1be6184fe1` |
| `firmware/nano_esp32_ble_simulator/ProtocolCore.h` | `fd09caab16af98ead2ba7f7aa53d86531c07deb148cb0a67d296f1ace3755dfe` |
| `firmware/nano_esp32_ble_simulator/nano_esp32_ble_simulator.ino` | `5ba257a0657dcdcc0cf82e52ad47b7a851879579c4cef9c0660d1f179d707f67` |
| `firmware/nano_esp32_signed_reader/AcquisitionDriver.h` | `711097ae1c39097ca890cd32cb5b26546a7023875122fcbb0e89060a59c56961` |
| `firmware/nano_esp32_signed_reader/AdcAcquisitionCore.h` | `4d2cb2d842cfe0e6872719b8cbcb4163988c145e5b32aa32dc575fe2b5d87901` |
| `firmware/nano_esp32_signed_reader/AdcAcquisitionDriver.h` | `1863434b7acaf25cf8796d36de47d883b8a0e115a492a01bd2e545fadb463005` |
| `firmware/nano_esp32_signed_reader/CanonicalJson.h` | `cdfd7ba0025174dbaed78d7e98329aa3437709e04f0d7241e2cbb56f224d2949` |
| `firmware/nano_esp32_signed_reader/ExactJson.h` | `a8cf883013158e51e22c1cd54519784c2fdca3e4d79d87d7d9be81591670a1d1` |
| `firmware/nano_esp32_signed_reader/ProtectedSigner.h` | `367ed5b894c371c16fcd101a8cba05b1f130bacdd81e904c71de79a7a9b335ad` |
| `firmware/nano_esp32_signed_reader/ProtocolCore.h` | `fd09caab16af98ead2ba7f7aa53d86531c07deb148cb0a67d296f1ace3755dfe` |
| `firmware/nano_esp32_signed_reader/README.md` | `3cbb559b160e58a58e409b298b02e434472b813f6470b208811481ea73c442ac` |
| `firmware/nano_esp32_signed_reader/ReaderLifecycle.h` | `d12a4e60177eccee75c9dc0d6bbe00ce0c88ab889ac060a6e3ee36645b27214e` |
| `firmware/nano_esp32_signed_reader/ReaderTime.h` | `fca40c349ec193c713d28b5c778a19951a4f34cd47537d1cba7a9b5592a611e0` |
| `firmware/nano_esp32_signed_reader/RyuDouble.cpp` | `9a924c52774e5e16ac3bc53b4cd7f6dc4522280706e4e88e372a1a9d65d82aa4` |
| `firmware/nano_esp32_signed_reader/SELECTED_PPG.md` | `a52503bfe9e238e05cce0bceb8d88cb60b2262db2113563bfe013f350d994d28` |
| `firmware/nano_esp32_signed_reader/ServerGrantCore.h` | `7270b813d9dd27d319158ce8c353ae928b4fd77d0ee429cfef27ab7e23b8ab58` |
| `firmware/nano_esp32_signed_reader/SparkFunBioSensor.cpp` | `03f1eee8b58e2aa08c99e36fb3a7a54b136d93bc83c88a50e99233fe99d9afb9` |
| `firmware/nano_esp32_signed_reader/SparkFunPpgCore.h` | `0d6a94f68999a03392c9a33e5c4c1da829e8cc735a35634709ebff0422458d85` |
| `firmware/nano_esp32_signed_reader/SparkFunPpgDriver.h` | `78c4bef5785667d40ee9c3bb52451fb5ab8fe5f33bff3f17b45f7fb70382da4e` |
| `firmware/nano_esp32_signed_reader/SparkFunPpgEvidence.h` | `bec7e46ee3df0365e45e4707ed70b65c561ae808c98cda7637ec71e30d4ed396` |
| `firmware/nano_esp32_signed_reader/nano_esp32_signed_reader.ino` | `e8d71cc23f5b6b8e93b5470daf838c4458652159bd429e70898e6bcbed6e79c6` |
| `firmware/nano_esp32_signed_reader/ryu/LICENSE-Apache2` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |
| `firmware/nano_esp32_signed_reader/ryu/LICENSE-Boost` | `c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566` |
| `firmware/nano_esp32_signed_reader/ryu/SOURCE.json` | `cb85706d52472304f12d3dc51aff166b9397ccf59865057ae97a461a8f9d95de` |
| `firmware/nano_esp32_signed_reader/ryu/common.h` | `0bbd71d26da6193e678d0776cf418f43f287c73d6fd6725353df0aadf70f2a19` |
| `firmware/nano_esp32_signed_reader/ryu/d2s.c` | `c6357b5d53ac1ba7f4984847d3a76f0803e0a931b7d0b02680656576829cf1d2` |
| `firmware/nano_esp32_signed_reader/ryu/d2s_full_table.h` | `2618f6e5fae6c4443899b184efe3d08295dd267dc9f1a994c983c7caca59ebe6` |
| `firmware/nano_esp32_signed_reader/ryu/d2s_intrinsics.h` | `01d9bdaada67b42f2d1bbdebb3765867e6c44e3a181b806c1d7e851b93f9cc21` |
| `firmware/nano_esp32_signed_reader/ryu/d2s_small_table.h` | `01f3d8a3ff739a26ecbddc2caae44c91574592b1de7c01fec67bc2d06672b606` |
| `firmware/nano_esp32_signed_reader/ryu/digit_table.h` | `8b782573abc0b8554d74163ae6c02f0beb5c30d1e63eaebdb0ddf2c98d817e01` |
| `firmware/nano_esp32_signed_reader/ryu/ryu.h` | `b7feab0ba1df5e9ef3d602f386592ad152491405e49b408fb21c0e0e9e6bfb16` |
| `firmware/nano_esp32_signed_reader/vendor/sparkfun/PATCHES.md` | `51e205e7639a89521a2951c0dcca66a48a79423ec7e42ff5aa5896adb3ea1591` |
| `firmware/nano_esp32_signed_reader/vendor/sparkfun/SOURCE.json` | `bc9a6e7d26a095aad4fbe44f70ee567baecc69512208839a60fecf793a7427ff` |
| `firmware/nano_esp32_signed_reader/vendor/sparkfun/SparkFun_Bio_Sensor_Hub_Library.cpp` | `d9c51c846617d1a6d1f0c0e29a9d2728200f54d1487a315bb39ea191f3162832` |
| `firmware/nano_esp32_signed_reader/vendor/sparkfun/SparkFun_Bio_Sensor_Hub_Library.h` | `fc0a2641fe2af5c062cc2d714f2547ad7fefa3ec279202ae6793984d9408a9aa` |
| `firmware/nano_esp32_signed_reader/vendor/sparkfun/UPSTREAM_README.md` | `40ddc45a6566a1a25c8b65a3536371fcc84f363a1057c47dc41976a7ec7446c3` |
| `firmware/nano_esp32_signed_reader/vendor/sparkfun/library.properties` | `9c829e10ae9c6f1ad46a7b3755f239e8c75300acb8711e1678f961fdd913e4a2` |
| `firmware/secure_reader/CMakeLists.txt` | `55a6da5dd9c96638afed3ed05c95e8b0f22729aba4e2ff70bc7ee55899a0ee9f` |
| `firmware/secure_reader/README.md` | `d2f60498eb5de83960196d62d70024951b993f290dcea5f517c3644da6cbd163` |
| `firmware/secure_reader/main/CMakeLists.txt` | `7cc583a6582d36ee899879816e0ff0f48a7a0fd04cb2c149f58a20dff6be94ac` |
| `firmware/secure_reader/main/reader.cpp` | `49922a626eae17c1ed76a303669923b51f7ac313fefcadb4e4dd222c6084cac2` |
| `firmware/secure_reader/partitions.csv` | `3e084616e3e2fe30bf7834ace4b9cba24ef67d9da5ca25e8a87f76166dd3ba0d` |
| `firmware/secure_reader/requirements.lock` | `26b65db2a61782e2d960a023fec5450bd027c0fa8af05a127165c0fb61a07446` |
| `firmware/secure_reader/sdkconfig.defaults` | `40ad2203811b04e501fab371040ff9ea1ee223643283a384ded01b2ccd13c97a` |
| `firmware/secure_reader/sources.json` | `517146e70b500ca46ffce9aa235f2332b1b80d2a379ec676de7639b5c068f498` |
| `firmware/tests/fixtures/sparkfun-ppg-result-v1.json` | `f889d5fab14484ab02812c98f9e44d32d71a597ad5faa888d3df4268fc63ba2a` |
| `firmware/tests/protocol_core_test.cpp` | `f9d29868cdde9121f5d8a6191d06df7fca14e5656316a6114bedbe21d4ab54bb` |
| `firmware/tests/signed_reader_acquisition_test.cpp` | `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a` |
| `firmware/tests/signed_reader_core_test.cpp` | `f00b6d2edc4b39911caf5418acb1c70d562a44600f8e158d9bb6cfa91753a386` |
| `firmware/tests/signed_reader_grant_test.cpp` | `f398cef88638601878d2182ed671be8624c14b3dcd9e5c4e1c23041e05d93b48` |
| `firmware/tests/sparkfun_fake/Arduino.h` | `74f0b9926a005dc69d08e63f92c9f4d05e28e0c0379d9efdce7339910a43b895` |
| `firmware/tests/sparkfun_fake/Wire.h` | `a86b8b51112e8b566ab44c1feeeda62e04c42d465edafbe528831f6f7b340dbe` |
| `firmware/tests/sparkfun_ppg_test.cpp` | `00121684618f2ea6a40bba22118a910c0cedef814d8e9f308c50f31a6cb9d78a` |
| `firmware/tools/secure_reader_build.py` | `efd8969e5d1bde21c5a779e398bf7945af2f905d6edcc6f77af5b3dee81136d1` |
| `apps/mobile/testfixtures/backend-reader-capture-authorization.json` (supplemental) | `d2da35e1737c8abcc2d75b72a753e70cf6f00ee0d2759228225098f1b6127791` |

### Supporting evidence hashes

| Evidence | SHA256 |
|---|---|
| `/tmp/otgd-firmware-verification/results.jsonl` | `18a6c823feddf1ad88e202773ec78fdbc7397a3042f519c46d9bb6d9264a7cd2` |
| `/tmp/otgd-firmware-verification/source-before.json` | `b13d8bbe70b09779e9f57ce119c822f78ab08be3ac97cd2cb776f8a1cf5f50c8` |
| `/tmp/otgd-firmware-verification/supplemental-source.json` | `49b572840c0f4e46078bb5bf6337d5494d83da6ba774cbbb47d6816e2a77c580` |
| `/tmp/otgd-firmware-verification/stock-build-manifest.json` | `9ab9fa9384c888e2c00a619456488ddae1892dba01610b3dc46e953ad968ae2b` |
| `/tmp/otgd-firmware-verification/secure-toolchain-checksums.json` | `265a5bb0b86b689433412d72f14f3e18d11a4c4bbc2f7ccc0de50b13abca2da6` |
| `/tmp/otgd-firmware-verification/python-download-inspection.json` | `e35e12876008bd760722293415beb634eedecf214bb0785ab1e88e9323a63cdd` |
| `/tmp/otgd-firmware-verification/final-evidence.json` | `e9d4e88789a6eccbf9946df90a4c9a8debc6c15aa9a611679dac8ce0733af923` |
| `/tmp/otgd-firmware-protected-build/build-manifest.json` | `1ff2fe31ce8fce409bfb694a8b525a3b531013e0c10abc751d75dc51d2f658e6` |

### Actual tool version receipt and SDK warnings

Final version check 2026-10-25T06:10:57.360696+00:00 to 2026-10-25T06:10:57.379543+00:00, exit 0; log `/tmp/otgd-firmware-verification/final-tool-versions.log`, SHA256 `b9be2f8d003bde5277efb2e5976e8d70e364d7fc03899088639813ebc0bbad5d`. Confirmed Arduino CLI 1.5.1 commit 01f3d4f2b, CMake 3.23.1, Ninja 1.10.2, Xtensa GCC esp-2021r2-patch5 8.4.0, Python 3.12.14.

```json
[
  "bash",
  "-euo",
  "pipefail",
  "-c",
  "/tmp/otgd-firmware-verification/cli/arduino-cli --config-file /tmp/otgd-firmware-verification/arduino-cli.yaml version\n/tmp/otgd-firmware-secure-sdk/tools/tools/cmake/3.23.1/bin/cmake --version\n/tmp/otgd-firmware-secure-sdk/tools/tools/ninja/1.10.2/ninja --version\n/tmp/otgd-firmware-secure-sdk/tools/tools/xtensa-esp32s3-elf/esp-2021r2-patch5-8.4.0/xtensa-esp32s3-elf/bin/xtensa-esp32s3-elf-gcc --version\n/tmp/otgd-firmware-secure-sdk/python/bin/python --version"
]
```

Protected build emitted upstream SDK warnings: Click MultiCommand deprecation; intentionally disabled component manager; certificate serial-number deprecation in the vendor certificate-bundle generator; I2S aggregate initializers; and WiFiClientSecure PSK configuration advice. The unchanged pinned SDK build completed successfully. Vendor SDK security/deprecation review remains a release prerequisite as documented in firmware/secure_reader/README.md; these logs do not establish that review.
