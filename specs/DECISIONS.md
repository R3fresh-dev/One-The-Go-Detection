# Architecture and product decisions

Version: 0.1.0. Decision date: 2026-10-10, America/Chicago. Status: proposed development baseline; no device, assay, or model has been clinically validated.

This file resolves choices used by the PRD, HLD, LLD, full specification, and starter guide. A change to a normative choice requires a versioned decision and updates to dependent contracts. Evidence and unresolved scientific questions are catalogued separately.

| ID | Decision | Reason and consequence |
|---|---|---|
| ADR-001 | Preserve one saliva collection and one continuous reaction task per valid consumer check. | The app also guides pupil and cardiac capture. A replacement after an invalid capture is a retry, not a requirement for serial saliva sampling. Research visits may collect multiple independently timestamped checks. |
| ADR-002 | The intended future output is probability of a specifically defined current functional impairment endpoint in the context of cannabis exposure. | Recent exposure, self-reported high, and functional impairment are separate labels. No prediction of metabolic clearance or safe-to-drive certification is specified. The endpoint and operating threshold remain release blockers. |
| ADR-003 | Phase P0 is an integration prototype, P1 is analytical feasibility, P2 is controlled research, and P3 is a possible validated product release. | No P0 or P1 session produces an intoxication probability. P3 depends on analytical, clinical, human-factors, and applicable regulatory gates; it is not a scheduled launch commitment. |
| ADR-004 | Use Arduino Nano ESP32 for the first electronics prototype, with an Arduino C++ firmware codebase. | It offers a practical USB and BLE development path. The supplied first sketch emits synthetic serial data only. BLE, sensors, enclosure, battery circuitry, and any assay remain implementation work. |
| ADR-005 | Use the smartphone for the game, guided eye capture, workflow, and local quality checks. | React Native with native Swift/Kotlin capture and timing modules is the proposed app stack. The phone is not assumed to chemically sense THC or to acquire an ECG without electrical-contact hardware. |
| ADR-006 | Start chemistry with parent delta-9 THC; evaluate THC-COOH and 11-OH-THC as additional assay channels. | Assay sensitivity, selectivity, free/total basis, recovery, and incremental predictive value must be demonstrated. No saliva cartridge design or THC sensing chemistry is selected by choosing a microcontroller. |
| ADR-007 | Use a common analyte envelope with canonical saliva concentrations in ng/mL. | Preserve original units, qualifier, assay basis, limits, lot, calibration, time, and provenance. A result below a limit is censored, not zero. Missing, invalid, and out-of-range are different states. |
| ADR-008 | ECG is an exploratory research input; resting heart rate is the initial cardiac feature. | ECG-derived features must demonstrate added value. Early ECG evaluation uses a signal simulator. A body-connected prototype requires an electrical-safety review and an appropriate isolated power design. |
| ADR-009 | Eye features describe the pupil light response, not dilation in a fixed direction. | Capture settings, illumination, frame timing, iris segmentation, and optical safety must be validated. Exact light intensity and exposure configuration are blocked pending the optical study. |
| ADR-010 | One game can contain repeated choice and inhibition trials. | The initial research task, choice_inhibit_v0, uses 60 scored trials with 48 go and 12 no-go stimuli after six practice trials. Its nominal duration is about two minutes, a design target rather than a validated minimum. The LLD defines event timing and outputs. |
| ADR-011 | Retain age, height, weight, BMI derived from height/weight, use-frequency history, and optional route/timing context. | Treat self-report as fallible and allow unknown values. Store both raw performance and optional changes from a qualified personal baseline. First-use and personalized model modes require separate evaluation. |
| ADR-012 | Use a Python/FastAPI modular backend and PostgreSQL for the research data service; private object storage holds approved raw artifacts. | Local synthetic work can run without a cloud account. An AWS deployment is a proposed future option, not a resource created by these specifications. No unnecessary microservices are required. |
| ADR-013 | Inference is versioned and gated by a model manifest. | Lifecycle values: unvalidated, active_research, retired. Outcome states: measurement_only, research_estimate, inconclusive, invalid. Only an authorized controlled-research session with an active_research model and valid required channels may carry a probability. There is no consumer clinical release mode in v0.1.0. |
| ADR-014 | Keep alcohol as a separate channel in the all-in-one vision. | A future calibrated fuel-cell system reports breath alcohol in mg/L with quality and calibration metadata. Do not derive alcohol from cannabis physiology, combine scores by averaging, or substitute a generic gas sensor for a calibrated breath instrument. Alcohol co-use is a validation condition for the cannabis model. |
| ADR-015 | Treat approximately US$20/month as a business hypothesis. | Cartridge usage, sensor life, replacement, support, studies, manufacturing, and applicable compliance costs are unknown. No viable cost-of-goods or margin is asserted. |
| ADR-016 | Store only synthetic examples and documentation in GitHub. | Participant identifiers, health measurements, facial video, ECG recordings, credentials, keys, and production exports must not enter this repository. Research upload is explicit and separate from basic app operation. |
| ADR-017 | Pin every training row and result to its acquisition, assay, task, feature, and model versions. | Hold out whole people and later sessions. No future measurements, outcome assessments, or post-session information may leak into an input vector. A baseline cannot use observations later than the evaluated check. |
| ADR-018 | Quantitative prototype budgets and engineering targets are proposed, not measured product specifications. | The full specification distinguishes requirement, design target, evidence, and unresolved decision. Mechanical drawings, final PCB files, manufacturing BOM, regulatory determination, and performance claims remain blocked until their named gates. |

## Canonical contract vocabulary

- Saliva analytes: THC, THC_COOH, OH11_THC.
- Reading qualifiers: quantified, below_loq, above_range, not_detected, not_measured, invalid.
- Provenance: simulated, reference_lab, prototype_sensor, validated_sensor.
- Assay basis: free, total_after_hydrolysis, unspecified. The last is permitted for recording an unresolved import, but never for an input to a model requiring a defined basis.
- Supported profile age range is an unresolved study decision. Early study proposals are adults only; an age value never itself authorizes enrollment.
- Clock storage: RFC 3339 UTC timestamps for cross-device alignment plus monotonic milliseconds for within-device ordering. Clock uncertainty is explicit.
- Raw ECG unit: mV. Heart rate: bpm. Pupil diameter: mm only with validated scale; normalized measures must not be mislabeled mm. Reaction times: ms. Breath alcohol: mg/L.
- Sample and task records are immutable once finalized. Corrections create new versions linked to the superseded record. There is no silent replacement of a finalized result.

## Document precedence

1. A future applicable law, approved protocol, or formal risk control takes precedence within its scope; these documents do not decide legal applicability.
2. FULL_SPECIFICATION.md is the requirement register, including acceptance criteria and unresolved gates.
3. Machine-readable contracts specify field types and structural constraints; the LLD supplies cross-field and state-machine semantics.
4. DECISIONS.md records architectural choices; PRD and HLD supply purpose and context.
5. Starter examples are explicitly incomplete implementations. They do not supersede requirements.
