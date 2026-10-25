import capsFixture from "../../testfixtures/backend-capabilities.json";
import { clone } from "../../src/core/integrity";
import { parseCapabilities } from "../../src/services/api";
import type { DeviceSnapshot } from "../../src/device/types";
import type { Identity } from "../../src/core/types";

/** Display-contract observations only. No reader/study/scientific authority is
 * created; actual framed-controller observations are tested separately. */
export function readerPresentationFixture(
  kind = "current",
  expiresAt = "2030-01-01T00:00:00Z",
) {
  const capabilities = clone(capsFixture) as any;
  capabilities.channels.cardiac = {
    available: true,
    software_available: true,
    authorization_available: true,
    reason_codes: [],
    configurations: [
      {
        study_id: "fictional-study",
        protocol_id: "fictional-protocol",
        configuration_id: "fictional-cardiac-config",
        configuration_hash: "1".repeat(64),
        submitted_sha256: "2".repeat(64),
        configuration_version: "v1",
        expires_at: expiresAt,
        supported_phone_models: [],
        software_adapter_id: "otgd_esp32_adc_v1",
      },
    ],
  };
  if (["unbound", "bound", "revoked", "simulator"].includes(kind)) {
    Object.assign(capabilities.channels.cardiac, {
      available: false,
      authorization_available: false,
      reason_codes: [
        kind === "revoked" ? "APPROVAL_REVOKED" : "NO_QUALIFIED_CONFIGURATION",
      ],
      configurations: [],
    });
  }
  if (kind === "expired")
    capabilities.channels.cardiac.configurations[0].expires_at =
      "2020-01-01T00:00:00Z";
  const admitted = parseCapabilities(capabilities);
  const identity: Identity = {
    accountRef: admitted.account_ref,
    issuer: "https://fictional-display.invalid",
    generation: admitted.data_generation,
    state: "active",
    verifiedAt: admitted.server_time,
  };
  if (kind === "mismatched")
    identity.accountRef = "different-fictional-account";
  if (kind === "generation") identity.generation++;
  const snapshot: DeviceSnapshot = {
    state: "connected_reader",
    observedAt: "2026-10-25T10:00:00Z",
    devices: [],
    reason: null,
    captureInProgress: false,
    signalPreview: null,
    humanCaptureAvailable: false,
    association: {
      source: "prototype_sensor",
      peripheralId: "fictional-peripheral",
      deviceId: "fictional-device",
      bootId: "fictional-current-boot",
      verifiedBindingId:
        kind === "unbound" ? null : "fictional-service-binding",
      transport: "ble_unprovisioned",
      hardwareRevision: "fictional-hw",
      firmwareVersion: "fictional-fw",
      protocolVersion: 1,
      capabilities: {
        protocol_version: 1,
        encodings: [1],
        max_logical_bytes: 8192,
        max_att_bytes: 160,
        source: "prototype_sensor",
        protocol_id: "otgd_signed_reader_v1",
        device_id: "fictional-device",
        boot_id: "fictional-current-boot",
        hardware_revision: "fictional-hw",
        firmware_version: "fictional-fw",
        key_id: "fictional-key",
        channels: ["ppg"],
        timestamp_resolution_ms: 1,
      },
    },
  };
  if (kind === "simulator") {
    snapshot.state = "connected_simulator";
    snapshot.association!.source = "simulated";
    snapshot.association!.verifiedBindingId = null;
    snapshot.association!.transport = "local_simulator";
  }
  if (kind === "disconnected" || kind === "rebooted") {
    snapshot.state = "error";
    snapshot.reason =
      kind === "disconnected" ? "LINK_DISCONNECTED" : "BOOT_MISMATCH";
    snapshot.association = null;
  }
  return {
    capabilities: admitted,
    identity,
    generation: admitted.data_generation,
    offline: kind === "offline",
    snapshot,
  };
}
