# OTGD-021: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md`; SHA-256 `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e`.
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
- `apps/mobile/tests/device-presentation.test.ts` — `11e79b59ead32c0a6bc4fa818784bc00347f337cfb5dff71d13534673064600a`
- `apps/mobile/tests/support-history.test.ts` — `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`
- `apps/mobile/tests/sync.test.ts` — `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`
- `apps/mobile/tests/workspace-scope.test.ts` — `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-DASH-001 — Honest scope and provenance

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` / `AND-DASH-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-021-AND-DASH-001-01 | dash-demo-home — **GIVEN** an isolated demo workspace with a synthetic check **WHEN** Home is displayed **THEN** the demo badge and synthetic source description remain visible and no intoxication percentage appears. | `apps/mobile/tests/sync.test.ts:352` — a new account epoch prevents late network results writing into its workspace<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-001-02 | dash-old-check — **GIVEN** the latest check was collected yesterday **WHEN** the dashboard opens today **THEN** its collection date/time is shown and the card does not claim to represent the user's present state. | `apps/mobile/tests/sync.test.ts:352` — a new account epoch prevents late network results writing into its workspace<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-DASH-002 — Single check entry and authorization

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` / `AND-DASH-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-021-AND-DASH-002-01 | dash-double-start-tap — **GIVEN** no active draft and an enabled start action **WHEN** two rapid taps occur before navigation completes **THEN** one logical session is created and both navigation events resolve to that session. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/sync.test.ts:77` — withdrawal fences an in-flight consent against both a late receipt and a late retryable failure | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-002-02 | dash-gated-capture — **GIVEN** pupil capture is unavailable because its approved protocol is not configured **WHEN** View availability is selected **THEN** the app explains that channel's unavailability and does not open the camera/flash or replace it with a fabricated account measurement. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/e2e/mobile.spec.ts:6` — guest completes a measurement-only check, exact export and privacy/settings journey | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-002-03 | dash-frozen-profile-at-creation — **GIVEN** profile revision P1 is selected when Start check is pressed **WHEN** P2 arrives before the first acquisition **THEN** the draft retains P1, target_at equals its created_at, and its review identifies P1. | `apps/mobile/tests/controller.test.ts:280` — signed-in profile revision freezes into Start check and a later profile save cannot replace it<br>`apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-DASH-003 — Explicit draft resumption

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` / `AND-DASH-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-021-AND-DASH-003-01 | dash-resume-saliva-draft — **GIVEN** a draft with one retained saliva attempt and no completed task **WHEN** Continue check is selected **THEN** the same draft opens at its next eligible step with the original sample identity. | `apps/mobile/tests/controller.test.ts:382` — server generation retirement quarantines prior checks and a new empty workspace requires separate acknowledgment<br>`apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-003-02 | dash-task-interruption-return — **GIVEN** the app was backgrounded during the native task **WHEN** Home is opened and the draft resumed **THEN** the interruption is shown and no task completion is inferred from elapsed wall time. | `apps/mobile/tests/controller.test.ts:382` — server generation retirement quarantines prior checks and a new empty workspace requires separate acknowledgment<br>`apps/mobile/tests/sync.test.ts:426` — already queued ordinary uploads remain untouched during service readiness pause | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-DASH-004 — Current device state

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` / `AND-DASH-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-021-AND-DASH-004-01 | dash-reader-disconnect — **GIVEN** a connected reader with a recent battery value **WHEN** its BLE link drops **THEN** Home changes to Not connected and the battery value cannot remain labeled live. | `apps/mobile/tests/device-presentation.test.ts:16` — a saved reader alias does not become connected readiness or live battery<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-004-02 | dash-reader-reboot — **GIVEN** a reader reconnects with a different boot identity **WHEN** readiness is recalculated **THEN** unfinished capture readiness resets and old monotonic readings are not presented as belonging to the new boot. | `apps/mobile/tests/device-presentation.test.ts:16` — a saved reader alias does not become connected readiness or live battery<br>`apps/mobile/tests/controller.test.ts:465` — unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-DASH-005 — Offline availability and synchronization truth

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` / `AND-DASH-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-021-AND-DASH-005-01 | dash-offline-check-list — **GIVEN** cached permitted history and no network **WHEN** Home opens **THEN** cached rows remain available with an offline indicator and the latest refresh time. | `apps/mobile/tests/support-history.test.ts:115` — mixed local and synced history uses acquisition time and stable identity ties<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-005-02 | dash-lost-finalization-response — **GIVEN** a session finalization request timed out **WHEN** Home renders its recent row **THEN** the row remains pending until the server is reconciled using the original identity/idempotency key. | `apps/mobile/tests/controller.test.ts:107` — explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity<br>`apps/mobile/tests/sync.test.ts:290` — a lost accepted response replays the same identity and unchanged bytes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-005-03 | dash-reconnect-respects-manual-retry — **GIVEN** an explicitly queued account check has automatic retries disabled **WHEN** the network reconnects **THEN** Home shows the waiting item and manual Upload/Retry action without beginning a network mutation. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/support-history.test.ts:96` — pending sync means explicitly requested delivery, not local saves or retired records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-DASH-006 — Refresh and workspace race control

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` / `AND-DASH-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-021-AND-DASH-006-01 | dash-account-switch-race — **GIVEN** an account-A refresh is in flight **WHEN** the user switches to demo before the response returns **THEN** A's response is discarded and no account data appears in demo. | `apps/mobile/tests/workspace-scope.test.ts:94` — same-owner same-generation response succeeds; locking or backgrounding invalidates the scope<br>`apps/mobile/tests/sync.test.ts:352` — a new account epoch prevents late network results writing into its workspace | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-006-02 | dash-out-of-order-refresh — **GIVEN** refresh B returns a newer session revision before refresh A **WHEN** A completes later **THEN** the displayed revision does not regress. | `apps/mobile/tests/sync.test.ts:352` — a new account epoch prevents late network results writing into its workspace<br>`apps/mobile/tests/controller.test.ts:353` — delayed history cannot enter another account or reopen a signed-out workspace | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-DASH-007 — Accessible navigation and iOS parity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md` / `AND-DASH-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-021-AND-DASH-007-01 | dash-accessible-status — **GIVEN** TalkBack is enabled and the reader disconnects **WHEN** the status changes **THEN** “Reader, not connected” is announced once without an unbounded repeating alert. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes<br>`apps/mobile/tests/device-presentation.test.ts:16` — a saved reader alias does not become connected readiness or live battery | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-007-02 | dash-ios-check-tab — **GIVEN** an existing draft on iOS **WHEN** the Check tab is selected using VoiceOver **THEN** the same draft decision used by the primary CTA appears with its correct focus and no duplicate session allocation. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-021-AND-DASH-007-03 | dash-alcohol-route-is-reachable — **GIVEN** no alcohol instrument or approved configuration exists **WHEN** the user selects Alcohol measurement on Home **THEN** the alcohol availability screen opens with Hardware required, its requirements action, and working Back navigation. ## Acceptance evidence Required evidence: Android/iOS home empty/draft/complete/error screenshots; double-start idempotency test; offline/pending-result tests; simulated BLE disconnect/reboot test; stale-response/account-switch tests; text-scale and screen-reader checks. Public dashboard availability does not demonstrate analytical validity, clinical approval, or a trained model. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes<br>`apps/mobile/tests/workspace-scope.test.ts:73` — scope checks reject a stale error and a previously opened destructive confirmation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `200`, `44`, `48`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

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

