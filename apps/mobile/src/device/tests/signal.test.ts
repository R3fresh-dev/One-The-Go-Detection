import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { createCheck, emptyWorkspace, settleAttempt, startAttempt } from '../../core/domain';
import { canonicalJson, clone, digest } from '../../core/integrity';
import { DeviceControllerImpl } from '../controller';
import { DeviceError } from '../protocol';
import { LocalSimulatorTransport } from '../simulator';
import { syntheticEcgSample, syntheticValues } from '../synthetic-values';
import { getSyntheticSignalFailure } from '../signalFailure';
import { assertSignalScenario, signalScenarios, SyntheticSignalError, SyntheticSignalReducer, syntheticSignalFrame } from '../signal';
import type { SyntheticSignalFrame, SyntheticSignalIdentity, SyntheticSignalScenario } from '../signal';
import { waveformSegments } from '../signalPresentation';

const at = '2026-10-11T18:00:00.000Z';
const identity = (channel: 'ppg' | 'ecg' = 'ecg', scenario: SyntheticSignalScenario = 'clean'): SyntheticSignalIdentity => ({ deviceId: 'SIM-LOCAL-01', bootId: randomUUID(), context: { sessionId: randomUUID(), attemptId: randomUUID(), captureId: randomUUID(), workspaceEpoch: 'guest:current-epoch' }, channel, scenario });
const fails = (code: string) => (error: unknown) => error instanceof DeviceError && error.code === code;
const frame = (id: SyntheticSignalIdentity, sequence: number, start = 1000) => syntheticSignalFrame(id, sequence, start)!;

test('clean PPG and ECG require every batch before transport completion; the visible ring does not replace full evidence', () => {
  for (const channel of ['ppg', 'ecg'] as const) {
    const id = identity(channel), reducer = new SyntheticSignalReducer(id, 1000), expected = channel === 'ecg' ? 40 : 30;
    const originalValues = clone(syntheticValues(channel));
    for (let i = 0; i <= expected; i++) {
      reducer.accept(frame(id, i), 1000 + i * 100, at);
      assert.ok(reducer.snapshot().samples.length <= 100);
    }
    const pending = reducer.snapshot();
    assert.equal(pending.terminal, false, 'preview alone does not complete the attempt');
    assert.equal(pending.acceptedBatches, expected);
    assert.equal(pending.heartRateBpm, 72);
    const completed = reducer.complete(1000, 1000 + expected * 100, 1001 + expected * 100);
    assert.equal(completed.state, 'complete');
    assert.equal(completed.heartRateBpm, null, 'completed observations are not current live values');
    assert.equal(completed.lastHeartRateBpm, 72);
    if (channel === 'ecg') {
      assert.equal(completed.acceptedSamples, 200);
      assert.deepEqual(completed.samples.map(s => s.index), Array.from({ length: 100 }, (_, i) => i + 100));
      assert.deepEqual(completed.samples.map(s => s.value), Array.from({ length: 100 }, (_, i) => syntheticEcgSample(i + 100)));
    } else {
      assert.equal(completed.acceptedSamples, 0); assert.deepEqual(completed.samples, []);
    }
    assert.deepEqual(syntheticValues(channel), originalValues, 'display collection does not mutate the fixture');
    const snapshot = reducer.snapshot(); snapshot.samples.length = 0;
    assert.equal(reducer.snapshot().samples.length, channel === 'ecg' ? 100 : 0, 'callers receive isolated snapshots');
    reducer.accept({ ...frame(id, 0), bootId: randomUUID() }, 50_000);
    assert.equal(reducer.snapshot().state, 'complete', 'late events cannot rewrite a terminal view');
  }
});

test('500 ms synthetic silence is terminal at equality and a 499 ms delivery delay cannot authorize a 500 ms late frame', () => {
  const id = identity(), first = new SyntheticSignalReducer(id, 0);
  first.accept(frame(id, 0, 0), 0, at);
  assert.doesNotThrow(() => first.tick(499));
  assert.throws(() => first.tick(500), fails('SYNTHETIC_STALE_SIGNAL'));
  assert.equal(first.snapshot().heartRateBpm, null);
  const delayed = new SyntheticSignalReducer(id, 0);
  assert.doesNotThrow(() => delayed.accept(frame(id, 0, 0), 499, at));
  assert.throws(() => delayed.accept(frame(id, 1, 0), 600, at), fails('SYNTHETIC_STALE_SIGNAL'));
});

