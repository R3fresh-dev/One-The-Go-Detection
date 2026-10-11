# Required merge checks

The required status is **`merge-gate`**, produced by [merge-gate.yml](../.github/workflows/merge-gate.yml). It runs on every pull request targeting `main`, every push to `main`, and merge-queue revisions. There are no path filters. A failed, skipped or cancelled mandatory job blocks the aggregate status.

The workflow calls [platform.yml](../.github/workflows/platform.yml) and [native-build.yml](../.github/workflows/native-build.yml). Standalone manual runs of those workflows do not satisfy the aggregate. Source changes require fresh checks; earlier passing runs are historical evidence.

| Requirement | Executed check |
|---|---|
| Unit coverage strictly above 80% | Every `otgd` Python module and the shared scientific `spec_validation` module, plus every executable mobile `src/**/*.ts` business module, including unloaded native adapters. The Python and mobile inventories must independently exceed 80%; rounded percentages cannot satisfy the boundary. Infrastructure operational unit tests also run. |
| ATDD | Playwright journeys against a fresh production export of `apps/mobile`, at phone and desktop sizes. |
| Components | Actual browser DOM interactions, accessibility and confirmation/privacy behavior, separately selected from the ATDD file. |
| Performance | Forty signed workflows across twenty fictional identities against the running API, PostgreSQL, S3/SQS and worker. All 400 measured writes must succeed; p95 must be below 1,000 ms and p99 below 2,000 ms; each queued result has a fifteen-second deadline. |
| Live dependencies | The complete API suite against disposable PostgreSQL 16, including concurrency cases, followed by repeat migrations and runtime-role privilege denial checks. |
| Docker health | All five long-running services healthy; resource initialization and migration exited zero. Worker health requires recent progress on every operational channel. |
| LocalStack APIs | Actual versioned/conditional S3 and SQS probes, repeat bootstrap, PKCE sign-in, immutable evidence/finalize replay, queued result, authenticated export and deletion/ownership denial requests. |
| Additional required checks | Contracts/OpenSpec/schema drift, CDK assertions, Android module tests and both APK builds, Swift golden tests and complete iOS simulator build, actual Nano ESP32 firmware compile. |

Mobile TSX views are covered by the separate browser component/journey checks; the TypeScript unit percentage measures the explicitly reported business-module inventory. Native, firmware and infrastructure coverage percentages are not inferred from Python or TypeScript coverage. Software checks do not establish AWS network/IAM/KMS behavior, physical-phone timing, qualified sensing or clinical model validity.

`scripts/ci_gate.py` is the shared local/CI entry point. Test reports are removed before execution. Mandatory JUnit tests must exist and have no failure, error or skipped cases. The infrastructure runner also rejects zero tests, skips, expected failures and unexpected successes. Mobile coverage rejects skipped/cancelled/TODO tests and records its source inventory. GitHub uploads current coverage, JUnit, browser and performance evidence as artifacts.

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

Provide `OTGD_DATABASE_URL` pointing to a **separate disposable PostgreSQL test database**, `OTGD_ENVIRONMENT=test`, `OTGD_DISPOSABLE_DATABASE=true`, its `OTGD_DATABASE_NAME`, test runtime-role user/password and a test `OTGD_TOMBSTONE_KEY` before the live-dependency check. The suite recreates its test schema. Never point it at the application's persistent database. The GitHub workflow supplies an isolated service and fictional fixture credentials.

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
