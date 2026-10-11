import { IntegrityError } from "./integrity";
import type { WorkspaceState } from "./types";

/** A 410 may retire the cached generation before its replacement number is known. */
export function retiredWithoutReplacement(
  previous: WorkspaceState,
  next: WorkspaceState,
): boolean {
  return (
    next.generation === previous.generation &&
    next.capabilities === null &&
    (next.queue.some(
      (item) =>
        item.state === "quarantined" &&
        previous.queue.find((old) => old.id === item.id)?.state !==
          "quarantined",
    ) ||
      next.checks.some(
        (check) =>
          check.delivery === "quarantined" &&
          previous.checks.find((old) => old.id === check.id)?.delivery !==
            "quarantined",
      ))
  );
}

export interface WorkspaceStamp {
  epoch: string;
  fence: number;
  authFlow: number;
  workspace: string | null;
  issuer: string | null;
  accountRef: string | null;
  generation: number | null;
  unlocked: boolean;
  foreground: boolean;
}

/** Capture before the first external await; checking only when commit starts is too late. */
export function captureWorkspaceScope(read: () => WorkspaceStamp): {
  current: () => boolean;
  assertCurrent: () => void;
  wait: <T>(pending: Promise<T>) => Promise<T>;
} {
  const captured = { ...read() };
  const current = () => {
    const value = read();
    return (
      captured.unlocked &&
      value.unlocked &&
      captured.foreground &&
      value.foreground &&
      (Object.keys(captured) as (keyof WorkspaceStamp)[]).every(
        (key) => value[key] === captured[key],
      )
    );
  };
  const assertCurrent = () => {
    if (!current())
      throw new IntegrityError(
        "WORKSPACE_CHANGED",
        "The response was discarded because the account, data generation or local workspace changed.",
      );
  };
  return {
    current,
    assertCurrent,
    wait: async <T>(pending: Promise<T>) => {
      try {
        const value = await pending;
        assertCurrent();
        return value;
      } catch (error) {
        assertCurrent();
        throw error;
      }
    },
  };
}
