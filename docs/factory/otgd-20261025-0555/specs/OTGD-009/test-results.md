# OTGD-009: verification results

Canonical: `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md`; SHA-256 `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 6 individually identified requirements and 16 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

| Evidence class | Actual activity / outcome | Status |
|---|---|---|
| Planning inspection | Read canonical requirements/scenarios and shared contracts; indexed existing test symbols, CI gates and workflow commands. Source hashes appear in test-plan.md and shared report. This is not a passing acceptance test. | EXECUTED inspection only |
| Related automated checks | Commands and named assertions planned; no execution authorized in this assignment. Exit code, execution timestamp and artifact hash therefore absent. | NOT_RUN |
| Complete criterion coverage | Every case requires full acceptance assertions; related symbol matching is not proof of complete coverage. No-match cases are explicitly identified in the plan. | NOT_RUN |
| Browser/native/firmware/real dependencies/performance | Scope-specific prerequisites and commands in plan/shared report; no substitution from unit mocks or historical CI. | NOT_RUN |
| Physical/scientific/release qualification | No actual participant/device/study/assay/deployment/store evidence adopted; external approvals remain separate. | BLOCKED where applicable |

## Current case results

All stable case IDs in test-plan.md are NOT_RUN, except explicitly external-only cases which are BLOCKED on named acceptance evidence. On execution replace this aggregate with one result row per affected case, retaining command/procedure, environment, UTC time, observed outcome, exit code, evidence path/hash and exact candidate/test bindings. Do not turn expected THEN statements into observed results.

No completion, engineering/product signoff or council PASS follows from this planning record.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

Final-candidate acceptance remains **NOT_RUN**; actual focused author executions are preserved below separately and do not establish this whole dossier PASS. Source/content changes after a focused run require fresh admission and affected reruns.

No new focused execution is adopted into this dossier in this audit. New UI/permissions/live/worker sources are WIP until author release and final bound execution; baseline firmware evidence retains its separate source/qualification limits.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 16 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"PARTIAL": 9, "PASS": 7}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-009-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-009 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/authorized-model-execution/specs/research-model-execution/spec.md`; SHA256 `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a`.

16 cases, 6 requirements: PARTIAL 7, PASS 9. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-009-MODEL-006-01 — PASS

Qualified diameter-only model — - **WHEN** current independent geometry and acquisition approvals match the exact camera, sampled ROI, extractor and phone build, and the pinned model uses baseline diameter only - **THEN** diameter may enter research execution while physical onset and response latency remain unqualified

Current proof: Actual typed fictional geometry registry lifecycle resolves optical_qualified, runs worker, reads validated1.1research result while preserving latency null/PHYSICAL_ONSET_UNMEASURED. Pure diameter arithmetic explicitly leaves physical onset false. This is software authority resolution on engineered evidence only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_http_optical_geometry_real_lifecycle_worker_and_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 422; 5 current observation(s).
- `services/api/tests/test_model_optical_authority.py::test_qualified_diameter_arithmetic_preserves_unmeasured_onset` — file SHA `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`, line 84; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 7f2586181682825e63293aa3870532dde685f8292bd2261d7baa235a7ee49e2d. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-006-02 — PASS

Geometry cannot qualify response timing — - **WHEN** a model requires eye latency or relative constriction, geometry is missing, the configuration is collection-only, or an additional quality failure exists - **THEN** the geometry-only path refuses research execution

