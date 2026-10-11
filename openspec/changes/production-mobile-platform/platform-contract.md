# Platform contract — durable jobs, storage, recovery, and environments

This is a normative engineering extension to [design.md](design.md), [shared-contracts.md](shared-contracts.md), and the 20 feature specifications. It closes the implementation ambiguity identified by the independent platform review. The shared contract owns identity, revocation, data generations, HTTP/job vocabulary, evidence DTOs, and authenticated export admission; this document owns their durable infrastructure behavior. Engineering defaults below are capacity/security settings, not clinical tolerances or achieved performance measurements.

The initial release has no executable impairment model and no preapproved human capture configuration. Infrastructure startup must not manufacture either. Real data-policy and deployment inputs are required where stated.

## 1. Environment and deployment inputs

Environment identifiers are `local`, `qa`, `prod`, and `test`. Local/test credentials and endpoints must be rejected by QA/prod startup. Cloud application images are promoted by immutable image digest; mobile identities and service configuration remain environment-specific.

| Setting | Local | QA | Production |
|---|---|---|---|
| Application services | Docker Compose API, worker/dispatcher, PostgreSQL, signed local identity | ECS Fargate API and worker/dispatcher | Same application images on ECS Fargate |
| AWS service implementation | Actual LocalStack S3/SQS | Actual AWS S3/SQS | Actual AWS S3/SQS |
| Data/identity isolation | Fictional local identities and separate named volumes | Separate AWS account preferred; mandatory separate stacks, buckets, keys, pools, secrets | Separate production account preferred; no QA/local identity or data |
| Default cloud region | Not an AWS deployment | `us-east-2`, override recorded in deployment manifest | `us-east-2`, override recorded in deployment manifest |
| Database | PostgreSQL 16 family, image digest pinned after integration verification | Managed PostgreSQL 16 family, supported exact minor recorded | Same supported major and compatible migration level |
| Database backups | Explicit disposable-development behavior | Seven-day automated retention | 35-day automated/PITR retention; older manual snapshots prohibited by this policy |
| TLS | Loopback development HTTP; explicit LAN override for phones | Required at ALB | Required at ALB |
| Availability | No production SLO | Reduced-capacity verification target | Two API tasks across two availability zones, Multi-AZ database |

The implementation must resolve and commit exact LocalStack/PostgreSQL image digests and package lockfiles. A moving `latest` tag is not reproducibility evidence. Managed database minor changes must be recorded with compatibility checks, whether applied through a reviewed upgrade or a configured maintenance policy.

Cloud synthesis requires concrete account, region, environment, VPC CIDR, application domain, certificate ARN, Cognito domain/client/callbacks, database sizing, image digest, budget amount, and alarm destination configuration. Deployment examples may contain clearly named placeholders; deployment automation rejects unresolved placeholders. Notification resources are configured only from the operator's supplied destination. No message or subscription confirmation is sent as part of writing these files.

## 2. LocalStack startup and phone connectivity

Compose must include API, worker/dispatcher, PostgreSQL, LocalStack, local identity, and separate idempotent resource-init/migration commands. Services start only after their required dependency health checks. Initialization creates the three versioned buckets and the source queue/DLQ with the same relevant limits as cloud. Repeating initialization must not clear data or create duplicate logical resources. Ordinary shutdown preserves volumes; destructive volume cleanup has an explicitly named command and warning.

Local secrets, database passwords and signing keys come from ignored files/environment inputs. The default compatibility environment uses the digest-pinned Apache-licensed LocalStack 4.14.0 release for S3/SQS. A separately selected licensed release requires its genuine activation token through the same protected inputs. Neither choice may skip the actual service checks or relax their assertions. The local issuer serves only the named fictional development accounts, including a fixed bounded set of performance identities. Its JWKS and token semantics match the shared access-token contract, but its issuer/client/key material cannot authenticate in QA/prod. Test-only identities remain distinct from LocalStack service credentials.

