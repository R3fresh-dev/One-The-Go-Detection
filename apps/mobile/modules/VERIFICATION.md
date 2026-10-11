# Native implementation verification

This file separates source implementation, executed host checks, actual native build evidence and physical qualification. A test is marked executed only when that command was run and its output inspected. An artifact build does not establish a successful device interaction or physical timing calibration.

Evidence date: **2026-10-11**. Reviewed specification checkpoint: **47d8ecbfc871b5026f32d4f5f474908e9c0e1b14**. See [shared contracts](../../../openspec/changes/production-mobile-platform/shared-contracts.md) and the eight reaction-task / eight device requirements for the normative rules.

## Implemented source

| Area | Implementation |
|---|---|
| Native task | Kotlin Android View/Module/Core and Swift iOS View/Module/Core; native frame/input clocks, bounded raw evidence, exact scoring, lifecycle invalidation, cancellation receipt with frozen result |
| Native BLE | Android BluetoothGatt module and iOS CoreBluetooth module with bounded discovery/read/write/notify, contextual permissions and generation checks |
| Device semantics | TypeScript strict framing, replay, clock evidence, capture controller, software simulator and Devices UI |
| Synthetic live preview | Local-only fictional quality scenarios, context/boot/sequence-bound 10 Hz events, 100-sample ECG display ring, terminal null-valued fault mapping; unchanged BLE complete proof |
| Board firmware | Arduino Nano ESP32 synthetic BLE peripheral and independent portable protocol/parser core |
| Storage helper | iOS directory backup exclusion with readback; Android backup-disabled verification and FLAG_SECURE window flag |
| CI | Android debug and embedded local preview APK targets, iOS Release simulator app, Swift/Kotlin golden suites and actual Nano ESP32 board compile |

Native timing and physical channels stay uncalibrated/unqualified. There is no native JavaScript-timer fallback and no intoxication inference path in these modules.

## Executed local checks

| Check | Observed result | What it establishes |
|---|---|---|
| Scoped TypeScript compile | Passed `tsc --noEmit -p modules/tsconfig.native.json` | Reaction/device interfaces and implementation type consistency |
| Integrated mobile TypeScript and host suite | Mobile owner executed `npm run typecheck` and the full follow-up host suite: 146 tests passed, zero failed or skipped; this reviewer independently passed TypeScript and the 13 focused export/projection cases | Integrated source contracts, pure auth/lifecycle/scope guards, profile/display, cardiac selection, generation/export refusal, replacement/report navigation, hostile archives and protocol/controller tests; not full native UI execution |
| Device tests | Passed 24 Node/tsx tests (14 transport + 10 signal) | Byte framing, parsing, clocks, replay, real timed software simulator/controller behavior, exact unchanged 10-message clean proof, all seven fault scripts, 499/500 ms cutoff, identity/sample tampering and bounded display geometry |
| Original export evidence follow-up | Passed TypeScript and 13 focused tests (8 complete evidence + 5 projection) | Every retained original attempt, including nonselected alternatives; exact typed metadata and source/record linkage; independent native schedule/outcome/quantile checks, canceled 999/1000 ms response windows, intact all-omission runs, actual software-only three-channel transcripts and rehashed replay/identity/timing mutations |
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
| `android-local-preview-apk` | Release variant with embedded `assets/index.android.bundle`, arm64/x86_64 native libraries, local app ID and actual signer checked against the generated development keystore | Standalone guest demonstration; development key, no Play signing, no production identity configuration or device acceptance claim |
| `ios-simulator-app` | Swift unit tests, CocoaPods/Xcode app build, embedded main.jsbundle, zipped `.app` | Simulator architecture; no iPhone signing, provisioning or TestFlight upload |
| `nano-esp32-synthetic-firmware` | Actual compile for `arduino:esp32:nano_nora` | No flashing, radio test or sensing qualification |

### Observed native CI execution

At commit `8aa56ce9883aaafeba11b809c94bc406e7ee0a0a`, [run 38111022849](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849) produced the following inspected job outcomes:

