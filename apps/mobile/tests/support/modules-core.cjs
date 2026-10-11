module.exports = {
  requireOptionalNativeModule: (name) =>
    name === "OTGDReactionTask"
      ? {
          getAvailability: () => ({
            available: globalThis.__otgdUnitRuntime.available,
            platform: "ios",
            configurationId: "choice_inhibit_v0_native_dev_1",
            configurationSha256:
              "61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3",
            modelEligible: false,
          }),
        }
      : null,
  requireNativeViewManager: () => () => null,
};
