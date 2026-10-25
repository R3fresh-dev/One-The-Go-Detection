import test from "node:test";
import assert from "node:assert/strict";
import { buildSync } from "esbuild";
import { deferred } from "./support/customer";

const compiled = buildSync({
  entryPoints: ["src/platform/sharing.native.ts"],
  bundle: true,
  write: false,
  platform: "node",
  format: "cjs",
  external: ["expo-file-system", "expo-sharing"],
}).outputFiles![0]!.text;

function nativeBoundary(available: Promise<boolean>) {
  const events: string[] = [];
  class Directory {
    create() {
      events.push("directory");
    }
  }
  class File {
    exists = false;
    uri = "file:///fictional-only.zip";
    create() {
      this.exists = true;
      events.push("create");
    }
    write() {
      events.push("write");
    }
    delete() {
      this.exists = false;
      events.push("delete");
    }
  }
  const output = { exports: {} as any };
  const boundaryRequire = (name: string) =>
    name === "expo-file-system"
      ? { Directory, File, Paths: { cache: "fictional-cache" } }
      : name === "expo-sharing"
        ? {
            isAvailableAsync: () => {
              events.push("availability");
              return available;
            },
            shareAsync: async () => {
              events.push("share");
            },
          }
        : require(name);
  new Function("module", "exports", "require", compiled)(
    output,
    output.exports,
    boundaryRequire,
  );
  return {
    events,
    share: output.exports
      .shareArchive as typeof import("../src/platform/sharing.native").shareArchive,
  };
}

test("actual native sharing waits for availability then fresh release admission before any file or share", async () => {
  const available = deferred<boolean>(),
    { events, share } = nativeBoundary(available.promise);
  let authorization = 0;
  const pending = share(
    new Uint8Array([1]),
    "fictional",
    () => events.push("guard"),
    async () => {
      authorization++;
      events.push("fresh-admission");
      throw Error("Fictional authority retired during availability await");
    },
  );
  assert.equal(authorization, 0);
  assert.deepEqual(events, ["availability"]);
  available.resolve(true);
  await assert.rejects(pending, /authority retired/);
  assert.equal(authorization, 1);
  assert.deepEqual(events, ["availability", "fresh-admission"]);
});

test("actual native sharing keeps synchronous scope guard after final admission await and cleans rejected files", async () => {
  const admission = deferred<void>(),
    { events, share } = nativeBoundary(Promise.resolve(true));
  let live = true;
  const pending = share(
    new Uint8Array([1]),
    "fictional",
    () => {
      events.push("guard");
      if (!live) throw Error("Workspace changed");
    },
    async () => {
      events.push("fresh-admission");
      await admission.promise;
    },
  );
  await new Promise(setImmediate);
  live = false;
  admission.resolve();
  await assert.rejects(pending, /Workspace changed/);
  assert.deepEqual(events, ["availability", "fresh-admission", "guard"]);

  const next = nativeBoundary(Promise.resolve(true));
  let guards = 0;
  await assert.rejects(
    next.share(
      new Uint8Array([1]),
      "fictional",
      () => {
        next.events.push("guard");
        if (++guards === 2) throw Error("Workspace changed before share");
      },
      async () => {
        next.events.push("fresh-admission");
      },
    ),
    /Workspace changed/,
  );
  assert.deepEqual(next.events, [
    "availability",
    "fresh-admission",
    "guard",
    "directory",
    "create",
    "write",
    "guard",
    "delete",
  ]);
});

test("actual native sharing preserves ordinary synchronous callers and successful cleanup ordering", async () => {
  const { events, share } = nativeBoundary(Promise.resolve(true));
  await share(new Uint8Array([1]), "fictional", () => {
    events.push("guard");
  });
  assert.deepEqual(events, [
    "availability",
    "guard",
    "directory",
    "create",
    "write",
    "guard",
    "share",
    "delete",
  ]);
});
