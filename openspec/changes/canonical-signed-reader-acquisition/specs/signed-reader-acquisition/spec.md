## ADDED Requirements

### Requirement: CAN-SR-001 Admit a distinct bounded physical reader dialect
The native client SHALL admit physical `prototype_sensor` only through the exact `otgd_signed_reader_v1` capability schema, supported channel inventory, physical BLE transport and bounded framing. It MUST reject unknown keys, conflicting duplicates, malformed identity/DER/sequence/timestamps or a fabricated `validated_sensor` advertisement. Physical transport alone MUST NOT establish device trust or model eligibility.

#### Scenario: A physical advertisement requests simulator handling
- **GIVEN** a reader advertises prototype_sensor under an unknown protocol identifier
- **WHEN** the app connects
- **THEN** the association is refused before capture.

#### Scenario: Compatible reader awaits trust
- **GIVEN** a bounded compatible physical capability
- **WHEN** the app connects without a verified binding receipt
- **THEN** measurement remains unavailable until server-backed binding and fresh authorization succeed.

### Requirement: CAN-SR-002 Preserve exact device binding proof and protected keys
Binding SHALL sign the exact approved server transcript using device-owned protected P256 under `OTGD-BIND-v1\n` plus RFC8785 JCS. The phone MUST forward that proof unchanged for server verification and install only the matching verified binding/device/key/hardware/firmware/environment/owner/generation receipt. Firmware MUST refuse plaintext or auto-generated identity fallback and require actual secure boot, flash encryption and encrypted-NVS key custody.

#### Scenario: Binding receipt references another device
- **GIVEN** successful proof from device A
- **WHEN** a receipt references device B or another owner generation
- **THEN** the native association remains untrusted.

#### Scenario: Stock SDK lacks protected NVS
- **GIVEN** a stock SDK compilation without NVS encryption
- **WHEN** the reader starts
- **THEN** it refuses protected-reader advertising and emits no fabricated measurement.

### Requirement: CAN-SR-003 Verify a fresh scoped server start signature on the reader
Reader start SHALL verify the exact scoped StartGrant schema, one-use actual32-byte nonce and physical boot. The server SHALL sign JCS under22-byte `OTGD capture grant v1\0` using approved P256. The device MUST verify its protected provisioned server SPKI/label and reject token-supplied keys or unsigned START. Required scope includes owner/generation/session/attempt/authorization/binding/device/key, configuration hashes/version, context SHA256, channel/duration and raw permission.

#### Scenario: Phone alters maximum acquisition duration
- **GIVEN** an authentic server token binds15000ms
- **WHEN** the phone requests a different channel, duration, context or configuration
- **THEN** the reader refuses start before touching acquisition hardware.

#### Scenario: Token includes a replacement verification key
- **GIVEN** the device trusts an offline provisioned server signer
- **WHEN** a caller substitutes an SPKI or signer label in the token
- **THEN** signature admission fails.

### Requirement: CAN-SR-004 Enforce signed expiry without inventing device wall time
Firmware SHALL strictly parse UTC issued/expiry timestamps with microsecond duration precision, require a positive signed lifetime no longer than60s and reject nonce age at or beyond that signed span. The nonce SHALL be consumed once before actual acquisition. Neither the device nor client MAY silently reset an expired token or substitute phone-owned signatures.

#### Scenario: Shortened grant reaches expiry boundary
- **GIVEN** a signed15s lifetime and nonce age15s
- **WHEN** START arrives
- **THEN** the reader refuses it even if the general nonce TTL is60s.

#### Scenario: Reversed or malformed timestamp
- **GIVEN** expiry precedes issue or contains invalid UTC syntax
- **WHEN** the reader validates the token
- **THEN** no hardware acquisition begins.

### Requirement: CAN-SR-005 Acquire actual bounded ADC observations from protected material
The opt-in ESP32-S3 ADC driver SHALL admit only protected exact approved ADCMaterial and calibration/configuration identity. It SHALL call actual analogRead, observe contact and monotonic sample times, preserve gaps without interpolation and bound RAM. Missing contact, saturation, gaps, poor amplitude, invalid calibration or insufficient intervals MUST prevent valid features. Chemical/THC values MUST NOT be inferred from ADC or MQ readings.

#### Scenario: Sensor contact is absent
- **GIVEN** a provisioned ADC channel with a separate contact input
- **WHEN** contact indicates no attached sensor
- **THEN** acquisition stops and no valid heart rate or ECG feature is produced.

#### Scenario: Loop misses samples
- **GIVEN** measured monotonic acquisition times skip scheduled observations
- **WHEN** the bounded extractor processes the next actual sample
- **THEN** it records explicit gaps and invalidates quality without generating missing values.

### Requirement: CAN-SR-006 Stop hardware independently of transport pressure
Driver tick/deadline enforcement SHALL precede TX backpressure decisions. The approved end guard SHALL stop actual ADC reads before the signed strict maximum. Cancellation, disconnect, unsupported configuration, queue/buffer failure and time overrun SHALL stop acquisition before any network/storage wait. Terminal evidence SHALL carry actual observed monotonic anchors; a completed hardware acquisition MAY await bounded TX delivery without resuming sampling.

#### Scenario: Notifications are congested at cutoff
- **GIVEN** the TX queue cannot publish another message
- **WHEN** the acquisition cutoff arrives
- **THEN** the driver stops regardless of queued acknowledgments.

