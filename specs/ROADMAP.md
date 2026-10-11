# Development roadmap

**Version:** 0.1.0\
**Status:** Proposed work sequence; calendar estimates are planning aids, not delivery promises.\
**Starting point:** Documentation, structural contracts, synthetic fixtures, and a USB serial demonstration. No validated detector, BLE implementation, mobile app, assay cartridge, or prediction service is supplied by those artifacts.

## 1. First objective and two parallel tracks

Start with an **Arduino Nano ESP32**. The first objective is a reliable, clearly synthetic measurement path from the board to a receiving computer. Advance to phone communication, then to qualified signal acquisition. Keep the phone responsible for the reaction game and guided pupil capture.

Run two tracks concurrently:

| Track | Initial owner | Work that can start immediately | Dependency before integrating real measurements |
|---|---|---|---|
| **A: software and electronics** | Engineering lead | Run the synthetic demo, bring up the board, implement transport, implement task-event recording, and exercise invalid states | Approved capture configurations, reference measurements, and the appropriate hardware gates |
| **B: professional assay and study development** | Analytical lead, with clinical/statistical leads | Prepare an assay feasibility brief, identify laboratory capabilities, define the independent outcome, and estimate study needs | Agreed method, qualified collection, research authorization, and prespecified acceptance criteria |

These tracks join when trustworthy chemical and app measurements can be associated with the same check. A custom PCB comes after measurement interfaces, power requirements, sampling paths, and assay feasibility are sufficiently stable.

Use [FULL_SPECIFICATION.md](FULL_SPECIFICATION.md) for requirement IDs and blocking gates. Assign each owner role to a named person as the team forms.

## 2. Suggested first week: integration work

The day labels suggest order. Repeat a stage until its definition of done is met; hardware delivery, unfamiliar tooling, or a failed experiment may extend it.

### Day 1 — Reproduce the software examples

Read [DECISIONS.md](DECISIONS.md), [LLD.md](LLD.md), and [HARDWARE_STARTER_GUIDE.md](HARDWARE_STARTER_GUIDE.md). From the repository root, follow the root README's environment instructions and run:

```bash
python tools/verify_specs.py
python tools/run_demo.py
```

Inspect the fixtures, qualifiers, and resulting `measurement_only` record. Identify where original units, canonical ng/mL, sample identity, and provenance are represented. Do not interpret the synthetic concentration values as product detection limits or training data.

**Done:** Verification completes, the demo is reproducible, and the result has no impairment probability. Record the actual commands and environment used. Relevant requirements: HW-002, ANA-006–008, MOD-009, DOC-001.

### Day 2 — Bring up the Nano alone

Purchase only the initial board and basic accessories needed for this step. The hardware guide identifies the selected board, wiring conventions, and a **$130–220 planning allowance** for a broader starter BLE/PPG bench setup. This allowance excludes chemistry, ECG equipment, alcohol calibration, studies, and the phone.

Install the current board toolchain and record its versions. Upload [synthetic_serial.ino](../examples/arduino/synthetic_serial/synthetic_serial.ino). Use a data-capable USB cable and the configured 115200 baud rate. Leave sensor modules and electrodes disconnected.

**Done:** Complete NDJSON records arrive, `source` remains `simulated`, and `assay_ready` remains false. Reset/reconnect behavior is understood. This sketch is a bring-up stream, not the complete session protocol. Relevant requirements: HW-001–004.

### Day 3 — Implement a robust receiver and synthetic BLE transport

Start with parsing, incomplete-line handling, sequence tracking, and visible connection state. Then implement the proposed LLD BLE service and bounded message framing as a separate increment. Add boot identity and session identity before associating incoming readings with finalized sessions.

Test an intentional disconnect, a duplicate command, an incomplete transfer, and a device reset. Use synthetic data throughout this stage. Save a short synthetic trace that explains the expected receiver behavior.

**Done:** The receiver associates accepted messages with the correct device boot and session; it rejects malformed or stale content and never silently reuses an earlier reading. BLE implementation has its own evidence rather than inheriting success from USB. Relevant requirements: HW-003/004, OPS-002/004.

### Day 4 — Integrate the first sensor and task separately

For the selected SparkFun PPG breakout, follow the exact hardware-guide wiring, including RESET and MFIO. Power down before rewiring. Confirm initialization and quality/status fields before displaying a processed value. Use appropriate fixtures and the permitted nonclinical acquisition procedure; retain missing-data and contact-quality information.

In parallel, implement the one continuous `choice_inhibit_v0` task. Start with event recording and deterministic replay: six practice trials, 48 scored go trials, and 12 scored no-go trials. Follow LLD timing and interruption semantics. Use synthetic input events for feature checks before investigating performance in people.

