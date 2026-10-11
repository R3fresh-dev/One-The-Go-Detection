import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID, generateKeyPairSync, sign } from "node:crypto";
import rawFixture from "../testfixtures/backend-raw-recordings.json";
import readerFixture from "../testfixtures/signed-reader-raw-ecg.json";
import { readerRawRecording } from "../src/device/physicalRaw";
import type {
  SignedReaderCapture,
  ExpectedReaderCapture,
  PhysicalCapabilities,
} from "../src/device/physicalProtocol";
import { clone, digest, digestText } from "../src/core/integrity";
import {
  configurationFor,
  configurationsFor,
  verifyCaptureGrant,
  verifyCaptureStart,
} from "../src/core/acquisition";
import { queueCheck } from "../src/services/sync";
import type { CheckRecord, JsonObject } from "../src/core/types";
require("./support/runtime.cjs");
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");
import { customerService, deferred } from "./support/customer";
import { DeviceError } from "../src/device/protocol";

async function approvedAccount(
  channel: "ppg" | "ecg" = "ppg",
  recordRaw = false,
) {
  const service = customerService(),
    previous = globalThis.fetch;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  const app = new AppController();
  await app.initialize();
  await app.signIn();
  const rawStatus = clone(rawFixture);
  rawStatus.choices.ecg_waveform = { record: true, upload: false };
  rawStatus.preference_receipt.choices.ecg_waveform = {
    record: true,
    upload: false,
  };
  const studyId = recordRaw ? rawStatus.study_id : "fictional-approved-study",
    protocolId = "fictional-approved-protocol",
    bindingId = randomUUID(),
    bootId = randomUUID();
  const document =
    "Fictional approved workflow test. No human or instrument qualification.";
  const study: any = {
    study_id: studyId,
    name: "Fictional workflow study",
    invitation_id: randomUUID(),
    document_version: "v1",
    document_text: document,
    document_sha256: digestText(document),
  };
  study.consent = {
    study_id: studyId,
    invitation_id: study.invitation_id,
    document_version: "v1",
    document_sha256: study.document_sha256,
    state: "active",
    accepted: true,
    consent_record_id: recordRaw ? rawStatus.consent_record_id : randomUUID(),
  };
  const material = {
    schema_version: "1.0.0",
    fixture: "fictional-controller-flow",
    sample_rate_hz: 1000,
    raw_sample_limit: recordRaw ? 1024 : 0,
    raw_encoding: recordRaw ? "otgd_ecg_samples_v1" : null,
  };
  const config = {
    study_id: studyId,
    protocol_id: protocolId,
    configuration_id:
      channel === "ppg" ? "fictional-ppg-v1" : "fictional-ecg-v1",
    configuration_hash: digest(material),
    configuration_version: "v1",
    submitted_sha256: "a".repeat(64),
    expires_at: new Date(Date.now() + 60_000).toISOString(),
    supported_phone_models: ["Fictional-phone"],
    software_adapter_id: "otgd_signed_reader_v1",
  };
  service.caps.channels[channel === "ppg" ? "cardiac" : "ecg"] = {
    available: true,
    authorization_available: true,
    software_available: true,
    reason_codes: [],
    configurations: [config],
  };
  service.overrides.set("/v1/me/studies", () =>
    service.result({ items: [study] }),
  );
  service.overrides.set(`/v1/studies/${studyId}/raw-recordings`, () =>
    service.result(rawStatus),
  );
  const events: string[] = [];
  const association: any = {
    deviceId: "fictional-reader",
    bootId,
    hardwareRevision: "fictional-hw",
    firmwareVersion: "fictional-fw",
    verifiedBindingId: bindingId,
    source: "prototype_sensor",
    capabilities: {
      key_id: "fictional-key",
      device_id: "fictional-reader",
      boot_id: bootId,
      hardware_revision: "fictional-hw",
      firmware_version: "fictional-fw",
      channels: [channel],
    },
  };
  const oldDevice = app.device,
    key = generateKeyPairSync("ec", { namedCurve: "prime256v1" });
  const signed = (value: any) =>
    sign(
      "sha256",
      Buffer.from(
        "OTGD-CAPTURE-v1\n" +
          require("../src/core/integrity").canonicalJson(value),
      ),
      key.privateKey,
    ).toString("base64");
  const device: any = {
    snapshot: () => ({
      state: "connected_reader",
      association,
      captureInProgress: false,
    }),
    cancelCapture: async () => {
      events.push("stop-device");
    },
    stopScan: async () => {},
    forget: async () => {
      association.verifiedBindingId = null;
    },
    dispose: async () => {},
    prepareAuthorizedCapture: async () => {
      events.push("prepare-device-nonce");
      return { device_boot_id: bootId, device_nonce: "N".repeat(43) };
    },
    captureAuthorized: async (channel: string, context: any, options: any) => {
      events.push("hardware-acquire");
      assert.equal(channel, recordRaw ? "ecg" : "ppg");
      assert.equal(options.capture_context_sha256, digest(app.check!.context));
      const startedAt = new Date().toISOString();
      const projection = {
        status: "valid",
        source: "prototype_sensor",
        started_at: startedAt,
        ended_at: recordRaw
          ? new Date(Date.now() + 1000).toISOString()
          : startedAt,
        quality_flags: [],
        acquisition_config_id: config.configuration_id,
        modality: channel,
        heart_rate_bpm: 72,
        ecg_status: channel === "ecg" ? "valid" : "not_collected",
        ecg_rmssd_ms: null,
        sample_rate_hz: 1000,
        raw_artifact_id: null,
      };
      const result: any = {
        attestation_id: randomUUID(),
        envelope: {
          schema_version: "1.0.0",
          environment: options.environment,
          owner_ref: service.caps.account_ref,
          data_generation: 1,
          session_id: context.sessionId,
          attempt_id: context.attemptId,
          authorization_id: options.authorization_id,
          binding_id: bindingId,
          device_id: association.deviceId,
          key_id: "fictional-key",
          boot_id: bootId,
          sequence: 1,
          configuration_hash: config.configuration_hash,
          payload_sha256: digest(projection),
        },
        signature: "TEST_BOUNDARY_NOT_A_PHYSICAL_SIGNATURE",
        normalized_payload: projection,
        startedAt,
        endedAt: projection.ended_at,
        source: "prototype_sensor",
        modelEligible: false,
        deviceStartedMonotonicMs: 100,
        deviceEndedMonotonicMs: 100,
        sampleChunks: [],
        rawRecording: null,
      };
      result.signature = signed(result.envelope);
      if (recordRaw) {
        const sample = clone(readerFixture.capture.sampleChunks[0]!);
        sample.envelope = {
          ...result.envelope,
          sequence: 0,
          payload_sha256: digest(sample.normalized_payload),
        };
        sample.signature = signed(sample.envelope);
        result.envelope.sequence = 1;
        result.signature = signed(result.envelope);
        result.deviceStartedMonotonicMs = 1000;
        result.deviceEndedMonotonicMs = 2000;
        result.sampleChunks = [sample];
        result.rawRecording = readerRawRecording(
          result as SignedReaderCapture,
          {
            ...options,
            session_id: context.sessionId,
            attempt_id: context.attemptId,
            record_id: context.captureId,
            workspace_epoch: context.workspaceEpoch,
            channel: "ecg",
          } as ExpectedReaderCapture,
          association.capabilities as PhysicalCapabilities,
        );
      }
      return result;
    },
  };
  Object.defineProperty(app, "device", { value: device });
  service.overrides.set("POST /v1/sessions", (call) => {
    events.push("register");
    return service.result(
      { session_id: call.body.session_id, revision: 0 },
      201,
      { ETag: '"0"' },
    );
  });
  let authorizationId = randomUUID();
  // The fake service implements only transport boundaries; all customer domain,
  // storage, idempotency, ownership and actual HTTP sequencing run unchanged.
  const original = service.fetcher;
  globalThis.fetch = async (input, init) => {
    const path = new URL(String(input)).pathname;
    if (path.includes("/context"))
      service.overrides.set("PUT " + path, (call) => {
        events.push("context");
        return service.result({
          record_id: call.body.session_id,
          revision: 1,
          sha256: digest(call.body),
        });
      });
    if (path.includes("/attempts/"))
      service.overrides.set("PUT " + path, (call) => {
        events.push(
          call.body.status === "started"
            ? "started-attempt"
            : "terminal-attempt",
        );
        return service.result({
          record_id: call.body.attempt_id,
          revision: call.body.status === "started" ? 1 : 2,
          sha256: digest(call.body),
        });
      });
    if (path.endsWith("/capture-authorizations"))
      service.overrides.set("POST " + path, (call) => {
        events.push("grant");
        return service.result({
          ...call.body,
          authorization_id: authorizationId,
          session_id: app.check!.id,
          state: "issued",
          expires_at: new Date(Date.now() + 60_000).toISOString(),
          expires_epoch: (Date.now() + 60_000) / 1000,
          configuration_max_duration_ms: recordRaw ? 1000 : 15_000,
          supported_phone_models: config.supported_phone_models,
          software_adapter_id: config.software_adapter_id,
          configuration_submitted_sha256: config.submitted_sha256,
          configuration_version: config.configuration_version,
          capture_context_sha256: digest(app.check!.context),
          configuration_material: material,
          raw_recording_permission: recordRaw
            ? {
                record: true,
                upload: false,
                receipt_id: rawStatus.receipt_id,
                policy_id: rawStatus.policy.policy_id,
                policy_version: rawStatus.policy.version,
                policy_sha256: rawStatus.policy.sha256,
                raw_notice_version: rawStatus.policy.raw_notice.version,
                raw_notice_sha256: rawStatus.policy.raw_notice.sha256,
              }
            : null,
        });
      });
    if (path.endsWith("/start"))
      service.overrides.set("POST " + path, (call) => {
        events.push("online-start");
        assert.equal(call.body.device_nonce, "N".repeat(43));
        return service.result({
          authorization_id: authorizationId,
          attempt_id: call.body.attempt_id,
          device_boot_id: call.body.device_boot_id,
          state: "started",
          server_started_at: new Date().toISOString(),
          raw_recording_permission: recordRaw
            ? {
                record: true,
                upload: false,
                receipt_id: rawStatus.receipt_id,
                policy_id: rawStatus.policy.policy_id,
                policy_version: rawStatus.policy.version,
                policy_sha256: rawStatus.policy.sha256,
                raw_notice_version: rawStatus.policy.raw_notice.version,
                raw_notice_sha256: rawStatus.policy.raw_notice.sha256,
              }
            : null,
          server_start: {
            domain: "OTGD capture grant v1\u0000",
            grant: {
              authorization_id: authorizationId,
              attempt_id: call.body.attempt_id,
              session_id: app.check!.id,
              configuration_hash: config.configuration_hash,
              configuration_submitted_sha256: config.submitted_sha256,
              capture_context_sha256: digest(app.check!.context),
              boot_id: call.body.device_boot_id,
              raw_recording_permission: recordRaw
                ? {
                    record: true,
                    upload: false,
                    receipt_id: rawStatus.receipt_id,
                    policy_id: rawStatus.policy.policy_id,
                    policy_version: rawStatus.policy.version,
                    policy_sha256: rawStatus.policy.sha256,
                    raw_notice_version: rawStatus.policy.raw_notice.version,
                    raw_notice_sha256: rawStatus.policy.raw_notice.sha256,
                  }
                : null,
            },
            signature: "TEST_DEVICE_BOUNDARY_NOT_A_SIGNATURE",
          },
        });
      });
    return original(input, init);
  };
  return {
    app,
    service,
    study,
    config,
    events,
    device,
    association,
    close: async () => {
      await app.auth.clear();
      await app.dispose();
      await oldDevice.dispose();
      globalThis.fetch = previous;
    },
  };
}

