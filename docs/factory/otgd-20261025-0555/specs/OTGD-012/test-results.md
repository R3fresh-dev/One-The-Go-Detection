# OTGD-012: verification results

Canonical: `openspec/changes/canonical-optical-native-acquisition/specs/optical-native/spec.md`; SHA-256 `1e25c5f543b73c2df18741240a266b39716ae17c31bc8b57e2bd91dc699a29c4`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 6 individually identified requirements and 13 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 13 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"PARTIAL": 13}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-012-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `1e25c5f543b73c2df18741240a266b39716ae17c31bc8b57e2bd91dc699a29c4`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-012 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/canonical-optical-native-acquisition/specs/optical-native/spec.md`; SHA256 `1e25c5f543b73c2df18741240a266b39716ae17c31bc8b57e2bd91dc699a29c4`.

13 cases, 6 requirements: PARTIAL 12, PASS 1. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-012-AND-EYE-101-01 — PARTIAL

OPTICAL-001 Fresh feature-only start — - **GIVEN** an owned started attempt, current study consent and independently released configuration with the installed camera tuple - **WHEN** the participant grants camera permission and explicitly starts feature-only collection - **THEN** context and attempt evidence are persisted before the online authorization is issued and started - **AND** the native view receives the exact material bytes, authorization and attempt record identity, with null recording permission - **AND** local completion does not queue an upload

Current proof: Controller retains null raw permission, distinct arming/acquisition clocks, local completion and no upload queue.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_material_fields_phone_build_sensor_and_stimulus_are_all_bound` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 310; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- No assertion observes the actual native view receive byte-identical material/authorization/record identity or proves context/attempt persistence occurs before start.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d45ff937004af632b4253670db7defd2895a040d1b1063d9b3c952cd139c85a6. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-101-02 — PARTIAL

OPTICAL-002 Missing or revoked start authority — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** camera permission, online start, exact hash or approved device tuple is missing or changed, or consent or configuration is retired before start - **THEN** acquisition remains stopped and no raw frame is persisted - **AND** an old positive authorization response cannot invoke hardware after its workspace is invalidated

