# Low-level design

Architecture reconciliation | 2026-10-25 UTC | Implementable software contracts; execution evidence is tracked separately

## 1. Scope and implementation status

This document defines module boundaries, record semantics, acquisition timing, transport, persistence, model gating, errors, and verification for the design in [HLD.md](HLD.md). Current source includes mobile/native, API/worker, signed-reader, offline evaluation and release-tooling implementations. Physical sensing/assay qualification, scientific approvals and deployment are separate evidence. The original serial and local measurement-only examples remain limited fictional tools; they are not the complete implementation inventory.

Normative product requirements are indexed in [FULL_SPECIFICATION.md](FULL_SPECIFICATION.md). Structural exchange contracts are in [../contracts/](../contracts/). The JSON Schemas use Draft 2020-12; API design uses OpenAPI 3.1. Version changes that alter units, meaning, required fields, timing, or model compatibility require migration and a new manifest, not merely a renamed UI label.

## 2. Module layout and source ownership

| Module | Owns | Explicit boundary |
|---|---|---|
| `firmware/nano_esp32_signed_reader`, `firmware/secure_reader` | Bounded framing, protected keys, server grants, ADC/selected vendor acquisition and shutdown | No clinical inference, fabricated assay or cloud credentials; stock SDK is not protected-runtime proof |
| `apps/mobile/src/controller.ts`, `src/core`, `src/services` | Workflow, immutable contexts/attempts, explicit upload, authorization and recovery fences | Cannot release scientific authority or mutate finalized evidence |
| `apps/mobile/src/platform/storage.native.ts`, `modules/storage-security` | SQLCipher account/environment storage and OS key/access protection | No plaintext fallback; same-account reauthentication before retained signed-out reads |
| `apps/mobile/modules/reaction-task` | Kotlin/Swift stimulus and input timing | No network or storage operation on each scored-trial path; native callbacks remain physically unqualified |
| `apps/mobile/modules/eye-capture` | Native bounded ROI/frame extraction and reviewed stimulus lifecycle | Pixels need released geometry for mm; callbacks do not measure photon onset |
| `apps/mobile/src/device`, `modules/device-transport` | BLE association, framing, signed-reader scope and native radio lifecycle | Reject unexpected identity/boot/attempt/workspace; server verifies signatures |
| `services/api/otgd/main.py`, `domain.py`, `dto.py`, `auth.py` | Routes, typed validation, ownership/generation, idempotency and finalization | Never trusts owner/role/approval claims in JSON |
| `services/api/otgd/operator_governance.py`, `participant_acquisition.py`, `lab_handoff.py` | Independent registry lifecycle, exact instructions, current start and laboratory handoff | Installed adapter and participant declaration are distinct from scientific/safety authority |
| `services/api/otgd/model_engine.py`, `cardiac_authority.py`, `optical_evidence.py` | Bounded data-only artifact execution and exact feature/authority admission | No ordinary/guest score; narrow HR interval and diameter exceptions cannot qualify other channels |
| `services/api/otgd/worker.py`, `storage.py`, `raw_*`, `recovery_*`, `journal_continuity.py` | Outbox, fenced leases, version-pinned bytes, privacy and retained recovery admission | At-least-once delivery; no stale publication or restored authority from a database flag |
| `tools/model_evaluation.py` | Frozen grouped splits, train-only fitting, ablations and denominators | Editable input references cannot authenticate independent assessment, custody or approval |
| `infra`, `deploy`, `apps/mobile/modules/scripts` | Local runtime, isolated cloud designs, signed browser/store and fictional preview tooling | Plan/build/probe/provider acceptance/public availability are separate outcomes |

The tables describe inspected source responsibilities. The full specification and pending OpenSpec requirements remain the acceptance baseline; related tests must be executed for the exact candidate before implementation is called verified. The [shared contracts](../openspec/changes/production-mobile-platform/shared-contracts.md) define cross-feature DTOs; [platform contracts](../openspec/changes/production-mobile-platform/platform-contract.md) define durable infrastructure semantics. Later explicit model/raw/recovery/release amendments refine their legacy release wording and bounds within their declared scope.

