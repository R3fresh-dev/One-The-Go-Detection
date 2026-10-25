import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
import { customerService, deferred } from "./support/customer";
import { parseAppConfig, ApiError } from "../src/services/api";
import type { Identity } from "../src/core/types";
const { AuthManager } =
  require("../src/services/auth") as typeof import("../src/services/auth");
const { vault } =
  require("../src/platform/storage") as typeof import("../src/platform/storage");
const unit = () => (globalThis as any).__otgdUnitRuntime;
async function harness() {
  const service = customerService(),
    previous = globalThis.fetch;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  let invalidated = 0;
  const auth = new AuthManager(() => {
    invalidated++;
  });
  await auth.clear();
  unit().prompt = async (request: any) => ({
    type: "success",
    params: { state: request.state, code: "one-time-code" },
  });
  const config = parseAppConfig(service.config, {
    environment: "test",
    issuer: "http://localhost:8081",
    clientId: "otgd-local-mobile",
  });
  const identity: Identity = {
    issuer: config.auth.issuer,
    accountRef: service.caps.account_ref,
    generation: 1,
    state: "active",
    verifiedAt: new Date().toISOString(),
  };
  return {
    auth,
    service,
    config,
    identity,
    invalidated: () => invalidated,
    close: async () => {
      await auth.clear();
      globalThis.fetch = previous;
    },
  };
}

