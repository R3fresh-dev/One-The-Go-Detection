import React from "react";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
import { AboutScreen, StatusScreen } from "../../src/ui/manage";
import { ThemeProvider } from "../../src/ui/theme";
const root = createRoot(document.getElementById("root")!);
(window as any).renderAvailability = (capabilities: any, about = false) => {
  const props: any = {
    controller: {
      navigate: async () => {},
      run: async (fn: () => Promise<void>) => fn(),
      refreshConfig: async () => {},
      refreshCapabilities: async () => {},
    },
    model: {
      state: { capabilities },
      offline: false,
      config: null,
      identity: null,
    },
  };
  root.render(
    <ThemeProvider mode="light">
      {about ? <AboutScreen {...props} /> : <StatusScreen {...props} />}
    </ThemeProvider>,
  );
};
