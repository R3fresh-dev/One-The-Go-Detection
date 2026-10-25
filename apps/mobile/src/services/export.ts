import { zipSync, unzipSync } from "fflate";
import {
  canonicalJson,
  clone,
  digest,
  digestBytes,
  digestText,
  IntegrityError,
  knownKeys,
  parseBoundedJson,
  requireObject,
  safeInteger,
  utf8,
} from "../core/integrity";
import {
  emptyProfile,
  emptyWorkspace,
  selectExportChecks,
  validateProfileEnvelope,
  validateSelection,
} from "../core/domain";
import { parseRemoteCheck } from "../core/remote";
import {
  reportArchiveRecords,
  verifyReportArchiveIndex,
} from "../core/reportRevisions";
import { verifyExportEvidence } from "../core/exportEvidence";
import { requiresCurrentHrRead } from "../core/resultPresentation";
import { parseRawExportManifest } from "../core/rawExport";
import type {
  CaptureAttempt,
  CaptureContext,
  CheckRecord,
  EvidenceManifest,
  ExportSelection,
  JsonObject,
  ProfileEnvelope,
  Snapshot,
  WorkspaceState,
} from "../core/types";

const RECORD_LIMIT = 524_288,
  TOTAL_LIMIT = 52_428_800,
  ARCHIVE_LIMIT = 67_108_864;
const LOCAL_LIMITATIONS =
  "Measurement records and uncalibrated practice do not determine intoxication or driving safety.";
const LOCAL_EXCLUSIONS = [
  "Raw eye images, ECG/PPG waveforms and other unapproved artifacts are excluded.",
];
const UUID = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}";
const uuid = new RegExp(`^${UUID}$`, "i"),
  pathPattern = new RegExp(
    `^(manifest\\.json|profile\\.json|(?:checks|contexts|manifests|attempts|alcohol)/${UUID}\\.json|report-revisions/${UUID}/${UUID}\\.json|raw/(?:eye_video|ecg_waveform)/${UUID}\\.bin)$`,
    "i",
  );
const fail = (code: string, message: string): never => {
  throw new IntegrityError(code, message);
};
function frozenProfile(check: CheckRecord) {
  return {
    profile_version_id: check.context.profile_version_id,
    profile: check.snapshot.profile,
    history: check.snapshot.history,
    context: check.context.self_report_context ?? null,
  };
}
export function createLocalExport(
  state: WorkspaceState,
  selection: ExportSelection,
  now: string,
  currentHrResultDigests: ReadonlyMap<string, string> = new Map(),
): Uint8Array {
  const checks = selectExportChecks(state, selection),
    files: Record<string, Uint8Array> = {},
    manifest: JsonObject[] = [];
  let total = 0;
  const add = (path: string, value: unknown) => {
    const text = canonicalJson(value),
      bytes = utf8(text);
    if (
      bytes.byteLength > RECORD_LIMIT ||
      total + bytes.byteLength > TOTAL_LIMIT ||
      files[path] ||
      manifest.length + 2 > 65_000
    )
      fail(
        "EXPORT_LIMIT",
        "The selected evidence exceeds this export’s size or entry limit. Select fewer checks; no records were omitted.",
      );
    total += bytes.byteLength;
    files[path] = bytes;
    manifest.push({ path, bytes: bytes.byteLength, sha256: digestText(text) });
  };
  for (const check of checks) {
    verifyExportEvidence(check);
    if (
      requiresCurrentHrRead(check.result) &&
      currentHrResultDigests.get(check.id) !== digest(check.result)
    )
      fail(
        "HR_RESULT_ADMISSION_REQUIRED",
        "Reconnect to admit each selected HR research result before exporting. No selected record was changed or omitted.",
      );
    const revisions = reportArchiveRecords(check);
    add(`checks/${check.id}.json`, {
      snapshot: check.snapshot,
      snapshot_sha256: check.snapshot_sha256,
      evidence_sha256: check.evidence_sha256,
      result: check.result,
      source: check.kind,
      delivery: check.delivery,
      report_revision_index: revisions.index,
      instruction_receipts: check.instruction_receipts ?? [],
      collections: check.collections ?? [],
      collection_abandons: check.collection_abandons ?? [],
    });
    add(`contexts/${check.id}.json`, check.context);
    add(`manifests/${check.id}.json`, check.manifest);
    for (const attempt of check.attempts)
      add(`attempts/${attempt.attempt_id}.json`, attempt);
    if (check.alcohol) add(`alcohol/${check.id}.json`, check.alcohol);
    for (const [path, record] of Object.entries(revisions.records))
      add(path, record);
  }
  add("profile.json", {
    schema_version: "1.0.0",
    selection_kind: selection.kind,
    current: selection.kind === "all" ? state.profile : null,
    versions: checks.map(frozenProfile),
  });
  const data = {
    schema_version: "1.0.0",
    canonicalization: "RFC8785",
    created_at: now,
    selection,
    session_ids: checks.map((c) => c.id),
    files: manifest,
    raw_artifacts_included: false,
    exclusions: LOCAL_EXCLUSIONS,
    limitations: LOCAL_LIMITATIONS,
  };
  const manifestBytes = utf8(
    canonicalJson({ ...data, manifest_sha256: digest(data) }),
  );
  if (total + manifestBytes.byteLength > TOTAL_LIMIT)
    fail(
      "EXPORT_LIMIT",
      "The manifest and selected evidence together exceed this export’s size limit. No records were omitted.",
    );
  files["manifest.json"] = manifestBytes;
  const archive = zipSync(files, { level: 6 });
  if (archive.byteLength > ARCHIVE_LIMIT)
    fail("EXPORT_LIMIT", "This export exceeds the archive size limit.");
  inspectExportArchive(archive, {
    selection: selection as unknown as JsonObject,
    generation: state.generation,
  });
  return archive;
}

