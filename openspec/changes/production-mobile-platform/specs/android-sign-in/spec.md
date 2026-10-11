# Android sign-in, account sessions, and sign-out

## Purpose and traceability

Authenticate an account for its own measurement records without enrolling it in research. QA/production use Cognito-hosted OAuth authorization code with PKCE; local development uses a separate development issuer. Upstream: HLD §§4.4, 8; PRD-018/020; full specification SEC-002/003/004/006/007, OPS-005, MOD-009/010, DOC-001.

## Shared contract authority

The [shared platform contracts](../../shared-contracts.md) are normative for release scope, workspace isolation, authentication, data generations, concurrency, privacy-job states, export selection, context freezing, and active-capture navigation. This feature SHALL follow those contracts; its UI preferences cannot weaken them.

## Customer journey and screen contract

1. **Sign in:** heading “Keep your records connected”; body “Sign in to access your account on your devices. Demo checks stay separate.” Primary **Continue to secure sign-in**; secondary **Explore demo**; **Back** returns to the caller. The app does not render password fields.
2. **Hosted browser:** the selected environment's issuer owns sign-in, sign-up, verification, password reset, and account-recovery pages. The app presents them in the OS browser authentication session. Cancel returns to the sign-in screen with “Sign-in canceled. Your local records are unchanged.”
3. **Completing sign-in:** progress text “Finishing sign-in”; buttons are disabled while a single callback is verified and exchanged. Failure shows a non-sensitive reason category and **Try again** / **Back**.
4. **Account dashboard:** the validated account identity is active only after token verification and local namespace initialization. A notice update or unresolved previous-account cleanup is completed before protected writes.
5. **Sign out:** Settings shows “Sign out of this account?” with the account identifier minimally disclosed. Default action **Keep encrypted records and sign out** removes credentials and locks the retained account namespace. Alternative **Remove this account's local records and sign out** requires a second confirmation naming the unsynchronized-record count. **Stay signed in** cancels before sign-out. Copy states that cloud records remain. Retained signed-out records require reauthentication as the same issuer and subject; device unlock alone cannot reopen them.

## Data, API, and state contract

Authentication states are `signed_out`, `authorizing`, `exchanging`, `signed_in`, `refreshing`, `reauthentication_required`, and `signing_out`. A persisted token alone cannot establish `signed_in`; the configured issuer/client_id/token_use, signature, expiry, and required access-token claims are checked under the shared verifier policy and authorized API responses. Account namespace keys derive from the verified issuer/subject and account reference returned by an authorized API response, never an unverified decoded token or email. No email/password/token enters analytics, crash breadcrumbs, URLs sent to logging, or check metadata.

The app discovers only the environment-allowlisted OIDC metadata and uses PKCE S256, a fresh high-entropy verifier, state, nonce, exact registered redirect URI, and system browser. QA/production client IDs are public clients without embedded client secrets. iOS universal links/registered authentication callback and Android verified App Links/registered callback must match the environment allowlist. Pending verifier/state/nonce are held in protected short-lived storage only when needed for process recovery and expire after ten minutes (engineering default). Refresh tokens use Android Keystore-backed secure storage and iOS Keychain; access tokens remain in memory where feasible. Ordinary AsyncStorage is forbidden for tokens. A 401 triggers at most one coordinated refresh and replay of an idempotent operation; 403 does not trigger repeated refresh. Only the issuer access token is sent to the API; ID tokens are not API bearer credentials. The API remains authoritative for resource ownership and study permissions. A destructive-action reauthentication must obtain a new trusted auth_time through the hosted browser; token refresh alone does not establish recent authentication.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-AUTH-006 detailed contract

Sign-out SHALL stop protected operations and discard late responses, remove credentials, and default to retaining a locked encrypted account namespace. Explicit local removal is the alternative; issuer revocation/logout is attempted when online. It SHALL state when offline sign-out removed local credentials but server revocation could not be confirmed. It MUST NOT claim cloud data deletion or remove demo history. Unsynchronized-record deletion requires a second explicit destructive choice naming the count.

### AND-AUTH-003/004/005/006 integration resolution

