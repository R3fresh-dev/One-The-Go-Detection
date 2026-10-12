## ADDED Requirements

### Requirement: WEB-DEP-001 Deliver public application bytes through a private origin
The system SHALL store web assets in a versioned private retained bucket with public access blocked and TLS enforced, and SHALL grant read access only to the exact CloudFront distribution through SigV4 OAC.

#### Scenario: Customer opens the published HTTPS origin
- **GIVEN** an admitted published application artifact
- **WHEN** a customer opens WebOrigin
- **THEN** CloudFront serves the application without public S3 access or credentials in the URL.

#### Scenario: Caller requests the bucket directly
- **GIVEN** an anonymous caller without distribution authority
- **WHEN** it requests an S3 asset
- **THEN** bucket policy does not grant public asset access.

### Requirement: WEB-DEP-002 Preserve browser routing and asset failures
Delivery SHALL rewrite only GET/HEAD extensionless navigation to index.html and SHALL preserve errors for missing script, image and font paths.

#### Scenario: Customer opens a history deep link
- **GIVEN** published index.html
- **WHEN** GET /history reaches the distribution
- **THEN** the actual application entry point is returned.

#### Scenario: A missing script is requested
- **GIVEN** no matching .js asset
- **WHEN** the browser requests that asset
- **THEN** an origin error is preserved rather than returning a successful HTML body.

### Requirement: WEB-DEP-003 Pin secure public browser identity
The cloud browser build SHALL fix its environment, API origin, exact OAuth issuer/public client and callback origin from actual deployment outputs; callbacks/CORS SHALL contain exact registered origins without wildcards.

#### Scenario: QA and production are opened together
- **GIVEN** separate approved account deployments
- **WHEN** both applications open
- **THEN** each uses its own identity/API and QA remains visibly identified.

#### Scenario: A host environment attempts to override identity
- **GIVEN** conflicting APP/EXPO_PUBLIC/EAS inputs on the build host
- **WHEN** the reviewed artifact builds
- **THEN** the explicit deployed identity controls the bundle and a mismatching output fails verification.

### Requirement: WEB-DEP-004 Bind all web bytes to reviewed source and authority
Web artifacts SHALL be built from the admitted immutable Git revision and committed npm lock, and SHALL bind every public file, archive, runtime, environment/account, source/image and service/gate receipt to an independently verified Ed25519 web release.

#### Scenario: The reviewed artifact is published
- **GIVEN** matching signed service/web records, archive and deployed identity
- **WHEN** publication is admitted
- **THEN** exact file SHA-256/size/path/type and runtime bindings verify before upload.

#### Scenario: An archive is altered after approval
- **GIVEN** a replaced file, duplicate entry or foreign identity
- **WHEN** the artifact is verified
- **THEN** publication fails before any byte is uploaded.

### Requirement: WEB-DEP-005 Bound public artifact content
Artifacts SHALL reject symlinks, unsafe paths, source maps and secret/unreviewed file types, and SHALL enforce 256 files, 16 MiB per file, 128 MiB total and the signed evidence size bound.

#### Scenario: A normal Expo export is packaged
- **GIVEN** reviewed HTML, JavaScript, metadata and supported assets
- **WHEN** limits hold
- **THEN** a deterministic ZIP and canonical manifest are created.

#### Scenario: Export contains a secret or traversal path
- **GIVEN** .env, ../, absolute paths or a symlink
- **WHEN** packaging or archive admission occurs
- **THEN** the artifact is rejected.

### Requirement: WEB-DEP-006 Publish immutably with an entry-point barrier
Publication SHALL verify the actual distribution/private origin/release prefix, upload dependency files before index.html using create-if-absent, verify actual stored bytes, and await bounded invalidation completion.

#### Scenario: An identical approved release is retried
- **GIVEN** existing same-prefix identical bytes
- **WHEN** publication repeats
- **THEN** those bytes verify and are preserved.

#### Scenario: A dependency conflicts or fails
- **GIVEN** a different existing file or failed upload
- **WHEN** publication runs
- **THEN** it fails before committing index.html or reporting publication success.

### Requirement: WEB-DEP-007 Enforce browser security headers
Delivery SHALL set no-sniff, frame denial, HSTS, no-referrer and CSP restricting scripts to self, object/frame ancestry to none and network connections to the configured API/issuer, with inline style allowance documented for React Native Web.

#### Scenario: Public transport probes execute
- **GIVEN** a published release
- **WHEN** index.html is retrieved over HTTPS
- **THEN** byte integrity and required security headers verify.

#### Scenario: The response lacks its security policy
- **GIVEN** missing CSP/HSTS/no-sniff/frame denial
- **WHEN** public verification runs
- **THEN** deployment exits nonzero without a verified-access receipt.

### Requirement: WEB-DEP-008 Keep customer access claims accurate
The hosted application SHALL retain notice, account/study authorization and initial measurement-only constraints; deployment receipts SHALL distinguish public transport verification from authenticated ATDD, native capture and cloud operational acceptance.

#### Scenario: A customer experiments in the browser
- **GIVEN** the actual shared web application
- **WHEN** a guest or authorized customer uses its UI
- **THEN** browser storage/hardware limits and fictional data remain explicit.

#### Scenario: A deployment command succeeds
- **GIVEN** only public HTTPS and worker health were checked
- **WHEN** the receipt is written
- **THEN** it does not claim signed-in browser, real-device, App Store or clinical validation.
