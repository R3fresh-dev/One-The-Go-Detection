# Task 6 ordinary-web live browser implementation

Owner: OpenAI browser builder, delegated by sole Factory PM. Run `otgd-20261025-0555`, branch `factory/one-the-go-detection-20261025`. D001v1/D002v1/D003v1/D004v1/D005v1/D006v3 and later D006v4 acknowledged AFFECTED. D006v4 is bounded PM-controlled current-source app-only runtime recreation; PG/LocalStack/journal/probe retained; no original cloud image claim. Correction0/2, recovery0/3 unchanged. This is implementation evidence, not independent signoff.

Status: Task6 live browser journey verified in both Chromium viewports against actual local services after three demonstrated defects were repaired. Final live run2/2passed, full mobile unit274/274passed with zero skips, focused auth/controller28/28passed, typecheck/export exited0. All owned production/test sources and port8082/dist released to PM. Final source-image refresh, exact frozen-candidate aggregate gates, CI and independent council decisions remain PM-owned and pending; this report is not app-complete or release signoff. No Docker mutation, deployment, merge, participant operation or journal reset was performed by this builder.

Owned changes:

- `apps/mobile/e2e/authenticated-live.spec.ts` and `playwright.live.config.ts`: actual ordinary Expo export, real issuer popup with S256 PKCE/exact callback, separate notice/profile/context, fictional measurement-only save and explicit upload; actual server finalization acknowledgement loss and exact accepted-receipt/idempotency-key replay; queued result/export; exact downloaded ZIP inventory, IDs, source/provenance and SHA256; memory-only reload and reauthentication/history; real foreign issuer identity denial; explicit fictional study consent/withdrawal and denied research start; actual deletion acknowledgement loss and pending intent; retired generation denial, new workspace acknowledgement, logout/family refresh refusal. Two Chromium viewports, no retries, no mock success responses. Credential-bearing traces/HAR/video disabled; explicit redacted evidence only.
- Default guest config excludes the new live file. README documents independent guest gates and live prerequisites.
- `infra/local/browser_fixture.py`: private bounded preserved namespace ledger; exact local origins, reserved identities, known accepted session/profile/study references; symlink/public/unbounded/unknown-record admission refusal. Optional maintenance-only governed provisioning reuses immutable registry workflow with exactly dedicated browser staff and UUID fictional studies. No cleanup/reset or human/scientific authority.
- Authorized extension `local_oauth_state.py`: exactly browser_mobile/browser_desktop/browser_staff added to local enum. `local_identity.py`: clearly fictional Mobile/Desktop buttons only. No origin/PKCE/state/token logic changed; backend staff has no consumer button.
- Authorized optional `participant_probe.provision(..., staff_subject=...)`: default remains local-participant_probe_staff; browser passes local-browser_staff. Original staff and scopes are untouched. Direct routing tests stop at identity boundary and establish default/override selection; these are not real database evidence.

Verification executed so far:

| Check | Observed result |
|---|---|
| New reserved Mobile/Desktop issuer tests before extension | 2 expected failures: absent reserved buttons/identity admission; arbitrary account negatives passed |
| New backend staff test before enum entry | Expected failure: authorization refused400 instead of303 |
| `uv run --project services/api pytest services/api/tests/test_browser_fixture_staff.py services/api/tests/test_local_identity.py services/api/tests/test_local_oauth_security.py -q -m 'not postgres'` | 37passed,4PostgreSQL cases deselected,1existing TestClient deprecation; final fixture/issuer source |
| `python -m unittest infra.test.test_browser_fixture -v` | 4passed; private ledger/origin/identity/inventory refusal. Initial absent-module and absent-helper runs failed with import/attribute errors, not claimed as behavioral RED evidence |
| `npm run typecheck` | Initial concurrent mobile change failed checks.tsx1721 Json/ReactNode; mobile owner fixed. Subsequent runs passed, including final TS harness edits |
| `npm test` | 267passed,0failed,0skipped; `/tmp/otgd-browser-mobile-unit.log` |
| `uv run --project services/api pytest services/api/tests -q -m 'not postgres'` | 1339passed,20PostgreSQL cases deselected,1existing warning; `/tmp/otgd-browser-api-suite.log`. Started before two new staff-routing cases were written; focused37 run covers these separately |
| Bare root pytest attempt | Failed collection: infra/test/test_cloud_endpoints.py ModuleNotFoundError deploy; invocation corrected to API tests. `/tmp/otgd-browser-python-suite.log` |
| Unfiltered focused identity+security attempt under isolated default SQLite | Four mandatory PostgreSQL-marked cases correctly failed infrastructure assertions; not a PostgreSQL PASS. PM owns actual disposable PostgreSQL gate |
| `CI=1 ... npx playwright test --config=playwright.live.config.ts --list` | Exactly2 viewport cases discovered; not execution evidence |

