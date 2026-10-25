# OTGD-009: verification plan

Canonical: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md`; SHA-256 `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/tests/research-result.test.ts` — `5e39d0bf4fb9376df15ae349da774b343dc0428d80fae35e6ee7f2b618ba33ea`
- `services/api/tests/test_cardiac_authority.py` — `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`
- `services/api/tests/test_model_admission.py` — `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`
- `services/api/tests/test_model_engine.py` — `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`
- `services/api/tests/test_model_evaluation.py` — `60013323430a0979caeffcef4b2983566a028b0f50e75938df7f053c0498fdc0`
- `services/api/tests/test_model_optical_authority.py` — `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### MODEL-006 — Independently qualified optical diameter

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md` / `MODEL-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-009-MODEL-006-01 | Qualified diameter-only model — **WHEN** current independent geometry and acquisition approvals match the exact camera, sampled ROI, extractor and phone build, and the pinned model uses baseline diameter only **THEN** diameter may enter research execution while physical onset and response latency remain unqualified | `services/api/tests/test_model_optical_authority.py:84` — test_qualified_diameter_arithmetic_preserves_unmeasured_onset<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-006-02 | Geometry cannot qualify response timing — **WHEN** a model requires eye latency or relative constriction, geometry is missing, the configuration is collection-only, or an additional quality failure exists **THEN** the geometry-only path refuses research execution | `services/api/tests/test_model_optical_authority.py:84` — test_qualified_diameter_arithmetic_preserves_unmeasured_onset<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-006-03 | Geometry approval withdrawn during computation — **WHEN** the geometry release is retired or replaced before result commit **THEN** current authority is resolved again and the old computation cannot commit | `services/api/tests/test_model_optical_authority.py:84` — test_qualified_diameter_arithmetic_preserves_unmeasured_onset<br>`services/api/tests/test_model_admission.py:442` — test_optical_geometry_retirement_between_compute_and_commit_refuses_result | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MODEL-001 — Approved immutable artifact admission

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md` / `MODEL-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-009-MODEL-001-01 | Admitted artifact — **WHEN** independently released authority names the exact version, length, SHA-256, feature contract and calibration **THEN** the worker loads only those bytes and executes bounded finite arithmetic | `apps/mobile/tests/research-result.test.ts:41` — actual signed API-to-worker HR-only fixture verifies conservative server interval authority without rewriting its sensor flags<br>`services/api/tests/test_model_admission.py:480` — test_current_authority_or_bytes_refusal_returns_no_score | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-001-02 | Unsupported or changed artifact — **WHEN** the artifact is executable, noncanonical, nonfinite, oversized, uses unknown features, has unstable scales or differs from its pinned hash **THEN** the worker returns a controlled refusal with no research probability | `services/api/tests/test_model_engine.py:305` — test_executable_unknown_future_and_nonfinite_artifacts_fail<br>`services/api/tests/test_model_admission.py:480` — test_current_authority_or_bytes_refusal_returns_no_score | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MODEL-002 — Current participant and scientific authority

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md` / `MODEL-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-009-MODEL-002-01 | Authorized positive path — **WHEN** all exact authority and acquisition dependencies are active and consistent for a controlled research participant **THEN** the worker may compute the approved endpoint within its stated population and protocol scope | `services/api/tests/test_model_admission.py:542` — test_model_retirement_and_consent_change_between_compute_and_commit<br>`apps/mobile/tests/research-result.test.ts:144` — actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-002-02 | Revocation during computation — **WHEN** a study, model, method, calibration, device binding or consent changes before commit **THEN** the result is refused or the operation fails without committing an estimate from stale authority | `services/api/tests/test_model_admission.py:542` — test_model_retirement_and_consent_change_between_compute_and_commit<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-002-03 | Unqualified demonstration — **WHEN** a guest, synthetic check, unapproved record or restored suspended study attempts inference **THEN** it receives no research estimate even if request fields claim approval | `services/api/tests/test_model_admission.py:542` — test_model_retirement_and_consent_change_between_compute_and_commit<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MODEL-003 — Qualified acquisition and temporal features

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md` / `MODEL-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-009-MODEL-003-01 | Missing or censored required chemical feature — **WHEN** a required analyte is missing, below quantification, incompatible or out of scope **THEN** the system preserves its qualifier and refuses inference without imputing zero | `apps/mobile/tests/research-result.test.ts:77` — HR-only proof refuses rebased intervals, broader models, altered calibration/policy/scope, fictional predictors and unpreserved uncertainty<br>`services/api/tests/test_cardiac_authority.py:277` — test_actual_artifact_not_just_required_channels_is_hr_only | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-003-02 | Native timing qualification — **WHEN** the phone model, OS, native build, input/presentation clocks, implementation and extractor match independently released timing qualification **THEN** the model uses its approved timing bias and uncertainty bound while retaining the unmodified native timing evidence | `services/api/tests/test_cardiac_authority.py:277` — test_actual_artifact_not_just_required_channels_is_hr_only<br>`services/api/tests/test_model_evaluation.py:312` — test_same_check_observations_and_later_assay_delivery_preserve_original_target | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-003-03 | Unqualified phone timing — **WHEN** a simulator or unsupported timing tuple supplies native timestamps **THEN** the system records measurement evidence and refuses model eligibility | `apps/mobile/tests/research-result.test.ts:77` — HR-only proof refuses rebased intervals, broader models, altered calibration/policy/scope, fictional predictors and unpreserved uncertainty<br>`services/api/tests/test_cardiac_authority.py:277` — test_actual_artifact_not_just_required_channels_is_hr_only | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MODEL-004 — Personal baseline ownership and age

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md` / `MODEL-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-009-MODEL-004-01 | Valid prior baseline — **WHEN** the current and historical captures meet all owned evidence and scope checks **THEN** the model uses their approved feature differences and binds the exact baseline snapshot hash | `apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields<br>`services/api/tests/test_cardiac_authority.py:282` — test_baseline_requires_independent_original_interval_same_scope_and_conservative_age | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-004-02 | Foreign or stale baseline — **WHEN** a baseline is foreign, retired, future, stale, incomplete or unqualified **THEN** the worker refuses personalized inference | `services/api/tests/test_cardiac_authority.py:282` — test_baseline_requires_independent_original_interval_same_scope_and_conservative_age<br>`apps/mobile/tests/research-result.test.ts:242` — personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### MODEL-005 — Abstention and authenticated research presentation

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md` / `MODEL-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-009-MODEL-005-01 | Admitted research estimate — **WHEN** a validated authenticated result is outside the abstention band **THEN** the interface shows the research endpoint, population, version, probability, threshold, limits and supplied measurement context | `apps/mobile/tests/research-result.test.ts:218` — a verified uncertainty band requires null abstention rather than a probability or optimistic classification<br>`services/api/tests/test_model_engine.py:518` — test_result_policy_classification_registry_and_baseline_cannot_be_relabelled | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-005-02 | Uncertainty abstention — **WHEN** the probability lies within the frozen abstention band **THEN** the result and interface show inconclusive with null score, classification and threshold | `apps/mobile/tests/research-result.test.ts:218` — a verified uncertainty band requires null abstention rather than a probability or optimistic classification<br>`services/api/tests/test_model_engine.py:518` — test_result_policy_classification_registry_and_baseline_cannot_be_relabelled | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-009-MODEL-005-03 | Relabeled or inconsistent proof — **WHEN** model version, endpoint, population, authority digest, baseline, uncertainty policy or threshold classification is inconsistent **THEN** the client refuses the research display | `apps/mobile/tests/research-result.test.ts:218` — a verified uncertainty band requires null abstention rather than a probability or optimistic classification<br>`services/api/tests/test_model_engine.py:518` — test_result_policy_classification_registry_and_baseline_cannot_be_relabelled | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1.1`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.
