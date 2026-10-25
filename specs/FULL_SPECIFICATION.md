# Full product and engineering specification

**Product:** One-The-Go Detection\
**Version:** 0.1.0\
**Decision date:** 2026-10-10, America/Chicago\
**Status:** Normative development specification; proposed targets are not measured product performance.

## 1. Scope, interpretation, and ownership

This is the requirement register for a research platform and its possible progression toward a pocket cannabis-and-alcohol product. It is not a manufacturing release package. Cartridge chemistry, final PCB and mechanical drawings, diagnostic performance, and commercial release remain gated deliverables.

**MUST** identifies an acceptance condition. **SHOULD** identifies a preferred approach; any deviation requires a recorded rationale and impact review. **MAY** identifies an optional capability. A **target** is proposed and unverified. **TBD** means no accepted value exists; the named gate must resolve it before dependent work proceeds. Absence of a value is not permission to invent one.

Phases are **P0 integration**, **P1 analytical feasibility**, **P2 controlled research**, and **P3 possible validated product release**. A requirement marked P2 does not authorize research. Roles below are accountable functions that the project must assign to named people: product (PL), engineering (EL), hardware (HWL), analytical chemistry (ANL), optics (OL), mobile application (APL), clinical research (CL), statistics (SL), machine learning (MLL), independent validation (IVL), security/data (SDL), quality/regulatory (QRL), and commercial (BUL).

The architectural baseline is [DECISIONS.md](DECISIONS.md). Implementation semantics belong to [LLD.md](LLD.md); evidence and study procedures belong to [SOURCES.md](SOURCES.md) and [VALIDATION_PLAN.md](VALIDATION_PLAN.md). A requirement is closed only by linked evidence reviewed by its owner.

## 2. Target product specification sheet

| Characteristic | v0.1.0 specification | Classification and release consequence |
|---|---|---|
| Intended future output | Probability of a prespecified current functional-impairment endpoint in the context of cannabis exposure | Research hypothesis; endpoint and claim are Gate G-01 |
| Consumer-format collection | One saliva collection per valid check; replacement attempts retained separately | Mandatory invariant |
| Consumer-format task | One continuous `choice_inhibit_v0` task: six practice trials; 60 scored, comprising 48 go and 12 no-go | Proposed research task; predictive validity unresolved |
| Task duration | Approximately two minutes nominal | Unmeasured target; actual duration and usable timing are evaluated |
| Other capture | Guided pupil light response and resting cardiac capture; exploratory ECG | Capture configuration and quality thresholds gated |
| Initial controller | Arduino Nano ESP32; Arduino C++ firmware | Selected integration platform, not an assay or final PCB |
| Mobile architecture | React Native workflow with native Swift/Kotlin timing and capture modules | Proposed implementation; supported device list unresolved |
| Communications | USB serial for first synthetic bench work; BLE planned | BLE and physical sensor integration are not supplied by the synthetic example |
| Research backend | Python/FastAPI modular service, PostgreSQL, private object storage for approved artifacts | Proposed architecture; no deployment asserted |
| Saliva channels | Parent delta-9 THC first; THC-COOH and 11-OH-THC evaluated separately | No completed cartridge or detection-performance claim |
| Cardiac units | Heart rate in bpm; raw ECG in mV | Mandatory data conventions |
| Eye units | Diameter in mm only with validated scale; otherwise explicitly normalized units | Mandatory unit qualification |
| Reaction units | Milliseconds, with monotonic event timing and device metadata | Mandatory data conventions |
| Saliva units | Canonical ng/mL plus original units, basis, limits, and provenance | Mandatory data conventions |
| Alcohol units | Breath alcohol in mg/L from a separately calibrated channel | Future channel; no automatic blood-alcohol conversion specified |
| Physical form | Pocket-sized integrated reader is the product goal | Final dimensions, mass, ingress rating, battery life, and materials TBD at G-10 |
| Turnaround | Complete-check collection-to-result target TBD | Gate G-03/G-10; no instant chemical result promised |
| Pricing | Approximately US$20/month hypothesis | Hardware charge, allowance, COGS, and margin unresolved at G-13 |
| Released model mode | No consumer clinical mode in v0.1.0 | P0/P1 measurement-only; controlled P2 inference is gated |

## 3. Hardware and signal acquisition requirements

