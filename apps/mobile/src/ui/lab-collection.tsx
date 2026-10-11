import React, { useState } from "react";
import {
  participantProtocol,
  COLLECTION_NULL_FIELDS,
  type CollectionMethod,
  type InstructionInput,
} from "../core/participantAcquisition";
import type { ApprovedConfiguration } from "../core/acquisition";
import { clone, requireObject } from "../core/integrity";
import type { JsonObject } from "../core/types";
import { action, friendly, type ScreenProps } from "./account";
import {
  Button,
  Card,
  Choice,
  Fact,
  Field,
  Notice,
  Paragraph,
  SwitchRow,
  Title,
} from "./components";

export function LabMethodConfirmation({
  configuration,
  busy,
  onStart,
}: {
  configuration: ApprovedConfiguration;
  busy: boolean;
  onStart: (input: InstructionInput) => Promise<void>;
}) {
  const protocol = participantProtocol(configuration),
    [methodId, setMethod] = useState(""),
    [confirmations, setConfirmations] = useState<string[]>([]),
    [error, setError] = useState<string | null>(null);
  const method = protocol.methods!.find((item) => item.id === methodId);
  return (
    <>
      <Title small>Approved laboratory collection</Title>
      <Paragraph>{protocol.text}</Paragraph>
      <Fact
        label="Instructions"
        value={`${protocol.instruction_id} · ${protocol.version}`}
      />
      <Fact
        label="Instruction SHA-256"
        value={configuration.participant_protocol_sha256!}
      />
      <Notice>
        This method collects a specimen for independent laboratory analysis. It
        does not use a Bluetooth reader or accept participant-entered
        concentrations.
      </Notice>
      <Choice
        label="Choose the approved collection method"
        value={methodId}
        options={protocol.methods!.map((method) => ({
          value: method.id,
          label: `${method.id} · ${method.version}`,
        }))}
        onChange={(value) => {
          setMethod(value);
          setConfirmations([]);
          setError(null);
        }}
      />
      {method && (
        <>
          <Paragraph>{method.instructions}</Paragraph>
          <Fact
            label="Dilution convention"
            value={
              method.dilution_definition ??
              "No approved dilution convention required"
            }
          />
          <Paragraph>
            Submit the actual specimen metadata within{" "}
            {protocol.maximum_collection_submission_delay_seconds} seconds of
            collection. Analysis must occur within{" "}
            {protocol.maximum_analysis_delay_seconds} seconds; the server checks
            the independently imported report.
          </Paragraph>
        </>
      )}
      {protocol.required_confirmations.map((item) => (
        <SwitchRow
          key={item.id}
          title={item.text}
          value={confirmations.includes(item.id)}
          disabled={!method}
          onChange={(value) =>
            setConfirmations((items) =>
              value
                ? [...items, item.id]
                : items.filter((id) => id !== item.id),
            )
          }
        />
      ))}
      {error && <Notice>{error}</Notice>}
      <Button
        title="Acknowledge method and start specimen draft"
        busy={busy}
        disabled={
          !method ||
          confirmations.length !== protocol.required_confirmations.length
        }
        onPress={() => {
          if (!method) return;
          void onStart({
            participant_protocol_sha256:
              configuration.participant_protocol_sha256!,
            acknowledged_at: new Date().toISOString(),
            confirmed: true,
            confirmations: [...confirmations],
            setup_id: null,
            rest_started_at: null,
            collection_method_id: method.id,
            collection_method_version: method.version,
          }).catch((error) =>
            setError(
              error instanceof Error
                ? error.message
                : "Collection could not start.",
            ),
          );
        }}
      />
    </>
  );
}

