# OTGD-042: verification results

Canonical: `openspec/changes/qualified-participant-acquisition/specs/scoped-cardiac-authority/spec.md`; SHA-256 `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 8 individually identified requirements and 23 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Focused evaluation/alcohol report: `../../reports/evaluation-implementation.md` SHA-256 `4332b81097b9dd4cc25545c46f808554439cf7d61a2425caa77cffe52ee96f0c`. Author reports185 evaluation/admission cases PASS, 43 governance cases PASS against actual disposable PG, 1338 non-PG API cases PASS with20 deselected;10 new evaluation and11 alcohol cases included. Initial alcohol fixture run4 failures and SQLite full-governance2 mandatory-PG failures preserved. Verifier read new assertions and confirmed all5 reported source hashes match at audit; raw pytest stdout/JUnit not linked, so execution is author-reported and not independently replayed/adopted. Only exact mapped focused assertions receive that evidence scope, not all planned cases.

Independent source assertion audits for this dossier: EVAL-007 history/reference/authenticity audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 23 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"PARTIAL": 7, "PASS": 16}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-042-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-042 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/qualified-participant-acquisition/specs/scoped-cardiac-authority/spec.md`; SHA256 `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7`.

23 cases, 8 requirements: PARTIAL 5, PASS 18. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-042-HR-AUTH-001-01 — PASS

Explicit approved heart-rate-only policy — - **GIVEN** a current independently released HR-only model, exact one-feature artifact and matching released server-interval policy - **WHEN** an owned fully admitted cardiac measurement is evaluated - **THEN** the service evaluates the separate interval authority before model execution - **AND** the policy alone grants no device, study or measurement qualification

Current proof: HTTP registry/signature/owned-check flow resolves separate interval authority before research worker; collection-only qualification cannot release interval scope; matching policy alone cannot supply released dependencies.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_hr_only_model_policy_release_and_retirement_recheck` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 108; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9f530ef38cbaa72d3790884827e3e91023a1c3d7a20de338f6753451a09bc21c. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-001-02 — PARTIAL

Unsupported predictor or implicit policy — - **GIVEN** missing policy, an ECG/RMSSD predictor, an additional required channel or a mismatching artifact feature - **WHEN** server interval qualification is requested - **THEN** the service refuses that authority and performs no model execution - **AND** no legacy model is silently upgraded

Current proof: ECG/RMSSD/additional artifact feature/channel refuses; legacy registry bytes remain unchanged without policy.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_actual_artifact_not_just_required_channels_is_hr_only` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 277; 10 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_interval_exception_cannot_extend_to_another_channel_or_artifact_feature` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 210; 15 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_required_channel_scope_is_heart_rate_only` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 145; 5 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_legacy_released_model_remains_readable_at_original_submitted_sha` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 166; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- missing policy refuses server-interval request with no model execution: explicit no-execution assertion for absent-policy legacy request not present in these bodies.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 71ef17f5bb20bc2296a42b0c0d46f9df539681093b9d795da72205613e0b6f03. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-002-01 — PARTIAL

Exact released measurement and behavior scope — - **GIVEN** current independently released model, configuration, hardware, firmware, qualification and calibration records for the exact protected reader and HR adapter - **WHEN** their complete immutable scope matches the owned accepted measurement - **THEN** the server may derive the restricted interval proof - **AND** externally observed sensor freshness and behavior evidence remains an approval prerequisite - **AND** the approved maximum interval is 100–120000 ms and server UTC error is 0–1000 ms - **AND** vendor signed-duration comparison requires independently reviewed monotonic rate error of 0–10000 ppm; ADC has no inferred signed duration or rate error

Current proof: Exact released fictional tuple resolves proof; mismatch scope and ambiguous/nonfinite authority refuse; ADC cannot infer signed duration and SDK needs reviewed rate bound.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_separate_release_checks_exact_current_configuration_tuple` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 93; 25 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_interval_scope_refuses_unimplemented_or_ambiguous_authority` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 70; 40 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_unsigned_adc_or_missing_unreviewed_sdk_clock_cannot_supply_signed_duration` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 140; 40 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- externally observed sensor freshness/behavior remains genuine approval prerequisite: physical evidence absent; lower/equality/upper full100–120000ms,0–1000ms,0–10000ppm release-bound matrix also not exhaustively asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d049bdd79003aac9549554eafe9bf91ca41c0938f2abb79f7d944ab897ef71cc. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-002-02 — PASS

