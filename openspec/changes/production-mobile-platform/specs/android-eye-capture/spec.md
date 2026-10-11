# Android eye capture

Scope: passive positioning preview, versioned optical capture integration, feature provenance, and explicit qualification gates. Android SHALL use a native camera path for frame/timing metadata; iOS SHALL provide equivalent behavior through its native camera APIs. This specification extends HW-008–009, APP-009, SEC-003–005, and LLD section 5.2. Pupil size is not by itself an intoxication determination.

Primary platform references: [Android camera characteristics and timestamp source](https://developer.android.com/reference/android/hardware/camera2/CameraCharacteristics#SENSOR_INFO_TIMESTAMP_SOURCE) and [Apple native video data output](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput). Platform timestamps are technical evidence whose physical meaning must be qualified in the capture protocol.

Shared normative baseline: [shared application contracts](../../shared-contracts.md), especially release/workspace policy, frozen context and companion evidence, qualified online starts, immediate cancellation, immutable artifacts, and the Android/iOS software matrix. These rules govern the same behavior on both platforms.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-EYE-001 detailed contract

The Eyes step SHALL show the distinction between Positioning preview and Measurement capture. Its available initial action SHALL be Preview positioning, with ordinary camera preview, a face/eye-position guide, ambient-light instructions that do not prescribe exposure, and Stop preview. It SHALL not enable flash, torch, brightness modulation, strobing, or a pupil-response experiment by entering preview. An unqualified preview SHALL not persist face images, emit pupil measurements, or mark the eye component measured. The screen SHALL show Capture unavailable with its qualification reason when there is no approved configuration; Continue without eye measurement MAY be offered if the current mode permits missing eyes. A synthetic fixture SHALL have a separate explicit demonstration action and source.

### AND-EYE-002 detailed contract

Camera permission SHALL be requested only when the user selects preview or an authorized capture. Microphone, media-library access, and photo-gallery write permission SHALL not be requested for this feature. Denial SHALL show a retry or Open settings action according to OS state; a camera occupied by another app SHALL show Camera unavailable without losing the check. The app SHALL release the camera when leaving the screen, backgrounding, or ending preview. During an authorized capture, permission revocation, screen lock, camera interruption, orientation change, or process termination SHALL invalidate the attempt and preserve its reason. The app SHALL not resume a timing sequence from an interrupted frame.

Any End capture, Back, tab/workspace transition, or overlay hiding an active stimulus SHALL stop the native camera/stimulus and settle invalid evidence in the original namespace before the transition or confirmation. Keep draft SHALL not resume the optical sequence. Passive preview SHALL release resources on the same hiding transition without falsely creating a measured attempt. Withdrawal intent stops dependent capture immediately, including offline.

### AND-EYE-003 detailed contract

Participant optical capture SHALL require an authoritative capability decision from GET /v1/me/capabilities, an approved protocol, applicable consent/retention policy, and an immutable optical configuration matching phone model, OS, camera/lens, capture/exposure settings, stimulus method, positioning/scale method, and feature extractor. The configuration SHALL include its ID/hash, version, limits, approval evidence references, and validity status. The capture adapter SHALL reject an unresolved, expired, revoked, or incompatible configuration. A local JSON file, developer toggle, server environment name, user consent alone, or signed artifact without qualification evidence SHALL not authorize exposure. No universal light intensity, duration, phone brightness, or distance is assigned here; these remain G-04 decisions.

At every qualified Start capture the orchestration layer SHALL obtain a fresh online capture-start acknowledgment tied to the attempt, exact optical configuration, current account/generation, and relevant hardware binding. Cached capability responses SHALL be explanatory only and cannot authorize offline stimulus. A phone wall-clock change or reboot SHALL not extend authority. The installed release SHALL expose the refusal path because it contains no qualified optical configuration; the adapter interface alone does not close G-04.

### AND-EYE-004 detailed contract

An authorized EyeCaptureAttempt SHALL retain capture/session IDs, source, native start/end times, camera/lens/device/OS identity, image dimensions, orientation, actual per-frame timestamp and timestamp-source metadata, requested and observed frame cadence, exposure duration, sensitivity/gain and focus/autoexposure state where available, dropped-frame information, and the capture configuration hash. Android Camera2/CameraX image and capture-result timing SHALL be associated by the supported native API; unknown sensor clock origin SHALL remain unknown. iOS SHALL preserve its native sample-buffer presentation/host-clock relationship explicitly. Stimulus request, frame callback, expected presentation, and measured stimulus onset SHALL remain different fields. The camera bridge SHALL send metadata or approved bounded artifact references, not unbounded frame blobs through the JavaScript event loop.

The full bounded metadata SHALL reside in the eyes component of version 1.0.0 CaptureAttempt and be covered by its immutable hash and selected EvidenceManifest mapping; the strict v0.1 eye component SHALL remain a verified projection. Per-frame arrays and quality evidence SHALL respect the 512 KiB attempt/1 MiB request limits and the protocol’s declared frame-count bound. Reaching a bound SHALL stop/invalidate capture rather than silently drop evidence. Approved larger raw artifacts SHALL use explicit hashed references with verified version identity, never embedded base64 frames.

### AND-EYE-005 detailed contract

Eye features SHALL be generated only by the named compatible extractor after protocol and signal-quality checks. Each feature SHALL preserve its unit and geometry basis: pixels, a defined dimensionless ratio, or millimeters only when a validated scale/geometry and calibration ID support the conversion. Relative constriction amplitude SHALL retain its defined baseline denominator; response and recovery latencies SHALL retain their onset definition and temporal uncertainty. Unsupported iris segmentation, occlusion, motion, changing exposure, insufficient scale evidence, or required timing failures SHALL produce explicit flags and null affected features, not a normal default. No pupil-dilation direction or fixed threshold SHALL be used to infer cannabis intoxication in this feature.

### AND-EYE-006 detailed contract

Preview SHALL remain memory-only. Any raw image/video retention SHALL require the protocol's explicit purpose, capture consent, retention duration, allowed roles, and withdrawal/deletion behavior before recording begins. Files SHALL remain in encrypted application-private storage and SHALL not enter the photo gallery, general device backup, crash reports, or analytics. Upload SHALL use the authorized artifact request/completion APIs, immutable digest, declared byte length/media type, and verified server completion. The app SHALL show whether raw media are stored locally, queued for authorized upload, uploaded, or deleted. Qualified optical starts SHALL remain unavailable offline; passive preview and explicit synthetic fixtures MAY work offline. Existing authorized retained data SHALL remain within its original lifetime and policy, with no indefinite-retention fallback. Save on this device SHALL not enqueue media; only an explicit eligible-account Upload check action with permitted raw scope SHALL do so. Guest media/fixtures SHALL never upload. Withdrawal intent SHALL stop new local recording and quarantine pending dependent work immediately; server-accepted withdrawal SHALL block new tickets, verification, and evidence acceptance. An already issued PUT may place bytes in quarantine until expiry but SHALL not yield accepted evidence. Server completion SHALL pin and verify the exact S3 VersionId; later reads SHALL authorize current ownership/generation/policy through the API gateway and use that version.

### AND-EYE-007 detailed contract

The review card SHALL state Preview only, Simulated example, Captured under named protocol, Invalid, or Not collected, and display actual retained feature units, capture times, calibration/timing status, and quality reasons. Android and iOS SHALL implement equivalent denial, lifecycle, compatibility, artifact, and null-feature behaviors. Verification SHALL use synthetic videos/optical fixtures, camera metadata inspection, denied permissions, process/background interruption, unit-invalid payloads, and missing/expired authorization. Bench capture validation and optical safety evidence SHALL be required separately before participant stimulus capability can be declared available. A successfully built app or a moving eye preview SHALL not be counted as a validated pupil-measurement subsystem.

Before finalization, a failed/interrupted attempt MAY be retried with a new linked attempt and fresh qualified-start acknowledgment; after local/remote finalization, a replacement requires a new check/target and no physical acquisition carryforward. The current release SHALL not render an intoxication probability or research_estimate from any source. The shared software matrix fixes Android minSdk 24 and iOS 16.4; software support SHALL not assert optical configuration compatibility.

## ADDED Requirements

### Requirement: AND-EYE-001 Eye screen and passive preview

The Eyes step SHALL show the distinction between Positioning preview and Measurement capture. The implementation SHALL also satisfy the AND-EYE-001 detailed contract above.

#### Scenario: Preview without an approved optical configuration

- **GIVEN** camera permission and no qualified optical configuration
- **WHEN** the user chooses Preview positioning
- **THEN** a passive camera preview SHALL appear without stimulus, recording, or derived features, and ending it SHALL leave the eye component not_collected.

#### Scenario: Synthetic eye fixture

- **GIVEN** P0 demonstration mode
- **WHEN** the user explicitly chooses the synthetic eye example
- **THEN** the stored component SHALL be labeled simulated, retain its fictional fixture/configuration ID, and SHALL not be represented as an extraction from the user's preview.

### Requirement: AND-EYE-002 Camera permission and lifecycle

Camera permission SHALL be requested only when the user selects preview or an authorized capture. The implementation SHALL also satisfy the AND-EYE-002 detailed contract above.

#### Scenario: Permission permanently denied

- **GIVEN** Android has denied camera permission permanently
- **WHEN** the user selects preview
- **THEN** the screen SHALL explain the missing permission, offer Open settings and Back to check, and SHALL not enter an indefinite loading state.

#### Scenario: Backgrounded active capture

- **GIVEN** an authorized optical capture in progress
- **WHEN** the app loses foreground activity
- **THEN** the stimulus SHALL stop, camera resources SHALL be released, the attempt SHALL become invalid, and returning SHALL require a new linked attempt.

### Requirement: AND-EYE-003 Approved configuration and stimulus authorization

Participant optical capture SHALL require an authoritative capability decision from GET /v1/me/capabilities, an approved protocol, applicable consent/retention policy, and an immutable optical configuration matching phone model, OS, camera/lens, capture/exposure settings, stimulus method, positioning/scale method, and feature extractor. The implementation SHALL also satisfy the AND-EYE-003 detailed contract above.

#### Scenario: Qualified capture configuration available

- **GIVEN** a valid matching optical configuration and all required authorizations
- **WHEN** the user reviews its instructions and selects Start capture
- **THEN** the native module SHALL execute only the bounded approved sequence and store its exact configuration hash and timing evidence.

#### Scenario: Local override requests phone flash

- **GIVEN** no approved configuration or a configuration for a different phone
- **WHEN** a deep link or modified local preference requests stimulus capture
- **THEN** the module and orchestration gate SHALL reject the request and SHALL not activate the flash, torch, or modulated screen.

#### Scenario: Offline cached optical approval

- **GIVEN** a previously available cached optical capability and a current camera permission
- **WHEN** the user enables airplane mode and selects Start capture
- **THEN** the app SHALL require a fresh online capture acknowledgment and SHALL leave all participant stimulus output disabled; passive preview remains a separately labeled action.

### Requirement: AND-EYE-004 Native frame and illumination evidence

An authorized EyeCaptureAttempt SHALL retain capture/session IDs, source, native start/end times, camera/lens/device/OS identity, image dimensions, orientation, actual per-frame timestamp and timestamp-source metadata, requested and observed frame cadence, exposure duration, sensitivity/gain and focus/autoexposure state where available, dropped-frame information, and the capture configuration hash. The implementation SHALL also satisfy the AND-EYE-004 detailed contract above.

#### Scenario: Flash request has no verified physical onset

- **GIVEN** a recorded OS stimulus request and frame callbacks
- **WHEN** the hardware lacks verified physical onset evidence
- **THEN** the record SHALL mark timing evidence unverified or estimated, and an extractor requiring measured onset SHALL produce no qualified response latency.

#### Scenario: Variable camera cadence

- **GIVEN** frame timestamps showing drops or irregular intervals
- **WHEN** feature eligibility is evaluated
- **THEN** the app SHALL retain actual cadence and gap evidence, apply the frozen configuration's quality rules, and SHALL not fabricate a constant high-rate sequence from requested FPS.

### Requirement: AND-EYE-005 Geometry, feature units, and quality

Eye features SHALL be generated only by the named compatible extractor after protocol and signal-quality checks. The implementation SHALL also satisfy the AND-EYE-005 detailed contract above.

#### Scenario: Pixels supplied as millimeters

- **GIVEN** a segmentation result with image-pixel diameter and no scale calibration
- **WHEN** an adapter attempts to populate diameter_mm
- **THEN** validation SHALL reject the unit conversion and retain only a correctly labeled pixel or dimensionless observation when permitted.

#### Scenario: Eye lost during response window

- **GIVEN** a capture with required frames obscured by blink or tracking loss
- **WHEN** the extractor applies the approved quality policy
- **THEN** the affected feature SHALL be null or the capture invalid according to that policy, with the reason retained; it SHALL not impute an apparently normal response.

### Requirement: AND-EYE-006 Raw artifact consent, minimization, and deletion

Preview SHALL remain memory-only. The implementation SHALL also satisfy the AND-EYE-006 detailed contract above.

#### Scenario: User declines raw recording

- **GIVEN** a protocol that permits local feature extraction without raw retention
- **WHEN** the user declines optional recording
- **THEN** raw data SHALL not be persisted or uploaded, and only explicitly permitted features and quality metadata MAY be retained.

#### Scenario: Artifact upload fails

- **GIVEN** an authorized retained capture and a network interruption
- **WHEN** upload cannot complete
- **THEN** the UI SHALL show pending upload, retain the immutable local artifact only within its permitted lifetime, and SHALL not mark a partial remote object available for extraction.

#### Scenario: Withdrawal races with an issued upload ticket

- **GIVEN** an optical artifact PUT URL issued before withdrawal
- **WHEN** the user withdraws locally and the server accepts withdrawal while old bytes arrive
- **THEN** local capture/queue work SHALL stop immediately, the server SHALL refuse artifact verification/evidence acceptance, and any uploaded version SHALL remain quarantined for scoped cleanup.

### Requirement: AND-EYE-007 Review, parity, and evidence boundaries

The review card SHALL state Preview only, Simulated example, Captured under named protocol, Invalid, or Not collected, and display actual retained feature units, capture times, calibration/timing status, and quality reasons. The implementation SHALL also satisfy the AND-EYE-007 detailed contract above.

#### Scenario: Review after passive preview

- **GIVEN** a user who previewed positioning but performed no authorized measurement
- **WHEN** Review is opened
- **THEN** Eyes SHALL show Not collected with Preview only context and null measured features rather than a successful pupil test.

#### Scenario: Cross-platform camera capability mismatch

- **GIVEN** an optical configuration qualified for a specific iPhone but not the Android device in use
- **WHEN** Android requests measurement capture
- **THEN** Android SHALL remain blocked with Unsupported optical configuration while iOS compatibility is assessed independently; visual similarity SHALL not establish equivalence.