async function bindingAccount() {
  const h = await approvedAccount();
  const proofs: string[] = [],
    accepted = new Map<string, any>();
  let loseReply = false,
    failProof = false,
    rejectInstall = false;
  Object.assign(h.association.capabilities, {
    protocol_version: 1,
    encodings: [1],
    max_logical_bytes: 8192,
    max_att_bytes: 20,
    protocol_id: "otgd_signed_reader_v1",
    source: "prototype_sensor",
    timestamp_resolution_ms: 1,
  });
  h.device.requestBindingProof = async (transcript: any) => {
    if (failProof) throw new Error("reader disconnected before proof");
    proofs.push(transcript.challenge_id);
    return { signature: "device-proof:" + transcript.challenge_id };
  };
  h.device.installBinding = (receipt: any, scope: any) => {
    assert.equal(scope.owner_ref, h.service.caps.account_ref);
    assert.equal(scope.data_generation, 1);
    if (rejectInstall) {
      rejectInstall = false;
      throw new DeviceError("PHYSICAL_CAPTURE_SCOPE");
    }
    h.association.verifiedBindingId = receipt.binding_id;
  };
  h.service.overrides.set("POST /v1/device-bindings/challenges", () => {
    const challengeId = randomUUID();
    return h.service.result({
      challenge_id: challengeId,
      domain: "OTGD-BIND-v1\n",
      signature_format: "ECDSA_P256_SHA256_DER_BASE64",
      transcript: {
        schema_version: "1.0.0",
        challenge_id: challengeId,
        environment: "test",
        owner_ref: h.service.caps.account_ref,
        data_generation: 1,
        device_id: h.association.deviceId,
        key_id: h.association.capabilities.key_id,
        nonce: Buffer.alloc(32, 1).toString("base64url"),
        expires_at: new Date(Date.now() + 300_000).toISOString(),
        hardware_revision: h.association.hardwareRevision,
        firmware_version: h.association.firmwareVersion,
      },
    });
  });
  h.service.overrides.set("POST /v1/device-bindings", (call) => {
    const key = call.headers.get("Idempotency-Key")!;
    const prior = accepted.get(key);
    if (prior) {
      assert.deepEqual(call.body, prior.request);
      return h.service.result(prior.receipt);
    }
    const intent = h.app.getSnapshot().state!.deviceBindingIntent!;
    assert.equal(call.body.signature, "device-proof:" + call.body.challenge_id);
    if (
      Date.parse(String((intent.challenge!.transcript as any).expires_at)) <=
      Date.now()
    )
      return h.service.result({ code: "CHALLENGE_EXPIRED_OR_USED" }, 409);
    const receipt = {
      binding_id: randomUUID(),
      device_id: h.association.deviceId,
      key_id: h.association.capabilities.key_id,
      hardware_revision: h.association.hardwareRevision,
      firmware_version: h.association.firmwareVersion,
      state: "active",
      bound_at: new Date().toISOString(),
    };
    accepted.set(key, { request: clone(call.body), receipt });
    if (loseReply) {
      loseReply = false;
      throw new Error("accepted reply lost");
    }
    return h.service.result(receipt);
  });
  h.service.overrides.set("GET /v1/device-bindings", () =>
    h.service.result({
      items: [...accepted.values()].map(({ receipt }) => ({
        ...receipt,
        key_active: true,
      })),
    }),
  );
  return {
    ...h,
    proofs,
    accepted,
    loseNextReply: () => {
      loseReply = true;
    },
    failNextProof: (value: boolean) => {
      failProof = value;
    },
    reconnectBeforeReceipt: () => {
      rejectInstall = true;
    },
  };
}

