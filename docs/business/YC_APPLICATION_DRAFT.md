# One-The-Go Detection YC Winter 2027 Application Draft

**Prepared:** October 12, 2026, America/Chicago.\
**Status:** Working application draft; incomplete fields remain bracketed. This repository version is the project document of record.

Working answers for Jacob Tyrawa and One-The-Go Detection. The intended MVP is an integrated device, companion app, and model research prototype, leading to a pocket product for everyday adult consumers. The company is prelaunch, and its current code was written using AI, primarily GPT.

Bracketed fields require Jacob's input. These are preparation topics, not a verified transcription of the signed-in Winter 2027 form. Check the current form's wording and limits before transferring the answers.

## Company name

One-The-Go Detection

## Short company description

Pocket cannabis testing with a companion app

44 characters, including spaces. This describes the intended product; the device remains in development.

## What we are building

We are developing a pocket cannabis-testing device and companion app with a model to investigate current functional impairment in adults. Our intended MVP combines a connected saliva-testing prototype, one short app-based reaction task, guided pupil capture, resting heart-rate capture, and an exploratory model of functional performance.

Our first product milestone includes both the physical device and the model in one research prototype. We have implemented the app and research-data software foundation; the saliva assay, physical measurements, and trained model still need development and evaluation. Pupil and heart-rate acquisition must meet the existing research requirements. The longer-term device would also include a separate breath-alcohol channel.

## Intended customer and problem

Our intended customer is an everyday adult who wants objective information to make more informed decisions after cannabis use. Detecting THC and measuring current functional impairment answer different questions. Our hypothesis is that a convenient combined check can provide useful information that people will use and pay for.

We have not validated that customer hypothesis yet. Research laboratories and assay developers would be potential development partners as we establish the measurement and validation methods. The eventual customer is the consumer.

## Current progress

Our software prototype includes Android and iOS applications, a research-data backend, and reader firmware. It covers guided measurement sessions, reaction-task recording, device communication, result history, and data export and deletion. The project has documented software-test and native-build checkpoints.

The prototype's sensor readings are simulated. The native reaction task is implemented, but its physical timing and clinical predictive value remain unqualified. We have not yet validated a saliva assay, qualified the physical sensing system, or shown that the combined measurements predict current impairment. Our next step is to connect the platform to genuine measurement methods and evaluate them through an appropriate research program.

## Time spent and full-time commitment

I started exploring the idea in [MONTH AND YEAR] and began building the current software in [MONTH AND YEAR]. I have worked on it [PART-TIME OR FULL-TIME] for [DURATION], alongside [WORK AND STUDY COMMITMENTS]. I am prepared to leave my job and work on this company full-time starting in January 2027.

My availability for the January through March 2027 batch in San Francisco is [CONFIRM AVAILABILITY].

## Users and revenue

We are prelaunch. We have no external users, paying customers, revenue, customer interviews, pilots, or committed laboratory or OEM partners yet. The progress so far is product research and software development.

## Evidence of customer need

I have not yet validated demand through customer interviews. The initial hypothesis is that adults who want objective feedback after cannabis use would value a convenient check combining exposure and functional measurements.

I plan to interview prospective users about the decisions they face, the products they use today, how often they would test, and what they would pay for. Those findings will shape the first product before we commit to custom hardware and subscription allowances.

## Founder background

I'm Jacob Tyrawa, a software engineer and AI engineer studying AI at the University of Pennsylvania. At work, I have led programs that helped my employer save more than $90 million annually.

My experience is in software and AI. The assay, hardware qualification, and clinical validation work require additional expertise, which I plan to obtain through specialist collaborators.

## Founder achievement

I led programs at work that helped my employer save more than $90 million per year. In one project, I analyzed call-center conversations and identified inconsistent status information across two credit-card pages that was confusing customers. My work included validating the user experience and implementing technical solutions. Our team added an API call and an ETL process to load data into a database, then revalidated the experience.