By default every published local port binds `127.0.0.1`. Physical-phone development uses a deliberate LAN override and a trusted development network. Internal container endpoints and externally reachable phone endpoints are different configuration values. The API's local S3 signer must sign against the configured public LocalStack origin; neither app nor API rewrites a URL host after signing. The identity issuer and registered callback must likewise match the phone-reachable configuration.

The quick start must provide separate examples for Android emulator host routing, iOS simulator routing, and physical Android/iPhone LAN routing. Android cleartext exceptions and iOS transport exceptions, where necessary, must be development-only and limited to the documented hosts. Production manifests must not contain broad cleartext/transport exceptions.

Local integration must exercise an actual S3 versioned upload, verification of that version, SQS dispatch/receive/delete, a persisted API result, an export download through the authenticated API, and deletion generation enforcement. Missing Docker, an invalid activation token, or unsupported LocalStack behavior is a failed/unexecuted integration prerequisite. Unit mocks remain useful but are reported separately. IAM, network isolation, Cognito hosted login, RDS recovery, and real managed-service behavior require QA evidence.

## 3. Capacity, network paths, and deployment lifecycle

Initial engineering defaults:

| Resource | QA | Production |
|---|---|---|
| API task | 0.25 vCPU, 512 MiB; desired/max 1 | 0.5 vCPU, 1024 MiB; desired 2, autoscaling max 4 |
| Worker task | 0.5 vCPU, 1024 MiB; desired/max 1 | 0.5 vCPU, 1024 MiB; desired 1, autoscaling max 2 |
| Worker job concurrency | At most 2 per task | At most 2 per task |
| API processes/pool | One process; pool 5, overflow 0 | Same |
| Worker database pool | Pool 3, overflow 0 per task | Same |
| Pool acquisition timeout | 5 seconds, then a retryable service error | Same |
| Planned DB connection budget | 40, including rollout/migration/operator reserve | 80, including rollout/migration/operator reserve |
| Candidate database size | `db.t4g.small`, single AZ | `db.t4g.medium`, Multi-AZ |
| Network | One QA NAT gateway; S3 gateway endpoint | NAT gateway in each of two active AZs; S3 gateway endpoint |
| Task rollout maximum | 200% of desired task count | 200% of desired task count |

These are starting configurations for load and cost verification. The selected region/engine must support the instance class before deployment. Record actual database `max_connections`; it must exceed the declared budget. Never increase task/process/pool counts without recalculating simultaneous connections during a maximum-capacity rolling deployment, including the migration job and at least ten reserved administrative connections.

ALB resides in public subnets. API and worker tasks have no public IP; the database resides in isolated/private database subnets. Security groups permit the ALB to reach only the API port and app/migration roles to reach only the database port. No internet-originated database access or SSH ingress is configured. Tasks use the explicit NAT/endpoint routes for image retrieval, Secrets Manager, CloudWatch, SQS, S3, and the allowlisted Cognito/JWKS endpoints. An ALB health check cannot substitute for verifying those outbound operations. [AWS ECS networking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/networking-outbound.html)

Use separate ECS execution and application task roles. The execution role retrieves images/secrets and writes required container logs. The API role signs only owned artifact-quarantine uploads, verifies approved object versions, reads authorized export versions, and writes/reads specific deletion-journal events. The worker role receives/deletes/extends source-queue messages, dispatches durable outbox events, manages permitted artifact/export objects, performs deletion steps, and invokes only the necessary configured identity-provider removal operation. Neither runtime role can delete journal events or disable bucket protections. A restore/audit role can enumerate/read the journal and perform recovery; it is not a participant API capability. IAM actions requiring wildcard resource scope must be individually justified rather than covered by broad administrator policies.

Migrations run once as a bounded one-off ECS task under a separate migration credential and database advisory lock. A failed migration blocks rollout. Releases use expand/contract migrations; the rollback target must remain compatible with the resulting schema. Readiness validates configuration, schema migration level, and required durable dependencies; it returns 503 while unusable. Liveness reports only the running process.

