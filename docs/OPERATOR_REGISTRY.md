# Operator registry administration

The canonical administration command is `python -m otgd.operator_cli` in
`services/api`. It provisions no study, participant, calibration or model by
default. The customer API and worker database role can read authority records;
they cannot submit, approve, release or rewrite them. Migration 003 creates the
version and decision tables without accepting existing generic registry rows as
new approvals. Historical records remain readable under their original rules.

Use a private operator host or approved database tunnel with verified TLS and
separately authorized maintenance credentials. Do not put database passwords in
arguments, commit them, expose the database publicly, or execute the command as
the generic ECS migration task and call that task the human reviewer.

## Submission and independent review

The typed JSON schemas are in [contracts/operator](../contracts/operator).
Regenerate them with `services/api/.venv/bin/python tools/generate_operator_contracts.py`.
Every submission names an immutable version, a bounded expiry and the reference
and digest of the evidence the independent reviewer must actually examine.
The command validates JSON, bounds, identity and semantics; accepting a string
reference does not validate a clinical study or replace review of the evidence.

| Kind | Material to review |
|---|---|
| `study` | Approved protocol, exact consent document/version/hash, invitation, explicitly authorized opaque account references, declared channel configuration IDs and optional model ID |
| `device` | P-256 public key and key ID, hardware/firmware, account inventory and approved protocols; private keys never enter this file |
| `calibration` | Device/hardware/firmware/channel tuple, model probability calibration, exact phone/OS/build/native timing tuple, or optical geometry including sampled ROI dimensions and extractor; these purposes cannot substitute for one another |
| `retention` | Study, exact optional purpose and notice text/hash/version, raw kinds, days, access roles, withdrawal behavior and exceptions; exceptions do not silently authorize a retention hold |
| `qualification` | Actual channel evidence, scientific material hash, and the exact configuration registry ID, version and normalized submitted content digest |
| `configuration` | Typed acquisition material, scientific hash, protocol/study, independently released qualification/retention, duration and phone or calibrated device compatibility |
| `method` | Explicit laboratory, collection, instrument and assay-basis scope supported by its evidence |
| `role` | Existing account, permitted laboratory operations and actual approved study membership |
| `model` | Complete research manifest, pinned immutable data-only artifact, frozen evaluation report, quality/co-use/compatibility policies, model calibration and native timing calibration when task inputs are required |
| `raw_export` | Exact participant/generation/study, independently approved export purpose and notice, permitted raw kinds, current retention version/hash and bounded copy lifetime/size; recording permission does not grant export |

The CLI defaults to a dry run: it executes validation inside a transaction and
rolls back. Its JSON result is a concrete reviewable plan with normalized content
and content SHA-256. Review that result before repeating with `--apply`.

For local software administration only:

```sh
cd services/api
uv run --no-sync python -m otgd.operator_cli --local-principal local:submitter submit study /tmp/study.json
uv run --no-sync python -m otgd.operator_cli --apply --local-principal local:submitter submit study /tmp/study.json
uv run --no-sync python -m otgd.operator_cli --apply --local-principal local:reviewer approve study STUDY_ID v1 --if-revision 1 --reason 'Reviewed exact protocol and consent evidence'
uv run --no-sync python -m otgd.operator_cli --apply --local-principal local:releaser release study STUDY_ID v1 --if-revision 2 --reason 'Authorized release after independent review'
uv run --no-sync python -m otgd.operator_cli --local-principal local:reviewer history study STUDY_ID
```

The three local labels represent fictional software-test identities, not AWS
authentication or real scientific approval. Local administration requires
PostgreSQL; SQLite is used only by isolated unit tests.

For QA or production, replace the local identity flag with both
`--expected-account ACCOUNT_ID` and `--expected-role-arn EXACT_STACK_OUTPUT_ARN`.
Use actual short-lived credentials for that role. The CLI verifies STS account
and assumed-role identity, resolves the canonical IAM role ARN and immutable
RoleId, and compares the caller's UserId. Different session names or fabricated
IAM path components do not create independent principals.

