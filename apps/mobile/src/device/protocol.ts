import { canonicalJson, digest, knownKeys, parseBoundedJson, requireObject, requiredString, safeInteger, utf8 } from '../core/integrity';

export const DEVICE_SERVICE_UUID = '680cf5d8-5656-4f41-81c4-0f48d26f1000';
export const CAPABILITIES_UUID = '680cf5d8-5656-4f41-81c4-0f48d26f1001';
export const COMMAND_UUID = '680cf5d8-5656-4f41-81c4-0f48d26f1002';
export const EVENT_UUID = '680cf5d8-5656-4f41-81c4-0f48d26f1003';
export const PROTOCOL_VERSION = 1;
export const MAX_LOGICAL_BYTES = 8192;
export const HEADER_BYTES = 12;
export const REASSEMBLY_MS = 120_000;
export const ACK_TIMEOUT_MS = 2000;
export const MAX_RETRIES = 3;
export const CLOCK_POLICY_ID = 'synthetic_interval_v1';
export class DeviceError extends Error {
  constructor(public readonly code: string, message = code) { super(message); this.name = 'DeviceError'; }
}
export type DeviceChannel = 'ppg' | 'ecg' | 'saliva';
export type MessageType = 'hello' | 'clock_sync' | 'start_capture' | 'cancel_capture' | 'capture_chunk' | 'capture_complete' | 'status' | 'ack' | 'error';
export interface DeviceEnvelope {
  protocol_version: 1;
  message_id: string;
  device_id: string;
  boot_id: string;
  session_id: string;
  sequence: number;
  monotonic_ms: number;
  type: MessageType;
  payload: Record<string, unknown>;
}
export interface SyntheticCapabilities {
  protocol_version: 1;
  encodings: [1];
  max_logical_bytes: 8192;
  max_att_bytes: number;
  source: 'simulated';
  device_id: string;
  boot_id: string;
  hardware_revision: string;
  firmware_version: string;
  channels: DeviceChannel[];
  configuration_id: 'synthetic_bench_v1';
  calibration_status: 'not_applicable';
  timestamp_resolution_ms: number;
}
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export function uuid(value: unknown): string { const s = requiredString(value, 36); if (!UUID.test(s)) throw new DeviceError('INVALID_IDENTIFIER'); return s; }
function finite(value: unknown, min = 0): number { if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > Number.MAX_SAFE_INTEGER) throw new DeviceError('INVALID_NUMBER'); return value; }
export function capabilities(text: string): SyntheticCapabilities {
  const o = requireObject(parseBoundedJson(text, 1024));
  knownKeys(o, ['protocol_version', 'encodings', 'max_logical_bytes', 'max_att_bytes', 'source', 'device_id', 'boot_id', 'hardware_revision', 'firmware_version', 'channels', 'configuration_id', 'calibration_status', 'timestamp_resolution_ms']);
  if (o.protocol_version !== 1 || o.max_logical_bytes !== MAX_LOGICAL_BYTES || !Array.isArray(o.encodings) || o.encodings.length !== 1 || o.encodings[0] !== 1) throw new DeviceError('UNSUPPORTED_PROTOCOL');
  // An unprovisioned peripheral is accepted only if its own record says synthetic.
  // Physiological claims are rejected, never relabelled as simulated.
  if (o.source !== 'simulated' || o.configuration_id !== 'synthetic_bench_v1' || o.calibration_status !== 'not_applicable') throw new DeviceError('UNVERIFIED_HUMAN_HARDWARE');
  const maxAtt = safeInteger(o.max_att_bytes, 20); if (maxAtt > 512) throw new DeviceError('UNSUPPORTED_MTU');
  requiredString(o.device_id, 64); uuid(o.boot_id); requiredString(o.hardware_revision, 64); requiredString(o.firmware_version, 32);
  if (!Array.isArray(o.channels) || !o.channels.length || o.channels.length > 3 || new Set(o.channels).size !== o.channels.length || o.channels.some(v => !['ppg', 'ecg', 'saliva'].includes(String(v)))) throw new DeviceError('UNSUPPORTED_CHANNELS');
  const resolution = finite(o.timestamp_resolution_ms); if (resolution <= 0 || resolution > 1000) throw new DeviceError('UNSUPPORTED_CLOCK');
  return o as unknown as SyntheticCapabilities;
}
export function envelope(value: unknown): DeviceEnvelope {
  const o = requireObject(value);
  knownKeys(o, ['protocol_version', 'message_id', 'device_id', 'boot_id', 'session_id', 'sequence', 'monotonic_ms', 'type', 'payload']);
  if (o.protocol_version !== 1 || !['hello', 'clock_sync', 'start_capture', 'cancel_capture', 'capture_chunk', 'capture_complete', 'status', 'ack', 'error'].includes(String(o.type))) throw new DeviceError('UNSUPPORTED_MESSAGE');
  uuid(o.message_id); uuid(o.boot_id); uuid(o.session_id); requiredString(o.device_id, 64); safeInteger(o.sequence); finite(o.monotonic_ms); requireObject(o.payload);
  return o as unknown as DeviceEnvelope;
}

