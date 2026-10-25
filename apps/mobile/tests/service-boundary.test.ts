import test from "node:test";
import assert from "node:assert/strict";
import actualConfig from "../testfixtures/backend-app-config.json";
import actualCapabilities from "../testfixtures/backend-capabilities.json";
import {
  ApiClient,
  isOrdinaryWrite,
  parseAppConfig,
  parseCapabilities,
  syncReadiness,
} from "../src/services/api";
import { clone } from "../src/core/integrity";

const expected = {
  environment: "test",
  issuer: "http://localhost:8081",
  clientId: "otgd-local-mobile",
  oauthOrigin: "http://localhost:8081",
  redirectUris: ["otgd-local://oauth/callback", "http://localhost:8082/"],
};
test("actual backend app-config and capabilities responses decode without removing mandatory fields", () => {
  const config = parseAppConfig(actualConfig, expected),
    caps = parseCapabilities(actualCapabilities);
  assert.equal(config.notice.mandatory, true);
  assert.equal(caps.notice.mandatory, true);
  assert.equal(caps.notice.acknowledged, true);
  assert.equal(syncReadiness(config, "0.2.0").allowed, true);
  assert.equal(caps.account_ref, actualCapabilities.account_ref);
  assert.throws(
    () =>
      parseAppConfig(
        {
          ...actualConfig,
          notice: { ...actualConfig.notice, mandatory: "true" },
        },
        expected,
      ),
    /notice metadata/,
  );
  assert.throws(
    () =>
      parseCapabilities({ ...actualCapabilities, inference_available: true }),
    /unsupported/,
  );
});

test("unsupported app version, minimum version or contract pauses synchronization; maintenance is separate", () => {
  const config = parseAppConfig(actualConfig, expected);
  assert.equal(syncReadiness(null, "0.2.0").code, "config_required");
  assert.equal(
    syncReadiness({ ...config, supported_app_versions: ["0.3.0"] }, "0.2.0")
      .code,
    "update_required",
  );
  assert.equal(
    syncReadiness({ ...config, minimum_app_version: "0.3.0" }, "0.2.0").code,
    "update_required",
  );
  const changed = clone(config);
  changed.contract_versions.capture_evidence = ["2.0.0"];
  assert.equal(syncReadiness(changed, "0.2.0").code, "update_required");
  assert.equal(
    syncReadiness({ ...config, maintenance: true }, "0.2.0").code,
    "maintenance",
  );
  assert.equal(
    syncReadiness({ ...config, minimum_app_version: "0.1.99" }, "0.2.0").code,
    "ready",
  );
});

test("research result format advertisement supports only the versioned reader and grants no inference authority", () => {
  const original = clone(actualConfig) as any;
  delete original.contract_versions.research_result;
  assert.equal(parseAppConfig(original, expected).inference_available, false);
  original.contract_versions.research_result = ["1.1.0"];
  const parsed = parseAppConfig(original, expected);
  assert.deepEqual(parsed.contract_versions.research_result, ["1.1.0"]);
  assert.deepEqual(parsed.contract_versions.scientific, ["0.1.0"]);
  assert.equal(parsed.inference_available, false);
  for (const invalid of [[], ["1.2.0"], ["1.1.0", "0.1.0"], "1.1.0", null]) {
    const changed = clone(original);
    changed.contract_versions.research_result = invalid;
    assert.throws(
      () => parseAppConfig(changed, expected),
      /format is unsupported/,
    );
  }
});

