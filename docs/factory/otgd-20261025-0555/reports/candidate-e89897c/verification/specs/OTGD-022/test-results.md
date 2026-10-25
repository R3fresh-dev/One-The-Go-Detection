# OTGD-022 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-data-export/spec.md`; SHA256 `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30`.

14 cases, 7 requirements: NOT_RUN 4, PARTIAL 4, PASS 6. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-022-AND-EXP-001-01 — PARTIAL

Local single-check export — - **GIVEN** History selects one check while unrelated records also exist - **WHEN** the customer confirms This device for that exact selection - **THEN** only the selected check, its frozen profile/context, attempts, alcohol, and linked results are exported locally, with no cloud mutation or unrelated profile revision.

Current proof: Multi-check unit archive excludes second check and unrelated current profile; browser explicit confirmation creates one-check local archive with context/manifest and bounded hash-verified entries, no cloud service succeeds because API routes aborted. ExistingHRcache exactdigest/view/epoch/account/gen ephemeralread, late/offline/denial/mismatch refusal; separateexportadmission atassembly/finalrelease, actualResultDOMwithprepopulatedHR.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::single-check export preserves exact scope and excludes unrelated current profile` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 407; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/hr-read-admission.test.ts::HR numeric display requires a matched owned200 per view and never persists admission or changes saved evidence` — file SHA `83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8`, line 54; 1 current observation(s).
- `apps/mobile/tests/hr-read-admission.test.ts::late HR200 cannot revive a left view, offline transition, retired generation, changed account or background workspace` — file SHA `83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8`, line 238; 1 current observation(s).
- `apps/mobile/tests/hr-read-admission.test.ts::local HR export independently reads before assembly and final release; refusal releases no archive` — file SHA `83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8`, line 341; 1 current observation(s).
- `apps/mobile/e2e/components.spec.ts::actual HR screen requires a fresh admitted result on open and after evidence navigation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 236; 4 current observation(s).
- `apps/mobile/e2e/components.spec.ts::actual HR manual refresh and late read after leaving cannot revive cached numeric research` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 279; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- History-selected single-check local export with unrelated retained records must preserve every linked frozen profile/context/attempt/alcohol/result and cause zero cloud mutation. Direct generator scoping and the visible one-record journey are proved separately; complete selected-with-unrelated-records transport/association conjunction is not retained as direct evidence.

Prerequisite/evidence type: software_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: The original prepopulatedHR scope is supplemented by FINAL_MOUNTED_HR; it did not prove that transition by itself. NativeOSsharing/realserverretirement not componentproof.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2344482ff9000ea5202c38b46279f737ba54fea712faa5fdc69256f9e85475e0. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-001-02 — NOT_RUN

Confirmation is canceled — - **GIVEN** the export summary sheet - **WHEN** the customer cancels - **THEN** no job/file/share action is created.

Current proof: Related executed cancellation test concerns automatic retry and local deletion, not export confirmation.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/components.spec.ts::confirmation components never enable retry or erase unsynced records on cancellation` — file SHA `a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1`, line 656; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- “customer cancels [export summary] ... no job/file/share action is created”: no observed export-summary cancellation with zero export job/file/share effects.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 5ba52e1038397c51f39a185c3c0d5dbbda61c40ccb607556248038cee86200c2. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-002-01 — PASS

Own synced records — - **GIVEN** a signed-in owner selecting their records - **WHEN** the export completes - **THEN** the archive contains only the authorized selected records.

