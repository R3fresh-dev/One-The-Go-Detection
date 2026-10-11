import type { WorkspaceState } from "../core/types";
export interface WorkspaceStore {
  load(): Promise<WorkspaceState | null>;
  save(state: WorkspaceState): Promise<void>;
  clear(): Promise<void>;
  close(): Promise<void>;
  /** Native-only encrypted binary storage. Web never persists participant raw data. */
  writeRaw?(
    id: string,
    bytes: Uint8Array,
    stillCurrent: () => boolean,
  ): Promise<void>;
  /** Commit encrypted bytes and their index in the same SQLCipher transaction. */
  saveWithRaw?(
    state: WorkspaceState,
    id: string,
    bytes: Uint8Array,
    stillCurrent: () => boolean,
  ): Promise<void>;
  /** Delete orphaned, fenced and expired bytes before exposing an unlocked workspace. */
  reconcileRaw?(state: WorkspaceState, at: string): Promise<WorkspaceState>;
  readRaw?(id: string): Promise<Uint8Array | null>;
  deleteRaw?(id: string): Promise<void>;
}
export interface SecureVault {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  remove(key: string): Promise<void>;
}
