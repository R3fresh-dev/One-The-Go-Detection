# OTGD-001: verification results

Canonical: `specs/FULL_SPECIFICATION.md`; SHA-256 `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Owner: `/root/verification`; OpenAI `gpt-6.1-sol/high` requested in PM dispatch; effective model identifier not independently exposed inside this worker. Scope: verification planning and static source inspection only. Relevant acknowledged decisions: D-001–005 v1 and D-006 v3; superseded D-006 v1/v2 retained as history. Execution candidate is not frozen.

Result: **NOT_RUN**. 128 individually identified requirements and 128 canonical acceptance cases are planned in `test-plan.md`. No current-source runtime suite, browser, native, firmware, live-dependency or performance result is claimed by this document. No historical evidence is transferred.

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

Focused evaluation/alcohol report: `../../reports/evaluation-implementation.md` SHA-256 `4332b81097b9dd4cc25545c46f808554439cf7d61a2425caa77cffe52ee96f0c`. Author reports185 evaluation/admission cases PASS, 43 governance cases PASS against actual disposable PG, 1338 non-PG API cases PASS with20 deselected;10 new evaluation and11 alcohol cases included. Initial alcohol fixture run4 failures and SQLite full-governance2 mandatory-PG failures preserved. Verifier read new assertions and confirmed all5 reported source hashes match at audit; raw pytest stdout/JUnit not linked, so execution is author-reported and not independently replayed/adopted. Only exact mapped focused assertions receive that evidence scope, not all planned cases.

Focused provenance report: `../../reports/provenance-implementation.md` SHA-256 `8d78d5000cbb7d1f08848a3420759a5139e3abdb83eb22f87c01944bb1d4d9f2`. Actual existing /tmp logs inspected:21/58/232-case focused runs show OK, original RED4 failures and canonical infra gate FAIL preserved. Runtime source-manifest binding is incomplete in author report; final raw source-bound gate required. No current remote/native job PASS or release authority adopted.

Independent source assertion audits for this dossier: EVAL-007 history/reference/authenticity audit; Alcohol dependency and acquisition-boundary audit; Rendered alcohol state/copy assertion audit; Permissions race and no-reprompt assertion audit; Current release provenance assertion audit; Actual-process interruption probe source audit; Authenticated ordinary-web live test source audit. Full assertion/limit details are in test-plan.md.


## Completed historical baseline semantic audit

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`: all 128 stable cases for this dossier were individually adjudicated against actual assertion bodies and named raw evidence. Counts: `{"BLOCKED": 38, "NOT_RUN": 1, "PARTIAL": 56, "PASS": 33}`. The complete case rows, exact remaining clauses and evidence references are in [this dossier's audit index](../../reports/acceptance-baseline-28e0729/OTGD-001-cases.md); full structured bodies and hash bindings are preserved in [acceptance-evidence.zip](../../reports/acceptance-baseline-28e0729/acceptance-evidence.zip). Archive SHA256 `89804264880c9a8e7676fb232eff570ff47921ec74cf11596400329ceb641ff8` was read back and all67member hashes matched.

These are historical scoped decisions, not current replacement acceptance. A PARTIAL case does not automatically establish a production defect or absent test; exact shared assertion evidence and unavailable external prerequisites remain distinct. Current canonical SHA256 at this checkpoint is `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`. Preserve the old candidate's canonical hash in the archived row. Current corrections require fresh frozen-source gates, affected case binding and independent confirmations; final approval remains pending.


## Final corrected source evidence — e89897cc852a

# OTGD-001 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `specs/FULL_SPECIFICATION.md`; SHA256 `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`.

128 cases, 128 requirements: BLOCKED 39, NOT_RUN 1, PARTIAL 55, PASS 33. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-001-HW-001-01 — PARTIAL

Owner acceptance evidence — BOM and firmware target agree with ADR-004.

Current proof: ADR004 and actual signed-reader guide both select NanoESP32 ArduinoC++; firmware build target is described with no fabricated final PCB/assay.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- BOM and firmware target agree: no accepted prototype BOM/manufacturing assembly evidence was supplied in the reviewed artifacts; target agreement alone does not establish that BOM.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 10b70df2e20fd27ecd76f9c6308f7540425aba5e720f0a73545d3f22497c236b. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-002-01 — PARTIAL

Owner acceptance evidence — End-to-end inspection shows no loss or replacement of provenance.

Current proof: Simulator source remains simulated/modelEligiblefalse; hosted guest saves measurement_only with null probability, no network/credentials; browser exported check source guest_demo and all archive entry hashes match; typed projections preserve simulated evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 87; 1 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/export-projection.test.ts::every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 29; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

Exact unproved clause(s):

- through EVERY storage/display layer: inspected simulator/client/archive/representative screen paths do not establish all server historical/cache/raw/native presentation layers.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f4c4ce9d81a1da0e3821892d91b10c9de4d09bf308e0165f4b9435f543395bf7. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-003-01 — PARTIAL

Owner acceptance evidence — Trace a captured record to one reader and firmware build.

Current proof: Signed fixture binds device/key/hardware/firmware/boot to exact grant; owned HTTP capture/result retains original signed identity/snapshot and device context.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual backend bound-reader HTTP fixture passes strict physical token and exact material digest` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 656; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Trace a PHYSICAL captured record to one reader/firmware build: no instrument-executed trace or protected physical-reader provisioning record supplied.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2b4cbd71871d5c58efb9ba993848ff9799b8238c71ca8b7632f8fb37cabfe750. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-004-01 — PASS

Owner acceptance evidence — Controlled fault injection produces explicit recoverable or invalid states.

Current proof: Out-of-order/duplicate fragments reconstruct once; conflicting content/CRC/replay/foreign identities refuse; cancellation invalidates before disconnect; synthetic stale/gap/contact faults latch explicit invalid reason and null current physiology. Scoped interface fault-injection acceptance is demonstrated.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::larger MTU, out-of-order fragments and identical duplicate reconstruct once` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 22; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::identity, changed message ID content and replay sequence are independently checked` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 67; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::corruption and conflicting duplicates fail closed and release in-progress storage` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 29; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::one transfer at a time and the 120-second assembly deadline are enforced` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 43; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::cancellation invalidates before disconnect and prevents stale completion into a different workspace` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 99; 1 current observation(s).
- `apps/mobile/src/device/tests/signal.test.ts::all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 62; 1 current observation(s).
- `apps/mobile/src/device/tests/signal.test.ts::stale identities, schema additions, sequence replay and bounded sample tampering cannot populate a current capture` — file SHA `6081eb0c7c2681f0520d69962d494c2dd14bfc60cd51bceed79209c9e862fba5`, line 81; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 23480c2d985c29463724a2c33529165f706ff5bf1fa148d8e7227be3e96754ee. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-005-01 — BLOCKED

Owner acceptance evidence — Gate G-05 sign-off and bench evidence precede participant connection.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Gate G-05 sign-off and bench evidence precede participant connection.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA c747b458fe558a3c766a0d2a7a8cf15f659be106fd672b0fde761b3fbfc08c98. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-006-01 — BLOCKED

Owner acceptance evidence — Approved power/connection diagram and documented permitted configurations.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Approved power/connection diagram and documented permitted configurations.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA ef34fcbad15cee4f55bdacf165a570881b595648fac9d69343426618616f48b8. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-007-01 — BLOCKED

Owner acceptance evidence — Reference signal reconstructs within frozen acquisition tolerances.

Current proof: Derived SDK fixture preserves configured rate with actual cadence null and refuses invented cadence/raw/quality; no physical calibration is implied.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Reference signal reconstructs within FROZEN acquisition tolerances: genuine reference-signal capture, accepted scaling/filter/contact/drop calibration and frozen tolerances are absent; requires HWL/G05/G06 instrument evidence.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 4f5f7428cb804a5aeae07c647bc256fb0803abfffce7a2138c90588e021a4a1f. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-008-01 — BLOCKED

Owner acceptance evidence — G-04 defines limits and verifies supported configurations.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-04 defines limits and verifies supported configurations.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 29a6714b256aee578beb56c9866271c1b100198d5cab5a96d10aae8d56263d06. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-009-01 — PARTIAL

Owner acceptance evidence — Reprocess retained permitted data to the same versioned features.

Current proof: Typed optical fixture retains native bounded evidence and refuses invented mm/onset/latency; local completion stores separate actual acquisition clock and verifies retained eye evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).
- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Reprocess retained permitted data to same versioned features: no independent permitted raw-recording reprocessing experiment with accepted geometry/segmentation/exposure calibration was supplied.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9473dc991b11354a1805634b88aa2739bc6d688f72c4868a6868b195f1d28a6e. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-010-01 — BLOCKED

Owner acceptance evidence — Handling review and inspection demonstrate the defined contamination boundary.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Handling review and inspection demonstrate the defined contamination boundary.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 2f8825fb660910e546df230ec3b6ce4fca66b4c421420ee0237b96e455e442b7. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-011-01 — BLOCKED

Owner acceptance evidence — G-10 approved drawings, duty-cycle measurements, and human-factors results.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-10 approved drawings, duty-cycle measurements, and human-factors results.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 010f0ca4a29efa639234e951b3c8394562d9e859bf68244cdaec2ed2e9145933. Actual current source and raw evidence supply this disposition.

## OTGD-001-HW-012-01 — PASS

Owner acceptance evidence — An expired or incompatible configuration cannot be reported as qualified.

Current proof: Retired exact configuration/calibration/qualification/device refuses current model authority; mismatched firmware/hardware/key/version/full digest fails; hypothetical config is selectable strictly before expiry and not at/after it. No actual calibration is invented.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_retired_current_authority_never_promotes_old_capture` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 229; 20 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_separate_release_checks_exact_current_configuration_tuple` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 93; 25 current observation(s).
- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::hypothetical breath contract configuration is selectable only strictly before its expiry` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1628; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3b203b4ac399dead9d6717511b9aa57184a470b9d7c77bb4702b8c609b256ae7. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-001-01 — PASS

Owner acceptance evidence — Specimen lineage shows one collection for a valid check.

Current proof: One accepted collection has original specimen/time/attempt and empty analytical projection; later separate report/analysis references same specimen; owner refresh/finalization preserve that lineage without a second collection.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4972f7e33dbbf5c611ff8875b43f001a032124b3722f851839dc9816b1376bfc. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-002-01 — BLOCKED

Owner acceptance evidence — Approved collection SOP and recovery/stability evidence at G-02.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Approved collection SOP and recovery/stability evidence at G-02.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 47fb2a073f7e9fc5aef6c6d644d3dded438cffc7793b6ca91dd7fdc8869c74b9. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-003-01 — BLOCKED

Owner acceptance evidence — Channel selection report identifies measured feasibility and unresolved channels.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Channel selection report identifies measured feasibility and unresolved channels.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 00be8bb27901d62e36e344a8cae9759bc5cf7fdf420c73928457dad6492fb7f9. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-004-01 — BLOCKED

Owner acceptance evidence — Prespecified qualification report passes G-03 criteria.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Prespecified qualification report passes G-03 criteria.

Prerequisite/evidence type: study_scientific_approval, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 633cc5f9e6c5d8fff08ce44d6ed5c49ef8a15495bbc13691f862bce756edef66. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-005-01 — BLOCKED

Owner acceptance evidence — Challenge panel and method comparison are approved before final qualification.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Challenge panel and method comparison are approved before final qualification.

Prerequisite/evidence type: study_scientific_approval, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 4fd73be14c20cc57f07df0140da6eb9095298771fde8945459bde59f786c87dd. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-006-01 — PASS

Owner acceptance evidence — Unit fixtures include pg/mL conversion without magnitude errors.

Current proof: 12500pg/mL converts exactly12.5ng/mL;6000pg/mL report remains original while canonical6ng/mL; conversion mismatch/limit/sample binding is rejected and null remains null.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::synthetic concentrations preserve unknown metabolites as null, with exact pg/mL conversion` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 222; 1 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).
- `apps/mobile/tests/export-projection.test.ts::retained sample unit conversion, censored null and collection binding are independently checked` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 54; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 9d689a32bfdcadc68b12d6730333244cc69d7dc288c1e78c9d35a9d5ef60e915. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-007-01 — PASS

Owner acceptance evidence — Contract validation rejects fabricated quantified values for censored results.

Current proof: Rehashed below_loq while numeric is refused by retained projection and report API; censored output retains null and supplied limit, never zero; genuine quantified zero remains0.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-projection.test.ts::retained sample unit conversion, censored null and collection binding are independently checked` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 54; 1 current observation(s).
- `services/api/tests/test_report_revisions.py::test_sample_identity_units_nulls_and_future_clock_bounds` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 725; 30 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::below LOQ displays the supplied bound without creating a concentration or rounding it to zero` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 23; 1 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::only quantified results display a numeric concentration, preserving a real zero if reported` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 65; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 145ab6f67fc5eba174a075fd06617e8612056ac9f4442539244416591bb59f6a. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-008-01 — PARTIAL

Owner acceptance evidence — Cross-field validation and incompatible-input cases pass.

Current proof: Incompatible approved assay tuple, duplicate/censored measurements and forged provenance refuse instead of entering prediction/import.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_import_rejects_forged_or_incompatible_analytical_evidence` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 304; 40 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- free versus total-after-hydrolysis and unspecified basis: the inspected negative bodies do not isolate missing/changed assay_basis and required-basis refusal with exact cross-field assertions.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2638e8e93edc7ddfce53a81a408748d0b7595a58bd4f1c52c09d4ab75c6a1240. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-009-01 — BLOCKED

Owner acceptance evidence — Prespecified agreement and failure analysis; external validation before claims.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Prespecified agreement and failure analysis; external validation before claims.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA c7597bbb47aa394df28cffbbec7c95429ba122341f250ff60c784b7f79e02133. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-010-01 — PARTIAL

Owner acceptance evidence — An independent reviewer reconstructs a selected reported measurement.

Current proof: Fictional specimen/report preserves original collection/measurement times, instrument/operator/method, original units and immutable versioned report provenance.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_distinct_operator_creates_subject_owned_source_and_import` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 164; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- An INDEPENDENT reviewer reconstructs selected REPORTED measurement under qualified assay: supplied records and PDF bytes are engineered/doubled; no actual laboratory custody/reconstruction review.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4a7ef09ff34c6b0a95e5dcf90f0a5ba5a1abea2e116d18607a763496b082cce2. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-011-01 — PARTIAL

Owner acceptance evidence — Deliberate invalid specimens cannot yield an apparently ordinary concentration.

Current proof: Unknown inadequate specimen/expired supply refuses valid collection or records explicit invalid reason; old invalid sample survives linked retry; unsupported/nonquantified fields cannot become numeric display.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_chronology_and_handling_are_actual_events_not_form_progress` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 535; 35 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_rejects_forged_analytical_authority_and_invalid_metadata` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 388; 60 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::only quantified results display a numeric concentration, preserving a real zero if reported` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 65; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- All deliberate invalid specimen classes including contamination/overflow/out-of-range must have distinct reasons and never ordinary concentration: inspected unit matrices do not cover every physical inadequacy class.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3e06a33b9138526e958af64b416a8c53d6651f52d5ab4e1425cfe33821765834. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-012-01 — PASS

Owner acceptance evidence — Retry audit preserves both attempts and their disposition.

Current proof: Retry allocates distinct specimen/attempt with supersedes link and retains original disposition; finalized original snapshot/result/digests remain byte-equivalent across linked correction/reanalysis; direct rewrite409.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).
- `services/api/tests/test_api.py::test_finalized_records_reject_rewrites` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 212; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA d582ccc9e35e116635eb6dd1b40e32690aedf9aee0d3f2dc7fabf89b28a8f4b0. Actual current source and raw evidence supply this disposition.

## OTGD-001-ANA-013-01 — BLOCKED

Owner acceptance evidence — G-03 and G-13 contain measured data or dated supplier evidence.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-03 and G-13 contain measured data or dated supplier evidence.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 626961ce7d65ad6eae97fbc97268ca2d5dc1c1d24e5237cf3c1518bcc66d7e52. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-001-01 — PASS

Owner acceptance evidence — Scripted P0 journey displays measurement-only completion.

Current proof: Scripted P0 guest journey navigates capture/review/save, displays Measurements saved, exports exact check with measurement_only/null probability; owned API measurement-only completion agrees and foreign owner sees404.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `services/api/tests/test_api.py::test_end_to_end_measurement_only_and_owner_isolation` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 197; 5 current observation(s).

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

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 0fb76586df11b54e936b25787d1c37539fecd4bbec30081ea3f8ebbb8c445d38. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-002-01 — PASS

Owner acceptance evidence — Boundary and unit examples produce correct BMI or explicit missing status.

Current proof: 5ft10/150lb converts177.8cm/68.0388555kg with exact expectedBMI; repeated unit toggles preserve canonical values, invalid boundaries reject and absent height/weight yields nullBMI.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::whole feet plus bounded inches and pounds use exact SI conversions` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 67; 1 current observation(s).
- `apps/mobile/tests/profile-form.test.ts::optional blank demographics stay null and unknown remains distinct from declined` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 56; 1 current observation(s).
- `apps/mobile/tests/profile-form.test.ts::display rounding and repeated unit toggles preserve original canonical values` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 87; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::profile converts SI units and rejects ranges, relative time and unknown enums` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 131; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 5a0f32d48b61762bd4c413cd33f736fc00848df342a7c8f7b1b1efb680019013. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-003-01 — PARTIAL

Owner acceptance evidence — Missing context survives export and cannot become a fabricated timestamp.

Current proof: Unknown/declined fields and null demographics stay distinct; frozen known last-use original UTC is preserved and elapsed time recomputed from check start; unrelated current profile excluded from selected export.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::optional blank demographics stay null and unknown remains distinct from declined` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 56; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::check freezes original profile timestamp and recomputes elapsed use at its start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 152; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::single-check export preserves exact scope and excludes unrelated current profile` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 407; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Missing context survives export and never fabricated timestamp: no exact unknown/declined last-use archive readback assertion in these reviewed bodies.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA ae4cbb1fb38ac74e6d776b1750a6089efd7a34774025ab3b3774bf3cbcaae7f0. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-004-01 — PASS

Owner acceptance evidence — Task event record verifies counts and excludes practice from scored features.

Current proof: Actual Swift core host execution verifies66literal schedule entries/hash and6practice/60scored/48go/12withhold counts; scored features exclude practice and omitted trials remain explicit.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 71885ec631023798330a4e10c0a50d73a06930bead515524c2f1fdc7c2e211bc. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-005-01 — PASS

Owner acceptance evidence — Seeded replay and event-level inspection reproduce features.

Current proof: Seeded literal schedule/onsets/hash match; every frozen trial boundary checks disposition/order/selected response; late frame/callback/onset and terminal drain/overflow/cancel rules have exact assertions in executed native core.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 23a338f251a15cfb03a90c848f6a7062a786dfc23d1c78b90c589be7b48dfec4. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-006-01 — PASS

Owner acceptance evidence — Reference event streams match expected derived feature records.

Current proof: Reference native core streams yield exact median/IQR/p90, omission rate and null speed on all omissions; literal trial vectors check wrong choices/commission outcomes and expected quantiles.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).
- `services/api/tests/test_cross_language.py::test_host_generated_native_contract_fixture_against_independent_server_scoring` — file SHA `f702d93abb8e32afa715db8bfce6f0677ed0276be8369c95b1ed321641c55c39`, line 142; 5 current observation(s).
- `services/api/tests/test_cross_language.py::test_native_contract_tampering_rejected` — file SHA `f702d93abb8e32afa715db8bfce6f0677ed0276be8369c95b1ed321641c55c39`, line 227; 30 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 78026ac4eae38cbd9b1d0b32c5f260a6fd05d61ca5964ac47b69afe3087ed818. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-007-01 — BLOCKED

Owner acceptance evidence — G-06 freezes and verifies device-specific timing acceptance.

Current proof: Host native core enforces monotonic event budgets and explicit late frames; these software boundaries are not measured physical onset.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- G06 freezes/verifies device-specific timing acceptance on supported phones: no named-device latency/calibration experiment or independent G06 approval supplied.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 65d4a50414f000b08b51632caaf5cd504e416d875a6cb0baecc70ceb7b9c9acd. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-008-01 — PARTIAL

Owner acceptance evidence — Interruption cases produce the prescribed quality and retry state.

Current proof: Process interruption retains invalid task/null features and linked retry; cancellation is immediate before delayed device stop; native late-frame/onset paths have explicit faults.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 847; 1 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- All background/notification/orientation/late-frame/interrupted-touch native OS cases produce prescribed quality/retry state on supported Android/iOS: host checks do not execute complete OS matrix.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e5afc69e040e419d37174f7f74a5c7d9a7c08b0901d0ad7f457781d5820020c4. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-009-01 — PASS

Owner acceptance evidence — Low-quality and unscaled examples cannot pass as calibrated diameter.

Current proof: Optical projections refuse fabricated calibrated geometry/onset/latency; model requires compatible optical qualification; rendered normalized/unmeasured response is visibly withheld rather than relabeled mm. Scoped software/refusal acceptance only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b79f88e58edcfc6bf24fe4f85a33bf1e1877d14cf1212315b187939495f3baaa. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-010-01 — PARTIAL

Owner acceptance evidence — Result inspection identifies whether a measurement followed the approved protocol.

Current proof: Exact instruction receipt and original device-signed cardiac projection retained through local save and server result; source/quality stay immutable.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- RESULT inspection identifies whether cardiac measurement followed approved duration/posture/activity protocol: no executed result-screen assertion displaying all instruction/compliance/duration context, and actual compliance remains declared.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1a4f78ec0e7fdb712e495929f5a31e9a77b22e5d78259c1b7deeb3d491fc4389. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-011-01 — PASS

Owner acceptance evidence — Temporal audit prevents later sessions entering a baseline.

Current proof: Future or incompatible baseline refuses; original independent baseline proof/current delta match; explicit historical age and earlier observation gates enforce; population mode has no fallback from missing personalized evidence. This proves temporal software audit, not first-use clinical validity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_baseline_bounds_and_bias_are_applied_to_frozen_features` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 567; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_personalized_baseline_uses_explicit_historical_proof_and_conservative_age` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 263; 20 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_personalized_http_capture_resolves_its_own_original_baseline_and_rejects_changed_signature` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 395; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b9233447530da7e18afa121d20522f9d417e1ed88465c5e09c7c7c2f2a4de499. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-012-01 — PARTIAL

Owner acceptance evidence — State-by-state screenshots and API checks match the LLD.

Current proof: Actual API/software contracts distinguish measurement_only,1.1research_estimate,inconclusive and invalid; guest browser screenshot/save/export proves measurement/nullstate and explicit invalid synthetic fault.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 142; 4 current observation(s).
- `services/api/tests/test_api.py::test_end_to_end_measurement_only_and_owner_isolation` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 197; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- State-by-state SCREENSHOTS and API checks matching LLD: complete four-state current result/history/notification screenshot matrix not supplied. This is missing presentation evidence, not a demonstrated state-machine defect.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1c18eb255fa61c7f53dda956d01b156dc4a04448259cb86ca27074fd23e9689a. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-013-01 — PARTIAL

Owner acceptance evidence — Copy review covers all result, notification, and error screens.

Current proof: Representative rendered alcohol/eye/ECG screens retain no-clearance/physical/diagnostic limits; research result is bound to fictional named historical endpoint.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).
- `apps/mobile/tests/research-result.test.ts::actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 147; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Copy review covers ALL result, notification and error screens for driving/legal/intoxication claims: complete current screen inventory review and independent clinical interpretation are not supplied by representative tests.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 07a208659344c85013018c40f882b6f0031b2859eae95a301dddde540c63b003. Actual current source and raw evidence supply this disposition.

## OTGD-001-APP-014-01 — BLOCKED

Owner acceptance evidence — G-10 lists supported configurations and tested accommodations.

Current proof: Task input/schedule compatibility remains versioned in native host tests; no physical accessibility qualification is inferred.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- G10 supported configurations and TESTED accommodations, language/input-mode limits and adaptation revalidation: named supported-device and assistive-technology approval/evidence absent; browser viewport tests cannot replace this owner/native requirement.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 5f21d2198a17193c0b4be076be5ac36df7140731418fabc4dcb2c97686e813f4. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-001-01 — BLOCKED

Owner acceptance evidence — G-01 protocol defines outcome, assessor, timing, and label rules.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-01 protocol defines outcome, assessor, timing, and label rules.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 8257ec5424696a30840a4b1fa8d2e0e8f43e3b8bd1a4eeca91793950dfa0bc87. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-002-01 — PARTIAL

Owner acceptance evidence — Model review identifies measured features and any explicitly evaluated latent model.

Current proof: Measured feature vectors are explicit and train-only fitting/HRdelta reproduce runtime; no clearance predictor is synthesized in these exercised artifacts.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Model review identifies measured features and ANY explicitly evaluated latent model across complete admitted model inventory: inspected examples do not establish exhaustive absence of invented demographic clearance formulas.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9b540e1ee872fd4b8ec4dc86f579ae15fbf73f61b85d19dd1234ea8ff07b351d. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-003-01 — PASS

Owner acceptance evidence — Adversarial synthetic records produce the specified validity behavior.

Current proof: Adversarial synthetic wrong provenance/quality/censored/missing/duplicate/range inputs refuse or remain invalid with all denominators; no healthy value replaces missing/invalid chemistry/cardiac evidence.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_invalid_custody_or_faults_remain_in_all_row_denominators` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 182; 440 current observation(s).
- `apps/mobile/tests/export-projection.test.ts::retained sample unit conversion, censored null and collection binding are independently checked` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 54; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c121108643cee5c6e3c91a9da2ba46785f17899809ee56228c49d8010c31e0ff. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-004-01 — PASS

