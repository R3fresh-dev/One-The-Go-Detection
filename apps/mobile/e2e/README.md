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