API SIGTERM stops admitting new work, drains accepted bounded requests, and releases resources. Worker SIGTERM stops new claims and either commits current work within its stop window or lets the lease expire without acknowledging uncommitted work. Secret rotation requires refresh/redeployment evidence; environment-injected secrets are not assumed to change inside an already running container. Promotion records tested image digest, migration version, infrastructure version, environment, and rollback task definition.

## 4. Mandatory bounds and rate controls

All sizes below count bytes. `MiB = 1,048,576` bytes; `GiB = 1,073,741,824` bytes. Approved policies may lower these bounds. Raising a bound requires a reviewed configuration and updated memory/storage/load evidence. Missing or nonpositive required bounds cause startup failure in QA/prod.

| Operation/resource | Default hard bound |
|---|---:|
| API JSON request | 1 MiB |
| Structured context/attempt record | 512 KiB, plus the stricter shared DTO field limits |
| Selected export records | 500 unique checks |
| Structured export uncompressed bytes | 50 MiB |
| Structured export ZIP object | 64 MiB, including archive overhead |
| Authorized eye video artifact | 64 MiB per object |
| Authorized ECG waveform artifact | 16 MiB per object |
| Authorized source laboratory report | 8 MiB per object |
| PPG waveform if added to the supported artifact enum | 16 MiB; otherwise reject the unsupported kind |
| Future explicitly authorized raw export | 256 MiB uncompressed / 320 MiB ZIP, and the same selection bound |
| Open upload tickets per account/generation | 3 |
| Reserved unverified upload bytes per account | 128 MiB |
| Retained raw object bytes per account | 1 GiB, subject to the lower approved data policy |
| Active export jobs per account | 1 |
| Accepted export creations per account per 24 hours | 5; identical idempotent replays do not create another job |
| Account metadata reads | 120/minute, burst 40 |
| Ordinary account mutations | 60/minute, burst 20 |
| API concurrent admitted requests | 100 per task |

The current raw-export capability remains unavailable without actual approved scope. The larger limits above do not authorize capture or retention. The structured export limits and selection semantics are exactly those in the shared contract. A single-check export cannot silently widen into all account data or omit overflowing evidence.

Quota reservations are transactionally associated with the account generation and upload/job. Reservations are released after verification accounting, rejection, expiry, or deletion. Deleted/expired byte accounting is not released merely because cleanup was requested. Server counters must work across multiple API tasks; an in-memory-only per-process limiter cannot enforce the account limits. Privacy deletion/status and withdrawal must retain a bounded operational path even when ordinary storage/export quota is exhausted. Replays of an accepted deletion receipt are not blocked by an exhausted export quota.

Reject oversized JSON/record bodies before full deserialization and before expensive work. Return 413 for size and 429 for rate/quota exhaustion with the shared error envelope. Retry-After is a nonnegative integer seconds with a client scheduling bound of 1–3600 seconds; a longer required wait is presented as a manual wait/retry state. Unknown quota configuration must not become unlimited storage.

## 5. Artifact upload, verification, and immutable reads

Use separate private, versioned S3 buckets for artifacts, exports, and the deletion journal. QA/prod require explicit encryption configuration, public-access blocking, TLS-only access, and no public bucket/object ACLs. The journal has an independent encryption key/policy so data-object deletion or a data-key operation cannot destroy restore evidence.

Quarantine keys are server-generated under an opaque account/generation namespace, for example `accounts/{account_ref}/generations/{generation}/artifacts/{artifact_id}/{upload_id}`. The request cannot supply an arbitrary bucket, key, URL, owner, or public ACL. All API/log/error output follows the shared redaction contract.

The upload ticket is a five-minute, SigV4 PUT for one key, exact content length, SHA-256 checksum header, declared supported media type, and the signed conditional header `If-None-Match: *`. Its required header map is exactly `Content-Length: <decimal declared bytes>`, `Content-Type: <approved media type>`, `x-amz-checksum-sha256: <base64 of the 32-byte SHA-256 digest>`, and `If-None-Match: *`, together with any explicitly returned encryption headers required by the selected bucket configuration. The checksum header is not the hexadecimal digest used in the scientific JSON. `host` is also signed using the configured public origin and supplied by the HTTP stack; the client must not rewrite it. The signed-header list must cover these constraints. No multipart client upload is issued in this release.

