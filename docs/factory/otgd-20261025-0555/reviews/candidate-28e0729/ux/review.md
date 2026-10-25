# UX council review — otgd-20261025-0555

Role: UX reviewer. Identity: `/root/review_ux`; fresh independent context, no authored implementation/spec artifacts. OpenAI configured `gpt-6.1-sol/high`, explicit parent dispatch with `fork:none`; PM confirmed this by direct message. Effective runtime model attestation is not separately exposed, so no stronger claim is made.

Candidate `28e07295cb37bb9dcaaac82cc8fc846eb89006a6`; baseline `0844868aa543af4ab75ac5065ad48cf807b86bb3`; SHA-256 frozen working-tree manifest `36ed8d800edcb560ac8ca189e98b64518b3342a29458d6e91a8d943085310f8c`. Factory pinned `4770878e18e9c587c2961b9e2bb13315da31abe9`. Review stage IMPLEMENTATION. Canonical hashes freshly recomputed: **47/47 match inventory**; **1,014 frozen manifest entries unchanged** on read-only recheck. Old council header hashes are not used as current bindings.

**Verdict: CHANGES_REQUIRED.** Seven per-spec decisions require source corrections; forty are BLOCKED on current acceptance evidence. No per-spec PASS. Current gates and native evidence remain independent blockers even for specs with source findings. This is a UX specialist judgment, not final council/engineering/product/scientific approval.

## Findings

### UX-001 — MEDIUM — Home and local history erase saved result scope and state

Affected: OTGD-001, OTGD-002, OTGD-004, OTGD-021, OTGD-028, OTGD-034.

CheckRow derives its frozen-row detail solely from check.frozen: every frozen record says Measurements only. Its ordinary measurement-kind badge likewise always says Measurement record. The component is reused for Home and local History, including fully verified 1.1.0 research_estimate/inconclusive records that ResultScreen deliberately supports, plus invalid/inconclusive legacy records. Home online availability also says Measurement-only release without consulting admitted scope. Thus the shared summary disagrees with the retained result and may disagree with the detail the user opens. This is source-established branching behavior, not a newly executed browser reproduction.

Impact: Customers cannot reliably identify an admitted historical research result or an invalid/inconclusive record from the saved row; capability text conceals the conditional research reader after D004 reconciliation.

Correction: Derive a concise result-state/scope label from already verified result data and current admitted capability, keep capture and synchronization states independent, preserve historical dates and fictional provenance, and keep legacy/unadmitted research closed. Do not infer approval from a local flag.

Verification: Rendered Home/History tests using actual verified result admission cover measurement_only, invalid, inconclusive, admitted research_estimate and admitted research abstention; rows and opened details agree, synthetic provenance remains visible, and unadmitted/legacy estimates never gain a score.

Evidence: `apps/mobile/src/ui/account.tsx:555`; `apps/mobile/src/ui/account.tsx:575`; `apps/mobile/src/ui/account.tsx:592`; `apps/mobile/src/ui/account.tsx:546`; `apps/mobile/src/ui/manage.tsx:359`; `apps/mobile/src/ui/checks.tsx:1550`.

### UX-002 — MEDIUM — Custom route changes announce the destination but do not move accessibility focus

Affected: OTGD-001, OTGD-021, OTGD-036.

Page navigation effect calls announceForAccessibility(title) and resets scroll restoration. Title renders a Text heading without a forwarded ref; neither Page nor custom tab routing supplies destination focus. A source search across App.tsx/src found no setAccessibilityFocus/findNodeHandle or equivalent route-heading handoff. The only explicit focus is profile validation. Announcing a title is distinct from relocating the screen reader cursor required by AND-DASH-007. No actual TalkBack/VoiceOver behavior is claimed.

Impact: Assistive-technology users can stay at persistent tab controls or lose their reading position instead of arriving at the destination heading. This affects orientation and task completion in the custom navigation shell.

Correction: Implement a lifecycle-safe destination-heading accessibility focus handoff for ordinary route transitions, preserving privacy cover/modal/native acquisition behavior, and restore appropriate trigger focus after dismissal/cancellation.

