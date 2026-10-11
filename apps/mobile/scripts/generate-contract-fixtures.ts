import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import {
  createCheck,
  emptyWorkspace,
  freezeCheck,
  settleAttempt,
  simulatedCapture,
  startAttempt,
  taskProjection,
  TASK_CONFIGURATION_ID,
  TASK_CONFIGURATION_SHA256,
} from "../src/core/domain";
import type { Channel, JsonObject } from "../src/core/types";
import type { NativeTaskResult } from "../modules/reaction-task/types";

// Host-generated integration fixtures only. They are never loaded by the application.
let sequence = 0;
const id = () =>
  `77777777-7777-4777-8777-${String(++sequence).padStart(12, "0")}`;
const owner = "00000000-0000-4000-8000-000000000001",
  at = "2026-10-11T00:00:00.000Z";
let fictional = createCheck(emptyWorkspace("local:contract-fixture", at), {
  now: at,
  id,
  kind: "engineering_fixture",
  accountRef: owner,
  contextConfirmed: true,
});
for (const channel of ["saliva", "eyes", "cardiac", "alcohol"] as Channel[])
  fictional = simulatedCapture(
    fictional,
    channel,
    at,
    id,
    channel === "cardiac" ? "ecg" : "ppg",
  );
fictional = freezeCheck(fictional, at, id);
const native = JSON.parse(
  readFileSync(
    "modules/reaction-task/fixtures/native-result-valid-contract-fixture.json",
    "utf8",
  ),
) as NativeTaskResult;
let practice = createCheck(
  emptyWorkspace("local:contract-native", native.startedAt),
  {
    now: native.startedAt,
    id,
    kind: "measurement",
    accountRef: owner,
    contextConfirmed: true,
  },
);
const started = startAttempt(
  practice,
  "task",
  native.startedAt,
  id,
  "prototype_sensor",
  TASK_CONFIGURATION_ID,
  TASK_CONFIGURATION_SHA256,
);
started.attempt.record_id = native.runId;
practice = settleAttempt(
  started.check,
  started.attempt.attempt_id,
  taskProjection(native as unknown as JsonObject, native.runId),
  native.status,
  native.endedAt,
  [...new Set(["uncalibrated", ...native.qualityFlags])],
  { native_result: native as unknown as JsonObject, contract_fixture: true },
);
practice = freezeCheck(practice, native.endedAt, id);
mkdirSync("testfixtures", { recursive: true });
for (const [name, value] of [
  ["fictional-check-contract", fictional],
  ["native-check-contract", practice],
] as const)
  writeFileSync(
    `testfixtures/${name}.json`,
    JSON.stringify(value, null, 2) + "\n",
  );
writeFileSync(
  "/tmp/mobile-check-bundle.json",
  JSON.stringify(fictional, null, 2),
);
writeFileSync(
  "/tmp/mobile-native-check-bundle.json",
  JSON.stringify(practice, null, 2),
);
console.log(
  JSON.stringify(
    {
      fictional: {
        id: fictional.id,
        snapshot: fictional.snapshot_sha256,
        evidence: fictional.evidence_sha256,
      },
      nativeContract: {
        id: practice.id,
        snapshot: practice.snapshot_sha256,
        evidence: practice.evidence_sha256,
        actualNativeExecution: false,
      },
    },
    null,
    2,
  ),
);
