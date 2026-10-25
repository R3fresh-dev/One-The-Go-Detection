# OTGD-046: verification plan

Canonical: `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md`; SHA-256 `1a331132cf6b66413d1705dc09d0c7f885b8fe1375ea72250dcd5a451162e241`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/hosted-preview.spec.ts` — `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`
- `apps/mobile/tests/hosted-preview.test.ts` — `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`
- `infra/test/test_codespaces_preview.py` — `86bf9b8b88e96ca030d5c148d2d46b8fe764ae7a610351704ae419fda759fd28`
- `infra/test/test_hosted_preview.py` — `7d44b7bd8f5482bf65109d9002908eefa2ee480b8eba524ab4fe3a24b240d8ce`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### PREVIEW-001 — Build an isolated fixed-origin guest export

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md` / `PREVIEW-001`.

Prerequisites and limits: NOT_RUN hosted-native workflow artifacts and current provenance; BLOCKED actual hosting/vendor account/session without authority. A local guest export does not prove hosted launch.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-046-PREVIEW-001-01 | Ambient production values are present — **GIVEN** a host or dotenv containing production API/OAuth configuration **WHEN** the preview is prepared **THEN** only explicit guest configuration enters its separate bundle. | `apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records<br>`apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-046-PREVIEW-001-02 | An ordinary export also exists — **GIVEN** dist and dist-preview from different modes **WHEN** the preview starts **THEN** the guest server uses only dist-preview and its matching manifest. | `apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service<br>`apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### PREVIEW-002 — Verify the correct preview before reuse

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md` / `PREVIEW-002`.

Prerequisites and limits: NOT_RUN hosted-native workflow artifacts and current provenance; BLOCKED actual hosting/vendor account/session without authority. A local guest export does not prove hosted launch.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-046-PREVIEW-002-01 | A correct private guest server is already running — **GIVEN** matching prepared guest bytes/manifest on the forwarded port **WHEN** post-start runs again **THEN** it reuses the verified server without duplicate processes. | `infra/test/test_codespaces_preview.py:134` — test_current_export_is_accepted_and_repeat_start_reuses_only_matching_guest<br>`apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-046-PREVIEW-002-02 | A foreign service occupies the port — **GIVEN** ordinary/unrelated HTTP 200 content or a missing guest export **WHEN** post-start runs **THEN** it refuses readiness and preserves the unrelated service. | `apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service<br>`infra/test/test_codespaces_preview.py:181` — test_generic_http_200_is_not_reused_or_stopped_by_startup | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `200`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### PREVIEW-003 — Document actual click-only hosting boundaries

Normative acceptance source: `openspec/changes/verified-release-and-browser-access/specs/fictional-browser-preview/spec.md` / `PREVIEW-003`.

Prerequisites and limits: NOT_RUN hosted-native workflow artifacts and current provenance; BLOCKED actual hosting/vendor account/session without authority. A local guest export does not prove hosted launch.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-046-PREVIEW-003-01 | A user has the supported service account — **GIVEN** the reviewed branch and successful source-bound guest artifacts **WHEN** the documented browser hosting steps are followed **THEN** no local clone/build commands are needed to explore the fictional UI. | `apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service<br>`apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-046-PREVIEW-003-02 | No hosting access exists — **GIVEN** no managed forwarding capability, existing Codespace or Appetize credentials **WHEN** delivery is reported **THEN** it supplies setup/artifacts and concrete account steps without claiming a launched session. | `apps/mobile/tests/hosted-preview.test.ts:11` — hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service<br>`apps/mobile/e2e/hosted-preview.spec.ts:3` — standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
