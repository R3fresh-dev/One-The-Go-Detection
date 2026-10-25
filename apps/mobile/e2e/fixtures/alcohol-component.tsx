import React from "react";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
import { AlcoholScreen, HistoryScreen } from "../../src/ui/manage";
import { ResultScreen, EvidenceScreen } from "../../src/ui/checks";
import { ThemeProvider } from "../../src/ui/theme";

// Controlled input to actual screens. No acquisition or scientific admission is
// performed here; research input is the existing Python-generated fixture.
const root = createRoot(document.getElementById("root")!);
(window as any).renderAlcohol = (check: any, screen = "alcohol") => {
  const model: any = {
    identity: null,
    state: {
      generation: check?.generation ?? 1,
      checks: check ? [check] : [],
      queue: [],
      historyIndex: [],
      reportRevisions: [],
      replacements: [],
      capabilities: null,
      preferences: { retryQueuedAutomatically: false },
    },
  };
  const controller: any = {
    check,
    epoch: "fictional-component-only",
    hasCurrentHrResultAdmission: () => false,
    getSnapshot: () => model,
    run: async (fn: () => Promise<void>) => fn(),
    navigate: async (next: string) => render(next),
    openCheck: async () => render("result"),
    selectCheck: async () => render("result"),
  };
  function render(next: string) {
    const Screen =
      next === "history"
        ? HistoryScreen
        : next === "result"
          ? ResultScreen
          : next === "evidence"
            ? EvidenceScreen
            : AlcoholScreen;
    root.render(
      <ThemeProvider mode="light">
        <Screen controller={controller} model={model} />
      </ThemeProvider>,
    );
  }
  render(screen);
};
