# Integrated device, app, and model MVP

**Product:** One-The-Go Detection\
**Decision date:** 2026-10-12, America/Chicago\
**Status:** Selected product direction and proposed research milestone; physical sensing, assay feasibility, human training data, and predictive performance remain unqualified.

## Selected direction

The founder has selected **a physical device, companion app, and model as one integrated MVP milestone**, leading toward a pocket consumer product. The MVP is an integrated research prototype: a connected saliva reader, the app's single guided check, and a bounded model evaluated against an independent functional outcome. Software integration, analytical feasibility, and authorized model evaluation are successive parts of that milestone.

The intended future customer is an adult seeking useful information to make everyday decisions in the context of cannabis exposure. The first consumer segment, specific decision, demand, and willingness to complete and pay for the check are still hypotheses. Research participants and operators are the initial users while measurement and predictive evidence are developed.

The [existing-products/refill service strategy](../../specs/research/FAST_MARKET_STRATEGY.md) remains an alternative commercial route. It is not the selected MVP and does not replace the device-and-model objective.

This document clarifies the milestone within the [PRD](../../specs/PRD.md), [architecture decisions](../../specs/DECISIONS.md), and [validation plan](../../specs/VALIDATION_PLAN.md). The [full specification](../../specs/FULL_SPECIFICATION.md) remains the normative requirement register. This scope does not modify source code, contracts, channel requirements, or research/release authority.

## What the integrated prototype must contain

| Component | Minimum scope | Evidence required |
| --- | --- | --- |
| Physical device and saliva path | A connected prototype with one standardized saliva collection and a selected parent delta-9 THC assay/readout pathway. Preserve specimen, collector/cartridge, lot, timing, calibration, quality, units, and assay-basis provenance. A bench enclosure is acceptable before pocket miniaturization. | Actual device operation and reference-method comparison on the intended collection matrix. Selecting a board, receiving BLE packets, or installing firmware is not evidence of chemical sensing. |
| Companion app | One continuous `choice_inhibit_v0` reaction task, guided pupil capture, resting heart-rate capture, contextual profile/use history, synchronized attempts, explicit quality states, and traceable results. Preserve approved retries and failed captures. | Reproducible acquisition with appropriate timing, optical/cardiac configuration, quality and reference checks, plus observed complete-check usability. |
| Bounded model | A versioned, data-only candidate for a specifically defined current functional-performance endpoint in the context of cannabis exposure. Start with a simple model that can be compared with simpler configurations. | Authorized human data, independently assessed outcomes, a prespecified analysis, whole-person holdouts, later-session evaluation, calibration/uncertainty reporting, and evidence of useful incremental value. |
| Integrated workflow | Measurements and model inputs belong to the same eligible check and retain their acquisition, assay, task, feature, and model versions. Research estimates appear only through the existing authority and eligibility gates. | End-to-end traceability, reproducible inference, invalid/inconclusive behavior, and enforcement of approved information and timing boundaries. |

Guided pupil capture and resting heart rate remain required research capabilities under PRD-002; this MVP does not remove them to simplify the story. Dynamic pupil features require their own optical/timing qualification. The currently documented geometry-only authority does not establish pupil-response latency or constriction validity. ECG remains exploratory, additional metabolites remain evidence-driven, and a separately calibrated alcohol channel remains in the longer-term product vision rather than a condition for this initial cannabis MVP.

The model can run on the phone or backend within a supported, qualified configuration; it need not run inside the reader. The current documented execution path uses a governed backend worker. Phone inference would need its own supported implementation and qualification and is not supplied by this scope decision. Final PCB design, production enclosure, manufacturing controls, and a consumer release are later milestones.

## Work still required

