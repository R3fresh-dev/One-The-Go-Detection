# OTGD-013: verification results

Canonical: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md`; SHA-256 `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 11 individually identified requirements and 23 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 23 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 1, "PARTIAL": 13, "PASS": 9}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-013-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-013 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md`; SHA256 `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29`.

23 cases, 11 requirements: BLOCKED 1, PARTIAL 13, PASS 9. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-013-CAN-SR-001-01 — PARTIAL

A physical advertisement requests simulator handling — - **GIVEN** a reader advertises prototype_sensor under an unknown protocol identifier - **WHEN** the app connects - **THEN** the association is refused before capture.

Current proof: Exact capability decoder rejects unknown protocol and simulated/validated physical source labels.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::physical advertisement has a distinct bounded dialect and never a synthetic/validated source` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 232; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Connection-level assertion that refusal occurs before any capture invocation for this malformed advertisement is absent.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 58506e44c541b7cd4cf524befee6613328ba1e1db8e34886f12caab13ff2f0c4. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-001-02 — PASS

Compatible reader awaits trust — - **GIVEN** a bounded compatible physical capability - **WHEN** the app connects without a verified binding receipt - **THEN** measurement remains unavailable until server-backed binding and fresh authorization succeed.

Current proof: Connected signed test peripheral exposes humanCaptureAvailable=false and rejects DEVICE_NOT_READY before verified proof/binding and current authorization.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual framed signed test peripheral requires verified binding before authorized capture` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 551; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b3b0cf819f423b5ad4bcca4afa5ef0c54138c179cf95a7d4df2f857fd09eaafd. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-002-01 — PARTIAL

Binding receipt references another device — - **GIVEN** successful proof from device A - **WHEN** a receipt references device B or another owner generation - **THEN** the native association remains untrusted.

Current proof: Wrong-generation installBinding throws PHYSICAL_CAPTURE_SCOPE; delayed foreign-device receipt cannot replace newer intent.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual framed signed test peripheral requires verified binding before authorized capture` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 551; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::late binding receipt cannot bind a foreign replacement or erase a newer same-owner intent` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1240; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Complete receipt mutation matrix including verified device A proof with receipt B must assert the native association stays untrusted for every matching field.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 319aebec082f47bf8c9e11da91403e7c2171ff2589c2dcc98ba3deaca8a7c8ce. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-002-02 — BLOCKED

Stock SDK lacks protected NVS — - **GIVEN** a stock SDK compilation without NVS encryption - **WHEN** the reader starts - **THEN** it refuses protected-reader advertising and emits no fabricated measurement.

Current proof: Stock signed-reader sketch compiles and protected SDK build succeeds separately.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_secure_reader_build.py::test_security_config_must_retain_every_enforced_security_option` — file SHA `beb1569ec43a14c535b13f29a77222e3d927b8a5c75f38e4bdf630eb79a7cc28`, line 77; 3 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/secure-sdk.xml` — SHA256 `1131c8095c4fa4d654f28ac7a2b907f587b8e8b58e129a25c1e1d0940c4c71b2`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/secure-sdk.xml` — SHA256 `257222d4edad30b4f2d654af931264ebd4d84e991402466b4d990086e9848fdd`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/secure-sdk.xml` — SHA256 `257222d4edad30b4f2d654af931264ebd4d84e991402466b4d990086e9848fdd`.

Exact unproved clause(s):

- No stock firmware boot executes to observe refused advertising and absence of telemetry when encrypted NVS is unavailable.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA a90654cf839f32df12f5e79331b84f53e562d4be3c889eb879801973898a5143. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-003-01 — PARTIAL

Phone alters maximum acquisition duration — - **GIVEN** an authentic server token binds15000ms - **WHEN** the phone requests a different channel, duration, context or configuration - **THEN** the reader refuses start before touching acquisition hardware.

Current proof: Host grant verifier validates real backend signature/material SHA and rejects altered signed channel/duration/context/configuration/origin fields.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_grant_test.cpp::main` — file SHA `f398cef88638601878d2182ed671be8624c14b3dcd9e5c4e1c23041e05d93b48`, line 12; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Exact valid-type phone option mutations against authentic unchanged 15000ms token, with a hardware-touch spy remaining zero, are not all exercised.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b8541d2c37dec78a1c5f44c6202303acfd55d84fb520448f447e02ba59727f47. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-003-02 — PARTIAL

