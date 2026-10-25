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
import { clone, digestBytes } from "../src/core/integrity";
import { ApiClient, ApiError } from "../src/services/api";
import { queueCheck, SyncEngine } from "../src/services/sync";
import type { RawArtifact } from "../src/core/rawArtifacts";
import type { WorkspaceState } from "../src/core/types";
import type { WorkspaceStore } from "../src/platform/storage.types";
import { deferred } from "./support/customer";

// Engineered transport fixture only: this suite proves orchestration and RAM
// cleanup, not physical optics, an approved study or an actual object store.
function harness(selected = true) {
  const at = new Date().toISOString(),
    bytes = new Uint8Array([1, 2, 3, 4]);
  let state = emptyWorkspace("unit-owned-raw-upload", at);
  let check = createCheck(state, {
    now: at,
    id: randomUUID,
    kind: "engineering_fixture",
    accountRef: randomUUID(),
    contextConfirmed: true,
  });
  check = freezeCheck(
    simulatedCapture(check, "eyes", at, randomUUID),
    at,
    randomUUID,
  );
  state = replaceCheck(state, check);
  const raw: RawArtifact = {
    local_id: randomUUID(),
    study_id: "fictional-unit-study",
    session_id: check.id,
    attempt_id: check.attempts[0]!.attempt_id,
    artifact_kind: "eye_video",
    format: "OTGD-EYE-ROI-v1",
    media_type: "application/octet-stream",
    sha256: digestBytes(bytes),
    size_bytes: bytes.length,
    capture_started_at: at,
    consent_record_id: randomUUID(),
    permission: {
      record: true,
      upload: true,
      receipt_id: randomUUID(),
      policy_id: "fictional-policy",
      policy_version: "v1",
      policy_sha256: "a".repeat(64),
      raw_notice_version: "v1",
      raw_notice_sha256: "b".repeat(64),
    },
    state: "local",
    server_artifact_id: null,
    created_at: at,
    retention_due_at: new Date(Date.now() + 86_400_000).toISOString(),
    error: null,
  };
  state.rawArtifacts = [raw];
  state = queueCheck(
    state,
    check.id,
    randomUUID,
    at,
    selected ? [raw.local_id] : [],
  );
  const calls: { path: string; options: any; persistedRawTickets?: any }[] = [],
    readBuffers: Uint8Array[] = [],
    artifactId = randomUUID();
  let putFailures = 0,
    renewLoss = false,
    completeLoss = false,
    serverVerified = false,
    readWait: ReturnType<typeof deferred<Uint8Array>> | null = null,
    reads = 0;
  const ticket = () => ({
    artifact_id: artifactId,
    method: "PUT",
    upload_url:
      "https://owned-artifacts.example.test/object?signature=fictional",
    required_headers: {
      "Content-Length": String(bytes.length),
      "Content-Type": raw.media_type,
      "If-None-Match": "*",
      "x-amz-checksum-sha256": Buffer.from(raw.sha256, "hex").toString(
        "base64",
      ),
      "x-amz-server-side-encryption": "AES256",
    },
    expires_in_seconds: 300,
    expires_at: new Date(Date.now() + 300_000).toISOString(),
  });
  const api = {
    request: async (path: string, options: any = {}) => {
      calls.push({
        path,
        options: clone(options),
        ...(path.endsWith("/ticket")
          ? { persistedRawTickets: clone(state.queue[0]!.body.raw_tickets) }
          : {}),
      });
      let value: any = {},
        status = 200;
      if (path === "/v1/artifact-uploads") value = ticket();
      else if (path.endsWith("/ticket")) {
        if (renewLoss) {
          renewLoss = false;
          throw new ApiError(
            0,
            "NETWORK_UNAVAILABLE",
            "Lost renewal receipt",
            true,
          );
        }
        value = ticket();
      } else if (path.endsWith("/complete")) {
        serverVerified = true;
        if (completeLoss) {
          completeLoss = false;
          throw new ApiError(
            0,
            "NETWORK_UNAVAILABLE",
            "Lost completion receipt",
            true,
          );
        }
        value = {
          artifact_id: artifactId,
          state: "verified",
          sha256: raw.sha256,
          size_bytes: bytes.length,
          version_id: "immutable-object-version",
        };
      } else if (path.startsWith("/v1/artifact-uploads/"))
        value = {
          artifact_id: artifactId,
          state: serverVerified ? "verified" : "quarantine",
          sha256: raw.sha256,
          version_id: serverVerified ? "immutable-object-version" : null,
        };
      else if (path === "/v1/sessions") value = { revision: 0 };
      else if (path.endsWith("/snapshot"))
        value = { revision: 1, snapshot_sha256: check.snapshot_sha256 };
      else if (path.endsWith("/result")) status = 202;
      return {
        value,
        status,
        etag: '"1"',
        evidenceSha256: check.evidence_sha256,
      };
    },
    putArtifact: async (_ticket: any, content: Uint8Array) => {
      calls.push({ path: "OBJECT PUT", options: {} });
      assert.deepEqual(content, bytes);
      if (putFailures > 0) {
        putFailures--;
        throw new ApiError(
          0,
          "NETWORK_UNAVAILABLE",
          "Offline object store",
          true,
        );
      }
      return 412;
    },
  } as unknown as ApiClient;
  const store = {
    readRaw: async () => {
      reads++;
      const content = readWait ? await readWait.promise : bytes.slice();
      readBuffers.push(content);
      return content;
    },
  } as unknown as WorkspaceStore;
  const engine = new SyncEngine(
    api,
    () => state,
    async (change) => {
      state = change(state);
    },
    () => state.workspace,
    () => true,
    () => true,
    () => store,
  );
  return {
    engine,
    raw,
    check,
    bytes,
    calls,
    readBuffers,
    get reads() {
      return reads;
    },
    get state() {
      return state;
    },
    set state(value: WorkspaceState) {
      state = value;
    },
    get queue() {
      return state.queue[0]!;
    },
    set failures(value: number) {
      putFailures = value;
    },
    set loseRenewal(value: boolean) {
      renewLoss = value;
    },
    set loseComplete(value: boolean) {
      completeLoss = value;
    },
    set deferredRead(value: ReturnType<typeof deferred<Uint8Array>>) {
      readWait = value;
    },
  };
}

