# OTGD-025: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md`; SHA-256 `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8`.
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

Independent source assertion audits for this dossier: Permissions race and no-reprompt assertion audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 16 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 3, "NOT_RUN": 1, "PARTIAL": 10, "PASS": 2}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-025-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-025 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-eye-capture/spec.md`; SHA256 `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8`.

16 cases, 7 requirements: BLOCKED 3, NOT_RUN 1, PARTIAL 10, PASS 2. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-025-AND-EYE-001-01 — BLOCKED

Preview without an approved optical configuration — - **GIVEN** camera permission and no qualified optical configuration - **WHEN** the user chooses Preview positioning - **THEN** a passive camera preview SHALL appear without stimulus, recording, or derived features, and ending it SHALL leave the eye component not_collected.

Current proof: DOM describes passive/approved observation and not-collected projection without claiming measured onset.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Actual passive camera preview without stimulus/recording/features and ending it not_collected has no native camera execution.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 164f2c5826ba31a8b47bd2cd56ee77e8c429059855ac8468366ad07647255fc8. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-001-02 — PARTIAL

Synthetic eye fixture — - **GIVEN** P0 demonstration mode - **WHEN** the user explicitly chooses the synthetic eye example - **THEN** the stored component SHALL be labeled simulated, retain its fictional fixture/configuration ID, and SHALL not be represented as an extraction from the user's preview.

Current proof: Synthetic typed eye projection is retained by export validator.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-projection.test.ts::every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 29; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Explicit synthetic-example choice must assert fixture/configuration ID and distinguish it from the user's passive preview.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA aef847c31379032b1c5c4253c31a986bb117155ad5a0814e9f6663e57194546a. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-002-01 — BLOCKED

Permission permanently denied — - **GIVEN** Android has denied camera permission permanently - **WHEN** the user selects preview - **THEN** the screen SHALL explain the missing permission, offer Open settings and Back to check, and SHALL not enter an indefinite loading state.

Current proof: No actual permanently-denied camera preview flow was executed.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Android permission permanently denied must settle loading and expose Open settings and Back to check.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA e8d981564d94b86f742f845f588aa89509a14327be4e7b52043828a0a0b1ba4d. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-002-02 — BLOCKED

Backgrounded active capture — - **GIVEN** an authorized optical capture in progress - **WHEN** the app loses foreground activity - **THEN** the stimulus SHALL stop, camera resources SHALL be released, the attempt SHALL become invalid, and returning SHALL require a new linked attempt.

Current proof: Native core cache clear and origin cleanup are exercised as isolated helpers.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::completedRawHandoffAcknowledgmentAndPrivacyStopRemoveNativeReferences` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 79; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testCompletedRawAcknowledgmentAndPrivacyClear` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 71; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.

Exact unproved clause(s):

- Actual background transition must stop stimulus/release camera, invalidate current attempt and require linked retry on return.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 4c77847d76b58e528e4d8b7eaae4e32df7d54d72878e42b3185103749c9f6e39. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-003-01 — PARTIAL

Qualified capture configuration available — - **GIVEN** a valid matching optical configuration and all required authorizations - **WHEN** the user reviews its instructions and selects Start capture - **THEN** the native module SHALL execute only the bounded approved sequence and store its exact configuration hash and timing evidence.

Current proof: Controller fresh-start fixture retains exact configuration/native result and separate clock anchors.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual instruction-driven native view must execute bounded sequence using exact approved material, with runtime timing evidence.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bccfa075b4520d9e23e013cf92b4e3014e2e0c87bfdd88d20613757a4ca9e083. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-003-02 — PARTIAL

Local override requests phone flash — - **GIVEN** no approved configuration or a configuration for a different phone - **WHEN** a deep link or modified local preference requests stimulus capture - **THEN** the module and orchestration gate SHALL reject the request and SHALL not activate the flash, torch, or modulated screen.

Current proof: Native config rejects digest mismatch, unknown fields, flashing mode and unreviewed millimeter scale; API exact phone tuple mutations fail.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_optical_evidence.py::test_material_fields_phone_build_sensor_and_stimulus_are_all_bound` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 310; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Modified deep-link/local preference must be rejected through actual module/orchestration with flash/torch/modulation side effects observed absent.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0bc212dda96563ab295044ea2eab011fe159abdf317c86f6d03d63e2abde87a3. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-003-03 — PARTIAL

