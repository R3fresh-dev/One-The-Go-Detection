# Android heart-rate capture

Scope: PPG heart-rate acquisition, context, bounded signal transport, quality, and review, with equivalent iOS behavior. This specification extends HW-002–004/007, APP-010, and LLD section 5.1. A heart-rate reading or sensor confidence value is not an intoxication score. The v0.1 cardiac envelope supports one capture modality; simultaneous PPG and ECG require a future versioned contract.

Shared normative baseline: [shared application contracts](../../shared-contracts.md), especially release/workspace policy, frozen context and companion evidence, qualified online starts, immediate cancellation, immutable artifacts, and the Android/iOS software matrix. These rules govern the same behavior on both platforms.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-HR-001 detailed contract

The Heart rate step SHALL identify the selected source as Simulated pulse or a named verified PPG reader and SHALL show readiness, contact, acquisition progress, quality, and completion states. Actions SHALL include View instructions, Start capture, Cancel, Retry invalid capture, and Continue with missing measurement where permitted. Live values SHALL be labeled bpm and SHALL not be colored or described as intoxicated/sober. A demonstration waveform or generated heart rate SHALL remain explicitly simulated in UI, storage, exports, and server input. The app SHALL not use camera-based pulse estimation, watch data, or a different sensor as an invisible substitute for the configured PPG source.

### AND-HR-002 detailed contract

Physical participant PPG capture SHALL require the approved acquisition configuration, the applicable authorization/consent policy, and a verified device association under the device-pairing specification. The configuration SHALL specify supported sensor/firmware, contact arrangement, duration, posture/rest/activity instructions, valid-sample rules, preprocessing, and quality thresholds. The interface SHALL present those instructions and preserve a recorded compliance/context response when the protocol requires it. A simulator MAY use a named engineering-duration fixture; its timing or quality values SHALL not become clinical defaults. Missing configuration, expired calibration, unsupported firmware, revoked binding, or a capability denial SHALL block participant acquisition with actionable reasons.

Each qualified physical start SHALL require a fresh online authorization/start acknowledgment bound to current generation, session/attempt, approved configuration hash, registered binding, and device boot. Cached capabilities SHALL only display last-known status; changing wall time or rebooting SHALL not enable an offline qualified start. PPG simulator and native uncalibrated phone practice remain distinct locally available actions. The release contains no approved human PPG configuration or active inference model.

### AND-HR-003 detailed contract

Each PpgCaptureAttempt SHALL contain capture/session IDs, modality=ppg, source, device/boot IDs, hardware/firmware/configuration IDs and hashes, acquisition start/end, native monotonic times, phone/device clock uncertainty, sample timing or sample rate with gaps, measured duration, position/activity context, and quality flags. Raw and processed sensor outputs MAY be retained when the approved configuration permits them, with their names and units preserved. Final heart_rate_bpm SHALL be finite and greater than zero only for a valid measured summary; not_collected or invalid output SHALL not carry a fabricated pulse value. Sensor-reported finger detection and confidence SHALL retain their original meaning and scale. ECG status and ECG-derived RMSSD SHALL remain not_collected/null for PPG in the v0.1 envelope.

The complete metadata and authorized artifact/attestation references SHALL be retained in the typed cardiac component of version 1.0.0 CaptureAttempt, hashed in the EvidenceManifest, and cross-checked against the selected v0.1 projection. The registry-bound signed normalized payload SHALL authenticate device/boot/sequence/configuration and actual values; source alone is insufficient. The manifest SHALL preserve earlier modality/failed attempts with their original hashes and SHALL select exactly one cardiac attempt.

### AND-HR-004 detailed contract

The UI SHALL distinguish acquiring, poor_contact, motion_artifact, insufficient_valid_samples, stale_signal, complete, and failed. After contact loss, transport gap, or a stale-data limit from the pinned configuration, the app SHALL stop presenting the previous number as a current reading. It MAY show a visibly timestamped last observation in details; it SHALL not use that value to fill missing samples or declare a completed interval. Capture acceptance SHALL require the configured amount of valid data and verified completion. Smoothing, beat rejection, averaging, interpolation, and missing-data rules SHALL be named by extractor version and SHALL preserve raw quality evidence where authorized.

### AND-HR-005 detailed contract

Cancel SHALL stop capture locally and send a best-effort device cancellation. Disconnect, reader reboot, clock discontinuity, permission loss, or an interruption prohibited by the acquisition protocol SHALL invalidate the active attempt. Retry SHALL create a new capture ID linked to the prior attempt while preserving its failure reason and quality data allowed by policy. A complete immutable capture SHALL survive a later transport loss. Process restart SHALL not convert a partially collected pulse buffer into a completed heart-rate summary. Out-of-order or late events SHALL be checked against device, boot, session, and capture identity before acceptance.

