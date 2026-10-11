## ADDED Requirements

### Requirement: OPERATOR-AUTHORITY-001 — Typed immutable submissions

Operator submissions SHALL require separately authorized maintenance
administration. Study, device, calibration, retention, qualification,
configuration, method, role, model and raw-export submissions SHALL reject unknown fields,
nonfinite values, unsupported types, expired material and payloads over 256 KiB.
The normalized body, version, principal, time and RFC 8785 SHA-256 SHALL remain
immutable. A repeated version SHALL fail and SHALL NOT replace submitted content.

#### Scenario: Alteration of accepted submission
- **GIVEN** a submitted version with a recorded canonical digest
- **WHEN** an administrator attempts to update its JSON, digest, version or submitting identity
- **THEN** PostgreSQL rejects the update and the original body remains reconstructable

#### Scenario: Normalized submission and same-version retry
- **GIVEN** a typed study body and a separately authorized submitter
- **WHEN** the submitter applies its first immutable version
- **THEN** the receipt exposes revision one, the exact normalized body and its canonical digest
- **AND** replaying the same version fails without replacing its body or creating a second submission decision

### Requirement: OPERATOR-AUTHORITY-002 — Independent authenticated decisions

Approval SHALL require a verified principal distinct from submission. Release
SHALL require a third principal distinct from both. QA/prod commands SHALL bind
STS account/session identity to the canonical IAM RoleId and ARN, reject
fabricated role paths and ambient SDK endpoint overrides, and require the named
submitter/reviewer/releaser role appropriate to the operation. Local aliases
SHALL be explicitly fictional and SHALL NOT count as cloud or scientific proof.

#### Scenario: Claimed role paths for one credential
- **GIVEN** one verified assumed-role credential and its actual IAM RoleId
- **WHEN** the caller supplies three different claimed path prefixes for that same role
- **THEN** every noncanonical path is rejected and it cannot self-approve or self-release

#### Scenario: Three authenticated duties release approved material
- **GIVEN** a submission under the named submitter role and an independent reviewer role
- **WHEN** the reviewer approves revision one and the independently authenticated releaser releases revision two
- **THEN** the active read validates three distinct canonical principals and the same submitted content hash
- **AND** the accepted history contains the exact request identity and reason for each decision

### Requirement: OPERATOR-AUTHORITY-003 — Reviewable atomic lifecycle

The CLI SHALL default to validated rollback. Applied transitions SHALL require
current revision and reason. Append-only decisions SHALL bind submitted digest,
request ID and principal. Release SHALL atomically retire the previous version.
Terminal versions SHALL never reopen; renewal SHALL create an immutable version.
Current reads SHALL deny expiry while history preserves its original deadline.

#### Scenario: Stale release or revoked configuration
- **GIVEN** a reviewed version whose revision changed or whose approval was revoked
- **WHEN** an operator releases it using an earlier revision
- **THEN** the command fails and customer acquisition remains unavailable

#### Scenario: Dry-run, applied renewal and terminal history
- **GIVEN** a valid typed renewal and its complete current dependencies
- **WHEN** the CLI runs without --apply
- **THEN** it displays the validated result and rolls back all registry changes
- **WHEN** three authorized operators submit, approve and release the renewal with --apply
- **THEN** the previous active version is atomically retired and both immutable bodies remain in history
- **AND** retiring the renewal immediately removes current authority while preserving accepted decisions

### Requirement: OPERATOR-AUTHORITY-004 — Exact scientific and scope identities

A configuration SHALL contain typed acquisition material whose canonical hash
matches its scientific hash. The reaction material SHALL equal the frozen
implemented native contract. Qualification SHALL additionally bind the registry
configuration ID, version and complete normalized submitted digest. Release
SHALL resolve active study, retention, device, calibration and method records
and reject mismatched protocol, hardware, firmware, device key or assay scope.

#### Scenario: Changed retention or duration with old proof
- **GIVEN** an approved configuration and qualification for version one
- **WHEN** version two changes duration or retention but retains the task material hash and old proof
- **THEN** release fails because the qualification does not cover the new submitted version/digest

#### Scenario: Exact reviewed configuration and device tuple
- **GIVEN** approved study and retention versions, an exact configuration proof, and a device/calibration with matching key, hardware, firmware and channel
- **WHEN** an independent releaser releases the configuration
- **THEN** runtime validation resolves the exact active versions and accepts the matching configuration identity
- **AND** its material hash and complete submitted hash remain separately available for acquisition fencing

### Requirement: OPERATOR-AUTHORITY-005 — Current customer capabilities

The server SHALL derive current capability from verified owner/generation,
account, notice, approved study/invitation, exact consent, configuration,
retention and required device binding/calibration. It SHALL distinguish shipped
software, authorization and collection availability, expose public references
and refusal reasons. Approval SHALL NOT invent absent software or clinical proof.

#### Scenario: Current approved task collection
- **GIVEN** an active account, current notice and exact consent to an independently released study with approved task configuration
- **WHEN** capabilities are requested on a build containing the matching native task adapter
- **THEN** task collection is available with its exact public configuration references
- **AND** retirement, expiry, changed consent or account generation closes the applicable capability