Current proof: Signed-in owner requests exact single selection; worker completes, ZIP exact check/profile/manifest set and four attempts; expanded companion export excludes foreign-owner, old-generation and unrelated-parent records by exact expected digest set. Foreign download path denied404. Storage is test double; this is owned-selection software proof. Genuine typed signed HR and nonHR result GET200 ->export202 ->real workerZIP/download200 with exact unchanged numeric result and every linked evidencefield/hash; emptyhead only without either companion; administrative/legacy/malformed controls retained, numeric and abstained revocation at build/commit/download.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_export_scope_and_authenticated_download` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 276; 5 current observation(s).
- `services/api/tests/test_participant_privacy_inventory.py::test_export_preserves_all_owned_preparation_and_collection_records` — file SHA `9b83b8ba8b871175413cf770b749beeba2924fe1496fd055a42e232faff4fd8e`, line 21; 5 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_current_numeric_research_export_preserves_exact_result_and_linked_evidence` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 129; 10 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_numeric_export_does_not_grant_administrative_revision_eligibility` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 183; 5 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_numeric_export_never_ignores_existing_ineligible_companions` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 197; 10 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_legacy_shaped_numeric_result_remains_unexportable` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 210; 5 current observation(s).
- `services/api/tests/test_current_result_readback.py::test_hr_export_rechecks_current_authority_at_each_boundary` — file SHA `8df4b2d22a0eb0b0167ec244dc5c46d93e28608682038074f3a6da4112177023`, line 251; 30 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: SQLite/model/archive objecttransport doubles remain explicit; liveS3/SQS and actualscientific qualification not inferred.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 1a91786e6d75cecb9d05b4f334ba1585a0b5cd5c2258a4f6744eeabce6d107c5. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-002-02 — NOT_RUN

Another user's session is injected — - **GIVEN** an export selection containing a foreign UUID - **WHEN** the request is validated - **THEN** it is rejected without including or disclosing the foreign record.

Current proof: Related tests deny foreign downloads and raw artifact IDs; they do not submit foreign session UUID in structured export selection.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_export_scope_and_authenticated_download` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 276; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_scope_revision_hash_owner_and_confirmation_clock_rechecked` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 245; 35 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “export selection containing foreign UUID ... rejected without including or disclosing foreign record”: no executed structured selection-injection request with foreign owned session and safe denial asserted.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 1b87f84558bcecb63d339b66cd52619397787ec1fc8406eec2edac92889d6dcd. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-003-01 — PASS

Censored saliva result — - **GIVEN** a below_loq measurement - **WHEN** exported - **THEN** value remains null and the qualifier/limit/original report remain available.

Current proof: laboratory fixture derives examples/synthetic_session.json containing below_loq/null saliva plus original BLQ report/limits. Executed HTTP worker export asserts exported check.snapshot exactly equals laboratory.snapshot; backend archive inspector verifies immutable source evidence. Exact snapshot equality preserves null, qualifier, limits and original report together; alcohol-only censor test is not adopted as saliva proof.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_report_revisions.py::test_export_freezes_report_head_and_uses_separate_bounded_hash_indexed_files` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1197; 5 current observation(s).
- `apps/mobile/tests/export-scope.test.ts::actual backend archive verifies original embedded evidence and both separate report revision companions` — file SHA `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46`, line 103; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a15bef1e155bfd04af0cc1ed6d6476e2ab03563f97ed88e38e81e3edc996f4c8. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-003-02 — PASS

Historical reanalysis — - **GIVEN** multiple linked results for one session - **WHEN** selected for export - **THEN** their immutable IDs, versions, and replacement relationship are preserved.

Current proof: Fixture has linked correction+reanalysis; local archive contains two separate revision companions and inspector validates chain. Parsed results explicitly preserve result_id/replaces_result_id relationships, original digest unchanged; archive index verifies parent, exact descriptor/result/full-file hashes and order; source copies each immutable companion without rewriting schema/version fields.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-scope.test.ts::cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache` — file SHA `2e0a94481f2c23702cccd7c4e6daa913b0f87e7b6a392e66afd4735d06fc7c46`, line 112; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::separate report archive index validates file path, parent, descriptor/result/full-file hashes and complete sequence` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 206; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 5bd7c2262328b180ed09cf36c1d57b307f92a4190f98ce0f5c303848314765a7. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-004-01 — PASS

Default export — - **GIVEN** an ordinary export request - **WHEN** the job is assembled - **THEN** raw eye/ECG files are excluded and the manifest records the exclusion.

Current proof: Ordinary metadata export worker ZIP exact fixed entry set has no raw binaries; local actual browser archive manifest.raw_artifacts_included=false and all members hash/size verified. Source manifest exclusion fields retain raw exclusions by default; no raw authority inherited.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `services/api/tests/test_api.py::test_export_scope_and_authenticated_download` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 276; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f6558706c97d2403d9e9337e820efa7868aaa8ca2aa85ef0978af1e1419eb623. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-004-02 — PASS

Raw consent is revoked during processing — - **GIVEN** raw inclusion was initially allowed - **WHEN** permission is revoked before delivery - **THEN** the gateway blocks a subsequently initiated download and reports the changed scope or failed job; it makes no promise to recall bytes already authorized/delivered.

Current proof: Initially permitted completed raw export, permission revoked before new delivery; new gateway download403 and current raw scopes artifact list emptied; after cleanup owned terminal receipt revoked with raw/download/hash/size absent and download still denied. No recall of previously delivered bytes claimed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_http_accepted_raw_replay_and_new_download_are_denied_after_revocation` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 470; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_http_revoked_cleanup_has_minimal_terminal_receipt` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 535; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA f82c8bb9abad4387203cadb94923cb4529dd173ac1a9891e5f3b03198b5915df. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-005-01 — PARTIAL

Expired export is reopened — - **GIVEN** an export past expires_at - **WHEN** the customer opens it - **THEN** no new valid ticket is issued and a new export action is offered.