Selecting Cancel, Back, another tab/workspace, or an overlay hiding acquisition SHALL stop local acceptance and settle its invalid/canceled attempt before confirmation or navigation; a Keep draft action cannot resume it. Local withdrawal intent SHALL do the same immediately. Retry before finalization uses a new linked attempt under the same session; after local or remote finalization Start replacement check creates new session/target identities and carries no physical acquisition forward. Late events SHALL also match workspace epoch and account generation before storage.

### AND-HR-006 detailed contract

The review card SHALL show source, modality, acquisition time/duration, captured bpm when valid, quality, posture/activity context, and any incompatible or missing status. Raw PPG or processed beat sequences SHALL be retained only under the applicable consent and retention policy in encrypted private storage. Logs/analytics SHALL not include waveforms, heart rate, or participant identifiers. Allowed local acquisition SHALL continue without network calls on the sensor timing path; upload SHALL remain a separate authorized queued operation. No generated model result SHALL be shown while remote processing is unavailable.

Offline local acquisition here means explicitly synthetic acquisition or native uncalibrated practice; it SHALL not override the fresh online requirement for each qualified PPG start. Save on this device SHALL preserve the complete immutable companion evidence without enqueuing it. Guest checks never upload; an eligible account must separately select Upload check. Authorized artifact verification SHALL recheck withdrawal/generation and pin an immutable S3 VersionId, while ordinary telemetry/logs SHALL contain no signal values. No research_estimate is accepted in this release.

### AND-HR-007 detailed contract

Android and iOS SHALL use the same semantic PPG contract, capability gates, quality states, unit fixtures, and stale-reading rules, while preserving platform-specific timing metadata. Unit/integration tests SHALL cover zero/nonfinite values, wrong modality, stale signal, confidence semantics, sample gaps, duplicate/late events, boot reset, offline durability, and forged verified-source claims. Device tests SHALL verify actual sensor initialization, quality transitions, bounded transport, and end-to-end timing before hardware compatibility is claimed. A display of plausible bpm in a simulator SHALL not close the PPG measurement-performance gate or establish predictive value.

## ADDED Requirements

### Requirement: AND-HR-001 Heart-rate screen and channel availability

The Heart rate step SHALL identify the selected source as Simulated pulse or a named verified PPG reader and SHALL show readiness, contact, acquisition progress, quality, and completion states. The implementation SHALL also satisfy the AND-HR-001 detailed contract above.

#### Scenario: Simulated PPG acquisition

- **GIVEN** synthetic mode and the named demonstration fixture
- **WHEN** the user starts capture
- **THEN** the app SHALL run its bounded fixture sequence, show simulated progress and signal quality, and save simulated provenance with no inference eligibility.

#### Scenario: Unsupported heart-rate device

- **GIVEN** a paired reader without the required PPG capability
- **WHEN** the user opens Heart rate
- **THEN** Start capture SHALL be unavailable with a clear missing-channel reason and SHALL not fall back to an unconfigured phone sensor.

### Requirement: AND-HR-002 Protocol and verified device prerequisites

Physical participant PPG capture SHALL require the approved acquisition configuration, the applicable authorization/consent policy, and a verified device association under the device-pairing specification. The implementation SHALL also satisfy the AND-HR-002 detailed contract above.

#### Scenario: Qualified participant capture prerequisites satisfied

- **GIVEN** a compatible configuration and verified bound reader
- **WHEN** the user acknowledges the applicable instructions and selects Start capture
- **THEN** the app SHALL freeze the configuration and association references for that capture and collect only the requested PPG modality.

#### Scenario: Unprovisioned reader sends a human-looking pulse

- **GIVEN** a synthetic-only unverified BLE connection
- **WHEN** its payload claims a real participant source
- **THEN** ingestion SHALL reject the source claim and SHALL not preserve it as a qualified physiological measurement.

#### Scenario: Network missing at a qualified start

- **GIVEN** a verified reader with previously cached available capability
- **WHEN** the phone is offline when Start capture is selected
- **THEN** the qualified start SHALL remain blocked with current-authorization-unavailable; an old capability timestamp SHALL not authorize collection.

### Requirement: AND-HR-003 PPG capture contract and context

Each PpgCaptureAttempt SHALL contain capture/session IDs, modality=ppg, source, device/boot IDs, hardware/firmware/configuration IDs and hashes, acquisition start/end, native monotonic times, phone/device clock uncertainty, sample timing or sample rate with gaps, measured duration, position/activity context, and quality flags. The implementation SHALL also satisfy the AND-HR-003 detailed contract above.

