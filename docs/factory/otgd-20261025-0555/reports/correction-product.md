# Correction round 1 — mobile presentation, sync and preparation

Latest author handoff: **370/370 mobile unit, 68/68 component/raw browser, final-format raw rerun 42/42**, current typecheck/format/ordinary export passed. All runs have zero skipped cases. These are author preflights before PM's final candidate freeze, required aggregate/CI gates and independent reviews; no app-complete or native/scientific qualification is issued. The final supplement and its hashes below supersede earlier source snapshots.

Author `/root/mobile_builder`, OpenAI Factory builder; sole PM `/root`. D009v1 acknowledged AFFECTED before edits. Reviewed candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; correction **1/2**, recovery **0/3**, counters unchanged by this worker. Scope: PROD-001/UX-001, PROD-002, PROD-003 only. No git, Docker, service/data, deployment, participant or paid-service action performed. No independent signoff is issued.

## Source corrections

- `src/core/resultPresentation.ts` is a new pure presentation helper. `presentCheckResult` calls the existing `verifyResult` before exposing any retained result/uncertainty. Measurement-only, invalid and inconclusive legacy results have distinct summaries; verified 1.1 estimates and abstentions explicitly say **historical research**. Missing, legacy-shaped research, simulated research or changed proof becomes Result unavailable with no score/policy. Delivery stays independent. Historical evidence never grants current access; the authenticated service remains responsible for independent admission.
- `ui/account.tsx` uses that helper in the shared CheckRow consumed by Home and History. The original acquisition date, fictional provenance and synchronization badge remain independent. Home now derives its online research-access detail from active authenticated identity and capabilities with matching account and all generations, plus both `model_execution_supported` and `inference_available`. Guest/preview, offline, missing capability, revoked/inactive account and mismatches cannot advertise research access. No local role, preference, sign-in or historical result grants it. The helper recomputes from supplied observations rather than retaining a previous scope label.
- Welcome states **Measurement mode is the default** and explains separately authenticated research, independent study/model approval and that introduction/sign-in do not enroll the person or grant research authority. The common explanation remains visible in the introduction; guest examples, no validated impairment model and no driving-clearance boundaries remain.
- `ui/checks.tsx::ResultScreen` consumes the same verified presentation. It shows the supplied policy ID, uncertainty method, original rationale and probability-band limits for a verified 1.1 result. Method none explicitly says no interval is supplied and that the policy does not quantify uncertainty. Supplied probability bands explain inclusive abstention and explicitly distinguish them from confidence intervals/clinical safety ranges. Rounded percentages are accompanied by the original exact probability limits, avoiding loss of narrow boundaries. Abstained results retain null probability/classification and show their policy. Malformed/mismatched policy/proof withholds the score and policy. No model output, confidence interval, clinical meaning or new authority is manufactured.
- `e2e/raw-recordings.spec.ts` has only the PM-authorized bounded navigation selector change: the existing alcohol test now clicks **Historical research result** instead of the old false **Measurements only** label. All original alcohol/raw/navigation assertions remain.

The PM explicitly confirmed the contract distinction: current capability governs new research access, while verified retained records may retain historical scope after current access is revoked. The existing capability lifecycle was inspected: sign-in receives authenticated capabilities before exposing the account workspace; refreshes are scoped and owner-checked. No API/schema/controller/auth boundary changed.

## Regression tests and actual evidence

`tests/result-presentation.test.ts` contains eight direct helper/verifier cases. They cover measurement-only, invalid, inconclusive, verified research estimate/abstention, absent/legacy/simulated/changed proof, live capability identity/generation checks and revocation, method none, supplied below/above/null band cases, inside-band numeric refusal, missing/malformed/mismatched uncertainty, and exact high-precision limits.

`tests/result-ui.test.ts` bundles `tests/support/result-rendering.tsx` against actual production Home, CheckRow, History, Welcome and ResultScreen using the existing web binding. Five tests assert actual server-rendered JSX text, not substitute result components. Controller/device inputs are controlled; no production test injection was added. These tests cover faithful measured/invalid/inconclusive/pending/fictional/unsupported states, actual historical result/detail labels, Home scope on revocation/offline/account change, default/conditional onboarding and rendered uncertainty none/band/abstention/refused corrupt policy. They are static component evidence, not browser interaction, native OS or scientific admission.

Observed RED evidence before UI corrections: `/tmp/correction-product-ui-red.log` executed four tests, all failed on the actual old output: frozen research rows said Measurements only, Home said Measurement-only release, Welcome omitted the default/separate-access explanation, and result details lacked the verified policy. The first SSR harness attempt lacked the bundler's `__DEV__` definition; that setup error was fixed before counting these semantic failures.

