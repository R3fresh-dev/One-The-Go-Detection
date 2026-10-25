# OTGD-028: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-history/spec.md`; SHA-256 `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 7 individually identified requirements and 17 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Independent source assertion audits for this dossier: Rendered alcohol state/copy assertion audit; Authenticated ordinary-web live test source audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 17 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 3, "NOT_RUN": 1, "PARTIAL": 12, "PASS": 1}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-028-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-028 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-history/spec.md`; SHA256 `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2`.

17 cases, 7 requirements: BLOCKED 3, NOT_RUN 1, PARTIAL 11, PASS 2. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-028-AND-HIST-001-01 — PARTIAL

hist-demo-isolation — - **GIVEN** both demo and account checks exist on the device - **WHEN** account History opens - **THEN** only authorized account checks are listed and demo rows require an explicit switch.

Current proof: Workspace scope rejects delayed other-account responses; guest check never migrates/account-empty checks asserted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/workspace-scope.test.ts::delayed history, job or study responses cannot publish into another account` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 31; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::guest check cannot upload and never acquires an account owner by sign-in` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 246; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual coexisting demo+account history list with explicit switch, exact authorized row IDs and no automatic guest inclusion is not asserted as a single history rendering context.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 80a0f0cd1d387cb374e6f5957b898a359bcd35f20858f8c6b239d0107d7db2ca. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-001-02 — PARTIAL

hist-cross-account-id — - **GIVEN** an account receives a deep link to another account's session ID - **WHEN** detail is requested - **THEN** no snapshot, profile, existence-revealing title, or measurement is disclosed.

Current proof: Actual API foreign session detail returns404 and foreign list empty; delayed owner response cannot publish into other namespace.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_end_to_end_measurement_only_and_owner_isolation` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 197; 5 current observation(s).
- `apps/mobile/tests/workspace-scope.test.ts::delayed history, job or study responses cannot publish into another account` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 31; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Deep-link UI must not show foreign snapshot/profile/existence title/measurements; reviewed HTTP test only asserts404 status, not safe body/title and rendered absence.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ecdbcf547f450ff64ef11555e9c9fb7303fce5a8d32ad328acfcde8775a39423. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-002-01 — PASS

hist-new-record-between-pages — - **GIVEN** page one has loaded and a new check is finalized - **WHEN** page two is requested with the original cursor - **THEN** existing rows are neither duplicated nor skipped and the new check appears after refresh.

Current proof: Session-list source uses created/id keyset boundaries and owner/gen SQL filtering. Actual authenticated listing cursor bindsowner/gen/environment/sort/MAC/ownedstableboundary; concurrentinsert/tiedpages no duplicate/skip and refreshnewrow assertions.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::mixed local and synced history uses acquisition time and stable identity ties` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 115; 1 current observation(s).
- `services/api/tests/test_history_cursors.py::test_history_cursor_cannot_be_replayed_for_a_foreign_owner` — file SHA `6c309744fdcd25f8d9b28ac4981736f52232700e3047e0ddb5dda45147fbf554`, line 50; 5 current observation(s).
- `services/api/tests/test_history_cursors.py::test_retired_generation_cursor_is_not_an_admitted_current_boundary` — file SHA `6c309744fdcd25f8d9b28ac4981736f52232700e3047e0ddb5dda45147fbf554`, line 63; 5 current observation(s).
- `services/api/tests/test_history_cursors.py::test_forged_position_scope_or_authenticator_is_refused` — file SHA `6c309744fdcd25f8d9b28ac4981736f52232700e3047e0ddb5dda45147fbf554`, line 90; 50 current observation(s).
- `services/api/tests/test_history_cursors.py::test_new_finalized_check_does_not_shift_existing_tied_pages_and_appears_on_refresh` — file SHA `6c309744fdcd25f8d9b28ac4981736f52232700e3047e0ddb5dda45147fbf554`, line 209; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current unitSQLite versus currentPG/live integration remains explicit; no crossowner disclosure claimed from original gap.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 544dd68e5339044f7979ee1a82bde35b96052aaaa22952d78c3ae044c82a93b0. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-002-02 — PARTIAL

hist-local-server-same-check — - **GIVEN** a local pending row is later returned by the server with the same UUID - **WHEN** reconciliation completes - **THEN** one row remains with updated sync status and unchanged source identity.

