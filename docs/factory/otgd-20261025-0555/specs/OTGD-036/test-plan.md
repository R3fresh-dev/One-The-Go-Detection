# OTGD-036: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md`; SHA-256 `2768fdfbe5ff0b1971d6aad04101ea2fa17db6f6c3012848aa3aa3f490e654c8`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/components.spec.ts` — `725effb97f2e9195340fd6370b8491065eabdf849ce5c5680974c39cc2125c53`
- `apps/mobile/e2e/raw-recordings.spec.ts` — `2ada98a52caf63a835d979adc71bef5542795c5edbd72fc859cdb7975cbfd3b7`
- `apps/mobile/tests/device-presentation.test.ts` — `11e79b59ead32c0a6bc4fa818784bc00347f337cfb5dff71d13534673064600a`
- `apps/mobile/tests/lifecycle.test.ts` — `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`
- `apps/mobile/tests/service-boundary.test.ts` — `70b18be9dc9bdc1edfee67e9ad73d525e84bb256db367acfa9ac779ce1686360`
- `apps/mobile/tests/support-history.test.ts` — `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-SET-001 — Complete, functional settings navigation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` / `AND-SET-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-036-AND-SET-001-01 | set-signed-out-navigation — **GIVEN** demo is active and no account is authenticated **WHEN** Settings is opened **THEN** Sign in is available, cloud deletion is unavailable with its account requirement, and local demo clearing remains reachable. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes<br>`apps/mobile/tests/lifecycle.test.ts:21` — sign-out removal finishes after an already-started OS credential write | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-001-02 | set-active-check-switch — **GIVEN** a check is active **WHEN** Switch workspace is selected **THEN** any active native run ends once before the decision; the UI explains that it cannot resume, the broader draft may be retained, and no record is moved between workspaces. | `apps/mobile/e2e/raw-recordings.spec.ts:1332` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload<br>`apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-001-03 | set-research-access-visible-empty-state — **GIVEN** a fresh account has no study memberships **WHEN** the user selects Settings then Research access **THEN** the feature opens its empty-state explanation and a working Back route without creating an invitation or enabling capture. | `apps/mobile/e2e/raw-recordings.spec.ts:519` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset<br>`apps/mobile/tests/service-boundary.test.ts:19` — actual backend app-config and capabilities responses decode without removing mandatory fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SET-002 — Persisted appearance without measurement mutation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` / `AND-SET-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-036-AND-SET-002-01 | set-theme-restart — **GIVEN** Dark theme was saved **WHEN** the process is terminated and relaunched **THEN** Dark theme is restored without a prolonged light-screen flash or record mutation. | `apps/mobile/e2e/raw-recordings.spec.ts:519` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-002-02 | set-units-do-not-rewrite — **GIVEN** finalized checks contain canonical ng/mL and profile cm/kg values **WHEN** US customary display is selected **THEN** profile presentation may convert units, saliva units remain qualified as reported, and stored measurements/record hashes do not change. | `apps/mobile/e2e/components.spec.ts:79` — profile fields announce validation, preserve canonical units and guard unsaved edits | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SET-003 — Permission visibility and OS round-trip

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` / `AND-SET-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-036-AND-SET-003-01 | set-camera-denied — **GIVEN** camera permission is denied **WHEN** Permissions opens **THEN** the camera row shows Denied with its feature explanation and Open app settings, without launching another prompt. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |
| OTGD-036-AND-SET-003-02 | set-permission-changed-outside-app — **GIVEN** the user grants Bluetooth permission in OS settings **WHEN** the app returns to foreground **THEN** the displayed state refreshes and the reader feature decides whether a new scan is needed; an old scan is not assumed successful. | `apps/mobile/tests/service-boundary.test.ts:70` — research result format advertisement supports only the versioned reader and grants no inference authority<br>`apps/mobile/tests/device-presentation.test.ts:23` — permission, radio, reboot and unsupported reader failures have distinct recovery | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SET-004 — Capability and environment integrity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` / `AND-SET-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-036-AND-SET-004-01 | set-tampered-model-toggle — **GIVEN** a modified preference file contains `inference_enabled:true` **WHEN** Settings and the result workflow load **THEN** the unsupported key grants no capability and probability remains unavailable in this release. | `apps/mobile/tests/service-boundary.test.ts:70` — research result format advertisement supports only the versioned reader and grants no inference authority<br>`apps/mobile/e2e/raw-recordings.spec.ts:749` — interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-004-02 | set-qa-build-visible — **GIVEN** the installed app uses QA services **WHEN** Home or About is displayed **THEN** QA is visible and the app cannot describe itself as a production clinical release. | `apps/mobile/e2e/raw-recordings.spec.ts:749` — interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG<br>`apps/mobile/tests/service-boundary.test.ts:45` — unsupported app version, minimum version or contract pauses synchronization; maintenance is separate | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-004-03 | set-authorized-looking-research-output-still-disabled — **GIVEN** a server response or local record advertises an active research model **WHEN** Settings or result navigation evaluates it **THEN** inference_available remains false and no current surface displays an impairment probability. | `apps/mobile/tests/service-boundary.test.ts:70` — research result format advertisement supports only the versioned reader and grants no inference authority<br>`apps/mobile/e2e/raw-recordings.spec.ts:749` — interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SET-005 — Redacted, user-initiated diagnostics

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` / `AND-SET-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-036-AND-SET-005-01 | set-diagnostics-copy — **GIVEN** a connection error has a support request ID **WHEN** the user reviews and copies diagnostics **THEN** only allowlisted build/environment/error-reference fields reach the clipboard. | `apps/mobile/tests/support-history.test.ts:10` — support diagnostics copy only bounded explicit fields, never an error payload<br>`apps/mobile/e2e/raw-recordings.spec.ts:519` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-005-02 | set-error-with-sensitive-payload — **GIVEN** an internal exception includes a server payload with profile fields **WHEN** diagnostics are generated **THEN** the payload is excluded rather than serialized or truncated into the copy text. | `apps/mobile/tests/support-history.test.ts:10` — support diagnostics copy only bounded explicit fields, never an error payload<br>`apps/mobile/e2e/raw-recordings.spec.ts:519` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SET-006 — Accessible application shell and content

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` / `AND-SET-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-036-AND-SET-006-01 | set-large-text-navigation — **GIVEN** 200% system font scale on a 360 dp Android display **WHEN** Settings and Privacy are traversed **THEN** labels wrap, controls remain reachable by scrolling, and no essential action is hidden behind navigation or keyboard. | `apps/mobile/e2e/raw-recordings.spec.ts:1400` — actual service component labels conditional approved channels and model support, while the fictional build refuses both<br>`apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-006-02 | set-screen-reader-task-boundary — **GIVEN** a timing-task configuration does not support the active input/accommodation **WHEN** the user attempts that task **THEN** the task feature explains the unsupported configuration and records unavailability rather than claiming equivalent measured timing. | `apps/mobile/e2e/raw-recordings.spec.ts:519` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset<br>`apps/mobile/tests/service-boundary.test.ts:45` — unsupported app version, minimum version or contract pauses synchronization; maintenance is separate | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-006-03 | set-active-task-navigation-ends-before-dialog — **GIVEN** a native reaction run is active **WHEN** the user initiates a Settings/workspace route or End task **THEN** the run ends once before an overlay, retained partial evidence is marked invalid, and subsequent draft choices never resume it. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes<br>`apps/mobile/tests/service-boundary.test.ts:45` — unsupported app version, minimum version or contract pauses synchronization; maintenance is separate | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1`, `200`, `3`, `4.5`, `48`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-SET-007 — iOS parity and platform-specific behavior

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md` / `AND-SET-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-036-AND-SET-007-01 | set-ios-dynamic-type — **GIVEN** a large accessibility Dynamic Type size and VoiceOver **WHEN** the user changes theme and opens privacy controls **THEN** each label/action remains reachable with correct state announcements and preferences persist across launch. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-036-AND-SET-007-02 | set-ios-restricted-permission — **GIVEN** iOS reports camera access restricted by device policy **WHEN** the permission row is opened **THEN** it shows Restricted, does not promise that an ordinary permission prompt will fix it, and preserves access to other permitted features. ## Acceptance evidence Required evidence: automated navigation of every enabled row; preference migration/restart/unit-immutability tests; OS permission round-trip on both platforms; QA/local label inspection; tampered-config rejection; diagnostics allowlist fixtures; contrast measurements and 200% text screenshots; TalkBack/VoiceOver review. Scientific supported-device/timing/optical limits remain named gates; accessibility implementation alone does not qualify those measurements. | `apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice<br>`apps/mobile/tests/support-history.test.ts:70` — history detail round-trip keeps filters, selected IDs and scroll only in the current workspace epoch | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `44`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Rendered alcohol state/copy assertion audit

