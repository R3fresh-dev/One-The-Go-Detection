# Android profile and immutable check context

## Purpose and traceability

Capture optional demographic and self-reported context accurately, preserve missingness, and freeze the profile used by each check. Demographics do not calculate a clearance rate or authorize study eligibility. Upstream: PRD §§5–6, PRD-016; HLD §§4.3, 6; LLD §§3, 7, 10 profile/session definitions; full specification APP-002/003/011, MOD-002/003/006, SEC-002/003, OPS-003/004.

## Shared contract authority

The [shared platform contracts](../../shared-contracts.md) are normative for release scope, workspace isolation, authentication, data generations, concurrency, privacy-job states, export selection, context freezing, and active-capture navigation. This feature SHALL follow those contracts; its UI preferences cannot weaken them.

## Customer journey and screen contract

1. **Profile summary:** heading “Your profile”, active workspace label, most recent saved revision/time, editable field summary, and **Edit profile**. Missing values read “Not provided”; demo reads “Use fictional details in this workspace.” No body-weight or BMI health-category labels appear.
2. **Edit profile:** units selector **Metric / US customary**; optional **Age**, **Height**, **Weight**, **Cannabis-use frequency**. Frequency options: **Never**, **Occasionally**, **Frequent**, **Daily or almost daily**, **Not sure**, **Prefer not to say**. Optional context section contains **Route** (inhaled, oral, other, unknown, declined), **Last use** (known date/time, unknown, declined), and **Recent exercise?** (yes, no, unknown), **Sleep in the last 24 hours** (0–24 hours or unknown), and **Alcohol co-use** (reported, not reported, unknown, declined). Frequency helper text reads “Your description; not a clinical tolerance category.” Every field permits explicit clearing except its missingness choice.
3. **Review/save:** derived BMI displayed only when qualified height and weight are both present; helper “Calculated from your entered height and weight.” CTA **Save profile**. In account mode the helper reads “Save these changes to your account”; this explicit Save action requests the account write. Demo Save remains local. Inline validation precedes submission; successful save returns to summary and announces “Profile saved. Completed checks keep their original profile.”
4. **Conflict:** “Your profile changed on another device.” Compare **Saved on account** and **Your unsaved changes**; **Use account version**, **Review my changes**, **Cancel**. No automatic last-write-wins merge.

Entry: dashboard profile action, Settings, or pre-check profile review. Exit: save, explicit discard, or retained encrypted draft. Android Back and iOS back/swipe prompt **Keep editing / Discard changes** when the draft differs from its initial revision. Navigation alone never changes a finalized check.

## Fields, validation, and contracts

Canonical values: age integer years or null; height cm or null; weight kg or null; BMI kg/m² or null; source `self_report` or `synthetic`; collection timestamps UTC. Adult-facing UI accepts age 18–125; height strictly greater than 0 and at most 300 cm; weight strictly greater than 0 and at most 500 kg. These are input guardrails, not research cohort or clinical limits. Metric entry accepts one decimal for height and two for weight. US customary height uses whole feet plus inches in [0,12); weight pounds uses up to two decimals. Exact conversions are 2.54 cm/in and 0.45359237 kg/lb. Store normalized numeric values without repeated unit-toggle rounding; display rounding never replaces stored values. BMI is calculated from canonical height/weight, stored at sufficient precision for the session contract, displayed to one decimal, and has no diagnostic categorization.

Use-frequency canonical enum is `never|occasional|frequent|daily|unknown|declined`; route is `inhaled|oral|other|unknown|declined`. A known last-use time must include timezone offset, must not be later than the current save/check target time, and remains `self_report`; a device-clock discrepancy triggers review rather than a fabricated value. Unknown and declined keep the timestamp null. Recent exercise maps to `recent_exercise: true|false|null`; sleep maps to `sleep_hours: number|null` in [0,24]; alcohol co-use maps to `reported|not_reported|unknown|declined`. Last-use input and these changing context fields are reviewed and saved before the **Start check** creation event; unknown is not filled from an old check. A confirmed known last-use time is converted once to nonnegative `time_since_use_min` at creation, where `target_at=created_at`; the original self-report time and profile/context revision remain available in account metadata. Optional context is never converted to a metabolic multiplier. Empty input maps to null only after the user clears it; network omission does not overwrite it.

