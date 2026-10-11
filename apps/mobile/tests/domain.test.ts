import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { unzipSync, zipSync } from "fflate";
import {
  canonicalJson,
  clone,
  digest,
  parseBoundedJson,
  utf8,
} from "../src/core/integrity";
import {
  createCheck,
  emptyWorkspace,
  freezeCheck,
  interruptStartedAttempts,
  normalizeConcentration,
  normalizeProfile,
  quarantineGeneration,
  replaceCheck,
  selectExportChecks,
  settleAttempt,
  simulatedCapture,
  startAttempt,
  validateSelection,
  verifyCheck,
  verifyResult,
  convertHeight,
  convertWeight,
} from "../src/core/domain";
import { parseProfile } from "../src/core/remote";
import {
  createLocalExport,
  decodeUtf8,
  inspectExportArchive,
} from "../src/services/export";
import {
  ApiError,
  parsePrivacyJob,
  verifyNotice,
  DEMO_NOTICE,
} from "../src/services/api";
import {
  errorDisposition,
  queueCheck,
  queueMutation,
} from "../src/services/sync";
import type {
  Channel,
  CheckRecord,
  JsonObject,
  WorkspaceState,
} from "../src/core/types";

const at = "2026-10-11T15:00:00.000Z",
  later = "2026-10-11T16:00:00.000Z",
  owner = "00000000-0000-4000-8000-000000000001";
function fixture(kind: CheckRecord["kind"] = "engineering_fixture") {
  const state = emptyWorkspace(
    kind === "guest_demo" ? "guest:local" : "local:fixture",
    at,
  );
  let check = createCheck(state, {
    now: at,
    id: randomUUID,
    kind,
    accountRef: kind === "guest_demo" ? undefined : owner,
    contextConfirmed: true,
  });
  if (kind !== "measurement")
    for (const channel of ["saliva", "eyes", "cardiac", "alcohol"] as Channel[])
      check = simulatedCapture(
        check,
        channel,
        at,
        randomUUID,
        channel === "cardiac" ? "ecg" : "ppg",
      );
  check = freezeCheck(check, later, randomUUID);
  return { check, state: replaceCheck(state, check) };
}

