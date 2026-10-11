import { canonicalJson, clone, digest, knownKeys, requiredString } from '../core/integrity';
import { ACK_TIMEOUT_MS, capabilities, clockExchange, DeviceError, fragmentMessage, fromBase64, MAX_RETRIES, MessageJournal, Reassembler, selectClock, toBase64, uuid } from './protocol';
import type { ClockEvidence, DeviceChannel, DeviceEnvelope } from './protocol';
import { LocalSimulatorTransport, syntheticValues } from './simulator';
import { assertSignalScenario, SyntheticSignalError, SyntheticSignalReducer } from './signal';
import type { SyntheticSignalOptions } from './signal';
import type { CaptureContext, DeviceAssociation, DeviceController, DeviceControllerOptions, DeviceSnapshot, DeviceTransport, SyntheticDeviceCapture, TransportEvent } from './types';

interface Pending {
  message: DeviceEnvelope;
  acked: boolean;
  expectedType: DeviceEnvelope['type'] | null;
  resolve: (value: {message: DeviceEnvelope; received: number}) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout> | null;
}
function code(error: unknown): string {
  if (error instanceof DeviceError) return error.code;
  const nativeCode = error && typeof error === 'object' && 'code' in error ? error.code : null;
  return typeof nativeCode === 'string' && /^[A-Z_]{3,80}$/.test(nativeCode) ? nativeCode : 'DEVICE_OPERATION_FAILED';
}
const MAX_EVIDENCE_MESSAGES = 32;