#### Scenario: A slow ADC call crosses the bound
- **GIVEN** an ADC call returns after the bounded stop
- **WHEN** its observation arrives
- **THEN** the late sample is discarded and overrun cannot become valid evidence.

### Requirement: CAN-SR-007 Isolate connection-origin effects and replay privacy
Firmware SHALL serialize connection transitions against hardware start, signing and notify using an immutable origin gate. Cached participant replies SHALL be scrubbed on reconnect; original command/hash/origin tombstones SHALL remain and foreign-origin replay MUST NOT restart acquisition or return previous health data. Client write/ack failures SHALL retain the originating generation and MUST NOT invalidate a replacement association.

#### Scenario: Link transition occurs after final origin check
- **GIVEN** a sensitive effect and a concurrent replacement connection
- **WHEN** the final check/effect boundary executes
- **THEN** the shared gate orders them and no old-origin action occurs in the replacement association.

#### Scenario: Old ACK write fails late
- **GIVEN** account/device capture A is canceled and a new link connects
- **WHEN** A's deferred acknowledgment write rejects
- **THEN** the new association remains intact.

### Requirement: CAN-SR-008 Bind raw purpose and immutable signed evidence
Raw permission SHALL be a nullable signed exact record/upload receipt/policy/notice snapshot, admitted only for the permitted signed channel. Feature-only ADC MUST NOT record/queue/persist raw waveform. Raw ECG SHALL require protected approved encoding and sample capacity; unsupported opt-in MUST be refused. Device signatures SHALL bind exact payload JCS SHA256, current scope/boot/sequence. Structural client checks MUST NOT be described as cryptographic or scientific qualification.

#### Scenario: Unsupported raw configuration receives opt-in
- **GIVEN** the protected ADC raw encoding/capacity does not support the requested operation
- **WHEN** a non-null raw permission is supplied
- **THEN** the driver refuses that unsupported operation without silently recording or dropping an opted-in purpose.

#### Scenario: Normalized feature bytes change in transit
- **GIVEN** a device-signed exact projection
- **WHEN** a value or identity is modified
- **THEN** client digest admission and server signature verification reject the evidence.

### Requirement: CAN-SR-009 Build and qualify the protected SDK branch explicitly
A separate build-only ESP-IDF entry SHALL verify immutable official sources, exact submodule identity and generated NVS/secure-boot/release-flash-encryption controls. It SHALL require bounded nofollow private owned regular RSA3072 boot-signing material and verify actual application/bootloader/partition binaries. It MUST NOT flash, provision, burn eFuses or claim physical qualification. Changed caches, insecure generated sdkconfig, missing artifacts and unsuitable keys SHALL fail closed.

#### Scenario: Build output omits NVS encryption
- **GIVEN** a successful compiler process but altered generated security configuration
- **WHEN** the helper inspects the build
- **THEN** qualification fails despite the process exit code.

#### Scenario: Signing key is a public-readable symlink
- **GIVEN** a key path is symlinked or group/world-readable
- **WHEN** the helper admits the key
- **THEN** it refuses before invoking the build.

### Requirement: CAN-SR-010 Preserve external qualification and unknown-driver limits
Software availability SHALL remain distinct from physical/electrical/calibration/time/model approval. ADC timestamps SHALL identify the unqualified server wall anchor and separately retain actual monotonic observations. Unknown vendor assay hardware MUST remain unavailable without its actual documented driver. Completion SHALL require fresh exact-source mandatory CI and adversarial review; stock compile/fictional fixtures MUST NOT substitute for protected-SDK or physical proof.

#### Scenario: ADC software builds without an attached board
- **GIVEN** core tests and board compilation pass
- **WHEN** release readiness is reviewed
- **THEN** physical key provisioning, contact/safety/calibration/timing and scientific qualification remain explicit pending evidence.

#### Scenario: Vendor assay SDK is undocumented
- **GIVEN** signed transport supports a compatible evidence schema
- **WHEN** no actual approved acquisition SDK exists for the instrument
- **THEN** capability remains unavailable and no assay value is fabricated.

### Requirement: CAN-SR-011 Require authenticated encrypted BLE before human telemetry
Reader BLE SHALL require LE Secure Connections with MITM bonding and a protected per-device six-digit passkey presented by a physical provisioned label. Capability reads, commands and notification configuration SHALL require encrypted MITM GATT permissions. Actual current-peer authentication SHALL fence command admission, signing and notify. Missing keys, downgraded/foreign authentication or three pairing failures MUST deny capture; Just Works and plaintext fallback are forbidden.

#### Scenario: A replacement peer receives an old authentication callback
- **GIVEN** a BLE connection transitions to a different peer or generation
- **WHEN** authentication or a command callback from the original peer arrives
- **THEN** it cannot authorize the replacement association or deliver previous health data.

#### Scenario: Pairing negotiates encryption without MITM
- **GIVEN** a peer lacks the physical passkey and offers unauthenticated encryption
- **WHEN** the peripheral evaluates completed pairing
- **THEN** it refuses commands, disconnects and produces no participant telemetry.

#### Scenario: The current protected peer completes authenticated pairing
- **GIVEN** the current device peer completes Secure Connections with MITM bonding using its protected provisioned passkey
- **WHEN** a command and notification are admitted under the same connection origin gate
- **THEN** only that authenticated connection can send commands and receive its connection-targeted frames, while physical and clinical qualification remain separate.
