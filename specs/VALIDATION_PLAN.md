# Validation plan

**Product:** One-The-Go Detection\
**Specification version:** 0.1.0\
**Date:** 2026-10-10, America/Chicago\
**Status:** Proposed engineering and research plan; no product performance has been demonstrated.

Validation table identifiers such as ANA-02 and BIO-01 are experiment IDs; three-digit IDs such as ANA-002 in FULL_SPECIFICATION.md are normative requirement IDs.

## 1. Purpose and release boundary

This plan evaluates a pocket alcohol/cannabis measurement device and companion app. The proposed cannabis check uses **one saliva collection, one repeated-trial reaction task, a guided pupil recording, and cardiac measurements**, with age, weight, calculated BMI, and cannabis-use history as contextual inputs. ECG is an optional research channel whose additional value must be demonstrated.

The research question is whether this snapshot can predict a precisely defined, independently assessed functional outcome. It does not assume that a saliva concentration, pupil diameter, or assigned cannabis dose establishes intoxication. Broad “cannabis intoxication” has no reference definition adopted by this project; selecting and defending the intended outcome is a release-blocking decision.

Research may collect multiple samples and sessions to characterize performance over time. **Each candidate product prediction must use only the single collection, single task, and other eligible measurements available at its decision time.** Subsequent measurements, reference-laboratory results unavailable to the product, and future outcomes cannot become prediction inputs.

No phase in this specification authorizes a consumer intoxication score, legal-use determination, workplace decision, or driving clearance. The future validated release requires an amended intended-use specification and the evidence gates below.

## 2. Evidence that shapes the experiments

In a controlled study of 20 frequent/occasional users, Swortwood and colleagues measured oral-fluid cannabinoids after smoked, vaporized, and oral cannabis. Early parent-cannabinoid peaks reflected oral deposition. Their laboratory method used hydrolysis, with quantification limits of 0.2 ng/mL for THC and 11-OH-THC and 0.015 ng/mL for THC-COOH. 11-OH-THC was detected infrequently and not beyond 1.5 hours in that protocol. These are properties of that laboratory study, not specifications already achieved by this cartridge. They support a parent-THC feasibility track, exploratory metabolites, and careful separation of hydrolyzed results from free-analyte measurements. [S1]

FDA's diagnostic reporting guidance distinguishes an accepted reference standard from a comparison method. Comparisons against a non-reference standard should be described using positive/negative percent agreement, rather than presented as diagnostic sensitivity/specificity. It also recommends reporting uncertainty and retaining equivocal results in the analysis. This project adopts those reporting principles while separately handling its repeated measurements per participant. [S2]

All numerical targets not explicitly identified as published results are proposed engineering requirements. They become binding acceptance criteria only when approved in a versioned protocol before the relevant data are examined.

## 3. Phases and advancement gates

| Phase | Work allowed by this development plan | Required evidence to advance |
|---|---|---|
| **P0: Synthetic integration** | Simulated cartridge outputs, electronic test signals, app timing fixtures, protocol replay, and synthetic profiles. No functional-impairment probability. | Data contracts, units, state transitions, quality rejection, timestamp handling, and end-to-end traceability pass. |
| **P1: Analytical feasibility** | Qualified laboratory evaluation of assay candidates, collection materials, and reader electronics; cardiac/optical test fixtures. Human-specimen work follows the laboratory's applicable approvals and procedures. | Fit-for-purpose collection/assay evidence, acceptable handling stability, chosen analytes, hardware safety review, and a feasible cost/turnaround estimate. |
| **P2: Supervised research** | Approved observational or controlled studies operated by qualified investigators. Research estimates are limited to approved study contexts. | Locked evaluation of the complete intended configuration, independent outcomes, uncertainty estimates, subgroup reporting, and usable completion rates. |
| **P3: Validated release, future** | A specifically defined product use supported by evidence and the applicable regulatory pathway. | Approved claim, final configuration, prospectively met performance bounds, external validation, manufacturing controls, usability evidence, and release authorization. |

Passing a phase does not establish the next phase's claims. A working Bluetooth prototype is not analytical validation; an accurate chemical assay is not functional-impairment validation.

### P0 verification

Use synthetic records spanning every valid, censored, missing, out-of-range, and failed result state. Exercise disconnects, duplicate packets, interrupted assays, expired cartridge metadata, clock changes, and unsupported model versions. Verify that no synthetic or unvalidated session produces a research probability.

Use an ECG simulator or approved signal fixture for initial cardiac development. Review electrical contact protection, optical exposure, fluid containment, and power architecture before human-contact testing. Battery operation alone is not proof of electrical safety.

### P1 analytical experiment

Start with blank, low, middle, and high concentration materials, then challenge the intended collection matrix and collection hardware. Expand across readers, operators, days, material donors, and cartridge lots. The analytical lead sets replicate counts after initial variance estimates; a single calibration curve or single successful specimen does not pass this gate.