test("Save and metadata-only upload never read or queue raw; explicit selection is immutable and exact", async () => {
  const h = harness(false);
  await h.engine.run(h.queue.id, true);
  assert.equal(h.reads, 0);
  assert.equal(
    h.calls.some((call) => call.path.startsWith("/v1/artifact-uploads")),
    false,
  );
  assert.equal(h.state.rawArtifacts![0]!.state, "local");
  const chosen = harness();
  assert.throws(
    () =>
      queueCheck(
        chosen.state,
        chosen.check.id,
        randomUUID,
        new Date().toISOString(),
        [],
      ),
    /original raw selection/,
  );
  await chosen.engine.run(chosen.queue.id, true);
  assert.equal(chosen.state.rawArtifacts![0]!.state, "uploaded");
  const admission = chosen.calls.find(
    (call) => call.path === "/v1/artifact-uploads",
  )!.options.body;
  assert.equal(
    admission.raw_consent_record_id,
    chosen.raw.permission.receipt_id,
  );
  assert.equal(admission.attempt_id, chosen.raw.attempt_id);
  assert.equal(admission.capture_started_at, chosen.raw.capture_started_at);
  assert.equal(
    chosen.calls.filter((call) => call.path.endsWith("/complete")).length,
    1,
  );
  assert.equal(
    chosen.readBuffers.every((buffer) => buffer.every((byte) => byte === 0)),
    true,
  );
});

