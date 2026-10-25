# OTGD-013 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md`; SHA256 `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-013/test-plan.md`. External review artifact only; PM controls import.

All 23 stable cases / 11 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `uv run --project services/api python scripts/ci_gate.py infra-unit`
- `node --import tsx --test --test-reporter=junit test/*.test.ts (cwd: infra)`
- `Exact compiler, executable and arduino-cli commands: immutable .github/workflows/native-build.yml; actual ci-firmware.log and ci-protected-reader.log retained.`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-013-CAN-SR-001-01 | A physical advertisement requests simulator handling — - **GIVEN** a reader advertises prototype_sensor under an unknown protocol identifier - **WHEN** the app connects - **THEN** the association is refused before capture. | PARTIAL |
| OTGD-013-CAN-SR-001-02 | Compatible reader awaits trust — - **GIVEN** a bounded compatible physical capability - **WHEN** the app connects without a verified binding receipt - **THEN** measurement remains unavailable until server-backed binding and fresh authorization succeed. | PASS |
| OTGD-013-CAN-SR-002-01 | Binding receipt references another device — - **GIVEN** successful proof from device A - **WHEN** a receipt references device B or another owner generation - **THEN** the native association remains untrusted. | PARTIAL |
| OTGD-013-CAN-SR-002-02 | Stock SDK lacks protected NVS — - **GIVEN** a stock SDK compilation without NVS encryption - **WHEN** the reader starts - **THEN** it refuses protected-reader advertising and emits no fabricated measurement. | BLOCKED |
| OTGD-013-CAN-SR-003-01 | Phone alters maximum acquisition duration — - **GIVEN** an authentic server token binds15000ms - **WHEN** the phone requests a different channel, duration, context or configuration - **THEN** the reader refuses start before touching acquisition hardware. | PARTIAL |
| OTGD-013-CAN-SR-003-02 | Token includes a replacement verification key — - **GIVEN** the device trusts an offline provisioned server signer - **WHEN** a caller substitutes an SPKI or signer label in the token - **THEN** signature admission fails. | PARTIAL |
| OTGD-013-CAN-SR-004-01 | Shortened grant reaches expiry boundary — - **GIVEN** a signed15s lifetime and nonce age15s - **WHEN** START arrives - **THEN** the reader refuses it even if the general nonce TTL is60s. | PASS |
| OTGD-013-CAN-SR-004-02 | Reversed or malformed timestamp — - **GIVEN** expiry precedes issue or contains invalid UTC syntax - **WHEN** the reader validates the token - **THEN** no hardware acquisition begins. | PASS |
| OTGD-013-CAN-SR-005-01 | Sensor contact is absent — - **GIVEN** a provisioned ADC channel with a separate contact input - **WHEN** contact indicates no attached sensor - **THEN** acquisition stops and no valid heart rate or ECG feature is produced. | PASS |
| OTGD-013-CAN-SR-005-02 | Loop misses samples — - **GIVEN** measured monotonic acquisition times skip scheduled observations - **WHEN** the bounded extractor processes the next actual sample - **THEN** it records explicit gaps and invalidates quality without generating missing values. | PARTIAL |
| OTGD-013-CAN-SR-006-01 | Notifications are congested at cutoff — - **GIVEN** the TX queue cannot publish another message - **WHEN** the acquisition cutoff arrives - **THEN** the driver stops regardless of queued acknowledgments. | PARTIAL |
| OTGD-013-CAN-SR-006-02 | A slow ADC call crosses the bound — - **GIVEN** an ADC call returns after the bounded stop - **WHEN** its observation arrives - **THEN** the late sample is discarded and overrun cannot become valid evidence. | PARTIAL |
| OTGD-013-CAN-SR-007-01 | Link transition occurs after final origin check — - **GIVEN** a sensitive effect and a concurrent replacement connection - **WHEN** the final check/effect boundary executes - **THEN** the shared gate orders them and no old-origin action occurs in the replacement association. | PARTIAL |
| OTGD-013-CAN-SR-007-02 | Old ACK write fails late — - **GIVEN** account/device capture A is canceled and a new link connects - **WHEN** A's deferred acknowledgment write rejects - **THEN** the new association remains intact. | PASS |
| OTGD-013-CAN-SR-008-01 | Unsupported raw configuration receives opt-in — - **GIVEN** the protected ADC raw encoding/capacity does not support the requested operation - **WHEN** a non-null raw permission is supplied - **THEN** the driver refuses that unsupported operation without silently recording or dropping an opted-in purpose. | PARTIAL |
| OTGD-013-CAN-SR-008-02 | Normalized feature bytes change in transit — - **GIVEN** a device-signed exact projection - **WHEN** a value or identity is modified - **THEN** client digest admission and server signature verification reject the evidence. | PARTIAL |
| OTGD-013-CAN-SR-009-01 | Build output omits NVS encryption — - **GIVEN** a successful compiler process but altered generated security configuration - **WHEN** the helper inspects the build - **THEN** qualification fails despite the process exit code. | PASS |
| OTGD-013-CAN-SR-009-02 | Signing key is a public-readable symlink — - **GIVEN** a key path is symlinked or group/world-readable - **WHEN** the helper admits the key - **THEN** it refuses before invoking the build. | PASS |
| OTGD-013-CAN-SR-010-01 | ADC software builds without an attached board — - **GIVEN** core tests and board compilation pass - **WHEN** release readiness is reviewed - **THEN** physical key provisioning, contact/safety/calibration/timing and scientific qualification remain explicit pending evidence. | PASS |
| OTGD-013-CAN-SR-010-02 | Vendor assay SDK is undocumented — - **GIVEN** signed transport supports a compatible evidence schema - **WHEN** no actual approved acquisition SDK exists for the instrument - **THEN** capability remains unavailable and no assay value is fabricated. | PASS |
| OTGD-013-CAN-SR-011-01 | A replacement peer receives an old authentication callback — - **GIVEN** a BLE connection transitions to a different peer or generation - **WHEN** authentication or a command callback from the original peer arrives - **THEN** it cannot authorize the replacement association or deliver previous health data. | PARTIAL |
| OTGD-013-CAN-SR-011-02 | Pairing negotiates encryption without MITM — - **GIVEN** a peer lacks the physical passkey and offers unauthenticated encryption - **WHEN** the peripheral evaluates completed pairing - **THEN** it refuses commands, disconnects and produces no participant telemetry. | PARTIAL |
| OTGD-013-CAN-SR-011-03 | The current protected peer completes authenticated pairing — - **GIVEN** the current device peer completes Secure Connections with MITM bonding using its protected provisioned passkey - **WHEN** a command and notification are admitted under the same connection origin gate - **THEN** only that authenticated connection can send commands and receive its connection-targeted frames, while physical and clinical qualification remain separate. | PARTIAL |
