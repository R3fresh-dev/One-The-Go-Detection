import type { RawArtifact } from "./rawArtifacts";
import type { AcquisitionLedger } from "./acquisition";
import type { LabCollectionLedger } from "./participantAcquisition";
import type { RawRecordingStatus, RawKind } from "./rawRecordings";
import type { ReplacementLinksCache } from "./replacements";
import type { ReportCache } from "./reportRevisions";
export type Environment = "local" | "qa" | "prod" | "test";
export type Json =
  null | boolean | number | string | Json[] | { [key: string]: Json };
export type JsonObject = { [key: string]: Json };
export type Source =
  "simulated" | "prototype_sensor" | "reference_lab" | "validated_sensor";
export type Channel = "saliva" | "eyes" | "cardiac" | "task" | "alcohol";
export type MeasurementStatus = "valid" | "invalid" | "not_collected";
export type Route =
  | "welcome"
  | "notice"
  | "home"
  | "profile"
  | "device"
  | "check"
  | "result"
  | "history"
  | "evidence"
  | "settings"
  | "privacy"
  | "export"
  | "studies"
  | "raw-recordings"
  | "alcohol"
  | "about"
  | "status";
export type Stage =
  | "profile"
  | "device"
  | "saliva"
  | "eyes"
  | "cardiac"
  | "ecg"
  | "task"
  | "review";
export type UseFrequency =
  "never" | "occasional" | "frequent" | "daily" | "unknown" | "declined";
export interface Profile {
  age_years: number | null;
  height_cm: number | null;
  weight_kg: number | null;
  bmi: number | null;
  recorded_at: string;
  source: "self_report" | "synthetic" | "study_measurement";
}
export interface HistoryContext {
  use_frequency: UseFrequency;
  route: "inhaled" | "oral" | "other" | "unknown" | "declined";
  time_since_use_min: number | null;
  recent_exercise: boolean | null;
  sleep_hours: number | null;
  alcohol_co_use: "reported" | "not_reported" | "unknown" | "declined";
}
export interface SelfReportContext {
  last_use_status: "known" | "unknown" | "declined";
  last_use_at: string | null;
  confirmed_at: string;
}
export interface ProfileEnvelope {
  profile_version_id: string | null;
  revision: number;
  profile: Profile;
  history: HistoryContext;
  context: SelfReportContext;
  etag: string;
  sync: "local" | "queued" | "synced" | "conflict";
}
export interface Component extends JsonObject {
  status: MeasurementStatus;
  source: Source;
  started_at: string | null;
  ended_at: string | null;
  quality_flags: string[];
}
export interface Sample extends JsonObject {
  sample_id: string;
  collection_method_id: string;
  collected_at: string | null;
  volume_ml: number | null;
  dilution_factor: number | null;
  status: MeasurementStatus;
  quality_flags: string[];
}
export interface Snapshot {
  schema_version: "0.1.0";
  session_id: string;
  supersedes_session_id: string | null;
  mode: "synthetic" | "analytical" | "controlled_research";
  subject_ref: string;
  study_id: string | null;
  protocol_id: string | null;
  created_at: string;
  target_at: string;
  capture_completed_at: string;
  clock_uncertainty_ms: number | null;
  acquisition_span_ms: number | null;
  device: {
    device_id: string;
    boot_id: string;
    hardware_revision: string;
    firmware_version: string;
  };
  profile: Profile;
  history: HistoryContext;
  baseline_ref: string | null;
  sample: Sample;
  saliva: JsonObject[];
  eyes: Component;
  cardiac: Component;
  task: Component;
}
export interface CaptureContext {
  schema_version: "1.0.0";
  session_id: string;
  context_confirmed_at: string;
  profile_version_id: string | null;
  profile_snapshot_sha256: string;
  history_snapshot_sha256: string;
  protocol_id: string | null;
  configuration_refs: JsonObject[];
  baseline_refs: string[];
  device_associations: JsonObject[];
  self_report_context: SelfReportContext;
}
export interface CaptureAttempt {
  schema_version: "1.0.0";
  session_id: string;
  attempt_id: string;
  component: Channel;
  record_id: string;
  supersedes_attempt_id: string | null;
  status: "started" | "valid" | "invalid" | "canceled" | "not_collected";
  source: Source;
  started_at: string | null;
  ended_at: string | null;
  configuration_id: string | null;
  configuration_hash: string | null;
  quality_flags: string[];
  component_metadata: JsonObject;
  artifact_refs: string[];
  attestation_refs: string[];
}
export interface EvidenceManifest {
  schema_version: "1.0.0";
  session_id: string;
  context_sha256: string;
  attempts: { attempt_id: string; sha256: string }[];
  selected: Record<Channel, string | null>;
}
export interface LegacyMeasurementResult {
  schema_version: "0.1.0";
  result_id: string;
  session_id: string;
  state: "measurement_only" | "invalid" | "inconclusive";
  target_at: string;
  evaluated_at: string;
  model_id: null;
  model_lifecycle: null;
  endpoint_id: null;
  probability: null;
  classification: null;
  operating_threshold: null;
  uncertainty_policy_id: null;
  reason_codes: string[];
  input_sha256: string;
  provenance_summary: Source[];
  replaces_result_id: string | null;
}
export interface ResearchExecution {
  schema_version: "1.0.0";
  registry_id: string;
  registry_version: string;
  manifest_sha256: string;
  model_artifact_sha256: string;
  evaluation_report_sha256: string;
  feature_version: string;
  feature_values_sha256: string;
  calibration_id: string;
  calibration_sha256: string;
  capture_context_sha256: string;
  evidence_manifest_sha256: string;
  baseline_sha256: string | null;
  authority_sha256: string;
  endpoint_definition: string;
  population_description: string;
  authority_manifest: {
    schema_version: "1.0.0";
    model_manifest: JsonObject;
    model_registry_sha256: string;
    model_registry_version: string;
    model_artifact_sha256: string;
    evaluation_report_sha256: string;
    calibration_sha256: string;
    quality_policy_sha256: string;
    co_use_policy_sha256: string;
    native_timing_calibration_sha256: string;
    compatibility_policy_sha256: string;
    study_approval_sha256: string;
    consent_sha256: string;
    registry_events_sha256: string;
    cardiac_authority?: JsonObject;
  };
}
export interface ResearchResult extends Omit<
  LegacyMeasurementResult,
  | "schema_version"
  | "state"
  | "model_id"
  | "model_lifecycle"
  | "endpoint_id"
  | "probability"
  | "classification"
  | "operating_threshold"
  | "uncertainty_policy_id"
