# OTGD-023: verification plan

Canonical: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md`; SHA-256 `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4`.
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
- `services/api/tests/test_capture_signing.py` — `bf0b38a0ec1eafef692a78ccb3d1bb0174d4f81b997a76c840b47ee1d2dc2751`
- `services/api/tests/test_vendor_evidence.py` — `ffb2ca5111d52df5d295f0e594a6eb00b17465c452c0abb21a4d2fb79a8930fe`

## Requirement and criterion cases

For each requirement, also exercise absent/null/malformed/unknown values, wrong owner/environment/generation, retired/revoked authority, duplicate same-body vs changed-body replay, delayed/out-of-order replies, cancellation/replacement and restart where applicable. For every numeric/string/time limit in the linked normative detailed contract, test equality plus the smallest representable increment below and above, including post-terminal immutability. Do not invent physical tolerances or treat a declaration as measured safety evidence.

### AND-DEV-001 — Device screen and association state

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-001`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-001-01 | Connect a demonstration device — **GIVEN** a supported phone and a discoverable synthetic peripheral **WHEN** the user selects Find device, chooses the listed device, and its handshake succeeds **THEN** the screen SHALL enter connected_simulator, show Simulated data, and enable only synthetic capture channels advertised by the handshake. | `apps/mobile/src/device/tests/protocol.test.ts:87` — local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance<br>`apps/mobile/tests/device-presentation.test.ts:16` — a saved reader alias does not become connected readiness or live battery | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-001-02 | Device connected but assay unavailable — **GIVEN** a connected reader advertising assay_ready=false **WHEN** the user proceeds to the saliva step **THEN** the step SHALL state that the assay is unavailable, offer its permitted sample-record or simulation workflow, and SHALL NOT report a chemical concentration or a completed assay merely because pairing succeeded. | `apps/mobile/tests/device-presentation.test.ts:16` — a saved reader alias does not become connected readiness or live battery<br>`apps/mobile/tests/acquisition.test.ts:1101` — binding reconnect reconciles old receipt then requires a new device proof in the current connection | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

