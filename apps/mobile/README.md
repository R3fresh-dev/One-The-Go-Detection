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
npm test
npm run config:check
```

This directory has its own lockfile. Run `npm ci` here; do not create a second root workspace lock. The project uses local Expo modules under `modules/`. Their Kotlin, Swift, Gradle and podspec sources must be committed. Only generated top-level `/android/` and `/ios/` directories are ignored.

## Start the local account backend

From the repository root, follow [infra/README.md](../../infra/README.md) to install Python/uv, Docker Compose and the required LocalStack credentials. For iOS simulator and desktop browser development:

```bash
uv sync --project services/api --locked
python scripts/local-platform.py prepare --host localhost
python scripts/local-platform.py up
python scripts/local-platform.py check
```

`prepare` writes local secrets to protected ignored settings. It does not print credentials. LocalStack startup requires its valid token. The isolated local issuer offers **Fictional Account A** and **Fictional Account B** for engineering; it is not a production identity provider. Use synthetic accounts/data with this stack.

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

| Artifact | Contents and intended use | Runtime and signing |
| --- | --- | --- |
| `android-local-preview-apk` | `otgd-local-preview.apk` includes the JavaScript/Hermes bundle and arm64-v8a/x86_64 native libraries. Use it for the guest demo and fictional local sensor scenarios without Metro. Guest operation does not require the API or OAuth server. | Local application ID `dev.r3fresh.otgd.local`. The generated Android **development key** signs the APK; it is not Play-signed. Account actions need the configured local backend. |
| `android-debug-apk` | Native development APK for editing and debugging. It obtains JavaScript from Metro on **port 8082**. | Same local application ID and generated development key. Installing it replaces the standalone local preview, and vice versa. |
| `ios-simulator-app` | `otgd-ios-simulator.app.zip` contains the complete `.app` and embedded `main.jsbundle`; it does not require Metro. | Built for **iOS Simulator** with code signing disabled. It runs in a compatible simulator on a Mac; it cannot be installed on an iPhone and is not a TestFlight package. |

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
- The frozen manifest binds context, every attempt and the selected component projections. Local verification checks supported schemas, canonical JSON and SHA-256 before upload/display/export. Results must bind the frozen session, target time and input digest; every `research_estimate` is rejected.
- A local read-only camera preview neither measures pupils nor records images. Permission denial remains an explicit recoverable state. The native simulator includes framed packets, CRC/replay validation and clock evidence; a connection never establishes measurement qualification.
- Home subscribes to the current device controller. It distinguishes discovery, connecting, a connected synthetic reader, permission/radio failure and reconnect states. A saved reader alias does not imply a live connection; battery or physical signal quality is never fabricated. The displayed connection observation time changes on actual state transitions, not on every sample.
- The local software cardiac simulator can demonstrate clean input, poor contact, motion, lead-off, saturation, transport gaps, stale input and insufficient samples. Its bounded live preview clears the current reading on failure and retains an invalid attempt with null physiological features. The fictional ECG trace uses arbitrary counts, draws only contiguous observed samples and does not claim mV or diagnostic quality. These scenarios do not enable human hardware or change saliva acquisition.

See [reaction task](modules/reaction-task/README.md), [device transport](src/device/README.md), [native module build evidence](modules/VERIFICATION.md), and [firmware](../../firmware/README.md) for the complete developmental protocol and board simulator.

## Account, synchronization and privacy

Hosted OAuth uses a public client, authorization code, PKCE S256, state verification, a ten-minute single-use attempt, and an allowlisted native/browser callback. API requests use the access token, never the ID token. A new authorization-code grant cannot inherit another account's refresh token. Refresh is single-flight; definitive rejection clears credentials and requires reauthentication. SecureStore writes and removals are serialized to prevent a late write restoring a signed-out session.

Every protected mutation carries a stable idempotency key and `X-Data-Generation`. Profile writes use ETag/If-Match. Snapshot, context, attempts and manifest keep distinct resource revisions. Conflict responses stop automatic overwrite; retired generations quarantine ordinary queues. Notice acknowledgments, deletion and withdrawal intents are persisted before sending, so a lost response replays the same exact request.

Maintenance, unsupported app versions and incompatible contract versions pause ordinary synchronization, including previously queued writes. Local history/practice and privacy escape routes remain available. `X-App-Version` identifies the installed version. No capability response can enable inference in this compiled release.

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

The six browser journeys cover phone-size and desktop guest checks, saved evidence, exact local export, profile validation, privacy/settings, actual simulator connection status, a fictional ECG quality failure, and bidirectional original/replacement navigation. They assert that the primary Home action is in the initial phone viewport and that there are no unexpected page errors. Report readers and cloud archive inspection are tested against actual backend-generated wire/archive fixtures at the host layer; native signed-in presentation remains a separate device check. It is distinct from native timing, camera, OS unlock and Bluetooth validation. An optional `OTGD_CHROMIUM_PATH` can point Playwright at an explicitly installed local Chromium executable; record its actual version when using that override. The default workflow uses Playwright's browser.

For a serverless Chromium alternative, verify that `FONTCONFIG_FILE` points to a readable Fontconfig file whose `<dir>` elements contain actual fonts. The temporary host verification used the package's OpenSans files plus `/usr/share/fonts/truetype` (DejaVu), a writable temporary font cache, and the runtime's library directory in `LD_LIBRARY_PATH`. A Fontconfig file referring only to an empty extraction path causes blank labels and zero-width headings; do not weaken UI visibility assertions to accommodate that configuration error. The verified alternative version and journey result are recorded in `VERIFICATION.md`; it is not an application dependency.

`fixtures:generate` writes reproducible **fictional contract fixtures** under `testfixtures/` and temporary `/tmp/mobile-*-check-bundle.json` files for independent backend parsing/upload tests. The native-result fixture was generated on a host from the frozen schedule; it is not an acquired human or hardware result. Exact backend app-config/capabilities response fixtures are also retained for boundary-decoder tests.

## QA, production and store builds

Configure the real environment's API origin, issuer, Cognito public client, OAuth redirects and EAS project ID before building. The build fails on missing cloud origins or local/example identities. `APP_BUILD_NUMBER` supplies a positive iOS build number / Android version code for local reproducibility; coordinate unique release numbering with EAS auto-increment when publishing.

```bash
# On an authenticated Expo/EAS workstation with configured environment values:
npx eas-cli build --profile qa --platform all
npx eas-cli build --profile production --platform all
```

`eas.json` defines development, internal QA and production profiles. Actual Apple/Google signing identities, provisioning, store entries, privacy declarations, any required encryption declaration, production domains and environment secrets must be supplied by the project owner/operator. No signing identity, store submission, deployed cloud environment or downloadable production binary is implied by source compilation.

Record the exact release digest and actual device evidence in [VERIFICATION.md](VERIFICATION.md). Run native installation/account transitions, lock/key-loss, cancellation/background races, VoiceOver/TalkBack and text scaling, Bluetooth denial/disconnect/replay, camera denial/restriction, export cancellation/temp cleanup, deletion/recovery and environment isolation on representative Android/iOS devices. Human hardware qualification and clinical inference validation remain separate evidence gates.