Current proof: Parametrized latency/relative-constriction features refuse geometry-only execution; unqualified/BLUR/NO_MILLIMETER_GEOMETRY refuse; independent validator refuses collection-only, wrong calibration, tampered feature and missing native evidence. Current named executions cover all listed software alternatives.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_optical_authority.py::test_geometry_never_admits_response_features` — file SHA `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`, line 99; 10 current observation(s).
- `services/api/tests/test_model_optical_authority.py::test_geometry_approval_does_not_ignore_unknown_quality_flags` — file SHA `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`, line 117; 15 current observation(s).
- `services/api/tests/test_model_optical_authority.py::test_independent_optical_validator_and_current_authority_are_required` — file SHA `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`, line 143; 25 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA e5047bf5ef0292a6189a6847334c3eeef131e34ddea6d468c08fe197d700da0e. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-006-03 — PARTIAL

Geometry approval withdrawn during computation — - **WHEN** the geometry release is retired or replaced before result commit - **THEN** current authority is resolved again and the old computation cannot commit

Current proof: Actual optical output is computed, geometry calibration retired, current verification raises Problem before commit.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_optical_geometry_retirement_between_compute_and_commit_refuses_result` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 442; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Replaced rather than retired geometry release between compute/commit is not directly asserted; retirement proves revocation but not every listed replacement branch.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e2ddc3336faca1a15d594e93f70022173fd86977f3a6a3d18a46d4597cffbd9d. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-001-01 — PASS

Admitted artifact — - **WHEN** independently released authority names the exact version, length, SHA-256, feature contract and calibration - **THEN** the worker loads only those bytes and executes bounded finite arithmetic

Current proof: Real typed fictional registry lifecycle plus worker admits exact pinned canonical artifact and returns validated finite research result. Pure loader test validates actual bytes/ref/manifest and arithmetic0..1, hash/target unchanged; signature/registry fixture remains fictional and S3 is a transport double, not independent scientific release.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_engine.py::test_engineering_gate_and_finite_math_are_executable` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 247; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 6c7a7561aa510dcb96c04d162f72204978f236dc65a61e3dbef640a1fce3b74a. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-001-02 — PARTIAL

Unsupported or changed artifact — - **WHEN** the artifact is executable, noncanonical, nonfinite, oversized, uses unknown features, has unstable scales or differs from its pinned hash - **THEN** the worker returns a controlled refusal with no research probability

Current proof: Executable/unknown feature/nonfinite/dimension/zero and underflow scales reject; pinned byte/size/version/calibration/feature/noncanonical mutations refuse. Runtime changed bytes returns null probability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_executable_unknown_future_and_nonfinite_artifacts_fail` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 305; 35 current observation(s).
- `services/api/tests/test_model_engine.py::test_artifact_pinning_is_required` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 314; 30 current observation(s).
- `services/api/tests/test_model_engine.py::test_reversed_abstention_and_underflow_scales_fail_before_execution` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 499; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Reviewed tests do not directly supply an artifact exceeding the maximum admitted byte limit; mismatched expected size is not the same oversized artifact boundary. Add exact max+1 and bounded-read/controlled no-score assertion if not covered elsewhere.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9c71f33228ee3dba3205b003a786e66952d129cbe526435eb79909224d8c6976. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-002-01 — PASS

Authorized positive path — - **WHEN** all exact authority and acquisition dependencies are active and consistent for a controlled research participant - **THEN** the worker may compute the approved endpoint within its stated population and protocol scope

Current proof: Actual HTTP lifecycle fixture uses separate fictional submit/review/release, owned controlled-research session, native evidence, worker completion and authenticated result read; validates1.1state and current capability support. Pure scope matrix rejects foreign protocol/study/age/hardware. This establishes executable software governance, never actual participant authorization/model qualification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 940fd152ac3b6e5f826867c039d1dbdf23f647724140317bd48da7597c2ad447. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-002-02 — PARTIAL

Revocation during computation — - **WHEN** a study, model, method, calibration, device binding or consent changes before commit - **THEN** the result is refused or the operation fails without committing an estimate from stale authority

