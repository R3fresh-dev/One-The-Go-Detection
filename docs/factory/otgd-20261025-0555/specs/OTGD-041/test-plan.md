# OTGD-041: verification plan

Canonical: `openspec/changes/qualified-participant-acquisition/specs/research-evaluation/spec.md`; SHA-256 `f4bef2eee7577e8f57b7cd27b7463d3879dcb1d452c73540d8916f9d6bf41726`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001 v1, D-002 v1, D-003 v1, D-004 v1 acknowledged through native messaging. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `services/api/tests/test_model_engine.py` — `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`
- `services/api/tests/test_model_evaluation.py` — `753cb94b151befc5742260804631c5e7517813c332d9c435564b25e1537a3aa7`
- `services/api/tests/test_model_evaluation_cardiac.py` — `23efe98238052ce2b19fbbc6aa50647a384196023d912c0f05fb436b491eca65`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### EVAL-002 — Complete matched evaluation and ablations

Normative acceptance source: `openspec/changes/qualified-participant-acquisition/specs/research-evaluation/spec.md` / `EVAL-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-041-EVAL-002-01 | Full report — **WHEN** the existing evaluation mode runs on supplied qualified data **THEN** its report names artifact, dataset, split and analysis digests and includes chemical-only, app-only, combined and ECG-removed analyses with complete matched denominators | `services/api/tests/test_model_evaluation.py:221` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_evaluation_cardiac.py:300` — test_legacy_absent_optional_fields_do_not_change_dataset_or_plan_bytes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-041-EVAL-002-02 | Omitted or changed rows — **WHEN** invalid or abstaining rows are removed, an ablation uses different rows, or a threshold changes after locking **THEN** the tooling refuses to attest a valid evaluation report | `services/api/tests/test_model_evaluation.py:221` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_evaluation_cardiac.py:220` — test_exact_interval_limit_uses_outward_rounding_not_zero_error | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-041-EVAL-002-03 | Engineering fixtures — **WHEN** automated tests use fictional cohort rows **THEN** their artifacts are labeled engineering evidence and never loaded as an approved study or human model by deployment | `services/api/tests/test_model_evaluation.py:221` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_evaluation_cardiac.py:276` — test_invalid_training_custody_is_rejected_without_cleaning_flags_or_losing_manifest_rows | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-041-EVAL-002-04 | Explicit restricted HR-only report — **GIVEN** a prespecified locked server-interval policy with exactly the approved HR predictor and independently bound current/baseline evidence **WHEN** the separate HR-only mode completes evaluation **THEN** its strict report names `cardiac_hr_only`, reconciles every cohort/stratum and invalid/abstained row, and retains frozen dataset/split/analysis/artifact digests **AND** chemical/app/ECG ablation comparisons are explicitly outside that mode and no multimodal superiority claim is emitted | `services/api/tests/test_model_evaluation.py:221` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-041-EVAL-002-05 | Implicit or mismatching reduced report — **GIVEN** an absent or mismatching HR-only policy, a legacy model, extra predictors or incomplete row accounting **WHEN** a single-variant report is submitted for model admission **THEN** the service refuses it **AND** the caller cannot use the new mode to omit required comparisons from the existing mode | `services/api/tests/test_model_evaluation.py:221` — test_later_validation_without_prior_held_out_session_and_single_class_cohort_fail<br>`services/api/tests/test_model_evaluation_cardiac.py:206` — test_held_out_hr_values_and_outcomes_cannot_affect_training | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.
