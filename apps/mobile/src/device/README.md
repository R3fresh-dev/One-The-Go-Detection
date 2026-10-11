# Synthetic device adapter

This adapter supports a local software simulator and the project-specific BLE simulator firmware. It implements discovery, capability negotiation, bounded transport, three-exchange clock evidence, scoped commands, acknowledgment/retry, replay checks, capture cancellation and complete synthetic capture evidence. It accepts only the exact fixed `synthetic_bench_v1` fixtures. It does not connect arbitrary sensors as verified human measurement devices.

## API and integration

```tsx
import { createDeviceController, DevicePanel } from './src/device';

const device = createDeviceController({
  idFactory: () => crypto.randomUUID(),
  onInvalidated: (reason, context) => recordInterruptedAttempt(reason, context),
});

<DevicePanel controller={device} />;

await device.useLocalSimulator(); // Explicit user-selected software simulation.
const result = await device.captureSynthetic('ppg', {
  sessionId, attemptId, captureId, workspaceEpoch,
});
```

The app already supplies its Expo UUID implementation; the example's factory is illustrative. A controller exposes `snapshot`, `subscribe`, `scan`, `stopScan`, `connect`, `disconnect`, `forget`, `useLocalSimulator`, `captureSynthetic`, `cancelCapture` and `dispose`. Reuse one controller per app workspace. Stop acquisition immediately on route hiding, background, withdrawal or identity change; ignore callbacks whose full capture context no longer matches the active attempt. `cancelCapture()` seals the pending operation before it awaits transport shutdown.

`DevicePanel` provides scan, connect, explicit local simulator selection, disconnect/forget and permission recovery. State is one of `unavailable`, `idle`, `scanning`, `connecting`, `connected_simulator` or `error`. `humanCaptureAvailable` is always false in this adapter. Platform aliases are display labels, not evidence of identity.

The native transport lives in `modules/device-transport`. It uses Android `BluetoothGatt` and iOS `CoreBluetooth`, without a third-party BLE dependency. Availability failure is explicit; it does not silently substitute software simulation. Android requests runtime scan/connect permissions on Android 12+ and the legacy discovery location permission only when needed. iOS initializes its central manager after discovery is requested. App configuration supplies the Bluetooth usage explanation. There is no background acquisition mode.

## Capture DTO

[types.ts](types.ts) defines the exact `SyntheticDeviceCapture` record. Keep its complete `context`, `association`, `clockEvidence`, `messages` and `evidenceSha256` alongside the outer capture projection. Do not keep only the displayed value.

| Field group | Contents |
|---|---|
| Identity | Session UUID, attempt UUID, capture UUID, workspace epoch, device ID and physical boot ID |
| Provenance | `source: simulated`, transport `local_simulator` or `ble_unprovisioned`, `verifiedBindingId: null` |
| Clock evidence | Three exchanges, selected interval, offset/uncertainty, resolution terms, physical boot ID, `calibrated: false` |
| Timing | Phone UTC start/end plus device monotonic start/end |
| Messages | Full received logical envelopes, bounded to 32; a normal capture has 10 |
| Integrity | Canonical SHA-256 of the complete evidence basis; CRC is retained at the transport boundary |
| Eligibility | `SIMULATED`, `UNVERIFIED_DEVICE`, `modelEligible: false` |

Every captured value must equal the named fixture, including field names, units and array contents. A peripheral advertising a human source, another configuration, or changed values is rejected. The fixtures are:

| Channel | Fictional data |
|---|---|
| PPG | 72 bpm, 3 seconds, method `ppg` |
| ECG | 72 bpm, 4 seconds, one lead, 50 Hz, 200 fixed samples in `arbitrary_counts` |
| Saliva | Oral-fluid synthetic assay; delta-9-THC 12 ng/mL; 11-hydroxy-THC and THC-COOH not detected with null values; fixed fictional LOD 1, LOQ 2 and ULOQ 100 ng/mL |

These concentrations and analytical limits are software test values. No physical assay is implemented or qualified. ECG arbitrary counts are not millivolts, and the generated waveform is not a person's cardiac signal. Current snapshot version 0.1 uses PPG or ECG as its single cardiovascular channel, not both in one capture.

