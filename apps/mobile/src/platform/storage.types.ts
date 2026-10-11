import type { WorkspaceState } from '../core/types';
export interface WorkspaceStore { load(): Promise<WorkspaceState | null>; save(state: WorkspaceState): Promise<void>; clear(): Promise<void>; close(): Promise<void> }
export interface SecureVault { get(key: string): Promise<string | null>; set(key: string, value: string): Promise<void>; remove(key: string): Promise<void> }
