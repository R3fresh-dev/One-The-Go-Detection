# Reference-laboratory specimen collection

Scope: Android/iOS participant collection of one identified specimen under an actual approved reference-lab method; separate authorized analytical import. This capability completes AND-SAL-001/002/005/006 and preserves ANA-001/012, LLD section 4 and the [engineering design](../../design.md).

## ADDED Requirements

### Requirement: SALCOL-001 Dispatch the actual reference-lab adapter
The client and service SHALL recognize `reference_lab_import_v1` as an approved collection/laboratory handoff workflow and SHALL not require BLE possession, reader nonce or unrelated electronic calibration. Availability SHALL reflect the complete installed collection path and current owned study/configuration/method authority; unsupported assay-reader adapters SHALL remain refused.

#### Scenario: Approved laboratory method without a peripheral
- **GIVEN** an authenticated participant has current consent and a released reference-lab collection configuration
- **WHEN** Saliva is opened with no BLE reader
- **THEN** approved instructions and collection actions are available, and no physical-reader start is attempted.

#### Scenario: Unsupported cartridge-reader configuration
- **GIVEN** a configuration names an unimplemented assay reader
- **WHEN** availability or Start is evaluated
- **THEN** the app identifies the missing adapter rather than substituting the laboratory form, a timer or a generic ADC reading.

### Requirement: SALCOL-002 Render only approved collection-form rules
The form SHALL use the exact released method/version and typed rules for status, volume/buffer/dilution, collector/container, lot/expiry and handling. Nulls SHALL retain an approved reason from `unknown`, `declined` or `not_applicable`. Impossible quantities, incompatible dilution, expired supply or missing required data SHALL prevent a valid collection claim. An explicit invalid disposition with reasons MAY preserve the failed attempt without analytical output.

#### Scenario: Approved buffered collection
- **GIVEN** the method permits measured saliva/buffer volumes and defines the dilution convention
- **WHEN** the participant records those values and current lot/handling information
- **THEN** the bounded form retains the explicit quantities, method/version and dilution meaning in companion metadata.

#### Scenario: Unknown required volume or expired supply
- **GIVEN** a required quantity is unknown or the submitted supply is expired
- **WHEN** Record sample is selected
- **THEN** the service refuses a valid collection claim with actionable field reasons, leaves quantities uninvented and offers an explicit immutable invalid disposition instead of silently losing the failed attempt.

#### Scenario: Protocol permits an unknown optional field
- **GIVEN** a field is optional and the released method permits an explicit unknown reason
- **WHEN** the participant declines it
- **THEN** null and that reason are preserved rather than storing zero or an assumed value.

#### Scenario: Unsupported or contradictory null reason
- **GIVEN** a missing field has a free-text or unapproved reason, or a present value also claims to be missing
- **WHEN** collection is submitted
- **THEN** exact null-reason validation rejects it; the service cannot manufacture permitted method semantics from caller text.

### Requirement: SALCOL-003 Allocate specimen and collection lineage before start
An owned draft/context SHALL exist before collection. The workflow SHALL allocate distinct specimen and collection-attempt identities before fresh online start and SHALL preserve actual collection-event time separately from arm, server acceptance, analysis and import times. A form timer or delayed import SHALL not establish or replace the collection time.

#### Scenario: One collection supplies multiple analytes
- **GIVEN** a started owned specimen attempt and its current instruction/start authority
- **WHEN** the specimen is collected and later analyzed for several analytes
- **THEN** every resulting report references the same original specimen and collection event, with separately identified analytical attempts.

#### Scenario: Wrong specimen or impossible event time
- **GIVEN** the draft expects specimen A or the claimed collection time falls outside admitted chronology
- **WHEN** specimen B or impossible time is submitted
- **THEN** identity/chronology validation refuses without relabeling the sample or replacing its original event.

### Requirement: SALCOL-004 Admit an immutable participant collection receipt
The server SHALL accept collection metadata only under the exact owned started attempt, current instruction receipt, configuration/version/full digest, consent and generation. Its immutable receipt SHALL bind the specimen and complete metadata digest. The operation SHALL reject participant analytical values, laboratory-role claims and forged import/provenance authority.

#### Scenario: Current complete sample record
- **GIVEN** an admitted participant collection with complete permitted metadata
- **WHEN** Record sample succeeds
- **THEN** the returned receipt binds the exact sample, attempt, protocol/configuration, current consent and original metadata digest without asserting a measured concentration.

#### Scenario: Customer submits a quantified laboratory result
- **GIVEN** a participant collection form or manually edited request
- **WHEN** it includes THC values or laboratory/import-role assertions
- **THEN** the API rejects the added authority and no measured analyte or authorized laboratory receipt is created.

#### Scenario: Lost accepted response
- **GIVEN** collection was accepted but the response was lost
- **WHEN** the exact retained body/key is retried
- **THEN** the original immutable receipt is reconciled without creating a second specimen, changing collection time or reopening expired authority.

### Requirement: SALCOL-005 Preserve pending analysis and independent staff import
Collection SHALL display analytical work as pending without invented values. Distinct staff import SHALL require current staff/study/method authority and the participant-owned draft, verified report, exact specimen/receipt, generation and consent. Evidence stays participant-owned; audit retains actor and target. Measurements preserve original times, qualifiers, units and basis. Participant refresh SHALL not self-import results.

#### Scenario: Distinct staff imports the participant report
- **GIVEN** an admitted collection remains in its participant-owned draft and a different currently authorized staff account verifies the matching participant-owned report
- **WHEN** the existing laboratory import operation accepts it
- **THEN** the participant can refresh the independently approved evidence while the original collection identity/time and analytical provenance remain intact.

