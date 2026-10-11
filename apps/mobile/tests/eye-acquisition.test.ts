import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import fixture from "../testfixtures/backend-optical-result.json";
import rawFixture from "../testfixtures/backend-raw-recordings.json";
import {
  clone,
  digest,
  digestBytes,
  digestText,
  utf8,
} from "../src/core/integrity";
import {
  projectNativeEye,
  verifyRetainedNativeEye,
} from "../src/core/eyeProjection";
import { verifyExportEvidence } from "../src/core/exportEvidence";
import type { EyeCaptureComplete } from "../modules/eye-capture";
import type { WorkspaceState } from "../src/core/types";
import { customerService, deferred } from "./support/customer";
require("./support/runtime.cjs");
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");
const identity = {
  runId: fixture.native_result.run_id,
  epoch: fixture.native_result.workspace_epoch,
  authorizationId: fixture.native_result.authorization_id,
  configurationId: fixture.configuration.configuration_id,
  configurationHash: fixture.configuration.sha256,
  material: fixture.configuration.material,
};

test("actual Python optical fixture projects bounded native evidence without inventing millimeters, physical onset or latency", () => {
  assert.deepEqual(
    projectNativeEye(fixture.native_result, identity),
    fixture.projection,
  );
  for (const mutate of [
    (v: any) => (v.run_id = randomUUID()),
    (v: any) => (v.workspace_epoch = "other-account"),
    (v: any) => (v.authorization_id = randomUUID()),
    (v: any) => (v.model_eligible = true),
    (v: any) => (v.physical_onset_verified = true),
    (v: any) => (v.features.total_frames = 9),
    (v: any) => (v.features.valid_frames = 100),
    (v: any) => (v.frame_events[1].sequence = 4),
    (v: any) => (v.frame_events[1].native_timestamp_ms = 900),
    (v: any) => (v.camera.output_rotation_degrees = 90),
    (v: any) => (v.features.baseline_diameter_mm = 3),
    (v: any) => (v.stimulus.physically_measured_at_ms = 1050),
  ]) {
    const changed = clone(fixture.native_result);
    mutate(changed);
    assert.throws(() => projectNativeEye(changed, identity));
  }
  const invalid = clone(fixture.native_result);
  invalid.status = "invalid";
  invalid.features.valid_frames = 0;
  const projection = projectNativeEye(invalid, identity);
  assert.equal(projection.status, "invalid");
  assert.equal(projection.baseline_diameter_mm, null);
  assert.equal(projection.relative_constriction, null);
  assert.equal(projection.latency_ms, null);
});
async function account() {
  const service = customerService(),
    previous = globalThis.fetch;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  (globalThis as any).__otgdUnitRuntime.eyeAvailable = true;
  const app = new AppController();
  await app.initialize();
  await app.signIn();
  const rawStatus = clone(rawFixture),
    text =
      "Fictional optical controller boundary; no physical phone or validation.";
  const study: any = {
    study_id: rawStatus.study_id,
    name: "Fictional optical study",
    invitation_id: randomUUID(),
    document_version: "v1",
    document_text: text,
    document_sha256: digestText(text),
  };
  study.consent = {
    study_id: study.study_id,
    invitation_id: study.invitation_id,
    document_version: "v1",
    document_sha256: study.document_sha256,
    state: "active",
    accepted: true,
    consent_record_id: rawStatus.consent_record_id,
  };
  const config = {
    study_id: study.study_id,
    protocol_id: "fictional-optical-protocol",
    configuration_id: fixture.configuration.configuration_id,
    configuration_hash: fixture.configuration.sha256,
    configuration_version: "v1",
    submitted_sha256: "a".repeat(64),
    expires_at: new Date(Date.now() + 60_000).toISOString(),
    supported_phone_models: fixture.configuration.supported_phone_models,
    supported_os_versions: fixture.configuration.supported_os_versions,
    supported_native_builds: fixture.configuration.supported_native_builds,
    software_adapter_id: "optical_roi_v1",
  };
  service.caps.channels.eyes = {
    available: true,
    authorization_available: true,
    software_available: true,
    reason_codes: [],
    configurations: [config],
  };
  service.overrides.set("/v1/me/studies", () =>
    service.result({ items: [study] }),
  );
  service.overrides.set(`/v1/studies/${study.study_id}/raw-recordings`, () =>
    service.result(rawStatus),
  );
  const old = service.fetcher,
    authorizationId = randomUUID();
  let granted: any;
  globalThis.fetch = async (input, init) => {
    const path = new URL(String(input)).pathname;
    if (path === "/v1/sessions")
      service.overrides.set("POST " + path, () =>
        service.result({ revision: 0 }, 201, { ETag: '"0"' }),
      );
    if (path.endsWith("/context") || path.includes("/attempts/"))
      service.overrides.set("PUT " + path, (call) =>
        service.result({ revision: 1, sha256: digest(call.body) }),
      );
    if (path.endsWith("/capture-authorizations"))
      service.overrides.set("POST " + path, (call) => {
        const policy = rawStatus.policy,
          permission = call.body.raw_recording_kind
            ? {
                record: true,
                upload: true,
                receipt_id: rawStatus.receipt_id,
                policy_id: policy.policy_id,
                policy_version: policy.version,
                policy_sha256: policy.sha256,
                raw_notice_version: policy.raw_notice.version,
                raw_notice_sha256: policy.raw_notice.sha256,
              }
            : null;
        granted = {
          ...call.body,
          authorization_id: authorizationId,
          session_id: app.check!.id,
          state: "issued",
          expires_at: new Date(Date.now() + 60_000).toISOString(),
          expires_epoch: (Date.now() + 60_000) / 1000,
          configuration_max_duration_ms: 1000,
          supported_phone_models: config.supported_phone_models,
          supported_os_versions: config.supported_os_versions,
          supported_native_builds: config.supported_native_builds,
          software_adapter_id: config.software_adapter_id,
          configuration_submitted_sha256: config.submitted_sha256,
          configuration_version: config.configuration_version,
          capture_context_sha256: digest(app.check!.context),
          configuration_material: fixture.configuration.material,
          raw_recording_permission: permission,
        };
        return service.result(granted);
      });
    if (path.endsWith("/start"))
      service.overrides.set("POST " + path, (call) => {
        assert.equal(call.body.device_boot_id, null);
        assert.equal(call.body.device_nonce, null);
        return service.result({
          authorization_id: authorizationId,
          attempt_id: call.body.attempt_id,
          device_boot_id: null,
          state: "started",
          server_started_at: new Date().toISOString(),
          raw_recording_permission: granted.raw_recording_permission,
          server_start: {
            domain: "OTGD capture grant v1\u0000",
            grant: {
              authorization_id: authorizationId,
              attempt_id: call.body.attempt_id,
              session_id: app.check!.id,
              configuration_hash: config.configuration_hash,
              configuration_submitted_sha256: config.submitted_sha256,
              capture_context_sha256: digest(app.check!.context),
              boot_id: null,
              raw_recording_permission: granted.raw_recording_permission,
            },
            signature: "TEST_ONLY_NOT_A_SIGNATURE",
          },
        });
      });
    return old(input, init);
  };
  await app.beginStudyCheck(study.study_id, config.protocol_id, true);
  return {
    app,
    service,
    study,
    rawStatus,
    close: async () => {
      await app.auth.clear();
      await app.dispose();
      globalThis.fetch = previous;
      (globalThis as any).__otgdUnitRuntime.eyeAvailable = false;
    },
  };
}
function completion(
  app: InstanceType<typeof AppController>,
): EyeCaptureComplete {
  const active = app.getSnapshot().activeEye!,
    native = clone(fixture.native_result);
  native.run_id = active.runId;
  native.workspace_epoch = active.epoch;
  native.authorization_id = active.options.authorization_id;
  native.started_at = new Date(Date.now() + 1).toISOString();
  native.ended_at = new Date(Date.now() + 1001).toISOString();
  return {
    run_id: active.runId,
    workspace_epoch: active.epoch,
    authorization_id: active.options.authorization_id,
    status: "valid",
    native_result: native,
    raw_recording: null,
  };
}
test("feature-only optical Start follows context, attempt and fresh grant; native completion saves locally with a separate actual acquisition clock", async () => {
  const { app, service, close } = await account();
  try {
    await app.startEyeCapture(false);
    const active = app.getSnapshot().activeEye!;
    assert.equal(active.options.raw_recording_permission, null);
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    const result = completion(app);
    await app.completeEyeCapture(result);
    const attempt = app.check!.attempts[0]!;
    assert.equal(attempt.started_at, result.native_result!.started_at);
    assert.equal(
      attempt.component_metadata.armed_at,
      app.check!.acquisition!.attempts[attempt.attempt_id]!.started_body
        .started_at,
    );
    assert.equal(app.check!.snapshot.eyes.latency_ms, null);
    assert.equal(app.getSnapshot().activeEye, null);
    await app.saveCheck();
    verifyExportEvidence(app.check!);
    verifyRetainedNativeEye(
      result.native_result,
      app.check!.snapshot.eyes,
      attempt,
    );
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    assert.equal(
      service.calls.some((call) => call.path === "/v1/artifact-uploads"),
      false,
    );
  } finally {
    await close();
  }
});
test("End camera dispatches native shutdown and running=false before delayed evidence persistence, and a committed completion survives cancel", async () => {
  const { app, close } = await account();
  try {
    await app.startEyeCapture(false);
    const active = app.getSnapshot().activeEye!,
      result = completion(app),
      entered = deferred<void>(),
      resume = deferred<void>();
    let stops = 0;
    app.eyeView = {
      cancel: async () => {
        stops++;
        return result;
      },
      releaseRaw: async () => ({ released: true }),
    };
    const original = (app as any).store,
      save = original.save.bind(original);
    original.save = async (state: WorkspaceState) => {
      entered.resolve();
      await resume.promise;
      await save(state);
    };
    const stopping = app.stopActive("USER_CANCELED");
    await entered.promise;
    assert.equal(stops, 1);
    assert.equal(app.getSnapshot().activeEye!.stopping, true);
    resume.resolve();
    await stopping;
    assert.equal(app.getSnapshot().activeEye, null);
    assert.equal(app.check!.attempts[0]!.status, "valid");
    assert.equal(app.check!.attempts[0]!.record_id, active.runId);
  } finally {
    await close();
  }
});
test("camera failure before the first frame preserves its original reason and arming metadata without inventing acquired clocks", async () => {
  const { app, close } = await account();
  try {
    await app.startEyeCapture(false);
    const active = app.getSnapshot().activeEye!;
    const terminal: EyeCaptureComplete = {
      run_id: active.runId,
      workspace_epoch: active.epoch,
      authorization_id: active.options.authorization_id,
      status: "invalid",
      reason: "CAMERA_START_FAILED",
      native_result: null,
      raw_recording: null,
    };
    await assert.rejects(
      app.completeEyeCapture({ ...terminal, status: "valid" }),
      /without acquired native evidence/,
    );
    await app.completeEyeCapture(terminal);
    const attempt = app.check!.attempts[0]!;
    assert.equal(attempt.started_at, null);
    assert.equal(attempt.ended_at, null);
    assert.deepEqual(attempt.quality_flags, ["CAMERA_START_FAILED"]);
    assert.equal(
      attempt.component_metadata.armed_at,
      app.check!.acquisition!.attempts[attempt.attempt_id]!.started_body
        .started_at,
    );
    assert.equal(app.check!.snapshot.eyes.started_at, null);
    await app.saveCheck();
    verifyExportEvidence(app.check!);
  } finally {
    await close();
  }
});
test("optional ROI handoff commits encrypted bytes plus exact receipt atomically, releases native RAM, and never queues upload", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const { app, study, close } = await account();
  try {
    await app.refreshRawRecordings(study.study_id);
    const store = (app as any).store,
      saved: Uint8Array[] = [];
    let released = 0;
    store.saveWithRaw = async (
      state: WorkspaceState,
      _id: string,
      bytes: Uint8Array,
      current: () => boolean,
    ) => {
      assert.equal(current(), true);
      saved.push(bytes);
      await store.save(state);
    };
    store.deleteRaw = async () => {};
    await app.startEyeCapture(true);
    app.eyeView = {
      cancel: async () => completion(app),
      releaseRaw: async () => {
        released++;
        return { released: true };
      },
    };
    const result = completion(app);
    result.raw_recording = clone(
      fixture.raw_recording,
    ) as EyeCaptureComplete["raw_recording"];
    await app.completeEyeCapture(result);
    assert.equal(released, 1);
    assert.equal(
      saved[0]!.every((byte) => byte === 0),
      true,
    );
    const raw = app.getSnapshot().state!.rawArtifacts![0]!;
    assert.equal(raw.state, "local");
    assert.equal(
      raw.permission.receipt_id,
      app.getSnapshot().state!.rawRecordingStatuses[study.study_id]!.receipt_id,
    );
    assert.equal(app.getSnapshot().state!.queue.length, 0);
  } finally {
    await close();
  }
});
