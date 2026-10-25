import { readerRawRecording, ECG_RECORDING_MAGIC } from "../physicalRaw";
import test from "node:test";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import {
  createHash,
  generateKeyPairSync,
  randomUUID,
  sign,
  verify,
} from "node:crypto";
import { canonicalJson, clone, digest } from "../../core/integrity";
import { DeviceControllerImpl } from "../controller";
import { presentDevice } from "../../core/devicePresentation";
import {
  DeviceError,
  fragmentMessage,
  fromBase64,
  Reassembler,
  toBase64,
} from "../protocol";
import type { DeviceEnvelope } from "../protocol";
import {
  bindingTranscript,
  derSignature,
  GRANT_DOMAIN,
  PHYSICAL_PROTOCOL_ID,
  physicalCapabilities,
  signedReaderCapture,
  signedSampleChunk,
  startToken,
} from "../physicalProtocol";
import type {
  AuthorizedReaderOptions,
  BindingTranscript,
  ExpectedReaderCapture,
  PhysicalCapabilities,
  ReaderBinding,
  SignedStartToken,
} from "../physicalProtocol";
import type { DeviceTransport, TransportEvent } from "../types";

const key = generateKeyPairSync("ec", { namedCurve: "prime256v1" });
const cap: PhysicalCapabilities = {
  protocol_version: 1,
  encodings: [1],
  max_logical_bytes: 8192,
  max_att_bytes: 512,
  source: "prototype_sensor",
  protocol_id: PHYSICAL_PROTOCOL_ID,
  device_id: "READER-TEST",
  boot_id: randomUUID(),
  hardware_revision: "bench_driver_fixture",
  firmware_version: "1.0.0",
  key_id: "fixture-p256",
  channels: ["ppg", "ecg", "saliva", "alcohol"],
  timestamp_resolution_ms: 1,
};
const scope = {
  environment: "test" as const,
  owner_ref: randomUUID(),
  data_generation: 1,
};
const options = {
  ...scope,
  authorization_id: randomUUID(),
  binding_id: randomUUID(),
  device_id: cap.device_id,
  key_id: cap.key_id,
  configuration_id: "physical_fixture_v1",
  configuration_hash: "a".repeat(64),
  max_duration_ms: 1000,
  capture_context_sha256: "b".repeat(64),
} as AuthorizedReaderOptions;
const context = {
  sessionId: randomUUID(),
  attemptId: randomUUID(),
  captureId: randomUUID(),
  workspaceEpoch: "test-owner:1",
};
const expected: ExpectedReaderCapture = {
  ...options,
  session_id: context.sessionId,
  attempt_id: context.attemptId,
  record_id: context.captureId,
  workspace_epoch: context.workspaceEpoch,
  channel: "ecg",
};
const deviceNonce = Buffer.alloc(32, 3).toString("base64url");
function serverStart(): SignedStartToken {
  const grant = {
    schema_version: "1.0.0" as const,
    ...scope,
    session_id: context.sessionId,
    attempt_id: context.attemptId,
    authorization_id: options.authorization_id,
    binding_id: options.binding_id,
    device_id: cap.device_id,
    device_key_id: cap.key_id,
    boot_id: cap.boot_id,
    configuration_id: options.configuration_id,
    configuration_hash: options.configuration_hash,
    configuration_submitted_sha256: "c".repeat(64),
    configuration_version: "1.0.0",
    capture_context_sha256: options.capture_context_sha256,
    channel: "ecg" as const,
    configuration_max_duration_ms: 1000,
    raw_recording_permission: null,
    participant_protocol_sha256: "d".repeat(64),
    instruction_receipt_id: randomUUID(),
    issued_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 60_000).toISOString(),
    device_nonce: deviceNonce,
    nonce: randomUUID(),
  };
  grant.expires_at = new Date(
    Date.parse(grant.issued_at) + 60_000,
  ).toISOString();
  return {
    grant,
    signature: signature(GRANT_DOMAIN, grant),
    key_id: "test-server",
    domain: GRANT_DOMAIN,
  };
}
options.server_start = serverStart();
const transcript: BindingTranscript = {
  schema_version: "1.0.0",
  challenge_id: randomUUID(),
  ...scope,
  device_id: cap.device_id,
  key_id: cap.key_id,
  nonce: Buffer.alloc(32, 1).toString("base64url"),
  expires_at: new Date(Date.now() + 240_000).toISOString(),
  hardware_revision: cap.hardware_revision,
  firmware_version: cap.firmware_version,
};
const binding: ReaderBinding = {
  binding_id: options.binding_id,
  device_id: cap.device_id,
  key_id: cap.key_id,
  hardware_revision: cap.hardware_revision,
  firmware_version: cap.firmware_version,
  state: "active",
  bound_at: "2026-01-01T00:00:00Z",
};
function signature(domain: string, value: unknown): string {
  return sign(
    "sha256",
    Buffer.from(domain + canonicalJson(value)),
    key.privateKey,
  ).toString("base64");
}
function signedEnvelope(value: unknown, sequence = 10) {
  return {
    schema_version: "1.0.0",
    ...scope,
    session_id: context.sessionId,
    attempt_id: context.attemptId,
    authorization_id: options.authorization_id,
    binding_id: options.binding_id,
    device_id: cap.device_id,
    key_id: cap.key_id,
    boot_id: cap.boot_id,
    sequence,
    configuration_hash: options.configuration_hash,
    payload_sha256: digest(value),
  };
}
function projection() {
  return {
    status: "valid",
    source: "prototype_sensor",
    started_at: "2026-01-01T00:00:00Z",
    ended_at: "2026-01-01T00:00:01Z",
    quality_flags: ["UNQUALIFIED_TEST_FIXTURE"],
    acquisition_config_id: options.configuration_id,
    modality: "ecg",
    heart_rate_bpm: 72,
    ecg_status: "valid",
    ecg_rmssd_ms: null,
    sample_rate_hz: 1000,
    raw_artifact_id: null,
  };
}
function completion(sequence = 10) {
  const normalized = projection(),
    e = signedEnvelope(normalized, sequence);
  return {
    source: "prototype_sensor",
    protocol_id: PHYSICAL_PROTOCOL_ID,
    channel: "ecg",
    attempt_id: context.attemptId,
    capture_id: context.captureId,
    workspace_epoch: context.workspaceEpoch,
    started_monotonic_ms: 1000,
    ended_monotonic_ms: 2000,
    attestation_id: randomUUID(),
    envelope: e,
    signature: signature("OTGD-CAPTURE-v1\n", e),
    normalized_payload: normalized,
  };
}
function chunk(sequence = 9) {
  const normalized = {
      schema_version: "1.0.0",
      channel: "ecg",
      first_sample_index: 0,
      sample_rate_hz: 1000,
      units: "uV",
      contact: "good",
      dropped_before: 0,
      acquisition_started_monotonic_us: 1000000,
      acquisition_ended_monotonic_us: 2000000,
      samples: [
        { monotonic_us: 1_000_100, value: 24 },
        { monotonic_us: 1_001_100, value: -4 },
      ],
    },
    e = signedEnvelope(normalized, sequence);
  return {
    envelope: e,
    signature: signature("OTGD-CAPTURE-v1\n", e),
    normalized_payload: normalized,
  };
}
function fails(code: string): (e: unknown) => boolean {
  return (e) => e instanceof DeviceError && e.code === code;
}

