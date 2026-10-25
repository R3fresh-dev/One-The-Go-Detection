# D012v1 / APR-001 — independent engineering addendum

**ACK: AFFECTED. OTGD-007 IMPLEMENTATION PASS is superseded by BLOCKED.** The other46 engineering decisions remain unchanged. Effective engineering disposition is **2 PASS (OTGD-002/004), 45 BLOCKED; full application acceptance NEEDS_HUMAN**. The two OTGD-007 recorded scenario PASS observations remain valid at their tested boundaries; they do not prove the additional normative About clause.

Reviewer `/root/replacement_engineering`, independent nonauthor engineering signer, explicitly configured OpenAI `gpt-6.1-sol/high`; effective runtime-model query unavailable. Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`, tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`, fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`, run `otgd-20261025-0555`. Correction2/2 and recovery0/3 unchanged.

I independently inspected the complete About function, shared Page/App rendering, capability fixture and actual assertion call sites. I missed the explicit About requirement in the earlier PASS judgment; this addendum corrects that judgment without altering the historical47-decision record.

## Independently corroborated source trace

- Canonical `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md:4` requires About to show both the actual environment and the account's currently admitted scope. The complete requirement controls acceptance, beyond its two named scenarios.
- `apps/mobile/src/ui/manage.tsx:1686–1765` renders About. The only `model` reads select the Back destination from notice/identity at1693–1697. Visible facts use compiled `BUILD`, platform/constants and static text. The environment is shown, but current identity/capabilities/data generation/offline state never reaches a scope display. Generic statements about ordinary checks, conditional research and no bundled approval cannot distinguish an admitted account from an ordinary, revoked or mismatched scope.
- `apps/mobile/src/ui/components.tsx:567+` Page supplies navigation/focus/heading/children, with no account-scope rendering. `apps/mobile/App.tsx:218` selects About; shared chrome at approximately396–408 shows LOCKED, ACCOUNT/environment, GUEST and OFFLINE. The adjacent ContextStrip receives only browser/guest context. None supplies the missing current admitted scope on About.
- `apps/mobile/e2e/fixtures/availability-component.tsx:8–25` defaults `about=false` to StatusScreen and selects About only for `about=true`. In `apps/mobile/e2e/raw-recordings.spec.ts:1407–1464`, dynamic approved/unavailable-channel and conditional-research assertions run on StatusScreen. After selecting About, the assertion checks only the static1.1 reader/no-bundled-approval text. Those passing observations do not exercise About's current-account scope clause.

This is source/control-flow evidence of an omitted required status display, consistent with approver APR-001/P2. It is not a new runtime reproduction, security authority bypass or scientific validity claim. Positive shared gates and the two valid scenario outcomes do not establish the unmet About requirement.

## Supporting SHA-256 bindings

| Artifact | SHA-256 |
|---|---|
| Approver report | `cfd31ee67e6e948bde6c1b123a77220367916e206f03345d30ad727520d19a31` |
| Historical engineering report, preserved verbatim | `ae49af4ff368073835022ae31e579336d9e1154fb4ba96ccdb5c3ccc1d9c4fec` |
| Historical engineering47decisions, preserved verbatim | `af9b06414253674020670b5eaefe9a75c1520dedf5fcc88f41d8ff46d2f53ed5` |
| Canonical OTGD-007 | `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6` |
| `src/ui/manage.tsx` | `023fd4fdb5819fd85be7dbd181a89d265cb24606b75ee21891b1136e66c210ac` |
| `src/ui/components.tsx` | `adc89118200592946e0f95cf2db81caadcbd627569a63f940f2b512ffb3a2071` |
| `App.tsx` | `62355551f8ab206fd0eb9efc2bec18f27256444b03a7119c660d8663d039207d` |
| `e2e/fixtures/availability-component.tsx` | `2c4aefe28e179bcb95016f52aaede5ffed51194074157b08edd95361bb3c966c` |
| `e2e/raw-recordings.spec.ts` | `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd` |

## Effective final boundary

Required action remains human handling of the exhausted correction limit and unmet normative clause, or preexisting direct proof of that About call path. No automatic third correction, new test order or scope waiver follows. Any subsequently authorized correction would need truthful current scoped presentation and direct About-path proof while preserving independent authority controls.

Original report/JSON, source, released782case/411requirement evidence and all other decisions are unchanged. D011's source-versus-metadata evidence-branch distinction remains unchanged. All7local/14CI gate passes remain factual; APP_VERIFIED/RELEASE_READY, merge/deployment and participant use remain unapproved. No tests, runtime/build/browser probes, source/Git/service/dependency actions or additional agents were performed. No denied or uncertain mutation exists. This addendum is the sole new engineering artifact and is released for final council reconciliation.
