import React, { useEffect, useRef, useState } from 'react';
import { Text, View } from 'react-native';
import { Button, Card, Choice, Fact, Metric, Notice, Paragraph, Row, Title } from '../ui/components';
import { useTheme } from '../ui/theme';
import type { DeviceController } from './types';
import { signalScenarios } from './signal';
import type { SyntheticSignalChannel, SyntheticSignalPreview, SyntheticSignalScenario } from './signal';
import { SIGNAL_SCENARIO_LABELS, SIGNAL_STATE_LABELS, signalRecovery, waveformSegments } from './signalPresentation';

export interface SignalPanelProps {
  device: DeviceController;
  sessionId: string;
  workspaceEpoch: string;
  channel: SyntheticSignalChannel;
  disabled: boolean;
  onStart: (scenario: SyntheticSignalScenario) => Promise<void>;
  onStop: () => Promise<void>;
  onDevices: () => Promise<void>;
  onError: (error: unknown) => void;
}
function FictionalWaveform({ preview }: { preview: SyntheticSignalPreview }) {
  const colors = useTheme(), [width, setWidth] = useState(0), height = 128;
  const stopped = preview.terminal;
  return <View style={{ gap: 8 }}>
    <Text style={{ color: colors.ink, fontSize: 15, fontWeight: '600' }}>{stopped ? 'Stopped fictional waveform — not current' : 'Fictional ECG waveform'}</Text>
    <View accessible accessibilityRole="image" accessibilityLabel={`Fictional ECG in arbitrary counts. A two-second window of ${preview.samples.length} displayed samples. ${SIGNAL_STATE_LABELS[preview.state]}.`} onLayout={event => setWidth(event.nativeEvent.layout.width)} style={{ height, overflow: 'hidden', borderWidth: 1, borderColor: colors.line, borderRadius: 10, backgroundColor: colors.surfaceMuted }}>
      <View accessible={false} pointerEvents="none" style={{ position: 'absolute', left: 0, right: 0, top: height / 2, height: 1, backgroundColor: colors.line }} />
      {waveformSegments(preview.samples, width, height).map(segment => <View key={segment.key} accessible={false} pointerEvents="none" style={{ position: 'absolute', left: segment.left, top: segment.top, width: segment.width, height: 2, backgroundColor: stopped ? colors.secondary : colors.accent, transform: [{ rotate: `${segment.angleRad}rad` }] }} />)}
    </View>
    <Text style={{ color: colors.secondary, fontSize: 12, lineHeight: 18 }}>50 fictional samples/s · two-second scrolling window · arbitrary counts (−1,000 to 1,000), not mV. The four-second fixture is independent of pulse/BPM and provides no HRV or diagnostic interpretation.</Text>
  </View>;
}

