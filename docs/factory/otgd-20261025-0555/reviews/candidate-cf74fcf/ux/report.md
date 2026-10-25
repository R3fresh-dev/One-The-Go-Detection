# Independent UX replacement review — provisional

Verdict **CHANGES_REQUIRED** for candidate `cf74fcff6ad19e639538d260f223ec18d618658d`, IMPLEMENTATION scope. Four direct per-spec source corrections and 43 BLOCKED dispositions; no PASS. This is an independent UX judgment, not product/engineering/scientific approval or global app completion. Final evidence update is required when current gates and exact-case replacement reconciliation are supplied.

Reviewer `/root/replacement_ux`; fresh independent context, no implementation or specification authorship. Configured OpenAI `gpt-6.1-sol/high` confirmed by PM's direct dispatch attestation (`fork_turns:none`). Independent runtime-model query unavailable. Source and test reads, archive inspection and report generation only; no source writes, tests, browser/runtime probes, Docker mutation or additional agents. Factory pin `4770878e18e9c587c2961b9e2bb13315da31abe9`; correction1/2, recovery0/3 unchanged.

Actual HEAD matches candidate; independently recomputed SHA-256 matches all47 canonical specs. Source fingerprint supplied by candidate binding is `d8b9455b68905dc6da7384a0ab85adb8644dc5d5c2e96c7f3bd1b69c2d08582a`. `source-manifest.json` binds canonical paths/hashes and the inspected source/assertions. `evidence-manifest.json` records hashes of actual inspected logs/receipts/archives, and explicitly distinguishes correction preflights from current-gate evidence. All47 historical case audit files are individually hash-bound in `per-spec-decisions.json`; historical status is never promoted to replacement acceptance.

Actual decision ACK sent PM: D001 AFFECTED (software scope and claims), D002 NOT_AFFECTED (supervision), D003 AFFECTED (fictional runtime evidence), D004 AFFECTED (authorized1.1/legacy precedence), D005 AFFECTED (preserve retained state), D006v9 NOT_AFFECTED to UX operations (no image/cache actions), D007 AFFECTED (browser/auth recovery), D008v2 AFFECTED (freeze/current gates), D009v11 AFFECTED (individual corrections/current HR admission). No unresolved policy clarification.

## UX-R001 — P2 — Home misreports a successfully connected signed reader

Direct requirements: OTGD-001 HW003/APP001; OTGD-002 AND-DASH001; OTGD-021 AND-DASH004 (case `OTGD-021-AND-DASH-004-01`); OTGD-039 PAI007 (related current presentation cases `OTGD-039-PAI-007-01/02`). This is one source defect with linked impacts, not several independent bugs.

`apps/mobile/src/device/controller.ts:249–277` creates the physical `prototype_sensor` association and publishes `state:connected_reader, reason:null` after successful hello. Its update at155–167 preserves real observation time and independently reflects installed binding. `core/devicePresentation.ts:107–168` handles a valid simulator, scanning, connecting, reason codes and idle; it has **no connected_reader branch**. Thus every healthy signed-reader snapshot falls through at161 to `connected:false`, “Reader connection unavailable” and “A current supported handshake could not be verified … reconnect.”

`ui/device-summary.tsx:29–47` renders this false Home state and fixed all-channel qualified-unavailable text. Its connected badge is also hardcoded “Synthetic only,” so merely adding a connected-reader helper branch would still falsely label the physical connection synthetic. `device/DevicePanel.tsx:30` correctly distinguishes signed-protocol connection from service-verified binding, so Home contradicts the actual Device screen. Current `tests/device-presentation.test.ts` tests idle/errors/scanning/connecting/invalid simulator but never a connected_reader snapshot.

Reproduction is deterministic read-only branch tracing, **not a newly executed runtime test**: use the actual controller's healthy physical snapshot with current association/reason:null, with either absent or installed verifiedBindingId; every handled state comparison fails and fallback161 is selected. The visible Home effect follows directly from the JSX.

