# D012 v1 / APR-001 — independent UI addendum

**ACK: AFFECTED. OTGD-007's prior UI PASS is superseded by BLOCKED.** The normative About clause is unmet. The other 46 recorded decisions are unchanged: effective UI disposition is **2 scoped PASS (OTGD-002/004), 45 BLOCKED**. The final council's NEEDS_HUMAN outcome is consistent with this correction; no aggregate APP_VERIFIED or release approval is given.

Reviewer `/root/replacement_ui`, independent nonauthor, configured OpenAI **gpt-6.1-sol/high**; independent runtime model query unavailable. Candidate **e89897cc852a111b131eaf5c2caaf163ef201a48**, tree **6b43a0a3058eb30bddb08d9476ca58929e7733f1**, fingerprint **1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7**. Correction **2/2**, recovery **0/3**. This addendum changes the independent UI judgment only; it neither edits the frozen source nor rewrites the historical 47 decisions.

## Independent finding confirmation

**APR-001 / P2 — OTGD-007, AND-SET-004.** The canonical amendment expressly requires: “About SHALL show the actual environment and account's currently admitted scope.” It also permits conditional research availability without clinical validation. The current About screen satisfies the environment part but does not display the current account's admitted scope.

I independently traced the source and test selection, rather than adopting the approver's conclusion from its label:

- `apps/mobile/src/ui/manage.tsx:1686–1765`: AboutScreen uses `model.state?.acknowledgedNotice || model.identity` only to choose the Back destination. Rendered content reads build/platform constants and static explanatory text. The environment Fact is actual build environment, while the research-reader Fact reports static 1.1 support/preview mode. There is no current account capability, account/generation scope or admission-state read in the About content.
- `apps/mobile/src/ui/components.tsx:567–650`: shared Page receives title, eyebrow, subtitle, children, Back and scroll properties. Its navigation context handles focus; it has no account/capability scope input or injected scope display.
- `apps/mobile/App.tsx:218–219,402–421`: About and Status are distinct routes. Shared chrome shows locked/account/guest, build environment and offline status; ContextStrip receives browser/guest flags. These do not supply About with the currently admitted account scope.
- `apps/mobile/e2e/fixtures/availability-component.tsx:8–25`: `renderAvailability(capabilities, about=false)` renders StatusScreen unless explicitly passed true. The fixture's supplied capabilities do not turn static About text into a current-scope display.
- `apps/mobile/e2e/raw-recordings.spec.ts:1422–1435`: dynamic approved/unavailable channel and conditional current research assertions call the default fixture route, therefore test StatusScreen. At `1438–1446`, the About=true assertion verifies only the static “Version 1.1 proof-bound research endpoint support; no model or approval is bundled” text. StatusScreen's dynamic capability read is visible in `manage.tsx:1808–1815,1826–1867`; it is not an About assertion.

For the same build/platform, varying the current account's admitted versus revoked/unavailable capabilities cannot change About's content because those values do not participate in that rendering path. This is a deterministic source/control-flow defect in a named normative clause, not merely an absent test. No new runtime reproduction, browser run or test execution is claimed. Its impact is missing current-scope information at the required About destination; no authority bypass or clinical harm is inferred.

## Effect on the previous decision

The two existing OTGD-007 scenario PASS observations remain true: the actual capability component can present conditional availability without claiming clinical validation, and legacy/unapproved/public-format claims do not grant numeric inference. Their current executions remain valid. They do **not** cover the complete About-specific normative requirement. My previous acceptance treated those scenario observations and the static About explanation as sufficient for the whole amendment; that judgment was too broad.

The prior OTGD-007 PASS is therefore superseded by **BLOCKED**, with APR-001 as its required source correction. No new 782-case reclassification is fabricated and no source defect count is inferred from aggregate evidence. Other 46 UI judgments and all prior gate results/finding closures remain unchanged. Since correction round2/2 is exhausted, handling this defect requires the responsible human decision; no third automatic correction, fix or new test run is authorized.

## Authority, preservation and evidence

D012v1 AFFECTED acknowledgment was delivered to PM through actual native messaging before this addendum. D001–D011 remain in force, including measurement defaults, fictional provenance, independent scientific/participant controls and the primary-source versus metadata-only evidence-branch distinction. A future records commit is not separately application-tested. No source/test/runtime/service/dependency/Git write was performed; the sole new output is this owned addendum.

Approver report was independently rehashed to **cfd31ee67e6e948bde6c1b123a77220367916e206f03345d30ad727520d19a31**. Original UI files remain verbatim history:

| File | Unchanged SHA-256 |
|---|---|
| report.md | e8730fc7434b3857255d0438d8f2f165fc2f17752c3327752b58b30d2bfaf9a7 |
| per-spec-decisions.json | 3ff12de3b1b2746dfaeccc3df32e59275e28a8871205ca6c1b507b6fe319d0e4 |

Current inspected file bindings:

| Path | SHA-256 |
|---|---|
| openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md | 8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6 |
| apps/mobile/src/ui/manage.tsx | 023fd4fdb5819fd85be7dbd181a89d265cb24606b75ee21891b1136e66c210ac |
| apps/mobile/src/ui/components.tsx | adc89118200592946e0f95cf2db81caadcbd627569a63f940f2b512ffb3a2071 |
| apps/mobile/App.tsx | 62355551f8ab206fd0eb9efc2bec18f27256444b03a7119c660d8663d039207d |
| apps/mobile/e2e/fixtures/availability-component.tsx | 2c4aefe28e179bcb95016f52aaede5ffed51194074157b08edd95361bb3c966c |
| apps/mobile/e2e/raw-recordings.spec.ts | 889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd |

No action was denied or left uncertain. APR-001 remains a confirmed unmet software requirement; the final exhausted-round disposition remains BLOCKED/NEEDS_HUMAN. No deployment, merge or participant-use approval follows.
