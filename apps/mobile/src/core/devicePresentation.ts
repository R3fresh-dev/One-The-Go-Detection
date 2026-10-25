import type { DeviceSnapshot } from "../device/types";
import type { Capabilities, Identity } from "./types";

export interface DevicePresentation {
  title: string;
  detail: string;
  action: string;
  tone: "neutral" | "warning" | "accent";
  bootId: string | null;
  observedAt: string | null;
  connected: boolean;
  badge: string;
}

const recovery: Record<
  string,
  { title: string; detail: string; action: string }
> = {
  NATIVE_BLUETOOTH_UNAVAILABLE: {
    title: "Bluetooth unavailable in this build",
    detail:
      "Use the local synthetic simulator, or connect from an installed native app.",
    action: "View device options",
  },
  BLUETOOTH_PERMISSION_DENIED: {
    title: "Bluetooth permission declined",
    detail:
      "Device discovery needs Bluetooth permission. Review permission and connection options.",
    action: "Review Bluetooth access",
  },
  BLUETOOTH_PERMISSION_BLOCKED: {
    title: "Bluetooth permission blocked",
    detail:
      "Enable Bluetooth access in system settings, then return to device discovery.",
    action: "Review Bluetooth access",
  },
  UNAUTHORIZED: {
    title: "Bluetooth permission unavailable",
    detail:
      "Review the app's Bluetooth access in system settings before reconnecting.",
    action: "Review Bluetooth access",
  },
  BLUETOOTH_POWERED_OFF: {
    title: "Bluetooth is off",
    detail: "Turn Bluetooth on, then find and reconnect the reader.",
    action: "Reconnect a reader",
  },
  POWERED_OFF: {
    title: "Bluetooth is off",
    detail: "Turn Bluetooth on, then find and reconnect the reader.",
    action: "Reconnect a reader",
  },
  BLUETOOTH_RESET: {
    title: "Bluetooth connection reset",
    detail:
      "The previous handshake is no longer current. Reconnect to verify the reader's boot and protocol.",
    action: "Reconnect a reader",
  },
  LINK_DISCONNECTED: {
    title: "Reader disconnected",
    detail:
      "The connection was lost. A new connection and handshake are required before another synthetic capture.",
    action: "Reconnect a reader",
  },
  CONNECTION_TIMEOUT: {
    title: "Reader connection timed out",
    detail:
      "Keep the reader nearby and reconnect. A saved device name does not establish readiness.",
    action: "Reconnect a reader",
  },
  BOOT_MISMATCH: {
    title: "Reader restarted",
    detail:
      "The reader boot changed. Reconnect and start a new capture attempt.",
    action: "Reconnect a reader",
  },
  UNVERIFIED_HUMAN_HARDWARE: {
    title: "Reader is unsupported",
    detail:
      "This reader has no approved synthetic handshake. A connection cannot authorize a human measurement.",
    action: "Review device compatibility",
  },
  UNSUPPORTED_DEVICE: {
    title: "Reader is unsupported",
    detail:
      "The reader does not provide the supported project protocol. Review device compatibility.",
    action: "Review device compatibility",
  },
  PROTOCOL_VERSION: {
    title: "Reader protocol is unsupported",
    detail: "Use a reader with the documented project protocol and reconnect.",
    action: "Review device compatibility",
  },
  REPLAY_JOURNAL_FULL: {
    title: "Reader session needs restarting",
    detail:
      "Restart the synthetic reader and reconnect before a new capture attempt.",
    action: "Reconnect a reader",
  },
  BACKGROUND: {
    title: "Capture stopped in background",
    detail:
      "Reconnect and start a new capture attempt. The interrupted capture cannot resume.",
    action: "Reconnect a reader",
  },
};

