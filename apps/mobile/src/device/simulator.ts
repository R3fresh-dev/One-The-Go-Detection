import { canonicalJson, knownKeys, requiredString, safeInteger } from '../core/integrity';
import { capabilities, DeviceError, fragmentMessage, fromBase64, MessageJournal, Reassembler, toBase64, uuid } from './protocol';
import type { DeviceChannel, DeviceEnvelope, SyntheticCapabilities } from './protocol';
import type { DeviceTransport, TransportEvent } from './types';
import { assertSignalScenario, syntheticSignalFrame } from './signal';
import type { SyntheticSignalIdentity, SyntheticSignalScenario } from './signal';
import { syntheticValues } from './synthetic-values';
export { syntheticValues } from './synthetic-values';

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
  private signalTimer: ReturnType<typeof setTimeout> | null = null;
  private signalScenario: SyntheticSignalScenario = 'clean';
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
  private clearCaptureTimers(): void {
    if (this.captureTimer) clearTimeout(this.captureTimer);
    if (this.signalTimer) clearTimeout(this.signalTimer);
    this.captureTimer = null; this.signalTimer = null;
  }
  prepareSyntheticSignal(scenario: SyntheticSignalScenario): void {
    if (this.active) throw new DeviceError('DEVICE_BUSY');
    assertSignalScenario('ecg', scenario); this.signalScenario = scenario;
  }
  async disconnect(): Promise<void> { this.connected = false; this.clearCaptureTimers(); this.active = null; this.signalScenario = 'clean'; this.receiver.reset(); this.emit({ kind: 'disconnected', peripheralId: 'local-simulator', reason: 'DISCONNECTED' }); }
  private streamSignal(identity: SyntheticSignalIdentity, start: number, complete: () => void): void {
    const last = identity.channel === 'ecg' ? 40 : 30;
    const deliver = (sequence: number): void => {
      this.signalTimer = null;
      if (!this.connected || this.active?.capture !== identity.context.captureId) return;
      const untilDue = start + sequence * 100 - this.now();
      if (untilDue > 0) { this.signalTimer = setTimeout(() => deliver(sequence), Math.ceil(untilDue)); return; }
      const frame = syntheticSignalFrame(identity, sequence, start);
      // The stale fixture becomes silent. The controller's independent watchdog must end it.
      if (!frame) return;
      this.emit({ kind: 'synthetic_signal', peripheralId: 'local-simulator', frame, receivedAtMonotonicMs: this.now() });
      if (!this.connected || this.active?.capture !== identity.context.captureId) return;
      if (sequence === last) { complete(); return; }
      const next = sequence + 1;
      // A single pending timer is bounded; a delayed UI cannot enqueue a backlog of callbacks.
      this.signalTimer = setTimeout(() => deliver(next), Math.max(0, Math.ceil(start + next * 100 - this.now())));
    };
    deliver(0);
  }
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
      const complete = () => {
        this.captureTimer = null;
        if (!this.connected || this.active?.capture !== capture) return;
        this.active = null;
        responses.push(this.send('capture_complete', message.session_id, { source: 'simulated', channel, attempt_id: attempt, capture_id: capture, workspace_epoch: epoch,
          started_monotonic_ms: start, ended_monotonic_ms: this.now(), fixture_id: 'synthetic_bench_v1', values: syntheticValues(channel) }));
      };
      if (channel === 'saliva') this.captureTimer = setTimeout(complete, duration);
      else {
        assertSignalScenario(channel, this.signalScenario);
        const identity: SyntheticSignalIdentity = { deviceId: this.capabilitiesRecord.device_id, bootId: this.capabilitiesRecord.boot_id, context: { sessionId: message.session_id, attemptId: attempt, captureId: capture, workspaceEpoch: epoch }, channel, scenario: this.signalScenario };
        this.streamSignal(identity, start, complete);
      }
    } else if (message.type === 'cancel_capture') {
      knownKeys(p, ['deadline_after_ms', 'attempt_id', 'capture_id', 'workspace_epoch']);
      if (this.active && (this.active.attempt !== p.attempt_id || this.active.capture !== p.capture_id || this.active.epoch !== p.workspace_epoch || this.active.session !== message.session_id)) throw new DeviceError('CANCEL_IDENTITY');
      this.clearCaptureTimers(); this.active = null; ack();
    } else throw new DeviceError('UNSUPPORTED_COMMAND');
    this.priorResponses.set(message.message_id, responses);
  }
}