Owner acceptance evidence — Any prediction can be reconstructed from immutable versioned inputs.

Current proof: Deterministic CLI reproduces exact dataset/split/analysis/training/artifact/report hashes and original row identity; strict result binds model/acquisition/context/evidence/version and rejects forged links. Reconstruction is scoped to software fixtures; external history authenticity stays false.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 137; 20 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `services/api/tests/test_model_engine.py::test_training_evaluation_policy_and_result_proof_are_bound` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 437; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a1352c6d6be6950b57d23e252811517bc2d158b079c537b4b0f2070823090ca3. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-005-01 — PARTIAL

Owner acceptance evidence — Split audit and leakage review pass before locked evaluation.

Current proof: Whole people held out, later-session partitions disjoint and exhaustive; held-out value/label changes cannot alter fitted artifact; CLI preserves lock refs but explicitly reports historical_lock_provenfalse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_frozen_participant_and_temporal_partitions_reproduce_without_outcomes` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 209; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_held_out_hr_values_and_outcomes_cannot_affect_training` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 221; 20 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Split audit/leakage review PASS BEFORE locked evaluation access for actual qualified research: supplied file consistency cannot prove true prespecification, blinding or independent historical review.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f248731662936b07e4835ca1763dddd193f1df9388fe3dc67d9543f152a9c787. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-006-01 — PASS

