# Independently authorized raw copies

The canonical application can export explicitly selected verified eye recordings
and ECG waveforms when an independently released participant-copy authority
exists. Ordinary export remains metadata-only. Recording/upload consent, a
device qualification, study acceptance or deployment never grants raw-copy
permission. The software ships no real approved grant or recorded human data.

## Operator prerequisite

Read [OPERATOR_REGISTRY.md](OPERATOR_REGISTRY.md) and use the canonical
`contracts/operator/raw_export.schema.json`. Supply actual approved evidence,
one exact participant account/generation/study, current retention ID/version/JCS
hash, eye-video/ECG-waveform kinds, literal
`participant_requested_raw_export` purpose, exact notice and its UTF-8 SHA-256,
expiry, copy lifetime and byte caps. Notice is at most 16 KiB; purpose text is at
most 4096 characters. The complete uncompressed export is at most 50 MiB and
the ZIP at most 64 MiB; grants may lower these limits. An individual recording
larger than the approved total cannot be selected. Privileged source laboratory
reports are not supported by this participant-copy scope.

Different authorized people must use the stack's verified submitter, reviewer
and releaser roles. On an approved private maintenance host with the locked API
environment and TLS database connection, each independently executes its own
operation, substituting actual identifiers, expected account and exact role ARN:

```bash
uv run --project services/api --no-sync python -m otgd.operator_cli --apply \
  --expected-account ACCOUNT_ID --expected-role-arn EXACT_SUBMITTER_ROLE_ARN \
  submit raw_export /secure/path/approved-raw-export.json

uv run --project services/api --no-sync python -m otgd.operator_cli --apply \
  --expected-account ACCOUNT_ID --expected-role-arn EXACT_REVIEWER_ROLE_ARN \
  approve raw_export AUTHORIZATION_ID VERSION --if-revision 1 \
  --reason 'Actual independently documented decision reference'

uv run --project services/api --no-sync python -m otgd.operator_cli --apply \
  --expected-account ACCOUNT_ID --expected-role-arn EXACT_RELEASER_ROLE_ARN \
  release raw_export AUTHORIZATION_ID VERSION --if-revision 2 \
  --reason 'Actual independently documented release reference'
```

Without `--apply` the CLI validates without committing. Use the actual returned
revision for later transitions; the example numbers describe the initial
submit/approve lifecycle. Session names do not establish different principals.
Do not pass secrets or participant health data in command arguments/reasons.

## Customer/API journey

The signed-in export form starts with raw inclusion off. Current choices come
from `GET /v1/privacy/raw-export-scopes`: four purposes per page, SHA
`next_cursor`, resumed by `authorization_cursor`. To browse source pages for one
purpose, send exact `authorization_id` and UUID `artifact_cursor` returned in
`artifacts_next_cursor`. These cursors scan all rows; a page with no current
eligible rows can still have a next cursor. Responses are bounded to 512 KiB.
The API never returns object bucket/key, presigned download URL or another
participant's artifacts.

The customer reviews the exact export purpose, notice, retention deadline and
recording/check identity, chooses eligible artifacts explicitly and checks a
fresh separate confirmation. The persisted request retains its acknowledgement,
idempotency key and data generation across retry. Changing purpose/account/
generation resets unfinished choices. Its body is:

```json
{
  "selection": {"kind": "single", "session_ids": ["OWNED_CHECK_UUID"]},
  "format": "json_zip",
  "include_raw": true,
  "raw_scope": {
    "authorization_id": "ACTUAL_AUTHORIZATION_ID",
    "authorization_version": "ACTUAL_VERSION",
    "authorization_sha256": "EXACT_RELEASED_CONTENT_SHA256",
    "export_notice_version": "ACTUAL_NOTICE_VERSION",
    "export_notice_sha256": "EXACT_NOTICE_UTF8_SHA256",
    "acknowledged_at": "ACTUAL_UTC_TIME_WITH_Z",
    "confirmed": true,
    "artifact_ids": ["EXPLICIT_OWNED_ARTIFACT_UUID"]
  }
}
```

This illustrative body is not executable approval: use actual UUIDs and SHA-256
values from the current owned response. `Authorization`, `X-Data-Generation` and
`Idempotency-Key` are required. Acknowledgement must be no older than ten minutes
and no more than five seconds in the future. There are at most 500 selected
checks and 128 explicit raw sources. No selected source may be unverified,
foreign, outside the selected check/study, expired or from another generation.
Current study and separate effective raw consent remain required throughout.

Acceptance returns a pending job, original selection and hash-bound `raw_export`
source tuple. Poll `/v1/privacy/jobs/JOB_UUID`. A completed job exposes only its
authenticated same-origin download route; a copied route is not a credential.
Job/manifest raw tuples bind source UUID, check UUID, raw kind, exact S3 version,
size, hash, media type and retention deadline. The mobile archive inspector
rejects extra/replaced sources even when an altered ZIP was internally rehashed.
ZIP paths are `raw/eye_video/ARTIFACT_UUID.bin` or
`raw/ecg_waveform/ARTIFACT_UUID.bin`. Structured evidence and exclusions remain
visible. Download expiry is the earliest approved copy lifetime, 24 hours,
authority expiry and selected source retention deadline.

## Revocation, protected delivery and runtime limits

Grant retirement, raw revocation, study withdrawal, account retirement/deletion
or retention expiry denies new reads, replay and publication. A failed/revoked/
expired owned job retains minimal status without raw grant/download metadata.
Recurring version-aware cleanup erases revoked output prefixes, including late
stale-worker arrivals; an earlier empty listing is not final physical proof.

The gateway buffers one verified archive per API process, at most 64 MiB, after
checking actual S3 VersionId, length and SHA-256. It rechecks current identity/
generation/consent/grant/sources after storage retrieval and before every 64 KiB
delivery chunk, outside database locks. Revocation stops the next chunk; already
sent or in-flight bytes and downloaded copies cannot be recalled. Other download
requests receive retryable 429 while the slot is occupied. Cancellation before
the first chunk releases capacity. Authenticated ranged/conditional requests
return 416. Responses are private/no-store.

The shared SDK has a five-second connection timeout, 30-second socket-read
timeout and bounded retries. Socket timeout is not an overall elapsed-time
deadline: continuously trickling storage can retain the one download slot.
Current software bounds memory/disclosure; a strict transport wall-clock cutoff
and AWS slow-source/load acceptance remain explicit operational limitations.

## Verification and evidence limits

From the repository root:

```bash
UV_CACHE_DIR=/tmp/otgd-uv-cache uv run --project services/api --no-sync \
  python -m pytest services/api/tests/test_raw_export.py -q \
  --cov=otgd.raw_export --cov-report=term-missing
```

The suite uses real typed registry lifecycle, signed JWT HTTP routes, worker
assembly, bounded storage doubles and disposable SQLite. It tests explicit
purpose, exact immutable source/receipt hashes, current consent and generations,
replay, output limits, delayed pre-disclosure revocation/expiry/deletion,
between-chunk cutoff, capacity/cancellation, pagination and recurring late
cleanup. [Fictional wire fixtures](../services/api/tests/fixtures/raw-export-v1/README.md)
come from actual backend execution for mobile interoperability. They establish
software behavior only. PostgreSQL/LocalStack raw interleavings, AWS QA memory/
load and slow-source delivery, physical codec/device qualification and actual
independent human grants require separate evidence and all final merge gates.
