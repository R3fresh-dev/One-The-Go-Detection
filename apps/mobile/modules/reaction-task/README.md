# Native choice and inhibition task

This Expo local module implements the reviewed `choice_inhibit_v0` developmental task on Android and iOS. Its stimulus scheduling, native touch timestamps, cancellation, scoring and raw event retention run in Kotlin or Swift. JavaScript starts a run and persists its terminal result; it does not time responses.

The module measures task performance. It does not infer cannabis intoxication, fitness to drive, drug concentration, or metabolic rate. Every acquired result has `calibrationStatus: "uncalibrated"`, `physicalOnsetVerified: false`, and `modelEligible: false`.

## Application integration

Import from `modules/reaction-task` relative to the app root. The complete versioned DTO and event types are in [types.ts](types.ts).

```tsx
import {
  ReactionTaskView, getReactionTaskAvailability,
  REACTION_CONFIGURATION_ID, REACTION_CONFIGURATION_SHA256,
  type ReactionTaskViewRef,
} from './modules/reaction-task';

// Allocate and durably record the attempt before mounting the view.
const view = React.useRef<ReactionTaskViewRef>(null);
const available = getReactionTaskAvailability();

<ReactionTaskView
  ref={view}
  runId={attempt.id}
  workspaceEpoch={workspace.epoch}
  seed={attempt.seed}
  configurationId={REACTION_CONFIGURATION_ID}
  configurationSha256={REACTION_CONFIGURATION_SHA256}
  running
  style={{ flex: 1 }}
  onComplete={({ nativeEvent }) => persistTerminalResult(nativeEvent)}
/>;

// First action on Back/End/navigation/withdrawal; do not wait for Bluetooth.
const receipt = await view.current?.cancel(attempt.id, 'ROUTE_HIDDEN');
if (receipt?.result) await persistTerminalResult(receipt.result);
// Only navigate after the same run's terminal result is durably reconciled.
```

Check availability before rendering. Expo Go, a web build, or an app binary built before installing this module returns `available: false`; display the explicit native-module availability state. There is no JavaScript timer fallback. `runId` is a UUID, `seed` is a uint32, and `workspaceEpoch` is a nonempty string with at most 128 characters. Configurations other than the exact reviewed ID and SHA are rejected.

`cancel()` runs on the native view queue and returns `{runId, status, result?}`. `result`, when present, is the same frozen object emitted in `onComplete`, including for an already terminal matching run. The app must deduplicate the event and receipt, including while a database write is pending. Do not replace delayed evidence with a timeout-generated valid result. Cancellation before the first layout seals the run and emits an invalid result; its layout dimensions may honestly be zero. A run cannot resume or emit a second terminal result. The native view remembers up to 128 run IDs; the app normally mounts one view per attempt.

The outer capture projection uses `prototype_sensor`, uncalibrated provenance, and the acquired result's actual `startedAt`. Preserve the full result in the versioned attempt's `component_metadata.native_result` and hash the complete canonical payload. Guest native practice stays local. A fully fictional engineering fixture is a separate source; never relabel a real native run as simulated to satisfy an upload gate.

## Frozen schedule and presentation

The configuration file is [fixtures/configuration.json](fixtures/configuration.json). Its canonical SHA-256 is:

`61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3`

The ID is `choice_inhibit_v0_native_dev_1`. The exact schedule vectors, scoring cases and boundary cases are in [fixtures/golden.json](fixtures/golden.json). The asset verification script compares these copies with the reviewed OpenSpec files; it does not regenerate the expected goldens from production code.

