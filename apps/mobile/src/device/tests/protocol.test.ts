import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { canonicalJson, utf8 } from '../../core/integrity';
import { capabilities, clockExchange, crc32, decodeUtf8, DeviceError, fragmentMessage, fromBase64, MessageJournal, Reassembler, selectClock, toBase64 } from '../protocol';
import type { DeviceEnvelope } from '../protocol';
import { DeviceControllerImpl } from '../controller';
import { LocalSimulatorTransport } from '../simulator';

const ids = { deviceId: 'SIM-TEST-01', bootId: '11111111-1111-4111-8111-111111111111', sessionId: '22222222-2222-4222-8222-222222222222' };
function message(sequence = 0): DeviceEnvelope { return { protocol_version: 1, message_id: randomUUID(), device_id: ids.deviceId, boot_id: ids.bootId, session_id: ids.sessionId, sequence, monotonic_ms: 500, type: 'hello', payload: { deadline_after_ms: 120_000 } }; }
function fails(code: string): (error: unknown) => boolean { return error => error instanceof DeviceError && error.code === code; }

test('CRC uses CRC-32/ISO-HDLC public check vector', () => { assert.equal(crc32(utf8('123456789')), 0xcbf43926); });
test('ATT MTU 23 carries eight logical bytes after the 12-byte header', () => {
  const input = message(), frames = fragmentMessage(input, 15, 20), receiver = new Reassembler(20);
  assert.ok(frames.length > 1); assert.equal(frames[0]!.length, 20);
  let decoded: DeviceEnvelope | null = null;
  frames.forEach((frame, i) => { const value = receiver.push(frame, i); if (value) decoded = value; });
  assert.deepEqual(decoded, input);
});
test('larger MTU, out-of-order fragments and identical duplicate reconstruct once', () => {
  const input = message(), frames = fragmentMessage(input, 42, 97), receiver = new Reassembler(97);
  assert.equal(receiver.push(frames[1]!, 0), null); assert.equal(receiver.push(frames[1]!, 1), null);
  let count = 0;
  for (const frame of frames) if (receiver.push(frame, 2)) count++;
  assert.equal(count, 1); for (const frame of frames) assert.equal(receiver.push(frame, 3), null);
});
test('corruption and conflicting duplicates fail closed and release in-progress storage', () => {
  const frames = fragmentMessage(message(), 7), receiver = new Reassembler();
  receiver.push(frames[0]!, 0); const changed = frames[0]!.slice(); changed[12] = changed[12]! ^ 1;
  assert.throws(() => receiver.push(changed, 1), fails('CONFLICTING_DUPLICATE_FRAGMENT'));
  const corrupt = frames.map(frame => frame.slice()); corrupt[1]![12] = corrupt[1]![12]! ^ 1;
  assert.throws(() => { corrupt.forEach((frame, i) => receiver.push(frame, i + 10)); }, fails('CRC_MISMATCH'));
  let restored: DeviceEnvelope | null = null; frames.forEach((frame, i) => { restored = receiver.push(frame, i + 100) ?? restored; }); assert.ok(restored);
});
test('impossible counts, encodings and excess MTU are rejected before allocation', () => {
  const frame = fragmentMessage(message(), 1)[0]!.slice();
  const wrong = frame.slice(); wrong[1] = 2; assert.throws(() => new Reassembler().push(wrong, 0), fails('FRAGMENT_VERSION'));
  new DataView(frame.buffer).setUint16(8, 65535, true); assert.throws(() => new Reassembler().push(frame, 0), fails('FRAGMENT_BOUNDS'));
  assert.throws(() => new Reassembler().push(new Uint8Array(21), 0), fails('FRAGMENT_LENGTH'));
});
test('one transfer at a time and the 120-second assembly deadline are enforced', () => {
  const a = fragmentMessage(message(), 1), b = fragmentMessage(message(), 2), receiver = new Reassembler();
  receiver.push(a[0]!, 0); assert.throws(() => receiver.push(b[0]!, 1), fails('CONCURRENT_TRANSFER'));
  receiver.push(a[0]!, 2); assert.throws(() => receiver.expire(120_003), fails('REASSEMBLY_TIMEOUT'));
  assert.equal(receiver.push(b[0]!, 120_004), null);
});
test('message and base64 limits reject unbounded or noncanonical input', () => {
  const huge = message(); huge.payload.pad = 'x'.repeat(8192);
  assert.throws(() => fragmentMessage(huge, 1), fails('MESSAGE_TOO_LARGE'));
  assert.throws(() => fromBase64('YQ==\n'), fails('INVALID_BASE64'));
  assert.throws(() => fromBase64('YR=='), fails('INVALID_BASE64'));
  const bytes = Uint8Array.from([0, 1, 2, 254, 255]); assert.deepEqual(fromBase64(toBase64(bytes)), bytes);
});
test('UTF-8 decoder rejects overlong, surrogate, truncated and out-of-range sequences', () => {
  assert.equal(decodeUtf8(utf8('Clock μs 😀')), 'Clock μs 😀');
  for (const bytes of [[0xc0, 0xaf], [0xed, 0xa0, 0x80], [0xf0, 0x9f], [0xf4, 0x90, 0x80, 0x80]]) assert.throws(() => decodeUtf8(Uint8Array.from(bytes)), fails('INVALID_UTF8'));
});
test('capability source and calibration cannot promote an unprovisioned peripheral', () => {
  const cap = { protocol_version: 1, encodings: [1], max_logical_bytes: 8192, max_att_bytes: 20, source: 'simulated', device_id: 'SIM-TEST-01', boot_id: ids.bootId, hardware_revision: 'nano_esp32', firmware_version: '1.0.0', channels: ['ppg'], configuration_id: 'synthetic_bench_v1', calibration_status: 'not_applicable', timestamp_resolution_ms: 1 };
  assert.equal(capabilities(canonicalJson(cap)).source, 'simulated');
  assert.throws(() => capabilities(canonicalJson({ ...cap, source: 'validated_sensor' })), fails('UNVERIFIED_HUMAN_HARDWARE'));
  assert.throws(() => capabilities(canonicalJson({ ...cap, protocol_version: 2 })), fails('UNSUPPORTED_PROTOCOL'));
  assert.throws(() => capabilities(canonicalJson(cap).replace('"source":"simulated"', '"source":"simulated","source":"simulated"')));
});
test('identity, changed message ID content and replay sequence are independently checked', () => {
  const journal = new MessageJournal(), a = message();
  assert.equal(journal.accept(a, ids), 'new'); assert.equal(journal.accept(a, ids), 'duplicate');
  assert.throws(() => journal.accept({ ...a, payload: {} }, ids), fails('MESSAGE_ID_CONFLICT'));
  assert.throws(() => journal.accept(message(), ids), fails('SEQUENCE_REPLAY'));
  assert.throws(() => journal.accept({ ...message(1), boot_id: randomUUID() }, ids), fails('IDENTITY_MISMATCH'));
  assert.throws(() => journal.accept({ ...message(1), session_id: randomUUID() }, ids), fails('IDENTITY_MISMATCH'));
  assert.equal(journal.accept(message(1), ids), 'new');
});
test('bounded replay journal refuses exhaustion without evicting prior identities', () => {
  const journal = new MessageJournal(1), a = message(); journal.accept(a, ids);
  assert.throws(() => journal.accept(message(1), ids), fails('REPLAY_JOURNAL_FULL')); assert.equal(journal.accept(a, ids), 'duplicate');
});
test('clock evidence retains all exchanges and chooses narrowest interval with resolution padding', () => {
  const exchanges = [clockExchange(100, 155, 157, 112, 1, 1), clockExchange(200, 253, 254, 208, 1, 1), clockExchange(300, 354, 356, 310, 1, 1)];
  const result = selectClock(exchanges, ids.bootId); assert.equal(result.selected_exchange, 1); assert.equal(result.exchanges.length, 3);
  assert.equal(result.offset_ms, 49.5); assert.equal(result.uncertainty_ms, 5.5); assert.equal(result.calibrated, false);
  assert.throws(() => clockExchange(100, 100, 200, 110, 1, 1), fails('CLOCK_INTERVAL_EMPTY'));
  assert.throws(() => clockExchange(110, 100, 100, 100, 1, 1), fails('CLOCK_DISCONTINUITY'));
});
test('local simulator exercises handshake, clocks, full framed capture and explicit simulated provenance', async () => {
  const controller = new DeviceControllerImpl({ idFactory: randomUUID }, () => new LocalSimulatorTransport(randomUUID));
  try {
    await controller.useLocalSimulator(); assert.equal(controller.snapshot().state, 'connected_simulator');
    const context = { sessionId: randomUUID(), attemptId: randomUUID(), captureId: randomUUID(), workspaceEpoch: 'guest:1' };
    const result = await controller.captureSynthetic('ppg', context);
    assert.equal(result.source, 'simulated'); assert.equal(result.modelEligible, false); assert.equal(result.association.verifiedBindingId, null);
    assert.deepEqual(result.context, context); assert.equal(result.clockEvidence.exchanges.length, 3); assert.equal(result.messages.at(-1)!.type, 'capture_complete');
    assert.deepEqual(result.values, { heart_rate_bpm: 72, duration_seconds: 3, method: 'ppg' });
    assert.equal(result.evidenceSha256.length, 64); assert.equal(controller.snapshot().captureInProgress, false);
  } finally { await controller.dispose(); }
});
test('cancellation invalidates before disconnect and prevents stale completion into a different workspace', async () => {
  let invalidated = false;
  const controller = new DeviceControllerImpl({ idFactory: randomUUID, onInvalidated(reason, context) { assert.equal(reason, 'WORKSPACE_CHANGED'); assert.equal(context?.workspaceEpoch, 'old:1'); invalidated = true; } }, () => new LocalSimulatorTransport(randomUUID));
  try {
    await controller.useLocalSimulator();
    const task = controller.captureSynthetic('ecg', { sessionId: randomUUID(), attemptId: randomUUID(), captureId: randomUUID(), workspaceEpoch: 'old:1' });
    const assertion = assert.rejects(task, fails('WORKSPACE_CHANGED'));
    const stopped = controller.cancelCapture('WORKSPACE_CHANGED');
    assert.equal(invalidated, true); assert.equal(controller.snapshot().captureInProgress, false);
    await stopped; await assertion; assert.equal(controller.snapshot().association, null);
  } finally { await controller.dispose(); }
});
