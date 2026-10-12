# Try the native application in a browser

[Appetize](https://appetize.io/signup) can run this application's **iOS Simulator app** and **standalone Android APK** in a browser. A supported GitHub-hosted macOS runner builds iOS, so a local Mac and Apple signing membership are unnecessary for this simulator path. GitHub Actions and Appetize account allowances apply. See the live [Appetize pricing](https://appetize.io/pricing), [Apple enrollment](https://developer.apple.com/programs/enroll/) and [Google Play registration](https://support.google.com/googleplay/android-developer/answer/6112435) pages before purchasing services.

The canonical preparation workflow and offline inspection/upload tooling are implemented. **No Appetize account, API token, upload or hosted launch has been established in this workspace.** The new guarded hosted artifacts must first pass their actual workflow. Existing ordinary local APK/simulator artifacts are separate builds. They do not prove this hosted mode was compiled or launched. Store distribution, real-device measurements and physical timing remain separate acceptance requirements.

## What the hosted preview does

The preview uses the canonical `apps/mobile` application. `EXPO_PUBLIC_HOSTED_PREVIEW=true` is accepted only with `APP_ENV=local`. A persistent label identifies the fictional guest workspace. Sign-in, account restoration, configuration refresh, uploads, Bluetooth, camera acquisition and native reaction-task acquisition are unavailable in this mode. Synthetic checks and their locally retained fictional evidence let you explore onboarding, consent presentation, guided stages, history, results, profile, privacy and export without a research account or backend.

These consent and privacy interactions apply only to fictional guest data. They do not enroll a participant or authorize a study. The compiled artifact embeds its JavaScript bundle and uses reserved `https://unavailable.invalid` API/OAuth origins. It does not need Metro, AWS or an OAuth server. Do not enter real participant information. A hosted simulator cannot establish camera/Bluetooth operation, OS secure-storage behavior, physical display/touch latency or sensing qualification.

## Build and download the artifacts

1. Open or update a pull request targeting `main`. The [required aggregate workflow](../../.github/workflows/merge-gate.yml) calls the [hosted-preview workflow](../../.github/workflows/hosted-native-preview.yml) to build guarded Android and iOS guest artifacts with read-only repository permissions and no external upload or service secrets. Inspect that PR's **Required application gates** run and its **preview / android** and **preview / ios** jobs; artifact evidence identifies the exact tested source, which may be GitHub's synthetic PR merge revision. Use artifacts only from a successful aggregate run for the reviewed source revision; build success is separate from an observed hosted launch. For manual runs, GitHub exposes **Actions → Prepare hosted native guest previews → Run workflow** only after the workflow exists on default `main`; then choose the reviewed committed branch. Before merge, you can also select the feature branch in [Codespaces](../../docs/BROWSER_ACCESS_AND_SERVICES.md) for the web UI.
2. Wait for both `preview / android` and `preview / ios` jobs and the aggregate `merge-gate` to pass. They run locked dependency installation, type checking, more-than-80% mobile unit coverage and actual native golden suites. Android compiles the Release preview APK and checks its actual local package ID, embedded bundle, both ABIs and signer against the generated development key. iOS uses the reviewed Xcode 26.4.1 toolchain, runs XCTest with fresh XML/native-log verification, and compiles an unsigned ARM64 Simulator app with its embedded bundle.
3. Download `android-hosted-guest-<commit>` and/or `ios-hosted-guest-<commit>` from that run. GitHub retains these artifacts for seven days. Extract the **outer GitHub artifact ZIP**. Keep each inner native artifact and matching JSON manifest together:

| Platform | Native file to upload | Matching manifest |
|---|---|---|
| Android | `otgd-local-preview.apk` | `android-hosted-preview.json` |
| iOS | `otgd-ios-simulator.app.zip` | `ios-hosted-preview.json` |

For iOS, upload the **inner `.app.zip`**, not the outer GitHub ZIP, an `.ipa`, or the extracted `.app` directory. Appetize supports simulator `.app` archives and recommends ARM simulator builds. Its available simulator OS must support the application's minimum iOS 16.4; confirm its current device/OS inventory in your account. Android uses minimum API 24 and target API 36. The generated public Android development key signs this local preview; no Play signing key is supplied.

The manifest binds the native file's bytes, platform and application identity to an exact source commit, a SHA-256 inventory of tracked canonical build inputs, and the hosted build environment. The inspector reads the actual iOS Info.plist/Mach-O simulator platform or Android binary manifest/ELF ABIs, requires the compiled hosted build marker and a nonempty embedded bundle, and rejects ordinary local builds that lack that marker. It rejects unsafe paths, symlinks, duplicate entries, excessive expansion, wrong platform, wrong app identity, malformed binaries and changed digests.

The marker helps prevent accidentally reusing a normal local artifact. **Neither that marker nor an editable unsigned JSON manifest proves the JavaScript guard was compiled, authenticates the claimed source revision, or establishes every release gate.** Preparation/review alone cannot admit an arbitrary archive as guest-only. Admit artifacts only from the successful reviewed hosted workflow, verify their source/run identity and GitHub artifact digest, and perform the guest-only launch acceptance described below. Unknown or manually relabeled artifacts remain unqualified.

## Inspect, upload, and launch

Create your [organization-owned Appetize account](https://appetize.io/signup). To use the API, an organization administrator creates an appropriately scoped token under **Organization → API Tokens**. Confirm token/API access on your plan. Store the credential in a secret manager as `APPETIZE_API_TOKEN`; do not put it in a CLI argument, application bundle, repository or chat.

Review either artifact offline first. `review` does not contact Appetize or read the token:

```bash
python3 apps/mobile/modules/scripts/hosted_preview.py review \
  --artifact /path/to/otgd-ios-simulator.app.zip \
  --manifest /path/to/ios-hosted-preview.json

python3 apps/mobile/modules/scripts/hosted_preview.py review \
  --artifact /path/to/otgd-local-preview.apk \
  --manifest /path/to/android-hosted-preview.json
```

Once the secret manager has injected `APPETIZE_API_TOKEN` into the process environment, explicitly upload the reviewed file:

```bash
python3 apps/mobile/modules/scripts/hosted_preview.py upload \
  --artifact /path/to/otgd-ios-simulator.app.zip \
  --manifest /path/to/ios-hosted-preview.json
```

Use the same command with the Android paths for Android. Each `upload` creates a new Appetize build and can consume your account's storage/quota. The helper posts the file directly to `https://api.appetize.io/v1/apps` using the documented `X-API-KEY` header and multipart `file` field. It rechecks the exact bytes immediately before sending. It does not create a public artifact-download URL, follow redirects, disable TLS verification, buy a plan, replace another build or delete data. Vendor error bodies and credentials are omitted from errors.

The helper requests `disabled=true` and **authenticated** run, debug-log, proxy/interception, ADB and package-manager permissions. It reports these as requested, not independently verified. Sign in to [Appetize Apps](https://appetize.io/apps), find package **`dev.r3fresh.otgd.local`** on the selected platform, inspect its **App Permissions** and organization session defaults, and verify authentication is required. Then enable the build, choose a supported simulator, and select **Play**. A direct build link can be public by default; use the organization page and authenticated membership rather than assuming a hard-to-guess URL protects access.

If API tokens are unavailable on your plan, use the [Appetize Upload page](https://appetize.io/upload) with the inspected native file after configuring authenticated organization defaults. Verify permissions before enabling the build. This manual upload remains an external action; the build workflow alone does not make a hosted session available.

On first launch, confirm the fictional guest label, explore a check and its history/export, and verify no sign-in, upload or real capture is offered. Record the exact source revision, workflow run, artifact SHA-256, Appetize build ID and successful launch/screenshots. If upload, compatibility, permission review or interaction fails, retain that failure and treat hosted acceptance as pending. Stop sessions when finished to preserve your minute allowance; remove obsolete builds and revoke unused tokens through your account dashboard.

## Reproduce and validate the tooling

Offline helper checks, including negative credential/redirect and artifact cases:

```bash
python3 -m unittest infra.test.test_hosted_preview infra.test.test_swift_xctest_report -v
```

To reproduce a hosted build on an existing supported machine, use a clean committed checkout, run `npm ci` in `apps/mobile`, and export **every** workflow build value before running its native commands:

```bash
export APP_ENV=local
export EXPO_PUBLIC_HOSTED_PREVIEW=true
export EXPO_NO_DOTENV=1
export EXPO_PUBLIC_API_URL=https://unavailable.invalid
export EXPO_PUBLIC_OAUTH_ISSUER=https://unavailable.invalid
export EXPO_PUBLIC_OAUTH_CLIENT_ID=otgd-hosted-fictional
```

Follow the exact platform build/test commands in [hosted-native-preview.yml](../../.github/workflows/hosted-native-preview.yml), then run `hosted_preview.py prepare` with `--platform ios` or `--platform android`, the built `--artifact`, and output `--manifest`. Preparation refuses a dirty source checkout or an application config that did not enable the local guest guard. Generated native projects, dependencies and native artifacts are ignored; source changes must be committed for meaningful revision evidence. The helper does not compile native code or substitute for a successful platform build.

Linux can inspect both artifact formats and upload them after validation. It cannot build iOS. An iOS simulator archive cannot install on an iPhone; App Store/TestFlight need a separately signed device build and Apple enrollment. Play distribution similarly requires its account, separately controlled signing and store review. PR guest builds are mandatory dependencies of `merge-gate`; a standalone manual preview run does not satisfy that aggregate or production release admission.

## Official sources checked on 2026-10-11

- [iOS simulator packaging and ARM recommendation](https://github.com/appetizeio/appetize-docs-gitbook/blob/master/platform/app-management/uploading-apps/ios.md)
- [API authentication](https://github.com/appetizeio/appetize-docs-gitbook/blob/master/rest-api/README.md), [direct file upload](https://github.com/appetizeio/appetize-docs-gitbook/blob/master/rest-api/v1/direct-file-uploads.md), and [official v1 permission/API schema](https://github.com/appetizeio/appetize-docs-gitbook/blob/master/.gitbook/assets/appetize-v1.yaml)
- [Appetize pricing](https://appetize.io/pricing), [Apple enrollment](https://developer.apple.com/programs/enroll/), [Google Play registration](https://support.google.com/googleplay/android-developer/answer/6112435)

Service documentation describes the supported path; it is not evidence this app has launched there. Review current prices, plan permissions and simulator inventory in the actual service before buying or uploading.