test("a stalled OAuth refresh has a bounded deadline and its late reply cannot replace retained credentials", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const { auth, service, config, identity, close } = await harness();
  try {
    const tokens = (await auth.authorize(config))!;
    await auth.commit({ ...tokens, expiresAt: 0 }, identity);
    const entered = deferred<void>(),
      reply = deferred<Response>();
    service.overrides.set("/oauth2/token", () => {
      entered.resolve();
      return reply.promise;
    });
    const pending = auth.accessToken();
    const rejected = assert.rejects(pending, {
      code: "AUTH_NETWORK_UNAVAILABLE",
    });
    await entered.promise;
    t.mock.timers.tick(15_000);
    await rejected;
    assert.deepEqual(auth.identity, identity);
    reply.resolve(
      service.result({
        access_token: "late-access",
        refresh_token: "late-refresh",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(auth.logoutReceiptToken(), tokens.accessToken);
    assert.equal(
      JSON.parse((await vault.get("otgd.auth.test"))!).refreshToken,
      "unit-refresh",
    );
    service.overrides.set("/oauth2/token", () =>
      service.result({
        access_token: "recovered-access",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    assert.equal(await auth.accessToken(), "recovered-access");
  } finally {
    await close();
  }
});

test("authorization supplies a fresh cryptographic state satisfying the issuer minimum", async () => {
  const { auth, config, close } = await harness();
  const states: string[] = [];
  try {
    unit().prompt = async (request: { state: string }) => {
      assert.match(request.state, /^[A-Za-z0-9_-]{32,256}$/);
      states.push(request.state);
      return { type: "cancel" };
    };
    assert.equal(await auth.authorize(config), null);
    assert.equal(await auth.authorize(config), null);
    assert.equal(states.length, 2);
    assert.notEqual(states[0], states[1]);
  } finally {
    await close();
  }
});

test("PKCE callback binds state and verifier and credential restore uses verified API identity", async () => {
  const { auth, service, config, identity, close } = await harness();
  try {
    assert.equal(await auth.restore(), null);
    const tokens = await auth.authorize(config);
    assert.ok(tokens);
    await auth.commit(tokens, identity);
    assert.equal(await auth.accessToken(), "signed-unit-access");
    const saved = new AuthManager();
    assert.deepEqual(await saved.restore(), identity);
    const request = service.calls.find((call) => call.path === "/oauth2/token");
    assert.equal(request?.body.grant_type, "authorization_code");
    assert.equal(request?.body.code_verifier, "unit-bound-pkce-verifier");
    assert.equal(request?.body.redirect_uri, "http://localhost:8082/");
    assert.equal(auth.logoutReceiptToken(), "signed-unit-access");
    await assert.rejects(
      () =>
        auth.commit(tokens, { ...identity, issuer: "https://other.example" }),
      /issuer/,
    );
  } finally {
    await close();
  }
});

test("cancelled, wrong-state, duplicate and invalidated callbacks cannot exchange a code", async () => {
  const { auth, service, config, close } = await harness();
  try {
    unit().prompt = async () => ({ type: "cancel" });
    assert.equal(await auth.authorize(config), null);
    unit().prompt = async () => ({
      type: "success",
      params: { state: "wrong", code: "stolen-code" },
    });
    await assert.rejects(() => auth.authorize(config), /verified/);
    assert.equal(service.calls.length, 0);
    const entered = deferred<void>(),
      answer = deferred<any>();
    unit().prompt = async (request: any) => {
      entered.resolve();
      await answer.promise;
      return {
        type: "success",
        params: { state: request.state, code: "old-code" },
      };
    };
    const pending = auth.authorize(config);
    await entered.promise;
    await auth.clear();
    const rejected = assert.rejects(() => pending, /expired|canceled/);
    answer.resolve(null);
    await rejected;
    assert.equal(service.calls.length, 0);
    await assert.rejects(
      () =>
        auth.authorize({
          ...config,
          auth: { ...config.auth, redirect_uris: [] },
        }),
      /callback/i,
    );
  } finally {
    await close();
  }
});

test("one current refresh request preserves an omitted refresh token and every waiter receives the same access token", async () => {
  const { auth, service, config, identity, close } = await harness();
  try {
    const tokens = (await auth.authorize(config))!;
    await auth.commit({ ...tokens, expiresAt: 0 }, identity);
    const entered = deferred<void>(),
      reply = deferred<Response>();
    service.overrides.set("/oauth2/token", () => {
      entered.resolve();
      return reply.promise;
    });
    const first = auth.accessToken();
    await entered.promise;
    const second = auth.accessToken();
    reply.resolve(
      service.result({
        access_token: "rotated",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    assert.deepEqual(await Promise.all([first, second]), [
      "rotated",
      "rotated",
    ]);
    const raw = JSON.parse((await vault.get("otgd.auth.test"))!);
    assert.equal(raw.refreshToken, "unit-refresh");
    assert.equal(
      service.calls.filter((call) => call.body?.grant_type === "refresh_token")
        .length,
      1,
    );
    await auth.whenRefreshSettled();
  } finally {
    await close();
  }
});

test("revoked refresh clears the current account while transient connection failure retains its protected identity", async () => {
  const { auth, service, config, identity, invalidated, close } =
    await harness();
  try {
    const tokens = (await auth.authorize(config))!;
    await auth.commit({ ...tokens, expiresAt: 0 }, identity);
    service.overrides.set("/oauth2/token", () => {
      throw Error("network unavailable");
    });
    await assert.rejects(() => auth.accessToken(), {
      code: "AUTH_NETWORK_UNAVAILABLE",
    });
    assert.deepEqual(auth.identity, identity);
    service.overrides.set("/oauth2/token", () =>
      service.result({ error: "invalid_grant" }, 400),
    );
    await assert.rejects(() => auth.accessToken(), { code: "AUTH_REQUIRED" });
    assert.equal(auth.identity, null);
    assert.equal(await vault.get("otgd.auth.test"), null);
    assert.equal(invalidated(), 1);
    assert.equal(await auth.accessToken(), null);
  } finally {
    await close();
  }
});

test("a stale refresh response cannot clear or overwrite a newly signed-in account", async () => {
  const { auth, service, config, identity, close } = await harness();
  try {
    const tokens = (await auth.authorize(config))!;
    await auth.commit({ ...tokens, expiresAt: 0 }, identity);
    const entered = deferred<void>(),
      reply = deferred<Response>();
    service.overrides.set("/oauth2/token", () => {
      entered.resolve();
      return reply.promise;
    });
    const old = auth.accessToken();
    await entered.promise;
    const next = {
      ...identity,
      accountRef: "00000000-0000-4000-8000-000000000002",
    };
    await auth.commit(
      { ...tokens, accessToken: "account-B", refreshToken: "refresh-B" },
      next,
    );
    const rejected = assert.rejects(() => old, { code: "AUTH_CHANGED" });
    reply.resolve(
      service.result({
        access_token: "old-A",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    await rejected;
    assert.equal(await auth.accessToken(), "account-B");
    assert.equal(auth.identity?.accountRef, next.accountRef);
  } finally {
    await close();
  }
});

test("a current-account refresh starts independently from an older in-flight account refresh", async () => {
  const { auth, service, config, identity, close } = await harness();
  try {
    const tokens = (await auth.authorize(config))!;
    await auth.commit({ ...tokens, expiresAt: 0 }, identity);
    const entered = deferred<void>(),
      reply = deferred<Response>();
    service.overrides.set("/oauth2/token", (call) => {
      if (call.body.refresh_token === "unit-refresh") {
        entered.resolve();
        return reply.promise;
      }
      return service.result({
        access_token: "fresh-B",
        token_type: "Bearer",
        expires_in: 900,
      });
    });
    const old = auth.accessToken();
    await entered.promise;
    await auth.commit(
      { ...tokens, accessToken: "B", refreshToken: "refresh-B", expiresAt: 0 },
      { ...identity, accountRef: "00000000-0000-4000-8000-000000000002" },
    );
    const current = auth.accessToken();
    await new Promise((resolve) => setImmediate(resolve));
    assert.equal(
      service.calls.filter((call) => call.body?.refresh_token === "refresh-B")
        .length,
      1,
    );
    const rejected = assert.rejects(() => old, { code: "AUTH_CHANGED" });
    reply.resolve(
      service.result({
        access_token: "old-A",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    await rejected;
    assert.equal(await current, "fresh-B");
  } finally {
    await close();
  }
});

test("credential writes cannot finish after a serialized sign-out removal", async () => {
  const { auth, config, identity, close } = await harness();
  const set = vault.set;
  try {
    const tokens = (await auth.authorize(config))!;
    const entered = deferred<void>(),
      release = deferred<void>();
    vault.set = async (key, value) => {
      entered.resolve();
      await release.promise;
      await set(key, value);
    };
    const pending = auth.commit(tokens, identity);
    await entered.promise;
    const clear = auth.clear();
    const rejected = assert.rejects(() => pending, { code: "AUTH_CHANGED" });
    release.resolve();
    await Promise.all([rejected, clear]);
    assert.equal(await vault.get("otgd.auth.test"), null);
    assert.equal(auth.identity, null);
  } finally {
    vault.set = set;
    await close();
  }
});

test("provider revocation and configured browser logout use the captured family without changing a replacement account", async () => {
  const { auth, service, config, identity, close } = await harness();
  try {
    const tokens = (await auth.authorize(config))!;
    await auth.commit(tokens, identity);
    const url = new URL(auth.providerLogoutUrl()!);
    assert.equal(url.origin, "http://localhost:8081");
    assert.equal(url.searchParams.get("client_id"), "otgd-local-mobile");
    assert.equal(url.searchParams.get("logout_uri"), "http://localhost:8082/");
    await auth.revokeProvider();
    assert.equal(
      service.calls.find((call) => call.path === "/oauth2/revoke")?.body.token,
      "unit-refresh",
    );
    await auth.openProviderLogout(url.toString());
    await auth.browserLogout();
    assert.ok(unit().providerCalls.length >= 2);
    await auth.updateIdentity({ ...identity, generation: 2 });
    assert.equal(auth.identity?.generation, 2);
    await auth.updateIdentity({ ...identity, accountRef: "other-account" });
    assert.equal(auth.identity?.generation, 2);
    await auth.clear();
    assert.equal(auth.providerLogoutUrl(), null);
    await auth.revokeProvider();
    await auth.browserLogout();
  } finally {
    await close();
  }
});

test("authorization-code tokens cannot inherit a prior account refresh credential and malformed responses are refused", async () => {
  const { auth, service, config, identity, close } = await harness();
  try {
    service.overrides.set("/oauth2/token", () =>
      service.result({
        access_token: "access-only",
        token_type: "Bearer",
        expires_in: 900,
      }),
    );
    const tokens = (await auth.authorize(config))!;
    assert.equal(tokens.refreshToken, null);
    await auth.commit({ ...tokens, expiresAt: 0 }, identity);
    assert.equal(await auth.accessToken(), null);
    service.overrides.set("/oauth2/token", () =>
      service.result({
        access_token: "bad",
        token_type: "Other",
        expires_in: 0,
      }),
    );
    await assert.rejects(() => auth.authorize(config), {
      code: "AUTH_REQUIRED",
    });
    await vault.set(
      "otgd.auth.test",
      JSON.stringify({
        identity: { ...identity, issuer: "https://foreign.example" },
        auth: config.auth,
      }),
    );
    await assert.rejects(() => new AuthManager().restore(), /another service/);
  } finally {
    await close();
  }
});
