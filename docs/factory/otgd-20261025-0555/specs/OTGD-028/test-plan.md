# OTGD-028: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-history/spec.md`; SHA-256 `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/components.spec.ts` — `725effb97f2e9195340fd6370b8491065eabdf849ce5c5680974c39cc2125c53`
- `apps/mobile/tests/export-scope.test.ts` — `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46`
- `apps/mobile/tests/generation-cache.test.ts` — `2a30b7da6606d73d185be5efed38968469e3fcde816063890f8e63bd7b32d756`
- `apps/mobile/tests/measurement-format.test.ts` — `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`
- `apps/mobile/tests/replacements.test.ts` — `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233`
- `apps/mobile/tests/report-revisions.test.ts` — `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`
- `apps/mobile/tests/support-history.test.ts` — `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`
- `apps/mobile/tests/workspace-scope.test.ts` — `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_replacement_links.py` — `e6091da29dd66c1f496bf9857bd70c8b73bceebf61494014aa3ab9ebec74597b`
- `services/api/tests/test_report_revisions.py` — `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-HIST-001 — Correct ownership and provenance

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-history/spec.md` / `AND-HIST-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-028-AND-HIST-001-01 | hist-demo-isolation — **GIVEN** both demo and account checks exist on the device **WHEN** account History opens **THEN** only authorized account checks are listed and demo rows require an explicit switch. | `apps/mobile/tests/support-history.test.ts:70` — history detail round-trip keeps filters, selected IDs and scroll only in the current workspace epoch<br>`apps/mobile/tests/workspace-scope.test.ts:31` — delayed history, job or study responses cannot publish into another account | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-001-02 | hist-cross-account-id — **GIVEN** an account receives a deep link to another account's session ID **WHEN** detail is requested **THEN** no snapshot, profile, existence-revealing title, or measurement is disclosed. | `apps/mobile/tests/support-history.test.ts:70` — history detail round-trip keeps filters, selected IDs and scroll only in the current workspace epoch<br>`apps/mobile/tests/workspace-scope.test.ts:31` — delayed history, job or study responses cannot publish into another account | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HIST-002 — Stable pagination and deduplication

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-history/spec.md` / `AND-HIST-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-028-AND-HIST-002-01 | hist-new-record-between-pages — **GIVEN** page one has loaded and a new check is finalized **WHEN** page two is requested with the original cursor **THEN** existing rows are neither duplicated nor skipped and the new check appears after refresh. | `apps/mobile/tests/replacements.test.ts:117` — bounded replacement pages reject duplicate/self links and preserve explicit remaining cursor<br>`apps/mobile/tests/export-scope.test.ts:112` — cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-002-02 | hist-local-server-same-check — **GIVEN** a local pending row is later returned by the server with the same UUID **WHEN** reconciliation completes **THEN** one row remains with updated sync status and unchanged source identity. | `apps/mobile/tests/support-history.test.ts:96` — pending sync means explicitly requested delivery, not local saves or retired records<br>`apps/mobile/tests/report-revisions.test.ts:246` — detail rejects a changing navigation chain without overwriting the immutable original | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HIST-003 — Faithful state, qualifier, and time display

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-history/spec.md` / `AND-HIST-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-028-AND-HIST-003-01 | hist-below-loq — **GIVEN** THC-COOH has qualifier below_loq with no quantified value **WHEN** detail is opened **THEN** it reads “Below quantification limit” with the reported limit when available, and no 0 ng/mL or inferred detection claim appears. | `apps/mobile/tests/measurement-format.test.ts:65` — only quantified results display a numeric concentration, preserving a real zero if reported<br>`apps/mobile/tests/report-revisions.test.ts:133` — rehashed report changes cannot move specimen collection, reuse prior analytical identities or misstate original units | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-003-02 | hist-delayed-laboratory-result — **GIVEN** a sample collected Monday was analyzed Wednesday **WHEN** its result is viewed Thursday **THEN** all relevant dates are distinct and the laboratory result is not described as a Thursday physiological assessment. | `apps/mobile/tests/measurement-format.test.ts:50` — every supported censored/missing qualifier has distinct human-readable semantics<br>`services/api/tests/test_report_revisions.py:793` — test_uncollected_specimen_is_refused_but_collected_empty_report_accepts_later_analysis | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-003-03 | hist-linked-research-estimate-is-still-unsupported — **GIVEN** an authenticated account receives a schema-valid research_estimate with matching session and digest **WHEN** History renders its detail **THEN** the app shows the unsupported-result state without displaying probability, classification, or a research-estimate card. | `apps/mobile/tests/measurement-format.test.ts:50` — every supported censored/missing qualifier has distinct human-readable semantics<br>`services/api/tests/test_api.py:429` — test_current_research_estimate_rejected_from_history | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HIST-004 — Immutable records and linked corrections

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-history/spec.md` / `AND-HIST-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-028-AND-HIST-004-01 | hist-profile-edited-later — **GIVEN** a historical check contains profile revision A **WHEN** current profile revision B is saved **THEN** historical detail continues to display A's values and acquisition context. | `apps/mobile/tests/export-scope.test.ts:112` — cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache<br>`services/api/tests/test_report_revisions.py:919` — test_saliva_free_finalized_check_lists_no_revisions_and_preserves_null_collection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-004-02 | hist-correction-linked — **GIVEN** a reviewed correction supersedes a finalized record **WHEN** either version is opened **THEN** the original remains readable and a labeled link identifies the other version without overwriting it. | `services/api/tests/test_report_revisions.py:1364` — test_deletion_retires_revisions_and_scrubs_both_record_kinds<br>`apps/mobile/tests/report-revisions.test.ts:246` — detail rejects a changing navigation chain without overwriting the immutable original | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HIST-005 — Offline detail and bounded retry

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-history/spec.md` / `AND-HIST-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-028-AND-HIST-005-01 | hist-offline-cached-detail — **GIVEN** an encrypted cached snapshot and no network **WHEN** its row is selected after local unlock **THEN** the stored snapshot is displayed with its cached state and no remote result is invented. | `apps/mobile/tests/replacements.test.ts:182` — a remote draft with an uploaded snapshot is not treated as a frozen readable result<br>`apps/mobile/tests/support-history.test.ts:70` — history detail round-trip keeps filters, selected IDs and scroll only in the current workspace epoch | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-005-02 | hist-offline-uncached-detail — **GIVEN** only a list summary is cached **WHEN** the user opens detail offline **THEN** the app explains unavailability and does not fill the screen from unrelated fixtures or another check. | `apps/mobile/tests/report-revisions.test.ts:74` — report list rejects another generation, changed original time, duplicate IDs, gaps and mutable result identity<br>`apps/mobile/tests/export-scope.test.ts:168` — rehashed extra profile version and unrelated current profile are rejected in a single-check archive | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-005-03 | hist-signed-out-device-unlock-is-insufficient — **GIVEN** A retained encrypted history when signing out **WHEN** the user opens the app offline and passes device unlock **THEN** A's history stays locked until the same issuer and subject reauthenticate; other workspaces remain separate. | `apps/mobile/tests/generation-cache.test.ts:188` — all-record device export excludes tombstoned and retired-generation retained records<br>`apps/mobile/tests/measurement-format.test.ts:99` — original report units, laboratory correction, matrix and separate times remain visible | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HIST-006 — Pending operations and deletion reconciliation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-history/spec.md` / `AND-HIST-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-028-AND-HIST-006-01 | hist-pending-filter — **GIVEN** two locally queued checks and three synchronized checks **WHEN** Pending sync is selected **THEN** only the two queue-owned checks appear and the label states that this is this device's queue. | `apps/mobile/tests/export-scope.test.ts:112` — cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache<br>`apps/mobile/tests/support-history.test.ts:96` — pending sync means explicitly requested delivery, not local saves or retired records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-006-02 | hist-delete-race — **GIVEN** a detail request is in flight when its deletion is accepted **WHEN** the old response arrives **THEN** it is discarded according to the deletion generation/tombstone and cannot repopulate History. | `apps/mobile/tests/support-history.test.ts:96` — pending sync means explicitly requested delivery, not local saves or retired records<br>`apps/mobile/tests/export-scope.test.ts:112` — cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-006-03 | hist-single-check-export-scope-survives-source-change — **GIVEN** History starts Export this check for A while unrelated checks B and C exist **WHEN** the user changes This device to Synced records or resumes after reauthentication **THEN** the selected scope remains only A and related authorized evidence; B and C cannot enter the archive without a new expanded-scope summary and confirmation. | `apps/mobile/tests/export-scope.test.ts:168` — rehashed extra profile version and unrelated current profile are rejected in a single-check archive<br>`apps/mobile/tests/support-history.test.ts:96` — pending sync means explicitly requested delivery, not local saves or retired records | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-HIST-007 — Accessible records and iOS parity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-history/spec.md` / `AND-HIST-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-028-AND-HIST-007-01 | hist-large-text-detail — **GIVEN** 200% font scaling and a narrow Android display **WHEN** a saliva detail section contains all three analytes **THEN** names, values, units, and qualifiers remain legible and reachable without clipped columns. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes<br>`apps/mobile/tests/report-revisions.test.ts:246` — detail rejects a changing navigation chain without overwriting the immutable original | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-028-AND-HIST-007-02 | hist-ios-back-position — **GIVEN** the iOS user opens a row after loading three pages **WHEN** they navigate back **THEN** the same selected row and list position are restored with no duplicated page fetch. ## Acceptance evidence Required evidence: cross-account denial, stable-cursor/concurrent-insert tests, local/server deduplication, qualifier/unit/time fixtures, profile immutability, supersession navigation, offline cache/no-cache paths, deletion race, and Android/iOS accessibility review. A history record is evidence of recorded measurements and provenance only; its presence does not establish clinical accuracy. | `apps/mobile/e2e/components.spec.ts:217` — navigation and theme components expose selected state at both viewport sizes<br>`apps/mobile/tests/support-history.test.ts:115` — mixed local and synced history uses acquisition time and stable identity ties | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Rendered alcohol state/copy assertion audit

Mapped existing cases: OTGD-019-AND-ALC-002/003/005/006 cases; related APP-012/013, AND-HIST-003 and AND-RES-004.

Assertion adequacy inspected: Read actual AlcoholScreen/ResultsScreen/HistoryScreen/ResultDetail fixture and assertions in raw-recordings.spec.ts. Measurement/guest/research variants retain unavailable qualified hardware, mg/L and model-specific co-use copy, replace stale unconditional classification statement. Six value/source variants (zero, low, below_loq, not_detected, invalid, simulated) traverse actual history/result/detail; assertions retain units, qualifier/source/time, dashes for null, separate alcohol meaning and no automatic BAC/impairment adjustment. Positive driving/legal-clearance/combined-score patterns absent; truthful clearance Unavailable remains visible.

Remaining limits: Controlled component inputs are hypothetical reporting records, not acquired sensor data; research fixture is not newly qualified scientific authority. Notification/OS-wide copy is not exhaustively proved by these component surfaces. Writer active; new component tests NOT_RUN in verifier final scope, author final report pending.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.