API: `GET /v1/me/profile` → current profile/revision + ETag; `PATCH /v1/me/profile` with `If-Match`, `X-Data-Generation`, stable idempotency key, and canonical changed fields → new immutable `profile_version_id`, version, timestamps, and ETag. Initial save uses the empty-resource ETag `"0"`. API validation returns field-addressable errors. Missing If-Match returns 428; stale ETag returns 412; state/idempotency conflict returns 409; stale data generation returns 410 and quarantines the draft operation. 401 pauses sync; 403 is permission failure; retryable errors retain the exact draft and generation. Session creation copies one saved profile version plus exact canonical fields into its snapshot; later edits cannot rebind it. Local queued revisions preserve their base ETag and order.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-PRO-005 detailed contract

Offline edits SHALL be stored only in the active workspace's approved protected storage and labeled **Saved on this device · Sync pending**. Pending changes SHALL remain tied to their original subject/base revision. Automatic retries require the separate Retry queued uploads automatically preference; otherwise the user explicitly retries the requested save. Saving a profile never queues a check upload. Account switching, sign-out, and deletion SHALL apply the corresponding pending-data policy; a draft MUST NOT be uploaded under another subject.

### AND-PRO-003/004/005 integration resolution

The authoritative freeze point SHALL be the **Start check** creation transaction, before any acquisition. It stores the selected immutable profile/context revision and canonical values, with `target_at=created_at` for a new check. The check's Profile step is a review of that frozen version, not a rebinding editor. **Edit for a new check** opens Profile and subsequently creates a new linked check; even a pre-acquisition draft keeps its original context. New profile values never rewrite an earlier snapshot. Exact profile/context linkage follows the shared companion-evidence contract.

Account profile **Save profile** is an explicit protected write; it does not queue any check. A stale ETag opens the comparison flow. A stale generation quarantines the old intent and displays the deletion/reset state; the app never substitutes the latest generation onto the old payload. After all-data deletion, new profile saves require the shared explicit new-generation acknowledgment. Local guest-demo revisions never migrate or upload. Native acquisition must be ended before a route change to edit profile; changing profile cannot resume or rescore an ended task.

## ADDED Requirements

### Requirement: AND-PRO-001 Optional values and explicit missingness

The profile SHALL allow every demographic/use-history field to remain unprovided, unknown, or declined as defined above. It MUST preserve distinct unknown and declined history values and MUST NOT populate age, cannabis frequency, BMI, or a last-use time from a sample fixture or population average in account mode.

#### Scenario: pro-empty-profile-save
- **GIVEN** an account profile with no provided fields
- **WHEN** the user saves without entering optional context
- **THEN** numeric values remain null and no default cannabis exposure or baseline is created.

#### Scenario: pro-declined-history
- **GIVEN** last use is set to Prefer not to say
- **WHEN** the profile is saved and reloaded
- **THEN** the declined marker persists and its timestamp remains null.

### Requirement: AND-PRO-002 Deterministic units and validation

The app and API SHALL validate finite numeric values and the specified bounds, retain canonical SI values, and perform the defined exact unit conversions. BMI SHALL be null unless both qualified inputs exist. Invalid entries SHALL show an inline field-specific correction without clearing other draft fields or issuing a save request.

#### Scenario: pro-imperial-bmi
- **GIVEN** the user enters 5 feet 10 inches and 180 pounds
- **WHEN** the draft is validated and saved
- **THEN** canonical height is 177.8 cm, weight is 81.6466266 kg before contract precision handling, and displayed BMI is 25.8 with no category label.

#### Scenario: pro-invalid-number
- **GIVEN** height is zero, weight is non-finite, or age contains a fraction
- **WHEN** Save profile is pressed
- **THEN** the relevant inline errors appear, BMI is unavailable, and no invalid profile is submitted.

### Requirement: AND-PRO-003 Revisioned save and frozen session context

Each accepted profile change SHALL create a revision. A new check SHALL reference and copy the chosen saved version at check creation. Later profile edits MUST NOT mutate draft snapshots already bound to that version or finalized check snapshots. Changing a draft check's profile requires an explicit linked restart under the session feature.

#### Scenario: pro-edit-after-check
- **GIVEN** a finalized check records weight 80 kg and profile version A
- **WHEN** the user saves weight 82 kg as version B
- **THEN** the historical check retains version A and 80 kg while the next check may use B.

