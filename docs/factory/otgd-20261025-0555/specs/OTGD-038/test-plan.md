# OTGD-038: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md`; SHA-256 `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/tests/acquisition.test.ts` — `797e9858167b9b80bff401e0b66c3fda1f9ae56c8f007fbe5b10c4aeb0b159be`
- `apps/mobile/tests/controller.test.ts` — `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92`
- `apps/mobile/tests/study-consent.test.ts` — `d862ef179f94af0018561a8c6dfa62972dcdd2d89c1e7060ea6a740552807481`
- `services/api/tests/test_capture_policy.py` — `971a808c066b099c4006aab592d052aa3867d08cdfb10fbd0eb2f5288e5febae`
- `services/api/tests/test_capture_signing.py` — `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`
- `services/api/tests/test_consent_versions.py` — `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963`
- `services/api/tests/test_operator_governance.py` — `4d512a3ad9f7c65b69ee09d94fb471799d1aff63a5bc4c34140526dcac280ae7`
- `services/api/tests/test_participant_acquisition.py` — `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57`
- `services/api/tests/test_participant_postgres.py` — `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-STUDY-001 — Show only authorized memberships

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md` / `AND-STUDY-001`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-038-AND-STUDY-001-01 | Invited customer opens research access — **GIVEN** one operator-provisioned invitation for the signed-in account **WHEN** memberships are requested **THEN** the app displays that invitation and its actual status. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/tests/controller.test.ts:353` — delayed history cannot enter another account or reopen a signed-out workspace | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-038-AND-STUDY-001-02 | Customer guesses another study UUID — **GIVEN** no membership in the requested study **WHEN** its consent or capability route is requested **THEN** access is refused without disclosing another participant's data. | `apps/mobile/tests/controller.test.ts:107` — explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity<br>`apps/mobile/tests/study-consent.test.ts:25` — only an active exact affirmative receipt suppresses new study consent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-STUDY-002 — Bind consent to complete approved content

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md` / `AND-STUDY-002`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-038-AND-STUDY-002-01 | Current approved consent is accepted — **GIVEN** an eligible active invitation and complete approved document **WHEN** the participant explicitly accepts **THEN** a durable receipt records the version, digest, authenticated subject, client time, and server receipt time. | `apps/mobile/tests/controller.test.ts:185` — a consent receipt for another document or timestamp is never accepted as research authorization<br>`services/api/tests/test_consent_versions.py:72` — test_same_text_new_version_or_invitation_requires_current_exact_consent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-038-AND-STUDY-002-02 | Protocol changes while the page is open — **GIVEN** the displayed consent version is no longer current **WHEN** acceptance is submitted **THEN** the server rejects the stale version and the app loads the updated document without transferring the old acceptance. | `services/api/tests/test_consent_versions.py:45` — test_updated_document_has_new_immutable_receipt_and_replay_keeps_current_pointer<br>`apps/mobile/tests/controller.test.ts:77` — a delayed old-account logout cannot open provider logout or replace the new-account screen | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-STUDY-003 — Separate consent from capability qualification

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md` / `AND-STUDY-003`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-038-AND-STUDY-003-01 | Consent exists but optics remain unqualified — **GIVEN** accepted consent and no approved optical configuration **WHEN** the app requests eye capture **THEN** passive guidance or an unavailable state is shown and no participant stimulus is emitted. | `apps/mobile/tests/controller.test.ts:107` — explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity<br>`services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-038-AND-STUDY-003-02 | Client edits capability JSON — **GIVEN** a locally modified available flag **WHEN** an upload or research request reaches the backend **THEN** server-owned qualification and membership checks still prevent unauthorized operation. | `apps/mobile/tests/controller.test.ts:107` — explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity<br>`apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-STUDY-004 — Require fresh authorization for qualified capture

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md` / `AND-STUDY-004`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-038-AND-STUDY-004-01 | Cached scope cannot authorize offline capture — **GIVEN** a cached available scope covering the device/configuration/channel **WHEN** qualified capture is requested offline **THEN** the app requires reconnection; local uncalibrated practice remains a separately labeled permitted path. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/tests/study-consent.test.ts:53` — withdrawal requires a fresh invitation, and local pending withdrawal blocks reconsent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-038-AND-STUDY-004-02 | Authorization expires offline — **GIVEN** the phone was restarted or its wall clock was rolled back **WHEN** new qualified capture is requested **THEN** the app asks for reconnection and preserves existing records without acquiring under stale permission. | `services/api/tests/test_operator_governance.py:623` — test_current_raw_permission_is_signed_and_old_preference_replay_cannot_restart_after_revocation<br>`apps/mobile/tests/acquisition.test.ts:1501` — scope-qualified preparation End stops the advanced capture token before a deferred server start reaches hardware | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-STUDY-005 — Make withdrawal effective for new operations

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md` / `AND-STUDY-005`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-038-AND-STUDY-005-01 | Participant withdraws — **GIVEN** active study access **WHEN** the participant confirms withdrawal while offline **THEN** local capture stops, the exact request is retained pending, and server completion is not claimed; later acceptance blocks verified uploads and returns the receipt. | `apps/mobile/tests/controller.test.ts:107` — explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity<br>`apps/mobile/tests/study-consent.test.ts:25` — only an active exact affirmative receipt suppresses new study consent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-038-AND-STUDY-005-02 | Old upload ticket is used after withdrawal — **GIVEN** an artifact ticket issued before withdrawal **WHEN** upload completion is requested afterward **THEN** authorization is rechecked and the object cannot become a verified research artifact through the stale ticket. | `apps/mobile/tests/controller.test.ts:107` — explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity<br>`apps/mobile/tests/study-consent.test.ts:25` — only an active exact affirmative receipt suppresses new study consent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-STUDY-006 — Preserve truthful study absence

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md` / `AND-STUDY-006`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-038-AND-STUDY-006-01 | Fresh production environment — **GIVEN** no approved study records **WHEN** research access opens **THEN** no research capture or prediction is offered. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`services/api/tests/test_operator_governance.py:360` — test_real_session_start_requires_current_approved_study_and_exact_protocol | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-038-AND-STUDY-006-02 | Synthetic local fixture — **GIVEN** a local development study fixture **WHEN** it is displayed **THEN** its synthetic identity and environment are explicit and its permissions cannot be reused in QA/prod. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`services/api/tests/test_operator_governance.py:360` — test_real_session_start_requires_current_approved_study_and_exact_protocol | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Alcohol dependency and acquisition-boundary audit

Mapped existing cases: OTGD-019-AND-ALC-001-02, AND-ALC-004-02; related AND-DEV-004, AND-CHECK-002, AND-STUDY-003/004.

Assertion adequacy inspected: Read operator-governance tests: configuration/calibration at -1ms, equality and +1ms; expiry history/body/hash/decisions immutable; calibration failure distinguished from still-current configuration. Current SOFTWARE_ADAPTERS/PHYSICAL_DRIVERS contain no alcohol entry and capability reason is HUMAN_ADAPTER_UNIMPLEMENTED. Four explicitly hypothetical HTTP grant/start cases expire before still-valid grant end, require403 APPROVED_REGISTRY_VERSION_REQUIRED, zero sign_start calls, no persisted start/alcohol and unchanged issued receipt. Mobile three new cases verify strict configuration selection before expiry, fresh absent inventory overrides stale cached availability with zero grant/nonce/hardware events, and a hypothetical returned authoritative-start refusal leaves invalid null alcohol and zero acquisition events.

Remaining limits: Client refusal transport is controlled, not an integrated real breath instrument. No qualified driver exists. Direct participant recalibration-specific start/recovery remains BLOCKED by absent instrument; generic server refusal must not be relabeled a diagnosis. Server -1ms/equality/+1ms and hypothetical grant race have reported focused execution; mobile author report/release and final gates pending.
