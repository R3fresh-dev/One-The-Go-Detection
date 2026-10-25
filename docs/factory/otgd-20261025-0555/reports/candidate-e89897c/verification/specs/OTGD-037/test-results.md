# OTGD-037 current test-result proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`; source fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`.

Canonical `openspec/changes/production-mobile-platform/specs/android-sign-in/spec.md`; SHA256 `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd`.

17 cases, 7 requirements: BLOCKED 6, PARTIAL 7, PASS 4. Zero unaudited rows.

**This is scoped case evidence, not a completed-spec/council/application/release approval.** Current CI14 jobs passed. Independent local all7 gates passed. Physical timing, predictive validity, sensing qualification and real participant authorization are not established. Fictional native fixtures remain `modelEligible=false`.

Actual current commands and evidence are indexed in `test-plan.md`, `../../source-assertions.json`, `../../named-observations.json` and `../../ci-artifact-inventory.json`. Historical candidate28/cf74fcf and author RED/GREEN remain development/history evidence; their raw outcomes are not promoted.

## OTGD-037-AND-AUTH-001-01 — PARTIAL

auth-valid-hosted-login — - **GIVEN** a configured production public client and a fresh authorization attempt - **WHEN** the user signs in through the hosted browser and returns with the matching code/state - **THEN** one exchange completes, the account namespace is selected, and the account dashboard opens.

Current proof: Controlled PKCE browser response exchanges matching code/state/verifier and controller selects verified opaque account/Home; credential restore returns verified identity. All selected authorization/token/revocation/logout endpoints are pinned before saved or fresh credentials/browser use; substitutions and pending mutations refuse without credential traffic. Actual returned callback target is separately asserted by FINAL_CALLBACK_TARGET.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::PKCE callback binds state and verifier and credential restore uses verified API identity` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 122; 1 current observation(s).
- `apps/mobile/tests/controller.test.ts::signed-in profile revision freezes into Start check and a later profile save cannot replace it` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 583; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::unadmitted ${endpoint} is rejected before authorization browser or credential fetch` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 449; 4 current observation(s).
- `apps/mobile/tests/auth.test.ts::restored ${endpoint} substitution never activates saved credentials` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 471; 4 current observation(s).
- `apps/mobile/tests/auth.test.ts::commit refuses altered endpoints before activating or persisting credentials` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 505; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::refresh and captured provider operations recheck endpoint metadata before credential traffic` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 531; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::admitted metadata snapshots cannot be retargeted while authorization or captured revocation is pending` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 565; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- The actual production public-client hosted browser and native callback account journey remains unexecuted. Current endpoint pinning, exact returned target, code/state, replay, refresh and no credential traffic on refusal are directly tested; Cognito/provider credentials and installed OS execution are separate prerequisites.

Prerequisite/evidence type: provider_credentials, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Scope limits: Public Cognito/installed native browser account journey remains an external execution prerequisite for AUTH001-01; software endpoint defect is closed, not evidence of provider deployment.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 99d077d57980a56fdb6c5b2c69a2da515c35ab327bbc6e14dccca5335b02733c. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-001-02 — PARTIAL

auth-local-token-in-production — - **GIVEN** a production build and a token issued by the local development issuer - **WHEN** that token is supplied through storage tampering or a callback - **THEN** protected requests and account activation fail without changing the current account's records.

Current proof: API invalid access-token issuer/client/token_use/expiry/nbf matrix rejects401; AuthManager commit foreign issuer refuses.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_api.py::test_invalid_access_tokens` — file SHA `f65197065d9330dc7a8075f4d109789429ed8ca3a4e7968c35bd4c4ca2a5dc48`, line 100; 25 current observation(s).
- `apps/mobile/tests/auth.test.ts::PKCE callback binds state and verifier and credential restore uses verified API identity` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 122; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Production build with local fixture token via tampered saved credentials/callback and unchanged current account inventory is not directly asserted. Arbitrary wrong issuer case differs from explicit production/local issuer namespace injection.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 9b603084ec6fac616b181c6fe819cccdf16357374fd01954b0e731cac811618a. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-002-01 — PASS

auth-replayed-callback — - **GIVEN** an authorization code was already exchanged successfully - **WHEN** the same callback is delivered again - **THEN** no second token exchange or account switch occurs.

Current proof: Pure AuthorizationAttemptGuard refuses consumed attempt twice; auth transport cancel/wrong-state/invalidation make zero exchange calls. AppController successful callback exchange then same old success during fresh attempt leaves exchange/capabilitylookup counts and account/authgeneration unchanged.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::cancelled, wrong-state, duplicate and invalidated callbacks cannot exchange a code` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 147; 1 current observation(s).
- `apps/mobile/tests/lifecycle.test.ts::PKCE attempts expire at ten minutes, reject repeated callbacks and invalidate on logout/new login` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 95; 1 current observation(s).
- `apps/mobile/tests/auth-acceptance.test.ts::OTGD-037-AND-AUTH-002-01: replaying an already exchanged successful callback cannot exchange again or switch accounts` — file SHA `ca9ec0ba337a779fc8675d02069a95dfd5b7054894fde67e3900b95833ce922c`, line 14; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Actual successful callback replay and final returned-target pin are both covered by current named assertions. Native browser OS/provider execution remains unavailable.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA e639f687c6bc961881160fb31d6701f1ed3310ec2246baf39ea20c4a360c2569. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-002-02 — PASS