## 3. Identifiers, clocks, and immutable records

Use UUIDs for session, sample, task, result, and artifact identifiers. A device has a provisioned identifier plus a fresh boot identifier after restart. Device boot identity distinguishes a reset counter from the continuation of an earlier capture. The synthetic serial example uses a visibly synthetic device identifier and a monotonic sequence for its limited demonstration scope.

Use RFC 3339 UTC timestamps for acquisition start/end, sample collection, assay completion, finalization, and evaluation. Store monotonic elapsed milliseconds for on-device event order and task responses. Do not calculate reaction times by subtracting wall-clock timestamps.

Clock alignment records offset and uncertainty. Synthetic BLE exercises use the bounded synchronization exchange; signed ADC/vendor evidence retains its actual host/device monotonic observations and explicit unqualified wall-clock/host-receive flags. No synchronization response qualifies physical sensor onset. A device reboot, clock discontinuity, or inability to align a required component triggers a timing quality failure. Only the exact independently released HR server-interval policy described below can admit its named unqualified-clock flags; it never deletes those flags or invents sampling cadence.

Each research manifest defines the maximum acquisition span and maximum clock uncertainty it supports. These limits have no clinical defaults. P0 may exercise proposed integration limits, but they cannot authorize inference. Store both target_at, the time represented by the check, and evaluated_at, when analysis finishes. A laboratory result returned later remains tied to its original collection time.

The submitted acquisition snapshot uses capture_completed_at for client capture completion; the server records finalized_at separately when it freezes the accepted snapshot. Unfinished or canceled draft state is not serialized as a completed snapshot. Not-collected components have null acquisition timestamps and features; their actual trial counts are zero. Allocated sample, task, and configuration identifiers may identify a planned attempt but do not establish that acquisition occurred. When saliva was not collected, its collection time is null and the saliva measurement list is empty. With no observed acquisitions, acquisition_span_ms is null. Unrun analytes use not_measured with null analysis time, method, instrument, and calibration; an actual collected specimen is still required for such an analyte record.

Finalized snapshots are immutable. Application digests use RFC 8785 JCS over validated JSON, UTF-8 then SHA-256, with cross-language fixtures in Python/TypeScript. Reject duplicate keys, nonfinite numbers, invalid Unicode and out-of-range interoperable integers. Display rounding must not change hashed data. The old Python demo's sorted/compact serialization is not an alternative application canonicalizer. Reacquisition after local or remote finalization creates a new session/target and `supersedes_session_id`; same-specimen report correction uses its separate authorized immutable companion-revision contract. Derived results reference the precise snapshot and evidence digests.

## 4. Saliva measurement contract

The measurement envelope contains measurement_id, sample_id, analyte, qualifier, value_ng_ml, unit, assay_basis, concentration_basis, correction_status, limits, source, method_id, calibration_id, cartridge_lot, collected_at, measured_at, and quality_flags. Original reported value/unit/qualifier and an optional uncertainty are retained when importing reference data. Sample-level collection method, volume, and dilution are recorded once in the session's sample object.

Canonical analytes are THC, THC_COOH, and OH11_THC. Canonical concentration unit is ng/mL. Convert pg/mL by dividing by 1000; therefore 15 pg/mL becomes 0.015 ng/mL. Preserve the original report so the conversion is auditable. Never infer a saliva-to-blood conversion or interpret a quantification limit as an impairment threshold.

| qualifier | value_ng_ml | Required interpretation |
|---|---|---|
| quantified | Nonnegative number inside the validated quantification interval | Exact reported quantitative result; limits and calibration must be available for model eligibility |
| below_loq | null | Below the quantifiable range; retain the applicable limit and the original qualifier; detection is not inferred |
| above_range | null | Above the validated interval; retain the upper bound; do not substitute that bound as an exact result |
| not_detected | null | No detection using the stated method and limit; not proof of zero analyte |
| not_measured | null | Channel absent or not run; not a chemical negative |
| invalid | null | Collection, control, sensor, or analytical failure; reason flags required |

