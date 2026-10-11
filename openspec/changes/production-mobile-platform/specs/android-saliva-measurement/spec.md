# Android saliva measurement

Scope: sample collection guidance, assay availability, exact analyte-result semantics, and review on Android with equivalent iOS behavior. This specification extends ANA-001–013, APP-012, and LLD section 4. It specifies working forms, adapters, and failure states; it does not invent a portable THC assay or a concentration-to-impairment threshold.

Engineering boundary: capability decisions come from GET /v1/me/capabilities; laboratory imports use the authorized POST /v1/research/lab-imports operation. An ordinary participant form SHALL not grant laboratory import privileges or bypass method/calibration verification.

Shared normative baseline: [shared application contracts](../../shared-contracts.md), especially release/workspace policy, frozen context and companion evidence, qualified online starts, immediate cancellation, immutable artifacts, and the Android/iOS software matrix. These rules govern the same behavior on both platforms.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-SAL-001 detailed contract

The Saliva screen SHALL explain that one identified collection can supply multiple analyte channels and SHALL show the selected mode, collection-method version, reader state, and available channels. Parent THC SHALL be the initial assay candidate; THC-COOH and 11-OH-THC SHALL remain separately available or unavailable. Actions SHALL include View collection instructions, Start collection, Record sample, Read cartridge when permitted, and Use simulated sample only in explicit synthetic mode. Physical collection instructions SHALL resolve to the approved method, required handling, volume/dilution, and materials. With no approved method or selective calibrated assay, the app SHALL expose a concrete unavailable state and SHALL not provide a generic procedure, timer-derived concentration, or electrical-signal-to-THC formula.

A qualified collection/read start SHALL obtain a fresh online authorization/start acknowledgment for its attempt, approved configuration, and bound reader where applicable. Cached capability expiry/status SHALL only explain availability; this release has no offline qualified start. An unprovisioned radio SHALL supply only explicit synthetic records. No currently shipped configuration SHALL imply that assay qualification or inference is available.

### AND-SAL-002 detailed contract

Before an actual sample is accepted, the app SHALL allocate sample_id and collection_attempt_id under the session and capture collection_method_id/version, collected_at, collection status, quality flags, and the selected method's volume/dilution fields. Available fields SHALL include saliva volume in mL, buffer volume in mL when relevant, dilution factor with its definition, collector/container identity, cartridge or collection lot, expiry, operator/automation reference, and storage/handling events when the protocol requires them. Missing values SHALL remain null with reasons; zero SHALL not mean unknown. Collected_at SHALL be the collection event, not the import or reader finish time. A not-collected specimen SHALL have null collection time and no analyte results.

The strict v0.1 specimen/analyte objects SHALL remain the selected projection. Collection fields, volume/dilution definitions, lot/handling/adequacy events, separate collection/analysis attempts, operator evidence, and configuration/authorization references SHALL be retained in the bounded saliva component of CaptureAttempt 1.0.0 and linked immutable CaptureContext/EvidenceManifest, not silently omitted or inserted as unknown v0.1 fields. Canonical hashes SHALL cover the complete retained context/terminal attempts; selection SHALL cross-check sample IDs, collected_at, status, quantities, and sources.

### AND-SAL-003 detailed contract

Each analyte measurement SHALL use one of THC, THC_COOH, or OH11_THC and preserve its measurement/sample IDs, method, source, calibration, instrument, lot, collected/measured times, quality, and original report. Canonical concentration SHALL use ng/mL, with finite numeric values only for quantified results. The permitted qualifiers SHALL be quantified, below_loq, above_range, not_detected, not_measured, and invalid. For every non-quantified qualifier, value_ng_ml SHALL be null. Below-LOQ, detection, and above-range displays SHALL name the relevant limit and units; invalid SHALL display its reason, and not_measured SHALL say Not measured. UI wording SHALL not turn a BLQ or <LLOQ report into confirmed detection.

### AND-SAL-004 detailed contract

The import adapter SHALL preserve original_report.value, unit, and qualifier. A pg/mL numeric value SHALL convert to ng/mL by division by 1000; its associated limits and uncertainty SHALL use the same conversion. assay_basis SHALL distinguish free, total_after_hydrolysis, and unspecified. concentration_basis SHALL distinguish neat_oral_fluid, collected_mixture, and unspecified. correction_status SHALL distinguish not_corrected, laboratory_corrected, and unspecified. Unit conversion SHALL not multiply by the sample dilution factor. Unknown basis SHALL be retained and flagged for incompatible inference rather than guessed. A later approved transformation SHALL create a linked record with a versioned adapter, original report, and explicit transformation provenance.

### AND-SAL-005 detailed contract

Semantic validation SHALL reject nonfinite quantities, contradictory LOD/LOQ/upper-limit ordering, quantified values outside the declared quantification interval, negative volumes, impossible timestamp ordering, and mismatched sample lineage. Unrun analytes SHALL use not_measured with null analytical time, method, instrument, and calibration; the sample itself must actually exist for such a channel record. Source SHALL be simulated, reference_lab, prototype_sensor, or validated_sensor, with each claim independently verified by the applicable registry/import permission. A participant or consumer form SHALL not self-attest reference_lab or validated_sensor. Approved laboratory import SHALL require the research/operator role and source evidence; a string in a payload SHALL not grant that role.