#### Scenario: Authorized configuration without a shipped adapter
- **GIVEN** current consent and an independently released device configuration with a matching owned binding
- **WHEN** its declared transport is absent from the shipped server/client adapter inventory
- **THEN** authorization availability and software availability are reported separately
- **AND** acquisition is denied with HUMAN_ADAPTER_UNIMPLEMENTED rather than accepting fabricated measurements

### Requirement: OPERATOR-AUTHORITY-006 — Capture approval fencing

Acquisition grants SHALL pin scientific material hash and registry version/content
digest. Start and settlement SHALL recheck current approvals, current owner and
device binding through a transaction-held reference lock. Registry retirement
SHALL serialize with runtime acceptance. A restored suspended scope SHALL remain
closed until independent recovery authority permits reconciliation.

#### Scenario: Approval replaced while a grant is outstanding
- **GIVEN** an issued acquisition grant for one approved configuration envelope
- **WHEN** a newly reviewed envelope replaces it before start
- **THEN** the old grant cannot start even when the scientific task hash is unchanged

#### Scenario: Current grant starts before an approval retirement
- **GIVEN** a current owned started attempt and an issued grant pinned to the active configuration envelope
- **WHEN** start commits while holding the shared registry authority lock
- **THEN** the server records its actual start anchor and exact pinned approval identity

### Requirement: OPERATOR-AUTHORITY-007 — Signed scoped start

The server SHALL sign fresh start authority with its separately pinned P-256
key. The signed body SHALL bind owner/generation, session/attempt, channel,
duration, configuration and context hashes, reader binding/boot/nonce, expiry
and optional recording permission. Readers SHALL verify the protected signer
and refuse unsigned, changed, expired or reused authority before acquisition.

#### Scenario: Owned reader starts under current signed authority
- **GIVEN** current independent approvals and an owned signature-proven reader binding in the frozen context
- **WHEN** start supplies the exact frozen boot and fresh reader nonce
- **THEN** the server emits a verifiable domain-separated token for the approved channel and duration
- **AND** feature-only collection has signed raw-recording permission null

#### Scenario: Signing authority fails or unsigned raw choice changes
- **GIVEN** a bound signing key and an issued current acquisition grant
- **WHEN** the key is missing, replaced, unavailable or produces an invalid signature
- **THEN** readiness or start fails closed and no acquisition authority is published
- **WHEN** a caller changes signed raw permission, channel or duration in a valid token
- **THEN** the signature fails and the reader cannot acquire under the changed scope

### Requirement: OPERATOR-AUTHORITY-008 — Optical accepted-run identity

Valid optical evidence SHALL match its current started authorization, attempt
record identity, acquisition times and approved camera/configuration tuple.
The server SHALL recompute descriptive arithmetic. Pre-start failure SHALL
retain arm lineage and a reason with absent native evidence and null features;
it SHALL NOT invent clock, frame, physical-onset or anatomical-response proof.

#### Scenario: Current optical run retains descriptive evidence
- **GIVEN** an owned started optical authorization under an independently released configuration
- **WHEN** the matching actual native run settles with bounded camera/frame evidence
- **THEN** the server binds its run and authorization identities and independently checks its arithmetic
- **AND** callback-relative response metadata remains separate from physically qualified projection fields

#### Scenario: Pre-start failure or relabeled camera run
- **GIVEN** a saved arm attempt and a camera that fails before acquisition clocks or frames exist
- **WHEN** the client settles a reason-bearing invalid attempt with native evidence absent
- **THEN** the server preserves its original arm time and null acquisition features
- **WHEN** valid evidence claims another run, authorization or acquisition interval
- **THEN** acceptance fails rather than assigning that evidence to the current attempt
- **WHEN** an operator subsequently retires or replaces that approval
- **THEN** later settlement cannot use the stale grant and no accepted scientific snapshot is silently rewritten

### Requirement: OPERATOR-AUTHORITY-009 — Authenticated raw publication

Participant raw artifacts SHALL remain quarantined until bounded codec bytes
match the accepted owned acquisition and current signed recording permission.
ECG sample chunks SHALL independently verify device signatures, signed clock
bounds, configuration, sequence and sample budget. Optical ROI bytes SHALL match
accepted frame digests and recomputed segmentation. Verification SHALL pin the
exact object version and digest; file hashes alone SHALL NOT authenticate samples.

#### Scenario: Original device samples are published under current permission
- **GIVEN** exact released configuration, explicit current recording/upload consent and an owned started authorization
- **WHEN** the original signed ECG chunks or optical ROI bytes match the accepted acquisition ledger
- **THEN** completion records the exact immutable object version, codec and evidence digests before marking the artifact verified
- **AND** research eligibility remains separate from raw transport verification

#### Scenario: Matching file hash contains forged or relabeled samples
- **GIVEN** a raw artifact whose uploaded bytes match its declared file hash and length
- **WHEN** a sample signature, signed clock, owner, capture identity, frame digest or approved sample budget is invalid
- **THEN** completion fails and the artifact remains quarantined without a verification receipt
- **AND** a historical verified state without an owned matching codec receipt cannot authorize raw export
