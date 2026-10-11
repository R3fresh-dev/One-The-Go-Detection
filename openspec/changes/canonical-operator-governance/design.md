# Design

`RegistryVersion` preserves normalized submitted JSON, RFC 8785 SHA-256,
submitter, time and immutable version identity. `RegistryEvent` retains each
decision, principal, previous/resulting state, revision, reason and request ID.
`Registry` is only the active read pointer. PostgreSQL enforces immutable
submitted content and append-only decisions. Migration creates no approvals.

The CLI verifies cloud STS identity against independently resolved IAM RoleId and
canonical ARN, binds named operator duty to the command, rejects ambient endpoint
overrides and defaults to transaction rollback. The independent role assignment
must be to different authorized people; administrator database access is a
trusted operational boundary rather than proof of human independence.

An exclusive transaction advisory lock encloses operator mutations; runtime
registry validation holds the shared counterpart and reference row locks. Every
active lookup validates typed content, the three distinct decision principals,
pointer/content identity and current expiry. A configuration's scientific hash
covers typed material; qualification additionally names the exact normalized
registry ID, version and submitted digest. A duration/retention/device scope
change cannot reuse an approval for the old envelope.

Capability responses separate current authorization from actually implemented
software. Public references contain configuration identity/hash, submitted
digest, expiry, protocol, study and supported phones, not internal evidence or
participant inventories. Model execution remains separately gated by its
complete manifest, artifact, policies, evaluation and applicable qualifications.

## Verification anchors

The generated contracts under `contracts/operator/` define each accepted body;
`tools/generate_operator_contracts.py` regenerates them from the strict typed
schemas. Operators run `python -m otgd.operator_cli` with explicit local aliases
or verified cloud account/role flags. The command returns the normalized result,
verified principal and `dry_run`/`applied` mode. Accepted lifecycle receipts expose
the registry version, state, revision and submitted hash; history reconstructs
the original body and append-only decisions.

`test_operator_governance.py` exercises immutable submission/replay, all three
independent duties, canonical IAM RoleId/path matching, ignored ambient SDK
endpoints, dry-run rollback, expiry/retirement/revocation, exact configuration
proofs, current customer capability and approval replacement while a grant is
outstanding. Its PostgreSQL-marked cases execute migration replay and direct
SQL mutation attempts against the actual immutable-version and append-only-event
triggers, and observe an actual advisory-lock wait while retirement serializes
behind an acceptance transaction. Unit aliases and evidence are visibly fictional software fixtures and
cannot qualify a real study, assay, phone or model.

`capture_signing.py` and `contracts/application/ServerStartToken.schema.json`
define the domain-separated signed start. Maintenance anchors the protected
public fingerprint; local private-file custody and cloud KMS account/region/key
identity are checked before publication. Firmware consumes the unchanged token
through base64 wire encoding and verifies the independently provisioned signer.
`test_capture_signing.py` covers signature alteration, signed optional raw
choices, missing/replaced/symlink/FIFO keys and controlled provider failure.
Actual HTTP software fixtures under `apps/mobile/testfixtures/backend-*-capture-authorization.json`
carry only fictional key and approval material for cross-language verification.

Valid optical runs require `validate_optical_attempt`: accepted authorization,
attempt record ID and clocks must match before independent arithmetic and camera
tuple validation. Missing pre-start evidence retains reason/arm lineage with
null acquisition features. Callback response fields do not qualify anatomical
or physical response merely because descriptive arithmetic is reproduced.

`raw_capture.py` accepts only bounded implemented codecs. Completion reads the
exact S3 version outside the account transaction and requires the provider's
returned version, length, media type and file hash to match. Inside the commit
transaction it rechecks current recording/upload purpose, accepted attempt,
configuration and started authorization. ECG chunks retain device signatures
over their exact scope, indices and monotonic acquisition bounds; optical ROI
pixels reproduce the accepted frame hashes and segmentation. A minimal owned
`raw_verification` record pins the object version and accepted evidence hash
before publication. Current raw-export admission requires that receipt.
`test_raw_capture.py` exercises authentic and altered signatures, exclusive end
times, bad returned versions, bounded sample clocks and actual HTTP completion;
the positive and matching-file-hash forgery cases also pass on disposable
PostgreSQL. The separately marked live cases create a unique versioned
LocalStack bucket, upload through the actual conditional presigned HTTP PUT,
and complete against the actual pinned S3 version. Original signatures publish
an owned receipt; altered sample values with a matching file hash remain
quarantined. The tests purge only their own object versions and bucket, and
fail if PostgreSQL or an explicit loopback `OTGD_LIVE_S3_ENDPOINT` is absent.
These are synthetic software custody checks, not hardware evidence or actual
AWS verification.

`authority_lock` serializes all maintenance mutations with shared runtime reads;
`released_version` additionally locks the referenced version and verifies
content, current expiry, pointer identity and independent decision history.
`main.py` pins full approval identity on authorization and rechecks it at start
and attestation acceptance. These checks remain inside the same transaction as
the owned scientific write. The full mandatory merge gate must be rerun on the
final revision; focused tests alone do not qualify deployment or hardware.
