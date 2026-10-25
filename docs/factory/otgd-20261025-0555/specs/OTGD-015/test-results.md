# OTGD-015: verification results

Canonical: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md`; SHA-256 `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 10 individually identified requirements and 21 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Focused provenance report: `../../reports/provenance-implementation.md` SHA-256 `8d78d5000cbb7d1f08848a3420759a5139e3abdb83eb22f87c01944bb1d4d9f2`. Actual existing /tmp logs inspected:21/58/232-case focused runs show OK, original RED4 failures and canonical infra gate FAIL preserved. Runtime source-manifest binding is incomplete in author report; final raw source-bound gate required. No current remote/native job PASS or release authority adopted.

Independent source assertion audits for this dossier: Current release provenance assertion audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 21 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"NOT_RUN": 1, "PARTIAL": 13, "PASS": 7}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-015-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-015 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md`; SHA256 `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6`.

21 cases, 10 requirements: NOT_RUN 1, PARTIAL 13, PASS 7. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-015-CLOUD-DEP-001-01 — PASS

QA plan is requested — - **GIVEN** a concrete validated QA configuration - **WHEN** qa.py --plan executes - **THEN** it lists infrastructure/code/maintenance/web stages and reports deployment_executed=false.

Current proof: QA parser --plan enters real orchestration; result deployment_executed=false, migration before activation, no preflight/run/web build called. Inspected steps() includes infrastructure/code/maintenance/web stages; wrapper delegates explicit qa environment. No deployment executed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_offline_plan_never_calls_aws_docker_build_or_release_signing` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 491; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA ae19301c217a5d2591598c39465ae49596fa8c82a34fac6f5a876afe17162108. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-001-02 — PASS

Production wrapper receives QA configuration — - **GIVEN** an environment mismatch - **WHEN** the wrapper starts - **THEN** it fails before AWS access or mutation.

Current proof: Production parser with QA config raises Gate in real orchestrator and AWS preflight is never called. Unapproved production source web admission also rejects before its AWS preflight.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_wrong_environment_and_unapproved_production_fail_before_aws` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 497; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4bf6686c7a47d72027cbd03ba961e2271213ad8f0c6db6a092972de2b7d667fd. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-002-01 — PARTIAL

Every required exact-revision gate passes — - **GIVEN** an eligible main/merge-group run and independently trusted signature - **WHEN** release operations execute - **THEN** source/run/attempt/job/image bindings are verified and retained.

Current proof: Mock GitHub latest-attempt proof includes exact source/run/attempt/job IDs, trusted signatures bind proof, image/config revision/digest and QA envelope verified by real crypto.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_provenance.py::test_latest_attempt_requires_every_nested_job_and_aggregate` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 102; 1 current observation(s).
- `infra/test/test_provenance.py::test_production_activation_rechecks_signed_git_and_exact_qa_envelopes` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 330; 1 current observation(s).
- `infra/test/test_provenance.py::test_cloud_image_manifest_and_local_config_must_bind_signed_source` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 382; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- An eligible main/merge-group release run with independently trusted operational signer must retain its release bindings. Current exact-tree draft-PR CI40185247204 passes14 jobs and local7 gates pass, but this is not an eligible authorized deployment/release operation or independent signing authority.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3f96dd671792514cfb6c579f2deb4748d24cade045c05dc2188e3cfe18e5cee5. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-002-02 — PASS

A prior or cancelled run is supplied — - **GIVEN** stale or incomplete evidence - **WHEN** admission executes - **THEN** the operation fails before release authorization.

