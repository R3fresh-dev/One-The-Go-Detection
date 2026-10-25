# OTGD-033: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-reaction-task/spec.md`; SHA-256 `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 8 individually identified requirements and 22 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 22 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 3, "NOT_RUN": 1, "PARTIAL": 15, "PASS": 3}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-033-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-033 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-reaction-task/spec.md`; SHA256 `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317`.

22 cases, 8 requirements: BLOCKED 3, NOT_RUN 1, PARTIAL 10, PASS 8. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-033-AND-TASK-001-01 — BLOCKED

First complete task — - **GIVEN** a supported native application with no accepted task in this check - **WHEN** the user selects Start task - **THEN** the task SHALL execute one practice-plus-scored sequence and return one bounded native completion event containing the attempt identity, timing evidence, planned trials, observations, and derived features.

Current proof: Core schedules/scoring and bounded DTO tests execute; controller accepts fictional native payloads.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::frozenLiteralSchedulesAndHashes` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 16; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).
- `apps/mobile/tests/export-evidence.test.ts::host-generated native golden is fully checked without claiming a physical acquisition` — file SHA `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`, line 207; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- No full supported Android/iOS native view practice+scored run and one bounded completion event with observed native timing is executed.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 1e3d809a0d6a7120ddf885a1632a280d17f3956fe9cf034ce2dcfe83f1d1f94f. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-001-02 — PARTIAL

Native module unavailable — - **GIVEN** a runtime without the compiled reaction module - **WHEN** the reaction screen opens - **THEN** the UI SHALL explain that a native build is required for capture and SHALL not silently replace it with JavaScript timers or mark a preview as a valid native task.

Current proof: Controller rejects unsupported/stale native task terminal and invalidates unmounted arm.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 889; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Module-unavailable screen must assert native-build explanation and no silent JavaScript fallback or valid-native labeling.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 481a0a109d8b7575ebc9f0cc30f217922291e783bbe757fd9d876665e2d73ec5. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-002-01 — PASS

Same seed on both native platforms — - **GIVEN** the same seed and pinned configuration - **WHEN** Kotlin and Swift generate the schedule - **THEN** all 66 stimulus identities, practice/scored classifications, onset intervals, and planned times SHALL match the shared golden fixture exactly.

Current proof: Both Kotlin and Swift compare every field in all66 literal trials for seeds0/1/UInt32max, exact configuration/hash and terminal-target arithmetic.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::frozenLiteralSchedulesAndHashes` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 16; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b954018437f4abe748985efd798c76f73786977dc9ff6ae7f356c69aa21441be. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-002-02 — PARTIAL

Responses influence apparent performance — - **GIVEN** two runs with the same seed but different response streams - **WHEN** either run advances - **THEN** its next planned stimulus SHALL remain unchanged by response speed, mistakes, omission, or a desired score; the app SHALL not adapt the schedule to improve the outcome.

Current proof: Schedule generator is deterministic and independent scoring uses precomputed literal schedules.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::frozenLiteralSchedulesAndHashes` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 16; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).
- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::aggregatesPracticeExclusionAndNullableNoResponseFeatures` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 87; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- Two native runs with contrasting response streams must directly compare subsequent planned stimuli and prove runtime cannot adapt timing/sequence to responses.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f3249c5f4b4b2f449e7e1c6385980fe0e72dedbfa5e67ef4bdebc5ec37a7ae52. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-002-03 — PARTIAL

Unused final interval cannot prolong the task — - **GIVEN** the seed-1 literal schedule with all trials presented without lateness - **WHEN** the final response window closes - **THEN** the run SHALL end after its 100-ms drain at the fixture terminal cutoff, independent of the retained final interval draw.