export function SignalPanel({ device, sessionId, workspaceEpoch, channel, disabled, onStart, onStop, onDevices, onError }: SignalPanelProps) {
  const colors = useTheme(), [snapshot, setSnapshot] = useState(() => device.snapshot()), [scenario, setScenario] = useState<SyntheticSignalScenario>('clean'), [busy, setBusy] = useState(false), mounted = useRef(true);
  useEffect(() => { mounted.current = true; const unsubscribe = device.subscribe(setSnapshot); return () => { mounted.current = false; unsubscribe(); }; }, [device]);
  useEffect(() => { setScenario('clean'); }, [channel, sessionId, workspaceEpoch]);
  const local = snapshot.association?.transport === 'local_simulator', connected = snapshot.state === 'connected_simulator';
  const candidate = snapshot.signalPreview;
  const preview = candidate && candidate.context.sessionId === sessionId && candidate.context.workspaceEpoch === workspaceEpoch && candidate.channel === channel ? candidate : null;
  const active = snapshot.captureInProgress;
  const run = (operation: () => Promise<void>) => { setBusy(true); void operation().catch(error => { if (mounted.current) onError(error); }).finally(() => { if (mounted.current) setBusy(false); }); };
  const recovery = preview ? signalRecovery(preview) : null;
  return <Card>
    <Title small>{channel === 'ecg' ? 'Synthetic ECG capture' : 'Synthetic PPG capture'}</Title>
    <Notice tone="warning">Software demonstration. Every signal, contact state and pulse value shown here is fictional. Qualified human acquisition remains unavailable.</Notice>
    {local && !active && !busy && !disabled && <Choice<SyntheticSignalScenario> label="Choose a fictional signal scenario" value={scenario} options={signalScenarios(channel).map(value => ({ value, label: SIGNAL_SCENARIO_LABELS[value] }))} onChange={setScenario} />}
    {preview && <>
      <Text accessibilityLiveRegion="polite" style={{ color: preview.reason ? colors.danger : colors.ink, fontSize: 16, lineHeight: 23, fontWeight: '600' }}>{SIGNAL_STATE_LABELS[preview.state]}</Text>
      <Fact label="Scenario" value={SIGNAL_SCENARIO_LABELS[preview.scenario]} />
      <Row><Metric label="Current fictional pulse" value={preview.heartRateBpm === null ? '—' : String(preview.heartRateBpm)} unit="bpm" detail={preview.terminal ? 'Ended; no current reading' : preview.state === 'acquiring' ? 'Fixed software fixture' : 'Waiting for a valid fictional batch'} /><Metric label="Accepted batches" value={`${preview.acceptedBatches}/${preview.expectedBatches}`} /></Row>
      <View accessibilityRole="progressbar" accessibilityLabel="Fictional capture progress" accessibilityValue={{ min: 0, max: preview.expectedBatches, now: preview.acceptedBatches }} style={{ height: 8, borderRadius: 4, backgroundColor: colors.surfaceMuted, overflow: 'hidden' }}><View style={{ height: 8, width: `${Math.min(100, preview.acceptedBatches / preview.expectedBatches * 100)}%`, backgroundColor: preview.reason ? colors.danger : colors.accent }} /></View>
      <Fact label="Fictional contact" value={preview.contact} />
      <Fact label="Last fictional batch received" value={preview.lastReceivedAt ?? 'No batch received'} />
      {preview.terminal && preview.lastHeartRateBpm !== null && <Fact label="Earlier fictional observation (not current)" value={`${preview.lastHeartRateBpm} bpm`} />}
      {channel === 'ecg' && <FictionalWaveform preview={preview} />}
      {preview.reason && <Fact label="Invalidity reason" value={preview.reason} />}
      {recovery && <Notice tone="warning">{recovery}</Notice>}
      {preview.state === 'complete' && <Paragraph>All expected fictional batches and the complete synthetic transport proof were accepted. The check controller saves the completed attempt separately. This display is not an impairment result.</Paragraph>}
    </>}
    {!preview && active && <Paragraph>{local ? 'Starting the local fictional signal after the handshake and clock exchanges…' : 'Live preview unavailable — waiting for verified synthetic completion. This unprovisioned BLE fixture does not stream live cardiac samples.'}</Paragraph>}
    {!active && !connected && <Paragraph>Connect the local simulator from Devices to try the live fictional scenarios. The Nano ESP32 bench fixture can send a bounded synthetic completion; live preview is unavailable over its current BLE protocol.</Paragraph>}
    {active ? <Button title="End synthetic capture" secondary onPress={() => run(onStop)} /> : connected ? <Button title={disabled ? 'Valid attempt already retained for this modality' : busy ? 'Saving ended synthetic attempt…' : `Start ${channel.toUpperCase()} ${local ? 'software demonstration' : 'BLE synthetic capture'}`} disabled={disabled || busy} onPress={() => run(() => onStart(local ? scenario : 'clean'))} /> : <Button title="Open Devices to reconnect" secondary disabled={busy} onPress={() => run(onDevices)} />}
  </Card>;
}
