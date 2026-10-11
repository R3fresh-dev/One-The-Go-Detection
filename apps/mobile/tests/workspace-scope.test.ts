import test from "node:test";
import assert from "node:assert/strict";
import {
  captureWorkspaceScope,
  retiredWithoutReplacement,
  type WorkspaceStamp,
} from "../src/core/workspaceScope";
import { emptyWorkspace, quarantineGeneration } from "../src/core/domain";
import { clone } from "../src/core/integrity";

const initial = (): WorkspaceStamp => ({
  epoch: "account-a-open-1",
  fence: 0,
  authFlow: 1,
  workspace: "env:account-a",
  issuer: "https://issuer.test",
  accountRef: "account-a",
  generation: 1,
  unlocked: true,
  foreground: true,
});
function deferred<T>() {
  let resolve!: (value: T) => void, reject!: (reason: unknown) => void;
  const pending = new Promise<T>((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { pending, resolve, reject };
}

test("delayed history, job or study responses cannot publish into another account", async () => {
  let stamp = initial();
  const response = deferred<{ rows: string[] }>(),
    scope = captureWorkspaceScope(() => stamp);
  let published: string[] = [];
  const request = scope.wait(response.pending).then((value) => {
    published = value.rows;
  });
  stamp = {
    ...stamp,
    accountRef: "account-b",
    workspace: "env:account-b",
    epoch: "account-b-open-1",
    authFlow: 2,
  };
  response.resolve({ rows: ["private account A record"] });
  await assert.rejects(request, /response was discarded/);
  assert.deepEqual(published, []);
});

test("a delayed export download never reaches sharing after generation change or local clear", async () => {
  for (const change of [
    { generation: 2 },
    { fence: 1 },
    { epoch: "reopened" },
    { authFlow: 2 },
  ]) {
    let stamp = initial();
    const response = deferred<Uint8Array>(),
      scope = captureWorkspaceScope(() => stamp);
    let shared = false;
    const request = scope.wait(response.pending).then(() => {
      scope.assertCurrent();
      shared = true;
    });
    stamp = { ...stamp, ...change };
    response.resolve(new Uint8Array([1, 2, 3]));
    await assert.rejects(request, /response was discarded/);
    assert.equal(shared, false);
  }
});

test("scope checks reject a stale error and a previously opened destructive confirmation", async () => {
  let stamp = initial();
  const response = deferred<void>(),
    scope = captureWorkspaceScope(() => stamp);
  const pending = scope.wait(response.pending);
  const oldConfirmation = () => {
    scope.assertCurrent();
    return "delete";
  };
  stamp = { ...stamp, authFlow: 2 };
  response.reject(new Error("private old-account service detail"));
  await assert.rejects(
    pending,
    (error) =>
      error instanceof Error &&
      !error.message.includes("private old-account") &&
      error.message.includes("discarded"),
  );
  assert.throws(oldConfirmation, /discarded/);
});

test("same-owner same-generation response succeeds; locking or backgrounding invalidates the scope", async () => {
  let stamp = initial();
  const scope = captureWorkspaceScope(() => stamp);
  assert.equal(await scope.wait(Promise.resolve(42)), 42);
  stamp = { ...stamp, foreground: false };
  assert.equal(scope.current(), false);
  stamp = { ...stamp, foreground: true, unlocked: false };
  assert.equal(scope.current(), false);
});

test("a deletion-only 410 fences presentation even when its retained error uses service wording", () => {
  const previous = emptyWorkspace("account-a", "2026-10-11T00:00:00Z", 1);
  previous.queue.push({
    id: "deletion",
    kind: "deletion",
    generation: 1,
    check_id: null,
    body: { scope: "all_data", confirmation: true },
    state: "queued",
    keys: { request: "stable" },
    attempts: 1,
    next_attempt_at: null,
    error: null,
    created_at: "2026-10-11T00:00:00Z",
    phase: 0,
  });
  const rejected = clone(previous);
  rejected.queue[0]!.state = "quarantined";
  rejected.queue[0]!.error = "The data generation has been retired.";
  const next = quarantineGeneration(rejected, -1);
  assert.equal(retiredWithoutReplacement(previous, next), true);
  assert.equal(next.queue[0]!.error, "The data generation has been retired.");
  assert.equal(retiredWithoutReplacement(next, clone(next)), false);
  assert.equal(
    retiredWithoutReplacement(previous, { ...next, generation: 2 }),
    false,
  );
});