Mapped existing cases: OTGD-019-AND-ALC-002/003/005/006 cases; related APP-012/013, AND-HIST-003 and AND-RES-004.

Assertion adequacy inspected: Read actual AlcoholScreen/ResultsScreen/HistoryScreen/ResultDetail fixture and assertions in raw-recordings.spec.ts. Measurement/guest/research variants retain unavailable qualified hardware, mg/L and model-specific co-use copy, replace stale unconditional classification statement. Six value/source variants (zero, low, below_loq, not_detected, invalid, simulated) traverse actual history/result/detail; assertions retain units, qualifier/source/time, dashes for null, separate alcohol meaning and no automatic BAC/impairment adjustment. Positive driving/legal-clearance/combined-score patterns absent; truthful clearance Unavailable remains visible.

Remaining limits: Controlled component inputs are hypothetical reporting records, not acquired sensor data; research fixture is not newly qualified scientific authority. Notification/OS-wide copy is not exhaustively proved by these component surfaces. Writer active; new component tests NOT_RUN in verifier final scope, author final report pending.

### Permissions race and no-reprompt assertion audit

Mapped existing cases: OTGD-036-AND-SET-003-01/02 and AND-SET-007-02; related AND-EYE-002, AND-ONB-004 and AND-AUTH-005.

Assertion adequacy inspected: Read PermissionsCard implementation and actual exported Settings component harness. Status labels cover denied/canAskAgain, denied/permanent, restricted, undetermined, failed reads; zero prompts across mount/refresh/active-return; OS settings call occurs once only explicit action. Deferred reads resolved newer-first, stale controller epoch before React render, account/generation changes and unmount must not publish old state; new scoped card is Not checked until current read; listener teardown asserted. Real ordinary UI test Settings/Back preserves draft/sample with no camera prompt. Implementation uses active+sequence+captured epoch guard and scoped card identity.

Remaining limits: Adapters are controlled OS observations. Real Android/iOS settings return, OS permission policy, TalkBack/VoiceOver, key storage and native lifecycle remain Task7 BLOCKED/NOT_RUN. Writer not released; no final gate execution or independent runtime PASS.
