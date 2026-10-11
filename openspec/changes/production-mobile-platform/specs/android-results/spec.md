# Android feature: result interpretation

Normative integration: [shared application contracts](../../shared-contracts.md) and [platform contracts](../../platform-contract.md). These define the exact cross-feature DTOs, error states, generation/revocation rules, current-release limits, and implementation evidence.

## Purpose and traceability

Give the customer an understandable completion record without confusing successful collection with an impairment estimate. Upstream: PRD-003–007/019/020; APP-012/013; MOD-008–013; HLD §§3/5/7; LLD §§7/11; contracts/result.schema.json.

## Customer experience

The review screen shows the collection time, selected sample, each component's source/quality, and any missing steps. Its primary action is **Save on this device**. Once locally frozen, the customer sees **Check saved** with the result-state title and a separate synchronization status. A server request in progress shows **Analysis pending**, never a simulated completed result. The results header contains the check's local date/time, an explicit **Demo** badge when applicable, and **Measurement record** for a measurement-only outcome.

The main card's supported titles are **Measurements saved**, **Result unavailable**, **Check needs attention**, ; `research_estimate` is an unsupported current-release state and never displays a probability. Supporting copy identifies the actual reason: e.g. **No validated impairment model is available for this check**. Component cards show an analyte value only when quantified, the original qualifier/limit when censored, and **Not measured** when absent. Unit labels are always adjacent. Heart and reaction features retain their measurement units. An **About this result** disclosure explains source, target/evaluation times, configuration versions, and the applicable endpoint when one actually exists.

Actions are **View measurements**, **Back to Home**, and **Upload check** only if account/study authorization permits. Before finalization, retry creates a linked attempt. After local or server finalization, **Start replacement check** creates a new session UUID and target time with supersedes_session_id, carrying no earlier physical acquisitions. The original remains immutable. Research inference requires a separate reviewed software release; no configuration can enable it here. A local percentage animation, progress ring, or color must not imply an intoxication level.

## Engineering contract

Use the existing result-state vocabulary measurement_only/research_estimate/inconclusive/invalid. Local pending/queued/sync_failed are delivery states stored separately. A result references one session and input SHA-256. The result's target_at is the frozen session target time established by Start check; component acquisition times are shown separately, and evaluated_at is analysis completion. Render a delayed result as **Recorded at …; analyzed at …**. Do not interpret a new HTTP receipt time as a new physiological assessment. Snapshot records and derived result IDs are immutable; a new result may replace another only through an explicit replaces_result_id relationship.

The app validates the response against result.schema.json and verifies session ID and expected input hash before displaying it. JSON shape is insufficient authority for a clinical result: the service must enforce current study/protocol, model lifecycle, compatible inputs, provenance, and an approved endpoint. This implementation fixes inference_available=false, has no executable impairment model, and returns null probability. A schema-valid research_estimate is rejected in live results, cache, history, and export with UNSUPPORTED_RESEARCH_RESULT. Invalid responses produce **We could not verify this result** and a retryable transport error; never repair an illegal score by clamping it into range.

Android and iOS use the same state mapping and copy. Announce completion once through accessibility APIs. Avoid red/green-only meaning and do not label low chemical values as a pass. Account logout clears the visible result. Offline results remain accessible only inside the proper unlocked encrypted account/demo namespace.

## ADDED Requirements

### Requirement: AND-RES-001 Separate capture outcome from delivery status
The app SHALL render the scientific result state independently of local save, queue, and server delivery state.

#### Scenario: Completed offline measurement check
- **GIVEN** a locally finalized check with no server result
- **WHEN** the result screen opens
- **THEN** it shows the local measurement record and **Not synced**, with no claim that cloud analysis finished.

#### Scenario: Pending server computation
- **GIVEN** GET result returns HTTP 202
- **WHEN** polling completes that request
- **THEN** the app keeps **Analysis pending** and offers navigation without inventing a terminal result.

