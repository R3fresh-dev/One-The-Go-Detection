# Data contracts

**Version:** 0.1.0. These files describe proposed exchanges for the development platform. They are not a running API, an implemented inference service, or evidence of measurement accuracy.

## Files

| File | Purpose |
|---|---|
| [measurement.schema.json](measurement.schema.json) | One saliva-analyte result, including units, analytical qualifiers, specimen basis, limits, and provenance. |
| [session.schema.json](session.schema.json) | A capture snapshot linking one collection, one task, profile/context, and physiological components. |
| [model_manifest.schema.json](model_manifest.schema.json) | Proposed model lifecycle, input compatibility, endpoint, policy, timing, and approval references. |
| [result.schema.json](result.schema.json) | Measurement-only, research-estimate, inconclusive, and invalid output envelopes. |
| [telemetry.schema.json](telemetry.schema.json) | The small synthetic serial bring-up record; it is not an assay-result or complete-session message. |
| [openapi.yaml](openapi.yaml) | Proposed HTTP API surface. No service is started by reading or validating this file. |

JSON Schemas use Draft 2020-12; the API description uses OpenAPI 3.1. The `.invalid` schema identifiers are identifiers, not deployed endpoints. See [LLD.md](../specs/LLD.md) for cross-field behavior and [FULL_SPECIFICATION.md](../specs/FULL_SPECIFICATION.md) for normative requirements.

## Measurement meaning

Canonical saliva concentrations use **ng/mL**. The original report remains available for auditing. The starter normalizes **units only**: dividing pg/mL by 1,000 produces ng/mL. It does not apply a new specimen-dilution correction.

Three separate concepts must remain distinct:

- `assay_basis`: `free`, `total_after_hydrolysis`, or `unspecified` describes the biochemical measurement definition.
- `concentration_basis`: `neat_oral_fluid`, `collected_mixture`, or `unspecified` describes the material to which both the original and canonical concentrations refer.
- `correction_status`: `not_corrected`, `laboratory_corrected`, or `unspecified` records whether a correction was already applied upstream. A dilution factor alone does not answer that question.

An unresolved basis can be retained as unresolved data; it cannot silently satisfy a model requiring a specific basis. The manifest's `compatibility_policy_id` identifies a policy that must check exact accepted analyte/method/assay-basis/concentration-basis/correction-status combinations, not merely membership in independent allowlists.

`quantified`, `below_loq`, `above_range`, `not_detected`, `not_measured`, and `invalid` have different meanings. Censored or missing canonical concentrations are `null`, not measured zero. A source report's “BLQ” must not be turned into a claim of detection without supporting information. Preserve its qualifier and applicable limits.

When an acquisition or analysis did not occur, retain its missing status without fabricating a timestamp, waveform, task score, or concentration. An uncollected saliva attempt has an empty reading list and null collection time. Allocated sample/configuration identifiers can describe a planned attempt without proving capture occurred. PPG-derived data must not be labeled ECG. Pupil diameter is in millimeters only when its scale supports that unit.

## Timing and inference boundary

`capture_completed_at` describes completion of the client capture snapshot. It is distinct from server-side database finalization. `target_at` identifies the time represented by the check; `evaluated_at` identifies when a result was produced. A delayed laboratory result is not automatically a current-state measurement.

Only an eligible `research_estimate` may contain a probability. Future use requires an `active_research` model plus independent server checks of protocol, enrollment, compatibility, quality, and approvals. A valid manifest or a client-supplied lifecycle string does not grant those permissions. The supplied local demo accepts only fictional inputs and returns `measurement_only` with null probability.

## Local checks

Run from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python tools/verify_specs.py
python tools/run_demo.py
python tools/check_telemetry.py examples/synthetic_telemetry.ndjson
```

These commands inspect the supplied specification/demo behavior. They do not compile hardware, operate a sensor, validate an assay, or measure predictive performance. [Examples](../examples/README.md) explains the fixtures and serial sketch.
