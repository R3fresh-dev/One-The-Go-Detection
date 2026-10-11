# Android settings, support diagnostics, and accessibility

## Purpose and traceability

Provide discoverable app controls, honest capability information, accessible navigation, and useful redacted diagnostics on Android and iOS. Settings may configure software behavior; they cannot activate clinical claims or authorize sensor protocols. The release invariant is `inference_available=false`. Upstream: PRD §§4–6; HLD §§3, 4.3, 8; full specification APP-008/012/013/014, HW-008, MOD-008/009/010, SEC-003/004/006, DOC-001.

## Shared contract authority

The [shared platform contracts](../../shared-contracts.md) are normative for release scope, workspace isolation, authentication, data generations, concurrency, privacy-job states, export selection, context freezing, and active-capture navigation. This feature SHALL follow those contracts; its UI preferences cannot weaken them.

## Customer journey and screen contract

1. **Settings:** grouped sections **Your workspace** (Profile, Reader, Research access, Sign in/Sign out, Switch to demo/account), **Privacy & data** (privacy, export, local clear, deletion), **Appearance & access** (theme, reduced motion, units preference), **App permissions** (Camera, Bluetooth; each with current OS status and **Open app settings**), and **About** (version/build/environment, measurement-only scope, capability status, notices/licenses, diagnostics).
2. **Appearance:** Theme choices **Use device setting / Light / Dark**. Reduced motion choices **Use device setting / Reduce motion**. Display-units preference **Metric / US customary** affects editable profile presentation and supported descriptive values only; original assay units and canonical stored values remain preserved. The first release's UI language is English; dates/numbers follow supported system locale formatting without changing stored values.
3. **Permissions:** each row explains the feature that needs the permission. **Open app settings** navigates to the OS app settings, then rechecks status on foreground. No permission is requested simply by viewing Settings. Microphone, location, photo library, and notifications are absent unless a separately implemented feature genuinely requires them.
4. **About this release:** show application version, build number, Android/iOS platform version, local/QA/production label, and “Measurement-only release”. **Available measurements** shows server capability states and reasons. It does not offer a clinical-model toggle or arbitrary phone-flash configuration.
5. **Help & diagnostics:** concise setup/troubleshooting topics for reader connection, offline records, unavailable captures, export, and deletion. **Copy diagnostics** creates a redacted text preview; **Copy** follows explicit review. It contains app/build/platform/environment, public service origin, non-sensitive capability codes, last sync reason category, and support request IDs. It excludes tokens, account email/subject, MAC addresses, raw records, profile values, and measurements. There is no automatic external message or attachment.

Entry: Settings tab or deep link to a named local setting. Exit: Back/tab change, OS settings round-trip, privacy/profile/device route, or sign-in/out. Unsaved edits follow their owning feature; simply visiting Settings changes nothing. State is partitioned into device preferences and account/workspace controls, with no public production endpoint editor.

## Preference and configuration contract

Local versioned preference record: `{schema_version, theme:"system"|"light"|"dark", reduced_motion:"system"|"reduce", display_units:"metric"|"us_customary", last_updated_at}`. Unknown future keys are ignored for display and not written back destructively; unsupported known values fall back to system/metric with a migration event containing no personal data. Preferences are committed atomically. Their defaults are system theme, system motion, and metric display. The automatic retry preference belongs to privacy controls and defaults off for a new account partition; it retries already explicitly requested operations only and never queues a new check. Account checks require an explicit Upload check action. All scientific/capture authorization remains server-derived.

`GET /v1/app-config` returns public release/capability metadata and current notice/policy versions; `GET /v1/me/capabilities` returns account actions. Both are validated against expected schema/environment. Network metadata cannot change issuer/API origin, weaken token verification, enable unsupported native modules, turn on raw recording, or switch this release to research inference. QA and local environments remain visibly identified; production cannot import a QA profile, token, or configuration as production authorization.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-SET-006 detailed contract

All non-timing-critical screens SHALL support TalkBack, 200% text scaling, 48 dp Android targets, visible keyboard/focus state where applicable, color-independent status, logical headings, and contrast of at least 4.5:1 for normal text/3:1 for large text and meaningful controls. Errors SHALL be announced once and linked to the relevant field/action. Reduced motion SHALL remove decorative animation. Timing tasks SHALL not silently change stimulus timing, input modality, or validated configuration to fit an accessibility preference; unsupported task configurations SHALL be explained and recorded under the task feature.

### AND-SET-001/002/003/004/006/007 integration resolution

Settings SHALL include **Research access** for all workspaces: signed-out users see Sign in to view invitations, accounts see their permitted memberships or the empty state, and no invitation is fabricated. Home owns the separate Alcohol measurement availability route. Shared route contracts preserve active workspace and typed export selection.

