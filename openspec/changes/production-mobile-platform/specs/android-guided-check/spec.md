# Android guided check

Scope: one identified saliva collection and one continuous reaction task per completed check, with separate optical and cardiac acquisition steps. This specification extends APP-001, APP-008, APP-012–014 and OPS-002–005. It requires the same domain workflow on iOS with platform-specific permission and interruption handling. Completion of the application does not close the assay, optical, electrical, study, or model gates in the full specification.

Engineering boundary: public GET /v1/app-config identifies release environment, minimum supported versions, and maintenance state; authenticated GET /v1/me/capabilities resolves channel modes, blocking reasons, protocol/configuration IDs and hashes, expiry, and authority. The app SHALL use the existing session registration, snapshot, finalization, and result APIs for remote checks. A production JWT and server-side authorization SHALL remain required; a local-development identity SHALL never authenticate against production.

Shared normative baseline: [shared application contracts](../../shared-contracts.md), especially release/workspace policy, frozen context and companion evidence, qualified online starts, immediate cancellation, immutable artifacts, and the Android/iOS software matrix. These rules govern the same behavior on both platforms.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-CHECK-001 detailed contract

The app SHALL expose Start check on Home and atomically create a client-side UUID only after the user selects it. It SHALL show the check mode, current environment when non-production, and a checklist containing Profile, Device, Saliva, Eyes, Heart rate, optional ECG, Reaction task, and Review. Profile within this check SHALL show the frozen context read-only; Edit profile for a future check SHALL explain that changing this check's context requires Start replacement check. The screen SHALL identify each step as not_started, ready, acquiring, complete, skipped, blocked, invalid, or canceled; these workflow states SHALL remain distinct from result states. Required/optional designations SHALL come from the applicable versioned protocol or fixed P0 demonstration configuration. The primary action SHALL be Continue, with the next available step named. A demo containing actual native reaction practice SHALL label each channel's source and the check Mixed demo and uncalibrated practice; it SHALL not label actual taps fictional. No screen SHALL present capture percentage as probability of intoxication.

### AND-CHECK-002 detailed contract

At Start check the app SHALL atomically freeze the confirmed profile version and exact profile/history objects, selected mode, protocol/configuration references, eligible earlier baseline references if any, and current device association in the version 1.0.0 CaptureContext. created_at, target_at, and context_confirmed_at SHALL equal the UTC timestamp of that action. The Profile step SHALL review that snapshot, including unknown/declined values; later edits to an account profile SHALL not rebind it. New capture associations/configurations SHALL be recorded in each attempt without rewriting frozen context. A materially different profile/context requires a newly identified check, with explicit fresh confirmation of carried profile fields and no carried physical acquisitions. OS permission, local storage policy, and research enrollment/upload authorization SHALL remain separate decisions. Capability evidence SHALL retain authority, mode, configuration ID/version/hash, expiry, and blocking reasons; a client preference, age, cached model, paired reader, or cached capability SHALL not grant research authority. Every qualified human start SHALL obtain a fresh online capture-start acknowledgment through the shared authorization contract; cached capabilities are display-only. Withdrawal intent SHALL immediately stop local dependent capture and quarantine queued study work before any server acknowledgment.

### AND-CHECK-003 detailed contract

Every collection, component acquisition, and task run SHALL have an immutable attempt UUID and parent session ID, persisted before activation. A valid consumer-format check SHALL have one accepted sample collection and one accepted continuous game; multiple analytes MAY reference the same sample. Before local or remote finalization, retry SHALL require a recorded invalid/canceled predecessor, create a new attempt under the same parent, and retain supersedes_attempt_id and all prior evidence. A valid accepted task SHALL not offer Retake for best score. After local or remote finalization, recovery SHALL offer Start replacement check with a new session UUID, newly confirmed context, new created_at/target_at, and supersedes_session_id linking the original. No physical saliva, optical, cardiac, or task acquisition SHALL be carried into that replacement as newly acquired evidence. Original records SHALL remain immutable. Allocated identifiers alone SHALL not imply that a measurement occurred; an administrative report correction SHALL remain a distinct authorized lineage, not a replacement physical check.

### AND-CHECK-004 detailed contract

