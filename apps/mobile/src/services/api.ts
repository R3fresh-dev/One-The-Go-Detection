import { admitOAuthMetadata, type OAuthPolicy } from "../core/oauthPolicy";
import type {
  AppConfig,
  Capabilities,
  JsonObject,
  NoticeContent,
  NoticeRef,
  PrivacyJob,
} from "../core/types";
import { fromBase64 } from "../device/protocol";
import { parseRawExportManifest } from "../core/rawExport";
import { participantProtocol } from "../core/participantAcquisition";
import type { ApprovedConfiguration } from "../core/acquisition";
import {
  digestText,
  digestBytes,
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
export interface ApiClientOptions {
  serverless?: boolean;
}
// A deadline must settle the caller even if token recovery or a platform fetch
// implementation does not honor AbortSignal. Late work never commits a reply.
export function withAbort<T>(
  signal: AbortSignal,
  operation: () => Promise<T>,
): Promise<T> {
  const reason = () =>
    signal.reason instanceof Error
      ? signal.reason
      : new ApiError(0, "REQUEST_CANCELED", "The request was canceled.", true);
  if (signal.aborted) return Promise.reject(reason());
  return new Promise<T>((resolve, reject) => {
    const abort = () => {
      signal.removeEventListener("abort", abort);
      reject(reason());
    };
    signal.addEventListener("abort", abort, { once: true });
    Promise.resolve()
      .then(() => {
        if (signal.aborted) throw reason();
        return operation();
      })
      .then(
        (value) => {
          signal.removeEventListener("abort", abort);
          if (signal.aborted) reject(reason());
          else resolve(value);
        },
        (error) => {
          signal.removeEventListener("abort", abort);
          reject(error);
        },
      );
  });
}
export class ApiClient {
  private pending = new Set<AbortController>();
  private readonly requestTimeoutMs: number;
  private readonly downloadTimeoutMs: number;
  constructor(
    readonly origin: string,
    private tokenProvider: TokenProvider,
    private readonly appVersion = "0.2.0",
    private readonly ordinaryWritesAllowed: () => SyncReadiness = () => ({
      allowed: true,
      code: "ready",
      message: "Synchronization is available.",
    }),
    private readonly networkAllowed: () => boolean = () => true,
    options: ApiClientOptions = {},
  ) {
    this.requestTimeoutMs = options.serverless === true ? 120_000 : 15_000;
    this.downloadTimeoutMs = options.serverless === true ? 180_000 : 60_000;
  }
  cancelAll(): void {
    for (const controller of this.pending)
      controller.abort(
        new ApiError(0, "REQUEST_CANCELED", "The request was canceled.", true),
      );
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
    if (!this.networkAllowed())
      throw new IntegrityError(
        "HOSTED_PREVIEW_LOCAL_ONLY",
        "This fictional preview does not connect to account services or upload data.",
      );
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
    const controller = new AbortController();
    this.pending.add(controller);
    const timeout = setTimeout(
      () =>
        controller.abort(
          new ApiError(
            0,
            "REQUEST_TIMEOUT",
            `The service did not respond within ${this.requestTimeoutMs / 1000} seconds. Your local records remain on this device.`,
            true,
          ),
        ),
      this.requestTimeoutMs,
    );
    const abort = () =>
      controller.abort(
        new ApiError(0, "REQUEST_CANCELED", "The request was canceled.", true),
      );
    options.signal?.addEventListener("abort", abort, { once: true });
    if (options.signal?.aborted) abort();
    const run = async (refresh: boolean): Promise<ApiResponse<T>> => {
      const headers: Record<string, string> = {
        Accept: "application/json",
        "X-App-Version": this.appVersion,
      };
      if (!options.public) {
        const access =
          options.token ??
          (await withAbort(controller.signal, () =>
            this.tokenProvider.accessToken(refresh),
          ));
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
      const response = await withAbort(controller.signal, () =>
        fetch(`${this.origin}${path}`, {
          method,
          headers,
          body:
            options.body === undefined
              ? undefined
              : JSON.stringify(options.body),
          signal: controller.signal,
          redirect: "error",
        }),
      );
      const raw = await withAbort(controller.signal, () => response.text());
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
    };
    try {
      return await run(false);
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
  }
  async putArtifact(
    ticket: unknown,
    bytes: Uint8Array,
    sha256: string,
    mediaType: string,
  ): Promise<number> {
    if (!this.networkAllowed())
      throw new IntegrityError(
        "HOSTED_PREVIEW_LOCAL_ONLY",
        "Raw upload is unavailable in the fictional preview.",
      );
    const readiness = this.ordinaryWritesAllowed();
    if (!readiness.allowed)
      throw new IntegrityError(readiness.code, readiness.message);
    const t = requireObject(ticket),
      headers = requireObject(t.required_headers);
    knownKeys(t, [
      "artifact_id",
      "method",
      "upload_url",
      "required_headers",
      "expires_in_seconds",
      "expires_at",
    ]);
    knownKeys(headers, [
      "Content-Length",
      "Content-Type",
      "x-amz-checksum-sha256",
      "If-None-Match",
      "x-amz-server-side-encryption",
      "x-amz-server-side-encryption-aws-kms-key-id",
    ]);
    let url: URL;
    try {
      url = new URL(String(t.upload_url));
    } catch {
      throw new IntegrityError(
        "RAW_TICKET_INVALID",
        "The raw upload destination is unsupported.",
      );
    }
    const host = url.hostname.replace(/^\[|\]$/g, ""),
      local =
        /^(localhost|127(?:\.\d{1,3}){3}|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|::1|[fd][cd][0-9a-f]*:.*|localstack)$/i.test(
          host,
        );
    const checksum =
      typeof headers["x-amz-checksum-sha256"] === "string"
        ? headers["x-amz-checksum-sha256"]
        : "";
    let checksumBytes: Uint8Array;
    try {
      checksumBytes = fromBase64(checksum, 32);
    } catch {
      throw new IntegrityError(
        "RAW_TICKET_INVALID",
        "The raw upload checksum is malformed.",
      );
    }
    if (
      !/^[a-f0-9]{64}$/.test(sha256) ||
      Object.values(headers).some((value) => typeof value !== "string") ||
      digestBytes(bytes) !== sha256 ||
      t.method !== "PUT" ||
      url.href.length > 8192 ||
      url.username ||
      url.password ||
      url.hash ||
      (url.protocol !== "https:" &&
        !(
          this.origin.startsWith("http:") &&
          url.protocol === "http:" &&
          local
        )) ||
      String(headers["Content-Length"]) !== String(bytes.length) ||
      headers["Content-Type"] !== mediaType ||
      headers["If-None-Match"] !== "*" ||
      !["AES256", "aws:kms"].includes(
        String(headers["x-amz-server-side-encryption"]),
      ) ||
      [...checksumBytes]
        .map((n) => n.toString(16).padStart(2, "0"))
        .join("") !== sha256 ||
      typeof t.expires_at !== "string" ||
      !Number.isFinite(Date.parse(t.expires_at)) ||
      Date.parse(t.expires_at) > Date.now() + 301_000
    )
      throw new IntegrityError(
        "RAW_TICKET_INVALID",
        "The exact raw size, checksum, encryption headers or ticket expiry differ from this recording.",
      );
    if (Date.parse(String(t.expires_at)) <= Date.now())
      throw new ApiError(
        410,
        "RAW_TICKET_EXPIRED",
        "The acknowledged ticket expired. Retry keeps unknown outcomes intact and requests a new eligible ticket.",
        true,
      );
    const controller = new AbortController();
    this.pending.add(controller);
    const timeout = setTimeout(
      () =>
        controller.abort(
          new ApiError(
            0,
            "RAW_UPLOAD_TIMEOUT",
            "Raw upload did not finish within 60 seconds. Its encrypted local copy remains available.",
            true,
          ),
        ),
      60_000,
    );
    try {
      const response = await withAbort(controller.signal, () =>
        fetch(url.href, {
          method: "PUT",
          headers: headers as Record<string, string>,
          body: bytes as unknown as BodyInit,
          signal: controller.signal,
          redirect: "error",
          credentials: "omit",
        }),
      );
      if (!response.ok && response.status !== 412)
        throw new ApiError(
          response.status,
          Date.parse(String(t.expires_at)) <= Date.now()
            ? "RAW_TICKET_EXPIRED"
            : "RAW_UPLOAD_FAILED",
          "Raw upload was not accepted. Its encrypted local copy remains available.",
          response.status >= 500 ||
            Date.parse(String(t.expires_at)) <= Date.now(),
        );
      return response.status;
    } catch (error) {
      if (error instanceof ApiError || error instanceof IntegrityError)
        throw error;
      throw new ApiError(
        0,
        "NETWORK_UNAVAILABLE",
        "The raw object store could not be reached. Its encrypted local copy remains available.",
        true,
      );
    } finally {
      clearTimeout(timeout);
      this.pending.delete(controller);
    }
  }
  async download(
    path: string,
    generation: number,
    expectedBytes?: number,
  ): Promise<Uint8Array> {
    if (!this.networkAllowed())
      throw new IntegrityError(
        "HOSTED_PREVIEW_LOCAL_ONLY",
        "Cloud downloads are unavailable in the fictional guest preview.",
      );
    if (!/^\/v1\/privacy\/jobs\/[0-9a-f-]+\/download$/i.test(path))
      throw new IntegrityError(
        "DOWNLOAD_ORIGIN",
        "The export download route is invalid.",
      );
    const controller = new AbortController();
    this.pending.add(controller);
    const timeout = setTimeout(
      () =>
        controller.abort(
          new ApiError(
            0,
            "REQUEST_TIMEOUT",
            `The export download did not complete within ${this.downloadTimeoutMs / 1000} seconds. Try again when connected.`,
            true,
          ),
        ),
      this.downloadTimeoutMs,
    );
    try {
      const token = await withAbort(controller.signal, () =>
        this.tokenProvider.accessToken(),
      );
      if (!token)
        throw new ApiError(401, "AUTH_REQUIRED", "Sign in to download.");
      const response = await withAbort(controller.signal, () =>
        fetch(`${this.origin}${path}`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "X-Data-Generation": String(generation),
            "X-App-Version": this.appVersion,
          },
          signal: controller.signal,
          redirect: "error",
        }),
      );
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
      const buffer = new Uint8Array(
        await withAbort(controller.signal, () => response.arrayBuffer()),
      );
      if (buffer.byteLength !== length)
        throw new IntegrityError(
          "DOWNLOAD_INCOMPLETE",
          "The export download is incomplete.",
        );
      return buffer;
    } catch (error) {
      if (error instanceof ApiError || error instanceof IntegrityError)
        throw error;
      throw new ApiError(
        0,
        "NETWORK_UNAVAILABLE",
        "The export could not be downloaded. Try again when connected.",
        true,
      );
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
  expected: OAuthPolicy,
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
  const auth = admitOAuthMetadata(v.auth, expected);
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
    "research_result",
  ]);
  if (
    contracts.research_result !== undefined &&
    (!Array.isArray(contracts.research_result) ||
      !contracts.research_result.length ||
      contracts.research_result.some((version) => version !== "1.1.0"))
  )
    throw new IntegrityError(
      "CONTRACT_READINESS_INVALID",
      "The advertised research result format is unsupported. Format support does not grant model authority.",
    );
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
  return { ...(v as unknown as AppConfig), auth, notice: noticeRef(v.notice) };
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
    (method === "DELETE" && /^\/v1\/device-bindings\/[^/]+$/.test(path)) ||
    /^\/v1\/studies\/[^/]+\/(withdrawals|raw-recording-revocations)$/.test(path)
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
    "model_execution_supported",
    "model_reason_codes",
    "channels",
    "studies",
    "auth_time",
  ]);
  if (
    typeof v.inference_available !== "boolean" ||
    (v.inference_available && v.model_execution_supported !== true) ||
    (v.model_execution_supported !== undefined &&
      typeof v.model_execution_supported !== "boolean") ||
    (v.model_reason_codes !== undefined &&
      (!Array.isArray(v.model_reason_codes) ||
        v.model_reason_codes.some((reason) => typeof reason !== "string"))) ||
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
    knownKeys(item, [
      "available",
      "reason_codes",
      "authorization_available",
      "software_available",
      "configurations",
      "configuration_id",
      "configuration_sha256",
    ]);
    if (item.configurations !== undefined) {
      if (
        !Array.isArray(item.configurations) ||
        item.configurations.length > 64
      )
        throw new IntegrityError(
          "CAPABILITY_UNSUPPORTED",
          "Capture configurations exceed their bounded scope.",
        );
      for (const value of item.configurations) {
        const config = requireObject(value);
        knownKeys(config, [
          "study_id",
          "protocol_id",
          "configuration_id",
          "configuration_hash",
          "configuration_version",
          "submitted_sha256",
          "expires_at",
          "supported_phone_models",
          "supported_os_versions",
          "supported_native_builds",
          "software_adapter_id",
          "participant_protocol",
          "participant_protocol_sha256",
        ]);
        for (const key of [
          "study_id",
          "protocol_id",
          "configuration_id",
          "configuration_version",
          "software_adapter_id",
        ])
          requiredString(config[key]);
        for (const key of ["configuration_hash", "submitted_sha256"])
          if (!/^[a-f0-9]{64}$/.test(String(config[key])))
            throw new IntegrityError(
              "CAPABILITY_UNSUPPORTED",
              "An approved capture digest is invalid.",
            );
        if (
          config.participant_protocol !== undefined &&
          config.participant_protocol !== null
        )
          participantProtocol(config as unknown as ApprovedConfiguration);
        else if (
          config.participant_protocol_sha256 !== undefined &&
          config.participant_protocol_sha256 !== null
        )
          throw new IntegrityError(
            "CAPABILITY_UNSUPPORTED",
            "An instruction digest requires its exact approved protocol.",
          );
        for (const list of [
          "supported_phone_models",
          "supported_os_versions",
          "supported_native_builds",
        ]) {
          if (
            config[list] !== undefined &&
            (!Array.isArray(config[list]) ||
              config[list].length > 128 ||
              config[list].some(
                (value) =>
                  typeof value !== "string" || !value || value.length > 256,
              ))
          )
            throw new IntegrityError(
              "CAPABILITY_UNSUPPORTED",
              "Approved runtime compatibility scope is invalid.",
            );
        }
        if (
          typeof config.expires_at !== "string" ||
          !config.expires_at.endsWith("Z") ||
          !Number.isFinite(Date.parse(config.expires_at)) ||
          !Array.isArray(config.supported_phone_models) ||
          config.supported_phone_models.some(
            (phone) => typeof phone !== "string",
          )
        )
          throw new IntegrityError(
            "CAPABILITY_UNSUPPORTED",
            "Approved phone scope or expiry is invalid.",
          );
      }
    }
    if (
      (item.authorization_available !== undefined &&
        typeof item.authorization_available !== "boolean") ||
      (item.software_available !== undefined &&
        typeof item.software_available !== "boolean") ||
      (item.available === true &&
        (item.software_available === false ||
          item.authorization_available === false))
    )
      throw new IntegrityError(
        "CAPABILITY_UNSUPPORTED",
        "Capture availability contradicts its software or authorization scope.",
      );
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
    "raw_export",
  ]);
  // Validate calendar components as well as Date.parse: Date.parse alone
  // normalizes impossible dates such as February 30 instead of refusing them.
  const receiptDate = (value: unknown): string => {
    const text = requiredString(value, 64);
    const match =
      /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,9})?(Z|[+-](\d{2}):(\d{2}))$/.exec(
        text,
      );
    const [year, month, day, hour, minute, second] = match
      ? match.slice(1, 7).map(Number)
      : [];
    const leap =
      year !== undefined &&
      year % 4 === 0 &&
      (year % 100 !== 0 || year % 400 === 0);
    const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if (
      !match ||
      !year ||
      !month ||
      month > 12 ||
      !day ||
      day > days[month - 1]! ||
      hour! > 23 ||
      minute! > 59 ||
      second! > 59 ||
      Number(match[8] ?? 0) > 23 ||
      Number(match[9] ?? 0) > 59 ||
      !Number.isFinite(Date.parse(text))
    )
      throw new IntegrityError(
        "PRIVACY_JOB_UNSUPPORTED",
        "The privacy receipt contains an invalid timestamp.",
      );
    return text;
  };
  const state = v.state ?? v.status;
  if (
    v.schema_version !== "1.0.0" ||
    typeof v.kind !== "string" ||
    typeof state !== "string" ||
    !["export", "deletion"].includes(String(v.kind)) ||
    ![
      "pending",
      "running",
      "completed",
      "failed",
      "expired",
      "revoked",
      "partially_retained",
    ].includes(String(state)) ||
    (["expired", "revoked"].includes(String(state)) && v.kind !== "export") ||
    (state === "partially_retained" && v.kind !== "deletion")
  )
    throw new IntegrityError(
      "PRIVACY_JOB_UNSUPPORTED",
      "This privacy job state is unsupported. Refresh status or use the request reference for support.",
    );
  requiredString(v.job_id);
  if (v.raw_export !== undefined) {
    if (v.kind !== "export" || ["expired", "revoked"].includes(String(state)))
      throw new IntegrityError(
        "PRIVACY_JOB_UNSUPPORTED",
        "A deletion or unavailable export receipt cannot contain export authority.",
      );
    parseRawExportManifest(v.raw_export);
  }
  safeInteger(v.data_generation, 1);
  receiptDate(v.accepted_at);
  for (const key of [
    "started_at",
    "completed_at",
    "expires_at",
    "download_fresh_until",
    "download_metadata_expires_at",
  ])
    if (v[key] !== undefined && v[key] !== null) receiptDate(v[key]);
  requiredString(v.policy_version);
  safeInteger(v.attempt_count);
  if (v.failure_code !== undefined && v.failure_code !== null)
    requiredString(v.failure_code);
  if (typeof v.scope === "string") requiredString(v.scope);
  else {
    const scope = requireObject(v.scope);
    knownKeys(scope, ["kind", "session_ids"]);
    requiredString(scope.kind, 64);
    if (scope.session_ids !== undefined) {
      if (!Array.isArray(scope.session_ids) || scope.session_ids.length > 500)
        throw new IntegrityError(
          "PRIVACY_JOB_UNSUPPORTED",
          "The privacy receipt scope is invalid.",
        );
      scope.session_ids.forEach((id) => requiredString(id));
    }
  }
  if (
    !Array.isArray(v.retained_categories) ||
    v.retained_categories.length > 32 ||
    !Array.isArray(v.allowed_actions) ||
    v.allowed_actions.length > 16
  )
    throw new IntegrityError(
      "PRIVACY_JOB_UNSUPPORTED",
      "The privacy receipt is incomplete.",
    );
  v.allowed_actions.forEach((action) => requiredString(action, 64));
  const retainedText = (value: unknown, max = 256) => {
    const text = requiredString(value, max);
    if (!text.trim())
      throw new IntegrityError(
        "PRIVACY_JOB_UNSUPPORTED",
        "A retained category detail is empty.",
      );
    return text;
  };
  const retained_categories = v.retained_categories.map((entry) => {
    if (typeof entry === "string") return retainedText(entry);
    const category = requireObject(entry);
    knownKeys(category, ["category", "policy_basis", "reason", "expires_at"]);
    return {
      category: retainedText(category.category),
      policy_basis: retainedText(category.policy_basis),
      reason: retainedText(category.reason, 1000),
      expires_at:
        category.expires_at === null ? null : receiptDate(category.expires_at),
    };
  });
  return {
    ...(v as unknown as PrivacyJob),
    retained_categories,
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