Verification: Demonstrate Home/Settings/History and deeper Back navigation with TalkBack and VoiceOver, including large text, browser auth cancellation and modal close; focus reaches the destination heading or restored trigger without reading hidden background content. Keep timed capture adaptation separate.

Evidence: `apps/mobile/src/ui/components.tsx:541`; `apps/mobile/src/ui/components.tsx:560`; `apps/mobile/src/ui/components.tsx:590`; `apps/mobile/App.tsx:227`.

### UX-E01 — BLOCKER — Frozen aggregate and per-criterion current verification pending

Affected: OTGD-001, OTGD-002, OTGD-003, OTGD-004, OTGD-005, OTGD-006, OTGD-007, OTGD-008, OTGD-009, OTGD-010, OTGD-011, OTGD-012, OTGD-013, OTGD-014, OTGD-015, OTGD-016, OTGD-017, OTGD-018, OTGD-019, OTGD-020, OTGD-021, OTGD-022, OTGD-023, OTGD-024, OTGD-025, OTGD-026, OTGD-027, OTGD-028, OTGD-029, OTGD-030, OTGD-031, OTGD-032, OTGD-033, OTGD-034, OTGD-035, OTGD-036, OTGD-037, OTGD-038, OTGD-039, OTGD-040, OTGD-041, OTGD-042, OTGD-043, OTGD-044, OTGD-045, OTGD-046, OTGD-047.

At review, dossiers record final-candidate acceptance NOT_RUN and final gates are PM-owned/in progress. Prior browser/author preflights have explicit candidate/evidence limitations. No current aggregate or criterion-by-criterion closure was supplied to this reviewer.

Impact: Required acceptance evidence is unavailable; completion cannot be inferred.

Correction: Admit completed unchanged-source gate artifacts, correct per-criterion results with exact bindings, and request focused reaffirmation; do not replace pending evidence with PASS.

Verification: Every applicable mandatory check has actual passing current-candidate evidence; skipped mandatory checks fail; coverage strictly greater than80%; scope and retained failure history remain explicit.

Evidence: `docs/factory/otgd-20261025-0555/specs/*/test-results.md`; `/workspace/scratch/otgd-20261025-0555-live/status.md`.

### UX-E02 — BLOCKER — Android and iOS end-to-end OS evidence is absent

Affected: OTGD-001, OTGD-012, OTGD-013, OTGD-018, OTGD-020, OTGD-021, OTGD-022, OTGD-023, OTGD-024, OTGD-025, OTGD-026, OTGD-027, OTGD-028, OTGD-029, OTGD-030, OTGD-031, OTGD-032, OTGD-033, OTGD-034, OTGD-035, OTGD-036, OTGD-037, OTGD-038, OTGD-039, OTGD-040, OTGD-043, OTGD-047.

Reports explicitly retain real Android/iOS permission dialogs and Settings return, SQLCipher/OS unlock/key loss/process death, native cancellation/focus/background/timing, Bluetooth/disconnect and native share cleanup as unexecuted. Browser memory-only reload, mocked native status components and source inspection cannot establish these journeys.

Impact: Required acceptance evidence is unavailable; completion cannot be inferred.

Correction: Execute the applicable installed Android and iOS journey matrix, including denial/restriction/cancel/offline/background/restart paths and assistive technologies, before implementation acceptance. Keep hardware/scientific qualification separate.

Verification: Current native artifact/build/OS bindings plus observed task completion/recovery and accessible parity evidence for each applicable criterion; do not claim participant or physical sensing qualification.

Evidence: `apps/mobile/VERIFICATION.md`; `apps/mobile/modules/VERIFICATION.md`; `apps/mobile/e2e/README.md`; `docs/factory/otgd-20261025-0555/reports/mobile-implementation.md`.

## Journey assessment and observed strengths

