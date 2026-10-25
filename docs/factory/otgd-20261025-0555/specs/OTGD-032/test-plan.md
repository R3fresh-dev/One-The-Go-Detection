# OTGD-032: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md`; SHA-256 `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/components.spec.ts` — `725effb97f2e9195340fd6370b8491065eabdf849ce5c5680974c39cc2125c53`
- `apps/mobile/tests/controller.test.ts` — `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92`
- `apps/mobile/tests/domain.test.ts` — `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`
- `apps/mobile/tests/profile-form.test.ts` — `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-PRO-001 — Optional values and explicit missingness

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` / `AND-PRO-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-032-AND-PRO-001-01 | pro-empty-profile-save — **GIVEN** an account profile with no provided fields **WHEN** the user saves without entering optional context **THEN** numeric values remain null and no default cannabis exposure or baseline is created. | `apps/mobile/tests/profile-form.test.ts:56` — optional blank demographics stay null and unknown remains distinct from declined<br>`apps/mobile/tests/domain.test.ts:117` — duplicate escaped keys, unknown numeric values and excessive JSON depth are rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-001-02 | pro-declined-history — **GIVEN** last use is set to Prefer not to say **WHEN** the profile is saved and reloaded **THEN** the declined marker persists and its timestamp remains null. | `apps/mobile/tests/profile-form.test.ts:56` — optional blank demographics stay null and unknown remains distinct from declined<br>`apps/mobile/tests/domain.test.ts:152` — check freezes original profile timestamp and recomputes elapsed use at its start | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRO-002 — Deterministic units and validation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` / `AND-PRO-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-032-AND-PRO-002-01 | pro-imperial-bmi — **GIVEN** the user enters 5 feet 10 inches and 180 pounds **WHEN** the draft is validated and saved **THEN** canonical height is 177.8 cm, weight is 81.6466266 kg before contract precision handling, and displayed BMI is 25.8 with no category label. | `apps/mobile/tests/profile-form.test.ts:67` — whole feet plus bounded inches and pounds use exact SI conversions<br>`apps/mobile/tests/domain.test.ts:117` — duplicate escaped keys, unknown numeric values and excessive JSON depth are rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-002-02 | pro-invalid-number — **GIVEN** height is zero, weight is non-finite, or age contains a fraction **WHEN** Save profile is pressed **THEN** the relevant inline errors appear, BMI is unavailable, and no invalid profile is submitted. | `apps/mobile/tests/profile-form.test.ts:36` — profile validation collects independent inline errors without clearing draft text<br>`apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRO-003 — Revisioned save and frozen session context

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` / `AND-PRO-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-032-AND-PRO-003-01 | pro-edit-after-check — **GIVEN** a finalized check records weight 80 kg and profile version A **WHEN** the user saves weight 82 kg as version B **THEN** the historical check retains version A and 80 kg while the next check may use B. | `apps/mobile/tests/controller.test.ts:280` — signed-in profile revision freezes into Start check and a later profile save cannot replace it<br>`apps/mobile/tests/domain.test.ts:152` — check freezes original profile timestamp and recomputes elapsed use at its start | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-003-02 | pro-edit-during-open-draft — **GIVEN** a check draft has already copied version A **WHEN** another device changes the profile **THEN** the open check does not silently acquire the new context and displays its saved profile version on review. | `apps/mobile/tests/controller.test.ts:280` — signed-in profile revision freezes into Start check and a later profile save cannot replace it<br>`apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-003-03 | pro-edit-before-first-acquisition-still-frozen — **GIVEN** Start check created session A with profile revision P1 and no capture yet **WHEN** the user saves revision P2 on this or another device **THEN** A still displays P1 and its original target time; using P2 requires a new linked check created after that save. | `apps/mobile/tests/controller.test.ts:280` — signed-in profile revision freezes into Start check and a later profile save cannot replace it<br>`apps/mobile/tests/domain.test.ts:152` — check freezes original profile timestamp and recomputes elapsed use at its start | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRO-004 — Conflict-aware and idempotent synchronization

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` / `AND-PRO-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-032-AND-PRO-004-01 | pro-two-device-conflict — **GIVEN** two devices edit the same base revision **WHEN** the first save succeeds and the second receives 412 **THEN** the second displays both versions and retains its draft until the user chooses. | `apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits<br>`apps/mobile/tests/controller.test.ts:423` — native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-004-02 | pro-save-timeout-retry — **GIVEN** the server saved a revision but the response was lost **WHEN** the app retries with the original key and payload **THEN** one revision is returned and no duplicate change is recorded. | `apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits<br>`apps/mobile/tests/controller.test.ts:280` — signed-in profile revision freezes into Start check and a later profile save cannot replace it | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-004-03 | pro-stale-generation-is-quarantined — **GIVEN** a queued profile Save carries an earlier data generation **WHEN** the service returns 410 after accepted all-data deletion **THEN** the operation is quarantined without rewriting its generation; new saves wait for the explicit reset acknowledgment. | `apps/mobile/tests/domain.test.ts:477` — HTTP concurrency and generation errors never force overwrite<br>`apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `412`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-PRO-005 — Offline drafts and account separation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` / `AND-PRO-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-032-AND-PRO-005-01 | pro-offline-edit — **GIVEN** an account profile is cached and the network is unavailable **WHEN** the user saves valid changes **THEN** the local revision is labeled pending and reconciliation later applies the original ETag rather than pretending a server save occurred. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-005-02 | pro-guest-to-account — **GIVEN** a fictional demo profile exists **WHEN** the user opens a newly authenticated account **THEN** the account profile is fetched or shown empty and the demo profile is not imported automatically. | `apps/mobile/tests/domain.test.ts:246` — guest check cannot upload and never acquires an account owner by sign-in<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRO-006 — Timestamp and baseline integrity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` / `AND-PRO-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-032-AND-PRO-006-01 | pro-future-use-time — **GIVEN** a last-use timestamp is later than the current device time **WHEN** the user saves **THEN** the app asks the user to review the date/time or select unknown and does not silently clamp the timestamp. | `apps/mobile/tests/profile-form.test.ts:117` — known last-use rejects impossible calendar dates and future times with a field error<br>`apps/mobile/tests/domain.test.ts:152` — check freezes original profile timestamp and recomputes elapsed use at its start | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-006-02 | pro-demographics-do-not-score — **GIVEN** a complete profile with daily use and all demographics **WHEN** the dashboard or result is displayed **THEN** no metabolic-rate calculation, baseline qualification, or intoxication probability is created from those fields. | `apps/mobile/tests/domain.test.ts:152` — check freezes original profile timestamp and recomputes elapsed use at its start<br>`apps/mobile/tests/profile-form.test.ts:117` — known last-use rejects impossible calendar dates and future times with a field error | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRO-007 — Accessible entry and iOS parity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md` / `AND-PRO-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-032-AND-PRO-007-01 | pro-accessible-errors — **GIVEN** screen-reader navigation and 200% text scaling **WHEN** two fields fail validation **THEN** the error summary is announced, the first invalid field receives focus, and Save/Cancel remain reachable without overlapping controls. | `apps/mobile/tests/profile-form.test.ts:23` — locale decimal and digit input becomes locale-independent numbers<br>`apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-032-AND-PRO-007-02 | pro-ios-unit-roundtrip — **GIVEN** an iOS profile contains canonical values with more precision than display **WHEN** the user toggles units twice without editing **THEN** stored values and BMI are unchanged and no new profile revision is created. ## Acceptance evidence Required evidence: unit/locale and boundary fixtures; missingness round-trip; frozen-session test; concurrent-update and response-loss integration tests; demo/account isolation; offline reconciliation; Android/iOS field navigation screenshots; log review demonstrating that profile values are excluded from telemetry. None of the numeric entry bounds closes a scientific eligibility or model gate. | `apps/mobile/tests/profile-form.test.ts:23` — locale decimal and digit input becomes locale-independent numbers<br>`apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.


