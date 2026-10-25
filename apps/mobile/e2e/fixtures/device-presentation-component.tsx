import React from "react";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
import { HomeScreen } from "../../src/ui/account";
import { DeviceScreen } from "../../src/ui/manage";
import { ThemeProvider } from "../../src/ui/theme";
import { emptyWorkspace } from "../../src/core/domain";
import { readerPresentationFixture } from "../../tests/support/device-presentation-fixtures";

// Actual Home/Device screens; controlled connection and parsed service-envelope
// observations only. No radio, device key, approval or participant use occurs.
const root = createRoot(document.getElementById("root")!);
(window as any).renderReaderPresentation = (
  kind: string,
  expiresAt?: string,
) => {
  const fixture = readerPresentationFixture(kind, expiresAt);
  const state = emptyWorkspace(
    "fictional-reader-presentation",
    fixture.capabilities.server_time,
  );
  state.capabilities = fixture.capabilities;
  state.generation = fixture.generation;
  let model: any = {
    state,
    identity: fixture.identity,
    offline: fixture.offline,
    route: "home",
    busy: false,
    config: null,
  };
  const device: any = {
    snapshot: () => fixture.snapshot,
    subscribe: (listener: (snapshot: any) => void) => {
      listener(fixture.snapshot);
      return () => {};
    },
  };
  const controller: any = {
    epoch: "fictional-reader-component",
    check: null,
    device,
    getSnapshot: () => model,
    run: async (fn: () => Promise<void>) => fn(),
    navigate: async (route: string) => {
      model = { ...model, route };
      render();
    },
  };
  function render() {
    const Screen = model.route === "device" ? DeviceScreen : HomeScreen;
    root.render(
      <ThemeProvider mode="light">
        <Screen controller={controller} model={model} />
      </ThemeProvider>,
    );
  }
  render();
};
