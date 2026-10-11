import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import {
  cardiacAttemptModality,
  createCheck,
  emptyWorkspace,
  freezeCheck,
  interruptStartedAttempts,
  selectCardiacAttempt,
  settleAttempt,
  simulatedCapture,
  startAttempt,
  verifyCheck,
} from "../src/core/domain";
import { clone, digest } from "../src/core/integrity";
import type { CheckRecord, JsonObject } from "../src/core/types";

const at = "2026-10-11T16:00:00.000Z";
const later = "2026-10-11T16:01:00.000Z";
const done = "2026-10-11T16:02:00.000Z";
function draft(): CheckRecord {
  return createCheck(emptyWorkspace("guest:cardiac-test", at), {
    now: at,
    id: randomUUID,
    kind: "guest_demo",
    contextConfirmed: true,
  });
}

test("one PPG plus one ECG is retained and requires an explicit final choice", () => {
  const ppg = simulatedCapture(draft(), "cardiac", at, randomUUID, "ppg");
  const first = ppg.attempts[0]!;
  const firstHash = digest(first),
    firstProjection = clone(ppg.snapshot.cardiac);
  const both = simulatedCapture(ppg, "cardiac", later, randomUUID, "ecg");
  assert.equal(both.attempts.length, 2);
  assert.equal(digest(both.attempts[0]), firstHash);
  assert.equal(both.attempts[1]!.supersedes_attempt_id, null);
  assert.equal(both.selected_cardiac_attempt_id, null);
  assert.deepEqual(both.snapshot.cardiac, firstProjection);
  assert.throws(() => freezeCheck(both, done, randomUUID), {
    code: "CARDIAC_SELECTION_REQUIRED",
  });

  for (const chosen of both.attempts) {
    const selected = selectCardiacAttempt(both, chosen.attempt_id, done);
    const saved = freezeCheck(selected, done, randomUUID);
    verifyCheck(saved);
    assert.equal(saved.manifest!.selected.cardiac, chosen.attempt_id);
    assert.deepEqual(
      saved.snapshot.cardiac,
      chosen.component_metadata.projection,
    );
    assert.equal(saved.manifest!.attempts.length, 2);
    assert.equal(digest(saved.attempts[0]), firstHash);
    assert.deepEqual(
      saved.attempts.map((a) => a.supersedes_attempt_id),
      [null, null],
    );
  }
});

test("ECG followed by PPG retains the same choice semantics and cannot relabel ECG", () => {
  const ecg = simulatedCapture(draft(), "cardiac", at, randomUUID, "ecg");
  const both = simulatedCapture(ecg, "cardiac", later, randomUUID, "ppg");
  assert.equal(both.snapshot.cardiac.modality, "ecg");
  assert.deepEqual(both.attempts.map(cardiacAttemptModality), ["ecg", "ppg"]);
  const saved = freezeCheck(
    selectCardiacAttempt(both, both.attempts[1]!.attempt_id),
    done,
    randomUUID,
  );
  assert.equal(saved.snapshot.cardiac.modality, "ppg");
  assert.equal(saved.snapshot.cardiac.ecg_status, "not_collected");
  assert.equal(saved.snapshot.cardiac.ecg_rmssd_ms, null);
  assert.equal(
    (saved.attempts[0]!.component_metadata.projection as JsonObject).modality,
    "ecg",
  );
});

test("same-modality valid retakes stay prohibited before and after collecting the alternative", () => {
  const ppg = simulatedCapture(draft(), "cardiac", at, randomUUID, "ppg");
  assert.throws(
    () => simulatedCapture(ppg, "cardiac", later, randomUUID, "ppg"),
    { code: "VALID_CAPTURE_EXISTS" },
  );
  const both = simulatedCapture(ppg, "cardiac", later, randomUUID, "ecg");
  for (const modality of ["ppg", "ecg"] as const)
    assert.throws(
      () => simulatedCapture(both, "cardiac", done, randomUUID, modality),
      { code: "VALID_CAPTURE_EXISTS" },
    );
});

