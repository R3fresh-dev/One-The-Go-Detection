import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import {
  createCheck,
  emptyWorkspace,
  freezeCheck,
  replaceCheck,
  simulatedCapture,
} from "../src/core/domain";
import { clone, digest } from "../src/core/integrity";
import { ApiClient, ApiError, type ApiResponse } from "../src/services/api";
import { queueCheck, queueMutation, SyncEngine } from "../src/services/sync";
import type { JsonObject, WorkspaceState } from "../src/core/types";

const at = "2026-10-11T15:00:00.000Z";
function seeded() {
  let state = emptyWorkspace("local:account", at);
  let check = createCheck(state, {
    now: at,
    id: randomUUID,
    kind: "engineering_fixture",
    accountRef: "00000000-0000-4000-8000-000000000001",
    contextConfirmed: true,
  });
  check = simulatedCapture(check, "saliva", at, randomUUID);
  check = freezeCheck(check, at, randomUUID);
  state = replaceCheck(state, check);
  return { state, check };
}
interface Call {
  path: string;
  options: Record<string, unknown>;
}
function harness(
  initial: WorkspaceState,
  options: {
    lostRegistration?: boolean;
    failStatus?: number;
    deletion?: boolean;
  } = {},
) {
  let state = clone(initial),
    lost = false,
    epoch = "owner-epoch-1",
    available = true;
  const calls: Call[] = [];
  const fake = {
    async request(
      path: string,
      input: Record<string, unknown> = {},
    ): Promise<ApiResponse<unknown>> {
      calls.push({ path, options: clone(input) });
      if (options.failStatus)
        throw new ApiError(
          options.failStatus,
          "TEST_FAILURE",
          "Request rejected",
        );
      if (path === "/v1/privacy/deletion-requests")
        return {
          value: {
            schema_version: "1.0.0",
            kind: "deletion",
            job_id: "88888888-8888-4888-8888-888888888888",
            scope: "all_data",
            data_generation: 2,
            state: "pending",
            accepted_at: at,
            retained_categories: [],
            policy_version: "privacy-v1",
            attempt_count: 0,
            allowed_actions: ["refresh"],
          },
          status: 202,
          etag: null,
          evidenceSha256: null,
        };
      const check = state.checks[0]!;
      if (path === "/v1/sessions" && options.lostRegistration && !lost) {
        lost = true;
        throw new ApiError(
          0,
          "LOST_REPLY",
          "The service accepted the request but its response was lost.",
          true,
        );
      }
      const value = path.endsWith("/snapshot")
        ? { revision: 2, snapshot_sha256: check.snapshot_sha256 }
        : path.endsWith("/result")
          ? check.result
          : { revision: 1 };
      return {
        value,
        status: path.endsWith("/finalize") ? 202 : 200,
        etag: path.endsWith("/snapshot") ? '"2"' : '"1"',
        evidenceSha256: check.evidence_sha256,
      };
    },
  };
  const engine = new SyncEngine(
    fake as unknown as ApiClient,
    () => state,
    async (change) => {
      state = change(state);
    },
    () => epoch,
    () => available,
  );
  return {
    engine,
    calls,
    get state() {
      return state;
    },
    set state(value: WorkspaceState) {
      state = value;
    },
    changeEpoch() {
      epoch = "new-owner";
    },
    pause() {
      available = false;
    },
  };
}
test("explicit upload registers evidence then snapshot then finalizes and verifies result", async () => {
  const { state, check } = seeded(),
    queued = queueCheck(state, check.id, randomUUID, at),
    h = harness(queued);
  await h.engine.run(queued.queue[0]!.id, true);
  assert.equal(h.state.checks[0]!.delivery, "synced");
  assert.equal(h.state.queue[0]!.state, "synced");
  assert.deepEqual(
    h.calls.map((x) => x.path),
    [
      "/v1/sessions",
      `/v1/sessions/${check.id}/context`,
      `/v1/sessions/${check.id}/attempts/${check.attempts[0]!.attempt_id}`,
      `/v1/sessions/${check.id}/evidence-manifest`,
      `/v1/sessions/${check.id}/snapshot`,
      `/v1/sessions/${check.id}/finalize`,
      `/v1/sessions/${check.id}/result`,
    ],
  );
  const context = h.calls[1]!;
  assert.equal(context.options.etag, '"0"');
  assert.equal(h.calls.at(-2)!.options.etag, '"2"');
  for (const call of h.calls.filter((x) => x.options.method)) {
    assert.equal(call.options.generation, 1);
    assert.ok(call.options.key);
  }
});
test("reconnection does not retry an ordinary explicit queue when preference remains off", async () => {
  const { state, check } = seeded(),
    queued = queueCheck(state, check.id, randomUUID, at),
    h = harness(queued);
  await h.engine.retryDue(false);
  assert.equal(h.calls.length, 0);
  assert.equal(h.state.queue[0]!.state, "queued");
  await h.engine.retryDue(true);
  assert.ok(h.calls.length > 0);
});
test("a lost accepted response replays the same identity and unchanged bytes", async () => {
  const { state, check } = seeded(),
    queued = queueCheck(state, check.id, randomUUID, at),
    h = harness(queued, { lostRegistration: true });
  await h.engine.run(queued.queue[0]!.id, true);
  assert.equal(h.state.queue[0]!.state, "retry_wait");
  const first = h.calls[0]!;
  await h.engine.run(queued.queue[0]!.id, true);
  const second = h.calls[1]!;
  assert.equal(second.path, "/v1/sessions");
  assert.equal(second.options.key, first.options.key);
  assert.equal(digest(second.options.body), digest(first.options.body));
  assert.equal(second.options.generation, first.options.generation);
  assert.equal(h.state.queue[0]!.state, "synced");
});
test("conflict and stale generation stop automatic replay without changing frozen evidence", async () => {
  for (const code of [409, 412, 428, 410]) {
    const { state, check } = seeded(),
      queued = queueCheck(state, check.id, randomUUID, at),
      h = harness(queued, { failStatus: code });
    h.state.preferences.retryQueuedAutomatically = true;
    await h.engine.run(queued.queue[0]!.id, true);
    const count = h.calls.length;
    await h.engine.retryDue();
    assert.equal(h.calls.length, count);
    assert.equal(h.state.checks[0]!.snapshot_sha256, check.snapshot_sha256);
    assert.equal(
      h.state.queue[0]!.state,
      code === 410 ? "quarantined" : "conflict",
    );
  }
});
test("accepted deletion intent may reconcile with its old generation and original key", async () => {
  const { state } = seeded();
  const queued = queueMutation(
    state,
    "deletion",
    { scope: "all_data", confirmation: true },
    randomUUID,
    at,
  );
  const key = queued.queue[0]!.keys.request;
  queued.generation = 2;
  const h = harness(queued);
  await h.engine.retryDue(false);
  assert.equal(h.calls[0]!.options.generation, 1);
  assert.equal(h.calls[0]!.options.key, key);
  assert.equal(h.state.jobs[0]!.kind, "deletion");
  assert.equal(h.state.queue[0]!.state, "synced");
});
test("repeated unconfirmed export click retains one durable operation identity", () => {
  const { state } = seeded(),
    body = {
      selection: { kind: "all", session_ids: [] },
      format: "json_zip",
      include_raw: false,
    } as JsonObject;
  const first = queueMutation(state, "export", body, randomUUID, at),
    second = queueMutation(first, "export", body, randomUUID, at);
  assert.equal(second.queue.length, 1);
  assert.equal(second.queue[0]!.keys.request, first.queue[0]!.keys.request);
});
test("a new account epoch prevents late network results writing into its workspace", async () => {
  const { state, check } = seeded(),
    queued = queueCheck(state, check.id, randomUUID, at);
  let current = queued,
    epoch = "one",
    resolve!: () => void;
  const gate = new Promise<void>((r) => {
    resolve = r;
  });
  const fake = {
    request: async () => {
      await gate;
      return {
        value: { revision: 1 },
        status: 200,
        etag: '"1"',
        evidenceSha256: null,
      };
    },
  };
  const engine = new SyncEngine(
    fake as unknown as ApiClient,
    () => current,
    async (change) => {
      current = change(current);
    },
    () => epoch,
    () => true,
  );
  const pending = engine.run(queued.queue[0]!.id, true);
  await new Promise((r) => setTimeout(r, 0));
  epoch = "two";
  current = emptyWorkspace("other-account", at);
  resolve();
  await pending;
  assert.equal(current.workspace, "other-account");
  assert.equal(current.checks.length, 0);
  assert.equal(current.queue.length, 0);
});
test("HTTP client sends access token and stable generation, rejects missing write identity", async () => {
  const oldFetch = globalThis.fetch;
  const requests: RequestInit[] = [];
  globalThis.fetch = async (_url, init) => {
    requests.push(init!);
    return new Response('{"accepted":true}', {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  try {
    const client = new ApiClient("https://api.example.test", {
      accessToken: async () => "access-only",
    });
    await assert.rejects(
      client.request("/v1/me/profile", { method: "PATCH", body: {} }),
      /stable operation identity/,
    );
    await client.request("/v1/me/profile", {
      method: "PATCH",
      body: {},
      generation: 3,
      key: "stable-key",
      etag: '"2"',
    });
    const headers = requests[0]!.headers as Record<string, string>;
    assert.equal(headers.Authorization, "Bearer access-only");
    assert.equal(headers["X-Data-Generation"], "3");
    assert.equal(headers["Idempotency-Key"], "stable-key");
    assert.equal(headers["If-Match"], '"2"');
  } finally {
    globalThis.fetch = oldFetch;
  }
});

test("already queued ordinary uploads remain untouched during service readiness pause", async () => {
  const { state, check } = seeded();
  let current = queueCheck(state, check.id, randomUUID, at),
    ready = false;
  const requests: string[] = [];
  const fake = {
    request: async (path: string) => {
      requests.push(path);
      throw new ApiError(0, "OFFLINE", "Offline", true);
    },
  };
  const engine = new SyncEngine(
    fake as unknown as ApiClient,
    () => current,
    async (change) => {
      current = change(current);
    },
    () => "same-account",
    () => true,
    () => ready,
  );
  const original = digest(current.queue[0]);
  await engine.run(current.queue[0]!.id, true);
  assert.equal(requests.length, 0);
  assert.equal(digest(current.queue[0]), original);
  ready = true;
  await engine.run(current.queue[0]!.id, true);
  assert.equal(requests.length, 1);
});

test("lost notice acknowledgment response replays its durable timestamp and key before unblocking", async () => {
  const { DEMO_NOTICE } = await import("../src/services/api");
  let current = emptyWorkspace("local:account", at);
  current.notice = DEMO_NOTICE;
  current = queueMutation(
    current,
    "acknowledgment",
    {
      version: DEMO_NOTICE.version,
      sha256: DEMO_NOTICE.sha256,
      acknowledged_at: at,
    },
    randomUUID,
    at,
  );
  const calls: { key: string; body: JsonObject }[] = [];
  const fake = {
    request: async (
      _path: string,
      options: { key: string; body: JsonObject },
    ) => {
      calls.push(clone(options));
      if (calls.length === 1)
        throw new ApiError(0, "LOST_REPLY", "Response lost", true);
      return {
        value: { version: DEMO_NOTICE.version, sha256: DEMO_NOTICE.sha256 },
        status: 200,
        etag: null,
        evidenceSha256: null,
      };
    },
  };
  const engine = new SyncEngine(
    fake as unknown as ApiClient,
    () => current,
    async (change) => {
      current = change(current);
    },
    () => "same-account",
    () => true,
    () => false,
  );
  await engine.run(current.queue[0]!.id, true);
  assert.equal(current.acknowledgedNotice, null);
  await engine.run(current.queue[0]!.id, true);
  assert.equal(current.acknowledgedNotice, DEMO_NOTICE.sha256);
  assert.equal(calls[0]!.key, calls[1]!.key);
  assert.deepEqual(calls[0]!.body, calls[1]!.body);
});
