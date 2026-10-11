# Engineering design — production mobile platform

## 1. Context and scope

This is the detailed software design for the 20 feature specifications in this change. Upstream sources are [HLD](../../../specs/HLD.md), [LLD](../../../specs/LLD.md), [PRD](../../../specs/PRD.md), and [full specification](../../../specs/FULL_SPECIFICATION.md). The user's current instruction makes LocalStack, AWS QA, and AWS production required deployment targets. This supersedes the HLD's earlier optional-AWS wording without changing its scientific boundaries.

Production grade is an engineering target: authenticated access, repeatable deployment, reliable state transitions, encryption, recovery, instrumentation, and verified behavior. No software deployment closes the assay, optics, human-contact electronics, clinical-study, or model-validation gates. The release is a measurement platform; all inference remains disabled until a separate reviewed change supplies actual qualification evidence and executable model artifacts.

The [shared application contracts](shared-contracts.md) and [platform contracts](platform-contract.md) are normative parts of this design and resolve the independent adversarial findings. They define exact generation/revocation, companion evidence, device proof, error/job states, object versions, export delivery, worker leases, and restore contracts. The current release fixes inference_available=false.

## 2. Implementation architecture

| Concern | Implementation | Why |
|---|---|---|
| Android/iOS interface | Expo SDK 57.0.27 with SDK-compatible React Native 0.86/React 19.2.3, TypeScript | Shared feature behavior with native platform capabilities; dependency versions frozen in lockfiles. |
| Timing-critical task | Local Expo module, Kotlin on Android and Swift on iOS | Native monotonic event timestamps and native view presentation callbacks. Frame callbacks remain uncalibrated evidence until device testing. |
| Local storage | SQLCipher through expo-sqlite; encryption key in OS secure storage | Persist profile, attempts, results, and outbox without writing plaintext health records. Web preview uses memory only. |
| Mobile identity | OAuth authorization code with PKCE through the system browser | Public client has no bundled client secret; Cognito identity is distinct from study authorization. |
| HTTP service | Python FastAPI modular monolith, Pydantic boundary validation | Explicit modules for identity, profile, sessions, artifacts, studies, privacy, and configuration. |
| Structured persistence | PostgreSQL, SQLAlchemy, migration scripts | Transactions, row locks, immutable snapshots, unique constraints, and transactional outbox. |
| Background work | Separate worker process using SQS and a database outbox | Durable asynchronous result and privacy processing with retry and dead-letter handling. |
| Raw artifacts/exports | Private versioned S3 objects, PUT-only quarantine tickets, and authenticated API export delivery | Object bytes are separated from structured metadata; verification precedes use. |
| Local AWS | LocalStack for S3/SQS, real PostgreSQL container, API/worker containers, isolated local OAuth issuer | Exercise application AWS APIs locally without pretending to emulate every managed service. |
| QA/prod AWS | ECS Fargate API/worker, ALB/TLS, RDS PostgreSQL, S3, SQS/DLQ, Cognito, Secrets Manager, CloudWatch | Same application images with environment-specific configuration and separate data/identity. |
| Infrastructure | AWS CDK TypeScript synthesized to CloudFormation | Typed infrastructure plus inspectable templates and repeatable per-environment deployment. |

The local OAuth issuer is a development adapter. It issues signed tokens only for named fictional accounts, implements code/PKCE/replay checks, and is excluded from QA/prod deployments. LocalStack is not asserted to reproduce Cognito, RDS failover, IAM enforcement, or Fargate scheduling. QA acceptance covers those differences.

## 3. Environments and immutable promotion

Environment identifiers are exactly local, qa, prod, and test. A native build fixes its environment, application/bundle ID, API origin, OAuth issuer/client ID, and permitted redirect URI. The production UI cannot edit the API origin or switch to local authentication. QA has a visible QA badge and a separate app ID; local has a development badge. Demo mode is a data mode within a build, not an environment or an authentication bypass.

Local Compose binds services to loopback by default. Physical-phone LAN testing uses an explicit development override and a documented host address. API and presigned-S3 public addresses must be configured before signing; the app must never rewrite a signed URL's host. Android-emulator host routing and iOS-simulator localhost routing receive separate examples. Cloud endpoint overrides and development credentials cause QA/prod startup to fail.

