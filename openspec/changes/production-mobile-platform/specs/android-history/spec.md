# Android check history and historical detail

## Purpose and traceability

Make a user's own check records recoverable, readable, and accurately labeled across local and synchronized state. Preserve completed evidence and version history. Upstream: PRD §§5–6, PRD-018/020; HLD §§5–8; full specification APP-012/013, ANA-006/007/008/010, MOD-004/013, OPS-002/003/004/005, SEC-002/006.

## Shared contract authority

The [shared platform contracts](../../shared-contracts.md) are normative for release scope, workspace isolation, authentication, data generations, concurrency, privacy-job states, export selection, context freezing, and active-capture navigation. This feature SHALL follow those contracts; its UI preferences cannot weaken them.

## Customer journey and screen contract

1. **History list:** title “Your checks”, active workspace badge, **All checks / Pending sync** selection, and latest refresh status. Group by local calendar date; each row has acquisition date/time, result/session state, source badge, and a concise availability summary. Empty state “No checks yet” has **Start a check** (or **Start demo check**). An error leaves cached rows visible with **Try again**.
2. **Pagination:** **Load more** is an accessible explicit control; automatic loading may supplement it. A footer states whether all records or only cached records are available. Pending sync is a device-local queue filter and is labeled as such; it does not pretend to search all other devices' queues.
3. **Historical detail:** heading “Check details”, full acquisition time/timezone, session ID, workspace/source, and status. Separate sections show saliva analytes with qualifier/units/basis, pupil capture availability, cardiac measurement/source, reaction-task features and quality, and original profile version. A separate “Recorded / Analyzed / Saved to account” timeline prevents delayed analysis from appearing contemporaneous with collection.
4. **Actions:** **Export this check** delegates to the data-export feature with `{kind:"single",session_ids:[this_session_id]}`; **Back to history** restores list position. If the record has a superseding correction, show **View newer revision** and **View original** with both IDs/times. There is no Edit finalized measurement action. Drafts offer **Continue check** through session orchestration; terminal invalid/canceled records remain terminal.

## Data and API contract

`GET /v1/sessions?cursor=<opaque>&limit=20` returns current-user records sorted by `(created_at DESC, session_id DESC)`, `next_cursor`, and optionally an explicitly named authoritative total. The cursor binds owner, environment, sort, and a stable pagination boundary; clients do not decode or alter it. `GET /v1/sessions/{id}` returns authorized metadata, immutable snapshot, and nullable result. The detail representation distinguishes not-finalized, result-pending, failed, invalid, inconclusive, and measurement-only; a null result does not mean normal. A 404 and an unauthorized inaccessible ID use the shared non-enumerating policy. Ownership is derived server-side.

Local rows carry workspace/subject, UUID, server revision/ETag when known, synchronization state, and a local capture timestamp. A synchronized row replaces its same-identity local projection without adding a duplicate. Server results never overwrite original immutable source records; supersession adds a linked record. Date grouping uses the current display timezone, while exported/stored timestamps remain UTC and the detail includes offset. Analyte `below_loq`, `above_range`, `not_detected`, `not_measured`, and `invalid` display their exact meanings; not-quantified values are not zero. Research-estimate content is unavailable in this measurement-only release even if a manipulated response claims otherwise; unexpected result types produce an unsupported-state message and no probability.

### AND-HIST-001/003/004/005/006 integration resolution

`inference_available=false` SHALL apply equally to live results, cached historical detail, and export projections. A correctly shaped/linked `research_estimate` is unsupported in this release and never displays a probability. Historical context SHALL identify the immutable profile/context revision frozen at Start check, selected capture attempts, and the companion-evidence references defined centrally. Retrying a finalized invalid acquisition SHALL enter the shared replacement-check flow with a new session/target time; the original snapshot remains read-only.