One changed dependency or self-asserted calibration — - **GIVEN** a different key, device, firmware, extractor, configuration version/digest, method or interval bound, or an expired/retired/revoked dependency - **WHEN** the measurement is admitted or re-admitted - **THEN** the interval authority is refused - **AND** a participant checkbox or a caller-supplied qualified boolean cannot replace the released evidence

Current proof: Retired calibration/config/qualification/device deny; changed exact key/hardware/firmware/config digest/version and evaluation references refuse; collection-only proof or participant-checkbox behavior cannot create interval qualification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_retired_current_authority_never_promotes_old_capture` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 229; 20 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_separate_release_checks_exact_current_configuration_tuple` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 93; 25 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_training_evidence_refs_cannot_qualify_different_current_reader` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 377; 25 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_collection_only_proof_cannot_qualify_server_interval` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 101; 5 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_interval_scope_refuses_unimplemented_or_ambiguous_authority` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 70; 40 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 73dd2a2f6c7b85f49f9244a52f60c152bbdd22badcdf32cdbe720c0e31514f5b. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-003-01 — PASS

Original custody bounds retained — - **GIVEN** an owned accepted valid PPG attempt whose exact signed grant and device-signed completion have been verified - **WHEN** the original attestation receipt follows original grant issue within the approved maximum - **THEN** the proof records both original endpoints and their conservative width - **AND** the original snapshot, target chronology and unqualified clock flags remain unchanged

Current proof: Owned signature-admitted interval retains original quality flags and snapshot hash; decimal widened endpoints preserve original snapshot bytes; PostgreSQL blocks anchor/body/time/revision rewrites.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_epoch_precision_uses_durable_decimal_values_and_never_rewrites_device_evidence` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 84; 5 current observation(s).
- `services/api/tests/test_participant_postgres.py::test_signed_issue_and_attestation_receipt_anchors_cannot_be_rewritten` — file SHA `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0`, line 60; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 100942479aca09bf61f61790e0cdcedd513bcf416c6234ef464e1bae6be13717. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-003-02 — PARTIAL

Missing, reversed or renewed endpoints — - **GIVEN** absent accepted attestation, negative/nonfinite/reversed times, a foreign attempt, a mismatching signature or an interval above its approved maximum - **WHEN** authority is computed - **THEN** the service refuses it - **AND** replay or a replacement receipt cannot restart its age or shorten the original interval

Current proof: Rehashed server/device signatures, owner/scope/anchor/binding/projection changes refuse; reversed companion time and changed width refuse; durable anchors cannot renew.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_rehashed_custody_records_still_require_original_signatures_and_exact_scope` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 310; 50 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_unsigned_timing_or_channel_changes_cannot_qualify` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 238; 40 current observation(s).
- `apps/mobile/tests/research-result.test.ts::HR-only proof refuses rebased intervals, broader models, altered calibration/policy/scope, fictional predictors and unpreserved uncertainty` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 80; 1 current observation(s).
- `services/api/tests/test_participant_postgres.py::test_signed_issue_and_attestation_receipt_anchors_cannot_be_rewritten` — file SHA `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0`, line 60; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- absent accepted attestation, negative/nonfinite endpoints, and actual replay/replacement attempts cannot restart age: each exact admission branch is not directly exercised by these named bodies.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3bcc49b2a74e83e4255e48471a02440f3c5b602c7260c8476cb1a4ffca239ea8. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-003-03 — PASS