Current proof: Both schedule tests compute expected terminal cutoff from final onset+window+100ms drain, excluding last retained interval.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::frozenLiteralSchedulesAndHashes` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 16; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- Actual run advancement/terminal commitment at that seed1 cutoff is not asserted; formula equality alone does not prove runtime end behavior.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0c82b4a3f5a4204dac7b2cea6074222a619f89defc455f440df237d6637924c9. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-003-01 — PARTIAL

Accurate-looking floating-point timestamps — - **GIVEN** nanosecond or submillisecond software timestamps without physical display/touch calibration - **WHEN** the task computes or displays reaction features - **THEN** it SHALL retain uncalibrated status and report appropriate precision, without claiming that numeric resolution establishes equivalent physical timing accuracy.

Current proof: Native evidence fixture is uncalibrated, physicalOnsetVerified=false/modelEligible=false and client preserves numeric values.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-evidence.test.ts::host-generated native golden is fully checked without claiming a physical acquisition` — file SHA `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`, line 207; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Rendered feature precision and absence of claims equating Android/iOS numeric timestamp resolution to physical accuracy are not fully asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA dd8cc397e1a9e30679c5fa29c9c458858ac958571cc730f42ad6d2437f26c8ef. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-003-02 — BLOCKED

Wall clock changes during task — - **GIVEN** an uninterrupted native run - **WHEN** the system wall clock changes - **THEN** native reaction intervals SHALL remain based on the monotonic clock, the wall-clock discontinuity SHALL be retained in timing quality, and cross-component time eligibility SHALL be resolved separately.

Current proof: Pure core reaction intervals use supplied monotonic event values.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::aggregatesPracticeExclusionAndNullableNoResponseFeatures` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 87; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- No native system wall-clock change during uninterrupted acquisition tests retained discontinuity flag and unchanged RT/cross-component eligibility.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 52bc5fc545e6f33b94c6a7bd80113df109576f7e72f5cf5eb1be100e6090855d. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-004-01 — PASS

Wrong then correct tap — - **GIVEN** a left-arrow go trial - **WHEN** the first qualifying tap is right and a later tap is left - **THEN** the trial SHALL remain an incorrect choice, both touches SHALL remain in the event ledger, and the later left tap SHALL not supply a correct-go reaction time.

Current proof: Both native scorer suites retain wrong-choice outcome, first sequence0, RT200 and null correct-go RT for wrong-then-correct fixture. ActualPythonreference full66fixture/literalvectors and timingnegative guards; retainedwrong+correctledger/delay80/reverseorder handled by sharedgoldens and authorednativeassertions.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::allLiteralTrialBoundaryVectors` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 32; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_literal_task_cases_through_actual_reference_validator` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 125; 40 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_wrong_then_correct_preserves_both_touches_without_correct_go_rt` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 161; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_forged_retained_dispatch_delay` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 172; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_retained_handler_at_or_after_cutoff` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 186; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current Kotlin Android HTML and actual macOS Swift XML/raw XCTest observations are now bound for both18-vector core suites. Physical/native UI timing and sensors remain unqualified.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bcd5921cd0b41788b2c510a899a431b4265970e4e3498ea8c70628d7b0d3cb44. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-004-02 — PASS

Omission and anticipatory input — - **GIVEN** a go trial with a tap before recorded onset and no qualifying tap afterward - **WHEN** the response window ends - **THEN** the early tap SHALL be retained as anticipatory, the go trial SHALL count as an omission, and no fabricated zero or 1000-ms reaction time SHALL enter the correct-go distribution.