The initial helper tests separately failed 7/7 with an explicit missing-presentation assertion (`/tmp/correction-product-red.log`). After implementing the helper, they passed 7/7 (`/tmp/correction-product-helper-green.log`). The later precision regression failed because the display only contained `40.0%–60.0%` rather than preserving `0.40001–0.60001`; `/tmp/correction-product-precision-red.log` records that exact expected/actual difference. The helper now appends the original probability limits. A test-only assumption that null rationale could be accepted was rejected by the existing stricter schema; that assumption was removed without loosening the verifier/schema.

Final focused run: **13/13 passed, zero skipped**, `/tmp/correction-product-focused.log`, command from `apps/mobile`:

```sh
node --import tsx --test tests/result-presentation.test.ts tests/result-ui.test.ts
```

Other observed checks from `apps/mobile`:

| Command | Observed result | Local log |
| --- | --- | --- |
| `npm run typecheck` | exit 0 after the accessibility owner's in-progress type correction | `/tmp/correction-product-typecheck.log` |
| `npm exec -- prettier --check src/core/resultPresentation.ts src/ui/account.tsx src/ui/checks.tsx tests/result-presentation.test.ts tests/result-ui.test.ts tests/support/result-rendering.tsx e2e/raw-recordings.spec.ts` | exit 0, all matched files formatted | `/tmp/correction-product-format-check.log` |
| `npm test` before precision addition and the accessibility owner's new focus test | 336 passed, zero failed/skipped | `/tmp/correction-product-unit.log` |
| `npm test` after the final product change, overlapping the accessibility owner's new RED | 338 executed: 337 passed, 1 failed, zero skipped; failure `deferred destination focus preserves a newer explicit user focus`, `tests/accessibility-focus.test.ts:140`, actual 1 / expected 0 | `/tmp/correction-product-unit-final.log` |
| `npm test` after the accessibility owner's guard correction | 338 passed, zero failed/skipped, exit 0 | `/tmp/correction-product-unit-stable.log` |

The retained full-suite failure was reported immediately to the accessibility owner and PM; that owner corrected it, and this worker's fresh full-suite rerun then passed 338/338. This is the product/source snapshot above, before the PM's subsequent D009v3 sync extension. No passing full suite is inferred for later source edits.

## Coordination and remaining boundaries

Accessibility builder owns `e2e/components.spec.ts`, shared UI/accessibility/motion and its browser slot. Product scenario labels, policy expectations and the actual JSX fixture/test paths were sent directly to that owner. No concurrent browser or export was started by this worker. Current-candidate ordinary export, full browser/component/raw gates, coverage and all platform/CI gates remain PM-owned after freeze. No earlier export/browser pass is reused for the corrected source.

Native supported-OS UI/assistive technology, actual OS Settings and physical sensing remain unexecuted here. Historical proof consistency does not authenticate genuine scientific/study authority. Measurement default and separate future calibrated fuel-cell breath mg/L/no-clearance scope remain unchanged. All scientific/hardware/participant/release prerequisites and independent reviews/signoffs remain separate.

## Owned source SHA-256

```text
f3ea68786a66ee96bc235ccd1375444dacbd285d74f23d87cc22f951f01575b8  apps/mobile/src/core/resultPresentation.ts
ab70f633e0a23ac8b185c2f547a686ac4081a27f194f9af64ec2765670c37f45  apps/mobile/src/ui/account.tsx
7bcc4d4125485968a8ddbc6b5183e51647177eb4401886da65235430087aed75  apps/mobile/src/ui/checks.tsx
2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120  apps/mobile/tests/result-presentation.test.ts
33b8cd778c791460e42f1e163062336d31217af7236d66bc5f9f24a45c38a681  apps/mobile/tests/result-ui.test.ts
7e66eb5adc2b8b67604ec5b7999f0d7fef30146466242d211dc4076bddbf076c  apps/mobile/tests/support/result-rendering.tsx
7ad974bbf3ba46dcd980dd217e4a35a3d836c71e3720a585989ad8c441d686ab  apps/mobile/e2e/raw-recordings.spec.ts
```

## D009v3 sync extension and profile acceptance supplement

PM subsequently released the corroborated AND-SYNC-005/006 defect within the same correction round. D009v3 acknowledged AFFECTED; D009v4 acknowledged for privacy ownership coordination only. This builder owns no PrivacyJob, JobCard, API/auth or privacy-receipt changes. The accessibility owner retained the historical raw-test selector and owns later raw/privacy edits. The file hashes above are the original product-only snapshot; the following bindings supersede affected files after the authorized sync extension.

### Implemented behavior

