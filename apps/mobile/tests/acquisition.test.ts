import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID, generateKeyPairSync, sign } from "node:crypto";
import rawFixture from "../testfixtures/backend-raw-recordings.json";
import participantFixture from "../testfixtures/backend-participant-acquisition.json";
import {
  validateInstructionInput,
  type InstructionInput,
} from "../src/core/participantAcquisition";
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
  channel: "ppg" | "ecg" | "saliva" = "ppg",
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
  const protocol: any =
    channel === "saliva"
      ? clone(participantFixture.import_flow.configuration.participant_protocol)
      : {
          schema_version: "1.0.0",
          kind: "cardiac",
          instruction_id: "FICTIONAL-PREPARATION",
          version: "v1",
          text: "Fictional engineering bench preparation; no human safety approval.",
          sha256: digestText(
            "Fictional engineering bench preparation; no human safety approval.",
          ),
          maximum_acknowledgment_age_seconds: 120,
          required_confirmations: [
            "rest_completed",
            "posture_confirmed",
            "activity_confirmed",
            "contact_confirmed",
            "isolation_confirmed",
          ].map((id) => ({ id, text: id })),
          operating_scope: "engineering_bench",
          operating_state_verifier: "participant_declaration_only",
          rest_duration_seconds: 0,
          posture_instruction: "Fictional seated setup",
          activity_instruction: "Remain still",
          contact_instruction: "Fictional bench only",
          isolation_instruction: "No human leads",
          permitted_setups: [
            {
              id: "fictional-bench",
              description: "Fictional bench",
              power_state: "battery",
              charging_state: "off",
              cable_state: "none",
              contact_or_lead_configuration: "bench-only",
            },
          ],
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
    software_adapter_id:
      channel === "saliva"
        ? "reference_lab_import_v1"
        : "otgd_signed_reader_v1",
    participant_protocol: protocol,
    participant_protocol_sha256: digest(protocol),
  };
  service.caps.channels[channel === "ppg" ? "cardiac" : channel] = {
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
  let acceptedInstruction: any = null;
  const instructionReceipts = new Map<string, any>();
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
    if (
      path.endsWith("/instruction-acknowledgments") &&
      !service.overrides.has("POST " + path)
    )
      service.overrides.set("POST " + path, (call) => {
        events.push("instruction-acknowledgment");
        const key = call.headers.get("Idempotency-Key")!;
        acceptedInstruction = instructionReceipts.get(key) ?? {
          ...clone(call.body),
          instruction_receipt_id: randomUUID(),
          session_id: app.check!.id,
          consent_record_id: study.consent.consent_record_id,
          accepted_at: new Date().toISOString(),
        };
        instructionReceipts.set(key, acceptedInstruction);
        return service.result(acceptedInstruction, 201);
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
          participant_protocol_sha256: config.participant_protocol_sha256,
          instruction_receipt_id: acceptedInstruction?.instruction_receipt_id,
          instruction_receipt: acceptedInstruction,
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
        assert.equal(
          call.body.device_nonce,
          channel === "saliva" ? null : "N".repeat(43),
        );
        return service.result({
          authorization_id: authorizationId,
          attempt_id: call.body.attempt_id,
          device_boot_id: call.body.device_boot_id,
          state: "started",
          server_started_at: new Date().toISOString(),
          participant_protocol_sha256: config.participant_protocol_sha256,
          instruction_receipt_id: acceptedInstruction?.instruction_receipt_id,
          instruction_receipt: acceptedInstruction,
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
              participant_protocol_sha256: config.participant_protocol_sha256,
              instruction_receipt_id:
                acceptedInstruction?.instruction_receipt_id,
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

function instruction(config: any): InstructionInput {
  const p = config.participant_protocol,
    acknowledgedAt = new Date().toISOString();
  return {
    participant_protocol_sha256: config.participant_protocol_sha256,
    acknowledged_at: acknowledgedAt,
    confirmed: true,
    confirmations: p.required_confirmations.map((c: any) => c.id),
    setup_id: p.kind === "cardiac" ? p.permitted_setups[0].id : null,
    rest_started_at:
      p.kind === "cardiac"
        ? new Date(
            Date.parse(acknowledgedAt) - p.rest_duration_seconds * 1000,
          ).toISOString()
        : null,
    collection_method_id: p.kind === "reference_lab" ? p.methods[0].id : null,
    collection_method_version:
      p.kind === "reference_lab" ? p.methods[0].version : null,
  };
}
test("instruction fixture samples one acknowledgment instant across clock rollover and preserves the approved rest duration", async () => {
  const h = await approvedAccount(),
    OriginalDate = Date,
    instant = OriginalDate.parse("2026-10-11T12:00:00.999Z");
  let clockReads = 0;
  const RollingDate = class extends OriginalDate {
    constructor(value?: string | number) {
      super(value === undefined ? instant + clockReads++ : value);
    }
    static now() {
      return instant + 100;
    }
  } as DateConstructor;
  try {
    globalThis.Date = RollingDate;
    for (const seconds of [0, 30]) {
      const config = clone(h.config);
      config.participant_protocol.rest_duration_seconds = seconds;
      config.participant_protocol_sha256 = digest(config.participant_protocol);
      const before = clockReads,
        value = instruction(config);
      assert.equal(clockReads - before, 1);
      assert.equal(
        Date.parse(value.acknowledged_at) - Date.parse(value.rest_started_at!),
        seconds * 1000,
      );
      assert.doesNotThrow(() =>
        validateInstructionInput(config, value, "cardiac"),
      );
      assert.throws(
        () =>
          validateInstructionInput(
            config,
            {
              ...value,
              rest_started_at: new OriginalDate(
                Date.parse(value.acknowledged_at) - seconds * 1000 + 1,
              ).toISOString(),
            },
            "cardiac",
          ),
        /approved rest period/,
      );
    }
  } finally {
    globalThis.Date = OriginalDate;
    await h.close();
  }
});
function currentInstruction(
  app: InstanceType<typeof AppController>,
  channel: string,
): InstructionInput {
  return instruction(
    app.getSnapshot().state!.capabilities!.channels[channel]!
      .configurations![0]!,
  );
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

test("lost accepted instruction reply is reconciled with its original body and key without restarting hardware", async () => {
  const h = await approvedAccount();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    const original = globalThis.fetch;
    let lost = false;
    globalThis.fetch = async (url, options) => {
      const reply = await original(url, options);
      if (String(url).endsWith("/instruction-acknowledgments") && !lost) {
        lost = true;
        throw new Error("accepted acknowledgment response lost");
      }
      return reply;
    };
    await assert.rejects(
      h.app.captureReader("ppg", false, currentInstruction(h.app, "cardiac")),
      (e: any) => e.retryable === true,
    );
    assert.equal(h.app.check!.attempts[0]!.status, "started");
    const saved = clone(
      h.app.check!.acquisition!.attempts[h.app.check!.attempts[0]!.attempt_id]!,
    );
    await h.app.reconcileInstructionReceipt();
    const calls = h.service.calls.filter((c) =>
      c.path.endsWith("/instruction-acknowledgments"),
    );
    assert.equal(calls.length, 2);
    assert.equal(
      calls[1]!.headers.get("Idempotency-Key"),
      saved.instruction_key,
    );
    assert.deepEqual(calls[1]!.body, calls[0]!.body);
    assert.equal(h.events.includes("hardware-acquire"), false);
    await h.app.stopActive("USER_CANCELED");
    assert.equal(h.app.check!.attempts[0]!.status, "invalid");
    assert.equal(h.app.check!.instruction_receipts!.length, 1);
    await assert.rejects(h.app.reconcileInstructionReceipt(), /No recoverable/);
  } finally {
    await h.close();
  }
});

test("online preparation persists before rest and current instructions cannot change the prepared acknowledgement", async () => {
  const h = await approvedAccount();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    const at = await h.app.prepareParticipantCapture("cardiac");
    assert.ok(Date.parse(at) <= Date.now());
    assert.deepEqual(h.events, ["register", "context", "started-attempt"]);
    assert.equal(h.app.check!.attempts[0]!.status, "started");
    assert.equal(h.events.includes("grant"), false);
    await h.app.captureReader("ppg", false, {
      ...currentInstruction(h.app, "cardiac"),
      rest_started_at: at,
    });
    assert.equal(h.events.filter((e) => e === "hardware-acquire").length, 1);
    assert.equal(h.app.check!.attempts.length, 1);
    assert.equal(
      h.app.check!.attempts[0]!.component_metadata.instruction_receipt != null,
      true,
    );
  } finally {
    await h.close();
  }
});

async function labAccount() {
  const h = await approvedAccount("saliva");
  let accepted: any = null,
    imported: any = null;
  let lost = false;
  let abandonLost = false,
    remoteAbandonment: any = null;
  const abandonResponses = new Map<string, any>();
  const responses = new Map<string, any>(),
    original = globalThis.fetch;
  globalThis.fetch = async (url, options) => {
    const path = new URL(String(url)).pathname;
    if (path.endsWith("/collections"))
      h.service.overrides.set("POST " + path, (call) => {
        const key = call.headers.get("Idempotency-Key")!,
          b = call.body,
          old = clone(
            h.app.check!.attempts.find((a) => a.attempt_id === b.attempt_id)!,
          );
        const sample = {
            sample_id: b.sample_id,
            collection_method_id: b.collection_method_id,
            collected_at: b.collected_at,
            volume_ml: b.saliva_volume_ml,
            dilution_factor: b.dilution_factor,
            status: b.status,
            quality_flags: b.quality_flags,
          },
          projection = { sample, saliva: [] };
        const grant =
          h.app.check!.acquisition!.attempts[b.attempt_id]!.authorization!;
        const receiptId = randomUUID();
        const terminal = {
          ...old,
          status: b.status,
          source: "reference_lab",
          started_at: b.collected_at,
          ended_at: b.collected_at,
          component_metadata: {
            armed_at: old.started_at,
            instruction_receipt: old.component_metadata.instruction_receipt,
            collection_receipt_id: receiptId,
            collection_request_sha256: digest(b),
            projection,
          },
        };
        accepted = responses.get(key) ?? {
          collection_receipt_id: receiptId,
          session_id: h.app.check!.id,
          request: clone(b),
          state: b.status === "valid" ? "pending_lab" : "invalid_collection",
          accepted_at: new Date().toISOString(),
          authorization_id: grant.authorization_id,
          configuration_submitted_sha256: grant.configuration_submitted_sha256,
          configuration_version: grant.configuration_version,
          participant_protocol_sha256: grant.participant_protocol_sha256,
          instruction_receipt: old.component_metadata.instruction_receipt,
          projection,
          attempt: terminal,
          attempt_revision: 2,
          attempt_sha256: digest(terminal),
        };
        responses.set(key, accepted);
        if (lost) {
          lost = false;
          throw new Error("specimen accepted response lost");
        }
        return h.service.result(accepted, 201);
      });
    if (path.includes("/collections/") && !path.endsWith("/abandon"))
      h.service.overrides.set("GET " + path, () =>
        h.service.result({
          ...(accepted ?? {}),
          collection_attempt: accepted?.attempt,
          collection_attempt_revision: 2,
          collection_attempt_sha256: accepted?.attempt_sha256,
          attempt: imported?.attempt ?? accepted?.attempt,
          attempt_revision: imported ? 1 : 2,
          attempt_sha256: imported
            ? digest(imported.attempt)
            : accepted?.attempt_sha256,
          state: remoteAbandonment
            ? "analysis_canceled"
            : imported
              ? "analysis_available"
              : "pending_lab",
          abandonment: remoteAbandonment,
          imports: imported ? [imported] : [],
        }),
      );
    if (path.endsWith("/abandon"))
      h.service.overrides.set("POST " + path, (call) => {
        const key = call.headers.get("Idempotency-Key")!;
        const receipt = abandonResponses.get(key) ?? {
          abandonment_id: randomUUID(),
          session_id: accepted.session_id,
          sample_id: accepted.request.sample_id,
          collection_receipt_id: accepted.collection_receipt_id,
          collection_sha256: digest(accepted),
          configuration_submitted_sha256: h.config.submitted_sha256,
          accepted_at: new Date().toISOString(),
          ...call.body,
          state: "analysis_canceled",
          collection: accepted,
        };
        abandonResponses.set(key, receipt);
        if (abandonLost) {
          abandonLost = false;
          throw new Error("accepted analysis cancellation response lost");
        }
        return h.service.result(receipt);
      });
    return original(url, options);
  };
  return {
    ...h,
    loseReply: () => {
      lost = true;
    },
    loseAbandonReply: () => {
      abandonLost = true;
    },
    abandonElsewhere: () => {
      remoteAbandonment = {
        abandonment_id: randomUUID(),
        session_id: accepted.session_id,
        sample_id: accepted.request.sample_id,
        collection_receipt_id: accepted.collection_receipt_id,
        collection_sha256: digest(accepted),
        configuration_submitted_sha256: h.config.submitted_sha256,
        accepted_at: new Date().toISOString(),
        confirmation: true,
        reason: "USER_CANCELED",
        state: "analysis_canceled",
      };
    },
    importReport: () => {
      const attempt = clone(accepted.attempt),
        measurements = clone(
          participantFixture.import_flow.import_status.imports[0]!.measurements,
        );
      for (const measurement of measurements) {
        measurement.sample_id = accepted.request.sample_id;
        measurement.collected_at = accepted.request.collected_at;
        measurement.measured_at = new Date().toISOString();
      }
      const report = randomUUID(),
        importId = randomUUID();
      attempt.attempt_id = randomUUID();
      attempt.supersedes_attempt_id = accepted.request.attempt_id;
      attempt.component_metadata.collection_attempt_id =
        accepted.request.attempt_id;
      attempt.component_metadata.lab_import_id = importId;
      attempt.component_metadata.projection.saliva = measurements;
      attempt.artifact_refs = [report];
      imported = {
        import_id: importId,
        measurements,
        attempt,
        source_report_artifact_id: report,
        attempt_revision: 1,
        attempt_sha256: digest(attempt),
      };
    },
    specimen: () => ({
      ...clone(participantFixture.import_flow.collection_request),
      collected_at: new Date().toISOString(),
      cartridge_expiry: new Date(Date.now() + 86400000).toISOString(),
      storage_handling_events: [
        {
          event: "sealed",
          occurred_at: new Date().toISOString(),
          temperature_c: null,
          duration_min: null,
        },
      ],
    }),
  };
}

test("reference laboratory collection has no BLE acquisition, persists a recoverable pending draft, imports separate analysis then permits explicit finalization", async () => {
  const h = await labAccount();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    await h.app.startLabCollection(currentInstruction(h.app, "saliva"));
    assert.equal(h.events.includes("prepare-device-nonce"), false);
    assert.equal(h.events.includes("hardware-acquire"), false);
    await h.app.saveLabCollectionDraft(
      h.app.check!.id,
      h.app.check!.labCollection!.attempt_id,
      { saliva_volume_ml: "1.0" },
    );
    assert.equal(h.app.check!.labCollection!.draft!.saliva_volume_ml, "1.0");
    await h.app.recordLabCollection(h.specimen());
    const checkId = h.app.check!.id,
      sampleId = h.app.check!.snapshot.sample.sample_id;
    assert.equal(h.app.check!.labCollection!.state, "pending_lab");
    assert.deepEqual(h.app.check!.snapshot.saliva, []);
    await h.app.saveCheck();
    assert.equal(h.app.check!.frozen, false);
    assert.equal(h.app.getSnapshot().route, "history");
    await assert.rejects(h.app.uploadCheck(), /draft/);
    assert.equal(h.app.getSnapshot().state!.queue.length, 0);
    // A failed serialized mutation is recovered by the next guarded local read/commit.
    await (h.app as any).commit((s: any) => s);
    await h.app.selectCheck(checkId);
    await h.app.refreshLabCollection();
    assert.equal(h.app.check!.labCollection!.state, "pending_lab");
    h.importReport();
    await h.app.refreshLabCollection();
    assert.equal(h.app.check!.labCollection!.state, "imported");
    assert.equal(h.app.check!.attempts.length, 2);
    assert.equal(h.app.check!.snapshot.sample.sample_id, sampleId);
    assert.equal(
      (h.app.check!.snapshot.saliva[0] as unknown as JsonObject).source,
      "reference_lab",
    );
    await h.app.saveCheck();
    assert.equal(h.app.check!.frozen, true);
    assert.equal(h.app.getSnapshot().state!.queue.length, 0);
    assert.equal(
      queueCheck(
        h.app.getSnapshot().state!,
        checkId,
        randomUUID,
        new Date().toISOString(),
      ).queue.length,
      1,
    );
  } finally {
    await h.close();
  }
});
test("unknown analysis cancellation preserves its exact body and key and never relabels the collected specimen", async () => {
  const h = await labAccount();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    await h.app.startLabCollection(currentInstruction(h.app, "saliva"));
    await h.app.recordLabCollection(h.specimen());
    const sample = clone(h.app.check!.snapshot.sample),
      attempt = clone(h.app.check!.attempts[0]);
    h.loseAbandonReply();
    await assert.rejects(h.app.abandonLabAnalysis(), (e: any) => e.retryable);
    const saved = clone(h.app.check!.labCollection!);
    await assert.rejects(
      h.app.abandonLabAnalysis("SPECIMEN_UNAVAILABLE"),
      (e: any) => e.code === "LAB_ABANDONMENT_INTENT_CHANGED",
    );
    await h.app.abandonLabAnalysis();
    const calls = h.service.calls.filter((call) =>
      call.path.endsWith("/abandon"),
    );
    assert.equal(calls.length, 2);
    assert.equal(calls[1]!.headers.get("Idempotency-Key"), saved.abandon_key);
    assert.deepEqual(calls[1]!.body, calls[0]!.body);
    assert.deepEqual(h.app.check!.snapshot.sample, sample);
    assert.deepEqual(h.app.check!.attempts[0], attempt);
    assert.equal(h.app.check!.labCollection!.state, "canceled");
  } finally {
    await h.close();
  }
});
test("refreshing analysis canceled on another device retains the original specimen and scoped abandonment proof", async () => {
  const h = await labAccount();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    await h.app.startLabCollection(currentInstruction(h.app, "saliva"));
    await h.app.recordLabCollection(h.specimen());
    const sample = clone(h.app.check!.snapshot.sample),
      attempt = clone(h.app.check!.attempts[0]);
    h.abandonElsewhere();
    await h.app.refreshLabCollection();
    assert.equal(h.app.check!.labCollection!.state, "canceled");
    assert.deepEqual(h.app.check!.snapshot.sample, sample);
    assert.deepEqual(h.app.check!.attempts[0], attempt);
    assert.equal(h.app.check!.collection_abandons!.length, 1);
    assert.deepEqual(h.app.check!.snapshot.saliva, []);
    await assert.rejects(h.app.refreshLabCollection(), /No active/);
    await h.app.saveCheck();
    assert.equal(h.app.check!.frozen, true);
  } finally {
    await h.close();
  }
});
test("reopening the owned workspace preserves the actual collecting form without restoring rest or invoking hardware", async () => {
  const h = await labAccount(),
    reopened = new AppController();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    await h.app.startLabCollection(currentInstruction(h.app, "saliva"));
    const checkId = h.app.check!.id,
      attemptId = h.app.check!.labCollection!.attempt_id;
    await h.app.saveLabCollectionDraft(checkId, attemptId, {
      saliva_volume_ml: "1.0",
      collector_lot: "UNSUBMITTED",
    });
    await reopened.initialize();
    await reopened.signIn();
    await reopened.selectCheck(checkId);
    assert.equal(reopened.check!.attempts[0]!.status, "started");
    assert.deepEqual(reopened.check!.labCollection!.draft, {
      saliva_volume_ml: "1.0",
      collector_lot: "UNSUBMITTED",
    });
    assert.equal(reopened.check!.labCollection!.state, "collecting");
    assert.equal(reopened.getSnapshot().activeTask, null);
    assert.equal(reopened.getSnapshot().activeEye, null);
    assert.equal(h.events.includes("hardware-acquire"), false);
  } finally {
    await reopened.dispose();
    await h.close();
  }
});
test("a changed submitted instruction envelope cannot reuse the original preparation or stop a newer scope", async () => {
  const h = await approvedAccount();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    await h.app.prepareParticipantCapture("cardiac");
    const epoch = h.app.epoch,
      intent = h.app.preparationGeneration,
      attempt = h.app.check!.attempts[0]!;
    const changed = { ...h.config, submitted_sha256: "f".repeat(64) };
    h.service.caps.channels.cardiac.configurations = [changed];
    await assert.rejects(
      h.app.captureReader("ppg", false, currentInstruction(h.app, "cardiac")),
      (e: any) => e.code === "PARTICIPANT_PROTOCOL_CHANGED",
    );
    assert.equal(h.events.includes("hardware-acquire"), false);
    await h.app.stopPreparedCapture(
      epoch,
      h.app.check!.id,
      intent,
      attempt.attempt_id,
    );
    assert.equal(h.app.check!.attempts[0]!.status, "started");
    await h.app.stopActive("USER_CANCELED");
    assert.equal(h.app.check!.attempts[0]!.status, "invalid");
  } finally {
    await h.close();
  }
});

