# OTGD-032: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-profile/spec.md`; SHA-256 `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 7 individually identified requirements and 16 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Independent source assertion audits for this dossier: Authenticated ordinary-web live test source audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 16 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"PARTIAL": 15, "PASS": 1}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-032-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-032 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-profile/spec.md`; SHA256 `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43`.

16 cases, 7 requirements: PARTIAL 14, PASS 2. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-032-AND-PRO-001-01 — PARTIAL

pro-empty-profile-save — - **GIVEN** an account profile with no provided fields - **WHEN** the user saves without entering optional context - **THEN** numeric values remain null and no default cannabis exposure or baseline is created.

Current proof: Blank validator leaves age/BMI null; domain starts empty context and browser allows profile-free guest check.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::optional blank demographics stay null and unknown remains distinct from declined` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 56; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No exact account empty-profile save plus reload asserts all numeric values null and absence of default cannabis exposure/baseline; validation-only assertion does not cover persisted account state.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA deec9da69ff8acf2756e5dfe5292ff2877cd9a235f6f0e7906b31914967aad0f. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-001-02 — PARTIAL

pro-declined-history — - **GIVEN** last use is set to Prefer not to say - **WHEN** the profile is saved and reloaded - **THEN** the declined marker persists and its timestamp remains null.

Current proof: Validator preserves distinct declined history and last_use_status markers.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::optional blank demographics stay null and unknown remains distinct from declined` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 56; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Saving and reopening that declined profile, with explicit last_use_at null assertion, is absent from reviewed current profile tests.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA facd2c38116281673504a0618c25e43d0fcac1da86fe33d7cfe7bf0922247352. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-002-01 — PARTIAL

pro-imperial-bmi — - **GIVEN** the user enters 5 feet 10 inches and 180 pounds - **WHEN** the draft is validated and saved - **THEN** canonical height is 177.8 cm, weight is 81.6466266 kg before contract precision handling, and displayed BMI is 25.8 with no category label.

Current proof: Imperial validator directly tests 5ft10in at 150lb, exact SI and BMI; browser tests metric180cm/80kg toggle.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::whole feet plus bounded inches and pounds use exact SI conversions` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 67; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::profile fields announce validation, preserve canonical units and guard unsaved edits` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 608; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Canonical scenario specifies 180lb ->81.6466266kg and displayed25.8 with no category. Existing150lb21.5225 fixture and metric browser values do not assert that exact numeric/display boundary.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5d2084acdb29c9eefa267de7134a721de924af7bfd8f4047237fbb9ac95751cb. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-002-02 — PARTIAL

pro-invalid-number — - **GIVEN** height is zero, weight is non-finite, or age contains a fraction - **WHEN** Save profile is pressed - **THEN** the relevant inline errors appear, BMI is unavailable, and no invalid profile is submitted.

Current proof: Validator collects four errors without clearing text; locale parser refuses Infinity; real browser age17 reports inline aria-invalid, focuses age and preserves values.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::profile validation collects independent inline errors without clearing draft text` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 36; 1 current observation(s).
- `apps/mobile/tests/profile-form.test.ts::locale decimal and digit input becomes locale-independent numbers` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 23; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::profile fields announce validation, preserve canonical units and guard unsaved edits` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 608; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Exact zero-height/nonfinite-weight/fractional-age submissions require assertions of BMI unavailable and no API profile submission; reviewed fixtures instead use age17/height301/weight0.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0ac92770454a2e8430f52a76918f2bdeeaa49f8bb63738ac7b6c5565523060d6. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-003-01 — PASS

pro-edit-after-check — - **GIVEN** a finalized check records weight 80 kg and profile version A - **WHEN** the user saves weight 82 kg as version B - **THEN** the historical check retains version A and 80 kg while the next check may use B.