auth-mismatched-state — - **GIVEN** a pending authorization attempt - **WHEN** a callback contains a different state or redirect host - **THEN** it is rejected before exchange and the user can start a new attempt.

Current proof: Wrong-state callback rejects before service call; absent permitted redirect refuses; expiration/invalidation prevent exchange and fresh states differ. Actual selected-target callback for web/android/iOS and exact code/state query: all wrong schemes/hosts/ports/paths/suffixes/userinfo/fragments/duplicates/unknown/missingURL/mismatch refuse before any HTTP and retain identity/generation; fresh exact retry succeeds. All selected authorization/token/revocation/logout endpoints are pinned before saved or fresh credentials/browser use; substitutions and pending mutations refuse without credential traffic. Actual returned callback target is separately asserted by FINAL_CALLBACK_TARGET.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::cancelled, wrong-state, duplicate and invalidated callbacks cannot exchange a code` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 147; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::authorization supplies a fresh cryptographic state satisfying the issuer minimum` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 104; 1 current observation(s).
- `apps/mobile/tests/auth-callback.test.ts::exact ${platform} callback succeeds; matching state at an unadmitted return target never exchanges or changes accounts` — file SHA `d4d89af5fcce9d3d7c902d89eea1c0b72cbb09be274a962d56358dc801e6ead8`, line 20; 3 current observation(s).
- `apps/mobile/tests/auth-callback.test.ts::a success callback requires an unambiguous exact code/state query bound to SDK params before token or account traffic` — file SHA `d4d89af5fcce9d3d7c902d89eea1c0b72cbb09be274a962d56358dc801e6ead8`, line 97; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::unadmitted ${endpoint} is rejected before authorization browser or credential fetch` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 449; 4 current observation(s).
- `apps/mobile/tests/auth.test.ts::restored ${endpoint} substitution never activates saved credentials` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 471; 4 current observation(s).
- `apps/mobile/tests/auth.test.ts::commit refuses altered endpoints before activating or persisting credentials` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 505; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::refresh and captured provider operations recheck endpoint metadata before credential traffic` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 531; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::admitted metadata snapshots cannot be retargeted while authorization or captured revocation is pending` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 565; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Current unit observations execute all exact positives and42 negative deliveries; SDK/platform fixtures, not installed native browser/provider execution. Public Cognito/installed native browser account journey remains an external execution prerequisite for AUTH001-01; software endpoint defect is closed, not evidence of provider deployment.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 52ec41edadde02fccd22ca57f7e53b1e890564666bf7ec060a0f16f1d845ac57. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-003-01 — PARTIAL

auth-two-accounts-same-device — - **GIVEN** account A has cached records and account B signs in after A signs out - **WHEN** B opens History - **THEN** neither A's records nor A's pending requests are displayed or submitted as B.

Current proof: Deferred A response after workspace/accountB stamp change rejects and publishes no rows; stale refresh cannot overwriteB access token/identity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/workspace-scope.test.ts::delayed history, job or study responses cannot publish into another account` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 31; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::a stale refresh response cannot clear or overwrite a newly signed-in account` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 252; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual A cached records/pending operations retained, sign-out, B sign-in then History list/submission must verify zero A IDs/requests; stamp-only fixture and AuthManager token race do not cover persistent controller namespace journey.

Prerequisite/evidence type: software_assertion_or_integration_evidence, deployment_cloud_or_owner_prerequisite.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA de030ccfd269ada7e6ebbb435ee900f280207af56809b190ef99c12c6a62fda9. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-003-02 — PARTIAL

auth-no-research-role — - **GIVEN** an ordinary authenticated account - **WHEN** it attempts a protected research operation - **THEN** the server rejects it and the app explains capability unavailability without treating the rejection as an expired login.

Current proof: Backend current consent/scope guard refuses unauthorized acquisition and model returns no score; revoked state differs from authentication.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `services/api/tests/test_model_admission.py::test_current_authority_or_bytes_refusal_returns_no_score` — file SHA `af9e33ad937fcbe0554136ee5340806a8054fc9a80340d15484dc9480d7bd867`, line 480; 50 current observation(s).
- `apps/mobile/tests/service-boundary.test.ts::actual backend app-config and capabilities responses decode without removing mandatory fields` — file SHA `3cfc990ad01c27ca3b1b6f1d0ce8185c3379932b50c70dc129928a443314a25e`, line 21; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595383532/postgres.xml` — SHA256 `3c111a5986dfd3a6baa305bb000e550a8d290ec863ed2c490744f4de24f2d114`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit.xml` — SHA256 `81a362401f55fbc21132ac6ff70349afc663dc4fe81535fe5940add0b67a8bf1`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/current-local/postgres.xml` — SHA256 `9fee53a7e4172574433621a7c34ee2c485a2aceacabe66f0a62f35e123b865ae`.
- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/current-ci/12595857777/reports/unit.xml` — SHA256 `f09f50e4024052c38f8df0b72791503b1fc2efaae68c6b1cb54447a200669419`.

Exact unproved clause(s):

- Ordinary authenticated research operation refusal must be rendered as capability unavailable without expired-login treatment; current capability/model unit tests do not assert that exact client error classification/message.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA b336c18d9309e93cde0234d4bcd86ee97b83d7527aa2045e58219518e2f55eb8. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-004-01 — PASS

auth-concurrent-401 — - **GIVEN** three authenticated requests receive 401 because an access token expired - **WHEN** refresh succeeds - **THEN** exactly one refresh occurs and each eligible request is replayed once with its original idempotency key.

Current proof: Two concurrent accessToken callers share exactly one refresh and same access token; API401 recovery keeps original bounded deadline. Actual ephemeralHTTP/real fetch gives3initial401; real AuthManager shares1refresh; each original method/path/body/key/generation/ETag exactly twice with old→newbearer.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::one current refresh request preserves an omitted refresh token and every waiter receives the same access token` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 188; 1 current observation(s).
- `apps/mobile/tests/api-deadline.test.ts::401 recovery shares the original request deadline rather than extending it` — file SHA `b570f5df8f75273390e4493f48d02ecf99c7fa2941ea7d9580b88224e9b61c1d`, line 78; 1 current observation(s).
- `apps/mobile/tests/auth-acceptance.test.ts::OTGD-037-AND-AUTH-004-01: three HTTP401 responses share one refresh and each request replays once with its original operation` — file SHA `ca9ec0ba337a779fc8675d02069a95dfd5b7054894fde67e3900b95833ce922c`, line 94; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Scope limits: Loopback real HTTP transport and software custody; exact target pinning is separately proved. No real Cognito or installed native OS inference.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 8a4862b3cc1ccce7613bdf07ebdb07c8a124c7cc21ab0eabf00bed5361ace64c. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-004-02 — PARTIAL

