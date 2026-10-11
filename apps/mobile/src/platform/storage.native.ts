import * as SQLite from 'expo-sqlite';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';
import * as Crypto from 'expo-crypto';
import { enableSecureWindowAsync, protectDatabaseDirectoryAsync } from '../../modules/storage-security';
import { clone, digestText, IntegrityError, parseBoundedJson } from '../core/integrity';
import type { WorkspaceState } from '../core/types';
import type { SecureVault, WorkspaceStore } from './storage.types';

const secureOptions: SecureStore.SecureStoreOptions = { keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY };
export const vault: SecureVault = {
  get: key => SecureStore.getItemAsync(key, secureOptions),
  set: (key, value) => SecureStore.setItemAsync(key, value, secureOptions),
  remove: key => SecureStore.deleteItemAsync(key, secureOptions)
};
export const newId = (): string => Crypto.randomUUID();
export async function unlockAccount(): Promise<boolean> {
  if (!(await SecureStore.isAvailableAsync())) throw new IntegrityError('SECURE_STORAGE_UNAVAILABLE', 'This device cannot protect account records.');
  if (await LocalAuthentication.getEnrolledLevelAsync() === LocalAuthentication.SecurityLevel.NONE) throw new IntegrityError('DEVICE_LOCK_REQUIRED', 'Set a device passcode or biometric lock before opening account records.');
  const result = await LocalAuthentication.authenticateAsync({ promptMessage: 'Unlock your One The Go records', cancelLabel: 'Keep locked', disableDeviceFallback: false, fallbackLabel: 'Use device passcode' });
  return result.success;
}
export async function openWorkspaceStore(workspace: string): Promise<WorkspaceStore> {
  if (!(await SecureStore.isAvailableAsync())) throw new IntegrityError('SECURE_STORAGE_UNAVAILABLE', 'Encrypted storage is unavailable. There is no plaintext fallback.');
  const name = `otgd-${digestText(workspace).slice(0, 32)}.db`, keyName = `otgd.key.${digestText(workspace)}`;
  const marker = await vault.get(`${keyName}.created`);
  let key = await vault.get(keyName);
  if (!key && marker) throw new IntegrityError('STORAGE_KEY_LOST', 'The encryption key is missing. You can explicitly remove this workspace’s local records.');
  if (!key) { key = [...await Crypto.getRandomBytesAsync(32)].map(n => n.toString(16).padStart(2, '0')).join(''); await vault.set(keyName, key); }
  if (!/^[a-f0-9]{64}$/.test(key)) throw new IntegrityError('STORAGE_KEY_INVALID', 'The encryption key is invalid.');
  const db = await SQLite.openDatabaseAsync(name, { useNewConnection: true });
  try {
    await db.execAsync(`PRAGMA key = "x'${key}'";`);
    const cipher = await db.getFirstAsync<Record<string, unknown>>('PRAGMA cipher_version');
    if (!cipher || !Object.values(cipher).some(v => typeof v === 'string' && v.length > 0)) throw new IntegrityError('SQLCIPHER_REQUIRED', 'Install the development or release native build with SQLCipher enabled. Expo Go cannot securely open this workspace.');
    await db.execAsync('PRAGMA cipher_memory_security = ON; PRAGMA secure_delete = ON; PRAGMA journal_mode = WAL; CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL);');
    const protection = await protectDatabaseDirectoryAsync(SQLite.defaultDatabaseDirectory);
    if (!protection.excludedFromBackup) throw new IntegrityError('BACKUP_EXCLUSION_REQUIRED', 'This build cannot exclude private local records from device backup.');
    await enableSecureWindowAsync();
    await vault.set(`${keyName}.created`, '1');
  } catch (error) { await db.closeAsync(); throw error; }
  let closed = false;
  const assertOpen = () => { if (closed) throw new IntegrityError('WORKSPACE_LOCKED', 'Unlock this workspace before reading records.'); };
  return {
    async load() { assertOpen(); const row = await db.getFirstAsync<{ payload: string }>('SELECT payload FROM app_state WHERE id=1'); if (!row) return null; const value = parseBoundedJson(row.payload, 268_435_456) as WorkspaceState; if (value.schema_version !== 1 || value.workspace !== workspace) throw new IntegrityError('STORE_VERSION', 'The stored workspace version or owner is unsupported.'); return value; },
    async save(state) { assertOpen(); if (state.workspace !== workspace) throw new IntegrityError('WORKSPACE_MISMATCH', 'Cannot save another account into this store.'); const payload = JSON.stringify(clone(state)); await db.withExclusiveTransactionAsync(async tx => { await tx.runAsync('INSERT INTO app_state(id,payload) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload', payload); }); },
    async clear() { assertOpen(); await db.execAsync('DELETE FROM app_state; PRAGMA wal_checkpoint(TRUNCATE); VACUUM;'); },
    async close() { if (!closed) { closed = true; await db.closeAsync(); } }
  };
}
export async function resetLocalWorkspace(workspace: string): Promise<void> {
  const suffix = digestText(workspace), name = `otgd-${suffix.slice(0, 32)}.db`;
  await SQLite.deleteDatabaseAsync(name); await vault.remove(`otgd.key.${suffix}`); await vault.remove(`otgd.key.${suffix}.created`);
}
