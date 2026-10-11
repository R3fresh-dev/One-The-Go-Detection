import type { DeviceChannel } from './protocol';
import type { SyntheticEcgValues, SyntheticPpgValues, SyntheticSalivaValues } from './types';

/** Exact pre-existing bench fixture; these counts are unrelated to the fictional BPM. */
export function syntheticEcgSample(index: number): number {
  if (!Number.isInteger(index) || index < 0 || index >= 200) throw new RangeError('Synthetic ECG sample index');
  const p = index % 42;
  return p === 10 ? 800 : p === 11 ? -250 : p >= 20 && p <= 25 ? (p <= 22 ? p - 19 : 26 - p) * 25 : p >= 4 && p <= 6 ? 30 : 0;
}

export function syntheticValues(channel: DeviceChannel): SyntheticPpgValues | SyntheticEcgValues | SyntheticSalivaValues {
  if (channel === 'ppg') return { heart_rate_bpm: 72, duration_seconds: 3, method: 'ppg' };
  if (channel === 'ecg') return { heart_rate_bpm: 72, duration_seconds: 4, method: 'ecg', sample_rate_hz: 50, lead_count: 1, units: 'arbitrary_counts', samples: Array.from({ length: 200 }, (_, i) => syntheticEcgSample(i)) };
  return { specimen: 'oral_fluid', assay_id: 'synthetic_assay_v1', analytes: [
    { analyte: 'delta9_thc', qualifier: 'quantified', value: 12, unit: 'ng/mL', lod: 1, loq: 2, uloq: 100 },
    { analyte: '11_hydroxy_thc', qualifier: 'not_detected', value: null, unit: 'ng/mL', lod: 1, loq: 2, uloq: 100 },
    { analyte: 'thc_cooh', qualifier: 'not_detected', value: null, unit: 'ng/mL', lod: 1, loq: 2, uloq: 100 },
  ] };
}
