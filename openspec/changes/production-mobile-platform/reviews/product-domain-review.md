# Product and domain adversarial review

**Change:** production-mobile-platform  
**Phase:** independent review snapshot before application implementation  
**Disposition:** changes required; all findings below are Open  
**Reviewer scope:** customer journeys, scientific claim boundaries, cross-feature integration, offline/account transitions, consent/withdrawal, accessibility, and acceptance completeness.

This review covers all 20 feature specifications, [design](../design.md), [proposal](../proposal.md), and the original [HLD](../../../../specs/HLD.md), [LLD](../../../../specs/LLD.md), [PRD](../../../../specs/PRD.md), and full requirement register. The reviewer authored seven of the feature drafts earlier and reviewed the other thirteen plus their integration in this pass. No feature/design files were edited during this review. Requirement IDs are used as stable references because the parallel formatting pass may move detailed clauses above the OpenSpec requirement headings without changing their substance.

## Executive finding

The specifications consistently preserve several necessary scientific boundaries: no saliva-to-blood conversion, no demographic clearance formula, censored concentrations stay null, camera preview is not a pupil measurement, PPG is not ECG, and physical/scientific qualification is distinct from source-code completion. The blocking gaps are at the joins between features. Different implementation teams could currently ship different upload, logout, retry, withdrawal, and result behaviors while each followed its own feature document.

**Finding count: 0 Critical, 12 High, 3 Medium, 0 Low.** High findings require a normative resolution before implementation. This document does not attest that any application, hosted service, physical device, or native binary has been tested.

## Coverage

| Feature reviewed | Main coverage and relevant findings |
|---|---|
| [android-onboarding](../specs/android-onboarding/spec.md) | Scope notice, guest isolation, acknowledgment; UX-004, UX-005 |
| [android-sign-in](../specs/android-sign-in/spec.md) | Account lifecycle, protected local access, reauthentication; UX-005, UX-009 |
| [android-profile](../specs/android-profile/spec.md) | Bounds, units, immutable revisions, conflicts, context timing; UX-002, UX-009, UX-011 |
| [android-dashboard](../specs/android-dashboard/spec.md) | Check entry, active draft, capability/source honesty, navigation; UX-011, UX-013 |
| [android-device-pairing](../specs/android-device-pairing/spec.md) | Trust versus association, boot identity, transport, revoked authority; UX-002, UX-006, UX-015 |
| [android-guided-check](../specs/android-guided-check/spec.md) | Attempts, finalization, replay, outcome, cancellation; UX-001–004, UX-011, UX-014 |
| [android-saliva-measurement](../specs/android-saliva-measurement/spec.md) | Sample identity, qualifiers/bases, delayed analysis, correction; UX-002, UX-003 |
| [android-eye-capture](../specs/android-eye-capture/spec.md) | Preview versus capture, optical authority, timing, raw retention; UX-002, UX-006, UX-007, UX-014 |
| [android-heart-rate](../specs/android-heart-rate/spec.md) | PPG context, source, stale readings, modality, retries; UX-002, UX-006 |
| [android-ecg-capture](../specs/android-ecg-capture/spec.md) | Electrical gates, one-modality selection, artifact quality; UX-002, UX-006, UX-007 |
| [android-reaction-task](../specs/android-reaction-task/spec.md) | Native evidence, schedule/scoring, lineage, focus, qualification; UX-002, UX-003, UX-010, UX-014, UX-015 |
| [android-results](../specs/android-results/spec.md) | Result authority, delivery status, retry and immutability; UX-001, UX-003 |
| [android-history](../specs/android-history/spec.md) | Owner/cursor isolation, historical time, revisions, export entry; UX-001, UX-002, UX-005, UX-012 |
| [android-offline-sync](../specs/android-offline-sync/spec.md) | Durable queue, explicit action, conflict, identity change; UX-003–006, UX-009 |
| [android-privacy-controls](../specs/android-privacy-controls/spec.md) | Retry preference, local clearing, deletion, retention semantics; UX-004–009 |
| [android-settings-accessibility](../specs/android-settings-accessibility/spec.md) | Functional destinations, fixed task styling, accessibility; UX-005, UX-013–015 |
| [android-study-enrollment](../specs/android-study-enrollment/spec.md) | Consent versus capabilities, version change, offline withdrawal; UX-001, UX-006, UX-007, UX-013 |
| [android-alcohol-channel](../specs/android-alcohol-channel/spec.md) | Independent mg/L record, calibration, separate result, entry; UX-002, UX-013 |
| [android-data-export](../specs/android-data-export/spec.md) | Selected record scope, raw permission, bearer delivery, cleanup; UX-007, UX-008, UX-012 |
| [android-app-environment](../specs/android-app-environment/spec.md) | Environment separation, startup, encrypted recovery, evidence; UX-005, UX-006, UX-015 |