Owner acceptance evidence — Timestamp and dependency audit covers each feature and baseline.

Current proof: Future observation/profile/endpoint fields and incompatible baseline refused; same-check target remains original despite later assay availability; no arbitrary later row supplies baseline. Software timestamp/dependency audit demonstrated.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_invalid_or_future_source_data_are_rejected_before_fitting` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 297; 110 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_same_check_observations_and_later_assay_delivery_preserve_original_target` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 319; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_personalized_baseline_uses_explicit_historical_proof_and_conservative_age` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 263; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 5d068596120e2e8b5fc73e2d43e7a464fe931511bc7c098072cdbffd9b014f17. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-007-01 — PASS

Owner acceptance evidence — Manifest review and incompatible-record checks pass.

Current proof: Manifest/artifact/report hashes and policy/endpoint/threshold/cohort/required-channel compatibility are validated; incompatible protocol/hardware/co-use/age/provenance/assay/timing or feature scope refuses.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_training_evaluation_policy_and_result_proof_are_bound` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 437; 5 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_actual_artifact_not_just_required_channels_is_hr_only` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 277; 10 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 53f0289e8f5628b95415fa0e899b289129852bdfe047cf07b80aaa0b9bcea501. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-008-01 — PASS

Owner acceptance evidence — Unauthorized activation and retired-model invocation are rejected.

Current proof: Current notice/consent/generation/recovery/qualification/calibration/bytes refusal returns no score; model revocation after compute prevents commit; retired dependencies cannot promote old captures and legacy model unchanged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `services/api/tests/test_model_admission.py::test_model_retirement_and_consent_change_between_compute_and_commit` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 542; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_retired_current_authority_never_promotes_old_capture` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 229; 20 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_legacy_released_model_remains_readable_at_original_submitted_sha` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 166; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 6f6a5893d6369652e356b32de658c09f22e8d88929ef61f9070cd50aec10da43. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-009-01 — PASS

Owner acceptance evidence — Negative inference cases verify null/absent probability and explicit reason.

Current proof: Ordinary/guest/P0 API completion probability null; simulated/changed required authority becomes inconclusive with model_idnull; strict uncertainty result requires null probability and explicit refusal/abstention state. Version1.1 governed exception is preserved.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_end_to_end_measurement_only_and_owner_isolation` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 197; 5 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `apps/mobile/tests/research-result.test.ts::a verified uncertainty band requires null abstention rather than a probability or optimistic classification` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 221; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA ab55638daa00b39d1bc133f07fb947780e26f64823f0cdb135d2a729845f1aa8. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-010-01 — PARTIAL

Owner acceptance evidence — Every gate has both passing and rejecting integration evidence.

Current proof: Real application HTTP/worker with fictional releases admits qualified conditional1.1; parameterized authority/model input negatives refuse no score; exact signed HR exception also admitted.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- EVERY gate has passing AND rejecting INTEGRATION evidence: some scope failures are unit scope_check calls and broad owner/native/physical prerequisite matrix remains unexecuted; not all current boundary pairs shown at integrated request/worker/read.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4c1d2e3653ebc0ef1aafed9c036b115687aba38bcc247b1bf6eb2c29222d306b. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-011-01 — PARTIAL

Owner acceptance evidence — Variant selection is explicit, versioned, and validated.

Current proof: Explicit HRonly mode validates exact sole feature/channel, no automatic broader model reuse, and legacy four-variant plan remains unchanged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_actual_artifact_not_just_required_channels_is_hr_only` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 277; 10 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_hr_scope_rejects_mixed_rows_and_unprespecified_legacy_evidence` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 302; 20 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_required_channel_scope_is_heart_rate_only` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 145; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_legacy_absent_optional_fields_do_not_change_dataset_or_plan_bytes` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 315; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Every permitted missing-channel variant selection must be explicit, versioned and validated. Current pending-chemistry required-versus-optional scope branch is tested with genuine released typed manifests and no invented value; that isolated scope fixture does not establish the full inventory of separately qualified model variants.

Prerequisite/evidence type: software_variant_inventory_evidence, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7e8e896c14a5953496248f46e0a2c1bad081bb6627502ffde9ad74a3c945feae. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-012-01 — BLOCKED

Owner acceptance evidence — Locked analysis plan and artifact hashes predate evaluation access.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Locked analysis plan and artifact hashes predate evaluation access.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA bb046570a9223662ac721fb3f70d3f7c68b99dfccf5aaaf0a623394a06d752f5. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-013-01 — PARTIAL

Owner acceptance evidence — Result contract and independent interpretation review pass.

Current proof: Strict1.1 result retains endpoint/model/version/uncertainty/originaltarget/evidence; altered proof/classification/time/owner/policy refuses; inconclusive uncertainty cannot carry a probability.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/research-result.test.ts::actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 147; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::a verified uncertainty band requires null abstention rather than a probability or optimistic classification` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 221; 1 current observation(s).
- `services/api/tests/test_model_engine.py::test_training_evaluation_policy_and_result_proof_are_bound` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 437; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- INDEPENDENT INTERPRETATION REVIEW passes: no named responsible clinical/statistical/user interpretation report supplied. Tested DTO integrity is not that owner review and no software defect follows from its absence.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c58675ffb5ffa81ad13600cb5855273d5a2753bc31b3be69698666224d39c3ab. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-014-01 — PARTIAL

Owner acceptance evidence — Ablation report supports retained measurement burden.

Current proof: Existing mode emits four matched-row ablations; invalid/abstained counts retained; restricted HRonly refuses fabricated chemistry/ECG comparison claims.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_hr_report_cannot_claim_unmeasured_chemical_or_ecg_comparisons` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 363; 25 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Ablation report SUPPORTS retained measurement BURDEN via independent predictive-value evidence: engineered cohort results do not establish real incremental clinical/usability benefit; requires G09 study evidence.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 72f17fe418d4dc589b7eee0ada11096eff22835e9e6737d9882df5055575bafc. Actual current source and raw evidence supply this disposition.

## OTGD-001-MOD-015-01 — PARTIAL

Owner acceptance evidence — Change-control exercise preserves the prior artifact and results.

Current proof: Model retirement fences compute-to-commit and leaves prior submitted artifact unchanged; changed locked pipeline/model thresholds refuse; no silent artifact mutation in exercised flows.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_model_retirement_and_consent_change_between_compute_and_commit` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 542; 5 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_legacy_released_model_remains_readable_at_original_submitted_sha` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 166; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Versioned UPDATE reevaluation/authorization exercise preserves PRIOR artifact AND results across a new deployed model, with no online retraining: retirement-only test does not execute full update/publish/prior-result-history path.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 93e5d7ee696fa1a345768b127d2d658e528f4273fa6491c380d8db407212ece3. Actual current source and raw evidence supply this disposition.

## OTGD-001-ALC-001-01 — PASS

Owner acceptance evidence — Interface and synthetic demonstrations retain channel identity and provenance.

Current proof: Distinct typed simulated alcohol projection remains separate; screen labels mg/L breath alcohol and qualified capture unavailable; missing adapter cannot acquire or manufacture concentration.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-projection.test.ts::every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 29; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::fresh absent-breath-adapter capability overrides stale cached availability before any hardware invocation` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1689; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 4151718a5e3c42960cc273af83caa0f30962352ab70e636f4af53e6edc19bbc5. Actual current source and raw evidence supply this disposition.

## OTGD-001-ALC-002-01 — BLOCKED

Owner acceptance evidence — G-11 documents supplier specifications and design tradeoffs.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-11 documents supplier specifications and design tradeoffs.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA e79721a1aac39a619634f3d836e6c10a5b07965a226f28bf03e41308687023cc. Actual current source and raw evidence supply this disposition.

## OTGD-001-ALC-003-01 — PARTIAL

Owner acceptance evidence — Contract fixtures preserve all metadata without unapproved blood conversion.

Current proof: Typed simulated fixture retains separate alcohol evidence; UI explicitly mg/L, no automatic combined classification/driving clearance.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/export-projection.test.ts::every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 29; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Full contract fixtures preserve actual calibration ID, sampling time/quality and every range qualifier with NO blood conversion: reviewed projection equality/copy tests do not inspect the complete field/qualifier matrix or a calibrated breath source.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6c8b8b041685171a45b79232bb25c9938ac56d7aa9f2f6a71756e21deb32228c. Actual current source and raw evidence supply this disposition.

## OTGD-001-ALC-004-01 — BLOCKED

Owner acceptance evidence — Dedicated alcohol qualification against the selected reference method.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Dedicated alcohol qualification against the selected reference method.

Prerequisite/evidence type: study_scientific_approval, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 74fdc519927ff74d5918eba54c8845326281c4969c706205934e5e014ccd3653. Actual current source and raw evidence supply this disposition.

## OTGD-001-ALC-005-01 — PARTIAL

Owner acceptance evidence — Protocol and model manifest agree on co-use handling.

Current proof: Unknown co-use gate rejects model scope and rendered copy requires model-specific co-use authority with no averaged classification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).

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

- ACTUAL study protocol and admitted model manifest agree on co-use cohort/policy: no genuine independent study protocol review provided; generic unsupported-co-use test does not authenticate it.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 6fdc02f08bf453655b7f0375f5c0b0d6398afa8a795d5d865678e5ffaaec5d32. Actual current source and raw evidence supply this disposition.

## OTGD-001-SEC-001-01 — NOT_RUN

Owner acceptance evidence — Pre-commit/release review and secret/data scan of the staged changes.

Current proof: Canonical source prohibits participant data/credentials and fixtures visibly declare fiction; this is policy/source inspection only.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Precommit/release review AND secret/data scan of exact staged revision: no executed exact-revision scan adopted here; unrelated raw/optical tests cannot establish repository-content safety.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / NOT_RUN; record SHA 9c6c35eb4e7ea0085ccbd76ca3b2879754acd14d005a182a90e4c69b9f42e165. Actual current source and raw evidence supply this disposition.

## OTGD-001-SEC-002-01 — PARTIAL

Owner acceptance evidence — Unauthorized-role tests and identity-mapping review pass.

Current proof: Foreign owner reads404/emptylist; distinct authorized staff import retains participant ownership and actor/targetaudit; missing/revoked role or wrong target/study/generation rejects.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_end_to_end_measurement_only_and_owner_isolation` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 197; 5 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_current_target_and_genuine_operator_authority_required` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 184; 45 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_distinct_operator_creates_subject_owned_source_and_import` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 164; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Defined complete ROLE MATRIX and identity-mapping independent review: these ownership/staff negative tests do not establish comprehensive pseudonym/direct-identity mapping and least-privilege deployment review. No new role/identity defect asserted.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 23e245d539593c2ede954c4c98e8d54aae47ebe1f8188c0c641a0fafb4107f7a. Actual current source and raw evidence supply this disposition.

