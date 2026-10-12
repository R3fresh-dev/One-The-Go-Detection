import React from "react";
const { createRoot } = require("react-dom/client") as {
  createRoot: (element: Element) => { render: (view: React.ReactNode) => void };
};
import { RawChoicesCard } from "../../src/ui/raw-choices";
import { parseRawRecordingStatus } from "../../src/core/rawRecordings";
import { ThemeProvider } from "../../src/ui/theme";
import { RawExportChoicesCard } from "../../src/ui/raw-export-choices";
import { parseRawExportPage } from "../../src/core/rawExport";
import { RawUploadSelectionCard } from "../../src/ui/raw-upload-selection";
import type { RawArtifact } from "../../src/core/rawArtifacts";
import type { ExportSelection } from "../../src/core/types";

const root = createRoot(document.getElementById("root")!);
(window as any).rawEvents = [];
(window as any).renderRaw = (
  value: any,
  scope = "account-A:g1",
  fences: string[] = [],
) => {
  const status = parseRawRecordingStatus(value, value.study_id);
  root.render(
    <ThemeProvider mode="light">
      <RawChoicesCard
        key={JSON.stringify([
          scope,
          status.consent_record_id,
          status.policy?.sha256,
          status.policy?.raw_notice.sha256,
          status.receipt_id,
        ])}
        status={status}
        fences={fences as any}
        onSave={(choices) =>
          (window as any).rawEvents.push({ kind: "save", choices })
        }
        onRevoke={(kinds) =>
          (window as any).rawEvents.push({ kind: "revoke", kinds })
        }
      />
    </ThemeProvider>,
  );
};
(window as any).renderRawExport = (
  value: any,
  scope = "account-A:g1",
  selection: ExportSelection = { kind: "all", session_ids: [] },
) => {
  const authority = parseRawExportPage(value).scopes[0]!;
  root.render(
    <ThemeProvider mode="light">
      <RawExportChoicesCard
        key={JSON.stringify([scope, authority, selection])}
        authority={authority}
        selection={selection}
        onChange={(choice) =>
          (window as any).rawEvents.push({ kind: "export_choice", choice })
        }
      />
    </ThemeProvider>,
  );
};
function Upload({ files, fences }: { files: RawArtifact[]; fences: any }) {
  const [selected, setSelected] = React.useState<string[]>([]);
  return (
    <RawUploadSelectionCard
      files={files}
      selected={selected}
      fences={fences}
      locked={false}
      onChange={(ids) => {
        setSelected(ids);
        (window as any).rawEvents.push({ kind: "upload_choice", ids });
      }}
    />
  );
}
(window as any).renderRawUpload = (
  files: RawArtifact[],
  scope = "account-A:g1",
  fences: any = {},
) =>
  root.render(
    <ThemeProvider mode="light">
      <Upload key={scope} files={files} fences={fences} />
    </ThemeProvider>,
  );
