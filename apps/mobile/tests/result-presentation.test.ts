import test from "node:test";
import assert from "node:assert/strict";
import researchFixture from "../testfixtures/backend-research-result.json";
import capabilitiesFixture from "../testfixtures/backend-capabilities.json";
import { clone, digest } from "../src/core/integrity";
import type { CheckRecord, Capabilities, Identity } from "../src/core/types";

// Every input remains fictional software evidence, never scientific admission.
const check = () => clone(researchFixture.check) as unknown as CheckRecord;
async function helpers() {
  const path = "../src/core/" + "resultPresentation";
  const module = await import(path).catch(() => null);
  assert.ok(module, "Verified result presentation must be implemented");
  return module;
}
function legacy(state: "measurement_only" | "invalid" | "inconclusive") {
  const owned = check(),
    result: any = clone(researchFixture.result);
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
  owned.result = result;
  return owned;
}
function band(probability: number | null) {
  const owned = check(),
    result: any = owned.result;
  const model = result.model_execution.authority_manifest.model_manifest;
  model.uncertainty_policy = {
    policy_id: result.uncertainty_policy_id,
    method: "probability_band",
    lower: 0.4,
    upper: 0.6,
    rationale:
      "Fictional abstention policy; no confidence interval or clinical meaning",
  };
  result.model_execution.manifest_sha256 = digest(model);
  result.model_execution.authority_sha256 = digest(
    result.model_execution.authority_manifest,
  );
  result.probability = probability;
  result.classification =
    probability === null
      ? null
      : probability >= 0.5
        ? "above_threshold"
        : "below_threshold";
  result.state = probability === null ? "inconclusive" : "research_estimate";
  result.operating_threshold = probability === null ? null : 0.5;
  result.reason_codes = probability === null ? ["UNCERTAINTY_ABSTENTION"] : [];
  return owned;
}

test("saved summaries distinguish verified measurement, invalid and inconclusive states from delivery", async () => {
  const { presentCheckResult } = await helpers();
  for (const [state, summary, title] of [
    ["measurement_only", "Measurements only", "Measurements saved"],
    ["invalid", "Invalid measurements", "Check needs attention"],
    ["inconclusive", "Inconclusive measurements", "Result inconclusive"],
  ] as const) {
    const owned = legacy(state);
    owned.delivery = "queued";
    const actual = presentCheckResult(owned);
    assert.equal(actual.summary, summary);
    assert.equal(actual.title, title);
    assert.equal(actual.result.state, state);
    assert.equal(actual.uncertainty, null);
    assert.equal(owned.delivery, "queued");
  }
});

test("verified research estimates and abstentions stay explicitly historical without granting current access", async () => {
  const { presentCheckResult } = await helpers();
  const estimate = presentCheckResult(check());
  assert.equal(estimate.summary, "Historical research result");
  assert.equal(estimate.badge, "Historical research");
  assert.equal(estimate.result.schema_version, "1.1.0");
  assert.equal(estimate.result.target_at, researchFixture.result.target_at);
  const abstained = presentCheckResult(band(null));
  assert.equal(abstained.summary, "Historical research abstention");
  assert.equal(abstained.title, "Research result abstained");
  assert.equal(abstained.result.probability, null);
});

test("absent, legacy-shaped, simulated and changed-proof research results cannot supply a score or uncertainty", async () => {
  const { presentCheckResult } = await helpers();
  for (const mutate of [
    (c: any) => {
      c.result = null;
    },
    (c: any) => {
      c.result.schema_version = "0.1.0";
    },
    (c: any) => {
      c.result.model_execution.authority_sha256 = "0".repeat(64);
    },
    (c: any) => {
      c.kind = "guest_demo";
    },
  ]) {
    const owned = check();
    mutate(owned);
    const actual = presentCheckResult(owned);
    assert.equal(actual.summary, "Result unavailable");
    assert.equal(actual.result, null);
    assert.equal(actual.uncertainty, null);
  }
});

