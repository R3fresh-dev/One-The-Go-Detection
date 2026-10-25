import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");
const { openWorkspaceStore } =
  require("../src/platform/storage") as typeof import("../src/platform/storage");

test("motion system choice and explicit booleans survive workspace reopen without changing other preferences", async () => {
  const previous = globalThis.fetch;
  globalThis.fetch = async () => {
    throw Error("offline unit boundary");
  };
  let app = new AppController();
  try {
    await app.initialize();
    await app.enterDemo();
    await app.changePreferences({ theme: "dark", units: "imperial" });
    for (const reducedMotion of [true, false, "system"] as const) {
      await app.changePreferences({ reducedMotion });
      const workspace = app.getSnapshot().state!.workspace;
      const store = await openWorkspaceStore(workspace);
      assert.equal(
        (await store.load())!.preferences.reducedMotion,
        reducedMotion,
      );
      await store.close();
      await app.dispose();
      app = new AppController();
      await app.initialize();
      assert.deepEqual(app.getSnapshot().state!.preferences, {
        theme: "dark",
        units: "imperial",
        reducedMotion,
        retryQueuedAutomatically: false,
      });
    }
  } finally {
    await app.dispose();
    globalThis.fetch = previous;
  }
});
