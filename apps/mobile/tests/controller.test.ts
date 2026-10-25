import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");

test("guest notice, confirmed Start check, immutable local Save and linked replacement never request account upload", async () => {
  const previous = globalThis.fetch;
  let requests = 0;
  globalThis.fetch = async () => {
    requests++;
    throw Error("offline fixture");
  };
  const app = new AppController();
  try {
    await app.initialize();
    await app.enterDemo();
    assert.equal(app.getSnapshot().route, "notice");
    await app.acknowledgeNotice();
    assert.equal(app.getSnapshot().route, "home");
    await assert.rejects(() => app.beginCheck("guest_demo", false), /confirm/i);
    await app.beginCheck("guest_demo", true);
    const first = app.check!.id;
    await app.simulate("saliva");
    await app.simulate("eyes");
    await app.simulate("cardiac");
    await app.saveCheck();
    assert.equal(app.check!.frozen, true);
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    assert.equal(app.check!.snapshot.created_at, app.check!.snapshot.target_at);
    await assert.rejects(() => app.uploadCheck(), /guest|sign/i);
    await app.prepareReplacement(first);
    await app.beginCheck("guest_demo", true);
    assert.notEqual(app.check!.id, first);
    assert.equal(app.check!.snapshot.supersedes_session_id, first);
    assert.equal(app.check!.attempts.length, 0);
    await app.discardDraft();
    assert.equal(app.check, null);
    assert.equal(app.getSnapshot().route, "home");
    assert.equal(requests, 1);
  } finally {
    await app.dispose();
    globalThis.fetch = previous;
  }
});

import { customerService, deferred } from "./support/customer";
import { clone, digestText } from "../src/core/integrity";
import nativeFixture from "../modules/reaction-task/fixtures/native-result-valid-contract-fixture.json";
import { randomUUID } from "node:crypto";
import type { NativeTaskResult } from "../modules/reaction-task/types";
const unit = () => (globalThis as any).__otgdUnitRuntime;
async function account() {
  const service = customerService(),
    previous = globalThis.fetch;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  const app = new AppController();
  await app.initialize();
  await app.signIn();
  return {
    app,
    service,
    close: async () => {
      await app.auth.clear();
      await app.dispose();
      globalThis.fetch = previous;
      unit().available = false;
      unit().prompt = async (request: any) => ({
        type: "success",
        params: { state: request.state, code: "one-time-code" },
      });
    },
  };
}

test("sign-out records the API receipt before provider revocation and clears local identity immediately", async () => {
  const { app, service, close } = await account();
  const order: string[] = [];
  const entered = deferred<void>(),
    release = deferred<Response>();
  try {
    service.overrides.set("/v1/auth/logout", () => {
      order.push("api");
      entered.resolve();
      return release.promise;
    });
    service.overrides.set("/oauth2/revoke", () => {
      order.push("provider");
      return service.result({});
    });
    const pending = app.signOut(false);
    await entered.promise;
    assert.equal(app.getSnapshot().identity, null);
    assert.equal(await app.auth.accessToken(), null);
    assert.deepEqual(order, ["api"]);
    release.resolve(
      service.result({ state: "accepted", remote_family_revoked: true }),
    );
    await pending;
    assert.deepEqual(order, ["api", "provider"]);
  } finally {
    release.resolve(service.result({}));
    await close();
  }
});

test("a failed API logout still revokes the captured provider family and reports the unconfirmed receipt", async () => {
  const { app, service, close } = await account();
  const order: string[] = [];
  const providerCalls = unit().providerCalls.length;
  try {
    service.overrides.set("/v1/auth/logout", () => {
      order.push("api");
      return service.result({ code: "UNAVAILABLE" }, 503);
    });
    service.overrides.set("/oauth2/revoke", (call) => {
      order.push("provider");
      assert.equal(call.body.token, "unit-refresh");
      return service.result({});
    });
    await app.signOut(false);
    assert.deepEqual(order, ["api", "provider"]);
    assert.equal(app.getSnapshot().identity, null);
    assert.match(app.getSnapshot().message!, /not confirmed/);
    assert.equal(unit().providerCalls.length, providerCalls);
  } finally {
    await close();
  }
});