Use traceable reference materials and an independently validated laboratory method. Record analytical failures and reasons. Do not select only easy specimens for method comparison.

### P2 research sequence

First establish usability and measurement repeatability under a supervised protocol. Then run a feasibility study that includes exposed and control conditions and the intended routes/use-frequency groups. Use its variance, failure rates, and outcome prevalence to design a prospectively powered validation study.

A clinical investigator determines eligibility, dosing when applicable, monitoring, session timing, stopping rules, and participant discharge arrangements. This document is not a drug-administration protocol. An appropriately experienced research institution or CRO should own that work.

## 4. Analytical validation

### 4.1 Analytes and specimen identity

The core candidate is **parent delta-9-THC**. THC-COOH and 11-OH-THC remain exploratory until measurement feasibility and additional predictive value justify their inclusion. “All metabolites” is not an assay requirement.

Every result must identify:

- Analyte and isomer specificity, specimen matrix, and collection-device version.
- Free analyte, separately measured conjugate, or a precisely defined hydrolyzed total.
- Reader, cartridge lot, assay/calibration versions, collection time, and analysis time.
- Raw measurement, calculation, dilution correction, quantification limits, and quality flags.
- Whether the value refers to neat oral fluid or the collected oral-fluid/buffer mixture.

Canonical concentration units are **ng/mL**. Preserve original laboratory units and the conversion provenance. For example, 15 pg/mL equals 0.015 ng/mL; 1 microgram/L equals 1 ng/mL. Unit conversion does not correct recovery losses or uncertain collection dilution.

Below-limit results carry their censoring status and limit. They are not measured zeros. Results above the upper limit are not clipped into apparently quantitative values. Ratios require compatible analyte definitions, units, and quantifiable denominators; an unsupported ratio is missing, not infinite or zero.

### 4.2 Assay test matrix

| Test ID | Question and experiment | Acceptance evidence |
|---|---|---|
| **ANA-01** | Can the intended amount of saliva be collected and its dilution known? Challenge low volume, viscosity, collection time, and material recovery. | Documented collection adequacy rule and recovery/dilution uncertainty. |
| **ANA-02** | What are the blank response, detection limit, and quantification limit? Repeat near the lower range using the final matrix. | Empirical limits with prespecified detection probability and precision/bias criteria. |
| **ANA-03** | Is concentration recovery accurate and repeatable across the reporting range? | Bias and imprecision by level, reader, operator, day, and lot. |
| **ANA-04** | Does the response remain interpretable at very high concentrations? | Defined upper range, saturation behavior, and safe out-of-range reporting. |
| **ANA-05** | Do related cannabinoids, conjugates, medications, or other matrix components interfere? | Tested specificity/cross-reactivity panel with concentrations and uncertainty. |
| **ANA-06** | Do food residue, oral-care products, pH, viscosity, or blood contamination affect measurement? | Interference results and justified collection instructions or rejection rules. |
| **ANA-07** | Do storage, transport, read delay, temperature, and humidity alter results? | Supported handling window and operating/storage conditions. |
| **ANA-08** | Does a high specimen contaminate the next result or reusable reader? | Carryover and cleaning/containment evidence. |
| **ANA-09** | Does the cartridge agree with the laboratory method in real specimens? | Paired comparison across the intended range, including censored and invalid results. |
| **ANA-10** | Are calibration transfer, lot release, and expiry rules adequate? | Lot acceptance procedure and stability evidence; no unsupported shelf-life claim. |

The analytical lead must approve numerical bounds before confirmatory testing. A laboratory assay's published quantification limit is a feasibility benchmark, not an automatic requirement for the cartridge.

Where sample volume allows, compare aliquots from the same collection. If separate research collections are necessary, record their timing and collection order and analyze the resulting disagreement. Never describe separately collected specimens as identical split samples.

For reference bioanalysis, the laboratory should assess fit-for-purpose validation against the relevant method framework. FDA's final ICH M10 guidance addresses chromatographic and ligand-binding bioanalysis supporting drug-development submissions; it does not automatically establish the acceptance criteria or authorization pathway for this consumer sensor. [S3]

## 5. Biometrics and reaction-task verification

