# Android feature: study access and consent

Normative integration: [shared application contracts](../../shared-contracts.md) and [platform contracts](../../platform-contract.md). These define the exact cross-feature DTOs, error states, generation/revocation rules, current-release limits, and implementation evidence.

## Purpose and traceability

Give an invited participant a clear view of authorized research access while keeping ordinary app use, identity, consent, capture permission, and model qualification separate. Upstream: PRD-004/005/018/028; SEC-002/003/005; VAL-001; MOD-008/010; HLD §§3/4.4/8; LLD §§7/9/11.

## Customer journey

Settings contains **Research access**. Signed-out customers see **Sign in to view invitations** and may continue using the local demo. Signed-in customers see only memberships returned by GET /v1/me/studies. An empty list displays **No research invitation is linked to this account**; there is no self-enrollment by typing a study ID.

Selecting an invitation shows study name, institution/contact from approved configuration, protocol version, purpose, expected measurements, collection burden, whether raw images/ECG are retained, retention period, withdrawal process, and current authorization state. Missing approved content prevents consent. The participant can scroll through the full approved text, open the contact information, **Decline**, or explicitly confirm **I consent to this study version**. Application terms are not prechecked research consent. Acceptance sends the exact consent version/hash and client acknowledgment time; the server stores its own receipt time.

After acceptance, show **Consent recorded** and a separate **Available measurements** list from capabilities. Consent does not turn an unqualified assay, optical stimulus, ECG circuit, or impairment model into an available feature. An expired or changed protocol displays **Review updated study information** before new acquisition. **Withdraw from study** explains that local study operations stop on the user's confirmed intent and server acceptance blocks future verified uploads; disconnected devices learn that change on reconnect. Qualified capture itself requires a fresh online start authorization in this release. The screen describes actual retained records and pending withdrawal status when offline. **Decline** closes the invitation without creating consent or changing the server membership; the invitation can be reviewed again.

## Engineering and lifecycle

Memberships and protocol documents are operator-provisioned, versioned records. States are invited/active/withdrawn/expired/suspended. Consent requires authenticated self ownership, active invitation, exact current protocol/notice hash, eligibility decision from the study system, and approved retention configuration. A capability response identifies authority, study/protocol/config IDs and hashes, expiry, permitted channels, raw upload permissions, and blocking reasons. Cache it encrypted for explanatory display only. It cannot authorize qualified acquisition while offline or after a restart/clock change.

GET /v1/me/studies; POST /v1/studies/{study_id}/consents; POST /v1/studies/{study_id}/withdrawals; GET /v1/me/capabilities. Writes are idempotent. The server checks current membership at fresh online capture authorization, upload, artifact ticket creation/completion, and finalization. Withdrawal intent immediately stops local active acquisition and persists its idempotent request before navigation. A preissued PUT may only create quarantined bytes until expiry; verification rechecks current authorization. Earlier consent alone does not override suspension or withdrawal. Clinical gate administration is separate from consumer APIs. The first release includes no preapproved real study, no enrolled real participant, and no active impairment model.

Android and iOS show equivalent complete consent text and controls with accessible reading order. Screen-reader access does not require checking a box merely because the user scrolled. Leaving the screen before acceptance saves no consent. Backgrounding a consent page may resume reading; backgrounding a measurement follows that measurement's stricter rules.

## ADDED Requirements

### Requirement: AND-STUDY-001 Show only authorized memberships
The service SHALL derive invitations and memberships from authenticated ownership and MUST NOT allow a submitted study ID to create enrollment.

#### Scenario: Invited customer opens research access
- **GIVEN** one operator-provisioned invitation for the signed-in account
- **WHEN** memberships are requested
- **THEN** the app displays that invitation and its actual status.

#### Scenario: Customer guesses another study UUID
- **GIVEN** no membership in the requested study
- **WHEN** its consent or capability route is requested
- **THEN** access is refused without disclosing another participant's data.

### Requirement: AND-STUDY-002 Bind consent to complete approved content
Consent SHALL reference the exact protocol/consent version and digest, scope, raw-data policy, and retention terms that were presented.

#### Scenario: Current approved consent is accepted
- **GIVEN** an eligible active invitation and complete approved document
- **WHEN** the participant explicitly accepts
- **THEN** a durable receipt records the version, digest, authenticated subject, client time, and server receipt time.

#### Scenario: Protocol changes while the page is open
- **GIVEN** the displayed consent version is no longer current
- **WHEN** acceptance is submitted
- **THEN** the server rejects the stale version and the app loads the updated document without transferring the old acceptance.

### Requirement: AND-STUDY-003 Separate consent from capability qualification
The service MUST compute capture/upload/inference permissions independently of an accepted consent record and MUST return explicit reasons for unavailable channels.

#### Scenario: Consent exists but optics remain unqualified
- **GIVEN** accepted consent and no approved optical configuration
- **WHEN** the app requests eye capture
- **THEN** passive guidance or an unavailable state is shown and no participant stimulus is emitted.

#### Scenario: Client edits capability JSON
- **GIVEN** a locally modified available flag
- **WHEN** an upload or research request reaches the backend
- **THEN** server-owned qualification and membership checks still prevent unauthorized operation.

### Requirement: AND-STUDY-004 Require fresh authorization for qualified capture
Qualified capture SHALL require a fresh online server authorization in this release. Cached availability SHALL be explanatory only and MUST NOT enable qualified capture while offline, after restart, or through wall-clock changes.

#### Scenario: Cached scope cannot authorize offline capture
- **GIVEN** a cached available scope covering the device/configuration/channel
- **WHEN** qualified capture is requested offline
- **THEN** the app requires reconnection; local uncalibrated practice remains a separately labeled permitted path.

#### Scenario: Authorization expires offline
- **GIVEN** the phone was restarted or its wall clock was rolled back
- **WHEN** new qualified capture is requested
- **THEN** the app asks for reconnection and preserves existing records without acquiring under stale permission.

### Requirement: AND-STUDY-005 Make withdrawal effective for new operations
Withdrawal intent SHALL stop new local study operations and settle active acquisition immediately; its durable request SHALL show pending while offline. Server acceptance SHALL block later verified uploads/finalization and initiate the declared data process.

#### Scenario: Participant withdraws
- **GIVEN** active study access
- **WHEN** the participant confirms withdrawal while offline
- **THEN** local capture stops, the exact request is retained pending, and server completion is not claimed; later acceptance blocks verified uploads and returns the receipt.

#### Scenario: Old upload ticket is used after withdrawal
- **GIVEN** an artifact ticket issued before withdrawal
- **WHEN** upload completion is requested afterward
- **THEN** authorization is rechecked and the object cannot become a verified research artifact through the stale ticket.

### Requirement: AND-STUDY-006 Preserve truthful study absence
Without an approved configured study, the app SHALL show an empty/unavailable research state and MUST NOT ship a fictional invitation as a real one.

#### Scenario: Fresh production environment
- **GIVEN** no approved study records
- **WHEN** research access opens
- **THEN** no research capture or prediction is offered.

#### Scenario: Synthetic local fixture
- **GIVEN** a local development study fixture
- **WHEN** it is displayed
- **THEN** its synthetic identity and environment are explicit and its permissions cannot be reused in QA/prod.
