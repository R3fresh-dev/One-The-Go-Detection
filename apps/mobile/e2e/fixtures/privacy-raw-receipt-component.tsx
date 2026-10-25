import React from "react";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
import { PrivacyScreen } from "../../src/ui/manage";
import { RawRecordingsScreen } from "../../src/ui/raw-recordings";
import { ThemeProvider } from "../../src/ui/theme";
import { emptyWorkspace } from "../../src/core/domain";
import { parsePrivacyJob } from "../../src/services/api";
import { parseRawRecordingStatus } from "../../src/core/rawRecordings";

// Render actual production screens through the actual receipt admission code.
// These controlled component inputs do not provide native storage/OS evidence.
const root = createRoot(document.getElementById("root")!);
(window as any).renderReceipt = (kind: "privacy" | "raw", value: any) => {
  const state = emptyWorkspace(
    "fictional-component-owner",
    "2026-10-11T12:00:00Z",
  );
  if (kind === "privacy") state.jobs = [parsePrivacyJob(value)];
  else
    state.rawRecordingStatuses[value.study_id] = parseRawRecordingStatus(
      value,
      value.study_id,
    );
  const model: any = {
    state,
    identity: { accountRef: "fictional-component-owner" },
    rawStudyId: value.study_id,
    offline: false,
  };
  const controller: any = { epoch: "component-only", getSnapshot: () => model };
  const Screen = kind === "privacy" ? PrivacyScreen : RawRecordingsScreen;
  root.render(
    <ThemeProvider mode="light">
      <Screen controller={controller} model={model} />
    </ThemeProvider>,
  );
};
