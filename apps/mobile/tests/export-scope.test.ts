import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import { URL } from "node:url";
import { unzipSync, zipSync } from "fflate";
import {
  canonicalJson,
  clone,
  digest,
  digestBytes,
  utf8,
} from "../src/core/integrity";
import {
  createCheck,
  emptyProfile,
  emptyWorkspace,
  freezeCheck,
  replaceCheck,
  simulatedCapture,
} from "../src/core/domain";
import { parseRemoteCheck } from "../src/core/remote";
import {
  createLocalExport,
  decodeUtf8,
  inspectExportArchive,
} from "../src/services/export";
import type { Capabilities } from "../src/core/types";

const wire = JSON.parse(
  readFileSync(
    new URL(
      "../../../services/api/tests/fixtures/report-revision-wire.json",
      import.meta.url,
    ),
    "utf8",
  ),
);
const cloudBytes = new Uint8Array(
  readFileSync(
    new URL(
      "../../../services/api/tests/fixtures/report-revision-export.zip",
      import.meta.url,
    ),
  ),
);
function local() {
  let state = emptyWorkspace("guest-demo", "2026-10-11T15:00:00.000Z"),
    check = createCheck(state, {
      now: "2026-10-11T15:00:00.000Z",
      id: randomUUID,
      kind: "guest_demo",
      contextConfirmed: true,
    });
  check = simulatedCapture(
    check,
    "saliva",
    "2026-10-11T15:00:01.000Z",
    randomUUID,
  );
  check = freezeCheck(check, "2026-10-11T15:00:04.000Z", randomUUID);
  state = replaceCheck(state, check);
  return {
    check,
    state,
    bytes: createLocalExport(
      state,
      { kind: "single", session_ids: [check.id] },
      "2026-10-11T15:00:06.000Z",
    ),
  };
}
function rezip(
  bytes: Uint8Array,
  mutate: (files: Record<string, any>) => void,
  mutateManifest?: (manifest: Record<string, any>) => void,
) {
  const files = Object.fromEntries(
    Object.entries(unzipSync(bytes)).map(([path, value]) => [
      path,
      JSON.parse(decodeUtf8(value)),
    ]),
  );
  const localLayout = Object.hasOwn(files["manifest.json"], "manifest_sha256");
  mutate(files);
  const manifest = files["manifest.json"],
    raw: Record<string, Uint8Array> = {};
  for (const [path, object] of Object.entries(files))
    if (path !== "manifest.json") raw[path] = utf8(canonicalJson(object));
  manifest.files = Object.entries(raw).map(([path, value]) => ({
    path,
    sha256: digestBytes(value),
    [localLayout ? "bytes" : "size_bytes"]: value.length,
  }));
  mutateManifest?.(manifest);
  if (manifest.manifest_sha256) {
    delete manifest.manifest_sha256;
    manifest.manifest_sha256 = digest(manifest);
  }
  raw["manifest.json"] = utf8(canonicalJson(manifest));
  return zipSync(raw);
}
test("actual backend archive verifies original embedded evidence and both separate report revision companions", () => {
  const result = inspectExportArchive(cloudBytes, {
    accountRef: wire.account_ref,
    generation: wire.data_generation,
    selection: wire.export.selection,
    manifestSha256: wire.export.manifest_sha256,
  });
  assert.equal(result.fileCount, Object.keys(wire.export.files).length);
});
test("cached local export of an actual laboratory record preserves two revisions separately and contains no transient cache", () => {
  let state = emptyWorkspace(
    "fixture",
    wire.base.created_at,
    wire.data_generation,
  );
  state.capabilities = { account_ref: wire.account_ref } as Capabilities;
  const check = parseRemoteCheck(wire.base, state);
  check.report_revision_cache = {
    list: wire.list,
    companions: wire.companions,
    observed_at: wire.list.items[1].accepted_at,
  };
  state = replaceCheck(state, check);
  const bytes = createLocalExport(
      state,
      { kind: "single", session_ids: [check.id] },
      wire.list.items[1].accepted_at,
    ),
    files = unzipSync(bytes);
  assert.equal(
    Object.keys(files).filter((path) => path.startsWith("report-revisions/"))
      .length,
    2,
  );
  assert.ok(
    !decodeUtf8(files[`checks/${check.id}.json`]!).includes(
      "report_revision_cache",
    ),
  );
  assert.ok(inspectExportArchive(bytes).fileCount > 5);
});
test("rehashed orphan contexts, manifests, attempts, alcohol and report files fail exact selected scope", () => {
  const { bytes } = local();
  for (const category of [
    "contexts",
    "manifests",
    "attempts",
    "alcohol",
    "report-revisions",
  ]) {
    const path =
      category === "report-revisions"
        ? `${category}/${randomUUID()}/${randomUUID()}.json`
        : `${category}/${randomUUID()}.json`;
    assert.throws(
      () =>
        inspectExportArchive(
          rezip(bytes, (files) => {
            files[path] = { unselected: true };
          }),
        ),
      /unselected or unbound/,
    );
  }
});
test("rehashed extra profile version and unrelated current profile are rejected in a single-check archive", () => {
  const { bytes } = local();
  assert.throws(
    () =>
      inspectExportArchive(
        rezip(bytes, (files) => {
          const extra = clone(files["profile.json"].versions[0]);
          extra.profile.age_years = 91;
          files["profile.json"].versions.push(extra);
        }),
      ),
    /profile version/,
  );
  assert.throws(
    () =>
      inspectExportArchive(
        rezip(bytes, (files) => {
          files["profile.json"].current = emptyProfile(
            "2026-10-11T00:00:00.000Z",
          );
        }),
      ),
    /selected scope/,
  );
  assert.throws(
    () =>
      inspectExportArchive(
        rezip(cloudBytes, (files) => {
          const p = emptyProfile("2026-10-11T00:00:00.000Z");
          files["profile.json"].versions.push({
            profile_version_id: randomUUID(),
            profile: p.profile,
            history: p.history,
            context: p.context,
          });
        }),
      ),
    /unrelated/,
  );
});
test("rehashed embedded foreign attempt and substituted context fail original evidence binding", () => {
  assert.throws(
    () =>
      inspectExportArchive(
        rezip(cloudBytes, (files) => {
          const check = files[`checks/${wire.session_id}.json`];
          check.attempts[0].session_id = randomUUID();
          check.manifest.attempts.find(
            (a: any) => a.attempt_id === check.attempts[0].attempt_id,
          ).sha256 = digest(check.attempts[0]);
          check.evidence_sha256 = digest(check.manifest);
        }),
      ),
    /foreign|identity|different|inconsistent/i,
  );
  const { bytes, check } = local();
  assert.throws(
    () =>
      inspectExportArchive(
        rezip(bytes, (files) => {
          files[`contexts/${check.id}.json`].session_id = randomUUID();
          files[`manifests/${check.id}.json`].context_sha256 = digest(
            files[`contexts/${check.id}.json`],
          );
          files[`checks/${check.id}.json`].evidence_sha256 = digest(
            files[`manifests/${check.id}.json`],
          );
        }),
      ),
    /context|binding/i,
  );
});
test("rehashed report path/index substitutions, missing companions and a fake owner or generation fail", () => {
  const revision = wire.companions[0],
    path = `report-revisions/${wire.session_id}/${revision.revision_id}.json`;
  assert.throws(
    () =>
      inspectExportArchive(
        rezip(cloudBytes, (files) => {
          delete files[path];
        }),
      ),
    /missing|indexed/,
  );
  assert.throws(
    () =>
      inspectExportArchive(
        rezip(cloudBytes, (files) => {
          files[
            `report-revisions/${randomUUID()}/${revision.revision_id}.json`
          ] = files[path];
        }),
      ),
    /unselected or unbound/,
  );
  assert.throws(
    () => inspectExportArchive(cloudBytes, { accountRef: randomUUID() }),
    /owner/,
  );
  assert.throws(
    () =>
      inspectExportArchive(cloudBytes, {
        generation: wire.data_generation + 1,
      }),
    /generation/,
  );
});
test("all nonmanifest structured records have the same 512 KiB bound before schema parsing", () => {
  const { bytes, check } = local();
  for (const path of [
    "profile.json",
    `checks/${check.id}.json`,
    `contexts/${check.id}.json`,
    `manifests/${check.id}.json`,
  ])
    assert.throws(
      () =>
        inspectExportArchive(
          rezip(bytes, (files) => {
            files[path].unexpected = "x".repeat(524_288);
          }),
        ),
      /limits/,
    );
});
test("unknown profile and original wrapper keys fail even with a consistent archive manifest", () => {
  const { bytes, check } = local();
  for (const path of ["profile.json", `checks/${check.id}.json`])
    assert.throws(
      () =>
        inspectExportArchive(
          rezip(bytes, (files) => {
            files[path].extra = "unbound";
          }),
        ),
      /Unsupported response field/,
    );
});

