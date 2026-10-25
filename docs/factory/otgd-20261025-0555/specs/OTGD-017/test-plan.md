# OTGD-017: verification plan

Canonical: `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md`; SHA-256 `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/hosted-preview.spec.ts` — `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`
- `apps/mobile/tests/hosted-preview.test.ts` — `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`
- `infra/test/test_hosted_preview.py` — `7d44b7bd8f5482bf65109d9002908eefa2ee480b8eba524ab4fe3a24b240d8ce`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-PREV-001 — Accept fictional hosted mode only in local builds

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md` / `AND-PREV-001`.

Prerequisites and limits: NOT_RUN hosted-native workflow artifacts and current provenance; BLOCKED actual hosting/vendor account/session without authority. A local guest export does not prove hosted launch.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-017-AND-PREV-001-01 | Production enables the preview flag — **GIVEN** APP_ENV=prod **WHEN** the hosted preview flag is true **THEN** configuration fails before building application code. | `apps/mobile/tests/hosted-preview.test.ts:93` — the hosted preview build flag is local-only and cannot alter QA or production account behavior<br>`infra/test/test_hosted_preview.py:194` — test_prepare_requires_guarded_environment_clean_source_and_actual_expo_flag | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-017-AND-PREV-001-02 | An isolated local preview is packaged — **GIVEN** APP_ENV=local and the matching compiled public environment **WHEN** the hosted flag is accepted and the reviewed workflow packages the app **THEN** its bundle and platform metadata identify fictional hosted mode and account and real acquisition services remain disabled. | `apps/mobile/tests/hosted-preview.test.ts:93` — the hosted preview build flag is local-only and cannot alter QA or production account behavior<br>`infra/test/test_hosted_preview.py:194` — test_prepare_requires_guarded_environment_clean_source_and_actual_expo_flag | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PREV-002 — Disable every account and real acquisition path

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md` / `AND-PREV-002`.

Prerequisites and limits: NOT_RUN hosted-native workflow artifacts and current provenance; BLOCKED actual hosting/vendor account/session without authority. A local guest export does not prove hosted launch.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-017-AND-PREV-002-01 | A customer saves a browser example — **GIVEN** the standalone fictional preview **WHEN** the customer acknowledges the notice, confirms context and saves a check **THEN** the UI shows a measurement-only fictional record with no account, sensor or upload calls. | `apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records<br>`apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-017-AND-PREV-002-02 | A credential or hardware path is invoked directly — **GIVEN** the standalone fictional preview **WHEN** a caller attempts sign-in, credential recovery, API download, Bluetooth discovery or native reaction acquisition **THEN** the request is refused before network or hardware access and no fictional record is promoted to a measurement. | `apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records<br>`apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PREV-003 — Isolate guest records and explain persistence

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md` / `AND-PREV-003`.

Prerequisites and limits: NOT_RUN hosted-native workflow artifacts and current provenance; BLOCKED actual hosting/vendor account/session without authority. A local guest export does not prove hosted launch.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-017-AND-PREV-003-01 | The browser reloads after saving an example — **GIVEN** a fictional saved browser check **WHEN** the page reloads **THEN** its records and acknowledgment disappear and the first-use fictional flow returns. | `apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service<br>`apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-017-AND-PREV-003-02 | A guest example is selected for account upload — **GIVEN** a saved check in the isolated fictional guest namespace **WHEN** a caller attempts account migration, import or upload **THEN** the operation is refused and the account namespace receives no guest data. | `apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records<br>`apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.


## Final corrected source evidence — e89897cc852a

# OTGD-017 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md`; SHA256 `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-017/test-plan.md`. External review artifact only; PM controls import.

All 6 stable cases / 3 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-017-AND-PREV-001-01 | Production enables the preview flag — - **GIVEN** APP_ENV=prod - **WHEN** the hosted preview flag is true - **THEN** configuration fails before building application code. | PASS |
| OTGD-017-AND-PREV-001-02 | An isolated local preview is packaged — - **GIVEN** APP_ENV=local and the matching compiled public environment - **WHEN** the hosted flag is accepted and the reviewed workflow packages the app - **THEN** its bundle and platform metadata identify fictional hosted mode and account and real acquisition services remain disabled. | PARTIAL |
| OTGD-017-AND-PREV-002-01 | A customer saves a browser example — - **GIVEN** the standalone fictional preview - **WHEN** the customer acknowledges the notice, confirms context and saves a check - **THEN** the UI shows a measurement-only fictional record with no account, sensor or upload calls. | PASS |
| OTGD-017-AND-PREV-002-02 | A credential or hardware path is invoked directly — - **GIVEN** the standalone fictional preview - **WHEN** a caller attempts sign-in, credential recovery, API download, Bluetooth discovery or native reaction acquisition - **THEN** the request is refused before network or hardware access and no fictional record is promoted to a measurement. | PASS |
| OTGD-017-AND-PREV-003-01 | The browser reloads after saving an example — - **GIVEN** a fictional saved browser check - **WHEN** the page reloads - **THEN** its records and acknowledgment disappear and the first-use fictional flow returns. | PASS |
| OTGD-017-AND-PREV-003-02 | A guest example is selected for account upload — - **GIVEN** a saved check in the isolated fictional guest namespace - **WHEN** a caller attempts account migration, import or upload - **THEN** the operation is refused and the account namespace receives no guest data. | PARTIAL |