Vendor signed duration fits the conservative interval — - **GIVEN** the actual SDK-signed monotonic duration and exact independently reviewed rate-error bound - **WHEN** its rational comparison satisfies `duration_us × 1000000 ≤ custody_window_us × (1000000 + maximum_monotonic_rate_error_ppm)` using the unrounded widened endpoints - **THEN** that consistency check permits admission - **AND** it does not establish sensor onset, actual cadence or absolute device UTC

Current proof: Exact rational SDK duration equality admits with reviewed rate error; test uses unrounded widened microsecond endpoint window, keeping duration as consistency only and no onset/cadence/UTC evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_signed_sdk_duration_uses_reviewed_rate_error_and_exact_unrounded_custody_bound` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 347; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_signed_sdk_duration_respects_exact_reviewed_rate_limit_not_a_rounded_millisecond` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 109; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a9a1804c2b8783224b33962fddc71e3574bb276051a9ae30fa5940d22479f5b3. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-003-04 — PASS

Signed duration cannot fit the original custody window — - **GIVEN** a vendor duration above the exact conservative bound, missing vendor rate-error qualification or an inferred ADC duration - **WHEN** interval authority is resolved or validated - **THEN** authority refuses despite an apparently fitting rounded millisecond interval - **AND** no endpoint, duration or original flag is rewritten

Current proof: One-microsecond overflow refuses despite outward rounded millisecond fit; missing duration/rate, rate>10000/bool and inferred ADC duration all refuse without mutation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_signed_sdk_duration_uses_reviewed_rate_error_and_exact_unrounded_custody_bound` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 347; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_signed_sdk_duration_respects_exact_reviewed_rate_limit_not_a_rounded_millisecond` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 109; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_unsigned_adc_or_missing_unreviewed_sdk_clock_cannot_supply_signed_duration` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 140; 40 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 7a40f3834a0d36f12d8baef7c2d6aabc605e200b919cee01c465e8bd858c6cc2. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-004-01 — PASS

Conservative bounds meet every limit — - **GIVEN** an exact admitted HR-only authority whose conservative width and acquisition bounds meet all model limits - **WHEN** current delivery age also meets the model's maximum - **THEN** timing admission may succeed using the separately labeled bounds - **AND** the immutable snapshot is not rewritten to look physically calibrated - **AND** both endpoint error margins widen the bounds with one shared outward-rounding calculation

Current proof: Both UTC margins widen conservative interval/acquisition/delivery bounds; exact declared maxima admit; canonical original snapshot unchanged with null clock uncertainty.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_shared_exact_interval_arithmetic_nonzero_margin_and_inclusive_boundary` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 255; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_epoch_precision_uses_durable_decimal_values_and_never_rewrites_device_evidence` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 84; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 89ec6b7107c2757726984b638e2815c7809bd253eb13cff37b906433d61582ed. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-004-02 — PASS

Original issue reveals late delivery — - **GIVEN** an apparently recent client capture timestamp but an original signed issue time whose delivery age exceeds the frozen maximum - **WHEN** execution is requested - **THEN** the service refuses the late measurement - **AND** a current retry time or attestation replay cannot make it current

Current proof: Fresh client capture time cannot hide old original interval delivery; publication rechecks current time and refuses expired result; durable original anchors cannot be rewritten to renew age.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority_provenance.py::test_fresh_client_end_time_and_baseline_mode_cannot_hide_an_old_delivery` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 161; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_publication_rechecks_original_delivery_age_instead_of_old_evaluation_time` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 385; 5 current observation(s).
- `services/api/tests/test_participant_postgres.py::test_signed_issue_and_attestation_receipt_anchors_cannot_be_rewritten` — file SHA `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0`, line 60; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA bdcef23089e18db6d1ad451fa439068b58cdc21b68fdddf536676ef4b1c561df. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-004-03 — PASS

Exact limit and adjacent overflow — - **GIVEN** the same valid immutable measurement with finite conservative bounds - **WHEN** a bound equals the declared inclusive maximum - **THEN** that comparison permits admission - **BUT WHEN** it exceeds the maximum by a representable positive amount - **THEN** that comparison refuses admission

Current proof: Equality202/1202/302 admits; lowering each inclusive maximum by1ms refuses; original5004ms policy limit equality and5003ms refusal independently exercised.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_shared_exact_interval_arithmetic_nonzero_margin_and_inclusive_boundary` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 255; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_epoch_precision_uses_durable_decimal_values_and_never_rewrites_device_evidence` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 84; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_each_conservative_limit_refuses_one_millisecond_below_required_bound` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 102; 15 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 465c44f8c9fc60797a3fd8c198e70c51812311ee5b83fde092d22c3335a000f6. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-005-01 — PARTIAL