export function crc32(bytes: Uint8Array): number {
  let crc = 0xffffffff;
  for (const byte of bytes) { crc ^= byte; for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0); }
  return (crc ^ 0xffffffff) >>> 0;
}
export function decodeUtf8(bytes: Uint8Array): string {
  // Strict decoder, also available in Hermes where a global TextDecoder is not assumed.
  let output = '';
  for (let i = 0; i < bytes.length;) {
    const a = bytes[i++]!; let cp: number; let n: number; let min: number;
    if (a < 128) { output += String.fromCharCode(a); continue; }
    if (a >= 0xc2 && a <= 0xdf) { cp = a & 31; n = 1; min = 128; }
    else if (a >= 0xe0 && a <= 0xef) { cp = a & 15; n = 2; min = 2048; }
    else if (a >= 0xf0 && a <= 0xf4) { cp = a & 7; n = 3; min = 65536; }
    else throw new DeviceError('INVALID_UTF8');
    if (i + n > bytes.length) throw new DeviceError('INVALID_UTF8');
    for (let j = 0; j < n; j++) { const b = bytes[i++]!; if ((b & 0xc0) !== 0x80) throw new DeviceError('INVALID_UTF8'); cp = (cp << 6) | (b & 63); }
    if (cp < min || cp > 0x10ffff || cp >= 0xd800 && cp <= 0xdfff) throw new DeviceError('INVALID_UTF8');
    output += String.fromCodePoint(cp);
  }
  return output;
}
const BASE64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
export function toBase64(bytes: Uint8Array): string {
  let out = '';
  for (let i = 0; i < bytes.length; i += 3) { const n = (bytes[i]! << 16) | ((bytes[i + 1] ?? 0) << 8) | (bytes[i + 2] ?? 0); out += BASE64[n >>> 18]! + BASE64[n >>> 12 & 63]! + (i + 1 < bytes.length ? BASE64[n >>> 6 & 63]! : '=') + (i + 2 < bytes.length ? BASE64[n & 63]! : '='); }
  return out;
}
export function fromBase64(value: string, maxBytes = 512): Uint8Array {
  if (typeof value !== 'string' || value.length > 4 * Math.ceil(maxBytes / 3) || value.length % 4 || !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)) throw new DeviceError('INVALID_BASE64');
  const out: number[] = [];
  for (let i = 0; i < value.length; i += 4) { const a = BASE64.indexOf(value[i]!); const b = BASE64.indexOf(value[i + 1]!); const c = value[i + 2] === '=' ? 0 : BASE64.indexOf(value[i + 2]!); const d = value[i + 3] === '=' ? 0 : BASE64.indexOf(value[i + 3]!); const n = a << 18 | b << 12 | c << 6 | d; out.push(n >>> 16 & 255); if (value[i + 2] !== '=') out.push(n >>> 8 & 255); if (value[i + 3] !== '=') out.push(n & 255); }
  const bytes = Uint8Array.from(out); if (bytes.length > maxBytes || toBase64(bytes) !== value) throw new DeviceError('INVALID_BASE64'); return bytes;
}
function attCapacity(attBytes: number): number { if (!Number.isInteger(attBytes) || attBytes < 20 || attBytes > 512) throw new DeviceError('UNSUPPORTED_MTU'); return attBytes - HEADER_BYTES; }
export function fragmentMessage(message: DeviceEnvelope, transferId: number, attBytes = 20): Uint8Array[] {
  safeInteger(transferId); if (transferId > 0xffffffff) throw new DeviceError('TRANSFER_ID_EXHAUSTED'); envelope(message);
  const json = utf8(canonicalJson(message));
  if (json.length + 4 > MAX_LOGICAL_BYTES) throw new DeviceError('MESSAGE_TOO_LARGE');
  const stream = new Uint8Array(json.length + 4); stream.set(json); new DataView(stream.buffer).setUint32(json.length, crc32(json), true);
  const capacity = attCapacity(attBytes); const count = Math.ceil(stream.length / capacity);
  return Array.from({ length: count }, (_, index) => {
    const payload = stream.subarray(index * capacity, Math.min((index + 1) * capacity, stream.length));
    const frame = new Uint8Array(HEADER_BYTES + payload.length); const v = new DataView(frame.buffer);
    v.setUint8(0, 1); v.setUint8(1, 1); v.setUint32(2, transferId, true); v.setUint16(6, index, true); v.setUint16(8, count, true); v.setUint16(10, payload.length, true); frame.set(payload, HEADER_BYTES); return frame;
  });
}
interface Transfer { id: number; count: number; started: number; frames: Map<number, Uint8Array>; bytes: number }
function equal(a: Uint8Array, b: Uint8Array): boolean { return a.length === b.length && a.every((v, i) => v === b[i]); }
export class Reassembler {
  private current: Transfer | null = null;
  private completed: Transfer | null = null;
  private readonly capacity: number;
  constructor(private readonly attBytes = 20) { this.capacity = attCapacity(attBytes); }
  reset(): void { this.current = null; this.completed = null; }
  expire(now: number): void { if (this.current && now - this.current.started > REASSEMBLY_MS) { this.current = null; throw new DeviceError('REASSEMBLY_TIMEOUT'); } }
  push(frame: Uint8Array, now: number): DeviceEnvelope | null {
    try { return this.accept(frame, finite(now)); } catch (error) { this.current = null; throw error; }
  }
  private accept(frame: Uint8Array, now: number): DeviceEnvelope | null {
    this.expire(now);
    if (frame.length < HEADER_BYTES + 1 || frame.length > this.attBytes) throw new DeviceError('FRAGMENT_LENGTH');
    const v = new DataView(frame.buffer, frame.byteOffset, frame.byteLength);
    const id = v.getUint32(2, true), index = v.getUint16(6, true), count = v.getUint16(8, true), size = v.getUint16(10, true);
    if (v.getUint8(0) !== 1 || v.getUint8(1) !== 1) throw new DeviceError('FRAGMENT_VERSION');
    if (!count || count > 1024 || index >= count || size !== frame.length - HEADER_BYTES || size > this.capacity || (index !== count - 1 && size !== this.capacity) || (count - 1) * this.capacity + 1 > MAX_LOGICAL_BYTES) throw new DeviceError('FRAGMENT_BOUNDS');
    if (this.completed?.id === id) {
      const old = this.completed.frames.get(index);
      if (this.completed.count !== count || !old || !equal(old, frame.subarray(HEADER_BYTES))) throw new DeviceError('CONFLICTING_DUPLICATE_FRAGMENT');
      return null;
    }
    if (!this.current) this.current = { id, count, started: now, frames: new Map(), bytes: 0 };
    const t = this.current;
    if (t.id !== id) throw new DeviceError('CONCURRENT_TRANSFER');
    if (now < t.started || t.count !== count) throw new DeviceError('FRAGMENT_SEQUENCE');
    const payload = frame.slice(HEADER_BYTES), prior = t.frames.get(index);
    if (prior) { if (!equal(prior, payload)) throw new DeviceError('CONFLICTING_DUPLICATE_FRAGMENT'); return null; }
    t.frames.set(index, payload); t.bytes += size;
    if (t.bytes > MAX_LOGICAL_BYTES) throw new DeviceError('MESSAGE_TOO_LARGE');
    if (t.frames.size !== count) return null;
    if (t.bytes < 6) throw new DeviceError('MESSAGE_TOO_SHORT');
    const stream = new Uint8Array(t.bytes); let offset = 0;
    for (let i = 0; i < count; i++) { const p = t.frames.get(i)!; stream.set(p, offset); offset += p.length; }
    const content = stream.subarray(0, -4), expected = new DataView(stream.buffer).getUint32(stream.length - 4, true);
    if (crc32(content) !== expected) throw new DeviceError('CRC_MISMATCH');
    const result = envelope(parseBoundedJson(decodeUtf8(content), MAX_LOGICAL_BYTES - 4));
    this.completed = t; this.current = null; return result;
  }
}

