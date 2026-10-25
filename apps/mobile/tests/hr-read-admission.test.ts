import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
import fixture from "../testfixtures/backend-cardiac-authority.json";
import { clone, digest } from "../src/core/integrity";
import { replaceCheck } from "../src/core/domain";
import { parseRemoteCheck } from "../src/core/remote";
import {
  createLocalExport,
  inspectExportArchive,
} from "../src/services/export";
import { customerService, deferred } from "./support/customer";
const { AppController } =
  require("../src/controller") as typeof import("../src/controller");

// Complete signed fictional API-to-worker evidence. HTTP/current-admission
// responses are controlled here; these tests do not supply real approvals.
async function cachedAccount() {
  const service = customerService(),
    previous = globalThis.fetch;
  service.caps.account_ref = fixture.snapshot.subject_ref;
  service.caps.data_generation = fixture.generation;
  globalThis.fetch = service.fetcher;
  (globalThis as any).location = { origin: "http://localhost:8082" };
  const app = new AppController();
  await app.initialize();
  await app.signIn();
  const check = parseRemoteCheck(
    clone(fixture.owned_session),
    app.getSnapshot().state!,
  );
  await (app as any).commit((state: any) => replaceCheck(state, check));
  await app.selectCheck(check.id);
  const path = `/v1/sessions/${check.id}/result`;
  const admitted = () =>
    service.result(clone(check.result), 200, {
      "X-Evidence-SHA256": check.evidence_sha256!,
    });
  service.overrides.set(path, admitted);
  return {
    app,
    check,
    service,
    path,
    admitted,
    close: async () => {
      await app.auth.clear();
      await app.dispose();
      globalThis.fetch = previous;
    },
  };
}

test("HR numeric display requires a matched owned200 per view and never persists admission or changes saved evidence", async () => {
  const { app, check, service, path, admitted, close } = await cachedAccount();
  try {
    const retained = digest(app.check);
    assert.equal(app.hasCurrentHrResultAdmission(check), false);
    await app.refreshHrResultAdmission(check.id, "fictional-view-1");
    assert.equal(app.hasCurrentHrResultAdmission(check), true);
    const request = service.calls.find((call) => call.path === path)!;
    assert.match(request.headers.get("Authorization")!, /^Bearer /);
    assert.equal(
      app.getSnapshot().hrResultAdmission!.generation,
      check.generation,
    );
    assert.equal(
      Object.hasOwn(app.getSnapshot().state!, "hrResultAdmission"),
      false,
    );
    assert.equal(digest(app.check), retained);
    app.releaseHrResultView("unrelated-cleanup");
    assert.equal(app.hasCurrentHrResultAdmission(check), true);
    app.releaseHrResultView("fictional-view-1");
    assert.equal(app.hasCurrentHrResultAdmission(check), false);

    for (const status of [403, 422]) {
      service.overrides.set(path, () =>
        service.result(
          {
            code: "APPROVED_REGISTRY_VERSION_REQUIRED",
            message: "Fictional current authority retired",
          },
          status,
        ),
      );
      await assert.rejects(
        app.refreshHrResultAdmission(check.id, `refused-${status}`),
        (error: any) =>
          error.status === status &&
          error.code === "APPROVED_REGISTRY_VERSION_REQUIRED",
      );
      assert.equal(app.hasCurrentHrResultAdmission(check), false);
      assert.equal(digest(app.check), retained);
    }
    service.overrides.set(path, admitted);
    await app.refreshHrResultAdmission(check.id, "fictional-view-2");
    assert.equal(app.hasCurrentHrResultAdmission(check), true);
    (app as any).patch({ offline: true });
    (app as any).patch({ offline: false });
    assert.equal(
      app.hasCurrentHrResultAdmission(check),
      false,
      "Online recovery cannot revive a cached grant",
    );
    await app.navigate("home");
    await app.selectCheck(check.id);
    assert.equal(
      app.hasCurrentHrResultAdmission(check),
      false,
      "Reopening needs a new read",
    );
    service.overrides.set(path, () => {
      throw new TypeError("Fictional offline transport");
    });
    await assert.rejects(
      app.refreshHrResultAdmission(check.id, "offline-reopen"),
    );
    assert.equal(app.hasCurrentHrResultAdmission(check), false);
    assert.equal(digest(app.check), retained);
  } finally {
    await close();
  }
});

