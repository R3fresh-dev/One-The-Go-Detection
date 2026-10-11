import { digest, IntegrityError, requireObject } from "./integrity";
import type { CheckRecord, ResearchResult } from "./types";

const METHODS = {
  otgd_esp32_adc_v1: {
    extractor: "adc_peak_intervals_v1",
    flags: ["SERVER_WALL_ANCHOR_UNQUALIFIED", "ADC_PEAK_INTERVALS_V1"],
  },
  otgd_sparkfun_max32664_v1: {
    extractor: "sparkfun_sensor_bpm_v1",
    flags: [
      "SERVER_WALL_ANCHOR_UNQUALIFIED",
      "SPARKFUN_SENSOR_BPM_V1",
      "HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED",
    ],
  },
};
const fail = (): never => {
  throw new IntegrityError(
    "CARDIAC_AUTHORITY_INVALID",
    "The HR-only server interval authority differs from its immutable capture or conservative timing bounds.",
  );
};

/** Exact decimal wire arithmetic; conservative bounds must round outwards. */
function decimal(value: number): { n: bigint; scale: number } {
  if (!Number.isFinite(value)) return fail();
  const match = /^(-?)(\d+)(?:\.(\d+))?(?:e([+-]?\d+))?$/.exec(String(value))!;
  const scale = (match[3]?.length ?? 0) - Number(match[4] ?? 0),
    n = BigInt((match[1] ?? "") + match[2] + (match[3] ?? ""));
  return scale < 0 ? { n: n * 10n ** BigInt(-scale), scale: 0 } : { n, scale };
}
function sum(values: [number, number][]): { n: bigint; scale: number } {
  const parts = values.map(([value, multiple]) => ({
      ...decimal(value),
      multiple,
    })),
    scale = Math.max(...parts.map((p) => p.scale));
  return {
    n: parts.reduce(
      (total, p) =>
        total + p.n * 10n ** BigInt(scale - p.scale) * BigInt(p.multiple),
      0n,
    ),
    scale,
  };
}
function ceil(values: [number, number][]): number {
  const { n, scale } = sum(values),
    denominator = 10n ** BigInt(scale),
    value = n < 0 ? n / denominator : (n + denominator - 1n) / denominator;
  if (value > BigInt(Number.MAX_SAFE_INTEGER)) return fail();
  return Number(value);
}
function epoch(iso: string): number {
  const fraction = /\.(\d+)Z$/.exec(iso)?.[1] ?? "";
  return (
    Date.parse(iso.replace(/\.\d+Z$/, "Z")) / 1000 +
    (fraction ? Number("0." + fraction) : 0)
  );
}

