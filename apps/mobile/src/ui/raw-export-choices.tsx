import React, { useState } from "react";
import type { RawExportAuthority } from "../core/rawExport";
import type { ExportSelection } from "../core/types";
import {
  Button,
  Card,
  Fact,
  Notice,
  Paragraph,
  SwitchRow,
  Title,
} from "./components";
export interface RawExportChoice {
  authorization_id: string;
  authority_sha256: string;
  notice_sha256: string;
  artifact_ids: string[];
}
export function RawExportChoicesCard({
  authority,
  selection,
  onChange,
  onNext,
}: {
  authority: RawExportAuthority;
  selection: ExportSelection;
  onChange: (choice: RawExportChoice | null) => void;
  onNext?: () => void;
}) {
  const [read, setRead] = useState(false),
    [ack, setAck] = useState(false),
    [selected, setSelected] = useState<string[]>([]);
  const expired = Date.parse(authority.expires_at) <= Date.now();
  const publish = (ids: string[], confirmed: boolean) =>
    onChange(
      confirmed && ids.length
        ? {
            authorization_id: authority.authorization_id,
            authority_sha256: authority.authorization_sha256,
            notice_sha256: authority.export_notice.sha256,
            artifact_ids: ids,
          }
        : null,
    );
  return (
    <Card>
      <Title small>Separate authorized raw export</Title>
      <Paragraph>
        Raw exports require this distinct approved purpose. Recording or upload
        choices never select an export. Default exports contain structured
        evidence only.
      </Paragraph>
      <Fact label="Export purpose" value={authority.purpose_text} />
      <Fact
        label="Export authorization"
        value={`${authority.authorization_id} · ${authority.authorization_version}`}
      />
      <Fact label="Authority SHA-256" value={authority.authorization_sha256} />
      <Fact
        label="Authorization expires"
        value={new Date(authority.expires_at).toLocaleString()}
      />
      <Fact
        label="Maximum export lifetime"
        value={`${authority.max_export_lifetime_seconds} seconds; original recording retention may shorten this`}
      />
      <Button
        secondary
        title={
          read
            ? "Hide complete raw export notice"
            : "Read complete raw export notice"
        }
        onPress={() => setRead(!read)}
      />
      {read && (
        <>
          <Paragraph>{authority.export_notice.content}</Paragraph>
          <Fact
            label="Exact export notice SHA-256"
            value={authority.export_notice.sha256}
          />
        </>
      )}
      {authority.artifacts.map((file) => {
        const allowed =
          !expired &&
          file.size_bytes <= authority.max_uncompressed_bytes &&
          Date.parse(file.retained_until) > Date.now() &&
          (selection.kind === "all" ||
            selection.session_ids.includes(file.session_id));
        return (
          <React.Fragment key={file.artifact_id}>
            <SwitchRow
              title={`Export raw ${file.kind === "eye_video" ? "eye ROI frames" : "ECG waveform"} ${file.artifact_id.slice(0, 8)}`}
              value={selected.includes(file.artifact_id) && allowed}
              disabled={!allowed}
              onChange={(value) => {
                const next = value
                  ? [...selected, file.artifact_id]
                  : selected.filter((id) => id !== file.artifact_id);
                setSelected(next);
                publish(next, ack);
              }}
              detail={`${file.size_bytes} bytes · check ${file.session_id} · retained until ${new Date(file.retained_until).toLocaleString()}`}
            />
            {!allowed && (
              <Notice>
                This source is expired or outside the exact selected checks; it
                cannot be included.
              </Notice>
            )}
          </React.Fragment>
        );
      })}
      {!authority.artifacts.length && (
        <Paragraph>
          No verified eligible artifacts appear in this bounded page.
        </Paragraph>
      )}
      <SwitchRow
        title="I reviewed this exact separate raw export purpose and selected sources"
        value={ack}
        disabled={!read || expired || !selected.length}
        onChange={(value) => {
          setAck(value);
          publish(selected, value);
        }}
        detail="Sharing an archive creates recipient copies that cannot be recalled. Unchecked for changed account, generation, policy, page or source scope."
      />
      {expired && (
        <Notice>
          Export authorization expired. Structured evidence export remains
          separate.
        </Notice>
      )}
      {authority.artifacts_next_cursor && onNext && (
        <Button
          secondary
          title="Review next page of eligible raw export sources"
          onPress={onNext}
        />
      )}
    </Card>
  );
}