| ID | Normative requirement | Phase; owner | Acceptance evidence |
|---|---|---|---|
| HW-001 | The first electronics prototype MUST use the selected Nano ESP32 platform unless an architectural decision records a replacement. | P0; HWL | BOM and firmware target agree with ADR-004. |
| HW-002 | Synthetic readings MUST be visibly labeled and carry `simulated` provenance through every storage and display layer. | P0+; EL | End-to-end inspection shows no loss or replacement of provenance. |
| HW-003 | Each physical reader MUST expose stable device identity, hardware revision, firmware version, and boot/session identity. | P1+; HWL | Trace a captured record to one reader and firmware build. |
| HW-004 | The interface MUST detect incomplete frames, duplicate messages, disconnects, and stale readings. | P0+; EL | Controlled fault injection produces explicit recoverable or invalid states. |
| HW-005 | A body-connected ECG prototype MUST pass the electrical-safety design review before use; early evaluation MUST use a simulator. | P0/P1; HWL, QRL | Gate G-05 sign-off and bench evidence precede participant connection. |
| HW-006 | ECG power, isolation, charging, exposed conductors, and attached USB equipment MUST be evaluated as one system. | P1+; HWL | Approved power/connection diagram and documented permitted configurations. |
| HW-007 | Cardiac acquisition MUST retain sample rate, gain/scaling, contact quality, dropped-sample information, and relevant filtering versions. | P1+; HWL | Reference signal reconstructs within frozen acquisition tolerances. |
| HW-008 | Optical capture MUST use an approved stimulus and positioning protocol with bounded exposure; arbitrary phone-flash settings MUST NOT be assumed safe or equivalent. | P1+; OL | G-04 defines limits and verifies supported configurations. |
| HW-009 | Pupil features MUST retain illumination, camera/device metadata, frame timing, segmentation quality, and the coordinate/scale basis. | P1+; OL, APL | Reprocess retained permitted data to the same versioned features. |
| HW-010 | The prototype MUST keep saliva-contaminated components separate from user electrical contacts and reusable optical surfaces. | P1+; HWL | Handling review and inspection demonstrate the defined contamination boundary. |
| HW-011 | The final product SHOULD minimize removable electronics and exposed wiring after feasibility; dimensions and battery targets MUST be selected from measured workload. | P3; HWL | G-10 approved drawings, duty-cycle measurements, and human-factors results. |
| HW-012 | Reader calibration, maintenance, component replacement, and compatibility MUST be traceable. | P1+; HWL | An expired or incompatible configuration cannot be reported as qualified. |

## 4. Saliva collection and analytical requirements

| ID | Normative requirement | Phase; owner | Acceptance evidence |
|---|---|---|---|
| ANA-001 | A valid check MUST use one identified saliva collection; multiple analyte channels MAY share it. | P1+; ANL | Specimen lineage shows one collection for a valid check. |
| ANA-002 | Collection method MUST define volume or dilution, container/collector, handling, timing, storage, and allowed processing. | P1; ANL | Approved collection SOP and recovery/stability evidence at G-02. |
| ANA-003 | Parent delta-9 THC MUST be evaluated first; THC-COOH and 11-OH-THC MUST remain separate feasibility decisions. | P1; ANL | Channel selection report identifies measured feasibility and unresolved channels. |
| ANA-004 | Each channel MUST establish analyte identity, selectivity, calibration range, detection and quantification limits, precision, bias, recovery, and stability. | P1; ANL | Prespecified qualification report passes G-03 criteria. |
| ANA-005 | The reference-method plan MUST address interferents, related cannabinoids/isomers, collection materials, carryover, and oral-matrix effects. | P1; ANL | Challenge panel and method comparison are approved before final qualification. |
| ANA-006 | Each value MUST preserve original units and a canonical ng/mL value when conversion is valid; conversion factors MUST be explicit. | P0+; EL, ANL | Unit fixtures include pg/mL conversion without magnitude errors. |
| ANA-007 | Results MUST use the canonical qualifier vocabulary; below-LOQ and not-detected results MUST NOT be stored as measured zero. | P0+; EL | Contract validation rejects fabricated quantified values for censored results. |
| ANA-008 | Free and total-after-hydrolysis measurements MUST remain distinguishable; unspecified basis MUST block any model requiring a defined basis. | P0+; ANL, MLL | Cross-field validation and incompatible-input cases pass. |
| ANA-009 | A portable assay MUST be compared with a reference laboratory method on paired specimens across its intended usable range. | P1/P2; ANL, IVL | Prespecified agreement and failure analysis; external validation before claims. |
| ANA-010 | Each assay record MUST retain collection/analysis time, lot, method version, calibration, instrument, operator or automation identity, and quality. | P1+; ANL | An independent reviewer reconstructs a selected reported measurement. |
| ANA-011 | Failed adequacy, contamination, overflow, expired supplies, and out-of-range results MUST have distinct recorded reasons. | P1+; ANL | Deliberate invalid specimens cannot yield an apparently ordinary concentration. |
| ANA-012 | A consumable replacement MUST create a new attempt linked to the prior one; finalized specimens MUST NOT be silently overwritten. | P1+; EL | Retry audit preserves both attempts and their disposition. |
| ANA-013 | Cartridge selection MUST document consumable cost, shelf life, storage, disposal, sample burden, and observed turnaround. | P1+; ANL, BUL | G-03 and G-13 contain measured data or dated supplier evidence. |

