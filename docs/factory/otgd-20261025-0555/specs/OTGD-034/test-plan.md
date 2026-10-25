# OTGD-034: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-results/spec.md`; SHA-256 `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/e2e/mobile.spec.ts` — `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`
- `apps/mobile/tests/measurement-format.test.ts` — `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`
- `apps/mobile/tests/replacements.test.ts` — `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233`
- `apps/mobile/tests/report-revisions.test.ts` — `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`
- `apps/mobile/tests/research-result.test.ts` — `5e39d0bf4fb9376df15ae349da774b343dc0428d80fae35e6ee7f2b618ba33ea`
- `apps/mobile/tests/sync.test.ts` — `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`
- `services/api/tests/test_api.py` — `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`
- `services/api/tests/test_cardiac_authority.py` — `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`
- `services/api/tests/test_model_admission.py` — `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`
- `services/api/tests/test_model_engine.py` — `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`
- `services/api/tests/test_model_optical_authority.py` — `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-RES-001 — Separate capture outcome from delivery status

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-results/spec.md` / `AND-RES-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-034-AND-RES-001-01 | Completed offline measurement check — **GIVEN** a locally finalized check with no server result **WHEN** the result screen opens **THEN** it shows the local measurement record and **Not synced**, with no claim that cloud analysis finished. | `apps/mobile/e2e/mobile.spec.ts:6` — guest completes a measurement-only check, exact export and privacy/settings journey | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-034-AND-RES-001-02 | Pending server computation — **GIVEN** GET result returns HTTP 202 **WHEN** polling completes that request **THEN** the app keeps **Analysis pending** and offers navigation without inventing a terminal result. | `apps/mobile/tests/report-revisions.test.ts:246` — detail rejects a changing navigation chain without overwriting the immutable original<br>`apps/mobile/tests/replacements.test.ts:47` — local original and replacement links are bidirectional without changing either snapshot | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RES-002 — Enforce result contract and linkage

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-results/spec.md` / `AND-RES-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-034-AND-RES-002-01 | Correctly linked measurement result — **GIVEN** the expected session and frozen digest **WHEN** a schema-valid measurement_only response arrives with matching references **THEN** it is saved once and displayed for that check. | `apps/mobile/e2e/mobile.spec.ts:6` — guest completes a measurement-only check, exact export and privacy/settings journey<br>`apps/mobile/tests/replacements.test.ts:182` — a remote draft with an uploaded snapshot is not treated as a frozen readable result | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-034-AND-RES-002-02 | Stale response after another check — **GIVEN** a response references an earlier session **WHEN** the current check screen receives it **THEN** the response cannot replace the current check's result and the mismatch is recorded without raw health payloads. | `apps/mobile/tests/report-revisions.test.ts:74` — report list rejects another generation, changed original time, duplicate IDs, gaps and mutable result identity<br>`apps/mobile/tests/sync.test.ts:305` — conflict and stale generation stop automatic replay without changing frozen evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-RES-003 — Keep impairment inference closed

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-results/spec.md` / `AND-RES-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-034-AND-RES-003-01 | Demo completes all steps — **GIVEN** every simulated channel contains a plausible value **WHEN** the check is finalized **THEN** its result remains measurement_only with null probability and a demo badge. | `apps/mobile/e2e/mobile.spec.ts:6` — guest completes a measurement-only check, exact export and privacy/settings journey<br>`apps/mobile/tests/research-result.test.ts:218` — a verified uncertainty band requires null abstention rather than a probability or optimistic classification | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-034-AND-RES-003-02 | Client requests research by changing a field — **GIVEN** an otherwise valid-shaped research_estimate or an operator record claiming an active model **WHEN** any current result path evaluates it **THEN** the service executes no model and the app rejects the unsupported estimate without displaying its probability. | `apps/mobile/tests/research-result.test.ts:218` — a verified uncertainty band requires null abstention rather than a probability or optimistic classification<br>`services/api/tests/test_api.py:429` — test_current_research_estimate_rejected_from_history | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RES-004 — Preserve qualifiers and missingness

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-results/spec.md` / `AND-RES-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-034-AND-RES-004-01 | Below quantification — **GIVEN** THC_COOH has qualifier below_loq and a stated LOQ **WHEN** its card renders **THEN** it shows below-quantification wording and the limit, with no exact numeric concentration or inferred detection claim. | `apps/mobile/tests/measurement-format.test.ts:23` — below LOQ displays the supplied bound without creating a concentration or rounding it to zero | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-034-AND-RES-004-02 | Unrun channel — **GIVEN** OH11_THC is not_measured **WHEN** measurements are expanded **THEN** the app shows **Not measured**, not **Negative**. | `apps/mobile/tests/measurement-format.test.ts:50` — every supported censored/missing qualifier has distinct human-readable semantics | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RES-005 — Preserve historical time and immutability

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-results/spec.md` / `AND-RES-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-034-AND-RES-005-01 | Delayed laboratory result — **GIVEN** analysis finishes the following day **WHEN** the result arrives **THEN** the original collection date remains the check's date and the later analysis time is visible. | `apps/mobile/tests/measurement-format.test.ts:99` — original report units, laboratory correction, matrix and separate times remain visible<br>`apps/mobile/tests/report-revisions.test.ts:164` — rehashed revised results cannot promote an originally invalid check or relabel evaluation as a new assessment | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-034-AND-RES-005-02 | Linked reanalysis — **GIVEN** a permitted newer result replaces an earlier result **WHEN** history is opened **THEN** both result identities remain reconstructable and the current display identifies the newer result's version. | `services/api/tests/test_model_engine.py:437` — test_training_evaluation_policy_and_result_proof_are_bound<br>`apps/mobile/tests/measurement-format.test.ts:99` — original report units, laboratory correction, matrix and separate times remain visible | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RES-006 — Provide actionable invalid and inconclusive states

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-results/spec.md` / `AND-RES-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-034-AND-RES-006-01 | Interrupted reaction task — **GIVEN** a required task is invalid due to backgrounding **WHEN** the completion summary opens **THEN** it names the interrupted task and, if already finalized, offers Start replacement check with a new UUID/time and no carried-forward physical acquisitions; the original result/hash remain unchanged. | `apps/mobile/e2e/mobile.spec.ts:142` — live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit<br>`apps/mobile/tests/report-revisions.test.ts:46` — actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-034-AND-RES-006-02 | Unknown server reason — **GIVEN** a newer service returns an unknown reason code **WHEN** the app displays the result **THEN** it shows a generic unavailable explanation and diagnostic request ID without silently treating the result as valid. | `apps/mobile/tests/measurement-format.test.ts:23` — below LOQ displays the supplied bound without creating a concentration or rounding it to zero<br>`apps/mobile/tests/report-revisions.test.ts:101` — unknown companion fields/versions and inference output fail even after descriptor and result hashes are recomputed | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-RES-007 — Use bounded and cancelable result polling

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-results/spec.md` / `AND-RES-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-034-AND-RES-007-01 | Temporary server outage — **GIVEN** the result endpoint returns 503 **WHEN** automatic retries exhaust the configured budget **THEN** the record remains pending and a retry action appears; the local check is preserved. | `apps/mobile/tests/sync.test.ts:305` — conflict and stale generation stop automatic replay without changing frozen evidence<br>`apps/mobile/tests/research-result.test.ts:144` — actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-034-AND-RES-007-02 | Account changes during polling — **GIVEN** an outstanding result request for account A **WHEN** the app signs into account B **THEN** A's request is canceled or ignored and its result never enters B's visible state. | `apps/mobile/tests/sync.test.ts:352` — a new account epoch prevents late network results writing into its workspace | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Rendered alcohol state/copy assertion audit

Mapped existing cases: OTGD-019-AND-ALC-002/003/005/006 cases; related APP-012/013, AND-HIST-003 and AND-RES-004.

Assertion adequacy inspected: Read actual AlcoholScreen/ResultsScreen/HistoryScreen/ResultDetail fixture and assertions in raw-recordings.spec.ts. Measurement/guest/research variants retain unavailable qualified hardware, mg/L and model-specific co-use copy, replace stale unconditional classification statement. Six value/source variants (zero, low, below_loq, not_detected, invalid, simulated) traverse actual history/result/detail; assertions retain units, qualifier/source/time, dashes for null, separate alcohol meaning and no automatic BAC/impairment adjustment. Positive driving/legal-clearance/combined-score patterns absent; truthful clearance Unavailable remains visible.

Remaining limits: Controlled component inputs are hypothetical reporting records, not acquired sensor data; research fixture is not newly qualified scientific authority. Notification/OS-wide copy is not exhaustively proved by these component surfaces. Writer active; new component tests NOT_RUN in verifier final scope, author final report pending.

### Actual-process interruption probe source audit

Mapped existing cases: Shared platform §§6/10; related OPS-002/003/005/006, RAW-EXP-004/006/007, RECOVERY-001, AND-SYNC-003/005/006, AND-PRIV-005, AND-RES-002.

Assertion adequacy inspected: Read worker_interrupt_probe.py validate_target, child_worker, OwnedChild, kill_case, verify_output, stale_case and budget_case. Exact separate disposable local DB/namespace/queues/buckets; wrappers delegate real production claim/commit/S3/SQS/run_job; only owned spawned PID receives signals; SIGKILL exit and actual barriers verified. Five export kill stages plus result after-claim/after-commit; unchanged outbox and winning fence/attempt/output assertions; version-pinned bytes/hash. SIGSTOP lets real120s lease expire; new generation denies stale output; SIGCONT late writer must lease_lost; real expiry cleanup removes only own versions and preserves neighbor. Real malformed durable work five-claim/backoff and actual five-receive120s DLQ redrive preserve production constants.

Remaining limits: Source inspected only; probe and integration WIP, no real process/recovery execution adopted. Unit harness targeting/barrier tests do not prove actual recovery. No study withdrawal or old-backup/cloud restore inferred from generation transaction. PM must assign isolated fixture setup and run after writer release; all resource mutations PM-only. Workflow timeout must fit real production waits; integration pending.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.


## Final corrected source evidence — e89897cc852a

# OTGD-034 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-results/spec.md`; SHA256 `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-034/test-plan.md`. External review artifact only; PM controls import.

