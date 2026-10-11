# Android device pairing

Scope: Android discovery, association, authenticated capture eligibility, and bounded BLE transport. The iOS implementation SHALL expose equivalent user states and data semantics through CoreBluetooth; platform permission mechanisms differ. This specification extends HLD sections 4, 7–8 and LLD sections 3 and 8. It does not establish a qualified chemical sensor or authorize participant hardware.

Engineering boundary: GET /v1/me/capabilities resolves available channels and authority. POST /v1/device-bindings creates only an independently approved binding; DELETE /v1/device-bindings/{id} revokes an authorized binding. The server's trusted device-key registry SHALL reject arbitrary client-supplied trust anchors. Production requests SHALL use verified access tokens and current account/generation policy. The exact P-256 binding and capture transcripts are fixed in shared contracts §6; actual device credentials and hardware qualification remain external dependencies.

Primary platform reference: [Android Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions).

Shared normative baseline: [shared application contracts](../../shared-contracts.md), especially release/workspace policy, frozen context and companion evidence, qualified online starts, immediate cancellation, immutable artifacts, and the Android/iOS software matrix. These rules govern the same behavior on both platforms.

## Detailed engineering contracts

The following ID-mapped rules are normative implementation details for their corresponding requirements. They preserve the complete field, lifecycle, timing, and verification rules while each OpenSpec requirement states its principal behavior concisely.

### AND-DEV-001 detailed contract

The Android app SHALL provide a Device screen reachable from navigation and from a check's device prerequisite. It SHALL display one of unavailable, permission_required, bluetooth_off, idle, scanning, connecting, verifying, connected_simulator, connected_verified, reconnect_required, or error. The screen SHALL show the current device alias, hardware/firmware versions when received, last successful contact time, connection state, and an explicit Simulated data badge for a simulator. Primary actions SHALL be Find device, Connect, Stop scan, Retry, Disconnect, and Forget device as applicable; unavailable actions SHALL explain the prerequisite. Pairing SHALL never itself indicate assay readiness or research eligibility.

### AND-DEV-002 detailed contract

Android SHALL request only the Bluetooth permissions required by its supported OS versions at the point the user selects discovery. Android 12 and later SHALL use the applicable BLUETOOTH_SCAN/BLUETOOTH_CONNECT permissions; earlier supported OS versions SHALL request location only where required for BLE scanning. The app SHALL not imply that operating-system permission grants research consent. It SHALL offer Open settings after a permanent denial, a retry after a recoverable denial, and a Bluetooth-enable explanation when the radio is off. Scanning SHALL stop on cancellation, backgrounding, permission revocation, or a 15-second discovery timeout; the timeout is an application UX setting, not a hardware performance guarantee.

### AND-DEV-003 detailed contract

Discovery SHALL filter by the project service UUID 680cf5d8-5656-4f41-81c4-0f48d26f1000 and deduplicate advertisements by the platform peripheral handle during the scan. Display names and RSSI SHALL be treated as hints, not authenticated identity. A DeviceAssociation SHALL retain the provisioned device ID, fresh boot ID, local platform handle, hardware revision, firmware version, protocol version, and verified binding ID when available. Advertisements, aliases, and logs SHALL contain no participant identifiers. Human physiological telemetry SHALL require a reviewed provisioned device credential, cryptographic verification of association, encrypted transport, and binding to the authorized app/study context; CRC, proximity, a QR label alone, and a user-entered source string SHALL not satisfy this gate. Until the provisioning implementation and its evidence are available, connected_verified SHALL be unreachable in a production build.

The client SHALL obtain binding challenge/transcript and public-key trust from the server registry, verify the named P-256/DER/JCS contract, and complete an owner/environment/generation-scoped one-use challenge. No participant endpoint SHALL register an arbitrary public key. A changed registry key version, expired/consumed challenge, revoked binding, wrong study scope, or differing signed identity SHALL block verified association. The app SHALL retain the proof reference separately from its display alias. Only explicit simulated telemetry is permitted from an unprovisioned radio; a real native phone task remains separately sourced prototype_sensor and does not upgrade radio trust.

### AND-DEV-004 detailed contract