## 5. Application, game, and profile requirements

| ID | Normative requirement | Phase; owner | Acceptance evidence |
|---|---|---|---|
| APP-001 | The app MUST guide one continuous session and show capture progress without representing data capture as a prediction. | P0+; APL | Scripted P0 journey displays measurement-only completion. |
| APP-002 | Profile MUST preserve age, height, weight, units, dates, and source; BMI MUST be derived consistently from qualified height/weight. | P0+; APL | Boundary and unit examples produce correct BMI or explicit missing status. |
| APP-003 | Use frequency and optional route/timing MUST allow unknown and declined values; self-report MUST remain identifiable as such. | P0+; APL | Missing context survives export and cannot become a fabricated timestamp. |
| APP-004 | `choice_inhibit_v0` MUST contain six practice and 60 scored trials with 48 go and 12 no-go trials. | P0+; APL | Task event record verifies counts and excludes practice from scored features. |
| APP-005 | Task timing, stimulus schedule, response windows, interruptions, and invalid-trial rules MUST follow the versioned LLD contract. | P0+; APL | Seeded replay and event-level inspection reproduce features. |
| APP-006 | Reaction features MUST include speed, variability, omissions, incorrect choices, and commission errors as defined by feature version. | P0/P2; APL, MLL | Reference event streams match expected derived feature records. |
| APP-007 | Timing-critical capture MUST use native monotonic timing; reported latency tolerances MUST be measured on supported devices. | P1+; APL | G-06 freezes and verifies device-specific timing acceptance. |
| APP-008 | Backgrounding, notifications, orientation changes, late frames, and interrupted touches MUST be recorded or invalidate the affected capture. | P0+; APL | Interruption cases produce the prescribed quality and retry state. |
| APP-009 | Pupil capture MUST reject inadequate recordings under frozen quality rules; normalized geometry MUST NOT be mislabeled millimeters. | P1+; OL, APL | Low-quality and unscaled examples cannot pass as calibrated diameter. |
| APP-010 | Heart-rate context MUST retain acquisition duration, position/activity instructions, quality, and source device. | P1+; APL | Result inspection identifies whether a measurement followed the approved protocol. |
| APP-011 | Personal baseline use MUST require qualified earlier sessions and a compatible mode; first-use behavior MUST be separately evaluated. | P2; MLL, APL | Temporal audit prevents later sessions entering a baseline. |
| APP-012 | The interface MUST distinguish `measurement_only`, `research_estimate`, `inconclusive`, and `invalid`; only `research_estimate` may carry probability. | P0+; APL | State-by-state screenshots and API checks match the LLD. |
| APP-013 | The app MUST NOT show “safe to drive,” a legal clearance, or unsupported intoxication certainty. | P0+; PL, CL | Copy review covers all result, notification, and error screens. |
| APP-014 | Supported-device, accessibility, language, and input-mode limits MUST be explicit; incompatible task adaptations MUST be revalidated. | P2/P3; APL, CL | G-10 lists supported configurations and tested accommodations. |

## 6. Model, data, and inference requirements