> {
  schema_version: "1.1.0";
  state: "research_estimate" | "inconclusive";
  model_id: string;
  model_lifecycle: "active_research";
  endpoint_id: string;
  probability: number | null;
  classification: "above_threshold" | "below_threshold" | null;
  operating_threshold: number | null;
  uncertainty_policy_id: string;
  model_execution: ResearchExecution;
}
export type MeasurementResult = LegacyMeasurementResult | ResearchResult;
export type DeliveryState =
  | "local_draft"
  | "local_finalized"
  | "queued"
  | "registering"
  | "uploading_evidence"
  | "uploading_snapshot"
  | "finalizing"
  | "awaiting_result"
  | "synced"
  | "retry_wait"
  | "auth_required"
  | "blocked"
  | "conflict"
  | "quarantined";
export interface CheckRecord {
  id: string;
  generation: number;
  workspace: string;
  kind: "guest_demo" | "engineering_fixture" | "measurement";
  stage: Stage;
  frozen: boolean;
  replacement_links?: ReplacementLinksCache;
  report_revision_cache?: ReportCache;
  snapshot: Snapshot;
  context: CaptureContext;
  attempts: CaptureAttempt[];
  /** Local draft choice; null with two valid cardiac alternatives requires Review selection. */
  selected_cardiac_attempt_id?: string | null;
  acquisition?: AcquisitionLedger;
  labCollection?: LabCollectionLedger;
  instruction_receipts?: JsonObject[];
  collections?: JsonObject[];
  collection_abandons?: JsonObject[];
  attestations?: Record<string, JsonObject>;
  manifest: EvidenceManifest | null;
  snapshot_sha256: string | null;
  evidence_sha256: string | null;
  result: MeasurementResult | null;
  alcohol: JsonObject | null;
  delivery: DeliveryState;
  error: string | null;
  remote_revision: number;
  remote_etag: string;
  updated_at: string;
}
export interface NoticeRef {
  version: string;
  sha256: string;
  locale: "en";
  content_path: string;
  mandatory: boolean;
  acknowledged?: boolean;
}
export interface NoticeContent {
  version: string;
  sha256: string;
  locale: "en";
  content_type: "text/plain";
  text: string;
  mandatory: boolean;
}
export interface AppConfig {
  schema_version: "1.0.0";
  environment: Environment;
  inference_available: false;
  notice: NoticeRef;
  auth: {
    issuer: string;
    client_id: string;
    authorization_endpoint: string;
    token_endpoint: string;
    revocation_endpoint?: string;
    logout_endpoint?: string;
    redirect_uris: string[];
  };
  maintenance: boolean;
  minimum_app_version: string;
  supported_app_versions: string[];
  contract_versions: {
    application: string[];
    scientific: string[];
    capture_evidence: string[];
    native_task: string[];
    research_result?: string[];
  };
  limits: JsonObject;
}
export interface Capabilities {
  account_ref: string;
  data_generation: number;
  account_state: "active" | "deleting" | "awaiting_generation_ack" | "deleted";
  server_time: string;
  notice: NoticeRef;
  inference_available: boolean;
  model_execution_supported?: boolean;
  model_reason_codes?: string[];
  channels: Record<
    string,
    {
      available: boolean;
      reason_codes: string[];
      authorization_available?: boolean;
      software_available?: boolean;
      configurations?: {
        study_id: string;
        protocol_id: string;
        configuration_id: string;
        configuration_hash: string;
        configuration_version: string;
        submitted_sha256: string;
        expires_at: string;
        supported_phone_models: string[];
        supported_os_versions?: string[];
        supported_native_builds?: string[];
        software_adapter_id: string;
        participant_protocol?: JsonObject | null;
        participant_protocol_sha256?: string | null;
      }[];
      configuration_id?: string;
      configuration_sha256?: string;
    }
  >;
  studies: JsonObject[];
}
export interface Identity {
  accountRef: string;
  issuer: string;
  generation: number;
  state: Capabilities["account_state"];
  verifiedAt: string;
}
export interface Preferences {
  theme: "system" | "light" | "dark";
  reducedMotion: boolean;
  units: "metric" | "imperial";
  retryQueuedAutomatically: boolean;
}
export type ExportSelection = {
  kind: "single" | "selected" | "all";
  session_ids: string[];
};
export interface ExportEntry {
  source: "device" | "cloud";
  selection: ExportSelection;
}
export interface PrivacyJob {
  schema_version: "1.0.0";
  kind: "export" | "deletion";
  job_id: string;
  scope: string | JsonObject;
  data_generation: number;
  state:
    | "pending"
    | "running"
    | "completed"
    | "failed"
    | "expired"
    | "revoked"
    | "partially_retained";
  accepted_at: string;
  started_at?: string;
  completed_at?: string;
  expires_at?: string;
  failure_code?: string;
  retained_categories: JsonObject[];
  policy_version: string;
  attempt_count: number;
  allowed_actions: string[];
  download_path?: string;
  manifest_sha256?: string;
  sha256?: string;
  size_bytes?: number;
  raw_export?: JsonObject;
}
export interface QueueOperation {
  id: string;
  kind:
    | "check"
    | "profile"
    | "withdrawal"
    | "deletion"
    | "export"
    | "consent"
    | "raw_preference"
    | "raw_revocation"
    | "device_unbind"
    | "acknowledgment";
  generation: number;
  check_id: string | null;
  body: JsonObject;
  state: DeliveryState;
  keys: Record<string, string>;
  attempts: number;
  next_attempt_at: string | null;
  error: string | null;
  created_at: string;
  phase: number;
}
export interface WorkspaceState {
  schema_version: 1;
  workspace: string;
  generation: number;
  profile: ProfileEnvelope;
  checks: CheckRecord[];
  queue: QueueOperation[];
  preferences: Preferences;
  notice: NoticeContent | null;
  acknowledgedNotice: string | null;
  jobs: PrivacyJob[];
  capabilities: Capabilities | null;
  exportEntry: ExportEntry | null;
  studies: JsonObject[];
  deviceBindings?: JsonObject[];
  deviceBindingIntent?: {
    device_id: string;
    key_id: string;
    challenge_key: string;
    completion_key: string;
    challenge: JsonObject | null;
    signature: string | null;
  };
  rawArtifacts?: RawArtifact[];
  rawExportAuthorities?: import("./rawExport").RawExportAuthority[];
  rawExportArtifactCursors?: Record<string, string | null>;
  rawExportNextCursor?: string | null;
  rawRecordingStatuses: Record<string, RawRecordingStatus>;
  rawRecordingFences: Record<string, RawKind[]>;
  historyIndex: JsonObject[];
  historyCursor: string | null;
}
export type IdFactory = () => string;
