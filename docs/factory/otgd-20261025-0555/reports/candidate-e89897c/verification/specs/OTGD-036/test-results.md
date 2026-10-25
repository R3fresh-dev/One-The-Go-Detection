# OTGD-036 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-settings-accessibility/spec.md`; SHA256 `2768fdfbe5ff0b1971d6aad04101ea2fa17db6f6c3012848aa3aa3f490e654c8`.

17 cases, 7 requirements: BLOCKED 3, PARTIAL 11, PASS 3. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-036-AND-SET-001-01 — PARTIAL

set-signed-out-navigation — - **GIVEN** demo is active and no account is authenticated - **WHEN** Settings is opened - **THEN** Sign in is available, cloud deletion is unavailable with its account requirement, and local demo clearing remains reachable.

Current proof: Guest browser reaches Settings/Privacy, Delete account absent and retry off; ordinary welcome Sign in available.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Settings itself must expose Sign in and cloud-deletion account-requirement wording while local clear remains reachable; current guest journey asserts Delete account absent, not every signed-out Settings item.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 57c5d3905d38de9d5f2059a01dbce2c2a2798e86282a1add771d1f17d7c9f6a7. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-001-02 — PARTIAL

set-active-check-switch — - **GIVEN** a check is active - **WHEN** Switch workspace is selected - **THEN** any active native run ends once before the decision; the UI explains that it cannot resume, the broader draft may be retained, and no record is moved between workspaces.

Current proof: RunStopGate deduplicates stop before persistence; controller stop asks native before awaiting radio, and browser Keep draft retains same attempt.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::concurrent route/background stops issue native cancel immediately and wait for terminal persistence` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 148; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 847; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::Settings and Back preserve the actual draft and collected example without a camera prompt` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 785; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Active native workspace switch before decision, explicit cannot-resume wording, ended once and no cross-workspace record move is not asserted end-to-end; browser draft is fictional nonactive task.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d92651562373cf2237208145d974f93313416058c2310209cc967ee2a023473a. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-001-03 — PARTIAL

set-research-access-visible-empty-state — - **GIVEN** a fresh account has no study memberships - **WHEN** the user selects Settings then Research access - **THEN** the feature opens its empty-state explanation and a working Back route without creating an invitation or enabling capture.

Current proof: Guest browser opens Research access and sees No automatic enrollment; ordinary service membership parser binds items.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/service-boundary.test.ts::actual backend app-config and capabilities responses decode without removing mandatory fields` — file SHA `3cfc990ad01c27ca3b1b6f1d0ce8185c3379932b50c70dc129928a443314a25e`, line 21; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Fresh authenticated empty-membership Settings→Research access→Back, no new invitation and capture remains unavailable is not directly asserted; guest empty-state differs from fresh account.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7c05b5efba525e47e4686e617c08216fb346e0c552cf297cde28896b8531d1d0. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-002-01 — BLOCKED

set-theme-restart — - **GIVEN** Dark theme was saved - **WHEN** the process is terminated and relaunched - **THEN** Dark theme is restored without a prolonged light-screen flash or record mutation.

Current proof: Browser dark radio changes computed color; controller saves theme/reducedMotion preference.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::navigation and theme components expose selected state at both viewport sizes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 746; 4 current observation(s).
- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual process termination/relaunch restores Dark without prolonged light flash and unchanged records is unexecuted; browser theme switching is not native startup flash evidence.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 1eae422b6d805ad15fe18ad491b747f44be003b7333e71e9cac05d848110e3ef. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-002-02 — PARTIAL

set-units-do-not-rewrite — - **GIVEN** finalized checks contain canonical ng/mL and profile cm/kg values - **WHEN** US customary display is selected - **THEN** profile presentation may convert units, saliva units remain qualified as reported, and stored measurements/record hashes do not change.

Current proof: Profile form25unit toggles preserve canonical values and browser toggles metric/imperial without losing displayed original values; saliva formatter preserves original units and qualifier.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::display rounding and repeated unit toggles preserve original canonical values` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 87; 1 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Finalized check hashes before/after global units preference and same rendered saliva/profile records are not compared in one test; profile draft-only conversion does not assert finalized-record nonmutation.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 28baa6b950f30c6bbaa29f027dfcab6302292961df57eaf8a58be4e5157d1426. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-003-01 — PASS

set-camera-denied — - **GIVEN** camera permission is denied - **WHEN** Permissions opens - **THEN** the camera row shows Denied with its feature explanation and Open app settings, without launching another prompt.

