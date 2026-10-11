/** In-memory browsing position only; never carried across workspace epochs or persisted with exports. */
export interface HistoryView {
  filter: "all" | "synthetic" | "measurement" | "pending";
  search: string;
  from: string;
  to: string;
  selected: string[];
  selectionMode: boolean;
  scrollY: number;
}
const fresh = (): HistoryView => ({
  filter: "all",
  search: "",
  from: "",
  to: "",
  selected: [],
  selectionMode: false,
  scrollY: 0,
});
export class HistoryViewMemory {
  private entries = new WeakMap<object, { epoch: string; view: HistoryView }>();
  read(owner: object, epoch: string): HistoryView {
    let entry = this.entries.get(owner);
    if (!entry || entry.epoch !== epoch) {
      entry = { epoch, view: fresh() };
      this.entries.set(owner, entry);
    }
    return { ...entry.view, selected: [...entry.view.selected] };
  }
  update(
    owner: object,
    epoch: string,
    patch: Partial<HistoryView>,
  ): HistoryView {
    const view = { ...this.read(owner, epoch), ...patch };
    view.selected = [...view.selected].slice(0, 500);
    view.scrollY = Number.isFinite(view.scrollY)
      ? Math.max(0, view.scrollY)
      : 0;
    this.entries.set(owner, { epoch, view });
    return this.read(owner, epoch);
  }
}
export const historyViews = new HistoryViewMemory();
export function sortHistoryRows<T extends { id: string; createdAt: string }>(
  rows: T[],
): T[] {
  return [...rows].sort((a, b) => {
    const time = Date.parse(b.createdAt) - Date.parse(a.createdAt);
    return Number.isFinite(time) && time !== 0
      ? time
      : b.id.localeCompare(a.id, "en");
  });
}
export function pendingSync(state: string): boolean {
  return [
    "queued",
    "registering",
    "uploading_evidence",
    "uploading_snapshot",
    "finalizing",
    "awaiting_result",
    "retry_wait",
    "auth_required",
    "blocked",
    "conflict",
  ].includes(state);
}
