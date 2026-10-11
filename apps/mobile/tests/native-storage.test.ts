import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID, randomBytes } from "node:crypto";
import { emptyWorkspace } from "../src/core/domain";
import { deferred } from "./support/customer";
require("./support/runtime.cjs");
const Module = require("node:module"),
  originalLoad = Module._load;
const keys = new Map<string, string>(),
  rows = new Map<
    string,
    { payload: string | null; blobs: Map<string, Uint8Array> }
  >();
let available = true,
  cipher = true,
  excluded = true,
  randomCalls = 0;
let firstRead: ReturnType<typeof deferred<string | null>> | null = null;
const calls: { sql: string; params: any[] }[] = [];
function connection(name: string) {
  const row = rows.get(name) ?? { payload: null, blobs: new Map() };
  rows.set(name, row);
  let closed = false;
  const handle: any = {
    execAsync: async (sql: string) => {
      assert.equal(closed, false);
      calls.push({ sql, params: [] });
      if (sql.includes("DELETE FROM raw_blobs")) row.blobs.clear();
      if (sql.includes("DELETE FROM app_state")) row.payload = null;
    },
    getFirstAsync: async (sql: string, ...params: any[]) => {
      assert.equal(closed, false);
      if (sql === "PRAGMA cipher_version")
        return cipher ? { cipher_version: "test-boundary-sqlcipher" } : null;
      if (sql.includes("SELECT payload FROM app_state"))
        return row.payload ? { payload: row.payload } : null;
      if (sql.includes("FROM raw_blobs")) {
        const payload = row.blobs.get(params[0]);
        return payload ? { id: params[0], payload: payload.slice() } : null;
      }
      return null;
    },
    getAllAsync: async (sql: string) => {
      assert.equal(sql, "SELECT id FROM raw_blobs LIMIT 10001");
      return [...row.blobs.keys()].map((id) => ({ id }));
    },
    runAsync: async (sql: string, ...params: any[]) => {
      assert.equal(closed, false);
      calls.push({ sql, params });
      if (sql.includes("INSERT INTO app_state")) row.payload = params[0];
      if (sql.includes("INSERT INTO raw_blobs"))
        row.blobs.set(params[0], params[1].slice());
      if (sql.includes("DELETE FROM raw_blobs WHERE"))
        row.blobs.delete(params[0]);
    },
    withExclusiveTransactionAsync: async (
      callback: (tx: any) => Promise<void>,
    ) => {
      const snapshot = { payload: row.payload, blobs: new Map(row.blobs) };
      try {
        await callback(handle);
      } catch (error) {
        row.payload = snapshot.payload;
        row.blobs = snapshot.blobs;
        throw error;
      }
    },
    closeAsync: async () => {
      closed = true;
    },
  };
  return handle;
}
Module._load = function (specifier: string, parent: any, isMain: any) {
  if (specifier === "expo-sqlite")
    return {
      defaultDatabaseDirectory: "/private/test-db",
      openDatabaseAsync: async (name: string) => connection(name),
      deleteDatabaseAsync: async (name: string) => {
        rows.delete(name);
      },
    };
  if (specifier === "expo-secure-store")
    return {
      WHEN_UNLOCKED_THIS_DEVICE_ONLY: 1,
      isAvailableAsync: async () => available,
      getItemAsync: async (key: string) => {
        if (firstRead) {
          const pending = firstRead;
          firstRead = null;
          return pending.promise;
        }
        return keys.get(key) ?? null;
      },
      setItemAsync: async (key: string, value: string) => {
        keys.set(key, value);
      },
      deleteItemAsync: async (key: string) => {
        keys.delete(key);
      },
    };
  if (specifier === "expo-local-authentication")
    return {
      SecurityLevel: { NONE: 0 },
      getEnrolledLevelAsync: async () => 1,
      authenticateAsync: async () => ({ success: true }),
    };
  if (specifier === "expo-crypto")
    return {
      randomUUID,
      getRandomBytesAsync: async (size: number) => {
        randomCalls++;
        return randomBytes(size);
      },
    };
  if (specifier === "../../modules/storage-security")
    return {
      protectDatabaseDirectoryAsync: async () => ({
        excludedFromBackup: excluded,
      }),
      enableSecureWindowAsync: async () => {},
    };
  return originalLoad.call(this, specifier, parent, isMain);
};
const storage =
  require("../src/platform/storage.native") as typeof import("../src/platform/storage.native");

test("concurrent native partition initialization keeps one keystore key and separate handles, then reopened records remain readable", async () => {
  const workspace = "native-unit-account:" + randomUUID(),
    read = deferred<string | null>();
  firstRead = read;
  const count = randomCalls;
  const first = storage.openWorkspaceStore(workspace),
    second = storage.openWorkspaceStore(workspace);
  read.resolve(null);
  const [a, b] = await Promise.all([first, second]);
  assert.equal(randomCalls - count, 1);
  const state = emptyWorkspace(workspace, new Date().toISOString());
  await a.save(state);
  await a.close();
  assert.deepEqual(await b.load(), state);
  await b.close();
  const reopened = await storage.openWorkspaceStore(workspace);
  assert.deepEqual(await reopened.load(), state);
  await reopened.close();
  await storage.resetLocalWorkspace(workspace);
});

