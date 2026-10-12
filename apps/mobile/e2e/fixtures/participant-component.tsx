import React from "react";
import { EyeAcquisitionExplanation, CardiacSummary } from "../../src/ui/checks";
import { ThemeProvider } from "../../src/ui/theme";
import { ParticipantPreparation } from "../../src/ui/participant-capture";
import {
  LabMethodConfirmation,
  SpecimenMetadataForm,
  ApprovedLabCollection,
} from "../../src/ui/lab-collection";
import {
  participantProtocol,
  validateCollectionBody,
} from "../../src/core/participantAcquisition";
import { clone } from "../../src/core/integrity";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
const root = createRoot(document.getElementById("root")!);
(window as any).unmountParticipant = () => root.render(null);
(window as any).renderParticipantCopy = (check: any, capabilities: any) => {
  root.render(
    <ThemeProvider mode="light">
      <EyeAcquisitionExplanation check={check} capabilities={capabilities} />
      <CardiacSummary component={check.snapshot.cardiac} />
    </ThemeProvider>,
  );
};
(window as any).participantCalls = [];
(window as any).renderPreparation = (
  configuration: any,
  channel: "cardiac" | "ecg" = "cardiac",
) => {
  root.render(
    <ThemeProvider mode="light">
      <ParticipantPreparation
        key={configuration.submitted_sha256}
        configuration={configuration}
        channel={channel}
        busy={false}
        onPrepare={() => {
          (window as any).participantCalls.push({ kind: "prepare" });
          return new Promise((resolve) => {
            (window as any).resolvePreparation = () =>
              resolve(new Date().toISOString());
          });
        }}
        onCapture={async (input, raw) => {
          (window as any).participantCalls.push({
            kind: "capture",
            input,
            raw,
          });
        }}
        onStop={async () => {
          (window as any).participantCalls.push({ kind: "stop" });
        }}
      />
    </ThemeProvider>,
  );
};
(window as any).renderLabMethod = (configuration: any) => {
  root.render(
    <ThemeProvider mode="light">
      <LabMethodConfirmation
        key={configuration.submitted_sha256}
        configuration={configuration}
        busy={false}
        onStart={async (input) => {
          (window as any).participantCalls.push({ kind: "method", input });
        }}
      />
    </ThemeProvider>,
  );
};
(window as any).renderSpecimenForm = (
  configuration: any,
  request: any,
  draft?: any,
) => {
  const protocol = participantProtocol(configuration),
    method = protocol.methods![0]!;
  root.render(
    <ThemeProvider mode="light">
      <SpecimenMetadataForm
        key={request.sample_id}
        method={method}
        draft={draft}
        busy={false}
        onDraft={async (value) => {
          (window as any).lastSpecimenDraft = value;
        }}
        onSubmit={async (value) => {
          const body = validateCollectionBody(
            { ...request, ...value },
            method,
            protocol,
          );
          (window as any).participantCalls.push({ kind: "specimen", body });
        }}
      />
    </ThemeProvider>,
  );
};
// The production component receives exact fictional HTTP receipts; callbacks
// replace only the unavailable account/HTTP boundary, never a measured result.
(window as any).renderLabLifecycle = (configuration: any, flow: any) => {
  const check: any = {
    id: flow.context.session_id,
    snapshot: {
      sample: clone(flow.collection_receipt.projection.sample),
      study_id: configuration.study_id,
      saliva: [],
    },
    attempts: [clone(flow.collection_receipt.attempt)],
    labCollection: {
      attempt_id: flow.collection_request.attempt_id,
      sample_id: flow.collection_request.sample_id,
      collection_method_id: flow.collection_request.collection_method_id,
      collection_method_version:
        flow.collection_request.collection_method_version,
      state: "pending_lab",
      body: clone(flow.collection_request),
      receipt: clone(flow.collection_receipt),
    },
  };
  const controller: any = {
    check,
    epoch: "fictional-dom",
    run: async (action: () => Promise<void>) => action(),
    saveCheck: async () => {
      (window as any).participantCalls.push({
        kind: "save",
        state: check.labCollection.state,
        frozen: false,
      });
    },
    refreshLabCollection: async () => {
      check.labCollection.state = "imported";
      check.labCollection.receipt = clone(flow.import_status);
      check.snapshot.saliva = clone(flow.import_status.imports[0].measurements);
      (window as any).participantCalls.push({
        kind: "refresh",
        sample: check.snapshot.sample.sample_id,
      });
      render();
    },
    abandonLabAnalysis: async () => {
      check.labCollection.state = "canceled";
      (window as any).participantCalls.push({
        kind: "abandon",
        sample: check.snapshot.sample.sample_id,
      });
      render();
    },
    ask: (sheet: any) => {
      (window as any).participantCalls.push({
        kind: "confirmation",
        text: sheet.text,
      });
      (window as any).confirmLaboratoryEnd = () => sheet.action();
    },
  };
  const render = () =>
    root.render(
      <ThemeProvider mode="light">
        <ApprovedLabCollection
          controller={controller}
          model={{ busy: false } as any}
          configuration={configuration}
        />
      </ThemeProvider>,
    );
  render();
};