## OTGD-001-SEC-003-01 — PASS

Owner acceptance evidence — Consent/authorization and upload traces demonstrate the boundary.

Current proof: Local/guest save never queues account upload or grants enrollment; explicit upload queues retained original evidence with stablekeys; exact study consent must precede owned server research start; missing consent/protocol/currentstudy rejects. Scoped software boundary traced; no participant authorization created.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 410; 1 current observation(s).
- `services/api/tests/test_operator_governance.py::test_real_session_start_requires_current_approved_study_and_exact_protocol` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 361; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 2e1639d014e6f2948452c10495f468a576f53affe0c753a78ee1ffb331cb1130. Actual current source and raw evidence supply this disposition.

## OTGD-001-SEC-004-01 — BLOCKED

Owner acceptance evidence — Deployment configuration and access review satisfy G-12.

Current proof: Named JS keystore/SQLCipher/backup-exclusion doubles refuse unavailable cryptographic prerequisites with no plaintextfallback. This is software failure behavior only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/native-storage.test.ts::native account storage fails closed when key storage, cipher support or backup exclusion is unavailable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 199; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Deployment CONFIGURATION/ACCESS REVIEW satisfies G12 approved transport/storage/secretmanagement and actual native protection: deployed encryption/access/provisioning and keycustody evidence absent; source policy or mocked SQLCipher does not replace them.

Prerequisite/evidence type: native_os_execution, deployment_cloud_or_owner_prerequisite, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 680fefb402b979f35ef6163164072b39601f077aead5a9f15bdc5c8ebc51cb07. Actual current source and raw evidence supply this disposition.

## OTGD-001-SEC-005-01 — PARTIAL

Owner acceptance evidence — G-12 states durations and tests deletion across primary/backup workflows.

Current proof: Optional recording defaults off, consent/policy expiry and generation deletion refuse; bounded export expiry is a hard cap and revoked consent cannot verify report after storage.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/raw-recordings.test.ts::default off, local-only opt-in, upload dependency, policy expiry and pending stop fences remain distinct` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 77; 1 current observation(s).
- `services/api/tests/test_raw_export.py::test_expiry_and_retention_are_hard_caps_and_generation_deletion_denies` — file SHA `4e56b75f3098467f17898644d3ae7d77f37d7be31efd3fb6e464c852dc2c3014`, line 319; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_completion_reauthorizes_after_external_storage_and_cannot_resurrect_cleanup` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 1127; 25 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- G12 names real approved durations and tests deletion across PRIMARY/BACKUP workflows: these modeled policies/storage doubles do not establish real deployment/backup erasure or approved participant retention.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 10304b714e274f05b35e5835529aeda5e49f365013e555cef70b5dc7a90215bd. Actual current source and raw evidence supply this disposition.

## OTGD-001-SEC-006-01 — PARTIAL

Owner acceptance evidence — Representative failure logs pass content review.

Current proof: Modeled administrative failure receipt contains exceptiontype/status without confidential passwordtext; successful receipt pins source/task/operation only; delegated import audits actor and targetaccounts.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_fargate_runtime.py::test_admin_failure_receipt_contains_only_exception_type_and_task_exits_failure` — file SHA `ca197ab6b956e6d137d18c955f7d5dce0df628423458b6fa18bcbf4a4f2877d1`, line 408; 5 current observation(s).
- `services/api/tests/test_fargate_runtime.py::test_maintenance_receipt_binds_actual_task_and_exact_source_without_result_contents` — file SHA `ca197ab6b956e6d137d18c955f7d5dce0df628423458b6fa18bcbf4a4f2877d1`, line 390; 5 current observation(s).
- `services/api/tests/test_lab_handoff.py::test_distinct_operator_creates_subject_owned_source_and_import` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 164; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- REPRESENTATIVE failure LOG CONTENT REVIEW omits all rawhealth/directidentifiers while preserving full audit actor/operation/record/time across deployment: specific receipt tests are not exhaustive real log/audit content review. No payloadleak defect inferred.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA eff9826c538fe920b364b3cda4beae730536fe44a87227e2969383182399e64f. Actual current source and raw evidence supply this disposition.

## OTGD-001-SEC-007-01 — BLOCKED

Owner acceptance evidence — Tabletop exercise and responsible contacts documented.

Current proof: Canonical SEC007/G12/G14 require security/withdrawal/correction/incident operational procedures before participantuse; no external participant action authorized.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- TABLETOP exercise and RESPONSIBLE CONTACTS documented: actual named operational ownership/contact roster and rehearsed incident/lostdevice/withdrawal/correction exercise absent from supplied qualified evidence. OAuth/UI tests cannot close this owner requirement.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA ddf35170d390b27481e2ec3c857e0ef910463c6d235cb901b2ce3bf912339972. Actual current source and raw evidence supply this disposition.

## OTGD-001-OPS-001-01 — BLOCKED

Owner acceptance evidence — Architecture review confirms boundaries and deployment configuration.

Current proof: Frozen ADR012 and architecture identify modularFastAPI/PostgreSQL/private artifacts. Existing realPG JUnit cases prove database trigger/locking behaviors; laboratory/model object storage in exercised HTTP fixtures is doubled.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Actual target deployment configuration/private object-storage access requires authorized deployment review. Current all7 local gates and exact-tree14-job CI pass; they establish local software/transport, not target AWS private network/IAM/storage behavior.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 00f7f54f0f3df49585678365d7c81f800fc44d17ed7e749feb4ca0c52f878875. Actual current source and raw evidence supply this disposition.

## OTGD-001-OPS-002-01 — PASS

Owner acceptance evidence — Repeated identical submissions produce one accepted logical record.

Current proof: Same-body/key collection retry returns identical immutable receipt, changed body/key conflicts, lost client reply retries exact declaration/key and one durable consent intent persists; no duplicate specimen or accepted logical record.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_positive_collection_without_ble_is_owned_immutable_and_pending` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 264; 5 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1114; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 410; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b2b77189730bc08470ab003695744879c3c8783871e813d392f70a23c4aba780. Actual current source and raw evidence supply this disposition.

## OTGD-001-OPS-003-01 — PASS

Owner acceptance evidence — Correction scenario preserves original content and provenance.

Current proof: Finalized snapshot direct overwrite409; corrections/reanalysis retain byte-identical original and separately linked revisions; specimen retry linked and old failed disposition immutable.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_finalized_records_reject_rewrites` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 212; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA fe2b42798741c51205f212c577d9f6dccdd1af79ebec564f7cbe4d1ab2c6f57d. Actual current source and raw evidence supply this disposition.

## OTGD-001-OPS-004-01 — PARTIAL

Owner acceptance evidence — Clock-drift and reordered-message cases retain interpretable timing.

Current proof: Clock interval bounds/padding retained, discontinuities rejected, out-of-order duplicate fragments reconstruct once, decimal epoch and original conservative interval preserve uncertainty without fake physical UTC.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/protocol.test.ts::clock evidence retains all exchanges and chooses narrowest interval with resolution padding` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 80; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::larger MTU, out-of-order fragments and identical duplicate reconstruct once` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 22; 1 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_epoch_precision_uses_durable_decimal_values_and_never_rewrites_device_evidence` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 84; 5 current observation(s).
- `services/api/tests/test_cardiac_authority_provenance.py::test_signed_sdk_duration_respects_exact_reviewed_rate_limit_not_a_rounded_millisecond` — file SHA `6247b1ba439b9d6f87a7467ec66a8fa83272aeb811ade6231196d23776294985`, line 109; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Cross-device clock-drift AND reordered-message cases retain interpretable timing across all actual/native devices: inspected host protocol/arithmetic checks do not establish real supported-device synchronization/failure matrix.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4e692c26670860e36d2f5f34ea8dc30ccd909f16e7f1af7af4a3929f1a60dbc8. Actual current source and raw evidence supply this disposition.

## OTGD-001-OPS-005-01 — PARTIAL

Owner acceptance evidence — Network interruption and restart exercises preserve correct terminal state.

Current proof: Unknown collection response retries exact retained body/key, reopened form persists without hardware; doubled native partitions preserve same encrypted-store API state and failclosed when cryptoprerequisites unavailable; sync markscomplete only after resultread.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1114; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::reopening the owned workspace preserves the actual collecting form without restoring rest or invoking hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1056; 1 current observation(s).
- `apps/mobile/tests/native-storage.test.ts::concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 128; 1 current observation(s).
- `apps/mobile/tests/native-storage.test.ts::native account storage fails closed when key storage, cipher support or backup exclusion is unavailable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 199; 1 current observation(s).
- `apps/mobile/tests/sync.test.ts::explicit upload registers evidence then snapshot then finalizes and verifies result` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 253; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual secure OS/device restart plus network interruption terminal-state acceptance across supportedAndroid/iOS: JS cryptostore doubles/controller requests do not demonstrate real protected storage/restart/suspension matrix. This is native evidence gap, not an implementation defect inferred from crashflowtags.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 4fbe07f8310020830369082db1137c8576849b2cc493394074e8e03505eb1a19. Actual current source and raw evidence supply this disposition.

## OTGD-001-OPS-006-01 — BLOCKED

Owner acceptance evidence — G-12 documents values and a successful recovery exercise.

Current proof: Mocked maintenance task verification refuses wrong restore command/environment/backup timestamp; this is control-logic evidence only.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `infra/test/test_maintenance.py::test_restore_requires_full_argv_and_recovery_environment` — file SHA `f7222dcd026bcbe70c73279fbb8c75a65bef166e311e93e0729f3d3570b356bf`, line 57; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- G12 specifies operational values, owner/monitoring/backup targets and SUCCESSFUL recovery exercise in real approved deployment: none supplied or authorized here; no live recovery action attempted.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA c6bc2ac0f5283a6f304cd8960e6a15c0b1e661c21ac2b1f355fe8afef190af70. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-001-01 — BLOCKED

Owner acceptance evidence — G-07 authorization and staff readiness records.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-07 authorization and staff readiness records.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 58866215ec2691b548c4076a9b5a7466c9e0da6c318ac3af45e3f377e992a88a. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-002-01 — BLOCKED

Owner acceptance evidence — Outcome manual and data-flow review exclude circular labels.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Outcome manual and data-flow review exclude circular labels.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA d07ae07024263552f85473e19d29bb4d3f4248b14227bba8016e2f21ebf5d76a. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-003-01 — BLOCKED

Owner acceptance evidence — Approved calculation/simulation at G-08; no arbitrary sample guarantee.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Approved calculation/simulation at G-08; no arbitrary sample guarantee.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA b294ac87af2c371ffa413a397e81695cda5e6f046e8d7a3efdb959a0eed4eaf8. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-004-01 — PARTIAL

