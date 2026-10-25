## Evidence reconciliation — 2026-10-25

Earlier checkboxes, BR-001–006 descriptions and the `9376dba` evidence summary are historical checkpoints, not the present source disposition or a final PASS. The later conditional changes supply signed reader, optical/raw, selected PPG, participant/lab and research-model software. Each feature scenario/native matrix remains open until fully executed for the current candidate. ENG-004–008 are focused copy/assertion gaps; ENG-009/010/011 cover actual worker/browser/native execution. All 20 features and their 140 requirements / 321 scenarios remain in scope; later amendments retain their own canonical IDs. No checkbox is upgraded by this author.

Current sources and exact bounded follow-up: [engineering author audit](../../../docs/factory/otgd-20261025-0555/reports/engineering-audit.md), [spec reconciliation](../../../docs/factory/otgd-20261025-0555/reports/spec-reconciliation.md), and [implementation plan](../../../docs/factory/otgd-20261025-0555/reports/implementation-plan.md). Checked history is preserved; unchecked implementation-plus-verification rows are **implemented-unverified** where source is present, **blocked** for unavailable execution/external inputs, and never silently completed. These author dispositions are not independent signoff.

---

# Implementation and verification tasks

Execute in this order: specification/review checkpoint, shared foundations, feature implementation, integration/release verification. A checked implementation task means the code exists and its stated local checks passed; external execution is recorded independently. Do not check a native build, LocalStack test, cloud deployment, or scientific qualification without actual evidence.

## 1. Specification and review checkpoint

- [x] 1.1 Analyze PRD, HLD, LLD, existing contracts, and the user's revised AWS requirement; record traceability.
- [x] 1.2 Write 20 fine-grained feature specs with customer journeys, engineering boundaries, Android/iOS parity, and negative acceptance scenarios.
- [x] 1.3 Validate all OpenSpec artifacts in strict mode and check requirement IDs, local links, and scenario structure.
- [x] 1.4 Complete independent product/domain, security/data, and platform/operations adversarial reviews across all 20 features.
- [x] 1.5 Resolve and re-review every critical/high finding; record all remaining dispositions and exact corrections.
- [x] 1.6 Commit the reviewed specification checkpoint before application implementation.

## 2. Shared application and service foundations

- [x] 2.1 Create locked dependency workspaces for Expo mobile, native module, Python service, and AWS CDK; document supported runtimes.
- [x] 2.2 Implement validated immutable environment configuration, separate local/QA/prod identities, release-only cloud restrictions, and safe public app configuration.
- [x] 2.3 Implement schema validation and shared JCS/SHA-256 fixtures with duplicate-key, Unicode, numeric, and cross-language rejection cases.
- [x] 2.4 Implement PostgreSQL migrations, ownership constraints, immutable revisions, idempotency records, transactional outbox, deletion barriers, and audit events.
- [x] 2.5 Implement Cognito RS256 access-token verification, PKCE mobile login, single-flight refresh, and isolated local development issuer with one-use codes.
- [x] 2.6 Implement API error envelopes, request/body limits, safe request IDs, authorization-before-serialization, and generated OpenAPI.
- [x] 2.7 Implement S3 artifact verification and SQS worker dispatch/retries/DLQ with durable result and privacy jobs.
- [x] 2.8 Implement native SQLCipher storage with protected keys, account/environment namespaces, encrypted outbox, and memory-only web preview.

## 3. Alcohol Channel — AND-ALC-001–AND-ALC-006

- [ ] 3.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 3.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-alcohol-channel](specs/android-alcohol-channel/spec.md).
- [ ] 3.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 6 requirements.
- [x] 3.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **BR-005: approved breath-device adapter and native specimen workflow**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 4. App Environment — AND-ENV-001–AND-ENV-007

- [x] 4.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 4.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-app-environment](specs/android-app-environment/spec.md).
- [ ] 4.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 4.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 5. Dashboard — AND-DASH-001–AND-DASH-007

- [x] 5.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 5.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-dashboard](specs/android-dashboard/spec.md).
- [ ] 5.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 5.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 6. Data Export — AND-EXP-001–AND-EXP-007

- [ ] 6.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 6.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-data-export](specs/android-data-export/spec.md).
- [ ] 6.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 6.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **historical BR-006, now supplied conditionally by raw recording/export software; actual native protection, live object/worker races and exact-candidate export acceptance remain open**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 7. Device Pairing — AND-DEV-001–AND-DEV-008