test("native raw writes bind binary bytes inside SQLCipher and rollback after a privacy fence without plaintext paths or overwrite", async () => {
  const workspace = "native-unit-raw:" + randomUUID(),
    store = await storage.openWorkspaceStore(workspace),
    id = randomUUID(),
    bytes = new Uint8Array([1, 2, 3, 4]);
  assert.ok(store.writeRaw && store.readRaw && store.deleteRaw);
  const state = emptyWorkspace(workspace, new Date().toISOString());
  state.rawArtifacts = [
    {
      local_id: id,
      state: "local",
      size_bytes: bytes.length,
      retention_due_at: new Date(Date.now() + 60_000).toISOString(),
      study_id: "test-owned-study",
      artifact_kind: "eye_video",
    } as any,
  ];
  await store.saveWithRaw!(state, id, bytes, () => true);
  assert.deepEqual(await store.readRaw(id), bytes);
  assert.ok(
    calls.some(
      (call) =>
        call.sql === "INSERT INTO raw_blobs(id,payload) VALUES(?,?)" &&
        call.params[1] instanceof Uint8Array,
    ),
  );
  await assert.rejects(
    store.writeRaw(id, new Uint8Array([9]), () => true),
    /cannot be overwritten/,
  );
  let checks = 0;
  const stoppedId = randomUUID();
  await assert.rejects(
    store.writeRaw(stoppedId, bytes, () => ++checks === 1),
    /before the encrypted transaction committed/,
  );
  assert.equal(await store.readRaw(stoppedId), null);
  await assert.rejects(
    store.writeRaw(randomUUID(), bytes, () => false),
    /before encrypted storage/,
  );
  await store.deleteRaw(id);
  assert.equal(await store.readRaw(id), null);
  await store.writeRaw(randomUUID(), bytes, () => true);
  await store.clear();
  await store.close();
  await assert.rejects(store.readRaw(id), /Unlock this workspace/);
  await storage.resetLocalWorkspace(workspace);
});

test("native account storage fails closed when key storage, cipher support or backup exclusion is unavailable", async () => {
  const workspace = "native-unit-deny:" + randomUUID();
  available = false;
  await assert.rejects(
    storage.openWorkspaceStore(workspace),
    /no plaintext fallback/,
  );
  available = true;
  cipher = false;
  await assert.rejects(storage.openWorkspaceStore(workspace), /SQLCipher/);
  cipher = true;
  excluded = false;
  await assert.rejects(
    storage.openWorkspaceStore(workspace),
    /exclude private local records/,
  );
  excluded = true;
  await storage.resetLocalWorkspace(workspace);
});

test("raw bytes and index rollback together on a workspace switch and expiry/orphan reconciliation completes before reopened reads", async () => {
  const workspace = "native-unit-atomic:" + randomUUID(),
    store = await storage.openWorkspaceStore(workspace),
    id = randomUUID(),
    bytes = new Uint8Array([3, 4, 5]);
  const state = emptyWorkspace(workspace, new Date().toISOString());
  state.rawArtifacts = [
    {
      local_id: id,
      state: "local",
      size_bytes: bytes.length,
      retention_due_at: new Date(Date.now() + 60_000).toISOString(),
      study_id: "test-study",
      artifact_kind: "eye_video",
    } as any,
  ];
  let guardCalls = 0;
  await assert.rejects(
    store.saveWithRaw!(state, id, bytes, () => ++guardCalls === 1),
    /before the encrypted transaction committed/,
  );
  assert.equal(await store.load(), null);
  assert.equal(await store.readRaw!(id), null);
  await store.saveWithRaw!(state, id, bytes, () => true);
  assert.deepEqual((await store.load())!.rawArtifacts, state.rawArtifacts);
  const orphan = randomUUID();
  await store.writeRaw!(orphan, bytes, () => true);
  assert.equal(await store.readRaw!(orphan), null);
  const expired = new Date(Date.now() + 120_000).toISOString();
  const reconciled = await store.reconcileRaw!(state, expired);
  assert.equal(reconciled.rawArtifacts![0]!.state, "deleted");
  assert.equal(await store.readRaw!(id), null);
  assert.ok(
    calls.some(
      (call) =>
        call.sql === "DELETE FROM raw_blobs WHERE id=?" &&
        call.params[0] === orphan,
    ),
  );
  await store.close();
  const reopened = await storage.openWorkspaceStore(workspace);
  assert.equal((await reopened.load())!.rawArtifacts![0]!.state, "deleted");
  await reopened.close();
  await storage.resetLocalWorkspace(workspace);
});
