# Application API and asynchronous worker

This service implements the [reviewed shared contracts](../../openspec/changes/production-mobile-platform/shared-contracts.md) and [platform contract](../../openspec/changes/production-mobile-platform/platform-contract.md). It records measurements, immutable acquisition evidence, user-requested exports and deletion jobs. **It does not execute an intoxication model.** Result probability, classification, operating threshold and active model fields remain null.

## Run and verify

Use Python 3.12 and the committed `uv.lock`. The supported local service path uses **actual PostgreSQL plus LocalStack S3/SQS**, with a separate fictional OAuth issuer:

```bash
uv sync --project services/api --locked
python scripts/local-platform.py prepare --host localhost
python scripts/local-platform.py up
python scripts/local-platform.py check
```

Run these commands from the repository root. Docker Compose and an appropriate LocalStack token are required. Full instructions, phone routing, isolated QA/prod configuration, and immutable promotion are in [infra](../../infra/README.md) and [deploy](../../deploy/README.md). The local issuer is never deployed to QA or production.

The [fictional local issuer contract](LOCAL_IDENTITY.md) documents browser session/Origin binding, fixed refresh deadlines, replay revocation, private signing-key custody, account deletion and disposable PostgreSQL verification.

For source verification without Docker:

```bash
uv run --project services/api pytest -q services/api/tests -m 'not postgres'
uv run --project services/api ruff check services/api/otgd --select E4,E7,E9,F
uv run --project services/api python tools/generate_application_contracts.py
uv run --project services/api python tools/verify_specs.py
```

The default unit fixture uses SQLite only under `OTGD_ENVIRONMENT=test`. Its explicit storage mock is named `MockVersionedStorage`. These checks do not establish PostgreSQL locking, LocalStack behavior or AWS execution. The platform workflow runs the same service tests with an actual disposable PostgreSQL 16 instance and verifies migration replay and the restricted runtime role. No test is authorized to reset a real deployment database.

## HTTP contract

The [generated OpenAPI](../../contracts/application/openapi.json) describes the implemented routes and typed request/response models. [Companion JSON Schemas](../../contracts/application/README.md) define profile, context, attempt, evidence manifest, alcohol, export, authorization, replacement navigation, report revisions and synthetic transport DTOs. Original scientific v0.1 schemas remain strict and are not widened to accept raw/native metadata; companion records carry that information.

| Area | Principal routes | Behavior |
|---|---|---|
| Startup | `/health/live`, `/health/ready`, `/v1/app-config`, `/v1/notices/{version}` | Safe public configuration, supported environment and exact current notice content/digest. Readiness checks schema and required recovery state. |
| Identity | `/v1/me/capabilities`, `/v1/auth/logout` | Pinned RS256 issuer/client access tokens, live family revocation, ownership and generation checks. |
| Profile | `/v1/me/profile`, `/v1/me/acknowledgments` | Versioned explicit saves, canonical units/BMI, current notice acknowledgment. |
| Check | `/v1/sessions`, `/v1/sessions/{id}` | Owner-scoped registration/history/detail, stable cursors, immutable finalized records and linked replacement checks. |
| Replacement navigation | `/v1/sessions/{id}/replacement-links` | Bounded, owner/generation-scoped predecessor and direct replacement pages; accepted frozen snapshots only, with independent link/hash checks. |
| Evidence | `.../snapshot`, `.../context`, `.../attempts/{id}`, `.../evidence-manifest`, `.../evidence` | Independent revisions and canonical digests; exact source, session, attempt, projection and context linkage. |
| Result | `.../finalize`, `.../result` | Transactional outbox plus SQS processing; measurement-only or invalid output. |
| Devices | `/v1/devices/...`, `.../capture-authorizations`, `.../attestations` | Domain-separated P-256 proof, operator trust anchors, single-use online start authorization and immutable signed payload mapping. |
| Studies | `/v1/me/studies`, `/v1/studies/{id}/consents`, `.../withdrawals` | Exact document hash, explicit consent and effective withdrawal, independently qualified channel/configuration checks. No real study is seeded. |
| Raw artifacts | `/v1/artifact-uploads`, `.../{id}`, `.../{id}/complete` | Approved scope only; bounded conditional PUT; checksum/media/size verification pinned to a non-null S3 version. |
| Reference laboratory | `/v1/research/lab-imports` | Current study and independently provisioned laboratory role; verified source report and strict normalized analyte records. |
| Report revisions | `/v1/research/sessions/{id}/report-artifact-uploads`, `.../report-revisions`; owner reads under `/v1/sessions/{id}/report-revisions` | Separate purpose-specific report completion, current administrative authority before replay, immutable same-specimen report/result chain, and preserved original capture/target times. |
| Alcohol | `/v1/sessions/{id}/alcohol` | Separate immutable v1 companion in mg/L; never inserted into the THC snapshot or converted to BAC. |
| Privacy | `/v1/privacy/exports`, `/v1/privacy/deletion-requests`, `/v1/privacy/jobs/{id}` | Stable explicit operations with visible pending/completed/failed/expired dispositions. |
| Download | `/v1/privacy/jobs/{id}/download` | Authenticated current-policy gateway, exact stored object version, no presigned bearer GET. |

Authenticated writes require `Authorization: Bearer ...`, `X-Data-Generation` and a stable `Idempotency-Key`. Revisioned writes also require a quoted integer `If-Match`. Use `"0"` for a new context, attempt or evidence manifest. A new session begins at revision 1; accepting its snapshot advances that session revision. Read the returned ETag instead of assuming later revisions.

