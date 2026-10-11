/** Serializes initialization and removal of a named private storage partition.
 * Separate callers keep separate handles; only key and database setup are shared. */
export class NamespaceGate {
  private tails = new Map<string, Promise<unknown>>();
  async run<T>(namespace: string, operation: () => Promise<T>): Promise<T> {
    const previous = this.tails.get(namespace) ?? Promise.resolve();
    const next = previous.catch(() => {}).then(operation);
    this.tails.set(namespace, next);
    try {
      return await next;
    } finally {
      if (this.tails.get(namespace) === next) this.tails.delete(namespace);
    }
  }
}