Current proof: Both native suites assert pre-onset input disposition anticipatory, go omission, null selected response and null correct-go RT; no fabricated zero/deadline value enters distribution.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::allLiteralTrialBoundaryVectors` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 32; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 8302ae36ef155d7efd0e9b3546116ee5048343b1f9dbcc3298957141a6b14fbd. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-004-03 — PASS

Response dispatched within the final drain — - **GIVEN** the final trial starts at 10000 ms and a left event occurs at 10999 ms - **WHEN** the native handler receives it at 11079 ms before cutoff 11100 ms - **THEN** the event SHALL be scored with RT=999 ms and dispatch delay=80 ms; a handler at the exact cutoff SHALL be outside committed acquisition.

Current proof: Both suites score event10999 received11079 as RT999 and ignore handler at exact11100 cutoff. ActualPythonreference full66fixture/literalvectors and timingnegative guards; retainedwrong+correctledger/delay80/reverseorder handled by sharedgoldens and authorednativeassertions.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::allLiteralTrialBoundaryVectors` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 32; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_literal_task_cases_through_actual_reference_validator` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 125; 40 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_wrong_then_correct_preserves_both_touches_without_correct_go_rt` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 161; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_forged_retained_dispatch_delay` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 172; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_retained_handler_at_or_after_cutoff` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 186; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current Kotlin Android HTML and actual macOS Swift XML/raw XCTest observations are now bound for both18-vector core suites. Physical/native UI timing and sensors remain unqualified.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5cd2b673119644a5ef6ea6eaae3d702d55e5e235666d756924b6cde6ffd1036c. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-004-04 — PASS

Opposing simultaneous touches are stable — - **GIVEN** a left trial and equal-timestamp right/left touches delivered in either order - **WHEN** timestamp ordering is applied - **THEN** left SHALL rank first, pointer/sequence ties SHALL follow the pinned comparator, and both platforms SHALL produce the golden correct choice.

Current proof: Literal equal-time right-then-left vector selects left and sorted sequences[1,0] on both platforms. ActualPythonreference full66fixture/literalvectors and timingnegative guards; retainedwrong+correctledger/delay80/reverseorder handled by sharedgoldens and authorednativeassertions.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::allLiteralTrialBoundaryVectors` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 32; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_literal_task_cases_through_actual_reference_validator` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 125; 40 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_wrong_then_correct_preserves_both_touches_without_correct_go_rt` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 161; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_forged_retained_dispatch_delay` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 172; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_retained_handler_at_or_after_cutoff` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 186; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current Kotlin Android HTML and actual macOS Swift XML/raw XCTest observations are now bound for both18-vector core suites. Physical/native UI timing and sensors remain unqualified.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 940771d422cdc646b2fb9648427189193b1f53dad91504b28c1f1e3443b571db. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-005-01 — PASS

All go trials omitted — - **GIVEN** an otherwise intact run with no correct go response - **WHEN** extraction executes - **THEN** correct-go quantiles SHALL be null, omission count/rate SHALL retain their true denominators, and the absence of a speed measurement SHALL not be interpreted as fast performance.

Current proof: Both core suites assert48 omissions/omissionRate1 and null median/IQR/p90 for intact full66-trial run; independent retained evidence test checks missing RT flag.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::aggregatesPracticeExclusionAndNullableNoResponseFeatures` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 87; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).
- `apps/mobile/tests/export-evidence.test.ts::an intact native task with no correct responses keeps null RT quantiles and its explicit quality flag` — file SHA `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`, line 320; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b32b1ea71c9bd70d78c7c7098ff02274fc1f3762abad5320e2370b38126e284a. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-005-02 — PARTIAL

Partial run stopped after ten scored trials — - **GIVEN** six completed practice trials and ten presented scored trials - **WHEN** the run is interrupted - **THEN** the attempt SHALL preserve those actual counts and planned remaining trials, mark invalid, and keep final-session aggregate task features null rather than pretending that a 60-trial task was completed.