`services/sync.ts` now performs one bounded, authenticated GET of the same owned session after a snapshot PUT receives 412 or 409. It preserves the authoritative response/ETag in the distinct optional `CheckRecord.sync_conflict` observation, together with owner, generation, observation time and readback failure state. It never replaces the pending local snapshot, context, manifest, attempts, local remote ETag, queue body or request keys. Known frozen responses pass the existing full remote/evidence verifier; draft responses cannot be treated as frozen. Session ID/mode/revision/ETag, owner and digest checks remain enforced. The existing canonical session-detail response bound of 67,108,864 bytes and ApiClient timeout apply; neither is widened. A failed or rejected readback remains a stopped conflict with unavailable comparison, not a fabricated copy of local state.

Late readback cannot publish after epoch, workspace generation, capability generation, owner, account state or queue cancellation/fencing changes. A 410 discovered during readback quarantines retired data. `inspectConflict` is an explicit read-only refresh; normal/manual upload replay remains closed for conflicts. Both `uploadCheck` and the older `prepareReplacement` path now enforce review/frozen-server correction semantics. The Stop action preserves an already stopped conflict's original intent/keys instead of deleting its fence and allowing another upload identity.

`controller.ts::prepareUploadCorrection` rechecks the actual owned comparison and current account/generation; a draft server check cannot acquire frozen status from the stored Boolean. A valid frozen correction stages the existing linked-new-check flow: new UUID, new target time, supersedes reference, current newly confirmed context and no copied acquisitions. The original pending record remains immutable. The actual controller regression also reopens the same account workspace and confirms preservation of comparison and original keys; this is browser-memory/software behavior, not native SQLCipher/process-death proof.

`checks.tsx` presents stopped conflict/validation and waiting states. A conflict exposes verified server revision/hash beside the pending local hash, explicit snapshot comparison, guarded read-only refresh and a deliberate new-linked-correction action. The snapshot values appear only after explicit comparison action; this never dumps an error response or substitutes a remote result for the local record. Current-owner/generation verification gates the comparison again on display. Direct upload buttons are suppressed for terminal conflict/blocked intents. The older replacement button is also safe because its controller path now uses the same conflict guard.

Valid HTTP 429 Retry-After delays through one hour schedule the waiting state (minimum one second) and also fence explicit retry until the server deadline. A larger valid delay retains that same waiting intent and full deadline, stops automatic retry and permits only manual retry after the deadline. Request keys/body remain unchanged. Unrepresentable deadlines remain stopped for inspection. The UI distinguishes the one-hour automatic bound from the full server-requested wait. Existing automatic retry limits remain unchanged. The final 3601-second boundary correction is recorded in the supplement below.

HTTP 422 retains at most 32 bounded field locations and recognized stable validation type codes. Paths reject malformed/reserved segments; arbitrary messages, nested input/context objects, token-like values and unknown codes do not become display text. Unknown codes become `invalid`. This follows the real API validation-handler contract, which emits locations/type codes rather than Pydantic input/context values. The actual saved-check renderer shows inspectable location/code pairs and keeps the immutable upload terminal; no arbitrary response payload or measurement input is placed in field-error output.

### RED/green evidence

- `/tmp/correction-sync-red.log`: all five initial direct regressions failed before implementation. Expected authoritative GET was absent; stale-read cases could not enter readback; comparison state was absent; explicit 429 retry bypassed the deadline; 422 field errors were missing.
- `/tmp/correction-sync-inspect-red.log`: bounded/redacted fields and the explicit read-only conflict-refresh entry were missing. `/tmp/correction-sync-code-red.log` then proved that a regex-shaped token-like value could still be retained as a code; the final implementation uses a known-code allowlist and a safe fallback.
- `/tmp/correction-sync-account-red.log`: changing account state/capability generation during readback still allowed publication before those captured fences were added.
- `/tmp/correction-sync-controller-red.log`: repeated direct upload did not reject the already stopped conflict. `/tmp/correction-sync-replacement-red.log`: the older replacement path could bypass draft/frozen-server review. `/tmp/correction-sync-cancel-red.log`: Stop removed the terminal conflict intent and its keys. Each corresponding controller regression now passes.
- `/tmp/correction-sync-ui-red.log`: actual saved-check JSX had no inspectable terminal validation presentation before the new card. Actual JSX assertions now cover safe field/code output, no token/value echo, verified server-comparison/correction affordances and refusal of foreign comparison.

The engine tests use the actual ApiClient/Response error parsing and controller/domain implementation with controlled fictional HTTP transport, never a live-backend claim. The server comparison component test uses the existing complete `backend-cardiac-authority.json` owned-session fixture and full remote parsing. The smaller data-only research-engine fixture does not satisfy full attempt projection validation and was not used to bypass that verifier.

