# UI design council — initial frozen-candidate review

Created: 2026-10-25T07:44:26.619300+00:00
Role: independent UI design reviewer /root/review_ui. Configured OpenAI gpt-6.1-sol, high reasoning, fork:none, confirmed by PM message; exact effective runtime attestation is not exposed. No authorship of reviewed implementation/specs.
Candidate: `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; baseline `0844868aa543af4ab75ac5065ad48cf807b86bb3`; working-tree SHA-256 `36ed8d800edcb560ac8ca189e98b64518b3342a29458d6e91a8d943085310f8c`. Factory pinned `4770878e18e9c587c2961b9e2bb13315da31abe9`.
Input, artifact, canonical current SHA-256 and exact per-spec criteria bindings: [review-bindings.json](review-bindings.json) (SHA-256 `915accf1d72ba02d0d9648a2a37396aeb38130b6878d7c12d8cefcaaad66200c`).
Scope: IMPLEMENTATION UI specialist review across all47 canonical inventory entries; static requirements/source inspection plus bounded independent guest rendering. This is initial review before final gate evidence followup.

**Verdict: CHANGES_REQUIRED.** UI-001 and UI-002 are source-confirmed acceptance defects. No spec receives final PASS. Other rows are BLOCKED awaiting specific current execution evidence; this is not a declaration that every backend spec has a UI defect. Formal correction round0/2 and recovery0 remain unchanged.

## Checks and observed evidence

- Read repository AGENTS.md and pinned Factory SKILL/spec-council/evidence/communication/model-policy/agent brief. Reviewed all47 canonical requirement sets for UI relevance; read selected UI detailed contracts, scenario clauses, actual common shell/components and account/manage/check/raw-recording implementations, component/guest/live browser tests and preflight records. No code/test/build installation, Docker operation, repository edit, commit, push, login or API mutation by reviewer.
- Initial requested artifact search found no screenshots in Playwright/test-results/report paths. PM explicitly granted a brief isolated independent visual slot before final browser/performance execution. Existing ordinary `apps/mobile/dist` served at127.0.0.1:8090 only; Chromium from existing /tmp/otgd-playwright. All other browser request origins aborted. This is ordinary guest rendering, not standalone hosted-preview certification.
- Two owned browser scripts each exited0. Phone412x839 and desktop1440x1000 captured welcome/notice/home/context/profile error/light Settings/check overview/check review/dark Settings;20PNG total, screenshot hashes/visible text/scrollWidth in two observation manifests. `*-demo-confirmation.png` is a filename for the welcome/Explore transition, not evidence of a modal. ScrollView clips to the current viewport, so these are viewport-state captures despite screenshot fullPage option. No saved result or destructive modal was executed.
- Inspected screenshots directly via view_image: phone Home/profile error/light Settings/check Review/welcome-Explore, desktop Home/dark Settings. Remaining images retained for peer inspection. Observed consistent typographic hierarchy, restrained card grouping, selected navigation state, inline actionable age error and persistent synthetic/memory-only notices at the tested sizes. This supports those pictured states only.
- Own server pid110523 stopped after browser close; recorded port8090 connection refusal111. Read-only gate execution slot released to PM. No services/tests run during the final gate window.
- Contrast calculation against exact source tokens: white-on-dark-danger1.6598:1; light danger6.7718:1. Existing functional e2e asserts theme changes/target dimensions/overflow but has no contrasting-danger assertion. These calculations are source inspection, not native/physical color measurement.
- Existing preflight live summary reports two viewport journeys with fictional ZIPs and receipt hashes. It explicitly predates final frozen aggregate and is not current final acceptance. PM reports exact-source CI merge891e5e7 tree9a62a8ae6bffd16394f68ea9147b8d7c5469f169 matches candidate tree and original Fargate/iOSnative/Androidpreview now passed; this report has not independently inspected those final raw artifacts and does not convert that message into gate PASS.

## Required corrections

### UI-001 — P2 — AND-SET-006; shared destructive-control presentation
Path: `apps/mobile/src/ui/components.tsx:215-244 and apps/mobile/src/ui/theme.tsx:4`.
Observed evidence: Button danger background c.danger uses dark #FFB6BA while foreground c.white is #FFFFFF at fontSize15; relative luminance contrast calculation yields1.6598:1. Light counterpart6.7718:1. No rendered dark danger screenshot claimed.
Impact: Destructive action labels are difficult to read in dark mode and fail4.5:1 normal-text minimum before privacy/withdrawal/discard actions.
Required correction: Provide theme-appropriate destructive foreground/background pairing meeting4.5:1 for normal button text in all supported states.
Verification: Compute from effective tokens and inspect/render dark destructive confirmation before confirmation; show label contrast>=4.5:1 and accessible Cancel. Preserve behavior and scopes.

### UI-002 — P2 — AND-SET-002/006 and AND-ONB-006 reduced motion
Path: `apps/mobile/src/ui/manage.tsx:690; apps/mobile/src/ui/components.tsx:624; apps/mobile/src/core/domain.ts:254`.
Observed evidence: rg of App.tsx and src shows reducedMotion only in Settings read/write, type and defaultfalse; no presentation consumer or OS reduced-motion listener. Shared Confirmation uses animationType=fade unconditionally.
Impact: Reduce motion preference is presented as functional but does not affect existing ordinary modal animation and does not follow system preference by default.
Required correction: Resolve effective system/user motion preference and consume it in decorative ordinary UI animation, including shared Confirmation. Preserve approved native task stimulus timing/geometry.
Verification: Exercise system reduced motion and explicit Reduce motion on/off; inspect effective rendered Modal animation and preference persistence; keep fixed acquisition configuration unchanged.

## Decision synchronization

| Decision | ACK | Impact/disposition |
|---|---|---|
| D-001 v1 | AFFECTED | Software-only scope, fictional provenance and no medical/drive/participant authority. |
| D-002 v1 | NOT_AFFECTED | Parent supervision and recovery scheduling not owned by reviewer. |
| D-003 v1 | AFFECTED | Only preserved fictional local evidence; no real participants. |
| D-004 v1 | AFFECTED | Interpret approved software/current conditional research claims consistently. |
| D-005 v1 | NOT_AFFECTED | Read-only review; no Docker/runtime/data mutation. |
| D-006 v5 | AFFECTED | ImageD/current-source execution needed; no original/cloud provenance claim. |
| D-007 v1 | AFFECTED | Auth preflight invalidated by repair; final frozen source evidence mandatory. |
| D-008 v1 | AFFECTED | All-source freeze; own outputs outside repo; approved isolated visual slot only. |

ACKs were sent through actual native PM messaging. D-006v5 supersedes prior image methods; prior histories are not carried as current runtime proof. PM visual-slot permission was a bounded exception to D-008 test/service exclusion, and is now closed.

## Per-spec initial decisions

| Spec | Current canonical SHA-256 | UI decision | Evidence / remaining requirement |
|---|---|---|
| OTGD-001 | `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7` | CHANGES_REQUIRED | Global APP-014 accessibility and ordinary UI acceptance inherit UI-001/UI-002; remaining chemistry, native and scientific qualification remain separate. |
| OTGD-002 | `c8e2d63aad6f7f973a181d917ef645e8d32b012ca41df1f2abd7d7a0b7525fe4` | BLOCKED | Dashboard scope/source labels inspected; guest Home rendered at both viewports. Authenticated conditional research dashboard not rendered; exact-source final browser evidence pending. |
| OTGD-003 | `c171a3fd1d7705d710dd172ebe5d59046cc0023a2ddfedaf162092008703e648` | BLOCKED | Guided check and ResultScreen separate local save/delivery/research scope in source. Guest review rendered; admitted research and refusal states not rendered. |
| OTGD-004 | `b29801322e8700aa11edce8289d84290485834005cba2fa80ee5695dd3d248ce` | BLOCKED | History source and scalar formatters inspected; conditional historical research presentation not rendered and final browser evidence pending. |
| OTGD-005 | `1b82b7101ffe6bf0538ffe24b814aea01369f322c9bb8e96808e05f0dd70e369` | BLOCKED | Welcome, notice and Home observed; research admission after onboarding not exercised in this bounded guest slot. |
| OTGD-006 | `e5c8877a4b483fb47aa30fb9811536166d10764d83d15eaef950e0727dc93a8f` | BLOCKED | ResultScreen displays conditional 1.1 endpoint/population/time and refusal copy in source. Live admission/refusal evidence not independently executed here. |
| OTGD-007 | `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6` | BLOCKED | About/capability route has current-scope wording in source. Account current authority state not rendered in guest slot. |
| OTGD-008 | `1307ac2ebe390b58619b599669a9c52773104dded84661be708aa132d95f8626` | BLOCKED | Offline evaluation artifact/tool specification has no dedicated application visual surface. Numeric report/denominator evidence belongs to evaluation and engineering; current gate bundle not yet supplied. |
| OTGD-009 | `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a` | BLOCKED | ResearchResult renderer preserves named endpoint/time and conditional probability in source. Exact admitted/abstention/denial fixtures not rendered here. |
| OTGD-010 | `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993` | CHANGES_REQUIRED | Raw export exact-scope confirmations use shared Confirmation. UI-002 prevents truthful reduced-motion behavior; current complete raw export rendered-state evidence remains pending. |
| OTGD-011 | `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2` | BLOCKED | Operator lifecycle is primarily CLI/API; capability screen must distinguish software/authority/availability. Current operator and resulting capability evidence pending; no operator approval invented. |
| OTGD-012 | `1e25c5f543b73c2df18741240a266b39716ae17c31bc8b57e2bd91dc699a29c4` | BLOCKED | Eye UI distinguishes positioning/measurement and timing/scale source in code. No camera/native stimulus or qualified optical behavior executed in this guest-only slot. |
| OTGD-013 | `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29` | BLOCKED | Reader verification/physical source spec has no new standalone visual design. UI truth depends on signed-reader states and refusal evidence not exercised here. |
| OTGD-014 | `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855` | BLOCKED | Cloud browser delivery has no new local visual layout; ordinary guest rendering does not verify hosted routing/headers or immutable public bytes. Deployment prohibited. |
| OTGD-015 | `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6` | BLOCKED | Release orchestration is primarily CLI/receipts; local screenshots do not verify QA/production activation or hosted authority. Deployment prohibited. |
| OTGD-016 | `430fe7dfbfdb117add502c5632150690905d94b3dcb42ddc892bf1e8943f273c` | BLOCKED | Recovery approval is API/registry authority; no distinct visual surface claimed. Current suspended/reapproved refusal states not rendered. |
| OTGD-017 | `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d` | BLOCKED | Standalone fictional hosted-mode banner/config differs from ordinary dist observed here. This slot did not establish hosted-preview build isolation or deny-path coverage. |
| OTGD-018 | `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218` | CHANGES_REQUIRED | Raw-recording revoke/remove sheets use danger Confirmation, so UI-001/UI-002 apply; source distinguishes retained bytes/pending cleanup and confirmed deletion. |
| OTGD-019 | `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a` | BLOCKED | Alcohol screen/source preserves separate mg/L and qualifiers and qualification refusal. No alcohol hardware or calibrated measurement observed; final component evidence pending. |
| OTGD-020 | `7cd3451fd8c13cd25bdc66403e879de3f9fe0e127e3655f2ed40017869916f76` | BLOCKED | Environment and memory-only strip observed. Startup/protected-store/native recovery states need current gate evidence; ordinary guest export is not native qualification. |
| OTGD-021 | `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e` | BLOCKED | Home rendered with named source/current reader-unavailable state and separate workspace counts. Native focus/200% text and account/refresh/recovery matrix remain unexecuted in UI slot. |
| OTGD-022 | `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30` | CHANGES_REQUIRED | Export review uses shared Confirmation, so UI-002 applies; existing preflight ZIP receipts cover fictional structured data only and do not prove current raw export rendering. |
| OTGD-023 | `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4` | BLOCKED | Device route source preserves software-versus-qualification boundary. Native permissions/radio/connection/error recovery and physical pairing not executed in this guest slot. |
| OTGD-024 | `c75f24b4beeda893b780af0d924747c0cd7ca599ead627d3d265f21ec3772895` | BLOCKED | ECG source labels optional simulation, quality and electrical gates. No native waveform/contact-loss rendering executed; simulator/bench success would not qualify body-connected use. |
| OTGD-025 | `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8` | BLOCKED | Eye preview/camera denial/release source inspected. No permission request or native camera execution in this guest slot; separate native state evidence pending. |
| OTGD-026 | `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562` | CHANGES_REQUIRED | Guided draft discard uses danger Confirmation, so UI-001/UI-002 apply. Guest profile/review and explicit synthetic status rendered; result/local save was not executed by reviewer. |
| OTGD-027 | `e9288b9fbec177d7287962239555b7633a0cfbf80ecf3e1e350158da607f5139` | BLOCKED | PPG source/status/quality and cardiac provenance inspected. Current native acquiring/stale/contact/refusal/recovery views not rendered. |
| OTGD-028 | `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2` | BLOCKED | History grouped layout and source/delivery display inspected. Current state/qualifier/research/invalid, scroll return and large-text matrix not rendered here; see independent UX review for its row-summary finding. |
| OTGD-029 | `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9` | BLOCKED | Source keeps save and explicit upload separate; preflight receipts describe unknown acknowledgement reconciliation. Current frozen-source integration evidence pending; no encrypted persistence inferred from web. |
| OTGD-030 | `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee` | CHANGES_REQUIRED | Onboarding requires reduced-motion stop behavior (AND-ONB-006). UI-002 affects its shared confirmation/navigation surfaces; observed first-run copy truthfully disclaims impairment and separates notice. |
| OTGD-031 | `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f` | CHANGES_REQUIRED | Privacy destructive confirmation inherits UI-001/UI-002. Source preserves unsynced count warning, deletion pending and independently reachable Cancel; actual 200%/screen-reader/native sheets not exercised. |
| OTGD-032 | `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43` | CHANGES_REQUIRED | Profile validation focus/inline errors observed at phone and desktop. Unsaved-edit Confirmation inherits UI-002; native locale/keyboard/200% text evidence pending. |
| OTGD-033 | `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317` | BLOCKED | Instructions distinguish arrow/WAIT and unsupported screen-reader configuration in source. Native fixed stimulus geometry/timing and adaptive instruction acceptance not observed; do not modify capture stimulus to satisfy ordinary UI preference. |
| OTGD-034 | `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba` | BLOCKED | ResultScreen source separates result/delivery, null/missing qualifiers and research claim boundaries. Invalid/inconclusive/research/unsupported rendered matrix not observed in reviewer slot. |
| OTGD-035 | `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610` | BLOCKED | Saliva source preserves qualifier/basis/units and report lineage. Current six-qualifier/pending/invalid large-text rendering and true collection states not rendered. |
| OTGD-036 | `2768fdfbe5ff0b1971d6aad04101ea2fa17db6f6c3012848aa3aa3f490e654c8` | CHANGES_REQUIRED | Direct AND-SET-002/006 failures UI-001 (1.6598:1 dark danger text) and UI-002 (stored motion toggle not consumed; unconditional modal fade). Light/dark Settings screenshots otherwise show consistent hierarchy and truthful browser permission limitations. |
| OTGD-037 | `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd` | CHANGES_REQUIRED | Sign-out alternative removes local records using danger Confirmation; UI-001/UI-002 apply. D-007 repair/auth cancellation/same-account/revocation wording source and preflight inspected; exact-candidate final live evidence pending. |
| OTGD-038 | `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8` | CHANGES_REQUIRED | Withdrawal uses danger Confirmation, so UI-001/UI-002 apply. Source separates consent/notice/capabilities and empty research states; no real study or participant operation executed. |
| OTGD-039 | `238b3c329cd79edb4bd57807926311a3bed0c935cf77ef77577fcf79afda02ef` | BLOCKED | Participant instruction source/contract distinguishes declaration, authority, timing and actual source. Fresh rest guidance, interruption and authority-refusal rendered states not executed in guest slot. |
| OTGD-040 | `09cbf8dccec136a1ec7895fc553c62160b63fa1e2133f5b5864d7d3aed13547a` | BLOCKED | Collection source/contracts preserve pending analysis and independent staff import. Exact approved form/null reasons/abandonment/retry rendered matrix not executed in guest slot. |
| OTGD-041 | `f4bef2eee7577e8f57b7cd27b7463d3879dcb1d452c73540d8916f9d6bf41726` | BLOCKED | HR-only evaluation report variant has no dedicated app screen. Current report denominator/ablation execution evidence pending; no predictive performance asserted. |
| OTGD-042 | `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7` | BLOCKED | Server-interval authority is primarily backend evidence; cardiac UI/source must not imply measured physical timing. Current qualified/rejected disclosure matrix not rendered. |
| OTGD-043 | `c6f863bc71ebf167438fbe5cffe07b892da12cc066d0487d21403ff8dd49fa0d` | BLOCKED | Vendor driver availability is primarily firmware/backend; app must preserve actual adapter and unavailable/quality reason. No physical/vendor rendering or accuracy executed by reviewer. |
| OTGD-044 | `758f7dd11a72a15750d44a61d49d986b923232ac981fcb9ab304a56526e5bb6c` | BLOCKED | Header/private-route/signed-byte deltas have no standalone visual layout. Current delivery tests pending; local static server intentionally does not claim hosted header or private-origin verification. |
| OTGD-045 | `c62bb011c5e71f177ededaf19e710e2ec40a97618a5b427d144f97bcd67d7a26` | BLOCKED | DNS and bounded authority inputs are CLI/receipt behavior; no standalone UI. No DNS mutation/production delivery executed; current test/receipt evidence pending. |
| OTGD-046 | `1a331132cf6b66413d1705dc09d0c7f885b8fe1375ea72250dcd5a451162e241` | BLOCKED | Fixed-origin dist-preview is distinct from ordinary dist used in the approved guest slot. Local screenshots do not prove hosted reuse/private forwarding or launched preview; exact-preview gate pending. |
| OTGD-047 | `b5523be8de175f257dda911b52b94732ae4e5e838b49cd9c38bea7802d0670c4` | BLOCKED | Store workflow/status receipts have no dedicated customer visual screen. Reported CI native build success is not real-device signing/submission/public availability; no store action executed. |

## Coverage gaps and residual risk

Current exact-source aggregate and CI raw evidence, full result/qualifier/permission/loading/error/recovery rendered matrix, 200% text, keyboard/modal focus restoration, TalkBack/VoiceOver/Dynamic Type, OS permission round trips and real native/device geometry remain unverified by this review. Empty/unexecuted/stale evidence is not PASS. Screenshot scope is limited to the stated guest viewport states and existing ordinary web bytes; no credentialed screenshots/traces were created.

No earlier findings are declared resolved; initial independent review. The separate UX agent reported row-state and destination-focus concerns; those remain its independently owned findings and are not substituted for this UI review. Reported source/system defects need a consolidated authorized correction round and affected current-source reverification/review.

Specification readiness: no final council judgment here. Implementation UI readiness: CHANGES_REQUIRED. Application verification: blocked by open findings/current evidence prerequisites. Release/external action: not assessed or authorized; no merge, deployment, store submission, participant use, scientific/hardware/native qualification implied.

Remaining blocker action: obtain final frozen-candidate gate artifacts and affected rendered/native evidence from PM/verification owner, then re-review after any authorized repair. Target:47 current canonical dossiers and shared UI. Reason: current acceptance evidence incomplete and UI001/002 open. Status: pending, not denied; no uncertain external action by reviewer.