Impact: a connected user receives false reconnect guidance; the Home summary conceals supported conditional acquisition. Fix must keep connection, service binding and independent channel qualification separate. Add truthful signed-reader presentation and capability-qualified availability wording; binding alone must never grant human capture or research. Required verification: actual helper/Home assertions for unbound reader, service-bound reader, active/denied/expired channel authority, disconnect/boot replacement and Device/Home agreement; no physical reader may say “Synthetic only.” No participant authority is assumed by this finding.

## Initial findings and correction review

- **UX-001:** source correction confirmed, final combined-source execution pending. `core/resultPresentation.ts` now verifies result before deriving labels; CheckRow at `ui/account.tsx:578` consumes it. Inspected `result-ui.test.ts` renders actual row/History/detail for measurement_only, invalid, inconclusive, pending, admitted1.1 research and abstention; delivery remains independently queued. Changed proof, synthetic provenance and legacy-shaped research produce unavailable/no score. `workspaceScope` requires matching active identity/account/generation, current capabilities and online state; capability mutation immediately changes Home scope. This closes the old branching defect; it does not clear unrelated UX-R001.
- **UX-002:** source and browser correction confirmed; actual native OS acceptance remains open. `ui/accessibility.tsx:14` supplies deferred web/native focus, origin/current-route guards, stale/detached cancellation and user-focus precedence. `components.tsx:601/686/694` hands focus to route/dialog headings and restores trigger. `components.spec.ts:626` explicitly asserts focused Home, Settings, Privacy, dialog heading, Cancel trigger, deeper Back and History. Correction log `/tmp/correction-HR-browser-final.log` records those exact cases passing at both viewports. Native `setAccessibilityFocus` calls are software implementation evidence only; no TalkBack/VoiceOver/browser-auth cancellation OS execution supplied.
- **UX-E01:** OPEN. The current seven-gate process was still running at inspection; readable `reports/local-gates.json` binds revision28 and is historical. Exact current CI and full per-case replacement evidence must be admitted before final positive dispositions. No aggregate test count or stale green job closes a clause.
- **UX-E02:** OPEN external native OS prerequisite. Build/core tests and browser fixtures do not execute camera/BLE permission dialogs, Settings return, SQLCipher/secure storage/unlock/key loss/process death, native share-sheet lifecycle, actual platform interruption/focus or screen readers/200% native text. These are unavailable execution prerequisites, not new source defects or permission denials.

Related initial UI/product corrections were independently inspected: supplied uncertainty `none` and exact abstention-band limits/rationale render from verified policy without invented clinical intervals; welcome explains default measurement and separately authorized study/model scope. Effective reduced-motion preference defaults to system and drives ordinary Modal animation, preserving scientific task stimuli. Actual DOM motion assertions at `components.spec.ts:693` inspect CSS animation after explicit system/on/off/reset changes. Actual destructive normal/pressed contrast assertions at738 composite group opacity over the rendered surface: correction raw JSON supplies light6.7718/5.5849 and dark10.0029/8.4208, both viewports. These narrow observations do not prove every text/control contrast or native large-text acceptance.

## Journey evidence assessed

The exact test body matters. A named fixture or successful screenshot is not proof of the full native journey.