- [ ] 7.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 7.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-device-pairing](specs/android-device-pairing/spec.md).
- [ ] 7.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 8 requirements.
- [x] 7.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **historical BR-001, now supplied by signed-reader binding/start/unbinding software; real protected provisioning, native/radio execution and independent human qualification remain open**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 8. Ecg Capture — AND-ECG-001–AND-ECG-007

- [ ] 8.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 8.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-ecg-capture](specs/android-ecg-capture/spec.md).
- [ ] 8.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 8.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **historical BR-003 ECG path: bounded signed ADC/raw software is present; actual supported front-end, observed permitted connection-state verification, safety/calibration and native execution remain blocked**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 9. Eye Capture — AND-EYE-001–AND-EYE-007

- [ ] 9.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 9.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-eye-capture](specs/android-eye-capture/spec.md).
- [ ] 9.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 9.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **historical BR-002, now supplied by conditional native extraction and encrypted raw software; actual OS execution and independently approved physical optics remain open**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 10. Guided Check — AND-CHECK-001–AND-CHECK-008

- [x] 10.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 10.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-guided-check](specs/android-guided-check/spec.md).
- [ ] 10.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 8 requirements.
- [x] 10.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 11. Heart Rate — AND-HR-001–AND-HR-007

- [ ] 11.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 11.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-heart-rate](specs/android-heart-rate/spec.md).
- [ ] 11.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 11.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **historical BR-003 PPG path: selected pinned SparkFun/MAX32664 driver and freshness/quality software are present; actual sensor/reference/native qualification remains open**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 12. History — AND-HIST-001–AND-HIST-007

- [x] 12.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 12.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-history](specs/android-history/spec.md).
- [ ] 12.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 12.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 13. Offline Sync — AND-SYNC-001–AND-SYNC-007

- [x] 13.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 13.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-offline-sync](specs/android-offline-sync/spec.md).
- [ ] 13.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 13.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 14. Onboarding — AND-ONB-001–AND-ONB-006

- [x] 14.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 14.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-onboarding](specs/android-onboarding/spec.md).
- [ ] 14.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 6 requirements.
- [x] 14.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 15. Privacy Controls — AND-PRIV-001–AND-PRIV-007

- [x] 15.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 15.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-privacy-controls](specs/android-privacy-controls/spec.md).
- [ ] 15.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 15.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 16. Profile — AND-PRO-001–AND-PRO-007

- [x] 16.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 16.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-profile](specs/android-profile/spec.md).
- [ ] 16.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 16.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 17. Reaction Task — AND-TASK-001–AND-TASK-008

- [x] 17.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 17.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-reaction-task](specs/android-reaction-task/spec.md).
- [ ] 17.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 8 requirements.
- [x] 17.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 18. Results — AND-RES-001–AND-RES-007

- [x] 18.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 18.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-results](specs/android-results/spec.md).
- [ ] 18.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 18.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 19. Saliva Measurement — AND-SAL-001–AND-SAL-007

- [ ] 19.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 19.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-saliva-measurement](specs/android-saliva-measurement/spec.md).
- [ ] 19.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 19.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **historical BR-004: approved-reference-lab form/handoff/import software is present; genuine collection/analytical approval and a selected portable quantitative reader remain separate unavailable inputs**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 20. Settings Accessibility — AND-SET-001–AND-SET-007

- [x] 20.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 20.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-settings-accessibility](specs/android-settings-accessibility/spec.md).
- [ ] 20.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 20.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 21. Sign In — AND-AUTH-001–AND-AUTH-007

- [x] 21.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 21.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-sign-in](specs/android-sign-in/spec.md).
- [ ] 21.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 21.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 22. Study Enrollment — AND-STUDY-001–AND-STUDY-006

- [ ] 22.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 22.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-study-enrollment](specs/android-study-enrollment/spec.md).
- [ ] 22.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 6 requirements.
- [x] 22.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

The enrollment, exact-version consent and withdrawal journeys are supplied. Later participant and signed/native acquisition changes supply fresh-start orchestration in source. **AND-STUDY-004** remains open for exact-candidate positive/refusal/lifecycle execution with actual permitted hardware/configuration and genuine authority; the historical BR-001–004 labels do not establish absent software or qualified hardware.

