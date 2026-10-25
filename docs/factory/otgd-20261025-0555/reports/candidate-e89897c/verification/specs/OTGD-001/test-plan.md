# OTGD-001 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `specs/FULL_SPECIFICATION.md`; SHA256 `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-001/test-plan.md`. External review artifact only; PM controls import.

All 128 stable cases / 128 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `python scripts/ci_gate.py components`
- `python scripts/ci_gate.py atdd`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`
- `swift test --package-path apps/mobile/modules/reaction-task --parallel --num-workers 1 --verbose --disable-swift-testing --xunit-output "$PWD/reports/ios-native.xml"`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-001-HW-001-01 | Owner acceptance evidence — BOM and firmware target agree with ADR-004. | PARTIAL |
| OTGD-001-HW-002-01 | Owner acceptance evidence — End-to-end inspection shows no loss or replacement of provenance. | PARTIAL |
| OTGD-001-HW-003-01 | Owner acceptance evidence — Trace a captured record to one reader and firmware build. | PARTIAL |
| OTGD-001-HW-004-01 | Owner acceptance evidence — Controlled fault injection produces explicit recoverable or invalid states. | PASS |
| OTGD-001-HW-005-01 | Owner acceptance evidence — Gate G-05 sign-off and bench evidence precede participant connection. | BLOCKED |
| OTGD-001-HW-006-01 | Owner acceptance evidence — Approved power/connection diagram and documented permitted configurations. | BLOCKED |
| OTGD-001-HW-007-01 | Owner acceptance evidence — Reference signal reconstructs within frozen acquisition tolerances. | BLOCKED |
| OTGD-001-HW-008-01 | Owner acceptance evidence — G-04 defines limits and verifies supported configurations. | BLOCKED |
| OTGD-001-HW-009-01 | Owner acceptance evidence — Reprocess retained permitted data to the same versioned features. | PARTIAL |
| OTGD-001-HW-010-01 | Owner acceptance evidence — Handling review and inspection demonstrate the defined contamination boundary. | BLOCKED |
| OTGD-001-HW-011-01 | Owner acceptance evidence — G-10 approved drawings, duty-cycle measurements, and human-factors results. | BLOCKED |
| OTGD-001-HW-012-01 | Owner acceptance evidence — An expired or incompatible configuration cannot be reported as qualified. | PASS |
| OTGD-001-ANA-001-01 | Owner acceptance evidence — Specimen lineage shows one collection for a valid check. | PASS |
| OTGD-001-ANA-002-01 | Owner acceptance evidence — Approved collection SOP and recovery/stability evidence at G-02. | BLOCKED |
| OTGD-001-ANA-003-01 | Owner acceptance evidence — Channel selection report identifies measured feasibility and unresolved channels. | BLOCKED |
| OTGD-001-ANA-004-01 | Owner acceptance evidence — Prespecified qualification report passes G-03 criteria. | BLOCKED |
| OTGD-001-ANA-005-01 | Owner acceptance evidence — Challenge panel and method comparison are approved before final qualification. | BLOCKED |
| OTGD-001-ANA-006-01 | Owner acceptance evidence — Unit fixtures include pg/mL conversion without magnitude errors. | PASS |
| OTGD-001-ANA-007-01 | Owner acceptance evidence — Contract validation rejects fabricated quantified values for censored results. | PASS |
| OTGD-001-ANA-008-01 | Owner acceptance evidence — Cross-field validation and incompatible-input cases pass. | PARTIAL |
| OTGD-001-ANA-009-01 | Owner acceptance evidence — Prespecified agreement and failure analysis; external validation before claims. | BLOCKED |
| OTGD-001-ANA-010-01 | Owner acceptance evidence — An independent reviewer reconstructs a selected reported measurement. | PARTIAL |
| OTGD-001-ANA-011-01 | Owner acceptance evidence — Deliberate invalid specimens cannot yield an apparently ordinary concentration. | PARTIAL |
| OTGD-001-ANA-012-01 | Owner acceptance evidence — Retry audit preserves both attempts and their disposition. | PASS |
| OTGD-001-ANA-013-01 | Owner acceptance evidence — G-03 and G-13 contain measured data or dated supplier evidence. | BLOCKED |
| OTGD-001-APP-001-01 | Owner acceptance evidence — Scripted P0 journey displays measurement-only completion. | PASS |
| OTGD-001-APP-002-01 | Owner acceptance evidence — Boundary and unit examples produce correct BMI or explicit missing status. | PASS |
| OTGD-001-APP-003-01 | Owner acceptance evidence — Missing context survives export and cannot become a fabricated timestamp. | PARTIAL |
| OTGD-001-APP-004-01 | Owner acceptance evidence — Task event record verifies counts and excludes practice from scored features. | PASS |
| OTGD-001-APP-005-01 | Owner acceptance evidence — Seeded replay and event-level inspection reproduce features. | PASS |
| OTGD-001-APP-006-01 | Owner acceptance evidence — Reference event streams match expected derived feature records. | PASS |
| OTGD-001-APP-007-01 | Owner acceptance evidence — G-06 freezes and verifies device-specific timing acceptance. | BLOCKED |
| OTGD-001-APP-008-01 | Owner acceptance evidence — Interruption cases produce the prescribed quality and retry state. | PARTIAL |
| OTGD-001-APP-009-01 | Owner acceptance evidence — Low-quality and unscaled examples cannot pass as calibrated diameter. | PASS |
| OTGD-001-APP-010-01 | Owner acceptance evidence — Result inspection identifies whether a measurement followed the approved protocol. | PARTIAL |
| OTGD-001-APP-011-01 | Owner acceptance evidence — Temporal audit prevents later sessions entering a baseline. | PASS |
| OTGD-001-APP-012-01 | Owner acceptance evidence — State-by-state screenshots and API checks match the LLD. | PARTIAL |
| OTGD-001-APP-013-01 | Owner acceptance evidence — Copy review covers all result, notification, and error screens. | PARTIAL |
| OTGD-001-APP-014-01 | Owner acceptance evidence — G-10 lists supported configurations and tested accommodations. | BLOCKED |
| OTGD-001-MOD-001-01 | Owner acceptance evidence — G-01 protocol defines outcome, assessor, timing, and label rules. | BLOCKED |
| OTGD-001-MOD-002-01 | Owner acceptance evidence — Model review identifies measured features and any explicitly evaluated latent model. | PARTIAL |
| OTGD-001-MOD-003-01 | Owner acceptance evidence — Adversarial synthetic records produce the specified validity behavior. | PASS |
| OTGD-001-MOD-004-01 | Owner acceptance evidence — Any prediction can be reconstructed from immutable versioned inputs. | PASS |
| OTGD-001-MOD-005-01 | Owner acceptance evidence — Split audit and leakage review pass before locked evaluation. | PARTIAL |
| OTGD-001-MOD-006-01 | Owner acceptance evidence — Timestamp and dependency audit covers each feature and baseline. | PASS |
| OTGD-001-MOD-007-01 | Owner acceptance evidence — Manifest review and incompatible-record checks pass. | PASS |
| OTGD-001-MOD-008-01 | Owner acceptance evidence — Unauthorized activation and retired-model invocation are rejected. | PASS |
| OTGD-001-MOD-009-01 | Owner acceptance evidence — Negative inference cases verify null/absent probability and explicit reason. | PASS |
| OTGD-001-MOD-010-01 | Owner acceptance evidence — Every gate has both passing and rejecting integration evidence. | PARTIAL |
| OTGD-001-MOD-011-01 | Owner acceptance evidence — Variant selection is explicit, versioned, and validated. | PARTIAL |
| OTGD-001-MOD-012-01 | Owner acceptance evidence — Locked analysis plan and artifact hashes predate evaluation access. | BLOCKED |
| OTGD-001-MOD-013-01 | Owner acceptance evidence — Result contract and independent interpretation review pass. | PARTIAL |
| OTGD-001-MOD-014-01 | Owner acceptance evidence — Ablation report supports retained measurement burden. | PARTIAL |
| OTGD-001-MOD-015-01 | Owner acceptance evidence — Change-control exercise preserves the prior artifact and results. | PARTIAL |
| OTGD-001-ALC-001-01 | Owner acceptance evidence — Interface and synthetic demonstrations retain channel identity and provenance. | PASS |
| OTGD-001-ALC-002-01 | Owner acceptance evidence — G-11 documents supplier specifications and design tradeoffs. | BLOCKED |
| OTGD-001-ALC-003-01 | Owner acceptance evidence — Contract fixtures preserve all metadata without unapproved blood conversion. | PARTIAL |
| OTGD-001-ALC-004-01 | Owner acceptance evidence — Dedicated alcohol qualification against the selected reference method. | BLOCKED |
| OTGD-001-ALC-005-01 | Owner acceptance evidence — Protocol and model manifest agree on co-use handling. | PARTIAL |
| OTGD-001-SEC-001-01 | Owner acceptance evidence — Pre-commit/release review and secret/data scan of the staged changes. | NOT_RUN |
| OTGD-001-SEC-002-01 | Owner acceptance evidence — Unauthorized-role tests and identity-mapping review pass. | PARTIAL |
| OTGD-001-SEC-003-01 | Owner acceptance evidence — Consent/authorization and upload traces demonstrate the boundary. | PASS |
| OTGD-001-SEC-004-01 | Owner acceptance evidence — Deployment configuration and access review satisfy G-12. | BLOCKED |
| OTGD-001-SEC-005-01 | Owner acceptance evidence — G-12 states durations and tests deletion across primary/backup workflows. | PARTIAL |
| OTGD-001-SEC-006-01 | Owner acceptance evidence — Representative failure logs pass content review. | PARTIAL |
| OTGD-001-SEC-007-01 | Owner acceptance evidence — Tabletop exercise and responsible contacts documented. | BLOCKED |
| OTGD-001-OPS-001-01 | Owner acceptance evidence — Architecture review confirms boundaries and deployment configuration. | BLOCKED |
| OTGD-001-OPS-002-01 | Owner acceptance evidence — Repeated identical submissions produce one accepted logical record. | PASS |
| OTGD-001-OPS-003-01 | Owner acceptance evidence — Correction scenario preserves original content and provenance. | PASS |
| OTGD-001-OPS-004-01 | Owner acceptance evidence — Clock-drift and reordered-message cases retain interpretable timing. | PARTIAL |
| OTGD-001-OPS-005-01 | Owner acceptance evidence — Network interruption and restart exercises preserve correct terminal state. | PARTIAL |
| OTGD-001-OPS-006-01 | Owner acceptance evidence — G-12 documents values and a successful recovery exercise. | BLOCKED |
| OTGD-001-VAL-001-01 | Owner acceptance evidence — G-07 authorization and staff readiness records. | BLOCKED |
| OTGD-001-VAL-002-01 | Owner acceptance evidence — Outcome manual and data-flow review exclude circular labels. | BLOCKED |
| OTGD-001-VAL-003-01 | Owner acceptance evidence — Approved calculation/simulation at G-08; no arbitrary sample guarantee. | BLOCKED |
| OTGD-001-VAL-004-01 | Owner acceptance evidence — Prespecified strata and exclusions appear in the final report. | PARTIAL |
| OTGD-001-VAL-005-01 | Owner acceptance evidence — Independent report reconciles every enrolled check with its disposition. | PARTIAL |
| OTGD-001-VAL-006-01 | Owner acceptance evidence — G-09 report states independence, limitations, and deviations. | BLOCKED |
| OTGD-001-VAL-007-01 | Owner acceptance evidence — Temporal audit and study report demonstrate the consumer information boundary. | PARTIAL |
| OTGD-001-VAL-008-01 | Owner acceptance evidence — G-14 documented applicability determination and required evidence. | BLOCKED |
| OTGD-001-BUS-001-01 | Owner acceptance evidence — Commercial material avoids an unverified price/performance promise. | BLOCKED |
| OTGD-001-BUS-002-01 | Owner acceptance evidence — Dated cost model with supplier quotations and sensitivity analysis. | BLOCKED |
| OTGD-001-BUS-003-01 | Owner acceptance evidence — Product decision cites ablation, usability, and cost evidence. | BLOCKED |
| OTGD-001-DOC-001-01 | Owner acceptance evidence — Repository review finds no unsupported completion claim. | PARTIAL |
| OTGD-001-DOC-002-01 | Owner acceptance evidence — Gate register contains approver, date, artifact, and decision. | BLOCKED |
| OTGD-001-DOC-003-01 | Owner acceptance evidence — Change-impact checklist and versioned repository history. | PARTIAL |
| OTGD-001-PRD-001-01 | PRD acceptance review — \| PRD-001 \| A valid consumer-format check MUST require one saliva collection and one continuous reaction task. Multiple channels may be measured from that collection. \| | PARTIAL |
| OTGD-001-PRD-002-01 | PRD acceptance review — \| PRD-002 \| The check MUST also support guided pupil capture and resting heart-rate capture; ECG MUST remain an exploratory input until its incremental value and hardware approach are justified. \| | PARTIAL |
| OTGD-001-PRD-003-01 | PRD acceptance review — \| PRD-003 \| P0 and P1 MUST produce measurement-only outputs, never an intoxication probability. \| | PASS |
| OTGD-001-PRD-004-01 | PRD acceptance review — \| PRD-004 \| A P2 probability MUST require an authorized research session, an `active_research` model, a compatible feature contract, and all model-required valid channels. \| | PASS |
| OTGD-001-PRD-005-01 | PRD acceptance review — \| PRD-005 \| The future impairment endpoint, intended population, operating threshold, and acceptable error rates MUST be selected before confirmatory evaluation. \| | BLOCKED |
| OTGD-001-PRD-006-01 | PRD acceptance review — \| PRD-006 \| A model result MUST NOT be presented as proof of cannabis causation, a legal determination, or clearance to drive. \| | PARTIAL |
| OTGD-001-PRD-007-01 | PRD acceptance review — \| PRD-007 \| The product MUST retain distinct invalid, inconclusive, measurement-only, and research-estimate outcomes. Missing information MUST NOT be interpreted as a normal measurement. \| | PASS |
| OTGD-001-PRD-008-01 | PRD acceptance review — \| PRD-008 \| Alcohol MUST remain a separately measured and separately reported channel; cannabis physiology MUST NOT substitute for a breath-alcohol measurement. \| | PASS |
| OTGD-001-PRD-009-01 | PRD acceptance review — \| PRD-009 \| Standardized session orchestration \| P0 MUST establish a complete synthetic workflow with unique attempts, timestamps, quality, and terminal states. \| | PASS |
| OTGD-001-PRD-010-01 | PRD acceptance review — \| PRD-010 \| Quantitative saliva interface \| P1 MUST establish reliable specimen handling and a reference-laboratory comparison before any portable concentration claim. \| | PARTIAL |
| OTGD-001-PRD-011-01 | PRD acceptance review — \| PRD-011 \| Parent THC channel \| P1 MUST evaluate delta-9 THC first. Selection of additional channels requires analytical feasibility and added-value evidence. \| | BLOCKED |
| OTGD-001-PRD-012-01 | PRD acceptance review — \| PRD-012 \| Additional saliva metabolites \| THC-COOH and 11-OH-THC SHOULD be investigated; neither is promised as a functional cartridge channel in v0.1.0. \| | PARTIAL |
| OTGD-001-PRD-013-01 | PRD acceptance review — \| PRD-013 \| One repeated-trial game \| P0 MUST support the task contract; P2 MUST evaluate reliability and independent predictive value. \| | PARTIAL |
| OTGD-001-PRD-014-01 | PRD acceptance review — \| PRD-014 \| Dynamic pupil measurements \| P1/P2 MUST establish acquisition quality, valid units, optical controls, and repeatability before features enter a model. \| | PARTIAL |
| OTGD-001-PRD-015-01 | PRD acceptance review — \| PRD-015 \| Heart rate and exploratory ECG \| Cardiac capture MUST preserve signal quality and context; an ECG-only benefit MUST be measured by ablation. \| | PARTIAL |
| OTGD-001-PRD-016-01 | PRD acceptance review — \| PRD-016 \| Profile and use history \| The app MUST preserve source, measurement date, units, and unknown values; demographics MUST NOT determine an assumed clearance rate. \| | PASS |
| OTGD-001-PRD-017-01 | PRD acceptance review — \| PRD-017 \| Separate alcohol channel \| The design SHOULD reserve integration capability; alcohol performance claims require a calibrated breath system and dedicated validation. \| | PARTIAL |
| OTGD-001-PRD-018-01 | PRD acceptance review — \| PRD-018 \| Versioned research dataset \| P2 MUST support reconstruction of the exact specimen, task, device, calibration, feature, and model versions. \| | PASS |
| OTGD-001-PRD-019-01 | PRD acceptance review — \| PRD-019 \| Quality-aware research result \| Inference MUST enforce the release manifest and required-channel rules without fallback to an incompatible model. \| | PARTIAL |
| OTGD-001-PRD-020-01 | PRD acceptance review — \| PRD-020 \| Understandable session feedback \| The app MUST distinguish capture success, analysis availability, and a research prediction. \| | PARTIAL |
| OTGD-001-PRD-029-01 | PRD acceptance review — \| PRD-029 \| A person can enter guest practice or authenticate, recover an interrupted sign-in, refresh safely and sign out with truthful remote-revocation status. Environment/account partitions and retained signed-out data stay isolated. \| SEC-002/004/007; AND-ONB-001–006; AND-AUTH-001–007; AND-ENV-001/002 \| | PARTIAL |
| OTGD-001-PRD-030-01 | PRD acceptance review — \| PRD-030 \| An invited eligible account can review exact study consent and current channel availability; sign-in, age, a guessed study ID or a checkbox cannot create research authority. Withdrawal stops local study work immediately and preserves its durable receipt. \| SEC-002/003; MOD-008–010; AND-STUDY-001–006; PAI-001–008 \| | PARTIAL |
| OTGD-001-PRD-031-01 | PRD acceptance review — \| PRD-031 \| A check freezes its confirmed optional profile/context, one-sample/one-task information boundary, original target, all attempts and selected evidence. Interruptions and linked replacements preserve original records. \| ANA-001/012; APP-001–008; OPS-002–005; AND-PRO-001–007; AND-CHECK-001–008 \| | PARTIAL |
| OTGD-001-PRD-032-01 | PRD acceptance review — \| PRD-032 \| Native reaction acquisition preserves deterministic practice/scored schedules, actual native events, missingness and immediate stop behavior; build success and clock resolution do not establish physical timing qualification. \| APP-004–008/014; AND-TASK-001–008; G-06 \| | PASS |
| OTGD-001-PRD-033-01 | PRD acceptance review — \| PRD-033 \| Device discovery, verified binding and fresh scoped starts distinguish a working connection from a qualified channel. Protected BLE, actual adapter inventory, quality, cancellation and replay/origin fences apply to conditional reader capture. \| HW-003/004/007/012; SEC-004; AND-DEV-001–008; CAN-SR-001–011; VPPG-001–007 \| | PARTIAL |
| OTGD-001-PRD-034-01 | PRD acceptance review — \| PRD-034 \| Saliva collection/import, optical capture and selected PPG/exploratory ECG have explicit pending, unavailable, invalid and permitted retry paths. Declarations, approved software and signatures do not qualify an assay, optics, electrical setup or sensor. \| ANA-001–012; HW-005–009; APP-009/010; AND-SAL-001–007; SALCOL-001–008; AND-EYE-001–007/101–106; AND-HR-001–007; AND-ECG-001–007 \| | PARTIAL |
| OTGD-001-PRD-035-01 | PRD acceptance review — \| PRD-035 \| Protected local save precedes a separate explicit account upload; restart, lost receipts, bounded retry and conflicts preserve ownership, original times and immutable evidence. Permission failures and retired generations cannot be repaired by automatic reupload. \| SEC-003/004; OPS-002–005; AND-SYNC-001–007; AND-CHECK-006; shared contracts §§2–5 \| | PARTIAL |
| OTGD-001-PRD-036-01 | PRD acceptance review — \| PRD-036 \| History/results show the actual scientific state separately from delivery, preserve qualifiers and old acquisition times, and navigate immutable original/replacement and same-specimen report-revision lineage. \| APP-012/013; MOD-013; AND-HIST-001–007; AND-RES-001–007; report-revision and replacement-links contracts \| | PASS |
| OTGD-001-PRD-037-01 | PRD acceptance review — \| PRD-037 \| Optional eye/ECG recording and upload default off, have distinct reviewed purposes, retain exact receipts and expire under original retention deadlines. Revocation stops capture before cleanup; pending quarantine/cleanup is visible. \| SEC-003–005; AND-RAW-001–007; AND-EYE-006/106; AND-ECG-007; raw-recording-retention contract \| | PARTIAL |
| OTGD-001-PRD-038-01 | PRD acceptance review — \| PRD-038 \| The owner can create a bounded exact-scope structured export, optionally include separately authorized retained raw sources, verify and deliberately share it. Downloads require current authority; expiration, revocation and temporary-file cleanup remain explicit. \| SEC-002/005/007; AND-EXP-001–007; RAW-EXP-001–008; AND-RAW-008 \| | PARTIAL |
| OTGD-001-PRD-039-01 | PRD acceptance review — \| PRD-039 \| Local clear, cloud-data deletion, account deletion and withdrawal show distinct scopes and honest asynchronous receipts. Generation barriers and independent retained recovery evidence prevent resurrection; study recovery requires fresh independent reapproval and participant consent. \| SEC-005/007; OPS-003–006; AND-PRIV-001–007; RECOVERY-001/002; platform contract \| | PARTIAL |
| OTGD-001-PRD-040-01 | PRD acceptance review — \| PRD-040 \| Instructions, navigation, errors and privacy controls support specified Android/iOS accessibility and permission recovery. Changes to timed-task presentation/input retain their separate compatibility and qualification boundary. \| APP-014; AND-SET-001–007 and feature-specific parity requirements; shared contracts §9 \| | BLOCKED |
| OTGD-001-PRD-041-01 | PRD acceptance review — \| PRD-041 \| Independently governed operator releases can admit the exact conditional research software, including only explicitly approved model variants and baseline scope. Measurement-only remains default; the restricted HR-only evaluation mode discloses absent multimodal comparisons. \| MOD-001–015; VAL-001–007; OPERATOR-AUTHORITY-001–009; MODEL-001–006; EVAL-001–008 as modified; HR-AUTH-001–008 \| | PASS |
| OTGD-001-PRD-042-01 | PRD acceptance review — \| PRD-042 \| Isolated fictional previews and reviewable local/QA/prod/store delivery tooling preserve exact source/artifact identity, environment and uncertain outcomes. Prepared software, submitted artifacts, hosted access, public availability and scientific qualification remain separate evidence. \| HW-002; SEC-001/004; OPS-001–006; AND-ENV-001–007; AND-PREV-001–003; WEB-DEP-001–010; CLOUD-DEP-001–011; PREVIEW-001–003; STORE-001–018 \| | PARTIAL |
| OTGD-001-PRD-021-01 | PRD acceptance review — \| PRD-021 \| Analytical usefulness \| Compare each intended cartridge channel with a traceable reference method over a prespecified range, including censored and invalid results. Freeze acceptance limits before qualification. \| | BLOCKED |
| OTGD-001-PRD-022-01 | PRD acceptance review — \| PRD-022 \| Independent prediction value \| Compare chemistry alone, app signals alone, and the combined model against the same independent outcome. Require evidence of useful incremental benefit. \| | PARTIAL |
| OTGD-001-PRD-023-01 | PRD acceptance review — \| PRD-023 \| Single-check usability \| Measure completion rate, duration distribution, retries, specimen failures, camera failures, and task interruptions using the intended workflow. \| | BLOCKED |
| OTGD-001-PRD-024-01 | PRD acceptance review — \| PRD-024 \| Generalization \| Report errors and calibration for held-out people, later sessions, supported devices, consumption routes, use-frequency strata, and first-use versus personalized modes. \| | PARTIAL |
| OTGD-001-PRD-025-01 | PRD acceptance review — \| PRD-025 \| Operational reliability \| Measure record completeness, upload reconciliation, recovery after interruption, and traceability of finalized results. \| | PARTIAL |
| OTGD-001-PRD-026-01 | PRD acceptance review — \| PRD-026 \| Economic feasibility \| Build usage-based cost scenarios before selecting subscription allowances or promising a hardware subsidy. \| | BLOCKED |
| OTGD-001-PRD-027-01 | PRD acceptance review — \| PRD-027 \| Freeze intended use, primary impairment outcome, population, thresholds, and collection-to-result interval \| Clinical and product leads, with statistical lead \| P2 confirmatory evaluation and all P3 claims \| | BLOCKED |
| OTGD-001-PRD-028-01 | PRD acceptance review — \| PRD-028 \| Select collection/cartridge chemistry, cardiac implementation, optical protocol, supported phone list, final retention policy, and subscription allowance \| Respective analytical, hardware, optical, app, data, and commercial leads \| Respective feasibility and release gates \| | BLOCKED |