Owner acceptance evidence — Prespecified strata and exclusions appear in the final report.

Current proof: Fictional final report reconciles six prespecified strata including empty groups and held-out/later rows; HR modes retained as restricted variants.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Genuine qualified final study report includes actual intended route/co-use/device/baseline/population exclusions: engineered cohorts and unverified lock refs do not establish study validation.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fb4ddf463b9fdf413c7795a6680a12463365256b68f1bc01ed491406a865e838. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-005-01 — PARTIAL

Owner acceptance evidence — Independent report reconciles every enrolled check with its disposition.

Current proof: All row denominators, invalid/abstained outcomes, interval draws and prevalence-qualified predictive values remain exact in software evidence; absent authoritative reference labels positive/negative agreement and external authenticityfalse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- INDEPENDENT report reconciles every ENROLLED check/disposition under accepted reference standard: no actual enrollment/assessor/custody report supplied; fictional file provenance is not independent validation.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7c798456266a6508e240d9aa9f92075adf1131d2fd00a0f13a136a00e5b60ee8. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-006-01 — BLOCKED

Owner acceptance evidence — G-09 report states independence, limitations, and deviations.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-09 report states independence, limitations, and deviations.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 22e712537be8dd739cc308a36d24378acd5faa4527c8b9a7c31450f59775d047. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-007-01 — PARTIAL

Owner acceptance evidence — Temporal audit and study report demonstrate the consumer information boundary.

Current proof: Original check target/information-cutoff chronology preserved and future sources/baselines excluded in synthetic temporal audit.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_same_check_observations_and_later_assay_delivery_preserve_original_target` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 319; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_invalid_or_future_source_data_are_rejected_before_fitting` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 297; 110 current observation(s).
- `services/api/tests/test_model_engine.py::test_feature_missingness_and_temporal_baseline_gates` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 410; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Actual complete one-sample/one-task STUDY REPORT demonstrates consumer information boundary for real repeated visits: no independently governed real workflow evaluation supplied.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 22640b7fe3a622af2d38dc48f48bfff7a4c2286defb63afeda0359ca7c4621bb. Actual current source and raw evidence supply this disposition.

## OTGD-001-VAL-008-01 — BLOCKED

Owner acceptance evidence — G-14 documented applicability determination and required evidence.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — G-14 documented applicability determination and required evidence.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA a7073fb5b6d9a4b4bf7da3139a7133a6fdb96ae9be9d337bdbaf9d0b93582dd0. Actual current source and raw evidence supply this disposition.

## OTGD-001-BUS-001-01 — BLOCKED

Owner acceptance evidence — Commercial material avoids an unverified price/performance promise.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Commercial material avoids an unverified price/performance promise.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA c7a597c8f12c456538b69444e0ad22adffeb2b194627308a1ee5e36a3aa71a20. Actual current source and raw evidence supply this disposition.

## OTGD-001-BUS-002-01 — BLOCKED

Owner acceptance evidence — Dated cost model with supplier quotations and sensitivity analysis.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Dated cost model with supplier quotations and sensitivity analysis.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 031760cde1bb2c36cc1b4a4d4e74a56be5ce83e5b1be5a675037b60c06dfedaa. Actual current source and raw evidence supply this disposition.

## OTGD-001-BUS-003-01 — BLOCKED

Owner acceptance evidence — Product decision cites ablation, usability, and cost evidence.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Product decision cites ablation, usability, and cost evidence.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 618d467090fc204315b81951460acc6fae346fcf9d84515eae99424b8f9134f5. Actual current source and raw evidence supply this disposition.

## OTGD-001-DOC-001-01 — PARTIAL

Owner acceptance evidence — Repository review finds no unsupported completion claim.

Current proof: FULLSPEC says proposed targets unmeasured, open gates and incomplete physical product; product audit distinguishes conditional code/default measurement from scientific approval; reconciliation labels tests source-present rather than executed.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Repository-wide review finds NO unsupported completion claim across all current docs/status/screens: this targeted audit does not establish exhaustive repository claims review; old status/task history must remain labeled.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 85b9fd4cd3b1fbbef9b21bc45a021b4bd49c4cde24aa4db032e0177e3a6973af. Actual current source and raw evidence supply this disposition.

## OTGD-001-DOC-002-01 — BLOCKED

Owner acceptance evidence — Gate register contains approver, date, artifact, and decision.

Current proof: External acceptance evidence required by canonical owner/gate; software tests cannot supply it.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Owner acceptance evidence — Gate register contains approver, date, artifact, and decision.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 60a3d8d52c5ad5658d6f398948477be651e7c6f2bb062af0730fc9551801762d. Actual current source and raw evidence supply this disposition.

## OTGD-001-DOC-003-01 — PARTIAL

Owner acceptance evidence — Change-impact checklist and versioned repository history.

Current proof: D004/product-audit/spec-reconciliation and versioned canonical traceability record amendment precedence and change impacts; frozen89 IDs/hashes are preserved.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- ALL dependent contracts/decisions/requirements/verification evidence are updated in ONE reviewed change: active correction writers have material source drift; final exact-revision rerun/review/signoff is pending.

Prerequisite/evidence type: independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 3ba87a6a68e5f1f45f9216e6c8124dd31c145f2ba2cd33aca12385ca7e7e8447. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-001-01 — PARTIAL

PRD acceptance review — | PRD-001 | A valid consumer-format check MUST require one saliva collection and one continuous reaction task. Multiple channels may be measured from that collection. |

Current proof: One specimen lineage and one66trial task independently proven; restricted HRonly research explicitly has no saliva/task and remains separately scoped.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- VALID CONSUMER-FORMAT check requires one collection AND one continuous task simultaneously; restricted research/measurement-draft exceptions must not be sold as consumer-format completion. No integrated consumer-format required-minimum admission assertion shown by these separate bodies.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA c4fd94cb9b73ab3dc0b3b957ec0cb1b3cfe2f791d86b8a7b08f2a9d28b3e77a2. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-002-01 — PARTIAL

PRD acceptance review — | PRD-002 | The check MUST also support guided pupil capture and resting heart-rate capture; ECG MUST remain an exploratory input until its incremental value and hardware approach are justified. |

Current proof: Conditional guided optical/PPG paths retain exact authority and exploratory ECG copy; human ECG remains unavailable without independent state verification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_human_ecg_state_verification_is_unavailable_even_when_declared_verified` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 470; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Full guided pupil+resting cardiac support and ECG incremental-value/hardware justification: native/physical optical/rest/calibration and independent ECG benefit remain external; no complete supported-device journey shown.

Prerequisite/evidence type: physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5a8c04723dd6f25bbba4994c8c14acecde8bd5b9f140fe926dc1875ed9ea8c9b. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-003-01 — PASS

PRD acceptance review — | PRD-003 | P0 and P1 MUST produce measurement-only outputs, never an intoxication probability. |

Current proof: P0/ordinary measurement workflows finish measurement_only with null probability and explicit fictional provenance; later authorized1.1 research exception is separately gated, not a change to P0/P1 output.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_end_to_end_measurement_only_and_owner_isolation` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 197; 5 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3419344a63730e1b3c6c7e92049a766fd6028ad1b8273263b4098eaf93a18990. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-004-01 — PASS

PRD acceptance review — | PRD-004 | A P2 probability MUST require an authorized research session, an `active_research` model, a compatible feature contract, and all model-required valid channels. |

Current proof: Owned fictional independently released P2context admits strict1.1 only aftercurrent model/acquisition/contractscope; wrongconsent/generation/protocol/cohort/provenance/quality/timing/artifactorcalibration yields refusal/nullscore. Legacy0.1 blanketrefusal remains scoped toolderformat.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 875d86515f087e851017bee79de27d4a78274feeedc9aca7f7a6c0f89ae3a123. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-005-01 — BLOCKED

PRD acceptance review — | PRD-005 | The future impairment endpoint, intended population, operating threshold, and acceptable error rates MUST be selected before confirmatory evaluation. |

Current proof: File-level locked plans/digests and postlock mutations enforced; tooling explicitly historical_lock_or_blinding_provenfalse.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_report_cannot_rebind_tampered_training_plans_or_temporal_order` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 338; 55 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Endpoint/population/threshold/acceptable errors selected BEFORE actual confirmatory evaluation by responsible experts: original independent study/G01/G08 history absent; editable timestamps cannot establish it.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA d52433ef7fec8f4a55ab2fb7ab9bde30c7edc677bb87760f38d9404c48cea0ee. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-006-01 — PARTIAL

PRD acceptance review — | PRD-006 | A model result MUST NOT be presented as proof of cannabis causation, a legal determination, or clearance to drive. |

Current proof: Representative rendered claims have no driving clearance or diagnostic interpretation and expose named fictional research endpoint/time.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).
- `apps/mobile/tests/research-result.test.ts::actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 147; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Every model result presentation excludes cannabis causation/legal clearance/unsupported certainty: complete result/notification/error copy inventory and independent interpretation not provided.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 00000d8edf4f03c5cef29d10b011d62ae86b8eb626cc343e8d1d51434444d6bd. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-007-01 — PASS

PRD acceptance review — | PRD-007 | The product MUST retain distinct invalid, inconclusive, measurement-only, and research-estimate outcomes. Missing information MUST NOT be interpreted as a normal measurement. |

Current proof: Measurement_only/research_estimate/inconclusive/invalid retained separately; unsupported/uncertain inputs yield null probability/features instead of healthy values. New1.1 valid research reader and strict legacy refusal are both preserved.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_end_to_end_measurement_only_and_owner_isolation` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 197; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).
- `apps/mobile/tests/research-result.test.ts::a verified uncertainty band requires null abstention rather than a probability or optimistic classification` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 221; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA ecb30cbf7973d4e16fa1bfcd576a0f4b78d35eac4eaf5a5950e7b0bbb31d6271. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-008-01 — PASS

PRD acceptance review — | PRD-008 | Alcohol MUST remain a separately measured and separately reported channel; cannabis physiology MUST NOT substitute for a breath-alcohol measurement. |

Current proof: Separate alcohol channel retains typed evidence and mg/L label; no physiology-to-breath conversion or invented calibrated value; missing driver refuses before hardware.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).
- `apps/mobile/tests/export-projection.test.ts::every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 29; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::fresh absent-breath-adapter capability overrides stale cached availability before any hardware invocation` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1689; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 5256ef35157902790c03cc190d4a0a1b8d64f0003a624f877f3ff27f460eddf1. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-009-01 — PASS

PRD acceptance review — | PRD-009 | Standardized session orchestration | P0 MUST establish a complete synthetic workflow with unique attempts, timestamps, quality, and terminal states. |

Current proof: P0 synthetic workflow creates/scopes attempts/timestamps, retains simulated source and invalid/terminal states, local immutable save and exact export finish measurement_only. Physical task unavailability remains explicit.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 87; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 24c39ca8b9070b656142f679fbbd2c746dde80622d928684ad59ca56d8a55b9f. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-010-01 — PARTIAL

PRD acceptance review — | PRD-010 | Quantitative saliva interface | P1 MUST establish reliable specimen handling and a reference-laboratory comparison before any portable concentration claim. |

Current proof: Reference-lab collection instructions/form metadata, independent staff import custody and no portable concentration fabrication proven in fictional software.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_collection_chronology_and_handling_are_actual_events_not_form_progress` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 535; 35 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Reliable specimen handling AND reference-laboratory COMPARISON before portable concentration CLAIM: no actual specimen recovery/stability/paired-assay evidence supplied; G02/G03/G09 remain open.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9c09d25961374e6718eefa911a162860d575843d50382312c5062f16a0f0defb. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-011-01 — BLOCKED

PRD acceptance review — | PRD-011 | Parent THC channel | P1 MUST evaluate delta-9 THC first. Selection of additional channels requires analytical feasibility and added-value evidence. |

