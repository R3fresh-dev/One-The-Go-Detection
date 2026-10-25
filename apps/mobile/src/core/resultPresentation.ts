import { verifyResult } from "./domain";
import { requireObject } from "./integrity";
import type {
  Capabilities,
  CheckRecord,
  Identity,
  MeasurementResult,
} from "./types";

export interface ResultPresentation {
  badge: string;
  summary: string;
  title: string;
  result: MeasurementResult | null;
  uncertainty: {
    policyId: string;
    method: string;
    band: string | null;
    explanation: string;
    rationale: string | null;
  } | null;
  currentAdmissionRequired?: boolean;
}

/** Only the explicitly typed HR companion has current-read admission rules.
 * Other historical research envelopes retain their existing display behavior. */
export function requiresCurrentHrRead(
  result: MeasurementResult | null,
): boolean {
  return (
    result?.schema_version === "1.1.0" &&
    result.model_execution.authority_manifest.cardiac_authority != null
  );
}

/** Historical display verification is not current model/study admission. The
 * authenticated service remains responsible for that independent authority. */
export function presentCheckResult(
  check: CheckRecord,
  currentHrReadAdmitted = false,
): ResultPresentation {
  const unavailable: ResultPresentation = {
    badge: "Result unavailable",
    summary: "Result unavailable",
    title: "Result unavailable",
    result: null,
    uncertainty: null,
  };
  if (!check.frozen)
    return {
      ...unavailable,
      badge: "Draft",
      title: "Draft check",
      summary: `Draft · ${check.stage.replaceAll("_", " ")}`,
    };
  if (!check.result) return unavailable;
  let result: MeasurementResult;
  try {
    result = verifyResult(check.result, check);
  } catch {
    return unavailable;
  }
  if (result.schema_version === "1.1.0") {
    if (requiresCurrentHrRead(result) && !currentHrReadAdmitted)
      return {
        badge: "Historical research",
        summary:
          result.state === "research_estimate"
            ? "Historical research result"
            : "Historical research abstention",
        title: "Current research result admission required",
        result: null,
        uncertainty: null,
        currentAdmissionRequired: true,
      };
    const policy = requireObject(
      result.model_execution.authority_manifest.model_manifest
        .uncertainty_policy,
    );
    const hasBand = policy.method === "probability_band";
    return {
      badge: "Historical research",
      summary:
        result.state === "research_estimate"
          ? "Historical research result"
          : "Historical research abstention",
      title:
        result.state === "research_estimate"
          ? "Historical research result"
          : "Research result abstained",
      result,
      uncertainty: {
        policyId: result.uncertainty_policy_id,
        method: hasBand ? "Probability band" : "None",
        band: hasBand
          ? `${(Number(policy.lower) * 100).toFixed(1)}%–${(Number(policy.upper) * 100).toFixed(1)}% (probability limits: ${policy.lower}–${policy.upper})`
          : null,
        explanation: hasBand
          ? "The model abstains within this probability band, including its limits. This is not a confidence interval or a clinical safety range."
          : "No uncertainty interval supplied. This policy does not quantify uncertainty.",
        rationale:
          typeof policy.rationale === "string" ? policy.rationale : null,
      },
    };
  }
  const labels = {
    measurement_only: [
      "Measurement record",
      "Measurements only",
      "Measurements saved",
    ],
    invalid: [
      "Invalid record",
      "Invalid measurements",
      "Check needs attention",
    ],
    inconclusive: [
      "Inconclusive record",
      "Inconclusive measurements",
      "Result inconclusive",
    ],
  } as const;
  const [badge, summary, title] = labels[result.state];
  return { badge, summary, title, result, uncertainty: null };
}

/** Present only the current authenticated capability observation. Neither a
 * historical result, local role, sign-in nor contract support grants access. */
export function workspaceScope(input: {
  identity: Identity | null;
  capabilities: Capabilities | null;
  generation: number;
  offline: boolean;
  hostedPreview: boolean;
}): string {
  const { identity, capabilities, generation, offline, hostedPreview } = input;
  if (!identity || hostedPreview) return "Measurement workspace";
  if (offline) return "Offline · research access unavailable";
  if (
    identity.state === "active" &&
    capabilities?.account_state === "active" &&
    identity.accountRef === capabilities.account_ref &&
    identity.generation === generation &&
    capabilities.data_generation === generation &&
    capabilities.model_execution_supported === true &&
    capabilities.inference_available === true
  )
    return "Research access available · separately authorized checks only";
  return "Measurement workspace · research access unavailable";
}