### AND-DEV-002 — Runtime permissions and radio availability

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-002`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-002-01 | Permission denied without losing the check — **GIVEN** an existing draft check and a first discovery request **WHEN** Android denies the required permission **THEN** no scan SHALL begin, the draft SHALL remain intact, and the screen SHALL explain the missing permission and present an appropriate retry or settings action. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization<br>`apps/mobile/tests/device-presentation.test.ts:23` — permission, radio, reboot and unsupported reader failures have distinct recovery | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-002-02 | Radio disabled during discovery — **GIVEN** an active scan **WHEN** Bluetooth becomes unavailable or the app moves to the background **THEN** scanning SHALL stop, any progress indicator SHALL settle into a named recovery state, and no stale discovery result SHALL be represented as a live connection. | `apps/mobile/tests/device-presentation.test.ts:23` — permission, radio, reboot and unsupported reader failures have distinct recovery<br>`apps/mobile/tests/acquisition.test.ts:1478` — revoked consent, stale approval and reader substitution cannot invoke hardware | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `12`, `15-second`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-DEV-003 — Discovery identity and verified association

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-003`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-003-01 | Spoofed device name — **GIVEN** an unprovisioned peripheral advertising the expected name and service **WHEN** it claims that it is a validated reader **THEN** the app SHALL refuse verified association, retain an explicit unverified-device reason, and SHALL NOT ingest human measurements from that connection. | `apps/mobile/tests/acquisition.test.ts:1412` — explicit ECG raw choice uses a fresh signed recording receipt and the real bounded encoder before atomic encrypted local save<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-003-02 | Known binding belongs to another context — **GIVEN** a device credential that verifies cryptographically but has no permitted binding for the current account or study **WHEN** association is requested **THEN** the app SHALL reject participant capture and SHALL not disclose another participant's sessions or identity. | `apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture<br>`apps/mobile/tests/acquisition.test.ts:1412` — explicit ECG raw choice uses a fresh signed recording receipt and the real bounded encoder before atomic encrypted local save | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-003-03 | Replayed binding challenge and substituted key — **GIVEN** a previously consumed server challenge or a client-supplied replacement trust key **WHEN** association is retried under that challenge or key **THEN** binding SHALL fail without a new verified state; the client SHALL retain only its permitted simulator association and reveal no other owner identity. | `apps/mobile/tests/acquisition.test.ts:1412` — explicit ECG raw choice uses a fresh signed recording receipt and the real bounded encoder before atomic encrypted local save<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `680`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-DEV-004 — Capability handshake and clock evidence

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-004`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-004-01 | Compatible handshake — **GIVEN** matching protocol versions and subscribed events **WHEN** the clock exchanges complete **THEN** the association SHALL retain the narrowest valid observed offset interval and an uncertainty no smaller than the exchange and clock resolution permit. | `apps/mobile/src/device/tests/protocol.test.ts:80` — clock evidence retains all exchanges and chooses narrowest interval with resolution padding<br>`apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-004-02 | Counter restarts after device reboot — **GIVEN** an accepted boot ID and an in-progress acquisition **WHEN** a new boot ID or unexplained monotonic regression is observed **THEN** the affected acquisition SHALL become invalid, previous clock alignment SHALL be discarded, and a new handshake and capture attempt SHALL be required. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/protocol.test.ts:60` — capability source and calibration cannot promote an unprovisioned peripheral | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-004-03 | Cached capability cannot enable an offline reader — **GIVEN** a bound reader and a cached available human capability **WHEN** the user starts capture while offline after changing the wall clock **THEN** the app SHALL reject the qualified start and explain that current server authorization is required. | `apps/mobile/tests/acquisition.test.ts:1319` — approved research start freezes exact online study/configuration context and device binding before any acquisition<br>`apps/mobile/src/device/tests/protocol.test.ts:60` — capability source and calibration cannot promote an unprovisioned peripheral | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1002`, `1003`, `6`, `680`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-DEV-005 — Bounded transport and message integrity

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-005`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-005-01 | Small-MTU valid message — **GIVEN** ATT MTU 23 and a valid bounded message **WHEN** its fragments arrive in the supported order, including an identical duplicate **THEN** the receiver SHALL reconstruct the exact logical bytes once, verify CRC and envelope semantics, and acknowledge one accepted message without duplicate capture events. | `apps/mobile/src/device/tests/protocol.test.ts:22` — larger MTU, out-of-order fragments and identical duplicate reconstruct once<br>`apps/mobile/src/device/tests/physical.test.ts:284` — DER parsing rejects nonminimal/negative/zero/trailing encodings without claiming key verification | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-005-02 | Malformed fragment flood — **GIVEN** an established connection **WHEN** the peripheral supplies an oversized declared length, conflicting duplicate, or more than the allowed in-flight transfer **THEN** the receiver SHALL release bounded buffers, emit a named protocol failure, and SHALL not allocate memory proportional to attacker-provided lengths or store a partial successful reading. | `apps/mobile/src/device/tests/protocol.test.ts:15` — ATT MTU 23 carries eight logical bytes after the 12-byte header<br>`apps/mobile/src/device/tests/physical.test.ts:284` — DER parsing rejects nonminimal/negative/zero/trailing encodings without claiming key verification | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-005-03 | Signature valid for another measurement — **GIVEN** a valid device signature for payload A and a selected snapshot containing changed payload B values **WHEN** upload or finalization validates evidence **THEN** the exact normalized payload hash/mapping check SHALL reject B, retain a provenance failure, and SHALL not infer trust from source=validated_sensor. | `apps/mobile/src/device/tests/protocol.test.ts:15` — ATT MTU 23 carries eight logical bytes after the 12-byte header<br>`apps/mobile/src/device/tests/physical.test.ts:284` — DER parsing rejects nonminimal/negative/zero/trailing encodings without claiming key verification | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `1`, `12`, `23`, `3`, `8188 bytes`, `8192 bytes`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-DEV-006 — Command scoping, completion, and replay

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-006`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-006-01 | Capture-complete acknowledgment is lost — **GIVEN** one complete capture already stored locally **WHEN** the peripheral retransmits its identical completion message after an acknowledgment timeout **THEN** the receiver SHALL acknowledge the existing disposition and SHALL not create a second capture or a second sample. | `apps/mobile/src/device/tests/protocol.test.ts:67` — identity, changed message ID content and replay sequence are independently checked<br>`apps/mobile/src/device/tests/physical.test.ts:381` — signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-006-02 | Completion arrives before missing chunks — **GIVEN** an ECG or other multi-chunk capture with a missing chunk **WHEN** capture_complete arrives **THEN** the component SHALL remain incomplete and become invalid at its bounded timeout unless the missing bytes and final digest are verified; a notification alone SHALL not count as success. | `apps/mobile/src/device/tests/protocol.test.ts:67` — identity, changed message ID content and replay sequence are independently checked<br>`apps/mobile/src/device/tests/physical.test.ts:381` — signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `0`, `1.0`, `120-second`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-DEV-007 — Disconnect, cancellation, and forgetting

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-007`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-007-01 | User cancels during capture — **GIVEN** an active device acquisition **WHEN** the user selects Disconnect, Cancel, or Forget before any wider-draft confirmation **THEN** the app SHALL send a best-effort cancel command, stop accepting that attempt's later payloads, retain its canceled/invalid disposition, and return to a recoverable device state. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-007-02 | Late event after reconnect — **GIVEN** a new boot or capture attempt after reconnection **WHEN** a queued event from the prior attempt arrives **THEN** the receiver SHALL reject it by identity and SHALL not populate the new check with a stale reading. | `apps/mobile/tests/acquisition.test.ts:870` — reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

Boundary inputs named in normative text (apply their actual units and semantics, not these bare numbers in isolation): `5`. Exact inclusive/exclusive comparisons and adjacent overflow/underflow must be asserted; see canonical detailed contract for the complete bounds.

### AND-DEV-008 — Platform parity, secret handling, and verification

Normative acceptance source: `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md` / `AND-DEV-008`.

Prerequisites and limits: NOT_RUN physical/native: actual Android/iOS permission, background/foreground, radio/camera/touch/secure-storage and hardware timing cases on supported devices; fixtures/browser DOM do not establish those outcomes.

| Stable case | Canonical criterion / expected observation | Existing related check (source, not execution) | Status and required supplement |
|---|---|---|---|
| OTGD-023-AND-DEV-008-01 | Simulator fixture on either platform — **GIVEN** the same synthetic message sequence on Android and iOS **WHEN** both clients complete a check **THEN** each SHALL preserve simulated provenance and matching semantic records even though OS peripheral handles differ. | `apps/mobile/tests/device-presentation.test.ts:23` — permission, radio, reboot and unsupported reader failures have distinct recovery<br>`apps/mobile/src/device/tests/protocol.test.ts:87` — local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |
| OTGD-023-AND-DEV-008-02 | Demo configuration copied into production — **GIVEN** a production build with no approved provisioned device **WHEN** a local demo file attempts to set a verified binding or validated source **THEN** the claim SHALL fail independent verification and SHALL never unlock human capture or inference. | `apps/mobile/src/device/tests/protocol.test.ts:87` — local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance<br>`apps/mobile/src/device/tests/physical.test.ts:550` — actual framed signed test peripheral requires verified binding before authorized capture | NOT_RUN: run related assertions, inspect full canonical case and add/execute missing acceptance assertions; no complete scenario-coverage claim. |

## Execution and evidence handoff

Before running: PM freezes implementation/tests/contracts; capture HEAD, changed/untracked implementation hashes and tool versions, confirm canonical hash still matches, and record actual clock/environment/commands. Log each check under `reports/` or a PM-designated immutable attempt path; preserve JUnit/coverage/Playwright traces/screenshots/performance JSON and compute SHA-256 of actual artifacts. Shared passing suites can serve this dossier only when its relevant assertions and exact binding are explicit.

Record each case PASS/FAIL/BLOCKED/NOT_RUN in `test-results.md`, with exit/result/timestamp and evidence path/hash. A historical file existing in reports is not a new execution. Required checks unavailable on this runner remain BLOCKED; neither design review nor npm tests substitute for native, firmware, physical or scientific evidence.

## Reactivated verification audit

Observed checkpoint `1891f8b7f06f6279e7f86371a0798cd373813fd4` plus active writers’ working-tree edits, 2026-10-25T06:53:56.344429+00:00. This is not source freeze. Original planning HEAD and prior no-execution record above remain historical. Canonical hash above is rebound to the reconciled current source; OTGD-001 and OTGD-047 changed. Existing411 requirements /782 case IDs are retained. No Docker/build/probe or suite execution performed by this verifier.

### Alcohol dependency and acquisition-boundary audit

Mapped existing cases: OTGD-019-AND-ALC-001-02, AND-ALC-004-02; related AND-DEV-004, AND-CHECK-002, AND-STUDY-003/004.

Assertion adequacy inspected: Read operator-governance tests: configuration/calibration at -1ms, equality and +1ms; expiry history/body/hash/decisions immutable; calibration failure distinguished from still-current configuration. Current SOFTWARE_ADAPTERS/PHYSICAL_DRIVERS contain no alcohol entry and capability reason is HUMAN_ADAPTER_UNIMPLEMENTED. Four explicitly hypothetical HTTP grant/start cases expire before still-valid grant end, require403 APPROVED_REGISTRY_VERSION_REQUIRED, zero sign_start calls, no persisted start/alcohol and unchanged issued receipt. Mobile three new cases verify strict configuration selection before expiry, fresh absent inventory overrides stale cached availability with zero grant/nonce/hardware events, and a hypothetical returned authoritative-start refusal leaves invalid null alcohol and zero acquisition events.

Remaining limits: Client refusal transport is controlled, not an integrated real breath instrument. No qualified driver exists. Direct participant recalibration-specific start/recovery remains BLOCKED by absent instrument; generic server refusal must not be relabeled a diagnosis. Server -1ms/equality/+1ms and hypothetical grant race have reported focused execution; mobile author report/release and final gates pending.


## Final corrected source evidence — e89897cc852a

# OTGD-023 current verification plan proposal

Candidate `e89897cc852a111b131eaf5c2caaf163ef201a48`; canonical `openspec/changes/production-mobile-platform/specs/android-device-pairing/spec.md`; SHA256 `c772a370e6d80b6568ad3d210081934ac57ecb9e7449e7e776efeb776cdd98c4`.

Proposed repository destination: `docs/factory/otgd-20261025-0555/specs/OTGD-023/test-plan.md`. External review artifact only; PM controls import.

All 19 stable cases / 8 requirements are preserved. The exact GIVEN/WHEN/THEN wording and negative/boundary/recovery clauses are in `test-results.md` and the central `case-evidence.json`; no renamed IDs or weakened criteria.

Current execution commands (already executed by PM/current CI where their raw observations are bound):

- `python scripts/ci_gate.py unit-coverage`
- `python scripts/ci_gate.py live-dependencies`
- `Exact compiler, executable and arduino-cli commands: immutable .github/workflows/native-build.yml; actual ci-firmware.log and ci-protected-reader.log retained.`

Shared full local command: `python scripts/run_all_gates.py`. Its independent local final receipt confirms all7 gates passed. No verifier tests or service mutations were run. Current CI exact-tree run 40185247204 passed all14 mandatory jobs. Exact workflow/source bindings and named artifacts are retained in `../../final-ci-admission.json` and `../../source-assertions.json`.

Each remaining clause requires the minimal evidence/action recorded beside that case. Review meaningful existing shared assertions/helpers/control flow before requesting any extra execution. After correction2/2, unresolved evidence does not authorize a third source correction or a broader test project. Native/hardware/study/deployment prerequisites remain separately typed.

| Stable case | Planned assertion | Current disposition |
|---|---|---|
| OTGD-023-AND-DEV-001-01 | Connect a demonstration device — - **GIVEN** a supported phone and a discoverable synthetic peripheral - **WHEN** the user selects Find device, chooses the listed device, and its handshake succeeds - **THEN** the screen SHALL enter connected_simulator, show Simulated data, and enable only synthetic capture channels advertised by the handshake. | PARTIAL |
| OTGD-023-AND-DEV-001-02 | Device connected but assay unavailable — - **GIVEN** a connected reader advertising assay_ready=false - **WHEN** the user proceeds to the saliva step - **THEN** the step SHALL state that the assay is unavailable, offer its permitted sample-record or simulation workflow, and SHALL NOT report a chemical concentration or a completed assay merely because pairing succeeded. | PARTIAL |
| OTGD-023-AND-DEV-002-01 | Permission denied without losing the check — - **GIVEN** an existing draft check and a first discovery request - **WHEN** Android denies the required permission - **THEN** no scan SHALL begin, the draft SHALL remain intact, and the screen SHALL explain the missing permission and present an appropriate retry or settings action. | BLOCKED |
| OTGD-023-AND-DEV-002-02 | Radio disabled during discovery — - **GIVEN** an active scan - **WHEN** Bluetooth becomes unavailable or the app moves to the background - **THEN** scanning SHALL stop, any progress indicator SHALL settle into a named recovery state, and no stale discovery result SHALL be represented as a live connection. | BLOCKED |
| OTGD-023-AND-DEV-003-01 | Spoofed device name — - **GIVEN** an unprovisioned peripheral advertising the expected name and service - **WHEN** it claims that it is a validated reader - **THEN** the app SHALL refuse verified association, retain an explicit unverified-device reason, and SHALL NOT ingest human measurements from that connection. | PARTIAL |
| OTGD-023-AND-DEV-003-02 | Known binding belongs to another context — - **GIVEN** a device credential that verifies cryptographically but has no permitted binding for the current account or study - **WHEN** association is requested - **THEN** the app SHALL reject participant capture and SHALL not disclose another participant's sessions or identity. | PARTIAL |
| OTGD-023-AND-DEV-003-03 | Replayed binding challenge and substituted key — - **GIVEN** a previously consumed server challenge or a client-supplied replacement trust key - **WHEN** association is retried under that challenge or key - **THEN** binding SHALL fail without a new verified state; the client SHALL retain only its permitted simulator association and reveal no other owner identity. | PARTIAL |
| OTGD-023-AND-DEV-004-01 | Compatible handshake — - **GIVEN** matching protocol versions and subscribed events - **WHEN** the clock exchanges complete - **THEN** the association SHALL retain the narrowest valid observed offset interval and an uncertainty no smaller than the exchange and clock resolution permit. | PASS |
| OTGD-023-AND-DEV-004-02 | Counter restarts after device reboot — - **GIVEN** an accepted boot ID and an in-progress acquisition - **WHEN** a new boot ID or unexplained monotonic regression is observed - **THEN** the affected acquisition SHALL become invalid, previous clock alignment SHALL be discarded, and a new handshake and capture attempt SHALL be required. | PARTIAL |
| OTGD-023-AND-DEV-004-03 | Cached capability cannot enable an offline reader — - **GIVEN** a bound reader and a cached available human capability - **WHEN** the user starts capture while offline after changing the wall clock - **THEN** the app SHALL reject the qualified start and explain that current server authorization is required. | PARTIAL |
| OTGD-023-AND-DEV-005-01 | Small-MTU valid message — - **GIVEN** ATT MTU 23 and a valid bounded message - **WHEN** its fragments arrive in the supported order, including an identical duplicate - **THEN** the receiver SHALL reconstruct the exact logical bytes once, verify CRC and envelope semantics, and acknowledge one accepted message without duplicate capture events. | PARTIAL |
| OTGD-023-AND-DEV-005-02 | Malformed fragment flood — - **GIVEN** an established connection - **WHEN** the peripheral supplies an oversized declared length, conflicting duplicate, or more than the allowed in-flight transfer - **THEN** the receiver SHALL release bounded buffers, emit a named protocol failure, and SHALL not allocate memory proportional to attacker-provided lengths or store a partial successful reading. | PARTIAL |
| OTGD-023-AND-DEV-005-03 | Signature valid for another measurement — - **GIVEN** a valid device signature for payload A and a selected snapshot containing changed payload B values - **WHEN** upload or finalization validates evidence - **THEN** the exact normalized payload hash/mapping check SHALL reject B, retain a provenance failure, and SHALL not infer trust from source=validated_sensor. | PARTIAL |
| OTGD-023-AND-DEV-006-01 | Capture-complete acknowledgment is lost — - **GIVEN** one complete capture already stored locally - **WHEN** the peripheral retransmits its identical completion message after an acknowledgment timeout - **THEN** the receiver SHALL acknowledge the existing disposition and SHALL not create a second capture or a second sample. | PARTIAL |
| OTGD-023-AND-DEV-006-02 | Completion arrives before missing chunks — - **GIVEN** an ECG or other multi-chunk capture with a missing chunk - **WHEN** capture_complete arrives - **THEN** the component SHALL remain incomplete and become invalid at its bounded timeout unless the missing bytes and final digest are verified; a notification alone SHALL not count as success. | NOT_RUN |
| OTGD-023-AND-DEV-007-01 | User cancels during capture — - **GIVEN** an active device acquisition - **WHEN** the user selects Disconnect, Cancel, or Forget before any wider-draft confirmation - **THEN** the app SHALL send a best-effort cancel command, stop accepting that attempt's later payloads, retain its canceled/invalid disposition, and return to a recoverable device state. | PARTIAL |
| OTGD-023-AND-DEV-007-02 | Late event after reconnect — - **GIVEN** a new boot or capture attempt after reconnection - **WHEN** a queued event from the prior attempt arrives - **THEN** the receiver SHALL reject it by identity and SHALL not populate the new check with a stale reading. | PARTIAL |
| OTGD-023-AND-DEV-008-01 | Simulator fixture on either platform — - **GIVEN** the same synthetic message sequence on Android and iOS - **WHEN** both clients complete a check - **THEN** each SHALL preserve simulated provenance and matching semantic records even though OS peripheral handles differ. | BLOCKED |
| OTGD-023-AND-DEV-008-02 | Demo configuration copied into production — - **GIVEN** a production build with no approved provisioned device - **WHEN** a local demo file attempts to set a verified binding or validated source - **THEN** the claim SHALL fail independent verification and SHALL never unlock human capture or inference. | PARTIAL |
