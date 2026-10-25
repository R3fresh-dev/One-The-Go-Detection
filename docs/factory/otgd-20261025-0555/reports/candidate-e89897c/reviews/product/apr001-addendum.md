# D012v1 / APR-001 independent product signoff addendum

**AFFECTED. Prior OTGD-007 IMPLEMENTATION PASS is superseded by BLOCKED.** The other46 product decisions remain unchanged: OTGD-002/004 PASS and44 other specifications BLOCKED. The resulting product disposition is **2 scoped PASS /45 BLOCKED**, with complete-application acceptance **NEEDS_HUMAN** after exhausted correction2/2. Recovery remains0/3. No third automatic correction is authorized.

Reviewer `/root/replacement_product`, independent nonauthor; configured OpenAI `gpt-6.1-sol/high`, no independently queryable effective-runtime attestation. Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`, tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`, tested fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`. D001–011 and the D011 primary-source/auxiliary-records distinction remain unchanged.

## Narrow independent source finding

I independently confirm **APR-001 /P2 /OTGD-007 AND-SET-004**. The canonical modified requirement says: “About SHALL show the actual environment and account's currently admitted scope.” About correctly displays its compiled environment, but its account-scope display is absent.

- `apps/mobile/src/ui/manage.tsx:1686–1765`: AboutScreen reads `model` only to choose the Back destination. Its generic research limitations and reader-support/no-bundled-model statements are static or build-derived. Identity, account capabilities, data generation and offline/revoked scope never reach a substantive About status value. Admitted and ordinary/revoked/mismatched accounts therefore receive the same scope presentation.
- `apps/mobile/src/ui/components.tsx:567–650`: Page wraps supplied title/eyebrow/subtitle/children and navigation/focus/scroll behavior; it has no account/capability input and supplies no missing current scope.
- `apps/mobile/App.tsx:405–425`: shared chrome labels ACCOUNT/environment, GUEST and OFFLINE. ContextStrip receives browser/guest inputs only. These do not identify current independently admitted research/channel scope.
- `apps/mobile/e2e/fixtures/availability-component.tsx:8–25`: `about=false` selects StatusScreen; only `about=true` selects AboutScreen. `apps/mobile/e2e/raw-recordings.spec.ts:1407–1463` asserts conditional approved/unavailable/current-model wording on Status, then switches About on only to assert the static version1.1/no-bundled-model string. These valid executions do not establish the additional About clause.

My previous OTGD-007 approval accepted those Service/Status scenario proofs as sufficient for the entire requirement. That was an incomplete normative assessment. The two recorded scenario PASS observations remain true; neither they nor the unchanged782-case evidence register is rewritten by this addendum. This is a source/control-flow-confirmed missing required status display, not a new runtime observation or a grant-of-authority vulnerability.

## Supersession and remaining action

The original47-decision files remain verbatim historical evidence. This addendum supersedes only their OTGD-007 PASS and any derived3-PASS/44-BLOCKED total. All other46 dispositions, prior repair closures, exact-source7local/14CI success and software/nativeOS/hardware/science/study/deployment limits stand. Overall application and release approval remain withheld.

Minimum next action is human scope/correction-budget handling or direct existing proof of the required About call path. Any later authorized repair must preserve current identity/generation/capability guards and demonstrate that About itself displays actual admitted scope; no automatic repair, duplicated test requirement, third round, merge, deployment or participant use follows.

No new runtime/test execution, source/test/runtime/Git modification, delegate or external action occurred. Only this addendum was written. No action was denied, left pending after mutation or has an uncertain external outcome.

## Evidence identity

Recorded at 2026-10-25T11:51:18.785298+00:00.

Original product report SHA-256 `51e33da06eb3fffd7ac1ff3467382866af77af315798434eef70273810cfe7cc`; original47 decisions SHA-256 `47d09bdbde122e170a786dcace4c12fd25d3f657fb10b9b39e73f193ec214fe1`. Both rechecked unchanged.

Independent approver report SHA-256 `cfd31ee67e6e948bde6c1b123a77220367916e206f03345d30ad727520d19a31`.

- `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md` — SHA-256 `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6`
- `apps/mobile/src/ui/manage.tsx` — SHA-256 `023fd4fdb5819fd85be7dbd181a89d265cb24606b75ee21891b1136e66c210ac`
- `apps/mobile/src/ui/components.tsx` — SHA-256 `adc89118200592946e0f95cf2db81caadcbd627569a63f940f2b512ffb3a2071`
- `apps/mobile/App.tsx` — SHA-256 `62355551f8ab206fd0eb9efc2bec18f27256444b03a7119c660d8663d039207d`
- `apps/mobile/e2e/fixtures/availability-component.tsx` — SHA-256 `2c4aefe28e179bcb95016f52aaede5ffed51194074157b08edd95361bb3c966c`
- `apps/mobile/e2e/raw-recordings.spec.ts` — SHA-256 `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`
