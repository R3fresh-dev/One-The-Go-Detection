# Final-round mobile author correction evidence

ACK D010v1 and D010v2 after reading the persisted decisions/correction-round-2 and preserved cf74fcf code, UX, UI, product and engineering findings. Correction **2/2**, recovery **0/3** unchanged. This is an author preflight, not independent signoff, final candidate acceptance or native/hardware/scientific qualification. No additional source finding was dismissed or scope added.

## CODE-R1-004 / ENG-R1-005 / PROD-CF-003

**True RED before repair.** The actual mounted production ResultScreen/Controller/browser memory store starts with a pending result. An existing queue resumes at its already-finalized phase; actual AppController.tick/SyncEngine calls the existing result GET through a controlled service boundary, verifies the complete signed fictional HR fixture and commits it for the same check ID/epoch. Both browser viewports then fail because only1 GET exists, while a second independent current-display admission GET is required. `hr-mounted-red2.log`:2 failures, expected2/received1. `hr-manual-red.log`:2 failures, a mounted pending result's visible service refresh commits HR but makes0 current-display GETs. These reproduce the review's actual integration gaps without inventing a result or changing authority. The earlier `hr-mounted-red.log` is an invalid fixture setup (already-synced delivery created no queue); it is retained and is not counted as product RED.

**Repair.** The ResultScreen effect now owns a view even before HR is available and depends on the exact saved result digest as well as ID/epoch. Pending/local measurement→first HR therefore replaces the old view token and performs a fresh exact-bound read. Unchanged result bytes do not repeat the effect. Explicit refresh can establish a current view when no prior token exists, only while that same check remains on the active Result route. A new UI-owned result view wins over the captured older view; existing result mismatch, newest-request, owner/generation/epoch, foreground, leaving, offline and late-callback guards are retained. Original HR evidence remains immutable; normal first-result completion still follows existing sync verification/commit. No numerical/scientific TTL, export reuse or new participant authority was introduced.

The new direct controller regression asserts no-prior-token refresh admission and navigation invalidation. Browser assertions cover both pending and locally saved measurement starts through actual SyncEngine completion, stable ID/epoch, withheld-before-current-read, admitted numeric81.8% and exactly2 GETs without a loop. A separate actual manual-refresh scenario recovers from the mounted pending state. All earlier current200,403/422, mismatch, offline/reopen/background/account/generation/late-read and independently admitted local-export assertions still execute.

## UX-R001 / UI-003 / ENG-R1-007 / PROD-CF-001

**True RED before repair.** `device-red.log`:17tests,15PASS/2FAIL. One failure is the actual DeviceControllerImpl operating through the existing framed signed fictional peripheral; its healthy connected_reader snapshot was falsely presented connected=false. The other directly asserts unbound/bound physical presentation. `home-device-red.log`:9tests,8PASS/1FAIL; actual Home JSX falsely renders Reader connection unavailable and blanket qualified-human-unavailable copy instead of the physical state that DevicePanel displays. These are named software boundaries, not real BLE/device/OS observations.

**Repair.** presentDevice now handles a healthy connected_reader/prototype_sensor/current boot/reason-null snapshot independently from service binding, using the same connection/binding wording as DevicePanel. Its badge identifies a signed reader connection; valid simulators keep Synthetic only. Reboot/error/disconnect states do not retain an old connected boot. Connection/binding never supplies channel qualification.

Home and Device now reuse AcquisitionAvailability and presentAcquisitionChannels. They display only an active matching authenticated owner/data-generation observation while online and outside the fictional preview. Each channel independently checks available, software/authorization flags and an existing configuration with expires_at strictly later than the current clock, matching existing acquisition semantics. Expired equality, revocation, missing configuration, mismatched owner/generation and offline data cannot advertise conditional availability. Reasons remain explicit. Connection is deliberately absent from this capability function's inputs; disconnected service-listed capability is still conditional and cannot enable Start. The UI states that each Start needs study, consent, current configuration, installed adapter and fresh server authorization. A small display timer rerenders at the next supplied configuration expiry; it is not a new authority/scientific validity period.

D010v2 manage.tsx edits are confined to the necessary import and the DeviceScreen acquisition Facts/list replacement. Settings/privacy/raw sections, DevicePanel and capability-admission engine were not edited. The existing DeviceController physical test gains only the presentation assertion/import; its actual binding and capture refusals remain. Controlled parsed-capability fixtures separately cover simulator, connected unbound/bound/current/revoked/expired, offline/owner/generation mismatch, disconnect and reboot. Actual Home/Device SSR and browser assertions agree, and a mounted browser-clock expiry removes availability before navigating to Device. No flag, binding, connection or fixture creates scientific/study/capture authority.

## Current checks and evidence

All commands run from apps/mobile. Raw author evidence is retained at `/workspace/scratch/otgd-20261025-0555-live/correction-round2-mobile/`.

