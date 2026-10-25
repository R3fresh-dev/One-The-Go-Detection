# OTGD-043 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/qualified-participant-acquisition/specs/selected-vendor-ppg/spec.md`; SHA256 `c6f863bc71ebf167438fbe5cffe07b892da12cc066d0487d21403ff8dd49fa0d`.

15 cases, 7 requirements: PARTIAL 10, PASS 5. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-043-VPPG-001-01 — PARTIAL

Exact selected breakout initializes — - **GIVEN** approved/provisioned selected hardware, firmware and SDK material - **WHEN** the current signed PPG start is admitted - **THEN** the actual SDK adapter initializes the declared I2C/reset/MFIO/BPM mode and progresses through bounded warmup without blocking cancellation.

Current proof: Pinned SDK host test verifies command bytes/mode1/2 and core reset/warmup stage deadlines; both firmware targets compile.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Full production adapter initialization must assert declared physical I2C/reset/MFIO sequence and cancellation remains nonblocking during each stage.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7f63fc07e771a91bcef0ea6b13251716cd77e5fd2678f5a8cef634402af98084. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-001-02 — PARTIAL

Generic ADC or failed hub initialization — - **GIVEN** a configuration expects SEN-15219 but a different adapter or failed I2C hub is present - **WHEN** acquisition is requested - **THEN** it returns a concrete invalid/unavailable disposition and never substitutes ADC counts, a simulator or a fabricated bpm.

Current proof: SDK failed/short/error reads return zeroed fields; raw ADC/signed generic material cannot invent missing sampling adapter.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).
- `services/api/tests/test_operator_governance.py::test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 649; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Failed hub initialization or wrong ADC adapter under exact SEN-15219 configuration must produce named unavailable/invalid completion with no fabricated bpm.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4d71051df7384309c084afffca6d6431e2cc0a79c91a988d9d48d0679028b920. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-002-01 — PASS

Fresh FIFO with known invalid records — - **GIVEN** the current capture receives bounded distinct vendor records with valid and poor-contact statuses - **WHEN** the adapter processes them - **THEN** received counts reconcile to valid/invalid dispositions and only fresh permitted records contribute to the summary.

Current proof: Host core has two valid observations and a separate poor-contact invalid observation, with explicit counts. Reviewedhostfixture assertsidenticalgenuinefreshdequeues/mixedvalidity/priorvalid→empty/stale/truncatednullsemantics inbothmodes withoutchangingoriginalproduction/goldens.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current actual portable compiler/executable stdout and firmware build job are bound. Full GPIO/BLE integration and physical vendor sensing qualification remain unexecuted.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0c1791b85e4db52b7d4d008ca3efc6e432f308726be8cf35d5c270a8c0855763. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-002-02 — PASS

No new FIFO data — - **GIVEN** one prior valid heart rate followed by empty FIFO, stale records or truncated responses - **WHEN** polling continues - **THEN** no prior number fills the missing interval, valid count does not advance and insufficient/stale evidence produces null completion.

Current proof: Pinned SDK zeroes prior values for short/error responses; empty FIFO returns0; separate core stale path has observed0 and null invalid projection. Reviewedhostfixture assertsidenticalgenuinefreshdequeues/mixedvalidity/priorvalid→empty/stale/truncatednullsemantics inbothmodes withoutchangingoriginalproduction/goldens.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current actual portable compiler/executable stdout and firmware build job are bound. Full GPIO/BLE integration and physical vendor sensing qualification remain unexecuted.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8a4ce9536b14249b45b615ec2b71ff64c411e0d9a635442d370f36371bd21094. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-002-03 — PASS

Identical values from genuine fresh dequeues — - **GIVEN** two separately successful current FIFO dequeues contain identical bpm/quality values and the vendor supplies no unique sample timestamp - **WHEN** the driver consumes each once - **THEN** both may count as observations, host sequence remains labeled as host-generated and neither equality nor polling cadence manufactures vendor timing or dropped-sample knowledge.

Current proof: Host sequence and client evidence retain unknown actual cadence/drop counts; production payload has sequential last observation. Reviewedhostfixture assertsidenticalgenuinefreshdequeues/mixedvalidity/priorvalid→empty/stale/truncatednullsemantics inbothmodes withoutchangingoriginalproduction/goldens.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current actual portable compiler/executable stdout and firmware build job are bound. Full GPIO/BLE integration and physical vendor sensing qualification remain unexecuted.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0e027274bc969db164c5c67b2d4df05c1c16453e131b89b92f66a67004c07175. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-003-01 — PASS

Valid finger and vendor quality — - **GIVEN** enough fresh vendor records meet the approved finger/status/confidence/range criteria - **WHEN** the named extractor completes - **THEN** a finite positive measured bpm and original bounded quality/count evidence are retained; confidence is labeled acquisition quality.

Current proof: Production core accepts two fresh permitted records and emits finite75bpm with bounded original confidence/status/count evidence; normalized payload preserves quality and remains model-ineligible.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 6c510254dabe9480b79c520ec7fb67a58d1b664ae87b6dcfcd9cf8b08d0791f0. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-003-02 — PARTIAL

Poor finger state or confidence reinterpretation — - **GIVEN** finger absence, insufficient accepted data or a vendor confidence score - **WHEN** output is validated/displayed - **THEN** invalid capture has null bpm and explicit reasons, and confidence cannot be shown as accuracy or cannabis impairment probability.

Current proof: Poor-contact and stale core produce invalid/null bpm; client rejects impossible confidence and retains modelEligible=false.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- UI must assert confidence is acquisition quality rather than accuracy/intoxication probability and display explicit inadequate reason.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 151ed5c85ab18262246d7637de6a53cdf79ba87eb437bbd6c6dab0cba8fdad98. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-004-01 — PARTIAL

Current signed vendor completion — - **GIVEN** a verified binding and current scoped start token with actual accepted vendor records - **WHEN** completion is signed and consumed by Android/iOS and the API - **THEN** the unchanged normalized evidence and timing/source labels survive exact signature and configuration validation.

Current proof: Vendor factory fixture survives strict client normalization/signature/configuration checks and timing/source labels remain intact.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::signed completion binds each current authorization scope field and exact immutable projection` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 294; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No same current signed vendor completion is independently accepted by actual Android/iOS applications and API as an end-to-end record.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 30cc371b3ce5c64321d00b9da09a6f8f843fdf3e89fbdfee0822aaeb1a8fbda4. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-004-02 — PARTIAL