[Add the timeframe and how the broader programs' annual savings were measured. If available, add a specific validated result for the credit-card project; no individual savings amount has been stated for this example.]

## Why this idea and why this founder

I became interested in this problem because [PERSONAL OBSERVATION OR EXPERIENCE THAT ACTUALLY LED TO THE IDEA]. I wanted to explore whether a single portable check could make cannabis-related measurements more useful to an everyday person.

My software and AI background is relevant to the app, data systems, and model-evaluation tools. The current code was generated using AI, primarily GPT. The central question now is whether genuine chemical and functional measurements can support the intended product, and whether consumers want it.

## Who writes the code

The current company code was written using AI, primarily GPT. I am a software engineer and AI engineer. My own contribution has been [DESCRIBE WHAT YOU PERSONALLY SPECIFIED, DESIGNED, REVIEWED, TESTED, OR DEBUGGED].

[State whether any other founders, employees, or contractors contributed, and what each contributed.]

## Technology and AI tools

The mobile app uses Expo and React Native with TypeScript, plus Kotlin and Swift modules for native measurement and Bluetooth functions. The backend uses Python, FastAPI, and PostgreSQL. Reader firmware targets ESP32-based hardware, and the repository includes AWS infrastructure tooling.

GPT has been the main tool used to write the code. [ADD OTHER AI TOOLS ACTUALLY USED, IF THE FORM ASKS.] Model-training and evaluation software exists, but we do not yet have a trained and validated clinical model.

## Competitors and alternatives

DRUID offers an app that assesses cognitive and motor performance. Oral-fluid THC screens, including Healgen's Accurate product family, test for THC in a specimen. BACtrack sells connected breath-alcohol products and is an adjacent alternative for the planned alcohol channel.

Our proposed distinction is a single portable workflow that combines chemical and functional measurements. We need to demonstrate that the combination provides enough additional value to justify its cost and effort. We have not established a performance advantage over existing products.

## What we understand about the problem

A chemical THC result does not by itself establish current functional impairment. The important question is whether combining chemistry with performance and physiological measurements predicts an independently measured functional outcome better than a simpler approach.

That is why we are starting with a research platform. We can compare the contribution of each measurement before deciding which sensors and consumables belong in the final consumer device. The product needs both useful measurement performance and a procedure that consumers are willing to complete repeatedly.

## Business model and revenue potential

Our proposed consumer model is to sell the reusable reader separately and offer a subscription for a defined allowance of consumables and app services. The initial subscription target is approximately $20 per month. Pricing, included usage, hardware cost, and gross margin remain unvalidated.

At $20 per month, 100,000 subscribers would produce $24 million in annual subscription revenue; one million would produce $240 million, before costs. Those figures illustrate scale at the target price, not an established market size or customer forecast. We need supplier quotes and customer evidence to determine whether this model works.

## First customer acquisition

I plan to start with direct interviews with prospective adult consumers, then test a narrowly defined product proposition with people who already seek objective feedback about cannabis use. We will use those conversations to select an initial customer segment and understand existing spending and testing habits.

Research partners would help establish the measurement methods. A consumer launch would follow evidence supporting the exact product and its intended use. We have not yet proven a sales channel or acquired customers.

## Next milestones

Our next milestones are to build a repeatable physical saliva-measurement pathway, establish a plan for paired measurement and independent outcome data, train an initial model, and connect the device, app, and model in one reproducible workflow. Consumer interviews, a specific initial customer segment, and component and consumable cost estimates will progress alongside that work.

The model must be evaluated against an independently defined functional outcome on held-out participants, with comparisons of chemistry-only, app-only, and combined measurements. Genuine participant data collection depends on the applicable research approvals and qualified measurement methods. Synthetic data can exercise the integration software; real paired measurements and outcomes are needed to evaluate predictive performance.

## Why YC

I want YC's help turning this technical project into a company with a specific customer and a focused first product. The most useful support would be pressure-testing demand, prioritizing the scientific and hardware milestones, and building a fundraising plan around the evidence those milestones produce.

The prototype gives us a starting point for testing the idea. I want to use the batch to establish which consumer problem we can solve and a credible path to delivering the pocket device.

## Company location

I currently live in [CITY AND COUNTRY]. The company is currently based in [CITY AND COUNTRY]. During YC, I would be based in [CONFIRMED LOCATION], and afterward I plan to operate from [PLANNED LOCATION].

[Explain the actual reason for the planned location and confirm San Francisco availability. Studying at Penn does not establish your residence.]

## Website and product access

Company website: [LIVE URL, OR CONFIRM NONE]

Product demo: [ACCESSIBLE DEMO URL OR VIDEO]

If a demonstration is provided, show the guided check, the recorded reaction-task workflow, measurement quality and source labels, and history or export. Identify simulated sensor values clearly. Use a separate product demo from the founder video.

## Founder team and profiles

Known founder: Jacob Tyrawa.

Founder count and cofounder status: [CONFIRM SOLE FOUNDER OR LIST COFOUNDERS]

If there are cofounders: [NAMES, ROLES, HOW YOU MET, HOW LONG YOU HAVE KNOWN EACH OTHER, AND WHETHER YOU HAVE MET IN PERSON]

Penn program: [EXACT PROGRAM OR DEGREE AND EXPECTED COMPLETION DATE]

Relevant work history: [ROLES AND DATES; EMPLOYER NAME IF YOU WANT TO INCLUDE IT]

Personal profile links and prior projects: [URLS]

For any personal achievement or resourcefulness question, use a real event: [CONSTRAINT], [ACTION YOU TOOK], and [SPECIFIC OUTCOME].

## Company and funding facts to complete

Incorporation: [ENTITY NAME, TYPE, JURISDICTION, AND DATE, OR CONFIRM NOT INCORPORATED]

Ownership: [FOUNDERS, PERCENTAGES, OPTIONS, AND ANY OTHER HOLDERS]

Investment to date: [TOTAL AND EACH INVESTOR'S INSTRUMENT, AMOUNT, AND DATE, OR CONFIRM NONE]

Cash, monthly spending, and runway: [CURRENT FIGURES AND AS-OF DATE]

Current fundraising: [STATUS AND AMOUNT, IF ANY]

Other accelerators or incubators: [DETAILS, OR CONFIRM NONE]

Prior YC applications and changes since then: [DETAILS, OR CONFIRM FIRST APPLICATION]

How you heard about YC and any relevant introductions: [FACTUAL ANSWER]

Other startup ideas under consideration: [ONLY IDEAS YOU ARE ACTUALLY CONSIDERING]

Batch preference: Winter 2027, with a planned January 2027 full-time start; San Francisco attendance remains to be confirmed.

## Founder video talking points

YC asks for a one-minute video containing the founders speaking. Use these as prompts, with all founders included if there is more than one. Speak naturally rather than reciting a script.

- Introduce Jacob and any other founders, with one short line about relevant experience.

- Explain the intended pocket cannabis-testing device and companion app for everyday adults.

- Explain that the MVP includes a physical saliva-testing prototype, an app-based reaction task, guided pupil and resting heart-rate capture, and an exploratory model, with the research platform supporting their evaluation.

- State the current progress: app, backend, and firmware software, with simulated sensor readings; no validated assay or impairment model yet.

- Explain the personal reason for pursuing the idea and the next customer or scientific milestone.

## AI coding example if requested by the form

Choose a genuine coding session that shows how you defined a feature, used GPT, reviewed its output, investigated a failure, and checked the resulting behavior. State your own decisions and contributions accurately. The current Winter 2027 field wording and upload requirements need to be checked in the signed-in form.

## References for review

The signed-in Winter 2027 form remains the source for exact fields and limits. [YC application page](https://www.ycombinator.com/apply).

YC recommends clear, concise descriptions, concrete founder achievements, and a credible account of the obstacles. [YC application advice](https://www.ycombinator.com/howtoapply).

The one-minute founder video format and spontaneous delivery come from [YC founder video instructions](https://www.ycombinator.com/video).

Competitor descriptions: [DRUID](https://www.impairmentscience.com/druid-app), [Healgen FDA decision summary](https://www.accessdata.fda.gov/cdrh_docs/reviews/K252523.pdf), and [BACtrack connected breathalyzers](https://www.bactrack.com/collections/smartphone-breathalyzers). These sources establish their described functions; they do not establish our product's performance.

Project implementation and scope are based on the [implementation status](../../IMPLEMENTATION_STATUS.md), [PRD](../../specs/PRD.md), [chemistry review](../../specs/research/THC_CHEMISTRY_REVIEW.md), and [selected integrated MVP scope](../product/MVP_SCOPE.md). Founder background, the savings achievement, AI code generation, intended customer, and absence of traction are Jacob's supplied facts. Personal contribution, dates, legal details, and commitments remain to be completed.
