# OTGD-034: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-results/spec.md`; SHA-256 `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 7 individually identified requirements and 14 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Independent source assertion audits for this dossier: Rendered alcohol state/copy assertion audit; Actual-process interruption probe source audit; Authenticated ordinary-web live test source audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 14 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"NOT_RUN": 3, "PARTIAL": 8, "PASS": 3}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-034-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-034 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-results/spec.md`; SHA256 `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba`.

14 cases, 7 requirements: NOT_RUN 3, PARTIAL 8, PASS 3. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-034-AND-RES-001-01 — PARTIAL

Completed offline measurement check — - **GIVEN** a locally finalized check with no server result - **WHEN** the result screen opens - **THEN** it shows the local measurement record and **Not synced**, with no claim that cloud analysis finished.

Current proof: Offline guest browser saves and shows Measurements saved/local finalized with no Upload; exported result is measurement_only/null probability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Canonical exact Not synced label and absence of cloud-analysis-complete claim are not asserted in current result UI test; local finalized may be truthful but is a different visible assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 01b215ec6656f0ed9c11e6d2b8081443c5a54740a3d6eca94ef4932a7c0d938c. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-001-02 — NOT_RUN

Pending server computation — - **GIVEN** GET result returns HTTP 202 - **WHEN** polling completes that request - **THEN** the app keeps **Analysis pending** and offers navigation without inventing a terminal result.

Current proof: Sync handles accepted finalize202 then immediate successful result200 in fixture.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::explicit upload registers evidence then snapshot then finalizes and verifies result` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 253; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No result GET202 fixture asserts Analysis pending retained and navigable without a terminal result; accepted finalize202 is not pending result202.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA cb974d8f6ec32aaf8c9b7dcc89904f44cc13a230e0ba6d0e400ffecb2671cf2d. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-002-01 — PARTIAL

Correctly linked measurement result — - **GIVEN** the expected session and frozen digest - **WHEN** a schema-valid measurement_only response arrives with matching references - **THEN** it is saved once and displayed for that check.

Current proof: Explicit upload sequence gets measurement result and marks one queue/check synced; parser validates frozen result links. Actual mounted Result/Controller/SyncEngine sameID+epoch pending/localmeasurement -> firstverifiedHR; one normal result GET then independent currentread, withheld until second200, exactly2GETs/no loop; visible manualrefresh establishes no-priortoken view and navigation invalidates.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::explicit upload registers evidence then snapshot then finalizes and verifies result` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 253; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::mounted pending or local measurement result starts fresh HR admission after same-ID normal sync completion` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 169; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::manual service refresh establishes current HR admission from a mounted pending result without a prior token` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 211; 4 current observation(s).
- `apps/mobile/tests/hr-read-admission.test.ts::explicit manual refresh can establish the active HR view when no previous token exists` — file SHA `83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8`, line 200; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- The measurement-only response must be saved once and displayed for that exact check. Current same-ID pending/measurement-to-HR transition is directly observed, but that does not itself assert the separate measurement-only save-once conjunction.

Prerequisite/evidence type: software_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Current actual80-case browser component gate executes same-ID pending/measurement first-HR arrival and visible manual recovery at both configured viewports. Controlled service boundary, not genuine registry/native OS.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8b4a06c9cb32b4f7a6caf59b4a6617beb1da692b85082f0e112e1bd172524cf7. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-002-02 — PARTIAL

Stale response after another check — - **GIVEN** a response references an earlier session - **WHEN** the current check screen receives it - **THEN** the response cannot replace the current check's result and the mismatch is recorded without raw health payloads.

Current proof: Result verifier rejects altered input hash/target/owner linkage and epoch protects a new account.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `apps/mobile/tests/sync.test.ts::a new account epoch prevents late network results writing into its workspace` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 352; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- A previous-session result arriving at current check screen with safe mismatch diagnostics/no raw health payload requires direct assertion. Generic hash mutation and owner epoch do not exercise same-account previous-session route.

Prerequisite/evidence type: software_assertion_or_integration_evidence, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3125c1bb48288a6181f6a8bcea7c31dfc83fd8559e1388ad1d6e5ee70fd70fbf. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-003-01 — PASS

Demo completes all steps — - **GIVEN** every simulated channel contains a plausible value - **WHEN** the check is finalized - **THEN** its result remains measurement_only with null probability and a demo badge.

Current proof: Actual guest browser fills synthetic saliva/eyes/cardiac, saves, exports and asserts source guest_demo, result measurement_only and probability null. Domain snapshot/manifest frozen and no queue. This establishes demo software completion without scientific normality inference.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/domain.test.ts::save freezes all evidence and never queues upload` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 233; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c1151ef630bff100b29498d75f8bb60d807c2926b7d8e6c0c4b76ceaaaf360d3. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-003-02 — PASS

Client requests research by changing a field — - **GIVEN** an otherwise valid-shaped research_estimate or an operator record claiming an active model - **WHEN** any current result path evaluates it - **THEN** the service executes no model and the app rejects the unsupported estimate without displaying its probability.

Current proof: Under canonical shared contracts section1 and authorized-model-execution delta, this historical row means legacy/unadmitted research fields cannot confer model authority. Current changed-proof/guest/synthetic mutation matrix refuses; server current authority refusals return null probability. Independently admitted1.1 software is governed by later MODEL requirements, not prohibited by this historical wording. D004 accepted narrowing; no scientific authorization follows.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 76da9fbf00a5e076d2817a9844bb8438c07e3921b6e792b7549bd4e790bbb22e. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-004-01 — PARTIAL

Below quantification — - **GIVEN** THC_COOH has qualifier below_loq and a stated LOQ - **WHEN** its card renders - **THEN** it shows below-quantification wording and the limit, with no exact numeric concentration or inferred detection claim.

Current proof: Formatter below_loq explicitly outputs limit<0.003ng/mL, preserves null concentration/input bytes and supplied LOD.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::below LOQ displays the supplied bound without creating a concentration or rounding it to zero` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 23; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Source fixture analyte is OH11_THC; canonical THC_COOH rendered card with exact below-quantification/no detection inference is not a named component assertion. Pure generic formatter arithmetic is established, exact card/analyte conjunction remains.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7fd9d493f1caf5ba74fb72c16575795c50e0fc665a7b3c97f5a8b7a34afbb49c. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-004-02 — PASS

