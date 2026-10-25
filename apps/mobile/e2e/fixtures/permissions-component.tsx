import React from "react";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
import { SettingsScreen } from "../../src/ui/manage";
import { ThemeProvider } from "../../src/ui/theme";
const root = createRoot(document.getElementById("root")!);
(window as any).permissionControl = {
  exact: "denied",
  permission: {
    status: "denied",
    granted: false,
    canAskAgain: true,
    expires: "never",
  },
  reads: 0,
  prompts: 0,
  settings: 0,
  defer: false,
  fail: false,
  pending: [],
  listeners: new Set(),
};
const model: any = {
  identity: null,
  state: {
    generation: 1,
    checks: [],
    queue: [],
    capabilities: null,
    preferences: { theme: "light", units: "metric", reducedMotion: false },
  },
};
const controller: any = {
  epoch: "fictional-account-A:g1",
  run: async (fn: () => Promise<void>) => fn(),
  report: (e: unknown) => {
    throw e;
  },
};
(window as any).renderPermissions = (
  epoch = controller.epoch,
  generation = 1,
) => {
  controller.epoch = epoch;
  model.state.generation = generation;
  root.render(
    <ThemeProvider mode="light">
      <SettingsScreen controller={controller} model={model} />
    </ThemeProvider>,
  );
};
(window as any).unmountPermissions = () => root.render(null);
(window as any).changePermissionEpoch = (epoch: string) => {
  controller.epoch = epoch;
};
(window as any).permissionActive = () => {
  for (const listener of (window as any).permissionControl.listeners)
    listener("active");
};
