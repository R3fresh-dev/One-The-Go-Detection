# Required merge checks

The required status is **`merge-gate`**, produced by [merge-gate.yml](../.github/workflows/merge-gate.yml). It runs on every pull request targeting `main`, every push to `main`, and merge-queue revisions. There are no path filters. A failed, skipped or cancelled mandatory job blocks the aggregate status.

The workflow calls [platform.yml](../.github/workflows/platform.yml), [native-build.yml](../.github/workflows/native-build.yml) and [hosted-native-preview.yml](../.github/workflows/hosted-native-preview.yml). The guarded Android and iOS guest-preview builds must also pass before the aggregate succeeds. Standalone manual runs of those workflows do not satisfy the aggregate. Source changes require fresh checks; earlier passing runs are historical evidence.

| Requirement | Executed check |
|---|---|
| Unit coverage strictly above 80% | Every `otgd` Python module, shared scientific `spec_validation`, executable `tools/model_evaluation.py`, and the native store release/input helpers, plus every executable mobile `src/**/*.ts` business module, including unloaded native adapters. Python and mobile inventories independently exceed 80%; each store helper also independently exceeds 80% with zero excluded statements. Missing helper coverage fails even if the aggregate passes. Infrastructure operational unit tests also run, with each serverless caller, gate-admission, initial-recovery and template module independently above 80% and no excluded statements. |
| ATDD | Playwright journeys against a fresh production export of `apps/mobile`, at phone and desktop sizes, plus a separately built hosted-preview export proving its guest-only boundary and reload behavior. |
| Components | Actual browser DOM interactions, accessibility, confirmation/privacy behavior and optional raw-recording screens, separately selected from the ATDD files. |
| Performance | Forty signed workflows across twenty fictional identities against the running API, PostgreSQL, S3/SQS and worker. All 400 measured writes must succeed; p95 must be below 1,000 ms and p99 below 2,000 ms; each queued result has a fifteen-second deadline. |
| Live dependencies | The complete API suite against disposable PostgreSQL 16, including concurrency cases, followed by repeat migrations and runtime-role privilege denial checks. |
| Docker health | All five long-running services healthy; resource initialization and migration exited zero. Worker health requires recent progress on every operational channel. |
| LocalStack APIs | Actual versioned/conditional S3 and SQS probes, repeat bootstrap, PKCE sign-in, immutable evidence/finalize replay, queued result, authenticated export and deletion/ownership denial requests; exact raw-version erasure, delete-marker limitations, unchanged neighbors and late-arrival reconciliation. The participant probe additionally exercises instruction acknowledgment, collection without BLE, delegated staff PDF custody through an actual conditional/versioned S3 upload, laboratory import, participant refresh/finalization and the real SQS worker. |
| Additional required checks | Contracts/OpenSpec/schema drift including all canonical follow-up changes, CDK assertions, Android module tests and both APK builds, Swift golden tests and complete iOS simulator build, portable signed-reader tests, actual Nano ESP32 synthetic/signed reader firmware compiles and the actual security-enabled ESP-IDF reader branch. The latter uses a fictional ephemeral boot-signing key and performs no hardware provisioning. |

Mobile TSX views are covered by the separate browser component/journey checks; the TypeScript unit percentage measures the explicitly reported business-module inventory. Native, firmware and infrastructure coverage percentages are not inferred from Python or TypeScript coverage. Software checks do not establish AWS network/IAM/KMS behavior, physical-phone timing, qualified sensing or clinical model validity.

The required platform job validates all twelve canonical OpenSpec changes, including `serverless-development-runtime`. Serverless control/lifecycle/worker modules are part of the full Python coverage inventory; caller, template, workflow and protocol refusal/interleaving regressions also run in the infrastructure suite. These checks exercise software contracts. They do not qualify a live Aurora/Lambda deployment or replace the separate canonical QA/prod restore and promotion evidence.

The separate infrastructure coverage report inventories `deploy/serverless.py`, `serverless_gates.py`, `serverless_recovery.py` and `serverless_template.py`. Each module must independently exceed 80% with zero excluded statements; this report is not folded into or substituted for backend/store coverage. Discovery and all actual infrastructure cases run under the collector.

The Python unit inventory explicitly includes `apps/mobile/modules/scripts/store_release.py` and `store_inputs.py`. API store-tool tests and `infra/test/test_store_inputs.py` exercise their actual implementation; no source exclusions or aggregate-only allowance can hide an untested release helper. The optional manual store workflow performs real billable/signing/submission actions only with genuine protected inputs and is not a pull-request job or evidence that an app is published.

