import test from "node:test";
import assert from "node:assert/strict";
import { presentDevice } from "../src/core/devicePresentation";
import type { DeviceSnapshot } from "../src/device/types";

const base = (): DeviceSnapshot => ({
  state: "idle",
  devices: [{ peripheralId: "old", alias: "Saved reader", rssi: -20 }],
  association: null,
  reason: null,
  captureInProgress: false,
  humanCaptureAvailable: false,
  observedAt: "2026-10-11T10:00:00.000Z",
  signalPreview: null,
});
test("a saved reader alias does not become connected readiness or live battery", () => {
  const summary = presentDevice(base());
  assert.equal(summary.title, "Not connected");
  assert.equal(summary.connected, false);
  assert.equal(summary.bootId, null);
  assert.equal("battery" in summary, false);
});
test("permission, radio, reboot and unsupported reader failures have distinct recovery", () => {
  const cases = [
    ["BLUETOOTH_PERMISSION_BLOCKED", "Bluetooth permission blocked"],
    ["BLUETOOTH_POWERED_OFF", "Bluetooth is off"],
    ["BOOT_MISMATCH", "Reader restarted"],
    ["UNVERIFIED_HUMAN_HARDWARE", "Reader is unsupported"],
    ["LINK_DISCONNECTED", "Reader disconnected"],
  ];
  for (const [reason, expected] of cases) {
    const summary = presentDevice({
      ...base(),
      state: "error",
      reason: reason!,
    });
    assert.equal(summary.title, expected);
    assert.equal(summary.connected, false);
    assert.equal(summary.tone, "warning");
    assert.ok(summary.action.length > 0);
  }
});
test("intermediate or unverified connection states never claim capture readiness", () => {
  for (const state of [
    "scanning",
    "connecting",
    "connected_simulator",
  ] as const) {
    const summary = presentDevice({ ...base(), state });
    assert.equal(summary.connected, false);
    assert.equal(summary.bootId, null);
  }
});
