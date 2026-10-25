# OTGD-027: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md`; SHA-256 `e9288b9fbec177d7287962239555b7633a0cfbf80ecf3e1e350158da607f5139`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/src/device/tests/physical.test.ts` — `23d4938d5015dc6cca7f978a44c3d823f0e9aef3f52631a87898ae5d28c82d9d`
- `apps/mobile/src/device/tests/protocol.test.ts` — `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`
- `apps/mobile/src/device/tests/signal.test.ts` — `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`
- `apps/mobile/tests/acquisition.test.ts` — `5a87445ae4174cdf15eccd8ec0b6b67105fea10d338aec183d1362ae6f8bfb9b`
- `apps/mobile/tests/cardiac-selection.test.ts` — `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`
- `apps/mobile/tests/device-presentation.test.ts` — `11e79b59ead32c0a6bc4fa818784bc00347f337cfb5dff71d13534673064600a`
- `services/api/tests/test_capture_signing.py` — `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`
- `services/api/tests/test_vendor_evidence.py` — `ffb2ca5111d52df5d295f0e594a6eb00b17465c452c0abb21a4d2fb79a8930fe`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-HR-001 — Heart-rate screen and channel availability

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` / `AND-HR-001`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-027-AND-HR-001-01 | Simulated PPG acquisition — **GIVEN** synthetic mode and the named demonstration fixture **WHEN** the user starts capture **THEN** the app SHALL run its bounded fixture sequence, show simulated progress and signal quality, and save simulated provenance with no inference eligibility. | `apps/mobile/src/device/tests/signal.test.ts:62` — all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion<br>`apps/mobile/src/device/tests/protocol.test.ts:87` — local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-001-02 | Unsupported heart-rate device — **GIVEN** a paired reader without the required PPG capability **WHEN** the user opens Heart rate **THEN** Start capture SHALL be unavailable with a clear missing-channel reason and SHALL not fall back to an unconfigured phone sensor. | `apps/mobile/src/device/tests/signal.test.ts:62` — all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion<br>`apps/mobile/tests/device-presentation.test.ts:43` — intermediate or unverified connection states never claim capture readiness | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HR-002 — Protocol and verified device prerequisites

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` / `AND-HR-002`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-027-AND-HR-002-01 | Qualified participant capture prerequisites satisfied — **GIVEN** a compatible configuration and verified bound reader **WHEN** the user acknowledges the applicable instructions and selects Start capture **THEN** the app SHALL freeze the configuration and association references for that capture and collect only the requested PPG modality. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/physical.test.ts:654` — actual backend bound-reader HTTP fixture passes strict physical token and exact material digest | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-002-02 | Unprovisioned reader sends a human-looking pulse — **GIVEN** a synthetic-only unverified BLE connection **WHEN** its payload claims a real participant source **THEN** ingestion SHALL reject the source claim and SHALL not preserve it as a qualified physiological measurement. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/protocol.test.ts:60` — capability source and calibration cannot promote an unprovisioned peripheral | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-002-03 | Network missing at a qualified start — **GIVEN** a verified reader with previously cached available capability **WHEN** the phone is offline when Start capture is selected **THEN** the qualified start SHALL remain blocked with current-authorization-unavailable; an old capability timestamp SHALL not authorize collection. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/physical.test.ts:654` — actual backend bound-reader HTTP fixture passes strict physical token and exact material digest | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HR-003 — PPG capture contract and context

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` / `AND-HR-003`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-027-AND-HR-003-01 | PPG device reports confidence — **GIVEN** a capture containing the sensor's quality/confidence field **WHEN** the app renders or exports it **THEN** it SHALL label it Sensor signal quality using its documented scale, preserve provenance, and SHALL not display it as probability of correct heart rate or probability of intoxication. | `apps/mobile/src/device/tests/signal.test.ts:127` — typed signal failures settle only their exact simulated attempt with null physiology and existing scalar metadata<br>`apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-003-02 | PPG adapter tries to populate ECG variability — **GIVEN** a modality=ppg capture **WHEN** an adapter supplies ecg_status=valid or ECG-derived RMSSD **THEN** schema/semantic validation SHALL reject the incompatible fields rather than labeling pulse-rate variability as ECG heart-rate variability. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/signal.test.ts:81` — stale identities, schema additions, sequence replay and bounded sample tampering cannot populate a current capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1`, `1.0`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-HR-004 — Live quality and stale-reading prevention

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` / `AND-HR-004`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-027-AND-HR-004-01 | Finger removed during measurement — **GIVEN** a live valid-looking pulse value **WHEN** the sensor reports no finger or the signal becomes stale **THEN** the primary live display SHALL change to an actionable contact/stale state, and the old bpm SHALL not continue as if freshly measured. | `apps/mobile/src/device/tests/signal.test.ts:113` — ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-004-02 | Few valid samples within a long recording — **GIVEN** a recording whose elapsed duration meets the requested duration but whose valid samples do not **WHEN** completion is evaluated **THEN** the capture SHALL fail its configured adequacy rule or remain incomplete, with no apparently ordinary final heart-rate value. | `apps/mobile/src/device/tests/signal.test.ts:144` — local ECG stream keeps the exact ten-message complete evidence and connection observation time separate from samples<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HR-005 — Cancellation, disconnect, and durable attempts

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` / `AND-HR-005`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-027-AND-HR-005-01 | Reboot resets sensor counter — **GIVEN** an active PPG capture **WHEN** a new boot ID or regressed monotonic counter appears **THEN** the attempt SHALL become invalid, the clock association SHALL be cleared, and the next acquisition SHALL require a new capture identity and synchronization. | `apps/mobile/tests/cardiac-selection.test.ts:282` — selection rejects another check, invalid attempts, active capture and saved changes<br>`apps/mobile/src/device/tests/physical.test.ts:604` — cancellation clears trusted association immediately and drops a late signed completion | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-005-02 | Duplicate completion after a successful capture — **GIVEN** an immutable accepted capture **WHEN** its identical completion event is repeated **THEN** the app SHALL retain exactly one logical capture, acknowledge the repeated event, and SHALL not overwrite the stored feature or timestamp. | `apps/mobile/tests/cardiac-selection.test.ts:282` — selection rejects another check, invalid attempts, active capture and saved changes<br>`apps/mobile/tests/acquisition.test.ts:1265` — delayed initial intent commit cannot overwrite the replacement reader's newer intent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-005-03 | Canceled route change keeps an ended attempt — **GIVEN** PPG acquisition is active and a navigation confirmation may be displayed **WHEN** the user selects Back and then keeps the wider draft **THEN** local acquisition SHALL already have stopped and the prior attempt SHALL retain its terminal invalid/canceled evidence; it SHALL never resume its original buffer. | `apps/mobile/tests/cardiac-selection.test.ts:282` — selection rejects another check, invalid attempts, active capture and saved changes<br>`apps/mobile/tests/device-presentation.test.ts:23` — permission, radio, reboot and unsupported reader failures have distinct recovery | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HR-006 — Review, privacy, and offline operation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` / `AND-HR-006`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-027-AND-HR-006-01 | Network unavailable after allowed capture — **GIVEN** a complete permitted local PPG capture and no network **WHEN** the user reaches Review **THEN** the app SHALL display the saved measurement and Saved on this device, retain its exact immutable record, and SHALL not claim it was uploaded or analyzed remotely. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/signal.test.ts:144` — local ECG stream keeps the exact ten-message complete evidence and connection observation time separate from samples | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-006-02 | Raw-signal storage not authorized — **GIVEN** a protocol allowing only summary features **WHEN** a PPG stream is processed **THEN** raw buffers SHALL remain transient and be released after permitted extraction, while the allowed summary/configuration/quality metadata MAY be saved. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/signal.test.ts:144` — local ECG stream keeps the exact ten-message complete evidence and connection observation time separate from samples | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HR-007 — Platform parity and acceptance evidence

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md` / `AND-HR-007`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-027-AND-HR-007-01 | Same quality-loss fixture on both platforms — **GIVEN** a recorded synthetic sequence containing good contact, contact loss, and recovery **WHEN** Android and iOS replay it **THEN** both SHALL show matching quality transitions and SHALL not carry forward the last valid pulse during the gap. | `apps/mobile/src/device/tests/signal.test.ts:81` — stale identities, schema additions, sequence replay and bounded sample tampering cannot populate a current capture<br>`apps/mobile/src/device/tests/physical.test.ts:231` — physical advertisement has a distinct bounded dialect and never a synthetic/validated source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-027-AND-HR-007-02 | New firmware changes quality scale — **GIVEN** a firmware revision outside the configured compatibility list **WHEN** the reader reports a confidence field with a different scale **THEN** the capture SHALL be blocked or marked incompatible until a reviewed adapter/configuration establishes its meaning; the app SHALL not reuse the prior threshold silently. | `apps/mobile/src/device/tests/signal.test.ts:81` — stale identities, schema additions, sequence replay and bounded sample tampering cannot populate a current capture<br>`apps/mobile/tests/acquisition.test.ts:1501` — scope-qualified preparation End stops the advanced capture token before a deferred server start reaches hardware | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