Current proof: Explicit sync keeps original sessionID and marks record synced; history source merges IDs.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::explicit upload registers evidence then snapshot then finalizes and verifies result` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 253; 1 current observation(s).
- `apps/mobile/tests/support-history.test.ts::pending sync means explicitly requested delivery, not local saves or retired records` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 96; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- No rendered local pending UUID returned by server test asserts one row, updated sync state and unchanged source identity. Generic pending predicate does not count merge results.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 71042baf23d9aafa720f9b2d0088e83e301c791718df17db0fd380eb233ad0d4. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-003-01 — PARTIAL

hist-below-loq — - **GIVEN** THC-COOH has qualifier below_loq with no quantified value - **WHEN** detail is opened - **THEN** it reads “Below quantification limit” with the reported limit when available, and no 0 ng/mL or inferred detection claim appears.

Current proof: Formatter preserves null quantified value, displays exact supplied LOQ and distinct censored wording with unchanged input bytes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::below LOQ displays the supplied bound without creating a concentration or rounding it to zero` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 23; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Exact THC_COOH history detail card is not asserted; current pure formatter fixture is OH11_THC. No original test binds rendered card and absence of inferred detection claim for this analyte.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2c853a690f76389a6743c553ba00c10323249e473a8be61b6ae8632129c7e023. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-003-02 — PARTIAL

hist-delayed-laboratory-result — - **GIVEN** a sample collected Monday was analyzed Wednesday - **WHEN** its result is viewed Thursday - **THEN** all relevant dates are distinct and the laboratory result is not described as a Thursday physiological assessment.

Current proof: Display formatter retains collected/measured UTC separately; backend delayed reanalysis retains original target.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Monday collection/Wednesday analysis/Thursday viewed history must display distinct dates and no Thursday physiological-assessment claim; reviewed one-hour formatter and parser contexts do not assert this route/date conjunction.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9eb886ebc540baddaa3afa45a99a44e52a9e2c5a91254c5ee73921f486a9a836. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-003-03 — PASS

hist-linked-research-estimate-is-still-unsupported — - **GIVEN** an authenticated account receives a schema-valid research_estimate with matching session and digest - **WHEN** History renders its detail - **THEN** the app shows the unsupported-result state without displaying probability, classification, or a research-estimate card.

Current proof: Shared-contractsection1 and later matching MODIFIED results requirement govern this historical row: legacy/unadmitted research estimate is refused, while complete independently admitted1.1 is separately supported. Client mutation matrix and legacy schema test reject proof-less/relabeled0.1 and prevent probability display admission. No blanket rejection of approved1.1 is inferred.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 245; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b8cfa675655fef1bc2f817a64afaa0b715af5beedd7861e0065e42d6962dbb87. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-004-01 — PARTIAL

hist-profile-edited-later — - **GIVEN** a historical check contains profile revision A - **WHEN** current profile revision B is saved - **THEN** historical detail continues to display A's values and acquisition context.

Current proof: Snapshot/context clone is unchanged after later profile save in controller; archive preserves embedded original context.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).
- `apps/mobile/tests/export-scope.test.ts::cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache` — file SHA `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46`, line 112; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual historical measurement with nonnull profileA shown after profileB saved is not asserted; engineering fixture overwrites profile with unknowns, and archive parsing is not rendered history values.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f09e385c70c9c3120c520584b1fee69d830cab1e8c85dc945e490dff62b06e36. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-004-02 — PARTIAL

hist-correction-linked — - **GIVEN** a reviewed correction supersedes a finalized record - **WHEN** either version is opened - **THEN** the original remains readable and a labeled link identifies the other version without overwriting it.

Current proof: Report companion chain and replacement helper retain original digest and explicit predecessor/successor IDs; browser replacement links navigate both ways.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 142; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- Reviewed correction/reanalysis UI needs original/current version labeled links in either opened version; replacement-check UI and correction parser alone do not establish report-version links/rendering.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 95182680cb77a97663cf79f0470f4484e6c3dac96110641c063971d3d33b2749. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-005-01 — PARTIAL

hist-offline-cached-detail — - **GIVEN** an encrypted cached snapshot and no network - **WHEN** its row is selected after local unlock - **THEN** the stored snapshot is displayed with its cached state and no remote result is invented.

Current proof: Controlled native store reopen returns exact workspace; ordinary local browser detail remains local and no remote result invented.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/native-storage.test.ts::concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 128; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Installed encrypted account snapshot selection after biometric unlock offline and cached-state label are unexecuted; mock SQLCipher module is not actual native database/keystore evidence.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 92cd72bac6276b9d7bdcf26dd6e374b0dac82f24c629761ad202cefef99148d6. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-005-02 — NOT_RUN

hist-offline-uncached-detail — - **GIVEN** only a list summary is cached - **WHEN** the user opens detail offline - **THEN** the app explains unavailability and does not fill the screen from unrelated fixtures or another check.

