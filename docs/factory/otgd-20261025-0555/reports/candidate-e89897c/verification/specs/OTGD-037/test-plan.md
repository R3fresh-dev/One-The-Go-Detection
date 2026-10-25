# OTGD-037 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md`; SHA256 `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-037/test-plan.md`. External review artifact only; PM controls import.

All 17 stable cases / 7 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-037-AND-AUTH-001-01 | auth-valid-hosted-login — - **GIVEN** a configured production public client and a fresh authorization attempt - **WHEN** the user signs in through the hosted browser and returns with the matching code/state - **THEN** one exchange completes, the account namespace is selected, and the account dashboard opens. | PARTIAL |
| OTGD-037-AND-AUTH-001-02 | auth-local-token-in-production — - **GIVEN** a production build and a token issued by the local development issuer - **WHEN** that token is supplied through storage tampering or a callback - **THEN** protected requests and account activation fail without changing the current account's records. | PARTIAL |
| OTGD-037-AND-AUTH-002-01 | auth-replayed-callback — - **GIVEN** an authorization code was already exchanged successfully - **WHEN** the same callback is delivered again - **THEN** no second token exchange or account switch occurs. | PASS |
| OTGD-037-AND-AUTH-002-02 | auth-mismatched-state — - **GIVEN** a pending authorization attempt - **WHEN** a callback contains a different state or redirect host - **THEN** it is rejected before exchange and the user can start a new attempt. | PASS |
| OTGD-037-AND-AUTH-003-01 | auth-two-accounts-same-device — - **GIVEN** account A has cached records and account B signs in after A signs out - **WHEN** B opens History - **THEN** neither A's records nor A's pending requests are displayed or submitted as B. | PARTIAL |
| OTGD-037-AND-AUTH-003-02 | auth-no-research-role — - **GIVEN** an ordinary authenticated account - **WHEN** it attempts a protected research operation - **THEN** the server rejects it and the app explains capability unavailability without treating the rejection as an expired login. | PARTIAL |
| OTGD-037-AND-AUTH-004-01 | auth-concurrent-401 — - **GIVEN** three authenticated requests receive 401 because an access token expired - **WHEN** refresh succeeds - **THEN** exactly one refresh occurs and each eligible request is replayed once with its original idempotency key. | PASS |
| OTGD-037-AND-AUTH-004-02 | auth-revoked-refresh-token — - **GIVEN** the issuer has revoked the refresh token - **WHEN** refresh is attempted - **THEN** no retry loop occurs, sync pauses, and Sign in again is offered without discarding an unsynchronized draft silently. | PARTIAL |
| OTGD-037-AND-AUTH-005-01 | auth-offline-existing-account — - **GIVEN** a cache belonging to the same still-signed-in account and no network - **WHEN** the app is opened and device credential/biometric authentication succeeds - **THEN** cached history is readable as cached, no token is invented, and uploads remain queued for that account. | BLOCKED |
| OTGD-037-AND-AUTH-005-02 | auth-browser-killed — - **GIVEN** the process terminates during browser authorization - **WHEN** the app restarts after the pending attempt expires - **THEN** it returns to signed out and offers a new attempt instead of assuming browser authentication succeeded. | BLOCKED |
| OTGD-037-AND-AUTH-005-03 | auth-signed-out-offline-cache-remains-locked — - **GIVEN** account A selected Keep encrypted records and sign out - **WHEN** A opens the app offline and passes device biometric authentication - **THEN** A's retained cache remains locked until same-issuer/subject reauthentication; biometric success alone does not recreate signed-in state. | BLOCKED |
| OTGD-037-AND-AUTH-005-04 | auth-canceled-device-unlock — - **GIVEN** the same account is still signed in with readable cached records - **WHEN** the user cancels device authentication on offline launch - **THEN** no account history or profile is displayed and the user may retry or enter isolated demo. | BLOCKED |
| OTGD-037-AND-AUTH-006-01 | auth-sign-out-with-pending-check — - **GIVEN** one account check has not synchronized - **WHEN** the user selects sign-out - **THEN** the sheet states “1 check has not synced”; the default retains the locked record, and choosing local removal requires the extra count-specific confirmation. | PARTIAL |
| OTGD-037-AND-AUTH-006-02 | auth-late-response-after-sign-out — - **GIVEN** an account-history request remains in flight - **WHEN** sign-out completes and the response later arrives - **THEN** the response is discarded and cannot unlock retained records, recreate removed records, or appear in demo. | PASS |
| OTGD-037-AND-AUTH-006-03 | auth-default-signout-retains-locked-pending-data — - **GIVEN** account A owns two unsynchronized checks - **WHEN** the default sign-out action completes and account B signs in - **THEN** A's encrypted records remain locked and unuploaded; B cannot list, unlock, or queue them. | PARTIAL |
| OTGD-037-AND-AUTH-007-01 | auth-accessible-browser-return — - **GIVEN** TalkBack or VoiceOver is active - **WHEN** the browser is canceled - **THEN** focus returns to the sign-in heading and the cancellation message is announced once with Try again reachable. | BLOCKED |
| OTGD-037-AND-AUTH-007-02 | auth-ios-secure-storage — - **GIVEN** an iOS sign-in completes - **WHEN** app storage and logs are inspected - **THEN** refresh credentials are confined to the approved Keychain path and no token appears in ordinary preferences, logs, or check exports. | BLOCKED |
