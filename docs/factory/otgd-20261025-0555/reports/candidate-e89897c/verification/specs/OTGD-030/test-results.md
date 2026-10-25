# OTGD-030 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-onboarding/spec.md`; SHA256 `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee`.

14 cases, 6 requirements: BLOCKED 4, NOT_RUN 1, PARTIAL 8, PASS 1. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-030-AND-ONB-001-01 — PARTIAL

onb-first-launch-demo — - **GIVEN** a fresh installation without preferences - **WHEN** the user selects Explore the demo - **THEN** the introduction identifies synthetic sample/sensor values and does not display a probability or create a research enrollment.

Current proof: Current browser traverses welcome/demo/notice and exports guest_demo measurement_only/null probability; research access states No automatic enrollment. Source intro explicitly names synthetic sample/sensor examples.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Exact introduction fictional provenance text is not asserted in current browser test, nor is enrollment store unchanged checked at entry. Existing final-record null probability is narrower than full introduction criterion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 940843d53ff21b48df94879ad4d7220e12318a31e5e4c2bd22e66547d6ca899b. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-001-02 — PARTIAL

onb-signed-in-still-measurement-only — - **GIVEN** an authenticated account with no study authorization - **WHEN** onboarding completes - **THEN** the dashboard shows measurement-only availability and no study capability is inferred from the account or notice receipt.

Current proof: Ordinary account fixture lands Home; API public config inference_availablefalse and missing study notice/consent cannot confer execution authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).
- `services/api/tests/test_api.py::test_health_and_compile_time_inference` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 83; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual authenticated no-study onboarding dashboard lacks a rendered assertion of measurement-only availability and no implied study capability. Current browser journey is guest, not authenticated account.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5d17c970498503a8475cabf568821a5afb61465c60349abc7367320abf8ec58e. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-001-03 — PARTIAL

onb-research-configuration-cannot-change-release — - **GIVEN** an authenticated account and a valid-looking research manifest - **WHEN** onboarding or public configuration reports research availability - **THEN** the release retains inference_available=false and displays no probability or research-estimate capability.

Current proof: Public config returns inference_availablefalse, while independent conditional account model support remains possible under later approved amendments. Client rejects unbound proof and unqualified synthetic records. Actual rendered Home/history/welcome conditional software copy, current account/generation and revoked/offline guards, immutable 1.1 proof and legacy/guest refusal. Later admitted 1.1 delta explicitly supersedes blanket legacy 0.1 fixed-false wording.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_health_and_compile_time_inference` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 83; 5 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual Home changes research access with current identity capabilities and immediately with revocation` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 137; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual saved row and History preserve historical research and invalid proof rather than frozen measurement-only copy` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 125; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual rows and details retain measured, invalid, inconclusive, pending and fictional boundaries` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 177; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual welcome describes measurement defaults and separate research authority without enrollment` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 228; 1 current observation(s).
- `apps/mobile/tests/result-presentation.test.ts::current research scope requires live matching authenticated account and generation capabilities` — file SHA `2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120`, line 120; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 147; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- A valid-looking public model manifest supplied during the actual onboarding transition is not directly exercised to prove no new capability/probability. Current onboarding copy is reconciled and capability/proof guards are tested; this is a residual scenario evidence gap, not the old copy defect.

Prerequisite/evidence type: software_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: SSR/controllers and fictional typed fixtures; not an independently enrolled participant, installed OS or real external study. No assertion of a new clinical/model admission.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 63a2dbdb26f3fd3bec325a20cbe784e8b3eab341c46cbc8315b237b0c2c2dd47. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-002-01 — PARTIAL

onb-demo-does-not-upload — - **GIVEN** a completed demo check and a subsequently authenticated account - **WHEN** the user opens the account workspace - **THEN** demo history is absent from account history and no upload request for the demo check is enqueued.

Current proof: Guest check refuses queue/upload and account-empty workspace has no checks; controller saves guest with no queue.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::guest check cannot upload and never acquires an account owner by sign-in` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 246; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- One actual saved demo then sign-in transition with account history excluding exact guestID and zero enqueued guest operation is not asserted by these separated contexts.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 09a48e4482a52cd479f4c09928ed52b269b4b60b2ba7693cbffe776ec5b34f96. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-002-02 — NOT_RUN

onb-cancel-workspace-switch — - **GIVEN** an unfinished demo check - **WHEN** the user selects Sign in and then Stay in check - **THEN** the check remains visible with unchanged identity and no authentication browser is opened; if a native run had already ended to leave capture, it remains ended with that fact displayed.

