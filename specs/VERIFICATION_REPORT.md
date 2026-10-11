# Verification Report

**Scope:** local specification, contract, and synthetic-starter verification for version 0.1.\
**Executed:** October 11, 2026 UTC (October 10, 2026 America/Chicago).\
**Environment:** Python 3.12; direct dependency versions recorded in requirements-dev.txt.\
**Result:** all 41 automated contract and documentation checks passed.

## Recorded checks

| Area | Evidence and outcome |
|---|---|
| JSON Schema | All five Draft 2020-12 schemas pass structural validation; supplied measurement, session, manifest, result, and telemetry examples validate. |
| API contract | OpenAPI 3.1 document validates with its local external schema references and contains eight proposed paths. |
| Units and assay semantics | Correct pg/mL-to-ng/mL conversion passes. Incorrect units, factor errors, reversed limits, out-of-range quantification, and numeric values for censored results are rejected. |
| Missingness and provenance | Absent acquisitions can use null timestamps and values. Skipped saliva has an empty analyte list. Unrun analytes cannot invent analysis times. Nonsynthetic profile or assay data are refused by the local demo. |
| Timing and association | Sample mismatches, invalid timing, incorrect acquisition span, telemetry gaps, clock resets, and mixed-device streams are rejected. |
| Physiological records | Nonfinite values, inconsistent BMI, uncalibrated millimeter eye values, and PPG presented as ECG features are rejected. |
| Result boundaries | Measurement-only output cannot carry a probability. Research-result shapes cannot cite an unvalidated model or simulated evidence. Incorrect input digests are rejected. |
| Documentation and code | Local Markdown links resolve, normative requirement identifiers are unique, and Python files parse. |

The standalone demo was executed successfully and returned measurement_only with null probability, classification, and threshold. The telemetry checker accepted the five-record fictional fixture. No predictive model was fitted or evaluated. Markdown destinations were checked; this does not constitute a fresh retrieval of every external citation or a rendered visual review of each document.

## Reproduce

From the repository root with Python 3.12 and the dependencies in [requirements-dev.txt](../requirements-dev.txt):

```bash
python tools/verify_specs.py
python tools/run_demo.py
python tools/check_telemetry.py examples/synthetic_telemetry.ndjson
```

## Scope limits

The Arduino sketch has not been compiled with an Arduino toolchain or tested on a board. No mobile app, API service, BLE implementation, assay, ECG circuit, pupil pipeline, or trained inference model is included. These checks cannot establish analytical accuracy, biological interpretation, predictive performance, electrical or optical suitability, production security, or regulatory status.

The [validation plan](VALIDATION_PLAN.md) defines the experiments and independent evidence needed for subsequent phases. The [hardware starter guide](HARDWARE_STARTER_GUIDE.md) defines the next bench steps.
