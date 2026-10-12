# Signed mobile builds and store distribution

The application is not currently published in the App Store, TestFlight or Google Play. Source compilation and a successful EAS upload do not make a public download available. This runbook prepares real signed artifacts and deliberately submits them to nonpublic store processing. Apple/Google account enrollment, actual signing identities, store listings, privacy disclosures, reviewer access and release approval remain external requirements. No approved human study, reader qualification or model is bundled or created by these commands.

For immediate fictional browser use, follow [HOSTED_PREVIEW.md](HOSTED_PREVIEW.md). Its local guest binary is a separate simulator/preview artifact and cannot enter this store release path. Ordinary native CI APKs use a development signer; iOS CI produces unsigned simulator apps. Neither is an App Store/Play package.

## Profiles and tools

| Profile       | Identity                 | Output and purpose                                                                                           |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `development` | `dev.r3fresh.otgd.local` | Local development client; requires Metro.                                                                    |
| `qa`          | `dev.r3fresh.otgd.qa`    | Internal direct-install APK / provisioned ad-hoc IPA.                                                        |
| `qa-store`    | `dev.r3fresh.otgd.qa`    | Signed AAB / device IPA for a separate QA store listing. Android submission remains an internal-track draft. |
| `production`  | `dev.r3fresh.otgd`       | Signed AAB / device IPA for the production listing. Android submission remains a production-track draft.     |

Store profiles explicitly disable hosted-preview mode, require committed source and use EAS remote version numbering with `autoIncrement`. Set the initial remote version counters in the actual EAS project; each returned native build number is pinned in the release receipt and compared with the actual artifact. `APP_BUILD_NUMBER` remains useful for local CI; it does not override EAS remote store numbering.

The helper [store_release.py](modules/scripts/store_release.py) uses **eas-cli 24.12.1** from its independent [locked toolchain](distribution/eas-toolchain/package-lock.json). It verifies the official npm archive SHA-512, installs locked dependencies without lifecycle scripts, compares every installed CLI source file with that verified archive, and executes that local entrypoint. It does not use an unpinned global CLI or `npx latest`. The main mobile dependency lock is separate. Network/TLS verification remains enabled.

