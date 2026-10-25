# OTGD-019: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md`; SHA-256 `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 6 individually identified requirements and 12 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Independent source assertion audits for this dossier: Alcohol dependency and acquisition-boundary audit; Rendered alcohol state/copy assertion audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 12 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"NOT_RUN": 2, "PARTIAL": 9, "PASS": 1}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-019-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.