export function SpecimenMetadataForm({
  method,
  draft,
  busy,
  onDraft,
  onSubmit,
}: {
  method: CollectionMethod;
  draft?: JsonObject;
  busy: boolean;
  onDraft: (draft: JsonObject) => Promise<void>;
  onSubmit: (body: JsonObject) => Promise<void>;
}) {
  const [form, setForm] = useState<JsonObject>(() =>
      clone(
        draft ?? {
          collected_at: "",
          status: "",
          quality_flags: "",
          ...Object.fromEntries(COLLECTION_NULL_FIELDS.map((k) => [k, ""])),
          missing_reasons: {},
          storage_handling_events: {},
        },
      ),
    ),
    [error, setError] = useState<string | null>(null);
  const update = (key: string, value: any) => {
    const next = { ...form, [key]: value };
    setForm(next);
    void onDraft(next).catch((error) =>
      setError(
        error instanceof Error
          ? error.message
          : "The private draft could not be saved.",
      ),
    );
  };
  const submit = () => {
    const reasons = requireObject(form.missing_reasons),
      events = requireObject(form.storage_handling_events);
    const values = Object.fromEntries(
      COLLECTION_NULL_FIELDS.map((key) => [
        key,
        String(form[key] ?? "").trim() === ""
          ? null
          : [
                "saliva_volume_ml",
                "buffer_volume_ml",
                "dilution_factor",
              ].includes(key)
            ? Number(form[key])
            : String(form[key]).trim(),
      ]),
    );
    const body = {
      collected_at: form.collected_at,
      status: form.status,
      quality_flags: String(form.quality_flags)
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean),
      ...values,
      missing_reasons: Object.fromEntries(
        COLLECTION_NULL_FIELDS.filter((key) => values[key] === null).map(
          (key) => [key, reasons[key] ?? ""],
        ),
      ),
      storage_handling_events: Object.entries(events).map(([event, value]) => {
        const v = requireObject(value);
        return {
          event,
          occurred_at: v.occurred_at,
          temperature_c:
            v.temperature_c === "" ? null : Number(v.temperature_c),
          duration_min: v.duration_min === "" ? null : Number(v.duration_min),
        };
      }),
    } as unknown as JsonObject;
    void onSubmit(body).catch((error) =>
      setError(
        error instanceof Error
          ? error.message
          : "The specimen declaration could not be accepted.",
      ),
    );
  };
  return (
    <>
      <Title small>Actual specimen metadata</Title>
      <Paragraph>{method.instructions}</Paragraph>
      <Notice>
        Record observed collection facts. A blank field stays unknown and
        requires an approved reason; the app does not calculate a concentration
        or infer an unprovided volume.
      </Notice>
      <Button
        title="Record actual collection time now"
        secondary
        onPress={() => update("collected_at", new Date().toISOString())}
      />
      <Field
        label="Actual collection time (UTC)"
        value={String(form.collected_at)}
        onChangeText={(value) => update("collected_at", value)}
        helper="Preserve the original collection time; do not replace it with a retry time."
      />
      <Choice
        label="Specimen adequacy"
        value={String(form.status)}
        options={[
          {
            value: "valid",
            label: "Adequate according to the approved method",
          },
          { value: "invalid", label: "Inadequate / collection failed" },
        ]}
        onChange={(value) => update("status", value)}
      />
      <Field
        label="Actual inadequacy / quality reasons (comma separated)"
        value={String(form.quality_flags)}
        onChangeText={(value) => update("quality_flags", value)}
      />
      {COLLECTION_NULL_FIELDS.map((key) => (
        <React.Fragment key={key}>
          <Field
            label={
              key === "saliva_volume_ml"
                ? "Observed saliva volume (mL)"
                : key === "buffer_volume_ml"
                  ? "Observed buffer volume (mL)"
                  : key === "dilution_factor"
                    ? "Recorded dilution factor"
                    : friendly(key)
            }
            value={String(form[key])}
            onChangeText={(value) => update(key, value)}
            keyboardType={
              [
                "saliva_volume_ml",
                "buffer_volume_ml",
                "dilution_factor",
              ].includes(key)
                ? "decimal-pad"
                : "default"
            }
            helper={
              key === "dilution_factor"
                ? (method.dilution_definition ??
                  "Do not invent a dilution convention.")
                : key === "cartridge_expiry"
                  ? "Actual UTC expiry timestamp, or an approved unknown reason."
                  : undefined
            }
          />
          {String(form[key]).trim() === "" && (
            <Choice
              label={`Reason for unknown ${friendly(key)}`}
              value={String(requireObject(form.missing_reasons)[key] ?? "")}
              options={method.permitted_null_reasons.map((reason) => ({
                value: reason,
                label: friendly(reason),
              }))}
              onChange={(value) =>
                update("missing_reasons", {
                  ...requireObject(form.missing_reasons),
                  [key]: value,
                })
              }
            />
          )}
        </React.Fragment>
      ))}
      {method.required_handling_events.map((event) => {
        const value = requireObject(
          requireObject(form.storage_handling_events)[event] ?? {
            occurred_at: "",
            temperature_c: "",
            duration_min: "",
          },
        );
        const set = (field: string, v: string) =>
          update("storage_handling_events", {
            ...requireObject(form.storage_handling_events),
            [event]: { ...value, [field]: v },
          });
        return (
          <Card key={event}>
            <Title small>{friendly(event)}</Title>
            <Button
              title={`Record ${event} now`}
              secondary
              onPress={() => set("occurred_at", new Date().toISOString())}
            />
            <Fact
              label="Recorded event time"
              value={String(value.occurred_at)}
            />
            <Field
              label={`${event} temperature (°C), if observed`}
              value={String(value.temperature_c)}
              onChangeText={(v) => set("temperature_c", v)}
              keyboardType="decimal-pad"
            />
            <Field
              label={`${event} duration (minutes), if observed`}
              value={String(value.duration_min)}
              onChangeText={(v) => set("duration_min", v)}
              keyboardType="decimal-pad"
            />
          </Card>
        );
      })}
      {error && <Notice>{error}</Notice>}
      <Button
        title="Submit exact specimen declaration"
        busy={busy}
        disabled={!form.collected_at || !form.status}
        onPress={submit}
      />
    </>
  );
}

