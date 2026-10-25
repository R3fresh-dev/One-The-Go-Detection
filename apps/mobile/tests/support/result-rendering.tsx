import React from "react";
const { renderToStaticMarkup } = require("react-dom/server") as {
  renderToStaticMarkup: (node: React.ReactNode) => string;
};
import { CheckRow, HomeScreen, WelcomeScreen } from "../../src/ui/account";
import { HistoryScreen } from "../../src/ui/manage";
import { ResultScreen } from "../../src/ui/checks";
import { ThemeProvider } from "../../src/ui/theme";
import { emptyProfile } from "../../src/core/domain";

/** Actual UI renderer; only controller/device inputs are controlled. This
 * server render cannot prove browser interaction, native OS or admission. */
export function renderResultUI(check: any, screen = "row", scope: any = {}) {
  const model: any = {
    identity: scope.identity ?? null,
    offline: scope.offline ?? false,
    state: {
      generation: scope.generation ?? check.generation,
      checks: [check],
      queue: scope.queue ?? [],
      historyIndex: [],
      reportRevisions: [],
      replacements: [],
      preferences: {
        theme: "light",
        units: "metric",
        reducedMotion: false,
        retryQueuedUploads: false,
      },
      profile: emptyProfile("2026-10-11T00:00:00Z"),
      capabilities: scope.capabilities ?? null,
    },
  };
  const controller: any = {
    check,
    epoch: "fictional-render-only",
    hasCurrentHrResultAdmission: () => scope.hrResultAdmitted === true,
    getSnapshot: () => model,
    device: {
      snapshot: () => ({
        state: "idle",
        observedAt: "2026-10-11T00:00:00Z",
        devices: [],
        association: null,
        reason: null,
        captureInProgress: false,
        signalPreview: null,
        humanCaptureAvailable: false,
      }),
    },
  };
  const Screen =
    screen === "home"
      ? HomeScreen
      : screen === "history"
        ? HistoryScreen
        : screen === "result"
          ? ResultScreen
          : WelcomeScreen;
  return renderToStaticMarkup(
    <ThemeProvider mode="light">
      {screen === "row" ? (
        <CheckRow check={check} onPress={() => {}} />
      ) : (
        <Screen controller={controller} model={model} />
      )}
    </ThemeProvider>,
  );
}