| Job | Actual observation |
|---|---|
| [iOS 114386425766](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/job/114386425766) | **Success**: actual Swift core suites, CocoaPods install, complete Xcode simulator application build and `ios-simulator-app` upload all succeeded |
| [Shared/firmware 114386425655](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/job/114386425655) | **Success**: TypeScript/host/asset checks, C++ test, actual Nano ESP32 compile and firmware artifact upload |
| [Android 114386425801](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38111022849/job/114386425801) | **Failed before Gradle**: Expo prebuild succeeded, but `sdkmanager` was absent from PATH; no APK was produced by this job |

The Android fix at `4264c89d1ff349b4782de26b87a3348ac736850f` uses the exact runner image's documented `$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager` and verifies SDK 36 files. Subsequent actual jobs exposed missing Expo module `versionName` values, then an artifact guard incorrectly running inside a React Native included plugin build. Those source corrections are recorded in the maintained [CI evidence](../../../openspec/changes/production-mobile-platform/verification/ci-evidence.md).

At `a24634574944f8da2248a7e78feb67b599be5654`, the Android job in [run 38112450362](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38112450362) reached Kotlin compilation and failed because the default Expo view event overload accepts `Map<String, Any>` while the result intentionally retains nullable fields. The source now selects the public `EventDispatcher<Map<String, Any?>>()` overload. The inspected installed `expo-modules-core@57.0.21` path is `ViewEvent.convertEventBody` → `JSTypeConverterProvider.convertToJSValue` → recursive map/list conversion → `putGeneric(null)` → `WritableMap.putNull`. No field is filtered or cast to nonnull. `NativeEventSerializationTest.kt` uses Expo's actual conversion code and React Native's Java-only test containers to check root, nested-map and list-element nulls; execution of that Android Gradle test remains pending the next job. No APK is claimed from the failed jobs.

Initial iOS success predates the SW-012 live preview source; the working-tree host checks above do not retroactively change the contents of that built artifact. Read the maintained CI evidence for later exact commit/artifact identities. Build success does not establish real device interaction or physical calibration.

### Connect the local artifacts to the development stack

CI builds the `local` environment, using `otgd-local://oauth/callback` and public client `otgd-local-mobile`. Start the local API, OAuth stub and LocalStack using the repository's deployment instructions. These addresses are deliberately development-only; QA/prod use separately configured HTTPS origins and a real identity provider.

| Runtime | API | OAuth issuer | JavaScript |
|---|---|---|---|
| Standard Android emulator | `http://10.0.2.2:8000` | `http://10.0.2.2:8081` | Metro on host port 8082 |
| iOS simulator on the host Mac | `http://localhost:8000` | `http://localhost:8081` | Embedded Release bundle |

### Standalone Android local preview contract

The additional `android-local-preview-apk` artifact is a **local development-signed APK with embedded JavaScript**, generated from the same committed `APP_ENV=local` Expo configuration. It uses Android's `release` variant to include the JS/Hermes bundle and remove the Metro dependency. That variant name does not mean production credentials or store signing. The generated Expo 57 project was inspected: its release signing configuration explicitly refers to `signingConfigs.debug`, the generated `debug.keystore` and `androiddebugkey`. No private Play signing key is supplied or requested.

`modules/scripts/local-preview.init.gradle` fails the build unless the application ID is `dev.r3fresh.otgd.local`, the environment is local, release uses that exact generated development keystore, and release is absent from React Native's debuggable variants. `verify_android_preview.py` then inspects the actual built APK for a nonempty embedded `assets/index.android.bundle`, arm64-v8a/x86_64 native libraries, the exact local app ID and a nondebuggable Android manifest. It runs `apksigner verify` and compares the actual signer certificate SHA-256 with the certificate exported from the generated development keystore. Only then is the APK copied to the named artifact path. These inspections are required steps; authoring the scripts is not recorded as a successful APK build.

The standalone APK runs the guest demo and explicit local synthetic scenarios without Metro or a network server. Account flows still require the configured local API/OAuth service. Its configured `10.0.2.2` origins target the standard Android emulator; a physical phone needs reachable, appropriate local origins and a rebuilt artifact for account flows. QA/prod continue to require their real environment-specific HTTPS origins, identity provider and separately managed signing. The debug and standalone local APKs use the same application ID and development key, so installing one replaces the other rather than creating two applications.

