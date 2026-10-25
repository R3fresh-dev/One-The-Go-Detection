# OTGD-015: verification plan

Canonical: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md`; SHA-256 `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `infra/test/test_deployment_cli.py` — `136f38dd76a17b8d342965735bb430862c823a1fb0dadfd5dd3ecd61f121a637`
- `infra/test/test_fargate_deploy.py` — `99970d95bab530bf235f2f53997c76b9ef96cf833c5051e3c1f6fab3707ab559`
- `infra/test/test_maintenance.py` — `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`
- `infra/test/test_provenance.py` — `996ead63b1f3ae3999aa31d81e3de893bbc50b62bfaac6e2a69f88a968d5f6a1`
- `infra/test/test_release.py` — `3013213897c8f1721e0f28a2c4610f18b48cb46ed6a5f5900ebb4495f3e3f9d5`
- `infra/test/test_serverless_deploy.py` — `2df73b06df3ecd0153d07b1bae18ff6636e8dcd745eb72992158404ec092a784`
- `infra/test/test_web_deployment.py` — `e0fbb440ac1b32d67b389b1261d3f6f8360e224793c8c4ad94809ea03fabb2d1`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### CLOUD-DEP-001 — Provide separate environment entry points

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-001`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-001-01 | QA plan is requested — **GIVEN** a concrete validated QA configuration **WHEN** qa.py --plan executes **THEN** it lists infrastructure/code/maintenance/web stages and reports deployment_executed=false. | `infra/test/test_web_deployment.py:413` — test_offline_plan_never_calls_aws_docker_build_or_release_signing<br>`infra/test/test_fargate_deploy.py:54` — test_plan_reconciles_official_prices_without_constructing_an_aws_session | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-001-02 | Production wrapper receives QA configuration — **GIVEN** an environment mismatch **WHEN** the wrapper starts **THEN** it fails before AWS access or mutation. | `infra/test/test_web_deployment.py:413` — test_offline_plan_never_calls_aws_docker_build_or_release_signing<br>`infra/test/test_fargate_deploy.py:54` — test_plan_reconciles_official_prices_without_constructing_an_aws_session | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-002 — Admit exact source and live release gates

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-002`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-002-01 | Every required exact-revision gate passes — **GIVEN** an eligible main/merge-group run and independently trusted signature **WHEN** release operations execute **THEN** source/run/attempt/job/image bindings are verified and retained. | `infra/test/test_provenance.py:115` — test_local_claims_cannot_replace_missing_failed_skipped_or_old_attempt_jobs<br>`infra/test/test_serverless_deploy.py:249` — test_missing_or_failed_gate_evidence_precedes_every_aws_operation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-002-02 | A prior or cancelled run is supplied — **GIVEN** stale or incomplete evidence **WHEN** admission executes **THEN** the operation fails before release authorization. | `infra/test/test_provenance.py:115` — test_local_claims_cannot_replace_missing_failed_skipped_or_old_attempt_jobs<br>`infra/test/test_serverless_deploy.py:249` — test_missing_or_failed_gate_evidence_precedes_every_aws_operation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-003 — Orchestrate infrastructure and code with actual inputs

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-003`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-003-01 | Actual approved inputs are present — **GIVEN** the configured credential chain and resource authority **WHEN** one environment command executes **THEN** its actual account/region is verified before infrastructure changes. | `infra/test/test_fargate_deploy.py:145` — test_regional_plan_binds_all_three_cost_components_without_credentials<br>`infra/test/test_web_deployment.py:42` — test_browser_build_environment_retains_transport_settings_without_deploy_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-003-02 | AWS credentials point to another account — **GIVEN** an STS mismatch **WHEN** preflight executes **THEN** no target deployment continues. | `infra/test/test_fargate_deploy.py:145` — test_regional_plan_binds_all_three_cost_components_without_credentials<br>`infra/test/test_web_deployment.py:42` — test_browser_build_environment_retains_transport_settings_without_deploy_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-003-03 | Local emulation endpoint settings are inherited — **GIVEN** global, service-specific or profile endpoint overrides **WHEN** cloud identity or mutation clients are constructed **THEN** their endpoints resolve to AWS and explicit endpoint overrides are rejected. | `infra/test/test_web_deployment.py:42` — test_browser_build_environment_retains_transport_settings_without_deploy_credentials<br>`infra/test/test_fargate_deploy.py:145` — test_regional_plan_binds_all_three_cost_components_without_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-004 — Complete maintenance before enablement

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-004`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-004-01 | First empty environment is established — **GIVEN** explicit establish-new and no admitted data **WHEN** bootstrap/migration succeed **THEN** actual receipts qualify for the later activation gate. | `infra/test/test_fargate_deploy.py:852` — test_either_stopped_database_verification_failure_blocks_bootstrap_migration_and_activation<br>`infra/test/test_serverless_deploy.py:766` — test_failed_gate_readmission_preserves_stopped_runtime_and_recovery_journal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-004-02 | Migration or fresh admission verification fails — **GIVEN** failed maintenance, absent authority or a stale/mismatching admission receipt **WHEN** deployment reaches the failure **THEN** activation and web publication do not execute and no success receipt is fabricated. | `infra/test/test_fargate_deploy.py:852` — test_either_stopped_database_verification_failure_blocks_bootstrap_migration_and_activation<br>`infra/test/test_maintenance.py:72` — test_activation_requires_fresh_exact_independent_admission_task | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-005 — Require actual healthy activation

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-005`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-005-01 | Worker dependencies make useful progress — **GIVEN** dispatcher/cleanup/both consumers qualify **WHEN** ECS reports the worker container HEALTHY **THEN** publication may proceed after the remaining gates. | `infra/test/test_web_deployment.py:441` — test_running_process_without_worker_progress_never_qualifies<br>`infra/test/test_fargate_deploy.py:83` — test_selected_and_maximum_capacity_prices_both_require_reconciled_line_items | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-005-02 | A worker process runs without qualifying progress — **GIVEN** UNKNOWN/unhealthy worker status **WHEN** the bounded health deadline expires **THEN** public enablement fails and is not called successful deployment. | `infra/test/test_web_deployment.py:441` — test_running_process_without_worker_progress_never_qualifies<br>`infra/test/test_serverless_deploy.py:281` — test_initial_recovery_cannot_be_used_for_routine_deployment | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-006 — Bind production to tested QA service and web evidence

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-006`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-006-01 | Approved QA is promoted — **GIVEN** source service/web records and actual protected QA evidence **WHEN** the authority signs and production admission runs **THEN** production preserves the image/source and binds its separately configured web artifact to the approved QA envelope. | `infra/test/test_web_deployment.py:469` — test_production_requires_results_reference_separate_from_artifact_binding<br>`infra/test/test_provenance.py:382` — test_cloud_image_manifest_and_local_config_must_bind_signed_source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-006-02 | Web evidence refers to another artifact — **GIVEN** a foreign/missing web digest or expired QA approval **WHEN** production starts **THEN** it fails before target deployment. | `infra/test/test_web_deployment.py:469` — test_production_requires_results_reference_separate_from_artifact_binding<br>`infra/test/test_release.py:65` — test_signed_digest_bound_to_account_environment_and_source | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-007 — Register only the exact deployed UI CNAME

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-007`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-007-01 | A valid public subdomain is registered — **GIVEN** a deployed matching distribution and issued TLS **WHEN** apply is explicitly requested **THEN** one CNAME targets that distribution and its actual change is awaited for at most ten minutes. | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed<br>`infra/test/test_fargate_deploy.py:330` — test_existing_east_redeploy_preserves_physical_zone_pair_without_ohio_repair_or_new_journal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-007-02 | Caller supplies apex, foreign zone or target — **GIVEN** a mismatching zone/alias/certificate/record **WHEN** validation executes **THEN** no DNS mutation occurs. | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed<br>`infra/test/test_fargate_deploy.py:330` — test_existing_east_redeploy_preserves_physical_zone_pair_without_ohio_repair_or_new_journal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-008 — Preserve immutable attempts and report actual checks

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-008`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-008-01 | An operator repeats deployment — **GIVEN** prior reviewed records **WHEN** another invocation starts **THEN** a separate attempt retains earlier evidence and same-prefix object conflicts fail closed. | `infra/test/test_web_deployment.py:396` — test_apex_foreign_private_zone_unready_tls_alias_and_existing_record_conflicts_fail_closed<br>`infra/test/test_fargate_deploy.py:939` — test_maintenance_requires_actual_zero_exit_reviewed_digest_and_source_bound_receipt | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-008-02 | Public access or invalidation fails — **GIVEN** incomplete delivery **WHEN** the bounded operation fails **THEN** no verified-access receipt is written and cloud acceptance remains unresolved. | `infra/test/test_web_deployment.py:199` — test_https_asset_deep_link_readiness_checks_do_not_claim_signed_in_acceptance<br>`infra/test/test_serverless_deploy.py:100` — test_explicit_success_receipt_remains_json_when_subprocesses_print_build_diagnostics | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-009 — Provision distinct registry operator authority without assigning approvals

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-009`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-009-01 | An authorized operator validates registry evidence — **GIVEN** an approved private operator host with the actual named role and protected database credentials **WHEN** the typed CLI validates the corresponding command **THEN** STS/IAM identity and database authority are verified independently of participant API access. | `infra/test/test_maintenance.py:39` — test_exact_task_definition_container_command_and_receipt_required<br>`infra/test/test_fargate_deploy.py:145` — test_regional_plan_binds_all_three_cost_components_without_credentials | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-009-02 | A deployed application task attempts an approval — **GIVEN** a runtime database/task identity **WHEN** it attempts to administer or impersonate a registry operator **THEN** runtime write/trust permissions do not authorize the operation and no approval is invented. | `infra/test/test_serverless_deploy.py:981` — test_runtime_error_sends_type_without_event_or_exception_secret | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CLOUD-DEP-010 — Require fresh independent admission evidence

Normative acceptance source: `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md` / `CLOUD-DEP-010`.

Prerequisites and limits: BLOCKED external release: no authorized actual QA/prod deployment, AWS IAM/KMS/private-network/public CloudFront/TLS/DNS and independently signed QA evidence. SDK doubles/template assertions are software evidence only.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-015-CLOUD-DEP-010-01 | Maintenance completes with current independent authority — **GIVEN** migration and required recovery have completed with services stopped **WHEN** the exact pinned admission task verifies journal/control versions and database barriers **THEN** its fresh actual ECS receipt may qualify activation alongside the other release gates. | `infra/test/test_maintenance.py:72` — test_activation_requires_fresh_exact_independent_admission_task<br>`infra/test/test_fargate_deploy.py:852` — test_either_stopped_database_verification_failure_blocks_bootstrap_migration_and_activation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-015-CLOUD-DEP-010-02 | Admission proof is stale or uses a no-op command — **GIVEN** stale completion, mismatching bindings or a command that only mentions the module **WHEN** activation verifies the receipt against ECS **THEN** services are not activated using that evidence. | `infra/test/test_maintenance.py:72` — test_activation_requires_fresh_exact_independent_admission_task<br>`infra/test/test_fargate_deploy.py:200` — test_recovery_session_uses_same_credentials_and_never_selects_another_region | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Current release provenance assertion audit

Mapped existing cases: OTGD-047-STORE-003-01/02; OTGD-015-CLOUD-DEP-002-01/02; related AND-ENV-005/007.

Assertion adequacy inspected: Read verify_github_gates/verify_gate_file and new test_provenance actual assertion bodies. Both current defaults require CURRENT_REQUIRED_JOBS=FARGATE_REQUIRED_JOBS (14), owned HTTP-client recursion retains selected set; tests reject missing/failure/skipped/cancelled fargate-container-runtime, reject base-only gate file, and verify platform build/serverless admission do not reach signing/cloud boundary. Existing exact-run/latest-attempt/duplicate/foreign/pagination checks retained. Explicit historical13 selectors remain only documented original recovery callers; signed historical receipt projection unchanged and cannot replace live admission.

Remaining limits: HTTP response fixtures prove software refusal only. Actual current remote14 mandatory jobs/run provenance and native artifacts remain pending; baseline38347011315 is historical only and normalized PR wrapper is not trusted-main admission. Logs substantiate focused runs but run-time source manifest absent from author report; do not adopt them as exact frozen-candidate result. Canonical infra gate recorded FAIL (Docker readonly buildx setup + then-missing probe import); secure-SDK follow-up not reached.


## Final corrected source evidence — e89897cc852a

# OTGD-015 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/cloud-deployment-customer-access/specs/cloud-release-orchestration/spec.md`; SHA256 `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-015/test-plan.md`. External review artifact only; PM controls import.