Current proof: Configuration hash/phone/build/stimulus mutations and unqualified projection claims reject.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_optical_evidence.py::test_material_fields_phone_build_sensor_and_stimulus_are_all_bound` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 310; 5 current observation(s).
- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Permission refusal plus delayed positive authorization after optical workspace invalidation must assert no native start and no persisted raw frame.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e843038d95b0ebe7b5024326f523e105ca310cca9e51414a6300c9523383d5d4. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-102-01 — PARTIAL

OPTICAL-003 Accepted bounded frames retain platform evidence — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** the approved capture receives an ordered bounded sequence with accepted frame spacing, dimensions and metadata - **THEN** frame sequences begin at zero and actual native timestamps and dispatch times are retained - **AND** Android exposure evidence says capture_result_timestamp_match only for matched sensor timestamps - **AND** Android joins images and results in either arrival order only by exact sensor timestamp, with three pending images and sixteen retained results - **AND** sensitivity ISO remains null when unavailable, and platform-specific AE state and its observation method remain explicit - **AND** iOS callback exposure evidence says device_state_at_callback and has the exposure-not-frame-matched quality flag

Current proof: Kotlin matcher joins both arrival orders, rejects fourth pending image, preserves replacement matcher; both cores retain ISO/AE labels.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::cameraFrameAndMetadataJoinEitherOrderAndOriginCleanupRemovesOnlyItsPendingFrames` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 9; 1 current observation(s).
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::frameMetadataPreservesObservedIsoAeAndRejectsUnsettledExposure` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 21; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testFrameMetadataPreservesObservedIsoAeWithoutFrameQualification` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 15; 2 current observation(s).
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::nativeProductionPayloadFactoryEmitsInteropFixture` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 88; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.

Exact unproved clause(s):

- No assertion covers sixteen-result eviction, expiry, zero-origin frame sequences through actual camera callbacks or the iOS exposure-not-frame-matched flag in runtime emission.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1d1be023f0655381870ea0dd8a4981c8456d6401a8a9d38659a10b0bc87484a7. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-102-02 — PARTIAL

OPTICAL-004 Gap, overflow or changed geometry stops collection — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** timestamps regress, a frame or silence gap exceeds the reviewed bound, the three-frame callback queue overflows, dispatch is late or source/processed dimensions change - **THEN** the originating capture stops invalid and emits no positive features or raw handoff - **AND** changing counts, dimensions or frame timestamps in a retained positive payload is rejected by the independent API validator - **AND** an unmatched Android result expires within the reviewed frame-gap bound, and searching, adjusting or unknown AE cannot produce accepted segmentation

Current proof: Unsettled AE fails core qualification and client rejects changed frame sequence/timestamps/counts/rotation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::frameMetadataPreservesObservedIsoAeAndRejectsUnsettledExposure` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 21; 1 current observation(s).
- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_invalid_capture_counts_and_null_features_do_not_become_positive` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 289; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Regressing callbacks, silence-gap timeout, three-frame runtime queue overflow, dispatch/geometry change and unmatched-result expiry must stop the originating view with no positive/raw handoff.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8b41c7a7348590e67b65b152b2034e8a0555f917a97d976434a6a179a25e6b86. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-102-03 — PARTIAL

OPTICAL-005 Camera fails before first accepted frame — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** permission, camera start or native setup fails before any accepted camera frame - **THEN** the terminal is invalid with its originating identity and reason, and native evidence and raw media are null - **AND** no acquisition timestamp, camera clock or optical feature is invented; the separate arming timestamp remains available for repair

Current proof: Both notStarted factories retain original run/epoch/reason with null evidence; controller keeps arming metadata and null acquired clocks.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::api24CompatibleWallTimeAndNoFrameFailureNeverInventEvidence` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 31; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testNoFrameFailureHasNoInventedAcquisitionEvidence` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 25; 2 current observation(s).
- `apps/mobile/tests/eye-acquisition.test.ts::camera failure before the first frame preserves its original reason and arming metadata without inventing acquired clocks` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 300; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.

Exact unproved clause(s):

- Actual native permission/setup/camera failure before first frame is not induced; actual originating-view terminal path remains unexecuted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7e9763f3f8298c4aba5107401af5dd64252f995692ae9e4526cc30ea78008891. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-103-01 — PASS

OPTICAL-006 Literal cross-language pixels and factory payload — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** Kotlin, Swift and the API process the checked-in synthetic pixel and response goldens - **THEN** the expected component statistics, feature arithmetic and codec bytes agree within the stated numerical tolerance - **AND** the production Kotlin payload factory matches the checked-in DTO accepted by the independent API validator - **AND** fixture success grants no anatomical or physical qualification

Current proof: Both cores match literal segmentation/response values; Kotlin matches complete raw hash and production DTO; Swift DTO equals Kotlin fixture; API accepts DTO. ReviewedSwiftassertion now compares everyliteralrawbyte including2frames/timestamps/sequences plusoriginalraw_sha256.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::literalSyntheticPixelGoldenParity` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 44; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testLiteralSyntheticPixelGoldenParity` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 39; 2 current observation(s).
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::reviewedResponseAndCalibratedScaleStaySeparateFromPhysicalOnset` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 51; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testReviewedResponseScaleAndMissingOnset` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 46; 2 current observation(s).
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::samplingRotationAndRawCodecMatchLiteralBinaryGolden` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 70; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testConfigurationFailClosedAndRawLittleEndian` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 54; 2 current observation(s).
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::nativeProductionPayloadFactoryEmitsInteropFixture` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 88; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testProductionPayloadFactoryMatchesActualKotlinDTOKeys` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 78; 2 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_actual_kotlin_production_factory_fixture_passes_independent_server_validation` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 342; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current ordinary and hosted macOS Swift raw XCTest/XML execute the exact full560-byte/hash assertion. No camera/sensing/anatomical qualification follows.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 041974b6a8430d47a6e907dc57113a943ca6922cc450e27fc78caf7db8d4391a. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-103-02 — PARTIAL