Current proof: Software keeps analytes/methods distinct and refuses incompatible imported evidence; this does not select or qualify chemistry.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_lab_handoff.py::test_import_rejects_forged_or_incompatible_analytical_evidence` — file SHA `104d40bebc567b3288972a2a1916655926ff69bd2a68b72ef61c67f4135f9492`, line 304; 40 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- P1 evaluate parentdelta9THCfirst; additional channel feasibility/added-value selection: no dated actual channel selection/analytical report supplied; requires ANL/G02/G03.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 7d55f320a9cb3362d434722db0a1a5db111c26244a61b97b2a13a86871778ae4. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-012-01 — PARTIAL

PRD acceptance review — | PRD-012 | Additional saliva metabolites | THC-COOH and 11-OH-THC SHOULD be investigated; neither is promised as a functional cartridge channel in v0.1.0. |

Current proof: Unmeasured THC-COOH/11-OH-THC remain null/not_measured, never promised as acquired values.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::synthetic concentrations preserve unknown metabolites as null, with exact pg/mL conversion` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 222; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- SHOULD investigate candidate metabolites: no actual analytical feasibility investigation adopted; data support alone is not a functional cartridge promise or qualification.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2f08638f4d7fe52ca47897fe15a7aad3dea09c92990c07ccf80e5f829f3ee211. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-013-01 — PARTIAL

PRD acceptance review — | PRD-013 | One repeated-trial game | P0 MUST support the task contract; P2 MUST evaluate reliability and independent predictive value. |

Current proof: P0 one continuous task exact6practice/60scored schedule/feature contract and boundary vectors execute native core.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAllLiteralTrialBoundaryVectors` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 33; 2 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

Exact unproved clause(s):

- P2 evaluate reliability AND independent predictive value: host/task contract tests cannot provide genuine repeated-person reliability or independent endpoint incremental value.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5a339e02b91a24e620cb3fb7e2a002989faedf19b70c0e4923628cb8576db0ce. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-014-01 — PARTIAL

PRD acceptance review — | PRD-014 | Dynamic pupil measurements | P1/P2 MUST establish acquisition quality, valid units, optical controls, and repeatability before features enter a model. |

Current proof: Unqualified optical geometry/response withheld; incompatible model quality/units/current authority refuse instead of model admission.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/eye-acquisition.test.ts::actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 33; 1 current observation(s).
- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- P1/P2 establish acquisition quality, valid scale, optical controls and REPEATABILITY before model use: physical G04 evidence/calibration/repeatability missing; structural fixtures cannot supply it.

Prerequisite/evidence type: physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5ed020f1d9f43a795e0a76e1eb86445ad1f4dacaf181c46ab041e5909b423a6e. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-015-01 — PARTIAL

PRD acceptance review — | PRD-015 | Heart rate and exploratory ECG | Cardiac capture MUST preserve signal quality and context; an ECG-only benefit MUST be measured by ablation. |

Current proof: Cardiac source/quality/instruction context and strict signed proof retained; software existing mode includes ECGremoved comparison and no diagnostic claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_cardiac_authority.py::test_http_signed_hr_only_research_worker_preserves_flags_and_snapshot` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 190; 5 current observation(s).
- `apps/mobile/tests/participant-acquisition.test.ts::actual Python protocol, immutable acknowledgement, specimen and imported report preserve separate truthful lineage` — file SHA `6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6`, line 87; 1 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 524; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- ECG-only benefit MEASURED by independent ablation and actual signal quality/context qualification: engineered ablation metrics do not establish physiological/incremental benefit.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f8195fa9c0fc70367deae41c8bc4854ebc469e17b7416eaf97be743a7fc0a816. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-016-01 — PASS

PRD acceptance review — | PRD-016 | Profile and use history | The app MUST preserve source, measurement date, units, and unknown values; demographics MUST NOT determine an assumed clearance rate. |

Current proof: Optional unknown/declined/source/date and SI fields remain explicit, frozen original timestamp survives start; model predictors are explicit actual task/assay/HRdelta rather than demographic clearance. Scoped source/unknown handling proven.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/profile-form.test.ts::optional blank demographics stay null and unknown remains distinct from declined` — file SHA `0c2b5f39798e297673af92b008243169f4628c08438fc0be9defe065da2dc30e`, line 56; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::profile converts SI units and rejects ranges, relative time and unknown enums` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 131; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::check freezes original profile timestamp and recomputes elapsed use at its start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 152; 1 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA b2cd766ebbf1aed130eace83e8325785fcb496da5502316e271a919d8000ee65. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-017-01 — PARTIAL

PRD acceptance review — | PRD-017 | Separate alcohol channel | The design SHOULD reserve integration capability; alcohol performance claims require a calibrated breath system and dedicated validation. |

Current proof: Separate future integration DTO/channel reserved; mg/L and unavailable qualification explicit; no generic missing adapter manufactures breath reading.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::alcohol copy remains accurate for measurement, guest and admitted research contexts` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 154; 4 current observation(s).
- `apps/mobile/tests/export-projection.test.ts::every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence` — file SHA `4707168f94a1706dd5f86d1014835651d57eba5be5d1093d2455bfd3d03732c2`, line 29; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::fresh absent-breath-adapter capability overrides stale cached availability before any hardware invocation` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1689; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Any alcohol PERFORMANCE claim requires calibrated instrument/dedicated validation: no actual breath instrument/qualification evidence, and complete commercial claims inventory not reviewed. No such approval granted.

Prerequisite/evidence type: physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8fbfc3c9555064e569cb968cb9195d1962bc7ec0a301f066ad1d663b0108ad5d. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-018-01 — PASS

PRD acceptance review — | PRD-018 | Versioned research dataset | P2 MUST support reconstruction of the exact specimen, task, device, calibration, feature, and model versions. |

Current proof: Exact frozen dataset/acquisition/task/feature/model references, source manifests and full result authority hashes reproduce deterministically; forged version/input links reject. External authenticity remains explicitly false.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 137; 20 current observation(s).
- `apps/mobile/tests/research-result.test.ts::changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 166; 1 current observation(s).
- `services/api/tests/test_model_engine.py::test_training_evaluation_policy_and_result_proof_are_bound` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 437; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 348e67b5138eaeddfc3fcbad8cfbc83407120dcd33cb6dfec0f4fc9a77a8ecda. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-019-01 — PARTIAL

PRD acceptance review — | PRD-019 | Quality-aware research result | Inference MUST enforce the release manifest and required-channel rules without fallback to an incompatible model. |

Current proof: Current requiredchannels, exactartifactfeatures and personalizedbaseline are enforced; incompatible/legacy/mixedscope refuses rather than silently reusing or zerofilling fullmodel.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_engine.py::test_every_acquisition_gate_has_rejection` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 364; 90 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_actual_artifact_not_just_required_channels_is_hr_only` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 277; 10 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_hr_scope_rejects_mixed_rows_and_unprespecified_legacy_evidence` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 302; 20 current observation(s).
- `apps/mobile/tests/research-result.test.ts::personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 245; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Complete independently admitted missing-channel variant admission and selection must remain bound to approved provenance, tuple, freshness and delivery. Current pending-chemistry required/optional scope refusal/admission and no-invented-value assertions close the previously absent scope branch; a complete independently admitted optional-pending result pipeline is not executed.

Prerequisite/evidence type: software_integration_evidence, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 1a3d3472da521eccf38bc698d415acf1410e7affad3c60d3c4cbeb842c37d629. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-020-01 — PARTIAL

PRD acceptance review — | PRD-020 | Understandable session feedback | The app MUST distinguish capture success, analysis availability, and a research prediction. |

Current proof: Pendinglab display has noconcentration, savedguest showsmeasurementonly, strict actualHTTP/worker fixture carries independently bound researchstate rather than deliverytime.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::pending laboratory UI preserves the draft, refreshes actual admitted analysis and requires explicit cancellation without inventing chemistry` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1041; 4 current observation(s).
- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/research-result.test.ts::actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint` — file SHA `d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682`, line 147; 1 current observation(s).
- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- A complete executed participant RESULT/HISTORY display comparison of capturesuccess/analysisavailability/researchprediction undercurrent1.1 scientificstate and deliverystatus: separate widgets/DTOchecks do not alone establish endtoend presentation. No clinicaltruth claim inferred.

Prerequisite/evidence type: software_assertion_or_integration_evidence, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA faf753b25ebc23c0f17a57cc9868b7aaa91473aa66f1771a267089a416b8381d. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-029-01 — PARTIAL

PRD acceptance review — | PRD-029 | A person can enter guest practice or authenticate, recover an interrupted sign-in, refresh safely and sign out with truthful remote-revocation status. Environment/account partitions and retained signed-out data stay isolated. | SEC-002/004/007; AND-ONB-001–006; AND-AUTH-001–007; AND-ENV-001/002 |

Current proof: PKCEstate/verifier/issuerbinds identity, canceled/stale callbacks donotexchange, concurrentrefresh singleflights and retains originalrefreshcredential; failedlogout and replacementlogin preserve truthful unconfirmedremote revocation and currentidentity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::PKCE callback binds state and verifier and credential restore uses verified API identity` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 122; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::cancelled, wrong-state, duplicate and invalidated callbacks cannot exchange a code` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 147; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::one current refresh request preserves an omitted refresh token and every waiter receives the same access token` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 188; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::a failed API logout still revokes the captured provider family and reports the unconfirmed receipt` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 243; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::a replacement login during local sign-out still revokes only the captured old family without old UI work` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 288; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Interrupted sign-in/recovery plus environment/accountretained signedoutdata and actual OS securestorage/browserroundtrip isolation on supportednative platforms: these modeledcallback/store traces donot close complete native identitymatrix.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 798c9f4d1e82f662ecc0680e76e369cc4c444c8d3ef609d308c006342195bca3. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-030-01 — PARTIAL

PRD acceptance review — | PRD-030 | An invited eligible account can review exact study consent and current channel availability; sign-in, age, a guessed study ID or a checkbox cannot create research authority. Withdrawal stops local study work immediately and preserves its durable receipt. | SEC-002/003; MOD-008–010; AND-STUDY-001–006; PAI-001–008 |

Current proof: Current document consent is durable and exact; wrong versions/withdrawn consent refuse current start, cached invitation alone does not authorize sensing. Actual controller locally stops active fictional reader on offline withdrawal, invalid/null measurement, exact durable pending request body/key and truthful pending membership; later same intent confirmation leaves prior verified upload blocked and no capture restart.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 410; 1 current observation(s).
- `apps/mobile/tests/study-consent.test.ts::only an active exact affirmative receipt suppresses new study consent` — file SHA `d862ef179f94af0018561a8c6dfa62972dcdd2d89c1e7060ea6a740552807481`, line 25; 1 current observation(s).
- `services/api/tests/test_consent_versions.py::test_updated_document_has_new_immutable_receipt_and_replay_keeps_current_pointer` — file SHA `bdfbbe725088b6adc5e01d3033fd7bfc2ae5f1424c966c3c3ef92249ece1b963`, line 45; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_config_retirement_and_withdrawal_after_acknowledgment_refuse_fresh_start` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 418; 5 current observation(s).
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/semantics/offline_withdrawal_probe.fragment.ts::supplemental offline active reader capture withdrawal retains exact privacy intent and later receipt without restoring uploads` — file SHA `24b54b1005e9a9e44e3dd5dea4f69e4447a36b892726e7186502edc446a713cf`, line 1; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/supplemental/semantics/offline-withdrawal-observations.json` — SHA256 `d1301a78b47f955bf914d70b1d7dde52e85bf2f06ef9f259b5e846b9a313194b`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Guessed study ID or a checkbox must never create research authority, while an invited eligible account can review exact document/current channel availability. Current server consent/retirement and client exact receipts are tested; the explicit guessed-ID/checkbox creation-negative conjunction is not directly asserted in this row. Offline active-work withdrawal, exact pending intent, truthful unknown outcome and later same-key receipt are now directly proved.

Prerequisite/evidence type: software_authority_boundary_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Fictional software fixtures; no installed OS, physical stop, real participant consent, assay qualification or clinical/model approval. Supplemental probes do not replace full local/CI gates.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 43cd4f7557f60a9fe1fe01c24f9a99d8e387a459a7525e962d463872aa1ea3b4. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-031-01 — PARTIAL

PRD acceptance review — | PRD-031 | A check freezes its confirmed optional profile/context, one-sample/one-task information boundary, original target, all attempts and selected evidence. Interruptions and linked replacements preserve original records. | ANA-001/012; APP-001–008; OPS-002–005; AND-PRO-001–007; AND-CHECK-001–008 |

Current proof: Start freezes optional context/original target, interrupted attempts retain disposition, specimen replacement/correction links preserve originals.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/domain.test.ts::check freezes original profile timestamp and recomputes elapsed use at its start` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 152; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Integrated one-sample/one-task consumer information boundary and ALL selected evidence across every native modality/replacement transition: partial modality-specific assertions do not close full integrated consumer-format matrix.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 0af369ee980cb6b14ba98c2996baed2d7950cb9394ad04c1cf907a8b83be4954. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-032-01 — PASS

