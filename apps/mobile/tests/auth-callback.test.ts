import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
import { customerService } from "./support/customer";
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");
const { Platform } = require("react-native");
const runtime = (globalThis as any).__otgdUnitRuntime;

function success(request: { state: string; redirectUri: string }) {
  const params = { state: request.state, code: "fictional-callback-code" };
  return {
    type: "success",
    params,
    url: request.redirectUri + "?" + new URLSearchParams(params),
  };
}

for (const platform of ["web", "android", "ios"]) {
  test(`exact ${platform} callback succeeds; matching state at an unadmitted return target never exchanges or changes accounts`, async () => {
    const service = customerService(),
      priorFetch = globalThis.fetch,
      priorLocation = globalThis.location,
      priorPlatform = Platform.OS,
      priorPrompt = runtime.prompt;
    globalThis.fetch = service.fetcher;
    (globalThis as any).location = { origin: "http://localhost:8082" };
    Platform.OS = platform;
    runtime.prompt = async (request: { state: string; redirectUri: string }) =>
      success(request);
    const app = new AppController();
    try {
      await app.auth.clear();
      await app.initialize();
      assert.equal(await app.signIn(), true);
      const identity = structuredClone(app.getSnapshot().identity),
        generation = app.auth.generation,
        expected =
          platform === "web"
            ? "http://localhost:8082/"
            : "otgd-local://oauth/callback";
      const exchange = service.calls.filter(
        (call) => call.path === "/oauth2/token",
      );
      assert.equal(exchange.length, 1);
      assert.equal(exchange[0]!.body.redirect_uri, expected);
      assert.equal(exchange[0]!.body.code_verifier, "unit-bound-pkce-verifier");
      assert.ok(identity);
      service.caps.account_ref = "00000000-0000-4000-8000-000000000099";
      const targets =
        platform === "web"
          ? [
              "https://localhost:8082/",
              "http://foreign.invalid:8082/",
              "http://localhost:8083/",
              "http://localhost:8082/wrong",
              "http://localhost:8082/extra",
              "http://user@localhost:8082/",
              "http://localhost:8082/path/../",
              "otgd-local://oauth/callback",
              "http://localhost:8082/#fragment",
            ]
          : [
              "otgd-other://oauth/callback",
              "otgd-local://foreign/callback",
              "otgd-local://oauth:8082/callback",
              "otgd-local://oauth/wrong",
              "otgd-local://oauth/callback-extra",
              "otgd-local://user@oauth/callback",
              "otgd-local://oauth/path/../callback",
              "http://localhost:8082/",
              "otgd-local://oauth/callback#fragment",
            ];
      for (const target of targets) {
        service.calls.length = 0;
        runtime.prompt = async (request: any) => ({
          ...success(request),
          url: target + "?" + new URLSearchParams(success(request).params),
        });
        await assert.rejects(() => app.signIn(), { code: "OAUTH_REJECTED" });
        assert.equal(service.calls.length, 0, "Refusal must precede all HTTP");
        assert.deepEqual(app.getSnapshot().identity, identity);
        assert.deepEqual(app.auth.identity, identity);
        assert.equal(app.auth.generation, generation);
      }
    } finally {
      await app.auth.clear();
      await app.dispose();
      globalThis.fetch = priorFetch;
      globalThis.location = priorLocation;
      Platform.OS = priorPlatform;
      runtime.prompt = priorPrompt;
    }
  });
}

test("a success callback requires an unambiguous exact code/state query bound to SDK params before token or account traffic", async () => {
  const service = customerService(),
    priorFetch = globalThis.fetch,
    priorLocation = globalThis.location,
    priorPrompt = runtime.prompt;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  const app = new AppController();
  try {
    await app.auth.clear();
    runtime.prompt = async (request: any) => success(request);
    await app.initialize();
    assert.equal(await app.signIn(), true);
    const identity = structuredClone(app.getSnapshot().identity),
      generation = app.auth.generation;
    const mutations: ((response: ReturnType<typeof success>) => unknown)[] = [
      () => undefined,
      () => null,
      () => 123,
      () => "not a URL",
      () => "",
      (response) => response.url + "#fragment",
      (response) => response.url + "#",
      (response) => response.url + "&code=" + response.params.code,
      (response) => response.url + "&state=" + response.params.state,
      (response) => response.url + "&unexpected=value",
      (response) => response.url.replace("fictional-callback-code", "other"),
      (response) => response.url.replace(response.params.state, "other"),
      (response) => response.url.replace(/&code=[^&]+/, ""),
      (response) => response.url.replace(/state=[^&]+&/, ""),
      (response) => response.url + "&",
    ];
    for (const mutate of mutations) {
      service.calls.length = 0;
      runtime.prompt = async (request: any) => {
        const response = success(request);
        return { ...response, url: mutate(response) };
      };
      await assert.rejects(() => app.signIn(), { code: "OAUTH_REJECTED" });
      assert.equal(service.calls.length, 0);
      assert.deepEqual(app.getSnapshot().identity, identity);
      assert.deepEqual(app.auth.identity, identity);
      assert.equal(app.auth.generation, generation);
    }
    // Refusal leaves no consumed code or credential mutation: a fresh exact
    // callback still exchanges successfully through the same controller.
    runtime.prompt = async (request: any) => success(request);
    assert.equal(await app.signIn(), true);
    assert.equal(
      service.calls.filter((call) => call.path === "/oauth2/token").length,
      1,
    );
    assert.equal(app.auth.identity?.accountRef, identity?.accountRef);
  } finally {
    await app.auth.clear();
    await app.dispose();
    globalThis.fetch = priorFetch;
    globalThis.location = priorLocation;
    runtime.prompt = priorPrompt;
  }
});