export class DeviceControllerImpl implements DeviceController {
  private state: DeviceSnapshot;
  private listeners = new Set<(snapshot: DeviceSnapshot) => void>();
  private transport: DeviceTransport;
  private unsubscribe: () => void;
  private generation = 0;
  private disposed = false;
  private receiver = new Reassembler(20);
  private journal = new MessageJournal(256);
  private attBytes = 20;
  private txSequence = 0;
  private transfer = 0;
  private sessionId: string | null = null;
  private pending = new Map<string, Pending>();
  private outgoing: Promise<void> = Promise.resolve();
  private scanTimer: ReturnType<typeof setTimeout> | null = null;
  private assemblyTimer: ReturnType<typeof setInterval> | null = null;
  private signal: SyntheticSignalReducer | null = null;
  private signalTimer: ReturnType<typeof setInterval> | null = null;
  private active: { context: CaptureContext; channel: DeviceChannel; clock: ClockEvidence | null; startedAt: string; messages: DeviceEnvelope[]; resolve: (value: SyntheticDeviceCapture) => void; reject: (error: Error) => void; timer: ReturnType<typeof setTimeout> } | null = null;
  constructor(private readonly options: DeviceControllerOptions, private readonly nativeFactory: () => DeviceTransport) {
    this.transport = nativeFactory(); this.unsubscribe = this.transport.subscribe(event => this.receive(event));
    this.state = { state: this.transport.available ? 'idle' : 'unavailable', observedAt: new Date().toISOString(), devices: [], association: null, reason: this.transport.available ? null : 'NATIVE_BLUETOOTH_UNAVAILABLE', captureInProgress: false, signalPreview: null, humanCaptureAvailable: false };
  }
  snapshot(): DeviceSnapshot { return clone(this.state); }
  subscribe(listener: (snapshot: DeviceSnapshot) => void): () => void { this.listeners.add(listener); listener(this.snapshot()); return () => this.listeners.delete(listener); }
  private update(patch: Partial<DeviceSnapshot>): void {
    const observed = ['state', 'association', 'reason', 'captureInProgress'].some(key => Object.prototype.hasOwnProperty.call(patch, key));
    this.state = { ...this.state, ...patch, ...(observed ? { observedAt: new Date().toISOString() } : {}), humanCaptureAvailable: false };
    this.listeners.forEach(listener => listener(this.snapshot()));
  }
  private checkLive(): void { if (this.disposed) throw new DeviceError('CONTROLLER_DISPOSED'); }
  private association(): DeviceAssociation { if (!this.state.association) throw new DeviceError('NOT_CONNECTED'); return this.state.association; }
  async scan(): Promise<void> {
    this.checkLive();
    await this.disconnect();
    if (this.transport.kind !== 'ble_unprovisioned') await this.changeTransport(this.nativeFactory());
    if (!this.transport.available) { this.update({ state: 'unavailable', reason: 'NATIVE_BLUETOOTH_UNAVAILABLE' }); return; }
    this.update({ state: 'scanning', devices: [], reason: null });
    try { await this.transport.scan(); this.scanTimer = setTimeout(() => { void this.stopScan(); }, 15_000); }
    catch (error) { this.update({ state: 'error', reason: code(error) }); throw error; }
  }
  async stopScan(): Promise<void> { if (this.scanTimer) clearTimeout(this.scanTimer); this.scanTimer = null; await this.transport.stopScan(); if (this.state.state === 'scanning') this.update({ state: 'idle' }); }
  async connect(peripheralId: string): Promise<void> {
    this.checkLive(); requiredString(peripheralId, 128);
    if (!this.state.devices.some(device => device.peripheralId === peripheralId) && !(this.transport.kind === 'local_simulator' && peripheralId === 'local-simulator')) throw new DeviceError('UNKNOWN_PERIPHERAL');
    await this.stopScan();
    if (this.state.association || this.active) await this.disconnect();
    const generation = ++this.generation;
    this.update({ state: 'connecting', reason: null });
    try {
      const connected = await this.transport.connect(peripheralId);
      if (generation !== this.generation || this.disposed) throw new DeviceError('CONNECTION_CANCELED');
      if (connected.peripheralId !== peripheralId) throw new DeviceError('PERIPHERAL_MISMATCH');
      const cap = capabilities(connected.capabilities);
      if (!Number.isInteger(connected.mtu) || connected.mtu < 23 || connected.mtu > 515) throw new DeviceError('UNSUPPORTED_MTU');
      this.attBytes = Math.min(connected.mtu - 3, cap.max_att_bytes);
      this.receiver = new Reassembler(this.attBytes); this.journal = new MessageJournal(256); this.txSequence = 0; this.transfer = 0; this.outgoing = Promise.resolve();
      this.sessionId = uuid(this.options.idFactory());
      this.update({ association: { peripheralId, deviceId: cap.device_id, bootId: cap.boot_id, hardwareRevision: cap.hardware_revision, firmwareVersion: cap.firmware_version, protocolVersion: 1,
        source: 'simulated', verifiedBindingId: null, transport: this.transport.kind, capabilities: cap } });
      this.assemblyTimer = setInterval(() => { try { this.receiver.expire(this.transport.now()); } catch (error) { this.fail(code(error)); } }, 1000);
      await this.hello(); await this.synchronize();
      if (generation !== this.generation) throw new DeviceError('CONNECTION_CANCELED');
      this.update({ state: 'connected_simulator', reason: null });
    } catch (error) { if (generation === this.generation) this.fail(code(error)); throw error; }
  }
  private async hello(): Promise<void> {
    const response = await this.command('hello', { deadline_after_ms: 120_000 }, 'hello');
    knownKeys(response.message.payload, ['request_message_id', 'source', 'configuration_id']);
    if (response.message.payload.source !== 'simulated' || response.message.payload.configuration_id !== 'synthetic_bench_v1') throw new DeviceError('UNVERIFIED_HUMAN_HARDWARE');
  }
  private async synchronize(): Promise<ClockEvidence> {
    const association = this.association(), exchanges = [];
    for (let i = 0; i < 3; i++) {
      const send = Math.floor(this.transport.now());
      const reply = await this.command('clock_sync', { deadline_after_ms: 120_000, phone_send_ms: send }, 'clock_sync');
      const p = reply.message.payload; knownKeys(p, ['request_message_id', 'phone_send_ms', 'device_receive_ms', 'device_send_ms']);
      if (p.phone_send_ms !== send || typeof p.device_receive_ms !== 'number' || typeof p.device_send_ms !== 'number') throw new DeviceError('CLOCK_RESPONSE_MISMATCH');
      // One millisecond is a conservative software timestamp quantization bound for this synthetic-only policy.
      // It does not bound clock oscillator accuracy or qualify a physiological channel.
      exchanges.push(clockExchange(send, p.device_receive_ms, p.device_send_ms, reply.received, 1, association.capabilities.timestamp_resolution_ms));
    }
    return selectClock(exchanges, association.bootId);
  }
  private envelope(type: DeviceEnvelope['type'], payload: Record<string, unknown>): DeviceEnvelope {
    const association = this.association(); if (!this.sessionId) throw new DeviceError('NO_SESSION');
    if (this.txSequence >= Number.MAX_SAFE_INTEGER) throw new DeviceError('SEQUENCE_EXHAUSTED');
    return { protocol_version: 1, message_id: uuid(this.options.idFactory()), device_id: association.deviceId, boot_id: association.bootId, session_id: this.sessionId, sequence: this.txSequence++, monotonic_ms: this.transport.now(), type, payload };
  }
  private send(message: DeviceEnvelope): Promise<void> {
    const generation = this.generation, transport = this.transport;
    const action = this.outgoing.then(async () => {
      if (generation !== this.generation) throw new DeviceError('STALE_OPERATION');
      const frames = fragmentMessage(message, this.transfer++, this.attBytes);
      for (const frame of frames) { if (generation !== this.generation) throw new DeviceError('STALE_OPERATION'); await transport.write(toBase64(frame)); }
    });
    this.outgoing = action.catch(() => {}); return action;
  }
  private command(type: DeviceEnvelope['type'], payload: Record<string, unknown>, expectedType: DeviceEnvelope['type'] | null): Promise<{message: DeviceEnvelope; received: number}> {
    const message = this.envelope(type, payload);
    return new Promise((resolve, reject) => {
      const pending: Pending = { message, acked: false, expectedType, resolve, reject, timer: null }; this.pending.set(message.message_id, pending);
      const attempt = async (retry: number): Promise<void> => {
        try {
          await this.send(message);
          if (!this.pending.has(message.message_id)) return;
          // The timer starts after the last fragment's write-with-response completion, never at the first fragment.
          pending.timer = setTimeout(() => {
            pending.timer = null;
            if (!this.pending.has(message.message_id)) return;
            if (retry < MAX_RETRIES) { void attempt(retry + 1); }
            else { this.pending.delete(message.message_id); reject(new DeviceError(pending.acked ? 'COMMAND_RESPONSE_TIMEOUT' : 'ACK_TIMEOUT')); }
          }, ACK_TIMEOUT_MS);
        } catch (error) { this.pending.delete(message.message_id); reject(error instanceof Error ? error : new DeviceError('COMMAND_FAILED')); }
      };
      void attempt(0);
    });
  }
  private settlePending(pending: Pending, message: DeviceEnvelope, received: number): void {
    if (pending.timer) clearTimeout(pending.timer); this.pending.delete(pending.message.message_id); pending.resolve({ message, received });
  }
  private record(message: DeviceEnvelope): void {
    if (!this.active) return;
    if (this.active.messages.length >= MAX_EVIDENCE_MESSAGES) throw new DeviceError('EVIDENCE_MESSAGE_LIMIT');
    this.active.messages.push(clone(message));
  }
  private receive(event: TransportEvent): void {
    if (this.disposed) return;
    if (event.kind === 'discovered') {
      if (this.state.state !== 'scanning') return;
      const devices = this.state.devices.filter(device => device.peripheralId !== event.peripheralId);
      if (devices.length >= 64) return;
      this.update({ devices: [...devices, { peripheralId: event.peripheralId, alias: event.alias.slice(0, 64), rssi: event.rssi }] }); return;
    }
    if (event.kind === 'state') {
      if (event.state === 'idle' && this.state.state === 'scanning') this.update({ state: 'idle' });
      else if (['powered_off', 'unauthorized', 'unsupported', 'background'].includes(event.state)) this.fail(event.state.toUpperCase());
      return;
    }
    if (event.kind === 'disconnected') { if (this.state.association || this.active || this.state.state === 'connecting') this.fail(event.reason); return; }
    if (event.kind === 'synthetic_signal') {
      if (!this.active || !this.signal) return;
      try {
        if (this.transport.kind !== 'local_simulator' || event.peripheralId !== this.state.association?.peripheralId) throw new DeviceError('SYNTHETIC_PREVIEW_UNAVAILABLE');
        this.update({ signalPreview: this.signal.accept(event.frame, event.receivedAtMonotonicMs) });
      } catch (error) {
        if (error instanceof SyntheticSignalError) { this.update({ signalPreview: this.signal.snapshot() }); this.fail(error.code, error); }
        else this.fail(code(error));
      }
      return;
    }
    if (!this.state.association || !this.sessionId || event.peripheralId !== this.state.association.peripheralId) return;
    try {
      const message = this.receiver.push(fromBase64(event.base64, this.attBytes), event.receivedAtMonotonicMs); if (!message) return;
      const association = this.association();
      const disposition = this.journal.accept(message, { deviceId: association.deviceId, bootId: association.bootId, sessionId: this.sessionId });
      if (message.type !== 'ack') { const acknowledgment = this.envelope('ack', { ack_message_id: message.message_id, status: 'accepted' }); void this.send(acknowledgment).catch(error => this.fail(code(error))); }
      if (disposition === 'duplicate') return;
      this.record(message);
      if (message.type === 'ack') {
        knownKeys(message.payload, ['ack_message_id', 'status']); const id = uuid(message.payload.ack_message_id);
        const pending = this.pending.get(id); if (!pending || message.payload.status !== 'accepted') throw new DeviceError('UNEXPECTED_ACK');
        pending.acked = true; if (!pending.expectedType) this.settlePending(pending, message, event.receivedAtMonotonicMs);
      } else if (message.type === 'hello' || message.type === 'clock_sync') {
        const id = uuid(message.payload.request_message_id), pending = this.pending.get(id);
        if (!pending || pending.expectedType !== message.type || !pending.acked) throw new DeviceError('RESPONSE_BEFORE_ACK');
        this.settlePending(pending, message, event.receivedAtMonotonicMs);
      } else if (message.type === 'capture_complete') this.complete(message);
      else if (message.type === 'error') {
        knownKeys(message.payload, ['request_message_id', 'code']); uuid(message.payload.request_message_id);
        const reason = requiredString(message.payload.code, 64);
        throw new DeviceError(['REPLAY_JOURNAL_FULL', 'DEVICE_BUSY', 'SEQUENCE_REPLAY', 'COMMAND_DEADLINE', 'CAPTURE_REFUSED'].includes(reason) ? reason : 'PERIPHERAL_REJECTED_COMMAND');
      }
      else throw new DeviceError('UNEXPECTED_DEVICE_MESSAGE');
    } catch (error) { this.fail(code(error), error instanceof SyntheticSignalError ? error : undefined); }
  }
  async captureSynthetic(channel: DeviceChannel, context: CaptureContext, options?: SyntheticSignalOptions): Promise<SyntheticDeviceCapture> {
    this.checkLive();
    if (this.state.state !== 'connected_simulator' || this.active) throw new DeviceError('DEVICE_NOT_READY');
    uuid(context.sessionId); uuid(context.attemptId); uuid(context.captureId); requiredString(context.workspaceEpoch, 128);
    if (!this.association().capabilities.channels.includes(channel)) throw new DeviceError('CHANNEL_UNAVAILABLE');
    if (options) knownKeys(options as Record<string, unknown>, ['signalScenario']);
    if (channel === 'saliva' && options?.signalScenario !== undefined) throw new DeviceError('SYNTHETIC_SCENARIO_UNAVAILABLE');
    const scenario = options?.signalScenario ?? 'clean';
    if (channel !== 'saliva') {
      assertSignalScenario(channel, scenario);
      if (this.transport.kind !== 'local_simulator' && scenario !== 'clean') throw new DeviceError('SYNTHETIC_SCENARIO_REQUIRES_LOCAL_SIMULATOR');
      if (this.transport.kind === 'local_simulator') {
        if (!this.transport.prepareSyntheticSignal) throw new DeviceError('SYNTHETIC_PREVIEW_UNAVAILABLE');
        this.transport.prepareSyntheticSignal(scenario);
      }
    }
    const generation = this.generation;
    this.sessionId = context.sessionId;
    const result = new Promise<SyntheticDeviceCapture>((resolve, reject) => {
      const timer = setTimeout(() => this.fail('CAPTURE_TIMEOUT'), 30_000);
      this.active = { context: clone(context), channel, clock: null, startedAt: new Date().toISOString(), messages: [], resolve, reject, timer };
    });
    // Install a rejection consumer immediately; callers still receive the original rejected promise.
    void result.catch(() => {});
    this.update({ captureInProgress: true, reason: null, signalPreview: null });
    try {
      await this.hello(); const clock = await this.synchronize();
      const active = this.active as NonNullable<DeviceControllerImpl['active']> | null;
      if (!active || generation !== this.generation) throw new DeviceError('CAPTURE_CANCELED');
      active.clock = clock;
      if (this.transport.kind === 'local_simulator' && channel !== 'saliva') {
        const association = this.association();
        this.signal = new SyntheticSignalReducer({ deviceId: association.deviceId, bootId: association.bootId, context, channel, scenario }, this.transport.now());
        this.update({ signalPreview: this.signal.snapshot() });
        this.signalTimer = setInterval(() => {
          const signal = this.signal; if (!signal || !this.active) return;
          try { signal.tick(this.transport.now()); }
          catch (error) { this.update({ signalPreview: signal.snapshot() }); this.fail(code(error), error instanceof SyntheticSignalError ? error : undefined); }
        }, 100);
      }
      await this.command('start_capture', { deadline_after_ms: 120_000, deadline_device_ms: this.transport.now() + clock.offset_ms + 15_000,
        attempt_id: context.attemptId, capture_id: context.captureId, workspace_epoch: context.workspaceEpoch, channel, source: 'simulated' }, null);
    } catch (error) { if (this.active && generation === this.generation) this.fail(code(error), error instanceof SyntheticSignalError ? error : undefined); }
    return result;
  }
  private complete(message: DeviceEnvelope): void {
    const a = this.active; if (!a || !a.clock) throw new DeviceError('UNEXPECTED_CAPTURE_COMPLETION');
    // Completion cannot outrun acceptance of the matching start command.
    if ([...this.pending.values()].some(p => p.message.type === 'start_capture')) throw new DeviceError('COMPLETION_BEFORE_START_ACK');
    const p = message.payload;
    knownKeys(p, ['source', 'channel', 'attempt_id', 'capture_id', 'workspace_epoch', 'started_monotonic_ms', 'ended_monotonic_ms', 'fixture_id', 'values']);
    if (p.source !== 'simulated' || p.fixture_id !== 'synthetic_bench_v1') throw new DeviceError('UNVERIFIED_HUMAN_HARDWARE');
    if (p.channel !== a.channel || p.attempt_id !== a.context.attemptId || p.capture_id !== a.context.captureId || p.workspace_epoch !== a.context.workspaceEpoch) throw new DeviceError('CAPTURE_IDENTITY_MISMATCH');
    const start = p.started_monotonic_ms, end = p.ended_monotonic_ms;
    if (typeof start !== 'number' || typeof end !== 'number' || !Number.isFinite(start + end) || start < 0 || end < start || end - start > 30_000) throw new DeviceError('CAPTURE_CLOCK_INVALID');
    const expected = syntheticValues(a.channel);
    if (canonicalJson(p.values) !== canonicalJson(expected)) throw new DeviceError('SYNTHETIC_FIXTURE_MISMATCH');
    if (this.association().transport === 'local_simulator' && a.channel !== 'saliva') {
      if (!this.signal) throw new DeviceError('SYNTHETIC_PREVIEW_UNAVAILABLE');
      try { this.update({ signalPreview: this.signal.complete(start, end, this.transport.now()) }); }
      catch (error) { this.update({ signalPreview: this.signal.snapshot() }); throw error; }
    }
    const association = clone(this.association());
    const payload = { source: 'simulated' as const, channel: a.channel, context: a.context, association, clockEvidence: a.clock,
      startedAt: a.startedAt, endedAt: new Date().toISOString(), deviceStartedMonotonicMs: start, deviceEndedMonotonicMs: end,
      values: expected, fixtureId: 'synthetic_bench_v1' as const, messages: a.messages, qualityFlags: ['SIMULATED', 'UNVERIFIED_DEVICE'] as ['SIMULATED', 'UNVERIFIED_DEVICE'], modelEligible: false as const };
    clearTimeout(a.timer); this.clearSignalTimer(); this.signal = null; this.active = null; this.update({ captureInProgress: false });
    a.resolve({ ...payload, evidenceSha256: digest(payload) });
  }
  private clearSignalTimer(): void { if (this.signalTimer) clearInterval(this.signalTimer); this.signalTimer = null; }
  private invalidate(reason: string, signalError?: SyntheticSignalError): void {
    this.generation++;
    for (const pending of this.pending.values()) { if (pending.timer) clearTimeout(pending.timer); pending.reject(new DeviceError(reason)); } this.pending.clear();
    if (this.assemblyTimer) clearInterval(this.assemblyTimer); this.assemblyTimer = null;
    this.clearSignalTimer(); this.signal = null;
    this.receiver.reset(); this.sessionId = null;
    const active = this.active; this.active = null;
    if (active) { clearTimeout(active.timer); active.reject(signalError ?? new DeviceError(reason)); this.options.onInvalidated?.(reason, clone(active.context)); }
    this.update({ association: null, captureInProgress: false, ...(signalError ? {} : { signalPreview: null }) });
  }
  private fail(reason: string, signalError?: SyntheticSignalError): void {
    this.invalidate(reason, signalError); this.update({ state: 'error', reason });
    // Disconnect also stops the simulator/peripheral acquisition. Local invalidation has already happened.
    void this.transport.disconnect().catch(() => {});
  }
  async cancelCapture(reason = 'USER_CANCELED'): Promise<void> {
    if (!this.active) { if (this.state.signalPreview) this.update({ signalPreview: null }); return; }
    await this.disconnectWithReason(reason);
  }
  private async disconnectWithReason(reason: string): Promise<void> {
    this.invalidate(reason); if (this.scanTimer) clearTimeout(this.scanTimer); this.scanTimer = null;
    this.update({ state: this.transport.available ? 'idle' : 'unavailable', reason: null });
    await this.transport.stopScan(); await this.transport.disconnect();
  }
  async disconnect(): Promise<void> { await this.disconnectWithReason('DISCONNECTED'); }
  async forget(): Promise<void> { await this.disconnectWithReason('FORGOTTEN'); this.update({ devices: [] }); }
  private async changeTransport(transport: DeviceTransport): Promise<void> {
    this.unsubscribe(); await this.transport.disconnect(); this.transport = transport; this.unsubscribe = transport.subscribe(event => this.receive(event));
    this.update({ state: transport.available ? 'idle' : 'unavailable', devices: [], association: null, reason: null, signalPreview: null });
  }
  async useLocalSimulator(): Promise<void> {
    this.checkLive(); await this.disconnect(); await this.changeTransport(new LocalSimulatorTransport(this.options.idFactory));
    await this.connect('local-simulator');
  }
  async dispose(): Promise<void> { if (this.disposed) return; this.disposed = true; await this.disconnect(); this.unsubscribe(); this.listeners.clear(); }
}