test("binding lost accepted response replays its durable completion identity after challenge expiry", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const h = await bindingAccount();
  try {
    h.loseNextReply();
    await assert.rejects(
      h.app.bindConnectedReader(),
      (e: any) => e.retryable === true,
    );
    const retained = clone(h.app.getSnapshot().state!.deviceBindingIntent!);
    assert.equal(h.proofs.length, 1);
    context.mock.timers.setTime(Date.now() + 301_000);
    await h.app.bindConnectedReader();
    const completions = h.service.calls.filter(
      (c) => c.method === "POST" && c.path === "/v1/device-bindings",
    );
    assert.equal(completions.length, 2);
    assert.equal(
      completions[1]!.headers.get("Idempotency-Key"),
      retained.completion_key,
    );
    assert.deepEqual(completions[1]!.body, completions[0]!.body);
    assert.equal(h.proofs.length, 1);
    assert.equal(h.accepted.size, 1);
    assert.equal(h.app.getSnapshot().state!.deviceBindingIntent, undefined);
  } finally {
    await h.close();
  }
});

test("binding reconnect reconciles old receipt then requires a new device proof in the current connection", async () => {
  const h = await bindingAccount();
  try {
    h.loseNextReply();
    await assert.rejects(h.app.bindConnectedReader());
    const firstKey =
      h.app.getSnapshot().state!.deviceBindingIntent!.completion_key;
    h.reconnectBeforeReceipt();
    await h.app.bindConnectedReader();
    assert.equal(h.proofs.length, 2);
    assert.notEqual(h.proofs[0], h.proofs[1]);
    assert.equal(h.accepted.size, 2);
    const completions = h.service.calls.filter(
      (c) => c.method === "POST" && c.path === "/v1/device-bindings",
    );
    assert.equal(completions[1]!.headers.get("Idempotency-Key"), firstKey);
    assert.notEqual(completions[2]!.headers.get("Idempotency-Key"), firstKey);
    assert.equal(h.app.getSnapshot().state!.deviceBindingIntent, undefined);
  } finally {
    await h.close();
  }
});