QA and prod use separate AWS accounts by default; separate stacks and roles are still mandatory if an operator deliberately uses one account. Terraform state is not used; CloudFormation stack identity and CDK bootstrap roles are environment-specific. Builds produce immutable application images. Promotion references the already-tested ECR image digest, never a mutable latest tag. Database migrations run as a bounded one-off task before service rollout. Destructive migrations require an explicit compatibility plan; normal releases use expand/contract changes.

Production infrastructure defaults include private API/worker tasks and database, TLS at the ALB, encrypted database/storage/queues/logs, backup retention, deletion protection, Multi-AZ database, two API tasks across availability zones, and alerts for unhealthy targets, elevated errors, failed jobs, and queue age. QA reduces capacity but preserves authentication and network boundaries. Actual account IDs, certificate ARN, DNS domain, notification destination, and signing credentials are deployment inputs; examples must not imply they have been provisioned.

## 4. Identity and authorization

The mobile application uses PKCE S256, cryptographically random state/verifier, an exact configured callback, and the system browser. The app validates the returned state, consumes each flow once, exchanges the code without a client secret, and stores refresh credentials only in OS secure storage. Access tokens stay in memory where practicable. A refresh operation is single-flight; a failed refresh pauses synchronization and preserves encrypted pending work.

The backend accepts only signed RS256 access tokens from the configured issuer, verifies exp/nbf/issuer and configured client_id, requires token_use=access and token-family claims, restricts algorithms, and resolves keys from the configured issuer's JWKS endpoint. The local issuer emits the same claim shape. Every protected request also checks current application account state, deleted-subject tombstones, and application origin_jti-family revocation; JWT signature/expiry alone is insufficient. Token headers cannot supply an arbitrary JWKS URL. Caches are bounded and unknown keys trigger one controlled refresh. A valid ID token is not an API credential. Development tokens are rejected in QA/prod.

Every row operation derives owner identity from the verified subject; no body field may assign ownership or a research role. Participant access is limited to the participant's own records. Researcher/import roles are trusted identity groups plus current database study membership. Registry administration and device provisioning are operator commands, not participant endpoints. A study ID, consent checkbox, positive assay result, or manifest string alone grants no role.

## 5. Shared endpoint contracts

Existing session/artifact/model routes in contracts/openapi.yaml remain the initial exchange boundary. The implementation adds the following feature operations. The generated service OpenAPI and tested DTOs must agree with this table.

