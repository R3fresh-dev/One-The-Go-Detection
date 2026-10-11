# Android privacy controls, local clearing, and deletion

## Purpose and traceability

Give users explicit control over local storage, account synchronization, exports, and deletion without conflating these operations with study consent. Upstream: PRD §§5–6; HLD §8; full specification SEC-001/003/004/005/006/007, OPS-002/003/005, MOD-015, VAL-001, DOC-001. Export implementation belongs to [android-data-export](../android-data-export/spec.md); this feature owns its privacy entry point only.

## Shared contract authority

The [shared platform contracts](../../shared-contracts.md) are normative for release scope, workspace isolation, authentication, data generations, concurrency, privacy-job states, export selection, context freezing, and active-capture navigation. This feature SHALL follow those contracts; its UI preferences cannot weaken them.

## Customer journey and screen contract

1. **Privacy & data:** show active workspace/account, storage description, synchronization state, current notice version, retention policy identifier, and four sections: **Upload preferences**, **Export your data**, **Clear this device**, **Delete account data**. Demo replaces account controls with an explanation and **Clear demo records**; it never offers a misleading cloud-delete button.
2. **Upload preferences:** **Retry queued uploads automatically** defaults off on a new installation/account partition. A check enters the upload queue only through its explicit **Upload check** action; account profile Save is likewise an explicit account-write action. Enabling the retry preference shows “Retry uploads you have already requested?” with CTAs **Enable automatic retries / Keep manual retries**. It never queues new checks or grants raw-media/study authorization. Disabling stops automatic retry work and says “Uploads you already requested remain queued. You can retry them manually. Existing account records remain.” Explicit new upload actions remain available when automatic retries are off.
3. **Export:** **Export my data** enters the dedicated export scope/review screen; no file is created or shared solely by opening Privacy.
4. **Clear this device:** sheet names workspace, record count, unsynchronized count, and cache categories. Account wording is “Remove this account's cached records from this device. Records already saved to your account will remain.” Demo wording states that demo records are local. **Clear local records / Cancel**; account pending unsynchronized records require an additional explicit **Remove unsynced records** choice. Clearing does not silently sign out or trigger server deletion.
5. **Delete account data:** choose **Delete my profile and check data** (account remains) or **Delete my account and its data**. Review identifies the exact scope, configured retention exceptions, expected processing/status semantics, and synchronization lock. CTAs **Continue to verify identity / Cancel**; after reauthentication, explicit **Request deletion** submits `confirmation:true`. No request occurs before this final choice.
6. **Deletion status:** display request ID, submission time, scope, `pending|running|completed|failed|partially_retained`, and any retained categories/reasons from the server. The response discriminator is `kind:"deletion"`. Copy begins “Deletion requested”; completed shows “Deletion completed under the displayed policy”, partially_retained shows “Deletion completed with the listed retained records”, and failed reports the incomplete operation without a completion claim. **Check status** retries a status read; **Back** does not cancel accepted work.

## Data, API, and policy contract

`POST /v1/privacy/deletion-requests` accepts `{scope:"all_data"|"account",confirmation:true}` with current access token, recent reauthentication, `X-Data-Generation`, and an idempotency key. Owner is derived from verified identity; body-supplied owner/study/role fields are rejected. Response 202 includes job ID, scope, policy version, accepted time, and status location. `GET /v1/privacy/jobs/{job_id}` returns only an owned job's status and permitted summary. A local confirmation alone cannot mark remote deletion completed. If credentials become unusable before a terminal status is read, the app preserves only the minimal accepted-request receipt allowed by policy and says completion has not been confirmed on this device.

Account reauthentication must be no older than five minutes when deletion is requested (engineering security default). Reauthentication uses the hosted OAuth session with the required reauth request; the server verifies freshness from signed access-token auth_time and does not trust a client timestamp; refresh alone does not reset authentication freshness. `all_data` includes profile revisions, checks, raw artifacts if any, exports, and derived per-user data; account identity and explicitly enumerated security/deletion receipts may remain per the displayed policy. `account` also removes the application account and schedules issuer account removal according to the platform workflow. Retention exceptions must be concrete server-returned categories, policy IDs, and expiry/reason; the UI cannot promise complete physical erasure while an exception remains. Unresolved human-data policy leaves human-data capture unavailable.

An accepted deletion atomically increments the data generation and establishes a server write lock for its scope; pending local operations are canceled or quarantined, and all devices reconcile tombstones before further writes. A stale upload cannot recreate deleted records. A request timeout retries the same idempotency key. Accepted deletion cannot be canceled from this release; that fact appears before submission. The app performs no advertising tracking or third-party analytics containing profile/measurement content. Privacy actions emit only redacted event metadata needed for audit.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-PRIV-001 detailed contract

The app SHALL display local storage, requested account uploads, automatic retry, raw-media upload, and research participation as separate controls/capabilities. An account check SHALL queue only after its explicit Upload check action and current notice acknowledgment; an account profile Save is an explicit account-write action. Automatic retries SHALL apply only to already requested operations. These actions MUST NOT create study consent, raw-artifact authorization, model-training permission, or enrollment.

