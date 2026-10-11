import test from "node:test";
import assert from "node:assert/strict";
import { ApiClient, ApiError } from "../src/services/api";
import { deferred } from "./support/customer";

const origin = "https://api.example.test";
const timeoutError = (error: unknown) =>
  error instanceof ApiError &&
  error.code === "REQUEST_TIMEOUT" &&
  error.retryable;

test("a stalled refresh cannot hold an API request past its 15-second deadline or send late credentials", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const previous = globalThis.fetch;
  const entered = deferred<void>(),
    token = deferred<string>();
  let requests = 0;
  globalThis.fetch = async () => {
    requests++;
    return new Response("{}");
  };
  try {
    const api = new ApiClient(origin, {
      accessToken: () => {
        entered.resolve();
        return token.promise;
      },
    });
    const request = api.request("/v1/me/capabilities");
    const rejected = assert.rejects(request, timeoutError);
    await entered.promise;
    t.mock.timers.tick(15_000);
    await rejected;
    token.resolve("late-account-token");
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(requests, 0);
  } finally {
    globalThis.fetch = previous;
  }
});

test("a transport or JSON body that ignores AbortSignal still settles within the request deadline", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const previous = globalThis.fetch;
  try {
    for (const phase of ["fetch", "body"] as const) {
      const entered = deferred<void>(),
        stalled = deferred<any>();
      globalThis.fetch = async () => {
        if (phase === "fetch") {
          entered.resolve();
          return stalled.promise;
        }
        return {
          ok: true,
          status: 200,
          headers: new Headers(),
          text: () => {
            entered.resolve();
            return stalled.promise;
          },
        } as Response;
      };
      const api = new ApiClient(origin, { accessToken: async () => "access" });
      const request = api.request("/v1/me/profile");
      const rejected = assert.rejects(request, timeoutError);
      await entered.promise;
      t.mock.timers.tick(15_000);
      await rejected;
      stalled.resolve(phase === "fetch" ? new Response("{}") : "{}");
      await new Promise<void>((resolve) => setImmediate(resolve));
    }
  } finally {
    globalThis.fetch = previous;
  }
});

test("401 recovery shares the original request deadline rather than extending it", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const previous = globalThis.fetch;
  const entered = deferred<void>(),
    response = deferred<Response>(),
    refresh = deferred<string>(),
    refreshing = deferred<void>();
  let requests = 0;
  globalThis.fetch = async () => {
    requests++;
    entered.resolve();
    return response.promise;
  };
  try {
    const api = new ApiClient(origin, {
      accessToken: async (force) => {
        if (force) {
          refreshing.resolve();
          return refresh.promise;
        }
        return "expired";
      },
    });
    const request = api.request("/v1/me/capabilities");
    const rejected = assert.rejects(request, timeoutError);
    await entered.promise;
    t.mock.timers.tick(10_000);
    response.resolve(new Response('{"code":"INVALID_TOKEN"}', { status: 401 }));
    await refreshing.promise;
    t.mock.timers.tick(5_000);
    await rejected;
    refresh.resolve("new-access");
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(requests, 1);
  } finally {
    globalThis.fetch = previous;
  }
});

test("cancelAll settles pending token recovery, and an already canceled caller never invokes fetch", async () => {
  const previous = globalThis.fetch;
  const token = deferred<string>(),
    entered = deferred<void>();
  let requests = 0,
    providers = 0;
  globalThis.fetch = async () => {
    requests++;
    return new Response("{}");
  };
  try {
    const api = new ApiClient(origin, {
      accessToken: () => {
        providers++;
        entered.resolve();
        return token.promise;
      },
    });
    const request = api.request("/v1/me/profile");
    const rejected = assert.rejects(
      request,
      (error: unknown) =>
        error instanceof ApiError && error.code === "REQUEST_CANCELED",
    );
    await entered.promise;
    api.cancelAll();
    await rejected;
    token.resolve("old-token");
    const controller = new AbortController();
    controller.abort();
    await assert.rejects(
      api.request("/v1/me/profile", { signal: controller.signal }),
      /canceled/,
    );
    assert.equal(providers, 1);
    assert.equal(requests, 0);
  } finally {
    globalThis.fetch = previous;
  }
});

test("the export download deadline covers credentials and the full binary body; cancellation discards late bytes", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const previous = globalThis.fetch;
  const token = deferred<string>(),
    entered = deferred<void>();
  let requests = 0;
  const route =
    "/v1/privacy/jobs/88888888-8888-4888-8888-888888888888/download";
  globalThis.fetch = async () => {
    requests++;
    return new Response("data", { headers: { "Content-Length": "4" } });
  };
  try {
    const api = new ApiClient(origin, {
      accessToken: () => {
        entered.resolve();
        return token.promise;
      },
    });
    const download = api.download(route, 1, 4);
    const rejected = assert.rejects(download, timeoutError);
    await entered.promise;
    t.mock.timers.tick(60_000);
    await rejected;
    token.resolve("late-token");
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(requests, 0);
    const body = deferred<ArrayBuffer>(),
      reading = deferred<void>();
    globalThis.fetch = async () =>
      ({
        ok: true,
        headers: new Headers({ "Content-Length": "4" }),
        arrayBuffer: () => {
          reading.resolve();
          return body.promise;
        },
      }) as Response;
    const current = new ApiClient(origin, {
      accessToken: async () => "access",
    });
    const buffered = current.download(route, 1, 4);
    const canceled = assert.rejects(buffered, /canceled/);
    await reading.promise;
    current.cancelAll();
    await canceled;
    body.resolve(new Uint8Array([1, 2, 3, 4]).buffer);
    await new Promise<void>((resolve) => setImmediate(resolve));
    globalThis.fetch = async () =>
      new Response("data", { headers: { "Content-Length": "4" } });
    assert.equal(
      new TextDecoder().decode(await current.download(route, 1, 4)),
      "data",
    );
  } finally {
    globalThis.fetch = previous;
  }
});
