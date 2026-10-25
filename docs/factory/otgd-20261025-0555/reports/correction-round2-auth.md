# SEC-02 returned callback validation — author evidence

Run `otgd-20261025-0555`; reviewed candidate `cf74fcff6ad19e639538d260f223ec18d618658d`; D010v1 acknowledged before dependent work. Correction **2/2**, recovery **0/3**. This is implementation evidence, not independent signoff or final gate approval.

## Actual RED

The reviewed AuthManager validated its requested callback but ignored the successful SDK response's `url`. Installed `expo-auth-session` returns that URL alongside parsed params; its parser does not establish exact callback-target admission. The app must enforce the selected compiled target itself.

Before editing production, four new callback regressions failed with missing expected rejection. A separate actual AppController/AuthManager execution using the explicit Android SDK/platform and fictional HTTP adapters selected `otgd-local://oauth/callback`, then received matching current state/code at `otgd-local://oauth/callback-extra`. Sign-in returned true, made **one token exchange and one protected capabilities lookup**, and switched to the fixture's different fictional account. This reproduces the app defect; it is not an executed Android/iOS OS exploit, issuer redirect-policy bypass or arbitrary account-takeover claim.

Raw `callback-red.log`, `red-native-observation.json`, `red-observation.json` and exact reviewed `reviewed-auth.ts` are preserved under `/workspace/scratch/otgd-20261025-0555-live/correction-round2-auth/`. Reviewed auth SHA256 is `c1f9ef918b2f2b8a1f52a82937a3576d51d232b89aa7f5656aa3d87156c15cc9`. The initial RED test source SHA256 was `8b53f0b4b47b56ccba5dcef841706c1da286bf252fb0db24d0c5a11555e43262`; the final test adds further same-boundary refusal controls and formatting.

## Narrow repair and assertions

`services/auth.ts` now admits the actual returned success URL before attempt consumption and exchange. Its original target bytes must exactly equal the callback selected for this pending platform/build, rather than another callback from the build allowlist. It rejects fragments, missing/malformed targets, suffixes, userinfo/port/path aliases and malformed percent syntax. The query must contain exactly one code and one state, with no additional fields or empty extra pair, and both must match the successful SDK params/current request state. No callback query, authorization code or token is included in the refusal message.

Outgoing endpoint/callback pins, cryptographic state, S256 PKCE, attempt expiry/single use, token refresh coordination, immediate credential clearing, captured-family revocation and API-before-provider logout remain unchanged. No controller production, UI, e2e, metadata admission, backend or workflow edit was made.

`auth-callback.test.ts` executes actual AppController/AuthManager logic through the existing explicitly fictional SDK/network adapters. Four test cases contain **five exact successful callback controls** and **42 refused callback deliveries**: web/Android/iOS selected-target positives; scheme/host/port/path/suffix/userinfo/dot-segment/other compiled callback/fragment substitutions; missing/non-string/malformed/empty URL; duplicate/unexpected/missing query fields; mismatched code/state; and a fresh valid retry after refusal. Every refused delivery requires **zero HTTP**, unchanged application/Auth identity and unchanged auth generation. Thus neither token fetch nor account lookup occurs. These are software platform fixtures, not native OS execution.

Auth-specific success fixtures now include the SDK's actual `url` field explicitly. The shared runtime supplies it only in its default fictional successful response; it does not synthesize a URL for arbitrary overrides, so missing-URL regressions remain meaningful. The mobile owner approved the sole `controller.test.ts` change: four lines adding the URL to its existing prompt-reset response. No controller test behavior was otherwise changed.

## Actual GREEN

Final command from `apps/mobile`:

```text
node --import tsx --test --test-timeout=20000 --test-reporter=spec --test-reporter-destination=stdout --test-reporter=junit --test-reporter-destination=/workspace/scratch/otgd-20261025-0555-live/correction-round2-auth/auth-release.xml tests/auth-callback.test.ts tests/auth.test.ts tests/auth-cognito.test.ts tests/auth-acceptance.test.ts tests/service-boundary.test.ts tests/api-deadline.test.ts tests/controller.test.ts tests/unit-build-isolation.test.ts tests/hosted-preview.test.ts tests/oauth-build.test.ts
```

**99 passed, zero failed/cancelled/skipped/todo**, exit0, 3.914 seconds. Raw `auth-release-final.log` and actual runner-generated `auth-release.xml` retain the assertions and results. Initial focused green was31/31 and expanded first green99/99; both logs remain. Existing successful-callback replay, three actual loopback HTTP401 requests/one refresh/original operation replay, endpoint substitution, distinct Cognito origin, logout ordering/races, guest no-network and actual-workflow unit fixture isolation all executed.

Prettier check and `git diff --check` exited0. Full mobile unit coverage, typecheck and browser execution are assigned to the mobile owner; they were not run or claimed here. Current frozen local/all14CI gates, current case rebind and independent confirmations remain pending. Native OS browser/storage/device, physical/scientific, cloud deployment and participant-use prerequisites remain separate.

## Release and exact bindings

Owned changed/new files: `src/services/auth.ts`; `tests/auth-callback.test.ts`; `tests/auth.test.ts`; `tests/auth-cognito.test.ts`; `tests/auth-acceptance.test.ts`; `tests/support/runtime.cjs`; and the coordinated prompt-reset block in `tests/controller.test.ts`. This author report is also released.

Final auth SHA256 `bcb384ac846cccd8796ec4a35b85c4aa92cab65221ac6dda3a075163a5770c62`; final callback test SHA256 `d4d89af5fcce9d3d7c902d89eea1c0b72cbb09be274a962d56358dc801e6ead8`. Full source/dependency/report/raw evidence bindings and XML counts are in external `source-evidence-hashes.json`; exact owned source copies are retained externally. No installs, Docker/service changes, browser ports, retained-data operations, git commits/pushes, deployment or merge occurred. All owned writes are released.
