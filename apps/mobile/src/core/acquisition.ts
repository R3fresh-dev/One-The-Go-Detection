import { verifyRawPermission } from "./rawArtifacts";
import type { RawKind, RawRecordingStatus } from "./rawRecordings";
import {
  clone,
  digest,
  IntegrityError,
  knownKeys,
  requireObject,
  requiredString,
  safeInteger,
} from "./integrity";
import type { Capabilities, CheckRecord, JsonObject } from "./types";

export type AcquisitionChannel =
  "saliva" | "eyes" | "cardiac" | "ecg" | "task" | "alcohol";
export interface ApprovedConfiguration {
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
}
export interface AcquisitionLedger {
  register_key: string;
  context_key: string;
  registered: boolean;
  context_registered: boolean;
  attempts: Record<
    string,
    {
      start_key: string;
      grant_key: string;
      invoke_key: string;
      terminal_key: string;
      attestation_key: string;
      started_body: JsonObject;
      remote_revision: number;
      authorization: JsonObject | null;
      prepared?: boolean;
      preparation_submitted_sha256?: string;
      instruction_key?: string;
      instruction_body?: JsonObject;
      instruction_receipt?: JsonObject;
    }
  >;
}
export function configurationsFor(
  capabilities: Capabilities | null,
  studyId: string,
  protocolId?: string,
): ApprovedConfiguration[] {
  if (!capabilities || capabilities.account_state !== "active") return [];
  return Object.values(capabilities.channels)
    .flatMap((channel) =>
      channel.available &&
      channel.authorization_available !== false &&
      channel.software_available !== false
        ? (channel.configurations ?? [])
        : [],
    )
    .filter(
      (config) =>
        config.study_id === studyId &&
        (!protocolId || config.protocol_id === protocolId) &&
        Date.parse(config.expires_at) > Date.now(),
    );
}
export function configurationFor(
  check: CheckRecord,
  capabilities: Capabilities | null,
  channel: AcquisitionChannel,
): ApprovedConfiguration {
  if (
    check.kind !== "measurement" ||
    check.snapshot.mode !== "controlled_research" ||
    !check.snapshot.study_id ||
    !check.snapshot.protocol_id
  )
    throw new IntegrityError(
      "AUTHORIZED_STUDY_REQUIRED",
      "Start an owned research check from a current study invitation and approved protocol. Local practice cannot become a research capture.",
    );
  const candidates = capabilities?.channels[channel];
  if (
    !candidates?.available ||
    candidates.authorization_available === false ||
    candidates.software_available === false
  )
    throw new IntegrityError(
      "CAPTURE_UNAVAILABLE",
      "This channel has no current approved configuration and installed software adapter.",
    );
  const matching = (candidates.configurations ?? []).filter(
    (config) =>
      config.study_id === check.snapshot.study_id &&
      config.protocol_id === check.snapshot.protocol_id &&
      Date.parse(config.expires_at) > Date.now() &&
      check.context.configuration_refs.some(
        (ref) =>
          ref.id === config.configuration_id &&
          ref.version === config.configuration_version &&
          ref.sha256 === config.configuration_hash,
      ),
  );
  if (matching.length !== 1)
    throw new IntegrityError(
      "CAPTURE_CONFIGURATION_AMBIGUOUS",
      "The frozen check does not select exactly one current configuration for this channel. Start a new check after reviewing the approved protocol.",
    );
  return clone(matching[0]!);
}
export function verifyCaptureGrant(
  value: unknown,
  check: CheckRecord,
  attemptId: string,
  channel: AcquisitionChannel,
  config: ApprovedConfiguration,
  bindingId: string | null,
  deviceId: string | null,
  rawAuthority?: {
    kind: RawKind;
    status: RawRecordingStatus;
    fences: RawKind[];
  },
  instructionReceipt?: JsonObject,
): JsonObject {
  const grant = requireObject(value);
  knownKeys(grant, [
    "attempt_id",
    "channel",
    "binding_id",
    "device_id",
    "configuration_id",
    "configuration_hash",
    "authorization_id",
    "session_id",
    "state",
    "expires_at",
    "expires_epoch",
    "configuration_max_duration_ms",
    "supported_phone_models",
    "supported_os_versions",
    "supported_native_builds",
    "software_adapter_id",
    "configuration_submitted_sha256",
    "configuration_version",
    "capture_context_sha256",
    "raw_recording_permission",
    "configuration_material",
    "raw_recording_kind",
    "instruction_receipt_id",
    "participant_protocol_sha256",
    "instruction_receipt",
  ]);
  if (
    instructionReceipt
      ? grant.instruction_receipt_id !==
          instructionReceipt.instruction_receipt_id ||
        grant.participant_protocol_sha256 !==
          config.participant_protocol_sha256 ||
        digest(grant.instruction_receipt) !== digest(instructionReceipt)
      : (grant.instruction_receipt_id ?? null) !== null ||
        (grant.instruction_receipt ?? null) !== null ||
        (grant.participant_protocol_sha256 ?? null) !== null
  )
    throw new IntegrityError(
      "INSTRUCTION_RECEIPT_MISMATCH",
      "The fresh grant differs from the exact confirmed participant instructions.",
    );
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      String(grant.authorization_id),
    ) ||
    grant.session_id !== check.id ||
    grant.attempt_id !== attemptId ||
    grant.channel !== channel ||
    grant.binding_id !== bindingId ||
    grant.device_id !== deviceId ||
    grant.configuration_id !== config.configuration_id ||
    grant.configuration_hash !== config.configuration_hash ||
    grant.configuration_version !== config.configuration_version ||
    grant.configuration_submitted_sha256 !== config.submitted_sha256 ||
    grant.software_adapter_id !== config.software_adapter_id ||
    grant.capture_context_sha256 !== digest(check.context) ||
    digest(grant.supported_phone_models) !==
      digest(config.supported_phone_models) ||
    digest(grant.supported_os_versions ?? []) !==
      digest(config.supported_os_versions ?? []) ||
    digest(grant.supported_native_builds ?? []) !==
      digest(config.supported_native_builds ?? []) ||
    grant.state !== "issued"
  )
    throw new IntegrityError(
      "CAPTURE_GRANT_MISMATCH",
      "The server capture authorization differs from this immutable check, device or configuration.",
    );
  if (rawAuthority) {
    if (grant.raw_recording_kind !== rawAuthority.kind)
      throw new IntegrityError(
        "RAW_AUTHORITY_MISMATCH",
        "The grant changed the requested recording kind.",
      );
    verifyRawPermission(
      grant.raw_recording_permission,
      rawAuthority.status,
      rawAuthority.kind,
      rawAuthority.fences,
    );
  } else if (
    grant.raw_recording_permission !== undefined &&
    grant.raw_recording_permission !== null
  )
    throw new IntegrityError(
      "UNREQUESTED_RAW_AUTHORITY",
      "This feature-only capture did not request optional raw recording.",
    );
  const expires = requiredString(grant.expires_at, 40),
    epoch = Number(grant.expires_epoch) * 1000;
  if (
    !expires.endsWith("Z") ||
    !Number.isFinite(epoch) ||
    Math.abs(Date.parse(expires) - epoch) > 1000 ||
    epoch <= Date.now() ||
    epoch > Date.now() + 61_000 ||
    safeInteger(grant.configuration_max_duration_ms, 1) > 300_000
  )
    throw new IntegrityError(
      "CAPTURE_GRANT_EXPIRED",
      "The online capture authorization is expired or unsupported.",
    );
  if (
    grant.configuration_material !== undefined &&
    digest(grant.configuration_material) !== config.configuration_hash
  )
    throw new IntegrityError(
      "CONFIGURATION_MATERIAL_MISMATCH",
      "The approved acquisition material differs from its frozen scientific hash.",
    );
  return clone(grant) as JsonObject;
}
export function verifyCaptureStart(
  value: unknown,
  authorization: JsonObject,
  attemptId: string,
  bootId: string | null,
): void {
  const started = requireObject(value);
  for (const key of [
    "instruction_receipt_id",
    "participant_protocol_sha256",
    "instruction_receipt",
  ])
    if (digest(started[key] ?? null) !== digest(authorization[key] ?? null))
      throw new IntegrityError(
        "INSTRUCTION_RECEIPT_MISMATCH",
        "The confirmed participant protocol changed before capture start.",
      );
  if (
    digest(started.raw_recording_permission ?? null) !==
    digest(authorization.raw_recording_permission ?? null)
  )
    throw new IntegrityError(
      "RAW_AUTHORITY_MISMATCH",
      "Optional recording authority changed before actual acquisition started.",
    );
  if (started.server_start !== undefined) {
    const token = requireObject(started.server_start),
      grant = requireObject(token.grant);
    if (
      token.domain !== "OTGD capture grant v1\u0000" ||
      digest(grant.raw_recording_permission ?? null) !==
        digest(authorization.raw_recording_permission ?? null) ||
      grant.authorization_id !== authorization.authorization_id ||
      grant.attempt_id !== attemptId ||
      grant.session_id !== authorization.session_id ||
      grant.configuration_hash !== authorization.configuration_hash ||
      grant.configuration_submitted_sha256 !==
        authorization.configuration_submitted_sha256 ||
      grant.capture_context_sha256 !== authorization.capture_context_sha256 ||
      grant.boot_id !== bootId ||
      (grant.instruction_receipt_id ?? null) !==
        (authorization.instruction_receipt_id ?? null) ||
      (grant.participant_protocol_sha256 ?? null) !==
        (authorization.participant_protocol_sha256 ?? null)
    )
      throw new IntegrityError(
        "CAPTURE_START_MISMATCH",
        "The signed start token differs from the frozen acquisition or optional recording authority.",
      );
  } else if (
    authorization.raw_recording_permission !== undefined &&
    authorization.raw_recording_permission !== null
  )
    throw new IntegrityError(
      "RAW_AUTHORITY_MISMATCH",
      "Optional acquisition requires its unchanged server-signed start permission.",
    );
  knownKeys(started, [
    "authorization_id",
    "attempt_id",
    "device_boot_id",
    "state",
    "server_started_at",
    "raw_recording_permission",
    "server_start",
    "instruction_receipt_id",
    "participant_protocol_sha256",
    "instruction_receipt",
  ]);
  if (
    started.authorization_id !== authorization.authorization_id ||
    started.attempt_id !== attemptId ||
    started.device_boot_id !== bootId ||
    started.state !== "started" ||
    typeof started.server_started_at !== "string" ||
    !started.server_started_at.endsWith("Z") ||
    !Number.isFinite(Date.parse(started.server_started_at))
  )
    throw new IntegrityError(
      "CAPTURE_START_MISMATCH",
      "The service has not confirmed the exact capture start. Hardware acquisition remains stopped.",
    );
}