The typed export entry SHALL preserve `{kind:"single",session_ids:[UUID]}` across local/synced source selection, authentication, navigation, and restart. Its review says **1 selected check**, names the date/ID, and includes only that check's allowed associated profile/context revisions, attempt evidence, linked results, and explicitly permitted optional artifacts under the shared export contract. A route must not broaden to all records; any scope expansion requires a visibly new summary and confirmation. Data-generation changes invalidate old selections/queue work; stale responses cannot repopulate a cleared generation.

Offline history follows the sign-in feature's exact account-lock policy. Canceled/failed device authentication leaves it locked. Clearing local records, keeping records at sign-out, and remote deletion use their separate policies; a retained signed-out namespace is not an offline read permission.

### AND-HIST-005 consolidated detailed contract

Cached detail SHALL remain available offline only for the same still-signed-in account after successful device credential/biometric authentication, and SHALL show its last successful synchronization time. Signed-out account caches remain locked until same-issuer/subject reauthentication. Uncached detail SHALL show “This check is not available offline” with **Back** and **Try again**. Retry SHALL use bounded backoff and stop on logout, account change, deletion, or terminal authorization failure.

## ADDED Requirements

### Requirement: AND-HIST-001 Correct ownership and provenance

History SHALL show only the active workspace's permitted records. Each row/detail SHALL retain simulated/reference-lab/prototype/validated-sensor provenance and the original acquisition time. Switching account or workspace SHALL clear the previous presentation before loading another partition; a stale response MUST NOT restore it.

#### Scenario: hist-demo-isolation
- **GIVEN** both demo and account checks exist on the device
- **WHEN** account History opens
- **THEN** only authorized account checks are listed and demo rows require an explicit switch.

#### Scenario: hist-cross-account-id
- **GIVEN** an account receives a deep link to another account's session ID
- **WHEN** detail is requested
- **THEN** no snapshot, profile, existence-revealing title, or measurement is disclosed.

### Requirement: AND-HIST-002 Stable pagination and deduplication

History SHALL consume opaque server cursors, deduplicate by logical record identity/revision, and preserve list position after detail navigation. Newer inserts SHALL appear after a refresh without shifting or repeating records in an existing pagination boundary. An invalid/expired cursor SHALL offer **Refresh list** and retain readable cached records.

#### Scenario: hist-new-record-between-pages
- **GIVEN** page one has loaded and a new check is finalized
- **WHEN** page two is requested with the original cursor
- **THEN** existing rows are neither duplicated nor skipped and the new check appears after refresh.

#### Scenario: hist-local-server-same-check
- **GIVEN** a local pending row is later returned by the server with the same UUID
- **WHEN** reconciliation completes
- **THEN** one row remains with updated sync status and unchanged source identity.

### Requirement: AND-HIST-003 Faithful state, qualifier, and time display

Detail SHALL display canonical units, original report units where present, assay basis, qualifier, collection/analysis times, quality, and source. Missing/censored/invalid values MUST NOT be rendered as measured zero. The app SHALL distinguish measurement-only, invalid, inconclusive, pending, and unavailable states without interpreting them as sobriety or intoxication.

#### Scenario: hist-below-loq
- **GIVEN** THC-COOH has qualifier below_loq with no quantified value
- **WHEN** detail is opened
- **THEN** it reads “Below quantification limit” with the reported limit when available, and no 0 ng/mL or inferred detection claim appears.

#### Scenario: hist-delayed-laboratory-result
- **GIVEN** a sample collected Monday was analyzed Wednesday
- **WHEN** its result is viewed Thursday
- **THEN** all relevant dates are distinct and the laboratory result is not described as a Thursday physiological assessment.

#### Scenario: hist-linked-research-estimate-is-still-unsupported
- **GIVEN** an authenticated account receives a schema-valid research_estimate with matching session and digest
- **WHEN** History renders its detail
- **THEN** the app shows the unsupported-result state without displaying probability, classification, or a research-estimate card.

### Requirement: AND-HIST-004 Immutable records and linked corrections

Finalized checks SHALL be read-only. Superseding corrections SHALL retain the original immutable record and expose both identities/revisions with clear direction. Profile edits, new model files, new device calibration, and date-display changes MUST NOT recompute or silently rewrite historical results.

