# Correction round 1 — product presentation

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

Valid HTTP 429 Retry-After delays from zero through the supported one-hour ceiling schedule the existing waiting state (minimum one second) and also fence explicit retry until that deadline. Exactly at the deadline another attempt is eligible. A larger supported-wire delay stops the upload rather than silently retrying earlier than requested. The UI states the one-hour supported bound. Existing eight-attempt automatic retry limits remain unchanged.

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

### Final executed commands for this author handoff

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
