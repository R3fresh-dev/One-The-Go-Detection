Scope: this executable adapter implements conditional collection for Android Camera2 and iOS AVFoundation and extends HW-008–009, APP-009, SEC-003–005, AND-EYE-002–006 and LLD section 5.2. The original G-04 physical qualification gate remains independent. Every scenario below defines Android/iOS parity unless it names a platform-specific exposure or rotation method.

## ADDED Requirements

### Requirement: AND-EYE-101 Governed executable optical start
The system SHALL require a current owned started acquisition authorization, exact canonical material hash, approved camera/lens/format/phone/OS/native-build tuple and explicit participant camera permission before native capture. Inventory and positioning SHALL NOT start recording. No checked-in numerical material SHALL become approved by installation.

#### Scenario: OPTICAL-001 Fresh feature-only start
- **GIVEN** an owned started attempt, current study consent and independently released configuration with the installed camera tuple
- **WHEN** the participant grants camera permission and explicitly starts feature-only collection
- **THEN** context and attempt evidence are persisted before the online authorization is issued and started
- **AND** the native view receives the exact material bytes, authorization and attempt record identity, with null recording permission
- **AND** local completion does not queue an upload

#### Scenario: OPTICAL-002 Missing or revoked start authority
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** camera permission, online start, exact hash or approved device tuple is missing or changed, or consent or configuration is retired before start
- **THEN** acquisition remains stopped and no raw frame is persisted
- **AND** an old positive authorization response cannot invoke hardware after its workspace is invalidated

### Requirement: AND-EYE-102 Bounded native frame evidence
The native adapter SHALL enforce reviewed duration, frame count, ROI dimensions, monotonic clock, frame gap and dispatch bounds. It SHALL preserve actual exposure evidence method, focus state, source format dimensions, applied rotation and processed output coordinate dimensions. Unknown sensor orientation SHALL remain null; a required unknown orientation SHALL prevent capture. No observed frame SHALL mean no acquired camera evidence.

#### Scenario: OPTICAL-003 Accepted bounded frames retain platform evidence
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** the approved capture receives an ordered bounded sequence with accepted frame spacing, dimensions and metadata
- **THEN** frame sequences begin at zero and actual native timestamps and dispatch times are retained
- **AND** Android exposure evidence says capture_result_timestamp_match only for matched sensor timestamps
- **AND** Android joins images and results in either arrival order only by exact sensor timestamp, with three pending images and sixteen retained results
- **AND** sensitivity ISO remains null when unavailable, and platform-specific AE state and its observation method remain explicit
- **AND** iOS callback exposure evidence says device_state_at_callback and has the exposure-not-frame-matched quality flag

#### Scenario: OPTICAL-004 Gap, overflow or changed geometry stops collection
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** timestamps regress, a frame or silence gap exceeds the reviewed bound, the three-frame callback queue overflows, dispatch is late or source/processed dimensions change
- **THEN** the originating capture stops invalid and emits no positive features or raw handoff
- **AND** changing counts, dimensions or frame timestamps in a retained positive payload is rejected by the independent API validator
- **AND** an unmatched Android result expires within the reviewed frame-gap bound, and searching, adjusting or unknown AE cannot produce accepted segmentation

#### Scenario: OPTICAL-005 Camera fails before first accepted frame
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** permission, camera start or native setup fails before any accepted camera frame
- **THEN** the terminal is invalid with its originating identity and reason, and native evidence and raw media are null
- **AND** no acquisition timestamp, camera clock or optical feature is invented; the separate arming timestamp remains available for repair

### Requirement: AND-EYE-103 Deterministic bounded ROI extraction
The versioned extractor SHALL use reviewed sampling and four-connected dark components. It SHALL reject ambiguous, edge, low contrast/roundness and unapproved-area components. The API SHALL recompute exposed scalar arithmetic and reject changed counts, geometry, features or projection.

#### Scenario: OPTICAL-006 Literal cross-language pixels and factory payload
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** Kotlin, Swift and the API process the checked-in synthetic pixel and response goldens
- **THEN** the expected component statistics, feature arithmetic and codec bytes agree within the stated numerical tolerance
- **AND** the production Kotlin payload factory matches the checked-in DTO accepted by the independent API validator
- **AND** fixture success grants no anatomical or physical qualification