| ID | Normative requirement | Phase; owner | Acceptance evidence |
|---|---|---|---|
| MOD-001 | The target MUST be a prespecified independent current-functional-impairment endpoint; exposure and subjective high MUST remain separate labels. | P2; CL, SL | G-01 protocol defines outcome, assessor, timing, and label rules. |
| MOD-002 | Inference MUST NOT require an invented demographic metabolic-clearance formula. | P0+; MLL | Model review identifies measured features and any explicitly evaluated latent model. |
| MOD-003 | Feature construction MUST preserve missingness, censoring, assay basis, provenance, and quality without silently normalizing them to healthy values. | P0+; MLL | Adversarial synthetic records produce the specified validity behavior. |
| MOD-004 | Training and results MUST be pinned to acquisition, assay, task, feature, and model versions. | P2; MLL, EL | Any prediction can be reconstructed from immutable versioned inputs. |
| MOD-005 | Data splits MUST hold out whole people and evaluate later sessions; preprocessing and selection MUST be fit on training data only. | P2; SL, MLL | Split audit and leakage review pass before locked evaluation. |
| MOD-006 | Features MUST use only information available at the check; future measurements and independent outcome assessments MUST NOT enter predictors. | P2; MLL | Timestamp and dependency audit covers each feature and baseline. |
| MOD-007 | The manifest MUST declare lifecycle, endpoint, required channels, compatibility, units/bases, quality rules, calibration, threshold policy, and permitted cohort. | P2; MLL | Manifest review and incompatible-record checks pass. |
| MOD-008 | Lifecycle MUST be `unvalidated`, `active_research`, or `retired`; activation MUST require recorded research authorization. | P0+; MLL, CL | Unauthorized activation and retired-model invocation are rejected. |
| MOD-009 | P0/P1 MUST never emit a probability; simulated required inputs MUST never qualify for a participant research estimate. | P0+; EL | Negative inference cases verify null/absent probability and explicit reason. |
| MOD-010 | A probability MUST require an authorized P2 session, `active_research` model, valid required channels, and compatible protocol/cohort. | P2; EL, MLL | Every gate has both passing and rejecting integration evidence. |
| MOD-011 | Missing channels MAY use a separately qualified model variant; automatic reuse of an incompatible full-channel model is prohibited. | P2; MLL | Variant selection is explicit, versioned, and validated. |
| MOD-012 | Thresholds and calibration MUST be selected before confirmatory testing and frozen with the model artifact. | P2; SL, MLL | Locked analysis plan and artifact hashes predate evaluation access. |
| MOD-013 | Prediction MUST include model version, applicable endpoint, valid-input summary, uncertainty policy, time basis, and outcome state. | P2; EL | Result contract and independent interpretation review pass. |
| MOD-014 | Feature selection MUST compare chemical-only, app-only, combined, and ECG-removed configurations on the same evaluation design. | P2; MLL, IVL | Ablation report supports retained measurement burden. |
| MOD-015 | Model updates MUST require versioned reevaluation and authorization; consumer measurements MUST NOT silently retrain a deployed model. | P2+; MLL | Change-control exercise preserves the prior artifact and results. |

## 7. Alcohol requirements

| ID | Normative requirement | Phase; owner | Acceptance evidence |
|---|---|---|---|
| ALC-001 | Alcohol MUST be a distinct measured channel; physiology or a generic gas-sensor signal MUST NOT be labeled calibrated breath alcohol. | P0+; HWL | Interface and synthetic demonstrations retain channel identity and provenance. |
| ALC-002 | The candidate design SHOULD use a fuel-cell measurement path with controlled sampling; final component choice remains gated. | P1+; HWL | G-11 documents supplier specifications and design tradeoffs. |
| ALC-003 | The channel MUST report mg/L with calibration identity, units, sampling quality, time, and range qualifier. | P1+; EL | Contract fixtures preserve all metadata without unapproved blood conversion. |
| ALC-004 | Mouthpiece hygiene, sample adequacy, environmental effects, calibration interval, and cross-sensitivity MUST be qualified independently. | P1/P2; HWL, IVL | Dedicated alcohol qualification against the selected reference method. |
| ALC-005 | Cannabis/alcohol co-use MUST be a defined study condition or explicitly unsupported cohort; scores MUST NOT be averaged. | P2; CL, MLL | Protocol and model manifest agree on co-use handling. |

## 8. Security, privacy, and operational requirements

