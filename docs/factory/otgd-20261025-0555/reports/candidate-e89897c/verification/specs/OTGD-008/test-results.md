# OTGD-008 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md`; SHA256 `1307ac2ebe390b58619b599669a9c52773104dded84661be708aa132d95f8626`.

19 cases, 8 requirements: PARTIAL 6, PASS 13. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-008-EVAL-001-01 — PASS

Reproducible fitting — - **WHEN** the same bounded data and frozen plans are supplied - **THEN** the tooling emits reproducible finite artifact bytes and exact dataset and plan digests

Current proof: Actual repeated fitting compares complete canonical artifacts/training/report/evidence; strict Artifact validates numeric shape. Full CLI helper snapshots and compares original dataset/analysis/split/training/report/artifact digests and all evidence. Current named full/HR executions pass. Software reproducibility only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a294521182fcb03b803b5d3f739f93a8e4ca42f3c3c1a5192a76b85ad9022dce. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-001-02 — PARTIAL

Participant or partition leakage — - **WHEN** a held-out participant enters fitting or a later session crosses its frozen partition boundary - **THEN** the tooling refuses the evaluation rather than reporting performance

Current proof: Frozen split identities are disjoint; altered split is rejected by evaluation; missing earlier held-out session and single-class whole cohorts refuse. Current named tests pass.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_frozen_participant_and_temporal_partitions_reproduce_without_outcomes` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 209; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 361; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Exact conjunction: direct train invocation with held-out participant inserted into fit and a later-session row reassigned across an already frozen partition is not explicitly asserted; evaluation-tamper rejection is narrower than refusal before fitting.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d01262c3f2b7ee8892bac2a25e69d317a3370712137f07a4dc149ab3f2a09439. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-002-01 — PASS

Full report — - **WHEN** evaluation runs on supplied qualified data - **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators

Current proof: Same full-mode pipeline supplies all4 artifacts/ablations, exact dataset/split/analysis/artifact hashes and matched8-session denominators, including invalid/abstained cases; actual current named tests compare those fields. This verifies software report accounting on fictional data, not scientific qualification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA d413327392ebc836172bf2224ec5221bbb11013b7c091a015bc7a37578378381. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-002-02 — PARTIAL

Omitted or changed rows — - **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking - **THEN** the tooling refuses to attest a valid evaluation report

Current proof: Positive invalid/abstain inclusion and matched rows asserted; registry rejects altered denominator/missing ablation/threshold and evaluator rejects altered split/training receipt/weights/chronology.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).
- `services/api/tests/test_model_engine.py::test_training_evaluation_policy_and_result_proof_are_bound` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 437; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Exact negative manipulation of an invalid/abstaining row removed from a frozen evaluation or row identities differing for only one ablation is not directly asserted; current denominator/missing-ablation negatives do not establish those exact row-subset cases.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 12ced89779f1719c0b99d07467983fbe35f02662589752bad6dff05eb5c5436d. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-002-03 — PARTIAL

Engineering fixtures — - **WHEN** automated tests use fictional cohort rows - **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment

Current proof: Fictional data_kind and authority/clinical-success false are asserted in actual CLI artifacts and evidence; typed/untyped forged approval flags refuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_self_asserted_or_extra_approval_fields_do_not_authenticate_history` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 205; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Deployment/runtime attempt using exactly those generated engineering artifacts as a human model is not part of these output assertions. Bind a direct current runtime/deployment refusal case, not actual scientific qualification.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f96787a5c497e0bb5293e855c1ac8fcd3280b81b074189b778debeaa1dbec9f6. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-003-01 — PARTIAL

Same-check acquisition — - **WHEN** a chemical or task observation follows the target but falls within the frozen capture and information cutoffs - **THEN** it remains eligible without changing the original target or partition