Current proof: Missing/failed/skipped/cancelled/in-progress/old-attempt/wrong-source jobs reject real verifier; platform build rejects incomplete evidence before login/signing, serverless admission before cloud client/journal. Software release guard only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_provenance.py::test_local_claims_cannot_replace_missing_failed_skipped_or_old_attempt_jobs` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 115; 1 current observation(s).
- `infra/test/test_provenance.py::test_platform_build_rejects_base_only_evidence_before_signing_or_docker` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 192; 1 current observation(s).
- `infra/test/test_provenance.py::test_serverless_admission_rejects_base_only_evidence_before_cloud_operations` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 210; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 95c4a2c04e6d656ef0a75d48f6a23925829e024885dc730c55b5ddfcd11d4b8d. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-003-01 — PARTIAL

Actual approved inputs are present — - **GIVEN** the configured credential chain and resource authority - **WHEN** one environment command executes - **THEN** its actual account/region is verified before infrastructure changes.

Current proof: Preflight SDK-double fixture verifies configured regional engine/capacity/zone selection with matching STS account. Inspected platform.preflight checks STS account before certificate/RDS/ECR operations.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_fargate_deploy.py::test_east1_preflight_requires_actual_engine_capacity_and_zone_metadata` — file SHA `3eabee526bb16d384fa159aca7e26f1a20d530edf0d2d413b14b69d19de47cca`, line 198; 1 current observation(s).
- `infra/test/test_fargate_deploy.py::test_continuation_pins_retained_engine_and_keeps_fargate_budget_when_newer_version_is_available` — file SHA `3eabee526bb16d384fa159aca7e26f1a20d530edf0d2d413b14b69d19de47cca`, line 504; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “actual configured credential chain ... actual account/region verified before infrastructure”: no live credential/ST S/TLS/resource authority or environment deployment; all AWS clients are doubles.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5db6f766a86fcd34cde243db38e90e685b77b3ded1af52d6f77b90a33a00482c. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-003-02 — NOT_RUN

AWS credentials point to another account — - **GIVEN** an STS mismatch - **WHEN** preflight executes - **THEN** no target deployment continues.

Current proof: Actual SDK endpoint resolution executes without network; inspected platform.py:75 raises on STS account mismatch.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_cloud_endpoints.py::test_identity_and_mutation_clients_ignore_global_service_and_profile_endpoints` — file SHA `786b0d3537e333ffa9d9114c7d946ef8aebfed4213702e7816b2f8cb47726bc4`, line 13; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “STS mismatch ... preflight ... no target deployment continues”: no executed QA/prod preflight wrong-account STS response with zero subsequent mutation assertion; plan cost/environment tests do not exercise that branch.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA efa435aa3a672a0a9f765a632faf005b3a9eb5bb090b1e82ef8fe038758ecc0e. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-003-03 — PASS

Local emulation endpoint settings are inherited — - **GIVEN** global, service-specific or profile endpoint overrides - **WHEN** cloud identity or mutation clients are constructed - **THEN** their endpoints resolve to AWS and explicit endpoint overrides are rejected.

Current proof: Real botocore SDK resolves STS/ECS to configured-region AWS despite global/service/profile endpoint overrides; unguarded controls resolve invalid endpoints; explicit endpoint_url rejected. Child environment strips endpoint variables and forces ignore true. No credential/network operations executed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_cloud_endpoints.py::test_identity_and_mutation_clients_ignore_global_service_and_profile_endpoints` — file SHA `786b0d3537e333ffa9d9114c7d946ef8aebfed4213702e7816b2f8cb47726bc4`, line 13; 1 current observation(s).
- `infra/test/test_cloud_endpoints.py::test_child_processes_drop_endpoints_and_force_configured_endpoint_ignore` — file SHA `786b0d3537e333ffa9d9114c7d946ef8aebfed4213702e7816b2f8cb47726bc4`, line 37; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b8da5006c1e6f8dccae52fcd50e3072bf6ac74f342bb7d806f388a34bd9841b2. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-004-01 — PARTIAL

First empty environment is established — - **GIVEN** explicit establish-new and no admitted data - **WHEN** bootstrap/migration succeed - **THEN** actual receipts qualify for the later activation gate.