A laboratory report stating only BLQ or <LLOQ does not necessarily assert detection. Preserve that original qualifier and do not convert it to a claim that a metabolite was detected.

The schema covers structure and simple conditional rules; ingestion must also enforce limit order, numeric finiteness, value-within-range, timestamp order, sample identity, and unit consistency. Import adapters must not silently clip an over-range value. Reanalysis after dilution produces a linked new measurement with its actual method, dilution, and result; it does not edit the original record.

assay_basis is free, total_after_hydrolysis, or unspecified. The unspecified state allows preservation of an unresolved import but blocks a model requiring a defined form. A model must enumerate method/basis combinations it accepts. Laboratory hydrolysis benchmarks do not establish the performance of a direct cartridge measuring only free analyte.

concentration_basis is neat_oral_fluid, collected_mixture, or unspecified and applies to the original report, canonical concentration, analytical limits, and uncertainty. correction_status is not_corrected, laboratory_corrected, or unspecified and records whether the reporting laboratory applied a dilution correction. These fields describe a separate issue from free versus hydrolyzed analyte. The import path converts units only; it never multiplies by the session dilution factor. An unknown reporting basis is preserved and blocks incompatible inference. A later scientifically justified transformation requires an explicit versioned adapter and new linked record; never silently correct twice.

The manifest's compatibility_policy_id must resolve to an immutable policy of accepted analyte/method/assay_basis/concentration_basis/correction_status tuples, including collection-method compatibility. Independent allowed_assay_ids and allowed_assay_bases lists are preliminary filters, not permission for their Cartesian product. A missing or unresolved tuple policy blocks inference.

source is simulated, reference_lab, prototype_sensor, or validated_sensor. A provenance string alone is not evidence of validation: the registry verifies the claimed method and calibration. Every concentration emitted by the starter is simulated and is prohibited from research inference.

## 5. Cardiac and pupil capture records

The v0.1 cardiac envelope describes one capture modality. PPG cannot populate ECG-derived fields; an ECG-derived metric requires an ECG capture and its provenance. A future design acquiring PPG and ECG together must represent separate capture identities and timing before extending this envelope.

### 5.1 Heart rate and ECG

The cardiac component records acquisition start/end, source, modality, firmware/hardware revision, resting posture/context, heart_rate_bpm, signal quality, and optional ECG features/artifact reference. An ECG waveform uses mV and sample timestamps or a verified sample rate plus explicit gap markers. Raw ADC counts must remain labeled counts until a calibration converts them.

An initial PPG driver should retain raw and processed measurements supported by the chosen breakout, including device-reported quality. A quality percentage from the sensor is not a calibrated probability of correct HR or of intoxication. The acquisition layer must not smooth away missing beats or replace signal loss with a previous valid value without marking the substitution.

ECG features remain experimental. The selected feature version declares lead configuration, preprocessing, artifact handling, valid duration, and any beat-interval measure. A model trained on a long stationary ECG recording cannot silently accept a shorter or motion-corrupted recording. Initial development uses a simulator; human contact requires the controls in the hardware guide.

### 5.2 Pupil response

The eye component records camera/lens identity, actual frame timestamps, capture configuration, illumination estimate and its source, stimulus timing evidence, distance/scale calibration, segmentation quality, and derived features. Candidate outputs are baseline diameter, relative constriction amplitude, response latency, and recovery measures. Optional normalized features must retain their unitless meaning.

No universal light intensity, flash duration, or camera distance is authorized by this version. An approved optical configuration ID must resolve to device-specific settings and an optical-safety review before a human stimulus experiment. Bench development can use synthetic videos or optical fixtures. Unsupported iris segmentation, autoexposure changes, dropped frames, or unverified stimulus timing yield explicit quality flags.

The frame rate limits timing resolution. Do not emit a high-precision latency simply because the software uses floating-point numbers. Validate the complete capture/extraction pipeline against a suitable reference and report error by phone, conditions, and relevant participant characteristics.

