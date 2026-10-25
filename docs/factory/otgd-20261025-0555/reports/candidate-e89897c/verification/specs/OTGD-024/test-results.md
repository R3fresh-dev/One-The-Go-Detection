# OTGD-024 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-ecg-capture/spec.md`; SHA256 `c75f24b4beeda893b780af0d924747c0cd7ca599ead627d3d265f21ec3772895`.

16 cases, 7 requirements: BLOCKED 1, NOT_RUN 1, PARTIAL 12, PASS 2. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-024-AND-ECG-001-01 — PARTIAL

Skip optional ECG — - **GIVEN** a workflow in which ECG is optional - **WHEN** the user selects Skip ECG - **THEN** the check SHALL continue with an explicit not_collected ECG status and null ECG features, without fabricating a normal ECG or marking the entire app unusable.

Current proof: Cardiac skip preserves selected PPG and records skipped ECG not_collected/null features.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/cardiac-selection.test.ts::skipping an ECG alternative cannot erase valid selected PPG` — file SHA `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`, line 179; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No initial optional ECG skip UI journey asserts check continuation when no PPG is present.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7ee63a4a3d921787b4dc673e6bf795a8b12a92d140fc2266db49902967011776. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-001-02 — PARTIAL

Run the simulator — - **GIVEN** synthetic mode and no ECG hardware - **WHEN** the user selects Run simulator - **THEN** a deterministic named waveform fixture SHALL exercise capture/progress/review states with simulated source and SHALL not require electrode contact or imply a measured heartbeat.

Current proof: Synthetic ECG controller reaches complete with deterministic values, exact evidence hash and200 accepted display samples.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/signal.test.ts::local ECG stream keeps the exact ten-message complete evidence and connection observation time separate from samples` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 144; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Visible progress/review simulator journey and no electrode-required/measured-heartbeat language are not fully asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a6f651967126dc647088170f2be1792bf195082c8730b72a70572b681d7558f4. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-002-01 — BLOCKED

Approved configuration and verified device — - **GIVEN** a valid approved whole-system configuration matching the connected device and permitted operating state - **WHEN** the authorized operator initiates capture - **THEN** the module SHALL execute only that protocol and retain the binding, approval/configuration hashes, power-state evidence, and lead configuration.

Current proof: Fresh reader flow freezes configuration/binding and human ECG operating-state verifier remains explicitly unavailable.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::approved research start freezes exact online study/configuration context and device binding before any acquisition` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1401; 1 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_human_ecg_state_verification_is_unavailable_even_when_declared_verified` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 470; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- No qualified whole-system human ECG/power/lead-state verification exists; approved physical protocol execution and retained power/lead evidence cannot be tested.

Prerequisite/evidence type: physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 1b80cfbfdd62ec5f29d610d6bbe5cd61a751526f78c5cbc1009c6b0fa1b1d8b5. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-002-02 — PARTIAL

Unreviewed USB-powered body connection — - **GIVEN** no matching approved power/connection configuration - **WHEN** the device or user requests hardware ECG capture - **THEN** the app SHALL reject Start hardware capture, show Electrical configuration not qualified, and SHALL not substitute a simple acknowledgment checkbox for the missing evidence.

Current proof: Both participant_declaration_only and device_attested_v1 human ECG configurations remain software unsupported.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_human_ecg_state_verification_is_unavailable_even_when_declared_verified` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 470; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- App must assert Start hardware capture rejected with exact Electrical configuration not qualified and no checkbox bypass for USB-powered connection.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bcedfc402a7d3f12f900bc776e0fffe3c5876c43cd02d81e325d9b6ff2e8fdbd. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-002-03 — PARTIAL

Cached gate after device restart — - **GIVEN** a cached approved-looking capability and a reader with a new boot ID - **WHEN** the operator attempts a hardware start offline - **THEN** the app SHALL refuse the start pending fresh online authorization and verified association; it SHALL not reuse the prior boot clock or provide connection instructions from an unresolved configuration.

Current proof: Changed boot is rejected before hardware and before allocating an attempt.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::revoked consent, stale approval and reader substitution cannot invoke hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1560; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Offline cached-gate journey must assert fresh association/start required, prior clock cleared and unresolved connection instructions withheld.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 17793994c3cf301414f81bc18cbfd6b5bb693c5cac6f5e14acd1a7e69c3ac69b. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-003-01 — PARTIAL

Raw ADC counts received — - **GIVEN** an otherwise well-formed stream without an approved scale calibration - **WHEN** the waveform is reviewed - **THEN** the app SHALL label values counts, retain the missing-scale reason, and SHALL not render an mV axis or supply calibrated features that require voltage units.

Current proof: Chunk validator preserves explicit units; waveform renderer does not rescale underlying values or samples.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 382; 1 current observation(s).
- `apps/mobile/src/device/tests/signal.test.ts::ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 113; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Uncalibrated counts capture must render counts/missing-scale reason, no mV axis, and no voltage-dependent calibrated features.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 24af881a4e1100cb424b0b64f5dbdcf004367b95ce62a359deac8df488e98141. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-003-02 — PARTIAL

