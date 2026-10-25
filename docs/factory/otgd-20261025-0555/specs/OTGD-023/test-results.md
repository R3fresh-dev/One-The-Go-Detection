# OTGD-023: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md`; SHA-256 `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 8 individually identified requirements and 19 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Independent source assertion audits for this dossier: Alcohol dependency and acquisition-boundary audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 19 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 3, "NOT_RUN": 1, "PARTIAL": 14, "PASS": 1}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-023-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-023 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md`; SHA256 `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4`.

19 cases, 8 requirements: BLOCKED 3, NOT_RUN 1, PARTIAL 14, PASS 1. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-023-AND-DEV-001-01 — PARTIAL

Connect a demonstration device — - **GIVEN** a supported phone and a discoverable synthetic peripheral - **WHEN** the user selects Find device, chooses the listed device, and its handshake succeeds - **THEN** the screen SHALL enter connected_simulator, show Simulated data, and enable only synthetic capture channels advertised by the handshake.

Current proof: Local simulator handshakes into connected_simulator with simulated source, exact channel values and no eligibility.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Discoverable peripheral Find/select UI sequence and enabling only advertised channels are not exercised on Android/iOS.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 405e9af9ef86fa112a6596c7fa4d26aa0ada38e92f362626e207df733f7c0d04. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-001-02 — PARTIAL

Device connected but assay unavailable — - **GIVEN** a connected reader advertising assay_ready=false - **WHEN** the user proceeds to the saliva step - **THEN** the step SHALL state that the assay is unavailable, offer its permitted sample-record or simulation workflow, and SHALL NOT report a chemical concentration or a completed assay merely because pairing succeeded.

Current proof: Unknown assay driver remains unavailable and laboratory path performs no BLE acquisition or concentration entry.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 649; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 870; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Connected assay_ready=false saliva screen must assert Assay unavailable and only permitted alternatives, without treating pairing as assay success.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA aa30dda326fa3127f39011d695a815c8b9122581ce68b4be072fb4e50c524b14. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-002-01 — BLOCKED

Permission denied without losing the check — - **GIVEN** an existing draft check and a first discovery request - **WHEN** Android denies the required permission - **THEN** no scan SHALL begin, the draft SHALL remain intact, and the screen SHALL explain the missing permission and present an appropriate retry or settings action.

Current proof: Presenter maps BLUETOOTH_PERMISSION_BLOCKED to named warning/recovery action.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/device-presentation.test.ts::permission, radio, reboot and unsupported reader failures have distinct recovery` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 117; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Real Android permission denial with existing draft must assert no scan, preserved draft and retry/settings recovery.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 080067cc7f940035882c837b0a8f57e26056041507381e5bd9a537f9e2189786. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-002-02 — BLOCKED

Radio disabled during discovery — - **GIVEN** an active scan - **WHEN** Bluetooth becomes unavailable or the app moves to the background - **THEN** scanning SHALL stop, any progress indicator SHALL settle into a named recovery state, and no stale discovery result SHALL be represented as a live connection.

Current proof: Presenter maps radio-off to recovery; unrelated consent/reboot tests do not establish scanning behavior.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/device-presentation.test.ts::permission, radio, reboot and unsupported reader failures have distinct recovery` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 117; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Native radio-off/background during discovery must stop scan, settle progress and reject stale discovery connection.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 7c0d27b0543621b12f72ef3dda699f652cdfc1d7561deff44e065567ea87feb0. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-003-01 — PARTIAL

Spoofed device name — - **GIVEN** an unprovisioned peripheral advertising the expected name and service - **WHEN** it claims that it is a validated reader - **THEN** the app SHALL refuse verified association, retain an explicit unverified-device reason, and SHALL NOT ingest human measurements from that connection.

Current proof: Decoder rejects validated_sensor claim and unknown protocol from unprovisioned peripheral.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::physical advertisement has a distinct bounded dialect and never a synthetic/validated source` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 232; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::capability source and calibration cannot promote an unprovisioned peripheral` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 60; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Full expected-name/service spoof connection must retain explicit unverified reason and assert no human ingestion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 74b6ca85e28870dad8f6666ed5928339211e1aa5768d0039f65345b5bc120006. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-003-02 — PARTIAL

Known binding belongs to another context — - **GIVEN** a device credential that verifies cryptographically but has no permitted binding for the current account or study - **WHEN** association is requested - **THEN** the app SHALL reject participant capture and SHALL not disclose another participant's sessions or identity.

Current proof: Wrong generation/scope binding throws; uninvited study has no available configurations.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual framed signed test peripheral requires verified binding before authorized capture` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 551; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::approved research start freezes exact online study/configuration context and device binding before any acquisition` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1401; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Cryptographically valid foreign-account/study binding must be exercised through association with explicit no-other-owner/session disclosure assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 21667271c204583f2ae8fc50a7c228b650317740134d5ab474f9a9f14f13ca09. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-003-03 — PARTIAL

Replayed binding challenge and substituted key — - **GIVEN** a previously consumed server challenge or a client-supplied replacement trust key - **WHEN** association is retried under that challenge or key - **THEN** binding SHALL fail without a new verified state; the client SHALL retain only its permitted simulator association and reveal no other owner identity.

