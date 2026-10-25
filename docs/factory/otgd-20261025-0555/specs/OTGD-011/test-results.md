# OTGD-011: verification results

Canonical: `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md`; SHA-256 `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 9 individually identified requirements and 18 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 18 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"PARTIAL": 13, "PASS": 5}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-011-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-011 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/canonical-operator-governance/specs/operator-authority/spec.md`; SHA256 `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2`.

18 cases, 9 requirements: PARTIAL 11, PASS 7. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-011-OPERATOR-AUTHORITY-001-01 — PASS

Alteration of accepted submission — - **GIVEN** a submitted version with a recorded canonical digest - **WHEN** an administrator attempts to update its JSON, digest, version or submitting identity - **THEN** PostgreSQL rejects the update and the original body remains reconstructable

Current proof: Actual PostgreSQL rejects body/submitted_by mutation and deletion; event mutation/deletion rejected; history still has three decisions. Expanded actualPGtrigger test rejects JSON/digest/version/submitter/time updates, rereads full original history/digest and append-only decision violations.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_actual_postgresql_preserves_registry_content_and_append_only_decisions` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 893; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current complete PostgreSQL gate executed1508 named cases, including this exact trigger test. PostgreSQL semantics are proven; no physical/study approval follows.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6f82c47a9743d45ac1987f56119e6851fe56af8490f181aa1f8697035727faee. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-001-02 — PARTIAL

Normalized submission and same-version retry — - **GIVEN** a typed study body and a separately authorized submitter - **WHEN** the submitter applies its first immutable version - **THEN** the receipt exposes revision one, the exact normalized body and its canonical digest - **AND** replaying the same version fails without replacing its body or creating a second submission decision

Current proof: Duplicate submission raises REGISTRY_VERSION_EXISTS; final released digest equals initial submitted digest and body; dry-run rolls back first version.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_immutable_submission_three_principals_lifecycle_history_and_revision` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 192; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_cli_dry_run_apply_history_and_authenticated_cloud_principal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 775; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “receipt exposes revision one, exact normalized body ... replay ... without ... second submission decision”: no initial receipt revision/body equality or post-replay event-count assertion; actor uses fictional local identity, not actual cloud authentication.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8365da608a7783b1d73bdca55a666f7a90061130c0d19cb3f4e3b89beba8fa57. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-002-01 — PASS

Claimed role paths for one credential — - **GIVEN** one verified assumed-role credential and its actual IAM RoleId - **WHEN** the caller supplies three different claimed path prefixes for that same role - **THEN** every noncanonical path is rejected and it cannot self-approve or self-release

Current proof: STS/IAM double supplies one RoleId/session; three claimed submitter/reviewer/releaser paths all rejected; independent lifecycle denies same principal approve/release. Software verifier test, not live IAM proof.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_cli_dry_run_apply_history_and_authenticated_cloud_principal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 775; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_immutable_submission_three_principals_lifecycle_history_and_revision` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 192; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 2a248597be732ed002d585c4c22101513d23c9c1972599b2505e905875ead6cf. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-002-02 — PARTIAL

Three authenticated duties release approved material — - **GIVEN** a submission under the named submitter role and an independent reviewer role - **WHEN** the reviewer approves revision one and the independently authenticated releaser releases revision two - **THEN** the active read validates three distinct canonical principals and the same submitted content hash - **AND** the accepted history contains the exact request identity and reason for each decision

Current proof: Distinct local principal lifecycle validates released submitted hash; cloud principal function resolves canonical role using doubled STS/IAM.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_immutable_submission_three_principals_lifecycle_history_and_revision` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 192; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_cli_dry_run_apply_history_and_authenticated_cloud_principal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 775; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “accepted history contains exact request identity and reason for each decision”; no per-event identity/reason comparison. Three named authenticated cloud duties are not integrated through CLI; actual cloud credentials/role exercise is external.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0f493021136e0cc7f263b8f1027106a09d2503aab1a3ebf06cccacf771a9398b. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-003-01 — PARTIAL

Stale release or revoked configuration — - **GIVEN** a reviewed version whose revision changed or whose approval was revoked - **WHEN** an operator releases it using an earlier revision - **THEN** the command fails and customer acquisition remains unavailable

Current proof: Stale revision approval rejected and unreleased version cannot release; revoked configuration closes task capability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_immutable_submission_three_principals_lifecycle_history_and_revision` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 192; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_capabilities_change_with_consent_revision_notice_expiry_and_revoke` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 332; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “operator releases it using an earlier revision”: existing stale-revision attempt is approve, not release after intervening revision/revocation, and no paired acquisition denial assertion for that stale release.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a834525a235d86410f91bcdfbab1e1f07bfd483f84d0d00b839d3924ae2b748a. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-003-02 — PARTIAL

