# OTGD-010: verification plan

Canonical: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md`; SHA-256 `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/raw-recordings.spec.ts` — `2ada98a52caf63a835d979adc71bef5542795c5edbd72fc859cdb7975cbfd3b7`
- `apps/mobile/tests/export-scope.test.ts` — `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46`
- `apps/mobile/tests/raw-export.test.ts` — `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`
- `services/api/tests/test_operator_governance.py` — `4d512a3ad9f7c65b69ee09d94fb471799d1aff63a5bc4c34140526dcac280ae7`
- `services/api/tests/test_raw_export.py` — `7ee249d50b4f2bd684639b4340159f3f8eab2f25ede232c0d67ba89bfb7ec627`
- `services/api/tests/test_raw_retention.py` — `4f2115aa7b12c65d238c674d9568a1a64c1d9666a7b50f6543ee5e602d6923ae`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### RAW-EXP-001 — Independently approve the exact participant-copy purpose

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-001-01 | Recording exists without export approval — **GIVEN** an owned retained recording and current optional recording consent **WHEN** a participant requests its raw export without separate released authority **THEN** raw export is denied and metadata-only export remains available. | `services/api/tests/test_raw_export.py:234` — test_metadata_only_request_remains_default_scope_and_cannot_carry_raw_approval<br>`apps/mobile/tests/raw-export.test.ts:148` — server boundary terms remain bounded and optional sources cannot inherit recording consent or broaden selection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-001-02 | The reviewer is also the submitter — **GIVEN** a submitted raw-export version **WHEN** the same verified principal tries to approve or release it **THEN** the registry rejects the transition and no current export grant exists. | `services/api/tests/test_raw_export.py:222` — test_typed_authority_rejects_unapproved_purpose_and_unbounded_scope<br>`services/api/tests/test_raw_retention.py:849` — test_administrative_reports_require_their_own_approved_purpose | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-001-03 | Three distinct authorized principals release an exact grant — **GIVEN** current independently approved dependencies and a typed owner/generation grant **WHEN** distinct submitter, reviewer and releaser complete its real registry lifecycle **THEN** its immutable version and content hash admit only the exact approved scope. | `services/api/tests/test_operator_governance.py:191` — test_immutable_submission_three_principals_lifecycle_history_and_revision<br>`services/api/tests/test_raw_retention.py:849` — test_administrative_reports_require_their_own_approved_purpose | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### RAW-EXP-002 — Bound and paginate current export choices

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-002`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-002-01 | Nine valid authorities contain maximum-sized notices — **GIVEN** nine current independently released owned authorities **WHEN** the client follows each authority cursor **THEN** all nine are offered across bounded pages without response overflow. | `services/api/tests/test_raw_export.py:635` — test_individually_over_export_budget_source_is_not_offered<br>`apps/mobile/tests/export-scope.test.ts:275` — all nonmanifest structured records have the same 512 KiB bound before schema parsing | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-002-02 | A source exceeds the complete export byte cap — **GIVEN** a retained recording larger than its authority's uncompressed cap **WHEN** current export choices are requested **THEN** that source cannot be selected and other eligible choices remain usable. | `services/api/tests/test_raw_export.py:635` — test_individually_over_export_budget_source_is_not_offered<br>`apps/mobile/tests/raw-export.test.ts:148` — server boundary terms remain bounded and optional sources cannot inherit recording consent or broaden selection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `128`, `512 KiB`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### RAW-EXP-003 — Confirm a separate immutable raw-copy selection

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-003`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-003-01 | Consent to recording is reused as export confirmation — **GIVEN** the participant approved optional recording earlier **WHEN** raw export is requested without its separate confirmed export notice **THEN** the request fails without creating a raw job. | `apps/mobile/tests/raw-export.test.ts:148` — server boundary terms remain bounded and optional sources cannot inherit recording consent or broaden selection<br>`apps/mobile/e2e/raw-recordings.spec.ts:1104` — actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-003-02 | An accepted reply was lost and the grant is later retired — **GIVEN** an accepted raw export and its original request key/body **WHEN** the request is retried after authority retirement **THEN** current admission denies it rather than disclosing the stale approved scope. | `apps/mobile/tests/raw-export.test.ts:225` — cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt<br>`services/api/tests/test_raw_export.py:234` — test_metadata_only_request_remains_default_scope_and_cannot_carry_raw_approval | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-003-03 | A separately confirmed owned selection creates a stable job — **GIVEN** exact current authority and an explicitly acknowledged export notice **WHEN** the customer submits selected owned artifacts and retries the identical body/key **THEN** one pending job preserves the original selected sources and acknowledgement. | `apps/mobile/tests/raw-export.test.ts:225` — cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt<br>`apps/mobile/tests/export-scope.test.ts:112` — cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### RAW-EXP-004 — Pin selected retained sources

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-004`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-004-01 | The current key has a new S3 version — **GIVEN** an accepted pinned original source version **WHEN** a different current object version appears **THEN** worker reads only the verified accepted version and checks its actual bytes. | `services/api/tests/test_raw_retention.py:1060` — test_verified_raw_requires_exact_owned_codec_receipt_and_accepted_native_evidence<br>`services/api/tests/test_raw_export.py:319` — test_expiry_and_retention_are_hard_caps_and_generation_deletion_denies | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-004-02 | Withdrawal occurs during source retrieval — **GIVEN** a raw job reading outside a database transaction **WHEN** its participant consent is withdrawn before the read completes **THEN** post-read admission rejects publication and no current ZIP is exposed. | `services/api/tests/test_raw_export.py:291` — test_consent_revoked_during_storage_read_blocks_publication<br>`services/api/tests/test_raw_retention.py:424` — test_participant_raw_status_excludes_same_study_administrative_report | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `24`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### RAW-EXP-005 — Verify archive lineage and selected raw members

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-005`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-005-01 | A ZIP contains a rehashed unselected recording — **GIVEN** an authenticated job permits only recording A **WHEN** a well-formed rehashed ZIP includes recording B instead **THEN** the client rejects the archive rather than importing or sharing it. | `apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources<br>`apps/mobile/tests/export-scope.test.ts:307` — rehashed local manifest metadata cannot carry nested or invented unselected data | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-005-02 | An exact selected archive verifies against its authenticated job — **GIVEN** a completed job with exact approved source descriptors **WHEN** its ZIP preserves all selected structured lineage and raw versions/hashes/bytes **THEN** the archive inspector validates it and exposes only the approved selected contents. | `apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources<br>`apps/mobile/tests/export-scope.test.ts:103` — actual backend archive verifies original embedded evidence and both separate report revision companions | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### RAW-EXP-006 — Re-admit protected delivery and cut off revoked streams

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-006`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-006-01 | Expiry occurs while S3 download is delayed — **GIVEN** a currently approved completed export **WHEN** it expires before the storage read returns **THEN** post-read admission returns a denial with no ZIP bytes disclosed. | `services/api/tests/test_raw_export.py:418` — test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial<br>`apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-006-02 | Revocation follows the first delivery chunk — **GIVEN** a verified archive larger than 64 KiB **WHEN** raw permission is revoked after its first admitted chunk **THEN** the next admission fails and no second chunk is sent. | `services/api/tests/test_raw_export.py:568` — test_admitted_asgi_download_stops_at_next_64k_chunk_after_revocation<br>`apps/mobile/e2e/raw-recordings.spec.ts:1332` — raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-006-03 | An uninterrupted verified download succeeds — **GIVEN** current authority and a completed exact-version ZIP **WHEN** storage bytes and every delivery-boundary admission remain valid **THEN** the signed-in owner receives the complete hash-matching no-store attachment. | `services/api/tests/test_raw_export.py:598` — test_download_cancelled_before_first_generator_iteration_releases_buffer_slot<br>`apps/mobile/tests/raw-export.test.ts:148` — server boundary terms remain bounded and optional sources cannot inherit recording consent or broaden selection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### RAW-EXP-007 — Preserve terminal privacy receipts and recurring erasure

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-007`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-007-01 | A stale worker uploads after the first cleanup sweep — **GIVEN** revoked logical delivery and a completed first prefix sweep **WHEN** an older worker's output arrives later **THEN** the recurring sweep deletes its exact version and delivery remains denied. | `services/api/tests/test_raw_export.py:485` — test_http_revoked_cleanup_has_minimal_terminal_receipt<br>`apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-007-02 | The customer refreshes after raw-copy cleanup — **GIVEN** an owned revoked export after cleanup **WHEN** its status is refreshed **THEN** the terminal revoked receipt remains visible without grant or download metadata. | `services/api/tests/test_raw_export.py:485` — test_http_revoked_cleanup_has_minimal_terminal_receipt<br>`apps/mobile/e2e/raw-recordings.spec.ts:1223` — local revocation fence overrides old confirmed grant without claiming cleanup completion | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### RAW-EXP-008 — Bound the entire archive without partial omission