Current proof: Server binding challenge is single-use/owner-scoped; physical proof signs exact transcript under test key.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_security.py::test_binding_challenge_is_single_use_and_owner_scoped` — file SHA `df21a343ca0d2ebb7e0232230c425b2e097e73d1e43f4137198ccfe50b092579`, line 92; 5 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::actual framed signed test peripheral requires verified binding before authorized capture` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 551; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Client-supplied replacement trust key and retained simulator-only association/no owner disclosure after retry are not all asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bcd389d95c913bf53a32d53acbc2f448dd76ad03f09498422ca150436138f04b. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-004-01 — PASS

Compatible handshake — - **GIVEN** matching protocol versions and subscribed events - **WHEN** the clock exchanges complete - **THEN** the association SHALL retain the narrowest valid observed offset interval and an uncertainty no smaller than the exchange and clock resolution permit.

Current proof: Clock selection retains three exchanges, chooses narrowest index1 with offset49.5/uncertainty5.5 including resolution padding, and rejects empty/regressed exchanges.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::clock evidence retains all exchanges and chooses narrowest interval with resolution padding` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 80; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA e5343bad4e88d3b43b61302b3de32e0e0345a155d1f7129d071ecdbc42ef232c. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-004-02 — PARTIAL

Counter restarts after device reboot — - **GIVEN** an accepted boot ID and an in-progress acquisition - **WHEN** a new boot ID or unexplained monotonic regression is observed - **THEN** the affected acquisition SHALL become invalid, previous clock alignment SHALL be discarded, and a new handshake and capture attempt SHALL be required.

Current proof: Journal rejects foreign boot identity and explicit clock discontinuity; controller rejects rebooted association before acquisition.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::identity, changed message ID content and replay sequence are independently checked` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 67; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::clock evidence retains all exchanges and chooses narrowest interval with resolution padding` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 80; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::revoked consent, stale approval and reader substitution cannot invoke hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1560; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Midcapture boot/regression must invalidate attempt, clear prior alignment and require a new handshake+attempt, with those state changes asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8cf5a68ff040041857312bc1c78c5a964b1e602676921878cfee20314a1d1c6f. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-004-03 — PARTIAL

Cached capability cannot enable an offline reader — - **GIVEN** a bound reader and a cached available human capability - **WHEN** the user starts capture while offline after changing the wall clock - **THEN** the app SHALL reject the qualified start and explain that current server authorization is required.

Current proof: Qualified capture obtains fresh grant/start and rejects mismatched boot before hardware invocation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::revoked consent, stale approval and reader substitution cannot invoke hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1560; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Cached available capability with network offline and modified wall clock must assert current-server-authorization explanation and zero hardware starts.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA dc46a89ae08a99e77e2d1f22ecd74386ce10c5e699de8b6895bd8c3926cb6b16. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-005-01 — PARTIAL

Small-MTU valid message — - **GIVEN** ATT MTU 23 and a valid bounded message - **WHEN** its fragments arrive in the supported order, including an identical duplicate - **THEN** the receiver SHALL reconstruct the exact logical bytes once, verify CRC and envelope semantics, and acknowledge one accepted message without duplicate capture events.

Current proof: MTU23 exact reconstruction, CRC public vector and larger-MTU duplicate-once logic execute.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::ATT MTU 23 carries eight logical bytes after the 12-byte header` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 15; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::larger MTU, out-of-order fragments and identical duplicate reconstruct once` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 22; 1 current observation(s).
- `firmware/tests/protocol_core_test.cpp::main` — file SHA `f9d29868cdde9121f5d8a6191d06df7fca14e5656316a6114bedbe21d4ab54bb`, line 5; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/raw/ci-firmware.log` — SHA256 `723d03e8ad8f725a1264467ca6ead937e9e361db6dd20939e3e71b13a10356fc`.

Exact unproved clause(s):

- MTU23 identical duplicate plus envelope acceptance and exactly one accepted ACK/capture event must be exercised together.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b64290a1ab19b981765fc684bf59618c3d4ed62f0296aa3763fc781fb94bafac. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-005-02 — PARTIAL

Malformed fragment flood — - **GIVEN** an established connection - **WHEN** the peripheral supplies an oversized declared length, conflicting duplicate, or more than the allowed in-flight transfer - **THEN** the receiver SHALL release bounded buffers, emit a named protocol failure, and SHALL not allocate memory proportional to attacker-provided lengths or store a partial successful reading.

