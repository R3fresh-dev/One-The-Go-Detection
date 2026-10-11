# Independent adversarial review — platform and operations

**Review date:** October 10, 2026, America/Chicago.  
**Reviewer:** independent platform/operations agent.  
**Reviewed scope:** all 20 feature specifications, proposal, design, task plan, and relevant HLD/LLD/PRD, full-specification, and exchange-contract dependencies.  
**Review boundary:** specification review before application implementation; no deployed AWS system or native application was tested.  
**Disposition at issue:** **Changes required.** High findings must be resolved in the specification and re-reviewed before implementation. Medium findings need an explicit correction or a documented release disposition.

The OPS-001–OPS-009 identifiers below are **review finding IDs within this document**, not the similarly named upstream operational requirements in FULL_SPECIFICATION.md. Each finding's status starts Open. Other independent reviews may describe the same defect; closure may reference one shared corrective change, but should retain each review's disposition.

## Review method and overall assessment

The architecture provides a coherent starting point: a modular API, PostgreSQL transactions, a durable outbox, SQS, private S3, separate local/QA/production identities, native mobile timing, and explicitly unavailable scientific capabilities. The review traced complete checks and privacy operations through network failures, duplicate delivery, user changes, deletion, worker termination, artifact replacement, and backup restoration.

The remaining material weaknesses are predominantly operational contracts. A specification can require idempotency or deletion without yet defining enough durable state to implement those guarantees. In particular, queue visibility is not a database work lease, an old database backup cannot contain newer deletion receipts, and a presigned object URL does not authenticate the current application user.

## Findings

### OPS-001 — Download URLs conflict with current-owner authorization

- **Severity:** High. **Status:** Open.
- **Sources:** [design §8](../design.md), [export engineering contract and AND-EXP-002/004/005](../specs/android-data-export/spec.md), [study AND-STUDY-005](../specs/android-study-enrollment/spec.md).
- **Failure:** The design returns a five-minute S3 download URL while the feature requires authorization of every download and prevention of delivery after permission changes. A user requests a raw-data export, obtains its URL, then withdraws. The URL can still deliver bytes without consulting application membership or the deletion generation. Anyone possessing it can also download without the owner's application token. AWS describes presigned URLs as bearer credentials; expiration is checked when a request starts, and an already started transfer may continue beyond that time. [AWS presigned URL behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- **Required correction:** Choose one authoritative delivery contract. For the stronger stated guarantee, provide an authenticated API download route, recheck owner/job/consent/deletion generation and logical expiry immediately before reading, stream only the immutable version, and expose no S3 bearer URL to the client. Define whether revocation cancels an already running stream or applies at request admission; do not promise recovery of bytes already shared. Set private/no-store response caching and define bounded range/resume behavior if supported.
- **Closure evidence:** An unauthenticated URL copy fails; another owner's token fails; withdrawal/deletion after job completion blocks a newly requested download; the declared in-flight behavior has a race test. Generated DTOs and the export UI use the same contract.

### OPS-002 — Restoring the database can also erase the deletion evidence

- **Severity:** High. **Status:** Open.
- **Sources:** [design §§6/8](../design.md), [AND-ENV-006](../specs/android-app-environment/spec.md), [AND-PRIV-005](../specs/android-privacy-controls/spec.md), upstream SEC-005/OPS-006.
- **Failure:** A backup is taken at 01:00. An all-data deletion and its tombstone commit at 02:00. At 03:00 the database is lost and the 01:00 backup is restored. The stated deletion_tombstones table is part of that older database, so the receipt needed by the restore procedure is absent. Simply instructing operators to replay tombstones does not identify a surviving source or prove its completeness.
- **Required correction:** Specify a deletion journal independent of the database recovery point, its minimal retained fields, retention/access policy, durability acknowledgment, and ordered watermark. Define the transaction/outbox handoff and the condition under which deletion is reported completed. Restoration must reconcile the recovered database against the authoritative journal through a known safe watermark before reopening traffic; unavailable or unverifiable evidence leaves the service closed. Define treatment of issuer-account deletion and fresh account data generations as part of the same barrier.
- **Closure evidence:** Restore a deliberately older database after later deletion events; demonstrate that deleted objects/records cannot be read or recreated by old queued writes. Kill the process between database receipt and journal persistence and show the operation cannot incorrectly reach completed. Journal unavailability must stop restore admission.