export function inspectExportArchive(
  bytes: Uint8Array,
  expected: {
    selection?: JsonObject;
    manifestSha256?: string;
    accountRef?: string;
    generation?: number;
    rawExport?: JsonObject;
  } = {},
): { fileCount: number; uncompressedBytes: number } {
  if (bytes.byteLength > ARCHIVE_LIMIT)
    fail("EXPORT_LIMIT", "The archive is too large.");
  let total = 0,
    count = 0;
  const names = new Set<string>();
  const files = unzipSync(bytes, {
    filter: (file) => {
      if (
        names.has(file.name) ||
        !pathPattern.test(file.name) ||
        file.originalSize >
          (file.name === "manifest.json" || file.name.startsWith("raw/")
            ? TOTAL_LIMIT
            : RECORD_LIMIT) ||
        total + file.originalSize > TOTAL_LIMIT ||
        ++count > 65_000
      )
        fail(
          "EXPORT_ARCHIVE_INVALID",
          "The archive contains duplicate/unsupported paths or exceeds its limits.",
        );
      names.add(file.name);
      total += file.originalSize;
      return true;
    },
  });
  if (!files["manifest.json"])
    fail("EXPORT_MANIFEST_MISSING", "The archive has no manifest.");
  const parsed: Record<string, unknown> = {},
    sizes: Record<string, number> = {};
  let actualTotal = 0;
  for (const [path, value] of Object.entries(files)) {
    if (
      value.byteLength >
      (path === "manifest.json" || path.startsWith("raw/")
        ? TOTAL_LIMIT
        : RECORD_LIMIT)
    )
      fail(
        "EXPORT_RECORD_LIMIT",
        "An exported structured record exceeds 512 KiB.",
      );
    actualTotal += value.byteLength;
    sizes[path] = value.byteLength;
    if (path.startsWith("raw/")) continue;
    parsed[path] = parseBoundedJson(
      decodeUtf8(value),
      path === "manifest.json" ? TOTAL_LIMIT : RECORD_LIMIT,
    );
    if (canonicalJson(parsed[path]) !== decodeUtf8(value))
      fail(
        "EXPORT_NONCANONICAL",
        "An exported record is not encoded in the declared canonical format.",
      );
  }
  if (actualTotal !== total || total > TOTAL_LIMIT)
    fail(
      "EXPORT_LIMIT",
      "The archive’s declared and actual uncompressed lengths differ.",
    );
  const manifest = requireObject(parsed["manifest.json"]),
    layout = Object.hasOwn(manifest, "job_id") ? "cloud" : "local";
  const manifestKeys = [
    "schema_version",
    "canonicalization",
    "selection",
    "session_ids",
    "created_at",
    "files",
    ...(layout === "cloud"
      ? [
          "job_id",
          "expires_at",
          "omitted_categories",
          ...(Object.hasOwn(manifest, "raw_export") ? ["raw_export"] : []),
        ]
      : [
          "manifest_sha256",
          "raw_artifacts_included",
          "exclusions",
          "limitations",
        ]),
  ];
  knownKeys(manifest, manifestKeys);
  const createdAt = manifestInstant(manifest.created_at);
  if (
    manifestKeys.some((key) => !Object.hasOwn(manifest, key)) ||
    manifest.schema_version !== "1.0.0" ||
    manifest.canonicalization !== "RFC8785" ||
    !Array.isArray(manifest.files) ||
    manifest.files.length > 64_999 ||
    !Array.isArray(manifest.session_ids) ||
    manifest.session_ids.length > 500 ||
    !files["profile.json"]
  )
    fail(
      "EXPORT_MANIFEST_INVALID",
      "The archive manifest is incomplete or has unsupported metadata.",
    );
  if (layout === "cloud") {
    if (
      typeof manifest.job_id !== "string" ||
      !uuid.test(manifest.job_id) ||
      manifestInstant(manifest.expires_at) <= createdAt ||
      !Array.isArray(manifest.omitted_categories) ||
      digest(manifest.omitted_categories) !==
        digest(
          manifest.raw_export === undefined
            ? ["raw_artifacts"]
            : ["unselected_raw_artifacts", "source_lab_reports"],
        )
    )
      fail(
        "EXPORT_MANIFEST_INVALID",
        "The cloud manifest has unsupported identity, expiry or exclusion metadata.",
      );
  } else if (
    manifest.raw_artifacts_included !== false ||
    manifest.limitations !== LOCAL_LIMITATIONS ||
    !Array.isArray(manifest.exclusions) ||
    manifest.exclusions.length !== 1 ||
    manifest.exclusions[0] !== LOCAL_EXCLUSIONS[0] ||
    typeof manifest.manifest_sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(manifest.manifest_sha256)
  )
    fail(
      "EXPORT_MANIFEST_INVALID",
      "The local manifest differs from the fixed release limitations and exclusions.",
    );
  const selectionObject = requireObject(manifest.selection);
  const rawExport =
    manifest.raw_export === undefined
      ? null
      : parseRawExportManifest(manifest.raw_export);
  if (
    (rawExport &&
      (layout !== "cloud" ||
        !expected.rawExport ||
        digest(rawExport) !== digest(expected.rawExport))) ||
    (!rawExport && expected.rawExport) ||
    (!rawExport && Object.keys(files).some((path) => path.startsWith("raw/")))
  )
    fail(
      "RAW_EXPORT_SCOPE_MISMATCH",
      "Raw files require the exact separately authorized scope from this authenticated job receipt.",
    );
  knownKeys(selectionObject, ["kind", "session_ids"]);
  const selection = selectionObject as unknown as ExportSelection;
  validateSelection(selection);
  if (expected.selection && digest(selection) !== digest(expected.selection))
    fail(
      "EXPORT_SCOPE_MISMATCH",
      "The archive selection differs from the requested scope.",
    );
  if (expected.manifestSha256 && digest(manifest) !== expected.manifestSha256)
    fail(
      "EXPORT_MANIFEST_HASH",
      "The downloaded manifest differs from its authenticated receipt.",
    );
  if (layout === "local") {
    const { manifest_sha256, ...content } = manifest;
    if (digest(content) !== manifest_sha256)
      fail(
        "EXPORT_MANIFEST_HASH",
        "The local manifest digest is inconsistent.",
      );
  }
  const listed = new Set<string>();
  for (const item of manifest.files as unknown[]) {
    const entry = requireObject(item);
    const sizeKey = layout === "cloud" ? "size_bytes" : "bytes";
    knownKeys(entry, ["path", "sha256", sizeKey]);
    const path = entry.path,
      size = entry[sizeKey];
    if (
      typeof path !== "string" ||
      !Number.isSafeInteger(size) ||
      Number(size) < 1 ||
      Number(size) >
        (typeof path === "string" && path.startsWith("raw/")
          ? TOTAL_LIMIT
          : RECORD_LIMIT) ||
      typeof entry.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/.test(entry.sha256) ||
      listed.has(path) ||
      path === "manifest.json" ||
      !files[path] ||
      files[path]!.byteLength !== size ||
      digestBytes(files[path]!) !== entry.sha256
    )
      fail(
        "EXPORT_FILE_HASH",
        "A file differs from the manifest or is duplicated.",
      );
    listed.add(path as string);
  }
  if (listed.size !== Object.keys(files).length - 1)
    fail("EXPORT_UNLISTED_FILE", "The archive contains an unlisted file.");
  const ids = Object.keys(files)
      .filter((path) => path.startsWith("checks/"))
      .map((path) => path.slice(7, -5))
      .sort(),
    declared = [...(manifest.session_ids as unknown[])].sort();
  if (
    new Set(declared).size !== declared.length ||
    declared.some((id) => typeof id !== "string" || !uuid.test(id)) ||
    digest(ids) !== digest(declared) ||
    (selection.kind !== "all" &&
      digest([...selection.session_ids].sort()) !== digest(declared))
  )
    fail(
      "EXPORT_SCOPE_MISMATCH",
      "The archive check IDs do not match its selected scope.",
    );
  const consumed = new Set(["manifest.json", "profile.json"]),
    checks: CheckRecord[] = [];
  let owner: string | undefined = expected.accountRef,
    generation = expected.generation;
  const take = (path: string): unknown => {
    if (!files[path] || consumed.has(path))
      fail(
        "EXPORT_EVIDENCE_SCOPE",
        "A selected evidence file is missing, duplicated or shared between unrelated checks.",
      );
    consumed.add(path);
    return parsed[path];
  };
  for (const id of ids) {
    const wrapper = requireObject(take(`checks/${id}.json`)),
      snapshot = requireObject(wrapper.snapshot) as unknown as Snapshot,
      index = requireObject(wrapper.report_revision_index);
    const currentGeneration = safeInteger(index.data_generation, 1);
    owner ??= snapshot.subject_ref;
    generation ??= currentGeneration;
    if (
      snapshot.session_id !== id ||
      snapshot.subject_ref !== owner ||
      currentGeneration !== generation
    )
      fail(
        "EXPORT_OWNER_MISMATCH",
        "The archive combines another owner’s record or retired data generation.",
      );
    const cloud = Object.hasOwn(wrapper, "session_id"),
      currentLayout = cloud ? "cloud" : "local";
    if (layout !== currentLayout)
      fail(
        "EXPORT_LAYOUT_MISMATCH",
        "The archive mixes unsupported evidence layouts.",
      );
    let check: CheckRecord;
    if (cloud) {
      if (
        wrapper.raw_artifacts_omitted_reason !==
        (rawExport ? "UNSELECTED_RAW_ARTIFACTS_OMITTED" : "NO_RAW_EXPORT_SCOPE")
      )
        fail(
          "RAW_EXPORT_SCOPE_MISMATCH",
          "The selected check raw omission label differs from this exact archive scope.",
        );
      const { report_revision_index: ignored, ...original } = wrapper;
      const state = emptyWorkspace(
        "export-verification",
        snapshot.created_at,
        currentGeneration,
      );
      state.capabilities = {
        account_ref: owner,
      } as WorkspaceState["capabilities"];
      check = parseRemoteCheck(original, state);
    } else {
      knownKeys(wrapper, [
        "snapshot",
        "snapshot_sha256",
        "evidence_sha256",
        "result",
        "source",
        "delivery",
        "report_revision_index",
        "instruction_receipts",
        "collections",
        "collection_abandons",
      ]);
      const deliveries = [
        "local_finalized",
        "queued",
        "registering",
        "uploading_evidence",
        "uploading_snapshot",
        "finalizing",
        "awaiting_result",
        "synced",
        "retry_wait",
        "auth_required",
        "blocked",
        "conflict",
      ];
      if (
        !["guest_demo", "engineering_fixture", "measurement"].includes(
          String(wrapper.source),
        ) ||
        !deliveries.includes(String(wrapper.delivery))
      )
        fail(
          "EXPORT_CHECK_STATE",
          "An exported local check has an unsupported source or state.",
        );
      const context = take(`contexts/${id}.json`) as CaptureContext,
        manifestValue = take(`manifests/${id}.json`) as EvidenceManifest;
      if (!Array.isArray(manifestValue.attempts))
        fail("EXPORT_EVIDENCE_SCOPE", "The attempt manifest is missing.");
      const attempts = manifestValue.attempts.map((entry) => {
        if (!uuid.test(entry.attempt_id))
          fail("EXPORT_EVIDENCE_SCOPE", "An attempt path is unsupported.");
        return take(`attempts/${entry.attempt_id}.json`) as CaptureAttempt;
      });
      check = {
        id,
        generation: currentGeneration,
        workspace: "export-verification",
        kind: wrapper.source as CheckRecord["kind"],
        stage: "review",
        frozen: true,
        snapshot,
        context,
        manifest: manifestValue,
        attempts,
        instruction_receipts: (wrapper.instruction_receipts ??
          []) as JsonObject[],
        collections: (wrapper.collections ?? []) as JsonObject[],
        collection_abandons: (wrapper.collection_abandons ??
          []) as JsonObject[],
        snapshot_sha256: wrapper.snapshot_sha256 as string,
        evidence_sha256: wrapper.evidence_sha256 as string,
        result: wrapper.result as CheckRecord["result"],
        alcohol: files[`alcohol/${id}.json`]
          ? (take(`alcohol/${id}.json`) as JsonObject)
          : null,
        delivery: wrapper.delivery as CheckRecord["delivery"],
        error: null,
        remote_revision: 0,
        remote_etag: '"0"',
        updated_at: snapshot.capture_completed_at,
      };
    }
    verifyExportEvidence(check);
    const revisionPaths = verifyReportArchiveIndex(index, check, parsed, sizes);
    for (const path of revisionPaths) take(path);
    checks.push(check);
  }
  if (rawExport) {
    for (const value of rawExport.sources as JsonObject[]) {
      const source = requireObject(value),
        path = String(source.path),
        file = files[path],
        check = checks.find((check) => check.id === source.session_id);
      if (
        !file ||
        !check ||
        check.snapshot.study_id !== rawExport.study_id ||
        file.byteLength !== source.size_bytes ||
        digestBytes(file) !== source.sha256 ||
        Number(source.retained_until) * 1000 <=
          Date.parse(String(manifest.created_at)) ||
        !check.attempts.some(
          (attempt) =>
            attempt.component ===
            (source.kind === "eye_video" ? "eyes" : "cardiac"),
        )
      )
        fail(
          "RAW_EXPORT_SOURCE_MISMATCH",
          "A raw member differs from its verified source bytes, retained lifetime or exact selected study check.",
        );
      consumed.add(path);
    }
  }
  for (const path of Object.keys(files))
    if (!consumed.has(path))
      fail(
        "EXPORT_ORPHAN_RECORD",
        "The archive contains an unselected or unbound evidence, profile, alcohol or report record.",
      );
  verifyProfileArchive(parsed["profile.json"], checks, selection, layout);
  return { fileCount: count, uncompressedBytes: total };
}

