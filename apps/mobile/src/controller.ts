import { Platform } from "react-native";
import { RunStopGate, TerminalEvidenceGate } from "./core/operationGuards";
import {
  captureWorkspaceScope,
  retiredWithoutReplacement,
} from "./core/workspaceScope";
import {
  mergeReplacementPage,
  parseReplacementLinks,
  verifyReplacementTarget,
} from "./core/replacements";
import {
  beginReportRefresh,
  parseReportDetail,
  parseReportList,
} from "./core/reportRevisions";
import {
  createDeviceController,
  getSyntheticSignalFailure,
  type SyntheticSignalScenario,
} from "./device";
import {
  projectSyntheticDevice,
  syntheticConfigurationDigest,
} from "./core/deviceProjection";
import {
  getReactionTaskAvailability,
  type NativeTaskResult,
  type ReactionTaskViewRef,
  type TaskCancelReason,
} from "../modules/reaction-task";
import {
  createCheck,
  emptyWorkspace,
  freezeCheck,
  interruptStartedAttempts,
  normalizeProfile,
  quarantineGeneration,
  replaceCheck,
  settleAttempt,
  selectCardiacAttempt,
  simulatedCapture,
  startAttempt,
  taskProjection,
  TASK_CONFIGURATION_ID,
  TASK_CONFIGURATION_SHA256,
  verifyCheck,
} from "./core/domain";
import {
  assertBytes,
  clone,
  digest,
  digestBytes,
  digestText,
  IntegrityError,
  requireObject,
} from "./core/integrity";
import {
  parseProfile,
  parseRemoteCheck,
  profileBody,
  sameFrozenEvidence,
} from "./core/remote";
import type {
  AppConfig,
  Capabilities,
  Channel,
  CheckRecord,
  ExportEntry,
  Identity,
  JsonObject,
  NoticeContent,
  PrivacyJob,
  ProfileEnvelope,
  Route,
  Stage,
  WorkspaceState,
} from "./core/types";
import { BUILD, validateBuild } from "./platform/config";
import { cleanupExports, shareArchive } from "./platform/sharing";
import {
  newId,
  openWorkspaceStore,
  resetLocalWorkspace,
  unlockAccount,
} from "./platform/storage";
import type { WorkspaceStore } from "./platform/storage.types";
import {
  ApiClient,
  ApiError,
  DEMO_NOTICE,
  parseAppConfig,
  parseCapabilities,
  parsePrivacyJob,
  syncReadiness,
  verifyNotice,
} from "./services/api";
import { AuthManager } from "./services/auth";
import { createLocalExport, inspectExportArchive } from "./services/export";
import { queueCheck, queueMutation, SyncEngine } from "./services/sync";
import type { SheetSpec } from "./ui/components";