**Done:** Sensor acquisition quality is separate from the displayed number, and task features reproduce from the saved events. Neither path estimates intoxication. Relevant requirements: HW-007, APP-004–008/010.

### Day 5 — Demonstrate a complete synthetic check

Assemble a synthetic session containing profile, saliva placeholders, pupil placeholders, cardiac capture metadata, and a recorded task. Keep real and simulated provenance distinct. Finalize once, retry the submission, and demonstrate that it does not create duplicate results.

Exercise missing saliva, an interrupted task, a failed eye recording, and unavailable model states. Confirm that no path produces a probability. Keep real biosignals and participant information out of repository fixtures.

**Done:** Another developer can reproduce the demonstration and explain every result state. Record unresolved work rather than relabeling placeholders as implemented sensors. Relevant requirements: APP-012, MOD-009/010, SEC-001, OPS-002/003.

## 3. Assay and research work running alongside the first week

Prepare a reviewable feasibility brief for a qualified analytical laboratory or assay-development partner. Do not purchase a cartridge reader architecture until the measurement method is selected.

The brief should request:

1. A defined saliva collection method, volume/dilution, handling, stability, and adequacy rules.
2. Parent delta-9 THC feasibility first; separate evidence for THC-COOH and 11-OH-THC.
3. Free versus hydrolyzed-total definitions, target measurement range, and reference method.
4. Experiments for precision, bias, recovery, interference, carryover, limits, and lot variation.
5. Expected assay time, reader requirements, storage, consumable cost, and a path to a sealed cartridge.

The analytical lead proposes acceptance limits before the qualification experiments. The statistical and clinical leads define an independent functional endpoint, participant population, sampling times, and the intended interpretation. A chemical positive and performance on the predictor game cannot independently supply the correct impairment label.

**Done:** Gates G-01–03 have specific experiment plans and accountable people; G-07/G-08 have a study-readiness plan. An assay shopping list or a selected microcontroller is not evidence that the chemistry works.

## 4. Subsequent milestones and dependencies

| Milestone | Tasks and dependencies | Definition of done |
|---|---|---|
| **P0 integration accepted** | Complete serial/BLE evidence, contracts, task replay, provenance, and negative-state demonstrations | Requirements are traced to observed bench behavior; inference remains unavailable |
| **P1 capture feasibility** | Establish camera timing/quality with fixtures; review optical settings; evaluate ECG with a simulator | G-04–06 provide approved configurations and repeatability evidence before corresponding participant capture |
| **P1 chemistry feasibility** | Execute the professional assay plan using the actual collection matrix and a reference method | G-02/G-03 support the selected analytes, range, limitations, and feasible reader interface |
| **Integrated research prototype** | Join the qualified channels, retain the one-sample/one-task boundary, synchronize timing, review human-contact design | Each measurement can be traced to the correct acquisition and approved configuration |
| **P2 authorized study** | Close research/data gates, recruit through the approved protocol, collect independent outcomes | The complete dataset includes failures, controls, and needed population/device strata |
| **P2 model evaluation** | Train with participant separation; compare chemistry-only, app-only, combined, and ECG-removed models | Locked evaluation quantifies uncertainty, calibration, errors, inconclusive coverage, and incremental benefit |
| **Product engineering decision** | Review evidence, economics, applicability, and usability; then finalize PCB/enclosure requirements | A justified P3 proposal specifies the claim and remaining release work; P2 does not automatically authorize launch |

Do not assign a fixed clinical-development completion date until partners, study scope, recruitment, and approvals are known. Software milestones can progress while those dependencies are resolved.

## 5. Decisions to resolve before major purchases

| Question | Accountable role | Decision consequence |
|---|---|---|
| What functional endpoint and error rates define success? | Clinical/statistical leads | Sets labels, study size, thresholds, and eventual claim |
| Can the intended saliva channels be quantified economically in one collection? | Analytical/commercial leads | Determines cartridge, reader technique, and whether optional channels survive |
| Does ECG add useful prediction beyond heart rate and other inputs? | ML/validation leads | Determines whether electrodes and ECG hardware merit final integration |
| Which phones reproduce the task and eye protocol? | App/optical leads | Defines supported devices and acquisition constraints |
| What does $20/month include? | Product/commercial leads | Defines hardware payment, consumable allowance, replacement, and margin scenarios |

Before ordering a custom PCB, measure actual power and signal requirements and freeze the assay electrical/optical interface. Before enclosure tooling, demonstrate sample handling, contamination separation, cartridge insertion, cleaning, and user contact with inexpensive fixtures. Before promising subscription economics, obtain supplier evidence and model usage. These decisions keep the next investment tied to a demonstrated need.