test("expired unsigned challenge rotates before proof while denied or unknown completion preserves exact identity", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const h = await bindingAccount();
  try {
    h.failNextProof(true);
    await assert.rejects(h.app.bindConnectedReader(), /reader disconnected/);
    const unsigned = clone(h.app.getSnapshot().state!.deviceBindingIntent!);
    context.mock.timers.setTime(Date.now() + 301_000);
    h.failNextProof(false);
    h.service.overrides.set("POST /v1/device-bindings", () =>
      h.service.result({ code: "DEVICE_KEY_REVOKED" }, 403),
    );
    await assert.rejects(
      h.app.bindConnectedReader(),
      (e: any) => e.code === "DEVICE_KEY_REVOKED",
    );
    const denied = clone(h.app.getSnapshot().state!.deviceBindingIntent!);
    assert.notEqual(denied.challenge_key, unsigned.challenge_key);
    assert.notEqual(denied.completion_key, unsigned.completion_key);
    assert.equal(h.proofs.length, 1);
    await assert.rejects(
      h.app.bindConnectedReader(),
      (e: any) => e.code === "DEVICE_KEY_REVOKED",
    );
    assert.deepEqual(h.app.getSnapshot().state!.deviceBindingIntent, denied);
    assert.equal(h.proofs.length, 1);
  } finally {
    await h.close();
  }
});