### Ordinary measurement profile acceptance

Two new `controller.test.ts` cases preserve the earlier engineering-fixture test and add the previously uncovered real measurement-mode software path. They save fictional self-reported P1 (80 kg, sleep 7 h), begin account measurement A, save P2 (82 kg, sleep 6.5 h), and assert A's P1 source/version, context hashes and target remain unchanged while it has no captures. One case additionally applies only the existing software attempt-ledger start/interruption transition and verifies the P1 context still holds; no sensor, grant, valid acquisition or participant qualification is supplied. After local save, linked check B has a new UUID/target, P2 version/context, no carried attempts and uncollected eye status. A remains P1. No check upload, finalization or capture-authorization request occurs. Both cases passed against existing production behavior; **no profile production bug or change** was needed.

### Executed commands at the sync/profile handoff

All commands ran from `apps/mobile`, before PM's replacement-candidate freeze. No mandatory case was skipped in these executions. They do not substitute for the final exact-candidate aggregate, coverage/CI gates or native acceptance.

| Command | Observed result | Raw local log |
| --- | --- | --- |
| `node --import tsx --test tests/result-presentation.test.ts tests/result-ui.test.ts tests/sync-conflict.test.ts tests/sync.test.ts tests/controller.test.ts` | 55 passed, zero failed/skipped | `/tmp/correction-mobile-focused-final.log` |
| `npm test` | 360 passed, zero failed/skipped; exit 0 | `/tmp/correction-mobile-unit-final.log` |
| `npm run typecheck` | exit 0 | `/tmp/correction-mobile-typecheck-final.log` |
| `npm exec -- prettier --check src/core/resultPresentation.ts src/controller.ts src/ui/account.tsx src/ui/checks.tsx src/services/sync.ts tests/result-presentation.test.ts tests/result-ui.test.ts tests/controller.test.ts tests/sync-conflict.test.ts tests/support/result-rendering.tsx` | exit 0; all matched files formatted | `/tmp/correction-mobile-format-final.log` |

An intermediate test-only TypeScript narrowing error after asserting an empty attempts array was corrected by reading the later attempt through the fresh snapshot; no production behavior changed. Final typecheck and full unit run above were executed after that correction. The shared `core/types.ts` hash below includes the separately owned privacy receipt type; this worker changed only CheckRecord/SyncConflict and QueueOperation fields there. No current correction browser/export/live-stack/native execution was performed by this worker, and no self-signoff is issued.

```text
f3ea68786a66ee96bc235ccd1375444dacbd285d74f23d87cc22f951f01575b8  apps/mobile/src/core/resultPresentation.ts
ab70f633e0a23ac8b185c2f547a686ac4081a27f194f9af64ec2765670c37f45  apps/mobile/src/ui/account.tsx
05c2741abfa93c9fdc50e7590a1bd920e579c62e2ec082dd2dc40c8950c77fb3  apps/mobile/src/ui/checks.tsx
46fc713e4a6ee147db17218f90475a4eb4e3af7bb0e0907dd52c23e5da514f74  apps/mobile/src/services/sync.ts
c4c8a611b15e6c3737dcd56005a77d8ff5fac952756066d342c21812696b76a9  apps/mobile/src/controller.ts
22b36cd917e6d961cae3bea3487ba281baf2d0d4cd0d7ec38500aca140c1608a  apps/mobile/src/core/types.ts
2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120  apps/mobile/tests/result-presentation.test.ts
21ce5bf103eed9417787db92e031794c5ac90c63d15d4fc2c09e6f0fc7b67274  apps/mobile/tests/result-ui.test.ts
eb6b0ef72ea88ff512513ee0eab57c360068bb0aece05aaabb3ffc6c4c09aee2  apps/mobile/tests/sync-conflict.test.ts
2732b7974198bc87f6643d3e27c3d89d88780cf769e5a3e6c928dbe4b866789a  apps/mobile/tests/controller.test.ts
839b0a0c0799c7abd7e2c12fa4a876b14a6aef0bbe6256125c478238eb4ae33b  apps/mobile/tests/support/result-rendering.tsx
```

## D009v5/v6 preparation integrity and final acceptance supplement

D009v5 and D009v6 acknowledged AFFECTED before dependent work. D006v7 acknowledged NOT_AFFECTED to this source scope, with its archive/data preservation and PM-only adoption hold respected; no Docker action occurred. Correction remains1/2, recovery0/3. The PM's interim checkpoint9 was respected as a repository write hold; work resumed only after release. No final freeze is implied by that checkpoint.

### Preparation chronology

