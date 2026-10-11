import type { DeviceSnapshot } from "../device/types";

export interface DevicePresentation {
  title: string;
  detail: string;
  action: string;
  tone: "neutral" | "warning" | "accent";
  bootId: string | null;
  observedAt: string | null;
  connected: boolean;
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
  const common = { bootId: null, observedAt, connected: false };
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
        "Find a reader and complete a new handshake to capture synthetic bench values.",
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
