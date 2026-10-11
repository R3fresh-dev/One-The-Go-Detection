# Android feature: offline save and synchronization

Normative integration: [shared application contracts](../../shared-contracts.md) and [platform contracts](../../platform-contract.md). These define the exact cross-feature DTOs, error states, generation/revocation rules, current-release limits, and implementation evidence.

## Purpose and traceability

Let a customer complete a permitted check without network dependence, know where it is stored, and upload only by an explicit authorized action. Upstream: PRD-009/018/025; OPS-002–005; SEC-002–006; HLD §§5/7/8; LLD §§3/9/10.

## Customer experience and states

The check screen displays **Saved on this device** after a durable encrypted write, **Waiting to sync** after the customer queues an authorized upload, **Syncing**, **Synced**, or **Sign in to continue syncing**. These labels are independent of measurement validity. A customer can open history while offline. An interrupted capture remains invalid; restoring an app draft does not resume a scored task mid-run.

The **Upload check** sheet states the destination environment/account, data categories, study/protocol if applicable, and whether raw files are included. Raw files are excluded unless explicitly authorized. The confirm action is **Upload check**; cancel leaves the check local. Guest demo data never uploads. Authenticated local/QA engineering fixtures are created separately in their own account namespace and require explicit Upload check. Reconnection never queues new data and never overrides the default-off automatic-retry preference.

State transitions are local_draft → local_finalized → queued → registering → uploading_evidence → uploading_snapshot → finalizing → awaiting_result → synced. Retryable failures move to retry_wait with the next-attempt time. Authentication failures pause at auth_required; authorization revocation moves to blocked. Cancellation of an upload queue item cannot erase server records already accepted; the UI reports its actual delivery state and routes deletion to privacy controls.

## Engineering contract

Use SQLCipher, a random installation/account encryption key in OS secure storage, transactionally persisted drafts/finalized snapshots/outbox, and in-memory web preview. Store stable UUIDs, operation keys, expected ETag, X-Data-Generation, snapshot/evidence JCS digests, route, bounded payload references, attempt count, next retry time, and workspace epoch. Queue items reference immutable data; never rebuild them from the user's subsequently changed profile. Namespaces are environment plus authenticated subject or isolated demo identity.

POST sessions is followed by context/attempt/evidence-manifest submission, PUT snapshot with If-Match, and POST finalize with both snapshot and evidence digests. All retries reuse the original Idempotency-Key and exact logical body. Server acknowledgments are committed locally before the next phase. A lost response is resolved by replay or GET current state, not a new session. Handle 400/422 as permanent data errors, 401 as refresh/pause, 403 as blocked authorization, 409 as semantic/idempotency conflict, 412 as stale-revision conflict, 428 as missing precondition, 410 as retired-generation quarantine, 429 using bounded Retry-After, and 5xx/network failures with exponential backoff and jitter. Proposed transport defaults: 15-second request timeout, delays of 2/4/8/16/32/60 seconds capped at 60, eight automatic attempts per foreground cycle only for already requested operations when automatic retries are enabled; Retry-After is clamped to 1–3600 seconds; a longer server-required wait is shown for manual retry. A manual Retry resumes the same intent. Result-status reads may poll within their separate read budget. These are engineering settings and do not define clinical freshness.

Local storage failure blocks the **Saved** claim. Check data cannot spill to plaintext AsyncStorage, console output, analytics, or crash reports. Startup fails closed on a missing/corrupt encryption key and offers a clearly destructive local reset. Qualified capture requires a fresh online authorization in this release; cached availability never grants offline capture. Previously captured data stays protected while upload is reconciled. Withdrawal intent immediately stops local dependent work. Retired generations quarantine old queues and cannot replay deleted response bodies. Android process death and iOS suspension follow the same durable state machine; neither platform assumes that a background task will run.

## ADDED Requirements

### Requirement: AND-SYNC-001 Persist before announcing save
The app MUST write a complete local state transition and its referenced data in an encrypted transaction before showing a successful save.

