import test from "node:test";
import assert from "node:assert/strict";
import {
  presentAcquisitionChannels,
  presentDevice,
} from "../src/core/devicePresentation";
import { readerPresentationFixture } from "./support/device-presentation-fixtures";
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

test("per-channel display uses active matching scope and unexpired admitted configuration independently from connection or binding", () => {
  for (const kind of [
    "simulator",
    "unbound",
    "bound",
    "current",
    "revoked",
    "expired",
    "disconnected",
    "rebooted",
    "mismatched",
    "generation",
    "offline",
  ]) {
    const fixture = readerPresentationFixture(kind);
    const row = presentAcquisitionChannels({
      ...fixture,
      hostedPreview: false,
      now: Date.parse("2026-10-25T10:00:00Z"),
    }).find((row) => row.channel === "cardiac")!;
    assert.equal(
      row.conditional,
      ["current", "disconnected", "rebooted"].includes(kind),
      kind,
    );
    if (kind === "revoked") assert.match(row.detail, /approval revoked/);
    if (kind === "expired") assert.match(row.detail, /configuration expired/);
    if (row.conditional)
      assert.match(
        row.detail,
        /fresh online authorization required for each Start/,
      );
    const connection = presentDevice(fixture.snapshot);
    assert.equal(
      connection.connected,
      !["disconnected", "rebooted"].includes(kind),
      kind,
    );
    if (kind === "simulator") assert.equal(connection.badge, "Synthetic only");
    else assert.notEqual(connection.badge, "Synthetic only");
    assert.equal(
      fixture.snapshot.humanCaptureAvailable,
      false,
      "Display must not create physical capture authority",
    );
  }
  const fixture = readerPresentationFixture("current", "2026-10-25T10:00:00Z");
  assert.equal(
    presentAcquisitionChannels({
      ...fixture,
      hostedPreview: false,
      now: Date.parse("2026-10-25T10:00:00Z"),
    }).find((row) => row.channel === "cardiac")!.conditional,
    false,
  );
  assert.ok(
    presentAcquisitionChannels({ ...fixture, hostedPreview: true }).every(
      (row) => !row.conditional,
    ),
  );
});
test("a healthy signed reader connection is physical and retains current boot independently from service binding", () => {
  for (const binding of [null, "fictional-service-binding"]) {
    const snapshot = {
      ...base(),
      state: "connected_reader",
      association: {
        peripheralId: "fictional-reader",
        deviceId: "fictional-device",
        bootId: "fictional-current-boot",
        hardwareRevision: "fictional-hw",
        firmwareVersion: "fictional-fw",
        protocolVersion: 1,
        source: "prototype_sensor",
        verifiedBindingId: binding,
        transport: "ble_unprovisioned",
        capabilities: {},
      },
    } as DeviceSnapshot;
    const summary = presentDevice(snapshot);
    assert.equal(summary.connected, true);
    assert.equal(summary.bootId, "fictional-current-boot");
    assert.match(summary.title, /reader/i);
    assert.doesNotMatch(
      summary.title + summary.detail,
      /unavailable|synthetic/i,
    );
  }
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