Current proof: Actual Settings DOM uses controlled camera status denied/canAskAgain variants, shows exact denial labels and feature explanation, never invokes prompt; OS-settings callback count remains0 until explicit button click then1. Current two-viewport component executions cover software behavior only; actual OS provider integration separately remains open.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::Settings reads denied, restricted, undetermined and failed camera status without prompting and opens OS settings only explicitly` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 297; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 06ec15dd787515f883de2897a3cf0985cb8b1f03beaa1044835c8161be40a417. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-003-02 — PARTIAL

set-permission-changed-outside-app — - **GIVEN** the user grants Bluetooth permission in OS settings - **WHEN** the app returns to foreground - **THEN** the displayed state refreshes and the reader feature decides whether a new scan is needed; an old scan is not assumed successful.

Current proof: Settings camera foreground event refreshes observed grant without prompting and out-of-order/unmounted/changed-owner reads discarded.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::Settings reads denied, restricted, undetermined and failed camera status without prompting and opens OS settings only explicitly` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 297; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::Settings ignores out-of-order and unmounted camera reads and replaces stale account and generation observations` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 392; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Canonical Bluetooth permission change outside app, foreground refresh, scan-decision/no old scan-success assertion is not exercised by camera provider fixture; actual Bluetooth OS transition also unavailable.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA eb521ee6e6152de5904a7ecf50e716d096ff76570098599539be59acd72cdd84. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-004-01 — PARTIAL

set-tampered-model-toggle — - **GIVEN** a modified preference file contains `inference_enabled:true` - **WHEN** Settings and the result workflow load - **THEN** the unsupported key grants no capability and probability remains unavailable in this release.

Current proof: Public version advertisement cannot enable inference; complete research result proof required independently.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/service-boundary.test.ts::research result format advertisement supports only the versioned reader and grants no inference authority` — file SHA `3cfc990ad01c27ca3b1b6f1d0ce8185c3379932b50c70dc129928a443314a25e`, line 72; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- An actual modified persisted preference inference_enabledtrue loaded through Settings/results must assert no capability or probability. Current public config format test does not inject preference storage. Legacy clause is scoped by shared-contractsection1, not prohibition on admitted1.1.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0e515f3d6a66c0afcda6a5e19dde6d9012fb6aa8c1ea99282a8f3002c1741415. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-004-02 — PARTIAL

set-qa-build-visible — - **GIVEN** the installed app uses QA services - **WHEN** Home or About is displayed - **THEN** QA is visible and the app cannot describe itself as a production clinical release.

Current proof: Source Home/About/welcome renders nonprod environment and clinical boundary; config pins expected environment.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/service-boundary.test.ts::unsupported app version, minimum version or contract pauses synchronization; maintenance is separate` — file SHA `3cfc990ad01c27ca3b1b6f1d0ce8185c3379932b50c70dc129928a443314a25e`, line 47; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual QA installed app Home/About rendered QA and no production clinical claim is not asserted by current local/test component fixtures; native installation remains external.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 63605fa4791b4bc2568854555c27273562533e5d3e62f9a2cfc74aab6d2e96a8. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-004-03 — PASS

set-authorized-looking-research-output-still-disabled — - **GIVEN** a server response or local record advertises an active research model - **WHEN** Settings or result navigation evaluates it - **THEN** inference_available remains false and no current surface displays an impairment probability.

Current proof: Accepted shared-contractsection1 plus authorized-model-execution AND-SET004 narrows historical fixedfalse to legacy/unadmitted claims. Version format advertisement grants no inference and forged/legacy proof is rejected; independently admitted1.1 remains separate conditional scope.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/service-boundary.test.ts::research result format advertisement supports only the versioned reader and grants no inference authority` — file SHA `3cfc990ad01c27ca3b1b6f1d0ce8185c3379932b50c70dc129928a443314a25e`, line 72; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 245; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA edba05a0f4b0b6d84aeea4ba79707991c877c7514ee3f9a124a61ce1689c3f26. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-005-01 — PARTIAL

set-diagnostics-copy — - **GIVEN** a connection error has a support request ID - **WHEN** the user reviews and copies diagnostics - **THEN** only allowlisted build/environment/error-reference fields reach the clipboard.

Current proof: Diagnostics generator copies only explicit build/environment/origin/requestID/categories, removes token/health/profile/payload and bounds arbitrary strings.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::support diagnostics copy only bounded explicit fields, never an error payload` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 10; 1 current observation(s).
- `apps/mobile/tests/support-history.test.ts::untrusted diagnostics strings cannot become fields or copied references` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 50; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual user reviews and invokes copy with a clipboard spy and exact allowed text is not in current tests; generating safe string is proven but clipboard interaction is not.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA d6daf3f20c1300434c7ef96eebb657bedcbcf43bb068812ba31522cf531bc9d5. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-005-02 — PASS

set-error-with-sensitive-payload — - **GIVEN** an internal exception includes a server payload with profile fields - **WHEN** diagnostics are generated - **THEN** the payload is excluded rather than serialized or truncated into the copy text.

Current proof: Actual contamination fixture includes token/profile/health/error message and verifies none of their content/keys serialized; arbitrary malformed fields refused and output bounded<1024. Entire source object is excluded, not truncated into diagnostics.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::support diagnostics copy only bounded explicit fields, never an error payload` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 10; 1 current observation(s).
- `apps/mobile/tests/support-history.test.ts::untrusted diagnostics strings cannot become fields or copied references` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 50; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 387c92b03684f9afbf551c24599a526e6b4589b4881e0f9a60a2b4d4c327f818. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-006-01 — BLOCKED