#### Scenario: hist-profile-edited-later
- **GIVEN** a historical check contains profile revision A
- **WHEN** current profile revision B is saved
- **THEN** historical detail continues to display A's values and acquisition context.

#### Scenario: hist-correction-linked
- **GIVEN** a reviewed correction supersedes a finalized record
- **WHEN** either version is opened
- **THEN** the original remains readable and a labeled link identifies the other version without overwriting it.

### Requirement: AND-HIST-005 Offline detail and bounded retry

The implementation SHALL satisfy the AND-HIST-005 consolidated detailed contract and the shared platform contracts, including their exact states, authorization, persistence, and failure behavior.

#### Scenario: hist-offline-cached-detail
- **GIVEN** an encrypted cached snapshot and no network
- **WHEN** its row is selected after local unlock
- **THEN** the stored snapshot is displayed with its cached state and no remote result is invented.

#### Scenario: hist-offline-uncached-detail
- **GIVEN** only a list summary is cached
- **WHEN** the user opens detail offline
- **THEN** the app explains unavailability and does not fill the screen from unrelated fixtures or another check.

#### Scenario: hist-signed-out-device-unlock-is-insufficient
- **GIVEN** A retained encrypted history when signing out
- **WHEN** the user opens the app offline and passes device unlock
- **THEN** A's history stays locked until the same issuer and subject reauthenticate; other workspaces remain separate.

### Requirement: AND-HIST-006 Pending operations and deletion reconciliation

Pending-sync filtering SHALL derive from the local durable queue and show only its active subject. A remotely deleted or access-revoked check SHALL be removed from available detail/cache according to the deletion/tombstone policy when reconciled. An in-flight response arriving after deletion MUST NOT resurrect its data. Export SHALL delegate to the scoped export flow and not share raw data immediately upon tapping a row.

#### Scenario: hist-pending-filter
- **GIVEN** two locally queued checks and three synchronized checks
- **WHEN** Pending sync is selected
- **THEN** only the two queue-owned checks appear and the label states that this is this device's queue.

#### Scenario: hist-delete-race
- **GIVEN** a detail request is in flight when its deletion is accepted
- **WHEN** the old response arrives
- **THEN** it is discarded according to the deletion generation/tombstone and cannot repopulate History.

#### Scenario: hist-single-check-export-scope-survives-source-change
- **GIVEN** History starts Export this check for A while unrelated checks B and C exist
- **WHEN** the user changes This device to Synced records or resumes after reauthentication
- **THEN** the selected scope remains only A and related authorized evidence; B and C cannot enter the archive without a new expanded-scope summary and confirmation.

### Requirement: AND-HIST-007 Accessible records and iOS parity

Rows SHALL expose one meaningful accessible summary and a labeled detail action without repeating every decorative icon. Dates SHALL be readable absolute values; source/state SHALL not depend on color. Tables SHALL become stacked labeled fields on narrow or large-text layouts. iOS SHALL implement equivalent ownership, pagination, qualifiers, revision links, offline states, and export entry using VoiceOver/Dynamic Type and platform back navigation.

#### Scenario: hist-large-text-detail
- **GIVEN** 200% font scaling and a narrow Android display
- **WHEN** a saliva detail section contains all three analytes
- **THEN** names, values, units, and qualifiers remain legible and reachable without clipped columns.

#### Scenario: hist-ios-back-position
- **GIVEN** the iOS user opens a row after loading three pages
- **WHEN** they navigate back
- **THEN** the same selected row and list position are restored with no duplicated page fetch.

## Acceptance evidence

Required evidence: cross-account denial, stable-cursor/concurrent-insert tests, local/server deduplication, qualifier/unit/time fixtures, profile immutability, supersession navigation, offline cache/no-cache paths, deletion race, and Android/iOS accessibility review. A history record is evidence of recorded measurements and provenance only; its presence does not establish clinical accuracy.