test("late binding receipt cannot bind a foreign replacement or erase a newer same-owner intent", async () => {
  const h = await bindingAccount();
  try {
    const entered = deferred<void>(),
      reply = deferred<Response>();
    const complete = h.service.overrides.get("POST /v1/device-bindings")!;
    h.service.overrides.set("POST /v1/device-bindings", async (call) => {
      const response = await complete(call);
      entered.resolve();
      await reply.promise;
      return response;
    });
    const pending = h.app.bindConnectedReader();
    const rejected = assert.rejects(
      pending,
      (e: any) => e.code === "BINDING_TARGET_CHANGED",
    );
    await entered.promise;
    h.association.deviceId = "different-reader";
    h.association.capabilities.device_id = "different-reader";
    h.association.capabilities.key_id = "different-key";
    const replacement = {
      device_id: "different-reader",
      key_id: "different-key",
      challenge_key: randomUUID(),
      completion_key: randomUUID(),
      challenge: null,
      signature: null,
    };
    await (h.app as any).commit((state: any) => ({
      ...state,
      deviceBindingIntent: replacement,
    }));
    reply.resolve(h.service.result({}));
    await rejected;
    assert.deepEqual(
      h.app.getSnapshot().state!.deviceBindingIntent,
      replacement,
    );
    assert.equal(h.proofs.length, 1);
    assert.equal(
      h.service.calls.filter((c) => c.path === "/v1/device-bindings/challenges")
        .length,
      1,
    );
    assert.equal(
      h.service.calls.filter(
        (c) => c.path === "/v1/device-bindings" && c.method === "POST",
      ).length,
      1,
    );
  } finally {
    await h.close();
  }
});

