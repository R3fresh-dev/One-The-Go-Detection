# Product requirements document

**Product:** One-The-Go Detection\
**Version:** 0.1.0\
**Decision date:** 2026-10-10, America/Chicago\
**Status:** Proposed research and engineering baseline; no device, assay, or prediction model is validated.

## 1. Product purpose

Develop a pocket device and mobile application that combine a quantitative saliva measurement, a single continuous reaction task, guided pupil measurements, and cardiac measurements to investigate current functional impairment in the context of cannabis exposure. Preserve a separate breath-alcohol channel in the eventual all-in-one product.

The initial deliverable is an integration and research platform. It must make chemical measurements, task performance, physiological signals, provenance, quality, and uncertainty available for disciplined evaluation. A future product claim depends on proving that the exact deployed combination predicts an independently defined outcome in the intended population.

The central product hypothesis is that combining current chemical and functional measurements improves prediction enough to justify the effort, cost, and uncertainty of the complete check. The commercial hypothesis is a consumer subscription around **US$20 per month**. Neither predictive performance nor viable unit economics has been established.

This PRD specifies what to build and evaluate. [FULL_SPECIFICATION.md](FULL_SPECIFICATION.md) is the normative requirement register. [DECISIONS.md](DECISIONS.md) contains the common architectural choices; [HLD.md](HLD.md) and [LLD.md](LLD.md) describe implementation. [VALIDATION_PLAN.md](VALIDATION_PLAN.md) defines the evidence program.

## 2. Problem and proposed value

The user wants a compact, integrated check that uses one saliva collection and one game rather than a series of separate consumer tests. The desired result is an estimate of current cannabis-related impairment, supported by measurements that address both exposure and present function.

The proposed value is convenience plus better-supported interpretation. The research must determine whether those benefits exist. A combined system that performs no better than a simpler test, produces frequent inconclusive results, or requires a cartridge that cannot meet its analytical specification would not satisfy the hypothesis.

The project must keep four questions distinct:

1. Was a particular cannabinoid detected in the specimen?
2. Does the evidence support recent cannabis exposure?
3. Is independently measured functional performance impaired now?
4. Is the person reporting that they feel high?

The future primary prediction target is question 3, in the context of cannabis exposure. Questions 1, 2, and 4 can support research but must not silently replace that target. The specifications do not define a safe-to-drive determination, a legal intoxication determination, or an estimate of individual hepatic metabolic clearance.

## 3. Users and phases

| Phase | User and setting | Product value available in this phase | Advancement condition |
|---|---|---|---|
| **P0: integration prototype** | Engineers working with synthetic inputs and signal simulators | Exercise the session workflow, hardware communications, quality states, and data contracts | Reproducible bench integration and explicit separation of simulated data |
| **P1: analytical feasibility** | Assay scientists and authorized research operators | Evaluate specimen collection and candidate assay channels against reference methods | Analytical performance and portable-sensor feasibility gates pass |
| **P2: controlled research** | Approved study personnel and eligible, consented participants | Collect paired measurements and evaluate versioned models against independent outcomes | Prospective analytical, model, human-factors, and applicability gates pass |
| **P3: possible product release** | A defined adult consumer population, if supported by evidence and applicable requirements | Only the validated intended use and labeling approved for that release | Separate release authorization; not included in v0.1.0 |

The initial prototype is not a public self-assessment service. The adult age range, recruitment criteria, and permitted study setting remain decisions for the research protocol. An entered age does not itself authorize participation.

### Primary user needs

- **Participant:** Understand the procedure, complete a short guided check, and know whether capture succeeded.
- **Research operator:** Identify missing or invalid inputs, preserve specimen identity, and complete the session without manual relabeling of finalized records.
- **Assay scientist:** Compare candidate sensor results with reference laboratory results while retaining units, censoring, collection conditions, calibration, and lot information.
- **Model researcher:** Reconstruct exactly which measurements were available at prediction time and evaluate new people and later sessions independently.
- **Engineer:** Develop electronics and software with synthetic data before body-connected hardware or human sampling is authorized.
- **Potential future consumer:** Obtain an understandable result appropriate to the validated intended use, including uncertainty and an inconclusive outcome when warranted.

