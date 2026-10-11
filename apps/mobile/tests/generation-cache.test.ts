import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import {
  createCheck,
  emptyWorkspace,
  freezeCheck,
  quarantineGeneration,
  selectExportChecks,
} from "../src/core/domain";
import { queueMutation } from "../src/services/sync";
import { clone } from "../src/core/integrity";
import type { PrivacyJob } from "../src/core/types";
import { createLocalExport, decodeUtf8 } from "../src/services/export";
import { unzipSync } from "fflate";

const at = "2026-10-11T15:00:00.000Z";
function job(kind: PrivacyJob["kind"], generation: number): PrivacyJob {
  return {
    schema_version: "1.0.0",
    kind,
    job_id: randomUUID(),
    scope: kind === "deletion" ? "all_data" : { kind: "all", session_ids: [] },
    data_generation: generation,
    state: "completed",
    accepted_at: at,
    retained_categories: [],
    policy_version: "fixture-policy-1",
    attempt_count: 1,
    allowed_actions: [],
  };
}

test("generation quarantine clears cached history, selections and consent without discarding exact deletion receipts", () => {
  let state = emptyWorkspace("account:fixture", at, 1);
  const checkId = randomUUID();
  state.historyIndex = [
    { session_id: checkId, created_at: at, mode: "analytical" },
  ];
  state.historyCursor = "opaque-old-generation-cursor";
  state.exportEntry = {
    source: "cloud",
    selection: { kind: "single", session_ids: [checkId] },
  };
  state.studies = [{ study_id: randomUUID(), consent: { state: "active" } }];
  const oldExport = job("export", 1),
    currentExport = job("export", 2),
    deletionReceipt = job("deletion", 1);
  state.jobs = [oldExport, currentExport, deletionReceipt];
  state = queueMutation(
    state,
    "deletion",
    { scope: "all_data", confirmation: true },
    randomUUID,
    at,
  );
  state = queueMutation(
    state,
    "export",
    {
      selection: { kind: "all", session_ids: [] },
      format: "json_zip",
      include_raw: false,
    },
    randomUUID,
    at,
  );
  const before = clone(state),
    next = quarantineGeneration(state, 2);
  assert.deepEqual(next.historyIndex, []);
  assert.equal(next.historyCursor, null);
  assert.equal(next.exportEntry, null);
  assert.deepEqual(next.studies, []);
  assert.deepEqual(next.jobs, [currentExport, deletionReceipt]);
  assert.deepEqual(
    next.queue.find((item) => item.kind === "deletion"),
    before.queue.find((item) => item.kind === "deletion"),
  );
  assert.equal(
    next.queue.find((item) => item.kind === "export")?.state,
    "quarantined",
  );
  assert.equal(
    next.queue.find((item) => item.kind === "export")?.generation,
    1,
  );
  assert.deepEqual(state, before);
});

test("unknown current generation invalidates every cached export but preserves deletion reconciliation evidence", () => {
  const state = emptyWorkspace("account:fixture", at, 1);
  state.capabilities = {
    account_ref: "00000000-0000-4000-8000-000000000001",
    data_generation: 1,
    account_state: "active",
    server_time: at,
    inference_available: false,
    notice: {
      version: "fixture-1",
      sha256: "a".repeat(64),
      locale: "en",
      content_path: "/v1/notices/fixture-1",
      mandatory: true,
    },
    channels: {
      saliva: {
        available: false,
        reason_codes: ["NO_QUALIFIED_CONFIGURATION"],
      },
    },
    studies: [],
  };
  const receipt = job("deletion", 2);
  state.jobs = [job("export", 1), job("export", 2), receipt];
  state.historyIndex = [{ session_id: randomUUID() }];
  state.historyCursor = "opaque-cursor";
  const next = quarantineGeneration(state, -1);
  assert.deepEqual(next.jobs, [receipt]);
  assert.deepEqual(next.historyIndex, []);
  assert.equal(next.historyCursor, null);
  assert.equal(
    next.capabilities,
    null,
    "old capability authority cannot survive unknown retirement",
  );
  assert.notEqual(state.capabilities, null, "the input remains immutable");
  assert.equal(
    next.generation,
    1,
    "the original payload generation is never rebound",
  );
});