test("physical advertisement has a distinct bounded dialect and never a synthetic/validated source", () => {
  assert.deepEqual(physicalCapabilities(canonicalJson(cap)), cap);
  for (const patch of [
    { source: "validated_sensor" },
    { source: "simulated" },
    { protocol_id: "vendor-unknown" },
    { key_id: "" },
    { channels: ["ecg", "ecg"] },
    { max_att_bytes: 513 },
    { timestamp_resolution_ms: 0 },
    { unknown: true },
  ])
    assert.throws(() =>
      physicalCapabilities(canonicalJson({ ...cap, ...patch })),
    );
  assert.throws(() =>
    physicalCapabilities('{"source":"prototype_sensor","source":"simulated"}'),
  );
});
test("binding preserves exact server domain/JCS bytes, identity, nonce and expiry", () => {
  assert.deepEqual(bindingTranscript(transcript, cap), transcript);
  const s = signature("OTGD-BIND-v1\n", transcript);
  assert.equal(derSignature(s), s);
  assert.equal(
    verify(
      "sha256",
      Buffer.from("OTGD-BIND-v1\n" + canonicalJson(transcript)),
      key.publicKey,
      Buffer.from(s, "base64"),
    ),
    true,
  );
  assert.equal(
    verify(
      "sha256",
      Buffer.from("OTGD-CAPTURE-v1\n" + canonicalJson(transcript)),
      key.publicKey,
      Buffer.from(s, "base64"),
    ),
    false,
  );
  for (const patch of [
    { device_id: "foreign" },
    { key_id: "rotated" },
    { hardware_revision: "unknown" },
    { nonce: "x".repeat(43) },
    { expires_at: "2020-01-01T00:00:00Z" },
    { data_generation: 0 },
    { owner_ref: "foreign" },
    { nonce: Buffer.alloc(31).toString("base64url") },
  ])
    assert.throws(() => bindingTranscript({ ...transcript, ...patch }, cap));
});
test("DER parsing rejects nonminimal/negative/zero/trailing encodings without claiming key verification", () => {
  for (const b of [
    [0x30, 6, 2, 1, 0, 2, 1, 1],
    [0x30, 6, 2, 1, 0x80, 2, 1, 1],
    [0x30, 7, 2, 2, 0, 1, 2, 1, 1],
    [0x30, 6, 2, 1, 1, 2, 1, 1, 0],
  ])
    assert.throws(() => derSignature(Buffer.from(b).toString("base64")));
});
test("signed completion binds each current authorization scope field and exact immutable projection", () => {
  const p = completion(),
    result = signedReaderCapture(p, expected, cap);
  assert.deepEqual(result.normalized_payload, p.normalized_payload);
  assert.equal(result.source, "prototype_sensor");
  assert.equal(result.modelEligible, false);
  assert.equal(
    verify(
      "sha256",
      Buffer.from("OTGD-CAPTURE-v1\n" + canonicalJson(result.envelope)),
      key.publicKey,
      Buffer.from(result.signature, "base64"),
    ),
    true,
  );
  for (const field of [
    "owner_ref",
    "data_generation",
    "session_id",
    "attempt_id",
    "authorization_id",
    "binding_id",
    "device_id",
    "key_id",
    "boot_id",
    "configuration_hash",
  ]) {
    const altered = clone(p);
    (altered.envelope as Record<string, unknown>)[field] =
      field === "data_generation" ? 2 : randomUUID();
    assert.throws(() => signedReaderCapture(altered, expected, cap));
  }
  const altered = clone(p);
  altered.normalized_payload.heart_rate_bpm = 80;
  assert.throws(
    () => signedReaderCapture(altered, expected, cap),
    fails("PHYSICAL_PAYLOAD_DIGEST"),
  );
  for (const patch of [
    { source: "simulated" },
    { workspace_epoch: "new-owner" },
    { capture_id: randomUUID() },
    { started_monotonic_ms: 2001 },
    { ended_monotonic_ms: 2001 },
  ])
    assert.throws(() => signedReaderCapture({ ...p, ...patch }, expected, cap));
});
test("fresh server grant binds the prepared nonce, boot, context and exact 60-second lifetime", () => {
  const token = serverStart();
  assert.deepEqual(startToken(token, expected, cap, deviceNonce), token);
  assert.equal(
    verify(
      "sha256",
      Buffer.from(GRANT_DOMAIN + canonicalJson(token.grant)),
      key.publicKey,
      Buffer.from(token.signature, "base64"),
    ),
    true,
  );
  for (const patch of [
    { device_nonce: "foreign" },
    { boot_id: randomUUID() },
    { capture_context_sha256: "d".repeat(64) },
    { expires_at: new Date(Date.now() + 61_000).toISOString() },
    { owner_ref: randomUUID() },
    { nonce: "bad" },
    { participant_protocol_sha256: null },
    { instruction_receipt_id: null },
    { participant_protocol_sha256: "bad" },
    { instruction_receipt_id: "bad" },
  ])
    assert.throws(() =>
      startToken(
        { ...token, grant: { ...token.grant, ...patch } },
        expected,
        cap,
        deviceNonce,
      ),
    );
  assert.throws(() =>
    startToken(
      { ...token, domain: "wrong" as typeof GRANT_DOMAIN },
      expected,
      cap,
      deviceNonce,
    ),
  );
});
test("signed sample chunks enforce monotonic actual timestamps, explicit drops, units and payload digest", () => {
  const first = signedSampleChunk(chunk(), expected, cap, null);
  assert.equal(first.normalized_payload.samples.length, 2);
  const second = chunk(10);
  second.normalized_payload.first_sample_index = 4;
  second.normalized_payload.dropped_before = 2;
  second.normalized_payload.samples = [{ monotonic_us: 1_004_100, value: 12 }];
  second.envelope.payload_sha256 = digest(second.normalized_payload);
  assert.equal(
    signedSampleChunk(second, expected, cap, first).normalized_payload
      .dropped_before,
    2,
  );
  for (const patch of [
    { first_sample_index: 3 },
    { sample_rate_hz: 1001 },
    { samples: [] },
    {
      samples: [
        { monotonic_us: 1, value: 1 },
        { monotonic_us: 1, value: 2 },
      ],
    },
    { samples: [{ monotonic_us: 1, value: 0.5 }] },
    {
      samples: Array.from({ length: 65 }, (_, i) => ({
        monotonic_us: i + 1,
        value: 0,
      })),
    },
  ]) {
    const bad = chunk();
    Object.assign(bad.normalized_payload, patch);
    bad.envelope.payload_sha256 = digest(bad.normalized_payload);
    assert.throws(() => signedSampleChunk(bad, expected, cap, null));
  }
});

