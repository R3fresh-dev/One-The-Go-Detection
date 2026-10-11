import type { CaptureAttempt, JsonObject } from '../core/types';
import { SyntheticSignalError, SYNTHETIC_SIGNAL_CONFIGURATION } from './signal';

export interface SyntheticSignalFailure { projection: JsonObject; qualityFlags: string[]; metadata: JsonObject }

/** Maps only an exact local synthetic failure to an existing started cardiac attempt. */
export function getSyntheticSignalFailure(error: unknown, attempt: CaptureAttempt, endedAt: string): SyntheticSignalFailure | null {
  if (!(error instanceof SyntheticSignalError) || attempt.component !== 'cardiac' || attempt.source !== 'simulated' || attempt.status !== 'started' || error.identity.context.sessionId !== attempt.session_id || error.identity.context.attemptId !== attempt.attempt_id || error.identity.context.captureId !== attempt.record_id || error.identity.channel !== attempt.component_metadata.modality) return null;
  if (!Number.isFinite(Date.parse(endedAt)) || !attempt.started_at || !Number.isFinite(Date.parse(attempt.started_at)) || Date.parse(endedAt) < Date.parse(attempt.started_at)) return null;
  const qualityFlags = ['SIMULATED', 'UNVERIFIED_DEVICE', error.signalReason];
  return {
    projection: { status: 'invalid', source: 'simulated', started_at: attempt.started_at, ended_at: endedAt, quality_flags: qualityFlags, acquisition_config_id: attempt.configuration_id ?? 'unavailable', modality: error.identity.channel, heart_rate_bpm: null, ecg_status: error.identity.channel === 'ecg' ? 'invalid' : 'not_collected', ecg_rmssd_ms: null, sample_rate_hz: null, raw_artifact_id: null },
    qualityFlags,
    metadata: { fixture_id: SYNTHETIC_SIGNAL_CONFIGURATION.id, context: error.identity.scenario, contact: error.contact, dropped_samples: error.droppedSamples, sample_rate_hz: error.identity.channel === 'ecg' ? 50 : null },
  };
}
