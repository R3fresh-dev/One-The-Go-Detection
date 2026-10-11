import React, { useEffect, useRef, useState } from "react";
import { AppState, Linking, Platform, Text, View } from "react-native";
import { Camera } from "expo-camera";
import Constants from "expo-constants";
import * as Clipboard from "expo-clipboard";
import {
  getBluetoothPermissionStatus,
  getCameraPermissionStatus,
} from "../../modules/device-transport";
import { createDiagnostics } from "../core/diagnostics";
import {
  historyViews,
  pendingSync,
  sortHistoryRows,
  type HistoryView,
} from "../core/historyView";
import { syncReadiness } from "../services/api";
import { useTheme } from "./theme";
import { getEnrolledLevelAsync } from "expo-local-authentication";
import { DevicePanel } from "../device";
import { digestText, utf8 } from "../core/integrity";
import type { CheckRecord, JsonObject, PrivacyJob } from "../core/types";
import { BUILD } from "../platform/config";
import { assessStudyConsent } from "./study-consent";
import {
  action,
  CheckRow,
  dateLabel,
  friendly,
  shortId,
  type ScreenProps,
} from "./account";
import {
  ActionRow,
  Badge,
  Button,
  Card,
  Choice,
  Fact,
  Field,
  Label,
  Metric,
  Notice,
  Page,
  Paragraph,
  Row,
  SwitchRow,
  Title,
  layout,
} from "./components";

