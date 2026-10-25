## ADDED Requirements

### Requirement: STORE-001 Define separate real-device release targets
The application SHALL define explicit QA-store and production store profiles with Android AAB and iOS device IPA targets, fixed QA/prod identities, remote unique build numbering and fictional preview disabled. Ordinary web/local/simulator builds SHALL not require an Expo account merely because store tooling exists.

#### Scenario: A real store candidate is planned
- **GIVEN** the selected QA-store or production profile
- **WHEN** its platform configuration is resolved
- **THEN** device artifact type, environment/package and version policy are explicit.

#### Scenario: A guest archive is offered for store release
- **GIVEN** a local/guest/simulator artifact or incompatible package
- **WHEN** store admission runs
- **THEN** it refuses rather than relabeling the artifact.

### Requirement: STORE-002 Validate actual project and backend identity
Store operations SHALL require a bounded nonsecret external config and verify the genuine Expo project/owner/slug, actual admitted API/issuer/client, exact native redirect and source environment. Production redirect SHALL be otgd://oauth/callback; QA SHALL use otgd-qa://oauth/callback. Ambient/demo/public origins SHALL not replace the verified backend.

#### Scenario: Cloud identity matches the compiled app
- **GIVEN** current project metadata and admitted cloud outputs including the exact callback
- **WHEN** build/submit admission runs
- **THEN** the candidate uses those exact public identity values.

#### Scenario: Production lists the wrong redirect
- **GIVEN** otgd-prod://oauth/callback or a foreign project/backend/callback
- **WHEN** admission checks the production package
- **THEN** it fails before build or submission.

### Requirement: STORE-003 Stage only admitted immutable source
Build/submission SHALL recheck trusted live gate provenance for every mandatory job in the exact committed aggregate workflow and its reusable workflows (including platform container-runtime verification where required), independently signed backend/QA authority and the exact source. Build staging SHALL contain only committed reviewed files and pinned dependency locks; it SHALL preserve the development checkout and omit untracked credentials, unrelated drafts and generated guest artifacts.

#### Scenario: Exact source and genuine release evidence agree
- **GIVEN** the allowed trusted GitHub release event and current signed backend/QA binding
- **WHEN** source is staged outside the development checkout
- **THEN** the provider receives only the admitted immutable tree.

#### Scenario: A local JSON or stale successful run is substituted
- **GIVEN** missing jobs, wrong commit/project, unsupported release event or edited evidence
- **WHEN** build/submit admission runs
- **THEN** no provider mutation occurs.

### Requirement: STORE-004 Provide a mutation-free plan
The Python store tool SHALL provide plan/build/submit/status with explicit platform and environment. Plan SHALL validate nonsecret inputs and list stages without network, signing, build, upload or secret-value output. It SHALL identify genuine external prerequisites rather than pretending to provision accounts.

#### Scenario: An operator reviews the intended command
- **GIVEN** a valid nonsecret store configuration
- **WHEN** plan runs without service credentials
- **THEN** the explicit stages and external requirements are returned without mutation.

#### Scenario: An invalid or ambiguous target is supplied
- **GIVEN** opposite environment, missing platform or placeholder identity
- **WHEN** plan runs
- **THEN** validation fails before a provider command.

### Requirement: STORE-005 Pin provider tooling and scope credentials
Store child commands SHALL require the reviewed exact EAS CLI version, retain verified proxy/CA transport, set explicit approved build identity and exclude unrelated cloud/GitHub/database credentials and arbitrary Node preloads. Genuine Expo/signing/store access SHALL remain in protected external bindings/files and never be logged or included in build source.

#### Scenario: Approved credentials and exact CLI are available
- **GIVEN** verified pinned tooling and scoped genuine provider credentials
- **WHEN** build/submission starts
- **THEN** the child receives only its required authentication and transport.