Dry-run, applied renewal and terminal history — - **GIVEN** a valid typed renewal and its complete current dependencies - **WHEN** the CLI runs without --apply - **THEN** it displays the validated result and rolls back all registry changes - **WHEN** three authorized operators submit, approve and release the renewal with --apply - **THEN** the previous active version is atomically retired and both immutable bodies remain in history - **AND** retiring the renewal immediately removes current authority while preserving accepted decisions

Current proof: CLI dry-run rollback, applied initial lifecycle and history display; direct renewal retires old version and preserves body, later revoke closes active authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_cli_dry_run_apply_history_and_authenticated_cloud_principal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 775; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_immutable_submission_three_principals_lifecycle_history_and_revision` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 192; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “CLI [renewal] displays validated result”; “retiring renewal ... preserving accepted decisions”: tests split initial CLI and direct renewal, revoke renewal rather than retire it, and do not compare immutable decision history after retirement.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a428e83fb10d437943ebb3696e8983a128c88e5f5312dd3c15cd58ada7c3349a. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-004-01 — PASS

Changed retention or duration with old proof — - **GIVEN** an approved configuration and qualification for version one - **WHEN** version two changes duration or retention but retains the task material hash and old proof - **THEN** release fails because the qualification does not cover the new submitted version/digest

Current proof: v2 changes max duration while keeping material hash; approve then release raises QUALIFICATION_CONFIGURATION_MISMATCH and exact prior active configuration remains. Duration is the canonical retention-or-duration alternative.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_changed_scope_cannot_reuse_scientific_hash_or_old_qualification` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 239; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f1f5f39a7c8425c8281bb3b188268f60316ece6979a737d06e51b38119460db3. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-004-02 — PARTIAL

Exact reviewed configuration and device tuple — - **GIVEN** approved study and retention versions, an exact configuration proof, and a device/calibration with matching key, hardware, firmware and channel - **WHEN** an independent releaser releases the configuration - **THEN** runtime validation resolves the exact active versions and accepts the matching configuration identity - **AND** its material hash and complete submitted hash remain separately available for acquisition fencing

Current proof: Device tuple exact active dependencies accepted via typed fixture and binding; mismatched firmware/hardware/calibration rejected; separate task authorization exposes submitted hash and scientific hash.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_online_task_start_is_signed_and_old_grant_cannot_survive_envelope_renewal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 375; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “matching [device] configuration identity ... material hash and complete submitted hash ... separately available for acquisition fencing”: device test does not assert both hashes from that exact device configuration runtime authority.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2dbbe311ee9cb848e7fffe79df641b6fa389515d655dccd6263e5988da3fa54b. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-005-01 — PARTIAL

Current approved task collection — - **GIVEN** an active account, current notice and exact consent to an independently released study with approved task configuration - **WHEN** capabilities are requested on a build containing the matching native task adapter - **THEN** task collection is available with its exact public configuration references - **AND** retirement, expiry, changed consent or account generation closes the applicable capability

Current proof: Task available with exact configuration ID after consent; stale consent, missing notice, deleting account, revoked configuration close capability; alcohol expiry boundaries checked.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_capabilities_change_with_consent_revision_notice_expiry_and_revoke` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 332; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_alcohol_configuration_and_calibration_expiry_boundary_preserves_history` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 71; 30 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “retirement, expiry ... or account generation closes applicable [task] capability”: no task capability assertion for retirement, expiry or changed generation. Alcohol dependency expiry does not establish task path or generation behavior.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7bc9f8bc25129f5857a27944ec1c25aa3fcf1836ecae32022d39266af9584ceb. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-005-02 — PASS

Authorized configuration without a shipped adapter — - **GIVEN** current consent and an independently released device configuration with a matching owned binding - **WHEN** its declared transport is absent from the shipped server/client adapter inventory - **THEN** authorization availability and software availability are reported separately - **AND** acquisition is denied with HUMAN_ADAPTER_UNIMPLEMENTED rather than accepting fabricated measurements