The existing local live browser record covers actual issuer PKCE, separate notice/profile/context, synthetic measurement-only save and deliberate upload, lost finalization acknowledgment replay, queued results/exports, downloaded ZIP checks, memory-only reload plus reauthentication/history, foreign-owner refusal, separate study consent/withdrawal and denied restart, lost deletion acknowledgment with pending intent, retired generation denial, and logout/refresh-family revocation. It ran Chromium at 412×839 and 1440×1000. It is a preflight record, not a fresh run by this reviewer or a substitute for the frozen aggregate. Both retained ZIP archives were independently opened read-only; selected IDs, synthetic mode, measurement-only/null probability, member sizes and SHA-256 match their manifests. Mobile archive SHA-256 `b88a6b164c5fdcfd3476c7284dbfcb7a32c365be981744b515dc7c4d930fc8a0`; desktop `83111f88049a154faf2dbac4bdfe1fa9758f5e68cb4f7181c11d303c6cc1fd44`.

Source inspection finds separate local clear/cloud data deletion/account deletion controls, count-specific extra unsynced confirmation, pending privacy receipts, explicit generation reset, deliberate exact export scope and raw-copy purpose, default-off retries, independent study and optional raw choices. Native storage refuses missing SQLCipher/OS secure storage; locked recovery explicitly warns about unsynced loss. These are source observations, not OS execution evidence.

Guided check shows frozen context, individual stages, explicit provenance, unavailable native reaction capture in browser, local save before account upload, immutable replacement lineage and separate delayed lab projections. Participant preparation distinguishes declarations from electrical proof, preserves unavailable human ECG and guides monotonic rest. Optical copy withholds unmeasured onset/scale; alcohol stays separate mg/L with calibrated hardware unavailable, no BAC conversion or driving clearance. These inspected branches do not establish physical or scientific qualification.

Six raw guest screenshots captured by the UI reviewer were visually inspected here: phone Home, profile validation error, check Review and dark Settings, plus desktop check Context and profile error. Sources are in artifact-manifest.json with SHA-256 and viewport provenance in the UI observation JSON. At these viewports the inspected states show legible source notices, selected controls, clear validation text and navigation; no OS, 200% text, screen reader or saved-result visual acceptance is inferred. No actual browser/service/test was launched by this reviewer.

## Per-spec decisions

Every row binds to the candidate and source/artifact manifests above. Full clause IDs, paths, evidence and blocker mappings are in review.json. BLOCKED means no additional UX source defect was established in that slice and required current evidence remains unavailable; it does not mean that the spec passed another review.

