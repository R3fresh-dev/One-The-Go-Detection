# Mobile implementation verification

This file records **source/host evidence**, with native and deployment checks kept separate. The reviewed requirement baseline is `47d8ecbfc871b5026f32d4f5f474908e9c0e1b14`; implementation follows the production-mobile-platform shared/platform contracts and all twenty feature specifications.

## Executed checks

| Check | Evidence / scope |
|---|---|
| TypeScript | `npm run typecheck` passed after account, cancellation, service-readiness and profile integration changes. |
| Host tests | Domain/schema/canonical fixtures; immutable context/attempts; native terminal and credential-write races; PKCE attempt expiry; locale/profile inputs; per-modality cardiac selection; measurement formatting; exact export; outbox/idempotency; actual backend config/capability decoding; diagnostics/history state; synthetic transport protocol; generation retirement (including deletion-only 410) and delayed owner/generation/clear scope guards. The latest aggregate run passed **94 of 94 tests** (0 skipped, 0 failed). |
| Expo configuration | `npm run config:check` was executed for the local build; cloud builds require real configured identities and HTTPS origins. |
| Web production bundle | `npm run export:web` executed; the export is a browser preview with memory-only storage and no native task fallback. |
| Cross-language check integration | Root backend tests uploaded/finalized/read both generated fictional application bundles, preserving exact companion bytes/digests and decoding the measurement-only result. The native bundle uses a labeled host-generated terminal fixture, not an acquired device run. |
| Native module linkage | The native module author verified local Expo autolinking/assets and scoped TypeScript. Native compile/runtime evidence belongs to the actual CI jobs and device checklist below. |

The standard Playwright browser download failed with truncated/corrupt ZIP files. An isolated temporary `@sparticuz/chromium` 153.0.0 runtime (Chromium 153.0.8010.0) then executed the browser suite. Its initial Fontconfig file referenced an empty font directory, producing blank glyphs and a renderer crash. With an explicit host-only Fontconfig file pointing at the package's OpenSans files and the system DejaVu fonts, **all four browser journeys passed**; the latest run took 7.6 seconds and covered mobile/desktop guest check, exact export, settings/privacy, profile validation, displayed BMI and reload isolation. Heading visibility and error assertions were retained. This is actual browser preview evidence; native execution remains separate.

## Feature traceability

All feature files are under `../../openspec/changes/production-mobile-platform/specs/`.

