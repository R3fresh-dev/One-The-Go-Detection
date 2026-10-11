# Android native reaction task

Scope: one continuous choice/inhibition task, native event acquisition, deterministic extraction, and equivalent iOS behavior. This specification extends APP-004–008/011/014 and LLD section 6. The task is an unvalidated research candidate. Completion and native timestamp precision SHALL not be presented as validated physical timing, cannabis impairment detection, or permission to drive.

Primary engineering references: [Expo native view API](https://docs.expo.dev/modules/native-view-tutorial/), [Expo module lifecycle](https://docs.expo.dev/modules/module-api/), [Android frame callbacks](https://developer.android.com/reference/android/view/Choreographer.FrameCallback), [Android native touch timestamps](https://developer.android.com/reference/android/view/MotionEvent#getEventTime()), and [Apple CADisplayLink](https://developer.apple.com/documentation/quartzcore/cadisplaylink). The native module is implemented only after review of this specification and the shared design.

Shared normative baseline: [shared application contracts](../../shared-contracts.md), especially release/workspace policy, frozen context and companion evidence, qualified online starts, immediate cancellation, immutable artifacts, and the Android/iOS software matrix. These rules govern the same behavior on both platforms.

## Frozen configuration and fixture identity

The normative configuration is [reaction-task-config-v1.json](../../fixtures/reaction-task-config-v1.json), JCS/SHA-256 `61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3`. [reaction-task-golden-v1.json](../../fixtures/reaction-task-golden-v1.json) fixes all three schedules and extractor/race vectors; [fixture conventions](../../fixtures/README.md) define exact digest coverage and comparison semantics. These artifacts precede implementation. Any changed budget, schedule, response boundary, tie rule, geometry, or terminal policy requires a new configuration version/hash and corresponding reviewed fixtures.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-TASK-001 detailed contract

The Reaction task screen SHALL explain Tap the side the arrow points to; when WAIT appears, do not tap, using text/shapes without relying on color. It SHALL identify six practice plus 60 scored trials in one continuous run, approximately two minutes as a design estimate. Actions SHALL be Start task, native End task during acquisition, and View saved task after completion. Start SHALL require a visible foreground native view, portrait geometry at least 240 × 400 logical points, and the exact selected development configuration hash. The configuration fixes fractional stimulus/target/end-control rectangles; actual point/pixel bounds, density, and text/input adaptation SHALL be retained. Native End task SHALL have a hit target of at least 48 logical points on Android and 44 on iOS; its 120-per-mille height satisfies this at the minimum 400-point view. It SHALL never count as a left/right task response, and any touch batch containing End task SHALL cancel before scoring other touches in that batch. The runtime SHALL disclose Uncalibrated native practice and distinguish intact acquisition from invalid interruption. If the compiled module is unavailable, the UI SHALL show unavailable; an optional JavaScript/web preview SHALL be explicitly Uncalibrated practice with fallback method and never claim native acquisition. Progress SHALL identify practice versus scored trials. Native uncalibrated practice MAY run offline and SHALL not create qualified human-study or inference eligibility.

The configuration SHALL also pin the exact requested sRGB colors/opacity, arrow polygon and mirror rule, fixed-point border/corner/fixation sizes, Android sans-serif versus iOS system sans-serif family policy, regular font weight, and WAIT/response/End labels at 32/20/16 logical points. The scored view SHALL use those constants independently of app light/dark theme or Dynamic Type/font-scale preferences; instructions and navigation outside acquisition still support the shared accessible text scaling. If text cannot fit the specified rectangles, Start SHALL be unavailable with LAYOUT_UNSUPPORTED, not silently resize the task. Any adapted text/input presentation SHALL be a separately identified uncalibrated practice configuration, never the same hash. Native font identity and actual glyph/view bounds SHALL be recorded because OS font implementations can differ. Between trials the screen shows the pinned neutral fixation dot. The app SHALL not request/override screen brightness. Requested sRGB colors are software values, not measured physical luminance, and SHALL not imply photometric or clinical equivalence.

### AND-TASK-002 detailed contract

The task SHALL use taskVersion=choice_inhibit_v0, implementationVersion=1.0.0, extractorVersion=choice_inhibit_features_1, and configurationId=choice_inhibit_v0_native_dev_1. The exact normative configuration and literal goldens SHALL be the linked fixture files. Six practice trials contain two left, two right, two no_go; 60 scored contain 24 left, 24 right, 12 no_go. A UInt32 seed initializes state=(1664525×state+1013904223) mod 2^32. Fisher–Yates descends i to 1, advances state once, and swaps index i with state mod (i+1), shuffling grouped practice then grouped scored lists without reseeding. Only after both shuffles, 66 successive draws SHALL yield 1500+(state mod 401) ms. The first planned onset is native start+2000 ms; interval[i] is the planned gap from trial i to i+1. The final interval is retained in the schedule/hash but does not control termination. Scheduling SHALL use precomputed absolute native targets, never response-dependent timing. The saved schedule includes all 66 trial indices/phases/stimuli/planned relative onsets/intervals, seed, and configuration digest; scheduleSha256 covers the exact versioned schedule object using JCS/SHA-256. Each response window is half-open [actual onset estimate, onset+1000 ms).

### AND-TASK-003 detailed contract

Android SHALL install each stimulus in the first Choreographer callback whose frameTimeNanos/1e6 is at or after its planned onset, using that frame time as the software onset estimate. iOS SHALL install it in the first CADisplayLink callback whose targetTimestamp×1000 is at or after the planned onset, using targetTimestamp as the expected presentation estimate and retaining timestamp separately. These platform estimates differ and SHALL remain explicitly labeled; neither proves photon onset. Native handler acquisition time and touch-event time SHALL share the declared platform uptime domain, with any conversion explicit. Android MotionEvent eventTime is in uptime milliseconds; API 34+ eventTimeNanos MAY supply finer reported resolution. iOS UITouch.timestamp×1000 uses its native uptime domain. JavaScript receipt and wall-clock subtraction SHALL not define RT. Every presented trial SHALL retain planned target, frame timestamp, callback acquisition time, software/expected onset, onset lateness, and applicable native clock resolution. Metadata SHALL retain phone/OS/build, actual point/pixel geometry, density/orientation, refresh information, input timestamp method, calibrationStatus=uncalibrated, physicalOnsetVerified=false, and modelEligible=false. Clock resolution SHALL not be described as accuracy. UTC start/end anchor context only; observed wall-clock discontinuity SHALL be retained without changing monotonic RT. Scheduled-onset lateness, frame callback dispatch delay relative to the platform frame timestamp, and successive native frame gap SHALL each be no greater than 100 ms during active acquisition, including countdown/drain. Exceeding a budget, a negative native dispatch delta, or monotonic clock regression SHALL invalidate with its named reason. No compatible frame callback by planned target+100 ms is a scheduled-onset fault. These are developmental integrity limits, not clinical quality thresholds.

### AND-TASK-004 detailed contract

The module SHALL retain all 66 planned trial records and at most 1024 direct native touch-down events, including presented=false/null timing for trials not shown. Every input retains native event timestamp, handler dispatch timestamp/delay, target left|right|outside, input kind, pointer ID, and native sequence. Touch events SHALL sort by (native timestamp, target rank left=0/right=1/outside=2, pointer ID, native sequence); equal-time opposing touches therefore choose left regardless of arrival order. Native sequence increments in the input collector; Android uses its native pointer ID, and iOS assigns run-local IDs on first touch using target rank, x, y, then native sequence within a received set. The first qualifying left/right event in the half-open response window determines the action only after timestamp-order scoring; provisional receipt order SHALL not lock a wrong answer before a valid earlier event is drained. Later taps remain recorded but cannot replace the first. Correct go yields RT, wrong go retains wrong-choice RT, absent go response is omission, no_go response is commission, and no_go withholding is correct_withhold. Outside-target input cannot answer a trial. Inputs before the first onset are anticipatory; inputs at/after a prior deadline and before the next onset are late for the prior trial and anticipatory for the next; trial associations/dispositions SHALL retain this explicitly. The no-go end boundary follows the same half-open rule. Input dispatch delay SHALL be between 0 and 100 ms inclusive while acquisition is active; a larger/negative value invalidates. Unsupported input invalidates with INPUT_MODE_UNSUPPORTED rather than silently mixing protocols. A 1025th input SHALL record the overflow trigger count, immediately stop/invalidate, and preserve the first 1024 events, never silently truncate a valid run. The fixed final cutoff is last actual onset+1000+100 ms; only handlers entering before the cutoff contribute. At/after cutoff, input is outside committed acquisition and SHALL neither be appended nor mutate a terminal result. The finite dispatch/drain bounds SHALL be disclosed as software observation limits.

### AND-TASK-005 detailed contract

Scored features SHALL exclude all six practice trials. For an intact run all presented trials are eligible under this developmental policy; there is no clinical RT cutoff, lapse threshold, or demographic speed adjustment. Correct-go RTs alone supply median, IQR=q75−q25, and p90 in milliseconds using sorted linear interpolation at index (n−1)p. Exact onset responses are eligible RT=0 under the half-open software rule; a tap before onset SHALL never be coerced to zero. Counts SHALL retain actual presented practice/scored, eligible go/no-go, correct go, omission, wrong go, commission, and correct withholding. An intact run has 60 presented scored, 48 eligible go, and 12 eligible no_go; omission/wrong rates divide by 48 and commission rate by 12. Empty correct-go RT sets yield null quantiles with NO_CORRECT_GO_RESPONSES, never zero; rates/counts remain factual. Any invalid/interrupted run retains bounded partial ledgers/counts but final features SHALL be null, including rates and quantiles in the selected v0.1 component. Unrounded native values remain in evidence, display rounds milliseconds to nearest integer with halves away from zero, and fixture arithmetic tolerance is 0.000001 ms while discrete fields/hashes match exactly. Research anticipatory/lapse/usable-trial thresholds and physical precision remain separately unresolved at G-06. This release always keeps inference_available=false.

### AND-TASK-006 detailed contract

The native module SHALL invalidate active acquisition on End task, explicit cancellation, app background, window/focus loss, phone call, screen lock, view detachment/hiding, route/tab/workspace change, geometry/orientation change, unsupported input mode, or the pinned timing/overflow fault. Display callbacks, native acceptance, and buffers SHALL stop immediately on the native UI path; no network request or JavaScript timer may delay shutdown. The parent SHALL invoke and await a native stop acknowledgment before presenting an acquisition-hiding overlay or changing route/workspace even if its navigator leaves the view mounted. Native End task acts directly. A subsequent Keep draft confirmation SHALL not resume the run. One terminal event is committed per run ID. Valid completion cannot commit before last actual onset+1000 ms response+100 ms drain; at cutoff no new inputs enter, and the next native loop commit emits once. If cancellation is pending on that native loop turn before terminal commitment it wins with invalid/USER_CANCELED or the specific interruption reason. A cancellation after a committed terminal result only returns already_terminal and emits no second result. Process loss is recovered from the parent’s durable started-attempt ledger as invalid/interrupted. A run SHALL never resume mid-trial. Native callbacks do not promise physical timing qualification; the exact development budgets are fixed in the fixture, not remotely tunable within this configuration.

### AND-TASK-007 detailed contract

The local module SHALL expose getAvailability() and ReactionTaskView with runId, seed, running, configurationId, configurationSha256, workspaceEpoch, and onProgress/onComplete. Its native cancel(runId,reason) method SHALL return a stop acknowledgment containing runId and stopped|already_terminal; it must stop before resolving. The parent SHALL persist attempt/session identity before setting running=true and never activate the same run twice. A completed native result SHALL include schemaVersion, taskVersion, implementationVersion, extractorVersion, status valid|invalid, source=native_task, platform, runId, seed, configurationId/hash, scheduleSha256, startedAt/endedAt UTC anchors, monotonic start/end and duration, all 66 trialEvents, bounded inputEvents, actual counts, features or null, qualityFlags, and timing metadata. onProgress contains only runId/epoch, phase, and presented/total counts at most once per presented trial; no frame/signal stream crosses JS. onComplete carries one at-most-512-KiB validated payload; overflow is invalid rather than dropped. Native method aliases and concrete DTO serialization SHALL be fixed in implementation against this contract, with unknown fields/versions rejected. The domain adapter SHALL preserve native method and map actual taps to prototype_sensor with calibrationStatus=uncalibrated and modelEligible=false. A fictional fixture remains simulated; actual taps in a JS fallback remain prototype_sensor with method=javascript_fallback and unsupported native compatibility, not fictional data or native_task. Mobile guest demo permits per-channel mixed provenance and never uploads; the all-fictional Python CLI keeps its separate stricter validator. Full native evidence SHALL be retained and JCS-hashed inside task CaptureAttempt 1.0.0 and the EvidenceManifest; the strict v0.1 snapshot stores only its selected projection. Parent acceptance SHALL check namespace epoch, run/attempt identity and digest, deduplicate identical completion, conflict on a changed same-ID result, and persist before navigation. A valid accepted task cannot be replaced for a preferred score. Invalid pre-finalization retry creates a linked new attempt; post-finalization recovery requires a new replacement check/target with no physical acquisition carryforward.

### AND-TASK-008 detailed contract

Kotlin, Swift, and an independent reference extractor SHALL consume the literal pre-code configuration/goldens linked below: seeds 0/1/4294967295, exact 66-trial schedules/digests, practice exclusion, quantiles, wrong/omitted go, no_go commission/withholding, first response, equal-time target ordering, early/deadline input, late dispatch and final drain, overflow, and cancellation. Exact state/source/count/null/hash comparisons and 0.000001-ms arithmetic tolerance SHALL be enforced without regenerating expected values using the same implementation under test. Android instrumentation and iOS native tests SHALL exercise focus/background/rotation, route hiding with mounted views, native cancellation, race/double-delivery, and actual timestamp fields. The software matrix SHALL follow shared §9: Expo 57.0.27/RN 0.86, Android minSdk 24/target 36, iOS 16.4 and required Xcode 26.4+, with unavailable toolchain/device rows explicitly unexecuted. Physical display/touch measurements are independently required at G-06; compilation/simulator success does not close it. Instructions/navigation support accessibility, but changed geometry/input language, screen-reader interaction, or assistive input SHALL retain adaptation and compatibility status and cannot inherit future original-protocol qualification. No profile-based adjustment, network operation, model output, or desired score may alter the sequence.

## ADDED Requirements

### Requirement: AND-TASK-001 Instructions, native entry, and completion states

The Reaction task screen SHALL explain Tap the side the arrow points to; when WAIT appears, do not tap, using text/shapes without relying on color. The implementation SHALL also satisfy the AND-TASK-001 detailed contract above.

#### Scenario: First complete task

- **GIVEN** a supported native application with no accepted task in this check
- **WHEN** the user selects Start task
- **THEN** the task SHALL execute one practice-plus-scored sequence and return one bounded native completion event containing the attempt identity, timing evidence, planned trials, observations, and derived features.

#### Scenario: Native module unavailable

- **GIVEN** a runtime without the compiled reaction module
- **WHEN** the reaction screen opens
- **THEN** the UI SHALL explain that a native build is required for capture and SHALL not silently replace it with JavaScript timers or mark a preview as a valid native task.

### Requirement: AND-TASK-002 Versioned deterministic schedule

The task identifier SHALL be choice_inhibit_v0 with a separately pinned implementation/configuration version and extraction version. The implementation SHALL also satisfy the AND-TASK-002 detailed contract above.

#### Scenario: Same seed on both native platforms

- **GIVEN** the same seed and pinned configuration
- **WHEN** Kotlin and Swift generate the schedule
- **THEN** all 66 stimulus identities, practice/scored classifications, onset intervals, and planned times SHALL match the shared golden fixture exactly.

#### Scenario: Responses influence apparent performance

- **GIVEN** two runs with the same seed but different response streams
- **WHEN** either run advances
- **THEN** its next planned stimulus SHALL remain unchanged by response speed, mistakes, omission, or a desired score; the app SHALL not adapt the schedule to improve the outcome.

#### Scenario: Unused final interval cannot prolong the task

- **GIVEN** the seed-1 literal schedule with all trials presented without lateness
- **WHEN** the final response window closes
- **THEN** the run SHALL end after its 100-ms drain at the fixture terminal cutoff, independent of the retained final interval draw.

### Requirement: AND-TASK-003 Native clocks and presentation evidence

Android SHALL use native Choreographer/MotionEvent timing and iOS SHALL use CADisplayLink/UITouch timing, retaining their different uncalibrated onset estimates and the pinned integrity limits. The implementation SHALL also satisfy the AND-TASK-003 detailed contract above.

#### Scenario: Accurate-looking floating-point timestamps

- **GIVEN** nanosecond or submillisecond software timestamps without physical display/touch calibration
- **WHEN** the task computes or displays reaction features
- **THEN** it SHALL retain uncalibrated status and report appropriate precision, without claiming that numeric resolution establishes equivalent physical timing accuracy.

#### Scenario: Wall clock changes during task

- **GIVEN** an uninterrupted native run
- **WHEN** the system wall clock changes
- **THEN** native reaction intervals SHALL remain based on the monotonic clock, the wall-clock discontinuity SHALL be retained in timing quality, and cross-component time eligibility SHALL be resolved separately.

### Requirement: AND-TASK-004 First-response semantics and bounded raw events

The module SHALL retain an ordered event ledger of native touch-down events and all planned trials, including trials not presented before interruption. The implementation SHALL also satisfy the AND-TASK-004 detailed contract above.

#### Scenario: Wrong then correct tap

- **GIVEN** a left-arrow go trial
- **WHEN** the first qualifying tap is right and a later tap is left
- **THEN** the trial SHALL remain an incorrect choice, both touches SHALL remain in the event ledger, and the later left tap SHALL not supply a correct-go reaction time.

#### Scenario: Omission and anticipatory input

- **GIVEN** a go trial with a tap before recorded onset and no qualifying tap afterward
- **WHEN** the response window ends
- **THEN** the early tap SHALL be retained as anticipatory, the go trial SHALL count as an omission, and no fabricated zero or 1000-ms reaction time SHALL enter the correct-go distribution.

#### Scenario: Response dispatched within the final drain

- **GIVEN** the final trial starts at 10000 ms and a left event occurs at 10999 ms
- **WHEN** the native handler receives it at 11079 ms before cutoff 11100 ms
- **THEN** the event SHALL be scored with RT=999 ms and dispatch delay=80 ms; a handler at the exact cutoff SHALL be outside committed acquisition.

#### Scenario: Opposing simultaneous touches are stable

- **GIVEN** a left trial and equal-timestamp right/left touches delivered in either order
- **WHEN** timestamp ordering is applied
- **THEN** left SHALL rank first, pointer/sequence ties SHALL follow the pinned comparator, and both platforms SHALL produce the golden correct choice.

### Requirement: AND-TASK-005 Feature extraction and missingness

Scored features SHALL exclude all six practice trials. The implementation SHALL also satisfy the AND-TASK-005 detailed contract above.

#### Scenario: All go trials omitted

- **GIVEN** an otherwise intact run with no correct go response
- **WHEN** extraction executes
- **THEN** correct-go quantiles SHALL be null, omission count/rate SHALL retain their true denominators, and the absence of a speed measurement SHALL not be interpreted as fast performance.

#### Scenario: Partial run stopped after ten scored trials

- **GIVEN** six completed practice trials and ten presented scored trials
- **WHEN** the run is interrupted
- **THEN** the attempt SHALL preserve those actual counts and planned remaining trials, mark invalid, and keep final-session aggregate task features null rather than pretending that a 60-trial task was completed.

### Requirement: AND-TASK-006 Interruptions, timing faults, and resource lifecycle

The native module SHALL stop and settle one invalid attempt before any interruption, navigation, or overlay hides its active stimulus; completion SHALL use the pinned final event drain. The implementation SHALL also satisfy the AND-TASK-006 detailed contract above.

#### Scenario: Notification drawer takes focus

- **GIVEN** an active Android run
- **WHEN** the system UI causes window focus loss
- **THEN** the module SHALL stop the display sequence, emit one invalid completion with FOCUS_LOST, and require a newly identified attempt when the user returns.

#### Scenario: Cancellation races with completion

- **GIVEN** a run approaching its final response window
- **WHEN** cancellation and completion callbacks become runnable together
- **THEN** the module SHALL commit one deterministic terminal state for that run, stop all callbacks, and SHALL not emit both a valid result and a separate canceled result.

#### Scenario: Navigation overlay cannot preserve an active scored run

- **GIVEN** an active task whose tab stays mounted after navigation
- **WHEN** the user selects another tab and then Keep draft in a confirmation
- **THEN** the native stop acknowledgment and invalid settlement SHALL precede the overlay; returning SHALL never resume that run.

### Requirement: AND-TASK-007 Native bridge, persistence, and repeat policy

The module SHALL expose a bounded native view contract with explicit run/epoch identity, cancellation acknowledgment, and retained native completion evidence. The implementation SHALL also satisfy the AND-TASK-007 detailed contract above.

#### Scenario: Completion event received twice

- **GIVEN** an accepted native result for a run ID
- **WHEN** the same payload is delivered again
- **THEN** persistence SHALL deduplicate it by run identity and hash; a different payload under the same run ID SHALL produce a conflict instead of replacing the accepted result.

#### Scenario: Actual taps in a JavaScript preview

- **GIVEN** a user interacting with an explicitly labeled fallback/practice view
- **WHEN** the preview ends
- **THEN** its output SHALL retain prototype_sensor with javascript_fallback provenance and SHALL not be labeled native_task or used as a compatible task baseline.

#### Scenario: Mixed guest demo preserves real native evidence

- **GIVEN** fictional saliva and an actual completed native reaction task in guest demo
- **WHEN** the check is saved and later exported or the user signs in
- **THEN** native taps SHALL remain prototype_sensor/uncalibrated in complete hashed companion evidence; guest upload/migration SHALL remain forbidden, while the CLI all-fictional validator stays unchanged.

### Requirement: AND-TASK-008 Platform parity, accessibility, and independent verification

The implementation SHALL provide deterministic shared schedule and scoring fixtures covering practice exclusion, correct/wrong/omitted go responses, no-go errors, multiple taps, anticipation, late delivery, empty RT sets, and interruption. The implementation SHALL also satisfy the AND-TASK-008 detailed contract above.

#### Scenario: Matching event fixtures across implementations

- **GIVEN** identical planned trials and ordered timestamped inputs
- **WHEN** Kotlin, Swift, and the reference extractor score them
- **THEN** counts, nullability, error rates, and quantiles SHALL match the named tolerances, with platform presentation-evidence differences retained in metadata.

#### Scenario: Passing native build without physical timing tests

- **GIVEN** successful Android/iOS compilation and fixture tests
- **WHEN** a release report is generated
- **THEN** it SHALL state native implementation/test completion separately from unresolved physical timing and predictive validation and SHALL keep modelEligible false.

#### Scenario: Development threshold and terminal boundaries are exercised

- **GIVEN** literal fixture inputs at exactly 100 ms and just over each native budget
- **WHEN** both platform test suites execute
- **THEN** exact-budget cases SHALL remain eligible, over-budget active cases SHALL invalidate, and post-cutoff arrivals SHALL leave committed results immutable.