Current proof: Oversized counts/MTU reject before allocation; conflicting duplicate/CRC and concurrent transfer/deadline fail and receiver can recover.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::impossible counts, encodings and excess MTU are rejected before allocation` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 37; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::corruption and conflicting duplicates fail closed and release in-progress storage` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 29; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::one transfer at a time and the 120-second assembly deadline are enforced` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 43; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No direct memory-allocation bound or partial-success persistence assertion covers the entire malformed flood at connection level.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9b6a8f0954151f657965545aaa16a858708782cef4ef943e44e497aef68a10ac. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-005-03 — PARTIAL

Signature valid for another measurement — - **GIVEN** a valid device signature for payload A and a selected snapshot containing changed payload B values - **WHEN** upload or finalization validates evidence - **THEN** the exact normalized payload hash/mapping check SHALL reject B, retain a provenance failure, and SHALL not infer trust from source=validated_sensor.

Current proof: Client altered normalized payload fails signed digest; client/server evidence tests reject projection tampering.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::signed completion binds each current authorization scope field and exact immutable projection` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 294; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Exact A signature with selected snapshot B must be driven through upload/finalization and retain named provenance failure, not merely local decode throw.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9e706c462b4de1c433f58f37a2e6e0c934739d0c441f5afe2e506992467e7173. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-006-01 — PARTIAL

Capture-complete acknowledgment is lost — - **GIVEN** one complete capture already stored locally - **WHEN** the peripheral retransmits its identical completion message after an acknowledgment timeout - **THEN** the receiver SHALL acknowledge the existing disposition and SHALL not create a second capture or a second sample.

Current proof: Message journal returns duplicate for identical ID/body and rejects conflicts/replays.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::identity, changed message ID content and replay sequence are independently checked` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 67; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Lost completion ACK after durable local save must retransmit and assert exactly one capture/sample plus repeated accepted disposition ACK.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e834a12ceb30e5e2d60e45c29a4664cbc4e7807e49ea16d61067e4740cc19966. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-006-02 — NOT_RUN

Completion arrives before missing chunks — - **GIVEN** an ECG or other multi-chunk capture with a missing chunk - **WHEN** capture_complete arrives - **THEN** the component SHALL remain incomplete and become invalid at its bounded timeout unless the missing bytes and final digest are verified; a notification alone SHALL not count as success.

Current proof: Related sample validators establish bounded chunks but do not drive missing-chunk completion order.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Deliver capture_complete before missing ECG chunk and assert incomplete state, bounded timeout invalidation and no success before verified bytes/digest.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 9ccc8c73b3bb8728c4dbbfbc2c2641718075e72ed3b96add5317acbfb6445385. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-007-01 — PARTIAL

User cancels during capture — - **GIVEN** an active device acquisition - **WHEN** the user selects Disconnect, Cancel, or Forget before any wider-draft confirmation - **THEN** the app SHALL send a best-effort cancel command, stop accepting that attempt's later payloads, retain its canceled/invalid disposition, and return to a recoverable device state.

Current proof: Controller cancellation invalidates before disconnect, clears association and rejects late completion by old workspace.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::cancellation invalidates before disconnect and prevents stale completion into a different workspace` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 99; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::cancellation clears trusted association immediately and drops a late signed completion` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 606; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Every Disconnect/Cancel/Forget UI action before draft confirmation plus best-effort cancel and recoverable visible state is not explicitly asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 31badb6ddf4feefea938938b4f68d2a64f0b140f9bc808fa65df044ae2758a22. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-007-02 — PARTIAL

Late event after reconnect — - **GIVEN** a new boot or capture attempt after reconnection - **WHEN** a queued event from the prior attempt arrives - **THEN** the receiver SHALL reject it by identity and SHALL not populate the new check with a stale reading.

Current proof: Foreign boot/session journal checks and old ACK rejection protect replacement association.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::identity, changed message ID content and replay sequence are independently checked` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 67; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::delayed old acknowledgment rejection cannot invalidate replacement association` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 634; 1 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::cancellation clears trusted association immediately and drops a late signed completion` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 606; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Late prior capture payload after replacement reconnect must explicitly leave the new check unchanged, not just reject old ACK failure.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 29c9af3bcc110e15bb89c8e4bd10023d061f4339cf6af66093cd8e91c33ea431. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-008-01 — BLOCKED

Simulator fixture on either platform — - **GIVEN** the same synthetic message sequence on Android and iOS - **WHEN** both clients complete a check - **THEN** each SHALL preserve simulated provenance and matching semantic records even though OS peripheral handles differ.

Current proof: Shared TS simulator preserves semantic source/record and complete evidence in Node tests.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No Android/iOS native application replay of the same sequence and semantic-record comparison exists.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 2149ad28dea98146c54bd6c1718be87da3e85fd08658f70fc4a52e34f6469933. Actual current source and raw evidence supply this disposition.

## OTGD-023-AND-DEV-008-02 — PARTIAL

Demo configuration copied into production — - **GIVEN** a production build with no approved provisioned device - **WHEN** a local demo file attempts to set a verified binding or validated source - **THEN** the claim SHALL fail independent verification and SHALL never unlock human capture or inference.

Current proof: Physical/synthetic capability decoders reject forged validated source and unknown protocol.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::physical advertisement has a distinct bounded dialect and never a synthetic/validated source` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 232; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::capability source and calibration cannot promote an unprovisioned peripheral` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 60; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Production build with copied demo binding file must assert independent verification prevents human capture/inference, not just decoder rejects a payload.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6afa1ebfda31c1b29699fa595ca21744b69d18f13eca551fb4f6e211de3c596d. Actual current source and raw evidence supply this disposition.