| ID | Normative requirement | Phase; owner | Acceptance evidence |
|---|---|---|---|
| SEC-001 | GitHub MUST contain only code, documentation, and synthetic examples; participant data, real eye video, ECG, exports, or credentials are prohibited. | P0+; SDL | Pre-commit/release review and secret/data scan of the staged changes. |
| SEC-002 | Research identifiers MUST be separated from direct identity; access MUST follow least privilege and a defined role matrix. | P2; SDL, CL | Unauthorized-role tests and identity-mapping review pass. |
| SEC-003 | Upload of participant data MUST be explicit and protocol-authorized; basic local operation MUST NOT imply research enrollment. | P2; SDL, APL | Consent/authorization and upload traces demonstrate the boundary. |
| SEC-004 | Protected transport and storage MUST use approved encryption and secret management; secrets MUST NOT be embedded in app or firmware source. | P2; SDL | Deployment configuration and access review satisfy G-12. |
| SEC-005 | Raw optical/cardiac retention MUST be justified, minimized, access-controlled, and bound to a defined retention/deletion policy. | P2; SDL, CL | G-12 states durations and tests deletion across primary/backup workflows. |
| SEC-006 | Logs MUST omit raw health payloads and direct identifiers; audit events MUST still preserve actor, operation, record identity, and time. | P0+; SDL, EL | Representative failure logs pass content review. |
| SEC-007 | Security incidents, lost devices, withdrawal, and data correction MUST have defined operational procedures before participant use. | P2; SDL, CL | Tabletop exercise and responsible contacts documented. |
| OPS-001 | The backend MUST begin as a modular FastAPI application with PostgreSQL; approved raw artifacts MUST use private object storage. | P1/P2; EL | Architecture review confirms boundaries and deployment configuration. |
| OPS-002 | Session submission MUST be idempotent; retries MUST not duplicate specimens, tasks, or finalized results. | P0+; EL | Repeated identical submissions produce one accepted logical record. |
| OPS-003 | Finalized sample/task records MUST be immutable; corrections MUST create linked superseding versions. | P0+; EL | Correction scenario preserves original content and provenance. |
| OPS-004 | Cross-device timestamps MUST use RFC 3339 UTC with explicit clock uncertainty; within-device timing MUST use monotonic milliseconds. | P0+; EL | Clock-drift and reordered-message cases retain interpretable timing. |
| OPS-005 | Offline behavior MUST preserve session state securely where permitted and reconcile explicitly; no unreceived result may appear complete. | P1+; EL, SDL | Network interruption and restart exercises preserve correct terminal state. |
| OPS-006 | Research deployments MUST define backups, restore verification, monitoring, incident ownership, and availability targets. | P2; EL | G-12 documents values and a successful recovery exercise. |

## 9. Validation, commercial, and documentation requirements

| ID | Normative requirement | Phase; owner | Acceptance evidence |
|---|---|---|---|
| VAL-001 | Participant work MUST require an approved protocol, eligibility rules, consent, and appropriate research oversight before collection. | P1/P2; CL | G-07 authorization and staff readiness records. |
| VAL-002 | Reference outcomes MUST be independent of predictor tasks and chemical positivity; assessor blinding and timing MUST be specified. | P2; CL, SL | Outcome manual and data-flow review exclude circular labels. |
| VAL-003 | Sample size MUST follow the endpoint, required precision, repeated-measure structure, intended subgroups, and planned error thresholds. | P2; SL | Approved calculation/simulation at G-08; no arbitrary sample guarantee. |
| VAL-004 | Validation MUST examine route, use frequency, co-use/confounding conditions, supported devices, baseline availability, and intended population limits. | P2; SL, IVL | Prespecified strata and exclusions appear in the final report. |
| VAL-005 | Reports MUST include sensitivity/specificity when an accepted reference standard supports them, otherwise positive/negative percent agreement; include calibration, uncertainty intervals, appropriately qualified prevalence-dependent predictive values, and inconclusive/invalid rates. | P2; SL | Independent report reconciles every enrolled check with its disposition. |
| VAL-006 | Confirmatory validation MUST use a locked pipeline and independent prospective or external evaluation appropriate to the claim. | P2/P3; IVL | G-09 report states independence, limitations, and deviations. |
| VAL-007 | The complete one-sample/one-task workflow MUST be evaluated using information available at each real check, even when a visit contains repeated research checks. | P2; IVL | Temporal audit and study report demonstrate the consumer information boundary. |
| VAL-008 | The intended use and applicable device, laboratory, privacy, and study requirements MUST be determined by the responsible experts before release. | P2/P3; QRL | G-14 documented applicability determination and required evidence. |
| BUS-001 | US$20/month MUST be labeled a hypothesis until hardware terms, consumable allowance, and recurring costs are specified. | P0+; BUL | Commercial material avoids an unverified price/performance promise. |
| BUS-002 | Economic scenarios MUST include consumables, reader yield, calibration, support, warranty, shipping, cloud operation, studies, and applicable compliance. | P1+; BUL | Dated cost model with supplier quotations and sensitivity analysis. |
| BUS-003 | Final feature inclusion SHOULD consider incremental predictive value, completion burden, and lifecycle cost together. | P2/P3; PL, BUL | Product decision cites ablation, usability, and cost evidence. |
| DOC-001 | Documentation MUST distinguish implemented code, synthetic demonstration, proposed design, evidence, and unresolved work. | P0+; EL | Repository review finds no unsupported completion claim. |
| DOC-002 | Every gate MUST have an assigned person before closure and linked evidence; a role label alone is insufficient to close it. | P1+; PL | Gate register contains approver, date, artifact, and decision. |
| DOC-003 | Normative changes MUST update dependent contracts, decisions, requirements, and verification evidence in one reviewed change. | P0+; EL | Change-impact checklist and versioned repository history. |

