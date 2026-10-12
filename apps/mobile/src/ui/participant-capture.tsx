import React, { useEffect, useRef, useState } from "react";
import { AppState, Platform } from "react-native";
import {
  participantProtocol,
  type InstructionInput,
} from "../core/participantAcquisition";
import type { ApprovedConfiguration } from "../core/acquisition";
import { PreparationClock } from "../core/preparationClock";
import { BUILD } from "../platform/config";
import { action, type ScreenProps } from "./account";
import {
  Button,
  Choice,
  Fact,
  Notice,
  Paragraph,
  SwitchRow,
  Title,
} from "./components";

export function ParticipantPreparation({
  configuration,
  channel,
  busy,
  onPrepare,
  onCapture,
  onStop,
  rawAllowed = false,
}: {
  configuration: ApprovedConfiguration;
  channel: "cardiac" | "ecg";
  busy: boolean;
  onPrepare: () => Promise<string>;
  onCapture: (input: InstructionInput, recordRaw: boolean) => Promise<void>;
  onStop: () => Promise<void>;
  rawAllowed?: boolean;
}) {
  const protocol = participantProtocol(configuration);
  const [error, setError] = useState<string | null>(null);
  const [setup, setSetup] = useState(""),
    [confirmed, setConfirmed] = useState<string[]>([]),
    [restStart, setRestStart] = useState<string | null>(null),
    [remaining, setRemaining] = useState(protocol.rest_duration_seconds!),
    [record, setRecord] = useState(false);
  const clock = useRef(new PreparationClock()),
    running = useRef(false),
    preparing = useRef(false),
    operationEpoch = useRef(0);
  const reset = () => {
    ++operationEpoch.current;
    preparing.current = false;
    clock.current.reset();
    running.current = false;
    setRestStart(null);
    setRemaining(protocol.rest_duration_seconds!);
    setConfirmed([]);
    setRecord(false);
  };
  useEffect(() => {
    const timer = setInterval(() => {
      if (running.current) {
        setRemaining(clock.current.remaining(protocol.rest_duration_seconds!));
        if (!clock.current.active) {
          reset();
          setError(
            "The monotonic rest clock changed. Start a new approved rest period.",
          );
          void onStop();
        }
      }
    }, 200);
    const stop = () => {
      if (running.current || preparing.current) {
        reset();
        void onStop();
      }
    };
    const subscription = AppState.addEventListener("change", (state) => {
      if (state !== "active") stop();
    });
    const visibility = () => {
      if (
        typeof document !== "undefined" &&
        document.visibilityState !== "visible"
      )
        stop();
    };
    if (typeof document !== "undefined")
      document.addEventListener("visibilitychange", visibility);
    return () => {
      clearInterval(timer);
      subscription.remove();
      if (typeof document !== "undefined")
        document.removeEventListener("visibilitychange", visibility);
      const active = running.current || preparing.current;
      ++operationEpoch.current;
      preparing.current = false;
      clock.current.reset();
      running.current = false;
      if (active) void onStop();
    };
  }, []);
  const unavailable =
    channel === "ecg" && protocol.operating_scope === "human_participant";
  return (
    <>
      <Title small>Approved preparation instructions</Title>
      {error && <Notice>{error}</Notice>}
      <Fact
        label="Instruction identity"
        value={`${protocol.instruction_id} · ${protocol.version}`}
      />
      <Fact
        label="Instruction SHA-256"
        value={configuration.participant_protocol_sha256!}
      />
      <Paragraph>{protocol.text}</Paragraph>
      <Fact label="Posture" value={protocol.posture_instruction!} />
      <Fact label="Activity" value={protocol.activity_instruction!} />
      <Fact label="Contact / leads" value={protocol.contact_instruction!} />
      <Fact label="Isolation" value={protocol.isolation_instruction!} />
      <Notice>
        These confirmations are participant declarations. They do not observe
        charging, cable, power or isolation state and do not establish
        electrical safety approval.
      </Notice>
      {unavailable && (
        <Notice>
          Human ECG acquisition is unavailable: this installed adapter cannot
          independently verify the released whole-system power, charging, cable
          and isolation state. A checkbox cannot enable it.
        </Notice>
      )}
      <Choice
        label="Approved whole-system setup"
        value={setup}
        options={protocol.permitted_setups!.map((item) => ({
          value: item.id,
          label: item.description,
        }))}
        onChange={(value) => {
          if (restStart) {
            reset();
            void onStop();
          }
          setSetup(value);
        }}
      />
      {protocol
        .permitted_setups!.filter((item) => item.id === setup)
        .map((item) => (
          <React.Fragment key={item.id}>
            <Fact label="Power state" value={item.power_state} />
            <Fact label="Charging state" value={item.charging_state} />
            <Fact label="Cable state" value={item.cable_state} />
            <Fact
              label="Contact configuration"
              value={item.contact_or_lead_configuration}
            />
          </React.Fragment>
        ))}
      <Button
        title="Start approved rest period"
        busy={busy}
        disabled={unavailable || !setup || !!restStart}
        onPress={() =>
          void (async () => {
            const epoch = ++operationEpoch.current;
            preparing.current = true;
            await onPrepare();
            if (epoch !== operationEpoch.current) return;
            preparing.current = false;
            clock.current.start();
            running.current = true;
            setRestStart(new Date().toISOString());
            setRemaining(
              clock.current.remaining(protocol.rest_duration_seconds!),
            );
            setConfirmed([]);
          })().catch((error) => {
            reset();
            setError(
              error instanceof Error
                ? error.message
                : "Preparation could not be admitted.",
            );
          })
        }
      />
      <Paragraph>
        {restStart
          ? `Required foreground rest: ${remaining} seconds remaining.`
          : `Rest required: ${protocol.rest_duration_seconds} seconds. Begin only after the service saves the preparation attempt.`}
      </Paragraph>
      <Paragraph>
        Leaving the app or interrupting preparation resets the wait and every
        confirmation. A wall-clock change cannot shorten the monotonic wait.
      </Paragraph>
      {protocol.required_confirmations.map((item) => (
        <SwitchRow
          key={item.id}
          title={item.text}
          value={confirmed.includes(item.id)}
          disabled={
            unavailable ||
            !restStart ||
            (item.id === "rest_completed" && remaining > 0)
          }
          onChange={(value) =>
            setConfirmed((items) =>
              value
                ? [...items, item.id]
                : items.filter((id) => id !== item.id),
            )
          }
        />
      ))}
      {channel === "ecg" && (
        <SwitchRow
          title="Record optional ECG samples for this capture"
          value={record && rawAllowed}
          disabled={!rawAllowed || unavailable}
          detail="Off by default. Separate optional recording permission, approved bounded signed sample codec and encrypted native storage are required; upload is a later explicit choice."
          onChange={setRecord}
        />
      )}
      <Button
        title={`Start authorized ${channel === "cardiac" ? "pulse" : "ecg"} capture`}
        busy={busy}
        disabled={
          unavailable ||
          !restStart ||
          remaining > 0 ||
          !setup ||
          confirmed.length !== protocol.required_confirmations.length
        }
        onPress={() =>
          void (async () => {
            if (
              clock.current.remaining(protocol.rest_duration_seconds!) > 0 ||
              !clock.current.active ||
              !restStart
            )
              return;
            const input: InstructionInput = {
              participant_protocol_sha256:
                configuration.participant_protocol_sha256!,
              acknowledged_at: new Date().toISOString(),
              confirmed: true,
              confirmations: [...confirmed],
              setup_id: setup,
              rest_started_at: restStart,
              collection_method_id: null,
              collection_method_version: null,
            };
            const requested = record && rawAllowed;
            setRecord(false);
            await onCapture(input, requested);
            reset();
          })().catch((error) => {
            reset();
            setError(
              error instanceof Error
                ? error.message
                : "Preparation could not be admitted.",
            );
          })
        }
      />
      {restStart && (
        <Button
          title="End preparation and reset confirmations"
          secondary
          onPress={() => {
            reset();
            void onStop();
          }}
        />
      )}
    </>
  );
}

