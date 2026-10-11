import React, { useMemo, useState } from "react";
import { View } from "react-native";
import { localReplacementChecks } from "../core/replacements";
import {
  verifyReportCache,
  type ReportCompanion,
} from "../core/reportRevisions";
import { formatSalivaMeasurement } from "./measurement-format";
import type { ScreenProps } from "./account";
import { action, dateLabel, friendly, shortId } from "./account";
import {
  ActionRow,
  Badge,
  Button,
  Card,
  Fact,
  Notice,
  Paragraph,
  Title,
} from "./components";

export function ReplacementLinksCard({ controller, model }: ScreenProps) {
  const check = controller.check,
    epoch = controller.epoch;
  if (!check?.frozen || !model.state) return null;
  const local = localReplacementChecks(model.state, check),
    cache = check.replacement_links;
  const cached =
    cache &&
    cache.schema_version === "1.0.0" &&
    cache.session_id === check.id &&
    cache.data_generation === check.generation &&
    cache.base_snapshot_sha256 === check.snapshot_sha256
      ? cache
      : null;
  const localOnly = local.items.filter(
    (item) => !cached?.items.some((row) => row.session_id === item.id),
  );
  const open = (targetId: string, direction: "previous" | "replacement") =>
    action(controller, () => {
      if (controller.epoch !== epoch) return;
      return controller.openLinkedCheck(check.id, targetId, direction);
    });
  return (
    <Card>
      <Title small>Acquisition lineage</Title>
      <Paragraph>
        Replacement checks have new acquisition times and new measurements. Each
        original captured record remains unchanged. Laboratory report revisions
        are shown separately.
      </Paragraph>
      {check.snapshot.supersedes_session_id ? (
        <>
          <Badge>This check replaces an earlier acquisition</Badge>
          {local.previous && (
            <Fact
              label="Original check started"
              value={dateLabel(local.previous.snapshot.created_at)}
            />
          )}
          {!local.previous && cached?.previous && (
            <Fact
              label="Original check started"
              value={dateLabel(cached.previous.created_at)}
            />
          )}
          <Button
            title="View original check"
            secondary
            disabled={
              model.busy ||
              (!local.previous && (!model.identity || model.offline))
            }
            onPress={open(check.snapshot.supersedes_session_id, "previous")}
            testID="view-original-check"
          />
          {!local.previous && (!model.identity || model.offline) && (
            <Notice>
              The original is not saved in this active device workspace.
              Reconnect to load an available account record.
            </Notice>
          )}
        </>
      ) : (
        <Paragraph muted>
          This record does not replace an earlier acquisition.
        </Paragraph>
      )}
      <Title small>Replacement checks</Title>
      {cached?.items.map((item) => (
        <ActionRow
          key={item.session_id}
          title={`View replacement check ${shortId(item.session_id)}`}
          detail={`Started ${dateLabel(item.created_at)} · ${friendly(item.state)} · service link`}
          onPress={open(item.session_id, "replacement")}
        />
      ))}
      {localOnly.map((item) => (
        <ActionRow
          key={item.id}
          title={`View replacement check ${shortId(item.id)}`}
          detail={`Started ${dateLabel(item.snapshot.created_at)} · ${friendly(item.delivery)} · saved on this device`}
          onPress={open(item.id, "replacement")}
        />
      ))}
      {!cached?.items.length && !localOnly.length && (
        <Paragraph muted>
          No replacement checks are currently available in this view.
        </Paragraph>
      )}
      {cached && (
        <Fact
          label="Service links checked"
          value={dateLabel(cached.observed_at)}
        />
      )}
      {model.identity && (!cached || model.offline || cached.next_cursor) && (
        <Paragraph muted>
          More links may be available when connected. Only available device
          records and verified service pages are shown.
        </Paragraph>
      )}
      {!!model.identity && check.remote_revision > 0 && (
        <>
          <Button
            title="Refresh replacement links"
            secondary
            busy={model.busy}
            onPress={action(controller, () =>
              controller.refreshReplacementLinks(),
            )}
          />
          {cached?.next_cursor && (
            <Button
              title="Load more replacement links"
              secondary
              busy={model.busy}
              onPress={action(controller, () =>
                controller.refreshReplacementLinks(true),
              )}
            />
          )}
        </>
      )}
    </Card>
  );
}