test("sign-out without retained credentials sends no fabricated API or provider revocation request", async () => {
  const { app, service, close } = await account();
  try {
    await app.auth.clear();
    const before = service.calls.length;
    await app.signOut(false);
    assert.equal(
      service.calls
        .slice(before)
        .filter((call) =>
          ["/v1/auth/logout", "/oauth2/revoke"].includes(call.path),
        ).length,
      0,
    );
    assert.equal(app.getSnapshot().identity, null);
    assert.match(app.getSnapshot().message!, /not confirmed/);
  } finally {
    await close();
  }
});

test("a replacement login during local sign-out still revokes only the captured old family without old UI work", async () => {
  const { app, service, close } = await account();
  const clear = app.auth.clear.bind(app.auth),
    entered = deferred<void>(),
    release = deferred<void>();
  const providerCalls = unit().providerCalls.length;
  try {
    app.auth.clear = async () => {
      await clear();
      entered.resolve();
      await release.promise;
    };
    const pending = app.signOut(false);
    await entered.promise;
    service.overrides.set("/oauth2/token", () =>
      service.result({
        access_token: "new-access",
        refresh_token: "new-refresh",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    service.caps.account_ref = randomUUID();
    await app.signIn();
    const next = app.getSnapshot();
    release.resolve();
    await pending;
    assert.equal(
      app.getSnapshot().identity?.accountRef,
      service.caps.account_ref,
    );
    assert.equal(app.getSnapshot().route, next.route);
    assert.equal(app.getSnapshot().message, next.message);
    assert.equal(unit().providerCalls.length, providerCalls);
    assert.equal(
      service.calls.filter((call) => call.path === "/v1/auth/logout").length,
      0,
    );
    const revocations = service.calls.filter(
      (call) => call.path === "/oauth2/revoke",
    );
    assert.equal(revocations.length, 1);
    assert.equal(revocations[0]!.body.token, "unit-refresh");
    assert.equal(await app.auth.accessToken(), "new-access");
  } finally {
    release.resolve();
    app.auth.clear = clear;
    await close();
  }
});

test("provider HTTP failure after an accepted API logout keeps sign-out local and its warning truthful", async () => {
  const { app, service, close } = await account();
  const providerCalls = unit().providerCalls.length;
  try {
    service.overrides.set("/oauth2/revoke", () =>
      service.result({ error: "unavailable" }, 503),
    );
    await app.signOut(false);
    assert.equal(app.getSnapshot().identity, null);
    assert.match(app.getSnapshot().message!, /not confirmed/);
    assert.equal(unit().providerCalls.length, providerCalls);
    assert.deepEqual(
      service.calls
        .filter((call) =>
          ["/v1/auth/logout", "/oauth2/revoke"].includes(call.path),
        )
        .map((call) => call.path),
      ["/v1/auth/logout", "/oauth2/revoke"],
    );
  } finally {
    await close();
  }
});

test("a delayed old-account logout cannot open provider logout or replace the new-account screen", async () => {
  const { app, service, close } = await account();
  try {
    const entered = deferred<void>(),
      receipt = deferred<Response>();
    service.overrides.set("/v1/auth/logout", () => {
      entered.resolve();
      return receipt.promise;
    });
    const providerCalls = unit().providerCalls.length;
    const signOut = app.signOut(false);
    await entered.promise;
    assert.equal(app.getSnapshot().identity, null);
    assert.equal(
      service.calls.filter((call) => call.path === "/oauth2/revoke").length,
      0,
    );
    service.overrides.set("/oauth2/token", () =>
      service.result({
        access_token: "replacement-access",
        refresh_token: "replacement-refresh",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    service.caps.account_ref = randomUUID();
    await app.signIn();
    const next = app.getSnapshot();
    receipt.resolve(service.result({ state: "token_family_revoked" }));
    await signOut;
    assert.equal(
      app.getSnapshot().identity?.accountRef,
      service.caps.account_ref,
    );
    assert.equal(app.getSnapshot().route, next.route);
    assert.equal(app.getSnapshot().message, next.message);
    assert.equal(unit().providerCalls.length, providerCalls);
    assert.equal(
      service.calls.find((call) => call.path === "/oauth2/revoke")!.body.token,
      "unit-refresh",
    );
    assert.equal(await app.auth.accessToken(), "replacement-access");
  } finally {
    await close();
  }
});

test("explicit study consent is durable before upload and a lost receipt retries the original timestamp and request identity", async () => {
  const { app, service, close } = await account();
  try {
    const text = "Fictional approved study information for the unit boundary.";
    const study = {
      study_id: "unit-study",
      invitation_id: randomUUID(),
      document_version: "v1",
      document_text: text,
      document_sha256: digestText(text),
      consent: null,
    };
    let receipt: any = null,
      failed = true;
    service.overrides.set("/v1/me/studies", () =>
      service.result({ items: [{ ...study, consent: receipt }] }),
    );
    service.overrides.set("POST /v1/studies/unit-study/consents", (call) => {
      const durable = app
        .getSnapshot()
        .state!.queue.find((q) => q.kind === "consent")!;
      assert.deepEqual(durable.body.payload, call.body);
      assert.equal(durable.keys.request, call.headers.get("Idempotency-Key"));
      receipt = {
        ...call.body,
        study_id: study.study_id,
        consent_record_id: randomUUID(),
        state: "active",
        accepted_at: new Date().toISOString(),
      };
      if (failed) {
        failed = false;
        throw Error("accepted response lost");
      }
      return service.result(receipt);
    });
    await app.refreshStudies();
    const before = new Date().toISOString();
    await app.consent(study);
    const queued = clone(
      app.getSnapshot().state!.queue.find((q) => q.kind === "consent")!,
    );
    assert.equal(queued.state, "retry_wait");
    assert.match(app.getSnapshot().message!, /not confirmed/i);
    assert.equal((queued.body.payload as any).accepted, true);
    assert.ok((queued.body.payload as any).acknowledged_at >= before);
    assert.equal(
      (queued.body.payload as any).document_sha256,
      study.document_sha256,
    );
    await app.consent(study);
    const calls = service.calls.filter(
      (call) => call.path === "/v1/studies/unit-study/consents",
    );
    assert.equal(calls.length, 2);
    assert.deepEqual(calls[1]!.body, calls[0]!.body);
    assert.equal(
      calls[1]!.headers.get("Idempotency-Key"),
      calls[0]!.headers.get("Idempotency-Key"),
    );
    assert.equal(
      app.getSnapshot().state!.queue.find((q) => q.id === queued.id)!.state,
      "synced",
    );
    assert.equal(
      app.getSnapshot().state!.queue.filter((q) => q.kind === "consent").length,
      1,
    );
    assert.equal(
      (app.getSnapshot().state!.studies[0]!.consent as any).acknowledged_at,
      calls[0]!.body.acknowledged_at,
    );
    assert.match(app.getSnapshot().message!, /Consent recorded/);
  } finally {
    await close();
  }
});

test("a consent receipt for another document or timestamp is never accepted as research authorization", async () => {
  const { app, service, close } = await account();
  try {
    const text = "Fictional approved study document.";
    const study = {
      study_id: "unit-study",
      invitation_id: randomUUID(),
      document_version: "v1",
      document_text: text,
      document_sha256: digestText(text),
      consent: null,
    };
    await app.commit((state) => ({ ...state, studies: [study] }));
    service.overrides.set("POST /v1/studies/unit-study/consents", (call) =>
      service.result({
        ...call.body,
        study_id: study.study_id,
        document_sha256: "0".repeat(64),
        consent_record_id: randomUUID(),
        state: "active",
        accepted_at: new Date().toISOString(),
      }),
    );
    await app.consent(study);
    const queued = app
      .getSnapshot()
      .state!.queue.find((q) => q.kind === "consent")!;
    assert.equal(queued.state, "blocked");
    assert.match(queued.error!, /exact confirmed/);
    assert.equal(app.getSnapshot().state!.studies[0]!.consent, null);
    await app.consent(study);
    assert.equal(
      service.calls.filter(
        (call) => call.path === "/v1/studies/unit-study/consents",
      ).length,
      1,
    );
    assert.match(app.getSnapshot().message!, /not confirmed/i);
  } finally {
    await close();
  }
});

test("maintenance pauses queued consent and withdrawal prevents its later automatic transmission", async () => {
  const { app, service, close } = await account();
  try {
    const text = "Fictional study document.";
    const study = {
      study_id: "unit-study",
      invitation_id: randomUUID(),
      document_version: "v1",
      document_text: text,
      document_sha256: digestText(text),
      consent: null,
    };
    await app.commit((state) => ({ ...state, studies: [study] }));
    service.config.maintenance = true;
    await app.refreshConfig();
    await app.consent(study);
    assert.equal(
      app.getSnapshot().state!.queue.find((q) => q.kind === "consent")!.state,
      "queued",
    );
    assert.equal(
      service.calls.filter(
        (call) => call.path === "/v1/studies/unit-study/consents",
      ).length,
      0,
    );
    service.overrides.set("/v1/studies/unit-study/withdrawals", () =>
      service.result({ state: "withdrawn" }),
    );
    await app.withdraw(study.study_id);
    assert.equal(
      app.getSnapshot().state!.queue.find((q) => q.kind === "consent")!.state,
      "blocked",
    );
    service.config.maintenance = false;
    await app.refreshConfig();
    await app.retryUploads();
    assert.equal(
      service.calls.filter(
        (call) => call.path === "/v1/studies/unit-study/consents",
      ).length,
      0,
    );
    assert.equal(
      (app.getSnapshot().state!.studies[0]!.consent as any).state,
      "withdrawn",
    );
  } finally {
    await close();
  }
});

test("signed-in profile revision freezes into Start check and a later profile save cannot replace it", async () => {
  const { app, service, close } = await account();
  try {
    assert.equal(
      app.getSnapshot().identity?.accountRef,
      service.caps.account_ref,
    );
    assert.equal(app.getSnapshot().route, "home");
    const form = clone(app.getSnapshot().state!.profile);
    form.profile.age_years = 30;
    form.profile.height_cm = 180;
    form.profile.weight_kg = 80;
    await app.saveProfile(form);
    assert.equal(app.getSnapshot().state!.profile.sync, "synced");
    await app.beginCheck("engineering_fixture", true);
    const original = clone(app.check!.context);
    await app.simulate("cardiac", "ppg");
    await app.simulate("cardiac", "ecg");
    await app.selectCardiac(app.check!.attempts.at(-1)!.attempt_id);
    await app.simulate("saliva");
    await app.setStage("review");
    await app.saveCheck();
    const frozen = clone(app.check!);
    form.profile.age_years = 31;
    form.etag = app.getSnapshot().state!.profile.etag;
    await app.saveProfile(form);
    assert.deepEqual(app.check!.context, original);
    assert.deepEqual(app.check!.snapshot, frozen.snapshot);
    assert.equal(
      service.calls.some((call) => call.path.includes("/finalize")),
      false,
    );
    await app.changePreferences({ theme: "dark", reducedMotion: true });
    assert.equal(app.getSnapshot().state!.preferences.theme, "dark");
    await app.refreshStudies();
    await app.navigate("studies");
    await app.clearLocal();
    assert.equal(app.getSnapshot().state!.checks.length, 0);
    assert.equal(app.getSnapshot().state!.profile.profile.age_years, null);
  } finally {
    await close();
  }
});

test("notice acknowledgment is explicit and keeps the exact displayed version through account synchronization", async () => {
  const { app, service, close } = await account();
  try {
    service.caps.notice.acknowledged = false;
    await app.refreshCapabilities();
    await app.commit((state) => ({ ...state, acknowledgedNotice: null }));
    await assert.rejects(
      () => app.saveProfile(app.getSnapshot().state!.profile),
      /notice/i,
    );
    await app.loadNotice();
    await app.acknowledgeNotice();
    assert.equal(
      app.getSnapshot().state!.acknowledgedNotice,
      service.notice.sha256,
    );
    const request = service.calls.find(
      (call) => call.path === "/v1/me/acknowledgments",
    );
    assert.equal(request?.body.sha256, service.notice.sha256);
    assert.equal(request?.body.version, "v1");
    assert.equal(request?.headers.get("X-Data-Generation"), "1");
    await app.navigate("notice");
    await app.navigate("home");
  } finally {
    await close();
  }
});

test("delayed history cannot enter another account or reopen a signed-out workspace", async () => {
  const { app, service, close } = await account();
  try {
    const entered = deferred<void>(),
      answer = deferred<Response>();
    service.overrides.set("/v1/sessions?limit=20", () => {
      entered.resolve();
      return answer.promise;
    });
    const history = app.refreshHistory();
    await entered.promise;
    const rejected = assert.rejects(() => history, /workspace|account/i);
    await app.signOut(false);
    answer.resolve(
      service.result({
        items: [{ session_id: "old-account-private-check" }],
        next_cursor: null,
      }),
    );
    await rejected;
    assert.equal(app.getSnapshot().identity, null);
    assert.deepEqual(app.getSnapshot().historyRows, []);
    assert.deepEqual(app.getSnapshot().state!.historyIndex, []);
    assert.equal(app.getSnapshot().route, "welcome");
  } finally {
    await close();
  }
});

test("server generation retirement quarantines prior checks and a new empty workspace requires separate acknowledgment", async () => {
  const { app, service, close } = await account();
  try {
    await app.beginCheck("engineering_fixture", true);
    await app.simulate("saliva");
    await app.saveCheck();
    const oldId = app.check!.id;
    service.caps.data_generation = 2;
    service.caps.account_state = "deleting";
    await app.refreshCapabilities();
    assert.equal(app.getSnapshot().state!.checks[0]!.delivery, "quarantined");
    assert.equal(app.getSnapshot().selectedCheck, null);
    await assert.rejects(() => app.selectCheck(oldId), /retired/i);
    await assert.rejects(
      () => app.beginCheck("engineering_fixture", true),
      /privacy|workspace/i,
    );
    await assert.rejects(
      () => app.acknowledgeNewGeneration(),
      /wait|deletion/i,
    );
    service.caps.account_state = "awaiting_generation_ack";
    service.overrides.set("/v1/me/data-generation/acknowledgments", () => {
      service.caps.account_state = "active";
      return service.result({ state: "active", data_generation: 2 });
    });
    await app.acknowledgeNewGeneration();
    assert.equal(app.getSnapshot().state!.checks.length, 0);
    assert.equal(app.getSnapshot().state!.profile.profile.age_years, null);
    assert.equal(app.getSnapshot().state!.generation, 2);
    assert.equal(app.getSnapshot().route, "notice");
    const request = service.calls.find(
      (call) => call.path === "/v1/me/data-generation/acknowledgments",
    );
    assert.equal(request?.headers.get("X-Data-Generation"), "2");
    assert.deepEqual(request?.body, { confirmation: true });
  } finally {
    await close();
  }
});

test("native stop requests cancellation before waiting for a delayed device stop and retains the immutable native completion", async () => {
  const { app, close } = await account();
  try {
    unit().available = true;
    await app.beginCheck("measurement", true);
    await app.startNativeTask();
    const active = app.getSnapshot().activeTask!;
    const result = clone(nativeFixture) as unknown as NativeTaskResult;
    result.runId = active.runId;
    result.workspaceEpoch = active.epoch;
    result.seed = active.seed;
    result.startedAt = new Date().toISOString();
    result.endedAt = new Date(Date.now() + result.durationMs).toISOString();
    let requested = 0;
    const radio = deferred<void>();
    app.nativeView = {
      cancel: async (runId: string) => {
        requested++;
        assert.equal(runId, active.runId);
        return { runId, status: "already_terminal", result };
      },
    } as any;
    app.device.cancelCapture = async () => radio.promise;
    const stopped = app.stopActive("USER_CANCELED");
    assert.equal(requested, 1);
    await new Promise((resolve) => setImmediate(resolve));
    assert.equal(app.getSnapshot().activeTask, null);
    assert.equal(app.check!.attempts[0]!.status, "valid");
    assert.deepEqual(
      app.check!.attempts[0]!.component_metadata.native_result,
      result,
    );
    radio.resolve();
    await stopped;
    await app.completeNativeTask(result);
    assert.equal(app.check!.attempts.length, 1);
    await app.navigate("home");
  } finally {
    await close();
  }
});

test("unmounted task arm is invalidated while unsupported or stale task terminals cannot become valid evidence", async () => {
  const { app, close } = await account();
  try {
    unit().available = false;
    await app.beginCheck("measurement", true);
    await assert.rejects(() => app.startNativeTask(), /native/i);
    unit().available = true;
    await app.startNativeTask();
    const active = app.getSnapshot().activeTask!;
    app.updateProgress(active.runId, active.epoch, "practice", 3);
    assert.match(app.getSnapshot().taskProgress!, /Practice/);
    const oldProgress = app.getSnapshot().taskProgress;
    app.updateProgress("stale", "wrong", "scored", 66);
    assert.equal(app.getSnapshot().taskProgress, oldProgress);
    await app.completeNativeTask({
      ...nativeFixture,
      runId: "old-run",
    } as unknown as NativeTaskResult);
    assert.equal(app.check!.attempts[0]!.status, "started");
    await app.stopActive("VIEW_DETACHED");
    assert.equal(app.getSnapshot().activeTask, null);
    assert.equal(app.check!.attempts[0]!.status, "invalid");
    assert.equal(
      app.check!.attempts[0]!.quality_flags.includes("INTERRUPTED"),
      true,
    );
  } finally {
    await close();
  }
});
