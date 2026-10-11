# Android onboarding and workspace selection

## Purpose and traceability

Give a new user a truthful first-run introduction and a usable account-free demonstration. This feature prepares the app; it does not enroll a participant, authorize optical exposure, or activate inference. Upstream: PRD §§3–6, PRD-003/009/020; HLD §§3, 4.3, 8; full specification APP-001/012/013/014, HW-002, SEC-003/005, MOD-009, DOC-001.

## Shared contract authority

The [shared platform contracts](../../shared-contracts.md) are normative for release scope, workspace isolation, authentication, data generations, concurrency, privacy-job states, export selection, context freezing, and active-capture navigation. This feature SHALL follow those contracts; its UI preferences cannot weaken them.

## Customer journey and screen contract

1. **Welcome:** product wordmark, heading “Your measurements, in one place”, body “Collect a saliva result, eye and pulse measurements, and one reaction task. This release reports measurements only.” Primary CTA **Explore the demo**; secondary **Sign in**; links **Privacy** and **About this release**. No sensor permission is requested here.
2. **Demo introduction:** heading “Try a complete check”, three rows “One sample”, “Guided measurements”, “One reaction task”, and persistent text “Demo sample and sensor values are synthetic. Reaction taps are a practice measurement.” CTA **Start demo**; **Back** returns without changing workspace.
3. **Data notice:** current notice version and digest are bundled with the release; scrollable readable content explains local demo storage, authenticated synchronization, retention, exports, and deletion separately. CTA **Continue** follows an unchecked acknowledgment labeled “I have read how this app handles data.” This is a notice acknowledgment, not study consent. **Back** discards an unchecked draft. Notice content is available again in Settings.
4. **Dashboard:** starts an isolated demo workspace or returns to the signed-in account after authentication. A visible **Demo** or **Account** badge identifies the active workspace. QA/local builds also identify their environment. Switching workspace is explicit.

Entry: first launch, selected **Explore demo**, or a new mandatory notice version. Exit: dashboard, sign-in browser flow, or OS dismissal. Onboarding stores only notice/version and workspace preferences until the user enters profile or check data. Android Back traverses introduction → welcome; it never exits a running native task through an onboarding route.

## Data and implementation defaults

Local preference object: `{schema_version, onboarding_completed_at, notice_version, notice_digest, acknowledged_at, selected_workspace: "demo"|"account"}`. UTC timestamps are generated at acknowledgment, never from notice publication time. Account acknowledgment is submitted idempotently to `POST /v1/me/acknowledgments` with `{notice_version, notice_digest, acknowledged_at}` and the authenticated account's current `X-Data-Generation` after authentication; the server verifies the current notice version/digest and returns its accepted version, receipt ID, and server `received_at` separately from client `acknowledged_at`. An acknowledgment receipt does not contain a study ID or consent grant. The shared platform contract owns endpoint envelopes and authentication.

Production, QA, and local configurations are build-time allowlists. Local development uses the isolated local issuer and LocalStack-backed services; production never accepts a local token, local notice receipt, or development endpoint override. Release notices and local demo assets must work without connectivity. Values and retention claims displayed by the notice must match the running configuration; an unset participant-data retention policy leaves participant capture unavailable.

### AND-ONB-001/002/003 integration resolution

This release SHALL keep `inference_available=false` independent of signed-in identity, configuration, or a schema-valid research response. The guest demo SHALL never upload. Authenticated synthetic fixtures are separate newly created account-owned records, permitted only in local/QA; they are not migrated guest records. All checks first use **Save on this device**. Only an eligible account check can subsequently enter the explicit **Upload check** confirmation. Reconnection and notice acknowledgment do not queue a check or enable automatic retries. App appearance preferences use the single Settings preference contract, not a second onboarding motion override.

### AND-ONB-002 consolidated detailed contract

The app SHALL maintain separate demo and account storage namespaces. Entering or leaving demo MUST NOT merge its checks, profile, pending operations, or device identity into the account. A switch during an inactive check SHALL require **Keep draft and switch** or **Stay in check**, and the draft SHALL remain in its original namespace. Active native acquisition SHALL end and record its invalid/canceled attempt before a route change or modal; any later Stay choice stays on the ended check and never resumes that run.

### AND-ONB-003 notice retrieval resolution

The app SHALL obtain version/hash and a same-origin content route from `GET /v1/app-config`, then retrieve `GET /v1/notices/{version}` as bounded English plain text of at most 64 KiB. SHA-256 covers the exact UTF-8 text bytes. A version/digest mismatch blocks acknowledgment and new protected writes, without blocking authorized history/export/deletion/withdrawal/sign-out. No remote HTML, script, arbitrary redirect, or unverified text is rendered. Bundled demo notice remains available offline. The acknowledgment itself is exempt from the old-notice gate and still uses current account generation.

## ADDED Requirements

### Requirement: AND-ONB-001 Accurate first-run scope

The Android app SHALL display the measurement-only scope before either workspace is entered and SHALL keep research/model authorization independent of onboarding completion. It MUST NOT promise detection accuracy, intoxication classification, or driving clearance in introductory copy.

#### Scenario: onb-first-launch-demo
- **GIVEN** a fresh installation without preferences
- **WHEN** the user selects Explore the demo
- **THEN** the introduction identifies synthetic sample/sensor values and does not display a probability or create a research enrollment.