test("HR display refuses non200, missing evidence acknowledgment, changed result and owner mismatch", async () => {
  const { app, check, service, path, admitted, close } = await cachedAccount();
  try {
    for (const response of [
      () => service.result(check.result, 202),
      () => service.result(check.result),
      () =>
        service.result(
          {
            ...check.result,
            result_id: "99999999-9999-4999-8999-999999999999",
          },
          200,
          { "X-Evidence-SHA256": check.evidence_sha256! },
        ),
    ]) {
      service.overrides.set(path, response);
      await assert.rejects(app.refreshHrResultAdmission(check.id, "mismatch"));
      assert.equal(app.hasCurrentHrResultAdmission(check), false);
    }
    service.overrides.set(path, admitted);
    const identity = app.getSnapshot().identity!;
    (app as any).patch({
      identity: { ...identity, accountRef: "foreign-owner" },
    });
    const before = service.calls.length;
    await assert.rejects(
      app.refreshHrResultAdmission(check.id, "wrong-owner"),
      /owned HR research result/,
    );
    assert.equal(service.calls.length, before);
    assert.equal(app.hasCurrentHrResultAdmission(check), false);
  } finally {
    await close();
  }
});

test("actual manual service refresh revokes the display first and preserves an immutable HR result on refusal or mismatch", async () => {
  const { app, check, service, path, admitted, close } = await cachedAccount();
  try {
    await app.refreshHrResultAdmission(check.id, "manual-refresh-view");
    const resultHash = digest(app.check!.result);
    service.overrides.set(`/v1/sessions/${check.id}`, () =>
      service.result(clone(fixture.owned_session)),
    );
    service.overrides.set(path, () =>
      service.result(
        { code: "APPROVED_REGISTRY_VERSION_REQUIRED", message: "Retired" },
        403,
      ),
    );
    const refresh = app.refreshCurrentCheck();
    assert.equal(app.hasCurrentHrResultAdmission(check), false);
    await assert.rejects(refresh, (error: any) => error.status === 403);
    assert.equal(digest(app.check!.result), resultHash);
    service.overrides.set(path, admitted);
    await app.refreshCurrentCheck();
    assert.equal(app.hasCurrentHrResultAdmission(app.check!), true);
    const changed = clone(fixture.owned_session);
    changed.result.result_id = "99999999-9999-4999-8999-999999999999";
    service.overrides.set(`/v1/sessions/${check.id}`, () =>
      service.result(changed),
    );
    await assert.rejects(
      app.refreshCurrentCheck(),
      (error: any) => error.code === "HR_RESULT_READ_MISMATCH",
    );
    assert.equal(app.hasCurrentHrResultAdmission(app.check!), false);
    assert.equal(digest(app.check!.result), resultHash);
  } finally {
    await close();
  }
});

test("explicit manual refresh can establish the active HR view when no previous token exists", async () => {
  const { app, check, service, close } = await cachedAccount();
  try {
    assert.equal(app.getSnapshot().hrResultAdmission, null);
    service.overrides.set(`/v1/sessions/${check.id}`, () =>
      service.result(clone(fixture.owned_session)),
    );
    await app.refreshCurrentCheck();
    assert.equal(app.hasCurrentHrResultAdmission(app.check!), true);
    assert.equal(app.getSnapshot().hrResultAdmission!.checkId, check.id);
    await app.navigate("history");
    assert.equal(app.hasCurrentHrResultAdmission(check), false);
  } finally {
    await close();
  }
});

test("same-account memory-cache reopen cannot restore an old HR view admission", async () => {
  const { app, check, close } = await cachedAccount();
  try {
    const retained = digest(check.result);
    await app.refreshHrResultAdmission(check.id, "before-background");
    assert.equal(app.hasCurrentHrResultAdmission(check), true);
    await app.background();
    assert.equal(app.getSnapshot().state, null);
    assert.equal(app.getSnapshot().hrResultAdmission, null);
    await app.foregrounded();
    await app.signIn();
    await app.selectCheck(check.id);
    assert.equal(digest(app.check!.result), retained);
    assert.equal(app.hasCurrentHrResultAdmission(app.check!), false);
    await app.refreshHrResultAdmission(check.id, "after-reopen");
    assert.equal(app.hasCurrentHrResultAdmission(app.check!), true);
  } finally {
    await close();
  }
});

