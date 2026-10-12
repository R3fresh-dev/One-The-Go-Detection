# One The Go — Android and iOS application

An Expo 57 / React Native research measurement application. It implements guest and account workspaces, optional profile context, approved study acquisition, native camera ROI and reaction modules, a device-signed reader dialect, immutable evidence, explicit uploads, history, exact-scope export, privacy jobs, study consent/withdrawal, and accessibility/settings flows. Installed software is separate from scientific and device qualification.

**The app does not provide driving clearance, a metabolic rate, or a clearance-time estimate.** No approved human configuration, participant study or active model is bundled. Ordinary and guest checks remain measurements. A separately admitted version 1.1 research result is accepted only with its immutable context, evidence, model authority and named historical endpoint; unapproved and simulated measurements cannot become an estimate. The native reaction practice remains uncalibrated. Fictional examples and account engineering fixtures carry their own provenance.

Read [verification evidence and outstanding device checks](VERIFICATION.md), the [reviewed requirements](../../openspec/changes/production-mobile-platform/proposal.md), [shared contracts](../../openspec/changes/production-mobile-platform/shared-contracts.md), and [platform contract](../../openspec/changes/production-mobile-platform/platform-contract.md). The backend and deployment guides are [services/api](../../services/api/README.md), [infra](../../infra/README.md), and [deploy](../../deploy/README.md).

## Standalone fictional browser and hosted native preview

Run `npm run export:preview` to build `dist-preview/`, then serve that directory with `OTGD_WEB_DIST=dist-preview npm run serve:web`. The static files can be hosted by an ordinary static website provider without AWS or an OAuth account. This build is restricted to local fictional guest use: no sign-in, network calls, camera/Bluetooth permissions, native reaction acquisition, raw recording or uploads. Browser records exist only in memory and disappear when the page reloads. Never enter real participant information.

Both web export commands clear Metro's transform cache so compiled environment, service origins and the hosted-preview guard are rebuilt rather than inherited from a previous environment's bundle.

For native iOS/Android in a browser, read [HOSTED_PREVIEW.md](HOSTED_PREVIEW.md). Successful reviewed hosted workflow provenance and the actual package preview markers are required; changing environment variables cannot relabel an older ordinary APK or simulator app. Scientific or hardware approval is not established by a simulator.

Separate raw recording choices and retention are specified in the [optional-purpose customer flow](../../openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md). The account UI verifies the exact policy and notice and displays immutable receipts independently from pending physical cleanup.

Optional native ROI/ECG recording starts off for each capture. A fresh online start must pin the separate consent receipt and approved codec. The app stores the bounded handoff and metadata together in SQLCipher, releases native memory, and never queues raw bytes merely because a check was saved. Select each retained file explicitly before Upload check; files upload before server finalization. Ticket retries preserve unknown request outcomes, and later acknowledged expired tickets receive a new bounded renewal identity. Revocation stops acquisition immediately and blocks dependent uploads. Expired and unindexed local bytes are purged before an unlocked workspace is exposed and on foreground maintenance; a stopped app cannot execute deletion at an exact wall-clock deadline, and reads are denied immediately when the deadline has passed.

Cloud exports keep raw data excluded by default. An independently approved export purpose, exact notice acknowledgment and explicit artifact selection are required to add eligible recordings. The downloaded ZIP must match the owned job receipt, selected study/checks, exact versioned source digests and bounded binary paths. Export permission is separate from permission to record or upload. Shared recipient copies cannot be recalled.

## Approved preparation and laboratory collection

An account check starts only from the current approved study, exact active consent and released configuration. Pulse and ECG present the configuration's versioned rest, posture, activity, contact and isolation instructions. The service persists the preparation attempt before the foreground monotonic rest timer starts. Interrupting the app, changing the instruction envelope or a discontinuous clock resets rest and confirmations. Each required declaration starts unchecked; it records declared compliance and does not prove electrical isolation, power or charging state. Human ECG remains unavailable when the required independent hardware-state verifier is not installed.

