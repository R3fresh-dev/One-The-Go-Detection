# Synthetic live signal preview v1

Authored before implementation on 2026-10-11 after reviewed checkpoint `8aa56ce9883aaafeba11b809c94bc406e7ee0a0a`. This implements the software preview gap SW-012 in AND-HR-001/004/007 and AND-ECG-004/005. It grants no physical sensor, clinical, acquisition or transport trust authority.

## Scope and immutable evidence

`synthetic_signal_preview_v1` is a local software demonstration with explicit fictional labels. Its events are delivered only by `LocalSimulatorTransport` through a separate typed callback. They are never BLE packets, authenticated device proof, original acquisition timestamps or persisted raw physiological artifacts. An unprovisioned BLE connection retains the existing bounded `synthetic_bench_v1` protocol and displays **Live preview unavailable — waiting for synthetic completion**. No human adapter is enabled.

The existing normal capture retains its exact ten accepted wire messages and canonical complete payload. The preview cannot settle a valid attempt. Only the existing complete-message identity, clock, value and transcript validation may do so, and local cardiac completion additionally requires a complete clean preview. The ECG samples are the same 200 fixed 50 Hz arbitrary-count samples supplied by `syntheticValues('ecg')`, independent of the fixed 72 bpm value. Neither PPG nor heart rate is converted into ECG. No RMSSD is calculated from this four-second demonstration.

## Fixed engineering configuration

| Parameter | Value |
|---|---|
| Version and fixture ID | `synthetic_signal_preview_v1` |
| UI/event cadence | One frame per 100 ms, maximum 10 frames per second; frame zero announces waiting for contact |
| Watchdog cadence | 100 ms; monotonic elapsed time is from the local software transport clock |
| Stale cutoff | `now - last_received >= 500 ms`; at equality the preview becomes invalid |
| Frame acceptance delay | Strictly less than 500 ms from its scheduled local monotonic time; delivery at or after 500 ms fails stale |
| Fictional PPG length | 3,000 ms, 30 numbered observation batches, no ECG samples |
| Fictional ECG length | 4,000 ms, 40 numbered batches, five samples per batch, 50 Hz, 200 samples total |
| Visible ECG window | Last 100 accepted samples (two seconds), maximum 99 drawn segments |
| Sample range and units | -1,000 to 1,000 arbitrary counts; no mV label or calibrated gain |
| Frame bound | Exactly frame 0 plus at most 40 data frames; five ECG samples per data frame |
| Terminal behavior | Terminal state is latched. All later events are ignored. A new attempt uses new session-context identifiers as specified by the check flow and starts with an empty ring |
| Fault onset | Scheduled frame 12, at 1,200 ms; insufficient-sample fixture fails at its normal final frame |
| Stale fixture | Delivers only frames 0 through 10, then remains silent until the watchdog invalidates at 500 ms since frame 10 |

These are deterministic UI engineering parameters, not physiological quality thresholds or hardware timing/calibration claims. Any ordinary runtime delay beyond the cutoff invalidates this demonstration rather than inventing samples or certifying continuity.

## Capture options and states

The scenario is selected explicitly before starting and is immutable during the attempt. `clean`, `poor_contact`, `motion_artifact`, `transport_gap`, `stale_signal` and `insufficient_samples` are available for PPG and ECG; `lead_off` and `saturated` are ECG-only. Nonclean options on BLE or any signal option on saliva are rejected before starting the peripheral. The default retains normal clean capture behavior.

Frame zero has `waiting_for_contact`, no current heart rate, unknown contact and no samples. Data frames use `acquiring`, present contact, and the explicit fictional 72 bpm. Every fault immediately clears current heart rate, stops new samples and latches its precise quality state. A last waveform may remain displayed only as **Stopped fictional waveform — not current**. The preview has `complete` only after the fully validated complete message; it remains a fictional completed observation, not a live reading.

`poor_contact` reports absent contact; `motion_artifact` reports motion; `lead_off` reports absent electrode contact; `saturated` reports a saturated fixture; `transport_gap` deliberately skips the next frame/sample interval and invalidates without filling it. `insufficient_samples` sends an explicit insufficiency fault at its final frame instead of a full data batch. The remaining unchanged acquisition cannot later become valid. Every fault rejects the capture, disconnects the simulator and causes the existing attempt to settle invalid with null cardiac values. Retry creates a new attempt; a good previous modality remains separately retained under the existing selection rules.

## Event validation and bounds

Each event repeats its local peripheral, boot ID, complete `CaptureContext` (session, attempt, capture and workspace epoch), channel, selected scenario and configuration ID. The receiver requires the current local simulator, matching active context, source `simulated`, frame sequence equal to the next sequence, elapsed time exactly sequence × 100 ms, and exact expected ECG sample indexes/values from the fixed fixture. Changing identity, inserting extra keys, duplicate/out-of-order frames, samples or an unsupported quality state invalidates that active local demonstration. Old context/boot events cannot populate a new capture.

The ring is fixed to 100 ECG samples. It is a display projection of accepted source samples, never an input to aggregate acceptance. Plot drawing uses at most 99 line segments, contains no UI timer that derives measurements, and never fabricates lines across a gap. PPG has no waveform samples. Completion checks the full expected accepted frame/sample count independently of the ring, preserving the original full 200-sample capture proof.

Connection `observedAt` is a UTC observation of actual connection, handshake, disconnection or capture-state changes. Sample updates do not change that connection observation time. Per-frame synthetic times remain explicitly local synthetic elapsed times. No battery percentage is invented.

## Durable failure and privacy

The local preview lives only in controller memory and is cleared on an explicit disconnect/forget, workspace or foreground cancellation, transport replacement or new attempt. A fault's frozen preview is visible only within the still-current capture context. A terminal error carries that exact context; the app may settle only the matching still-started attempt within its existing workspace/generation fence. Cancellation and workspace changes use the existing interruption path and cannot be revived by a delayed preview.

The failure helper returns an invalid cardiac projection with null heart rate/RMSSD/sample rate/raw artifact, `source=simulated`, original attempt start, terminal UTC end and the precise allowlisted synthetic quality reason. Metadata uses only the existing scalar fields `fixture_id`, `context`, `contact`, `dropped_samples` and `sample_rate_hz`. It does not store preview samples or masquerade as a completed transport attestation. An unavailable or unmatched error returns null to the caller's ordinary interruption path. Human model eligibility remains false.

## Required verification

Host tests shall cover exact normal PPG/ECG frame counts and complete-wire evidence unchanged; all scenario terminal reasons and null projections; 499/500 ms cutoff; delayed dispatch; unknown/old boot, session, attempt, capture and epoch; duplicated/out-of-order frames; sample/value/bounds tampering; bounded scrolling without mutation of the full fixture; no ECG on PPG; cancellation before late events and completion; nonclean BLE refusal; and a clean retry starting with an empty ring and fresh identity. Native rendering, Bluetooth and physical device quality are separate unexecuted acceptance tasks unless actual execution is recorded.

## Specification adversarial review

The root reviewer confirmed the strict separation between fictional preview and accepted transport evidence, bounded sample retention, latched failure and current-context settlement before source implementation. **SLIVE-001 (Medium)** identified inconsistent equality wording between the frame-delay bound and the 500 ms stale cutoff. Both now reject at 500 ms; the required 499/500 ms boundary tests cover that resolution. Source, native rendering and hardware evidence remain separate.
