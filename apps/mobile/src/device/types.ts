import type {
  ClockEvidence,
  DeviceChannel,
  DeviceEnvelope,
  SyntheticCapabilities,
} from "./protocol";
import type {
  SyntheticSignalFrame,
  SyntheticSignalOptions,
  SyntheticSignalPreview,
  SyntheticSignalScenario,
} from "./signal";
import type {
  AuthorizedReaderOptions,
  BindingTranscript,
  PhysicalCapabilities,
  PhysicalChannel,
  ReaderBinding,
  ReaderScope,
  SignedReaderCapture,
} from "./physicalProtocol";
export type DeviceState =
  | "unavailable"
  | "idle"
  | "scanning"
  | "connecting"
  | "connected_simulator"
  | "connected_reader"
  | "error";
export interface DiscoveredDevice {
  peripheralId: string;
  alias: string;
  rssi: number;
}
export interface DeviceAssociation {
  peripheralId: string;
  deviceId: string;
  bootId: string;
  hardwareRevision: string;
  firmwareVersion: string;
  protocolVersion: 1;
  source: "simulated" | "prototype_sensor";
  verifiedBindingId: string | null;
  transport: "ble_unprovisioned" | "local_simulator";
  capabilities: SyntheticCapabilities | PhysicalCapabilities;
}
export interface DeviceSnapshot {
  state: DeviceState;
  observedAt: string;
  devices: DiscoveredDevice[];
  association: DeviceAssociation | null;
  reason: string | null;
  captureInProgress: boolean;
  signalPreview: SyntheticSignalPreview | null;
  humanCaptureAvailable: boolean;
}
export interface CaptureContext {
  sessionId: string;
  attemptId: string;
  captureId: string;
  workspaceEpoch: string;
}
export interface SyntheticPpgValues {
  heart_rate_bpm: number;
  duration_seconds: number;
  method: "ppg";
}
export interface SyntheticEcgValues {
  heart_rate_bpm: number;
  duration_seconds: number;
  method: "ecg";
  sample_rate_hz: number;
  lead_count: 1;
  units: "arbitrary_counts";
  samples: number[];
}
export interface SyntheticAnalyte {
  analyte: "delta9_thc" | "11_hydroxy_thc" | "thc_cooh";
  qualifier: "quantified" | "not_detected";
  value: number | null;
  unit: "ng/mL";
  lod: number;
  loq: number;
  uloq: number;
}
export interface SyntheticSalivaValues {
  specimen: "oral_fluid";
  assay_id: "synthetic_assay_v1";
  analytes: SyntheticAnalyte[];
}
export interface SyntheticDeviceCapture {
  source: "simulated";
  channel: DeviceChannel;
  context: CaptureContext;
  association: DeviceAssociation;
  clockEvidence: ClockEvidence;
  startedAt: string;
  endedAt: string;
  deviceStartedMonotonicMs: number;
  deviceEndedMonotonicMs: number;
  values: SyntheticPpgValues | SyntheticEcgValues | SyntheticSalivaValues;
  fixtureId: "synthetic_bench_v1";
  messages: DeviceEnvelope[];
  evidenceSha256: string;
  qualityFlags: ["SIMULATED", "UNVERIFIED_DEVICE"];
  modelEligible: false;
}
export interface DeviceController {
  snapshot(): DeviceSnapshot;
  subscribe(listener: (snapshot: DeviceSnapshot) => void): () => void;
  scan(): Promise<void>;
  stopScan(): Promise<void>;
  connect(peripheralId: string): Promise<void>;
  disconnect(): Promise<void>;
  forget(): Promise<void>;
  useLocalSimulator(): Promise<void>;
  captureSynthetic(
    channel: DeviceChannel,
    context: CaptureContext,
    options?: SyntheticSignalOptions,
  ): Promise<SyntheticDeviceCapture>;
  requestBindingProof(
    transcript: BindingTranscript,
  ): Promise<{ signature: string }>;
  installBinding(receipt: ReaderBinding, scope: ReaderScope): void;
  prepareAuthorizedCapture(
    context: CaptureContext,
  ): Promise<{ device_boot_id: string; device_nonce: string }>;
  captureAuthorized(
    channel: PhysicalChannel,
    context: CaptureContext,
    options: AuthorizedReaderOptions,
  ): Promise<SignedReaderCapture>;
  cancelCapture(reason?: string): Promise<void>;
  dispose(): Promise<void>;
}
export interface DeviceControllerOptions {
  idFactory: () => string;
  onInvalidated?: (reason: string, context: CaptureContext | null) => void;
}

/** A transport has no trust authority. All packet semantics are checked in the bounded controller. */
export type TransportEvent =
  | { kind: "discovered"; peripheralId: string; alias: string; rssi: number }
  | { kind: "state"; state: string }
  | {
      kind: "packet";
      peripheralId: string;
      base64: string;
      receivedAtMonotonicMs: number;
    }
  | {
      kind: "synthetic_signal";
      peripheralId: string;
      frame: SyntheticSignalFrame;
      receivedAtMonotonicMs: number;
    }
  | { kind: "disconnected"; peripheralId: string; reason: string };
export interface DeviceTransport {
  kind: "ble_unprovisioned" | "local_simulator";
  available: boolean;
  now(): number;
  subscribe(listener: (event: TransportEvent) => void): () => void;
  scan(): Promise<void>;
  stopScan(): Promise<void>;
  connect(
    peripheralId: string,
  ): Promise<{ peripheralId: string; mtu: number; capabilities: string }>;
  write(base64: string): Promise<void>;
  prepareSyntheticSignal?(scenario: SyntheticSignalScenario): void;
  disconnect(): Promise<void>;
}