| Test ID | Channel | Required checks |
|---|---|---|
| **BIO-01** | Pupil recording | Compare extraction with a suitable reference across supported cameras, iris appearances, lighting, glasses, positioning, and motion. Record actual frame timing, stimulus timing, and failed captures. |
| **BIO-02** | Pupil features | Evaluate normalized diameter change, response latency, constriction, and recovery; do not assume dilation direction. Validate absolute millimeters only if spatial calibration supports them. |
| **BIO-03** | Heart rate | Compare with a suitable simultaneous reference over the intended resting range. Characterize motion, contact pressure, perfusion, and missing beats. |
| **BIO-04** | ECG | Test sample timing, gain, waveform quality, electrode contact, clipping, and beat detection. Separate acquisition validity from any hypothesized impairment association. |
| **BIO-05** | Reaction timing | Measure stimulus-to-display and touch-to-event timing with suitable fixtures. Record device/OS/display settings and dropped frames. |
| **BIO-06** | Reaction task | Validate one continuous task containing repeated trials; characterize practice, comprehension, accessibility, interrupted sessions, errors, and response variability. |
| **BIO-07** | Synchronization | Confirm every feature comes from the eligible session window and has a known relationship to the prediction and independent-outcome timestamps. |

The optical configuration requires an exposure/safety review before human use. A brighter light or longer illumination cannot be introduced merely to improve camera signal without reviewing the new configuration. ECG test hardware likewise requires an electrical safety review before body contact.

Resting conditions, task duration, minimum usable trials, and recording-quality thresholds are protocol decisions. The research team must justify them through repeatability and usability evidence. Historical baselines require a defined collection protocol and enough repeated observations to characterize normal variation; a positive residual chemistry result does not alone establish whether a baseline session is suitable.

Evaluate both first-use operation and operation with a stored personal baseline. Avoid making the baseline a silent requirement in a product advertised to work immediately.

## 6. Independent outcome and study dataset

The clinical/scientific lead must approve a target-outcome definition before model development. Possible outcomes include a separately administered functional battery or a specified simulator endpoint. A subjective “feeling high” measure can be a separate outcome, but is not interchangeable with either.

The reference procedure must not incorporate the candidate reaction game's scores, its model output, or its classification. Outcome assessors should be masked to candidate results where practicable. Blood chemistry can provide valuable exposure/reference pharmacology information without becoming a functional-impairment ground truth.

Record exposure/control conditions, route, use frequency, relevant concurrent substances, sleep/activity context, and measurement failures. Include plausible challenging cases such as residual cannabinoids without the target functional deficit and a functional deficit without cannabis exposure. This tests whether the classifier depends on simplistic shortcuts.

Split data by participant for generalization to new users. Keep all records from one session together. Evaluate personalization separately using earlier eligible baseline data and later held-out sessions from the same person. Fit imputation, feature selection, scaling, calibration, and thresholds using training/development data only.

For every prediction, store a manifest of permitted inputs and their cutoff time. An independently collected outcome may be measured afterward under a defined timing tolerance; its values cannot enter the prediction. Samples collected after the cutoff cannot fill earlier missing features.

## 7. Model evaluation and acceptance

Compare prespecified candidates on the same evaluation participants:

1. Chemistry only.
2. Reaction task and biometrics only.
3. Chemistry, task, biometrics, and profile/history.
4. The combined model without ECG.
5. Combined models with and without each exploratory metabolite and personal baseline.

Assess discrimination, calibration, agreement or diagnostic accuracy as justified by the reference, and decision coverage. Report confusion counts, 95% uncertainty intervals, invalid/inconclusive rates, and the denominator behind every percentage. Show predictive values for the observed setting; do not assume they transfer unchanged to another prevalence.

Resample or model uncertainty at participant level to account for repeated observations. Participant, session, and timepoint counts must remain distinct. Select sample size from required precision, expected outcome prevalence, participant clustering, and subgroup objectives. There is no defensible fixed sample size in this specification before those decisions exist.

Report performance by route, use frequency, baseline availability, relevant demographic ranges, device family, and recording conditions. Low numbers in a subgroup indicate uncertainty, not demonstrated equivalence. Retain all attempted checks in an operational analysis so abstention cannot artificially inflate the headline performance.

Tune classification and inconclusive thresholds only on development data. Lock the model, feature pipeline, assay configuration, task, and thresholds before prospective evaluation. If a candidate fails, document the result; a revised candidate needs a new evaluation plan and independent test data.

### Release-blocking decisions

| Decision | Accountable owner | Completion evidence |
|---|---|---|
| Target outcome and reference procedure | Clinical/scientific lead | Signed endpoint specification and rationale. |
| Numerical accuracy/agreement, calibration, and coverage bounds | Clinical lead + statistician + product lead | Prespecified statistical analysis plan with consequences of false results. |
| Study size and subgroup adequacy | Statistician | Precision/power calculation accounting for clustering and missingness. |
| Assay reporting range and precision/bias bounds | Analytical lead | Approved validation protocol and matrix study. |
| Supported phone/cardiac/optical configurations | Engineering + human-factors leads | Verification and usability evidence. |
| Final intended use and applicable pathway | Regulatory lead | Written applicability/claims assessment and necessary agency interactions. |

Until these decisions and their evidence are complete, they remain **TBD and release-blocking**, rather than assumed passed.

## 8. Model and result states