| Rule | Value |
|---|---|
| Practice | 6 trials: 2 left, 2 right, 2 no-go |
| Scored | 60 trials: 24 left, 24 right, 12 no-go |
| RNG | uint32 LCG: `state = 1664525 * state + 1013904223`, wrapping modulo 2^32 |
| Shuffle | Descending Fisher–Yates on practice, then scored; use successive RNG values |
| First planned onset | 2,000 ms after the native start anchor |
| Onset gaps | 66 subsequent RNG draws: `1500 + state % 401` ms |
| Gap indexing | Gap i is from trial i to trial i+1; the final gap is hashed but does not delay termination |
| Response window | `[actual onset, actual onset + 1000 ms)` |
| Final drain | 100 ms after the final response window |
| Input limit | 1,024 retained touch-downs; a 1,025th invalidates with an overflow count |
| Timing budgets | More than 100 ms of input dispatch delay, frame gap/dispatch, or onset lateness invalidates |
| Aggregate quantile | Sorted correct-go RTs, linear interpolation at `(n - 1) p` |

The fixed profile controls colors, geometry, text sizes, arrow polygon, fixation dot and no-go label. A minimum 240 × 400 logical portrait view is required; changes during a run invalidate it. The End task target is separate from the response targets and is at least 48 dp high on Android / 44 pt on iOS at the supported minimum size. Task text scale stays 1. Screen-reader touch exploration is refused at entry or invalidates a running task; the surrounding app remains accessible and offers the explicit unsupported-task state.

First response selection sorts by native timestamp, target order left/right/outside, pointer ID, then native sequence. Touch-downs outside the targets and anticipatory/additional/late events remain in the raw evidence. The End task control cancels and never enters scoring. Practice is excluded from aggregates. Valid omission/choice/no-go error rates use the reviewed denominators; invalid trials retain partial evidence and set aggregate features to null. A valid run with no correct go response keeps RT quantiles null.

## Timing evidence and its limits

Android uses `Choreographer` frame time, `MotionEvent` uptime timestamps, and `System.nanoTime()` for the native monotonic anchor. API 34+ retains `eventTimeNanos`; older supported Android versions use the millisecond event timestamp. Reported numeric granularity is not a latency accuracy claim.

iOS uses `CADisplayLink.timestamp` plus `targetTimestamp`, `UITouch.timestamp`, and `CACurrentMediaTime()`. Target timestamp is a presentation estimate. The input timestamp resolution is null because this implementation has no independently established physical resolution for the supported devices.

Neither frame callback establishes the instant photons reached a participant or establishes touchscreen latency. The record retains callback time, presentation estimate, native input and dispatch times, observed frame/input maxima, dimensions, density, OS/build/device identifiers, and simulation status. Physical luminance remains unmeasured. UTC end time derives from the start UTC anchor plus native elapsed time; a separately observed wall-clock end and delta expose clock changes.

Both views invalidate on native background/focus loss, detach, layout change, unsupported input, call interruption or a timing fault. A native watchdog detects missing presentation callbacks. The terminal cutoff excludes arrivals at or beyond its boundary. Cancellation processed before native terminal commit wins; after commit the immutable existing result is returned.

## Build and verification

The module is autolinked by Expo using `expo-module.config.json`. Its native directories are source code and must be committed. Generated app projects live at `apps/mobile/android` and `apps/mobile/ios`; only those generated directories should be ignored.

Android uses Expo SDK 57 / RN 0.86, minimum API 24 and compile/target API 36. iOS uses deployment target 16.4 and the reviewed Xcode 26.4+ toolchain. The source layout follows the official [Expo Modules API](https://docs.expo.dev/modules/module-api/), [native view guide](https://docs.expo.dev/modules/native-view-tutorial/) and [autolinking documentation](https://docs.expo.dev/modules/autolinking/).

See [../VERIFICATION.md](../VERIFICATION.md) for the exact checks executed, pending device checks, requirement mapping and artifact boundaries. The checked-in `native-result-valid-contract-fixture.json` is **host-generated fictional contract data**. It exercises the exact DTO, literal seed-1 schedule and +300 ms correct-go responses; it is not evidence of a native build, hardware timing, or an acquired participant result.

Primary timing references: [Android Choreographer](https://developer.android.com/reference/android/view/Choreographer), [Android MotionEvent](https://developer.android.com/reference/android/view/MotionEvent), [Apple CADisplayLink](https://developer.apple.com/documentation/quartzcore/cadisplaylink), [Apple UITouch.timestamp](https://developer.apple.com/documentation/uikit/uitouch/timestamp).