PRD acceptance review — | PRD-032 | Native reaction acquisition preserves deterministic practice/scored schedules, actual native events, missingness and immediate stop behavior; build success and clock resolution do not establish physical timing qualification. | APP-004–008/014; AND-TASK-001–008; G-06 |

Current proof: Native core deterministic scored/practice schedules, literal events/quality/missingness and terminal once rules pass; controller dispatches cancellation before delayed device stop and retains immutable terminal. This scoped software proof makes no supported-device physical timing claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testFrozenLiteralSchedulesAndHashes` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 19; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testAggregatesAndPracticeExclusion` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 77; 2 current observation(s).
- `apps/mobile/modules/reaction-task/tests/swift/ReactionCoreTests.swift::testQuantileBudgetsDrainAndTerminalOnce` — file SHA `9d845ce1dd56be186b8acc826333954e53e184764749d07324781c90a28c3abc`, line 90; 2 current observation(s).
- `apps/mobile/tests/controller.test.ts::native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 847; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596297227/ios-hosted-native.xml` — SHA256 `58e7cf359c085a84a9ff299785ea51a943e0c972f7e6ce652f3126aacb9f3745`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12596147789/ios-native.xml` — SHA256 `6e7f89715db81a6a09e132f5acf86cd0c57c43dcbede35b41265fbada7be8e7b`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA aab840bd3b515bf649ee9eb854a7209f0b58c965156b3b211ba3260a33ac9a48. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-033-01 — PARTIAL

PRD acceptance review — | PRD-033 | Device discovery, verified binding and fresh scoped starts distinguish a working connection from a qualified channel. Protected BLE, actual adapter inventory, quality, cancellation and replay/origin fences apply to conditional reader capture. | HW-003/004/007/012; SEC-004; AND-DEV-001–008; CAN-SR-001–011; VPPG-001–007 |

Current proof: Binding proof/current connection, signed fresh scope, replay identity and exact adapter inventory/quality preserved in host/controller/HTTP fixtures.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/src/device/tests/physical.test.ts::actual backend bound-reader HTTP fixture passes strict physical token and exact material digest` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 656; 1 current observation(s).
- `apps/mobile/src/device/tests/protocol.test.ts::identity, changed message ID content and replay sequence are independently checked` — file SHA `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`, line 67; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::binding reconnect reconciles old receipt then requires a new device proof in the current connection` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1183; 1 current observation(s).
- `services/api/tests/test_operator_governance.py::test_current_device_calibration_binding_and_software_inventory` — file SHA `0a942e16b6c648daf32f044b550bbcb25f68fed8990b1c934959d7496cdbf600`, line 740; 5 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Protected BLE confidentiality/pairing/bond resumption and real same-address reconnect/origin failure matrix: physical stack validation and per-device provisioning evidence absent; host tests cannot certify them.

Prerequisite/evidence type: physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8cd1840f811fe1d6c1914093c930b78482f4d85c369343f42834f44d7be1a20f. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-034-01 — PARTIAL

PRD acceptance review — | PRD-034 | Saliva collection/import, optical capture and selected PPG/exploratory ECG have explicit pending, unavailable, invalid and permitted retry paths. Declarations, approved software and signatures do not qualify an assay, optics, electrical setup or sensor. | ANA-001–012; HW-005–009; APP-009/010; AND-SAL-001–007; SALCOL-001–008; AND-EYE-001–007/101–106; AND-HR-001–007; AND-ECG-001–007 |

Current proof: Explicit saliva pending/import/retry, optical authority, SDK invalid evidence and unavailable human ECG paths proven without fabricated assay or safety proof.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_actual_http_collection_staff_report_import_refresh_and_finalize` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 906; 5 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_invalid_collection_preserves_failure_and_linked_retry_allocates_new_sample` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 436; 5 current observation(s).
- `apps/mobile/tests/eye-acquisition.test.ts::feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock` — file SHA `88e39f5aa09db012ecee16274b7a54f938f85f5f1e6df42ecfb5e1f72172d8a5`, line 230; 1 current observation(s).
- `services/api/tests/test_participant_acquisition.py::test_human_ecg_state_verification_is_unavailable_even_when_declared_verified` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 470; 5 current observation(s).
- `apps/mobile/src/device/tests/physical.test.ts::actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence` — file SHA `6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc`, line 822; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- All modality-specific interruption/retry/pending/unavailable states and NATIVE parity exact cases remain not fully executed; PAI008 wall-clock invalidation mismatch remains open on frozen28. Physical/science qualification is separately absent.

Prerequisite/evidence type: software_assertion_or_integration_evidence, physical_hardware_execution, study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5f62bc8bd26e375f19579152cfaf78b04d7c5b4cc2b247c1784093c594f0addf. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-035-01 — PARTIAL

PRD acceptance review — | PRD-035 | Protected local save precedes a separate explicit account upload; restart, lost receipts, bounded retry and conflicts preserve ownership, original times and immutable evidence. Permission failures and retired generations cannot be repaired by automatic reupload. | SEC-003/004; OPS-002–005; AND-SYNC-001–007; AND-CHECK-006; shared contracts §§2–5 |

Current proof: Local immutable save occurs before explicit queue; upload ordered context/evidence/snapshot/finalize with stable keys; lost acknowledgment reconciles unchanged and never resumes hardware.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 7; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1448; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::lost accepted instruction reply is reconciled with its original body and key without restarting hardware` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 624; 1 current observation(s).
- `apps/mobile/tests/sync.test.ts::explicit upload registers evidence then snapshot then finalizes and verifies result` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 253; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Protected native storage/restart/permission failures/retired-generation no-auto-reupload across full supported device matrix: native hardware/OS checks not supplied by these source fixtures.

Prerequisite/evidence type: native_os_execution, physical_hardware_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 7d991a1ef2e3966445e7008ccd9549dc57bd9151c017f4b416d099a4fb110009. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-036-01 — PASS

PRD acceptance review — | PRD-036 | History/results show the actual scientific state separately from delivery, preserve qualifiers and old acquisition times, and navigate immutable original/replacement and same-specimen report-revision lineage. | APP-012/013; MOD-013; AND-HIST-001–007; AND-RES-001–007; report-revision and replacement-links contracts |

Current proof: Actual browser replacement links navigate both ways without changingoriginal; qualifier/null/original units and distinct collection/measurementtimes visible; correction/reanalysis preserves original hash/target and linked resultlineage. Scientificmeasurement status stays independent of lateranalysis/deliverytime. Scoped softwaredisplay/custody proven.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 142; 4 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::below LOQ displays the supplied bound without creating a concentration or rounding it to zero` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 23; 1 current observation(s).
- `apps/mobile/tests/measurement-format.test.ts::original report units, laboratory correction, matrix and separate times remain visible` — file SHA `f9506b63c3317bd24d653230d67e4913d63cdf527d1ff849e9ccd534770532c2`, line 99; 1 current observation(s).
- `apps/mobile/tests/report-revisions.test.ts::actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings` — file SHA `4d1d9f5becc44e8d716ab339de02cdd5c3afde155d2afbbdec5957c33114c3fb`, line 46; 1 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA c31620eeb75ea711c14ec4c9917458f256d23e96dce61ad28eb1aebdec44a818. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-037-01 — PARTIAL

PRD acceptance review — | PRD-037 | Optional eye/ECG recording and upload default off, have distinct reviewed purposes, retain exact receipts and expire under original retention deadlines. Revocation stops capture before cleanup; pending quarantine/cleanup is visible. | SEC-003–005; AND-RAW-001–007; AND-EYE-006/106; AND-ECG-007; raw-recording-retention contract |

Current proof: Recording/upload switches defaultoff and require separate notice; recording dependency/current policy enforced, local stop fence overrides prior receipt while cleanup visiblypending.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1111; 4 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::local revocation fence overrides old confirmed grant without claiming cleanup completion` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1230; 4 current observation(s).
- `apps/mobile/tests/raw-recordings.test.ts::default off, local-only opt-in, upload dependency, policy expiry and pending stop fences remain distinct` — file SHA `f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08`, line 77; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Full recording retention original-deadline, immediate capture stop and real native quarantine/cleanup through OS restart/backend backup deletion: component/control checks do not close entire native/live retention matrix.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9d910d35ca1b8d96c46d0c5b919b1c20a8ab776c9c58bedb782cbf1fb90e8287. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-038-01 — PARTIAL

PRD acceptance review — | PRD-038 | The owner can create a bounded exact-scope structured export, optionally include separately authorized retained raw sources, verify and deliberately share it. Downloads require current authority; expiration, revocation and temporary-file cleanup remain explicit. | SEC-002/005/007; AND-EXP-001–007; RAW-EXP-001–008; AND-RAW-008 |

Current proof: Exact structured single scope archives/hashfiles verified before deliberate share; separately authorized raw sources require current matching scope; revoked job has no download path and expired sources disabled.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/mobile.spec.ts::guest completes a measurement-only check, exact export and privacy/settings journey` — file SHA `b98ad26a21ad603dea26e39747ff25cb8cf7456bb586a0741bd32321cf29d24b`, line 6; 4 current observation(s).
- `apps/mobile/tests/raw-export.test.ts::actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources` — file SHA `c68c9146811b6261e384bef9759f0bde4a8a08f3be26391c888da40700d09359`, line 65; 1 current observation(s).
- `apps/mobile/e2e/raw-recordings.spec.ts::expired or unselected raw export sources remain unavailable while structured export stays separate` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 1304; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595253497/reports/atdd.xml` — SHA256 `4487aa6116b629a25830ef3c4a32a4b11b17180cfdccb4ab8e10fcd2a207a305`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/atdd.xml` — SHA256 `8f7f6be05f22df4eeedb2681d2f568c59457dd99fea80af10f687185d18ef410`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- All bounded-size failures, current download reauthorization, revocation races and actual OS temporary-file cleanup across supported Android/iOS: typed fixture/archive/UI proof is not full live/native export lifecycle acceptance.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 5655c1653026d9f17c8e520cd7a6141a140af9763f18d6d2bed5f76aebfcb40a. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-039-01 — PARTIAL

PRD acceptance review — | PRD-039 | Local clear, cloud-data deletion, account deletion and withdrawal show distinct scopes and honest asynchronous receipts. Generation barriers and independent retained recovery evidence prevent resurrection; study recovery requires fresh independent reapproval and participant consent. | SEC-005/007; OPS-003–006; AND-PRIV-001–007; RECOVERY-001/002; platform contract |

Current proof: Recovery seal admits exact fresh study scope only, stale approval/consent/foreign/tampered seal refuses; withdrawal prevents queued consent revival and reinvitation required.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_recovery_scopes.py::test_fresh_registry_reapproval_seal_allows_only_exact_study_and_new_consent` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 90; 5 current observation(s).
- `services/api/tests/test_recovery_scopes.py::test_no_stale_or_mutated_authority_reopens_study` — file SHA `3fe448145c086a5441b96caeffa0fa006f24a0b18396da3ac60462fba4850344`, line 121; 45 current observation(s).
- `apps/mobile/tests/study-consent.test.ts::withdrawal requires a fresh invitation, and local pending withdrawal blocks reconsent` — file SHA `d862ef179f94af0018561a8c6dfa62972dcdd2d89c1e7060ea6a740552807481`, line 53; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::maintenance pauses queued consent and withdrawal prevents its later automatic transmission` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 531; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Full distinct local/cloud/account deletion/withdrawal receipts and live independent retained recovery/backup erasure/no-resurrection exercise: mocked recovery object store and isolated state helpers do not establish actual deployment recovery.

Prerequisite/evidence type: deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 39ad9932997e43249d6c6ef8d042051e09979f80e5d1473601c981414e240a37. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-040-01 — BLOCKED

PRD acceptance review — | PRD-040 | Instructions, navigation, errors and privacy controls support specified Android/iOS accessibility and permission recovery. Changes to timed-task presentation/input retain their separate compatibility and qualification boundary. | APP-014; AND-SET-001–007 and feature-specific parity requirements; shared contracts §9 |

Current proof: Software controls display human ECG unavailable and background resets preparation; browser/host test is not native accessibility qualification.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/e2e/raw-recordings.spec.ts::interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG` — file SHA `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`, line 753; 4 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/components.xml` — SHA256 `a137af31ada043a249ad62b8720ab6b6a0dc7a6e1d4991d5336f7aa5b65e3e31`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595408442/reports/components.xml` — SHA256 `e7e7d926b5f3a9b2a7ed5cebe1aef20a55d8735c6b2886248edf6d77955ea580`.