Model lifecycle states are `unvalidated`, `active_research`, and `retired`. `active_research` means approved for the specified study workflow; it does not mean validated for consumers.

| Result state | Meaning | Probability field |
|---|---|---|
| `measurement_only` | Measurements may be available; no eligible research inference is being returned. | `null` |
| `research_estimate` | An `active_research` model is used in its approved study context with acceptable eligible inputs. | Research estimate allowed. |
| `inconclusive` | Measurements or inference do not support an interpretable result under the approved rules. | `null` |
| `invalid` | Acquisition, integrity, provenance, or protocol requirements failed. | `null` |

An `unvalidated` or `retired` model must never populate a probability field. A consumer session cannot become an approved study session merely by accepting ordinary app terms. Keep evidence of study authorization, consent version, model/configuration versions, input manifest, and decision reason with each research result.

## 9. Alcohol channel and combined use

Validate breath-alcohol measurement independently against traceable standards and a suitable reference instrument. Characterize calibration, drift, sampling volume/flow, environment, carryover, interferents, and mouth-alcohol handling. Preserve the distinction between measured breath concentration and any derived blood-alcohol estimate.

NHTSA publishes separate model specifications and conforming-product lists for evidential and screening alcohol instruments. They are useful references when selecting a future intended use; a component purchase or successful bench comparison does not put this integrated device on those lists. [S4]

Evaluate whether the saliva workflow affects breath sampling or vice versa. Validate any proposed collection order and waiting instructions. A cannabis model must not silently treat alcohol as absent when no eligible alcohol measurement exists. Predictions involving co-use require explicit training/evaluation evidence rather than adding two independent scores.

## 10. Study governance, product applicability, and records

For the United States, determine device status from the actual intended use and indications; this document does not assign a class or presume a 510(k), De Novo, or exempt route. FDA describes intended use as a starting point for that determination. [S5]

FDA guidance requires RUO/IUO labeling to be consistent with actual intended use and distribution circumstances. Adding “research use only” is therefore not a substitute for deciding how this product and its studies will be used. [S6]

The research sponsor must obtain the applicable ethics, consent, device-study, and controlled-substance determinations before enrollment. FDA notes that some IVD investigations are exempt from most IDE provisions under specified conditions; this should be assessed rather than assumed. The added optical/cardiac functions and any drug administration also require consideration. [S7]

If the commercial product falls within the applicable medical-device framework, assess its quality-system obligations under the current **QMSR**, effective February 2, 2026. FDA describes its scope and exceptions; the date is already past at this specification's issue date. [S8]

An electrical safety specialist should choose the applicable standard family for the final integrated system. IEC 61010-2-101 explicitly covers IVD equipment, including self-tests; do not automatically apply only IEC 60601 to every subsystem. Evaluate contact materials, optical exposure, EMC, battery behavior, and cleaning according to the actual design. [S9]

Research records must link requirement, protocol, configuration, raw observation, deviation, analysis, and conclusion. Raw ECG and eye recordings require restricted access and explicit study consent; retain only justified information under the approved retention policy. **No real participant records, identifiable images, biosignals, credentials, or consent documents belong in this repository.** Use synthetic fixtures in software tests.

## Sources

- **[S1]** Swortwood et al. *Cannabinoid disposition in oral fluid after controlled smoked, vaporized, and oral cannabis administration*. [Primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5357602/).
- **[S2]** FDA. *Statistical Guidance on Reporting Results from Studies Evaluating Diagnostic Tests*. [Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda).
- **[S3]** FDA. *M10 Bioanalytical Method Validation and Study Sample Analysis*, final, November 2022. [Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/m10-bioanalytical-method-validation-and-study-sample-analysis).
- **[S4]** NHTSA. *Alcohol Measurement Devices*. [Specifications and lists](https://www.nhtsa.gov/drunk-driving/alcohol-measurement-devices).
- **[S5]** FDA. *How to Determine if Your Product is a Medical Device*. [Official guidance page](https://www.fda.gov/medical-devices/classify-your-medical-device/how-determine-if-your-product-medical-device).
- **[S6]** FDA. *Distribution of In Vitro Diagnostic Products Labeled for Research Use Only or Investigational Use Only*. [Final guidance](https://www.fda.gov/media/87374/download).
- **[S7]** FDA. *In Vitro Diagnostic Device Studies—Frequently Asked Questions*. [Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/in-vitro-diagnostic-ivd-device-studies-frequently-asked-questions).
- **[S8]** FDA. *Quality Management System Regulation*. [Current framework](https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr).
- **[S9]** IEC. *IEC 61010-2-101:2018*. [Scope](https://webstore.iec.ch/en/publication/60197).

Sources checked on 2026-10-10, America/Chicago. Standards editions and regulatory applicability must be rechecked when the final product and study configurations are selected.
