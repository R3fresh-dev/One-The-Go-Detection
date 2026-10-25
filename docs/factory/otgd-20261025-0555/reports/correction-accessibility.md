# Accessibility correction implementation evidence

Builder `/root/accessibility_builder`; run `otgd-20261025-0555`; formal consolidated correction **1/2**, PM recovery **0/3**. Pinned Factory `4770878e18e9c587c2961b9e2bb13315da31abe9`; original independent-review candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`. Current checkpoint HEAD observed `3d2c71a435b261f3291d92ac44f6c91ce416e3cc`. Decisions D001–D009 acknowledged before edits; D009 v2 acknowledged not affected, v3 acknowledged shared ownership. This is author implementation evidence, **not independent signoff or final frozen-candidate acceptance**.

## Changes

**UX-002:** `Title` forwards its native/DOM reference. `Page` schedules heading focus after interactions and a layout frame: web uses DOM focus with `preventScroll`; native resolves the mounted tag and uses `AccessibilityInfo.setAccessibilityFocus`. Effect cleanup cancels both deferred stages; current-route, privacy-cover, modal and active-task/eye guards reject stale or hidden destinations. A newer explicit browser focus takes precedence over a pending route handoff. Dialog focus waits for `Modal.onShow`; shared buttons/switches retain the actual initiating reference and route for guarded restoration after dismissal. Dismissed dialogs unmount immediately, preventing React Native Web's old fade-out focus trap from stealing destination focus or leaving an invisible pointer-blocking portal after a motion-setting change. Allowed entrance animation remains a fade. Existing Page scroll restoration callbacks are preserved; the web focus helper explicitly prevents scrolling. No accessibility-builder edits to production native task timing, geometry or stimulus configuration; `git diff --exit-code -- apps/mobile/modules/reaction-task/android/src/main apps/mobile/modules/reaction-task/ios apps/mobile/modules/reaction-task/src` exited 0 at verification.

**UI-001:** themes supply an explicit destructive foreground (`onDanger`): light white on `#A72F35`; dark `#3A1015` on `#FFB6BA`. The button text and busy indicator use it. Destructive pressed opacity is 0.9; prior 0.75 also failed the light-theme minimum after compositing. Browser tests inspect the actual computed foreground/background/surface/opacity, including a held pointer press, and composite the group opacity over its rendered dialog surface.

| Actual rendered state | Light | Dark |
|---|---:|---:|
| Normal | 6.7718:1 | 10.0029:1 |
| Pressed | 5.5849:1 | 8.4208:1 |

Identical values were observed at both browser viewports. Cancel remains enabled and tested; neither contrast test confirms deletion.

**UI-002:** new workspaces default to `reducedMotion: "system"`; the preference type permits explicit booleans. Existing stored true/false values remain explicit overrides, while missing/unrecognized legacy values follow the system without rewriting workspace data. `ThemeProvider` reads `isReduceMotionEnabled`, subscribes to `reduceMotionChanged`, ignores an obsolete initial result after a newer event, and removes the subscription on unmount. Until OS state is known/unavailable it conservatively reduces ordinary motion. The effective preference drives shared Confirmation `animationType` (`none` or `fade`). Settings shows the effective switch, explains system/override status, and provides Use system motion setting. The existing serialized controller setter handles all choices; **no controller edit was made**. Product owner released only the Settings section in `manage.tsx`; separate sync-conflict type/controller ownership was respected.

## Executed verification

Working directory for commands below: `apps/mobile`. Installed dependencies only; no install, Docker operation, retained-service mutation, commit, push, supervision change, deployment or participant operation by this builder. PM allocated and then received release of port8082; `ss -ltnp 'sport = :8082'` showed no listener after completion.

| Command | Observed result | Retained log |
|---|---|---|
| `node --import tsx --test tests/accessibility-ui.test.ts` before correction | 2 intended failures: dark contrast 1.6598:1 and false default instead of system | `unit-red.log` |
| `PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm exec -- playwright test e2e/components.spec.ts --grep 'route headings\|system motion\|rendered destructive'` before correction | 6 intended failures, all 3 regressions at both viewports | `browser-red.log` |
| `node --import tsx --test tests/accessibility-focus.test.ts` for rapid-user-focus regression | Intended failure: deferred route handoff focused once after newer user focus (expected zero) | `focus-race-red.log` |
| `node --import tsx --test tests/accessibility-*.test.ts` | **8 passed, 0 failed/skipped** | `unit-green.log` |
| `npm test` after final modal correction | **339 passed, 0 failed/skipped**, exit0 | `full-unit-final-stable.log` |
| `npm run typecheck` | exit0 | `typecheck-final.log` |
| `EXPO_NO_TELEMETRY=1 EXPO_OFFLINE=1 __UNSAFE_EXPO_HOME_DIRECTORY=/tmp/otgd-expo npm run export:web` | exit0 | `export-final.log` |
| `PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm exec -- playwright test e2e/components.spec.ts` | **18 passed**, both configured viewports, 29.6s, exit0 | `browser-final-stable.log` |
| Installed Prettier `--check` on App, owned UI/accessibility modules, direct tests and components.spec | all matched files pass, exit0 | `format-check-final.log` |
| `git diff --check` on owned tracked paths | exit0 | terminal evidence |