test("interrupted ECG alternative preserves valid PPG and does not copy its physiological features", () => {
  const ppg = simulatedCapture(draft(), "cardiac", at, randomUUID, "ppg");
  const original = clone(ppg.snapshot.cardiac);
  const started = startAttempt(
    ppg,
    "cardiac",
    later,
    randomUUID,
    "simulated",
    "ecg-fixture",
    null,
    "ecg",
  );
  assert.equal(started.attempt.supersedes_attempt_id, null);
  const stopped = interruptStartedAttempts(started.check, done);
  const failed = stopped.attempts[1]!;
  const projection = failed.component_metadata.projection as JsonObject;
  assert.deepEqual(stopped.snapshot.cardiac, original);
  assert.equal(
    stopped.selected_cardiac_attempt_id,
    ppg.attempts[0]!.attempt_id,
  );
  assert.equal(projection.modality, "ecg");
  assert.equal(projection.heart_rate_bpm, null);
  assert.equal(projection.ecg_rmssd_ms, null);
  assert.equal(projection.sample_rate_hz, null);
  assert.equal(projection.raw_artifact_id, null);
  const saved = freezeCheck(stopped, done, randomUUID);
  assert.equal(saved.manifest!.selected.cardiac, ppg.attempts[0]!.attempt_id);
  const retry = startAttempt(
    stopped,
    "cardiac",
    done,
    randomUUID,
    "simulated",
    "ecg-fixture",
    null,
    "ecg",
  );
  assert.equal(retry.attempt.supersedes_attempt_id, failed.attempt_id);
});

test("different-modality invalid attempts never become a retry predecessor", () => {
  const first = startAttempt(
    draft(),
    "cardiac",
    at,
    randomUUID,
    "simulated",
    "ppg-fixture",
    null,
    "ppg",
  );
  const stopped = interruptStartedAttempts(first.check, later);
  const other = startAttempt(
    stopped,
    "cardiac",
    done,
    randomUUID,
    "simulated",
    "ecg-fixture",
    null,
    "ecg",
  );
  assert.equal(other.attempt.supersedes_attempt_id, null);
  const same = startAttempt(
    stopped,
    "cardiac",
    done,
    randomUUID,
    "simulated",
    "ppg-fixture",
    null,
    "ppg",
  );
  assert.equal(same.attempt.supersedes_attempt_id, first.attempt.attempt_id);
  assert.equal(
    freezeCheck(stopped, done, randomUUID).snapshot.cardiac.heart_rate_bpm,
    null,
  );
});

test("skipping an ECG alternative cannot erase valid selected PPG", () => {
  const ppg = simulatedCapture(draft(), "cardiac", at, randomUUID, "ppg");
  const started = startAttempt(
    ppg,
    "cardiac",
    later,
    randomUUID,
    "simulated",
    "ecg-fixture",
    null,
    "ecg",
  );
  const skipped = settleAttempt(
    started.check,
    started.attempt.attempt_id,
    {
      status: "not_collected",
      source: "simulated",
      started_at: null,
      ended_at: null,
      quality_flags: ["SKIPPED"],
      acquisition_config_id: "ecg-fixture",
      modality: "ecg",
      heart_rate_bpm: null,
      ecg_status: "not_collected",
      ecg_rmssd_ms: null,
      sample_rate_hz: null,
      raw_artifact_id: null,
    },
    "not_collected",
    later,
    ["SKIPPED"],
  );
  assert.deepEqual(skipped.snapshot.cardiac, ppg.snapshot.cardiac);
  const saved = freezeCheck(skipped, done, randomUUID);
  assert.equal(saved.manifest!.selected.cardiac, ppg.attempts[0]!.attempt_id);
  assert.equal(saved.attempts[1]!.status, "not_collected");
});

