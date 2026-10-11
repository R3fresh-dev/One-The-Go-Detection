import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { clone, digest } from "../src/core/integrity";
import {
  createCheck,
  emptyWorkspace,
  freezeCheck,
  replaceCheck,
} from "../src/core/domain";
import {
  localReplacementChecks,
  mergeReplacementPage,
  parseReplacementLinks,
  verifyReplacementTarget,
} from "../src/core/replacements";
import { parseRemoteCheck } from "../src/core/remote";

const at = "2026-10-11T10:00:00.000Z";
function fixture() {
  let state = emptyWorkspace("fixture-workspace", at);
  const original = freezeCheck(
    createCheck(state, {
      now: at,
      id: randomUUID,
      kind: "guest_demo",
      contextConfirmed: true,
    }),
    at,
    randomUUID,
  );
  state = replaceCheck(state, original);
  const replacement = freezeCheck(
    createCheck(state, {
      now: "2026-10-12T10:00:00.000Z",
      id: randomUUID,
      kind: "guest_demo",
      contextConfirmed: true,
      supersedes: original.id,
    }),
    "2026-10-12T10:01:00.000Z",
    randomUUID,
  );
  state = replaceCheck(state, replacement);
  return { state, original, replacement };
}
test("local original and replacement links are bidirectional without changing either snapshot", () => {
  const { state, original, replacement } = fixture(),
    before = digest(state);
  assert.equal(
    localReplacementChecks(state, original).items[0]!.id,
    replacement.id,
  );
  assert.equal(
    localReplacementChecks(state, replacement).previous!.id,
    original.id,
  );
  verifyReplacementTarget(original, replacement, "replacement");
  verifyReplacementTarget(replacement, original, "previous");
  assert.equal(digest(state), before);
  assert.notEqual(original.snapshot.target_at, replacement.snapshot.target_at);
  assert.notEqual(
    original.snapshot.sample.sample_id,
    replacement.snapshot.sample.sample_id,
  );
});
test("retired, quarantined, foreign-workspace and unfinished replacement records are excluded", () => {
  for (const edit of [
    { generation: 2 },
    { workspace: "other" },
    { delivery: "quarantined" as const },
    { frozen: false },
  ]) {
    const { state, original, replacement } = fixture();
    state.checks = [original, { ...replacement, ...edit }];
    assert.deepEqual(localReplacementChecks(state, original).items, []);
    assert.throws(
      () => verifyReplacementTarget(original, state.checks[1]!, "replacement"),
      /expected immutable/,
    );
  }
});
test("the replacement wire parser binds parent hash, generation, frozen states and direct predecessor", () => {
  const { original, replacement } = fixture();
  const page = {
    schema_version: "1.0.0",
    session_id: replacement.id,
    data_generation: replacement.generation,
    base_snapshot_sha256: replacement.snapshot_sha256,
    previous: {
      session_id: original.id,
      created_at: original.snapshot.created_at,
      state: "completed",
    },
    items: [],
    next_cursor: null,
  };
  assert.equal(
    parseReplacementLinks(page, replacement).previous?.session_id,
    original.id,
  );
  for (const mutation of [
    { schema_version: "2.0.0" },
    { data_generation: 2 },
    { base_snapshot_sha256: "0".repeat(64) },
    { session_id: original.id },
    { previous: { ...page.previous, session_id: randomUUID() } },
    { previous: { ...page.previous, state: "draft" } },
    { next_cursor: "unusable-empty-page" },
    { undocumented: true },
  ]) {
    assert.throws(() =>
      parseReplacementLinks({ ...page, ...mutation }, replacement),
    );
  }
});
test("bounded replacement pages reject duplicate/self links and preserve explicit remaining cursor", () => {
  const { original, replacement } = fixture(),
    item = {
      session_id: replacement.id,
      created_at: replacement.snapshot.created_at,
      state: "completed",
    };
  const value = {
    schema_version: "1.0.0",
    session_id: original.id,
    data_generation: 1,
    base_snapshot_sha256: original.snapshot_sha256,
    previous: null,
    items: [item],
    next_cursor: "opaque-next",
  };
  const first = parseReplacementLinks(value, original),
    cached = mergeReplacementPage(undefined, first, false, at);
  assert.equal(cached.next_cursor, "opaque-next");
  assert.throws(() =>
    parseReplacementLinks({ ...value, items: [item, item] }, original),
  );
  assert.throws(() =>
    parseReplacementLinks(
      { ...value, items: [{ ...item, session_id: original.id }] },
      original,
    ),
  );
  assert.throws(() =>
    parseReplacementLinks(
      { ...value, next_cursor: "x".repeat(1025) },
      original,
    ),
  );
  assert.throws(
    () => mergeReplacementPage(cached, first, true, at),
    /navigation changed/,
  );
  const second = parseReplacementLinks(
    {
      ...value,
      items: [{ ...item, session_id: randomUUID() }],
      next_cursor: null,
    },
    original,
  );
  assert.equal(mergeReplacementPage(cached, second, true, at).items.length, 2);
  assert.equal(
    mergeReplacementPage(cached, second, true, at).next_cursor,
    null,
  );
});
test("a linked target must prove the direct relation before navigation", () => {
  const { original, replacement } = fixture(),
    changed = clone(replacement);
  changed.snapshot.supersedes_session_id = randomUUID();
  assert.throws(
    () => verifyReplacementTarget(original, changed, "replacement"),
    /expected immutable/,
  );
  assert.throws(
    () => verifyReplacementTarget(original, original, "previous"),
    /expected immutable/,
  );
});
test("a remote draft with an uploaded snapshot is not treated as a frozen readable result", () => {
  const { state, original } = fixture();
  assert.throws(
    () =>
      parseRemoteCheck(
        {
          session_id: original.id,
          state: "draft",
          revision: 2,
          mode: "synthetic",
          created_at: at,
          snapshot: original.snapshot,
          snapshot_sha256: original.snapshot_sha256,
          evidence_sha256: original.evidence_sha256,
          result: null,
          context: original.context,
          manifest: original.manifest,
          attempts: original.attempts,
          alcohol: null,
        },
        state,
      ),
    /still uploading/,
  );
});
