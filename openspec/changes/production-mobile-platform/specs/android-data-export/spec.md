# Android feature: export my data

Normative integration: [shared application contracts](../../shared-contracts.md) and [platform contracts](../../platform-contract.md). These define the exact cross-feature DTOs, error states, generation/revocation rules, current-release limits, and implementation evidence.

## Purpose and traceability

Allow a customer to obtain a deliberate, understandable copy of their own records without exposing other users or bypassing study/media policy. Upstream: PRD-018/025; SEC-001–006; OPS-003/005; HLD §§6/8; LLD §§9/10. Deletion belongs to android-privacy-controls; this capability owns export generation and delivery.

## Customer journey

Settings → **Privacy and data** → **Export my data**. The customer chooses **This device** or **Synced records** and sees the fixed typed selection: one check, selected checks, or all owned records. History's Export this check supplies exactly that UUID. Changing source preserves it; expanding scope requires a new summary/confirmation. The summary lists profile versions, check measurements, task summaries, result metadata, and dates. Raw eye recordings and ECG waveforms are excluded by default and are offered only under an actual current permitted policy. The screen states **Anyone you share the exported file with may be able to read it.** The primary action is **Create export**; cancel performs no export or upload.

A local export is prepared from the unlocked active account/demo namespace and then invokes the system share sheet. A synced export creates a cloud job and shows **Preparing export**, **Ready until …**, **Expired**, or an actionable failure. The customer can leave the screen and revisit the job. **Download and share** fetches the file to an app-private temporary path and opens the OS share sheet. The app does not automatically email, message, or publish it. An expired export offers **Create a new export**.

## Engineering contract

POST /v1/privacy/exports accepts the shared selection DTO (single/selected/all), at most 500 checks, format=json_zip, and include_raw=false. The structured archive is at most 50 MiB uncompressed with bounded 512 KiB structured records/attempts. The service derives owner/study scope, validates consent for any raw inclusion, stores an idempotent job, and queues processing. GET /v1/privacy/jobs/{id} returns kind=export and pending/running/completed/expired/failed plus accepted/start/completion/expiry times, manifest hash, size, and the authenticated same-origin download path with bounded freshness metadata. It does not expose S3 keys of unrelated objects.

The ZIP contains manifest.json, profile.json, checks/<UUID>.json, and approved optional artifact files using generated UUID filenames. The manifest includes schema/canonicalization versions, export time, selected record IDs and hashes, provenance/qualifiers, and exclusions. No arbitrary user filename becomes an archive path. A job snapshots its record selection so later profile edits do not retroactively alter an export. Deleted/revoked records are rechecked before authorizing a new download stream. GET /v1/privacy/jobs/{id}/download requires the current owner token/generation/policy; a copied path grants no authority. Already authorized streams/bytes cannot be recalled, as stated in the sharing notice. Stream records with bounded memory and declared size limits; oversized exports fail visibly; this release has no partitioned-export alternative and never silently truncates.

Private version-pinned S3 exports logically expire after 24 hours; authenticated download-path metadata stays fresh at most five minutes and never outlives expiry. S3 physical cleanup is asynchronous; API expiry is enforced independently. No direct S3 bearer GET is returned. Temporary mobile files are removed after sharing/cancelation or on the next startup cleanup. Export retention is separate from primary-data retention. No unauthenticated direct download route exists. Local exports remain local unless the customer chooses a destination in the share sheet. Android FileProvider/content URI and iOS share-sheet handling use app-private paths; neither writes to a public downloads folder without the user's choice.

## ADDED Requirements

### Requirement: AND-EXP-001 Require a deliberate scope and action
An export SHALL begin only after the customer sees its scope, exclusions, and sharing notice and selects **Create export**.

#### Scenario: Local single-check export
- **GIVEN** History selects one check while unrelated records also exist
- **WHEN** the customer confirms This device for that exact selection
- **THEN** only the selected check, its frozen profile/context, attempts, alcohol, and linked results are exported locally, with no cloud mutation or unrelated profile revision.