#### Scenario: Tooling or credential state is unavailable
- **GIVEN** a different CLI, missing genuine signing/account access or a Node preload
- **WHEN** the operation starts
- **THEN** it refuses or excludes the unapproved setting without inventing a build.

### Requirement: STORE-006 Bind builds to explicit provider records
Build SHALL select one explicit platform/profile and record actual returned build UUID, project, source/environment, version and provider state. A successful request SHALL not be reported as a completed artifact before official metadata confirms the expected finished build. Rechecking SHALL reject foreign, failed, pending or mismatching metadata.

#### Scenario: The provider completes the selected build
- **GIVEN** matching official finished-build metadata
- **WHEN** the completion receipt is written
- **THEN** it identifies the actual build UUID/version and admitted project/source.

#### Scenario: Build execution merely starts
- **GIVEN** an accepted request with pending/failed/wrong-project output
- **WHEN** completion is assessed
- **THEN** no finished artifact or downloadable store app is claimed.

### Requirement: STORE-007 Submit only the exact verified candidate
Submission SHALL explicitly select platform and a previously admitted build UUID, reverify current project/release/build authority, and use the exact provider ID rather than latest or an arbitrary local artifact. QA-store and production commands SHALL preserve matching compiled package/callback and never infer authority from a hand-edited receipt.

#### Scenario: A genuine exact candidate is submitted
- **GIVEN** the current finished-build UUID and real matching store record
- **WHEN** explicit submission is requested
- **THEN** that exact candidate is sent and provider observations are recorded.

#### Scenario: Another build is substituted
- **GIVEN** latest selection, a foreign UUID or altered receipt/metadata
- **WHEN** submission admission runs
- **THEN** it refuses before upload.

### Requirement: STORE-008 Separate submission from public availability
Submission SHALL remain deliberate and non-public: Android uses the declared internal or production track with draft/not-sent-for-review status, and iOS SHALL not automatically schedule public release. Receipts SHALL distinguish build finished, submission accepted, platform processing, tester availability, review and public publication; unavailable provider status SHALL remain unknown.

#### Scenario: An upload request succeeds
- **GIVEN** a successful provider submission request
- **WHEN** status is reported
- **THEN** it reports only actual observed submission/processing evidence and no public-download claim.

#### Scenario: Apple or Google has not approved delivery
- **GIVEN** processing/review/tester/enrollment or first-upload work remains
- **WHEN** the operator asks for installation
- **THEN** documentation names the required platform step without inventing a store URL or completed publication.

### Requirement: STORE-009 Preserve bounded operation receipts
Each operation SHALL preserve prior receipts, use bounded stable regular configuration/evidence inputs, omit secret values, record exact source/project/platform/provider IDs and distinguish actual remote checks from local fixtures. Failure SHALL exit nonzero without a fabricated successful receipt or inferred rollback.

#### Scenario: A successful operation is retained
- **GIVEN** actual matching provider observations
- **WHEN** a receipt is created
- **THEN** it records the performed stage and identity without overwriting earlier evidence.

#### Scenario: An external stage fails
- **GIVEN** denied credentials, wrong metadata or failed build/upload
- **WHEN** execution stops
- **THEN** failure is explicit and earlier provider work is not falsely described as rolled back.

### Requirement: STORE-010 Inspect the actual signed device artifact
Store admission SHALL inspect the actual bounded candidate archive, native platform/package/version, compiled project/backend/guest configuration and independently expected signer. Metadata alone SHALL not admit bytes; a substituted artifact or unsupported verifier SHALL refuse submission.

#### Scenario: A genuine device candidate matches authority
- **GIVEN** the exact provider build bytes, reviewed signer and supported verifier
- **WHEN** inspection executes
- **THEN** the signed receipt binds its actual digest and observed native/configuration/signing metadata.

#### Scenario: Metadata describes a different binary
- **GIVEN** a simulator IPA, unsigned/foreign AAB, wrong package/version/backend/guest marker or different signer
- **WHEN** binary inspection runs
- **THEN** metadata alone cannot admit it and no submission occurs.