| Spec | Current canonical SHA-256 | Decision | UX scope / finding |
|---|---|---|---|
| OTGD-001 | `c8f052979fd2a15da2d0bc09c8533bde246cdc559d798696af728378cf5850f7` | CHANGES_REQUIRED | Full normative register: measurement default, source/claims, one-collection/one-task lineage, optional profile, alcohol separation, privacy and recovery; applied current amendment precedence. UX-001; UX-002; UX-E01; UX-E02 |
| OTGD-002 | `c8e2d63aad6f7f973a181d917ef645e8d32b012ca41df1f2abd7d7a0b7525fe4` | CHANGES_REQUIRED | Dashboard admitted scope and fictional provenance. UX-001; UX-E01 |
| OTGD-003 | `c171a3fd1d7705d710dd172ebe5d59046cc0023a2ddfedaf162092008703e648` | BLOCKED | Save before upload, historical research navigation and missingness. UX-E01 |
| OTGD-004 | `b29801322e8700aa11edce8289d84290485834005cba2fa80ee5695dd3d248ce` | CHANGES_REQUIRED | Historical state, qualifier, time and admitted research scope. UX-001; UX-E01 |
| OTGD-005 | `1b82b7101ffe6bf0538ffe24b814aea01369f322c9bb8e96808e05f0dd70e369` | BLOCKED | Guest versus research onboarding and independent notice. UX-E01 |
| OTGD-006 | `e5c8877a4b483fb47aa30fb9811536166d10764d83d15eaef950e0727dc93a8f` | BLOCKED | Verified research presentation versus ordinary null scores. UX-E01 |
| OTGD-007 | `8dc5faf4274edf798f4828bacff599c2c34c5aa6f5cb594481f2ca365ef401f6` | BLOCKED | Environment and account capability presentation. UX-E01 |
| OTGD-008 | `1307ac2ebe390b58619b599669a9c52773104dded84661be708aa132d95f8626` | BLOCKED | Research evaluation reports: genuine calculation versus externally unverified authority; no scientific claim adopted. UX-E01 |
| OTGD-009 | `a110df0160cb1dfa6b1eb471ebe558eec1af8bcb86c7c883b8795bac2fdf714a` | BLOCKED | Research admission, abstention and authenticated historical endpoint display. UX-E01 |
| OTGD-010 | `6e7ff5b60880e7234eec431ccb702b3e452b6a1d6e76a01720cb60b478782993` | BLOCKED | Separate exact raw-export purpose, notice, selected IDs, retention and share-copy limits. UX-E01 |
| OTGD-011 | `a7bb7170b6fc7c119e8e93eae9783767876a8f861a71588027577172c30a80e2` | BLOCKED | Operator reviewability, independent principals, rollback default and truthful capabilities. UX-E01 |
| OTGD-012 | `1e25c5f543b73c2df18741240a266b39716ae17c31bc8b57e2bd91dc699a29c4` | BLOCKED | Conditional optical start, passive preview distinction, privacy stop and ROI opt-in. UX-E01; UX-E02 |
| OTGD-013 | `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29` | BLOCKED | Signed reader identity/trust distinction, encrypted BLE and independent transport stop. UX-E01; UX-E02 |
| OTGD-014 | `735f76493e8188925c157347dc22b0a2acad4cb76721f2ea8a7f324629631855` | BLOCKED | Browser customer access, exact origins, navigation and honest release status. UX-E01 |
| OTGD-015 | `32e918e2908b70dbf00f7c9533aa462402b71ffc5c5ce9b8f4da499783cc3bc6` | BLOCKED | Cloud operator plan/apply, bounded recovery receipts and independent admission. UX-E01 |
| OTGD-016 | `430fe7dfbfdb117add502c5632150690905d94b3dcb42ddc892bf1e8943f273c` | BLOCKED | Recovery fail-closed boundaries and retained deletion barriers. UX-E01 |
| OTGD-017 | `ee9d68e204d40b0500732c19096ce4fc4a362892d09106034678baacde4e961d` | BLOCKED | Isolated fictional preview, no account/acquisition services and honest persistence. UX-E01 |
| OTGD-018 | `a688ab279a337ce745968e41c3d834c1afa8486a45901544cd7f779df2d54218` | BLOCKED | Raw recording/upload separation, exact notice, local stop and independent cleanup status. UX-E01; UX-E02 |
| OTGD-019 | `6c423c75ae449e935fe8856f61d70af07aaab582719baba1d1e1bc63d787f45a` | BLOCKED | Separate unavailable breath channel, mg/L/censoring, time, fictional data and no combined clearance. UX-E01 |
| OTGD-020 | `7cd3451fd8c13cd25bdc66403e879de3f9fe0e127e3655f2ed40017869916f76` | BLOCKED | Fixed environments, bounded startup/recovery and truthful verification status. UX-E01; UX-E02 |
| OTGD-021 | `c756e1eb65e8b3e9929a58c4c191e7c179529f8cd238da6e9cd6b5403439105e` | CHANGES_REQUIRED | Home start/resume, device readiness, workspace races and accessible navigation. UX-001; UX-002; UX-E01; UX-E02 |
| OTGD-022 | `2e02ae2e4ea75c4e789b29399dee2b6e4206f12ecb81630b04ca54c4a6e1ef30` | BLOCKED | Deliberate export source/scope and explicit sharing, expiry and cleanup. UX-E01; UX-E02 |
| OTGD-023 | `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4` | BLOCKED | BLE discovery/permission/radio denial, association, verified binding, disconnect/forget recovery. UX-E01; UX-E02 |
| OTGD-024 | `c75f24b4beeda893b780af0d924747c0cd7ca599ead627d3d265f21ec3772895` | BLOCKED | Optional ECG and declared versus actual electrical state; unavailable human ECG remains explicit. UX-E01; UX-E02 |
| OTGD-025 | `bfb351373c6c3c2d33fd74fa1537ed0c610aa65624e5ce0e8c07fa8f5d1a6cf8` | BLOCKED | Camera preview/permission/lifecycle and conditional optical units/timing. UX-E01; UX-E02 |
| OTGD-026 | `cef15148de295ecabe3b38d6f9b2d45530b60993c1aacf1b41e1b4fc495c6562` | BLOCKED | Frozen context, eight-stage guided check, retained attempts, cancel/save/upload and parity. UX-E01; UX-E02 |
| OTGD-027 | `e9288b9fbec177d7287962239555b7633a0cfbf80ecf3e1e350158da607f5139` | BLOCKED | Pulse source/quality/contact/stale state and independent acquisition timing. UX-E01; UX-E02 |
| OTGD-028 | `eb9f89e04620ed296b248ce076e2c5447df6c5fb2c9da0eb9fa90725f2bd99a2` | CHANGES_REQUIRED | Local/remote history, exact selection, immutable lineage and faithful states. UX-001; UX-E01; UX-E02 |
| OTGD-029 | `388f00c1fab3eb1f905e140b7248ce8e737ae87349eb8a508068becbb51456b9` | BLOCKED | Local-first storage, explicit queueing, lost acknowledgment replay and account generation. UX-E01; UX-E02 |
| OTGD-030 | `da9837761a2034853336456f15dc249daf23aed73a9808bbdf4b1b690eda53ee` | BLOCKED | First-run explicit guest/account entry, versioned notice and no permission prompt on entry. UX-E01; UX-E02 |
| OTGD-031 | `993e7c0f65b5ee4bd9b2f470e2d4111f6329f083e7650a76ab71f78abf5e9f3f` | BLOCKED | Separate local clear/cloud deletion/account deletion, extra unsynced confirmation and durable pending intent. UX-E01; UX-E02 |
| OTGD-032 | `b90bbf657f3c8e8a24eab7ab93f04c680018bbe2179131c1b8aa70c6d3d67a43` | BLOCKED | Optional profile, unit conversion, first-error focus, drafts/conflicts and frozen context. UX-E01; UX-E02 |
| OTGD-033 | `1c5bfceae8b4e2b5e1bd8c9edd7f19fd73908cde1fb804af4e9530700d3ea317` | BLOCKED | Native reaction instructions, practice/scored split, unavailable browser capture and interruption/retry semantics. UX-E01; UX-E02 |
| OTGD-034 | `dadd53ea7fd8027bb76d17c26e51d4910cc3c8763bfd8a838434fbf8112397ba` | CHANGES_REQUIRED | Measurement/research/invalid/inconclusive states, missingness, historical time and separate delivery state. UX-001; UX-E01; UX-E02 |
| OTGD-035 | `6edc6d7603b66733858b1f7fe42dc93d22712dd8cadbac29121a65f2ffd23610` | BLOCKED | One saliva collection, quantity/qualifier/units, original report and delayed lab status. UX-E01; UX-E02 |
| OTGD-036 | `2768fdfbe5ff0b1971d6aad04101ea2fa17db6f6c3012848aa3aa3f490e654c8` | CHANGES_REQUIRED | Functional settings, no-prompt permission status/recovery, diagnostics, appearance and accessibility. UX-002; UX-E01; UX-E02 |
| OTGD-037 | `b20292aa0a4f47fa00fa5e652eafd1dffdd75e2a710ac2b0165f5f2ae4e2a1bd` | BLOCKED | PKCE browser sign-in, cancel/unlock/account isolation, explicit logout and remote-revocation uncertainty. UX-E01; UX-E02 |
| OTGD-038 | `e0c8f1f81be37cbe775f274e6c2aa81d3f3eacc64da92f01bcdd1c31adfb9ee8` | BLOCKED | Exact consent and invitation, withdrawal, fresh capture admission and truthful study absence. UX-E01; UX-E02 |
| OTGD-039 | `238b3c329cd79edb4bd57807926311a3bed0c935cf77ef77577fcf79afda02ef` | BLOCKED | Exact approved participant instructions, declaration boundaries, fresh acknowledgment and monotonic rest. UX-E01; UX-E02 |
| OTGD-040 | `09cbf8dccec136a1ec7895fc553c62160b63fa1e2133f5b5864d7d3aed13547a` | BLOCKED | Governed lab collection, specimen lineage, pending analysis and independent staff import. UX-E01; UX-E02 |
| OTGD-041 | `f4bef2eee7577e8f57b7cd27b7463d3879dcb1d452c73540d8916f9d6bf41726` | BLOCKED | Prespecified matched evaluation / HR variant and truthful absent comparisons. UX-E01 |
| OTGD-042 | `277f1727d50ffc6c0ee8717d1c77541bca64139ea78ffe032795ebf8a0c2b0a7` | BLOCKED | Restricted cardiac timing authority and historical qualification limits. UX-E01 |
| OTGD-043 | `c6f863bc71ebf167438fbe5cffe07b892da12cc066d0487d21403ff8dd49fa0d` | BLOCKED | Selected vendor source/quality/freshness and software versus physical qualification. UX-E01; UX-E02 |
| OTGD-044 | `758f7dd11a72a15750d44a61d49d986b923232ac981fcb9ab304a56526e5bb6c` | BLOCKED | Private route/security header verification and bounded byte receipts. UX-E01 |
| OTGD-045 | `c62bb011c5e71f177ededaf19e710e2ec40a97618a5b427d144f97bcd67d7a26` | BLOCKED | Exact CNAME preview/atomic create/no-op and bounded operator inputs. UX-E01 |
| OTGD-046 | `1a331132cf6b66413d1705dc09d0c7f885b8fe1375ea72250dcd5a451162e241` | BLOCKED | Fictional browser preview manifest, verified readiness and hosting boundaries. UX-E01 |
| OTGD-047 | `b5523be8de175f257dda911b52b94732ae4e5e838b49cd9c38bea7802d0670c4` | BLOCKED | Store plan/build/submit/status, genuine signed artifact, uncertain submission and encrypted handoffs. UX-E01; UX-E02 |

