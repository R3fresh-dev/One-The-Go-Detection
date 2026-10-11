# FDA regulatory and compliance assessment

## On-the-Go Detection: pocket alcohol, cannabis, and functional-assessment system

**Research date:** October 11, 2026 UTC / October 10, 2026 America/Chicago.  
**Repository:** R3fresh-dev/One-The-Go-Detection.  
**Specification snapshot reviewed:** [85a1545213dd6a12d2b566ffd9e596933358f405](https://github.com/R3fresh-dev/One-The-Go-Detection/tree/85a1545213dd6a12d2b566ffd9e596933358f405).  
**Status:** Research and planning assessment. Final intended use, classification, study determinations, and commercial authorization remain open. Recommendations here do not close a release gate or amend the normative specification.

The review examined the README, PRD, HLD, LLD, full requirement register, validation plan, hardware guide, roadmap, decisions, schemas, examples, and verification report. It combines three parallel research workstreams: classification and claims; studies, quality and physical safety; and software, AI, cybersecurity and records. “Not evidenced in the repo” does not mean no records exist elsewhere.

The retrieved eCFR pages displayed Title 21 current through October 7, 2026, with the latest amendment October 6. Sources distinguish binding law, FDA's nonbinding guidance, individual device clearance records, and project-specific judgment. The latest chemistry review is available in [THC_CHEMISTRY_REVIEW.md](THC_CHEMISTRY_REVIEW.md).

For the user's subsequent request to accelerate launch, see the [faster market-entry strategy](FAST_MARKET_STRATEGY.md). It distinguishes an initial unchanged-product distribution and limited-app offering from manufacturing the custom device assessed here; the applicable responsibilities differ.

## 1. Decision that matters most

**The custom consumer cannabinoid-testing product should be planned as a regulated device development program, even if an impairment output is deferred.** An individualized medical impairment assessment adds a further intended-use and evidence question. There is a concrete regulatory precedent for OTC oral-fluid THC screening. That precedent does not establish the route for the repository's quantitative, multimodal current-impairment probability. The generic breath-alcohol function has a different classification and exemption framework. A single enclosure does not collapse those questions into one answer. [R01–R10]

The practical choice is whether the first commercial scope will be a carefully defined chemical screen, with separately qualified breath alcohol, or the broader functional-assessment system. The broader scope remains a research hypothesis until its independent endpoint and clinical usefulness can be demonstrated. Preserving it as a research workstream is consistent with the current specification; narrowing a first release would require an explicit product decision.

This is a review of a **P0 synthetic integration starter and proposed specification**, not a finding that an operating consumer product is currently violating FDA requirements. The existing repo explicitly says there is no validated assay, trained model, working production app or completed hardware. Its research gates are useful foundations.

### Function-by-function assessment

| Proposed function | Verified regulatory anchor | Consequence for this project |
|---|---|---|
| OTC qualitative saliva THC screen | Cannabinoid test systems are Class II under 21 CFR 862.3870; NFW is the OTC cannabinoid code. A current OTC clearance exists. [R02, R04, R05] | A 510(k) strategy is plausible for a sufficiently comparable, narrowly specified screen. Predicate suitability is not established merely by sharing an analyte. |
| Quantitative saliva THC; optional THC-COOH or 11-OH-THC | The cannabinoid category includes saliva; the reviewed OTC comparator is qualitative. [R02, R04] | Quantitation, additional analytes, collector, reader and numerical interpretation need their own claim-specific evidence and pathway analysis. |
| Calibrated breath-alcohol measurement | The generic type in 21 CFR 862.3050 is Class I and 510(k)-exempt subject to 862.9. [R06–R08] | Assess the actual intended use, technology and final configuration against exemption limits. Exemption does not remove all FDA obligations. |
| Saliva plus reaction task, pupil and cardiac signals producing current-impairment probability | Device-definition and software-function analysis depend on actual intended use, inputs, users and outputs. [R01, R12] | No suitable predicate for the complete proposed claim was established in this review. Broader predicate work and FDA feedback are needed; De Novo is a possibility, not a determined route. |
| App history, transfer and display | Pure transfer/display can have a different status from signal interpretation; effects on regulated functions still matter. [R10, R12] | Maintain a function inventory. Do not assume either the whole app is unregulated or every administrative feature requires identical review. |
| All functions in one pocket enclosure | Device/device integration is not automatically a statutory drug/device combination product. [R09, R10] | Evaluate shared power, firmware, connectivity, sample handling and result presentation. Submission organization follows the actual claims and interactions. |

## 2. Claims and the available THC precedent

### The October 6, 2026 change does not exempt consumer testing

The current cannabinoid regulation preserves the premarket exemption only for qualifying systems intended and labeled solely for employment or insurance testing, subject to the general limitations. FDA's October 6, 2026 final rule expands that exemption to otherwise qualifying federal drug-testing uses. It does not exempt an OTC consumer self-test. Class II classification remains. [R02, R03]

Switching a website's wording to “research,” “wellness,” or “subscription” does not itself change the product's actual function and intended use. The proposed consumer use must be assessed as described and supplied. The existing PRD's exclusion of employment and law-enforcement deployment also means those exemption conditions should not be imported into this baseline.

### What K252523 establishes

FDA's K252523 decision summary covers a **qualitative oral-fluid THC screen calibrated to delta-9 THC at a 40 ng/mL cutoff**, preliminary results, and laboratory confirmation. Its THC indication does not establish a quantitative reportable range, elapsed time since use, current impairment, or driving fitness. It is an important commercial precedent with a limited claim. [R04]

The summary's lay-user evidence includes paired users; the additional THC study reports that subjects did not self-test. That does not negate the OTC clearance. It limits what the published evidence establishes about the proposed solo collection, reader and app workflow. A new collector, reading technology, cutoff or interface needs an impact and evidence assessment. [R04]

**Project implication:** successful agreement with an LC–MS/MS concentration can support the chemical-measurement layer. It does not independently validate a functional-impairment endpoint. The repo already recognizes this in ANA-009, MOD-001, PRD-005 and the validation plan's separate outcomes.

### Why the impairment claim changes the program

The repo's stated outcome is a probability of a specified current functional impairment in the context of cannabis exposure. The following remain release-blocking decisions under PRD-027 and G-01:

- The exact functional endpoint and how it is independently adjudicated.
- Intended adults, use setting, self-use or assisted use, routes and patterns of cannabis use, and permitted co-use.
- The time represented by a result and what action the user is intended to take.
- Acceptable false-negative, false-positive, invalid and inconclusive outcomes.
- Whether a quantitative analyte value is displayed or only used internally, and which analytes the first claim includes.

These are research-design choices, not values FDA has supplied for this project. An outcome built from the same reaction or pupil features used as predictors would risk circular validation. A positive exposure reference cannot by itself serve as the reference for impairment. The existing participant-separated splits, locked confirmatory evaluation and incremental-value requirements are therefore central.

### Alcohol and integrated use

Retain ALC-001–005: a separately calibrated breath channel, explicit units and provenance, qualified sampling, and a defined cannabis/alcohol co-use policy. FDA's 2017 final determination expressly lists DJZ as exempt; the exemption remains subject to 862.9. That section's changed-use, changed-technology and IVD limitations require contextual assessment. They should not be read in isolation to claim either universal exemption or that every consumer breathalyzer loses its exemption. [R06–R08]

For the finished system, evaluate whether collection order, fluids, shared air paths, common electronics or combined interpretation changes safety or effectiveness. Two separately supported numbers do not automatically substantiate an integrated impairment conclusion. These are design implications of the proposed architecture and FDA's multiple-function policy. [R10]

## 3. Wellness, software exclusions and submission strategy

The current **General Wellness guidance is January 6, 2026**. Its low-risk wellness policy and the statutory exclusion for certain healthy-lifestyle software have defined limits. A noninvasive sensor or consumer app does not qualify solely because it uses familiar hardware. An individualized medical impairment conclusion needs analysis of the actual claim and its consequences. [R11]

The current **Clinical Decision Support guidance is January 29, 2026**. The non-device CDS exclusion is not a sound default for the described consumer model: processing raw assay responses, eye images and ECG signals raises the signal-processing criterion, and direct consumer recommendations do not satisfy the health-professional-support criterion merely by adding an explanation. Discrete reported medical facts are not all treated as raw signals; functions must be assessed separately. [R12]

| Regulatory interaction or pathway | Appropriate purpose | Limit to preserve |
|---|---|---|
| Section 513(g) request | FDA information on classification and applicable requirements for a clearly described product. [R13] | A response is not a classification decision, final agency action, clearance or approval. It does not establish substantial equivalence. |
| Pre-Submission under Q-Sub | Focused feedback on proposed predicates, analytical strategy, independent clinical endpoint, study design and software/human-factors evidence. [R14] | Classification/applicable-requirement information requests belong in the 513(g) process. Pre-Sub feedback is not marketing authorization. |
| 510(k) | Demonstrate substantial equivalence to a suitable legally marketed predicate, with the same intended use and acceptable technology differences. [R15] | Chemical similarity does not cure a different intended use or new safety/effectiveness questions. |
| De Novo | Possible classification route for a novel low/moderate-risk device type without a suitable predicate, with adequate general/special controls. [R16] | Novelty does not guarantee eligibility or authorization. This review has not established that De Novo is required. |

**Recommended decision process:** define the first claim, prepare a product-code and predicate comparison, resolve genuine classification/exemption uncertainty, then seek focused feedback on a proposed evidence package. Do not ask FDA to design the product from a concept alone. Existing cognitive-assessment categories also deserve investigation; this review does not claim that all functional-assessment software is unprecedented.

## 4. Human studies: evaluate the complete configuration

### The active optical functions matter

The hardware guide proposes active MAX30101 finger PPG, and the pupil workflow deliberately illuminates the eye. The diagnostic IVD study exemption includes a condition that the device not intentionally introduce energy into the subject, along with other conditions concerning sampling, diagnostic use and labeling. An assay-only rationale therefore cannot automatically cover the integrated protocol. This is a configuration-specific regulatory issue, not a conclusion that the study is necessarily significant risk. [R20, R21]

| Development activity | Decision needed before that activity |
|---|---|
| Synthetic sessions, dummy cells and ECG simulator | Continue the documented P0 engineering boundary; make no human performance claim. |
| Assay-only specimen investigation | Assess every diagnostic-exemption condition and applicable labeling, IRB and consent obligations. [R20–R22] |
| Active PPG, illuminated pupil, ECG and task study | Document the exact configuration, risk controls and use of results; determine exempt, nonsignificant-risk or significant-risk status. [R20, R21] |
| Nonsignificant-risk study under Part 812 | Follow abbreviated IDE requirements, including IRB approval and applicable consent, monitoring, records and reporting; a routine advance FDA IDE application is not required when those conditions are met. [R20] |
| Significant-risk study | Obtain both FDA IDE and IRB approval before starting. Device class and study risk are different questions. [R21] |

IDE exemption is not blanket exemption from applicable human-subject protections. The repo correctly separates app use from research enrollment. A study's actual use of results, participant recruitment and specimen source matter. Controlled cannabis administration, substance handling and any drug-study requirements require a separate institution-led assessment before such a protocol; this review does not authorize administration or enrollment. [R21]

**Recommended G-07 evidence package:** sponsor and investigator responsibilities; protocol/configuration-specific exemption or risk rationale; necessary approvals; controlled consent; eligibility and supervision; device accountability; data-quality monitoring; deviations; stopping rules; and adverse-event escalation. Record an actual approval reference and version, rather than treating an arbitrary string in a JSON manifest as proof of authorization.

Where Part 812 applies, unanticipated adverse device effects have investigational reporting rules. Investigators must report specified effects to sponsor and IRB as soon as possible and within 10 working days; sponsors have immediate evaluation duties and specified reports within 10 working days of first notice. These differ from the commercial MDR reporting regime. [R25]

### RUO/IUO and the proposed subscription

The labeling rules in 809.10(c) and the applicable investigational rules control. FDA's RUO/IUO guidance explains how it evaluates labeling against actual intended use and distribution. A research disclaimer or consumer checkbox does not independently make a clinical-use product exempt. [R22, R23]

If Part 812 applies, 812.7 restricts promotion/test marketing and charging beyond the specified recovery of manufacture, research, development and handling costs. A legitimate research cost-recovery arrangement is not categorically prohibited, but a $20/month consumer “research” subscription is not a substitute for the appropriate study or marketing pathway. [R24]

## 5. Quality system and design evidence

**QMSR has been effective since February 2, 2026.** Revised Part 820 incorporates ISO 13485:2016 with FDA-specific requirements. An ISO certificate is neither an FDA prerequisite nor proof that the manufacturer satisfies FDA requirements. Buying a cleared component or outsourcing production does not itself settle responsibility for the finished system. [R17, R18]

Do not postpone the entire quality assessment until commercial sale. Section 812.1 retains applicable 820.10(c) design/development requirements within the IDE exemption from other manufacturing requirements. Part 820 includes applicable design/development requirements for Class II/III devices and specified Class I devices, including those automated with computer software. The precise scope still needs determination; this does not impose every commercial manufacturing obligation on P0 synthetic work. [R17, R19]

The repo supplies requirements, owner roles, gates, traceability, versioning and synthetic verification. The next step is an operating process with records showing it is followed. **Recommended implementation artifacts** are:

- A scoped quality plan with named decision-makers, responsibilities, controlled documents and training.
- A design/risk record linking user needs, inputs, outputs, risks, controls, reviews, verification, validation and changes.
- Supplier and purchasing specifications for collector, cartridge, sensor, electronics, reference laboratory and relevant outsourced software services.
- Nonconformance, corrective action, complaint, calibration/service and release procedures.
- Transfer specifications and acceptance evidence for production cartridges, readers, calibration software, packaging and supported app/phone configurations.
- Internal review and audit records, with objective gate-closure evidence in controlled storage.

A useful initial hazard register should connect each hazard to a requirement and a verification method. Examples specific to this design include falsely reassuring interpretation; stale or misassociated sessions; wrong lot/calibration pairing; oral-fluid dilution or inadequate sample; optical/ECG exposure; phone timing drift; unsupported co-use; insecure software updates; and expired or degraded cartridges. These are proposed analysis inputs, not findings that an implemented product has failed.

The **41 checks described in the current verification report** concern documents/contracts and synthetic behavior. They do not verify a physical assay, clinical performance, human use, a deployed API/BLE implementation or an operating QMS.

## 6. Analytical, clinical, human-factors and physical evidence

### Four distinct evidence layers

| Layer | Existing repo foundation | Evidence still needed for the actual claim |
|---|---|---|
| Chemistry and specimen handling | ANA-001–013; G-02/G-03; collection volume, dilution, free/total basis, recovery, specificity, stability and paired reference comparison | Approved numerical protocol; authentic intended-user specimens; donor/lot/operator/reader variation; uncertainty and invalid-rate results; manufacturing and shelf-life bridge. |
| Sensor and software measurement | HW requirements; LLD units, timing, provenance and schemas | Verified physical signal acquisition, calibration, interference, timestamp alignment, image/PPG/ECG quality and final-system fault behavior. |
| Clinical interpretation | MOD-001; VAL-002–007; G-08/G-09 | Independent outcome definition; locked evaluation; adequate precision; calibration; subgroup and co-use analyses; clinically justified decision thresholds and incremental benefit. |
| User operation and understanding | APP-012–014; G-10; one-sample/one-task design | Use-risk analysis, critical tasks, formative studies and appropriate final-interface validation in representative intended users and settings. |

The assay's labeling must accurately describe intended use, collection, operation, calibration, result interpretation, limitations and applicable performance characteristics. A low detection limit is not a clinical impairment threshold. There is no universal project-specific FDA “95% accurate” rule supplied by these sources. Keep the repo's correct distinction between ICH M10 drug-development bioanalysis and validation of this consumer device. [R22]

For the clinical study, the repo's own design implies that participant-level independence, temporal information boundaries, repeated-check accounting and reference-label independence must be demonstrated. Report uncertainty, false reassurance, false positives and unusable results together. A high overall accuracy can obscure clinically important failures in a subgroup or use condition. No clinical sample size or acceptance percentage is established by this desk review.

### Human factors: use the current 2026 documents

FDA finalized **Content of Human Factors Information in Medical Device Marketing Submissions on May 29, 2026** and revised **Applying Human Factors and Usability Engineering to Medical Devices on August 3, 2026**. The former uses a risk-based submission-category framework; the latter supplies development and validation recommendations. [R26, R27]

For this product, candidate critical tasks include adequate saliva collection, correct cartridge and timing, eye/finger alignment, task completion, handling interruption, recognizing invalid results, and understanding what a measured exposure or research estimate means. Assess the consequences of error, not just task completion or user satisfaction. Validate the final supported self-use workflow; trained-staff operation does not establish solo use.

If intended use includes operation after cannabis consumption, plan an ethically supported evaluation representing the relevant user capabilities. The general guidance recommends at least 15 participants per distinct user population for human-factors validation, sometimes more. This is not a clinical sample-size rule, an assay-accuracy study size, or automatic evidence that the overall device is adequate. [R27]

### Physical safety and standards

Keep the repo's simulator-first ECG approach and whole-system power/isolation review, optical-exposure gate, and separation of fluid handling from electronics. Assess battery/charging, EMC, fluid ingress, cleaning, materials, electrical faults and supported configurations. A component's certification or battery operation does not establish finished-system safety.

Biological evaluation should follow final contact materials, sites, durations, processing and cleaning. Collector/mouthpiece mucosal contact and finger/electrode contact need separate analysis. FDA's September 2023 biocompatibility guidance supports risk-based evaluation; it does not mean every device needs every possible biological test. [R28]

FDA **partially recognized ISO 10993-1:2025 on May 25, 2026**, recognition 2-313. The entry specifies exclusions and implementation caveats, and accepts declarations to the recognized 2018 edition until July 1, 2029. Record the exact edition and recognition scope rather than automatically calling the older edition the sole current option. [R29]

IEC 61010-2-101 explicitly covers IVD equipment, including self-tests. The additional body-connected/optical functions require a qualified applicability assessment; neither IEC 60601 alone for every subsystem nor 61010 alone for the whole assembly should be presumed sufficient. Most recognized consensus standards are voluntary evidence routes, distinct from the ISO requirements incorporated into QMSR or a specific applicable control. [R30, R31]

## 7. Software, AI, cybersecurity and electronic records

### Software evidence and model lifecycle

FDA's June 14, 2023 software-submission guidance uses **Basic/Enhanced documentation levels based on risk**. AI alone does not automatically select Enhanced. Prepare the rationale, software description, requirements/architecture, risk traceability, verification and validation, version history, unresolved anomalies and maintenance evidence appropriate to the device. Current PDFs may retain older QSR terminology alongside a QMSR notice; current regulations govern. [R32]

The existing LLD and schemas already propose immutable finalized records, linked corrections, manifest/version pinning, compatible feature/assay checks and restricted inference. Implementation is the missing step: an independent server must verify authorization, access rights, data integrity and model eligibility. A client-selected “active_research” state or a digest does not establish trustworthy provenance or scientific validity.

**Recommended initial engineering choice:** freeze the first evaluated pipeline and require explicit review for each change. A personalized baseline used as a predefined model input is not necessarily online learning; specify the distinction. Assess changes to thresholds, feature extraction, calibration, supported phones, collection materials and population as well as model weights.

FDA's **August 18, 2025 final PCCP guidance** describes an optional authorized plan for bounded AI changes, with a description of modifications, modification protocol and impact assessment. Internal approvals or a GitHub merge are not an FDA-authorized PCCP, and a PCCP does not permit unlimited indication expansion. The separate **January 2025 AI lifecycle document remains draft**, not final guidance. [R33, R34]

### Connected-device cybersecurity

Plan for FD&C Act **section 524B** if the marketed system meets the cyber-device definition and the relevant submission provisions apply. The statute addresses software, internet connectivity and vulnerability characteristics; required submission elements include vulnerability-monitoring/disclosure plans, cybersecurity processes, updates/patches and an SBOM. It does not mean every bench prototype immediately needs a marketing submission. [R35]

FDA's current final cybersecurity guidance is **February 3, 2026**. The proposed BLE/phone/cloud architecture should not be assumed outside scope because the pocket reader lacks its own cellular modem. The guidance expressly addresses connectivity including Bluetooth/BLE, cloud and USB/serial. [R36]

The repo proposes encryption, identity binding, replay protection, signed releases and recovery. No deployed evidence is supplied. **Recommended next security artifacts:** a trust-boundary/threat model; tested device identity and provisioning; authenticated software/model updates with safe recovery; access-control and session-association tests; production component inventory/SBOM; vulnerability intake and coordinated disclosure process; patch policy; and a defined supported service life. A development requirements file is not a complete finished-product SBOM.

Threat scenarios should include a cloned or substituted reader, a replayed assay, wrong participant association, a replaced model manifest, an expired calibration, compromised signing credentials, dependency vulnerabilities and interrupted update. The aim is to connect credible security failures to product risks and verified controls.

### Part 11 is record-specific

Identify electronic records required by applicable FDA predicate rules or submitted to FDA, and determine Part 11 scope for those records and signatures. Do not label every consumer history or log a Part 11 record automatically. FDA's scope guidance describes a narrower interpretation and limited enforcement discretion; the underlying record obligations remain. [R37, R38]

Hashes and immutable snapshots support integrity but do not by themselves authenticate an approver, validate a workflow or satisfy electronic-signature requirements. Record the actor, role, authority, time, meaning and relationship to the approved record where applicable. The current clinical electronic-records Q&A is **October 2024, Revision 1**. [R37, R39]

For this repo, implement an evidence register linking protocol versions, approvals, device/assay/software configurations, raw observations, deviations and reports. Preserve the existing rule excluding real participant data, identifiable eye recordings, biosignals, consent forms and credentials from GitHub. Broader HIPAA, state privacy and consumer-health-data determinations need a separate role- and data-flow-specific review; no blanket compliance badge is established here.

## 8. Commercial operations and the $20/month hypothesis

Before commercial distribution, determine manufacturer/specification-developer roles, registration and listing, applicable UDI/GUDID, labeling and authorization requirements. Research/investigational exceptions need assessment; commercial registration or UDI is not a universal P0 prerequisite. Registration/listing is not FDA approval. [R40, R41]

| Ongoing workstream | Required applicability analysis and proposed operating response |
|---|---|
| Complaints, calibration and service | Establish intake, investigation and traceability to reader, cartridge lot, calibration and software/model versions; connect support to reportability review. QMSR contains specific complaint/servicing and labeling controls. [R17] |
| Manufacturer MDR | For reportable marketed-device events, the usual deadline is 30 calendar days after awareness. Certain remedial-action situations or FDA requests trigger five-work-day reports. Not every error is an MDR. [R42, R43] |
| Corrections and removals | Report qualifying actions under Part 806 within 10 working days of initiation, subject to exceptions; preserve required records. An update or calibration fault needs assessment rather than an automatic “recall” or “not reportable” label. [R44] |
| Controlled changes | Determine whether a hardware, assay, labeling or software change needs a new submission or is within an applicable authorized PCCP. Preserve the evidence and decision, not just the source-code diff. [R33, R40] |
| End of support and incident recovery | Define support life, vulnerability response, field actions, account/device loss and recovery; ensure the subscription promises align with those capabilities. [R35, R36] |

The $20/month target remains an economic hypothesis under BUS-001–003 and G-13. A useful model must state reader purchase/subsidy, included tests and usage distribution, then include cartridge/collector costs, lot release, calibration/service, replacement/warranty, shipping, customer support, secure operations, studies and continuing regulatory work. This review verifies no supplier prices, agency fee amounts, approval timetable or cost per compliant test.

**Product recommendation:** evaluate whether each extra analyte and physiological channel adds enough validated benefit to justify collection burden and lifecycle cost. Keeping one enclosure remains possible as a design goal, but claiming more outputs can increase the evidence needed. A narrower first claim should be a deliberate roadmap decision, not an unsupported shortcut in labeling.

## 9. Repository gap register

The table separates existing planning strengths from records and decisions still needed. Roles use the repo's existing owner model; assign named individuals before execution. The proposed artifacts below are deliverables, not claims that new procedures have already been implemented.

| Priority and existing anchor | Already specified | Next reviewable deliverable | Accountable role |
|---|---|---|---|
| First: PRD-005/027, G-01/G-14 | Intended use, endpoint and applicability are unresolved and release-blocking | Draft intended use and claims matrix; function inventory; product-code/predicate comparison; written regulatory applicability analysis | Product + quality/regulatory + clinical |
| Before relevant development/studies: Validation Plan §10 | QMSR is acknowledged | Development-stage QMS scope decision including 812.1/820.10(c), named quality plan and controlled design/risk process | Quality/regulatory |
| Before human work: VAL-001, G-07 | Protocol, consent, oversight and safety gates | Exact-configuration study exemption/NSR/SR rationale; approvals, monitoring, accountability and investigational reporting plan | Sponsor + clinical + quality/regulatory |
| Before analytical claims: ANA-001–013, G-02/G-03 | Detailed collection/assay matrix | Approved numerical analytical protocol, authentic-specimen results, lot/reader variation and manufacturing bridge | Analytical + independent validation |
| Before body-connected/optical work: HW-005–010, G-04/G-05 | ECG and optical reviews | Complete schematic/power-mode and optical/PPG assessment, applicable standards, test evidence and residual-risk review | Hardware + qualified safety specialists |
| Before clinical performance claims: MOD-001–015, VAL-002–007, G-08/G-09 | Independent endpoint and locked evaluation | Endpoint/adjudication charter; statistical plan; participant-separated evaluation; subgroup, co-use and incremental-value evidence | Clinical + statistics + independent validation |
| Before self-use release: APP-012–014, G-10 | Result-state boundaries and usability gate | Use-risk analysis, critical tasks, formative findings and final-interface validation under current HF guidance | App + human factors + clinical |
| Before participant-data deployment: SEC-001–007, OPS-001–006, G-12 | Access, consent, retention, encryption and recovery principles | Implemented authorization and audit; record-applicability register; threat model, SBOM, patch/disclosure and restore evidence | Security/data + engineering |
| Before model release/change: LLD manifests, MOD requirements | Versioning, compatibility and research-only inference | Enforced manifest approvals; software evidence package; change assessment; optional proposed PCCP strategy | ML + engineering + quality/regulatory |
| Before alcohol claim: ALC-001–005, G-11 | Separate sampling, calibration and co-use handling | Finished-configuration exemption analysis and independent alcohol qualification, including integration effects | Hardware + quality/regulatory |
| Before production/P3: G-10/G-14 | Manufacturing and commercial authorization gates | Supplier/transfer/lot-release package; labeling, authorization, registration/listing/UDI and postmarket procedures as applicable | Quality/regulatory + operations |
| Before price promise: BUS-001–003, G-13 | $20/month is explicitly a hypothesis | Quoted, usage-sensitive lifecycle cost model including evidence generation and service obligations | Business + product |

### Targeted specification corrections proposed for a later controlled revision

1. **Validation Plan §10:** expand the commercial-only QMSR framing to assess applicable development/research design requirements.
2. **Same section:** replace “FDA guidance requires” for RUO/IUO with a distinction between binding labeling regulations and FDA's explanatory guidance.
3. **G-07 evidence definition:** explicitly record the integrated optical/PPG configuration and exemption/NSR/SR reasoning.
4. **G-10/G-12/G-14 evidence definitions:** reference current HF guidance and identify software/cybersecurity, electronic-record and postmarket artifacts.

This research commit intentionally records those proposed revisions without marking a gate passed or silently changing the documented project scope.

## 10. Prioritized work plan and questions for FDA

### Next planning cycle

**First, settle the claim.** Produce a one-page intended-use draft with two explicit scope candidates: chemical screen with separate alcohol, and the broader functional-assessment system. Compare users, specimen, analytes, result type, interpretation, endpoint and expected action. Record which first-release scope the team selects.

**Second, make the evidence strategy concrete.** Prepare the predicate comparison, planned assay/collector/reader evaluation, independent endpoint charter, statistical outline, critical-task inventory and exact investigational configuration. Establish the quality and study responsibilities before relevant work.

**Third, prepare focused agency questions.** Use 513(g) if a classification/requirements information question remains. Use a Pre-Sub for a proposed predicate and evidence strategy. These are prepared deliverables; this review did not contact FDA or submit anything.

**Fourth, turn specifications into operating evidence.** Begin controlled analytical feasibility, risk reviews and synthetic software verification within the applicable phase. Close gates only on their defined evidence. Commercial marketing, human-study permission and an internally eligible research model remain distinct decisions.

### Suggested Pre-Sub questions, after a concrete proposal exists

1. Does the proposed predicate comparison adequately address the specified OTC assay, collector and reader differences?
2. Are the proposed specimen, collection, interference, stability, lot and intended-user studies adequate for the precise chemical claim?
3. Is the independently defined functional endpoint appropriate for the intended impairment claim, and what additional evidence would address false reassurance and uncertain results?
4. Does the planned locked, prospective evaluation adequately address repeat checks, subgroup performance, cannabis routes/use patterns, co-use and supported phone configurations?
5. Is the proposed human-factors validation appropriate for the final self-use workflow and relevant intended-user capabilities?
6. Is the proposed software documentation rationale, cybersecurity evidence and bounded model-change strategy appropriate for the described system?
7. How should shared functions and integration effects be represented in the proposed submission package?

Questions about **classification or applicable regulatory requirements** should be separated from those evidence questions and directed through the appropriate information process. [R13, R14]

### Scope still requiring separate determinations

This assessment does not establish the final class, predicate, submission route, study risk status, clinical sample size, device performance, manufacturing compliance or total development cost. It also does not replace a separate assessment of controlled-substance/drug-study rules, laboratory/CLIA arrangements, NHTSA/DOT requirements for any later evidential/workplace claim, FCC/battery transport, state consumer-health privacy, or non-US market access.

## 11. Primary source register

All sources were accessed October 11, 2026 UTC. FDA guidance is nonbinding except where it describes separately binding law. eCFR is authoritative but unofficial; Federal Register entries document the published actions. Current-page references should be rechecked when the intended use is frozen and before study or commercial submission.

| ID | Source, status and date | Link |
|---|---|---|
| R01 | FDA, How to Determine if Your Product is a Medical Device; current agency explanation of device definition and intended use | [FDA](https://www.fda.gov/medical-devices/classify-your-medical-device/how-determine-if-your-product-medical-device) |
| R02 | 21 CFR 862.3870, Cannabinoid test system; current regulation, amended October 6, 2026 | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-862/subpart-D/section-862.3870) |
| R03 | FDA, Certain Clinical Toxicology Test Systems; final rule, 91 FR 63478–63487, October 6, 2026, effective same day | [Federal Register](https://www.govinfo.gov/content/pkg/FR-2026-10-06/html/2026-20448.htm) |
| R04 | FDA, K252523 substantial-equivalence decision summary; OTC oral-fluid cotinine/THC system, 2026; THC indication and lay-user studies | [Decision summary](https://www.accessdata.fda.gov/cdrh_docs/reviews/K252523.pdf) |
| R05 | FDA, NFW product classification, OTC cannabinoid test; current database record | [Classification](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?ID=NFW) |
| R06 | 21 CFR 862.3050, Breath-alcohol test system; current regulation | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-862/subpart-D/section-862.3050) |
| R07 | 21 CFR 862.9, Limitations of exemptions; current regulation | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-862/subpart-A/section-862.9) |
| R08 | FDA, Class I exemptions final determination, 82 FR 17841–17844, April 13, 2017; DJZ listing | [Federal Register](https://www.govinfo.gov/content/pkg/FR-2017-04-13/html/2017-07468.htm) |
| R09 | FDA, Frequently Asked Questions About Combination Products; explanation of 21 CFR 3.2(e) and device/device distinction | [FDA](https://www.fda.gov/combination-products/about-combination-products/frequently-asked-questions-about-combination-products) |
| R10 | FDA, Multiple Function Device Products: Policy and Considerations; final guidance, July 29, 2020; current PDF includes QMSR notice | [Guidance](https://www.fda.gov/media/112671/download) |
| R11 | FDA, General Wellness: Policy for Low Risk Devices; final guidance, January 6, 2026 | [Guidance](https://www.fda.gov/media/90652/download) |
| R12 | FDA, Clinical Decision Support Software; final guidance, January 29, 2026, supersedes January 6 version | [Guidance](https://www.fda.gov/media/109618/download) |
| R13 | FDA, FDA and Industry Procedures for Section 513(g) Requests for Information; final guidance, August 23, 2024 | [Guidance](https://www.fda.gov/media/78456/download) |
| R14 | FDA, Requests for Feedback and Meetings for Medical Device Submissions: The Q-Submission Program; final guidance, May 29, 2025 | [Guidance](https://www.fda.gov/media/114034/download) |
| R15 | FDA, Content of a 510(k); current agency explanation of substantial equivalence | [FDA](https://www.fda.gov/medical-devices/premarket-notification-510k/content-510k) |
| R16 | FDA, De Novo Classification Request; current pathway explanation | [FDA](https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/de-novo-classification-request) |
| R17 | 21 CFR Part 820, QMSR; effective February 2, 2026, including 820.10, 820.35 and 820.45 | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-820) |
| R18 | FDA, QMSR Frequently Asked Questions; current implementation, certification and inspection explanations | [FDA](https://www.fda.gov/medical-devices/quality-management-system-regulation-qmsr/quality-management-system-regulation-frequently-asked-questions) |
| R19 | 21 CFR 812.1; current scope and applicable investigational design/development requirement | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-812/subpart-A/section-812.1) |
| R20 | 21 CFR 812.2; current diagnostic exemption and abbreviated IDE conditions | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-812/subpart-A/section-812.2) |
| R21 | FDA, In Vitro Diagnostic Device Studies: Frequently Asked Questions; final guidance, June 2010; use current regulations for amended cross-references | [Guidance](https://www.fda.gov/media/71075/download) |
| R22 | 21 CFR 809.10; current IVD labeling requirements, including RUO/IUO provisions | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-809/subpart-B/section-809.10) |
| R23 | FDA, Distribution of IVD Products Labeled RUO or IUO; final guidance, November 2013 | [Guidance](https://www.fda.gov/media/87374/download) |
| R24 | 21 CFR 812.7; investigational promotion, commercialization and related restrictions | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-812/subpart-A/section-812.7) |
| R25 | 21 CFR 812.150; investigational reports, including unanticipated adverse device effects | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-812/subpart-G/section-812.150) |
| R26 | FDA, Content of Human Factors Information in Medical Device Marketing Submissions; final guidance, May 29, 2026 | [Guidance](https://www.fda.gov/media/163694/download) |
| R27 | FDA, Applying Human Factors and Usability Engineering to Medical Devices; revised August 3, 2026; originally February 2016 | [Guidance](https://www.fda.gov/media/80481/download) |
| R28 | FDA, Use of ISO 10993-1: Biological Evaluation of Medical Devices; final guidance, September 8, 2023 | [Guidance](https://www.fda.gov/media/142959/download) |
| R29 | FDA recognized standards, ISO 10993-1:2025, recognition 2-313, May 25, 2026; partial scope and 2018 transition | [Recognition record](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfstandards/detail.cfm?standard__identification_no=47116) |
| R30 | IEC 61010-2-101:2018; publisher's scope, including self-test IVD equipment | [IEC catalogue](https://webstore.iec.ch/en/publication/60197) |
| R31 | FDA, Appropriate Use of Voluntary Consensus Standards in Premarket Submissions; final guidance, September 2018 | [Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/appropriate-use-voluntary-consensus-standards-premarket-submissions-medical-devices) |
| R32 | FDA, Content of Premarket Submissions for Device Software Functions; final guidance, June 14, 2023; current PDF includes QMSR notice | [Guidance](https://www.fda.gov/media/153781/download) |
| R33 | FDA, Marketing Submission Recommendations for a PCCP for AI-Enabled Device Software Functions; final guidance, August 18, 2025 | [Guidance](https://www.fda.gov/media/166704/download) |
| R34 | FDA, AI-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations; January 2025 DRAFT, not for implementation | [Draft status](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/artificial-intelligence-enabled-device-software-functions-lifecycle-management-and-marketing) |
| R35 | FD&C Act 524B / 21 USC 360n-2, cybersecurity statutory requirements; added December 29, 2022 | [U.S. Code](https://www.govinfo.gov/content/pkg/USCODE-2024-title21/html/USCODE-2024-title21-chap9-subchapV-partA-sec360n-2.htm) |
| R36 | FDA, Cybersecurity in Medical Devices: Quality Management System Considerations and Content of Premarket Submissions; final guidance, February 3, 2026 | [Guidance](https://www.fda.gov/media/119933/download) |
| R37 | 21 CFR Part 11, Electronic Records; Electronic Signatures; current regulation | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11) |
| R38 | FDA, Part 11, Electronic Records; Electronic Signatures — Scope and Application; final guidance, August 2003 | [Guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application) |
| R39 | FDA, Electronic Systems, Electronic Records, and Electronic Signatures in Clinical Investigations: Questions and Answers; final, October 2024, Revision 1 | [Guidance](https://www.fda.gov/media/166215/download) |
| R40 | 21 CFR Part 807; registration/listing, research exemption and 807.81 change-submission provisions | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-807) |
| R41 | 21 CFR Part 801 Subpart B; UDI labeling and specified research/investigational exceptions; includes Part 830 cross-references | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-801/subpart-B) |
| R42 | 21 CFR 803.50; manufacturer MDR requirements | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-803/subpart-E/section-803.50) |
| R43 | 21 CFR 803.53; manufacturer five-work-day reports | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-803/subpart-E/section-803.53) |
| R44 | 21 CFR 806.10; reports of corrections and removals | [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-806/subpart-B/section-806.10) |

### Repository evidence

The analysis uses the frozen specification commit linked at the top. The following relative links lead to the corresponding documents in the current checkout:

- [PRD](../PRD.md), especially claims, research phases and PRD-027.
- [Full specification](../FULL_SPECIFICATION.md), requirement families ANA, HW, APP, MOD, ALC, SEC, OPS, VAL and BUS; gates G-01–G-14.
- [Validation plan](../VALIDATION_PLAN.md), especially independent outcomes and section 10.
- [LLD](../LLD.md) and [HLD](../HLD.md), especially inference authorization, manifests, provenance and trust boundaries.
- [Hardware starter guide](../HARDWARE_STARTER_GUIDE.md), active finger PPG, optical collection and ECG simulator/safety boundaries.
- [Decisions](../DECISIONS.md), [roadmap](../ROADMAP.md) and [verification report](../VERIFICATION_REPORT.md), especially the limits of the current synthetic starter.