A version 1.1 HR-only research result may carry an independently admitted cardiac interval authority. The reader verifies the preserved sensor flags, exact policy/calibration/configuration and selected attempt, conservative server issue-to-receipt bounds, and any baseline scope. This does not claim precise sensor onset, ECG timing or physiological validation. Missing optional self-report context remains absent in the immutable capture and is represented as null in an export's profile summary.

For `reference_lab_import_v1`, choose and acknowledge the exact approved collection method; no BLE reader is involved. The specimen form retains observed saliva/buffer volumes, the approved dilution convention, supply identities and expiry, handling events, and explicit approved reasons for unknown values. It never accepts participant-entered concentrations. Its sample identity, original time, complete declaration digest and accepted collection receipt remain immutable. Invalid specimens retain their actual failure facts and require a fresh sample for retry.

Save a collecting or pending specimen as a draft to resume it later. The cloud check stays open while independent laboratory analysis is pending; ordinary upload/finalization is blocked. Refresh analysis explicitly to retain the independently admitted source report and its separate analysis attempt. Then review, save and explicitly upload the complete check. Ending pending analysis requires a separate confirmation and preserves the collected sample and receipt; a delayed report cannot revive it. A new laboratory collection after cancellation requires a new check. The current protocol may still refuse a check without the required chemical evidence.

Lost acknowledgment, collection and cancellation replies retain the original body, idempotency key and event time. Reconciliation never restarts hardware or credits an expired acknowledgment with a new time. Local and cloud structured exports preserve `instruction_receipts`, `collections` and `collection_abandons` alongside immutable attempts, including invalid or unused specimens. The reviewed flow is in [qualified participant acquisition](../../openspec/changes/qualified-participant-acquisition/proposal.md).

## Prerequisites and installation

| Component                   | Pinned or required value                                              |
| --------------------------- | --------------------------------------------------------------------- |
| Node                        | 22.13 or later; the checked-in CI workflow uses 24.19.0               |
| Expo / React Native / React | 57.0.27 / 0.86.3 / 19.2.3, with the independent `package-lock.json`   |
| Android                     | API 24 minimum; compile/target 36; JDK 17 and Android SDK 36          |
| iOS                         | iOS 16.4 minimum; Xcode 26.4 or newer compatible toolchain; CocoaPods |
| Development networking      | API 8000, fictional issuer 8081, Metro/web 8082                       |

Run from this directory:

```bash
npm ci
npm run typecheck
npm run test:coverage
npm run config:check
```

This directory has its own lockfile. Run `npm ci` here; do not create a second root workspace lock. The project uses local Expo modules under `modules/`. Their Kotlin, Swift, Gradle and podspec sources must be committed. Only generated top-level `/android/` and `/ios/` directories are ignored.

## Start the local account backend

From the repository root, follow [infra/README.md](../../infra/README.md) to install Python/uv and Docker Compose. The pinned LocalStack 4.14.0 community image is the default and needs no authentication token. For iOS simulator and desktop browser development:

```bash
uv sync --project services/api --locked
python scripts/local-platform.py prepare --host localhost
python scripts/local-platform.py up
python scripts/local-platform.py check
```

`prepare` writes local secrets to protected ignored settings. It does not print credentials. An explicitly selected licensed LocalStack alternative requires its genuine token; the community default does not. The isolated local issuer offers **Fictional Account A** and **Fictional Account B** for engineering; it is not a production identity provider. Use synthetic accounts/data with this stack.

Copy `.env.example` to `.env` inside `apps/mobile` and choose one consistent network origin before generating the native build:

| Environment          | API                                                              | OAuth issuer                | Callback                      |
| -------------------- | ---------------------------------------------------------------- | --------------------------- | ----------------------------- |
| iOS simulator        | `http://localhost:8000`                                          | `http://localhost:8081`     | `otgd-local://oauth/callback` |
| Android emulator     | `http://10.0.2.2:8000`                                           | `http://10.0.2.2:8081`      | `otgd-local://oauth/callback` |
| Browser preview      | `http://localhost:8000`                                          | `http://localhost:8081`     | `http://localhost:8082/`      |
| Physical local phone | Computer's explicitly configured reachable LAN origin, port 8000 | Same hostname/IP, port 8081 | `otgd-local://oauth/callback` |

