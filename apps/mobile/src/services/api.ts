import type {
  AppConfig,
  Capabilities,
  JsonObject,
  NoticeContent,
  NoticeRef,
  PrivacyJob,
} from "../core/types";
import {
  digestText,
  IntegrityError,
  knownKeys,
  parseBoundedJson,
  requireObject,
  requiredString,
  safeInteger,
  utf8,
} from "../core/integrity";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public retryable = false,
    public requestId: string | null = null,
    public retryAfter: number | null = null,
    public fields: Record<string, string> = {},
  ) {
    super(message);
    this.name = "ApiError";
  }
}
export interface TokenProvider {
  accessToken(force?: boolean): Promise<string | null>;
}
export interface ApiResponse<T> {
  value: T;
  etag: string | null;
  status: number;
  evidenceSha256: string | null;
}
export class ApiClient {
  private pending = new Set<AbortController>();
  constructor(
    readonly origin: string,
    private tokenProvider: TokenProvider,
    private readonly appVersion = "0.2.0",
    private readonly ordinaryWritesAllowed: () => SyncReadiness = () => ({
      allowed: true,
      code: "ready",
      message: "Synchronization is available.",
    }),
  ) {}
  cancelAll(): void {
    for (const controller of this.pending) controller.abort();
    this.pending.clear();
  }
  async request<T>(
    path: string,
    options: {
      method?: string;
      body?: unknown;
      generation?: number;
      key?: string;
      etag?: string;
      public?: boolean;
      token?: string;
      signal?: AbortSignal;
    } = {},
  ): Promise<ApiResponse<T>> {
    if (!path.startsWith("/v1/") && !path.startsWith("/health/"))
      throw new IntegrityError("INVALID_ROUTE", "Unsupported service route.");
    const method = options.method ?? "GET";
    if (isOrdinaryWrite(path, method)) {
      const readiness = this.ordinaryWritesAllowed();
      if (!readiness.allowed)
        throw new ApiError(
          readiness.code === "maintenance" ? 503 : 426,
          readiness.code.toUpperCase(),
          readiness.message,
          readiness.code === "maintenance",
        );
    }
    const run = async (refresh: boolean): Promise<ApiResponse<T>> => {
      const controller = new AbortController();
      this.pending.add(controller);
      const timeout = setTimeout(() => controller.abort(), 15_000);
      const abort = () => controller.abort();
      options.signal?.addEventListener("abort", abort, { once: true });
      try {
        const headers: Record<string, string> = {
          Accept: "application/json",
          "X-App-Version": this.appVersion,
        };
        if (!options.public) {
          const access =
            options.token ?? (await this.tokenProvider.accessToken(refresh));
          if (!access)
            throw new ApiError(401, "AUTH_REQUIRED", "Sign in to continue.");
          headers.Authorization = `Bearer ${access}`;
        }
        if (method !== "GET") {
          if (!options.key || !options.generation)
            throw new IntegrityError(
              "MUTATION_IDENTITY",
              "The request is missing its stable operation identity.",
            );
          headers["Idempotency-Key"] = options.key;
          headers["X-Data-Generation"] = String(options.generation);
          headers["Content-Type"] = "application/json";
        }
        if (options.etag) headers["If-Match"] = options.etag;
        const response = await fetch(`${this.origin}${path}`, {
          method,
          headers,
          body:
            options.body === undefined
              ? undefined
              : JSON.stringify(options.body),
          signal: controller.signal,
          redirect: "error",
        });
        const raw = await response.text();
        const value = raw
          ? parseBoundedJson(
              raw,
              method === "GET" && /^\/v1\/sessions\/[0-9a-f-]+$/i.test(path)
                ? 67_108_864
                : 1_048_576,
            )
          : null;
        if (
          response.status === 401 &&
          !refresh &&
          !options.public &&
          !options.token
        )
          return run(true);
        if (!response.ok) {
          const error =
            value && typeof value === "object"
              ? (value as Record<string, unknown>)
              : {};
          const retryHeader = response.headers.get("Retry-After"),
            retry = retryHeader === null ? NaN : Number(retryHeader);
          const fields =
            error.field_errors &&
            typeof error.field_errors === "object" &&
            !Array.isArray(error.field_errors)
              ? (error.field_errors as Record<string, string>)
              : {};
          throw new ApiError(
            response.status,
            typeof error.code === "string" ? error.code : "SERVICE_ERROR",
            typeof error.message === "string"
              ? error.message
              : "The service could not complete this request.",
            Boolean(error.retryable),
            typeof error.request_id === "string" ? error.request_id : null,
            Number.isFinite(retry) && retry >= 0 ? retry : null,
            fields,
          );
        }
        return {
          value: value as T,
          status: response.status,
          etag: response.headers.get("ETag"),
          evidenceSha256: response.headers.get("X-Evidence-Sha256"),
        };
      } catch (error) {
        if (error instanceof ApiError || error instanceof IntegrityError)
          throw error;
        throw new ApiError(
          0,
          "NETWORK_UNAVAILABLE",
          "The service could not be reached. Your local records remain on this device.",
          true,
        );
      } finally {
        clearTimeout(timeout);
        options.signal?.removeEventListener("abort", abort);
        this.pending.delete(controller);
      }
    };
    return run(false);
  }
  async download(
    path: string,
    generation: number,
    expectedBytes?: number,
  ): Promise<Uint8Array> {
    if (!/^\/v1\/privacy\/jobs\/[0-9a-f-]+\/download$/i.test(path))
      throw new IntegrityError(
        "DOWNLOAD_ORIGIN",
        "The export download route is invalid.",
      );
    const token = await this.tokenProvider.accessToken();
    if (!token)
      throw new ApiError(401, "AUTH_REQUIRED", "Sign in to download.");
    const controller = new AbortController();
    this.pending.add(controller);
    const timeout = setTimeout(() => controller.abort(), 60_000);
    try {
      const response = await fetch(`${this.origin}${path}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "X-Data-Generation": String(generation),
          "X-App-Version": this.appVersion,
        },
        signal: controller.signal,
        redirect: "error",
      });
      if (!response.ok)
        throw new ApiError(
          response.status,
          "DOWNLOAD_DENIED",
          "This export is unavailable or its authorization changed. Refresh its status.",
        );
      const length = Number(response.headers.get("Content-Length"));
      if (
        !Number.isSafeInteger(length) ||
        length < 1 ||
        length > 67_108_864 ||
        (expectedBytes !== undefined && length !== expectedBytes)
      )
        throw new IntegrityError(
          "DOWNLOAD_SIZE",
          "The export length is missing or outside the permitted bound.",
        );
      const buffer = new Uint8Array(await response.arrayBuffer());
      if (buffer.byteLength !== length)
        throw new IntegrityError(
          "DOWNLOAD_INCOMPLETE",
          "The export download is incomplete.",
        );
      return buffer;
    } finally {
      clearTimeout(timeout);
      this.pending.delete(controller);
    }
  }
}
function noticeRef(value: unknown): NoticeRef {
  const n = requireObject(value);
  knownKeys(n, [
    "version",
    "sha256",
    "locale",
    "content_path",
    "mandatory",
    "acknowledged",
  ]);
  if (
    n.locale !== "en" ||
    typeof n.mandatory !== "boolean" ||
    (n.acknowledged !== undefined && typeof n.acknowledged !== "boolean") ||
    typeof n.sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(n.sha256) ||
    typeof n.content_path !== "string" ||
    !/^\/v1\/notices\/[A-Za-z0-9._-]+$/.test(n.content_path)
  )
    throw new IntegrityError(
      "NOTICE_UNSUPPORTED",
      "The service notice metadata could not be verified.",
    );
  return {
    version: requiredString(n.version),
    sha256: n.sha256,
    locale: "en",
    content_path: n.content_path,
    mandatory: n.mandatory,
    ...(typeof n.acknowledged === "boolean"
      ? { acknowledged: n.acknowledged }
      : {}),
  };
}
export function parseAppConfig(
  value: unknown,
  expected: { environment: string; issuer: string; clientId: string },
): AppConfig {
  const v = requireObject(value);
  knownKeys(v, [
    "schema_version",
    "environment",
    "inference_available",
    "notice",
    "auth",
    "limits",
    "maintenance",
    "minimum_app_version",
    "supported_app_versions",
    "contract_versions",
  ]);
  if (
    v.schema_version !== "1.0.0" ||
    v.environment !== expected.environment ||
    v.inference_available !== false
  )
    throw new IntegrityError(
      "SERVICE_CONFIG_MISMATCH",
      "This service does not match the installed measurement-only build.",
    );
  const auth = requireObject(v.auth);
  knownKeys(auth, [
    "issuer",
    "client_id",
    "authorization_endpoint",
    "token_endpoint",
    "revocation_endpoint",
    "logout_endpoint",
    "redirect_uris",
  ]);
  if (
    auth.issuer !== expected.issuer ||
    auth.client_id !== expected.clientId ||
    !Array.isArray(auth.redirect_uris) ||
    auth.redirect_uris.some((v) => typeof v !== "string")
  )
    throw new IntegrityError(
      "AUTH_CONFIG_MISMATCH",
      "The service identity differs from this build.",
    );
  for (const key of [
    "authorization_endpoint",
    "token_endpoint",
    "revocation_endpoint",
    "logout_endpoint",
  ]) {
    const endpoint = auth[key];
    if (endpoint === undefined || endpoint === null) continue;
    const url = new URL(requiredString(endpoint, 2048));
    if (
      !["http:", "https:"].includes(url.protocol) ||
      (["qa", "prod"].includes(expected.environment) &&
        url.protocol !== "https:") ||
      url.username ||
      url.password ||
      url.hash
    )
      throw new IntegrityError(
        "AUTH_ENDPOINT_INVALID",
        "An authentication endpoint is invalid.",
      );
  }
  if (
    typeof v.maintenance !== "boolean" ||
    typeof v.minimum_app_version !== "string" ||
    !/^\d+\.\d+\.\d+$/.test(v.minimum_app_version) ||
    !Array.isArray(v.supported_app_versions) ||
    !v.supported_app_versions.length ||
    v.supported_app_versions.some(
      (x) => typeof x !== "string" || !/^\d+\.\d+\.\d+$/.test(x),
    )
  )
    throw new IntegrityError(
      "SERVICE_READINESS_INVALID",
      "Service version and maintenance metadata could not be verified.",
    );
  const contracts = requireObject(v.contract_versions);
  knownKeys(contracts, [
    "application",
    "scientific",
    "capture_evidence",
    "native_task",
  ]);
  for (const family of [
    "application",
    "scientific",
    "capture_evidence",
    "native_task",
  ]) {
    const versions = contracts[family];
    if (
      !Array.isArray(versions) ||
      !versions.length ||
      versions.some((x) => typeof x !== "string" || !/^\d+\.\d+\.\d+$/.test(x))
    )
      throw new IntegrityError(
        "CONTRACT_READINESS_INVALID",
        "The service contract versions could not be verified.",
      );
  }
  const limits = requireObject(v.limits);
  knownKeys(limits, ["request_bytes", "attempt_bytes", "export_sessions"]);
  safeInteger(limits.request_bytes, 1);
  safeInteger(limits.attempt_bytes, 1);
  safeInteger(limits.export_sessions, 1);
  return { ...(v as unknown as AppConfig), notice: noticeRef(v.notice) };
}
export interface SyncReadiness {
  allowed: boolean;
  code: "config_required" | "maintenance" | "update_required" | "ready";
  message: string;
}
export function syncReadiness(
  config: AppConfig | null,
  appVersion: string,
): SyncReadiness {
  if (!config)
    return {
      allowed: false,
      code: "config_required",
      message:
        "Connect to verify service compatibility before synchronization.",
    };
  const actual = appVersion.split(".").map(Number),
    minimum = config.minimum_app_version.split(".").map(Number);
  let belowMinimum = false;
  for (let index = 0; index < 3; index++) {
    if (actual[index]! < minimum[index]!) {
      belowMinimum = true;
      break;
    }
    if (actual[index]! > minimum[index]!) break;
  }
  const known = {
    application: "1.0.0",
    scientific: "0.1.0",
    capture_evidence: "1.0.0",
    native_task: "1.0.0",
  } as const;
  if (
    !/^\d+\.\d+\.\d+$/.test(appVersion) ||
    belowMinimum ||
    !config.supported_app_versions.includes(appVersion) ||
    Object.entries(known).some(
      ([family, version]) =>
        !config.contract_versions[family as keyof typeof known].includes(
          version,
        ),
    )
  )
    return {
      allowed: false,
      code: "update_required",
      message:
        "Update required for synchronization. Local records, native practice, history and privacy controls remain available.",
    };
  if (config.maintenance)
    return {
      allowed: false,
      code: "maintenance",
      message:
        "Service maintenance: queued uploads are paused. Local records and privacy controls remain available.",
    };
  return {
    allowed: true,
    code: "ready",
    message: "Synchronization is available.",
  };
}
export function isOrdinaryWrite(path: string, method: string): boolean {
  if (method === "GET") return false;
  return !(
    path.startsWith("/v1/privacy/") ||
    path === "/v1/me/acknowledgments" ||
    path === "/v1/me/data-generation/acknowledgments" ||
    path === "/v1/auth/logout" ||
    /^\/v1\/studies\/[^/]+\/withdrawals$/.test(path)
  );
}
export function parseCapabilities(value: unknown): Capabilities {
  const v = requireObject(value);
  knownKeys(v, [
    "schema_version",
    "account_ref",
    "data_generation",
    "account_state",
    "server_time",
    "notice",
    "inference_available",
    "channels",
    "studies",
    "auth_time",
  ]);
  if (
    v.inference_available !== false ||
    !["active", "deleting", "awaiting_generation_ack", "deleted"].includes(
      String(v.account_state),
    )
  )
    throw new IntegrityError(
      "CAPABILITY_UNSUPPORTED",
      "The account capability response is unsupported.",
    );
  requiredString(v.account_ref);
  safeInteger(v.data_generation, 1);
  requiredString(v.server_time);
  const channels = requireObject(v.channels);
  for (const c of Object.values(channels)) {
    const item = requireObject(c);
    if (
      typeof item.available !== "boolean" ||
      !Array.isArray(item.reason_codes)
    )
      throw new IntegrityError(
        "CAPABILITY_UNSUPPORTED",
        "Channel availability could not be verified.",
      );
  }
  if (!Array.isArray(v.studies))
    throw new IntegrityError(
      "CAPABILITY_UNSUPPORTED",
      "Study availability could not be verified.",
    );
  return { ...(v as unknown as Capabilities), notice: noticeRef(v.notice) };
}
export function verifyNotice(
  value: unknown,
  expected: NoticeRef,
): NoticeContent {
  const v = requireObject(value);
  knownKeys(v, [
    "version",
    "locale",
    "content_type",
    "text",
    "sha256",
    "mandatory",
  ]);
  if (
    v.version !== expected.version ||
    v.sha256 !== expected.sha256 ||
    v.locale !== "en" ||
    v.content_type !== "text/plain" ||
    typeof v.text !== "string" ||
    utf8(v.text).byteLength > 65_536 ||
    digestText(v.text) !== expected.sha256 ||
    typeof v.mandatory !== "boolean"
  )
    throw new IntegrityError(
      "NOTICE_HASH_MISMATCH",
      "The notice could not be verified. New account writes are paused; history and privacy controls remain available.",
    );
  return v as unknown as NoticeContent;
}
export function parsePrivacyJob(value: unknown): PrivacyJob {
  const v = requireObject(value);
  knownKeys(v, [
    "schema_version",
    "kind",
    "job_id",
    "scope",
    "data_generation",
    "state",
    "status",
    "accepted_at",
    "started_at",
    "completed_at",
    "expires_at",
    "failure_code",
    "retained_categories",
    "policy_version",
    "attempt_count",
    "allowed_actions",
    "download_path",
    "download_fresh_until",
    "download_metadata_expires_at",
    "manifest_sha256",
    "sha256",
    "size_bytes",
    "completed_steps",
  ]);
  const state = v.state ?? v.status;
  if (
    v.schema_version !== "1.0.0" ||
    !["export", "deletion"].includes(String(v.kind)) ||
    ![
      "pending",
      "running",
      "completed",
      "failed",
      "expired",
      "partially_retained",
    ].includes(String(state)) ||
    (state === "expired" && v.kind !== "export") ||
    (state === "partially_retained" && v.kind !== "deletion")
  )
    throw new IntegrityError(
      "PRIVACY_JOB_UNSUPPORTED",
      "This privacy job state is unsupported. Refresh status or use the request reference for support.",
    );
  requiredString(v.job_id);
  safeInteger(v.data_generation, 1);
  requiredString(v.accepted_at);
  if (
    !Array.isArray(v.retained_categories) ||
    !Array.isArray(v.allowed_actions)
  )
    throw new IntegrityError(
      "PRIVACY_JOB_UNSUPPORTED",
      "The privacy receipt is incomplete.",
    );
  return {
    ...(v as unknown as PrivacyJob),
    state: state as PrivacyJob["state"],
  };
}
export const DEMO_NOTICE_TEXT =
  "One The Go is a measurement platform. This release does not determine whether you are intoxicated or safe to drive.\n\nDemo chemistry, eye, pulse, ECG and alcohol examples are fictional. A native reaction task records your actual taps as uncalibrated practice; those taps are not fictional and have not been validated to measure impairment. Camera positioning preview neither records images nor measures pupils.\n\nGuest demo records stay on this device and never upload or migrate when you sign in. Native records use encrypted local storage. The web preview keeps data only in memory. Export happens only after your explicit selection and share action. Anyone receiving an exported file may be able to read it.\n\nAge, height, weight and context are optional. They do not generate a metabolic rate, clearance time or impairment score. Profile context freezes when you select Start check.\n\nQualified sensors, research enrollment and raw recording require their own approved configuration and permissions; this release ships no approved human assay or active impairment model. Account notice acknowledgment is separate from research consent.";
export const DEMO_NOTICE: NoticeContent = {
  version: "local-demo-v1",
  locale: "en",
  content_type: "text/plain",
  text: DEMO_NOTICE_TEXT,
  sha256: digestText(DEMO_NOTICE_TEXT),
  mandatory: true,
};
