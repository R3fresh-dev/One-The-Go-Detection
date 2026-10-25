# OTGD-016: verification plan

Canonical: `openspec/changes/independent-recovery-admission/specs/recovery-authority/spec.md`; SHA-256 `430fe7dfbfdb117add502c5632150690905d94b3dcb42ddc892bf1e8943f273c`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `infra/test/test_recovery.py` — `598881481a5ab8561446d64b3d949c8f883f52ee4d1d9cc3120a909a383c737c`
- `services/api/tests/test_identity_barriers.py` — `79480e9dde91c88207e1f10675e1a30f1a5e06e6d7df10cdc8c07c4d70fc15d2`
- `services/api/tests/test_journal_continuity.py` — `4ca05e80289e4626c0096814050433fc39077912de8e761135d1aea59ca9b6cb`
- `services/api/tests/test_recovery_authority.py` — `8729463f12702d5da5850ce2436f24c05389a14ed556348f683525e9508bf236`
- `services/api/tests/test_recovery_scopes.py` — `3783cfcb8a1e80662e828d51356a5f7037d9b40468a3451a8b3e8f1960f63ad1`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### RECOVERY-001 — Independent retained admission

Normative acceptance source: `openspec/changes/independent-recovery-admission/specs/recovery-authority/spec.md` / `RECOVERY-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-016-RECOVERY-001-01 | Consistent retained authority — **WHEN** the database matches all pinned retained control, identity, generation, deletion and recovery evidence **THEN** ordinary service admission may proceed subject to current participant and study authority | `services/api/tests/test_recovery_authority.py:489` — test_worker_claim_and_commit_refuse_retained_activation_missing_in_database<br>`services/api/tests/test_journal_continuity.py:144` — test_retained_database_never_automatically_adopts_journal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-016-RECOVERY-001-02 | Stale restored active row — **WHEN** a retained deletion or recovery activation conflicts with an active database row or its queued job **THEN** API and worker refuse new data work before commit, including when the database recovery row is absent | `services/api/tests/test_recovery_authority.py:489` — test_worker_claim_and_commit_refuse_retained_activation_missing_in_database<br>`services/api/tests/test_journal_continuity.py:144` — test_retained_database_never_automatically_adopts_journal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-016-RECOVERY-001-03 | Missing local establishment — **WHEN** retained PostgreSQL is paired with a missing or replacement emulator journal **THEN** bootstrap and running service admission refuse silent establishment or account provisioning | `services/api/tests/test_recovery_authority.py:489` — test_worker_claim_and_commit_refuse_retained_activation_missing_in_database<br>`services/api/tests/test_journal_continuity.py:144` — test_retained_database_never_automatically_adopts_journal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### RECOVERY-002 — Scoped independent reapproval

Normative acceptance source: `openspec/changes/independent-recovery-admission/specs/recovery-authority/spec.md` / `RECOVERY-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-016-RECOVERY-002-01 | Reapproved study — **WHEN** every current registry dependency is freshly submitted, independently reviewed and released, and the exact study seal and participant consent are current **THEN** that study may collect through current qualified configurations while every unsealed study remains suspended | `services/api/tests/test_recovery_scopes.py:89` — test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent<br>`services/api/tests/test_recovery_authority.py:489` — test_worker_claim_and_commit_refuse_retained_activation_missing_in_database | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-016-RECOVERY-002-02 | Boolean or stale approval override — **WHEN** a database flag changes, old approval or consent is reused, a seal disappears or a dependency is retired or changed **THEN** study capture and model execution refuse resumption | `services/api/tests/test_recovery_scopes.py:89` — test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent<br>`services/api/tests/test_recovery_authority.py:489` — test_worker_claim_and_commit_refuse_retained_activation_missing_in_database | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-016-RECOVERY-002-03 | Privacy cleanup during suspension — **WHEN** nonprivacy admission fails while an accepted deletion needs safe object cleanup **THEN** privacy cleanup may continue without reopening data or removing independently retained deletion evidence | `services/api/tests/test_recovery_scopes.py:89` — test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent<br>`services/api/tests/test_recovery_authority.py:271` — test_recovery_claim_requires_latest_independent_activation_and_suspension | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Actual-process interruption probe source audit

Mapped existing cases: Shared platform §§6/10; related OPS-002/003/005/006, RAW-EXP-004/006/007, RECOVERY-001, AND-SYNC-003/005/006, AND-PRIV-005, AND-RES-002.

Assertion adequacy inspected: Read worker_interrupt_probe.py validate_target, child_worker, OwnedChild, kill_case, verify_output, stale_case and budget_case. Exact separate disposable local DB/namespace/queues/buckets; wrappers delegate real production claim/commit/S3/SQS/run_job; only owned spawned PID receives signals; SIGKILL exit and actual barriers verified. Five export kill stages plus result after-claim/after-commit; unchanged outbox and winning fence/attempt/output assertions; version-pinned bytes/hash. SIGSTOP lets real120s lease expire; new generation denies stale output; SIGCONT late writer must lease_lost; real expiry cleanup removes only own versions and preserves neighbor. Real malformed durable work five-claim/backoff and actual five-receive120s DLQ redrive preserve production constants.

Remaining limits: Source inspected only; probe and integration WIP, no real process/recovery execution adopted. Unit harness targeting/barrier tests do not prove actual recovery. No study withdrawal or old-backup/cloud restore inferred from generation transaction. PM must assign isolated fixture setup and run after writer release; all resource mutations PM-only. Workflow timeout must fit real production waits; integration pending.
