# Platform operator runbooks

These procedures correspond to the [platform contract](../../openspec/changes/production-mobile-platform/platform-contract.md). Assign the actual responsible person/team in deployment inputs before participant use. Alarm resources and procedures are supplied; staffed coverage, delivered alerts, a four-hour RTO and a 24-hour RPO have **not** been demonstrated here.

## Readiness and incident triage

Use the exact environment's stack outputs and image digest. Check ALB target health, ECS desired/running counts, readiness, RDS availability/connections, SQS source/dead-letter age and custom outbox/privacy/cleanup metrics. Inspect request/job references and reason codes only. Do not put access tokens, signed upload URLs, request bodies, raw measurements or email addresses into incident logs.

Open the stack output `CloudWatchDashboardUrl` for the environment's `otgd-qa-health` or `otgd-prod-health` dashboard. It shows alarm states, ready API targets, traffic/errors/latency, API and worker utilization, database capacity, source/dead-letter queues, aggregate privacy/cleanup health and CloudFront web delivery. CloudFront widgets read basic metrics from `us-east-1` with the `Region=Global` dimension. Empty graphs require investigation; they do not establish healthy services. ECS desired/running counts still come from ECS service inspection because Container Insights is disabled.

| Signal | Initial alarm | Operator response |
|---|---|---|
| Any DLQ message | One visible message | Inspect its stable job ID and database disposition; follow replay procedure. |
| Old source message | Five minutes | Check workers, private dependency access and lease recovery. |
| Unsent outbox age | Two minutes | Inspect database dispatcher lease, SQS permission/reachability and message publication. |
| Active/failed privacy job age | 15 minutes | Check journal receipt, generation barrier, declared cleanup steps and identity-provider response. |
| Cleanup beyond objective | One overdue item | Check quarantine/export version enumeration; do not report physical erasure from a delete marker. |
| Database connections | 30 QA / 70 production for five minutes | Inspect task overlap/pools; keep zero overflow and the 40/80 application budgets. |
| Unhealthy production target | Above zero for five minutes | Check migration/readiness and rollback a verified incompatible release. |
| API server errors | At least 5% over five minutes with at least 20 requests | Correlate random request references, dependency health and recent rollout. |
| No ready API targets | Fewer than one target for five minutes after activation; missing data breaches | Check ECS desired/running tasks, rollout events, readiness dependencies and ALB registration. |
| Missing aggregate worker metrics | Five missing one-minute publications after activation | Inspect worker/metrics sidecar tasks, database access and CloudWatch permissions; idle workers must still publish zero ages/counts. |

The sidecar publishes three aggregate metrics once per minute, without identity dimensions. Maximum aggregation tolerates duplicate publishers during rollout. Three consecutive publishing failures terminate the essential sidecar so ECS restarts that worker task. The missing-publisher and no-ready-target alarms are omitted while `activateServices=false`, preserving stopped migration/recovery stages. Service metrics still require an external alarm-delivery probe; verify the SNS subscription and KMS permissions. Do not test notification delivery to an invented recipient.

## A failed or delayed deletion

First verify that the account generation advanced and access to retired data is denied. Inspect the accepted journal key and non-null VersionId recorded with the job. A 202 response requires that independent receipt; a failed write stays retryable under the same original idempotency key.

A pending upload ticket retains its conditional-create protection through its five-minute expiry plus the 60-second margin. That margin constrains admission; it does not prove a transfer admitted earlier has finished. Do not remove the current object early, reset the ticket or create another unrestricted overwrite URL. A scheduled wait must not consume one of the five failed execution attempts.

Check all artifact/export versions and delete markers under the retired generation. The worker repeats whole-prefix sweeps for completed deletion jobs and retained cleanup references, because an older restored database may lack individual artifact rows and a late upload may become visible after an earlier sweep. A delete marker alone is not physical erasure. Technical cleanup failure stays pending/failed with its actual reason; it cannot be renamed an approved retention exception.

Account deletion also requires provider removal/revocation. If recovery has the subject HMAC but no trustworthy provider subject for an incomplete account deletion, the reconstructed job remains blocked with `IDENTITY_RECONCILIATION_REQUIRED`. An operator must resolve the original issuer/subject from independent approved identity records and verify its HMAC and account reference. A keyed hash is not reversible; never guess a Cognito username. Record the authorized reconciliation, requeue the same job through the maintenance identity, and preserve its accepted scope/generation.

## Queue failure and controlled replay

Each message contains a schema version and stable job UUID, not health JSON. Source visibility and database leases are 120 seconds; heartbeat is 30 seconds; the database fencing token increments on each claim. At-least-once delivery is expected. A stale worker cannot publish merely because it still owns an SQS receipt. The dispatcher requeues expired leases and unpublished outbox records so acknowledgment of a duplicate cannot lose work.

