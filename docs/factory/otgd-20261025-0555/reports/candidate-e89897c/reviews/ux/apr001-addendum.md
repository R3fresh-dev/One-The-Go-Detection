# APR-001 / D012v1 independent UX addendum

**ACK: AFFECTED. Prior OTGD-007 UX IMPLEMENTATION PASS is superseded by BLOCKED.** Other46 decisions remain unchanged: OTGD-002/004 PASS;44 previously blocked specs remain BLOCKED. Effective combined UX disposition is2 scoped PASS/45BLOCKED, with overall NEEDS_HUMAN handling after exhausted correction2/2. Recovery0/3. Original report.md/per-spec-decisions.json and all original47 decisions are preserved verbatim as history; this addendum is the sole new write.

Reviewer `/root/replacement_ux`, independent nonauthor, explicitly configured OpenAI gpt-6.1-sol/high; independent runtime-model query unavailable. Candidate e89897cc852a111b131eaf5c2caaf163ef201a48/tree6b43a0a3058eb30bddb08d9476ca58929e7733f1/fingerprint1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7. D012v1 ACK delivered by actual PM message. D001–D011 preserved; auxiliary evidence documentation is not separately application-tested. No source/tests/runtime/Git actions or third correction.

## Independent narrow trace

Canonical OTGD-007 AND-SET-004 expressly says About SHALL show the actual environment and account's currently admitted scope. I read the complete AboutScreen function at apps/mobile/src/ui/manage.tsx:1686 through its closing brace. Its only model-dependent branch selects Back destination from acknowledgedNotice/identity. Rendered content correctly identifies BUILD.environment, binary/version/native platform and static general research limitations. Its research-result fact varies only with BUILD.hostedPreview and describes binary format support/no bundled approval. No current account capability, admitted scope, generation or offline/revocation observation is read or rendered. Thus account admission changes cannot update About's required current-scope status.

I also inspected Page in ui/components.tsx:572 onward: it adds heading, Back, eyebrow, subtitle and children, with accessibility/scroll handling, and no account-scope fact. App.tsx routes about to AboutScreen and status to StatusScreen separately (218/219). Its shared chrome around390 onward displays LOCKED/ACCOUNT plus environment/GUEST and connectivity context; account identity/environment is not currently admitted research/channel scope. No shared rendering supplies the missing About fact.

The passing capability test at e2e/raw-recordings.spec.ts:1407 first calls renderAvailability(caps) without about=true. availability-component.tsx defaults about=false, so its conditional channel/model assertions render StatusScreen. The later about=true call renders AboutScreen but checks only static Version1.1 proof-bound support/no bundled model text. Hosted assertions return to StatusScreen. These true observations do not exercise About's current account-scope obligation. No new runtime execution was performed; this is deterministic source/control-flow and assertion-target inspection.

## Disposition and correction to my prior review

APR-001/P2 is a demonstrated missing required status display, not solely an unexecuted test, a permission bypass or newly observed authority grant. My prior007 PASS overextended valid capability-screen and legacy-refusal scenarios to the entire normative requirement. I accept the approver's finding based on the independent trace above and supersede that PASS with BLOCKED. Both existing scenario PASS observations remain unchanged and true; the verifier's original782 case records and current successful gates are not rewritten. Gates do not close this omitted normative About clause.

Minimum next action is explicit human handling of this unmet requirement after exhausted correction2/2. A future authorized change would need actual About rendering for matching admitted, ordinary/revoked, mismatched generation/account and offline states while preserving all authority guards; no fix or additional test is authorized or attempted here. No APP_VERIFIED/RELEASE_READY/global completion follows. No action was denied or has an uncertain external outcome.

## Binding

Approver report independently rehashed to cfd31ee67e6e948bde6c1b123a77220367916e206f03345d30ad727520d19a31.

Preserved prior UX report SHA256: e598cf79a5797cb704cc9b9933fa10d5f90ad73bc4dc4735365a47693759627a. Preserved prior47-decision JSON SHA256:81f1522504e21e1f94f102dd3e1c053d25ed66631f00142cab3fcb2bf9cfd657.

Read-only source SHA256 bindings:
- `apps/mobile/src/ui/manage.tsx`: `023fd4fdb5819fd85be7dbd181a89d265cb24606b75ee21891b1136e66c210ac`
- `apps/mobile/src/ui/components.tsx`: `adc89118200592946e0f95cf2db81caadcbd627569a63f940f2b512ffb3a2071`
- `apps/mobile/App.tsx`: `62355551f8ab206fd0eb9efc2bec18f27256444b03a7119c660d8663d039207d`
- `apps/mobile/e2e/fixtures/availability-component.tsx`: `2c4aefe28e179bcb95016f52aaede5ffed51194074157b08edd95361bb3c966c`
- `apps/mobile/e2e/raw-recordings.spec.ts`: `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd`
- `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md`: `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6`
