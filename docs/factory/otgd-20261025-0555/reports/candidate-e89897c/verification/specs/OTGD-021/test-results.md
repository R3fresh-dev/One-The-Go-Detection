# OTGD-021 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-dashboard/spec.md`; SHA256 `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e`.

17 cases, 7 requirements: BLOCKED 2, NOT_RUN 1, PARTIAL 14. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-021-AND-DASH-001-01 — PARTIAL

dash-demo-home — - **GIVEN** an isolated demo workspace with a synthetic check - **WHEN** Home is displayed - **THEN** the demo badge and synthetic source description remain visible and no intoxication percentage appears.

Current proof: Guest browser finishes explicit synthetic record and domain result null probability; Home source identifies guest workspace.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/domain.test.ts::save freezes all evidence and never queues upload` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 233; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Exact Home demo badge plus synthetic-source description with saved check and no percentage is not asserted in mapped browser Home expectations; final export/result assertions are narrower.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c4f33141a1fc3a6256e1dbb5c03d29debc1167ed228224cd452c941a89fd2693. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-001-02 — PARTIAL

dash-old-check — - **GIVEN** the latest check was collected yesterday - **WHEN** the dashboard opens today - **THEN** its collection date/time is shown and the card does not claim to represent the user's present state.

Current proof: History sorter uses original acquisition timestamps; Home source renders created_at.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::mixed local and synced history uses acquisition time and stable identity ties` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 115; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No actual Home opened next day with yesterday check asserts date/time and absent present-state claim. Stable sorter alone does not verify card copy/time.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 160173d337ac81296ff4ee1cac9749c25d688d9c101f3711a78529bd177ab698. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-002-01 — PARTIAL

dash-double-start-tap — - **GIVEN** no active draft and an enabled start action - **WHEN** two rapid taps occur before navigation completes - **THEN** one logical session is created and both navigation events resolve to that session.

Current proof: Domain explicitly refuses second draft allocation and controller creates one session on ordinary Start.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::context must be explicitly confirmed and a second draft cannot start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 196; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Two rapid UI taps before navigation are not directly asserted with both callbacks resolving sameID and session count1. Sequential domain refusal is narrower than concurrent controller/UI admission.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1fe10726a4ec0aecacfc12eaf7cd55864b12534b2a48dfdf44a9d09c0d1ee682. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-002-02 — PARTIAL

dash-gated-capture — - **GIVEN** pupil capture is unavailable because its approved protocol is not configured - **WHEN** View availability is selected - **THEN** the app explains that channel's unavailability and does not open the camera/flash or replace it with a fabricated account measurement.

Current proof: Browser native task unavailable and qualified optical source requires approved configuration; no automatic substitute is permitted in account measurement.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Specific Home View availability action for absent optical config, exact blocker and zero camera/flash with no fabricated account projection is not directly asserted. Guest fictional example is an explicit different mode.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ff0bd54293539147414e2e0a4aa546d992ad14151d5b157a833f8a2bc7163396. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-002-03 — PARTIAL

dash-frozen-profile-at-creation — - **GIVEN** profile revision P1 is selected when Start check is pressed - **WHEN** P2 arrives before the first acquisition - **THEN** the draft retains P1, target_at equals its created_at, and its review identifies P1.

Current proof: Domain copies context at creation and target_at equals created_at; controller keeps original engineering snapshot after edit. Real measurement-mode software context P1=80kg/versionA before capture remains after P2=82kg/versionB, optional software interrupted ledger; new linked check usesP2/no carriedattempts, original staysP1.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::check freezes original profile timestamp and recomputes elapsed use at its start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 152; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::ordinary measurement P1 stays frozen after P2 profile update ${ledgerTransition ? "across a software-only interrupted first attempt" : "while the draft has no captures"}` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 628; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- The actual Review UI must identify frozen P1 after P2 arrives before first capture. The real measurement controller now proves P1=80kg/versionA and target immutability, then a new linked P2 check, but the visible P1 review assertion is not retained.

Prerequisite/evidence type: software_ui_assertion_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: No physical capture/another-device rendered version/native encrypted restart; these additions passed existing implementation and do not establish a profile behavior defect.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 054c444d9e2dcef15fad08b764c388206f18fa53a237d15ca9aea6210f3071a8. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-003-01 — PARTIAL

dash-resume-saliva-draft — - **GIVEN** a draft with one retained saliva attempt and no completed task - **WHEN** Continue check is selected - **THEN** the same draft opens at its next eligible step with the original sample identity.

Current proof: Actual browser Settings/Back returns same saliva draft text and Add example remains disabled, proving attempt retained.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::Settings and Back preserve the actual draft and collected example without a camera prompt` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 785; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Home Continue check specifically choosing next eligible step and exact original sampleID is not asserted; Check tab same displayed identity is narrower.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3ebabfbee52a01ce19c0a936f57503882062d807f659893bce056a69eb096d13. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-003-02 — PARTIAL