| Journey | Concrete inspected behavior/assertions | Unproven boundary |
|---|---|---|
| Guest/default measurement and guided check | `mobile.spec.ts:6` enters demo with API blocked, separately acknowledges notice/context, adds fictional saliva/eye/ECG, asserts native reaction unavailable, saves before upload, asserts no guest Upload action/null probability, opens exact single-check ZIP and verifies every listed file digest. | Browser cannot execute actual native reaction, physical sensors or native encrypted restart. |
| Actual account/upload/recovery | `authenticated-live.spec.ts:220` body inspects real issuer S256/state/redirect, explicit account upload, forwarded finalization then dropped response, exact same-key receipt replay, null measurement result, memory-only reload/relogin/server history, worker export, foreign-owner refusal, study consent/withdrawal denied new capture, durable lost deletion acknowledgment, generation retirement and logout-family revocation. Prior correction receipts identify fictional origins/viewports; these are historical/current-source preflight evidence until final gates finish. | No mock success substitutes for the current real-service run. Browser reload proves memory-only behavior, not SQLCipher restart. |
| History and exact export | `components.spec.ts:499` retains selected IDs hidden by filters and prevents accidental broadening. Result tests retain historical target/evaluation dates and verified scope. I opened both correction-auth-evidence ZIPs read-only: exact member lists/selection and all member digests match. Mobile ZIP SHA7322071e8ab151fc217429e75bd910741392ef555f97b69e057ff424d955e5b4; desktop b83f370de6f3c60943351a03b31367e856f95580b5908e0a513c5efbd9c170bf. | Full current acceptance, actual native share/cancel/startup cleanup and OS lock remain pending. |
| Result admission/HR cached display | `resultPresentation.ts:48` verifies proof and withholds typed HR numeric/threshold/classification/uncertainty without current admission. `controller.ts:332–449` binds current view/result digest/check/epoch/active owner/generation and exact authenticated200/evidence acknowledgment. `components.spec.ts:31/74` actual screens use controlled service responses: fresh200 reveals81.8, evidence-return403 withholds, manual refresh revokes first, leaving invalidates late200, reopened422 stays withheld. | Controlled component HTTP is explicit; it is not genuine server registry-retirement execution. Backend correction report preserves separate actual authenticated red/green. No scientific TTL/clinical claim is invented. |
| HR export admission | `hr-read-admission.test.ts:288/324` rejects direct cached-proof export, checks independent preassembly and final-release reads, zero downloads after final refusal, unchanged retained evidence. `controller.ts:4155`, `services/export.ts:71`, web/native sharing callbacks enforce exact selected digest/current scope. `sharing-admission.test.ts` executes actual native sharing code with named filesystem/share doubles and guards the final async availability boundary. | Native OS sharing not executed; test-only digest map is a serializer contract, not genuine authority. |
| Permissions/BLE | `raw-recordings.spec.ts:297/392` actual Settings DOM with controlled camera provider asserts denied/restricted/undetermined/failure, zero prompts, explicit Settings callback only, foreground refresh and stale-owner/result rejection. Device screen/source distinguishes radio/permission/disconnect/boot/unsupported responses. | Actual Android/iOS permission/BLE/security/Settings integration absent. Current helper misses healthy signed reader (UX-R001). |
| Reaction and interruption | Browser asserts unavailable native task, never substitutes JS performance score. Current stable TASK cases distinguish core schedule/scoring execution from actual OS input/presentation. Source states practice6/scored60, no best-score retake, native stop before navigation/overlay and immutable replacement lineage. | `OTGD-033-AND-TASK-001-01`,003-02,006-01/007-02 lack actual native input/system-focus execution. Pure Kotlin/Swift/golden tests do not close these. |
| Sync failures and correction | `sync-conflict.test.ts:107` asserts412/frozen409 guarded server readback, retained pending evidence/key and no replay.155/200 guard epoch/owner/generation/foreign response;227/316 retain actual Retry-After waits;256/277 terminal422 field paths/redacted codes. `result-ui.test.ts` checks actual conflict/validation cards with blocked retry and new linked correction. | Final candidate execution pending; no generic PARTIAL count is called a software bug. |
| Privacy/delete/raw purposes | `components.spec.ts:451` Cancel leaves retry off/unsynced records; `raw-recordings.spec.ts:1111/1174/1230` records/upload separately off, exact policy acknowledgment reset and local fence;1260/1304/1339 exact raw export/source eligibility;1466 distinguishes quarantine/cleanup/deadline;1526 shows real category/policy/reason/explicit absent or supplied expiry. `manage.tsx:835` retains minimal terminal status and truthful legacy missing-detail copy. | Actual native encrypted raw storage/cleanup absent. Deletion receipt cannot promise physical erasure or recall shared bytes. |
| Participant instructions/lab | `components.spec.ts:171/230/263/297` forward/backward wall discontinuity and unavailable clock clear preparation, no capture, zero/max approved rest preserved; `raw-recordings.spec.ts:692/753/806/872` declarations cannot qualify ECG, interruption/replacement reset.920/972/1041 render exact lab method, true quantity/missing reasons/no concentration entry, retained pending chronology and explicit abandonment. | Real study/physical/chemistry/electrical authority absent. Existing required-chemistry abandonment repair is backend-controlled, never inferred from a timer/UI checkbox. |
| Operator/cloud/store/preview | All canonical clauses reviewed for deliberate plan/apply, exact scope/status/uncertain outcome and no false delivery claims; approved software remains distinct from actual hosting/release. Guest preview prevents account/acquisition/upload/inference and explains memory-only browser persistence. | Real service account, independently signed release, cloud deployment/store signing/submission/availability and protected environment setup remain external. None performed by reviewer. |

