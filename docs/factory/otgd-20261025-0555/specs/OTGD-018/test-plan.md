# OTGD-018: verification plan

Canonical: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md`; SHA-256 `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/raw-recordings.spec.ts` — `2ada98a52caf63a835d979adc71bef5542795c5edbd72fc859cdb7975cbfd3b7`
- `apps/mobile/tests/native-storage.test.ts` — `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`
- `apps/mobile/tests/raw-artifacts.test.ts` — `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`
- `apps/mobile/tests/raw-export.test.ts` — `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`
- `apps/mobile/tests/raw-recordings.test.ts` — `c850243e541fffdce52a7b44db52ff300e637448bb26d6281eef4c8428c51354`
- `apps/mobile/tests/raw-upload.test.ts` — `7771c6a9657ccd0dba4d716eb6504e80a97c36290fb6bbd00b6969db2ba769d9`
- `services/api/tests/test_raw_capture.py` — `ebedc54a2c384fb5992fb61e1959b61d767ad41afbacd8ecf7aec6729710905e`
- `services/api/tests/test_raw_export.py` — `7ee249d50b4f2bd684639b4340159f3f8eab2f25ede232c0d67ba89bfb7ec627`
- `services/api/tests/test_raw_retention.py` — `4f2115aa7b12c65d238c674d9568a1a64c1d9666a7b50f6543ee5e602d6923ae`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-RAW-001 — Present exact optional-purpose terms before recording

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-001-01 | Approved terms are independently verified — **GIVEN** the owned study returns current consent and an approved policy **WHEN** the participant opens Recording choices & retention **THEN** exact verified terms appear before any choice can be confirmed. | `apps/mobile/tests/raw-recordings.test.ts:21` — actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states<br>`apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-001-02 | A projected purpose is substituted — **GIVEN** the server reply contains policy.content for purpose A and displayed purpose B **WHEN** the client verifies the reply **THEN** the policy is rejected and acquisition remains unavailable. | `apps/mobile/tests/raw-recordings.test.ts:21` — actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states<br>`services/api/tests/test_raw_export.py:319` — test_expiry_and_retention_are_hard_caps_and_generation_deletion_denies | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RAW-002 — Separate recording and upload from study acceptance

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-002-01 | Participant chooses local recording only — **GIVEN** verified terms and both choices off **WHEN** the participant enables device recording and confirms the separate notice **THEN** upload remains off and no raw file is queued. | `apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice<br>`apps/mobile/tests/raw-recordings.test.ts:77` — default off, local-only opt-in, upload dependency, policy expiry and pending stop fences remain distinct | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-002-02 | The workspace changes before confirmation — **GIVEN** unchecked choices were edited in account A generation 1 **WHEN** account B or a new generation opens the form **THEN** unfinished choices and notice acknowledgment reset. | `apps/mobile/e2e/raw-recordings.spec.ts:1167` — account or generation change resets unfinished choices and notice acknowledgment<br>`apps/mobile/tests/raw-export.test.ts:148` — server boundary terms remain bounded and optional sources cannot inherit recording consent or broaden selection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RAW-003 — Preserve exact intent and acknowledgment receipt

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-003-01 | Accepted response is lost — **GIVEN** the service accepted a preference but its reply was lost **WHEN** the customer retries **THEN** the original body, timestamp and request key are reused and the original receipt is reconciled. | `apps/mobile/tests/raw-recordings.test.ts:188` — lost optional-choice receipt replays exact durable body, original acknowledgment and idempotency key<br>`apps/mobile/e2e/raw-recordings.spec.ts:1167` — account or generation change resets unfinished choices and notice acknowledgment | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-003-02 | Effective permission exceeds the receipt — **GIVEN** a receipt confirms upload=false **WHEN** a status reply says upload=true without a new matching receipt **THEN** the client rejects the status. | `apps/mobile/tests/raw-recordings.test.ts:188` — lost optional-choice receipt replays exact durable body, original acknowledgment and idempotency key<br>`apps/mobile/e2e/raw-recordings.spec.ts:1167` — account or generation change resets unfinished choices and notice acknowledgment | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RAW-004 — Stop locally and retain privacy barriers

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-004-01 | A grant reply arrives after revocation — **GIVEN** an optional-purpose grant request is in flight **WHEN** the participant requests revocation before its reply **THEN** the grant intent remains blocked and the late reply cannot revive it. | `apps/mobile/tests/raw-recordings.test.ts:355` — an older completed revocation cannot clear a newer accepted cleanup-pending stop fence<br>`apps/mobile/tests/raw-artifacts.test.ts:70` — fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-004-02 | Old cleanup and new pending cleanup coexist — **GIVEN** completed revocation A and newer cleanup-pending revocation B for eye video **WHEN** status is refreshed after B was accepted **THEN** eye recording remains fenced until B is completed. | `apps/mobile/tests/raw-recordings.test.ts:355` — an older completed revocation cannot clear a newer accepted cleanup-pending stop fence<br>`apps/mobile/e2e/raw-recordings.spec.ts:1223` — local revocation fence overrides old confirmed grant without claiming cleanup completion | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RAW-005 — Distinguish upload and physical retention cleanup

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-005-01 | An uploaded object is awaiting verification — **GIVEN** retention state retained and upload_state quarantine **WHEN** status is displayed **THEN** quarantine is visible and the app does not claim verified upload or completed deletion. | `apps/mobile/tests/raw-upload.test.ts:411` — object PUT has a real 60-second deadline and privacy cancellation aborts transport without late success<br>`apps/mobile/e2e/raw-recordings.spec.ts:1034` — pending laboratory UI preserves the draft, refreshes actual admitted analysis and requires explicit cancellation without inventing chemistry | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-005-02 | Physical cleanup has not completed — **GIVEN** a revoked artifact has cleanup_pending with no cleanup_completed_at **WHEN** its receipt is displayed **THEN** pending cleanup remains explicit and is never labeled deleted. | `services/api/tests/test_raw_export.py:485` — test_http_revoked_cleanup_has_minimal_terminal_receipt<br>`apps/mobile/tests/raw-recordings.test.ts:137` — separate revocation preserves original granted receipt while effective choices turn off and cleanup remains pending | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RAW-006 — Bind recording to fresh acquisition and encrypted local commit

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-006-01 | Participant saves approved local recording — **GIVEN** an approved codec and separately confirmed record=true, upload=false **WHEN** native acquisition completes and its immutable evidence matches the fresh start **THEN** bytes and metadata commit together to SQLCipher, native handoff memory is released, and the upload queue remains empty. | `apps/mobile/tests/raw-artifacts.test.ts:39` — native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff<br>`apps/mobile/tests/raw-upload.test.ts:221` — Save and metadata-only upload never read or queue raw; explicit selection is immutable and exact | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-006-02 | Consent was revoked on another device — **GIVEN** a cached optional receipt appears to permit recording **WHEN** fresh capture start refuses or narrows the receipt **THEN** native raw recording never starts and cached permission cannot override the fresh decision. | `apps/mobile/tests/raw-artifacts.test.ts:39` — native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff<br>`apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RAW-007 — Enforce local retention and bounded ticket recovery

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-007`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-007-01 | A stopped app resumes after retention expiry — **GIVEN** local raw bytes expired while the app was stopped **WHEN** the owner unlocks the workspace **THEN** expired and unindexed bytes are removed before exposure, failed removal remains pending, no expired read or upload is admitted, and the stopped app makes no exact-time physical cleanup claim. | `apps/mobile/e2e/raw-recordings.spec.ts:1332` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload<br>`apps/mobile/tests/native-storage.test.ts:219` — raw bytes and index rollback together on a workspace switch and expiry/orphan reconciliation completes before reopened reads | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-007-02 | Renewal response is lost — **GIVEN** a ticket renewal has an unknown response **WHEN** explicit upload is retried **THEN** its exact key and body are reused; after an acknowledged ticket later expires, a new bounded renewal epoch is persisted before requesting a replacement, and decrypted buffers are wiped on success, failure or cancellation. | `apps/mobile/tests/raw-upload.test.ts:263` — acknowledged expired tickets advance durable renewal identity, while a lost renewal replays its exact key<br>`apps/mobile/e2e/raw-recordings.spec.ts:1332` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RAW-008 — Require a distinct raw export purpose and exact binary scope

Normative acceptance source: `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md` / `AND-RAW-008`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-018-AND-RAW-008-01 | Participant explicitly includes an authorized recording — **GIVEN** a distinct current export purpose and eligible retained source for the selected check **WHEN** the participant reads the exact notice, selects the source and confirms the separate export **THEN** recording or upload consent alone grants no export scope, the service job retains the exact authority, source selection, notice and acknowledgment timestamp, a lost receipt reuses the same key and body, and the archive verifies against that receipt before sharing. | `apps/mobile/tests/raw-export.test.ts:225` — cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt<br>`apps/mobile/e2e/raw-recordings.spec.ts:1253` — actual raw export component keeps every source and separate acknowledgment off until exact purpose review, then resets for another owner | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-018-AND-RAW-008-02 | A raw member is substituted — **GIVEN** a downloaded ZIP has internally rehashed files but a changed raw source version or an unselected binary member **WHEN** the app compares the archive with the authenticated job receipt **THEN** exact source ID, version, kind, SHA-256, size and retained lifetime are compared with the owned frozen job; substituted, unknown or orphan paths refuse sharing, and no broadened permission is inferred from recording consent. | `apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources<br>`apps/mobile/e2e/raw-recordings.spec.ts:1297` — expired or unselected raw export sources remain unavailable while structured export stays separate | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `50 MiB`, `64 MiB`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Actual-process interruption probe source audit

