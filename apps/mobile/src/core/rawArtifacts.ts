import {
  canonicalJson,
  clone,
  digest,
  digestBytes,
  IntegrityError,
  knownKeys,
  parseBoundedJson,
  requireObject,
  safeInteger,
  utf8,
} from "./integrity";
import { decodeUtf8, fromBase64, uuid } from "../device/protocol";
import {
  derSignature,
  signedSampleChunk,
  type ExpectedReaderCapture,
  type PhysicalCapabilities,
  type SignedSampleChunk,
} from "../device/physicalProtocol";
import type { RawKind, RawRecordingStatus } from "./rawRecordings";
import type { JsonObject } from "./types";

export interface RawPermission extends JsonObject {
  record: boolean;
  upload: boolean;
  receipt_id: string;
  policy_id: string;
  policy_version: string;
  policy_sha256: string;
  raw_notice_version: string;
  raw_notice_sha256: string;
}
export interface RawArtifact {
  local_id: string;
  study_id: string;
  session_id: string;
  attempt_id: string;
  artifact_kind: RawKind;
  format: string;
  media_type: "application/octet-stream" | "video/mp4";
  sha256: string;
  size_bytes: number;
  capture_started_at: string;
  consent_record_id: string;
  permission: RawPermission;
  state: "local" | "queued" | "uploaded" | "quarantined" | "deleted";
  server_artifact_id: string | null;
  created_at: string;
  retention_due_at: string;
  error: string | null;
}
export function verifyRawPermission(
  value: unknown,
  status: RawRecordingStatus,
  kind: RawKind,
  fences: RawKind[],
): RawPermission {
  const p = requireObject(value);
  knownKeys(p, [
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
    fences.includes(kind) ||
    p.record !== true ||
    typeof p.upload !== "boolean" ||
    !status.consent_record_id ||
    !status.receipt_id ||
    !status.policy ||
    Date.parse(status.policy.expires_at) <= Date.now() ||
    status.choices[kind].record !== true ||
    p.upload !== status.choices[kind].upload ||
    p.receipt_id !== status.receipt_id ||
    p.policy_id !== status.policy.policy_id ||
    p.policy_version !== status.policy.version ||
    p.policy_sha256 !== status.policy.sha256 ||
    p.raw_notice_version !== status.policy.raw_notice.version ||
    p.raw_notice_sha256 !== status.policy.raw_notice.sha256
  )
    throw new IntegrityError(
      "RAW_AUTHORITY_MISMATCH",
      "The fresh capture start does not authorize this exact optional recording choice and policy.",
    );
  return clone(p) as RawPermission;
}
/** Decode only bounded in-memory native output; no plaintext path is accepted. */
export function decodeRawRecording(
  value: unknown,
  kind: RawKind,
): {
  format: string;
  media_type: RawArtifact["media_type"];
  sha256: string;
  size_bytes: number;
  bytes: Uint8Array;
  evidence?: JsonObject;
} {
  const raw = requireObject(value);
  knownKeys(raw, ["format", "media_type", "sha256", "size_bytes", "chunks"]);
  const size = safeInteger(raw.size_bytes, 1),
    limit = (kind === "eye_video" ? 64 : 16) * 1024 * 1024;
  if (
    size > limit ||
    typeof raw.sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(raw.sha256) ||
    raw.media_type !== "application/octet-stream" ||
    !["OTGD-EYE-ROI-v1", "OTGD-ECG-SAMPLES-v1"].includes(String(raw.format)) ||
    (kind === "eye_video") !== (raw.format === "OTGD-EYE-ROI-v1") ||
    !Array.isArray(raw.chunks) ||
    !raw.chunks.length ||
    raw.chunks.length > 342
  )
    throw new IntegrityError(
      "RAW_RECORDING_INVALID",
      "The native recording format, size or kind is unsupported.",
    );
  const bytes = new Uint8Array(size);
  let offset = 0;
  try {
    for (const chunk of raw.chunks) {
      if (typeof chunk !== "string" || chunk.length > 262_144)
        throw new IntegrityError(
          "RAW_RECORDING_INVALID",
          "A native recording chunk exceeded its memory limit.",
        );
      const decoded = fromBase64(chunk, 196_608);
      if (offset + decoded.length > size)
        throw new IntegrityError(
          "RAW_RECORDING_INVALID",
          "Native recording chunks exceed the declared size.",
        );
      bytes.set(decoded, offset);
      offset += decoded.length;
      decoded.fill(0);
    }
    if (offset !== size || digestBytes(bytes) !== raw.sha256)
      throw new IntegrityError(
        "RAW_RECORDING_DIGEST",
        "The raw recording bytes failed their digest or size check.",
      );
    const magic = utf8(`${raw.format}\n`);
    if (!magic.every((byte, index) => bytes[index] === byte))
      throw new IntegrityError(
        "RAW_RECORDING_FORMAT",
        "The raw recording codec marker is missing.",
      );
    let evidence: JsonObject | undefined;
    if (kind === "eye_video") {
      const header = magic.length + 8;
      if (size < header)
        throw new IntegrityError(
          "RAW_RECORDING_FORMAT",
          "The eye ROI header is truncated.",
        );
      const view = new DataView(bytes.buffer),
        width = view.getUint16(magic.length, true),
        height = view.getUint16(magic.length + 2, true),
        count = view.getUint32(magic.length + 4, true);
      if (
        !width ||
        width > 128 ||
        !height ||
        height > 128 ||
        !count ||
        count > 300 ||
        size !== header + count * (12 + width * height)
      )
        throw new IntegrityError(
          "RAW_RECORDING_FORMAT",
          "The bounded ROI geometry and frame count differ from its bytes.",
        );
      let previous = -Infinity;
      for (let index = 0; index < count; index++) {
        const at = header + index * (12 + width * height),
          timestamp = view.getFloat64(at, true),
          sequence = view.getUint32(at + 8, true);
        if (
          !Number.isFinite(timestamp) ||
          timestamp < 0 ||
          timestamp <= previous ||
          sequence !== index
        )
          throw new IntegrityError(
            "RAW_RECORDING_FORMAT",
            "Raw ROI timing or sequence is inconsistent.",
          );
        previous = timestamp;
      }
    } else {
      if (size > 262_144)
        throw new IntegrityError(
          "RAW_RECORDING_FORMAT",
          "The signed ECG handoff exceeds its approved bounded codec.",
        );
      const text = decodeUtf8(bytes.subarray(magic.length)),
        body = requireObject(parseBoundedJson(text, 262_144));
      knownKeys(body, [
        "schema_version",
        "attestation_id",
        "envelope",
        "signature",
        "normalized_payload",
        "sample_chunks",
      ]);
      const envelope = requireObject(body.envelope),
        projection = requireObject(body.normalized_payload);
      if (
        body.schema_version !== "1.0.0" ||
        text !== canonicalJson(body) ||
        projection.source !== "prototype_sensor" ||
        projection.modality !== "ecg" ||
        envelope.payload_sha256 !== digest(projection) ||
        !Array.isArray(body.sample_chunks) ||
        !body.sample_chunks.length ||
        body.sample_chunks.length > 64
      )
        throw new IntegrityError(
          "RAW_RECORDING_FORMAT",
          "The ECG recording must preserve its exact canonical device-signed capture and measured chunks.",
        );
      uuid(body.attestation_id);
      derSignature(body.signature);
      // Structural/digest checks only: authenticity is independently verified
      // by the service against the approved reader key, never by a phone signature.
      const expected = {
          ...envelope,
          channel: "ecg",
        } as unknown as ExpectedReaderCapture,
        cap = { boot_id: envelope.boot_id } as PhysicalCapabilities;
      let previous: SignedSampleChunk | null = null,
        count = 0,
        sequence = -1;
      for (const value of body.sample_chunks) {
        const chunk = signedSampleChunk(value, expected, cap, previous),
          n = chunk.normalized_payload;
        count += n.samples.length;
        if (
          n.units !== "uV" ||
          count > 1024 ||
          n.first_sample_index + n.samples.length > 1024 ||
          chunk.envelope.sequence <= sequence ||
          chunk.envelope.sequence >= Number(envelope.sequence)
        )
          throw new IntegrityError(
            "RAW_RECORDING_FORMAT",
            "The signed ECG sample count, unit or signature sequence is outside its bounded capture.",
          );
        sequence = chunk.envelope.sequence;
        previous = chunk;
      }
      evidence = clone(body) as JsonObject;
    }
    return {
      format: String(raw.format),
      media_type: raw.media_type as RawArtifact["media_type"],
      sha256: raw.sha256,
      size_bytes: size,
      bytes,
      ...(evidence ? { evidence } : {}),
    };
  } catch (error) {
    bytes.fill(0);
    throw error;
  }
}