Current proof: Current independently approved config and owned binding with absent adapter yields authorization_available=true, software_available=false, available=false, HUMAN_ADAPTER_UNIMPLEMENTED; acquisition resolver refuses. No fabricated measurement accepted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_alcohol_current_dependencies_do_not_manufacture_an_available_adapter` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 98; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 2781f12e91ec28b8426e9d6914dd9a5123a28644cc2e8a0999fc22d503398c4b. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-006-01 — PASS

Approval replaced while a grant is outstanding — - **GIVEN** an issued acquisition grant for one approved configuration envelope - **WHEN** a newly reviewed envelope replaces it before start - **THEN** the old grant cannot start even when the scientific task hash is unchanged

Current proof: Issued grant then v2 envelope duration renewal with same material hash; starting old grant returns CONFIGURATION_APPROVAL_CHANGED.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_online_task_start_is_signed_and_old_grant_cannot_survive_envelope_renewal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 375; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 1ac0fabd5f6a05a0da6c6731925e5d6ba8510a9fb38fac94a898937153725168. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-006-02 — PARTIAL

Current grant starts before an approval retirement — - **GIVEN** a current owned started attempt and an issued grant pinned to the active configuration envelope - **WHEN** start commits while holding the shared registry authority lock - **THEN** the server records its actual start anchor and exact pinned approval identity

Current proof: Actual PG observes registry shared transaction lock blocking retirement; separate HTTP start signs exact configuration submitted hash/context.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_actual_postgresql_retirement_waits_for_current_reference_acceptance_transaction` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 849; 2 current observation(s).
- `services/api/tests/test_operator_governance.py::test_online_task_start_is_signed_and_old_grant_cannot_survive_envelope_renewal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 375; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “server records its actual start anchor and exact pinned approval identity” for start committing under that lock: PG concurrency test reads active_body only; no HTTP start transaction anchor/identity persistence assertion under concurrent retirement.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fe05646557046c48812730196ee3dec9e9b826003eb221dbe7880dbed7879fe2. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-007-01 — PARTIAL

Owned reader starts under current signed authority — - **GIVEN** current independent approvals and an owned signature-proven reader binding in the frozen context - **WHEN** start supplies the exact frozen boot and fresh reader nonce - **THEN** the server emits a verifiable domain-separated token for the approved channel and duration - **AND** feature-only collection has signed raw-recording permission null

Current proof: Real owned device binding challenge/signature and frozen context; wrong boot/no nonce refused; emitted token verified with domain-separated P256 signature, binding/boot/nonce exact and raw permission null; task test verifies approved channel/duration; sign_start body equality independently checked. Hypothetical inventory and fictional keys qualify software only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 543; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_online_task_start_is_signed_and_old_grant_cannot_survive_envelope_renewal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 375; 5 current observation(s).
- `services/api/tests/test_capture_signing.py::test_local_signed_start_is_exact_domain_bound_and_anchor_is_not_replaced` — file SHA `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`, line 37; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “approved channel and duration” in the owned reader start: reader-bound HTTP test asserts binding/boot/nonce/null raw but not token channel/duration against that approved device configuration; task test checks those on a separate task configuration.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a7e8975a9a68ed13941d2eb10480dd5ca6b3058f1da3c622f3b64692794a883f. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-007-02 — PASS

Signing authority fails or unsigned raw choice changes — - **GIVEN** a bound signing key and an issued current acquisition grant - **WHEN** the key is missing, replaced, unavailable or produces an invalid signature - **THEN** readiness or start fails closed and no acquisition authority is published - **WHEN** a caller changes signed raw permission, channel or duration in a valid token - **THEN** the signature fails and the reader cannot acquire under the changed scope

Current proof: Missing/replaced/unavailable/invalid-signature signing authority fails with controlled error; changed signed raw permission causes InvalidSignature. Raw CI firmware log now binds actual compiled production verifier main and its P256/key/domain/material/channel/duration/raw-permission mutation assertions; stdout confirms all negatives passed. This is host software execution, not physical reader qualification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_capture_signing.py::test_missing_anchor_cannot_sign_and_connection_binding_is_idempotent` — file SHA `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`, line 76; 5 current observation(s).
- `services/api/tests/test_capture_signing.py::test_local_private_key_custody_and_retained_identity_fail_closed` — file SHA `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`, line 88; 40 current observation(s).
- `services/api/tests/test_capture_signing.py::test_cloud_signing_provider_failures_are_controlled_retryable_and_publish_no_authority` — file SHA `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`, line 165; 25 current observation(s).
- `services/api/tests/test_capture_signing.py::test_signed_raw_recording_choice_is_not_an_unsigned_start_hint` — file SHA `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`, line 57; 5 current observation(s).
- `firmware/tests/signed_reader_grant_test.cpp::main` — file SHA `f398cef88638601878d2182ed671be8624c14b3dcd9e5c4e1c23041e05d93b48`, line 12; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA bcabf75d9fb06fdb505fff8589936ddf7881eee8465982bf9de228d4688418c5. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-008-01 — PARTIAL

Current optical run retains descriptive evidence — - **GIVEN** an owned started optical authorization under an independently released configuration - **WHEN** the matching actual native run settles with bounded camera/frame evidence - **THEN** the server binds its run and authorization identities and independently checks its arithmetic - **AND** callback-relative response metadata remains separate from physically qualified projection fields