After connection, the app SHALL read capabilities using characteristic 680cf5d8-5656-4f41-81c4-0f48d26f1001 and subscribe to event TX ending 1003 before commands use RX ending 1002. A successful handshake SHALL resolve supported protocol, encodings, maximum payload, source mode, channel availability, configuration/calibration references, firmware/hardware, device ID, and boot ID. Unknown or incompatible mandatory versions SHALL fail closed with Upgrade required or Unsupported device. Clock synchronization SHALL preserve phone and device monotonic send/receive timestamps, round-trip offset interval, timestamp resolution, selected offset, and uncertainty. A clock policy SHALL be versioned; no clinical synchronization limit is introduced by this feature.

A capability handshake SHALL not authorize a human start. Cached server capability data SHALL be display-only, and every qualified start SHALL obtain the fresh online authorization/start acknowledgment in shared contracts §6. The authorization, configuration hash, binding, boot, and attempt SHALL be pinned together. Wall-clock rollback, airplane mode, or a reconnect SHALL not extend or create authority.

### AND-DEV-005 detailed contract

The receiver SHALL implement the LLD 12-byte little-endian fragment header: version u8=1, encoding u8=1, transfer_id u32, zero-based fragment_index u16, fragment_count u16, and fragment_payload_bytes u16. A complete logical message SHALL be at most 8192 bytes including its final four-byte little-endian CRC-32/ISO-HDLC checksum; JSON content is therefore at most 8188 bytes. Fragment payload capacity SHALL respect negotiated ATT_MTU minus 3 minus 12; MTU 23 therefore permits eight bytes. Only one in-progress transfer per direction SHALL be accepted. The implementation SHALL reject unknown encodings, inconsistent lengths/counts, impossible indices, conflicting duplicate fragments, oversized data, CRC mismatch, malformed JSON, nonfinite numbers, and wrong device/boot/session identities before domain storage. CRC SHALL be described as corruption detection, never authentication.

For human evidence, successful CRC/JSON parsing SHALL remain insufficient: the server and permitted native adapter SHALL verify the exact shared-contract capture envelope, device key version, current authorization, replay/sequence uniqueness, payload digest, and normalized-value mapping. Verified artifact reads SHALL pin the accepted S3 VersionId. Neither a changed source string nor a valid signature over different normalized fields SHALL qualify the selected v0.1 projection.

### AND-DEV-006 detailed contract

Each logical command SHALL include protocol_version, message_id, device_id, boot_id, session_id, sequence, monotonic_ms, type, and payload. Supported types SHALL match hello, clock_sync, start_capture, cancel_capture, capture_chunk, capture_complete, status, ack, and error. Commands SHALL be bound to an attempt and deadline. Reuse of a message ID with identical content SHALL return its prior disposition; reuse with different content SHALL fail. Accepted human commands SHALL additionally have application replay protection bound to the verified association. The two-second ACK timeout SHALL begin after the final fragment has been sent; at most three retries and a separate 120-second reassembly deadline SHALL apply. Larger raw artifacts SHALL use bounded chunks plus a verified final length/digest manifest. Capture completion SHALL require both transport integrity and the channel's domain validation.

Application routing SHALL additionally bind attempt_id, capture/run identity, and workspace epoch to every command/result; the versioned payload SHALL carry fields not present in the legacy envelope. The immutable CaptureAttempt and evidence manifest SHALL preserve the original signed capture evidence and its hashes through the version 1.0.0 companion APIs. Changed-body retries SHALL conflict, old-epoch events SHALL be discarded, and post-withdrawal/deletion authorization SHALL be rechecked before evidence acceptance.

### AND-DEV-007 detailed contract

Disconnect SHALL stop channel subscriptions, pending commands, and scanning and invalidate an unfinished capture. Reconnect SHALL preserve completed immutable records and create fresh session transport state; it SHALL not resume a scored reaction run or infer that an interrupted assay completed. The app SHALL provide a manual Reconnect action and SHALL not reconnect indefinitely in the background. Forget device SHALL remove the local association and its credential references after any active capture is canceled; remotely revoking an enrolled binding SHALL use the authorized server operation and display pending status if offline. Forgetting a device SHALL not delete historical sessions without the separate data-deletion workflow.

Selecting Disconnect, Forget, Cancel, Back, or a route change that hides an active acquisition SHALL stop locally and settle its invalid/canceled disposition before a confirmation sheet or best-effort remote operation. Canceling a later wider-draft confirmation SHALL not restart the acquisition. Forget while offline SHALL remove local eligibility immediately and display Remote revocation pending; it SHALL not promise that the disconnected server or other phones have received revocation. Retry before finalization uses a new linked attempt; after finalization it requires Start replacement check under shared §5.

