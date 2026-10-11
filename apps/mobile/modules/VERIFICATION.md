# Native implementation verification

This file separates source implementation, executed host checks, actual native build evidence and physical qualification. A test is marked executed only when that command was run and its output inspected. An artifact build does not establish a successful device interaction or physical timing calibration.

Evidence date: **2026-10-11**. Reviewed specification checkpoint: **47d8ecbfc871b5026f32d4f5f474908e9c0e1b14**. See [shared contracts](../../../openspec/changes/production-mobile-platform/shared-contracts.md) and the eight reaction-task / eight device requirements for the normative rules.

## Implemented source

| Area | Implementation |
|---|---|
| Native task | Kotlin Android View/Module/Core and Swift iOS View/Module/Core; native frame/input clocks, bounded raw evidence, exact scoring, lifecycle invalidation, cancellation receipt with frozen result |
| Native BLE | Android BluetoothGatt module and iOS CoreBluetooth module with bounded discovery/read/write/notify, contextual permissions and generation checks |
| Device semantics | TypeScript strict framing, replay, clock evidence, capture controller, software simulator and Devices UI |
| Board firmware | Arduino Nano ESP32 synthetic BLE peripheral and independent portable protocol/parser core |
| Storage helper | iOS directory backup exclusion with readback; Android backup-disabled verification and FLAG_SECURE window flag |
| CI | Android debug APK, iOS Release simulator app, Swift/Kotlin golden suites and actual Nano ESP32 board compile |

Native timing and physical channels stay uncalibrated/unqualified. There is no native JavaScript-timer fallback and no intoxication inference path in these modules.

## Executed local checks

| Check | Observed result | What it establishes |
|---|---|---|
| Scoped TypeScript compile | Passed `tsc --noEmit -p modules/tsconfig.native.json` | Reaction/device interfaces and implementation type consistency |
| Integrated mobile TypeScript and host suite | Passed `npm run typecheck`; 94 tests passed, zero failed | Integrated source contracts, pure auth/lifecycle/scope guards, profile/display, cardiac selection, generation/export refusal and protocol/controller tests; not full native UI execution |
| Device tests | Passed 14 Node/tsx tests | Byte framing, parsing, clocks, replay and real timed software simulator/controller behavior |
| Kotlin production core compile | Passed using Kotlin compiler 2.2.20 and JRE 17 | Actual `ReactionCore.kt` and its test source compile outside Android |
| Kotlin JUnit suite | Passed `OK (6 tests)` | All three literal 66-trial schedules/hashes, scoring fixtures, boundaries, quantiles, terminal latch/admission and bounded result size |
| C++ protocol compile/test | Passed with `g++ -std=c++17 -Wall -Wextra -Werror` | Portable firmware parser/framing behavior, including adversarial inputs |
| Actual Nano ESP32 sketch compile | Passed using Arduino CLI 1.5.1, `arduino:esp32@2.0.18-arduino.5`, ArduinoJson 7.4.2 and pyserial 3.5 | Board-target compilation and binary output; sketch 956,469 bytes, static globals 75,068 bytes; no flashing/radio test |
| Reviewed asset verification | Passed `node modules/scripts/verify-native-assets.mjs` | Exact fixture copies and canonical configuration/schedule hashes |
| Android Expo autolinking resolution | All three local modules resolved | Module discovery; this is not a native compile |
| Full synthetic captures | PPG, ECG, saliva completed with 10 retained messages each | Actual software simulator/controller transcript and canonical evidence generation |
| Backend independent contract checks | Root agent verified native and all three synthetic fixture projections/hashes; malformed native timing/count/input/geometry rejected | Cross-language DTO/evidence agreement for explicitly fictional fixtures |

The Kotlin test process used the production `ReactionCore.kt`, JUnit 4.13.2 and the literal fixture resources. It did **not** compile the Android View, Expo bridge, Bluetooth module or storage helper. No Android SDK or Xcode toolchain is installed in the local workspace.

### Reproduce checks

From `apps/mobile`:

```sh
npm ci
npm run typecheck
node --import tsx --test tests/*.test.ts src/device/tests/*.test.ts
node modules/scripts/verify-native-assets.mjs
```

