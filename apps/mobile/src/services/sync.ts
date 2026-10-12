import { digestBytes } from "../core/integrity";
import type { WorkspaceStore } from "../platform/storage.types";
import { verifyRawExportReceipt, type RawExportScope } from "../core/rawExport";
import {
  parseRawRecordingStatus,
  type RawRecordingStatus,
  type RawKind,
} from "../core/rawRecordings";
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
  rawLocalIds: string[] = [],
): WorkspaceState {
  const check = state.checks.find((c) => c.id === checkId);
  if (
    check?.labCollection &&
    ["collecting", "pending_lab"].includes(check.labCollection.state)
  )
    throw new IntegrityError(
      "LAB_ANALYSIS_PENDING",
      "Laboratory analysis must remain a draft until independently imported or explicitly ended.",
    );
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
  if (
    new Set(rawLocalIds).size !== rawLocalIds.length ||
    rawLocalIds.length > 16
  )
    throw new IntegrityError(
      "RAW_SELECTION_INVALID",
      "Select only the exact bounded raw recordings you intend to upload.",
    );
  for (const localId of rawLocalIds) {
    const raw = state.rawArtifacts?.find((raw) => raw.local_id === localId);
    if (
      !raw ||
      raw.session_id !== checkId ||
      (raw.state !== "local" &&
        raw.state !== "queued" &&
        raw.state !== "uploaded") ||
      !raw.permission.upload ||
      state.rawRecordingFences[raw.study_id]?.includes(raw.artifact_kind) ||
      Date.parse(raw.retention_due_at) <= Date.now()
    )
      throw new IntegrityError(
        "RAW_UPLOAD_UNAVAILABLE",
        "A selected recording is missing, expired, stopped or not authorized for upload.",
      );
  }
  const existing = state.queue.find(
    (q) => q.check_id === checkId && q.state !== "synced",
  );
  if (
    existing &&
    digest(existing.body.raw_local_ids ?? []) !== digest(rawLocalIds)
  )
    throw new IntegrityError(
      "RAW_SELECTION_IMMUTABLE",
      "A pending upload retains its original raw selection. Reconcile or cancel that exact upload before choosing a different scope.",
    );
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
  if (check.acquisition) {
    keys.register = check.acquisition.register_key;
    keys.context = check.acquisition.context_key;
    for (const [attemptId, ledger] of Object.entries(
      check.acquisition.attempts,
    ))
      keys[`attempt:${attemptId}`] = ledger.terminal_key;
  }
  for (const localId of rawLocalIds) {
    keys[`raw:create:${localId}`] = id();
    keys[`raw:complete:${localId}`] = id();
    keys[`raw:renew:${localId}`] = id();
    next.rawArtifacts!.find((raw) => raw.local_id === localId)!.state =
      "queued";
  }
  next.queue.push({
    id: id(),
    kind: "check",
    generation: state.generation,
    check_id: checkId,
    body: rawLocalIds.length ? { raw_local_ids: [...rawLocalIds] } : {},
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
    private readonly rawStore: () => WorkspaceStore | null = () => null,
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
      queue.kind === "withdrawal" ||
      queue.kind === "deletion" ||
      queue.kind === "raw_revocation" ||
      queue.kind === "device_unbind";
    const ready = () =>
      this.ordinaryWritesAllowed() ||
      !["check", "profile", "consent", "raw_preference"].includes(queue.kind) ||
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
      if (queue.phase < 1 && check.acquisition?.registered)
        await update(1, "uploading_evidence");
      if (queue.phase < 1 && !check.acquisition?.registered) {
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
      if (queue.phase < 2 && check.acquisition?.context_registered)
        await update(2, "uploading_evidence");
      if (queue.phase < 2 && !check.acquisition?.context_registered) {
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
          const acquisition = check.acquisition?.attempts[attempt.attempt_id];
          let startedRevision = acquisition?.remote_revision ?? 0;
          if (acquisition && startedRevision === 0) {
            const started = await this.api.request<JsonObject>(
              `${path}/attempts/${attempt.attempt_id}`,
              {
                method: "PUT",
                body: acquisition.started_body,
                ...write,
                key: acquisition.start_key,
                etag: '"0"',
              },
            );
            if (started.value.sha256 !== digest(acquisition.started_body))
              throw new IntegrityError(
                "ATTEMPT_ACK_MISMATCH",
                "The service acknowledged different arming metadata.",
              );
            startedRevision = Number(started.value.revision);
            guard();
          }
          await this.api.request(`${path}/attempts/${attempt.attempt_id}`, {
            method: "PUT",
            body: attempt,
            ...write,
            key: queue.keys[`attempt:${attempt.attempt_id}`],
            etag: `"${startedRevision}"`,
          });
          const signed = check.attestations?.[attempt.attempt_id];
          if (signed) {
            const capture = requireObject(signed),
              ledger = check.acquisition?.attempts[attempt.attempt_id];
            if (
              !ledger ||
              !attempt.attestation_refs.includes(String(capture.attestation_id))
            )
              throw new IntegrityError(
                "ATTESTATION_LINKAGE",
                "The device-signed evidence has no immutable upload request or matching attempt.",
              );
            guard();
            await this.api.request(`${path}/attestations`, {
              method: "POST",
              body: {
                attestation_id: capture.attestation_id,
                envelope: capture.envelope,
                signature: capture.signature,
                normalized_payload: capture.normalized_payload,
              },
              ...write,
              key: ledger.attestation_key,
            });
          }
          await update(phase, "uploading_evidence");
        }
      }
      for (const localId of (queue.body.raw_local_ids ?? []) as string[]) {
        guard();
        await this.uploadRaw(localId, queue, guard, save);
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
  private async uploadRaw(
    localId: string,
    queue: QueueOperation,
    guard: () => void,
    save: (
      change: (state: WorkspaceState, queue: QueueOperation) => void,
    ) => Promise<void>,
  ): Promise<void> {
    const current = () => {
      guard();
      const raw = this.read()?.rawArtifacts?.find(
        (raw) => raw.local_id === localId,
      );
      if (
        !raw ||
        !["queued", "uploaded"].includes(raw.state) ||
        raw.session_id !== queue.check_id ||
        !raw.permission.upload ||
        this.read()?.rawRecordingFences[raw.study_id]?.includes(
          raw.artifact_kind,
        ) ||
        Date.parse(raw.retention_due_at) <= Date.now()
      )
        throw new IntegrityError(
          "RAW_UPLOAD_STOPPED",
          "The selected raw recording is expired, revoked or belongs to a stopped upload.",
        );
      return raw;
    };
    let raw = current();
    if (raw.state === "uploaded") return;
    const store = this.rawStore();
    if (!store?.readRaw)
      throw new IntegrityError(
        "ENCRYPTED_RAW_STORAGE_REQUIRED",
        "Raw uploads require unlocked encrypted native storage.",
      );
    const bytes = await store.readRaw(localId);
    // Every post-read path, including an account/fence change, must wipe RAM.
    try {
      raw = current();
      if (
        !bytes ||
        bytes.length !== raw.size_bytes ||
        digestBytes(bytes) !== raw.sha256
      )
        throw new IntegrityError(
          "RAW_RECORDING_DIGEST",
          "The encrypted local recording is missing or failed its integrity check.",
        );
      const write = { generation: queue.generation, method: "POST" };
      const renewal = () =>
        requireObject(
          requireObject(
            this.read()!.queue.find((q) => q.id === queue.id)!.body
              .raw_tickets ?? {},
          )[localId] ?? {},
        );
      const acknowledge = async (ticket: unknown) => {
        const t = requireObject(ticket);
        if (
          t.artifact_id !== current().server_artifact_id ||
          typeof t.expires_at !== "string" ||
          !Number.isFinite(Date.parse(t.expires_at))
        )
          throw new IntegrityError(
            "RAW_TICKET_INVALID",
            "The ticket receipt changed its artifact identity or expiry.",
          );
        await save((_state, q) => {
          current();
          const tickets = requireObject(q.body.raw_tickets ?? {}),
            prior = requireObject(tickets[localId] ?? {});
          tickets[localId] = {
            ...prior,
            epoch: prior.epoch ?? 0,
            ticket: clone(t),
          };
          q.body.raw_tickets = tickets as JsonObject;
        });
        return t;
      };
      let ticket: unknown;
      if (raw.server_artifact_id) {
        const response = await this.api.request<JsonObject>(
          `/v1/artifact-uploads/${raw.server_artifact_id}`,
        );
        current();
        if (
          response.value.artifact_id !== raw.server_artifact_id ||
          response.value.sha256 !== raw.sha256
        )
          throw new IntegrityError(
            "RAW_ACK_MISMATCH",
            "The service artifact differs from this retained recording.",
          );
        if (response.value.state === "verified") {
          if (
            typeof response.value.version_id !== "string" ||
            !response.value.version_id ||
            response.value.version_id === "null"
          )
            throw new IntegrityError(
              "RAW_VERSION_REQUIRED",
              "A raw upload requires a verified immutable object version.",
            );
          await save((state) => {
            current();
            state.rawArtifacts!.find(
              (file) => file.local_id === localId,
            )!.state = "uploaded";
          });
          return;
        }
        if (response.value.state !== "quarantine")
          throw new IntegrityError(
            "RAW_UPLOAD_STOPPED",
            "This artifact is no longer eligible for upload.",
          );
        let pending = renewal();
        const old =
          pending.ticket == null ? null : requireObject(pending.ticket);
        if (old && Date.parse(String(old.expires_at)) > Date.now())
          ticket = old;
        else {
          // Advance only after the previous ticket was acknowledged and expired.
          // A lost renewal response keeps its original key and exact body.
          if (old) {
            const epoch = Number(pending.epoch ?? 0) + 1;
            if (!Number.isSafeInteger(epoch) || epoch > 8192)
              throw new IntegrityError(
                "RAW_RENEWAL_LIMIT",
                "This artifact exceeded its bounded ticket renewal history.",
              );
            const h = digest({
              root: queue.keys[`raw:renew:${localId}`],
              epoch,
            });
            const key = `${h.slice(0, 8)}-${h.slice(8, 12)}-4${h.slice(13, 16)}-8${h.slice(17, 20)}-${h.slice(20, 32)}`;
            await save((_state, q) => {
              current();
              const tickets = requireObject(q.body.raw_tickets ?? {});
              tickets[localId] = { epoch, key, ticket: null };
              q.body.raw_tickets = tickets as JsonObject;
            });
            pending = renewal();
          }
          const key = String(pending.key ?? queue.keys[`raw:renew:${localId}`]);
          ticket = (
            await this.api.request<unknown>(
              `/v1/artifact-uploads/${raw.server_artifact_id}/ticket`,
              { ...write, body: {}, key },
            )
          ).value;
          current();
          ticket = await acknowledge(ticket);
        }
      } else {
        ticket = (
          await this.api.request<unknown>("/v1/artifact-uploads", {
            ...write,
            key: queue.keys[`raw:create:${localId}`],
            body: {
              study_id: raw.study_id,
              session_id: raw.session_id,
              consent_record_id: raw.consent_record_id,
              retention_policy_id: raw.permission.policy_id,
              artifact_kind: raw.artifact_kind,
              sha256: raw.sha256,
              size_bytes: raw.size_bytes,
              media_type: raw.media_type,
              raw_consent_record_id: raw.permission.receipt_id,
              attempt_id: raw.attempt_id,
              capture_started_at: raw.capture_started_at,
            },
          })
        ).value;
        current();
        const artifactId = String(requireObject(ticket).artifact_id);
        if (
          !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
            artifactId,
          )
        )
          throw new IntegrityError(
            "RAW_TICKET_INVALID",
            "The upload ticket has no valid artifact identity.",
          );
        await save((state) => {
          current();
          state.rawArtifacts!.find(
            (file) => file.local_id === localId,
          )!.server_artifact_id = artifactId;
        });
        raw = current();
        ticket = await acknowledge(ticket);
      }
      if (requireObject(ticket).artifact_id !== raw.server_artifact_id)
        throw new IntegrityError(
          "RAW_ACK_MISMATCH",
          "The upload ticket changed its artifact identity.",
        );
      await this.api.putArtifact(ticket, bytes, raw.sha256, raw.media_type);
      raw = current();
      const receipt = await this.api.request<JsonObject>(
        `/v1/artifact-uploads/${raw.server_artifact_id}/complete`,
        {
          ...write,
          key: queue.keys[`raw:complete:${localId}`],
          body: {
            sha256: raw.sha256,
            size_bytes: raw.size_bytes,
            media_type: raw.media_type,
          },
        },
      );
      current();
      if (
        receipt.value.artifact_id !== raw.server_artifact_id ||
        receipt.value.state !== "verified" ||
        receipt.value.sha256 !== raw.sha256 ||
        typeof receipt.value.version_id !== "string" ||
        !receipt.value.version_id ||
        receipt.value.version_id === "null"
      )
        throw new IntegrityError(
          "RAW_ACK_MISMATCH",
          "The service has not verified this exact raw recording and immutable version.",
        );
      await save((state) => {
        current();
        state.rawArtifacts!.find((file) => file.local_id === localId)!.state =
          "uploaded";
      });
    } finally {
      bytes?.fill(0);
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
    if (queue.kind === "device_unbind") {
      const response = await this.api.request<JsonObject>(
        `/v1/device-bindings/${queue.body.binding_id}`,
        { ...common, method: "DELETE", body: {} },
      );
      if (
        response.value.binding_id !== queue.body.binding_id ||
        response.value.state !== "revoked"
      )
        throw new IntegrityError(
          "DEVICE_UNBIND_MISMATCH",
          "Remote device forget is not confirmed.",
        );
      await save((s, q) => {
        q.state = "synced";
        q.error = null;
        q.next_attempt_at = null;
        s.deviceBindings = (s.deviceBindings ?? []).map((binding) =>
          binding.binding_id === queue.body.binding_id
            ? { ...binding, state: "revoked" }
            : binding,
        );
      });
      return;
    }
    const path =
      queue.kind === "withdrawal"
        ? `/v1/studies/${queue.body.study_id}/withdrawals`
        : queue.kind === "raw_preference"
          ? `/v1/studies/${queue.body.study_id}/raw-recording-preferences`
          : queue.kind === "raw_revocation"
            ? `/v1/studies/${queue.body.study_id}/raw-recording-revocations`
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
    let rawStatus: RawRecordingStatus | null = null;
    if (queue.kind === "raw_preference" || queue.kind === "raw_revocation") {
      rawStatus = parseRawRecordingStatus(
        response.value,
        String(queue.body.study_id),
      );
      const payload = requireObject(queue.body.payload);
      if (
        queue.kind === "raw_preference" &&
        (!rawStatus.receipt_id ||
          rawStatus.consent_record_id !== payload.consent_record_id ||
          rawStatus.policy?.policy_id !== payload.policy_id ||
          rawStatus.policy?.version !== payload.policy_version ||
          rawStatus.policy?.sha256 !== payload.policy_sha256 ||
          rawStatus.policy?.raw_notice.version !== payload.raw_notice_version ||
          rawStatus.policy?.raw_notice.sha256 !== payload.raw_notice_sha256 ||
          rawStatus.preference_receipt?.acknowledged_at !==
            payload.acknowledged_at ||
          digest(rawStatus.preference_receipt?.choices) !==
            digest(payload.choices) ||
          digest(rawStatus.choices) !== digest(payload.choices))
      )
        throw new IntegrityError(
          "RAW_RECEIPT_MISMATCH",
          "The recording receipt differs from the exact choices and policy you confirmed.",
        );
      if (
        queue.kind === "raw_revocation" &&
        (!rawStatus.accepted_receipt_id ||
          (payload.artifact_kinds as string[]).some(
            (kind) =>
              rawStatus!.choices[kind as RawKind]?.record ||
              rawStatus!.choices[kind as RawKind]?.upload,
          ))
      )
        throw new IntegrityError(
          "RAW_REVOCATION_MISMATCH",
          "The service has not confirmed that the requested recording choices are off.",
        );
    }
    await save((s, q) => {
      q.state = "synced";
      q.error = null;
      q.next_attempt_at = null;
      if (rawStatus)
        s.rawRecordingStatuses[String(queue.body.study_id)] = rawStatus;
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
        if (queue.kind === "export") {
          if (queue.body.include_raw === true)
            verifyRawExportReceipt(
              job.raw_export,
              queue.body.raw_scope as RawExportScope,
            );
          else if (job.raw_export !== undefined)
            throw new IntegrityError(
              "RAW_EXPORT_SCOPE_WIDENED",
              "The service included raw export scope in a metadata-only request.",
            );
        }
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
