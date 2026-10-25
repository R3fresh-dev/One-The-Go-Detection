# First-round Swift optical and vendor FIFO assertion correction

Actual author: OpenAI gpt-6.1-sol/high `/root/firmware_validation`, run `otgd-20261025-0555`. D009v7 AFFECTED ACK sent before dependent work; read-only inspection preceded PM checkpoint9 `52ffa1044e787f7fea088c82797d4525af02e9a3`, and repository writes began only after PM released that hold. Still correction **1/2**, recovery **0/3**. No self-signoff, final acceptance or physical qualification is implied.

Only the two assigned test sources changed. Existing test bodies/assertions and original fixtures were retained exactly, verified by removing only the new test additions and comparing retained before copies. No production code, timing thresholds, configuration, API tests, COPY golden fixtures, protected settings or gate edits. No Docker/image/service action, install, cleanup, Git operation, firmware flash/provision/eFuse or participant use. F and all earlier image archives remain preserved and unadopted by this worker.

## Observed gaps and new assertions

Read the verification-native/store/native-gap-handoff.md/json and immutable168-case report before edits. Existing Swift `testConfigurationFailClosedAndRawLittleEndian` checked magic/header/size, while Kotlin already checked whole raw SHA. Existing vendor executable checked73→75 valid data, independent poor contact and separate zero-observation stale cases. Those bodies did not prove the assigned exact conjunctions. No test failure or production defect was inferred from the missing assertions; no production repair was needed or assigned.

| Existing acceptance clause | Current source assertion mapping | Actual result and scope |
|---|---|---|
| OTGD-012 AND-EYE-103 OPTICAL-006 complete codec parity | EyeCoreTests.swift:54, new61–67 in `testConfigurationFailClosedAndRawLittleEndian`: full560-byte equality to independently literal header/Float64LE1000/1100/UInt32LE0/1 plus both original256-byte luminance planes; CryptoKitSHA256 equals original checked-in raw_sha256 | Authored, **NOT_RUN Swift**. Independent Python literal packing agrees with original560-byte hash; this is not Swift compiler/execution evidence. |
| OTGD-043 VPPG-002-03 two genuine fresh identical records | sparkfun_ppg_test.cpp:32, identical34–46: actual pinnedSDK mode1 and2, FIFO count2, two separately successful readSensorBpm calls returning73/95/status3, consumed replies, observed2/valid2/invalid0, final73, hostsequence1 and actualsecondreceive2010002; explicit unqualified-host timestamp label and unknown actualcadence/drop counts | Actual host compile/execution **PASS** in both modes. No vendor sample timing or identity manufactured. |
| OTGD-043 VPPG-002-01 one mixed valid/poor-contact stream | samefunction48–57: actualFIFO3, two valid73 then poor-contact120/status2, observed3=valid2+invalid1, retained truthful rejected last observation120, completion invalid/null heart rate | Actual host **PASS** in both modes. MinimumValid2 is already reached, so contact invalidation is tested independently of insufficient count. |
| OTGD-043 VPPG-002-02 prior valid followed by empty FIFO | samefunction59–63: prior successful SDKread, actualemptyFIFO0, no read/observe substituted, count remains1/valid1/invalid0, originalsequence/timestamp intact, emptycount1; insufficient final heart rate null | Actual host **PASS** in both modes. Empty polling alone is not redefined as invalid if other approved evidence suffices. |
| Same clause, stale interval after qualifying fresh data | samefunction64–71: second separately successful fresh read reaches minimum2, next empty FIFO does not increment count; exactly1000ms since lastreceive is not stale, +1microsecond is stale; count stays2, originallastreceive retained, completion null | Actual host **PASS** in both modes. Existing maxNoData1000ms and strictgreaterthan stale boundary unchanged. |
| Same clause, truncated SDK response after qualifying data | samefunction73–80: two successful currentreads reach valid2, actual short I2Creply returns ERR_UNKNOWN and allzero transient vendor fields; no failed observation admitted, count remains2/valid2/invalid0, ioError true, final invalid/null heart rate and priorsequence1 retained only as old evidence | Actual host **PASS** in both modes. Failure cannot become a fabricated new0bpm or fill the missing interval with73. |