Current proof: Both core suites assert interrupted prefix16 retains10 presented scored and final features=null.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::aggregatesPracticeExclusionAndNullableNoResponseFeatures` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 87; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- Tests pass only trials.take16, so they do not assert all66 planned records retained with remaining unpresented trials, six practice count and invalid terminal status together.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8ca91ddc8ea028c7d7cfd3c9958ecbdfa5356a85df73ee7d2a8d5fb64aabe289. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-006-01 — BLOCKED

Notification drawer takes focus — - **GIVEN** an active Android run - **WHEN** the system UI causes window focus loss - **THEN** the module SHALL stop the display sequence, emit one invalid completion with FOCUS_LOST, and require a newly identified attempt when the user returns.

Current proof: No Android instrumentation/system UI focus test is executed.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Notification drawer focus loss must stop native callbacks, emit exactly one FOCUS_LOST invalid event and require newly identified run on return.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA b4b73b793fdb9ca588e6422babeb76d4edcab6b71d748c00057e80a710d7eed4. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-006-02 — PARTIAL

Cancellation races with completion — - **GIVEN** a run approaching its final response window - **WHEN** cancellation and completion callbacks become runnable together - **THEN** the module SHALL commit one deterministic terminal state for that run, stop all callbacks, and SHALL not emit both a valid result and a separate canceled result.

Current proof: Both terminal latches deterministically let pending cancel win and suppress second commit; postcompletion cancel leaves committed latch unchanged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::terminalDrainOverflowAndPendingCancellation` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 111; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- Native view callback/display teardown and one emitted terminal event under actual runnable callback race remain unexecuted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 15e77ba652116ce5cf90cd28c8632a512bee576d451663c6b6a4ec80d5c02a41. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-006-03 — PARTIAL

Navigation overlay cannot preserve an active scored run — - **GIVEN** an active task whose tab stays mounted after navigation - **WHEN** the user selects another tab and then Keep draft in a confirmation - **THEN** the native stop acknowledgment and invalid settlement SHALL precede the overlay; returning SHALL never resume that run.

Current proof: Parent controller dispatches native cancellation before waiting for delayed device stop.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 847; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Mounted-view tab change plus Keep draft must assert native acknowledgment/invalid settlement precede overlay and old run never resumes.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b2c66dc51363161875de1cfc6da0a04457faab607ab5c18e4dabbfd7641270e8. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-007-01 — PARTIAL

Completion event received twice — - **GIVEN** an accepted native result for a run ID - **WHEN** the same payload is delivered again - **THEN** persistence SHALL deduplicate it by run identity and hash; a different payload under the same run ID SHALL produce a conflict instead of replacing the accepted result.

Current proof: Native terminal latch emits once and retained task evidence is digest-bound.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::terminalDrainOverflowAndPendingCancellation` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 111; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).
- `apps/mobile/tests/export-evidence.test.ts::host-generated native golden is fully checked without claiming a physical acquisition` — file SHA `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`, line 207; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- Parent persistence must receive identical result twice then changed same-run result and assert deduplication/conflict with unchanged stored original.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9ce314e14ffa6be1d3631a7b461e8e54cdd895a8e10723bf89c50b991ee86574. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-007-02 — NOT_RUN

Actual taps in a JavaScript preview — - **GIVEN** a user interacting with an explicitly labeled fallback/practice view - **WHEN** the preview ends - **THEN** its output SHALL retain prototype_sensor with javascript_fallback provenance and SHALL not be labeled native_task or used as a compatible task baseline.

Current proof: Native DTO/golden fixtures do not execute actual user input in JavaScript fallback.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Run actual taps in labeled fallback and assert prototype_sensor/javascript_fallback, never native_task or compatible baseline.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA bc3c1f1f7c913a0563c4030971cfa78500a6112a17723c995ea8a4023a39fe4f. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-007-03 — PARTIAL

Mixed guest demo preserves real native evidence — - **GIVEN** fictional saliva and an actual completed native reaction task in guest demo - **WHEN** the check is saved and later exported or the user signs in - **THEN** native taps SHALL remain prototype_sensor/uncalibrated in complete hashed companion evidence; guest upload/migration SHALL remain forbidden, while the CLI all-fictional validator stays unchanged.

Current proof: Guest immutable save prohibits upload; retained native golden preserves prototype/uncalibrated evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/tests/export-evidence.test.ts::host-generated native golden is fully checked without claiming a physical acquisition` — file SHA `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`, line 207; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Mixed fictional-saliva+actual native task save/export/signin must assert complete hashed companion survives and no guest migration/upload, while CLI validator stays strict.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 54e4d2dbcca8963ea6337b63c8c522164413da34c7dc888cacdef4eb48387e0d. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-008-01 — PARTIAL