Foreign boot or configuration — - **GIVEN** a signed completion from another boot, authorization, protocol/configuration or workspace - **WHEN** it is delivered late or replayed - **THEN** current client/server admission rejects it without attaching the old bpm to the replacement attempt.

Current proof: Client rejects altered boot/owner/generation/config authorization scope under signed completion.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::signed completion binds each current authorization scope field and exact immutable projection` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 294; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::delayed old acknowledgment rejection cannot invalidate replacement association` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 634; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Late foreign-boot/config vendor completion must pass actual server ingestion rejection and leave replacement attempt bpm untouched.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4c9494b0b2655c27feae5761fccf4f5882347c55488adb12175ae4e4496bbf17. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-005-01 — PARTIAL

Cancellation during warmup or blocked delivery — - **GIVEN** vendor acquisition is warming up or terminal transport is backpressured - **WHEN** Cancel or the admitted cutoff occurs - **THEN** the actual adapter stops before later delivery, retains the originating terminal identity and performs no resumed sampling.

Current proof: Core cancel during warmup ends once with no later end mutation; deadline overrun discards observation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Integrated adapter must stop before delayed/backpressured terminal delivery and preserve origin identity/no resumed sampling; core-only callback tests omit transport pressure.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a4c21612049c897a1db454b13b0097463445ff8ed832c1af246acaec9e20a2a8. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-005-02 — PARTIAL

Late old vendor read versus reconnect — - **GIVEN** an old read/result is delayed while another authenticated connection becomes current - **WHEN** it completes or notification is attempted - **THEN** origin fencing rejects its effects and only its own resources may be stopped; no participant payload reaches the replacement peer.

