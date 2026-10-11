module.exports = {
  maybeCompleteAuthSession() {},
  async openAuthSessionAsync(url, redirect) {
    globalThis.__otgdUnitRuntime.providerCalls.push({ url, redirect });
    return { type: "dismiss" };
  },
};
