# OTGD-030: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md`; SHA-256 `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/components.spec.ts` — `725effb97f2e9195340fd6370b8491065eabdf849ce5c5680974c39cc2125c53`
- `apps/mobile/e2e/mobile.spec.ts` — `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`
- `apps/mobile/tests/controller.test.ts` — `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92`
- `apps/mobile/tests/domain.test.ts` — `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`
- `apps/mobile/tests/hosted-preview.test.ts` — `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`
- `apps/mobile/tests/workspace-scope.test.ts` — `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-ONB-001 — Accurate first-run scope

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md` / `AND-ONB-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-030-AND-ONB-001-01 | onb-first-launch-demo — **GIVEN** a fresh installation without preferences **WHEN** the user selects Explore the demo **THEN** the introduction identifies synthetic sample/sensor values and does not display a probability or create a research enrollment. | `apps/mobile/tests/controller.test.ts:185` — a consent receipt for another document or timestamp is never accepted as research authorization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-001-02 | onb-signed-in-still-measurement-only — **GIVEN** an authenticated account with no study authorization **WHEN** onboarding completes **THEN** the dashboard shows measurement-only availability and no study capability is inferred from the account or notice receipt. | `apps/mobile/tests/controller.test.ts:185` — a consent receipt for another document or timestamp is never accepted as research authorization<br>`apps/mobile/e2e/mobile.spec.ts:6` — guest completes a measurement-only check, exact export and privacy/settings journey | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-001-03 | onb-research-configuration-cannot-change-release — **GIVEN** an authenticated account and a valid-looking research manifest **WHEN** onboarding or public configuration reports research availability **THEN** the release retains inference_available=false and displays no probability or research-estimate capability. | `apps/mobile/tests/domain.test.ts:323` — every research_estimate is rejected even when its shape could be schema-valid<br>`apps/mobile/tests/controller.test.ts:353` — delayed history cannot enter another account or reopen a signed-out workspace | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ONB-002 — Explicit workspace isolation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md` / `AND-ONB-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-030-AND-ONB-002-01 | onb-demo-does-not-upload — **GIVEN** a completed demo check and a subsequently authenticated account **WHEN** the user opens the account workspace **THEN** demo history is absent from account history and no upload request for the demo check is enqueued. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-002-02 | onb-cancel-workspace-switch — **GIVEN** an unfinished demo check **WHEN** the user selects Sign in and then Stay in check **THEN** the check remains visible with unchanged identity and no authentication browser is opened; if a native run had already ended to leave capture, it remains ended with that fact displayed. | `apps/mobile/e2e/mobile.spec.ts:227` — profile errors remain actionable and browser reload never pretends encrypted persistence<br>`apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-002-03 | onb-guest-demo-never-has-upload-path — **GIVEN** a guest demo check and an authenticated local/QA synthetic project both exist **WHEN** the user opens the guest check, signs in, or reconnects **THEN** the guest check remains local and has no upload action; a separate account-owned synthetic fixture requires its own creation and upload choice. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ONB-003 — Versioned notice acknowledgment

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md` / `AND-ONB-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-030-AND-ONB-003-01 | onb-notice-accepted-once — **GIVEN** the current notice is visible and its checkbox is initially unchecked **WHEN** the user checks it and selects Continue **THEN** one dated receipt is saved, the dashboard opens, and repeating the submission creates no duplicate receipt. | `apps/mobile/tests/controller.test.ts:324` — notice acknowledgment is explicit and keeps the exact displayed version through account synchronization<br>`apps/mobile/tests/domain.test.ts:454` — privacy jobs keep deletion-only and export-only terminal states separate | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-003-02 | onb-stale-notice-write — **GIVEN** the server requires a newer notice than the bundled accepted version **WHEN** the app attempts an account write **THEN** the write remains pending, the app offers the newer notice, and neither a fabricated acknowledgment nor a research-consent record is sent. | `apps/mobile/tests/controller.test.ts:324` — notice acknowledgment is explicit and keeps the exact displayed version through account synchronization<br>`apps/mobile/tests/domain.test.ts:454` — privacy jobs keep deletion-only and export-only terminal states separate | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ONB-004 — Permission timing and offline entry

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md` / `AND-ONB-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-030-AND-ONB-004-01 | onb-airplane-mode-demo — **GIVEN** the phone is offline on first launch **WHEN** the user completes demo onboarding **THEN** the dashboard and synthetic check are usable and the UI describes their local state. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-004-02 | onb-no-permission-prompts — **GIVEN** every OS permission is denied **WHEN** all onboarding screens are traversed **THEN** no permission dialog appears and onboarding is not blocked by those denials. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ONB-005 — Restart-safe progression

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md` / `AND-ONB-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-030-AND-ONB-005-01 | onb-kill-before-commit — **GIVEN** acknowledgment persistence has not completed **WHEN** the process is terminated and relaunched **THEN** the notice remains unacknowledged and no account write is sent. | `apps/mobile/tests/controller.test.ts:77` — a delayed old-account logout cannot open provider logout or replace the new-account screen<br>`apps/mobile/e2e/mobile.spec.ts:227` — profile errors remain actionable and browser reload never pretends encrypted persistence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-005-02 | onb-kill-after-commit — **GIVEN** the acknowledgment transaction completed before process termination **WHEN** the app relaunches **THEN** the chosen workspace opens with the existing receipt and no duplicate onboarding event. | `apps/mobile/tests/controller.test.ts:77` — a delayed old-account logout cannot open provider logout or replace the new-account screen<br>`apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ONB-006 — Accessible introduction and parity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md` / `AND-ONB-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-030-AND-ONB-006-01 | onb-talkback-and-large-text — **GIVEN** TalkBack and 200% font scaling are enabled on a 360 dp-wide Android screen **WHEN** the user traverses welcome and the notice **THEN** each action is reachable, its role/label is announced, and scrolling exposes the entire notice and Continue control. | `services/api/tests/test_api.py:106` — test_notice_exact_text_hash | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-030-AND-ONB-006-02 | onb-ios-parity — **GIVEN** a fresh iOS installation with Reduce Motion enabled **WHEN** demo onboarding completes using VoiceOver **THEN** the same workspace and notice states are stored without required animation or a camera/Bluetooth prompt. ## Acceptance evidence Required artifacts: Android/iOS first-run and returning-run UI tests; offline demo test; network assertion showing zero onboarding sensor/research calls; crash-boundary persistence tests; version-mismatch API test; screenshots at standard and 200% text size; TalkBack/VoiceOver manual checklist. A specification, screenshot, or passing onboarding test is not evidence that G-01–G-14 scientific/product gates have closed. | `services/api/tests/test_api.py:106` — test_notice_exact_text_hash<br>`apps/mobile/tests/hosted-preview.test.ts:65` — network-disabled API transport refuses even explicitly supplied credentials and cloud downloads | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `200`, `44`, `48`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Permissions race and no-reprompt assertion audit

Mapped existing cases: OTGD-036-AND-SET-003-01/02 and AND-SET-007-02; related AND-EYE-002, AND-ONB-004 and AND-AUTH-005.

Assertion adequacy inspected: Read PermissionsCard implementation and actual exported Settings component harness. Status labels cover denied/canAskAgain, denied/permanent, restricted, undetermined, failed reads; zero prompts across mount/refresh/active-return; OS settings call occurs once only explicit action. Deferred reads resolved newer-first, stale controller epoch before React render, account/generation changes and unmount must not publish old state; new scoped card is Not checked until current read; listener teardown asserted. Real ordinary UI test Settings/Back preserves draft/sample with no camera prompt. Implementation uses active+sequence+captured epoch guard and scoped card identity.

Remaining limits: Adapters are controlled OS observations. Real Android/iOS settings return, OS permission policy, TalkBack/VoiceOver, key storage and native lifecycle remain Task7 BLOCKED/NOT_RUN. Writer not released; no final gate execution or independent runtime PASS.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.
