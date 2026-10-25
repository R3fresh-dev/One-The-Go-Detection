# OTGD-031: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md`; SHA-256 `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/components.spec.ts` — `725effb97f2e9195340fd6370b8491065eabdf849ce5c5680974c39cc2125c53`
- `apps/mobile/tests/controller.test.ts` — `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92`
- `apps/mobile/tests/generation-cache.test.ts` — `2a30b7da6606d73d185be5efed38968469e3fcde816063890f8e63bd7b32d756`
- `apps/mobile/tests/raw-recordings.test.ts` — `c850243e541fffdce52a7b44db52ff300e637448bb26d6281eef4c8428c51354`
- `apps/mobile/tests/sync.test.ts` — `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`
- `apps/mobile/tests/workspace-scope.test.ts` — `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_identity_barriers.py` — `79480e9dde91c88207e1f10675e1a30f1a5e06e6d7df10cdc8c07c4d70fc15d2`
- `services/api/tests/test_raw_retention.py` — `4f2115aa7b12c65d238c674d9568a1a64c1d9666a7b50f6543ee5e602d6923ae`
- `services/api/tests/test_replica_cleanup.py` — `7bc5222b3b8d6e05d7d5f6c969a00d717ed1714c862d6f5db59296cdcf8c7ef4`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-PRIV-001 — Separate storage and upload choices

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` / `AND-PRIV-001`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-031-AND-PRIV-001-01 | priv-enable-queued-upload-retries — **GIVEN** a signed-in account with one explicitly queued check and another unqueued local check **WHEN** the user confirms Enable automatic retries **THEN** only the already queued check is eligible for automatic retry and the other check, raw media, and research data remain unqueued. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/sync.test.ts:426` — already queued ordinary uploads remain untouched during service readiness pause | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-001-02 | priv-disable-during-upload — **GIVEN** a permitted upload is in flight and more operations are queued **WHEN** the user disables automatic retries **THEN** no new automatic retry starts, the in-flight outcome is reconciled honestly, and the UI does not claim previously accepted data was deleted. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/sync.test.ts:426` — already queued ordinary uploads remain untouched during service readiness pause | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRIV-002 — Scoped and explicit local clearing

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` / `AND-PRIV-002`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-031-AND-PRIV-002-01 | priv-clear-demo-only — **GIVEN** demo and account caches coexist **WHEN** Clear demo records is confirmed **THEN** demo records disappear, account records remain, and no cloud deletion request is made. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`services/api/tests/test_raw_retention.py:680` — test_cleanup_purges_verified_data_after_authority_loss | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-002-02 | priv-cancel-unsynced-clear — **GIVEN** three account records are unsynchronized **WHEN** the warning shows three and the user selects Cancel **THEN** all records and queue entries remain unchanged. | `apps/mobile/e2e/components.spec.ts:127` — confirmation components never enable retry or erase unsynced records on cancellation<br>`services/api/tests/test_raw_retention.py:680` — test_cleanup_purges_verified_data_after_authority_loss | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRIV-003 — Owned, reauthenticated cloud deletion

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` / `AND-PRIV-003`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-031-AND-PRIV-003-01 | priv-valid-data-deletion — **GIVEN** an owned account, current policy review, and reauthentication within five minutes **WHEN** the user confirms deletion of profile and check data **THEN** one all_data job is accepted and the account identity is retained according to the displayed scope. | `apps/mobile/tests/generation-cache.test.ts:208` — explicit export containing one retired or quarantined check fails as a whole and never expands its scope<br>`apps/mobile/tests/sync.test.ts:391` — HTTP client sends access token and stable generation, rejects missing write identity | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-003-02 | priv-forged-owner-or-stale-auth — **GIVEN** a deletion body contains another owner's ID or authentication is stale **WHEN** it is submitted **THEN** the server rejects it and no deletion job affects another account or bypasses reauthentication. | `apps/mobile/tests/workspace-scope.test.ts:73` — scope checks reject a stale error and a previously opened destructive confirmation<br>`apps/mobile/tests/sync.test.ts:391` — HTTP client sends access token and stable generation, rejects missing write identity | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRIV-004 — Honest asynchronous completion

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` / `AND-PRIV-004`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-031-AND-PRIV-004-01 | priv-deletion-response-lost — **GIVEN** the server accepted a deletion but its response was lost **WHEN** the app retries with the same key and scope **THEN** the same job is returned and the UI remains requested/running until actual completion is reported. | `apps/mobile/tests/sync.test.ts:290` — a lost accepted response replays the same identity and unchanged bytes<br>`services/api/tests/test_api.py:314` — test_deletion_barrier_survives_journal_failure_and_same_key_resumes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-004-02 | priv-retention-exception — **GIVEN** a kind=deletion job reports partially_retained for a named audit category retained until a stated date **WHEN** status is shown **THEN** that exception remains visible and the app does not claim every copy was erased. | `apps/mobile/tests/raw-recordings.test.ts:21` — actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states<br>`services/api/tests/test_raw_retention.py:849` — test_administrative_reports_require_their_own_approved_purpose | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-004-03 | priv-job-kind-state-discriminator — **GIVEN** a completed export and a partially_retained deletion are returned by the shared job route **WHEN** Privacy routes each response **THEN** export-only expired is never interpreted as deletion state; partially_retained displays the listed exception and no partially_completed fallback is created. | `services/api/tests/test_api.py:314` — test_deletion_barrier_survives_journal_failure_and_same_key_resumes<br>`apps/mobile/tests/controller.test.ts:185` — a consent receipt for another document or timestamp is never accepted as research authorization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRIV-005 — Prevent resurrection and cross-device writes

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` / `AND-PRIV-005`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-031-AND-PRIV-005-01 | priv-offline-device-reconnects — **GIVEN** device A completed all_data deletion while device B held old queued records offline **WHEN** B reconnects **THEN** the server returns 410 for new stale-generation mutations and B quarantines their original operations instead of rebinding or restoring them. | `apps/mobile/tests/sync.test.ts:322` — accepted deletion intent may reconcile with its old generation and original key<br>`apps/mobile/tests/controller.test.ts:382` — server generation retirement quarantines prior checks and a new empty workspace requires separate acknowledgment | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-005-02 | priv-late-fetch-after-clear — **GIVEN** an old-history fetch is in flight when account deletion is accepted **WHEN** the fetch returns **THEN** its payload cannot recreate deleted local content. | `apps/mobile/tests/sync.test.ts:322` — accepted deletion intent may reconcile with its old generation and original key<br>`apps/mobile/tests/raw-recordings.test.ts:310` — revocation fences an in-flight preference receipt before any late reply can mark it accepted | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-005-03 | priv-explicit-generation-reset-required — **GIVEN** an all_data deletion finished and the account remains usable **WHEN** the user returns to Profile or Check before acknowledging the new generation **THEN** old queued records remain quarantined and new protected writes stay blocked until Start a new empty workspace is explicitly confirmed. | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/sync.test.ts:322` — accepted deletion intent may reconcile with its old generation and original key | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-005-04 | priv-deletion-replay-does-not-create-new-job — **GIVEN** a deletion was accepted and advanced generation but its response was lost **WHEN** the exact original idempotent request is replayed under the shared replay policy **THEN** the original job is returned; a distinct mutation carrying the old generation receives 410 and is quarantined. | `apps/mobile/tests/sync.test.ts:322` — accepted deletion intent may reconcile with its old generation and original key<br>`apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRIV-006 — Clear retention and protected temporary data

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` / `AND-PRIV-006`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-031-AND-PRIV-006-01 | priv-unconfigured-retention — **GIVEN** production has no approved policy for raw eye recordings **WHEN** the privacy and capture availability screens load **THEN** raw recording is unavailable and no generic consent checkbox enables it. | `apps/mobile/tests/raw-recordings.test.ts:21` — actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states<br>`apps/mobile/tests/controller.test.ts:185` — a consent receipt for another document or timestamp is never accepted as research authorization | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-006-02 | priv-redacted-deletion-log — **GIVEN** a deletion request fails validation **WHEN** the event is logged **THEN** logs include a redacted operation/request reference and reason category without tokens, profile values, or measurements. | `apps/mobile/tests/raw-recordings.test.ts:21` — actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states<br>`apps/mobile/tests/sync.test.ts:340` — repeated unconfirmed export click retains one durable operation identity | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-PRIV-007 — Accessible controls and iOS parity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md` / `AND-PRIV-007`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup. NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-031-AND-PRIV-007-01 | priv-accessible-confirmation — **GIVEN** TalkBack and 200% text scaling **WHEN** the deletion review opens **THEN** scope, retention exceptions, and both final/cancel actions are reachable before confirmation can occur. | `apps/mobile/tests/workspace-scope.test.ts:73` — scope checks reject a stale error and a previously opened destructive confirmation<br>`apps/mobile/e2e/components.spec.ts:127` — confirmation components never enable retry or erase unsynced records on cancellation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-031-AND-PRIV-007-02 | priv-ios-account-deletion — **GIVEN** an authenticated iOS account **WHEN** the user completes in-app account deletion review and reauthentication **THEN** the same scoped asynchronous job is requested and its completion status is represented without sending the user to an unrelated website. ## Acceptance evidence Required evidence: explicit-upload/queued-retry/no-research trace; local-clear isolation/cancel; recent-auth and ownership rejection; lost-response idempotency; running/failed/partial/completed screenshots; deletion/late-response and cross-device queue tests; temporary-file cleanup; redacted logs; Android/iOS accessibility checks. The implementation must record actual retention/backup cleanup limitations; an API 202 alone is not deletion evidence. | `apps/mobile/tests/raw-recordings.test.ts:355` — an older completed revocation cannot clear a newer accepted cleanup-pending stop fence<br>`apps/mobile/tests/workspace-scope.test.ts:73` — scope checks reject a stale error and a previously opened destructive confirmation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Actual-process interruption probe source audit

Mapped existing cases: Shared platform §§6/10; related OPS-002/003/005/006, RAW-EXP-004/006/007, RECOVERY-001, AND-SYNC-003/005/006, AND-PRIV-005, AND-RES-002.

Assertion adequacy inspected: Read worker_interrupt_probe.py validate_target, child_worker, OwnedChild, kill_case, verify_output, stale_case and budget_case. Exact separate disposable local DB/namespace/queues/buckets; wrappers delegate real production claim/commit/S3/SQS/run_job; only owned spawned PID receives signals; SIGKILL exit and actual barriers verified. Five export kill stages plus result after-claim/after-commit; unchanged outbox and winning fence/attempt/output assertions; version-pinned bytes/hash. SIGSTOP lets real120s lease expire; new generation denies stale output; SIGCONT late writer must lease_lost; real expiry cleanup removes only own versions and preserves neighbor. Real malformed durable work five-claim/backoff and actual five-receive120s DLQ redrive preserve production constants.

Remaining limits: Source inspected only; probe and integration WIP, no real process/recovery execution adopted. Unit harness targeting/barrier tests do not prove actual recovery. No study withdrawal or old-backup/cloud restore inferred from generation transaction. PM must assign isolated fixture setup and run after writer release; all resource mutations PM-only. Workflow timeout must fit real production waits; integration pending.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.


## Final corrected source evidence — e89897cc852a

# OTGD-031 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-privacy-controls/spec.md`; SHA256 `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-031/test-plan.md`. External review artifact only; PM controls import.

