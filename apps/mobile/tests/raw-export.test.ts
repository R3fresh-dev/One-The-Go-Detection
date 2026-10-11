import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { URL } from "node:url";
import { randomUUID } from "node:crypto";
import { unzipSync, zipSync } from "fflate";
import {
  canonicalJson,
  clone,
  digest,
  digestBytes,
  digestText,
  utf8,
} from "../src/core/integrity";
import {
  confirmRawExport,
  parseRawExportAuthorities,
  parseRawExportPage,
  parseRawExportManifest,
  verifyRawExportReceipt,
} from "../src/core/rawExport";
import { parsePrivacyJob } from "../src/services/api";
import { decodeUtf8, inspectExportArchive } from "../src/services/export";
import type { ExportSelection, JsonObject } from "../src/core/types";
import { customerService } from "./support/customer";
require("./support/runtime.cjs");
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");
const path = (name: string) =>
  new URL(
    "../../../services/api/tests/fixtures/raw-export-v1/" + name,
    import.meta.url,
  );
const wire = JSON.parse(readFileSync(path("raw-export-scopes.json"), "utf8"));
const receipt = JSON.parse(readFileSync(path("raw-export-job.json"), "utf8"));
const revokedReceipt = JSON.parse(
  readFileSync(path("raw-export-revoked-job.json"), "utf8"),
);
const archive = new Uint8Array(readFileSync(path("raw-export.zip"))),
  files = unzipSync(archive),
  manifest = JSON.parse(decodeUtf8(files["manifest.json"]!));