Token includes a replacement verification key — - **GIVEN** the device trusts an offline provisioned server signer - **WHEN** a caller substitutes an SPKI or signer label in the token - **THEN** signature admission fails.

Current proof: Host verifier uses externally captured P256 SPKI and label; wrong domain and signed-field changes reject.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_grant_test.cpp::main` — file SHA `f398cef88638601878d2182ed671be8624c14b3dcd9e5c4e1c23041e05d93b48`, line 12; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Token-supplied replacement SPKI and signer-label changes are not directly tested against the provisioned firmware admission path.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cef08fddde091359637bb6bd695b921dd16fdc35383d0578da176cc8e28832a0. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-004-01 — PASS

Shortened grant reaches expiry boundary — - **GIVEN** a signed15s lifetime and nonce age15s - **WHEN** START arrives - **THEN** the reader refuses it even if the general nonce TTL is60s.

Current proof: Production nonceWithinSignedLifetime accepts age14999 and rejects ages15000/15001 for a signed15000ms lifetime; host execution observed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 131de4fb8ecea882cd7695066708d17530d6bfdd62b3c197bcacb7bdafd2538b. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-004-02 — PASS

Reversed or malformed timestamp — - **GIVEN** expiry precedes issue or contains invalid UTC syntax - **WHEN** the reader validates the token - **THEN** no hardware acquisition begins.

Current proof: Production UTC/lifetime helper rejects reversed expiry, malformed UTC, impossible date, leap second, timezone offset and excess precision before scheduler admission.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 567888d46850f8536ad59033d64dcd32ea907fddf0730830db7a963d9732dcb7. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-005-01 — PASS

Sensor contact is absent — - **GIVEN** a provisioned ADC channel with a separate contact input - **WHEN** contact indicates no attached sensor - **THEN** acquisition stops and no valid heart rate or ECG feature is produced.

Current proof: Production ADC core executes absent-contact callback, ends with lostContact and invalid signal, and performs zero additional analog-read callbacks.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA ba663874b59b08efa48aeb96abd85295063260fbac16b19fb4185338f9fe08c2. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-005-02 — PARTIAL

Loop misses samples — - **GIVEN** measured monotonic acquisition times skip scheduled observations - **WHEN** the bounded extractor processes the next actual sample - **THEN** it records explicit gaps and invalidates quality without generating missing values.

Current proof: Scheduler preserves actual indices0/3 and dropped=2 without interpolating raw observations.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- The skipped-observation subcase does not directly assert validSignal=false or a specific gap quality flag after settling that same capture.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1cb3004086803ef791a28144a84e4d1cc38c60c0b0227834e26baafcc4e16a68. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-006-01 — PARTIAL

Notifications are congested at cutoff — - **GIVEN** the TX queue cannot publish another message - **WHEN** the acquisition cutoff arrives - **THEN** the driver stops regardless of queued acknowledgments.

Current proof: ADC core stops exactly before bounded maximum and no subsequent tick invokes reads or stop again.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- No integrated nonempty/backpressured TX queue is held during cutoff to prove production loop ordering independently of acknowledgments.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d295010c91e199c3b7998d19dbc0b3bb7d0e3e4c7dadf7c4e407e913d95707ed. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-006-02 — PARTIAL

A slow ADC call crosses the bound — - **GIVEN** an ADC call returns after the bounded stop - **WHEN** its observation arrives - **THEN** the late sample is discarded and overrun cannot become valid evidence.

Current proof: Slow observation callback beyond stop sets ended/overran/invalid.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- The slow-read subcase does not directly assert discarded raw sample queue length or no accepted sample emission.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9c6f7acb6eb6a55a76cbad9501b538919cd1166844f6427d998f4e947ecd4f43. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-007-01 — PARTIAL

Link transition occurs after final origin check — - **GIVEN** a sensitive effect and a concurrent replacement connection - **WHEN** the final check/effect boundary executes - **THEN** the shared gate orders them and no old-origin action occurs in the replacement association.

Current proof: Concurrent OriginGate tests serialize check/effect against transition and reject old epoch after replacement.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Production hardware start/sign/connection-targeted notify effects are not directly exercised in that concurrency test.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 390301ca00b07b83cdf169dad79f08523361b6a15d23d139895d8ae89b9abc74. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-007-02 — PASS

Old ACK write fails late — - **GIVEN** account/device capture A is canceled and a new link connects - **WHEN** A's deferred acknowledgment write rejects - **THEN** the new association remains intact.

Current proof: Deferred old ACK rejection after disconnect/reconnect leaves new connected_reader association/device unchanged and causes no extra disconnect.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::delayed old acknowledgment rejection cannot invalidate replacement association` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 634; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f8d0db3a3bc18aa463d930958777ca63bf30814eac78df9c44b11d5b17894126. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-008-01 — PARTIAL