### Requirement: AND-RES-002 Enforce result contract and linkage
The client and service MUST reject a probability outside [0,1], any nonfinite field, and a result for a different session or input digest.

#### Scenario: Correctly linked measurement result
- **GIVEN** the expected session and frozen digest
- **WHEN** a schema-valid measurement_only response arrives with matching references
- **THEN** it is saved once and displayed for that check.

#### Scenario: Stale response after another check
- **GIVEN** a response references an earlier session
- **WHEN** the current check screen receives it
- **THEN** the response cannot replace the current check's result and the mismatch is recorded without raw health payloads.

### Requirement: AND-RES-003 Keep impairment inference closed
The service MUST keep inference_available=false and emit null probability/classification/threshold in this release. The app SHALL reject every research_estimate across live, cache, history, and export paths and SHALL contain no local impairment formula.

#### Scenario: Demo completes all steps
- **GIVEN** every simulated channel contains a plausible value
- **WHEN** the check is finalized
- **THEN** its result remains measurement_only with null probability and a demo badge.

#### Scenario: Client requests research by changing a field
- **GIVEN** an otherwise valid-shaped research_estimate or an operator record claiming an active model
- **WHEN** any current result path evaluates it
- **THEN** the service executes no model and the app rejects the unsupported estimate without displaying its probability.

### Requirement: AND-RES-004 Preserve qualifiers and missingness
Each measurement card SHALL preserve the reported analyte, unit, qualifier, source, and collection basis without substituting zero for missing or censored values.

#### Scenario: Below quantification
- **GIVEN** THC_COOH has qualifier below_loq and a stated LOQ
- **WHEN** its card renders
- **THEN** it shows below-quantification wording and the limit, with no exact numeric concentration or inferred detection claim.

#### Scenario: Unrun channel
- **GIVEN** OH11_THC is not_measured
- **WHEN** measurements are expanded
- **THEN** the app shows **Not measured**, not **Negative**.

### Requirement: AND-RES-005 Preserve historical time and immutability
The app SHALL display acquisition and evaluation times distinctly and MUST NOT update a saved result in place when reanalysis produces a new result ID.

#### Scenario: Delayed laboratory result
- **GIVEN** analysis finishes the following day
- **WHEN** the result arrives
- **THEN** the original collection date remains the check's date and the later analysis time is visible.

#### Scenario: Linked reanalysis
- **GIVEN** a permitted newer result replaces an earlier result
- **WHEN** history is opened
- **THEN** both result identities remain reconstructable and the current display identifies the newer result's version.

### Requirement: AND-RES-006 Provide actionable invalid and inconclusive states
The app SHALL map known reason codes to specific missing/recapture/support actions while preserving unknown codes as unavailable-result details.

#### Scenario: Interrupted reaction task
- **GIVEN** a required task is invalid due to backgrounding
- **WHEN** the completion summary opens
- **THEN** it names the interrupted task and, if already finalized, offers Start replacement check with a new UUID/time and no carried-forward physical acquisitions; the original result/hash remain unchanged.

#### Scenario: Unknown server reason
- **GIVEN** a newer service returns an unknown reason code
- **WHEN** the app displays the result
- **THEN** it shows a generic unavailable explanation and diagnostic request ID without silently treating the result as valid.

### Requirement: AND-RES-007 Use bounded and cancelable result polling
The client SHALL poll pending results with bounded backoff, stop on logout/screen disposal, and offer manual retry after the polling budget expires.

#### Scenario: Temporary server outage
- **GIVEN** the result endpoint returns 503
- **WHEN** automatic retries exhaust the configured budget
- **THEN** the record remains pending and a retry action appears; the local check is preserved.

#### Scenario: Account changes during polling
- **GIVEN** an outstanding result request for account A
- **WHEN** the app signs into account B
- **THEN** A's request is canceled or ignored and its result never enters B's visible state.