Current proof: Same-check observations at target+10s/task capture and availability at cutoff are accepted; original confirmatory target times retained, and shorter span/delivery limits refuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_same_check_observations_and_later_assay_delivery_preserve_original_target` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 319; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- The original frozen partition identity and every output variant/later-session target are not explicitly compared after this timing change; source positive target assertion is narrower than full unchanged-target/partition conjunction.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e43f96312dafef62f84cb7930ad2bbdea69169bcd4ebaf42a3f63c30f07e4559. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-003-02 — PASS

Future information — - **WHEN** a profile predictor follows the target, a same-check observation follows capture completion, availability follows its cutoff, or an interval exceeds its frozen bound - **THEN** the tooling rejects the dataset, including when that row is marked invalid

Current proof: 11 source/timing/typed corruptions reject while row valid; separate invalid-training case proves retained invalid rows. Current test parametrizes valid/invalid acquisition status with existing11corruptions; clean row first admitted, then source timing/type corruption rejects.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_invalid_or_future_source_data_are_rejected_before_fitting` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 297; 110 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_invalid_training_rows_are_shared_by_every_ablation_and_constant_scaling_is_train_only` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 281; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current exact-source unit and complete PostgreSQL suites execute the22 corruption variants; scientific chronology/endpoint validity is independent.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b68d02d4a2b00caaff04e30422aaeb7d6e6f950c86f738113065d4d81d288d9a. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-004-01 — PASS

Reconciled categories — - **WHEN** evaluation completes - **THEN** category session identities and counts reconcile to their cohort aggregate independently for each of the six dimensions

Current proof: Each of six STRATA dimensions explicitly compares category set/session identities/count totals to its partition for each variant; current named test passes. This closes row reconciliation only, not scientific generalization.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f279888c97573e73de40b42d52c8037525386d217584ae206c963c735cea9344. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-004-02 — PASS

Sparse or omitted categories — - **WHEN** a frozen category is empty, contains one endpoint class or too few participants - **THEN** counts remain visible and unsupported rates and intervals remain null

Current proof: Related source assertions and named observations only; full canonical GIVEN/WHEN/THEN linkage is not established by these related checks. Full and cardiac-cohort tests call same reviewed helper. It binds original artifact/data/plan/split hashes and all six dimensions/partitions/variants, explicit one-class null statistics and singleton-versus2participant cluster support.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_sparse_one_class_and_participant_boundary_subgroups_preserve_all_rows` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 561; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::assert_sparse_subgroups_preserve_rows_and_unsupported_statistics` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 470; 0 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_sparse_one_class_and_participant_boundary_subgroups_preserve_all_rows` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 145; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Reviewed helper uses valid/fully classified sparse fixture; combine meaningful existing invalid/abstain accounting assertions carefully, never infer scientific subgroup validity. Helper body has no independent execution; callers carry actual executions.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1753e237c4b7f60799fea848264babc22ededc638ef1f1cb9599221fafd5b0ed. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-004-03 — PARTIAL

Unplanned category — - **WHEN** a row omits a dimension or introduces a category outside the frozen plan - **THEN** admission fails before fitting or evaluation

Current proof: An unprespecified route category causes evaluated evidence refusal in changed-plan test.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- A missing stratum dimension and refusal before both fitting/evaluation for that malformed row are not directly asserted; unknown-category evaluation refusal does not close all named admissions.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f165ade748aac59aa9bb1dea3684417de51df26a017eebcfd55aa4c74a292ef6. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-005-01 — PASS

Unclassified checks — - **WHEN** checks abstain or fail quality admission - **THEN** they remain in full-row accounting without receiving invented classifications or entering classified predictive-value denominators

Current proof: All-abstain+one-censored fixture retains8 rows for every ablation; true positive/negative denominators remain4/4; invalid output probability/classification null;7 valid rows counted abstained and decision coverage0/PPV/NPV null. No unclassified row silently enters a classified denominator. Fictional software accounting only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3c766618fda3b95447acc5b5e031e9e50b7a8c984b357a7508287f5a2e45bf69. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-005-02 — PASS

Undefined predictive value — - **WHEN** no positive or negative classifications exist or too few bootstrap draws define a statistic - **THEN** the affected statistic or interval is null and its denominator and effective draw count remain visible

Current proof: Related source assertions and named observations only; full canonical GIVEN/WHEN/THEN linkage is not established by these related checks. Actual fixed-seed bootstrap with prespecified minimum150 yields149/163 or150/146; exact classified denominators/effective draws/nullunsupported intervals, prevalence and coverage asserted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_predictive_intervals_require_frozen_minimum_defined_cluster_draws` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 567; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Engineering statistics only; no frozen threshold change or scientific qualification.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9339e03e036151c8a6987b8eff2de3527e66feec7791c0d8b050430ee296b56b. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-005-03 — PASS

Defined predictive values — - **WHEN** both classified denominators and sufficient participant-cluster draws exist - **THEN** PPV and NPV equal their respective correct classifications divided by classified denominators, with qualified intervals and observed prevalence

Current proof: Balanced fully classified fixture explicitly asserts observed prevalence0.5, coverage1, PPV=NPV=1 and both intervals[1,1], qualified as not target-population; named current executions pass. This is bounded software-statistic evidence, not predictive validity/generalization.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 6a68d925f5b01809779d42b7bbcb420936bbc67a2c4263ac21f01d33c1ba7700. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-006-01 — PASS

Server-compatible evidence — - **WHEN** fitting follows dataset custody lock and evaluation follows the post-fit pipeline lock - **THEN** the engine report carries the post-fit lock and admits the exact trained-artifact chronology

Current proof: Real toolkit report chronologies are generated after fit/post-fit lock; actual server chronology guard admits these bytes before mocked execution and refuses substituted earlier custody lock. CLI source/hash evidence retains exact trained-artifact chronology. Auth/storage/execute are unit doubles for this chronology-only boundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_actual_toolkit_artifact_and_postfit_lock_pass_server_chronology_guard` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 621; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 839a393f76715439c950ac8f6ec27ea7222fa48c5c49cc405d811b71563c5628. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-006-02 — PASS

