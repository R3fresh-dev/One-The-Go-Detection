import type { SyntheticSignalPreview, SyntheticSignalSample, SyntheticSignalScenario, SyntheticSignalState } from './signal';

export const SIGNAL_SCENARIO_LABELS: Record<SyntheticSignalScenario, string> = {
  clean: 'Clean fictional signal', poor_contact: 'Contact lost', motion_artifact: 'Motion artifact', lead_off: 'Electrode lead off', saturated: 'Saturated signal', transport_gap: 'Missing signal batch', stale_signal: 'Signal becomes stale', insufficient_samples: 'Insufficient samples',
};
export const SIGNAL_STATE_LABELS: Record<SyntheticSignalState, string> = {
  waiting_for_contact: 'Waiting for fictional contact', acquiring: 'Receiving fictional signal', poor_contact: 'Fictional contact lost', motion_artifact: 'Fictional motion artifact', lead_off: 'Fictional electrode lead off', saturated: 'Fictional signal saturated', transport_gap: 'Missing fictional signal batch', stale_signal: 'Fictional signal is stale', insufficient_valid_samples: 'Insufficient fictional samples', complete: 'Fictional capture complete', invalid: 'Fictional signal rejected',
};
export function signalRecovery(preview: SyntheticSignalPreview): string | null {
  if (!preview.reason) return null;
  const details: Partial<Record<SyntheticSignalState, string>> = {
    poor_contact: 'The contact-loss example ended this attempt.', motion_artifact: 'The motion example ended this attempt.', lead_off: 'The lead-off example ended this attempt. No electrode input was used.', saturated: 'The saturation example ended this attempt.', transport_gap: 'A signal interval is missing. The display did not fill the gap.', stale_signal: 'No acceptable new batch arrived within the 500 ms development window.', insufficient_valid_samples: 'The fixture did not provide the required complete sample sequence.', invalid: 'Signal identity, order, values or bounds did not match this fictional attempt.',
  };
  return `${details[preview.state] ?? 'This fictional attempt is invalid.'} Reconnect the local simulator, select a scenario, and start a new attempt. The ended attempt remains in the evidence ledger.`;
}
export interface WaveformSegment { key: string; left: number; top: number; width: number; angleRad: number }
/** Display-only two-second scrolling window. Never fills gaps or changes source samples. */
export function waveformSegments(samples: readonly SyntheticSignalSample[], width: number, height: number): WaveformSegment[] {
  if (!Number.isFinite(width + height) || width <= 0 || height <= 0) return [];
  const bounded = samples.slice(-100), last = bounded.at(-1);
  if (!last) return [];
  const endMs = Math.max(2000, last.elapsedMs), startMs = endMs - 2000;
  const x = (s: SyntheticSignalSample) => (s.elapsedMs - startMs) / 2000 * width;
  const y = (s: SyntheticSignalSample) => (1000 - s.value) / 2000 * height;
  const segments: WaveformSegment[] = [];
  for (let i = 1; i < bounded.length; i++) {
    const a = bounded[i - 1]!, b = bounded[i]!;
    if (![a.value, b.value, a.elapsedMs, b.elapsedMs].every(Number.isFinite) || a.value < -1000 || a.value > 1000 || b.value < -1000 || b.value > 1000 || b.index !== a.index + 1 || b.elapsedMs - a.elapsedMs !== 20 || a.elapsedMs < startMs || b.elapsedMs > endMs) continue;
    const x1 = x(a), x2 = x(b), y1 = y(a), y2 = y(b), length = Math.hypot(x2 - x1, y2 - y1);
    segments.push({ key: `${a.index}:${b.index}`, left: (x1 + x2 - length) / 2, top: (y1 + y2) / 2 - 1, width: length, angleRad: Math.atan2(y2 - y1, x2 - x1) });
  }
  return segments;
}