test("reader change during expired-intent removal never starts recovery for its replacement", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const h = await bindingAccount();
  const store = (h.app as any).store,
    originalSave = store.save.bind(store);
  try {
    h.failNextProof(true);
    await assert.rejects(h.app.bindConnectedReader(), /reader disconnected/);
    context.mock.timers.setTime(Date.now() + 301_000);
    h.failNextProof(false);
    const entered = deferred<void>(),
      release = deferred<void>();
    store.save = async (state: any) => {
      if (!state.deviceBindingIntent) {
        entered.resolve();
        await release.promise;
      }
      await originalSave(state);
    };
    const pending = h.app.bindConnectedReader();
    const rejected = assert.rejects(
      pending,
      (e: any) => e.code === "BINDING_TARGET_CHANGED",
    );
    await entered.promise;
    h.association.deviceId = "replacement-reader";
    h.association.capabilities.device_id = "replacement-reader";
    h.association.capabilities.key_id = "replacement-key";
    release.resolve();
    await rejected;
    assert.equal(h.proofs.length, 0);
    assert.equal(
      h.service.calls.filter((c) => c.path === "/v1/device-bindings/challenges")
        .length,
      1,
    );
    assert.equal(
      h.service.calls.some(
        (c) => c.method === "POST" && c.path === "/v1/device-bindings",
      ),
      false,
    );
  } finally {
    store.save = originalSave;
    await h.close();
  }
});

test("delayed initial intent commit cannot overwrite the replacement reader's newer intent", async () => {
  const h = await bindingAccount();
  const store = (h.app as any).store,
    originalSave = store.save.bind(store);
  try {
    const entered = deferred<void>(),
      release = deferred<void>();
    const replacement = {
      device_id: "replacement-reader",
      key_id: "replacement-key",
      challenge_key: randomUUID(),
      completion_key: randomUUID(),
      challenge: null,
      signature: null,
    };
    store.save = async (state: any) => {
      entered.resolve();
      await release.promise;
      await originalSave(state);
    };
    const newer = h.app.commit((state) => ({
      ...state,
      deviceBindingIntent: replacement,
    }));
    await entered.promise;
    const pending = h.app.bindConnectedReader();
    const rejected = assert.rejects(
      pending,
      (e: any) => e.code === "BINDING_TARGET_CHANGED",
    );
    h.association.deviceId = "replacement-reader";
    h.association.capabilities.device_id = "replacement-reader";
    h.association.capabilities.key_id = "replacement-key";
    release.resolve();
    await newer;
    await rejected;
    assert.deepEqual(
      h.app.getSnapshot().state!.deviceBindingIntent,
      replacement,
    );
    assert.equal(h.proofs.length, 0);
    assert.equal(
      h.service.calls.some((c) => c.path === "/v1/device-bindings/challenges"),
      false,
    );
    // A rejected serialized mutation preserves the published model. The next
    // explicit commit recovers the write chain before ordinary shutdown.
    await h.app.commit((state) => state);
  } finally {
    store.save = originalSave;
    await h.close();
  }
});

test("approved research start freezes exact online study/configuration context and device binding before any acquisition", async () => {
  const { app, service, study, config, association, close } =
    await approvedAccount();
  try {
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    const check = app.check!;
    assert.equal(check.snapshot.mode, "controlled_research");
    assert.equal(check.snapshot.study_id, study.study_id);
    assert.deepEqual(check.context.configuration_refs, [
      {
        id: config.configuration_id,
        version: "v1",
        sha256: config.configuration_hash,
        scope: "measurement_collection",
      },
    ]);
    assert.equal(
      check.context.device_associations[0]!.binding_id,
      association.verifiedBindingId,
    );
    assert.equal(
      service.calls.filter(
        (call) => call.method !== "GET" && call.path.startsWith("/v1/sessions"),
      ).length,
      0,
    );
    assert.equal(
      configurationFor(check, app.getSnapshot().state!.capabilities, "cardiac")
        .submitted_sha256,
      config.submitted_sha256,
    );
    assert.equal(
      configurationsFor(
        app.getSnapshot().state!.capabilities,
        "uninvited-study",
      ).length,
      0,
    );
    await assert.rejects(
      app.beginStudyCheck(study.study_id, config.protocol_id, true),
      /Resume or discard/,
    );
  } finally {
    await close();
  }
});