Current proof: Server validator checks literal frame arithmetic, optical identity and deliberately false physical/model qualification; descriptive callback response separate.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_optical_evidence_cannot_relabel_a_different_authorized_attempt_or_acquisition_clock` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 440; 5 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_response_and_scale_reference_match_literal_vector_and_raw_codec` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 174; 5 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_positive_reviewed_config_evidence_is_never_physical_or_model_qualification` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 206; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “matching actual native run settles ... server binds run and authorization identities”: direct literal-fixture validator is not a native run settled through HTTP under independently released optical config; no native-to-server settled receipt binding.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b9ada4e1ccd2e816f80b436b01a41560dc5e4965a327d0f4ffe0c33a99dd80f7. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-008-02 — PASS

Pre-start failure or relabeled camera run — - **GIVEN** a saved arm attempt and a camera that fails before acquisition clocks or frames exist - **WHEN** the client settles a reason-bearing invalid attempt with native evidence absent - **THEN** the server preserves its original arm time and null acquisition features - **WHEN** valid evidence claims another run, authorization or acquisition interval - **THEN** acceptance fails rather than assigning that evidence to the current attempt - **WHEN** an operator subsequently retires or replaces that approval - **THEN** later settlement cannot use the stale grant and no accepted scientific snapshot is silently rewritten

Current proof: HTTP pre-start invalid preserves armed_at, absent native evidence and null acquisition times; forged feature denied. Identity validator denies other run/auth/time. Real typed optical lifecycle prevalidates evidence, retires configuration then HTTPsettlement denied with unchanged arm/revision and prior accepted snapshot/digest.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_prestart_invalid_optical_attempt_retains_arm_lineage_without_invented_camera_evidence` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 457; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_optical_evidence_cannot_relabel_a_different_authorized_attempt_or_acquisition_clock` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 440; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_retired_optical_approval_refuses_later_settlement_without_rewriting_snapshot` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 494; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Fictional software authority and nativefixture, not physical optics qualification.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 04b96616604db1c503235a7a4fb0ee97dbf749a1b118517052effbbaa43c7b79. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-009-01 — PARTIAL

Original device samples are published under current permission — - **GIVEN** exact released configuration, explicit current recording/upload consent and an owned started authorization - **WHEN** the original signed ECG chunks or optical ROI bytes match the accepted acquisition ledger - **THEN** completion records the exact immutable object version, codec and evidence digests before marking the artifact verified - **AND** research eligibility remains separate from raw transport verification

Current proof: HTTP original signed ECG completes verified with immutable version+codec receipt; codec validates accepted evidence digest; ROI verifies frame ledger and false physical proof.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_capture.py::test_http_raw_completion_authenticates_device_chunks_and_keeps_forgery_quarantined` — file SHA `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`, line 635; 10 current observation(s).
- `services/api/tests/test_raw_capture.py::test_original_device_signatures_and_signed_clock_bounds_verify_without_creating_health_values` — file SHA `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`, line 162; 5 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_roi_codec_verification_binds_actual_luminance_native_ledger_and_attempt` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 429; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “completion records ... evidence digests before marking ... verified ... research eligibility remains separate”: HTTP completion asserts version/codec only, not evidence digest or ordering, nor paired research eligibility on verified artifact.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4c60a2e28a11933936f538664dee4d45b6eaad6a64bef92fdf4494bdd7a1c375. Actual current source and raw evidence supply this disposition.

## OTGD-011-OPERATOR-AUTHORITY-009-02 — PARTIAL

Matching file hash contains forged or relabeled samples — - **GIVEN** a raw artifact whose uploaded bytes match its declared file hash and length - **WHEN** a sample signature, signed clock, owner, capture identity, frame digest or approved sample budget is invalid - **THEN** completion fails and the artifact remains quarantined without a verification receipt - **AND** a historical verified state without an owned matching codec receipt cannot authorize raw export

Current proof: HTTP freshly rehashed forged ECG sample remains quarantined with no receipt; validators reject scope/signature/clock/budget/ROI faults; missing/mismatched owned codec receipt blocks raw job validation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_capture.py::test_http_raw_completion_authenticates_device_chunks_and_keeps_forgery_quarantined` — file SHA `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`, line 635; 10 current observation(s).
- `services/api/tests/test_raw_capture.py::test_phone_changes_do_not_authenticate_raw_device_samples` — file SHA `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`, line 288; 60 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_roi_codec_rejects_relabeling_or_changed_binary_content` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 475; 70 current observation(s).
- `services/api/tests/test_raw_export.py::test_verified_status_never_substitutes_for_exact_owned_accepted_codec_receipt` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 749; 25 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “completion fails and artifact remains quarantined without verification receipt” for all owner/capture/frame/budget fault variants: those variants exercise validator only, HTTP state+receipt assertion covers forged sample variant alone.

Prerequisite/evidence type: software_assertion_or_integration_evidence, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 455ddc451599dbeae47365347e854984778c2ee4f96e5a67afb959b9d094f8dd. Actual current source and raw evidence supply this disposition.