### Requirement: STORE-011 Fence uncertain submission outcomes
Before an external submission call, the tool SHALL durably preserve a signed exact-build/platform/project intent without overwriting existing outcomes. An interrupted/unknown result SHALL remain uncertain; retries SHALL require the exact provider submission UUID and perform read-only reconciliation rather than repeat the upload. Actual accepted/failed provider state SHALL remain separate from store availability.

#### Scenario: The provider accepted a request before interruption
- **GIVEN** a durable signed intent and an uncertain CLI outcome
- **WHEN** the operator supplies the actual submission UUID for reconciliation
- **THEN** the tool queries that exact matching provider record without another upload.

#### Scenario: The operator repeats an unknown upload without identity
- **GIVEN** an existing pending intent and no matching provider submission record
- **WHEN** submission is retried
- **THEN** it refuses duplicate mutation and preserves the uncertainty.

### Requirement: STORE-012 Verify the complete Android upload signature
Android admission SHALL require an AAB, the independently selected upload certificate and valid signatures covering every meaningful archive entry. A jarsigner success string alone SHALL be insufficient. Manifest decoding SHALL use the pinned verified bundletool and confirm actual package/version. Play's later app-signing identity SHALL not be confused with this upload certificate.

#### Scenario: A complete registered-upload candidate is supplied
- **GIVEN** an AAB with the expected upload certificate and all payload entries signed
- **WHEN** actual signature and manifest inspection runs
- **THEN** the admitted digest/package/version/signer are recorded.

#### Scenario: Unsigned payload is appended to a signed archive
- **GIVEN** a previously signed JAR/AAB containing newly appended unsigned payload
- **WHEN** jarsigner returns a general success with incomplete entry coverage
- **THEN** admission still rejects the candidate before submission.

### Requirement: STORE-013 Verify genuine iOS device signing and provisioning
iOS admission SHALL require an iPhoneOS device Mach-O, exact bundle/version/team, matching store provisioning and actual code-signature/certificate validation using supported macOS tooling. Ad-hoc/development/simulator or foreign signing SHALL be refused; local fixtures SHALL not be reported as real Apple distribution validation.

#### Scenario: A genuine store-signed device IPA is inspected
- **GIVEN** the independently expected Apple distribution identity and matching profile
- **WHEN** actual macOS signing/platform inspection runs
- **THEN** the device artifact and observed signing metadata bind the receipt.

#### Scenario: A simulator or unsupported signing path is used
- **GIVEN** an iOS simulator ZIP, foreign/development identity or unsupported verifier
- **WHEN** admission executes
- **THEN** no store upload or successful Apple-signing claim occurs.

### Requirement: STORE-014 Execute the exact verified provider toolchain
Provider CLI execution SHALL use the reviewed npm lock and the actual verified EAS package/tree; verifying one tarball and subsequently executing an unchecked re-fetch SHALL be refused. Installation SHALL exclude service credentials, preserve TLS/integrity verification and never alter the application's dependency locks.

#### Scenario: Pinned verified CLI installation matches the lock
- **GIVEN** the reviewed exact EAS archive integrity and matching isolated toolchain tree
- **WHEN** the provider CLI is executed
- **THEN** that inspected installation supplies the command.

#### Scenario: Execution selects different CLI bytes
- **GIVEN** changed package integrity, substituted tree or a separate unchecked fetch
- **WHEN** toolchain admission runs
- **THEN** no provider operation or credential-bearing CLI execution occurs.

### Requirement: STORE-015 Bound local provider subprocesses
Provider subprocesses SHALL enforce operation/output limits and, on timeout/overflow, terminate/reap only their owned local process group. Children SHALL not retain credentials after the caller returns. Remote build/submission outcome SHALL remain unknown when not actually observed; local termination SHALL not be called cloud cancellation.