Current proof: Controller checks snapshot/context deep equality after later profile edit. Real measurement-mode software context P1=80kg/versionA before capture remains after P2=82kg/versionB, optional software interrupted ledger; new linked check usesP2/no carriedattempts, original staysP1.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::check freezes original profile timestamp and recomputes elapsed use at its start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 152; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::ordinary measurement P1 stays frozen after P2 profile update ${ledgerTransition ? "across a software-only interrupted first attempt" : "while the draft has no captures"}` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 628; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: No physical capture/another-device rendered version/native encrypted restart; these additions passed existing implementation and do not establish a profile behavior defect.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1808d916919be235283770bd77a36069da232ac6c98a9def3a9ea6cbe1effc9e. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-003-02 — PARTIAL

pro-edit-during-open-draft — - **GIVEN** a check draft has already copied version A - **WHEN** another device changes the profile - **THEN** the open check does not silently acquire the new context and displays its saved profile version on review.

Current proof: Controller asserts original context/snapshot equality after profile save; UI exposes snapshot revision.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- An open measurement draft receiving another-device profile update, visible saved revision and unchanged non-null context are not directly exercised; current finalized engineering fixture does not establish exact open-draft conjunction.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ae7acfc0d7468413be9a0c139d9fa62886bfc9165bbefa1922a140cd08bb3c23. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-003-03 — PARTIAL

pro-edit-before-first-acquisition-still-frozen — - **GIVEN** Start check created session A with profile revision P1 and no capture yet - **WHEN** the user saves revision P2 on this or another device - **THEN** A still displays P1 and its original target time; using P2 requires a new linked check created after that save.

Current proof: Domain copies profile and original start time; controller refuses implicit snapshot replacement. Real measurement-mode software context P1=80kg/versionA before capture remains after P2=82kg/versionB, optional software interrupted ledger; new linked check usesP2/no carriedattempts, original staysP1.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::check freezes original profile timestamp and recomputes elapsed use at its start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 152; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::ordinary measurement P1 stays frozen after P2 profile update ${ledgerTransition ? "across a software-only interrupted first attempt" : "while the draft has no captures"}` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 628; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- The check must still display P1 when P2 is saved on this or another device. Current no-capture controller state, original target and linked P2 replacement are proved; actual rendered frozen-P1 review / another-device presentation is not directly observed.

Prerequisite/evidence type: software_ui_assertion_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: No physical capture/another-device rendered version/native encrypted restart; these additions passed existing implementation and do not establish a profile behavior defect.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c9666892602304a3230f2b03b5da13772d970500b05dc9f54667169c3d5d2b10. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-004-01 — PARTIAL

pro-two-device-conflict — - **GIVEN** two devices edit the same base revision - **WHEN** the first save succeeds and the second receives 412 - **THEN** the second displays both versions and retains its draft until the user chooses.

Current proof: API ETag/idempotency tests reject stale writes; controller saveProfile refreshes current profile after conflict and exposes explicit resolution.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::profile fields announce validation, preserve canonical units and guard unsaved edits` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 608; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Two-device UI scenario must assert both versions displayed, original local draft retained, and no write until explicit choice. Existing browser form only tests validation/unsaved navigation; no current same-context412 journey found.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2fcf2da5644501aa8b3d3938acbffe7f6a142dddd4a6ff3c1990a16fed8c9fd7. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-004-02 — PARTIAL

pro-save-timeout-retry — - **GIVEN** the server saved a revision but the response was lost - **WHEN** the app retries with the original key and payload - **THEN** one revision is returned and no duplicate change is recorded.

Current proof: Server profile idempotency uses original key/payload; controller queues exact profile operation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual accepted-profile-response-lost retry with original key and payload, one server revision and no duplicate change is not directly asserted in the reviewed profile tests; ordinary successful save is narrower.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e0203b362c5c89923cfac81b32329da5b3c18aa4dc8af0c4d5ec844d1745b880. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-004-03 — PARTIAL

pro-stale-generation-is-quarantined — - **GIVEN** a queued profile Save carries an earlier data generation - **WHEN** the service returns 410 after accepted all-data deletion - **THEN** the operation is quarantined without rewriting its generation; new saves wait for the explicit reset acknowledgment.

Current proof: Generic generation410 queue test quarantines unchanged request evidence; explicit reset controller prevents prior data reuse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::conflict and stale generation stop automatic replay without changing frozen evidence` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 305; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Need profile-specific accepted-all-data-deletion410 scenario proving original queued profile generation unchanged and new profile save waits for acknowledgment, rather than session queue only.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 63a42e241bbed8a9c2961db88036184a01b9a6395f278cddece0001645acd18c. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-005-01 — PARTIAL