`core/preparationClock.ts` now samples both monotonic and wall time. The PM explicitly accepted **PREPARATION_CLOCK_TOLERANCE_MS =100 ms inclusive**, independently documented as a sequential-sampling/quantization engineering consistency allowance, not scientific clock accuracy, a rest-duration change or acknowledgment-age allowance. It checks both elapsed time since Start and the delta since the previous observation; disagreement greater than100ms resets. Actual wall or monotonic regression and nonfinite observations also reset. Only monotonic elapsed time counts toward the approved rest; a wall jump never reduces it. Reset cannot regain authority without a fresh Start. Approved0–3600-second protocol bounds remain unchanged.

`ui/participant-capture.tsx` clears rest authority, all declarations and optional recording choice on timing failure, reports the required fresh guidance and invokes the existing scoped stop boundary. The actual Start handler checks timing again: a clock jump after rest completion but before the next200ms timer tick cannot leave an enabled prepared state or submit a capture. A bad wall clock after service preparation stops that admitted attempt rather than stranding it. The preparation callback retains its operation-epoch guard for both late success and failure. New successful guidance clears the old timing notice. Existing attempt/workspace/configuration/background and unavailable-human-ECG boundaries remain.

`tests/preparation-clock.test.ts` adds six cases: inclusive±100ms disagreement; ±101ms refusal; accumulated/opposing delta changes; zero and3600-second rest; unavailable clocks/monotonic regression/interruption; and actual1ms wall regression even within the disagreement tolerance. Existing participant clock tests now inject a matching wall observation for valid monotonic steps, preserving their original interruption/regression assertions. The old expectation that changing global wall time is ignored was intentionally removed.

Actual component tests in `e2e/components.spec.ts` use the existing real ParticipantPreparation fixture with a complete controlled bench-instruction configuration in `e2e/fixtures/preparation-configuration.ts`. They cover forward/backward two-hour wall changes, fresh service guidance and unchecked declarations before another capture; a paused-timer clock jump at explicit Start; zero/max rest with every declaration still required; and an unavailable wall clock after service preparation. These controls supply no real OS, instrument, physical rest, electrical safety or participant authority. `raw-recordings.spec.ts` retains its positive rest case without the contradictory two-hour jump, pairs injected monotonic/wall observations in its monotonic-regression case, and preserves every privacy/raw assertion.

RED evidence: `/tmp/correction-clock-red.log` failed4/5 before wall consistency implementation; `/tmp/correction-clock-regression-red.log` showed29 seconds instead of a full30-second reset after actual wall regression. Actual rendered REDs are retained at `/tmp/correction-clock-component-red.log`, `/tmp/correction-clock-click-red.log` (Start remained enabled with timers paused) and `/tmp/correction-clock-unavailable-red.log` (only prepare, no stop). The corrected focused desktop component run passed4/4, `/tmp/correction-clock-component-green.log`, before the complete two-viewport gate below.

### Long Retry-After alignment

Final inspection of the canonical AND-SYNC-006 paragraph found the initial author branch for waits over one hour was too terminal. The PM agreed to correct it within the existing round/scope. `/tmp/correction-sync-long-wait-red.log` records expected `retry_wait`, actual `blocked`. Final behavior retains the full valid server deadline and the same queue keys/body, disables automatic replay for the long wait and permits explicit replay only at/after that deadline. A3601-second case checks just before the boundary, automatic refusal at the boundary and one manual same-intent attempt at the boundary. All9 sync-conflict cases passed in `/tmp/correction-sync-long-wait-green.log`. Unrepresentable deadlines remain closed; no server delay is shortened.

### Exact late collection callbacks

Read-only inventory confirmed that prior binding/history/epoch tests did not directly cover SALCOL-007-02. Two cases in `tests/acquisition.test.ts` now hold the actual ApiClient's collection HTTP response after fictional service acceptance, then either withdraw the study or sign out/switch to a new account with a new ordinary measurement draft. Releasing the old successful response is rejected by existing cancellation/scope logic. The complete fenced state and selected replacement remain unchanged, immutable original intent is preserved under withdrawal, no original record enters the new account, and hardware-call count stays zero. The26-case acquisition module passed; **no production late-collection bug or change** was needed. This is controlled transport/software evidence, not live laboratory custody or native persistence.

### Final observed checks

Commands ran from `apps/mobile`. The complete component/raw run preceded a formatting-only condensation of the owned rest assertion; the42-case raw rerun binds the final test bytes. Production code/export did not change after the final export. All mandatory final-candidate categories, CI jobs, coverage and independent confirmations still belong to PM's later unchanged-source run.

