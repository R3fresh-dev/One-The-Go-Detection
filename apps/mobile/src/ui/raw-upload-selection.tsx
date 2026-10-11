import React from "react";
import type { RawArtifact } from "../core/rawArtifacts";
import type { RawKind } from "../core/rawRecordings";
import {
  Card,
  Title,
  Paragraph,
  SwitchRow,
  Fact,
  Badge,
  Notice,
} from "./components";
export function RawUploadSelectionCard({
  files,
  selected,
  fences,
  locked,
  onChange,
}: {
  files: RawArtifact[];
  selected: string[];
  fences: Record<string, RawKind[]>;
  locked: boolean;
  onChange: (ids: string[]) => void;
}) {
  return (
    <Card>
      <Title small>Optional raw upload selection</Title>
      <Paragraph>
        Saving measurements never queues recordings. Select each eligible
        encrypted recording explicitly for this upload. Leaving these choices
        off sends feature evidence only.
      </Paragraph>
      {!files.length && (
        <Paragraph>
          No encrypted raw recordings are retained for this check.
        </Paragraph>
      )}
      {files.map((file) => {
        const eligible =
          ["local", "queued", "uploaded"].includes(file.state) &&
          file.permission.upload &&
          Date.parse(file.retention_due_at) > Date.now() &&
          !fences[file.study_id]?.includes(file.artifact_kind);
        return (
          <React.Fragment key={file.local_id}>
            <SwitchRow
              title={`Include ${file.artifact_kind === "eye_video" ? "eye ROI recording" : "ECG waveform"} ${file.local_id.slice(0, 8)}`}
              value={selected.includes(file.local_id) && eligible}
              disabled={locked || !eligible}
              onChange={(value) =>
                onChange(
                  value
                    ? [...selected, file.local_id]
                    : selected.filter((id) => id !== file.local_id),
                )
              }
              detail={`${file.format} · ${file.size_bytes} bytes · ${file.state}`}
            />
            <Fact label="Raw bytes SHA-256" value={file.sha256} />
            <Fact
              label="Retention deadline"
              value={new Date(file.retention_due_at).toLocaleString()}
            />
            <Badge>{file.state}</Badge>
            {!eligible && (
              <Notice>
                This recording is unavailable for upload: permission, expiry or
                a local stop fence prevents inclusion.
              </Notice>
            )}
          </React.Fragment>
        );
      })}
      {locked && (
        <Notice>
          A requested upload keeps its original immutable raw selection.
          Finalized uploads cannot acquire additional recordings.
        </Notice>
      )}
    </Card>
  );
}
