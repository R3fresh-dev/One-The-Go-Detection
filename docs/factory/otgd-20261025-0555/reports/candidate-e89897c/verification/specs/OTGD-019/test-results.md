# OTGD-019 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-alcohol-channel/spec.md`; SHA256 `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a`.

12 cases, 6 requirements: NOT_RUN 2, PARTIAL 9, PASS 1. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-019-AND-ALC-001-01 — PARTIAL

Only the starter PPG board is connected — - **GIVEN** a Nano ESP32 and PPG module without a calibrated breath channel - **WHEN** Alcohol is opened - **THEN** the app shows hardware-required guidance and does not start a blow timer or produce an alcohol value.

Current proof: Production inventory has no alcohol driver and capabilities report HUMAN_ADAPTER_UNIMPLEMENTED; UI says qualified capture unavailable.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_alcohol_current_dependencies_do_not_manufacture_an_available_adapter` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 98; 5 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Connected PPG-only user journey must assert hardware-required guidance, no blow timer and no alcohol value through opening Alcohol.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 82455f9bd7654827109e1c5778c58db32951d2ad873fbdfe592c66829297e7d2. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-001-02 — PARTIAL

Approved configuration is missing — - **GIVEN** a connected device advertises alcohol capability without an approved configuration - **WHEN** sampling is requested - **THEN** the app and server reject the request with a configuration-unavailable reason.

Current proof: API refuses unavailable alcohol adapter and current invalid registry authority; controller never invokes acquisition on authoritative start refusal.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_alcohol_current_dependencies_do_not_manufacture_an_available_adapter` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 98; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::a start-time registry dependency refusal after a hypothetical breath grant preserves its authoritative reason and never acquires concentration` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1731; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Advertised alcohol with absent configuration must exercise both app and HTTP request and assert the specified configuration-unavailable reason.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 31d5bd2115b7a8c996a9c4ff0251ffee9a7704e593add26e50214020c60f15d0. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-002-01 — PARTIAL

Combined session has two measured channels — - **GIVEN** independently valid alcohol and cannabis records - **WHEN** session detail is displayed - **THEN** each channel has its own card, units, timing, and validity explanation.

Current proof: DOM card tests preserve alcohol units/time/qualifier/source separately from displayed cannabis result.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol qualifiers retain zero, low, censored, invalid and simulated evidence without clearance from history through result and detail` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 187; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- The conjunction of independently validated alcohol+cannabis records is hypothetical; no real breath adapter/qualified record exists and separate cannabis card validity text is not fully asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 66514a2a8d2a0b019004d80378c1baf79fd53c7bb34bacebe4ad57de35804725. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-002-02 — PARTIAL

Cannabis result is unavailable — - **GIVEN** a valid authorized alcohol record and unavailable cannabis inference - **WHEN** results render - **THEN** the alcohol measurement does not manufacture a cannabis estimate.

Current proof: Measurement/guest copy does not invent a result; domain rejects locally generated research estimates.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Valid authorized alcohol plus unavailable inference must be rendered with an explicit assertion that no cannabis estimate appears.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d0f9acb9fa13024f92c085a967360f2ef800f360e479e06e172af84b648d9479. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-003-01 — PARTIAL

Quantified record arrives — - **GIVEN** an in-range qualified measurement in mg/L - **WHEN** the record is validated and displayed - **THEN** its numeric value and mg/L label remain paired.