test('all named fictional fault scenarios latch their exact reason, clear current BPM and reject later completion', () => {
  const expected: Record<Exclude<SyntheticSignalScenario, 'clean'>, string> = { poor_contact: 'SYNTHETIC_POOR_CONTACT', motion_artifact: 'SYNTHETIC_MOTION_ARTIFACT', lead_off: 'SYNTHETIC_LEAD_OFF', saturated: 'SYNTHETIC_SATURATED', transport_gap: 'SYNTHETIC_TRANSPORT_GAP', stale_signal: 'SYNTHETIC_STALE_SIGNAL', insufficient_samples: 'SYNTHETIC_INSUFFICIENT_SAMPLES' };
  for (const channel of ['ppg', 'ecg'] as const) for (const scenario of signalScenarios(channel).filter(x => x !== 'clean')) {
    const id = identity(channel, scenario), reducer = new SyntheticSignalReducer(id, 1000), end = channel === 'ecg' ? 40 : 30;
    assert.throws(() => {
      for (let i = 0; i <= end; i++) {
        const next = syntheticSignalFrame(id, i, 1000);
        if (!next) { reducer.tick(2500); break; }
        reducer.accept(next, 1000 + i * 100, at);
      }
    }, fails(expected[scenario]));
    const stopped = reducer.snapshot();
    assert.equal(stopped.reason, expected[scenario]); assert.equal(stopped.terminal, true); assert.equal(stopped.heartRateBpm, null); assert.equal(stopped.lastHeartRateBpm, 72);
    assert.throws(() => reducer.complete(1000, 5000, 5000), fails(expected[scenario]));
    if (scenario === 'poor_contact' || scenario === 'lead_off') assert.equal(stopped.contact, 'absent');
    if (scenario === 'transport_gap' && channel === 'ecg') assert.equal(stopped.droppedSamples, 5);
  }
});

test('stale identities, schema additions, sequence replay and bounded sample tampering cannot populate a current capture', () => {
  const changes: ((f: SyntheticSignalFrame) => SyntheticSignalFrame)[] = [
    f => ({ ...f, deviceId: 'SIM-OTHER' }), f => ({ ...f, bootId: randomUUID() }),
    ...(['sessionId', 'attemptId', 'captureId', 'workspaceEpoch'] as const).map(key => (f: SyntheticSignalFrame) => ({ ...f, context: { ...f.context, [key]: randomUUID() } })),
    f => ({ ...f, source: 'prototype_sensor' as 'simulated' }), f => ({ ...f, extra: true } as SyntheticSignalFrame),
    f => ({ ...f, samples: new Array(6).fill(0) }), f => ({ ...f, startedMonotonicMs: Number.NaN }),
    f => ({ ...f, elapsedMs: 1 }), f => ({ ...f, heartRateBpm: 999 }),
  ];
  for (const mutate of changes) {
    const id = identity(), reducer = new SyntheticSignalReducer(id, 1000);
    assert.throws(() => reducer.accept(mutate(frame(id, 0)), 1000), fails('SYNTHETIC_SIGNAL_INVALID'));
    assert.deepEqual(reducer.snapshot().samples, []);
  }
  const id = identity(), replay = new SyntheticSignalReducer(id, 1000);
  replay.accept(frame(id, 0), 1000);
  assert.throws(() => replay.accept(frame(id, 0), 1001), fails('SYNTHETIC_SIGNAL_INVALID'));
  const gap = new SyntheticSignalReducer(id, 1000); gap.accept(frame(id, 0), 1000);
  assert.throws(() => gap.accept(frame(id, 2), 1200), fails('SYNTHETIC_TRANSPORT_GAP'));
  for (const bad of [Number.NaN, Infinity, -1001, 1001, 1.25, 42]) {
    const reducer = new SyntheticSignalReducer(id, 1000); reducer.accept(frame(id, 0), 1000);
    const changed = frame(id, 1); changed.samples[0] = bad;
    assert.throws(() => reducer.accept(changed, 1100), fails('SYNTHETIC_SIGNAL_INVALID'));
  }
});

