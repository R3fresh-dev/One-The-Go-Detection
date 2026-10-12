import { NamespaceGate } from "../core/namespaceGate";
import * as SQLite from "expo-sqlite";
import * as SecureStore from "expo-secure-store";
import * as LocalAuthentication from "expo-local-authentication";
import * as Crypto from "expo-crypto";
import {
  enableSecureWindowAsync,
  protectDatabaseDirectoryAsync,
} from "../../modules/storage-security";
import {
  clone,
  digestText,
  IntegrityError,
  parseBoundedJson,
} from "../core/integrity";
import type { WorkspaceState } from "../core/types";
import type { SecureVault, WorkspaceStore } from "./storage.types";

const initialization = new NamespaceGate();
const secureOptions: SecureStore.SecureStoreOptions = {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
};
export const vault: SecureVault = {
  get: (key) => SecureStore.getItemAsync(key, secureOptions),
  set: (key, value) => SecureStore.setItemAsync(key, value, secureOptions),
  remove: (key) => SecureStore.deleteItemAsync(key, secureOptions),
};
export const newId = (): string => Crypto.randomUUID();
export async function unlockAccount(): Promise<boolean> {
  if (!(await SecureStore.isAvailableAsync()))
    throw new IntegrityError(
      "SECURE_STORAGE_UNAVAILABLE",
      "This device cannot protect account records.",
    );
  if (
    (await LocalAuthentication.getEnrolledLevelAsync()) ===
    LocalAuthentication.SecurityLevel.NONE
  )
    throw new IntegrityError(
      "DEVICE_LOCK_REQUIRED",
      "Set a device passcode or biometric lock before opening account records.",
    );
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Unlock your One The Go records",
    cancelLabel: "Keep locked",
    disableDeviceFallback: false,
    fallbackLabel: "Use device passcode",
  });
  return result.success;
}
export async function openWorkspaceStore(
  workspace: string,
): Promise<WorkspaceStore> {
  return initialization.run(workspace, () =>
    initializeWorkspaceStore(workspace),
  );
}
async function initializeWorkspaceStore(
  workspace: string,
): Promise<WorkspaceStore> {
  if (!(await SecureStore.isAvailableAsync()))
    throw new IntegrityError(
      "SECURE_STORAGE_UNAVAILABLE",
      "Encrypted storage is unavailable. There is no plaintext fallback.",
    );
  const name = `otgd-${digestText(workspace).slice(0, 32)}.db`,
    keyName = `otgd.key.${digestText(workspace)}`;
  const marker = await vault.get(`${keyName}.created`);
  let key = await vault.get(keyName);
  if (!key && marker)
    throw new IntegrityError(
      "STORAGE_KEY_LOST",
      "The encryption key is missing. You can explicitly remove this workspace’s local records.",
    );
  if (!key) {
    key = [...(await Crypto.getRandomBytesAsync(32))]
      .map((n) => n.toString(16).padStart(2, "0"))
      .join("");
    await vault.set(keyName, key);
  }
  if (!/^[a-f0-9]{64}$/.test(key))
    throw new IntegrityError(
      "STORAGE_KEY_INVALID",
      "The encryption key is invalid.",
    );
  const db = await SQLite.openDatabaseAsync(name, { useNewConnection: true });
  try {
    await db.execAsync(`PRAGMA key = "x'${key}'";`);
    const cipher = await db.getFirstAsync<Record<string, unknown>>(
      "PRAGMA cipher_version",
    );
    if (
      !cipher ||
      !Object.values(cipher).some((v) => typeof v === "string" && v.length > 0)
    )
      throw new IntegrityError(
        "SQLCIPHER_REQUIRED",
        "Install the development or release native build with SQLCipher enabled. Expo Go cannot securely open this workspace.",
      );
    await db.execAsync(
      "PRAGMA cipher_memory_security = ON; PRAGMA secure_delete = ON; PRAGMA journal_mode = WAL; CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL); CREATE TABLE IF NOT EXISTS raw_blobs (id TEXT PRIMARY KEY, payload BLOB NOT NULL);",
    );
    const protection = await protectDatabaseDirectoryAsync(
      SQLite.defaultDatabaseDirectory,
    );
    if (!protection.excludedFromBackup)
      throw new IntegrityError(
        "BACKUP_EXCLUSION_REQUIRED",
        "This build cannot exclude private local records from device backup.",
      );
    await enableSecureWindowAsync();
    await vault.set(`${keyName}.created`, "1");
  } catch (error) {
    await db.closeAsync();
    throw error;
  }
  let closed = false;
  const assertOpen = () => {
    if (closed)
      throw new IntegrityError(
        "WORKSPACE_LOCKED",
        "Unlock this workspace before reading records.",
      );
  };
  return {
    async load() {
      assertOpen();
      const row = await db.getFirstAsync<{ payload: string }>(
        "SELECT payload FROM app_state WHERE id=1",
      );
      if (!row) return null;
      const value = parseBoundedJson(
        row.payload,
        268_435_456,
      ) as WorkspaceState;
      if (value.schema_version !== 1 || value.workspace !== workspace)
        throw new IntegrityError(
          "STORE_VERSION",
          "The stored workspace version or owner is unsupported.",
        );
      return value;
    },
    async save(state) {
      assertOpen();
      if (state.workspace !== workspace)
        throw new IntegrityError(
          "WORKSPACE_MISMATCH",
          "Cannot save another account into this store.",
        );
      const payload = JSON.stringify(clone(state));
      await db.withExclusiveTransactionAsync(async (tx) => {
        await tx.runAsync(
          "INSERT INTO app_state(id,payload) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
          payload,
        );
      });
    },
    async writeRaw(id, bytes, stillCurrent) {
      assertOpen();
      if (
        bytes.length < 1 ||
        bytes.length > 64 * 1024 * 1024 ||
        !/^[0-9a-f-]{36}$/i.test(id)
      )
        throw new IntegrityError(
          "RAW_STORAGE_LIMIT",
          "Raw recording is outside its bounded native storage contract.",
        );
      await db.withExclusiveTransactionAsync(async (tx) => {
        if (!stillCurrent())
          throw new IntegrityError(
            "RAW_RECORDING_STOPPED",
            "Recording permission or workspace changed before encrypted storage.",
          );
        const existing = await tx.getFirstAsync<{ id: string }>(
          "SELECT id FROM raw_blobs WHERE id=?",
          id,
        );
        if (existing)
          throw new IntegrityError(
            "IMMUTABLE_RAW_RECORDING",
            "A retained recording cannot be overwritten.",
          );
        await tx.runAsync(
          "INSERT INTO raw_blobs(id,payload) VALUES(?,?)",
          id,
          bytes,
        );
        if (!stillCurrent())
          throw new IntegrityError(
            "RAW_RECORDING_STOPPED",
            "Recording stopped before the encrypted transaction committed.",
          );
      });
    },
    async saveWithRaw(state, id, bytes, stillCurrent) {
      assertOpen();
      const raw = state.rawArtifacts?.find((raw) => raw.local_id === id);
      if (
        state.workspace !== workspace ||
        !raw ||
        raw.state !== "local" ||
        raw.size_bytes !== bytes.length ||
        bytes.length < 1 ||
        bytes.length > 64 * 1024 * 1024 ||
        !/^[0-9a-f-]{36}$/i.test(id)
      )
        throw new IntegrityError(
          "RAW_STORAGE_LIMIT",
          "Encrypted recording bytes require their exact owned metadata in the same transaction.",
        );
      const payload = JSON.stringify(clone(state));
      await db.withExclusiveTransactionAsync(async (tx) => {
        if (!stillCurrent())
          throw new IntegrityError(
            "RAW_RECORDING_STOPPED",
            "Recording stopped before encrypted storage.",
          );
        if (await tx.getFirstAsync("SELECT id FROM raw_blobs WHERE id=?", id))
          throw new IntegrityError(
            "IMMUTABLE_RAW_RECORDING",
            "A retained recording cannot be overwritten.",
          );
        await tx.runAsync(
          "INSERT INTO raw_blobs(id,payload) VALUES(?,?)",
          id,
          bytes,
        );
        await tx.runAsync(
          "INSERT INTO app_state(id,payload) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
          payload,
        );
        if (!stillCurrent())
          throw new IntegrityError(
            "RAW_RECORDING_STOPPED",
            "Recording stopped before the encrypted transaction committed.",
          );
      });
    },
    async reconcileRaw(state, at) {
      assertOpen();
      if (state.workspace !== workspace || !Number.isFinite(Date.parse(at)))
        throw new IntegrityError(
          "WORKSPACE_MISMATCH",
          "Raw cleanup requires this exact workspace and a valid deadline clock.",
        );
      const next = clone(state),
        keep = new Set<string>();
      for (const raw of next.rawArtifacts ?? []) {
        if (
          raw.state === "deleted" ||
          raw.state === "quarantined" ||
          !Number.isFinite(Date.parse(raw.retention_due_at)) ||
          Date.parse(raw.retention_due_at) <= Date.parse(at)
        ) {
          raw.state = "deleted";
          raw.error = null;
        } else keep.add(raw.local_id);
      }
      await db.withExclusiveTransactionAsync(async (tx) => {
        const rows = await tx.getAllAsync<{ id: string }>(
          "SELECT id FROM raw_blobs LIMIT 10001",
        );
        if (rows.length > 10_000)
          throw new IntegrityError(
            "RAW_CLEANUP_LIMIT",
            "The encrypted recording index exceeds its bounded recovery inventory.",
          );
        for (const row of rows)
          if (!keep.has(row.id))
            await tx.runAsync("DELETE FROM raw_blobs WHERE id=?", row.id);
        await tx.runAsync(
          "INSERT INTO app_state(id,payload) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
          JSON.stringify(next),
        );
      });
      await db.execAsync("PRAGMA wal_checkpoint(TRUNCATE);");
      return next;
    },
    async readRaw(id) {
      assertOpen();
      const index = await db.getFirstAsync<{ payload: string }>(
        "SELECT payload FROM app_state WHERE id=1",
      );
      const state = index
          ? (parseBoundedJson(index.payload, 268_435_456) as WorkspaceState)
          : null,
        raw = state?.rawArtifacts?.find((raw) => raw.local_id === id);
      if (
        !raw ||
        !["local", "queued", "uploaded"].includes(raw.state) ||
        !Number.isFinite(Date.parse(raw.retention_due_at)) ||
        Date.parse(raw.retention_due_at) <= Date.now() ||
        state!.rawRecordingFences[raw.study_id]?.includes(raw.artifact_kind)
      )
        return null;
      const row = await db.getFirstAsync<{ payload: Uint8Array }>(
        "SELECT payload FROM raw_blobs WHERE id=?",
        id,
      );
      return row ? new Uint8Array(row.payload) : null;
    },
    async deleteRaw(id) {
      assertOpen();
      await db.withExclusiveTransactionAsync(async (tx) => {
        await tx.runAsync("DELETE FROM raw_blobs WHERE id=?", id);
      });
      await db.execAsync("PRAGMA wal_checkpoint(TRUNCATE);");
    },
    async clear() {
      assertOpen();
      await db.execAsync(
        "DELETE FROM raw_blobs; DELETE FROM app_state; PRAGMA wal_checkpoint(TRUNCATE); VACUUM;",
      );
    },
    async close() {
      if (!closed) {
        closed = true;
        await db.closeAsync();
      }
    },
  };
}
export async function resetLocalWorkspace(workspace: string): Promise<void> {
  return initialization.run(workspace, () => removeWorkspace(workspace));
}
async function removeWorkspace(workspace: string): Promise<void> {
  const suffix = digestText(workspace),
    name = `otgd-${suffix.slice(0, 32)}.db`;
  await SQLite.deleteDatabaseAsync(name);
  await vault.remove(`otgd.key.${suffix}`);
  await vault.remove(`otgd.key.${suffix}.created`);
}
