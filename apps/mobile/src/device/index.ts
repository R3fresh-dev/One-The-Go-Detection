import { AppState } from 'react-native';
import { createNativeDeviceTransport } from '../../modules/device-transport';
import { DeviceControllerImpl } from './controller';
import type { DeviceController, DeviceControllerOptions } from './types';
export * from './types';
export { DeviceError, DEVICE_SERVICE_UUID, CLOCK_POLICY_ID } from './protocol';
export { DevicePanel } from './DevicePanel';
export type { DevicePanelProps } from './DevicePanel';
export { getSyntheticSignalFailure } from './signalFailure';
export type { SyntheticSignalFailure } from './signalFailure';
export { signalScenarios, SYNTHETIC_SIGNAL_CONFIGURATION } from './signal';
export type { SyntheticSignalScenario, SyntheticSignalOptions, SyntheticSignalPreview } from './signal';

export function createDeviceController(options: DeviceControllerOptions): DeviceController {
  const controller = new DeviceControllerImpl(options, createNativeDeviceTransport);
  // Local simulation also stops acquisition on backgrounding; no component crosses a hidden workspace.
  const lifecycle = AppState.addEventListener('change', state => {
    if (state !== 'active') { void controller.cancelCapture('BACKGROUND'); void controller.stopScan(); }
  });
  const dispose = controller.dispose.bind(controller);
  controller.dispose = async () => { lifecycle.remove(); await dispose(); };
  return controller;
}
