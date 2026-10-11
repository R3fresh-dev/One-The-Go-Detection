# Study reapproval after restore

Restoring PostgreSQL does not restore authority. API readiness, authentication
and nonprivacy worker leases/computation/commits verify the independently
retained deletion journal and latest recovery activation. Local development also
checks the pinned journal establishment version; an ephemeral replacement
LocalStack journal cannot silently become authority for retained accounts.

The restore procedure retains `scopes_suspended: true`. That global field stays
true. Reopening one study requires a fresh independently retained seal for that
study and recovery activation; changing a database Boolean never resumes it.

## Reapprove and seal one study

1. Verify the isolated restored database against its actual retained control,
   deletion inventory and recovery activation. Deploy's `verify-admission` step
   must succeed before services activate. Preserve all authentication cutoffs
   and accepted generation/deletion barriers.
2. Independently submit, review and release fresh versions after activation for
   the study and its complete dependency closure: acquisition configurations,
   qualification, retention, devices, calibrations, methods and model where
   applicable. Each version has three distinct authenticated principals and
   the exact content digest. Old approvals cannot be reused as fresh decisions.
3. Issue fresh study consent documents/invitations and obtain fresh participant
   acceptance after the recovery cutoff. The customer API refuses old consent
   even when an old database row says active.
4. On a private maintenance host, use actual short-lived credentials for the
   environment's `registry-releaser` role and the independently authorized
   maintenance database identity. Run in the locked application image:

   ```sh
   uv run --no-sync python /app/scripts/reapprove-recovered-study.py \
     --study-id APPROVED_STUDY_ID \
     --expected-account AWS_ACCOUNT_ID \
     --expected-role-arn EXACT_REGISTRY_RELEASER_ROLE_ARN
   ```

The command verifies actual cloud role/account identity, database maintenance
privilege, independent recovery admission and every current fresh approval. It
writes one immutable canonical object under `scope-resumptions/` and verifies
its actual pinned version, bytes, KMS encryption and COMPLIANCE retention. The
receipt prints its version and SHA-256, never credentials or participant data.
It enables no service and changes no global suspension flag.

Customer capture checks read the retained seal again and compare its exact
current dependency closure. Missing/replaced seals, later incompatible seals,
retired approvals, stale consent and foreign recovery anchors refuse the study.
Every unsealed study remains suspended. Privacy deletion cleanup can continue
when other recovery admission fails; retained deletion evidence is never erased
to reopen a study.

Automated tests use visibly fictional reviews and modeled versioned transport.
Actual AWS Object Lock, operator assignments, restore rehearsal and participant
reconsent require observed QA evidence before production approval.
