import { requireOptionalNativeModule, type EventSubscription } from 'expo-modules-core';
import { AppState, PermissionsAndroid, Platform } from 'react-native';
import type { DeviceTransport, TransportEvent } from '../../src/device/types';
import { DeviceError } from '../../src/device/protocol';

interface NativeTransport {
  getAvailability(): { available: boolean };
  getBluetoothPermissionStatus?(): BluetoothPermissionStatus;
  getCameraPermissionStatus?(): BluetoothPermissionStatus;
  monotonicNow(): number;
  scanAsync(): Promise<void>;
  stopScanAsync(): Promise<void>;
  connectAsync(id: string): Promise<{ peripheralId: string; mtu: number; capabilities: string }>;
  writeAsync(base64: string): Promise<void>;
  disconnectAsync(): Promise<void>;
  addListener(name: 'onDeviceEvent', listener: (event: TransportEvent) => void): EventSubscription;
}
const native = requireOptionalNativeModule<NativeTransport>('OTGDDeviceTransport');
export type BluetoothPermissionStatus = 'granted' | 'denied' | 'restricted' | 'not_requested' | 'unavailable' | 'unknown';
/** Reads OS authorization only. It never scans, creates an iOS central manager, or opens a permission prompt. */
export async function getBluetoothPermissionStatus(): Promise<BluetoothPermissionStatus> {
  try {
    if (!native || !native.getAvailability().available) return 'unavailable';
    if (Platform.OS === 'android') {
      const required = Number(Platform.Version) >= 31
        ? [PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN, PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT]
        : [PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION];
      const grants = await Promise.all(required.map(p => PermissionsAndroid.check(p)));
      // Android's check API cannot distinguish never-requested from a prior denial.
      return grants.every(Boolean) ? 'granted' : 'denied';
    }
    if (Platform.OS === 'ios') return native.getBluetoothPermissionStatus?.() ?? 'unknown';
    return 'unavailable';
  } catch { return 'unknown'; }
}
/** No-prompt OS camera authorization query; Expo's denied value does not distinguish iOS restriction. */
export async function getCameraPermissionStatus(): Promise<BluetoothPermissionStatus> {
  try {
    if (Platform.OS === 'android') return await PermissionsAndroid.check(PermissionsAndroid.PERMISSIONS.CAMERA) ? 'granted' : 'denied';
    if (Platform.OS === 'ios') return native?.getCameraPermissionStatus?.() ?? 'unknown';
    return 'unknown';
  } catch { return 'unknown'; }
}
function requiredNative(): NativeTransport { if (!native) throw new DeviceError('NATIVE_BLUETOOTH_UNAVAILABLE'); return native; }
async function permission(): Promise<void> {
  if (Platform.OS !== 'android') return;
  const permissions = Number(Platform.Version) >= 31
    ? [PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN, PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT]
    : [PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION];
  const result = await PermissionsAndroid.requestMultiple(permissions);
  if (permissions.some(p => result[p] === PermissionsAndroid.RESULTS.NEVER_ASK_AGAIN)) throw new DeviceError('BLUETOOTH_PERMISSION_BLOCKED');
  if (permissions.some(p => result[p] !== PermissionsAndroid.RESULTS.GRANTED)) throw new DeviceError('BLUETOOTH_PERMISSION_DENIED');
}
export function createNativeDeviceTransport(): DeviceTransport {
  return {
    kind: 'ble_unprovisioned', available: native?.getAvailability().available ?? false,
    now: () => requiredNative().monotonicNow(),
    subscribe(listener) {
      const subscription = native?.addListener('onDeviceEvent', listener);
      // Browser/local simulators do not receive this native adapter's events. Physical transport always stops on hiding.
      const app = AppState.addEventListener('change', state => { if (state !== 'active') listener({ kind: 'state', state: 'background' }); });
      return () => { subscription?.remove(); app.remove(); };
    },
    async scan() { await permission(); await requiredNative().scanAsync(); },
    async stopScan() { await native?.stopScanAsync(); },
    async connect(id) { await permission(); return requiredNative().connectAsync(id); },
    async write(base64) { await requiredNative().writeAsync(base64); },
    async disconnect() { await native?.disconnectAsync(); },
  };
}