No current settings, public capability, local preference, or valid-looking research result can change `inference_available=false`. The production build contains no environment editor. Task stimulus colors, luminance, geometry, and timing remain fixed by the native task configuration independently of theme and accessibility styling. Selecting an action that leaves active native capture SHALL first execute its immediate **End task**/stop transition and retain one invalid/canceled attempt. A later confirmation concerns only the inactive broader draft and never offers mid-run resume.

Sign-out defaults to **Keep encrypted records and sign out**. **Remove this account's local records and sign out** is a separate count-confirmed action. Signed-out caches stay locked until same-issuer/subject reauthentication. Same-still-signed-in offline access uses device credential/biometric authentication through expo-local-authentication; cancellation or failure leaves data locked. Automatic-retry settings apply only to already explicitly queued operations and never queue new checks. Protected preference-related account writes follow the shared data-generation/precondition policy; local appearance changes need no server write.

### AND-SET-002 consolidated detailed contract

Theme/motion/units changes SHALL persist atomically and update presentation without modifying any frozen draft/finalized snapshot, assay basis, canonical concentration, task schedule, or model configuration. Theme SHALL follow device changes while set to system; reduced motion SHALL suppress decorative transitions while leaving timing-critical capture under its own versioned module. Task stimulus colors, luminance, size, and timing SHALL remain fixed by the task configuration independently of app theme.

### AND-SET-004/007 shared support and capture matrix

About SHALL report the concrete minimum/target toolchain and tested configuration matrix frozen in shared-contracts.md, separately from unresolved scientific device qualification. The mandatory evidence covers Android minimum/current emulator, a physical Android handset, iOS minimum/current simulator, a physical iPhone, portrait phone/responsive tablet flow, 200% text, TalkBack/VoiceOver, permission denial, focus/background/cancel, and offline restart. Unexecuted rows are shown as unexecuted. No capability flag authorizes offline qualified capture in this release; a fresh online server authorization is required at every qualified start. Offline demo and uncalibrated native practice remain distinctly available.

## ADDED Requirements

### Requirement: AND-SET-001 Complete, functional settings navigation

Every enabled Settings action SHALL reach its implemented destination or execute its described local action. Unavailable capabilities SHALL display the specific unavailable reason and SHALL not look enabled. Account actions SHALL reflect actual auth state; demo and account switching SHALL follow workspace isolation and active-check rules.

#### Scenario: set-signed-out-navigation
- **GIVEN** demo is active and no account is authenticated
- **WHEN** Settings is opened
- **THEN** Sign in is available, cloud deletion is unavailable with its account requirement, and local demo clearing remains reachable.

#### Scenario: set-active-check-switch
- **GIVEN** a check is active
- **WHEN** Switch workspace is selected
- **THEN** any active native run ends once before the decision; the UI explains that it cannot resume, the broader draft may be retained, and no record is moved between workspaces.

#### Scenario: set-research-access-visible-empty-state
- **GIVEN** a fresh account has no study memberships
- **WHEN** the user selects Settings then Research access
- **THEN** the feature opens its empty-state explanation and a working Back route without creating an invitation or enabling capture.

### Requirement: AND-SET-002 Persisted appearance without measurement mutation

The implementation SHALL satisfy the AND-SET-002 consolidated detailed contract and the shared platform contracts, including their exact states, authorization, persistence, and failure behavior.

#### Scenario: set-theme-restart
- **GIVEN** Dark theme was saved
- **WHEN** the process is terminated and relaunched
- **THEN** Dark theme is restored without a prolonged light-screen flash or record mutation.

#### Scenario: set-units-do-not-rewrite
- **GIVEN** finalized checks contain canonical ng/mL and profile cm/kg values
- **WHEN** US customary display is selected
- **THEN** profile presentation may convert units, saliva units remain qualified as reported, and stored measurements/record hashes do not change.

### Requirement: AND-SET-003 Permission visibility and OS round-trip

Settings SHALL read actual current permission state and show granted, denied, restricted, or not-requested as supported by the platform. It SHALL request no permission on screen entry. Open app settings SHALL use the platform settings link and re-evaluate on return; a denied permission SHALL not be represented as hardware failure or bypassed by a fabricated measurement.

#### Scenario: set-camera-denied
- **GIVEN** camera permission is denied
- **WHEN** Permissions opens
- **THEN** the camera row shows Denied with its feature explanation and Open app settings, without launching another prompt.

