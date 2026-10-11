import type { NativeSyntheticEvent, ViewProps } from 'react-native';

export const REACTION_CONFIGURATION_ID = 'choice_inhibit_v0_native_dev_1' as const;
export const REACTION_CONFIGURATION_SHA256 = '61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3' as const;
export type TaskSide = 'left' | 'right' | 'outside';
export type TaskStimulus = 'left' | 'right' | 'no_go';
export type TaskPhase = 'practice' | 'scored';
export type TaskOutcome = 'correct' | 'wrong_choice' | 'omission' | 'commission' | 'correct_withhold' | 'unresolved';
export type TaskCancelReason = 'USER_CANCELED' | 'ROUTE_HIDDEN' | 'WORKSPACE_CHANGED' | 'WITHDRAWAL' | 'BACKGROUND' | 'FOCUS_LOST' | 'VIEW_DETACHED' | 'LAYOUT_CHANGED';

/** All *Ms timing observations below are relative to nativeStartMs, unless explicitly absolute. */
export interface NativeTrialEvent {
  index: number;
  phase: TaskPhase;
  stimulus: TaskStimulus;
  plannedOnsetMs: number;
  onsetIntervalMs: number;
  presented: boolean;
  frameTimestampMs: number | null;
  callbackTimestampMs: number | null;
  onsetMs: number | null;
  onsetLatenessMs: number | null;
  outcome: TaskOutcome;
  selectedInputSequence: number | null;
  responseTimeMs: number | null;
  correctGoRtMs: number | null;
}
export interface NativeInputEvent {
  nativeTimestampMs: number;
  dispatchTimestampMs: number;
  dispatchDelayMs: number;
  target: TaskSide;
  pointerId: number;
  nativeSequence: number;
  inputKind: 'direct_touch' | 'unsupported';
  disposition: 'selected' | 'additional_response' | 'outside' | 'anticipatory' | 'late' | 'unsupported' | 'timing_fault';
  trialIndex: number | null;
  anticipatoryForTrialIndex: number | null;
}
export interface NativeTaskCounts {
  presentedPractice: number;
  presentedScored: number;
  presentedGo: number;
  presentedNoGo: number;
  completedScored: number;
  correctGo: number;
  omissions: number;
  wrongGo: number;
  noGoErrors: number;
  correctWithholds: number;
}
export interface NativeTaskFeatures {
  medianRtMs: number | null;
  iqrRtMs: number | null;
  p90RtMs: number | null;
  omissionRate: number;
  wrongGoRate: number;
  noGoErrorRate: number;
}
export interface NativeTaskTiming {
  clockDomain: 'android_uptime' | 'ios_uptime';
  inputTimestampMethod: 'motion_event_uptime_ms' | 'motion_event_uptime_nanos' | 'uitouch_timestamp';
  /** API numeric granularity where documented; null when unknown. Never physical accuracy. */
  inputTimestampResolutionMs: number | null;
  presentationEvidenceMethod: 'choreographer_frame_time_nanos' | 'cadisplaylink_target_timestamp';
  calibrationStatus: 'uncalibrated';
  physicalOnsetVerified: false;
  modelEligible: false;
  simulator: boolean;
  deviceModel: string;
  osVersion: string;
  nativeBuild: string;
  viewWidthPoints: number;
  viewHeightPoints: number;
  viewWidthPixels: number;
  viewHeightPixels: number;
  pixelDensity: number;
  orientation: 'portrait';
  fontFamily: string;
  textScale: 1;
  nominalRefreshHz: number;
  maxObservedFrameGapMs: number;
  maxObservedFrameDispatchMs: number;
  maxObservedInputDispatchMs: number;
  terminalCutoffMs: number | null;
  finalDrainMs: 100;
  overflowTriggerCount: number;
  utcAnchorMethod: 'start_utc_plus_monotonic_elapsed';
  observedEndedAt: string;
  observedWallClockDeltaMs: number;
  physicalLuminance: 'unmeasured';
}
export interface NativeTaskResult {
  schemaVersion: '1.0.0';
  taskVersion: 'choice_inhibit_v0';
  implementationVersion: '1.0.0';
  extractorVersion: 'choice_inhibit_features_1';
  status: 'valid' | 'invalid';
  source: 'native_task';
  platform: 'android' | 'ios';
  runId: string;
  workspaceEpoch: string;
  seed: number;
  configurationId: typeof REACTION_CONFIGURATION_ID;
  configurationSha256: typeof REACTION_CONFIGURATION_SHA256;
  scheduleSha256: string;
  startedAt: string;
  endedAt: string;
  nativeStartMs: number;
  nativeEndMs: number;
  durationMs: number;
  trialEvents: NativeTrialEvent[];
  inputEvents: NativeInputEvent[];
  counts: NativeTaskCounts;
  features: NativeTaskFeatures | null;
  qualityFlags: string[];
  timing: NativeTaskTiming;
}
export interface TaskProgress {
  runId: string;
  workspaceEpoch: string;
  phase: TaskPhase;
  presented: number;
  total: 66;
}
export interface ReactionTaskViewRef {
  /** Exact frozen completion also returned here, so navigation need not race event delivery. */
  cancel(runId: string, reason: TaskCancelReason): Promise<{ runId: string; status: 'stopped' | 'already_terminal'; result?: NativeTaskResult }>;
}
export interface ReactionTaskViewProps extends ViewProps {
  runId: string;
  seed: number;
  running: boolean;
  configurationId: string;
  configurationSha256: string;
  workspaceEpoch: string;
  onProgress?: (event: NativeSyntheticEvent<TaskProgress>) => void;
  onComplete: (event: NativeSyntheticEvent<NativeTaskResult>) => void;
}
export interface ReactionTaskAvailability {
  available: boolean;
  platform: 'android' | 'ios' | 'unavailable';
  configurationId: string;
  configurationSha256: string;
  modelEligible: false;
  reason: string | null;
}