Before replay, establish whether the job is already completed, expired, permanently invalid, generation-retired, awaiting upload expiry or transiently failed. Do not redrive a whole DLQ indiscriminately. Inspect the relevant immutable inputs and accepted journal if it is a deletion. Record operator identity, job ID, separate replay ID, reason and authorized scope. Recheck current generation/policy; a replay does not revive data or generate a new accepted deletion.

For a bounded replay, the maintenance identity locks the existing job, increments its fence, clears the expired lease, records replay evidence, resets only the approved five-attempt cycle, and marks its existing outbox due. The implementation provides [replay-job.py](../../scripts/replay-job.py); it refuses current leases, already terminal/retired jobs and missing deletion acceptance. Source queue redrive remains five receives and a maximum 15-minute attempt; do not lengthen those settings to hide a stuck task. Probe kill points before claim, after claim, after object write, after database commit and before queue acknowledgment in QA.

## Database recovery without resurrecting deleted data

1. Record incident ID, environment, deployed digest, chosen recovery point, actual outage start and responsible operator. The permitted recovery point is at most 35 days old. Inventory retained snapshots and journal/key versions; a snapshot outside that window blocks this procedure until its retention conflict is resolved.
2. Run `deploy/platform.py quiesce` with the correct environment config. It suspends dynamic/scheduled ECS scaling, requests zero API/worker tasks and waits for complete drain. Verify no manual task, separate dispatcher or operator writer remains. Do not treat zero desired count as proof that running tasks have stopped.
3. Set `activateServices=false`, `recoveryRequired=true` and the exact `databaseSnapshotIdentifier` ARN. Use `deploy-stopped` with the trusted signed image. Preflight requires the snapshot's source deployment tag, expected data KMS key, available encrypted PostgreSQL version, supported storage and original age. CDK restores into a replacement private database and retains the old database for reconciliation. Journal, tombstone key, data key and authoritative identity infrastructure remain the environment's existing independent resources.
4. Verify the restored database endpoint and exact TLS identity. Run the compatible migration with services stopped, saving a new receipt. This updates the schema and resets the application role to the current injected secret. Do not establish a new journal during recovery.
5. Run the restore command below with the actual recovery point timestamp. It first commits `recovery.verified=false`, so a subsequent error leaves readiness closed.
6. The tool lists every retained event version twice while writers remain paused, rejects replacement/deletion markers/noncanonical events, reads exact VersionIds, verifies required identity-key versions and constructs an immutable watermark in a separate prefix. Journal continuity must cover the recovery point with the 90-day-minimum policy. A mismatch or unavailable key keeps recovery closed.
7. The tool rebuilds subject-HMAC lookups for **both** all-data and account deletion, including accounts absent from the backup. It reapplies maximum valid generations, erases restored old-generation health rows for completed deletions, reconstructs missing accepted work and keeps incomplete accounts blocked. Every recovered operator/study/device qualification is suspended.
8. The tool writes and version-verifies a separate `RecoveryActivation` record. Its authentication cutoff is at least current time and at least every retained earlier cutoff. The database records that receipt and watermark. Signed `auth_time`, not a refreshed token's `iat`, must meet the cutoff after reopening. Fresh sign-in does not automatically restore study or capture permission.
9. With services still isolated from participant traffic, run targeted probes against deleted and nondeleted fixture accounts, stale tokens, stale generations, old queues, expired exports and unavailable journal/key paths. Pending deletions remain blocked while workers reconcile their accepted scope. Restore current studies/device authority only from independent current approved records, with audit evidence. This release has no preapproved human configurations to re-enable.
10. With services still stopped, run `verify-admission` against the exact restored image/source and save its actual task receipt. Activate within fifteen minutes of that task's completion using migration, restore and admission receipts, exact-revision GitHub gate evidence and the signed QA approval. Keep `recoveryRequired=true`. Confirm readiness and current authenticated owner behavior before admitting traffic. Record achieved recovery duration and data-loss interval, plus outstanding identity/cleanup cases; do not describe configured RTO/RPO objectives as achieved performance.

```bash
uv run --project services/api python deploy/platform.py restore \
  --config infra/config/prod.local.json \
  --release deploy/releases/prod-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --qa-evidence deploy/receipts/qa-validation-signed.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --backup-created-at ACTUAL_UTC_RECOVERY_POINT \
  --output deploy/receipts/prod-restore.json
```

After successful isolated probes, run independent admission verification while `activateServices=false`:

```bash
uv run --project services/api python deploy/platform.py verify-admission \
  --config infra/config/prod.local.json \
  --release deploy/releases/prod-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --qa-evidence deploy/receipts/qa-validation-signed.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --output deploy/receipts/prod-admission.json
```

Set `activateServices=true`, retain `recoveryRequired=true` and the reviewed snapshot identifier, then activate within fifteen minutes of admission-task completion:

