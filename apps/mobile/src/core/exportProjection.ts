import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import sessionSchema from "../contracts/session.schema.json";
import measurementSchema from "../contracts/measurement.schema.json";
import alcoholSchema from "../contracts/Alcohol.schema.json";
import {
  assertBytes,
  assertPlainJson,
  IntegrityError,
  knownKeys,
  requireObject,
} from "./integrity";
import type { CaptureAttempt, JsonObject, Snapshot } from "./types";

const ajv = new Ajv2020({
  strict: false,
  allErrors: true,
  allowUnionTypes: true,
});
addFormats(ajv);
const sampleValidator = ajv.compile(sessionSchema.properties.sample),
  measurementValidator = ajv.compile(measurementSchema),
  alcoholValidator = ajv.compile(alcoholSchema),
  componentValidators = {
    eyes: ajv.compile(sessionSchema.properties.eyes),
    cardiac: ajv.compile(sessionSchema.properties.cardiac),
    task: ajv.compile(sessionSchema.properties.task),
  };
const common = [
  "projection",
  "armed_at",
  "fixture_id",
  "transport_evidence",
  "instruction_receipt",
];
const fields = {
  saliva: [
    "collector_id",
    "collector_lot",
    "cartridge_lot",
    "adequacy",
    "volume_ml",
    "dilution_factor",
    "collected_at",
    "analysis_at",
    "source_report_artifact_id",
    "correction_reason",
    "original_report",
    "laboratory_id",
    "lab_import_id",
    "collection_method_version",
    "collection_receipt_id",
    "collection_request_sha256",
    "saliva_volume_ml",
    "buffer_volume_ml",
    "dilution_definition",
    "container_id",
    "cartridge_expiry",
    "operator_ref",
    "collection_attempt_id",
    "analysis_attempt_id",
    "storage_handling_events",
  ],
  eyes: [
    "native_result",
    "camera_id",
    "geometry_id",
    "illumination_id",
    "scale_basis",
    "frame_timing",
    "segmentation_version",
    "capture_config_id",
  ],
  cardiac: [
    "modality",
    "sample_rate_hz",
    "gain",
    "scaling",
    "contact",
    "filter_version",
    "dropped_samples",
    "context",
    "acquisition_config_id",
    "ppg_evidence",
  ],
  task: [
    "native_result",
    "extractor_version",
    "timing_method",
    "contract_fixture",
  ],
  alcohol: ["measurement_id"],
};
const nested = new Set([
  "projection",
  "native_result",
  "original_report",
  "frame_timing",
  "storage_handling_events",
  "transport_evidence",
  "instruction_receipt",
  "ppg_evidence",
]);
const fail = (message: string): never => {
  throw new IntegrityError("EXPORT_PROJECTION_INVALID", message);
};
function instant(value: unknown): number {
  if (
    typeof value !== "string" ||
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value)
  )
    return fail("An evidence timestamp is unsupported.");
  const time = Date.parse(value);
  if (
    !Number.isFinite(time) ||
    new Date(time).toISOString().slice(0, 19) !== value.slice(0, 19)
  )
    return fail("An evidence timestamp is not a real UTC instant.");
  return time;
}
function boundedScalars(object: Record<string, unknown>): void {
  for (const value of Object.values(object))
    if (
      (typeof value === "object" && value !== null) ||
      (typeof value === "string" && value.length > 256)
    )
      fail("Unapproved nested or overlong component metadata is present.");
}
function limits(value: JsonObject, names: string[]): void {
  const values = names
    .map((key) => value[key])
    .filter((n): n is number => typeof n === "number");
  if (values.some((n, i) => i > 0 && n < values[i - 1]!))
    fail("Analytical limits are out of order.");
}
function measurement(
  reading: JsonObject,
  sample: JsonObject,
  source: string,
): void {
  if (!measurementValidator(reading))
    fail("A retained analyte projection has an unsupported schema.");
  if (
    reading.sample_id !== sample.sample_id ||
    reading.collected_at !== sample.collected_at ||
    reading.source !== source
  )
    fail("A retained analyte belongs to another specimen, time or source.");
  if (
    reading.measured_at !== null &&
    instant(reading.measured_at) < instant(reading.collected_at)
  )
    fail("A retained analytical time precedes collection.");
  const analyticalLimits = reading.limits as JsonObject;
  limits(analyticalLimits, ["lod_ng_ml", "loq_ng_ml", "upper_ng_ml"]);
  if (reading.qualifier === "quantified") {
    const amount = reading.value_ng_ml as number,
      original = reading.original_report as JsonObject,
      converted =
        original.unit === "pg/mL"
          ? Number(original.value) / 1000
          : original.value;
    if (
      typeof original.value !== "number" ||
      typeof converted !== "number" ||
      Math.abs(converted - amount) >
        Math.max(
          1e-12,
          1e-9 * Math.max(Math.abs(converted), Math.abs(amount)),
        ) ||
      amount < Number(analyticalLimits.loq_ng_ml) ||
      amount > Number(analyticalLimits.upper_ng_ml)
    )
      fail(
        "A retained analyte changes its original units or quantitative range.",
      );
  }
}

