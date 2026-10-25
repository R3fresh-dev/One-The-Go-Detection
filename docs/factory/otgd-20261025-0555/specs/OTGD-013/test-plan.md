# OTGD-013: Test plan

Canonical spec: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md`

Spec SHA-256: `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29`

Baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Decision register: `docs/factory/otgd-20261025-0555/decisions.md`.

Status: PENDING verification specialist planning. Every criterion below requires a mapped check, expected result, prerequisites and explicit software/external scope.

- CAN-SR-001 Admit a distinct bounded physical reader dialect
- CAN-SR-002 Preserve exact device binding proof and protected keys
- CAN-SR-003 Verify a fresh scoped server start signature on the reader
- CAN-SR-004 Enforce signed expiry without inventing device wall time
- CAN-SR-005 Acquire actual bounded ADC observations from protected material
- CAN-SR-006 Stop hardware independently of transport pressure
- CAN-SR-007 Isolate connection-origin effects and replay privacy
- CAN-SR-008 Bind raw purpose and immutable signed evidence
- CAN-SR-009 Build and qualify the protected SDK branch explicitly
- CAN-SR-010 Preserve external qualification and unknown-driver limits
- CAN-SR-011 Require authenticated encrypted BLE before human telemetry