The repository already contains substantial application, backend, firmware, acquisition/governance, and model training/execution software. It supplies synthetic examples and conditional research pathways. It does **not** supply a validated saliva assay, qualified human sensor configuration, genuine study approvals, a human training cohort, or a scientifically qualified impairment model. See the [repository evidence boundaries](../../README.md#result-and-release-boundaries), [research execution guide](../RESEARCH_MODEL_EXECUTION.md), and [training/evaluation toolkit](../MODEL_TRAINING_AND_EVALUATION.md).

| Workstream | Remaining work | Accountable expertise needed |
| --- | --- | --- |
| Physical integration | Assemble and observe the board, power, transport, sensor fixtures, reader electronics, and fluid path. Establish actual signal quality and relevant human-contact safety before participant use. | Hardware and acquisition engineering |
| Saliva assay | Select chemistry and collection, define the measurand and reporting range, evaluate recovery/selectivity/repeatability/stability, and compare actual specimens with a qualified reference method. Obtain realistic supplier and consumable costs. | Analytical assay lead and suitable laboratory |
| App measurements | Qualify the exact phone, task timing, optical protocol, resting HR configuration, and feature extraction. Measure failures, retries, duration, and accessibility of the complete procedure. | Mobile, optical/cardiac, and human-factors expertise |
| Human dataset | Approve the endpoint, population, protocol, independent reference procedure, consent/data handling, and sampling plan; collect representative paired observations and failures. | Scientific/clinical investigator and statistical lead |
| Model evaluation | Freeze participant allocation and the analysis, train on eligible development data, lock the pipeline, evaluate unseen participants and later sessions, and compare matched configurations. | ML lead with independent scientific/statistical review |
| Consumer fit and economics | Define a first segment and use case; interview intended customers; test procedure burden, willingness to pay, usage, and hardware/consumable costs. | Founder/product lead |

A qualitative THC-positive result cannot be promoted to a quantitative concentration or impairment label. Delayed laboratory results can support analytical research but cannot become deployed-model inputs if unavailable within the approved single-check decision window. A reference-laboratory-only workflow is useful intermediate work, not completion of the physical saliva-reader objective.

## Model target and evaluation

The target is an independently defined current functional deficit, not simply THC detection, assigned dose, self-reported high, or the app's own reaction-task score. The scientific lead must choose and justify the reference procedure, such as a separate functional battery or specified simulator endpoint. The independent outcome must not incorporate the candidate task, its model output, or its classification.

Before confirmatory evaluation, freeze the endpoint/population, acceptable measurement-to-outcome window, model inputs, preprocessing, operating threshold, uncertainty policy, and acceptance limits. Keep all sessions from a participant outside training when evaluating generalization to new users. Evaluate later sessions and any personalized mode separately using only qualified earlier baselines. Fit preprocessing and tune candidate choices on development data alone.

Compare chemistry-only, app-only, and combined configurations on the same held-out participants, alongside justified simple baselines. Report whether the complete check adds enough benefit to justify its cost and burden. Evaluate ECG and additional metabolites by ablation when included. Report calibration, uncertainty, coverage, subgroup limitations, and invalid/inconclusive sessions with explicit denominators. Do not select a headline accuracy target or sample count without the endpoint, error consequences, and statistical plan.

The existing combined-channel toolkit has four prescribed configurations, including ECG and ECG removal; it also supports a separately prespecified HR-only mode. These software modes do not establish the selected multimodal MVP's validity. If the approved initial study uses a combined configuration without ECG, any required evaluation/contract changes must be versioned and reviewed separately; this document does not implement them or silently reinterpret an existing report.

## Phase boundaries within the milestone

| Phase | Deliverable toward the integrated MVP | Output boundary |
| --- | --- | --- |
| **P0: integration** | Reproducible physical bench/software integration with clearly identified synthetic inputs, task workflow, transport, traceability, and failure handling. | Measurement-only. No functional-impairment probability. |
| **P1: analytical feasibility** | Actual collection/assay/reference comparison and qualified capture configurations, with documented limitations and cost/turnaround feasibility. | Measurement-only. Chemical measurement qualification does not qualify impairment prediction. |
| **P2: authorized research** | Approved participant acquisition, independent outcomes, trained/locked candidate, held-out evaluation, and the integrated device/app/research-model workflow. | A research estimate only for an authorized session, an `active_research` model, compatible qualified inputs, and current required authority. Otherwise retain measurement-only, inconclusive, or invalid states. |
| **P3: possible consumer release** | Evidence for the exact consumer use, prospective performance bounds, human factors, applicable release requirements, manufacturing, and viable economics. | Separate release decision. Completion of the research MVP does not authorize consumer claims or distribution. |

Model-development infrastructure may be built during P0/P1. That does not enable numerical impairment outputs for those sessions. `active_research` means approved for a specified study, not validated for consumers.

## Completion conditions and decision

The integrated research MVP is complete only when the following evidence is reviewable for the exact configuration:

1. The physical reader produces real, traceable saliva measurements whose analytical purpose and limitations are supported by a reference comparison.
2. The app captures the required saliva, single task, pupil, and resting-HR workflow with qualified acquisition, explicit quality states, and observed usability.
3. An authorized dataset has independent functional outcomes, retained failed attempts, appropriate participant/population coverage, and auditable custody.
4. A locked candidate is evaluated on held-out participants and later sessions against the same independent outcome, with simple/comparator models, uncertainty, calibration, and failure denominators.
5. The actual device, app, and governed research-model path operate together without synthetic substitution, information leakage, or bypass of eligibility and authority.
6. The team records whether prespecified scientific and usability acceptance criteria passed, what remains unresolved, and what customer/cost evidence supports the next product decision.

A completed study can reject the product hypothesis. Failed analytical feasibility, inadequate capture, or no useful improvement over a simpler configuration requires an explicit design/scope decision and new evidence before advancing. It is not a reason to relabel exposure as impairment or omit difficult sessions.

Run customer discovery in parallel with engineering and research. Test concrete everyday situations and the complete procedure before committing to subscription allowances or hardware subsidy. Approximately $20/month remains a commercial hypothesis; no interviews, users, pilots, revenue, assay partner agreement, or viable unit economics have been established in the founder's current account.

## Application wording

> We are building an integrated research MVP: a connected saliva-testing prototype, a companion app that captures one reaction task plus pupil and heart-rate measurements, and a model evaluated against an independently assessed functional outcome. The goal is a pocket consumer device. We have built substantial software infrastructure; physical assay qualification, human training data, independent model evaluation, and customer validation are the next work.

This wording describes the selected goal and current evidence. It does not claim that the physical detector or prediction model already works, or that the system establishes cannabis causation, legal intoxication, or clearance to drive.