Current proof: Actual claimed worker output cannot commit after model revocation; stored result remains null. Separate pre-execution current consent/calibration/qualification/recovery mutations refuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_model_retirement_and_consent_change_between_compute_and_commit` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 542; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Only model retirement is directly interleaved after computation. Same boundary mutation of study/method/calibration/device binding/consent is not explicitly asserted before commit in reviewed model tests.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 149cdf2ad1e272d760367a4aaf64f9af6675ed72b40442bc676a9cbfa2391cf7. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-002-03 — PASS

Unqualified demonstration — - **WHEN** a guest, synthetic check, unapproved record or restored suspended study attempts inference - **THEN** it receives no research estimate even if request fields claim approval

Current proof: Client mutation matrix rejects guest_demo, synthetic snapshot/profile/sensors, missing study/protocol/context/manifest; runtime current authority matrix refuses suspended recovery, withdrawn consent and simulator. Every refusal has no research estimate, with server no-score assertion. Engineered software negatives only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 29cca3cd737f43ee6c230eed68f911731df3ef3ba71abae5013fa758e62ebfb1. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-003-01 — PARTIAL

Missing or censored required chemical feature — - **WHEN** a required analyte is missing, below quantification, incompatible or out of scope - **THEN** the system preserves its qualifier and refuses inference without imputing zero

Current proof: Acquisition matrix refuses censored below_loq and incompatible assay tuple; feature matrix refuses missing task/censored chemical feature rather than producing value.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Exact missing required analyte and all named censored/incompatible/out-of-scope alternatives need input qualifier/value preservation comparison and explicit no-zero-imputation output; exception assertions do not compare original input after refusal.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 66e4b4d656ebc55ff0684a88ba4cc8f13e11bcd03eaa70e62dca035114219c39. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-003-02 — PARTIAL

Native timing qualification — - **WHEN** the phone model, OS, native build, input/presentation clocks, implementation and extractor match independently released timing qualification - **THEN** the model uses its approved timing bias and uncertainty bound while retaining the unmodified native timing evidence

Current proof: Typed native HTTP lifecycle resolves exact fictional timing approval and result proof includes timing-calibration SHA. Bias test hashes feature vector after2ms adjustment; current input snapshot remains frozen in owned fixture.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_baseline_bounds_and_bias_are_applied_to_frozen_features` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 567; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Complete independent physical timing qualification for actual phone/OS/build/input/presentation clocks remains absent; software fixture does not establish calibrated uncertainty/bias on hardware. Exact approved uncertainty-bound application is not explicitly compared in reviewed model test.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5e1ccc728369fa7d127980b14d281b8260198a2d1ec04770aba18bf6bc5bd4ab. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-003-03 — PASS

Unqualified phone timing — - **WHEN** a simulator or unsupported timing tuple supplies native timestamps - **THEN** the system records measurement evidence and refuses model eligibility

Current proof: Runtime authority matrix mutates simulator true or OS foreign, rehashes attempt/manifest, and asserts controlled0.1inconclusive/null probability/model. This proves unsupported software-tuple refusal without laundering native timestamp evidence into model eligibility.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a6613a30e34edd1f0ec52a3530d7b724c10f293ae4b92071ff8d00ea5f2829be. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-004-01 — PARTIAL

Valid prior baseline — - **WHEN** the current and historical captures meet all owned evidence and scope checks - **THEN** the model uses their approved feature differences and binds the exact baseline snapshot hash

Current proof: Pure feature calculation compares prior/current owned features and yields differences; HR personalized HTTP fixture resolves original baseline and rejects changed signature.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_personalized_http_capture_resolves_its_own_original_baseline_and_rejects_changed_signature` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 395; 5 current observation(s).
- `apps/mobile/tests/research-result.test.ts::personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 245; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Generic model case requires exact baseline snapshot SHA bound into personalized output; client baseline test accepts supplied arbitrary nonzero digest after adding owned reference, not independent full generic baseline resolution. Need explicit actual prior baseline digest and approved feature-difference output binding.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3062e4689b6e28cdc0c6d8acb1a55b920854d98856ad1888f3aba70bcd94c4f2. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-004-02 — PARTIAL

Foreign or stale baseline — - **WHEN** a baseline is foreign, retired, future, stale, incomplete or unqualified - **THEN** the worker refuses personalized inference

