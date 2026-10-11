import {
  assertBytes,
  IntegrityError,
  knownKeys,
  requireObject,
} from "./integrity";
import type { CaptureAttempt, Component, JsonObject } from "./types";

export function verifyRetainedNativeEye(
  value: unknown,
  projection: JsonObject,
  attempt: CaptureAttempt,
): void {
  const result = eyeTerminal(value);
  if (
    attempt.component !== "eyes" ||
    attempt.source !== "prototype_sensor" ||
    result.run_id !== attempt.record_id ||
    result.configuration_sha256 !== attempt.configuration_hash ||
    result.status !== projection.status ||
    result.started_at !== attempt.started_at ||
    result.ended_at !== attempt.ended_at ||
    projection.capture_config_id !== attempt.configuration_id ||
    projection.latency_ms !== null ||
    projection.relative_constriction !== null ||
    projection.source !== "prototype_sensor"
  )
    throw new IntegrityError(
      "NATIVE_EYE_EVIDENCE_INVALID",
      "Retained optical evidence differs from its original acquisition or claims unmeasured physical timing.",
    );
}
function eyeTerminal(value: unknown): Record<string, unknown> {
  assertBytes(value, 524_288);
  const result = requireObject(value),
    features = requireObject(result.features);
  knownKeys(result, [
    "schema_version",
    "implementation_version",
    "extractor_version",
    "run_id",
    "workspace_epoch",
    "authorization_id",
    "configuration_sha256",
    "status",
    "started_at",
    "ended_at",
    "clock_domain",
    "camera",
    "physical_onset_verified",
    "model_eligible",
    "stimulus",
    "frame_events",
    "features",
    "quality_flags",
  ]);
  if (
    result.schema_version !== "1.0.0" ||
    result.implementation_version !== "optical_roi_v1" ||
    result.extractor_version !== "otgd-dark-component-v1" ||
    !["valid", "invalid"].includes(String(result.status)) ||
    result.physical_onset_verified !== false ||
    result.model_eligible !== false ||
    !Array.isArray(result.frame_events) ||
    result.frame_events.length > 300 ||
    !Array.isArray(result.quality_flags) ||
    result.quality_flags.length > 64 ||
    result.quality_flags.some(
      (flag) => typeof flag !== "string" || flag.length > 128,
    ) ||
    !Number.isSafeInteger(features.valid_frames) ||
    Number(features.valid_frames) < 0 ||
    Number(features.valid_frames) > result.frame_events.length ||
    features.total_frames !== result.frame_events.length
  )
    throw new IntegrityError(
      "NATIVE_EYE_EVIDENCE_INVALID",
      "The bounded native optical ledger or its quality counts are unsupported.",
    );
  let previous = -Infinity;
  for (const [index, value] of result.frame_events.entries()) {
    const frame = requireObject(value),
      segmentation = requireObject(frame.segmentation);
    knownKeys(frame, [
      "sequence",
      "native_timestamp_ms",
      "dispatch_ms",
      "exposure_duration_ms",
      "sensitivity_iso",
      "autoexposure_state",
      "focus_state",
      "exposure_evidence",
      "roi_luma_sha256",
      "segmentation",
    ]);
    if (
      typeof frame.roi_luma_sha256 !== "string" ||
      !/^[a-f0-9]{64}$/.test(frame.roi_luma_sha256)
    )
      throw new IntegrityError(
        "NATIVE_EYE_EVIDENCE_INVALID",
        "Each sampled native ROI must preserve its exact luminance byte digest.",
      );
    if (
      (frame.sensitivity_iso !== null &&
        (typeof frame.sensitivity_iso !== "number" ||
          !Number.isFinite(frame.sensitivity_iso) ||
          frame.sensitivity_iso <= 0 ||
          frame.sensitivity_iso > 10_000_000)) ||
      ![
        "converged",
        "searching",
        "locked",
        "flash_required",
        "inactive",
        "adjusting_or_unknown",
        "stable_at_callback",
        "adjusting_at_callback",
        "unknown",
      ].includes(String(frame.autoexposure_state))
    )
      throw new IntegrityError(
        "NATIVE_EYE_EVIDENCE_INVALID",
        "Native ISO or automatic exposure observations are unsupported.",
      );
    if (
      frame.sequence !== index ||
      typeof frame.native_timestamp_ms !== "number" ||
      !Number.isFinite(frame.native_timestamp_ms) ||
      frame.native_timestamp_ms < 0 ||
      frame.native_timestamp_ms <= previous ||
      typeof frame.dispatch_ms !== "number" ||
      !Number.isFinite(frame.dispatch_ms) ||
      frame.dispatch_ms < frame.native_timestamp_ms ||
      !["valid", "invalid"].includes(String(segmentation.status))
    )
      throw new IntegrityError(
        "NATIVE_EYE_EVIDENCE_INVALID",
        "Optical frame sequence, native clock or segmentation state is inconsistent.",
      );
    previous = frame.native_timestamp_ms;
  }
  const stimulus = requireObject(result.stimulus);
  if (stimulus.physically_measured_at_ms !== null)
    throw new IntegrityError(
      "NATIVE_EYE_EVIDENCE_INVALID",
      "The optical adapter does not provide a physically measured illumination onset.",
    );
  return result;
}