Recognized timing limitation remains visible — - **GIVEN** a valid exact adapter measurement carrying its complete known unqualified server/host timing flags and a matching interval proof - **WHEN** restricted HR-only execution succeeds - **THEN** the original evidence and authority manifest retain those flags and explain the conservative method - **AND** vendor confidence remains acquisition quality rather than a calibrated prediction probability

Current proof: ADC flags and immutable snapshot retained through server worker/client result/export with conservative proof; physical clock flags remain unqualified.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).
- `apps/mobile/tests/research-result.test.ts::actual signed API-to-worker HR-only fixture verifies conservative server interval authority without rewriting its sensor flags` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 41; 1 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_epoch_precision_uses_durable_decimal_values_and_never_rewrites_device_evidence` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 84; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- vendor confidence remains acquisition quality rather than prediction probability in successful vendor execution: no successful vendor confidence presentation assertion in these bodies.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fe5a68a57bcaeac156ee0a88d20f470f9394987eeb6e8f1931727dfe67d21e32. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-005-02 — PASS

Fault flag or different modality — - **GIVEN** a contact, range, confidence, dropped-data or unknown additional fault flag, or ECG/unsupported modality - **WHEN** an interval proof is presented - **THEN** the service refuses the exception - **AND** no flag is removed, normalized or hidden to make the measurement eligible

Current proof: Both adapter known flag sets reject rehashed contact/range/drops/unknown firmware faults; cleaned flags, ECG/RMSSD/unsupported model scope or changed features refuse without normalizing input.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority_provenance.py::test_matching_rehashed_snapshot_and_companion_never_whitelist_a_device_fault` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 150; 60 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_unsigned_timing_or_channel_changes_cannot_qualify` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 238; 40 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_interval_exception_cannot_extend_to_another_channel_or_artifact_feature` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 210; 15 current observation(s).
- `apps/mobile/tests/research-result.test.ts::HR-only proof refuses rebased intervals, broader models, altered calibration/policy/scope, fictional predictors and unpreserved uncertainty` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 80; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c673bb6692a32943cd37cbe7178a5a26834202be51604f08055fa70e98c56114. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-006-01 — PASS

Independently admitted compatible baseline — - **GIVEN** explicit baseline-delta permission and current and historical measurements with the same exact allowed scope - **WHEN** each original interval is independently valid and baseline age meets the frozen historical limit - **THEN** the model may calculate only the approved heart-rate baseline delta - **AND** both authority proofs are retained separately

Current proof: HTTP baseline retains its own prior attestation/authorization and earlier interval; feature digest is exact delta; offline raw/personalized fixtures reproduce runtime values with independent baseline age.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_personalized_http_capture_resolves_its_own_original_baseline_and_rejects_changed_signature` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 395; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_personalized_baseline_uses_explicit_historical_proof_and_conservative_age` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 263; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f0725a51385973a95433781a2782ecca0a8f8820da423e0f0d247933799fa287. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-006-02 — PASS