Current proof: Maintenance launcher reads mocked ECS stopped/zero-exit/exact-image task and source-bound receipt, forwards establish-new to bootstrap, writes bootstrap receipt; modeled lifecycle orders bootstrap/migrate/admission before activation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_fargate_deploy.py::test_maintenance_requires_actual_zero_exit_reviewed_digest_and_source_bound_receipt` — file SHA `3eabee526bb16d384fa159aca7e26f1a20d530edf0d2d413b14b69d19de47cca`, line 957; 1 current observation(s).
- `infra/test/test_serverless_deploy.py::test_fresh_runtime_bootstraps_and_migrates_stopped_before_activation` — file SHA `4a0e05d2bfc18ceb2b584ada8177793ffa2649a12ec1289fcfe92c1937683ef6`, line 767; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “first empty environment ... actual receipts qualify”: ECS, bootstrap/migration and database emptiness are simulated; no actual stopped environment, retained journal establishment or verified admission task receipt.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9d6577cdff46e9d3715c6ab82f770f25fff260e6dc19cc9f531488c1c84a3f08. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-004-02 — PASS

Migration or fresh admission verification fails — - **GIVEN** failed maintenance, absent authority or a stale/mismatching admission receipt - **WHEN** deployment reaches the failure - **THEN** activation and web publication do not execute and no success receipt is fabricated.

Current proof: Injected migration stops lifecycle at migrate with neither web build/publish nor activation; verify-admission stage failure writes failed journal/no final deployment receipt. Fresh-admission validator rejects stale/time/no-op authority. Software stop-before-enable behavior verified.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_failed_migration_never_activates_or_uploads_web` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 506; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_partial_failures_journal_completed_stages_without_inferred_rollback` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 524; 1 current observation(s).
- `infra/test/test_maintenance.py::test_activation_requires_fresh_exact_independent_admission_task` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 72; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA e4ab566bdcea4d0e9178cbcd357fad0145028342e37ad9a2397df6a24f16ee89. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-005-01 — PARTIAL

Worker dependencies make useful progress — - **GIVEN** dispatcher/cleanup/both consumers qualify - **WHEN** ECS reports the worker container HEALTHY - **THEN** publication may proceed after the remaining gates.

Current proof: Worker health refuses UNKNOWN progress; separate mocked Fargate observation accepts healthy owned runtime and actual app-config DTO.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_running_process_without_worker_progress_never_qualifies` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 519; 1 current observation(s).
- `infra/test/test_fargate_deploy.py::test_actual_app_config_dto_passes_auth_identity_and_rejects_wrong_client_or_old_oauth_key` — file SHA `3eabee526bb16d384fa159aca7e26f1a20d530edf0d2d413b14b69d19de47cca`, line 1027; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “dispatcher/cleanup/both consumers qualify ... actual ECS HEALTHY ... publication may proceed”: no real worker progress/consumer evidence tied to an actual ECS task and admitted public rollout; unrelated cost tests are not adopted.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f9521570f9f2aa73f561b457ec281d467bdde080f7eb2e3b36cd79c571134463. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-005-02 — PARTIAL

A worker process runs without qualifying progress — - **GIVEN** UNKNOWN/unhealthy worker status - **WHEN** the bounded health deadline expires - **THEN** public enablement fails and is not called successful deployment.

Current proof: Bounded UNKNOWN-health fixture reaches601 seconds and raises Gate; process RUNNING alone is insufficient.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_running_process_without_worker_progress_never_qualifies` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 519; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “public enablement fails ... not called successful deployment”: direct health-helper test does not run one-shot orchestration with UNKNOWN deadline and assert zero web publish/final receipt; negative health gate exists but end-to-end software effect remains unasserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4983d9a9ff092de4341b57fa5a3f30d83693482ae1a257c34e16016672f74801. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-006-01 — PARTIAL

Approved QA is promoted — - **GIVEN** source service/web records and actual protected QA evidence - **WHEN** the authority signs and production admission runs - **THEN** production preserves the image/source and binds its separately configured web artifact to the approved QA envelope.

Current proof: Real signatures bind production image/source and exact QA envelope; source-web admission requires artifact hash plus separate protected customer-results URL; modeled prod web build includes source QA web envelope.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_provenance.py::test_production_activation_rechecks_signed_git_and_exact_qa_envelopes` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 330; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_production_requires_results_reference_separate_from_artifact_binding` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 547; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_each_signed_environment_export_rebuilds_stale_hosted_metro_cache` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 85; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “actual protected QA evidence ... promoted production ... separately configured web artifact”: fixtures invent QA probe references and double source-web verification/exporter; no operational QA signed customer run or actual production promotion.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7dbef89b20ac67e663c40d87dec4269150c2d6c56d7ae0713767ef511c370d6b. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-006-02 — PARTIAL