The app SHALL record RFC 3339 UTC creation, target, component start/end, sample collection, and capture_completed_at times, alongside native monotonic evidence and clock uncertainty where relevant. target_at SHALL equal created_at at Start check and SHALL not move to delayed analysis time. Review SHALL display each channel, source, quality, collection time, missing reason, and completion status. Not-collected components SHALL have null acquisition timestamps/features and zero actual task counts; an uncollected sample SHALL have null collected_at and no analyte measurement records. acquisition_span_ms SHALL cover actual acquisitions only and be null if none occurred. Pending assay analysis SHALL remain distinguishable from completed capture. The strict v0.1 snapshot SHALL contain only its selected scientific projection; full context, prior attempts, raw native task evidence, configuration references, and authorized artifact/attestation references SHALL remain in the bounded version 1.0.0 companion contracts. The manifest SHALL retain every failed/superseded attempt hash and selected attempt mapping. Local save, upload, finalization, history, and export SHALL verify both snapshot and companion digests and cross-check selected identities, times, statuses, quantities, and sources.

### AND-CHECK-005 detailed contract

The app SHALL provide End task within the native task view and Cancel check outside trial response controls. Selecting End task, Cancel check, platform Back, another tab/route/workspace, or any app overlay that hides an active stimulus SHALL immediately stop native acquisition and settle exactly one invalid/interrupted task in the original namespace before showing a confirmation or navigating. Native shutdown SHALL not wait for BLE/network delivery or a JavaScript timer. A later confirmation MAY ask whether to discard the wider draft; Keep draft SHALL preserve the ended invalid attempt and SHALL never resume it. Background/focus loss, phone-call interruption, screen lock, geometry change, or prohibited sensor interruption SHALL use the same immediate stop behavior. An inactive draft MAY be preserved on navigation. Process restart SHALL restore its durable ledger and settle a previously started unfinished acquisition as invalid/interrupted, never complete it from a spinner. Local withdrawal intent SHALL stop dependent acquisition immediately even when offline, and late events SHALL fail run/attempt/workspace-epoch matching.

### AND-CHECK-006 detailed contract

Permitted synthetic acquisition and native uncalibrated practice SHALL operate offline and persist drafts/evidence in the applicable encrypted native store. This release SHALL not start qualified human acquisition offline: cached capabilities SHALL explain the last known state only, and each qualified start SHALL require a fresh online authorization acknowledgment. Sensor timing SHALL not depend on a cloud round trip per sample. Save on this device SHALL validate and freeze the local v0.1 snapshot, companion manifest, canonical bytes, and both digests without creating an upload queue entry. Guest demo SHALL never upload or migrate records on sign-in. An eligible signed-in account MAY separately select Upload check after destination/scope review; that action alone creates the upload intent. Retries SHALL retain session UUID, generation, snapshot/manifest hashes, and operation idempotency keys; Retry queued uploads automatically SHALL default off. Transport labels SHALL distinguish Saved on this device, Waiting to upload, Uploading, Awaiting analysis, and Synced without implying measurement validity. Unknown acknowledgments SHALL reconcile only an explicitly requested intent. Withdrawal/deletion policy SHALL block new protected work and quarantine retired-generation or unauthorized queues; stale artifact PUTs SHALL remain unverified quarantine bytes. No outage SHALL fabricate a server result.

### AND-CHECK-007 detailed contract

After Review the primary action SHALL always be Save on this device, with local scope stated; eligible account result/history detail SHALL separately offer Upload check and explicit destination/data-scope review. This release fixes inference_available=false on client and service. Accepted states SHALL render measurement_only, inconclusive, and invalid with null probability. research_estimate remains future schema vocabulary but SHALL be rejected as UNSUPPORTED_RESEARCH_RESULT from current live responses, history, imports, or caches even if signed or accompanied by a model manifest. No configuration or remote flag SHALL enable it. Missing channels/delayed analysis SHALL not become normal findings. The result SHALL avoid intoxicated/sober certainty, driving clearance, guessed metabolic clearance, and physiological-normality claims. Detailed measurements, per-channel provenance, reasons, actual assessment time, and evidence availability SHALL be accessible from the result card.

### AND-CHECK-008 detailed contract

Android and iOS SHALL implement identical check identities, frozen context, missingness, attempt/replacement lineage, result semantics, and explicit upload idempotency. Guest demo with actual native taps SHALL retain mixed per-channel provenance, remain local-only, and use the mobile adapter rather than the all-fictional CLI validator. Instructions/status SHALL use text and icons and support platform screen readers, accessible button names, readable text scaling, and sufficient touch targets outside native scored acquisition. Timing-task accommodations SHALL retain a distinct compatibility decision. Verification SHALL include complete fictional and mixed local journeys, blocked physical gates, denied permissions, canceled attempts, offline restart, profile-change immutability, late events across namespace changes, explicit upload retry, dual-digest finalization conflict, and replacement-check lineage on both platforms. The Android/iOS minimum/current simulator, physical-handset, and accessibility matrix SHALL follow shared contracts §9; unavailable rows SHALL remain unexecuted. Physical timing and sensor qualification SHALL remain separate from UI/simulator tests.