test("actual customer sequence persists keys and metadata before fresh online start, retains signed projection locally, and only explicit upload queues evidence", async () => {
  const { app, study, config, events, close } = await approvedAccount();
  try {
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    await app.captureReader("ppg");
    assert.deepEqual(events, [
      "register",
      "context",
      "started-attempt",
      "grant",
      "prepare-device-nonce",
      "online-start",
      "hardware-acquire",
    ]);
    const check = app.check!,
      attempt = check.attempts[0]!;
    assert.equal(attempt.status, "valid");
    assert.equal(check.snapshot.cardiac.heart_rate_bpm, 72);
    assert.equal(attempt.attestation_refs.length, 1);
    assert.equal(
      app.check!.attestations![attempt.attempt_id]!.sampleChunks,
      undefined,
    );
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    await app.saveCheck();
    assert.equal(app.check!.frozen, true);
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    const queued = queueCheck(
        app.getSnapshot().state!,
        check.id,
        randomUUID,
        new Date().toISOString(),
      ),
      intent = queued.queue[0]!;
    assert.equal(intent.keys.register, check.acquisition!.register_key);
    assert.equal(intent.keys.context, check.acquisition!.context_key);
    assert.equal(
      intent.keys[`attempt:${attempt.attempt_id}`],
      check.acquisition!.attempts[attempt.attempt_id]!.terminal_key,
    );
  } finally {
    await close();
  }
});

test("explicit ECG raw choice uses a fresh signed recording receipt and the real bounded encoder before atomic encrypted local save", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const { app, study, service, events, close } = await approvedAccount(
    "ecg",
    true,
  );
  try {
    await app.beginStudyCheck(
      study.study_id,
      "fictional-approved-protocol",
      true,
    );
    await app.refreshRawRecordings(study.study_id);
    await assert.rejects(
      app.captureReader("ecg", true),
      /encrypted native storage/,
    );
    assert.equal(events.includes("hardware-acquire"), false);
    const store = (app as any).store,
      saved: Uint8Array[] = [];
    store.deleteRaw = async () => {};
    store.saveWithRaw = async (
      state: any,
      _id: string,
      bytes: Uint8Array,
      current: () => boolean,
    ) => {
      assert.equal(current(), true);
      saved.push(bytes);
      await store.save(state);
    };
    await app.captureReader("ecg", true);
    const raw = app.getSnapshot().state!.rawArtifacts![0]!;
    assert.equal(raw.artifact_kind, "ecg_waveform");
    assert.equal(raw.permission.record, true);
    assert.equal(raw.permission.upload, false);
    assert.equal(raw.state, "local");
    assert.equal(saved.length, 1);
    assert.equal(
      saved[0]!.every((byte) => byte === 0),
      true,
    );
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    assert.equal(
      service.calls.some((call) => call.path === "/v1/artifact-uploads"),
      false,
    );
    const grant = service.calls.find((call) =>
      call.path.endsWith("/capture-authorizations"),
    )!;
    assert.equal(grant.body.raw_recording_kind, "ecg_waveform");
    context.mock.timers.setTime(Date.now() + 1000);
    await app.saveCheck();
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    assert.equal(
      app.check!.attestations![raw.attempt_id]!.sampleChunks,
      undefined,
    );
  } finally {
    await close();
  }
});

test("revoked consent, stale approval and reader substitution cannot invoke hardware", async () => {
  const { app, study, config, device, association, events, close } =
    await approvedAccount();
  try {
    study.consent.state = "withdrawn";
    await assert.rejects(
      app.beginStudyCheck(study.study_id, config.protocol_id, true),
      /Confirm the current/,
    );
    study.consent.state = "active";
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    association.bootId = randomUUID();
    await assert.rejects(
      app.captureReader("ppg"),
      /different reader or reboot/,
    );
    assert.equal(events.includes("hardware-acquire"), false);
    assert.equal(app.check!.attempts.length, 0);
  } finally {
    await close();
  }
});