Matching event fixtures across implementations — - **GIVEN** identical planned trials and ordered timestamped inputs - **WHEN** Kotlin, Swift, and the reference extractor score them - **THEN** counts, nullability, error rates, and quantiles SHALL match the named tolerances, with platform presentation-evidence differences retained in metadata.

Current proof: Kotlin/Swift match literal scoring outcomes/nullability and aggregate quantiles; independent client reference validates retained native fixture.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::allLiteralTrialBoundaryVectors` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 32; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).
- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::aggregatesPracticeExclusionAndNullableNoResponseFeatures` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 87; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).
- `apps/mobile/tests/export-evidence.test.ts::host-generated native golden is fully checked without claiming a physical acquisition` — file SHA `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`, line 207; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- Not all same event vectors are scored by independent reference extractor and compared for all counts/rates/metadata across three implementations.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a015ff8c2784342521e7a038c6139ebafdd358a275b8abe45fd1c138be97d182. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-008-02 — PASS

Passing native build without physical timing tests — - **GIVEN** successful Android/iOS compilation and fixture tests - **WHEN** a release report is generated - **THEN** it SHALL state native implementation/test completion separately from unresolved physical timing and predictive validation and SHALL keep modelEligible false.

Current proof: Retained native evidence keeps physicalOnsetVerified/modelEligible false; this audit explicitly separates native build/core success from physical timing and predictive validation. Actual current Android/Swift core executions are bound individually; the generated dossier explicitly states physical timing and predictive validation remain unexecuted, while literal fictional native evidence retains modelEligible=false.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-evidence.test.ts::host-generated native golden is fully checked without claiming a physical acquisition` — file SHA `786b535dfe7940928cdcc9149b7efbb4b8cb9541066a3d2e7d39a78819cc64ee`, line 207; 1 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_literal_task_cases_through_actual_reference_validator` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 125; 40 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_wrong_then_correct_preserves_both_touches_without_correct_go_rt` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 161; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_forged_retained_dispatch_delay` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 172; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_retained_handler_at_or_after_cutoff` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 186; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1a40cd4e8e68b8f6f879cc7d6048d0281b8d75d1cadf1b9c4a735499024f3319. Actual current source and raw evidence supply this disposition.

## OTGD-033-AND-TASK-008-03 — PASS

Development threshold and terminal boundaries are exercised — - **GIVEN** literal fixture inputs at exactly 100 ms and just over each native budget - **WHEN** both platform test suites execute - **THEN** exact-budget cases SHALL remain eligible, over-budget active cases SHALL invalidate, and post-cutoff arrivals SHALL leave committed results immutable.

Current proof: Both cores accept exactly100ms budgets, reject100.001ms active frame/callback/lateness budgets and ignore exact-cutoff input; input overbudget fixture invalidates.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::quantilesAndDevelopmentBudgets` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 100; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).
- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::terminalDrainOverflowAndPendingCancellation` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 111; 1 current observation(s).
- `apps/mobile/modules/reaction-task/android/src/test/java/expo/modules/otgdreaction/ReactionCoreTest.kt::allLiteralTrialBoundaryVectors` — file SHA `a8ab3f8d36028c621cd0e65df73d1f2bb0d6edd9b0c2107dd70c5f013d1c121e`, line 32; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_literal_task_cases_through_actual_reference_validator` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 125; 40 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_wrong_then_correct_preserves_both_touches_without_correct_go_rt` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 161; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_forged_retained_dispatch_delay` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 172; 5 current observation(s).
- `services/api/tests/test_reaction_task_goldens.py::test_reference_rejects_retained_handler_at_or_after_cutoff` — file SHA `748931e4e751153aa09ebcf0a61437d3d6433e113e1199a026fb5806605a108e`, line 186; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/reaction-task/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdreaction.ReactionCoreTest/index.html` — SHA256 `3e02641f15a9c126856b104fa5a4aca6492f5b41cabc26e04776954a852ed8df`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6eecfb048c22d041bb77547dd233d47bfe2b3c4c3ff2572144a6f9d7389feb8a. Actual current source and raw evidence supply this disposition.