| Operation | Required cloud role name |
|---|---|
| Submit | `otgd-ENVIRONMENT-registry-submitter` |
| Approve | `otgd-ENVIRONMENT-registry-reviewer` |
| Release, retire, revoke | `otgd-ENVIRONMENT-registry-releaser` |
| Read history | Any of these three roles |

Operator roles require `sts:GetCallerIdentity`, `iam:GetRole` for these identities
and approved private maintenance database access. The infrastructure does not
invent assignments to real people. Independently assign the three roles to
different authorized people and review their IAM access; one person assuming
three roles is not independent scientific review. Privileged database
administrators remain trusted and can bypass the Python CLI; this workflow is
not a claim of protection against a malicious database administrator.

## Versions, release and retirement

Submitted normalized content, content digest, submission principal and time are
immutable. PostgreSQL triggers reject modification or deletion of those fields;
decision events are append-only. The workflow is `submitted → approved → active`.
Approval and release require distinct principals from the submitter and each
other. Every transition requires the exact revision and a bounded nonempty
reason. The receipt includes the resulting revision. Stale revisions fail with
`REGISTRY_REVISION_CONFLICT`; repeated submission of an existing version fails
with `REGISTRY_VERSION_EXISTS` and never replaces its content.

Release checks referenced current approvals, their integrity and expiry.
Release order is study, device where applicable, calibration, retention,
qualification, then configuration. A qualification can pin a prepared
configuration before that configuration is released. Its
`configuration_submitted_sha256` is the SHA-256 of RFC 8785 serialization of the
complete normalized Configuration DTO displayed by the submission dry run.
The separate scientific `sha256` covers `material`; for reaction tasks that is
the exact frozen native task configuration. A changed duration, firmware,
hardware, retention scope or version requires fresh matching qualification
even when the task's scientific material hash stays the same.

A new released version retires the previous active version atomically while
preserving its submitted body and all decisions. `retire` closes an active
version; `revoke` closes a submitted, approved or active version. Neither action
reopens a retired or revoked version. Use a new immutable version for renewal.
Expiration is enforced against the original deadline at every current read and
capture boundary; history shows `expired` and the effective state without
rewriting historical evidence. Active reads require the complete three-principal
decision ledger, exact pointer/content digest and typed content validity.

Registry mutations take an exclusive transaction advisory lock; runtime
reference validation takes its shared counterpart and retains row locks through
the transaction. Retirement therefore cannot race acceptance of an acquisition
under the same authority. Grants pin both the scientific configuration hash and
the submitted envelope digest/version and recheck them at start and settlement.

## Online acquisition and signed start

For real collection, save the immutable owned session context first. Its
configuration references contain the released configuration ID, version and
scientific material hash. Reader associations contain the actual binding,
hardware, firmware and observed boot identifier. Save a `started` attempt before
requesting `POST /v1/sessions/{session_id}/capture-authorizations`. The request
names the attempt, channel, configuration ID/hash and required reader binding.
Optional raw recording must be explicitly requested through `raw_recording_kind`;
cached preferences are not authority to record.

Within the grant's 60-second window, call
`POST /v1/sessions/{session_id}/capture-authorizations/{authorization_id}/start`
with `attempt_id`, `device_boot_id` and `device_nonce`. Readers require their
actual canonical UUID boot and fresh base64url nonce containing 32 bytes;
unbound phone acquisition uses null for the unavailable reader boot/nonce.
A changed frozen boot, revoked binding, retired configuration, changed approval
digest or changed raw choice refuses start.

