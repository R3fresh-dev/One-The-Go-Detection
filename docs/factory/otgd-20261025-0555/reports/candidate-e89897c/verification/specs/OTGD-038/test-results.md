# OTGD-038 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-study-enrollment/spec.md`; SHA256 `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8`.

12 cases, 6 requirements: PARTIAL 10, PASS 2. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-038-AND-STUDY-001-01 — PARTIAL

Invited customer opens research access — - **GIVEN** one operator-provisioned invitation for the signed-in account - **WHEN** memberships are requested - **THEN** the app displays that invitation and its actual status.

Current proof: The service membership item retains the latest immutable consent and the client refreshes/stores that item.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_consent_versions.py::test_updated_document_has_new_immutable_receipt_and_replay_keeps_current_pointer` — file SHA `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963`, line 45; 5 current observation(s).
- `apps/mobile/tests/controller.test.ts::explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 410; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- the app displays that invitation and its actual status: visible invitation/status rendering is not asserted by these checks.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 83140955eeb2407a4d9895076220db48ab4cb1ac3ba5636cede89aeb8be3d2ad. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-001-02 — PARTIAL

Customer guesses another study UUID — - **GIVEN** no membership in the requested study - **WHEN** its consent or capability route is requested - **THEN** access is refused without disclosing another participant's data.

Current proof: A foreign account receives403 on consent for an approved document.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_consent_versions.py::test_queued_confirmation_keeps_actual_past_time_if_approved_document_remains_current` — file SHA `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963`, line 118; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- access is refused without disclosing another participant's data: capability-route denial and response nondisclosure are not asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cbbf5c6dc911a6c8eeffae88b06a14e85ba5eabaf856cd3ea83bba604559afda. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-002-01 — PASS

Current approved consent is accepted — - **GIVEN** an eligible active invitation and complete approved document - **WHEN** the participant explicitly accepts - **THEN** a durable receipt records the version, digest, authenticated subject, client time, and server receipt time.

Current proof: Current versioned acceptance is201; exact acknowledgment time, server acceptance time, owned immutable historical receipt and document digest persist; same-key retry preserves identity and real PostgreSQL rejects receipt mutation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_consent_versions.py::test_updated_document_has_new_immutable_receipt_and_replay_keeps_current_pointer` — file SHA `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963`, line 45; 5 current observation(s).
- `apps/mobile/tests/controller.test.ts::explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 410; 1 current observation(s).
- `services/api/tests/test_participant_postgres.py::test_receipt_update_is_denied_in_postgres_without_blocking_privacy_deletion` — file SHA `ca85c9d47be13ef424a67378116482b36d8be72225c66619edac625d1b0159c0`, line 12; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f75153451b51073a541a9aef57abf56e1e70a4939cdce1c5c6748548897a850d. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-002-02 — PARTIAL

Protocol changes while the page is open — - **GIVEN** the displayed consent version is no longer current - **WHEN** acceptance is submitted - **THEN** the server rejects the stale version and the app loads the updated document without transferring the old acceptance.

Current proof: Old document acceptance403; immutable original remains; exact-version assessment requires fresh consent.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_consent_versions.py::test_updated_document_has_new_immutable_receipt_and_replay_keeps_current_pointer` — file SHA `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963`, line 45; 5 current observation(s).
- `apps/mobile/tests/study-consent.test.ts::only an active exact affirmative receipt suppresses new study consent` — file SHA `d862ef179f94af0018561a8c6dfa62972dcdd2d89c1e7060ea6a740552807481`, line 25; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- the app loads the updated document without transferring the old acceptance: no executed stale-page reload interaction is asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f62550bfc6512d8d3331bb1a69d513eb911ee28ff623b6a485012cf1b281ab08. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-003-01 — PARTIAL

Consent exists but optics remain unqualified — - **GIVEN** accepted consent and no approved optical configuration - **WHEN** the app requests eye capture - **THEN** passive guidance or an unavailable state is shown and no participant stimulus is emitted.

Current proof: Unprovisioned hardware and all human capture channels are unavailable; exact-version consent enables only task authority; rendered fictional eyes show unavailable and retain physical-onset limits. startEyeCapture implementation requires installed native module and admitted exact optical configuration before publishing active capture.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_unprovisioned_device_and_human_capture_unavailable` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 412; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_capabilities_change_with_consent_revision_notice_expiry_and_revoke` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 332; 5 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).

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

- After accepted study consent specifically without approved optical configuration, screen shows passive/unavailable and no participant stimulus is emitted: the inspected unprovisioned and visible copy checks do not execute this exact consent-plus-unqualified-optics branch.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 97669c152208628cb59d0892423e96fd172ff664a5e2ac70c439164972af31e7. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-003-02 — PARTIAL

Client edits capability JSON — - **GIVEN** a locally modified available flag - **WHEN** an upload or research request reaches the backend - **THEN** server-owned qualification and membership checks still prevent unauthorized operation.

Current proof: Current server study/protocol gates and fresh unavailable inventory refuse; client has no hardware event on stale alcohol capability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_real_session_start_requires_current_approved_study_and_exact_protocol` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 361; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::fresh absent-breath-adapter capability overrides stale cached availability before any hardware invocation` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1689; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- server-owned qualification and membership checks still prevent unauthorized operation after specifically edited client capability JSON reaches upload/research routes: not directly exercised.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f4a6e722f9f057ca21ac42b23252ab15f47036c4cccb0736c83ac49e352c4dfe. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-004-01 — PARTIAL

