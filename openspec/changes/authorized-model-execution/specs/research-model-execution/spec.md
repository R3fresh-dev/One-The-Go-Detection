## ADDED Requirements

### Requirement: MODEL-006 Independently qualified optical diameter
Optical model admission SHALL independently validate native evidence arithmetic,
the current exact camera configuration, a released optical geometry calibration
and a released qualified-measurement record. Geometry-only admission SHALL permit
only the eye baseline diameter feature. Physical-onset uncertainty SHALL remain
visible and SHALL block latency and constriction features.

#### Scenario: Qualified diameter-only model
- **WHEN** current independent geometry and acquisition approvals match the exact camera, sampled ROI, extractor and phone build, and the pinned model uses baseline diameter only
- **THEN** diameter may enter research execution while physical onset and response latency remain unqualified

#### Scenario: Geometry cannot qualify response timing
- **WHEN** a model requires eye latency or relative constriction, geometry is missing, the configuration is collection-only, or an additional quality failure exists
- **THEN** the geometry-only path refuses research execution

#### Scenario: Geometry approval withdrawn during computation
- **WHEN** the geometry release is retired or replaced before result commit
- **THEN** current authority is resolved again and the old computation cannot commit

### Requirement: MODEL-001 Approved immutable artifact admission
The system SHALL execute only bounded canonical JSON logistic_linear_v1 artifacts
with explicit finite otgd.features.v1 parameters and exact approved pinned bytes.

#### Scenario: Admitted artifact
- **WHEN** independently released authority names the exact version, length, SHA-256, feature contract and calibration
- **THEN** the worker loads only those bytes and executes bounded finite arithmetic

#### Scenario: Unsupported or changed artifact
- **WHEN** the artifact is executable, noncanonical, nonfinite, oversized, uses unknown features, has unstable scales or differs from its pinned hash
- **THEN** the worker returns a controlled refusal with no research probability

### Requirement: MODEL-002 Current participant and scientific authority
The system SHALL require the exact current study membership, consent document,
notice, independently reviewed model and policies, calibration, selected capture
configuration and evidence before execution and transactional commit.

#### Scenario: Authorized positive path
- **WHEN** all exact authority and acquisition dependencies are active and consistent for a controlled research participant
- **THEN** the worker may compute the approved endpoint within its stated population and protocol scope

#### Scenario: Revocation during computation
- **WHEN** a study, model, method, calibration, device binding or consent changes before commit
- **THEN** the result is refused or the operation fails without committing an estimate from stale authority

#### Scenario: Unqualified demonstration
- **WHEN** a guest, synthetic check, unapproved record or restored suspended study attempts inference
- **THEN** it receives no research estimate even if request fields claim approval

### Requirement: MODEL-003 Qualified acquisition and temporal features
The system SHALL enforce required valid nonsynthetic channels, exact method
tuples, population and provenance scope, finite limits, acquisition span,
delivery delay, clock uncertainty and profile timestamps before the target.

#### Scenario: Missing or censored required chemical feature
- **WHEN** a required analyte is missing, below quantification, incompatible or out of scope
- **THEN** the system preserves its qualifier and refuses inference without imputing zero

#### Scenario: Native timing qualification
- **WHEN** the phone model, OS, native build, input/presentation clocks, implementation and extractor match independently released timing qualification
- **THEN** the model uses its approved timing bias and uncertainty bound while retaining the unmodified native timing evidence

#### Scenario: Unqualified phone timing
- **WHEN** a simulator or unsupported timing tuple supplies native timestamps
- **THEN** the system records measurement evidence and refuses model eligibility

### Requirement: MODEL-004 Personal baseline ownership and age
The system SHALL permit a personalized baseline only when it is owned in the same
data generation and study/protocol, completed before the target, within the
explicit approved maximum age, and passes current acquisition qualification.

#### Scenario: Valid prior baseline
- **WHEN** the current and historical captures meet all owned evidence and scope checks
- **THEN** the model uses their approved feature differences and binds the exact baseline snapshot hash

#### Scenario: Foreign or stale baseline
- **WHEN** a baseline is foreign, retired, future, stale, incomplete or unqualified
- **THEN** the worker refuses personalized inference

### Requirement: MODEL-005 Abstention and authenticated research presentation
The system SHALL apply the frozen uncertainty policy before classification and
emit result 1.1 with exact snapshot and authority evidence. The client SHALL
validate scope, hashes, threshold, classification and null abstention behavior.

#### Scenario: Admitted research estimate
- **WHEN** a validated authenticated result is outside the abstention band
- **THEN** the interface shows the research endpoint, population, version, probability, threshold, limits and supplied measurement context

#### Scenario: Uncertainty abstention
- **WHEN** the probability lies within the frozen abstention band
- **THEN** the result and interface show inconclusive with null score, classification and threshold

#### Scenario: Relabeled or inconsistent proof
- **WHEN** model version, endpoint, population, authority digest, baseline, uncertainty policy or threshold classification is inconsistent
- **THEN** the client refuses the research display
