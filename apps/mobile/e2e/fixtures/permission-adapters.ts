// OS boundary only: these spies are controlled observations, never native proof.
const control = () => (window as any).permissionControl;
export const createNativeDeviceTransport = () => {
  throw new Error("No native acquisition in permission component tests");
};
export const setStringAsync = async () => {
  throw new Error("Clipboard is outside permission component tests");
};
export const getCameraPermissionStatus = async () => control().exact;
export const getBluetoothPermissionStatus = async () => "denied";
export const getEnrolledLevelAsync = async () => 1;
export const Camera = {
  getCameraPermissionsAsync: () => {
    const c = control();
    c.reads++;
    if (c.defer)
      return new Promise((resolve, reject) =>
        c.pending.push({ resolve, reject }),
      );
    return c.fail
      ? Promise.reject(new Error("fictional OS status failure"))
      : Promise.resolve(c.permission);
  },
  requestCameraPermissionsAsync: async () => {
    control().prompts++;
    return control().permission;
  },
};
export const CameraView = () => null;
export const useCameraPermissions = () => [
  null,
  Camera.requestCameraPermissionsAsync,
  Camera.getCameraPermissionsAsync,
];