For Android, run backend preparation with `--host 10.0.2.2` and set **both** mobile public origins to `10.0.2.2`. For a physical phone, use the backend helper's documented `--lan` mode and matching local build configuration. Backend issuer metadata, token issuer, app build issuer and redirect registration must match exactly; `localhost` and `127.0.0.1` are different OAuth identities. A build configured for localhost cannot use localhost to reach a laptop from a physical phone.

Example Android settings:

```dotenv
APP_ENV=local
APP_BUILD_NUMBER=1
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
EXPO_PUBLIC_OAUTH_ISSUER=http://10.0.2.2:8081
EXPO_PUBLIC_OAUTH_CLIENT_ID=otgd-local-mobile
```

Local HTTP exceptions are limited to the configured development hosts. QA and production require real HTTPS origins and their Cognito public client IDs. Secrets, tokens and signing credentials do not belong in `EXPO_PUBLIC_*` values.

## Run Android or iOS

These are **native development builds**, because the reaction task, Bluetooth transport, storage protection and SQLCipher configuration need compiled native code. Expo Go cannot provide those guarantees and is not the supported test runtime.

```bash
# Android emulator/device; generates the native project when needed.
npm run android

# iOS simulator/device, on a supported macOS/Xcode machine.
npm run ios

# Start Metro for an already-installed development build.
npm start
```

All three scripts select port **8082**, because the local OAuth issuer occupies 8081. Keep the same environment variables when generating/building and starting Metro. Changing an origin, scheme, native plugin or module requires rebuilding the development client; a JavaScript reload cannot replace a native configuration.

### Choose the build artifact