| Operation | Behavior |
|---|---|
| GET /health/live | Process liveness only; no secrets or database details. |
| GET /health/ready | Required dependency readiness; 503 until migrations/config/database are usable. |
| GET /v1/app-config | Public environment, supported app/contract versions, maintenance state, current notice version/hash, and feature availability without private study data. |
| GET/PATCH /v1/me/profile | Current profile + ETag; PATCH with If-Match creates a new immutable revision. First empty profile has ETag "0". |
| POST /v1/me/acknowledgments | Persist current application-notice acknowledgment, client time, and server receipt time; never research consent. |
| GET /v1/me/capabilities | Owner-scoped capture/upload availability, blocking reasons, qualified configuration IDs/hashes, scope, and expiry. |
| GET /v1/me/studies | Current participant memberships and approved protocol availability. |
| POST /v1/studies/{study_id}/consents | Record explicit consent version for an already authorized enrollment; does not enroll an arbitrary account. |
| POST /v1/studies/{study_id}/withdrawals | Revoke future study access and start policy-governed data processing. |
| POST /v1/device-bindings/challenges | Create a one-time owner/device challenge with five-minute expiry. |
| POST /v1/device-bindings | Verify device proof against an operator-provisioned registry and bind to the authenticated owner. |
| DELETE /v1/device-bindings/{binding_id} | Revoke an owned binding; does not delete past measurement evidence. |
| GET /v1/sessions | Owner-scoped cursor pagination; bounded page size 1–100, default 20. |
| GET /v1/sessions/{session_id} | Authorized metadata, frozen snapshot when present, and latest linked result. |
| POST /v1/privacy/exports | Create an idempotent owner export job; raw artifacts excluded by default. |
| POST /v1/privacy/deletion-requests | Explicit scope all_data or account plus confirmation; create a durable job. |
| GET /v1/privacy/jobs/{job_id} | Owner-scoped typed job state and authenticated gateway path when ready. |
| GET /v1/privacy/jobs/{job_id}/download | Current owner/generation/policy check before streaming a version-pinned export; no S3 bearer GET. |
| GET /v1/notices/{version} | Bounded plain-text versioned notice with exact UTF-8 SHA-256. |
| POST /v1/auth/logout | Application revocation of the current origin_jti token family; minimal idempotent receipt. |
| POST /v1/me/data-generation/acknowledgments | Explicitly activate a new empty generation after all-data deletion completes. |
| GET /v1/device-bindings | Current owned bindings with public trust-key versions. |
| PUT /v1/sessions/{id}/context | Immutable versioned companion context with exact profile/history hashes. |
| PUT /v1/sessions/{id}/attempts/{attempt_id} | Preserve started/terminal attempts and full bounded typed evidence. |
| PUT /v1/sessions/{id}/evidence-manifest | Freeze context/attempt hashes and selected projection references. |
| GET /v1/sessions/{id}/evidence | Owned companion evidence, explicitly excluding unauthorized raw media. |
| POST /v1/sessions/{id}/capture-authorizations | Fresh online, one-use qualified-start authorization; absent real qualification remains unavailable. |
| POST /v1/sessions/{id}/capture-authorizations/{authorization_id}/start | Atomically consume an unexpired online start authorization for the named attempt/boot. |
| POST /v1/sessions/{id}/attestations | Verify signed normalized capture evidence against exact scope/value mapping. |
| GET/POST /v1/sessions/{id}/alcohol | Separate versioned mg/L record selected before finalization; immutable afterward. |

All protected writes require Idempotency-Key and X-Data-Generation. Mutable resources require If-Match: 428 means missing, 412 stale; 409 is a state/idempotency conflict and 410 is a retired generation. The shared contracts define the minimal accepted-deletion-receipt replay exception and privacy escape paths from a stale notice gate. Limits: JSON request body at most 1 MiB, validated bounded string lengths and list sizes, and no arbitrary nested custom objects. Correlation IDs are random server-issued values; errors use code/message/request_id/retryable. Authorization failures disclose no other owner's resource existence.

## 6. Record and consistency model

Session acquisition snapshots continue to use the v0.1 JSON contracts. Application-only draft state has its own versioned local record and cannot masquerade as a finalized snapshot. Profile inputs use cm/kg, age in completed years, source/date, and explicit null/unknown/declined values. Optional UI guardrails cap entered height at 300 cm and weight at 500 kg; these are typo checks, not model cohort definitions. Use frequency follows the existing enum never/occasional/frequent/daily/unknown/declined.

Canonical snapshot hashing resolves the earlier cross-language open decision: use RFC 8785 JCS over the validated JSON value, UTF-8, then SHA-256. Reject NaN/infinity, duplicate JSON keys, integers outside the interoperable safe range, and invalid Unicode. Freeze the canonicalization version in the service/app contract. Decimal values remain JSON numbers without display-rounding before hashing. Test the same fixtures in Python and TypeScript.

Tables include accounts with data generation/state, revoked_token_families, profile_revisions, acknowledgments, study_memberships/consents, device_registry/bindings/challenges/attestations, sessions/revisions, capture_contexts/attempts/evidence_manifests, alcohol_records, results, artifact_requests, privacy_jobs, idempotency_records, outbox_events, audit_events, and deletion_tombstones/journal_watermarks. Version 1.0.0 companion records preserve full attempt/context/native evidence while the v0.1 snapshot remains its selected scientific projection. Identifiers are UUIDs except authenticated opaque subject strings; owner columns and foreign keys are required. Query authorization precedes record serialization and artifact access.

Session registration is unique by session UUID and owner. PUT snapshot accepts only the current revision and validated selected component references. Finalize locks account and session rows, verifies current generation/authority and submitted snapshot plus companion evidence digests, freezes both, stores an audit event, and inserts one outbox event in a transaction. Identical retries return the original response. Reusing the same idempotency key with changed content returns 409. A second finalize with the same snapshot/evidence hashes returns the existing job/result; a different hash returns 409. Post-finalization reacquisition uses Start replacement check with new UUID/target time, supersedes reference, and no prior physical components. Administrative report correction remains a separate authorized workflow.

