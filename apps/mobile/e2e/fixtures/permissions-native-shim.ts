export * from "./native-web-shim";
const { Platform: WebPlatform } = require("react-native-web");
export const Platform = {
  ...WebPlatform,
  OS: "ios",
  Version: "fictional-controlled-os",
};
export const Linking = {
  openSettings: async () => {
    (window as any).permissionControl.settings++;
  },
};
export const AppState = {
  addEventListener: (_: string, listener: (state: string) => void) => {
    const c = (window as any).permissionControl;
    c.listeners.add(listener);
    return { remove: () => c.listeners.delete(listener) };
  },
};