/** Display current handshake state; an alias, battery placeholder or prior measurement is never readiness. */
export function presentDevice(snapshot: DeviceSnapshot): DevicePresentation {
  const timestamp = "observedAt" in snapshot ? snapshot.observedAt : null;
  const observedAt =
    typeof timestamp === "string" && Number.isFinite(Date.parse(timestamp))
      ? timestamp
      : null;
  const common = {
    bootId: null,
    observedAt,
    connected: false,
    badge: "Not connected",
  };
  if (
    snapshot.state === "connected_reader" &&
    snapshot.association?.source === "prototype_sensor" &&
    snapshot.association.bootId &&
    !snapshot.reason
  )
    return {
      title: snapshot.association.verifiedBindingId
        ? "Reader binding verified by service"
        : "Signed-protocol reader connected · identity unverified",
      badge: "Signed reader connection",
      detail:
        "Connection and service binding do not authorize measurement. Current study consent, configuration, calibration and fresh online capture authorization remain separate.",
      action: "Manage reader connection",
      tone: "accent",
      bootId: snapshot.association.bootId,
      observedAt,
      connected: true,
    };
  if (
    snapshot.state === "connected_simulator" &&
    snapshot.association?.source === "simulated" &&
    snapshot.association.verifiedBindingId === null &&
    snapshot.humanCaptureAvailable === false
  ) {
    return {
      title: "Synthetic reader connected",
      detail: snapshot.captureInProgress
        ? "A synthetic capture is running. The complete terminal evidence is saved separately."
        : "The current reader handshake and clock exchange support synthetic bench captures only.",
      action: "Manage reader connection",
      tone: "accent",
      bootId: snapshot.association.bootId,
      observedAt,
      connected: true,
      badge: "Synthetic only",
    };
  }
  if (snapshot.state === "scanning")
    return {
      ...common,
      title: "Searching for readers",
      detail:
        "Discovery is in progress. No reader is connected or ready for capture yet.",
      action: "View discovery",
      tone: "neutral",
    };
  if (snapshot.state === "connecting")
    return {
      ...common,
      title: "Checking reader connection",
      detail:
        "The app is checking capabilities, current boot identity and clock exchange.",
      action: "View connection progress",
      tone: "neutral",
    };
  const reason = snapshot.reason && recovery[snapshot.reason];
  if (reason) return { ...common, ...reason, tone: "warning" };
  if (snapshot.state === "idle")
    return {
      ...common,
      title: "Not connected",
      detail:
        "Find a supported reader or choose a synthetic simulator. Connection and capture authorization are separate.",
      action: "Connect or reconnect a reader",
      tone: "neutral",
    };
  return {
    ...common,
    title: "Reader connection unavailable",
    detail:
      "A current supported handshake could not be verified. Review device status and reconnect.",
    action: "Review device status",
    tone: "warning",
  };
}

export interface ChannelPresentation {
  channel: string;
  label: string;
  detail: string;
  conditional: boolean;
  expiresAt: string | null;
}

/** Displays an already authenticated capability observation. Connection/binding
 * is deliberately not an input and cannot create capture or scientific authority. */
export function presentAcquisitionChannels(input: {
  identity: Identity | null;
  capabilities: Capabilities | null;
  generation: number | null;
  offline: boolean;
  hostedPreview: boolean;
  now?: number;
}): ChannelPresentation[] {
  const { identity, capabilities, generation, offline, hostedPreview } = input;
  const current =
    !hostedPreview &&
    !offline &&
    identity?.state === "active" &&
    capabilities?.account_state === "active" &&
    identity.accountRef === capabilities.account_ref &&
    identity.generation === generation &&
    capabilities.data_generation === generation;
  const labels: Record<string, string> = {
    saliva: "Saliva",
    eyes: "Pupil",
    cardiac: "Cardiac (PPG)",
    ecg: "ECG",
    alcohol: "Alcohol",
    task: "Reaction task",
  };
  const channels = new Set([
    ...Object.keys(labels).filter((name) => name !== "task"),
    ...(current ? Object.keys(capabilities!.channels) : []),
  ]);
  const now = input.now ?? Date.now();
  return [...channels].map((channel) => {
    const base = {
      channel,
      label: labels[channel] ?? channel,
      conditional: false,
      expiresAt: null,
    };
    if (!current)
      return {
        ...base,
        detail: hostedPreview
          ? "Unavailable in fictional preview"
          : offline
            ? "Current authorization unavailable · offline"
            : "Current authorization unavailable · sign in to the matching active workspace",
      };
    const cap = capabilities!.channels[channel];
    if (
      !cap?.available ||
      cap.authorization_available === false ||
      cap.software_available === false
    )
      return {
        ...base,
        detail: `Unavailable · ${cap?.reason_codes.length ? cap.reason_codes.map((code) => code.replaceAll("_", " ").toLowerCase()).join(" · ") : "no current approved configuration and installed adapter"}`,
      };
    const active = (cap.configurations ?? []).filter(
      (configuration) => Date.parse(configuration.expires_at) > now,
    );
    if (!active.length)
      return {
        ...base,
        detail:
          (cap.configurations?.length ?? 0) > 0
            ? "Unavailable · approved configuration expired"
            : "Unavailable · no current approved configuration",
      };
    return {
      ...base,
      conditional: true,
      detail:
        "Conditionally available · fresh online authorization required for each Start",
      expiresAt: active
        .map((configuration) => configuration.expires_at)
        .sort((a, b) => Date.parse(a) - Date.parse(b))[0]!,
    };
  });
}
