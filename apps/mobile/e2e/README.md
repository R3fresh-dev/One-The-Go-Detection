# Browser acceptance and component checks

These tests load the actual Expo web export of `apps/mobile/App.tsx` in Chromium.
Both projects run every test: a Pixel 7 viewport and a 1440 × 1000 desktop viewport.
The server binds only to `127.0.0.1:8082` and serves `dist`; a build is required before testing.

From `apps/mobile`:

```bash
npm ci
EXPO_NO_TELEMETRY=1 CI=1 npm run export:web
npx playwright install --with-deps chromium
CI=1 npx playwright test e2e/mobile.spec.ts
CI=1 npx playwright test e2e/components.spec.ts
```

Use `npm run test:e2e` to run both suites together. For an already installed local
browser, supply `OTGD_CHROMIUM_PATH=/usr/bin/chromium`; CI normally installs the
Playwright browser. The cloud host verification used Chromium 154.0.8037.57.
Tests have no retries and retain traces and screenshots for failures. The HTML
report is in `playwright-report`; downloadable archives and traces are in
`test-results`. These directories are generated evidence, not application source.

`mobile.spec.ts` is the browser acceptance gate. It covers explicit guest entry,
separate notice and context acknowledgment, synthetic sample/eye/ECG values,
the unavailable native reaction task, measurement-only saving, privacy/settings,
profile errors and reload behavior. The actual downloaded ZIP is opened and
checked for exact single-check scope, null impairment probability, associated
context/evidence, and every declared file's SHA-256 digest.

`components.spec.ts` is the browser DOM component gate. It checks enabled and
disabled controls, accessible validation and first-error focus, metric/imperial
conversion, unsaved-edit cancellation, named modal dialogs and hidden background
controls, separate unsynced-data confirmation, exact history selection across
filters, keyboard navigation, theme changes and minimum tab target size.

Guest tests deliberately block account API requests. They establish offline
browser behavior and never substitute for real API, PostgreSQL, LocalStack,
identity, Docker-health or performance checks. Browser storage is memory only;
reload clears the workspace. This is the shared application UI, while SQLCipher,
SecureStore, OS unlock, Bluetooth, camera restrictions and reaction timing require
installed native builds and their separate verification gates.

To try the same UI interactively after exporting, run `npm run serve:web` and
open `http://localhost:8082`. Choose **Explore demo**, then **Start demo**. External
access requires the environment's private forwarding mechanism. Hosted native
iOS interaction additionally requires a compiled simulator build and a service
such as Appetize; browser success does not imply that build or an App Store release.

The mandatory live ordinary-web suite uses `playwright.live.config.ts`, selects
only `authenticated-live.spec.ts`, and runs Chromium in the same two viewports
with one worker and no retries. The default guest config explicitly excludes
this file; guest/component checks stay independently executable.

Prepare the canonical fictional local stack with `scripts/local-platform.py`
and the matching localstack-api gate. The identity image must include the two
reserved `browser_mobile`/`browser_desktop` fixture accounts and the backend-only
`browser_staff` identity. Never use Account A/B or participant-probe identities
for browser cleanup. The actual callback must be `http://localhost:8082/`.

Prepare the private fixture ledger from the repository root:

```bash
python infra/local/browser_fixture.py --confirm-fictional-workspace \
  --manifest /tmp/otgd-browser-fixture.json
python -m unittest infra.test.test_browser_fixture -v
```

The gate's local maintenance wrapper then runs the same helper with
`--provision-governed` using the canonical maintenance environment, carrying
that private manifest into the container and its updated public fictional
study locators back to the same host manifest. This runs the existing immutable
registry workflow under a distinct browser-only staff account. It preserves
prior staff scopes, all unrelated records and the protected deletion journal.
No human enrollment or scientific authority follows from these software fixtures.

After fixture setup, from `apps/mobile`:

```bash
EXPO_PUBLIC_HOSTED_PREVIEW=false EXPO_NO_TELEMETRY=1 CI=1 npm run export:web
CI=1 OTGD_BROWSER_FIXTURE=/tmp/otgd-browser-fixture.json \
  npx playwright test --config=playwright.live.config.ts
```

The suite serves ordinary `dist` on port 8082. `dist-preview` remains isolated.
Missing live services, callbacks, fixture identities or private ledger fail the
gate. Browser credentials come from the actual issuer PKCE popup, never a
replacement token. Actual API results and queued S3/SQS worker jobs must finish;
no mocked successful response can satisfy the journey. Lost-acknowledgement
checks forward the real server request before dropping its response. Before
any all-data deletion, server session IDs must be a subset of the ledger's
accepted browser session IDs; an unexpected row stops the test and preserves it.
Keep the ledger on retries so a failed run never loses its ownership evidence.

`test-results-live` stores fictional structured ZIP evidence and redacted JSON
receipts including viewport, origins, network destinations and archive SHA-256.
`playwright-live-report` stores the HTML report. Traces, HAR, screenshots and
videos are disabled for this suite to keep OAuth codes, bearer credentials and
signed URLs out of artifacts. A memory-only browser reload loses local records
and credentials; the test reauthenticates and explicitly retrieves server
history. This provides no native encrypted-persistence or physical-sensing evidence.