auth-revoked-refresh-token — - **GIVEN** the issuer has revoked the refresh token - **WHEN** refresh is attempted - **THEN** no retry loop occurs, sync pauses, and Sign in again is offered without discarding an unsynchronized draft silently.

Current proof: Invalid_grant clears current identity/vault and invalidation count1, next accessTokennull; transient network retains identity.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::revoked refresh clears the current account while transient connection failure retains its protected identity` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 226; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Client sync paused/Sign in again UI and unsynchronized draft preservation on revoked refresh are not asserted in same context. AuthManager state clearing is narrower than draft/user recovery journey.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA de1089abf72117b3a3794ce0e5bc0a45d4a72d85607c83426faa5a68416e55d8. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-005-01 — BLOCKED

auth-offline-existing-account — - **GIVEN** a cache belonging to the same still-signed-in account and no network - **WHEN** the app is opened and device credential/biometric authentication succeeds - **THEN** cached history is readable as cached, no token is invented, and uploads remain queued for that account.

Current proof: Auth refresh network failure retains protected identity and bounded deadline; controlled native store can reopen.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::revoked refresh clears the current account while transient connection failure retains its protected identity` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 226; 1 current observation(s).
- `apps/mobile/tests/native-storage.test.ts::concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable` — file SHA `52005beea373ed0bf603dffffc6a20cb2e8fd07371bf5cb0712afa4b3bf208df`, line 128; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual same-still-signed-in cached account offline successful biometric unlock/history cachedlabel/no inventedtoken/queue owner requires actual OS credential+SQLCipher evidence.