test("maintenance blocks an ordinary HTTP write before fetch and preserves exact privacy escape routes", async () => {
  const oldFetch = globalThis.fetch,
    calls: { url: string; init: RequestInit }[] = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), init: init! });
    return new Response("{}", {
      headers: { "Content-Type": "application/json" },
    });
  };
  try {
    const client = new ApiClient(
      "https://api.example.test",
      { accessToken: async () => "access" },
      "0.2.0",
      () => ({
        allowed: false,
        code: "maintenance",
        message: "Maintenance in progress.",
      }),
    );
    await assert.rejects(
      client.request("/v1/sessions", {
        method: "POST",
        generation: 1,
        key: "stable",
        body: {},
      }),
      /Maintenance/,
    );
    assert.equal(calls.length, 0);
    for (const path of [
      "/v1/me/acknowledgments",
      "/v1/privacy/exports",
      "/v1/privacy/deletion-requests",
      "/v1/me/data-generation/acknowledgments",
      "/v1/studies/study/withdrawals",
      "/v1/auth/logout",
    ])
      await client.request(path, {
        method: "POST",
        generation: 1,
        key: "stable",
        body: {},
      });
    await client.request("/v1/sessions/session");
    assert.equal(calls.length, 7);
    for (const call of calls)
      assert.equal(
        (call.init.headers as Record<string, string>)["X-App-Version"],
        "0.2.0",
      );
    assert.equal(isOrdinaryWrite("/v1/studies/study/consents", "POST"), true);
  } finally {
    globalThis.fetch = oldFetch;
  }
});

for (const key of [
  "authorization_endpoint",
  "token_endpoint",
  "revocation_endpoint",
  "logout_endpoint",
] as const) {
  const path =
    key === "logout_endpoint"
      ? "/logout"
      : `/oauth2/${key === "authorization_endpoint" ? "authorize" : key === "token_endpoint" ? "token" : "revoke"}`;
  for (const [name, endpoint] of Object.entries({
    foreign_origin: "https://foreign.invalid" + path,
    changed_port: "http://localhost:8089" + path,
    wrong_path: expected.oauthOrigin + path + "/extra",
    query: expected.oauthOrigin + path + "?override=1",
    fragment: expected.oauthOrigin + path + "#override",
    userinfo: "http://user@localhost:8081" + path,
    encoded_path: expected.oauthOrigin + path.replace("/", "/%2e/"),
  }))
    test(`OAuth metadata refuses ${key} ${name} despite matching issuer and client`, () => {
      const changed = clone(actualConfig);
      changed.auth[key] = endpoint;
      assert.throws(
        () => parseAppConfig(changed, expected),
        /authentication|endpoint/i,
      );
    });
}

test("OAuth callbacks are independently pinned and missing hosted-origin policy fails closed", () => {
  for (const redirect_uris of [
    [...expected.redirectUris, "https://foreign.invalid/"],
    ["https://foreign.invalid/"],
    [...expected.redirectUris, expected.redirectUris[0]],
    [expected.redirectUris[0]],
  ]) {
    assert.throws(
      () =>
        parseAppConfig(
          { ...actualConfig, auth: { ...actualConfig.auth, redirect_uris } },
          expected,
        ),
      /callback/i,
    );
  }
  assert.throws(
    () => parseAppConfig(actualConfig, { ...expected, oauthOrigin: "" }),
    /authentication|origin|configured/i,
  );
});

test("separately compiled Cognito hosted origin works without treating the user-pool issuer as its domain", () => {
  const pins = {
    environment: "qa",
    issuer: "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_fixture",
    clientId: "public-client",
    oauthOrigin: "https://admitted.auth.us-east-2.amazoncognito.com",
    redirectUris: ["otgd-qa://oauth/callback", "https://web.qa.otgd.test/"],
  };
  const changed = clone(actualConfig) as any;
  changed.environment = "qa";
  changed.auth = {
    issuer: pins.issuer,
    client_id: pins.clientId,
    authorization_endpoint: pins.oauthOrigin + "/oauth2/authorize",
    token_endpoint: pins.oauthOrigin + "/oauth2/token",
    revocation_endpoint: pins.oauthOrigin + "/oauth2/revoke",
    logout_endpoint: pins.oauthOrigin + "/logout",
    redirect_uris: pins.redirectUris,
  };
  assert.equal(
    parseAppConfig(changed, pins).auth.token_endpoint,
    pins.oauthOrigin + "/oauth2/token",
  );
  changed.auth.token_endpoint = pins.issuer + "/oauth2/token";
  assert.throws(
    () => parseAppConfig(changed, pins),
    /authentication|endpoint/i,
  );
});
