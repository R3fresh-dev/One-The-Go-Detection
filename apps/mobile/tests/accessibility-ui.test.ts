import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
import { emptyWorkspace } from "../src/core/domain";
const { light, dark } =
  require("../src/ui/theme") as typeof import("../src/ui/theme");
function luminance(hex: string) {
  const channels = hex.match(/[a-f\d]{2}/gi)!.map((part) => {
    const value = parseInt(part, 16) / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return channels[0]! * 0.2126 + channels[1]! * 0.7152 + channels[2]! * 0.0722;
}
test("destructive button foreground is readable against each actual theme background", () => {
  for (const theme of [light, dark]) {
    const foreground = (theme as any).onDanger ?? theme.white;
    const values = [luminance(foreground), luminance(theme.danger)].sort(
      (a, b) => b - a,
    );
    const ratio = (values[0]! + 0.05) / (values[1]! + 0.05);
    assert.ok(ratio >= 4.5, `${foreground} on ${theme.danger}: ${ratio}:1`);
  }
});
test("new workspaces follow system reduced motion until the user chooses an override", () => {
  const state = emptyWorkspace("guest", "2026-10-25T00:00:00.000Z");
  assert.equal(state.preferences.reducedMotion, "system");
});