test("late HR200 cannot revive a left view, offline transition, retired generation, changed account or background workspace", async () => {
  for (const boundary of [
    "release",
    "route",
    "offline",
    "generation",
    "account",
    "background",
  ]) {
    const { app, check, service, path, admitted, close } =
      await cachedAccount();
    try {
      const pending = deferred<Response>();
      service.overrides.set(path, () => pending.promise);
      const read = app.refreshHrResultAdmission(check.id, "late-view");
      const settled = read.catch((error) => error);
      await new Promise(setImmediate);
      if (boundary === "release") app.releaseHrResultView("late-view");
      if (boundary === "route") await app.navigate("home");
      if (boundary === "offline") (app as any).patch({ offline: true });
      if (boundary === "generation")
        await (app as any).commit((state: any) => ({
          ...state,
          generation: state.generation + 1,
        }));
      if (boundary === "account")
        (app as any).patch({
          identity: {
            ...app.getSnapshot().identity!,
            accountRef: "replacement-owner",
          },
        });
      if (boundary === "background") await app.background();
      pending.resolve(admitted());
      await settled;
      assert.equal(app.hasCurrentHrResultAdmission(check), false, boundary);
      assert.equal(app.getSnapshot().hrResultAdmission, null, boundary);
    } finally {
      await close();
    }
  }
});

test("an older HR200 cannot override a newer manual current-authority refusal", async () => {
  const { app, check, service, path, admitted, close } = await cachedAccount();
  try {
    const pending = deferred<Response>();
    service.overrides.set(path, () => pending.promise);
    const old = app.refreshHrResultAdmission(check.id, "same-mounted-view");
    await new Promise(setImmediate);
    service.overrides.set(path, () =>
      service.result(
        { code: "APPROVED_REGISTRY_VERSION_REQUIRED", message: "Retired" },
        403,
      ),
    );
    await assert.rejects(
      app.refreshHrResultAdmission(check.id, "same-mounted-view"),
    );
    pending.resolve(admitted());
    await old;
    assert.equal(app.hasCurrentHrResultAdmission(check), false);
  } finally {
    await close();
  }
});

test("direct local HR export refuses cached proofs and accepts only an explicit exact-result admission contract", async () => {
  const { app, check, close } = await cachedAccount();
  try {
    const state = app.getSnapshot().state!,
      selection = { kind: "single" as const, session_ids: [check.id] };
    const retained = digest(check);
    for (const admission of [
      undefined,
      new Map(),
      new Map([[check.id, "0".repeat(64)]]),
    ])
      assert.throws(
        () =>
          createLocalExport(
            state,
            selection,
            fixture.result.evaluated_at,
            admission,
          ),
        (error: any) => error.code === "HR_RESULT_ADMISSION_REQUIRED",
      );
    // Explicit serializer contract only; actual authenticated admission is
    // exercised through AppController, not inferred from this map fixture.
    const archive = createLocalExport(
      state,
      selection,
      fixture.result.evaluated_at,
      new Map([[check.id, digest(check.result)]]),
    );
    assert.ok(inspectExportArchive(archive).fileCount > 0);
    assert.equal(digest(check), retained);
  } finally {
    await close();
  }
});

test("local HR export independently reads before assembly and final release; refusal releases no archive", async () => {
  const { app, check, service, path, admitted, close } = await cachedAccount();
  const previous = (globalThis as any).document;
  let downloads = 0;
  (globalThis as any).document = {
    createElement: () => ({
      click: () => {
        downloads++;
      },
      remove() {},
    }),
    body: { appendChild() {} },
  };
  try {
    await app.refreshHrResultAdmission(check.id, "display-only");
    await app.openExport({
      source: "device",
      selection: { kind: "single", session_ids: [check.id] },
    });
    let reads = 0;
    service.overrides.set(path, () => {
      reads++;
      return reads === 2
        ? service.result(
            {
              code: "APPROVED_REGISTRY_VERSION_REQUIRED",
              message: "Retired before release",
            },
            403,
          )
        : admitted();
    });
    const retained = digest(
      app.getSnapshot().state!.checks.find((saved) => saved.id === check.id),
    );
    await assert.rejects(
      app.createExport(),
      (error: any) => error.status === 403,
    );
    assert.equal(reads, 2, "A display grant cannot replace either export read");
    assert.equal(downloads, 0);
    assert.equal(
      digest(
        app.getSnapshot().state!.checks.find((saved) => saved.id === check.id),
      ),
      retained,
    );
    service.overrides.set(path, () => {
      reads++;
      return admitted();
    });
    await app.createExport();
    assert.equal(reads, 4);
    assert.equal(downloads, 1);
  } finally {
    (globalThis as any).document = previous;
    await close();
  }
});