#### Scenario: OPTICAL-007 Ambiguous pixels and forged retained statistics
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** a component touches the rejected edge, has unapproved area, roundness or contrast, or multiple plausible components exist
- **THEN** extraction returns an explicit invalid reason without guessing a pupil
- **WHEN** a retained payload changes a count, normalized diameter, geometry, material hash or declared scalar result
- **THEN** API and client projection validation reject the changed evidence

### Requirement: AND-EYE-104 Reviewed stimulus and scale boundaries
Passive collection SHALL leave illumination unchanged and response features null. A display-step mode SHALL require explicit reviewed gray, brightness, timing and response settings, restore brightness after every exit, and preserve requested, native-callback and physical onset separately. Millimeters SHALL require the exact released optical geometry calibration and accepted pixel range. Physical onset SHALL NOT be inferred from a display callback.

#### Scenario: OPTICAL-008 Reviewed geometry and descriptive display response
- **GIVEN** exact independently released geometry and configuration authority for the installed tuple and sampled pixel basis
- **WHEN** accepted component diameters lie inside the calibrated range
- **THEN** baseline millimeters use the frozen pixel-to-mm conversion and its stated uncertainty
- **WHEN** a separately reviewed display step has enough accepted baseline and post-step frames
- **THEN** callback-relative change and threshold timing may be retained as descriptive metadata, with physical onset explicitly unmeasured
- **AND** original screen brightness is restored after settlement or interruption

#### Scenario: OPTICAL-009 Unmeasured onset cannot become a pupil response
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** a retained payload claims measured physical onset, scientific latency or pupil relative constriction from native callbacks alone
- **THEN** the payload is rejected and response-dependent model admission fails closed
- **AND** normalized or out-of-range geometry leaves scientific millimeters null
- **AND** missing, stale or mismatched calibration cannot qualify even a diameter-only model

### Requirement: AND-EYE-105 Originating lifecycle and privacy settlement
Every callback SHALL carry its originating run/generation. Cancellation SHALL invalidate authority synchronously before asynchronous platform shutdown. A deferred positive settlement SHALL yield to queued interruption. Late camera opens and results SHALL close or update only their originating lease. A committed scientific terminal SHALL remain immutable within its originating workspace.

#### Scenario: OPTICAL-010 Cancel after committed completion
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** completion committed before a participant End action but durable local evidence persistence is delayed
- **THEN** the native cancellation receipt returns that same immutable scientific completion
- **AND** the UI disables native running and requests shutdown before awaiting persistence

#### Scenario: OPTICAL-011 Late origin after workspace replacement
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** an old camera opens, session configures, capture result arrives or frame callback executes after its workspace was canceled
- **THEN** the originating handle closes or the old callback is discarded without mutating the replacement ledger or handles
- **AND** a queued cancellation wins over a positive settlement that has not committed

### Requirement: AND-EYE-106 Explicit ephemeral ROI recording
Raw recording SHALL default off and require fresh separate recording permission. Native media SHALL remain bounded in RAM, use the versioned ROI codec and never fall back to a plaintext file. The app SHALL commit it only to encrypted local storage; saving SHALL NOT queue an upload. Durable acknowledgment, abort, timeout or privacy transitions SHALL release native media references.

#### Scenario: OPTICAL-012 Opted-in encrypted handoff
- **GIVEN** fresh separate record permission bound to the current consent, policy and raw notice
- **WHEN** a valid native acquisition returns the bounded ROI codec and chunks
- **THEN** encrypted bytes and the exact immutable local receipt commit atomically before native release acknowledgment
- **AND** ROI dimensions, count, sequence, Float64 timestamps and each decoded luminance digest match the originating accepted frame ledger
- **AND** temporary decoded bytes are wiped and neither local Save nor native handoff queues an upload
- **WHEN** an explicitly requested upload completes
- **THEN** the server independently decodes the exact admitted object version, repeats extraction on its pixels and rejects changed statistics or linkage
- **AND** an owned verification receipt binds the object version and digest to the accepted attempt, complete configuration and native evidence digest

#### Scenario: OPTICAL-013 Withdrawal, timeout or absent opt-in
- **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions
- **WHEN** recording permission is absent or false
- **THEN** feature collection emits no raw handoff
- **WHEN** a completed raw recording is acknowledged, aborted, unacknowledged for thirty seconds or followed by a privacy/workspace/background/detach transition
- **THEN** native cached raw media references are released
- **AND** withdrawal's durable local fence blocks upload and later cancellation cannot recover the old raw chunks
- **AND** changed pixels, timestamps, sequence, dimensions or accepted acquisition identity cannot be reclassified as authenticated raw recording