Unrun channel — - **GIVEN** OH11_THC is not_measured - **WHEN** measurements are expanded - **THEN** the app shows **Not measured**, not **Negative**.

Current proof: Formatter fixture is OH11_THC; not_measured explicitly yields Not measured, distinct from not_detected/invalid/below_loq/above_range. Current named pure display function runs; no negative result is invented.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::every supported censored/missing qualifier has distinct human-readable semantics` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 50; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 67a8d5e325a71cf83871c2c0f776bc80a4abb9dd6eb11bf8780711f7441c1495. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-005-01 — PARTIAL

Delayed laboratory result — - **GIVEN** analysis finishes the following day - **WHEN** the result arrives - **THEN** the original collection date remains the check's date and the later analysis time is visible.

Current proof: Formatter displays separate collected/measured UTC values, report companion keeps original target and reanalysis identity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual next-day report arrival→result screen retains check collection date and visibly later analysis time is not asserted as one current route; generic formatter values differ by1hour and report parser is not UI.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a1629e455bca9e285470869303d55275b4068c878c947215a5d2277a1fa5eb4d. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-005-02 — PARTIAL

Linked reanalysis — - **GIVEN** a permitted newer result replaces an earlier result - **WHEN** history is opened - **THEN** both result identities remain reconstructable and the current display identifies the newer result's version.

Current proof: Actual backend-wire chain parses correction+reanalysis, links replaces_result_id through original, keeps original digest/target; incomplete/regressed chain refuses.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::known incomplete report cache blocks device exports and append-only cache cannot regress` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 179; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- History opened with newer revision must visibly identify current version while both result IDs reconstructable; parser/revision cache assertions do not establish rendered history selection/version copy.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3deafe3859a965518a4099370bdaa674a1bb192c5552f46ab2c8cf79fdac4013. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-006-01 — PARTIAL

Interrupted reaction task — - **GIVEN** a required task is invalid due to backgrounding - **WHEN** the completion summary opens - **THEN** it names the interrupted task and, if already finalized, offers Start replacement check with a new UUID/time and no carried-forward physical acquisitions; the original result/hash remain unchanged.

Current proof: Interrupted domain task keeps invalid/null aggregates; replacement helper preserves original digest, distinct sample/target and bidirectional links; browser invalid ECG supports replacement UI.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).
- `apps/mobile/tests/replacements.test.ts::local original and replacement links are bidirectional without changing either snapshot` — file SHA `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233`, line 47; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 142; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Exact interrupted required task summary→replacement newUUID/time/no carried physical acquisition and unchanged original result/hash is not one context; ECG invalid browser plus empty-guest replacement math is narrower. Actual OS interruption also external.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 70bebf2a13f9ef64501cf5cf90a16bf15a00fd502b069f9b6b2b7e39d482200f. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-006-02 — NOT_RUN

Unknown server reason — - **GIVEN** a newer service returns an unknown reason code - **WHEN** the app displays the result - **THEN** it shows a generic unavailable explanation and diagnostic request ID without silently treating the result as valid.

Current proof: Diagnostics sanitizer permits bounded request IDs and generic categories, rejects raw payload.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::support diagnostics copy only bounded explicit fields, never an error payload` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No unknown result reason-code current UI case asserts generic unavailable explanation, requestID and no valid-state promotion. Formatter unknown measurement qualifier is a different input contract.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA f403fc42f0d2b66c48d85fba124c70c3cfb1ab7b56bdc5f7e5e6d93c5334f6b7. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-007-01 — NOT_RUN

Temporary server outage — - **GIVEN** the result endpoint returns 503 - **WHEN** automatic retries exhaust the configured budget - **THEN** the record remains pending and a retry action appears; the local check is preserved.

Current proof: Sync catch retains retryable queue and frozen evidence; current mapped tests exercise conflict, not result503 budget exhaustion.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::conflict and stale generation stop automatic replay without changing frozen evidence` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 305; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Need actual result endpoint503 through configured retry budget, pending local record preserved and visible manual retry. No current exact assertion located.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 8c1c55d8d35c26460f8810e6ad55814439eb610cce5da3bea36a6ef53ac451b1. Actual current source and raw evidence supply this disposition.

## OTGD-034-AND-RES-007-02 — PARTIAL

Account changes during polling — - **GIVEN** an outstanding result request for account A - **WHEN** the app signs into account B - **THEN** A's request is canceled or ignored and its result never enters B's visible state.

Current proof: Actual deferred network response after epoch change leaves new workspace untouched and old queue unresolved.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::a new account epoch prevents late network results writing into its workspace` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 352; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Current fixture defers registration response, not result polling. Exact outstanding A result request→B sign-in with no A result entering B visible state remains unproved.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8e9ec71671fb24eed0d7f252450648d4886e0036abae199cc8b0adb61a6d45f0. Actual current source and raw evidence supply this disposition.