Runtime source refresh: firmware specialist notified to include final fixture bytes; no later image-source edits planned. Preserved host ledger `/tmp/otgd-browser-fixture.json`, namespace `fictional-browser-6a1246886f3240f2b8ddba15c1f8764a`. It contains no credentials. Must preserve across retries.

PM integration (builder does not own scripts/CI workflow): run fixture through canonical maintenance wrapper with `--confirm-fictional-workspace --manifest <protected writable copy> --provision-governed`, read back its public fictional locator JSON into the private host ledger. Then from mobile: `CI=1 OTGD_BROWSER_FIXTURE=/tmp/otgd-browser-fixture.json PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npx playwright test --config=playwright.live.config.ts`. Add that exact suite to localstack-api and matching CI; preserve guest/component commands. Actual wrapper command/output will be recorded after PM provides it.

Remaining requirements at the initial handoff (resolved live execution is recorded below): actual two-viewport live execution and redacted receipt/archive evidence; gate integration by PM; exact-source whole required gates and independent reviews. Browser memory-only behavior provides no native SQLCipher/OS lock/device/physical/scientific qualification. Future alcohol remains separate calibrated fuel-cell mg/L scope. Measurement/default/no-model and fictional provenance remain unchanged.

Exact proposed PM maintenance command (not yet executed by this builder):

```bash
docker compose --project-name otgd-local --env-file infra/local/.env \
  -f infra/local/compose.yml run --rm --no-deps \
  --volume /tmp/otgd-browser-fixture.json:/tmp/otgd-browser-fixture.json \
  migrate uv run --no-sync python /app/infra/local/browser_fixture.py \
  --confirm-fictional-workspace --manifest /tmp/otgd-browser-fixture.json \
  --provision-governed
```

The writable single-file bind retains the private host ledger and its ownership
history across maintenance exit. No PostgreSQL/LocalStack restart, volume reset,
Account A/B cleanup, or participant staff role mutation is part of this command.

## Live execution and demonstrated defects

PM released actual runtime after D006v4 verified RoundC source adoption and all app services healthy; governed fixture provisioning exited0 and updated the preserved private host ledger. PostgreSQL/LocalStack/journal/probe were retained.

