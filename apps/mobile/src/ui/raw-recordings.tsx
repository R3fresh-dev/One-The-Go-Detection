import React from "react";
import { action, dateLabel, friendly, type ScreenProps } from "./account";
import {
  Badge,
  Button,
  Card,
  Fact,
  Notice,
  Page,
  Paragraph,
  Title,
} from "./components";
import { RawChoicesCard, rawKindNames as names } from "./raw-choices";
export function RawRecordingsScreen({ controller, model }: ScreenProps) {
  const studyId = model.rawStudyId,
    state = model.state;
  const status = studyId ? state?.rawRecordingStatuses[studyId] : null;
  const fences = studyId ? (state?.rawRecordingFences[studyId] ?? []) : [];
  return (
    <Page
      title="Recording choices & retention"
      eyebrow="Separate optional purpose"
      onBack={action(controller, () => controller.navigate("studies"))}
    >
      <Notice>
        Account and policy receipts authorize a purpose, never a sensor,
        scientific method or impairment estimate. A valid device and fresh
        capture authorization remain required.
      </Notice>
      {model.offline && (
        <Notice>
          Cached receipts are shown while offline. New recording permission is
          not confirmed from a cached policy. A stop request is durable and will
          reconcile when connected.
        </Notice>
      )}
      {studyId && (
        <Button
          secondary
          title="Refresh recording receipts and cleanup"
          onPress={action(controller, () =>
            controller.refreshRawRecordings(studyId),
          )}
        />
      )}
      <Card>
        <Title small>Encrypted recordings on this device</Title>
        {!(state?.rawArtifacts ?? []).some(
          (file) => file.study_id === studyId,
        ) && (
          <Paragraph>
            No device recording is indexed for this study. Raw acquisition is
            unavailable in the browser; there is no plaintext fallback.
          </Paragraph>
        )}
        {(state?.rawArtifacts ?? [])
          .filter((file) => file.study_id === studyId)
          .map((file) => (
            <React.Fragment key={file.local_id}>
              <Fact
                label="Device recording"
                value={`${file.artifact_kind === "eye_video" ? "Eye ROI frames" : "ECG waveform"} · ${file.local_id}`}
              />
              <Badge>{friendly(file.state)}</Badge>
              <Fact
                label="Exact bytes and checksum"
                value={`${file.size_bytes} bytes · ${file.sha256}`}
              />
              <Fact
                label="Device cleanup deadline"
                value={dateLabel(file.retention_due_at)}
              />
              {file.error && <Notice>{file.error}</Notice>}
              {file.state !== "deleted" && (
                <Button
                  secondary
                  title={`Remove local recording ${file.local_id.slice(0, 8)}`}
                  onPress={() =>
                    void controller.runPrivacy(() =>
                      controller.ask({
                        title: "Remove this device recording?",
                        text: "The encrypted local bytes will be removed and dependent upload attempts stopped. Measurements and already accepted server artifacts remain; remote cleanup requires a separate revocation request.",
                        confirm: "Remove device copy",
                        interrupting: true,
                        danger: true,
                        action: () =>
                          controller.removeLocalRawFile(file.local_id),
                      }),
                    )
                  }
                />
              )}
            </React.Fragment>
          ))}
        <Paragraph>
          Expired or stopped bytes are purged before an unlocked workspace is
          exposed and during foreground maintenance. A stopped app cannot run a
          deletion timer; cleanup runs on its next open. Pending cleanup is
          shown until deletion succeeds.
        </Paragraph>
      </Card>
      {status && studyId ? (
        <>
          <RawChoicesCard
            key={JSON.stringify([
              controller.epoch,
              state?.generation,
              status.consent_record_id,
              status.policy?.sha256,
              status.policy?.raw_notice.sha256,
              status.receipt_id,
            ])}
            status={status}
            fences={fences}
            onSave={(choices) =>
              void controller.run(() =>
                controller.ask({
                  title: "Confirm optional raw recording choices?",
                  text: "Only these exact choices and this approved notice are recorded. No raw files are uploaded by this action. Reauthentication confirms the same account.",
                  confirm: "Reauthenticate and save choices",
                  action: () =>
                    controller.saveRawRecordingChoices(studyId, choices),
                }),
              )
            }
            onRevoke={(kinds) =>
              void controller.runPrivacy(() =>
                controller.ask({
                  title: "Stop recording and revoke uploads?",
                  interrupting: true,
                  text: "Acquisition stops locally before the request is sent. Existing quarantined or verified files follow the approved cleanup policy. Pending cleanup is not completed deletion.",
                  confirm: "Stop and request cleanup",
                  danger: true,
                  action: () => controller.revokeRawRecordings(studyId, kinds),
                }),
              )
            }
          />
          <Card>
            <Title small>Exact pending requests</Title>
            {state?.queue
              .filter(
                (q) =>
                  q.body.study_id === studyId &&
                  ["raw_preference", "raw_revocation"].includes(q.kind),
              )
              .map((q) => (
                <React.Fragment key={q.id}>
                  <Badge>
                    {friendly(q.kind)} · {friendly(q.state)}
                  </Badge>
                  <Fact label="Confirmed at" value={dateLabel(q.created_at)} />
                  {q.error && <Notice>{q.error}</Notice>}
                </React.Fragment>
              ))}
          </Card>
          <Card>
            <Title small>Server recording and cleanup receipts</Title>
            {!status.artifacts.length && (
              <Paragraph>
                No uploaded raw files are listed in this page of owned server
                records. Device-only recordings are separate.
              </Paragraph>
            )}
            {status.artifacts.map((file) => (
              <React.Fragment key={file.artifact_id}>
                <Fact label="Artifact" value={file.artifact_id} />
                <Badge>
                  {names[file.artifact_kind]} · {friendly(file.upload_state)} ·{" "}
                  {friendly(file.state)}
                </Badge>
                <Fact
                  label="Retention deadline"
                  value={dateLabel(file.retention_due_at)}
                />
                <Fact
                  label="Cleanup completed"
                  value={
                    file.cleanup_completed_at
                      ? dateLabel(file.cleanup_completed_at)
                      : "Not confirmed"
                  }
                />
              </React.Fragment>
            ))}
            {status.has_more_artifacts && (
              <>
                <Notice>
                  Additional server artifact records exist beyond this bounded
                  page. Refresh does not imply that older records have been
                  deleted.
                </Notice>
                <Button
                  secondary
                  title="View next page of server recordings"
                  onPress={action(controller, () =>
                    controller.refreshRawRecordings(
                      studyId,
                      status.next_artifact_cursor!,
                    ),
                  )}
                />
              </>
            )}
            {status.revocations.map((receipt) => (
              <Fact
                key={receipt.receipt_id}
                label={`Cleanup receipt ${receipt.receipt_id}`}
                value={`${receipt.artifact_kinds.map((kind) => names[kind]).join(", ")} · ${friendly(receipt.state)}`}
              />
            ))}
          </Card>
        </>
      ) : (
        <Card>
          <Paragraph>
            Load owned study recording receipts to review the exact policy. All
            choices remain off until verified.
          </Paragraph>
        </Card>
      )}
    </Page>
  );
}