## Findings

### UX-001 — Research-result reachability conflicts with the closed release

- **Severity:** High
- **Status:** Open
- **Sources:** design §§1/7; AND-CHECK-007; AND-RES-003 and its engineering contract; android-history engineering contract; AND-SET-004.
- **Counterexample:** A correctly shaped `research_estimate` references the current account/session/hash and an `active_research` manifest. Guided Check permits rendering an authorized estimate; Results describes a server-controlled future capability and a default absence of a model; History explicitly rejects research estimates in this measurement-only release; design says inference requires a separate reviewed change. The same record can therefore be accepted on completion and rejected in History, or enabled by registry configuration despite the declared release boundary.
- **Required correction:** Define one release-wide `inference_available=false` invariant for this change, enforced in service execution and all client result paths. Operator configuration alone cannot enable it. Retain the schema vocabulary for future compatibility, but make the current handling of any `research_estimate` explicit and consistent. Amend future examples so they cannot be interpreted as current acceptance criteria.
- **Acceptance:** Submit an otherwise schema-valid, correctly linked research estimate through API, live result, restored cache, history, and export. No current client path displays its probability and no current worker executes a model. Verify consistent unsupported-state behavior.

### UX-002 — Mandatory capture evidence has no complete persistence/exchange mapping

- **Severity:** High
- **Status:** Open
- **Sources:** AND-CHECK-002/003/004; AND-SAL-002; AND-EYE-004; AND-HR-003; AND-ECG-003/006; AND-TASK-007; design §§5/6; existing `contracts/session.schema.json`; original LLD §10.
- **Counterexample:** A check has a failed PPG attempt, a successful PPG attempt, then an ECG alternative, plus an interrupted task and its successful retry. The features require immutable attempt UUIDs, lineage, detailed metadata, and review/history retention. The strict v0.1 snapshot contains one cardiac and one task projection and lacks a full attempt ledger, profile-version reference, optical frame metadata, and many collection fields. The design does not define a complete companion DTO/API/table mapping. Implementers can discard evidence to satisfy the snapshot schema or attach forbidden extra properties and fail ingestion.
- **Required correction:** Specify versioned companion capture/attempt/context contracts, their immutable linkage and digest rules, their local/server storage, their submission/read/export routes or bounded envelope, and their privacy classification. Map every mandatory feature field to either a snapshot field, a companion field, or an explicitly authorized artifact. Include alcohol routes/records in the shared endpoint inventory. Define which evidence remains local when upload is not authorized; do not silently equate local-only retention with complete cloud history.
- **Acceptance:** Complete a multi-attempt check, restart, upload, fetch on another device, and export. All accepted and superseded/failed attempt identities, selected modality, original profile revision, timing/quality metadata, and references remain reconstructable without schema violations or unauthorized raw upload.

### UX-003 — Retry after finalization can require mutating an immutable check