#### Scenario: A CLI child exceeds its deadline
- **GIVEN** an owned local process tree with scoped provider authentication
- **WHEN** timeout or output overflow occurs
- **THEN** the group is terminated/reaped and the unknown remote state is preserved.

#### Scenario: Another local process is running
- **GIVEN** an unrelated process outside the owned group
- **WHEN** provider cleanup runs
- **THEN** that process remains untouched.

### Requirement: STORE-016 Supply a deliberate cloud operator workflow
The repository SHALL provide an optional manual macOS workflow for plan/build/status and read-only submission reconciliation with explicit environment/platform/candidate. It SHALL use intended protected environments and account-bound OIDC when needed, retain helper admission and refuse fresh store upload from an ephemeral runner. Default-main registration, real environment protection and genuine inputs remain prerequisites; PR gates SHALL never sign or publish.

#### Scenario: The operator has configured actual protected inputs
- **GIVEN** reviewed main source, protected store environment and genuine provider/cloud/signing access
- **WHEN** the deliberate browser workflow is dispatched
- **THEN** it builds/inspects, reads status or reconciles the exact original intent/submission without a local Mac or clone; initial upload remains a separate persistent operator operation.

#### Scenario: A fresh upload is requested from ephemeral Actions
- **GIVEN** only a signed build receipt or a missing original pending intent/submission UUID
- **WHEN** a fresh submit or incomplete reconcile operation is requested
- **THEN** it refuses before private credential staging or AWS/EAS/store action rather than losing an upload fence on runner failure; GitHub artifact metadata reads may precede refusal.

#### Scenario: The workflow exists only on an unmerged branch
- **GIVEN** missing default-main registration/protection/credentials
- **WHEN** delivery is reported
- **THEN** it describes supplied automation and prerequisites without claiming execution.

### Requirement: STORE-017 Encrypt operator handoffs in public repositories
The cloud workflow SHALL publish only a fixed authenticated encrypted receipt/intent bundle using a genuinely supplied 32-byte secret key. It SHALL preserve original signed wire bytes, bind repository/source/environment/platform as authenticated data, refuse foreign/malformed/oversized artifacts, and stage decrypted data only in new private fixed-name files. Credentials, raw signed operator receipts and build/staging bytes SHALL not enter public Actions artifacts.

#### Scenario: A later operation consumes the same exact candidate
- **GIVEN** a same-repository encrypted artifact and matching protected key/scope
- **WHEN** the workflow authenticates and stages it
- **THEN** original receipt bytes and cross-receipt hashes survive for normal signed/provider admission.

#### Scenario: An artifact or ciphertext is substituted
- **GIVEN** a wrong repository/source/platform, altered ciphertext or arbitrary archive path
- **WHEN** handoff admission runs
- **THEN** it refuses before credentials or receipt data are exposed.

### Requirement: STORE-018 Transfer an operator-held pending intent without upload mutation
Tooling SHALL support mutation-free packing of exact signed build/intent and optional submission wire bytes into the encrypted handoff after validating trusted signatures, configuration/source/environment/platform and cross-record byte hashes. The browser workflow SHALL accept a bounded protected ciphertext package mutually exclusively with an artifact ID, preserve original wires and refuse fresh upload. Packing SHALL not call AWS/EAS/stores or read unrelated keys.

#### Scenario: A persistent operator transfers an uncertain existing submission
- **GIVEN** the original signed build and pending intent, trusted public key and protected encryption key
- **WHEN** pack completes and its ciphertext is supplied for browser reconciliation
- **THEN** the exact original byte links survive; the existing provider UUID is queried without another upload.

#### Scenario: A transfer replaces or ambiguously selects evidence
- **GIVEN** changed receipt bytes, wrong signature/scope, a foreign pending intent or both input selectors
- **WHEN** packing or browser admission is attempted
- **THEN** it refuses without a provider mutation or private credential staging.