The outbox dispatcher sends pending event IDs to SQS. It may send duplicates after a crash; consumers acquire the corresponding row and check a unique processing key. Results are committed before the message is acknowledged. A worker crash cannot create two final results for one snapshot/model/feature combination. Failed work has five receives before DLQ; 120-second fenced database leases/visibility and 30-second heartbeats permit crash recovery and reject stale-worker commits. Operator replay retains the original job identity. Deletion/export jobs store recoverable completed-step metadata. Database polling is only a test/local fallback when explicitly selected, not an automatic response to a cloud outage.

## 7. Device and scientific capability boundaries

The HLD's unprovisioned BLE path remains synthetic only. Device association is separate from trust. Approved device registry entries contain a P-256 public key, hardware/firmware scope, and status. The shared contracts freeze domain-separated JCS challenge/capture envelopes, P-256 SPKI public keys, ECDSA/SHA-256 DER signatures, environment/owner/generation/attempt/configuration binding, exact normalized payload digest, replay checks, and atomic one-time challenge consumption. The attestation endpoint verifies that the signed normalized values equal the selected snapshot evidence. No endpoint lets a participant upload an arbitrary trusted public key. Revocation prevents new captures/uploads from using that binding.

Frame CRC establishes integrity against accidental corruption, not device authenticity. Human-capture telemetry must also be signed and bound to session ID, boot ID, monotonic sequence, and qualified configuration. Qualified human capture requires a fresh online server authorization per start in this release. Cached capability data is explanatory only; wall-clock rollback or restart cannot enable qualified offline capture. Native uncalibrated practice and synthetic acquisition work offline. Withdrawal intent stops local dependent work immediately, and server acceptance blocks later artifact verification/finalization. The synthetic starter requires none of these credentials because it is explicitly synthetic.

Capability responses default to unavailable for qualified saliva hardware, optical features/stimulus, body-connected ECG, alcohol, and inference. The software implements the disabled state, reasons, configuration lookup, and authorization checks. Operator-supplied qualification records can enable only the named scope; an environment variable or mobile switch cannot supply scientific evidence. No trained clinical model or final cartridge calibration exists in this change.

## 8. Storage, uploads, exports, and deletion

Mobile data is encrypted with per-account/environment SQLCipher keys stored using Keychain/Keystore-backed secure storage. Current account views require OS device-credential/biometric unlock; retained signed-out caches require the same issuer/subject to reauthenticate before access. Persist only bounded metadata and authorized records; raw camera/ECG recordings require a separate approved retention configuration. Key loss fails closed and offers explicit local reset. Logout defaults to retaining a locked encrypted cache and removing credentials, with explicit scoped removal as the alternative and a second count-specific choice before unsynced deletion. Online logout revokes the current application token family; offline logout says remote revocation was not confirmed. It never uploads or exposes another account's data. Demo records have a separate namespace. Web preview keeps all records in memory.

S3 buckets block public access. Ticket creation verifies owner, active study consent where needed, allowed media type, declared size, digest, and retention policy. Upload tickets expire after five minutes and sign exact byte/media/checksum headers plus mandatory If-None-Match:*, enforced by bucket policy. S3 412 reconciles the existing upload. Quarantine cleanup respects the ticket expiry/known-active-write boundary and cannot reopen conditional replay. Completion pins the quarantine object VersionId, streams exactly that version with a hard size bound, verifies SHA-256/length/media signature, and rechecks generation/policy before acceptance. Every later read uses the verified VersionId; a reused conditional PUT ticket cannot overwrite its current quarantine object or modify accepted evidence; all downstream reads remain version-pinned. A caller-supplied metadata hash is not proof of content. Unverified objects cannot enter features or exports. Stale incomplete uploads are lifecycle-cleaned.

