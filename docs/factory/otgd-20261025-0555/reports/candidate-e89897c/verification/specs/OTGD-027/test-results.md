# OTGD-027 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-heart-rate/spec.md`; SHA256 `e9288b9fbec177d7287962239555b7633a0cfbf80ecf3e1e350158da607f5139`.

16 cases, 7 requirements: BLOCKED 1, PARTIAL 14, PASS 1. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-027-AND-HR-001-01 — PARTIAL

Simulated PPG acquisition — - **GIVEN** synthetic mode and the named demonstration fixture - **WHEN** the user starts capture - **THEN** the app SHALL run its bounded fixture sequence, show simulated progress and signal quality, and save simulated provenance with no inference eligibility.

Current proof: Local PPG simulator retains exact72bpm/3s fixture, simulated source, no model eligibility and complete framed evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Visible bounded simulated progress/quality and saved provenance through full capture UI remain unasserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2308ffdf48566cb5d32a062eb4ef7c6242537dcddf8715fd30ec73fa4b62112b. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-001-02 — PARTIAL

Unsupported heart-rate device — - **GIVEN** a paired reader without the required PPG capability - **WHEN** the user opens Heart rate - **THEN** Start capture SHALL be unavailable with a clear missing-channel reason and SHALL not fall back to an unconfigured phone sensor.

Current proof: Reader inventory and capability decoder reject unknown hardware/source and missing driver support.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::capability source and calibration cannot promote an unprovisioned peripheral` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 60; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Paired reader missing PPG must render disabled Start with exact missing-channel reason and no phone-sensor fallback.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0a945dcaed98eadb3fda5183b7169611041d7cea3fb8cd0effa8ac1acfe5e765. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-002-01 — PARTIAL

Qualified participant capture prerequisites satisfied — - **GIVEN** a compatible configuration and verified bound reader - **WHEN** the user acknowledges the applicable instructions and selects Start capture - **THEN** the app SHALL freeze the configuration and association references for that capture and collect only the requested PPG modality.

Current proof: Frozen check records exact config/binding; full customer fixture persists context/attempt before grant/start and retains signed PPG projection locally.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::approved research start freezes exact online study/configuration context and device binding before any acquisition` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1401; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual qualified participant reader/instruction flow remains externally unqualified; channel-only acquisition is a software fixture boundary.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 37bca656859be43a4fd0507ae07087854b43f33c672b60567f65f0baa8dd86d8. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-002-02 — PASS

Unprovisioned reader sends a human-looking pulse — - **GIVEN** a synthetic-only unverified BLE connection - **WHEN** its payload claims a real participant source - **THEN** ingestion SHALL reject the source claim and SHALL not preserve it as a qualified physiological measurement.

Current proof: Synthetic dialect rejects prototype/validated source promotion; physical dialect never accepts simulated/validated source; no unverified human measurement can pass decoder.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::capability source and calibration cannot promote an unprovisioned peripheral` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 60; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::physical advertisement has a distinct bounded dialect and never a synthetic/validated source` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 232; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 11b52da3acb4d884ed2271589244a1bb621e921e37df3dd54fba1c9f25a961bc. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-002-03 — PARTIAL

Network missing at a qualified start — - **GIVEN** a verified reader with previously cached available capability - **WHEN** the phone is offline when Start capture is selected - **THEN** the qualified start SHALL remain blocked with current-authorization-unavailable; an old capability timestamp SHALL not authorize collection.

Current proof: Reader capture uses separate fresh online start and cannot derive authority from local fixture material alone.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Cached capability with offline phone must assert current-authorization-unavailable and no hardware starts, not only reboot/consent rejection.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6930fc80038e24a6b204e6ff79d70731530e0a46e7b168a87f29710a4892ae28. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-003-01 — PARTIAL

PPG device reports confidence — - **GIVEN** a capture containing the sensor's quality/confidence field - **WHEN** the app renders or exports it - **THEN** it SHALL label it Sensor signal quality using its documented scale, preserve provenance, and SHALL not display it as probability of correct heart rate or probability of intoxication.