test("acknowledged expired tickets advance durable renewal identity, while a lost renewal replays its exact key", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const h = harness();
  h.failures = 2;
  await h.engine.run(h.queue.id, true);
  assert.equal(h.queue.state, "retry_wait");
  const createKey = h.calls.find(
    (call) => call.path === "/v1/artifact-uploads",
  )!.options.key;
  context.mock.timers.setTime(Date.now() + 301_000);
  h.loseRenewal = true;
  await h.engine.run(h.queue.id, true);
  const firstRenew = h.calls.find((call) => call.path.endsWith("/ticket"))!
    .options.key;
  await h.engine.run(h.queue.id, true);
  const renewals = h.calls.filter((call) => call.path.endsWith("/ticket"));
  assert.equal(renewals[1]!.options.key, firstRenew);
  assert.deepEqual(renewals[0]!.options.body, {});
  assert.deepEqual(renewals[1]!.options.body, renewals[0]!.options.body);
  for (const renewal of renewals) {
    // These snapshots are captured before the replacement HTTP response, at
    // the request boundary after SyncEngine's persisted state update.
    assert.deepEqual(renewal.persistedRawTickets[h.raw.local_id], {
      epoch: 1,
      key: firstRenew,
      ticket: null,
    });
    assert.equal(renewal.options.method, "POST");
    assert.equal(renewal.options.generation, h.queue.generation);
  }
  const acknowledged = clone((h.queue.body.raw_tickets as any)[h.raw.local_id]);
  assert.equal(acknowledged.epoch, 1);
  assert.equal(
    acknowledged.ticket.artifact_id,
    h.state.rawArtifacts![0]!.server_artifact_id,
  );
  context.mock.timers.setTime(Date.now() + 301_000);
  await h.engine.run(h.queue.id, true);
  const keys = h.calls
    .filter((call) => call.path.endsWith("/ticket"))
    .map((call) => call.options.key);
  assert.notEqual(keys[2], firstRenew);
  const nextRenewal = h.calls.filter((call) =>
    call.path.endsWith("/ticket"),
  )[2]!;
  assert.deepEqual(nextRenewal.options.body, {});
  assert.deepEqual(nextRenewal.persistedRawTickets[h.raw.local_id], {
    epoch: 2,
    key: keys[2],
    ticket: null,
  });
  assert.notEqual(firstRenew, createKey);
  assert.equal(h.state.rawArtifacts![0]!.state, "uploaded");
  assert.equal(
    h.calls.filter((call) => call.path === "/v1/artifact-uploads").length,
    1,
  );
  assert.equal(
    h.readBuffers.every((buffer) => buffer.every((byte) => byte === 0)),
    true,
  );
});

test("lost verified completion reconciles immutable server version without another overwrite or completion", async () => {
  const h = harness();
  h.loseComplete = true;
  await h.engine.run(h.queue.id, true);
  assert.equal(h.queue.state, "retry_wait");
  await h.engine.run(h.queue.id, true);
  assert.equal(h.state.rawArtifacts![0]!.state, "uploaded");
  assert.equal(h.calls.filter((call) => call.path === "OBJECT PUT").length, 1);
  assert.equal(
    h.calls.filter((call) => call.path.endsWith("/complete")).length,
    1,
  );
});

test("revocation arriving during decryption wipes returned bytes and cannot send or revive the fenced intent", async () => {
  const h = harness(),
    read = deferred<Uint8Array>();
  h.deferredRead = read;
  const pending = h.engine.run(h.queue.id, true);
  while (h.reads === 0)
    await new Promise<void>((resolve) => setImmediate(resolve));
  const blocked = clone(h.state);
  blocked.rawRecordingFences[h.raw.study_id] = ["eye_video"];
  blocked.queue[0]!.state = "blocked";
  blocked.queue[0]!.error = "RAW_REVOCATION_PENDING";
  h.state = blocked;
  const content = h.bytes.slice();
  read.resolve(content);
  await pending;
  assert.equal(
    content.every((byte) => byte === 0),
    true,
  );
  assert.equal(
    h.calls.some((call) => call.path.startsWith("/v1/artifact-uploads")),
    false,
  );
  assert.equal(h.queue.error, "RAW_REVOCATION_PENDING");
});

