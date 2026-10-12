import {
  canonicalJson,
  clone,
  digestBytes,
  requireObject,
  utf8,
} from "../core/integrity";
import { DeviceError, toBase64 } from "./protocol";
import {
  signedSampleChunk,
  type ExpectedReaderCapture,
  type PhysicalCapabilities,
  type SignedReaderCapture,
} from "./physicalProtocol";

export const ECG_RECORDING_MAGIC = "OTGD-ECG-SAMPLES-v1\n";
export interface ReaderRawRecording {
  format: "OTGD-ECG-SAMPLES-v1";
  media_type: "application/octet-stream";
  sha256: string;
  size_bytes: number;
  chunks: string[];
}
/** Bounded immutable transport handoff. These checks do not replace server
 * verification of the reader signatures against the approved device key. */
export function readerRawRecording(
  capture: SignedReaderCapture,
  expected: ExpectedReaderCapture,
  cap: PhysicalCapabilities,
): ReaderRawRecording | null {
  if (expected.server_start.grant.raw_recording_permission === null)
    return null;
  if (
    expected.channel !== "ecg" ||
    expected.server_start.grant.raw_recording_permission.record !== true
  )
    throw new DeviceError("PHYSICAL_RAW_PERMISSION");
  if (!capture.sampleChunks.length) return null;
  if (capture.sampleChunks.length > 64)
    throw new DeviceError("PHYSICAL_RAW_BOUNDS");
  let previous: SignedReaderCapture["sampleChunks"][number] | null = null,
    sequence = -1,
    count = 0;
  for (const value of capture.sampleChunks) {
    const checked = signedSampleChunk(value, expected, cap, previous),
      n = checked.normalized_payload;
    count += n.samples.length;
    if (
      n.channel !== "ecg" ||
      n.units !== "uV" ||
      count > 1024 ||
      n.first_sample_index + n.samples.length > 1024 ||
      n.first_sample_index + n.samples.length >
        Math.ceil((n.sample_rate_hz * expected.max_duration_ms) / 1000) ||
      checked.envelope.sequence <= sequence ||
      checked.envelope.sequence >= capture.envelope.sequence
    )
      throw new DeviceError("PHYSICAL_RAW_BOUNDS");
    if (
      n.samples.some(
        (s) =>
          s.monotonic_us < capture.deviceStartedMonotonicMs * 1000 ||
          s.monotonic_us > capture.deviceEndedMonotonicMs * 1000,
      )
    )
      throw new DeviceError("PHYSICAL_SAMPLE_CAPTURE_WINDOW");
    sequence = checked.envelope.sequence;
    previous = checked;
  }
  const body = clone({
    schema_version: "1.0.0",
    attestation_id: capture.attestation_id,
    envelope: capture.envelope,
    signature: capture.signature,
    normalized_payload: requireObject(capture.normalized_payload),
    sample_chunks: capture.sampleChunks,
  });
  const bytes = utf8(ECG_RECORDING_MAGIC + canonicalJson(body));
  if (bytes.length > 256 * 1024) throw new DeviceError("PHYSICAL_RAW_BOUNDS");
  const chunks: string[] = [];
  for (let at = 0; at < bytes.length; at += 32 * 1024)
    chunks.push(toBase64(bytes.subarray(at, at + 32 * 1024)));
  return {
    format: "OTGD-ECG-SAMPLES-v1",
    media_type: "application/octet-stream",
    sha256: digestBytes(bytes),
    size_bytes: bytes.length,
    chunks,
  };
}
