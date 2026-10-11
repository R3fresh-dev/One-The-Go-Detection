import type { SecureVault } from "../platform/storage.types";

/** A removal waits for any earlier OS keystore write; old writes cannot finish after sign-out. */
export class SerializedVault implements SecureVault {
  private tail: Promise<void> = Promise.resolve();
  constructor(private readonly delegate: SecureVault) {}
  async get(key: string): Promise<string | null> {
    await this.tail.catch(() => {});
    return this.delegate.get(key);
  }
  set(
    key: string,
    value: string,
    stillCurrent: () => boolean = () => true,
  ): Promise<void> {
    return this.enqueue(async () => {
      if (stillCurrent()) await this.delegate.set(key, value);
    });
  }
  remove(key: string): Promise<void> {
    return this.enqueue(() => this.delegate.remove(key));
  }
  private enqueue(operation: () => Promise<void>): Promise<void> {
    const next = this.tail.catch(() => {}).then(operation);
    this.tail = next;
    return next;
  }
}

export function refreshTokenForGrant(
  grantType: string,
  responseToken: unknown,
  capturedRefreshToken: string | null,
): string | null {
  if (typeof responseToken === "string" && responseToken.length)
    return responseToken;
  return grantType === "refresh_token" ? capturedRefreshToken : null;
}