The vendor branches execute within **one** assert-based host executable; these are five scenario branches × two modes, not ten separately named JUnit tests. New helper `sampling` only arranges public core stages; `received` maps actual SDK fields. Tests exercise the real vendored SDK against explicit fake I2C bytes, the production-used SparkFunCapture and actual sparkFunResult factory. They do **not** instantiate the entire hardware/GPIO/BLE `SparkFunPpgDriver`; automatic adapter shutdown/origin/backpressure integration remains a separate evidence gap. No claims are made about physical FIFO freshness, sensor onset, contact/calibration or genuine hardware behavior.

The full literal Swift expected stream is assembled from hand-written public wire bytes, not a call to the production codec or shared integer/Double serializer. Header/dimension/count, both Float64 timestamps, both sequences, every luminance byte and total order are covered by complete Data equality plus fixture hash `1f475a4186591458a25bac00a9bf37b6c9a6e482ebe9c946ee41186999c49f59`. Independent Python reconstruction read the exact new literal arrays and original gray fixture:560bytes and that SHA agree. CryptoKit import is test-only; this package already targets macOS13/iOS16.4 and production camera uses CryptoKit. Its availability/type checking still requires actual current Swift CI.

## Executed evidence

Host g++14.2.0, `-std=c++17 -Wall -Wextra -Werror`, noNDEBUG. Reused installed pinned ArduinoJson7.4.2; exact SDK1.1commit91575258e5e2c47f0f4b8ec97b651381671f4637. No downloads/installs. Evidence below records exact argv, start/endUTC, exitcode and retained raw log. Initial host version already passed; it was strengthened to reach minimumValid2 before contact/stale/I/O failures and then rebuilt/reexecuted on final released source. These are assertion additions, not a hidden failed production repair.

| Check | Start UTC | End UTC | Exit | Log |
|---|---|---|---:|---|
| compile-sparkfun | 2026-10-25T09:01:32.596847+00:00 | 2026-10-25T09:01:34.331738+00:00 | 0 | `/tmp/otgd-native-optical-fifo/compile-sparkfun.log` |
| execute-sparkfun | 2026-10-25T09:01:55.374998+00:00 | 2026-10-25T09:01:55.378519+00:00 | 0 | `/tmp/otgd-native-optical-fifo/execute-sparkfun.log` |
| compare-fixture | 2026-10-25T09:01:55.413006+00:00 | 2026-10-25T09:01:55.414475+00:00 | 0 | `/tmp/otgd-native-optical-fifo/compare-fixture.log` |
| verify-native-assets | 2026-10-25T09:01:55.449057+00:00 | 2026-10-25T09:01:55.504517+00:00 | 0 | `/tmp/otgd-native-optical-fifo/verify-native-assets.log` |
| compile-sparkfun-final | 2026-10-25T09:02:33.580237+00:00 | 2026-10-25T09:02:35.183059+00:00 | 0 | `/tmp/otgd-native-optical-fifo/compile-sparkfun-final.log` |
| compile-protocol | 2026-10-25T09:02:52.739848+00:00 | 2026-10-25T09:02:53.249297+00:00 | 0 | `/tmp/otgd-native-optical-fifo/compile-protocol.log` |
| compile-acquisition | 2026-10-25T09:02:52.749001+00:00 | 2026-10-25T09:02:53.826679+00:00 | 0 | `/tmp/otgd-native-optical-fifo/compile-acquisition.log` |
| execute-sparkfun-final | 2026-10-25T09:02:53.974715+00:00 | 2026-10-25T09:02:53.977673+00:00 | 0 | `/tmp/otgd-native-optical-fifo/execute-sparkfun-final.log` |
| compare-fixture-final | 2026-10-25T09:02:54.002199+00:00 | 2026-10-25T09:02:54.003375+00:00 | 0 | `/tmp/otgd-native-optical-fifo/compare-fixture-final.log` |
| execute-protocol | 2026-10-25T09:03:01.827453+00:00 | 2026-10-25T09:03:01.829370+00:00 | 0 | `/tmp/otgd-native-optical-fifo/execute-protocol.log` |
| execute-acquisition | 2026-10-25T09:03:01.853858+00:00 | 2026-10-25T09:03:01.856995+00:00 | 0 | `/tmp/otgd-native-optical-fifo/execute-acquisition.log` |