- **Severity:** High
- **Status:** Open
- **Sources:** AND-RES-006 interrupted-task scenario; AND-CHECK-003/006/007; AND-SYNC-005; AND-SAL-006; AND-HIST-004; design §6.
- **Counterexample:** The user finishes a check with an interrupted task. The immutable snapshot and invalid result are saved. Results offers a linked retry through the guided flow, whose retry rule allocates a new attempt under the current session. Selecting that new attempt changes the finalized snapshot/hash, which the server forbids. The alternatives—silent mutation, a permanently unsyncable retry, or a hidden new session—are not specified.
- **Required correction:** Distinguish retries before finalization from reacquisition after finalization. Define exact UI copy and identity transitions for a post-finalization replacement check, and separate that path from an administrative correction of an existing report. Freeze whether previous components may be carried into a replacement and under what explicit protocol/timing rule. A new physical acquisition cannot retain an old target time merely to preserve linkage.
- **Acceptance:** Retry from an already finalized invalid result. The original session/hash/result remain unchanged; the replacement has the declared new identity/time and explicit linkage. The same test must pass after a server acknowledgment and after offline local finalization.

### UX-004 — Guest-demo upload policy and automatic-retry policy diverge

- **Severity:** High
- **Status:** Open
- **Sources:** AND-ONB-002 and demo-does-not-upload scenario; AND-PRO-005; android-offline-sync customer experience and AND-SYNC-006; AND-PRIV-001; AND-CHECK-006/007.
- **Counterexample:** Onboarding promises isolated demo checks that never enter an account upload queue, while Offline Sync permits demo synchronization to an explicitly allowed synthetic project. In parallel, Privacy says automatic retries default off and require an already explicit upload request, while Guided Check and Offline Sync require retry on reconnection without referencing that preference. A guest record or queue item can receive different behavior depending on the implementation entry point.
- **Required correction:** Publish a single environment × workspace × data-mode × destination policy. Separate an account-free guest demo from authenticated synthetic development fixtures/projects. Define whether the guest demo has any cloud path and align all notices/actions accordingly. Make manual versus automatic retry precedence explicit for profile, session, artifact, and privacy operations; reconnection must not override a disabled retry preference. Use one consistent finalization/upload action sequence and copy.
- **Acceptance:** Exercise guest demo, authenticated synthetic local/QA fixture, ordinary local account check, and study check with automatic retries on/off. Assert the exact allowed network mutations after Finish, Upload, reconnect, and account switch.

### UX-005 — Logout retention and local unlock are not one defined policy

- **Severity:** High
- **Status:** Open
- **Sources:** android-sign-in journey step 5 and AND-AUTH-005/006; design §8; AND-HIST-005; AND-ENV-002; android-offline-sync engineering contract.
- **Counterexample:** Auth's displayed sign-out action removes the account cache; design says logout locks account records and retains pending work. Offline History requires a local unlock, but no shared requirement defines that unlock, its key access, whether a signed-out account may unlock offline, or what a second account on the same phone can access. Android could retain account A's records under an installation key while iOS removes them, and both could appear to satisfy their local clauses.
- **Required correction:** Define explicit sign-out choices and defaults, pending-data handling, token removal, database/key scope, cache-retention/erasure semantics, and a deterministic signed-out/offline read policy. If local unlock exists, specify its device-credential/biometric mechanism, failure/cancel/restart behavior, and account binding; otherwise remove the undefined unlock promise and require reauthentication before access. Clear-local, sign-out, key loss, and account deletion must have separate state transitions.
- **Acceptance:** Use accounts A and B on one phone with an unsynced A check; sign out online/offline, restart, cancel unlock, switch accounts, and lose the storage key. Verify the declared retention outcome and that no alternative account obtains A's records or queue.

### UX-006 — Withdrawal and offline capabilities cannot provide the promised immediate stop