Current proof: Domain enforces one owned draft and controlled native Stop preserves terminal completion; source offers stay/leave confirmation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 847; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No named current acceptance test invokes Sign in then Stay in check with unchanged checkID, no auth browser, and explicit previously-ended native run fact. Existing profile-cancel/browser reload is another action.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 0943429604ac321622182a230782c2dea113fc6233af5f007f6b8c3348301d3f. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-002-03 — PARTIAL

onb-guest-demo-never-has-upload-path — - **GIVEN** a guest demo check and an authenticated local/QA synthetic project both exist - **WHEN** the user opens the guest check, signs in, or reconnects - **THEN** the guest check remains local and has no upload action; a separate account-owned synthetic fixture requires its own creation and upload choice.

Current proof: Guest upload is explicitly rejected; isolated account engineering fixture is separately created and never shares guest ownership.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::guest check cannot upload and never acquires an account owner by sign-in` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 246; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Simultaneous guest and account-owned fixture followed by sign-in/reconnect requires a direct no guest upload action/no queue assertion plus distinct fixtureID. Current unit tests separate those workspaces.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 62b3df22ff0bf82b69be9f2509c8f105645576a5ef0308ead2052d67400ad14e. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-003-01 — PARTIAL

onb-notice-accepted-once — - **GIVEN** the current notice is visible and its checkbox is initially unchecked - **WHEN** the user checks it and selects Continue - **THEN** one dated receipt is saved, the dashboard opens, and repeating the submission creates no duplicate receipt.

Current proof: Browser notice starts unchecked/disabled and explicit checkbox opens Home. Controller sends exact displayed sha/version/gen; lost-response retry retains timestamp/key/body.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::notice and context components require separate explicit acknowledgments` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 575; 4 current observation(s).
- `apps/mobile/tests/controller.test.ts::notice acknowledgment is explicit and keeps the exact displayed version through account synchronization` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 748; 1 current observation(s).
- `apps/mobile/tests/sync.test.ts::lost notice acknowledgment response replays its durable timestamp and key before unblocking` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 456; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- One durable dated receipt and repeated successful acknowledgment creating no duplicate server receipt is not asserted; lost first reply unit transport does not count real duplicate receipts.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e85b4a87f0d53fdd32d5b0d6eec33ac1b82df53bc140a58cad4750965f3f252e. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-003-02 — PARTIAL

onb-stale-notice-write — - **GIVEN** the server requires a newer notice than the bundled accepted version - **WHEN** the app attempts an account write - **THEN** the write remains pending, the app offers the newer notice, and neither a fabricated acknowledgment nor a research-consent record is sent.

