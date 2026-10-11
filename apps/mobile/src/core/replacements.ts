import {
  clone,
  IntegrityError,
  knownKeys,
  requireObject,
  requiredString,
  safeInteger,
} from "./integrity";
import type { CheckRecord, WorkspaceState } from "./types";

export interface ReplacementLink {
  session_id: string;
  created_at: string;
  state: "processing" | "completed" | "invalid";
}
export interface ReplacementLinksPage {
  schema_version: "1.0.0";
  session_id: string;
  data_generation: number;
  base_snapshot_sha256: string;
  previous: ReplacementLink | null;
  items: ReplacementLink[];
  next_cursor: string | null;
}
export interface ReplacementLinksCache extends ReplacementLinksPage {
  observed_at: string;
}
const uuid = (value: unknown): string => {
  const text = requiredString(value);
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      text,
    )
  )
    throw new IntegrityError(
      "REPLACEMENT_LINK_INVALID",
      "A replacement link identity is unsupported.",
    );
  return text;
};
function link(value: unknown): ReplacementLink {
  const object = requireObject(value);
  knownKeys(object, ["session_id", "created_at", "state"]);
  const session_id = uuid(object.session_id),
    created_at = requiredString(object.created_at);
  if (
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(created_at) ||
    !Number.isFinite(Date.parse(created_at)) ||
    !["processing", "completed", "invalid"].includes(String(object.state))
  )
    throw new IntegrityError(
      "REPLACEMENT_LINK_INVALID",
      "A replacement link time or frozen state is unsupported.",
    );
  return {
    session_id,
    created_at,
    state: object.state as ReplacementLink["state"],
  };
}
export function parseReplacementLinks(
  value: unknown,
  check: CheckRecord,
): ReplacementLinksPage {
  const object = requireObject(value);
  knownKeys(object, [
    "schema_version",
    "session_id",
    "data_generation",
    "base_snapshot_sha256",
    "previous",
    "items",
    "next_cursor",
  ]);
  if (
    !check.frozen ||
    !check.snapshot_sha256 ||
    !/^[a-f0-9]{64}$/.test(check.snapshot_sha256) ||
    object.schema_version !== "1.0.0" ||
    object.session_id !== check.id ||
    safeInteger(object.data_generation, 1) !== check.generation ||
    object.base_snapshot_sha256 !== check.snapshot_sha256 ||
    !Array.isArray(object.items) ||
    object.items.length > 100
  )
    throw new IntegrityError(
      "REPLACEMENT_LINK_BINDING",
      "These links do not match the current saved check and data generation.",
    );
  const previous = object.previous === null ? null : link(object.previous),
    items = object.items.map(link),
    cursor = object.next_cursor;
  if (
    (previous &&
      previous.session_id !== check.snapshot.supersedes_session_id) ||
    previous?.session_id === check.id ||
    items.some(
      (item) =>
        item.session_id === check.id ||
        item.session_id === previous?.session_id,
    ) ||
    new Set(items.map((item) => item.session_id)).size !== items.length ||
    (cursor !== null &&
      (typeof cursor !== "string" ||
        cursor.length < 1 ||
        cursor.length > 1024 ||
        !/^[\x20-\x7e]+$/.test(cursor) ||
        items.length === 0))
  )
    throw new IntegrityError(
      "REPLACEMENT_LINK_INTEGRITY",
      "The service returned duplicate, unsupported or inconsistent replacement navigation.",
    );
  return {
    schema_version: "1.0.0",
    session_id: check.id,
    data_generation: check.generation,
    base_snapshot_sha256: check.snapshot_sha256!,
    previous,
    items,
    next_cursor: cursor as string | null,
  };
}
export function mergeReplacementPage(
  previous: ReplacementLinksCache | undefined,
  page: ReplacementLinksPage,
  more: boolean,
  observedAt: string,
): ReplacementLinksCache {
  if (!more || !previous) return { ...clone(page), observed_at: observedAt };
  if (
    previous.session_id !== page.session_id ||
    previous.data_generation !== page.data_generation ||
    previous.base_snapshot_sha256 !== page.base_snapshot_sha256 ||
    previous.previous?.session_id !== page.previous?.session_id ||
    page.items.some((item) =>
      previous.items.some((old) => old.session_id === item.session_id),
    )
  )
    throw new IntegrityError(
      "REPLACEMENT_PAGE_CHANGED",
      "Replacement navigation changed while loading. Refresh the first page; existing records remain unchanged.",
    );
  if (previous.items.length + page.items.length > 500)
    throw new IntegrityError(
      "REPLACEMENT_CACHE_LIMIT",
      "This view has reached 500 cached links. Use History to find additional checks; the service list has not been marked complete.",
    );
  return {
    ...clone(page),
    items: [...clone(previous.items), ...clone(page.items)],
    observed_at: observedAt,
  };
}
export function localReplacementChecks(
  state: WorkspaceState,
  check: CheckRecord,
): { previous: CheckRecord | null; items: CheckRecord[] } {
  const eligible = (record: CheckRecord) =>
    record.workspace === state.workspace &&
    record.generation === state.generation &&
    record.delivery !== "quarantined" &&
    record.frozen;
  if (!eligible(check)) return { previous: null, items: [] };
  return {
    previous:
      state.checks.find(
        (record) =>
          eligible(record) &&
          record.id === check.snapshot.supersedes_session_id,
      ) ?? null,
    items: state.checks
      .filter(
        (record) =>
          eligible(record) &&
          record.snapshot.supersedes_session_id === check.id &&
          record.id !== check.id,
      )
      .sort(
        (a, b) =>
          b.snapshot.created_at.localeCompare(a.snapshot.created_at) ||
          b.id.localeCompare(a.id),
      ),
  };
}
export function verifyReplacementTarget(
  base: CheckRecord,
  target: CheckRecord,
  direction: "previous" | "replacement",
): void {
  if (
    !base.frozen ||
    !target.frozen ||
    base.workspace !== target.workspace ||
    base.generation !== target.generation ||
    base.delivery === "quarantined" ||
    target.delivery === "quarantined" ||
    base.id === target.id ||
    (direction === "previous"
      ? base.snapshot.supersedes_session_id !== target.id
      : target.snapshot.supersedes_session_id !== base.id)
  )
    throw new IntegrityError(
      "REPLACEMENT_LINK_INTEGRITY",
      "The selected check does not have the expected immutable acquisition relationship.",
    );
}