Current proof: Vendor payload preserves confidence_percent as acquisition evidence with modelEligible=false, actual cadence unknown and no raw counts.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Rendered/exported confidence must explicitly say Sensor signal quality/documented scale and never accuracy/intoxication probability.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d6b46eacc64c9460e79817099ae2f7b1a48ca1183a7b6e6d6a7077b6344af145. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-003-02 — PARTIAL

PPG adapter tries to populate ECG variability — - **GIVEN** a modality=ppg capture - **WHEN** an adapter supplies ecg_status=valid or ECG-derived RMSSD - **THEN** schema/semantic validation SHALL reject the incompatible fields rather than labeling pulse-rate variability as ECG heart-rate variability.

Current proof: Vendor decoder rejects PPG projection relabeled ECG and baseline retains ecg_rmssd_ms=null.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).
- `apps/mobile/tests/cardiac-selection.test.ts::a cardiac modality is pinned at start and cannot be supplied to another component` — file SHA `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`, line 218; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Explicit PPG ecg_status=valid and finite ecg_rmssd_ms mutations must reject independently, including server schema path.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 178ca3298ce875c0f92423b3459b04804e6d0f0ba583a1efff838861ac1c7b66. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-004-01 — PARTIAL

Finger removed during measurement — - **GIVEN** a live valid-looking pulse value - **WHEN** the sensor reports no finger or the signal becomes stale - **THEN** the primary live display SHALL change to an actionable contact/stale state, and the old bpm SHALL not continue as if freshly measured.

Current proof: Synthetic poor_contact/stale fixtures clear current bpm, keep last value separately, latch reason and reject later completion.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/signal.test.ts::all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 62; 1 current observation(s).
- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Actual PPG live UI sensor contact/stale state and withholding old bpm must be executed; host/model fixtures do not exercise hardware display.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4a9ea0e72ec65837778a2838f6af4e8babbed06b582c277dde040a74bf937478. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-004-02 — PARTIAL

Few valid samples within a long recording — - **GIVEN** a recording whose elapsed duration meets the requested duration but whose valid samples do not - **WHEN** completion is evaluated - **THEN** the capture SHALL fail its configured adequacy rule or remain incomplete, with no apparently ordinary final heart-rate value.

Current proof: Synthetic insufficient_samples clears bpm and rejects completion; vendor no-data yields invalid null bpm.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/signal.test.ts::all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 62; 1 current observation(s).
- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Long-enough duration with too few otherwise valid vendor records must directly assert configured adequacy and null final heart rate.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 63ff742862b2028010ded14acbcb809a39a12e08e2646b7fc8df603be59d7251. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-005-01 — PARTIAL

Reboot resets sensor counter — - **GIVEN** an active PPG capture - **WHEN** a new boot ID or regressed monotonic counter appears - **THEN** the attempt SHALL become invalid, the clock association SHALL be cleared, and the next acquisition SHALL require a new capture identity and synchronization.

Current proof: Journal rejects boot mismatch and synthetic reducer rejects foreign boot/sequence replay.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::identity, changed message ID content and replay sequence are independently checked` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 67; 1 current observation(s).
- `apps/mobile/src/device/tests/signal.test.ts::stale identities, schema additions, sequence replay and bounded sample tampering cannot populate a current capture` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 81; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Active PPG reboot/regression must explicitly clear clock association and require new synchronization+capture identity.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 42132a50643b5a81f68d09136daf5d8ab04ed1ac89ce5f3af8b856700e71947a. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-005-02 — PARTIAL

Duplicate completion after a successful capture — - **GIVEN** an immutable accepted capture - **WHEN** its identical completion event is repeated - **THEN** the app SHALL retain exactly one logical capture, acknowledge the repeated event, and SHALL not overwrite the stored feature or timestamp.

Current proof: Journal deduplicates identical body and protects immutable message ID; full customer capture stores one immutable projection.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::identity, changed message ID content and replay sequence are independently checked` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 67; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Repeat actual accepted PPG completion after ACK timeout and assert one saved capture, repeated ACK and unchanged timestamp/feature.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c25b362f03c13f37d76c1538e35f93c6195c2b9edbfca76a8936e44666110547. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-005-03 — PARTIAL