## Final corrected source evidence — e89897cc852a

# OTGD-032 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-profile/spec.md`; SHA256 `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-032/test-plan.md`. External review artifact only; PM controls import.

All 16 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-032-AND-PRO-001-01 | pro-empty-profile-save — - **GIVEN** an account profile with no provided fields - **WHEN** the user saves without entering optional context - **THEN** numeric values remain null and no default cannabis exposure or baseline is created. | PARTIAL |
| OTGD-032-AND-PRO-001-02 | pro-declined-history — - **GIVEN** last use is set to Prefer not to say - **WHEN** the profile is saved and reloaded - **THEN** the declined marker persists and its timestamp remains null. | PARTIAL |
| OTGD-032-AND-PRO-002-01 | pro-imperial-bmi — - **GIVEN** the user enters 5 feet 10 inches and 180 pounds - **WHEN** the draft is validated and saved - **THEN** canonical height is 177.8 cm, weight is 81.6466266 kg before contract precision handling, and displayed BMI is 25.8 with no category label. | PARTIAL |
| OTGD-032-AND-PRO-002-02 | pro-invalid-number — - **GIVEN** height is zero, weight is non-finite, or age contains a fraction - **WHEN** Save profile is pressed - **THEN** the relevant inline errors appear, BMI is unavailable, and no invalid profile is submitted. | PARTIAL |
| OTGD-032-AND-PRO-003-01 | pro-edit-after-check — - **GIVEN** a finalized check records weight 80 kg and profile version A - **WHEN** the user saves weight 82 kg as version B - **THEN** the historical check retains version A and 80 kg while the next check may use B. | PASS |
| OTGD-032-AND-PRO-003-02 | pro-edit-during-open-draft — - **GIVEN** a check draft has already copied version A - **WHEN** another device changes the profile - **THEN** the open check does not silently acquire the new context and displays its saved profile version on review. | PARTIAL |
| OTGD-032-AND-PRO-003-03 | pro-edit-before-first-acquisition-still-frozen — - **GIVEN** Start check created session A with profile revision P1 and no capture yet - **WHEN** the user saves revision P2 on this or another device - **THEN** A still displays P1 and its original target time; using P2 requires a new linked check created after that save. | PARTIAL |
| OTGD-032-AND-PRO-004-01 | pro-two-device-conflict — - **GIVEN** two devices edit the same base revision - **WHEN** the first save succeeds and the second receives 412 - **THEN** the second displays both versions and retains its draft until the user chooses. | PARTIAL |
| OTGD-032-AND-PRO-004-02 | pro-save-timeout-retry — - **GIVEN** the server saved a revision but the response was lost - **WHEN** the app retries with the original key and payload - **THEN** one revision is returned and no duplicate change is recorded. | PARTIAL |
| OTGD-032-AND-PRO-004-03 | pro-stale-generation-is-quarantined — - **GIVEN** a queued profile Save carries an earlier data generation - **WHEN** the service returns 410 after accepted all-data deletion - **THEN** the operation is quarantined without rewriting its generation; new saves wait for the explicit reset acknowledgment. | PARTIAL |
| OTGD-032-AND-PRO-005-01 | pro-offline-edit — - **GIVEN** an account profile is cached and the network is unavailable - **WHEN** the user saves valid changes - **THEN** the local revision is labeled pending and reconciliation later applies the original ETag rather than pretending a server save occurred. | PARTIAL |
| OTGD-032-AND-PRO-005-02 | pro-guest-to-account — - **GIVEN** a fictional demo profile exists - **WHEN** the user opens a newly authenticated account - **THEN** the account profile is fetched or shown empty and the demo profile is not imported automatically. | PARTIAL |
| OTGD-032-AND-PRO-006-01 | pro-future-use-time — - **GIVEN** a last-use timestamp is later than the current device time - **WHEN** the user saves - **THEN** the app asks the user to review the date/time or select unknown and does not silently clamp the timestamp. | PASS |
| OTGD-032-AND-PRO-006-02 | pro-demographics-do-not-score — - **GIVEN** a complete profile with daily use and all demographics - **WHEN** the dashboard or result is displayed - **THEN** no metabolic-rate calculation, baseline qualification, or intoxication probability is created from those fields. | PARTIAL |
| OTGD-032-AND-PRO-007-01 | pro-accessible-errors — - **GIVEN** screen-reader navigation and 200% text scaling - **WHEN** two fields fail validation - **THEN** the error summary is announced, the first invalid field receives focus, and Save/Cancel remain reachable without overlapping controls. | PARTIAL |
| OTGD-032-AND-PRO-007-02 | pro-ios-unit-roundtrip — - **GIVEN** an iOS profile contains canonical values with more precision than display - **WHEN** the user toggles units twice without editing - **THEN** stored values and BMI are unchanged and no new profile revision is created. | PARTIAL |