Offline cached account access SHALL be allowed only for a previously authenticated, still-signed-in matching issuer/subject after `expo-local-authentication` succeeds using the configured device credential or biometric. Cancel, failed authentication, unavailable device credentials, or invalid account-lock metadata leave the namespace locked and offer a retry or online sign-in path without a plaintext/read bypass. Sign-out invalidates that offline eligibility even if credentials are retained by the OS; only a new same-issuer/subject login can restore the retained namespace. Another account cannot unlock it. Active native acquisition stops and commits one terminal attempt before sign-out/navigation UI.

Every protected write SHALL carry the pinned `X-Data-Generation`. Refresh and identity reauthentication do not automatically acknowledge a new generation or rebind stale queued data. HTTP 428 means missing precondition, 412 stale ETag, 409 state/idempotency conflict, and 410 stale generation; none is repaired through a refresh loop. The shared contract defines replay of an already accepted idempotent request. Account credentials remain distinct from study and model permission, and `inference_available=false` applies to every current path.

### AND-AUTH-004/005/006 shared lifecycle details

Online sign-out SHALL call `POST /v1/auth/logout` with the current access token, generation, and idempotency key to revoke the current token family; provider/browser logout remains a separate best-effort step. It does not revoke other device families or delete cloud data. Failure/unknown outcome is reported truthfully while local credentials are removed and the namespace locked. Account views lock on backgrounding. Offline credential/biometric unlock applies only to the same still-signed-in account and grants read access to permitted cached records, never qualified capture. All qualified capture in this release needs fresh online server start authorization. The API checks current application account/family state in addition to signature/claims; refresh alone does not satisfy recent destructive-action authentication.

## ADDED Requirements

### Requirement: AND-AUTH-001 Browser PKCE and environment separation

The app SHALL use browser code + PKCE S256 for its configured Cognito/local issuer and reject issuer, client, redirect, and state mismatches. API credentials SHALL meet the shared access-token claim policy. Production SHALL reject local issuer tokens and runtime endpoint overrides.

#### Scenario: auth-valid-hosted-login
- **GIVEN** a configured production public client and a fresh authorization attempt
- **WHEN** the user signs in through the hosted browser and returns with the matching code/state
- **THEN** one exchange completes, the account namespace is selected, and the account dashboard opens.

#### Scenario: auth-local-token-in-production
- **GIVEN** a production build and a token issued by the local development issuer
- **WHEN** that token is supplied through storage tampering or a callback
- **THEN** protected requests and account activation fail without changing the current account's records.

### Requirement: AND-AUTH-002 Callback integrity and single use

The app SHALL verify callback state, nonce where applicable, pending attempt identity, expiry, and exact redirect before token exchange. Each attempt SHALL be consumed once. Unsolicited, replayed, or expired callbacks SHALL display “This sign-in link is no longer valid. Start again.” without logging the callback query.

#### Scenario: auth-replayed-callback
- **GIVEN** an authorization code was already exchanged successfully
- **WHEN** the same callback is delivered again
- **THEN** no second token exchange or account switch occurs.

#### Scenario: auth-mismatched-state
- **GIVEN** a pending authorization attempt
- **WHEN** a callback contains a different state or redirect host
- **THEN** it is rejected before exchange and the user can start a new attempt.

### Requirement: AND-AUTH-003 Account ownership and capability boundaries

The app SHALL derive its account partition from validated issuer/subject and SHALL never authorize server access from a route parameter, email match, cached UI role, or locally modified profile. Successful sign-in MUST NOT enable research upload, study enrollment, validated sensor status, or inference.

#### Scenario: auth-two-accounts-same-device
- **GIVEN** account A has cached records and account B signs in after A signs out
- **WHEN** B opens History
- **THEN** neither A's records nor A's pending requests are displayed or submitted as B.

#### Scenario: auth-no-research-role
- **GIVEN** an ordinary authenticated account
- **WHEN** it attempts a protected research operation
- **THEN** the server rejects it and the app explains capability unavailability without treating the rejection as an expired login.

### Requirement: AND-AUTH-004 Token lifecycle and coordinated refresh

The app SHALL coordinate concurrent refresh attempts into one request, replace rotated refresh tokens atomically, and retry each eligible request at most once after a refresh. Refresh rejection SHALL move to `reauthentication_required`, pause protected sync, clear unusable credentials, and retain permitted encrypted drafts in their existing partition. A 403 SHALL remain a permission failure.

