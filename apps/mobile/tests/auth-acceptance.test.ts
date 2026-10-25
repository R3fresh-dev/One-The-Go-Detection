import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { once } from "node:events";
import "./support/runtime.cjs";
import { customerService, deferred } from "./support/customer";
import { ApiClient, parseAppConfig } from "../src/services/api";
import type { Identity } from "../src/core/types";
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");
const { AuthManager } =
  require("../src/services/auth") as typeof import("../src/services/auth");

test("OTGD-037-AND-AUTH-002-01: replaying an already exchanged successful callback cannot exchange again or switch accounts", async () => {
  const service = customerService(),
    previousFetch = globalThis.fetch,
    previousLocation = globalThis.location,
    runtime = (globalThis as any).__otgdUnitRuntime,
    previousPrompt = runtime.prompt;
  let callback: {
    type: "success";
    params: { state: string; code: string };
    url: string;
  };
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  const app = new AppController();
  try {
    await app.auth.clear();
    runtime.prompt = async (request: {
      state: string;
      redirectUri: string;
    }) => {
      callback = {
        type: "success",
        params: { state: request.state, code: "fictional-exchanged-once" },
        url:
          request.redirectUri +
          "?" +
          new URLSearchParams({
            state: request.state,
            code: "fictional-exchanged-once",
          }),
      };
      return callback;
    };
    await app.initialize();
    assert.equal(await app.signIn(), true);
    const originalIdentity = structuredClone(app.getSnapshot().identity),
      originalAuthGeneration = app.auth.generation;
    assert.equal(originalIdentity?.accountRef, service.caps.account_ref);
    const tokenCalls = () =>
      service.calls.filter((call) => call.path === "/oauth2/token");
    assert.equal(tokenCalls().length, 1);
    assert.equal(tokenCalls()[0]!.body.code, callback!.params.code);
    assert.equal(tokenCalls()[0]!.body.grant_type, "authorization_code");
    assert.equal(
      tokenCalls()[0]!.body.code_verifier,
      "unit-bound-pkce-verifier",
    );
    const capabilityCalls = service.calls.filter(
      (call) => call.path === "/v1/me/capabilities",
    ).length;
    // If a replay wrongly reaches the protected identity lookup, this different
    // fictional account makes an unintended account switch observable.
    service.caps.account_ref = "00000000-0000-4000-8000-000000000099";
    let replayDeliveries = 0;
    runtime.prompt = async (request: { state: string }) => {
      replayDeliveries++;
      assert.notEqual(request.state, callback!.params.state);
      return structuredClone(callback!);
    };
    await assert.rejects(() => app.signIn(), { code: "OAUTH_REJECTED" });
    assert.equal(replayDeliveries, 1);
    assert.equal(tokenCalls().length, 1);
    assert.equal(
      service.calls.filter((call) => call.path === "/v1/me/capabilities")
        .length,
      capabilityCalls,
    );
    assert.deepEqual(app.getSnapshot().identity, originalIdentity);
    assert.deepEqual(app.auth.identity, originalIdentity);
    assert.equal(app.auth.generation, originalAuthGeneration);
    assert.equal(await app.auth.accessToken(), "signed-unit-access");
  } finally {
    await app.auth.clear();
    await app.dispose();
    globalThis.fetch = previousFetch;
    globalThis.location = previousLocation;
    runtime.prompt = previousPrompt;
  }
});

