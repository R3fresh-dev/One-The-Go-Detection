import { canonicalJson, knownKeys, requiredString, safeInteger } from '../core/integrity';
import { capabilities, DeviceError, fragmentMessage, fromBase64, MessageJournal, Reassembler, toBase64, uuid } from './protocol';
import type { DeviceChannel, DeviceEnvelope, SyntheticCapabilities } from './protocol';
import type { DeviceTransport, SyntheticEcgValues, SyntheticPpgValues, SyntheticSalivaValues, TransportEvent } from './types';

export function syntheticValues(channel: DeviceChannel): SyntheticPpgValues | SyntheticEcgValues | SyntheticSalivaValues {
  if (channel === 'ppg') return { heart_rate_bpm: 72, duration_seconds: 3, method: 'ppg' };
  if (channel === 'ecg') return { heart_rate_bpm: 72, duration_seconds: 4, method: 'ecg', sample_rate_hz: 50, lead_count: 1, units: 'arbitrary_counts',
    samples: Array.from({ length: 200 }, (_, i) => { const p = i % 42; return p === 10 ? 800 : p === 11 ? -250 : p >= 20 && p <= 25 ? (p <= 22 ? p - 19 : 26 - p) * 25 : p >= 4 && p <= 6 ? 30 : 0; }) };
  return { specimen: 'oral_fluid', assay_id: 'synthetic_assay_v1', analytes: [
    { analyte: 'delta9_thc', qualifier: 'quantified', value: 12, unit: 'ng/mL', lod: 1, loq: 2, uloq: 100 },
    { analyte: '11_hydroxy_thc', qualifier: 'not_detected', value: null, unit: 'ng/mL', lod: 1, loq: 2, uloq: 100 },
    { analyte: 'thc_cooh', qualifier: 'not_detected', value: null, unit: 'ng/mL', lod: 1, loq: 2, uloq: 100 },
  ] };
}