Android inspection requires Java with `keytool` and the `jdk.jartool` module, plus official [bundletool 1.18.3](https://github.com/google/bundletool/releases/tag/1.18.3). Its `bundletool-all-1.18.3.jar` SHA-256 is `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`. Download it through the normal HTTPS path, verify that checksum and configure its absolute file selector. Android verification trusts only the specified upload certificate, requires strict JAR signature coverage and checks the actual package/version/minimum API 24/target API 36 manifest. Google Play App Signing uses its own distribution key; the upload certificate is a different identity.

iOS inspection and submission run on **macOS with Xcode**. The helper verifies the actual ARM64 iOS-device Mach-O, embedded public runtime configuration, version/build number, minimum iOS 16.4, `codesign`, App Store provisioning, team and independently pinned distribution certificate. It refuses a simulator, ad-hoc/enterprise/debug provisioning or guest marker. EAS cloud building alone does not run this independent admission checker. A configured protected GitHub-hosted macOS operator workflow can perform the checks without a personal Mac or local checkout; genuine account/signing inputs are still required.

The optional [manual store workflow](../../.github/workflows/mobile-store-release.yml) supports plan/build/inspection/status and read-only reconciliation of an existing submission. Its reconcile choice requires the original signed pending intent and exact provider submission UUID; a fresh upload is refused before private credential staging or AWS/EAS/store action. GitHub artifact metadata may be read during admission. Initial submission must use the helper with persistent protected operator storage, including on a properly provisioned hosted Mac. An ephemeral Actions runner cannot preserve the sole upload fence after runner loss, so automatic initial submission is not supplied by that workflow. It is separate from all mandatory PR gates and never runs on merge.

The [browser operator runbook](../../docs/RELEASE_AND_BROWSER_TESTING.md#operate-mobile-builds-from-the-browser) defines protected environment inputs, encrypted artifact selection and the pure `store_inputs.py pack` command for transferring an original operator-held pending intent through `STORE_RECEIPT_PACKAGE`. Only authenticated ciphertext crosses that handoff; original signed wire bytes and their links survive.

## Inputs and prerequisites

Use the API's locked Python environment (`uv sync --project services/api --locked`) and Node 24.19.0 or newer. Copy [store-prod.example.json](distribution/store-prod.example.json) or [store-qa.example.json](distribution/store-qa.example.json) to a protected location **outside the repository**, then replace every placeholder with actual values. Placeholders deliberately fail validation. The selected platform must be configured; the other platform may be `null`.

The JSON contains public identity/configuration and private **file selectors**, never key contents. Required fields are:

- `project_id` and `expo_account`: actual project UUID and owning account/organization slug, checked with authenticated `project:info` before any billable build. Organization membership is not assumed to equal the logged-in username.
- `api_url`, `oauth_issuer`, `oauth_client_id`: exact deployed QA/prod CloudFormation outputs. The actual target services must run the signed image and pass readiness. Their app configuration must allow `otgd-qa://oauth/callback` or production `otgd://oauth/callback`.
- `artifact_hosts`: exact operator-approved EAS artifact download hosts. Every redirect is rechecked. No authentication or Expo token is sent to these hosts; signed artifact URLs are excluded from receipts/logs.
- `android.upload_certificate_sha256`: independently trusted SHA-256 of the upload certificate **DER**; `service_account_key_path`: authorized Google Play service-account JSON selector for submission. Configure least-privilege access to the selected listing. The first Play upload and App Signing enrollment may require Play Console setup.
- `ios.asc_app_id`, `apple_team_id`, `distribution_certificate_sha256`, `api_key_id`, `api_issuer_id`, `api_key_path`: exact Apple listing/team/distribution certificate and App Store Connect API identity. The private `.p8` selector is used only for deliberate submission.

Supply genuine `EXPO_TOKEN` securely through the operator environment. Configure real remote build signing credentials in EAS first; `--freeze-credentials` refuses to silently create or replace signing identities. Set the three `EXPO_PUBLIC_*` service values in the selected project's EAS `preview` or `production` environment. The helper reads only those public named variables and requires exact equality with the deployed target; failed/absent cloud environment resolution cannot fall back to invented values.

Credential files must be owner-only regular files (0600), at most 64 KiB, outside the checkout and not symlinks/hardlinks. The helper snapshots the explicitly selected key into an isolated private temporary file, checks the original inode/version and removes the staged copy afterward. Never put secret contents in CLI arguments, source, screenshots or chat. Receipt digests bind logical credential roles, the pinned bundletool version/content, and every public target/signer field; ephemeral absolute file selectors may move between isolated remote runners. Relocating a file cannot change a listing, app/team/key ID, origin or trusted signer.

Release operations require the existing [independently signed backend release and promotion evidence](../../deploy/README.md): same source SHA/environment, the trusted Ed25519 authority, current live thirteen-job GitHub evidence and, for production, the genuine signed QA approval. PR/manual runs and local `passed` arrays cannot approve a store release. Signing a mobile receipt does not execute missing QA probes.

## Plan, build, submit and inspect status

The following commands run from the repository root. Paths stand for operator-provided inputs, not generated approval fixtures. `plan` is pure validation: no network, account operation, build, signing or submission, and no credential-file read.

```bash
uv run --project services/api python apps/mobile/modules/scripts/store_release.py plan \
  --config /tmp/otgd-store-inputs/store-config.json --platform ios
```

Build one selected platform after backend deployment and exact-revision qualification:

```bash
uv run --project services/api python apps/mobile/modules/scripts/store_release.py build \
  --config /tmp/otgd-store-inputs/store-config.json --platform ios \
  --backend-config /tmp/otgd-store-inputs/backend-config.json \
  --backend-release /tmp/otgd-store-inputs/backend-release.json \
  --gate-evidence /tmp/otgd-store-inputs/gates.json \
  --trusted-public-key /tmp/otgd-store-inputs/release-public.pem \
  --qa-evidence /tmp/otgd-store-inputs/qa-approval.json \
  --signing-key /tmp/otgd-store-inputs/release-private.pem \
  --output /tmp/otgd-store-inputs/mobile-build.json
```

Use `--platform android` for AAB. QA does not require `--qa-evidence`; production does. The helper copies only committed source into an isolated checkout, uses frozen package locks, verifies official cloud configuration and waits for the exact build UUID. It then downloads/inspects the exact bounded artifact and rechecks source, actual backend, public EAS environment and live gate authority before signing the build receipt. It does not submit automatically. Artifact limits are 512 MiB compressed / 1 GiB expanded; unsupported files fail, rather than disabling inspection. Store binary URLs are not exported in receipts.

Submit the exact signed build receipt with the same authority inputs:

```bash
uv run --project services/api python apps/mobile/modules/scripts/store_release.py submit \
  --config /tmp/otgd-store-inputs/store-config.json --platform ios \
  --backend-config /tmp/otgd-store-inputs/backend-config.json \
  --backend-release /tmp/otgd-store-inputs/backend-release.json \
  --gate-evidence /tmp/otgd-store-inputs/gates.json \
  --trusted-public-key /tmp/otgd-store-inputs/release-public.pem \
  --qa-evidence /tmp/otgd-store-inputs/qa-approval.json \
  --signing-key /tmp/otgd-store-inputs/release-private.pem \
  --receipt /tmp/otgd-store-inputs/mobile-build.json \
  --output /tmp/otgd-store-inputs/mobile-submission.json
```

The signed build receipt expires after seven days. Submission rechecks actual build metadata, bytes/signature, target configuration and backend authority. A submission-only temporary EAS configuration supplies the actual listing ID and private key selector; it never rebuilds from that modified configuration. The exact command uses `--id UUID`, never `--latest`, `--url` or automatic public rollout. iOS automatic TestFlight group setup is disabled. Android is always a draft with changes not automatically sent for review.

A signed `mobile-submission.json.intent.json` is stored **before** the external call in existing protected operator storage. The helper creates it exclusively with mode 0600, flushes and fsyncs the file, then fsyncs its parent directory. A failed durability barrier refuses upload and retains any created fence. If the response is lost, retain that original intent and inspect the protected EAS dashboard. Retrying without an exact `--submission-id UUID` refuses to create a second request. With that UUID, the helper queries `submit:view`, checks the original intent/build/listing/track and signs the resolved receipt. It never uploads again during reconciliation. A timeout terminates only the owned local tool process group; an already-created remote build/submission may still exist. Do not delete pending intent evidence to force a retry.

Read status without making a new submission:

```bash
uv run --project services/api python apps/mobile/modules/scripts/store_release.py status \
  --config /tmp/otgd-store-inputs/store-config.json --platform ios \
  --trusted-public-key /tmp/otgd-store-inputs/release-public.pem \
  --receipt /tmp/otgd-store-inputs/mobile-build.json \
  --submission-receipt /tmp/otgd-store-inputs/mobile-submission.json
```

An EAS `FINISHED` submission means the upload completed. **`store_availability: not_verified` remains explicit.** Apple still processes the build; choose actual TestFlight groups and satisfy any external-testing review. Public App Store release requires store information, required privacy/research disclosures, App Review and a deliberate release choice. Play drafts must be reviewed and deliberately released to the selected test/production track; a draft serves no users. Testing opt-in links and actual App Store/Play listing URLs exist only after the project owner completes those steps. This tool does not manufacture public listing or tester URLs.

## Official contracts and verification

The pinned CLI source was inspected for its actual output: `config --json` returns `{buildProfile, appConfig}`; `build --json` returns an array even for one platform; `build:view --json` returns one build. `submit` has **no `--json` option**. The helper extracts its exact submission UUID and independently queries `submit:view --json`; Android GraphQL status is uppercase `DRAFT`. JSON output removes null fields. The exact public variable command is `env:get ENV --variable-name NAME --scope project --format short --non-interactive`. No genuine account-authenticated store operation has been executed in this environment.

Relevant official documentation: [Expo iOS submission](https://docs.expo.dev/submit/ios/), [Expo Android submission](https://docs.expo.dev/submit/android/), [EAS version management](https://docs.expo.dev/build-reference/app-versions/), [Apple review submission](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app), [Google signing](https://developer.android.com/studio/publish/app-signing), and [Google release preparation](https://support.google.com/googleplay/android-developer/answer/9859348).

Meaningful helper unit tests live in [test_mobile_store_release.py](../../services/api/tests/test_mobile_store_release.py) and run in the existing mandatory API unit gate. They include actual JDK cryptographic JAR verification and appended-unsigned-entry refusal, while macOS tool and vendor-account boundaries are explicitly doubled. Their results do not establish a real signed IPA/AAB, physical sensing approval, tester availability or store publication. Full repository gates and platform release evidence remain required for the exact final revision.
