import type { ReaderRawRecording } from "./physicalRaw";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import sessionSchema from "../contracts/session.schema.json";
import measurementSchema from "../contracts/measurement.schema.json";
import alcoholSchema from "../contracts/Alcohol.schema.json";
import {
  assertBytes,
  canonicalJson,
  clone,
  digest,
  knownKeys,
  parseBoundedJson,
  requireObject,
  requiredString,
  safeInteger,
} from "../core/integrity";
import type { JsonObject } from "../core/types";
import { DeviceError, fromBase64, MAX_LOGICAL_BYTES, uuid } from "./protocol";

export const PHYSICAL_PROTOCOL_ID = "otgd_signed_reader_v1";
export type PhysicalChannel = "ppg" | "ecg" | "saliva" | "alcohol";
export interface PhysicalCapabilities {
  protocol_version: 1;
  encodings: [1];
  max_logical_bytes: 8192;
  max_att_bytes: number;
  source: "prototype_sensor";
  protocol_id: typeof PHYSICAL_PROTOCOL_ID;
  device_id: string;
  boot_id: string;
  hardware_revision: string;
  firmware_version: string;
  key_id: string;
  channels: PhysicalChannel[];
  timestamp_resolution_ms: number;
}
export interface BindingTranscript {
  schema_version: "1.0.0";
  challenge_id: string;
  environment: "local" | "qa" | "prod" | "test";
  owner_ref: string;
  data_generation: number;
  device_id: string;
  key_id: string;
  nonce: string;
  expires_at: string;
  hardware_revision: string;
  firmware_version: string;
}
export interface ReaderBinding {
  binding_id: string;
  device_id: string;
  key_id: string;
  hardware_revision: string;
  firmware_version: string;
  state: "active";
  bound_at: string;
}
export interface ReaderScope {
  environment: BindingTranscript["environment"];
  owner_ref: string;
  data_generation: number;
}
export interface AuthorizedReaderOptions extends ReaderScope {
  authorization_id: string;
  binding_id: string;
  device_id: string;
  key_id: string;
  configuration_id: string;
  configuration_hash: string;
  max_duration_ms: number;
  capture_context_sha256: string;
  server_start: SignedStartToken;
}
export const GRANT_DOMAIN = "OTGD capture grant v1\u0000";
export interface ReaderRawPermission {
  record: true;
  upload: boolean;
  receipt_id: string;
  policy_id: string;
  policy_version: string;
  policy_sha256: string;
  raw_notice_version: string;
  raw_notice_sha256: string;
}
export interface SignedStartToken {
  grant: ReaderScope & {
    schema_version: "1.0.0";
    session_id: string;
    attempt_id: string;
    authorization_id: string;
    binding_id: string;
    device_id: string;
    device_key_id: string;
    boot_id: string;
    configuration_id: string;
    configuration_hash: string;
    configuration_submitted_sha256: string;
    configuration_version: string;
    capture_context_sha256: string;
    channel: "cardiac" | "ecg" | "saliva" | "alcohol";
    configuration_max_duration_ms: number;
    raw_recording_permission: ReaderRawPermission | null;
    participant_protocol_sha256: string | null;
    instruction_receipt_id: string | null;
    expires_at: string;
    issued_at: string;
    device_nonce: string;
    nonce: string;
  };
  signature: string;
  key_id: string;
  domain: typeof GRANT_DOMAIN;
}
export interface SignedCaptureEnvelope extends ReaderScope {
  schema_version: "1.0.0";
  session_id: string;
  attempt_id: string;
  authorization_id: string;
  binding_id: string;
  device_id: string;
  key_id: string;
  boot_id: string;
  sequence: number;
  configuration_hash: string;
  payload_sha256: string;
}
export interface SignedReaderCapture {
  attestation_id: string;
  envelope: SignedCaptureEnvelope;
  signature: string;
  normalized_payload: JsonObject;
  startedAt: string;
  endedAt: string;
  source: "prototype_sensor";
  modelEligible: false;
  deviceStartedMonotonicMs: number;
  deviceEndedMonotonicMs: number;
  sampleChunks: SignedSampleChunk[];
  rawRecording: ReaderRawRecording | null;
}
export interface SignedSampleChunk {
  envelope: SignedCaptureEnvelope;
  signature: string;
  normalized_payload: {
    schema_version: "1.0.0";
    channel: "ppg" | "ecg";
    first_sample_index: number;
    sample_rate_hz: number;
    units: "adc_counts" | "uV";
    contact: "good" | "poor" | "lost" | "unknown";
    dropped_before: number;
    acquisition_started_monotonic_us: number;
    acquisition_ended_monotonic_us: number;
    samples: { monotonic_us: number; value: number }[];
  };
}
export const BINDING_KEYS = [
  "schema_version",
  "challenge_id",
  "environment",
  "owner_ref",
  "data_generation",
  "device_id",
  "key_id",
  "nonce",
  "expires_at",
  "hardware_revision",
  "firmware_version",
] as const;
export const ENVELOPE_KEYS = [
  "schema_version",
  "environment",
  "owner_ref",
  "data_generation",
  "session_id",
  "attempt_id",
  "authorization_id",
  "binding_id",
  "device_id",
  "key_id",
  "boot_id",
  "sequence",
  "configuration_hash",
  "payload_sha256",
] as const;
const ajv = new Ajv2020({
  strict: false,
  allErrors: true,
  allowUnionTypes: true,
});
addFormats(ajv);
const cardiac = ajv.compile(sessionSchema.properties.cardiac),
  sample = ajv.compile(sessionSchema.properties.sample),
  measurement = ajv.compile(measurementSchema),
  alcohol = ajv.compile(alcoholSchema);