## 4. Product invariants

| ID | Requirement |
|---|---|
| PRD-001 | A valid consumer-format check MUST require one saliva collection and one continuous reaction task. Multiple channels may be measured from that collection. |
| PRD-002 | The check MUST also support guided pupil capture and resting heart-rate capture; ECG MUST remain an exploratory input until its incremental value and hardware approach are justified. |
| PRD-003 | P0 and P1 MUST produce measurement-only outputs, never an intoxication probability. |
| PRD-004 | A P2 probability MUST require an authorized research session, an `active_research` model, a compatible feature contract, and all model-required valid channels. |
| PRD-005 | The future impairment endpoint, intended population, operating threshold, and acceptable error rates MUST be selected before confirmatory evaluation. |
| PRD-006 | A model result MUST NOT be presented as proof of cannabis causation, a legal determination, or clearance to drive. |
| PRD-007 | The product MUST retain distinct invalid, inconclusive, measurement-only, and research-estimate outcomes. Missing information MUST NOT be interpreted as a normal measurement. |
| PRD-008 | Alcohol MUST remain a separately measured and separately reported channel; cannabis physiology MUST NOT substitute for a breath-alcohol measurement. |

One collection does not prohibit an authorized repeat after an invalid specimen. A retry is a separately identified attempt, not an invisible replacement. Repeated research visits are permitted and are needed to evaluate change over time, but each simulated consumer check must obey the single-check information boundary.

## 5. Consumer-format research journey

### Before the check

The app identifies the participant through a study identifier, verifies that the permitted workflow is available, and explains the measurements and data handling. Age, height, weight, calculated BMI, and cannabis-use frequency are recorded with timestamps and units. Route and timing context can be entered when known. Unknown values remain explicit.

Personalization is optional. A participant with qualified earlier baseline sessions may use a compatible personalized research mode. A first-use participant receives only a model mode evaluated for first use. The system cannot fabricate a baseline from population averages or use later measurements to improve a previous prediction.

### During the check

The app creates a session and acquires a standardized saliva specimen through the collection method selected by the analytical program. Collection volume or dilution, specimen identity, assay basis, timing, cartridge or batch details, and quality are retained. Candidate chemistry is measured by a reference laboratory or prototype system with explicit provenance.

The app guides the participant through pupil capture and cardiac capture. Acquisition includes environmental and signal-quality information. Exact optical stimulus settings remain blocked until the optical protocol is approved. Early ECG work uses a simulator; an electrical-safety gate applies before a body-connected prototype is used.

The participant completes **one continuous task**, `choice_inhibit_v0`, comprising six practice trials and 60 scored trials: 48 go and 12 no-go stimuli. The nominal task duration is approximately two minutes, a proposed design target. Event timing, permitted input behavior, interruption rules, and derived features belong to the LLD. The exact task is a research candidate, not an established diagnostic instrument.

The final sequence and maximum interval between channels will be frozen by the study protocol. Every component is timestamped so that a delayed assay result is not confused with a later physiological state. A valid claim of a near-current check will require an acceptable collection-to-result interval.

### After the check

The session is finalized only when required records are present or their absence is explicitly recorded. P0 and P1 show measurement capture and quality. P2 may show a research estimate only under the inference gate. The interface identifies which channels contributed and whether the result is incomplete, without suggesting that a missing channel was normal.

The app preserves an audit trail of retries and corrections. Approved research uploads are separate from basic operation and use the data permissions of the study. A disconnected device must not appear to have completed an assay that never finished.

## 6. Capability scope and priorities