test("current research scope requires live matching authenticated account and generation capabilities", async () => {
  const { workspaceScope } = await helpers();
  const capabilities = clone(capabilitiesFixture) as Capabilities;
  Object.assign(capabilities, {
    model_execution_supported: true,
    inference_available: true,
  });
  const identity: Identity = {
    accountRef: capabilities.account_ref,
    issuer: "http://fictional.local",
    generation: capabilities.data_generation,
    state: "active",
    verifiedAt: capabilities.server_time,
  };
  const input = {
    identity,
    capabilities,
    generation: capabilities.data_generation,
    offline: false,
    hostedPreview: false,
  };
  assert.equal(
    workspaceScope(input),
    "Research access available · separately authorized checks only",
  );
  for (const change of [
    { offline: true },
    { identity: null },
    { capabilities: null },
    { hostedPreview: true },
    { generation: input.generation + 1 },
    { identity: { ...identity, accountRef: "another-account" } },
    { identity: { ...identity, generation: identity.generation + 1 } },
    { identity: { ...identity, state: "deleting" } },
    { capabilities: { ...capabilities, account_state: "deleting" } },
    { capabilities: { ...capabilities, inference_available: false } },
    { capabilities: { ...capabilities, model_execution_supported: false } },
  ])
    assert.doesNotMatch(
      workspaceScope({ ...input, ...change }),
      /^Research access available/,
    );
  // No memoized capability survives the same object's revocation/account switch.
  capabilities.inference_available = false;
  assert.equal(
    workspaceScope(input),
    "Measurement workspace · research access unavailable",
  );
  assert.equal(
    workspaceScope({ ...input, identity: null }),
    "Measurement workspace",
  );
});

test("verified method none explicitly supplies no uncertainty interval and preserves its policy and rationale", async () => {
  const { presentCheckResult } = await helpers();
  const actual = presentCheckResult(check()).uncertainty;
  assert.equal(actual.policyId, "uncertainty");
  assert.equal(actual.method, "None");
  assert.equal(actual.band, null);
  assert.equal(
    actual.explanation,
    "No uncertainty interval supplied. This policy does not quantify uncertainty.",
  );
  assert.equal(actual.rationale, "Engineering fixture only");
});

test("supplied verified probability band shows exact abstention limits for below, above and null outcomes", async () => {
  const { presentCheckResult } = await helpers();
  for (const probability of [0.3, 0.7, null]) {
    const actual = presentCheckResult(band(probability));
    assert.equal(actual.result.probability, probability);
    assert.equal(actual.uncertainty.policyId, "uncertainty");
    assert.equal(actual.uncertainty.method, "Probability band");
    assert.equal(
      actual.uncertainty.band,
      "40.0%–60.0% (probability limits: 0.4–0.6)",
    );
    assert.equal(
      actual.uncertainty.rationale,
      "Fictional abstention policy; no confidence interval or clinical meaning",
    );
    assert.match(actual.uncertainty.explanation, /including its limits/);
    assert.match(actual.uncertainty.explanation, /not a confidence interval/);
  }
  // An inside-band numeric result violates the real verifier and is withheld.
  assert.equal(presentCheckResult(band(0.5)).result, null);
});

test("missing, malformed and mismatched uncertainty cannot become a displayed policy by local rebinding", async () => {
  const { presentCheckResult } = await helpers();
  for (const mutate of [
    (r: any) => {
      delete r.model_execution.authority_manifest.model_manifest
        .uncertainty_policy;
    },
    (r: any) => {
      r.uncertainty_policy_id = "another-policy";
    },
    (r: any) => {
      r.model_execution.authority_manifest.model_manifest.uncertainty_policy.lower = 0.2;
    },
  ]) {
    const owned = check(),
      result: any = owned.result;
    mutate(result);
    result.model_execution.manifest_sha256 = digest(
      result.model_execution.authority_manifest.model_manifest,
    );
    result.model_execution.authority_sha256 = digest(
      result.model_execution.authority_manifest,
    );
    const actual = presentCheckResult(owned);
    assert.equal(actual.result, null);
    assert.equal(actual.uncertainty, null);
  }
});

test("probability-band presentation preserves supplied exact limits beyond rounded percentages", async () => {
  const { presentCheckResult } = await helpers();
  const owned = band(0.7),
    result: any = owned.result;
  const model = result.model_execution.authority_manifest.model_manifest;
  model.uncertainty_policy.lower = 0.40001;
  model.uncertainty_policy.upper = 0.60001;
  result.model_execution.manifest_sha256 = digest(model);
  result.model_execution.authority_sha256 = digest(
    result.model_execution.authority_manifest,
  );
  assert.equal(
    presentCheckResult(owned).uncertainty.band,
    "40.0%–60.0% (probability limits: 0.40001–0.60001)",
  );
});