Current proof: DOM tests pair exact zero/0.001 value with mg/L across history/result/detail.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol qualifiers retain zero, low, censored, invalid and simulated evidence without clearance from history through result and detail` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 187; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- In-range qualified breath record validation is unavailable without actual approved adapter; display fixtures are explicitly hypothetical.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b7faedba1f8edf0dfbfe595c8acc3773562d5356d79ee2204ebedc1ea83e10cf. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-003-02 — NOT_RUN

Caller submits a BAC percentage — - **GIVEN** a value labeled percent BAC - **WHEN** it is submitted to the breath-alcohol route - **THEN** the service rejects the incompatible unit and performs no conversion.

Current proof: Related saliva-unit and schema tests do not execute this breath-route unit mutation.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Submit percent BAC to the breath-alcohol route and assert incompatible-unit rejection with no conversion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA a355d530eddfccce0671f5a36911511a1d36eff7131ec14462bb6d41e4737b9f. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-004-01 — PARTIAL

Sampling is inadequate — - **GIVEN** the device reports an inadequate breath sample - **WHEN** acquisition ends - **THEN** the result is invalid with no exact concentration and an actionable retry explanation.

Current proof: Alcohol censored/invalid schema requires null concentration; UI renders invalid as em dash.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_alcohol_censoring_is_null` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 459; 25 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol qualifiers retain zero, low, censored, invalid and simulated evidence without clearance from history through result and detail` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 187; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Inadequate actual breath completion and actionable retry explanation are absent because no breath driver is implemented.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e825fa8d0ad9d4b8fd4e38a35ae553671ff2c7870f0cfe3e1301b3ade080e0a7. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-004-02 — PARTIAL

Calibration expires — - **GIVEN** the instrument calibration is outside its qualified interval - **WHEN** a new record is requested - **THEN** the app blocks qualified sampling and identifies recalibration as the required action.

Current proof: API expiry equality and just-over reject calibration/configuration, preserve history and refuse fresh/cached starts; controller preserves authoritative refusal and never acquires.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_alcohol_configuration_and_calibration_expiry_boundary_preserves_history` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 71; 30 current observation(s).
- `services/api/tests/test_operator_governance.py::test_alcohol_expiry_between_contract_grant_and_start_rejects_cached_authority` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 121; 20 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::a start-time registry dependency refusal after a hypothetical breath grant preserves its authoritative reason and never acquires concentration` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1731; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- UI identifies only generic registry refusal; it does not assert recalibration as required action for specifically expired calibration.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 43c02f95dc7ba1884ecd78c32eb2ae59694bd1f31fefbedf6e988f403bb88e70. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-005-01 — PARTIAL

Demo is intentionally opened — - **GIVEN** the development demo action - **WHEN** the customer previews the channel - **THEN** every value is labeled fictional and no real measurement claim is made.

Current proof: Simulated qualifier/source appears on separate alcohol DOM card with no clearance copy.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol qualifiers retain zero, low, censored, invalid and simulated evidence without clearance from history through result and detail` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 187; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Explicit development-demo opening must assert every displayed value is fictional and no real-measurement claim appears throughout capture/review.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5622d84a683fe38382ea6adb075631672730240dcd625c7700a6f9f2b1ef80f6. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-005-02 — NOT_RUN

Simulated record targets a participant session — - **GIVEN** a nonsynthetic parent session - **WHEN** a simulated alcohol record is submitted - **THEN** the service rejects the provenance mismatch.

Current proof: Synthetic export fixture validates typed projections only; it does not submit to a participant parent.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- POST simulated alcohol evidence to nonsynthetic session and assert provenance mismatch and no persisted reading.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 396ab1953c7bba241afd2cbed257f3e319d223fbbc938016af5824102d23cb06. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-006-01 — PARTIAL

Alcohol co-use is present — - **GIVEN** the cannabis model does not support alcohol co-use - **WHEN** a future research request is evaluated - **THEN** the unsupported cohort is handled by the manifest gate rather than a score adjustment in the app.

Current proof: Model scope-check co_use mutation is rejected and DOM explains model-specific co-use authority/no automatic combined classification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Test uses alcohol_co_use=unknown; a present unsupported alcohol co-use cohort must be directly asserted rather than relying on unknown-state rejection.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2f1d198f3d126bb3e9447182d0a58f2edd27a36afc1b1f16e9e8a4993cd9ea4f. Actual current source and raw evidence supply this disposition.

## OTGD-019-AND-ALC-006-02 — PASS

A low displayed value — - **GIVEN** a low or censored alcohol result - **WHEN** the result screen is shown - **THEN** no **Safe to drive** or legal-clearance message appears.

Current proof: Low0.001, real zero, censored and invalid DOM variants across history/result/detail assert no safe-to-drive, cleared-to-drive, legal-clearance or combined-score copy.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol qualifiers retain zero, low, censored, invalid and simulated evidence without clearance from history through result and detail` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 187; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA cc25d14e82afb8543dec01554e1e30b4537b4bcb9891d1cd6d06a04c48022692. Actual current source and raw evidence supply this disposition.