/** Software-only peripheral. It deliberately passes through the same framing and validation path. */
export class LocalSimulatorTransport implements DeviceTransport {
  readonly kind = 'local_simulator' as const;
  readonly available = true;
  private listeners = new Set<(event: TransportEvent) => void>();
  private receiver = new Reassembler(20);
  private journal = new MessageJournal(64);
  private priorResponses = new Map<string, DeviceEnvelope[]>();
  private connected = false;
  private sequence = 0;
  private transfer = 0;
  private captureTimer: ReturnType<typeof setTimeout> | null = null;
  private active: { session: string; attempt: string; capture: string; epoch: string } | null = null;
  private capabilitiesRecord: SyntheticCapabilities;
  constructor(private readonly idFactory: () => string) {
    this.capabilitiesRecord = { protocol_version: 1, encodings: [1], max_logical_bytes: 8192, max_att_bytes: 20, source: 'simulated', device_id: 'SIM-LOCAL-01', boot_id: uuid(idFactory()), hardware_revision: 'software_simulator_1', firmware_version: '1.0.0', channels: ['ppg', 'ecg', 'saliva'], configuration_id: 'synthetic_bench_v1', calibration_status: 'not_applicable', timestamp_resolution_ms: 1 };
    capabilities(canonicalJson(this.capabilitiesRecord));
  }
  now(): number { return performance.now(); }
  subscribe(listener: (event: TransportEvent) => void): () => void { this.listeners.add(listener); return () => this.listeners.delete(listener); }
  private emit(event: TransportEvent): void { this.listeners.forEach(listener => listener(event)); }
  async scan(): Promise<void> { this.emit({ kind: 'discovered', peripheralId: 'local-simulator', alias: 'Local synthetic simulator', rssi: 0 }); }
  async stopScan(): Promise<void> {}
  async connect(peripheralId: string): Promise<{peripheralId: string; mtu: number; capabilities: string}> {
    if (peripheralId !== 'local-simulator') throw new DeviceError('UNKNOWN_PERIPHERAL');
    this.connected = true; this.receiver.reset(); this.journal = new MessageJournal(64); this.priorResponses.clear();
    this.sequence = 0; this.transfer = 0; this.capabilitiesRecord.boot_id = uuid(this.idFactory());
    return { peripheralId, mtu: 23, capabilities: canonicalJson(this.capabilitiesRecord) };
  }
  async disconnect(): Promise<void> { this.connected = false; if (this.captureTimer) clearTimeout(this.captureTimer); this.captureTimer = null; this.active = null; this.receiver.reset(); this.emit({ kind: 'disconnected', peripheralId: 'local-simulator', reason: 'DISCONNECTED' }); }
  private send(type: DeviceEnvelope['type'], session: string, payload: Record<string, unknown>): DeviceEnvelope {
    const message: DeviceEnvelope = { protocol_version: 1, message_id: uuid(this.idFactory()), device_id: this.capabilitiesRecord.device_id, boot_id: this.capabilitiesRecord.boot_id, session_id: session, sequence: this.sequence++, monotonic_ms: this.now(), type, payload };
    this.retransmit(message); return message;
  }
  private retransmit(message: DeviceEnvelope): void {
    if (!this.connected) return;
    for (const frame of fragmentMessage(message, this.transfer++, 20)) this.emit({ kind: 'packet', peripheralId: 'local-simulator', base64: toBase64(frame), receivedAtMonotonicMs: this.now() });
  }
  async write(base64: string): Promise<void> {
    if (!this.connected) throw new DeviceError('NOT_CONNECTED');
    const message = this.receiver.push(fromBase64(base64, 20), this.now()); if (!message) return;
    const result = this.journal.accept(message, { deviceId: this.capabilitiesRecord.device_id, bootId: this.capabilitiesRecord.boot_id, sessionId: message.session_id });
    if (result === 'duplicate') { this.priorResponses.get(message.message_id)?.forEach(m => this.retransmit(m)); return; }
    if (message.type === 'ack') return;
    const p = message.payload;
    const deadline = safeInteger(p.deadline_after_ms, 1); if (deadline > 120_000) throw new DeviceError('COMMAND_DEADLINE');
    const responses: DeviceEnvelope[] = [];
    const ack = () => responses.push(this.send('ack', message.session_id, { ack_message_id: message.message_id, status: 'accepted' }));
    if (message.type === 'hello') {
      knownKeys(p, ['deadline_after_ms']); ack();
      responses.push(this.send('hello', message.session_id, { request_message_id: message.message_id, source: 'simulated', configuration_id: 'synthetic_bench_v1' }));
    } else if (message.type === 'clock_sync') {
      knownKeys(p, ['deadline_after_ms', 'phone_send_ms']); if (typeof p.phone_send_ms !== 'number' || !Number.isFinite(p.phone_send_ms)) throw new DeviceError('CLOCK_REQUEST');
      const receive = this.now(); ack();
      responses.push(this.send('clock_sync', message.session_id, { request_message_id: message.message_id, phone_send_ms: p.phone_send_ms, device_receive_ms: receive, device_send_ms: this.now() }));
    } else if (message.type === 'start_capture') {
      knownKeys(p, ['deadline_after_ms', 'deadline_device_ms', 'attempt_id', 'capture_id', 'workspace_epoch', 'channel', 'source']);
      const attempt = uuid(p.attempt_id), capture = uuid(p.capture_id), epoch = requiredString(p.workspace_epoch, 128);
      if (!['ppg', 'ecg', 'saliva'].includes(String(p.channel)) || p.source !== 'simulated' || this.active || typeof p.deadline_device_ms !== 'number' || p.deadline_device_ms < this.now() || p.deadline_device_ms > this.now() + 120_000) throw new DeviceError('CAPTURE_REFUSED');
      const channel = p.channel as DeviceChannel, start = this.now(); this.active = { session: message.session_id, attempt, capture, epoch }; ack();
      const duration = channel === 'ppg' ? 3000 : channel === 'ecg' ? 4000 : 2000;
      this.captureTimer = setTimeout(() => {
        this.captureTimer = null;
        if (!this.connected || this.active?.capture !== capture) return;
        this.active = null;
        responses.push(this.send('capture_complete', message.session_id, { source: 'simulated', channel, attempt_id: attempt, capture_id: capture, workspace_epoch: epoch,
          started_monotonic_ms: start, ended_monotonic_ms: this.now(), fixture_id: 'synthetic_bench_v1', values: syntheticValues(channel) }));
      }, duration);
    } else if (message.type === 'cancel_capture') {
      knownKeys(p, ['deadline_after_ms', 'attempt_id', 'capture_id', 'workspace_epoch']);
      if (this.active && (this.active.attempt !== p.attempt_id || this.active.capture !== p.capture_id || this.active.epoch !== p.workspace_epoch || this.active.session !== message.session_id)) throw new DeviceError('CANCEL_IDENTITY');
      if (this.captureTimer) clearTimeout(this.captureTimer); this.captureTimer = null; this.active = null; ack();
    } else throw new DeviceError('UNSUPPORTED_COMMAND');
    this.priorResponses.set(message.message_id, responses);
  }
}