# OTGD-021 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md`; SHA256 `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-021/test-plan.md`. External review artifact only; PM controls import.

All 17 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-021-AND-DASH-001-01 | dash-demo-home — - **GIVEN** an isolated demo workspace with a synthetic check - **WHEN** Home is displayed - **THEN** the demo badge and synthetic source description remain visible and no intoxication percentage appears. | PARTIAL |
| OTGD-021-AND-DASH-001-02 | dash-old-check — - **GIVEN** the latest check was collected yesterday - **WHEN** the dashboard opens today - **THEN** its collection date/time is shown and the card does not claim to represent the user's present state. | PARTIAL |
| OTGD-021-AND-DASH-002-01 | dash-double-start-tap — - **GIVEN** no active draft and an enabled start action - **WHEN** two rapid taps occur before navigation completes - **THEN** one logical session is created and both navigation events resolve to that session. | PARTIAL |
| OTGD-021-AND-DASH-002-02 | dash-gated-capture — - **GIVEN** pupil capture is unavailable because its approved protocol is not configured - **WHEN** View availability is selected - **THEN** the app explains that channel's unavailability and does not open the camera/flash or replace it with a fabricated account measurement. | PARTIAL |
| OTGD-021-AND-DASH-002-03 | dash-frozen-profile-at-creation — - **GIVEN** profile revision P1 is selected when Start check is pressed - **WHEN** P2 arrives before the first acquisition - **THEN** the draft retains P1, target_at equals its created_at, and its review identifies P1. | PARTIAL |
| OTGD-021-AND-DASH-003-01 | dash-resume-saliva-draft — - **GIVEN** a draft with one retained saliva attempt and no completed task - **WHEN** Continue check is selected - **THEN** the same draft opens at its next eligible step with the original sample identity. | PARTIAL |
| OTGD-021-AND-DASH-003-02 | dash-task-interruption-return — - **GIVEN** the app was backgrounded during the native task - **WHEN** Home is opened and the draft resumed - **THEN** the interruption is shown and no task completion is inferred from elapsed wall time. | PARTIAL |
| OTGD-021-AND-DASH-004-01 | dash-reader-disconnect — - **GIVEN** a connected reader with a recent battery value - **WHEN** its BLE link drops - **THEN** Home changes to Not connected and the battery value cannot remain labeled live. | PARTIAL |
| OTGD-021-AND-DASH-004-02 | dash-reader-reboot — - **GIVEN** a reader reconnects with a different boot identity - **WHEN** readiness is recalculated - **THEN** unfinished capture readiness resets and old monotonic readings are not presented as belonging to the new boot. | PARTIAL |
| OTGD-021-AND-DASH-005-01 | dash-offline-check-list — - **GIVEN** cached permitted history and no network - **WHEN** Home opens - **THEN** cached rows remain available with an offline indicator and the latest refresh time. | PARTIAL |
| OTGD-021-AND-DASH-005-02 | dash-lost-finalization-response — - **GIVEN** a session finalization request timed out - **WHEN** Home renders its recent row - **THEN** the row remains pending until the server is reconciled using the original identity/idempotency key. | PARTIAL |
| OTGD-021-AND-DASH-005-03 | dash-reconnect-respects-manual-retry — - **GIVEN** an explicitly queued account check has automatic retries disabled - **WHEN** the network reconnects - **THEN** Home shows the waiting item and manual Upload/Retry action without beginning a network mutation. | PARTIAL |
| OTGD-021-AND-DASH-006-01 | dash-account-switch-race — - **GIVEN** an account-A refresh is in flight - **WHEN** the user switches to demo before the response returns - **THEN** A's response is discarded and no account data appears in demo. | PARTIAL |
| OTGD-021-AND-DASH-006-02 | dash-out-of-order-refresh — - **GIVEN** refresh B returns a newer session revision before refresh A - **WHEN** A completes later - **THEN** the displayed revision does not regress. | NOT_RUN |
| OTGD-021-AND-DASH-007-01 | dash-accessible-status — - **GIVEN** TalkBack is enabled and the reader disconnects - **WHEN** the status changes - **THEN** “Reader, not connected” is announced once without an unbounded repeating alert. | BLOCKED |
| OTGD-021-AND-DASH-007-02 | dash-ios-check-tab — - **GIVEN** an existing draft on iOS - **WHEN** the Check tab is selected using VoiceOver - **THEN** the same draft decision used by the primary CTA appears with its correct focus and no duplicate session allocation. | BLOCKED |
| OTGD-021-AND-DASH-007-03 | dash-alcohol-route-is-reachable — - **GIVEN** no alcohol instrument or approved configuration exists - **WHEN** the user selects Alcohol measurement on Home - **THEN** the alcohol availability screen opens with Hardware required, its requirements action, and working Back navigation. | PARTIAL |