test("unknown specimen receipt retries the immutable declaration and key; explicit analysis cancellation never erases collection", async () => {
  const h = await labAccount();
  try {
    await h.app.beginStudyCheck(h.study.study_id, h.config.protocol_id, true);
    await h.app.startLabCollection(currentInstruction(h.app, "saliva"));
    const body = h.specimen();
    h.loseReply();
    await assert.rejects(
      h.app.recordLabCollection(body),
      (e: any) => e.retryable,
    );
    const immutable = clone(h.app.check!.labCollection!);
    await h.app.recordLabCollection(body);
    const calls = h.service.calls.filter((call) =>
      call.path.endsWith("/collections"),
    );
    assert.equal(calls.length, 2);
    assert.equal(calls[0]!.headers.get("Idempotency-Key"), immutable.key);
    assert.deepEqual(calls[0]!.body, calls[1]!.body);
    const sample = clone(h.app.check!.snapshot.sample),
      attempt = clone(h.app.check!.attempts[0]!);
    await h.app.abandonLabAnalysis();
    assert.equal(h.app.check!.labCollection!.state, "canceled");
    assert.deepEqual(h.app.check!.snapshot.sample, sample);
    assert.deepEqual(h.app.check!.attempts[0], attempt);
    assert.deepEqual(h.app.check!.snapshot.saliva, []);
    assert.equal(h.app.check!.collection_abandons!.length, 1);
    h.importReport();
    await assert.rejects(h.app.refreshLabCollection(), /No active/);
    await h.app.saveCheck();
    assert.equal(h.app.check!.frozen, true);
  } finally {
    await h.close();
  }
});

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
    await app.captureReader("ppg", false, currentInstruction(app, "cardiac"));
    assert.deepEqual(events, [
      "register",
      "context",
      "started-attempt",
      "instruction-acknowledgment",
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
      app.captureReader("ecg", true, currentInstruction(app, "ecg")),
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
    await app.captureReader("ecg", true, currentInstruction(app, "ecg"));
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
      app.captureReader("ppg", false, currentInstruction(app, "cardiac")),
      /different reader or reboot/,
    );
    assert.equal(events.includes("hardware-acquire"), false);
    assert.equal(app.check!.attempts.length, 0);
  } finally {
    await close();
  }
});