/** Dedup journal lasts for this association. Exhaustion forces a new handshake; no replay-enabling eviction. */
export class MessageJournal {
  private readonly seen = new Map<string, { hash: string; disposition: string }>();
  private lastSequence = -1;
  constructor(private readonly limit = 256) {}
  accept(message: DeviceEnvelope, identity: {deviceId: string; bootId: string; sessionId: string}): 'new' | 'duplicate' {
    if (message.device_id !== identity.deviceId || message.boot_id !== identity.bootId || message.session_id !== identity.sessionId) throw new DeviceError('IDENTITY_MISMATCH');
    const hash = digest(message), prior = this.seen.get(message.message_id);
    if (prior) { if (prior.hash !== hash) throw new DeviceError('MESSAGE_ID_CONFLICT'); return 'duplicate'; }
    if (message.sequence <= this.lastSequence) throw new DeviceError('SEQUENCE_REPLAY');
    if (this.seen.size >= this.limit) throw new DeviceError('REPLAY_JOURNAL_FULL');
    this.seen.set(message.message_id, { hash, disposition: 'accepted' }); this.lastSequence = message.sequence; return 'new';
  }
}
export interface ClockExchange {
  phone_send_ms: number; device_receive_ms: number; device_send_ms: number; phone_receive_ms: number;
  phone_timestamp_resolution_ms: number; device_timestamp_resolution_ms: number;
  offset_lower_ms: number; offset_upper_ms: number; round_trip_ms: number;
}
export interface ClockEvidence {
  policy_id: typeof CLOCK_POLICY_ID; source: 'simulated'; boot_id: string; exchanges: ClockExchange[];
  selected_exchange: number; offset_ms: number; uncertainty_ms: number; calibrated: false;
}
export function clockExchange(phoneSend: number, deviceReceive: number, deviceSend: number, phoneReceive: number, phoneResolution: number, deviceResolution: number): ClockExchange {
  [phoneSend, deviceReceive, deviceSend, phoneReceive].forEach(v => finite(v));
  if (phoneReceive < phoneSend || deviceSend < deviceReceive || phoneResolution <= 0 || deviceResolution <= 0 || !Number.isFinite(phoneResolution + deviceResolution)) throw new DeviceError('CLOCK_DISCONTINUITY');
  const pad = phoneResolution + deviceResolution;
  const lo = deviceSend - phoneReceive - pad, hi = deviceReceive - phoneSend + pad;
  if (hi < lo) throw new DeviceError('CLOCK_INTERVAL_EMPTY');
  return { phone_send_ms: phoneSend, device_receive_ms: deviceReceive, device_send_ms: deviceSend, phone_receive_ms: phoneReceive,
    phone_timestamp_resolution_ms: phoneResolution, device_timestamp_resolution_ms: deviceResolution,
    offset_lower_ms: lo, offset_upper_ms: hi, round_trip_ms: phoneReceive - phoneSend };
}
export function selectClock(exchanges: ClockExchange[], bootId: string): ClockEvidence {
  if (exchanges.length !== 3) throw new DeviceError('CLOCK_EXCHANGE_COUNT'); uuid(bootId);
  let selected = 0;
  for (let i = 1; i < exchanges.length; i++) if (exchanges[i]!.offset_upper_ms - exchanges[i]!.offset_lower_ms < exchanges[selected]!.offset_upper_ms - exchanges[selected]!.offset_lower_ms) selected = i;
  const e = exchanges[selected]!;
  return { policy_id: CLOCK_POLICY_ID, source: 'simulated', boot_id: bootId, exchanges, selected_exchange: selected,
    offset_ms: (e.offset_lower_ms + e.offset_upper_ms) / 2, uncertainty_ms: (e.offset_upper_ms - e.offset_lower_ms) / 2, calibrated: false };
}