The Node import form avoids the extra IPC server opened by the `tsx` command-line wrapper in restricted hosts.

On a machine with the generated Android project and SDK:

```sh
cd apps/mobile
node node_modules/expo/bin/cli prebuild --platform android --no-install
cd android
./gradlew --no-daemon --max-workers=2 \
  -PreactNativeDevServerPort=8082 \
  -PreactNativeArchitectures=arm64-v8a,x86_64 \
  :otgd-reaction-task:testDebugUnitTest :app:assembleDebug
```

On the reviewed Mac toolchain:

```sh
swift test --package-path apps/mobile/modules/reaction-task
cd apps/mobile
node node_modules/expo/bin/cli prebuild --platform ios --no-install
pod install --project-directory=ios
python3 modules/scripts/build_ios.py
```

The portable firmware test and pinned board compilation commands are in [firmware/README.md](../../../firmware/README.md).

## CI and artifact boundaries

[native-build.yml](../../../.github/workflows/native-build.yml) pins official action commit SHAs, Node 24.19.0, JDK 17, Arduino CLI 1.5.1 and the reviewed board/library versions. The CLI download has a verified release SHA-256. The iOS runner uses `macos-26` and `/Applications/Xcode_26.4.1.app/Contents/Developer`, as recorded by the official [runner inventory](https://github.com/actions/runner-images/blob/main/images/macos/macos-26-Readme.md).

| Artifact/job | Required evidence | Boundary |
|---|---|---|
| `android-debug-apk` | Native Gradle compile, Kotlin unit tests, actual APK file | Development APK uses Metro; no Play signing or device calibration |
| `ios-simulator-app` | Swift unit tests, CocoaPods/Xcode app build, embedded main.jsbundle, zipped `.app` | Simulator architecture; no iPhone signing, provisioning or TestFlight upload |
| `nano-esp32-synthetic-firmware` | Actual compile for `arduino:esp32:nano_nora` | No flashing, radio test or sensing qualification |

At the time of this local evidence record, the GitHub workflow has been authored but a completed workflow run has **not yet been observed**. Do not describe the native application binaries as built until the relevant job succeeds and its artifacts are present. Record actual run links and failures in the delivery report; never substitute a generated success file for a build.

### Connect the local artifacts to the development stack

CI builds the `local` environment, using `otgd-local://oauth/callback` and public client `otgd-local-mobile`. Start the local API, OAuth stub and LocalStack using the repository's deployment instructions. These addresses are deliberately development-only; QA/prod use separately configured HTTPS origins and a real identity provider.

| Runtime | API | OAuth issuer | JavaScript |
|---|---|---|---|
| Standard Android emulator | `http://10.0.2.2:8000` | `http://10.0.2.2:8081` | Metro on host port 8082 |
| iOS simulator on the host Mac | `http://localhost:8000` | `http://localhost:8081` | Embedded Release bundle |

The Android development APK is built for Metro port **8082** because port 8081 is reserved by the local OAuth stub. Start Metro from `apps/mobile` with the same environment used to compile that artifact:

```sh
APP_ENV=local \
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000 \
EXPO_PUBLIC_OAUTH_ISSUER=http://10.0.2.2:8081 \
EXPO_PUBLIC_OAUTH_CLIENT_ID=otgd-local-mobile \
node node_modules/expo/bin/cli start --port 8082
```

Install the debug APK with `adb install -r <downloaded.apk>` and open the app in the emulator. On the Mac, unzip the simulator artifact and install it with `xcrun simctl install booted <extracted.app>`; launch its local bundle identifier `dev.r3fresh.otgd.local`. The iOS Release simulator artifact does not need Metro.

An emulator's loopback address is different from the host. `10.0.2.2` is the standard Android emulator's host alias; other emulators may differ. A physical phone cannot use the same host-loopback assumptions: set reachable origins and rebuild the local application, or use the repository's configured QA environment. A simulator build cannot be installed on a physical iPhone. The local OAuth stub and synthetic devices are development services, not production identity or sensing qualification.

## Requirement mapping and remaining evidence

| Requirements | Source coverage | Executed evidence | Still required |
|---|---|---|---|
| AND-TASK-001, 007 | Typed view API, native start/cancel/terminal receipt, full result, workspace/run IDs | TS compile; pure terminal latch tests; independent DTO checks | Full app/native lifecycle and durable event/receipt dedup on devices |
| AND-TASK-002 | Identical Kotlin/Swift LCG, shuffle, gap indexing, frozen configuration | Kotlin literal schedules and asset hashes | Swift suite and full app build |
| AND-TASK-003 | Choreographer/CADisplayLink, native input/dispatch clocks and provenance | Core budget cases and DTO validation | Physical timing bench and per-device latency characterization; no calibration claimed |
| AND-TASK-004, 005 | Bounded touch ledger, deterministic first response, quantiles/missingness | Kotlin literal scoring/boundary tests, payload bound | Native multitouch injection and runtime trace comparisons |
| AND-TASK-006 | Native background/focus/call/detach/layout invalidation and immutable terminal latch | Core terminal race/admission tests | Android/iOS interruption instrumentation including pre-layout cancel and delayed JS |
| AND-TASK-008 | Shared config/goldens, fixed presentation profile, explicit unsupported input mode | Config hash and Kotlin suite | Swift suite, screenshots, screen-reader and device-layout verification |
| AND-DEV-001, 002 | Devices UI and native contextual permission/radio transitions | TS tests and autolinking | Physical permission-denial, revocation, radio-off and Settings recovery tests |
| AND-SET-003, 007 | No-prompt OS permission queries; static iOS Bluetooth/camera authorization, explicit restricted/unknown state, Android check-only permission access | TypeScript check; Apple API signature inspection | Full native compile and OS authorization/restriction/device-policy behavior |
| AND-DEV-003, 004 | Simulator-only association, exact fixture gate, boot binding, three clock exchanges | Synthetic controller capture and spoofed-source/replay tests | Real board handshake, reconnect/reboot and clock traces |
| AND-DEV-005, 006 | Bounded framing/CRC, duplicate/conflict checks, deadlines, command identity, replay journal | TS and C++ adversarial protocol suites; actual Nano ESP32 target compile | Board flashing/run and over-the-air loss/retry/overflow tests |
| AND-DEV-007, 008 | Generation-scoped disconnect, local cancellation, forget and native lifecycle shutdown | Software cancellation test | Android/iOS BLE background and stale-callback instrumentation |
| AND-CHECK-003, 005, 006 | Capture context interface, terminal result receipt, immediate device invalidation | Interface checks; app owner covers ledger/storage tests | Full navigation/capture/background persistence integration on both platforms |
| AND-HR, AND-ECG, AND-SAL | Exact synthetic fixture adapters with transport evidence | Timed software captures and independent backend hash/projection validation | Human protocol, hardware/assay qualification and verified device trust remain external prerequisites |
| AND-EYE | No optical stimulus command exists in this firmware/adapter; app owns passive preview and gate UI | Source scope reviewed | Approved optical configuration and physical safety/performance evidence before human stimulus work |
| Storage/privacy contracts | iOS excluded-from-backup readback and Android backup-disabled/FLAG_SECURE helper | Autolinking and interface compile | OS backup/restore and screen-capture bench verification; iOS does not claim a screenshot-prevention API |

## Physical bench acceptance record to collect

For each Android/iOS device, record model, OS, app/native build, task configuration hash, test operator/date and observed results. Exercise Back before layout, End during response, simultaneous touches including End, final-cutoff arrivals, rotation, app switch, incoming call, screen lock, touch exploration, delayed bridge delivery, input overflow, and a render stall. Inspect exactly one terminal result per run and preserve raw timing evidence. Quantify display onset with external optical instrumentation and touch latency with a controlled fixture before any calibrated-performance claim.

For BLE, record the board firmware/core version and boot ID. Exercise scan denial, radio loss, reconnect with the same boot, board reboot, duplicate/conflicting fragments and message IDs, CRC failure, slow notification/ack retry, timeout, queue/journal exhaustion and cancellation. Verify the app never promotes the board above unverified simulator status and never accepts changed fictional values. A software transcript cannot replace these observations.

All host fixtures, simulator captures and generated test values are engineering evidence only. Human assay validity, electrical/optical qualification and clinical impairment-model validation are separate external dependencies.