test("rehashed local manifest metadata cannot carry nested or invented unselected data", () => {
  const { bytes } = local();
  const mutations: Array<(manifest: Record<string, any>) => void> = [
    (m) => {
      m.limitations = { other_subject: { age: 91, heart_rate: 140 } };
    },
    (m) => {
      m.limitations = "A new unsupported health-data narrative";
    },
    (m) => {
      m.exclusions = [{ other_subject: { age: 91 } }];
    },
    (m) => {
      m.exclusions = ["An invented exclusion"];
    },
    (m) => {
      m.job_id = randomUUID();
    },
    (m) => {
      delete m.raw_artifacts_included;
    },
    (m) => {
      delete m.manifest_sha256;
    },
    (m) => {
      m.created_at = "2026-02-30T00:00:00.000Z";
    },
    (m) => {
      m.created_at = { hidden: "unselected" };
    },
  ];
  for (const mutate of mutations)
    assert.throws(
      () =>
        inspectExportArchive(rezip(bytes, (f) => mutate(f["manifest.json"]))),
      /manifest|Unsupported response field/,
    );
});
test("rehashed cloud manifests require exact omitted categories, real identity and UTC expiry", () => {
  const mutations: Array<(manifest: Record<string, any>) => void> = [
    (m) => {
      m.omitted_categories = ["raw_artifacts", "unselected-health-data"];
    },
    (m) => {
      m.omitted_categories = [{ raw_artifacts: { age: 91 } }];
    },
    (m) => {
      delete m.omitted_categories;
    },
    (m) => {
      m.limitations = { hidden: "unselected" };
    },
    (m) => {
      m.manifest_sha256 = "0".repeat(64);
    },
    (m) => {
      m.job_id = "not-a-uuid";
    },
    (m) => {
      m.expires_at = m.created_at;
    },
    (m) => {
      m.expires_at = "2026-02-30T00:00:00.000Z";
    },
    (m) => {
      m.created_at = "2026-01-01T25:00:00.000Z";
    },
  ];
  for (const mutate of mutations)
    assert.throws(
      () =>
        inspectExportArchive(
          rezip(cloudBytes, (f) => mutate(f["manifest.json"])),
        ),
      /manifest|Unsupported response field/,
    );
});
test("manifest file entry size fields are bound to the original local or cloud layout", () => {
  for (const [bytes, from, to] of [
    [local().bytes, "bytes", "size_bytes"],
    [cloudBytes, "size_bytes", "bytes"],
  ] as const) {
    assert.throws(
      () =>
        inspectExportArchive(
          rezip(
            bytes,
            () => {},
            (manifest) => {
              const entry = manifest.files[0];
              entry[to] = entry[from];
              delete entry[from];
            },
          ),
        ),
      /Unsupported response field/,
    );
  }
});