Reader-backed source verification SHALL bind the server-owned key registry, environment/account generation, session/attempt/authorization, boot/sequence, configuration hash, and exact normalized payload digest according to shared contracts §6. Laboratory evidence SHALL retain its independently authorized import identity and original report linkage. Neither a client assertion nor a server available flag lacking actual qualification evidence SHALL create analytical validity. Local withdrawal intent stops collection/read and quarantines pending upload immediately; backend policy and generation SHALL be checked again before attestation, artifact verification, and finalization.

### AND-SAL-006 detailed contract

The saliva workflow SHALL distinguish inadequate volume, contamination, overflow, expired supply, unreadable cartridge, failed control, incompatible calibration, reader disconnect, analysis pending, and above-range report. Instructions for correction SHALL come from the selected method; no universal rinse/wait/retest interval SHALL be invented. Before finalization, retrying failed collection SHALL create a new sample attempt under the same parent and link the failed one. After local or remote finalization, acquiring a new sample SHALL require Start replacement check with a new session/target and no carried physical acquisitions. Reanalysis of the same specimen or a corrected laboratory report SHALL use a separate authorized administrative revision workflow preserving original collection/target times, report lineage, and immutable earlier evidence; it SHALL not append to a finalized manifest or masquerade as a fresh current assessment. A delayed lab result SHALL remain associated with the original sample collection and assessment time, and offline completion SHALL never invent analytical results.

Cancel, Back, withdrawal intent, or hiding an active collection/read screen SHALL stop local acceptance and settle the attempt before any confirmation or navigation; a later Keep draft choice SHALL not resume the interrupted read. Each permitted new attempt SHALL obtain a fresh start authorization when qualified; an offline timer or cached authorization SHALL not fabricate collection or analysis.

### AND-SAL-007 detailed contract

The channel review SHALL show analyte label, qualifier/value with units, collection and analysis times, source, sample identity, basis, correction status, limits, quality, and an expandable original-report summary. It SHALL state what was measured without deriving intoxication, metabolic rate, blood concentration, or a driving decision. Both mobile platforms SHALL use the canonical measurement/session contracts and the same unit/qualifier fixtures. Field and import errors SHALL remain actionable without exposing raw laboratory identifiers in logs. Verification SHALL include all six qualifiers, unknown basis, double-dilution prevention, pg/mL conversion, sample mismatch, expired supplies, offline pending analysis, and forged source claims; actual assay-performance validation SHALL remain a separate required evidence gate.

This release SHALL retain null intoxication probability and reject research_estimate in live, imported, or cached results. Guest fictional chemistry and actual native practice MAY share a local mobile demo check with exact per-channel provenance; guest records SHALL never upload. Every check SHALL save locally before a separate explicitly authorized account Upload check action creates its queue entry.

## ADDED Requirements

### Requirement: AND-SAL-001 Saliva step and method availability

The Saliva screen SHALL explain that one identified collection can supply multiple analyte channels and SHALL show the selected mode, collection-method version, reader state, and available channels. The implementation SHALL also satisfy the AND-SAL-001 detailed contract above.

#### Scenario: Simulated sample workflow

- **GIVEN** explicit P0 mode
- **WHEN** the user selects Use simulated sample
- **THEN** the app SHALL create a labeled fictional sample and fictional analyte records, retain simulated source on all channels, and show the same validation/review UI used by the production adapters.

#### Scenario: Reader has no assay implementation

- **GIVEN** a connected Nano that only supplies telemetry
- **WHEN** the user opens Saliva
- **THEN** Read cartridge SHALL be unavailable with Assay not available, and the app SHALL permit only authorized sample-record or demonstration actions without implying chemical detection.

### Requirement: AND-SAL-002 Collection identity, fields, and timestamps

Before an actual sample is accepted, the app SHALL allocate sample_id and collection_attempt_id under the session and capture collection_method_id/version, collected_at, collection status, quality flags, and the selected method's volume/dilution fields. The implementation SHALL also satisfy the AND-SAL-002 detailed contract above.

#### Scenario: Buffered collector

- **GIVEN** a qualified collection method with recorded saliva and buffer quantities
- **WHEN** collection is accepted
- **THEN** the sample record SHALL retain those quantities, the defined dilution convention, method version, lot, and collection time for later comparison with each report's concentration basis.

#### Scenario: Invalid sample identity from device

- **GIVEN** a session expecting sample A
- **WHEN** a reader result identifies sample B or a different session
- **THEN** the import SHALL fail with identity mismatch and SHALL not silently relabel the reading or attach it to sample A.

#### Scenario: Companion evidence cannot be omitted

- **GIVEN** a saliva sample with buffer, lot, adequacy, and report lineage metadata beyond the v0.1 projection
- **WHEN** the check is saved and exported or explicitly uploaded
- **THEN** the full typed companion attempt and its digest SHALL accompany the selected projection; unknown v0.1 fields or an incomplete manifest SHALL fail validation.

