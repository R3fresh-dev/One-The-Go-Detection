import {
  getEyeCaptureAvailability,
  type EyeOptions,
  type EyeCaptureComplete,
  type EyeCaptureViewRef,
} from "../modules/eye-capture";
import { projectNativeEye } from "./core/eyeProjection";
import type { RawPermission } from "./core/rawArtifacts";
import { decodeRawRecording, verifyRawPermission } from "./core/rawArtifacts";
import {
  configurationFor,
  configurationsFor,
  verifyCaptureGrant,
  verifyCaptureStart,
  type AcquisitionChannel,
  type ApprovedConfiguration,
} from "./core/acquisition";
import {
  bindingTranscript,
  readerBinding,
  type PhysicalCapabilities,
  type PhysicalChannel,
  type ReaderBinding,
  type SignedStartToken,
} from "./device/physicalProtocol";
import { assessStudyConsent } from "./ui/study-consent";
import {
  assertRawChoicesAllowed,
  parseRawRecordingStatus,
  RAW_KINDS,
  type RawChoices,
  type RawKind,
} from "./core/rawRecordings";
import { Platform } from "react-native";
import { RunStopGate, TerminalEvidenceGate } from "./core/operationGuards";
import {
  parseRawExportPage,
  confirmRawExport,
  type RawExportScope,
} from "./core/rawExport";
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
  canonicalJson,
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
export interface ActiveEye {
  runId: string;
  attemptId: string;
  checkId: string;
  epoch: string;
  configurationId: string;
  options: EyeOptions;
  stopping?: boolean;
}
export interface AppModel {
  state: WorkspaceState | null;
  config: AppConfig | null;
  identity: Identity | null;
  route: Route;
  selectedCheck: string | null;
  rawStudyId: string | null;
  locked: boolean;
  loading: boolean;
  busy: boolean;
  privacyBusy: boolean;
  error: string | null;
  message: string | null;
  offline: boolean;
  activeTask: ActiveTask | null;
  activeEye: ActiveEye | null;
  eyeProgress: string | null;
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
    rawStudyId: null,
    locked: false,
    loading: true,
    busy: false,
    privacyBusy: false,
    error: null,
    message: null,
    offline: false,
    activeTask: null,
    activeEye: null,
    eyeProgress: null,
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
  eyeView: EyeCaptureViewRef | null = null;
  private readonly eyeRuns = new Map<string, ActiveEye>();
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
  readonly device = createDeviceController(
    { idFactory: newId },
    !BUILD.hostedPreview,
  );
  readonly api = new ApiClient(
    BUILD.apiUrl,
    this.auth,
    BUILD.version,
    () => syncReadiness(this.model.config, BUILD.version),
    () => !BUILD.hostedPreview,
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
    () => this.store,
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
  async runPrivacy(action: () => Promise<void>): Promise<void> {
    if (this.model.privacyBusy) return;
    this.patch({ privacyBusy: true });
    try {
      await action();
    } catch (error) {
      if (
        !(error instanceof IntegrityError || error instanceof ApiError) ||
        !["WORKSPACE_CHANGED", "AUTH_CHANGED"].includes(error.code)
      )
        this.report(error);
    } finally {
      this.patch({ privacyBusy: false });
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
      const identity = BUILD.hostedPreview ? null : await this.auth.restore();
      if (identity)
        this.patch({ identity, locked: true, loading: false, route: "home" });
      else {
        await this.openGuest();
        this.patch({ loading: false });
      }
      if (!BUILD.hostedPreview)
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
          state.rawRecordingStatuses ??= {};
          state.rawRecordingFences ??= {};
          state.historyIndex ??= [];
          state.historyCursor ??= null;
          state.checks = state.checks.map((c) =>
            c.frozen ? c : interruptStartedAttempts(c, now()),
          );
          if (opened.reconcileRaw)
            state = await opened.reconcileRaw(state, now());
          await opened.save(state);
          current();
          this.store = opened;
          this.patch({
            state,
            locked: false,
            selectedCheck: null,
            rawStudyId: null,
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
    await this.activate(this.guestWorkspace(), 1, () => flow === this.authFlow);
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
  private guestWorkspace(): string {
    return `guest:${BUILD.environment}${BUILD.hostedPreview ? ":fictional-preview" : ""}`;
  }
  async resetStore(): Promise<void> {
    ++this.authFlow;
    this.authenticating = false;
    await this.stopActive("WORKSPACE_CHANGED");
    this.workspaceEpoch = newId();
    this.api.cancelAll();
    const name = this.model.identity
      ? this.accountWorkspace(this.model.identity)
      : this.guestWorkspace();
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
    raw?: { id: string; bytes: Uint8Array; current: () => boolean },
    maintainRaw = false,
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
        let next = change(this.model.state);
        const unknownRetirement = retiredWithoutReplacement(previous, next);
        if (raw) {
          if (!this.store.saveWithRaw)
            throw new IntegrityError(
              "ENCRYPTED_RAW_STORAGE_REQUIRED",
              "This native store cannot atomically protect recording bytes and their index.",
            );
          await this.store.saveWithRaw(
            next,
            raw.id,
            raw.bytes,
            () =>
              epoch === this.workspaceEpoch && scope.current() && raw.current(),
          );
        } else if (
          (maintainRaw || unknownRetirement) &&
          this.store.reconcileRaw
        )
          next = await this.store.reconcileRaw(next, now());
        else await this.store.save(next);
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
                rawStudyId: null,
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
    if (BUILD.hostedPreview)
      throw new IntegrityError(
        "HOSTED_PREVIEW_LOCAL_ONLY",
        "Sign-in is unavailable in the fictional preview. Guest examples never connect to an account.",
      );
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
    await this.commit(
      (state) => {
        const next = changed
          ? quarantineGeneration(state, cap.data_generation, now())
          : clone(state);
        next.generation = cap.data_generation;
        next.capabilities = cap;
        return next;
      },
      undefined,
      changed,
    );
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
            rawStudyId: null,
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
    if (BUILD.hostedPreview && kind !== "guest_demo")
      throw new IntegrityError(
        "HOSTED_PREVIEW_FICTIONAL_ONLY",
        "This preview creates isolated fictional guest checks only.",
      );
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
  async beginStudyCheck(
    studyId: string,
    protocolId: string,
    contextConfirmed: boolean,
  ): Promise<void> {
    this.requireWritable();
    if (!this.model.identity || BUILD.hostedPreview)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Research capture requires an owned account and fresh online study authorization.",
      );
    const scope = this.scope();
    await scope.wait(this.refreshCapabilities());
    await scope.wait(this.refreshStudies());
    const study = this.model.state!.studies.find(
      (study) => study.study_id === studyId,
    );
    if (
      !study ||
      !assessStudyConsent(study).current ||
      study.local_withdrawal_pending
    )
      throw new IntegrityError(
        "CURRENT_STUDY_CONSENT_REQUIRED",
        "Confirm the current approved study document before starting research capture.",
      );
    const configurations = configurationsFor(
      this.model.state!.capabilities,
      studyId,
      protocolId,
    );
    if (!configurations.length || configurations.length > 16)
      throw new IntegrityError(
        "CAPTURE_UNAVAILABLE",
        "No current approved protocol with an installed capture adapter is available.",
      );
    const check = createCheck(this.model.state!, {
      now: now(),
      id: newId,
      kind: "measurement",
      accountRef: this.model.identity.accountRef,
      contextConfirmed,
    });
    check.snapshot.mode = "controlled_research";
    check.snapshot.study_id = studyId;
    check.snapshot.protocol_id = protocolId;
    check.context.protocol_id = protocolId;
    check.context.configuration_refs = [
      ...new Map(
        configurations.map((config) => [
          config.configuration_id,
          {
            id: config.configuration_id,
            version: config.configuration_version,
            sha256: config.configuration_hash,
            scope: "measurement_collection",
          },
        ]),
      ).values(),
    ];
    if (this.model.state!.profile.sync !== "synced")
      check.context.profile_version_id = null;
    const association = this.device.snapshot().association;
    if (
      association?.source === "prototype_sensor" &&
      association.verifiedBindingId
    ) {
      check.snapshot.device = {
        device_id: association.deviceId,
        boot_id: association.bootId,
        hardware_revision: association.hardwareRevision,
        firmware_version: association.firmwareVersion,
      };
      check.context.device_associations = [
        {
          ...check.snapshot.device,
          binding_id: association.verifiedBindingId,
          clock_evidence_ref: null,
        },
      ];
    }
    check.acquisition = {
      register_key: newId(),
      context_key: newId(),
      registered: false,
      context_registered: false,
      attempts: {},
    };
    await scope.wait(this.commit((state) => replaceCheck(state, check)));
    this.patch({
      route: "check",
      selectedCheck: check.id,
      pendingReplacement: null,
      message:
        "Research context saved on this device. Each acquisition requires a fresh online grant; no measurement or raw upload is queued.",
    });
  }
  async refreshDeviceBindings(): Promise<void> {
    if (!this.model.identity || BUILD.hostedPreview) return;
    const scope = this.scope(),
      response = await scope.wait(
        this.api.request<JsonObject>("/v1/device-bindings"),
      );
    if (
      !Array.isArray(response.value.items) ||
      response.value.items.length > 500
    )
      throw new IntegrityError(
        "DEVICE_BINDINGS_UNSUPPORTED",
        "The owned device binding list is unsupported.",
      );
    const items = response.value.items.map((value) => {
      const item = requireObject(value);
      if (
        typeof item.binding_id !== "string" ||
        !["active", "revoked"].includes(String(item.state)) ||
        typeof item.device_id !== "string" ||
        typeof item.key_id !== "string" ||
        typeof item.key_active !== "boolean"
      )
        throw new IntegrityError(
          "DEVICE_BINDINGS_UNSUPPORTED",
          "A device binding receipt is incomplete.",
        );
      return clone(item) as JsonObject;
    });
    await scope.wait(
      this.commit((state) => ({ ...state, deviceBindings: items })),
    );
  }
  async bindConnectedReader(
    recovery = 0,
    selected?: {
      deviceId: string;
      keyId: string;
      hardwareRevision: string;
      firmwareVersion: string;
    },
  ): Promise<void> {
    this.requireWritable();
    if (!this.model.identity || BUILD.hostedPreview)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "A signed reader must be bound to an authenticated owner.",
      );
    const scope = this.scope(),
      association = this.device.snapshot().association;
    if (
      !association ||
      association.source !== "prototype_sensor" ||
      this.device.snapshot().state !== "connected_reader"
    )
      throw new IntegrityError(
        "SIGNED_READER_REQUIRED",
        "Connect a reader advertising the documented signed protocol first.",
      );
    const cap = association.capabilities as PhysicalCapabilities;
    const generation = this.model.state!.generation;
    const readerTarget = selected ?? {
      deviceId: association.deviceId,
      keyId: cap.key_id,
      hardwareRevision: association.hardwareRevision,
      firmwareVersion: association.firmwareVersion,
    };
    const assertReader = () => {
      scope.assertCurrent();
      const current = this.device.snapshot(),
        reader = current.association;
      if (
        current.state !== "connected_reader" ||
        !reader ||
        reader.source !== "prototype_sensor" ||
        reader.deviceId !== readerTarget.deviceId ||
        (reader.capabilities as PhysicalCapabilities).key_id !==
          readerTarget.keyId ||
        reader.hardwareRevision !== readerTarget.hardwareRevision ||
        reader.firmwareVersion !== readerTarget.firmwareVersion
      )
        throw new IntegrityError(
          "BINDING_TARGET_CHANGED",
          "The selected reader changed. Select and confirm the connected reader again.",
        );
    };
    assertReader();
    let intent = this.model.state!.deviceBindingIntent;
    if (
      !intent ||
      intent.device_id !== association.deviceId ||
      intent.key_id !== cap.key_id
    ) {
      const observedKey = intent?.completion_key;
      intent = {
        device_id: association.deviceId,
        key_id: cap.key_id,
        challenge_key: newId(),
        completion_key: newId(),
        challenge: null,
        signature: null,
      };
      await scope.wait(
        this.commit((state) => {
          assertReader();
          if (state.deviceBindingIntent?.completion_key !== observedKey)
            throw new IntegrityError(
              "BINDING_TARGET_CHANGED",
              "A newer binding request was retained. Confirm that request before retrying.",
            );
          return { ...state, deviceBindingIntent: intent };
        }),
      );
    }
    const target = {
      completionKey: intent.completion_key,
    };
    const assertTarget = () => {
      assertReader();
      if (
        this.model.state!.deviceBindingIntent?.completion_key !==
        target.completionKey
      )
        throw new IntegrityError(
          "BINDING_TARGET_CHANGED",
          "The selected reader or binding request changed. Select and confirm the connected reader again.",
        );
    };
    const challenge = intent.challenge
      ? { value: intent.challenge }
      : await scope.wait(
          this.api.request<JsonObject>("/v1/device-bindings/challenges", {
            method: "POST",
            body: { device_id: association.deviceId, key_id: cap.key_id },
            generation,
            key: intent.challenge_key,
          }),
        );
    assertTarget();
    if (!intent.challenge) {
      await scope.wait(
        this.commit((state) => {
          assertTarget();
          return {
            ...state,
            deviceBindingIntent: {
              ...intent!,
              challenge: clone(challenge.value),
            },
          };
        }),
      );
      intent = this.model.state!.deviceBindingIntent!;
    }
    if (
      challenge.value.domain !== "OTGD-BIND-v1\n" ||
      challenge.value.signature_format !== "ECDSA_P256_SHA256_DER_BASE64"
    )
      throw new IntegrityError(
        "BINDING_DOMAIN_UNSUPPORTED",
        "The device proof transcript is unsupported.",
      );
    const storedTranscript = requireObject(challenge.value.transcript);
    if (
      storedTranscript.environment !== BUILD.environment ||
      storedTranscript.owner_ref !== this.model.identity.accountRef ||
      storedTranscript.data_generation !== generation ||
      storedTranscript.device_id !== association.deviceId ||
      storedTranscript.key_id !== cap.key_id ||
      storedTranscript.hardware_revision !== cap.hardware_revision ||
      storedTranscript.firmware_version !== cap.firmware_version ||
      storedTranscript.challenge_id !== challenge.value.challenge_id
    )
      throw new IntegrityError(
        "BINDING_OWNER_MISMATCH",
        "The retained challenge belongs to another owner, generation or reader.",
      );
    const restart = async () => {
      assertTarget();
      if (recovery >= 1)
        throw new IntegrityError(
          "BINDING_RECOVERY_REQUIRED",
          "The reader proof could not be recovered. Reconnect the provisioned reader and retry.",
        );
      await scope.wait(
        this.commit((state) => {
          assertTarget();
          const next = clone(state);
          delete next.deviceBindingIntent;
          return next;
        }),
      );
      assertReader();
      await scope.wait(this.bindConnectedReader(recovery + 1, readerTarget));
    };
    const complete = async (value: unknown) => {
      assertTarget();
      const receipt = readerBinding(value, cap);
      this.device.installBinding(receipt, {
        environment: BUILD.environment,
        owner_ref: this.model.identity!.accountRef,
        data_generation: generation,
      });
      await scope.wait(this.refreshDeviceBindings());
      await scope.wait(
        this.commit((state) => {
          assertTarget();
          const next = clone(state);
          delete next.deviceBindingIntent;
          return next;
        }),
      );
      this.patch({
        message:
          "The service verified the reader's device-owned signature and recorded this binding. Each measurement still requires current device calibration and a fresh approved configuration.",
      });
    };
    if (intent.signature) {
      // Reconcile the immutable accepted receipt before freshness checks. The
      // server's same-key replay independently verifies current owner authority.
      try {
        const response = await scope.wait(
          this.api.request<unknown>("/v1/device-bindings", {
            method: "POST",
            body: {
              challenge_id: String(storedTranscript.challenge_id),
              signature: intent.signature,
            },
            generation,
            key: intent.completion_key,
          }),
        );
        await complete(response.value);
        return;
      } catch (error) {
        const code =
          error && typeof error === "object" && "code" in error
            ? String(error.code)
            : "";
        if (
          code === "CHALLENGE_EXPIRED_OR_USED" ||
          code === "PHYSICAL_CAPTURE_SCOPE"
        ) {
          await restart();
          return;
        }
        throw error;
      }
    }
    if (
      typeof storedTranscript.expires_at === "string" &&
      Date.parse(storedTranscript.expires_at) <= Date.now()
    ) {
      await restart();
      return;
    }
    const transcript = bindingTranscript(challenge.value.transcript, cap);
    if (
      transcript.challenge_id !== challenge.value.challenge_id ||
      transcript.environment !== BUILD.environment ||
      transcript.owner_ref !== this.model.identity.accountRef ||
      transcript.data_generation !== generation
    )
      throw new IntegrityError(
        "BINDING_OWNER_MISMATCH",
        "The challenge belongs to another owner, environment or data generation.",
      );
    const proof = intent.signature
      ? { signature: intent.signature }
      : await scope.wait(this.device.requestBindingProof(transcript));
    assertTarget();
    if (!intent.signature) {
      await scope.wait(
        this.commit((state) => {
          assertTarget();
          return {
            ...state,
            deviceBindingIntent: { ...intent!, signature: proof.signature },
          };
        }),
      );
      intent = this.model.state!.deviceBindingIntent!;
    }
    const response = await scope.wait(
      this.api.request<unknown>("/v1/device-bindings", {
        method: "POST",
        body: {
          challenge_id: transcript.challenge_id,
          signature: proof.signature,
        },
        generation,
        key: intent.completion_key,
      }),
    );
    await complete(response.value);
  }
  async forgetReaderBinding(bindingId: string): Promise<void> {
    if (!this.model.identity)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "An owned device binding is required.",
      );
    const scope = this.scope(),
      stop = this.stopActive("USER_CANCELED");
    this.api.cancelAll();
    await scope.wait(this.device.forget());
    await scope.wait(stop);
    await scope.wait(
      this.commit((state) =>
        queueMutation(
          state,
          "device_unbind",
          { binding_id: bindingId },
          newId,
          now(),
        ),
      ),
    );
    const intent = this.model.state!.queue.find(
      (q) =>
        q.kind === "device_unbind" &&
        q.body.binding_id === bindingId &&
        q.state !== "synced",
    );
    if (intent) await scope.wait(this.sync.run(intent.id, true));
    await scope.wait(this.refreshDeviceBindings());
    this.patch({
      message:
        intent &&
        this.model.state!.queue.find((q) => q.id === intent.id)?.state !==
          "synced"
          ? "Local reader disconnected. Remote forget remains pending; retry the exact request from privacy controls."
          : "Local reader disconnected and the service binding was revoked.",
    });
  }
  private async armApprovedCapture(
    check: CheckRecord,
    channel: AcquisitionChannel,
    current: () => boolean,
    rawKind?: RawKind,
  ): Promise<{
    attemptId: string;
    config: ApprovedConfiguration;
    grant: JsonObject;
  }> {
    const scope = this.scope();
    this.api.cancelAll();
    await scope.wait(this.sync.whenIdle());
    await scope.wait(this.auth.whenRefreshSettled());
    await scope.wait(this.writes.catch(() => {}));
    if (!current())
      throw new IntegrityError(
        "CAPTURE_STOPPED",
        "Capture was stopped before authorization.",
      );
    await scope.wait(this.refreshCapabilities());
    await scope.wait(this.refreshStudies());
    const study = this.model.state!.studies.find(
      (study) => study.study_id === check.snapshot.study_id,
    );
    if (
      !study ||
      !assessStudyConsent(study).current ||
      study.local_withdrawal_pending
    )
      throw new IntegrityError(
        "CURRENT_STUDY_CONSENT_REQUIRED",
        "The current study consent no longer authorizes acquisition.",
      );
    const config = configurationFor(
      check,
      this.model.state!.capabilities,
      channel,
    );
    let rawAuthority;
    if (rawKind) {
      const previous =
        this.model.state!.rawRecordingStatuses[check.snapshot.study_id!];
      if (!previous?.receipt_id || !previous.choices[rawKind].record)
        throw new IntegrityError(
          "OPTIONAL_RAW_CONSENT_REQUIRED",
          "Review and confirm separate recording choices before this acquisition.",
        );
      await scope.wait(this.refreshRawRecordings(check.snapshot.study_id!));
      const status =
        this.model.state!.rawRecordingStatuses[check.snapshot.study_id!];
      if (
        !status ||
        status.receipt_id !== previous.receipt_id ||
        status.policy?.sha256 !== previous.policy?.sha256 ||
        status.policy?.raw_notice.sha256 !== previous.policy?.raw_notice.sha256
      )
        throw new IntegrityError(
          "RAW_POLICY_CHANGED",
          "Optional recording permission changed. Review the exact current policy and consent before starting.",
        );
      rawAuthority = {
        kind: rawKind,
        status,
        fences:
          this.model.state!.rawRecordingFences[check.snapshot.study_id!] ?? [],
      };
    }
    const association = this.device.snapshot().association;
    const usesReader = !["task", "eyes"].includes(channel);
    if (
      usesReader &&
      (!association ||
        association.source !== "prototype_sensor" ||
        !association.verifiedBindingId ||
        !check.context.device_associations.some(
          (ref) =>
            ref.binding_id === association.verifiedBindingId &&
            ref.device_id === association.deviceId &&
            ref.boot_id === association.bootId,
        ))
    )
      throw new IntegrityError(
        "FROZEN_DEVICE_BINDING_REQUIRED",
        "Bind the approved reader before Start check. A different reader or reboot requires a new check.",
      );
    const armed = startAttempt(
      this.check!,
      channel === "ecg" ? "cardiac" : channel,
      now(),
      newId,
      "prototype_sensor",
      config.configuration_id,
      config.configuration_hash,
      channel === "cardiac" ? "ppg" : channel === "ecg" ? "ecg" : undefined,
    );
    armed.check.acquisition ??= {
      register_key: newId(),
      context_key: newId(),
      registered: false,
      context_registered: false,
      attempts: {},
    };
    armed.check.acquisition.attempts[armed.attempt.attempt_id] = {
      start_key: newId(),
      grant_key: newId(),
      invoke_key: newId(),
      terminal_key: newId(),
      attestation_key: newId(),
      started_body: clone(armed.attempt) as unknown as JsonObject,
      remote_revision: 0,
      authorization: null,
    };
    await scope.wait(this.commit((state) => replaceCheck(state, armed.check)));
    const path = `/v1/sessions/${check.id}`,
      ledger = armed.check.acquisition;
    const save = async (change: (check: CheckRecord) => void) =>
      scope.wait(
        this.commit((state) => {
          if (!current())
            throw new IntegrityError(
              "CAPTURE_STOPPED",
              "Capture stopped before committing authorization.",
            );
          const next = clone(state),
            record = next.checks.find((c) => c.id === check.id)!;
          change(record);
          return next;
        }),
      );
    try {
      if (!ledger.registered) {
        const response = await scope.wait(
          this.api.request<JsonObject>("/v1/sessions", {
            method: "POST",
            body: {
              session_id: check.id,
              mode: check.snapshot.mode,
              protocol_id: check.snapshot.protocol_id,
              study_id: check.snapshot.study_id,
              supersedes_session_id: check.snapshot.supersedes_session_id,
            },
            generation: check.generation,
            key: ledger.register_key,
          }),
        );
        await save((record) => {
          record.acquisition!.registered = true;
          record.remote_revision = Number(response.value.revision);
          record.remote_etag = response.etag ?? `"${response.value.revision}"`;
        });
      }
      if (!ledger.context_registered) {
        const response = await scope.wait(
          this.api.request<JsonObject>(`${path}/context`, {
            method: "PUT",
            body: check.context,
            generation: check.generation,
            key: ledger.context_key,
            etag: '"0"',
          }),
        );
        if (response.value.sha256 !== digest(check.context))
          throw new IntegrityError(
            "CONTEXT_ACK_MISMATCH",
            "The service did not acknowledge this frozen context.",
          );
        await save((record) => {
          record.acquisition!.context_registered = true;
        });
      }
      const attemptLedger = ledger.attempts[armed.attempt.attempt_id]!;
      const persisted = await scope.wait(
        this.api.request<JsonObject>(
          `${path}/attempts/${armed.attempt.attempt_id}`,
          {
            method: "PUT",
            body: attemptLedger.started_body,
            generation: check.generation,
            key: attemptLedger.start_key,
            etag: '"0"',
          },
        ),
      );
      if (persisted.value.sha256 !== digest(attemptLedger.started_body))
        throw new IntegrityError(
          "ATTEMPT_ACK_MISMATCH",
          "The service acknowledged different capture metadata.",
        );
      await save((record) => {
        record.acquisition!.attempts[
          armed.attempt.attempt_id
        ]!.remote_revision = Number(persisted.value.revision);
      });
      const bindingId = usesReader ? association!.verifiedBindingId : null,
        deviceId = usesReader ? association!.deviceId : null;
      const response = await scope.wait(
        this.api.request<unknown>(`${path}/capture-authorizations`, {
          method: "POST",
          body: {
            attempt_id: armed.attempt.attempt_id,
            channel,
            binding_id: bindingId,
            device_id: deviceId,
            configuration_id: config.configuration_id,
            configuration_hash: config.configuration_hash,
            raw_recording_kind: rawKind ?? null,
          },
          generation: check.generation,
          key: attemptLedger.grant_key,
        }),
      );
      const grant = verifyCaptureGrant(
        response.value,
        armed.check,
        armed.attempt.attempt_id,
        channel,
        config,
        bindingId,
        deviceId,
        rawAuthority,
      );
      await save((record) => {
        record.acquisition!.attempts[armed.attempt.attempt_id]!.authorization =
          grant;
      });
      const prepared = usesReader
        ? await scope.wait(
            this.device.prepareAuthorizedCapture({
              sessionId: check.id,
              attemptId: armed.attempt.attempt_id,
              captureId: armed.attempt.record_id,
              workspaceEpoch: this.workspaceEpoch,
            }),
          )
        : null;
      const bootId = prepared?.device_boot_id ?? null;
      if (usesReader && bootId !== association!.bootId)
        throw new IntegrityError(
          "DEVICE_REBOOTED",
          "The reader rebooted after the frozen check began. Start a new check.",
        );
      const invoked = await scope.wait(
        this.api.request<unknown>(
          `${path}/capture-authorizations/${grant.authorization_id}/start`,
          {
            method: "POST",
            body: {
              attempt_id: armed.attempt.attempt_id,
              device_boot_id: bootId,
              device_nonce: prepared?.device_nonce ?? null,
            },
            generation: check.generation,
            key: attemptLedger.invoke_key,
          },
        ),
      );
      verifyCaptureStart(
        invoked.value,
        grant,
        armed.attempt.attempt_id,
        bootId,
      );
      if (usesReader) {
        const reply = requireObject(invoked.value);
        grant.server_start = reply.server_start as JsonObject;
        await save((record) => {
          record.acquisition!.attempts[
            armed.attempt.attempt_id
          ]!.authorization = clone(grant);
        });
      }
      if (!current())
        throw new IntegrityError(
          "CAPTURE_STOPPED",
          "Capture was stopped before hardware invocation.",
        );
      return { attemptId: armed.attempt.attempt_id, config, grant };
    } catch (error) {
      await this.abandonArmedCapture(check.id, armed.attempt.attempt_id);
      throw error;
    }
  }
  async captureReader(
    channel: PhysicalChannel,
    recordRaw = false,
  ): Promise<void> {
    if (recordRaw && channel !== "ecg")
      throw new IntegrityError(
        "RAW_CHANNEL_UNAVAILABLE",
        "This optional recording adapter is available only for the approved ECG channel.",
      );
    if (recordRaw && (!this.store?.saveWithRaw || !this.store.deleteRaw))
      throw new IntegrityError(
        "ENCRYPTED_RAW_STORAGE_REQUIRED",
        "Optional ECG recording requires unlocked encrypted native storage before acquisition.",
      );
    this.requireWritable();
    const check = this.check;
    if (!check || check.frozen)
      throw new IntegrityError(
        "CHECK_REQUIRED",
        "Start an authorized draft check first.",
      );
    await this.withCaptureIntent(check, async (current) => {
      const authorization = await this.armApprovedCapture(
        check,
        channel === "ppg" ? "cardiac" : channel,
        current,
        recordRaw ? "ecg_waveform" : undefined,
      );
      const association = this.device.snapshot().association!,
        cap = association.capabilities as PhysicalCapabilities;
      const attempt = this.check!.attempts.find(
        (a) => a.attempt_id === authorization.attemptId,
      )!;
      try {
        const captured = await this.device.captureAuthorized(
          channel,
          {
            sessionId: check.id,
            attemptId: attempt.attempt_id,
            captureId: attempt.record_id,
            workspaceEpoch: this.workspaceEpoch,
          },
          {
            environment: BUILD.environment,
            owner_ref: this.model.identity!.accountRef,
            data_generation: check.generation,
            authorization_id: String(authorization.grant.authorization_id),
            binding_id: association.verifiedBindingId!,
            device_id: association.deviceId,
            key_id: cap.key_id,
            configuration_id: authorization.config.configuration_id,
            configuration_hash: authorization.config.configuration_hash,
            max_duration_ms: Number(
              authorization.grant.configuration_max_duration_ms,
            ),
            server_start: authorization.grant
              .server_start as unknown as SignedStartToken,
            capture_context_sha256: digest(check.context),
          },
        );
        if (!current()) {
          await this.abandonArmedCapture(check.id, attempt.attempt_id);
          return;
        }
        const projection = captured.normalized_payload;
        const component =
          channel === "saliva" ? requireObject(projection.sample) : projection;
        const valid =
          channel === "alcohol"
            ? [
                "quantified",
                "not_detected",
                "below_loq",
                "above_range",
              ].includes(String(component.qualifier))
            : component.status === "valid";
        await this.commit((state) => {
          if (!current())
            throw new IntegrityError(
              "CAPTURE_STOPPED",
              "A late reader reply cannot settle a stopped capture.",
            );
          const record = state.checks.find((c) => c.id === check.id)!;
          const next = settleAttempt(
            record,
            attempt.attempt_id,
            projection,
            valid ? "valid" : "invalid",
            captured.endedAt,
            Array.isArray(component.quality_flags)
              ? (component.quality_flags as string[])
              : [],
            {},
          );
          next.attempts.find(
            (a) => a.attempt_id === attempt.attempt_id,
          )!.attestation_refs = [captured.attestation_id];
          next.attestations ??= {};
          next.attestations[attempt.attempt_id] = {
            attestation_id: captured.attestation_id,
            envelope: captured.envelope as unknown as JsonObject,
            signature: captured.signature,
            normalized_payload: captured.normalized_payload,
          };
          return replaceCheck(state, next);
        });
        if (captured.rawRecording) {
          if (!recordRaw)
            throw new IntegrityError(
              "UNREQUESTED_RAW_RECORDING",
              "Feature-only acquisition cannot retain raw recording.",
            );
          await this.retainRawRecording(
            check.id,
            attempt.attempt_id,
            "ecg_waveform",
            captured.rawRecording,
            authorization.grant.raw_recording_permission,
          );
        }
        this.patch({
          message:
            "Device-signed measurement saved locally. Its signature will be independently verified by the service only when you explicitly upload the saved check. No raw upload was queued.",
        });
      } catch (error) {
        await this.abandonArmedCapture(check.id, attempt.attempt_id);
        if (current()) throw error;
      }
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
      if (!this.model.activeTask && !this.model.activeEye)
        this.acquiring = false;
    }
  }
  private async abandonArmedCapture(
    checkId: string,
    attemptId: string,
    noFrameReason?: string,
  ): Promise<void> {
    if (!this.model.state || this.model.locked) return;
    await this.commit((state) => {
      const check = state.checks.find((c) => c.id === checkId);
      const original = check?.attempts.find(
        (a) => a.attempt_id === attemptId && a.status === "started",
      );
      if (!check || !original) return state;
      const next = interruptStartedAttempts(check, now());
      if (noFrameReason && original.component === "eyes") {
        const attempt = next.attempts.find((a) => a.attempt_id === attemptId)!,
          projection = requireObject(
            attempt.component_metadata.projection,
          ) as JsonObject;
        projection.started_at = null;
        projection.ended_at = null;
        projection.quality_flags = [noFrameReason];
        projection.capture_config_id = original.configuration_id;
        const material = requireObject(
          check.acquisition?.attempts[attemptId]?.authorization
            ?.configuration_material ?? {},
        );
        projection.camera_id =
          typeof material.camera_id === "string"
            ? material.camera_id
            : "unavailable";
        projection.frame_rate_hz = null;
        projection.scale_basis =
          material.scale_basis === "millimeters"
            ? "calibrated_mm"
            : "normalized";
        projection.baseline_diameter_mm = null;
        projection.relative_constriction = null;
        projection.latency_ms = null;
        projection.raw_artifact_id = null;
        attempt.started_at = null;
        attempt.ended_at = null;
        attempt.quality_flags = [noFrameReason];
        attempt.component_metadata = {
          armed_at: original.started_at,
          native_result: null,
          projection,
        };
        next.snapshot.eyes = clone(projection) as typeof next.snapshot.eyes;
      }
      return replaceCheck(state, next);
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
  async startEyeCapture(recordRaw = false): Promise<void> {
    this.requireWritable();
    if (recordRaw && (!this.store?.saveWithRaw || !this.store.deleteRaw))
      throw new IntegrityError(
        "ENCRYPTED_RAW_STORAGE_REQUIRED",
        "Optional ROI recording requires unlocked encrypted native storage before acquisition.",
      );
    if (BUILD.hostedPreview || !getEyeCaptureAvailability().available)
      throw new IntegrityError(
        "NATIVE_CAMERA_MODULE_UNAVAILABLE",
        "Install an approved native build with the optical acquisition adapter. Browser previews do not acquire eye measurements.",
      );
    const check = this.check;
    if (!check || check.frozen)
      throw new IntegrityError(
        "CHECK_REQUIRED",
        "Start an approved research check first.",
      );
    await this.withCaptureIntent(check, async (current) => {
      const approved = await this.armApprovedCapture(
        check,
        "eyes",
        current,
        recordRaw ? "eye_video" : undefined,
      );
      if (
        approved.config.software_adapter_id !== "optical_roi_v1" ||
        !approved.config.supported_os_versions?.length ||
        !approved.config.supported_native_builds?.length
      ) {
        await this.abandonArmedCapture(check.id, approved.attemptId);
        throw new IntegrityError(
          "OPTICAL_CONFIGURATION_UNAVAILABLE",
          "The approved optical adapter requires exact reviewed phone, OS and native build inventories.",
        );
      }
      if (!current()) {
        await this.abandonArmedCapture(check.id, approved.attemptId);
        return;
      }
      const attempt = this.check!.attempts.find(
        (a) => a.attempt_id === approved.attemptId,
      )!;
      const active: ActiveEye = {
        runId: attempt.record_id,
        attemptId: attempt.attempt_id,
        checkId: check.id,
        epoch: this.workspaceEpoch,
        configurationId: approved.config.configuration_id,
        options: {
          run_id: attempt.record_id,
          workspace_epoch: this.workspaceEpoch,
          authorization_id: String(approved.grant.authorization_id),
          configuration_sha256: approved.config.configuration_hash,
          material_json: canonicalJson(approved.grant.configuration_material),
          supported_phone_models: approved.config.supported_phone_models,
          supported_os_versions: approved.config.supported_os_versions!,
          supported_native_builds: approved.config.supported_native_builds!,
          raw_recording_permission: recordRaw
            ? (approved.grant
                .raw_recording_permission as unknown as RawPermission)
            : null,
        },
      };
      this.eyeRuns.set(active.runId, active);
      this.patch({
        activeEye: active,
        eyeProgress: "Preparing approved camera",
      });
    });
  }
  async completeEyeCapture(
    result: EyeCaptureComplete,
    origin?: ActiveEye,
  ): Promise<void> {
    const active = origin ?? this.eyeRuns.get(result.run_id);
    if (
      !active ||
      active.epoch !== this.workspaceEpoch ||
      result.workspace_epoch !== active.epoch ||
      result.run_id !== active.runId
    )
      return;
    const view = this.eyeView;
    try {
      return await this.terminalEvidence.persist(
        active.runId,
        digest({
          native_result: result.native_result,
          status: result.status,
          reason: result.reason ?? null,
        }),
        async () => {
          if (
            result.authorization_id !== undefined &&
            result.authorization_id !== active.options.authorization_id
          )
            throw new IntegrityError(
              "OPTICAL_AUTHORIZATION_MISMATCH",
              "The native camera completion belongs to another authorization.",
            );
          if (!result.native_result) {
            if (result.status !== "invalid" || result.raw_recording !== null)
              throw new IntegrityError(
                "OPTICAL_TERMINAL_INVALID",
                "An optical completion without acquired native evidence must be invalid and contain no recording.",
              );
            await this.abandonArmedCapture(
              active.checkId,
              active.attemptId,
              (result.reason ?? "CAMERA_NOT_STARTED").slice(0, 64),
            );
          } else {
            const native = requireObject(result.native_result),
              material = requireObject(
                JSON.parse(active.options.material_json),
              );
            if (native.status !== result.status)
              throw new IntegrityError(
                "OPTICAL_STATUS_MISMATCH",
                "The native terminal status contradicts its immutable frame evidence.",
              );
            const projection = projectNativeEye(native, {
              runId: active.runId,
              epoch: active.epoch,
              authorizationId: active.options.authorization_id,
              configurationId: active.configurationId,
              configurationHash: active.options.configuration_sha256,
              material: material as JsonObject,
            });
            await this.commit((state) => {
              if (active.epoch !== this.workspaceEpoch)
                throw new IntegrityError(
                  "WORKSPACE_CHANGED",
                  "Optical evidence belongs to a retired workspace.",
                );
              const check = state.checks.find((c) => c.id === active.checkId);
              if (!check)
                throw new IntegrityError(
                  "CHECK_REQUIRED",
                  "The original optical check is unavailable.",
                );
              return replaceCheck(
                state,
                settleAttempt(
                  check,
                  active.attemptId,
                  projection,
                  result.status,
                  String(projection.ended_at),
                  projection.quality_flags,
                  { native_result: native as JsonObject },
                ),
              );
            });
            if (result.raw_recording) {
              if (
                !active.options.raw_recording_permission ||
                !active.options.raw_recording_permission.record
              )
                throw new IntegrityError(
                  "UNREQUESTED_RAW_RECORDING",
                  "The native camera returned a recording without an explicit fresh recording grant.",
                );
              const studyId = this.model.state!.checks.find(
                (check) => check.id === active.checkId,
              )?.snapshot.study_id;
              if (
                studyId &&
                !this.model.state!.rawRecordingFences[studyId]?.includes(
                  "eye_video",
                )
              )
                await this.retainRawRecording(
                  active.checkId,
                  active.attemptId,
                  "eye_video",
                  result.raw_recording,
                  active.options.raw_recording_permission,
                );
            }
          }
          this.eyeRuns.delete(active.runId);
          this.acquiring = false;
          if (this.model.activeEye?.runId === active.runId)
            this.patch({ activeEye: null, eyeProgress: null });
          this.patch({
            message:
              result.status === "valid"
                ? "Optical ROI evidence saved locally. Physical illumination timing remains unmeasured; no impairment or driving-safety claim is available."
                : "Eye acquisition ended invalid. Its evidence is retained; retry creates a new attempt.",
          });
        },
      );
    } finally {
      if (result.raw_recording && view)
        await view
          .releaseRaw(active.runId, result.raw_recording.sha256)
          .catch(() => {});
    }
  }
  updateEyeProgress(
    runId: string,
    epoch: string,
    frames: number,
    maximum: number,
  ): void {
    if (
      this.model.activeEye?.runId === runId &&
      epoch === this.workspaceEpoch &&
      !this.model.activeEye.stopping
    )
      this.patch({ eyeProgress: `${frames} / ${maximum} bounded ROI frames` });
  }
  async startNativeTask(): Promise<void> {
    if (BUILD.hostedPreview)
      throw new IntegrityError(
        "HOSTED_PREVIEW_FICTIONAL_ONLY",
        "Real reaction taps are unavailable in this fictional preview.",
      );
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
      let attempt;
      if (check.snapshot.mode === "controlled_research") {
        const approved = await this.armApprovedCapture(check, "task", current);
        if (
          approved.config.configuration_hash !== TASK_CONFIGURATION_SHA256 ||
          approved.config.software_adapter_id !== "task_native_v1"
        )
          throw new IntegrityError(
            "TASK_CONFIGURATION_UNSUPPORTED",
            "The approved task configuration differs from this native implementation.",
          );
        attempt = this.check!.attempts.find(
          (a) => a.attempt_id === approved.attemptId,
        )!;
      } else {
        const armed = startAttempt(
          this.check!,
          "task",
          now(),
          newId,
          "prototype_sensor",
          TASK_CONFIGURATION_ID,
          TASK_CONFIGURATION_SHA256,
        );
        await this.commit((state) => replaceCheck(state, armed.check));
        attempt = armed.attempt;
      }
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
    const eye = this.model.activeEye,
      eyeView = this.eyeView;
    return this.stopRequests.run(
      active?.runId ?? eye?.runId ?? `device:${this.workspaceEpoch}`,
      async () => {
        // This call is deliberately first; a radio timeout cannot delay native UI-thread cancellation.
        const nativeStop =
          active && view
            ? view.cancel(active.runId, reason)
            : Promise.resolve(null);
        const eyeStop =
          eye && eyeView
            ? eyeView.cancel(eye.runId, reason)
            : Promise.resolve(null);
        if (eye)
          this.patch({
            eyeProgress: "Stopping camera immediately",
            activeEye: { ...eye, stopping: true },
          });
        const deviceStops = Promise.allSettled([
          this.device.cancelCapture(reason),
          this.device.stopScan(),
        ]);
        try {
          const eyeReceipt = await eyeStop;
          if (eye) {
            if (eyeReceipt) await this.completeEyeCapture(eyeReceipt, eye);
            else if (!eyeView) {
              await this.abandonArmedCapture(eye.checkId, eye.attemptId);
              this.eyeRuns.delete(eye.runId);
              this.acquiring = false;
              this.patch({ activeEye: null, eyeProgress: null });
            }
            if (this.model.activeEye?.runId === eye.runId)
              throw new IntegrityError(
                "NATIVE_TERMINAL_PENDING",
                "The camera is stopped, but its terminal evidence has not been preserved. Retry End eye capture to save that same ended run.",
              );
          }
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
    if (
      (!this.model.busy || this.model.sheet?.interrupting) &&
      !this.model.privacyBusy
    )
      this.patch({ sheet: null });
  }
  async confirmSheet(secondary = false): Promise<void> {
    const sheet = this.model.sheet;
    if (!sheet) return;
    this.patch({ sheet: null });
    await (secondary ? sheet.secondary?.action() : sheet.action());
  }
  async uploadCheck(rawLocalIds: string[] = []): Promise<void> {
    this.requireWritable();
    const check = this.check;
    if (!check || !this.model.identity)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Account uploads require a signed-in owner. Guest records never migrate.",
      );
    await this.commit((s) =>
      queueCheck(s, check.id, newId, now(), rawLocalIds),
    );
    const queue = this.model.state!.queue.find(
      (q) => q.check_id === check.id && q.state !== "synced",
    );
    if (queue) await this.sync.run(queue.id, true);
  }
  async reconcilePrivacy(queueId: string): Promise<void> {
    const original = this.model.state?.queue.find((q) => q.id === queueId);
    if (
      !original ||
      !["deletion", "withdrawal", "raw_revocation", "device_unbind"].includes(
        original.kind,
      )
    )
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
  async refreshRawExportScopes(
    authorizationId?: string,
    artifactCursor?: string,
    authorizationCursor?: string,
  ): Promise<void> {
    if (!this.model.identity || BUILD.hostedPreview)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Separate raw export permissions require an owned account.",
      );
    if (authorizationCursor && (authorizationId || artifactCursor))
      throw new IntegrityError(
        "RAW_EXPORT_PAGE_INVALID",
        "Choose an authorization page or an exact source page.",
      );
    const scope = this.scope(),
      query = new URLSearchParams();
    if (authorizationId) query.set("authorization_id", authorizationId);
    if (artifactCursor) query.set("artifact_cursor", artifactCursor);
    if (authorizationCursor)
      query.set("authorization_cursor", authorizationCursor);
    const response = await scope.wait(
      this.api.request<unknown>(
        `/v1/privacy/raw-export-scopes${query.size ? "?" + query.toString() : ""}`,
      ),
    );
    const page = parseRawExportPage(response.value);
    await this.commit((state) => {
      const replacedIds = new Set(page.scopes.map((a) => a.authorization_id));
      if (authorizationId) replacedIds.add(authorizationId);
      const previous =
        authorizationCursor || authorizationId
          ? (state.rawExportAuthorities ?? []).filter(
              (a) => !replacedIds.has(a.authorization_id),
            )
          : [];
      if (previous.length + page.scopes.length > 100)
        throw new IntegrityError(
          "RAW_EXPORT_PAGE_LIMIT",
          "The bounded authorization inventory is full. Reload the first page.",
        );
      return {
        ...state,
        rawExportAuthorities: [...previous, ...page.scopes],
        rawExportArtifactCursors: {
          ...(authorizationCursor || authorizationId
            ? state.rawExportArtifactCursors
            : {}),
          ...Object.fromEntries(
            page.scopes.map((a) => [
              a.authorization_id,
              artifactCursor ?? null,
            ]),
          ),
        },
        rawExportNextCursor: authorizationId
          ? state.rawExportNextCursor
          : page.next_cursor,
      };
    });
  }
  async createExport(rawChoice?: {
    authorization_id: string;
    authority_sha256: string;
    notice_sha256: string;
    artifact_ids: string[];
  }): Promise<void> {
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
      if (rawChoice)
        throw new IntegrityError(
          "RAW_EXPORT_CLOUD_ONLY",
          "Authorized raw exports are prepared by the service; device exports retain their metadata-only scope.",
        );
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
    let rawScope: RawExportScope | null = null;
    if (rawChoice) {
      const cursor =
        state.rawExportArtifactCursors?.[rawChoice.authorization_id];
      await scope.wait(
        this.refreshRawExportScopes(
          rawChoice.authorization_id,
          cursor ?? undefined,
        ),
      );
      const authority = this.model.state!.rawExportAuthorities?.find(
        (a) => a.authorization_id === rawChoice.authorization_id,
      );
      if (
        !authority ||
        authority.authorization_sha256 !== rawChoice.authority_sha256 ||
        authority.export_notice.sha256 !== rawChoice.notice_sha256
      )
        throw new IntegrityError(
          "RAW_EXPORT_AUTHORITY_CHANGED",
          "Raw export authority or its exact notice changed. Review the new terms and selection.",
        );
      rawScope = confirmRawExport(
        authority,
        rawChoice.artifact_ids,
        entry.selection,
        now(),
      );
    }
    let body = {
      selection: entry.selection,
      format: "json_zip",
      include_raw: rawScope !== null,
      ...(rawScope ? { raw_scope: rawScope } : {}),
    } as unknown as JsonObject;
    const semantic = (value: JsonObject) =>
      digest({
        ...value,
        ...(value.raw_scope
          ? {
              raw_scope: {
                ...requireObject(value.raw_scope),
                acknowledged_at: null,
              },
            }
          : {}),
      });
    const unresolved = this.model.state!.queue.find(
      (q) =>
        q.kind === "export" &&
        ["queued", "retry_wait", "auth_required"].includes(q.state) &&
        semantic(q.body) === semantic(body),
    );
    if (unresolved) body = clone(unresolved.body);
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
      rawExport: job.raw_export,
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
    const stopped = this.stopActive("WITHDRAWAL");
    this.api.cancelAll();
    await this.commit((state) => {
      const next = queueMutation(
        state,
        "deletion",
        { scope, confirmation: true },
        newId,
        now(),
      );
      for (const study of next.studies)
        next.rawRecordingFences[String(study.study_id)] = [...RAW_KINDS];
      for (const raw of next.rawArtifacts ?? [])
        if (raw.state !== "deleted") {
          raw.state = "quarantined";
          raw.error = "DELETION_REQUESTED";
        }
      for (const q of next.queue)
        if (q.kind !== "deletion" && q.state !== "synced") {
          q.state = "blocked";
          q.error = "DELETION_REQUESTED";
        }
      return next;
    });
    await scopeGuard.wait(stopped);
    await scopeGuard.wait(this.purgeLocalRaw());
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
    await scope.wait(this.purgeLocalRaw());
    await scope.wait(
      this.commit((state) => ({
        ...emptyWorkspace(state.workspace, now(), state.generation),
        preferences: state.preferences,
        notice: state.notice,
        acknowledgedNotice: state.acknowledgedNotice,
        capabilities: state.capabilities,
        jobs: state.jobs.filter((job) => job.kind === "deletion"),
        rawRecordingFences: state.rawRecordingFences,
        queue: state.queue.filter((q) =>
          [
            "deletion",
            "withdrawal",
            "raw_revocation",
            "device_unbind",
          ].includes(q.kind),
        ),
      })),
    );
    scope.assertCurrent();
    this.patch({
      selectedCheck: null,
      rawStudyId: null,
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
    // This is the explicit confirmation time, before the browser reauthentication.
    // A lost receipt reuses the original durable intent instead of confirming again.
    const acknowledgedAt = now();
    const text = String(study.document_text ?? ""),
      hash = String(study.document_sha256 ?? "");
    if (
      !text ||
      digestText(text) !== hash ||
      typeof study.study_id !== "string" ||
      typeof study.invitation_id !== "string" ||
      typeof study.document_version !== "string"
    )
      throw new IntegrityError(
        "STUDY_DOCUMENT_INVALID",
        "Approved study information is missing or could not be verified.",
      );
    const studyId = study.study_id,
      invitationId = study.invitation_id,
      documentVersion = study.document_version;
    if (!(await this.signIn(true))) return;
    this.requireWritable();
    const scope = this.scope(),
      state = this.model.state!;
    const matches = (q: WorkspaceState["queue"][number]) =>
      q.kind === "consent" &&
      q.generation === state.generation &&
      q.body.study_id === studyId &&
      (q.body.payload as JsonObject)?.invitation_id === invitationId &&
      (q.body.payload as JsonObject)?.document_version === documentVersion &&
      (q.body.payload as JsonObject)?.document_sha256 === hash;
    let intent = state.queue.find(matches);
    if (!intent) {
      await scope.wait(
        this.commit((current) =>
          queueMutation(
            current,
            "consent",
            {
              study_id: studyId,
              payload: {
                invitation_id: invitationId,
                document_version: documentVersion,
                document_sha256: hash,
                accepted: true,
                acknowledged_at: acknowledgedAt,
              },
            },
            newId,
            acknowledgedAt,
          ),
        ),
      );
      intent = this.model.state!.queue.find(matches)!;
    }
    await scope.wait(this.sync.run(intent.id, true));
    scope.assertCurrent();
    if (
      this.model.state!.queue.find((q) => q.id === intent!.id)?.state !==
      "synced"
    ) {
      this.patch({
        message:
          "Your exact study consent confirmation is saved as a pending request. Its original timestamp and request identity will be retained when reconciling the receipt. Research access is not confirmed yet.",
      });
      return;
    }
    await scope.wait(this.refreshStudies());
    await this.refreshCapabilities();
    if (!scope.current()) return;
    this.patch({
      message:
        "Consent recorded for that exact study version. Measurement qualification remains separate.",
    });
  }
  async openRawRecordings(studyId: string): Promise<void> {
    if (!this.model.identity || BUILD.hostedPreview)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Raw recording choices require an owned account study. Guest previews never record or upload.",
      );
    const scope = this.scope();
    await scope.wait(this.stopActive("ROUTE_HIDDEN"));
    this.patch({ rawStudyId: studyId, route: "raw-recordings" });
    await scope.wait(this.refreshRawRecordings(studyId));
  }
  async refreshRawRecordings(
    studyId = this.model.rawStudyId,
    artifactCursor?: string,
  ): Promise<void> {
    if (!studyId || !this.model.identity) return;
    const scope = this.scope();
    const response = await scope.wait(
      this.api.request<unknown>(
        `/v1/studies/${encodeURIComponent(studyId)}/raw-recordings${artifactCursor ? `?artifact_cursor=${encodeURIComponent(artifactCursor)}` : ""}`,
      ),
    );
    const status = parseRawRecordingStatus(response.value, studyId);
    await scope.wait(
      this.commit((current) => {
        const next = clone(current);
        next.rawRecordingStatuses[studyId] = status;
        // Completed receipts can remove a stop fence. Pending/lost revocation cannot.
        const pending = next.queue.some(
          (q) =>
            q.kind === "raw_revocation" &&
            q.body.study_id === studyId &&
            q.state !== "synced",
        );
        if (!pending)
          next.rawRecordingFences[studyId] = (
            next.rawRecordingFences[studyId] ?? []
          ).filter(
            (kind) =>
              status.revocations.some(
                (receipt) =>
                  receipt.state === "cleanup_pending" &&
                  receipt.artifact_kinds.includes(kind),
              ) ||
              !status.revocations.some(
                (receipt) =>
                  receipt.state === "completed" &&
                  receipt.artifact_kinds.includes(kind),
              ),
          );
        return next;
      }),
    );
  }
  async saveRawRecordingChoices(
    studyId: string,
    choices: RawChoices,
  ): Promise<void> {
    this.requireWritable();
    if (!this.model.identity)
      throw new IntegrityError(
        "SIGN_IN_REQUIRED",
        "Recording choices require a signed-in study owner.",
      );
    const partition = {
      epoch: this.workspaceEpoch,
      workspace: this.model.state!.workspace,
      generation: this.model.state!.generation,
      accountRef: this.model.identity.accountRef,
    };
    const status = this.model.state!.rawRecordingStatuses[studyId];
    if (!status)
      throw new IntegrityError(
        "RAW_POLICY_UNAVAILABLE",
        "Load the approved policy before changing recording choices.",
      );
    assertRawChoicesAllowed(
      status,
      choices,
      this.model.state!.rawRecordingFences[studyId],
    );
    if (
      this.model.state!.studies.some(
        (study) => study.study_id === studyId && study.local_withdrawal_pending,
      )
    )
      throw new IntegrityError(
        "WITHDRAWAL_PENDING",
        "Recording cannot restart while study withdrawal is pending.",
      );
    const acknowledgedAt = now();
    const payload = {
      consent_record_id: status.consent_record_id,
      policy_id: status.policy!.policy_id,
      policy_version: status.policy!.version,
      policy_sha256: status.policy!.sha256,
      raw_notice_version: status.policy!.raw_notice.version,
      raw_notice_sha256: status.policy!.raw_notice.sha256,
      acknowledged_at: acknowledgedAt,
      choices: clone(choices),
    } as unknown as JsonObject;
    if (!(await this.signIn(true))) return;
    if (
      partition.epoch !== this.workspaceEpoch ||
      partition.workspace !== this.model.state?.workspace ||
      partition.generation !== this.model.state?.generation ||
      partition.accountRef !== this.model.identity?.accountRef
    )
      throw new IntegrityError(
        "WORKSPACE_CHANGED",
        "The recording confirmation was discarded because its owner workspace changed.",
      );
    const origin = this.scope();
    this.requireWritable();
    assertRawChoicesAllowed(
      status,
      choices,
      this.model.state!.rawRecordingFences[studyId],
    );
    const matches = (q: WorkspaceState["queue"][number]) =>
      q.kind === "raw_preference" &&
      q.generation === this.model.state!.generation &&
      q.body.study_id === studyId &&
      digest({ ...requireObject(q.body.payload), acknowledged_at: null }) ===
        digest({ ...payload, acknowledged_at: null });
    let intent = this.model.state!.queue.find(matches);
    if (!intent) {
      await origin.wait(
        this.commit((current) =>
          queueMutation(
            current,
            "raw_preference",
            { study_id: studyId, payload },
            newId,
            acknowledgedAt,
          ),
        ),
      );
      intent = this.model.state!.queue.find(matches)!;
    }
    await origin.wait(this.sync.run(intent.id, true));
    const accepted =
      this.model.state!.queue.find((q) => q.id === intent!.id)?.state ===
      "synced";
    this.patch({
      message: accepted
        ? "Your separate recording and upload choices were confirmed by the service. Each capture still requires current authorization."
        : "Your exact choices are saved as a pending request. Recording permission is not confirmed until its receipt is verified.",
    });
  }
  async retainRawRecording(
    checkId: string,
    attemptId: string,
    kind: RawKind,
    value: unknown,
    permissionValue: unknown,
  ): Promise<void> {
    const scope = this.scope(),
      check = this.model.state?.checks.find((check) => check.id === checkId),
      store = this.store;
    if (
      !this.model.identity ||
      BUILD.hostedPreview ||
      !check ||
      check.snapshot.mode !== "controlled_research" ||
      !check.snapshot.study_id ||
      !store?.saveWithRaw ||
      !store.deleteRaw
    )
      throw new IntegrityError(
        "ENCRYPTED_RAW_STORAGE_REQUIRED",
        "Participant recordings require an owned approved check and unlocked encrypted native storage.",
      );
    const attempt = check.attempts.find(
        (attempt) => attempt.attempt_id === attemptId,
      ),
      status = this.model.state!.rawRecordingStatuses[check.snapshot.study_id];
    if (
      !attempt ||
      !attempt.started_at ||
      attempt.status === "started" ||
      attempt.component !== (kind === "eye_video" ? "eyes" : "cardiac") ||
      !status
    )
      throw new IntegrityError(
        "RAW_ATTEMPT_REQUIRED",
        "The raw recording requires its actual completed acquisition attempt and exact consent receipt.",
      );
    const permission = verifyRawPermission(
      permissionValue,
      status,
      kind,
      this.model.state!.rawRecordingFences[check.snapshot.study_id] ?? [],
    );
    const raw = decodeRawRecording(value, kind),
      localId = newId();
    const current = () =>
      scope.current() &&
      !this.model.state!.rawRecordingFences[check.snapshot.study_id!]?.includes(
        kind,
      ) &&
      !this.model.state!.studies.some(
        (study) =>
          study.study_id === check.snapshot.study_id &&
          study.local_withdrawal_pending,
      );
    try {
      if (kind === "eye_video") {
        const native = requireObject(attempt.component_metadata.native_result),
          frames = native.frame_events;
        const material = requireObject(
            check.acquisition?.attempts[attemptId]?.authorization
              ?.configuration_material,
          ),
          view = new DataView(raw.bytes.buffer);
        if (
          !Array.isArray(frames) ||
          view.getUint16(16, true) !== material.roi_sample_width ||
          view.getUint16(18, true) !== material.roi_sample_height ||
          view.getUint32(20, true) !== frames.length
        )
          throw new IntegrityError(
            "RAW_FRAME_LINKAGE",
            "The retained ROI geometry or count differs from its actual native acquisition ledger.",
          );
        const stride = 12 + view.getUint16(16, true) * view.getUint16(18, true);
        for (let index = 0; index < frames.length; index++) {
          const frame = requireObject(frames[index]),
            at = 24 + index * stride;
          if (
            Math.abs(
              view.getFloat64(at, true) - Number(frame.native_timestamp_ms),
            ) > 1e-6 ||
            digestBytes(raw.bytes.subarray(at + 12, at + stride)) !==
              frame.roi_luma_sha256
          )
            throw new IntegrityError(
              "RAW_FRAME_LINKAGE",
              "Raw frame timestamps or luminance digests differ from their immutable native evidence.",
            );
        }
      } else {
        const body = raw.evidence!,
          attestation = check.attestations?.[attemptId],
          material = requireObject(
            check.acquisition?.attempts[attemptId]?.authorization
              ?.configuration_material,
          );
        if (
          !attestation ||
          [
            "attestation_id",
            "envelope",
            "signature",
            "normalized_payload",
          ].some((key) => digest(body[key]) !== digest(attestation[key])) ||
          material.raw_encoding !== "otgd_ecg_samples_v1" ||
          !Number.isSafeInteger(material.raw_sample_limit) ||
          Number(material.raw_sample_limit) < 1 ||
          Number(material.raw_sample_limit) > 1024
        )
          throw new IntegrityError(
            "RAW_SAMPLE_LINKAGE",
            "The retained ECG bytes do not match their actual signed acquisition and approved raw codec.",
          );
        let total = 0;
        for (const value of body.sample_chunks as JsonObject[]) {
          const n = requireObject(requireObject(value).normalized_payload);
          total += (n.samples as unknown[]).length;
          if (
            n.sample_rate_hz !== material.sample_rate_hz ||
            Number(n.first_sample_index) + (n.samples as unknown[]).length >
              Number(material.raw_sample_limit)
          )
            throw new IntegrityError(
              "RAW_SAMPLE_LINKAGE",
              "The retained ECG sample rate or range exceeds its approved material.",
            );
        }
        if (total > Number(material.raw_sample_limit))
          throw new IntegrityError(
            "RAW_SAMPLE_LINKAGE",
            "The retained ECG sample count exceeds its approved recording limit.",
          );
      }
      await this.commit(
        (state) => {
          if (!current())
            throw new IntegrityError(
              "RAW_RECORDING_STOPPED",
              "A stopped recording cannot return to local storage.",
            );
          const next = clone(state);
          next.rawArtifacts ??= [];
          next.rawArtifacts.push({
            local_id: localId,
            study_id: check.snapshot.study_id!,
            session_id: check.id,
            attempt_id: attemptId,
            artifact_kind: kind,
            format: raw.format,
            media_type: raw.media_type,
            sha256: raw.sha256,
            size_bytes: raw.size_bytes,
            capture_started_at: attempt.started_at!,
            consent_record_id: status.consent_record_id!,
            permission,
            state: "local",
            server_artifact_id: null,
            created_at: now(),
            retention_due_at: new Date(
              Date.parse(attempt.started_at!) +
                status.policy!.max_retention_days * 86_400_000,
            ).toISOString(),
            error: null,
          });
          return next;
        },
        { id: localId, bytes: raw.bytes, current },
      );
    } catch (error) {
      await store.deleteRaw(localId).catch(() => {});
      throw error;
    } finally {
      raw.bytes.fill(0);
    }
  }
  private async purgeLocalRaw(
    studyId?: string,
    kinds: RawKind[] = [...RAW_KINDS],
  ): Promise<void> {
    const scope = this.scope(),
      store = this.store;
    const files = (this.model.state?.rawArtifacts ?? []).filter(
      (raw) =>
        (!studyId || raw.study_id === studyId) &&
        kinds.includes(raw.artifact_kind) &&
        raw.state !== "deleted",
    );
    for (const file of files) {
      if (!store?.deleteRaw)
        throw new IntegrityError(
          "ENCRYPTED_RAW_STORAGE_REQUIRED",
          "The encrypted recording store is unavailable for local cleanup.",
        );
      await scope.wait(store.deleteRaw(file.local_id));
      await scope.wait(
        this.commit((state) => {
          const next = clone(state),
            raw = next.rawArtifacts?.find(
              (raw) => raw.local_id === file.local_id,
            );
          if (raw) {
            raw.state = "deleted";
            raw.error = null;
          }
          return next;
        }),
      );
    }
  }
  private async maintainLocalRaw(): Promise<void> {
    if (!this.model.state || this.model.locked || !this.store?.reconcileRaw)
      return;
    if (
      !(this.model.state.rawArtifacts ?? []).some(
        (raw) =>
          raw.state !== "deleted" &&
          (raw.state === "quarantined" ||
            !Number.isFinite(Date.parse(raw.retention_due_at)) ||
            Date.parse(raw.retention_due_at) <= Date.now()),
      )
    )
      return;
    await this.commit((state) => state, undefined, true);
  }
  async removeLocalRawFile(localId: string): Promise<void> {
    const scope = this.scope(),
      file = this.model.state?.rawArtifacts?.find(
        (file) => file.local_id === localId,
      );
    if (!file || file.state === "deleted") return;
    const stop = this.stopActive("USER_CANCELED");
    this.api.cancelAll();
    await this.commit((state) => {
      const next = clone(state),
        raw = next.rawArtifacts!.find((raw) => raw.local_id === localId)!;
      raw.state = "quarantined";
      raw.error = "LOCAL_COPY_REMOVAL_REQUESTED";
      for (const q of next.queue)
        if (
          q.kind === "check" &&
          q.state !== "synced" &&
          ((q.body.raw_local_ids ?? []) as string[]).includes(localId)
        ) {
          q.state = "blocked";
          q.error = "LOCAL_COPY_REMOVAL_REQUESTED";
        }
      return next;
    });
    await scope.wait(stop);
    if (!this.store?.deleteRaw)
      throw new IntegrityError(
        "ENCRYPTED_RAW_STORAGE_REQUIRED",
        "Local cleanup is pending until encrypted native storage is unlocked.",
      );
    await scope.wait(this.store.deleteRaw(localId));
    await this.commit((state) => {
      const next = clone(state),
        raw = next.rawArtifacts!.find((raw) => raw.local_id === localId)!;
      raw.state = "deleted";
      raw.error = null;
      return next;
    });
    this.patch({
      message:
        "This encrypted device copy was removed. Already uploaded files remain governed by their server cleanup receipts.",
    });
  }
  async revokeRawRecordings(studyId: string, kinds: RawKind[]): Promise<void> {
    if (
      !this.model.identity ||
      !this.model.state ||
      !kinds.length ||
      new Set(kinds).size !== kinds.length ||
      kinds.some((kind) => !RAW_KINDS.includes(kind))
    )
      throw new IntegrityError(
        "RAW_REVOCATION_INVALID",
        "Choose owned recording kinds to stop.",
      );
    const scope = this.scope();
    // Stop acquisition before any durable write or server request can wait.
    const stopped = this.stopActive("WITHDRAWAL");
    this.api.cancelAll();
    await scope.wait(
      this.commit((current) => {
        const next = queueMutation(
          current,
          "raw_revocation",
          {
            study_id: studyId,
            payload: { confirmation: true, artifact_kinds: [...kinds] },
          },
          newId,
          now(),
        );
        next.rawRecordingFences[studyId] = [
          ...new Set([...(next.rawRecordingFences[studyId] ?? []), ...kinds]),
        ];
        for (const raw of next.rawArtifacts ?? [])
          if (
            raw.study_id === studyId &&
            kinds.includes(raw.artifact_kind) &&
            raw.state !== "deleted"
          )
            raw.state = "quarantined";
        for (const q of next.queue)
          if (
            q.kind === "check" &&
            q.state !== "synced" &&
            ((q.body.raw_local_ids ?? []) as string[]).some((id) =>
              next.rawArtifacts?.some(
                (raw) =>
                  raw.local_id === id &&
                  raw.study_id === studyId &&
                  kinds.includes(raw.artifact_kind),
              ),
            )
          ) {
            q.state = "blocked";
            q.error = "RAW_REVOCATION_PENDING";
            const check = next.checks.find((check) => check.id === q.check_id);
            if (check) {
              check.delivery = "blocked";
              check.error = "RAW_REVOCATION_PENDING";
            }
          }
        for (const q of next.queue)
          if (
            q.kind === "raw_preference" &&
            q.body.study_id === studyId &&
            q.state !== "synced"
          ) {
            q.state = "blocked";
            q.error = "RAW_REVOCATION_PENDING";
          }
        return next;
      }),
    );
    await scope.wait(stopped);
    await scope.wait(this.purgeLocalRaw(studyId, kinds));
    const intent = this.model.state!.queue.find(
      (q) =>
        q.kind === "raw_revocation" &&
        q.body.study_id === studyId &&
        q.state !== "synced",
    );
    if (intent) await scope.wait(this.sync.run(intent.id, true));
    this.patch({
      message:
        "Local recording is stopped. Pending requests and server cleanup receipts are shown separately; cleanup is complete only when the service confirms it.",
    });
  }
  async withdraw(studyId: string): Promise<void> {
    const scope = this.scope();
    const stopped = this.stopActive("WITHDRAWAL");
    this.api.cancelAll();
    await this.commit((s) => {
      const next = queueMutation(
        s,
        "withdrawal",
        { study_id: studyId, payload: { confirmation: true } },
        newId,
        now(),
      );
      next.rawRecordingFences[studyId] = [...RAW_KINDS];
      for (const raw of next.rawArtifacts ?? [])
        if (raw.study_id === studyId && raw.state !== "deleted")
          raw.state = "quarantined";
      next.studies = next.studies.map((x) =>
        String(x.study_id) === studyId
          ? { ...x, local_withdrawal_pending: true }
          : x,
      );
      next.queue = next.queue.map((q) =>
        (q.kind === "check" ||
          q.kind === "consent" ||
          q.kind === "raw_preference") &&
        q.state !== "synced" &&
        (["consent", "raw_preference"].includes(q.kind)
          ? q.body.study_id === studyId
          : s.checks.find((c) => c.id === q.check_id)?.snapshot.study_id ===
            studyId)
          ? { ...q, state: "blocked", error: "WITHDRAWAL_PENDING" }
          : q,
      );
      return next;
    });
    await scope.wait(stopped);
    await scope.wait(this.purgeLocalRaw(studyId));
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
    if (flow !== this.authFlow) return;
    this.workspaceEpoch = newId();
    await this.writes.catch(() => {});
    if (flow !== this.authFlow) return;
    if (this.store) await this.store.close();
    if (flow !== this.authFlow) return;
    this.store = null;
    this.patch({
      state: null,
      identity: null,
      locked: false,
      sheet: null,
      diagnosticError: null,
      route: "welcome",
      selectedCheck: null,
      rawStudyId: null,
      historyRows: [],
      historyCursor: null,
    });
    await this.openGuest();
    if (flow !== this.authFlow) return;
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
        if (flow !== this.authFlow) return;
        await providerRevoke;
        if (flow !== this.authFlow) return;
        if (providerLogout) await this.auth.openProviderLogout(providerLogout);
      } catch {
        if (flow === this.authFlow)
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
        await this.maintainLocalRaw();
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
      await this.maintainLocalRaw();
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
