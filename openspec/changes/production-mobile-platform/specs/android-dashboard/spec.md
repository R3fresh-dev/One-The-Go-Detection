# Android dashboard and check entry

## Purpose and traceability

Provide a clear home for one guided check, device state, the most recent measurements, and account/demo navigation. The dashboard must communicate observed data availability rather than infer a person's current condition. Upstream: PRD §§4–6, PRD-009/019/020; HLD §§3, 5, 7; full specification APP-001/012/013, HW-002/004, MOD-009/010, OPS-002/005.

## Shared contract authority

The [shared platform contracts](../../shared-contracts.md) are normative for release scope, workspace isolation, authentication, data generations, concurrency, privacy-job states, export selection, context freezing, and active-capture navigation. This feature SHALL follow those contracts; its UI preferences cannot weaken them.

## Customer journey and screen contract

1. **Home:** header product name, active workspace badge, **Profile** action. Heading “A complete check. A clearer record.” Primary card **Start a check** with subtitle “One saliva collection · Guided measurements · One reaction task.” In demo the card instead says **Start demo check** and “Synthetic sample and sensor values; practice reaction task.” The persistent scope line is “Measurement-only release.” No diagnostic score, traffic-light safety rating, countdown to sobriety, or estimated clearance rate appears.
2. **Readiness:** four labeled rows/cards: **Reader**, **Profile**, **Capture availability**, **Sync**. Unknown measurements and device battery are shown as unavailable, never zero. **Connect reader** enters device setup; **Review profile** opens profile; **View availability** explains capability-specific reasons; **Sync details** shows queue state without raw payloads.
3. **Open draft:** a separate card shows original start time, completed steps, workspace, and **Continue check** / **Discard draft**. If a new check is requested while one exists, show **Continue existing check** or **Start a separate check**. The latter closes/retains the old attempt according to the session workflow instead of overwriting it.
4. **Alcohol measurement:** a separate Home row labeled **Alcohol measurement · Hardware required** enters the alcohol feature's availability/instructions screen. It remains reachable when sampling is unavailable and never infers an alcohol value from the reader's PPG capability.
5. **Latest check:** heading “Latest check”, absolute collection date/time with local timezone, status, source badges, and **View measurements**. A pending/canceled/invalid check uses its actual state and does not display invented normal values. **View all checks** opens History. With no records, show “Your completed checks will appear here.”
6. **Navigation:** persistent tabs **Home**, **Check**, **History**, **Settings**. Device and profile are nested routes with a Back action. Selecting Check enters the same start/resume decision as the primary CTA; it does not independently allocate a second session.

## Data and API contract

Home consumes `GET /v1/app-config` for environment/release/public capability definitions, `GET /v1/me/capabilities` for server-derived account actions and gate reasons, `GET /v1/me/profile`, and `GET /v1/sessions?limit=3`. Guest demo uses a local isolated repository. The app must not send a subject/role override in these requests. Display counts come from server totals when supplied or are labeled “On this device”; the number of cached rows must not be called an all-time account total.

The presentation model contains workspace ID, environment label, scope, local draft summary, current device connection state, capture capability state, sync state, recent rows, and `last_successful_refresh_at`. A device summary includes current boot identity and latest observed timestamp; last-known battery values are explicitly dated and never represented as live while disconnected. Clinical/model gates remain server policy and cannot be enabled by a UI toggle. Public configuration is fetched on foreground entry; authenticated capabilities refresh after login, foreground, or a capability error. Cached capabilities are explanatory only for qualified capture. Every qualified start in this release requires a fresh online server authorization; offline native uncalibrated practice and synthetic acquisition remain available under their explicit sources.

### AND-DASH-001/002/003/005/006/007 integration resolution

The release SHALL keep `inference_available=false`; a server capability or cached record cannot change that constant. **Start check** allocates and durably freezes one context with `target_at=created_at` in the same creation transaction. A resumed draft shows that frozen profile/context revision even if a newer profile exists. A new/replacement check gets a new identity, target time, and explicit lineage. Completion first uses **Save on this device**; eligible account records then expose a separate **Upload check** confirmation. Guest demo never uploads, and newly created authenticated synthetic fixtures are limited to local/QA. Automatic reconnect work follows the queued-upload retry preference and never starts a disabled retry.

Home SHALL expose the Alcohol measurement availability route alongside the existing Reader/Profile routes. Every route change during active native acquisition first ends and invalidates/cancels that attempt; a following draft decision never offers mid-run resume. Stale generation 410 quarantines corresponding queue items and shows the reset state; it is not an ordinary network error or a successful synchronization.

## ADDED Requirements

### Requirement: AND-DASH-001 Honest scope and provenance

The dashboard SHALL show active workspace, measurement-only release scope, and synthetic provenance where applicable. It SHALL identify latest results by their acquisition time and MUST NOT present an earlier check as a current assessment of the user. Missing channels SHALL remain unavailable.

#### Scenario: dash-demo-home
- **GIVEN** an isolated demo workspace with a synthetic check
- **WHEN** Home is displayed
- **THEN** the demo badge and synthetic source description remain visible and no intoxication percentage appears.

#### Scenario: dash-old-check
- **GIVEN** the latest check was collected yesterday
- **WHEN** the dashboard opens today
- **THEN** its collection date/time is shown and the card does not claim to represent the user's present state.

### Requirement: AND-DASH-002 Single check entry and authorization

Start/Check-tab actions SHALL share one session-allocation path with an idempotency key and an in-flight guard. Account actions SHALL respect server capabilities, notice requirements, and channel gates. Account login or a locally editable capability flag MUST NOT enable human research capture or inference. Demo entry SHALL remain available without account or hardware.