#### Scenario: pro-edit-during-open-draft
- **GIVEN** a check draft has already copied version A
- **WHEN** another device changes the profile
- **THEN** the open check does not silently acquire the new context and displays its saved profile version on review.

#### Scenario: pro-edit-before-first-acquisition-still-frozen
- **GIVEN** Start check created session A with profile revision P1 and no capture yet
- **WHEN** the user saves revision P2 on this or another device
- **THEN** A still displays P1 and its original target time; using P2 requires a new linked check created after that save.

### Requirement: AND-PRO-004 Conflict-aware and idempotent synchronization

Profile updates SHALL use an optimistic-concurrency precondition and idempotency key. On 412 the app SHALL keep the unsaved draft and require the conflict choice described above. It MUST NOT issue an unconditional overwrite or combine fields without user review. Repeated identical requests SHALL return the same logical revision.

#### Scenario: pro-two-device-conflict
- **GIVEN** two devices edit the same base revision
- **WHEN** the first save succeeds and the second receives 412
- **THEN** the second displays both versions and retains its draft until the user chooses.

#### Scenario: pro-save-timeout-retry
- **GIVEN** the server saved a revision but the response was lost
- **WHEN** the app retries with the original key and payload
- **THEN** one revision is returned and no duplicate change is recorded.

#### Scenario: pro-stale-generation-is-quarantined
- **GIVEN** a queued profile Save carries an earlier data generation
- **WHEN** the service returns 410 after accepted all-data deletion
- **THEN** the operation is quarantined without rewriting its generation; new saves wait for the explicit reset acknowledgment.

### Requirement: AND-PRO-005 Offline drafts and account separation

Offline edits SHALL be stored only in the active workspace's approved protected storage and labeled **Saved on this device · Sync pending**. The implementation SHALL also satisfy the AND-PRO-005 detailed contract above.

#### Scenario: pro-offline-edit
- **GIVEN** an account profile is cached and the network is unavailable
- **WHEN** the user saves valid changes
- **THEN** the local revision is labeled pending and reconciliation later applies the original ETag rather than pretending a server save occurred.

#### Scenario: pro-guest-to-account
- **GIVEN** a fictional demo profile exists
- **WHEN** the user opens a newly authenticated account
- **THEN** the account profile is fetched or shown empty and the demo profile is not imported automatically.

### Requirement: AND-PRO-006 Timestamp and baseline integrity

The app SHALL preserve timestamp source/timezone and explicit unknown values. It SHALL reject inconsistent future last-use input and MUST NOT infer individual clearance, sobriety, qualified baseline, or research eligibility from age, BMI, use frequency, or an earlier demo check.

#### Scenario: pro-future-use-time
- **GIVEN** a last-use timestamp is later than the current device time
- **WHEN** the user saves
- **THEN** the app asks the user to review the date/time or select unknown and does not silently clamp the timestamp.

#### Scenario: pro-demographics-do-not-score
- **GIVEN** a complete profile with daily use and all demographics
- **WHEN** the dashboard or result is displayed
- **THEN** no metabolic-rate calculation, baseline qualification, or intoxication probability is created from those fields.

### Requirement: AND-PRO-007 Accessible entry and iOS parity

Fields SHALL expose labels, units, optional status, error text, and selection state to TalkBack/VoiceOver. Validation SHALL focus the first error and provide an error summary without erasing the draft. iOS SHALL implement equivalent fields, conversion precision, conflicts, missingness, and immutable snapshots with locale-aware keyboards and Dynamic Type. Both platforms SHALL accept locale decimal input while storing locale-independent numbers.

#### Scenario: pro-accessible-errors
- **GIVEN** screen-reader navigation and 200% text scaling
- **WHEN** two fields fail validation
- **THEN** the error summary is announced, the first invalid field receives focus, and Save/Cancel remain reachable without overlapping controls.

#### Scenario: pro-ios-unit-roundtrip
- **GIVEN** an iOS profile contains canonical values with more precision than display
- **WHEN** the user toggles units twice without editing
- **THEN** stored values and BMI are unchanged and no new profile revision is created.

## Acceptance evidence

Required evidence: unit/locale and boundary fixtures; missingness round-trip; frozen-session test; concurrent-update and response-loss integration tests; demo/account isolation; offline reconciliation; Android/iOS field navigation screenshots; log review demonstrating that profile values are excluded from telemetry. None of the numeric entry bounds closes a scientific eligibility or model gate.