1. Actual two-viewport run `/tmp/otgd-browser-live-run1.log`: both failed before sign-in at issuer `400 invalid_request`. Installed Expo AuthRequest source defaults to ten-character state; issuer intentionally requires16..256. The numeric outgoing-state assertion reproduced RED (`Received10`, `/tmp/otgd-browser-state-red.log`) without logging state/code/token values. No browser profile/session was accepted; ledger counts0/0.
2. PM authorized smallest auth client correction. `auth.ts` now passes `state:newId()` using the existing cryptographic platform UUID (36characters; web Crypto/native ExpoCrypto). The directly related auth unit adapter previously overwrote explicit state with UUID and masked this defect; it now honors explicit state and mirrors the SDK's ten-character default. New fresh-state/allowed-character/length regression was RED, then11/11 focused auth cases GREEN, including prior wrong-state/cancellation/invalidation checks. `npm run typecheck` and ordinary `CI=1 EXPO_PUBLIC_HOSTED_PREVIEW=false EXPO_NO_TELEMETRY=1 npm run export:web` exited0. Full mobile unit suite268passed/0failed/0skipped (`/tmp/otgd-browser-mobile-unit-final.log`).
3. The next actual run passed issuer GET/state admission but stalled before callback completion. Builder interrupted only its own test process after~1minute to add bounded sanitized diagnostics; result is1interrupted/1not run, not a pass. No browser profile/session was accepted. The following mobile diagnostic failed after15seconds with popup still on issuer authorize form; a further sanitized diagnostic confirmed `formRedirectBlocked:true` for CSP `form-action`. No code/token/query values were logged (`/tmp/otgd-browser-csp-red.log`). Issuer's `form-action 'self'` prevents the configured303redirect to the browser callback's different origin. PM notified; backend source remains frozen pending coordinated correction/adoption. Existing issuer grants are left to normal one-use/expiry rules; none are manually deleted or repurposed.

Current blocker: exact action is changing the local issuer CSP to permit the already configured browser callback origins, then PM identity-image refresh and actual rerun. Target `services/api/otgd/local_identity.py`; reason is demonstrated browser redirect refusal. Permission/recreation is pending PM coordination with the real worker matrix; no denial or uncertain Docker action by this builder. Proposed focused header regression plus actual-browser validation; do not bypass CSP or weaken origin/PKCE/state guards.

D007v1 acknowledged AFFECTED. PM released only `local_identity.py` for the demonstrated CSP repair; the concurrent worker preflight must report its known all-otgd source drift as failure, and a fresh final frozen-source matrix remains mandatory. No hash or assertion is relaxed. PM plans an exact read-only source-file identity bind for browser preflight and a final full source-image refresh after fixes settle.

CSP header regression: expected RED1failed/1native-only-pass, then focused identity/security/staff GREEN39passed/4PostgreSQL-deselected/1existing warning. Logs `/tmp/otgd-browser-csp-unit-red.log`, `/tmp/otgd-browser-csp-unit-green.log`. Released local issuer source SHA256 `1576b35868abd7a22b402f2efea4777b6d34dcfb786e8670350b915972bc1e9e`. Form policy adds only `web_origins(settings)` already derived from exact registered OAuth callbacks; issuer self origin, default-src none and frame-ancestors none remain. No wildcard, alternate token, CSP browser bypass, broader callback admission or weaker POST-origin/PKCE/state check was added. Actual browser confirmation awaits PM identity recreation/readiness.


## Final live result and released client repair

Final actual command, run from `apps/mobile`:

```bash
CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright \
  OTGD_BROWSER_FIXTURE=/tmp/otgd-browser-fixture.json \
  npx playwright test --config=playwright.live.config.ts
```

Observed2/2passed in31.1seconds: mobile14.4s at412x839, desktop14.9s at1440x1000. Log: [browser-live/playwright-live.log](browser-live/playwright-live.log). [Machine summary](browser-live/summary.json), [mobile redacted receipts](browser-live/live-mobile/redacted-live-receipts.json), [desktop redacted receipts](browser-live/live-desktop/redacted-live-receipts.json), [mobile downloaded fictional ZIP](browser-live/live-mobile/fictional-structured-export.zip), [desktop downloaded fictional ZIP](browser-live/live-desktop/fictional-structured-export.zip). These ZIPs contain deliberately fictional software fixtures only; their current profile excludes personal demographics from the synthetic check snapshot.

| Viewport | Archive bytes / members | SHA256 |
|---|---|---|
| Mobile412x839 |3190 /3|`b88a6b164c5fdcfd3476c7284dbfcb7a32c365be981744b515dc7c4d930fc8a0`|
| Desktop1440x1000 |3188 /3|`83111f88049a154faf2dbac4bdfe1fa9758f5e68cb4f7181c11d303c6cc1fd44`|

