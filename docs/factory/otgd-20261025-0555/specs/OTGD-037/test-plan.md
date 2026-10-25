# OTGD-037: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md`; SHA-256 `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/tests/api-deadline.test.ts` — `b570f5df8f75273390e4493f48d02ecf99c7fa2941ea7d9580b88224e9b61c1d`
- `apps/mobile/tests/auth.test.ts` — `f1ded241cdf9d531fb4ab27dc3657e5377ccb0f8f5e3a5ba0f8c0df66b47f047`
- `apps/mobile/tests/lifecycle.test.ts` — `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`
- `apps/mobile/tests/workspace-scope.test.ts` — `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`
- `services/api/tests/test_identity_barriers.py` — `79480e9dde91c88207e1f10675e1a30f1a5e06e6d7df10cdc8c07c4d70fc15d2`
- `services/api/tests/test_local_identity.py` — `991733f845ff60d0ca13e145482497b6273425b1f293361a6d73eb874d29993f`
- `services/api/tests/test_local_oauth_security.py` — `97d79c648fe5a9b1dc3085146df8bba286647bf2d63b10c76b74c2e63af38b5a`
- `services/api/tests/test_security.py` — `df21a343ca0d2ebb7e0232230c425b2e097e73d1e43f4137198ccfe50b092579`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-AUTH-001 — Browser PKCE and environment separation

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` / `AND-AUTH-001`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-037-AND-AUTH-001-01 | auth-valid-hosted-login — **GIVEN** a configured production public client and a fresh authorization attempt **WHEN** the user signs in through the hosted browser and returns with the matching code/state **THEN** one exchange completes, the account namespace is selected, and the account dashboard opens. | `apps/mobile/tests/auth.test.ts:367` — authorization-code tokens cannot inherit a prior account refresh credential and malformed responses are refused<br>`services/api/tests/test_local_identity.py:144` — test_discovery_jwks_and_issuer_bound_access_token | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-001-02 | auth-local-token-in-production — **GIVEN** a production build and a token issued by the local development issuer **WHEN** that token is supplied through storage tampering or a callback **THEN** protected requests and account activation fail without changing the current account's records. | `apps/mobile/tests/auth.test.ts:337` — provider revocation and configured browser logout use the captured family without changing a replacement account<br>`services/api/tests/test_local_identity.py:144` — test_discovery_jwks_and_issuer_bound_access_token | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-AUTH-002 — Callback integrity and single use

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` / `AND-AUTH-002`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-037-AND-AUTH-002-01 | auth-replayed-callback — **GIVEN** an authorization code was already exchanged successfully **WHEN** the same callback is delivered again **THEN** no second token exchange or account switch occurs. | `apps/mobile/tests/auth.test.ts:123` — cancelled, wrong-state, duplicate and invalidated callbacks cannot exchange a code<br>`apps/mobile/tests/api-deadline.test.ts:117` — cancelAll settles pending token recovery, and an already canceled caller never invokes fetch | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-002-02 | auth-mismatched-state — **GIVEN** a pending authorization attempt **WHEN** a callback contains a different state or redirect host **THEN** it is rejected before exchange and the user can start a new attempt. | `apps/mobile/tests/auth.test.ts:123` — cancelled, wrong-state, duplicate and invalidated callbacks cannot exchange a code<br>`apps/mobile/tests/lifecycle.test.ts:95` — PKCE attempts expire at ten minutes, reject repeated callbacks and invalidate on logout/new login | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-AUTH-003 — Account ownership and capability boundaries

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` / `AND-AUTH-003`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-037-AND-AUTH-003-01 | auth-two-accounts-same-device — **GIVEN** account A has cached records and account B signs in after A signs out **WHEN** B opens History **THEN** neither A's records nor A's pending requests are displayed or submitted as B. | `apps/mobile/tests/workspace-scope.test.ts:31` — delayed history, job or study responses cannot publish into another account<br>`services/api/tests/test_local_identity.py:144` — test_discovery_jwks_and_issuer_bound_access_token | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-003-02 | auth-no-research-role — **GIVEN** an ordinary authenticated account **WHEN** it attempts a protected research operation **THEN** the server rejects it and the app explains capability unavailability without treating the rejection as an expired login. | `apps/mobile/tests/lifecycle.test.ts:95` — PKCE attempts expire at ten minutes, reject repeated callbacks and invalidate on logout/new login<br>`services/api/tests/test_local_identity.py:144` — test_discovery_jwks_and_issuer_bound_access_token | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-AUTH-004 — Token lifecycle and coordinated refresh

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` / `AND-AUTH-004`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-037-AND-AUTH-004-01 | auth-concurrent-401 — **GIVEN** three authenticated requests receive 401 because an access token expired **WHEN** refresh succeeds **THEN** exactly one refresh occurs and each eligible request is replayed once with its original idempotency key. | `apps/mobile/tests/auth.test.ts:164` — one current refresh request preserves an omitted refresh token and every waiter receives the same access token<br>`services/api/tests/test_local_identity.py:250` — test_refresh_rotation_preserves_auth_time_and_family_and_revocation_blocks_new_tokens | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-004-02 | auth-revoked-refresh-token — **GIVEN** the issuer has revoked the refresh token **WHEN** refresh is attempted **THEN** no retry loop occurs, sync pauses, and Sign in again is offered without discarding an unsynchronized draft silently. | `apps/mobile/tests/auth.test.ts:202` — revoked refresh clears the current account while transient connection failure retains its protected identity<br>`services/api/tests/test_local_identity.py:250` — test_refresh_rotation_preserves_auth_time_and_family_and_revocation_blocks_new_tokens | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `403`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-AUTH-005 — Offline and interrupted authentication

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` / `AND-AUTH-005`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-037-AND-AUTH-005-01 | auth-offline-existing-account — **GIVEN** a cache belonging to the same still-signed-in account and no network **WHEN** the app is opened and device credential/biometric authentication succeeds **THEN** cached history is readable as cached, no token is invented, and uploads remain queued for that account. | `apps/mobile/tests/lifecycle.test.ts:133` — failed terminal storage remains retryable using the native cached receipt<br>`services/api/tests/test_identity_barriers.py:73` — test_logout_cannot_select_another_token_family_or_reactivate_locked_account | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-005-02 | auth-browser-killed — **GIVEN** the process terminates during browser authorization **WHEN** the app restarts after the pending attempt expires **THEN** it returns to signed out and offers a new attempt instead of assuming browser authentication succeeded. | `services/api/tests/test_local_oauth_security.py:261` — test_expired_cleanup_is_bounded_and_never_expires_disabled_identity<br>`services/api/tests/test_identity_barriers.py:60` — test_locked_identity_can_logout_own_signed_family_without_opening_data_routes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-005-03 | auth-signed-out-offline-cache-remains-locked — **GIVEN** account A selected Keep encrypted records and sign out **WHEN** A opens the app offline and passes device biometric authentication **THEN** A's retained cache remains locked until same-issuer/subject reauthentication; biometric success alone does not recreate signed-in state. | `services/api/tests/test_identity_barriers.py:60` — test_locked_identity_can_logout_own_signed_family_without_opening_data_routes<br>`apps/mobile/tests/auth.test.ts:311` — credential writes cannot finish after a serialized sign-out removal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-005-04 | auth-canceled-device-unlock — **GIVEN** the same account is still signed in with readable cached records **WHEN** the user cancels device authentication on offline launch **THEN** no account history or profile is displayed and the user may retry or enter isolated demo. | `apps/mobile/tests/lifecycle.test.ts:133` — failed terminal storage remains retryable using the native cached receipt<br>`services/api/tests/test_identity_barriers.py:60` — test_locked_identity_can_logout_own_signed_family_without_opening_data_routes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-AUTH-006 — Explicit and reliable sign-out

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` / `AND-AUTH-006`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-037-AND-AUTH-006-01 | auth-sign-out-with-pending-check — **GIVEN** one account check has not synchronized **WHEN** the user selects sign-out **THEN** the sheet states “1 check has not synced”; the default retains the locked record, and choosing local removal requires the extra count-specific confirmation. | `apps/mobile/tests/auth.test.ts:311` — credential writes cannot finish after a serialized sign-out removal<br>`apps/mobile/tests/lifecycle.test.ts:21` — sign-out removal finishes after an already-started OS credential write | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-006-02 | auth-late-response-after-sign-out — **GIVEN** an account-history request remains in flight **WHEN** sign-out completes and the response later arrives **THEN** the response is discarded and cannot unlock retained records, recreate removed records, or appear in demo. | `apps/mobile/tests/api-deadline.test.ts:12` — a stalled refresh cannot hold an API request past its 15-second deadline or send late credentials<br>`apps/mobile/tests/auth.test.ts:311` — credential writes cannot finish after a serialized sign-out removal | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-006-03 | auth-default-signout-retains-locked-pending-data — **GIVEN** account A owns two unsynchronized checks **WHEN** the default sign-out action completes and account B signs in **THEN** A's encrypted records remain locked and unuploaded; B cannot list, unlock, or queue them. | `apps/mobile/tests/auth.test.ts:311` — credential writes cannot finish after a serialized sign-out removal<br>`services/api/tests/test_identity_barriers.py:73` — test_logout_cannot_select_another_token_family_or_reactivate_locked_account | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-AUTH-007 — Accessible recovery and iOS parity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md` / `AND-AUTH-007`.