Prerequisite/evidence type: native_os_execution, independent_owner_review.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 789f4aa73d868b19d8736aed93c029972739c5435f92a1ae9ba7c88596b0b91b. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-005-02 — BLOCKED

auth-browser-killed — - **GIVEN** the process terminates during browser authorization - **WHEN** the app restarts after the pending attempt expires - **THEN** it returns to signed out and offers a new attempt instead of assuming browser authentication succeeded.

Current proof: Pure PKCE guard expires at600000ms and invalidates old flow; canceled transport cannot commit.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::PKCE attempts expire at ten minutes, reject repeated callbacks and invalidate on logout/new login` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 95; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Native process killed during hosted browser auth then expired-attempt restart signedout/new attempt is not executed. In-memory expiry is not actual process restart.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 2a1dc62513433c00a879dc85253c52ce3ef0aaae9156439da46eaa4ca2037824. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-005-03 — BLOCKED

auth-signed-out-offline-cache-remains-locked — - **GIVEN** account A selected Keep encrypted records and sign out - **WHEN** A opens the app offline and passes device biometric authentication - **THEN** A's retained cache remains locked until same-issuer/subject reauthentication; biometric success alone does not recreate signed-in state.

Current proof: Sign-out clears credentials/identity and workspace locked scopes reject data publication; biometric alone is not provider identity source.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::sign-out removal finishes after an already-started OS credential write` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 21; 1 current observation(s).
- `apps/mobile/tests/workspace-scope.test.ts::same-owner same-generation response succeeds; locking or backgrounding invalidates the scope` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 94; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual Keep encrypted records→signout→offline biometric success→retained account cache stays locked until sameissuer/subject reauthentication is unexecuted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 7f455e952c1959bcd103231e5e22c11dc7bdf215b2d69bd94b465c08c3b7a9b0. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-005-04 — BLOCKED

auth-canceled-device-unlock — - **GIVEN** the same account is still signed in with readable cached records - **WHEN** the user cancels device authentication on offline launch - **THEN** no account history or profile is displayed and the user may retry or enter isolated demo.

Current proof: Controlled scope unlockedfalse refuses current publication; native store fail-closed guards exist.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/workspace-scope.test.ts::same-owner same-generation response succeeds; locking or backgrounding invalidates the scope` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 94; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual offline account unlock canceled must show zero cached history/profile and allow retry/isolated demo. No native canceled biometric journey admitted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA dcec21540cc9ee45f779d7a4b5cbe7ef5a742ae0a2ffdaeb0360faadd93ea186. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-006-01 — PARTIAL

auth-sign-out-with-pending-check — - **GIVEN** one account check has not synchronized - **WHEN** the user selects sign-out - **THEN** the sheet states “1 check has not synced”; the default retains the locked record, and choosing local removal requires the extra count-specific confirmation.

Current proof: Controller signout clears identity immediately; source counts unsynced checks and defaults retain protected records.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::sign-out records the API receipt before provider revocation and clears local identity immediately` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 212; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Rendered one-check count-specific signout sheet, default retention and extra local-removal confirmation are not asserted in current component/browser tests. Credential removal ordering is a different assertion.

Prerequisite/evidence type: software_assertion_or_integration_evidence.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA fb4860ff9b0c7d189d99b188478e59ac0c10d6dc0c594b04b6f7ccab50464e76. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-006-02 — PASS

auth-late-response-after-sign-out — - **GIVEN** an account-history request remains in flight - **WHEN** sign-out completes and the response later arrives - **THEN** the response is discarded and cannot unlock retained records, recreate removed records, or appear in demo.

