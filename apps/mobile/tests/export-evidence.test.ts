import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import {
  createCheck,
  emptyWorkspace,
  freezeCheck,
  interruptStartedAttempts,
  selectCardiacAttempt,
  settleAttempt,
  simulatedCapture,
  startAttempt,
  taskProjection,
  TASK_CONFIGURATION_ID,
  TASK_CONFIGURATION_SHA256,
} from "../src/core/domain";
import {
  projectSyntheticDevice,
  syntheticConfigurationDigest,
} from "../src/core/deviceProjection";
import { verifyExportEvidence } from "../src/core/exportEvidence";
import { clone, digest } from "../src/core/integrity";
import type { CheckRecord, JsonObject } from "../src/core/types";
import type { NativeTaskResult } from "../modules/reaction-task/types";
import { DeviceControllerImpl } from "../src/device/controller";
import { LocalSimulatorTransport } from "../src/device/simulator";
import type { SyntheticDeviceCapture } from "../src/device/types";
import { getSyntheticSignalFailure } from "../src/device/signalFailure";
import { SyntheticSignalError } from "../src/device/signal";

const at = "2026-10-11T00:00:00.000Z",
  later = "2026-10-11T01:00:00.000Z";
const owner = "00000000-0000-4000-8000-000000000001";
function draft(kind: CheckRecord["kind"] = "guest_demo", now = at) {
  return createCheck(
    emptyWorkspace(kind === "guest_demo" ? "guest:local" : "account:test", now),
    {
      now,
      id: randomUUID,
      kind,
      accountRef: kind === "guest_demo" ? undefined : owner,
      contextConfirmed: true,
    },
  );
}
function rehash(check: CheckRecord) {
  check.context.profile_snapshot_sha256 = digest(check.snapshot.profile);
  check.context.history_snapshot_sha256 = digest(check.snapshot.history);
  check.manifest!.context_sha256 = digest(check.context);
  check.manifest!.attempts = check.attempts.map((a) => ({
    attempt_id: a.attempt_id,
    sha256: digest(a),
  }));
  check.snapshot_sha256 = digest(check.snapshot);
  check.evidence_sha256 = digest(check.manifest);
  if (check.result) check.result.input_sha256 = check.snapshot_sha256;
  return check;
}
function nativeFixture(): NativeTaskResult {
  // This fixture is host-generated, fictional contract evidence. It is never
  // presented as an executed native task, participant data or calibrated timing.
  return JSON.parse(
    readFileSync(
      "modules/reaction-task/fixtures/native-result-valid-contract-fixture.json",
      "utf8",
    ),
  ) as NativeTaskResult;
}
function nativeCheck(native = nativeFixture()): CheckRecord {
  const started = startAttempt(
    draft("measurement", native.startedAt),
    "task",
    native.startedAt,
    randomUUID,
    "prototype_sensor",
    TASK_CONFIGURATION_ID,
    TASK_CONFIGURATION_SHA256,
  );
  native.runId = started.attempt.record_id;
  const body = native as unknown as JsonObject;
  const next = settleAttempt(
    started.check,
    started.attempt.attempt_id,
    taskProjection(body, native.runId),
    native.status,
    native.endedAt,
    ["uncalibrated", ...native.qualityFlags],
    { native_result: body, contract_fixture: true },
  );
  return freezeCheck(
    next,
    new Date(Date.parse(native.endedAt) + 1000).toISOString(),
    randomUUID,
  );
}

test("exports verify exact originals and retain supported absent self-report context", () => {
  for (const kind of [
    "guest_demo",
    "engineering_fixture",
    "measurement",
  ] as const) {
    const check = freezeCheck(draft(kind), later, randomUUID);
    const original = digest(check);
    assert.doesNotThrow(() => verifyExportEvidence(check));
    (check.context as unknown as JsonObject).self_report_context = null;
    rehash(check);
    assert.doesNotThrow(() => verifyExportEvidence(check));
    assert.equal(digest(check), digest(clone(check)));
    assert.notEqual(
      original,
      digest(check),
      "test changes are explicit; verifier never rewrites them",
    );
  }
  assert.throws(() => verifyExportEvidence(draft()));
  const retired = freezeCheck(draft(), later, randomUUID);
  retired.delivery = "quarantined";
  assert.throws(() => verifyExportEvidence(retired));
});