Web evidence refers to another artifact — - **GIVEN** a foreign/missing web digest or expired QA approval - **WHEN** production starts - **THEN** it fails before target deployment.

Current proof: Expired QA approval rejected by real validator; source-web admission refuses absent separate results reference.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_production_requires_results_reference_separate_from_artifact_binding` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 547; 1 current observation(s).
- `infra/test/test_provenance.py::test_qa_approval_expiry_future_execution_and_non_utc_are_rejected` — file SHA `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`, line 309; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “foreign/missing web digest ... fails before target deployment”: existing source-web test uses the correct artifact digest and fails for missing RESULTS reference; no wrong/missing artifact digest production-admission test with zero target mutations assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bbd18b2d6c6ed0d79ce8c44cc90ae747f834597e7bd12a69536c41c860e6ba95. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-007-01 — PARTIAL

A valid public subdomain is registered — - **GIVEN** a deployed matching distribution and issued TLS - **WHEN** apply is explicitly requested - **THEN** one CNAME targets that distribution and its actual change is awaited for at most ten minutes.

Current proof: SDK-double apply sends one atomic CREATE to exact distribution, calls waiter; source sets600-second deadline and late601 success refused.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_plan_has_no_dns_mutation_and_apply_waits_for_actual_change` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 429; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_late_dns_success_is_refused_without_claiming_rollback` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 450; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “actual change awaited ... deployed distribution and issued TLS”: live Route53/ACM/CloudFront not executed; fixture waiter success is not real propagation.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 940e68706026d049fefecf774cfe83d2904fbfd25fc90a4cf5a4be9074e45f67. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-007-02 — PASS

Caller supplies apex, foreign zone or target — - **GIVEN** a mismatching zone/alias/certificate/record - **WHEN** validation executes - **THEN** no DNS mutation occurs.

Current proof: Real admission given SDK-double apex/foreign/private zone, pending TLS, absent alias, foreign/conflicting target or disabled/misbound distribution raises Gate; Route53 change method never called in every mutation. Scoped software refusal only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 474; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_disabled_foreign_origin_or_non_sigv4_distribution_cannot_publish_dns` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 457; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 7827692bc77de214832717dd175ae8cf532608f70f99d2ab7ec2c286a7c41672. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-008-01 — PARTIAL

An operator repeats deployment — - **GIVEN** prior reviewed records - **WHEN** another invocation starts - **THEN** a separate attempt retains earlier evidence and same-prefix object conflicts fail closed.

Current proof: Failure journal preserves completed stage receipt hashes under private attempt path; immutable object conflict rejects.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_partial_failures_journal_completed_stages_without_inferred_rollback` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 524; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_conflicting_immutable_object_and_asset_upload_failure_block_entrypoint` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 209; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “another invocation ... separate attempt retains earlier evidence”: test gives a new TemporaryDirectory for each invocation and never repeats the same work-dir with prior reviewed records, so preservation across retry remains unasserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fe0bbd402d40301a3119c9ad62c4514e1ffcc7a41ebea1fef2084da956ae6878. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-008-02 — PARTIAL

Public access or invalidation fails — - **GIVEN** incomplete delivery - **WHEN** the bounded operation fails - **THEN** no verified-access receipt is written and cloud acceptance remains unresolved.

