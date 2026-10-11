import type {
  NativeInputEvent,
  NativeTaskResult,
  TaskOutcome,
} from "../../modules/reaction-task/types";
import {
  capabilities,
  clockExchange,
  envelope,
  selectClock,
  uuid,
} from "../device/protocol";
import { syntheticValues } from "../device/synthetic-values";
import type { SyntheticDeviceCapture } from "../device/types";
import {
  CHANNELS,
  TASK_CONFIGURATION_ID,
  TASK_CONFIGURATION_SHA256,
  verifyCheck,
} from "./domain";
import { verifyAttemptProjection } from "./exportProjection";
import { verifyRetainedNativeEye } from "./eyeProjection";
import {
  assertBytes,
  assertPlainJson,
  canonicalJson,
  digest,
  IntegrityError,
  requireObject,
  requiredString,
  safeInteger,
  utf8,
} from "./integrity";
import type { CaptureAttempt, CheckRecord, JsonObject } from "./types";

// Offline contract/integrity verification, not an acquisition path. Recomputed
// software schedules, hashes and fictional packets do not authenticate a person,
// qualify a sensor, prove photon onset, or permit impairment inference.
function demand(value: unknown): asserts value {
  if (!value)
    throw new IntegrityError(
      "EXPORT_EVIDENCE_INVALID",
      "The retained evidence is inconsistent or uses an unsupported field. Nothing was shared.",
    );
}
function exact(value: unknown, names: string): Record<string, unknown> {
  const object = requireObject(value),
    keys = names.split(" ");
  demand(
    Object.keys(object).length === keys.length &&
      keys.every((key) => Object.hasOwn(object, key)),
  );
  return object;
}
function number(
  value: unknown,
  min = -Number.MAX_SAFE_INTEGER,
  max = Number.MAX_SAFE_INTEGER,
): number {
  demand(
    typeof value === "number" &&
      Number.isFinite(value) &&
      value >= min &&
      value <= max,
  );
  return value;
}
function integer(
  value: unknown,
  min = 0,
  max = Number.MAX_SAFE_INTEGER,
): number {
  const result = safeInteger(value, min);
  demand(result <= max);
  return result;
}
function utc(value: unknown): number {
  const text = requiredString(value, 64);
  demand(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(text));
  const time = Date.parse(text);
  demand(
    Number.isFinite(time) &&
      new Date(time).toISOString().slice(0, 19) === text.slice(0, 19),
  );
  return time;
}
function array(value: unknown, min: number, max: number): unknown[] {
  demand(Array.isArray(value) && value.length >= min && value.length <= max);
  return value;
}
function oneOf(value: unknown, values: readonly unknown[]): void {
  demand(values.includes(value));
}
function close(
  actual: unknown,
  expected: number | null,
  tolerance = 1e-6,
): void {
  if (expected === null) {
    demand(actual === null);
    return;
  }
  demand(Math.abs(number(actual) - expected) <= tolerance);
}
function nullableNumber(value: unknown): void {
  if (value !== null) number(value);
}
function same(a: unknown, b: unknown): void {
  demand(digest(a) === digest(b));
}

/** Validate every retained original record, including unselected attempts.
 * Replacement/report caches are separate mutable companions: export.ts validates
 * and exports their bounded records independently, never inside this base chain.
 */
