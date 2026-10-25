# APR-001 independent CODE addendum — D012v1

**AFFECTED. Prior OTGD-007 code-specialist PASS is superseded by BLOCKED.** I independently confirm the approver's APR-001/P2 source/control-flow finding. Other46 code dispositions remain unchanged. Effective code review totals are2 scoped PASS (OTGD-002/004) and45 BLOCKED; overall NEEDS_HUMAN after final correction2/2. The original47 decisions, report and released verifier782-case record remain verbatim history; this addendum is the explicit narrow supersession. The two recorded OTGD-007 scenario PASS observations remain true, but do not prove the entire normative requirement.

Reviewer `/root/replacement_code`, independent configured OpenAI `gpt-6.1-sol/high`; no independently queryable runtime-model attestation. Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`, tree `6b43a0a3058eb30bddb08d9476ca58929e7733f1`, frozen fingerprint `1855fca1465dc9e19c006cba7b749967ebc28c839282b42c56079ca6159c19a7`, IMPLEMENTATION scope. Actual D012v1 ACK AFFECTED sent to PM before this disposition. D011 source/evidence separation and all D001–011 boundaries persist. No new runtime test or execution is claimed.

## Independently checked trace

Canonical `openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md`, AND-SET-004, expressly requires: “About SHALL show the actual environment and account's currently admitted scope.” The environment is displayed, but the current account scope is missing.

- Whole `AboutScreen` in `apps/mobile/src/ui/manage.tsx:1686–1766` reads `model` only inside its Back-navigation handler. Rendered facts come from BUILD/platform/static strings. The generic research limitation and1.1 reader-support text cannot distinguish a currently admitted account from ordinary, revoked, offline or mismatched scope. No identity/capability/generation/offline value reaches a current-scope display.
- `Page` in `src/ui/components.tsx:567` only supplies heading/navigation/layout/accessibility and its provided children; it receives no capability scope. `App.tsx:218` routes AboutScreen directly. Shared chrome around `App.tsx:401` supplies ACCOUNT/environment/GUEST/OFFLINE, and ContextStrip supplies browser/guest persistence information; it does not supply currently admitted research/channel scope. Thus the missing About status is not supplied by a shared rendering path.
- The passing `raw-recordings.spec.ts:1407` conditional approval assertions call `renderAvailability(caps)` with default `about=false`. `e2e/fixtures/availability-component.tsx:8–25` therefore renders StatusScreen. The later `renderAvailability(caps,true)` selects About and asserts only the static1.1 proof-bound reader/no-bundled-approval wording. This is valid evidence for those displayed strings and separate capability scenarios; it does not establish About's current admitted scope.

This is a concrete missing required status display shown by source/control flow. It is not inferred solely from an absent test, nor is it a demonstrated authorization bypass. My prior007PASS overextended the two valid scenario observations to the unproved normative About clause; this addendum corrects that judgment without rewriting historical evidence.

## Disposition and boundaries

OTGD-007/AND-SET-004: **BLOCKED — APR-001/P2**. Exact unmet clause: About must display the actual account's currently admitted scope, using current trusted identity/capability/generation/online policy as applicable. The current source cannot do so. Existing StatusScreen observations do not close the About call path. All7 local/all14CI successes remain true; they do not cover or cure this omitted requirement.

Other46 dispositions and previous CODE001/002/R1-003/R1-004 closures are unchanged. No original canonical spec, per-case count/status, prior47-decision file, source or test was modified. No fix/test/runtime/Git action, extra worker, merge, deployment or participant use occurred. Only this addendum is written. Correction2/2 and recovery0/3 remain exhausted/preserved; no third automatic correction is authorized. Minimum next action is human scope/budget/evidence adjudication of APR-001. A later explicitly authorized correction would need the actual About path to reflect current scope and preserve refusal/measurement defaults; this addendum does not authorize it. No APP_VERIFIED, RELEASE_READY or global completion decision follows.

## Bindings

| Artifact | SHA-256 |
|---|---|
| Original code47 decisions (unchanged) (`/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/reviews/code/per-spec-decisions.json`) | `d4fbf4ce67dbebe9734c7dd370c33c2dba11da87620f4495a885bdab2ec18298` |
| Original final code report (unchanged) (`/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/reviews/code/report.md`) | `67237a2968e6bca498ffe2ed931624becaf22badc903dd6fac99c39f634c7af0` |
| Released final approver report (`/workspace/scratch/otgd-20261025-0555-live/candidate-e89897cc852a/reviews/approver/report.md`) | `cfd31ee67e6e948bde6c1b123a77220367916e206f03345d30ad727520d19a31` |
| Canonical OTGD-007 (`/workspace/One-The-Go-Detection/openspec/changes/authorized-model-execution/specs/android-settings-accessibility/spec.md`) | `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6` |
| About/Status implementation (`/workspace/One-The-Go-Detection/apps/mobile/src/ui/manage.tsx`) | `023fd4fdb5819fd85be7dbd181a89d265cb24606b75ee21891b1136e66c210ac` |
| Page implementation (`/workspace/One-The-Go-Detection/apps/mobile/src/ui/components.tsx`) | `adc89118200592946e0f95cf2db81caadcbd627569a63f940f2b512ffb3a2071` |
| App routing/chrome (`/workspace/One-The-Go-Detection/apps/mobile/App.tsx`) | `62355551f8ab206fd0eb9efc2bec18f27256444b03a7119c660d8663d039207d` |
| Actual availability fixture (`/workspace/One-The-Go-Detection/apps/mobile/e2e/fixtures/availability-component.tsx`) | `2c4aefe28e179bcb95016f52aaede5ffed51194074157b08edd95361bb3c966c` |
| Passing conditional/static About assertions (`/workspace/One-The-Go-Detection/apps/mobile/e2e/raw-recordings.spec.ts`) | `889dd5531958c8b2995141698485fd3e192db80db2402e41ee3527129fab1abd` |

Recorded 2026-10-25T11:51:03.511130+00:00. No action was denied or has uncertain mutation effects.
