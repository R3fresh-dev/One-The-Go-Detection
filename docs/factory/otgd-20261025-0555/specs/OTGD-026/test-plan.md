# OTGD-026: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md`; SHA-256 `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/mobile.spec.ts` — `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`
- `apps/mobile/tests/acquisition.test.ts` — `797e9858167b9b80bff401e0b66c3fda1f9ae56c8f007fbe5b10c4aeb0b159be`
- `apps/mobile/tests/cardiac-selection.test.ts` — `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`
- `apps/mobile/tests/controller.test.ts` — `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92`
- `apps/mobile/tests/domain.test.ts` — `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`
- `apps/mobile/tests/lifecycle.test.ts` — `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`
- `apps/mobile/tests/replacements.test.ts` — `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233`
- `apps/mobile/tests/sync.test.ts` — `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_participant_acquisition.py` — `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57`
- `services/api/tests/test_replacement_links.py` — `e6091da29dd66c1f496bf9857bd70c8b73bceebf61494014aa3ab9ebec74597b`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-CHECK-001 — Start and capability-aware checklist

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-001-01 | Start a synthetic check — **GIVEN** local demonstration mode and no physical assay **WHEN** the user selects Start check **THEN** the app SHALL allocate a new session UUID, display Simulated data for fictional channels and Uncalibrated practice for actual native taps, and present concrete synthetic steps without requiring a cloud account or claiming a physical measurement. | `apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit<br>`apps/mobile/tests/acquisition.test.ts:1703` — actual Python HTTP grant/start envelope binds material, frozen context and signed fresh start without simulated clinical authority | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-001-02 | Required capability is blocked — **GIVEN** an unavailable approved optical or assay configuration **WHEN** the checklist evaluates that capability **THEN** it SHALL show the specific blocker and an allowed preview, sample-record, or skip action where the mode permits it; it SHALL not show a completed measurement or fabricate a substitute. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-CHECK-002 — Immutable context and independent consent

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-002-01 | Profile changes during a check — **GIVEN** a newly created check with a frozen profile version, before any acquisition **WHEN** the user edits their profile elsewhere **THEN** the active check SHALL retain its original snapshot, and a later check SHALL use the new version; the older record SHALL not change silently. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-002-02 | Local capture permission without upload consent — **GIVEN** a granted camera or Bluetooth permission but no research upload authorization **WHEN** the user completes an allowed local action **THEN** the app SHALL keep it within the permitted local scope and SHALL not enqueue participant data for a study merely because OS permission was granted. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-002-03 | Offline clock rollback cannot grant capture — **GIVEN** cached formerly available capabilities and no network **WHEN** the wall clock is set backward or the phone reboots **THEN** qualified Start capture SHALL remain blocked pending a fresh online acknowledgment; permitted local uncalibrated practice SHALL remain available. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1.0`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-CHECK-003 — Attempt identity and sequence rules

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-003-01 | Invalid saliva collection retried — **GIVEN** a sample marked invalid for inadequate volume **WHEN** the user selects Replace sample and follows the allowed protocol **THEN** a new sample attempt SHALL be created, the first SHALL remain in the audit history, and only the accepted sample SHALL supply that check's analyte records. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`services/api/tests/test_participant_acquisition.py:380` — test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-003-02 | User requests repeated valid game — **GIVEN** one completed valid task in the current check **WHEN** the user reopens the reaction step **THEN** the app SHALL show the saved completion and review action, not a rerun action that can replace the accepted task with a faster result. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`services/api/tests/test_participant_acquisition.py:380` — test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-003-03 | Finalized invalid check requires a fresh assessment — **GIVEN** an invalid check already saved locally with a completed saliva or cardiac observation **WHEN** the user selects Start replacement check **THEN** the app SHALL create new session/target identities and explicit supersedes_session_id, keep the original immutable, and SHALL not carry any physical acquisition into the replacement. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-CHECK-004 — Capture timing, partial data, and review

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-004-01 | Device step skipped in a permitted measurement-only workflow — **GIVEN** no actual cardiac capture and a mode that permits a missing cardiac component **WHEN** the user advances to Review **THEN** cardiac data SHALL be marked not_collected with null timing/features and the stated reason; the app SHALL not copy an earlier pulse value or substitute zero. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization<br>`apps/mobile/tests/domain.test.ts:297` — altered context, selected projection, duplicate manifest and foreign attempt fail integrity | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-004-02 | Laboratory analysis returns the next day — **GIVEN** saliva collected yesterday with separately timed physiological/task measurements **WHEN** a permitted laboratory result is linked today **THEN** Review and history SHALL retain yesterday's collection and target times, identify the later analysis time, and SHALL not call the result a current real-time assessment. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1`, `1.0`, `3339`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-CHECK-005 — Cancellation, navigation, and interruptions

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-005-01 | App terminated during reaction task — **GIVEN** a persisted started task attempt without a completion event **WHEN** the app restarts **THEN** it SHALL mark that attempt interrupted, preserve already completed independent components, and require a new linked task attempt before representing task completion. | `apps/mobile/tests/lifecycle.test.ts:148` — concurrent route/background stops issue native cancel immediately and wait for terminal persistence<br>`apps/mobile/tests/sync.test.ts:352` — a new account epoch prevents late network results writing into its workspace | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-005-02 | Cancel command cannot reach the peripheral — **GIVEN** an active capture and a lost BLE connection **WHEN** the user selects Cancel check **THEN** the UI SHALL terminate locally, record cancellation, and reject subsequent late events for the canceled attempt regardless of whether the peripheral received the command. | `apps/mobile/tests/lifecycle.test.ts:148` — concurrent route/background stops issue native cancel immediately and wait for terminal persistence<br>`apps/mobile/tests/cardiac-selection.test.ts:282` — selection rejects another check, invalid attempts, active capture and saved changes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-005-03 | Keep draft cannot resume an ended task — **GIVEN** an active scored task whose parent navigator keeps tabs mounted **WHEN** the user selects another tab and then Keep draft in the resulting sheet **THEN** the native stimulus SHALL have already stopped and the attempt SHALL remain invalid; returning SHALL expose a permitted new attempt or replacement action rather than resuming. | `apps/mobile/tests/lifecycle.test.ts:148` — concurrent route/background stops issue native cancel immediately and wait for terminal persistence<br>`apps/mobile/tests/sync.test.ts:352` — a new account epoch prevents late network results writing into its workspace | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-CHECK-006 — Offline persistence and finalization

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-006-01 | Network drops after finalization submission — **GIVEN** a frozen local snapshot and an unknown server acknowledgment outcome **WHEN** the user requests reconciliation, or previously enabled automatic retry permits it, after connectivity returns **THEN** the app SHALL retry or query with the same identifiers and digest, reconcile one logical finalization, and SHALL not create another sample, task, or check. | `apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-006-02 | Draft version conflicts with server — **GIVEN** a stale local snapshot version **WHEN** the server returns a version conflict **THEN** the app SHALL preserve both the local pending content and authoritative version metadata, show Conflict needs review, and SHALL not overwrite a finalized remote record. | `apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-006-03 | Save and sign in cannot upload guest evidence — **GIVEN** a guest demo containing fictional chemistry and actual uncalibrated native taps **WHEN** the user saves the check, reconnects, and signs in **THEN** the check SHALL remain in its guest namespace with exact mixed provenance and no queue entry or account migration. | `apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-CHECK-007 — Result navigation and claim boundaries

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-007-01 | Synthetic check completes successfully — **GIVEN** a valid synthetic snapshot **WHEN** the measurement-only result arrives or is generated by the permitted local demonstration **THEN** the app SHALL show completion of the demonstration and its measurement details, with no intoxication percentage or physiological normality claim. | `apps/mobile/tests/domain.test.ts:323` — every research_estimate is rejected even when its shape could be schema-valid<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-007-02 | Forged result includes a probability — **GIVEN** a synthetic or unauthorized check **WHEN** a malformed cache or response contains an intoxication probability **THEN** the client SHALL reject that field/result, surface a data-integrity error, and SHALL not display it as a research estimate. | `apps/mobile/tests/domain.test.ts:323` — every research_estimate is rejected even when its shape could be schema-valid<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-007-03 | Signed future result is unsupported in this release — **GIVEN** an otherwise owner-matching signed response with research_estimate and a probability **WHEN** the result is opened from live navigation or history **THEN** the client SHALL reject it as UNSUPPORTED_RESEARCH_RESULT and SHALL not render the probability or relabel the result successful. | `apps/mobile/tests/domain.test.ts:323` — every research_estimate is rejected even when its shape could be schema-valid<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-CHECK-008 — Accessible parity and end-to-end evidence

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md` / `AND-CHECK-008`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-026-AND-CHECK-008-01 | Screen-reader navigation outside capture — **GIVEN** an enabled Android or iOS screen reader **WHEN** the user traverses the checklist and Review **THEN** step names, states, reasons, and actions SHALL be announced in a meaningful order without depending on badge color. | `apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-026-AND-CHECK-008-02 | Cross-platform offline replay — **GIVEN** equivalent fictional engineering-account records saved offline on each platform **WHEN** each signed-in user explicitly selects Upload check to the same permitted API environment **THEN** both SHALL preserve quantities, qualifiers, provenance, context/evidence hashes, and terminal states with platform metadata retained; guest demo records SHALL remain local and ineligible for this upload. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `9`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Alcohol dependency and acquisition-boundary audit

Mapped existing cases: OTGD-019-AND-ALC-001-02, AND-ALC-004-02; related AND-DEV-004, AND-CHECK-002, AND-STUDY-003/004.

Assertion adequacy inspected: Read operator-governance tests: configuration/calibration at -1ms, equality and +1ms; expiry history/body/hash/decisions immutable; calibration failure distinguished from still-current configuration. Current SOFTWARE_ADAPTERS/PHYSICAL_DRIVERS contain no alcohol entry and capability reason is HUMAN_ADAPTER_UNIMPLEMENTED. Four explicitly hypothetical HTTP grant/start cases expire before still-valid grant end, require403 APPROVED_REGISTRY_VERSION_REQUIRED, zero sign_start calls, no persisted start/alcohol and unchanged issued receipt. Mobile three new cases verify strict configuration selection before expiry, fresh absent inventory overrides stale cached availability with zero grant/nonce/hardware events, and a hypothetical returned authoritative-start refusal leaves invalid null alcohol and zero acquisition events.

Remaining limits: Client refusal transport is controlled, not an integrated real breath instrument. No qualified driver exists. Direct participant recalibration-specific start/recovery remains BLOCKED by absent instrument; generic server refusal must not be relabeled a diagnosis. Server -1ms/equality/+1ms and hypothetical grant race have reported focused execution; mobile author report/release and final gates pending.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.