#### Scenario: set-permission-changed-outside-app
- **GIVEN** the user grants Bluetooth permission in OS settings
- **WHEN** the app returns to foreground
- **THEN** the displayed state refreshes and the reader feature decides whether a new scan is needed; an old scan is not assumed successful.

### Requirement: AND-SET-004 Capability and environment integrity

About/capability screens SHALL display the actual build environment and supported measurement-only scope. No setting, remote public field, deep link, or local preference SHALL enable clinical inference, arbitrary illumination, body-connected ECG, or participant upload without the separate implemented server/protocol gates. Production SHALL reject environment overrides and unsupported capability values.

#### Scenario: set-tampered-model-toggle
- **GIVEN** a modified preference file contains `inference_enabled:true`
- **WHEN** Settings and the result workflow load
- **THEN** the unsupported key grants no capability and probability remains unavailable in this release.

#### Scenario: set-qa-build-visible
- **GIVEN** the installed app uses QA services
- **WHEN** Home or About is displayed
- **THEN** QA is visible and the app cannot describe itself as a production clinical release.

#### Scenario: set-authorized-looking-research-output-still-disabled
- **GIVEN** a server response or local record advertises an active research model
- **WHEN** Settings or result navigation evaluates it
- **THEN** inference_available remains false and no current surface displays an impairment probability.

### Requirement: AND-SET-005 Redacted, user-initiated diagnostics

Diagnostics SHALL be generated from an allowlist of non-sensitive fields, previewed before copying, and copied only after the explicit Copy action. They MUST NOT contain authentication callbacks/tokens, direct identifiers, account subject/email, device MAC address, profile fields, saliva values, eye/ECG artifacts, or task event streams. Copy failure SHALL report failure without showing unredacted fallback content.

#### Scenario: set-diagnostics-copy
- **GIVEN** a connection error has a support request ID
- **WHEN** the user reviews and copies diagnostics
- **THEN** only allowlisted build/environment/error-reference fields reach the clipboard.

#### Scenario: set-error-with-sensitive-payload
- **GIVEN** an internal exception includes a server payload with profile fields
- **WHEN** diagnostics are generated
- **THEN** the payload is excluded rather than serialized or truncated into the copy text.

### Requirement: AND-SET-006 Accessible application shell and content

All non-timing-critical screens SHALL support TalkBack, 200% text scaling, 48 dp Android targets, visible keyboard/focus state where applicable, color-independent status, logical headings, and contrast of at least 4.5:1 for normal text/3:1 for large text and meaningful controls. The implementation SHALL also satisfy the AND-SET-006 detailed contract above.

#### Scenario: set-large-text-navigation
- **GIVEN** 200% system font scale on a 360 dp Android display
- **WHEN** Settings and Privacy are traversed
- **THEN** labels wrap, controls remain reachable by scrolling, and no essential action is hidden behind navigation or keyboard.

#### Scenario: set-screen-reader-task-boundary
- **GIVEN** a timing-task configuration does not support the active input/accommodation
- **WHEN** the user attempts that task
- **THEN** the task feature explains the unsupported configuration and records unavailability rather than claiming equivalent measured timing.

#### Scenario: set-active-task-navigation-ends-before-dialog
- **GIVEN** a native reaction run is active
- **WHEN** the user initiates a Settings/workspace route or End task
- **THEN** the run ends once before an overlay, retained partial evidence is marked invalid, and subsequent draft choices never resume it.

### Requirement: AND-SET-007 iOS parity and platform-specific behavior

iOS SHALL implement all settings destinations and equivalent persistence, scope, permission, diagnostics, and scientific gates. It SHALL use VoiceOver, Dynamic Type, at least 44 pt targets, safe-area-aware layouts, Reduce Motion, and the iOS app-settings link. Platform differences SHALL affect presentation and permission wording only unless explicitly documented as a supported-capability difference.

#### Scenario: set-ios-dynamic-type
- **GIVEN** a large accessibility Dynamic Type size and VoiceOver
- **WHEN** the user changes theme and opens privacy controls
- **THEN** each label/action remains reachable with correct state announcements and preferences persist across launch.

#### Scenario: set-ios-restricted-permission
- **GIVEN** iOS reports camera access restricted by device policy
- **WHEN** the permission row is opened
- **THEN** it shows Restricted, does not promise that an ordinary permission prompt will fix it, and preserves access to other permitted features.

## Acceptance evidence

Required evidence: automated navigation of every enabled row; preference migration/restart/unit-immutability tests; OS permission round-trip on both platforms; QA/local label inspection; tampered-config rejection; diagnostics allowlist fixtures; contrast measurements and 200% text screenshots; TalkBack/VoiceOver review. Scientific supported-device/timing/optical limits remain named gates; accessibility implementation alone does not qualify those measurements.
