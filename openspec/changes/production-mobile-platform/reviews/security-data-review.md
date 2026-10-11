# Independent security and data-integrity review

Review date: 2026-10-10, America/Chicago. Phase: specification review before implementation. Reviewer lens: authentication, ownership, deletion/revocation races, immutable evidence, native timing, device trust, and cross-feature contracts.

**Disposition: changes required before implementation.** This review identifies six High and eight Medium findings. No Critical finding was identified in this document snapshot. All findings begin **Open**; a later resolution must identify the corrected contract and evidence rather than replacing this initial finding with a claim that testing already passed. Finding IDs in this document are review IDs, not the similarly named upstream full-specification requirements.

The review read the proposal, design, all 20 feature specifications, and the upstream HLD/LLD/PRD. It also inspected the existing session, measurement, result, and OpenAPI contracts to distinguish an actual missing field from an already implemented schema property. The author's seven Android capture specifications were included in the review. Moving long requirement bodies into ID-mapped detailed-contract sections during formatting does not change the affected requirement identities below.

This is a document and contract review. It does not constitute native compilation, a penetration test, a physical sensor experiment, an AWS deployment, or clinical validation. No feature or scientific gate is marked implemented or qualified by this review.

## Findings

### SEC-001 — Deletion generation is required but absent from the wire and persistence contract

**Severity:** High. **Status:** Open.

**Sources:** design.md §§5–6 and §8; android-privacy-controls AND-PRIV-005 and Data/API/policy contract; android-offline-sync Engineering contract and AND-SYNC-003/004; existing contracts/session.schema.json and the RegisterSession request in contracts/openapi.yaml.

**Problem:** Privacy requires a new data generation after deletion and rejection of stale offline writes. The shared endpoint/DTO design does not identify where a client receives this generation, how it accompanies registration/profile/artifact/export writes, or how a worker checks it. The v0.1 snapshot has no generation field, and registration accepts only session ID, mode, and protocol. Tombstones for already-known session IDs cannot identify never-uploaded old records with new UUIDs. Idempotency records may also retain response bodies containing data already deleted.

**Failure example:** Phone B captures check X offline. Phone A completes all_data deletion and begins a new account-data generation. B later registers X, which the server has never seen. Subject, UUID uniqueness, and JWT are valid; without a generation precondition the server accepts the old check and recreates the deleted dataset. An old idempotency response can additionally return a deleted profile revision.

**Required correction:** Define a server-issued account data generation and its authenticated retrieval, required mutation precondition, local queue field, database column, and outbox/worker check. Compare it transactionally against the account's current writable generation. Define deletion locking, stale-generation error/reconciliation, and when a new generation becomes usable. Remove sensitive idempotency response bodies during deletion while retaining only the minimal denial/deduplication metadata permitted by policy. Cover profile, sessions, artifacts, exports, device bindings where applicable, and restore replay. Existing scientific snapshots can remain v0.1 if generation belongs to a clearly versioned transport envelope.

**Acceptance target:** Two-device test with an old never-uploaded UUID; concurrent deletion/finalization; delayed worker event; old idempotency replay; restore followed by stale upload. None may resurrect the deleted generation.

### SEC-002 — Signature-only JWT validation does not enforce promised account revocation

**Severity:** High. **Status:** Open.

**Sources:** design.md §4 JWT validation and §8 account deletion; android-sign-in AND-AUTH-004/006; android-privacy-controls AND-PRIV-003/005.