## 6. One reaction task: choice_inhibit_v0

This is an unvalidated research task design, not an established impairment test. It is one continuous activity with six practice trials followed by 60 scored trials. Practice results are excluded from scored features. The scored schedule contains 48 go trials (24 left, 24 right) and 12 no-go trials. A seeded shuffled schedule is saved with the configuration hash; the same stored schedule supports deterministic replay. Do not select the schedule based on the user's eventual result.

Each trial has a target onset, an allowed response interval, and the next onset. Initial design: 1000 ms response deadline; onset-to-onset interval sampled in advance from 1500–1900 ms, mean approximately 1700 ms. Nominal scored duration is about 102 seconds, with practice and instructions making the complete task about two minutes. These are engineering starting settings; validation determines whether the task has useful sensitivity and reliability.

Use native display presentation timestamps for onset and native touch event timestamps for response. A task version pins stimulus assets, visual size rules, response targets, language, timing, randomization algorithm, and extraction version. Avoid instructions that rely on color alone. Accessibility modes changing the task require separate compatibility and validation decisions.

| Event/rule | Required behavior |
|---|---|
| Go trial, correct first response within deadline | Record reaction time and correct response |
| Go trial, wrong first response | Count incorrect response; preserve timing; a later correct tap does not replace it |
| Go trial, no response | Count omission; do not enter a reaction time of zero or the timeout as if measured |
| No-go trial, any response within deadline | Count inhibition error |
| No-go trial, no response | Count correct withholding; no invented reaction time |
| Multiple taps | Preserve event sequence; first qualifying response determines the scored action |
| Response before stimulus onset | Record anticipatory input separately and apply the versioned quality policy |
| App backgrounded, focus lost, call interruption, or timing fault | Mark run invalid; do not resume a scored run from the middle |

Features include median correct-go reaction time, interquartile range, p90, omission rate, wrong-go response rate, no-go error rate, and valid trial count. Lapse definition, minimum valid trials, anticipatory-response limits, and quality thresholds must be fixed in the task validation plan before training. The sample fixture's numbers illustrate structure, not a normative performance range.

A repeat after an invalid run is linked to the original attempt and retained in completion statistics. Repeating a valid game simply to select the fastest score is not permitted in the study analysis. Qualified personal baselines use only earlier sessions and the same compatible task; their acquisition protocol and practice effects are part of validation.

## 7. Session and result states

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Collecting
    Collecting --> Canceled
    Collecting --> Ready
    Collecting --> Invalid
    Ready --> Finalized
    Finalized --> MeasurementOnly
    Finalized --> Inconclusive
    Finalized --> ResearchEstimate
    Finalized --> Invalid