#### Scenario: onb-signed-in-still-measurement-only
- **GIVEN** an authenticated account with no study authorization
- **WHEN** onboarding completes
- **THEN** the dashboard shows measurement-only availability and no study capability is inferred from the account or notice receipt.

#### Scenario: onb-research-configuration-cannot-change-release
- **GIVEN** an authenticated account and a valid-looking research manifest
- **WHEN** onboarding or public configuration reports research availability
- **THEN** the release retains inference_available=false and displays no probability or research-estimate capability.

### Requirement: AND-ONB-002 Explicit workspace isolation

The implementation SHALL satisfy the AND-ONB-002 consolidated detailed contract and the shared platform contracts, including their exact states, authorization, persistence, and failure behavior.

#### Scenario: onb-demo-does-not-upload
- **GIVEN** a completed demo check and a subsequently authenticated account
- **WHEN** the user opens the account workspace
- **THEN** demo history is absent from account history and no upload request for the demo check is enqueued.

#### Scenario: onb-cancel-workspace-switch
- **GIVEN** an unfinished demo check
- **WHEN** the user selects Sign in and then Stay in check
- **THEN** the check remains visible with unchanged identity and no authentication browser is opened; if a native run had already ended to leave capture, it remains ended with that fact displayed.

#### Scenario: onb-guest-demo-never-has-upload-path
- **GIVEN** a guest demo check and an authenticated local/QA synthetic project both exist
- **WHEN** the user opens the guest check, signs in, or reconnects
- **THEN** the guest check remains local and has no upload action; a separate account-owned synthetic fixture requires its own creation and upload choice.

### Requirement: AND-ONB-003 Versioned notice acknowledgment

The app SHALL require an affirmative notice acknowledgment with the exact displayed version/digest before persisting newly entered account profile data or enabling account synchronization. It SHALL keep Privacy readable without acknowledgment. A new mandatory notice version SHALL suspend new protected writes until acknowledged, while allowing authorized history, export, deletion, withdrawal, and sign-out.

#### Scenario: onb-notice-accepted-once
- **GIVEN** the current notice is visible and its checkbox is initially unchecked
- **WHEN** the user checks it and selects Continue
- **THEN** one dated receipt is saved, the dashboard opens, and repeating the submission creates no duplicate receipt.

#### Scenario: onb-stale-notice-write
- **GIVEN** the server requires a newer notice than the bundled accepted version
- **WHEN** the app attempts an account write
- **THEN** the write remains pending, the app offers the newer notice, and neither a fabricated acknowledgment nor a research-consent record is sent.

### Requirement: AND-ONB-004 Permission timing and offline entry

Onboarding SHALL request no camera, microphone, Bluetooth, location, photo-library, or notification permission. Demo assets and the bundled data notice SHALL be usable offline. A failed sign-in SHALL offer **Return to welcome** and **Explore demo** without substituting demo records into an account screen.

#### Scenario: onb-airplane-mode-demo
- **GIVEN** the phone is offline on first launch
- **WHEN** the user completes demo onboarding
- **THEN** the dashboard and synthetic check are usable and the UI describes their local state.

#### Scenario: onb-no-permission-prompts
- **GIVEN** every OS permission is denied
- **WHEN** all onboarding screens are traversed
- **THEN** no permission dialog appears and onboarding is not blocked by those denials.

### Requirement: AND-ONB-005 Restart-safe progression

The app SHALL commit acknowledgment and onboarding state atomically before navigating. A crash before that commit SHALL return to the unacknowledged screen; a crash after it SHALL open the selected workspace without generating a second acknowledgment. Unfinished authentication SHALL never be restored as signed in merely because the browser opened.

#### Scenario: onb-kill-before-commit
- **GIVEN** acknowledgment persistence has not completed
- **WHEN** the process is terminated and relaunched
- **THEN** the notice remains unacknowledged and no account write is sent.

#### Scenario: onb-kill-after-commit
- **GIVEN** the acknowledgment transaction completed before process termination
- **WHEN** the app relaunches
- **THEN** the chosen workspace opens with the existing receipt and no duplicate onboarding event.

### Requirement: AND-ONB-006 Accessible introduction and parity

All onboarding controls SHALL have descriptive accessibility labels, logical heading/focus order, at least 48 dp Android touch targets, support for 200% text scaling without clipped actions, and sufficient text/control contrast. Animation SHALL stop under reduced-motion preference. iOS SHALL provide the same choices, copy, state isolation, and receipt semantics using VoiceOver, Dynamic Type, safe areas, and at least 44 pt targets.

#### Scenario: onb-talkback-and-large-text
- **GIVEN** TalkBack and 200% font scaling are enabled on a 360 dp-wide Android screen
- **WHEN** the user traverses welcome and the notice
- **THEN** each action is reachable, its role/label is announced, and scrolling exposes the entire notice and Continue control.

#### Scenario: onb-ios-parity
- **GIVEN** a fresh iOS installation with Reduce Motion enabled
- **WHEN** demo onboarding completes using VoiceOver
- **THEN** the same workspace and notice states are stored without required animation or a camera/Bluetooth prompt.

## Acceptance evidence

Required artifacts: Android/iOS first-run and returning-run UI tests; offline demo test; network assertion showing zero onboarding sensor/research calls; crash-boundary persistence tests; version-mismatch API test; screenshots at standard and 200% text size; TalkBack/VoiceOver manual checklist. A specification, screenshot, or passing onboarding test is not evidence that G-01–G-14 scientific/product gates have closed.