Use the same key and byte-equivalent canonical request when reconciling an unknown outcome. A changed request under the same key receives 409. A stale revision receives 412; a missing precondition receives 428; a retired ordinary generation receives 410. Current-generation replay precedes ETag conflict, but never bypasses account/notice/generation policy. Deletion/logout retain only their narrowly defined minimal-receipt replay exceptions.

## Check upload order

1. Persist the frozen local check and explicit upload intent.
2. Register the account-owned session with its existing UUID, mode and optional replacement link.
3. Upload immutable CaptureContext and every CaptureAttempt, preserving invalid/canceled predecessors.
4. Upload the separately selected alcohol companion if one exists.
5. Upload the v0.1 snapshot with the current session ETag.
6. Upload the EvidenceManifest linking the complete attempt set, selected attempts and context digest.
7. Finalize with snapshot and manifest SHA-256 values and the current session ETag.
8. Poll the returned result with bounded retry. Delivery state is separate from measurement validity.

The service independently checks the native reaction schedule and scoring against the frozen configuration, preserving actual native evidence as uncalibrated `prototype_sensor`. Software simulator records retain all accepted receive messages, their original JS digest, bounded clock exchanges, device/boot/attempt identity and fixed fictional values. None of these mechanisms qualifies human measurements. Guest records have no upload route in the mobile domain; signed-in local/QA fictional checks use a separate account namespace.

## Concurrency and privacy design

All account mutations serialize on the owner account row. Locked ORM queries refresh existing identity-map values after commits or waits; locking alone would not refresh cached SQLAlchemy objects. Duplicate job deliveries claim a database lease and increasing fencing token. Outbox selection filters eligible jobs before its page limit so terminal records cannot starve pending work.

External S3/SQS calls are kept outside long account transactions where the operation requires a two-phase handoff. Final publication rechecks current generation, consent and job fence. Worker visibility/lease is 120 seconds, heartbeat is 30 seconds, the execution budget is five attempts and a claim is bounded to 15 minutes. A scheduled wait for a still-live upload ticket does not consume a failed attempt.

Deletion first advances the account generation and records a durable local barrier. A 202 receipt is returned only after the independent deletion journal is version-verified. The worker removes all relevant artifact/export versions, clears health rows and response bodies, removes the identity-provider user for account deletion, journals completion, and then publishes the fenced terminal state. All-data deletion requires explicit acknowledgment before a new empty generation becomes writable.

Cleanup claims an artifact disposition before external deletion. Artifact completion rejects a cleanup claim and rechecks immutable metadata under the row lock, preventing resurrection of a version already selected for removal. Cleanup pages use per-row due times, independent failure handling and repeated generation-prefix sweeps. Already admitted download bytes and copies the user has exported cannot be recalled.

Restoring PostgreSQL does not restore the journal or its independent key. [Recovery tooling](../../scripts/restore-journal.py) requires consistent journal inventories and provenance, applies generation barriers before readiness, and suspends recovered study/device scopes. A missing provider subject for an incomplete account deletion requires independently verified identity reconciliation; its HMAC is not treated as reversible.

The identity tombstone key has immutable migration-owned provenance: its configured label and SHA-256 fingerprint of the secret bytes. Admission and readiness check that provenance before looking up or creating an account. Replacing either the secret or its label fails closed, and the restore inventory must name the same effective key ID. Key rotation is unsupported until a retained-keyring migration is implemented. An existing database without recorded key provenance requires independent reconciliation; migration does not guess which key originally derived its accounts.

Research consent preserves each accepted receipt separately from the current consent pointer. The receipt includes the exact approved invitation, document version/hash, actual client acknowledgment time and server acceptance time. A changed approved version or invitation requires explicit new consent even when its text hash is unchanged. Lost-response retries keep their original acknowledgment and return the original immutable receipt. Withdrawal changes the current pointer without rewriting the historical acceptance. Deletion receipts declare retained identity barriers, audit/security metadata, minimal receipts, membership references, cleanup references and journal evidence; they do not claim those categories were erased.

## Deployment authority

The numbered additive migration `002_replacement_navigation` creates and verifies the index for bounded direct replacement queries and records its immutable migration identity. It is replay-safe and does not rewrite scientific evidence or change the v1 serialization. Baseline and index migrations run with migration authority before the application starts; host tests and actual PostgreSQL CI evidence are recorded separately.

Migration `005_participant_acquisition` prevents rewriting instruction, specimen, abandonment and lab-import receipts. `006_cardiac_interval_anchors` protects the original signed-start and device-attestation timestamps, allowing only the initial issued-to-started authorization transition. Migration `007_capture_guard_unicode` upgrades an already installed preliminary v6 comparison so PostgreSQL can handle the signing domain's escaped NUL. It preserves all existing records, hashes, timestamps, grants and the v6 marker; it does not rebind or delete an anchor. The comparison-only escape also distinguishes an actual NUL from literal backslash text. Run the normal `uv run --no-sync python -m otgd.migrate` maintenance command before restarting the service. Actual PostgreSQL regressions reproduce the preliminary failure, apply v7 twice, and verify immutable timestamps, original records, unchanged permissions and the allowed signed-domain transition.

The migration role performs DDL. Runtime identities have bounded PostgreSQL pools, verified TLS in QA/prod, no authority to modify qualification/trust/recovery records, and append-only audit writes. Secrets are injected by the environment; the repository contains only an official public RDS CA bundle. Real operator qualification, study documents, device trust anchors, clinical models, domain/certificate inputs and AWS credentials are not fabricated or supplied by this service.