test('a missing final batch cannot be promoted by an otherwise matching transport completion', () => {
  const id = identity(), reducer = new SyntheticSignalReducer(id, 1000);
  for (let i = 0; i < 40; i++) reducer.accept(frame(id, i), 1000 + i * 100);
  assert.throws(() => reducer.complete(1000, 5000, 5000), fails('SYNTHETIC_INSUFFICIENT_SAMPLES'));
  assert.equal(reducer.snapshot().acceptedSamples, 195);
});

test('ECG display draws at most 99 contiguous segments and does not fill a gap, rescale units or change source samples', () => {
  const samples = Array.from({ length: 200 }, (_, i) => ({ index: i, elapsedMs: (i + 1) * 20, value: syntheticEcgSample(i) })), before = clone(samples);
  const segments = waveformSegments(samples, 320, 128);
  assert.equal(segments.length, 99); assert.equal(segments[0]!.key, '100:101');
  assert.ok(segments.every(s => Number.isFinite(s.left + s.top + s.width + s.angleRad)));
  const gapped = samples.slice(100); gapped.splice(30, 1);
  const withGap = waveformSegments(gapped, 320, 128);
  assert.equal(withGap.length, 97); assert.ok(!withGap.some(s => s.key === '129:131'));
  assert.deepEqual(samples, before);
  assert.deepEqual(waveformSegments(samples, 0, 128), []);
  assert.throws(() => assertSignalScenario('ppg', 'lead_off'), fails('SYNTHETIC_SCENARIO_UNAVAILABLE'));
  assert.throws(() => assertSignalScenario('ppg', 'saturated'), fails('SYNTHETIC_SCENARIO_UNAVAILABLE'));
});

test('typed signal failures settle only their exact simulated attempt with null physiology and existing scalar metadata', () => {
  const state = emptyWorkspace('guest', at), check = createCheck(state, { now: at, id: randomUUID, kind: 'engineering_fixture', contextConfirmed: true });
  const started = startAttempt(check, 'cardiac', at, randomUUID, 'simulated', 'synthetic_bench_v1', digest({ fixture: 'synthetic_bench_v1', channel: 'ecg' }), 'ecg');
  const id = identity('ecg', 'lead_off'); id.context = { sessionId: check.id, attemptId: started.attempt.attempt_id, captureId: started.attempt.record_id, workspaceEpoch: 'guest:current-epoch' };
  const error = new SyntheticSignalError('SYNTHETIC_LEAD_OFF', id, 'absent', 0), endedAt = '2026-10-11T18:00:01.200Z';
  const failure = getSyntheticSignalFailure(error, started.attempt, endedAt)!;
  assert.ok(failure); assert.equal(failure.projection.heart_rate_bpm, null); assert.equal(failure.projection.ecg_rmssd_ms, null); assert.equal(failure.projection.sample_rate_hz, null); assert.equal(failure.projection.raw_artifact_id, null);
  assert.deepEqual(failure.qualityFlags, ['SIMULATED', 'UNVERIFIED_DEVICE', 'SYNTHETIC_LEAD_OFF']);
  const settled = settleAttempt(started.check, started.attempt.attempt_id, failure.projection, 'invalid', endedAt, failure.qualityFlags, failure.metadata);
  assert.equal(settled.snapshot.cardiac.status, 'invalid'); assert.equal(settled.attempts.length, 1);
  assert.equal(settled.attempts[0]!.component_metadata.contact, 'absent');
  assert.equal(getSyntheticSignalFailure(new Error('not typed'), started.attempt, endedAt), null);
  assert.equal(getSyntheticSignalFailure(error, { ...started.attempt, source: 'prototype_sensor' }, endedAt), null);
  assert.equal(getSyntheticSignalFailure(error, { ...started.attempt, status: 'valid' }, endedAt), null);
  assert.equal(getSyntheticSignalFailure(error, { ...started.attempt, record_id: randomUUID() }, endedAt), null);
});

