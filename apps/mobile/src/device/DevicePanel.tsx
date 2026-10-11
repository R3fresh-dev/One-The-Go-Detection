import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Linking, Pressable, StyleSheet, Text, View } from 'react-native';
import type { DeviceController } from './types';

export interface DevicePanelProps { controller: DeviceController }
const explanations: Record<string, string> = {
  NATIVE_BLUETOOTH_UNAVAILABLE: 'Bluetooth is unavailable in this build. Use the local synthetic simulator or install a native development build.',
  BLUETOOTH_PERMISSION_DENIED: 'Bluetooth access was declined. Select Find simulator to try again.',
  BLUETOOTH_PERMISSION_BLOCKED: 'Bluetooth access is blocked. Enable it in system settings, then try again.',
  BLUETOOTH_POWERED_OFF: 'Bluetooth is off. Turn it on in system settings, then try again.',
  POWERED_OFF: 'Bluetooth is off. Turn it on in system settings, then try again.',
  UNAUTHORIZED: 'Bluetooth permission is unavailable. Review the app permission in system settings.',
  CONNECTION_TIMEOUT: 'Connection timed out. Keep the simulator nearby and try again.',
  LINK_DISCONNECTED: 'The connection was lost. Any active capture was invalidated. Reconnect to start a new attempt.',
  UNVERIFIED_HUMAN_HARDWARE: 'This peripheral is not an approved synthetic simulator. Human hardware requires verified credentials and qualification.',
  REPLAY_JOURNAL_FULL: 'This simulator reached its bounded message limit. Restart the physical board and reconnect, or select the local simulator again.',
  BACKGROUND: 'Capture stopped when the app left the foreground. Start a new attempt after reconnecting.',
};
export function DevicePanel({ controller }: DevicePanelProps): React.ReactElement {
  const [snapshot, setSnapshot] = useState(controller.snapshot());
  const [busy, setBusy] = useState(false);
  const [operationError, setOperationError] = useState<string | null>(null);
  useEffect(() => controller.subscribe(setSnapshot), [controller]);
  const run = (operation: () => Promise<void>) => { setBusy(true); setOperationError(null); void operation().catch((error: unknown) => { setOperationError(error instanceof Error ? error.message : 'Device operation failed.'); }).finally(() => setBusy(false)); };
  const button = (label: string, action: () => Promise<void>, disabled = false) => <Pressable accessibilityRole="button" accessibilityLabel={label} accessibilityState={{ disabled: busy || disabled }} disabled={busy || disabled} style={[styles.button, (busy || disabled) && styles.disabled]} onPress={() => run(action)}><Text style={styles.buttonText}>{label}</Text></Pressable>;
  const reason = snapshot.reason ?? operationError;
  return <View style={styles.panel}>
    <Text style={styles.heading} accessibilityRole="header">Device simulator</Text>
    <Text style={styles.body}>Synthetic bench data only. A Bluetooth connection does not establish a trusted human measurement. No intoxication prediction is available.</Text>
    <Text style={styles.status} accessibilityLiveRegion="polite">{snapshot.state === 'connected_simulator' ? 'Synthetic simulator connected' : snapshot.state === 'scanning' ? 'Looking for project simulators…' : snapshot.state === 'connecting' ? 'Checking capabilities and clock exchange…' : 'No simulator connected'}</Text>
    {busy && <ActivityIndicator accessibilityLabel="Device operation in progress" />}
    {reason && <Text style={styles.error} accessibilityLiveRegion="assertive">{explanations[reason] ?? `Device operation stopped: ${reason}. Reconnect or use the local simulator.`}</Text>}
    {snapshot.association && <View style={styles.details}>
      <Text style={styles.body}>Device: {snapshot.association.deviceId}</Text>
      <Text style={styles.body}>Firmware: {snapshot.association.firmwareVersion}</Text>
      <Text style={styles.body}>Connection: {snapshot.association.transport === 'local_simulator' ? 'Local software simulator' : 'Unprovisioned Bluetooth simulator'}</Text>
      <Text style={styles.body}>Human capture: unavailable</Text>
      {button('Disconnect simulator', () => controller.disconnect())}
      {button('Forget simulator', () => controller.forget())}
    </View>}
    {!snapshot.association && <>
      {snapshot.state === 'scanning' ? button('Stop discovery', () => controller.stopScan()) : button('Find Bluetooth simulator', () => controller.scan())}
      {snapshot.devices.map(device => <View key={device.peripheralId} style={styles.device}>
        <Text style={styles.body}>{device.alias}</Text><Text style={styles.caption}>Signal {device.rssi} dBm · identity unverified</Text>
        {button(`Connect ${device.alias}`, () => controller.connect(device.peripheralId))}
      </View>)}
      {button('Use local synthetic simulator', () => controller.useLocalSimulator())}
    </>}
    {(reason?.includes('PERMISSION') || ['UNAUTHORIZED', 'POWERED_OFF', 'BLUETOOTH_POWERED_OFF'].includes(reason ?? '')) && button('Open system settings', () => Linking.openSettings())}
    {snapshot.captureInProgress && <Text style={styles.caption}>Disconnecting immediately invalidates this capture. A reconnect requires a new attempt.</Text>}
  </View>;
}
const styles = StyleSheet.create({
  panel: { borderRadius: 16, borderWidth: 1, borderColor: '#cad6df', padding: 16, gap: 12, backgroundColor: '#f5f8fa' },
  heading: { fontSize: 22, fontWeight: '600', color: '#132f40' },
  body: { color: '#223f50', fontSize: 16, lineHeight: 24 },
  caption: { color: '#456172', fontSize: 14, lineHeight: 20 },
  status: { color: '#125751', fontSize: 16, fontWeight: '600' },
  error: { color: '#8e3025', fontSize: 16, lineHeight: 24 },
  button: { minHeight: 48, borderRadius: 10, padding: 14, backgroundColor: '#155c60', alignItems: 'center', justifyContent: 'center' },
  buttonText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  disabled: { opacity: 0.5 },
  details: { gap: 8 }, device: { borderTopWidth: 1, borderTopColor: '#ccd9df', paddingTop: 12, gap: 8 },
});
