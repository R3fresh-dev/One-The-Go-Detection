# OTGD-026: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md`; SHA-256 `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 8 individually identified requirements and 21 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Independent source assertion audits for this dossier: Alcohol dependency and acquisition-boundary audit; Authenticated ordinary-web live test source audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 21 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 3, "PARTIAL": 16, "PASS": 2}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-026-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-026 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-guided-check/spec.md`; SHA256 `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562`.

21 cases, 8 requirements: BLOCKED 3, PARTIAL 14, PASS 4. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-026-AND-CHECK-001-01 — PARTIAL

Start a synthetic check — - **GIVEN** local demonstration mode and no physical assay - **WHEN** the user selects Start check - **THEN** the app SHALL allocate a new session UUID, display Simulated data for fictional channels and Uncalibrated practice for actual native taps, and present concrete synthetic steps without requiring a cloud account or claiming a physical measurement.

Current proof: Guest controller allocates UUID, confirmed context and explicit fictional captures; browser shows unavailable native task and measurement-only completion without cloud account.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Rendered Simulated data for each fictional channel versus Uncalibrated practice for actual native taps in one synthetic check is not directly asserted by current no-native browser journey. Actual native mixed-provenance path remains separate.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fe4edfb7372e6dc51d88dc9a8cb9ca148733578156f791d72ef97240afda06ee. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-001-02 — PARTIAL

Required capability is blocked — - **GIVEN** an unavailable approved optical or assay configuration - **WHEN** the checklist evaluates that capability - **THEN** it SHALL show the specific blocker and an allowed preview, sample-record, or skip action where the mode permits it; it SHALL not show a completed measurement or fabricate a substitute.

Current proof: Conditional availability component distinguishes approved/unavailable channel; participant flow shows pending lab without fabricated chemistry; browser permits no-native skip.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::actual service component labels conditional approved channels and model support, while the fictional build refuses both` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1407; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::pending laboratory UI preserves the draft, refreshes actual admitted analysis and requires explicit cancellation without inventing chemistry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1041; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Checklist evaluating missing approved optical/assay configuration needs exact blocker plus permitted preview/sample/skip and no-completed-substitute assertions; direct availability component is narrower than checklist action.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 35ee42a41c5708df4ff5a74365d8dd3b53cc0d2a4a5b8551bf2b561f5bcea806. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-002-01 — PASS

Profile changes during a check — - **GIVEN** a newly created check with a frozen profile version, before any acquisition - **WHEN** the user edits their profile elsewhere - **THEN** the active check SHALL retain its original snapshot, and a later check SHALL use the new version; the older record SHALL not change silently.

Current proof: Domain copies profile and target at Start, controller checks frozen engineering snapshot after later edit. Real measurement-mode software context P1=80kg/versionA before capture remains after P2=82kg/versionB, optional software interrupted ledger; new linked check usesP2/no carriedattempts, original staysP1.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::check freezes original profile timestamp and recomputes elapsed use at its start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 152; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::ordinary measurement P1 stays frozen after P2 profile update ${ledgerTransition ? "across a software-only interrupted first attempt" : "while the draft has no captures"}` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 628; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: No physical capture/another-device rendered version/native encrypted restart; these additions passed existing implementation and do not establish a profile behavior defect.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c18030c70b02600ba2d0cf88b26c585c7556ddf4160aa3851183be0d507dbfee. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-002-02 — PARTIAL

Local capture permission without upload consent — - **GIVEN** a granted camera or Bluetooth permission but no research upload authorization - **WHEN** the user completes an allowed local action - **THEN** the app SHALL keep it within the permitted local scope and SHALL not enqueue participant data for a study merely because OS permission was granted.

Current proof: Owned signed capture retains projection locally and save does not queue until explicit queueCheck; permission receipt never itself grants study consent.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Local camera/Bluetooth granted but no upload authorization context must complete a permitted local action with explicit no study queue. Existing approved capture fixture already has study consent, so it cannot prove no-consent branch.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 358c5deaa420677c30f6943d6a0b518636818a1dc1624b04c7474bfa0fc19e44. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-002-03 — PARTIAL

Offline clock rollback cannot grant capture — - **GIVEN** cached formerly available capabilities and no network - **WHEN** the wall clock is set backward or the phone reboots - **THEN** qualified Start capture SHALL remain blocked pending a fresh online acknowledgment; permitted local uncalibrated practice SHALL remain available.

Current proof: Fresh online instruction/grant/start sequence precedes hardware, and revoked/stale/reader-substituted state cannot invoke hardware.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::revoked consent, stale approval and reader substitution cannot invoke hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1560; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Cached formerlyavailable capabilities plus offline backward wall clock/reboot must remain blocked while local practice stays available; no exact combined stale-cache/clock/reboot test located. Physical reboot and native practice remain OS prerequisites.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1e79937b281bc185347e9baab1663825d28933edb05549d6877ab8ce4ebd6cf1. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-003-01 — PARTIAL