test("actual object PUT validates checksum/header authority, suppresses credentials and treats 412 as reconciliation only", async () => {
  const previous = globalThis.fetch,
    h = harness(),
    bytes = h.bytes,
    sha = digestBytes(bytes);
  let calls = 0;
  const ticket = {
    artifact_id: randomUUID(),
    method: "PUT",
    upload_url: "https://storage.example.test/object?presigned=test",
    required_headers: {
      "Content-Length": "4",
      "Content-Type": "application/octet-stream",
      "If-None-Match": "*",
      "x-amz-checksum-sha256": Buffer.from(sha, "hex").toString("base64"),
      "x-amz-server-side-encryption": "AES256",
    },
    expires_in_seconds: 300,
    expires_at: new Date(Date.now() + 300_000).toISOString(),
  };
  globalThis.fetch = async (_input, init) => {
    calls++;
    assert.equal(init?.credentials, "omit");
    assert.equal(init?.redirect, "error");
    assert.equal(new Headers(init?.headers).has("Authorization"), false);
    assert.deepEqual(init?.body, bytes);
    return new Response("", { status: 412 });
  };
  try {
    const api = new ApiClient("https://api.example.test", {
      accessToken: async () => {
        throw Error("Object PUT cannot request identity credentials");
      },
    });
    assert.equal(
      await api.putArtifact(ticket, bytes, sha, "application/octet-stream"),
      412,
    );
    for (const mutate of [
      (v: any) => (v.required_headers.Authorization = "leaked-token"),
      (v: any) => (v.required_headers["If-None-Match"] = ""),
      (v: any) => (v.required_headers["Content-Length"] = "5"),
      (v: any) => (v.required_headers["x-amz-checksum-sha256"] = "AAAA"),
      (v: any) => (v.upload_url = "http://public.example.test/object"),
      (v: any) => (v.expires_at = "invalid"),
    ]) {
      const changed = clone(ticket);
      mutate(changed);
      await assert.rejects(
        api.putArtifact(changed, bytes, sha, "application/octet-stream"),
      );
    }
    assert.equal(calls, 1);
    // A previously acknowledged ticket that expires while waiting is an
    // ordinary transient renewal condition, not malformed authority.
    const expired = clone(ticket);
    expired.expires_at = new Date(Date.now() - 1).toISOString();
    await assert.rejects(
      api.putArtifact(expired, bytes, sha, "application/octet-stream"),
      (error) =>
        error instanceof ApiError &&
        error.code === "RAW_TICKET_EXPIRED" &&
        error.retryable,
    );
    assert.equal(calls, 1);
  } finally {
    globalThis.fetch = previous;
  }
});

test("object PUT has a real 60-second deadline and privacy cancellation aborts transport without late success", async (context) => {
  context.mock.timers.enable({ apis: ["setTimeout"] });
  const previous = globalThis.fetch,
    h = harness(),
    entered = deferred<void>();
  let stalled = deferred<Response>();
  const ticket = {
    artifact_id: randomUUID(),
    method: "PUT",
    upload_url: "https://storage.example.test/object",
    required_headers: {
      "Content-Length": "4",
      "Content-Type": "application/octet-stream",
      "If-None-Match": "*",
      "x-amz-checksum-sha256": Buffer.from(
        digestBytes(h.bytes),
        "hex",
      ).toString("base64"),
      "x-amz-server-side-encryption": "AES256",
    },
    expires_in_seconds: 300,
    expires_at: new Date(Date.now() + 300_000).toISOString(),
  };
  globalThis.fetch = async () => {
    entered.resolve();
    return stalled.promise;
  };
  try {
    const api = new ApiClient("https://api.example.test", {
      accessToken: async () => "",
    });
    const first = api.putArtifact(
      ticket,
      h.bytes,
      digestBytes(h.bytes),
      "application/octet-stream",
    );
    const rejected = assert.rejects(
      first,
      (error) =>
        error instanceof ApiError && error.code === "RAW_UPLOAD_TIMEOUT",
    );
    await entered.promise;
    context.mock.timers.tick(60_000);
    await rejected;
    stalled = deferred<Response>();
    const second = api.putArtifact(
      ticket,
      h.bytes,
      digestBytes(h.bytes),
      "application/octet-stream",
    );
    const canceled = assert.rejects(
      second,
      (error) => error instanceof ApiError && error.code === "REQUEST_CANCELED",
    );
    api.cancelAll();
    await canceled;
    stalled.resolve(new Response(""));
    await new Promise<void>((resolve) => setImmediate(resolve));
  } finally {
    globalThis.fetch = previous;
  }
});