### OPS-003 — Worker crashes lack an explicit recoverable work lease

- **Severity:** High. **Status:** Open.
- **Sources:** [design §6](../design.md), [AND-EXP-006](../specs/android-data-export/spec.md), [AND-PRIV-004](../specs/android-privacy-controls/spec.md), [AND-ENV-006](../specs/android-app-environment/spec.md), upstream OPS-002/006.
- **Failure:** An export worker changes a job to running and dies before final commit. A replacement receives the same SQS event. The spec does not define when it can reclaim the running job, how it distinguishes a slow worker from a dead worker, or how an old worker is prevented from publishing after a replacement takes ownership. Holding a database transaction for the entire export would also create avoidable lock and connection pressure. SQS may redeliver, and its visibility timer alone does not fence database or S3 side effects. [AWS SQS visibility and heartbeat guidance](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- **Required correction:** Define a durable lease owner, lease expiry, attempt number/fencing token, bounded job deadline, heartbeat interval, and reclamation policy. Claim and final commits must use short conditional transactions. Extend SQS visibility while current work is healthy; check the fencing token and deletion generation before publishing side effects. Make external S3/identity operations idempotent, specify retryable/permanent errors, queue retention, max receives, DLQ replay, and orderly task shutdown.
- **Closure evidence:** Kill workers before claim, after claim, after object creation, after database commit, and before SQS deletion. A stalled worker can be replaced; a stale worker cannot publish; the same job eventually has one terminal disposition; poison jobs reach the DLQ without uncontrolled retries.

### OPS-004 — Immutable artifact verification needs an exact object version

- **Severity:** High. **Status:** Open.
- **Sources:** [design §8](../design.md), [artifact routes](../../../../contracts/openapi.yaml), [AND-EYE-006](../specs/android-eye-capture/spec.md), [AND-ECG-007](../specs/android-ecg-capture/spec.md), [AND-EXP-006](../specs/android-data-export/spec.md).
- **Failure:** The upload ticket can be reused before expiry. Completion verifies bytes under an object key, then the client uploads another object to that key. A later key-only read can obtain different bytes from those accepted. A HEAD/GET race can similarly associate the hash of one version with the ID of another. Merely recording an immutable version after verification does not establish that the bytes checked were that version. [AWS reusable upload URL and replacement behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- **Required correction:** Require S3 versioning and pin the exact VersionId before any verification GET, or move verified bytes to a new server-only immutable destination under an equally explicit scheme. All later extraction/export reads must identify the accepted version. Completion must recheck current consent and deletion generation before commit. Subsequent uploads remain quarantined and cannot replace the accepted artifact. Define expiration and cleanup of unreferenced versions.
- **Closure evidence:** Replace the key before, during, and after completion. Either the exact original accepted version remains readable and hash-correct or completion fails; no alternative version may enter a finalized input or export. Assert required bucket/version and role behavior in infrastructure tests.

### OPS-005 — Logical expiration and physical object cleanup are conflated

- **Severity:** Medium. **Status:** Open.
- **Sources:** [design §8](../design.md), [AND-EXP-005](../specs/android-data-export/spec.md), [AND-PRIV-004/006](../specs/android-privacy-controls/spec.md), upstream SEC-005.
- **Failure:** The spec says export objects expire after 24 hours without distinguishing an application access deadline from physical deletion. An S3 lifecycle rule is asynchronous. On a versioned bucket, current-version expiration normally adds a delete marker and does not remove older versions. A job that deletes only the current key can leave the exact immutable version used by an export recoverable. [AWS lifecycle expiration semantics](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html)
- **Required correction:** Enforce the exact 24-hour logical access deadline in the application, independently of lifecycle timing. Define separate cleanup state and a bounded cleanup objective. Deletion enumerates/removes the applicable versions and abandoned multipart uploads, or records the specific permitted retention exception. Configure noncurrent-version cleanup and verify it; do not label a delete marker or lifecycle eligibility as physical erasure.
- **Closure evidence:** An object intentionally left present after its logical expiry is not downloadable. Versioned objects with multiple versions are deleted or explicitly retained according to policy. The job's terminal state reflects verified cleanup/exception evidence.

### OPS-006 — Quotas and upload limits lack a mandatory deployed configuration

- **Severity:** Medium. **Status:** Open.
- **Sources:** [design §§5/8](../design.md), [AND-EXP-007](../specs/android-data-export/spec.md), [AND-SYNC-006](../specs/android-offline-sync/spec.md), [artifact request schema](../../../../contracts/openapi.yaml), PRD-026.
- **Failure:** The API has a 1 MiB JSON bound, but an authenticated client can create many distinct idempotency keys, export jobs, and upload tickets. Artifact size_bytes has no hard maximum in the exchange contract. A declared size check at completion occurs after storage/network resources may already have been consumed. Requirements mention configured bounds without defining their required deployment inputs or fail-closed defaults.
- **Required correction:** Define mandatory maxima for each artifact kind, export selection count/total bytes, concurrent jobs, queued jobs, owner storage, per-principal mutation rate, and global worker/API concurrency. Enforce upload size/checksum through the chosen signed upload mechanism as well as completion. Define 413/429 responses, Retry-After bounds, quota reclamation, and behavior when limit configuration is missing. Keep research-dependent limits separately reviewed; no unlimited fallback is acceptable.
- **Closure evidence:** Oversized and excessive requests fail before expensive work, signed upload requests cannot bypass the agreed constraints, rate limiting works across multiple API tasks, and cleanup releases reserved quota even after a failed job.

### OPS-007 — Private AWS tasks need an explicit outbound and startup plan

- **Severity:** Medium. **Status:** Open.
- **Sources:** [design §§2/3](../design.md), [AND-ENV-003/004/005](../specs/android-app-environment/spec.md), [deployment tasks §23](../tasks.md).
- **Failure:** A template can satisfy the proposed assertions for private tasks, encrypted resources, and TLS while its tasks cannot pull images, obtain secrets, publish logs, access queues/objects, or refresh allowlisted issuer keys. Private placement alone does not establish an outbound route. Separately, unconstrained task counts and per-process database pools can exhaust the small QA database during a rolling deployment. [AWS private-task outbound networking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/networking-outbound.html)
- **Required correction:** Specify the VPC routing/endpoints or NAT design for each required dependency, DNS behavior, security groups, execution-role versus application-role permissions, and health/startup dependencies. Define API/worker task sizes, desired/max counts, pool sizes and deployment surge against a database connection budget. Include migration credentials/locking, secret rotation rollout, graceful request draining, and rollback compatibility in the runbook.
- **Closure evidence:** Synthesized assertions cover connectivity and roles as well as placement. A QA task performs each required dependency operation with no public IP; a rolling deploy stays inside the connection budget; a failed migration prevents promotion; secret refresh and draining are exercised.

### OPS-008 — Shared API vocabulary does not yet cover every feature consistently

- **Severity:** Medium. **Status:** Open.
- **Sources:** [design §5](../design.md), [AND-PRO-004](../specs/android-profile/spec.md), [AND-SYNC-005](../specs/android-offline-sync/spec.md), [privacy status contract](../specs/android-privacy-controls/spec.md), [alcohol engineering contract](../specs/android-alcohol-channel/spec.md), [LLD §9](../../../../specs/LLD.md).
- **Failure:** Profile concurrency uses 412, while snapshot/LLD stale-revision handling uses 409; a generic outbox has no complete status mapping. Privacy UI names partially_completed while the design names partially_retained. The shared operation table omits the alcohol GET/POST paths declared by that feature. Endpoint additions mostly have prose shapes and therefore can diverge between app and API even while the old OpenAPI passes validation.
- **Required correction:** Establish an authoritative versioned platform DTO/API contract with every route, request/response envelope, error code, status enum, ETag rule, idempotency scope/retention, and deletion-generation field. Choose the stale If-Match status and use it consistently, preserving 409 for the distinct idempotency/state conflict if desired. Define compatibility/migration from the existing exchange contract and generate or test mobile/API consumers against it.
- **Closure evidence:** One contract test inventory covers all 20 features' network operations, every terminal job state renders, every documented endpoint is implemented or explicitly unavailable with its specified response, and mobile/service tests agree on stale preconditions and replay.

### OPS-009 — AWS operating cost is missing from the production acceptance plan

- **Severity:** Medium. **Status:** Open.
- **Sources:** [design §3](../design.md), [AND-ENV-004/006](../specs/android-app-environment/spec.md), [PRD-026 and economics](../../../../specs/PRD.md), upstream BUS-001/002.
- **Failure:** The proposed always-running ALB, multiple Fargate tasks, Multi-AZ database, network egress infrastructure, backups, logs, and QA copy can be deployed successfully without a recorded operating-cost estimate or spending alarm. A small initial user population may then have disproportionate per-user platform cost, undermining the stated subscription hypothesis. No actual monthly cost is claimed by this review.
- **Required correction:** Add a dated, region-specific estimate using exact proposed resource sizes, baseline/no-user cost, representative usage/retention/egress cases, and QA operating schedule. Require an owner-set monthly budget and alert destination, resource tags, bounded log retention, and a QA teardown/recreation procedure that preserves only intentionally retained resources. Budget alerts are notifications, not a guaranteed hard spending cap. Record separate production availability and cost choices.
- **Closure evidence:** The deployment checklist includes the estimate and configured budget alarms; synthesized resources have cost allocation tags/retention; an operator can identify and remove the QA cost drivers without touching production. These are financial-planning inputs, not proof of viable subscription margins.

## All-20 capability coverage

Every capability below was read and traced through its platform dependencies. A row without a unique finding is not a certification that an implementation exists or passes.

| Capability | Platform dependency reviewed | Finding links |
|---|---|---|
| android-onboarding | Bundled/current notice, receipt idempotency, offline entry, fixed environment | OPS-008 |
| android-sign-in | PKCE, issuer access tokens, refresh race, namespace lock, environment separation | OPS-007/008 |
| android-profile | Immutable revision, initial ETag, offline queued saves, ownership | OPS-008 |
| android-dashboard | Current capabilities, stale refreshes, pending result and delivery state | OPS-003/008 |
| android-device-pairing | Provisioned registry, association context, bounded replay, revocation | OPS-008 |
| android-guided-check | Attempt lineage, immutable finalization, outbox, delayed result | OPS-003/008 |
| android-saliva-measurement | Authorized lab import, sample lineage, unit and source controls | OPS-004/006/008 |
| android-eye-capture | Raw-media retention, signed upload, verified object, permission changes | OPS-001/004/005/006 |
| android-heart-rate | Qualified configuration, local protected persistence, bounded transport | OPS-008 |
| android-ecg-capture | Optional modality, protected raw artifacts, qualified hardware gate | OPS-004/005/006 |
| android-reaction-task | Native clock separation, event bounds, durable start and terminal state | No additional platform finding; domain/timing review remains required |
| android-results | Null result versus pending, immutable digest link, worker retries | OPS-003/008 |
| android-history | Owner cursor boundary, account generation, supersession, deletion reconciliation | OPS-002/008 |
| android-offline-sync | Stable operation keys, conflict handling, worker/queue boundary, deletion | OPS-002/003/006/008 |
| android-privacy-controls | Recent reauthentication, scope, generation barrier, deletion/restore | OPS-001/002/003/005/008 |
| android-settings-accessibility | Immutable production endpoints, safe diagnostics, truthful capability display | OPS-008 |
| android-study-enrollment | Membership, consent version, revocation at upload/delivery | OPS-001/004 |
| android-alcohol-channel | Independent append-only record and dedicated endpoints | OPS-008 |
| android-data-export | Selection snapshot, asynchronous worker, immutable bytes, owner delivery | OPS-001/003/004/005/006/008 |
| android-app-environment | LocalStack parity, private AWS dependencies, promotion, recovery, cost | OPS-002/003/005/006/007/008/009 |

## Boundaries and positive controls to preserve

- LocalStack must remain an explicit S3/SQS test target. Mock tests cannot be relabeled as LocalStack, and LocalStack success cannot substitute for QA IAM/network behavior.
- The same application images should be promoted by digest while environment identity and data remain separate. Schema compatibility must survive rollback.
- Scientific gates must remain unavailable until their specific evidence exists. Authenticated use, successful app compilation, or AWS deployment cannot close assay, optical, body-connected hardware, timing, or model gates.
- Restore, native-device, load, signed-build, and QA/production evidence must stay marked unexecuted until actually run. This review creates no such evidence.

## Closure record

The implementing/reconciling agent should append, per finding, the correction location, tests required, reviewer, final disposition, and date. An Open finding must not be silently removed from this record when its text is fixed elsewhere. This report is complete as an independent pre-implementation review; it is not a production release approval.
