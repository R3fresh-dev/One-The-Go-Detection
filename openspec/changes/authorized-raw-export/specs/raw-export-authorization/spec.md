## ADDED Requirements

### Requirement: RAW-EXP-001 Independently approve the exact participant-copy purpose
The service SHALL require immutable independently submitted, reviewed and
released typed `raw_export` authority for the exact account, generation, study,
raw kinds, literal participant-copy purpose, current retention version/hash,
notice version/hash and bounded expiry/size. Recording, upload, device, study or
model approval MUST NOT grant raw export permission. No setup SHALL seed a real
approval, and participant scope MUST NOT include privileged laboratory reports.

#### Scenario: Recording exists without export approval
- **GIVEN** an owned retained recording and current optional recording consent
- **WHEN** a participant requests its raw export without separate released authority
- **THEN** raw export is denied and metadata-only export remains available.

#### Scenario: The reviewer is also the submitter
- **GIVEN** a submitted raw-export version
- **WHEN** the same verified principal tries to approve or release it
- **THEN** the registry rejects the transition and no current export grant exists.

#### Scenario: Three distinct authorized principals release an exact grant
- **GIVEN** current independently approved dependencies and a typed owner/generation grant
- **WHEN** distinct submitter, reviewer and releaser complete its real registry lifecycle
- **THEN** its immutable version and content hash admit only the exact approved scope.

### Requirement: RAW-EXP-002 Bound and paginate current export choices
Current owner/generation approval discovery SHALL expose four authorities per
page and at most 128 sources per exact-authority page, explicit resumable cursors
and a 512 KiB response bound. It SHALL omit currently invalid and individually
over-budget sources without replacing explicit pagination by silent truncation.
It MUST NOT expose arbitrary cloud bucket/key/URL or another participant's data.

#### Scenario: Nine valid authorities contain maximum-sized notices
- **GIVEN** nine current independently released owned authorities
- **WHEN** the client follows each authority cursor
- **THEN** all nine are offered across bounded pages without response overflow.

#### Scenario: A source exceeds the complete export byte cap
- **GIVEN** a retained recording larger than its authority's uncompressed cap
- **WHEN** current export choices are requested
- **THEN** that source cannot be selected and other eligible choices remain usable.

### Requirement: RAW-EXP-003 Confirm a separate immutable raw-copy selection
Raw inclusion SHALL default off and require explicit artifact IDs, exact
authority and export-notice identities/hashes, strict true confirmation and the
actual acknowledgement time within the acceptance window. Context changes MUST
reset unfinished acknowledgement. Identical idempotent retry SHALL preserve the
original selection and acknowledgement and recheck current admission.

#### Scenario: Consent to recording is reused as export confirmation
- **GIVEN** the participant approved optional recording earlier
- **WHEN** raw export is requested without its separate confirmed export notice
- **THEN** the request fails without creating a raw job.

#### Scenario: An accepted reply was lost and the grant is later retired
- **GIVEN** an accepted raw export and its original request key/body
- **WHEN** the request is retried after authority retirement
- **THEN** current admission denies it rather than disclosing the stale approved scope.

#### Scenario: A separately confirmed owned selection creates a stable job
- **GIVEN** exact current authority and an explicitly acknowledged export notice
- **WHEN** the customer submits selected owned artifacts and retries the identical body/key
- **THEN** one pending job preserves the original selected sources and acknowledgement.

### Requirement: RAW-EXP-004 Pin selected retained sources
Acceptance SHALL require current account/generation/study and separate effective
raw consent, exact owned selected checks, supported results, permitted kinds,
retention/configuration identities and non-null verified source versions. It
SHALL freeze grant/source descriptors under JCS SHA-256 and set expiry to the
earliest approved lifetime, 24-hour limit, grant expiry and source deadline.

#### Scenario: The current key has a new S3 version
- **GIVEN** an accepted pinned original source version
- **WHEN** a different current object version appears
- **THEN** worker reads only the verified accepted version and checks its actual bytes.

#### Scenario: Withdrawal occurs during source retrieval
- **GIVEN** a raw job reading outside a database transaction
- **WHEN** its participant consent is withdrawn before the read completes
- **THEN** post-read admission rejects publication and no current ZIP is exposed.

