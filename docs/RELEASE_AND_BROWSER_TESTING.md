# Release, deployment and browser testing

The canonical application lives in apps/mobile, services/api, infra and deploy. The separate Python entry points are [deploy/qa.py](../deploy/qa.py), [deploy/prod.py](../deploy/prod.py) and [deploy/register_cname.py](../deploy/register_cname.py). Each uses the same reviewed release admission; no script creates an account or invents approvals.

## What is implemented and what remains

| Area | Supplied software | Required external acceptance |
|---|---|---|
| Research/customer flows | Account/consent/approval registries; native reaction/optical/Bluetooth; signed ADC and pinned SparkFun digital PPG; approved instructions/rest; laboratory collection without BLE; separate staff PDF/import; immutable records/export/privacy; gated model/evaluation | Assigned operators, real study/assay/model authority, phone/reader/reference and electrical/optical validation |
| AWS delivery | Separate QA/prod one-shot infrastructure/security/code/web orchestration, maintenance/recovery, exact-source signed promotion, public probes and conflict-safe CNAME | Intended AWS accounts/profiles, owned domains/issued TLS, trusted signing authority, actual QA/production operational/customer probes |
| Native store delivery | Explicit device/AAB profiles and exact-source build/inspection/submission/status tooling | Expo/Apple/Google project/app records and credentials, signed builds, required first-upload/testing/processing/review and real tester/public availability |
| Browser preview | Dedicated fixed-origin guest web export and automatic Codespaces lifecycle; guarded native simulator/APK builds | Actual Codespace or Appetize account/session; physical hardware behavior stays separate |
| Portable saliva chemistry/breath instruments | Typed analytical contracts and reference-laboratory import; unavailable instrument capabilities remain explicit | A selected instrument's complete vendor protocol/SDK and calibration/reference method, then the actual driver and observed analytical acceptance |
| Human ECG safety observation | Signed acquisition and approved instruction/declaration software | A real observer/interface for permitted power/charging/cable/isolation state plus complete electrical safety evidence; a checkbox cannot supply observation |

