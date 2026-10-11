import test from "node:test";
import assert from "node:assert/strict";
import { ApiClient } from "../src/services/api";
import configure from "../app.config";

process.env.OTGD_UNIT_PREVIEW = "true";
require("./support/runtime.cjs");
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");

test("hosted preview starts an isolated fictional guest flow without reading account credentials or calling any service", async () => {
  const previous = globalThis.fetch;
  let calls = 0,
    restoreCalls = 0;
  globalThis.fetch = async () => {
    calls++;
    throw Error("preview must not use the network");
  };
  const app = new AppController();
  app.auth.restore = async () => {
    restoreCalls++;
    throw Error("preview must not restore an account");
  };
  try {
    await app.initialize();
    await app.enterDemo();
    await app.acknowledgeNotice();
    assert.equal(app.getSnapshot().identity, null);
    assert.equal(
      app.getSnapshot().state!.workspace,
      "guest:local:fictional-preview",
    );
    await app.beginCheck("guest_demo", true);
    await app.simulate("saliva");
    await app.simulate("eyes");
    await app.simulate("cardiac");
    await app.saveCheck();
    assert.equal(app.getSnapshot().state!.queue.length, 0);
    assert.equal(app.check!.snapshot.eyes.source, "simulated");
    assert.equal(app.check!.result!.state, "measurement_only");
    assert.equal(app.check!.result!.probability, null);
    await assert.rejects(app.signIn(), /fictional preview/);
    await assert.rejects(app.startNativeTask(), /fictional preview/);
    await assert.rejects(
      app.beginCheck("measurement", true),
      /fictional guest/,
    );
    await assert.rejects(
      app.api.request("/v1/app-config", { public: true }),
      /does not connect/,
    );
    await app.device.scan();
    assert.equal(app.device.snapshot().state, "unavailable");
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(calls, 0);
    assert.equal(restoreCalls, 0);
    await app.clearLocal();
    assert.equal(app.getSnapshot().state!.checks.length, 0);
  } finally {
    await app.dispose();
    globalThis.fetch = previous;
  }
});

test("network-disabled API transport refuses even explicitly supplied credentials and cloud downloads", async () => {
  let providerCalls = 0;
  const api = new ApiClient(
    "https://unreachable.example.test",
    {
      accessToken: async () => {
        providerCalls++;
        return "access";
      },
    },
    "0.2.0",
    undefined,
    () => false,
  );
  await assert.rejects(
    api.request("/v1/me/capabilities", { token: "old-account-access" }),
    /does not connect/,
  );
  await assert.rejects(
    api.download(
      "/v1/privacy/jobs/88888888-8888-4888-8888-888888888888/download",
      1,
    ),
    /fictional guest/,
  );
  assert.equal(providerCalls, 0);
});

test("the hosted preview build flag is local-only and cannot alter QA or production account behavior", () => {
  const keys = [
    "APP_ENV",
    "EXPO_PUBLIC_APP_ENV",
    "EXPO_PUBLIC_HOSTED_PREVIEW",
  ] as const;
  const saved = Object.fromEntries(keys.map((key) => [key, process.env[key]]));
  try {
    process.env.EXPO_PUBLIC_HOSTED_PREVIEW = "true";
    for (const environment of ["qa", "prod", "test"]) {
      process.env.APP_ENV = environment;
      process.env.EXPO_PUBLIC_APP_ENV = environment;
      assert.throws(
        () => configure({ config: {} } as any),
        /only in APP_ENV=local/,
      );
    }
    process.env.APP_ENV = "local";
    process.env.EXPO_PUBLIC_APP_ENV = "local";
    const config = configure({ config: {} } as any);
    assert.equal(config.extra!.hostedPreview, true);
    assert.equal(config.ios!.infoPlist!.OTGDHostedPreview, true);
    process.env.EXPO_PUBLIC_HOSTED_PREVIEW = "yes";
    assert.throws(() => configure({ config: {} } as any), /true or false/);
  } finally {
    for (const key of keys) {
      if (saved[key] === undefined) delete process.env[key];
      else process.env[key] = saved[key];
    }
  }
});