Browser scenarios cover Home/Settings/Privacy/deeper Back/History heading focus, dialog heading focus and initiating-trigger restoration, selected keyboard tab state, system reduced motion, explicit off/on and reset-to-system, live media changes, actual dialog CSS animation, contrast, existing notice/context acknowledgments, profile first-error focus, unsaved cancellation, exact history selection, unsynced-data cancellation, and retained draft/example on navigation without a camera request. Unit tests cover real scheduling logic with controlled native API boundaries, cancellation before/after deferred scheduling, stale-route guards, detached web nodes, explicit user focus, and actual workspace reopen preserving motion choices and other settings.

Intermediate browser failures are retained, not discarded: `browser-refinement.log` includes corrected test-selector mistakes (actual History title and named inner dialog), plus the real pressed contrast failure; `browser-green.log` recorded 15/18 with rapid keyboard-focus and stale-modal-overlay failures; `browser-final.log` recorded 16/18 with two remaining mobile entrance/dismissal timing failures. The final complete run above follows the corrected modal lifecycle. Initial export attempts also retained the unwritable default Expo cache error and then a temporary concurrent OAuth config-loader import error; the read/write cache override and OAuth-owner repair allowed the final successful export. These development runs were not immutable candidate gates.

Raw logs, initial/intermediate failure traces/screenshots, final embedded Playwright HTML report and computed contrast attachment extracts are preserved at `reports/correction-accessibility-round1/` (ignored evidence), with a second copy at `/tmp/otgd-accessibility-evidence/`. `computed-destructive-contrast.json` contains both viewport observations. Key SHA-256 bindings:

```text
109c775bdf97063192404ba5f11c41b5607b32c62b1498c4b33ad2a34a0dce95  unit-red.log
9a3e056946dc25eb9b89e75809ec155fca4aa4ea78236032f6abc66fdfc1b210  browser-red.log
becb4af871e3f433726d671170ba660c4877bbd975bc016b2dc25804755db9f8  focus-race-red.log
4cafc06cf6bdbf3fe64f090926e3a822a7007732dff9beee9ad34ef388436402  browser-final-stable.log
71383f1b6576d974d9a906e6c9ea90b1d297059b2d389c164c738f86380e86f1  full-unit-final-stable.log
c304e11cf9df205491c51502be84cfce866c109938819c0fe8d67d590c5ff52f  computed-destructive-contrast.json
67bd13483f07d9a686858fd954f20225cfe900b5cea6eee8cc20dcbbc2f5f538  owned-SHA256SUMS
```

Owned source/test snapshot hashes recorded before handoff (final PM freeze must bind the combined source). Rechecking after report creation matched10/11: only shared `core/types.ts` had subsequently changed under the separately authorized D009v3 sync-conflict ownership; the preference union remains intact. This known shared-file mismatch is not waived or claimed as frozen-candidate evidence:

```text
62355551f8ab206fd0eb9efc2bec18f27256444b03a7119c660d8663d039207d  apps/mobile/App.tsx
25398bbe930bf27079a4e26b157860702b86fbc0a74f23c41869218e953068e8  apps/mobile/src/ui/accessibility.tsx
adc89118200592946e0f95cf2db81caadcbd627569a63f940f2b512ffb3a2071  apps/mobile/src/ui/components.tsx
48d5e8b34b44415d1bcad3f31380547a0bf315b976a4ead81df81f662610410d  apps/mobile/src/ui/theme.tsx
594490c9a3fff945c744d11ee555100cde61552a5a353018e3d9654320855419  apps/mobile/src/ui/manage.tsx
3d931b5266af1fd2eb1206b0506738fb5a8c287ce7129594402d5a9f4e3844c1  apps/mobile/src/core/types.ts
ec3caeeefbf7fa22c2d137476b170311cbcb568c31ebbf135ecc66022d4fc108  apps/mobile/src/core/domain.ts
f9c68684978ffbbd41e83b4b7d1f41bba2ab58a7716bcad0af1ec5741ea82a9d  apps/mobile/tests/accessibility-focus.test.ts
f2376be005cddb016adc334162863d858e08024f1eea7ce1f3c73d8fcd96074b  apps/mobile/tests/accessibility-preferences.test.ts
4340dd4e61e22e687e0486684a995231f6a51536eb6e7e53567c33a1e05a602d  apps/mobile/tests/accessibility-ui.test.ts
03fa1c915540a1dd8e1d721128a6cb663d0d3f1acca397d518059315e8bf4776  apps/mobile/e2e/components.spec.ts
```

## Remaining verification and authority gaps

The assigned source corrections have passing direct/browser evidence. TalkBack/VoiceOver, native modal dismissal/auth cancellation, Android/iOS OS focus, large system text, real native storage/unlock and device lifecycle/hardware were **not executed here**: no installed native OS target was supplied to this builder. Native-boundary unit calls establish software API use only. The web focus helper and unchanged scroll callbacks do not prove actual native screen-reader behavior or every native Back/scroll recovery path.

The project-wide unchanged-source local gate, coverage strictly greater than80%, all14 exact-tree CI jobs, 782-case reconciliation, affected independent rereviews and final approver remain PM/council prerequisites; this report does not clear them. Other authorized owners were editing shared source during these development checks, so the final combined candidate requires its own freeze and full gates. Scientific/clinical qualification, physical sensing, participant authorization, original/cloud image provenance and release claims remain separate unresolved requirements. No action was denied or left with an uncertain external outcome by this builder; remaining items are unexecuted verification prerequisites, not an approval bypass.