dash-task-interruption-return — - **GIVEN** the app was backgrounded during the native task - **WHEN** Home is opened and the draft resumed - **THEN** the interruption is shown and no task completion is inferred from elapsed wall time.

Current proof: Native lifecycle unit stops before terminal persistence; domain process interruption invalidates task with null aggregates.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::concurrent route/background stops issue native cancel immediately and wait for terminal persistence` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 148; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual backgrounded task ->Home ->resume displaying interruption and no wall-clock completion has no native OS execution; unit pure invalidation does not establish installed route.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f72a1054b5b14dd1f4323b6c41412b7a54bf641b6544b038602c2b27720c6023. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-004-01 — PARTIAL

dash-reader-disconnect — - **GIVEN** a connected reader with a recent battery value - **WHEN** its BLE link drops - **THEN** Home changes to Not connected and the battery value cannot remain labeled live.

Current proof: Presentation helper idle/failed link marks not connected and excludes battery; distinct LINK_DISCONNECTED title is asserted. Healthy signed protocol state/currentboot is distinct from servicebinding and syntheticconnection; actualHome/Device current/revoked/expired/owner/gen/offline observations match; mountedexpiry removesconditionalavailability, no flag grants capture authority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/device-presentation.test.ts::a saved reader alias does not become connected readiness or live battery` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 110; 1 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::permission, radio, reboot and unsupported reader failures have distinct recovery` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 117; 1 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::per-channel display uses active matching scope and unexpired admitted configuration independently from connection or binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 21; 1 current observation(s).
- `apps/mobile/tests/device-presentation.test.ts::a healthy signed reader connection is physical and retains current boot independently from service binding` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 82; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual Home and Device agree on a connected physical reader without synthetic or unconditional unavailable claims` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 49; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home and Device distinguish physical/synthetic connection from current, revoked, expired or mismatched channel authority` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 56; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Home expires its current channel observation while mounted and Device retains that expired status` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 130; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- A connected reader with recent battery must lose its live-battery label after BLE disconnect in actual Home. Current shared Home/Device connection states are rendered, but the recent-battery-to-disconnect transition is not directly asserted.

Prerequisite/evidence type: software_ui_assertion_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Loopback/framed/parsed-capability software fixtures only. Actual BLE handshake/radio/physicalreader/sensing qualification remain explicit; conditionaldisplay cannot independently qualify capture.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA cdff443b5dcdfa69269e1b6eb501869a1ccc6b4e05e7b49aefcfaada027ec7cb. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-004-02 — PARTIAL

dash-reader-reboot — - **GIVEN** a reader reconnects with a different boot identity - **WHEN** readiness is recalculated - **THEN** unfinished capture readiness resets and old monotonic readings are not presented as belonging to the new boot.

Current proof: BOOT_MISMATCH presentation clears connected readiness and shows Reader restarted; firmware source enforces boot-bound evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/device-presentation.test.ts::permission, radio, reboot and unsupported reader failures have distinct recovery` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 117; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual connected reader reboot/newboot and unfinished Home capture reset with old monotonic readings excluded is not asserted by presentation fixture alone; hardware reboot prerequisite remains separate.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f1826d001d37f6c3d7fa2b49a03d18886d5f33292cc022a1782a70bc21a9de53. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-005-01 — PARTIAL

dash-offline-check-list — - **GIVEN** cached permitted history and no network - **WHEN** Home opens - **THEN** cached rows remain available with an offline indicator and the latest refresh time.

Current proof: Local guest works while backend aborts; history sorter retains timestamps.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/tests/support-history.test.ts::mixed local and synced history uses acquisition time and stable identity ties` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 115; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Cached account history plus failed refresh needs actual Home assertions for retained rows, offline indicator and last refresh time. Offline empty guest workflow does not prove cached account Home.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0fc3a27b1a36b3f2bc1e65a6145b04caf5222c9b2bdb501e7aee937baccdfb42. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-005-02 — PARTIAL

dash-lost-finalization-response — - **GIVEN** a session finalization request timed out - **WHEN** Home renders its recent row - **THEN** the row remains pending until the server is reconciled using the original identity/idempotency key.

