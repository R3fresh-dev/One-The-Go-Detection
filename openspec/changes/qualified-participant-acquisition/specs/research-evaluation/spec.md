## MODIFIED Requirements

### Requirement: EVAL-002 Complete matched evaluation and ablations
The research tooling SHALL report invalid/abstaining rows, sensitivity/specificity with prespecified intervals, Brier score and calibration error on frozen held-out/later-session partitions. The existing mode SHALL retain four ablations with identical confirmatory rows. Only an explicit frozen HR-only interval policy SHALL select the separate `cardiac_hr_only` report/artifact variant, retain complete accounting, and disclose absent comparisons without inventing their results.

#### Scenario: Full report
- **WHEN** the existing evaluation mode runs on supplied qualified data
- **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators

#### Scenario: Omitted or changed rows
- **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking
- **THEN** the tooling refuses to attest a valid evaluation report

#### Scenario: Engineering fixtures
- **WHEN** automated tests use fictional cohort rows
- **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment

#### Scenario: Explicit restricted HR-only report
- **GIVEN** a prespecified locked server-interval policy with exactly the approved HR predictor and independently bound current/baseline evidence
- **WHEN** the separate HR-only mode completes evaluation
- **THEN** its strict report names `cardiac_hr_only`, reconciles every cohort/stratum and invalid/abstained row, and retains frozen dataset/split/analysis/artifact digests
- **AND** chemical/app/ECG ablation comparisons are explicitly outside that mode and no multimodal superiority claim is emitted

#### Scenario: Implicit or mismatching reduced report
- **GIVEN** an absent or mismatching HR-only policy, a legacy model, extra predictors or incomplete row accounting
- **WHEN** a single-variant report is submitted for model admission
- **THEN** the service refuses it
- **AND** the caller cannot use the new mode to omit required comparisons from the existing mode