Altered or premature evidence — - **WHEN** an artifact or denominator changes, evaluation precedes the pipeline lock, or the report substitutes the earlier custody lock for the pipeline lock - **THEN** reproduction or server admission rejects the evidence

Current proof: Explicit artifact weights, receipt/denominator, threshold, split, version, data and premature train/evaluation/pipeline-lock substitutions reject; actual server guard rejects custody lock substituted for post-fit lock; CLI altered report fails reproduction. Current named software checks pass.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_actual_toolkit_artifact_and_postfit_lock_pass_server_chronology_guard` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 621; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_cli_private_canonical_pipeline_and_full_reproduction_detect_corruption` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 372; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 710f3820efafbba94448d403f61e7bb7d1f6aa1da5fd1cda872cc9ba78011fa9. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-007-01 — PASS

Supplied historical assertions — - **WHEN** a dataset names an authorization, independent assessor or historical lock - **THEN** output retains those references and labels their authenticity unverified rather than treating JSON assertions as approval

Current proof: Exact caller references retained in complete reproduced CLI evidence and full/HR custody; authenticity/history/authority flags false at emitted contract locations, all current named parameter cases pass. This is software handling of unverified references, not genuine external approval.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 137; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 25bed1cfbf594df2be4d28b5ad2c5d9f9f307591d519406ed760ac1f79e3402f. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-007-02 — PARTIAL

Self-approved model — - **WHEN** tooling output is supplied as authority without independently released study, model, calibration and qualification records - **THEN** runtime admission refuses an estimate despite internally consistent artifact and report bytes

Current proof: CLI output authority flags false and extra/rehashed assertions rejected; registry self-review/self-release fail independently; current authority/qualification/calibration revocation returns no score.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_self_asserted_or_extra_approval_fields_do_not_authenticate_history` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 205; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_immutable_submission_three_principals_lifecycle_history_and_revision` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 192; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- No direct exact run presents the actual generated internally consistent toolkit artifact/report with all independent registry approvals absent and asserts runtime refusal. Existing revocation/self-approval tests use other contexts; do not infer genuine approval from tooling.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 82151bd23cdb60fb01c86789c7dc86ab6989f7d362062cd31b2761925f5e3c18. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-008-01 — PASS

Stable regular input — - **WHEN** a bounded regular file has unchanged identity, size and metadata throughout reading - **THEN** its exact bytes are parsed and hashed for reproducible evidence

Current proof: Actual opened regular-file loader performs bounded read and parses exact object; full CLI reproduction compares loaded input objects and expected canonical dataset/plan/training/artifact hashes. Unchanged regular input identity is the tested positive path. No mutation refusal implied.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_input_snapshot_uses_bounded_read_and_rejects_nonregular_files` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 406; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 896b140893e86e30ca577d2208ad798ee3e7b0850bd176ba91271c5782947f3d. Actual current source and raw evidence supply this disposition.

## OTGD-008-EVAL-008-02 — PASS

Unsafe or changing input — - **WHEN** an input is a symlink, FIFO, oversized file or changes during its descriptor read - **THEN** the CLI refuses it without blocking indefinitely or producing an evaluation

Current proof: Related source assertions and named observations only; full canonical GIVEN/WHEN/THEN linkage is not established by these related checks. Actual opened inode is mutated after real bounded read/before secondfstat; both same-size+mtime and size change refuse training/output; adjacent stable samefile read admits exact bytes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_input_snapshot_uses_bounded_read_and_rejects_nonregular_files` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 406; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_json_ingestion_is_bounded_duplicate_safe_and_data_only` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 397; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_descriptor_change_during_actual_bounded_read_refuses_training_without_output` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 422; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Software file custody only; no study/model approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a655c84fafa03a40f8b59c2414a535c90a75309562a0276e8030702ba790d36a. Actual current source and raw evidence supply this disposition.

