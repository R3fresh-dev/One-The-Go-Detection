import {
  clone,
  digest,
  IntegrityError,
  requireObject,
} from "../core/integrity";
import {
  quarantineGeneration,
  verifyCheck,
  verifyResult,
} from "../core/domain";
import type {
  CheckRecord,
  IdFactory,
  JsonObject,
  QueueOperation,
  WorkspaceState,
} from "../core/types";
import { ApiClient, ApiError, parsePrivacyJob } from "./api";

export function queueCheck(
  state: WorkspaceState,
  checkId: string,
  id: IdFactory,
  now: string,
): WorkspaceState {
  const check = state.checks.find((c) => c.id === checkId);
  if (!check?.frozen)
    throw new IntegrityError(
      "SAVE_FIRST",
      "Save this check on the device before uploading.",
    );
  if (check.kind === "guest_demo")
    throw new IntegrityError(
      "GUEST_UPLOAD_FORBIDDEN",
      "Guest demo records never upload or migrate to an account.",
    );
  if (check.generation !== state.generation || check.delivery === "quarantined")
    throw new IntegrityError(
      "DATA_GENERATION_RETIRED",
      "This check belongs to a retired data generation.",
    );
  verifyCheck(check);
  const next = clone(state);
  if (check.delivery === "synced") return next;
  if (next.queue.some((q) => q.check_id === checkId && q.state !== "synced"))
    return next;
  const keys = Object.fromEntries(
    [
      "register",
      "context",
      "manifest",
      "snapshot",
      "finalize",
      "alcohol",
      ...check.attempts.map((a) => `attempt:${a.attempt_id}`),
    ].map((key) => [key, id()]),
  );
  next.queue.push({
    id: id(),
    kind: "check",
    generation: state.generation,
    check_id: checkId,
    body: {},
    state: "queued",
    keys,
    attempts: 0,
    next_attempt_at: null,
    error: null,
    created_at: now,
    phase: 0,
  });
  next.checks.find((c) => c.id === checkId)!.delivery = "queued";
  return next;
}
export function queueMutation(
  state: WorkspaceState,
  kind: QueueOperation["kind"],
  body: JsonObject,
  id: IdFactory,
  now: string,
): WorkspaceState {
  const next = clone(state);
  if (
    next.queue.some(
      (q) =>
        q.kind === kind &&
        q.state !== "synced" &&
        digest(q.body) === digest(body) &&
        (q.generation === state.generation || kind === "deletion"),
    )
  )
    return next;
  next.queue.push({
    id: id(),
    kind,
    generation: state.generation,
    check_id: null,
    body: clone(body),
    state: "queued",
    keys: { request: id() },
    attempts: 0,
    next_attempt_at: null,
    error: null,
    created_at: now,
    phase: 0,
  });
  return next;
}
export function errorDisposition(error: unknown): {
  state: QueueOperation["state"];
  message: string;
  retryAfter: number | null;
} {
  if (error instanceof ApiError) {
    const state =
      error.status === 401
        ? "auth_required"
        : error.status === 403
          ? "blocked"
          : error.status === 410
            ? "quarantined"
            : [409, 412, 428].includes(error.status)
              ? "conflict"
              : error.status === 422 ||
                  error.status === 400 ||
                  error.status === 413
                ? "blocked"
                : "retry_wait";
    return {
      state,
      message: `${error.code}: ${error.message}${error.requestId ? ` Reference ${error.requestId}.` : ""}`,
      retryAfter: error.retryAfter,
    };
  }
  return {
    state: "blocked",
    message:
      error instanceof Error
        ? error.message
        : "The operation could not be verified.",
    retryAfter: null,
  };
}
export class SyncEngine {
  private active = false;
  private idleWaiters: (() => void)[] = [];
  constructor(
    private readonly api: ApiClient,
    private readonly read: () => WorkspaceState | null,
    private readonly commit: (
      change: (s: WorkspaceState) => WorkspaceState,
    ) => Promise<void>,
    private readonly epoch: () => string,
    private readonly available: () => boolean,
    private readonly ordinaryWritesAllowed: () => boolean = () => true,
  ) {}
  get busy(): boolean {
    return this.active;
  }
  async whenIdle(): Promise<void> {
    if (!this.active) return;
    await new Promise<void>((resolve) => this.idleWaiters.push(resolve));
  }
  async run(queueId: string, manual = false): Promise<void> {
    const state = this.read(),
      queue = state?.queue.find((q) => q.id === queueId);
    if (
      this.active ||
      !state ||
      !queue ||
      !this.available() ||
      ["synced", "blocked", "conflict", "quarantined"].includes(queue.state)
    )
      return;
    const durablePrivacy =
      queue.kind === "withdrawal" || queue.kind === "deletion";
    const ready = () =>
      this.ordinaryWritesAllowed() ||
      !["check", "profile", "consent"].includes(queue.kind) ||
      queue.state === "awaiting_result";
    if (!ready()) return;
    if (
      !manual &&
      ((!state.preferences.retryQueuedAutomatically && !durablePrivacy) ||
        (queue.attempts >= 8 && !durablePrivacy) ||
        (queue.next_attempt_at &&
          Date.parse(queue.next_attempt_at) > Date.now()))
    )
      return;
    const epoch = this.epoch(),
      workspace = state.workspace;
    this.active = true;
    const guard = () => {
      const current = this.read()?.queue.find((item) => item.id === queueId);
      if (
        this.epoch() !== epoch ||
        this.read()?.workspace !== workspace ||
        !current ||
        ["synced", "blocked", "conflict", "quarantined"].includes(
          current.state,
        ) ||
        !this.available() ||
        !ready()
      )
        throw new IntegrityError(
          "WORKSPACE_CHANGED",
          "Synchronization paused because the workspace or capture state changed.",
        );
    };
    const save = async (
      change: (s: WorkspaceState, q: QueueOperation) => void,
    ) => {
      guard();
      await this.commit((current) => {
        guard();
        const next = clone(current);
        const q = next.queue.find((x) => x.id === queueId);
        if (!q)
          throw new IntegrityError(
            "QUEUE_REMOVED",
            "This queued operation was canceled.",
          );
        if (["synced", "blocked", "conflict", "quarantined"].includes(q.state))
          throw new IntegrityError(
            "QUEUE_FENCED",
            "This operation was fenced while its receipt was being saved.",
          );
        change(next, q);
        return next;
      });
    };
    try {
      if (queue.generation !== state.generation && queue.kind !== "deletion")
        throw new ApiError(
          410,
          "DATA_GENERATION_RETIRED",
          "This queued record cannot be restored into the new workspace.",
        );
      if (queue.kind !== "check") {
        await this.simple(queue, save, guard);
        return;
      }
      const check = state.checks.find((c) => c.id === queue.check_id);
      if (!check)
        throw new IntegrityError(
          "MISSING_CHECK",
          "The queued check is missing.",
        );
      verifyCheck(check);
      if (check.kind === "guest_demo")
        throw new IntegrityError(
          "GUEST_UPLOAD_FORBIDDEN",
          "Guest demo cannot upload.",
        );
      const path = `/v1/sessions/${check.id}`,
        write = { generation: queue.generation };
      const update = async (
        phase: number,
        delivery: CheckRecord["delivery"],
        values: Partial<CheckRecord> = {},
      ) =>
        save((s, q) => {
          q.phase = phase;
          q.state = delivery;
          q.error = null;
          const current = s.checks.find((c) => c.id === check.id)!;
          Object.assign(current, values, { delivery, error: null });
        });
      guard();
      if (queue.phase < 1) {
        await update(0, "registering");
        const result = await this.api.request<JsonObject>("/v1/sessions", {
          method: "POST",
          body: {
            session_id: check.id,
            mode: check.snapshot.mode,
            protocol_id: check.snapshot.protocol_id,
            study_id: check.snapshot.study_id,
            supersedes_session_id: check.snapshot.supersedes_session_id,
          },
          ...write,
          key: queue.keys.register,
        });
        await update(1, "uploading_evidence", {
          remote_revision: Number(result.value.revision),
          remote_etag: result.etag ?? `"${result.value.revision}"`,
        });
      }
      if (queue.phase < 2) {
        guard();
        await this.api.request(`${path}/context`, {
          method: "PUT",
          body: check.context,
          ...write,
          key: queue.keys.context,
          etag: '"0"',
        });
        await update(2, "uploading_evidence");
      }
      for (let i = 0; i < check.attempts.length; i++) {
        const attempt = check.attempts[i]!;
        const phase = i + 3;
        if (queue.phase < phase) {
          guard();
          await this.api.request(`${path}/attempts/${attempt.attempt_id}`, {
            method: "PUT",
            body: attempt,
            ...write,
            key: queue.keys[`attempt:${attempt.attempt_id}`],
            etag: '"0"',
          });
          await update(phase, "uploading_evidence");
        }
      }
      const offset = check.attempts.length + 3;
      if (queue.phase < offset) {
        guard();
        if (check.alcohol)
          await this.api.request(`${path}/alcohol`, {
            method: "POST",
            body: check.alcohol,
            ...write,
            key: queue.keys.alcohol,
          });
        await update(offset, "uploading_evidence");
      }
      if (queue.phase < offset + 1) {
        guard();
        await this.api.request(`${path}/evidence-manifest`, {
          method: "PUT",
          body: check.manifest,
          ...write,
          key: queue.keys.manifest,
          etag: '"0"',
        });
        await update(offset + 1, "uploading_snapshot");
      }
      if (queue.phase < offset + 2) {
        guard();
        const current = this.read()!.checks.find((c) => c.id === check.id)!;
        const result = await this.api.request<JsonObject>(`${path}/snapshot`, {
          method: "PUT",
          body: check.snapshot,
          ...write,
          key: queue.keys.snapshot,
          etag: current.remote_etag,
        });
        if (result.value.snapshot_sha256 !== check.snapshot_sha256)
          throw new IntegrityError(
            "SNAPSHOT_ACK_MISMATCH",
            "The service acknowledged a different snapshot.",
          );
        await update(offset + 2, "finalizing", {
          remote_revision: Number(result.value.revision),
          remote_etag: result.etag ?? `"${result.value.revision}"`,
        });
      }
      if (queue.phase < offset + 3) {
        guard();
        const current = this.read()!.checks.find((c) => c.id === check.id)!;
        await this.api.request(`${path}/finalize`, {
          method: "POST",
          body: {
            snapshot_sha256: check.snapshot_sha256,
            evidence_sha256: check.evidence_sha256,
          },
          ...write,
          key: queue.keys.finalize,
          etag: current.remote_etag,
        });
        await update(offset + 3, "awaiting_result");
      }
      guard();
      const response = await this.api.request<unknown>(`${path}/result`);
      if (response.status === 202) {
        await update(offset + 3, "awaiting_result");
        return;
      }
      if (response.evidenceSha256 !== check.evidence_sha256)
        throw new IntegrityError(
          "EVIDENCE_ACK_MISMATCH",
          "The service result does not bind the expected evidence.",
        );
      const result = verifyResult(response.value, check);
      await update(offset + 4, "synced", { result });
    } catch (error) {
      if (
        this.epoch() === epoch &&
        this.read()?.workspace === workspace &&
        this.available() &&
        ready()
      ) {
        const disposition = errorDisposition(error);
        await this.commit((current) => {
          if (
            this.epoch() !== epoch ||
            current.workspace !== workspace ||
            !this.available() ||
            !ready()
          )
            return current;
          let next = clone(current);
          const q = next.queue.find((q) => q.id === queueId);
          // Withdrawal/deletion may fence an operation while its HTTP reply is
          // in flight. Neither a success nor an error may revive that intent.
          if (
            !q ||
            ["synced", "blocked", "conflict", "quarantined"].includes(q.state)
          )
            return next;
          q.state = disposition.state;
          q.error = disposition.message;
          q.attempts++;
          const delay =
            disposition.retryAfter ??
            Math.min(60, 2 ** Math.min(q.attempts, 6));
          q.next_attempt_at =
            delay <= 3600
              ? new Date(Date.now() + Math.max(1, delay) * 1000).toISOString()
              : null;
          if (delay > 3600) q.attempts = Math.max(8, q.attempts);
          if (q.check_id) {
            const c = next.checks.find((c) => c.id === q.check_id);
            if (c) {
              c.delivery = q.state;
              c.error = q.error;
            }
          }
          if (disposition.state === "quarantined")
            next = quarantineGeneration(next, -1, new Date().toISOString());
          return next;
        });
      }
    } finally {
      this.active = false;
      for (const resolve of this.idleWaiters.splice(0)) resolve();
    }
  }
  private async simple(
    queue: QueueOperation,
    save: (
      change: (s: WorkspaceState, q: QueueOperation) => void,
    ) => Promise<void>,
    guard: () => void,
  ): Promise<void> {
    guard();
    const common = {
      method: "POST",
      generation: queue.generation,
      key: queue.keys.request,
    };
    if (queue.kind === "profile") {
      const response = await this.api.request<JsonObject>("/v1/me/profile", {
        ...common,
        method: "PATCH",
        body: queue.body.payload,
        etag: String(queue.body.etag),
      });
      await save((s, q) => {
        q.state = "synced";
        const r = requireObject(response.value);
        if (
          digest({
            profile: s.profile.profile,
            history: s.profile.history,
            context: s.profile.context,
          }) === digest(queue.body.payload)
        ) {
          s.profile.profile_version_id =
            typeof r.profile_version_id === "string"
              ? r.profile_version_id
              : null;
          s.profile.revision = Number(r.revision);
          s.profile.etag = response.etag ?? `"${r.revision}"`;
          s.profile.sync = "synced";
        }
      });
      return;
    }
    const path =
      queue.kind === "withdrawal"
        ? `/v1/studies/${queue.body.study_id}/withdrawals`
        : queue.kind === "consent"
          ? `/v1/studies/${queue.body.study_id}/consents`
          : queue.kind === "deletion"
            ? "/v1/privacy/deletion-requests"
            : queue.kind === "export"
              ? "/v1/privacy/exports"
              : "/v1/me/acknowledgments";
    const response = await this.api.request<unknown>(path, {
      ...common,
      body: queue.body.payload ?? queue.body,
    });
    if (queue.kind === "acknowledgment") {
      const receipt = requireObject(response.value);
      if (
        receipt.version !== queue.body.version ||
        receipt.sha256 !== queue.body.sha256
      )
        throw new IntegrityError(
          "NOTICE_ACKNOWLEDGMENT_MISMATCH",
          "The notice receipt does not match the exact acknowledged version.",
        );
    }
    if (queue.kind === "consent") {
      const receipt = requireObject(response.value);
      const payload = requireObject(queue.body.payload);
      if (
        receipt.study_id !== queue.body.study_id ||
        receipt.state !== "active" ||
        receipt.accepted !== true ||
        !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
          String(receipt.consent_record_id),
        ) ||
        typeof receipt.accepted_at !== "string" ||
        !receipt.accepted_at.endsWith("Z") ||
        !Number.isFinite(Date.parse(receipt.accepted_at)) ||
        [
          "invitation_id",
          "document_version",
          "document_sha256",
          "acknowledged_at",
        ].some((key) => receipt[key] !== payload[key])
      )
        throw new IntegrityError(
          "CONSENT_RECEIPT_MISMATCH",
          "The consent receipt does not match the exact confirmed study document and acknowledgment.",
        );
    }
    await save((s, q) => {
      q.state = "synced";
      q.error = null;
      q.next_attempt_at = null;
      if (queue.kind === "consent")
        s.studies = s.studies.map((study) =>
          study.study_id === queue.body.study_id
            ? { ...study, consent: response.value as JsonObject }
            : study,
        );
      if (
        queue.kind === "acknowledgment" &&
        s.notice?.sha256 === queue.body.sha256
      )
        s.acknowledgedNotice = String(queue.body.sha256);
      if (queue.kind === "deletion" || queue.kind === "export") {
        const job = parsePrivacyJob(response.value);
        s.jobs = [job, ...s.jobs.filter((j) => j.job_id !== job.job_id)];
        if (queue.kind === "deletion") {
          if (s.capabilities) s.capabilities.account_state = "deleting";
          for (const item of s.queue)
            if (item.id !== q.id && item.state !== "synced") {
              item.state = "quarantined";
              item.error = "DELETION_REQUESTED";
            }
        }
      }
      if (queue.kind === "withdrawal")
        s.studies = s.studies.map((study) =>
          study.study_id === queue.body.study_id
            ? {
                ...study,
                local_withdrawal_pending: false,
                consent: {
                  ...((study.consent as JsonObject) ?? {}),
                  state: "withdrawn",
                },
              }
            : study,
        );
    });
  }
  async retryDue(manual = false): Promise<void> {
    const state = this.read();
    if (!state) return;
    for (const q of state.queue) {
      if (!this.available()) return;
      await this.run(q.id, manual);
    }
  }
}
