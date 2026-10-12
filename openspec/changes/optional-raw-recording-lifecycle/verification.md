# Software verification evidence

On 2026-10-11, the mobile unit gate passed 241 tests with zero failures, skipped,
canceled or TODO tests. The complete executable `apps/mobile/src/**/*.ts`
inventory measured 89.47% line coverage: 15,235 of 17,028 lines. Unloaded
modules remain in the denominator, including native sharing at zero. The
generated report is `apps/mobile/reports/mobile-unit-coverage.json`, whose
source inventory SHA-256 is
`71d11aa2b130bd192a48caa6d0e203a08d507ec7065573d636a6a174982dc45b`.

The commands were `npm run typecheck`, `npm run format:check` and
`npm run test:coverage` from `apps/mobile`. Strict OpenSpec validation passed
with `openspec validate optional-raw-recording-lifecycle --strict`.

The tests exercise actual controller, domain, transport, queue and archive
readers. Native storage tests replace the operating-system boundary and do
not establish SQLCipher or keystore qualification on a physical phone.
Actual Python-produced optional-preference, capture-grant, optical-evidence,
retained-source export-scope, worker ZIP and revoked-job fixtures verify wire
compatibility. The signed ECG fixture is produced by the real client encoder
using a clearly fictional test key and measured-shape test samples; it does
not establish instrument calibration or human validation.

Covered failure cases include default-off independent raw choices, account
and generation reset, offline revocation fences, expired-byte denial and
orphan cleanup, atomic raw/index rollback, cancellation during decryption,
lost-response identity replay, acknowledged-ticket renewal, early camera
failure without invented acquisition clocks, exact signed sample scope,
separate export authority, raw-source substitution, unselected ZIP paths,
and export-only revoked receipts. Device-binding recovery tests also reject
a delayed receipt or persistence operation that could otherwise bind a
replacement reader or erase a newer request.

The standalone cache-cleared fictional export passed both mobile and desktop
Chromium acceptance cases. The browser asserts zero external service requests,
zero camera or Bluetooth acquisition, absent account/upload controls, fictional
local saving, and memory-only records reset on reload. A real packaging failure
revealed that Metro can reuse a normal build's transformed environment values;
both normal and fictional web exports now clear that cache. These assertions
apply to the compiled preview, not a runtime flag applied to an ordinary build.

The final cache-cleared normal web export passed all 30 Chromium tests across
mobile and desktop viewports. This includes 10 application component cases,
6 complete customer journeys and 14 raw-purpose, upload, independent-export
and conditional-capability component cases. The commands were
`EXPO_NO_TELEMETRY=1 npm run export:web` and
`CI=1 OTGD_CHROMIUM_PATH=/usr/bin/chromium npx playwright test`.
The hosted command was `npm run export:preview` followed by the same
Playwright environment with `--config=playwright.preview.config.ts`.
All 32 browser cases passed with no skipped cases.

Independent adversarial review passed the final binding-recovery branch and
ran 24 acquisition/physical-protocol cases without skips. Final controller
SHA-256 is
`705750874222158c9dc29040a37e4fca3208c5a507488d0955333fc9c08e97d7`.

Actual native build results and real cloud dependencies are separate required
gates. The final coordinated backend,
worker, mobile, Docker health, LocalStack, performance and exact-revision CI
evidence must pass before merge. Physical camera timing, device calibration,
scientific qualification and App Store publication are not established by
these unit tests or fictional browser fixtures.