Cached scope cannot authorize offline capture — - **GIVEN** a cached available scope covering the device/configuration/channel - **WHEN** qualified capture is requested offline - **THEN** the app requires reconnection; local uncalibrated practice remains a separately labeled permitted path.

Current proof: Online context is frozen before any acquisition and ordered calls require grant and online-start before hardware.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::approved research start freezes exact online study/configuration context and device binding before any acquisition` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1401; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- the app requires reconnection; local uncalibrated practice remains a separately labeled permitted path when cached available scope is used offline: exact offline branch is not asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0f39444292317f7476419c935a156b310694af7e52065db99a7a363c3f68aced. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-004-02 — PARTIAL

Authorization expires offline — - **GIVEN** the phone was restarted or its wall clock was rolled back - **WHEN** new qualified capture is requested - **THEN** the app asks for reconnection and preserves existing records without acquiring under stale permission.

Current proof: Reboot/reader substitution refuses before hardware and before adding attempts.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::revoked consent, stale approval and reader substitution cannot invoke hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1560; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- the app asks for reconnection and preserves existing records after restart or wall-clock rollback: no offline restarted/rolled-back record-preservation journey is asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bbab8c94354fa1078867b3694a1a9a8c291e356eb5ca666c39c545ea1eea46d3. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-005-01 — PASS

Participant withdraws — - **GIVEN** active study access - **WHEN** the participant confirms withdrawal while offline - **THEN** local capture stops, the exact request is retained pending, and server completion is not claimed; later acceptance blocks verified uploads and returns the receipt.

Current proof: Withdrawal prevents queued consent transmission; original acceptance receipt remains immutable and reinvitation is required. Actual controller locally stops active fictional reader on offline withdrawal, invalid/null measurement, exact durable pending request body/key and truthful pending membership; later same intent confirmation leaves prior verified upload blocked and no capture restart.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::maintenance pauses queued consent and withdrawal prevents its later automatic transmission` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 531; 1 current observation(s).
- `services/api/tests/test_consent_versions.py::test_withdrawal_does_not_rewrite_original_acceptance_receipt` — file SHA `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963`, line 86; 5 current observation(s).
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/semantics/offline_withdrawal_probe.fragment.ts::supplemental offline active reader capture withdrawal retains exact privacy intent and later receipt without restoring uploads` — file SHA `24b54b1005e9a9e44e3dd5dea4f69e4447a36b892726e7186502edc446a713cf`, line 1; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/semantics/offline-withdrawal-observations.json` — SHA256 `d1301a78b47f955bf914d70b1d7dde52e85bf2f06ef9f259b5e846b9a313194b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Fictional software fixtures; no installed OS, physical stop, real participant consent, assay qualification or clinical/model approval. Supplemental probes do not replace full local/CI gates.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4d701b9591ce0935329517c6d7b3a0048cfc481c29b58332aab6860a8b211264. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-005-02 — PARTIAL

Old upload ticket is used after withdrawal — - **GIVEN** an artifact ticket issued before withdrawal - **WHEN** upload completion is requested afterward - **THEN** authorization is rechecked and the object cannot become a verified research artifact through the stale ticket.

Current proof: Administrative report completion rechecks consent after storage, refuses403/409/410 and keeps artifact unverified; generic capture route refuses administrative purpose. Inspected generic artifact_complete explicitly rechecks assert_artifact_admitted before/after external reads and qualification before commit.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_report_revisions.py::test_completion_reauthorizes_after_external_storage_and_cannot_resurrect_cleanup` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1127; 25 current observation(s).
- `services/api/tests/test_report_revisions.py::test_report_completion_and_generic_capture_purpose_are_separate` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1054; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- A participant capture artifact ticket issued before study withdrawal cannot verify on later completion: inspected executed race is administrative-report purpose, explicitly distinct from generic participant artifact. Need captured-raw preissued-ticket withdrawal execution; administrative result must not be substituted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 548e5655cecc7d970d35b920ce998b936597262db07caee90eb187b17d6999c8. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-006-01 — PARTIAL

Fresh production environment — - **GIVEN** no approved study records - **WHEN** research access opens - **THEN** no research capture or prediction is offered.

Current proof: Unconsented or inactive study/protocol denies session creation and absent model remains unavailable.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_operator_governance.py::test_real_session_start_requires_current_approved_study_and_exact_protocol` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 361; 5 current observation(s).
- `services/api/tests/test_operator_governance.py::test_capabilities_change_with_consent_revision_notice_expiry_and_revoke` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 332; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- no research capture or prediction is offered when Research access opens in a fresh production environment without study records: visible fresh-empty journey not directly asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e2444b2e3119fb034f682284b2e76885b08c5bb144bd4eee6a315ee5ed0f57a4. Actual current source and raw evidence supply this disposition.

## OTGD-038-AND-STUDY-006-02 — PARTIAL

Synthetic local fixture — - **GIVEN** a local development study fixture - **WHEN** it is displayed - **THEN** its synthetic identity and environment are explicit and its permissions cannot be reused in QA/prod.

Current proof: Fictional hosted preview refuses acquisition and inference despite public available capability flags.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::actual service component labels conditional approved channels and model support, while the fictional build refuses both` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1407; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- synthetic identity/environment explicit and permissions cannot be reused in QA/prod: cross-environment authority refusal is not tested by this component body.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ea4434d7f37cbedb2840e76a418fd47046c6826b7c05abf96d23e6fee68d7b82. Actual current source and raw evidence supply this disposition.

