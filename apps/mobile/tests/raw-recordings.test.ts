import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import fixture from "../testfixtures/backend-raw-recordings.json";
import { clone, digest } from "../src/core/integrity";
import {
  assertRawChoicesAllowed,
  parseRawChoices,
  parseRawRecordingStatus,
  rawChoicesOff,
} from "../src/core/rawRecordings";

test.beforeEach((context) => {
  if (!("mock" in context)) throw Error("Expected a test clock context");
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
});

test("actual Python raw_status envelope verifies complete policy, exact UTF-8 notice, separate receipt and upload/retention states", () => {
  const status = parseRawRecordingStatus(fixture, fixture.study_id);
  assert.equal(status.policy!.retention_basis, "first_owned_acquisition_start");
  assert.equal(status.policy!.purpose, status.policy!.content.purpose_text);
  assert.equal(status.artifacts[0]!.state, "retained");
  assert.equal(status.artifacts[0]!.upload_state, "quarantine");
  assert.deepEqual(status.preference_receipt!.choices, status.choices);
  assert.equal(status.has_more_artifacts, false);
  assertRawChoicesAllowed(
    status,
    status.choices,
    [],
    Date.parse("2026-10-11T01:00:00Z"),
  );
});

test("raw policy or notice substitution, wrong owner, unknown data and inconsistent immutable receipt fail closed", () => {
  for (const alter of [
    (f: any) => (f.study_id = "another-study"),
    (f: any) => (f.policy.purpose = "another purpose"),
    (f: any) => (f.policy.content.max_retention_days = 365),
    (f: any) => (f.policy.raw_notice.content += "changed"),
    (f: any) => (f.policy.raw_notice.version = "changed"),
    (f: any) => (f.policy.sha256 = "not-a-sha"),
    (f: any) => (f.policy.expires_at = "2026-11-01T00:00:00Z"),
    (f: any) => (f.policy.retention_basis = "upload_time"),
    (f: any) => (f.policy.unrecognized = "permission"),
    (f: any) => (f.preference_receipt.consent_record_id = randomUUID()),
    (f: any) => (f.preference_receipt.policy_version = "another"),
    (f: any) => (f.receipt_id = null),
    (f: any) => (f.preference_receipt = null),
    (f: any) =>
      (f.preference_receipt.choices.eye_video = {
        record: false,
        upload: false,
      }),
    (f: any) => (f.has_more_artifacts = true),
    (f: any) => (f.artifacts[0].upload_state = "invented_complete"),
    (f: any) => (f.artifacts[0].state = "invented_deleted"),
    (f: any) => (f.artifacts[0].artifact_kind = "source_lab_report"),
    (f: any) =>
      (f.revocations = [
        {
          receipt_id: randomUUID(),
          artifact_kinds: ["eye_video"],
          accepted_at: "yesterday",
          state: "completed",
        },
      ]),
  ]) {
    const changed = clone(fixture);
    alter(changed);
    assert.throws(() => parseRawRecordingStatus(changed, fixture.study_id));
  }
});

test("default off, local-only opt-in, upload dependency, policy expiry and pending stop fences remain distinct", () => {
  const status = parseRawRecordingStatus(fixture, fixture.study_id),
    off = rawChoicesOff();
  assert.deepEqual(parseRawChoices(off), off);
  assert.throws(
    () =>
      parseRawChoices({ ...off, eye_video: { record: false, upload: true } }),
    /requires/,
  );
  assert.throws(
    () =>
      parseRawChoices({
        ...off,
        source_lab_report: { record: true, upload: true },
      }),
    /Unsupported/,
  );
  assert.throws(() =>
    parseRawChoices({ ...off, eye_video: { record: "yes", upload: false } }),
  );
  assertRawChoicesAllowed(
    status,
    { ...off, eye_video: { record: true, upload: false } },
    [],
    Date.parse("2026-10-11T00:00:00Z"),
  );
  assert.throws(
    () =>
      assertRawChoicesAllowed(
        status,
        status.choices,
        ["eye_video"],
        Date.parse("2026-10-11T00:00:00Z"),
      ),
    /revocation/,
  );
  assert.throws(
    () =>
      assertRawChoicesAllowed(
        status,
        status.choices,
        [],
        Date.parse("2026-10-22T00:00:00Z"),
      ),
    /current approved/,
  );
  status.availability.eye_video.upload_allowed = false;
  assert.throws(() =>
    assertRawChoicesAllowed(
      status,
      status.choices,
      [],
      Date.parse("2026-10-11T00:00:00Z"),
    ),
  );
  const absent: any = clone(fixture);
  absent.policy = null;
  assert.throws(() => parseRawRecordingStatus(absent, fixture.study_id));
});