function manifestInstant(value: unknown): number {
  if (
    typeof value !== "string" ||
    value.length > 32 ||
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z$/.test(value)
  )
    fail(
      "EXPORT_MANIFEST_INVALID",
      "An archive manifest timestamp is not a bounded UTC instant.",
    );
  const instant = Date.parse(value as string);
  if (
    !Number.isFinite(instant) ||
    new Date(instant).toISOString().slice(0, 19) !==
      (value as string).slice(0, 19)
  )
    fail(
      "EXPORT_MANIFEST_INVALID",
      "An archive manifest timestamp is not a real UTC instant.",
    );
  return instant;
}

function verifyProfileArchive(
  value: unknown,
  checks: CheckRecord[],
  selection: ExportSelection,
  layout: "local" | "cloud",
): void {
  const object = requireObject(value);
  knownKeys(object, [
    "schema_version",
    "selection_kind",
    "current",
    "versions",
  ]);
  if (
    object.schema_version !== "1.0.0" ||
    object.selection_kind !== selection.kind ||
    !Array.isArray(object.versions) ||
    object.versions.length > 500 ||
    (selection.kind !== "all" && object.current !== null)
  )
    fail(
      "EXPORT_PROFILE_SCOPE",
      "The profile archive differs from the selected scope.",
    );
  const versions = object.versions as unknown[],
    ids = new Set<string>();
  const validateVersion = (
    value: unknown,
    localCurrent = false,
  ): ProfileEnvelope => {
    const p = requireObject(value);
    knownKeys(
      p,
      localCurrent
        ? [
            "profile_version_id",
            "revision",
            "profile",
            "history",
            "context",
            "etag",
            "sync",
          ]
        : ["profile_version_id", "profile", "history", "context"],
    );
    if (
      p.profile_version_id !== null &&
      (typeof p.profile_version_id !== "string" ||
        !uuid.test(p.profile_version_id))
    )
      fail(
        "EXPORT_PROFILE_SCOPE",
        "An exported profile version has an unsupported identity.",
      );
    if (
      localCurrent &&
      (!Number.isSafeInteger(p.revision) ||
        Number(p.revision) < 0 ||
        p.etag !== `"${p.revision}"` ||
        !["local", "queued", "synced", "conflict"].includes(String(p.sync)))
    )
      fail(
        "EXPORT_PROFILE_SCOPE",
        "The local profile metadata is inconsistent.",
      );
    const parsed = {
      ...emptyProfile("1970-01-01T00:00:00.000Z"),
      ...clone(p),
    } as ProfileEnvelope;
    validateProfileEnvelope(parsed);
    return parsed;
  };
  for (const version of versions) validateVersion(version);
  if (layout === "local") {
    const actual = versions.map(digest).sort(),
      expected = checks.map((check) => digest(frozenProfile(check))).sort();
    if (digest(actual) !== digest(expected))
      fail(
        "EXPORT_PROFILE_SCOPE",
        "The archive includes a profile version not frozen into the exact selected checks, or omits a selected profile.",
      );
    if (object.current !== null) validateVersion(object.current, true);
  } else {
    const needed = new Set(
      checks
        .map((check) => check.context.profile_version_id)
        .filter((id): id is string => id !== null),
    );
    for (const version of versions) {
      const p = version as { profile_version_id: string; profile: unknown };
      if (
        !p.profile_version_id ||
        ids.has(p.profile_version_id) ||
        (selection.kind !== "all" && !needed.has(p.profile_version_id))
      )
        fail(
          "EXPORT_PROFILE_SCOPE",
          "The archive includes an unrelated or duplicate cloud profile version.",
        );
      ids.add(p.profile_version_id);
      for (const check of checks.filter(
        (check) => check.context.profile_version_id === p.profile_version_id,
      ))
        if (digest(p.profile) !== digest(check.snapshot.profile))
          fail(
            "EXPORT_PROFILE_SCOPE",
            "An immutable cloud profile version differs from the selected captured profile.",
          );
    }
    if ([...needed].some((id) => !ids.has(id)))
      fail(
        "EXPORT_PROFILE_SCOPE",
        "A profile version used by a selected check is missing.",
      );
    if (object.current !== null) {
      validateVersion(object.current);
      if (
        !versions.some((version) => digest(version) === digest(object.current))
      )
        fail(
          "EXPORT_PROFILE_SCOPE",
          "The current profile is not an accepted version in this all-data archive.",
        );
    }
  }
}
export function decodeUtf8(value: Uint8Array): string {
  return decodeURIComponent(
    [...value].map((b) => `%${b.toString(16).padStart(2, "0")}`).join(""),
  );
}