## 10. Blocking gate register

All gates begin **OPEN**. Quantitative acceptance values are intentionally unset when the evidence or intended use is unresolved. Each owner must freeze its criteria before the confirmatory experiment; passing cannot be defined after observing the result.

| Gate | Required decision or evidence | Owner | Blocks |
|---|---|---|---|
| G-01 | Intended use, independent endpoint, population, time window, meaning of impairment, and error consequences | CL, PL, SL | Model claim and confirmatory study |
| G-02 | Saliva collector, volume/dilution, recovery, handling, storage, adequacy, and free/total basis | ANL | Qualified specimen collection |
| G-03 | Channel-specific LOQ/LOD, range, bias/precision/agreement limits, interference criteria, stability, and turnaround | ANL, IVL | Quantitative portable assay claim |
| G-04 | Optical stimulus bounds, safety, supported cameras, scale, feature repeatability, and quality cutoffs | OL, QRL | Participant optical capture and model use |
| G-05 | ECG power/isolation/contact design, simulator results, electrical-safety controls | HWL, QRL | Body-connected prototype |
| G-06 | Game timing tolerance, supported phones, invalid-trial rules, reliability, baseline protocol | APL, SL | Qualified task feature input |
| G-07 | Protocol authorization, participant eligibility, consent, staffing, collection and adverse-event procedures | CL | Human research execution |
| G-08 | Sample size, label adjudication, splits, metrics, thresholds, uncertainty handling, missingness, subgroup plan | SL, IVL | Confirmatory model evaluation |
| G-09 | Locked analytical/feature/model pipeline, external or prospective performance, incremental-value evidence | IVL, MLL | Any claim of validated performance |
| G-10 | Complete-check duration/completion goals, supported configurations, final enclosure, battery, cleaning, human factors | PL, HWL, APL | Manufacturing specification and consumer workflow |
| G-11 | Alcohol component selection, sampling, calibration, comparison limits, environmental and co-use evaluation | HWL, IVL | Breath-alcohol product claim |
| G-12 | Data access, explicit upload authorization, retention/deletion, security, operational recovery | SDL, CL, EL | Participant-data deployment |
| G-13 | Hardware price/subsidy, included collections, usage distribution, verified cost model, sustainable margin | BUL, PL | Subscription promise |
| G-14 | Intended-use applicability determination, required evidence, labeling, release authorization | QRL, CL, PL | P3 release |

## 11. Traceability and release definition

| PRD family | Implementing requirements | Main verification |
|---|---|---|
| PRD-001–008: invariants and claims | ANA-001/012; APP-012/013; MOD-001/008–010; ALC-001/005 | Session/state review; G-01/G-07/G-09 |
| PRD-009–012: workflow and chemistry | HW-002–004; ANA-001–013; OPS-002–004 | Integration faults and G-02/G-03 |
| PRD-013–017: task, physiology, profile, alcohol | HW-005–010; APP-002–011; ALC-001–005 | G-04/G-05/G-06/G-11 |
| PRD-018–020: datasets and interpretation | MOD-003–013; SEC-001–007; OPS-001–006 | Provenance, inference gate, G-12 |
| PRD-021–025: performance and reliability | VAL-001–007; MOD-014/015; APP-014 | G-08/G-09/G-10 |
| PRD-026–028: economics and open decisions | BUS-001–003; DOC-001–003; VAL-008 | G-13/G-14 and gate register |

