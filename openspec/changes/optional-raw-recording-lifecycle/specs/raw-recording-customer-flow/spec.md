## ADDED Requirements

### Requirement: AND-RAW-001 Present exact optional-purpose terms before recording
The Android and iOS application SHALL present complete approved purpose, policy identity/version/digest, exact raw notice and digest, retention basis and duration, expiry, permitted access roles, withdrawal/deletion behavior and exceptions before optional recording. It MUST independently verify policy.content using JCS SHA-256 and notice content using UTF-8 SHA-256, and MUST reject contradictory summaries or unsupported data.

#### Scenario: Approved terms are independently verified
- **GIVEN** the owned study returns current consent and an approved policy
- **WHEN** the participant opens Recording choices & retention
- **THEN** exact verified terms appear before any choice can be confirmed.

#### Scenario: A projected purpose is substituted
- **GIVEN** the server reply contains policy.content for purpose A and displayed purpose B
- **WHEN** the client verifies the reply
- **THEN** the policy is rejected and acquisition remains unavailable.

### Requirement: AND-RAW-002 Separate recording and upload from study acceptance
Each participant raw purpose SHALL default to record=false and upload=false without an exact current optional-purpose receipt. Eye video and ECG waveform SHALL have distinct device-recording and upload choices, with upload requiring recording. Declining raw SHALL preserve permitted feature-only measurement. The app MUST NOT expose privileged laboratory-report upload or inherit unfinished acknowledgment across account, generation, consent, policy or notice changes.

#### Scenario: Participant chooses local recording only
- **GIVEN** verified terms and both choices off
- **WHEN** the participant enables device recording and confirms the separate notice
- **THEN** upload remains off and no raw file is queued.

#### Scenario: The workspace changes before confirmation
- **GIVEN** unchecked choices were edited in account A generation 1
- **WHEN** account B or a new generation opens the form
- **THEN** unfinished choices and notice acknowledgment reset.

### Requirement: AND-RAW-003 Preserve exact intent and acknowledgment receipt
An optional-purpose change SHALL durably retain its complete body, actual explicit acknowledgment time, data generation and idempotency key before transmission. Retry SHALL preserve this identity and MUST validate the exact accepted consent, policy, notice, choices and acknowledgment time before claiming confirmed permission. Effective choices MAY narrow a historical immutable receipt after revocation but MUST NOT widen it.

#### Scenario: Accepted response is lost
- **GIVEN** the service accepted a preference but its reply was lost
- **WHEN** the customer retries
- **THEN** the original body, timestamp and request key are reused and the original receipt is reconciled.

#### Scenario: Effective permission exceeds the receipt
- **GIVEN** a receipt confirms upload=false
- **WHEN** a status reply says upload=true without a new matching receipt
- **THEN** the client rejects the status.

### Requirement: AND-RAW-004 Stop locally and retain privacy barriers
Revocation or study withdrawal SHALL stop native acquisition before network or storage waits can delay hardware shutdown, fence affected purposes locally and quarantine dependent raw intents. Privacy requests SHALL retain their original scope/key while offline and across clearing local checks. Late replies MUST NOT restore permission; an older completed cleanup receipt MUST NOT clear a newer pending fence.

#### Scenario: A grant reply arrives after revocation
- **GIVEN** an optional-purpose grant request is in flight
- **WHEN** the participant requests revocation before its reply
- **THEN** the grant intent remains blocked and the late reply cannot revive it.

#### Scenario: Old cleanup and new pending cleanup coexist
- **GIVEN** completed revocation A and newer cleanup-pending revocation B for eye video
- **WHEN** status is refreshed after B was accepted
- **THEN** eye recording remains fenced until B is completed.

### Requirement: AND-RAW-005 Distinguish upload and physical retention cleanup
The app SHALL display actual owned artifact upload_state, independent retention state, original acquisition-based retention deadline and physical cleanup completion separately. It MUST distinguish locally stored, queued, quarantined, verified, cleanup-pending and purged evidence without inventing missing state. Artifact history SHALL be bounded and offer explicit pagination; privacy completion MUST consider all targeted artifacts.