Exports are asynchronous owner requests with fixed single/selected/all scope, at most 500 checks and 50 MiB structured data. A job snapshots authorized selection, writes a manifest plus JSON archive, records its hash/VersionId, and exposes an authenticated same-origin gateway download path with freshness metadata at most five minutes. The gateway checks current owner/generation/policy at stream authorization; copied paths confer no authority. Already-authorized bytes cannot be recalled. Exports logically expire after 24 hours and S3 cleanup is asynchronous. The user-facing export notice explains that a shared copy leaves app access control. Local exports also require an explicit share action and remove temporary files after completion/cancelation.

Data deletion uses durable jobs and tombstones so a retry, stale outbox, or backup restore cannot resurrect erased records. All-data deletion removes app-owned profile/session data except a specifically authorized retention obligation, which must be disclosed in job status. Account deletion additionally revokes identity access and invokes the configured identity-provider deletion operation. Study withdrawal intent stops new local work; server acceptance blocks future accepted/verified uploads. A preissued PUT may still write quarantined bytes until its five-minute expiry but cannot enter accepted evidence. Production backup retention is bounded; a separately versioned encrypted S3 deletion journal with watermarks survives database rollback. Restore reapplies all post-backup journal records and fails closed if continuity cannot be established before traffic reopens. Privacy jobs use kind=export|deletion; common states pending/running/completed/failed, export-only expired, and deletion-only partially_retained, never an unsupported claim of immediate physical removal from every backup.

## 9. Native acquisition and customer experience

The exact user journeys are defined in the feature specs. The app presents Home, Check, History, and Settings as primary navigation. Profile and Device are reachable without beginning a check. Each check has a visible current step and persistent demo/source indication. Start check freezes current confirmed profile/context and target time. Active timing capture offers immediate End task; any overlay/navigation stops it before presentation, with confirmation reserved for later discarding the broader inactive draft. A working camera preview is not labeled a pupil measurement. Missing sensor channels offer clear next actions and remain null, never zero.

The reaction module owns its clock and native input view. The app must not perform network or storage writes during each scored trial. Practice is excluded from scored features, first qualifying response wins, and interruption produces an invalid attempt whose event history remains associated with the check. Native frame callbacks and touch timestamps are retained alongside calibration status; no claim of physical photon-onset accuracy is made without bench evidence.

Accessibility covers names/roles, screen-reader order, large text, contrast, and non-color instructions. Modifications affecting the measured task cannot silently reuse the same scientifically qualified configuration. General navigation remains accessible even when a task configuration is unsupported.

## 10. Verification, review, and release

Before application implementation, all feature specs and this design receive adversarial review for contradictions, bypasses, race conditions, provenance errors, hidden customer dead ends, and environment leakage. Findings identify severity, reproducing scenario, affected requirement, correction, and final disposition. Critical/high findings must be resolved in the spec before implementation.

Verification uses TypeScript/Python unit and contract tests, cross-language canonical hash fixtures, authorization and concurrency integration tests against PostgreSQL, S3/SQS tests against LocalStack, mobile interaction tests, native build checks, CDK synthesis assertions, and release/runbook review. LocalStack checks are labeled unexecuted if Docker or an activation token is unavailable; an in-memory AWS mock is not called LocalStack validation. Native iOS compilation requires Xcode/macOS or an authorized build service; JavaScript export does not count as an iOS binary.

The delivery ledger distinguishes implemented, automatically verified, externally blocked, and not implemented per requirement. QA/prod deployment and physical-device evidence remain visible until executed. No task is checked merely because its implementation is planned. Application-store publication and paid infrastructure creation are separate operator deployment actions.

## 11. Primary implementation references

- [OpenSpec official framework](https://github.com/Fission-AI/OpenSpec) and [CLI reference](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md).
- [Expo SDK](https://docs.expo.dev/versions/latest/), [local native modules](https://docs.expo.dev/modules/get-started/), [SQLite/SQLCipher](https://docs.expo.dev/versions/latest/sdk/sqlite/), [SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/), and [Camera](https://docs.expo.dev/versions/latest/sdk/camera/).
- [LocalStack installation and activation](https://docs.localstack.cloud/aws/getting-started/installation/), [S3](https://docs.localstack.cloud/aws/services/s3/), and [SQS](https://docs.localstack.cloud/aws/services/sqs/).
- [Cognito access-token semantics](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html) and [ECS overview](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html).
- [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785).