Prerequisites and limits: NOT_RUN native OS UI parity, TalkBack/VoiceOver, maximum text, permission/settings round trip, restart and encrypted-cache recovery; browser component checks cover a subset.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-037-AND-AUTH-007-01 | auth-accessible-browser-return — **GIVEN** TalkBack or VoiceOver is active **WHEN** the browser is canceled **THEN** focus returns to the sign-in heading and the cancellation message is announced once with Try again reachable. | `services/api/tests/test_local_identity.py:250` — test_refresh_rotation_preserves_auth_time_and_family_and_revocation_blocks_new_tokens<br>`apps/mobile/tests/auth.test.ts:367` — authorization-code tokens cannot inherit a prior account refresh credential and malformed responses are refused | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-037-AND-AUTH-007-02 | auth-ios-secure-storage — **GIVEN** an iOS sign-in completes **WHEN** app storage and logs are inspected **THEN** refresh credentials are confined to the approved Keychain path and no token appears in ordinary preferences, logs, or check exports. ## Acceptance evidence Required tests cover real configured QA Cognito browser login on Android/iOS; local-issuer parity; bad/replayed callbacks; cross-account resource access; refresh races; key rotation; offline launch/sign-out; process termination; unsynchronized-data warning; redacted logs; secure-storage inspection. A local issuer test cannot substitute for hosted OAuth/device validation or prove production signing/distribution readiness. | `services/api/tests/test_local_identity.py:250` — test_refresh_rotation_preserves_auth_time_and_family_and_revocation_blocks_new_tokens<br>`apps/mobile/tests/lifecycle.test.ts:95` — PKCE attempts expire at ten minutes, reject repeated callbacks and invalidate on logout/new login | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Permissions race and no-reprompt assertion audit