/** Camera callbacks and ROI extraction are software evidence, never physical
 * illumination timing or a standalone clinical pupil measurement. */
export function projectNativeEye(
  value: unknown,
  identity: {
    runId: string;
    epoch: string;
    authorizationId: string;
    configurationId: string;
    configurationHash: string;
    material: JsonObject;
  },
): Component {
  const result = eyeTerminal(value),
    camera = requireObject(result.camera),
    features = requireObject(result.features);
  if (
    result.schema_version !== "1.0.0" ||
    result.implementation_version !== "optical_roi_v1" ||
    result.extractor_version !== "otgd-dark-component-v1" ||
    result.run_id !== identity.runId ||
    result.workspace_epoch !== identity.epoch ||
    result.authorization_id !== identity.authorizationId ||
    result.configuration_sha256 !== identity.configurationHash ||
    !["valid", "invalid"].includes(String(result.status)) ||
    result.physical_onset_verified !== false ||
    result.model_eligible !== false ||
    !Array.isArray(result.frame_events) ||
    result.frame_events.length > 300 ||
    !Array.isArray(result.quality_flags) ||
    result.quality_flags.length > 64 ||
    result.quality_flags.some((flag) => typeof flag !== "string") ||
    camera.camera_id !== identity.material.camera_id
  )
    throw new IntegrityError(
      "NATIVE_EYE_EVIDENCE_INVALID",
      "The bounded optical evidence differs from this actual authorized native run.",
    );
  const started = result.started_at,
    ended = result.ended_at;
  if (
    typeof started !== "string" ||
    typeof ended !== "string" ||
    !started.endsWith("Z") ||
    !ended.endsWith("Z") ||
    !Number.isFinite(Date.parse(started)) ||
    Date.parse(ended) < Date.parse(started) ||
    Date.parse(ended) - Date.parse(started) >
      Number(identity.material.duration_ms) + 2000
  )
    throw new IntegrityError(
      "NATIVE_EYE_CLOCK_INVALID",
      "The native optical timing is missing or outside its authorized duration.",
    );
  const valid = result.status === "valid",
    millimeters = identity.material.scale_basis === "millimeters";
  const number = (key: string) =>
    typeof features[key] === "number" && Number.isFinite(features[key])
      ? (features[key] as number)
      : null;
  const relative = number("relative_constriction"),
    diameter = number("baseline_diameter_mm");
  if (
    valid &&
    (typeof features.valid_frames !== "number" ||
      features.valid_frames < Number(identity.material.minimum_valid_frames) ||
      !result.frame_events.length ||
      Number(features.valid_frames) / result.frame_events.length <
        Number(identity.material.minimum_valid_frame_fraction) ||
      camera.width !== identity.material.capture_width ||
      camera.height !== identity.material.capture_height ||
      camera.output_rotation_degrees !==
        identity.material.expected_output_rotation_degrees)
  )
    throw new IntegrityError(
      "NATIVE_EYE_QUALITY_INVALID",
      "A valid optical result requires the approved frame-quality minimum.",
    );
  if (
    (relative !== null && (relative < 0 || relative > 1)) ||
    (!millimeters && diameter !== null) ||
    (millimeters && valid && (diameter === null || diameter <= 0))
  )
    throw new IntegrityError(
      "NATIVE_EYE_GEOMETRY_INVALID",
      "Optical scale or normalized response is inconsistent with its approved material.",
    );
  return {
    status: valid ? "valid" : "invalid",
    source: "prototype_sensor",
    started_at: started,
    ended_at: ended,
    quality_flags: [
      ...new Set([
        ...(result.quality_flags as string[]),
        "PHYSICAL_ONSET_UNMEASURED",
        "UNCALIBRATED_CAMERA_RESPONSE",
        "UNQUALIFIED_OPTICAL_EXTRACTOR",
        ...(millimeters ? [] : ["NO_MILLIMETER_GEOMETRY"]),
      ]),
    ],
    capture_config_id: identity.configurationId,
    camera_id: camera.camera_id as string,
    frame_rate_hz: valid ? Number(identity.material.frame_rate_hz) : null,
    scale_basis: millimeters ? "calibrated_mm" : "normalized",
    baseline_diameter_mm: valid && millimeters ? diameter : null,
    relative_constriction: null,
    latency_ms: null,
    raw_artifact_id: null,
  };
}
