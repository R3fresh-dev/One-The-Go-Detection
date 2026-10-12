import {
  assertBytes,
  clone,
  digest,
  digestText,
  IntegrityError,
  knownKeys,
  requireObject,
  requiredString,
  safeInteger,
} from "./integrity";
import type { ExportSelection, JsonObject } from "./types";
import type { RawKind } from "./rawRecordings";
const uuid =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
  sha = /^[a-f0-9]{64}$/;
const fail = (): never => {
  throw new IntegrityError(
    "RAW_EXPORT_AUTHORITY_INVALID",
    "The separate raw export authority, notice or exact source scope is unsupported.",
  );
};
const time = (value: unknown) => {
  if (
    typeof value !== "string" ||
    !value.endsWith("Z") ||
    !Number.isFinite(Date.parse(value))
  )
    fail();
  return value as string;
};
const hash = (value: unknown) => {
  if (typeof value !== "string" || !sha.test(value)) fail();
  return value as string;
};
const id = (value: unknown) => {
  if (typeof value !== "string" || !uuid.test(value)) fail();
  return value as string;
};
const kind = (value: unknown): RawKind => {
  if (value !== "eye_video" && value !== "ecg_waveform") fail();
  return value as RawKind;
};
export interface RawExportArtifact {
  artifact_id: string;
  session_id: string;
  kind: RawKind;
  size_bytes: number;
  media_type: string;
  retained_until: string;
}
export interface RawExportAuthority {
  authorization_id: string;
  authorization_version: string;
  authorization_sha256: string;
  study_id: string;
  purpose_id: string;
  purpose_text: string;
  expires_at: string;
  max_export_lifetime_seconds: number;
  max_uncompressed_bytes: number;
  max_archive_bytes: number;
  raw_kinds: RawKind[];
  export_notice: { version: string; sha256: string; content: string };
  artifacts: RawExportArtifact[];
  artifacts_next_cursor: string | null;
}
export interface RawExportScope extends JsonObject {
  authorization_id: string;
  authorization_version: string;
  authorization_sha256: string;
  export_notice_version: string;
  export_notice_sha256: string;
  acknowledged_at: string;
  confirmed: true;
  artifact_ids: string[];
}
export interface RawExportPage {
  scopes: RawExportAuthority[];
  next_cursor: string | null;
}
export function parseRawExportAuthorities(
  value: unknown,
): RawExportAuthority[] {
  return parseRawExportPage(value).scopes;
}
export function parseRawExportPage(value: unknown): RawExportPage {
  assertBytes(value, 524_288);
  const body = requireObject(value);
  knownKeys(body, ["schema_version", "scopes", "next_cursor"]);
  if (
    body.schema_version !== "1.0.0" ||
    !Array.isArray(body.scopes) ||
    body.scopes.length > 4
  )
    fail();
  if (body.next_cursor !== null) hash(body.next_cursor);
  const authorities = (body.scopes as unknown[]).map((value: unknown) => {
    const a = requireObject(value);
    knownKeys(a, [
      "authorization_id",
      "authorization_version",
      "authorization_sha256",
      "study_id",
      "purpose_id",
      "purpose_text",
      "expires_at",
      "max_export_lifetime_seconds",
      "max_uncompressed_bytes",
      "max_archive_bytes",
      "raw_kinds",
      "export_notice",
      "artifacts",
      "artifacts_next_cursor",
    ]);
    requiredString(a.authorization_id, 128);
    requiredString(a.authorization_version, 128);
    hash(a.authorization_sha256);
    requiredString(a.study_id, 128);
    requiredString(a.purpose_id, 128);
    requiredString(a.purpose_text, 4096);
    time(a.expires_at);
    if (
      safeInteger(a.max_export_lifetime_seconds, 1) > 86400 ||
      safeInteger(a.max_uncompressed_bytes, 1) > 52_428_800 ||
      safeInteger(a.max_archive_bytes, 1) > 67_108_864 ||
      !Array.isArray(a.raw_kinds) ||
      !a.raw_kinds.length ||
      a.raw_kinds.length > 2 ||
      new Set(a.raw_kinds).size !== a.raw_kinds.length ||
      !Array.isArray(a.artifacts) ||
      a.artifacts.length > 128
    )
      fail();
    (a.raw_kinds as unknown[]).forEach(kind);
    const n = requireObject(a.export_notice);
    knownKeys(n, ["version", "sha256", "content"]);
    requiredString(n.version, 128);
    hash(n.sha256);
    requiredString(n.content, 65_536);
    if (digestText(n.content as string) !== n.sha256) fail();
    const artifacts = (a.artifacts as unknown[]).map((value: unknown) => {
      const r = requireObject(value);
      knownKeys(r, [
        "artifact_id",
        "session_id",
        "kind",
        "size_bytes",
        "media_type",
        "retained_until",
      ]);
      id(r.artifact_id);
      id(r.session_id);
      kind(r.kind);
      if (
        !(a.raw_kinds as string[]).includes(String(r.kind)) ||
        safeInteger(r.size_bytes, 1) >
          (r.kind === "eye_video" ? 64 : 16) * 1024 * 1024 ||
        !["application/octet-stream", "video/mp4", "application/json"].includes(
          String(r.media_type),
        )
      )
        fail();
      time(r.retained_until);
      return clone(r) as unknown as RawExportArtifact;
    });
    if (new Set(artifacts.map((a) => a.artifact_id)).size !== artifacts.length)
      fail();
    if (a.artifacts_next_cursor !== null) id(a.artifacts_next_cursor);
    return { ...clone(a), artifacts } as unknown as RawExportAuthority;
  });
  if (
    new Set(authorities.map((a) => a.authorization_id)).size !==
    authorities.length
  )
    fail();
  return {
    scopes: authorities,
    next_cursor: body.next_cursor as string | null,
  };
}
export function confirmRawExport(
  authority: RawExportAuthority,
  artifactIds: string[],
  selection: ExportSelection,
  acknowledgedAt: string,
): RawExportScope {
  time(acknowledgedAt);
  if (
    Date.parse(authority.expires_at) <= Date.now() ||
    !artifactIds.length ||
    artifactIds.length > 128 ||
    new Set(artifactIds).size !== artifactIds.length
  )
    fail();
  const sources = artifactIds.map((sourceId) => {
    id(sourceId);
    const file = authority.artifacts.find(
      (file) => file.artifact_id === sourceId,
    );
    if (
      !file ||
      Date.parse(file.retained_until) <= Date.now() ||
      (selection.kind !== "all" &&
        !selection.session_ids.includes(file.session_id))
    )
      fail();
    return file!;
  });
  if (
    sources.reduce((size, file) => size + file.size_bytes, 0) >
    authority.max_uncompressed_bytes
  )
    fail();
  return {
    authorization_id: authority.authorization_id,
    authorization_version: authority.authorization_version,
    authorization_sha256: authority.authorization_sha256,
    export_notice_version: authority.export_notice.version,
    export_notice_sha256: authority.export_notice.sha256,
    acknowledged_at: acknowledgedAt,
    confirmed: true,
    artifact_ids: [...artifactIds].sort(),
  };
}
export function parseRawExportManifest(value: unknown): JsonObject {
  assertBytes(value, 262_144);
  const m = requireObject(value);
  knownKeys(m, [
    "schema_version",
    "frozen_sha256",
    "authorization_id",
    "authorization_version",
    "authorization_sha256",
    "study_id",
    "purpose",
    "purpose_id",
    "acknowledged_at",
    "export_notice_version",
    "export_notice_sha256",
    "sources",
  ]);
  if (
    m.schema_version !== "1.0.0" ||
    m.purpose !== "participant_requested_raw_export"
  )
    fail();
  for (const field of [
    "frozen_sha256",
    "authorization_sha256",
    "export_notice_sha256",
  ])
    hash(m[field]);
  for (const field of [
    "authorization_id",
    "authorization_version",
    "study_id",
    "purpose_id",
    "export_notice_version",
  ])
    requiredString(m[field], 128);
  time(m.acknowledged_at);
  if (!Array.isArray(m.sources) || !m.sources.length || m.sources.length > 128)
    fail();
  const ids = new Set();
  let total = 0;
  for (const value of m.sources as unknown[]) {
    const s = requireObject(value);
    knownKeys(s, [
      "artifact_id",
      "session_id",
      "kind",
      "version_id",
      "sha256",
      "size_bytes",
      "media_type",
      "retained_until",
      "path",
    ]);
    id(s.artifact_id);
    id(s.session_id);
    const k = kind(s.kind);
    hash(s.sha256);
    requiredString(s.version_id, 256);
    if (
      s.version_id === "null" ||
      !["application/octet-stream", "video/mp4", "application/json"].includes(
        String(s.media_type),
      ) ||
      typeof s.retained_until !== "number" ||
      !Number.isFinite(s.retained_until) ||
      s.retained_until <= 0 ||
      s.path !== `raw/${k}/${s.artifact_id}.bin` ||
      ids.has(s.artifact_id)
    )
      fail();
    ids.add(s.artifact_id);
    total += safeInteger(s.size_bytes, 1);
    if (total > 52_428_800) fail();
  }
  return clone(m) as JsonObject;
}
export function verifyRawExportReceipt(
  manifest: unknown,
  scope: RawExportScope,
): JsonObject {
  const m = parseRawExportManifest(manifest);
  if (
    [
      "authorization_id",
      "authorization_version",
      "authorization_sha256",
      "export_notice_version",
      "export_notice_sha256",
      "acknowledged_at",
    ].some((key) => m[key] !== scope[key]) ||
    digest(
      (m.sources as JsonObject[]).map((s) => String(s.artifact_id)).sort(),
    ) !== digest([...scope.artifact_ids].sort())
  )
    fail();
  return m;
}
