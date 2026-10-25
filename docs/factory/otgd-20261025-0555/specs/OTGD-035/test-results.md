# OTGD-035: verification results

Canonical: `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md`; SHA-256 `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 7 individually identified requirements and 16 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 16 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 2, "NOT_RUN": 1, "PARTIAL": 12, "PASS": 1}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-035-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-035 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-saliva-measurement/spec.md`; SHA256 `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610`.

16 cases, 7 requirements: BLOCKED 2, NOT_RUN 1, PARTIAL 12, PASS 1. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-035-AND-SAL-001-01 — PARTIAL

Simulated sample workflow — - **GIVEN** explicit P0 mode - **WHEN** the user selects Use simulated sample - **THEN** the app SHALL create a labeled fictional sample and fictional analyte records, retain simulated source on all channels, and show the same validation/review UI used by the production adapters.

Current proof: Simulated sample/analyte typed companion projection validates and fixture provenance remains simulated.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-projection.test.ts::every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 29; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Explicit Use simulated sample UI must show fictional sample/all channels and shared production validation/review journey rather than merely validate fixture shape.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 041eb7f9aae9929ae9a30ff849d1dd4d7e825ac2a363c46a99a6b25ae3916ab5. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-001-02 — PARTIAL

Reader has no assay implementation — - **GIVEN** a connected Nano that only supplies telemetry - **WHEN** the user opens Saliva - **THEN** Read cartridge SHALL be unavailable with Assay not available, and the app SHALL permit only authorized sample-record or demonstration actions without implying chemical detection.

Current proof: Governance never turns generic transport approval into missing assay software; lab collection never invokes BLE.

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

- Connected telemetry-only Nano saliva screen must assert Read cartridge disabled/Assay not available and only permitted alternatives.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5d3e40721be6fbdd212d5bffd7d98d5db6edd9057b4f4737e0465addca32431a. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-002-01 — PARTIAL

Buffered collector — - **GIVEN** a qualified collection method with recorded saliva and buffer quantities - **WHEN** collection is accepted - **THEN** the sample record SHALL retain those quantities, the defined dilution convention, method version, lot, and collection time for later comparison with each report's concentration basis.

Current proof: Real backend import fixture and collection validator preserve immutable collection/report lineage; specimen DOM submits observed saliva1/buffer1/factor2 and lot.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 972; 4 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 364; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- No exact assertion simultaneously compares retained method version, dilution convention, lot and collection time after accepted buffered collection to later report concentration basis.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7f72ea2f0de104ed1316aa8ad3b5f7ec8f892dbc14da53b5fb3017f0136501c5. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-002-02 — PARTIAL

Invalid sample identity from device — - **GIVEN** a session expecting sample A - **WHEN** a reader result identifies sample B or a different session - **THEN** the import SHALL fail with identity mismatch and SHALL not silently relabel the reading or attach it to sample A.

Current proof: Client rejects altered saliva record/sample identity and changed report specimen/time identity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-projection.test.ts::an unselected projection cannot hide unknown metadata or a different run/sample identity` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 37; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::rehashed report changes cannot move specimen collection, reuse prior analytical identities or misstate original units` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 133; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Reader/lab import result for foreign sample B/session must assert named identity mismatch and unchanged sample A persisted reading across server/client.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3f50648c3ed7fe618ee131cad0e65e6ae89112047cefc36d1fa2412d904daf81. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-002-03 — PARTIAL

Companion evidence cannot be omitted — - **GIVEN** a saliva sample with buffer, lot, adequacy, and report lineage metadata beyond the v0.1 projection - **WHEN** the check is saved and exported or explicitly uploaded - **THEN** the full typed companion attempt and its digest SHALL accompany the selected projection; unknown v0.1 fields or an incomplete manifest SHALL fail validation.

Current proof: Typed companion validates/freeze/exports actual backend fixture; unknown companion field, changed lot and inconsistent lineage reject.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::accepted collection and export companions bind all declared facts and reject duplicate or inconsistent report lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 364; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Explicit upload must assert the full companion+digest accompanies selected v0.1 projection and missing manifest fails, not only local archive inspect.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7baac2b861c634def2cc5df0da276d4430360d59283a143db168929700a62e9f. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-003-01 — PARTIAL

