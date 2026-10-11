# Android ECG capture

Scope: optional ECG simulator workflow and a gated interface for qualified hardware. Android and iOS SHALL preserve equivalent acquisition, quality, privacy, and failure semantics. This specification extends HW-005–007, SEC-003–005, and LLD section 5.1. The present cardiac contract represents one modality per component; a future combined PPG-plus-ECG check requires a separately versioned schema and compatibility decision.

Shared normative baseline: [shared application contracts](../../shared-contracts.md), especially release/workspace policy, frozen context and companion evidence, qualified online starts, immediate cancellation, immutable artifacts, and the Android/iOS software matrix. These rules govern the same behavior on both platforms.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-ECG-001 detailed contract

The guided check SHALL expose ECG as optional unless a future authorized protocol explicitly requires it. The screen SHALL state Simulator available or Qualified hardware required and SHALL provide Run simulator, View hardware requirements, and Skip ECG as applicable. Participant connection instructions and Start hardware capture SHALL remain unavailable until the electrical and protocol prerequisites are independently satisfied. Simulator traces SHALL be labeled Simulated ECG, remain synthetic throughout storage/export, and SHALL not be described as the user's rhythm. The feature SHALL not identify arrhythmia, a heart condition, cannabis intoxication, or a driving decision.

### AND-ECG-002 detailed contract

Human-connected ECG acquisition SHALL require a reviewed whole-system hardware configuration, G-05 approval evidence, a permitted power/charging/cable state, lead/contact configuration, firmware/ADC/front-end versions, a verified device binding, and an authorized protocol/consent/retention decision from the capabilities service. Review SHALL cover the actual power source, isolation, exposed conductors, enclosure, USB equipment, electrodes, and charging arrangement together. Selection of an AD8232 or other front-end IC, battery use by itself, or a user checkbox SHALL not close this gate. The app SHALL expose exact unresolved prerequisites and implement a refusal path; it SHALL not ship a hidden override that enables participant connection.

The app SHALL request a fresh online authorization/start acknowledgment for each qualified hardware attempt and pin its account generation, exact configuration, binding, boot, and attempt references. Cached capabilities SHALL only explain availability and cannot authorize an offline body-connected start. Actual registry/qualification evidence remains required even when a response or local setting says available; the current release contains no approved human ECG configuration. Local withdrawal intent SHALL stop dependent acquisition immediately without awaiting a server response.

### AND-ECG-003 detailed contract

An EcgCaptureAttempt SHALL retain capture/session/device/boot IDs, modality=ecg, source, lead configuration, hardware/firmware/configuration versions, start/end UTC and native monotonic times, sampling clock/source, sample rate or explicit sample timestamps, gap/drop markers, ADC gain/reference/scaling, filter version, contact/lead-off status, and quality flags. Calibrated waveform samples SHALL use mV; raw ADC data SHALL remain counts until the named calibration justifies conversion. The stream SHALL be chunked into bounded transport blocks and accepted only after verified total length and final digest. Any gain, sample-rate, lead, or filter change during a capture SHALL invalidate or start a new explicitly identified segment according to the pinned protocol; it SHALL not be silently mixed into one homogeneous trace.

Full structured metadata and approved artifact/attestation references SHALL use the version 1.0.0 typed cardiac CaptureAttempt, preserving every failed/superseded attempt in the hashed EvidenceManifest. The selected v0.1 projection SHALL agree on capture ID, modality, times, status, source, and features. The server SHALL verify the shared device-signed envelope against exact normalized payload bytes and current registry/configuration scope. Raw waveform bytes SHALL remain outside bounded metadata and use immutable verified artifact-version references only under an actual approved retention scope.

### AND-ECG-004 detailed contract

The native/React Native presentation SHALL display a bounded scrolling waveform and acquisition status without blocking sample ingestion. Visual decimation MAY reduce points for rendering but SHALL not change the stored samples or extractor input. An ECG summary MAY include heart rate and RR/HRV features only when a named extractor, valid beat detection, required duration, artifact policy, and compatible protocol support them. RMSSD, if produced, SHALL use milliseconds and preserve its preprocessing and eligible interval count. Unqualified duration, lead-off, clipping, corrupted rhythm extraction, or insufficient valid beats SHALL yield null affected features with reasons. An ECG waveform SHALL not be generated from PPG or from a heart-rate number.

### AND-ECG-005 detailed contract

The screen SHALL distinguish waiting_for_contact, acquiring, lead_off, saturated, poor_signal, transport_gap, complete, and invalid. It SHALL react to lead-off and disallowed power-state changes using the approved hardware/protocol rule. User cancellation, device reboot, changed boot identity, transport failure, permission loss, or prohibited app interruption SHALL stop acceptance of the current attempt and produce an explicit final disposition. Retry SHALL create a linked new capture. A complete record SHALL remain immutable. Recovery SHALL never continue a stream across device restarts using the old sampling clock or copy a prior valid ECG summary into the new attempt.