export function DeviceScreen({ controller, model }: ScreenProps) {
  return (
    <Page
      title="Devices & connection"
      eyebrow="Hardware workspace"
      onBack={action(controller, () =>
        controller.navigate(
          controller.check && !controller.check.frozen ? "check" : "home",
        ),
      )}
      subtitle="Bluetooth discovery starts only when you request it."
    >
      <DevicePanel controller={controller.device} />
      <Card>
        <Title small>Qualification is separate from connection</Title>
        <Paragraph>
          Project simulators provide synthetic test data. This release has no
          approved credentials, assay, optical configuration or human
          ECG/alcohol hardware. A successful Bluetooth connection cannot enable
          a human measurement.
        </Paragraph>
        <Fact label="Qualified human acquisition" value="Unavailable" />
        <Fact label="Impairment inference" value="Unavailable" />
        <Fact label="Stored raw human signals" value="Not supported" />
      </Card>
      {controller.check && !controller.check.frozen && (
        <Button
          title="Return to current check"
          onPress={action(controller, () => controller.navigate("check"))}
        />
      )}
    </Page>
  );
}
export function HistoryScreen({ controller, model }: ScreenProps) {
  const state = model.state!,
    scope = `${controller.epoch}:${state.generation}`;
  const [savedView, setSavedView] = useState(() => ({
    scope,
    view: historyViews.read(controller, scope),
  }));
  const view =
    savedView.scope === scope
      ? savedView.view
      : historyViews.read(controller, scope);
  const { filter, search, from, to, selected, selectionMode } = view;
  const isCurrent = () =>
    `${controller.epoch}:${controller.getSnapshot().state?.generation}` ===
    scope;
  const updateView = (patch: Partial<HistoryView>) => {
    if (isCurrent())
      setSavedView({
        scope,
        view: historyViews.update(controller, scope, patch),
      });
  };
  const setFilter = (filter: HistoryView["filter"]) => updateView({ filter });
  const setSearch = (search: string) => updateView({ search });
  const setFrom = (from: string) => updateView({ from });
  const setTo = (to: string) => updateView({ to });
  const setSelected = (next: string[] | ((prior: string[]) => string[])) =>
    updateView({
      selected:
        typeof next === "function"
          ? next(historyViews.read(controller, scope).selected)
          : next,
    });
  const setSelectionMode = (selectionMode: boolean) =>
    updateView({ selectionMode });
  const local = state.checks.filter(
      (c) => c.generation === state.generation && c.delivery !== "quarantined",
    ),
    ids = new Set(local.map((c) => c.id)),
    remote = state.historyIndex.filter((r) => !ids.has(String(r.session_id)));
  const matches = (
    id: string,
    created: string,
    synthetic: boolean,
    pending = false,
  ) =>
    id.toLowerCase().includes(search.toLowerCase().trim()) &&
    (filter === "all" ||
      (filter === "synthetic" && synthetic) ||
      (filter === "measurement" && !synthetic) ||
      (filter === "pending" && pending)) &&
    (!from || created.slice(0, 10) >= from) &&
    (!to || created.slice(0, 10) <= to);
  const visible = local.filter((c) =>
      matches(
        c.id,
        c.snapshot.created_at,
        c.kind !== "measurement",
        pendingSync(c.delivery),
      ),
    ),
    visibleRemote = remote.filter((r) =>
      matches(
        String(r.session_id),
        String(r.created_at),
        r.mode === "synthetic",
      ),
    );
  const combined = sortHistoryRows<{
    id: string;
    createdAt: string;
    check: CheckRecord | null;
    row: JsonObject | null;
  }>([
    ...visible.map((check) => ({
      id: check.id,
      createdAt: check.snapshot.created_at,
      check,
      row: null,
    })),
    ...visibleRemote.map((row) => ({
      id: String(row.session_id),
      createdAt: String(row.created_at),
      check: null,
      row,
    })),
  ]);
  const day = (at: string) =>
    new Date(at).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  const toggle = (id: string) =>
    setSelected((list) =>
      list.includes(id)
        ? list.filter((x) => x !== id)
        : list.length >= 500
          ? list
          : [...list, id],
    );
  return (
    <Page
      key={scope}
      title="Your check history"
      initialScrollY={view.scrollY}
      onScrollY={(scrollY) => {
        if (isCurrent()) historyViews.update(controller, scope, { scrollY });
      }}
      eyebrow="Local and synced records"
      subtitle="Drafts, saved measurements and requested uploads keep separate states."
    >
      <Card>
        <Choice
          label="Check type"
          value={filter}
          options={[
            { value: "all", label: "All" },
            { value: "measurement", label: "Measurements" },
            { value: "synthetic", label: "Demo / fictional" },
            { value: "pending", label: "Pending sync" },
          ]}
          onChange={setFilter}
        />
        <Field
          label="Find by check ID"
          value={search}
          onChangeText={setSearch}
          autoCapitalize="none"
        />
        <View style={layout.grid}>
          <Field
            label="From date (YYYY-MM-DD)"
            value={from}
            onChangeText={setFrom}
            placeholder="YYYY-MM-DD"
          />
          <Field
            label="To date (YYYY-MM-DD)"
            value={to}
            onChangeText={setTo}
            placeholder="YYYY-MM-DD"
          />
        </View>
        <Paragraph muted>
          Date filters use the saved UTC check date. A filter does not change an
          export selection.
        </Paragraph>
        {model.identity && (
          <Button
            title="Refresh synced history"
            secondary
            onPress={action(controller, () => controller.refreshHistory())}
            busy={model.busy}
          />
        )}
        <SwitchRow
          title="Select saved checks to export"
          detail="Up to 500 exact check IDs; changing a filter does not silently add records."
          value={selectionMode}
          onChange={(v) => {
            setSelectionMode(v);
            if (!v) setSelected([]);
          }}
        />
      </Card>
      {model.offline && (
        <Notice tone="warning">
          Offline: only cached records can be opened. A queued check is not
          necessarily uploaded.
        </Notice>
      )}
      {selectionMode && (
        <Card>
          <Fact label="Selected" value={`${selected.length} checks`} />
          <Button
            title="Review selected export"
            disabled={selected.length === 0}
            onPress={action(controller, () =>
              controller.openExport({
                source: "device",
                selection: {
                  kind: selected.length === 1 ? "single" : "selected",
                  session_ids: selected,
                },
              }),
            )}
          />
          <Button
            title="Clear selection"
            secondary
            onPress={() => setSelected([])}
          />
        </Card>
      )}
      {visible.length + visibleRemote.length === 0 && (
        <Card>
          <Title small>
            {local.length + remote.length
              ? "No matching checks"
              : "Your first check starts here"}
          </Title>
          <Paragraph>
            {local.length + remote.length
              ? "Try another check ID, date range or check type."
              : "Saved checks will appear with their source, quality and upload state."}
          </Paragraph>
          <Button
            title="Go to home"
            secondary
            onPress={action(controller, () => controller.navigate("home"))}
          />
        </Card>
      )}
      {combined.map((item, index) => (
        <View key={item.id} style={{ gap: 9 }}>
          {(index === 0 ||
            day(combined[index - 1]!.createdAt) !== day(item.createdAt)) && (
            <Label>{day(item.createdAt)}</Label>
          )}
          {item.check ? (
            <>
              {selectionMode && item.check.frozen && (
                <SwitchRow
                  title={`Select ${shortId(item.id)}`}
                  value={selected.includes(item.id)}
                  onChange={() => toggle(item.id)}
                />
              )}
              <CheckRow
                check={item.check}
                onPress={action(controller, () =>
                  controller.selectCheck(item.id),
                )}
              />
            </>
          ) : (
            <Card>
              {selectionMode && (
                <SwitchRow
                  title={`Select ${shortId(item.id)}`}
                  value={selected.includes(item.id)}
                  onChange={() => toggle(item.id)}
                />
              )}
              <Row>
                <Badge>Synced metadata</Badge>
                <Badge
                  tone={item.row!.mode === "synthetic" ? "warning" : "neutral"}
                >
                  {friendly(item.row!.mode)}
                </Badge>
              </Row>
              <ActionRow
                title={dateLabel(item.createdAt)}
                detail={`${friendly(item.row!.state)} · ${shortId(item.id)}`}
                onPress={action(controller, () =>
                  controller.selectCheck(item.id),
                )}
              />
            </Card>
          )}
        </View>
      ))}
      <Paragraph muted>
        {model.offline
          ? "Showing cached records only."
          : state.historyCursor
            ? "More synced records are available below."
            : "Showing all loaded local and synced records."}{" "}
        Pending sync is this device’s requested-upload queue.
      </Paragraph>
      {state.historyCursor && (
        <Button
          title="Load more synced checks"
          secondary
          onPress={action(controller, () => controller.refreshHistory(true))}
        />
      )}
      <Card>
        <Label>Requested operations</Label>
        <Paragraph muted>
          “Retry queued uploads automatically” is{" "}
          {state.preferences.retryQueuedAutomatically ? "on" : "off"}. Saving a
          future check never queues it.
        </Paragraph>
        {state.queue
          .filter((q) => q.state !== "synced")
          .map((q) => (
            <View key={q.id} style={{ gap: 8, paddingVertical: 10 }}>
              <Fact
                label={`${friendly(q.kind)} · ${shortId(q.check_id ?? q.id)}`}
                value={friendly(q.state)}
              />
              {q.error && <Paragraph muted>{q.error}</Paragraph>}
              {q.kind === "check" && q.state !== "quarantined" && (
                <Button
                  title="Stop further upload attempts"
                  secondary
                  onPress={action(controller, () =>
                    controller.ask({
                      title: "Stop retrying this upload?",
                      text: "No more requests will be sent for this operation. Already accepted server data is unaffected and requires a separate privacy deletion request.",
                      confirm: "Stop upload attempts",
                      action: () => controller.cancelQueue(q.id),
                    }),
                  )}
                />
              )}
            </View>
          ))}
        <Button
          title="Retry requested operations now"
          disabled={
            !model.identity ||
            state.queue.every(
              (q) => q.state === "synced" || q.state === "quarantined",
            )
          }
          onPress={action(controller, () => controller.retryUploads())}
        />
      </Card>
    </Page>
  );
}
function PermissionsCard({ controller }: Pick<ScreenProps, "controller">) {
  const [camera, setCamera] = useState("Not checked"),
    [bluetooth, setBluetooth] = useState("Not checked"),
    [unlock, setUnlock] = useState("Not checked");
  const active = useRef(true),
    sequence = useRef(0);
  const refresh = async () => {
    const run = ++sequence.current;
    const current = () => active.current && run === sequence.current;
    if (Platform.OS === "web") {
      if (current()) {
        setCamera("Browser permission is checked at eye preview");
        setBluetooth("Unavailable in browser preview");
        setUnlock("Web preview uses memory only");
      }
      return;
    }
    const results = await Promise.allSettled([
      Promise.all([
        getCameraPermissionStatus(),
        Camera.getCameraPermissionsAsync(),
      ]),
      getBluetoothPermissionStatus(),
      getEnrolledLevelAsync(),
    ]);
    if (!current()) return;
    const [cameraResult, bluetoothResult, unlockResult] = results;
    if (cameraResult.status === "fulfilled") {
      const [exact, permission] = cameraResult.value;
      setCamera(
        exact === "restricted"
          ? "Restricted by device policy"
          : permission.granted
            ? "Granted"
            : permission.status === "undetermined"
              ? "Not requested"
              : permission.canAskAgain
                ? "Denied · request only in eye preview"
                : "Denied · review app settings",
      );
    } else setCamera("Status unavailable · refresh to retry");
    const labels = {
      granted: "Granted",
      denied: "Not granted",
      restricted: "Restricted by device policy",
      not_requested: "Not requested",
      unavailable: "Native Bluetooth unavailable",
      unknown: "Status unavailable",
    };
    setBluetooth(
      bluetoothResult.status === "fulfilled"
        ? labels[bluetoothResult.value]
        : "Status unavailable · refresh to retry",
    );
    setUnlock(
      unlockResult.status === "fulfilled"
        ? unlockResult.value > 0
          ? "Device credential or biometrics enrolled"
          : "Set up a device credential first"
        : "Status unavailable · refresh to retry",
    );
  };
  useEffect(() => {
    active.current = true;
    void refresh();
    const subscription = AppState.addEventListener("change", (state) => {
      if (state === "active") void refresh();
    });
    return () => {
      active.current = false;
      ++sequence.current;
      subscription.remove();
    };
  }, []);
  return (
    <Card>
      <Title small>Device permissions</Title>
      <Fact label="Camera · eye-positioning preview" value={camera} />
      <Fact
        label="Bluetooth · find and connect to a reader"
        value={bluetooth}
      />
      <Fact label="Private record unlock" value={unlock} />
      <Paragraph muted>
        Viewing this page requests no permission. Bluetooth permission is
        requested only from Devices. Android 11 and earlier require the OS
        discovery location permission for Bluetooth scanning; the app does not
        collect location. No microphone, photo-library or notification
        permission is requested.
      </Paragraph>
      <Button
        title="Refresh permission status"
        secondary
        onPress={() => {
          void refresh();
        }}
      />
      {Platform.OS !== "web" && (
        <Button
          title="Open device settings"
          secondary
          onPress={action(controller, async () => {
            await Linking.openSettings();
          })}
        />
      )}
    </Card>
  );
}
function DiagnosticsCard({ controller, model }: ScreenProps) {
  const colors = useTheme();
  const [preview, setPreview] = useState<string | null>(null),
    [copied, setCopied] = useState(false),
    [copyFailed, setCopyFailed] = useState(false);
  const prepare = () => {
    const latest = model.state?.queue.at(-1);
    setPreview(
      createDiagnostics({
        appVersion: Constants.nativeAppVersion ?? BUILD.version,
        buildNumber: Constants.nativeBuildVersion ?? "unavailable",
        platform: Platform.OS,
        platformVersion: String(Platform.Version),
        environment: BUILD.environment,
        publicServiceOrigin: BUILD.apiUrl,
        capabilityCodes: Object.values(
          model.state?.capabilities?.channels ?? {},
        ).flatMap((channel) => channel.reason_codes),
        syncState: latest?.state ?? "none",
        errorCode: model.diagnosticError?.code,
        supportRequestId: model.diagnosticError?.requestId,
      }),
    );
    setCopied(false);
    setCopyFailed(false);
  };
  return (
    <Card>
      <Title small>Help & diagnostics</Title>
      <Paragraph>
        Reader connection: check Bluetooth access, power and distance, then
        request a fresh scan. A simulator connection does not qualify a sensor.
      </Paragraph>
      <Paragraph>
        Offline records: unlock the current workspace to view local saves.
        Upload only queues after your explicit choice; Pending sync shows
        requested delivery.
      </Paragraph>
      <Paragraph>
        Unavailable capture: read Service status for the reason. Export and
        deletion are in Privacy & data; a pending request is not a completed
        request.
      </Paragraph>
      <Button title="Preview diagnostics" secondary onPress={prepare} />
      {preview !== null && (
        <>
          <Paragraph muted>
            Review this allowlisted support report before copying. It contains
            no account, profile, measurement, token or device-address fields.
          </Paragraph>
          <Text
            selectable
            accessibilityLabel="Redacted diagnostics preview"
            style={{
              color: colors.ink,
              fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
              fontSize: 12,
              lineHeight: 19,
            }}
          >
            {preview}
          </Text>
          <Button
            title="Copy reviewed diagnostics"
            onPress={() => {
              void (async () => {
                try {
                  const accepted = await Clipboard.setStringAsync(preview);
                  if (!accepted) throw new Error("Clipboard unavailable");
                  setCopied(true);
                  setCopyFailed(false);
                } catch {
                  setCopied(false);
                  setCopyFailed(true);
                }
              })();
            }}
          />
          <Button
            title="Close preview"
            secondary
            onPress={() => {
              setPreview(null);
              setCopied(false);
              setCopyFailed(false);
            }}
          />
          {copied && <Notice>Diagnostics copied.</Notice>}
          {copyFailed && (
            <Notice tone="warning">
              Diagnostics were not copied. Check clipboard access and try again.
              No additional error content was included.
            </Notice>
          )}
        </>
      )}
    </Card>
  );
}
export function SettingsScreen({ controller, model }: ScreenProps) {
  const state = model.state!,
    unsynced = state.checks.filter(
      (c) => c.delivery !== "synced" && c.delivery !== "quarantined",
    ).length;
  return (
    <Page title="Settings" eyebrow="Make this workspace yours">
      <Card>
        <Label>Appearance & accessibility</Label>
        <Choice
          label="Theme"
          value={state.preferences.theme}
          options={[
            { value: "system", label: "System" },
            { value: "light", label: "Light" },
            { value: "dark", label: "Dark" },
          ]}
          onChange={(v) => {
            void controller
              .changePreferences({ theme: v })
              .catch((e) => controller.report(e));
          }}
        />
        <SwitchRow
          title="Reduce motion"
          value={state.preferences.reducedMotion}
          onChange={(v) => {
            void controller
              .changePreferences({ reducedMotion: v })
              .catch((e) => controller.report(e));
          }}
          detail="Navigation uses no continuous animation. The native task keeps its fixed acquisition presentation."
        />
        <Choice
          label="Profile display units"
          value={state.preferences.units}
          options={[
            { value: "metric", label: "Metric" },
            { value: "imperial", label: "Imperial" },
          ]}
          onChange={(v) => {
            void controller
              .changePreferences({ units: v })
              .catch((e) => controller.report(e));
          }}
        />
        <Paragraph muted>
          Text outside acquisition follows system text scaling. Task requested
          sRGB colors, shape/text size, geometry and timing are fixed by its
          configuration. Physical luminance is unmeasured; the app does not
          override brightness.
        </Paragraph>
      </Card>
      <PermissionsCard controller={controller} />
      <DiagnosticsCard
        key={`${controller.epoch}:${state.generation}`}
        controller={controller}
        model={model}
      />
      <Card>
        <ActionRow
          title="Privacy & data"
          detail="Local storage, export, deletion and upload retry preference"
          onPress={action(controller, () => controller.navigate("privacy"))}
        />
        <ActionRow
          title="Research access"
          detail="Separate study invitation and consent; no automatic enrollment"
          onPress={action(controller, () => controller.navigate("studies"))}
        />
        <ActionRow
          title="Application data notice"
          detail={state.notice?.version ?? "Current notice"}
          onPress={action(controller, () => controller.navigate("notice"))}
        />
        <ActionRow
          title="About this release"
          detail={`Version ${BUILD.version} · ${BUILD.environment.toUpperCase()}`}
          onPress={action(controller, () => controller.navigate("about"))}
        />
        <ActionRow
          title="Service status & capabilities"
          detail={
            model.offline
              ? "Offline or unavailable"
              : "View current limitations"
          }
          onPress={action(controller, () => controller.navigate("status"))}
        />
      </Card>
      <Card>
        <Title small>{model.identity ? "Account" : "Guest workspace"}</Title>
        <Paragraph>
          {model.identity
            ? "Account records are isolated by service identity and data generation. Signing out locks this account’s retained cache."
            : "Guest records stay separate and never upload. Sign-in opens another workspace without importing this one."}
        </Paragraph>
        {model.identity ? (
          <>
            <Fact
              label="Account reference"
              value={shortId(model.identity.accountRef)}
            />
            <Fact label="Local unsynced checks" value={String(unsynced)} />
            <Button
              title="Sign out"
              secondary
              onPress={action(controller, () =>
                controller.ask({
                  title: "Keep encrypted records and sign out?",
                  text: "The default keeps this account’s encrypted records locked on the device. The same account must sign in again to open them. Offline sign-out removes local credentials immediately; remote revocation may remain unconfirmed.",
                  confirm: "Keep records and sign out",
                  action: () => controller.signOut(false),
                  secondary: {
                    title: "Remove this account’s local records and sign out",
                    action: () =>
                      controller.ask({
                        title: "Remove local records and sign out?",
                        text: `This permanently removes this account’s local records, including ${unsynced} unsynced checks. Other workspaces and cloud records are unaffected.`,
                        confirm: "Remove local records and sign out",
                        danger: true,
                        action: () => controller.signOut(true),
                      }),
                  },
                }),
              )}
            />
          </>
        ) : (
          <Button
            title="Sign in to a separate account workspace"
            onPress={action(controller, () =>
              controller.ask({
                title: "Open the account workspace?",
                text: "The guest draft and records stay in their original workspace. No guest data is imported or uploaded.",
                confirm: "Keep guest draft and sign in",
                action: async () => {
                  await controller.signIn();
                },
              }),
            )}
          />
        )}
      </Card>
    </Page>
  );
}
function JobCard({
  job,
  controller,
}: {
  job: PrivacyJob;
  controller: ScreenProps["controller"];
}) {
  return (
    <Card>
      <Row>
        <Title small>
          {job.kind === "export" ? "Data export" : "Deletion request"}
        </Title>
        <Badge
          tone={
            job.state === "failed"
              ? "danger"
              : job.state === "completed"
                ? "accent"
                : "neutral"
          }
        >
          {friendly(job.state)}
        </Badge>
      </Row>
      <Fact label="Job" value={shortId(job.job_id)} />
      <Fact label="Accepted" value={dateLabel(job.accepted_at)} />
      <Fact
        label="Scope"
        value={
          typeof job.scope === "string"
            ? friendly(job.scope)
            : friendly(job.scope.kind)
        }
      />
      {job.failure_code && (
        <Notice tone="danger">
          {friendly(job.failure_code)}. This is not a completed request.
        </Notice>
      )}
      {job.state === "partially_retained" && (
        <Notice tone="warning">
          The named categories remain under the stated retention policy. This is
          not complete erasure of those categories.
        </Notice>
      )}
      {job.retained_categories.map((category, index) => (
        <Fact
          key={index}
          label={String(category.category ?? `Retained category ${index + 1}`)}
          value={String(
            category.reason ?? category.policy_basis ?? "Policy retention",
          )}
        />
      ))}
      {job.expires_at && (
        <Fact label="Logical expiry" value={dateLabel(job.expires_at)} />
      )}
      <Fact label="Policy version" value={job.policy_version} />
      <Button
        title="Refresh request status"
        secondary
        onPress={action(controller, () => controller.refreshJob(job.job_id))}
      />
      {job.kind === "export" && job.state === "completed" && (
        <Button
          title="Download and share export"
          onPress={action(controller, () =>
            controller.ask({
              title: "Share this export?",
              text: "The archive contains personal context and measurement evidence. Choose recipients carefully. The app removes its temporary copy after sharing or canceling, but cannot recall copies already shared.",
              confirm: "Download and open share sheet",
              action: () => controller.shareJob(job.job_id),
            }),
          )}
        />
      )}
    </Card>
  );
}
export function PrivacyScreen({ controller, model }: ScreenProps) {
  const state = model.state;
  const localCount =
      state?.checks.filter((c) => c.generation === state.generation).length ??
      0,
    unsynced =
      state?.checks.filter(
        (c) => c.delivery !== "synced" && c.delivery !== "quarantined",
      ).length ?? 0;
  return (
    <Page
      title="Privacy & data"
      eyebrow="You choose what leaves the device"
      onBack={action(controller, () =>
        controller.navigate(
          model.state?.acknowledgedNotice || model.identity
            ? "settings"
            : "welcome",
        ),
      )}
    >
      <Card>
        <Title small>Local save and cloud upload are separate</Title>
        <Paragraph>
          Every check is saved on this device first. An eligible account check
          uploads only after Upload check is confirmed. Guest checks never
          upload. Research enrollment is separate.
        </Paragraph>
        {state && (
          <SwitchRow
            title="Retry queued uploads automatically"
            value={state.preferences.retryQueuedAutomatically}
            onChange={(v) => {
              void controller.run(async () => {
                if (!v) {
                  await controller.changePreferences({
                    retryQueuedAutomatically: false,
                  });
                  return;
                }
                await controller.ask({
                  title: "Enable automatic retries?",
                  text: "Already requested uploads may retry when the app is active and a connection is available. This can use mobile data. New checks still require their own Upload check action. You can turn this off at any time.",
                  confirm: "Enable automatic retries",
                  action: () =>
                    controller.changePreferences({
                      retryQueuedAutomatically: true,
                    }),
                });
              });
            }}
            detail="Default off. Applies only to operations you already explicitly requested. It never queues a new check. Pending deletion or withdrawal may still retry to reconcile that exact privacy intent."
          />
        )}
      </Card>
      {state && (
        <>
          <Card>
            <Title small>Export your data</Title>
            <Paragraph>
              Choose device or synced records and review the exact scope.
              Exports include associated snapshots, profile context, all attempt
              evidence and separate alcohol data; unapproved raw artifacts are
              excluded.
            </Paragraph>
            <Button
              title="Review export options"
              onPress={action(controller, () =>
                controller.openExport({
                  source: "device",
                  selection: { kind: "all", session_ids: [] },
                }),
              )}
            />
          </Card>
          <Card>
            <Title small>Clear this device’s workspace</Title>
            <Fact label="Local checks" value={String(localCount)} />
            <Fact label="Unsynced checks" value={String(unsynced)} />
            <Paragraph>
              Clears this workspace’s cache and ordinary upload queue. It does
              not delete cloud records or another account’s local storage.
              Durable privacy receipts remain visible.
            </Paragraph>
            <Button
              title="Clear local records"
              secondary
              onPress={action(controller, () =>
                controller.ask({
                  title: "Clear this workspace’s local records?",
                  text: `${localCount} local checks, including ${unsynced} unsynced checks, will be removed. This cannot be undone on this device. Cloud records and other account workspaces are unaffected.`,
                  confirm: "Clear local records",
                  danger: true,
                  action: async () => {
                    const currentUnsynced =
                      controller
                        .getSnapshot()
                        .state?.checks.filter(
                          (check) =>
                            check.delivery !== "synced" &&
                            check.delivery !== "quarantined",
                        ).length ?? 0;
                    if (!currentUnsynced) {
                      await controller.clearLocal();
                      return;
                    }
                    await controller.ask({
                      title: `Discard ${currentUnsynced} unsynced checks?`,
                      text: "These checks do not have a confirmed synced copy. Clearing this workspace permanently discards their local evidence and ordinary pending uploads. Export them first if you need a copy. Durable privacy receipts remain.",
                      confirm: `Discard ${currentUnsynced} unsynced checks and clear`,
                      danger: true,
                      action: () => controller.clearLocal(),
                    });
                  },
                }),
              )}
            />
          </Card>
        </>
      )}
      {model.identity && state ? (
        <>
          <Card>
            <Title small>Cloud deletion</Title>
            <Paragraph>
              A fresh hosted sign-in to the same account confirms this request.
              Accepted deletion locks the current data generation. Old queued
              data cannot be restored into a new generation.
            </Paragraph>
            <Fact
              label="Account state"
              value={friendly(state.capabilities?.account_state)}
            />
            <Fact label="Data generation" value={String(state.generation)} />
            <Button
              title="Delete all synced data"
              secondary
              disabled={state.capabilities?.account_state !== "active"}
              onPress={action(controller, () =>
                controller.ask({
                  title: "Delete all synced data?",
                  text: "Requests deletion of this account’s synced checks, context, evidence and study data subject to the named retention policy. The account remains. Pending or failed status is not completed deletion. You must explicitly start a new empty workspace after completion.",
                  confirm: "Reauthenticate and request data deletion",
                  danger: true,
                  action: () => controller.deleteCloud("all_data"),
                }),
              )}
            />
            <Button
              title="Delete account"
              secondary
              disabled={state.capabilities?.account_state !== "active"}
              onPress={action(controller, () =>
                controller.ask({
                  title: "Delete this account and its data?",
                  text: "Requests removal of this account and its synced data, subject to named policy retention. Account deletion is irreversible once completed. Other users and local guest data are unaffected.",
                  confirm: "Reauthenticate and request account deletion",
                  danger: true,
                  action: () => controller.deleteCloud("account"),
                }),
              )}
            />
            {state.capabilities?.account_state ===
              "awaiting_generation_ack" && (
              <Button
                title="Start a new empty workspace"
                onPress={action(controller, () =>
                  controller.ask({
                    title: "Start a new empty workspace?",
                    text: "Deletion has completed. This acknowledges the new data generation. Old profile, checks, queues and study consent will not be restored.",
                    confirm: "Start new empty workspace",
                    action: () => controller.acknowledgeNewGeneration(),
                  }),
                )}
              />
            )}
          </Card>
          {state.queue
            .filter(
              (q) =>
                ["withdrawal", "deletion"].includes(q.kind) &&
                q.state !== "synced",
            )
            .map((q) => (
              <Card key={q.id}>
                <Title small>Pending {friendly(q.kind)} intent</Title>
                <Badge>{friendly(q.state)}</Badge>
                <Paragraph>
                  {q.error ??
                    "The exact request is durably recorded, but no completed server outcome has been confirmed."}
                </Paragraph>
                <Button
                  title="Reauthenticate and reconcile this request"
                  onPress={action(controller, () =>
                    controller.reconcilePrivacy(q.id),
                  )}
                />
              </Card>
            ))}
          {state.jobs.map((job) => (
            <JobCard key={job.job_id} job={job} controller={controller} />
          ))}
        </>
      ) : (
        <Notice>
          Cloud export and deletion require the owning account. Guest demo data
          has no cloud account and can be exported or cleared locally.
        </Notice>
      )}
      <Button
        title="Read application data notice"
        secondary
        onPress={action(controller, () => controller.navigate("notice"))}
      />
    </Page>
  );
}
export function ExportScreen({ controller, model }: ScreenProps) {
  const state = model.state!,
    entry = state.exportEntry,
    [reviewed, setReviewed] = useState(false);
  if (!entry)
    return (
      <Page title="Choose data to export">
        <Button
          title="Open privacy controls"
          onPress={action(controller, () => controller.navigate("privacy"))}
        />
      </Page>
    );
  return (
    <Page
      title="Review your export"
      eyebrow="Exact selection"
      onBack={action(controller, () => controller.navigate("privacy"))}
    >
      <Card>
        <Choice
          label="Record source"
          value={entry.source}
          options={[
            { value: "device", label: "On this device" },
            { value: "cloud", label: "Synced records" },
          ]}
          onChange={(source) => {
            setReviewed(false);
            void controller
              .changeExportSource(source)
              .catch((e) => controller.report(e));
          }}
        />
        <Fact
          label="Scope"
          value={
            entry.selection.kind === "all"
              ? "All records in the chosen source"
              : entry.selection.kind === "single"
                ? "Exactly one check"
                : `${entry.selection.session_ids.length} selected checks`
          }
        />
        {entry.selection.session_ids.map((id) => (
          <Fact key={id} label="Selected check" value={id} />
        ))}
        <Notice>
          Changing the source keeps the exact check IDs. Unavailable selected
          records cause an error; the selection is never expanded automatically.
        </Notice>
        <Paragraph>
          Includes the selected checks’ frozen context, component measurements,
          all capture attempts, integrity manifest, available result and
          associated alcohol evidence. Unapproved raw images and waveforms are
          excluded. “All” also includes the current profile when available.
        </Paragraph>
        <Paragraph muted>
          Limits: 500 checks, 50 MiB uncompressed, 64 MiB archive. An oversized
          selection fails as a whole; nothing is silently omitted.
        </Paragraph>
        <SwitchRow
          title="I have reviewed the source and selected data."
          detail="The export can contain sensitive personal and measurement information."
          value={reviewed}
          onChange={setReviewed}
        />
        <Button
          title={
            entry.source === "device"
              ? "Create local export and share"
              : "Request synced-data export"
          }
          disabled={!reviewed || (entry.source === "cloud" && !model.identity)}
          busy={model.busy}
          onPress={action(controller, () =>
            controller.ask({
              title: "Create this exact export?",
              text:
                entry.source === "device"
                  ? "The system share sheet will receive the selected archive. The private app copy is removed afterward; copies you share cannot be recalled."
                  : "The service will prepare the exact selected scope. A completed export expires after 24 hours. Download access is rechecked for this account and generation.",
              confirm:
                entry.source === "device"
                  ? "Create export and share"
                  : "Request export",
              action: () => controller.createExport(),
            }),
          )}
          testID="create-export"
        />
      </Card>
      {entry.selection.kind !== "all" && (
        <Button
          title="Choose all records instead"
          secondary
          onPress={action(controller, () =>
            controller.ask({
              title: "Replace the exact check selection with all records?",
              text: "This expands the export scope to all records in the chosen source. You will review a new summary before requesting an export.",
              confirm: "Review all-records selection",
              action: async () => {
                setReviewed(false);
                await controller.openExport({
                  source: entry.source,
                  selection: { kind: "all", session_ids: [] },
                });
              },
            }),
          )}
        />
      )}
      {state.jobs
        .filter((job) => job.kind === "export")
        .map((job) => (
          <JobCard key={job.job_id} job={job} controller={controller} />
        ))}
    </Page>
  );
}
function StudyCard({
  study,
  controller,
}: {
  study: JsonObject;
  controller: ScreenProps["controller"];
}) {
  const [expanded, setExpanded] = useState(false),
    [accepted, setAccepted] = useState(false),
    text = String(study.document_text ?? ""),
    hash = String(study.document_sha256 ?? ""),
    assessment = assessStudyConsent(study),
    verified = assessment.documentValid,
    consent = assessment.receipt;
  return (
    <Card>
      <Title small>{String(study.name ?? study.study_id)}</Title>
      <Badge>
        {study.local_withdrawal_pending
          ? "Withdrawal pending"
          : assessment.current
            ? "Current consent recorded"
            : assessment.needsFreshInvitation
              ? "New invitation required"
              : consent?.state === "active"
                ? "Updated information requires consent"
                : consent
                  ? friendly(consent.state)
                  : "Invitation available"}
      </Badge>
      <Fact label="Study" value={String(study.study_id)} />
      <Fact
        label="Document version"
        value={String(study.document_version ?? "Unavailable")}
      />
      <Paragraph>
        {String(
          study.retention_summary ??
            "Review the exact approved document for retention information.",
        )}
      </Paragraph>
      <Button
        title={
          expanded
            ? "Hide study information"
            : "Read complete study information"
        }
        secondary
        onPress={() => setExpanded((v) => !v)}
      />
      {expanded &&
        (verified ? (
          <>
            <Paragraph>{text}</Paragraph>
            <Fact label="Verified SHA-256" value={hash} />
          </>
        ) : (
          <Notice tone="danger">
            The study document is missing, oversized, or failed its digest
            check. Consent is unavailable.
          </Notice>
        ))}
      {assessment.needsFreshInvitation && (
        <Notice>
          You withdrew from this invitation. A new server-issued invitation is
          required before you can consent again; refreshing this document does
          not reverse withdrawal.
        </Notice>
      )}
      {assessment.mayAccept && (
        <>
          <SwitchRow
            title="I consent to this exact study document."
            value={accepted}
            onChange={setAccepted}
            detail="Optional and separate from account sign-in or the application notice."
          />
          <Button
            title="Reauthenticate and record study consent"
            disabled={!expanded || !verified || !accepted}
            onPress={action(controller, () =>
              controller.ask({
                title: "Record consent for this study?",
                text: `Records your affirmative consent to document ${study.document_version}. No measurements are uploaded by this action, and unqualified hardware remains unavailable.`,
                confirm: "Reauthenticate and consent",
                action: () => controller.consent(study),
              }),
            )}
          />
          <Button
            title="Decline and return"
            secondary
            onPress={action(controller, () => controller.navigate("settings"))}
          />
        </>
      )}
      {consent?.state === "active" && (
        <Button
          title="Withdraw from this study"
          secondary
          onPress={action(controller, () =>
            controller.ask({
              title: "Withdraw from this study?",
              text: "The app stops this study’s local work and queues your exact withdrawal. The request remains pending until the service confirms it. Previously accepted data follows the study retention policy; withdrawal and deletion are separate.",
              confirm: "Stop local work and request withdrawal",
              danger: true,
              action: () => controller.withdraw(String(study.study_id)),
            }),
          )}
        />
      )}
    </Card>
  );
}
export function StudiesScreen({ controller, model }: ScreenProps) {
  return (
    <Page
      title="Research access"
      eyebrow="Separate, explicit consent"
      onBack={action(controller, () => controller.navigate("settings"))}
    >
      <Card>
        <Title small>No automatic enrollment</Title>
        <Paragraph>
          Only an account’s server-issued invitations appear here. Demo use,
          notice acknowledgment, sign-in and measurements do not enroll you. A
          study consent never enables an unqualified device or impairment model.
        </Paragraph>
        <Notice>
          Qualified human-study capture is unavailable in this release. It would
          require fresh online authorization and an approved configuration for
          every capture. Offline native practice remains uncalibrated.
        </Notice>
        {model.identity ? (
          <Button
            title="Refresh invitations and membership"
            secondary
            onPress={action(controller, () => controller.refreshStudies())}
          />
        ) : (
          <Button
            title="Sign in to view invitations"
            onPress={action(controller, () => controller.signIn())}
          />
        )}
      </Card>
      {model.identity && !model.state?.studies.length && (
        <Card>
          <Title small>No study invitations</Title>
          <Paragraph>
            No active invitation is available to this account. An app user
            cannot grant themselves a study role or approved hardware
            configuration.
          </Paragraph>
        </Card>
      )}
      {model.state?.studies.map((study) => (
        <StudyCard
          key={JSON.stringify([
            study.study_id,
            study.invitation_id,
            study.document_version,
            study.document_sha256,
          ])}
          study={study}
          controller={controller}
        />
      ))}
    </Page>
  );
}
export function AlcoholScreen({ controller, model }: ScreenProps) {
  const check = controller.check;
  return (
    <Page
      title="Alcohol measurement"
      eyebrow="Separate analyte · separate evidence"
      onBack={action(controller, () => controller.navigate("home"))}
    >
      <Card>
        <Badge tone="warning">Qualified capture unavailable</Badge>
        <Title small>Requires a qualified breath instrument</Title>
        <Paragraph>
          A quantitative result needs an approved method, device identity,
          calibration, units, timing, quality and quantification limits. This
          release cannot infer breath alcohol from heart rate, ECG, pupil
          measurements or a reaction task.
        </Paragraph>
        <Fact label="Supported reporting unit" value="mg/L breath alcohol" />
        <Fact label="Blood alcohol conversion" value="Unavailable" />
        <Fact label="Driving threshold or clearance" value="Unavailable" />
        <Fact
          label="Effect on cannabis classification"
          value="No classification exists"
        />
      </Card>
      {check && !check.frozen && check.kind !== "measurement" ? (
        <Card>
          <Title small>Fictional example for this demo check</Title>
          <Paragraph>
            Attach an explicitly simulated alcohol value to the current
            synthetic parent check. It remains a separate evidence component.
          </Paragraph>
          <Button
            title={
              check.alcohol
                ? "Fictional alcohol example already added"
                : "Add fictional alcohol example"
            }
            disabled={!!check.alcohol}
            onPress={action(controller, () => controller.simulate("alcohol"))}
          />
          <Button
            title="Return to check"
            secondary
            onPress={action(controller, () => controller.navigate("check"))}
          />
        </Card>
      ) : (
        <Notice>
          A fictional example is available only inside a newly created guest
          demo or local/QA engineering fixture. A saved check cannot be changed.
        </Notice>
      )}
      <Button
        title="Devices and connection"
        secondary
        onPress={action(controller, () => controller.navigate("device"))}
      />
    </Page>
  );
}
export function AboutScreen({ controller, model }: ScreenProps) {
  return (
    <Page
      title="About this release"
      eyebrow="One The Go Detection"
      onBack={action(controller, () =>
        controller.navigate(
          model.state?.acknowledgedNotice || model.identity
            ? "settings"
            : "welcome",
        ),
      )}
    >
      <Card>
        <Title small>Measurement-only software</Title>
        <Paragraph>
          This application organizes optional profile context, saliva
          measurements, eye and cardiac evidence, native reaction practice, and
          a separate alcohol channel. It preserves quality, provenance,
          timestamps and immutable evidence links.
        </Paragraph>
        <Notice tone="warning">
          No validated intoxication or impairment model is included.
          Measurements cannot be used as an app-provided driving clearance.
        </Notice>
        <Fact label="App version" value={BUILD.version} />
        <Fact label="Environment" value={BUILD.environment.toUpperCase()} />
        <Fact label="Application contract" value="1.0.0" />
        <Fact label="Measurement snapshot" value="0.1.0" />
        <Fact label="Inference" value="Compiled off" />
        <Fact
          label="Native runtime"
          value={`${Platform.OS} ${String(Platform.Version)}`}
        />
        <Fact
          label="Build number"
          value={Constants.nativeBuildVersion ?? "Development / web preview"}
        />
        <Fact
          label="Toolchain"
          value="Expo 57 · React Native 0.86 · Node 22.13+"
        />
        <Fact
          label="Android support"
          value="Minimum API 24 · compile/target API 36"
        />
        <Fact label="iOS support" value="Minimum iOS 16.4 · Xcode 26.4+" />
        <Paragraph muted>
          Host software checks are recorded in the repository verification
          report. Physical Android/iPhone acquisition, OS permission
          round-trips, screen-reader review and calibrated timing remain
          unexecuted release checks until their evidence is recorded.
        </Paragraph>
      </Card>
      <Card>
        <Title small>What remains a qualification gate</Title>
        <Paragraph>
          Human assay validation, optical scale and photometric testing, ECG
          electrical/device safety, breath-instrument validation, physical
          reaction timing calibration, approved study authorization, regulatory
          decisions and a clinically validated inference model require evidence
          outside this software build.
        </Paragraph>
      </Card>
      <Button
        title="Read application notice"
        secondary
        onPress={action(controller, () => controller.navigate("notice"))}
      />
    </Page>
  );
}
export function StatusScreen({ controller, model }: ScreenProps) {
  const readiness = syncReadiness(model.config, BUILD.version);
  return (
    <Page
      title="Service & availability"
      eyebrow={BUILD.environment.toUpperCase()}
      onBack={action(controller, () => controller.navigate("home"))}
    >
      <Card>
        <Fact
          label="Connection"
          value={
            model.offline
              ? "Offline / service unreachable"
              : "Last request connected"
          }
        />
        <Fact
          label="Current configuration"
          value={
            model.config ? "Verified environment and issuer" : "Not loaded"
          }
        />
        <Fact
          label="Service maintenance"
          value={
            model.config?.maintenance
              ? "Active · new account writes paused"
              : "Not announced"
          }
        />
        <Notice tone={readiness.allowed ? "neutral" : "warning"}>
          {readiness.message}
        </Notice>
        <Fact label="Current app version" value={BUILD.version} />
        <Fact
          label="Minimum supported app"
          value={
            model.config?.minimum_app_version ?? "Configuration not loaded"
          }
        />
        <Fact label="Inference" value="Unavailable in every environment" />
        <Button
          title="Refresh service status"
          onPress={action(controller, async () => {
            await controller.refreshConfig();
            await controller.refreshCapabilities();
          })}
        />
      </Card>
      {Object.entries(
        model.state?.capabilities?.channels ?? {
          saliva: {
            available: false,
            reason_codes: ["NO_QUALIFIED_CONFIGURATION"],
          },
          eyes: {
            available: false,
            reason_codes: ["NO_QUALIFIED_CONFIGURATION"],
          },
          cardiac: {
            available: false,
            reason_codes: ["NO_QUALIFIED_CONFIGURATION"],
          },
          ecg: {
            available: false,
            reason_codes: ["NO_QUALIFIED_CONFIGURATION"],
          },
          alcohol: {
            available: false,
            reason_codes: ["NO_QUALIFIED_CONFIGURATION"],
          },
        },
      ).map(([channel, cap]) => (
        <Card key={channel}>
          <Title small>{friendly(channel)}</Title>
          <Badge tone="warning">Qualified acquisition unavailable</Badge>
          <Paragraph muted>
            {cap.reason_codes.map(friendly).join(" · ") ||
              "This compiled release does not contain a qualified acquisition implementation."}
          </Paragraph>
        </Card>
      ))}
      <Notice>
        Cached availability explains the interface. It never authorizes a human
        capture offline or enables a model.
      </Notice>
    </Page>
  );
}