### AND-PRIV-001/003/004/005/006 integration resolution

Privacy/withdrawal requests already explicitly accepted for submission may retry their original intent to reconcile an unknown outcome even when automatic profile/check retries are off; the confirmation explains that durable intent. Guest demo SHALL never upload. An authenticated synthetic fixture is separately created under a local/QA account; it is not a guest-data import. A check first uses **Save on this device** and only an explicit **Upload check** action queues it. Automatic retries apply only to already requested operations while the preference is enabled; reconnection alone cannot override the preference. Profile Save is its own explicit write. Neither notice acceptance nor upload/retry consent enables raw media, study participation, or inference.

All protected writes SHALL carry `X-Data-Generation`. Missing If-Match on an applicable mutable resource returns 428, stale ETag returns 412, state/idempotency conflict returns 409, and stale generation returns 410. Accepted deletion increments and locks generation atomically; clients quarantine older queue work and invalidate old read/export responses. They never rewrite a stale payload with the new generation. Exact replay of an already accepted idempotent deletion follows the shared replay rule and returns its existing job. After `all_data` completes, **Start a new empty workspace** calls `POST /v1/me/data-generation/acknowledgments` with the new current generation, explicit confirmation, and its own idempotency key before new protected writes can resume. Account deletion never offers that continuation.

Privacy jobs SHALL use `kind: export|deletion`. Shared common states are pending, running, completed, and failed; expired is export-only and partially_retained is deletion-only. These exact kind/state pairs are validated before display; there is no partially_completed state. Deletion status uses the shared version 1.0.0 PrivacyJob DTO: kind, job_id, scope, data_generation, accepted_at, started_at/completed_at where present, retained_categories, policy_version, failure_code, attempt_count, and allowed_actions. The original-generation request and accepted-generation minimal receipt follow the shared deletion protocol; fields are not invented in the job DTO. A partially_retained status is terminal policy-aware completion, not permission to retry erasure of retained records. Export downloads use the authenticated same-origin `/v1/privacy/jobs/{job_id}/download` gateway. The gateway checks current owner/generation/policy before stream authorization; a copied path grants no authority. Revocation before stream authorization prevents a new stream, while already-authorized/shared bytes cannot be recalled. The notice states that limit without implying a job-status check alone controls delivery.

### AND-PRIV-004 consolidated detailed contract

Deletion SHALL be represented as an asynchronous job with accepted/running/terminal states and explicit policy exceptions. A timeout, app closure, local clear, or sign-out MUST NOT be described as successful remote erasure. Retrying the accepted request SHALL reuse the same idempotency key and return the same logical job. A failed job SHALL expose a reference ID and support/retry path; partially_retained SHALL list policy-authorized retained records and SHALL NOT imply a failed or retriable erase of those records.

## ADDED Requirements

### Requirement: AND-PRIV-001 Separate storage and upload choices

The app SHALL display local storage, requested account uploads, automatic retry, raw-media upload, and research participation as separate controls/capabilities. The implementation SHALL also satisfy the AND-PRIV-001 detailed contract above.

#### Scenario: priv-enable-queued-upload-retries
- **GIVEN** a signed-in account with one explicitly queued check and another unqueued local check
- **WHEN** the user confirms Enable automatic retries
- **THEN** only the already queued check is eligible for automatic retry and the other check, raw media, and research data remain unqueued.

#### Scenario: priv-disable-during-upload
- **GIVEN** a permitted upload is in flight and more operations are queued
- **WHEN** the user disables automatic retries
- **THEN** no new automatic retry starts, the in-flight outcome is reconciled honestly, and the UI does not claim previously accepted data was deleted.

### Requirement: AND-PRIV-002 Scoped and explicit local clearing

Local clearing SHALL remove only the selected workspace's approved local records, related temporary exports, and queue entries after the displayed confirmation. It MUST preserve other account/demo namespaces and MUST NOT call a remote deletion endpoint. Unsynchronized data loss SHALL require a count-specific additional choice; Cancel SHALL perform no deletion.

#### Scenario: priv-clear-demo-only
- **GIVEN** demo and account caches coexist
- **WHEN** Clear demo records is confirmed
- **THEN** demo records disappear, account records remain, and no cloud deletion request is made.

#### Scenario: priv-cancel-unsynced-clear
- **GIVEN** three account records are unsynchronized
- **WHEN** the warning shows three and the user selects Cancel
- **THEN** all records and queue entries remain unchanged.

### Requirement: AND-PRIV-003 Owned, reauthenticated cloud deletion

Cloud/account deletion SHALL require the exact reviewed scope, explicit final confirmation, recent trusted reauthentication, and server ownership enforcement. A job ID or client-supplied account identifier MUST NOT authorize deletion or status access. Failed reauthentication SHALL return to review without submitting a request.

#### Scenario: priv-valid-data-deletion
- **GIVEN** an owned account, current policy review, and reauthentication within five minutes
- **WHEN** the user confirms deletion of profile and check data
- **THEN** one all_data job is accepted and the account identity is retained according to the displayed scope.