Current proof with incompatible baseline — - **GIVEN** a valid current proof but an old baseline with another device/key/configuration, absent signed evidence, retired calibration or excess historical age - **WHEN** personalized execution is requested - **THEN** personalized admission refuses - **AND** the service does not silently substitute zero delta, a population result or the current proof for the baseline proof

Current proof: Changed device/calibration/config/age/chronology fails; rehashed old signature fails current verification; missing/hash/subject/protocol/same-session/attempt/wrong-ref/device/fault baseline refuses without substituted delta.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_baseline_requires_independent_original_interval_same_scope_and_conservative_age` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 282; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_personalized_http_capture_resolves_its_own_original_baseline_and_rejects_changed_signature` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 395; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_personalized_baseline_uses_explicit_historical_proof_and_conservative_age` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 263; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 511b906e1a293df83c861bbd49f42261135b83cc85afe2726a52878d5a4a3380. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-007-01 — PASS

Bound proof through accepted job and read — - **GIVEN** exact independently admitted current and optional baseline authority - **WHEN** the accepted worker publishes and the participant reads the versioned result - **THEN** its immutable authority manifest binds the original proof digest and model/input scope - **AND** current checks pass before every numeric disclosure

Current proof: Accepted worker publishes strict1.1 with immutable input/current+baseline proof; participant GET and strict server/client result validation succeed only against matching proof/model scope; changed baseline signature fails current execution verification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_personalized_http_capture_resolves_its_own_original_baseline_and_rejects_changed_signature` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 395; 5 current observation(s).
- `apps/mobile/tests/research-result.test.ts::actual signed API-to-worker HR-only fixture verifies conservative server interval authority without rewriting its sensor flags` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 41; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b7d995b744446e69f813aeaeab5e55e64cde19ca9c13c27206fced90581fcf04. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-007-02 — PASS

Revocation after acceptance or forged companion — - **GIVEN** authority revoked after job acceptance, or a changed companion with a newly computed caller digest - **WHEN** execution, commit, cached replay or result read occurs - **THEN** current server admission refuses numeric disclosure - **AND** neither a hash alone nor a fictional fixture creates an approval

Current proof: Current execution refuses retired dependency/rehashed signature; publication rejects old original delivery; client refuses rehashed altered companion. SignedHTTPworker numeric before retirement, currentadmissionrefuses aftermodel/exactcalibrationretirement; result/detail/history withhold and immutableevidence unchanged. TypedHR requirescontext/nonHR preserved. Export build/commit/download rechecks tested using abstainedHR fixture. ExistingHRcache exactdigest/view/epoch/account/gen ephemeralread, late/offline/denial/mismatch refusal; separateexportadmission atassembly/finalrelease, actualResultDOMwithprepopulatedHR.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_retired_current_authority_never_promotes_old_capture` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 229; 20 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_publication_rechecks_original_delivery_age_instead_of_old_evaluation_time` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 385; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_rehashed_custody_records_still_require_original_signatures_and_exact_scope` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 310; 50 current observation(s).
- `apps/mobile/tests/research-result.test.ts::HR-only proof refuses rebased intervals, broader models, altered calibration/policy/scope, fictional predictors and unpreserved uncertainty` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 80; 1 current observation(s).
- `services/api/tests/test_model_admission.py::test_model_retirement_and_consent_change_between_compute_and_commit` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 542; 5 current observation(s).
- `services/api/otgd/main.py::result_get` — file SHA `a84b0694e0e97b41ed113f78ad261e0cfc352c9d84961969311d72d10681a46a`, line 977; 0 current observation(s).
- `services/api/otgd/domain.py::safe_result` — file SHA `ba1d898a1107ab9983a5ce4d2f6f04884b94acab3fc6130e04ad106fb3fc92d5`, line 672; 0 current observation(s).
- `services/api/otgd/model_engine.py::verify_current_execution` — file SHA `8c145b7674d44068ad0b16fdab04776f3fc9c3ce9c03bfb772efb211683760e7`, line 1087; 0 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_retired_hr_authority_prevents_stored_numeric_readback` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 32; 30 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_current_hr_read_requires_context_but_keeps_original_result` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 107; 5 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_non_hr_historical_result_retains_context_free_validation` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 118; 5 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_hr_export_rechecks_current_authority_at_each_boundary` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 251; 30 current observation(s).
- `apps/mobile/tests/hr-read-admission.test.ts::HR numeric display requires a matched owned200 per view and never persists admission or changes saved evidence` — file SHA `83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8`, line 54; 1 current observation(s).
- `apps/mobile/tests/hr-read-admission.test.ts::late HR200 cannot revive a left view, offline transition, retired generation, changed account or background workspace` — file SHA `83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8`, line 238; 1 current observation(s).
- `apps/mobile/tests/hr-read-admission.test.ts::local HR export independently reads before assembly and final release; refusal releases no archive` — file SHA `83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8`, line 341; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::actual HR screen requires a fresh admitted result on open and after evidence navigation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 236; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::actual HR manual refresh and late read after leaving cannot revive cached numeric research` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 279; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: The final numeric cloudexport positive is tested separately under FINAL_NUMERIC_EXPORT; this original group retains its narrower revocation scope. SQLite/objectstore doubles; no full currentlive claim. The original prepopulatedHR scope is supplemented by FINAL_MOUNTED_HR; it did not prove that transition by itself. NativeOSsharing/realserverretirement not componentproof.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d402b772b4cccd48501def9699fc665c056b318c0c1ec0db37e01bb9cad7a93e. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-007-03 — PASS