| Command | Observed result | Raw local log |
| --- | --- | --- |
| `node --import tsx --test tests/preparation-clock.test.ts tests/participant-acquisition.test.ts` | 13 passed,0 failed/skipped | `/tmp/correction-clock-focused.log` |
| `node --import tsx --test tests/acquisition.test.ts` | 26 passed,0 failed/skipped | `/tmp/correction-late-collection.log` |
| `npm test` after the last test edits and released auth acceptance tests | 370 passed,0 failed/skipped, exit0 | `/tmp/correction-mobile-handoff-unit.log` |
| `npm run typecheck` | exit0 | `/tmp/correction-mobile-handoff-typecheck.log` |
| `npm run format:check` | exit0, all matched files formatted | `/tmp/correction-mobile-handoff-format-final.log` |
| `CI=1 EXPO_NO_TELEMETRY=1 npm run export:web` after last production edit | exit0, ordinary `dist` exported | `/tmp/correction-clock-export-final.log` |
| `CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm run test:e2e -- e2e/components.spec.ts e2e/raw-recordings.spec.ts` | 68 passed at Pixel7 and desktop,0 failed/skipped | `/tmp/correction-clock-components-final.log` |
| Same browser command selecting only `e2e/raw-recordings.spec.ts` after the formatting-only assertion change | 42 passed,0 failed/skipped | `/tmp/correction-clock-raw-final.log` |

One global formatter check reported only the new shorter timing-notice assertion's line layout. A read-only formatter diff confirmed that single owned rest-block difference; it was corrected without touching privacy/raw behavior, then both global format and the raw suite passed. All earlier RED and intermediate author results remain distinct from this handoff evidence. No merge, deployment, participant action, new paid service, supervision or recovery operation occurred. Native OS/assistive technology, hardware, independent scientific/study authority and final release prerequisites remain unexecuted/separate as previously recorded.

### Current source bindings at final author release

These are current file hashes, including coordinated shared-file contributions where identified earlier. They supersede older hashes in this report. No independent signoff is asserted.

```text
f3ea68786a66ee96bc235ccd1375444dacbd285d74f23d87cc22f951f01575b8  apps/mobile/src/core/resultPresentation.ts
ab70f633e0a23ac8b185c2f547a686ac4081a27f194f9af64ec2765670c37f45  apps/mobile/src/ui/account.tsx
28b26a694cc0598575be9226c91cf89f9763a1b346537ab78427486ac9a6546f  apps/mobile/src/ui/checks.tsx
5062dd28e9db43709b010b8da65fcbafbda563fdd40c33bfe1b32c10a499e3a4  apps/mobile/src/services/sync.ts
c4c8a611b15e6c3737dcd56005a77d8ff5fac952756066d342c21812696b76a9  apps/mobile/src/controller.ts
67c30cbea6ea4568d6b9f1b1e7aa9be93542321cc707e4d917b2419443e0512d  apps/mobile/src/core/types.ts
2e40afa442c1e7ba2f736ba324542361e7897485901d569d9b7a69326ea93120  apps/mobile/tests/result-presentation.test.ts
21ce5bf103eed9417787db92e031794c5ac90c63d15d4fc2c09e6f0fc7b67274  apps/mobile/tests/result-ui.test.ts
d07ac22260034e8b944704a194419121035b2ac3c56992f4b3e6fe80fd7d997f  apps/mobile/tests/sync-conflict.test.ts
2732b7974198bc87f6643d3e27c3d89d88780cf769e5a3e6c928dbe4b866789a  apps/mobile/tests/controller.test.ts
839b0a0c0799c7abd7e2c12fa4a876b14a6aef0bbe6256125c478238eb4ae33b  apps/mobile/tests/support/result-rendering.tsx
853b394a82f3ce04d7d66ede53bd6c0c42280560bc44bff115b3cde57cd7aad2  apps/mobile/src/core/preparationClock.ts
85a70b5260e2add61c68c6360cb08314564776517661d1446dc2263532c260f4  apps/mobile/src/ui/participant-capture.tsx
26e1ae978c239b5ac48bb5b7ceac75114d96e7642fbcffd57623e49c3dc652dc  apps/mobile/tests/preparation-clock.test.ts
6602c720f2be3570ccfc936f85950b0b1dc96b55906d1a74b07243e4070799a6  apps/mobile/tests/participant-acquisition.test.ts
fdf31a7b39efaff9c94d68e4d3ae61aa5caff87e54a0020da594119f0c1dad28  apps/mobile/tests/acquisition.test.ts
8749028fd40a278f2bc23a79bf7412678565b6b16a1db557b53b8f3c4853b4d5  apps/mobile/e2e/components.spec.ts
889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd  apps/mobile/e2e/raw-recordings.spec.ts
da1964a0db9272b0350de91e12d56de8df6779ba77138f6f5aefccf5f0a2684c  apps/mobile/e2e/fixtures/preparation-configuration.ts
```