At commit [9694554](https://github.com/R3fresh-dev/One-The-Go-Detection/commit/96945549ab0466c26300a2863f907cf20da35042), all seven local categories and [all thirteen GitHub jobs](https://github.com/R3fresh-dev/One-The-Go-Detection/actions/runs/38131498621) passed. This follow-up changes source and therefore needs a new completed run. Historical evidence does not verify new changes. Main protection was independently observed absent; Administration returned 403. The user's prerequisite remains enforced as our completion policy: do not merge or call the task complete before actual required-check/admin enforcement is verified.

## Explore the web UI entirely in a browser

1. Open [Create a Codespace](https://codespaces.new/R3fresh-dev/One-The-Go-Detection), sign into your existing GitHub account and select feat/complete-research-platform, the reviewed development branch.
2. Select the two-core machine and create it. Its committed devcontainer installs locked dependencies, checks types, clears Metro and exports the fictional guest application into dist-preview automatically.
3. Open Ports, choose Fictional application preview and Open in Browser if the preview did not open automatically. Keep the default private visibility. The startup hook verifies the guest export and refuses stale output or an unrelated server.
4. Explore first-run notice, profile, guided fictional check, results, history, privacy and export. Browser guest records are memory-only and reset on reload; account, camera, BLE, raw recording, uploads and inference are unavailable in this preview.
5. Stop the Codespace when finished; delete it when its stored workspace is no longer needed. Your compute/storage allowance and billing settings apply.

No local clone, terminal or AWS account is needed for that guest flow. A Codespace is created in your GitHub account; source/setup alone does not create a hosted session. The current managed workspace has no user-facing forwarding capability, no existing Codespace or Pages site, and no Appetize credentials. Internal browser validation is therefore distinct from a live URL you can open. Signed-in web acceptance uses the separately deployed QA HTTPS web_origin and its real Cognito identity.

## Explore iOS or Android in a browser

Use [Appetize](https://appetize.io/) with its available free allowance or an appropriate account plan. No local Mac or Apple membership is needed for a simulator guest preview.

1. In the reviewed PR, open the successful Required application gates workflow run for its exact source. Download the Android/iOS hosted guest artifacts from the run summary. Both preview jobs and the aggregate must pass.
2. Extract the outer GitHub artifact ZIP. For iOS keep the inner otgd-ios-simulator.app.zip intact; for Android select otgd-local-preview.apk. Preserve the matching JSON manifests. These are guest/simulator artifacts, not App Store IPA/Play AAB releases.
3. Create/sign into Appetize and upload the selected native file. Select a supported hosted device/OS and launch it in your browser. Follow the guest notice and explore the fictional flow.
4. Keep actual account/camera/Bluetooth/sensor or physical timing acceptance separate. Browser simulation does not measure a phone/reader or validate a human model.

[HOSTED_PREVIEW.md](../apps/mobile/HOSTED_PREVIEW.md) gives artifact IDs, verified historical source, inspection/upload details and service limits. GitHub artifacts are retained for seven days after upload; a newer changed revision requires its own source-bound successful builds. No upload/session is claimed before it actually occurs.

## Prepare genuine AWS inputs

Use Python 3.12/uv, Node 24.19, Docker Buildx, the committed dependency locks and intended AWS CLI profiles. Install locked Python dependencies and infra npm dependencies. Copy [qa.example.json](../infra/config/qa.example.json) and [prod.example.json](../infra/config/prod.example.json) into ignored qa.local.json/prod.local.json files. Templates deliberately reject placeholder account/domain/certificate/budget values until replaced.

| Input | Meaning |
|---|---|
| account, region, profile | Actual separate QA/prod account; STS must return the configured account. An existing selector alone does not prove authenticated access. |
| domain, certificateArn | Owned API host and issued regional ACM certificate. CloudFront custom TLS separately uses an issued same-account us-east-1 certificate. |
| releaseId, imageDigest | Reviewed immutable source and admitted tested service digest; production preserves QA's digest. |
| gate-evidence, trusted-public-key | Actual exact-source trusted GitHub run provenance and independently trusted Ed25519 public authority. A hand-edited passed JSON or PR/manual event is not a production release. |
| signing-key | Protected current-user-owned Ed25519 PEM, no group/other access, regular stable single-link file; never a command-line secret value. |
| cost estimate, budget, operator | Current actual workload/region estimate, approved budget/alarm destination and accountable role. Alerts do not cap spending. |
| webDomain, webCertificateArn, public zone | Optional web subdomain/issued us-east-1 TLS/public same-account zone. Managed Route 53 enables the full one-shot custom-name path. |
| source QA approval | Independent signed actual QA network/worker/privacy/restore/alarm and authenticated web acceptance for the exact service/web artifacts; never generated by public probes. |

Production mobile callbacks are otgd://oauth/callback; QA callbacks are otgd-qa://oauth/callback. The web callback is the exact deployed web_origin plus slash. Store tooling checks compiled callbacks against actual deployed registration.

## One command deploys QA

Review a valid configuration without cloud/build/signing actions:

```bash
uv run --project services/api python deploy/qa.py --config infra/config/qa.local.json --plan
```

For a genuinely new empty QA environment:

```bash
uv run --project services/api python deploy/qa.py \
  --config infra/config/qa.local.json --profile your-qa-profile \
  --gate-evidence /protected/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /protected/release-public.pem \
  --signing-key /protected/release-private.pem --establish-new
```

The command verifies account/release/TLS/database/cost inputs, bootstraps CDK and registry, builds/signs the exact service, drains an existing rollout, deploys infrastructure with services stopped, verifies the independent journal, runs migrations and admission, builds/signs the actual environment web export, activates healthy services, publishes dependency bytes before index, invalidates CloudFront and checks public HTTPS bytes/full security policy/deep-link/missing-asset/API readiness. CDK supplies VPC/security groups, private RDS/services, IAM/KMS, S3/SQS/Cognito, TLS/public routing, monitoring and budgets.

Use establish-new only for a first empty environment. Existing deployment/recovery must preserve its journal and use the documented migration/admission/restore sequence. The final receipt contains actual resource/public identities, service/web release paths, maintenance/publication evidence and web_origin. It explicitly does not report authenticated customer/physical/scientific acceptance as executed. Perform actual QA tests and have the independent authority sign their real protected results before production.

## A separate command promotes production

```bash
uv run --project services/api python deploy/prod.py \
  --config infra/config/prod.local.json --profile your-prod-profile \
  --source-config /protected/qa/stopped.local.json \
  --source-release /protected/qa/service-release.json \
  --source-web-release /protected/qa/web-release.json \
  --source-web-artifact /protected/qa/web.zip --source-profile your-qa-profile \
  --qa-evidence /protected/qa-validation-signed.json \
  --gate-evidence /protected/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /protected/release-public.pem \
  --signing-key /protected/release-private.pem --establish-new
```

Use the actual paths from the successful QA attempt. Production verifies a different target account, current signed QA approval and the exact QA service/source/web binding. It copies the admitted service digest rather than rebuilding it; production web bytes use the same reviewed source with fixed production identity. Use establish-new only for the first empty production deployment.

Each invocation preserves prior records and writes stage/failure state under .local/deploy/environment/commit/attempt-id. A later failure does not imply backend activation or uploaded bytes were rolled back. Inspect the protected deployment-state.json, actual receipts and task logs; follow [deploy/README.md](../deploy/README.md) and [operations](../infra/runbooks/OPERATIONS.md) before retry/rollback/recovery.

## Register the UI CNAME

Managed same-account public Route 53 DNS is recommended for the one-shot custom web name. Otherwise register DNS after distribution/TLS admission before public access can verify; an initially failed public-check attempt remains recorded. Register the name and rerun verified access rather than calling that failed attempt successful.

Preview validates actual AWS distribution, private regional S3/OAC/release route, alias, certificate, owned public zone and current records:

```bash
AWS_PROFILE=your-qa-profile uv run --project services/api python deploy/register_cname.py \
  --config /protected/qa/stopped.local.json --release /protected/qa/service-release.json \
  --gate-evidence /protected/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /protected/release-public.pem --hosted-zone-id YOUR_ACTUAL_PUBLIC_ZONE
```

Add --apply to create an absent record. Its successful change observation must occur within ten minutes; AWS SDK socket/retry timeouts can delay failure reporting. A timeout does not imply cancellation or rollback. Production also requires --qa-evidence. An exact existing target is an observed no-op. Apex/private/foreign zones, disabled/foreign routes, pending TLS and conflicting records fail; a record created concurrently cannot be overwritten because the operation uses CREATE. DNS propagation is not authenticated UI acceptance.

## Install native apps through Apple/Google

Use the separate real-device store tooling and [STORE_RELEASE.md](../apps/mobile/STORE_RELEASE.md), not guest APK/simulator files. The owner supplies actual Expo project/access, Apple Developer/App Store Connect and Google Play identities, application records, signing/provisioning and applicable agreements/testing/first-upload requirements.

The [Python store helper](../apps/mobile/modules/scripts/store_release.py) accepts an explicit platform and nonsecret external configuration. Review the intended stages without network/build/submission:

```bash
uv run --project services/api python apps/mobile/modules/scripts/store_release.py \
  plan --config /protected/store-prod.json --platform ios
```

Build with real project/signing access, exact admitted backend and current evidence; substitute android for ios to produce the Android store candidate:

```bash
uv run --project services/api python apps/mobile/modules/scripts/store_release.py \
  build --config /protected/store-prod.json --platform ios \
  --backend-config infra/config/prod.local.json \
  --backend-release /protected/prod/service-release.json \
  --gate-evidence /protected/gates-REVIEWED_COMMIT.json \
  --trusted-public-key /protected/release-public.pem \
  --qa-evidence /protected/qa-validation-signed.json \
  --signing-key /protected/release-private.pem --output /protected/store-build.json
```

The same authority/backend flags apply to submit, plus --receipt /protected/store-build.json and a new output path. It submits the exact provider build UUID from that signed receipt, never latest, and retains a signed intent before upload. An uncertain/interrupted upload cannot be blindly repeated; the documented submission-ID reconciliation queries the exact existing submission instead of uploading again. Status takes the signed build receipt and trusted public key; an optional signed submission receipt supplies the exact accepted submission identity. Read the platform-specific credential, artifact inspection and reconciliation details before invoking those operations. Genuine signing/processing is not demonstrated by software fixtures.

iPhone beta testers install Apple's TestFlight app and accept the real invitation after the signed iOS build finishes processing. Android testers join the actual internal Play test and install through its Play link. Public App Store/Play downloads require actual approved publication. The Python helper can plan, build, inspect, submit and report observed provider status; it does not purchase enrollment, create an approval or turn request acceptance into public availability. No store URL is supplied until one exists.

## Operate mobile builds from the browser

The optional [mobile-store-release.yml](../.github/workflows/mobile-store-release.yml) runs on macOS through GitHub Actions after the workflow is registered on default main. Create and actually protect the store-qa/store-prod environments, bind their intended AWS OIDC roles and genuine Expo/store/release inputs, then use Actions → Manual mobile store release → Run workflow. No environment protection, account role or store enrollment is created by committing this file.

Select plan, build, reconcile or status, platform and environment explicitly. Plan makes no cloud/store call. Build performs exact-source admission and native device/signature inspection. Status reads the selected signed candidate. Reconcile is read-only: it requires the original signed pending intent, exact candidate build UUID and existing provider submission UUID. Fresh upload from an ephemeral runner is refused before private credential staging or AWS/EAS/store action; GitHub artifact metadata may be read during admission. Initial submission uses persistent protected operator storage, including a separately provisioned hosted Mac for iOS.

The protected STORE_RELEASE_INPUTS JSON has exactly nine keys: schema_version, store_config, backend_config, backend_release, gate_evidence, trusted_public_key, release_signing_key, platform_credentials and qa_approval. Unused values are null. Its configuration uses null credential/bundletool file selectors; the materializer supplies fixed private runner paths for only the selected operation. Credentials and signing keys belong in environment secrets, not dispatch fields, repository files or logs. EXPO_TOKEN authenticates the actual Expo project. STORE_AWS_ROLE_ARN is the intended account-bound protected environment variable; build and reconciliation authenticate only that account.

STORE_RECEIPT_KEY is a separate securely generated base64 encoding of 32 random bytes, retained in the protected environment. The workflow publishes only an authenticated encrypted receipt bundle, preserving original signed bytes and binding repository/source/environment/platform. Later status/reconciliation takes its numeric receipt_artifact_id and exact candidate_build_id; submission_id selects the existing submission. Missing/foreign/malformed/expired artifacts refuse rather than falling back to latest or plaintext input. Preserve the encrypted artifact and its key before the seven-day GitHub retention expires. No native store binary, plaintext receipt, operator bundle or key is uploaded as a public repository artifact. The workflow has not been executed with real external credentials here.

For an original pending intent retained by the persistent operator, the mutation-free [store_inputs.py](../apps/mobile/modules/scripts/store_inputs.py) pack command supplies the encrypted transfer. With STORE_RECEIPT_KEY securely configured and an existing owned, canonical transfer directory, run:

```bash
RUNNER_TEMP=/protected/operator-transfer uv run --project services/api python \
  apps/mobile/modules/scripts/store_inputs.py pack \
  --config /protected/store-prod.json --build-receipt /protected/store-build.json \
  --submission-intent /protected/store-submission.json.intent.json \
  --trusted-public-key /protected/release-public.pem \
  --environment prod --platform ios --revision REVIEWED_40_HEX_COMMIT
```

Each selected source is a stable owner-only regular file. Add --submission-receipt only for an actual signed completed outcome. Packing validates original signatures, scope and byte links without AWS/EAS/store calls; it prints only the new private ciphertext file's path. Place that file's UTF-8 encrypted JSON in the protected STORE_RECEIPT_PACKAGE secret, leave receipt_artifact_id blank and select the exact candidate/submission UUIDs. The two input selectors are mutually exclusive. Packages above 48 KiB refuse rather than dropping evidence. Original operator receipts remain on persistent storage; packing does not create or repeat an upload.

## Tests, specifications and evidence

[CI_GATES.md](CI_GATES.md) defines strict greater-than-80-percent Python/mobile inventories, actual ATDD/components/performance/PostgreSQL, all five healthy canonical services plus two successful initializers, real LocalStack HTTP/S3/SQS/worker/API/privacy and native/firmware/guest checks. All seven local categories and all thirteen GitHub jobs must pass for frozen source, with no mandatory skips. Workflow YAML does not enforce merges; actual main rules must require merge-gate, including administrators.

The [release/browser OpenSpec delta](../openspec/changes/verified-release-and-browser-access/proposal.md) describes each new boundary and positive/refusal scenario. [Alignment audit](REQUIREMENTS_ALIGNMENT_AUDIT.md) records existing customer/scientific scope and adversarial findings. The current product is not fully qualified: genuine instrument interfaces, hardware/safety/assay/study/model evidence, actual cloud acceptance, hosted launch, store publication and verified merge enforcement remain distinct outstanding requirements.
