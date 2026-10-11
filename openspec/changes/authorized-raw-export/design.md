# Raw export admission and delivery

## Independent authority

`RawExportAuthorization` schema 1.0.0 is immutable registry content: exact
authorization ID/version/content SHA, owner account UUID, positive data
generation, study, permitted eye-video/ECG-waveform kinds, literal
`participant_requested_raw_export` purpose, purpose identity/text, exact
retention policy ID/version/JCS SHA, notice version/text/UTF-8 SHA, expiry, copy
lifetime and byte caps. Identity/study/purpose/notice labels are at most 128
characters; revision is at most 64, purpose text at most 4096 characters, notice
at most 16384 UTF-8 bytes. Lifetime is 60–86400 seconds; approved caps can only
narrow 50 MiB uncompressed and 64 MiB archive. Existing three different verified
operator principals submit, approve and release. Retirement locks and current
dependency verification are shared with other registry kinds.

## Explicit acceptance

`GET /v1/privacy/raw-export-scopes` returns no cloud object keys or URLs. Its
current owner/generation choices are four authorities per page with SHA
`next_cursor`; `authorization_cursor` resumes authority scanning. An exact
`authorization_id` may have 128-source pages with UUID
`artifacts_next_cursor`; only this exact authority accepts `artifact_cursor`.
Pages are bounded to 512 KiB and can be empty while a next cursor exists.
Expired or invalid authority is not offered; individually over-budget sources
are not offered. The UI shows exact purpose, notice, kind, source check, size and
retention deadline. New purpose/page/account/generation clears unfinished
confirmation and selections. No raw selection is implied by recording choices.

`POST /v1/privacy/exports` retains `selection`, `format:json_zip` and
`include_raw:false` for the ordinary path. Raw requests require `include_raw:true`
and `raw_scope` containing exact authorization/notice identities and hashes,
`confirmed:true`, actual UTC acknowledgement time and 1–128 distinct explicit
artifact UUIDs. The acknowledgement must be within 600 seconds before or five
seconds after server acceptance. Current study consent and separate effective
recording/upload consent must still admit every source. Check ownership,
generation, selected check IDs, completed/invalid state, permitted study/kind,
exact retention authority and non-null verified S3 VersionId are rechecked.

The job freezes original grant and source descriptors under a JCS hash. Scope
expiry is the minimum of acceptance plus approved lifetime, 24 hours, grant
expiry and every source's original acquisition-based retention deadline.
Duplicate request bodies replay the original job under current admission;
different bodies with the same key fail. A stored positive flag cannot replace
current released authority. No raw branch accepts source laboratory reports.

## Worker and public evidence

The existing fenced claim/lease and generation checks apply. Each source is
re-admitted before and after an exact-version S3 read performed without holding
a database lock. Reads require actual matching VersionId, ContentLength,
ContentType and SHA-256 and consume at most declared size plus one byte. Raw
members use only `raw/<eye_video|ecg_waveform>/<UUID>.bin`. Structured lineage,
all raw bytes and the manifest share the approved uncompressed cap; complete
ZIP bytes share the approved archive cap. Any overflow rejects the whole job.

Manifest `raw_export` and admitted job `raw_export` preserve exact purpose,
acknowledgement, authorization and notice hashes, frozen hash and source
ID/check/kind/version/size/hash/media/retention/path descriptors, without cloud
bucket/key, token or signed URL. Metadata-only bundles state
`NO_RAW_EXPORT_SCOPE`; raw-inclusive bundles state
`UNSELECTED_RAW_ARTIFACTS_OMITTED`. The archive declares unselected raw and source
lab reports omitted. The mobile reader verifies exactly selected checks and
approved raw sources, each byte count/hash and all common ZIP safety limits.

## Delivery and cleanup

Completed status exposes only an authenticated same-origin download route,
bounded metadata, hash and size. A revoked/failed/expired owned job retains only
its minimal terminal receipt, without authority or download metadata. Download
requires current ownership, generation, account/family, study consent, exact
grant and source retention. One download per API process may buffer at most
64 MiB; busy returns retryable 429. Before response disclosure, the exact stored
S3 version/size/hash is verified and authority is re-admitted after network read.
Each 64 KiB chunk is re-admitted with the transaction closed before yield.
Revocation terminates the stream at the next boundary; at most one already
admitted chunk can be in flight. Already delivered bytes and copies cannot be
recalled. Authentication precedes Range/conditional rejection; resume is 416.
Cancellation before the first generator iteration releases the buffer slot.

Authority loss/expiry fences publication and removes logical delivery first.
Recurring owned-prefix cleanup removes all versions and delete markers and
reconciles late stale-worker writes; it retains next-sweep state and failure
observability rather than declaring erasure from one empty listing. Source raw
retention cleanup and account-generation erasure remain independent obligations.
Live PostgreSQL/S3 interleaving, AWS memory/load, physical-device evidence and
independently approved human grants require their own acceptance evidence.

## Concrete software verification

`services/api/tests/test_raw_export.py` ties the positive scope lifecycle to
`test_actual_distinct_release_freezes_exact_sources_and_public_scope`, stable
accepted customer intent and exact full ZIP/delivery to
`test_actual_http_async_worker_zip_download_replay_expiry_and_foreign_denial`,
pre-disclosure loss to
`test_delayed_http_download_discloses_no_bytes_after_current_authority_loss`,
between-chunk cutoff to
`test_admitted_asgi_download_stops_at_next_64k_chunk_after_revocation`, and
minimal terminal visibility to
`test_http_revoked_cleanup_has_minimal_terminal_receipt`. Actual backend-generated
fictional wire fixtures under `services/api/tests/fixtures/raw-export-v1` are
shared with mobile archive tests. These tests execute the software's typed
registry and HTTP/worker paths; their deliberately fictional principals/data do
not constitute independently authentic human approval or scientific evidence.