Offline cached optical approval — - **GIVEN** a previously available cached optical capability and a current camera permission - **WHEN** the user enables airplane mode and selects Start capture - **THEN** the app SHALL require a fresh online capture acknowledgment and SHALL leave all participant stimulus output disabled; passive preview remains a separately labeled action.

Current proof: Controller obtains separate online grant/start for optical fixture before accepting local result.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Airplane-mode cached optical approval must assert no participant stimulus output and distinct available passive preview action.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 662582f3d6c740566021529fc153c445191e89a4126465cc09eff0777759c6d1. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-004-01 — PASS

Flash request has no verified physical onset — - **GIVEN** a recorded OS stimulus request and frame callbacks - **WHEN** the hardware lacks verified physical onset evidence - **THEN** the record SHALL mark timing evidence unverified or estimated, and an extractor requiring measured onset SHALL produce no qualified response latency.

Current proof: Projection rejects physical onset invention and retains null scientific latency/mm; native descriptive callback response does not qualify physical pupil response.

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

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 01c49e592f995b576ab126fca8e321208b306513f4a53f584c62b90442f3d1b3. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-004-02 — PARTIAL

Variable camera cadence — - **GIVEN** frame timestamps showing drops or irregular intervals - **WHEN** feature eligibility is evaluated - **THEN** the app SHALL retain actual cadence and gap evidence, apply the frozen configuration's quality rules, and SHALL not fabricate a constant high-rate sequence from requested FPS.

Current proof: Client rejects changed sequence/regressing frame timestamps and impossible frame counts; evidence retains actual frame ledger.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_invalid_capture_counts_and_null_features_do_not_become_positive` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 289; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Irregular cadence/drop fixtures need exact frozen maximum-gap/quality boundary assertions without requested-FPS substitution.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5b31f2f2d8797fc29dec78031c9657c9c408bad7220ae237d2005dd0a29551ba. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-005-01 — PASS

Pixels supplied as millimeters — - **GIVEN** a segmentation result with image-pixel diameter and no scale calibration - **WHEN** an adapter attempts to populate diameter_mm - **THEN** validation SHALL reject the unit conversion and retain only a correctly labeled pixel or dimensionless observation when permitted.

Current proof: Client rejects baseline millimeter invention in normalized fixture; both core feature tests keep unapproved physical scale/onset separate; no fabricated latency qualifies.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).
- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::reviewedResponseAndCalibratedScaleStaySeparateFromPhysicalOnset` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 51; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testReviewedResponseScaleAndMissingOnset` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 46; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-optical.xml` — SHA256 `2d4be76b142ebf9538bc6a71d356831e48f485ae12689e35fc3db62ec524f3b3`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595993071/eye-capture/android/build/reports/tests/testDebugUnitTest/expo.modules.otgdeye.EyeCoreTest/index.html` — SHA256 `3fb4d8afdf872b4b46f8d0881104c71ba16fb451e0ead73045ebce4e437d22fe`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-optical.xml` — SHA256 `7d317e7776fb5c46c46f6b3979894133b370640bb57d0d9c166c2efe8aa89457`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 8b9cb0c4ea4508e8e4596b1d7a57c77a2d658a8aba552d35f8ee5e3cb2e50ee9. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-005-02 — PARTIAL

Eye lost during response window — - **GIVEN** a capture with required frames obscured by blink or tracking loss - **WHEN** the extractor applies the approved quality policy - **THEN** the affected feature SHALL be null or the capture invalid according to that policy, with the reason retained; it SHALL not impute an apparently normal response.