Canceled route change keeps an ended attempt — - **GIVEN** PPG acquisition is active and a navigation confirmation may be displayed - **WHEN** the user selects Back and then keeps the wider draft - **THEN** local acquisition SHALL already have stopped and the prior attempt SHALL retain its terminal invalid/canceled evidence; it SHALL never resume its original buffer.

Current proof: Controller cancellation precedes awaited transport stop and preserves terminal invalid evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::cancellation invalidates before disconnect and prevents stale completion into a different workspace` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 99; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- PPG Back then Keep draft UI journey must assert prior buffer cannot resume and wider draft survives, including visible confirmation ordering.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ce1b3a88dda7383c636eb5182b53567682847f1a55d9d0f4736565d7b8cb6576. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-006-01 — PARTIAL

Network unavailable after allowed capture — - **GIVEN** a complete permitted local PPG capture and no network - **WHEN** the user reaches Review - **THEN** the app SHALL display the saved measurement and Saved on this device, retain its exact immutable record, and SHALL not claim it was uploaded or analyzed remotely.

Current proof: Full customer PPG completion persists locally and queues only explicit upload.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Disable network after allowed capture, open Review and assert Saved on this device/unchanged immutable record/no uploaded or remote-analysis claim.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5b42e375e0ea2ec60dad5863b76747915259ecb146f8a33755974eb72c1a1088. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-006-02 — PARTIAL

Raw-signal storage not authorized — - **GIVEN** a protocol allowing only summary features - **WHEN** a PPG stream is processed - **THEN** raw buffers SHALL remain transient and be released after permitted extraction, while the allowed summary/configuration/quality metadata MAY be saved.

Current proof: Vendor factory removes raw IR/red counts, client accepts derived-only zero sample chunks/rawRecording=null and rejects raw field injection.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).
- `firmware/tests/sparkfun_ppg_test.cpp::main` — file SHA `c99c4f33547dcf20d4091bf867e2c8d6ac7452f0fc784a1d8e89ad5bce6ab6bb`, line 83; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Actual in-firmware transient raw buffers released after extraction and no persistent raw payload on summary-only path remain unobserved on hardware.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 539fcbf9ab62e13d3acca051b3518ae06df66df3c4f78447a39bf4fc34223546. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-007-01 — BLOCKED

Same quality-loss fixture on both platforms — - **GIVEN** a recorded synthetic sequence containing good contact, contact loss, and recovery - **WHEN** Android and iOS replay it - **THEN** both SHALL show matching quality transitions and SHALL not carry forward the last valid pulse during the gap.

Current proof: Shared synthetic reducer executes contact/stale failure transitions and clears bpm in Node.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/signal.test.ts::all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 62; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Same good/loss/recovery sequence must run in both actual Android/iOS apps and compare visible transitions without carrying stale bpm.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 07fff1dc1eb33eb0967709af6138ed0dc1468f7d6a4cce50c9b9acadbc4aaeda. Actual current source and raw evidence supply this disposition.

## OTGD-027-AND-HR-007-02 — PARTIAL

New firmware changes quality scale — - **GIVEN** a firmware revision outside the configured compatibility list - **WHEN** the reader reports a confidence field with a different scale - **THEN** the capture SHALL be blocked or marked incompatible until a reviewed adapter/configuration establishes its meaning; the app SHALL not reuse the prior threshold silently.

Current proof: Client rejects changed SDK commit/config evidence; exact firmware inventory enforced before authorization.

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

Exact unproved clause(s):

- New firmware specifically changing confidence scale must assert incompatibility until reviewed adapter/configuration rather than silently reuse old threshold.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9a8257489385b4ec4fc570dc2cb121d09449ad5612629f8dfe0ad0d0101f321c. Actual current source and raw evidence supply this disposition.