To reproduce after generating the Android project, export the same local environment variables as the CI job and run:

```sh
cd apps/mobile/android
./gradlew --no-daemon --max-workers=2 \
  --init-script ../modules/scripts/local-preview.init.gradle \
  -PreactNativeArchitectures=arm64-v8a,x86_64 :app:assembleRelease
cd ..
python3 modules/scripts/verify_android_preview.py
```

Install the resulting `native-build/otgd-local-preview.apk` using `adb install -r`. It does not need a development server. Actual installation, UI behavior and physical device acceptance are separate from compiling and inspecting the file.

### Metro development APK

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
| AND-TASK-002 | Identical Kotlin/Swift LCG, shuffle, gap indexing, frozen configuration | Kotlin literal schedules and asset hashes; actual Swift suite and iOS full simulator build | Android full app build and device runtime traces |
| AND-TASK-003 | Choreographer/CADisplayLink, native input/dispatch clocks and provenance | Core budget cases and DTO validation | Physical timing bench and per-device latency characterization; no calibration claimed |
| AND-TASK-004, 005 | Bounded touch ledger, deterministic first response, quantiles/missingness | Kotlin literal scoring/boundary tests, payload bound | Native multitouch injection and runtime trace comparisons |
| AND-TASK-006 | Native background/focus/call/detach/layout invalidation and immutable terminal latch | Core terminal race/admission tests | Android/iOS interruption instrumentation including pre-layout cancel and delayed JS |
| AND-TASK-008 | Shared config/goldens, fixed presentation profile, explicit unsupported input mode | Config hash, Kotlin and actual Swift suites; iOS full simulator build | Screenshots, screen-reader and device-layout verification |
| AND-DEV-001, 002 | Devices UI and native contextual permission/radio transitions | TS tests and autolinking | Physical permission-denial, revocation, radio-off and Settings recovery tests |
| AND-SET-003, 007 | No-prompt OS permission queries; static iOS Bluetooth/camera authorization, explicit restricted/unknown state, Android check-only permission access | TypeScript check; actual iOS full app compile including these modules | Android full compile and actual OS authorization/restriction/device-policy behavior |
| AND-DEV-003, 004 | Simulator-only association, exact fixture gate, boot binding, three clock exchanges | Synthetic controller capture and spoofed-source/replay tests | Real board handshake, reconnect/reboot and clock traces |
| AND-DEV-005, 006 | Bounded framing/CRC, duplicate/conflict checks, deadlines, command identity, replay journal | TS and C++ adversarial protocol suites; actual Nano ESP32 target compile | Board flashing/run and over-the-air loss/retry/overflow tests |
| AND-DEV-007, 008 | Generation-scoped disconnect, local cancellation, forget and native lifecycle shutdown | Software cancellation test | Android/iOS BLE background and stale-callback instrumentation |
| AND-CHECK-003, 005, 006 | Capture context interface, terminal result receipt, immediate device invalidation | Interface checks; app owner covers ledger/storage tests | Full navigation/capture/background persistence integration on both platforms |
| AND-HR, AND-ECG, AND-SAL | Exact synthetic fixture adapters with transport evidence | Timed software captures and independent backend hash/projection validation | Human protocol, hardware/assay qualification and verified device trust remain external prerequisites |
| SW-012; AND-HR-001/004/007, AND-ECG-004/005 | Explicitly fictional live contact/motion/lead-off/saturation/gap/stale/insufficiency states, immediate null current reading, independent ECG sample fixture and bounded scrolling | Ten new host tests including actual timed software clean/fault captures, refusal and isolated display projection | Native accessible UI/gesture screenshots and device behavior; no human stream adapter is claimed |
| AND-EXP-003; retained native/device evidence | Export checks every original selected and nonselected projection, exact bounded metadata, seeded task and input classifications, and full synthetic transcript; changing a hash alone cannot bypass typed validation | Thirteen focused host tests; canceled response-window and all-omission task regressions, three actually executed fictional software transports and rehashed hostile mutations | Android/iOS share-sheet and file lifecycle acceptance; software hashes do not establish acquisition authenticity or qualification |
| AND-EYE | No optical stimulus command exists in this firmware/adapter; app owns passive preview and gate UI | Source scope reviewed | Approved optical configuration and physical safety/performance evidence before human stimulus work |
| Storage/privacy contracts | iOS excluded-from-backup readback and Android backup-disabled/FLAG_SECURE helper | Autolinking and interface compile | OS backup/restore and screen-capture bench verification; iOS does not claim a screenshot-prevention API |

