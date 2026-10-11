const { registerHooks } = require("node:module");
const { fileURLToPath, pathToFileURL } = require("node:url");
const { resolve } = require("node:path");
// These suites exercise two explicit fictional binary modes through the native
// boundary. A workflow's artifact-build flag must not relabel the ordinary
// account test binary; hosted-preview.test.ts selects the guarded mode itself.
// Actual compiled hosted behavior is verified separately by browser/native gates.
process.env.EXPO_PUBLIC_HOSTED_PREVIEW =
  process.env.OTGD_UNIT_PREVIEW === "true" ? "true" : "false";
const runtime = {
  available: false,
  prompt: async (request) => ({
    type: "success",
    params: { state: request.state, code: "one-time-code" },
  }),
  providerCalls: [],
};
globalThis.__otgdUnitRuntime = runtime;
// Test-only native boundary adapters. Actual controller, domain, HTTP and
// serialized storage logic are loaded unchanged by the TypeScript runner.
const Module = require("node:module"),
  originalLoad = Module._load;
Module._load = function (specifier, parent, isMain) {
  const files = {
    "react-native": "react-native.cjs",
    "expo-constants": "constants.cjs",
    "expo-auth-session": "auth-session.cjs",
    "expo-web-browser": "web-browser.cjs",
    "expo-modules-core": "modules-core.cjs",
  };
  return originalLoad.call(
    this,
    files[specifier] ? resolve(__dirname, files[specifier]) : specifier,
    parent,
    isMain,
  );
};
module.exports = runtime;
