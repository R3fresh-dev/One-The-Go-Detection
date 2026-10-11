# One-The-Go Detection

Design and development starter for a portable cannabis-assessment device and mobile application, with a separate future breath-alcohol channel.

**Status: engineering specification v0.1 and synthetic integration starter.** The intended cannabis workflow is one saliva collection, one continuous reaction task with repeated trials, and synchronized physiological measurements. The scientific question is whether these measurements can predict a defined functional-impairment endpoint. That question remains open: this repository contains no trained model, validated cannabis assay, working mobile app, or production hardware.

The initial hardware recommendation is an **Arduino Nano ESP32**. Start with the supplied synthetic USB-serial sketch, then implement BLE transport and PPG acquisition. Develop the saliva chemistry with an analytical laboratory in parallel. See the [hardware starter guide](specs/HARDWARE_STARTER_GUIDE.md) for the shopping list, wiring proposal, development sequence, and sources.

## Requested design documents

| Document | What it defines |
|---|---|
| [Product Requirements Document](specs/PRD.md) | Intended users, scope, workflow, product requirements, success criteria, release boundaries, and commercial assumptions |
| [High-Level Design](specs/HLD.md) | Device, mobile, backend, research, and assay responsibilities; system flow; security and deployment boundaries |
| [Low-Level Design](specs/LLD.md) | Record semantics, timing, reaction-task proposal, BLE framing, API behavior, storage, model gating, and errors |
| [Full Specification Sheet](specs/FULL_SPECIFICATION.md) | Normative requirements, subsystem specifications, acceptance evidence, traceability, and decisions required before release |

Supporting documents: [reading order](specs/README.md), [hardware starter guide](specs/HARDWARE_STARTER_GUIDE.md), [validation plan](specs/VALIDATION_PLAN.md), [roadmap](specs/ROADMAP.md), [decision log](specs/DECISIONS.md), [sources](specs/SOURCES.md), and [verification report](specs/VERIFICATION_REPORT.md).

## Research reports

- [THC chemistry and sensing review](specs/research/THC_CHEMISTRY_REVIEW.md): 46-source review of metabolites in blood, urine, and saliva; breath collection; sensing methods; and implications for the pocket device. [PDF edition](specs/research/THC_Chemistry_and_Pocket_Device_Research.pdf).

## What is implemented

- Five JSON Schemas for measurements, sessions, model manifests, results, and synthetic telemetry.
- An OpenAPI 3.1 design describing eight proposed API paths; no server is deployed.
- Fictional, explicitly simulated example data, including pg/mL-to-ng/mL conversion.
- A Python measurement-only demo and contract-verification tools.
- An Arduino sketch that emits synthetic NDJSON over USB serial at 115200 baud.

The sketch has no sensor drivers, BLE implementation, chemical measurement, or impairment inference. It has not been compiled with an Arduino board toolchain or tested on physical hardware. Those are recorded development steps, not implied deliverables.

## Run the local demonstration

Python 3.12 was used for the recorded verification. These commands assume a POSIX shell; activate the virtual environment using the corresponding command on Windows.

```bash
git clone https://github.com/R3fresh-dev/One-The-Go-Detection.git
cd One-The-Go-Detection
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python tools/verify_specs.py
python tools/run_demo.py
python tools/check_telemetry.py examples/synthetic_telemetry.ndjson
```

The demo validates the fictional session and emits JSON with `state: "measurement_only"` and `probability: null`. It does not train a model or estimate an individual's intoxication, metabolic rate, or clearance time. The verifier checks software contracts and documented consistency; passing it does not establish clinical or analytical validity.

See [examples/README.md](examples/README.md) for the fixture meanings and Arduino upload steps, and [contracts/README.md](contracts/README.md) for unit, provenance, missingness, and lifecycle rules.

## Hardware: the first useful milestone

1. Obtain a Nano ESP32, a data-capable USB cable, and basic bench accessories.
2. Open [synthetic_serial.ino](examples/arduino/synthetic_serial/synthetic_serial.ino) in Arduino IDE, select the actual board and port, record the installed toolchain versions, and upload it.
3. Inspect the explicitly synthetic JSON lines. Resetting or reconnecting starts a fresh receiver capture; the starter does not yet provide persistent session identity.
4. Implement and verify the proposed BLE protocol using synthetic data.
5. Add the selected SparkFun MAX30101 + MAX32664 PPG breakout and a repeatable finger fixture. Use the exact wiring and driver configuration described in the hardware guide.
6. In parallel, define the oral-fluid collection method and commission assay feasibility against a qualified reference method.

Phone-camera capture and the reaction task are mobile-development work. ECG begins with simulator evaluation and review of the complete human-contact circuit. Optical stimulus configuration also needs device-specific review before human experiments. A custom PCB follows demonstrated sensing and power requirements.

## Result and release boundaries

| Phase | Purpose | Permitted result |
|---|---|---|
| P0 | Synthetic device/software integration | Measurement-only demonstration |
| P1 | Analytical and acquisition feasibility | Measurements and quality states; no intoxication probability |
| P2 | Authorized controlled research with an independently evaluated endpoint | Gated research estimates only after the specified model and protocol requirements are met |
| P3 | Possible future product | Requires additional validation, a new release contract, and a reviewed intended-use claim |

Cannabinoid detection establishes evidence about exposure. An impairment claim needs independently collected outcome labels and prospective validation of the complete workflow. Adding biometrics does not by itself establish that claim. The evidence and proposed experiments are detailed in the [validation plan](specs/VALIDATION_PLAN.md) and [source register](specs/SOURCES.md).

## Working rules

Keep real participant measurements, identifiable recordings, credentials, and production secrets out of this public repository. Use approved private study storage for research data. The included examples are entirely fictional. Schema-valid data, source labels, or manifest approval strings do not independently authorize research or establish measurement validity.

Changes to units, assay basis, collection matrix, task configuration, feature extraction, hardware scope, or model eligibility require coordinated updates to the specification, contracts, examples, and relevant validation evidence. Use the [decision log](specs/DECISIONS.md) to distinguish settled engineering choices from open scientific and product decisions.