## D009v11 HR cached numeric disclosure correction — author preflight, not independent approval

ACK D009v9/HR-AUTH007 and PM-accepted D009v11, correction1/2, recovery0/3 unchanged. The PM authorized the bounded sharing-platform extension after review of the async availability boundary. No auth/API/config/permissions, hardware/scientific thresholds, data/archives, Docker/services, commits or pushes were changed by this author.

**Confirmed RED.** `node --import tsx --test tests/result-ui.test.ts` ran actual production ResultScreen with the complete parsed fictional signed HR fixture and no fresh service read: 7 passed, 1 failed. It rendered cached81.8%, endpoint classification and uncertainty. `/tmp/correction-HR-cached-red.log` retains this expected regression failure. The separately owned backend reproduction established actual authenticated read after authority retirement; this author did not repeat or claim its registry/service work.

**Implemented boundary.** `presentCheckResult` still verifies immutable proof first. Only a verified1.1 result with the typed nonnull cardiac authority companion requires current HR admission; generic historical research, legacy measurement/invalid/inconclusive results and historical nonnumeric row labels retain their existing behavior. ResultScreen withholds HR probability, threshold, classification and uncertainty and explains the need for a fresh authenticated read. Each opening/evidence-return creates a unique view token and requests `/v1/sessions/{id}/result`. The actual ApiClient supplies normal authentication; existing GET semantics do not add a mutation generation header. Local admission independently binds current active owner/capability/check generation and the captured workspace scope. Matched200 must acknowledge the exact evidence SHA and verify to the exact saved result digest. The memory-only marker binds check/result digest/owner/generation/epoch/view; it is outside WorkspaceState and never persisted. Leaving, background/lock, offline, account/generation/scope change, disposal or mismatched/newer read invalidates it. A late older200 cannot reverse a newer refusal. Manual refresh revokes first, requires a new read, and refuses to overwrite a differing saved HR result. No TTL or continuing remote-authority guarantee was invented.

**Export boundary.** Direct `createLocalExport` refuses a selected typed HR result without explicit exact-result admission input; it never silently removes a selected record/result. AppController independently reads every selected HR result before assembly and again at final release; a display marker is never reused. The optional async sharing authorization callback is awaited after native `Sharing.isAvailableAsync`, followed by the original synchronous scope/result guard immediately before file creation/write and again before share. Web authorization precedes Blob/download release. Refusal releases no archive, and native file cleanup remains in `finally`. Measurement and generic non-HR callers retain ordinary synchronous guards. The existing actual-HR serializer fixture now explicitly labels its digest map as a controlled serialization contract, not genuine authority.

**Disclosure-path inspection.** ResultScreen is the existing numeric research display. CheckRow/Home/History use historical labels without scalar output. EvidenceScreen shows original state/evaluated time/reasons, frozen context, measurements and attempts; its expandable JSON is capture component metadata, not stored result JSON. The stopped-conflict JSON panels show snapshots, not results. No result clipboard/raw-result-copy route was found. Local archive serialization was the additional cached numeric path and is now guarded. Immutable retained records are preserved; the correction does not recall previously shared files or establish scientific approval.

**Regression assertions.** `hr-read-admission.test.ts` has8 cases using actual AppController+ApiClient/AuthManager transport with controlled HTTP responses: matched authenticated200/evidence/result/owner/generation;403/422 and offline refusal; missing acknowledgment/202/result mismatch; owner mismatch before request; manual refresh refusal and immutable mismatch; same-account memory-cache reopen; deferred200 after view/route/offline/account/generation/background changes; older200 versus newer refusal; direct export contract refusal; independent preassembly/final-release reads with zero downloads on retirement. `sharing-admission.test.ts` has3 cases executing bundled actual native sharing code against explicit filesystem/sharing boundary doubles: deferred availability/current admission refusal, last-await scope guard, cleanup after write-before-share rejection, ordinary caller behavior. This is not actual OS execution. The actual screen SSR regression also checks verified positive display, preserved measurements/record digest and unchanged generic historical research.

**Browser evidence.** Two new scenarios run on both phone and desktop (4cases) using actual controller, production screens and the actual browser memory WorkspaceStore; only current-service responses are controlled. They verify withheld-before-read, matched200, evidence-return fresh403, manual refresh refusal, late200 after leaving and reopened422. No production test-only route/injection was added. Initial harness attempts used an incorrect Back/accessibility label and lacked a writable memory store; those interrupted/failing development runs are retained under `/tmp/correction-HR-browser-focused*.log` and are not counted as passes. Final exact labels include the ActionRow punctuation. Original component/raw/privacy assertions remain; the alcohol component fixture only supplies the new controller admission predicate.