/** Validates every retained projection, including superseded attempts. Never rewrites evidence. */
export function verifyAttemptProjection(
  attempt: CaptureAttempt,
  snapshot: Snapshot,
): JsonObject {
  assertPlainJson(attempt);
  assertBytes(attempt, 524_288);
  if (
    !Object.hasOwn(fields, attempt.component) ||
    attempt.session_id !== snapshot.session_id ||
    attempt.status === "started"
  )
    fail("A retained attempt is unfinished or belongs to another check.");
  const metadata = requireObject(attempt.component_metadata);
  knownKeys(metadata, [...common, ...fields[attempt.component]]);
  if (
    (Object.hasOwn(metadata, "fixture_id") ||
      Object.hasOwn(metadata, "transport_evidence")) &&
    attempt.source !== "simulated"
  )
    fail("Synthetic fixture metadata cannot claim a human source.");
  if (
    metadata.fixture_id !== undefined &&
    metadata.fixture_id !== null &&
    (typeof metadata.fixture_id !== "string" ||
      metadata.fixture_id.length < 1 ||
      metadata.fixture_id.length > 128)
  )
    fail("Synthetic fixture identity is invalid.");
  if (metadata.armed_at !== undefined && metadata.armed_at !== null)
    instant(metadata.armed_at);
  for (const [key, value] of Object.entries(metadata))
    if (!nested.has(key)) boundedScalars({ [key]: value });
  for (const field of [
    "volume_ml",
    "saliva_volume_ml",
    "buffer_volume_ml",
    "dilution_factor",
  ])
    if (
      metadata[field] !== undefined &&
      metadata[field] !== null &&
      (typeof metadata[field] !== "number" || Number(metadata[field]) < 0)
    )
      fail(
        "Retained collection metadata contains an invalid volume or dilution value.",
      );
  if (metadata.original_report !== undefined) {
    const original = requireObject(metadata.original_report);
    knownKeys(original, ["value", "unit", "qualifier", "report_id"]);
    boundedScalars(original);
    if (
      original.value !== undefined &&
      original.value !== null &&
      (typeof original.value !== "number" || original.value < 0)
    )
      fail("The retained original report value is invalid.");
  }
  if (metadata.frame_timing !== undefined) {
    const frame = requireObject(metadata.frame_timing);
    knownKeys(frame, [
      "first_timestamp_ms",
      "last_timestamp_ms",
      "frame_count",
      "dropped_frames",
      "maximum_gap_ms",
    ]);
    for (const [key, value] of Object.entries(frame))
      if (
        value !== null &&
        (typeof value !== "number" ||
          value < 0 ||
          (["frame_count", "dropped_frames"].includes(key) &&
            !Number.isSafeInteger(value)))
      )
        fail("Frame timing is not bounded numeric metadata.");
  }
  if (metadata.storage_handling_events !== undefined) {
    if (
      !Array.isArray(metadata.storage_handling_events) ||
      metadata.storage_handling_events.length > 64
    )
      fail("Retained sample handling exceeds the supported event bound.");
    for (const item of metadata.storage_handling_events as unknown[]) {
      const event = requireObject(item);
      knownKeys(event, [
        "event",
        "occurred_at",
        "operator_ref",
        "temperature_c",
        "duration_min",
        "configuration_ref",
      ]);
      boundedScalars(event);
      if (event.occurred_at !== undefined && event.occurred_at !== null)
        instant(event.occurred_at);
    }
  }
  if (metadata.native_result !== undefined && metadata.native_result !== null)
    requireObject(metadata.native_result);
  if (
    metadata.transport_evidence !== undefined &&
    metadata.transport_evidence !== null
  )
    requireObject(metadata.transport_evidence);
  if (metadata.contract_fixture !== undefined) {
    const native = requireObject(metadata.native_result),
      timing = requireObject(native.timing);
    if (metadata.contract_fixture !== true || timing.simulator !== true)
      fail(
        "A host contract fixture must preserve its explicit simulator provenance.",
      );
  }
  const projection = requireObject(metadata.projection) as JsonObject,
    expectedStatus = attempt.status === "canceled" ? "invalid" : attempt.status;
  if (
    attempt.started_at !== null &&
    attempt.ended_at !== null &&
    instant(attempt.ended_at) < instant(attempt.started_at)
  )
    fail("A retained attempt ends before it starts.");
  if (
    attempt.status === "not_collected" &&
    (attempt.started_at !== null || attempt.ended_at !== null)
  )
    fail("An uncollected attempt has fabricated acquisition times.");
  if (attempt.component === "saliva") {
    knownKeys(projection, ["sample", "saliva"]);
    const sample = requireObject(projection.sample) as JsonObject;
    if (
      !sampleValidator(sample) ||
      !Array.isArray(projection.saliva) ||
      projection.saliva.length > 3 ||
      sample.sample_id !== attempt.record_id ||
      sample.status !== expectedStatus
    )
      fail(
        "The retained saliva projection does not match its sample identity or status.",
      );
    const readings = projection.saliva as unknown[];
    if (sample.collected_at === null && readings.length)
      fail("Uncollected saliva cannot contain analytical measurements.");
    const ids = new Set<string>(),
      analytes = new Set<string>();
    for (const value of readings) {
      const m = requireObject(value) as JsonObject;
      measurement(m, sample, attempt.source);
      if (ids.has(String(m.measurement_id)) || analytes.has(String(m.analyte)))
        fail(
          "Retained saliva has duplicate analytical identities or analytes.",
        );
      ids.add(String(m.measurement_id));
      analytes.add(String(m.analyte));
    }
  } else if (attempt.component === "alcohol") {
    if (
      !alcoholValidator(projection) ||
      projection.session_id !== snapshot.session_id ||
      projection.measurement_id !== attempt.record_id ||
      projection.source !== attempt.source
    )
      fail("Retained alcohol evidence has an unsupported shape or identity.");
    const status =
      projection.qualifier === "not_measured"
        ? "not_collected"
        : projection.qualifier === "invalid"
          ? "invalid"
          : "valid";
    if (status !== expectedStatus)
      fail("Alcohol qualifier and attempt status disagree.");
    const analyticalLimits = projection.limits as JsonObject;
    limits(analyticalLimits, ["lod_mg_l", "loq_mg_l", "upper_mg_l"]);
    if (projection.qualifier === "quantified") {
      if (
        typeof projection.value_mg_l !== "number" ||
        projection.collected_at === null ||
        projection.measured_at === null ||
        typeof analyticalLimits.loq_mg_l !== "number" ||
        typeof analyticalLimits.upper_mg_l !== "number" ||
        projection.value_mg_l < analyticalLimits.loq_mg_l ||
        projection.value_mg_l > analyticalLimits.upper_mg_l
      )
        fail("Quantified alcohol lacks timing or an in-range measurement.");
    } else if (projection.value_mg_l !== null)
      fail("Censored alcohol cannot be replaced with a numeric concentration.");
    if (
      projection.qualifier === "not_measured" &&
      projection.measured_at !== null
    )
      fail("Unmeasured alcohol cannot have an analysis time.");
    if (
      projection.collected_at !== null &&
      projection.measured_at !== null &&
      instant(projection.measured_at) < instant(projection.collected_at)
    )
      fail("Alcohol analysis precedes collection.");
    if (
      projection.source === "validated_sensor" &&
      [
        "calibration_id",
        "method_id",
        "device_id",
        "boot_id",
        "configuration_hash",
      ].some((key) => !projection[key])
    )
      fail("Qualified alcohol is missing acquisition provenance.");
  } else {
    if (
      !componentValidators[attempt.component](projection) ||
      projection.source !== attempt.source ||
      projection.status !== expectedStatus ||
      projection.started_at !== attempt.started_at ||
      projection.ended_at !== attempt.ended_at
    )
      fail(
        "Retained component source, quality or timing differs from its attempt.",
      );
    if (attempt.component === "cardiac") {
      if (
        (metadata.modality !== undefined &&
          metadata.modality !== projection.modality) ||
        !["ppg", "ecg", "simulated"].includes(String(projection.modality))
      )
        fail("Retained cardiac modality changed.");
      if (
        projection.modality === "ppg" &&
        (projection.ecg_status !== "not_collected" ||
          projection.ecg_rmssd_ms !== null)
      )
        fail("PPG cannot supply ECG features.");
      if (
        projection.status !== "valid" &&
        (projection.heart_rate_bpm !== null || projection.ecg_rmssd_ms !== null)
      )
        fail(
          "An invalid or absent cardiac attempt cannot retain physiological features.",
        );
    }
    if (
      attempt.component === "eyes" &&
      projection.status !== "valid" &&
      ["baseline_diameter_mm", "relative_constriction", "latency_ms"].some(
        (key) => projection[key] !== null,
      )
    )
      fail("An invalid or absent eye attempt cannot retain pupil features.");
    if (attempt.component === "task") {
      if (
        projection.task_id !== attempt.record_id ||
        (attempt.configuration_hash !== null &&
          projection.config_sha256 !== attempt.configuration_hash)
      )
        fail("The task projection changes its run or configuration identity.");
      if (
        projection.status !== "valid" &&
        Object.values(requireObject(projection.features)).some(
          (value) => value !== null,
        )
      )
        fail("An invalid task cannot retain aggregate reaction features.");
      if (
        attempt.source === "prototype_sensor" &&
        attempt.status === "valid" &&
        (!metadata.native_result ||
          !attempt.quality_flags.includes("uncalibrated"))
      )
        fail(
          "A valid prototype task requires full native evidence and explicit uncalibrated provenance.",
        );
    }
  }
  return projection;
}