## ADDED Requirements

### Requirement: AND-CHECK-001 Start and capability-aware checklist

The app SHALL expose Start check on Home and create a new client-side UUID only after the user selects it. The implementation SHALL also satisfy the AND-CHECK-001 detailed contract above.

#### Scenario: Start a synthetic check

- **GIVEN** local demonstration mode and no physical assay
- **WHEN** the user selects Start check
- **THEN** the app SHALL allocate a new session UUID, display Simulated data for fictional channels and Uncalibrated practice for actual native taps, and present concrete synthetic steps without requiring a cloud account or claiming a physical measurement.

#### Scenario: Required capability is blocked

- **GIVEN** an unavailable approved optical or assay configuration
- **WHEN** the checklist evaluates that capability
- **THEN** it SHALL show the specific blocker and an allowed preview, sample-record, or skip action where the mode permits it; it SHALL not show a completed measurement or fabricate a substitute.

### Requirement: AND-CHECK-002 Immutable context and independent consent

At Start check the app SHALL atomically freeze the confirmed profile/context and set created_at, target_at, and context_confirmed_at to that action’s UTC timestamp. The implementation SHALL also satisfy the AND-CHECK-002 detailed contract above.

#### Scenario: Profile changes during a check

- **GIVEN** a newly created check with a frozen profile version, before any acquisition
- **WHEN** the user edits their profile elsewhere
- **THEN** the active check SHALL retain its original snapshot, and a later check SHALL use the new version; the older record SHALL not change silently.

#### Scenario: Local capture permission without upload consent

- **GIVEN** a granted camera or Bluetooth permission but no research upload authorization
- **WHEN** the user completes an allowed local action
- **THEN** the app SHALL keep it within the permitted local scope and SHALL not enqueue participant data for a study merely because OS permission was granted.

#### Scenario: Offline clock rollback cannot grant capture

- **GIVEN** cached formerly available capabilities and no network
- **WHEN** the wall clock is set backward or the phone reboots
- **THEN** qualified Start capture SHALL remain blocked pending a fresh online acknowledgment; permitted local uncalibrated practice SHALL remain available.

### Requirement: AND-CHECK-003 Attempt identity and sequence rules

Every actual collection, component acquisition, and task run SHALL have an immutable attempt UUID and parent session ID. The implementation SHALL also satisfy the AND-CHECK-003 detailed contract above.

#### Scenario: Invalid saliva collection retried

- **GIVEN** a sample marked invalid for inadequate volume
- **WHEN** the user selects Replace sample and follows the allowed protocol
- **THEN** a new sample attempt SHALL be created, the first SHALL remain in the audit history, and only the accepted sample SHALL supply that check's analyte records.

#### Scenario: User requests repeated valid game

- **GIVEN** one completed valid task in the current check
- **WHEN** the user reopens the reaction step
- **THEN** the app SHALL show the saved completion and review action, not a rerun action that can replace the accepted task with a faster result.

#### Scenario: Finalized invalid check requires a fresh assessment

- **GIVEN** an invalid check already saved locally with a completed saliva or cardiac observation
- **WHEN** the user selects Start replacement check
- **THEN** the app SHALL create new session/target identities and explicit supersedes_session_id, keep the original immutable, and SHALL not carry any physical acquisition into the replacement.

### Requirement: AND-CHECK-004 Capture timing, partial data, and review

The app SHALL record RFC 3339 UTC creation, target, component start/end, sample collection, and capture_completed_at times, alongside native monotonic timing and clock uncertainty where relevant. target_at SHALL identify the original assessment time and SHALL not move to the time a delayed assay result arrives. The implementation SHALL also satisfy the AND-CHECK-004 detailed contract above.

#### Scenario: Device step skipped in a permitted measurement-only workflow

- **GIVEN** no actual cardiac capture and a mode that permits a missing cardiac component
- **WHEN** the user advances to Review
- **THEN** cardiac data SHALL be marked not_collected with null timing/features and the stated reason; the app SHALL not copy an earlier pulse value or substitute zero.

#### Scenario: Laboratory analysis returns the next day

- **GIVEN** saliva collected yesterday with separately timed physiological/task measurements
- **WHEN** a permitted laboratory result is linked today
- **THEN** Review and history SHALL retain yesterday's collection and target times, identify the later analysis time, and SHALL not call the result a current real-time assessment.

