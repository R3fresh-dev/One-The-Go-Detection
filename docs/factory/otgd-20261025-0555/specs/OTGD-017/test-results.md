# OTGD-017: verification results

Canonical: `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md`; SHA-256 `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 3 individually identified requirements and 6 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

No new focused execution is adopted into this dossier in this audit. New UI/permissions/live/worker sources are WIP until author release and final bound execution; baseline firmware evidence retains its separate source/qualification limits.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 6 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"PARTIAL": 2, "PASS": 4}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-017-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-017 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/optional-raw-recording-lifecycle/specs/fictional-hosted-preview/spec.md`; SHA256 `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d`.

6 cases, 3 requirements: PARTIAL 2, PASS 4. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-017-AND-PREV-001-01 — PASS

Production enables the preview flag — - **GIVEN** APP_ENV=prod - **WHEN** the hosted preview flag is true - **THEN** configuration fails before building application code.

Current proof: Actual configuration test sets preview true for prod/qa/test and requires a throw; only matching local is accepted, with invalid flag text refused. Current named Node execution exists. Configuration refusal precedes any Expo build invocation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/hosted-preview.test.ts::the hosted preview build flag is local-only and cannot alter QA or production account behavior` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 93; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA db0f8558b6e8190d65efcf8de87187b462d74f6dcc2ea91249678be2c7f76d3f. Actual current source and raw evidence supply this disposition.

## OTGD-017-AND-PREV-001-02 — PARTIAL

An isolated local preview is packaged — - **GIVEN** APP_ENV=local and the matching compiled public environment - **WHEN** the hosted flag is accepted and the reviewed workflow packages the app - **THEN** its bundle and platform metadata identify fictional hosted mode and account and real acquisition services remain disabled.

Current proof: Config test asserts accepted local extra.hostedPreview and iOS infoPlist metadata, controller has disabled account/native paths; current preview CI jobs succeeded.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/hosted-preview.test.ts::the hosted preview build flag is local-only and cannot alter QA or production account behavior` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 93; 1 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- The same packaged bundle and Android/iOS platform metadata are not yet independently bound to downloaded binary bytes with reviewed provenance in this case; configuration output is narrower than final artifact admission. Actual installed native acquisition refusal also remains an OS prerequisite.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6cc448388a1e7da3278814a8c1b40b4f15935d355b995f748af83ca2c94423b6. Actual current source and raw evidence supply this disposition.

## OTGD-017-AND-PREV-002-01 — PASS

A customer saves a browser example — - **GIVEN** the standalone fictional preview - **WHEN** the customer acknowledges the notice, confirms context and saves a check - **THEN** the UI shows a measurement-only fictional record with no account, sensor or upload calls.

Current proof: Exported browser journey explicitly acknowledges notice/context and saves; banner visible, sign-in/upload/native acquisition controls absent, camera/Bluetooth spies and external request list remain empty. Controller companion asserts simulated source, measurement_only state, null probability, zero restore/network and no queue. These are current named browser/Node executions of fictional software only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/hosted-preview.spec.ts::standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records` — file SHA `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`, line 3; 4 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/hosted-preview.xml` — SHA256 `c416ab04fd7865c331eb9dfb7287e5f3d8933e422590fa2ddce38c7905702434`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 7e8e78b298a329e8900f38b4dc4d7191a2544fd9e48bdef91dd27033023f04dd. Actual current source and raw evidence supply this disposition.

## OTGD-017-AND-PREV-002-02 — PASS

A credential or hardware path is invoked directly — - **GIVEN** the standalone fictional preview - **WHEN** a caller attempts sign-in, credential recovery, API download, Bluetooth discovery or native reaction acquisition - **THEN** the request is refused before network or hardware access and no fictional record is promoted to a measurement.

Current proof: Controller test spies restore/network and rejects direct signIn, native task and measurement beginCheck; device scan returns unavailable. Dedicated disabled API test rejects supplied credentials and download before token-provider calls. Same fictional check remains simulated/measurement-only and no service calls occur. These are executable software route guards, not physical hardware qualification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::network-disabled API transport refuses even explicitly supplied credentials and cloud downloads` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 65; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c9c0d2342e754aa14da34979319cbd505ec544f7029f50e3942b6d11454ad590. Actual current source and raw evidence supply this disposition.

## OTGD-017-AND-PREV-003-01 — PASS

The browser reloads after saving an example — - **GIVEN** a fictional saved browser check - **WHEN** the page reloads - **THEN** its records and acknowledgment disappear and the first-use fictional flow returns.

Current proof: Actual exported-browser case saves then reloads, first-use Explore returns and resume absent. It reruns with zero external/sensor calls. Controller uses isolated fictional namespace and clearLocal empties saved checks. Browser memory persistence and first-use return only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/hosted-preview.spec.ts::standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records` — file SHA `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`, line 3; 4 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/hosted-preview.xml` — SHA256 `c416ab04fd7865c331eb9dfb7287e5f3d8933e422590fa2ddce38c7905702434`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 15a7c99c8cc9563d8ba118c587732e5436079830c6d48248bc92384a5cb9724c. Actual current source and raw evidence supply this disposition.

## OTGD-017-AND-PREV-003-02 — PARTIAL

A guest example is selected for account upload — - **GIVEN** a saved check in the isolated fictional guest namespace - **WHEN** a caller attempts account migration, import or upload - **THEN** the operation is refused and the account namespace receives no guest data.

Current proof: Dedicated fictional workspace and disabled transport are asserted; normal domain guest check refuses upload/owner promotion.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::guest check cannot upload and never acquires an account owner by sign-in` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 246; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No same-context test presents a saved hosted-preview check to account migration/import/upload and verifies unchanged account namespace digest. General guest/domain and network refusal do not prove that entire selected-example admission.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5407cf76fc114cad5bae44c99f835ef19a7c809dd76ded36be9980d29e57efb0. Actual current source and raw evidence supply this disposition.