#### Scenario: Laboratory response is unavailable
- **GIVEN** a collected sample has no accepted report or the client is offline
- **WHEN** the saved check is reviewed
- **THEN** it shows analysis pending/not measured and no timer, prior reading or missing response becomes a concentration or impairment estimate.

#### Scenario: Foreign target or caller scope
- **GIVEN** an authorized staff caller but a target from another study/generation or a mismatching specimen/report
- **WHEN** initial import is attempted
- **THEN** target-scope validation refuses; the staff caller's owner/generation or supplied participant identifier cannot replace actual participant authority.

#### Scenario: Consent changes before import
- **GIVEN** a collection was accepted under an earlier current scope
- **WHEN** withdrawn consent, retired configuration or foreign staff/report is used for import
- **THEN** current authority refuses; the historic collection receipt does not restore analysis access.

### Requirement: SALCOL-006 Retain failed attempts and immutable finalized boundaries
Collection failure/cancellation SHALL preserve its specimen/attempt identity, actual disposition and reasons. A protocol-permitted prefinalization retry SHALL allocate and link a new attempt/sample. A new specimen after finalization SHALL require a replacement check; same-specimen correction/reanalysis SHALL use the existing independent companion-revision workflow and SHALL not mutate the finalized manifest.

#### Scenario: Inadequate volume before finalization
- **GIVEN** a collection fails its approved adequacy rule
- **WHEN** the protocol permits retry
- **THEN** a new sample/attempt links the failed one and obtains fresh current instructions/start without silently reusing the old specimen.

#### Scenario: Explicit invalid collection receipt
- **GIVEN** an inadequate or expired collection cannot be claimed valid
- **WHEN** the participant records an invalid disposition with actual metadata and an explicit reason, or cancels its started attempt
- **THEN** the failure lineage remains immutable and later retry cannot erase it or turn it into an accepted analytical concentration.

#### Scenario: Corrected finalized laboratory report
- **GIVEN** a check and original report are finalized
- **WHEN** authorized staff accepts a same-specimen correction
- **THEN** the immutable original remains, a separately identified companion revision is added and later reanalysis retains its own lineage.

### Requirement: SALCOL-007 Apply privacy and preserve complete collection evidence
Collection metadata, receipts and failed/pending analytical lineage SHALL remain in the encrypted owned workspace and bounded immutable evidence/export contracts. Withdrawal, generation retirement, account switch or interruption SHALL stop acceptance and quarantine dependent work. Raw recording/upload/export remain separately authorized and SHALL not be inferred from collection consent.

#### Scenario: Owned evidence review and export
- **GIVEN** accepted collection metadata and permitted immutable evidence
- **WHEN** the participant reviews, explicitly uploads or exports the check
- **THEN** specimen identity/time, protocol/receipt scope, null reasons, volumes/handling and analytical status survive with their digests and separate provenance.

#### Scenario: Withdrawal while collection response is delayed
- **GIVEN** the customer withdraws or switches workspace before a pending collection callback completes
- **WHEN** that callback returns
- **THEN** it cannot revive the old form, accepted specimen, queue or current collection authority in the replacement scope.

### Requirement: SALCOL-008 Preserve pending chronology and versioned projections
Active/pending analysis SHALL remain a resumable draft and block finalization until genuine import or explicit abandonment settles it. Submission and collection-to-analysis limits SHALL be 1–3600 and 1–604800 seconds. Strict Session 0.1 SHALL keep sample-only/empty analytical projections and typed companion details. Abandonment SHALL preserve collected evidence, require permitted missing-channel scope and never satisfy a required model measurement.

#### Scenario: Save and resume a pending laboratory handoff
- **GIVEN** the immutable collection receipt exists but its genuine report is pending
- **WHEN** the participant saves, leaves, resumes or continues to another supported stage
- **THEN** the same sample/attempt and pending status remain, acquisition is not repeated and finalization reports `LAB_ANALYSIS_PENDING` without discarding the draft.

#### Scenario: Collection submission arrives too late
- **GIVEN** the released method's maximum submission delay has elapsed since actual collection
- **WHEN** the original collection request is first admitted
- **THEN** the service refuses a new valid receipt rather than substituting upload time; an already accepted exact-key response remains historical evidence only.

#### Scenario: Delayed laboratory evidence is not current state
- **GIVEN** a report's actual analysis falls outside the approved collection-to-analysis interval, or current result acquisition/delivery bounds fail
- **WHEN** staff imports evidence or research execution is considered
- **THEN** the relevant chronology gate refuses rather than using import time as collection/analysis time or presenting delayed evidence as current impairment.

#### Scenario: Strict legacy companion compatibility
- **GIVEN** a sample is collected without measured analytical values
- **WHEN** its Session 0.1 projection and typed companion evidence are generated
- **THEN** the strict legacy projection retains empty/null/not-measured analytical values while protocol, instruction receipts and collection metadata remain in declared companion contracts; no unknown legacy field or forged lab provenance is inserted.

#### Scenario: Required versus optional model channel
- **GIVEN** a collection remains pending
- **WHEN** an independently approved 1.1 manifest requires its chemical measurement or explicitly permits that channel to be missing
- **THEN** pending collection cannot satisfy the required measurement; any separately eligible result still obeys exact approved missing-channel, provenance, tuple, freshness and delivery rules without deriving a value from pending status.

#### Scenario: Explicitly abandon pending analysis
- **GIVEN** an actual collected specimen is awaiting analysis and the participant explicitly confirms abandonment
- **WHEN** a current owned immutable abandonment proof settles the pending analytical handoff
- **THEN** the actual sample and original collection attempt remain unchanged, analysis is shown canceled, delayed report/replay cannot revive it, and finalization succeeds only when current configured minimum channels permit missing chemistry; otherwise it identifies the missing requirement.