OPTICAL-007 Ambiguous pixels and forged retained statistics — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** a component touches the rejected edge, has unapproved area, roundness or contrast, or multiple plausible components exist - **THEN** extraction returns an explicit invalid reason without guessing a pupil - **WHEN** a retained payload changes a count, normalized diameter, geometry, material hash or declared scalar result - **THEN** API and client projection validation reject the changed evidence

Current proof: Literal edge/ambiguous/contrast/roundness vectors reject; API/client reject retained-statistics/hash/projection mutations.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::literalSyntheticPixelGoldenParity` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 44; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testLiteralSyntheticPixelGoldenParity` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 39; 2 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_roi_same_pixel_summary_cannot_hide_changed_content_and_statistics_cannot_be_forged` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 512; 5 current observation(s).
- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- No direct invalid area-bound vector covers below/above approved component area and not every geometry/scalar mutation is asserted across client and API.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cd16fd874622f13ec5fb493264683974b06005fbbc680b5f1b95e1c5e5de81ae. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-104-01 — PARTIAL

OPTICAL-008 Reviewed geometry and descriptive display response — - **GIVEN** exact independently released geometry and configuration authority for the installed tuple and sampled pixel basis - **WHEN** accepted component diameters lie inside the calibrated range - **THEN** baseline millimeters use the frozen pixel-to-mm conversion and its stated uncertainty - **WHEN** a separately reviewed display step has enough accepted baseline and post-step frames - **THEN** callback-relative change and threshold timing may be retained as descriptive metadata, with physical onset explicitly unmeasured - **AND** original screen brightness is restored after settlement or interruption

Current proof: Both cores assert frozen .1 pixels-to-mm conversion and descriptive response arithmetic; absent onset retains null latency.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::reviewedResponseAndCalibratedScaleStaySeparateFromPhysicalOnset` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 51; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testReviewedResponseScaleAndMissingOnset` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 46; 2 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_response_and_scale_reference_match_literal_vector_and_raw_codec` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 174; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual brightness restoration after valid settlement and interruption is not executed; uncertainty/range boundaries are not all asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a3e9877672cd12883baa456d3b75a35bec41342582913aec6aedb17d10d62cfd. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-104-02 — PARTIAL

OPTICAL-009 Unmeasured onset cannot become a pupil response — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** a retained payload claims measured physical onset, scientific latency or pupil relative constriction from native callbacks alone - **THEN** the payload is rejected and response-dependent model admission fails closed - **AND** normalized or out-of-range geometry leaves scientific millimeters null - **AND** missing, stale or mismatched calibration cannot qualify even a diameter-only model

Current proof: Client rejects physical onset, millimeter invention and model-eligible claim; API rejects descriptive response as qualification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_descriptive_native_change_cannot_become_unqualified_pupil_response` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 358; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Missing/stale/mismatched geometry calibration admission for a diameter-only model is not completely asserted by these particular tests.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f767fd92688922a5a7f04e9af0b371b7387b9eae08d0ec3adf7afa6b0edfec83. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-105-01 — PARTIAL

OPTICAL-010 Cancel after committed completion — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** completion committed before a participant End action but durable local evidence persistence is delayed - **THEN** the native cancellation receipt returns that same immutable scientific completion - **AND** the UI disables native running and requests shutdown before awaiting persistence

Current proof: Controller dispatches cancel before delayed store persistence and preserves an already committed valid result.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::End camera dispatches native shutdown and running=false before delayed evidence persistence, and a committed completion survives cancel` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 264; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Real native cancellation receipt preserving immutable committed completion, and rendered running=false before persistence, remain unobserved.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3166eddb16b492084479439a46f6c7800e22d3a2586c356d42b69131b9ad387b. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-105-02 — PARTIAL