#### Scenario: auth-concurrent-401
- **GIVEN** three authenticated requests receive 401 because an access token expired
- **WHEN** refresh succeeds
- **THEN** exactly one refresh occurs and each eligible request is replayed once with its original idempotency key.

#### Scenario: auth-revoked-refresh-token
- **GIVEN** the issuer has revoked the refresh token
- **WHEN** refresh is attempted
- **THEN** no retry loop occurs, sync pauses, and Sign in again is offered without discarding an unsynchronized draft silently.

### Requirement: AND-AUTH-005 Offline and interrupted authentication

The app SHALL distinguish offline, canceled, failed, and expired authentication. Offline account reads SHALL require the same still-signed-in identity plus successful device authentication. Signed-out records SHALL require same-issuer/subject reauthentication. Failed or canceled unlock SHALL remain locked; demo remains separately available.

#### Scenario: auth-offline-existing-account
- **GIVEN** a cache belonging to the same still-signed-in account and no network
- **WHEN** the app is opened and device credential/biometric authentication succeeds
- **THEN** cached history is readable as cached, no token is invented, and uploads remain queued for that account.

#### Scenario: auth-browser-killed
- **GIVEN** the process terminates during browser authorization
- **WHEN** the app restarts after the pending attempt expires
- **THEN** it returns to signed out and offers a new attempt instead of assuming browser authentication succeeded.

#### Scenario: auth-signed-out-offline-cache-remains-locked
- **GIVEN** account A selected Keep encrypted records and sign out
- **WHEN** A opens the app offline and passes device biometric authentication
- **THEN** A's retained cache remains locked until same-issuer/subject reauthentication; biometric success alone does not recreate signed-in state.

#### Scenario: auth-canceled-device-unlock
- **GIVEN** the same account is still signed in with readable cached records
- **WHEN** the user cancels device authentication on offline launch
- **THEN** no account history or profile is displayed and the user may retry or enter isolated demo.

### Requirement: AND-AUTH-006 Explicit and reliable sign-out

Sign-out SHALL stop protected operations and discard late responses, remove credentials, and default to retaining a locked encrypted account namespace. Explicit local removal is the alternative; issuer revocation/logout is attempted when online. The implementation SHALL also satisfy the AND-AUTH-006 detailed contract above.

#### Scenario: auth-sign-out-with-pending-check
- **GIVEN** one account check has not synchronized
- **WHEN** the user selects sign-out
- **THEN** the sheet states “1 check has not synced”; the default retains the locked record, and choosing local removal requires the extra count-specific confirmation.

#### Scenario: auth-late-response-after-sign-out
- **GIVEN** an account-history request remains in flight
- **WHEN** sign-out completes and the response later arrives
- **THEN** the response is discarded and cannot unlock retained records, recreate removed records, or appear in demo.

#### Scenario: auth-default-signout-retains-locked-pending-data
- **GIVEN** account A owns two unsynchronized checks
- **WHEN** the default sign-out action completes and account B signs in
- **THEN** A's encrypted records remain locked and unuploaded; B cannot list, unlock, or queue them.

### Requirement: AND-AUTH-007 Accessible recovery and iOS parity

The app SHALL expose status changes to accessibility services without reading tokens or codes, preserve focus after browser cancellation, support password managers through the system browser, and keep recovery actions reachable under large text. iOS SHALL implement equivalent account, PKCE, refresh, partition, and sign-out behavior using its system authentication session and Keychain.

#### Scenario: auth-accessible-browser-return
- **GIVEN** TalkBack or VoiceOver is active
- **WHEN** the browser is canceled
- **THEN** focus returns to the sign-in heading and the cancellation message is announced once with Try again reachable.

#### Scenario: auth-ios-secure-storage
- **GIVEN** an iOS sign-in completes
- **WHEN** app storage and logs are inspected
- **THEN** refresh credentials are confined to the approved Keychain path and no token appears in ordinary preferences, logs, or check exports.

## Acceptance evidence

Required tests cover real configured QA Cognito browser login on Android/iOS; local-issuer parity; bad/replayed callbacks; cross-account resource access; refresh races; key rotation; offline launch/sign-out; process termination; unsynchronized-data warning; redacted logs; secure-storage inspection. A local issuer test cannot substitute for hosted OAuth/device validation or prove production signing/distribution readiness.