/** Test-only signed peripheral. Values are explicitly fictional and never a hardware qualification. */
class SignedFixtureTransport implements DeviceTransport {
  readonly kind = "ble_unprovisioned";
  readonly available = true;
  private listener: ((e: TransportEvent) => void) | null = null;
  private receiver = new Reassembler(512);
  private sequence = 0;
  private transfer = 0;
  disconnects = 0;
  deferAck = false;
  rejectAck: ((e: Error) => void) | null = null;
  autoComplete = true;
  sendUnrequestedSamples = false;
  lastStart: DeviceEnvelope | null = null;
  now() {
    return 3000;
  }
  subscribe(listener: (e: TransportEvent) => void) {
    this.listener = listener;
    return () => {
      this.listener = null;
    };
  }
  async scan() {
    this.listener?.({
      kind: "discovered",
      peripheralId: "fixture-reader",
      alias: "signed test fixture",
      rssi: -20,
    });
  }
  async stopScan() {}
  async connect(id: string) {
    return { peripheralId: id, mtu: 515, capabilities: canonicalJson(cap) };
  }
  async disconnect() {
    this.disconnects++;
  }
  emit(
    type: DeviceEnvelope["type"],
    payload: Record<string, unknown>,
    session: string,
  ): void {
    const message: DeviceEnvelope = {
      protocol_version: 1,
      message_id: randomUUID(),
      device_id: cap.device_id,
      boot_id: cap.boot_id,
      session_id: session,
      sequence: this.sequence++,
      monotonic_ms: this.now(),
      type,
      payload,
    };
    if ("envelope" in payload) {
      const e = requireEnvelope(payload.envelope);
      e.sequence = message.sequence;
      payload.signature = signature("OTGD-CAPTURE-v1\n", e);
    }
    for (const frame of fragmentMessage(message, this.transfer++, 512))
      this.listener?.({
        kind: "packet",
        peripheralId: "fixture-reader",
        base64: toBase64(frame),
        receivedAtMonotonicMs: this.now(),
      });
  }
  finish() {
    const command = this.lastStart!;
    if (this.sendUnrequestedSamples)
      this.emit("capture_chunk", chunk(), command.session_id);
    this.emit("capture_complete", completion(), command.session_id);
  }
  async write(base64: string) {
    const command = this.receiver.push(fromBase64(base64, 512), this.now());
    if (!command) return;
    if (command.type === "ack") {
      if (this.deferAck) {
        this.deferAck = false;
        await new Promise<void>((_, reject) => {
          this.rejectAck = reject;
        });
      }
      return;
    }
    this.emit(
      "ack",
      { ack_message_id: command.message_id, status: "accepted" },
      command.session_id,
    );
    if (command.type === "hello") {
      const t = command.payload.binding_transcript as
        BindingTranscript | undefined;
      this.emit(
        "hello",
        {
          request_message_id: command.message_id,
          source: "prototype_sensor",
          protocol_id: PHYSICAL_PROTOCOL_ID,
          key_id: cap.key_id,
          ...(t
            ? {
                challenge_id: t.challenge_id,
                signature: signature("OTGD-BIND-v1\n", t),
              }
            : {}),
          ...(command.payload.request_start_nonce
            ? { device_nonce: deviceNonce }
            : {}),
        },
        command.session_id,
      );
    } else if (command.type === "start_capture") {
      this.lastStart = command;
      if (this.autoComplete) setImmediate(() => this.finish());
    }
  }
}
function requireEnvelope(value: unknown): Record<string, unknown> {
  return value as Record<string, unknown>;
}
async function connected() {
  const transport = new SignedFixtureTransport(),
    controller = new DeviceControllerImpl(
      { idFactory: randomUUID },
      () => transport,
    );
  await controller.scan();
  await controller.connect("fixture-reader");
  return { controller, transport };
}
test("actual framed signed test peripheral requires verified binding before authorized capture", async () => {
  const { controller, transport } = await connected();
  try {
    assert.equal(controller.snapshot().state, "connected_reader");
    assert.equal(presentDevice(controller.snapshot()).connected, true);
    assert.equal(controller.snapshot().humanCaptureAvailable, false);
    await assert.rejects(
      controller.captureAuthorized("ecg", context, options),
      fails("DEVICE_NOT_READY"),
    );
    assert.throws(
      () => controller.installBinding(binding, scope),
      fails("PHYSICAL_CAPTURE_SCOPE"),
    );
    const proof = await controller.requestBindingProof(transcript);
    assert.equal(
      verify(
        "sha256",
        Buffer.from("OTGD-BIND-v1\n" + canonicalJson(transcript)),
        key.publicKey,
        Buffer.from(proof.signature, "base64"),
      ),
      true,
    );
    controller.installBinding(binding, scope);
    await controller.prepareAuthorizedCapture(context);
    options.server_start = serverStart();
    await assert.rejects(
      controller.captureAuthorized("ecg", context, {
        ...options,
        data_generation: 2,
      }),
      fails("PHYSICAL_CAPTURE_SCOPE"),
    );
    const result = await controller.captureAuthorized("ecg", context, options);
    const wire = transport.lastStart!.payload.authorization as Record<
      string,
      unknown
    >;
    assert.deepEqual(
      JSON.parse(
        Buffer.from(String(wire.server_start_base64), "base64").toString(
          "utf8",
        ),
      ),
      options.server_start,
    );
    assert.equal(result.sampleChunks.length, 0);
    assert.equal(result.rawRecording, null);
    assert.deepEqual(result.normalized_payload, projection());
    assert.equal(controller.snapshot().captureInProgress, false);
  } finally {
    await controller.dispose();
  }
});
test("cancellation clears trusted association immediately and drops a late signed completion", async () => {
  const { controller, transport } = await connected();
  try {
    await controller.requestBindingProof(transcript);
    controller.installBinding(binding, scope);
    transport.autoComplete = false;
    await controller.prepareAuthorizedCapture(context);
    options.server_start = serverStart();
    const capture = controller.captureAuthorized("ecg", context, options);
    void capture.catch(() => {});
    for (let i = 0; i < 20 && !transport.lastStart; i++)
      await new Promise<void>((resolve) => setImmediate(resolve));
    assert.ok(transport.lastStart);
    const stop = controller.cancelCapture("WORKSPACE_CHANGED");
    assert.equal(controller.snapshot().association, null);
    assert.equal(controller.snapshot().humanCaptureAvailable, false);
    await assert.rejects(capture, fails("WORKSPACE_CHANGED"));
    transport.finish();
    await stop;
    assert.equal(controller.snapshot().association, null);
    assert.equal(controller.snapshot().captureInProgress, false);
  } finally {
    await controller.dispose();
  }
});