```

Lifecycle transitions are append-only audit events. Finalized is not itself a scientific conclusion. Result states are exactly measurement_only, research_estimate, inconclusive, and invalid. Only research_estimate may contain a non-null probability, classification, operating threshold, and endpoint ID.

Gate order for the conditional research inference service:

1. Verify actor, study/session authorization, schema, identifiers, and input digest. Reject malformed or unauthorized requests before model work.
2. Validate component quality and semantics. A broken required acquisition is invalid; a coherent but unsupported combination is inconclusive.
3. If session mode is synthetic or analytical, or any model-input channel is simulated, produce measurement_only with probability null.
4. Resolve the server-selected manifest. Missing/unvalidated models yield measurement_only; retired models cannot generate a new estimate.
5. Require controlled_research mode, an approved current protocol, authorized enrollment, an active_research manifest, and reviewer approvals. A client request cannot supply these permissions.
6. Enforce population, assay/basis, collection method, hardware/software, task, baseline, required-channel, provenance, co-use scope, and acquisition-time rules. Unsupported inputs yield inconclusive with reasons.
7. Extract features using the pinned feature implementation. Nonfinite or impossible features fail quality validation.
8. Run the pinned model and calibration. Check probability is finite and in [0,1]. Apply the manifest's approved uncertainty/abstention policy first; an abstention yields inconclusive with probability null in the output contract. Otherwise apply the manifest threshold to a separate classification field. The approved policy may use a frozen probability band or another justified procedure; unresolved bounds cannot enable inference.
9. Persist the immutable result, target/evaluation times, reasons, and all input/model references. A delayed result is displayed as historical.

The included run_demo.py implements only a measurement-only path and cannot exercise step 8. The service's separate model engine implements the bounded research path. Its 1.1.0 result reader verifies schema, exact snapshot/context/evidence/model/policy/approval linkage and digests; every legacy-shaped research estimate remains unsupported. Current scientific authority is rechecked before computation, transactional commit, replay/read and protected disclosure. Retired history preserves immutable evidence but cannot disclose a newly unauthorized numeric result. Reanalysis creates a linked result ID.

## 8. BLE and USB transport

USB serial in the supplied sketch is newline-delimited JSON at 115200 baud. Each line has schema_version, device_id, seq, monotonic_ms, source, heart_rate_bpm, and assay_ready. source is always simulated and assay_ready is always false. It is a bring-up record, not a session or a saliva assay result. Firmware version and broader component payloads enter the later protocol.

Custom GATT service UUID: 680cf5d8-5656-4f41-81c4-0f48d26f1000. Suffixes 1001, 1002, and 1003 designate capabilities (read), command RX (write with response), and event TX (notify). These are project-local UUID assignments, not Bluetooth SIG standard profiles. Phone and firmware implementations share the exact complete UUIDs.

Logical messages use UTF-8 JSON with protocol_version=1, message_id, device_id, boot_id, session_id, sequence, monotonic_ms, type, and payload. Supported initial types are hello, clock_sync, start_capture, cancel_capture, capture_chunk, capture_complete, status, ack, and error. A command is scoped to one session and has a deadline. Repeating a command message_id with identical content returns the prior outcome; different content under the same ID is rejected.

Fragment logical messages at the negotiated ATT payload length; do not assume a large MTU. The 12-byte binary fragment header is little endian: version u8 (1), encoding u8 (1 = UTF-8 JSON; other values rejected), transfer_id u32, fragment_index u16 (zero-based), fragment_count u16, fragment_payload_bytes u16. Message type remains the named string inside the JSON envelope. Append a four-byte little-endian CRC-32/ISO-HDLC checksum of the JSON bytes to the logical byte stream before fragmenting it. Thus the checksum may share the final fragment with JSON bytes. Fragment payload capacity is ATT_MTU minus 3 minus 12 bytes; at MTU 23 this is eight bytes. CRC detects corruption; it does not authenticate a sender.

Bound logical payload size to 8192 bytes including the four checksum bytes and allow one in-progress transfer per direction. Larger raw recordings use multiple bounded blocks with a final length/digest manifest. Receiver rejects invalid lengths, duplicate fragments with different bytes, mismatched session IDs, out-of-range indices, and incomplete transfers. A complete-message acknowledgment precedes capture acceptance. A proposed two-second complete-message acknowledgment timeout starts after the last fragment is sent, with three retries and a separate 120-second reassembly limit. These are bench parameters to verify, not measured radio performance; at a small MTU a transfer can take substantially longer than two seconds. Queue overflow or lost raw samples must be reported.

P0 BLE may carry synthetic data only. Before P2, require encrypted pairing, verified association with a provisioned device identity, application-level replay protection, and reviewed credential handling. The exact authenticated provisioning implementation is a security gate; no default shared secret or unauthenticated physiological upload is authorized. Credentials must never be included in examples or source code.

## 9. API surface and idempotency

The initial exchange API is documented in [../contracts/openapi.yaml](../contracts/openapi.yaml). The implemented route surface extends it through the shared application, participant-acquisition, raw-export and report-revision contracts. `services/api/otgd/main.py` and its generated FastAPI OpenAPI are the source route inventory; the initial hand-authored file is not a complete list of current endpoints. Protected routes require server-side authorization; local fictional HTTP does not become a QA/prod TLS exception. P0 examples need no network or account.

| Operation | Purpose |
|---|---|
| POST /v1/sessions | Register the client-created session UUID under the authenticated context; server validates identity and uniqueness |
| PUT /v1/sessions/{session_id}/snapshot | Supply the completed acquisition snapshot pending server finalization; If-Match prevents stale replacement |
| POST /v1/sessions/{session_id}/finalize | Freeze the snapshot, verify its digest, and queue the permitted result path |
| GET /v1/sessions/{session_id}/result | Retrieve status/result for an authorized session |
| POST /v1/artifact-uploads | Request a short-lived private upload destination under the session's consent and retention policy |
| POST /v1/artifact-uploads/{artifact_id}/complete | Verify digest, length, and media type before marking the object usable |
| POST /v1/research/lab-imports | Import a source laboratory report and normalized measurements; research role only |
| GET /v1/model-manifests/{model_id} | Retrieve a permitted manifest; does not grant permission to execute it |

Protected writes require `Idempotency-Key` and `X-Data-Generation`, with owner/generation/route/body/family checks defined by the shared contract. Persist the original request digest, response and operation identity; a client cannot rotate an unknown-outcome key to repeat an effect. An identical currently admitted retry returns its accepted response; changed content under a key returns 409. Revocation/deletion gates still apply; only the documented minimal deletion-receipt exception survives its retired generation. Mutable resources require `If-Match`: missing is 428 and stale is 412. No arbitrary response-cache timeout authorizes a duplicate session/sample/privacy operation.

Use 400 for malformed input, 401 for unauthenticated, 403 for unauthorized scope, 404 for inaccessible/nonexistent resources, 409 for idempotency/state conflict, 410 for retired generation, 412/428 for stale/missing preconditions, 413 for excess bytes, 422 for semantic violations, 429 for rate limiting, and 503 for temporary infrastructure unavailability. Errors carry `code/message/request_id/retryable`; unknown codes remain visible unavailable details. HTTP success is not scientific validity: a 200 result may be inconclusive or measurement_only.

Clients cannot write outcome labels, registry approvals, calibration validity, or the probability field through the session API. Laboratory imports verify provenance and require review before participating in a finalized model input. Artifact upload completion verifies contents before data are eligible for feature extraction.

## 10. Persistence and concurrency

The implemented relational model uses account/check/job/outbox/artifact/idempotency/revocation and typed bounded `records` tables, plus operator registry/version/decision and recovery/system authority tables (`services/api/otgd/db.py`). Profile, study, context, attempt, laboratory and report companions use declared kinds and validated JSON bodies; they are not arbitrary unowned blobs. Relational owner/generation fields are authoritative, never JSON ownership claims. Schema migrations and database guards enforce immutable approved bodies. Access checks precede serialization and object access; live PostgreSQL tests must exercise locks/guards/tenant isolation, which SQLite fixtures cannot prove.

Uniqueness and replay invariants include device/boot/sequence, specimen/measurement identity, immutable session snapshot/evidence, one outbox per job and exact snapshot/model/feature/calibration result identity. Some are enforced through typed record keys and transactional checks rather than one table per scientific entity; inspect the models/migrations before adding a constraint. Many immutable results/revisions may reference one check; the selected current view must never erase original evidence or behave as a mutable probability record.

Finalization is a transaction that checks the current draft version, validates required references, writes the immutable snapshot/digest and audit event, and creates a pending result job. The queue consumer is at-least-once and deduplicates by job key. A worker crash after computing but before acknowledgment cannot duplicate the scientific result. An outbox record written in the same transaction prevents a finalized session from losing its result job.

Raw artifacts are private, content-addressed or UUID-addressed without personal names, and have immutable digests. Client quarantine upload uses narrowly scoped expiring PUT tickets; protected exports use the authenticated API gateway, never an S3 bearer GET. Retention is resolved from the approved policy before upload; a missing policy blocks raw upload. Deletion/withdrawal jobs reconcile database and object storage and record completion or any permitted retention exception.

## 11. Model registry and release contract

The manifest schema declares lifecycle, endpoint definition, study scope, artifact hash, input-contract version, required channels, allowed acquisition/assay/task configurations, baseline mode, calibration, threshold, population bounds, timing limits, validation report, and reviewer approval references. The example manifest is unvalidated; all unresolved decision fields are null or empty and cannot enable a score.

In active_research state, every scientifically material eligibility field must be resolved. The model registry service validates the approval records independently of the JSON document. A signature verifies artifact origin and integrity, not predictive validity. A version-compatible schema likewise does not establish that an assay or model has been validated.

Training artifacts include a frozen data manifest, participant/session split assignments, labeling protocol, exclusion log, feature code, model hyperparameters, calibration procedure, subgroup results, uncertainty/coverage analysis, and provenance. Choose thresholds only using designated development data. External evaluation must not influence later tuning without declaring a new development cycle.

## 12. Observability, failures, and verification

Record component completion rates, quality-failure reasons, drift alerts, sample inadequacy, upload and inference latency, model compatibility failures, and invalid/inconclusive coverage. Do not log raw face video, ECG, chemical report text with identifiers, tokens, or secrets. A metric such as successful HTTP response rate must not be used as model accuracy.

Minimum negative checks include simulated-source rejection for inference, below-LOQ versus zero handling, free/total mismatch, stale baseline, mismatched sample/session IDs, missing required channel, interrupted game, device reboot, replayed command, model retirement, unauthorized enrollment, nonfinite probability, and cross-study access. Record what is implemented and tested versus only specified.

The first repository verification checks document links, machine-readable contract structure, synthetic examples, qualifier semantics, and the measurement-only result path. It does not validate sensor hardware, compile against an installed Arduino board package unless explicitly reported, establish BLE behavior, or demonstrate prediction accuracy. Physical and clinical acceptance belong to the full specification and validation plan.

## 13. Current companion, authority and recovery contracts

**Contexts and attempts.** Start check freezes target/profile/history/configuration in one owned local action. Persist an attempt before activation and retain all failed/canceled attempts. Context and terminal attempts use JCS digests; the evidence manifest selects at most one attempt per component and includes at most 128 unique attempt hashes. The v0.1 snapshot stays a strict selected projection; null/not-collected is not a success. Snapshot and evidence digests freeze together; result `input_sha256` remains the snapshot digest and `X-Evidence-Sha256` binds the companion. Local save is transactional and does not enqueue. A pending reference-lab handoff remains a resumable draft with `LAB_ANALYSIS_PENDING`; explicit abandonment retains the specimen and may finalize only under a protocol permitting missing chemistry. Staff import requires separate current staff authority over that participant/specimen/report. Same-specimen revisions and new-specimen replacements remain distinct.

**Fresh start.** An exact instruction receipt binds configuration ID/version/full submitted digest, protocol, current consent, attempt, original acknowledgment and acceptance times. Its approved freshness is 1–300 seconds using the earlier original time; equal maximum age is allowed, greater age is denied. Every qualified start is online: a one-use authorization expires after 60 seconds, binds the boot/attempt and is consumed atomically; native round trips over five seconds are refused. The capture duration is independently bounded by the signed configuration. Registry reference locks order retirement against start/acceptance. Sign-in, a capability cache or a participant checkbox cannot supply any missing approval or observed electrical state.

**Reader proof and supported drivers.** Device binding signs `OTGD-BIND-v1\n` plus exact server JCS. Capture signs `OTGD-CAPTURE-v1\n` plus its exact payload digest and scope. Server start signs the strict grant under the 22-byte `OTGD capture grant v1\0` domain; protected provisioned P-256 keys, not token-supplied keys, establish origin. Firmware requires Secure Connections/MITM bonding and per-device protected passkey custody. ADC defaults to feature-only. Optional ECG samples require separately signed record permission, approved `otgd_ecg_samples_v1`, capacity 1–1024 and a configured sampling budget that fits; chunks hold at most 64 actual observations and preserve gaps/timestamps. The phone verifies the bounded unchanged handoff before encrypted local retention and forwards device evidence for server signature verification. The selected SparkFun MAX32664 adapter uses its pinned actual SDK/FIFO path, counts only fresh successful dequeues, retains vendor confidence as quality, and has no supported raw codec. Missing portable saliva/breath drivers and the missing human-ECG operating-state observer stay unavailable, with precise reasons; no generic ADC or declaration substitutes for them.

**Restricted numeric admission.** Research artifacts are canonical data-only JSON of at most 65,536 bytes with exact S3 version/length/SHA, ordered known features, finite limits/weights/scales and calibration. Ordinary/guest/simulated sessions never score. The full mode needs every named qualified channel and matched evaluation. The explicit HR-only policy requires exactly `cardiac_hr` and `cardiac.heart_rate_bpm`, exact independently released `cardiac_server_interval` calibration and current device/key/configuration/adapter. Its conservative interval uses original signed issue and original verified attestation receipt, widened by both approved UTC-error margins; replay cannot renew it. Compare width/acquisition/delivery bounds directly and retain original flags. Vendor signed duration must fit the unrounded widened interval under the exact approved rate-error inequality. Baseline delta additionally needs independently admitted earlier owned evidence under the same scope and age bound. Geometry-only optical qualification permits baseline diameter only; it cannot qualify constriction/latency. Offline evaluation verifies consistency and partitions, retains supplied authority/lock/endpoint references and labels external authenticity unverified; it never grants clinical/research authority.

**Objects and privacy.** Upload tickets last five minutes, sign exact length/media/checksum and conditional `If-None-Match:*`, and create quarantined bytes only. Completion bounded-reads a non-null pinned VersionId, verifies actual bytes/codec and rechecks current authority before commit. No accepted read follows a bare current key. Raw record/upload defaults off; explicit raw export has an independent exact participant-copy authority. Complete structured+raw+manifest payload fits 50 MiB and ZIP 64 MiB or narrower grants, at most 500 checks/128 raw sources; no overflow truncation. The authenticated download verifies exact bytes before disclosure and re-admits before every at-most-64-KiB chunk. All paths release buffer slots and wipe temporary decoded data. Logical denial and eventual version-aware cleanup are different states; a late upload or stale worker cannot reopen delivery or justify a premature physical-erasure claim.

**Worker/recovery.** Finalize/job acceptance writes its outbox atomically. Canonical continuous workers use 120-second fenced leases/visibility and 30-second heartbeats, with at most five failed claims and explicit DLQ/retry disposition. Work runs outside long database locks; commit rechecks lease/fence/account/generation/scientific authority, stores output before queue deletion, and leaves stable job identity for crash recovery. Explicit serverless/ECS executors retain their own bounded control/lease configuration and do not inherit evidence from another deployment. Retained journal control and accepted deletion/recovery barriers are independently checked before API admission/nonprivacy claim/compute/commit and disclosure. A restored database flag cannot reenable a study; exact fresh three-principal dependency releases, retained study seal and fresh consent are required. Safe privacy cleanup can continue while ordinary data work is suspended.

**Acceptance evidence.** Execute the repository's same local/Actions gates on a stable exact revision; coverage must be strictly greater than 80% and mandatory skips fail. Include actual PostgreSQL guard/locking, actual LocalStack S3 conditional/versioned bytes and SQS delivery, plus actual worker-process kills before/after claim, object write, DB commit and queue acknowledgment. Show stable IDs, no lost job/duplicate publication, rejected stale fences, late-object cleanup, current-authority refusal and bounded failures. Add a complete signed-in fictional PKCE → owned save/upload → result/history/export → deletion/logout journey using live dependencies, with reload and foreign-account/revocation negatives. Guest Playwright and component doubles remain separate. Native minimum/current Android/iOS, physical handsets, SQLCipher kill/restart/denied unlock, OS permission-settings return without reprompt, BLE/camera lifecycle, 200% text and TalkBack/VoiceOver require observed matrix rows. Missing hardware/toolchains/external approvals remain explicit blockers; none is replaced by software mocks.