test("separate revocation preserves original granted receipt while effective choices turn off and cleanup remains pending", () => {
  const changed: any = clone(fixture);
  changed.choices = rawChoicesOff();
  changed.artifacts[0]!.state = "cleanup_pending";
  changed.artifacts[0]!.upload_state = "cleanup_pending";
  changed.revocations = [
    {
      receipt_id: randomUUID(),
      artifact_kinds: ["eye_video"],
      accepted_at: "2026-10-11T01:00:00Z",
      state: "cleanup_pending",
    },
  ] as any;
  (changed as any).accepted_receipt_id = changed.revocations[0]!.receipt_id;
  const status = parseRawRecordingStatus(changed, fixture.study_id);
  assert.equal(status.choices.eye_video.record, false);
  assert.equal(status.preference_receipt!.choices.eye_video.record, true);
  assert.equal(status.revocations[0]!.state, "cleanup_pending");
  assert.equal(status.artifacts[0]!.cleanup_completed_at, null);
  assert.equal(
    digest(status.preference_receipt),
    digest(fixture.preference_receipt),
  );
});

require("./support/runtime.cjs");
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");
import { customerService, deferred } from "./support/customer";
async function account() {
  const service = customerService(),
    previous = globalThis.fetch;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  const app = new AppController();
  await app.initialize();
  await app.signIn();
  service.overrides.set(`/v1/studies/${fixture.study_id}/raw-recordings`, () =>
    service.result(fixture),
  );
  return {
    app,
    service,
    close: async () => {
      await app.auth.clear();
      await app.dispose();
      globalThis.fetch = previous;
    },
  };
}

test("lost optional-choice receipt replays exact durable body, original acknowledgment and idempotency key", async () => {
  const { app, service, close } = await account();
  try {
    await app.openRawRecordings(fixture.study_id);
    let failed = true;
    let accepted: any;
    service.overrides.set(
      `POST /v1/studies/${fixture.study_id}/raw-recording-preferences`,
      (call) => {
        const queued = app
          .getSnapshot()
          .state!.queue.find((q) => q.kind === "raw_preference")!;
        assert.deepEqual(queued.body.payload, call.body);
        accepted = clone(fixture);
        accepted.receipt_id = randomUUID();
        accepted.choices = call.body.choices;
        accepted.preference_receipt = {
          ...call.body,
          receipt_id: accepted.receipt_id,
          accepted_at: new Date().toISOString(),
        };
        if (failed) {
          failed = false;
          throw Error("accepted receipt lost");
        }
        return service.result(accepted);
      },
    );
    await app.saveRawRecordingChoices(fixture.study_id, rawChoicesOff());
    const intent = clone(
      app.getSnapshot().state!.queue.find((q) => q.kind === "raw_preference")!,
    );
    assert.equal(intent.state, "retry_wait");
    await app.saveRawRecordingChoices(fixture.study_id, rawChoicesOff());
    const calls = service.calls.filter((call) =>
      call.path.endsWith("raw-recording-preferences"),
    );
    assert.deepEqual(calls[0]!.body, calls[1]!.body);
    assert.equal(
      calls[0]!.headers.get("Idempotency-Key"),
      calls[1]!.headers.get("Idempotency-Key"),
    );
    assert.equal(
      app.getSnapshot().state!.queue.find((q) => q.id === intent.id)!.state,
      "synced",
    );
    assert.equal(
      app.getSnapshot().state!.rawRecordingStatuses[fixture.study_id]!
        .receipt_id,
      accepted.receipt_id,
    );
  } finally {
    await close();
  }
});