| Command | Observed outcome | Raw evidence |
|---|---|---|
| `node --import tsx --test tests/hr-read-admission.test.ts tests/device-presentation.test.ts tests/result-ui.test.ts src/device/tests/physical.test.ts` |37/37PASS,0skip|focused-green.log|
| `npm test` |394/394PASS,0fail/cancel/skip/todo|full-unit.log|
| `npm run test:coverage` |394/394PASS,0fail/cancel/skip/todo;18914/20739 executable lines,91.20015429866436%, strict>80%|coverage.log; copied mobile-unit-coverage.json/mobile-unit-events.log|
| `npm run typecheck` |exit0|typecheck-initial.log|
| `npm run format:check` |exit0|format.log|
| `npx prettier --check src/ui/checks.tsx src/ui/device-summary.tsx src/ui/manage.tsx src/core/devicePresentation.ts src/device/tests/physical.test.ts` |exit0|format-scoped.log|
| `CI=1 EXPO_NO_TELEMETRY=1 npm run export:web` |exit0, current ordinary dist|export.log|
| `Focused browser command below` |8/8PASS16.3s, both viewports|focused-browser-green.log|
| `CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm run test:e2e -- e2e/components.spec.ts e2e/raw-recordings.spec.ts` |80/80PASS2.3m,0fail/skip|full-browser.log|

Exact focused browser command:

```sh
CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm run test:e2e -- e2e/components.spec.ts -g 'mounted pending|manual service refresh establishes|Home and Device|Home expires'
```

Coverage source digest `a29fdc53897feec4251daaeaaf5d517516fe0c6d8f27d04c0025116c4a26e817`. The conservative inventory still counts sharing.native.ts unloaded/zero; bundled boundary tests do not imply actual native OS coverage. Auth owner's released SEC02 source/test changes are included in these combined394 checks; their authorship/report remains separate. The coordinated controller.test.ts successful callback URL fixture is auth-owned; this author did not edit it.

All original component/raw assertions remain. Raw-recordings.spec.ts is unchanged from round1 (SHA889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd). Alcohol's isolated fixture adds only no-op view-lifecycle methods needed by its controlled generic-result rendering; actual controller semantics are tested separately. No production test-only injection route was added.

The final frozen commit, complete seven local gates, all14 current CI jobs, per-case reconciliation and six independent confirmations remain PM-owned and pending. Actual native permission/browser/secure storage/share/accessibility lifecycle, hardware, calibration, scientific/study/participant authorization and deployment/store evidence remain separate. No agents, install, git mutation, Docker/service/data/archive changes, merge, deployment, paid service or participant operation was performed by this author.

## Bound author source/test files

These15 bindings were reread after the final executable edit. Prior candidate/round1 reports remain historical.

```text
5e1c20cb71a72004b32aff1ef9585b61aeb721b2f3336a3862b98b6c3b801e53  apps/mobile/src/controller.ts
11f5d3e659726c77590b06ad56eed8cce8a890d121352d797d46b95ad3cf0cd5  apps/mobile/src/ui/checks.tsx
59eae66daaf4dbfcf0daa7341fb1649b2aa3b092c657fef57c0b6f73460e9768  apps/mobile/src/core/devicePresentation.ts
2b1126a8f49a8c035e2c4ebec7fa57271e7f3b781b8f895c2bf2a31d7074233d  apps/mobile/src/ui/device-summary.tsx
023fd4fdb5819fd85be7dbd181a89d265cb24606b75ee21891b1136e66c210ac  apps/mobile/src/ui/manage.tsx
83dc55ed2473fc54f54d43a26a76dd31a6cbb0c019118a8b612166944bc49fa8  apps/mobile/tests/hr-read-admission.test.ts
b5ef6ea88a473d082e49cf89eb4afa8e50b1bed4d7fe572ebdabdf31062ee733  apps/mobile/tests/device-presentation.test.ts
217ae43bfcae4cb9826bafd8ad66bef8e97327c0638400c0e6263c5eb7d66a60  apps/mobile/tests/result-ui.test.ts
2c890041f348af9e54462fde8f77f806e8d8b7cf6b1c211bae73bad992c81eb9  apps/mobile/tests/support/result-rendering.tsx
483f069e5dcde3aced0162ccc54e92c2b99acc604c3462051605c558a6323934  apps/mobile/tests/support/device-presentation-fixtures.ts
6df427ba040c5193847772dc4a6d630b51153c5e23bdb6e5c3d473f6b5e295bc  apps/mobile/src/device/tests/physical.test.ts
a1d8cd2e19f072ac0d981602e7a96d29415b25b47cbfe98292f556d682612bd1  apps/mobile/e2e/components.spec.ts
ad64e9697e9f6575d76c442aa325a381e05d5428e8428d645ec090a7fbb79a6b  apps/mobile/e2e/fixtures/hr-result-component.tsx
10c3d77f398b1c571e1f43cc20df7341ffe0b2ce423b80dbc281ebbafdd48e48  apps/mobile/e2e/fixtures/device-presentation-component.tsx
dfafd09b27580553506f00a96bc8a7a71c806c625584939e2bc51dc69dab11a9  apps/mobile/e2e/fixtures/alcohol-component.tsx
```