// A rejected ACK write belongs to its old link generation, even after the
// replacement link is connected and serving fresh commands.
test("delayed old acknowledgment rejection cannot invalidate replacement association", async () => {
  const { controller, transport } = await connected();
  try {
    await new Promise<void>((resolve) => setImmediate(resolve));
    transport.deferAck = true;
    await controller.requestBindingProof(transcript);
    for (let i = 0; i < 20 && !transport.rejectAck; i++)
      await new Promise<void>((resolve) => setImmediate(resolve));
    assert.ok(transport.rejectAck);
    await controller.disconnect();
    await controller.connect("fixture-reader");
    const before = transport.disconnects;
    transport.rejectAck!(new Error("old ACK write failed"));
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(controller.snapshot().state, "connected_reader");
    assert.equal(controller.snapshot().association?.deviceId, cap.device_id);
    assert.equal(transport.disconnects, before);
  } finally {
    await controller.dispose();
  }
});

test("actual backend bound-reader HTTP fixture passes strict physical token and exact material digest", () => {
  const fixture = JSON.parse(
    readFileSync(
      fileURLToPath(
        new URL(
          "../../../testfixtures/backend-reader-capture-authorization.json",
          import.meta.url,
        ).href,
      ),
      "utf8",
    ),
  );
  const token = fixture.start.server_start as SignedStartToken,
    g = token.grant,
    a = fixture.authorization;
  const capabilities = {
    ...cap,
    device_id: g.device_id,
    key_id: g.device_key_id,
    boot_id: g.boot_id,
    firmware_version: "1.0.0",
    hardware_revision: "fixture-hw",
  };
  const capture: ExpectedReaderCapture = {
    ...g,
    key_id: g.device_key_id,
    max_duration_ms: g.configuration_max_duration_ms,
    configuration_id: g.configuration_id,
    server_start: token,
    record_id: randomUUID(),
    workspace_epoch: "literal-test-epoch",
    channel: "ppg",
  };
  const clock = Date.now;
  Date.now = () => Date.parse(g.issued_at) + 1;
  try {
    assert.deepEqual(
      startToken(token, capture, capabilities, g.device_nonce),
      token,
    );
    assert.equal(digest(a.configuration_material), g.configuration_hash);
    assert.equal(
      verify(
        "sha256",
        Buffer.from(GRANT_DOMAIN + canonicalJson(g)),
        {
          key: Buffer.from(fixture.server_public_key_spki, "base64"),
          format: "der",
          type: "spki",
        },
        Buffer.from(token.signature, "base64"),
      ),
      true,
    );
  } finally {
    Date.now = clock;
  }
});

