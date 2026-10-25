# OTGD-005: verification plan

Canonical: `openspec/changes/authorized-model-execution/specs/android-onboarding/spec.md`; SHA-256 `1b82b7101ffe6bf0538ffe24b814aea01369f322c9bb8e96808e05f0dd70e369`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/tests/controller.test.ts` — `e354d822120520b2336bacd98cac30b34de7921862cd4562342706358d9efa92`
- `apps/mobile/tests/research-result.test.ts` — `5e39d0bf4fb9376df15ae349da774b343dc0428d80fae35e6ee7f2b618ba33ea`
- `services/api/tests/test_cardiac_authority.py` — `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`
- `services/api/tests/test_model_admission.py` — `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`
- `services/api/tests/test_model_engine.py` — `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`
- `services/api/tests/test_model_optical_authority.py` — `597f44b706a05d5d730b7b4bd28f44e9cbe9d8d02c61cce256dd3eddf5c0150b`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-ONB-001 — Accurate first-run scope

Normative acceptance source: `openspec/changes/authorized-model-execution/specs/android-onboarding/spec.md` / `AND-ONB-001`.

Prerequisites and limits: NOT_RUN software acceptance on final frozen source; actual scientific/hardware/release approvals remain required when the canonical scope calls for them.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-005-AND-ONB-001-01 | Independent research admission — **WHEN** onboarding completes for an account whose separate current study and channel authority is admitted **THEN** the dashboard identifies authorized research access independently of the onboarding receipt | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/research-result.test.ts:163` — changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-005-AND-ONB-001-02 | Legacy or unapproved claim — **WHEN** a legacy result, local preference or valid-looking manifest claims research authority without current complete admission **THEN** no score is admitted and the historical measurement-only or unsupported-result boundary remains in force | `apps/mobile/tests/controller.test.ts:7` — guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload<br>`apps/mobile/tests/research-result.test.ts:144` — actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.


## Final corrected source evidence — e89897cc852a

# OTGD-005 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/authorized-model-execution/specs/android-onboarding/spec.md`; SHA256 `1b82b7101ffe6bf0538ffe24b814aea01369f322c9bb8e96808e05f0dd70e369`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-005/test-plan.md`. External review artifact only; PM controls import.

All 2 stable cases / 1 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-005-AND-ONB-001-01 | Independent research admission — - **WHEN** onboarding completes for an account whose separate current study and channel authority is admitted - **THEN** the dashboard identifies authorized research access independently of the onboarding receipt | PARTIAL |
| OTGD-005-AND-ONB-001-02 | Legacy or unapproved claim — - **WHEN** a legacy result, local preference or valid-looking manifest claims research authority without current complete admission - **THEN** no score is admitted and the historical measurement-only or unsupported-result boundary remains in force | PASS |
