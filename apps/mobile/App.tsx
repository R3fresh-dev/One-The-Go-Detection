import React, {
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
} from "react";
import {
  ActivityIndicator,
  AppState,
  BackHandler,
  Platform,
  Pressable,
  Text,
  View,
  useWindowDimensions,
} from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { AppController } from "./src/controller";
import type { Route } from "./src/core/types";
import { BUILD } from "./src/platform/config";
import {
  AboutScreen,
  AlcoholScreen,
  DeviceScreen,
  ExportScreen,
  HistoryScreen,
  PrivacyScreen,
  SettingsScreen,
  StatusScreen,
  StudiesScreen,
} from "./src/ui/manage";
import {
  HomeScreen,
  LockedScreen,
  NoticeScreen,
  ProfileScreen,
  WelcomeScreen,
  action,
} from "./src/ui/account";
import { CheckScreen, EvidenceScreen, ResultScreen } from "./src/ui/checks";
import { RawRecordingsScreen } from "./src/ui/raw-recordings";
import { Button, Confirmation, Notice } from "./src/ui/components";
import { ThemeProvider, useTheme } from "./src/ui/theme";

const primary: { route: Route; label: string; glyph: string }[] = [
  { route: "home", label: "Home", glyph: "⌂" },
  { route: "check", label: "Check", glyph: "+" },
  { route: "history", label: "History", glyph: "≡" },
  { route: "settings", label: "Settings", glyph: "⚙" },
];
class AppErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <SafeAreaView
        style={{
          flex: 1,
          backgroundColor: "#F5F6F2",
          justifyContent: "center",
          padding: 28,
          gap: 18,
        }}
      >
        <Text style={{ color: "#122B35", fontSize: 25, fontWeight: "700" }}>
          This view could not be opened
        </Text>
        <Text style={{ color: "#49606A", fontSize: 16, lineHeight: 25 }}>
          Your saved records remain in their original workspace. Close and
          reopen the app. A native capture interrupted by this error is not a
          valid completed task.
        </Text>
      </SafeAreaView>
    ) : (
      this.props.children
    );
  }
}
export default function App() {
  return (
    <SafeAreaProvider>
      <AppErrorBoundary>
        <Application />
      </AppErrorBoundary>
    </SafeAreaProvider>
  );
}
function Application() {
  const controller = useMemo(() => new AppController(), []),
    model = useSyncExternalStore(
      controller.subscribe,
      controller.getSnapshot,
      controller.getSnapshot,
    ),
    [privateCover, setPrivateCover] = useState(false);
  useEffect(() => {
    void controller.initialize();
    const subscription = AppState.addEventListener("change", (state) => {
      setPrivateCover(state !== "active");
      void (
        state === "active" ? controller.foregrounded() : controller.background()
      ).catch((e) => controller.report(e));
    });
    const blur =
      Platform.OS === "android"
        ? AppState.addEventListener("blur", () => {
            setPrivateCover(true);
            void controller
              .stopActive("FOCUS_LOST")
              .catch((e) => controller.report(e));
          })
        : null;
    const focus =
      Platform.OS === "android"
        ? AppState.addEventListener("focus", () => setPrivateCover(false))
        : null;
    const timer = setInterval(() => {
      void controller.tick().catch((e) => controller.report(e));
    }, 3000);
    const back = BackHandler.addEventListener("hardwareBackPress", () => {
      const current = controller.getSnapshot();
      if (current.activeTask || current.activeEye) {
        void controller
          .stopActive("ROUTE_HIDDEN")
          .catch((e) => controller.report(e));
        return true;
      }
      if (current.sheet) {
        controller.closeSheet();
        return true;
      }
      if (!["home", "welcome"].includes(current.route)) {
        void controller
          .navigate(
            current.identity || current.state?.acknowledgedNotice
              ? "home"
              : "welcome",
          )
          .catch((e) => controller.report(e));
        return true;
      }
      return false;
    });
    return () => {
      clearInterval(timer);
      subscription.remove();
      blur?.remove();
      focus?.remove();
      back.remove();
      void controller.dispose();
    };
  }, [controller]);
  return (
    <ThemeProvider mode={model.state?.preferences.theme ?? "system"}>
      <Shell
        controller={controller}
        model={model}
        privateCover={privateCover}
      />
    </ThemeProvider>
  );
}
function Shell({
  controller,
  model,
  privateCover,
}: {
  controller: AppController;
  model: ReturnType<AppController["getSnapshot"]>;
  privateCover: boolean;
}) {
  const colors = useTheme(),
    { width } = useWindowDimensions(),
    wide = width >= 980,
    showNav =
      !!model.state &&
      !model.locked &&
      (!!model.identity || !!model.state.acknowledgedNotice) &&
      !model.activeTask &&
      !model.activeEye;
  const props = { controller, model },
    screens: Record<Route, React.ReactNode> = {
      welcome: <WelcomeScreen {...props} />,
      notice: <NoticeScreen {...props} key={model.state?.notice?.sha256} />,
      home: model.state ? (
        <HomeScreen
          {...props}
          key={`${controller.epoch}:${model.state.generation}`}
        />
      ) : null,
      profile: model.state ? (
        <ProfileScreen
          {...props}
          key={`${controller.epoch}:${model.state.generation}:${model.profileConflict ? "conflict" : "normal"}`}
        />
      ) : null,
      device: <DeviceScreen {...props} />,
      check: <CheckScreen {...props} />,
      result: <ResultScreen {...props} />,
      history: model.state ? <HistoryScreen {...props} /> : null,
      evidence: <EvidenceScreen {...props} />,
      settings: model.state ? <SettingsScreen {...props} /> : null,
      privacy: <PrivacyScreen {...props} />,
      export: model.state ? <ExportScreen {...props} /> : null,
      studies: <StudiesScreen {...props} />,
      "raw-recordings": <RawRecordingsScreen {...props} />,
      alcohol: <AlcoholScreen {...props} />,
      about: <AboutScreen {...props} />,
      status: <StatusScreen {...props} />,
    };
  const nav = (vertical: boolean) => (
    <View
      accessibilityRole="tablist"
      style={{
        flexDirection: vertical ? "column" : "row",
        gap: vertical ? 9 : 0,
        padding: vertical ? 16 : 8,
        backgroundColor: colors.surface,
        borderTopWidth: vertical ? 0 : 1,
        borderColor: colors.line,
      }}
    >
      {primary.map((item) => {
        const selected =
          item.route === model.route ||
          (item.route === "history" &&
            ["result", "evidence", "export"].includes(model.route));
        return (
          <Pressable
            key={item.route}
            accessibilityRole="tab"
            accessibilityLabel={item.label}
            accessibilityState={{ selected }}
            aria-selected={selected}
            onPress={action(controller, () => controller.navigate(item.route))}
            style={({ pressed }) => ({
              flex: vertical ? undefined : 1,
              minHeight: 58,
              flexDirection: vertical ? "row" : "column",
              justifyContent: vertical ? "flex-start" : "center",
              alignItems: "center",
              gap: vertical ? 14 : 3,
              paddingHorizontal: 15,
              paddingVertical: 10,
              backgroundColor: selected ? colors.accentSoft : "transparent",
              borderRadius: 13,
              opacity: pressed ? 0.7 : 1,
            })}
          >
            <Text
              style={{
                color: selected ? colors.accent : colors.secondary,
                fontSize: vertical ? 22 : 20,
              }}
            >
              {item.glyph}
            </Text>
            <Text
              style={{
                color: selected ? colors.accent : colors.secondary,
                fontSize: vertical ? 16 : 12,
                fontWeight: selected ? "700" : "500",
              }}
            >
              {item.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <StatusBar style={colors.background === "#0D2027" ? "light" : "dark"} />
      <View
        aria-hidden={!!model.sheet || privateCover}
        accessibilityElementsHidden={!!model.sheet || privateCover}
        importantForAccessibility={
          model.sheet || privateCover ? "no-hide-descendants" : "auto"
        }
        style={{
          flex: 1,
          flexDirection: wide ? "row" : "column",
          maxWidth: 1440,
          width: "100%",
          alignSelf: "center",
        }}
      >
        {wide && showNav && (
          <View
            style={{
              width: 245,
              backgroundColor: colors.surface,
              borderRightWidth: 1,
              borderColor: colors.line,
              paddingTop: 30,
            }}
          >
            <View style={{ paddingHorizontal: 24, paddingBottom: 30, gap: 8 }}>
              <Text
                style={{
                  color: colors.ink,
                  fontSize: 23,
                  fontWeight: "800",
                  letterSpacing: -0.5,
                }}
              >
                one the go<Text style={{ color: colors.accent }}>.</Text>
              </Text>
              <Text
                style={{
                  color: colors.secondary,
                  fontSize: 12,
                  lineHeight: 20,
                }}
              >
                MEASUREMENT COMPANION
              </Text>
            </View>
            {nav(true)}
            <View style={{ padding: 22, gap: 12, marginTop: "auto" }}>
              <Text
                style={{
                  color: colors.secondary,
                  fontSize: 13,
                  lineHeight: 21,
                }}
              >
                Evidence and context. No impairment verdict.
              </Text>
              <Text
                style={{
                  color: colors.accent,
                  fontSize: 12,
                  fontWeight: "700",
                }}
              >
                {BUILD.environment.toUpperCase()} · v{BUILD.version}
              </Text>
            </View>
          </View>
        )}
        <View style={{ flex: 1, minWidth: 0, maxWidth: 1100 }}>
          {!model.activeTask && !model.activeEye && (
            <View
              style={{
                paddingHorizontal: 24,
                paddingVertical: 15,
                flexDirection: "row",
                flexWrap: "wrap",
                justifyContent: "space-between",
                alignItems: "center",
                gap: 9,
                borderBottomWidth: 1,
                borderColor: colors.line,
              }}
            >
              <Text
                style={{
                  color: colors.ink,
                  fontSize: 18,
                  fontWeight: "800",
                  letterSpacing: -0.5,
                }}
              >
                one the go<Text style={{ color: colors.accent }}>.</Text>
              </Text>
              <View
                style={{ flexDirection: "row", alignItems: "center", gap: 8 }}
              >
                {model.busy && (
                  <ActivityIndicator
                    color={colors.accent}
                    accessibilityLabel="Saving or connecting"
                  />
                )}
                <Text
                  accessibilityLiveRegion="polite"
                  style={{
                    color: colors.secondary,
                    fontSize: 12,
                    fontWeight: "600",
                  }}
                >
                  {model.locked
                    ? "LOCKED"
                    : model.identity
                      ? `ACCOUNT · ${BUILD.environment.toUpperCase()}`
                      : "GUEST DEMO"}
                  {model.offline ? " · OFFLINE" : ""}
                </Text>
              </View>
            </View>
          )}
          {!model.activeTask && !model.activeEye && (
            <ContextStrip
              key={`${controller.epoch}:${model.state?.generation}`}
              browser={Platform.OS === "web"}
              guest={
                !!model.state?.acknowledgedNotice &&
                !model.identity &&
                model.route !== "welcome"
              }
            />
          )}
          {BUILD.hostedPreview && (
            <View
              accessibilityRole="text"
              testID="fictional-preview-banner"
              style={{
                paddingHorizontal: 24,
                paddingVertical: 12,
                backgroundColor: colors.accentSoft,
              }}
            >
              <Text style={{ color: colors.ink, fontSize: 13, lineHeight: 20 }}>
                FICTIONAL GUEST PREVIEW · Use invented values only. No account
                services, sensor permissions, raw recording or uploads.{" "}
                {Platform.OS === "web"
                  ? "Browser records last only until this page closes."
                  : "Fictional records are isolated in this app’s local preview workspace."}
              </Text>
            </View>
          )}
          {!model.activeTask &&
            !model.activeEye &&
            (model.error || model.message) && (
              <View
                style={{
                  paddingHorizontal: 24,
                  paddingVertical: 8,
                  gap: 8,
                  flexDirection: "row",
                  alignItems: "center",
                  backgroundColor: model.error
                    ? colors.dangerSoft
                    : colors.accentSoft,
                }}
              >
                <Text
                  accessibilityLiveRegion="polite"
                  style={{
                    flex: 1,
                    color: model.error ? colors.danger : colors.ink,
                    fontSize: 13,
                    lineHeight: 19,
                  }}
                >
                  {model.error ?? model.message}
                </Text>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel="Dismiss message"
                  onPress={() => controller.dismissError()}
                  style={{
                    minWidth: 48,
                    minHeight: 48,
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Text style={{ color: colors.secondary, fontSize: 22 }}>
                    ×
                  </Text>
                </Pressable>
              </View>
            )}
          <View style={{ flex: 1, minHeight: 0 }}>
            {model.loading ? (
              <View
                style={{
                  flex: 1,
                  justifyContent: "center",
                  alignItems: "center",
                  gap: 16,
                }}
              >
                <ActivityIndicator color={colors.accent} />
                <Text style={{ color: colors.secondary }}>
                  Opening your workspace…
                </Text>
              </View>
            ) : model.locked ? (
              <LockedScreen {...props} />
            ) : (
              (screens[model.route] ?? <WelcomeScreen {...props} />)
            )}
          </View>
          {!wide && showNav && nav(false)}
        </View>
      </View>
      <Confirmation
        sheet={model.activeTask || model.activeEye ? null : model.sheet}
        busy={model.sheet?.interrupting ? model.privacyBusy : model.busy}
        onClose={() => controller.closeSheet()}
        onConfirm={() =>
          void (model.sheet?.interrupting
            ? controller.runPrivacy(() => controller.confirmSheet())
            : controller.run(() => controller.confirmSheet()))
        }
        onSecondary={action(controller, () => controller.confirmSheet(true))}
      />
      {privateCover && (
        <View
          accessibilityViewIsModal
          style={{
            position: "absolute",
            inset: 0,
            backgroundColor: colors.navy,
            justifyContent: "center",
            alignItems: "center",
            gap: 14,
            padding: 28,
          }}
        >
          <Text style={{ color: "#FFFFFF", fontSize: 28, fontWeight: "700" }}>
            one the go.
          </Text>
          <Text style={{ color: "#D6E6E8", fontSize: 16 }}>
            Private workspace
          </Text>
        </View>
      )}
    </SafeAreaView>
  );
}
function ContextStrip({
  browser,
  guest,
}: {
  browser: boolean;
  guest: boolean;
}) {
  const colors = useTheme(),
    [expanded, setExpanded] = useState(false);
  if (!browser && !guest) return null;
  return (
    <View
      style={{
        paddingHorizontal: 24,
        backgroundColor: colors.warningSoft,
        borderBottomWidth: 1,
        borderColor: colors.line,
      }}
    >
      <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
        <View style={{ flex: 1, gap: 3, paddingVertical: 8 }}>
          {browser && (
            <Text style={{ color: colors.ink, fontSize: 12, lineHeight: 17 }}>
              Browser preview · memory only
            </Text>
          )}
          {guest && (
            <Text style={{ color: colors.ink, fontSize: 12, lineHeight: 17 }}>
              Guest demo · synthetic values · no uploads
            </Text>
          )}
        </View>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={
            expanded
              ? "Hide preview and demo details"
              : "Preview and demo details"
          }
          accessibilityState={{ expanded }}
          onPress={() => setExpanded((value) => !value)}
          style={{
            minHeight: 48,
            minWidth: 52,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Text
            style={{ color: colors.accent, fontSize: 13, fontWeight: "600" }}
          >
            {expanded ? "Hide" : "Details"}
          </Text>
        </Pressable>
      </View>
      {expanded && (
        <View style={{ paddingBottom: 12, gap: 8 }}>
          {browser && (
            <Text style={{ color: colors.ink, fontSize: 13, lineHeight: 20 }}>
              Reloading clears this browser workspace. Encrypted persistence and
              the native reaction task require an installed Android or iOS
              build.
            </Text>
          )}
          {guest && (
            <Text style={{ color: colors.ink, fontSize: 13, lineHeight: 20 }}>
              Sample and sensor values are synthetic. Native taps, when
              available, are uncalibrated practice. Guest data never uploads.
            </Text>
          )}
        </View>
      )}
    </View>
  );
}