Current proof: Actual controller defers history, completes signOut(false), then resolves private old rows; refresh rejects and identitynull/historyRows/historyIndexempty/routewelcome. This proves software late-history publication cannot resurrect signed-out workspace; actual retained encrypted OS files remain separate prerequisite.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/controller.test.ts::delayed history cannot enter another account or reopen a signed-out workspace` — file SHA `9d467077dd365a048585943fcb33b17859535db4bcb8c7741dd48782b16370d0`, line 777; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

All scoped criterion clauses are supported. Fixture limitations and external scientific/OS release gates are not converted into approval.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PASS; record SHA 3d8a8987c7f78e78c734478e8c84d1d5b8019ae50665245ef7005dd034cd6e87. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-006-03 — PARTIAL

auth-default-signout-retains-locked-pending-data — - **GIVEN** account A owns two unsynchronized checks - **WHEN** the default sign-out action completes and account B signs in - **THEN** A's encrypted records remain locked and unuploaded; B cannot list, unlock, or queue them.

Current proof: Delayed old logout and refresh cannot replace currentB identity/UI; account stamps excludeA responses.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/workspace-scope.test.ts::delayed history, job or study responses cannot publish into another account` — file SHA `d009b00717789b980a437f76ee379dbf1f3771aac46021d718f649b30544339d`, line 31; 1 current observation(s).
- `apps/mobile/tests/auth.test.ts::a stale refresh response cannot clear or overwrite a newly signed-in account` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 252; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Two unsynchronized A encrypted records default-retained then B login must explicitly remain locked/unuploaded and unlistable/unqueuable byB; current races do not inspect those retained record IDs or queue state. Actual native storage proof separate.

Prerequisite/evidence type: software_assertion_or_integration_evidence, native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / PARTIAL; record SHA 2f38b2e375db1764380c94639cfbcc37f68bf6acd4da297dde0094d8f64e6d6b. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-007-01 — BLOCKED

auth-accessible-browser-return — - **GIVEN** TalkBack or VoiceOver is active - **WHEN** the browser is canceled - **THEN** focus returns to the sign-in heading and the cancellation message is announced once with Try again reachable.

Current proof: Auth cancel returnsnull and no token exchange; cancellation message route exists. Current DOM focus restoration, modal semantics, contrast and reduced-motion assertions are executed; no actual TalkBack/VoiceOver/native OS claim.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/auth.test.ts::cancelled, wrong-state, duplicate and invalidated callbacks cannot exchange a code` — file SHA `4fe1cf28a5cbd70e1b35528ead96f32090f47b4025bfad9b5fc09eca24f67827`, line 147; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual TalkBack/VoiceOver browser cancellation focus returns heading, single announcement and Try again reachable unexecuted. Current DOM focus/reduced-motion software repairs have current named observations; actual OS scenario remains unexecuted.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA 879b7119c98948429e0973c491142360403b3804dc71b3ffb3b6259eeffce81d. Actual current source and raw evidence supply this disposition.

## OTGD-037-AND-AUTH-007-02 — BLOCKED

auth-ios-secure-storage — - **GIVEN** an iOS sign-in completes - **WHEN** app storage and logs are inspected - **THEN** refresh credentials are confined to the approved Keychain path and no token appears in ordinary preferences, logs, or check exports.

Current proof: Serialized vault removes credentials in proper ordering; native source selects approved secure store; diagnostics excludes tokens.

Current source assertions (full body/helper hashes and exact execution references are in the central source index):

- `apps/mobile/tests/lifecycle.test.ts::sign-out removal finishes after an already-started OS credential write` — file SHA `a69785a96f7fbe8c6193ba617741db43650cf9ad32a2eb595d92bf04ae9a4099`, line 21; 1 current observation(s).
- `apps/mobile/tests/support-history.test.ts::support diagnostics copy only bounded explicit fields, never an error payload` — file SHA `69eb3cea0dd3adba88f964c5b9fedd872f60b0488d53aad4fd242320aecf5f69`, line 10; 1 current observation(s).

Actual current raw artifacts:

- `/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/verification/evidence-snapshots/repo/reports/unit-coverage.log` — SHA256 `67fea75b905579ae4b1d5c0cf1f034dd6a32bd11dfa83cd3701bd7cf47763499`.

Exact unproved clause(s):

- Actual iOS Keychain path/file/preferences/log/export inspection after sign-in not executed. JavaScript vault double cannot establish Keychain confinement.

Prerequisite/evidence type: native_os_execution.

Minimal next action: review the referenced current shared assertion/helper/control-flow proof for the literal clause above; supply a targeted observation or the identified external prerequisite if it is available. Preserve PARTIAL/NOT_RUN/BLOCKED if it is unavailable. This is not an implementation-defect finding or permission for a new correction round.

Baseline history: 28e07295cb37bb9dcaaac82cc8fc846eb89006a6 / BLOCKED; record SHA caef02b2b363ca2ad3c38510679c88d455fe0f8d9391c22d1683c72523c75449. Actual current source and raw evidence supply this disposition.

