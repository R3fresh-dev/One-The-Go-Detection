# OTGD-035: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md`; SHA-256 `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/raw-recordings.spec.ts` — `2ada98a52caf63a835d979adc71bef5542795c5edbd72fc859cdb7975cbfd3b7`
- `apps/mobile/tests/acquisition.test.ts` — `797e9858167b9b80bff401e0b66c3fda1f9ae56c8f007fbe5b10c4aeb0b159be`
- `apps/mobile/tests/export-projection.test.ts` — `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`
- `apps/mobile/tests/measurement-format.test.ts` — `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`
- `apps/mobile/tests/participant-acquisition.test.ts` — `1867260acffffc4ac828866c0022ce3d1e2bb34b001e1b6558786a794939cf2f`
- `apps/mobile/tests/report-revisions.test.ts` — `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`
- `services/api/tests/test_lab_handoff.py` — `3396acf6ae29a8d994bc37f937417b446acb1c40499b6c6a6ce81fff7e0cbeb0`
- `services/api/tests/test_participant_acquisition.py` — `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57`
- `services/api/tests/test_report_revisions.py` — `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-SAL-001 — Saliva step and method availability

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` / `AND-SAL-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-035-AND-SAL-001-01 | Simulated sample workflow — **GIVEN** explicit P0 mode **WHEN** the user selects Use simulated sample **THEN** the app SHALL create a labeled fictional sample and fictional analyte records, retain simulated source on all channels, and show the same validation/review UI used by the production adapters. | `apps/mobile/e2e/raw-recordings.spec.ts:965` — specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry<br>`apps/mobile/tests/participant-acquisition.test.ts:405` — rounded approved dilution and explicit invalid observations retain the server's actual semantics | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-001-02 | Reader has no assay implementation — **GIVEN** a connected Nano that only supplies telemetry **WHEN** the user opens Saliva **THEN** Read cartridge SHALL be unavailable with Assay not available, and the app SHALL permit only authorized sample-record or demonstration actions without implying chemical detection. | `apps/mobile/e2e/raw-recordings.spec.ts:965` — specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry<br>`apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `11`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-SAL-002 — Collection identity, fields, and timestamps

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` / `AND-SAL-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-035-AND-SAL-002-01 | Buffered collector — **GIVEN** a qualified collection method with recorded saliva and buffer quantities **WHEN** collection is accepted **THEN** the sample record SHALL retain those quantities, the defined dilution convention, method version, lot, and collection time for later comparison with each report's concentration basis. | `services/api/tests/test_report_revisions.py:793` — test_uncollected_specimen_is_refused_but_collected_empty_report_accepts_later_analysis<br>`apps/mobile/e2e/raw-recordings.spec.ts:965` — specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-002-02 | Invalid sample identity from device — **GIVEN** a session expecting sample A **WHEN** a reader result identifies sample B or a different session **THEN** the import SHALL fail with identity mismatch and SHALL not silently relabel the reading or attach it to sample A. | `apps/mobile/tests/participant-acquisition.test.ts:223` — approved quantities and unknown reasons refuse contradictory or invented collection facts<br>`apps/mobile/tests/export-projection.test.ts:37` — an unselected projection cannot hide unknown metadata or a different run/sample identity | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-002-03 | Companion evidence cannot be omitted — **GIVEN** a saliva sample with buffer, lot, adequacy, and report lineage metadata beyond the v0.1 projection **WHEN** the check is saved and exported or explicitly uploaded **THEN** the full typed companion attempt and its digest SHALL accompany the selected projection; unknown v0.1 fields or an incomplete manifest SHALL fail validation. | `apps/mobile/tests/participant-acquisition.test.ts:87` — actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage<br>`apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1`, `1.0`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-SAL-003 — Quantities, original reports, and qualifiers

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` / `AND-SAL-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-035-AND-SAL-003-01 | Below quantification without detection assertion — **GIVEN** a laboratory report stating BLQ at an LOQ of 0.1 ng/mL **WHEN** the report is imported and viewed **THEN** the canonical value SHALL remain null, the display SHALL say Below quantification with the limit and original qualifier, and SHALL not say Detected or 0 ng/mL. | `apps/mobile/tests/measurement-format.test.ts:65` — only quantified results display a numeric concentration, preserving a real zero if reported<br>`apps/mobile/tests/participant-acquisition.test.ts:87` — actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-003-02 | Upper limit is not an exact result — **GIVEN** an above-range report with a validated upper bound **WHEN** the user reviews the channel **THEN** the app SHALL display Above range and the bound, preserve null quantitative value, and SHALL not clip the reading to that bound for model or chart use. | `apps/mobile/tests/measurement-format.test.ts:65` — only quantified results display a numeric concentration, preserving a real zero if reported<br>`apps/mobile/tests/report-revisions.test.ts:74` — report list rejects another generation, changed original time, duplicate IDs, gaps and mutable result identity | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SAL-004 — Units, analyte basis, and dilution discipline

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` / `AND-SAL-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-035-AND-SAL-004-01 | Laboratory already corrected dilution — **GIVEN** a result of 75 pg/mL reported for neat oral fluid with laboratory_corrected status **WHEN** the app imports it from a buffered sample **THEN** it SHALL store 0.075 ng/mL, retain the original 75 pg/mL and correction status, and SHALL not apply the collection dilution factor again. | `apps/mobile/tests/export-projection.test.ts:54` — retained sample unit conversion, censored null and collection binding are independently checked<br>`apps/mobile/tests/measurement-format.test.ts:65` — only quantified results display a numeric concentration, preserving a real zero if reported | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-004-02 | Unspecified assay basis — **GIVEN** a report that does not specify free or hydrolyzed analyte **WHEN** it is retained for review **THEN** assay_basis SHALL remain unspecified, the app SHALL expose the unresolved basis, and no compatible-model claim SHALL be made from separate allowed-method and allowed-basis lists alone. | `apps/mobile/tests/measurement-format.test.ts:99` — original report units, laboratory correction, matrix and separate times remain visible<br>`apps/mobile/tests/export-projection.test.ts:54` — retained sample unit conversion, censored null and collection binding are independently checked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1000`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-SAL-005 — Analytical bounds, provenance, and role control

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` / `AND-SAL-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-035-AND-SAL-005-01 | Quantified value outside interval — **GIVEN** a reported value below its method's LOQ but labeled quantified **WHEN** validation runs **THEN** the app and server SHALL reject the inconsistent quantitative record with a field-specific reason and SHALL not coerce it to a valid reading. | `apps/mobile/tests/participant-acquisition.test.ts:364` — accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage<br>`services/api/tests/test_report_revisions.py:543` — test_not_measured_withdrawal_preserves_null_analytical_identity_and_unchanged_analytes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-005-02 | Forged validated source — **GIVEN** a synthetic device or a manually edited local payload **WHEN** it claims validated_sensor with an unknown calibration ID **THEN** the claim SHALL not pass provenance validation, and no qualified concentration or research estimate SHALL result. | `services/api/tests/test_report_revisions.py:543` — test_not_measured_withdrawal_preserves_null_analytical_identity_and_unchanged_analytes<br>`apps/mobile/tests/participant-acquisition.test.ts:364` — accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `6`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-SAL-006 — Adequacy failures, retry, and delayed analysis

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` / `AND-SAL-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-035-AND-SAL-006-01 | Assay disconnect — **GIVEN** a cartridge read in progress **WHEN** the reader disconnects before a verified completion payload **THEN** the app SHALL show Read interrupted, preserve the identified sample and failed analytical attempt, and offer only method-permitted recovery without treating progress as a concentration. | `apps/mobile/tests/report-revisions.test.ts:46` — actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings<br>`apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-006-02 | Corrected laboratory report — **GIVEN** a previously finalized analyte measurement **WHEN** an authorized corrected report is accepted **THEN** the system SHALL preserve the original immutable record, create a linked correction, and make any reanalysis a separately identified result rather than changing past evidence silently. | `apps/mobile/tests/report-revisions.test.ts:46` — actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings<br>`apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-006-03 | Replacing a finalized sample is a new check — **GIVEN** a finalized invalid check with an inadequate specimen and earlier physical task evidence **WHEN** the user chooses to collect another sample **THEN** Start replacement check SHALL allocate a new session/target and require new physical acquisitions without overwriting the original or reusing its task. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization<br>`apps/mobile/tests/report-revisions.test.ts:46` — actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SAL-007 — Review display, API mapping, and platform evidence

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md` / `AND-SAL-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-035-AND-SAL-007-01 | Metabolite panel partly unavailable — **GIVEN** a quantified THC result and two unrun metabolite channels **WHEN** the panel is displayed **THEN** it SHALL show the THC value with provenance and Not measured for each other channel; absence of 11-OH-THC measurement SHALL not be described as evidence of sobriety. | `apps/mobile/tests/measurement-format.test.ts:99` — original report units, laboratory correction, matrix and separate times remain visible<br>`apps/mobile/tests/export-projection.test.ts:54` — retained sample unit conversion, censored null and collection binding are independently checked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-035-AND-SAL-007-02 | Same report on Android and iOS — **GIVEN** the same permitted laboratory report and sample metadata **WHEN** either platform normalizes and renders it **THEN** both SHALL preserve identical numeric meaning, qualifiers, original-report evidence, basis, and lineage, subject only to locale-specific display formatting. | `apps/mobile/tests/measurement-format.test.ts:99` — original report units, laboratory correction, matrix and separate times remain visible<br>`apps/mobile/tests/export-projection.test.ts:54` — retained sample unit conversion, censored null and collection binding are independently checked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.