Below quantification without detection assertion — - **GIVEN** a laboratory report stating BLQ at an LOQ of 0.1 ng/mL - **WHEN** the report is imported and viewed - **THEN** the canonical value SHALL remain null, the display SHALL say Below quantification with the limit and original qualifier, and SHALL not say Detected or 0 ng/mL.

Current proof: Formatter keeps BLQ null, supplied bound and original qualifier without rounding zero; original fields remain available.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::below LOQ displays the supplied bound without creating a concentration or rounding it to zero` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 23; 1 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Exact imported0.1ng/mL laboratory BLQ case must assert no Detected/0ng/mL in complete view; current formatter fixture uses0.003 and does not import.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5244ca75faba85d23b64552eecd073377037b5077244d91f42f2fad84bfce969. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-003-02 — PARTIAL

Upper limit is not an exact result — - **GIVEN** an above-range report with a validated upper bound - **WHEN** the user reviews the channel - **THEN** the app SHALL display Above range and the bound, preserve null quantitative value, and SHALL not clip the reading to that bound for model or chart use.

Current proof: Formatter distinguishes above_range and shows supplied upper bound while typed censored projection rejects value tampering.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::only quantified results display a numeric concentration, preserving a real zero if reported` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 65; 1 current observation(s).
- `apps/mobile/tests/export-projection.test.ts::retained sample unit conversion, censored null and collection binding are independently checked` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 54; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Full above-range import/model/chart path must preserve null quantitative value and not clip to upper bound; title assertion alone is narrower.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0f21667b7aa88034477f5b4b548e8f1b97b01497925eeb2cf9afc8db7e892db9. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-004-01 — PARTIAL

Laboratory already corrected dilution — - **GIVEN** a result of 75 pg/mL reported for neat oral fluid with laboratory_corrected status - **WHEN** the app imports it from a buffered sample - **THEN** it SHALL store 0.075 ng/mL, retain the original 75 pg/mL and correction status, and SHALL not apply the collection dilution factor again.

Current proof: Import/report correction tests preserve original pg/mL and converted ng/mL; formatter retains laboratory correction and basis.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-projection.test.ts::retained sample unit conversion, censored null and collection binding are independently checked` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 54; 1 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Exact75pg/mL neat oral fluid with laboratory_corrected buffered sample must assert0.075ng/mL and no second dilution; existing units fixtures use different values/bases.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fd0806de45cc5fe3a270ada9fb900eae7e242f942d912d81ac990cb51fdb436a. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-004-02 — PARTIAL

Unspecified assay basis — - **GIVEN** a report that does not specify free or hydrolyzed analyte - **WHEN** it is retained for review - **THEN** assay_basis SHALL remain unspecified, the app SHALL expose the unresolved basis, and no compatible-model claim SHALL be made from separate allowed-method and allowed-basis lists alone.

Current proof: Formatter exposes declared assay basis and model scope uses exact assay tuples.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Unspecified input must remain unspecified, be visibly unresolved, and fail false compatibility from independent method/basis lists; current formatting test uses total_after_hydrolysis.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7dc0538c0f99211ba8ac9427861548d69220f4be592491d95409d0194b9305e2. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-005-01 — NOT_RUN

Quantified value outside interval — - **GIVEN** a reported value below its method's LOQ but labeled quantified - **WHEN** validation runs - **THEN** the app and server SHALL reject the inconsistent quantitative record with a field-specific reason and SHALL not coerce it to a valid reading.

Current proof: Mapped companion-lineage and not_measured-report tests do not submit quantified-below-LOQ record.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Client and server must reject quantified value below method LOQ with field-specific error and no coercion; execute exact boundary mutation.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 02c30568cfbb9a9869f5a46c6b4e24f8ce0cefb6efda2a7befe7e207cddc48c7. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-005-02 — PARTIAL

Forged validated source — - **GIVEN** a synthetic device or a manually edited local payload - **WHEN** it claims validated_sensor with an unknown calibration ID - **THEN** the claim SHALL not pass provenance validation, and no qualified concentration or research estimate SHALL result.

Current proof: Capability decoders prevent source promotion; exact schema/provenance validation disallows unsupported claims.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::capability source and calibration cannot promote an unprovisioned peripheral` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 60; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Explicit synthetic/manual saliva payload claiming validated_sensor with unknown calibration must fail app+server provenance and produce no qualified concentration/model result.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f8ee255fcc39b486468e7ad0fe4d0021be96feb8f44f4ff31a449f8b4c9a52f1. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-006-01 — BLOCKED