### Requirement: RAW-EXP-005 Verify archive lineage and selected raw members
The worker and client SHALL bind the immutable approved raw tuple to both job
receipt and manifest; allow only exact selected `raw/<kind>/<UUID>.bin` members;
verify source version, byte size and SHA; and retain all existing structured
lineage/ZIP safety checks. Raw-inclusive omission text SHALL identify unselected
raw data; no job may claim a privileged laboratory report was included.

#### Scenario: A ZIP contains a rehashed unselected recording
- **GIVEN** an authenticated job permits only recording A
- **WHEN** a well-formed rehashed ZIP includes recording B instead
- **THEN** the client rejects the archive rather than importing or sharing it.

#### Scenario: An exact selected archive verifies against its authenticated job
- **GIVEN** a completed job with exact approved source descriptors
- **WHEN** its ZIP preserves all selected structured lineage and raw versions/hashes/bytes
- **THEN** the archive inspector validates it and exposes only the approved selected contents.

### Requirement: RAW-EXP-006 Re-admit protected delivery and cut off revoked streams
Delivery SHALL verify current account/family/generation/consent/grant/source
authority, exact S3 VersionId/length/SHA and bounded bytes before first disclosure,
then re-admit before every at-most-64-KiB chunk. It SHALL release its single
per-process buffer slot on failure or cancellation, use no-store and authenticate
before rejecting ranged/conditional requests. Previously sent copies cannot be
recalled; the next denied boundary MUST terminate further delivery.

#### Scenario: Expiry occurs while S3 download is delayed
- **GIVEN** a currently approved completed export
- **WHEN** it expires before the storage read returns
- **THEN** post-read admission returns a denial with no ZIP bytes disclosed.

#### Scenario: Revocation follows the first delivery chunk
- **GIVEN** a verified archive larger than 64 KiB
- **WHEN** raw permission is revoked after its first admitted chunk
- **THEN** the next admission fails and no second chunk is sent.

#### Scenario: An uninterrupted verified download succeeds
- **GIVEN** current authority and a completed exact-version ZIP
- **WHEN** storage bytes and every delivery-boundary admission remain valid
- **THEN** the signed-in owner receives the complete hash-matching no-store attachment.

### Requirement: RAW-EXP-007 Preserve terminal privacy receipts and recurring erasure
Expired, failed or revoked jobs SHALL expose only owned minimal terminal status
without download or raw authority. Invalid authority SHALL fence publication and
delivery before cleanup, and recurring version-aware owned-prefix erasure SHALL
retain failure/next-sweep information and remove late stale-worker arrivals.

#### Scenario: A stale worker uploads after the first cleanup sweep
- **GIVEN** revoked logical delivery and a completed first prefix sweep
- **WHEN** an older worker's output arrives later
- **THEN** the recurring sweep deletes its exact version and delivery remains denied.

#### Scenario: The customer refreshes after raw-copy cleanup
- **GIVEN** an owned revoked export after cleanup
- **WHEN** its status is refreshed
- **THEN** the terminal revoked receipt remains visible without grant or download metadata.

### Requirement: RAW-EXP-008 Bound the entire archive without partial omission
The complete structured/raw/manifest payload SHALL fit 50 MiB or a narrower
approved grant cap, and ZIP SHALL fit 64 MiB or a narrower approved cap. Each
structured record SHALL fit 512 KiB. Overflow MUST fail the whole export rather
than omit a selected record or exceed the bounded API/worker memory profile.

#### Scenario: Raw sources fit but their structured evidence exceeds the cap
- **GIVEN** raw files fit within the approved uncompressed byte limit
- **WHEN** adding selected structured records and the manifest exceeds that limit
- **THEN** the entire job fails without producing a partial downloadable archive.

#### Scenario: The complete selected archive fits all approved bounds
- **GIVEN** selected structured records, manifest and explicit raw sources within the narrower caps
- **WHEN** the fenced worker assembles and publishes the exact verified archive
- **THEN** the complete job succeeds without omitting a selected record or widening the limits.