export function verifyExportEvidence(check: CheckRecord): void {
  const raw = requireObject(check);
  const required =
    "id generation workspace kind stage frozen snapshot context attempts manifest snapshot_sha256 evidence_sha256 result alcohol delivery error remote_revision remote_etag updated_at".split(
      " ",
    );
  const allowed = [
    ...required,
    "selected_cardiac_attempt_id",
    "replacement_links",
    "report_revision_cache",
    "acquisition",
    "attestations",
  ];
  demand(
    required.every((key) => Object.hasOwn(raw, key)) &&
      Object.keys(raw).every((key) => allowed.includes(key)),
  );
  const original = Object.fromEntries(
    Object.entries(raw).filter(
      ([key]) =>
        ![
          "replacement_links",
          "report_revision_cache",
          "acquisition",
          "attestations",
        ].includes(key),
    ),
  );
  assertPlainJson(original);
  demand(
    check.frozen === true &&
      check.delivery !== "quarantined" &&
      check.delivery !== "local_draft",
  );
  uuid(check.id);
  integer(check.generation, 1);
  requiredString(check.workspace, 256);
  integer(check.remote_revision);
  requiredString(check.remote_etag, 256);
  utc(check.updated_at);
  demand(
    check.error === null ||
      (typeof check.error === "string" && check.error.length <= 4096),
  );
  oneOf(check.kind, ["guest_demo", "engineering_fixture", "measurement"]);
  oneOf(check.stage, [
    "profile",
    "device",
    "saliva",
    "eyes",
    "cardiac",
    "ecg",
    "task",
    "review",
  ]);
  oneOf(check.delivery, [
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
  ]);
  array(check.attempts, 0, 128);
  for (const record of [
    check.snapshot,
    check.context,
    check.manifest,
    ...check.attempts,
    ...(check.alcohol ? [check.alcohol] : []),
    ...(check.result ? [check.result] : []),
  ])
    assertBytes(record, 524_288);
  demand(
    check.result === null ||
      (typeof check.result === "object" && !Array.isArray(check.result)),
  );
  demand(
    check.alcohol === null ||
      (typeof check.alcohol === "object" && !Array.isArray(check.alcohol)),
  );
  verifyCheck(check);
  demand(
    check.kind === "measurement"
      ? ["analytical", "controlled_research"].includes(check.snapshot.mode)
      : check.snapshot.mode === "synthetic",
  );
  if (check.kind === "guest_demo")
    demand(check.snapshot.subject_ref === "local-guest");
  demand(check.snapshot.supersedes_session_id !== check.id);
  const target = utc(check.snapshot.target_at);
  utc(check.context.context_confirmed_at);
  utc(check.snapshot.capture_completed_at);
  utc(check.snapshot.profile.recorded_at);
  const profile = check.snapshot.profile;
  const bmi =
    profile.height_cm && profile.weight_kg
      ? profile.weight_kg / (profile.height_cm / 100) ** 2
      : null;
  close(profile.bmi, bmi, 0.01);
  // Older supported server records explicitly use null here. Absence of context
  // is preserved, never replaced with a guessed last-use time.
  const report = check.context.self_report_context;
  if (report != null) {
    utc(report.confirmed_at);
    demand(
      (report.last_use_status === "known") === (report.last_use_at !== null),
    );
    if (report.last_use_status === "known") {
      const elapsed = (target - utc(report.last_use_at)) / 60_000;
      demand(elapsed >= 0);
      close(check.snapshot.history.time_since_use_min, elapsed, 1 / 60);
    } else demand(check.snapshot.history.time_since_use_min === null);
  }
  for (const list of [
    check.context.baseline_refs,
    check.context.configuration_refs.map(
      (ref) => `${ref.id}:${ref.version}:${ref.scope}`,
    ),
    check.context.device_associations.map(
      (ref) => `${ref.device_id}:${ref.boot_id}`,
    ),
  ])
    demand(new Set(list).size === list.length);
  const byId = new Map(
    check.attempts.map((attempt) => [attempt.attempt_id, attempt]),
  );
  const validComponents = new Set<string>();
  for (const attempt of check.attempts) {
    const projection = verifyAttemptProjection(attempt, check.snapshot);
    for (const refs of [attempt.artifact_refs, attempt.attestation_refs])
      demand(new Set(refs).size === refs.length);
    if (attempt.started_at !== null) utc(attempt.started_at);
    if (attempt.ended_at !== null) utc(attempt.ended_at);
    const visited = new Set([attempt.attempt_id]);
    let previous = attempt.supersedes_attempt_id;
    while (previous !== null) {
      demand(!visited.has(previous));
      visited.add(previous);
      const predecessor = byId.get(previous);
      demand(predecessor);
      previous = predecessor.supersedes_attempt_id;
    }
    if (attempt.status === "valid") {
      const key =
        attempt.component === "cardiac"
          ? `cardiac:${projection.modality}`
          : attempt.component;
      demand(!validComponents.has(key));
      validComponents.add(key);
    }
    if (
      attempt.component_metadata.native_result != null &&
      attempt.component === "eyes"
    )
      verifyRetainedNativeEye(
        attempt.component_metadata.native_result,
        projection,
        attempt,
      );
    else if (attempt.component_metadata.native_result != null)
      verifyNative(
        attempt.component_metadata.native_result,
        projection,
        attempt,
      );
    if (attempt.component_metadata.transport_evidence != null)
      verifySynthetic(
        attempt.component_metadata.transport_evidence,
        projection,
        attempt,
      );
  }
  for (const channel of CHANNELS) {
    if (check.manifest!.selected[channel] !== null) continue;
    if (channel === "saliva")
      demand(
        check.snapshot.sample.status === "not_collected" &&
          check.snapshot.saliva.length === 0,
      );
    else if (channel === "alcohol") demand(check.alcohol === null);
    else demand(check.snapshot[channel].status === "not_collected");
  }
}

