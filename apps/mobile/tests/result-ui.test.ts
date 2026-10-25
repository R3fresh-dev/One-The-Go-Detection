import test from "node:test";
import assert from "node:assert/strict";
import { buildSync } from "esbuild";
import { resolve } from "node:path";
import fixture from "../testfixtures/backend-research-result.json";
import capsFixture from "../testfixtures/backend-capabilities.json";
import cardiacFixture from "../testfixtures/backend-cardiac-authority.json";
import { clone, digest } from "../src/core/integrity";
import { emptyWorkspace } from "../src/core/domain";
import { parseRemoteCheck } from "../src/core/remote";
const compiled = buildSync({
  entryPoints: [resolve("tests/support/result-rendering.tsx")],
  bundle: true,
  write: false,
  platform: "node",
  format: "cjs",
  resolveExtensions: [
    ".web.tsx",
    ".web.ts",
    ".web.js",
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".json",
  ],
  alias: { "react-native": resolve("e2e/fixtures/native-web-shim.js") },
  define: {
    __DEV__: "false",
    "process.env.EXPO_OS": '"web"',
    "process.env.NODE_ENV": '"test"',
    "process.env.EXPO_PUBLIC_APP_ENV": '"local"',
    "process.env.EXPO_PUBLIC_HOSTED_PREVIEW": '"false"',
  },
}).outputFiles![0]!.text;
const output = { exports: {} as any };
new Function("module", "exports", "require", compiled)(
  output,
  output.exports,
  require,
);
const render = (check: any, screen = "row", scope: any = {}) =>
  output.exports
    .renderResultUI(check, screen, scope)
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ");

test("actual saved row and History preserve historical research and invalid proof rather than frozen measurement-only copy", () => {
  const check: any = clone(fixture.check);
  for (const screen of ["row", "history"]) {
    const text = render(check, screen);
    assert.match(text, /Historical research result/);
    assert.doesNotMatch(text, /Measurements only/);
  }
  check.result.model_execution.authority_sha256 = "0".repeat(64);
  assert.match(render(check), /Result unavailable/);
  assert.doesNotMatch(render(check), /Historical research result|83\.2/);
});

test("actual Home changes research access with current identity capabilities and immediately with revocation", () => {
  const check: any = clone(fixture.check),
    capabilities: any = clone(capsFixture);
  capabilities.model_execution_supported = true;
  capabilities.inference_available = true;
  const identity = {
    accountRef: capabilities.account_ref,
    generation: capabilities.data_generation,
    state: "active",
    verifiedAt: capabilities.server_time,
    issuer: "http://fictional.local",
  };
  const scope = {
    identity,
    capabilities,
    generation: capabilities.data_generation,
  };
  assert.match(
    render(check, "home", scope),
    /Research access available · separately authorized checks only/,
  );
  capabilities.inference_available = false;
  assert.doesNotMatch(
    render(check, "home", scope),
    /Research access available/,
  );
  assert.match(render(check, "home", scope), /Historical research result/);
  assert.doesNotMatch(
    render(check, "home", { ...scope, offline: true }),
    /Research access available/,
  );
  assert.doesNotMatch(
    render(check, "home", {
      ...scope,
      identity: { ...identity, accountRef: "other-account" },
    }),
    /Research access available/,
  );
});

test("actual rows and details retain measured, invalid, inconclusive, pending and fictional boundaries", () => {
  for (const [state, summary, title] of [
    ["measurement_only", "Measurements only", "Measurements saved"],
    ["invalid", "Invalid measurements", "Check needs attention"],
    ["inconclusive", "Inconclusive measurements", "Result inconclusive"],
  ]) {
    const check: any = clone(fixture.check),
      result = check.result;
    delete result.model_execution;
    Object.assign(result, {
      schema_version: "0.1.0",
      state,
      model_id: null,
      model_lifecycle: null,
      endpoint_id: null,
      probability: null,
      classification: null,
      operating_threshold: null,
      uncertainty_policy_id: null,
      reason_codes: [],
    });
    check.delivery = "queued";
    for (const screen of ["row", "history"]) {
      const text = render(check, screen);
      assert.ok(text.includes(summary!));
      assert.match(text, /queued/);
      assert.doesNotMatch(text, /Historical research/);
    }
    const detail = render(check, "result");
    assert.ok(detail.includes(title!));
    assert.doesNotMatch(
      detail,
      /Probability of the named research endpoint|Uncertainty policy/,
    );
  }
  const pending: any = clone(fixture.check);
  pending.result = null;
  pending.delivery = "awaiting_result";
  assert.match(render(pending), /Result unavailable/);
  assert.match(render(pending), /awaiting result/);
  const guest: any = clone(fixture.check);
  guest.kind = "guest_demo";
  assert.match(render(guest), /Guest demo/);
  assert.doesNotMatch(render(guest), /Historical research/);
  assert.doesNotMatch(render(guest, "result"), /83\.2%|Uncertainty policy/);
  const legacy: any = clone(fixture.check);
  legacy.result.schema_version = "0.1.0";
  assert.match(render(legacy), /Result unavailable/);
  assert.doesNotMatch(render(legacy, "result"), /83\.2%|Uncertainty policy/);
});