### Requirement: AND-CHECK-005 Cancellation, navigation, and interruptions

The app SHALL stop active native acquisition and settle an invalid/interrupted attempt before any cancellation confirmation, route change, or stimulus-hiding overlay. The implementation SHALL also satisfy the AND-CHECK-005 detailed contract above.

#### Scenario: App terminated during reaction task

- **GIVEN** a persisted started task attempt without a completion event
- **WHEN** the app restarts
- **THEN** it SHALL mark that attempt interrupted, preserve already completed independent components, and require a new linked task attempt before representing task completion.

#### Scenario: Cancel command cannot reach the peripheral

- **GIVEN** an active capture and a lost BLE connection
- **WHEN** the user selects Cancel check
- **THEN** the UI SHALL terminate locally, record cancellation, and reject subsequent late events for the canceled attempt regardless of whether the peripheral received the command.

#### Scenario: Keep draft cannot resume an ended task

- **GIVEN** an active scored task whose parent navigator keeps tabs mounted
- **WHEN** the user selects another tab and then Keep draft in the resulting sheet
- **THEN** the native stimulus SHALL have already stopped and the attempt SHALL remain invalid; returning SHALL expose a permitted new attempt or replacement action rather than resuming.

### Requirement: AND-CHECK-006 Offline persistence and finalization

The app SHALL save permitted checks locally before offering an explicit eligible-account upload and SHALL never start qualified human capture offline. The implementation SHALL also satisfy the AND-CHECK-006 detailed contract above.

#### Scenario: Network drops after finalization submission

- **GIVEN** a frozen local snapshot and an unknown server acknowledgment outcome
- **WHEN** the user requests reconciliation, or previously enabled automatic retry permits it, after connectivity returns
- **THEN** the app SHALL retry or query with the same identifiers and digest, reconcile one logical finalization, and SHALL not create another sample, task, or check.

#### Scenario: Draft version conflicts with server

- **GIVEN** a stale local snapshot version
- **WHEN** the server returns a version conflict
- **THEN** the app SHALL preserve both the local pending content and authoritative version metadata, show Conflict needs review, and SHALL not overwrite a finalized remote record.

#### Scenario: Save and sign in cannot upload guest evidence

- **GIVEN** a guest demo containing fictional chemistry and actual uncalibrated native taps
- **WHEN** the user saves the check, reconnects, and signs in
- **THEN** the check SHALL remain in its guest namespace with exact mixed provenance and no queue entry or account migration.

### Requirement: AND-CHECK-007 Result navigation and claim boundaries

Review SHALL always offer Save on this device first, and this release SHALL reject research_estimate with inference_available=false. The implementation SHALL also satisfy the AND-CHECK-007 detailed contract above.

#### Scenario: Synthetic check completes successfully

- **GIVEN** a valid synthetic snapshot
- **WHEN** the measurement-only result arrives or is generated by the permitted local demonstration
- **THEN** the app SHALL show completion of the demonstration and its measurement details, with no intoxication percentage or physiological normality claim.

#### Scenario: Forged result includes a probability

- **GIVEN** a synthetic or unauthorized check
- **WHEN** a malformed cache or response contains an intoxication probability
- **THEN** the client SHALL reject that field/result, surface a data-integrity error, and SHALL not display it as a research estimate.

#### Scenario: Signed future result is unsupported in this release

- **GIVEN** an otherwise owner-matching signed response with research_estimate and a probability
- **WHEN** the result is opened from live navigation or history
- **THEN** the client SHALL reject it as UNSUPPORTED_RESEARCH_RESULT and SHALL not render the probability or relabel the result successful.

### Requirement: AND-CHECK-008 Accessible parity and end-to-end evidence

Android and iOS SHALL implement identical check identities, missingness, attempt lineage, result semantics, and upload idempotency. The implementation SHALL also satisfy the AND-CHECK-008 detailed contract above.

#### Scenario: Screen-reader navigation outside capture

- **GIVEN** an enabled Android or iOS screen reader
- **WHEN** the user traverses the checklist and Review
- **THEN** step names, states, reasons, and actions SHALL be announced in a meaningful order without depending on badge color.

#### Scenario: Cross-platform offline replay

- **GIVEN** equivalent fictional engineering-account records saved offline on each platform
- **WHEN** each signed-in user explicitly selects Upload check to the same permitted API environment
- **THEN** both SHALL preserve quantities, qualifiers, provenance, context/evidence hashes, and terminal states with platform metadata retained; guest demo records SHALL remain local and ineligible for this upload.
