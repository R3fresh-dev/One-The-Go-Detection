import type { SyntheticDeviceCapture, SyntheticEcgValues, SyntheticPpgValues, SyntheticSalivaValues } from '../device/types';
import { digest, IntegrityError } from './integrity';
import type { CaptureAttempt, IdFactory, JsonObject } from './types';

/** Transport evidence never establishes human-device trust or clinical eligibility. */
export function projectSyntheticDevice(capture: SyntheticDeviceCapture, attempt: CaptureAttempt, id: IdFactory): JsonObject {
  if (capture.source !== 'simulated' || capture.modelEligible !== false || capture.context.attemptId !== attempt.attempt_id || capture.context.sessionId !== attempt.session_id || capture.context.captureId !== attempt.record_id) throw new IntegrityError('DEVICE_CAPTURE_LINKAGE', 'The simulator response does not match this capture.');
  const base: JsonObject = { status: 'valid', source: 'simulated', started_at: capture.startedAt, ended_at: capture.endedAt, quality_flags: capture.qualityFlags };
  if (capture.channel === 'saliva') {
    const values = capture.values as SyntheticSalivaValues, sampleId = attempt.record_id, names = { delta9_thc: 'THC', '11_hydroxy_thc': 'OH11_THC', thc_cooh: 'THC_COOH' };
    return { sample: { sample_id: sampleId, collection_method_id: values.assay_id, collected_at: capture.startedAt, volume_ml: 1, dilution_factor: 1, status: 'valid', quality_flags: capture.qualityFlags }, saliva: values.analytes.map(x => ({ schema_version: '0.1.0', measurement_id: id(), sample_id: sampleId, analyte: names[x.analyte], qualifier: x.qualifier, value_ng_ml: x.qualifier === 'quantified' ? x.value : null, unit: 'ng/mL', assay_basis: 'free', limits: { lod_ng_ml: x.lod, loq_ng_ml: x.loq, upper_ng_ml: x.uloq }, source: 'simulated', method_id: values.assay_id, calibration_id: 'synthetic-calibration-v1', cartridge_lot: 'SYNTHETIC-LOT', instrument_id: capture.association.deviceId, operator_ref: null, collected_at: capture.startedAt, measured_at: capture.endedAt, quality_flags: capture.qualityFlags, original_report: { value: x.value, unit: x.unit, qualifier: x.qualifier }, uncertainty_ng_ml: null, concentration_basis: 'neat_oral_fluid', correction_status: 'not_corrected' })) };
  }
  const values = capture.values as SyntheticPpgValues | SyntheticEcgValues;
  return { ...base, acquisition_config_id: capture.fixtureId, modality: capture.channel, heart_rate_bpm: values.heart_rate_bpm, ecg_status: capture.channel === 'ecg' ? 'valid' : 'not_collected', ecg_rmssd_ms: null, sample_rate_hz: capture.channel === 'ecg' ? (values as SyntheticEcgValues).sample_rate_hz : null, raw_artifact_id: null };
}
export function syntheticConfigurationDigest(channel: string): string { return digest({ fixture: 'synthetic_bench_v1', channel }); }