export interface ActiveTask {
  runId: string;
  attemptId: string;
  checkId: string;
  seed: number;
  epoch: string;
}
export interface AppModel {
  state: WorkspaceState | null;
  config: AppConfig | null;
  identity: Identity | null;
  route: Route;
  selectedCheck: string | null;
  locked: boolean;
  loading: boolean;
  busy: boolean;
  error: string | null;
  message: string | null;
  offline: boolean;
  activeTask: ActiveTask | null;
  taskProgress: string | null;
  sheet: SheetSpec | null;
  historyRows: JsonObject[];
  historyCursor: string | null;
  profileConflict: ProfileEnvelope | null;
  pendingReplacement: string | null;
  diagnosticError: { code: string; requestId: string | null } | null;
}
const now = () => new Date().toISOString();
export class AppController {
  private model: AppModel = {
    state: null,
    config: null,
    identity: null,
    route: "welcome",
    selectedCheck: null,
    locked: false,
    loading: true,
    busy: false,
    error: null,
    message: null,
    offline: false,
    activeTask: null,
    taskProgress: null,
    sheet: null,
    historyRows: [],
    historyCursor: null,
    profileConflict: null,
    pendingReplacement: null,
    diagnosticError: null,
  };
  private listeners = new Set<() => void>();
  private store: WorkspaceStore | null = null;
  private writes: Promise<void> = Promise.resolve();
  private workspaceEpoch = newId();
  private readonly terminalEvidence = new TerminalEvidenceGate();
  private readonly stopRequests = new RunStopGate();
  private transitions: Promise<void> = Promise.resolve();
  private authFlow = 0;
  private scopeFence = 0;
  private replacementRequest = 0;
  private reportRequest = 0;
  private nativeMountedRun: string | null = null;
  private nativeReference: ReactionTaskViewRef | null = null;
  private acquiring = false;
  private captureIntent = 0;
  private pendingCapture: Promise<void> | null = null;
  private foreground = true;
  private authenticating = false;
  private resultPolls = new Map<string, number>();
  private disposed = false;
  get nativeView(): ReactionTaskViewRef | null {
    return this.nativeReference;
  }
  set nativeView(value: ReactionTaskViewRef | null) {
    this.nativeReference = value;
    if (value && this.model.activeTask)
      this.nativeMountedRun = this.model.activeTask.runId;
  }
  readonly auth = new AuthManager(() => {
    void this.authenticationRequired().catch((error) => this.report(error));
  });
  readonly device = createDeviceController({ idFactory: newId });
  readonly api = new ApiClient(BUILD.apiUrl, this.auth, BUILD.version, () =>
    syncReadiness(this.model.config, BUILD.version),
  );
  readonly sync = new SyncEngine(
    this.api,
    () => this.model.state,
    (fn) => this.commit(fn),
    () => this.workspaceEpoch,
    () =>
      this.foreground &&
      !this.acquiring &&
      !this.model.locked &&
      !!this.model.identity,
    () => syncReadiness(this.model.config, BUILD.version).allowed,
  );
  getSnapshot = (): AppModel => this.model;
  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };
  get epoch(): string {
    return this.workspaceEpoch;
  }
  get check(): CheckRecord | null {
    return (
      this.model.state?.checks.find(
        (c) =>
          c.id === this.model.selectedCheck &&
          c.generation === this.model.state!.generation &&
          c.delivery !== "quarantined",
      ) ?? null
    );
  }
  private patch(values: Partial<AppModel>): void {
    if (this.disposed) return;
    this.model = { ...this.model, ...values };
    this.listeners.forEach((fn) => fn());
  }
  async run(action: () => Promise<void>): Promise<void> {
    if (this.model.busy) return;
    this.patch({ busy: true, error: null, message: null });
    try {
      await action();
    } catch (error) {
      if (
        !(error instanceof IntegrityError || error instanceof ApiError) ||
        !["WORKSPACE_CHANGED", "AUTH_CHANGED"].includes(error.code)
      )
        this.report(error);
    } finally {
      this.patch({ busy: false });
    }
  }
  report(error: unknown): void {
    this.patch({
      diagnosticError:
        error instanceof ApiError
          ? { code: error.code, requestId: error.requestId }
          : null,
      error:
        error instanceof Error
          ? error.message
          : "The action could not be completed. Your saved records are preserved.",
      ...(error instanceof ApiError && error.status === 0
        ? { offline: true }
        : {}),
    });
  }
  dismissError(): void {
    this.patch({ error: null, message: null });
  }
  async initialize(): Promise<void> {
    try {
      validateBuild();
      await cleanupExports();
      const identity = await this.auth.restore();
      if (identity)
        this.patch({ identity, locked: true, loading: false, route: "home" });
      else {
        await this.openGuest();
        this.patch({ loading: false });
      }
      void this.refreshConfig().catch((e) => {
        this.patch({ offline: true });
        if (this.model.identity) this.report(e);
      });
    } catch (error) {
      this.patch({ loading: false });
      this.report(error);
    }
  }
  private async activate(
    workspace: string,
    generation: number,
    isCurrent: () => boolean = () => true,
  ): Promise<void> {
    const operation = this.transitions
      .catch(() => {})
      .then(async () => {
        const guard = () => {
          if (!isCurrent() || this.disposed)
            throw new IntegrityError(
              "AUTH_CHANGED",
              "The workspace transition was canceled.",
            );
        };
        guard();
        await this.device.cancelCapture("WORKSPACE_CHANGED");
        guard();
        await this.device.forget();
        guard();
        const epoch = newId();
        this.workspaceEpoch = epoch;
        this.api.cancelAll();
        const current = () => {
          guard();
          if (epoch !== this.workspaceEpoch)
            throw new IntegrityError(
              "WORKSPACE_CHANGED",
              "The active workspace changed.",
            );
        };
        await this.writes.catch(() => {});
        current();
        const prior = this.store;
        this.store = null;
        if (prior) await prior.close();
        current();
        const opened = await openWorkspaceStore(workspace);
        try {
          current();
          let state =
            (await opened.load()) ??
            emptyWorkspace(workspace, now(), generation);
          current();
          state = clone(state);
          state.historyIndex ??= [];
          state.historyCursor ??= null;
          state.checks = state.checks.map((c) =>
            c.frozen ? c : interruptStartedAttempts(c, now()),
          );
          await opened.save(state);
          current();
          this.store = opened;
          this.patch({
            state,
            locked: false,
            selectedCheck: null,
            historyRows: state.historyIndex,
            historyCursor: state.historyCursor,
            pendingReplacement: null,
            diagnosticError: null,
          });
        } catch (error) {
          await opened.close();
          throw error;
        }
      });
    this.transitions = operation;
    await operation;
  }
  private async openGuest(): Promise<void> {
    const flow = this.authFlow;
    await this.activate(
      `guest:${BUILD.environment}`,
      1,
      () => flow === this.authFlow,
    );
    if (flow !== this.authFlow) return;
    this.patch({
      identity: null,
      route:
        this.model.state?.acknowledgedNotice === DEMO_NOTICE.sha256
          ? "home"
          : "welcome",
    });
  }
  async enterDemo(): Promise<void> {
    if (this.model.identity) await this.signOut(false);
    if (!this.model.state) await this.openGuest();
    await this.commit((s) => ({ ...s, notice: DEMO_NOTICE }));
    this.patch({
      route:
        this.model.state!.acknowledgedNotice === DEMO_NOTICE.sha256
          ? "home"
          : "notice",
    });
  }
  async unlock(): Promise<void> {
    const identity = this.model.identity;
    if (!identity) return;
    if (!this.auth.identity) {
      await this.signIn(true);
      return;
    }
    const flow = this.authFlow,
      epoch = this.workspaceEpoch,
      authGeneration = this.auth.generation;
    if (!(await unlockAccount())) {
      this.patch({ message: "Records remain locked." });
      return;
    }
    if (
      flow !== this.authFlow ||
      epoch !== this.workspaceEpoch ||
      authGeneration !== this.auth.generation
    )
      return;
    await this.activate(
      this.accountWorkspace(identity),
      identity.generation,
      () => flow === this.authFlow && authGeneration === this.auth.generation,
    );
    if (flow !== this.authFlow || authGeneration !== this.auth.generation)
      return;
    this.patch({ route: "home" });
    try {
      await this.refreshCapabilities();
      await this.refreshProfile();
    } catch (error) {
      if (
        error instanceof ApiError &&
        (error.status === 0 || error.status === 401)
      )
        this.patch({
          offline: true,
          message:
            "Showing this account’s cached records. Reconnect or sign in again to synchronize.",
        });
      else throw error;
    }
  }
  private accountWorkspace(identity: Identity): string {
    return `${BUILD.environment}:${digestText(`${identity.issuer}:${identity.accountRef}`)}`;
  }
  async resetStore(): Promise<void> {
    ++this.authFlow;
    this.authenticating = false;
    await this.stopActive("WORKSPACE_CHANGED");
    this.workspaceEpoch = newId();
    this.api.cancelAll();
    const name = this.model.identity
      ? this.accountWorkspace(this.model.identity)
      : `guest:${BUILD.environment}`;
    await this.writes.catch(() => {});
    if (this.store) {
      await this.store.close();
      this.store = null;
    }
    await resetLocalWorkspace(name);
    if (this.model.identity) this.patch({ state: null, locked: true });
    else await this.openGuest();
    this.patch({
      error: null,
      message: "Only this workspace’s local records were removed.",
    });
  }
  async commit(
    change: (state: WorkspaceState) => WorkspaceState,
  ): Promise<void> {
    const epoch = this.workspaceEpoch,
      scope = this.scope(false);
    const task = this.writes
      .catch(() => {})
      .then(async () => {
        if (
          epoch !== this.workspaceEpoch ||
          !this.store ||
          !this.model.state ||
          this.model.locked
        )
          throw new IntegrityError(
            "WORKSPACE_LOCKED",
            "The workspace changed or is locked.",
          );
        scope.assertCurrent();
        const previous = this.model.state;
        const next = change(this.model.state);
        const unknownRetirement = retiredWithoutReplacement(previous, next);
        await this.store.save(next);
        if (epoch !== this.workspaceEpoch || !scope.current()) return;
        if (unknownRetirement) {
          ++this.scopeFence;
          ++this.captureIntent;
          this.workspaceEpoch = newId();
          this.api.cancelAll();
        }
        this.patch({
          state: next,
          ...(unknownRetirement
            ? {
                selectedCheck: null,
                pendingReplacement: null,
                profileConflict: null,
                sheet: null,
                historyRows: [],
                historyCursor: null,
                diagnosticError: null,
                message:
                  "The service retired this data generation. Retained records are quarantined. Refresh account status before creating or opening current data.",
              }
            : {}),
        });
      });
    this.writes = task;
    await task;
  }
  async refreshConfig(): Promise<void> {
    const { value } = await this.api.request<unknown>("/v1/app-config", {
      public: true,
    });
    const config = parseAppConfig(value, BUILD);
    this.patch({ config, offline: false });
    if (
      this.model.identity &&
      this.model.state &&
      !this.model.locked &&
      this.model.state.notice?.sha256 !== config.notice.sha256
    )
      await this.loadNotice();
  }
  async loadNotice(): Promise<void> {
    const config = this.model.config,
      scope = this.scope();
    if (!this.model.identity) {
      await scope.wait(
        this.commit((state) => ({ ...state, notice: DEMO_NOTICE })),
      );
      return;
    }
    if (!config)
      throw new ApiError(
        0,
        "CONFIG_REQUIRED",
        "Reconnect to load the current account notice.",
        true,
      );
    const response = await scope.wait(
      this.api.request<unknown>(config.notice.content_path, { public: true }),
    );
    const notice = verifyNotice(response.value, config.notice);
    await scope.wait(this.commit((state) => ({ ...state, notice })));
  }
  async acknowledgeNotice(): Promise<void> {
    const scope = this.scope();
    const state = this.model.state,
      notice = state?.notice,
      epoch = this.workspaceEpoch;
    if (!state || !notice)
      throw new IntegrityError(
        "NOTICE_REQUIRED",
        "Load and review the complete notice.",
      );
    if (digestText(notice.text) !== notice.sha256)
      throw new IntegrityError(
        "NOTICE_HASH_MISMATCH",
        "The displayed notice could not be verified.",
      );
    if (this.model.identity) {
      if (notice.sha256 !== this.model.config?.notice.sha256)
        throw new IntegrityError(
          "NOTICE_CHANGED",
          "Review the current notice before continuing.",
        );
      let intent = state.queue.find(
        (q) =>
          q.kind === "acknowledgment" &&
          q.generation === state.generation &&
          q.body.version === notice.version &&
          q.body.sha256 === notice.sha256,
      );
      if (!intent) {
        await this.commit((current) =>
          queueMutation(
            current,
            "acknowledgment",
            {
              version: notice.version,
              sha256: notice.sha256,
              acknowledged_at: now(),
            },
            newId,
            now(),
          ),
        );
        intent = this.model.state!.queue.find(
          (q) =>
            q.kind === "acknowledgment" &&
            q.generation === state.generation &&
            q.body.sha256 === notice.sha256,
        )!;
      }
      await scope.wait(this.sync.run(intent.id, true));
      scope.assertCurrent();
      if (this.model.state?.acknowledgedNotice !== notice.sha256) {
        this.patch({
          message:
            "Your exact acknowledgment is saved as a pending request. Reconnect and continue to reconcile its receipt; research consent remains separate.",
        });
        return;
      }
      await this.refreshCapabilities();
      if (epoch !== this.workspaceEpoch || !scope.current()) return;
    } else
      await this.commit((current) => ({
        ...current,
        acknowledgedNotice: notice.sha256,
      }));
    this.patch({
      route: "home",
      message:
        "Application notice acknowledged. Research consent remains separate.",
    });
  }
  async signIn(reauthenticate = false): Promise<boolean> {
    const flow = ++this.authFlow;
    this.authenticating = true;
    const liveFlow = () => flow === this.authFlow && !this.disposed;
    try {
      await this.stopActive("WORKSPACE_CHANGED");
      if (!liveFlow()) return false;
      this.api.cancelAll();
      await this.sync.whenIdle();
      await this.auth.whenRefreshSettled();
      if (!liveFlow()) return false;
      const originEpoch = this.workspaceEpoch,
        expectedAuth = this.auth.generation,
        prior = this.model.identity;
      const awaitingLogin = () =>
        liveFlow() &&
        originEpoch === this.workspaceEpoch &&
        expectedAuth === this.auth.generation;
      if (!this.model.config) await this.refreshConfig();
      if (!awaitingLogin()) return false;
      await this.writes.catch(() => {});
      if (!awaitingLogin()) return false;
      if (prior) this.patch({ locked: true });
      const tokens = await this.auth.authorize(
        this.model.config!,
        reauthenticate,
      );
      if (!tokens || !awaitingLogin()) return false;
      const response = await this.api.request<unknown>("/v1/me/capabilities", {
        token: tokens.accessToken,
      });
      if (!awaitingLogin()) return false;
      const cap = parseCapabilities(response.value);
      if (reauthenticate && prior && cap.account_ref !== prior.accountRef)
        throw new IntegrityError(
          "REAUTH_ACCOUNT_MISMATCH",
          "Use the same account to confirm this action. No deletion was submitted.",
        );
      const identity: Identity = {
        accountRef: cap.account_ref,
        issuer: BUILD.issuer,
        generation: cap.data_generation,
        state: cap.account_state,
        verifiedAt: now(),
      };
      await this.auth.commit(tokens, identity, expectedAuth);
      const committedGeneration = this.auth.generation;
      const signedIn = () =>
        liveFlow() &&
        committedGeneration === this.auth.generation &&
        this.auth.identity?.accountRef === identity.accountRef;
      if (!signedIn() || originEpoch !== this.workspaceEpoch) return false;
      this.patch({ identity, locked: true });
      const unlocked = await unlockAccount();
      if (!signedIn() || originEpoch !== this.workspaceEpoch) return false;
      if (!unlocked) {
        this.patch({
          route: "home",
          message:
            "Signed in. Your records remain locked until device authentication succeeds.",
        });
        return false;
      }
      if (
        reauthenticate &&
        prior &&
        this.model.state?.workspace === this.accountWorkspace(identity) &&
        this.store
      ) {
        this.patch({ locked: false });
        await this.applyCapabilities(cap);
        return signedIn();
      }
      await this.activate(
        this.accountWorkspace(identity),
        identity.generation,
        signedIn,
      );
      if (!signedIn()) return false;
      await this.applyCapabilities(cap);
      if (!signedIn()) return false;
      const accountEpoch = this.workspaceEpoch;
      const activeAccount = () =>
        signedIn() &&
        accountEpoch === this.workspaceEpoch &&
        this.model.state?.workspace === this.accountWorkspace(identity);
      if (!activeAccount()) return false;
      if (cap.account_state === "active") {
        await this.refreshProfile();
        if (!activeAccount()) return false;
      }
      await this.loadNotice();
      if (!activeAccount()) return false;
      if (cap.notice.acknowledged) {
        await this.commit((s) => ({
          ...s,
          acknowledgedNotice: cap.notice.sha256,
        }));
        if (!activeAccount()) return false;
      }
      this.patch({
        route:
          cap.account_state !== "active"
            ? "privacy"
            : cap.notice.acknowledged
              ? "home"
              : "notice",
      });
      return true;
    } finally {
      if (liveFlow()) {
        this.authenticating = false;
        const store = this.store;
        if (this.model.locked && store) {
          await this.writes.catch(() => {});
          if (liveFlow() && this.store === store && this.model.locked) {
            this.store = null;
            await store.close();
            if (liveFlow()) this.patch({ state: null });
          }
        }
      }
    }
  }
  private async authenticationRequired(): Promise<void> {
    if (this.auth.identity || !this.model.identity) return;
    ++this.authFlow;
    this.authenticating = false;
    this.api.cancelAll();
    await this.stopActive("WORKSPACE_CHANGED");
    if (this.auth.identity) return;
    this.workspaceEpoch = newId();
    await this.writes.catch(() => {});
    const store = this.store;
    this.store = null;
    if (store) await store.close();
    this.patch({
      locked: true,
      state: null,
      sheet: null,
      historyRows: [],
      message:
        "The service rejected this sign-in session. Sign in again to the same account to reopen its encrypted records.",
    });
  }
  private scope(requireForeground = true, allowLocked = false) {
    return captureWorkspaceScope(() => ({
      epoch: this.workspaceEpoch,
      fence: this.scopeFence,
      authFlow: this.authFlow,
      workspace: this.model.state?.workspace ?? null,
      issuer: this.model.identity?.issuer ?? null,
      accountRef: this.model.identity?.accountRef ?? null,
      generation:
        this.model.state?.generation ?? this.model.identity?.generation ?? null,
      unlocked: allowLocked || (!!this.model.state && !this.model.locked),
      foreground: requireForeground ? this.foreground : true,
    }));
  }
  private async applyCapabilities(cap: Capabilities): Promise<void> {
    const scope = this.scope();
    scope.assertCurrent();
    if (cap.account_ref !== this.model.identity?.accountRef)
      throw new IntegrityError(
        "ACCOUNT_MISMATCH",
        "The response belongs to another account.",
      );
    const changed = cap.data_generation !== this.model.state!.generation;
    if (changed) {
      await scope.wait(this.stopActive("WORKSPACE_CHANGED"));
      this.scopeFence++;
      this.workspaceEpoch = newId();
      this.api.cancelAll();
    }
    const epoch = this.workspaceEpoch,
      flow = this.authFlow;
    await this.commit((state) => {
      const next = changed
        ? quarantineGeneration(state, cap.data_generation, now())
        : clone(state);
      next.generation = cap.data_generation;
      next.capabilities = cap;
      return next;
    });
    if (
      epoch !== this.workspaceEpoch ||
      flow !== this.authFlow ||
      this.model.identity?.accountRef !== cap.account_ref
    )
      return;
    const identity = {
      ...this.model.identity,
      generation: cap.data_generation,
      state: cap.account_state,
    };
    this.patch({
      identity,
      offline: false,
      ...(changed
        ? {
            selectedCheck: null,
            pendingReplacement: null,
            profileConflict: null,
            sheet: null,
            historyRows: [],
            historyCursor: null,
            diagnosticError: null,
          }
        : {}),
    });
    await this.auth.updateIdentity(identity);
  }
  async refreshCapabilities(): Promise<void> {
    if (!this.model.identity || this.model.locked) return;
    const scope = this.scope(),
      response = await scope.wait(
        this.api.request<unknown>("/v1/me/capabilities"),
      );
    scope.assertCurrent();
    await this.applyCapabilities(parseCapabilities(response.value));
  }
  async refreshProfile(): Promise<void> {
    if (!this.model.identity || this.model.locked) return;
    const scope = this.scope(),
      response = await scope.wait(this.api.request<unknown>("/v1/me/profile"));
    const profile = parseProfile(response.value, response.etag, now());
    scope.assertCurrent();
    if (
      this.model.state?.queue.some(
        (q) => q.kind === "profile" && q.state !== "synced",
      )
    ) {
      if (profile.etag !== this.model.state.profile.etag)
        this.patch({ profileConflict: profile });
      return;
    }
    await scope.wait(this.commit((state) => ({ ...state, profile })));
  }
  async saveProfile(profile: ProfileEnvelope): Promise<void> {
    this.requireWritable();
    const scope = this.scope();
    const normalized = normalizeProfile(profile, now());
    normalized.profile_version_id = newId();
    normalized.sync = this.model.identity ? "queued" : "local";
    await this.commit((s) => {
      const updated = { ...s, profile: normalized };
      return this.model.identity
        ? queueMutation(
            updated,
            "profile",
            { payload: profileBody(normalized), etag: profile.etag },
            newId,
            now(),
          )
        : updated;
    });
    scope.assertCurrent();
    this.patch({
      message: this.model.identity
        ? "Profile saved on this device. Its account update was explicitly queued."
        : "Profile saved on this device.",
    });
    if (this.model.identity) {
      const q = this.model.state!.queue.at(-1)!;
      await scope.wait(this.sync.run(q.id, true));
      if (
        this.model.state!.queue.find((x) => x.id === q.id)?.state === "conflict"
      )
        await this.refreshProfile();
    }
  }
  async resolveProfile(useServer: boolean): Promise<void> {
    const remote = this.model.profileConflict;
    if (!remote) return;
    const local = clone(this.model.state!.profile);
    await this.commit((s) => ({
      ...s,
      profile: useServer
        ? remote
        : { ...local, etag: remote.etag, revision: remote.revision },
      queue: s.queue.filter(
        (q) => q.kind !== "profile" || q.state === "synced",
      ),
    }));
    this.patch({ profileConflict: null });
    if (!useServer)
      await this.saveProfile({
        ...local,
        etag: remote.etag,
        revision: remote.revision,
      });
  }
  private requireWritable(requireNotice = true): void {
    if (!this.model.state || this.model.locked)
      throw new IntegrityError(
        "WORKSPACE_LOCKED",
        "Unlock this workspace first.",
      );
    if (
      this.model.identity &&
      this.model.state.capabilities?.account_state !== "active"
    )
      throw new IntegrityError(
        "ACCOUNT_READ_ONLY",
        "Finish the privacy request and start a new empty workspace before saving new account data.",
      );
    if (
      requireNotice &&
      this.model.identity &&
      this.model.state.acknowledgedNotice !==
        this.model.config?.notice.sha256 &&
      !(
        this.model.state.capabilities?.notice.acknowledged &&
        this.model.state.capabilities.notice.sha256 ===
          this.model.config?.notice.sha256
      )
    )
      throw new IntegrityError(
        "NOTICE_REQUIRED",
        "Review the current application notice before account writes.",
      );
  }
  async beginCheck(
    kind: CheckRecord["kind"],
    contextConfirmed: boolean,
    supersedes?: string,
  ): Promise<void> {
    this.requireWritable(false);
    if (
      kind === "engineering_fixture" &&
      (!this.model.identity ||
        !["local", "qa", "test"].includes(BUILD.environment))
    )
      throw new IntegrityError(
        "FIXTURE_ENVIRONMENT",
        "Account-owned fictional fixtures are limited to local and QA engineering accounts.",
      );
    if (kind === "guest_demo" && this.model.identity)
      throw new IntegrityError(
        "GUEST_NAMESPACE_REQUIRED",
        "Switch to the separate guest demo workspace.",
      );
    const check = createCheck(this.model.state!, {
      now: now(),
      id: newId,
      kind,
      accountRef: this.model.identity?.accountRef,
      contextConfirmed,
      supersedes: supersedes ?? this.model.pendingReplacement ?? undefined,
    });
    if (this.model.identity && this.model.state!.profile.sync !== "synced")
      check.context.profile_version_id = null;
    const association = this.device.snapshot().association;
    if (association) {
      check.context.device_associations = [
        {
          device_id: association.deviceId,
          binding_id: null,
          boot_id: association.bootId,
          hardware_revision: association.hardwareRevision,
          firmware_version: association.firmwareVersion,
          clock_evidence_ref: null,
        },
      ];
      check.snapshot.device = {
        device_id: association.deviceId,
        boot_id: association.bootId,
        hardware_revision: association.hardwareRevision,
        firmware_version: association.firmwareVersion,
      };
    }
    await this.commit((s) => replaceCheck(s, check));
    this.patch({
      route: "check",
      selectedCheck: check.id,
      pendingReplacement: null,
    });
  }
  async prepareReplacement(id: string): Promise<void> {
    const scope = this.scope(),
      check = this.check;
    if (!check || check.id !== id || !check.frozen)
      throw new IntegrityError(
        "CHECK_UNAVAILABLE",
        "Open the original saved check before starting its replacement.",
      );
    await scope.wait(this.stopActive("ROUTE_HIDDEN"));
    this.patch({ pendingReplacement: id, route: "home" });
  }
  async selectCheck(
    id: string,
    route: Route = "result",
    validate?: (check: CheckRecord) => void,
  ): Promise<void> {
    const scope = this.scope();
    await scope.wait(this.stopActive("ROUTE_HIDDEN"));
    if (
      this.model.state?.checks.some(
        (c) => c.id === id && c.delivery === "quarantined",
      )
    )
      throw new IntegrityError(
        "DATA_GENERATION_RETIRED",
        "This retained check belongs to retired data and cannot be opened in the active workspace.",
      );
    let check = this.model.state?.checks.find(
      (c) =>
        c.id === id &&
        c.generation === this.model.state!.generation &&
        c.delivery !== "quarantined",
    );
    if (!check && this.model.identity) {
      const response = await scope.wait(
        this.api.request<unknown>(`/v1/sessions/${id}`),
      );
      check = parseRemoteCheck(response.value, this.model.state!);
      validate?.(check);
      scope.assertCurrent();
      await scope.wait(this.commit((state) => replaceCheck(state, check!)));
    }
    if (!check)
      throw new IntegrityError(
        "CHECK_UNAVAILABLE",
        "This check is not available in the active workspace.",
      );
    validate?.(check);
    if (check.frozen) verifyCheck(check);
    scope.assertCurrent();
    this.patch({ selectedCheck: id, route: check.frozen ? route : "check" });
  }
  async openLinkedCheck(
    baseId: string,
    targetId: string,
    direction: "previous" | "replacement",
  ): Promise<void> {
    const base = this.check;
    if (!base || base.id !== baseId)
      throw new IntegrityError(
        "WORKSPACE_CHANGED",
        "The originating check is no longer open.",
      );
    await this.selectCheck(targetId, "result", (target) =>
      verifyReplacementTarget(base, target, direction),
    );
  }
  async refreshReplacementLinks(more = false): Promise<void> {
    const check = this.check,
      scope = this.scope(),
      requestId = ++this.replacementRequest;
    if (!check?.frozen || !check.remote_revision || !this.model.identity)
      throw new IntegrityError(
        "LOCAL_LINKS_ONLY",
        "This check has local replacement links only. Eligible account checks need a completed upload before loading service links.",
      );
    const cursor = more ? check.replacement_links?.next_cursor : null;
    if (more && !cursor) return;
    await scope.wait(this.stopActive("ROUTE_HIDDEN"));
    const response = await scope.wait(
      this.api.request<unknown>(
        `/v1/sessions/${check.id}/replacement-links?limit=20${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
      ),
    );
    const page = parseReplacementLinks(response.value, check);
    if (requestId !== this.replacementRequest || this.check?.id !== check.id)
      return;
    await scope.wait(
      this.commit((state) => {
        const current = state.checks.find((item) => item.id === check.id);
        if (
          !current ||
          current.snapshot_sha256 !== check.snapshot_sha256 ||
          requestId !== this.replacementRequest
        )
          throw new IntegrityError(
            "WORKSPACE_CHANGED",
            "The originating check changed before its links were saved.",
          );
        if (more && current.replacement_links?.next_cursor !== cursor)
          throw new IntegrityError(
            "REPLACEMENT_PAGE_CHANGED",
            "The replacement page changed. Refresh the first page before continuing.",
          );
        return replaceCheck(state, {
          ...current,
          replacement_links: mergeReplacementPage(
            current.replacement_links,
            page,
            more,
            now(),
          ),
        });
      }),
    );
  }
  async refreshReportRevisions(): Promise<void> {
    const check = this.check,
      scope = this.scope(),
      requestId = ++this.reportRequest;
    if (
      !check?.frozen ||
      !check.remote_revision ||
      !this.model.identity ||
      !check.result
    )
      throw new IntegrityError(
        "REPORT_ORIGINAL_REQUIRED",
        "Laboratory report history requires the uploaded original check and its completed original result. Local original evidence remains available.",
      );
    const current = () =>
      scope.current() &&
      this.check?.id === check.id &&
      requestId === this.reportRequest;
    await scope.wait(this.stopActive("ROUTE_HIDDEN"));
    if (!current()) return;
    const response = await scope.wait(
      this.api.request<unknown>(`/v1/sessions/${check.id}/report-revisions`),
    );
    if (!current()) return;
    const list = parseReportList(response.value, check);
    let cache = beginReportRefresh(list, check, now());
    const save = () =>
      this.commit((state) => {
        if (!current())
          throw new IntegrityError(
            "WORKSPACE_CHANGED",
            "The original check is no longer open.",
          );
        const saved = state.checks.find((item) => item.id === check.id);
        if (
          !saved ||
          !sameFrozenEvidence(saved, check) ||
          saved.result?.result_id !== check.result?.result_id
        )
          throw new IntegrityError(
            "REPORT_ORIGINAL_CHANGED",
            "The original result changed while report history was loading. Refresh the original record before continuing.",
          );
        return replaceCheck(state, {
          ...saved,
          report_revision_cache: clone(cache),
        });
      });
    // Persist the complete known index first. A missing later detail must block
    // local export instead of silently omitting a report discovered here.
    await scope.wait(save());
    for (let i = cache.companions.length; i < list.items.length; i++) {
      if (!current()) return;
      const detail = await scope.wait(
        this.api.request<unknown>(
          `/v1/sessions/${check.id}/report-revisions/${list.items[i]!.revision_id}`,
        ),
      );
      if (!current()) return;
      const companion = parseReportDetail(
        detail.value,
        check,
        list,
        cache.companions,
      );
      cache = {
        ...cache,
        companions: [...cache.companions, companion],
        observed_at: now(),
      };
      await scope.wait(save());
    }
    if (current())
      this.patch({
        message: list.items.length
          ? "Laboratory report history verified and saved separately from the original captured record."
          : "No laboratory report revisions were available when checked.",
        offline: false,
      });
  }
  async navigate(route: Route): Promise<void> {
    await this.stopActive("ROUTE_HIDDEN");
    this.patch({ route, error: null, message: null });
    if (route === "notice" && !this.model.state?.notice)
      await this.loadNotice();
    if (route === "studies" && this.model.identity) await this.refreshStudies();
  }
  async setStage(stage: Stage): Promise<void> {
    await this.stopActive("ROUTE_HIDDEN");
    const check = this.check;
    if (!check || check.frozen) return;
    await this.commit((s) => replaceCheck(s, { ...check, stage }));
  }
  async simulate(
    channel: Channel,
    modality: "ppg" | "ecg" = "ppg",
  ): Promise<void> {
    const check = this.check;
    if (!check)
      throw new IntegrityError("CHECK_REQUIRED", "Start a check first.");
    await this.commit((s) =>
      replaceCheck(s, simulatedCapture(check, channel, now(), newId, modality)),
    );
    this.patch({
      message: "Fictional example saved with simulated provenance.",
    });
  }
  private async withCaptureIntent(
    check: CheckRecord,
    operation: (current: () => boolean) => Promise<void>,
  ): Promise<void> {
    if (this.acquiring || this.pendingCapture)
      throw new IntegrityError(
        "CAPTURE_ACTIVE",
        "End the active capture before starting another.",
      );
    const intent = ++this.captureIntent,
      epoch = this.workspaceEpoch,
      stage = check.stage;
    const current = () =>
      intent === this.captureIntent &&
      epoch === this.workspaceEpoch &&
      this.foreground &&
      !this.disposed &&
      !this.model.locked &&
      this.model.route === "check" &&
      this.check?.id === check.id &&
      this.check.stage === stage;
    this.acquiring = true;
    const pending = Promise.resolve().then(async () => {
      if (current()) await operation(current);
    });
    this.pendingCapture = pending;
    try {
      await pending;
    } finally {
      if (this.pendingCapture === pending) this.pendingCapture = null;
      if (!this.model.activeTask) this.acquiring = false;
    }
  }
  private async abandonArmedCapture(
    checkId: string,
    attemptId: string,
  ): Promise<void> {
    if (!this.model.state || this.model.locked) return;
    await this.commit((state) => {
      const check = state.checks.find((c) => c.id === checkId);
      return check?.attempts.some(
        (a) => a.attempt_id === attemptId && a.status === "started",
      )
        ? replaceCheck(state, interruptStartedAttempts(check, now()))
        : state;
    });
  }
  async simulateDevice(
    channel: "saliva" | "ppg" | "ecg",
    signalScenario: SyntheticSignalScenario = "clean",
  ): Promise<void> {
    const check = this.check;
    if (!check || check.frozen || check.kind === "measurement")
      throw new IntegrityError(
        "SYNTHETIC_PARENT_REQUIRED",
        "A simulator capture requires an unfinished synthetic check.",
      );
    if (this.device.snapshot().state !== "connected_simulator")
      throw new IntegrityError(
        "DEVICE_REQUIRED",
        "Connect a synthetic simulator from Devices first.",
      );
    await this.withCaptureIntent(check, async (current) => {
      this.api.cancelAll();
      await this.sync.whenIdle();
      if (!current()) return;
      await this.auth.whenRefreshSettled();
      if (!current()) return;
      await this.writes.catch(() => {});
      if (!current()) return;
      const epoch = this.workspaceEpoch,
        started = startAttempt(
          this.check!,
          channel === "saliva" ? "saliva" : "cardiac",
          now(),
          newId,
          "simulated",
          "synthetic_bench_v1",
          syntheticConfigurationDigest(channel),
          channel === "saliva" ? undefined : channel,
        );
      try {
        await this.commit((state) => replaceCheck(state, started.check));
        if (!current()) {
          await this.abandonArmedCapture(check.id, started.attempt.attempt_id);
          return;
        }
        const result = await this.device.captureSynthetic(
          channel,
          {
            sessionId: check.id,
            attemptId: started.attempt.attempt_id,
            captureId: started.attempt.record_id,
            workspaceEpoch: epoch,
          },
          channel === "saliva" ? undefined : { signalScenario },
        );
        if (!current() || result.context.workspaceEpoch !== epoch) {
          await this.abandonArmedCapture(check.id, started.attempt.attempt_id);
          return;
        }
        const projection = projectSyntheticDevice(
          result,
          started.attempt,
          newId,
        );
        await this.commit((state) => {
          const currentCheck = state.checks.find((c) => c.id === check.id)!;
          return replaceCheck(
            state,
            settleAttempt(
              currentCheck,
              started.attempt.attempt_id,
              projection,
              "valid",
              result.endedAt,
              result.qualityFlags,
              {
                transport_evidence: result as unknown as JsonObject,
                fixture_id: result.fixtureId,
              },
            ),
          );
        });
        if (current())
          this.patch({
            message:
              "Bounded synthetic transport capture saved. The complete packet and clock evidence is retained; human measurement remains unavailable.",
          });
      } catch (error) {
        const endedAt = now(),
          signalFailure = current()
            ? getSyntheticSignalFailure(error, started.attempt, endedAt)
            : null;
        if (signalFailure) {
          await this.commit((state) => {
            const currentCheck = state.checks.find(
              (item) => item.id === check.id,
            );
            if (!current() || !currentCheck)
              throw new IntegrityError(
                "WORKSPACE_CHANGED",
                "The synthetic capture belongs to a prior check or workspace.",
              );
            return replaceCheck(
              state,
              settleAttempt(
                currentCheck,
                started.attempt.attempt_id,
                signalFailure.projection,
                "invalid",
                endedAt,
                signalFailure.qualityFlags,
                signalFailure.metadata,
              ),
            );
          });
          if (current())
            this.patch({
              message:
                "Synthetic signal quality failed. The invalid attempt and its reason were saved with null physiological features. Reconnect and start a new attempt.",
            });
          return;
        }
        if (epoch === this.workspaceEpoch)
          await this.abandonArmedCapture(check.id, started.attempt.attempt_id);
        if (current()) throw error;
      }
    });
  }
  async selectCardiac(attemptId: string): Promise<void> {
    const check = this.check;
    if (!check || check.frozen)
      throw new IntegrityError(
        "CHECK_REQUIRED",
        "Choose a cardiac acquisition in an unfinished check.",
      );
    await this.commit((state) =>
      replaceCheck(state, selectCardiacAttempt(check, attemptId, now())),
    );
  }
  async saveCheck(): Promise<void> {
    await this.stopActive("USER_CANCELED");
    if (!this.check) return;
    const record = freezeCheck(this.check, now(), newId);
    await this.commit((s) => replaceCheck(s, record));
    this.patch({
      route: "result",
      message: "Check saved on this device. No upload was queued.",
    });
  }
  async discardDraft(): Promise<void> {
    await this.stopActive("USER_CANCELED");
    const check = this.check;
    if (!check || check.frozen) return;
    await this.commit((s) => ({
      ...s,
      checks: s.checks.filter((c) => c.id !== check.id),
    }));
    this.patch({ selectedCheck: null, route: "home" });
  }
  async startNativeTask(): Promise<void> {
    const check = this.check;
    if (!check || check.frozen)
      throw new IntegrityError(
        "CHECK_REQUIRED",
        "Start or resume a draft check.",
      );
    if (check.kind === "engineering_fixture")
      throw new IntegrityError(
        "FICTIONAL_FIXTURE_ONLY",
        "Real native taps require a separate measurement check or guest demo.",
      );
    if (!getReactionTaskAvailability().available)
      throw new IntegrityError(
        "NATIVE_MODULE_UNAVAILABLE",
        "Install a native development or release build to run the reaction task.",
      );
    await this.withCaptureIntent(check, async (current) => {
      this.api.cancelAll();
      await this.sync.whenIdle();
      if (!current()) return;
      await this.auth.whenRefreshSettled();
      if (!current()) return;
      await this.writes.catch(() => {});
      if (!current()) return;
      const { check: next, attempt } = startAttempt(
        this.check!,
        "task",
        now(),
        newId,
        "prototype_sensor",
        TASK_CONFIGURATION_ID,
        TASK_CONFIGURATION_SHA256,
      );
      await this.commit((state) => replaceCheck(state, next));
      if (!current()) {
        await this.abandonArmedCapture(check.id, attempt.attempt_id);
        return;
      }
      this.patch({
        activeTask: {
          runId: attempt.record_id,
          attemptId: attempt.attempt_id,
          checkId: check.id,
          seed: parseInt(newId().slice(0, 8), 16),
          epoch: this.workspaceEpoch,
        },
        taskProgress: "Practice · ready",
      });
    });
  }
  async completeNativeTask(result: NativeTaskResult): Promise<void> {
    assertBytes(result, 524_288);
    const active = this.model.activeTask;
    if (
      !active ||
      result.runId !== active.runId ||
      result.workspaceEpoch !== active.epoch ||
      active.epoch !== this.workspaceEpoch
    ) {
      const pending = this.terminalEvidence.pending(result.runId);
      if (pending) await pending;
      return;
    }
    return this.terminalEvidence.persist(
      result.runId,
      digest(result),
      async () => {
        if (
          result.configurationSha256 !== TASK_CONFIGURATION_SHA256 ||
          result.configurationId !== TASK_CONFIGURATION_ID ||
          result.source !== "native_task" ||
          result.schemaVersion !== "1.0.0" ||
          result.timing.modelEligible !== false ||
          result.timing.physicalOnsetVerified !== false ||
          result.trialEvents.length !== 66 ||
          result.inputEvents.length > 1024
        )
          throw new IntegrityError(
            "NATIVE_RESULT_INVALID",
            "The native task evidence is unsupported or incomplete. End task again to retrieve its terminal record.",
          );
        const projection = taskProjection(
          result as unknown as JsonObject,
          active.runId,
        );
        await this.commit((state) => {
          const check = state.checks.find((c) => c.id === active.checkId);
          if (!check || active.epoch !== this.workspaceEpoch)
            throw new IntegrityError(
              "WORKSPACE_CHANGED",
              "The task evidence belongs to another workspace.",
            );
          return replaceCheck(
            state,
            settleAttempt(
              check,
              active.attemptId,
              projection,
              result.status,
              result.endedAt,
              [...new Set(["uncalibrated", ...result.qualityFlags])],
              { native_result: result as unknown as JsonObject },
            ),
          );
        });
        if (
          this.model.activeTask?.runId === active.runId &&
          this.workspaceEpoch === active.epoch
        ) {
          this.acquiring = false;
          this.patch({
            activeTask: null,
            taskProgress: null,
            message:
              result.status === "valid"
                ? "Native practice recorded. Physical timing and impairment prediction remain unqualified."
                : "Task ended as invalid. Its evidence was retained; a new attempt is required.",
          });
        }
      },
    );
  }
  updateProgress(
    runId: string,
    epoch: string,
    phase: string,
    presented: number,
  ): void {
    if (this.model.activeTask?.runId === runId && epoch === this.workspaceEpoch)
      this.patch({
        taskProgress: `${phase === "practice" ? "Practice" : "Scored"} · ${presented} / 66 presented`,
      });
  }
  async stopActive(reason: TaskCancelReason): Promise<void> {
    ++this.captureIntent;
    const pendingStart = this.pendingCapture;
    const active = this.model.activeTask,
      view = this.nativeView;
    return this.stopRequests.run(
      active?.runId ?? `device:${this.workspaceEpoch}`,
      async () => {
        // This call is deliberately first; a radio timeout cannot delay native UI-thread cancellation.
        const nativeStop =
          active && view
            ? view.cancel(active.runId, reason)
            : Promise.resolve(null);
        const deviceStops = Promise.allSettled([
          this.device.cancelCapture(reason),
          this.device.stopScan(),
        ]);
        try {
          const receipt = await nativeStop;
          if (active) {
            if (receipt?.result) await this.completeNativeTask(receipt.result);
            else {
              const pending = this.terminalEvidence.pending(active.runId);
              if (pending) await pending;
              else if (
                !view &&
                this.nativeMountedRun !== active.runId &&
                this.model.activeTask?.runId === active.runId
              ) {
                // The persisted intent never mounted a native view: invalidate that intent explicitly.
                await this.commit((state) => {
                  const check = state.checks.find(
                    (c) => c.id === active.checkId,
                  );
                  return check
                    ? replaceCheck(
                        state,
                        interruptStartedAttempts(check, now()),
                      )
                    : state;
                });
                this.acquiring = false;
                this.patch({ activeTask: null, taskProgress: null });
              }
            }
            if (this.model.activeTask?.runId === active.runId)
              throw new IntegrityError(
                "NATIVE_TERMINAL_PENDING",
                "The task is stopping, but its complete terminal evidence has not been saved. End task again to retry; this check remains open.",
              );
          }
          await pendingStart;
          // A previous failed arm invalidation remains recoverable on the next explicit stop.
          if (
            !this.model.activeTask &&
            this.model.state?.checks.some(
              (check) =>
                check.generation === this.model.state!.generation &&
                check.delivery !== "quarantined" &&
                check.attempts.some((attempt) => attempt.status === "started"),
            )
          )
            await this.commit((state) => ({
              ...state,
              checks: state.checks.map((check) =>
                check.generation === state.generation &&
                check.delivery !== "quarantined"
                  ? interruptStartedAttempts(check, now())
                  : check,
              ),
            }));
          await this.writes;
        } finally {
          const results = await deviceStops;
          for (const result of results)
            if (result.status === "rejected") this.report(result.reason);
        }
      },
    );
  }
  async ask(sheet: SheetSpec): Promise<void> {
    const scope = this.scope(true, true);
    await scope.wait(this.stopActive("ROUTE_HIDDEN"));
    const guarded: SheetSpec = {
      ...sheet,
      action: async () => {
        scope.assertCurrent();
        await sheet.action();
      },
      ...(sheet.secondary
        ? {
            secondary: {
              ...sheet.secondary,
              action: async () => {
                scope.assertCurrent();
                await sheet.secondary!.action();
              },
            },
          }
        : {}),
    };
    scope.assertCurrent();
    this.patch({ sheet: guarded });
  }
  closeSheet(): void {
    if (!this.model.busy) this.patch({ sheet: null });
  }
  async confirmSheet(secondary = false): Promise<void> {
    const sheet = this.model.sheet;
    if (!sheet) return;
    this.patch({ sheet: null });
    await (secondary ? sheet.secondary?.action() : sheet.action());
  }
  async uploadCheck(): Promise<void> {
    this.requireWritable();
    const check = this.check;
    if (!check || !this.model.identity)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Account uploads require a signed-in owner. Guest records never migrate.",
      );
    await this.commit((s) => queueCheck(s, check.id, newId, now()));
    const queue = this.model.state!.queue.find(
      (q) => q.check_id === check.id && q.state !== "synced",
    );
    if (queue) await this.sync.run(queue.id, true);
  }
  async reconcilePrivacy(queueId: string): Promise<void> {
    const original = this.model.state?.queue.find((q) => q.id === queueId);
    if (!original || !["deletion", "withdrawal"].includes(original.kind))
      return;
    if (!(await this.signIn(true))) return;
    await this.commit((s) => ({
      ...s,
      queue: s.queue.map((q) =>
        q.id === queueId
          ? { ...q, state: "queued", error: null, next_attempt_at: null }
          : q,
      ),
    }));
    await this.sync.run(queueId, true);
  }
  async retryUploads(): Promise<void> {
    await this.sync.retryDue(true);
  }
  async cancelQueue(id: string): Promise<void> {
    this.api.cancelAll();
    await this.commit((s) => ({
      ...s,
      queue: s.queue.filter((q) => q.id !== id),
      checks: s.checks.map((c) =>
        s.queue.find((q) => q.id === id)?.check_id === c.id
          ? {
              ...c,
              delivery: c.remote_revision
                ? "awaiting_result"
                : "local_finalized",
            }
          : c,
      ),
    }));
    this.patch({
      message:
        "Further upload attempts stopped. Data already accepted by the service is not erased; use Privacy for deletion.",
    });
  }
  async refreshHistory(more = false): Promise<void> {
    if (!this.model.identity) return;
    const scope = this.scope(),
      cursor = more ? this.model.state?.historyCursor : null;
    const response = await scope.wait(
      this.api.request<JsonObject>(
        `/v1/sessions?limit=20${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
      ),
    );
    if (!Array.isArray(response.value.items))
      throw new IntegrityError(
        "HISTORY_UNSUPPORTED",
        "The history response is unsupported.",
      );
    const rows = response.value.items as JsonObject[];
    const historyRows = [
      ...new Map(
        [...(more ? this.model.state!.historyIndex : []), ...rows].map(
          (row) => [String(row.session_id), row],
        ),
      ).values(),
    ].slice(0, 500);
    const historyCursor =
      typeof response.value.next_cursor === "string" && historyRows.length < 500
        ? response.value.next_cursor
        : null;
    await scope.wait(
      this.commit((state) => ({
        ...state,
        historyIndex: historyRows,
        historyCursor,
      })),
    );
    scope.assertCurrent();
    this.patch({ historyRows, historyCursor, offline: false });
  }
  async refreshCurrentCheck(): Promise<void> {
    const check = this.check;
    if (!check || !this.model.identity || !check.remote_revision) return;
    const scope = this.scope(),
      response = await scope.wait(
        this.api.request<unknown>(`/v1/sessions/${check.id}`),
      );
    const remote = parseRemoteCheck(response.value, this.model.state!);
    if (!sameFrozenEvidence(check, remote))
      throw new IntegrityError(
        "REMOTE_RECORD_CONFLICT",
        "The remote snapshot/evidence differs. The local record was retained.",
      );
    await scope.wait(
      this.commit((state) => {
        const current = state.checks.find((item) => item.id === check.id);
        if (!current || remote.remote_revision < current.remote_revision)
          return state;
        return replaceCheck(state, {
          ...remote,
          ...(current.replacement_links
            ? { replacement_links: current.replacement_links }
            : {}),
          ...(current.report_revision_cache
            ? { report_revision_cache: current.report_revision_cache }
            : {}),
        });
      }),
    );
  }
  async changePreferences(
    values: Partial<WorkspaceState["preferences"]>,
  ): Promise<void> {
    await this.commit((s) => ({
      ...s,
      preferences: { ...s.preferences, ...values },
    }));
  }
  async openExport(entry: ExportEntry): Promise<void> {
    const scope = this.scope();
    await scope.wait(this.stopActive("ROUTE_HIDDEN"));
    await this.commit((s) => ({ ...s, exportEntry: clone(entry) }));
    scope.assertCurrent();
    this.patch({ route: "export" });
  }
  async changeExportSource(source: ExportEntry["source"]): Promise<void> {
    await this.commit((s) => ({
      ...s,
      exportEntry: { ...s.exportEntry!, source },
    }));
  }
  async createExport(): Promise<void> {
    const scope = this.scope(),
      state = this.model.state!,
      entry = state.exportEntry;
    scope.assertCurrent();
    if (!entry)
      throw new IntegrityError(
        "EXPORT_SELECTION_REQUIRED",
        "Choose an export scope first.",
      );
    if (entry.source === "device") {
      const bytes = createLocalExport(state, entry.selection, now());
      scope.assertCurrent();
      await shareArchive(bytes, newId(), scope.assertCurrent);
      if (scope.current())
        this.patch({
          message:
            Platform.OS === "web"
              ? "Your selected export was prepared for download."
              : "Share sheet closed. Temporary app copy removed; shared copies remain with their recipients.",
        });
      return;
    }
    if (!this.model.identity)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Synced records require an account. Guest checks remain local.",
      );
    const body = {
      selection: entry.selection,
      format: "json_zip",
      include_raw: false,
    } as unknown as JsonObject;
    await scope.wait(
      this.commit((current) =>
        queueMutation(current, "export", body, newId, now()),
      ),
    );
    const queued = this.model.state!.queue.find(
      (q) =>
        q.kind === "export" &&
        q.state !== "synced" &&
        digest(q.body) === digest(body),
    );
    if (queued) await scope.wait(this.sync.run(queued.id, true));
    scope.assertCurrent();
    this.patch({
      message:
        "The exact export request is recorded. View the job receipt or requested-operation state; an unconfirmed outcome can retry with the same idempotency key.",
    });
  }
  async refreshJob(id: string): Promise<void> {
    const scope = this.scope();
    const response = await scope.wait(
        this.api.request<unknown>(`/v1/privacy/jobs/${id}`),
      ),
      job = parsePrivacyJob(response.value);
    if (job.job_id !== id)
      throw new IntegrityError(
        "PRIVACY_JOB_MISMATCH",
        "The service returned another request receipt.",
      );
    if (
      job.kind === "export" &&
      job.data_generation !== this.model.state!.generation
    )
      throw new IntegrityError(
        "DATA_GENERATION_RETIRED",
        "This export belongs to a retired generation.",
      );
    await scope.wait(
      this.commit((state) => ({
        ...state,
        jobs: [job, ...state.jobs.filter((item) => item.job_id !== id)],
      })),
    );
    if (job.kind === "deletion") {
      scope.assertCurrent();
      await this.refreshCapabilities();
    }
  }
  async shareJob(id: string): Promise<void> {
    const scope = this.scope();
    await scope.wait(this.refreshJob(id));
    const job = this.model.state!.jobs.find((item) => item.job_id === id);
    if (
      !job ||
      job.kind !== "export" ||
      job.state !== "completed" ||
      !job.download_path ||
      job.data_generation !== this.model.state!.generation
    )
      throw new IntegrityError(
        "EXPORT_NOT_READY",
        "This export is not ready to download in the current workspace.",
      );
    const bytes = await scope.wait(
      this.api.download(
        job.download_path,
        this.model.state!.generation,
        job.size_bytes,
      ),
    );
    if (!job.sha256 || digestBytes(bytes) !== job.sha256)
      throw new IntegrityError(
        "EXPORT_HASH_MISMATCH",
        "The archive failed its integrity check or its receipt lacks a checksum.",
      );
    inspectExportArchive(bytes, {
      selection: typeof job.scope === "object" ? job.scope : undefined,
      manifestSha256: job.manifest_sha256,
      accountRef: this.model.identity!.accountRef,
      generation: this.model.state!.generation,
    });
    scope.assertCurrent();
    await shareArchive(bytes, id, scope.assertCurrent);
    if (scope.current())
      this.patch({
        message:
          "Share sheet closed. Already shared copies cannot be recalled.",
      });
  }
  async deleteCloud(scope: "all_data" | "account"): Promise<void> {
    if (!this.model.identity)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Sign in to request cloud deletion.",
      );
    if (!(await this.signIn(true))) return;
    const identity = this.model.identity!,
      generation = this.model.state!.generation;
    await this.ask({
      title:
        scope === "account"
          ? "Request account deletion?"
          : "Request deletion of all cloud data?",
      text:
        scope === "account"
          ? "Your fresh sign-in is complete. This request deletes this account and its cloud data under the displayed retention policy. A pending receipt is not completed deletion. Local guest records are outside this scope."
          : "Your fresh sign-in is complete. This request deletes all data in this account’s current cloud generation under the displayed retention policy. The account remains; new data can resume only after completed deletion and a separate new-workspace acknowledgment.",
      confirm: "Request deletion",
      danger: true,
      action: () => this.submitDeletion(scope, identity.accountRef, generation),
    });
  }
  private async submitDeletion(
    scope: "all_data" | "account",
    accountRef: string,
    generation: number,
  ): Promise<void> {
    if (
      this.model.identity?.accountRef !== accountRef ||
      this.model.state?.generation !== generation ||
      this.model.locked
    )
      throw new IntegrityError(
        "DELETION_CONFIRMATION_CHANGED",
        "The account or data generation changed. Review and reauthenticate before requesting deletion.",
      );
    const scopeGuard = this.scope();
    await scopeGuard.wait(this.stopActive("WITHDRAWAL"));
    this.api.cancelAll();
    await this.commit((state) =>
      queueMutation(
        state,
        "deletion",
        { scope, confirmation: true },
        newId,
        now(),
      ),
    );
    const item = this.model.state!.queue.find(
      (q) =>
        q.kind === "deletion" && q.state !== "synced" && q.body.scope === scope,
    )!;
    await scopeGuard.wait(this.sync.run(item.id, true));
    scopeGuard.assertCurrent();
    this.patch({
      message:
        "Deletion request recorded. A pending or failed request is not completed deletion. Its exact intent may retry to reconcile the outcome.",
      route: "privacy",
    });
    try {
      await this.refreshCapabilities();
    } catch {
      /* The exact receipt remains available when the provider identity has been removed. */
    }
  }
  async acknowledgeNewGeneration(): Promise<void> {
    await this.refreshCapabilities();
    const state = this.model.state!,
      scope = this.scope();
    if (state.capabilities?.account_state !== "awaiting_generation_ack")
      throw new IntegrityError(
        "DELETION_NOT_COMPLETE",
        "Wait until deletion completes before starting a new workspace.",
      );
    await this.api.request("/v1/me/data-generation/acknowledgments", {
      method: "POST",
      body: { confirmation: true },
      generation: state.generation,
      key: newId(),
    });
    scope.assertCurrent();
    await this.commit((s) => ({
      ...emptyWorkspace(s.workspace, now(), s.generation),
      preferences: s.preferences,
      jobs: s.jobs,
      notice: s.notice,
    }));
    scope.assertCurrent();
    await this.refreshCapabilities();
    if (!scope.current()) return;
    await scope.wait(this.loadNotice());
    scope.assertCurrent();
    this.patch({
      route: "notice",
      message:
        "A new empty workspace was created. Old records and study consent were not restored.",
    });
  }
  async clearLocal(): Promise<void> {
    const before = this.scope();
    await before.wait(this.stopActive("WORKSPACE_CHANGED"));
    this.scopeFence++;
    this.workspaceEpoch = newId();
    this.api.cancelAll();
    await this.writes.catch(() => {});
    const scope = this.scope();
    await scope.wait(
      this.commit((state) => ({
        ...emptyWorkspace(state.workspace, now(), state.generation),
        preferences: state.preferences,
        notice: state.notice,
        acknowledgedNotice: state.acknowledgedNotice,
        capabilities: state.capabilities,
        jobs: state.jobs.filter((job) => job.kind === "deletion"),
        queue: state.queue.filter((q) =>
          ["deletion", "withdrawal"].includes(q.kind),
        ),
      })),
    );
    scope.assertCurrent();
    this.patch({
      selectedCheck: null,
      historyRows: [],
      historyCursor: null,
      pendingReplacement: null,
      profileConflict: null,
      diagnosticError: null,
      sheet: null,
      message:
        "This workspace’s local records were cleared. Cloud records were not deleted.",
    });
  }
  async refreshStudies(): Promise<void> {
    if (!this.model.identity) return;
    const scope = this.scope(),
      response = await scope.wait(
        this.api.request<JsonObject>("/v1/me/studies"),
      );
    if (!Array.isArray(response.value.items))
      throw new IntegrityError(
        "STUDIES_UNSUPPORTED",
        "The study membership response is unsupported.",
      );
    await scope.wait(
      this.commit((state) => ({
        ...state,
        studies: response.value.items as JsonObject[],
      })),
    );
  }
  async consent(study: JsonObject): Promise<void> {
    this.requireWritable();
    if (!(await this.signIn(true))) return;
    const scope = this.scope();
    const text = String(study.document_text ?? ""),
      hash = String(study.document_sha256 ?? "");
    if (!text || digestText(text) !== hash)
      throw new IntegrityError(
        "STUDY_DOCUMENT_INVALID",
        "Approved study information is missing or could not be verified.",
      );
    await this.api.request(`/v1/studies/${study.study_id}/consents`, {
      method: "POST",
      body: {
        invitation_id: study.invitation_id,
        document_version: study.document_version,
        document_sha256: hash,
        accepted: true,
      },
      generation: this.model.state!.generation,
      key: newId(),
    });
    scope.assertCurrent();
    await scope.wait(this.refreshStudies());
    await this.refreshCapabilities();
    if (!scope.current()) return;
    this.patch({
      message:
        "Consent recorded for that exact study version. Measurement qualification remains separate.",
    });
  }
  async withdraw(studyId: string): Promise<void> {
    const scope = this.scope();
    await scope.wait(this.stopActive("WITHDRAWAL"));
    this.api.cancelAll();
    await this.commit((s) => {
      const next = queueMutation(
        s,
        "withdrawal",
        { study_id: studyId, payload: { confirmation: true } },
        newId,
        now(),
      );
      next.studies = next.studies.map((x) =>
        String(x.study_id) === studyId
          ? { ...x, local_withdrawal_pending: true }
          : x,
      );
      next.queue = next.queue.map((q) =>
        q.kind === "check" &&
        q.state !== "synced" &&
        s.checks.find((c) => c.id === q.check_id)?.snapshot.study_id === studyId
          ? { ...q, state: "blocked", error: "WITHDRAWAL_PENDING" }
          : q,
      );
      return next;
    });
    const queued = this.model.state!.queue.find(
      (q) =>
        q.kind === "withdrawal" &&
        q.state !== "synced" &&
        q.body.study_id === studyId,
    );
    scope.assertCurrent();
    if (queued) await scope.wait(this.sync.run(queued.id, true));
    scope.assertCurrent();
    this.patch({
      message:
        "Local study work stopped. Read the membership receipt or pending request status to confirm the service outcome.",
    });
  }
  async signOut(removeLocal: boolean): Promise<void> {
    const flow = ++this.authFlow;
    this.authenticating = false;
    this.api.cancelAll();
    const identity = this.model.identity,
      generation = this.model.state?.generation ?? identity?.generation,
      token = this.auth.logoutReceiptToken(),
      providerLogout = this.auth.providerLogoutUrl();
    // Clear memory and serialize OS credential removal before a late login can commit.
    const providerRevoke = this.auth.revokeProvider().catch(() => {});
    const credentialRemoval = this.auth.clear();
    await this.stopActive("WORKSPACE_CHANGED");
    await credentialRemoval;
    if (flow !== this.authFlow) return;
    if (removeLocal && this.store) await this.store.clear();
    this.workspaceEpoch = newId();
    await this.writes.catch(() => {});
    if (this.store) await this.store.close();
    this.store = null;
    this.patch({
      state: null,
      identity: null,
      locked: false,
      sheet: null,
      diagnosticError: null,
      route: "welcome",
      selectedCheck: null,
      historyRows: [],
      historyCursor: null,
    });
    await this.openGuest();
    this.patch({
      route: "welcome",
      message:
        "Signed out. The retained account cache requires the same account to sign in again.",
    });
    if (token && generation) {
      try {
        await this.api.request("/v1/auth/logout", {
          method: "POST",
          body: {},
          token,
          generation,
          key: newId(),
        });
        await providerRevoke;
        if (providerLogout) await this.auth.openProviderLogout(providerLogout);
      } catch {
        this.patch({
          message:
            "Signed out on this device. Remote token or provider-session revocation was not confirmed.",
        });
      }
    } else
      this.patch({
        message:
          "Signed out on this device. Remote token revocation was not confirmed.",
      });
  }
  async background(): Promise<void> {
    this.foreground = false;
    this.api.cancelAll();
    await this.stopActive("BACKGROUND");
    if (this.authenticating) return;
    if (this.model.identity) {
      this.workspaceEpoch = newId();
      await this.writes.catch(() => {});
      if (this.store) await this.store.close();
      this.store = null;
      this.patch({ locked: true, state: null, sheet: null, historyRows: [] });
    }
  }
  async foregrounded(): Promise<void> {
    this.foreground = true;
    if (!this.authenticating && !this.model.locked && !this.acquiring) {
      try {
        await this.refreshConfig();
        if (this.model.identity) {
          await this.refreshCapabilities();
          await this.sync.retryDue();
        }
      } catch {
        this.patch({ offline: true });
      }
    }
  }
  async tick(): Promise<void> {
    if (
      this.foreground &&
      !this.authenticating &&
      !this.acquiring &&
      !this.model.busy &&
      !this.model.locked &&
      this.model.identity
    ) {
      await this.sync.retryDue();
      for (const q of this.model.state?.queue ?? [])
        if (
          q.kind === "check" &&
          q.state === "awaiting_result" &&
          (this.resultPolls.get(q.id) ?? 0) < 10
        ) {
          this.resultPolls.set(q.id, (this.resultPolls.get(q.id) ?? 0) + 1);
          await this.sync.run(q.id, true);
          break;
        }
    }
  }
  async dispose(): Promise<void> {
    ++this.authFlow;
    this.authenticating = false;
    await this.stopActive("VIEW_DETACHED");
    this.disposed = true;
    this.api.cancelAll();
    await this.device.dispose();
    if (this.store) await this.store.close();
    this.listeners.clear();
  }
}