Invalid saliva collection retried — - **GIVEN** a sample marked invalid for inadequate volume - **WHEN** the user selects Replace sample and follows the allowed protocol - **THEN** a new sample attempt SHALL be created, the first SHALL remain in the audit history, and only the accepted sample SHALL supply that check's analyte records.

Current proof: Actual API inadequate-specimen invalid collection preserved byte-for-byte; linked retry has new sample/receipt, supersedes first attempt and first null volume remains.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Accepted replacement sample alone supplying this check analyte projection is not explicitly asserted by this retry test; collection receipts with no analysis do not prove selected analyte source.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 09fb8403ffa4008bed20d829e1c53fa058a326d9a0aa01b3c8342c5fc99ac725. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-003-02 — PARTIAL

User requests repeated valid game — - **GIVEN** one completed valid task in the current check - **WHEN** the user reopens the reaction step - **THEN** the app SHALL show the saved completion and review action, not a rerun action that can replace the accepted task with a faster result.

Current proof: Domain and cardiac same-modality retake guards reject preferred-reading replacement; native terminal persistence deduplicates same run.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::a valid component cannot be retaken for a preferred reading` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 256; 1 current observation(s).
- `apps/mobile/tests/lifecycle.test.ts::native callback and cancellation receipt share one durable terminal write while persistence is delayed` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 110; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- A completed valid native task reopened in UI must show saved completion/review and no rerun action; current domain retake test uses cardiac, not reaction task. Need task-specific same-check retake assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0cad36f04b541a91e4ad37425562d780bd741bca92d72d5b61f52f28845d5038. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-003-03 — PARTIAL

Finalized invalid check requires a fresh assessment — - **GIVEN** an invalid check already saved locally with a completed saliva or cardiac observation - **WHEN** the user selects Start replacement check - **THEN** the app SHALL create new session/target identities and explicit supersedes_session_id, keep the original immutable, and SHALL not carry any physical acquisition into the replacement.

Current proof: Replacement helper keeps original digest, creates distinct target/sample and bidirectional links; controller new guest replacement has zero attempts; browser invalid synthetic ECG replacement navigates original/new.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/replacements.test.ts::local original and replacement links are bidirectional without changing either snapshot` — file SHA `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233`, line 47; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 142; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Actual finalized invalid check with completed physical saliva/cardiac observation needs explicit original-hash unchanged and no physical evidence carried into replacement. Existing guest fixtures prove logical replacement, not actual acquisition noncarry.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8cc88f8397ec05b3b7a0ea088640376af6a2778440aa2bb30808f9ff41b96849. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-004-01 — PARTIAL

Device step skipped in a permitted measurement-only workflow — - **GIVEN** no actual cardiac capture and a mode that permits a missing cardiac component - **WHEN** the user advances to Review - **THEN** cardiac data SHALL be marked not_collected with null timing/features and the stated reason; the app SHALL not copy an earlier pulse value or substitute zero.