| ID | Capability | Priority and completion meaning |
|---|---|---|
| PRD-009 | Standardized session orchestration | P0 MUST establish a complete synthetic workflow with unique attempts, timestamps, quality, and terminal states. |
| PRD-010 | Quantitative saliva interface | P1 MUST establish reliable specimen handling and a reference-laboratory comparison before any portable concentration claim. |
| PRD-011 | Parent THC channel | P1 MUST evaluate delta-9 THC first. Selection of additional channels requires analytical feasibility and added-value evidence. |
| PRD-012 | Additional saliva metabolites | THC-COOH and 11-OH-THC SHOULD be investigated; neither is promised as a functional cartridge channel in v0.1.0. |
| PRD-013 | One repeated-trial game | P0 MUST support the task contract; P2 MUST evaluate reliability and independent predictive value. |
| PRD-014 | Dynamic pupil measurements | P1/P2 MUST establish acquisition quality, valid units, optical controls, and repeatability before features enter a model. |
| PRD-015 | Heart rate and exploratory ECG | Cardiac capture MUST preserve signal quality and context; an ECG-only benefit MUST be measured by ablation. |
| PRD-016 | Profile and use history | The app MUST preserve source, measurement date, units, and unknown values; demographics MUST NOT determine an assumed clearance rate. |
| PRD-017 | Separate alcohol channel | The design SHOULD reserve integration capability; alcohol performance claims require a calibrated breath system and dedicated validation. |
| PRD-018 | Versioned research dataset | P2 MUST support reconstruction of the exact specimen, task, device, calibration, feature, and model versions. |
| PRD-019 | Quality-aware research result | Inference MUST enforce the release manifest and required-channel rules without fallback to an incompatible model. |
| PRD-020 | Understandable session feedback | The app MUST distinguish capture success, analysis availability, and a research prediction. |

### Out of scope for this baseline

The baseline does not include a completed THC cartridge chemistry, manufacturing-ready PCB, released consumer scoring algorithm, clinical diagnosis, treatment recommendation, driving authorization, or law-enforcement or employment deployment. It does not prescribe home cannabis dosing or participant self-experimentation. A microcontroller prototype and synthetic data generator do not constitute a chemical detector.

Consumer distribution, medical-device applicability, manufacturing certification, approved labeling, and final pricing are gated future decisions. No cloud service is deployed merely because an architecture is documented.

## 7. Evidence and product assumptions

