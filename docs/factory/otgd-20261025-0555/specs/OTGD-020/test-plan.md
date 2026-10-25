# OTGD-020: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md`; SHA-256 `7cd3451fd8c13cd25bdc66403e879de3f9fe0e127e3655f2ed40017869916f76`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/tests/native-storage.test.ts` — `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`
- `apps/mobile/tests/serverless-build.test.ts` — `77087c0fe85b1f27039d6a207636478e56b82d227c33fb4928371f4b2b318e6f`
- `apps/mobile/tests/service-boundary.test.ts` — `70b18be9dc9bdc1edfee67e9ad73d525e84bb256db367acfa9ac779ce1686360`
- `infra/test/test_canonical_health.py` — `5ef6623480bf0056aef21d0a97ff2e90c0be15c44003b12bebb6f4d308bc828e`
- `infra/test/test_ci_gates.py` — `82805a98da905f9704f2016c67c726ad10c679f55f548179ed8981cf177f7904`
- `infra/test/test_fargate_template.py` — `7d41cd2239fccafdb4f8ee2b96a81906fbecfa6ada5fd074fca86ac15f02ba06`
- `infra/test/test_serverless_template.py` — `3391a66f5ee3b76b3faa08c3e4c981b81c17d10555eba227b2efc23ca3da9984`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_journal_continuity.py` — `4ca05e80289e4626c0096814050433fc39077912de8e761135d1aea59ca9b6cb`
- `services/api/tests/test_schema_cache.py` — `316bef49cdd9ade7c67fe5cecc22064b19126a553ecd0e6375150458271da90c`
- `services/api/tests/test_storage.py` — `66250af1472d94d2d175a3467e9f4304b80445261538ad85a3bea8210678e27f`
- `services/api/tests/test_worker_health.py` — `ece26d38e5588ebff044ca72d1ba09582066202bc49c0d72bd434d6cdd532334`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-ENV-001 — Fix environment identity in each build

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` / `AND-ENV-001`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-020-AND-ENV-001-01 | QA and production are installed together — **GIVEN** separate configured builds **WHEN** both run on one phone **THEN** they have distinct app identities and local namespaces and QA is visibly labeled. | `infra/test/test_fargate_template.py:313` — test_controller_never_receives_sql_or_application_secret_configuration<br>`infra/test/test_serverless_template.py:188` — test_queue_resource_policies_use_one_resource_per_statement_and_deny_plaintext_for_both_queues | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-020-AND-ENV-001-02 | Cloud service receives local-only configuration — **GIVEN** APP_ENV=prod **WHEN** local authentication or an emulator endpoint is configured **THEN** startup fails before accepting requests. | `infra/test/test_fargate_template.py:313` — test_controller_never_receives_sql_or_application_secret_configuration<br>`apps/mobile/tests/serverless-build.test.ts:5` — longer service deadlines are an explicit cloud build setting | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ENV-002 — Bound startup and preserve local data

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` / `AND-ENV-002`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-020-AND-ENV-002-01 | Phone launches offline — **GIVEN** a usable encrypted store **WHEN** the configuration request times out **THEN** permitted local functions open with an offline state and no fabricated server result. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-020-AND-ENV-002-02 | Store cannot be decrypted — **GIVEN** a missing or invalid local key **WHEN** startup opens storage **THEN** the app reports a storage recovery/reset choice and does not fall back to plaintext storage. | `services/api/tests/test_api.py:371` — test_recovery_cutoff_uses_auth_time_not_refresh_issue_time<br>`apps/mobile/tests/native-storage.test.ts:199` — native account storage fails closed when key storage, cipher support or backup exclusion is unavailable | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ENV-003 — Provide a reproducible LocalStack path

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` / `AND-ENV-003`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-020-AND-ENV-003-01 | Local prerequisites are present — **GIVEN** Docker and an authorized LocalStack activation token **WHEN** the documented local startup command runs **THEN** resources initialize idempotently and a synthetic session reaches a persisted result through the API/worker path. | `services/api/tests/test_worker_health.py:81` — test_health_command_returns_status_only<br>`infra/test/test_canonical_health.py:35` — test_filtered_inspect_never_reads_environment_or_health_log | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-020-AND-ENV-003-02 | LocalStack prerequisite is absent — **GIVEN** no Docker daemon or activation token **WHEN** local integration is requested **THEN** the command fails with a clear prerequisite message and no test report calls a mock execution LocalStack validation. | `services/api/tests/test_worker_health.py:81` — test_health_command_returns_status_only<br>`infra/test/test_canonical_health.py:35` — test_filtered_inspect_never_reads_environment_or_health_log | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ENV-004 — Keep cloud isolation and secrets explicit

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` / `AND-ENV-004`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-020-AND-ENV-004-01 | Synthesized production stack — **GIVEN** complete deployment inputs **WHEN** infrastructure is synthesized and checked **THEN** required encryption, private database/task placement, TLS listener, production capacity, and scoped resource access appear in the template. | `infra/test/test_fargate_template.py:204` — test_database_has_ipv6_access_without_weakened_pause_or_tls_contract<br>`infra/test/test_serverless_template.py:375` — test_unsafe_deployment_inputs_fail_before_cloud_calls | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-020-AND-ENV-004-02 | Secret is omitted — **GIVEN** a required database or identity setting is unavailable **WHEN** the service starts **THEN** readiness fails without logging the secret or accepting unauthenticated fallback traffic. | `infra/test/test_fargate_template.py:204` — test_database_has_ipv6_access_without_weakened_pause_or_tls_contract<br>`apps/mobile/tests/serverless-build.test.ts:5` — longer service deadlines are an explicit cloud build setting | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ENV-005 — Promote immutable verified releases

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` / `AND-ENV-005`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-020-AND-ENV-005-01 | QA release passes its checks — **GIVEN** a tested image digest and compatible schema **WHEN** promoted to production **THEN** production references that digest and records the migration/release evidence. | `infra/test/test_canonical_health.py:27` — test_no_missing_health_running_initializer_failed_migration_or_oneoff_counts<br>`services/api/tests/test_schema_cache.py:56` — test_concurrent_cold_requests_compile_immutable_schema_once | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-020-AND-ENV-005-02 | Migration fails — **GIVEN** a nonzero migration exit **WHEN** deployment automation evaluates the gate **THEN** service rollout stops and the previous deployment remains the rollback target. | `infra/test/test_canonical_health.py:27` — test_no_missing_health_running_initializer_failed_migration_or_oneoff_counts<br>`infra/test/test_fargate_template.py:270` — test_owned_immutable_images_use_ecr_dualstack_endpoints_at_runtime | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ENV-006 — Implement observable recovery boundaries

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` / `AND-ENV-006`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-020-AND-ENV-006-01 | Database is unavailable — **GIVEN** a live API process without a usable database **WHEN** health is checked **THEN** liveness may pass while readiness returns 503 and traffic is not represented as healthy. | `infra/test/test_serverless_template.py:273` — test_web_artifact_contract_and_native_monitoring_do_not_force_idle_database_queries<br>`infra/test/test_fargate_template.py:328` — test_actual_sql_metrics_and_native_health_have_ten_alarms_and_approved_budget | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-020-AND-ENV-006-02 | Backup contains subsequently deleted data — **GIVEN** a restore from an older backup **WHEN** the restore runbook is executed **THEN** deletion tombstones are reapplied before access is reopened and the drill records whether RPO/RTO objectives were achieved. | `apps/mobile/tests/native-storage.test.ts:128` — concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-ENV-007 — Report verification honestly

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-app-environment/spec.md` / `AND-ENV-007`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-020-AND-ENV-007-01 | iOS source exists on a Linux runner — **GIVEN** no Xcode/macOS build toolchain **WHEN** delivery status is generated **THEN** iOS native compilation is recorded as unexecuted rather than inferred from a JavaScript bundle. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |
| OTGD-020-AND-ENV-007-02 | Infrastructure synthesis succeeds without AWS credentials — **GIVEN** a synthesized template but no deployment **WHEN** the release report is written **THEN** it states synthesis passed and QA/prod deployment remains unexecuted. | **NO TEST FOUND for this clause in the inspected mapped test inventory; author a meaningful check or execute the stated review/fixture procedure.** | NOT_RUN: no matching assertion found; execute the linked fixture/manual procedure with its full expected conditions and retain evidence, or implement a meaningful automated test. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Current release provenance assertion audit