Current proof: Domain creation initializes missing cardiac not_collected with null features/timing; no earlier value copied by source.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/cardiac-selection.test.ts::ECG followed by PPG retains the same choice semantics and cannot relabel ECG` — file SHA `f4dd04b4e81fd3770810da46fd0c22ecb130c524cbb1da4a091621c6388a0bb7`, line 64; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Direct review/save with no cardiac capture must assert all null timing/features, reason and no reused prior pulse/zero. Current cardiac-selection tests skip alternative ECG after validPPG, a different context.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b0a4db6bc58ddbbd9e4ae1b7f9e999d59cb219e030cfca0fe4ce8d1d08e39bc7. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-004-02 — PARTIAL

Laboratory analysis returns the next day — - **GIVEN** saliva collected yesterday with separately timed physiological/task measurements - **WHEN** a permitted laboratory result is linked today - **THEN** Review and history SHALL retain yesterday's collection and target times, identify the later analysis time, and SHALL not call the result a current real-time assessment.

Current proof: Laboratory controller retains same specimenID across pending/import; report parser preserves original target, formatter shows collection/analysis separately.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 870; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Next-day lab arrival with separately timed physiology/task must visibly retain original collection/target in Review/history and avoid current real-time claim. Existing imported fixture/parser contexts do not assert all UI/time clauses.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c40ae795fe6d387dcda9ac6e7237cdf4b21766a6cebd7c28345e132bf7707796. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-005-01 — BLOCKED

App terminated during reaction task — - **GIVEN** a persisted started task attempt without a completion event - **WHEN** the app restarts - **THEN** it SHALL mark that attempt interrupted, preserve already completed independent components, and require a new linked task attempt before representing task completion.

Current proof: Pure process-interruption reducer marks started task invalid/null aggregates, linked retry supersedes original; controlled store reopen retains serialized state.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual process death mid-task then reopen with independent prior components retained and new linked task requirement is unexecuted; reducer does not simulate native restart persistence.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 6cea051628b9f0d301531b712f38d2baee278183209b043ae193c35ac4e63b44. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-005-02 — PARTIAL

Cancel command cannot reach the peripheral — - **GIVEN** an active capture and a lost BLE connection - **WHEN** the user selects Cancel check - **THEN** the UI SHALL terminate locally, record cancellation, and reject subsequent late events for the canceled attempt regardless of whether the peripheral received the command.

Current proof: Controller requests local native cancellation before delayed radio stop; stale terminal run ignored and unmounted arm invalidates.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 847; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 889; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Lost BLE Cancel check route must terminate UI, retain cancellation and reject all late peripheral events even when cancel command never arrives. Current test radio Promise later resolves and terminal fixture was already valid, not unreachable peripheral canceled attempt.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 01815ed97d1fcd9ba16b63c3113125d8f52920789161841b7d690c91ad449213. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-005-03 — PARTIAL

Keep draft cannot resume an ended task — - **GIVEN** an active scored task whose parent navigator keeps tabs mounted - **WHEN** the user selects another tab and then Keep draft in the resulting sheet - **THEN** the native stimulus SHALL have already stopped and the attempt SHALL remain invalid; returning SHALL expose a permitted new attempt or replacement action rather than resuming.

Current proof: RunStopGate coalesces route/background stop before persistence; unmounted task invalidation keeps INTERRUPTED.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::concurrent route/background stops issue native cancel immediately and wait for terminal persistence` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 148; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 889; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Mounted-tab active-scored-task→other tab→Keep draft must assert native stimulus already stopped, attempt invalid and returning offers only new attempt/replacement, never resume. Browser retained saliva draft has no active native task.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f5f8d288d55deaca6b7cc6c8bd5157d6240343e51d2c26617e2a2e3ff4d8610c. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-006-01 — PARTIAL

Network drops after finalization submission — - **GIVEN** a frozen local snapshot and an unknown server acknowledgment outcome - **WHEN** the user requests reconciliation, or previously enabled automatic retry permits it, after connectivity returns - **THEN** the app SHALL retry or query with the same identifiers and digest, reconcile one logical finalization, and SHALL not create another sample, task, or check.

Current proof: Lost accepted registration request retries exact key/body/gen and ends synced; original frozen evidence stays.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::a lost accepted response replays the same identity and unchanged bytes` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 290; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Accepted finalization response lost specifically, then explicit/manual or permitted auto reconciliation must assert one logical finalization and no new sample/task/checkIDs. Registration-loss fixture is narrower and does not count finalize acceptance.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c0380ab887d63999bfe43fc0395ed3e1debd30769479f77b9c20013d38750e6c. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-006-02 — PASS

Draft version conflicts with server — - **GIVEN** a stale local snapshot version - **WHEN** the server returns a version conflict - **THEN** the app SHALL preserve both the local pending content and authoritative version metadata, show Conflict needs review, and SHALL not overwrite a finalized remote record.

Current proof: 409/412 queue becomes conflict, stops retry and frozen hash unchanged. Actual ApiClient error parsing and SyncEngine guardedreadback preserves local evidence/key, holds conflict, rejects changed scope/foreign response; actual saved JSX presents verified comparison and linked correction.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::conflict and stale generation stop automatic replay without changing frozen evidence` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 305; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::snapshot 412 and frozen 409 read back one authoritative revision without changing or replaying pending evidence` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 107; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::conflict readback cannot publish after epoch, generation, owner or cancellation changes` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 155; 1 current observation(s).
- `apps/mobile/tests/sync-conflict.test.ts::unavailable or foreign authoritative readback stays a preserved conflict and never substitutes local data` — file SHA `d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f`, line 200; 1 current observation(s).
- `apps/mobile/tests/result-ui.test.ts::actual saved conflict offers a verified server comparison and linked correction while keeping upload stopped` — file SHA `217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60`, line 351; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Controlled HTTP/component transport; complete live dependencies/current native storage not established.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 19bd7e0972e0ce843c58816df4917edb45c5ceef8bd214004b0ddedac6106ae7. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-006-03 — PARTIAL

Save and sign in cannot upload guest evidence — - **GIVEN** a guest demo containing fictional chemistry and actual uncalibrated native taps - **WHEN** the user saves the check, reconnects, and signs in - **THEN** the check SHALL remain in its guest namespace with exact mixed provenance and no queue entry or account migration.