export function ApprovedParticipantCapture({
  controller,
  model,
  configuration,
  channel,
}: ScreenProps & {
  configuration: ApprovedConfiguration;
  channel: "cardiac" | "ecg";
}) {
  const check = controller.check!,
    studyId = check.snapshot.study_id!,
    status = model.state?.rawRecordingStatuses[studyId];
  const preparationScope = useRef<{
    epoch: string;
    checkId: string;
    attemptId: string | null;
    intent: number;
  } | null>(null);
  const rawAllowed =
    channel === "ecg" &&
    Platform.OS !== "web" &&
    !BUILD.hostedPreview &&
    !!status?.receipt_id &&
    status.choices.ecg_waveform.record &&
    status.availability.ecg_waveform.record_allowed &&
    !model.state?.rawRecordingFences[studyId]?.includes("ecg_waveform") &&
    !!status.policy &&
    Date.parse(status.policy.expires_at) > Date.now();
  const invoke = async (operation: () => Promise<void>) => {
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
  return (
    <>
      {check.attempts.some(
        (a) =>
          a.status === "started" &&
          check.acquisition?.attempts[a.attempt_id]?.instruction_body &&
          !check.acquisition?.attempts[a.attempt_id]?.instruction_receipt,
      ) && (
        <Button
          title="Reconcile saved acknowledgment without starting hardware"
          secondary
          onPress={action(controller, () =>
            controller.reconcileInstructionReceipt(),
          )}
        />
      )}
      <ParticipantPreparation
        configuration={configuration}
        channel={channel}
        busy={model.busy}
        rawAllowed={rawAllowed}
        onPrepare={async () => {
          let at = "";
          await controller.run(async () => {
            const operation = controller.prepareParticipantCapture(channel);
            preparationScope.current = {
              epoch: controller.epoch,
              checkId: check.id,
              attemptId: null,
              intent: controller.preparationGeneration,
            };
            at = await operation;
          });
          if (!at) throw new Error("Preparation was not admitted.");
          const attempt = controller.check?.attempts.find(
            (a) =>
              a.status === "started" &&
              a.started_at === at &&
              a.configuration_id === configuration.configuration_id,
          );
          if (!attempt || controller.check?.id !== check.id)
            throw new Error("Preparation scope changed.");
          if (preparationScope.current)
            preparationScope.current.attemptId = attempt.attempt_id;
          return at;
        }}
        onCapture={(input, record) =>
          invoke(async () => {
            const operation = controller.captureReader(
              channel === "cardiac" ? "ppg" : "ecg",
              record,
              input,
            );
            const scope = preparationScope.current;
            if (
              scope &&
              scope.epoch === controller.epoch &&
              scope.checkId === controller.check?.id
            )
              scope.intent = controller.preparationGeneration;
            await operation;
          })
        }
        onStop={async () => {
          const scope = preparationScope.current;
          preparationScope.current = null;
          if (!scope) return;
          await controller.runPrivacy(() =>
            controller.stopPreparedCapture(
              scope.epoch,
              scope.checkId,
              scope.intent,
              scope.attemptId,
            ),
          );
        }}
      />
    </>
  );
}
