# OTGD-042: verification results

Canonical: `openspec/changes/qualified-participant-acquisition/specs/scoped-cardiac-authority/spec.md`; SHA-256 `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 8 individually identified requirements and 23 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

| Evidence class | Actual activity / outcome | Status |
|---|---|---|
| Planning inspection | Read canonical requirements/scenarios and shared contracts; indexed existing test symbols, CI gates and workflow commands. Source hashes appear in test-plan.md and shared report. This is not a passing acceptance test. | EXECUTED inspection only |
| Related automated checks | Commands and named assertions planned; no execution authorized in this assignment. Exit code, execution timestamp and artifact hash therefore absent. | NOT_RUN |
| Complete criterion coverage | Every case requires full acceptance assertions; related symbol matching is not proof of complete coverage. No-match cases are explicitly identified in the plan. | NOT_RUN |
| Browser/native/firmware/real dependencies/performance | Scope-specific prerequisites and commands in plan/shared report; no substitution from unit mocks or historical CI. | NOT_RUN |
| Physical/scientific/release qualification | No actual participant/device/study/assay/deployment/store evidence adopted; external approvals remain separate. | BLOCKED where applicable |

## Current case results

All stable case IDs in test-plan.md are NOT_RUN, except explicitly external-only cases which are BLOCKED on named acceptance evidence. On execution replace this aggregate with one result row per affected case, retaining command/procedure, environment, UTC time, observed outcome, exit code, evidence path/hash and exact candidate/test bindings. Do not turn expected THEN statements into observed results.

No completion, engineering/product signoff or council PASS follows from this planning record.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

Final-candidate acceptance remains **NOT_RUN**; actual focused author executions are preserved below separately and do not establish this whole dossier PASS. Source/content changes after a focused run require fresh admission and affected reruns.

Focused evaluation/alcohol report: `../../reports/evaluation-implementation.md` SHA-256 `4332b81097b9dd4cc25545c46f808554439cf7d61a2425caa77cffe52ee96f0c`. Author reports185 evaluation/admission cases PASS, 43 governance cases PASS against actual disposable PG, 1338 non-PG API cases PASS with20 deselected;10 new evaluation and11 alcohol cases included. Initial alcohol fixture run4 failures and SQLite full-governance2 mandatory-PG failures preserved. Verifier read new assertions and confirmed all5 reported source hashes match at audit; raw pytest stdout/JUnit not linked, so execution is author-reported and not independently replayed/adopted. Only exact mapped focused assertions receive that evidence scope, not all planned cases.

Independent source assertion audits for this dossier: EVAL-007 history/reference/authenticity audit. Full assertion/limit details are in test-plan.md.