Current proof: Guest save queue empty and guest upload refused; native measurements retain prototype provenance in separately tested native flow.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::guest check cannot upload and never acquires an account owner by sign-in` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 246; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Guest demo with actual native taps then reconnect/sign-in must retain exact mixed provenance/namespace/no queue/no migration in one journey; current browser lacks native module and unitguest uses fictional task absent.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 337ea8a876c8238fc4b49a8c3be5b310d6101eeeb338d5292ff5d35cdf74db00. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-007-01 — PASS

Synthetic check completes successfully — - **GIVEN** a valid synthetic snapshot - **WHEN** the measurement-only result arrives or is generated by the permitted local demonstration - **THEN** the app SHALL show completion of the demonstration and its measurement details, with no intoxication percentage or physiological normality claim.

Current proof: Actual guest synthetic browser fills measurement steps, saves Measurements saved and exports exact guest_demo measurement_only/null probability. Source result uses measurement details rather than physiological normality classification; no scientific validity is claimed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/domain.test.ts::save freezes all evidence and never queues upload` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 233; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA e001234a0a2b5e58aff30fc3ca5ef7cf19d4fe0cd025f877b10c065e2e265227. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-007-02 — PARTIAL

Forged result includes a probability — - **GIVEN** a synthetic or unauthorized check - **WHEN** a malformed cache or response contains an intoxication probability - **THEN** the client SHALL reject that field/result, surface a data-integrity error, and SHALL not display it as a research estimate.

Current proof: Legacy0.1research-shaped result and guest/synthetic proof mutation refuse verification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::every research_estimate is rejected even when its shape could be schema-valid` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 323; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual malformed cache/response opened from synthetic current UI must surface data-integrity error and no estimate; current parser rejection asserts throw, not rendered safe error transition.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 01aa0e6dfdb494cdd88f9ff786b212eb504c19080f169e307376eda5b593160e. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-007-03 — PASS

Signed future result is unsupported in this release — - **GIVEN** an otherwise owner-matching signed response with research_estimate and a probability - **WHEN** the result is opened from live navigation or history - **THEN** the client SHALL reject it as UNSUPPORTED_RESEARCH_RESULT and SHALL not render the probability or relabel the result successful.

Current proof: Accepted shared-contractsection1 explicit supersession and matching authorized-model-execution AND-CHECK007 scope this historical row to legacy/unadmitted estimates.0.1research shape and forged/guest/missing-authority1.1 refuse; no probability promoted. Fully admitted1.1support is separately tested under MODEL requirements, not a defect.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::every research_estimate is rejected even when its shape could be schema-valid` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 323; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 245; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA bfd961df0ce38c5a59f3d2dc41db6c4a5d4aca8b27641ec30bcb1861870c39db. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-008-01 — BLOCKED

Screen-reader navigation outside capture — - **GIVEN** an enabled Android or iOS screen reader - **WHEN** the user traverses the checklist and Review - **THEN** step names, states, reasons, and actions SHALL be announced in a meaningful order without depending on badge color.

Current proof: Browser role/step labels and control reachability exercised at two viewports. Current DOM focus restoration, modal semantics, contrast and reduced-motion assertions are executed; no actual TalkBack/VoiceOver/native OS claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::navigation and theme components expose selected state at both viewport sizes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 746; 4 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual Android/iOS screen-reader checklist/Review spoken names/states/reasons/actions meaningful order without color dependency unexecuted. Current DOM focus/reduced-motion software repairs have current named observations; actual OS scenario remains unexecuted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 5770dc0bd1510b9575ac6a6d173e8cf6299a53c30532ab56cd867f4ddcb1b19a. Actual current source and raw evidence supply this disposition.

## OTGD-026-AND-CHECK-008-02 — BLOCKED

Cross-platform offline replay — - **GIVEN** equivalent fictional engineering-account records saved offline on each platform - **WHEN** each signed-in user explicitly selects Upload check to the same permitted API environment - **THEN** both SHALL preserve quantities, qualifiers, provenance, context/evidence hashes, and terminal states with platform metadata retained; guest demo records SHALL remain local and ineligible for this upload.

Current proof: Shared exact canonical hashing/DTO and explicit upload fixture preserve evidence; guest refuses cloud upload.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::explicit upload registers evidence then snapshot then finalizes and verifies result` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 253; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::guest check cannot upload and never acquires an account owner by sign-in` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 246; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Equivalent native Android+iOS offline engineering-account saves/uploads to same actual API with preserved quantities/qualifiers/provenance/platform metadata and terminal states are not executed. CI pure native modules do not constitute full installed cross-platform offline replay.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 25e51cff81d7fc072ddfdc677722e4e6603548e4acd36ceed4be16f5e7502cb3. Actual current source and raw evidence supply this disposition.
