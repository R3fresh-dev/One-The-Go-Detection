// Component-only browser binding. Production UI is unchanged; these unavailable
// native APIs must never be treated as physical permission or acquisition proof.
export * from "react-native-web";
export const PermissionsAndroid = {
  PERMISSIONS: {},
  RESULTS: {},
  check: async () => false,
};
export const TurboModuleRegistry = {
  get: () => null,
  getEnforcing: () => {
    throw Error("Native module unavailable in this component test.");
  },
};