Mapped existing cases: OTGD-047-STORE-003-01/02; OTGD-015-CLOUD-DEP-002-01/02; related AND-ENV-005/007.

Assertion adequacy inspected: Read verify_github_gates/verify_gate_file and new test_provenance actual assertion bodies. Both current defaults require CURRENT_REQUIRED_JOBS=FARGATE_REQUIRED_JOBS (14), owned HTTP-client recursion retains selected set; tests reject missing/failure/skipped/cancelled fargate-container-runtime, reject base-only gate file, and verify platform build/serverless admission do not reach signing/cloud boundary. Existing exact-run/latest-attempt/duplicate/foreign/pagination checks retained. Explicit historical13 selectors remain only documented original recovery callers; signed historical receipt projection unchanged and cannot replace live admission.

Remaining limits: HTTP response fixtures prove software refusal only. Actual current remote14 mandatory jobs/run provenance and native artifacts remain pending; baseline38347011315 is historical only and normalized PR wrapper is not trusted-main admission. Logs substantiate focused runs but run-time source manifest absent from author report; do not adopt them as exact frozen-candidate result. Canonical infra gate recorded FAIL (Docker readonly buildx setup + then-missing probe import); secure-SDK follow-up not reached.

### Actual-process interruption probe source audit

Mapped existing cases: Shared platform §§6/10; related OPS-002/003/005/006, RAW-EXP-004/006/007, RECOVERY-001, AND-SYNC-003/005/006, AND-PRIV-005, AND-RES-002.

Assertion adequacy inspected: Read worker_interrupt_probe.py validate_target, child_worker, OwnedChild, kill_case, verify_output, stale_case and budget_case. Exact separate disposable local DB/namespace/queues/buckets; wrappers delegate real production claim/commit/S3/SQS/run_job; only owned spawned PID receives signals; SIGKILL exit and actual barriers verified. Five export kill stages plus result after-claim/after-commit; unchanged outbox and winning fence/attempt/output assertions; version-pinned bytes/hash. SIGSTOP lets real120s lease expire; new generation denies stale output; SIGCONT late writer must lease_lost; real expiry cleanup removes only own versions and preserves neighbor. Real malformed durable work five-claim/backoff and actual five-receive120s DLQ redrive preserve production constants.

Remaining limits: Source inspected only; probe and integration WIP, no real process/recovery execution adopted. Unit harness targeting/barrier tests do not prove actual recovery. No study withdrawal or old-backup/cloud restore inferred from generation transaction. PM must assign isolated fixture setup and run after writer release; all resource mutations PM-only. Workflow timeout must fit real production waits; integration pending.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.