#### Scenario: PPG device reports confidence

- **GIVEN** a capture containing the sensor's quality/confidence field
- **WHEN** the app renders or exports it
- **THEN** it SHALL label it Sensor signal quality using its documented scale, preserve provenance, and SHALL not display it as probability of correct heart rate or probability of intoxication.

#### Scenario: PPG adapter tries to populate ECG variability

- **GIVEN** a modality=ppg capture
- **WHEN** an adapter supplies ecg_status=valid or ECG-derived RMSSD
- **THEN** schema/semantic validation SHALL reject the incompatible fields rather than labeling pulse-rate variability as ECG heart-rate variability.

### Requirement: AND-HR-004 Live quality and stale-reading prevention

The UI SHALL distinguish acquiring, poor_contact, motion_artifact, insufficient_valid_samples, stale_signal, complete, and failed. The implementation SHALL also satisfy the AND-HR-004 detailed contract above.

#### Scenario: Finger removed during measurement

- **GIVEN** a live valid-looking pulse value
- **WHEN** the sensor reports no finger or the signal becomes stale
- **THEN** the primary live display SHALL change to an actionable contact/stale state, and the old bpm SHALL not continue as if freshly measured.

#### Scenario: Few valid samples within a long recording

- **GIVEN** a recording whose elapsed duration meets the requested duration but whose valid samples do not
- **WHEN** completion is evaluated
- **THEN** the capture SHALL fail its configured adequacy rule or remain incomplete, with no apparently ordinary final heart-rate value.

### Requirement: AND-HR-005 Cancellation, disconnect, and durable attempts

Cancel SHALL stop capture locally and send a best-effort device cancellation. The implementation SHALL also satisfy the AND-HR-005 detailed contract above.

#### Scenario: Reboot resets sensor counter

- **GIVEN** an active PPG capture
- **WHEN** a new boot ID or regressed monotonic counter appears
- **THEN** the attempt SHALL become invalid, the clock association SHALL be cleared, and the next acquisition SHALL require a new capture identity and synchronization.

#### Scenario: Duplicate completion after a successful capture

- **GIVEN** an immutable accepted capture
- **WHEN** its identical completion event is repeated
- **THEN** the app SHALL retain exactly one logical capture, acknowledge the repeated event, and SHALL not overwrite the stored feature or timestamp.

#### Scenario: Canceled route change keeps an ended attempt

- **GIVEN** PPG acquisition is active and a navigation confirmation may be displayed
- **WHEN** the user selects Back and then keeps the wider draft
- **THEN** local acquisition SHALL already have stopped and the prior attempt SHALL retain its terminal invalid/canceled evidence; it SHALL never resume its original buffer.

### Requirement: AND-HR-006 Review, privacy, and offline operation

The review card SHALL show source, modality, acquisition time/duration, captured bpm when valid, quality, posture/activity context, and any incompatible or missing status. The implementation SHALL also satisfy the AND-HR-006 detailed contract above.

#### Scenario: Network unavailable after allowed capture

- **GIVEN** a complete permitted local PPG capture and no network
- **WHEN** the user reaches Review
- **THEN** the app SHALL display the saved measurement and Saved on this device, retain its exact immutable record, and SHALL not claim it was uploaded or analyzed remotely.

#### Scenario: Raw-signal storage not authorized

- **GIVEN** a protocol allowing only summary features
- **WHEN** a PPG stream is processed
- **THEN** raw buffers SHALL remain transient and be released after permitted extraction, while the allowed summary/configuration/quality metadata MAY be saved.

### Requirement: AND-HR-007 Platform parity and acceptance evidence

Android and iOS SHALL use the same semantic PPG contract, capability gates, quality states, unit fixtures, and stale-reading rules, while preserving platform-specific timing metadata. The implementation SHALL also satisfy the AND-HR-007 detailed contract above.

#### Scenario: Same quality-loss fixture on both platforms

- **GIVEN** a recorded synthetic sequence containing good contact, contact loss, and recovery
- **WHEN** Android and iOS replay it
- **THEN** both SHALL show matching quality transitions and SHALL not carry forward the last valid pulse during the gap.

#### Scenario: New firmware changes quality scale

- **GIVEN** a firmware revision outside the configured compatibility list
- **WHEN** the reader reports a confidence field with a different scale
- **THEN** the capture SHALL be blocked or marked incompatible until a reviewed adapter/configuration establishes its meaning; the app SHALL not reuse the prior threshold silently.