- **Severity:** High
- **Status:** Open
- **Sources:** android-study-enrollment customer journey; AND-STUDY-004/005; AND-SYNC-002; AND-PRIV-005; design §§7/8; AND-EYE-003/006; AND-HR-002; AND-ECG-002.
- **Counterexample:** A participant selects Withdraw while offline, but the cached scope remains unexpired and the withdrawal API cannot accept the request. The feature does not specify immediate local suppression, so another capture may start. A second offline phone cannot observe server-accepted withdrawal and can also continue until expiry. Rolling back the wall clock or restarting the phone can extend an expiry check unless the cached-authorization time basis is defined. “Stops immediately” is therefore not a universally achievable contract as written.
- **Required correction:** Stop new local study operations immediately on withdrawal intent, represent server submission as pending when offline, define active-capture behavior, and preserve/retry the exact withdrawal request. Choose and state the remote/offline rule: prohibit offline qualified capture, or use an explicitly bounded grant policy with trusted elapsed-time handling, restart/clock-discontinuity behavior, and clearly limited revocation observability. Server acceptance must block later verification/upload regardless of a stale client grant. Define Decline's persistence/state/API effect separately from withdrawal.
- **Acceptance:** Withdraw offline on A, revoke remotely while B is offline, roll the wall clock back, restart, and replay a pre-withdrawal upload ticket. No local intent is ignored; server-side revocation always wins; any documented offline exposure window is measured and disclosed accurately.

### UX-007 — Presigned export delivery conflicts with current-owner and revocation guarantees

- **Severity:** High
- **Status:** Open
- **Sources:** android-data-export engineering contract; AND-EXP-002/004/005; AND-STUDY-005; AND-EYE-006; AND-PRIV-005; design §8.
- **Counterexample:** An owner obtains a five-minute S3 presigned download URL, then withdraws raw-data permission or requests deletion. The previously issued bearer URL can still retrieve the object without another application-owner or policy check. A person who receives that URL can use it during its lifetime. The requirements nevertheless promise authorization on every download, no unauthenticated direct download, and prevention of delivery after permission changes.
- **Required correction:** Select a delivery model that matches the guarantee. Either use an authenticated, revocable delivery gateway/ticket checked at byte access, with a defined revocation race; or explicitly document bearer-URL authority and its bounded lifetime, remove the stronger current-authorization promise, and define object/ticket invalidation for withdrawal/deletion. Align mobile sharing copy, job status, and raw-media authorization with the actual model. Presigned-query strings must remain out of logs and diagnostics.
- **Acceptance:** Request a ticket, change permission/delete, then attempt the original URL; test a copied URL as well. Verify actual behavior against the chosen policy rather than testing job-status ownership alone.

### UX-008 — Privacy job discriminators and terminal states disagree

- **Severity:** High
- **Status:** Open
- **Sources:** android-privacy-controls journey step 6 and AND-PRIV-004; design §8; android-data-export engineering contract; shared GET `/v1/privacy/jobs/{job_id}`.
- **Counterexample:** The deletion worker returns `partially_retained` under design, the privacy UI accepts `partially_completed`, and the export view uses `expired`. A retained-by-policy completion can be treated as an unknown failure or a retriable deletion, while a processing failure can be displayed as an accepted retention exception. The shared endpoint has no frozen discriminated response shape in these clauses.
- **Required correction:** Define a versioned job-type discriminator and one exact state machine per type, including whether policy retention is a terminal state or completion metadata. Specify accepted/start/completion/expiry timestamps, permitted actions, retained categories, failure reasons, and account-deletion status access after identity revocation. Reuse the same enums and display mapping everywhere.
- **Acceptance:** Round-trip every job-type/state pair from API through persisted cache and UI, including partial failure, completed-with-retention, expired export, logout, and account deletion. Unknown values must produce a recoverable unsupported state without a false completion claim.

### UX-009 — Optimistic-concurrency errors are handled inconsistently