test("actual welcome describes measurement defaults and separate research authority without enrollment", () => {
  const text = render(clone(fixture.check), "welcome");
  assert.match(text, /Measurement mode is the default/);
  assert.match(
    text,
    /Separately authenticated research access requires independent study and model approval/,
  );
  assert.match(text, /Sign-in and this introduction do not enroll you/);
  assert.doesNotMatch(text, /This release reports measurements only/);
});

test("actual research result renders its verified uncertainty none and supplied band while refusing corrupted policy", () => {
  const check: any = clone(fixture.check);
  const none = render(check, "result");
  assert.match(none, /Uncertainty policy uncertainty/);
  assert.match(none, /Uncertainty method None/);
  assert.match(none, /No uncertainty interval supplied/);
  assert.match(none, /Engineering fixture only/);
  const result = check.result,
    model = result.model_execution.authority_manifest.model_manifest;
  model.uncertainty_policy = {
    policy_id: result.uncertainty_policy_id,
    method: "probability_band",
    lower: 0.4,
    upper: 0.6,
    rationale: "Fictional band policy",
  };
  result.model_execution.manifest_sha256 = digest(model);
  result.model_execution.authority_sha256 = digest(
    result.model_execution.authority_manifest,
  );
  const supplied = render(check, "result");
  assert.match(supplied, /Abstention probability band 40\.0%–60\.0%/);
  assert.match(supplied, /probability limits: 0\.4–0\.6/);
  assert.match(supplied, /including its limits/);
  assert.match(supplied, /Fictional band policy/);
  result.state = "inconclusive";
  result.probability = null;
  result.classification = null;
  result.operating_threshold = null;
  result.reason_codes = ["UNCERTAINTY_ABSTENTION"];
  assert.match(render(check), /Historical research abstention/);
  const abstained = render(check, "result");
  assert.match(abstained, /Research result abstained/);
  assert.match(abstained, /Abstention probability band 40\.0%–60\.0%/);
  assert.match(abstained, /No probability or classification was produced/);
  assert.doesNotMatch(abstained, /Probability of the named research endpoint/);
  result.uncertainty_policy_id = "other-policy";
  const invalid = render(check, "result");
  assert.match(invalid, /Result unavailable/);
  assert.doesNotMatch(invalid, /83\.2%|Fictional band policy|40\.0%–60\.0%/);
});

test("actual saved-check upload issue shows bounded validation paths and redacted codes without sensitive response values", () => {
  const check: any = clone(fixture.check);
  const fields: any = {
    "snapshot.sample.collected_volume_ml": "greater_than",
    "snapshot.history.sleep_hours": "Bearer SECRET-TOKEN measured value 99.9",
  };
  for (let i = 0; i < 40; i++) fields[`snapshot.field_${i}`] = "missing";
  const queue = [
    {
      id: "fictional-validation-queue",
      kind: "check",
      check_id: check.id,
      generation: check.generation,
      state: "blocked",
      body: {},
      field_errors: fields,
    },
  ];
  const text = render(check, "result", { queue });
  assert.match(text, /Upload needs correction/);
  assert.match(text, /snapshot.sample.collected_volume_ml greater than/);
  assert.doesNotMatch(text, /SECRET|99\.9|Bearer/);
  assert.doesNotMatch(text, /Upload check|Retry requested upload/);
});

test("actual saved conflict offers a verified server comparison and linked correction while keeping upload stopped", () => {
  const remote = clone(cardiacFixture.owned_session);
  remote.revision = 7;
  const capabilities: any = clone(capsFixture);
  capabilities.account_ref = remote.snapshot.subject_ref;
  capabilities.data_generation = cardiacFixture.generation;
  const state = emptyWorkspace(
    "fictional-conflict-component",
    "2026-10-11T00:00:00Z",
  );
  state.capabilities = capabilities;
  state.generation = capabilities.data_generation;
  const check = parseRemoteCheck(remote, state);
  check.delivery = "conflict";
  const identity = {
    accountRef: capabilities.account_ref,
    generation: check.generation,
    state: "active",
  };
  check.sync_conflict = {
    account_ref: identity.accountRef,
    data_generation: check.generation,
    observed_at: "2026-10-11T15:00:00Z",
    server_record: remote,
    server_etag: '"7"',
    frozen: true,
    read_error: null,
  };
  const queue = [
    {
      id: "fictional-conflict-queue",
      kind: "check",
      check_id: check.id,
      generation: check.generation,
      state: "conflict",
      body: {},
    },
  ];
  const scope = { identity, capabilities, queue };
  const text = render(check, "result", scope);
  assert.match(text, /Upload conflict needs review/);
  assert.match(text, /Server state \/ revision completed \/ 7/);
  assert.match(text, /Inspect server and pending local evidence/);
  assert.match(text, /Review a new linked correction/);
  assert.doesNotMatch(text, /Upload check|Retry requested upload/);
  capabilities.account_ref = "foreign-account";
  const foreign = render(check, "result", scope);
  assert.match(
    foreign,
    /Server comparison is unavailable or could not be verified/,
  );
  assert.doesNotMatch(foreign, /Review a new linked correction/);
});