All 17 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `python scripts/ci_gate.py localstack-api`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-031-AND-PRIV-001-01 | priv-enable-queued-upload-retries — - **GIVEN** a signed-in account with one explicitly queued check and another unqueued local check - **WHEN** the user confirms Enable automatic retries - **THEN** only the already queued check is eligible for automatic retry and the other check, raw media, and research data remain unqueued. | PARTIAL |
| OTGD-031-AND-PRIV-001-02 | priv-disable-during-upload — - **GIVEN** a permitted upload is in flight and more operations are queued - **WHEN** the user disables automatic retries - **THEN** no new automatic retry starts, the in-flight outcome is reconciled honestly, and the UI does not claim previously accepted data was deleted. | PARTIAL |
| OTGD-031-AND-PRIV-002-01 | priv-clear-demo-only — - **GIVEN** demo and account caches coexist - **WHEN** Clear demo records is confirmed - **THEN** demo records disappear, account records remain, and no cloud deletion request is made. | PARTIAL |
| OTGD-031-AND-PRIV-002-02 | priv-cancel-unsynced-clear — - **GIVEN** three account records are unsynchronized - **WHEN** the warning shows three and the user selects Cancel - **THEN** all records and queue entries remain unchanged. | PARTIAL |
| OTGD-031-AND-PRIV-003-01 | priv-valid-data-deletion — - **GIVEN** an owned account, current policy review, and reauthentication within five minutes - **WHEN** the user confirms deletion of profile and check data - **THEN** one all_data job is accepted and the account identity is retained according to the displayed scope. | PASS |
| OTGD-031-AND-PRIV-003-02 | priv-forged-owner-or-stale-auth — - **GIVEN** a deletion body contains another owner's ID or authentication is stale - **WHEN** it is submitted - **THEN** the server rejects it and no deletion job affects another account or bypasses reauthentication. | PARTIAL |
| OTGD-031-AND-PRIV-004-01 | priv-deletion-response-lost — - **GIVEN** the server accepted a deletion but its response was lost - **WHEN** the app retries with the same key and scope - **THEN** the same job is returned and the UI remains requested/running until actual completion is reported. | PASS |
| OTGD-031-AND-PRIV-004-02 | priv-retention-exception — - **GIVEN** a kind=deletion job reports partially_retained for a named audit category retained until a stated date - **WHEN** status is shown - **THEN** that exception remains visible and the app does not claim every copy was erased. | PASS |
| OTGD-031-AND-PRIV-004-03 | priv-job-kind-state-discriminator — - **GIVEN** a completed export and a partially_retained deletion are returned by the shared job route - **WHEN** Privacy routes each response - **THEN** export-only expired is never interpreted as deletion state; partially_retained displays the listed exception and no partially_completed fallback is created. | PASS |
| OTGD-031-AND-PRIV-005-01 | priv-offline-device-reconnects — - **GIVEN** device A completed all_data deletion while device B held old queued records offline - **WHEN** B reconnects - **THEN** the server returns 410 for new stale-generation mutations and B quarantines their original operations instead of rebinding or restoring them. | PASS |
| OTGD-031-AND-PRIV-005-02 | priv-late-fetch-after-clear — - **GIVEN** an old-history fetch is in flight when account deletion is accepted - **WHEN** the fetch returns - **THEN** its payload cannot recreate deleted local content. | PARTIAL |
| OTGD-031-AND-PRIV-005-03 | priv-explicit-generation-reset-required — - **GIVEN** an all_data deletion finished and the account remains usable - **WHEN** the user returns to Profile or Check before acknowledging the new generation - **THEN** old queued records remain quarantined and new protected writes stay blocked until Start a new empty workspace is explicitly confirmed. | PARTIAL |
| OTGD-031-AND-PRIV-005-04 | priv-deletion-replay-does-not-create-new-job — - **GIVEN** a deletion was accepted and advanced generation but its response was lost - **WHEN** the exact original idempotent request is replayed under the shared replay policy - **THEN** the original job is returned; a distinct mutation carrying the old generation receives 410 and is quarantined. | PASS |
| OTGD-031-AND-PRIV-006-01 | priv-unconfigured-retention — - **GIVEN** production has no approved policy for raw eye recordings - **WHEN** the privacy and capture availability screens load - **THEN** raw recording is unavailable and no generic consent checkbox enables it. | PARTIAL |
| OTGD-031-AND-PRIV-006-02 | priv-redacted-deletion-log — - **GIVEN** a deletion request fails validation - **WHEN** the event is logged - **THEN** logs include a redacted operation/request reference and reason category without tokens, profile values, or measurements. | PARTIAL |
| OTGD-031-AND-PRIV-007-01 | priv-accessible-confirmation — - **GIVEN** TalkBack and 200% text scaling - **WHEN** the deletion review opens - **THEN** scope, retention exceptions, and both final/cancel actions are reachable before confirmation can occur. | BLOCKED |
| OTGD-031-AND-PRIV-007-02 | priv-ios-account-deletion — - **GIVEN** an authenticated iOS account - **WHEN** the user completes in-app account deletion review and reauthentication - **THEN** the same scoped asynchronous job is requested and its completion status is represented without sending the user to an unrelated website. | BLOCKED |
