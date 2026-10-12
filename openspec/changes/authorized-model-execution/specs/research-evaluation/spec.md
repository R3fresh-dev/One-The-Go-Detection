## ADDED Requirements

### Requirement: EVAL-001 Frozen leakage-resistant partitions
The research tooling SHALL bind an exact dataset, participant-held-out
confirmatory partition, later-session partition and prespecified analysis plan
before evaluation; preprocessing and fitting SHALL use only training rows.

#### Scenario: Reproducible fitting
- **WHEN** the same bounded data and frozen plans are supplied
- **THEN** the tooling emits reproducible finite artifact bytes and exact dataset and plan digests

#### Scenario: Participant or partition leakage
- **WHEN** a held-out participant enters fitting or a later session crosses its frozen partition boundary
- **THEN** the tooling refuses the evaluation rather than reporting performance

### Requirement: EVAL-002 Complete matched evaluation and ablations
The research tooling SHALL report invalid and abstaining rows, sensitivity and
specificity with prespecified confidence intervals, Brier score and calibration
error on the frozen held-out and later-session partitions. Four ablations SHALL
use identical confirmatory rows.

#### Scenario: Full report
- **WHEN** evaluation runs on supplied qualified data
- **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators

#### Scenario: Omitted or changed rows
- **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking
- **THEN** the tooling refuses to attest a valid evaluation report

#### Scenario: Engineering fixtures
- **WHEN** automated tests use fictional cohort rows
- **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment

### Requirement: EVAL-003 Explicit information cutoffs
The tooling SHALL preserve the original target, capture completion and information
cutoff in that order. Profile observations and availability SHALL precede the
target. Same-check observations SHALL precede capture completion and availability
SHALL precede the information cutoff. Frozen maximum acquisition span and delivery
delay SHALL bound these intervals, including invalid rows.

#### Scenario: Same-check acquisition
- **WHEN** a chemical or task observation follows the target but falls within the frozen capture and information cutoffs
- **THEN** it remains eligible without changing the original target or partition

#### Scenario: Future information
- **WHEN** a profile predictor follows the target, a same-check observation follows capture completion, availability follows its cutoff, or an interval exceeds its frozen bound
- **THEN** the tooling rejects the dataset, including when that row is marked invalid

### Requirement: EVAL-004 Prespecified subgroup accounting
The tooling SHALL freeze categories for route, use frequency, co-use, device,
baseline and population. Every category SHALL appear for each ablation and
evaluation cohort with session identities, complete denominators and invalid and
abstained counts. Unsupported estimates SHALL remain null with explicit reasons.

#### Scenario: Reconciled categories
- **WHEN** evaluation completes
- **THEN** category session identities and counts reconcile to their cohort aggregate independently for each of the six dimensions

#### Scenario: Sparse or omitted categories
- **WHEN** a frozen category is empty, contains one endpoint class or too few participants
- **THEN** counts remain visible and unsupported rates and intervals remain null

#### Scenario: Unplanned category
- **WHEN** a row omits a dimension or introduces a category outside the frozen plan
- **THEN** admission fails before fitting or evaluation

### Requirement: EVAL-005 Qualified predictive values
The tooling SHALL report PPV and NPV with classified-positive and
classified-negative denominators, observed cohort prevalence, decision coverage
and participant-cluster intervals. It SHALL label these values conditional on
classification and observed cohort prevalence, without asserting target-population
predictive values from restricted or case-control cohorts.

#### Scenario: Unclassified checks
- **WHEN** checks abstain or fail quality admission
- **THEN** they remain in full-row accounting without receiving invented classifications or entering classified predictive-value denominators

#### Scenario: Undefined predictive value
- **WHEN** no positive or negative classifications exist or too few bootstrap draws define a statistic
- **THEN** the affected statistic or interval is null and its denominator and effective draw count remain visible

#### Scenario: Defined predictive values
- **WHEN** both classified denominators and sufficient participant-cluster draws exist
- **THEN** PPV and NPV equal their respective correct classifications divided by classified denominators, with qualified intervals and observed prevalence

### Requirement: EVAL-006 Custody and pipeline locks
The tooling SHALL bind exact dataset, plan, split, four artifact and evaluation
bytes. Dataset custody lock SHALL precede fitting, fitting SHALL precede the
post-fit pipeline lock, and that lock SHALL precede evaluation. Later-session
evaluation SHALL reuse the same frozen models and policies without retraining.

#### Scenario: Server-compatible evidence
- **WHEN** fitting follows dataset custody lock and evaluation follows the post-fit pipeline lock
- **THEN** the engine report carries the post-fit lock and admits the exact trained-artifact chronology

#### Scenario: Altered or premature evidence
- **WHEN** an artifact or denominator changes, evaluation precedes the pipeline lock, or the report substitutes the earlier custody lock for the pipeline lock
- **THEN** reproduction or server admission rejects the evidence

### Requirement: EVAL-007 Independent research evidence
The tooling SHALL distinguish verified byte, calculation and partition checks from
unverified authorization, independent assessment and historical custody assertions.
Scientific approval SHALL require independently controlled plan locks, custody
records, endpoint evidence and cohort qualification reviewed outside this tool.

#### Scenario: Supplied historical assertions
- **WHEN** a dataset names an authorization, independent assessor or historical lock
- **THEN** output retains those references and labels their authenticity unverified rather than treating JSON assertions as approval

#### Scenario: Self-approved model
- **WHEN** tooling output is supplied as authority without independently released study, model, calibration and qualification records
- **THEN** runtime admission refuses an estimate despite internally consistent artifact and report bytes

### Requirement: EVAL-008 Bounded file custody
CLI inputs SHALL be bounded regular files opened without following symlinks or
blocking on special files. Each read SHALL validate a stable descriptor snapshot
before parsing or hashing. Inputs SHALL be at most 16 MiB and datasets SHALL contain
at most 2,000 sessions and 1,000 participants. Unsupported or changing inputs SHALL
fail without fitting or evaluation.

#### Scenario: Stable regular input
- **WHEN** a bounded regular file has unchanged identity, size and metadata throughout reading
- **THEN** its exact bytes are parsed and hashed for reproducible evidence

#### Scenario: Unsafe or changing input
- **WHEN** an input is a symlink, FIFO, oversized file or changes during its descriptor read
- **THEN** the CLI refuses it without blocking indefinitely or producing an evaluation