function expectedSchedule(seed: number) {
  let state = seed;
  const next = () => (state = (Math.imul(1664525, state) + 1013904223) >>> 0);
  const shuffled = (left: number, right: number, noGo: number) => {
    const list = [
      ...Array<string>(left).fill("left"),
      ...Array<string>(right).fill("right"),
      ...Array<string>(noGo).fill("no_go"),
    ];
    for (let i = list.length - 1; i > 0; i--) {
      const j = next() % (i + 1);
      [list[i], list[j]] = [list[j]!, list[i]!];
    }
    return list;
  };
  const stimuli = [...shuffled(2, 2, 2), ...shuffled(24, 24, 12)];
  let onset = 2000;
  const trials = stimuli.map((stimulus, index) => {
    const interval = 1500 + (next() % 401);
    const trial = {
      index,
      phase: index < 6 ? "practice" : "scored",
      stimulus,
      planned_onset_ms: onset,
      onset_interval_ms: interval,
    };
    onset += interval;
    return trial;
  });
  return {
    schema_version: "1.0.0",
    configuration_sha256: TASK_CONFIGURATION_SHA256,
    seed,
    trials,
  };
}

function verifyNative(
  raw: unknown,
  projection: JsonObject,
  attempt: CaptureAttempt,
): void {
  exact(
    raw,
    "schemaVersion taskVersion implementationVersion extractorVersion status source platform runId workspaceEpoch seed configurationId configurationSha256 scheduleSha256 startedAt endedAt nativeStartMs nativeEndMs durationMs trialEvents inputEvents counts features qualityFlags timing",
  );
  const value = raw as NativeTaskResult;
  same(
    [
      value.schemaVersion,
      value.taskVersion,
      value.implementationVersion,
      value.extractorVersion,
      value.source,
    ],
    [
      "1.0.0",
      "choice_inhibit_v0",
      "1.0.0",
      "choice_inhibit_features_1",
      "native_task",
    ],
  );
  oneOf(value.status, ["valid", "invalid"]);
  oneOf(value.platform, ["android", "ios"]);
  requiredString(value.runId, 128);
  requiredString(value.workspaceEpoch, 128);
  integer(value.seed, 0, 0xffffffff);
  demand(
    attempt.component === "task" &&
      attempt.source === "prototype_sensor" &&
      attempt.configuration_id === TASK_CONFIGURATION_ID &&
      attempt.configuration_hash === TASK_CONFIGURATION_SHA256,
  );
  demand(
    value.configurationId === TASK_CONFIGURATION_ID &&
      value.configurationSha256 === TASK_CONFIGURATION_SHA256 &&
      projection.config_sha256 === TASK_CONFIGURATION_SHA256,
  );
  same(
    [value.status, value.runId, value.startedAt, value.endedAt],
    [
      projection.status,
      projection.task_id,
      projection.started_at,
      projection.ended_at,
    ],
  );
  demand(
    projection.source === "prototype_sensor" &&
      value.runId === attempt.record_id,
  );
  number(value.nativeStartMs, 0);
  number(value.nativeEndMs, 0);
  number(value.durationMs, 0);
  close(value.nativeEndMs - value.nativeStartMs, value.durationMs, 0.01);
  close(utc(value.endedAt) - utc(value.startedAt), value.durationMs, 2);
  array(value.qualityFlags, 1, 64).forEach((flag) => requiredString(flag, 128));
  const schedule = expectedSchedule(value.seed);
  demand(value.scheduleSha256 === digest(schedule));
  array(value.trialEvents, 66, 66);
  array(value.inputEvents, 0, 1024);
  const timing = exact(
    value.timing,
    "clockDomain inputTimestampMethod inputTimestampResolutionMs presentationEvidenceMethod calibrationStatus physicalOnsetVerified modelEligible simulator deviceModel osVersion nativeBuild viewWidthPoints viewHeightPoints viewWidthPixels viewHeightPixels pixelDensity orientation fontFamily textScale nominalRefreshHz maxObservedFrameGapMs maxObservedFrameDispatchMs maxObservedInputDispatchMs terminalCutoffMs finalDrainMs overflowTriggerCount utcAnchorMethod observedEndedAt observedWallClockDeltaMs physicalLuminance",
  );
  same(
    [
      timing.calibrationStatus,
      timing.modelEligible,
      timing.physicalOnsetVerified,
      timing.physicalLuminance,
      timing.finalDrainMs,
    ],
    ["uncalibrated", false, false, "unmeasured", 100],
  );
  for (const key of ["deviceModel", "osVersion", "nativeBuild", "fontFamily"])
    requiredString(timing[key], 256);
  utc(timing.observedEndedAt);
  demand(
    typeof timing.simulator === "boolean" &&
      timing.orientation === "portrait" &&
      timing.textScale === 1 &&
      timing.utcAnchorMethod === "start_utc_plus_monotonic_elapsed",
  );
  demand(
    timing.clockDomain ===
      (value.platform === "android" ? "android_uptime" : "ios_uptime"),
  );
  demand(
    timing.presentationEvidenceMethod ===
      (value.platform === "android"
        ? "choreographer_frame_time_nanos"
        : "cadisplaylink_target_timestamp"),
  );
  oneOf(
    timing.inputTimestampMethod,
    value.platform === "android"
      ? ["motion_event_uptime_ms", "motion_event_uptime_nanos"]
      : ["uitouch_timestamp"],
  );
  if (timing.inputTimestampResolutionMs !== null)
    demand(number(timing.inputTimestampResolutionMs) > 0);
  nullableNumber(timing.terminalCutoffMs);
  for (const key of [
    "viewWidthPoints",
    "viewHeightPoints",
    "viewWidthPixels",
    "viewHeightPixels",
    "pixelDensity",
    "nominalRefreshHz",
  ])
    number(timing[key], 0);
  for (const key of [
    "maxObservedFrameGapMs",
    "maxObservedFrameDispatchMs",
    "maxObservedInputDispatchMs",
    "observedWallClockDeltaMs",
  ])
    number(timing[key]);
  integer(timing.overflowTriggerCount);
  if (attempt.component_metadata.contract_fixture !== undefined)
    demand(
      attempt.component_metadata.contract_fixture === true &&
        timing.simulator === true,
    );
  for (const [index, trial] of value.trialEvents.entries()) {
    exact(
      trial,
      "index phase stimulus plannedOnsetMs onsetIntervalMs presented frameTimestampMs callbackTimestampMs onsetMs onsetLatenessMs outcome selectedInputSequence responseTimeMs correctGoRtMs",
    );
    const expected = schedule.trials[index]!;
    same(
      [
        trial.index,
        trial.phase,
        trial.stimulus,
        trial.plannedOnsetMs,
        trial.onsetIntervalMs,
      ],
      [
        expected.index,
        expected.phase,
        expected.stimulus,
        expected.planned_onset_ms,
        expected.onset_interval_ms,
      ],
    );
    demand(
      typeof trial.presented === "boolean" &&
        trial.presented === (trial.onsetMs !== null),
    );
    oneOf(trial.outcome, [
      "correct",
      "wrong_choice",
      "omission",
      "commission",
      "correct_withhold",
      "unresolved",
    ]);
    if (trial.selectedInputSequence !== null)
      integer(trial.selectedInputSequence);
    for (const key of [
      "frameTimestampMs",
      "callbackTimestampMs",
      "onsetMs",
      "onsetLatenessMs",
      "responseTimeMs",
      "correctGoRtMs",
    ] as const)
      nullableNumber(trial[key]);
    if (trial.presented) {
      number(trial.frameTimestampMs);
      number(trial.callbackTimestampMs);
      close(trial.onsetLatenessMs, trial.onsetMs! - trial.plannedOnsetMs);
    } else
      demand(
        trial.frameTimestampMs === null &&
          trial.callbackTimestampMs === null &&
          trial.onsetLatenessMs === null,
      );
  }
  const sequenceIds = new Set<number>();
  for (const input of value.inputEvents) {
    exact(
      input,
      "nativeTimestampMs dispatchTimestampMs dispatchDelayMs target pointerId nativeSequence inputKind disposition trialIndex anticipatoryForTrialIndex",
    );
    number(input.nativeTimestampMs);
    number(input.dispatchTimestampMs);
    number(input.dispatchDelayMs);
    close(
      input.dispatchDelayMs,
      input.dispatchTimestampMs - input.nativeTimestampMs,
    );
    integer(input.nativeSequence);
    integer(input.pointerId);
    demand(!sequenceIds.has(input.nativeSequence));
    sequenceIds.add(input.nativeSequence);
    oneOf(input.target, ["left", "right", "outside"]);
    oneOf(input.inputKind, ["direct_touch", "unsupported"]);
    oneOf(input.disposition, [
      "selected",
      "additional_response",
      "outside",
      "anticipatory",
      "late",
      "unsupported",
      "timing_fault",
    ]);
    for (const key of ["trialIndex", "anticipatoryForTrialIndex"] as const)
      if (input[key] !== null) integer(input[key], 0, 65);
  }
  const ranked = ["left", "right", "outside"];
  const inputs = [...value.inputEvents].sort(
    (a, b) =>
      a.nativeTimestampMs - b.nativeTimestampMs ||
      ranked.indexOf(a.target) - ranked.indexOf(b.target) ||
      a.pointerId - b.pointerId ||
      a.nativeSequence - b.nativeSequence,
  );
  const presented = value.trialEvents.filter((trial) => trial.presented);
  const selected = new Map<number, NativeInputEvent>();
  // The same documented classification rules are checked independently of the
  // supplied outcomes. Invalid runs keep their partial ledger and null features.
  for (const input of inputs) {
    const trial = presented.find(
      (t) =>
        input.nativeTimestampMs >= t.onsetMs! &&
        input.nativeTimestampMs < t.onsetMs! + 1000,
    );
    let trialIndex = trial?.index ?? null,
      anticipatory: number | null = null,
      disposition: NativeInputEvent["disposition"];
    if (
      input.inputKind !== "direct_touch" ||
      input.dispatchDelayMs < 0 ||
      input.dispatchDelayMs > 100
    )
      disposition =
        input.inputKind !== "direct_touch" ? "unsupported" : "timing_fault";
    else if (input.target === "outside") disposition = "outside";
    else if (!trial) {
      const previous = presented
        .filter((t) => input.nativeTimestampMs >= t.onsetMs! + 1000)
        .at(-1);
      trialIndex = previous?.index ?? null;
      anticipatory =
        presented.find((t) => input.nativeTimestampMs < t.onsetMs!)?.index ??
        null;
      disposition = previous ? "late" : "anticipatory";
    } else if (selected.has(trial.index)) disposition = "additional_response";
    else {
      selected.set(trial.index, input);
      disposition = "selected";
    }
    same(
      [input.disposition, input.trialIndex, input.anticipatoryForTrialIndex],
      [disposition, trialIndex, anticipatory],
    );
  }
  for (const trial of value.trialEvents) {
    const first = selected.get(trial.index);
    let outcome: TaskOutcome = "unresolved";
    if (trial.presented && first)
      outcome =
        trial.stimulus === "no_go"
          ? "commission"
          : first.target === trial.stimulus
            ? "correct"
            : "wrong_choice";
    else if (trial.presented && value.durationMs >= trial.onsetMs! + 1000)
      outcome = trial.stimulus === "no_go" ? "correct_withhold" : "omission";
    const response = first ? first.nativeTimestampMs - trial.onsetMs! : null;
    demand(
      trial.outcome === outcome &&
        trial.selectedInputSequence === (first?.nativeSequence ?? null),
    );
    close(trial.responseTimeMs, response);
    close(trial.correctGoRtMs, outcome === "correct" ? response : null);
  }
  const scored = presented.filter((t) => t.phase === "scored");
  const expectedCounts = {
    presentedPractice: presented.filter((t) => t.phase === "practice").length,
    presentedScored: scored.length,
    presentedGo: scored.filter((t) => t.stimulus !== "no_go").length,
    presentedNoGo: scored.filter((t) => t.stimulus === "no_go").length,
    completedScored: scored.filter((t) => value.durationMs >= t.onsetMs! + 1000)
      .length,
    correctGo: scored.filter((t) => t.outcome === "correct").length,
    omissions: scored.filter((t) => t.outcome === "omission").length,
    wrongGo: scored.filter((t) => t.outcome === "wrong_choice").length,
    noGoErrors: scored.filter((t) => t.outcome === "commission").length,
    correctWithholds: scored.filter((t) => t.outcome === "correct_withhold")
      .length,
  };
  exact(value.counts, Object.keys(expectedCounts).join(" "));
  Object.values(value.counts).forEach((count) => integer(count, 0, 66));
  same(value.counts, expectedCounts);
  for (const [field, key] of Object.entries({
    practice_trials: "presentedPractice",
    scored_trials: "presentedScored",
    go_trials: "presentedGo",
    no_go_trials: "presentedNoGo",
    valid_correct_go_trials: "correctGo",
  }))
    demand(
      projection[field] === value.counts[key as keyof typeof value.counts],
    );
  const projectedFeatures = requireObject(projection.features);
  if (value.status === "invalid") {
    demand(
      value.features === null &&
        Object.values(projectedFeatures).every((v) => v === null),
    );
    return;
  }
  demand(
    value.timing.viewWidthPoints >= 240 &&
      value.timing.viewHeightPoints >= 400 &&
      value.timing.pixelDensity > 0 &&
      value.timing.overflowTriggerCount === 0,
  );
  for (const key of [
    "maxObservedFrameGapMs",
    "maxObservedFrameDispatchMs",
    "maxObservedInputDispatchMs",
  ] as const)
    number(value.timing[key], 0, 100);
  demand(
    value.qualityFlags.includes("UNCALIBRATED_TIMING") &&
      value.qualityFlags.every((flag) =>
        ["UNCALIBRATED_TIMING", "NO_CORRECT_GO_RESPONSES"].includes(flag),
      ) &&
      value.qualityFlags.includes("NO_CORRECT_GO_RESPONSES") ===
        (expectedCounts.correctGo === 0),
  );
  demand(
    value.trialEvents.every(
      (t) =>
        t.presented &&
        t.onsetLatenessMs !== null &&
        t.onsetLatenessMs >= 0 &&
        t.onsetLatenessMs <= 100,
    ),
  );
  demand(
    inputs.every(
      (input) =>
        input.inputKind === "direct_touch" &&
        input.dispatchDelayMs >= 0 &&
        input.dispatchDelayMs <= 100,
    ),
  );
  close(value.timing.terminalCutoffMs, value.trialEvents[65]!.onsetMs! + 1100);
  close(value.durationMs, value.timing.terminalCutoffMs!);
  const rts = scored
    .filter((t) => t.outcome === "correct")
    .map((t) => t.correctGoRtMs!)
    .sort((a, b) => a - b);
  const q = (p: number): number | null => {
    if (!rts.length) return null;
    const index = (rts.length - 1) * p,
      lo = Math.floor(index);
    return (
      rts[lo]! +
      (rts[Math.min(lo + 1, rts.length - 1)]! - rts[lo]!) * (index - lo)
    );
  };
  const firstQ = q(0.25),
    thirdQ = q(0.75);
  const expectedFeatures = {
    medianRtMs: q(0.5),
    iqrRtMs: firstQ === null || thirdQ === null ? null : thirdQ - firstQ,
    p90RtMs: q(0.9),
    omissionRate: expectedCounts.omissions / 48,
    wrongGoRate: expectedCounts.wrongGo / 48,
    noGoErrorRate: expectedCounts.noGoErrors / 12,
  };
  const features = exact(
    value.features,
    Object.keys(expectedFeatures).join(" "),
  );
  for (const [key, expected] of Object.entries(expectedFeatures))
    close(features[key], expected);
  for (const [field, key] of Object.entries({
    median_rt_ms: "medianRtMs",
    iqr_rt_ms: "iqrRtMs",
    p90_rt_ms: "p90RtMs",
    omission_rate: "omissionRate",
    wrong_go_rate: "wrongGoRate",
    no_go_error_rate: "noGoErrorRate",
  }))
    close(
      projectedFeatures[field],
      expectedFeatures[key as keyof typeof expectedFeatures],
    );
}

