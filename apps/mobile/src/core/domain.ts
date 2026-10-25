import { laboratorySupersession } from "./labEvidence";
import { verifyResearchResult } from "./researchResult";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import sessionSchema from "../contracts/session.schema.json";
import measurementSchema from "../contracts/measurement.schema.json";
import resultSchema from "../contracts/result.schema.json";
import attemptSchema from "../contracts/CaptureAttempt.schema.json";
import contextSchema from "../contracts/CaptureContext.schema.json";
import manifestSchema from "../contracts/EvidenceManifest.schema.json";
import alcoholSchema from "../contracts/Alcohol.schema.json";
import profileWriteSchema from "../contracts/ProfileWrite.schema.json";
import {
  assertBytes,
  assertPlainJson,
  clone,
  digest,
  IntegrityError,
  requireObject,
} from "./integrity";
import type {
  CaptureAttempt,
  Channel,
  CheckRecord,
  Component,
  ExportSelection,
  HistoryContext,
  IdFactory,
  Json,
  JsonObject,
  MeasurementResult,
  ProfileEnvelope,
  Snapshot,
  Source,
  WorkspaceState,
} from "./types";

export const INFERENCE_AVAILABLE = false as const;
export const CHANNELS: Channel[] = [
  "saliva",
  "eyes",
  "cardiac",
  "task",
  "alcohol",
];
export const TASK_CONFIGURATION_ID = "choice_inhibit_v0_native_dev_1";
export const TASK_CONFIGURATION_SHA256 =
  "61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3";
export const NULL_TASK_FEATURES = {
  median_rt_ms: null,
  iqr_rt_ms: null,
  p90_rt_ms: null,
  omission_rate: null,
  wrong_go_rate: null,
  no_go_error_rate: null,
};
const ajv = new Ajv2020({
  strict: false,
  allErrors: true,
  allowUnionTypes: true,
});
addFormats(ajv);
ajv.addSchema(measurementSchema);
const sessionValidator = ajv.compile(sessionSchema);
const resultValidator = ajv.compile(resultSchema);
const attemptValidator = ajv.compile(attemptSchema),
  contextValidator = ajv.compile(contextSchema),
  manifestValidator = ajv.compile(manifestSchema),
  alcoholValidator = ajv.compile(alcoholSchema),
  profileValidator = ajv.compile(profileWriteSchema);