test("rehashed unselected cardiac projection and metadata cannot bypass export validation", () => {
  let check = simulatedCapture(draft(), "cardiac", at, randomUUID, "ppg");
  const selected = check.attempts[0]!.attempt_id;
  check = simulatedCapture(check, "cardiac", at, randomUUID, "ecg");
  check = freezeCheck(selectCardiacAttempt(check, selected), later, randomUUID);
  assert.doesNotThrow(() => verifyExportEvidence(check));
  for (const alter of [
    (c: CheckRecord) => {
      (c.attempts[1]!.component_metadata.projection as JsonObject).unapproved =
        "hidden";
    },
    (c: CheckRecord) => {
      c.attempts[1]!.component_metadata.gain = { raw: [1, 2] };
    },
    (c: CheckRecord) => {
      c.attempts[1]!.component_metadata.hidden = "private";
    },
    (c: CheckRecord) => {
      (
        c.attempts[1]!.component_metadata.projection as JsonObject
      ).heart_rate_bpm = -1;
    },
    (c: CheckRecord) => {
      c.attempts[1]!.session_id = randomUUID();
    },
  ]) {
    const changed = clone(check);
    alter(changed);
    rehash(changed);
    assert.throws(() => verifyExportEvidence(changed));
  }
});

test("a rehashed null selection, invented BMI, contradictory use history and retry cycle are rejected", () => {
  const check = freezeCheck(
    simulatedCapture(draft(), "eyes", at, randomUUID),
    later,
    randomUUID,
  );
  const unbound = clone(check);
  unbound.manifest!.selected.eyes = null;
  assert.throws(() => verifyExportEvidence(rehash(unbound)));
  const badBmi = clone(check);
  badBmi.snapshot.profile.bmi = 27;
  assert.throws(() => verifyExportEvidence(rehash(badBmi)));
  const history = clone(check);
  history.context.self_report_context = {
    last_use_status: "known",
    last_use_at: "2026-10-10T23:00:00.000Z",
    confirmed_at: at,
  };
  history.snapshot.history.time_since_use_min = 0;
  assert.throws(() => verifyExportEvidence(rehash(history)));
  const unknown = clone(check);
  (unknown as unknown as Record<string, unknown>).foreignOwner = owner;
  assert.throws(() => verifyExportEvidence(unknown));
  const first = startAttempt(
    draft(),
    "task",
    at,
    randomUUID,
    "prototype_sensor",
  );
  const second = startAttempt(
    interruptStartedAttempts(first.check, at),
    "task",
    at,
    randomUUID,
    "prototype_sensor",
  );
  const interrupted = freezeCheck(
    interruptStartedAttempts(second.check, at),
    later,
    randomUUID,
  );
  assert.doesNotThrow(
    () => verifyExportEvidence(interrupted),
    "unmounted canceled arms legitimately have no native payload",
  );
  interrupted.attempts[0]!.supersedes_attempt_id =
    interrupted.attempts[1]!.attempt_id;
  assert.throws(() => verifyExportEvidence(rehash(interrupted)));
});

test("host-generated native golden is fully checked without claiming a physical acquisition", () => {
  const check = nativeCheck(),
    original = digest(check);
  assert.doesNotThrow(() => verifyExportEvidence(check));
  assert.equal(digest(check), original);
  for (const mutate of [
    (n: NativeTaskResult) => {
      n.seed++;
    },
    (n: NativeTaskResult) => {
      n.trialEvents[0]!.correctGoRtMs = 301;
    },
    (n: NativeTaskResult) => {
      n.inputEvents[0]!.disposition = "additional_response";
    },
    (n: NativeTaskResult) => {
      n.inputEvents[0]!.trialIndex = 2;
    },
    (n: NativeTaskResult) => {
      n.inputEvents[0]!.dispatchTimestampMs++;
    },
    (n: NativeTaskResult) => {
      n.timing.clockDomain = "ios_uptime";
    },
    (n: NativeTaskResult) => {
      n.timing.viewWidthPoints = 200;
    },
    (n: NativeTaskResult) => {
      (n.timing as unknown as JsonObject).hidden_stream = [1, 2, 3];
    },
    (n: NativeTaskResult) => {
      n.counts.completedScored = 59;
    },
    (n: NativeTaskResult) => {
      n.timing.terminalCutoffMs = n.durationMs + 1;
    },
  ]) {
    const changed = clone(check),
      native = changed.attempts[0]!.component_metadata
        .native_result as unknown as NativeTaskResult;
    mutate(native);
    rehash(changed);
    assert.throws(() => verifyExportEvidence(changed));
  }
});