test("OTGD-037-AND-AUTH-004-01: three HTTP401 responses share one refresh and each request replays once with its original operation", async () => {
  const previousFetch = globalThis.fetch,
    initialRequests = deferred<void>(),
    allRefreshWaiters = deferred<void>(),
    refreshEntered = deferred<void>(),
    releaseRefresh = deferred<void>();
  const captures: {
    path: string;
    method: string;
    body: string;
    authorization: string | undefined;
    key: string | undefined;
    generation: string | undefined;
    etag: string | undefined;
  }[] = [];
  const requests = ["one", "two", "three"].map((id) => ({
    path: `/v1/sessions/fictional-${id}/finalize`,
    key: `fictional-finalize-${id}`,
    body: { snapshot_sha256: id.repeat(8), reference: { label: id } },
    etag: `"fictional-revision-${id}"`,
  }));
  let expiredRequests = 0,
    refreshRequests = 0,
    refreshWaiters = 0;
  const server = createServer(async (request, response) => {
    const chunks: Buffer[] = [];
    for await (const chunk of request) chunks.push(Buffer.from(chunk));
    const body = Buffer.concat(chunks).toString("utf8");
    const reply = (status: number, value: unknown) => {
      response.writeHead(status, { "Content-Type": "application/json" });
      response.end(JSON.stringify(value));
    };
    if (request.url === "/oauth2/token") {
      refreshRequests++;
      const fields = Object.fromEntries(new URLSearchParams(body));
      assert.deepEqual(fields, {
        grant_type: "refresh_token",
        client_id: "otgd-local-mobile",
        refresh_token: "fictional-refresh-family",
      });
      refreshEntered.resolve();
      await releaseRefresh.promise;
      reply(200, {
        access_token: "fictional-rotated-access",
        token_type: "Bearer",
        expires_in: 900,
      });
      return;
    }
    captures.push({
      path: request.url!,
      method: request.method!,
      body,
      authorization: request.headers.authorization,
      key: request.headers["idempotency-key"] as string | undefined,
      generation: request.headers["x-data-generation"] as string | undefined,
      etag: request.headers["if-match"],
    });
    if (request.headers.authorization === "Bearer fictional-expired-access") {
      if (++expiredRequests === 3) initialRequests.resolve();
      await initialRequests.promise;
      reply(401, { code: "TOKEN_EXPIRED", message: "Fictional expiry." });
      return;
    }
    if (request.headers.authorization !== "Bearer fictional-rotated-access") {
      reply(403, { code: "UNEXPECTED_FICTIONAL_CREDENTIAL" });
      return;
    }
    reply(200, { accepted: request.url });
  });
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const address = server.address();
  assert.ok(address && typeof address !== "string");
  const origin = `http://127.0.0.1:${address.port}`,
    auth = new AuthManager();
  // Only the independently pinned fictional issuer destination is remapped to
  // this ephemeral HTTP fixture. ApiClient requests use real fetch unchanged.
  globalThis.fetch = (input, init) => {
    const url = new URL(String(input));
    if (url.origin === "http://localhost:8081") {
      assert.equal(url.pathname, "/oauth2/token");
      return previousFetch(`${origin}${url.pathname}`, init);
    }
    assert.equal(url.origin, origin);
    return previousFetch(input, init);
  };
  try {
    await auth.clear();
    const config = parseAppConfig(customerService().config, {
      environment: "test",
      issuer: "http://localhost:8081",
      clientId: "otgd-local-mobile",
      oauthOrigin: "http://localhost:8081",
      redirectUris: ["otgd-local://oauth/callback", "http://localhost:8082/"],
    });
    const identity: Identity = {
      issuer: config.auth.issuer,
      accountRef: "00000000-0000-4000-8000-000000000037",
      generation: 3,
      state: "active",
      verifiedAt: "2026-10-25T00:00:00Z",
    };
    await auth.commit(
      {
        accessToken: "fictional-expired-access",
        refreshToken: "fictional-refresh-family",
        // Locally unexpired; real HTTP401 is what must trigger recovery.
        expiresAt: Date.now() + 900_000,
        auth: config.auth,
      },
      identity,
    );
    const api = new ApiClient(origin, {
      accessToken(force) {
        if (force && ++refreshWaiters === 3) allRefreshWaiters.resolve();
        return auth.accessToken(force);
      },
    });
    const pending = requests.map((request) =>
      api.request(request.path, {
        method: "POST",
        body: request.body,
        key: request.key,
        etag: request.etag,
        generation: identity.generation,
      }),
    );
    await Promise.all([refreshEntered.promise, allRefreshWaiters.promise]);
    assert.equal(expiredRequests, 3);
    assert.equal(refreshWaiters, 3);
    assert.equal(refreshRequests, 1);
    assert.equal(captures.length, 3);
    releaseRefresh.resolve();
    assert.deepEqual(
      (await Promise.all(pending)).map((response) => response.value),
      requests.map((request) => ({ accepted: request.path })),
    );
    assert.equal(refreshRequests, 1);
    assert.equal(captures.length, 6);
    for (const request of requests) {
      const calls = captures.filter((call) => call.path === request.path);
      assert.equal(calls.length, 2);
      assert.deepEqual(
        calls.map(({ authorization, ...operation }) => operation),
        Array.from({ length: 2 }, () => ({
          path: request.path,
          method: "POST",
          body: JSON.stringify(request.body),
          key: request.key,
          generation: "3",
          etag: request.etag,
        })),
      );
      assert.deepEqual(
        calls.map((call) => call.authorization),
        ["Bearer fictional-expired-access", "Bearer fictional-rotated-access"],
      );
    }
    assert.deepEqual(auth.identity, identity);
    assert.equal(await auth.accessToken(), "fictional-rotated-access");
  } finally {
    releaseRefresh.resolve();
    await auth.clear();
    globalThis.fetch = previousFetch;
    server.closeAllConnections();
    await new Promise<void>((resolve, reject) =>
      server.close((error) => (error ? reject(error) : resolve())),
    );
  }
});
