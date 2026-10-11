import { zipSync, unzipSync } from "fflate";
import {
  canonicalJson,
  digest,
  digestBytes,
  digestText,
  IntegrityError,
  knownKeys,
  parseBoundedJson,
  requireObject,
  utf8,
} from "../core/integrity";
import {
  selectExportChecks,
  validateSelection,
  validateSnapshot,
  verifyResult,
} from "../core/domain";
import type {
  ExportSelection,
  JsonObject,
  WorkspaceState,
} from "../core/types";

export function createLocalExport(
  state: WorkspaceState,
  selection: ExportSelection,
  now: string,
): Uint8Array {
  const checks = selectExportChecks(state, selection),
    files: Record<string, Uint8Array> = {},
    manifest: JsonObject[] = [];
  let total = 0;
  const add = (path: string, value: unknown) => {
    const text = canonicalJson(value),
      bytes = utf8(text);
    if (bytes.byteLength > 524_288 || total + bytes.byteLength > 52_428_800)
      throw new IntegrityError(
        "EXPORT_LIMIT",
        "The selected evidence exceeds this export’s size limit. Select fewer checks; no records were omitted.",
      );
    total += bytes.byteLength;
    files[path] = bytes;
    manifest.push({ path, bytes: bytes.byteLength, sha256: digestText(text) });
  };
  for (const check of checks) {
    add(`checks/${check.id}.json`, {
      snapshot: check.snapshot,
      snapshot_sha256: check.snapshot_sha256,
      evidence_sha256: check.evidence_sha256,
      result: check.result,
      source: check.kind,
      delivery: check.delivery,
    });
    add(`contexts/${check.id}.json`, check.context);
    add(`manifests/${check.id}.json`, check.manifest);
    for (const attempt of check.attempts)
      add(`attempts/${attempt.attempt_id}.json`, attempt);
    if (check.alcohol) add(`alcohol/${check.id}.json`, check.alcohol);
  }
  add("profile.json", {
    schema_version: "1.0.0",
    selection_kind: selection.kind,
    current: selection.kind === "all" ? state.profile : null,
    versions: checks.map((check) => ({
      profile_version_id: check.context.profile_version_id,
      profile: check.snapshot.profile,
      history: check.snapshot.history,
      context: check.context.self_report_context,
    })),
  });
  const data = {
    schema_version: "1.0.0",
    canonicalization: "RFC8785",
    created_at: now,
    selection,
    session_ids: checks.map((c) => c.id),
    files: manifest,
    raw_artifacts_included: false,
    exclusions: [
      "Raw eye images, ECG/PPG waveforms and other unapproved artifacts are excluded.",
    ],
    limitations:
      "Measurement records and uncalibrated practice do not determine intoxication or driving safety.",
  };
  files["manifest.json"] = utf8(
    canonicalJson({ ...data, manifest_sha256: digest(data) }),
  );
  const archive = zipSync(files, { level: 6 });
  if (archive.byteLength > 67_108_864)
    throw new IntegrityError(
      "EXPORT_LIMIT",
      "This export exceeds the archive size limit.",
    );
  return archive;
}
export function inspectExportArchive(
  bytes: Uint8Array,
  expected: { selection?: JsonObject; manifestSha256?: string } = {},
): { fileCount: number; uncompressedBytes: number } {
  if (bytes.byteLength > 67_108_864)
    throw new IntegrityError("EXPORT_LIMIT", "The archive is too large.");
  let total = 0,
    count = 0;
  const names = new Set<string>();
  const files = unzipSync(bytes, {
    filter: (file) => {
      if (
        names.has(file.name) ||
        !/^(manifest\.json|profile\.json|(?:checks|contexts|manifests|attempts|alcohol)\/[0-9a-f-]+\.json)$/i.test(
          file.name,
        ) ||
        file.originalSize >
          (file.name.startsWith("attempts/") ? 524_288 : 52_428_800) ||
        total + file.originalSize > 52_428_800 ||
        ++count > 65_000
      )
        throw new IntegrityError(
          "EXPORT_ARCHIVE_INVALID",
          "The archive contains duplicate/unsupported paths or exceeds its limits.",
        );
      names.add(file.name);
      total += file.originalSize;
      return true;
    },
  });
  if (!files["manifest.json"])
    throw new IntegrityError(
      "EXPORT_MANIFEST_MISSING",
      "The archive has no manifest.",
    );
  const parsed = Object.fromEntries(
    Object.entries(files).map(([path, value]) => [
      path,
      parseBoundedJson(
        decodeUtf8(value),
        path.startsWith("attempts/") ? 524_288 : 52_428_800,
      ),
    ]),
  );
  const manifest = requireObject(parsed["manifest.json"]);
  knownKeys(manifest, [
    "schema_version",
    "canonicalization",
    "job_id",
    "selection",
    "session_ids",
    "created_at",
    "expires_at",
    "omitted_categories",
    "files",
    "manifest_sha256",
    "raw_artifacts_included",
    "exclusions",
    "limitations",
  ]);
  if (
    manifest.schema_version !== "1.0.0" ||
    manifest.canonicalization !== "RFC8785" ||
    !Array.isArray(manifest.files) ||
    !Array.isArray(manifest.session_ids) ||
    manifest.session_ids.length > 500 ||
    !files["profile.json"]
  )
    throw new IntegrityError(
      "EXPORT_MANIFEST_INVALID",
      "The archive manifest is incomplete.",
    );
  const selection = manifest.selection as ExportSelection;
  validateSelection(selection);
  if (expected.selection && digest(selection) !== digest(expected.selection))
    throw new IntegrityError(
      "EXPORT_SCOPE_MISMATCH",
      "The archive selection differs from the requested scope.",
    );
  if (expected.manifestSha256 && digest(manifest) !== expected.manifestSha256)
    throw new IntegrityError(
      "EXPORT_MANIFEST_HASH",
      "The downloaded manifest differs from its authenticated receipt.",
    );
  if (manifest.manifest_sha256) {
    const { manifest_sha256, ...content } = manifest;
    if (digest(content) !== manifest_sha256)
      throw new IntegrityError(
        "EXPORT_MANIFEST_HASH",
        "The local manifest digest is inconsistent.",
      );
  }
  const listed = new Set<string>();
  for (const item of manifest.files) {
    const entry = requireObject(item);
    knownKeys(entry, ["path", "sha256", "size_bytes", "bytes"]);
    const path = String(entry.path),
      content = files[path],
      size = entry.size_bytes ?? entry.bytes;
    if (
      listed.has(path) ||
      path === "manifest.json" ||
      !content ||
      content.byteLength !== size ||
      digestBytes(content) !== entry.sha256
    )
      throw new IntegrityError(
        "EXPORT_FILE_HASH",
        "A file differs from the manifest or is duplicated.",
      );
    listed.add(path);
  }
  if (listed.size !== Object.keys(files).length - 1)
    throw new IntegrityError(
      "EXPORT_UNLISTED_FILE",
      "The archive contains an unlisted file.",
    );
  const ids = Object.keys(files)
      .filter((x) => x.startsWith("checks/"))
      .map((x) => x.slice(7, -5))
      .sort(),
    declared = [...manifest.session_ids].sort();
  if (
    new Set(declared).size !== declared.length ||
    digest(ids) !== digest(declared) ||
    (selection.kind !== "all" &&
      digest([...selection.session_ids].sort()) !== digest(declared))
  )
    throw new IntegrityError(
      "EXPORT_SCOPE_MISMATCH",
      "The archive check IDs do not match its selected scope.",
    );
  for (const id of ids) {
    const check = requireObject(parsed[`checks/${id}.json`]);
    if (check.snapshot) {
      const snapshot = check.snapshot as Parameters<typeof validateSnapshot>[0];
      validateSnapshot(snapshot);
      if (
        snapshot.session_id !== id ||
        digest(snapshot) !== check.snapshot_sha256
      )
        throw new IntegrityError(
          "EXPORT_SNAPSHOT_HASH",
          "An exported snapshot differs from its digest.",
        );
      if (check.result)
        verifyResult(check.result, {
          id,
          snapshot,
          snapshot_sha256: String(check.snapshot_sha256),
        });
    }
    if (Array.isArray(check.attempts))
      for (const attempt of check.attempts)
        if (utf8(canonicalJson(attempt)).byteLength > 524_288)
          throw new IntegrityError(
            "EXPORT_ATTEMPT_LIMIT",
            "An exported attempt exceeds its limit.",
          );
  }
  return { fileCount: count, uncompressedBytes: total };
}
export function decodeUtf8(value: Uint8Array): string {
  return decodeURIComponent(
    [...value].map((b) => `%${b.toString(16).padStart(2, "0")}`).join(""),
  );
}