## 23. LocalStack, AWS QA, and AWS production

- [x] 23.1 Supply Dockerfiles and Compose for API/worker/PostgreSQL/LocalStack/local identity, migration/init jobs, health dependencies, loopback defaults, and documented physical-phone override.
- [x] 23.2 Supply executable local bootstrap and integration tests using actual S3/SQS endpoints; distinguish tests with mocks from tests against LocalStack.
- [x] 23.3 Implement separate QA/prod CDK stacks with TLS ALB, private Fargate/RDS, private encrypted objects and queues, Cognito, secrets, backups, alarms, and least-privilege roles.
- [x] 23.4 Implement immutable image-digest promotion and one-off migration commands with deployment prerequisites and rollback/runbook instructions.
- [x] 23.5 Verify synthesized CloudFormation assertions for networking, encryption, private storage, retention, identity isolation, and production capacity.
- [ ] 23.6 Execute actual LocalStack integration when Docker and the configured LocalStack release prerequisites are available (the default pinned community release requires no licensed activation token); record exact commands/results or the concrete external blocker.
- [ ] 23.7 Execute QA deployment, restore/incident drill, and load targets with authorized AWS inputs; keep unexecuted work visible.
- [ ] 23.8 Execute production deployment only with actual deployment inputs and the release gates satisfied; no deployment is implied by synthesis.

## 24. Integrated verification and delivery

- [x] 24.1 Run existing 41 contract checks and adapt only intentionally superseded inventory assumptions; preserve semantic rejection checks.
- [ ] 24.2 Run mobile/service tests and cross-language contracts; exercise complete fictional check, upload retry, privacy jobs, account changes, and result rendering.
- [x] 24.3 Run PostgreSQL concurrency and owner-isolation cases, including duplicate finalization and deletion racing queued work.
- [x] 24.4 Compile Android native code, execute Kotlin suites and produce the verified local preview/debug APKs in actual CI.
- [ ] 24.4a Execute Android emulator/physical-device journeys, permissions, lifecycle, secure storage, BLE and accessibility checks; compilation alone does not close this task.
- [x] 24.5 Compile the complete iOS simulator app and execute Swift suites on actual macOS/Xcode CI; the final `9376dba` checkpoint passed and produced its own artifact.
- [ ] 24.5a Execute iOS simulator/physical-device journeys, permissions, lifecycle, secure storage, BLE and VoiceOver checks; compilation alone does not close this task.
- [x] 24.6 Review implementation against adversarial findings; fix material regressions and document release limitations.
- [x] 24.7 Update shopping list, root quick start, API reference, environment/deployment runbooks, feature implementation ledger, and verification report.
- [x] 24.8 Commit implemented artifacts and lockfiles; report commit IDs, local start commands, verified checks, and outstanding external release prerequisites.

For 24.2, the host/API/cross-language suites and six browser journeys passed. The complete account/native application integration against actual LocalStack, including its asynchronous upload/privacy path, still requires the declared runtime and any prerequisites of its explicitly selected release; the combined task remains open for that execution.

## Evidence scope at the current implementation checkpoint

The [requirement map](verification/implementation-map.md) links every requirement to source, named tests and remaining native/cloud/qualification evidence. Section 3–22 scenario tasks remain open until their entire applicable acceptance matrix has been executed; passing host or browser tests do not automatically execute all 321 written scenarios. Later conditional software supersedes the old blanket positive-code-gap descriptions; current concrete software/assertion gaps are ENG-004–010, while actual native execution and independent qualification remain separate open work.

The [CI evidence ledger](verification/ci-evidence.md) records actual Android/iOS/firmware compilation and PostgreSQL execution. At final build checkpoint `9376dba`, native and platform workflows both passed: **7/7 Android JUnit tests, 146/146 mobile host tests, the Swift test/build steps, both APKs, the iOS simulator package, actual Nano ESP32 compilation and 171 actual-PostgreSQL tests with no skips**. Two migration replays and least-privilege checks passed. Actual LocalStack, AWS QA, production, store distribution and native emulator/physical-phone interaction remain open. Those 121 source-present / 15 conditional positive-code-gap / 4 operations-source dispositions describe that historical checkpoint only. They are not current source counts or final acceptance; use the run inventory and current audits for present disposition.