Current proof: API write without current notice403; client blocks save without acknowledgment and sends exact displayed notice version/hash.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_no_write_without_current_notice` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 116; 5 current observation(s).
- `apps/mobile/tests/controller.test.ts::notice acknowledgment is explicit and keeps the exact displayed version through account synchronization` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 748; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Newer server notice versus bundled accepted old version needs a queued write/pending state/new notice UI assertion and zero fabricated acknowledgment/consent requests. Reviewed test only clears acknowledgment, not mismatched versions.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 87d83b66d4c21145ccfde50a013b339b72d1599904622ed50130ecaf070625fa. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-004-01 — PASS

onb-airplane-mode-demo — - **GIVEN** the phone is offline on first launch - **WHEN** the user completes demo onboarding - **THEN** the dashboard and synthetic check are usable and the UI describes their local state.

Current proof: Browser denies backend network, completes first-use notice/context and synthetic check, displays local finalized state and exports measurement_only/null probability. Controller companion catches one offline config failure and guest save leaves no queue. Bounded offline browser software journey only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a55336088436238e9ec0bcd8eabbac200fcf8edcc498092df4698fb2b93bebc0. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-004-02 — PARTIAL

onb-no-permission-prompts — - **GIVEN** every OS permission is denied - **WHEN** all onboarding screens are traversed - **THEN** no permission dialog appears and onboarding is not blocked by those denials.

Current proof: Browser guest and fictional preview run with zero camera/Bluetooth calls; native task unavailable is visible and does not block onboarding.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/hosted-preview.spec.ts::standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records` — file SHA `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`, line 3; 4 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/hosted-preview.xml` — SHA256 `c416ab04fd7865c331eb9dfb7287e5f3d8933e422590fa2ddce38c7905702434`.

Exact unproved clause(s):

- Actual installed OS with every permission denied traversing all onboarding and no permission dialog is unexecuted. Browser spies do not establish OS denial lifecycle.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a1ea48eb406f994e204361a6454d8ba015bd3645a868713bd50cd5e94a8c82e0. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-005-01 — BLOCKED

onb-kill-before-commit — - **GIVEN** acknowledgment persistence has not completed - **WHEN** the process is terminated and relaunched - **THEN** the notice remains unacknowledged and no account write is sent.

Current proof: Browser reload returns first-use and never claims native encrypted persistence; queue logic does not mark lost notice reply acknowledged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::lost notice acknowledgment response replays its durable timestamp and key before unblocking` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 456; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::profile errors remain actionable and browser reload never pretends encrypted persistence` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 227; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Native process termination before acknowledgment transaction commit and relaunch, unacknowledged notice and zero account writes is not executed. Controlled Promise/lost reply is not process death.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 94fb9515ec0c37e365978924c69609c6c435a980ae1d4d51bb5ac9e546aef584. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-005-02 — BLOCKED

onb-kill-after-commit — - **GIVEN** the acknowledgment transaction completed before process termination - **WHEN** the app relaunches - **THEN** the chosen workspace opens with the existing receipt and no duplicate onboarding event.

Current proof: Controlled native store reopen preserves an ordinary serialized workspace; controller retains accepted hash.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::notice acknowledgment is explicit and keeps the exact displayed version through account synchronization` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 748; 1 current observation(s).
- `apps/mobile/tests/native-storage.test.ts::concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 128; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Native process termination after actual acknowledgment commit and relaunch with same dated receipt/no duplicate onboarding event has no admitted actual OS execution.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA d9a7170842963b75b4855f3f8da1109343fd6d1d749c2c0f768597f8a5989592. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-006-01 — BLOCKED

onb-talkback-and-large-text — - **GIVEN** TalkBack and 200% font scaling are enabled on a 360 dp-wide Android screen - **WHEN** the user traverses welcome and the notice - **THEN** each action is reachable, its role/label is announced, and scrolling exposes the entire notice and Continue control.

Current proof: DOM component tests assert roles and reachable controls at two viewports; exact notice text hash is verified server-side.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::notice and context components require separate explicit acknowledgments` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 575; 4 current observation(s).
- `services/api/tests/test_api.py::test_notice_exact_text_hash` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 106; 5 current observation(s).

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

- Actual Android TalkBack+200%font360dp welcome/entire notice/Continue traversal is not executed. DOM role checks cannot establish spoken announcements or native scrolling.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 50ffecca1ffe91937bd127b736c91203586066e4c60c6a6ae6b61eb4fb42e738. Actual current source and raw evidence supply this disposition.

## OTGD-030-AND-ONB-006-02 — BLOCKED

onb-ios-parity — - **GIVEN** a fresh iOS installation with Reduce Motion enabled - **WHEN** demo onboarding completes using VoiceOver - **THEN** the same workspace and notice states are stored without required animation or a camera/Bluetooth prompt.

Current proof: Fictional browser guards avoid camera/Bluetooth; shared workspace/notice logic is exercised. ActualDOMroute/dialog/backfocus, renderedmodalanimation preference/system, destructive light/dark normal/pressed compositecontrast atbothviewports. Current DOM focus restoration, modal semantics, contrast and reduced-motion assertions are executed; no actual TalkBack/VoiceOver/native OS claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/hosted-preview.spec.ts::standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records` — file SHA `8862cec87ea3ab0121502d9d5a6da7faca0d70a5dab77b4914f2448ee5659e1d`, line 3; 4 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::route headings receive focus across tabs, deeper navigation and Back` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 831; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::system motion and explicit overrides control rendered ordinary modal animation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 898; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::rendered destructive labels meet contrast minimum in light and dark themes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 943; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/hosted-preview.xml` — SHA256 `374044d14f7d671489e6a5e364841c09bbff43fc2ec9a338e00e74139b465f6c`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/hosted-preview.xml` — SHA256 `c416ab04fd7865c331eb9dfb7287e5f3d8933e422590fa2ddce38c7905702434`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual fresh iOS VoiceOver+Reduce Motion onboarding, stored state and no native permission prompt is unexecuted. Current DOM focus/reduced-motion software repairs have current named observations; actual OS scenario remains unexecuted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: These support ordinarysoftwareUI only; actual200%nativeTalkBack/VoiceOver/iOSReduceMotion acceptance remains unavailable, no wholecasePASS inferred.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA e1a627a1edc42496a7dd1299ca83decaeb6a8f1185d39bb255aa4e15306f1617. Actual current source and raw evidence supply this disposition.

