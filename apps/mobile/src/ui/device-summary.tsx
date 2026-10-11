import React, { useEffect, useState } from "react";
import type { AppController } from "../controller";
import { presentDevice } from "../core/devicePresentation";
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
      <Badge tone={view.tone}>
        {view.connected ? "Synthetic only" : "Not ready for capture"}
      </Badge>
      <Title small>{view.title}</Title>
      <Paragraph>{view.detail}</Paragraph>
      {view.bootId && <Fact label="Current reader boot" value={view.bootId} />}
      {view.observedAt && (
        <Fact
          label="Connection state observed"
          value={new Date(view.observedAt).toLocaleString()}
        />
      )}
      <Paragraph muted>
        Qualified human saliva, pupil, PPG, ECG and alcohol measurement remains
        unavailable. This connection does not change that gate.
      </Paragraph>
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