#### Scenario: dash-double-start-tap
- **GIVEN** no active draft and an enabled start action
- **WHEN** two rapid taps occur before navigation completes
- **THEN** one logical session is created and both navigation events resolve to that session.

#### Scenario: dash-gated-capture
- **GIVEN** pupil capture is unavailable because its approved protocol is not configured
- **WHEN** View availability is selected
- **THEN** the app explains that channel's unavailability and does not open the camera/flash or replace it with a fabricated account measurement.

#### Scenario: dash-frozen-profile-at-creation
- **GIVEN** profile revision P1 is selected when Start check is pressed
- **WHEN** P2 arrives before the first acquisition
- **THEN** the draft retains P1, target_at equals its created_at, and its review identifies P1.

### Requirement: AND-DASH-003 Explicit draft resumption

The dashboard SHALL display a resumable draft's identity, start time, and step completion from persisted session state. An interrupted native task SHALL remain interrupted/invalid according to the task spec and MUST NOT resume at an assumed trial or appear completed. A separate check SHALL have a new session/attempt identity and preserve prior records.

#### Scenario: dash-resume-saliva-draft
- **GIVEN** a draft with one retained saliva attempt and no completed task
- **WHEN** Continue check is selected
- **THEN** the same draft opens at its next eligible step with the original sample identity.

#### Scenario: dash-task-interruption-return
- **GIVEN** the app was backgrounded during the native task
- **WHEN** Home is opened and the draft resumed
- **THEN** the interruption is shown and no task completion is inferred from elapsed wall time.

### Requirement: AND-DASH-004 Current device state

Device readiness SHALL derive from the active connection and capability handshake, not a saved device name. Disconnect, reboot, permission denial, and unsupported firmware SHALL each produce a distinct state and actionable route. A disconnected device SHALL show “Not connected”; stale measurements/battery SHALL be dated or hidden.

#### Scenario: dash-reader-disconnect
- **GIVEN** a connected reader with a recent battery value
- **WHEN** its BLE link drops
- **THEN** Home changes to Not connected and the battery value cannot remain labeled live.

#### Scenario: dash-reader-reboot
- **GIVEN** a reader reconnects with a different boot identity
- **WHEN** readiness is recalculated
- **THEN** unfinished capture readiness resets and old monotonic readings are not presented as belonging to the new boot.

### Requirement: AND-DASH-005 Offline availability and synchronization truth

The dashboard SHALL separate local persistence, upload pending, server accepted, and result pending states. Offline local/draft/demo operation SHALL show **Offline · Saved on this device** where true. It MUST NOT label an unacknowledged upload synchronized or fabricate a result after a timeout. Manual refresh SHALL retain valid cached content and show a recoverable error if refresh fails.

#### Scenario: dash-offline-check-list
- **GIVEN** cached permitted history and no network
- **WHEN** Home opens
- **THEN** cached rows remain available with an offline indicator and the latest refresh time.

#### Scenario: dash-lost-finalization-response
- **GIVEN** a session finalization request timed out
- **WHEN** Home renders its recent row
- **THEN** the row remains pending until the server is reconciled using the original identity/idempotency key.

#### Scenario: dash-reconnect-respects-manual-retry
- **GIVEN** an explicitly queued account check has automatic retries disabled
- **WHEN** the network reconnects
- **THEN** Home shows the waiting item and manual Upload/Retry action without beginning a network mutation.

### Requirement: AND-DASH-006 Refresh and workspace race control

Refresh results SHALL be applied only to the workspace/account generation that initiated them. Stale responses, canceled requests, and older revisions SHALL not overwrite newer state. Backgrounding SHALL stop unnecessary polling; foregrounding SHALL trigger bounded reconciliation rather than multiple overlapping loops.

#### Scenario: dash-account-switch-race
- **GIVEN** an account-A refresh is in flight
- **WHEN** the user switches to demo before the response returns
- **THEN** A's response is discarded and no account data appears in demo.

#### Scenario: dash-out-of-order-refresh
- **GIVEN** refresh B returns a newer session revision before refresh A
- **WHEN** A completes later
- **THEN** the displayed revision does not regress.

### Requirement: AND-DASH-007 Accessible navigation and iOS parity

The dashboard SHALL offer descriptive tab roles/selected states, logical heading order, 48 dp Android/44 pt iOS minimum targets, high-contrast status text independent of color, and usable layout at 200% text scale. Screen-reader focus SHALL move to the destination heading after navigation. iOS SHALL expose equivalent start/resume, sources, timestamps, offline states, and capability behavior through its native accessibility APIs.

#### Scenario: dash-accessible-status
- **GIVEN** TalkBack is enabled and the reader disconnects
- **WHEN** the status changes
- **THEN** “Reader, not connected” is announced once without an unbounded repeating alert.

#### Scenario: dash-ios-check-tab
- **GIVEN** an existing draft on iOS
- **WHEN** the Check tab is selected using VoiceOver
- **THEN** the same draft decision used by the primary CTA appears with its correct focus and no duplicate session allocation.

#### Scenario: dash-alcohol-route-is-reachable
- **GIVEN** no alcohol instrument or approved configuration exists
- **WHEN** the user selects Alcohol measurement on Home
- **THEN** the alcohol availability screen opens with Hardware required, its requirements action, and working Back navigation.

## Acceptance evidence

Required evidence: Android/iOS home empty/draft/complete/error screenshots; double-start idempotency test; offline/pending-result tests; simulated BLE disconnect/reboot test; stale-response/account-switch tests; text-scale and screen-reader checks. Public dashboard availability does not demonstrate analytical validity, clinical approval, or a trained model.