#### Scenario: Confirmation is canceled
- **GIVEN** the export summary sheet
- **WHEN** the customer cancels
- **THEN** no job/file/share action is created.

### Requirement: AND-EXP-002 Enforce ownership on selection and download
The service MUST authorize every selected record and job-status request, and authorize current owner/generation/policy at the authenticated download gateway before opening a new byte stream.

#### Scenario: Own synced records
- **GIVEN** a signed-in owner selecting their records
- **WHEN** the export completes
- **THEN** the archive contains only the authorized selected records.

#### Scenario: Another user's session is injected
- **GIVEN** an export selection containing a foreign UUID
- **WHEN** the request is validated
- **THEN** it is rejected without including or disclosing the foreign record.

### Requirement: AND-EXP-003 Preserve evidence semantics
Exports SHALL retain units, censoring, nulls, source labels, capture/evaluation times, record versions, and hashes without converting missing values into measurements.

#### Scenario: Censored saliva result
- **GIVEN** a below_loq measurement
- **WHEN** exported
- **THEN** value remains null and the qualifier/limit/original report remain available.

#### Scenario: Historical reanalysis
- **GIVEN** multiple linked results for one session
- **WHEN** selected for export
- **THEN** their immutable IDs, versions, and replacement relationship are preserved.

### Requirement: AND-EXP-004 Separate raw-data authorization
Raw recordings SHALL be excluded unless explicitly selected and currently authorized by the relevant retention/consent policy.

#### Scenario: Default export
- **GIVEN** an ordinary export request
- **WHEN** the job is assembled
- **THEN** raw eye/ECG files are excluded and the manifest records the exclusion.

#### Scenario: Raw consent is revoked during processing
- **GIVEN** raw inclusion was initially allowed
- **WHEN** permission is revoked before delivery
- **THEN** the gateway blocks a subsequently initiated download and reports the changed scope or failed job; it makes no promise to recall bytes already authorized/delivered.

### Requirement: AND-EXP-005 Bound availability and clean temporary copies
Cloud exports SHALL become inaccessible after 24 hours, download metadata SHALL expire within five minutes, and mobile temporary files SHALL be removed after sharing/cancelation or startup cleanup. Physical S3 deletion follows the bounded asynchronous cleanup policy.

#### Scenario: Expired export is reopened
- **GIVEN** an export past expires_at
- **WHEN** the customer opens it
- **THEN** no new valid ticket is issued and a new export action is offered.

#### Scenario: Share sheet is canceled
- **GIVEN** a downloaded temporary export
- **WHEN** the share sheet returns without sharing
- **THEN** the app schedules immediate cleanup and does not claim it sent the file anywhere.

### Requirement: AND-EXP-006 Make jobs idempotent and failures visible
Repeated identical export requests with one idempotency key SHALL resolve to one job; failures SHALL preserve a status and reason without returning a partial archive as complete.

#### Scenario: Export request response is lost
- **GIVEN** a created cloud job
- **WHEN** the same request is retried
- **THEN** the same job ID is returned.

#### Scenario: Artifact verification fails
- **GIVEN** a selected permitted artifact whose bytes fail the stored hash
- **WHEN** the worker assembles the export
- **THEN** the job fails with a safe reason and no complete-download state is exposed.

### Requirement: AND-EXP-007 Prevent archive path and memory abuse
Archive paths SHALL use fixed prefixes and generated identifiers, and export processing MUST enforce selection/file/total-size limits.

#### Scenario: Profile text resembles a path
- **GIVEN** text containing ../ or absolute-path characters in user data
- **WHEN** an export is generated
- **THEN** it remains JSON content and cannot control an archive entry name.

#### Scenario: Export exceeds its configured bound
- **GIVEN** selected data larger than the supported single-export limit
- **WHEN** the job validates size
- **THEN** it reports an explicit size failure and never silently omits records or invents an unimplemented partitioning workflow.
