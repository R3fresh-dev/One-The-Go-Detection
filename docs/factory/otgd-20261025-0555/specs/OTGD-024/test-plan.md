# OTGD-024: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md`; SHA-256 `c75f24b4beeda893b780af0d924747c0cd7ca599ead627d3d265f21ec3772895`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/src/device/tests/physical.test.ts` — `23d4938d5015dc6cca7f978a44c3d823f0e9aef3f52631a87898ae5d28c82d9d`
- `apps/mobile/src/device/tests/signal.test.ts` — `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`
- `apps/mobile/tests/cardiac-selection.test.ts` — `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`
- `apps/mobile/tests/eye-acquisition.test.ts` — `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`
- `apps/mobile/tests/raw-artifacts.test.ts` — `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`
- `apps/mobile/tests/raw-upload.test.ts` — `7771c6a9657ccd0dba4d716eb6504e80a97c36290fb6bbd00b6969db2ba769d9`
- `services/api/tests/test_capture_policy.py` — `971a808c066b099c4006aab592d052aa3867d08cdfb10fbd0eb2f5288e5febae`
- `services/api/tests/test_participant_acquisition.py` — `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57`
- `services/api/tests/test_raw_capture.py` — `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-ECG-001 — Optional ECG screen and explicit mode

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` / `AND-ECG-001`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-024-AND-ECG-001-01 | Skip optional ECG — **GIVEN** a workflow in which ECG is optional **WHEN** the user selects Skip ECG **THEN** the check SHALL continue with an explicit not_collected ECG status and null ECG features, without fabricating a normal ECG or marking the entire app unusable. | `services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-001-02 | Run the simulator — **GIVEN** synthetic mode and no ECG hardware **WHEN** the user selects Run simulator **THEN** a deterministic named waveform fixture SHALL exercise capture/progress/review states with simulated source and SHALL not require electrode contact or imply a measured heartbeat. | `services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ECG-002 — Whole-system electrical and authorization gates

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` / `AND-ECG-002`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-024-AND-ECG-002-01 | Approved configuration and verified device — **GIVEN** a valid approved whole-system configuration matching the connected device and permitted operating state **WHEN** the authorized operator initiates capture **THEN** the module SHALL execute only that protocol and retain the binding, approval/configuration hashes, power-state evidence, and lead configuration. | `apps/mobile/tests/raw-artifacts.test.ts:70` — fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop<br>`services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-002-02 | Unreviewed USB-powered body connection — **GIVEN** no matching approved power/connection configuration **WHEN** the device or user requests hardware ECG capture **THEN** the app SHALL reject Start hardware capture, show Electrical configuration not qualified, and SHALL not substitute a simple acknowledgment checkbox for the missing evidence. | `apps/mobile/tests/raw-artifacts.test.ts:70` — fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop<br>`services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-002-03 | Cached gate after device restart — **GIVEN** a cached approved-looking capability and a reader with a new boot ID **WHEN** the operator attempts a hardware start offline **THEN** the app SHALL refuse the start pending fresh online authorization and verified association; it SHALL not reuse the prior boot clock or provide connection instructions from an unresolved configuration. | `apps/mobile/tests/raw-artifacts.test.ts:70` — fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop<br>`services/api/tests/test_participant_acquisition.py:414` — test_human_ecg_state_verification_is_unavailable_even_when_declared_verified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ECG-003 — ECG sample and timing contract

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` / `AND-ECG-003`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-024-AND-ECG-003-01 | Raw ADC counts received — **GIVEN** an otherwise well-formed stream without an approved scale calibration **WHEN** the waveform is reviewed **THEN** the app SHALL label values counts, retain the missing-scale reason, and SHALL not render an mV axis or supply calibrated features that require voltage units. | `apps/mobile/src/device/tests/physical.test.ts:381` — signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest<br>`apps/mobile/src/device/tests/signal.test.ts:113` — ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-003-02 | Sample gap inside a recording — **GIVEN** a stream with a missing block or nonconsecutive sample index **WHEN** reassembly completes or times out **THEN** the gap SHALL be represented explicitly and the applicable quality rule enforced; the app SHALL not draw a continuous valid trace by interpolating away lost evidence. | `apps/mobile/src/device/tests/physical.test.ts:381` — signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest<br>`apps/mobile/src/device/tests/signal.test.ts:113` — ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1`, `1.0`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-ECG-004 — Native display and feature restrictions

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` / `AND-ECG-004`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-024-AND-ECG-004-01 | Waveform visually smooth but inadequate for HRV — **GIVEN** a capture shorter than its extractor's approved duration or with too few usable beat intervals **WHEN** the summary is generated **THEN** the waveform MAY remain available within policy but RMSSD SHALL be null with an adequacy reason, not a guessed feature. | `apps/mobile/src/device/tests/signal.test.ts:113` — ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples<br>`apps/mobile/tests/cardiac-selection.test.ts:97` — interrupted ECG alternative preserves valid PPG and does not copy its physiological features | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-004-02 | Heavy rendering load — **GIVEN** a supported synthetic or approved stream **WHEN** the screen drops rendering frames **THEN** raw sample acquisition SHALL remain independently bounded, display lag SHALL be reported where relevant, and lost acquisition samples SHALL not be hidden by the appearance of the graph. | `apps/mobile/src/device/tests/signal.test.ts:113` — ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples<br>`apps/mobile/tests/cardiac-selection.test.ts:97` — interrupted ECG alternative preserves valid PPG and does not copy its physiological features | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ECG-005 — Contact loss, interruption, and retry

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` / `AND-ECG-005`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-024-AND-ECG-005-01 | Lead detaches during capture — **GIVEN** an active hardware or simulator lead-off test **WHEN** contact is lost **THEN** the UI SHALL show Lead contact lost, retain lead-off timing, and apply the fixed protocol's stop/invalid behavior without continuing to display an unqualified live heart rate as current. | `services/api/tests/test_participant_acquisition.py:380` — test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample<br>`apps/mobile/tests/raw-artifacts.test.ts:70` — fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-005-02 | Late samples after cancellation — **GIVEN** a canceled ECG capture **WHEN** remaining Bluetooth notifications arrive **THEN** those samples SHALL be rejected by capture identity and SHALL not populate a later attempt or turn the canceled attempt complete. | `apps/mobile/src/device/tests/signal.test.ts:144` — local ECG stream keeps the exact ten-message complete evidence and connection observation time separate from samples<br>`services/api/tests/test_participant_acquisition.py:380` — test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ECG-006 — One-modality contract and review semantics

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` / `AND-ECG-006`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-024-AND-ECG-006-01 | User selects ECG after a PPG capture — **GIVEN** a check with an accepted PPG cardiac component **WHEN** the user selects the allowed ECG alternative **THEN** the UI SHALL explain that v0.1 selects one cardiac modality, preserve the PPG attempt, and require an explicit selection of which accepted capture becomes the final cardiac component. | `apps/mobile/tests/cardiac-selection.test.ts:31` — one PPG plus one ECG is retained and requires an explicit final choice<br>`services/api/tests/test_capture_policy.py:59` — test_one_valid_cardiac_attempt_per_modality_allows_alternative_without_retake | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-006-02 | Protocol demands both modalities — **GIVEN** the installed client supports only the v0.1 cardiac schema **WHEN** a protocol requires both PPG and ECG as distinct model inputs **THEN** capability resolution SHALL report Unsupported cardiac contract and SHALL not merge the two sources or fabricate a compatible feature vector. | `apps/mobile/tests/cardiac-selection.test.ts:282` — selection rejects another check, invalid attempts, active capture and saved changes<br>`services/api/tests/test_participant_acquisition.py:559` — test_pending_sample_blocks_finalization_until_explicit_cancellation_without_erasing_history | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-006-03 | Optional ECG skip preserves selected PPG — **GIVEN** a pre-finalization check with a valid selected PPG capture **WHEN** the user selects Skip ECG **THEN** the PPG selection SHALL remain unchanged, ECG SHALL remain explicitly not_collected, and no mixed-modality v0.1 component SHALL be created. | `apps/mobile/tests/cardiac-selection.test.ts:282` — selection rejects another check, invalid attempts, active capture and saved changes<br>`services/api/tests/test_capture_policy.py:59` — test_one_valid_cardiac_attempt_per_modality_allows_alternative_without_retake | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-ECG-007 — Privacy, offline behavior, and verification

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md` / `AND-ECG-007`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-024-AND-ECG-007-01 | Offline completed simulation — **GIVEN** a complete synthetic ECG capture with the network disabled **WHEN** the user saves the check **THEN** the app SHALL store the permitted fictional record locally, retain its simulated label, and show sync status independently from capture completion. | `apps/mobile/tests/raw-upload.test.ts:221` — Save and metadata-only upload never read or queue raw; explicit selection is immutable and exact<br>`apps/mobile/src/device/tests/physical.test.ts:231` — physical advertisement has a distinct bounded dialect and never a synthetic/validated source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-024-AND-ECG-007-02 | Missing raw-data retention policy — **GIVEN** a proposed participant protocol without a resolved ECG retention policy **WHEN** recording or upload is requested **THEN** the app SHALL block the dependent recording/upload path and SHALL not choose indefinite retention as a fallback. | `apps/mobile/tests/raw-upload.test.ts:221` — Save and metadata-only upload never read or queue raw; explicit selection is immutable and exact<br>`services/api/tests/test_participant_acquisition.py:559` — test_pending_sample_blocks_finalization_until_explicit_cancellation_without_erasing_history | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.