Cancel, Back, a tab/workspace change, or an acquisition-hiding overlay SHALL stop acceptance and settle the original attempt before navigation or wider-draft confirmation. Keeping the draft SHALL not resume the ended stream. Before finalization a permitted retry creates a linked new attempt and fresh qualified start; after local or remote finalization it requires Start replacement check with a new session/target and no physical component reuse. Late events SHALL also match workspace epoch and account generation.

### AND-ECG-006 detailed contract

For the existing v0.1 session cardiac envelope, the app SHALL accept either PPG or ECG as the selected cardiac capture. Switching to ECG after PPG SHALL explicitly explain the selection and preserve the earlier attempt in local/history lineage; it SHALL not silently overwrite or label the PPG record ECG. Separate observations MAY remain visible in an attempt ledger, but both SHALL not be squeezed into the same envelope. A future protocol that requires simultaneous PPG and ECG SHALL be blocked until its new multi-capture contract and model compatibility are implemented. Review SHALL show source, modality, lead/scaling/timing status, actual duration, quality, retained features, and skipped/invalid reasons.

Modality selection SHALL be explicit before local/remote finalization and persisted in the companion manifest; all earlier attempts SHALL remain retrievable through /v1/sessions/{id}/evidence and scoped export. Once saved, selection is immutable. A later physical acquisition uses the replacement-check rule rather than appending ECG to a finalized PPG check. ECG Skip SHALL not erase an already selected permitted PPG component.

### AND-ECG-007 detailed contract

ECG traces SHALL remain in encrypted application-private storage only when explicitly authorized by a resolved retention policy. Raw traces SHALL not enter analytics, crash logs, general device backup, image galleries, or public repository fixtures. Allowed local acquisition SHALL not require a cloud round trip for each sample; authorized uploads SHALL use bounded artifact transfer and verified digest completion. Android and iOS tests SHALL cover deterministic simulator output, counts-versus-mV, lead-off, gaps, saturation, cancellation, reboot, missing approval, rejected source substitution, and modality conflicts. Physical electrical testing and independent configuration review SHALL be reported as outstanding until real evidence is available; passing simulator tests SHALL not be described as approval for body-connected use.

The no-per-sample-network rule SHALL not authorize an offline qualified start. Offline operation in this release permits the labeled simulator and review of already permitted saved data. Save on this device SHALL not queue anything; guest records never upload, while eligible account Upload check is a distinct explicit action. Server artifact completion SHALL verify and pin a non-null S3 VersionId and recheck consent/withdrawal/account generation. An old presigned PUT may create only quarantined bytes; authenticated downloads SHALL recheck owner/policy and serve the pinned verified version. This release SHALL reject research_estimate and keep probability null.

## ADDED Requirements

### Requirement: AND-ECG-001 Optional ECG screen and explicit mode

The guided check SHALL expose ECG as optional unless a future authorized protocol explicitly requires it. The implementation SHALL also satisfy the AND-ECG-001 detailed contract above.

#### Scenario: Skip optional ECG

- **GIVEN** a workflow in which ECG is optional
- **WHEN** the user selects Skip ECG
- **THEN** the check SHALL continue with an explicit not_collected ECG status and null ECG features, without fabricating a normal ECG or marking the entire app unusable.

#### Scenario: Run the simulator

- **GIVEN** synthetic mode and no ECG hardware
- **WHEN** the user selects Run simulator
- **THEN** a deterministic named waveform fixture SHALL exercise capture/progress/review states with simulated source and SHALL not require electrode contact or imply a measured heartbeat.

### Requirement: AND-ECG-002 Whole-system electrical and authorization gates

Human-connected ECG acquisition SHALL require a reviewed whole-system hardware configuration, G-05 approval evidence, a permitted power/charging/cable state, lead/contact configuration, firmware/ADC/front-end versions, a verified device binding, and an authorized protocol/consent/retention decision from the capabilities service. The implementation SHALL also satisfy the AND-ECG-002 detailed contract above.

#### Scenario: Approved configuration and verified device

- **GIVEN** a valid approved whole-system configuration matching the connected device and permitted operating state
- **WHEN** the authorized operator initiates capture
- **THEN** the module SHALL execute only that protocol and retain the binding, approval/configuration hashes, power-state evidence, and lead configuration.

#### Scenario: Unreviewed USB-powered body connection

- **GIVEN** no matching approved power/connection configuration
- **WHEN** the device or user requests hardware ECG capture
- **THEN** the app SHALL reject Start hardware capture, show Electrical configuration not qualified, and SHALL not substitute a simple acknowledgment checkbox for the missing evidence.

#### Scenario: Cached gate after device restart

- **GIVEN** a cached approved-looking capability and a reader with a new boot ID
- **WHEN** the operator attempts a hardware start offline
- **THEN** the app SHALL refuse the start pending fresh online authorization and verified association; it SHALL not reuse the prior boot clock or provide connection instructions from an unresolved configuration.

