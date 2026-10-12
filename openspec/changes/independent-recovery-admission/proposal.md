# Independent journal admission and scoped recovery reapproval

## Why

A restored database may contain active accounts, approvals or queued jobs from
before accepted deletion or revocation. A database-only verified flag cannot
authorize service admission or research scope resumption.

## What changes

Check retained versioned control, deletion barriers and recovery activation at
API admission and nonprivacy worker boundaries. Preserve local journal
establishment continuity. Implement fresh independent per-study reapproval seals
without clearing global suspension or bypassing deletion cutoffs.

## Impact

API authentication/readiness, worker leases/computation/commits, additive
migration, maintenance restore/reapproval tools and least-privilege journal
permissions. Actual AWS retention and recovery rehearsal remain QA evidence.