OPTICAL-011 Late origin after workspace replacement — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** an old camera opens, session configures, capture result arrives or frame callback executes after its workspace was canceled - **THEN** the originating handle closes or the old callback is discarded without mutating the replacement ledger or handles - **AND** a queued cancellation wins over a positive settlement that has not committed

Current proof: Matcher cleanup removes only originating pending images; Swift cleanup retains origin until queued cleanup executes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::cameraFrameAndMetadataJoinEitherOrderAndOriginCleanupRemovesOnlyItsPendingFrames` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 9; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.

Exact unproved clause(s):

- Delayed real camera open/session/result/frame callbacks against a replacement view and cancellation-before-positive-commit race are not executed.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 85d119bc70aed328f6162ab99fa554e59ea4bc20902b9416903ef437436aec42. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-106-01 — PARTIAL

OPTICAL-012 Opted-in encrypted handoff — - **GIVEN** fresh separate record permission bound to the current consent, policy and raw notice - **WHEN** a valid native acquisition returns the bounded ROI codec and chunks - **THEN** encrypted bytes and the exact immutable local receipt commit atomically before native release acknowledgment - **AND** ROI dimensions, count, sequence, Float64 timestamps and each decoded luminance digest match the originating accepted frame ledger - **AND** temporary decoded bytes are wiped and neither local Save nor native handoff queues an upload - **WHEN** an explicitly requested upload completes - **THEN** the server independently decodes the exact admitted object version, repeats extraction on its pixels and rejects changed statistics or linkage - **AND** an owned verification receipt binds the object version and digest to the accepted attempt, complete configuration and native evidence digest

Current proof: Controller mocked saveWithRaw receives bytes, releases native RAM and wipes bytes without queueing upload; codecs and API ROI ledger checks run.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::optional ROI handoff commits encrypted bytes plus exact receipt atomically, releases native RAM, and never queues upload` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 335; 1 current observation(s).
- `apps/mobile/tests/raw-artifacts.test.ts::native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff` — file SHA `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`, line 39; 1 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_roi_codec_verification_binds_actual_luminance_native_ledger_and_attempt` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 429; 5 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_roi_same_pixel_summary_cannot_hide_changed_content_and_statistics_cannot_be_forged` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 512; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual encrypted native bytes+receipt transaction and exact immutable receipt atomicity, plus real object PUT/version receipt roundtrip, are not proven by mocked save or object client.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0ad96ca4c23dda9a5a6fd66a612fb597776866934cf2fed7003a7ea31efcf958. Actual current source and raw evidence supply this disposition.

## OTGD-012-AND-EYE-106-02 — PARTIAL

OPTICAL-013 Withdrawal, timeout or absent opt-in — - **GIVEN** an originating optical attempt in its current account workspace and the scenario's stated evidence or authority conditions - **WHEN** recording permission is absent or false - **THEN** feature collection emits no raw handoff - **WHEN** a completed raw recording is acknowledged, aborted, unacknowledged for thirty seconds or followed by a privacy/workspace/background/detach transition - **THEN** native cached raw media references are released - **AND** withdrawal's durable local fence blocks upload and later cancellation cannot recover the old raw chunks - **AND** changed pixels, timestamps, sequence, dimensions or accepted acquisition identity cannot be reclassified as authenticated raw recording

Current proof: Feature-only grant is null; both terminal caches release exact run/digest raw references and reject wrong run/hash.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::completedRawHandoffAcknowledgmentAndPrivacyStopRemoveNativeReferences` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 79; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testCompletedRawAcknowledgmentAndPrivacyClear` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 71; 2 current observation(s).
- `apps/mobile/tests/eye-acquisition.test.ts::optional ROI handoff commits encrypted bytes plus exact receipt atomically, releases native RAM, and never queues upload` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 335; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.

Exact unproved clause(s):

- Thirty-second timeout, actual background/detach/privacy hooks, durable withdrawal race and inability to recover old raw chunks through native cancellation are not executed together.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3ccfc3eeac2d8064204e313e84f0dca8efe551f0bfad0c8ff5d7a33e1b16918f. Actual current source and raw evidence supply this disposition.