export function ApprovedLabCollection({
  controller,
  model,
  configuration,
}: ScreenProps & { configuration: ApprovedConfiguration }) {
  const check = controller.check!,
    ledger = check.labCollection,
    protocol = participantProtocol(configuration);
  const perform = async (operation: () => Promise<void>) => {
    let failure: unknown;
    await controller.run(async () => {
      try {
        await operation();
      } catch (error) {
        failure = error;
        throw error;
      }
    });
    if (failure) throw failure;
  };
  if (ledger?.state === "canceled")
    return (
      <>
        <Notice>
          The pending analysis ended explicitly. The actual specimen, collection
          receipt and declarations remain in history. Start a new check to
          collect a fresh specimen; the current protocol decides whether this
          check can finish without chemical analysis.
        </Notice>
        <Fact label="Original specimen identity" value={ledger.sample_id} />
        <Fact
          label="Original collection time"
          value={String(ledger.body?.collected_at)}
        />
        <Button
          title="Save remaining check with specimen history"
          onPress={action(controller, () => controller.saveCheck())}
        />
      </>
    );
  if (!ledger || ledger.state === "invalid")
    return (
      <>
        {check.attempts.some(
          (a) =>
            a.status === "started" &&
            check.acquisition?.attempts[a.attempt_id]?.instruction_body &&
            !check.acquisition?.attempts[a.attempt_id]?.instruction_receipt,
        ) && (
          <Button
            title="Reconcile saved acknowledgment without starting collection"
            secondary
            onPress={action(controller, () =>
              controller.reconcileInstructionReceipt(),
            )}
          />
        )}
        {ledger && (
          <Notice>
            The previous specimen and its failure or explicitly ended analysis
            remain in the attempt history. A new collection requires a fresh
            specimen identity and method acknowledgment. An explicitly ended
            analysis requires a new check.
          </Notice>
        )}
        <LabMethodConfirmation
          configuration={configuration}
          busy={model.busy}
          onStart={(input) =>
            perform(() => controller.startLabCollection(input))
          }
        />
      </>
    );
  const method = protocol.methods!.find(
    (m) =>
      m.id === ledger.collection_method_id &&
      m.version === ledger.collection_method_version,
  );
  if (!method)
    return (
      <Notice>
        The selected collection method changed. Preserve this draft and review
        the current study protocol before collecting another specimen.
      </Notice>
    );
  return (
    <>
      <Fact label="Specimen identity" value={ledger.sample_id} />
      <Fact label="Collection attempt" value={ledger.attempt_id} />
      <Fact
        label="Acknowledged method"
        value={`${method.id} · ${method.version}`}
      />
      {ledger.state === "collecting" ? (
        <SpecimenMetadataForm
          key={ledger.attempt_id}
          method={method}
          draft={ledger.draft}
          busy={model.busy}
          onDraft={(draft) =>
            controller.saveLabCollectionDraft(
              check.id,
              ledger.attempt_id,
              draft,
            )
          }
          onSubmit={(body) =>
            perform(() => controller.recordLabCollection(body))
          }
        />
      ) : (
        <>
          <Notice tone={ledger.state === "imported" ? "neutral" : "warning"}>
            {ledger.state === "imported"
              ? "Independent laboratory analysis received. Review the retained report and measurements before saving and explicitly uploading."
              : "Laboratory analysis pending. This owned cloud check remains a draft; no concentration or probability is shown and finalization is blocked."}
          </Notice>
          <Fact
            label="Collection receipt"
            value={String(ledger.receipt?.collection_receipt_id)}
          />
          <Fact
            label="Original collection time"
            value={String(ledger.body?.collected_at)}
          />
          <Button
            title="Refresh independent laboratory analysis"
            busy={model.busy}
            onPress={action(controller, () =>
              controller.refreshLabCollection(),
            )}
          />
          {ledger.state === "pending_lab" && (
            <Button
              title="End pending laboratory analysis"
              secondary
              onPress={action(controller, () =>
                controller.ask({
                  title: "End this pending analysis?",
                  text: "The actual specimen receipt stays in history. No chemical result will be selected, and a delayed report cannot revive this canceled analysis. The current protocol still decides whether the remaining check can finalize.",
                  confirm: "End analysis and preserve specimen receipt",
                  action: () => controller.abandonLabAnalysis(),
                }),
              )}
            />
          )}
        </>
      )}
      <Button
        title={
          ledger.state === "pending_lab"
            ? "Save pending draft and resume later"
            : "Save collection draft"
        }
        secondary
        onPress={action(controller, () => controller.saveCheck())}
      />
    </>
  );
}