test("opt-in ECG handoff preserves measured signed chunks and refuses bounds/scope changes", () => {
  const expected = {
    ...options,
    session_id: context.sessionId,
    attempt_id: context.attemptId,
    record_id: context.captureId,
    workspace_epoch: context.workspaceEpoch,
    channel: "ecg" as const,
  };
  const capture = signedReaderCapture(completion(), expected, cap);
  capture.sampleChunks = [signedSampleChunk(chunk(), expected, cap, null)];
  assert.equal(readerRawRecording(capture, expected, cap), null);
  const permission = {
    record: true as const,
    upload: false,
    receipt_id: randomUUID(),
    policy_id: "raw",
    policy_version: "1",
    policy_sha256: "a".repeat(64),
    raw_notice_version: "1",
    raw_notice_sha256: "b".repeat(64),
  };
  expected.server_start = clone(serverStart());
  expected.server_start.grant.raw_recording_permission = permission;
  expected.server_start.signature = signature(
    GRANT_DOMAIN,
    expected.server_start.grant,
  );
  const recording = readerRawRecording(capture, expected, cap)!;
  if (process.env.OTGD_WRITE_READER_FIXTURE === "true")
    writeFileSync(
      "testfixtures/signed-reader-raw-ecg.json",
      JSON.stringify(
        {
          fixture_scope:
            "fictional_signed_reader_raw_software_only_not_physical_evidence",
          device_public_key_pem: key.publicKey.export({
            type: "spki",
            format: "pem",
          }),
          capabilities: cap,
          binding,
          expected,
          capture,
          recording,
        },
        null,
        2,
      ) + "\n",
    );
  const bytes = Buffer.concat(
    recording.chunks.map((b) => Buffer.from(b, "base64")),
  );
  assert.equal(recording.size_bytes, bytes.length);
  assert.equal(
    recording.sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
  assert.equal(
    bytes.subarray(0, ECG_RECORDING_MAGIC.length).toString(),
    ECG_RECORDING_MAGIC,
  );
  const body = JSON.parse(
    bytes.subarray(ECG_RECORDING_MAGIC.length).toString(),
  );
  assert.deepEqual(body.sample_chunks, capture.sampleChunks);
  assert.deepEqual(body.envelope, capture.envelope);
  assert.equal(body.signature, capture.signature);
  assert.equal(
    canonicalJson(body),
    bytes.subarray(ECG_RECORDING_MAGIC.length).toString(),
  );
  const changed = clone(capture);
  changed.sampleChunks[0]!.normalized_payload.samples[0]!.value++;
  assert.throws(() => readerRawRecording(changed, expected, cap));
  changed.sampleChunks = Array.from(
    { length: 65 },
    () => capture.sampleChunks[0]!,
  );
  assert.throws(() => readerRawRecording(changed, expected, cap));
  assert.throws(() =>
    readerRawRecording(capture, { ...expected, channel: "ppg" }, cap),
  );
  const foreign = clone(capture);
  foreign.sampleChunks[0]!.envelope.owner_ref = randomUUID();
  assert.throws(() => readerRawRecording(foreign, expected, cap));
});

test("feature-only reader rejects unsolicited raw samples before retaining a ledger", async () => {
  const { controller, transport } = await connected();
  transport.sendUnrequestedSamples = true;
  await controller.requestBindingProof(transcript);
  controller.installBinding(binding, scope);
  const prepared = await controller.prepareAuthorizedCapture(context);
  assert.equal(prepared.device_nonce, deviceNonce);
  const started = {
    ...options,
    server_start: serverStart(),
  };
  await assert.rejects(
    controller.captureAuthorized("ecg", context, started),
    fails("UNREQUESTED_RAW_SAMPLES"),
  );
  assert.equal(controller.snapshot().association, null);
  await controller.dispose();
});

test("actual SparkFun production factory decodes derived-only quality evidence without inventing raw consent or cadence", () => {
  const normalized = JSON.parse(
    readFileSync(
      fileURLToPath(
        new URL(
          "../../../../../firmware/tests/fixtures/sparkfun-ppg-result-v1.json",
          import.meta.url,
        ).href,
      ),
      "utf8",
    ),
  );
  const sdkExpected: ExpectedReaderCapture = {
    ...expected,
    channel: "ppg",
    configuration_id: normalized.projection.acquisition_config_id,
    max_duration_ms: 5000,
  };
  function sdkCompletion(n: typeof normalized) {
    const e = signedEnvelope(n);
    return {
      ...completion(),
      channel: "ppg",
      started_monotonic_ms: 0,
      ended_monotonic_ms: 2160,
      envelope: e,
      signature: signature("OTGD-CAPTURE-v1\n", e),
      normalized_payload: n,
    };
  }
  const result = signedReaderCapture(
    sdkCompletion(normalized),
    sdkExpected,
    cap,
  );
  assert.deepEqual(result.normalized_payload, normalized);
  assert.equal(result.modelEligible, false);
  assert.equal(result.rawRecording, null);
  assert.equal(result.sampleChunks.length, 0);
  assert.equal(normalized.projection.heart_rate_bpm, 75);
  assert.equal(normalized.ppg_evidence.configured_sensor_rate_hz, 50);
  assert.equal(normalized.ppg_evidence.actual_sensor_cadence_hz, null);
  assert.equal(
    Object.hasOwn(normalized.ppg_evidence.last_observation, "ir_count"),
    false,
  );
  for (const modify of [
    (n: typeof normalized) => {
      n.ppg_evidence.last_observation.ir_count = 123;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.last_observation.red_count = 123;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.actual_sensor_cadence_hz = 50;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.sensor_dropped_samples = 0;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.sdk_commit = "f".repeat(40);
    },
    (n: typeof normalized) => {
      n.ppg_evidence.last_observation.sequence = 2;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.last_observation.finger_status = 2;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.last_observation.confidence_percent = 101;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.valid_samples = 3;
    },
    (n: typeof normalized) => {
      n.ppg_evidence.last_observation.host_received_monotonic_us =
        n.ppg_evidence.acquisition_ended_monotonic_us;
    },
    (n: typeof normalized) => {
      n.projection.heart_rate_bpm = 74;
    },
    (n: typeof normalized) => {
      n.projection.modality = "ecg";
    },
    (n: typeof normalized) => {
      n.ppg_evidence.algorithm_mode = true;
    },
    (n: typeof normalized) => {
      n.projection.quality_flags = [];
    },
  ]) {
    const changed = clone(normalized);
    modify(changed);
    assert.throws(() =>
      signedReaderCapture(sdkCompletion(changed), sdkExpected, cap),
    );
  }
  const invalid = clone(normalized);
  invalid.projection.status = "invalid";
  invalid.projection.heart_rate_bpm = null;
  invalid.ppg_evidence.hub_firmware = null;
  invalid.ppg_evidence.configured_sensor_rate_hz = null;
  invalid.ppg_evidence.observed_samples = 0;
  invalid.ppg_evidence.valid_samples = 0;
  invalid.ppg_evidence.last_observation = null;
  assert.deepEqual(
    signedReaderCapture(sdkCompletion(invalid), sdkExpected, cap)
      .normalized_payload,
    invalid,
  );
});