## Physical bench acceptance record to collect

For each Android/iOS device, record model, OS, app/native build, task configuration hash, test operator/date and observed results. Exercise Back before layout, End during response, simultaneous touches including End, final-cutoff arrivals, rotation, app switch, incoming call, screen lock, touch exploration, delayed bridge delivery, input overflow, and a render stall. Inspect exactly one terminal result per run and preserve raw timing evidence. Quantify display onset with external optical instrumentation and touch latency with a controlled fixture before any calibrated-performance claim.

For BLE, record the board firmware/core version and boot ID. Exercise scan denial, radio loss, reconnect with the same boot, board reboot, duplicate/conflicting fragments and message IDs, CRC failure, slow notification/ack retry, timeout, queue/journal exhaustion and cancellation. Verify the app never promotes the board above unverified simulator status and never accepts changed fictional values. A software transcript cannot replace these observations.

All host fixtures, simulator captures and generated test values are engineering evidence only. Human assay validity, electrical/optical qualification and clinical impairment-model validation are separate external dependencies.

### SW-012 independent follow-up review

After implementation, the root reviewer independently read `signal.ts`, `signalFailure.ts`, `signalPresentation.ts`, `SignalPanel.tsx` and their controller/transport integration. No blocking source finding remained in the reviewed deadline latch, 100-sample/99-segment bounds, ECG independence, unchanged complete proof, cancellation/reset or current-scope invalid settlement. The root also passed an **actually executed local software** lead-off fixture through the backend's `CaptureAttempt` DTO and `validate_component`: the record remained invalid with null cardiac values and `SYNTHETIC_LEAD_OFF` provenance flags. The deterministic construction and settlement regression is retained in `src/device/tests/signal.test.ts`. This is a source/API review and software execution, not native rendering, electrode contact or Bluetooth execution acceptance.

The mobile owner then reviewed settlement scope and identified a queued UI callback precision issue. Start, End, Devices and error callbacks now retain the rendered workspace epoch, check ID and stage, and compare all three before invoking the controller. This complements the controller's capture-intent fence and prevents an old screen callback from operating on a new check.

### Export and partial native ledger follow-up

`src/core/exportEvidence.ts` validates the immutable original chain and calls the separately reviewed `exportProjection.ts` for every retained projection. It reconstructs the frozen native schedule, deterministic touch classification, trial outcomes, completed response windows, counts and quantiles from the retained events. An intact task with no correct responses keeps null RT quantiles and the exact `NO_CORRECT_GO_RESPONSES` flag; an invalid run keeps its partial ledger with null aggregates. Neither missingness is replaced with zero.

The follow-up found a concrete backend count mismatch: it treated an early correct response as a completed response window on a canceled run. The root corrected the independent backend count to match unchanged Kotlin/Swift semantics, `durationMs >= onsetMs + 1000` for a presented scored trial. The source and new 999/1000 ms backend regression were independently re-read; the mobile export regressions exercise both boundaries and reject an inflated count. The eight complete-evidence and five projection tests passed after this correction and formatting. Physical input/display behavior remains outside those tests.

The final targeted independent archive review also found no remaining blocker in the corrected manifest metadata admission: local and cloud fields are disjoint and required, local limitations/exclusions are fixed release text, cloud omissions are exactly `raw_artifacts`, identity/timestamps are bounded and typed, and entry sizes use the field belonging to their layout. Exact selection/owner/generation and file consumption reject orphan, foreign and unselected records. The reviewed rehashed metadata-splice tests reconstruct file and manifest hashes before verification; structural refusal therefore does not depend on an incidental stale digest. The mobile owner then reported the executed full 146-test host pass. No physical share-sheet or native file-lifecycle acceptance is implied.
