# Faster market-entry strategy

## On-the-Go Detection: a commercial launch that funds the all-in-one device

**Prepared:** October 11, 2026 UTC / October 10, 2026 America/Chicago.  
**Basis:** The product specification at [85a1545213dd6a12d2b566ffd9e596933358f405](https://github.com/R3fresh-dev/One-The-Go-Detection/tree/85a1545213dd6a12d2b566ffd9e596933358f405), the user's single-pocket-device vision and $20/month target, and the accompanying [FDA regulatory assessment](FDA_REGULATORY_ASSESSMENT.md).  
**Status:** Recommended strategy and proposed first-release scope. This document does not change the normative PRD, authorize a study, establish supplier agreements or close a release gate.

## 1. Recommendation

**Launch the service around existing legally marketed products first, develop a simpler all-in-one exposure-testing device with an experienced manufacturer in parallel, and retain the impairment system as a later research program.**

This separates the first revenue milestone from the hardest scientific problem in the repo: validating an individualized current-impairment probability. It preserves the single-instrument destination while giving the business an earlier opportunity to learn whether customers value convenient testing, refills and result history.

The initial service would supply an existing OTC oral-fluid THC test and a legally marketed pocket breathalyzer through an appropriate domestic distribution arrangement. The first app would provide general education, refills, support and clearly attributed result history. The next physical product would combine preliminary qualitative parent-THC screening and separately qualified breath alcohol. Metabolites, physiological sensing and impairment prediction would continue through the existing research gates.

**Why this can reduce FDA work for the first offering:** FDA distinguishes distribution of another manufacturer's unchanged product from making or materially changing a device. It also distinguishes software that solely stores/displays existing results from software that measures, interprets or controls a device. Those are substantive activity and function boundaries, not a disclaimer strategy. [S01–S06]

No currently authorized, commercially available, single alcohol-plus-THC pocket instrument has been verified in this research. Selling existing products together is an interim service offering; the subsequent integrated instrument is the original physical vision.

## 2. Compare the three routes

| Route | What customers receive | Principal regulatory/evidence work | Assessment of speed |
|---|---|---|---|
| **1. Existing products + service app** | Finished OTC THC test, existing breathalyzer, replenishment and result history | Verify exact product/label scope, distribution role, app's limited functions and commercial operations | **Best first-revenue candidate.** May avoid a new device premarket submission for this unchanged distribution and genuinely non-device software scope. Sourcing and execution still need verification. |
| **2. OEM all-in-one exposure device** | One pocket instrument with qualitative THC screening and separate breath alcohol | Final system, collector/reader, integration and self-use evidence; manufacturer responsibilities and change/submission assessment | **Preferred first custom product.** Reuse a supported finished design where possible. No fixed review duration or automatic exemption is established. |
| **3. Full multimodal impairment system** | Quantitative analytes plus pupil/cardiac/task inputs and individualized impairment output | New endpoint, independent clinical evidence, software/model performance, physiological safety, human factors and lifecycle controls | **Keep in R&D.** Its scientific and regulatory uncertainties should not control the first revenue date. |

The speed rankings are planning judgments, not agency timelines. If one integrated instrument is mandatory for the first sale, Route 2 becomes the initial route and the schedule must include its actual remaining evidence and any required review. There is no basis yet for promising that new instrument in 30 or 90 days.

## 3. Concrete first-release scope

### Customer proposition

Proposed positioning for review against the selected suppliers' actual labeling:

> One place to manage your breath-alcohol results, THC screening results and test refills.

Describe the individual tests accurately, identify their manufacturers, and preserve their instructions and limitations. A THC result remains the selected test's preliminary screen; a result entered into the app is labeled as user-entered. Consumer-facing copy should describe the actual first offering, while the integrated device appears separately as a development goal.

### App features to include

| Function | Proposed initial behavior | Reason |
|---|---|---|
| Orders and membership | Purchase, replenish, manage deliveries, cancel and obtain support | Directly tests the convenience/subscription proposition. |
| General education | Explain screening terminology and link to the supplier's current instructions | Provides useful context without calculating a personal medical conclusion. |
| Result history | Manually enter the supplier-reported result, units where applicable, date/time and product source | Avoids developing a new measurement method. FDA lists relevant logging and storage/display examples. [S05, S06] |
| Corrections and export | Correct a mistaken entry with clear provenance; export the entered history | Supports useful, trustworthy records without deriving a new score. |
| Service reminders | Refill and manufacturer-specified service/calibration scheduling | Supports maintenance and supply; any actual device procedure stays within the established workflow. |
| OEM data import, later | Faithfully import existing results through a documented, permitted read-only interface | Can improve convenience if the function remains transfer/storage/display and does not control or interpret the instrument. [S05] |

For the first app, exclude automated strip-image interpretation, line-intensity quantitation, custom breath-test initiation/calibration, assay control, pupil/ECG/PPG acquisition, clinical reaction-task scoring, impairment probability and clearance countdowns. These are scope reductions in the released product, while the existing research specification retains the longer-term work.

A new name for an unchanged impairment algorithm would not produce the same reduction. The commercial implementation and claims must match.

The full device's software-submission, QMS and section 524B program should not automatically become prerequisites for a separately scoped, genuinely non-device service app. Security, privacy, truthful claims and reliable operation still need an appropriate implementation for the actual data and business roles. [S05, S06; assessment sections 5 and 7]

## 4. Use existing products without accidentally becoming the new manufacturer

### Begin with a domestic distribution arrangement

Prefer sourcing through an established U.S. supplier while preserving the finished products, original packaging, instructions and supported use. FDA's activity table lists a domestic distributor that does not import as not requiring device establishment registration, listing or its fee in that role. Importing, specification development, relabeling, repackaging and kit assembly are different activities. [S02]

FDA's 510(k) overview and distributor FAQ support distribution of another manufacturer's product without a new distributor 510(k) in appropriate unchanged circumstances. Section 807.85(b) also provides a conditional own-name distribution/repackaging exemption where its conditions are met. This is not a transfer of authorization to a redesigned instrument or a different indication. [S01, S03, S04]

**Practical first arrangement:** fulfill orders for the independent finished products with their labeling intact, and put the service brand on the ordering/support experience. FDA excludes shipping containers from its repackager definition. Review any new retail presentation or claim of a combined device before assuming it remains the same activity. [S02]

Private labeling can be considered with the manufacturer after exact responsibilities and labeling are settled. A proper “Distributed by” relationship is different from changing the collector, chemistry, read method, indicated user or result meaning. The latter changes may affect safety/effectiveness or intended use and need a documented assessment. [S03, S04, S10]

### Do not assume a convenience-kit exemption

FDA's convenience-kit policy is limited to qualifying types and conditions; it is not blanket permission to put any cleared devices in a new retail kit and market a new combined use. Start with a documented distribution model and assess any actual kit or integrated configuration on its facts. [S11]

### Two concrete supplier leads

| Lead | What has been verified | What must be established commercially |
|---|---|---|
| **Healgen Accurate oral-fluid COT/THC family, K252523** | FDA records an OTC qualitative oral-fluid THC screen calibrated to delta-9 THC at 40 ng/mL, with preliminary results and confirmation. [S07] | Exact currently supplied SKU, permitted solo/assisted workflow, labeling, inventory, wholesale price, storage/shelf life, distribution/private-label rights and confirmation arrangements. A THC-only SKU and OEM agreement have not been verified. |
| **BACtrack developer platform** | BACtrack advertises an iOS/Android SDK and depicts connection, test initiation and result retrieval. [S08] | Supported product models, lawful use/label scope, rights, export behavior, pricing, support and whether a read-only result route is available without adding device control. |

These are diligence leads, not selected vendors or confirmed contracts. FDA clearance does not prove retail availability; an SDK does not prove that the proposed third-party medical functions are authorized.

If an OEM's only integration requires our app to control measurement, use its established measurement workflow initially and allow manual history entry. A custom control interface can be evaluated later without holding up the limited service app. [S05, S08, S09]

### Supplier information to obtain before committing to a launch date

Obtain the exact authorization or exemption basis and final instructions; configuration and user limitations; stock/lead time and volume pricing; product/lot traceability; calibration, shelf life and returns; complaint/field-action responsibilities; change notification; and permitted brand/software integration. For custom OEM development, additionally determine the legal manufacturer, submission owner, evidence access, design-change authority and rights to keep supporting the product.

These documents make the proposed arrangement reviewable. This research did not send inquiries, negotiate, purchase, or make commitments.

## 5. Simplify the first all-in-one instrument

The preferred first custom specification is:

- **Alcohol:** an established, separately qualified breath measurement path.
- **Cannabis:** a preliminary qualitative oral-fluid THC screen using the chosen system's supported cutoff and workflow.
- **App:** faithful result presentation, history and service.
- **Hardware:** a pocket enclosure designed around the established sampling and read processes, with final integration validated.

For the first commercial configuration, defer THC-COOH and 11-OH-THC quantitation, user-specific metabolism models, pupil stimulation, ECG, PPG and a functional-impairment score. This is a proposal for a smaller commercial scope, not an edit to the existing scientific hypothesis.

### Highest-value reductions in work

| Decision | Work removed from the narrower first launch's critical path | Work that remains |
|---|---|---|
| Exposure screen instead of impairment prediction | Independent impairment endpoint, multimodal prediction, personalization and clinical inference validation | Evidence and labeling for the exposure test and its actual user workflow |
| Parent-THC screen first | Additional metabolite sensitivity, specificity, recovery and interpretation questions | Reliable performance of the chosen THC assay |
| Supported finished OEM collection/assay system | Reinvention of collector, formulation, flow and manufacturing process where evidence is reusable | Evidence access, configuration equivalence, transfer and supplier responsibilities |
| Established collector and read method | Avoidable repeat studies after changing buffer, recovery, volume, timing or interpretation | Verification of the final supported system and intended user |
| Omit active physiological channels initially | Their body-contact/optical safety, signal validation, power interactions, usability and sensitive-data burden | Safety, analytical, human-factors and study determinations for the remaining device |
| Bounded software release | New inference and automatic-learning work before first sale | Correct measurement/display behavior, applicable software/security controls and change assessment |

These savings are engineering and evidence judgments grounded in the repo's dependency structure. They do not automatically make a new integrated device exempt.

For saliva, seek the full supported system rather than a raw strip or antibody. Swab material, saliva volume, dilution buffer, strip geometry, read timing and optical interpretation can all affect the claimed assay. A new camera reader is a measurement change even if the cartridge looks unchanged. The classification and change framework must be applied to the finished configuration. [S07, S09, S10]

For alcohol, the generic breath-alcohol category is Class I with a conditional 510(k) exemption. Preserve its actual sampling, calibration and allowed result interpretation. That exemption does not extend automatically to the THC function or a fused impairment result. [S12]

## 6. Keep regulatory work focused on actual decisions

Use a short written function/activity assessment for the initial service: what is sold, by whom, whose labels are used, what the app does, whether devices are changed, and what claims are made. When the unchanged distribution and non-device software boundaries are settled, do not make an unnecessary agency request a prerequisite simply because the later project is ambitious.

For the new instrument, pursue a focused sequence:

1. Freeze analyte/result type, user, workflow, reading method and draft labeling.
2. Compare the exact system with suitable legally marketed products and identify every meaningful difference.
3. Resolve any genuine classification/exemption uncertainty using the appropriate information route.
4. Seek Pre-Sub feedback on a concrete assay, integration and self-use evidence strategy if useful for the unresolved questions.
5. Complete the applicable evidence and submission before that configuration is marketed.

A 513(g) request supplies FDA information on classification/requirements; its response is not clearance or a final classification decision. A Pre-Sub addresses a proposed evidence/predicate strategy and also is not authorization. Neither is a blanket requirement for selling an unchanged finished product through an appropriate distributor model. [S13, S14]

**Potential OEM review advantage:** if a new submission is needed, ask whether the authorized manufacturer can use a Special 510(k) for a qualifying modification to its own legally marketed device. Eligibility depends on the change, established evaluation methods and whether the supporting data can be reviewed in summary/risk-analysis form. FDA describes an intended 30-day processing period for eligible Special submissions; that is not a development or launch guarantee, and an unsuitable submission can convert to Traditional. The new all-in-one design has not been shown eligible. [S16]

Set up scoped design, supplier and change controls during the custom-device program so that evidence is reusable. The current repo already provides a strong traceability foundation. Treat QMSR and study requirements according to the actual role and phase; relevant investigational design requirements cannot simply be deferred until sale. [Assessment sections 4–6]

### Exemptions that do not fit the proposed consumer offer

The October 6, 2026 cannabinoid rule preserves an employment/insurance-only exemption under specified conditions. A genuine employer/insurer-only product would be a different business and intended-use decision, with its own obligations. It is not the current consumer self-test strategy. [S15]

RUO labeling, a “beta” label, a subscription and a wellness description do not substitute for matching actual activities and functions to an applicable pathway. The time savings proposed here come from reusing established products and releasing fewer new medical functions. [Assessment sections 3–4]

## 7. Make $20/month a testable commercial design

**Recommended structure:** price the reader separately at first, then offer a clearly bounded refill/service membership targeted at $20/month. Set the included test allowance only after quotes and expected usage are known. State any confirmation-laboratory charges separately if they are not included. Do not make a custom reader subsidy or unlimited disposable tests an unexamined launch obligation.

The arithmetic below is a sensitivity example, not a supplier quote or a claim of feasible production cost:

- Monthly revenue: $20.
- Illustrative gross-margin target: 60%.
- Maximum direct cost at that target: $20 × (1 − 0.60) = **$8/month**.
- Illustrative non-test direct costs, including fulfillment/service/payment/cloud allocations: **$3/month**.
- Remaining allowance for the supplied THC tests: **$5/month**.

| Included tests per month | Maximum cost per supplied test under those assumptions |
|---|---|
| 2 | $2.50 |
| 4 | $1.25 |
| 8 | $0.625 |

If all non-test direct costs exceed $3, the allowable test cost falls. If the business also absorbs a hypothetical $60 reader over 24 months, that adds $2.50/month and halves the $5 test budget. These values illustrate why an upfront reader charge and a metered allowance deserve testing.

Gross margin is not net profit: acquisition, research, regulatory development, administration and other expenses still require funding. Existing cleared product sourcing can shorten the revenue path without guaranteeing enough margin for a $20 plan.

Commercial experiments should answer four questions: how often people use the tests, whether they value history/refills enough to subscribe, what fulfillment pattern preserves product quality and reduces cost, and whether the contribution margin supports service and replacement. Actual supplier quotes and customer behavior decide the allowance.

## 8. A 30-day readiness sprint

This is a proposed execution schedule for the limited service route, not an FDA review promise or a guaranteed launch date. It assumes suitable finished products and a workable business arrangement can be obtained.

| Window | Concrete deliverable | Decision it resolves |
|---|---|---|
| Days 1–5 | First-release claims/feature matrix; domestic distribution role assessment; exact supplier authorization/label packets and requested quotes | Whether the limited offering can use the intended route and whether the products actually fit the user/market |
| Days 6–14 | Supplier/commercial terms; source-labeled history prototype; ordering, cancellation, support and complaint-forwarding workflows; quoted cost model | Whether the service can work operationally and economically without custom measurement development |
| Days 15–21 | Synthetic end-to-end verification of entries, corrections, exports and fulfillment; review of product presentation and instructions; inventory/service readiness | Whether the actual release matches the scoped offer |
| Days 22–30 | Launch-readiness review and, if dependencies are satisfied, a limited ordinary commercial rollout within the existing products' labeling | Whether a first-revenue launch is ready or a concrete supplier/scope/operational blocker remains |

Any human-study work intended to establish new device or clinical performance follows its own authorization process; an operational sales pilot does not authorize the impairment research program.

In parallel, produce an OEM request-for-information package for the true all-in-one instrument: preliminary layout, exact assay and breath functions, collector/read constraints, proposed claim, evidence access needs, manufacturing responsibilities and cost targets. Do not freeze industrial design around an unsupported sampling or reading method.

### Stop or redirect quickly when an assumption fails

If no suitable OTC oral-fluid SKU is available on workable terms, the dual-testing service launch is blocked on sourcing. A breath-only service or app-only launch is a separate optional interim business decision and should be labeled accurately. Do not substitute a professional-use or employment-only assay into the consumer offer.

If an OEM cannot provide the needed design/evidence rights, compare another partner or treat the instrument as new development. If $20 cannot cover the intended allowance, adjust hardware pricing, allowance or economics before promising the subscription.

The most useful early milestone is **a verified product-and-supplier arrangement with a released, limited feature set**, followed by real operational learning. The original all-in-one instrument advances on its own documented evidence milestones.

## 9. Proposed repository follow-through

The accompanying regulatory assessment retains the full specification's obligations. This strategy adds a proposed commercial path; it does not silently reclassify the P0 starter as a consumer release.

Recommended next controlled artifacts are a first-release PRD/claims matrix, activity/function applicability record, supplier authorization and responsibility register, quoted unit-economics model, and separate all-in-one OEM requirements. Preserve the existing impairment research requirements and gates rather than deleting them to make a launch checklist look complete.

## 10. Source register

Accessed October 11, 2026 UTC. Binding regulations, FDA's nonbinding explanations/guidance, individual clearance evidence and a vendor capability page are distinguished below. Older FDA webpages sometimes retain old QSR section references; this strategy uses the current QMSR analysis in the companion assessment.

| ID | Primary source and scope | Link |
|---|---|---|
| S01 | FDA, Premarket Notification 510(k), especially “When a 510(k) Is Not Required”; unchanged distribution versus manufacturing/modification | [FDA](https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/premarket-notification-510k) |
| S02 | FDA, Who Must Register, List and Pay the Fee; domestic distributor, importer, relabeler/repackager and specification-developer activities | [FDA](https://www.fda.gov/medical-devices/device-registration-and-listing/who-must-register-list-and-pay-fee) |
| S03 | 21 CFR 807.85(b), current conditional own-name distribution/repackaging exemption | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-807/subpart-E/section-807.85) |
| S04 | FDA, 510(k) Frequently Asked Questions, distributor section and truthful manufacturer/distributor attribution | [FDA](https://www.fda.gov/medical-devices/premarket-notification-510k/510k-frequently-asked-questions) |
| S05 | FDA, Medical Device Data Systems, Medical Image Storage Devices, and Medical Image Communications Devices; final September 28, 2022; statutory non-device software exclusion and direct third-party information-only connection example | [Guidance](https://www.fda.gov/media/88572/download) |
| S06 | FDA, Examples of Software Functions That Are NOT Medical Devices; general education, logging, organization and data-display examples; older CDS examples are not used instead of current CDS guidance | [FDA](https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices) |
| S07 | FDA K252523 decision summary, 2026; Healgen Accurate oral-fluid COT/THC family, OTC preliminary qualitative THC screen and actual studied workflow | [Clearance evidence](https://www.accessdata.fda.gov/cdrh_docs/reviews/K252523.pdf) |
| S08 | BACtrack official SDK page; current iOS/Android developer capability and depicted connect/start-test/get-result workflow; not FDA authorization for this project | [Vendor capability](https://www.bactrack.com/pages/sdk) |
| S09 | FDA, Clinical Decision Support Software; final January 29, 2026; assay signals, image analysis and exclusion criteria | [Guidance](https://www.fda.gov/media/109618/download) |
| S10 | FDA, Deciding When to Submit a 510(k) for a Change to an Existing Device; final October 2017; assess actual device/labeling changes | [Guidance](https://www.fda.gov/media/99812/download) |
| S11 | FDA, Convenience Kits Interim Regulatory Guidance; May 1997; qualifying types and limits, not a general all-in-one exemption | [Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/convenience-kits-interim-regulatory-guidance) |
| S12 | 21 CFR 862.3050, breath-alcohol generic type; conditional Class I 510(k) exemption and 862.9 cross-reference | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-862/subpart-D/section-862.3050) |
| S13 | FDA, Section 513(g) Requests for Information; final August 23, 2024; information request and limits of the response | [Guidance](https://www.fda.gov/media/78456/download) |
| S14 | FDA, Q-Submission Program; final May 29, 2025; proposed evidence/predicate feedback and 513(g) distinction | [Guidance](https://www.fda.gov/media/114034/download) |
| S15 | 21 CFR 862.3870, cannabinoid test systems; current consumer/nonconsumer exemption distinction following October 6, 2026 amendment | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-862/subpart-D/section-862.3870) |
| S16 | FDA, How To Prepare A Special 510(k); qualifying manufacturer-owned modifications, methods/data criteria and conditional review process | [FDA](https://www.fda.gov/medical-devices/premarket-notification-510k/how-prepare-special-510k) |

For studies, QMSR, human factors, physical safety, cybersecurity, records and postmarket sources, see the [44-source FDA regulatory assessment](FDA_REGULATORY_ASSESSMENT.md). For the chemistry behind analyte and matrix choices, see the [THC chemistry review](THC_CHEMISTRY_REVIEW.md).
