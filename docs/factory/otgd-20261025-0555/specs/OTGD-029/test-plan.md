# OTGD-029: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md`; SHA-256 `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/tests/generation-cache.test.ts` — `2a30b7da6606d73d185be5efed38968469e3fcde816063890f8e63bd7b32d756`
- `apps/mobile/tests/native-storage.test.ts` — `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`
- `apps/mobile/tests/sync.test.ts` — `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`
- `apps/mobile/tests/workspace-scope.test.ts` — `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_interleavings.py` — `e551a4927813b0ba6550e09bec34d0af953ac8e12cebbe2123159bbb49c0e6c1`
- `services/api/tests/test_participant_postgres.py` — `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-SYNC-001 — Persist before announcing save

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` / `AND-SYNC-001`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-029-AND-SYNC-001-01 | Storage transaction succeeds — **GIVEN** a completed permitted check **WHEN** the finalization transaction commits **THEN** the app shows **Saved on this device** and can reopen the same record after restart. | `apps/mobile/tests/generation-cache.test.ts:188` — all-record device export excludes tombstoned and retired-generation retained records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-029-AND-SYNC-001-02 | Disk is full — **GIVEN** the encrypted database write fails **WHEN** the user finishes the check **THEN** the app reports the save failure and does not show a success state or queue a nonexistent record. | `apps/mobile/tests/generation-cache.test.ts:208` — explicit export containing one retired or quarantined check fails as a whole and never expands its scope | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SYNC-002 — Require explicit authorized upload

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` / `AND-SYNC-002`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-029-AND-SYNC-002-01 | Customer cancels upload sheet — **GIVEN** a local-only check **WHEN** the upload confirmation is canceled **THEN** no network mutation occurs and the check remains local. | `apps/mobile/tests/sync.test.ts:426` — already queued ordinary uploads remain untouched during service readiness pause<br>`apps/mobile/tests/workspace-scope.test.ts:73` — scope checks reject a stale error and a previously opened destructive confirmation | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-029-AND-SYNC-002-02 | Study consent is revoked — **GIVEN** a previously queued study check **WHEN** authorization is rechecked after revocation **THEN** upload is blocked and the app explains the permission change without retrying as another account or study. | `apps/mobile/tests/workspace-scope.test.ts:31` — delayed history, job or study responses cannot publish into another account<br>`apps/mobile/tests/sync.test.ts:426` — already queued ordinary uploads remain untouched during service readiness pause | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SYNC-003 — Use stable idempotent operations

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` / `AND-SYNC-003`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-029-AND-SYNC-003-01 | Response is lost after server acceptance — **GIVEN** a finalize request committed remotely but its response was lost **WHEN** the client retries **THEN** it receives the same logical result/job and no second specimen/task/session is created. | `apps/mobile/tests/sync.test.ts:456` — lost notice acknowledgment response replays its durable timestamp and key before unblocking | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-029-AND-SYNC-003-02 | Queue body is changed under the same key — **GIVEN** an existing accepted idempotency key **WHEN** different content is submitted under that key **THEN** the service returns 409 and the app exposes a conflict rather than changing the frozen record. | `apps/mobile/tests/sync.test.ts:305` — conflict and stale generation stop automatic replay without changing frozen evidence<br>`services/api/tests/test_participant_postgres.py:35` — test_sample_identity_collisions_are_atomic_across_different_subjects | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SYNC-004 — Isolate users and environments

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` / `AND-SYNC-004`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-029-AND-SYNC-004-01 | Two accounts use one phone — **GIVEN** account A has unsynced records **WHEN** A signs out and B signs in **THEN** B cannot list or upload A's records. | `apps/mobile/tests/native-storage.test.ts:128` — concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable<br>`apps/mobile/tests/workspace-scope.test.ts:51` — a delayed export download never reaches sharing after generation change or local clear | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-029-AND-SYNC-004-02 | Production build receives local configuration — **GIVEN** a production app/backend configuration **WHEN** a local issuer or AWS-emulator endpoint is supplied **THEN** startup fails closed; the configuration cannot silently redirect participant data. | `apps/mobile/tests/native-storage.test.ts:128` — concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable<br>`apps/mobile/tests/workspace-scope.test.ts:51` — a delayed export download never reaches sharing after generation change or local clear | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SYNC-005 — Reconcile stale revisions without overwrite

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` / `AND-SYNC-005`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-029-AND-SYNC-005-01 | Another device finalized the session — **GIVEN** a stale local ETag **WHEN** PUT snapshot returns 412 for its stale precondition or 409 for a frozen-state conflict **THEN** the app fetches the server state and does not overwrite it. | `apps/mobile/tests/sync.test.ts:305` — conflict and stale generation stop automatic replay without changing frozen evidence<br>`services/api/tests/test_api.py:158` — test_profile_initial_missing_stale_etag_and_replay | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-029-AND-SYNC-005-02 | Correcting an accepted value — **GIVEN** a finalized session requires correction **WHEN** a correction is created **THEN** reacquisition uses a new session UUID/target time and supersedes reference with no earlier physical components copied; an administrative report correction remains a distinct authorized workflow. | `apps/mobile/tests/sync.test.ts:305` — conflict and stale generation stop automatic replay without changing frozen evidence<br>`services/api/tests/test_api.py:371` — test_recovery_cutoff_uses_auth_time_not_refresh_issue_time | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SYNC-006 — Bound retries and preserve terminal failures

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` / `AND-SYNC-006`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-029-AND-SYNC-006-01 | Rate limit response — **GIVEN** HTTP 429 with a valid Retry-After **WHEN** scheduling the next attempt **THEN** the queue honors the delay within a documented bound and shows a waiting state. | `apps/mobile/tests/sync.test.ts:280` — reconnection does not retry an ordinary explicit queue when preference remains off | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-029-AND-SYNC-006-02 | Invalid snapshot — **GIVEN** HTTP 422 **WHEN** the client classifies the failure **THEN** automatic retry stops and the customer can inspect the reported field error. | `apps/mobile/tests/sync.test.ts:305` — conflict and stale generation stop automatic replay without changing frozen evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-SYNC-007 — Preserve scientific and acquisition time

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md` / `AND-SYNC-007`.

Prerequisites and limits: NOT_RUN real transport/concurrency/privacy acceptance on fresh fictional runtime and separate disposable PostgreSQL; preserve retained identities after setup.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-029-AND-SYNC-007-01 | Upload occurs after a day offline — **GIVEN** a previously captured record **WHEN** it reaches the service the next day **THEN** history retains the original check time and separately records synchronization/evaluation time. | `apps/mobile/tests/generation-cache.test.ts:188` — all-record device export excludes tombstoned and retired-generation retained records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-029-AND-SYNC-007-02 | Reboot during scored game — **GIVEN** an interrupted reaction run in a restored draft **WHEN** the application restarts **THEN** it marks that attempt invalid and cannot submit it as a completed uninterrupted task. | `services/api/tests/test_participant_postgres.py:60` — test_signed_issue_and_attestation_receipt_anchors_cannot_be_rewritten<br>`apps/mobile/tests/sync.test.ts:19` — a queued receipt commit cannot revive consent when withdrawal publishes before its serialized callback | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

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
