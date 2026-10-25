import React, { useEffect, useState } from "react";
import type { AppController, AppModel } from "../controller";
import {
  presentAcquisitionChannels,
  presentDevice,
} from "../core/devicePresentation";
import { BUILD } from "../platform/config";
import {
  Badge,
  Button,
  Card,
  Fact,
  Label,
  Paragraph,
  Title,
  layout,
} from "./components";

export function HomeDeviceSummary({
  controller,
}: {
  controller: AppController;
}) {
  const epoch = controller.epoch;
  const [snapshot, setSnapshot] = useState(() => controller.device.snapshot());
  useEffect(
    () =>
      controller.device.subscribe((value) => {
        if (controller.epoch === epoch) setSnapshot(value);
      }),
    [controller, epoch],
  );
  const view = presentDevice(snapshot);
  return (
    <Card style={layout.column}>
      <Label>Reader connection</Label>
      <Badge tone={view.tone}>{view.badge}</Badge>
      <Title small>{view.title}</Title>
      <Paragraph>{view.detail}</Paragraph>
      {view.bootId && <Fact label="Current reader boot" value={view.bootId} />}
      {view.observedAt && (
        <Fact
          label="Connection state observed"
          value={new Date(view.observedAt).toLocaleString()}
        />
      )}
      <AcquisitionAvailability model={controller.getSnapshot()} />
      <Button
        title={view.action}
        secondary
        testID="home-device-connection"
        onPress={() => {
          if (controller.epoch !== epoch) return;
          void controller.run(() => controller.navigate("device"));
        }}
      />
    </Card>
  );
}

/** One display policy for Home and Device; these facts never enable a Start. */
export function AcquisitionAvailability({ model }: { model: AppModel }) {
  const [, expireObservation] = useState(0);
  const rows = presentAcquisitionChannels({
    identity: model.identity,
    capabilities: model.state?.capabilities ?? null,
    generation: model.state?.generation ?? null,
    offline: model.offline,
    hostedPreview: BUILD.hostedPreview,
  });
  const nextExpiry = Math.min(
    ...rows.flatMap((row) =>
      row.expiresAt ? [Date.parse(row.expiresAt)] : [],
    ),
  );
  useEffect(() => {
    if (!Number.isFinite(nextExpiry)) return;
    const timer = setTimeout(
      () => expireObservation((version) => version + 1),
      Math.min(2_147_483_647, Math.max(1, nextExpiry - Date.now())),
    );
    return () => clearTimeout(timer);
  }, [nextExpiry]);
  return (
    <>
      <Title small>Current acquisition capabilities</Title>
      {rows.map((row) => (
        <Fact key={row.channel} label={row.label} value={row.detail} />
      ))}
      <Paragraph muted>
        Connection and binding do not grant capture or scientific approval. Each
        Start still requires the selected study, consent, current configuration,
        installed adapter and fresh server authorization.
      </Paragraph>
    </>
  );
}