test("canceling after a correct native tap counts only fully elapsed scored response windows", () => {
  for (const elapsed of [999, 1000]) {
    const native = nativeFixture(),
      last = native.trialEvents.find(
        (t) => t.phase === "scored" && t.stimulus !== "no_go",
      )!;
    const duration = last.onsetMs! + elapsed;
    native.status = "invalid";
    native.features = null;
    native.qualityFlags.push("USER_CANCELED");
    native.durationMs = duration;
    native.nativeEndMs = native.nativeStartMs + duration;
    native.endedAt = new Date(
      Date.parse(native.startedAt) + duration,
    ).toISOString();
    native.timing.observedEndedAt = native.endedAt;
    native.timing.terminalCutoffMs = null;
    native.inputEvents = native.inputEvents.filter(
      (input) => input.nativeTimestampMs <= duration,
    );
    for (const trial of native.trialEvents.filter(
      (t) => t.index > last.index,
    )) {
      trial.presented = false;
      trial.outcome = "unresolved";
      trial.frameTimestampMs =
        trial.callbackTimestampMs =
        trial.onsetMs =
        trial.onsetLatenessMs =
        trial.selectedInputSequence =
        trial.responseTimeMs =
        trial.correctGoRtMs =
          null;
    }
    const scored = native.trialEvents.filter(
      (t) => t.phase === "scored" && t.presented,
    );
    native.counts = {
      presentedPractice: 6,
      presentedScored: scored.length,
      presentedGo: scored.filter((t) => t.stimulus !== "no_go").length,
      presentedNoGo: scored.filter((t) => t.stimulus === "no_go").length,
      completedScored: scored.filter((t) => duration >= t.onsetMs! + 1000)
        .length,
      correctGo: scored.filter((t) => t.outcome === "correct").length,
      omissions: 0,
      wrongGo: 0,
      noGoErrors: 0,
      correctWithholds: scored.filter((t) => t.outcome === "correct_withhold")
        .length,
    };
    assert.equal(last.outcome, "correct");
    assert.equal(
      native.counts.completedScored,
      scored.length - (elapsed < 1000 ? 1 : 0),
    );
    const check = nativeCheck(native);
    assert.doesNotThrow(() => verifyExportEvidence(check));
    const changed = clone(check);
    (
      changed.attempts[0]!.component_metadata
        .native_result as unknown as NativeTaskResult
    ).counts.completedScored++;
    assert.throws(() => verifyExportEvidence(rehash(changed)));
  }
});

test("an intact native task with no correct responses keeps null RT quantiles and its explicit quality flag", () => {
  const native = nativeFixture();
  native.inputEvents = [];
  native.qualityFlags.push("NO_CORRECT_GO_RESPONSES");
  for (const trial of native.trialEvents) {
    trial.outcome =
      trial.stimulus === "no_go" ? "correct_withhold" : "omission";
    trial.selectedInputSequence =
      trial.responseTimeMs =
      trial.correctGoRtMs =
        null;
  }
  native.counts.correctGo = 0;
  native.counts.omissions = 48;
  native.features = {
    medianRtMs: null,
    iqrRtMs: null,
    p90RtMs: null,
    omissionRate: 1,
    wrongGoRate: 0,
    noGoErrorRate: 0,
  };
  const check = nativeCheck(native);
  assert.doesNotThrow(() => verifyExportEvidence(check));
  assert.equal((check.snapshot.task.features as JsonObject).median_rt_ms, null);
  assert.equal((check.snapshot.task.features as JsonObject).omission_rate, 1);
  const changed = clone(check);
  (
    changed.attempts[0]!.component_metadata
      .native_result as unknown as NativeTaskResult
  ).features!.medianRtMs = 0;
  assert.throws(() => verifyExportEvidence(rehash(changed)));
});

