# Platform implementation review

Reviewed **2026-10-11**, after the specification review checkpoint and before the integrated implementation commit. The reviewer owns infrastructure and operational scripts; the backend owner applied the corrections below. This is a targeted source and regression review, not evidence of deployed AWS behavior or clinical validity.

## Outcome and scope

The three findings below are **resolved in source and pass their targeted deterministic regressions**. Review covered the API's account/generation admission boundary, worker claim/commit fencing, queue dispatch liveness, deletion journal ordering, artifact completion/cleanup coordination, and authenticated export admission. Infrastructure synthesis, recovery logic and signed release validation have separate executed evidence in [VERIFICATION.md](VERIFICATION.md).

Executed `uv run pytest tests/test_interleavings.py -q` from `services/api`: **4 passed**. The two authorization/claim interleavings, terminal outbox page and artifact completion/cleanup regression are in [test_interleavings.py](../services/api/tests/test_interleavings.py). This workspace used SQLite and replaced SQS/S3 dependencies for these cases. Separately, all **10** infrastructure Python unit tests passed, including [cleanup alarm state progression](test/test_metrics.py).

The original counterexamples are retained so future refactoring preserves the reasons for these controls. PostgreSQL contention, real S3 conditional writes, process termination, late uploads and recovery from a deployed database snapshot still require the actual integration gates described in [OPERATIONS.md](runbooks/OPERATIONS.md). No SQLite or mocked dependency test is counted as that evidence.

## IMPL-OPS-001 — Stale ORM state can defeat generation and fencing checks

**Severity: Critical. Status: Resolved in source.**

**Sources:** [auth.authenticate](../services/api/otgd/auth.py), [main.access](../services/api/otgd/main.py), [worker.claim_job/current](../services/api/otgd/worker.py), and the `expire_on_commit=False` session configuration in [db.py](../services/api/otgd/db.py). Requirements: [shared account/generation contract](../openspec/changes/production-mobile-platform/shared-contracts.md) §§2–3 and [platform worker contract](../openspec/changes/production-mobile-platform/platform-contract.md) §6.

**Counterexample:** An API request loads an active generation-1 account, commits its rate-limit transaction, and then waits while another request commits the deletion barrier. A second locked SELECT can return the already loaded ORM object without replacing its cached attributes. The old implementation could therefore authorize against generation 1 even after locking the now deleting generation-2 database row. Similarly, a worker loaded a pending job as an account lookup hint before acquiring the account lock. A competing worker could claim the job while it waited; the later locked SELECT could still reuse cached pending/fence-0 values and create a duplicate fence-1 claim.

**Correction verified:** Locked Account and Job reads explicitly use `execution_options(populate_existing=True)`. The same refresh is applied to other `SELECT FOR UPDATE` reads. Admission now evaluates the current locked row, and a claimant re-evaluates the current running state, lease, attempts and fence after lock acquisition. Existing account-before-job lock ordering remains intact.

**Verification:** `test_deletion_between_authorization_passes_refreshes_account` and `test_waiting_worker_refreshes_job_after_other_claim` passed. They exercise the stale loaded objects across deliberately scheduled changes. Source refresh semantics and deterministic SQLite interleavings do not replace testing row contention on PostgreSQL.

## IMPL-OPS-002 — Terminal outbox rows can starve live jobs

**Severity: High. Status: Resolved in source.**

**Sources:** [worker.dispatch_once](../services/api/otgd/worker.py); [platform contract](../openspec/changes/production-mobile-platform/platform-contract.md) §6.

**Counterexample:** At least 25 failed or otherwise ineligible jobs retain unpublished, due outbox rows. The old dispatcher selected the first 25 outbox rows and rejected their jobs only in Python. Those rows stayed eligible for the next page, indefinitely preventing a later valid job from being sent.