- **Severity:** High
- **Status:** Open
- **Sources:** android-profile API contract and AND-PRO-004; AND-SYNC-005; original LLD §9; design §§5/6.
- **Counterexample:** A profile edit gets HTTP 412 and opens its specified compare/review flow. A snapshot update with the same stale `If-Match` precondition expects 409 in Offline Sync. A generic client implementing only the documented common error map may classify 412 as an unknown/retryable error or discard the unsaved profile. Conversely, an implementation returning only 409 never opens the profile's 412 handler.
- **Required correction:** Freeze HTTP semantics centrally: distinguish stale precondition, immutable-state conflict, and idempotency-key/body conflict. Update every endpoint/client/error fixture to the same codes and typed reason payloads. A conflict must preserve the exact pending data, show the authoritative revision, and never trigger an unconditional overwrite or repeated automatic retry.
- **Acceptance:** Perform two-device profile edits, two-device snapshot finalization, changed-body idempotency reuse, and a lost successful response. Verify the intended distinct recovery route and retained data for each case.

### UX-010 — Native timing/scoring has unresolved engineering rules

- **Severity:** High
- **Status:** Open
- **Sources:** AND-TASK-002/003/004/005/006/008; original LLD §6; design §9.
- **Counterexample:** A native touch has an event timestamp 990 ms after onset but is dispatched after the 1000 ms window closes. One platform records an omission before it arrives; the other includes the tap. Simultaneous left/right touches can have the same timestamp and arrive from an unordered native touch collection. The text requires deterministic tie handling but does not choose it. Likewise the 66 generated onset intervals are not explicitly assigned to the 65 successive onset gaps and terminal window, and callback/dispatch integrity budgets are still to be frozen.
- **Required correction:** Before native implementation, provide the exact developmental task configuration, schedule/golden fixture and hash, interval-index convention, half-open/inclusive window boundary, tie/multi-touch ordering, delayed-dispatch finalization policy, callback/input lateness budgets, eligibility calculation, and deterministic terminal arbitration. These can be conservative engineering defaults labeled uncalibrated; they are distinct from still-open clinical timing qualification. Define output precision and cross-platform comparison tolerances numerically.
- **Acceptance:** Golden tests must cover exact deadline timestamps, late dispatch with an in-window event timestamp, simultaneous opposing touches, every schedule boundary, all-omission runs, overflow, and cancel/final-completion races in Kotlin, Swift, and the reference extractor.

### UX-011 — Profile/context is frozen at different lifecycle points

- **Severity:** Medium
- **Status:** Open
- **Sources:** AND-PRO-003 and profile API contract; AND-CHECK-002; AND-DASH-002/003; original HLD §5.
- **Counterexample:** Start check creates a draft and copies profile A per Profile. Before acquisition, the user edits to B. Guided Check freezes profile at start of acquisition and therefore selects B. The same user journey produces different snapshots depending on which requirement an implementer uses. Changing last-use/exercise context increases the consequence of this ambiguity.
- **Required correction:** Name one authoritative context-freeze event and its UI acknowledgment, define whether pre-acquisition drafts can update without a restart, and distinguish session creation time from physiological target time. Preserve the original self-report time and context revision; never recalculate an earlier snapshot from the current profile.
- **Acceptance:** Start a draft, edit the profile locally/remotely before first acquisition, edit again afterward, and resume after restart. All clients choose the same declared revision and show when it was confirmed.

### UX-012 — “Export this check” lacks a fixed one-check scope contract

- **Severity:** High
- **Status:** Open
- **Sources:** android-history journey step 4 and AND-HIST-006; android-data-export customer journey/engineering contract and AND-EXP-001/002/003.
- **Counterexample:** History offers Export this check, but the export screens specify only This device versus Synced records and an ordinary profile/check summary. No caller contract requires the selected check ID to survive that route or limits profile versions to the selected check's context. An implementation can export all local checks after a user chose one check, unexpectedly disclosing additional records.
- **Required correction:** Define typed export entry parameters and immutable selection scope: single check, explicit selected list, or all owned records. Show selected count/date range before Create export and preserve the exact choice across source switching, restart, and retry. Define which associated profile versions, attempts, linked results, and optional artifacts belong to a single-check export; changing scope requires a visible new confirmation.
- **Acceptance:** Start export from one historical check while multiple unrelated checks/profile revisions exist. Verify archive membership exactly, including after switching local/synced source, reauthentication, and a resumed export draft.