### Requirement: AND-ECG-003 ECG sample and timing contract

An EcgCaptureAttempt SHALL retain capture/session/device/boot IDs, modality=ecg, source, lead configuration, hardware/firmware/configuration versions, start/end UTC and native monotonic times, sampling clock/source, sample rate or explicit sample timestamps, gap/drop markers, ADC gain/reference/scaling, filter version, contact/lead-off status, and quality flags. The implementation SHALL also satisfy the AND-ECG-003 detailed contract above.

#### Scenario: Raw ADC counts received

- **GIVEN** an otherwise well-formed stream without an approved scale calibration
- **WHEN** the waveform is reviewed
- **THEN** the app SHALL label values counts, retain the missing-scale reason, and SHALL not render an mV axis or supply calibrated features that require voltage units.

#### Scenario: Sample gap inside a recording

- **GIVEN** a stream with a missing block or nonconsecutive sample index
- **WHEN** reassembly completes or times out
- **THEN** the gap SHALL be represented explicitly and the applicable quality rule enforced; the app SHALL not draw a continuous valid trace by interpolating away lost evidence.

### Requirement: AND-ECG-004 Native display and feature restrictions

The native/React Native presentation SHALL display a bounded scrolling waveform and acquisition status without blocking sample ingestion. The implementation SHALL also satisfy the AND-ECG-004 detailed contract above.

#### Scenario: Waveform visually smooth but inadequate for HRV

- **GIVEN** a capture shorter than its extractor's approved duration or with too few usable beat intervals
- **WHEN** the summary is generated
- **THEN** the waveform MAY remain available within policy but RMSSD SHALL be null with an adequacy reason, not a guessed feature.

#### Scenario: Heavy rendering load

- **GIVEN** a supported synthetic or approved stream
- **WHEN** the screen drops rendering frames
- **THEN** raw sample acquisition SHALL remain independently bounded, display lag SHALL be reported where relevant, and lost acquisition samples SHALL not be hidden by the appearance of the graph.

### Requirement: AND-ECG-005 Contact loss, interruption, and retry

The screen SHALL distinguish waiting_for_contact, acquiring, lead_off, saturated, poor_signal, transport_gap, complete, and invalid. The implementation SHALL also satisfy the AND-ECG-005 detailed contract above.

#### Scenario: Lead detaches during capture

- **GIVEN** an active hardware or simulator lead-off test
- **WHEN** contact is lost
- **THEN** the UI SHALL show Lead contact lost, retain lead-off timing, and apply the fixed protocol's stop/invalid behavior without continuing to display an unqualified live heart rate as current.

#### Scenario: Late samples after cancellation

- **GIVEN** a canceled ECG capture
- **WHEN** remaining Bluetooth notifications arrive
- **THEN** those samples SHALL be rejected by capture identity and SHALL not populate a later attempt or turn the canceled attempt complete.

### Requirement: AND-ECG-006 One-modality contract and review semantics

For the existing v0.1 session cardiac envelope, the app SHALL accept either PPG or ECG as the selected cardiac capture. The implementation SHALL also satisfy the AND-ECG-006 detailed contract above.

#### Scenario: User selects ECG after a PPG capture

- **GIVEN** a check with an accepted PPG cardiac component
- **WHEN** the user selects the allowed ECG alternative
- **THEN** the UI SHALL explain that v0.1 selects one cardiac modality, preserve the PPG attempt, and require an explicit selection of which accepted capture becomes the final cardiac component.

#### Scenario: Protocol demands both modalities

- **GIVEN** the installed client supports only the v0.1 cardiac schema
- **WHEN** a protocol requires both PPG and ECG as distinct model inputs
- **THEN** capability resolution SHALL report Unsupported cardiac contract and SHALL not merge the two sources or fabricate a compatible feature vector.

#### Scenario: Optional ECG skip preserves selected PPG

- **GIVEN** a pre-finalization check with a valid selected PPG capture
- **WHEN** the user selects Skip ECG
- **THEN** the PPG selection SHALL remain unchanged, ECG SHALL remain explicitly not_collected, and no mixed-modality v0.1 component SHALL be created.

### Requirement: AND-ECG-007 Privacy, offline behavior, and verification

ECG traces SHALL remain in encrypted application-private storage only when explicitly authorized by a resolved retention policy. The implementation SHALL also satisfy the AND-ECG-007 detailed contract above.

#### Scenario: Offline completed simulation

- **GIVEN** a complete synthetic ECG capture with the network disabled
- **WHEN** the user saves the check
- **THEN** the app SHALL store the permitted fictional record locally, retain its simulated label, and show sync status independently from capture completion.

#### Scenario: Missing raw-data retention policy

- **GIVEN** a proposed participant protocol without a resolved ECG retention policy
- **WHEN** recording or upload is requested
- **THEN** the app SHALL block the dependent recording/upload path and SHALL not choose indefinite retention as a fallback.
