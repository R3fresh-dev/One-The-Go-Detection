# OTGD-043: Test plan

Canonical spec: `openspec/changes/qualified-participant-acquisition/specs/selected-vendor-ppg/spec.md`

Spec SHA-256: `c6f863bc71ebf167438fbe5cffe07b892da12cc066d0487d21403ff8dd49fa0d`

Baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Decision register: `docs/factory/otgd-20261025-0555/decisions.md`.

Status: PENDING verification specialist planning. Every criterion below requires a mapped check, expected result, prerequisites and explicit software/external scope.

- VPPG-001 Pin and initialize the actual selected sensor SDK
- VPPG-002 Count only fresh bounded vendor records
- VPPG-003 Preserve vendor quality and finite extraction semantics
- VPPG-004 Bind measured output to signed current origin
- VPPG-005 Stop independently of transport and connection replacement
- VPPG-006 Advertise only the installed matching vendor adapter
- VPPG-007 Verify executable software separately from physical qualification