Unsupported raw configuration receives opt-in — - **GIVEN** the protected ADC raw encoding/capacity does not support the requested operation - **WHEN** a non-null raw permission is supplied - **THEN** the driver refuses that unsupported operation without silently recording or dropping an opted-in purpose.

Current proof: Client raw ECG encoder refuses PPG operation, excessive chunk count and altered sample scope; API refuses missing driver/raw codec authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::opt-in ECG handoff preserves measured signed chunks and refuses bounds/scope changes` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 715; 1 current observation(s).
- `services/api/tests/test_operator_governance.py::test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 649; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Protected driver unsupported encoding/capacity admission with non-null permission must assert no sampling/raw queue, rather than only client encode failure.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9528a3d5cb59552d3fde0c01441c2ad1082a5479d4860daa5c5852cafccf748a. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-008-02 — PARTIAL

Normalized feature bytes change in transit — - **GIVEN** a device-signed exact projection - **WHEN** a value or identity is modified - **THEN** client digest admission and server signature verification reject the evidence.

Current proof: Client rejects normalized payload changed under unchanged signed digest; unchanged signature verifies cryptographically.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::signed completion binds each current authorization scope field and exact immutable projection` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 294; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- The same changed normalized bytes must be submitted through server completion verification and reject there; client structural rejection alone is narrower.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c2eb7ddc0b6ff80062e0929d4bf919ebb7fdc2ad16a164515568c3522d962a39. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-009-01 — PASS

Build output omits NVS encryption — - **GIVEN** a successful compiler process but altered generated security configuration - **WHEN** the helper inspects the build - **THEN** qualification fails despite the process exit code.

Current proof: Helper test removes each required security option from generated sdkconfig and rejects; real protected CI build records validated app/bootloader/partition binary hashes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_secure_reader_build.py::test_security_config_must_retain_every_enforced_security_option` — file SHA `beb1569ec43a14c535b13f29a77222e3d927b8a5c75f38e4bdf630eb79a7cc28`, line 77; 3 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/secure-sdk.xml` — SHA256 `1131c8095c4fa4d654f28ac7a2b907f587b8e8b58e129a25c1e1d0940c4c71b2`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/secure-sdk.xml` — SHA256 `257222d4edad30b4f2d654af931264ebd4d84e991402466b4d990086e9848fdd`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/secure-sdk.xml` — SHA256 `257222d4edad30b4f2d654af931264ebd4d84e991402466b4d990086e9848fdd`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9706ed4ccb842c87dd7b71e0217da00bd48e56972511175222b98d006e9ff2e8. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-009-02 — PASS

Signing key is a public-readable symlink — - **GIVEN** a key path is symlinked or group/world-readable - **WHEN** the helper admits the key - **THEN** it refuses before invoking the build.

Current proof: Private-key admission rejects chmod0644, symlink, hardlink, wrong algorithm/size and nonregular paths; invocation precedes build in helper.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_secure_reader_build.py::test_only_private_rsa3072_build_key_is_admitted` — file SHA `beb1569ec43a14c535b13f29a77222e3d927b8a5c75f38e4bdf630eb79a7cc28`, line 42; 3 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/secure-sdk.xml` — SHA256 `1131c8095c4fa4d654f28ac7a2b907f587b8e8b58e129a25c1e1d0940c4c71b2`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/secure-sdk.xml` — SHA256 `257222d4edad30b4f2d654af931264ebd4d84e991402466b4d990086e9848fdd`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/secure-sdk.xml` — SHA256 `257222d4edad30b4f2d654af931264ebd4d84e991402466b4d990086e9848fdd`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 0f453535aa123c9c4d0c5fcefcc6cf3262e738033975c54b221c1906b8965db7. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-010-01 — PASS

ADC software builds without an attached board — - **GIVEN** core tests and board compilation pass - **WHEN** release readiness is reviewed - **THEN** physical key provisioning, contact/safety/calibration/timing and scientific qualification remain explicit pending evidence.

Current proof: Real Arduino/protected builds are explicitly build-only; protected report records flashed=false and physical_qualification=false with concrete binary hashes; physical prerequisites remain open.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).
- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 329e5a9dd6b85c3639074f9d140f27de47eae4bc4cf9d82f0a35703a9e101fa4. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-010-02 — PASS

Vendor assay SDK is undocumented — - **GIVEN** signed transport supports a compatible evidence schema - **WHEN** no actual approved acquisition SDK exists for the instrument - **THEN** capability remains unavailable and no assay value is fabricated.

Current proof: Governance rejects signed transport or recording approval naming a missing sampling driver/raw codec instead of creating software availability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 649; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA e8a248107afb95fe3dc594f9949aeef10afd5638fdeba6d2fb515230a4a619d6. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-011-01 — PARTIAL

A replacement peer receives an old authentication callback — - **GIVEN** a BLE connection transitions to a different peer or generation - **WHEN** authentication or a command callback from the original peer arrives - **THEN** it cannot authorize the replacement association or deliver previous health data.

Current proof: AuthenticatedPeer helper rejects old authentication and disconnect callbacks after replacement peer connects.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Actual ESP32 BLE authentication callback provenance and connection-targeted notification behavior are not executed on a device.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0e9facff8d6179e3631d8e87f0660a53a31cbbf3fa7251913837d6035fbe0d8c. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-011-02 — PARTIAL

Pairing negotiates encryption without MITM — - **GIVEN** a peer lacks the physical passkey and offers unauthenticated encryption - **WHEN** the peripheral evaluates completed pairing - **THEN** it refuses commands, disconnects and produces no participant telemetry.

Current proof: AuthenticatedPeer rejects missing Secure Connections/MITM/bond flags in host helper.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Real pairing negotiated without MITM must disconnect with no participant command/telemetry; helper returns false but does not exercise BLE stack side effects.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4055fa974017a3526c253fb973a6bac8d29887182e83b35e68d5563ca6222c4b. Actual current source and raw evidence supply this disposition.

## OTGD-013-CAN-SR-011-03 — PARTIAL

The current protected peer completes authenticated pairing — - **GIVEN** the current device peer completes Secure Connections with MITM bonding using its protected provisioned passkey - **WHEN** a command and notification are admitted under the same connection origin gate - **THEN** only that authenticated connection can send commands and receive its connection-targeted frames, while physical and clinical qualification remain separate.

Current proof: Helper permits only matching current authenticated peer/address/connection for writes and rejects replaced peer.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `firmware/tests/signed_reader_acquisition_test.cpp::main` — file SHA `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- Actual protected passkey provisioning, SC+MITM bonding, command and targeted notification are not executed on real BLE hardware.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e41588b8c3af96095eb856ca4601a9ccb3906d4a8afb52f78a283cd7ab33303f. Actual current source and raw evidence supply this disposition.