The response's `server_start` contains an ECDSA P-256 SHA-256 DER signature over
the 22-byte domain `OTGD capture grant v1\0` followed by RFC 8785 JSON for `grant`.
It signs the owner/generation, session/attempt/authorization, reader binding/key/
boot/nonce, channel, duration limit, scientific and submitted configuration
hashes/version, context digest, issued/expiry times, single-use nonce and nullable
raw-recording permission. Verify it with a protected provisioned public key;
a public key supplied in a token is never trusted. The physical wire carries the
unchanged token as base64 to preserve its NUL domain.

QA and production use a pinned account/region KMS P-256 key. Local mode requires
a durable private P-256 file owned by the runtime user, mode 0600, with no symlink
or extra hard link. Migration binds its public fingerprint; missing or replaced
material fails readiness and signing. Provider failures return a controlled
retryable 503 and publish no authority.

Actual acquisition may start after the saved attempt's arm time. Terminal
metadata retains its original `armed_at`; acquisition timestamps must fit the
server-authorized interval. Optical native evidence additionally binds its run
ID to the attempt's record ID, authorization ID to the accepted start and times
to the terminal record. The server checks the exact camera/build/configuration
tuple and independently recomputes optical arithmetic. This does not prove
anatomical or physical onset validity. Callback response estimates remain
descriptive metadata until separately qualified.

The optional ESP32 ADC material names every pin, contact rule, sample rate,
deadline guard, scale and peak-extractor setting. A signed reader transport
requires the exact named acquisition driver in the build. Vendor saliva and
breath instruments require an implemented driver and reviewed method facts;
registry submission creates neither. Fixture pin assignments are not deployment
guidance, and fixtures contain no real scientific or hardware qualification.

Raw acquisition also requires a shipped codec. The optical adapter's bounded
grayscale ROI sequence uses `otgd_eye_roi_v1`; it is an octet-stream artifact,
not an MP4 recording. The bounded ADC ECG path uses `otgd_ecg_samples_v1`, with
at most 1,024 real signed samples and a configuration-pinned sample budget.
Feature-only ADC material sets `raw_sample_limit` to zero and `raw_encoding` to
null. A recording policy cannot enable a missing codec. Raw exports require a
separate current `raw_export` approval and explicit participant selection;
the initial release limits the entire archive to 50 MiB uncompressed and 64 MiB
compressed, and an approval may lower either bound.

Completion independently verifies device P-256 sample signatures and their
signed monotonic acquisition bounds for ECG. Optical completion matches decoded
ROI luminance to the accepted frame hashes and recomputes segmentation. These
checks run before publication; matching file length and SHA-256 alone do not
authenticate samples. The owned verification receipt pins the codec, original
attempt, exact S3 version, file digest, complete configuration digest and accepted
evidence digest. Current permission and version checks also apply to raw export.

`tests/test_raw_capture.py` includes mandatory PostgreSQL/LocalStack completion
cases. Supply a disposable PostgreSQL `OTGD_DATABASE_URL` and the explicit
loopback `OTGD_LIVE_S3_ENDPOINT`; missing live dependencies fail the check.
Each case uses its own UUID-named versioned bucket, an actual presigned HTTP
upload and exact returned S3 version, and then removes its own versions and
bucket. Fictional original device signatures are accepted; changing a sample
while supplying a matching file hash leaves the artifact quarantined. This
tests storage and software custody, not real AWS or physical sensor validity.

## Customer capability decisions

`GET /v1/me/capabilities` computes each channel independently from the verified
account/generation, current notice, approved study and exact current consent,
configuration, qualification, retention and any required signed binding and
device calibration. It returns current public configuration references and
specific refusal reasons. A valid registry row does not manufacture a software
adapter: `authorization_available`, `software_available` and `available` are
separate facts. Only adapters actually shipped in the server build can enable
collection. Model execution capability also distinguishes installed software
from the current acquisition and scientific model gates.

No production study, supported real phone/board, assay, model weights, human
timing evidence or reviewer approval is included in migration or deployment.
Fictional test approvals exercise the software only. Those real materials and
qualified operators must be provided and reviewed before a human research
release can be enabled.