test("executed software-only saliva, PPG and ECG transcript exports reject rehashed clock/replay/identity tampering", async () => {
  const checks = await Promise.all(
    (["ppg", "ecg", "saliva"] as const).map(async (channel) => {
      const controller = new DeviceControllerImpl(
        { idFactory: randomUUID },
        () => new LocalSimulatorTransport(randomUUID),
      );
      const now = new Date().toISOString();
      const started = startAttempt(
        draft("guest_demo", now),
        channel === "saliva" ? "saliva" : "cardiac",
        now,
        randomUUID,
        "simulated",
        "synthetic_bench_v1",
        syntheticConfigurationDigest(channel),
        channel === "saliva" ? undefined : channel,
      );
      try {
        await controller.useLocalSimulator();
        const capture = await controller.captureSynthetic(channel, {
          sessionId: started.check.id,
          attemptId: started.attempt.attempt_id,
          captureId: started.attempt.record_id,
          workspaceEpoch: "export-test:fictional",
        });
        assert.equal(capture.messages.length, 10);
        const projection = projectSyntheticDevice(
          capture,
          started.attempt,
          randomUUID,
        );
        const settled = settleAttempt(
          started.check,
          started.attempt.attempt_id,
          projection,
          "valid",
          capture.endedAt,
          capture.qualityFlags,
          {
            fixture_id: capture.fixtureId,
            transport_evidence: capture as unknown as JsonObject,
          },
        );
        return freezeCheck(settled, new Date().toISOString(), randomUUID);
      } finally {
        await controller.dispose();
      }
    }),
  );
  for (const check of checks) {
    const before = digest(check);
    assert.doesNotThrow(() => verifyExportEvidence(check));
    assert.equal(digest(check), before);
    for (const change of [
      (v: SyntheticDeviceCapture) => {
        v.context.sessionId = randomUUID();
      },
      (v: SyntheticDeviceCapture) => {
        v.clockEvidence.offset_ms += 1;
      },
      (v: SyntheticDeviceCapture) => {
        v.clockEvidence.exchanges[0]!.offset_upper_ms += 1;
      },
      (v: SyntheticDeviceCapture) => {
        v.association.verifiedBindingId = randomUUID() as never;
      },
      (v: SyntheticDeviceCapture) => {
        v.messages[1]!.message_id = v.messages[0]!.message_id;
      },
      (v: SyntheticDeviceCapture) => {
        v.messages[2]!.sequence = v.messages[1]!.sequence;
      },
      (v: SyntheticDeviceCapture) => {
        v.messages[0]!.payload.extra = "unexpected";
      },
      (v: SyntheticDeviceCapture) => {
        v.messages.pop();
      },
      (v: SyntheticDeviceCapture) => {
        (v.values as unknown as JsonObject).invented_value = 99;
      },
    ]) {
      const changed = clone(check),
        transport = changed.attempts[0]!.component_metadata
          .transport_evidence as unknown as SyntheticDeviceCapture;
      change(transport);
      const { evidenceSha256: ignored, ...payload } = transport;
      void ignored;
      transport.evidenceSha256 = digest(payload);
      assert.throws(() => verifyExportEvidence(rehash(changed)));
    }
  }
});

test("bounded synthetic lead-off failure keeps null values without inventing a successful transport proof", () => {
  const started = startAttempt(
    draft(),
    "cardiac",
    at,
    randomUUID,
    "simulated",
    "synthetic_bench_v1",
    syntheticConfigurationDigest("ecg"),
    "ecg",
  );
  const identity = {
    deviceId: "SIM-LOCAL-01",
    bootId: randomUUID(),
    context: {
      sessionId: started.check.id,
      attemptId: started.attempt.attempt_id,
      captureId: started.attempt.record_id,
      workspaceEpoch: "export-test:fictional",
    },
    channel: "ecg" as const,
    scenario: "lead_off" as const,
  };
  const failure = getSyntheticSignalFailure(
    new SyntheticSignalError("SYNTHETIC_LEAD_OFF", identity, "absent", 0),
    started.attempt,
    later,
  )!;
  assert.ok(failure);
  const settled = settleAttempt(
    started.check,
    started.attempt.attempt_id,
    failure.projection,
    "invalid",
    later,
    failure.qualityFlags,
    failure.metadata,
  );
  const check = freezeCheck(settled, later, randomUUID);
  assert.doesNotThrow(() => verifyExportEvidence(check));
  assert.equal(check.snapshot.cardiac.heart_rate_bpm, null);
  assert.equal(
    check.attempts[0]!.component_metadata.transport_evidence,
    undefined,
  );
});
