# OTGD-041 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/qualified-participant-acquisition/specs/research-evaluation/spec.md`; SHA256 `f4bef2eee7577e8f57b7cd27b7463d3879dcb1d452c73540d8916f9d6bf41726`.

5 cases, 1 requirements: PARTIAL 2, PASS 3. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-041-EVAL-002-01 — PASS

Full report — - **WHEN** the existing evaluation mode runs on supplied qualified data - **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators

Current proof: Deterministic train-only pipeline emits all four variants, matched8-row confirmatory denominators including invalid/abstained and exact dataset/split/analysis/artifact/report hashes; fictional software evidence only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 7059b2460412feac3fa11094d2b8a16dc5eaa6958d1cad837b14264ce9968d95. Actual current source and raw evidence supply this disposition.

## OTGD-041-EVAL-002-02 — PARTIAL

Omitted or changed rows — - **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking - **THEN** the tooling refuses to attest a valid evaluation report

Current proof: Changed locked threshold/dataset/training receipt and corrupted output refuse; positive four-variant rows retain invalid/abstained denominators.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_cli_private_canonical_pipeline_and_full_reproduction_detect_corruption` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 372; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- explicit removal of invalid/abstaining output rows or different submitted ablation row membership is refused: negative report row-removal mutations are not directly asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 045b9442ba30fe415ede25dd7ea512c1f00779b4740c44df006923531dd7d079. Actual current source and raw evidence supply this disposition.

## OTGD-041-EVAL-002-03 — PARTIAL

Engineering fixtures — - **WHEN** automated tests use fictional cohort rows - **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment

Current proof: CLI artifacts/evidence retain engineering_synthetic, status unvalidated, authority/clinical/history flags false; strict forged approval and rehashed false authority evidence refuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_self_asserted_or_extra_approval_fields_do_not_authenticate_history` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 205; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 137; 20 current observation(s).
- `deploy/platform.py::main` — file SHA `6d157097dac3cb938377fe56cb2cc9c66aa2a41fbf5e32ab1550ff0ce9157a6f`, line 310; 0 current observation(s).
- `infra/local/bootstrap_resources.py::initialize` — file SHA `fb2eb230c8b9cc6609e93c5373297ed5c2a8d33aef17d1babd3f21b65ce52751`, line 15; 0 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- CLI outputs are explicitly engineering_synthetic/unvalidated with authority flags false. Reviewed deployment maintenance dispatch invokes resource bootstrap, migration and recovery admission, not a study/model fixture seed. No executed negative attempts to admit the exact generated engineering artifact as a human-approved deployed model were located; factual absence of a configured real study is not scientific approval.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5de8829f414b5bd6c0515d9a8fcf65de390ba5d3dc8bf188f77236b0979635c0. Actual current source and raw evidence supply this disposition.

## OTGD-041-EVAL-002-04 — PASS

Explicit restricted HR-only report — - **GIVEN** a prespecified locked server-interval policy with exactly the approved HR predictor and independently bound current/baseline evidence - **WHEN** the separate HR-only mode completes evaluation - **THEN** its strict report names `cardiac_hr_only`, reconciles every cohort/stratum and invalid/abstained row, and retains frozen dataset/split/analysis/artifact digests - **AND** chemical/app/ECG ablation comparisons are explicitly outside that mode and no multimodal superiority claim is emitted

Current proof: Separate cardiac_hr_only report/artifact,32-row custody manifest, held-out/later8-row accounting, no paired multimodal comparisons, exact frozen digests and false external authority are asserted across4variants. Full and cardiac-cohort tests call same reviewed helper. It binds original artifact/data/plan/split hashes and all six dimensions/partitions/variants, explicit one-class null statistics and singleton-versus2participant cluster support. Actual four-variant HR-only train/evaluate pipeline retains exact invalid/abstained identities and all six strata for both held-out partitions, totals8/invalid1/valid7/abstained7; original dataset/plan/split/artifact hashes, explicit cardiac_hr_only and no multimodal/approval claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_invalid_custody_or_faults_remain_in_all_row_denominators` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 182; 440 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 137; 20 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_sparse_one_class_and_participant_boundary_subgroups_preserve_all_rows` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 561; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::assert_sparse_subgroups_preserve_rows_and_unsupported_statistics` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 470; 0 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_sparse_one_class_and_participant_boundary_subgroups_preserve_all_rows` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 145; 20 current observation(s).
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/semantics/hr_strata_probe.py::actual_train_evaluate_four_HR_variants_all48_strata` — file SHA `4adbf7575d8031de164f6e5a6cc09309de766c5924a3f2969f92bb17d2180c03`, line 1; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/semantics/hr-strata-results.json` — SHA256 `de0990f31646c35aab2fcead7d28574ff2fd38da095d9c2021503b2bb3306bac`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Reviewed helper uses valid/fully classified sparse fixture; combine meaningful existing invalid/abstain accounting assertions carefully, never infer scientific subgroup validity. Helper body has no independent execution; callers carry actual executions. Fictional software fixtures; no installed OS, physical stop, real participant consent, assay qualification or clinical/model approval. Supplemental probes do not replace full local/CI gates.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 55ae39dbd5d47b03bc2954d288b89d19fadd516a68294e6ec900010f4a8073b1. Actual current source and raw evidence supply this disposition.

## OTGD-041-EVAL-002-05 — PASS

Implicit or mismatching reduced report — - **GIVEN** an absent or mismatching HR-only policy, a legacy model, extra predictors or incomplete row accounting - **WHEN** a single-variant report is submitted for model admission - **THEN** the service refuses it - **AND** the caller cannot use the new mode to omit required comparisons from the existing mode

Current proof: Wrong report scope, fake chemistry comparisons, missing evidence, wrong policy or denominator refuse; mixed HR features and unprespecified legacy evidence refuse; legacy still requires four variants.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_hr_report_cannot_claim_unmeasured_chemical_or_ecg_comparisons` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 363; 25 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_hr_scope_rejects_mixed_rows_and_unprespecified_legacy_evidence` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 302; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_legacy_absent_optional_fields_do_not_change_dataset_or_plan_bytes` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 315; 5 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_required_channel_scope_is_heart_rate_only` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 145; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c6af4d8674ff6f191faecfa5fac2ea24c43df5e0d0f0a131157349179d03b248. Actual current source and raw evidence supply this disposition.