function verifySynthetic(
  raw: unknown,
  projection: JsonObject,
  attempt: CaptureAttempt,
): void {
  const object = exact(
    raw,
    "source channel context association clockEvidence startedAt endedAt deviceStartedMonotonicMs deviceEndedMonotonicMs values fixtureId messages evidenceSha256 qualityFlags modelEligible",
  );
  const value = raw as SyntheticDeviceCapture;
  demand(
    value.source === "simulated" &&
      attempt.source === "simulated" &&
      attempt.status === "valid" &&
      value.modelEligible === false &&
      value.fixtureId === "synthetic_bench_v1",
  );
  oneOf(value.channel, ["ppg", "ecg", "saliva"]);
  same(value.qualityFlags, ["SIMULATED", "UNVERIFIED_DEVICE"]);
  demand(
    value.evidenceSha256 ===
      digest(
        Object.fromEntries(
          Object.entries(object).filter(([key]) => key !== "evidenceSha256"),
        ),
      ),
  );
  exact(value.context, "sessionId attemptId captureId workspaceEpoch");
  const context = value.context;
  uuid(context.sessionId);
  uuid(context.attemptId);
  uuid(context.captureId);
  requiredString(context.workspaceEpoch, 128);
  same(
    [
      context.sessionId,
      context.attemptId,
      context.captureId,
      value.channel === "saliva" ? "saliva" : "cardiac",
    ],
    [
      attempt.session_id,
      attempt.attempt_id,
      attempt.record_id,
      attempt.component,
    ],
  );
  demand(
    attempt.configuration_id === value.fixtureId &&
      attempt.configuration_hash ===
        digest({ fixture: value.fixtureId, channel: value.channel }),
  );
  const association = exact(
    value.association,
    "peripheralId deviceId bootId hardwareRevision firmwareVersion protocolVersion source verifiedBindingId transport capabilities",
  );
  for (const key of [
    "peripheralId",
    "deviceId",
    "hardwareRevision",
    "firmwareVersion",
  ])
    requiredString(association[key], 256);
  uuid(association.bootId);
  oneOf(association.transport, ["ble_unprovisioned", "local_simulator"]);
  demand(
    association.protocolVersion === 1 &&
      association.source === "simulated" &&
      association.verifiedBindingId === null,
  );
  exact(
    association.capabilities,
    "protocol_version encodings max_logical_bytes max_att_bytes source device_id boot_id hardware_revision firmware_version channels configuration_id calibration_status timestamp_resolution_ms",
  );
  const caps = capabilities(canonicalJson(association.capabilities));
  same(
    [
      association.deviceId,
      association.bootId,
      association.hardwareRevision,
      association.firmwareVersion,
    ],
    [
      caps.device_id,
      caps.boot_id,
      caps.hardware_revision,
      caps.firmware_version,
    ],
  );
  demand(caps.channels.includes(value.channel));
  same(value.values, syntheticValues(value.channel));
  const duration = utc(value.endedAt) - utc(value.startedAt);
  demand(
    duration >= 0 && duration <= 120_000 && value.endedAt === attempt.ended_at,
  );
  number(value.deviceStartedMonotonicMs, 0);
  number(value.deviceEndedMonotonicMs, 0);
  number(
    value.deviceEndedMonotonicMs - value.deviceStartedMonotonicMs,
    0,
    30_000,
  );
  const clock = value.clockEvidence;
  exact(
    clock,
    "policy_id source boot_id exchanges selected_exchange offset_ms uncertainty_ms calibrated",
  );
  demand(
    clock.policy_id === "synthetic_interval_v1" &&
      clock.source === "simulated" &&
      clock.boot_id === caps.boot_id &&
      clock.calibrated === false,
  );
  array(clock.exchanges, 3, 3);
  integer(clock.selected_exchange, 0, 2);
  number(clock.offset_ms);
  number(clock.uncertainty_ms, 0);
  const recomputed = clock.exchanges.map((exchange) => {
    exact(
      exchange,
      "phone_send_ms device_receive_ms device_send_ms phone_receive_ms phone_timestamp_resolution_ms device_timestamp_resolution_ms offset_lower_ms offset_upper_ms round_trip_ms",
    );
    for (const field of [
      "phone_send_ms",
      "device_receive_ms",
      "device_send_ms",
      "phone_receive_ms",
      "round_trip_ms",
    ] as const)
      number(exchange[field], 0);
    for (const field of [
      "phone_timestamp_resolution_ms",
      "device_timestamp_resolution_ms",
    ] as const)
      demand(number(exchange[field], 0, 1000) > 0);
    const recompute = clockExchange(
      exchange.phone_send_ms,
      exchange.device_receive_ms,
      exchange.device_send_ms,
      exchange.phone_receive_ms,
      exchange.phone_timestamp_resolution_ms,
      exchange.device_timestamp_resolution_ms,
    );
    for (const field of [
      "offset_lower_ms",
      "offset_upper_ms",
      "round_trip_ms",
    ] as const)
      close(exchange[field], recompute[field]);
    close(
      exchange.device_timestamp_resolution_ms,
      caps.timestamp_resolution_ms,
    );
    return recompute;
  });
  const chosen = selectClock(recomputed, caps.boot_id);
  demand(clock.selected_exchange === chosen.selected_exchange);
  close(clock.offset_ms, chosen.offset_ms);
  close(clock.uncertainty_ms, chosen.uncertainty_ms);
  array(value.messages, 10, 32);
  const ids = new Set<string>(),
    acknowledgments = new Set<string>(),
    replied = new Set<string>(),
    clockReplies: Record<string, unknown>[] = [];
  let lastSequence = -1,
    helloCount = 0,
    completeCount = 0;
  for (const [index, message] of value.messages.entries()) {
    exact(
      message,
      "protocol_version message_id device_id boot_id session_id sequence monotonic_ms type payload",
    );
    envelope(message);
    demand(
      utf8(canonicalJson(message)).length + 4 <= 8192 &&
        !ids.has(message.message_id) &&
        message.sequence > lastSequence,
    );
    same(
      [message.device_id, message.boot_id, message.session_id],
      [caps.device_id, caps.boot_id, context.sessionId],
    );
    ids.add(message.message_id);
    lastSequence = message.sequence;
    const p = message.payload;
    if (message.type === "ack") {
      exact(p, "ack_message_id status");
      const request = uuid(p.ack_message_id);
      demand(p.status === "accepted" && !acknowledgments.has(request));
      acknowledgments.add(request);
    } else if (message.type === "hello" || message.type === "clock_sync") {
      exact(
        p,
        message.type === "hello"
          ? "request_message_id source configuration_id"
          : "request_message_id phone_send_ms device_receive_ms device_send_ms",
      );
      const request = uuid(p.request_message_id);
      demand(acknowledgments.has(request) && !replied.has(request));
      replied.add(request);
      if (message.type === "hello") {
        demand(
          p.source === "simulated" &&
            p.configuration_id === "synthetic_bench_v1",
        );
        helloCount++;
      } else {
        for (const key of [
          "phone_send_ms",
          "device_receive_ms",
          "device_send_ms",
        ])
          number(p[key], 0);
        clockReplies.push(p);
      }
    } else {
      demand(
        message.type === "capture_complete" &&
          index === value.messages.length - 1,
      );
      completeCount++;
      exact(
        p,
        "source channel attempt_id capture_id workspace_epoch started_monotonic_ms ended_monotonic_ms fixture_id values",
      );
      same(
        [
          p.source,
          p.channel,
          p.attempt_id,
          p.capture_id,
          p.workspace_epoch,
          p.started_monotonic_ms,
          p.ended_monotonic_ms,
          p.fixture_id,
          p.values,
        ],
        [
          "simulated",
          value.channel,
          context.attemptId,
          context.captureId,
          context.workspaceEpoch,
          value.deviceStartedMonotonicMs,
          value.deviceEndedMonotonicMs,
          value.fixtureId,
          value.values,
        ],
      );
    }
  }
  demand(
    helloCount === 1 &&
      completeCount === 1 &&
      clockReplies.length === 3 &&
      acknowledgments.size === 5,
  );
  for (const [index, reply] of clockReplies.entries())
    for (const key of [
      "phone_send_ms",
      "device_receive_ms",
      "device_send_ms",
    ] as const)
      close(reply[key], clock.exchanges[index]![key]);
  if (value.channel === "saliva") {
    const sample = requireObject(projection.sample),
      results = array(projection.saliva, 3, 3);
    demand(sample.collected_at === value.startedAt);
    const analytes = ["THC", "OH11_THC", "THC_COOH"];
    for (const [index, rawResult] of results.entries()) {
      const result = requireObject(rawResult);
      same(
        [
          result.analyte,
          result.qualifier,
          result.value_ng_ml,
          result.collected_at,
          result.measured_at,
          result.instrument_id,
        ],
        [
          analytes[index],
          index === 0 ? "quantified" : "not_detected",
          index === 0 ? 12 : null,
          value.startedAt,
          value.endedAt,
          association.deviceId,
        ],
      );
      same(result.limits, { lod_ng_ml: 1, loq_ng_ml: 2, upper_ng_ml: 100 });
    }
  } else
    same(
      [
        projection.modality,
        projection.heart_rate_bpm,
        projection.started_at,
        projection.ended_at,
        projection.ecg_rmssd_ms,
        projection.sample_rate_hz,
      ],
      [
        value.channel,
        72,
        value.startedAt,
        value.endedAt,
        null,
        value.channel === "ecg" ? 50 : null,
      ],
    );
}