function frozen(generation: number) {
  const state = emptyWorkspace("account:fixture", at, generation);
  return freezeCheck(
    createCheck(state, {
      now: at,
      id: randomUUID,
      kind: "measurement",
      accountRef: "00000000-0000-4000-8000-000000000001",
      contextConfirmed: true,
    }),
    at,
    randomUUID,
  );
}

test("all-record device export excludes tombstoned and retired-generation retained records", () => {
  const state = emptyWorkspace("account:fixture", at, 2);
  const retired = frozen(1),
    quarantined = frozen(2),
    current = frozen(2);
  quarantined.delivery = "quarantined";
  state.checks = [retired, quarantined, current];
  assert.deepEqual(
    selectExportChecks(state, { kind: "all", session_ids: [] }).map(
      (check) => check.id,
    ),
    [current.id],
  );
  assert.equal(
    state.checks.length,
    3,
    "quarantined records remain retained without becoming export-eligible",
  );
});

test("explicit export containing one retired or quarantined check fails as a whole and never expands its scope", () => {
  const state = emptyWorkspace("account:fixture", at, 2);
  const retired = frozen(1),
    quarantined = frozen(2),
    current = frozen(2);
  quarantined.delivery = "quarantined";
  state.checks = [retired, quarantined, current];
  for (const unavailable of [retired, quarantined]) {
    assert.throws(
      () =>
        selectExportChecks(state, {
          kind: "single",
          session_ids: [unavailable.id],
        }),
      /not available/,
    );
    const selection = {
      kind: "selected" as const,
      session_ids: [current.id, unavailable.id],
    };
    assert.throws(() => selectExportChecks(state, selection), /not available/);
    assert.deepEqual(selection.session_ids, [current.id, unavailable.id]);
  }
  assert.deepEqual(
    selectExportChecks(state, {
      kind: "single",
      session_ids: [current.id],
    }).map((check) => check.id),
    [current.id],
  );
});

test("a fresh all-device export after retirement contains no prior current demographic or use context", () => {
  const state = emptyWorkspace("account:fixture", at, 1);
  state.profile.profile = {
    ...state.profile.profile,
    age_years: 47,
    weight_kg: 81,
    height_cm: 176,
    bmi: 26.15,
  };
  state.profile.history = {
    ...state.profile.history,
    use_frequency: "daily",
    route: "oral",
    time_since_use_min: 90,
    sleep_hours: 5.5,
  };
  state.profile.context = {
    last_use_status: "known",
    last_use_at: "2026-10-11T13:30:00.000Z",
    confirmed_at: at,
  };
  state.checks = [frozen(1)];
  const clearedAt = "2026-10-11T16:00:00.000Z",
    next = quarantineGeneration(state, 2, clearedAt);
  next.generation = 2;
  const archive = unzipSync(
    createLocalExport(next, { kind: "all", session_ids: [] }, clearedAt),
  );
  const profile = JSON.parse(decodeUtf8(archive["profile.json"]!));
  assert.equal(profile.current.profile.age_years, null);
  assert.equal(profile.current.profile.weight_kg, null);
  assert.equal(profile.current.profile.height_cm, null);
  assert.equal(profile.current.profile.bmi, null);
  assert.equal(profile.current.history.use_frequency, "unknown");
  assert.equal(profile.current.history.route, "unknown");
  assert.equal(profile.current.history.time_since_use_min, null);
  assert.equal(profile.current.history.sleep_hours, null);
  assert.equal(profile.current.context.last_use_status, "unknown");
  assert.equal(profile.current.context.last_use_at, null);
  assert.equal(profile.current.profile.recorded_at, clearedAt);
  assert.deepEqual(profile.versions, []);
  assert.equal(
    Object.keys(archive).some((path) => path.startsWith("checks/")),
    false,
  );
  assert.equal(
    state.profile.profile.age_years,
    47,
    "the input and original frozen evidence are not rewritten",
  );
});