The quarantine bucket policy requires conditional creation for the application upload principal, so an omitted or changed conditional header cannot become an alternate overwrite path. One ticket reserves and can create at most one current object. A second successful upload is not required for recovery: an S3 412 response sends the app to completion/status reconciliation of the existing object, never to an unrestricted PUT. The server verifies the originally declared checksum and pinned version before accepting that reconciliation. Quarantine cleanup must not remove the current object or insert a delete marker before the ticket expiry plus a 60-second engineering clock margin, even after rejection or withdrawal; removing it early would permit another conditional creation under the same still-valid ticket. S3 condition semantics and bucket-policy enforcement require actual LocalStack and QA negative tests. [AWS conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html) and [conditional-write policy](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes-enforce.html)

Native clients must send the exact signed headers and body length. QA tests must demonstrate rejection of altered length/checksum/media/conditional constraints; a runtime that cannot enforce the chosen mechanism must refuse upload rather than issue an unrestricted replacement. Completion remains independently mandatory; S3 metadata submitted by the caller is not content evidence.

Completion follows this order:

1. Authenticate and verify ticket ownership, requested generation, current policy/consent, ticket state, and expected metadata.
2. HEAD the server-selected key and obtain a **non-null VersionId**. A nonversioned/null-version object is not eligible.
3. GET that exact VersionId using bounded streaming; reject before exceeding the permitted byte count. Verify actual length, SHA-256, and supported media signature/encoding, independent of client headers.
4. In a short database transaction, lock the account/ticket, recheck current generation/policy, and commit the exact bucket/key/VersionId/hash/size/media tuple as the accepted immutable artifact.
5. An identical completion replay returns that tuple's existing receipt. A different claimed body or a later uploaded version cannot replace it.

All later feature, export, copy, and download operations use the accepted VersionId. Bare-current-key reads are prohibited. Version pinning remains mandatory even with conditional creation; it protects against administrative/service races and future implementation mistakes. Reusing a ticket while its current object exists is refused, and the app reconciles that existing version. Any unexpected additional version remains inaccessible and enters investigated cleanup; it cannot replace accepted evidence. [AWS upload URL behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)

## 6. Durable outbox, SQS leases, and worker recovery

The database and SQS are at-least-once boundaries. Correctness comes from durable idempotency, short claim/finalization transactions, and fencing, not an assertion that one queue delivery happens exactly once.

Fixed defaults are **120-second SQS visibility**, **120-second database work lease**, and **30-second heartbeat**. Each source queue long-polls for 20 seconds, receives one message per available worker slot, and uses a redrive policy of **five receives** before DLQ. Source retention is four days; DLQ retention is 14 days. A logical job also has at most five failed execution claims per automatic retry cycle, so duplicate outbox messages cannot reset its retry budget. A processing attempt has a 15-minute deadline; larger work must be partitioned under an explicit continuation contract.

Each durable job stores job ID/kind, account reference, original data generation, stable event ID, internal execution state, attempt count, `lease_owner`, `lease_expires_at`, increasing `fencing_token`, next-attempt time, deadline, completed-step evidence, and immutable output references. Internal lease state does not add new public job-state strings; public status follows the shared PrivacyJob/result contracts.