**Correction verified:** The dispatcher joins Job, filters to pending/running work and confirmed deletion-journal acceptance in SQL before applying the limit, and orders by outbox availability and ID. `FOR UPDATE OF outbox SKIP LOCKED` claims only the selected outbox rows. Terminal rows can no longer consume the eligible page. Durable send disposition still supports retry after a crash between SQS send and database acknowledgment.

**Verification:** `test_terminal_outbox_rows_cannot_starve_eligible_job` passed with 26 terminal jobs preceding the live job. It verifies the selected SQS send through a test double. Real SQS delivery, duplicate receipt and process-kill recovery remain integration tests.

## IMPL-OPS-003 — Artifact cleanup can delete a version during completion

**Severity: High for the implemented qualified artifact path. Status: Resolved in source.** The current release has no active approved human capture configuration; that release gate limits current exposure but does not remove the requirement to coordinate this path correctly.

**Sources:** [main.artifact_complete](../services/api/otgd/main.py), [worker.cleanup_once](../services/api/otgd/worker.py), [storage.verify_artifact](../services/api/otgd/storage.py); [shared artifact contract](../openspec/changes/production-mobile-platform/shared-contracts.md) §7 and [platform contract](../openspec/changes/production-mobile-platform/platform-contract.md) §§5,8.

**Counterexample:** Completion verifies a particular S3 version outside its database transaction. Cleanup then deletes that version and marks the artifact purged. The old completion commit could overwrite the purged disposition as verified without rechecking its immutable metadata, thereby accepting a reference to deleted evidence. A cleanup task selected before completion could also later delete a newly accepted version.

**Correction verified:** Cleanup commits the locked `cleanup_pending` disposition before performing external deletion, and retains failed cleanup claims for later attempts. Completion locks and refreshes the Artifact row both before verification and at commit, accepts only quarantine/verified dispositions, rechecks the submitted hash, size and media type, and preserves an already verified VersionId. A cleanup claim therefore wins by making completion refuse; a completion commit wins by moving the row out of the cleanup query's eligible states.

**Operational follow-through:** The metrics sidecar includes `cleanup_pending` in overdue cleanup alarms. A passing regression verifies that entering this disposition cannot hide an overdue cleanup, and that a recorded successful cleanup clears the alarm contribution. Unverified artifact count/byte quota accounting includes both quarantine and cleanup-pending artifacts until disposal succeeds.

**Verification:** `test_artifact_completion_cannot_resurrect_cleanup_claim` passed: cleanup wins after external verification, and completion returns 410 without setting an accepted VersionId. Source and deterministic interleaving tests address the database disposition race. The actual conditional S3 upload, version deletion and admitted-late-upload matrix remains unexecuted here. The ticket-expiry margin does not guarantee that every previously admitted transfer has finished.

## Additional checks and retained constraints

- Export download authorization still verifies owner, current generation, account/policy/consent, job state and logical expiry before opening a stream. Range/conditional requests cannot bypass that admission. Reads specify the accepted S3 VersionId; previously admitted streams remain subject to the documented recall limits.
- A deletion acceptance preserves the generation barrier through an independent journal failure. The original request can resume its same durable intent. The worker writes and verifies terminal journal evidence before publishing terminal database state, and commit still requires the current fence.
- Cleanup pages claim and defer oldest due records before external work, isolate per-record failures, and retain prefix references for late-arrival reconciliation. The previous 100-row cleanup starvation regression remains relevant independently of the outbox fix.
- The runtime database role cannot alter operator trust/recovery records or update/delete audit rows. The disposable PostgreSQL role probe verifies these restrictions after two migrations; execution requires the actual PostgreSQL CI service.
- The public RDS CA bundle has an explicit gitignore exception and an independently checked digest. Container build inputs must include that bundle; cloud database connections require `verify-full` and the configured CA path.

This review authorizes no AWS deployment, credential use, subscription confirmation, human capture, intoxication inference or production promotion. Deployment remains gated by the signed immutable image and actual QA evidence.