Exact executed commands (argv serialized to avoid shell ambiguity):

```json
[
  {
    "label": "compile-sparkfun",
    "argv": [
      "g++",
      "-std=c++17",
      "-Wall",
      "-Wextra",
      "-Werror",
      "-I",
      "firmware/tests/sparkfun_fake",
      "-I",
      "/tmp/otgd-firmware-verification/arduino-user/libraries/ArduinoJson/src",
      "firmware/tests/sparkfun_ppg_test.cpp",
      "firmware/nano_esp32_signed_reader/SparkFunBioSensor.cpp",
      "firmware/nano_esp32_signed_reader/RyuDouble.cpp",
      "-o",
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-test"
    ]
  },
  {
    "label": "execute-sparkfun",
    "argv": [
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-test",
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-result-v1.json"
    ]
  },
  {
    "label": "compare-fixture",
    "argv": [
      "cmp",
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-result-v1.json",
      "firmware/tests/fixtures/sparkfun-ppg-result-v1.json"
    ]
  },
  {
    "label": "verify-native-assets",
    "argv": [
      "node",
      "apps/mobile/modules/scripts/verify-native-assets.mjs"
    ]
  },
  {
    "label": "compile-sparkfun-final",
    "argv": [
      "g++",
      "-std=c++17",
      "-Wall",
      "-Wextra",
      "-Werror",
      "-I",
      "firmware/tests/sparkfun_fake",
      "-I",
      "/tmp/otgd-firmware-verification/arduino-user/libraries/ArduinoJson/src",
      "firmware/tests/sparkfun_ppg_test.cpp",
      "firmware/nano_esp32_signed_reader/SparkFunBioSensor.cpp",
      "firmware/nano_esp32_signed_reader/RyuDouble.cpp",
      "-o",
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-test-final"
    ]
  },
  {
    "label": "compile-protocol",
    "argv": [
      "g++",
      "-std=c++17",
      "-Wall",
      "-Wextra",
      "-Werror",
      "firmware/tests/protocol_core_test.cpp",
      "-o",
      "/tmp/otgd-native-optical-fifo/protocol-test"
    ]
  },
  {
    "label": "compile-acquisition",
    "argv": [
      "g++",
      "-std=c++17",
      "-Wall",
      "-Wextra",
      "-Werror",
      "-pthread",
      "firmware/tests/signed_reader_acquisition_test.cpp",
      "-o",
      "/tmp/otgd-native-optical-fifo/acquisition-test"
    ]
  },
  {
    "label": "execute-sparkfun-final",
    "argv": [
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-test-final",
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-result-final.json"
    ]
  },
  {
    "label": "compare-fixture-final",
    "argv": [
      "cmp",
      "/tmp/otgd-native-optical-fifo/sparkfun-ppg-result-final.json",
      "firmware/tests/fixtures/sparkfun-ppg-result-v1.json"
    ]
  },
  {
    "label": "execute-protocol",
    "argv": [
      "/tmp/otgd-native-optical-fifo/protocol-test"
    ]
  },
  {
    "label": "execute-acquisition",
    "argv": [
      "/tmp/otgd-native-optical-fifo/acquisition-test"
    ]
  }
]
```

Final SparkFun build/execution and exact original fixture comparison all exit0. Portable protocol and signed-reader acquisition regressions compiled/executed exit0. Native asset verification exit0 and preserves reviewed configuration plus three schedule hashes. No broad rerun of unchanged firmware targets was attempted; production firmware is unchanged, but required exact-revision CI stock/protected build jobs still must run before any overall acceptance.