### AND-DEV-008 detailed contract

Android and iOS SHALL share domain fixtures for identity, command idempotency, framing, duplicate handling, and provenance. Android SHALL use its native BLE stack through the reviewed library/module; iOS SHALL use CoreBluetooth-compatible behavior without requesting Android-specific permissions. Device secrets SHALL remain in OS-protected storage; diagnostic logs SHALL contain reason codes and non-identifying event metadata only. Simulator and production backend environments SHALL have separate bindings and storage namespaces. Test evidence SHALL include Android permission/radio instrumentation, both platform lifecycle tests, protocol unit fixtures at small and larger MTUs, and physical peripheral integration before claiming verified human hardware support.

## ADDED Requirements

### Requirement: AND-DEV-001 Device screen and association state

The Android app SHALL provide a Device screen reachable from navigation and from a check's device prerequisite. The implementation SHALL also satisfy the AND-DEV-001 detailed contract above.

#### Scenario: Connect a demonstration device

- **GIVEN** a supported phone and a discoverable synthetic peripheral
- **WHEN** the user selects Find device, chooses the listed device, and its handshake succeeds
- **THEN** the screen SHALL enter connected_simulator, show Simulated data, and enable only synthetic capture channels advertised by the handshake.

#### Scenario: Device connected but assay unavailable

- **GIVEN** a connected reader advertising assay_ready=false
- **WHEN** the user proceeds to the saliva step
- **THEN** the step SHALL state that the assay is unavailable, offer its permitted sample-record or simulation workflow, and SHALL NOT report a chemical concentration or a completed assay merely because pairing succeeded.

### Requirement: AND-DEV-002 Runtime permissions and radio availability

Android SHALL request only the Bluetooth permissions required by its supported OS versions at the point the user selects discovery. The implementation SHALL also satisfy the AND-DEV-002 detailed contract above.

#### Scenario: Permission denied without losing the check

- **GIVEN** an existing draft check and a first discovery request
- **WHEN** Android denies the required permission
- **THEN** no scan SHALL begin, the draft SHALL remain intact, and the screen SHALL explain the missing permission and present an appropriate retry or settings action.

#### Scenario: Radio disabled during discovery

- **GIVEN** an active scan
- **WHEN** Bluetooth becomes unavailable or the app moves to the background
- **THEN** scanning SHALL stop, any progress indicator SHALL settle into a named recovery state, and no stale discovery result SHALL be represented as a live connection.

### Requirement: AND-DEV-003 Discovery identity and verified association

Discovery SHALL filter by the project service UUID 680cf5d8-5656-4f41-81c4-0f48d26f1000 and deduplicate advertisements by the platform peripheral handle during the scan. The implementation SHALL also satisfy the AND-DEV-003 detailed contract above.

#### Scenario: Spoofed device name

- **GIVEN** an unprovisioned peripheral advertising the expected name and service
- **WHEN** it claims that it is a validated reader
- **THEN** the app SHALL refuse verified association, retain an explicit unverified-device reason, and SHALL NOT ingest human measurements from that connection.

#### Scenario: Known binding belongs to another context

- **GIVEN** a device credential that verifies cryptographically but has no permitted binding for the current account or study
- **WHEN** association is requested
- **THEN** the app SHALL reject participant capture and SHALL not disclose another participant's sessions or identity.

#### Scenario: Replayed binding challenge and substituted key

- **GIVEN** a previously consumed server challenge or a client-supplied replacement trust key
- **WHEN** association is retried under that challenge or key
- **THEN** binding SHALL fail without a new verified state; the client SHALL retain only its permitted simulator association and reveal no other owner identity.

### Requirement: AND-DEV-004 Capability handshake and clock evidence

After connection, the app SHALL read capabilities using characteristic 680cf5d8-5656-4f41-81c4-0f48d26f1001 and subscribe to event TX ending 1003 before commands use RX ending 1002. The implementation SHALL also satisfy the AND-DEV-004 detailed contract above.

#### Scenario: Compatible handshake

- **GIVEN** matching protocol versions and subscribed events
- **WHEN** the clock exchanges complete
- **THEN** the association SHALL retain the narrowest valid observed offset interval and an uncertainty no smaller than the exchange and clock resolution permit.

#### Scenario: Counter restarts after device reboot