1. **Dispatch:** business commit creates its outbox row in the same transaction. The dispatcher sends only stable event/job identifiers and schema version to SQS, then marks its send disposition. A crash can cause resend but cannot remove the unsent durable event. Queue bodies never contain raw health records or access tokens.
2. **Claim:** a consumer locks the job. Terminal jobs return their existing disposition; already leased work is not recomputed. An available/expired eligible job increments its fencing token and claims a 120-second lease in a short transaction. The account/generation/policy check is performed at admission.
3. **Heartbeat:** every 30 seconds, the current owner conditionally extends its database lease and SQS visibility. Loss of the database lease, token mismatch, deadline, or failed ability to maintain ownership stops publishing work. A visibility extension is not a replacement for the database fence. [AWS SQS visibility guidance](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
4. **Work:** perform bounded computation/streaming outside a long-held database transaction. External side effects use stable job/step IDs; temporary objects are isolated by job/fencing token and are not customer-visible before commit.
5. **Publish:** conditionally commit only if lease owner/fencing token are still current, the lease has not expired, and the account/data-policy check still permits the output. Store the immutable output version and audit disposition before deleting the SQS message. Deletion jobs use the specifically authorized retired generation and the journal rules below.
6. **Recover:** the dispatcher also identifies expired database leases and due outbox work and enqueues the same logical event again. It never executes jobs directly as an automatic cloud-outage fallback. This recovery scan prevents loss if a duplicate delivery was acknowledged while an original worker later died. A stale worker's final update affects zero rows and its temporary output enters cleanup.
7. **Retry or dead letter:** transient errors use 2/4/8/16/32-second delays within the logical attempt budget. Validation, unauthorized scope, stale generation, and immutable-content conflicts are permanent. Five failed claims move the job to an explicit failed disposition and an auditable dead-letter condition; queue redrive also protects against unhandled deliveries. A permitted operator replay retains the job ID, records a separate replay ID/reason, and obtains a new bounded cycle. It rechecks current authorization and cannot revive deleted data.

No SQS message is acknowledged merely because its output file was started. No replacement worker adopts another worker's unverified temporary file. Worker cancellation and shutdown must leave sufficient state for the recovery scan.

## 7. Restore-independent deletion journal

The application database contains deletion jobs/tombstones, but it is not the only deletion evidence. The separate versioned encrypted S3 journal is authoritative for post-backup deletion barriers. Runtime roles can append/read designated events but cannot overwrite accepted versions or delete the journal. Journal schema, encryption-key availability, retention, inventory, and recovery access are deployed prerequisites.

Journal events contain only version, event UUID, deletion job UUID, opaque account reference, retired/new generation, scope, policy version, server acceptance time, event type, and required barrier/completion metadata. They contain no profile, sample, biometric, token, email, or other raw record content. Every deletion acceptance event, for both `all_data` and `account`, additionally includes `subject_ref_hmac` and `hmac_key_id` so restoration can link the verified issuer/subject even if the restored database predates creation of that account. `subject_ref_hmac` is lowercase hex HMAC-SHA-256 over the UTF-8 JCS array `[configured_issuer, verified_sub]`, using a separate server-only 256-bit random identity-tombstone key held outside PostgreSQL in Secrets Manager. The journal's account UUID alone cannot supply this protection. For account deletion the restored match is permanently nonwritable under the retained tombstone policy. For all-data deletion the restored match resolves to the original opaque account reference, maximum valid generation, deletion state, and required new-workspace acknowledgment; it must never create a new account UUID at generation 1 that could accept the old outbox. Keep the required key versions throughout the lifetime of corresponding journal/restore evidence; key rotation must preserve verification of retained references. A missing required key blocks recovery/admission rather than disabling the subject check. The pseudonymous reference remains protected data under the approved receipt-retention policy. Event JSON is at most 8 KiB, canonically serialized and SHA-256 identified. Event keys are deterministic from job/event identity; conditional create prevents changed content from replacing an existing event.

### Acceptance and completion ordering

1. Under the account lock, validate the original generation and deletion request; commit the deleting state, incremented generation, durable job, and journal intent together. Data access is blocked according to the shared contract.
2. Persist the acceptance event in the independent journal, read/verify its non-null VersionId and digest, and record its receipt. The API returns the accepted **202 receipt only after both the database intent and this independent event are durable**. If journal persistence is unavailable, return a retryable 503 and retain the account barrier; the same idempotency key resumes that intent. Do not report a completed deletion or erase the durable intent to hide the failure.
3. The worker proceeds only after journal acceptance is confirmed. It deletes the specifically scoped records, every relevant artifact/export version/delete marker, temporary objects, queued payload references, and retained sensitive idempotency response bodies, while preserving only the stated policy exceptions and minimal receipts. Quarantine cleanup waits for the conditional-upload protection interval in §5; such a scheduled wait remains pending/running and does not consume a failed-execution retry. Access and evidence acceptance are already denied by the generation barrier during this wait.
4. Account deletion performs the provider-removal/revocation step as a separately evidenced idempotent operation. A failure leaves the job failed/retryable with honest completed-step metadata, not completed.
5. Persist the terminal barrier/retention disposition in the journal before publishing a terminal deletion result and new writable-generation availability. For all_data, the shared contract still requires the user's new-empty-workspace acknowledgment. No ordinary stale operation can exploit the journal handoff to write a new UUID under the old generation.

A crash between database intent and journal persistence may leave an unacknowledged pending deletion. Recovery retries the intent; it cannot infer completed status. The independent acceptance event provides a recoverable deletion instruction even if a later database restore loses the local job row. HTTP response loss is reconciled with the original key and receipt, never with another deletion scope.

### Retention and restore watermark

Journal events have an initial **90-day minimum retention**, longer than the **35-day maximum permitted database recovery-point age**. Raw event cleanup is allowed only when inventory proves that no permitted recovery point predates the event and the current generation barrier is present in later verified recovery points. If an operator retains an older snapshot, journal cleanup is suspended and the declared retention policy/exception must be reconciled. Journal retention never authorizes retaining raw health records. A deployment without an approved applicable receipt-retention policy keeps human-data capabilities unavailable.

Recovery first isolates API traffic, pauses workers/dispatchers, and prevents concurrent admissions in the recovering environment. The recovery tool lists all retained deletion-event versions, validates their schema/hash/version identities, and creates an immutable **watermark manifest** containing the sorted event IDs, accepted VersionIds/digests, count, inventory time, and digest of that set. A second enumeration must agree while writers remain paused. Deletion events, watermark manifests, and recovery-activation records occupy separate journal prefixes and versioned schemas; creating a watermark must not change the deletion-event inventory it describes. A disagreement, missing required post-backup interval, unbounded older snapshot, unavailable encryption key, or unreadable event blocks reopening.

The restored database records the applied watermark ID/digest and replays every acceptance/completion barrier relevant to the recovery point, using the maximum valid generation for each account. Journal-accepted jobs absent from the restored DB are reconstructed as blocked pending deletion work. Restore builds the keyed subject-reference lookup before any account auto-provisioning can run. A verified subject matching a reconstructed barrier resolves to its journal account reference and state, even when the backup has no original identity row; ambiguous/conflicting matches fail closed for operator reconciliation. Apply deletion/retention and identity barriers before owner records become accessible. Reconcile current object versions and existing outbox/queue work under those generations. Old queue events are not treated as new accepted data.

Post-backup token-family logout and study/device revocation are not reconstructed merely by replaying deletion events. Before reopening, recovery conditionally writes and version-verifies an independent `RecoveryActivation` record in the same protected journal bucket. Its versioned schema contains a recovery UUID, environment, verified deletion-watermark ID/digest, server UTC activation time, and integer-second `authentication_cutoff`; it contains no token or health content. The cutoff is at least the current server time and never less than an earlier retained recovery cutoff. Its receipt is committed to the restored database, and API tasks reload it before readiness. A missing/unverified activation record blocks reopening.

Every subsequent protected request requires a signed access-token `auth_time` at or after the latest recovery cutoff in addition to ordinary identity/account/family checks. Token `iat` alone is insufficient: refreshing an old family cannot bypass the new authentication requirement. The client presents a fresh hosted sign-in/reauthentication path; it does not erase its encrypted cache or claim remote completion while locked. Future restores load the maximum retained cutoff from the independent journal rather than trusting the older database value.

Recovered study memberships, consent-derived capture permissions, and device qualification/binding authority remain suspended until reconciled from independent current authoritative records under an audited operator procedure. Missing withdrawal/revocation/qualification evidence leaves the affected permission unavailable. A recovered database value, fresh account sign-in, old consent receipt, or available flag cannot by itself reactivate those scopes. This release has zero preapproved human configurations and no executable inference, so recovery never manufactures a qualified path. Suspension need not prevent the freshly authenticated owner's separately authorized history or privacy operations.

Traffic may reopen only after the restored system has the verified watermark, the required barriers are enforced, and targeted probes confirm that deleted data cannot be read or resurrected. Operators record actual achieved recovery time and data loss interval against the initial RTO four-hour/RPO 24-hour objectives. Those objectives are not achieved claims. A journal outage leaves recovery closed rather than using the old backup alone.

## 8. Logical expiry, cleanup, and exceptional retention

Export `expires_at` is creation time plus 24 hours, and the authenticated download gateway enforces it even while object bytes remain. The five-minute status freshness metadata in the shared contract never becomes a reusable bearer authority. New downloads after committed deletion/withdrawal are denied; the shared contract defines the limits of canceling an already admitted stream.

All protected metadata and export responses use `Cache-Control: private, no-store`; the gateway is excluded from any CDN/shared-cache route. Export delivery sets the fixed supported content type, `X-Content-Type-Options: nosniff`, and an attachment filename generated from the job UUID, never untrusted input. This release does not implement ranged/resumable export delivery: an authenticated, currently authorized Range request returns 416, and an unauthenticated one is rejected before any object metadata is disclosed. Conditional HTTP requests do not bypass current authorization or produce a stale cached 304 for protected export bytes. A mobile retry restarts the bounded authenticated download into a private temporary file and discards its earlier incomplete file.

Cleanup workers run at least every 15 minutes. Targets: remove expired export objects within 24 hours after logical expiry; remove abandoned quarantine objects within 24 hours after ticket expiry; abort abandoned multipart uploads within 24 hours after their permitted lifetime. These are initial operational objectives with age metrics and failure alarms. They are not promises that an S3 lifecycle rule deletes bytes at an exact instant.

The upload expiry plus 60-second margin is a minimum cleanup delay, not proof that an upload admitted before expiry has completed. Bearer expiry constrains admission and must not be presented as a guaranteed transfer deadline. Cleanup retains durable quarantined-ticket references, repeats version enumeration, and quarantines/removes a detected late arrival without enabling access or releasing unverified-byte accounting early. A deletion job awaiting known outstanding upload work cannot report physical cleanup complete from one earlier empty listing. If a stronger physical-erasure deadline is required, the upload path must first supply enforceable admission/transfer fencing; this release claims the exact generation-based acceptance/access prohibition and records the separate cleanup outcome honestly.

Versioned cleanup enumerates all applicable versions and delete markers. A current-key delete marker alone is not proof of erasure. Lifecycle configuration includes noncurrent-version cleanup as defense in depth, plus incomplete-upload cleanup where used. Lifecycle timing is asynchronous and must not govern access authorization. [AWS expiration semantics](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html)

Completed deletion means the worker verified its declared cleanup scope or reported the exact approved retention exception. `partially_retained` identifies only policy-required retained categories; failed technical cleanup remains `failed` with step evidence and retry/support. Policy exceptions identify category, policy ID, reason, and expiry/review deadline. Permanent exceptions or arbitrary indefinite fallback retention are not synthesized by software.

## 9. Observability, costs, and operator ownership

Every environment records request count/error/latency, readiness, unhealthy targets, database pool/connection pressure, oldest outbox event, SQS age/depth, expired leases, retries/DLQ messages, privacy-job age, cleanup age, and refused quota requests. Logs contain random request/job references and reason codes, never request bodies, tokens, signed upload queries, raw measurements, images, or direct identity. Audit access is separate from general application diagnostics.

Initial cloud alarm settings are: any DLQ message; oldest source message over five minutes; oldest unsent outbox event over two minutes; oldest active privacy job over 15 minutes; cleanup older than its objective; unhealthy production target count above zero for five minutes; and API 5xx rate above 5% over five minutes with at least 20 requests. Alert destinations are explicit deployment inputs. Alarm resources without verified delivery are recorded as configured, not as a staffed incident-response capability.

CloudWatch application logs default to seven-day retention in QA and 30-day retention in production. The separate approved audit/receipt policy controls its own retention. Resource tags include project, environment, owner role, and cost center. Secret rotation, device compromise/revocation, failed deletion, queue backlog, account lockout, database failure, and rollback have named runbook actions and an actual responsible operator before participant deployment.

Before cloud deployment, commit a dated cost estimate for the chosen region/resource sizes with separate QA and production totals. Include idle compute, ALB, database instances/storage/backups, both NAT hourly/data charges, S3 storage/versions/requests, SQS, logs, identity, egress, and managed key charges. Provide no-user baseline and at least 100-user/1,000-user usage cases, keeping actual usage/retention assumptions explicit. Use current official AWS pricing or a saved AWS Pricing Calculator estimate; the estimate cannot be inferred from the hardware shopping list.

The deployment input `monthly_budget_usd` must be a positive owner-supplied amount. Configure alerts at 50%, 80%, and 100% actual spend and 100% forecast spend. Alerts notify; they are not a guaranteed spending cap. No arbitrary account budget or recipient is invented. QA teardown/recreation instructions identify retained snapshots, journal, and other residual cost items; they must not remove production resources. A deployment lacking its estimate/budget/destination inputs remains unexecuted, even if its templates synthesize successfully.

## 10. Acceptance evidence and review mapping

| Evidence | Required outcome |
|---|---|
| Local bootstrap twice | Same logical buckets/queues/migrations; no data reset; actual LocalStack behavior reported. |
| Android/iOS local connection paths | Correct signer/issuer origins; no rewritten signed URL; no production cleartext override. |
| Artifact replacement race | Accepted bytes are bound to the pinned VersionId and remain unchanged through export. |
| Size/quota attack | Rejection before expensive acceptance; mandatory signed conditional PUT and bucket-policy enforcement; one object per ticket; 412 reconciles existing version; reservation cleanup; limits shared across API tasks. |
| Worker kill matrix | Before claim, after claim, after object write, after DB commit, before queue delete; no lost job or duplicate published result. |
| Lease expiry/stale worker | New fence rejects old commits; recovery requeues with the same logical job identity. |
| DLQ/replay | Five-failure budget is enforced; authorized replay does not reset deletion or source authority. |
| Export revocation/expiry | Current-owner admission, immutable version, explicit stream limit, and exact logical expiry. |
| Versioned deletion | All relevant object versions/markers cleaned or a precise retained category reported. |
| Journal acknowledgment loss | Retry resumes the same deletion intent; 202 requires independent journal durability. |
| Old-backup recovery | Post-backup deletions replay through a verified watermark before access; journal failure keeps recovery closed. |
| QA dependency/network test | Actual image/secret/log/S3/SQS/JWKS paths work through the intended private network. |
| Rollout/rotation | Connection budget maintained; migration failure blocks; drain/lease shutdown and secret refresh work. |
| Cost/runbook evidence | Dated per-environment estimate, configured budgets/tags/retention, named owner, and verified alarm delivery when deployed. |

Review mapping: OPS-001 is resolved by shared-contracts §7 plus this document §§5/8; OPS-002 by §7; OPS-003 by §6; OPS-004 by §5; OPS-005 by §8; OPS-006 by §4; OPS-007 by §§1–3; OPS-008 by shared-contracts §§3–8 and generated contract checks; OPS-009 by §9. These are proposed **specification corrections**. Re-review and implementation tests must establish closure; this mapping alone does not mark a finding or deployment verified.