Current proof: Sync lost-registration reply retains retry_wait and exact key/body/gen, then completes same queue.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::a lost accepted response replays the same identity and unchanged bytes` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 290; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Fixture loses registration, not finalize response; no actual Home recent-row pending assertion until original finalization identity reconciles. Add accepted-finalize/lost-response context and visible pending→one result.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b89bba292c02bab53ceaa667db76bf90c0c3723c266f72e32c3359fb592ffe77. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-005-03 — PARTIAL

dash-reconnect-respects-manual-retry — - **GIVEN** an explicitly queued account check has automatic retries disabled - **WHEN** the network reconnects - **THEN** Home shows the waiting item and manual Upload/Retry action without beginning a network mutation.

Current proof: retryDue(false) sends zero requests and leaves ordinary explicitly queued row queued; pendingSync classifies requested delivery correctly.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::reconnection does not retry an ordinary explicit queue when preference remains off` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 280; 1 current observation(s).
- `apps/mobile/tests/support-history.test.ts::pending sync means explicitly requested delivery, not local saves or retired records` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 96; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Home waiting row plus manual Upload/Retry rendering on reconnect is not asserted. Engine request count proves scheduling guard, not actionable Home UI.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d9009dba82e1f4660b7d1c239a88e5317c26b653419ffcef4e7f85171e1d5173. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-006-01 — PARTIAL

dash-account-switch-race — - **GIVEN** an account-A refresh is in flight - **WHEN** the user switches to demo before the response returns - **THEN** A's response is discarded and no account data appears in demo.

Current proof: Account epoch late response cannot write; controller delayed history after sign-out rejected and visible/historyIndex empty.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::a new account epoch prevents late network results writing into its workspace` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 352; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::delayed history cannot enter another account or reopen a signed-out workspace` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 777; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Exact A->demo switch while Home refresh in flight and unchanged demo data is not directly asserted; sign-out-to-welcome is another transition.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9bc03bf3c9d06fe960c5f80ca5728a8261ea4807edb9132288058946839beb48. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-006-02 — NOT_RUN

dash-out-of-order-refresh — - **GIVEN** refresh B returns a newer session revision before refresh A - **WHEN** A completes later - **THEN** the displayed revision does not regress.

Current proof: Workspace generation guards reject stale owner responses; no same-owner revision-order assertion located.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::delayed history cannot enter another account or reopen a signed-out workspace` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 777; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Need B newer session revision arrives first, A older same-owner revision later, and displayed revision must not regress. Epoch/owner race is not this ordering scenario.

Prerequisite/evidence type: software_assertion_or_integration_evidence, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA bffa13351a06a4bc7e07b3b9cc403eb3bf62a35dbddbfe521bb4b73f383d3c82. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-007-01 — BLOCKED

dash-accessible-status — - **GIVEN** TalkBack is enabled and the reader disconnects - **WHEN** the status changes - **THEN** “Reader, not connected” is announced once without an unbounded repeating alert.

Current proof: Presentation helper provides distinct disconnect state and component roles exist.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/device-presentation.test.ts::permission, radio, reboot and unsupported reader failures have distinct recovery` — file SHA `b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733`, line 117; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual TalkBack disconnect announcement once with bounded repeats has no admitted Android execution.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 04d0f89d03498a376d803addefda4736a415ea4ee34620e4af7c79a5f6da3bf0. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-007-02 — BLOCKED

dash-ios-check-tab — - **GIVEN** an existing draft on iOS - **WHEN** the Check tab is selected using VoiceOver - **THEN** the same draft decision used by the primary CTA appears with its correct focus and no duplicate session allocation.

Current proof: Browser Check tab keeps same draft identity across Settings/Back. ActualDOMroute/dialog/backfocus, renderedmodalanimation preference/system, destructive light/dark normal/pressed compositecontrast atbothviewports.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::Settings and Back preserve the actual draft and collected example without a camera prompt` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 785; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::route headings receive focus across tabs, deeper navigation and Back` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 831; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::system motion and explicit overrides control rendered ordinary modal animation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 898; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::rendered destructive labels meet contrast minimum in light and dark themes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 943; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual iOS VoiceOver Check-tab focus and same primary-CTA draft decision/no duplicate allocation is unexecuted. Source route focus defect UX002 remains separate.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: These support ordinarysoftwareUI only; actual200%nativeTalkBack/VoiceOver/iOSReduceMotion acceptance remains unavailable, no wholecasePASS inferred.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA fdcc9bfd0eb0fc7b9954a701744c62922a39a83d428ba882dff676b4919d7f78. Actual current source and raw evidence supply this disposition.

## OTGD-021-AND-DASH-007-03 — PARTIAL

dash-alcohol-route-is-reachable — - **GIVEN** no alcohol instrument or approved configuration exists - **WHEN** the user selects Alcohol measurement on Home - **THEN** the alcohol availability screen opens with Hardware required, its requirements action, and working Back navigation.

Current proof: Alcohol screen direct component tests display future mg/L hardware/qualification boundary.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- No actual Home Alcohol action→Hardware required→requirements→Back browser journey is asserted by current direct Alcohol render fixture. Native physical fuel-cell channel remains independently unavailable.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c5a50bf55ea39a26a3329f158c171c25cb8ccaf43abde877b1eaea505d569d64. Actual current source and raw evidence supply this disposition.

