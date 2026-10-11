/** Explicit support-data allowlist. Never pass an exception, record or token to a serializer. */
export interface DiagnosticInput {
  appVersion: unknown;
  buildNumber: unknown;
  platform: unknown;
  platformVersion: unknown;
  environment: unknown;
  publicServiceOrigin: unknown;
  capabilityCodes?: unknown;
  syncState?: unknown;
  errorCode?: unknown;
  supportRequestId?: unknown;
}

const CAPABILITY_CODES = new Set([
  "NO_QUALIFIED_CONFIGURATION",
  "INFERENCE_UNAVAILABLE",
  "MEASUREMENT_ONLY",
  "NOT_ENROLLED",
  "CONSENT_REQUIRED",
  "CONSENT_WITHDRAWN",
  "CONFIGURATION_UNAVAILABLE",
  "NO_APPROVED_CONFIGURATION",
  "UNSUPPORTED_HARDWARE",
  "RAW_CAPTURE_UNAVAILABLE",
  "RELEASE_DISABLED",
  "NO_VALIDATED_MODEL",
  "QUALIFICATION_REQUIRED",
]);
const SYNC_STATES = new Set([
  "local_draft",
  "local_finalized",
  "queued",
  "registering",
  "uploading_evidence",
  "uploading_snapshot",
  "finalizing",
  "awaiting_result",
  "synced",
  "retry_wait",
  "auth_required",
  "blocked",
  "conflict",
  "quarantined",
  "none",
]);
const ERROR_CATEGORIES: Readonly<Record<string, string>> = Object.freeze({
  AUTH_REQUIRED: "authentication_required",
  AUTH_EXPIRED: "authentication_required",
  TOKEN_REVOKED: "authentication_required",
  AUTH_REJECTED: "authentication_required",
  SERVICE_MAINTENANCE: "maintenance",
  MAINTENANCE: "maintenance",
  UPDATE_REQUIRED: "update_required",
  CONFIG_REQUIRED: "configuration_required",
  DATA_GENERATION_RETIRED: "generation_changed",
  GENERATION_RETIRED: "generation_changed",
  REVISION_CONFLICT: "conflict",
  IDEMPOTENCY_CONFLICT: "conflict",
  NETWORK_ERROR: "network_unavailable",
  NETWORK_UNAVAILABLE: "network_unavailable",
  DEPENDENCY_UNAVAILABLE: "service_unavailable",
  LIMIT_EXCEEDED: "capacity_limit",
  RATE_LIMITED: "capacity_limit",
  NOTICE_REQUIRED: "notice_required",
});

function version(value: unknown): string {
  return typeof value === "string" && /^\d{1,5}(?:\.\d{1,5}){0,3}$/.test(value)
    ? value
    : "unavailable";
}
function origin(value: unknown): string {
  if (typeof value !== "string" || value.length > 2048) return "unavailable";
  try {
    const parsed = new URL(value);
    return ["https:", "http:"].includes(parsed.protocol) &&
      !parsed.username &&
      !parsed.password
      ? parsed.origin
      : "unavailable";
  } catch {
    return "unavailable";
  }
}

export function createDiagnostics(input: DiagnosticInput): string {
  const codes = Array.isArray(input.capabilityCodes)
    ? input.capabilityCodes.slice(0, 64)
    : [];
  const capabilities = [
    ...new Set(
      codes.map((code) =>
        typeof code === "string" && CAPABILITY_CODES.has(code)
          ? code
          : "OTHER_CAPABILITY_CODE",
      ),
    ),
  ].sort();
  const requestId =
    typeof input.supportRequestId === "string" &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      input.supportRequestId,
    )
      ? input.supportRequestId.toLowerCase()
      : null;
  const report = {
    format: "otgd-support-1",
    app_version: version(input.appVersion),
    build_number: version(input.buildNumber),
    platform:
      typeof input.platform === "string" &&
      ["android", "ios", "web"].includes(input.platform)
        ? input.platform
        : "unknown",
    platform_version: version(input.platformVersion),
    environment:
      typeof input.environment === "string" &&
      ["local", "qa", "prod", "test"].includes(input.environment)
        ? input.environment
        : "unknown",
    public_service_origin: origin(input.publicServiceOrigin),
    inference_available: false,
    capability_codes: capabilities,
    last_sync_state:
      typeof input.syncState === "string" && SYNC_STATES.has(input.syncState)
        ? input.syncState
        : "none",
    last_error_category:
      typeof input.errorCode === "string"
        ? Object.hasOwn(ERROR_CATEGORIES, input.errorCode)
          ? ERROR_CATEGORIES[input.errorCode]
          : "other_error"
        : "none",
    support_request_id: requestId,
  };
  return JSON.stringify(report, null, 2);
}