| Feature | Main implementation | Host/boundary evidence | Native or external evidence still required |
|---|---|---|---|
| Android onboarding / iOS parity — AND-ONB | `ui/account.tsx`, controller notice flow, API decoder | Exact UTF-8 notice digest; mandatory metadata; stable acknowledgment replay; no guest upload | First-install flow, screen-reader announcement and interrupted notice acceptance on both OSes |
| Sign-in — AND-AUTH | `services/auth.ts`, `core/operationGuards.ts`, `core/serializedVault.ts`, controller account transitions | Single-use/ten-minute guard; new-grant refresh isolation; serialized set/remove; same-account workspace guards | Hosted browser PKCE redirect/expiry/logout, OS unlock cancellation and native offline account transitions |
| Profile — AND-PRO | `ui/account.tsx`, `core/profileForm.ts`, domain/profile API | Locale digits/decimal separators; bounds/precision; feet+inches; exact SI/BMI; canonical rounding preservation; missingness and immutable snapshots | TalkBack/VoiceOver first-error focus, keyboards, Dynamic Type and concurrent edit screen flow |
| Dashboard — AND-HOME | `ui/account.tsx`, controller check creation | Optional context/default-off retry; guest/account fixture separation; frozen target time | Resume/replacement cards on representative phones/tablets |
| History — AND-HIST | `ui/manage.tsx`, `core/historyView.ts`, remote parser | Owner/epoch-scoped view memory; Pending sync semantics; immutable full-detail checks | Physical scroll restoration, screen reader selection and large history performance |
| Privacy controls — AND-PRIV | `ui/manage.tsx`, controller privacy flow, sync | Explicit intent and old-generation replay; quarantine; account transition guards; default-off retry | Fresh-auth final deletion confirmation, OS credentials, process death during deletion and real service recovery |
| Settings/accessibility — AND-SET | `ui/manage.tsx`, theme/components | Allowlisted bounded diagnostics; isolated history state; fixed task styling independent from theme | Native permission return, clipboard, VoiceOver/TalkBack, large text, contrast and device-scale screenshots |
| Saliva — AND-SAL | `ui/checks.tsx`, `ui/measurement-format.ts`, domain/device projection | Null censored values; qualifier/limits; matrix/correction/time/provenance display; simulated source | Qualified collection/assay/reader evidence remains unavailable; synthetic physical reader integration must be tested |
| Eye capture — AND-EYE | `ui/checks.tsx`, Expo Camera | No human pupil measurement; positioning preview and synthetic examples remain distinct | Camera allowed/denied/restricted/background behavior on both OSes; no image persistence verification |
| Pulse/PPG — AND-HR | `ui/checks.tsx`, device projection/domain | PPG source/modality isolation, absent ECG metrics, null invalid features | Physical simulated BLE acquisition and disconnect; qualified human PPG remains gated |
| ECG — AND-ECG | `ui/checks.tsx`, domain cardiac selection | One valid attempt per modality; explicit final selection; retain invalid alternatives without copying PPG features | Physical ECG safety/calibration/sampling qualification remains unavailable; synthetic transport on native devices |
| Reaction task — AND-TASK | `modules/reaction-task`, controller, `ui/checks.tsx` | Frozen golden configuration/schedules, full native-result fixture, terminal deduplication, no timer fallback | Actual Kotlin/Swift CI results; native end/background/focus/touch cancellation; physical onset/input latency calibration |
| Devices — AND-DEV | `src/device`, `modules/device-transport` | CRC/framing/MTU bounds/replay/clock vectors; explicit synthetic-only capability | Native discovery/denial/revocation/disconnect/forget/board round trip and RF behavior |
| Check workflow — AND-CHECK | controller, domain, `ui/checks.tsx` | Frozen context/target, durable starts, stopped pending starts, invalid retries and explicit local save | Process death and background at every acquisition/save boundary on real devices |
| Results — AND-RES | domain/remote validators, `ui/checks.tsx` | Reject all research estimates; target/input/evidence linkage; valid/missing component presentation | Native assistive-technology reading order and stale response scenarios |
| Synchronization — AND-SYNC | `services/api.ts`, `services/sync.ts`, controller | Stable phase keys; lost accepted reply replay; ETags; generation quarantine; readiness pause and privacy escape routes | Real network interruptions, TLS/issuer deployment, multi-device concurrent write and durable offline restart |
| Data export — AND-EXP | `services/export.ts`, `platform/sharing*`, `ui/manage.tsx` | Exact typed selection, profile scope, ZIP manifest/hash/size checks, tamper/traversal denial | Native share success/cancel/background/process death and temporary file cleanup; deployed authenticated download |
| Research access — AND-STUDY | `ui/manage.tsx`, controller consent/withdrawal | No automatic enrollment; exact document digest; local stop and durable withdrawal | Actual per-user invitation/consent/revocation/retention workflow against QA; no offline qualified capture |
| Alcohol — AND-ALC | `ui/manage.tsx`, domain alcohol DTO | Separate mg/L evidence and simulated parent restrictions; no BAC or impairment conversion | Qualified breath hardware/limits/calibration remain unavailable; native specimen timing workflow |
| Environments/release — AND-ENV | `app.config.ts`, platform config, API readiness, `eas.json` | Exact issuer/environment, HTTPS cloud configuration, app/contract minimum gates and X-App-Version | Actual signed builds, QA/prod deployment, store privacy/encryption declarations, runtime release evidence |

The requirement identifiers above name feature families; the exact clauses, scenarios and engineering details remain in their linked feature specifications. Host tests do not prove native UI, OS security or scientific validation.

## Storage and lifecycle checks to execute on devices

1. Verify SQLCipher is active in Android/iOS builds; no plaintext fallback is accepted. Verify random per-owner database keys in SecureStore and device-credential cancellation leaving the account locked.
2. Inspect iOS backup exclusion and Android `allowBackup=false` / secure-window behavior. Verify the application cover during backgrounding and the documented iOS screenshot limitation.
3. Reinstall, simulate key loss, sign out while retaining records, reauthenticate as another account, and confirm that only the original account can reopen its cache. Exercise pending SecureStore writes and rejected refresh tokens with process termination.
4. Cancel or leave during every pending start, active trial, final drain and terminal persistence step. Confirm no resumed task, one terminal record per run, and stopped native presentation before any modal/navigation.
5. Execute all device permission states without replacing denial with a synthetic success. Confirm passive camera preview never records an image.
6. Exercise privacy pending/running/failure/retained/expired states against the real backend, including replay after lost acknowledgment, stale generation rejection, signed-out access denial and deletion restoration barriers.

## Reproducible commands and artifacts

Use the commands in [README.md](README.md). Host fixtures are in `testfixtures/`, task golden vectors in the reviewed OpenSpec fixture directory, device tests in `src/device/tests/`, and native fixture suites in `modules/reaction-task/`. Browser screenshots/traces/reports are generated into ignored `artifacts/`, `test-results/` and `playwright-report/` directories. CI publishes its own build/test artifacts.

No local host result in this document asserts that a production APK/IPA has been signed, that an app has reached TestFlight/Play, that AWS environments have been deployed, or that a hardware/model scientific gate has closed.
