import React from "react";
const { renderToStaticMarkup } = require("react-dom/server") as {
  renderToStaticMarkup: (node: React.ReactNode) => string;
};
import { PrivacyScreen } from "../../src/ui/manage";
import { RawRecordingsScreen } from "../../src/ui/raw-recordings";
import { ThemeProvider } from "../../src/ui/theme";
import { emptyWorkspace } from "../../src/core/domain";
import { parsePrivacyJob } from "../../src/services/api";
import { parseRawRecordingStatus } from "../../src/core/rawRecordings";

// Actual production screens with controlled controller/OS boundaries. SSR is
// presentation evidence only; it does not run encrypted storage or native AT.
export function renderPrivacyReceipt(value: unknown) {
  const state = emptyWorkspace("fictional-owned", "2026-10-25T00:00:00Z");
  state.jobs = [parsePrivacyJob(value)];
  const model: any = {
    state,
    identity: { accountRef: "fictional-owner" },
    offline: false,
  };
  const controller: any = { getSnapshot: () => model };
  return renderToStaticMarkup(
    <ThemeProvider mode="light">
      <PrivacyScreen controller={controller} model={model} />
    </ThemeProvider>,
  );
}
export function renderRawReceipt(value: any) {
  const state = emptyWorkspace("fictional-owned", "2026-10-11T12:00:00Z");
  state.rawRecordingStatuses[value.study_id] = parseRawRecordingStatus(
    value,
    value.study_id,
  );
  const model: any = { state, rawStudyId: value.study_id, offline: false };
  const controller: any = { epoch: "fixture-render", getSnapshot: () => model };
  return renderToStaticMarkup(
    <ThemeProvider mode="light">
      <RawRecordingsScreen controller={controller} model={model} />
    </ThemeProvider>,
  );
}