Current proof: Direct foreign/future/missing/censored baseline features refuse; personalized max-age gate refuses incompatible baseline; HR scope/interval signature tests apply independent baseline authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_baseline_bounds_and_bias_are_applied_to_frozen_features` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 567; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Generic retired or independently unqualified baseline refusal is not directly executed in reviewed model baseline test; HR-only scope test does not prove each generic multi-channel baseline dependency.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f43721ad2e10d3a4794d7b59b5f624c99d3df9e5889cbfcd197aa4b7c9d7b33c. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-005-01 — PASS

Admitted research estimate — - **WHEN** a validated authenticated result is outside the abstention band - **THEN** the interface shows the research endpoint, population, version, probability, threshold, limits and supplied measurement context

Current proof: Authenticated result parser validates endpoint/population/version/probability/threshold and proof; result screen source displays research endpoint fields. Actual Result/History/row rendering preserves uncertainty policy/method/exact supplied limits/rationale, null abstention and historical scope; malformed/mismatched policy withheld. Shared current Result source supplies endpoint/population/research-only/no-driving text, not a probabilistic fitness claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 147; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual research result renders its verified uncertainty none and supplied band while refusing corrupted policy` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 239; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual rows and details retain measured, invalid, inconclusive, pending and fictional boundaries` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 177; 1 current observation(s).
- `apps/mobile/tests/result-presentation.test.ts::verified method none explicitly supplies no uncertainty interval and preserves its policy and rationale` — file SHA `2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120`, line 174; 1 current observation(s).
- `apps/mobile/tests/result-presentation.test.ts::supplied verified probability band shows exact abstention limits for below, above and null outcomes` — file SHA `2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120`, line 187; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::a verified uncertainty band requires null abstention rather than a probability or optimistic classification` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 221; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Software rendering and fictional engineering authority only; current independent scientific approval is not provided by the fixture.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ddce224838b38f8cb712e831665e265643a13162c7b17f824b49907fd5654453. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-005-02 — PASS

Uncertainty abstention — - **WHEN** the probability lies within the frozen abstention band - **THEN** the result and interface show inconclusive with null score, classification and threshold

Current proof: Server and client uncertainty-band tests require inconclusive with null probability/classification/threshold, reject optimistic probability/classification. Actual Result/History/row rendering preserves uncertainty policy/method/exact supplied limits/rationale, null abstention and historical scope; malformed/mismatched policy withheld. Shared current Result source supplies endpoint/population/research-only/no-driving text, not a probabilistic fitness claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_uncertainty_abstains_before_classification` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 268; 5 current observation(s).
- `apps/mobile/tests/research-result.test.ts::a verified uncertainty band requires null abstention rather than a probability or optimistic classification` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 221; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual research result renders its verified uncertainty none and supplied band while refusing corrupted policy` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 239; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual rows and details retain measured, invalid, inconclusive, pending and fictional boundaries` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 177; 1 current observation(s).
- `apps/mobile/tests/result-presentation.test.ts::verified method none explicitly supplies no uncertainty interval and preserves its policy and rationale` — file SHA `2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120`, line 174; 1 current observation(s).
- `apps/mobile/tests/result-presentation.test.ts::supplied verified probability band shows exact abstention limits for below, above and null outcomes` — file SHA `2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120`, line 187; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Software rendering and fictional engineering authority only; current independent scientific approval is not provided by the fixture.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fe473b4e1937d3dc5d932ba33953764a1b1fde258efe32f84a1bc270be179041. Actual current source and raw evidence supply this disposition.

## OTGD-009-MODEL-005-03 — PASS

Relabeled or inconsistent proof — - **WHEN** model version, endpoint, population, authority digest, baseline, uncertainty policy or threshold classification is inconsistent - **THEN** the client refuses the research display

Current proof: Client mutation matrix changes version/endpoint/population/authority/manifest/baseline/policy/classification/threshold and requires verifyResult rejection. Additional rebound-hash semantics matrix refuses inconsistent population/uncertainty/provenance. Tests exercise the display-admission boundary, not UI visualization.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::manifest semantic bounds and frozen source summaries cannot be forged by rebinding their hashes` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 259; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA d38e94f539fa62c07db8429407388b61f214e15283048fa6d4d26302ec20b378. Actual current source and raw evidence supply this disposition.
