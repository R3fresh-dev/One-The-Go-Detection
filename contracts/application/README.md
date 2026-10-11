# Application contracts

These generated contracts accompany the unchanged strict scientific v0.1 schemas in the parent directory. They implement the [reviewed shared contract](../../openspec/changes/production-mobile-platform/shared-contracts.md).

Regenerate from locked source at the repository root:

```bash
uv run --project services/api python tools/generate_application_contracts.py
```

| Contract | Purpose |
|---|---|
| `openapi.json` | Application API, owner/generation headers, current access-token policy, typed requests and error dispositions. |
| `ProfileWrite.schema.json` | Optional demographics/context, canonical units and BMI consistency. |
| `CaptureContext.schema.json` | Frozen profile/history hashes, original self-report timing and exact configuration/device references. |
| `CaptureAttempt.schema.json` | Complete acquisition identity, terminal status, predecessor, source, projection and companion evidence. |
| `EvidenceManifest.schema.json` | Context digest, all attempts and independently selected records. |
| `Alcohol.schema.json` | Separate breath-alcohol measurement with qualifiers, limits, mg/L units and provenance. |
| `ExportRequest.schema.json` | Explicit single/selected/all scope and no implicit raw authorization. |
| `CaptureAuthorization.schema.json`, `StartAuthorization.schema.json` | Fresh single-use qualified-start request/consumption. |
| `Attestation.schema.json` | Domain-separated signature envelope and exact normalized payload. |
| `SyntheticDeviceCapture.schema.json` | Bounded fictional transport, association, clock exchanges, fixed values and transcript. |
| `ReplacementLinks.schema.json` | Owner/generation-scoped navigation between immutable physical checks, with bounded keyset pagination. |
| `ReportRevisionRequest.schema.json`, `ReportDescriptor.schema.json` | Authorized same-specimen correction/reanalysis and its immutable original-evidence links. |
| `ReportRevisionResult.schema.json`, `ReportRevisionCompanion.schema.json` | Separate measurement-only report result, effective analyte projection and complete hashed companion. |
| `ReportRevisionList.schema.json`, `ReportRevisionDetail.schema.json`, `ReportRevisionIndex.schema.json` | Typed historical navigation and exact separately bounded export-file references. |
| `canonical-golden.json` | RFC 8785 Unicode/numeric fixtures and rejected JSON inputs. |

A JSON Schema pass is one layer. Server semantic checks additionally enforce exact nested metadata keys, limits, source/time/identity consistency, native schedule and score recomputation, simulator transcript and clock arithmetic, full manifest lineage, current authority and immutable state. The original snapshot carries a selected projection; the complete native evidence is retained and hashed in its companion attempt. Unknown fields cannot be used to smuggle raw health media into unrestricted metadata.

Report contracts embed `ScientificMeasurement`, derived without modification from the original `measurement.schema.json`. This prevents generated clients from interpreting the report DTO's delegated measurement validation as permission to submit arbitrary dictionaries. Semantic unit, specimen, chronology, method-authority and chain checks remain required. Administrative report revisions never rewrite the original capture or supply an intoxication estimate; see the [reviewed revision contract](../../openspec/changes/production-mobile-platform/report-revision-contract.md).

## Fixture provenance

`fixtures/synthetic-transport-ppg.json`, `synthetic-transport-ecg.json` and `synthetic-transport-saliva.json` were emitted by the application's **software-only local simulator**, using its actual framing/controller/clock code. They contain no human acquisition and establish no radio or sensor performance. The Python tests independently check the exact JavaScript-produced SHA-256 and mapped projection, then reject source, identity, transcript, clock and payload tampering.

The mobile app's fictional and native-shaped integration bundles live in `apps/mobile/testfixtures`. The latter is explicitly host-generated contract evidence with simulator provenance. It is not a recording from an Android phone or iPhone. API integration tests remap only the fictional account ID, retain the complete companion evidence, finalize through the worker and read the immutable record back.
