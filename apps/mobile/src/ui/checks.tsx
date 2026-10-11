import React, { useEffect, useState } from "react";
import {
  AccessibilityInfo,
  AppState,
  Linking,
  Platform,
  ScrollView,
  Text,
  View,
  useWindowDimensions,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { getCameraPermissionStatus, type BluetoothPermissionStatus } from "../../modules/device-transport";
import {
  getReactionTaskAvailability,
  ReactionTaskView,
  REACTION_CONFIGURATION_ID,
  REACTION_CONFIGURATION_SHA256,
} from "../../modules/reaction-task";
import type { CaptureAttempt, CheckRecord, JsonObject, Stage } from "../core/types";
import { cardiacAttemptModality } from "../core/domain";
import { formatSalivaMeasurement } from "./measurement-format";
import { SignalPanel } from "../device/SignalPanel";
import { canonicalJson } from "../core/integrity";
import { BUILD } from "../platform/config";
import { ReplacementLinksCard, ReportRevisionsCard } from "./revisions";
import {
  action,
  ContextFacts,
  dateLabel,
  friendly,
  shortId,
  type ScreenProps,
} from "./account";
import {
  ActionRow,
  Badge,
  Button,
  Card,
  Choice,
  Fact,
  Label,
  Metric,
  Notice,
  Page,
  Paragraph,
  Row,
  SwitchRow,
  Title,
  layout,
} from "./components";
import { useTheme } from "./theme";

const stages: { id: Stage; title: string }[] = [
  { id: "profile", title: "Context" },
  { id: "device", title: "Device" },
  { id: "saliva", title: "Saliva" },
  { id: "eyes", title: "Eyes" },
  { id: "cardiac", title: "Pulse" },
  { id: "ecg", title: "ECG" },
  { id: "task", title: "Reaction" },
  { id: "review", title: "Review" },
];
const numberText = (value: unknown, digits = 0) =>
  typeof value === "number" && Number.isFinite(value)
    ? value.toFixed(digits)
    : "—";
export function Provenance({ check }: { check: CheckRecord }) {
  return (
    <Notice tone={check.kind === "measurement" ? "neutral" : "warning"}>
      {check.kind === "measurement"
        ? "Measurement record. Native reaction measurements are uncalibrated. Qualified sample and sensor acquisition is unavailable."
        : "Synthetic session: sample, eye, pulse, ECG and alcohol examples are fictional. Any actual native reaction taps are uncalibrated practice with separate provenance."}
    </Notice>
  );
}
function CurrentMeasurement({
  component,
  title,
}: {
  component: JsonObject;
  title: string;
}) {
  return (
    <Card>
      <Row>
        <Title small>{title}</Title>
        <Badge tone={component.status === "invalid" ? "danger" : "neutral"}>
          {friendly(component.status)}
        </Badge>
      </Row>
      <Fact label="Source" value={friendly(component.source)} />
      <Fact
        label="Quality"
        value={
          Array.isArray(component.quality_flags)
            ? component.quality_flags.join(", ")
            : "Not collected"
        }
      />
    </Card>
  );
}
function PassiveEyePreview() {
  const [permission, request, refreshPermission] = useCameraPermissions(),
    [open, setOpen] = useState(false),
    [error, setError] = useState<string | null>(null),
    [front, setFront] = useState(true),
    [osPermission, setOsPermission] = useState<BluetoothPermissionStatus>("unknown");
  useEffect(() => {
    let live = true;
    const refresh = async () => {
      const status = await getCameraPermissionStatus();
      const response = await refreshPermission();
      if (!live) return;
      setOsPermission(status);
      if (status === "restricted" || !response.granted) setOpen(false);
    };
    void refresh().catch(() => { if (live) setOsPermission("unknown"); });
    const sub = AppState.addEventListener("change", (s) => {
      if (s !== "active") setOpen(false);
      else void refresh().catch(() => { if (live) setOsPermission("unknown"); });
    });
    return () => { live = false; sub.remove(); };
  }, [refreshPermission]);
  return (
    <Card>
      <Label>Optional camera preview</Label>
      <Paragraph>
        A passive positioning preview only. No pupil diameter, light response or
        intoxication value is extracted. No image is captured, saved or
        uploaded, and no light or flash sequence runs.
      </Paragraph>
      {error && <Notice tone="danger">{error}</Notice>}
      {osPermission === "restricted" && (
        <Notice tone="warning">Camera access is restricted by device policy. The passive preview is unavailable. You can continue without it; ordinary app permission settings may not change this restriction.</Notice>
      )}
      {open && permission?.granted ? (
        <>
          <View style={{ height: 260, borderRadius: 16, overflow: "hidden" }}>
            <CameraView
              style={{ flex: 1 }}
              facing={front ? "front" : "back"}
              mode="picture"
              enableTorch={false}
              flash="off"
              mirror={front}
              onMountError={(e) => {
                setOpen(false);
                setError(e.message);
              }}
            />
            <View
              pointerEvents="none"
              style={{
                position: "absolute",
                bottom: 12,
                left: 12,
                right: 12,
                backgroundColor: "#102A36DD",
                padding: 10,
                borderRadius: 8,
              }}
            >
              <Text style={{ color: "white", textAlign: "center" }}>
                Passive preview · no measurement
              </Text>
            </View>
          </View>
          <Button
            title="Switch camera"
            secondary
            onPress={() => setFront((v) => !v)}
          />
          <Button
            title="Close preview"
            secondary
            onPress={() => setOpen(false)}
          />
        </>
      ) : (
        <>
          <Button
            title={
              osPermission === "restricted"
                ? "Camera access restricted"
                : permission?.granted
                ? "Open passive preview"
                : "Allow camera for preview"
            }
            secondary
            disabled={osPermission === "restricted"}
            onPress={() => {
              void (async () => {
                setError(null);
                const status = await getCameraPermissionStatus();
                setOsPermission(status);
                if (status === "restricted") { setOpen(false); return; }
                const current = await refreshPermission();
                const p = current.granted ? current : await request();
                const resolved = await getCameraPermissionStatus();
                setOsPermission(resolved);
                if (resolved === "restricted") { setOpen(false); return; }
                if (p.granted) setOpen(true);
                else
                  setError(
                    "Camera access was denied. You can continue without an eye measurement.",
                  );
              })().catch((e) => setError(String(e)));
            }}
          />
          {permission && !permission.granted && !permission.canAskAgain && osPermission === "denied" && (
            <Button
              title="Open device settings"
              secondary
              onPress={() => {
                void Linking.openSettings();
              }}
            />
          )}
        </>
      )}
    </Card>
  );
}
export function ActiveReactionScreen({ controller, model }: ScreenProps) {
  const active = model.activeTask!;
  return (
    <View style={{ flex: 1, backgroundColor: "#101820", minHeight: 400 }}>
      <View style={{ paddingHorizontal: 20, paddingVertical: 12, gap: 5 }}>
        <Text style={{ color: "#C2D8DB", fontSize: 12, fontWeight: "700" }}>
          UNCALIBRATED NATIVE PRACTICE
        </Text>
        <Text style={{ color: "#FFFFFF", fontSize: 14 }}>
          {model.taskProgress ?? "Preparing task"} · use End task to stop
          immediately
        </Text>
        {model.error && (
          <>
            <Text accessibilityRole="alert" style={{ color: "#FFC3C3", fontSize: 14 }}>{model.error}</Text>
            <Text style={{ color: "#FFFFFF", fontSize: 14 }}>End task again to retry saving its terminal evidence. The same ended run stays on screen until its evidence is preserved.</Text>
            <Button title="Retry saving ended task" secondary onPress={action(controller, () => controller.stopActive("USER_CANCELED"))} />
          </>
        )}
      </View>
      <ReactionTaskView
        ref={(value) => {
          controller.nativeView = value;
        }}
        style={{ flex: 1, minHeight: 400 }}
        runId={active.runId}
        seed={active.seed}
        running
        configurationId={REACTION_CONFIGURATION_ID}
        configurationSha256={REACTION_CONFIGURATION_SHA256}
        workspaceEpoch={active.epoch}
        onProgress={(event) => {
          const x = event.nativeEvent;
          controller.updateProgress(
            x.runId,
            x.workspaceEpoch,
            x.phase,
            x.presented,
          );
        }}
        onComplete={(event) => {
          void controller.completeNativeTask(event.nativeEvent).catch(error => controller.report(error));
        }}
      />
    </View>
  );
}
export function CheckScreen({ controller, model }: ScreenProps) {
  const check = controller.check,
    [instructions, setInstructions] = useState(false),
    [screenReader, setScreenReader] = useState(false),
    dimensions = useWindowDimensions();
  useEffect(() => {
    void AccessibilityInfo.isScreenReaderEnabled().then(setScreenReader);
    const sub = AccessibilityInfo.addEventListener(
      "screenReaderChanged",
      setScreenReader,
    );
    return () => sub.remove();
  }, []);
  if (!check)
    return (
      <Page title="No active check">
        <Card>
          <Paragraph>
            Start a check after confirming your current profile and context.
          </Paragraph>
          <Button
            title="Go to home"
            onPress={action(controller, () => controller.navigate("home"))}
          />
        </Card>
      </Page>
    );
  if (model.activeTask)
    return <ActiveReactionScreen controller={controller} model={model} />;
  const stage = check.stage,
    index = stages.findIndex((x) => x.id === stage),
    synthetic = check.kind !== "measurement",
    taskAvailability = getReactionTaskAvailability(),
    nativeGeometry =
      dimensions.width >= 240 &&
      dimensions.height >= 560 &&
      dimensions.height > dimensions.width;
  const continueTo = () =>
    controller.setStage(stages[Math.min(index + 1, stages.length - 1)]!.id);
  const validCardiac = check.attempts.filter(a => a.component === "cardiac" && a.status === "valid");
  const cardiacChoicePending = validCardiac.length > 1 && !check.selected_cardiac_attempt_id;
  const requestedCardiacModality = stage === "ecg" ? "ecg" : "ppg";
  const cardiacAlreadyCaptured = validCardiac.some(a => cardiacAttemptModality(a) === requestedCardiacModality);
  const renderedEpoch = controller.epoch;
  const signalScopeCurrent = () => controller.epoch === renderedEpoch && controller.check?.id === check.id && controller.check.stage === stage;
  const skip = () =>
    controller.ask({
      title: "Continue without this measurement?",
      text: "The component stays explicitly not collected or retains its invalid attempt. Missing values are not treated as zero. You can revisit an unfinished component before saving.",
      confirm: "Continue without measurement",
      action: continueTo,
    });
  return (
    <Page
      title={stages[index]?.title ?? "Guided check"}
      eyebrow={`Check ${index + 1} of ${stages.length} · ${shortId(check.id)}`}
      onBack={action(controller, () =>
        controller.ask({
          title: "Leave this draft?",
          text: "Your draft and completed attempts stay on this device. An ended reaction task never resumes; an invalid attempt requires a new run.",
          confirm: "Keep draft and leave",
          action: () => controller.navigate("home"),
          secondary: {
            title: "Discard this draft",
            action: () =>
              controller.ask({
                title: "Discard unsaved check?",
                text: "This removes the local draft and its attempt evidence. It has never been uploaded.",
                confirm: "Discard draft",
                danger: true,
                action: () => controller.discardDraft(),
              }),
          },
        }),
      )}
    >
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ gap: 8, paddingBottom: 3 }}
      >
        {stages.map((x, i) => (
          <Button
            key={x.id}
            compact
            secondary={stage !== x.id}
            title={`${i + 1} ${x.title}`}
            onPress={action(controller, () => controller.setStage(x.id))}
          />
        ))}
      </ScrollView>
      <Provenance check={check} />
      {stage === "profile" && (
        <>
          <Card>
            <Title small>Frozen at Start check</Title>
            <Fact
              label="Check time"
              value={dateLabel(check.snapshot.created_at)}
            />
            <Fact
              label="Profile revision ID"
              value={
                check.context.profile_version_id ?? "No saved profile revision"
              }
            />
            <ContextFacts
              profile={{
                ...model.state!.profile,
                profile: check.snapshot.profile,
                history: check.snapshot.history,
                context: check.context.self_report_context,
              }}
            />
            <Notice>
              This exact context is read only. Changing the current profile
              later affects a new check.
            </Notice>
          </Card>
          <Button
            title="Continue to device"
            onPress={action(controller, continueTo)}
          />
        </>
      )}
      {stage === "device" && (
        <>
          <Card>
            <Title small>Choose what is available</Title>
            <Paragraph>
              Qualified hardware is not configured for this release. You may
              inspect nearby engineering devices or use the fictional local
              transport. Native reaction practice runs on the phone.
            </Paragraph>
            <Button
              title="Devices and connection"
              secondary
              onPress={action(controller, () => controller.navigate("device"))}
            />
            <Fact label="Qualified reader" value="Unavailable" />
            <Fact
              label="Phone reaction module"
              value={
                taskAvailability.available
                  ? "Installed · uncalibrated"
                  : "Unavailable in this runtime"
              }
            />
          </Card>
          <Button
            title="Continue to saliva"
            onPress={action(controller, continueTo)}
          />
        </>
      )}
      {stage === "saliva" && (
        <>
          <Card>
            <Title small>One saliva sample</Title>
            <Paragraph>
              A quantitative result needs a qualified oral-fluid collection
              method, compatible reader, cartridge lot, calibration and
              analyte-specific limits. The app does not turn a phone sensor or
              an unqualified reader signal into a concentration.
            </Paragraph>
            <Notice tone="warning">
              Qualified assay unavailable. THC or metabolite detection alone
              cannot confirm current intoxication.
            </Notice>
            {synthetic && (
              <Button
                title={
                  check.snapshot.sample.status === "valid"
                    ? "Fictional saliva example already added"
                    : "Add fictional saliva example"
                }
                disabled={check.snapshot.sample.status === "valid"}
                onPress={action(controller, () =>
                  controller.simulate("saliva"),
                )}
                testID="simulate-saliva"
              />
            )}
          </Card>
          {synthetic && (
            <Button
              secondary
              title="Capture saliva from connected simulator"
              disabled={check.snapshot.sample.status === "valid"}
              onPress={action(controller, () =>
                controller.simulateDevice("saliva"),
              )}
            />
          )}
          {check.snapshot.saliva.length > 0 && <SalivaCard check={check} />}
          <Button
            title={
              check.snapshot.sample.status === "valid"
                ? "Continue to eyes"
                : "Continue without saliva measurement"
            }
            secondary={check.snapshot.sample.status !== "valid"}
            onPress={action(
              controller,
              check.snapshot.sample.status === "valid" ? continueTo : skip,
            )}
          />
        </>
      )}
      {stage === "eyes" && (
        <>
          <Card>
            <Title small>Eye measurement</Title>
            <Paragraph>
              Physical pupil diameter needs a known scale. A light-response
              measurement also needs an approved optical configuration and
              timing evidence. This release has neither.
            </Paragraph>
            <Notice tone="warning">
              Unqualified optics · measurement unavailable
            </Notice>
            {synthetic && (
              <Button
                title={
                  check.snapshot.eyes.status === "valid"
                    ? "Fictional eye example already added"
                    : "Add fictional eye example"
                }
                disabled={check.snapshot.eyes.status === "valid"}
                onPress={action(controller, () => controller.simulate("eyes"))}
              />
            )}
          </Card>
          <PassiveEyePreview />
          <CurrentMeasurement
            title="Eye evidence"
            component={check.snapshot.eyes}
          />
          <Button
            title={
              check.snapshot.eyes.status === "valid"
                ? "Continue to pulse"
                : "Continue without eye measurement"
            }
            onPress={action(
              controller,
              check.snapshot.eyes.status === "valid" ? continueTo : skip,
            )}
          />
        </>
      )}
      {(stage === "cardiac" || stage === "ecg") && (
        <>
          <Card>
            <Title small>
              {stage === "ecg"
                ? "ECG is a separate signal"
                : "Pulse measurement"}
            </Title>
            <Paragraph>
              {stage === "ecg"
                ? "ECG needs a qualified electrode-based acquisition device, contact quality and sampling evidence. Phone PPG and heart rate do not supply an ECG."
                : "PPG estimates pulse from an optical signal. Motion, contact and acquisition quality belong with every measurement. No qualified live PPG configuration is available."}
            </Paragraph>
            <Notice tone="warning">
              {stage === "ecg" ? "Qualified ECG" : "Qualified PPG"} unavailable.
              This check can retain one valid PPG and one valid ECG before saving.
              If both are collected, Review requires you to choose one cardiac
              observation for the final snapshot. Both original attempts stay in
              the evidence ledger. A valid attempt of the same modality cannot
              be retaken within this check.
            </Notice>
            {synthetic && (
              <Button
                title={
                  stage === "ecg"
                    ? cardiacAlreadyCaptured
                      ? "Fictional ECG example already added"
                      : "Add fictional ECG example"
                    : cardiacAlreadyCaptured
                      ? "Fictional pulse example already added"
                      : "Add fictional pulse example"
                }
                disabled={cardiacAlreadyCaptured}
                onPress={action(controller, () =>
                  controller.simulate(
                    "cardiac",
                    stage === "ecg" ? "ecg" : "ppg",
                  ),
                )}
              />
            )}
          </Card>
          {synthetic && (
            <SignalPanel
              key={`${check.id}:${stage}:${controller.epoch}`}
              device={controller.device}
              sessionId={check.id}
              workspaceEpoch={controller.epoch}
              channel={stage === "ecg" ? "ecg" : "ppg"}
              disabled={cardiacAlreadyCaptured}
              onStart={async scenario => { if (signalScopeCurrent()) await controller.simulateDevice(requestedCardiacModality, scenario); }}
              onStop={async () => { if (signalScopeCurrent()) await controller.stopActive("USER_CANCELED"); }}
              onDevices={async () => { if (signalScopeCurrent()) await controller.setStage("device"); }}
              onError={error => { if (signalScopeCurrent()) controller.report(error); }}
            />
          )}
          <CurrentMeasurement
            title={cardiacChoicePending ? "Cardiac preview (choice pending)" : "Selected cardiac evidence"}
            component={check.snapshot.cardiac}
          />
          {cardiacChoicePending && <Notice tone="warning">Both cardiac observations are retained. Choose PPG or ECG on Review before saving; the current preview is not a final selection.</Notice>}
          {check.snapshot.cardiac.status === "valid" && (
            <Card>
              <Row>
                <Metric
                  label="Saved heart rate"
                  value={numberText(check.snapshot.cardiac.heart_rate_bpm)}
                  unit="bpm"
                />
                <Metric
                  label="ECG RMSSD"
                  value={numberText(check.snapshot.cardiac.ecg_rmssd_ms)}
                  unit="ms"
                  detail={
                    check.snapshot.cardiac.modality === "ppg"
                      ? "Not measured by PPG"
                      : "Fictional ECG example"
                  }
                />
              </Row>
              <Fact
                label="Modality"
                value={friendly(check.snapshot.cardiac.modality)}
              />
            </Card>
          )}
          <Button
            title={`Continue to ${stage === "ecg" ? "reaction task" : "ECG"}`}
            onPress={action(controller, continueTo)}
          />
        </>
      )}
      {stage === "task" && (
        <>
          <Card>
            <Row>
              <Title small>One reaction task</Title>
              <Badge tone="warning">Uncalibrated native practice</Badge>
            </Row>
            <Paragraph>
              Tap the side the arrow points to. When WAIT appears, do not tap.
            </Paragraph>
            <View style={layout.grid}>
              <Card style={{ flexGrow: 1 }}>
                <Title small>← Left</Title>
                <Paragraph>Tap Left</Paragraph>
              </Card>
              <Card style={{ flexGrow: 1 }}>
                <Title small>Right →</Title>
                <Paragraph>Tap Right</Paragraph>
              </Card>
              <Card style={{ flexGrow: 1 }}>
                <Title small>WAIT</Title>
                <Paragraph>Do not tap</Paragraph>
              </Card>
            </View>
            <Paragraph>
              Six practice trials and 60 scored trials run continuously,
              approximately two minutes. Hold the device still in portrait. Use
              End task to stop immediately; the run becomes invalid and cannot
              resume.
            </Paragraph>
            <Notice>
              The native clock and input events are recorded. Physical
              display/touch timing and luminance are unmeasured. This task does
              not determine intoxication or driving safety.
            </Notice>
            {check.kind === "engineering_fixture" && (
              <Notice tone="warning">
                Authenticated fictional fixtures remain entirely fictional. To
                record real reaction taps, save this fixture and start a
                separate measurement check.
              </Notice>
            )}
            {screenReader && (
              <Notice tone="warning">
                Screen-reader input is not qualified for this fixed visual task.
                You may continue without it. Adapted input must use a separately
                identified practice configuration.
              </Notice>
            )}
            {(!taskAvailability.available || !nativeGeometry) && (
              <Notice tone="warning">
                {!taskAvailability.available
                  ? `Native task unavailable: ${taskAvailability.reason ?? "install a native build"}. Web and Expo Go do not produce native task evidence.`
                  : "Hold a supported phone in portrait. The native task requires at least 240 × 400 logical points after the screen header."}
              </Notice>
            )}
            {check.snapshot.task.status !== "valid" && (
              <>
                <SwitchRow
                  title="I understand the task instructions."
                  detail="No network or unrelated storage work runs during the native task."
                  value={instructions}
                  onChange={setInstructions}
                />
                <Button
                  title={
                    check.snapshot.task.status === "invalid"
                      ? "Start a new task attempt"
                      : "Start task"
                  }
                  disabled={
                    !instructions ||
                    !taskAvailability.available ||
                    !nativeGeometry ||
                    screenReader ||
                    check.kind === "engineering_fixture"
                  }
                  onPress={action(controller, () =>
                    controller.startNativeTask(),
                  )}
                  testID="start-native-task"
                />
              </>
            )}
          </Card>
          <TaskCard check={check} />
          <Button
            title={
              check.snapshot.task.status === "valid"
                ? "Review check"
                : "Continue without a valid task"
            }
            onPress={action(
              controller,
              check.snapshot.task.status === "valid" ? continueTo : skip,
            )}
          />
        </>
      )}
      {stage === "review" && (
        <>
          <Card>
            <Title small>Review before saving</Title>
            <Paragraph>
              Saving freezes this snapshot and its evidence manifest on this
              device. New measurements after saving require a replacement check
              with a new start time.
            </Paragraph>
            <Fact
              label="Saliva"
              value={friendly(check.snapshot.sample.status)}
            />
            <Fact label="Eyes" value={friendly(check.snapshot.eyes.status)} />
            <Fact
              label="Cardiac"
              value={cardiacChoicePending ? "Two valid observations · selection required" : `${friendly(check.snapshot.cardiac.status)} · ${friendly(check.snapshot.cardiac.modality)}`}
            />
            <Fact
              label="Reaction task"
              value={friendly(check.snapshot.task.status)}
            />
            <Fact
              label="Alcohol"
              value={
                check.alcohol ? "Separate evidence included" : "Not collected"
              }
            />
            <Fact
              label="Capture attempts retained"
              value={String(check.attempts.length)}
            />
            <Fact label="Upload" value="Nothing queued by saving" />
          </Card>
          <CardiacSelectionCard controller={controller} model={model} />
          <SalivaCard check={check} />
          <Button
            title="Save on this device"
            onPress={action(controller, () => controller.saveCheck())}
            busy={model.busy}
            disabled={cardiacChoicePending}
            testID="save-check"
          />
          <Button
            title="Review attempt evidence"
            secondary
            onPress={action(controller, () => controller.navigate("evidence"))}
          />
        </>
      )}
      <Paragraph muted>
        Check context: {dateLabel(check.snapshot.created_at)}. Each component
        retains its own acquisition time. Missing and censored values are never
        filled with zero.
      </Paragraph>
    </Page>
  );
}
function CardiacAttemptFacts({ attempt }: { attempt: CaptureAttempt }) {
  const projection = (attempt.component_metadata.projection ?? {}) as JsonObject;
  const transport = (attempt.component_metadata.transport_evidence ?? {}) as JsonObject;
  const values = (transport.values ?? {}) as JsonObject;
  const start = attempt.started_at ? Date.parse(attempt.started_at) : NaN;
  const end = attempt.ended_at ? Date.parse(attempt.ended_at) : NaN;
  return <>
    <Fact label="Attempt" value={attempt.attempt_id} />
    <Fact label="Source" value={friendly(attempt.source)} />
    <Fact label="Status" value={friendly(attempt.status)} />
    <Fact label="Heart rate" value={typeof projection.heart_rate_bpm === "number" ? `${projection.heart_rate_bpm} bpm` : "Not available"} />
    <Fact label="Started (UTC)" value={attempt.started_at ?? "Not collected"} />
    <Fact label="Ended (UTC)" value={attempt.ended_at ?? "Not collected"} />
    <Fact label="Observed duration" value={Number.isFinite(start) && Number.isFinite(end) && end >= start ? `${(end - start) / 1000} s` : "Not available"} />
    <Fact label="Sample rate" value={typeof projection.sample_rate_hz === "number" ? `${projection.sample_rate_hz} Hz` : "Not reported"} />
    <Fact label="Lead count" value={cardiacAttemptModality(attempt) === "ecg" ? typeof values.lead_count === "number" ? String(values.lead_count) : "Not reported" : "Not applicable to PPG"} />
    <Fact label="Waveform scale" value={values.units === "arbitrary_counts" ? "Arbitrary counts (synthetic; no mV calibration)" : cardiacAttemptModality(attempt) === "ecg" ? "No calibrated voltage scale reported" : "PPG optical signal; no ECG waveform"} />
    <Fact label="ECG RMSSD" value={typeof projection.ecg_rmssd_ms === "number" ? `${projection.ecg_rmssd_ms} ms${attempt.source === "simulated" ? " (fictional)" : ""}` : "Not available"} />
    <Fact label="Configuration" value={attempt.configuration_id ?? "Not reported"} />
    <Fact label="Quality flags" value={attempt.quality_flags.join(", ") || "None reported"} />
  </>;
}
function CardiacSelectionCard({ controller, model }: ScreenProps) {
  const check = controller.check;
  if (!check) return null;
  const attempts = check.attempts.filter(a => a.component === "cardiac" && a.status === "valid");
  if (!attempts.length) return null;
  const selected = check.frozen ? check.manifest?.selected.cardiac : check.selected_cardiac_attempt_id ?? (attempts.length === 1 ? attempts[0]!.attempt_id : null);
  return <Card>
    <Title small>{check.frozen ? "Retained cardiac observations" : "Choose the cardiac observation"}</Title>
    <Paragraph>The saved v0.1 snapshot contains one cardiac observation. PPG and ECG remain separate attempts with their original source, timing and quality. All retained attempts are included in evidence and scoped export.</Paragraph>
    {attempts.length > 1 && !selected && <Notice tone="warning">Selection required: choose PPG or ECG to enable Save on this device.</Notice>}
    {attempts.map(attempt => <Card key={attempt.attempt_id}>
      <Row>
        <Title small>{cardiacAttemptModality(attempt)?.toUpperCase() ?? "Unknown modality"}</Title>
        <Badge tone={selected === attempt.attempt_id ? "accent" : "neutral"}>{selected === attempt.attempt_id ? "Selected for snapshot" : "Retained alternative"}</Badge>
      </Row>
      <CardiacAttemptFacts attempt={attempt} />
      {!check.frozen && <Button
        title={selected === attempt.attempt_id ? `${cardiacAttemptModality(attempt)?.toUpperCase()} selected` : `Select ${cardiacAttemptModality(attempt)?.toUpperCase()} for this check`}
        secondary={selected !== attempt.attempt_id}
        disabled={selected === attempt.attempt_id || model.busy}
        onPress={action(controller, () => controller.selectCardiac(attempt.attempt_id))}
        testID={`select-cardiac-${cardiacAttemptModality(attempt)}`}
      />}
    </Card>)}
    {check.frozen && <Paragraph muted>The selected modality is frozen. A later acquisition requires a replacement check with a new start time.</Paragraph>}
  </Card>;
}
function SalivaMeasurementDetail({ measurement }: { measurement: JsonObject }) {
  const [expanded, setExpanded] = useState(false);
  const display = formatSalivaMeasurement(measurement);
  return <View style={{ gap: 7, paddingVertical: 12 }}>
    <Row style={{ justifyContent: "space-between" }}>
      <Label>{display.name}</Label>
      <Badge tone={measurement.source === "simulated" ? "warning" : "neutral"}>{friendly(measurement.source)}</Badge>
    </Row>
    <Title small>{display.title}</Title>
    <Paragraph muted>{display.explanation}</Paragraph>
    {display.facts.slice(0, 9).map(fact => <Fact key={fact.label} {...fact} />)}
    <Button title={expanded ? "Hide original report and provenance" : "Show original report and provenance"} secondary onPress={() => setExpanded(value => !value)} />
    {expanded && display.facts.slice(9).map(fact => <Fact key={fact.label} {...fact} />)}
  </View>;
}
export function SalivaCard({ check }: { check: CheckRecord }) {
  return (
    <Card>
      <Title small>Saliva measurements</Title>
      <Fact label="Sample" value={shortId(check.snapshot.sample.sample_id)} />
      <Fact
        label="Collected"
        value={
          check.snapshot.sample.collected_at
            ? dateLabel(check.snapshot.sample.collected_at)
            : "Not collected"
        }
      />
      <Fact label="Collection method" value={friendly(check.snapshot.sample.collection_method_id)} />
      <Fact label="Sample status" value={friendly(check.snapshot.sample.status)} />
      <Fact label="Collected volume" value={typeof check.snapshot.sample.volume_ml === "number" ? `${check.snapshot.sample.volume_ml} mL` : "Not reported"} />
      <Fact label="Reported dilution factor" value={typeof check.snapshot.sample.dilution_factor === "number" ? String(check.snapshot.sample.dilution_factor) : "Not reported"} />
      <Paragraph muted>Limits and concentrations use the reporting method's stated matrix and analyte basis. This app does not calculate or repeat a dilution correction. Missing concentrations remain null.</Paragraph>
      {check.snapshot.saliva.length ? (
        check.snapshot.saliva.map((m) => (
          <SalivaMeasurementDetail key={String(m.measurement_id)} measurement={m} />
        ))
      ) : (
        <Paragraph muted>No saliva measurements were collected.</Paragraph>
      )}
    </Card>
  );
}
export function TaskCard({ check }: { check: CheckRecord }) {
  const task = check.snapshot.task,
    features = task.features as JsonObject;
  return (
    <Card>
      <Row>
        <Title small>Reaction evidence</Title>
        <Badge tone={task.status === "invalid" ? "danger" : "neutral"}>
          {friendly(task.status)}
        </Badge>
      </Row>
      <Fact label="Source" value={friendly(task.source)} />
      <Fact
        label="Scored trials presented"
        value={String(task.scored_trials)}
      />
      <Fact
        label="Correct go trials"
        value={String(task.valid_correct_go_trials)}
      />
      <Row>
        <Metric
          label="Median response"
          value={numberText(features.median_rt_ms)}
          unit="ms"
        />
        <Metric label="IQR" value={numberText(features.iqr_rt_ms)} unit="ms" />
        <Metric
          label="90th percentile"
          value={numberText(features.p90_rt_ms)}
          unit="ms"
        />
      </Row>
      <Fact
        label="Omission rate"
        value={
          features.omission_rate === null
            ? "Not available"
            : `${numberText(Number(features.omission_rate) * 100, 1)}% of go trials`
        }
      />
      <Fact
        label="Wrong go rate"
        value={
          features.wrong_go_rate === null
            ? "Not available"
            : `${numberText(Number(features.wrong_go_rate) * 100, 1)}% of go trials`
        }
      />
      <Fact
        label="No-go error rate"
        value={
          features.no_go_error_rate === null
            ? "Not available"
            : `${numberText(Number(features.no_go_error_rate) * 100, 1)}% of no-go trials`
        }
      />
      <Paragraph muted>
        Trial error rates describe this practice task. They are not an
        intoxication probability. Invalid runs have no aggregate features.
      </Paragraph>
      <Fact
        label="Quality flags"
        value={(task.quality_flags as string[]).join(", ") || "None reported"}
      />
    </Card>
  );
}
export function ResultScreen({ controller, model }: ScreenProps) {
  const check = controller.check;
  if (!check)
    return (
      <Page title="Result unavailable">
        <Button
          title="Open history"
          onPress={action(controller, () => controller.navigate("history"))}
        />
      </Page>
    );
  return (
    <Page
      title="Your measurements"
      eyebrow={check.frozen ? "Saved check" : "Draft check"}
      onBack={action(controller, () => controller.navigate("history"))}
      subtitle={`Started ${dateLabel(check.snapshot.created_at)}`}
    >
      <Card>
        <Row>
          <Badge tone={check.result?.state === "invalid" ? "danger" : "accent"}>
            {check.result?.state === "measurement_only"
              ? "Measurement record"
              : friendly(check.result?.state ?? "unavailable")}
          </Badge>
          {check.kind !== "measurement" && <Badge tone="warning">Demo</Badge>}
          <Badge>{friendly(check.delivery)}</Badge>
        </Row>
        <Title small>
          {check.result?.state === "measurement_only"
            ? "Measurements saved"
            : check.result?.state === "invalid"
              ? "Check needs attention"
              : "Result unavailable"}
        </Title>
        <Paragraph>
          No validated impairment model is available for this check.
          Intoxication cannot be determined.
        </Paragraph>
        {check.result?.state === "invalid" && (
          <Paragraph muted>
            Review the invalid acquisitions below. A replacement check uses new
            measurements and preserves this record.
          </Paragraph>
        )}
        {check.result?.state === "inconclusive" && (
          <Paragraph muted>
            The available evidence could not produce a complete result. The
            recorded measurements and missing values remain visible below.
          </Paragraph>
        )}
        <Fact label="Recorded at" value={dateLabel(check.snapshot.target_at)} />
      </Card>
      {check.error && <Notice tone="danger">{check.error}</Notice>}
      <SalivaCard check={check} />
      <View style={layout.grid}>
        <Card style={layout.column}>
          <Title small>Eyes</Title>
          <Badge>{friendly(check.snapshot.eyes.status)}</Badge>
          <Metric
            label="Relative constriction"
            value={numberText(check.snapshot.eyes.relative_constriction, 3)}
            detail="Normalized, dimensionless"
          />
          <Fact
            label="Pupil diameter"
            value={
              check.snapshot.eyes.scale_basis === "absolute_mm"
                ? `${numberText(check.snapshot.eyes.baseline_diameter_mm, 2)} mm`
                : "No physical scale available"
            }
          />
          <Fact label="Source" value={friendly(check.snapshot.eyes.source)} />
        </Card>
        <Card style={layout.column}>
          <Title small>Cardiac</Title>
          <Badge>{friendly(check.snapshot.cardiac.status)}</Badge>
          <Metric
            label="Heart rate"
            value={numberText(check.snapshot.cardiac.heart_rate_bpm)}
            unit="bpm"
          />
          <Fact
            label="Modality"
            value={friendly(check.snapshot.cardiac.modality)}
          />
          <Fact
            label="ECG"
            value={friendly(check.snapshot.cardiac.ecg_status)}
          />
          <Fact
            label="ECG RMSSD"
            value={
              check.snapshot.cardiac.ecg_rmssd_ms === null
                ? "Not available"
                : `${numberText(check.snapshot.cardiac.ecg_rmssd_ms)} ms`
            }
          />
          <Fact
            label="Source"
            value={friendly(check.snapshot.cardiac.source)}
          />
        </Card>
      </View>
      <TaskCard check={check} />
      <CardiacSelectionCard controller={controller} model={model} />
      {check.alcohol && (
        <Card>
          <Title small>Separate alcohol measurement</Title>
          <Metric
            label="Breath alcohol"
            value={
              check.alcohol.qualifier === "quantified"
                ? numberText(check.alcohol.value_mg_l, 3)
                : "—"
            }
            unit="mg/L"
          />
          <Fact
            label="Qualifier / source"
            value={`${friendly(check.alcohol.qualifier)} / ${friendly(check.alcohol.source)}`}
          />
          <Paragraph muted>
            No BAC conversion or cannabis impairment adjustment is calculated.
          </Paragraph>
        </Card>
      )}
      <ReportRevisionsCard key={`${controller.epoch}:${check.id}:${check.generation}`} controller={controller} model={model} />
      <ReplacementLinksCard controller={controller} model={model} />
      <Provenance check={check} />
      <Card>
        <ActionRow
          title="About this result"
          detail="Sources, recorded and evaluated times, frozen context and evidence hashes"
          onPress={action(controller, () => controller.navigate("evidence"))}
        />
        <ActionRow
          title="Export this check"
          detail="Exactly this check and its associated evidence"
          onPress={action(controller, () =>
            controller.openExport({
              source: "device",
              selection: { kind: "single", session_ids: [check.id] },
            }),
          )}
        />
        {check.remote_revision > 0 && (
          <ActionRow
            title="Refresh service result"
            detail="Verify the same snapshot and evidence before displaying"
            onPress={action(controller, () => controller.refreshCurrentCheck())}
          />
        )}
      </Card>
      {model.identity &&
        check.kind !== "guest_demo" &&
        check.delivery !== "synced" &&
        check.delivery !== "quarantined" && (
          <Button
            title={
              check.remote_revision ? "Retry requested upload" : "Upload check"
            }
            onPress={action(controller, () =>
              controller.ask({
                title: "Upload this check?",
                text: `Upload ${shortId(check.id)} to this account in ${BUILD.environment.toUpperCase()}? The frozen profile, measurements, complete capture attempts and evidence manifest are included. Unapproved raw images and waveforms are excluded. This action does not enable automatic uploads of future checks.`,
                confirm: "Upload check",
                action: () => controller.uploadCheck(),
              }),
            )}
            busy={model.busy}
            testID="upload-check"
          />
        )}
      {check.kind === "guest_demo" && (
        <Notice>
          Guest checks stay in the guest workspace. Signing in never uploads or
          migrates them.
        </Notice>
      )}
      <Button
        title="Start a replacement check"
        secondary
        onPress={action(controller, () =>
          controller.ask({
            title: "Start a new check with current context?",
            text: "The existing result remains immutable. The replacement has a new check ID and start time, and needs new measurements. No previous sample, eye, cardiac or reaction acquisition is carried forward.",
            confirm: "Review current context on Home",
            action: () => controller.prepareReplacement(check.id),
          }),
        )}
      />
    </Page>
  );
}
export function EvidenceScreen({ controller, model }: ScreenProps) {
  const check = controller.check,
    [expanded, setExpanded] = useState<string | null>(null),
    colors = useTheme();
  if (!check)
    return (
      <Page title="Evidence unavailable">
        <Button
          title="Open history"
          onPress={action(controller, () => controller.navigate("history"))}
        />
      </Page>
    );
  return (
    <Page
      title="Evidence & context"
      eyebrow={shortId(check.id)}
      onBack={action(controller, () =>
        controller.navigate(check.frozen ? "result" : "check"),
      )}
    >
      <Card>
        <Title small>Frozen context</Title>
        <Fact label="Check ID" value={check.id} />
        <Fact label="Created / target time" value={check.snapshot.target_at} />
        <Fact label="Capture completed" value={check.snapshot.capture_completed_at ?? "Not completed"} />
        <Fact label="Original result evaluated" value={check.result?.evaluated_at ?? "Not evaluated"} />
        <Fact label="Original result state" value={friendly(check.result?.state ?? "unavailable")} />
        {check.result && <Fact label="Original result reasons" value={check.result.reason_codes.map(friendly).join(", ") || "None recorded"} />}
        <Fact
          label="Profile revision"
          value={check.context.profile_version_id ?? "None"}
        />
        <Fact
          label="Context confirmed"
          value={check.context.context_confirmed_at}
        />
        <Fact
          label="Original profile recorded"
          value={check.snapshot.profile.recorded_at}
        />
        <Fact
          label="Original last use"
          value={
            check.context.self_report_context?.last_use_at ??
            friendly(check.context.self_report_context?.last_use_status ?? "not_recorded")
          }
        />
        <Fact
          label="Elapsed at check start"
          value={
            check.snapshot.history.time_since_use_min === null
              ? "Unknown"
              : `${check.snapshot.history.time_since_use_min.toFixed(1)} min`
          }
        />
        <Fact
          label="Profile SHA-256"
          value={check.context.profile_snapshot_sha256}
        />
        <Fact
          label="History SHA-256"
          value={check.context.history_snapshot_sha256}
        />
        <Fact
          label="Snapshot SHA-256"
          value={check.snapshot_sha256 ?? "Assigned when saved"}
        />
        <Fact
          label="Manifest SHA-256"
          value={check.evidence_sha256 ?? "Assigned when saved"}
        />
      </Card>
      <Notice>
        All attempts are retained, including interruptions and retries. “Valid”
        means an intact recorded acquisition under its stated software rules; it
        does not mean clinically qualified.
      </Notice>
      <SalivaCard check={check} />
      {check.attempts.length === 0 && (
        <Card>
          <Paragraph>No capture attempts have been recorded.</Paragraph>
        </Card>
      )}
      {check.attempts.map((a) => (
        <Card key={a.attempt_id}>
          <Row>
            <Title small>{friendly(a.component)}</Title>
            <Badge tone={a.status === "invalid" ? "danger" : "neutral"}>
              {friendly(a.status)}
            </Badge>
            <Badge>{friendly(a.source)}</Badge>
          </Row>
          <Fact label="Attempt" value={a.attempt_id} />
          {a.component === "cardiac" && <Fact label="Modality" value={cardiacAttemptModality(a)?.toUpperCase() ?? "Not reported"} />}
          <Fact
            label="Started / ended"
            value={`${a.started_at ?? "—"} / ${a.ended_at ?? "—"}`}
          />
          <Fact label="Configuration" value={a.configuration_id ?? "None"} />
          <Fact
            label="Configuration digest"
            value={a.configuration_hash ?? "None"}
          />
          <Fact
            label="Supersedes"
            value={a.supersedes_attempt_id ?? "Independent acquisition"}
          />
          <Fact
            label="Selected"
            value={
              check.manifest?.selected[a.component] === a.attempt_id
                ? "Yes"
                : check.frozen
                  ? "No"
                  : a.component === "cardiac"
                    ? check.selected_cardiac_attempt_id === a.attempt_id
                      ? "Chosen for snapshot; freezes on save"
                      : check.attempts.filter(item => item.component === "cardiac" && item.status === "valid").length > 1 && !check.selected_cardiac_attempt_id
                        ? "Choice pending at Review"
                        : "Retained; not selected"
                    : "Selection freezes on save"
            }
          />
          <Fact
            label="Quality"
            value={a.quality_flags.join(", ") || "None reported"}
          />
          <Button
            title={
              expanded === a.attempt_id
                ? "Hide recorded metadata"
                : "View recorded metadata"
            }
            secondary
            onPress={() =>
              setExpanded(expanded === a.attempt_id ? null : a.attempt_id)
            }
          />
          {expanded === a.attempt_id && (
            <Text
              selectable
              style={{
                fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
                fontSize: 12,
                lineHeight: 19,
                color: colors.ink,
              }}
            >
              {canonicalJson(a.component_metadata)}
            </Text>
          )}
        </Card>
      ))}
    </Page>
  );
}
