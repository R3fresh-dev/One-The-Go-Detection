import { clone, knownKeys, requireObject } from '../core/integrity';
import { DeviceError, uuid } from './protocol';
import { syntheticEcgSample } from './synthetic-values';
import type { CaptureContext } from './types';

/** Development-only constants. No setting here qualifies physiological quality or timing. */
export const SYNTHETIC_SIGNAL_CONFIGURATION = Object.freeze({
  id: 'synthetic_signal_preview_v1' as const,
  frameMs: 100,
  staleMs: 500,
  ecgSampleRateHz: 50,
  ecgBatchSamples: 5,
  visibleSamples: 100,
  ecgTotalSamples: 200,
  faultFrame: 12,
});
export type SyntheticSignalChannel = 'ppg' | 'ecg';
export type SyntheticSignalScenario = 'clean' | 'poor_contact' | 'motion_artifact' | 'lead_off' | 'saturated' | 'transport_gap' | 'stale_signal' | 'insufficient_samples';
export interface SyntheticSignalOptions { signalScenario?: SyntheticSignalScenario }
export type SyntheticSignalState = 'waiting_for_contact' | 'acquiring' | 'poor_contact' | 'motion_artifact' | 'lead_off' | 'saturated' | 'transport_gap' | 'stale_signal' | 'insufficient_valid_samples' | 'complete' | 'invalid';
export type SyntheticContact = 'unknown' | 'present' | 'absent';
export type SyntheticSignalFailureReason = 'SYNTHETIC_POOR_CONTACT' | 'SYNTHETIC_MOTION_ARTIFACT' | 'SYNTHETIC_LEAD_OFF' | 'SYNTHETIC_SATURATED' | 'SYNTHETIC_TRANSPORT_GAP' | 'SYNTHETIC_STALE_SIGNAL' | 'SYNTHETIC_INSUFFICIENT_SAMPLES' | 'SYNTHETIC_SIGNAL_INVALID';
export interface SyntheticSignalIdentity {
  deviceId: string; bootId: string; context: CaptureContext; channel: SyntheticSignalChannel; scenario: SyntheticSignalScenario;
}
export interface SyntheticSignalFrame extends SyntheticSignalIdentity {
  fixtureId: typeof SYNTHETIC_SIGNAL_CONFIGURATION.id;
  source: 'simulated';
  sequence: number;
  elapsedMs: number;
  startedMonotonicMs: number;
  state: Exclude<SyntheticSignalState, 'complete' | 'invalid' | 'stale_signal'>;
  contact: SyntheticContact;
  heartRateBpm: number | null;
  sampleOffset: number;
  samples: number[];
}
export interface SyntheticSignalSample { index: number; elapsedMs: number; value: number }
export interface SyntheticSignalPreview extends SyntheticSignalIdentity {
  fixtureId: typeof SYNTHETIC_SIGNAL_CONFIGURATION.id;
  source: 'simulated';
  state: SyntheticSignalState;
  terminal: boolean;
  reason: SyntheticSignalFailureReason | null;
  contact: SyntheticContact;
  heartRateBpm: number | null;
  lastHeartRateBpm: number | null;
  lastReceivedAt: string | null;
  elapsedMs: number;
  acceptedBatches: number;
  expectedBatches: number;
  acceptedSamples: number;
  droppedSamples: number;
  samples: SyntheticSignalSample[];
  modelEligible: false;
}

const COMMON_SCENARIOS: readonly SyntheticSignalScenario[] = ['clean', 'poor_contact', 'motion_artifact', 'transport_gap', 'stale_signal', 'insufficient_samples'];
export function signalScenarios(channel: SyntheticSignalChannel): readonly SyntheticSignalScenario[] {
  return channel === 'ecg' ? [...COMMON_SCENARIOS, 'lead_off', 'saturated'] : [...COMMON_SCENARIOS];
}
export function assertSignalScenario(channel: SyntheticSignalChannel, scenario: unknown): asserts scenario is SyntheticSignalScenario {
  if (typeof scenario !== 'string' || !signalScenarios(channel).includes(scenario as SyntheticSignalScenario)) throw new DeviceError('SYNTHETIC_SCENARIO_UNAVAILABLE');
}
export function sameCaptureContext(a: CaptureContext, b: CaptureContext): boolean {
  return a.sessionId === b.sessionId && a.attemptId === b.attemptId && a.captureId === b.captureId && a.workspaceEpoch === b.workspaceEpoch;
}
export function syntheticSignalFrame(identity: SyntheticSignalIdentity, sequence: number, startedMonotonicMs: number): SyntheticSignalFrame | null {
  assertSignalScenario(identity.channel, identity.scenario);
  const last = identity.channel === 'ecg' ? 40 : 30;
  if (!Number.isInteger(sequence) || sequence < 0 || sequence > last) throw new DeviceError('SYNTHETIC_FRAME_BOUNDS');
  if (identity.scenario === 'stale_signal' && sequence > 10) return null;
  let state: SyntheticSignalFrame['state'] = sequence === 0 ? 'waiting_for_contact' : 'acquiring';
  if (sequence === 12 && !['clean', 'stale_signal', 'insufficient_samples'].includes(identity.scenario)) state = identity.scenario as SyntheticSignalFrame['state'];
  if (identity.scenario === 'insufficient_samples' && sequence === last) state = 'insufficient_valid_samples';
  const contact = state === 'waiting_for_contact' ? 'unknown' : state === 'poor_contact' || state === 'lead_off' ? 'absent' : 'present';
  const sampleOffset = identity.channel === 'ecg' ? Math.max(0, sequence - 1) * 5 + (state === 'transport_gap' ? 5 : 0) : 0;
  const samples = identity.channel === 'ecg' && state === 'acquiring' ? Array.from({ length: 5 }, (_, i) => syntheticEcgSample(sampleOffset + i)) : [];
  return { ...clone(identity), fixtureId: SYNTHETIC_SIGNAL_CONFIGURATION.id, source: 'simulated', sequence, elapsedMs: sequence * 100, startedMonotonicMs, state, contact, heartRateBpm: state === 'acquiring' ? 72 : null, sampleOffset, samples };
}