- **GIVEN** an accepted boot ID and an in-progress acquisition
- **WHEN** a new boot ID or unexplained monotonic regression is observed
- **THEN** the affected acquisition SHALL become invalid, previous clock alignment SHALL be discarded, and a new handshake and capture attempt SHALL be required.

#### Scenario: Cached capability cannot enable an offline reader

- **GIVEN** a bound reader and a cached available human capability
- **WHEN** the user starts capture while offline after changing the wall clock
- **THEN** the app SHALL reject the qualified start and explain that current server authorization is required.

### Requirement: AND-DEV-005 Bounded transport and message integrity

The receiver SHALL implement the LLD 12-byte little-endian fragment header: version u8=1, encoding u8=1, transfer_id u32, zero-based fragment_index u16, fragment_count u16, and fragment_payload_bytes u16. The implementation SHALL also satisfy the AND-DEV-005 detailed contract above.

#### Scenario: Small-MTU valid message

- **GIVEN** ATT MTU 23 and a valid bounded message
- **WHEN** its fragments arrive in the supported order, including an identical duplicate
- **THEN** the receiver SHALL reconstruct the exact logical bytes once, verify CRC and envelope semantics, and acknowledge one accepted message without duplicate capture events.

#### Scenario: Malformed fragment flood

- **GIVEN** an established connection
- **WHEN** the peripheral supplies an oversized declared length, conflicting duplicate, or more than the allowed in-flight transfer
- **THEN** the receiver SHALL release bounded buffers, emit a named protocol failure, and SHALL not allocate memory proportional to attacker-provided lengths or store a partial successful reading.

#### Scenario: Signature valid for another measurement

- **GIVEN** a valid device signature for payload A and a selected snapshot containing changed payload B values
- **WHEN** upload or finalization validates evidence
- **THEN** the exact normalized payload hash/mapping check SHALL reject B, retain a provenance failure, and SHALL not infer trust from source=validated_sensor.

### Requirement: AND-DEV-006 Command scoping, completion, and replay

Each logical command SHALL include protocol_version, message_id, device_id, boot_id, session_id, sequence, monotonic_ms, type, and payload. The implementation SHALL also satisfy the AND-DEV-006 detailed contract above.

#### Scenario: Capture-complete acknowledgment is lost

- **GIVEN** one complete capture already stored locally
- **WHEN** the peripheral retransmits its identical completion message after an acknowledgment timeout
- **THEN** the receiver SHALL acknowledge the existing disposition and SHALL not create a second capture or a second sample.

#### Scenario: Completion arrives before missing chunks

- **GIVEN** an ECG or other multi-chunk capture with a missing chunk
- **WHEN** capture_complete arrives
- **THEN** the component SHALL remain incomplete and become invalid at its bounded timeout unless the missing bytes and final digest are verified; a notification alone SHALL not count as success.

### Requirement: AND-DEV-007 Disconnect, cancellation, and forgetting

Disconnect SHALL stop channel subscriptions, pending commands, and scanning and invalidate an unfinished capture. The implementation SHALL also satisfy the AND-DEV-007 detailed contract above.

#### Scenario: User cancels during capture

- **GIVEN** an active device acquisition
- **WHEN** the user selects Disconnect, Cancel, or Forget before any wider-draft confirmation
- **THEN** the app SHALL send a best-effort cancel command, stop accepting that attempt's later payloads, retain its canceled/invalid disposition, and return to a recoverable device state.

#### Scenario: Late event after reconnect

- **GIVEN** a new boot or capture attempt after reconnection
- **WHEN** a queued event from the prior attempt arrives
- **THEN** the receiver SHALL reject it by identity and SHALL not populate the new check with a stale reading.

### Requirement: AND-DEV-008 Platform parity, secret handling, and verification

Android and iOS SHALL share domain fixtures for identity, command idempotency, framing, duplicate handling, and provenance. The implementation SHALL also satisfy the AND-DEV-008 detailed contract above.

#### Scenario: Simulator fixture on either platform

- **GIVEN** the same synthetic message sequence on Android and iOS
- **WHEN** both clients complete a check
- **THEN** each SHALL preserve simulated provenance and matching semantic records even though OS peripheral handles differ.

#### Scenario: Demo configuration copied into production

- **GIVEN** a production build with no approved provisioned device
- **WHEN** a local demo file attempts to set a verified binding or validated source
- **THEN** the claim SHALL fail independent verification and SHALL never unlock human capture or inference.
