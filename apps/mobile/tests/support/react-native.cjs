module.exports = {
  ...require("react-native-web"),
  Platform: { OS: "web", Version: 0 },
  AppState: {
    currentState: "active",
    addEventListener: () => ({ remove() {} }),
  },
  PermissionsAndroid: { PERMISSIONS: {}, check: async () => false },
};
