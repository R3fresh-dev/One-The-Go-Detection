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

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **BR-006: authorized raw-acquisition artifact orchestration; structured export integration is separately verified**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 7. Device Pairing — AND-DEV-001–AND-DEV-008

- [ ] 7.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 7.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-device-pairing](specs/android-device-pairing/spec.md).
- [ ] 7.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 8 requirements.
- [x] 7.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **BR-001: provisioned human-reader client binding, fresh qualified starts and durable unbinding**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 8. Ecg Capture — AND-ECG-001–AND-ECG-007

- [ ] 8.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 8.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-ecg-capture](specs/android-ecg-capture/spec.md).
- [ ] 8.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 8.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **BR-003: qualified physical ECG adapter and calibrated waveform/feature pipeline**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

## 9. Eye Capture — AND-EYE-001–AND-EYE-007

- [ ] 9.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [ ] 9.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-eye-capture](specs/android-eye-capture/spec.md).
- [ ] 9.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 7 requirements.
- [x] 9.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **BR-002: approved frame/illumination extraction and encrypted raw optical evidence**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

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

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **BR-003: qualified physical PPG adapter and its quality pipeline**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

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

Current-release demonstration, refusal and available measurement paths are supplied. The original full implementation tasks above remain open for **BR-004: approved saliva collection/handling and quantitative reader workflow**. See the requirement map for exact clauses; no simulator or unavailable state is counted as that positive branch.

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

- [x] 22.1 Implement the specified screen journey, copy, navigation, field validation, and accessible controls for Android and iOS.
- [x] 22.2 Implement the feature data/state contract, authorized API or native integration, provenance, and persistence boundaries in [android-study-enrollment](specs/android-study-enrollment/spec.md).
- [ ] 22.3 Verify positive, failure, cancel/restart, permission, ownership, and offline scenarios applicable to this feature; record test references for its 6 requirements.
- [x] 22.4 Record platform evidence and any hardware, clinical configuration, credentials, or device-only verification still required; do not substitute simulated evidence.

## 23. LocalStack, AWS QA, and AWS production

- [x] 23.1 Supply Dockerfiles and Compose for API/worker/PostgreSQL/LocalStack/local identity, migration/init jobs, health dependencies, loopback defaults, and documented physical-phone override.
- [x] 23.2 Supply executable local bootstrap and integration tests using actual S3/SQS endpoints; distinguish tests with mocks from tests against LocalStack.
- [x] 23.3 Implement separate QA/prod CDK stacks with TLS ALB, private Fargate/RDS, private encrypted objects and queues, Cognito, secrets, backups, alarms, and least-privilege roles.
- [x] 23.4 Implement immutable image-digest promotion and one-off migration commands with deployment prerequisites and rollback/runbook instructions.
- [x] 23.5 Verify synthesized CloudFormation assertions for networking, encryption, private storage, retention, identity isolation, and production capacity.
- [ ] 23.6 Execute actual LocalStack integration when Docker and an activation token are available; record exact commands/results or the concrete external blocker.
- [ ] 23.7 Execute QA deployment, restore/incident drill, and load targets with authorized AWS inputs; keep unexecuted work visible.
- [ ] 23.8 Execute production deployment only with actual deployment inputs and the release gates satisfied; no deployment is implied by synthesis.

## 24. Integrated verification and delivery

- [x] 24.1 Run existing 41 contract checks and adapt only intentionally superseded inventory assumptions; preserve semantic rejection checks.
- [ ] 24.2 Run mobile/service tests and cross-language contracts; exercise complete fictional check, upload retry, privacy jobs, account changes, and result rendering.
- [x] 24.3 Run PostgreSQL concurrency and owner-isolation cases, including duplicate finalization and deletion racing queued work.
- [ ] 24.4 Compile Android native code, execute Kotlin suites and produce the verified local preview/debug APKs in actual CI.
- [ ] 24.4a Execute Android emulator/physical-device journeys, permissions, lifecycle, secure storage, BLE and accessibility checks; compilation alone does not close this task.
- [x] 24.5 Compile the complete iOS simulator app and execute Swift suites on actual macOS/Xcode CI; initial checkpoint passed, and changed source requires a fresh build artifact.
- [ ] 24.5a Execute iOS simulator/physical-device journeys, permissions, lifecycle, secure storage, BLE and VoiceOver checks; compilation alone does not close this task.
- [ ] 24.6 Review implementation against adversarial findings; fix material regressions and document release limitations.
- [ ] 24.7 Update shopping list, root quick start, API reference, environment/deployment runbooks, feature implementation ledger, and verification report.
- [ ] 24.8 Commit implemented artifacts and lockfiles; report commit IDs, local start commands, verified checks, and outstanding external release prerequisites.

## Evidence scope at the current implementation checkpoint

The [requirement map](verification/implementation-map.md) links every requirement to source, named tests and remaining native/cloud/qualification evidence. Section 3–22 scenario tasks remain open until their entire applicable acceptance matrix has been executed; passing host or browser tests do not automatically execute all 321 written scenarios. The positive qualified-acquisition branches remain explicit additional software and qualification work.

The [CI evidence ledger](verification/ci-evidence.md) records actual iOS/firmware compilation and PostgreSQL execution. At service checkpoint `cf5df00`, all 168 PostgreSQL tests passed, including competing report revisions, with two migration replays and least-privilege checks. Actual LocalStack, AWS QA, production, store distribution and physical-phone evidence remain open.
