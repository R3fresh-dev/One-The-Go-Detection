import test from "node:test";
import assert from "node:assert/strict";
import fixture from "../testfixtures/backend-research-result.json";
import { clone, digest } from "../src/core/integrity";
import { verifyResult } from "../src/core/domain";
import type { CheckRecord } from "../src/core/types";

const check = () => clone(fixture.check) as unknown as CheckRecord;
const result = () => clone(fixture.result);
function rebind(value: any) {
  value.model_execution.manifest_sha256 = digest(
    value.model_execution.authority_manifest.model_manifest,
  );
  value.model_execution.authority_sha256 = digest(
    value.model_execution.authority_manifest,
  );
}

test("actual Python data-only engine interoperability result verifies immutable proof and named historical research endpoint", () => {
  assert.match(fixture.evidence_boundary, /not a server-admitted study/);
  const value = verifyResult(fixture.result, check());
  assert.equal(value.schema_version, "1.1.0");
  assert.equal(value.state, "research_estimate");
  assert.notEqual(value.target_at, value.evaluated_at);
  if (value.schema_version !== "1.1.0")
    throw Error("Missing versioned research evidence");
  assert.equal(value.model_execution.registry_version, "v1");
  assert.equal(
    value.model_execution.endpoint_definition,
    "Fictional engineering endpoint",
  );
  assert.equal(
    digest(value.model_execution.authority_manifest),
    value.model_execution.authority_sha256,
  );
});

test("changed immutable proof, endpoint, registry identity, classification or owner-record link is never displayed", () => {
  for (const mutate of [
    (v: any) => (v.model_execution.authority_sha256 = "1".repeat(64)),
    (v: any) => (v.model_execution.manifest_sha256 = "1".repeat(64)),
    (v: any) => (v.model_execution.capture_context_sha256 = "1".repeat(64)),
    (v: any) => (v.model_execution.evidence_manifest_sha256 = "1".repeat(64)),
    (v: any) => (v.model_execution.registry_id = "another-model"),
    (v: any) => (v.model_execution.registry_version = "v2"),
    (v: any) => (v.model_execution.model_artifact_sha256 = "1".repeat(64)),
    (v: any) => (v.model_execution.evaluation_report_sha256 = "1".repeat(64)),
    (v: any) => (v.model_execution.calibration_sha256 = "1".repeat(64)),
    (v: any) =>
      (v.model_execution.endpoint_definition = "A different endpoint"),
    (v: any) =>
      (v.model_execution.population_description = "A different population"),
    (v: any) => (v.model_execution.feature_version = "unapproved-features"),
    (v: any) => (v.model_execution.calibration_id = "another-calibration"),
    (v: any) => (v.uncertainty_policy_id = "another-policy"),
    (v: any) =>
      (v.classification =
        v.classification === "above_threshold"
          ? "below_threshold"
          : "above_threshold"),
    (v: any) => (v.operating_threshold = 0.4),
    (v: any) => (v.input_sha256 = "1".repeat(64)),
    (v: any) => (v.target_at = "2026-10-10T00:00:00Z"),
    (v: any) => (v.evaluated_at = "2026-10-01T00:00:00Z"),
    (v: any) => (v.provenance_summary = ["simulated"]),
    (v: any) => (v.model_execution.baseline_sha256 = "1".repeat(64)),
    (v: any) => (v.unrecognized_probability = 0.9),
    (v: any) => (v.reason_codes = ["UNCERTAINTY_ABSTENTION"]),
  ]) {
    const value = result();
    mutate(value);
    assert.throws(() => verifyResult(value, check()));
  }
  for (const mutate of [
    (c: any) => (c.kind = "guest_demo"),
    (c: any) => (c.frozen = false),
    (c: any) => (c.snapshot.mode = "synthetic"),
    (c: any) => (c.snapshot.study_id = null),
    (c: any) => (c.snapshot.protocol_id = null),
    (c: any) => (c.context = null),
    (c: any) => (c.manifest = null),
    (c: any) => (c.attempts[0].source = "simulated"),
    (c: any) => (c.snapshot.cardiac.source = "simulated"),
    (c: any) => (c.snapshot.saliva[0].source = "simulated"),
    (c: any) => (c.snapshot.profile.source = "synthetic"),
  ]) {
    const changed = check();
    mutate(changed);
    assert.throws(() => verifyResult(result(), changed));
  }
});

test("a verified uncertainty band requires null abstention rather than a probability or optimistic classification", () => {
  const value: any = result(),
    model = value.model_execution.authority_manifest.model_manifest;
  model.uncertainty_policy = {
    policy_id: value.uncertainty_policy_id,
    method: "probability_band",
    lower: 0,
    upper: 1,
    rationale: "Fictional engineering abstention test",
  };
  rebind(value);
  assert.throws(() => verifyResult(value, check()), /requires.*abstain/);
  value.state = "inconclusive";
  value.probability = null;
  value.classification = null;
  value.operating_threshold = null;
  value.reason_codes = ["UNCERTAINTY_ABSTENTION"];
  const accepted = verifyResult(value, check());
  assert.equal(accepted.state, "inconclusive");
  assert.equal(accepted.probability, null);
  value.classification = "below_threshold";
  assert.throws(() => verifyResult(value, check()));
});

test("personalized baseline cannot omit baseline evidence and legacy 0.1 result cannot acquire research fields", () => {
  const value: any = result();
  value.model_execution.authority_manifest.model_manifest.baseline_mode =
    "personalized";
  rebind(value);
  assert.throws(() => verifyResult(value, check()), /baseline/);
  const changed = check();
  changed.snapshot.baseline_ref = "owned-baseline";
  value.model_execution.baseline_sha256 = "1".repeat(64);
  assert.equal(verifyResult(value, changed).schema_version, "1.1.0");
  value.schema_version = "0.1.0";
  assert.throws(() => verifyResult(value, changed), /cannot display/);
});

test("manifest semantic bounds and frozen source summaries cannot be forged by rebinding their hashes", () => {
  for (const mutate of [
    (m: any) => (m.population.min_age_years = 66),
    (m: any) =>
      (m.uncertainty_policy = {
        ...m.uncertainty_policy,
        method: "probability_band",
        lower: 0.6,
        upper: 0.4,
      }),
    (m: any) =>
      (m.uncertainty_policy = {
        ...m.uncertainty_policy,
        method: "probability_band",
        lower: 0.6,
        upper: 0.9,
      }),
    (m: any) => (m.uncertainty_policy.lower = 0.2),
    (m: any) => (m.allowed_provenance = ["prototype_sensor"]),
  ]) {
    const value: any = result();
    mutate(value.model_execution.authority_manifest.model_manifest);
    rebind(value);
    assert.throws(() => verifyResult(value, check()));
  }
  const value: any = result();
  value.provenance_summary = ["prototype_sensor"];
  assert.throws(() => verifyResult(value, check()), /provenance/);
  const changed = check();
  changed.snapshot.saliva[0]!.source = "simulated";
  assert.throws(() => verifyResult(result(), changed), /provenance|Fictional/);
});