`swift` and `xcodebuild` resolve to null locally; no Swift execution/compilation occurred and no install was authorized or attempted. This is **BLOCKED on local tool availability / NOT_RUN**, not a denied action or an uncertain command. Current CI must run the changed Swift source; old candidate28 native XML cannot close it. The prescribed macOS command is:

```sh
set -euo pipefail
mkdir -p reports
swift test --package-path apps/mobile/modules/eye-capture --parallel --num-workers 1 --verbose --disable-swift-testing --xunit-output "$PWD/reports/ios-optical.xml" 2>&1 | tee reports/ios-optical.log
python3 scripts/verify-swift-xctest.py reports/ios-optical.xml reports/ios-optical.log
python3 scripts/ci_gate.py verify-junit reports/ios-optical.xml
```

These are the current native-build.yml optical commands; current-source result binding is mandatory. Existing earlier native TASK00418-vector changes also still require their own current Kotlin/Swift CI evidence.

No denied action occurred. Read-only path discovery initially tried incorrect speculative spec/header paths; rg located canonical sources without source mutation. Every actual compile/test above completed successfully. Hardware qualification, genuine device reference, scientific/clinical validation, anatomical specificity, nativeOS lifecycle, secure storage, physical BLE pairing/protectedboot, participant authorization and fitness-to-drive claims remain outside these software checks. Measurement defaults/provenance/research eligibility and future calibrated fuel-cell breath alcohol mg/L scope unchanged.

## Source manifest

Released sources; all other scoped inspected production/fixtures unchanged:

| Path | SHA-256 | Changed |
|---|---|---|
| `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift` | `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552` | yes, tests only |
| `firmware/tests/sparkfun_ppg_test.cpp` | `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb` | yes, tests only |
| `apps/mobile/modules/eye-capture/fixtures/eye-golden-v1.json` | `a004817f11370115f904def07cd8113bb459dbda70da9b5d3ee36fe412d9d740` | no |
| `apps/mobile/modules/eye-capture/ios/EyeCore.swift` | `9e496ba028f497796e204c0fa3ba961eef2d8a5d941c5966e3a8bacbf3aaf1e8` | no |
| `firmware/nano_esp32_signed_reader/SparkFunPpgCore.h` | `0d6a94f68999a03392c9a33e5c4c1da829e8cc735a35634709ebff0422458d85` | no |
| `firmware/nano_esp32_signed_reader/SparkFunPpgEvidence.h` | `bec7e46ee3df0365e45e4707ed70b65c561ae808c98cda7637ec71e30d4ed396` | no |
| `firmware/nano_esp32_signed_reader/SparkFunPpgDriver.h` | `78c4bef5785667d40ee9c3bb52451fb5ab8fe5f33bff3f17b45f7fb70382da4e` | no |
| `firmware/nano_esp32_signed_reader/vendor/sparkfun/SparkFun_Bio_Sensor_Hub_Library.cpp` | `d9c51c846617d1a6d1f0c0e29a9d2728200f54d1487a315bb39ea191f3162832` | no |
| `firmware/tests/fixtures/sparkfun-ppg-result-v1.json` | `f889d5fab14484ab02812c98f9e44d32d71a597ad5faa888d3df4268fc63ba2a` | no |