Current proof: Remote-draft parser refuses to present uploaded but unfinished snapshot as a readable frozen result.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/replacements.test.ts::a remote draft with an uploaded snapshot is not treated as a frozen readable result` — file SHA `5942e7dddc7b8e7c403b71d242c7168c28f64890db69543091331e89bea60233`, line 182; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Only-list-summary cached detail opened offline needs explicit unavailable UI and no unrelated fixture/check fallback; no current named exact journey located.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA b2404d3d1661ebe38007b44b83dba51d196f15d28679ad1108ac000820cfb9b6. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-005-03 — BLOCKED

hist-signed-out-device-unlock-is-insufficient — - **GIVEN** A retained encrypted history when signing out - **WHEN** the user opens the app offline and passes device unlock - **THEN** A's history stays locked until the same issuer and subject reauthenticate; other workspaces remain separate.

Current proof: Credential-clear tests remove identity; controlled workspace guards reject locked scopes.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/workspace-scope.test.ts::same-owner same-generation response succeeds; locking or backgrounding invalidates the scope` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 94; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual retained encrypted accountA cache after sign-out/offline biometric success must stay locked until sameissuer/subject reauthentication; no installed OS evidence. Biometric success cannot establish sign-in.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 5d772d2562be39487aafb9ef28639998acb4a8203cd8b70f436e1a57ca7e5120. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-006-01 — PARTIAL

hist-pending-filter — - **GIVEN** two locally queued checks and three synchronized checks - **WHEN** Pending sync is selected - **THEN** only the two queue-owned checks appear and the label states that this is this device's queue.

Current proof: pendingSync exactly classifies queued/retry/blocked/awaiting/conflict and excludes local saves/synced/quarantine; browser filter does not expand selected export.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::pending sync means explicitly requested delivery, not local saves or retired records` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 96; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Two queued+three synchronized history rows, exact two displayed and this-device queue wording are not directly asserted together.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6634ae24e02937c362c4ce941adb93b585f02ac0fb0931d5f478c299bcf21d43. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-006-02 — PARTIAL

hist-delete-race — - **GIVEN** a detail request is in flight when its deletion is accepted - **WHEN** the old response arrives - **THEN** it is discarded according to the deletion generation/tombstone and cannot repopulate History.

Current proof: Owner/generation/fence scope invalidation rejects late responses; actual deletion increments generation and client quarantine clears cached history.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::server generation retirement quarantines prior checks and a new empty workspace requires separate acknowledgment` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 806; 1 current observation(s).
- `apps/mobile/tests/workspace-scope.test.ts::a delayed export download never reaches sharing after generation change or local clear` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 51; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- A history detail HTTP response delayed across accepted deletion must be delivered then asserted absent/tombstoned; current delayed export and sign-out contexts are narrower than deletion detail.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 33728417e4041d841d68a5dec392db21e3a8dabacccaddf0b96e77d049da6225. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-006-03 — PARTIAL

hist-single-check-export-scope-survives-source-change — - **GIVEN** History starts Export this check for A while unrelated checks B and C exist - **WHEN** the user changes This device to Synced records or resumes after reauthentication - **THEN** the selected scope remains only A and related authorized evidence; B and C cannot enter the archive without a new expanded-scope summary and confirmation.

Current proof: Single-check archive inspector rejects rehashed unrelated profile/attempts; exact selection remains when browser filter hides row.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-scope.test.ts::rehashed extra profile version and unrelated current profile are rejected in a single-check archive` — file SHA `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46`, line 168; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::history selection remains exact when filters hide selected records` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 704; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- History ExportA with B/C plus source switch or reauthentication must preserve onlyA and require expanded-scope reconfirmation. Current archive validation and hidden-filter selection do not execute this source-switch/reauth context.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 69145fe0fa85679a50e00f7ee25ca763fce194d41af7771205333ddb2668b3ad. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-007-01 — BLOCKED

hist-large-text-detail — - **GIVEN** 200% font scaling and a narrow Android display - **WHEN** a saliva detail section contains all three analytes - **THEN** names, values, units, and qualifiers remain legible and reachable without clipped columns.

Current proof: Browser component viewport checks bound horizontal width; formatter gives distinct analyte names/units/qualifiers.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::navigation and theme components expose selected state at both viewport sizes` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 746; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Actual Android200%systemfont narrow history containing all3 analytes with no clipping and reachable controls is unexecuted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA f362557992d7c43f95580ee4c6e5cce1e457917f6a2be8b6ad30d09b7c08aa15. Actual current source and raw evidence supply this disposition.

## OTGD-028-AND-HIST-007-02 — BLOCKED

hist-ios-back-position — - **GIVEN** the iOS user opens a row after loading three pages - **WHEN** they navigate back - **THEN** the same selected row and list position are restored with no duplicated page fetch.

Current proof: HistoryViewMemory retains filter/selection/scroll within same epoch and isolates account epochs.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/support-history.test.ts::history detail round-trip keeps filters, selected IDs and scroll only in the current workspace epoch` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 70; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual iOS after three loaded pages→detail→Back must restore selected row/list offset without duplicate fetch. Pure memory fixture does not execute native navigation/pagination.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA a4acd332983e949ad65bc3f00e63e36cd3d669ae18b263c24fe6edbdb82b73af. Actual current source and raw evidence supply this disposition.
