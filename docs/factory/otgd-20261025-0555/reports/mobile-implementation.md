# Mobile implementation — Tasks 1, 4 and client portion of Task 3

Author: OpenAI Factory mobile builder `/root/mobile_builder`; sole PM `/root`.
Date: 2026-10-25. Decisions D001v1, D002v1, D003v1, D004v1, D005v1 and D006v3 acknowledged AFFECTED before edits. Correction/recovery counters unchanged. No git, Docker, deployment, participant, firmware-provisioning or external publication action performed.

## Changes and regression evidence

### Task 1 — truthful separate alcohol reporting (ENG-004/007)

`manage.tsx::AlcoholScreen` replaces the unconditional `No classification exists` with `No automatic combined classification; research co-use requires model-specific authority`. Qualified breath capture remains unavailable; mg/L, unavailable blood conversion and unavailable driving clearance remain explicit. Measurement default, existing fictional demo behavior and scientific authority are unchanged.

`checks.tsx::ResultScreen` now reports the alcohol companion's own `Measured (UTC)` value, using `Not reported` when its generic JSON field is not a string. PM explicitly released this smallest additional file change after inspection found the missing acquisition timestamp. No new alcohol history/detail surface was invented: the actual history row opens the actual result, and its existing About action opens actual evidence/context.

New `alcohol-component.tsx` renders actual AlcoholScreen, HistoryScreen, ResultScreen and EvidenceScreen. Inputs clone `testfixtures/backend-research-result.json`; its admitted-result display is not created with an approval Boolean. No admission occurs in this fixture. Alcohol variants retain a complete companion, hypothetical reporting limits and fictional quality flags. They cover quantified zero, quantified 0.001 mg/L, below_loq, not_detected, invalid, and simulated source. Nonquantified magnitudes are null. Assertions verify exact value/dash, mg/L, qualifier/source, companion timestamp and separate-channel disclaimer. The existing named research endpoint retains 83.2% and above-threshold classification across all variants. Each actual rendered history/result/detail screen rejects positive safe-to-drive/legal-clearance/combined-score copy; AlcoholScreen explicitly permits truthful clearance-unavailable text.

Observed RED before source edits:

- `/tmp/mobile-red.log`: bounded truthful copy absent; old unconditional classification copy was rendered.
- `/tmp/mobile-red3.log`: `Separate alcohol measurement` card lacked literal `2026-10-11T07:08:09Z`; value/unit/source already rendered.

The subsequent focused desktop run passed all four new rendered cases (`/tmp/mobile-green2.log`). Final gate runs below cover both viewport projects.

### Task 4 — no-prompt Settings recovery and workspace races (ENG-008)

The existing PermissionsCard refresh sequence and unmount guards were retained. Settings now keys the card with a distinct `permissions:` prefix plus actual controller epoch and state generation; pending OS status from a replaced workspace cannot publish into its replacement. A captured actual controller epoch also guards promise completion before React commits navigation. Distinct prefix avoids collision with the existing sibling DiagnosticsCard key.

New `permissions-component.tsx`, `permission-adapters.ts` and `permissions-native-shim.ts` bind actual SettingsScreen to controlled native observations. They are isolated to a dedicated esbuild bundle; the shared native-web shim and production native modules were not edited. Only camera status/request, Bluetooth status, enrolled unlock status, AppState and Settings/unused clipboard/transport boundaries are replaced. The latter unused operations throw if called rather than pretend to acquire evidence.

Rendered assertions cover denied/canAskAgain, denied/cannotAskAgain, restricted, undetermined, and rejected status query. They verify the exact recovery labels on refresh and active return, zero request calls, zero automatic Settings opens, one explicit Settings open, and granted status after active return. Deferred reads verify newest-read wins, stale epoch/generation completion refusal, unmount listener removal and no late display. The additional actual exported-app test creates a real guest draft with a collected fictional saliva example, visits Settings/refresh, returns to the same draft, uses Back/Keep draft and returns again. Check identity, stage and already-collected state remain intact; browser camera requests remain zero.

Observed RED before corrections:

- `/tmp/mobile-red3.log`: after account replacement and old denied completion, `Not checked` was absent; the old card could publish.
- `/tmp/mobile-epoch-red.log`: after changing the actual controller epoch before React rerender and settling the old read, the prior `Granted` display was replaced. The test advances the controlled clock 50 ms to flush the queued React update; an immediate assertion had incorrectly observed the earlier state and was strengthened before changing production code.
- `/tmp/mobile-epoch-green.log`: the same pre-render epoch regression passed after the explicit epoch guard, 1/1 executed.

### Task 3 client — configuration expiry and absent instrument (ENG-006)

Only `tests/acquisition.test.ts` changed; `src/core/acquisition.ts` and controller/acquisition implementation required no correction.