test("a cardiac modality is pinned at start and cannot be supplied to another component", () => {
  assert.throws(
    () => startAttempt(draft(), "cardiac", at, randomUUID, "simulated"),
    { code: "CARDIAC_MODALITY_REQUIRED" },
  );
  assert.throws(
    () =>
      startAttempt(
        draft(),
        "task",
        at,
        randomUUID,
        "prototype_sensor",
        null,
        null,
        "ecg",
      ),
    { code: "CARDIAC_MODALITY_MISPLACED" },
  );
  const started = startAttempt(
    draft(),
    "cardiac",
    at,
    randomUUID,
    "simulated",
    "ppg-fixture",
    null,
    "ppg",
  );
  const projection = {
    ...started.check.snapshot.cardiac,
    status: "valid",
    source: "simulated",
    started_at: at,
    ended_at: later,
    modality: "ecg",
  } as JsonObject;
  assert.throws(
    () =>
      settleAttempt(
        started.check,
        started.attempt.attempt_id,
        projection,
        "valid",
        later,
      ),
    { code: "CARDIAC_MODALITY_CHANGED" },
  );
  projection.modality = "ppg";
  assert.throws(
    () =>
      settleAttempt(
        started.check,
        started.attempt.attempt_id,
        projection,
        "valid",
        later,
        [],
        { modality: "ecg" },
      ),
    { code: "CARDIAC_MODALITY_CHANGED" },
  );
});

test("selection rejects another check, invalid attempts, active capture and saved changes", () => {
  const ppg = simulatedCapture(draft(), "cardiac", at, randomUUID, "ppg");
  const id = ppg.attempts[0]!.attempt_id;
  assert.throws(() => selectCardiacAttempt(ppg, randomUUID()), {
    code: "CARDIAC_SELECTION_INVALID",
  });
  const started = startAttempt(
    ppg,
    "cardiac",
    later,
    randomUUID,
    "simulated",
    "ecg-fixture",
    null,
    "ecg",
  );
  assert.throws(() => selectCardiacAttempt(started.check, id), {
    code: "ACTIVE_CAPTURE",
  });
  const stopped = interruptStartedAttempts(started.check, done);
  assert.throws(
    () => selectCardiacAttempt(stopped, started.attempt.attempt_id),
    { code: "CARDIAC_SELECTION_INVALID" },
  );
  const saved = freezeCheck(stopped, done, randomUUID);
  assert.throws(() => selectCardiacAttempt(saved, id), {
    code: "FROZEN_CHECK",
  });
  assert.throws(
    () =>
      startAttempt(
        saved,
        "cardiac",
        done,
        randomUUID,
        "simulated",
        null,
        null,
        "ecg",
      ),
    { code: "FROZEN_CHECK" },
  );
});

test("manifest cannot silently change the cardiac choice even after rehashing", () => {
  const both = simulatedCapture(
    simulatedCapture(draft(), "cardiac", at, randomUUID, "ppg"),
    "cardiac",
    later,
    randomUUID,
    "ecg",
  );
  const saved = freezeCheck(
    selectCardiacAttempt(both, both.attempts[0]!.attempt_id),
    done,
    randomUUID,
  );
  const changed = clone(saved);
  changed.manifest!.selected.cardiac = both.attempts[1]!.attempt_id;
  changed.evidence_sha256 = digest(changed.manifest);
  assert.throws(() => verifyCheck(changed), {
    code: "CARDIAC_SELECTION_CHANGED",
  });
  const omitted = clone(saved);
  omitted.manifest!.selected.cardiac = null;
  omitted.evidence_sha256 = digest(omitted.manifest);
  omitted.selected_cardiac_attempt_id = null;
  assert.throws(() => verifyCheck(omitted), {
    code: "CARDIAC_SELECTION_INVALID",
  });
});

test("task score retake protection remains separate from permitted cardiac alternatives", () => {
  const initial = draft();
  const start = startAttempt(
    initial,
    "task",
    at,
    randomUUID,
    "prototype_sensor",
  );
  const terminal = settleAttempt(
    start.check,
    start.attempt.attempt_id,
    {
      ...initial.snapshot.task,
      status: "valid",
      source: "prototype_sensor",
      started_at: at,
      ended_at: later,
      task_id: start.attempt.record_id,
    },
    "valid",
    later,
  );
  assert.throws(
    () => startAttempt(terminal, "task", done, randomUUID, "prototype_sensor"),
    { code: "VALID_CAPTURE_EXISTS" },
  );
});
