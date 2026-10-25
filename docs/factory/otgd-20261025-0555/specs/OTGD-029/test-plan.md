# OTGD-029: Test plan

Canonical spec: `openspec/changes/production-mobile-platform/specs/android-offline-sync/spec.md`

Spec SHA-256: `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9`

Baseline implementation: `0844868aa543af4ab75ac5065ad48cf807b86bb3`.

Decision register: `docs/factory/otgd-20261025-0555/decisions.md`.

Status: PENDING verification specialist planning. Every criterion below requires a mapped check, expected result, prerequisites and explicit software/external scope.

- AND-SYNC-001 Persist before announcing save
- AND-SYNC-002 Require explicit authorized upload
- AND-SYNC-003 Use stable idempotent operations
- AND-SYNC-004 Isolate users and environments
- AND-SYNC-005 Reconcile stale revisions without overwrite
- AND-SYNC-006 Bound retries and preserve terminal failures
- AND-SYNC-007 Preserve scientific and acquisition time