Current proof: Expired API export gives410; raw expired status has no raw_export/download_path, so no new valid gateway metadata disclosed.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_export_scope_and_authenticated_download` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 276; 5 current observation(s).
- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “new export action is offered” when reopening expired customer job: no UI/controller expired-job test asserts new export action; manage.tsx renders expired badge and general privacy export controls but job-specific offer is not executed. Do not infer a behavior defect from missing assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c5ac3f77b06b2a7bc618eed3e5d07c06f7c91a26fee8f2412d4dc0fb452f69a1. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-005-02 — NOT_RUN

Share sheet is canceled — - **GIVEN** a downloaded temporary export - **WHEN** the share sheet returns without sharing - **THEN** the app schedules immediate cleanup and does not claim it sent the file anywhere.

Current proof: Related integrity test rejects tampered archive only; native sharing.native.ts finally deletes temporary file after shareAsync returns (source inspected).

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::export rejects file tampering and traversal or hidden files before sharing` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 435; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “share sheet returns without sharing ... immediate cleanup ... does not claim it sent file”: no executed cancel-return native-sharing/temporary-file test. OS sheet and app-private deletion behavior not established by browser downloads.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 4baf467fda29b42ce0fed2b2f71e3e8d7fa406abaa83d5b1bdad5de6c3dbf5c6. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-006-01 — PASS

Export request response is lost — - **GIVEN** a created cloud job - **WHEN** the same request is retried - **THEN** the same job ID is returned.

Current proof: Controller loses accepted response then retries exact original body and Idempotency-Key; real API identical body/key returns same accepted job ID while pending. Metadata-only API also replays same job after expiry. Software idempotency proof; no live cloud transport claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-export.test.ts::cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 225; 1 current observation(s).
- `services/api/tests/test_raw_export.py::test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 418; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c24136096f5f8869f1f67018db9364f89fc5fff438d07bd0e4af42f5cf5b3fb2. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-006-02 — PARTIAL

Artifact verification fails — - **GIVEN** a selected permitted artifact whose bytes fail the stored hash - **WHEN** the worker assembles the export - **THEN** the job fails with a safe reason and no complete-download state is exposed.

Current proof: Source read rejects incorrect returned version/length/type/hash or read-limit excess, closes stream and returns no partial files.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_raw_export.py::test_version_length_type_hash_and_read_limit_failure_never_returns_partial_file` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 283; 30 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “job fails with safe reason and no complete-download state is exposed”: test calls read_sources directly rather than worker.run_job and does not assert failed job receipt/failure_code/download denial after a selected artifact hash mismatch.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 52623106b9dc36e12ced0da5afa4e13ea64a0d8763a66e3c5928af7eb1920ff9. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-007-01 — NOT_RUN

Profile text resembles a path — - **GIVEN** text containing ../ or absolute-path characters in user data - **WHEN** an export is generated - **THEN** it remains JSON content and cannot control an archive entry name.

Current proof: Traversal ZIP entry is rejected and empty metadata export works. Generator source uses fixed prefixes and generated IDs.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::export rejects file tampering and traversal or hidden files before sharing` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 435; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::empty all-data export contains profile metadata and no invented check` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 427; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- “text containing ../ or absolute-path characters in user data ... remains JSON content ... cannot control entry name”: existing path-negative test supplies a malicious ZIP entry, not pathlike text inside valid user data passed through export generation.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA baf5d017b09cb3067a658bdeb8086c079c1b627f99f916990daa7d37d50c8c0e. Actual current source and raw evidence supply this disposition.

## OTGD-022-AND-EXP-007-02 — PARTIAL

Export exceeds its configured bound — - **GIVEN** selected data larger than the supported single-export limit - **WHEN** the job validates size - **THEN** it reports an explicit size failure and never silently omits records or invents an unimplemented partitioning workflow.

Current proof: Total-byte helper includes manifest and raises EXPORT_TOO_LARGE at 50MiB+manifest; oversized structured record/profile jobs fail with zero export objects; no truncation/partition code adopted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_report_revisions.py::test_archive_budget_includes_manifest_bytes_without_a_manifest_record_cap` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1252; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_combined_check_record_over_512k_refuses_whole_export_before_object_write` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1282; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_profile_history_file_over_512k_refuses_whole_export` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1327; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- “reports explicit size failure”: worker tests assert run_job failed and absence of written archive, but do not assert exposed failed-job failure_code/actionable customer message identifies size overflow instead of generic failure.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 979a05bd61b376df37268f0eb477eb9c03255ebf17e404e932782615a0061ef5. Actual current source and raw evidence supply this disposition.