**Problem:** The backend algorithm validates JWT signature, issuer, token use, client, and times, but no current application-account disabled/deleting state or revocation generation is specified as an API authorization prerequisite. Calling Cognito revocation or deleting a refresh credential does not make a separately running JWT verifier consult Cognito's revocation state. AWS explicitly documents that a revoked token can still pass a JWT library's signature/expiry checks: [Cognito token revocation](https://docs.aws.amazon.com/cognito/latest/developerguide/token-revocation.html).

**Failure example:** An access token is copied before account deletion. After deletion is accepted and Cognito logout/revocation succeeds, that unexpired token still passes the specified FastAPI verifier. A request that lazily recreates an account row or creates a new export can restore access during the token's remaining lifetime.

**Required correction:** Add an application authorization check for active account state and a monotonic revocation/session generation on every protected request and protected worker delivery. Define retained minimal deleted-subject tombstones and prohibit automatic account recreation from a still-valid old token. State whether ordinary sign-out revokes one app session or all app sessions; enforce the chosen scope independently of Cognito's remote response. Define the intentionally limited post-deletion receipt/status behavior if normal credentials are revoked.

**Acceptance target:** A previously accepted access token must be denied after application account revocation/deletion, without waiting for JWT expiry or relying only on a failed refresh.

### SEC-003 — Signed device evidence has no complete backend-verifiable representation

**Severity:** High. **Status:** Open.

**Sources:** design.md §7; android-device-pairing AND-DEV-003/004/006/008; android-heart-rate AND-HR-002/003; android-saliva-measurement AND-SAL-005; existing session and measurement schemas; design.md §5 endpoint inventory.

**Problem:** The design correctly requires provisioned P-256 keys and signed human telemetry. It does not freeze the signed challenge/telemetry serialization, domain separator, signature/key encoding, trust-key delivery, or atomic challenge-consumption rule. More importantly, the v0.1 snapshot contains a device ID and source strings but no binding ID, authorization ID, signed evidence reference, or mapping from signed payload values to accepted normalized fields. No separate capture-attestation ingestion DTO/route is defined. Local signature verification alone cannot establish the provenance of a later independently submitted HTTP snapshot.

**Failure example:** A modified client supplies a legitimate registered device ID, a known calibration ID, and source=validated_sensor while changing the concentration or pulse value in the uploaded snapshot. The server can confirm that a device/key/calibration exists, but the specified snapshot does not carry proof that the device signed these values for this session. A repeated challenge can also race two binding requests unless one-time use is an atomic database transition.

**Required correction:** Freeze domain-separated signed envelopes for binding challenges and capture evidence, including environment, owner/binding or authorization scope, device/key ID, boot/capture/session IDs, sequence, configuration hash, payload digest, and expiry where applicable. Specify JCS or another exact serialization and one signature encoding. Define authenticated trust-key retrieval/rotation and atomic challenge consumption. Add a versioned capture-attestation record/endpoint or explicitly bound artifact envelope; the server must verify its signature, scope, replay state, and exact normalized-value mapping before accepting verified hardware provenance. Keep verified human capture unavailable until this contract and real provisioning evidence exist.

**Acceptance target:** Reject modified signed values, cross-session/environment replay, arbitrary trust keys, concurrent challenge replay, stale boot IDs, and a valid device signature paired with a different normalized measurement.

### SEC-004 — Presigned export delivery conflicts with owner and revocation guarantees

**Severity:** High. **Status:** Open.

**Sources:** design.md §8 export URLs; android-data-export Engineering contract, AND-EXP-002/004/005; android-study-enrollment AND-STUDY-005; android-privacy-controls AND-PRIV-005.

**Problem:** Export requirements authorize every download to the current owner and prevent now-unauthorized raw delivery after revocation. A direct five-minute S3 presigned URL is a bearer capability; S3 does not call this application's ownership or consent logic for each GET. Issuing the URL after an owner check is not the same contract as checking the actual later download. This property is documented in [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).

**Failure example:** At 12:00 an owner receives a raw-data export URL. At 12:01 raw permission is revoked or deletion is accepted. At 12:02 the old URL is used, possibly by another holder. Checking permission only when issuing the ticket or generating the archive does not block that GET.

**Required correction:** Choose and document one enforceable delivery model. To retain the current guarantee, use an authenticated download operation/proxy that checks current ownership, generation, policy, and export status at request start, with a defined revocation behavior for an already-open stream. Alternatively narrow the guarantee explicitly to ticket issuance, disclose its bounded bearer lifetime, and define prompt deletion/revocation of all relevant export object versions; do not simultaneously promise per-download account authorization. Never put bearer URLs into logs or diagnostics.

**Acceptance target:** Issue a ticket, revoke permission/delete data before a subsequent download starts, and prove the selected policy's outcome. A ticket-creation authorization test is insufficient.

### SEC-005 — Artifact immutability is asserted without a pinned version or promotion rule

**Severity:** High. **Status:** Open.

**Sources:** design.md §8 upload completion and infrastructure §§2–3; android-eye-capture AND-EYE-006; android-ecg-capture AND-ECG-003/007; android-data-export AND-EXP-006; original LLD §10.

**Problem:** The design says completion verifies bytes and records an immutable object version, but does not require bucket versioning in every environment or define how every downstream read pins that exact version. A still-valid upload ticket can be reused. A normal S3 GET retrieves the current version unless versionId is specified: [S3 version retrieval](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RetrievingObjectVersions.html).

**Failure example:** The uploader sends bytes A. Completion verifies A and marks the artifact usable. Before the upload URL expires, the uploader writes bytes B to the same key. A later feature extractor or export worker reads the key without the verified version ID and consumes B under A's accepted metadata/hash.

**Required correction:** Freeze an immutable promotion strategy: either require S3 versioning and pin the verified VersionId on all reads/copies/exports/deletions, or verify an upload-only quarantine object and promote it to a separate immutable final key that the upload principal/ticket cannot overwrite. Define completion locking, exact source version, content-size enforcement, orphan cleanup, and authorization/generation recheck at promotion commit. Avoid relying on caller metadata or a key name as immutability evidence.

**Acceptance target:** Reuse the original upload ticket after successful completion, race overwrite with verification, and prove that feature extraction/export consumes only the verified bytes or rejects the artifact. Test actual LocalStack behavior and real QA S3 separately.

### SEC-006 — Offline authorization expiry can be bypassed by wall-clock rollback

**Severity:** High. **Status:** Open.

**Sources:** design.md §7 cached authorization; android-study-enrollment AND-STUDY-004; android-guided-check AND-CHECK-002/006; android-offline-sync Engineering contract; android-reaction-task AND-TASK-003.

**Problem:** Expiry enforcement is required, but the trusted time source, signed/verified grant format, local time anchor, reboot behavior, and maximum offline lifetime are unspecified. Native monotonic task timing does not automatically solve authorization expiry. Comparing expires_at with the editable device wall clock permits rollback and persistence across restarts.

**Failure example:** A cached optical/hardware authorization expires at 15:00. The phone is offline; its clock is set back before 15:00. A naive expiry comparison continues to allow new capture despite the supposedly expired grant. Reboot can defeat a locally stored uptime comparison if boot identity is not part of the policy.

**Required correction:** Define the authorization record and its authenticated integrity, environment/owner/generation/configuration binding, issue/expiry times, and permitted offline scope. Anchor a bounded lifetime to a server-confirmed time interval and native monotonic elapsed time with phone boot identity. If trustworthy continuity is lost through reboot or clock uncertainty, require online reauthorization. State that revocation cannot be learned instantly while completely offline and define the allowed offline validity policy; the server must recheck current authority at upload/commit.

**Acceptance target:** Device clock forward/backward changes, app restart, phone reboot, expired grant, altered cached payload, and revoked authorization on reconnect must not extend capture permission.

### SEC-007 — The release's research-result display rule conflicts across features

**Severity:** Medium. **Status:** Open.

**Sources:** design.md §1 and §7; android-history Data/API contract; android-settings-accessibility Configuration contract and AND-SET-004; android-guided-check AND-CHECK-007; android-results Customer experience and AND-RES-003.

**Problem:** Design, History, and Settings say this release cannot enable research inference and manipulated research results must be rejected. Guided check permits display of a verified authorized research_estimate, while Results lists Research estimate among supported titles and describes research as server-controlled. These can lead to different treatment of the same valid-shaped server payload on different screens.

**Failure example:** A server fixture or later service returns research_estimate. The completion screen displays its percentage while History rejects the same result as unsupported, even though the installed release is intended to remain measurement-only.

**Required correction:** Freeze one release-level rule: this build rejects/withholds all research_estimate display and emits no non-null probability regardless of remote available flags; a future reviewed release may support the already-defined research schema. Apply that rule to result receipt, cache, historical navigation, export preview, and notifications. Distinguish schema compatibility from enabled product capability.

**Acceptance target:** Feed an otherwise valid-shaped research result to every entry path in this release; none may display its probability or activate local/remote inference through a flag.

### SEC-008 — Profile freeze time conflicts with the guided profile step

**Severity:** Medium. **Status:** Open.

**Sources:** android-profile Data/API contract and AND-PRO-003; android-guided-check AND-CHECK-001/002; android-dashboard AND-DASH-002/003; original HLD §5.

**Problem:** Profile fixes the snapshot at check creation and requires a linked restart to change a bound draft. Guided check places Profile inside the newly created checklist and freezes context at first acquisition. Those are different boundaries. Last-use/exercise/sleep context must also be reviewed anew, but no consistent pre-freeze state is defined.

**Failure example:** A new user starts a check with an empty profile, completes the offered Profile step, then returns. One implementation retains the empty version because the UUID already exists; another replaces it because no acquisition has begun. Both follow one specification, and the stored model context depends on implementation order.

**Required correction:** Select an explicit lifecycle boundary. A practical choice is draft allocation followed by editable context review, then a Begin acquisition transition that freezes profile/context and target time. After that transition require a linked restart for changes. Alternatively move profile/context review before session allocation. Update all three features and source timestamps consistently.

**Acceptance target:** First check with empty profile, edit before first capture, edit after first capture, and simultaneous remote profile revision must produce one documented snapshot-selection behavior.

### SEC-009 — Conflict and privacy job vocabularies disagree

**Severity:** Medium. **Status:** Open.

**Sources:** android-profile Data/API contract and AND-PRO-004; android-offline-sync Engineering contract and AND-SYNC-005; original LLD §9; design.md §8; android-privacy-controls Customer journey item 6; android-data-export Engineering contract.

**Problem:** Profile optimistic conflicts use HTTP 412, while the shared sync policy and upstream LLD use 409 for version conflicts. Privacy UI uses partially_completed but design uses partially_retained; the shared jobs endpoint also returns export-specific expired states without an explicit discriminated job envelope. Independent clients/workers can treat legitimate responses as unknown or retry incorrectly.

**Failure example:** A profile adapter returns 412, but the shared outbox has only a 409 conflict branch. The retained draft receives no review route. A deletion worker returns partially_retained and the privacy UI never recognizes it as a terminal state with retained categories.

**Required correction:** Publish one error/status registry and typed job DTO. Choose 412 for failed If-Match versus 409 for idempotency/state conflict, or explicitly keep 409 consistently; update upstream compatibility notes and every client branch. Choose one partial-deletion enum and distinguish deletion/export jobs by kind with their exact allowed states and transition rules.

**Acceptance target:** Shared response fixtures must exercise profile/snapshot precondition failures, changed-idempotency-body conflicts, partial deletion, expired export, and unknown future codes without inappropriate retries or false success.

### SEC-010 — Mandatory notice updates have no content retrieval contract

**Severity:** Medium. **Status:** Open.

**Sources:** android-onboarding AND-ONB-003 and Data/implementation defaults; design.md §5 GET /v1/app-config; android-settings-accessibility Preference/configuration contract.

**Problem:** A mandatory new notice suspends protected writes and the app must display/acknowledge the new exact content. The shared endpoint only supplies its version/hash; the bundled release contains the old notice. No versioned content endpoint, allowed content URL, or inline verified document is specified. Thus the stale-notice recovery path cannot be implemented without inventing an API and integrity policy.

**Failure example:** The service advances notice v1 to v2 before an app update. An installed client detects the new hash, blocks saves, but has only v1 text. It must either strand account writes or acknowledge unseen v2 text.

**Required correction:** Add bounded versioned notice-content retrieval with an allowed origin, exact digest verification, supported content type/rendering policy, locale/fallback behavior, and offline cache. The acknowledgment must name the actually displayed version. Explicitly exempt authorized export/deletion/sign-out from a notice-write gate as promised by onboarding, without making the acknowledgment itself impossible to submit.

**Acceptance target:** Old installed bundle plus a newer server notice must display the verified new document and recover; a content/hash mismatch must fail without fabricating acknowledgment or blocking the promised privacy escape paths.

### SEC-011 — Native final-window delivery and timing budgets are not yet pinned

**Severity:** Medium. **Status:** Open.

**Sources:** android-reaction-task AND-TASK-002/003/004/005/006; design.md §9; original LLD §6.

**Problem:** The deterministic schedule is detailed, but the exact software onset estimate per platform, inclusive/exclusive deadline boundary, engineering late-frame/dispatch thresholds, and terminal event-drain boundary remain unresolved. Scoring by native event time conflicts with immediate completion if a qualifying final-trial touch is delivered after the deadline callback. Uncalibrated status appropriately limits claims but does not settle the software algorithm.

**Failure example:** A final-trial touch has native timestamp onset+999 ms but is dispatched after the main-thread deadline at 1000 ms. An implementation that emits completion immediately counts omission; one that drains pending native events counts the response. Both can claim native timing, yet they produce different immutable features.

**Required correction:** Pin a versioned engineering timing configuration, selected onset-evidence field on each platform, response boundary/tie rule, bounded late-event acceptance/drain interval, and finalization barrier. Route delayed events to trials using their native timestamps rather than only the currently displayed trial. Record clock-domain conversion and null/invalid behavior for timing faults. These choices remain developmental and do not close physical latency calibration at G-06.

**Acceptance target:** Golden fixtures at exactly the deadline, just before/after it, delayed native dispatch, final-trial cancellation race, and large frame gaps must have one identical documented disposition on Kotlin, Swift, and the reference extractor.

### SEC-012 — In-app workspace switching can leave a native run active

**Severity:** Medium. **Status:** Open.

**Sources:** android-onboarding AND-ONB-002; android-settings-accessibility AND-SET-001; android-guided-check AND-CHECK-005; android-reaction-task AND-TASK-006/007.

**Problem:** Workspace switching offers Keep draft and switch, while native invalidation lists OS focus/background/view detachment. An in-app tab, route, or workspace change may hide a still-mounted native view without causing any of those OS callbacks. The specification does not require the orchestration layer to stop and durably settle the native attempt before changing namespace.

**Failure example:** The user switches to Settings or signs in during a task. The React Native navigator retains the native view mounted and the app's window remains focused. The task continues offscreen and later emits a valid completion into a different visible workspace or into an apparently resumable draft.

**Required correction:** Make active acquisition an explicit navigation guard. Workspace/route changes that hide its view must invoke native cancellation, invalidate the attempt, and commit its terminal disposition in the original namespace before switching. Late events must carry the original namespace/run generation and be rejected after cancellation. Keep draft means retain the interrupted attempt, not suspend/resume its trial timer.

**Acceptance target:** Switch tab, replace route, change workspace, sign out, and open an overlay that obscures stimuli while the native view remains mounted; no hidden run may complete as valid or move into the new account.

### SEC-013 — Demo native taps conflict with the all-synthetic starter contract

**Severity:** Medium. **Status:** Open.

**Sources:** android-onboarding Customer journey item 2; android-dashboard demo copy; android-reaction-task AND-TASK-007; android-guided-check AND-CHECK-001/007; android-offline-sync Customer experience; tools/run_demo.py and tools/spec_validation.py.

**Problem:** Demo copy accurately says sample/sensor values are synthetic while reaction taps are actual practice. The native adapter maps those taps to prototype_sensor. The existing Python run_demo path and its result provenance validation require all demonstration channels to be simulated. Onboarding says demo is local and never queued into an account, while offline sync allows an explicitly approved synthetic project without defining whether that is a separate engineering API fixture or a customer workspace.

**Failure example:** A real native task inside the demo creates mixed source provenance. Reusing the starter validator rejects an otherwise completed demonstration; forcing the task source to simulated misstates how the tap data were obtained. Automatically using a synthetic project upload to fix the rejection can also violate the local-demo notice.

**Required correction:** Define separate all-fictional fixture demonstrations and locally interactive practice sessions. Preserve actual native acquisition provenance and uncalibrated status for real taps, while the enclosing demo/workspace mode independently prevents inference and automatic account upload. Update the mobile/domain validator for this allowed mixed-provenance measurement-only case without weakening the existing all-fictional CLI demo invariant. Limit any cloud synthetic-project test to an explicitly separate engineering path or specify its opt-in UI/data notice; do not silently upload customer demo practice.

**Acceptance target:** Complete a local demo with real native taps, export it locally, and verify accurate mixed provenance, null probability, and zero account upload. The fully synthetic CLI fixture must continue to pass its stricter validator.

### SEC-014 — Alcohol routes are mandatory in a feature but absent from the shared API inventory

**Severity:** Medium. **Status:** Open.

**Sources:** android-alcohol-channel Engineering contract and AND-ALC-002–005; design.md §5 shared endpoint table and §6 snapshot-version boundary; existing contracts/openapi.yaml.

**Problem:** The alcohol feature requires GET/POST /v1/sessions/{session_id}/alcohol with a separate versioned record, but neither the shared design table nor the existing OpenAPI declares the route/envelope. The route's ordering relative to session finalization, generation ownership, correction semantics, and export inclusion also remain unspecified. The UI can remain correctly hardware-gated, but the claimed complete software interface needs one agreed record path.

**Failure example:** A permitted synthetic alcohol fixture reaches an implemented Alcohol screen, but the generated API client has no route; alternatively a developer adds the record into the forbidden cannabinoid enum/v0.1 snapshot to reuse existing persistence.

**Required correction:** Add the explicit separate alcohol DTO/routes to the shared contract with provenance, ownership/generation, idempotency, immutable correction, finalization/linkage, and export/history rules. If no ingestion is intended in this change, revise the feature scope and acceptance ledger to state that only availability/demo UI is delivered; do not leave a mandatory route implied but absent.

**Acceptance target:** A synthetic parent session accepts one authorized fictional alcohol record through the declared route, deduplicates retry, rejects a nonsynthetic provenance mismatch and wrong owner, and preserves a separate mg/L record in detail/export without changing the v0.1 cannabis snapshot.

## Feature coverage ledger

All 20 feature files were reviewed. The list records coverage, not approval or test execution.

| Feature | Review focus and finding links |
|---|---|
| android-onboarding | Notice recovery, isolated workspaces, actual practice provenance: SEC-010, SEC-012, SEC-013 |
| android-sign-in | JWT revocation, account partition and late-response behavior: SEC-002 |
| android-profile | Freeze moment, stale generation, HTTP conflicts: SEC-001, SEC-008, SEC-009 |
| android-dashboard | Single allocation, refresh generations, profile/check boundaries: SEC-008, SEC-013 |
| android-device-pairing | Key trust, signed transcripts, nonce/boot replay and proof propagation: SEC-003 |
| android-guided-check | Capture freeze, offline grants, result capability, cancellation: SEC-006, SEC-007, SEC-008, SEC-012 |
| android-saliva-measurement | Qualifiers, conversion, double-dilution prevention, source attestation: SEC-003 |
| android-eye-capture | Optical gate remains closed, artifact immutability, offline authority: SEC-005, SEC-006 |
| android-heart-rate | PPG provenance, stale/contact handling, one-modality fields: SEC-003 |
| android-ecg-capture | Whole-system gate remains closed, sample units, immutable raw evidence: SEC-005 |
| android-reaction-task | Native event semantics, calibration limits, lifecycle, practice mapping: SEC-011, SEC-012, SEC-013 |
| android-results | Immutable hash linkage, globally disabled inference consistency: SEC-007 |
| android-history | Non-enumerating ownership, cursor context, deleted-generation projection: SEC-001, SEC-007 |
| android-offline-sync | Generation transport, optimistic conflicts, exact queued provenance: SEC-001, SEC-006, SEC-009, SEC-013 |
| android-privacy-controls | Deletion barriers, token validity, job state contract: SEC-001, SEC-002, SEC-009 |
| android-settings-accessibility | Remote-flag boundaries and hidden native-view lifecycle: SEC-007, SEC-012 |
| android-study-enrollment | Revocation at delivery, offline grant time and integrity: SEC-004, SEC-006 |
| android-alcohol-channel | Separate mandatory API contract and immutable lineage: SEC-014 |
| android-data-export | Owner-scoped delivery, raw revocation, immutable source version: SEC-004, SEC-005, SEC-009 |
| android-app-environment | Fixed issuers, versioned storage, restore generations: SEC-001, SEC-002, SEC-005 |

## Preserved strengths and limits

The specifications already separate specimen exposure from impairment, preserve censored/missing quantities, prohibit double dilution correction, use source labels without treating them as validation, isolate PPG from ECG, keep physical optical/electrode work gated, retain immutable results, and reject a local inference toggle. Those protections should remain intact while resolving the findings. The review does not suggest weakening them to make a demonstration appear complete.

Implementation may proceed only after the High findings have an explicit corrected design and the cross-feature ambiguities have a recorded disposition. Later tests must exercise the failure examples; a schema-valid document, strict OpenSpec validation, or successful native build alone does not establish those runtime guarantees.