#### Scenario: Storage transaction succeeds
- **GIVEN** a completed permitted check
- **WHEN** the finalization transaction commits
- **THEN** the app shows **Saved on this device** and can reopen the same record after restart.

#### Scenario: Disk is full
- **GIVEN** the encrypted database write fails
- **WHEN** the user finishes the check
- **THEN** the app reports the save failure and does not show a success state or queue a nonexistent record.

### Requirement: AND-SYNC-002 Require explicit authorized upload
The app and service MUST require account ownership and current upload scope before accepting a queued check, independently of application-notice acknowledgment.

#### Scenario: Customer cancels upload sheet
- **GIVEN** a local-only check
- **WHEN** the upload confirmation is canceled
- **THEN** no network mutation occurs and the check remains local.

#### Scenario: Study consent is revoked
- **GIVEN** a previously queued study check
- **WHEN** authorization is rechecked after revocation
- **THEN** upload is blocked and the app explains the permission change without retrying as another account or study.

### Requirement: AND-SYNC-003 Use stable idempotent operations
Each queued mutation SHALL retain its operation key, body digest, session UUID, and expected revision across retries and process restarts.

#### Scenario: Response is lost after server acceptance
- **GIVEN** a finalize request committed remotely but its response was lost
- **WHEN** the client retries
- **THEN** it receives the same logical result/job and no second specimen/task/session is created.

#### Scenario: Queue body is changed under the same key
- **GIVEN** an existing accepted idempotency key
- **WHEN** different content is submitted under that key
- **THEN** the service returns 409 and the app exposes a conflict rather than changing the frozen record.

### Requirement: AND-SYNC-004 Isolate users and environments
The app SHALL partition local records, credentials, and queue ownership by build environment and identity, and SHALL stop active synchronization on identity change.

#### Scenario: Two accounts use one phone
- **GIVEN** account A has unsynced records
- **WHEN** A signs out and B signs in
- **THEN** B cannot list or upload A's records.

#### Scenario: Production build receives local configuration
- **GIVEN** a production app/backend configuration
- **WHEN** a local issuer or AWS-emulator endpoint is supplied
- **THEN** startup fails closed; the configuration cannot silently redirect participant data.

### Requirement: AND-SYNC-005 Reconcile stale revisions without overwrite
The client SHALL preserve both local pending content and the authoritative server revision after a conflict and SHALL require a linked correction for a frozen server snapshot.

#### Scenario: Another device finalized the session
- **GIVEN** a stale local ETag
- **WHEN** PUT snapshot returns 412 for its stale precondition or 409 for a frozen-state conflict
- **THEN** the app fetches the server state and does not overwrite it.

#### Scenario: Correcting an accepted value
- **GIVEN** a finalized session requires correction
- **WHEN** a correction is created
- **THEN** reacquisition uses a new session UUID/target time and supersedes reference with no earlier physical components copied; an administrative report correction remains a distinct authorized workflow.

### Requirement: AND-SYNC-006 Bound retries and preserve terminal failures
Retries SHALL follow the documented error policy and SHALL never convert permission, validation, or conflict failures into unbounded background traffic.

#### Scenario: Rate limit response
- **GIVEN** HTTP 429 with a valid Retry-After
- **WHEN** scheduling the next attempt
- **THEN** the queue honors the delay within a documented bound and shows a waiting state.

#### Scenario: Invalid snapshot
- **GIVEN** HTTP 422
- **WHEN** the client classifies the failure
- **THEN** automatic retry stops and the customer can inspect the reported field error.

### Requirement: AND-SYNC-007 Preserve scientific and acquisition time
Synchronization SHALL retain original collection/capture times, clock uncertainty, and source flags; network receipt time MUST NOT replace the physiological target time.

#### Scenario: Upload occurs after a day offline
- **GIVEN** a previously captured record
- **WHEN** it reaches the service the next day
- **THEN** history retains the original check time and separately records synchronization/evaluation time.

#### Scenario: Reboot during scored game
- **GIVEN** an interrupted reaction run in a restored draft
- **WHEN** the application restarts
- **THEN** it marks that attempt invalid and cannot submit it as a completed uninterrupted task.