### Current software refinement precedence and individual PRD traceability

The 46 active/pending OpenSpec capability files across 11 changes refine this register; their canonical run IDs remain OTGD-002–047 and this register remains OTGD-001. These identifiers track evidence, not new capabilities. [Shared contracts §1](../openspec/changes/production-mobile-platform/shared-contracts.md#1-release-and-workspace-policy) scopes historical fixed-false clauses to legacy Result 0.1.0 and assigns ResearchResult 1.1.0 to the authorized-model-execution amendment with the explicitly restricted qualified-participant-acquisition HR variant. Default measurement behavior and all scientific gates above remain unchanged. [Shared contracts §7](../openspec/changes/production-mobile-platform/shared-contracts.md#7-export-artifact-versions-and-privacy-jobs) and authorized-raw-export govern the complete raw-inclusive archive at 50 MiB uncompressed / 64 MiB ZIP, with lower authority limits honored; a historical larger proposal is superseded.

Each PRD identifier below is independently mapped. Full-register families supply product/scientific requirements; canonical OpenSpec IDs supply software refinements and acceptance scenarios. The canonical ID/path/hash and reverse PRD mappings are in the [run inventory](../docs/factory/otgd-20261025-0555/inventory.json). [HLD](HLD.md) and [LLD](LLD.md) describe implementation boundaries; the [implementation plan](../docs/factory/otgd-20261025-0555/reports/implementation-plan.md) links the remaining bounded gaps to exact files and tests. Source mappings and a written scenario are not executed evidence; current per-case results and independent review remain required. PRD-029–042 trace existing approved scope.

| PRD identifier | Full-register requirements | Canonical software refinements | Verification focus |
|---|---|---|---|
| `PRD-001` | ANA-001/012; APP-012/013 | OTGD-026, OTGD-033, OTGD-035, OTGD-040 | one collection / one task; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-002` | HW-005–009; APP-009/010 | OTGD-024, OTGD-025, OTGD-027, OTGD-043 | pupil / cardiac / exploratory ECG; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-003` | MOD-001/009; APP-012/013 | OTGD-021, OTGD-030, OTGD-034 | measurement defaults; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-004` | MOD-008–011 | OTGD-009, OTGD-011, OTGD-038, OTGD-042 | current independent model admission; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-005` | MOD-002/012; VAL-002/003/006 | OTGD-008, OTGD-041 | prespecified endpoint and error policy; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-006` | APP-013; MOD-013; ALC-005 | OTGD-006, OTGD-019, OTGD-034 | claims and no clearance; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-007` | APP-012/013; MOD-010/013 | OTGD-006, OTGD-026, OTGD-034 | outcome and missingness; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-008` | ALC-001/003/005 | OTGD-019 | separate alcohol evidence; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-009` | APP-001–008; OPS-002–005 | OTGD-026, OTGD-029, OTGD-033 | attempts and orchestration; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-010` | ANA-001–013 | OTGD-035, OTGD-040 | saliva analytical boundary; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-011` | ANA-002–005 | OTGD-035, OTGD-040 | parent THC; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-012` | ANA-002–005; MOD-014 | OTGD-035, OTGD-040 | candidate analytes; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-013` | APP-004–008/014; MOD-014 | OTGD-033 | one continuous task; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-014` | HW-005/006; APP-009 | OTGD-012, OTGD-025 | optical evidence; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-015` | HW-007–009; APP-010; MOD-014 | OTGD-024, OTGD-027, OTGD-042, OTGD-043 | cardiac evidence; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-016` | APP-002/003/011; MOD-006 | OTGD-032, OTGD-026 | optional profile and unknowns; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-017` | ALC-001–005 | OTGD-019 | future fuel-cell mg/L channel; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-018` | MOD-003–007; OPS-003/004; SEC-001–006 | OTGD-008, OTGD-009, OTGD-011, OTGD-041, OTGD-042 | versioned dataset; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-019` | MOD-007–013 | OTGD-006, OTGD-009, OTGD-042 | quality-aware admission; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-020` | APP-012/013; MOD-013 | OTGD-021, OTGD-028, OTGD-034 | scientific and delivery states; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-021` | ANA-005–013; VAL-001–008 | OTGD-035, OTGD-040 | analytical qualification; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-022` | MOD-014; VAL-002–007 | OTGD-008, OTGD-041, OTGD-042 | matched incremental value; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-023` | APP-014; VAL-007 | OTGD-020, OTGD-026, OTGD-033, OTGD-036 | single-check usability; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-024` | VAL-004/005; MOD-013 | OTGD-008, OTGD-041, OTGD-042 | prespecified strata and uncertainty; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-025` | APP-014; VAL-007; OPS-005 | OTGD-020, OTGD-026, OTGD-029, OTGD-033, OTGD-036 | complete-check reliability; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-026` | BUS-001–003 | Full register only | economic feasibility; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-027` | MOD-002/012; VAL-002/003/006/008 | OTGD-008, OTGD-041 | freeze intended use and endpoint; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-028` | HW-001–012; ANA-001–013; SEC-005; BUS-001–003; DOC-001–003 | OTGD-019, OTGD-024, OTGD-025, OTGD-027, OTGD-033, OTGD-035, OTGD-043 | freeze feasibility and release choices; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-029` | SEC-002/004/007 | OTGD-020, OTGD-030, OTGD-037 | guest / identity / sign-out; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-030` | SEC-002/003; MOD-008–010 | OTGD-011, OTGD-038, OTGD-039 | consent / fresh start / withdrawal; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-031` | ANA-001/012; APP-001–008; OPS-002–005 | OTGD-026, OTGD-032, OTGD-033, OTGD-040 | frozen context / attempts; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-032` | APP-004–008/014 | OTGD-033 | native timing and stop; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-033` | HW-003/004/007/012; SEC-004 | OTGD-013, OTGD-023, OTGD-043 | binding and actual adapter scope; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-034` | ANA-001–012; HW-005–009; APP-009/010 | OTGD-012, OTGD-024, OTGD-025, OTGD-027, OTGD-035, OTGD-039, OTGD-040, OTGD-043 | acquisition and laboratory handoff; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-035` | SEC-003/004; OPS-002–005 | OTGD-026, OTGD-029, OTGD-037 | protected save / explicit upload; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-036` | APP-012/013; MOD-013; OPS-003 | OTGD-004, OTGD-006, OTGD-028, OTGD-034 | history / result / immutable lineage; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-037` | SEC-003–005 | OTGD-012, OTGD-013, OTGD-018, OTGD-024, OTGD-025 | default-off recording and cleanup; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-038` | SEC-002/005/007 | OTGD-010, OTGD-018, OTGD-022 | bounded exact-scope export; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-039` | SEC-005/007; OPS-003–006 | OTGD-016, OTGD-031, OTGD-038 | privacy / generation / recovery; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-040` | APP-014 | OTGD-020, OTGD-023, OTGD-025, OTGD-033, OTGD-036, OTGD-037 | accessibility / permission recovery; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-041` | MOD-001–015; VAL-001–007 | OTGD-002, OTGD-003, OTGD-004, OTGD-005, OTGD-006, OTGD-007, OTGD-008, OTGD-009, OTGD-011, OTGD-041, OTGD-042 | governed conditional research; canonical acceptance plus applicable G-01–G-14 evidence |
| `PRD-042` | HW-002; SEC-001/004; OPS-001–006 | OTGD-014, OTGD-015, OTGD-017, OTGD-020, OTGD-044, OTGD-045, OTGD-046, OTGD-047 | environment / preview / release tooling; canonical acceptance plus applicable G-01–G-14 evidence |

A **P0 demonstration** is accepted when synthetic data can complete the documented workflow, failure cases produce correct states, and no clinical probability is emitted. A **P1 feasibility result** is accepted per the prespecified analytical or capture gate and is not a clinical conclusion. A **P2 research estimate** is permitted only through the authorized manifest gate; that permission does not itself validate the model. A **P3 release** requires a separate specification version and evidence supporting the exact intended use.

Release records must identify the requirements satisfied, unresolved deviations, evidence locations, responsible reviewers, software/hardware/assay/model versions, and remaining limitations. A full requirement register can be complete while a physical product is still unbuilt; documentation completeness must never be represented as completed development or proven intoxication detection.
