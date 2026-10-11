// Web application preview: memory only. No persistent account-security claim.
import { clone } from '../core/integrity';
import type { WorkspaceState } from '../core/types';
import type { SecureVault, WorkspaceStore } from './storage.types';
const records = new Map<string, WorkspaceState>();
const secrets = new Map<string, string>();
export const vault: SecureVault = { get: async key => secrets.get(key) ?? null, set: async (key, value) => { secrets.set(key, value); }, remove: async key => { secrets.delete(key); } };
export const newId = (): string => globalThis.crypto.randomUUID();
export async function unlockAccount(): Promise<boolean> { return true; }
export async function openWorkspaceStore(workspace: string): Promise<WorkspaceStore> { let closed = false; return { load: async () => closed ? null : clone(records.get(workspace) ?? null), save: async state => { if (closed) throw new Error('Workspace is locked'); if (state.workspace !== workspace) throw new Error('Workspace mismatch'); records.set(workspace, clone(state)); }, clear: async () => { records.delete(workspace); }, close: async () => { closed = true; } }; }
export async function resetLocalWorkspace(workspace: string): Promise<void> { records.delete(workspace); }
