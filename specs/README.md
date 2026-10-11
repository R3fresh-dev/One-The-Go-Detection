# Specification package

**Version:** 0.1.0\
**Status:** Proposed engineering and research baseline. No assay, hardware configuration, or impairment model has been validated by this repository.

The product vision is a pocket cannabis-and-alcohol device with a mobile app. The proposed cannabis check combines one saliva collection, one continuous repeated-trial task, pupil response, cardiac measurements, and profile/history. The alcohol channel remains a separate measurement system.

## Reading order

| Order | Document | Use it to answer |
|---|---|---|
| 1 | [PRD](PRD.md) | What are we building, for whom, and what evidence would make it useful? |
| 2 | [Architecture decisions](DECISIONS.md) | Which choices and contract terms are shared across the package? |
| 3 | [Full specification](FULL_SPECIFICATION.md) | What must each subsystem do, who owns it, and how is acceptance demonstrated? |
| 4 | [High-level design](HLD.md) | How do the device, app, assay, backend, and research workflow fit together? |
| 5 | [Low-level design](LLD.md) | What are the data semantics, task rules, state transitions, interfaces, and inference gates? |
| 6 | [Hardware starter guide](HARDWARE_STARTER_GUIDE.md) | Which Arduino board and first sensor should we evaluate, and how should bench development proceed? |
| 7 | [Roadmap](ROADMAP.md) | What work comes next, what can run in parallel, and what defines completion? |
| 8 | [Validation plan](VALIDATION_PLAN.md) | Which analytical, hardware, human-factors, and independent model experiments are required? |
| 9 | [Sources](SOURCES.md) | Which primary studies and official component documents support the decisions, and what do they not establish? |

For an immediate hardware start, read the hardware guide and roadmap first, then use the other documents as implementation references.

## Background research

- [THC chemistry and sensing review](research/THC_CHEMISTRY_REVIEW.md) and [PDF edition](research/THC_Chemistry_and_Pocket_Device_Research.pdf): metabolite chemistry, matrix-specific evidence, breath research, and sensing limitations. Research recommendations inform future decisions; they do not supersede the current requirement register or release gates.

## Contracts and starter material

- [Machine-readable contracts](../contracts/): JSON Schemas and the proposed OpenAPI interface. Structural validity does not establish measurement or model validity.
- [Synthetic examples](../examples/): illustrative records and the Arduino serial sketch. They are not participant data or accuracy evidence.
- [Development tools](../tools/): the local measurement-only demo and verification helpers. These do not implement the mobile app, BLE transport, chemical assay, or inference service.

## Phase boundaries

| Phase | Permitted development result |
|---|---|
| P0 integration | Synthetic/bench integration and explicit quality states; no impairment probability |
| P1 analytical feasibility | Qualified measurements for their stated analytical purpose; no impairment probability |
| P2 controlled research | A research estimate only through approved study and model gates |
| P3 possible product | Requires a new release decision, supported intended use, and completion of applicable evidence gates |

The current model remains **unvalidated**. The saliva sensing chemistry, final hardware, supported phones, endpoint, numerical acceptance limits, and subscription economics remain unresolved where marked. Approximately $20/month is a business hypothesis.

The full specification is the requirement register; the LLD supplies semantics beyond structural schemas. Normative three-digit requirement IDs and two-digit validation experiment IDs serve different purposes. Changes to shared choices require corresponding updates to dependent documents and contracts.