The [native build workflow](../../.github/workflows/native-build.yml) generates projects from committed configuration, verifies local-module assets and runs Android Kotlin and Swift tests. [Run 38114016108](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38114016108) at commit `9376dbaac603252bb49ad2bb5ec5ba8cc5be5017` successfully built, inspected and uploaded both Android APKs and the iOS simulator app. The Android report contains seven passed tests, with no failures or skips. Consult the [observed native CI evidence](modules/VERIFICATION.md#observed-native-ci-execution) for exact artifact IDs, hashes and retention dates; installation and device interaction remain separate acceptance checks.

| Artifact                    | Contents and intended use                                                                                                                                                                                                                     | Runtime and signing                                                                                                                                                               |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `android-local-preview-apk` | `otgd-local-preview.apk` includes the JavaScript/Hermes bundle and arm64-v8a/x86_64 native libraries. Use it for the guest demo and fictional local sensor scenarios without Metro. Guest operation does not require the API or OAuth server. | Local application ID `dev.r3fresh.otgd.local`. The generated Android **development key** signs the APK; it is not Play-signed. Account actions need the configured local backend. |
| `android-debug-apk`         | Native development APK for editing and debugging. It obtains JavaScript from Metro on **port 8082**.                                                                                                                                          | Same local application ID and generated development key. Installing it replaces the standalone local preview, and vice versa.                                                     |
| `ios-simulator-app`         | `otgd-ios-simulator.app.zip` contains the complete `.app` and embedded `main.jsbundle`; it does not require Metro.                                                                                                                            | Built for **iOS Simulator** with code signing disabled. It runs in a compatible simulator on a Mac; it cannot be installed on an iPhone and is not a TestFlight package.          |

The standalone Android preview uses the `release` build variant to embed its bundle. Here, that variant name describes the build mode, not production signing. Before upload, the workflow checks the actual APK for a nonempty bundle, both native architectures, the exact local application ID and a nondebuggable manifest. It verifies the signer certificate against the generated `debug.keystore`/`androiddebugkey`. The exact Gradle and artifact-verification commands are in [native build verification](modules/VERIFICATION.md#standalone-android-local-preview-contract).

After downloading and extracting a successful standalone artifact, install it on the connected Android emulator or compatible phone:

```bash
adb install -r /path/to/otgd-local-preview.apk
```

Open the application and choose **Explore demo**. The synthetic sensor readings are fictional, and the native reaction task remains explicitly uncalibrated practice. To use the debug APK instead, install its extracted APK and run `npm start` from this directory with the same local environment; keep Metro on 8082. For iOS, extract both the GitHub artifact ZIP and its contained app ZIP, then use `xcrun simctl install booted /path/to/extracted.app` and `xcrun simctl launch booted dev.r3fresh.otgd.local` on a Mac with a booted compatible simulator.

**CI networking targets simulators.** The Android artifacts embed API `http://10.0.2.2:8000` and OAuth issuer `http://10.0.2.2:8081`; these are the standard Android emulator's routes to the development host. The iOS simulator artifact embeds `http://localhost:8000` and `http://localhost:8081`. These settings use `otgd-local://oauth/callback` and public client `otgd-local-mobile`.

A physical Android phone can use the bundled guest demonstration independently of those backend addresses. For account/API testing on a physical phone, prepare the backend with its documented `--host`/`--lan` settings, set **both** `EXPO_PUBLIC_API_URL` and `EXPO_PUBLIC_OAUTH_ISSUER` to the same phone-reachable development host, and rebuild with `APP_ENV=local`. A downloaded embedded bundle cannot acquire new API origins merely by editing a `.env` file afterward. Physical iPhone testing additionally needs a separately signed device build; the simulator artifact does not supply one. Use the network table above and the [local platform guide](../../infra/README.md) for matching origins and redirect registration.

## Guest demonstration and browser preview

```bash
npm run web
```

Choose **Explore demo**, read the limitations, acknowledge the local notice, review optional context and start a demo check. The guided stages provide fictional saliva/eye/cardiac examples and a camera-positioning preview. On native builds, a separate action starts the real native reaction task. On web, the native task is explicitly unavailable; the app does not substitute a JavaScript timer for native acquisition.

Guest checks never upload or migrate into a signed-in workspace. The **browser preview keeps records and tokens in memory only**; reload clears them. It does not claim encrypted browser persistence. Native storage uses SQLCipher with a random per-workspace key protected by SecureStore. Account unlocking uses the device credential/biometric prompt and owner namespace; signed-out records need the same issuer/account to sign in again.

A check is first saved using **Save on this device**. Account checks then offer a separate **Upload check** action. “Retry queued uploads automatically” starts off and applies only to already explicitly queued operations. It never queues a future check. Guest upload is rejected by the domain layer. Account-owned fictional fixtures are limited to local/QA engineering environments and do not include personal profile values or real native task data.

## Evidence, profile and capture behavior

- Optional demographics are nullable. Locale decimal input is normalized to SI units. US customary height uses feet plus inches; conversion factors are exact. Unit display rounding does not replace retained canonical values. Entry bounds are software guardrails, not clinical thresholds.
- Profile and time-varying context freeze at **Start check**. A known last-use timestamp is retained and elapsed time is derived for that check's frozen target time. Later profile edits apply only to new checks.
- An attempt ID is persisted before acquisition. Terminal attempts are immutable. Invalid attempts can be retried with new IDs. A valid acquisition cannot be repeated merely to choose a preferred value.
- One valid PPG and one valid ECG alternative can coexist. Both stay in the ledger, and Review requires an explicit final cardiac selection. PPG does not acquire ECG features.
- Native cancellation is requested before radio/storage waits. Route changes/backgrounding invalidate pending starts. The callback and cancellation receipt share the exact native terminal ledger and one durable write. There is no time-based discard of delayed native evidence.
- The frozen manifest binds context, every attempt and the selected component projections. Local verification checks supported schemas, canonical JSON and SHA-256 before upload/display/export. Results bind the frozen session, target time and input digest. Version 0.1 rejects research estimates; a separately admitted version 1.1 research estimate additionally verifies immutable model, policy, artifact and evidence authority. Simulated inputs and missing approvals never qualify.
- A local read-only camera preview neither measures pupils nor records images. Permission denial remains an explicit recoverable state. The native simulator includes framed packets, CRC/replay validation and clock evidence; a connection never establishes measurement qualification.
- Home subscribes to the current device controller. It distinguishes discovery, connecting, a connected synthetic reader, permission/radio failure and reconnect states. A saved reader alias does not imply a live connection; battery or physical signal quality is never fabricated. The displayed connection observation time changes on actual state transitions, not on every sample.
- The local software cardiac simulator can demonstrate clean input, poor contact, motion, lead-off, saturation, transport gaps, stale input and insufficient samples. Its bounded live preview clears the current reading on failure and retains an invalid attempt with null physiological features. The fictional ECG trace uses arbitrary counts, draws only contiguous observed samples and does not claim mV or diagnostic quality. These scenarios do not enable human hardware or change saliva acquisition.

See [reaction task](modules/reaction-task/README.md), [device transport](src/device/README.md), [native module build evidence](modules/VERIFICATION.md), and [firmware](../../firmware/README.md) for the complete developmental protocol and board simulator.

## Account, synchronization and privacy

Hosted OAuth uses a public client, authorization code, PKCE S256, state verification, a ten-minute single-use attempt, and an allowlisted native/browser callback. API requests use the access token, never the ID token. A new authorization-code grant cannot inherit another account's refresh token. Refresh is single-flight; definitive rejection clears credentials and requires reauthentication. SecureStore writes and removals are serialized to prevent a late write restoring a signed-out session.

Every protected mutation carries a stable idempotency key and `X-Data-Generation`. Profile writes use ETag/If-Match. Snapshot, context, attempts and manifest keep distinct resource revisions. Conflict responses stop automatic overwrite; retired generations quarantine ordinary queues. Notice acknowledgments, deletion and withdrawal intents are persisted before sending, so a lost response replays the same exact request.

Maintenance, unsupported app versions and incompatible contract versions pause ordinary synchronization, including previously queued writes. Local history/practice and privacy escape routes remain available. `X-App-Version` identifies the installed version. A capability advertises software formats and current service eligibility; it cannot by itself authorize an estimate. The version 1.1 reader additionally requires the exact admitted model authority, frozen context/evidence and named historical endpoint. No approved model or human qualification is bundled, and ordinary or simulated checks remain measurement-only. Historical version 0.1 results retain their measurement-only validation rules.

Cloud deletion requires fresh same-account sign-in followed by a final **Request deletion** confirmation. Jobs distinguish pending/running/completed/failed and the applicable partially-retained/expired states. Acknowledging a new generation after completed all-data deletion opens an empty workspace; old queues cannot restore erased records.

Export selection records source and exact check IDs. One-check exports cannot silently expand. Local/cloud archives include verified profile/context, selected snapshots/results, every selected and nonselected attempt, manifests and available immutable report revisions. Limits are 500 selected checks, **512 KiB per structured record**, 50 MiB total uncompressed, 64 MiB archive and 65,000 entries. Only the archive manifest is exempt from the per-record bound; its bytes still count toward the total. Each report index is at most 16 KiB and references at most 20 separate 512 KiB companions. An oversized selection fails as a whole.

Archive verification reconstructs the original context/attempt/selection chain, checks native timing and fictional transport evidence, verifies report predecessor/result hashes, and rejects unselected files or profile versions even if every container hash has been recomputed. Local and cloud manifests have separate exact schemas and fixed exclusion metadata. A known incomplete report cache blocks a device export with an explicit refresh instruction; the app never silently leaves known report revisions out. Share sheets receive a temporary copy, which the app removes afterward; already shared copies cannot be recalled.

### New acquisitions and laboratory report history

A **replacement check** is a new acquisition with newly confirmed, frozen context. Results link directly to the original and its replacements, preserving each original snapshot. Current account/generation checks and the direct relationship are verified before a link opens. Server pagination remains explicit when further replacements exist.

**Laboratory report history** is separate from new acquisition. For an eligible uploaded check, **Refresh laboratory reports** loads a bounded immutable chain of verified correction or same-specimen reanalysis companions. The reader preserves the original result, makes original collection/target time and later report/acceptance/evaluation times distinct, and identifies carried-forward versus revised analytes. It provides previous/next and original-record navigation. Cached verified revisions remain readable offline, but a new or partial chain needs the same account to refresh. These read-only views cannot change the original sample or classify present intoxication. Administrative report authoring and its source-document permissions are enforced by the API; the mobile reader does not expose an arbitrary PDF or result editor.

Research invitations and exact-version consent are separate from sign-in and application notice acknowledgment. Withdrawal first stops local study work and persists its exact request. This release contains no approved human study acquisition configuration; consent does not change that gate.

## Verify the implementation

```bash
npm run typecheck
npm test
npm run fixtures:generate
npm run config:check
npm run export:web

# Browser journeys against the exported application:
npx playwright install chromium
npm run test:e2e
```

Browser component and application journeys run at phone and desktop sizes. They cover guest checks, exact export, profile/privacy/settings, simulator faults and replacement navigation, plus separate raw permissions, approved preparation, monotonic-clock interruption, stale approval/unmount, specimen quantities and pending laboratory refresh/cancellation. Hosted-preview tests use a separate fresh fictional build. Structured report and archive readers also consume actual backend-generated fictional HTTP/worker fixtures. These software checks do not establish native timing, camera, SQLCipher, OS unlock or Bluetooth qualification; signed-in native presentation still requires device verification. An optional `OTGD_CHROMIUM_PATH` can point Playwright at an explicitly installed Chromium; record its actual version. The default workflow uses Playwright's browser.

For a serverless Chromium alternative, verify that `FONTCONFIG_FILE` points to a readable Fontconfig file whose `<dir>` elements contain actual fonts. The temporary host verification used the package's OpenSans files plus `/usr/share/fonts/truetype` (DejaVu), a writable temporary font cache, and the runtime's library directory in `LD_LIBRARY_PATH`. A Fontconfig file referring only to an empty extraction path causes blank labels and zero-width headings; do not weaken UI visibility assertions to accommodate that configuration error. The verified alternative version and journey result are recorded in `VERIFICATION.md`; it is not an application dependency.

`fixtures:generate` writes reproducible **fictional contract fixtures** under `testfixtures/` and temporary `/tmp/mobile-*-check-bundle.json` files for independent backend parsing/upload tests. The native-result fixture was generated on a host from the frozen schedule; it is not an acquired human or hardware result. Exact backend app-config/capabilities response fixtures are also retained for boundary-decoder tests.

## QA, production and store builds

Follow [STORE_RELEASE.md](STORE_RELEASE.md) for the guarded store automation, exact inputs, nonpublic submission and status semantics. Configure the actual backend API origin, issuer, public client, OAuth redirects and Expo project. Local CI uses `APP_BUILD_NUMBER`; store profiles use EAS remote version numbering and pin the actual returned native version.

```bash
# Pure configuration plan; no account/build/submission:
uv run --project ../../services/api python modules/scripts/store_release.py plan \
  --config /secure/store-config.json --platform ios
```

`eas.json` separates development, direct-install QA, QA store and production store profiles. The store helper requires exact trusted release gates, signed backend/production QA authority and genuine signing/store inputs; it inspects the actual device IPA/AAB before deliberate submission. Apple/Google review, privacy declarations and tester/public release remain operator actions. No downloadable production binary is implied by source compilation or a draft upload.

Record the exact release digest and actual device evidence in [VERIFICATION.md](VERIFICATION.md). Run native installation/account transitions, lock/key-loss, cancellation/background races, VoiceOver/TalkBack and text scaling, Bluetooth denial/disconnect/replay, camera denial/restriction, export cancellation/temp cleanup, deletion/recovery and environment isolation on representative Android/iOS devices. Human hardware qualification and clinical inference validation remain separate evidence gates.
