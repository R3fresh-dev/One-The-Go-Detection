import { clone, digest, IntegrityError, knownKeys, requireObject, requiredString, safeInteger } from './integrity';
import { emptyProfile, validateProfileEnvelope, verifyCheck, verifyResult } from './domain';
import type { CaptureAttempt, CaptureContext, CheckRecord, EvidenceManifest, JsonObject, ProfileEnvelope, Snapshot, WorkspaceState } from './types';

export function parseProfile(value: unknown, etag: string | null, now: string): ProfileEnvelope {
  const v = requireObject(value); knownKeys(v, ['profile_version_id', 'revision', 'profile', 'history', 'context']);
  const revision = safeInteger(v.revision); if (!etag || etag !== `"${revision}"`) throw new IntegrityError('PROFILE_ETAG_MISMATCH', 'The profile version could not be verified.');
  const empty = emptyProfile(now);
  if (v.profile === null) return { ...empty, revision, etag, sync: 'synced' };
  const profile = requireObject(v.profile), history = requireObject(v.history);
  knownKeys(profile, ['age_years', 'height_cm', 'weight_kg', 'bmi', 'recorded_at', 'source']);
  knownKeys(history, ['use_frequency', 'route', 'time_since_use_min', 'recent_exercise', 'sleep_hours', 'alcohol_co_use']);
  const parsed: ProfileEnvelope = { profile_version_id: v.profile_version_id === null ? null : requiredString(v.profile_version_id), revision, etag, profile: clone(profile) as unknown as ProfileEnvelope['profile'], history: clone(history) as unknown as ProfileEnvelope['history'], context: v.context ? clone(v.context) as ProfileEnvelope['context'] : empty.context, sync: 'synced' };
  validateProfileEnvelope(parsed); return parsed;
}
export function parseRemoteCheck(value: unknown, state: WorkspaceState): CheckRecord {
  const v = requireObject(value);
  knownKeys(v, ['session_id', 'state', 'revision', 'mode', 'created_at', 'snapshot_sha256', 'evidence_sha256', 'result', 'snapshot', 'context', 'manifest', 'attempts', 'alcohol', 'raw_artifacts_omitted_reason']);
  const id = requiredString(v.session_id), snapshot = v.snapshot as Snapshot, context = v.context as CaptureContext, manifest = v.manifest as EvidenceManifest;
  if (!snapshot || !context || !manifest || !Array.isArray(v.attempts)) throw new IntegrityError('REMOTE_EVIDENCE_INCOMPLETE', 'The full check evidence is not available on this device. The server record is preserved; retry its detail request.');
  const check: CheckRecord = { id, generation: state.generation, workspace: state.workspace, kind: v.mode === 'synthetic' ? 'engineering_fixture' : 'measurement', stage: 'review', frozen: true, snapshot, context, attempts: v.attempts as CaptureAttempt[], manifest, snapshot_sha256: requiredString(v.snapshot_sha256), evidence_sha256: requiredString(v.evidence_sha256), result: null, alcohol: v.alcohol as JsonObject | null, delivery: v.result ? 'synced' : 'awaiting_result', error: null, remote_revision: safeInteger(v.revision, 1), remote_etag: `"${v.revision}"`, updated_at: requiredString(v.created_at) };
  if (snapshot.subject_ref !== state.capabilities?.account_ref) throw new IntegrityError('REMOTE_OWNER_MISMATCH', 'The check is not owned by the active account.');
  if (v.result) check.result = verifyResult(v.result, check);
  verifyCheck(check); return check;
}
export function profileBody(profile: ProfileEnvelope): JsonObject { return clone({ profile: profile.profile, history: profile.history, context: profile.context }) as unknown as JsonObject; }
export function sameFrozenEvidence(a: CheckRecord, b: CheckRecord): boolean { return a.snapshot_sha256 === b.snapshot_sha256 && a.evidence_sha256 === b.evidence_sha256 && digest(a.context) === digest(b.context); }
