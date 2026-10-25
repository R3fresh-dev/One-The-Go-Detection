# OTGD-025: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md`; SHA-256 `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/raw-recordings.spec.ts` — `0d2a3a316e8c1b4eadadaef61e57dde071bf7a94b7a6bad8820d1e54619383af`
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt` — `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift` — `5efcf344d7a09069f312fa3e89b08cfca833293b955fb781a31b947813b38bac`
- `apps/mobile/tests/eye-acquisition.test.ts` — `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`
- `apps/mobile/tests/raw-artifacts.test.ts` — `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`
- `services/api/tests/test_optical_evidence.py` — `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`
- `services/api/tests/test_raw_capture.py` — `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-EYE-001 — Eye screen and passive preview

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` / `AND-EYE-001`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-025-AND-EYE-001-01 | Preview without an approved optical configuration — **GIVEN** camera permission and no qualified optical configuration **WHEN** the user chooses Preview positioning **THEN** a passive camera preview SHALL appear without stimulus, recording, or derived features, and ending it SHALL leave the eye component not_collected. | `apps/mobile/e2e/raw-recordings.spec.ts:86` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset<br>`services/api/tests/test_optical_evidence.py:358` — test_descriptive_native_change_cannot_become_unqualified_pupil_response | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-001-02 | Synthetic eye fixture — **GIVEN** P0 demonstration mode **WHEN** the user explicitly chooses the synthetic eye example **THEN** the stored component SHALL be labeled simulated, retain its fictional fixture/configuration ID, and SHALL not be represented as an extraction from the user's preview. | `apps/mobile/e2e/raw-recordings.spec.ts:86` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset<br>`services/api/tests/test_optical_evidence.py:358` — test_descriptive_native_change_cannot_become_unqualified_pupil_response | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EYE-002 — Camera permission and lifecycle

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` / `AND-EYE-002`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-025-AND-EYE-002-01 | Permission permanently denied — **GIVEN** Android has denied camera permission permanently **WHEN** the user selects preview **THEN** the screen SHALL explain the missing permission, offer Open settings and Back to check, and SHALL not enter an indefinite loading state. | `apps/mobile/tests/raw-artifacts.test.ts:39` — native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff<br>`apps/mobile/tests/eye-acquisition.test.ts:300` — camera failure before the first frame preserves its original reason and arming metadata without inventing acquired clocks | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-002-02 | Backgrounded active capture — **GIVEN** an authorized optical capture in progress **WHEN** the app loses foreground activity **THEN** the stimulus SHALL stop, camera resources SHALL be released, the attempt SHALL become invalid, and returning SHALL require a new linked attempt. | `apps/mobile/tests/raw-artifacts.test.ts:39` — native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff<br>`apps/mobile/tests/eye-acquisition.test.ts:300` — camera failure before the first frame preserves its original reason and arming metadata without inventing acquired clocks | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EYE-003 — Approved configuration and stimulus authorization

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` / `AND-EYE-003`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-025-AND-EYE-003-01 | Qualified capture configuration available — **GIVEN** a valid matching optical configuration and all required authorizations **WHEN** the user reviews its instructions and selects Start capture **THEN** the native module SHALL execute only the bounded approved sequence and store its exact configuration hash and timing evidence. | `apps/mobile/tests/eye-acquisition.test.ts:230` — feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock<br>`apps/mobile/e2e/raw-recordings.spec.ts:899` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-003-02 | Local override requests phone flash — **GIVEN** no approved configuration or a configuration for a different phone **WHEN** a deep link or modified local preference requests stimulus capture **THEN** the module and orchestration gate SHALL reject the request and SHALL not activate the flash, torch, or modulated screen. | `apps/mobile/tests/eye-acquisition.test.ts:230` — feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock<br>`apps/mobile/e2e/raw-recordings.spec.ts:899` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-003-03 | Offline cached optical approval — **GIVEN** a previously available cached optical capability and a current camera permission **WHEN** the user enables airplane mode and selects Start capture **THEN** the app SHALL require a fresh online capture acknowledgment and SHALL leave all participant stimulus output disabled; passive preview remains a separately labeled action. | `apps/mobile/tests/eye-acquisition.test.ts:230` — feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock<br>`apps/mobile/e2e/raw-recordings.spec.ts:899` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EYE-004 — Native frame and illumination evidence

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` / `AND-EYE-004`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-025-AND-EYE-004-01 | Flash request has no verified physical onset — **GIVEN** a recorded OS stimulus request and frame callbacks **WHEN** the hardware lacks verified physical onset evidence **THEN** the record SHALL mark timing evidence unverified or estimated, and an extractor requiring measured onset SHALL produce no qualified response latency. | `apps/mobile/tests/eye-acquisition.test.ts:33` — actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency<br>`services/api/tests/test_optical_evidence.py:367` — test_sensor_sensitivity_metadata_is_bounded_observed_number | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-004-02 | Variable camera cadence — **GIVEN** frame timestamps showing drops or irregular intervals **WHEN** feature eligibility is evaluated **THEN** the app SHALL retain actual cadence and gap evidence, apply the frozen configuration's quality rules, and SHALL not fabricate a constant high-rate sequence from requested FPS. | `services/api/tests/test_optical_evidence.py:367` — test_sensor_sensitivity_metadata_is_bounded_observed_number<br>`apps/mobile/tests/raw-artifacts.test.ts:39` — native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1`, `1 MiB`, `1.0`, `512 KiB`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-EYE-005 — Geometry, feature units, and quality

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` / `AND-EYE-005`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-025-AND-EYE-005-01 | Pixels supplied as millimeters — **GIVEN** a segmentation result with image-pixel diameter and no scale calibration **WHEN** an adapter attempts to populate diameter_mm **THEN** validation SHALL reject the unit conversion and retain only a correctly labeled pixel or dimensionless observation when permitted. | `apps/mobile/e2e/raw-recordings.spec.ts:86` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset<br>`apps/mobile/tests/eye-acquisition.test.ts:33` — actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-005-02 | Eye lost during response window — **GIVEN** a capture with required frames obscured by blink or tracking loss **WHEN** the extractor applies the approved quality policy **THEN** the affected feature SHALL be null or the capture invalid according to that policy, with the reason retained; it SHALL not impute an apparently normal response. | `services/api/tests/test_optical_evidence.py:289` — test_invalid_capture_counts_and_null_features_do_not_become_positive<br>`apps/mobile/e2e/raw-recordings.spec.ts:86` — eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EYE-006 — Raw artifact consent, minimization, and deletion

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` / `AND-EYE-006`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-025-AND-EYE-006-01 | User declines raw recording — **GIVEN** a protocol that permits local feature extraction without raw retention **WHEN** the user declines optional recording **THEN** raw data SHALL not be persisted or uploaded, and only explicitly permitted features and quality metadata MAY be retained. | `apps/mobile/tests/eye-acquisition.test.ts:335` — optional ROI handoff commits encrypted bytes plus exact receipt atomically, releases native RAM, and never queues upload<br>`apps/mobile/e2e/raw-recordings.spec.ts:671` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-006-02 | Artifact upload fails — **GIVEN** an authorized retained capture and a network interruption **WHEN** upload cannot complete **THEN** the UI SHALL show pending upload, retain the immutable local artifact only within its permitted lifetime, and SHALL not mark a partial remote object available for extraction. | `apps/mobile/e2e/raw-recordings.spec.ts:899` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload<br>`apps/mobile/tests/raw-artifacts.test.ts:70` — fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-006-03 | Withdrawal races with an issued upload ticket — **GIVEN** an optical artifact PUT URL issued before withdrawal **WHEN** the user withdraws locally and the server accepts withdrawal while old bytes arrive **THEN** local capture/queue work SHALL stop immediately, the server SHALL refuse artifact verification/evidence acceptance, and any uploaded version SHALL remain quarantined for scoped cleanup. | `services/api/tests/test_raw_capture.py:635` — test_http_raw_completion_authenticates_device_chunks_and_keeps_forgery_quarantined<br>`apps/mobile/e2e/raw-recordings.spec.ts:899` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EYE-007 — Review, parity, and evidence boundaries

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md` / `AND-EYE-007`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-025-AND-EYE-007-01 | Review after passive preview — **GIVEN** a user who previewed positioning but performed no authorized measurement **WHEN** Review is opened **THEN** Eyes SHALL show Not collected with Preview only context and null measured features rather than a successful pupil test. | `apps/mobile/tests/eye-acquisition.test.ts:230` — feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock<br>`services/api/tests/test_optical_evidence.py:289` — test_invalid_capture_counts_and_null_features_do_not_become_positive | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-025-AND-EYE-007-02 | Cross-platform camera capability mismatch — **GIVEN** an optical configuration qualified for a specific iPhone but not the Android device in use **WHEN** Android requests measurement capture **THEN** Android SHALL remain blocked with Unsupported optical configuration while iOS compatibility is assessed independently; visual similarity SHALL not establish equivalence. | `apps/mobile/tests/eye-acquisition.test.ts:230` — feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock<br>`apps/mobile/tests/raw-artifacts.test.ts:70` — fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `16.4`, `24`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