The project has a plausible multimodal research basis. A study of 125 adults evaluated blood cannabinoids, tablet psychomotor testing, and handheld pupillometry together against a driving-simulator outcome. This is precedent for testing combined signals; its results do not establish the performance of saliva, a phone camera, or this task. [Bird et al., 2026](https://pubmed.ncbi.nlm.nih.gov/42297468/).

A controlled smartphone-eye study included 12 cannabis recipients and investigated recordings under different lighting conditions. It supports evaluating a guided camera method and its acquisition conditions, rather than treating pupil size alone as a universal intoxication marker. [Kuijpers et al., 2025](https://pubmed.ncbi.nlm.nih.gov/39840007/).

Controlled research has also evaluated an app-based performance assessment after oral and vaporized cannabis. That evidence supports the measurement category, not the untested `choice_inhibit_v0` implementation. [Spindle et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34049452/).

The broader evidence ledger and limitations belong in [SOURCES.md](SOURCES.md). None of these studies is a transferable product accuracy claim. The major assumptions to test are portable saliva quantification, a tolerable complete-check duration, usable eye recordings across supported devices, independent model generalization, and sustainable cartridge economics.

## 8. Success measures and decision rules

| ID | Measure | Definition and product decision |
|---|---|---|
| PRD-021 | Analytical usefulness | Compare each intended cartridge channel with a traceable reference method over a prespecified range, including censored and invalid results. Freeze acceptance limits before qualification. |
| PRD-022 | Independent prediction value | Compare chemistry alone, app signals alone, and the combined model against the same independent outcome. Require evidence of useful incremental benefit. |
| PRD-023 | Single-check usability | Measure completion rate, duration distribution, retries, specimen failures, camera failures, and task interruptions using the intended workflow. |
| PRD-024 | Generalization | Report errors and calibration for held-out people, later sessions, supported devices, consumption routes, use-frequency strata, and first-use versus personalized modes. |
| PRD-025 | Operational reliability | Measure record completeness, upload reconciliation, recovery after interruption, and traceability of finalized results. |
| PRD-026 | Economic feasibility | Build usage-based cost scenarios before selecting subscription allowances or promising a hardware subsidy. |

The performance scorecard must include sensitivity/specificity when supported by an accepted reference standard; otherwise report positive/negative percent agreement against the prespecified comparator. Include calibration, confidence intervals, predictive values with appropriately qualified target-population interpretation, and the rate and causes of inconclusive results. Overall accuracy alone is insufficient for a product decision. The study plan must state how invalid and inconclusive sessions affect the denominator so that rejecting difficult cases cannot silently inflate the reported result.

Numerical clinical success thresholds are intentionally unresolved release blockers. Selecting arbitrary percentages now would create unsupported commitments. The clinical and statistical leads must choose them from the intended use, consequences of each error type, and prospective study design.

## 9. Commercial hypothesis

The proposed subscription is approximately US$20 per month. The business model must specify whether hardware is purchased separately, financed, subsidized, or replaced under subscription, and how many single-use collections are included. “Unlimited testing” must not be promised before usage and variable costs are understood.

The economic model must include reader manufacturing and yield, saliva collectors and cartridges, shipping, calibration, expired stock, warranty replacement, returns, study costs, software operation, support, and applicable compliance costs. Cost evidence should come from dated supplier quotations and measured process assumptions. Prototype purchase prices are not manufacturing quotes.

Early value testing should establish whether intended users will complete the full procedure and pay for the defined benefit. Hardware miniaturization and ECG inclusion should follow evidence of their contribution. If portable metabolite channels or ECG add cost without sufficient benefit, the product decision is to revise the design or intended use openly, not to hide the missing capability.

## 10. Milestones, owners, and stopping conditions

| Milestone | Accountable role | Deliverable and exit condition |
|---|---|---|
| P0 integration | Engineering lead | Reproducible simulator workflow, documented interfaces, quality-state demonstration, and no probability on synthetic inputs |
| P1 assay and capture feasibility | Analytical lead; hardware and optical leads | Selected collection method, reference-method plan, assay feasibility data, repeatable app signals, and body-connected hardware gate if required |
| P2 study readiness | Clinical lead; statistical lead | Approved protocol, frozen endpoint, intended population, independent outcomes, split plan, analysis plan, and data governance |
| P2 model qualification | ML lead; independent validation lead | Locked model and thresholds, complete provenance, independent evaluation, and justified feature set |
| P3 release consideration | Product lead; clinical lead; regulatory/quality lead | Evidence supports the exact intended use, applicable requirements are resolved, and economics and human factors are acceptable |

The project must pause a dependent workstream if its required gate is unresolved. Examples include a cartridge that cannot quantify the intended channel, an unsafe ECG connection, unusable camera data on supported phones, a model that learns exposure rather than the chosen outcome, or no useful improvement over a simpler configuration. A pause is a decision to resolve evidence, change scope, or stop that approach; it is not a reason to substitute simulated success.

## 11. Open decisions and acceptance of this PRD

| ID | Decision still required | Owner | Blocking phase |
|---|---|---|---|
| PRD-027 | Freeze intended use, primary impairment outcome, population, thresholds, and collection-to-result interval | Clinical and product leads, with statistical lead | P2 confirmatory evaluation and all P3 claims |
| PRD-028 | Select collection/cartridge chemistry, cardiac implementation, optical protocol, supported phone list, final retention policy, and subscription allowance | Respective analytical, hardware, optical, app, data, and commercial leads | Respective feasibility and release gates |

This PRD is accepted as an engineering baseline when every requirement maps to the full specification, every unresolved gate has an accountable role, and the repository clearly distinguishes specification from implementation. Acceptance does not authorize human research, make the algorithm validated, or approve a consumer release. Changes to the one-sample/one-task invariant, target outcome, analyte semantics, or inference lifecycle require a new documented decision and updates to all dependent contracts.