Mapped existing cases: OTGD-036-AND-SET-003-01/02 and AND-SET-007-02; related AND-EYE-002, AND-ONB-004 and AND-AUTH-005.

Assertion adequacy inspected: Read PermissionsCard implementation and actual exported Settings component harness. Status labels cover denied/canAskAgain, denied/permanent, restricted, undetermined, failed reads; zero prompts across mount/refresh/active-return; OS settings call occurs once only explicit action. Deferred reads resolved newer-first, stale controller epoch before React render, account/generation changes and unmount must not publish old state; new scoped card is Not checked until current read; listener teardown asserted. Real ordinary UI test Settings/Back preserves draft/sample with no camera prompt. Implementation uses active+sequence+captured epoch guard and scoped card identity.

Remaining limits: Adapters are controlled OS observations. Real Android/iOS settings return, OS permission policy, TalkBack/VoiceOver, key storage and native lifecycle remain Task7 BLOCKED/NOT_RUN. Writer not released; no final gate execution or independent runtime PASS.

### Authenticated ordinary-web live test source audit

Mapped existing cases: Related actual paths: AND-AUTH-001/003/005/006; AND-SYNC-002/003/004/007; AND-HIST-001/005/006; AND-EXP-001/002/003/006; AND-PRIV-003/004/005; WEB-DEP-003/008; complete full canonical scenarios remain separately assessed.

Assertion adequacy inspected: Read authenticated-live.spec.ts ordinary account test and helpers. Real issuer PKCE/token responses, notice/profile/context and deliberate synthetic-account Save then Upload. route.fetch sends actual finalize and validates202 before connection-reset abort; no fake success. Actual queued measurement-only result, reload clears account memory and reauthentication retrieves server history, actual export job/ZIP manifest/hash/single-check bytes, foreign404, reauthenticated deletion/current generation barrier, explicit new empty workspace and logout refresh-family refusal. Two actual viewport projects and private bounded fixture inventory; unknown records stop all-data deletion. Network receipts redacted; live config disables OAuth/token-bearing traces/HAR/screenshots.

Remaining limits: Writer active; planned final gate NOT_RUN. Current inspected ordinary case does not establish all governed consent/withdrawal, raw, pending-lab or research UI/API journeys; later governed work is WIP. No native encrypted persistence, public CloudFront delivery or physical sensing inferred. Need actual raw JUnit/redacted receipts/archive hashes and final gate wiring after freeze.
