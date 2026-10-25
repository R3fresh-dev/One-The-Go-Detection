# Privacy receipt and raw UI correction evidence

Builder `/root/accessibility_builder`; run `otgd-20261025-0555`; accepted D009v4 acknowledged **before edits**, within existing consolidated correction **1/2**, recovery **0/3**. Pinned Factory `4770878e18e9c587c2961b9e2bb13315da31abe9`. Original reviewed candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; current checkpoint HEAD observed `3d2c71a435b261f3291d92ac44f6c91ce416e3cc` plus ongoing authorized worktree corrections. This is **author evidence, not independent signoff, frozen-candidate acceptance or release readiness**.

## Implemented client boundary and presentation

Backend owner `/root/worker_builder` and client owner agreed the exact retained-category shape: `{category, policy_basis, reason, expires_at: string|null}`. Six actual server categories carry existing `privacy-v1`, factual technical reasons and explicit null because no configured exact expiry is known. The client does not infer a date, retention change or legal/scientific authority.

`services/api.ts::parsePrivacyJob` now admits at most32 retained entries; accepts bounded nonblank legacy category strings; and requires exactly the four known structured fields with category/policy at most256 characters and reason at most1000. Nested, unknown, missing, blank and oversized category details are rejected rather than converted to text. Structured expiry must be explicit null or a valid bounded RFC3339 timestamp. Calendar component checks reject normalized impossible dates such as February30; valid leap days and offsets preserve the original string. Displayed top-level receipt timestamps, policy/failure text, scope fields, attempt count and action lists also receive bounded validation. Actual API nullable optional timestamps/failure code are represented truthfully in `PrivacyJob`; existing conflict and preference type areas remain unchanged by this correction.

`manage.tsx::JobCard` renders each actual structured category, its supplied policy basis and reason, and exact supplied expiry string or **No scheduled expiry supplied**. Legacy strings retain their real names with **Legacy receipt: policy basis, retention reason and expiry were not supplied.** No generic category replacement or arbitrary payload stringification remains in this path. Job-level logical expiry remains a separate field. The source change is limited to JobCard; earlier authorized Settings changes are retained.

The regression fixture `apps/mobile/testfixtures/backend-privacy-deletion-receipt.json` is byte-for-byte the backend owner's generated `reports/correction-deletion-receipt.json`: SHA-256 **a237d6c027633bd537e187930149dca08a91bffba75eca38642c3e1f135445ca**. It came from actual API TestClient POST202 followed by GET200 through production handlers with an explicitly controlled journal-accept transport. This is software integration fixture provenance, **not live LocalStack/journal dependency proof**. Tests run this actual receipt through the real client parser and real PrivacyScreen/JobCard, and separately exercise legacy strings, supplied expiry, invalid/nested payloads and length limits.

## Raw assertion repairs

- The lost optional-choice acknowledgment oracle now creates its fictional accepted receipt **once**, preserves the original receipt ID/body, and verifies that the client presents that original ID and immutable receipt after retry. Existing exact request-body, acknowledgment and Idempotency-Key assertions remain. This repairs the test oracle; it is not a claim of an independently executed real-server retry.
- PM explicitly extended narrow ownership to the existing renewal case in `tests/raw-upload.test.ts`. Its test harness records the current committed raw-ticket state at the `/ticket` HTTP boundary. The case now asserts exact `{}` renewal body on lost/replayed/new renewals, POST/generation, epoch1/key/null-ticket committed before both lost-response and replay requests, acknowledged epoch1/artifact identity, and epoch2/new-key/null-ticket committed before replacing the next expired ticket. Original key, retry, buffer wiping and other suite assertions remain. The harness commit adapter stores state in memory: these observations do not establish native SQLCipher durability. No upload/sync/controller production code changed here.
- Actual RawRecordingsScreen SSR and browser component checks distinguish **quarantine · retained**, **cleanup pending · cleanup pending**, and **purged · purged**, independent from the displayed retention deadline. An already-past deadline plus pending cleanup still says **Not confirmed**; only a supplied cleanup timestamp and completed receipt display confirmation. The existing production raw screen required no repair. The earlier product-owned `/Historical research result/` selector is preserved.

Test-only SSR/browser fixtures import actual production parsers/screens, with controlled controller/native inputs. They add no production fixture injection or native storage fallback.

## Executed checks

Commands ran from `apps/mobile` using installed dependencies. No install, retained-service/Docker operation, data reset, export rebuild, commit, push, supervision change, merge, deployment, paid service or participant action was performed by this builder.