Current proof: Literal invalid segmentation produces explicit reasons and API invalid projection leaves features null/model ineligible.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/eye-capture/android/src/test/java/expo/modules/otgdeye/EyeCoreTest.kt::literalSyntheticPixelGoldenParity` — file SHA `8699039fb6bd8673ba07cd7ea601c219b296ca4bf44573caab299aab3b4042c6`, line 44; 1 current observation(s).
- `apps/mobile/modules/eye-capture/tests/swift/EyeCoreTests.swift::testLiteralSyntheticPixelGoldenParity` — file SHA `bea5fa65942293bffcc1cdf14918fc22ded6db527ee6becb5142db7b72a47552`, line 39; 2 current observation(s).
- `services/api/tests/test_optical_evidence.py::test_invalid_capture_counts_and_null_features_do_not_become_positive` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 289; 5 current observation(s).

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

- Required blink/tracking-loss frames during a response window must exercise configured adequacy failure and preserve exact reason.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 05ddc4766338f423599dc650455760a54113363bed79604a8dc7e2495b44a881. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-006-01 — PARTIAL

User declines raw recording — - **GIVEN** a protocol that permits local feature extraction without raw retention - **WHEN** the user declines optional recording - **THEN** raw data SHALL not be persisted or uploaded, and only explicitly permitted features and quality metadata MAY be retained.

Current proof: Feature-only grant has null recording permission; completion/save never requests artifact upload and local queue stays empty.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Native raw frame persistence must be directly observed absent when optional recording declined; mocked controller cannot establish camera buffers/storage.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8d054db27ff916643533c0c97abd6cf811302b290e40e9f23246babf8635b5f5. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-006-02 — PARTIAL

Artifact upload fails — - **GIVEN** an authorized retained capture and a network interruption - **WHEN** upload cannot complete - **THEN** the UI SHALL show pending upload, retain the immutable local artifact only within its permitted lifetime, and SHALL not mark a partial remote object available for extraction.

Current proof: Explicit raw upload selection validates exact local artifact/permission; dependent upload tests preserve bounded immutable selection.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-upload.test.ts::Save and metadata-only upload never read or queue raw; explicit selection is immutable and exact` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 227; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Network interruption during optical upload needs pending-upload UI, lifetime-bound retention and partial-remote-object extraction refusal assertions together.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b00b316082d7823b4add68b9166e26d5a55e4611021b1dfa0e69d20e08336394. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-006-03 — PARTIAL

Withdrawal races with an issued upload ticket — - **GIVEN** an optical artifact PUT URL issued before withdrawal - **WHEN** the user withdraws locally and the server accepts withdrawal while old bytes arrive - **THEN** local capture/queue work SHALL stop immediately, the server SHALL refuse artifact verification/evidence acceptance, and any uploaded version SHALL remain quarantined for scoped cleanup.

Current proof: Local raw permission/withdrawal tests fence purposes and generic HTTP raw verification quarantines forged chunks.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-artifacts.test.ts::fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop` — file SHA `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`, line 70; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual optical issued-PUT-ticket versus local+server withdrawal race must assert immediate stop, refused optical evidence and quarantine of arriving object version.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3a79c292dd3ed0d5b991e8e5ab7594e8ad0a1243cf550dedc60d6b3d61f6aa5b. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-007-01 — NOT_RUN

Review after passive preview — - **GIVEN** a user who previewed positioning but performed no authorized measurement - **WHEN** Review is opened - **THEN** Eyes SHALL show Not collected with Preview only context and null measured features rather than a successful pupil test.

Current proof: Related optical fixture tests do not open Review after passive-only preview.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Review after passive positioning must show Eyes Not collected/Preview only and null features with no successful pupil-test language.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 4f6829aa478cef54bb31ace30e46219dd6b4bcaf2bf836884af90c6863919a78. Actual current source and raw evidence supply this disposition.

## OTGD-025-AND-EYE-007-02 — PARTIAL

Cross-platform camera capability mismatch — - **GIVEN** an optical configuration qualified for a specific iPhone but not the Android device in use - **WHEN** Android requests measurement capture - **THEN** Android SHALL remain blocked with Unsupported optical configuration while iOS compatibility is assessed independently; visual similarity SHALL not establish equivalence.

Current proof: API rejects changed phone/build/configuration tuple and native config pins identity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_optical_evidence.py::test_material_fields_phone_build_sensor_and_stimulus_are_all_bound` — file SHA `5870d66e52eee9904f360272f4d1a15725f1fef4b6400e5235fcc36384e72414`, line 310; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Android with iPhone-only configuration must surface Unsupported optical configuration while iOS is assessed independently.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 611b19f69e4ed683dd797932210de8eb949a9baf6d727aa4e9571f89510ad073. Actual current source and raw evidence supply this disposition.