### Requirement: AND-SAL-003 Quantities, original reports, and qualifiers

Each analyte measurement SHALL use one of THC, THC_COOH, or OH11_THC and preserve its measurement/sample IDs, method, source, calibration, instrument, lot, collected/measured times, quality, and original report. The implementation SHALL also satisfy the AND-SAL-003 detailed contract above.

#### Scenario: Below quantification without detection assertion

- **GIVEN** a laboratory report stating BLQ at an LOQ of 0.1 ng/mL
- **WHEN** the report is imported and viewed
- **THEN** the canonical value SHALL remain null, the display SHALL say Below quantification with the limit and original qualifier, and SHALL not say Detected or 0 ng/mL.

#### Scenario: Upper limit is not an exact result

- **GIVEN** an above-range report with a validated upper bound
- **WHEN** the user reviews the channel
- **THEN** the app SHALL display Above range and the bound, preserve null quantitative value, and SHALL not clip the reading to that bound for model or chart use.

### Requirement: AND-SAL-004 Units, analyte basis, and dilution discipline

The import adapter SHALL preserve original_report.value, unit, and qualifier. The implementation SHALL also satisfy the AND-SAL-004 detailed contract above.

#### Scenario: Laboratory already corrected dilution

- **GIVEN** a result of 75 pg/mL reported for neat oral fluid with laboratory_corrected status
- **WHEN** the app imports it from a buffered sample
- **THEN** it SHALL store 0.075 ng/mL, retain the original 75 pg/mL and correction status, and SHALL not apply the collection dilution factor again.

#### Scenario: Unspecified assay basis

- **GIVEN** a report that does not specify free or hydrolyzed analyte
- **WHEN** it is retained for review
- **THEN** assay_basis SHALL remain unspecified, the app SHALL expose the unresolved basis, and no compatible-model claim SHALL be made from separate allowed-method and allowed-basis lists alone.

### Requirement: AND-SAL-005 Analytical bounds, provenance, and role control

Semantic validation SHALL reject nonfinite quantities, contradictory LOD/LOQ/upper-limit ordering, quantified values outside the declared quantification interval, negative volumes, impossible timestamp ordering, and mismatched sample lineage. The implementation SHALL also satisfy the AND-SAL-005 detailed contract above.

#### Scenario: Quantified value outside interval

- **GIVEN** a reported value below its method's LOQ but labeled quantified
- **WHEN** validation runs
- **THEN** the app and server SHALL reject the inconsistent quantitative record with a field-specific reason and SHALL not coerce it to a valid reading.

#### Scenario: Forged validated source

- **GIVEN** a synthetic device or a manually edited local payload
- **WHEN** it claims validated_sensor with an unknown calibration ID
- **THEN** the claim SHALL not pass provenance validation, and no qualified concentration or research estimate SHALL result.

### Requirement: AND-SAL-006 Adequacy failures, retry, and delayed analysis

The saliva workflow SHALL distinguish inadequate volume, contamination, overflow, expired supply, unreadable cartridge, failed control, incompatible calibration, reader disconnect, analysis pending, and above-range report. The implementation SHALL also satisfy the AND-SAL-006 detailed contract above.

#### Scenario: Assay disconnect

- **GIVEN** a cartridge read in progress
- **WHEN** the reader disconnects before a verified completion payload
- **THEN** the app SHALL show Read interrupted, preserve the identified sample and failed analytical attempt, and offer only method-permitted recovery without treating progress as a concentration.

#### Scenario: Corrected laboratory report

- **GIVEN** a previously finalized analyte measurement
- **WHEN** an authorized corrected report is accepted
- **THEN** the system SHALL preserve the original immutable record, create a linked correction, and make any reanalysis a separately identified result rather than changing past evidence silently.

#### Scenario: Replacing a finalized sample is a new check

- **GIVEN** a finalized invalid check with an inadequate specimen and earlier physical task evidence
- **WHEN** the user chooses to collect another sample
- **THEN** Start replacement check SHALL allocate a new session/target and require new physical acquisitions without overwriting the original or reusing its task.

### Requirement: AND-SAL-007 Review display, API mapping, and platform evidence

The channel review SHALL show analyte label, qualifier/value with units, collection and analysis times, source, sample identity, basis, correction status, limits, quality, and an expandable original-report summary. The implementation SHALL also satisfy the AND-SAL-007 detailed contract above.

#### Scenario: Metabolite panel partly unavailable

- **GIVEN** a quantified THC result and two unrun metabolite channels
- **WHEN** the panel is displayed
- **THEN** it SHALL show the THC value with provenance and Not measured for each other channel; absence of 11-OH-THC measurement SHALL not be described as evidence of sobriety.

#### Scenario: Same report on Android and iOS

- **GIVEN** the same permitted laboratory report and sample metadata
- **WHEN** either platform normalizes and renders it
- **THEN** both SHALL preserve identical numeric meaning, qualifiers, original-report evidence, basis, and lineage, subject only to locale-specific display formatting.