/** This checks server-admitted evidence consistency, never independent clinical approval. */
export function verifyCardiacAuthority(
  result: ResearchResult,
  check: Pick<CheckRecord, "snapshot" | "context" | "manifest"> &
    Partial<Pick<CheckRecord, "attempts" | "generation">>,
): void {
  const execution = result.model_execution,
    authority = execution.authority_manifest;
  if (authority.cardiac_authority === undefined) return;
  const companion = requireObject(authority.cardiac_authority),
    policy = requireObject(companion.policy),
    model = requireObject(authority.model_manifest),
    current = requireObject(companion.current),
    baseline =
      companion.baseline === null ? null : requireObject(companion.baseline);
  if (
    digest(model.required_channels) !== digest(["cardiac_hr"]) ||
    policy.allow_baseline_delta !== (model.baseline_mode === "personalized") ||
    digest(policy) !== companion.policy_sha256 ||
    companion.calibration_registry_sha256 !==
      current.calibration_registry_sha256 ||
    current.policy_sha256 !== companion.policy_sha256 ||
    current.snapshot_sha256 !== result.input_sha256 ||
    current.session_id !== result.session_id ||
    current.account_ref !== check.snapshot.subject_ref ||
    (check.generation !== undefined &&
      current.data_generation !== check.generation) ||
    current.capture_context_sha256 !== execution.capture_context_sha256 ||
    current.evidence_manifest_sha256 !== execution.evidence_manifest_sha256 ||
    check.manifest?.selected.cardiac !== current.attempt_id ||
    (model.baseline_mode === "population") !== (baseline === null)
  )
    fail();
  const target = epoch(result.target_at),
    evaluated = epoch(result.evaluated_at);
  const validate = (item: Record<string, unknown>, original: boolean) => {
    const adapter = METHODS[item.adapter_id as keyof typeof METHODS];
    const issued = Number(item.issued_epoch),
      received = Number(item.received_epoch),
      origin = Number(item.target_epoch),
      error = Number(item.server_utc_error_ms);
    if (item.adapter_id === "otgd_sparkfun_max32664_v1") {
      const duration = item.signed_acquisition_duration_us,
        rate = item.maximum_monotonic_rate_error_ppm;
      if (
        typeof duration !== "number" ||
        !Number.isSafeInteger(duration) ||
        duration <= 0 ||
        duration > 60000000 ||
        typeof rate !== "number" ||
        !Number.isSafeInteger(rate) ||
        rate < 0 ||
        rate > 10000
      )
        fail();
      const elapsed = sum([
        [received, 1000000],
        [issued, -1000000],
        [error, 2000],
      ]);
      if (
        BigInt(duration as number) * 1000000n * 10n ** BigInt(elapsed.scale) >
        elapsed.n * BigInt(1000000 + Number(rate))
      )
        fail();
    } else if (
      item.signed_acquisition_duration_us !== null ||
      item.maximum_monotonic_rate_error_ppm !== null
    )
      fail();
    if (
      !adapter ||
      item.extractor_version !== adapter.extractor ||
      item.policy_sha256 !== companion.policy_sha256 ||
      !(origin <= issued && issued < received && received <= evaluated) ||
      item.interval_ms !==
        ceil([
          [received, 1000],
          [issued, -1000],
          [error, 2],
        ]) ||
      item.acquisition_bound_ms !==
        ceil([
          [received, 1000],
          [origin, -1000],
          [error, 2],
        ]) ||
      Number(item.interval_ms) >
        Math.min(
          Number(policy.max_interval_ms),
          Number(model.max_clock_uncertainty_ms),
        ) ||
      Number(item.acquisition_bound_ms) >
        Number(model.max_acquisition_span_ms) ||
      digest([...(item.preserved_quality_flags as string[])].sort()) !==
        digest([...adapter.flags].sort()) ||
      (original &&
        (origin !== target ||
          ceil([
            [evaluated, 1000],
            [issued, -1000],
            [error, 2],
          ]) > Number(model.max_delivery_delay_ms)))
    )
      fail();
  };
  validate(current, true);
  const cardiac = check.snapshot.cardiac;
  if (
    cardiac.status !== "valid" ||
    cardiac.source !== "prototype_sensor" ||
    cardiac.modality !== "ppg" ||
    cardiac.ecg_status !== "not_collected" ||
    cardiac.ecg_rmssd_ms !== null ||
    typeof cardiac.heart_rate_bpm !== "number" ||
    digest(cardiac.quality_flags) !== digest(current.preserved_quality_flags) ||
    !check.context.configuration_refs.some(
      (ref) =>
        ref.id === current.configuration_id &&
        ref.version === current.configuration_version &&
        ref.sha256 === current.configuration_sha256,
    ) ||
    !check.context.device_associations.some(
      (ref) =>
        ref.binding_id === current.binding_id &&
        ref.device_id === current.device_id &&
        ref.boot_id === current.boot_id,
    )
  )
    fail();
  if (check.attempts) {
    const selected = check.attempts.find(
      (a) => a.attempt_id === current.attempt_id,
    );
    if (
      !selected ||
      selected.component !== "cardiac" ||
      selected.status !== "valid" ||
      selected.source !== "prototype_sensor" ||
      selected.configuration_id !== current.configuration_id ||
      selected.configuration_hash !== current.configuration_sha256 ||
      !selected.attestation_refs.includes(String(current.attestation_id)) ||
      digest(selected.component_metadata.projection) !== digest(cardiac) ||
      digest(selected.quality_flags) !==
        digest(current.preserved_quality_flags) ||
      requireObject(selected.component_metadata.instruction_receipt)
        .configuration_submitted_sha256 !==
        current.configuration_submitted_sha256
    )
      fail();
    if (current.adapter_id === "otgd_sparkfun_max32664_v1") {
      const vendor = requireObject(selected!.component_metadata.ppg_evidence);
      if (
        Number(vendor.acquisition_ended_monotonic_us) -
          Number(vendor.acquisition_started_monotonic_us) !==
        current.signed_acquisition_duration_us
      )
        fail();
    }
  }
  if (baseline) {
    validate(baseline, false);
    const same = [
      "account_ref",
      "data_generation",
      "device_id",
      "key_id",
      "hardware_revision",
      "firmware_version",
      "adapter_id",
      "extractor_version",
      "configuration_id",
      "configuration_version",
      "configuration_sha256",
      "configuration_submitted_sha256",
      "calibration_registry_sha256",
      "calibration_scope_sha256",
      "qualification_registry_sha256",
      "device_registry_sha256",
      "policy_sha256",
      "server_utc_error_ms",
      "maximum_monotonic_rate_error_ppm",
    ];
    if (
      policy.allow_baseline_delta !== true ||
      baseline.snapshot_sha256 !== execution.baseline_sha256 ||
      same.some((key) => baseline[key] !== current[key]) ||
      sum([
        [Number(baseline.received_epoch), 1000],
        [Number(baseline.server_utc_error_ms), 1],
        [target, -1000],
        [Number(current.server_utc_error_ms), 1],
      ]).n >= 0n
    )
      fail();
  } else if (
    execution.feature_values_sha256 !== digest([cardiac.heart_rate_bpm])
  )
    fail();
}
