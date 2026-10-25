import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
import source from "../testfixtures/backend-app-config.json";

// This file runs in its own Node test process. These are inert compiled-build
// fixtures; no Cognito account, cloud request, or identity authority is created.
const pins = {
  environment: "qa",
  issuer: "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_fixture",
  clientId: "approved-public-client",
  oauthOrigin: "https://admitted.auth.us-east-2.amazoncognito.com",
  redirectUri: "otgd-qa://oauth/callback",
  webCallbackUri: "https://web.owned-research.org/",
};
Object.assign(require("expo-constants").default.expoConfig.extra, pins);
const { AuthManager } =
  require("../src/services/auth") as typeof import("../src/services/auth");
const { parseAppConfig } =
  require("../src/services/api") as typeof import("../src/services/api");
const { BUILD } =
  require("../src/platform/config") as typeof import("../src/platform/config");
const { vault } =
  require("../src/platform/storage") as typeof import("../src/platform/storage");

test("compiled Cognito hosted origin admits code, refresh, restored family, revocation and logout without using the pool issuer as a destination", async () => {
  const originalFetch = globalThis.fetch,
    calls: string[] = [];
  const config = structuredClone(source) as any;
  config.environment = "qa";
  config.auth = {
    issuer: pins.issuer,
    client_id: pins.clientId,
    authorization_endpoint: pins.oauthOrigin + "/oauth2/authorize",
    token_endpoint: pins.oauthOrigin + "/oauth2/token",
    revocation_endpoint: pins.oauthOrigin + "/oauth2/revoke",
    logout_endpoint: pins.oauthOrigin + "/logout",
    redirect_uris: [pins.redirectUri, pins.webCallbackUri],
  };
  const admitted = parseAppConfig(config, BUILD);
  const auth = new AuthManager();
  (globalThis as any).location = { origin: "https://web.owned-research.org" };
  const unit = (globalThis as any).__otgdUnitRuntime;
  unit.prompt = async (request: any) => {
    assert.equal(request.redirectUri, pins.webCallbackUri);
    return {
      type: "success",
      params: { state: request.state, code: "fictional-code" },
      url:
        request.redirectUri +
        "?" +
        new URLSearchParams({ state: request.state, code: "fictional-code" }),
    };
  };
  globalThis.fetch = async (url) => {
    calls.push(String(url));
    return new Response(
      JSON.stringify(
        String(url).endsWith("/oauth2/token")
          ? {
              access_token: "fictional-access",
              refresh_token: "fictional-refresh",
              token_type: "Bearer",
              expires_in: 900,
            }
          : {},
      ),
      { status: 200 },
    );
  };
  try {
    const tokens = (await auth.authorize(admitted))!;
    const identity = {
      issuer: pins.issuer,
      accountRef: "fictional-owned-account",
      generation: 1,
      state: "active",
      verifiedAt: new Date().toISOString(),
    } as const;
    await auth.commit({ ...tokens, expiresAt: 0 }, identity);
    const restored = new AuthManager();
    assert.deepEqual(await restored.restore(), identity);
    assert.equal(await restored.accessToken(), "fictional-access");
    const logout = restored.providerLogoutUrl()!;
    const revoke = restored.captureProviderRevocation();
    await restored.clear();
    await revoke();
    await restored.openProviderLogout(logout);
    assert.deepEqual(calls, [
      pins.oauthOrigin + "/oauth2/token",
      pins.oauthOrigin + "/oauth2/token",
      pins.oauthOrigin + "/oauth2/revoke",
    ]);
    assert.equal(
      new URL(unit.providerCalls.at(-1).url).origin,
      pins.oauthOrigin,
    );
    const bad = structuredClone(tokens);
    bad.auth.token_endpoint = pins.issuer + "/oauth2/token";
    await assert.rejects(
      () => auth.commit(bad, identity),
      /authentication|endpoint/i,
    );
    const stored = JSON.parse((await vault.get("otgd.auth.qa")) ?? "null");
    assert.equal(stored, null);
  } finally {
    await auth.clear();
    globalThis.fetch = originalFetch;
  }
});