test("all retained measurement and application DTO schema copies match source contracts", () => {
  for (const name of ["session", "measurement", "result"])
    assert.equal(
      readFileSync(`src/contracts/${name}.schema.json`, "utf8"),
      readFileSync(`../../contracts/${name}.schema.json`, "utf8"),
    );
  for (const name of [
    "CaptureAttempt",
    "CaptureContext",
    "EvidenceManifest",
    "Alcohol",
    "ProfileWrite",
    "ReportRevisionCompanion",
    "ReportRevisionList",
    "ReportRevisionDetail",
    "ReportRevisionIndex",
  ])
    assert.equal(
      readFileSync(`src/contracts/${name}.schema.json`, "utf8"),
      readFileSync(`../../contracts/application/${name}.schema.json`, "utf8"),
    );
});
test("RFC8785 and SHA256 match every independently generated canonical golden", () => {
  const golden = JSON.parse(
    readFileSync("../../contracts/application/canonical-golden.json", "utf8"),
  );
  for (const row of golden.valid) {
    assert.equal(canonicalJson(row.value), row.canonical_utf8);
    assert.equal(digest(row.value), row.sha256);
  }
  for (const row of golden.invalid_json)
    assert.throws(() => parseBoundedJson(row));
});
test("duplicate escaped keys, unknown numeric values and excessive JSON depth are rejected", () => {
  assert.throws(() => parseBoundedJson('{"x":1,"\\u0078":2}'));
  assert.throws(() => canonicalJson({ a: Number.NaN }));
  assert.throws(() => canonicalJson({ a: 9007199254740992 }));
  assert.throws(() => parseBoundedJson("[".repeat(42) + "0" + "]".repeat(42)));
});
test("default workspace contains no invented demographics and no automatic retry", () => {
  const s = emptyWorkspace("guest:local", at);
  assert.equal(s.profile.profile.age_years, null);
  assert.equal(s.profile.profile.bmi, null);
  assert.equal(s.profile.context.last_use_at, null);
  assert.equal(s.preferences.retryQueuedAutomatically, false);
  assert.deepEqual(s.queue, []);
});
test("profile converts SI units and rejects ranges, relative time and unknown enums", () => {
  const p = emptyWorkspace("guest", at).profile;
  p.profile.height_cm = convertHeight(70, "in");
  p.profile.weight_kg = convertWeight(150, "lb");
  p.profile.age_years = 18;
  const valid = normalizeProfile(p, at);
  assert.equal(valid.profile.height_cm, 177.8);
  assert.equal(valid.profile.weight_kg, 68.0388555);
  assert.ok(Math.abs(valid.profile.bmi! - 21.52253815221916) < 1e-10);
  for (const age of [17, 126, 18.5]) {
    const invalid = clone(p);
    invalid.profile.age_years = age;
    assert.throws(() => normalizeProfile(invalid, at));
  }
  const invalid = clone(p);
  invalid.context.last_use_status = "known";
  invalid.context.last_use_at = "yesterday";
  assert.throws(() => normalizeProfile(invalid, at));
  (invalid.history as unknown as JsonObject).use_frequency = "weekly";
  assert.throws(() => normalizeProfile(invalid, at));
});
test("check freezes original profile timestamp and recomputes elapsed use at its start", () => {
  const s = emptyWorkspace("account", at);
  s.profile.context = {
    last_use_status: "known",
    last_use_at: "2026-10-11T14:00:00.000Z",
    confirmed_at: at,
  };
  s.profile.history.time_since_use_min = 60;
  const c = createCheck(s, {
    now: later,
    id: randomUUID,
    kind: "measurement",
    accountRef: owner,
    contextConfirmed: true,
  });
  s.profile.profile.weight_kg = 100;
  assert.equal(c.snapshot.profile.weight_kg, null);
  assert.equal(c.snapshot.profile.recorded_at, at);
  assert.equal(c.snapshot.history.time_since_use_min, 120);
  assert.equal(
    c.context.self_report_context.last_use_at,
    "2026-10-11T14:00:00.000Z",
  );
  assert.equal(c.snapshot.created_at, c.snapshot.target_at);
  assert.equal(c.context.context_confirmed_at, later);
});
test("engineering fixture has an isolated unknown synthetic profile and absent simulated task", () => {
  const s = emptyWorkspace("account", at);
  s.profile.profile.age_years = 42;
  s.profile.profile.weight_kg = 95;
  s.profile.profile_version_id = randomUUID();
  const c = createCheck(s, {
    now: later,
    id: randomUUID,
    kind: "engineering_fixture",
    accountRef: owner,
    contextConfirmed: true,
  });
  assert.equal(c.snapshot.profile.age_years, null);
  assert.equal(c.snapshot.profile.weight_kg, null);
  assert.equal(c.snapshot.profile.source, "synthetic");
  assert.equal(c.context.profile_version_id, null);
  assert.equal(c.snapshot.task.source, "simulated");
});
test("context must be explicitly confirmed and a second draft cannot start", () => {
  const s = emptyWorkspace("guest", at);
  assert.throws(() =>
    createCheck(s, {
      now: at,
      id: randomUUID,
      kind: "guest_demo",
      contextConfirmed: false,
    }),
  );
  const c = createCheck(s, {
    now: at,
    id: randomUUID,
    kind: "guest_demo",
    contextConfirmed: true,
  });
  s.checks.push(c);
  assert.throws(() =>
    createCheck(s, {
      now: at,
      id: randomUUID,
      kind: "guest_demo",
      contextConfirmed: true,
    }),
  );
});
test("synthetic concentrations preserve unknown metabolites as null, with exact pg/mL conversion", () => {
  const { check } = fixture();
  assert.equal(check.snapshot.saliva[0]!.value_ng_ml, 12.5);
  for (const m of check.snapshot.saliva.slice(1)) {
    assert.equal(m.qualifier, "not_measured");
    assert.equal(m.value_ng_ml, null);
  }
  assert.equal(normalizeConcentration(12500, "pg/mL"), 12.5);
  assert.equal(normalizeConcentration(null, "ng/mL"), null);
  assert.throws(() => normalizeConcentration(-1, "ng/mL"));
});
test("save freezes all evidence and never queues upload", () => {
  const { check, state } = fixture();
  verifyCheck(check);
  assert.equal(check.delivery, "local_finalized");
  assert.equal(state.queue.length, 0);
  assert.equal(check.result!.probability, null);
  assert.equal(check.manifest!.attempts.length, 4);
  assert.equal(
    check.manifest!.selected.alcohol,
    check.attempts.at(-1)!.attempt_id,
  );
  assert.throws(() => simulatedCapture(check, "saliva", later, randomUUID));
});
test("guest check cannot upload and never acquires an account owner by sign-in", () => {
  const { state, check } = fixture("guest_demo");
  assert.throws(
    () => queueCheck(state, check.id, randomUUID, at),
    /never upload/,
  );
  assert.equal(check.snapshot.subject_ref, "local-guest");
  const account = emptyWorkspace("account", at);
  assert.equal(account.checks.length, 0);
});
test("a valid component cannot be retaken for a preferred reading", () => {
  const s = emptyWorkspace("guest", at);
  const c = createCheck(s, {
    now: at,
    id: randomUUID,
    kind: "guest_demo",
    contextConfirmed: true,
  });
  const captured = simulatedCapture(c, "cardiac", at, randomUUID);
  assert.throws(
    () => simulatedCapture(captured, "cardiac", later, randomUUID, "ppg"),
    /valid capture already exists/,
  );
});
test("process interruption preserves invalid task evidence with null aggregate features", () => {
  const s = emptyWorkspace("guest", at),
    c = createCheck(s, {
      now: at,
      id: randomUUID,
      kind: "guest_demo",
      contextConfirmed: true,
    }),
    started = startAttempt(c, "task", at, randomUUID, "prototype_sensor");
  const stopped = interruptStartedAttempts(started.check, later);
  assert.equal(stopped.attempts[0]!.status, "invalid");
  assert.equal(stopped.snapshot.task.status, "invalid");
  assert.ok(
    Object.values(stopped.snapshot.task.features as JsonObject).every(
      (x) => x === null,
    ),
  );
  const retry = startAttempt(
    stopped,
    "task",
    later,
    randomUUID,
    "prototype_sensor",
  );
  assert.equal(retry.attempt.supersedes_attempt_id, started.attempt.attempt_id);
  verifyCheck(freezeCheck(stopped, later, randomUUID));
});
test("altered context, selected projection, duplicate manifest and foreign attempt fail integrity", () => {
  const { check } = fixture();
  for (const mutate of [
    (c: CheckRecord) => {
      c.snapshot.profile.weight_kg = 100;
    },
    (c: CheckRecord) => {
      c.manifest!.attempts[1] = clone(c.manifest!.attempts[0]!);
      c.evidence_sha256 = digest(c.manifest);
    },
    (c: CheckRecord) => {
      c.attempts[0]!.session_id = randomUUID();
      c.manifest!.attempts[0]!.sha256 = digest(c.attempts[0]);
      c.evidence_sha256 = digest(c.manifest);
    },
    (c: CheckRecord) => {
      c.context.protocol_id = "changed";
      c.manifest!.context_sha256 = digest(c.context);
      c.evidence_sha256 = digest(c.manifest);
    },
  ]) {
    const broken = clone(check);
    mutate(broken);
    assert.throws(() => verifyCheck(broken));
  }
});
test("every research_estimate is rejected even when its shape could be schema-valid", () => {
  const { check } = fixture();
  assert.throws(
    () =>
      verifyResult(
        {
          ...check.result!,
          state: "research_estimate",
          model_id: "model",
          model_lifecycle: "active_research",
          endpoint_id: "endpoint",
          probability: 0.9,
          classification: "above_threshold",
          operating_threshold: 0.5,
          uncertainty_policy_id: "policy",
          provenance_summary: ["prototype_sensor"],
        },
        check,
      ),
    /cannot display or generate/,
  );
  assert.throws(() =>
    verifyResult({ ...check.result!, input_sha256: "0".repeat(64) }, check),
  );
});
test("profile responses require matching ETag and reject arbitrary context fields", () => {
  const p = emptyWorkspace("guest", at).profile,
    body = {
      profile_version_id: null,
      revision: 1,
      profile: p.profile,
      history: p.history,
      context: p.context,
    };
  assert.throws(() => parseProfile(body, '"0"', at));
  assert.throws(() =>
    parseProfile(
      { ...body, context: { ...p.context, owner: "fake" } },
      '"1"',
      at,
    ),
  );
  assert.equal(parseProfile(body, '"1"', at).revision, 1);
});
test("versioned notice verifies exact UTF8 including whitespace and rejects tampering", () => {
  const ref = { ...DEMO_NOTICE, content_path: "/v1/notices/demo" };
  assert.equal(verifyNotice(DEMO_NOTICE, ref).sha256, DEMO_NOTICE.sha256);
  assert.throws(() =>
    verifyNotice({ ...DEMO_NOTICE, text: DEMO_NOTICE.text + " " }, ref),
  );
});
test("retired generation quarantines ordinary data while preserving exact pending deletion replay", () => {
  const { check, state } = fixture();
  let queued = queueCheck(state, check.id, randomUUID, at);
  queued = queueMutation(
    queued,
    "deletion",
    { scope: "all_data", confirmation: true },
    randomUUID,
    at,
  );
  const next = quarantineGeneration(queued, 2);
  assert.equal(next.checks[0]!.delivery, "quarantined");
  assert.equal(next.queue[0]!.state, "quarantined");
  assert.equal(next.queue[1]!.state, "queued");
  assert.equal(next.queue[1]!.generation, 1);
  assert.equal(next.queue[1]!.keys.request, queued.queue[1]!.keys.request);
});
test("export cardinality rejects duplicates, missing selection and overbroad single scope", () => {
  const { state, check } = fixture();
  assert.throws(() =>
    validateSelection({
      kind: "single",
      session_ids: [check.id, randomUUID()],
    }),
  );
  assert.throws(() =>
    validateSelection({ kind: "all", session_ids: [check.id] }),
  );
  assert.throws(() => validateSelection({ kind: "selected", session_ids: [] }));
  assert.throws(() =>
    selectExportChecks(state, { kind: "single", session_ids: [randomUUID()] }),
  );
});
test("single-check export preserves exact scope and excludes unrelated current profile", () => {
  const first = fixture(),
    second = fixture();
  let state = replaceCheck(first.state, second.check);
  state.profile.profile.age_years = 99;
  const bytes = createLocalExport(
    state,
    { kind: "single", session_ids: [first.check.id] },
    later,
  );
  const inspected = inspectExportArchive(bytes),
    files = unzipSync(bytes),
    manifest = JSON.parse(decodeUtf8(files["manifest.json"]!)),
    profile = JSON.parse(decodeUtf8(files["profile.json"]!));
  assert.equal(inspected.fileCount, manifest.files.length + 1);
  assert.deepEqual(manifest.session_ids, [first.check.id]);
  assert.equal(profile.current, null);
  assert.equal(files[`checks/${second.check.id}.json`], undefined);
  assert.ok(!decodeUtf8(files["profile.json"]!).includes("99"));
});
test("empty all-data export contains profile metadata and no invented check", () => {
  const bytes = createLocalExport(
    emptyWorkspace("guest", at),
    { kind: "all", session_ids: [] },
    at,
  );
  assert.equal(inspectExportArchive(bytes).fileCount, 2);
});
test("export rejects file tampering and traversal or hidden files before sharing", () => {
  const { state, check } = fixture();
  const files = unzipSync(
    createLocalExport(
      state,
      { kind: "single", session_ids: [check.id] },
      later,
    ),
  );
  files["profile.json"] = new Uint8Array(utf8("{}"));
  assert.throws(
    () => inspectExportArchive(zipSync(files)),
    /differs from the manifest/,
  );
  assert.throws(
    () => inspectExportArchive(zipSync({ "../private.txt": utf8("x") })),
    /paths/,
  );
});
test("privacy jobs keep deletion-only and export-only terminal states separate", () => {
  const base = {
    schema_version: "1.0.0",
    kind: "deletion",
    job_id: randomUUID(),
    scope: "all_data",
    data_generation: 2,
    state: "pending",
    accepted_at: at,
    retained_categories: [],
    policy_version: "privacy-v1",
    attempt_count: 0,
    allowed_actions: ["refresh"],
  };
  assert.equal(parsePrivacyJob(base).state, "pending");
  assert.throws(() => parsePrivacyJob({ ...base, state: "expired" }));
  assert.throws(() =>
    parsePrivacyJob({ ...base, kind: "export", state: "partially_retained" }),
  );
  assert.throws(() =>
    parsePrivacyJob({ ...base, state: "partially_completed" }),
  );
});
test("HTTP concurrency and generation errors never force overwrite", () => {
  for (const status of [409, 412, 428])
    assert.equal(
      errorDisposition(new ApiError(status, "CONFLICT", "Conflict")).state,
      "conflict",
    );
  assert.equal(
    errorDisposition(new ApiError(410, "RETIRED", "Retired")).state,
    "quarantined",
  );
  assert.equal(
    errorDisposition(new ApiError(401, "AUTH", "Auth")).state,
    "auth_required",
  );
});