function exact(o: Record<string, unknown>, keys: readonly string[]): void {
  knownKeys(o, keys);
  if (Object.keys(o).length !== keys.length)
    throw new DeviceError("PHYSICAL_REQUIRED_FIELD");
}
function name(value: unknown, max = 128): string {
  const s = requiredString(value, max);
  if (!/^[A-Za-z0-9][A-Za-z0-9_.:-]*$/.test(s))
    throw new DeviceError("PHYSICAL_IDENTIFIER");
  return s;
}
function sha(value: unknown): string {
  const s = requiredString(value, 64);
  if (!/^[0-9a-f]{64}$/.test(s)) throw new DeviceError("PHYSICAL_DIGEST");
  return s;
}
function utc(value: unknown): string {
  const s = requiredString(value, 40);
  if (
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/.test(s) ||
    !Number.isFinite(Date.parse(s))
  )
    throw new DeviceError("PHYSICAL_TIMESTAMP");
  return s;
}
function scope(o: Record<string, unknown>): void {
  if (!["local", "qa", "prod", "test"].includes(String(o.environment)))
    throw new DeviceError("PHYSICAL_ENVIRONMENT");
  uuid(o.owner_ref);
  safeInteger(o.data_generation, 1);
}
/** Advertisement is a claim, never a key/binding approval or analytical qualification. */
export function physicalCapabilities(text: string): PhysicalCapabilities {
  const o = requireObject(parseBoundedJson(text, 1024));
  exact(o, [
    "protocol_version",
    "encodings",
    "max_logical_bytes",
    "max_att_bytes",
    "source",
    "protocol_id",
    "device_id",
    "boot_id",
    "hardware_revision",
    "firmware_version",
    "key_id",
    "channels",
    "timestamp_resolution_ms",
  ]);
  if (
    o.protocol_version !== 1 ||
    o.source !== "prototype_sensor" ||
    o.protocol_id !== PHYSICAL_PROTOCOL_ID ||
    o.max_logical_bytes !== MAX_LOGICAL_BYTES ||
    canonicalJson(o.encodings) !== "[1]"
  )
    throw new DeviceError("UNSUPPORTED_PHYSICAL_PROTOCOL");
  const att = safeInteger(o.max_att_bytes, 20);
  if (att > 512) throw new DeviceError("UNSUPPORTED_MTU");
  name(o.device_id);
  uuid(o.boot_id);
  name(o.hardware_revision, 64);
  name(o.firmware_version, 32);
  name(o.key_id);
  if (
    !Array.isArray(o.channels) ||
    !o.channels.length ||
    o.channels.length > 4 ||
    new Set(o.channels).size !== o.channels.length ||
    o.channels.some(
      (v) => !["ppg", "ecg", "saliva", "alcohol"].includes(String(v)),
    )
  )
    throw new DeviceError("UNSUPPORTED_CHANNELS");
  if (
    typeof o.timestamp_resolution_ms !== "number" ||
    !Number.isFinite(o.timestamp_resolution_ms) ||
    o.timestamp_resolution_ms <= 0 ||
    o.timestamp_resolution_ms > 1000
  )
    throw new DeviceError("UNSUPPORTED_CLOCK");
  return clone(o) as unknown as PhysicalCapabilities;
}
export function bindingTranscript(
  value: unknown,
  cap: PhysicalCapabilities,
): BindingTranscript {
  const o = requireObject(value);
  exact(o, BINDING_KEYS);
  scope(o);
  uuid(o.challenge_id);
  utc(o.expires_at);
  if (
    o.schema_version !== "1.0.0" ||
    typeof o.nonce !== "string" ||
    !/^[A-Za-z0-9_-]{43}$/.test(o.nonce)
  )
    throw new DeviceError("PHYSICAL_BINDING_TRANSCRIPT");
  // A canonical nonce carries exactly 32 bytes (no alternative pad bits).
  fromBase64(o.nonce.replace(/-/g, "+").replace(/_/g, "/") + "=", 32);
  for (const key of [
    "device_id",
    "key_id",
    "hardware_revision",
    "firmware_version",
  ] as const)
    if (o[key] !== cap[key]) throw new DeviceError("PHYSICAL_BINDING_IDENTITY");
  if (
    Date.parse(String(o.expires_at)) <= Date.now() ||
    Date.parse(String(o.expires_at)) > Date.now() + 301_000
  )
    throw new DeviceError("PHYSICAL_BINDING_EXPIRED");
  return clone(o) as unknown as BindingTranscript;
}
/** ASN.1 structural check only. Server verification against the approved key remains mandatory. */
export function derSignature(value: unknown): string {
  const s = requiredString(value, 100),
    b = fromBase64(s, 72);
  if (b.length < 8 || b[0] !== 0x30 || b[1] !== b.length - 2)
    throw new DeviceError("PHYSICAL_SIGNATURE_ENCODING");
  let offset = 2;
  for (let n = 0; n < 2; n++) {
    if (b[offset++] !== 0x02)
      throw new DeviceError("PHYSICAL_SIGNATURE_ENCODING");
    const length = b[offset++]!;
    if (
      length < 1 ||
      length > 33 ||
      offset + length > b.length ||
      b[offset]! & 0x80 ||
      (length > 1 && b[offset] === 0 && !(b[offset + 1]! & 0x80))
    )
      throw new DeviceError("PHYSICAL_SIGNATURE_ENCODING");
    if (!b.subarray(offset, offset + length).some((byte) => byte !== 0))
      throw new DeviceError("PHYSICAL_SIGNATURE_ENCODING");
    offset += length;
  }
  if (offset !== b.length) throw new DeviceError("PHYSICAL_SIGNATURE_ENCODING");
  return s;
}
export function authorizedReaderOptions(
  value: AuthorizedReaderOptions,
  cap: PhysicalCapabilities,
  binding: ReaderBinding,
  currentScope: ReaderScope,
): AuthorizedReaderOptions {
  const o = requireObject(value);
  exact(o, [
    "environment",
    "owner_ref",
    "data_generation",
    "authorization_id",
    "binding_id",
    "device_id",
    "key_id",
    "configuration_id",
    "configuration_hash",
    "max_duration_ms",
    "capture_context_sha256",
    "server_start",
  ]);
  scope(o);
  uuid(o.authorization_id);
  uuid(o.binding_id);
  name(o.configuration_id);
  sha(o.configuration_hash);
  sha(o.capture_context_sha256);
  const duration = safeInteger(o.max_duration_ms, 1);
  if (duration > 120_000) throw new DeviceError("PHYSICAL_DURATION");
  if (
    o.device_id !== cap.device_id ||
    o.key_id !== cap.key_id ||
    o.binding_id !== binding.binding_id ||
    o.environment !== currentScope.environment ||
    o.owner_ref !== currentScope.owner_ref ||
    o.data_generation !== currentScope.data_generation
  )
    throw new DeviceError("PHYSICAL_CAPTURE_SCOPE");
  return clone(value);
}
export function startToken(
  value: SignedStartToken,
  expected: ExpectedReaderCapture,
  cap: PhysicalCapabilities,
  deviceNonce: string,
): SignedStartToken {
  const token = requireObject(value);
  exact(token, ["grant", "signature", "key_id", "domain"]);
  name(token.key_id);
  derSignature(token.signature);
  if (token.domain !== GRANT_DOMAIN)
    throw new DeviceError("PHYSICAL_GRANT_DOMAIN");
  const g = requireObject(token.grant);
  exact(g, [
    "schema_version",
    "environment",
    "owner_ref",
    "data_generation",
    "session_id",
    "attempt_id",
    "authorization_id",
    "binding_id",
    "device_id",
    "device_key_id",
    "boot_id",
    "configuration_id",
    "configuration_hash",
    "configuration_submitted_sha256",
    "configuration_version",
    "capture_context_sha256",
    "channel",
    "configuration_max_duration_ms",
    "raw_recording_permission",
    "participant_protocol_sha256",
    "instruction_receipt_id",
    "expires_at",
    "issued_at",
    "device_nonce",
    "nonce",
  ]);
  scope(g);
  uuid(g.nonce);
  sha(g.configuration_submitted_sha256);
  name(g.configuration_version);
  if (
    g.schema_version !== "1.0.0" ||
    g.boot_id !== cap.boot_id ||
    g.device_nonce !== deviceNonce ||
    g.device_key_id !== cap.key_id
  )
    throw new DeviceError("PHYSICAL_GRANT_SCOPE");
  if (
    g.channel !== (expected.channel === "ppg" ? "cardiac" : expected.channel) ||
    g.configuration_max_duration_ms !== expected.max_duration_ms
  )
    throw new DeviceError("PHYSICAL_GRANT_SCOPE");
  for (const field of [
    "environment",
    "owner_ref",
    "data_generation",
    "session_id",
    "attempt_id",
    "authorization_id",
    "binding_id",
    "device_id",
    "configuration_id",
    "configuration_hash",
    "capture_context_sha256",
  ] as const)
    if (g[field] !== expected[field])
      throw new DeviceError("PHYSICAL_GRANT_SCOPE");
  sha(g.participant_protocol_sha256);
  uuid(g.instruction_receipt_id);
  if (g.raw_recording_permission !== null) {
    const permission = requireObject(g.raw_recording_permission);
    exact(permission, [
      "record",
      "upload",
      "receipt_id",
      "policy_id",
      "policy_version",
      "policy_sha256",
      "raw_notice_version",
      "raw_notice_sha256",
    ]);
    if (
      g.channel !== "ecg" ||
      permission.record !== true ||
      typeof permission.upload !== "boolean"
    )
      throw new DeviceError("PHYSICAL_RAW_PERMISSION");
    uuid(permission.receipt_id);
    for (const field of ["policy_id", "policy_version", "raw_notice_version"])
      requiredString(permission[field], 256);
    for (const field of ["policy_sha256", "raw_notice_sha256"])
      sha(permission[field]);
  }
  const issued = Date.parse(utc(g.issued_at)),
    expires = Date.parse(utc(g.expires_at));
  if (
    expires <= Date.now() ||
    expires - issued <= 0 ||
    expires - issued > 60_000 ||
    issued > Date.now() + 30_000
  )
    throw new DeviceError("PHYSICAL_GRANT_EXPIRED");
  return clone(value);
}
export function readerBinding(
  value: unknown,
  cap: PhysicalCapabilities,
): ReaderBinding {
  const o = requireObject(value);
  exact(o, [
    "binding_id",
    "device_id",
    "key_id",
    "hardware_revision",
    "firmware_version",
    "state",
    "bound_at",
  ]);
  uuid(o.binding_id);
  utc(o.bound_at);
  if (o.state !== "active") throw new DeviceError("PHYSICAL_BINDING_INACTIVE");
  for (const key of [
    "device_id",
    "key_id",
    "hardware_revision",
    "firmware_version",
  ] as const)
    if (o[key] !== cap[key]) throw new DeviceError("PHYSICAL_BINDING_IDENTITY");
  return clone(o) as unknown as ReaderBinding;
}
export type ExpectedReaderCapture = AuthorizedReaderOptions & {
  session_id: string;
  attempt_id: string;
  record_id: string;
  workspace_epoch: string;
  channel: PhysicalChannel;
};
function checkEnvelope(
  value: unknown,
  expected: ExpectedReaderCapture,
  cap: PhysicalCapabilities,
): Record<string, unknown> {
  const e = requireObject(value);
  exact(e, ENVELOPE_KEYS);
  scope(e);
  safeInteger(e.sequence);
  sha(e.configuration_hash);
  sha(e.payload_sha256);
  if (e.schema_version !== "1.0.0" || e.boot_id !== cap.boot_id)
    throw new DeviceError("PHYSICAL_CAPTURE_IDENTITY");
  for (const key of [
    "environment",
    "owner_ref",
    "data_generation",
    "session_id",
    "attempt_id",
    "authorization_id",
    "binding_id",
    "device_id",
    "key_id",
    "configuration_hash",
  ] as const)
    if (e[key] !== expected[key])
      throw new DeviceError("PHYSICAL_CAPTURE_SCOPE");
  return e;
}
/** Chunks remain provisional evidence; structural/digest checks do not verify P-256. */
export function signedSampleChunk(
  payload: unknown,
  expected: ExpectedReaderCapture,
  cap: PhysicalCapabilities,
  prior: SignedSampleChunk | null,
): SignedSampleChunk {
  const p = requireObject(payload);
  exact(p, ["envelope", "signature", "normalized_payload"]);
  const e = checkEnvelope(p.envelope, expected, cap),
    n = requireObject(p.normalized_payload);
  exact(n, [
    "schema_version",
    "channel",
    "first_sample_index",
    "sample_rate_hz",
    "units",
    "contact",
    "dropped_before",
    "acquisition_started_monotonic_us",
    "acquisition_ended_monotonic_us",
    "samples",
  ]);
  if (
    n.schema_version !== "1.0.0" ||
    !["ppg", "ecg"].includes(expected.channel) ||
    n.channel !== expected.channel ||
    !["adc_counts", "uV"].includes(String(n.units)) ||
    !["good", "poor", "lost", "unknown"].includes(String(n.contact))
  )
    throw new DeviceError("PHYSICAL_SAMPLE_METADATA");
  const index = safeInteger(n.first_sample_index),
    dropped = safeInteger(n.dropped_before),
    rate = safeInteger(n.sample_rate_hz, 1);
  if (
    rate > 1000 ||
    index > 120_000 ||
    dropped > 120_000 ||
    !Array.isArray(n.samples) ||
    !n.samples.length ||
    n.samples.length > 64
  )
    throw new DeviceError("PHYSICAL_SAMPLE_BOUNDS");
  const previous = prior?.normalized_payload;
  if (
    index !==
      (previous ? previous.first_sample_index + previous.samples.length : 0) +
        dropped ||
    (previous &&
      (previous.sample_rate_hz !== rate || previous.units !== n.units))
  )
    throw new DeviceError("PHYSICAL_SAMPLE_SEQUENCE");
  const acquisitionStart = safeInteger(n.acquisition_started_monotonic_us),
    acquisitionEnd = safeInteger(n.acquisition_ended_monotonic_us);
  if (
    acquisitionEnd <= acquisitionStart ||
    acquisitionEnd - acquisitionStart > expected.max_duration_ms * 1000 ||
    (previous &&
      (previous.acquisition_started_monotonic_us !== acquisitionStart ||
        previous.acquisition_ended_monotonic_us !== acquisitionEnd))
  )
    throw new DeviceError("PHYSICAL_SAMPLE_CAPTURE_WINDOW");
  let monotonic = previous?.samples.at(-1)?.monotonic_us ?? -1;
  for (const item of n.samples) {
    const s = requireObject(item);
    exact(s, ["monotonic_us", "value"]);
    const at = safeInteger(s.monotonic_us);
    if (
      at < acquisitionStart ||
      at >= acquisitionEnd ||
      at <= monotonic ||
      typeof s.value !== "number" ||
      !Number.isSafeInteger(s.value) ||
      s.value < -2147483648 ||
      s.value > 2147483647
    )
      throw new DeviceError("PHYSICAL_SAMPLE_CLOCK");
    monotonic = at;
  }
  if (e.payload_sha256 !== digest(n))
    throw new DeviceError("PHYSICAL_PAYLOAD_DIGEST");
  return clone({
    envelope: e,
    signature: derSignature(p.signature),
    normalized_payload: n,
  }) as unknown as SignedSampleChunk;
}
/** A bounded derived/quality summary, not optical raw recording or a cadence claim. */
export function signedPpgEvidence(
  value: unknown,
  projection: Record<string, unknown>,
  expected: ExpectedReaderCapture,
): JsonObject {
  const e = requireObject(value);
  exact(e, [
    "schema_version",
    "adapter_id",
    "sdk_commit",
    "sdk_version",
    "algorithm_mode",
    "hub_firmware",
    "configured_sensor_rate_hz",
    "actual_sensor_cadence_hz",
    "host_poll_interval_ms",
    "sample_timestamp_source",
    "acquisition_started_monotonic_us",
    "acquisition_ended_monotonic_us",
    "observed_samples",
    "valid_samples",
    "invalid_samples",
    "missed_poll_intervals",
    "fifo_empty_polls",
    "fifo_backlog_peak",
    "sensor_dropped_samples",
    "last_observation",
  ]);
  if (
    e.schema_version !== "1.0.0" ||
    e.adapter_id !== "otgd_sparkfun_max32664_v1" ||
    e.sdk_commit !== "91575258e5e2c47f0f4b8ec97b651381671f4637" ||
    e.sdk_version !== "1.1" ||
    (e.algorithm_mode !== 1 && e.algorithm_mode !== 2) ||
    e.sample_timestamp_source !== "host_i2c_receive_unqualified_sensor_time" ||
    e.actual_sensor_cadence_hz !== null ||
    e.sensor_dropped_samples !== null ||
    expected.channel !== "ppg"
  )
    throw new DeviceError("PHYSICAL_PPG_PROVENANCE");
  if (
    !["valid", "invalid"].includes(String(projection.status)) ||
    !Array.isArray(projection.quality_flags) ||
    ![
      "SERVER_WALL_ANCHOR_UNQUALIFIED",
      "SPARKFUN_SENSOR_BPM_V1",
      "HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED",
    ].every(
      (flag) =>
        projection.quality_flags instanceof Array &&
        projection.quality_flags.includes(flag),
    )
  )
    throw new DeviceError("PHYSICAL_PPG_PROVENANCE");
  const bounded = (v: unknown, min: number, max: number): number => {
    const n = safeInteger(v, min);
    if (n > max) throw new DeviceError("PHYSICAL_PPG_BOUNDS");
    return n;
  };
  if (e.hub_firmware !== null) {
    const f = requireObject(e.hub_firmware);
    exact(f, ["major", "minor", "revision"]);
    for (const k of ["major", "minor", "revision"]) bounded(f[k], 0, 255);
  }
  if (e.configured_sensor_rate_hz !== null)
    bounded(e.configured_sensor_rate_hz, 50, 3200);
  bounded(e.host_poll_interval_ms, 50, 1000);
  const begin = safeInteger(e.acquisition_started_monotonic_us),
    end = safeInteger(e.acquisition_ended_monotonic_us),
    observed = bounded(e.observed_samples, 0, 120000),
    valid = bounded(e.valid_samples, 0, 120000),
    invalid = bounded(e.invalid_samples, 0, 120000);
  bounded(e.missed_poll_intervals, 0, 120000);
  bounded(e.fifo_empty_polls, 0, 120000);
  bounded(e.fifo_backlog_peak, 0, 255);
  if (
    end < begin ||
    end - begin > expected.max_duration_ms * 1000 ||
    observed !== valid + invalid ||
    (e.last_observation === null) !== (observed === 0)
  )
    throw new DeviceError("PHYSICAL_PPG_COUNTS");
  let last: Record<string, unknown> | null = null;
  if (e.last_observation !== null) {
    last = requireObject(e.last_observation);
    exact(last, [
      "sequence",
      "host_received_monotonic_us",
      "heart_rate_bpm",
      "confidence_percent",
      "finger_status",
      "extended_status",
    ]);
    const at = safeInteger(last.host_received_monotonic_us);
    if (safeInteger(last.sequence) !== observed - 1 || at < begin || at >= end)
      throw new DeviceError("PHYSICAL_PPG_SEQUENCE");
    bounded(last.heart_rate_bpm, 0, 65535);
    bounded(last.confidence_percent, 0, 255);
    bounded(last.finger_status, 0, 255);
    if (e.algorithm_mode === 1 && last.extended_status !== null)
      throw new DeviceError("PHYSICAL_PPG_MODE");
    if (e.algorithm_mode === 2) bounded(last.extended_status, -128, 127);
  }
  if (
    projection.status === "valid" &&
    (!last ||
      !valid ||
      invalid !== 0 ||
      e.missed_poll_intervals !== 0 ||
      e.hub_firmware === null ||
      e.configured_sensor_rate_hz === null ||
      last.finger_status !== 3 ||
      Number(last.confidence_percent) > 100 ||
      last.heart_rate_bpm !== projection.heart_rate_bpm ||
      projection.ecg_status !== "not_collected" ||
      projection.ecg_rmssd_ms !== null ||
      projection.sample_rate_hz !== null)
  )
    throw new DeviceError("PHYSICAL_PPG_QUALITY");
  if (projection.status === "invalid" && projection.heart_rate_bpm !== null)
    throw new DeviceError("PHYSICAL_PPG_QUALITY");
  return clone(e) as JsonObject;
}
export function signedReaderCapture(
  payload: unknown,
  expected: ExpectedReaderCapture,
  cap: PhysicalCapabilities,
): SignedReaderCapture {
  const p = requireObject(payload);
  exact(p, [
    "source",
    "protocol_id",
    "channel",
    "attempt_id",
    "capture_id",
    "workspace_epoch",
    "started_monotonic_ms",
    "ended_monotonic_ms",
    "attestation_id",
    "envelope",
    "signature",
    "normalized_payload",
  ]);
  if (
    p.source !== "prototype_sensor" ||
    p.protocol_id !== PHYSICAL_PROTOCOL_ID ||
    p.channel !== expected.channel ||
    p.attempt_id !== expected.attempt_id ||
    p.capture_id !== expected.record_id ||
    p.workspace_epoch !== expected.workspace_epoch
  )
    throw new DeviceError("PHYSICAL_CAPTURE_IDENTITY");
  uuid(p.attestation_id);
  const e = checkEnvelope(p.envelope, expected, cap);
  const normalized = requireObject(p.normalized_payload);
  assertBytes(normalized, 6000);
  if (e.payload_sha256 !== digest(normalized))
    throw new DeviceError("PHYSICAL_PAYLOAD_DIGEST");
  const signature = derSignature(p.signature),
    start = safeInteger(p.started_monotonic_ms),
    end = safeInteger(p.ended_monotonic_ms);
  if (end < start || end - start > expected.max_duration_ms)
    throw new DeviceError("PHYSICAL_CAPTURE_CLOCK");
  let startedAt: string, endedAt: string;
  if (expected.channel === "ppg" || expected.channel === "ecg") {
    let projection = normalized;
    if (Object.hasOwn(normalized, "ppg_evidence")) {
      exact(normalized, ["projection", "ppg_evidence"]);
      projection = requireObject(normalized.projection);
      signedPpgEvidence(normalized.ppg_evidence, projection, expected);
      const evidence = requireObject(normalized.ppg_evidence);
      if (
        Math.floor(Number(evidence.acquisition_started_monotonic_us) / 1000) <
          start ||
        Math.floor(Number(evidence.acquisition_ended_monotonic_us) / 1000) !==
          end
      )
        throw new DeviceError("PHYSICAL_PPG_CAPTURE_CLOCK");
    }
    if (
      !cardiac(projection) ||
      projection.source !== "prototype_sensor" ||
      projection.modality !== expected.channel ||
      projection.acquisition_config_id !== expected.configuration_id
    )
      throw new DeviceError("PHYSICAL_PROJECTION");
    startedAt = utc(projection.started_at);
    endedAt = utc(projection.ended_at);
  } else if (expected.channel === "saliva") {
    exact(normalized, ["sample", "saliva"]);
    const s = requireObject(normalized.sample);
    if (
      !sample(s) ||
      s.sample_id !== expected.record_id ||
      !Array.isArray(normalized.saliva) ||
      normalized.saliva.length > 3 ||
      normalized.saliva.some(
        (v) =>
          !measurement(v) ||
          requireObject(v).source !== "prototype_sensor" ||
          requireObject(v).sample_id !== expected.record_id,
      )
    )
      throw new DeviceError("PHYSICAL_PROJECTION");
    startedAt = utc(s.collected_at);
    endedAt = normalized.saliva.length
      ? utc(requireObject(normalized.saliva[0]).measured_at)
      : startedAt;
  } else {
    if (
      !alcohol(normalized) ||
      normalized.source !== "prototype_sensor" ||
      normalized.measurement_id !== expected.record_id ||
      normalized.session_id !== expected.session_id
    )
      throw new DeviceError("PHYSICAL_PROJECTION");
    startedAt = utc(normalized.collected_at);
    endedAt = utc(normalized.measured_at);
  }
  if (
    Date.parse(endedAt) < Date.parse(startedAt) ||
    Date.parse(endedAt) - Date.parse(startedAt) > expected.max_duration_ms
  )
    throw new DeviceError("PHYSICAL_CAPTURE_CLOCK");
  return clone({
    attestation_id: p.attestation_id,
    envelope: e,
    signature,
    normalized_payload: normalized,
    startedAt,
    endedAt,
    source: "prototype_sensor",
    modelEligible: false,
    deviceStartedMonotonicMs: start,
    deviceEndedMonotonicMs: end,
    sampleChunks: [],
    rawRecording: null,
  }) as unknown as SignedReaderCapture;
}