All 14 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-034-AND-RES-001-01 | Completed offline measurement check — - **GIVEN** a locally finalized check with no server result - **WHEN** the result screen opens - **THEN** it shows the local measurement record and **Not synced**, with no claim that cloud analysis finished. | PARTIAL |
| OTGD-034-AND-RES-001-02 | Pending server computation — - **GIVEN** GET result returns HTTP 202 - **WHEN** polling completes that request - **THEN** the app keeps **Analysis pending** and offers navigation without inventing a terminal result. | NOT_RUN |
| OTGD-034-AND-RES-002-01 | Correctly linked measurement result — - **GIVEN** the expected session and frozen digest - **WHEN** a schema-valid measurement_only response arrives with matching references - **THEN** it is saved once and displayed for that check. | PARTIAL |
| OTGD-034-AND-RES-002-02 | Stale response after another check — - **GIVEN** a response references an earlier session - **WHEN** the current check screen receives it - **THEN** the response cannot replace the current check's result and the mismatch is recorded without raw health payloads. | PARTIAL |
| OTGD-034-AND-RES-003-01 | Demo completes all steps — - **GIVEN** every simulated channel contains a plausible value - **WHEN** the check is finalized - **THEN** its result remains measurement_only with null probability and a demo badge. | PASS |
| OTGD-034-AND-RES-003-02 | Client requests research by changing a field — - **GIVEN** an otherwise valid-shaped research_estimate or an operator record claiming an active model - **WHEN** any current result path evaluates it - **THEN** the service executes no model and the app rejects the unsupported estimate without displaying its probability. | PASS |
| OTGD-034-AND-RES-004-01 | Below quantification — - **GIVEN** THC_COOH has qualifier below_loq and a stated LOQ - **WHEN** its card renders - **THEN** it shows below-quantification wording and the limit, with no exact numeric concentration or inferred detection claim. | PARTIAL |
| OTGD-034-AND-RES-004-02 | Unrun channel — - **GIVEN** OH11_THC is not_measured - **WHEN** measurements are expanded - **THEN** the app shows **Not measured**, not **Negative**. | PASS |
| OTGD-034-AND-RES-005-01 | Delayed laboratory result — - **GIVEN** analysis finishes the following day - **WHEN** the result arrives - **THEN** the original collection date remains the check's date and the later analysis time is visible. | PARTIAL |
| OTGD-034-AND-RES-005-02 | Linked reanalysis — - **GIVEN** a permitted newer result replaces an earlier result - **WHEN** history is opened - **THEN** both result identities remain reconstructable and the current display identifies the newer result's version. | PARTIAL |
| OTGD-034-AND-RES-006-01 | Interrupted reaction task — - **GIVEN** a required task is invalid due to backgrounding - **WHEN** the completion summary opens - **THEN** it names the interrupted task and, if already finalized, offers Start replacement check with a new UUID/time and no carried-forward physical acquisitions; the original result/hash remain unchanged. | PARTIAL |
| OTGD-034-AND-RES-006-02 | Unknown server reason — - **GIVEN** a newer service returns an unknown reason code - **WHEN** the app displays the result - **THEN** it shows a generic unavailable explanation and diagnostic request ID without silently treating the result as valid. | NOT_RUN |
| OTGD-034-AND-RES-007-01 | Temporary server outage — - **GIVEN** the result endpoint returns 503 - **WHEN** automatic retries exhaust the configured budget - **THEN** the record remains pending and a retry action appears; the local check is preserved. | NOT_RUN |
| OTGD-034-AND-RES-007-02 | Account changes during polling — - **GIVEN** an outstanding result request for account A - **WHEN** the app signs into account B - **THEN** A's request is canceled or ignored and its result never enters B's visible state. | PARTIAL |
