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
import { ApiClient } from "../src/services/api";
import { queueCheck, SyncEngine } from "../src/services/sync";
import capabilities from "../testfixtures/backend-capabilities.json";
import { deferred } from "./support/customer";
import type { Capabilities, WorkspaceState } from "../src/core/types";

const at = "2026-10-11T15:00:00.000Z";
function fixture() {
  let state = emptyWorkspace("local:fictional-sync-owner", at);
  const caps = clone(capabilities) as Capabilities;
  state.capabilities = caps;
  const draft = createCheck(state, {
    now: at,
    id: randomUUID,
    kind: "engineering_fixture",
    accountRef: caps.account_ref,
    contextConfirmed: true,
  });
  const local = freezeCheck(
    simulatedCapture(clone(draft), "saliva", at, randomUUID),
    at,
    randomUUID,
  );
  const server = freezeCheck(
    simulatedCapture(clone(draft), "eyes", at, randomUUID),
    at,
    randomUUID,
  );
  state = queueCheck(replaceCheck(state, local), local.id, randomUUID, at);
  state.queue[0]!.phase = local.attempts.length + 4; // Only the snapshot write remains before finalization.
  state.preferences.retryQueuedAutomatically = true;
  const remote: any = {
    session_id: server.id,
    state: "completed",
    revision: 7,
    mode: server.snapshot.mode,
    created_at: server.snapshot.created_at,
    snapshot_sha256: server.snapshot_sha256,
    evidence_sha256: server.evidence_sha256,
    result: server.result,
    snapshot: server.snapshot,
    context: server.context,
    manifest: server.manifest,
    attempts: server.attempts,
    alcohol: server.alcohol,
    instruction_receipts: [],
    collections: [],
    collection_abandons: [],
    raw_artifacts_omitted_reason: "NO_RAW_EXPORT_SCOPE",
  };
  return { state, local, server, remote };
}
const response = (
  value: unknown,
  status = 200,
  headers: Record<string, string> = {},
) =>
  new Response(JSON.stringify(value), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
function harness(state: WorkspaceState, transport: typeof fetch) {
  const prior = globalThis.fetch;
  globalThis.fetch = transport;
  let current = clone(state),
    epoch = "same-fictional-owner";
  const api = new ApiClient("http://localhost:8000", {
    accessToken: async () => "fictional-unit-token",
  });
  const engine = new SyncEngine(
    api,
    () => current,
    async (change) => {
      current = change(current);
    },
    () => epoch,
    () => true,
  );
  return {
    engine,
    get state() {
      return current;
    },
    set state(value: WorkspaceState) {
      current = value;
    },
    changeEpoch() {
      epoch = "replacement-owner";
    },
    close() {
      globalThis.fetch = prior;
    },
  };
}

test("snapshot 412 and frozen 409 read back one authoritative revision without changing or replaying pending evidence", async () => {
  for (const status of [412, 409]) {
    const f = fixture(),
      calls: string[] = [];
    const h = harness(f.state, async (input, init) => {
      calls.push(`${init?.method ?? "GET"} ${new URL(String(input)).pathname}`);
      return init?.method === "PUT"
        ? response(
            { code: status === 409 ? "STATE_CONFLICT" : "ETAG_MISMATCH" },
            status,
          )
        : response(f.remote, 200, { ETag: '"7"' });
    });
    try {
      const pending = clone(h.state.checks[0]!),
        keys = clone(h.state.queue[0]!.keys),
        body = clone(h.state.queue[0]!.body);
      await h.engine.run(h.state.queue[0]!.id, true);
      assert.deepEqual(calls, [
        `PUT /v1/sessions/${f.local.id}/snapshot`,
        `GET /v1/sessions/${f.local.id}`,
      ]);
      const conflict = (h.state.checks[0] as any).sync_conflict;
      assert.deepEqual(conflict.server_record, f.remote);
      assert.equal(conflict.server_etag, '"7"');
      assert.equal(conflict.frozen, true);
      assert.equal(h.state.queue[0]!.state, "conflict");
      assert.equal(
        digest(h.state.checks[0]!.snapshot),
        digest(pending.snapshot),
      );
      assert.equal(
        digest(h.state.checks[0]!.manifest),
        digest(pending.manifest),
      );
      assert.deepEqual(h.state.checks[0]!.attempts, pending.attempts);
      assert.equal(h.state.checks[0]!.remote_etag, pending.remote_etag);
      assert.deepEqual(h.state.queue[0]!.keys, keys);
      assert.deepEqual(h.state.queue[0]!.body, body);
      await h.engine.retryDue(true);
      await h.engine.retryDue(false);
      assert.equal(calls.length, 2);
    } finally {
      h.close();
    }
  }
});

test("conflict readback cannot publish after epoch, generation, owner or cancellation changes", async () => {
  for (const mutation of [
    "epoch",
    "generation",
    "owner",
    "account-state",
    "capability-generation",
    "cancel",
  ]) {
    const f = fixture(),
      entered = deferred<void>(),
      reply = deferred<Response>();
    const h = harness(f.state, async (_input, init) => {
      if (init?.method === "PUT")
        return response({ code: "ETAG_MISMATCH" }, 412);
      entered.resolve();
      return reply.promise;
    });
    try {
      const pending = h.engine.run(h.state.queue[0]!.id, true);
      // A missing readback must fail rather than hanging this regression.
      await Promise.race([
        entered.promise,
        pending.then(() =>
          assert.fail("Conflict did not request authoritative state"),
        ),
      ]);
      if (mutation === "epoch") h.changeEpoch();
      else if (mutation === "generation") h.state.generation++;
      else if (mutation === "owner")
        h.state.capabilities!.account_ref = "replacement-owner";
      else if (mutation === "account-state")
        h.state.capabilities!.account_state = "deleting";
      else if (mutation === "capability-generation")
        h.state.capabilities!.data_generation++;
      else h.state.queue[0]!.state = "blocked";
      reply.resolve(response(f.remote, 200, { ETag: '"7"' }));
      await pending;
      assert.equal((h.state.checks[0] as any).sync_conflict, undefined);
    } finally {
      h.close();
    }
  }
});

test("unavailable or foreign authoritative readback stays a preserved conflict and never substitutes local data", async () => {
  for (const invalid of ["unavailable", "foreign", "etag"]) {
    const f = fixture();
    if (invalid === "foreign")
      f.remote.snapshot.subject_ref = "foreign-account";
    const h = harness(f.state, async (_input, init) =>
      init?.method === "PUT"
        ? response({ code: "STATE_CONFLICT" }, 409)
        : invalid === "unavailable"
          ? response({ code: "TEMPORARY_UNAVAILABLE" }, 503)
          : response(f.remote, 200, {
              ETag: invalid === "etag" ? '"8"' : '"7"',
            }),
    );
    try {
      await h.engine.run(h.state.queue[0]!.id, true);
      const conflict = (h.state.checks[0] as any).sync_conflict;
      assert.equal(h.state.queue[0]!.state, "conflict");
      assert.equal(conflict.server_record, null);
      assert.ok(conflict.read_error);
      assert.equal(h.state.checks[0]!.snapshot_sha256, f.local.snapshot_sha256);
    } finally {
      h.close();
    }
  }
});

test("HTTP 429 Retry-After waits even on explicit retry and becomes eligible at its boundary", async (context) => {
  context.mock.timers.enable({ apis: ["Date"], now: Date.parse(at) });
  const f = fixture();
  let calls = 0;
  const h = harness(f.state, async () => {
    calls++;
    return response({ code: "LIMIT_EXCEEDED", retryable: true }, 429, {
      "Retry-After": "10",
    });
  });
  try {
    const id = h.state.queue[0]!.id;
    await h.engine.run(id, true);
    assert.equal(h.state.queue[0]!.state, "retry_wait");
    assert.equal(h.state.queue[0]!.next_attempt_at, "2026-10-11T15:00:10.000Z");
    await h.engine.run(id, true);
    await h.engine.retryDue(false);
    assert.equal(calls, 1);
    context.mock.timers.setTime(Date.parse(at) + 9999);
    await h.engine.run(id, true);
    assert.equal(calls, 1);
    context.mock.timers.setTime(Date.parse(at) + 10000);
    await h.engine.run(id, true);
    assert.equal(calls, 2);
  } finally {
    h.close();
  }
});

test("HTTP 422 retains terminal field errors for inspection without retrying immutable snapshot", async () => {
  const f = fixture();
  let calls = 0;
  const fields = { "snapshot.sample.collected_volume_ml": "greater_than" };
  const h = harness(f.state, async () => {
    calls++;
    return response({ code: "VALIDATION_FAILED", field_errors: fields }, 422);
  });
  try {
    await h.engine.run(h.state.queue[0]!.id, true);
    assert.equal(h.state.queue[0]!.state, "blocked");
    assert.deepEqual((h.state.queue[0] as any).field_errors, fields);
    await h.engine.retryDue(true);
    await h.engine.retryDue(false);
    assert.equal(calls, 1);
    assert.equal(h.state.checks[0]!.snapshot_sha256, f.local.snapshot_sha256);
  } finally {
    h.close();
  }
});

test("422 field inspection retains bounded paths and safe codes rather than response inputs or arbitrary values", async () => {
  const f = fixture();
  const fields: any = {
    "snapshot.sample.collected_volume_ml": "greater_than",
    "snapshot.history.sleep_hours": "Bearer SECRET-TOKEN measured value 99.9",
    "snapshot.task.status": "PRIVATE_TOKEN_VALUE",
    "snapshot.<script>value</script>": "missing",
    nested: { input: "PRIVATE" },
  };
  for (let i = 0; i < 40; i++) fields[`snapshot.field_${i}`] = "missing";
  const h = harness(f.state, async () =>
    response(
      {
        code: "VALIDATION_FAILED",
        field_errors: fields,
        input: "PRIVATE-PAYLOAD",
      },
      422,
    ),
  );
  try {
    await h.engine.run(h.state.queue[0]!.id, true);
    const retained = (h.state.queue[0] as any).field_errors;
    assert.ok(Object.keys(retained).length <= 32);
    assert.equal(
      retained["snapshot.sample.collected_volume_ml"],
      "greater_than",
    );
    assert.equal(retained["snapshot.history.sleep_hours"], "invalid");
    assert.equal(retained["snapshot.task.status"], "invalid");
    assert.doesNotMatch(
      JSON.stringify(retained),
      /SECRET|PRIVATE|99\.9|script/,
    );
  } finally {
    h.close();
  }
});

test("Retry-After beyond one hour requires manual same-intent retry after the full server deadline", async (context) => {
  context.mock.timers.enable({ apis: ["Date"], now: Date.parse(at) });
  const f = fixture();
  let calls = 0;
  const h = harness(f.state, async () => {
    calls++;
    return response({ code: "LIMIT_EXCEEDED" }, 429, { "Retry-After": "3601" });
  });
  try {
    const keys = clone(h.state.queue[0]!.keys),
      body = clone(h.state.queue[0]!.body);
    await h.engine.run(h.state.queue[0]!.id, true);
    assert.equal(h.state.queue[0]!.state, "retry_wait");
    assert.equal(h.state.queue[0]!.next_attempt_at, "2026-10-11T16:00:01.000Z");
    assert.match(h.state.queue[0]!.error!, /one-hour retry bound/);
    await h.engine.retryDue(true);
    await h.engine.retryDue(false);
    assert.equal(calls, 1);
    context.mock.timers.setTime(Date.parse(at) + 3_600_999);
    await h.engine.retryDue(true);
    assert.equal(calls, 1);
    context.mock.timers.setTime(Date.parse(at) + 3_601_000);
    await h.engine.retryDue(false);
    assert.equal(calls, 1);
    await h.engine.retryDue(true);
    assert.equal(calls, 2);
    assert.deepEqual(h.state.queue[0]!.keys, keys);
    assert.deepEqual(h.state.queue[0]!.body, body);
  } finally {
    h.close();
  }
});

test("explicit conflict refresh makes only a guarded read and retains the original pending operation", async () => {
  const f = fixture();
  let reads = 0;
  const h = harness(f.state, async (_input, init) => {
    if (init?.method === "PUT") return response({ code: "ETAG_MISMATCH" }, 412);
    reads++;
    return reads === 1
      ? response({ code: "TEMPORARY_UNAVAILABLE" }, 503)
      : response(f.remote, 200, { ETag: '"7"' });
  });
  try {
    const id = h.state.queue[0]!.id,
      original = clone(h.state.queue[0]!);
    await h.engine.run(id, true);
    assert.equal((h.state.checks[0] as any).sync_conflict.server_record, null);
    assert.equal(
      typeof (h.engine as any).inspectConflict,
      "function",
      "Conflict refresh needs an explicit read-only path",
    );
    await (h.engine as any).inspectConflict(id);
    assert.equal(reads, 2);
    assert.deepEqual(
      (h.state.checks[0] as any).sync_conflict.server_record,
      f.remote,
    );
    assert.equal(h.state.queue[0]!.state, "conflict");
    assert.deepEqual(h.state.queue[0]!.body, original.body);
    assert.deepEqual(h.state.queue[0]!.keys, original.keys);
  } finally {
    h.close();
  }
});

test("a server-retired generation discovered during conflict readback is quarantined", async () => {
  const f = fixture();
  const h = harness(f.state, async (_input, init) =>
    init?.method === "PUT"
      ? response({ code: "STATE_CONFLICT" }, 409)
      : response({ code: "DATA_GENERATION_RETIRED" }, 410),
  );
  try {
    await h.engine.run(h.state.queue[0]!.id, true);
    assert.equal(h.state.queue[0]!.state, "quarantined");
    assert.equal(h.state.checks[0]!.delivery, "quarantined");
    assert.equal((h.state.checks[0] as any).sync_conflict, undefined);
    assert.equal(h.state.checks[0]!.snapshot_sha256, f.local.snapshot_sha256);
  } finally {
    h.close();
  }
});