Mapped existing cases: Shared platform §§6/10; related OPS-002/003/005/006, RAW-EXP-004/006/007, RECOVERY-001, AND-SYNC-003/005/006, AND-PRIV-005, AND-RES-002.

Assertion adequacy inspected: Read worker_interrupt_probe.py validate_target, child_worker, OwnedChild, kill_case, verify_output, stale_case and budget_case. Exact separate disposable local DB/namespace/queues/buckets; wrappers delegate real production claim/commit/S3/SQS/run_job; only owned spawned PID receives signals; SIGKILL exit and actual barriers verified. Five export kill stages plus result after-claim/after-commit; unchanged outbox and winning fence/attempt/output assertions; version-pinned bytes/hash. SIGSTOP lets real120s lease expire; new generation denies stale output; SIGCONT late writer must lease_lost; real expiry cleanup removes only own versions and preserves neighbor. Real malformed durable work five-claim/backoff and actual five-receive120s DLQ redrive preserve production constants.

Remaining limits: Source inspected only; probe and integration WIP, no real process/recovery execution adopted. Unit harness targeting/barrier tests do not prove actual recovery. No study withdrawal or old-backup/cloud restore inferred from generation transaction. PM must assign isolated fixture setup and run after writer release; all resource mutations PM-only. Workflow timeout must fit real production waits; integration pending.