Legacy measurement behavior preserved — - **GIVEN** a legacy 0.1 result or an HR measurement without the explicit released model/calibration policy - **WHEN** it is rendered or evaluated - **THEN** existing measurement-only or unavailable behavior remains - **AND** no new numeric research claim is inserted into the strict legacy envelope

Current proof: Legacy0.1 envelope rejects appended research proof; old released model remains readable at original submitted hash with no policy or report-scope mutation; no silent authority inserted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 245; 1 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_legacy_released_model_remains_readable_at_original_submitted_sha` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 166; 5 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_additive_scope_fields_preserve_prior_submission_identity` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 152; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA dfd042a3ae71de46120933caf27e5f574942211914f0c7ec8d101fcac6c64d29. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-007-04 — PARTIAL

Safe measurement job without model authority — - **GIVEN** an otherwise admitted measurement whose current HR model or calibration authority is unavailable - **WHEN** the participant explicitly finalizes and queues its measurement job - **THEN** the service may process its measurement-only result under the ordinary current account/study rules - **AND** accepting that job supplies no numeric HR-model authority; every subsequent conditional execution or disclosure still requires complete current proof

Current proof: No-model fictional participant job completes inconclusive with null probability; losing HR authority prevents conditional execution.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_retired_current_authority_never_promotes_old_capture` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 229; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- otherwise admitted cardiac measurement can finalize/queue under ordinary rules when current HR model/calibration absent, with no numeric authority: exact cardiac missing-authority finalize/worker path is not executed here.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9005e810abf2ee6c733047aa60fd842c8213e8d1514c12dda921e2e09e6fec87. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-008-01 — PASS

Scoped population training and evaluation — - **GIVEN** a frozen HR-only plan and source-bundle/custody review references with exact typed current snapshot and interval companions - **WHEN** original flags, value, target, information cutoff, policy and source digests match and every conservative timing gate passes - **THEN** train-only fitting and held-out/later-session evaluation produce the explicit `cardiac_hr_only` artifact/report variant - **AND** invalid and abstaining rows and all six frozen strata retain complete counts - **AND** the output does not invent chemical/app/ECG comparison results

Current proof: Train-only fitting/held-out independence, HR-only artifact,32 custody rows, invalid denominators, exact source/policy hashes and no multimodal paired claims proven for4adapter/baseline variants. Full and cardiac-cohort tests call same reviewed helper. It binds original artifact/data/plan/split hashes and all six dimensions/partitions/variants, explicit one-class null statistics and singleton-versus2participant cluster support. Actual four-variant HR-only train/evaluate pipeline retains exact invalid/abstained identities and all six strata for both held-out partitions, totals8/invalid1/valid7/abstained7; original dataset/plan/split/artifact hashes, explicit cardiac_hr_only and no multimodal/approval claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_held_out_hr_values_and_outcomes_cannot_affect_training` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 221; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_invalid_custody_or_faults_remain_in_all_row_denominators` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 182; 440 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_invalid_training_custody_is_rejected_without_cleaning_flags_or_losing_manifest_rows` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 291; 20 current observation(s).
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

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0134c8133cf34a7f306aeeceb28bdeb6306766eb8bced299ac6161f6e22360d8. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-008-02 — PASS