test("interruption while server start is pending stops before hardware and rejects a late matching response", async () => {
  const { app, service, study, config, events, close } =
    await approvedAccount();
  try {
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    const entered = deferred<void>(),
      reply = deferred<Response>();
    const original = globalThis.fetch;
    globalThis.fetch = async (input, init) => {
      if (new URL(String(input)).pathname.endsWith("/start")) {
        entered.resolve();
        return reply.promise;
      }
      return original(input, init);
    };
    const pending = app.captureReader("ppg");
    await entered.promise;
    const stopped = app.stopActive("USER_CANCELED");
    // Shutdown requests are dispatched before the outstanding start reply.
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(events.includes("stop-device"), true);
    reply.resolve(service.result({ state: "started" }));
    await Promise.allSettled([pending, stopped]);
    assert.equal(events.includes("hardware-acquire"), false);
    assert.equal(app.check!.attempts[0]!.status, "invalid");
  } finally {
    await close();
  }
});

test("actual Python HTTP grant/start envelope binds material, frozen context and signed fresh start without simulated clinical authority", (context) => {
  const fixture = require("../testfixtures/backend-capture-authorization.json");
  const grant = fixture.authorization;
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(fixture.start.server_started_at),
  });
  const config = {
    study_id: "fictional-governance-study",
    protocol_id: fixture.context.protocol_id,
    configuration_id: grant.configuration_id,
    configuration_hash: grant.configuration_hash,
    configuration_version: grant.configuration_version,
    submitted_sha256: grant.configuration_submitted_sha256,
    expires_at: grant.expires_at,
    supported_phone_models: grant.supported_phone_models,
    supported_os_versions: grant.supported_os_versions,
    supported_native_builds: grant.supported_native_builds,
    software_adapter_id: grant.software_adapter_id,
  };
  const check = {
    id: grant.session_id,
    context: fixture.context,
  } as CheckRecord;
  const accepted = verifyCaptureGrant(
    grant,
    check,
    grant.attempt_id,
    "task",
    config,
    null,
    null,
  );
  verifyCaptureStart(
    fixture.start,
    accepted,
    grant.attempt_id,
    fixture.start.device_boot_id,
  );
  assert.equal(digest(grant.configuration_material), grant.configuration_hash);
  const { createPublicKey, verify } = require("node:crypto");
  const { canonicalJson } = require("../src/core/integrity");
  const token = fixture.start.server_start;
  assert.equal(
    verify(
      "sha256",
      Buffer.from(token.domain + canonicalJson(token.grant)),
      createPublicKey({
        key: Buffer.from(fixture.server_public_key_spki, "base64"),
        format: "der",
        type: "spki",
      }),
      Buffer.from(token.signature, "base64"),
    ),
    true,
  );
  for (const mutate of [
    (g: any) => (g.configuration_material.changed = true),
    (g: any) => (g.configuration_submitted_sha256 = "1".repeat(64)),
    (g: any) => (g.configuration_version = "v2"),
    (g: any) => (g.capture_context_sha256 = "1".repeat(64)),
    (g: any) => (g.supported_os_versions = ["unapproved"]),
    (g: any) => (g.supported_native_builds = ["unapproved"]),
    (g: any) => (g.raw_recording_permission = { record: true }),
    (g: any) => (g.expires_epoch = 0),
  ]) {
    const changed = clone(grant);
    mutate(changed);
    assert.throws(() =>
      verifyCaptureGrant(
        changed,
        check,
        grant.attempt_id,
        "task",
        config,
        null,
        null,
      ),
    );
  }
  assert.throws(() =>
    verifyCaptureStart(
      { ...fixture.start, device_boot_id: randomUUID() },
      accepted,
      grant.attempt_id,
      fixture.start.device_boot_id,
    ),
  );
});
