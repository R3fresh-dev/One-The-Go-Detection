# Bounded round1 auth acceptance assertions — preflight

Run otgd-20261025-0555, D009v7 acknowledged, correction1/2 and recovery0/3 unchanged. Checkpoint9 base52ffa1044e787f7fea088c82797d4525af02e9a3. Repository changes are solely new apps/mobile/tests/auth-acceptance.test.ts; no production edits, credentials, service changes or browser-port use.

## Coverage inspection and exact criteria

Read current auth.test.ts, api-deadline.test.ts, controller signIn, AuthManager, ApiClient, AuthorizationAttemptGuard and canonical OTGD-037 test-plan before additions. Historical coverage at /tmp/otgd-correction-mobile-coverage.log reported auth97.24% lines and API93.26%, but high percentages did not demonstrate these missing scenarios. The existing callback test title included duplicate; its body tested cancel, wrong state, invalidation and absent callbacks, never a successfully exchanged callback replay. Existing refresh case used two direct accessToken waiters rather than three HTTP401 requests. New tests preserve all existing assertions.

OTGD-037-AND-AUTH-002-01: actual AppController/AuthManager signIn succeeds through the test SDK adapter, exchanges a code with the PKCE verifier and adopts the protected fictional account. A subsequent signIn receives the identical already-exchanged state/code. A different service candidate account makes an accidental switch observable. Assert OAUTH_REJECTED, exactly one total token exchange, no additional protected capabilities lookup, original UI/Auth identity, unchanged auth generation and original access token. This is application logic with the existing explicit fictional SDK/network adapters; it is not an actual OS browser/PKCE transport execution.

OTGD-037-AND-AUTH-004-01: three actual ApiClient requests use locally unexpired but server-rejected fictional access. An ephemeral127.0.0.1 HTTP fixture and real Node fetch send three actual401 responses. The admitted fictional issuer token URL alone is remapped to that fixture; production metadata admission remains unchanged. Actual AuthManager refresh is held until all three request recoveries are waiting. Assert one refresh request with exact refresh grant fields, three original requests before release, six total API captures afterwards and exactly two captures per operation. For each pair compare exact original method/path/serialized body/idempotency key/generation/ETag; only bearer changes from old to rotated. All three200 results and unchanged account identity are required. This proves HTTP client/auth coordination, not live canonical API/identity deployment.

Verification specialist independently inspected the complete new bodies and confirmed both exact missing assertions are covered; old candidate rows remain historical/PARTIAL until replacement binding.

## Actual execution

Focused new file: node --import tsx --test --test-timeout=20000 tests/auth-acceptance.test.ts =>2passed,0failed/cancelled/skipped/todo; /tmp/otgd-auth-finalassertions-first.log.

Focused combined: node --import tsx --test --test-timeout=20000 tests/auth-acceptance.test.ts tests/auth.test.ts tests/auth-cognito.test.ts tests/service-boundary.test.ts tests/api-deadline.test.ts =>69passed,0failed/cancelled/skipped/todo,2.066seconds; /tmp/otgd-auth-finalassertions-release.log. npm run typecheck =>exit0; /tmp/otgd-auth-finalassertions-typecheck.log. Prettier newfile unchanged and git diff --check exit0.

No baseline production defect was demonstrated. Isolated source copies under /tmp/otgd-auth-assertion-mutants intentionally changed one behavior each; original repository sources were never mutated. Removing callback state comparison fails00201 with missing expected rejection. Disabling shared refresh join fails00401 with AUTH_CHANGED because independent refreshes race. Altering only the replay Idempotency-Key fails00401 exact operation equality. All three isolated runs returned exit1 with one failed case and one passing case; exact records /tmp/otgd-auth-assertion-mutations.json and /tmp/otgd-auth-mutant-{callback-state,refresh-join,replay-key}.log. These controls show meaningful failure detection, not repaired production failures.

## Binding and limits

/tmp/otgd-auth-finalassertions-hashes.json binds the new test,13 direct source/adapter dependencies and seven raw logs/records. Newtest SHA256 a90f860a3dafbd0f83a8c7a0c35cc6dea8bff167aa0585ed70b1ed2c8341b164. Auth SHA256 c1f9ef918b2f2b8a1f52a82937a3576d51d232b89aa7f5656aa3d87156c15cc9. API SHA25655987fdae9b06762e5e31118a52f64eb6256e782fe921b3c5b16674cfd1f0e94.

No new actual ordinary-web/native/physical/cloud run occurred during this bounded task. Existing prior browser evidence is not rebound or replaced. Final frozen full unit/coverage/all mandatory local and CI gates plus independent current reviews remain PM-owned prerequisites; this report is not signoff. Production auth/API source remains unchanged, with no backend image COPY change from this task. All owned writes are released; no browser8082/8083 use occurred.