export function validateProfileEnvelope(value: ProfileEnvelope): void {
  if (
    !profileValidator({
      profile: value.profile,
      history: value.history,
      context: value.context,
    })
  )
    throw new IntegrityError(
      "PROFILE_CONTRACT",
      "Profile or context fields do not match the supported contract.",
    );
}
export function validateSnapshot(snapshot: Snapshot): void {
  assertPlainJson(snapshot);
  assertBytes(snapshot, 1_048_576);
  if (!sessionValidator(snapshot))
    throw new IntegrityError(
      "INVALID_SNAPSHOT",
      `Check could not be verified: ${sessionValidator.errors
        ?.map((e) => `${e.instancePath} ${e.keyword}`)
        .slice(0, 4)
        .join("; ")}`,
    );
  if (snapshot.created_at !== snapshot.target_at)
    throw new IntegrityError(
      "CONTEXT_TIME_CHANGED",
      "The frozen check time changed.",
    );
  const earliest = Date.parse(snapshot.created_at);
  if (Date.parse(snapshot.capture_completed_at) < earliest)
    throw new IntegrityError(
      "INVALID_TIME",
      "Completion cannot precede check creation.",
    );
  for (const component of [snapshot.eyes, snapshot.cardiac, snapshot.task]) {
    if (
      component.started_at &&
      component.ended_at &&
      Date.parse(component.ended_at) < Date.parse(component.started_at)
    )
      throw new IntegrityError(
        "INVALID_TIME",
        "A capture ends before it starts.",
      );
    if (
      component.status === "invalid" &&
      component === snapshot.task &&
      Object.values(component.features as JsonObject).some((v) => v !== null)
    )
      throw new IntegrityError(
        "INVALID_TASK_FEATURES",
        "An invalid task cannot have aggregate features.",
      );
  }
  if (
    snapshot.cardiac.modality === "ppg" &&
    (snapshot.cardiac.ecg_status !== "not_collected" ||
      snapshot.cardiac.ecg_rmssd_ms !== null)
  )
    throw new IntegrityError("MODALITY_CONFLICT", "PPG is not ECG.");
  for (const measurement of snapshot.saliva) {
    if (measurement.sample_id !== snapshot.sample.sample_id)
      throw new IntegrityError(
        "SAMPLE_MISMATCH",
        "An analyte belongs to another sample.",
      );
    if (
      measurement.qualifier !== "quantified" &&
      measurement.value_ng_ml !== null
    )
      throw new IntegrityError(
        "QUALIFIER_CONFLICT",
        "Censored results must keep null concentrations.",
      );
    const limits = measurement.limits as JsonObject;
    const lod = limits.lod_ng_ml,
      loq = limits.loq_ng_ml,
      upper = limits.upper_ng_ml;
    if (
      (typeof lod === "number" && typeof loq === "number" && lod > loq) ||
      (typeof loq === "number" && typeof upper === "number" && loq > upper)
    )
      throw new IntegrityError(
        "LIMIT_ORDER",
        "The assay limits are inconsistent.",
      );
    if (
      measurement.qualifier === "quantified" &&
      typeof measurement.value_ng_ml === "number" &&
      ((typeof loq === "number" && measurement.value_ng_ml < loq) ||
        (typeof upper === "number" && measurement.value_ng_ml > upper))
    )
      throw new IntegrityError(
        "QUANTIFICATION_RANGE",
        "A concentration is outside the stated quantification interval.",
      );
  }
}
export function verifyResult(
  value: unknown,
  check: Pick<CheckRecord, "id" | "snapshot_sha256" | "snapshot"> &
    Partial<
      Pick<CheckRecord, "context" | "manifest" | "frozen" | "kind" | "attempts">
    >,
): MeasurementResult {
  const object = requireObject(value);
  if (object.schema_version === "1.1.0")
    return verifyResearchResult(value, check);
  if (object.state === "research_estimate")
    throw new IntegrityError(
      "UNSUPPORTED_RESEARCH_RESULT",
      "This release cannot display or generate an impairment estimate.",
    );
  if (!resultValidator(value))
    throw new IntegrityError(
      "INVALID_RESULT",
      "We could not verify this result.",
    );
  if (
    object.session_id !== check.id ||
    object.input_sha256 !== check.snapshot_sha256 ||
    object.target_at !== check.snapshot.target_at
  )
    throw new IntegrityError(
      "RESULT_LINKAGE",
      "This result does not match the frozen check.",
    );
  if (
    object.probability !== null ||
    object.classification !== null ||
    object.operating_threshold !== null ||
    object.model_id !== null
  )
    throw new IntegrityError(
      "INFERENCE_DISABLED",
      "Impairment inference is unavailable in this release.",
    );
  return value as unknown as MeasurementResult;
}
export function emptyProfile(now: string): ProfileEnvelope {
  return {
    profile_version_id: null,
    revision: 0,
    etag: '"0"',
    sync: "local",
    profile: {
      age_years: null,
      height_cm: null,
      weight_kg: null,
      bmi: null,
      recorded_at: now,
      source: "self_report",
    },
    history: {
      use_frequency: "unknown",
      route: "unknown",
      time_since_use_min: null,
      recent_exercise: null,
      sleep_hours: null,
      alcohol_co_use: "unknown",
    },
    context: {
      last_use_status: "unknown",
      last_use_at: null,
      confirmed_at: now,
    },
  };
}
export function emptyWorkspace(
  workspace: string,
  now: string,
  generation = 1,
): WorkspaceState {
  return {
    schema_version: 1,
    workspace,
    generation,
    profile: emptyProfile(now),
    checks: [],
    queue: [],
    preferences: {
      theme: "system",
      reducedMotion: "system",
      units: "metric",
      retryQueuedAutomatically: false,
    },
    notice: null,
    acknowledgedNotice: null,
    jobs: [],
    capabilities: null,
    exportEntry: null,
    studies: [],
    rawRecordingStatuses: {},
    rawRecordingFences: {},
    historyIndex: [],
    historyCursor: null,
  };
}
export function normalizeProfile(
  profile: ProfileEnvelope,
  now: string,
): ProfileEnvelope {
  const next = clone(profile),
    p = next.profile;
  if (
    p.age_years !== null &&
    (!Number.isInteger(p.age_years) || p.age_years < 18 || p.age_years > 125)
  )
    throw new IntegrityError(
      "AGE_RANGE",
      "Age must be a whole number from 18 to 125, or blank.",
    );
  for (const [key, cap, label] of [
    ["height_cm", 300, "Height"],
    ["weight_kg", 500, "Weight"],
  ] as const)
    if (
      p[key] !== null &&
      (!Number.isFinite(p[key]) || p[key]! <= 0 || p[key]! > cap)
    )
      throw new IntegrityError(
        "PROFILE_RANGE",
        `${label} is outside the supported entry range.`,
      );
  p.bmi =
    p.height_cm && p.weight_kg ? p.weight_kg / (p.height_cm / 100) ** 2 : null;
  p.recorded_at = now;
  if (
    next.history.sleep_hours !== null &&
    (!Number.isFinite(next.history.sleep_hours) ||
      next.history.sleep_hours < 0 ||
      next.history.sleep_hours > 24)
  )
    throw new IntegrityError(
      "SLEEP_RANGE",
      "Sleep must be between 0 and 24 hours, or blank.",
    );
  if (next.context.last_use_status === "known") {
    if (
      typeof next.context.last_use_at !== "string" ||
      !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(
        next.context.last_use_at,
      )
    )
      throw new IntegrityError(
        "LAST_USE_TIME",
        "Enter a complete date and time with a UTC offset or Z.",
      );
    const time = next.context.last_use_at
      ? Date.parse(next.context.last_use_at)
      : NaN;
    if (!Number.isFinite(time) || time > Date.parse(now))
      throw new IntegrityError(
        "LAST_USE_TIME",
        "Choose a last-use date and time that is not in the future.",
      );
    next.context.last_use_at = new Date(time).toISOString();
    next.history.time_since_use_min = (Date.parse(now) - time) / 60_000;
  } else {
    next.context.last_use_at = null;
    next.history.time_since_use_min = null;
  }
  next.context.confirmed_at = now;
  validateProfileEnvelope(next);
  assertPlainJson(next);
  return next;
}
export function convertHeight(value: number, unit: "cm" | "in"): number {
  return unit === "in" ? value * 2.54 : value;
}
export function convertWeight(value: number, unit: "kg" | "lb"): number {
  return unit === "lb" ? value * 0.45359237 : value;
}
export function normalizeConcentration(
  value: number | null,
  unit: "pg/mL" | "ng/mL",
): number | null {
  if (value === null) return null;
  if (!Number.isFinite(value) || value < 0)
    throw new IntegrityError(
      "CONCENTRATION",
      "Concentration must be finite and nonnegative.",
    );
  return unit === "pg/mL" ? value / 1000 : value;
}
const baseComponent = (source: Source = "prototype_sensor"): Component => ({
  status: "not_collected",
  source,
  started_at: null,
  ended_at: null,
  quality_flags: ["NOT_COLLECTED"],
});
export function createCheck(
  state: WorkspaceState,
  opts: {
    now: string;
    id: IdFactory;
    kind: CheckRecord["kind"];
    accountRef?: string;
    contextConfirmed: boolean;
    supersedes?: string;
  },
): CheckRecord {
  if (!opts.contextConfirmed)
    throw new IntegrityError(
      "CONTEXT_CONFIRMATION",
      "Review and confirm this check’s context before starting.",
    );
  if (
    state.checks.some(
      (c) =>
        !c.frozen &&
        c.workspace === state.workspace &&
        c.generation === state.generation &&
        c.delivery !== "quarantined",
    )
  )
    throw new IntegrityError(
      "ACTIVE_DRAFT",
      "Resume or discard your current draft before starting another.",
    );
  const { now, id } = opts,
    profile =
      opts.kind === "engineering_fixture"
        ? emptyProfile(now)
        : normalizeProfile(state.profile, now),
    sessionId = id();
  if (opts.kind === "engineering_fixture") profile.profile.source = "synthetic";
  else profile.profile.recorded_at = state.profile.profile.recorded_at;
  const history = clone(profile.history),
    source: Source =
      opts.kind === "measurement" ? "prototype_sensor" : "simulated";
  const snapshot: Snapshot = {
    schema_version: "0.1.0",
    session_id: sessionId,
    supersedes_session_id: opts.supersedes ?? null,
    mode: opts.kind === "measurement" ? "analytical" : "synthetic",
    subject_ref: opts.accountRef ?? "local-guest",
    study_id: null,
    protocol_id: opts.kind === "measurement" ? null : "mobile-demonstration-v1",
    created_at: now,
    target_at: now,
    capture_completed_at: now,
    clock_uncertainty_ms: null,
    acquisition_span_ms: null,
    device: {
      device_id: "unassociated",
      boot_id: "unassociated",
      hardware_revision: "unknown",
      firmware_version: "unknown",
    },
    profile: clone(profile.profile),
    history,
    baseline_ref: null,
    sample: {
      sample_id: id(),
      collection_method_id: "unavailable",
      collected_at: null,
      volume_ml: null,
      dilution_factor: null,
      status: "not_collected",
      quality_flags: ["NOT_COLLECTED"],
    },
    saliva: [],
    eyes: {
      ...baseComponent(source),
      capture_config_id: "unavailable",
      camera_id: "unavailable",
      frame_rate_hz: null,
      scale_basis: "unscaled",
      baseline_diameter_mm: null,
      relative_constriction: null,
      latency_ms: null,
      raw_artifact_id: null,
    },
    cardiac: {
      ...baseComponent(source),
      acquisition_config_id: "unavailable",
      modality: "ppg",
      heart_rate_bpm: null,
      ecg_status: "not_collected",
      ecg_rmssd_ms: null,
      sample_rate_hz: null,
      raw_artifact_id: null,
    },
    task: {
      ...baseComponent(source),
      task_id: id(),
      task_version: "choice_inhibit_v0",
      config_sha256: TASK_CONFIGURATION_SHA256,
      practice_trials: 0,
      scored_trials: 0,
      go_trials: 0,
      no_go_trials: 0,
      valid_correct_go_trials: 0,
      features: { ...NULL_TASK_FEATURES },
      events_artifact_id: null,
    },
  };
  return {
    id: sessionId,
    generation: state.generation,
    workspace: state.workspace,
    kind: opts.kind,
    stage: "profile",
    frozen: false,
    snapshot,
    context: {
      schema_version: "1.0.0",
      session_id: sessionId,
      context_confirmed_at: now,
      profile_version_id: profile.profile_version_id,
      profile_snapshot_sha256: digest(snapshot.profile),
      history_snapshot_sha256: digest(history),
      protocol_id: snapshot.protocol_id,
      configuration_refs: [
        {
          id: TASK_CONFIGURATION_ID,
          version: "1.0.0",
          sha256: TASK_CONFIGURATION_SHA256,
          scope: "uncalibrated_practice",
        },
      ],
      baseline_refs: [],
      device_associations: [],
      self_report_context: { ...profile.context, confirmed_at: now },
    },
    attempts: [],
    selected_cardiac_attempt_id: null,
    manifest: null,
    snapshot_sha256: null,
    evidence_sha256: null,
    result: null,
    alcohol: null,
    delivery: "local_draft",
    error: null,
    remote_revision: 0,
    remote_etag: '"0"',
    updated_at: now,
  };
}
export type CardiacModality = "ppg" | "ecg";
export function cardiacAttemptModality(
  attempt: CaptureAttempt,
): CardiacModality | null {
  if (attempt.component !== "cardiac") return null;
  const declared = attempt.component_metadata.modality;
  const projection = attempt.component_metadata.projection;
  const projected =
    projection && typeof projection === "object" && !Array.isArray(projection)
      ? projection.modality
      : null;
  if (declared === "ppg" || declared === "ecg") return declared;
  return projected === "ppg" || projected === "ecg" ? projected : null;
}
export function selectCardiacAttempt(
  check: CheckRecord,
  attemptId: string,
  now = check.updated_at,
): CheckRecord {
  if (check.frozen)
    throw new IntegrityError(
      "FROZEN_CHECK",
      "The saved cardiac selection is immutable. Start a replacement check for new measurements.",
    );
  if (check.attempts.some((a) => a.status === "started"))
    throw new IntegrityError(
      "ACTIVE_CAPTURE",
      "End the active capture before choosing the cardiac result.",
    );
  const attempt = check.attempts.find(
    (a) => a.attempt_id === attemptId && a.component === "cardiac",
  );
  if (
    !attempt ||
    attempt.status !== "valid" ||
    !cardiacAttemptModality(attempt)
  )
    throw new IntegrityError(
      "CARDIAC_SELECTION_INVALID",
      "Choose a retained valid PPG or ECG attempt from this check.",
    );
  const projection = requireObject(attempt.component_metadata.projection);
  if (
    projection.modality !== cardiacAttemptModality(attempt) ||
    projection.status !== "valid" ||
    projection.source !== attempt.source ||
    projection.started_at !== attempt.started_at ||
    projection.ended_at !== attempt.ended_at
  )
    throw new IntegrityError(
      "CARDIAC_SELECTION_INVALID",
      "The chosen cardiac attempt differs from its retained projection.",
    );
  const next = clone(check);
  next.selected_cardiac_attempt_id = attemptId;
  next.snapshot.cardiac = clone(projection) as Component;
  next.updated_at = now;
  return next;
}
export function startAttempt(
  check: CheckRecord,
  channel: Channel,
  now: string,
  id: IdFactory,
  source: Source,
  configId: string | null = null,
  configHash: string | null = null,
  cardiacModality?: CardiacModality,
): { check: CheckRecord; attempt: CaptureAttempt } {
  if (check.frozen)
    throw new IntegrityError(
      "FROZEN_CHECK",
      "Start a replacement check to collect new measurements.",
    );
  if (check.attempts.some((a) => a.status === "started"))
    throw new IntegrityError(
      "ACTIVE_CAPTURE",
      "End the active capture before continuing.",
    );
  if (check.attempts.length >= 128)
    throw new IntegrityError(
      "ATTEMPT_LIMIT",
      "This check has reached its attempt limit. Save it and start a replacement.",
    );
  if (
    channel === "cardiac" &&
    cardiacModality !== "ppg" &&
    cardiacModality !== "ecg"
  )
    throw new IntegrityError(
      "CARDIAC_MODALITY_REQUIRED",
      "Choose PPG or ECG before starting the cardiac attempt.",
    );
  if (channel !== "cardiac" && cardiacModality !== undefined)
    throw new IntegrityError(
      "CARDIAC_MODALITY_MISPLACED",
      "A cardiac modality cannot be attached to another component.",
    );
  const componentAttempts = check.attempts.filter(
    (a) => a.component === channel,
  );
  if (
    channel === "cardiac" &&
    componentAttempts.some(
      (a) => a.status === "valid" && !cardiacAttemptModality(a),
    )
  )
    throw new IntegrityError(
      "CARDIAC_MODALITY_UNKNOWN",
      "The existing cardiac evidence has no verifiable modality.",
    );
  const matching = componentAttempts.filter(
    (a) =>
      channel !== "cardiac" || cardiacAttemptModality(a) === cardiacModality,
  );
  const prior = matching.at(-1);
  if (matching.some((a) => a.status === "valid"))
    throw new IntegrityError(
      "VALID_CAPTURE_EXISTS",
      "A valid capture already exists for this component and modality. Start a new check for another acquisition.",
    );
  const next = clone(check),
    attempt: CaptureAttempt = {
      schema_version: "1.0.0",
      session_id: check.id,
      attempt_id: id(),
      component: channel,
      record_id: id(),
      supersedes_attempt_id:
        prior && ["invalid", "canceled"].includes(prior.status)
          ? prior.attempt_id
          : null,
      status: "started",
      source,
      started_at: now,
      ended_at: null,
      configuration_id: configId,
      configuration_hash: configHash,
      quality_flags: [],
      component_metadata:
        channel === "cardiac" ? { modality: cardiacModality! } : {},
      artifact_refs: [],
      attestation_refs: [],
    };
  if (channel === "saliva") attempt.record_id = check.snapshot.sample.sample_id;
  next.attempts.push(attempt);
  next.updated_at = now;
  return { check: next, attempt };
}
export function settleAttempt(
  check: CheckRecord,
  attemptId: string,
  projection: JsonObject,
  status: "valid" | "invalid" | "canceled" | "not_collected",
  now: string,
  flags: string[] = [],
  metadata: JsonObject = {},
): CheckRecord {
  if (check.frozen)
    throw new IntegrityError(
      "FROZEN_CHECK",
      "The saved check cannot be changed.",
    );
  const next = clone(check),
    attempt = next.attempts.find((a) => a.attempt_id === attemptId);
  if (!attempt)
    throw new IntegrityError(
      "ATTEMPT_MISMATCH",
      "The capture belongs to another check.",
    );
  const modality = cardiacAttemptModality(attempt);
  if (
    attempt.component === "cardiac" &&
    (!modality ||
      projection.modality !== modality ||
      (metadata.modality !== undefined && metadata.modality !== modality))
  )
    throw new IntegrityError(
      "CARDIAC_MODALITY_CHANGED",
      "A cardiac attempt cannot change its selected acquisition modality.",
    );
  const modalityMetadata: JsonObject =
    attempt.component === "cardiac" ? { modality: modality! } : {};
  if (attempt.status !== "started") {
    if (
      attempt.status === status &&
      attempt.ended_at === (status === "not_collected" ? null : now) &&
      digest(attempt.quality_flags) === digest(flags) &&
      digest(attempt.component_metadata) ===
        digest({
          ...metadata,
          ...modalityMetadata,
          ...(attempt.component_metadata.armed_at !== undefined
            ? { armed_at: attempt.component_metadata.armed_at }
            : {}),
          projection,
        })
    )
      return next;
    throw new IntegrityError(
      "IMMUTABLE_ATTEMPT",
      "The accepted capture cannot be overwritten.",
    );
  }
  attempt.status = status;
  attempt.ended_at = status === "not_collected" ? null : now;
  if (status === "not_collected") attempt.started_at = null;
  const armedAt = attempt.started_at;
  if (
    ["eyes", "cardiac", "task"].includes(attempt.component) &&
    typeof projection.started_at === "string"
  )
    attempt.started_at = projection.started_at;
  else if (
    attempt.component === "saliva" &&
    typeof (projection.sample as JsonObject)?.collected_at === "string"
  )
    attempt.started_at = (projection.sample as JsonObject)
      .collected_at as string;
  else if (
    attempt.component === "alcohol" &&
    typeof projection.collected_at === "string"
  )
    attempt.started_at = projection.collected_at;
  attempt.quality_flags = flags;
  attempt.component_metadata = {
    ...metadata,
    ...modalityMetadata,
    ...(armedAt !== attempt.started_at ? { armed_at: armedAt } : {}),
    projection: clone(projection),
  };
  assertBytes(attempt, 524_288);
  if (attempt.component === "saliva") {
    next.snapshot.sample = clone(
      projection.sample,
    ) as unknown as Snapshot["sample"];
    next.snapshot.saliva = clone(projection.saliva) as JsonObject[];
    attempt.record_id = next.snapshot.sample.sample_id;
  } else if (attempt.component === "alcohol") next.alcohol = clone(projection);
  else if (attempt.component === "cardiac") {
    const otherValid = next.attempts.filter(
      (a) =>
        a.component === "cardiac" &&
        a.status === "valid" &&
        a.attempt_id !== attemptId,
    );
    if (otherValid.some((a) => cardiacAttemptModality(a) === modality))
      throw new IntegrityError(
        "VALID_CAPTURE_EXISTS",
        "A second valid acquisition of the same cardiac modality is not permitted.",
      );
    if (status === "valid" && otherValid.length > 0) {
      // Keep the earlier displayed projection until Review explicitly chooses between the two retained observations.
      next.selected_cardiac_attempt_id = null;
    } else if (otherValid.length === 0) {
      next.snapshot.cardiac = clone(projection) as Component;
      next.selected_cardiac_attempt_id = attemptId;
    }
  } else {
    next.snapshot[attempt.component] = clone(projection) as Component;
    if (attempt.component === "task")
      attempt.record_id = String(projection.task_id);
  }
  next.updated_at = now;
  return next;
}
export function simulatedCapture(
  check: CheckRecord,
  channel: Channel,
  now: string,
  id: IdFactory,
  modality: "ppg" | "ecg" = "ppg",
): CheckRecord {
  if (check.kind === "measurement")
    throw new IntegrityError(
      "SYNTHETIC_PARENT_REQUIRED",
      "Fictional values can only be added to an explicitly synthetic check.",
    );
  const configId = `fictional-${channel}-${modality}-v1`;
  const started = startAttempt(
    check,
    channel,
    now,
    id,
    "simulated",
    configId,
    digest({ fixture: configId }),
    channel === "cardiac" ? modality : undefined,
  );
  let projection: JsonObject;
  const base: Component = {
    status: "valid",
    source: "simulated",
    started_at: now,
    ended_at: now,
    quality_flags: ["FICTIONAL_FIXTURE"],
  };
  if (channel === "saliva") {
    const sampleId = id();
    projection = {
      sample: {
        sample_id: sampleId,
        collection_method_id: configId,
        collected_at: now,
        volume_ml: 1,
        dilution_factor: 1,
        status: "valid",
        quality_flags: ["FICTIONAL_FIXTURE"],
      },
      saliva: ["THC", "THC_COOH", "OH11_THC"].map((analyte, index) => ({
        schema_version: "0.1.0",
        measurement_id: id(),
        sample_id: sampleId,
        analyte,
        qualifier: index === 0 ? "quantified" : "not_measured",
        value_ng_ml: index === 0 ? 12.5 : null,
        unit: "ng/mL",
        assay_basis: "free",
        limits: {
          lod_ng_ml: index === 0 ? 1 : null,
          loq_ng_ml: index === 0 ? 2 : null,
          upper_ng_ml: index === 0 ? 100 : null,
        },
        source: "simulated",
        method_id: index === 0 ? configId : null,
        calibration_id: index === 0 ? "fictional-calibration-v1" : null,
        cartridge_lot: index === 0 ? "FICTIONAL-LOT" : null,
        instrument_id: index === 0 ? "fictional-reader" : null,
        operator_ref: null,
        collected_at: now,
        measured_at: index === 0 ? now : null,
        quality_flags: ["FICTIONAL_FIXTURE"],
        original_report: {
          value: index === 0 ? 12.5 : null,
          unit: "ng/mL",
          qualifier: index === 0 ? "quantified" : "not_measured",
        },
        uncertainty_ng_ml: null,
        concentration_basis: "neat_oral_fluid",
        correction_status: "not_corrected",
      })),
    };
  } else if (channel === "eyes")
    projection = {
      ...base,
      capture_config_id: configId,
      camera_id: "fictional-camera",
      frame_rate_hz: 60,
      scale_basis: "normalized",
      baseline_diameter_mm: null,
      relative_constriction: 0.18,
      latency_ms: 280,
      raw_artifact_id: null,
    };
  else if (channel === "cardiac")
    projection = {
      ...base,
      acquisition_config_id: configId,
      modality,
      heart_rate_bpm: 72,
      ecg_status: modality === "ecg" ? "valid" : "not_collected",
      ecg_rmssd_ms: modality === "ecg" ? 35 : null,
      sample_rate_hz: modality === "ecg" ? 250 : 100,
      raw_artifact_id: null,
    };
  else if (channel === "alcohol")
    projection = {
      schema_version: "1.0.0",
      measurement_id: started.attempt.record_id,
      session_id: check.id,
      collected_at: now,
      measured_at: now,
      source: "simulated",
      qualifier: "quantified",
      value_mg_l: 0.1,
      unit: "mg/L",
      limits: { lod_mg_l: 0.01, loq_mg_l: 0.02, upper_mg_l: 1 },
      method_id: configId,
      calibration_id: "fictional-calibration",
      device_id: "fictional-breath-instrument",
      boot_id: "fictional-boot",
      configuration_hash: digest({ fixture: configId }),
      quality_flags: ["FICTIONAL_FIXTURE"],
    };
  else
    throw new IntegrityError(
      "NATIVE_TASK_REQUIRED",
      "Use the native reaction task for actual tap measurements.",
    );
  return settleAttempt(
    started.check,
    started.attempt.attempt_id,
    projection,
    "valid",
    now,
    ["FICTIONAL_FIXTURE"],
    { fixture_id: configId },
  );
}
export function taskProjection(native: JsonObject, taskId: string): Component {
  const counts = requireObject(native.counts ?? {}),
    features = native.status === "valid" ? requireObject(native.features) : {};
  const num = (key: string) =>
    typeof counts[key] === "number" ? (counts[key] as number) : 0;
  const featureKeys: Record<string, string> = {
    median_rt_ms: "medianRtMs",
    iqr_rt_ms: "iqrRtMs",
    p90_rt_ms: "p90RtMs",
    omission_rate: "omissionRate",
    wrong_go_rate: "wrongGoRate",
    no_go_error_rate: "noGoErrorRate",
  };
  return {
    status: native.status === "valid" ? "valid" : "invalid",
    source: "prototype_sensor",
    started_at: typeof native.startedAt === "string" ? native.startedAt : null,
    ended_at: typeof native.endedAt === "string" ? native.endedAt : null,
    quality_flags: [
      ...new Set([
        "uncalibrated",
        ...(Array.isArray(native.qualityFlags)
          ? (native.qualityFlags as string[])
          : ["NATIVE_RESULT_UNAVAILABLE"]),
      ]),
    ],
    task_id: taskId,
    task_version: "choice_inhibit_v0",
    config_sha256: TASK_CONFIGURATION_SHA256,
    practice_trials: num("presentedPractice"),
    scored_trials: num("presentedScored"),
    go_trials: num("presentedGo"),
    no_go_trials: num("presentedNoGo"),
    valid_correct_go_trials: num("correctGo"),
    features: Object.fromEntries(
      Object.entries(featureKeys).map(([key, from]) => [
        key,
        typeof features[from] === "number" ? features[from] : null,
      ]),
    ) as JsonObject,
    events_artifact_id: null,
  };
}
export function interruptStartedAttempts(
  check: CheckRecord,
  now: string,
  preserveAttemptId?: string,
): CheckRecord {
  let next = clone(check);
  for (const attempt of next.attempts.filter(
    (a) => a.status === "started" && a.attempt_id !== preserveAttemptId,
  )) {
    const component = attempt.component;
    let projection: JsonObject;
    if (component === "saliva")
      projection = {
        sample: {
          ...next.snapshot.sample,
          status: "invalid",
          quality_flags: ["INTERRUPTED"],
          collected_at: null,
        },
        saliva: [],
      };
    else if (component === "alcohol")
      projection = {
        ...(next.alcohol ?? {}),
        qualifier: "invalid",
        value_mg_l: null,
        quality_flags: ["INTERRUPTED"],
      };
    else if (component === "cardiac")
      projection = {
        status: "invalid",
        source: attempt.source,
        started_at: attempt.started_at,
        ended_at: now,
        quality_flags: ["INTERRUPTED"],
        acquisition_config_id: attempt.configuration_id ?? "unavailable",
        modality: cardiacAttemptModality(attempt),
        heart_rate_bpm: null,
        ecg_status:
          cardiacAttemptModality(attempt) === "ecg"
            ? "invalid"
            : "not_collected",
        ecg_rmssd_ms: null,
        sample_rate_hz: null,
        raw_artifact_id: null,
      };
    else
      projection = {
        ...next.snapshot[component],
        status: "invalid",
        source: attempt.source,
        started_at: attempt.started_at,
        ended_at: now,
        quality_flags: ["INTERRUPTED"],
        ...(component === "task"
          ? { features: { ...NULL_TASK_FEATURES }, task_id: attempt.record_id }
          : {}),
      };
    next = settleAttempt(
      next,
      attempt.attempt_id,
      projection,
      "invalid",
      now,
      ["INTERRUPTED"],
      attempt.component_metadata.instruction_receipt
        ? {
            instruction_receipt: clone(
              attempt.component_metadata.instruction_receipt,
            ),
          }
        : {},
    );
  }
  return next;
}
export function freezeCheck(
  check: CheckRecord,
  now: string,
  id: IdFactory,
): CheckRecord {
  if (
    check.labCollection &&
    ["collecting", "pending_lab"].includes(check.labCollection.state)
  )
    throw new IntegrityError(
      "LAB_ANALYSIS_PENDING",
      "Save this specimen as a draft. Refresh its independently admitted laboratory report or explicitly end analysis before finalizing.",
    );
  if (check.frozen) {
    verifyCheck(check);
    return clone(check);
  }
  if (check.attempts.some((a) => a.status === "started"))
    throw new IntegrityError(
      "ACTIVE_CAPTURE",
      "End the active capture before saving.",
    );
  const next = clone(check);
  next.snapshot.capture_completed_at = now;
  const cardiac = next.attempts.filter((a) => a.component === "cardiac");
  const validCardiac = cardiac.filter((a) => a.status === "valid");
  if (validCardiac.length > 1 && !next.selected_cardiac_attempt_id)
    throw new IntegrityError(
      "CARDIAC_SELECTION_REQUIRED",
      "Review both retained observations and choose PPG or ECG before saving this check.",
    );
  const cardiacId =
    next.selected_cardiac_attempt_id ??
    (validCardiac.length === 1
      ? validCardiac[0]!.attempt_id
      : (cardiac.at(-1)?.attempt_id ?? null));
  if (
    cardiacId &&
    !cardiac.some(
      (a) =>
        a.attempt_id === cardiacId &&
        (validCardiac.length === 0 || a.status === "valid"),
    )
  )
    throw new IntegrityError(
      "CARDIAC_SELECTION_INVALID",
      "The chosen cardiac attempt is not available in this check.",
    );
  next.selected_cardiac_attempt_id = cardiacId;
  const dates = next.attempts
    .flatMap((a) => [a.started_at, a.ended_at])
    .filter((x): x is string => !!x)
    .map(Date.parse);
  next.snapshot.acquisition_span_ms = dates.length
    ? Math.max(...dates) - Math.min(...dates)
    : null;
  validateSnapshot(next.snapshot);
  if (
    digest(next.snapshot.profile) !== next.context.profile_snapshot_sha256 ||
    digest(next.snapshot.history) !== next.context.history_snapshot_sha256
  )
    throw new IntegrityError(
      "FROZEN_CONTEXT_CHANGED",
      "The original profile/context no longer matches.",
    );
  const selected = Object.fromEntries(
    CHANNELS.map((c) => [
      c,
      next.attempts.filter((a) => a.component === c).at(-1)?.attempt_id ?? null,
    ]),
  ) as Record<Channel, string | null>;
  selected.cardiac = cardiacId;
  next.manifest = {
    schema_version: "1.0.0",
    session_id: next.id,
    context_sha256: digest(next.context),
    attempts: next.attempts.map((a) => ({
      attempt_id: a.attempt_id,
      sha256: digest(a),
    })),
    selected,
  };
  next.snapshot_sha256 = digest(next.snapshot);
  next.evidence_sha256 = digest(next.manifest);
  next.frozen = true;
  next.delivery = "local_finalized";
  next.updated_at = now;
  next.result = {
    schema_version: "0.1.0",
    result_id: id(),
    session_id: next.id,
    state: "measurement_only",
    target_at: next.snapshot.target_at,
    evaluated_at: now,
    model_id: null,
    model_lifecycle: null,
    endpoint_id: null,
    probability: null,
    classification: null,
    operating_threshold: null,
    uncertainty_policy_id: null,
    reason_codes: [
      "MODEL_UNAVAILABLE",
      ...(next.kind !== "measurement"
        ? ["SIMULATED_INPUT", "DEMO_ONLY"]
        : ["ANALYTICAL_ONLY"]),
    ],
    input_sha256: next.snapshot_sha256,
    provenance_summary: [
      ...new Set<Source>([
        ...next.attempts.map((a) => a.source),
        next.snapshot.task.source,
      ]),
    ],
    replaces_result_id: null,
  };
  verifyCheck(next);
  return next;
}
export function verifyCheck(check: CheckRecord): void {
  if (!check.frozen) return;
  validateSnapshot(check.snapshot);
  if (
    !contextValidator(check.context) ||
    !manifestValidator(check.manifest) ||
    check.attempts.some((a) => !attemptValidator(a)) ||
    (check.alcohol && !alcoholValidator(check.alcohol))
  )
    throw new IntegrityError(
      "EVIDENCE_CONTRACT",
      "The evidence does not match this application contract.",
    );
  if (
    check.snapshot.session_id !== check.id ||
    check.context.session_id !== check.id ||
    check.context.context_confirmed_at !== check.snapshot.created_at ||
    check.context.protocol_id !== check.snapshot.protocol_id ||
    digest(check.snapshot.profile) !== check.context.profile_snapshot_sha256 ||
    digest(check.snapshot.history) !== check.context.history_snapshot_sha256
  )
    throw new IntegrityError(
      "CONTEXT_BINDING",
      "The frozen context is inconsistent with this check.",
    );
  if (
    !check.manifest ||
    digest(check.snapshot) !== check.snapshot_sha256 ||
    digest(check.manifest) !== check.evidence_sha256 ||
    digest(check.context) !== check.manifest.context_sha256
  )
    throw new IntegrityError(
      "EVIDENCE_HASH_MISMATCH",
      "The saved evidence could not be verified.",
    );
  if (
    check.attempts.length !== check.manifest.attempts.length ||
    check.attempts.length > 128
  )
    throw new IntegrityError(
      "MANIFEST_COUNT",
      "The attempt manifest is incomplete.",
    );
  if (
    check.manifest.session_id !== check.id ||
    new Set(check.attempts.map((a) => a.attempt_id)).size !==
      check.attempts.length ||
    new Set(check.manifest.attempts.map((a) => a.attempt_id)).size !==
      check.manifest.attempts.length ||
    check.attempts.some((a) => a.session_id !== check.id)
  )
    throw new IntegrityError(
      "MANIFEST_IDENTITY",
      "The evidence manifest contains duplicate or foreign records.",
    );
  for (const entry of check.manifest.attempts) {
    const a = check.attempts.find(
      (item) => item.attempt_id === entry.attempt_id,
    );
    if (!a || a.status === "started" || digest(a) !== entry.sha256)
      throw new IntegrityError(
        "ATTEMPT_HASH_MISMATCH",
        "Capture evidence is incomplete or changed.",
      );
  }
  for (const attempt of check.attempts) {
    if (attempt.supersedes_attempt_id) {
      const previous = check.attempts.find(
        (a) => a.attempt_id === attempt.supersedes_attempt_id,
      );
      if (
        !previous ||
        previous.component !== attempt.component ||
        (!["invalid", "canceled"].includes(previous.status) &&
          !laboratorySupersession(check, attempt, previous)) ||
        (attempt.component === "cardiac" &&
          cardiacAttemptModality(previous) !== cardiacAttemptModality(attempt))
      )
        throw new IntegrityError(
          "ATTEMPT_LINEAGE",
          "A retry can replace only an invalid or canceled attempt of the same component and cardiac modality.",
        );
    }
    if (["eyes", "cardiac", "task"].includes(attempt.component)) {
      const projection = attempt.component_metadata.projection as JsonObject;
      if (
        !projection ||
        projection.started_at !== attempt.started_at ||
        projection.ended_at !== attempt.ended_at ||
        projection.source !== attempt.source ||
        projection.status !==
          (attempt.status === "canceled" ? "invalid" : attempt.status)
      )
        throw new IntegrityError(
          "ATTEMPT_PROJECTION",
          "Capture timing, quality or source differs from its projection.",
        );
    }
    if (
      attempt.component === "cardiac" &&
      (!cardiacAttemptModality(attempt) ||
        (attempt.component_metadata.projection as JsonObject).modality !==
          cardiacAttemptModality(attempt))
    )
      throw new IntegrityError(
        "CARDIAC_MODALITY_CHANGED",
        "Retained cardiac modality differs from its projection.",
      );
  }
  const validCardiac = check.attempts.filter(
    (a) => a.component === "cardiac" && a.status === "valid",
  );
  if (
    new Set(validCardiac.map(cardiacAttemptModality)).size !==
    validCardiac.length
  )
    throw new IntegrityError(
      "VALID_CAPTURE_EXISTS",
      "More than one valid capture of the same cardiac modality is present.",
    );
  if (
    validCardiac.length &&
    !validCardiac.some((a) => a.attempt_id === check.manifest!.selected.cardiac)
  )
    throw new IntegrityError(
      "CARDIAC_SELECTION_INVALID",
      "The manifest must select one retained valid cardiac observation.",
    );
  if (
    check.selected_cardiac_attempt_id !== undefined &&
    check.selected_cardiac_attempt_id !== check.manifest.selected.cardiac
  )
    throw new IntegrityError(
      "CARDIAC_SELECTION_CHANGED",
      "Local cardiac selection differs from the immutable manifest.",
    );
  for (const channel of CHANNELS) {
    const selectedId = check.manifest.selected[channel];
    if (!selectedId) continue;
    const attempt = check.attempts.find(
      (a) => a.attempt_id === selectedId && a.component === channel,
    );
    if (!attempt)
      throw new IntegrityError(
        "SELECTED_ATTEMPT_MISMATCH",
        "A selected capture is missing.",
      );
    const projection =
      channel === "saliva"
        ? { sample: check.snapshot.sample, saliva: check.snapshot.saliva }
        : channel === "alcohol"
          ? check.alcohol
          : check.snapshot[channel];
    if (digest(attempt.component_metadata.projection) !== digest(projection))
      throw new IntegrityError(
        "PROJECTION_MISMATCH",
        "The selected measurement differs from its capture evidence.",
      );
  }
  if (check.result) verifyResult(check.result, check);
}
export function validateSelection(selection: ExportSelection): void {
  const { kind, session_ids: ids } = selection;
  if (
    !["single", "selected", "all"].includes(kind) ||
    !Array.isArray(ids) ||
    new Set(ids).size !== ids.length ||
    ids.some(
      (id) =>
        !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
          id,
        ),
    ) ||
    (kind === "single" && ids.length !== 1) ||
    (kind === "selected" && (ids.length < 1 || ids.length > 500)) ||
    (kind === "all" && ids.length !== 0)
  )
    throw new IntegrityError(
      "INVALID_SELECTION",
      "Review the exact checks selected for export.",
    );
}
export function selectExportChecks(
  state: WorkspaceState,
  selection: ExportSelection,
): CheckRecord[] {
  validateSelection(selection);
  const eligible = (check: CheckRecord) =>
    check.frozen &&
    check.workspace === state.workspace &&
    check.generation === state.generation &&
    check.delivery !== "quarantined";
  const checks =
    selection.kind === "all"
      ? state.checks.filter(eligible)
      : selection.session_ids.map((id) => {
          const c = state.checks.find((c) => c.id === id && eligible(c));
          if (!c)
            throw new IntegrityError(
              "SELECTION_UNAVAILABLE",
              "A selected check is not available in the active workspace and data generation. The selection was not expanded.",
            );
          return c;
        });
  if (checks.length > 500)
    throw new IntegrityError("EXPORT_LIMIT", "Select no more than 500 checks.");
  checks.forEach(verifyCheck);
  return checks;
}
export function replaceCheck(
  state: WorkspaceState,
  check: CheckRecord,
): WorkspaceState {
  if (
    check.workspace !== state.workspace ||
    check.generation !== state.generation
  )
    throw new IntegrityError(
      "WORKSPACE_CHANGED",
      "This check belongs to another workspace or data generation.",
    );
  const next = clone(state);
  const index = next.checks.findIndex((c) => c.id === check.id);
  if (index < 0) next.checks.unshift(check);
  else next.checks[index] = check;
  return next;
}
export function quarantineGeneration(
  state: WorkspaceState,
  current: number,
  clearedAt = state.profile.profile.recorded_at,
): WorkspaceState {
  const next = clone(state);
  for (const item of next.queue)
    if (
      item.generation !== current &&
      !(item.kind === "deletion" && item.state !== "synced")
    ) {
      item.state = "quarantined";
      item.error = "DATA_GENERATION_RETIRED";
    }
  for (const check of next.checks)
    if (check.generation !== current) {
      check.delivery = "quarantined";
      check.error = "DATA_GENERATION_RETIRED";
    }
  // Metadata and selections have no authority after a generation fence. Retain only
  // deletion receipts and export receipts explicitly belonging to the known generation.
  next.historyIndex = [];
  next.historyCursor = null;
  next.exportEntry = null;
  next.studies = [];
  next.rawRecordingStatuses = {};
  next.rawRecordingFences = {};
  next.deviceBindings = [];
  delete next.deviceBindingIntent;
  next.rawExportAuthorities = [];
  next.rawExportArtifactCursors = {};
  next.rawExportNextCursor = null;
  for (const raw of next.rawArtifacts ?? [])
    if (
      next.checks.some(
        (check) =>
          check.id === raw.session_id && check.delivery === "quarantined",
      )
    ) {
      raw.state = "quarantined";
      raw.error = "DATA_GENERATION_RETIRED";
    }
  next.profile = emptyProfile(clearedAt);
  if (current < 0) next.capabilities = null;
  next.jobs = next.jobs.filter(
    (job) => job.kind === "deletion" || job.data_generation === current,
  );
  return next;
}