pro-offline-edit — - **GIVEN** an account profile is cached and the network is unavailable - **WHEN** the user saves valid changes - **THEN** the local revision is labeled pending and reconciliation later applies the original ETag rather than pretending a server save occurred.

Current proof: Controller implementation saves local profile pending and queues ETag; sync sends exact request.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual cached account edit offline then reconnect is not exercised with pending label and original ETag assertion; guest local-save and ordinary account-success tests are different contexts.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 033d48ad3936ecc8335930bb30ead60cf06a98c939a42ca593fc9c56450b6ae4. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-005-02 — PARTIAL

pro-guest-to-account — - **GIVEN** a fictional demo profile exists - **WHEN** the user opens a newly authenticated account - **THEN** the account profile is fetched or shown empty and the demo profile is not imported automatically.

Current proof: Guest domain object cannot acquire account ownership; controller partitions workspace.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::guest check cannot upload and never acquires an account owner by sign-in` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 246; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Need same-context fictional profile with known values followed by authenticated account fetch/empty response and explicit no-import comparison; guest check ownership assertion alone does not prove profile isolation.

Prerequisite/evidence type: software_assertion_or_integration_evidence, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5b7b7e9990499fb46a7dba588ce059200de6ac4528557a1481c3b9d6cf89ab99. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-006-01 — PASS

pro-future-use-time — - **GIVEN** a last-use timestamp is later than the current device time - **WHEN** the user saves - **THEN** the app asks the user to review the date/time or select unknown and does not silently clamp the timestamp.

Current proof: Known last-use validator refuses future and impossible date with field error and returns no valid profile; source error asks review of future time. Valid explicit timezone converts to UTC/time-since-use120, proving no silent clamp. Current named validation execution only, not installed native UI.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::known last-use rejects impossible calendar dates and future times with a field error` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 117; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c86881541b5861f53826d263adb64d775aaefb01cc1bd4ea90096e1297a48fce. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-006-02 — PARTIAL

pro-demographics-do-not-score — - **GIVEN** a complete profile with daily use and all demographics - **WHEN** the dashboard or result is displayed - **THEN** no metabolic-rate calculation, baseline qualification, or intoxication probability is created from those fields.

Current proof: Profile is context, not numeric model output; engineering snapshot result remains measurement-only with null probability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No exact complete daily-use/demographics profile rendered in dashboard/result asserts absence of metabolic rate, baseline qualification and generated intoxication probability. Null-profile engineering fixture is not that scenario.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 38ce4024a63ad758f88fc2a71e2390168dcde8526feda0d68cf3a30ca94be18c. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-007-01 — PARTIAL

pro-accessible-errors — - **GIVEN** screen-reader navigation and 200% text scaling - **WHEN** two fields fail validation - **THEN** the error summary is announced, the first invalid field receives focus, and Save/Cancel remain reachable without overlapping controls.

Current proof: Real browser age error announces alert/focus and retains Save; two viewport component execution exists.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::profile fields announce validation, preserve canonical units and guard unsaved edits` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 608; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual screen-reader and200%text with two simultaneous field failures, summary announcement, first-invalid focus and unobscured Save/Cancel is not executed; browser17age alone is narrower.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f4e713ecfc1f5e15f7bbe51008e145ee024b8a98c9b8783b401412b711fe5674. Actual current source and raw evidence supply this disposition.

## OTGD-032-AND-PRO-007-02 — PARTIAL

pro-ios-unit-roundtrip — - **GIVEN** an iOS profile contains canonical values with more precision than display - **WHEN** the user toggles units twice without editing - **THEN** stored values and BMI are unchanged and no new profile revision is created.

Current proof: Pure validator25unit toggles preserve177.8cm/68.0388555kg; browser roundtrip preserves180cm/80kg.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::display rounding and repeated unit toggles preserve original canonical values` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 87; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::profile fields announce validation, preserve canonical units and guard unsaved edits` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 608; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual iOS installed profile toggle twice with original high precision, unchanged BMI and no new revision has no admitted native execution; pure validator does not assert revision count.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c3732ef6e94aa3978d42f7d478f86e9f7c4bc6bf14218c92eb9e1a9d1b4e04cc. Actual current source and raw evidence supply this disposition.