Current proof: Shared origin gate orders concurrent transition; client old ACK rejection leaves replacement association intact.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::delayed old acknowledgment rejection cannot invalidate replacement association` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 634; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Delay an actual vendor read and notification across authenticated reconnect, assert only old resources stop and no old participant payload reaches replacement peer.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e949612bf4a4b6e1bd5ecfcb5a2904033ef375033f438837d06141d0ba9295af. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-006-01 — PARTIAL

Installed and currently admitted vendor PPG — - **GIVEN** the selected adapter is compiled and all its exact current independently released scopes match - **WHEN** Home and PPG capture are opened - **THEN** the supported vendor path and instruction journey are shown while actual acquisition still obtains a fresh start.

Current proof: Exact inventory/configuration compatibility and fresh authorized customer sequence execute at software fixture boundary. Healthy signed protocol state/currentboot is distinct from servicebinding and syntheticconnection; actualHome/Device current/revoked/expired/owner/gen/offline observations match; mountedexpiry removesconditionalavailability, no flag grants capture authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::per-channel display uses active matching scope and unexpired admitted configuration independently from connection or binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 21; 1 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::a healthy signed reader connection is physical and retains current boot independently from service binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 82; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual Home and Device agree on a connected physical reader without synthetic or unconditional unavailable claims` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 49; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home and Device distinguish physical/synthetic connection from current, revoked, expired or mismatched channel authority` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 56; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home expires its current channel observation while mounted and Device retains that expired status` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 130; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual native Home-to-PPG instruction journey for the installed currently admitted vendor path must obtain a fresh Start. Current shared presentation, exact conditional capabilities and fresh-start server guards are proved; installed native journey and physical adapter remain unexecuted.

Prerequisite/evidence type: native_os_execution, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Loopback/framed/parsed-capability software fixtures only. Actual BLE handshake/radio/physicalreader/sensing qualification remain explicit; conditionaldisplay cannot independently qualify capture.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f7a65d13e3922ac8508dc8a21461c7bc4a8be2c3de763043190a01c90efbec33. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-006-02 — PARTIAL

Approved record names an absent driver or raw codec — - **GIVEN** an operator record names a missing vendor build or unsupported raw encoding - **WHEN** capability/start/recording is evaluated - **THEN** software availability remains refused; an approval cannot manufacture code or raw permission.

Current proof: Governance rejects generic signed transport missing actual sampling driver and refuses unsupported raw codec/material.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 649; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Exact missing vendor build/raw encoding must be evaluated across capability/start/recording routes, not just generic ADC driver support helper.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d45cc53608e37d89d04c0286912807e348debe9264e98bfaa7d9b9bcac3fef4c. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-007-01 — PARTIAL

Actual driver software fixtures — - **GIVEN** the same adapter used by firmware and the pinned vendor commands - **WHEN** fresh/empty/malformed FIFO, reset, quality, cutoff and cancellation cases execute - **THEN** tests verify its actual observable outcomes and both target builds retain source/artifact evidence without claiming sensor execution.

Current proof: Actual patched vendor source executes I2C decode/short/error/empty/contact/quality/deadline/cancel host tests; Arduino and protectedSDK build logs retain binary digests. Reviewedhostfixture assertsidenticalgenuinefreshdequeues/mixedvalidity/priorvalid→empty/stale/truncatednullsemantics inbothmodes withoutchangingoriginalproduction/goldens.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Full production GPIO/BLE adapter initialization/reset/error/cutoff/cancellation transitions must execute with both target build evidence. Current actual pinned-SDK fresh/empty/malformed/stale/truncated software core fixtures pass, including identical fresh records; they do not execute the complete physical adapter integration.

Prerequisite/evidence type: software_adapter_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Current actual portable compiler/executable stdout and firmware build job are bound. Full GPIO/BLE integration and physical vendor sensing qualification remain unexecuted.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bae7116461d4ddc0bf69cdc6e379e23697428e8d86418cb5c9c3af1f37349c6c. Actual current source and raw evidence supply this disposition.

## OTGD-043-VPPG-007-02 — PASS

Compile mistaken for participant qualification — - **GIVEN** stock/protected compilation and fictional interoperability pass but no genuine reference/device/study evidence exists - **WHEN** participant or model eligibility is evaluated - **THEN** those external gates remain closed and the reports explicitly distinguish software tests from real sensor validation.

Current proof: Client normalized vendor result remains modelEligible=false; exact inventory refuses unqualified current cardiac acquisition; protected report explicitly says unprovisioned build only/flashed=false/physical_qualification=false.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).
- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4700d729a416b4ba4ff9ceacf24dfb3d0d72d40f6d72e83b8dac79f0593defab. Actual current source and raw evidence supply this disposition.

