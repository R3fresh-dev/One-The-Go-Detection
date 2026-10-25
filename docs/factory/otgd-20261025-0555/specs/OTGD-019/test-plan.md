# OTGD-019: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md`; SHA-256 `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/mobile.spec.ts` — `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`
- `apps/mobile/tests/domain.test.ts` — `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`
- `apps/mobile/tests/export-projection.test.ts` — `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`
- `apps/mobile/tests/measurement-format.test.ts` — `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_model_engine.py` — `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-ALC-001 — Display actual alcohol availability

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md` / `AND-ALC-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-019-AND-ALC-001-01 | Only the starter PPG board is connected — **GIVEN** a Nano ESP32 and PPG module without a calibrated breath channel **WHEN** Alcohol is opened **THEN** the app shows hardware-required guidance and does not start a blow timer or produce an alcohol value. | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence<br>`apps/mobile/tests/measurement-format.test.ts:35` — missing limits produce a qualifier without an invented cutoff | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-019-AND-ALC-001-02 | Approved configuration is missing — **GIVEN** a connected device advertises alcohol capability without an approved configuration **WHEN** sampling is requested **THEN** the app and server reject the request with a configuration-unavailable reason. | `services/api/tests/test_api.py:412` — test_unprovisioned_device_and_human_capture_unavailable<br>`apps/mobile/tests/measurement-format.test.ts:35` — missing limits produce a qualifier without an invented cutoff | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ALC-002 — Keep alcohol records independent

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md` / `AND-ALC-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-019-AND-ALC-002-01 | Combined session has two measured channels — **GIVEN** independently valid alcohol and cannabis records **WHEN** session detail is displayed **THEN** each channel has its own card, units, timing, and validity explanation. | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence<br>`apps/mobile/tests/domain.test.ts:84` — all retained measurement and application DTO schema copies match source contracts | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-019-AND-ALC-002-02 | Cannabis result is unavailable — **GIVEN** a valid authorized alcohol record and unavailable cannabis inference **WHEN** results render **THEN** the alcohol measurement does not manufacture a cannabis estimate. | `apps/mobile/tests/domain.test.ts:323` — every research_estimate is rejected even when its shape could be schema-valid<br>`apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ALC-003 — Preserve mg/L and qualifiers

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md` / `AND-ALC-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-019-AND-ALC-003-01 | Quantified record arrives — **GIVEN** an in-range qualified measurement in mg/L **WHEN** the record is validated and displayed **THEN** its numeric value and mg/L label remain paired. | `apps/mobile/tests/measurement-format.test.ts:23` — below LOQ displays the supplied bound without creating a concentration or rounding it to zero<br>`apps/mobile/tests/domain.test.ts:117` — duplicate escaped keys, unknown numeric values and excessive JSON depth are rejected | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-019-AND-ALC-003-02 | Caller submits a BAC percentage — **GIVEN** a value labeled percent BAC **WHEN** it is submitted to the breath-alcohol route **THEN** the service rejects the incompatible unit and performs no conversion. | `apps/mobile/tests/export-projection.test.ts:54` — retained sample unit conversion, censored null and collection binding are independently checked<br>`apps/mobile/tests/measurement-format.test.ts:23` — below LOQ displays the supplied bound without creating a concentration or rounding it to zero | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ALC-004 — Require calibration and sample adequacy

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md` / `AND-ALC-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-019-AND-ALC-004-01 | Sampling is inadequate — **GIVEN** the device reports an inadequate breath sample **WHEN** acquisition ends **THEN** the result is invalid with no exact concentration and an actionable retry explanation. | `apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-019-AND-ALC-004-02 | Calibration expires — **GIVEN** the instrument calibration is outside its qualified interval **WHEN** a new record is requested **THEN** the app blocks qualified sampling and identifies recalibration as the required action. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |

### AND-ALC-005 — Isolate fictional demonstrations

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md` / `AND-ALC-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-019-AND-ALC-005-01 | Demo is intentionally opened — **GIVEN** the development demo action **WHEN** the customer previews the channel **THEN** every value is labeled fictional and no real measurement claim is made. | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-019-AND-ALC-005-02 | Simulated record targets a participant session — **GIVEN** a nonsynthetic parent session **WHEN** a simulated alcohol record is submitted **THEN** the service rejects the provenance mismatch. | `apps/mobile/tests/export-projection.test.ts:29` — every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence<br>`apps/mobile/tests/domain.test.ts:178` — engineering fixture has an isolated unknown synthetic profile and absent simulated task | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ALC-006 — Prohibit combined impairment shortcuts

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md` / `AND-ALC-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-019-AND-ALC-006-01 | Alcohol co-use is present — **GIVEN** the cannabis model does not support alcohol co-use **WHEN** a future research request is evaluated **THEN** the unsupported cohort is handled by the manifest gate rather than a score adjustment in the app. | `services/api/tests/test_model_engine.py:364` — test_every_acquisition_gate_has_rejection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-019-AND-ALC-006-02 | A low displayed value — **GIVEN** a low or censored alcohol result **WHEN** the result screen is shown **THEN** no **Safe to drive** or legal-clearance message appears. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