export class SyntheticSignalError extends DeviceError {
  readonly identity: SyntheticSignalIdentity;
  constructor(public readonly signalReason: SyntheticSignalFailureReason, identity: SyntheticSignalIdentity, public readonly contact: SyntheticContact, public readonly droppedSamples: number) {
    super(signalReason); this.name = 'SyntheticSignalError'; this.identity = clone(identity);
  }
}
const FAULTS: Partial<Record<SyntheticSignalState, SyntheticSignalFailureReason>> = {
  poor_contact: 'SYNTHETIC_POOR_CONTACT', motion_artifact: 'SYNTHETIC_MOTION_ARTIFACT', lead_off: 'SYNTHETIC_LEAD_OFF', saturated: 'SYNTHETIC_SATURATED', transport_gap: 'SYNTHETIC_TRANSPORT_GAP', stale_signal: 'SYNTHETIC_STALE_SIGNAL', insufficient_valid_samples: 'SYNTHETIC_INSUFFICIENT_SAMPLES', invalid: 'SYNTHETIC_SIGNAL_INVALID',
};

/** Validates local fictional preview events. It never authorizes a capture or replaces wire proof. */
export class SyntheticSignalReducer {
  private readonly identity: SyntheticSignalIdentity;
  private data: SyntheticSignalPreview;
  private nextSequence = 0;
  private startedMonotonicMs: number | null = null;
  private lastReceived: number;
  constructor(identity: SyntheticSignalIdentity, armedMonotonicMs: number) {
    assertSignalScenario(identity.channel, identity.scenario);
    uuid(identity.bootId); uuid(identity.context.sessionId); uuid(identity.context.attemptId); uuid(identity.context.captureId);
    if (!Number.isFinite(armedMonotonicMs) || armedMonotonicMs < 0 || !identity.context.workspaceEpoch || identity.context.workspaceEpoch.length > 128) throw new DeviceError('SYNTHETIC_SIGNAL_INVALID');
    this.identity = clone(identity); this.lastReceived = armedMonotonicMs;
    this.data = { ...clone(identity), fixtureId: SYNTHETIC_SIGNAL_CONFIGURATION.id, source: 'simulated', state: 'waiting_for_contact', terminal: false, reason: null, contact: 'unknown', heartRateBpm: null, lastHeartRateBpm: null, lastReceivedAt: null, elapsedMs: 0, acceptedBatches: 0, expectedBatches: identity.channel === 'ecg' ? 40 : 30, acceptedSamples: 0, droppedSamples: 0, samples: [], modelEligible: false };
  }
  snapshot(): SyntheticSignalPreview { return clone(this.data); }
  private reject(state: SyntheticSignalState, dropped = 0): never {
    const reason = FAULTS[state] ?? 'SYNTHETIC_SIGNAL_INVALID';
    this.data = { ...this.data, state, terminal: true, reason, heartRateBpm: null, droppedSamples: Math.min(200, Math.max(0, dropped)) };
    throw new SyntheticSignalError(reason, this.identity, this.data.contact, this.data.droppedSamples);
  }
  tick(now: number): void {
    if (this.data.terminal) return;
    if (!Number.isFinite(now) || now < this.lastReceived) this.reject('invalid');
    if (now - this.lastReceived >= SYNTHETIC_SIGNAL_CONFIGURATION.staleMs) this.reject('stale_signal');
  }
  accept(frame: SyntheticSignalFrame, receivedAtMonotonicMs: number, receivedAt = new Date().toISOString()): SyntheticSignalPreview {
    if (this.data.terminal) return this.snapshot();
    try {
      this.tick(receivedAtMonotonicMs);
      const record = requireObject(frame);
      knownKeys(record, ['deviceId', 'bootId', 'context', 'channel', 'scenario', 'fixtureId', 'source', 'sequence', 'elapsedMs', 'startedMonotonicMs', 'state', 'contact', 'heartRateBpm', 'sampleOffset', 'samples']);
      knownKeys(requireObject(frame.context), ['sessionId', 'attemptId', 'captureId', 'workspaceEpoch']);
      if (frame.fixtureId !== SYNTHETIC_SIGNAL_CONFIGURATION.id || frame.source !== 'simulated' || frame.deviceId !== this.identity.deviceId || frame.bootId !== this.identity.bootId || !sameCaptureContext(frame.context, this.identity.context) || frame.channel !== this.identity.channel || frame.scenario !== this.identity.scenario) this.reject('invalid');
      if (!Number.isInteger(frame.sequence) || frame.sequence < 0 || frame.sequence > this.data.expectedBatches || !Array.isArray(frame.samples) || frame.samples.length > 5) this.reject('invalid');
      if (frame.sequence !== this.nextSequence) this.reject(frame.sequence > this.nextSequence ? 'transport_gap' : 'invalid', this.identity.channel === 'ecg' && frame.sequence > this.nextSequence ? (frame.sequence - this.nextSequence) * 5 : 0);
      if (!Number.isFinite(frame.startedMonotonicMs) || frame.startedMonotonicMs < 0 || frame.elapsedMs !== frame.sequence * 100 || frame.startedMonotonicMs + frame.elapsedMs > receivedAtMonotonicMs) this.reject('invalid');
      if (this.startedMonotonicMs !== null && frame.startedMonotonicMs !== this.startedMonotonicMs) this.reject('invalid');
      if (receivedAtMonotonicMs - (frame.startedMonotonicMs + frame.elapsedMs) >= 500) this.reject('stale_signal');
      const expected = syntheticSignalFrame(this.identity, frame.sequence, frame.startedMonotonicMs);
      if (!expected) this.reject('stale_signal');
      if (frame.state !== expected.state || frame.contact !== expected.contact || frame.heartRateBpm !== expected.heartRateBpm || frame.sampleOffset !== expected.sampleOffset || frame.samples.length !== expected.samples.length || frame.samples.some((v, i) => !Number.isInteger(v) || v < -1000 || v > 1000 || v !== expected.samples[i])) this.reject('invalid');
      this.startedMonotonicMs = frame.startedMonotonicMs; this.lastReceived = receivedAtMonotonicMs; this.nextSequence++;
      this.data = { ...this.data, elapsedMs: frame.elapsedMs, lastReceivedAt: receivedAt, contact: frame.contact };
      if (frame.state !== 'acquiring' && frame.state !== 'waiting_for_contact') this.reject(frame.state, frame.state === 'transport_gap' && this.identity.channel === 'ecg' ? 5 : 0);
      const appended = frame.samples.map((value, i) => ({ index: frame.sampleOffset + i, elapsedMs: (frame.sampleOffset + i + 1) * 20, value }));
      const retainFrom = Math.max(0, this.data.samples.length + appended.length - SYNTHETIC_SIGNAL_CONFIGURATION.visibleSamples);
      this.data = { ...this.data, state: frame.state, heartRateBpm: frame.heartRateBpm, lastHeartRateBpm: frame.heartRateBpm ?? this.data.lastHeartRateBpm, acceptedBatches: this.data.acceptedBatches + (frame.sequence > 0 ? 1 : 0), acceptedSamples: this.data.acceptedSamples + frame.samples.length, samples: this.data.samples.slice(retainFrom).concat(appended) };
      return this.snapshot();
    } catch (error) {
      if (error instanceof SyntheticSignalError) throw error;
      return this.reject('invalid');
    }
  }
  /** Called only after the controller verifies the matching full transport completion. */
  complete(startedMonotonicMs: number, endedMonotonicMs: number, receivedAtMonotonicMs: number): SyntheticSignalPreview {
    if (this.data.terminal) throw new SyntheticSignalError(this.data.reason ?? 'SYNTHETIC_SIGNAL_INVALID', this.identity, this.data.contact, this.data.droppedSamples);
    this.tick(receivedAtMonotonicMs);
    if (this.identity.scenario !== 'clean' || this.data.acceptedBatches !== this.data.expectedBatches || this.data.acceptedSamples !== (this.identity.channel === 'ecg' ? 200 : 0)) this.reject('insufficient_valid_samples');
    if (startedMonotonicMs !== this.startedMonotonicMs || !Number.isFinite(endedMonotonicMs) || endedMonotonicMs < startedMonotonicMs + this.data.expectedBatches * 100) this.reject('invalid');
    this.data = { ...this.data, state: 'complete', terminal: true, heartRateBpm: null };
    return this.snapshot();
  }
}