Exact unproved clause(s):

- Specified Android/iOS accessibility/navigation/errors/privacy/permission recovery and timed-input adaptation revalidation on supported device matrix: actual OS assistive-technology rows and compatibility approvals absent.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 3a8223bbe129363af8140fdc7fb75073b457b1dc232ea0382ac1441233394868. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-041-01 — PASS

PRD acceptance review — | PRD-041 | Independently governed operator releases can admit the exact conditional research software, including only explicitly approved model variants and baseline scope. Measurement-only remains default; the restricted HR-only evaluation mode discloses absent multimodal comparisons. | MOD-001–015; VAL-001–007; OPERATOR-AUTHORITY-001–009; MODEL-001–006; EVAL-001–008 as modified; HR-AUTH-001–008 |

Current proof: Current typed independentoperator releases gateconditional1.1software; exactHRonly/baselineproofs and explicit mode retained; absent multimodalpairedcomparisons disclosed; guest/ordinarydefault measurementonly. None of the fictionalrelease/fit tests authenticate realstudy/clinicalauthority.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_http_native_evidence_real_registry_lifecycle_worker_and_research_read` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 396; 5 current observation(s).
- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `services/api/tests/test_cardiac_interval_governance.py::test_hr_only_model_policy_release_and_retirement_recheck` — file SHA `542124d8874ec1307305a677039b9d5b36355778cc06c9ccb8799af5cc8e14ff`, line 108; 5 current observation(s).
- `services/api/tests/test_cardiac_authority.py::test_personalized_http_capture_resolves_its_own_original_baseline_and_rejects_changed_signature` — file SHA `96d34c6540fcdbaedcd35a347c30661bbe94e9bb5582a7b6c5ecd42ec247695a`, line 395; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).
- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA a83fc7389d7b802640decbf2a26a23b02228736baf3ad675d3027ef4e9654b4c. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-042-01 — PARTIAL

PRD acceptance review — | PRD-042 | Isolated fictional previews and reviewable local/QA/prod/store delivery tooling preserve exact source/artifact identity, environment and uncertain outcomes. Prepared software, submitted artifacts, hosted access, public availability and scientific qualification remain separate evidence. | HW-002; SEC-001/004; OPS-001–006; AND-ENV-001–007; AND-PREV-001–003; WEB-DEP-001–010; CLOUD-DEP-001–011; PREVIEW-001–003; STORE-001–018 |

Current proof: Fictional preview isolates credentials/network/device and remains measurementonly; verified submission receipt explicitly public_releasefalse/storeavailabilitynot_verified, changed build/config refuses.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/hosted-preview.test.ts::hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service` — file SHA `7fff06703afe20aa97dba60c4dc5c3d0ac72ba962cc1f2b6b63a56c6ade374cb`, line 11; 1 current observation(s).
- `services/api/tests/test_mobile_store_release.py::test_actual_submission_receipt_never_means_public_store_availability` — file SHA `6e39fe7f435848bc9f1c4b033695e11dfb40b821e845d5f397c3a3ca9a3bb13d`, line 428; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Complete tooling source/artifact/environment and uncertain-outcome assertions across every local/QA/prod/host/store delivery boundary remain broader than the isolated-preview and submission-versus-availability checks. Current all7 local and14 CI gates pass; no target deployment, store signing/submission or public availability is claimed. Existing detailed delivery-case assertions may compose additional software proof; their presence is not inferred from the aggregate.

Prerequisite/evidence type: software_toolchain_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA f6068d2d71785021cf86518c1c2b75f372e389fbe0077267d8153e87f7d7ed9a. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-021-01 — BLOCKED

PRD acceptance review — | PRD-021 | Analytical usefulness | Compare each intended cartridge channel with a traceable reference method over a prespecified range, including censored and invalid results. Freeze acceptance limits before qualification. |

Current proof: Strict software can retain invalid/censored metadata without invented numbers; no analytical performance is established.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_participant_acquisition.py::test_collection_rejects_forged_analytical_authority_and_invalid_metadata` — file SHA `70585678405b2ba85fc9cf53d515c327118bd63b74b16fee2cd5ce6caa8a647a`, line 388; 60 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Compare EVERY intended cartridge channel with traceable reference across prespecified usable range including censored/invalid; freeze limits BEFORE qualification: actual assay/reference paired data and G03/G09 reports absent.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 31fa935378e7111fe1f8416a38cbbbdd8632b8e5723ea65df6470707adacc939. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-022-01 — PARTIAL

PRD acceptance review — | PRD-022 | Independent prediction value | Compare chemistry alone, app signals alone, and the combined model against the same independent outcome. Require evidence of useful incremental benefit. |

Current proof: Tooling compares chemical/app/combined/ECGremoved on matched heldout rows with full invalid/abstention denominators and prespecified strata.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_real_logistic_fitting_is_train_only_deterministic_and_engine_compatible` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 225; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_censored_invalid_and_abstaining_rows_stay_in_every_matched_denominator` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 255; 5 current observation(s).
- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Require USEFUL incremental benefit against SAME INDEPENDENT real outcome: fictional trainable cohorts/unauthenticated endpoint refs cannot establish that scientific result.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 259d4a6ac8c8852fbec949a953eca7d1c4119f12b9d21659793b25038e9548a7. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-023-01 — BLOCKED

PRD acceptance review — | PRD-023 | Single-check usability | Measure completion rate, duration distribution, retries, specimen failures, camera failures, and task interruptions using the intended workflow. |

Current proof: Individual software retries/failures preserve lineage; no product usability result inferred.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/acquisition.test.ts::unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1114; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- MEASURE completion rate/duration distribution/retries/specimen/camera/task failures in intended workflow: no independently collected representative human-factors/user-study dataset or G10 acceptance supplied.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 1850f572d80fbc61878c2789e87c7f9e3bd846b8add21ce8301bd10a0749ed7c. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-024-01 — PARTIAL

PRD acceptance review — | PRD-024 | Generalization | Report errors and calibration for held-out people, later sessions, supported devices, consumption routes, use-frequency strata, and first-use versus personalized modes. |

Current proof: Software heldout/later-session partitions and six strata reconcile and trained HR artifacts ignore heldout labels/features, explicit population/personalized modes retained.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_subgroups_reconcile_all_rows_and_predictive_values_are_prevalence_qualified` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 598; 5 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_held_out_hr_values_and_outcomes_cannot_affect_training` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 221; 20 current observation(s).
- `services/api/tests/test_model_evaluation_cardiac.py::test_raw_and_personalized_hr_training_reproduces_runtime_projection_and_report` — file SHA `61c92b0c9d5d91f6a486626ba778e8f2a9229a22837eaa456c7e217664700b83`, line 149; 20 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- GENUINE generalization errors/calibration across supported devices/routes/frequency and first-use/personalized cohorts: synthetic partitions and example metrics do not establish independent external validity.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA a175fc17176719241987ce55df947f24362420fffd1e945b67917d805d1ae98e. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-025-01 — PARTIAL

PRD acceptance review — | PRD-025 | Operational reliability | Measure record completeness, upload reconciliation, recovery after interruption, and traceability of finalized results. |

Current proof: Modeled explicit delivery/retry and interruption/correction preserve record keys/originals/provenance; local state and finalization scopes are distinct.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/sync.test.ts::explicit upload registers evidence then snapshot then finalizes and verifies result` — file SHA `fdecf6e32f0caa79633a66c7ac11f3da9504e497c6c42739a6aa4a8e8956a202`, line 253; 1 current observation(s).
- `apps/mobile/tests/acquisition.test.ts::unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection` — file SHA `fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28`, line 1114; 1 current observation(s).
- `apps/mobile/tests/domain.test.ts::process interruption preserves invalid task evidence with null aggregate features` — file SHA `e71b15500f0d22ff8859b950cdda014ba20ed2a5b7f836c4b880b96abb87ed1d`, line 270; 1 current observation(s).
- `services/api/tests/test_report_revisions.py::test_correction_and_delayed_reanalysis_preserve_original_evidence_and_exact_units` — file SHA `d83d92bfad35040a508a5dfa79b586eec0411021b2da06c3f4c8a1c955096d06`, line 463; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- MEASURE complete-record/upload reconciliation/recovery/reliability under actual intended workflow with representative interruption/restart: unit/controller traces alone do not provide real operational reliability study or complete live gate.

Prerequisite/evidence type: study_scientific_approval, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA bf5810ed55cd29bb1d66e814cbdfe3a7d1daaf158e400fd7b523e2649fe738cf. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-026-01 — BLOCKED

PRD acceptance review — | PRD-026 | Economic feasibility | Build usage-based cost scenarios before selecting subscription allowances or promising a hardware subsidy. |

Current proof: FULLSPEC labels20USD/month hypothesis with hardware allowance/COGS/margin unresolved; no price promise adopted.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Usage-based economic scenarios BEFORE subscription allowance/hardware subsidy: actual cost model/usage distribution/dated supplier quotations absent; requires BUL/PL/G13 evidence, no paid service requested.

Prerequisite/evidence type: physical_hardware_execution, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 8b0f621953052caecb9285173fa0d96b2499db1683b47c06948d91a89a8d6400. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-027-01 — BLOCKED

PRD acceptance review — | PRD-027 | Freeze intended use, primary impairment outcome, population, thresholds, and collection-to-result interval | Clinical and product leads, with statistical lead | P2 confirmatory evaluation and all P3 claims |

Current proof: Locked file hashes/chronology/refusal are executable; tool explicitly does not authenticate historic endpoint/plan approval.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_evaluation.py::test_external_history_references_remain_unverified_through_pipeline` — file SHA `7d8df519466ee08a3461fbac69176b621e07b587fe85c07e07098d94b57b3d31`, line 201; 5 current observation(s).
- `services/api/tests/test_model_engine.py::test_training_evaluation_policy_and_result_proof_are_bound` — file SHA `1bf4b788a6089c054bdc6a192b9c0fca8475363dd738b2ca5a69a106535a17ce`, line 437; 5 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Clinical/product/statistical freeze of intendeduse/independent impairment outcome/population/thresholds/collection-to-result interval before P2/P3 claims: named genuine G01/G08/G14 decision record absent.

Prerequisite/evidence type: study_scientific_approval.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA b5b861295e74603274cfe81db8ceca2f2c58d7900a274224b8b806bb2ff04412. Actual current source and raw evidence supply this disposition.

## OTGD-001-PRD-028-01 — BLOCKED

PRD acceptance review — | PRD-028 | Select collection/cartridge chemistry, cardiac implementation, optical protocol, supported phone list, final retention policy, and subscription allowance | Respective analytical, hardware, optical, app, data, and commercial leads | Respective feasibility and release gates |

Current proof: Canonical gate register explicitly leaves chemistry/cardio/optics/device/retention/allowance decisions to named responsible experts; deployment seeds no genuine approvals.


No current named execution is adopted for this exact scenario.

Exact unproved clause(s):

- Responsible experts SELECT actual collection chemistry/cardiac/optical/supportedphone/finalretention/subscription allowance at corresponding feasibility/release gates: no complete named real decision/evidence package supplied.

Prerequisite/evidence type: independent_prerequisite_or_exact_scenario_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 1a22cf06a72e3c23a185ff525638a4a10b20d3dbe7ac613b82ca2cafab047c6d. Actual current source and raw evidence supply this disposition.