#### Scenario: priv-forged-owner-or-stale-auth
- **GIVEN** a deletion body contains another owner's ID or authentication is stale
- **WHEN** it is submitted
- **THEN** the server rejects it and no deletion job affects another account or bypasses reauthentication.

### Requirement: AND-PRIV-004 Honest asynchronous completion

The implementation SHALL satisfy the AND-PRIV-004 consolidated detailed contract and the shared platform contracts, including their exact states, authorization, persistence, and failure behavior.

#### Scenario: priv-deletion-response-lost
- **GIVEN** the server accepted a deletion but its response was lost
- **WHEN** the app retries with the same key and scope
- **THEN** the same job is returned and the UI remains requested/running until actual completion is reported.

#### Scenario: priv-retention-exception
- **GIVEN** a kind=deletion job reports partially_retained for a named audit category retained until a stated date
- **WHEN** status is shown
- **THEN** that exception remains visible and the app does not claim every copy was erased.

#### Scenario: priv-job-kind-state-discriminator
- **GIVEN** a completed export and a partially_retained deletion are returned by the shared job route
- **WHEN** Privacy routes each response
- **THEN** export-only expired is never interpreted as deletion state; partially_retained displays the listed exception and no partially_completed fallback is created.

### Requirement: AND-PRIV-005 Prevent resurrection and cross-device writes

Acceptance of deletion SHALL pause matching local queue work, invalidate in-flight response application, and establish server-side write blocking/tombstones for the affected generation. Stale devices SHALL reconcile that state before retrying writes. Post-deletion account continuation, when permitted, SHALL start with a new data generation rather than replay old queued records.

#### Scenario: priv-offline-device-reconnects
- **GIVEN** device A completed all_data deletion while device B held old queued records offline
- **WHEN** B reconnects
- **THEN** the server returns 410 for new stale-generation mutations and B quarantines their original operations instead of rebinding or restoring them.

#### Scenario: priv-late-fetch-after-clear
- **GIVEN** an old-history fetch is in flight when account deletion is accepted
- **WHEN** the fetch returns
- **THEN** its payload cannot recreate deleted local content.

#### Scenario: priv-explicit-generation-reset-required
- **GIVEN** an all_data deletion finished and the account remains usable
- **WHEN** the user returns to Profile or Check before acknowledging the new generation
- **THEN** old queued records remain quarantined and new protected writes stay blocked until Start a new empty workspace is explicitly confirmed.

#### Scenario: priv-deletion-replay-does-not-create-new-job
- **GIVEN** a deletion was accepted and advanced generation but its response was lost
- **WHEN** the exact original idempotent request is replayed under the shared replay policy
- **THEN** the original job is returned; a distinct mutation carrying the old generation receives 410 and is quarantined.

### Requirement: AND-PRIV-006 Clear retention and protected temporary data

The privacy view SHALL show the actual deployed retention policy and data categories. Raw media capture/upload SHALL remain unavailable when policy or protocol authorization is absent. Export temporary files SHALL follow the dedicated export cleanup policy; no raw recording, token, or profile field SHALL enter diagnostics, clipboard summaries, crash logs, or repository fixtures.

#### Scenario: priv-unconfigured-retention
- **GIVEN** production has no approved policy for raw eye recordings
- **WHEN** the privacy and capture availability screens load
- **THEN** raw recording is unavailable and no generic consent checkbox enables it.

#### Scenario: priv-redacted-deletion-log
- **GIVEN** a deletion request fails validation
- **WHEN** the event is logged
- **THEN** logs include a redacted operation/request reference and reason category without tokens, profile values, or measurements.

### Requirement: AND-PRIV-007 Accessible controls and iOS parity

Privacy switches SHALL announce current state, exact retry scope, and pending operations. Destructive sheets SHALL provide clear headings, Cancel as an independently reachable action, and focus restoration on dismissal. iOS SHALL provide the same in-app export/deletion/local-clear capabilities, scope review, authentication freshness, job status, and anti-resurrection behavior using VoiceOver and native presentation conventions.

#### Scenario: priv-accessible-confirmation
- **GIVEN** TalkBack and 200% text scaling
- **WHEN** the deletion review opens
- **THEN** scope, retention exceptions, and both final/cancel actions are reachable before confirmation can occur.

#### Scenario: priv-ios-account-deletion
- **GIVEN** an authenticated iOS account
- **WHEN** the user completes in-app account deletion review and reauthentication
- **THEN** the same scoped asynchronous job is requested and its completion status is represented without sending the user to an unrelated website.

## Acceptance evidence

Required evidence: explicit-upload/queued-retry/no-research trace; local-clear isolation/cancel; recent-auth and ownership rejection; lost-response idempotency; running/failed/partial/completed screenshots; deletion/late-response and cross-device queue tests; temporary-file cleanup; redacted logs; Android/iOS accessibility checks. The implementation must record actual retention/backup cleanup limitations; an API 202 alone is not deletion evidence.