export function ReportRevisionsCard({ controller, model }: ScreenProps) {
  const check = controller.check,
    epoch = controller.epoch,
    [selected, setSelected] = useState<string | null>(null),
    [provenance, setProvenance] = useState(false);
  const verified = useMemo(() => {
    if (!check?.report_revision_cache) return { cache: null, error: null };
    try {
      return {
        cache: verifyReportCache(check.report_revision_cache, check),
        error: null,
      };
    } catch {
      return {
        cache: null,
        error:
          "Saved laboratory history could not be verified. Refresh it before opening or exporting revised reports.",
      };
    }
  }, [
    check?.report_revision_cache,
    check?.snapshot_sha256,
    check?.evidence_sha256,
    check?.result,
  ]);
  if (!check?.frozen) return null;
  const cache = verified.cache,
    item = cache?.companions.find((value) => value.revision_id === selected),
    selectedIndex =
      cache?.list.items.findIndex((value) => value.revision_id === selected) ??
      -1,
    canFetch = !!model.identity && check.remote_revision > 0 && !!check.result;
  const choose = (id: string | null) => {
    if (epoch !== controller.epoch || controller.check?.id !== check.id) return;
    setSelected(id);
    setProvenance(false);
  };
  return (
    <Card>
      <Title small>Laboratory report history</Title>
      <Paragraph>
        Corrections and later analyses concern the original specimen. They
        preserve the original acquisition time, physiological evidence and
        captured result.
      </Paragraph>
      {verified.error && <Notice tone="danger">{verified.error}</Notice>}
      {check.snapshot.mode === "synthetic" && (
        <Notice>
          Synthetic checks cannot acquire a reference laboratory report. Their
          fictional values remain labeled as synthetic.
        </Notice>
      )}
      {!cache && !verified.error && check.snapshot.mode !== "synthetic" && (
        <Paragraph muted>
          No report revision history has been downloaded for this original
          record. Reconnect and refresh to check for available laboratory
          reports.
        </Paragraph>
      )}
      {cache && (
        <>
          <Fact label="History checked" value={dateLabel(cache.observed_at)} />
          <Fact
            label="Verified reports saved on this device"
            value={`${cache.companions.length} of ${cache.list.items.length}`}
          />
          {cache.companions.length < cache.list.items.length && (
            <Notice tone="warning">
              This cached history is incomplete. Refresh laboratory reports to
              load the remaining records before a device export; a partial chain
              is never silently exported.
            </Notice>
          )}
          {!cache.list.items.length && (
            <Paragraph muted>
              No laboratory report revisions were available when this history
              was checked.
            </Paragraph>
          )}
          {!selected &&
            cache.list.items.map((entry) => (
              <ActionRow
                key={entry.revision_id}
                title={`View ${entry.kind === "correction" ? "corrected laboratory report" : "later specimen analysis"} · revision ${entry.sequence}`}
                detail={`Report issued ${dateLabel(entry.reported_at)} · ${cache.companions.some((c) => c.revision_id === entry.revision_id) ? "saved on this device" : "detail requires refresh"}`}
                onPress={() => choose(entry.revision_id)}
              />
            ))}
        </>
      )}
      {selected && (
        <>
          <Button
            title="View original captured record"
            secondary
            onPress={() => choose(null)}
            testID="report-view-original"
          />
          {!item ? (
            <Notice>
              The selected report detail is not saved on this device. Refresh
              this history to verify and open it.
            </Notice>
          ) : (
            <>
              <Badge>
                {item.descriptor.report.kind === "correction"
                  ? "Corrected laboratory report"
                  : "Later specimen analysis"}
              </Badge>
              <Title small>Report revision {item.sequence}</Title>
              <Notice>
                Administrative report result · measurement only. This is a
                report about the original specimen; it does not determine
                present intoxication or driving safety.
              </Notice>
              <Fact
                label="Original check started / assessment target"
                value={dateLabel(item.descriptor.original_target_at)}
              />
              <Fact
                label="Original specimen collected"
                value={dateLabel(item.descriptor.original_collected_at)}
              />
              <Fact
                label="Original capture completed"
                value={dateLabel(item.descriptor.original_capture_completed_at)}
              />
              <Fact
                label="Laboratory report issued"
                value={dateLabel(item.descriptor.report.reported_at)}
              />
              <Fact
                label="Report accepted by service"
                value={dateLabel(item.accepted_at)}
              />
              <Fact
                label="Revised report evaluated"
                value={dateLabel(item.result.evaluated_at)}
              />
              <Fact
                label="Administrative result state"
                value={friendly(item.result.state)}
              />
              <Fact
                label="Reasons retained"
                value={item.result.reason_codes.map(friendly).join(", ")}
              />
              <Title small>Effective laboratory report</Title>
              <Paragraph muted>
                Changed analytes carry this report’s analytical times. Unchanged
                analytes retain their earlier records and provenance.
              </Paragraph>
              {item.effective_measurements.map((measurement) => {
                const presentation = formatSalivaMeasurement(measurement),
                  changed =
                    item.descriptor.report.replacement_measurements.some(
                      (m) => m.measurement_id === measurement.measurement_id,
                    );
                return (
                  <View
                    key={String(measurement.measurement_id)}
                    style={{ gap: 9, marginVertical: 7 }}
                  >
                    <Title small>
                      {presentation.name} · {presentation.title}
                    </Title>
                    <Badge>
                      {changed
                        ? "Changed in this report"
                        : "Carried forward unchanged"}
                    </Badge>
                    <Paragraph>{presentation.explanation}</Paragraph>
                    <Fact
                      label="Measured (UTC)"
                      value={
                        typeof measurement.measured_at === "string"
                          ? measurement.measured_at
                          : "Not measured"
                      }
                    />
                    {provenance &&
                      presentation.facts.map((fact) => (
                        <Fact
                          key={fact.label}
                          label={fact.label}
                          value={fact.value}
                        />
                      ))}
                  </View>
                );
              })}
              <Button
                title={
                  provenance
                    ? "Hide report provenance"
                    : "Show report provenance"
                }
                secondary
                onPress={() => setProvenance((value) => !value)}
              />
              {provenance && <ReportProvenance item={item} />}
              <View style={{ gap: 10 }}>
                {selectedIndex > 0 && (
                  <Button
                    title="Previous laboratory report"
                    secondary
                    onPress={() =>
                      choose(cache!.list.items[selectedIndex - 1]!.revision_id)
                    }
                  />
                )}
                {cache && selectedIndex < cache.list.items.length - 1 && (
                  <Button
                    title="Next laboratory report"
                    secondary
                    onPress={() =>
                      choose(cache.list.items[selectedIndex + 1]!.revision_id)
                    }
                  />
                )}
              </View>
            </>
          )}
        </>
      )}
      {canFetch && check.snapshot.mode !== "synthetic" && (
        <Button
          title="Refresh laboratory reports"
          secondary
          busy={model.busy}
          onPress={action(controller, () =>
            controller.refreshReportRevisions(),
          )}
        />
      )}
      {model.offline && (
        <Paragraph muted>
          Only previously verified reports saved in this active workspace can be
          read offline. New revisions may exist on the service.
        </Paragraph>
      )}
    </Card>
  );
}
function ReportProvenance({ item }: { item: ReportCompanion }) {
  const report = item.descriptor.report;
  return (
    <>
      <Fact label="Report revision ID" value={item.revision_id} />
      <Fact label="Report descriptor SHA-256" value={item.revision_sha256} />
      <Fact label="Administrative result SHA-256" value={item.result_sha256} />
      <Fact
        label="Original snapshot SHA-256"
        value={item.descriptor.base_snapshot_sha256}
      />
      <Fact
        label="Original evidence SHA-256"
        value={item.descriptor.base_evidence_sha256}
      />
      <Fact
        label="Source PDF artifact"
        value={report.source_report.artifact_id}
      />
      <Fact
        label="Source PDF version"
        value={report.source_report.version_id}
      />
      <Fact label="Source PDF SHA-256" value={report.source_report.sha256} />
      <Fact
        label="Approved laboratory configuration"
        value={report.authorization.configuration_id}
      />
      <Fact
        label="Configuration SHA-256"
        value={report.authorization.configuration_sha256}
      />
      <Fact
        label="Operator account reference"
        value={report.authorization.operator_account_ref}
      />
      <Fact
        label="Consent record reference"
        value={report.authorization.consent_record_id}
      />
      <Paragraph muted>
        Raw source PDFs are excluded from this app’s ordinary exports. These
        records preserve authorization provenance; they do not create a new
        assay qualification or clinical interpretation.
      </Paragraph>
    </>
  );
}
