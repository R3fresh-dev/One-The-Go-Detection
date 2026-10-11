import { IntegrityError } from "./integrity";

/** Both the native event and its cancellation receipt may deliver the same terminal ledger. */
export class TerminalEvidenceGate {
  private entry: {
    runId: string;
    fingerprint: string;
    pending: Promise<void>;
  } | null = null;

  persist(
    runId: string,
    fingerprint: string,
    operation: () => Promise<void>,
  ): Promise<void> {
    if (this.entry?.runId === runId) {
      if (this.entry.fingerprint !== fingerprint)
        return Promise.reject(
          new IntegrityError(
            "NATIVE_TERMINAL_CONFLICT",
            "The native run returned two different terminal records.",
          ),
        );
      return this.entry.pending;
    }
    const pending = Promise.resolve().then(operation);
    const entry = { runId, fingerprint, pending };
    this.entry = entry;
    void pending.catch(() => {
      if (this.entry === entry) this.entry = null;
    });
    return pending;
  }

  pending(runId: string): Promise<void> | null {
    return this.entry?.runId === runId ? this.entry.pending : null;
  }
}

/** Route changes, backgrounding and explicit cancellation join one immediate stop request. */
export class RunStopGate {
  private entry: { runId: string; pending: Promise<void> } | null = null;

  run(runId: string, operation: () => Promise<void>): Promise<void> {
    if (this.entry?.runId === runId) return this.entry.pending;
    if (this.entry)
      return Promise.reject(
        new IntegrityError(
          "STOP_IN_PROGRESS",
          "A previous acquisition is still stopping.",
        ),
      );
    // Invoke now: native cancellation must be requested before any radio or storage wait.
    const pending = operation();
    const entry = { runId, pending };
    this.entry = entry;
    void pending.then(
      () => {
        if (this.entry === entry) this.entry = null;
      },
      () => {
        if (this.entry === entry) this.entry = null;
      },
    );
    return pending;
  }
}

export interface AuthorizationAttempt {
  id: number;
  expiresAt: number;
  consumed: boolean;
}

/** A PKCE code can be consumed once, for this login attempt, within ten minutes. */
export class AuthorizationAttemptGuard {
  private generation = 0;
  begin(now: number): AuthorizationAttempt {
    return { id: ++this.generation, expiresAt: now + 600_000, consumed: false };
  }
  invalidate(): void {
    this.generation++;
  }
  assertCurrent(attempt: AuthorizationAttempt, now: number): void {
    if (attempt.id !== this.generation || now >= attempt.expiresAt)
      throw new IntegrityError(
        "OAUTH_ATTEMPT_EXPIRED",
        "This sign-in attempt expired or was canceled. Start sign-in again.",
      );
  }
  consume(attempt: AuthorizationAttempt, now: number): void {
    this.assertCurrent(attempt, now);
    if (attempt.consumed)
      throw new IntegrityError(
        "OAUTH_CODE_REPLAY",
        "This sign-in callback was already used. Start sign-in again.",
      );
    attempt.consumed = true;
  }
}