Current proof: Injected publish-web failure leaves no deployment.json and journal says failed/no rollback; unprotected history makes public probe throw.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_web_deployment.py::test_partial_failures_journal_completed_stages_without_inferred_rollback` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 524; 1 current observation(s).
- `infra/test/test_web_deployment.py::test_navigation_cannot_omit_required_policy_when_index_is_secure` — file SHA `e14f26278041db1bb3f5c34cf42c4f7a3f752a4aaabcaa4d15d2aaeac11aa4e1`, line 385; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “public access or invalidation ... bounded operation ... no verified-access receipt”: no one-shot failure injection at verify-public-access or CloudFront invalidation waiter with final receipt absence asserted. Separate helper/pub-stage failures do not execute those exact branches.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d4877f22f83ec9ab17448c5860813f7252f21b7eef67d46b753f02f11c5c785d. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-009-01 — PARTIAL

An authorized operator validates registry evidence — - **GIVEN** an approved private operator host with the actual named role and protected database credentials - **WHEN** the typed CLI validates the corresponding command - **THEN** STS/IAM identity and database authority are verified independently of participant API access.

Current proof: Real typed CLI lifecycle and principal verifier distinguish fictional local vs canonical mocked STS/IAM role; application database maintenance authority checks refuse fake app/superuser context.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_cli_dry_run_apply_history_and_authenticated_cloud_principal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 775; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “approved private operator host ... actual named role ... protected database credentials ... verified independently”: no actual private operator access/assigned roles/admin credential execution. No participant API role or fixture is treated as real operator evidence.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9e22dbdc5dd2e258f155c8d05eb7a486f5b0656a10d8206c67d556703f16a888. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-009-02 — PARTIAL

A deployed application task attempts an approval — - **GIVEN** a runtime database/task identity - **WHEN** it attempts to administer or impersonate a registry operator - **THEN** runtime write/trust permissions do not authorize the operation and no approval is invented.

Current proof: Application maintenance context rejected in operator CLI boundary; inspected CDK role trust has three MFA roles, no service principal, narrow scopes; postgres_roles.py contains runtime authority-write denial assertions.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_cli_dry_run_apply_history_and_authenticated_cloud_principal` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 775; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual deployed runtime database/task write/trust permissions must refuse unauthorized operational authority. Current local PostgreSQL role and LocalStack checks pass, but deployed IAM/task-role impersonation and target database write denial are not executed.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c9c3fd3f9da893522c5df8f340b0df6f622f3c6f42c9ba4505406165371fc401. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-010-01 — PARTIAL

Maintenance completes with current independent authority — - **GIVEN** migration and required recovery have completed with services stopped - **WHEN** the exact pinned admission task verifies journal/control versions and database barriers - **THEN** its fresh actual ECS receipt may qualify activation alongside the other release gates.

Current proof: Receipt validator accepts fresh exact recovery_authority command with matching modeled ECS task, source/image/container identity; maintenance mutations/time offsets refused.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_maintenance.py::test_activation_requires_fresh_exact_independent_admission_task` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 72; 1 current observation(s).
- `infra/test/test_maintenance.py::test_exact_task_definition_container_command_and_receipt_required` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 39; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “exact pinned admission task verifies journal/control/database ... fresh actual ECS receipt qualifies activation”: mock task metadata and direct helper success do not execute recovery_authority in stopped AWS environment or activate using that actual receipt.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b3797c172700c1f245666898d65b5d9964f27f645fb9ae9886840ba255dd9771. Actual current source and raw evidence supply this disposition.

## OTGD-015-CLOUD-DEP-010-02 — PASS

Admission proof is stale or uses a no-op command — - **GIVEN** stale completion, mismatching bindings or a command that only mentions the module - **WHEN** activation verifies the receipt against ECS - **THEN** services are not activated using that evidence.

Current proof: Real verifier rejects old completion, receipt/ECS time mismatch, future completion, fake python -c command merely mentioning module, wrong account/region/source/image/task/container/overrides. Platform activation invokes this gate before enabling services, so rejected proof cannot authorize activation. Software authority guard only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_maintenance.py::test_activation_requires_fresh_exact_independent_admission_task` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 72; 1 current observation(s).
- `infra/test/test_maintenance.py::test_exact_task_definition_container_command_and_receipt_required` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 39; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 919e8ee2a52ff1416920f2e642270b44f32a4b1e5a208ac364fde1eab3c1d3be. Actual current source and raw evidence supply this disposition.