Sample gap inside a recording — - **GIVEN** a stream with a missing block or nonconsecutive sample index - **WHEN** reassembly completes or times out - **THEN** the gap SHALL be represented explicitly and the applicable quality rule enforced; the app SHALL not draw a continuous valid trace by interpolating away lost evidence.

Current proof: Signed chunks retain dropped_before=2; waveform omits bridging129:131 and preserves source samples.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 382; 1 current observation(s).
- `apps/mobile/src/device/tests/signal.test.ts::ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 113; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Integrated missing-block stream completion/timeout must assert applicable final invalid quality disposition, including missing chunk semantics.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 668c8bb1557dbe8eba24b2cb4adb816b342bca4f63bc3dd086ce724ebc851a5b. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-004-01 — PARTIAL

Waveform visually smooth but inadequate for HRV — - **GIVEN** a capture shorter than its extractor's approved duration or with too few usable beat intervals - **WHEN** the summary is generated - **THEN** the waveform MAY remain available within policy but RMSSD SHALL be null with an adequacy reason, not a guessed feature.

Current proof: ADC core with insufficient valid beat intervals has invalid signal and NaN HR; synthetic insufficient_samples fails null physiology.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).
- `apps/mobile/src/device/tests/signal.test.ts::all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 62; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Short-duration/too-few-interval ECG waveform must specifically retain RMSSD=null and adequacy reason, not merely generic invalid signal.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cedf973850933d88d4cac7d4b17a3b07f938bce4eee84cdcceb491fc71b4b2cb. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-004-02 — PARTIAL

Heavy rendering load — - **GIVEN** a supported synthetic or approved stream - **WHEN** the screen drops rendering frames - **THEN** raw sample acquisition SHALL remain independently bounded, display lag SHALL be reported where relevant, and lost acquisition samples SHALL not be hidden by the appearance of the graph.

Current proof: Waveform display draws at most99 segments and never fills index gaps or mutates source data.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/signal.test.ts::ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 113; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Heavy rendering load must be applied while acquisition runs and assert independent sample bounds plus relevant lag reporting.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 13bb3dfbe9d26628e732b633ac93dd61cecd84ad02dac7d701e59e256552921d. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-005-01 — PARTIAL

Lead detaches during capture — - **GIVEN** an active hardware or simulator lead-off test - **WHEN** contact is lost - **THEN** the UI SHALL show Lead contact lost, retain lead-off timing, and apply the fixed protocol's stop/invalid behavior without continuing to display an unqualified live heart rate as current.

Current proof: Lead_off fixture clears live bpm, latches exact reason/contact absent, and rejects later completion.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/signal.test.ts::all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 62; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- UI Lead contact lost and retained lead-off timing with fixed-protocol terminal behavior need exact assertions.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 87d04dc263ab7f595c9fa29d17726d0dad16e165de2cffc768de3cac868ec2b5. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-005-02 — PASS

Late samples after cancellation — - **GIVEN** a canceled ECG capture - **WHEN** remaining Bluetooth notifications arrive - **THEN** those samples SHALL be rejected by capture identity and SHALL not populate a later attempt or turn the canceled attempt complete.

