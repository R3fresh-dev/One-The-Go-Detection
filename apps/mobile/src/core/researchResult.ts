import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import schema from "../contracts/ResearchResult.schema.json";
import {
  assertBytes,
  digest,
  IntegrityError,
  requireObject,
} from "./integrity";
import type { CheckRecord, ResearchResult } from "./types";

const ajv = new Ajv2020({
  strict: false,
  allErrors: true,
  allowUnionTypes: true,
});
addFormats(ajv);
const validate = ajv.compile(schema);
const fail = (code: string, message: string): never => {
  throw new IntegrityError(code, message);
};

/** Verifies immutable execution evidence. Registry approval is admitted by the
 * authenticated service; this digest check alone is never clinical approval. */
export function verifyResearchResult(
  value: unknown,
  check: Pick<CheckRecord, "id" | "snapshot_sha256" | "snapshot"> &
    Partial<
      Pick<CheckRecord, "context" | "manifest" | "frozen" | "kind" | "attempts">
    >,
): ResearchResult {
  assertBytes(value, 524_288);
  if (!validate(value))
    fail(
      "INVALID_RESEARCH_RESULT",
      "The versioned research result or execution evidence is unsupported.",
    );
  const result = value as ResearchResult,
    execution = result.model_execution;
  const authority = execution.authority_manifest,
    model = requireObject(authority.model_manifest);
  if (
    !check.frozen ||
    !check.context ||
    !check.manifest ||
    check.kind !== "measurement" ||
    check.snapshot.mode !== "controlled_research" ||
    !check.snapshot.study_id ||
    !check.snapshot.protocol_id
  )
    fail(
      "RESEARCH_CAPTURE_REQUIRED",
      "Research estimates require an owned, frozen, authorized research capture.",
    );
  if (
    result.session_id !== check.id ||
    result.input_sha256 !== check.snapshot_sha256 ||
    result.target_at !== check.snapshot.target_at ||
    Date.parse(result.evaluated_at) < Date.parse(result.target_at)
  )
    fail(
      "RESULT_LINKAGE",
      "The research result differs from the frozen check or historical target time.",
    );
  const frozenSources = [
    ...new Set([
      ...check.snapshot.saliva.map((row) => row.source),
      check.snapshot.eyes.source,
      check.snapshot.cardiac.source,
      check.snapshot.task.source,
    ]),
  ].sort();
  if (digest([...result.provenance_summary].sort()) !== digest(frozenSources))
    fail(
      "RESEARCH_PROVENANCE_MISMATCH",
      "The research result provenance differs from its frozen source records.",
    );
  if (
    check.snapshot.profile.source === "synthetic" ||
    frozenSources.includes("simulated") ||
    result.provenance_summary.includes("simulated") ||
    check.attempts?.some(
      (a) => a.status === "valid" && a.source === "simulated",
    ) ||
    [
      check.snapshot.eyes,
      check.snapshot.cardiac,
      check.snapshot.task,
      ...check.snapshot.saliva,
    ].some((c) => c.status === "valid" && c.source === "simulated")
  )
    fail(
      "SIMULATED_RESEARCH_FORBIDDEN",
      "Fictional measurements cannot receive a research estimate.",
    );
  if (
    digest(check.context) !== execution.capture_context_sha256 ||
    digest(check.manifest) !== execution.evidence_manifest_sha256 ||
    digest(authority) !== execution.authority_sha256 ||
    digest(model) !== execution.manifest_sha256
  )
    fail(
      "RESEARCH_EVIDENCE_MISMATCH",
      "The research execution evidence differs from its immutable manifests.",
    );
  if (
    execution.registry_id !== result.model_id ||
    authority.model_registry_version !== execution.registry_version ||
    authority.model_artifact_sha256 !== execution.model_artifact_sha256 ||
    authority.evaluation_report_sha256 !== execution.evaluation_report_sha256 ||
    authority.calibration_sha256 !== execution.calibration_sha256
  )
    fail(
      "RESEARCH_AUTHORITY_MISMATCH",
      "The execution and admitted model authority do not agree.",
    );
  const population = requireObject(model.population),
    uncertainty = requireObject(model.uncertainty_policy);
  if (
    Number(population.min_age_years) > Number(population.max_age_years) ||
    (typeof check.snapshot.profile.age_years === "number" &&
      (check.snapshot.profile.age_years < Number(population.min_age_years) ||
        check.snapshot.profile.age_years > Number(population.max_age_years))) ||
    (uncertainty.method === "none" &&
      (uncertainty.lower !== null || uncertainty.upper !== null)) ||
    (uncertainty.method === "probability_band" &&
      (Number(uncertainty.lower) > Number(uncertainty.upper) ||
        Number(model.operating_threshold) < Number(uncertainty.lower) ||
        Number(model.operating_threshold) > Number(uncertainty.upper))) ||
    frozenSources.some(
      (source) =>
        !(model.allowed_provenance as string[]).includes(String(source)),
    )
  )
    fail(
      "RESEARCH_SCOPE_INVALID",
      "The admitted model population, source scope or uncertainty interval is inconsistent.",
    );
  if (
    model.lifecycle !== "active_research" ||
    model.model_id !== result.model_id ||
    model.artifact_sha256 !== execution.model_artifact_sha256 ||
    model.endpoint_id !== result.endpoint_id ||
    model.endpoint_definition !== execution.endpoint_definition ||
    population.description !== execution.population_description ||
    model.feature_version !== execution.feature_version ||
    model.calibration_id !== execution.calibration_id ||
    uncertainty.policy_id !== result.uncertainty_policy_id ||
    !(model.allowed_protocol_ids as string[]).includes(
      check.snapshot.protocol_id!,
    )
  )
    fail(
      "RESEARCH_MODEL_MISMATCH",
      "The displayed endpoint and model differ from the admitted model manifest.",
    );
  if (
    (model.baseline_mode === "population" &&
      execution.baseline_sha256 !== null) ||
    (model.baseline_mode === "personalized" &&
      (!execution.baseline_sha256 || !check.snapshot.baseline_ref))
  )
    fail(
      "RESEARCH_BASELINE_MISMATCH",
      "The result has inconsistent personalized baseline evidence.",
    );
  if (result.state === "research_estimate") {
    if (
      uncertainty.method === "probability_band" &&
      result.probability !== null &&
      result.probability >= Number(uncertainty.lower) &&
      result.probability <= Number(uncertainty.upper)
    )
      fail(
        "RESEARCH_UNCERTAINTY_ABSTENTION",
        "The approved probability band requires this research result to abstain.",
      );
    if (
      result.reason_codes.length !== 0 ||
      result.probability === null ||
      result.operating_threshold !== model.operating_threshold ||
      result.classification !==
        (result.probability >= result.operating_threshold!
          ? "above_threshold"
          : "below_threshold")
    )
      fail(
        "RESEARCH_CLASSIFICATION_MISMATCH",
        "The probability classification differs from the approved operating threshold.",
      );
  } else if (
    uncertainty.method !== "probability_band" ||
    digest(result.reason_codes) !== digest(["UNCERTAINTY_ABSTENTION"]) ||
    result.probability !== null ||
    result.classification !== null ||
    result.operating_threshold !== null
  )
    fail(
      "RESEARCH_ABSTENTION_INVALID",
      "An abstained research result cannot display a probability or classification.",
    );
  return result;
}