## Decision acknowledgments and completion limits

- **D-001 v1:** AFFECTED: all47 approved scope, default measurement/fictional/research/alcohol limits and two correction rounds.
- **D-002 v1:** NOT_AFFECTED: parent owns saved supervision; recovery0 retained, no duplicate automation.
- **D-003 v1:** AFFECTED: existing fictional local browser evidence only; no older or participant runtime.
- **D-004 v1:** AFFECTED: full approved journeys and later research precedence applied; no global no-model assumption.
- **D-005 v1:** NOT_AFFECTED: review read-only; no cleanup/runtime mutation.
- **D-006 v5:** AFFECTED: accept disclosed reconstructed local software runtime only; final source and mandatory gates still required, no original/cloud digest claim.
- **D-007 v1:** AFFECTED: current repaired auth/issuer source reviewed; earlier changed-source preflight not final PASS.
- **D-008 v1:** AFFECTED: freeze respected, scratch-only writes; no tests/services/browser by this reviewer; inspect existing artifacts only.

Exact acknowledgments were sent to PM by native collaboration messaging before evidence-dependent signoff. D006v1–v4 are superseded by current v5 for this review; no stale acknowledgment is substituted. Current source manifest and artifact hashes permit later revalidation without altering historical records. Correction round0/2 and recovery0 remain unchanged.

Prior findings: First independent UX report for this candidate; no carried-forward specialist PASS. Author reports record repaired permission race and OAuth/CSP/logout defects; these are preflight evidence with explicit limits, not independent resolution of UX001/002.

Remaining blockers: Final current-source gates and criterion records pending; actual Android/iOS device/AT/native journeys unavailable. No action denied; no approval escalation attempted. No tests/services launched because PM source-freeze/concurrency instruction prohibits them.

No repository edits, installations, Docker operations, commits, pushes, merge, deployment, paid services or participant actions were performed. Frozen acceptance stays pending until PM supplies current results; focused follow-up can update evidence judgments, while UX001/002 require actual correction and affected revalidation.
