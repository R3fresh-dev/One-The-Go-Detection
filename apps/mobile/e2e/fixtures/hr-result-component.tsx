import React, { useSyncExternalStore } from "react";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
import { AppController } from "../../src/controller";
import { emptyWorkspace } from "../../src/core/domain";
import { parseRemoteCheck } from "../../src/core/remote";
import { clone, digest } from "../../src/core/integrity";
import { ResultScreen, EvidenceScreen } from "../../src/ui/checks";
import { ThemeProvider } from "../../src/ui/theme";
import fixture from "../../testfixtures/backend-cardiac-authority.json";
import capsFixture from "../../testfixtures/backend-capabilities.json";
import { ApiError } from "../../src/services/api";
import { openWorkspaceStore } from "../../src/platform/storage";

// Actual controller and screens, with a controlled service boundary and complete
// fictional signed evidence. This does not authenticate study/registry authority.
const app = new AppController();
const state = emptyWorkspace(
  "fictional-HR-browser",
  fixture.result.evaluated_at,
);
state.generation = fixture.generation;
state.capabilities = {
  ...clone(capsFixture),
  account_ref: fixture.snapshot.subject_ref,
  data_generation: fixture.generation,
} as any;
const check = parseRemoteCheck(clone(fixture.owned_session), state);
state.checks = [check];
(app as any).model = {
  ...app.getSnapshot(),
  state,
  loading: false,
  route: "result",
  selectedCheck: check.id,
  identity: {
    accountRef: fixture.snapshot.subject_ref,
    generation: fixture.generation,
    issuer: "https://fictional-browser.invalid",
    state: "active",
    verifiedAt: fixture.result.evaluated_at,
  },
};
const pending: {
  resolve: (value: any) => void;
  reject: (error: Error) => void;
}[] = [];
(window as any).hrReadRequests = [];
(app.api as any).request = (path: string) => {
  if (path === `/v1/sessions/${check.id}`)
    return Promise.resolve({
      value: clone(fixture.owned_session),
      status: 200,
      etag: '"4"',
      evidenceSha256: check.evidence_sha256,
    });
  if (path !== `/v1/sessions/${check.id}/result`)
    throw Error("Unexpected fixture route");
  (window as any).hrReadRequests.push(path);
  return new Promise((resolve, reject) => pending.push({ resolve, reject }));
};
(window as any).resolveHrRead = (status = 200) => {
  const read = pending.shift();
  if (!read) throw Error("No pending current HR read");
  if (status === 200)
    read.resolve({
      value: clone(check.result),
      status,
      etag: null,
      evidenceSha256: check.evidence_sha256,
    });
  else
    read.reject(
      new ApiError(
        status,
        "APPROVED_REGISTRY_VERSION_REQUIRED",
        "Fictional current HR authority retired",
      ),
    );
};
(window as any).hrRetainedDigest = () =>
  digest(app.getSnapshot().state!.checks[0]);
function Fixture() {
  const model = useSyncExternalStore(app.subscribe, app.getSnapshot);
  return (
    <ThemeProvider mode="light">
      {model.error && <p role="alert">{model.error}</p>}
      {model.route === "result" ? (
        <ResultScreen controller={app} model={model} />
      ) : model.route === "evidence" ? (
        <EvidenceScreen controller={app} model={model} />
      ) : (
        <button onClick={() => void app.selectCheck(check.id)}>
          Reopen cached result
        </button>
      )}
    </ThemeProvider>
  );
}
const root = createRoot(document.getElementById("root")!);
void openWorkspaceStore(state.workspace).then(async (store) => {
  (app as any).store = store;
  await store.save(state);
  root.render(<Fixture />);
});