set-large-text-navigation — - **GIVEN** 200% system font scale on a 360 dp Android display - **WHEN** Settings and Privacy are traversed - **THEN** labels wrap, controls remain reachable by scrolling, and no essential action is hidden behind navigation or keyboard.

Current proof: Browser two-viewport checks minimum44x44tab bounds and no horizontal overflow. ActualDOMroute/dialog/backfocus, renderedmodalanimation preference/system, destructive light/dark normal/pressed compositecontrast atbothviewports.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::navigation and theme components expose selected state at both viewport sizes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 746; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::route headings receive focus across tabs, deeper navigation and Back` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 831; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::system motion and explicit overrides control rendered ordinary modal animation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 898; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::rendered destructive labels meet contrast minimum in light and dark themes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 943; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual Android200%systemfont360dp Settings/Privacy/keyboard reachability and wrapping is not executed; normal-scale browser viewports do not establish native scaling.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: These support ordinarysoftwareUI only; actual200%nativeTalkBack/VoiceOver/iOSReduceMotion acceptance remains unavailable, no wholecasePASS inferred.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 96f57b6aa55a24c651ed0935629a677b509d18b2d05d86aeb48f121d23679122. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-006-02 — PARTIAL

set-screen-reader-task-boundary — - **GIVEN** a timing-task configuration does not support the active input/accommodation - **WHEN** the user attempts that task - **THEN** the task feature explains the unsupported configuration and records unavailability rather than claiming equivalent measured timing.

Current proof: Native task qualification metadata and model gates refuse unsupported tuples; task unavailable state shown when native module absent.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 889; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Active screen-reader/input accommodation unsupported by task config needs explicit rejection/reason/no-equivalent-timing assertion; current tests toggle native availability, not accommodation compatibility. Actual accommodation qualification remains separate.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 930658c7eb34cc3ff744c3d67c4c1f50a8fa8b2e3d7f73f0c63f8848811d67cc. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-006-03 — PARTIAL

set-active-task-navigation-ends-before-dialog — - **GIVEN** a native reaction run is active - **WHEN** the user initiates a Settings/workspace route or End task - **THEN** the run ends once before an overlay, retained partial evidence is marked invalid, and subsequent draft choices never resume it.

Current proof: Controlled route/background stop coalesces once, awaits durable terminal; unmounted task invalidates and INTERRUPTED retained.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::concurrent route/background stops issue native cancel immediately and wait for terminal persistence` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 148; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 889; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual Settings/workspace/End action must demonstrate stop before overlay, partial invalid and draft choice never resumes it; current RunStopGate is pure and controller case stops manually, not overlay route sequencing.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 75b2ab317d0fbf11f38aea28e3d16186eb84abe9c5493781e6a2c9be23293c1c. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-007-01 — BLOCKED

set-ios-dynamic-type — - **GIVEN** a large accessibility Dynamic Type size and VoiceOver - **WHEN** the user changes theme and opens privacy controls - **THEN** each label/action remains reachable with correct state announcements and preferences persist across launch.

Current proof: Browser roles/selected theme and controls tested; preference saved in controller.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::navigation and theme components expose selected state at both viewport sizes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 746; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual iOS accessibility DynamicType+VoiceOver theme/privacy traversal, state announcements and persisted relaunch unavailable.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 79e307c7face5ed47cdaa2a2e6771dc8ec84649de3234ad7092261829bf9ea06. Actual current source and raw evidence supply this disposition.

## OTGD-036-AND-SET-007-02 — PARTIAL

set-ios-restricted-permission — - **GIVEN** iOS reports camera access restricted by device policy - **WHEN** the permission row is opened - **THEN** it shows Restricted, does not promise that an ordinary permission prompt will fix it, and preserves access to other permitted features.

Current proof: Controlled Settings restricted by policy label and no prompt are directly asserted; unrelated settings screen remains mounted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::Settings reads denied, restricted, undetermined and failed camera status without prompting and opens OS settings only explicitly` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 297; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual iOS native restricted provider state and continued other-feature access is unexecuted. Current DOM fixture does not establish device policy bridge; no ordinary prompt promise is rendered by source.

Prerequisite/evidence type: native_os_execution, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6030dcca3e49497dad52c2583041f2fd648ae99b3c998a8e9631a07e89629d8e. Actual current source and raw evidence supply this disposition.