- `hypothetical breath contract configuration is selectable only strictly before its expiry`: actual configurationsFor/configurationFor receive frozen owned-study context; 999 ms before the one-second boundary selects, exactly 1000 ms and 1001 ms refuse. No grant or instrument is invoked. This is a hypothetical configuration-selection contract, not an installed adapter.
- `fresh absent-breath-adapter capability overrides stale cached availability before any hardware invocation`: actual controller refreshes stale cached availability to the unavailable software observation and refuses CAPTURE_UNAVAILABLE; no grant, device nonce preparation, hardware acquisition, accepted alcohol or attempt is created.
- `a start-time registry dependency refusal after a hypothetical breath grant preserves its authoritative reason and never acquires concentration`: actual controller/API transport handling propagates exact current server code APPROVED_REGISTRY_VERSION_REQUIRED after the fictional grant. Hardware-call count stays zero; the attempted acquisition is invalid with null concentration. The initial test expected a null companion, but inspection showed the existing interrupted-attempt contract preserves an invalid companion; the assertion was corrected to require invalid/null rather than erase that record. This was a test expectation mismatch, not a production bug.

Calibration expiry is authoritative on the API. These client fixtures do not invent a client calibration field, pretend that generic APPROVED_REGISTRY_VERSION_REQUIRED diagnoses calibration, or replace a true missing-adapter reason. PM confirmed the separate API builder's direct actual PostgreSQL governance evidence; that execution is not claimed as this author's work. Source inspection still shows no alcohol entry in SOFTWARE_ADAPTERS/PHYSICAL_DRIVERS.

## Executed checks

All commands below ran from `apps/mobile`; no mandatory cases were skipped in these runs. Full platform/coverage/live/native gates remain PM-owned and are not implied by this bounded report.

| Command | Observed result | Raw local log |
| --- | --- | --- |
| `node --import tsx --test tests/acquisition.test.ts` | 24 tests passed, 0 failed/skipped | `/tmp/mobile-acquisition.log` |
| `npm test` (final run) | 267 tests passed, 0 failed/skipped | `/tmp/mobile-unit-final.log` |
| `npm run typecheck` (final run) | exit 0 | `/tmp/mobile-typecheck-final.log` |
| `CI=1 EXPO_NO_TELEMETRY=1 npm run export:web` (after final production edit) | exit 0, ordinary `dist` exported | `/tmp/mobile-export.log` |
| `CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm run test:e2e -- e2e/components.spec.ts e2e/raw-recordings.spec.ts` | 50 passed, both Pixel 7 and desktop projects, 0 failures/skips | `/tmp/mobile-components-final.log` |
| `npm exec -- prettier --check e2e/raw-recordings.spec.ts e2e/components.spec.ts e2e/fixtures/alcohol-component.tsx e2e/fixtures/permissions-component.tsx e2e/fixtures/permission-adapters.ts e2e/fixtures/permissions-native-shim.ts tests/acquisition.test.ts` | exit 0; all matched files formatted | `/tmp/mobile-format-final.log` |
| `CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm run test:e2e -- e2e/raw-recordings.spec.ts` after test-only formatting | 38 passed, both viewport projects, 0 failures/skips | `/tmp/mobile-raw-final.log` |

The combined 50-case run preceded a formatting-only rewrite of two new test assertions. The raw-recordings rerun binds those final test bytes; production/export source did not change. Expo cache rebuild, inherited NO_COLOR/FORCE_COLOR and npm update notices are nonfailing environment output. Early setup-only attempts exposed invalid esbuild relative aliases, an unused missing transport export, fixture fields and iOS clipboard import; these were corrected at isolated test boundaries before counting the behavioral RED/green evidence above. A new timestamp JSX type error was corrected with a string guard before successful final typecheck/export.

## Remaining boundaries

Android/iOS actual OS Settings round trips, permission dialogs and physical capture are unexecuted here. Controlled native observations are component evidence only; the ordinary web journey proves browser/controller draft behavior only. A qualified calibrated breath instrument/driver is absent, so real breath start/recalibration, sensing qualification, clinical validity, participant authorization and driving/legal clearance remain unavailable. No real participant/scientific approval or release readiness follows from these tests. Parent retains all commits/pushes, independent reviews/signoffs and final gate acceptance.

## Owned file SHA-256

```text
df28e91c2335b54179bed5f1ad3e606a240f19d471fc735234a577e3a448ce7c  apps/mobile/src/ui/manage.tsx
aa00421169fedb903393a7b778d2cd47281bf007d6ef24b2794e92fbbbc20b95  apps/mobile/src/ui/checks.tsx
725effb97f2e9195340fd6370b8491065eabdf849ce5c5680974c39cc2125c53  apps/mobile/e2e/components.spec.ts
2ada98a52caf63a835d979adc71bef5542795c5edbd72fc859cdb7975cbfd3b7  apps/mobile/e2e/raw-recordings.spec.ts
bd717897803a6155993eab073f59dddafb248d07b226f6d98ce9d0b6010d01a7  apps/mobile/e2e/fixtures/alcohol-component.tsx
f5eb1d04773d280fb7f57149141634a9253dfb98c7c017c36d7124503329921d  apps/mobile/e2e/fixtures/permission-adapters.ts
d7b52bf5c6e5b9f7d793e89de8b3ace55b2be7eb7cccf0a8710e6b5055aa58bd  apps/mobile/e2e/fixtures/permissions-component.tsx
8dfb8303c16c5e6b0c53500ee6a43e885f1a2d3a15812233b21ba7861098d43d  apps/mobile/e2e/fixtures/permissions-native-shim.ts
797e9858167b9b80bff401e0b66c3fda1f9ae56c8f007fbe5b10c4aeb0b159be  apps/mobile/tests/acquisition.test.ts
```