`scripts/ci_gate.py` is the shared local/CI entry point. Test reports are removed before execution. Mandatory JUnit tests must exist and have no failure, error or skipped cases. The infrastructure runner also rejects zero tests, skips, expected failures and unexpected successes. Mobile coverage rejects skipped/cancelled/TODO tests and records its source inventory. GitHub uploads current coverage, JUnit, browser and performance evidence as artifacts.

SwiftPM's XCTest XML is generated through its parallel runner with one worker. The native gate preserves the test process exit status and checks every XML case against the actual verbose XCTest start/pass log, rejecting skips and expected failures. Both files are uploaded; a missing report cannot count as a passing native test run.

## Run locally

Use the canonical application directories: `services/api`, `apps/mobile`, `infra` and `deploy`.

```bash
uv sync --project services/api --locked
npm ci --prefix apps/mobile
npm ci --ignore-scripts --prefix infra
npm run typecheck --prefix apps/mobile
npm run export:web --prefix apps/mobile
cd apps/mobile
npx playwright install --with-deps chromium
cd ../..
python scripts/local-platform.py prepare
python scripts/local-platform.py up
```

The default emulator is the pinned Apache-2.0 LocalStack 4.14.0 release, which requires no subscription. The explicit licensed alternative is documented in [infra/README.md](../infra/README.md). Preserve existing volumes; never reset a database to hide a failed check. `localstack-api` deletes only the explicitly fictional local Account A workspace.

The additional [participant probe](../infra/local/participant_probe.py) runs inside the maintenance container with `--confirm-fictional-workspace`. It requires the exact local PostgreSQL/Compose and loopback public endpoints, creates UUID-namespaced fictional registry/session/sample records under two dedicated local identities, and preserves existing records and journal anchors. Three distinct local engineering principals execute the registry decisions; these are software fixtures, not human-study or assay approvals. The dedicated staff role preserves prior scopes and stops explicitly at its 64-study limit. No worker or storage operation is mocked. Run it only in an authorized fictional local workspace; it is not an AWS production provisioning command.

Provide `OTGD_DATABASE_URL` pointing to a **separate disposable PostgreSQL test database**, `OTGD_ENVIRONMENT=test`, `OTGD_DISPOSABLE_DATABASE=true`, its `OTGD_DATABASE_NAME`, test runtime-role user/password and a test `OTGD_TOMBSTONE_KEY` before the live-dependency check. The suite recreates its test schema. Never point it at the application's persistent database. The GitHub workflow supplies an isolated service and fictional fixture credentials.

The shared gate removes the caller's `OTGD_TOMBSTONE_KEY` only when launching retained local Compose checks, including their nested scripts and performance command. Compose otherwise gives that disposable test key precedence over `infra/local/.env`, breaking the retained identity anchor and maintenance account lookup. The protected local `.env` remains the authority for those commands; Docker configuration, proxy settings and supported local origin/password overrides are preserved. Disposable database test commands keep their test key.

```bash
python scripts/ci_gate.py unit-coverage
python scripts/ci_gate.py atdd
python scripts/ci_gate.py components
python scripts/ci_gate.py live-dependencies
python scripts/ci_gate.py docker-health
python scripts/ci_gate.py localstack-api
python scripts/ci_gate.py performance
python scripts/run_all_gates.py
```

The combined runner writes `reports/local-gates.json` only with the checks actually completed, binds it to HEAD and the full source fingerprint, and rejects source changes during execution. Local reports do not prove GitHub enforcement or replace the signed release's trusted GitHub run provenance.

## Enforce merges

The workflow must be paired with actual GitHub protection. A YAML file alone does not prevent a merge.

```bash
python scripts/configure_merge_protection.py
python scripts/configure_merge_protection.py --apply
```

The first command shows the proposed policy. The second reads existing protections, preserves additional required checks and review requirements, requires the GitHub Actions `merge-gate` check with an up-to-date branch, enforces administrators, dismisses stale approvals, and prohibits force pushes/deletion. It then reads back and verifies the settings. Existing review bypass allowances are preserved and must be reviewed separately if configured.

`--apply` uses the securely supplied `GH_ADMIN_TOKEN` when present and requires repository **Administration: read and write** permission. It never prints the token. HTTP 403 is a failure, not evidence of an unprotected or successfully configured branch. Do not report merge enforcement complete until read-back succeeds and the exact revision's aggregate Actions run is green.

Production release admission additionally verifies the trusted repository/workflow/latest GitHub run and every mandatory nested job, immutable source/image binding, and independently signed, expiring QA acceptance. It does not accept a hand-edited local JSON claim as passing CI or QA evidence. See [deploy/README.md](../deploy/README.md).
