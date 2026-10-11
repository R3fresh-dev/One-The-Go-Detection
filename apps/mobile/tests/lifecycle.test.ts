import test from "node:test";
import assert from "node:assert/strict";
import {
  SerializedVault,
  refreshTokenForGrant,
} from "../src/core/serializedVault";
import {
  AuthorizationAttemptGuard,
  RunStopGate,
  TerminalEvidenceGate,
} from "../src/core/operationGuards";

function deferred() {
  let resolve!: () => void;
  const pending = new Promise<void>((r) => {
    resolve = r;
  });
  return { pending, resolve };
}

test("sign-out removal finishes after an already-started OS credential write", async () => {
  const entered = deferred(),
    release = deferred();
  let stored: string | null = null;
  const order: string[] = [];
  const vault = new SerializedVault({
    get: async () => stored,
    set: async (_key, value) => {
      entered.resolve();
      await release.pending;
      stored = value;
      order.push("set");
    },
    remove: async () => {
      stored = null;
      order.push("remove");
    },
  });
  const write = vault.set("session", "old-account");
  await entered.pending;
  const clear = vault.remove("session");
  release.resolve();
  await Promise.all([write, clear]);
  assert.equal(await vault.get("session"), null);
  assert.deepEqual(order, ["set", "remove"]);
});

test("a queued stale identity update cannot restore credentials after invalidation", async () => {
  const release = deferred();
  let current = true;
  const values: string[] = [];
  const vault = new SerializedVault({
    get: async () => null,
    set: async (_key, value) => {
      if (value === "first") await release.pending;
      values.push(value);
    },
    remove: async () => {
      values.length = 0;
    },
  });
  const first = vault.set("session", "first");
  await Promise.resolve();
  const stale = vault.set("session", "stale-update", () => current);
  current = false;
  const clear = vault.remove("session");
  release.resolve();
  await Promise.all([first, stale, clear]);
  assert.deepEqual(values, []);
});

test("only a same-session refresh grant can retain an omitted refresh token", () => {
  assert.equal(
    refreshTokenForGrant(
      "authorization_code",
      undefined,
      "prior-account-token",
    ),
    null,
  );
  assert.equal(
    refreshTokenForGrant("authorization_code", "", "prior-account-token"),
    null,
  );
  assert.equal(
    refreshTokenForGrant("refresh_token", undefined, "captured-same-session"),
    "captured-same-session",
  );
  assert.equal(
    refreshTokenForGrant("refresh_token", "rotated", "captured-same-session"),
    "rotated",
  );
});

test("PKCE attempts expire at ten minutes, reject repeated callbacks and invalidate on logout/new login", () => {
  const guard = new AuthorizationAttemptGuard(),
    first = guard.begin(1_000);
  guard.consume(first, 600_999);
  assert.throws(() => guard.consume(first, 600_999), /already used/);
  const expired = guard.begin(1_000);
  assert.throws(() => guard.consume(expired, 601_000), /expired/);
  const signedOut = guard.begin(2_000);
  guard.invalidate();
  assert.throws(() => guard.consume(signedOut, 2_001), /canceled/);
  const superseded = guard.begin(3_000);
  guard.begin(3_001);
  assert.throws(() => guard.consume(superseded, 3_002), /canceled/);
});

test("native callback and cancellation receipt share one durable terminal write while persistence is delayed", async () => {
  const gate = new TerminalEvidenceGate(),
    release = deferred();
  let count = 0;
  const callback = gate.persist("run", "exact-terminal-digest", async () => {
    count++;
    await release.pending;
  });
  const receipt = gate.persist("run", "exact-terminal-digest", async () => {
    count++;
  });
  assert.equal(callback, receipt);
  await Promise.resolve();
  assert.equal(count, 1);
  await assert.rejects(
    gate.persist("run", "changed-terminal-digest", async () => {}),
    /two different terminal/,
  );
  release.resolve();
  await Promise.all([callback, receipt]);
  assert.equal(count, 1);
});

test("failed terminal storage remains retryable using the native cached receipt", async () => {
  const gate = new TerminalEvidenceGate();
  let count = 0;
  await assert.rejects(
    gate.persist("run", "digest", async () => {
      count++;
      throw new Error("disk temporarily unavailable");
    }),
  );
  await gate.persist("run", "digest", async () => {
    count++;
  });
  assert.equal(count, 2);
});

test("concurrent route/background stops issue native cancel immediately and wait for terminal persistence", async () => {
  const gate = new RunStopGate(),
    nativeStopped = deferred(),
    persisted = deferred();
  const order: string[] = [];
  const stop = () =>
    gate.run("run", async () => {
      order.push("native-cancel-requested");
      await nativeStopped.pending;
      order.push("native-stopped");
      await persisted.pending;
      order.push("persisted");
    });
  const background = stop(),
    navigation = stop();
  assert.equal(background, navigation);
  assert.deepEqual(order, ["native-cancel-requested"]);
  nativeStopped.resolve();
  await Promise.resolve();
  assert.deepEqual(order, ["native-cancel-requested", "native-stopped"]);
  persisted.resolve();
  await Promise.all([background, navigation]);
  assert.deepEqual(order, [
    "native-cancel-requested",
    "native-stopped",
    "persisted",
  ]);
});