## Retained evidence hashes

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `/tmp/otgd-native-optical-fifo/compare-fixture-final.log` | 174 | `a9cc48e6ad75219a436d1cc930f5f07e1558ee64de04e87c97c769b9590877f0` |
| `/tmp/otgd-native-optical-fifo/compare-fixture.log` | 171 | `2a545383f9bc27fbd815552cea109efe060799ace02c6d29d1fbb893467c2659` |
| `/tmp/otgd-native-optical-fifo/compile-acquisition.log` | 221 | `b8e89d468da71e4937bf5fa6d3ca51b04f0dbd303428d2ed7dd01dfe9778be8a` |
| `/tmp/otgd-native-optical-fifo/compile-protocol.log` | 194 | `6d6fce984f5b9c05bff4d85f989b121842ce46b87d7d5c6c2049a419366c3b7f` |
| `/tmp/otgd-native-optical-fifo/compile-sparkfun-final.log` | 431 | `eb666ece6a27b24195f7616c6720db0dad795dccb4ede81720e885a8b4ebc461` |
| `/tmp/otgd-native-optical-fifo/compile-sparkfun.log` | 425 | `cafd3279285786e7e5df89d99d764a0e778e5e3d6da4e1099e269222d8ecbd73` |
| `/tmp/otgd-native-optical-fifo/execute-acquisition.log` | 244 | `074e2afc1f01213fc096bc96d2095b9ae0db6eba2e4cf32d0a98858adec46b1f` |
| `/tmp/otgd-native-optical-fifo/execute-protocol.log` | 200 | `9b2a854b69436de59e88d81fdad773bb8035fa94df1b6e7831fdae6d4b41849b` |
| `/tmp/otgd-native-optical-fifo/execute-sparkfun-final.log` | 304 | `a8bdf480284164c9d34e30bb442bb8abe4905d13b4e70461816fc94c35501eab` |
| `/tmp/otgd-native-optical-fifo/execute-sparkfun.log` | 295 | `1c9c352d9608f9f8a66e3b55eeafd2a8b092a83800f60254954b9e03ef5618ee` |
| `/tmp/otgd-native-optical-fifo/verify-native-assets.log` | 346 | `35c2c36a4ab25c3b80c638e8ff1f960f934799b0ea416373fa8521c33e568636` |
| `/tmp/otgd-native-optical-fifo/preservation.json` | 255 | `6417072d782655e16b6076da9ff3fab6df191f997ae22c4700a9ecdf7edbf712` |
| `/tmp/otgd-native-optical-fifo/source-before.json` | 1251 | `ad6749325b9cf7256db87e756638736010ed19b52d408abd1a607cdb0f89f2ba` |
| `/tmp/otgd-native-optical-fifo/source-release.json` | 1437 | `87d243430c56712f9d1bdbecf3a9c04f4689dd454aa88edbece071eacfea1917` |
| `/tmp/otgd-native-optical-fifo/sparkfun-ppg-result-final.json` | 1219 | `f889d5fab14484ab02812c98f9e44d32d71a597ad5faa888d3df4268fc63ba2a` |
| `/tmp/otgd-native-optical-fifo/sparkfun-ppg-result-v1.json` | 1219 | `f889d5fab14484ab02812c98f9e44d32d71a597ad5faa888d3df4268fc63ba2a` |
| `/tmp/otgd-native-optical-fifo/swift-literal-check.json` | 331 | `d2beeaece50385afe5f3caca27f9c1920b1a838d9e77a3a90a6e8e90376c8c47` |
| `/tmp/otgd-native-optical-fifo/results.jsonl` | 4420 | `00e2be31e0873465b143613bfa9aa10d4e85668ebbc640b6d3459b25317dd642` |
| `/tmp/otgd-native-optical-fifo/run.py` | 715 | `d7bb3d18b47fe205a4dabc862d81ed479ed5ea5000912ba96573fbcb593a62dc` |
| `/tmp/otgd-native-optical-fifo/sparkfun-ppg-test-final` | 417048 | `4dc2eb9296c34a7ee64b1b32c1a209cdc5b9edbb59cd8f7e100e6a4d56e753bb` |
| `/tmp/otgd-native-optical-fifo/protocol-test` | 80096 | `bd3a3ef2ee07a6364dc9b24b4cab377f028ade81858dee4179696366be0dd763` |
| `/tmp/otgd-native-optical-fifo/acquisition-test` | 274744 | `8fd9bc91cfb4e2df835b5bca04d5e85e00482d9449032f35a22e80ba6c0ee736` |

This report is evidence for PM/verifier reconciliation, not an independent scenario signoff. Current full gates and six independent replacement reviews remain required.
