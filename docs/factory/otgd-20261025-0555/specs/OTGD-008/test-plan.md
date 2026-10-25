# OTGD-008: verification plan

Canonical: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md`; SHA-256 `1307ac2ebe390b58619b599669a9c52773104dded84661be708aa132d95f8626`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `services/api/tests/test_model_admission.py` — `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`
- `services/api/tests/test_model_engine.py` — `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`
- `services/api/tests/test_model_evaluation.py` — `60013323430a0979caeffcef4b2983566a028b0f50e75938df7f053c0498fdc0`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### EVAL-001 — Frozen leakage-resistant partitions

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-001-01 | Reproducible fitting — **WHEN** the same bounded data and frozen plans are supplied **THEN** the tooling emits reproducible finite artifact bytes and exact dataset and plan digests | `services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-001-02 | Participant or partition leakage — **WHEN** a held-out participant enters fitting or a later session crosses its frozen partition boundary **THEN** the tooling refuses the evaluation rather than reporting performance | `services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### EVAL-002 — Complete matched evaluation and ablations

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-002-01 | Full report — **WHEN** evaluation runs on supplied qualified data **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators | `services/api/tests/test_model_evaluation.py:255` — test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-002-02 | Omitted or changed rows — **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking **THEN** the tooling refuses to attest a valid evaluation report | `services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-002-03 | Engineering fixtures — **WHEN** automated tests use fictional cohort rows **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment | `services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_admission.py:396` — test_http_native_evidence_real_registry_lifecycle_worker_and_research_read | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### EVAL-003 — Explicit information cutoffs

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-003-01 | Same-check acquisition — **WHEN** a chemical or task observation follows the target but falls within the frozen capture and information cutoffs **THEN** it remains eligible without changing the original target or partition | `services/api/tests/test_model_evaluation.py:312` — test_same_check_observations_and_later_assay_delivery_preserve_original_target | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-003-02 | Future information — **WHEN** a profile predictor follows the target, a same-check observation follows capture completion, availability follows its cutoff, or an interval exceeds its frozen bound **THEN** the tooling rejects the dataset, including when that row is marked invalid | `services/api/tests/test_model_evaluation.py:312` — test_same_check_observations_and_later_assay_delivery_preserve_original_target | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### EVAL-004 — Prespecified subgroup accounting

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-004-01 | Reconciled categories — **WHEN** evaluation completes **THEN** category session identities and counts reconcile to their cohort aggregate independently for each of the six dimensions | `services/api/tests/test_model_evaluation.py:281` — test_invalid_training_rows_are_shared_by_every_ablation_and_constant_scaling_is_train_only | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-004-02 | Sparse or omitted categories — **WHEN** a frozen category is empty, contains one endpoint class or too few participants **THEN** counts remain visible and unsupported rates and intervals remain null | `services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_admission.py:567` — test_baseline_bounds_and_bias_are_applied_to_frozen_features | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-004-03 | Unplanned category — **WHEN** a row omits a dimension or introduces a category outside the frozen plan **THEN** admission fails before fitting or evaluation | `services/api/tests/test_model_evaluation.py:281` — test_invalid_training_rows_are_shared_by_every_ablation_and_constant_scaling_is_train_only<br>`services/api/tests/test_model_admission.py:567` — test_baseline_bounds_and_bias_are_applied_to_frozen_features | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### EVAL-005 — Qualified predictive values

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-005-01 | Unclassified checks — **WHEN** checks abstain or fail quality admission **THEN** they remain in full-row accounting without receiving invented classifications or entering classified predictive-value denominators | `services/api/tests/test_model_evaluation.py:414` — test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-005-02 | Undefined predictive value — **WHEN** no positive or negative classifications exist or too few bootstrap draws define a statistic **THEN** the affected statistic or interval is null and its denominator and effective draw count remain visible | `services/api/tests/test_model_evaluation.py:414` — test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-005-03 | Defined predictive values — **WHEN** both classified denominators and sufficient participant-cluster draws exist **THEN** PPV and NPV equal their respective correct classifications divided by classified denominators, with qualified intervals and observed prevalence | `services/api/tests/test_model_evaluation.py:414` — test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### EVAL-006 — Custody and pipeline locks

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-006-01 | Server-compatible evidence — **WHEN** fitting follows dataset custody lock and evaluation follows the post-fit pipeline lock **THEN** the engine report carries the post-fit lock and admits the exact trained-artifact chronology | `services/api/tests/test_model_evaluation.py:225` — test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-006-02 | Altered or premature evidence — **WHEN** an artifact or denominator changes, evaluation precedes the pipeline lock, or the report substitutes the earlier custody lock for the pipeline lock **THEN** reproduction or server admission rejects the evidence | `services/api/tests/test_model_evaluation.py:365` — test_cli_private_canonical_pipeline_and_full_reproduction_detect_corruption | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### EVAL-007 — Independent research evidence

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-007`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-007-01 | Supplied historical assertions — **WHEN** a dataset names an authorization, independent assessor or historical lock **THEN** output retains those references and labels their authenticity unverified rather than treating JSON assertions as approval | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |
| OTGD-008-EVAL-007-02 | Self-approved model — **WHEN** tooling output is supplied as authority without independently released study, model, calibration and qualification records **THEN** runtime admission refuses an estimate despite internally consistent artifact and report bytes | `services/api/tests/test_model_evaluation.py:354` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_admission.py:480` — test_current_authority_or_bytes_refusal_returns_no_score | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### EVAL-008 — Bounded file custody

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-evaluation/spec.md` / `EVAL-008`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-008-EVAL-008-01 | Stable regular input — **WHEN** a bounded regular file has unchanged identity, size and metadata throughout reading **THEN** its exact bytes are parsed and hashed for reproducible evidence | `services/api/tests/test_model_evaluation.py:399` — test_input_snapshot_uses_bounded_read_and_rejects_nonregular_files<br>`services/api/tests/test_model_admission.py:396` — test_http_native_evidence_real_registry_lifecycle_worker_and_research_read | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-008-EVAL-008-02 | Unsafe or changing input — **WHEN** an input is a symlink, FIFO, oversized file or changes during its descriptor read **THEN** the CLI refuses it without blocking indefinitely or producing an evaluation | `services/api/tests/test_model_evaluation.py:399` — test_input_snapshot_uses_bounded_read_and_rejects_nonregular_files | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `000`, `1`, `16 MiB`, `2`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### EVAL-007 history/reference/authenticity audit

Mapped existing cases: OTGD-008-EVAL-007-01/02; OTGD-041-EVAL-002-03/04/05; OTGD-042-HR-AUTH-008-01/02/03/04; full MOD-004/005/012/014/015 and VAL-004/005/006 are related, not automatically closed.

Assertion adequacy inspected: Independently read test_model_evaluation.py::external_history_pipeline/assert_forged_history_refused and both named test_external_history_references_remain_unverified_through_pipeline/test_self_asserted_or_extra_approval_fields_do_not_authenticate_history wrappers in full and four HR variants. Actual CLI index/freeze/train/evaluate/verify compares original dataset/analysis/split/training/report/artifact hashes, full evidence and eight-row evaluation membership. Original refs and HR custody/source/baseline/manifest remain exact. Every emitted authority/authenticity/history/clinical flag is false; strict extra fields and untyped/rehashed forged manifest refuse. Existing test_real_logistic_fitting... already asserted verified_by_tool false: the original V-SW-001 claim is narrowed accordingly.

Remaining limits: No scientific authenticity is established. Focused author-reported execution exists, but raw pytest stdout/JUnit is not linked; no final-candidate PASS adopted. These checks cover history custody; independent endpoint, genuine approvals and locked real study remain separate.