**Current source checks (all exit0):**

- `node --import tsx --test tests/hr-read-admission.test.ts tests/sharing-admission.test.ts tests/result-ui.test.ts tests/research-result.test.ts tests/result-presentation.test.ts`:34/34PASS,0skip (`/tmp/correction-HR-focused2.log`).
- `npm test`:385/385PASS,0fail/cancel/skip/todo (`/tmp/correction-HR-unit-final.log`).
- `npm run test:coverage`:385/385PASS,0fail/cancel/skip/todo; executable TypeScript coverage91.14059386693881%, strict>80% (`/tmp/correction-HR-coverage-final.log`, `apps/mobile/reports/mobile-unit-coverage.json`). Conservative inventory still counts `src/platform/sharing.native.ts` unloaded/zero despite the separately bundled boundary execution; no native OS coverage is inferred.
- `npm run typecheck` and `npm run format:check`:0 (`/tmp/correction-HR-typecheck-handoff.log`, `/tmp/correction-HR-format-handoff.log`).
- `CI=1 EXPO_NO_TELEMETRY=1 npm run export:web`:0 (`/tmp/correction-HR-export.log`), after the final production edit; later edits were test fixture/selector changes only.
- `CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm run test:e2e -- e2e/components.spec.ts -g 'actual HR'`:4/4PASS9.2s (`/tmp/correction-HR-browser-focused5.log`).
- `CI=1 EXPO_NO_TELEMETRY=1 PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm run test:e2e -- e2e/components.spec.ts e2e/raw-recordings.spec.ts`:72/72PASS1.9m, no skipped cases (`/tmp/correction-HR-browser-final.log`).

Coverage source digest: `75b08a0d2043e26cfae1fcc97d82d510603dedca7f779bdf83caf531e64324db`. These are author preflights on the bound files below. PM final committed-source gates/CI and all independent reviews remain required; no completion/merge/deployment/participant-use or actual native/hardware/scientific qualification is asserted. Generic cached non-HR history remains allowed. The backend must enforce current HR read admission; the client marker records only the successful current read for the active view/operation, with no invented scientific lifetime.

Current D009v11 source/test bindings (prior report snapshots remain historical):

```text
b732ee942a27c57abd638ef5806574c574b746313c29101ca19a925e68d95665  apps/mobile/src/controller.ts
17b4d4f2e7bf60909c41f0cc6359655c6175d3e978bb0ccb9bc70fa08af7bcd0  apps/mobile/src/core/resultPresentation.ts
6cc4977cc639f5629629ce09f25651e1fb63add8c96ddf740add87698ad5b22d  apps/mobile/src/services/export.ts
4742d753029e4d03e4536863203517501ed4e8516dc6e0efe977e4bb1126a419  apps/mobile/src/platform/sharing.ts
8b0d71f308e8f0feb988e8ee9c7cce0cade86ca55e8ff8da58261d7795213f89  apps/mobile/src/platform/sharing.native.ts
52bb48e4cc5e71e73df793c34e7204d6100eb8c7ea6a6cecc0a06040a3686be7  apps/mobile/src/ui/checks.tsx
b55d7461225c3c94494bbbeb5317d63fb7f1736da8ed1a64af7a55c1645a0142  apps/mobile/tests/hr-read-admission.test.ts
75df19a0364a14c763f81523c72f0fe32a7a71405d365105279cd9cc88d55418  apps/mobile/tests/sharing-admission.test.ts
f6252bca25084765c1681b662b6acbb1493483b08046f9547ec617f709b5e5aa  apps/mobile/tests/result-ui.test.ts
d8f22b8bc0ed8468d22c5f075419bc06aa09d2532f04ff169d3032b7a4ee8682  apps/mobile/tests/research-result.test.ts
38c9dfa9f9c0ddf2313779ceb9f915039acbf31a6d2bd35851f36340284cf1c5  apps/mobile/tests/support/result-rendering.tsx
a0811f2434ec80f0603fb0fdb509b96c3b7d030fbbe6d2f62fa2bcf6df1cb713  apps/mobile/e2e/components.spec.ts
e35e26086e482febc5136eb57424964d1c2f9a58172afb7328339ba657d9d0f6  apps/mobile/e2e/fixtures/hr-result-component.tsx
9509dc311794d5a7ab7fa4f0bec2619a0ef3d021b6cb2fb68239055adc4a1ef3  apps/mobile/e2e/fixtures/alcohol-component.tsx
```
