import type { DeviceTransport } from '../../src/device/types';
import { DeviceError } from '../../src/device/protocol';
export type BluetoothPermissionStatus = 'granted' | 'denied' | 'restricted' | 'not_requested' | 'unavailable' | 'unknown';
export async function getBluetoothPermissionStatus(): Promise<BluetoothPermissionStatus> { return 'unavailable'; }
export async function getCameraPermissionStatus(): Promise<BluetoothPermissionStatus> { return 'unknown'; }
export function createNativeDeviceTransport(): DeviceTransport {
  const fail = () => { throw new DeviceError('NATIVE_BLUETOOTH_UNAVAILABLE'); };
  return {
    kind: 'ble_unprovisioned', available: false, now: fail,
    subscribe: () => () => {}, scan: async () => fail(), stopScan: async () => {},
    connect: async () => fail(), write: async () => fail(), disconnect: async () => {},
  };
}