#### Scenario: An uploaded object is awaiting verification
- **GIVEN** retention state retained and upload_state quarantine
- **WHEN** status is displayed
- **THEN** quarantine is visible and the app does not claim verified upload or completed deletion.

#### Scenario: Physical cleanup has not completed
- **GIVEN** a revoked artifact has cleanup_pending with no cleanup_completed_at
- **WHEN** its receipt is displayed
- **THEN** pending cleanup remains explicit and is never labeled deleted.

### Requirement: AND-RAW-006 Bind recording to fresh acquisition and encrypted local commit
Optional native recording SHALL require an unchanged current optional-purpose receipt in both the fresh issued authorization and server-signed capture start. The app MUST bind the codec bytes, acquisition attempt, actual native or device timing and original consent/policy before atomically committing a raw BLOB and its metadata index to encrypted local storage. A successful commit or failed handoff MUST release native recording memory. Save on this device MUST NOT enqueue raw upload.

#### Scenario: Participant saves approved local recording
- **GIVEN** an approved codec and separately confirmed record=true, upload=false
- **WHEN** native acquisition completes and its immutable evidence matches the fresh start
- **THEN** bytes and metadata commit together to SQLCipher, native handoff memory is released, and the upload queue remains empty.

#### Scenario: Consent was revoked on another device
- **GIVEN** a cached optional receipt appears to permit recording
- **WHEN** fresh capture start refuses or narrows the receipt
- **THEN** native raw recording never starts and cached permission cannot override the fresh decision.

### Requirement: AND-RAW-007 Enforce local retention and bounded ticket recovery
Local recordings SHALL be reconciled before workspace access and during foreground maintenance. Expired reads MUST be denied; cleanup remains pending until storage confirms removal. Explicit upload SHALL precede immutable finalization, preserve unknown request identities, renew only acknowledged expired tickets, and wipe decrypted buffers on every path.

#### Scenario: A stopped app resumes after retention expiry
- **GIVEN** local raw bytes expired while the app was stopped
- **WHEN** the owner unlocks the workspace
- **THEN** expired and unindexed bytes are removed before exposure, failed removal remains pending, no expired read or upload is admitted, and the stopped app makes no exact-time physical cleanup claim.

#### Scenario: Renewal response is lost
- **GIVEN** a ticket renewal has an unknown response
- **WHEN** explicit upload is retried
- **THEN** its exact key and body are reused; after an acknowledged ticket later expires, a new bounded renewal epoch is persisted before requesting a replacement, and decrypted buffers are wiped on success, failure or cancellation.

### Requirement: AND-RAW-008 Require a distinct raw export purpose and exact binary scope
Exports SHALL exclude raw by default. Raw inclusion requires distinct current export authority, exact notice, unchecked acknowledgment and explicit eligible sources. Requests MUST retain their identity through lost receipts. Archives SHALL match the owned job's frozen authority and source descriptors, reject extra paths, and stay within 50 MiB uncompressed and 64 MiB archive; grants may only lower these limits.

#### Scenario: Participant explicitly includes an authorized recording
- **GIVEN** a distinct current export purpose and eligible retained source for the selected check
- **WHEN** the participant reads the exact notice, selects the source and confirms the separate export
- **THEN** recording or upload consent alone grants no export scope, the service job retains the exact authority, source selection, notice and acknowledgment timestamp, a lost receipt reuses the same key and body, and the archive verifies against that receipt before sharing.

#### Scenario: A raw member is substituted
- **GIVEN** a downloaded ZIP has internally rehashed files but a changed raw source version or an unselected binary member
- **WHEN** the app compares the archive with the authenticated job receipt
- **THEN** exact source ID, version, kind, SHA-256, size and retained lifetime are compared with the owned frozen job; substituted, unknown or orphan paths refuse sharing, and no broadened permission is inferred from recording consent.