test("offline stop intent survives clearing local checks, never revives permission and accepts only actual cleanup receipts", async () => {
  const { app, service, close } = await account();
  try {
    await app.openRawRecordings(fixture.study_id);
    service.overrides.set(
      `POST /v1/studies/${fixture.study_id}/raw-recording-revocations`,
      () => {
        throw Error("offline");
      },
    );
    await app.revokeRawRecordings(fixture.study_id, ["eye_video"]);
    const intent = clone(
      app.getSnapshot().state!.queue.find((q) => q.kind === "raw_revocation")!,
    );
    assert.equal(intent.state, "retry_wait");
    assert.deepEqual(
      app.getSnapshot().state!.rawRecordingFences[fixture.study_id],
      ["eye_video"],
    );
    await app.clearLocal();
    assert.equal(app.getSnapshot().state!.queue[0]!.id, intent.id);
    await app.refreshRawRecordings(fixture.study_id);
    await assert.rejects(
      app.saveRawRecordingChoices(fixture.study_id, fixture.choices),
      /revocation/,
    );
    const stopped: any = clone(fixture);
    stopped.choices = rawChoicesOff();
    stopped.artifacts = [];
    stopped.accepted_receipt_id = randomUUID();
    stopped.revocations = [
      {
        receipt_id: stopped.accepted_receipt_id,
        artifact_kinds: ["eye_video"],
        accepted_at: new Date().toISOString(),
        state: "completed",
      },
    ];
    service.overrides.set(
      `POST /v1/studies/${fixture.study_id}/raw-recording-revocations`,
      () => service.result(stopped),
    );
    await app.sync.run(intent.id, true);
    assert.equal(
      app.getSnapshot().state!.queue.find((q) => q.id === intent.id)!.state,
      "synced",
    );
    // Until a fresh reconciled status is read, local stop remains conservative.
    assert.deepEqual(
      app.getSnapshot().state!.rawRecordingFences[fixture.study_id],
      ["eye_video"],
    );
    service.overrides.set(
      `/v1/studies/${fixture.study_id}/raw-recordings`,
      () => service.result(stopped),
    );
    await app.refreshRawRecordings(fixture.study_id);
    assert.deepEqual(
      app.getSnapshot().state!.rawRecordingFences[fixture.study_id],
      [],
    );
  } finally {
    await close();
  }
});

test("revocation fences an in-flight preference receipt before any late reply can mark it accepted", async () => {
  const { app, service, close } = await account();
  try {
    await app.openRawRecordings(fixture.study_id);
    const entered = deferred<void>(),
      reply = deferred<Response>();
    service.overrides.set(
      `POST /v1/studies/${fixture.study_id}/raw-recording-preferences`,
      () => {
        entered.resolve();
        return reply.promise;
      },
    );
    service.overrides.set(
      `POST /v1/studies/${fixture.study_id}/raw-recording-revocations`,
      () => {
        throw Error("offline");
      },
    );
    const pending = app.run(() =>
      app.saveRawRecordingChoices(fixture.study_id, fixture.choices),
    );
    await entered.promise;
    assert.equal(app.getSnapshot().busy, true);
    await app.runPrivacy(() =>
      app.revokeRawRecordings(fixture.study_id, ["eye_video"]),
    );
    await pending;
    reply.resolve(service.result(fixture));
    await new Promise<void>((resolve) => setImmediate(resolve));
    const state = app.getSnapshot().state!;
    assert.equal(
      state.queue.find((q) => q.kind === "raw_preference")!.state,
      "blocked",
    );
    assert.equal(
      state.queue.find((q) => q.kind === "raw_preference")!.error,
      "RAW_REVOCATION_PENDING",
    );
    assert.deepEqual(state.rawRecordingFences[fixture.study_id], ["eye_video"]);
  } finally {
    await close();
  }
});

test("an older completed revocation cannot clear a newer accepted cleanup-pending stop fence", async () => {
  const { app, service, close } = await account();
  try {
    await app.openRawRecordings(fixture.study_id);
    const current: any = clone(fixture);
    current.choices = rawChoicesOff();
    current.accepted_receipt_id = randomUUID();
    current.revocations = [
      {
        receipt_id: current.accepted_receipt_id,
        artifact_kinds: ["eye_video"],
        accepted_at: new Date().toISOString(),
        state: "cleanup_pending",
      },
      {
        receipt_id: randomUUID(),
        artifact_kinds: ["eye_video"],
        accepted_at: fixture.preference_receipt.accepted_at,
        state: "completed",
      },
    ];
    service.overrides.set(
      `POST /v1/studies/${fixture.study_id}/raw-recording-revocations`,
      () => service.result(current),
    );
    await app.revokeRawRecordings(fixture.study_id, ["eye_video"]);
    assert.equal(
      app.getSnapshot().state!.queue.find((q) => q.kind === "raw_revocation")!
        .state,
      "synced",
    );
    service.overrides.set(
      `/v1/studies/${fixture.study_id}/raw-recordings`,
      () => service.result(current),
    );
    await app.refreshRawRecordings(fixture.study_id);
    assert.deepEqual(
      app.getSnapshot().state!.rawRecordingFences[fixture.study_id],
      ["eye_video"],
    );
    await assert.rejects(
      app.saveRawRecordingChoices(fixture.study_id, fixture.choices),
      /revocation/,
    );
  } finally {
    await close();
  }
});