## BLE framing

| Attribute | UUID suffix (base `680cf5d8-5656-4f41-81c4-0f48d26f`) |
|---|---|
| Service | `1000` |
| Capability READ | `1001` |
| Command WRITE with response | `1002` |
| Event NOTIFY | `1003` |

Native transports deliberately use 20-byte ATT values (MTU 23). The generic framing code can validate ATT capacities up to 512 bytes, but the shipped peripheral advertises 20. Each fragment starts with this 12-byte little-endian header:

| Byte offset | Width | Meaning |
|---|---|---|
| 0 | 1 | Protocol version 1 |
| 1 | 1 | Encoding 1, strict UTF-8 JSON |
| 2 | 4 | Transfer ID |
| 6 | 2 | Zero-based fragment index |
| 8 | 2 | Fragment count |
| 10 | 2 | Payload byte count |

The reassembled logical stream is JSON followed by a four-byte little-endian CRC-32/ISO-HDLC, at most 8,192 bytes including CRC. CRC detects transport corruption; it is not authentication. The decoder rejects duplicate JSON keys, invalid UTF-8, nonfinite values, unsupported headers, noncanonical base64, impossible lengths, conflicting duplicates, interleaved transfers and overlong assemblies. It accepts identical duplicate fragments without duplicate delivery.

The message envelope contains protocol version, message UUID, device ID, boot UUID, session UUID, monotonic sequence and timestamp, type and bounded payload. An association-scoped journal binds message IDs to canonical content hashes; changed content under an old ID fails. Sequence replay and mismatched session/boot/device fail before persistence. Journals do not evict entries to permit replay; exhaustion produces an explicit restart/reconnect recovery state.

Only one logical fragment transfer is in progress at a time. Assembly expires after 120 seconds. Command acknowledgment timeout is two seconds **after the final fragment** and permits three retries of the same message ID/content; retries do not create another capture. A command's attempt/capture/epoch plus its time window scope it to one operation. Native scan and connection attempts time out after 15 seconds; a native write times out after five seconds. Native callback generation checks discard stale connections. Complete fixed records fit within one bounded logical message; larger recordings and `capture_chunk` assembly are not supported by this configuration and are rejected rather than truncated.

## Clock evidence

Policy `synthetic_interval_v1` retains exactly three request/response exchanges after hello, including a fresh handshake for each capture. Phone send timestamps are integer milliseconds to retain exact JSON round trips through the microcontroller; native packet receipt time is captured before JavaScript event delivery. Each interval includes both clock resolution terms:

`lower = device_send - phone_receive - (phone_resolution + device_resolution)`

`upper = device_receive - phone_send + (phone_resolution + device_resolution)`

Select the narrowest interval, taking the earliest exchange on ties. Offset is its midpoint and uncertainty is its half-width. A changed physical boot, backward clock, impossible interval or context mismatch invalidates the operation. This bounds a software clock mapping for synthetic bench testing; it does not calibrate human sensing.

## Tests and external dependencies

From `apps/mobile` run:

```sh
node --import tsx --test src/device/tests/*.test.ts
```

Tests cover byte framing, CRC, strict parsing, replay, timeout, clock intervals and a complete timed software capture/cancellation. See [../../modules/VERIFICATION.md](../../modules/VERIFICATION.md) for the executed evidence and device test gaps. The [Nano ESP32 firmware](../../../../firmware/README.md) exercises the same synthetic BLE protocol. Android/iOS radio, permissions and lifecycle behavior require a real device bench run; the host simulator does not prove them.

Future human measurements need an approved device implementation, electrical/optical/assay qualification as applicable, server-registry device public-key trust, authenticated per-device binding, approved capture configuration and fresh one-time online capture authorization. The app cannot register an arbitrary public key or promote a radio alias, CRC, software hash or simulator message into that trust chain. See the reviewed [shared contracts](../../../../openspec/changes/production-mobile-platform/shared-contracts.md).

Primary platform references: [Android BluetoothGatt](https://developer.android.com/reference/android/bluetooth/BluetoothGatt), [Android Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions), [Apple CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager).