```bash
uv run --project services/api python deploy/platform.py activate \
  --config infra/config/prod.local.json \
  --release deploy/releases/prod-REVIEWED_COMMIT.json \
  --gate-evidence deploy/receipts/gates-REVIEWED_COMMIT.json \
  --qa-evidence deploy/receipts/qa-validation-signed.json \
  --trusted-public-key /secure/otgd-release-public.pem \
  --output deploy/receipts/prod-migration.json \
  --recovery-receipt deploy/receipts/prod-restore.json \
  --admission-receipt deploy/receipts/prod-admission.json
```

The tool verifies the corresponding actual ECS tasks, exact commands, immutable image and source/account/region bindings. Missing or stale evidence fails closed; if admission expires, rerun it with services stopped and retain a fresh receipt. QA follows the same sequence with QA configuration/release paths and omits `--qa-evidence`; production requires the signed QA approval on every release operation. No script silently changes a failed recovery record to verified. The [deployment guide](../../deploy/README.md) documents the separate QA/prod one-shot wrappers, protected stage journals and DNS/public-access checks.

The standalone [restore-journal.py](../../scripts/restore-journal.py) can run inside the maintenance image for controlled exercises. It requires `OTGD_RECOVERY_REQUIRED=true`, the chosen UTC timestamp and `--confirm-quiesced`. It does not start services. Current support includes the reviewed privacy-v1 events; unknown event/key/retention schemas deliberately block recovery.

## Journal retention, lost keys and rotation

The journal has no automatic expiry. Runtime API, worker and maintenance roles cannot delete its events or replace an accepted current version. Before any administrator pruning, prove that every permitted recovery point is newer than the event and contains the later verified generation barrier; keep that evidence. The minimum is 90 days, while the permitted database recovery-point age is 35 days. Older manually retained snapshots suspend pruning. A journal outage or missing key is a recovery outage, not permission to admit old backup data.

Automatic **KMS key material rotation** preserves the key ARN and decryptability of older ciphertext; include retained key-version pricing when it applies. It is different from replacing the identity-tombstone HMAC secret. This initial release accepts the configured HMAC key identifier and fails closed on unknown retained identifiers. Do not rotate that secret to a new value/ID without a reviewed multi-key migration and a recovery exercise covering all retained references. Keep its existing value outside the database backup lifecycle.

For an application database credential rotation, stop admission or follow a tested compatible overlap procedure, rotate the separate application secret through the approved secret-management workflow, run the maintenance migration to update its login, then replace runtime tasks so ECS loads the new secret. Existing tasks do not automatically reread an injected secret. Preserve rollback credentials under the approved policy; never paste passwords into CLI arguments or tickets.

For a signing/device compromise, immediately suspend the affected configuration/binding using the operator identity, retain evidence, and verify newly admitted operations reject it. Old consent or a cached capability cannot reactivate authority. Clinical/device qualification updates require their own approved evidence and are not inferred by these infrastructure tools.

## Rollback, cleanup and QA teardown

Roll back application code to a retained, previously signed digest only if it is compatible with the current schema. The baseline migration supports schema 1 and refuses a downgrade. Stop/verify services, deploy the known digest stopped, execute/verify its compatible migration, run fresh `verify-admission`, and activate with both receipts through the ordinary release gate. Production still requires current signed QA approval bound to that exact release; an expired approval or missing retained gate evidence cannot be waived by calling the operation a rollback. After recovery, preserve the recovery-required setting, latest cutoff, restore receipt and journal authority. Do not roll back the independent journal, subject key or generation barriers. Partial one-shot failure does not imply rollback: inspect its protected `deployment-state.json`, actual completed receipts and current stack before choosing a new deployment attempt or compatible rollback.

QA teardown is explicit: quiesce, verify account/environment, then invoke `qa-destroy --confirm-qa-destroy`. The helper refuses production. CloudFormation keeps the versioned buckets, journal, KMS keys, secrets, software images and retained log groups; the normal QA database policy creates a final snapshot. Recovery-origin databases use retain rather than destroy. Inventory residual resources and costs after deletion; `down` or stack removal does not mean zero AWS cost. Remove residual QA data only under its actual retention/deletion policy and never delete journal evidence needed by retained snapshots.

## Required release evidence

Record actual digest, configuration version, execution time, tool/runtime versions, fixture IDs, expected/observed outcomes and operator/run reference. Required QA evidence includes private image/secret/log/S3/SQS/JWKS access, verified database TLS, conditional-upload overwrite races and version pinning, limits, the worker kill matrix/fencing/replay, authenticated export expiry/revocation, deletion acknowledgment loss, old-backup recovery with missing evidence, credential refresh and alarm delivery. These are the acceptance tests to execute; the repository's source/unit checks alone do not establish them.