| Check | Actual result | Evidence file |
|---|---|---|
| `node --import tsx --test tests/privacy-receipt.test.ts` before implementation | **4 intended failures**: missing null-expiry wording, lost legacy names, omitted exact supplied expiry, malformed category date accepted | `privacy-red.log` |
| Additional nonblank-category regression before guard | intended failure on legacy `" "` | `privacy-blank-red.log` |
| `node --import tsx --test tests/privacy-receipt.test.ts tests/raw-recordings.test.ts tests/raw-upload.test.ts` | **20 passed,0 failed/skipped**, exit0 | `privacy-raw-direct-final.log` |
| `npm test` after final source/test changes | **358 passed,0 failed/skipped**,18.1s, exit0 | `full-unit-final.log` |
| `npm run typecheck` | exit0 | `typecheck-final.log` |
| Installed Prettier `--check` on changed client/test/harness files | all matched files pass, exit0 | `format-check.log` |
| `git diff --check` on changed tracked paths | exit0 | terminal record |
| `PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm exec -- playwright test e2e/raw-recordings.spec.ts --grep 'actual raw receipt screen\|actual API privacy receipt'` | **4 passed**,9.0s, both viewports, exit0 | `browser-focused.log` |
| `PLAYWRIGHT_BROWSERS_PATH=/tmp/otgd-playwright npm exec -- playwright test e2e/raw-recordings.spec.ts` | **42 passed**,1.2m, both viewports, exit0 | `browser-full.log` |

The full browser suite preserves existing raw choice/export/upload, ownership, permission, interruption and historical alcohol assertions. The two new scenarios mount real parsed privacy/raw receipts, update state in the same screen, and assert that obsolete labels disappear. These are controlled browser components, not live/native dependency checks. Initial test development also retained an incorrect fixture enum (`deleted`); the existing admitted server enum is `purged`, so the fixture was corrected without modifying production state semantics. The initial SSR harness missing react-dom TypeScript declaration was fixed using the repository's typed-require pattern, without installing packages. All failure logs remain retained.

The browser owner explicitly released both ports; this builder then used the PM-announced8082 slot. After completion `ss -ltnp 'sport = :8082'` showed no listener and PM received release. Production export directories were not rewritten.

Raw evidence is preserved in ignored `reports/correction-privacy-raw-ui-round1/`, duplicated at `/tmp/otgd-privacy-raw-evidence/`, including both complete embedded Playwright HTML reports. Key SHA-256 hashes:

```text
bad6266b93b916f773940129cc638125d981aa3f46df105972ce1596f79bd022  privacy-red.log
1a79d212361650e3eee1dee74023ff99285682db66878084c1955b1ec07370c0  privacy-blank-red.log
5b515a5b3e2e9627a23d3c7c1b53d71d648295877b38038478ec3abd217f96fd  privacy-raw-direct-final.log
584cc8f054539c68bdfe8539a03824d0d196597e4872e21dcf93c91bed17d6d4  browser-full.log
f7793f1a7d3722a51b681489abc130e9d769d2ece5aec3a580a7d8e2f57ff15c  full-unit-final.log
88c289e1a9530b9294e7d0cea6a65392dc85ee1b03f56a85ba57c1a11b8134fa  owned-SHA256SUMS
```

Current source/test snapshot (whole shared-file hashes also include other previously authorized changes):

```text
55987fdae9b06762e5e31118a52f64eb6256e782fe921b3c5b16674cfd1f0e94  apps/mobile/src/services/api.ts
22b36cd917e6d961cae3bea3487ba281baf2d0d4cd0d7ec38500aca140c1608a  apps/mobile/src/core/types.ts
1c74b1ebbc41ff28a837ee7f1e62d5aacb82031453ab1f222db2a0f0f24a6dc9  apps/mobile/src/ui/manage.tsx
064fd7d4007a4a2f9752a98c557b35af90e1958145d1326bf047b91144c4d6f3  apps/mobile/tests/privacy-receipt.test.ts
6dacbfb5a34b82dd7b3fb85496f718f5de3cf5ee15ac64cd6bd3f9a28bd23ddc  apps/mobile/tests/support/privacy-rendering.tsx
f2d9a32b5ff0e11ca6aacfb3ea86b246341a1900cfa0042623a0552222900a08  apps/mobile/tests/raw-recordings.test.ts
90d5120384148e33dd319309f64395cc83057aa1fe500cee90ee906746ad95ef  apps/mobile/tests/raw-upload.test.ts
e6be520ba3f81acdde4ac09e79f0c1049c4d96a2d27f5eab592008a02dd2bc9f  apps/mobile/e2e/raw-recordings.spec.ts
0d9f69fdc251681e9dd0a13fad43b4d9d2dd18ce8a978bc375214e9c73e5963b  apps/mobile/e2e/fixtures/privacy-raw-receipt-component.tsx
a237d6c027633bd537e187930149dca08a91bffba75eca38642c3e1f135445ca  apps/mobile/testfixtures/backend-privacy-deletion-receipt.json
```

## Remaining prerequisites

No action was denied or left with an uncertain external outcome. Actual Android/iOS OS workflows, native encrypted storage/durable process recovery, real dependency execution and physical cleanup were **not executed in this component/unit scope**; no installed native OS target was supplied. A displayed receipt/deadline is not proof of universal physical erasure or cleanup of copies already shared.

The final combined-source freeze, unchanged-source mandatory local gate, coverage strictly greater than80%, exact-tree14-job CI evidence,782-case reconciliation, affected independent rereviews and final approver remain PM/council prerequisites. Other authorized authors continued shared corrections during these development checks; the hashes and passes here must not be represented as a frozen final-candidate gate. Scientific/clinical/hardware/participant/cloud release requirements remain separate. This report neither signs off its own changes nor authorizes release.