Each viewport actually completed issuer S256 PKCE/callback/state admission; separate application notice, profile and context; synthetic measurement-only frozen save with zero server session creation until explicit upload; server-accepted finalization with dropped acknowledgement, same idempotency key and exact receipt replay; real queued result; memory-only reload requiring sign-in, empty browser history then explicit owned server retrieval; exact structured cloud export with every declared member digest, closed file inventory, single selected session, synthetic provenance and null impairment probability; independently authenticated foreign session/export404; separately fictional study consent, withdrawal receipt and subsequent research-start403; accepted deletion acknowledgement dropped after the real request, visible pending intent, worker completion, retired-generation refusal and revoked archive access; reload/re-authentication and explicit new-generation acknowledgement; API logout200, actual provider revocation200, revoked refresh400 and signed-out welcome UI. Browser network origins were exactly localhost8000/8081/8082. No mock-success transport was used.

Accepted export/deletion receipt JSON deliberately retains its original `pending` state as received. Completion was independently awaited through actual job-status endpoints before downloading and before acknowledging the new generation; the passed executable assertions bind those later observations. Receipt JSON is not rewritten into a claimed completion receipt.

Third demonstrated defect and repair: final browser run4 returned401 on `/v1/auth/logout` in both viewports after all prior paths succeeded. The client started provider-family revocation before requesting the API logout receipt; the server correctly refused a new operation from the revoked family. PM approved a bounded client fix after checkpoint6. `AuthManager.captureProviderRevocation()` captures the old refresh family without network activity; `AppController.signOut` clears local credentials immediately, attempts the API receipt first, then invokes the captured revocation. A memoized `finally` fallback also attempts that exact old-family action when API logout fails or a replacement login supersedes old UI work. Old flows cannot open provider logout or overwrite a replacement account after awaits. Provider HTTP non-success now rejects with `AUTH_REVOCATION_UNCONFIRMED`, and the user sees the existing unconfirmed-revocation warning; no server fail-closed check changed.

Regression evidence: ordering, API-failure fallback, provider HTTP failure, no credentials, replacement before API work and replacement after delayed API response are covered. Initial focused run was RED for early provider request/order, HTTP failure being treated as success and late-account ordering. Final focused auth/controller28/28passed; full mobile suite274passed/0failed/0skipped (`/tmp/otgd-browser-mobile-unit-release.log`); typecheck and ordinary export exited0; formatting and `git diff --check` passed. The prior run3 failure was a harness read racing the asynchronous generation acknowledgement; it now waits for the actual POST200 before asserting active state. Prior accepted deletions were reconciled by reading capabilities first and explicitly acknowledging a completed generation when necessary; no reset or journal cleanup was used.

Additional authorized owned files: `apps/mobile/src/services/auth.ts`, `src/controller.ts`, `tests/auth.test.ts`, `tests/controller.test.ts`, and directly related `tests/support/auth-session.cjs`. Backend/image source stayed unchanged during this client repair. CSP preflight runtime used PM-verified exact read-only identity source overlay SHA1576b358...; it is disclosed preflight evidence, not a claim that the old base image digest contains the change. All code/tests released final to PM after live pass. Browser dedicated accounts finished active with empty current data generation4, and the final main-test sign-in families were revoked by logout; foreign read-only probe contexts were closed without asserting remote family revocation, and earlier unused authorization grants remain under normal one-use/expiry rules; unrelated accounts, registries, staff scopes, PostgreSQL/LocalStack identities, protected journal and retained prior receipts were preserved.

Outstanding boundaries: final current-source image adoption and frozen full worker/aggregate/CI gates; independent security/UX/UI/code/product/engineering/council review; native custom-scheme CSP behavior, native identity persistence/SQLCipher/OS controls and physical/scientific qualification remain separately unexecuted here. No browser result implies native OAuth success, participant authorization, clinical validity, alcohol sensing qualification or fitness to drive. Formal correction0/2 and recovery0/3 remain PM-owned and unchanged.
