import React, { useState } from "react";
import { clone } from "../core/integrity";
import {
  RAW_KINDS,
  rawChoicesOff,
  type RawChoices,
  type RawKind,
  type RawRecordingStatus,
} from "../core/rawRecordings";
import {
  Button,
  Card,
  Fact,
  Notice,
  Paragraph,
  SwitchRow,
  Title,
} from "./components";
const dateLabel = (value: string) => new Date(value).toLocaleString();
const friendly = (value: string) => value.toLowerCase().replaceAll("_", " ");
export const rawKindNames: Record<RawKind, string> = {
  eye_video: "Eye video",
  ecg_waveform: "ECG waveform",
};

export function RawChoicesCard({
  status,
  fences,
  onSave,
  onRevoke,
}: {
  status: RawRecordingStatus;
  fences: RawKind[];
  onSave: (choices: RawChoices) => void;
  onRevoke: (kinds: RawKind[]) => void;
}) {
  const [choices, setChoices] = useState(() =>
    status.receipt_id ? clone(status.choices) : rawChoicesOff(),
  );
  const [read, setRead] = useState(false),
    [acknowledged, setAcknowledged] = useState(false);
  const policy = status.policy,
    expired = !policy || Date.parse(policy.expires_at) <= Date.now();
  const update = (kind: RawKind, field: "record" | "upload", value: boolean) =>
    setChoices((current) => ({
      ...current,
      [kind]: {
        ...current[kind],
        [field]: value,
        ...(field === "record" && !value ? { upload: false } : {}),
      },
    }));
  return (
    <Card>
      <Title small>Optional raw recordings</Title>
      <Paragraph>
        These choices are separate from study consent. Leaving every choice off
        preserves any authorized feature-only measurements. Saving a check
        locally never queues raw files.
      </Paragraph>
      {policy ? (
        <>
          <Fact label="Purpose" value={policy.purpose} />
          <Fact
            label="Approved policy"
            value={`${policy.policy_id} · ${policy.version}`}
          />
          <Fact label="Verified policy SHA-256" value={policy.sha256} />
          <Fact
            label="Retention limit"
            value={`${policy.max_retention_days} days from the first owned acquisition start`}
          />
          <Fact
            label="Policy authorization expires"
            value={dateLabel(policy.expires_at)}
          />
          <Fact
            label="Permitted access roles"
            value={policy.access_roles.join(", ")}
          />
          <Fact
            label="Withdrawal and deletion"
            value={policy.withdrawal_behavior}
          />
          <Fact
            label="Retention exceptions"
            value={policy.exceptions.join("; ") || "None in this policy"}
          />
          <Button
            secondary
            title={
              read
                ? "Hide raw recording notice"
                : "Read complete raw recording notice"
            }
            onPress={() => setRead(!read)}
          />
          {read && (
            <>
              <Paragraph>{policy.raw_notice.content}</Paragraph>
              <Fact
                label="Verified notice"
                value={`${policy.raw_notice.version} · ${policy.raw_notice.sha256}`}
              />
            </>
          )}
          {expired && (
            <Notice>
              Policy authorization has expired. New recording choices are
              unavailable; you can still stop recording and review cleanup.
            </Notice>
          )}
          {RAW_KINDS.map((kind) => {
            const allowed = status.availability[kind],
              stopped = fences.includes(kind);
            return (
              <React.Fragment key={kind}>
                <SwitchRow
                  title={`Record ${rawKindNames[kind].toLowerCase()} on this device`}
                  value={choices[kind].record && !stopped}
                  disabled={expired || !allowed.record_allowed || stopped}
                  onChange={(value) => update(kind, "record", value)}
                  detail="Optional local raw acquisition only. This does not authorize an upload."
                />
                <SwitchRow
                  title={`Allow explicit upload of ${rawKindNames[kind].toLowerCase()}`}
                  value={choices[kind].upload && !stopped}
                  disabled={
                    expired ||
                    !choices[kind].record ||
                    !allowed.upload_allowed ||
                    stopped
                  }
                  onChange={(value) => update(kind, "upload", value)}
                  detail="A separate Upload action and current server permission are required. Automatic check retries never opt you in."
                />
                {!!allowed.reasons.length && (
                  <Notice>
                    {rawKindNames[kind]} unavailable:{" "}
                    {allowed.reasons.map(friendly).join(", ")}.
                  </Notice>
                )}
                {stopped && (
                  <Notice>
                    {rawKindNames[kind]} stopped locally. Its exact revocation
                    request or physical cleanup may still be pending.
                  </Notice>
                )}
              </React.Fragment>
            );
          })}
          <SwitchRow
            title="I reviewed this exact raw recording notice and retention policy"
            value={acknowledged}
            onChange={setAcknowledged}
            disabled={!read || expired}
            detail="Unchecked for a new account, data generation, consent receipt, policy or notice."
          />
          <Button
            title="Confirm separate recording and upload choices"
            disabled={
              !read || !acknowledged || expired || !status.consent_record_id
            }
            onPress={() => {
              const effective = clone(choices);
              for (const kind of fences)
                effective[kind] = { record: false, upload: false };
              onSave(effective);
            }}
          />
        </>
      ) : (
        <Notice>
          No current approved raw recording policy is available. Recording and
          upload remain off.
        </Notice>
      )}
      {RAW_KINDS.map((kind) => (
        <Button
          key={kind}
          secondary
          title={`Stop and revoke ${rawKindNames[kind].toLowerCase()}`}
          onPress={() => onRevoke([kind])}
        />
      ))}
      <Fact
        label="Verified optional-purpose receipt"
        value={status.receipt_id ?? "No confirmed receipt"}
      />
    </Card>
  );
}
