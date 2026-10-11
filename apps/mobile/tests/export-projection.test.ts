import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import {
  createCheck,
  emptyWorkspace,
  simulatedCapture,
  startAttempt,
  settleAttempt,
  taskProjection,
} from "../src/core/domain";
import { verifyAttemptProjection } from "../src/core/exportProjection";
import { clone } from "../src/core/integrity";

const at = "2026-10-11T14:00:00.000Z";
function fixture() {
  const state = emptyWorkspace("guest", at);
  let check = createCheck(state, {
    now: at,
    id: randomUUID,
    kind: "guest_demo",
    contextConfirmed: true,
  });
  for (const channel of ["saliva", "eyes", "cardiac", "alcohol"] as const)
    check = simulatedCapture(check, channel, at, randomUUID);
  return check;
}
test("every retained simulated sample, eye, PPG and separate alcohol projection satisfies its exact typed evidence", () => {
  const check = fixture();
  for (const attempt of check.attempts)
    assert.deepEqual(
      verifyAttemptProjection(attempt, check.snapshot),
      attempt.component_metadata.projection,
    );
});
test("an unselected projection cannot hide unknown metadata or a different run/sample identity", () => {
  const check = fixture();
  for (const original of check.attempts) {
    const attempt = clone(original);
    attempt.component_metadata.unapproved = { sample: "unrelated" };
    assert.throws(
      () => verifyAttemptProjection(attempt, check.snapshot),
      /Unsupported/,
    );
  }
  const saliva = clone(check.attempts[0]!);
  saliva.record_id = randomUUID();
  assert.throws(
    () => verifyAttemptProjection(saliva, check.snapshot),
    /sample identity/,
  );
});
test("retained sample unit conversion, censored null and collection binding are independently checked", () => {
  const check = fixture();
  for (const change of [
    (p: any) => {
      p.saliva[0].original_report.value = 99_999;
    },
    (p: any) => {
      p.saliva[0].qualifier = "below_loq";
    },
    (p: any) => {
      p.saliva[0].sample_id = randomUUID();
    },
    (p: any) => {
      p.saliva[0].limits.loq_ng_ml = 99;
    },
  ]) {
    const attempt = clone(check.attempts[0]!);
    change(attempt.component_metadata.projection);
    assert.throws(() => verifyAttemptProjection(attempt, check.snapshot));
  }
});
test("metadata nested event/frame/report fields stay bounded and cannot become hidden payload containers", () => {
  const check = fixture(),
    saliva = clone(check.attempts[0]!);
  saliva.component_metadata.storage_handling_events = [
    { event: "received", occurred_at: at, temperature_c: 4 },
  ];
  assert.doesNotThrow(() => verifyAttemptProjection(saliva, check.snapshot));
  saliva.component_metadata.storage_handling_events = [
    { event: { unbound: true } },
  ];
  assert.throws(
    () => verifyAttemptProjection(saliva, check.snapshot),
    /nested/,
  );
  const eyes = clone(check.attempts.find((a) => a.component === "eyes")!);
  eyes.component_metadata.frame_timing = { unrelated: 1 };
  assert.throws(
    () => verifyAttemptProjection(eyes, check.snapshot),
    /Unsupported/,
  );
});
test("an unmounted invalid native arm may omit acquired native evidence but valid prototype task cannot", () => {
  const check = fixture(),
    start = startAttempt(
      check,
      "task",
      at,
      randomUUID,
      "prototype_sensor",
      "dev",
      String(check.snapshot.task.config_sha256),
    );
  const invalid = {
    ...clone(check.snapshot.task),
    task_id: start.attempt.record_id,
    source: "prototype_sensor",
    status: "invalid",
    started_at: at,
    ended_at: at,
    quality_flags: ["INTERRUPTED"],
  };
  const ended = settleAttempt(
    start.check,
    start.attempt.attempt_id,
    invalid,
    "invalid",
    at,
    ["INTERRUPTED"],
  );
  assert.doesNotThrow(() =>
    verifyAttemptProjection(ended.attempts.at(-1)!, ended.snapshot),
  );
  const native = JSON.parse(
    readFileSync(
      "modules/reaction-task/fixtures/native-result-valid-contract-fixture.json",
      "utf8",
    ),
  );
  native.runId = start.attempt.record_id;
  native.startedAt = at;
  native.endedAt = "2026-10-11T14:01:52.408Z";
  const valid = settleAttempt(
    start.check,
    start.attempt.attempt_id,
    taskProjection(native, start.attempt.record_id),
    "valid",
    native.endedAt,
    ["uncalibrated"],
  );
  assert.throws(
    () => verifyAttemptProjection(valid.attempts.at(-1)!, valid.snapshot),
    /full native evidence/,
  );
});