Normative acceptance source: `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md` / `RAW-EXP-008`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-010-RAW-EXP-008-01 | Raw sources fit but their structured evidence exceeds the cap — **GIVEN** raw files fit within the approved uncompressed byte limit **WHEN** adding selected structured records and the manifest exceeds that limit **THEN** the entire job fails without producing a partial downloadable archive. | `apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources<br>`apps/mobile/tests/export-scope.test.ts:275` — all nonmanifest structured records have the same 512 KiB bound before schema parsing | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-010-RAW-EXP-008-02 | The complete selected archive fits all approved bounds — **GIVEN** selected structured records, manifest and explicit raw sources within the narrower caps **WHEN** the fenced worker assembles and publishes the exact verified archive **THEN** the complete job succeeds without omitting a selected record or widening the limits. | `apps/mobile/tests/raw-export.test.ts:65` — actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources<br>`apps/mobile/tests/export-scope.test.ts:275` — all nonmanifest structured records have the same 512 KiB bound before schema parsing | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `50 MiB`, `512 KiB`, `64 MiB`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

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

# OTGD-010 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/authorized-raw-export/specs/raw-export-authorization/spec.md`; SHA256 `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-010/test-plan.md`. External review artifact only; PM controls import.

All 19 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-010-RAW-EXP-001-01 | Recording exists without export approval — - **GIVEN** an owned retained recording and current optional recording consent - **WHEN** a participant requests its raw export without separate released authority - **THEN** raw export is denied and metadata-only export remains available. | PARTIAL |
| OTGD-010-RAW-EXP-001-02 | The reviewer is also the submitter — - **GIVEN** a submitted raw-export version - **WHEN** the same verified principal tries to approve or release it - **THEN** the registry rejects the transition and no current export grant exists. | PASS |
| OTGD-010-RAW-EXP-001-03 | Three distinct authorized principals release an exact grant — - **GIVEN** current independently approved dependencies and a typed owner/generation grant - **WHEN** distinct submitter, reviewer and releaser complete its real registry lifecycle - **THEN** its immutable version and content hash admit only the exact approved scope. | PASS |
| OTGD-010-RAW-EXP-002-01 | Nine valid authorities contain maximum-sized notices — - **GIVEN** nine current independently released owned authorities - **WHEN** the client follows each authority cursor - **THEN** all nine are offered across bounded pages without response overflow. | PASS |
| OTGD-010-RAW-EXP-002-02 | A source exceeds the complete export byte cap — - **GIVEN** a retained recording larger than its authority's uncompressed cap - **WHEN** current export choices are requested - **THEN** that source cannot be selected and other eligible choices remain usable. | PASS |
| OTGD-010-RAW-EXP-003-01 | Consent to recording is reused as export confirmation — - **GIVEN** the participant approved optional recording earlier - **WHEN** raw export is requested without its separate confirmed export notice - **THEN** the request fails without creating a raw job. | PARTIAL |
| OTGD-010-RAW-EXP-003-02 | An accepted reply was lost and the grant is later retired — - **GIVEN** an accepted raw export and its original request key/body - **WHEN** the request is retried after authority retirement - **THEN** current admission denies it rather than disclosing the stale approved scope. | PASS |
| OTGD-010-RAW-EXP-003-03 | A separately confirmed owned selection creates a stable job — - **GIVEN** exact current authority and an explicitly acknowledged export notice - **WHEN** the customer submits selected owned artifacts and retries the identical body/key - **THEN** one pending job preserves the original selected sources and acknowledgement. | PARTIAL |
| OTGD-010-RAW-EXP-004-01 | The current key has a new S3 version — - **GIVEN** an accepted pinned original source version - **WHEN** a different current object version appears - **THEN** worker reads only the verified accepted version and checks its actual bytes. | PARTIAL |
| OTGD-010-RAW-EXP-004-02 | Withdrawal occurs during source retrieval — - **GIVEN** a raw job reading outside a database transaction - **WHEN** its participant consent is withdrawn before the read completes - **THEN** post-read admission rejects publication and no current ZIP is exposed. | PARTIAL |
| OTGD-010-RAW-EXP-005-01 | A ZIP contains a rehashed unselected recording — - **GIVEN** an authenticated job permits only recording A - **WHEN** a well-formed rehashed ZIP includes recording B instead - **THEN** the client rejects the archive rather than importing or sharing it. | PARTIAL |
| OTGD-010-RAW-EXP-005-02 | An exact selected archive verifies against its authenticated job — - **GIVEN** a completed job with exact approved source descriptors - **WHEN** its ZIP preserves all selected structured lineage and raw versions/hashes/bytes - **THEN** the archive inspector validates it and exposes only the approved selected contents. | PASS |
| OTGD-010-RAW-EXP-006-01 | Expiry occurs while S3 download is delayed — - **GIVEN** a currently approved completed export - **WHEN** it expires before the storage read returns - **THEN** post-read admission returns a denial with no ZIP bytes disclosed. | PASS |
| OTGD-010-RAW-EXP-006-02 | Revocation follows the first delivery chunk — - **GIVEN** a verified archive larger than 64 KiB - **WHEN** raw permission is revoked after its first admitted chunk - **THEN** the next admission fails and no second chunk is sent. | PASS |
| OTGD-010-RAW-EXP-006-03 | An uninterrupted verified download succeeds — - **GIVEN** current authority and a completed exact-version ZIP - **WHEN** storage bytes and every delivery-boundary admission remain valid - **THEN** the signed-in owner receives the complete hash-matching no-store attachment. | PASS |
| OTGD-010-RAW-EXP-007-01 | A stale worker uploads after the first cleanup sweep — - **GIVEN** revoked logical delivery and a completed first prefix sweep - **WHEN** an older worker's output arrives later - **THEN** the recurring sweep deletes its exact version and delivery remains denied. | PARTIAL |
| OTGD-010-RAW-EXP-007-02 | The customer refreshes after raw-copy cleanup — - **GIVEN** an owned revoked export after cleanup - **WHEN** its status is refreshed - **THEN** the terminal revoked receipt remains visible without grant or download metadata. | PASS |
| OTGD-010-RAW-EXP-008-01 | Raw sources fit but their structured evidence exceeds the cap — - **GIVEN** raw files fit within the approved uncompressed byte limit - **WHEN** adding selected structured records and the manifest exceeds that limit - **THEN** the entire job fails without producing a partial downloadable archive. | PASS |
| OTGD-010-RAW-EXP-008-02 | The complete selected archive fits all approved bounds — - **GIVEN** selected structured records, manifest and explicit raw sources within the narrower caps - **WHEN** the fenced worker assembles and publishes the exact verified archive - **THEN** the complete job succeeds without omitting a selected record or widening the limits. | PARTIAL |