test('local ECG stream keeps the exact ten-message complete evidence and connection observation time separate from samples', async () => {
  const controller = new DeviceControllerImpl({ idFactory: randomUUID }, () => new LocalSimulatorTransport(randomUUID));
  const observedDuringFrames = new Set<string>();
  const unsubscribe = controller.subscribe(snapshot => { if (snapshot.captureInProgress && snapshot.signalPreview?.state === 'acquiring') observedDuringFrames.add(snapshot.observedAt); });
  try {
    await controller.useLocalSimulator();
    const result = await controller.captureSynthetic('ecg', identity().context);
    assert.equal(result.messages.length, 10);
    assert.deepEqual(result.messages.reduce<Record<string, number>>((counts, m) => { counts[m.type] = (counts[m.type] ?? 0) + 1; return counts; }, {}), { ack: 5, hello: 1, clock_sync: 3, capture_complete: 1 });
    assert.equal(canonicalJson(result.values), canonicalJson(syntheticValues('ecg')));
    const { evidenceSha256, ...payload } = result; assert.equal(evidenceSha256, digest(payload));
    assert.equal(controller.snapshot().signalPreview?.acceptedSamples, 200);
    assert.equal(controller.snapshot().signalPreview?.state, 'complete');
    assert.equal(observedDuringFrames.size, 1, 'sample updates do not falsify last connection observation');
    await controller.cancelCapture('WORKSPACE_CHANGED');
    assert.equal(controller.snapshot().signalPreview, null, 'even a completed display is cleared when its workspace is hidden');
  } finally { unsubscribe(); await controller.dispose(); }
});

test('runtime faults cancel the source, leave bounded stopped previews and allow a fresh clean attempt', async () => {
  await Promise.all((['poor_contact', 'motion_artifact', 'lead_off', 'saturated', 'transport_gap', 'stale_signal', 'insufficient_samples'] as const).map(async scenario => {
    const controller = new DeviceControllerImpl({ idFactory: randomUUID }, () => new LocalSimulatorTransport(randomUUID));
    try {
      await controller.useLocalSimulator(); const originalBoot = controller.snapshot().association!.bootId;
      await assert.rejects(controller.captureSynthetic('ecg', identity('ecg', scenario).context, { signalScenario: scenario }), error => error instanceof SyntheticSignalError);
      const ended = controller.snapshot(); assert.equal(ended.captureInProgress, false); assert.equal(ended.association, null); assert.equal(ended.state, 'error');
      assert.equal(ended.signalPreview?.terminal, true); assert.equal(ended.signalPreview?.heartRateBpm, null); assert.ok(ended.signalPreview!.samples.length <= 100);
      await controller.useLocalSimulator(); assert.notEqual(controller.snapshot().association!.bootId, originalBoot); assert.equal(controller.snapshot().signalPreview, null);
      const task = controller.captureSynthetic('ecg', identity().context);
      const canceled = assert.rejects(task, fails('WORKSPACE_CHANGED'));
      await controller.cancelCapture('WORKSPACE_CHANGED'); await canceled;
      assert.equal(controller.snapshot().signalPreview, null, 'workspace cancellation clears the old preview immediately');
    } finally { await controller.dispose(); }
  }));
});

test('nonclean preview options cannot enable a BLE preview or affect saliva capture', async () => {
  const transport = new LocalSimulatorTransport(randomUUID);
  // Deliberately classify the host transport as unprovisioned BLE to test the refusal boundary; no radio executes.
  Object.defineProperty(transport, 'kind', { value: 'ble_unprovisioned' });
  const controller = new DeviceControllerImpl({ idFactory: randomUUID }, () => transport);
  try {
    await controller.scan(); await controller.connect('local-simulator');
    const context = identity().context;
    await assert.rejects(controller.captureSynthetic('ecg', context, { signalScenario: 'lead_off' }), fails('SYNTHETIC_SCENARIO_REQUIRES_LOCAL_SIMULATOR'));
    await assert.rejects(controller.captureSynthetic('saliva', context, { signalScenario: 'clean' }), fails('SYNTHETIC_SCENARIO_UNAVAILABLE'));
    assert.equal(controller.snapshot().captureInProgress, false); assert.equal(controller.snapshot().signalPreview, null);
  } finally { await controller.dispose(); }
});