### UX-013 — Research and alcohol entry points are absent from the owning navigation inventory

- **Severity:** Medium
- **Status:** Open
- **Sources:** android-study-enrollment customer journey; android-alcohol-channel customer experience; android-settings-accessibility journey step 1; android-dashboard journey/navigation.
- **Counterexample:** Settings implementation includes every row listed in its specification but no Research access entry. Home implements its complete listed cards but no Alcohol entry. Each individual feature can pass its own component tests, while the study and alcohol screens have no user-reachable path required by their feature specifications.
- **Required correction:** Publish a shared route/entry-point inventory and add both entries to their owner screens, including signed-out/unavailable states and Back behavior. Include route parameters and workspace changes rather than relying on ad hoc callbacks. Disabled scientific capabilities should remain explainable through the intended route.
- **Acceptance:** Starting from a fresh installation on each platform, navigate to all 20 feature destinations using visible controls alone; verify unavailable/empty features are reachable and never imply availability.

### UX-014 — Cancellation confirmation can invalidate a task before the user confirms

- **Severity:** High
- **Status:** Open
- **Sources:** AND-CHECK-005; AND-TASK-006; AND-EYE-002; android-onboarding workspace-switch behavior; AND-SET-001.
- **Counterexample:** During a native task the user selects Cancel check. Guided Check requires a confirmation while acquisition is active. Showing the dialog obscures the stimulus or loses native focus, which the task must invalidate. The user chooses Stay in check, but the task can no longer continue; resuming would violate the no-mid-run-resume rule, while silently losing the attempt would contradict the cancellation choice.
- **Required correction:** Specify cancellation behavior for active timing acquisitions separately from ordinary drafts. End the native run deterministically before any overlay that changes stimulus visibility/focus, and use copy that does not offer to resume an already invalidated run; or make the initial action an explicit immediate End task with confirmation reserved for discarding the broader inactive draft. Apply the same rule to Back, workspace switching, settings dialogs, and active optical stimulus capture.
- **Acceptance:** Select Cancel, Back, and workspace switch during a task and exercise every dialog choice on Android/iOS. Exactly one terminal event occurs; no obscured task stays valid, no invalid run resumes, and the user receives accurate retained-attempt/draft feedback.

### UX-015 — Software support and device acceptance matrix is not frozen

- **Severity:** Medium
- **Status:** Open
- **Sources:** design §§2/9/10; AND-ENV-001/007; AND-DEV-002; AND-TASK-008; AND-SET-006/007; original APP-014/G-06/G-10.
- **Counterexample:** Bluetooth contains paths for older Android versions, the native modules require current framework support, and the acceptance plan calls for both platforms without naming a minimum OS, target SDK, supported orientations/form factors, or representative native-device matrix. Teams may label an unsupported old OS as a permission fault or call a single simulator pass Android/iOS coverage. Scientific supported-device limits should remain open, but the software build/support contract must be concrete.
- **Required correction:** Freeze the application minimum/target OS/build versions and supported form factors/orientations from the selected toolchain; name the mandatory emulator/simulator and physical-device/lifecycle/accessibility test matrix. Separately identify which configurations are software-supported but scientifically unqualified. Define a tested unavailable screen for unsupported native features and list externally unexecuted evidence in the release ledger.
- **Acceptance:** Build and exercise the declared minimum/representative platform configurations, large text/screen readers, camera/BLE denial, navigation, and native-task lifecycle. Report exact tested devices/OS versions and outstanding physical/clinical qualification separately.

## Review exit and re-review scope

Resolve every High finding with explicit source amendments before coding. A central policy is sufficient only when each conflicting feature points to it and no contradictory scenario remains. Re-review the exact amended clauses, shared DTO/state definitions, and added acceptance cases; do not mark a finding resolved merely because an implementer plans to choose a behavior later.

The later implementation ledger must map these resolved requirements to actual artifacts and evidence. OpenSpec structural validation verifies document form; it does not establish cross-feature correctness, native hardware performance, access-control enforcement, or clinical qualification.