Assay disconnect — - **GIVEN** a cartridge read in progress - **WHEN** the reader disconnects before a verified completion payload - **THEN** the app SHALL show Read interrupted, preserve the identified sample and failed analytical attempt, and offer only method-permitted recovery without treating progress as a concentration.

Current proof: No implemented cartridge assay driver exists; unrelated lab-report revision tests do not execute cartridge read disconnect.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Actual assay reader disconnect must retain sample/failed analytical attempt, show Read interrupted and method-permitted recovery without concentration.

Prerequisite/evidence type: physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 8c1c68dbf4d34e29e2e316baaabde48cbaf27792cc33d5c04d7c27bc36ada71f. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-006-02 — PASS

Corrected laboratory report — - **GIVEN** a previously finalized analyte measurement - **WHEN** an authorized corrected report is accepted - **THEN** the system SHALL preserve the original immutable record, create a linked correction, and make any reanalysis a separately identified result rather than changing past evidence silently.

Current proof: API canonical snapshot/result/revision/evidence bytes remain unchanged across linked correction then separate reanalysis; client compares original digest and links each replacement result identity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 777bff6febd2ff4aa11b0e4de260298ee003da3257dfe0b0bc0a391005a3d99f. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-006-03 — PARTIAL

Replacing a finalized sample is a new check — - **GIVEN** a finalized invalid check with an inadequate specimen and earlier physical task evidence - **WHEN** the user chooses to collect another sample - **THEN** Start replacement check SHALL allocate a new session/target and require new physical acquisitions without overwriting the original or reusing its task.

Current proof: Guest replacement/save tests allocate linked replacement checks and preserve original; capture policy prevents retake replacement.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Finalized inadequate saliva with earlier actual physical task must create new target/session and assert task cannot carry forward to replacement.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c48f1fd13097363aa1c92bf961359bd281175191820ab8d7a7602f6365c64ee9. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-007-01 — PARTIAL

Metabolite panel partly unavailable — - **GIVEN** a quantified THC result and two unrun metabolite channels - **WHEN** the panel is displayed - **THEN** it SHALL show the THC value with provenance and Not measured for each other channel; absence of 11-OH-THC measurement SHALL not be described as evidence of sobriety.

Current proof: Formatter gives distinct Not measured versus quantified labels and preserves per-analyte provenance.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/measurement-format.test.ts::only quantified results display a numeric concentration, preserving a real zero if reported` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 65; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Exact panel with quantifiedTHC and two unrun metabolites must render both Not measured and assert no sobriety interpretation for absent11-OH-THC.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f71142d59f3f71f91e116a7758d7fc91deb9b7fe410bcc3c2d7b6117ca4babcf. Actual current source and raw evidence supply this disposition.

## OTGD-035-AND-SAL-007-02 — BLOCKED

Same report on Android and iOS — - **GIVEN** the same permitted laboratory report and sample metadata - **WHEN** either platform normalizes and renders it - **THEN** both SHALL preserve identical numeric meaning, qualifiers, original-report evidence, basis, and lineage, subject only to locale-specific display formatting.

Current proof: Shared TypeScript formatter/export/import tests preserve numeric meaning and report lineage.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual same report must normalize/render on supported Android+iOS and compare semantics; shared Node execution does not establish native platform UI parity.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 02995c3f6ba38046f594e12e7b21c93c450eef5d6a1c224cff9d6f5fc71b2fd2. Actual current source and raw evidence supply this disposition.
