# OTGD-022: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md`; SHA-256 `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/mobile.spec.ts` — `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`
- `apps/mobile/tests/domain.test.ts` — `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`
- `apps/mobile/tests/export-evidence.test.ts` — `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`
- `apps/mobile/tests/export-projection.test.ts` — `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`
- `apps/mobile/tests/export-scope.test.ts` — `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46`
- `apps/mobile/tests/raw-export.test.ts` — `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_raw_export.py` — `7ee249d50b4f2bd684639b4340159f3f8eab2f25ede232c0d67ba89bfb7ec627`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-EXP-001 — Require a deliberate scope and action

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` / `AND-EXP-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-022-AND-EXP-001-01 | Local single-check export — **GIVEN** History selects one check while unrelated records also exist **WHEN** the customer confirms This device for that exact selection **THEN** only the selected check, its frozen profile/context, attempts, alcohol, and linked results are exported locally, with no cloud mutation or unrelated profile revision. | `apps/mobile/tests/domain.test.ts:407` — single-check export preserves exact scope and excludes unrelated current profile<br>`apps/mobile/tests/export-scope.test.ts:168` — rehashed extra profile version and unrelated current profile are rejected in a single-check archive | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-022-AND-EXP-001-02 | Confirmation is canceled — **GIVEN** the export summary sheet **WHEN** the customer cancels **THEN** no job/file/share action is created. | `apps/mobile/tests/domain.test.ts:435` — export rejects file tampering and traversal or hidden files before sharing<br>`services/api/tests/test_raw_export.py:245` — test_scope_revision_hash_owner_and_confirmation_clock_rechecked | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EXP-002 — Enforce ownership on selection and download

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` / `AND-EXP-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-022-AND-EXP-002-01 | Own synced records — **GIVEN** a signed-in owner selecting their records **WHEN** the export completes **THEN** the archive contains only the authorized selected records. | `services/api/tests/test_api.py:276` — test_export_scope_and_authenticated_download<br>`apps/mobile/tests/export-scope.test.ts:112` — cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-022-AND-EXP-002-02 | Another user's session is injected — **GIVEN** an export selection containing a foreign UUID **WHEN** the request is validated **THEN** it is rejected without including or disclosing the foreign record. | `services/api/tests/test_api.py:276` — test_export_scope_and_authenticated_download<br>`apps/mobile/tests/raw-export.test.ts:104` — rehashed raw version, size, digest, omitted-scope and orphan substitutions never expand the authenticated job scope | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EXP-003 — Preserve evidence semantics

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` / `AND-EXP-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-022-AND-EXP-003-01 | Censored saliva result — **GIVEN** a below_loq measurement **WHEN** exported **THEN** value remains null and the qualifier/limit/original report remain available. | `apps/mobile/tests/export-evidence.test.ts:98` — exports verify exact originals and retain supported absent self-report context<br>`services/api/tests/test_api.py:459` — test_alcohol_censoring_is_null | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-022-AND-EXP-003-02 | Historical reanalysis — **GIVEN** multiple linked results for one session **WHEN** selected for export **THEN** their immutable IDs, versions, and replacement relationship are preserved. | `apps/mobile/tests/export-evidence.test.ts:98` — exports verify exact originals and retain supported absent self-report context<br>`services/api/tests/test_raw_export.py:302` — test_late_export_versions_and_markers_are_recurring_scoped_cleanup | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EXP-004 — Separate raw-data authorization

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` / `AND-EXP-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-022-AND-EXP-004-01 | Default export — **GIVEN** an ordinary export request **WHEN** the job is assembled **THEN** raw eye/ECG files are excluded and the manifest records the exclusion. | `services/api/tests/test_raw_export.py:234` — test_metadata_only_request_remains_default_scope_and_cannot_carry_raw_approval<br>`apps/mobile/tests/export-scope.test.ts:144` — rehashed orphan contexts, manifests, attempts, alcohol and report files fail exact selected scope | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-022-AND-EXP-004-02 | Raw consent is revoked during processing — **GIVEN** raw inclusion was initially allowed **WHEN** permission is revoked before delivery **THEN** the gateway blocks a subsequently initiated download and reports the changed scope or failed job; it makes no promise to recall bytes already authorized/delivered. | `services/api/tests/test_raw_export.py:291` — test_consent_revoked_during_storage_read_blocks_publication<br>`apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EXP-005 — Bound availability and clean temporary copies

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` / `AND-EXP-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-022-AND-EXP-005-01 | Expired export is reopened — **GIVEN** an export past expires_at **WHEN** the customer opens it **THEN** no new valid ticket is issued and a new export action is offered. | `apps/mobile/tests/domain.test.ts:435` — export rejects file tampering and traversal or hidden files before sharing<br>`apps/mobile/tests/export-projection.test.ts:75` — metadata nested event/frame/report fields stay bounded and cannot become hidden payload containers | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-022-AND-EXP-005-02 | Share sheet is canceled — **GIVEN** a downloaded temporary export **WHEN** the share sheet returns without sharing **THEN** the app schedules immediate cleanup and does not claim it sent the file anywhere. | `apps/mobile/tests/domain.test.ts:435` — export rejects file tampering and traversal or hidden files before sharing<br>`apps/mobile/tests/export-projection.test.ts:75` — metadata nested event/frame/report fields stay bounded and cannot become hidden payload containers | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `24`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-EXP-006 — Make jobs idempotent and failures visible

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` / `AND-EXP-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-022-AND-EXP-006-01 | Export request response is lost — **GIVEN** a created cloud job **WHEN** the same request is retried **THEN** the same job ID is returned. | `apps/mobile/tests/raw-export.test.ts:225` — cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-022-AND-EXP-006-02 | Artifact verification fails — **GIVEN** a selected permitted artifact whose bytes fail the stored hash **WHEN** the worker assembles the export **THEN** the job fails with a safe reason and no complete-download state is exposed. | `services/api/tests/test_raw_export.py:418` — test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial<br>`apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-EXP-007 — Prevent archive path and memory abuse

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md` / `AND-EXP-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-022-AND-EXP-007-01 | Profile text resembles a path — **GIVEN** text containing ../ or absolute-path characters in user data **WHEN** an export is generated **THEN** it remains JSON content and cannot control an archive entry name. | `apps/mobile/tests/export-scope.test.ts:384` — manifest file entry size fields are bound to the original local or cloud layout<br>`apps/mobile/tests/domain.test.ts:427` — empty all-data export contains profile metadata and no invented check | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-022-AND-EXP-007-02 | Export exceeds its configured bound — **GIVEN** selected data larger than the supported single-export limit **WHEN** the job validates size **THEN** it reports an explicit size failure and never silently omits records or invents an unimplemented partitioning workflow. | `services/api/tests/test_raw_export.py:283` — test_version_length_type_hash_and_read_limit_failure_never_returns_partial_file<br>`apps/mobile/tests/export-scope.test.ts:384` — manifest file entry size fields are bound to the original local or cloud layout | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

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
