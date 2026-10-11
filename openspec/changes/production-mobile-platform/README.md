# Feature specification index and source analysis

This change contains one OpenSpec capability per Android application feature. Each feature also defines iOS parity; shared backend and infrastructure responsibilities are traced through the customer feature that needs them. The detailed [design](design.md), [shared application contracts](shared-contracts.md), [platform contract](platform-contract.md), [proposal](proposal.md), [tasks](tasks.md), and feature requirements are one review unit.

## Source analysis

| Source | Existing decisions retained | Detail supplied in this change |
|---|---|---|
| [PRD](../../../specs/PRD.md) §§4–8 | One collection/one task, distinct evidence states, optional context, separate alcohol, unknown values, valid clinical evidence before inference | Screen entry/exit, exact controls and copy, permissions, account-free demo, retry/cancel/error journeys, acceptance scenarios |
| [HLD](../../../specs/HLD.md) §§4–8 | Mobile acquisition, FastAPI/PostgreSQL, private artifacts, provenance, offline recovery | Native bridges, SQLCipher, OAuth/PKCE, deployment boundaries, transactional outbox, owner isolation, LocalStack/QA/prod topology |
| [LLD](../../../specs/LLD.md) §§3–12 | Identifiers, clock uncertainty, analyte qualifiers, deterministic reaction contract, immutable finalization | Endpoint and DTO rules, idempotency and ETags, JCS hashing, device binding, capability enforcement, lifecycle failure handling |
| [Full specification](../../../specs/FULL_SPECIFICATION.md) §§3–11 | Normative requirement IDs and scientific gates G-01–G-14 | Fine-grained AND-* requirements with negative scenarios and engineering evidence requirements |
| User's latest instruction | Detailed OpenSpec before implementation, adversarial review of all specs, Android and iOS implementation, LocalStack then AWS QA and prod | Mandatory review checkpoint, three deployment configurations, per-feature implementation/verification ledger |

The later instruction makes AWS environments required, superseding the earlier optional AWS wording. Production engineering remains separate from assay/model/optics/electrical qualification; the existing scientific gates remain open. Any design correction made during review is recorded with the originating finding.

## Feature inventory

| Android application feature (iOS parity included) | Requirement range | Requirements | Acceptance scenarios |
|---|---|---:|---:|
| [android-alcohol-channel](specs/android-alcohol-channel/spec.md) | AND-ALC-001–AND-ALC-006 | 6 | 12 |
| [android-app-environment](specs/android-app-environment/spec.md) | AND-ENV-001–AND-ENV-007 | 7 | 14 |
| [android-dashboard](specs/android-dashboard/spec.md) | AND-DASH-001–AND-DASH-007 | 7 | 17 |
| [android-data-export](specs/android-data-export/spec.md) | AND-EXP-001–AND-EXP-007 | 7 | 14 |
| [android-device-pairing](specs/android-device-pairing/spec.md) | AND-DEV-001–AND-DEV-008 | 8 | 19 |
| [android-ecg-capture](specs/android-ecg-capture/spec.md) | AND-ECG-001–AND-ECG-007 | 7 | 16 |
| [android-eye-capture](specs/android-eye-capture/spec.md) | AND-EYE-001–AND-EYE-007 | 7 | 16 |
| [android-guided-check](specs/android-guided-check/spec.md) | AND-CHECK-001–AND-CHECK-008 | 8 | 21 |
| [android-heart-rate](specs/android-heart-rate/spec.md) | AND-HR-001–AND-HR-007 | 7 | 16 |
| [android-history](specs/android-history/spec.md) | AND-HIST-001–AND-HIST-007 | 7 | 17 |
| [android-offline-sync](specs/android-offline-sync/spec.md) | AND-SYNC-001–AND-SYNC-007 | 7 | 14 |
| [android-onboarding](specs/android-onboarding/spec.md) | AND-ONB-001–AND-ONB-006 | 6 | 14 |
| [android-privacy-controls](specs/android-privacy-controls/spec.md) | AND-PRIV-001–AND-PRIV-007 | 7 | 17 |
| [android-profile](specs/android-profile/spec.md) | AND-PRO-001–AND-PRO-007 | 7 | 16 |
| [android-reaction-task](specs/android-reaction-task/spec.md) | AND-TASK-001–AND-TASK-008 | 8 | 22 |
| [android-results](specs/android-results/spec.md) | AND-RES-001–AND-RES-007 | 7 | 14 |
| [android-saliva-measurement](specs/android-saliva-measurement/spec.md) | AND-SAL-001–AND-SAL-007 | 7 | 16 |
| [android-settings-accessibility](specs/android-settings-accessibility/spec.md) | AND-SET-001–AND-SET-007 | 7 | 17 |
| [android-sign-in](specs/android-sign-in/spec.md) | AND-AUTH-001–AND-AUTH-007 | 7 | 17 |
| [android-study-enrollment](specs/android-study-enrollment/spec.md) | AND-STUDY-001–AND-STUDY-006 | 6 | 12 |
| **Total** | | **140** | **321** |

## Required review perspectives

Every feature is read by independent reviewers through product/domain, security/data, and platform/operations perspectives. Author self-checks do not replace independent review. Reviewers record concrete counterexamples and severities; root resolves the specifications and asks reviewers to recheck the corrections. Open critical/high findings block application implementation. An accepted medium/low limitation must identify its bounded scope and verification consequence.

Review reports live in `reviews/`. The resolution ledger identifies the exact correction and re-review disposition. Spec validation checks syntax and structure; it does not establish correctness, clinical validity, native compilation, LocalStack integration, or AWS deployment.

## Reviewed implementation amendments

Three concrete contracts were frozen before their respective follow-up implementations:

- [Administrative laboratory report revisions](report-revision-contract.md), with the [six-finding adversarial review ledger](reviews/report-revision-review.md), preserve the original sample, target and evidence while adding separately hashed report/result versions.
- [Physical replacement navigation](replacement-links-contract.md) defines bounded, owner/generation-scoped original/replacement links. Its review correction excludes mutable uploaded drafts.
- [Synthetic live signal preview](synthetic-signal-contract.md) defines exact fictional PPG/ECG display bounds, fault states and deadlines. It cannot authorize a valid capture without the unchanged complete transport evidence.

The [implementation map](verification/implementation-map.md), [machine-readable requirement map](verification/requirements-implementation.json), and [CI evidence](verification/ci-evidence.md) distinguish supplied source, executed checks and remaining external gates.

## Repository synchronization

The source analysis uses the unchanged normative PRD/HLD/LLD. Before this checkpoint, upstream research and commercial-strategy documentation through `e2226e28a80e73729b9763bd6c65bab533b52403` was preserved by fast-forward. Those documents identify proposed alternative commercial scope and explicitly do not amend the normative PRD. This change therefore retains the requested multimodal research application and its unavailable clinical-inference gate.
