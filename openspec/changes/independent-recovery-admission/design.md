# Retained authority and per-study resumption

The database stores a pinned journal establishment binding. Bootstrap verifies
that binding before creating replacement resources. Existing unbound accounts
require an explicit administrator-supplied retained version and digest; no empty
bucket, successful process or replacement marker silently establishes authority.

Cloud admission independently reads versioned KMS-encrypted COMPLIANCE objects
with actual retention of at least 90 days. Deletion history is contiguous and
maps one identity to one account. Latest recovery activation binds account,
region, source, control, inventory, backup time and authentication cutoff. API
and nonprivacy workers refuse stale active database rows before writes and again
before result/export delivery. Bounded transport deadlines fail closed.

Global recovered scope suspension stays true. A maintenance releaser seals one
study only after its exact complete registry closure receives fresh independent
three-principal releases after activation. Its canonical immutable seal binds
the recovery receipt, source, region, study and complete approval digests. The
runtime can read but cannot write these seals. Current capture additionally
requires fresh participant consent. Retired/changed dependencies invalidate the
seal automatically; every unsealed study stays suspended.

Safe privacy cleanup remains available during other admission failures. Unit
transport models and actual LocalStack version behavior do not prove AWS Object
Lock, IAM, KMS or complete recovery behavior; QA rehearsal demonstrates those.