## Final corrected source evidence — e89897cc852a

# OTGD-018 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/optional-raw-recording-lifecycle/specs/raw-recording-customer-flow/spec.md`; SHA256 `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-018/test-plan.md`. External review artifact only; PM controls import.

All 16 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-018-AND-RAW-001-01 | Approved terms are independently verified — - **GIVEN** the owned study returns current consent and an approved policy - **WHEN** the participant opens Recording choices & retention - **THEN** exact verified terms appear before any choice can be confirmed. | PARTIAL |
| OTGD-018-AND-RAW-001-02 | A projected purpose is substituted — - **GIVEN** the server reply contains policy.content for purpose A and displayed purpose B - **WHEN** the client verifies the reply - **THEN** the policy is rejected and acquisition remains unavailable. | PARTIAL |
| OTGD-018-AND-RAW-002-01 | Participant chooses local recording only — - **GIVEN** verified terms and both choices off - **WHEN** the participant enables device recording and confirms the separate notice - **THEN** upload remains off and no raw file is queued. | PASS |
| OTGD-018-AND-RAW-002-02 | The workspace changes before confirmation — - **GIVEN** unchecked choices were edited in account A generation 1 - **WHEN** account B or a new generation opens the form - **THEN** unfinished choices and notice acknowledgment reset. | PASS |
| OTGD-018-AND-RAW-003-01 | Accepted response is lost — - **GIVEN** the service accepted a preference but its reply was lost - **WHEN** the customer retries - **THEN** the original body, timestamp and request key are reused and the original receipt is reconciled. | PASS |
| OTGD-018-AND-RAW-003-02 | Effective permission exceeds the receipt — - **GIVEN** a receipt confirms upload=false - **WHEN** a status reply says upload=true without a new matching receipt - **THEN** the client rejects the status. | PASS |
| OTGD-018-AND-RAW-004-01 | A grant reply arrives after revocation — - **GIVEN** an optional-purpose grant request is in flight - **WHEN** the participant requests revocation before its reply - **THEN** the grant intent remains blocked and the late reply cannot revive it. | PASS |
| OTGD-018-AND-RAW-004-02 | Old cleanup and new pending cleanup coexist — - **GIVEN** completed revocation A and newer cleanup-pending revocation B for eye video - **WHEN** status is refreshed after B was accepted - **THEN** eye recording remains fenced until B is completed. | PASS |
| OTGD-018-AND-RAW-005-01 | An uploaded object is awaiting verification — - **GIVEN** retention state retained and upload_state quarantine - **WHEN** status is displayed - **THEN** quarantine is visible and the app does not claim verified upload or completed deletion. | PASS |
| OTGD-018-AND-RAW-005-02 | Physical cleanup has not completed — - **GIVEN** a revoked artifact has cleanup_pending with no cleanup_completed_at - **WHEN** its receipt is displayed - **THEN** pending cleanup remains explicit and is never labeled deleted. | PASS |
| OTGD-018-AND-RAW-006-01 | Participant saves approved local recording — - **GIVEN** an approved codec and separately confirmed record=true, upload=false - **WHEN** native acquisition completes and its immutable evidence matches the fresh start - **THEN** bytes and metadata commit together to SQLCipher, native handoff memory is released, and the upload queue remains empty. | PARTIAL |
| OTGD-018-AND-RAW-006-02 | Consent was revoked on another device — - **GIVEN** a cached optional receipt appears to permit recording - **WHEN** fresh capture start refuses or narrows the receipt - **THEN** native raw recording never starts and cached permission cannot override the fresh decision. | PARTIAL |
| OTGD-018-AND-RAW-007-01 | A stopped app resumes after retention expiry — - **GIVEN** local raw bytes expired while the app was stopped - **WHEN** the owner unlocks the workspace - **THEN** expired and unindexed bytes are removed before exposure, failed removal remains pending, no expired read or upload is admitted, and the stopped app makes no exact-time physical cleanup claim. | PARTIAL |
| OTGD-018-AND-RAW-007-02 | Renewal response is lost — - **GIVEN** a ticket renewal has an unknown response - **WHEN** explicit upload is retried - **THEN** its exact key and body are reused; after an acknowledged ticket later expires, a new bounded renewal epoch is persisted before requesting a replacement, and decrypted buffers are wiped on success, failure or cancellation. | PASS |
| OTGD-018-AND-RAW-008-01 | Participant explicitly includes an authorized recording — - **GIVEN** a distinct current export purpose and eligible retained source for the selected check - **WHEN** the participant reads the exact notice, selects the source and confirms the separate export - **THEN** recording or upload consent alone grants no export scope, the service job retains the exact authority, source selection, notice and acknowledgment timestamp, a lost receipt reuses the same key and body, and the archive verifies against that receipt before sharing. | PARTIAL |
| OTGD-018-AND-RAW-008-02 | A raw member is substituted — - **GIVEN** a downloaded ZIP has internally rehashed files but a changed raw source version or an unselected binary member - **WHEN** the app compares the archive with the authenticated job receipt - **THEN** exact source ID, version, kind, SHA-256, size and retained lifetime are compared with the owned frozen job; substituted, unknown or orphan paths refuse sharing, and no broadened permission is inferred from recording consent. | PASS |