const expected = {
  accountRef: manifest.account_ref,
  generation: receipt.data_generation,
  selection: receipt.scope,
  manifestSha256: receipt.manifest_sha256,
  rawExport: receipt.raw_export,
};
function rewrite(
  change: (members: Record<string, Uint8Array>, m: any) => void,
) {
  const members: Record<string, Uint8Array> = unzipSync(archive),
    m = JSON.parse(decodeUtf8(members["manifest.json"]!));
  change(members, m);
  m.files = Object.entries(members)
    .filter(([name]) => name !== "manifest.json")
    .map(([name, bytes]) => ({
      path: name,
      size_bytes: bytes.length,
      sha256: digestBytes(bytes),
    }));
  members["manifest.json"] = utf8(canonicalJson(m));
  return zipSync(members);
}
test("actual authenticated Python scope, completed job and worker ZIP verify exact independent raw authority and versioned binary sources", (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(receipt.accepted_at),
  });
  const page = parseRawExportPage(wire),
    authority = page.scopes[0]!;
  assert.equal(page.next_cursor, null);
  assert.deepEqual(parseRawExportAuthorities(wire), page.scopes);
  const scope = confirmRawExport(
    authority,
    authority.artifacts.map((a) => a.artifact_id),
    receipt.scope,
    receipt.raw_export.acknowledged_at,
  );
  assert.deepEqual(
    verifyRawExportReceipt(receipt.raw_export, scope),
    receipt.raw_export,
  );
  assert.equal(parsePrivacyJob(receipt).state, "completed");
  assert.equal(digestBytes(archive), receipt.sha256);
  assert.equal(archive.length, receipt.size_bytes);
  assert.equal(
    inspectExportArchive(archive, expected).fileCount,
    Object.keys(files).length,
  );
  assert.equal(
    files[receipt.raw_export.sources[0].path]!.length,
    receipt.raw_export.sources[0].size_bytes,
    "The worker fixture contains exact fictional gray-pixel codec bytes, not a human recording.",
  );
  assert.equal(parsePrivacyJob(revokedReceipt).state, "revoked");
  assert.equal(revokedReceipt.raw_export, undefined);
  assert.equal(revokedReceipt.download_path, undefined);
  assert.throws(
    () => inspectExportArchive(archive, { ...expected, rawExport: undefined }),
    /exact separately authorized scope/,
  );
});
test("rehashed raw version, size, digest, omitted-scope and orphan substitutions never expand the authenticated job scope", () => {
  for (const change of [
    (_: Record<string, Uint8Array>, m: any) =>
      (m.raw_export.sources[0].version_id = "different-version"),
    (_: Record<string, Uint8Array>, m: any) =>
      m.raw_export.sources[0].size_bytes++,
    (_: Record<string, Uint8Array>, m: any) =>
      (m.raw_export.sources[0].sha256 = "1".repeat(64)),
    (_: Record<string, Uint8Array>, m: any) =>
      (m.raw_export.authorization_sha256 = "1".repeat(64)),
    (_: Record<string, Uint8Array>, m: any) =>
      (m.omitted_categories = ["raw_artifacts"]),
    (members: Record<string, Uint8Array>) =>
      (members[`raw/eye_video/${randomUUID()}.bin`] = new Uint8Array([
        1, 2, 3,
      ])),
    (members: Record<string, Uint8Array>) => {
      const key = receipt.raw_export.sources[0].path;
      members[key]![0] = (members[key]![0] ?? 0) ^ 1;
    },
    (members: Record<string, Uint8Array>) => {
      const key = `checks/${receipt.scope.session_ids[0]}.json`,
        check = JSON.parse(decodeUtf8(members[key]!));
      check.raw_artifacts_omitted_reason = "NO_RAW_EXPORT_SCOPE";
      members[key] = utf8(canonicalJson(check));
    },
  ])
    assert.throws(() =>
      inspectExportArchive(rewrite(change), {
        ...expected,
        manifestSha256: undefined,
      }),
    );
  for (const change of [
    (m: any) => (m.sources[0].version_id = "null"),
    (m: any) => (m.sources[0].path = "raw/../token.bin"),
    (m: any) => m.sources.push(m.sources[0]),
    (m: any) => (m.sources[0].retained_until = -1),
  ]) {
    const changed = clone(receipt.raw_export);
    change(changed);
    assert.throws(() => parseRawExportManifest(changed));
  }
});
test("server boundary terms remain bounded and optional sources cannot inherit recording consent or broaden selection", (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(receipt.accepted_at),
  });
  const boundary = clone(wire);
  boundary.scopes[0].purpose_text = "p".repeat(4096);
  boundary.scopes[0].export_notice.version = "v".repeat(128);
  boundary.scopes[0].artifacts[0].size_bytes = 64 * 1024 * 1024;
  boundary.next_cursor = "a".repeat(64);
  const page = parseRawExportPage(boundary);
  assert.equal(page.next_cursor, boundary.next_cursor);
  const authority = page.scopes[0]!;
  assert.throws(() =>
    confirmRawExport(
      authority,
      [authority.artifacts[0]!.artifact_id],
      receipt.scope,
      receipt.accepted_at,
    ),
  );
  const valid = parseRawExportAuthorities(wire)[0]!;
  for (const ids of [
    [],
    [randomUUID()],
    [valid.artifacts[0]!.artifact_id, valid.artifacts[0]!.artifact_id],
  ])
    assert.throws(() =>
      confirmRawExport(valid, ids, receipt.scope, receipt.accepted_at),
    );
  assert.throws(() =>
    confirmRawExport(
      valid,
      [valid.artifacts[0]!.artifact_id],
      { kind: "single", session_ids: [randomUUID()] },
      receipt.accepted_at,
    ),
  );
  const future = clone(valid);
  future.expires_at = receipt.accepted_at;
  assert.throws(() =>
    confirmRawExport(
      future,
      [future.artifacts[0]!.artifact_id],
      receipt.scope,
      receipt.accepted_at,
    ),
  );
  for (const mutate of [
    (w: any) => (w.scopes[0].purpose_text += "p"),
    (w: any) => (w.scopes[0].export_notice.version += "v"),
    (w: any) => (w.scopes[0].export_notice.content = "changed"),
    (w: any) => (w.next_cursor = "not-hash"),
    (w: any) => w.scopes.push(w.scopes[0]),
    (w: any) => w.scopes[0].artifacts[0].size_bytes++,
  ]) {
    const changed = clone(boundary);
    mutate(changed);
    assert.throws(() => parseRawExportPage(changed));
  }
  assert.throws(() =>
    verifyRawExportReceipt(receipt.raw_export, {
      ...confirmRawExport(
        valid,
        [valid.artifacts[0]!.artifact_id],
        receipt.scope,
        receipt.accepted_at,
      ),
      artifact_ids: [randomUUID()],
    }),
  );
  const unavailable = { ...receipt, state: "revoked" };
  delete unavailable.raw_export;
  assert.equal(parsePrivacyJob(unavailable).state, "revoked");
  assert.throws(() => parsePrivacyJob({ ...unavailable, kind: "deletion" }));
  assert.throws(() => parsePrivacyJob({ ...receipt, state: "revoked" }));
});
test("cloud export defaults raw off; explicit separate scope persists original acknowledgment and key through a lost receipt", async (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse(receipt.accepted_at),
  });
  const service = customerService(),
    previous = globalThis.fetch;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  const app = new AppController();
  await app.initialize();
  await app.signIn();
  const selection = receipt.scope as ExportSelection;
  let lost = true;
  service.overrides.set("/v1/privacy/raw-export-scopes", () =>
    service.result(wire),
  );
  service.overrides.set(
    "/v1/privacy/raw-export-scopes?authorization_id=FICTIONAL-RAW-EXPORT",
    () => service.result(wire),
  );
  service.overrides.set("POST /v1/privacy/exports", (call) => {
    if (!call.body.include_raw) {
      const structured = clone(receipt);
      delete structured.raw_export;
      return service.result(structured, 202);
    }
    if (lost) {
      lost = false;
      throw Error("Lost accepted receipt");
    }
    return service.result(receipt, 202);
  });
  try {
    await app.openExport({ source: "cloud", selection });
    await app.createExport();
    const baseline = service.calls.find(
      (call) => call.path === "/v1/privacy/exports",
    )!;
    assert.equal(baseline.body.include_raw, false);
    assert.equal(baseline.body.raw_scope, undefined);
    await app.refreshRawExportScopes();
    const a = app.getSnapshot().state!.rawExportAuthorities![0]!;
    const choice = {
      authorization_id: a.authorization_id,
      authority_sha256: a.authorization_sha256,
      notice_sha256: a.export_notice.sha256,
      artifact_ids: a.artifacts.map((a) => a.artifact_id),
    };
    await app.createExport(choice);
    const first = service.calls.filter(
      (call) => call.path === "/v1/privacy/exports" && call.body.include_raw,
    )[0]!;
    context.mock.timers.setTime(Date.parse(receipt.accepted_at) + 1000);
    await app.createExport(choice);
    const requests = service.calls.filter(
      (call) => call.path === "/v1/privacy/exports" && call.body.include_raw,
    );
    assert.equal(requests.length, 2);
    assert.deepEqual(requests[1]!.body, first.body);
    assert.equal(
      requests[1]!.headers.get("Idempotency-Key"),
      first.headers.get("Idempotency-Key"),
    );
    assert.equal(
      app
        .getSnapshot()
        .state!.queue.filter((q) => q.kind === "export" && q.body.include_raw)
        .length,
      1,
    );
  } finally {
    await app.auth.clear();
    await app.dispose();
    globalThis.fetch = previous;
  }
});