## Per-spec dispositions

Every row is IMPLEMENTATION scope and binds exact current canonical SHA-256 in the stable JSON. **G** means pending current gates plus exact-case replacement evidence; **N** means required native OS/accessibility runtime evidence unavailable; **S** means demonstrated source correction UX-R001. Research/physical/release limits are additionally explicit per row in JSON and are never silently excluded.

| Spec | UX journey | Decision | Holds |
|---|---|---|---|
| OTGD-001 | Full normative register: measurement default, source/claims, one-collection/one-task lineage, optional profile, alcohol separation, privacy and recovery; applied current amendment precedence. | CHANGES_REQUIRED | G,N,S |
| OTGD-002 | Dashboard admitted scope and fictional provenance. | CHANGES_REQUIRED | G,S |
| OTGD-003 | Save before upload, historical research navigation and missingness. | BLOCKED | G |
| OTGD-004 | Historical state, qualifier, time and admitted research scope. | BLOCKED | G |
| OTGD-005 | Guest versus research onboarding and independent notice. | BLOCKED | G |
| OTGD-006 | Verified research presentation versus ordinary null scores. | BLOCKED | G |
| OTGD-007 | Environment and account capability presentation. | BLOCKED | G |
| OTGD-008 | Research evaluation reports: genuine calculation versus externally unverified authority; no scientific claim adopted. | BLOCKED | G |
| OTGD-009 | Research admission, abstention and authenticated historical endpoint display. | BLOCKED | G |
| OTGD-010 | Separate exact raw-export purpose, notice, selected IDs, retention and share-copy limits. | BLOCKED | G |
| OTGD-011 | Operator reviewability, independent principals, rollback default and truthful capabilities. | BLOCKED | G |
| OTGD-012 | Conditional optical start, passive preview distinction, privacy stop and ROI opt-in. | BLOCKED | G,N |
| OTGD-013 | Signed reader identity/trust distinction, encrypted BLE and independent transport stop. | BLOCKED | G,N |
| OTGD-014 | Browser customer access, exact origins, navigation and honest release status. | BLOCKED | G |
| OTGD-015 | Cloud operator plan/apply, bounded recovery receipts and independent admission. | BLOCKED | G |
| OTGD-016 | Recovery fail-closed boundaries and retained deletion barriers. | BLOCKED | G |
| OTGD-017 | Isolated fictional preview, no account/acquisition services and honest persistence. | BLOCKED | G |
| OTGD-018 | Raw recording/upload separation, exact notice, local stop and independent cleanup status. | BLOCKED | G,N |
| OTGD-019 | Separate unavailable breath channel, mg/L/censoring, time, fictional data and no combined clearance. | BLOCKED | G |
| OTGD-020 | Fixed environments, bounded startup/recovery and truthful verification status. | BLOCKED | G,N |
| OTGD-021 | Home start/resume, device readiness, workspace races and accessible navigation. | CHANGES_REQUIRED | G,N,S |
| OTGD-022 | Deliberate export source/scope and explicit sharing, expiry and cleanup. | BLOCKED | G,N |
| OTGD-023 | BLE discovery/permission/radio denial, association, verified binding, disconnect/forget recovery. | BLOCKED | G,N |
| OTGD-024 | Optional ECG and declared versus actual electrical state; unavailable human ECG remains explicit. | BLOCKED | G,N |
| OTGD-025 | Camera preview/permission/lifecycle and conditional optical units/timing. | BLOCKED | G,N |
| OTGD-026 | Frozen context, eight-stage guided check, retained attempts, cancel/save/upload and parity. | BLOCKED | G,N |
| OTGD-027 | Pulse source/quality/contact/stale state and independent acquisition timing. | BLOCKED | G,N |
| OTGD-028 | Local/remote history, exact selection, immutable lineage and faithful states. | BLOCKED | G,N |
| OTGD-029 | Local-first storage, explicit queueing, lost acknowledgment replay and account generation. | BLOCKED | G,N |
| OTGD-030 | First-run explicit guest/account entry, versioned notice and no permission prompt on entry. | BLOCKED | G,N |
| OTGD-031 | Separate local clear/cloud deletion/account deletion, extra unsynced confirmation and durable pending intent. | BLOCKED | G,N |
| OTGD-032 | Optional profile, unit conversion, first-error focus, drafts/conflicts and frozen context. | BLOCKED | G,N |
| OTGD-033 | Native reaction instructions, practice/scored split, unavailable browser capture and interruption/retry semantics. | BLOCKED | G,N |
| OTGD-034 | Measurement/research/invalid/inconclusive states, missingness, historical time and separate delivery state. | BLOCKED | G,N |
| OTGD-035 | One saliva collection, quantity/qualifier/units, original report and delayed lab status. | BLOCKED | G,N |
| OTGD-036 | Functional settings, no-prompt permission status/recovery, diagnostics, appearance and accessibility. | BLOCKED | G,N |
| OTGD-037 | PKCE browser sign-in, cancel/unlock/account isolation, explicit logout and remote-revocation uncertainty. | BLOCKED | G,N |
| OTGD-038 | Exact consent and invitation, withdrawal, fresh capture admission and truthful study absence. | BLOCKED | G,N |
| OTGD-039 | Exact approved participant instructions, declaration boundaries, fresh acknowledgment and monotonic rest. | CHANGES_REQUIRED | G,N,S |
| OTGD-040 | Governed lab collection, specimen lineage, pending analysis and independent staff import. | BLOCKED | G,N |
| OTGD-041 | Prespecified matched evaluation / HR variant and truthful absent comparisons. | BLOCKED | G |
| OTGD-042 | Restricted cardiac timing authority and historical qualification limits. | BLOCKED | G |
| OTGD-043 | Selected vendor source/quality/freshness and software versus physical qualification. | BLOCKED | G,N |
| OTGD-044 | Private route/security header verification and bounded byte receipts. | BLOCKED | G |
| OTGD-045 | Exact CNAME preview/atomic create/no-op and bounded operator inputs. | BLOCKED | G |
| OTGD-046 | Fictional browser preview manifest, verified readiness and hosting boundaries. | BLOCKED | G |
| OTGD-047 | Store plan/build/submit/status, genuine signed artifact, uncertain submission and encrypted handoffs. | BLOCKED | G,N |

The nineteen specs with only current software evidence holds in this UX slice are listed by `gate_only_hold:true` in JSON. That label means no demonstrated UX source defect or native runtime prerequisite was identified for that particular review slice; it does not waive independent scientific/release prerequisites or guarantee final PASS. No case is excluded to improve counts.

Next action: PM consolidate UX-R001 for the remaining correction round if accepted. If source changes, invalidate affected bindings and repeat affected current gates/reviews. Supply completed current gate/CI and exact-case evidence for the required final update. Source is frozen and this reviewer cannot run OS or concurrent runtime probes. These remaining actions are pending/unexecuted, not denied; no uncertain external action was attempted.