All 21 stable cases / 10 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-015-CLOUD-DEP-001-01 | QA plan is requested — - **GIVEN** a concrete validated QA configuration - **WHEN** qa.py --plan executes - **THEN** it lists infrastructure/code/maintenance/web stages and reports deployment_executed=false. | PASS |
| OTGD-015-CLOUD-DEP-001-02 | Production wrapper receives QA configuration — - **GIVEN** an environment mismatch - **WHEN** the wrapper starts - **THEN** it fails before AWS access or mutation. | PASS |
| OTGD-015-CLOUD-DEP-002-01 | Every required exact-revision gate passes — - **GIVEN** an eligible main/merge-group run and independently trusted signature - **WHEN** release operations execute - **THEN** source/run/attempt/job/image bindings are verified and retained. | PARTIAL |
| OTGD-015-CLOUD-DEP-002-02 | A prior or cancelled run is supplied — - **GIVEN** stale or incomplete evidence - **WHEN** admission executes - **THEN** the operation fails before release authorization. | PASS |
| OTGD-015-CLOUD-DEP-003-01 | Actual approved inputs are present — - **GIVEN** the configured credential chain and resource authority - **WHEN** one environment command executes - **THEN** its actual account/region is verified before infrastructure changes. | PARTIAL |
| OTGD-015-CLOUD-DEP-003-02 | AWS credentials point to another account — - **GIVEN** an STS mismatch - **WHEN** preflight executes - **THEN** no target deployment continues. | NOT_RUN |
| OTGD-015-CLOUD-DEP-003-03 | Local emulation endpoint settings are inherited — - **GIVEN** global, service-specific or profile endpoint overrides - **WHEN** cloud identity or mutation clients are constructed - **THEN** their endpoints resolve to AWS and explicit endpoint overrides are rejected. | PASS |
| OTGD-015-CLOUD-DEP-004-01 | First empty environment is established — - **GIVEN** explicit establish-new and no admitted data - **WHEN** bootstrap/migration succeed - **THEN** actual receipts qualify for the later activation gate. | PARTIAL |
| OTGD-015-CLOUD-DEP-004-02 | Migration or fresh admission verification fails — - **GIVEN** failed maintenance, absent authority or a stale/mismatching admission receipt - **WHEN** deployment reaches the failure - **THEN** activation and web publication do not execute and no success receipt is fabricated. | PASS |
| OTGD-015-CLOUD-DEP-005-01 | Worker dependencies make useful progress — - **GIVEN** dispatcher/cleanup/both consumers qualify - **WHEN** ECS reports the worker container HEALTHY - **THEN** publication may proceed after the remaining gates. | PARTIAL |
| OTGD-015-CLOUD-DEP-005-02 | A worker process runs without qualifying progress — - **GIVEN** UNKNOWN/unhealthy worker status - **WHEN** the bounded health deadline expires - **THEN** public enablement fails and is not called successful deployment. | PARTIAL |
| OTGD-015-CLOUD-DEP-006-01 | Approved QA is promoted — - **GIVEN** source service/web records and actual protected QA evidence - **WHEN** the authority signs and production admission runs - **THEN** production preserves the image/source and binds its separately configured web artifact to the approved QA envelope. | PARTIAL |
| OTGD-015-CLOUD-DEP-006-02 | Web evidence refers to another artifact — - **GIVEN** a foreign/missing web digest or expired QA approval - **WHEN** production starts - **THEN** it fails before target deployment. | PARTIAL |
| OTGD-015-CLOUD-DEP-007-01 | A valid public subdomain is registered — - **GIVEN** a deployed matching distribution and issued TLS - **WHEN** apply is explicitly requested - **THEN** one CNAME targets that distribution and its actual change is awaited for at most ten minutes. | PARTIAL |
| OTGD-015-CLOUD-DEP-007-02 | Caller supplies apex, foreign zone or target — - **GIVEN** a mismatching zone/alias/certificate/record - **WHEN** validation executes - **THEN** no DNS mutation occurs. | PASS |
| OTGD-015-CLOUD-DEP-008-01 | An operator repeats deployment — - **GIVEN** prior reviewed records - **WHEN** another invocation starts - **THEN** a separate attempt retains earlier evidence and same-prefix object conflicts fail closed. | PARTIAL |
| OTGD-015-CLOUD-DEP-008-02 | Public access or invalidation fails — - **GIVEN** incomplete delivery - **WHEN** the bounded operation fails - **THEN** no verified-access receipt is written and cloud acceptance remains unresolved. | PARTIAL |
| OTGD-015-CLOUD-DEP-009-01 | An authorized operator validates registry evidence — - **GIVEN** an approved private operator host with the actual named role and protected database credentials - **WHEN** the typed CLI validates the corresponding command - **THEN** STS/IAM identity and database authority are verified independently of participant API access. | PARTIAL |
| OTGD-015-CLOUD-DEP-009-02 | A deployed application task attempts an approval — - **GIVEN** a runtime database/task identity - **WHEN** it attempts to administer or impersonate a registry operator - **THEN** runtime write/trust permissions do not authorize the operation and no approval is invented. | PARTIAL |
| OTGD-015-CLOUD-DEP-010-01 | Maintenance completes with current independent authority — - **GIVEN** migration and required recovery have completed with services stopped - **WHEN** the exact pinned admission task verifies journal/control versions and database barriers - **THEN** its fresh actual ECS receipt may qualify activation alongside the other release gates. | PARTIAL |
| OTGD-015-CLOUD-DEP-010-02 | Admission proof is stale or uses a no-op command — - **GIVEN** stale completion, mismatching bindings or a command that only mentions the module - **WHEN** activation verifies the receipt against ECS - **THEN** services are not activated using that evidence. | PASS |