Current proof: Active signed ECG cancellation rejects pending capture, clears trust, and later transport completion cannot reactivate it; workspace cancellation also prevents stale acceptance.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::cancellation clears trusted association immediately and drops a late signed completion` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 606; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::cancellation invalidates before disconnect and prevents stale completion into a different workspace` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 99; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9b464f236006cdce3b8bb472a6af7ec4f4e906152bbd47a43e9c6895303c12a5. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-006-01 — PARTIAL

User selects ECG after a PPG capture — - **GIVEN** a check with an accepted PPG cardiac component - **WHEN** the user selects the allowed ECG alternative - **THEN** the UI SHALL explain that v0.1 selects one cardiac modality, preserve the PPG attempt, and require an explicit selection of which accepted capture becomes the final cardiac component.

Current proof: Two accepted modalities retain immutable attempts, require explicit choice and select exact final projection in client/server.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/cardiac-selection.test.ts::one PPG plus one ECG is retained and requires an explicit final choice` — file SHA `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`, line 31; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- UI explanation that v0.1 selects one modality and explicit selection interaction remain unasserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c95cdedcedcb90729584c359dafe37c495bc20ddcce742a7563322070c18d728. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-006-02 — NOT_RUN

Protocol demands both modalities — - **GIVEN** the installed client supports only the v0.1 cardiac schema - **WHEN** a protocol requires both PPG and ECG as distinct model inputs - **THEN** capability resolution SHALL report Unsupported cardiac contract and SHALL not merge the two sources or fabricate a compatible feature vector.

Current proof: Alternative-selection and unrelated pending-specimen tests do not request a both-modalities protocol.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Resolve a protocol requiring separate PPG+ECG inputs and assert Unsupported cardiac contract with no merged/fabricated model vector.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 7356dfcd020b6676a81d35da6a5d8959264acfef84df198adfc6619865abb3b3. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-006-03 — PASS

Optional ECG skip preserves selected PPG — - **GIVEN** a pre-finalization check with a valid selected PPG capture - **WHEN** the user selects Skip ECG - **THEN** the PPG selection SHALL remain unchanged, ECG SHALL remain explicitly not_collected, and no mixed-modality v0.1 component SHALL be created.

Current proof: Skipping active ECG alternative leaves selected PPG snapshot unchanged, preserves selected attempt in final manifest and retains ECG not_collected.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/cardiac-selection.test.ts::skipping an ECG alternative cannot erase valid selected PPG` — file SHA `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`, line 179; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c91080691d0bd77db18266d9d86f9bf16fbdfaf410a52b81ad619d1afd294707. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-007-01 — PARTIAL

Offline completed simulation — - **GIVEN** a complete synthetic ECG capture with the network disabled - **WHEN** the user saves the check - **THEN** the app SHALL store the permitted fictional record locally, retain its simulated label, and show sync status independently from capture completion.

Current proof: Local synthetic ECG and immutable guest save tests run without participant upload.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/signal.test.ts::local ECG stream keeps the exact ten-message complete evidence and connection observation time separate from samples` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 144; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Complete synthetic ECG with network disabled must be saved/reopened and assert simulated label plus independent sync status through UI.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ec6718429f9f3e904636d5899df357566146421c196aa82163d5a5975aa24382. Actual current source and raw evidence supply this disposition.

## OTGD-024-AND-ECG-007-02 — PARTIAL

Missing raw-data retention policy — - **GIVEN** a proposed participant protocol without a resolved ECG retention policy - **WHEN** recording or upload is requested - **THEN** the app SHALL block the dependent recording/upload path and SHALL not choose indefinite retention as a fallback.

Current proof: Raw permission validator rejects mismatched policy/receipt and revoked/expired purpose; raw choice requires encrypted native storage.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-artifacts.test.ts::fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop` — file SHA `80522a5edec7a841cdaf1ed5257ce336ea1ababb4d2a4001d1c7a443fe7e94b3`, line 70; 1 current observation(s).
- `apps/mobile/tests/raw-upload.test.ts::Save and metadata-only upload never read or queue raw; explicit selection is immutable and exact` — file SHA `90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef`, line 227; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Specifically unresolved ECG retention policy must drive both record/upload requests and assert no indefinite-retention fallback.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 20255b210296848111819a1d703ed7e145031613743af127b7bbc110727f0aad. Actual current source and raw evidence supply this disposition.