Explicit personalized baseline evidence — - **GIVEN** a frozen baseline-delta policy, historical age bound and both full original current/baseline snapshots - **WHEN** the companion independently binds both snapshots and runtime-equivalent original interval, scope, chronology and baseline-age checks succeed - **THEN** the sole fitted predictor is the exact current-minus-baseline heart-rate value - **AND** no arbitrary earlier dataset row supplies a missing baseline

Current proof: Exact current-minus-baseline is sole feature and matches runtime; independent baseline age equality/overflow enforced; arbitrary earlier reference and missing/incompatible baseline refuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_personalized_baseline_uses_explicit_historical_proof_and_conservative_age` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 263; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 8280f923322283ffe1a2bde3df79217a74518195e3f2780c5a5fe0fe9988bbe5. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-008-03 — PASS

Forged consistency or incomplete baseline — - **GIVEN** changed original flags/value/target, mismatching policy/source digest, missing required baseline or an incompatible/late interval - **WHEN** fitting or evaluation is attempted - **THEN** the tooling refuses the incompatible row or dataset under its explicit invalid-row rules - **AND** matching editable hashes do not establish trusted server signatures, current registry state or genuine custody review

Current proof: Changed original flags/value/target/policy/source hash or missing/late/incompatible baseline becomes invalid with retained denominator; strict forged authority/rehashed unauthenticated review cannot produce authenticated signatures/registry/independent custody.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation_cardiac.py::test_invalid_custody_or_faults_remain_in_all_row_denominators` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 182; 440 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_personalized_baseline_uses_explicit_historical_proof_and_conservative_age` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 263; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_self_asserted_or_extra_approval_fields_do_not_authenticate_history` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 141; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3c54ee8db34391f77339d957838f60898dc4ade3620bff95f96edcaa06d02ad8. Actual current source and raw evidence supply this disposition.

## OTGD-042-HR-AUTH-008-04 — PASS

Legacy quality and four-ablation behavior — - **GIVEN** a plan without the explicit HR-only policy - **WHEN** it encounters an unqualified flagged cardiac row or runs the existing evaluation mode - **THEN** the original quality refusal and all four matched-ablation requirements remain - **AND** a caller cannot switch modes after dataset/analysis locking to remove failures or comparisons

Current proof: Legacy rejects unprespecified HR evidence/reduced feature plan and retains four ablations; changed locked plan/data/threshold/training refuses rather than switching to reduced mode after lock.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation_cardiac.py::test_hr_scope_rejects_mixed_rows_and_unprespecified_legacy_evidence` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 302; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_legacy_absent_optional_fields_do_not_change_dataset_or_plan_bytes` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 315; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 41b65e7a404c3ff1c79bd1ad008f2baf4c839bccdc188d9d8e0ace58149b8497. Actual current source and raw evidence supply this disposition.