test("scope-qualified preparation End stops the advanced capture token before a deferred server start reaches hardware", async () => {
  const { app, service, study, config, events, close } =
    await approvedAccount();
  try {
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    await app.prepareParticipantCapture("cardiac");
    const epoch = app.epoch,
      previousIntent = app.preparationGeneration,
      attemptId = app.check!.attempts[0]!.attempt_id;
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
    const pending = app.captureReader(
      "ppg",
      false,
      currentInstruction(app, "cardiac"),
    );
    const captureIntent = app.preparationGeneration;
    assert.notEqual(captureIntent, previousIntent);
    await entered.promise;
    const stopped = app.stopPreparedCapture(
      epoch,
      app.check!.id,
      captureIntent,
      attemptId,
    );
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

test("hypothetical breath contract configuration is selectable only strictly before its expiry", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const { app, study, config, close } = await approvedAccount();
  try {
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    // Selection contract only. This does not install a breath adapter, validate
    // a calibration, obtain a server grant or invoke an instrument.
    const caps = clone(app.getSnapshot().state!.capabilities)!;
    for (const key of Object.keys(caps.channels))
      caps.channels[key]!.available = false;
    const breath = {
      ...config,
      configuration_id: "fictional-breath-contract-only",
      software_adapter_id: "fictional-uninstalled-breath-contract",
      expires_at: "2026-10-11T12:00:01Z",
    };
    caps.channels.alcohol = {
      available: true,
      software_available: true,
      authorization_available: true,
      reason_codes: [],
      configurations: [breath],
    };
    const check = clone(app.check!);
    check.context.configuration_refs = [
      {
        id: breath.configuration_id,
        version: "v1",
        sha256: breath.configuration_hash,
        scope: "measurement_collection",
      },
    ];
    for (const [offset, selectable] of [
      [999, true],
      [1000, false],
      [1001, false],
    ] as const) {
      context.mock.timers.setTime(Date.parse("2026-10-11T12:00:00Z") + offset);
      assert.equal(
        configurationsFor(caps, study.study_id, config.protocol_id).length,
        selectable ? 1 : 0,
      );
      if (selectable)
        assert.equal(
          configurationFor(check, caps, "alcohol").configuration_id,
          "fictional-breath-contract-only",
        );
      else
        assert.throws(() => configurationFor(check, caps, "alcohol"), {
          code: "CAPTURE_CONFIGURATION_AMBIGUOUS",
        });
    }
    assert.equal(app.check!.alcohol, null);
  } finally {
    await close();
  }
});

test("fresh absent-breath-adapter capability overrides stale cached availability before any hardware invocation", async () => {
  const { app, study, config, service, events, close } =
    await approvedAccount();
  try {
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    // Deliberately stale cached input cannot override the refreshed server
    // inventory. Real software_supported() inventory is tested by the API suite.
    app.getSnapshot().state!.capabilities!.channels.alcohol = {
      available: true,
      authorization_available: true,
      software_available: true,
      reason_codes: [],
      configurations: [config],
    };
    service.caps.channels.alcohol = {
      available: false,
      authorization_available: true,
      software_available: false,
      reason_codes: ["HUMAN_ADAPTER_UNIMPLEMENTED"],
      configurations: [config],
    };
    await assert.rejects(app.captureReader("alcohol"), {
      code: "CAPTURE_UNAVAILABLE",
    });
    assert.equal(
      app.getSnapshot().state!.capabilities!.channels.alcohol!
        .software_available,
      false,
    );
    assert.deepEqual(
      events.filter((event) =>
        ["grant", "prepare-device-nonce", "hardware-acquire"].includes(event),
      ),
      [],
    );
    assert.equal(app.check!.attempts.length, 0);
    assert.equal(app.check!.alcohol, null);
  } finally {
    await close();
  }
});

test("a start-time registry dependency refusal after a hypothetical breath grant preserves its authoritative reason and never acquires concentration", async () => {
  const { app, study, config, service, events, close } =
    await approvedAccount();
  try {
    // Reuse the actual controller transport boundary with explicitly fictional
    // eligibility. No successful breath driver or calibration is supplied.
    service.caps.channels.alcohol = {
      available: true,
      authorization_available: true,
      software_available: true,
      reason_codes: [],
      configurations: [
        {
          ...config,
          participant_protocol: null,
          participant_protocol_sha256: null,
        },
      ],
    };
    await app.beginStudyCheck(study.study_id, config.protocol_id, true);
    const transport = globalThis.fetch;
    globalThis.fetch = async (input, init) => {
      const path = new URL(String(input)).pathname;
      if (path.endsWith("/capture-authorizations")) {
        const response = await transport(input, init),
          body = await response.json();
        body.participant_protocol_sha256 = null;
        return service.result(body, response.status);
      }
      if (path.endsWith("/start")) {
        events.push("authoritative-start-refusal");
        return service.result(
          { code: "APPROVED_REGISTRY_VERSION_REQUIRED", retryable: false },
          403,
        );
      }
      return transport(input, init);
    };
    await assert.rejects(app.captureReader("alcohol"), {
      code: "APPROVED_REGISTRY_VERSION_REQUIRED",
    });
    assert.equal(events.includes("grant"), true);
    assert.equal(events.includes("authoritative-start-refusal"), true);
    assert.equal(events.includes("hardware-acquire"), false);
    assert.equal(app.check!.alcohol!.value_mg_l, null);
    assert.equal(app.check!.alcohol!.qualifier, "invalid");
    assert.equal(app.check!.attempts[0]!.status, "invalid");
    // The generic real server code cannot honestly be called a calibration
    // diagnosis. Direct dependency expiry/recalibration belongs to API evidence.
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
