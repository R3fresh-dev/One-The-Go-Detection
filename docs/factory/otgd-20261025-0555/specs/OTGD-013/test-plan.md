# OTGD-013: verification plan

Canonical: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md`; SHA-256 `df6d046105c408da0217d264ba7d9ec83e11682c55933c65753c12c196a7fb29`.
Planning snapshot HEAD: `33901a1ff785cd28e351d935be510d184fb7f8e2`; approved implementation baseline: `0844868aa543af4ab75ac5065ad48cf807b86bb3`. This is a mutable audit snapshot, not a frozen execution candidate.

Owner: `/root/verification`, verification specialist; OpenAI `gpt-6.1-sol/high` requested explicitly in PM dispatch; effective model identifier is not independently exposed inside this worker. Decisions: D-001–005 v1 and D-006 v3 acknowledged through native messaging; D-006 v1/v2 retained as superseded method history. See `../../decisions.md`, `../../impact-register.md` and `../../reports/verification-plan.md`.

Stage: PLANNED / NOT_RUN. Test-source symbols below are related existing checks, not a claim that every assertion is adequate or has passed. Static indexing does not establish runtime coverage. Every stated canonical scenario must execute and meet its full THEN conditions; use the source reference for complete GIVEN/WHEN context. Missing exact-case coverage remains a software verification gap until a meaningful assertion is inspected/added and executed. No historical test/CI result is adopted.

Use the shared command catalog and source-binding rules in `../../reports/verification-plan.md`. API checks: C-UNIT/C-PG; mobile business checks: C-MOBILE; visible flows: C-ATDD/C-COMP; native: C-ANDROID/C-IOS; firmware: C-FW/C-SECURE. Real runtime: C-DOCKER/C-LOCAL/C-PERF. Contracts: C-SPEC/C-SCHEMA/C-CDK. Applicable external prerequisites are recorded per requirement below.

Acceptance: no failure/error/skip/xfail/zero-case report; Python and TypeScript business-module coverage independently strictly >80%, each store helper >80% without excluded statements. Performance: all 400 writes, p95 <1000 ms, p99 <2000 ms, result <=15 s. Require fresh exact-source evidence, scoped independent signoffs and council decision before acceptance.

## Existing mapped test source bindings

These SHA-256 bindings identify inspected source at planning time. Any edit requires remapping and a fresh execution binding.

- `apps/mobile/src/device/tests/physical.test.ts` — `23d4938d5015dc6cca7f978a44c3d823f0e9aef3f52631a87898ae5d28c82d9d`
- `apps/mobile/src/device/tests/protocol.test.ts` — `4a919e3666e80fe6917744170312b773c88deda8f2f08d63a35d16218e5d382c`
- `apps/mobile/tests/acquisition.test.ts` — `797e9858167b9b80bff401e0b66c3fda1f9ae56c8f007fbe5b10c4aeb0b159be`
- `apps/mobile/tests/device-presentation.test.ts` — `11e79b59ead32c0a6bc4fa818784bc00347f337cfb5dff71d13534673064600a`
- `firmware/tests/signed_reader_acquisition_test.cpp` — `fcab5453fa6058f9ec5c02c9aa30044e979896007eaf06afb7129287af926e7a`
- `firmware/tests/signed_reader_core_test.cpp` — `f00b6d2edc4b39911caf5418acb1c70d562a44600f8e158d9bb6cfa91753a386`
- `firmware/tests/signed_reader_grant_test.cpp` — `f398cef88638601878d2182ed671be8624c14b3dcd9e5c4e1c23041e05d93b48`
- `infra/test/test_secure_reader_build.py` — `beb1569ec43a14c535b13f29a77222e3d927b8a5c75f38e4bdf630eb79a7cc28`
- `services/api/tests/test_capture_policy.py` — `971a808c066b099c4006aab592d052aa3867d08cdfb10fbd0eb2f5288e5febae`
- `services/api/tests/test_capture_signing.py` — `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`
- `services/api/tests/test_operator_governance.py` — `4d512a3ad9f7c65b69ee09d94fb471799d1aff63a5bc4c34140526dcac280ae7`
- `services/api/tests/test_participant_acquisition.py` — `a9113ffb30c7907e12aad494ddfdf7d83afc96ef5f3d8c0668768158c2948b57`
- `services/api/tests/test_vendor_evidence.py` — `ffb2ca5111d52df5d295f0e594a6eb00b17465c452c0abb21a4d2fb79a8930fe`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### CAN-SR-001 — Admit a distinct bounded physical reader dialect

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-001`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-001-01 | A physical advertisement requests simulator handling — **GIVEN** a reader advertises prototype_sensor under an unknown protocol identifier **WHEN** the app connects **THEN** the association is refused before capture. | `apps/mobile/src/device/tests/physical.test.ts:231` — physical advertisement has a distinct bounded dialect and never a synthetic/validated source<br>`apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-001-02 | Compatible reader awaits trust — **GIVEN** a bounded compatible physical capability **WHEN** the app connects without a verified binding receipt **THEN** measurement remains unavailable until server-backed binding and fresh authorization succeed. | `apps/mobile/src/device/tests/physical.test.ts:231` — physical advertisement has a distinct bounded dialect and never a synthetic/validated source<br>`apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-002 — Preserve exact device binding proof and protected keys

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-002`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-002-01 | Binding receipt references another device — **GIVEN** successful proof from device A **WHEN** a receipt references device B or another owner generation **THEN** the native association remains untrusted. | `apps/mobile/tests/acquisition.test.ts:1158` — late binding receipt cannot bind a foreign replacement or erase a newer same-owner intent<br>`services/api/tests/test_operator_governance.py:492` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-002-02 | Stock SDK lacks protected NVS — **GIVEN** a stock SDK compilation without NVS encryption **WHEN** the reader starts **THEN** it refuses protected-reader advertising and emits no fabricated measurement. | `services/api/tests/test_operator_governance.py:492` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot<br>`apps/mobile/tests/acquisition.test.ts:1158` — late binding receipt cannot bind a foreign replacement or erase a newer same-owner intent | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-003 — Verify a fresh scoped server start signature on the reader

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-003`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-003-01 | Phone alters maximum acquisition duration — **GIVEN** an authentic server token binds15000ms **WHEN** the phone requests a different channel, duration, context or configuration **THEN** the reader refuses start before touching acquisition hardware. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`services/api/tests/test_operator_governance.py:492` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-003-02 | Token includes a replacement verification key — **GIVEN** the device trusts an offline provisioned server signer **WHEN** a caller substitutes an SPKI or signer label in the token **THEN** signature admission fails. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`services/api/tests/test_operator_governance.py:492` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### CAN-SR-004 — Enforce signed expiry without inventing device wall time

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-004`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-004-01 | Shortened grant reaches expiry boundary — **GIVEN** a signed15s lifetime and nonce age15s **WHEN** START arrives **THEN** the reader refuses it even if the general nonce TTL is60s. | `services/api/tests/test_operator_governance.py:492` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot<br>`apps/mobile/src/device/tests/physical.test.ts:340` — fresh server grant binds the prepared nonce, boot, context and exact 60-second lifetime | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-004-02 | Reversed or malformed timestamp — **GIVEN** expiry precedes issue or contains invalid UTC syntax **WHEN** the reader validates the token **THEN** no hardware acquisition begins. | `services/api/tests/test_operator_governance.py:492` — test_bound_reader_start_token_comes_from_real_owned_proof_and_exact_frozen_boot<br>`apps/mobile/src/device/tests/physical.test.ts:340` — fresh server grant binds the prepared nonce, boot, context and exact 60-second lifetime | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-005 — Acquire actual bounded ADC observations from protected material

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-005`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-005-01 | Sensor contact is absent — **GIVEN** a provisioned ADC channel with a separate contact input **WHEN** contact indicates no attached sensor **THEN** acquisition stops and no valid heart rate or ECG feature is produced. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`services/api/tests/test_operator_governance.py:291` — test_invalid_key_calibration_and_configuration_scopes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-005-02 | Loop misses samples — **GIVEN** measured monotonic acquisition times skip scheduled observations **WHEN** the bounded extractor processes the next actual sample **THEN** it records explicit gaps and invalidates quality without generating missing values. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`services/api/tests/test_operator_governance.py:291` — test_invalid_key_calibration_and_configuration_scopes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-006 — Stop hardware independently of transport pressure

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-006`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-006-01 | Notifications are congested at cutoff — **GIVEN** the TX queue cannot publish another message **WHEN** the acquisition cutoff arrives **THEN** the driver stops regardless of queued acknowledgments. | `services/api/tests/test_operator_governance.py:598` — test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec<br>`apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-006-02 | A slow ADC call crosses the bound — **GIVEN** an ADC call returns after the bounded stop **WHEN** its observation arrives **THEN** the late sample is discarded and overrun cannot become valid evidence. | `services/api/tests/test_operator_governance.py:598` — test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec<br>`apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-007 — Isolate connection-origin effects and replay privacy

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-007`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-007-01 | Link transition occurs after final origin check — **GIVEN** a sensitive effect and a concurrent replacement connection **WHEN** the final check/effect boundary executes **THEN** the shared gate orders them and no old-origin action occurs in the replacement association. | `apps/mobile/src/device/tests/physical.test.ts:632` — delayed old acknowledgment rejection cannot invalidate replacement association<br>`apps/mobile/tests/acquisition.test.ts:1101` — binding reconnect reconciles old receipt then requires a new device proof in the current connection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-007-02 | Old ACK write fails late — **GIVEN** account/device capture A is canceled and a new link connects **WHEN** A's deferred acknowledgment write rejects **THEN** the new association remains intact. | `apps/mobile/src/device/tests/physical.test.ts:632` — delayed old acknowledgment rejection cannot invalidate replacement association<br>`apps/mobile/tests/acquisition.test.ts:1101` — binding reconnect reconciles old receipt then requires a new device proof in the current connection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-008 — Bind raw purpose and immutable signed evidence

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-008`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-008-01 | Unsupported raw configuration receives opt-in — **GIVEN** the protected ADC raw encoding/capacity does not support the requested operation **WHEN** a non-null raw permission is supplied **THEN** the driver refuses that unsupported operation without silently recording or dropping an opted-in purpose. | `apps/mobile/src/device/tests/physical.test.ts:713` — opt-in ECG handoff preserves measured signed chunks and refuses bounds/scope changes<br>`apps/mobile/tests/acquisition.test.ts:1412` — explicit ECG raw choice uses a fresh signed recording receipt and the real bounded encoder before atomic encrypted local save | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-008-02 | Normalized feature bytes change in transit — **GIVEN** a device-signed exact projection **WHEN** a value or identity is modified **THEN** client digest admission and server signature verification reject the evidence. | `apps/mobile/tests/acquisition.test.ts:1366` — actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence<br>`apps/mobile/src/device/tests/physical.test.ts:713` — opt-in ECG handoff preserves measured signed chunks and refuses bounds/scope changes | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-009 — Build and qualify the protected SDK branch explicitly

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-009`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-009-01 | Build output omits NVS encryption — **GIVEN** a successful compiler process but altered generated security configuration **WHEN** the helper inspects the build **THEN** qualification fails despite the process exit code. | `services/api/tests/test_capture_signing.py:88` — test_local_private_key_custody_and_retained_identity_fail_closed<br>`infra/test/test_secure_reader_build.py:42` — test_only_private_rsa3072_build_key_is_admitted | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-009-02 | Signing key is a public-readable symlink — **GIVEN** a key path is symlinked or group/world-readable **WHEN** the helper admits the key **THEN** it refuses before invoking the build. | `services/api/tests/test_capture_signing.py:88` — test_local_private_key_custody_and_retained_identity_fail_closed<br>`infra/test/test_secure_reader_build.py:42` — test_only_private_rsa3072_build_key_is_admitted | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-010 — Preserve external qualification and unknown-driver limits

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-010`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-010-01 | ADC software builds without an attached board — **GIVEN** core tests and board compilation pass **WHEN** release readiness is reviewed **THEN** physical key provisioning, contact/safety/calibration/timing and scientific qualification remain explicit pending evidence. | `apps/mobile/src/device/tests/physical.test.ts:381` — signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest<br>`services/api/tests/test_operator_governance.py:238` — test_changed_scope_cannot_reuse_scientific_hash_or_old_qualification | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-010-02 | Vendor assay SDK is undocumented — **GIVEN** signed transport supports a compatible evidence schema **WHEN** no actual approved acquisition SDK exists for the instrument **THEN** capability remains unavailable and no assay value is fabricated. | `services/api/tests/test_operator_governance.py:598` — test_signed_reader_transport_and_recording_approval_cannot_invent_a_sampling_driver_or_raw_codec<br>`apps/mobile/src/device/tests/protocol.test.ts:60` — capability source and calibration cannot promote an unprovisioned peripheral | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### CAN-SR-011 — Require authenticated encrypted BLE before human telemetry

Normative acceptance source: `openspec/changes/canonical-signed-reader-acquisition/specs/signed-reader-acquisition/spec.md` / `CAN-SR-011`.

Prerequisites and limits: NOT_RUN firmware target builds; BLOCKED physical provisioning, protected-key/eFuse/secure-boot configuration, authenticated BLE pairing, contact/calibration/safety and sensor qualification. No flash or provisioning authorized.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-013-CAN-SR-011-01 | A replacement peer receives an old authentication callback — **GIVEN** a BLE connection transitions to a different peer or generation **WHEN** authentication or a command callback from the original peer arrives **THEN** it cannot authorize the replacement association or deliver previous health data. | `apps/mobile/src/device/tests/physical.test.ts:632` — delayed old acknowledgment rejection cannot invalidate replacement association<br>`apps/mobile/tests/acquisition.test.ts:1101` — binding reconnect reconciles old receipt then requires a new device proof in the current connection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-011-02 | Pairing negotiates encryption without MITM — **GIVEN** a peer lacks the physical passkey and offers unauthenticated encryption **WHEN** the peripheral evaluates completed pairing **THEN** it refuses commands, disconnects and produces no participant telemetry. | `apps/mobile/src/device/tests/protocol.test.ts:60` — capability source and calibration cannot promote an unprovisioned peripheral<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-013-CAN-SR-011-03 | The current protected peer completes authenticated pairing — **GIVEN** the current device peer completes Secure Connections with MITM bonding using its protected provisioned passkey **WHEN** a command and notification are admitted under the same connection origin gate **THEN** only that authenticated connection can send commands and receive its connection-targeted frames, while physical and clinical qualification remain separate. | `services/api/tests/test_capture_signing.py:165` — test_cloud_signing_provider_failures_are_controlled_retryable_and_publish_no_authority<br>`apps/mobile/tests/device-presentation.test.ts:23` — permission, radio, reboot and unsupported reader failures have distinct recovery | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.


## Final corrected source evidence — e89897cc852a

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
