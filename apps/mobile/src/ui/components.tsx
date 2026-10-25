import React, { useEffect, useRef } from "react";
import {
  ActivityIndicator,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
  type StyleProp,
  type TextInputProps,
  type ViewStyle,
} from "react-native";
import { useReducedMotion, useTheme } from "./theme";
import {
  scheduleAccessibilityFocus,
  useAccessibilityNavigation,
} from "./accessibility";

export const Title = React.forwardRef<
  Text,
  { children: React.ReactNode; small?: boolean; focusable?: boolean }
>(function Title({ children, small = false, focusable = false }, ref) {
  const c = useTheme();
  return (
    <Text
      ref={ref}
      accessible
      {...(Platform.OS === "web" && focusable ? { tabIndex: -1 } : {})}
      accessibilityRole="header"
      style={{
        color: c.ink,
        fontSize: small ? 23 : 32,
        fontWeight: "700",
        letterSpacing: -0.6,
        lineHeight: small ? 30 : 40,
      }}
    >
      {children}
    </Text>
  );
});
export function Paragraph({
  children,
  muted = false,
  style,
}: {
  children: React.ReactNode;
  muted?: boolean;
  style?: StyleProp<ViewStyle>;
}) {
  const c = useTheme();
  return (
    <Text
      style={[
        { color: muted ? c.secondary : c.ink, fontSize: 16, lineHeight: 25 },
        style,
      ]}
    >
      {children}
    </Text>
  );
}
export function Label({ children }: { children: React.ReactNode }) {
  const c = useTheme();
  return (
    <Text
      style={{
        color: c.secondary,
        fontSize: 12,
        fontWeight: "700",
        letterSpacing: 1.5,
        textTransform: "uppercase",
      }}
    >
      {children}
    </Text>
  );
}
export function Card({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}) {
  const c = useTheme();
  return (
    <View
      style={[
        {
          backgroundColor: c.surface,
          padding: 22,
          borderRadius: 22,
          gap: 13,
          borderWidth: 1,
          borderColor: c.line,
        },
        style,
      ]}
    >
      {children}
    </View>
  );
}
export function Row({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}) {
  return (
    <View
      style={[
        {
          flexDirection: "row",
          flexWrap: "wrap",
          alignItems: "center",
          gap: 10,
        },
        style,
      ]}
    >
      {children}
    </View>
  );
}
export function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "accent" | "warning" | "danger";
}) {
  const c = useTheme();
  const bg =
      tone === "accent"
        ? c.accentSoft
        : tone === "warning"
          ? c.warningSoft
          : tone === "danger"
            ? c.dangerSoft
            : c.surfaceMuted,
    fg =
      tone === "accent"
        ? c.accent
        : tone === "warning"
          ? c.warning
          : tone === "danger"
            ? c.danger
            : c.secondary;
  return (
    <View
      style={{
        alignSelf: "flex-start",
        borderRadius: 8,
        backgroundColor: bg,
        paddingVertical: 6,
        paddingHorizontal: 10,
      }}
    >
      <Text style={{ color: fg, fontSize: 12, fontWeight: "700" }}>
        {children}
      </Text>
    </View>
  );
}
export function Button({
  title,
  onPress,
  secondary = false,
  danger = false,
  disabled = false,
  busy = false,
  testID,
  compact = false,
}: {
  title: string;
  onPress: () => void;
  secondary?: boolean;
  danger?: boolean;
  disabled?: boolean;
  busy?: boolean;
  testID?: string;
  compact?: boolean;
}) {
  const c = useTheme(),
    trigger = useRef<View>(null),
    navigation = useAccessibilityNavigation();
  return (
    <Pressable
      ref={trigger}
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityState={{ disabled: disabled || busy, busy }}
      testID={testID}
      disabled={disabled || busy}
      onPress={() => {
        navigation.origin.current = {
          target: trigger.current,
          routeKey: navigation.routeKey,
        };
        onPress();
      }}
      style={({ pressed }) => ({
        minHeight: 50,
        paddingVertical: 13,
        paddingHorizontal: compact ? 16 : 22,
        borderRadius: 13,
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "row",
        gap: 10,
        borderWidth: 1,
        borderColor: secondary ? c.line : "transparent",
        backgroundColor: disabled
          ? c.surfaceMuted
          : secondary
            ? c.surface
            : danger
              ? c.danger
              : c.accent,
        opacity: pressed ? (danger && !secondary ? 0.9 : 0.75) : 1,
        alignSelf: compact ? "flex-start" : "stretch",
      })}
    >
      {busy && (
        <ActivityIndicator
          color={secondary ? c.accent : danger ? c.onDanger : c.onAccent}
        />
      )}
      <Text
        style={{
          fontSize: 15,
          fontWeight: "700",
          textAlign: "center",
          color: disabled
            ? c.secondary
            : secondary
              ? c.ink
              : danger
                ? c.onDanger
                : c.onAccent,
        }}
      >
        {title}
      </Text>
    </Pressable>
  );
}
export function ActionRow({
  title,
  detail,
  onPress,
  glyph = "›",
  disabled = false,
}: {
  title: string;
  detail?: string;
  onPress: () => void;
  glyph?: string;
  disabled?: boolean;
}) {
  const c = useTheme();
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      accessibilityRole="button"
      accessibilityLabel={`${title}${detail ? `. ${detail}` : ""}`}
      accessibilityState={{ disabled }}
      style={({ pressed }) => ({
        minHeight: 66,
        paddingVertical: 14,
        flexDirection: "row",
        gap: 16,
        alignItems: "center",
        borderBottomWidth: 1,
        borderBottomColor: c.line,
        opacity: pressed ? 0.7 : 1,
      })}
    >
      <View style={{ flex: 1, gap: 4 }}>
        <Text style={{ fontSize: 16, color: c.ink, fontWeight: "600" }}>
          {title}
        </Text>
        {detail && (
          <Text style={{ fontSize: 13, lineHeight: 20, color: c.secondary }}>
            {detail}
          </Text>
        )}
      </View>
      <Text style={{ color: c.accent, fontSize: 25 }}>{glyph}</Text>
    </Pressable>
  );
}
export function Field({
  label,
  helper,
  error,
  inputRef,
  ...props
}: TextInputProps & {
  label: string;
  helper?: string;
  error?: string;
  inputRef?: React.Ref<TextInput>;
}) {
  const c = useTheme();
  return (
    <View style={{ gap: 7, flexGrow: 1 }}>
      <Text style={{ fontSize: 14, fontWeight: "600", color: c.ink }}>
        {label}
      </Text>
      <TextInput
        {...props}
        ref={inputRef}
        accessibilityLabel={label}
        accessibilityHint={[helper, error].filter(Boolean).join(" ")}
        aria-invalid={!!error}
        placeholderTextColor={c.secondary}
        style={[
          {
            minHeight: 52,
            borderWidth: 1,
            borderColor: error ? c.danger : c.line,
            backgroundColor: c.background,
            padding: 13,
            borderRadius: 12,
            color: c.ink,
            fontSize: 16,
          },
          props.style,
        ]}
      />
      {helper && (
        <Text style={{ color: c.secondary, fontSize: 13, lineHeight: 20 }}>
          {helper}
        </Text>
      )}
      {error && (
        <Text
          accessibilityRole="alert"
          style={{ color: c.danger, fontSize: 13 }}
        >
          {error}
        </Text>
      )}
    </View>
  );
}
export function Choice<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
}) {
  const c = useTheme();
  return (
    <View style={{ gap: 8 }}>
      <Text style={{ fontSize: 14, fontWeight: "600", color: c.ink }}>
        {label}
      </Text>
      <Row>
        {options.map((option) => (
          <Pressable
            key={option.value}
            onPress={() => onChange(option.value)}
            accessibilityRole="radio"
            accessibilityLabel={option.label}
            accessibilityState={{ checked: value === option.value }}
            aria-checked={value === option.value}
            style={{
              minHeight: 48,
              justifyContent: "center",
              paddingHorizontal: 14,
              paddingVertical: 10,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: value === option.value ? c.accent : c.line,
              backgroundColor:
                value === option.value ? c.accentSoft : c.surface,
            }}
          >
            <Text
              style={{
                color: value === option.value ? c.accent : c.secondary,
                fontSize: 14,
                fontWeight: value === option.value ? "700" : "500",
              }}
            >
              {option.label}
            </Text>
          </Pressable>
        ))}
      </Row>
    </View>
  );
}
export function SwitchRow({
  title,
  detail,
  value,
  onChange,
  disabled = false,
}: {
  title: string;
  detail?: string;
  value: boolean;
  disabled?: boolean;
  onChange: (value: boolean) => void;
}) {
  const c = useTheme(),
    trigger = useRef<Switch>(null),
    navigation = useAccessibilityNavigation();
  return (
    <Row style={{ flexWrap: "nowrap" }}>
      <View style={{ flex: 1, gap: 5 }}>
        <Text style={{ fontSize: 16, fontWeight: "600", color: c.ink }}>
          {title}
        </Text>
        {detail && (
          <Text style={{ fontSize: 13, lineHeight: 20, color: c.secondary }}>
            {detail}
          </Text>
        )}
      </View>
      <Switch
        ref={trigger}
        value={value}
        disabled={disabled}
        accessibilityState={{ disabled, checked: value }}
        aria-disabled={disabled}
        aria-checked={value}
        onValueChange={(value) => {
          navigation.origin.current = {
            target: trigger.current,
            routeKey: navigation.routeKey,
          };
          onChange(value);
        }}
        accessibilityLabel={title}
        trackColor={{ true: c.accent }}
      />
    </Row>
  );
}
export function Fact({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  const c = useTheme();
  return (
    <View
      style={{
        flexDirection: "row",
        flexWrap: "wrap",
        gap: 8,
        justifyContent: "space-between",
        paddingVertical: 8,
        borderBottomWidth: 1,
        borderBottomColor: c.line,
      }}
    >
      <Text style={{ color: c.secondary, fontSize: 14 }}>{label}</Text>
      <Text
        selectable
        style={{
          color: c.ink,
          fontSize: 14,
          fontWeight: "600",
          maxWidth: "100%",
        }}
      >
        {value}
      </Text>
    </View>
  );
}
export function Metric({
  label,
  value,
  unit,
  detail,
}: {
  label: string;
  value: string;
  unit?: string;
  detail?: string;
}) {
  const c = useTheme();
  return (
    <View style={{ flexGrow: 1, flexBasis: 130, gap: 7, paddingVertical: 10 }}>
      <Label>{label}</Label>
      <Text
        style={{
          color: c.ink,
          fontSize: 29,
          fontWeight: "700",
          letterSpacing: -0.6,
        }}
      >
        {value}
        {unit && (
          <Text style={{ fontSize: 15, fontWeight: "500" }}> {unit}</Text>
        )}
      </Text>
      {detail && (
        <Text style={{ color: c.secondary, fontSize: 13, lineHeight: 19 }}>
          {detail}
        </Text>
      )}
    </View>
  );
}
export function Notice({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "warning" | "danger";
}) {
  const c = useTheme();
  return (
    <View
      accessibilityRole={tone === "danger" ? "alert" : undefined}
      style={{
        padding: 16,
        borderRadius: 14,
        backgroundColor:
          tone === "warning"
            ? c.warningSoft
            : tone === "danger"
              ? c.dangerSoft
              : c.accentSoft,
      }}
    >
      <Text
        style={{
          color:
            tone === "warning"
              ? c.warning
              : tone === "danger"
                ? c.danger
                : c.accent,
          fontSize: 14,
          lineHeight: 22,
        }}
      >
        {children}
      </Text>
    </View>
  );
}
export function Page({
  title,
  eyebrow,
  children,
  onBack,
  subtitle,
  initialScrollY = 0,
  onScrollY,
}: {
  title: string;
  eyebrow?: string;
  children: React.ReactNode;
  onBack?: () => void;
  subtitle?: string;
  initialScrollY?: number;
  onScrollY?: (y: number) => void;
}) {
  const scroll = useRef<ScrollView>(null),
    heading = useRef<Text>(null),
    restored = useRef(false),
    focusedRoute = useRef<string | null>(null),
    navigation = useAccessibilityNavigation();
  const current = useRef(navigation);
  current.current = navigation;
  useEffect(() => {
    restored.current = false;
  }, [title]);
  useEffect(() => {
    const key = `${navigation.routeKey}:${title}`;
    if (navigation.suspended) {
      focusedRoute.current = null;
      return;
    }
    if (navigation.backgroundBlocked || focusedRoute.current === key) return;
    return scheduleAccessibilityFocus(
      () => heading.current,
      () =>
        current.current.routeKey === navigation.routeKey &&
        !current.current.backgroundBlocked &&
        !current.current.suspended,
      () => {
        focusedRoute.current = key;
      },
    );
  }, [
    title,
    navigation.routeKey,
    navigation.backgroundBlocked,
    navigation.suspended,
  ]);
  return (
    <ScrollView
      ref={scroll}
      keyboardShouldPersistTaps="handled"
      onContentSizeChange={() => {
        if (!restored.current) {
          restored.current = true;
          scroll.current?.scrollTo({
            y: Math.max(
              0,
              Number.isFinite(initialScrollY) ? initialScrollY : 0,
            ),
            animated: false,
          });
        }
      }}
      onScroll={(event) => {
        const y = event.nativeEvent.contentOffset.y;
        if (Number.isFinite(y)) onScrollY?.(Math.max(0, y));
      }}
      scrollEventThrottle={32}
      contentContainerStyle={{ padding: 24, paddingBottom: 40, gap: 20 }}
    >
      <View style={{ gap: 10 }}>
        {onBack && <Button compact secondary title="‹ Back" onPress={onBack} />}
        {eyebrow && <Label>{eyebrow}</Label>}
        <Title ref={heading} focusable>
          {title}
        </Title>
        {subtitle && <Paragraph muted>{subtitle}</Paragraph>}
      </View>
      {children}
    </ScrollView>
  );
}
export interface SheetSpec {
  title: string;
  text: string;
  confirm: string;
  danger?: boolean;
  interrupting?: boolean;
  action: () => Promise<void> | void;
  secondary?: { title: string; action: () => Promise<void> | void };
}
export function Confirmation({
  sheet,
  busy,
  onClose,
  onConfirm,
  onSecondary,
}: {
  sheet: SheetSpec | null;
  busy: boolean;
  onClose: () => void;
  onConfirm: () => void;
  onSecondary: () => void;
}) {
  const c = useTheme(),
    reducedMotion = useReducedMotion(),
    navigation = useAccessibilityNavigation();
  const cancelHeadingFocus = useRef<(() => void) | undefined>(undefined),
    cancelRestoreFocus = useRef<(() => void) | undefined>(undefined);
  const heading = useRef<Text>(null),
    previous = useRef(false),
    origin = useRef(navigation.origin.current),
    latest = useRef({ navigation, sheet });
  latest.current = { navigation, sheet };
  const focusHeading = () => {
    cancelHeadingFocus.current?.();
    cancelHeadingFocus.current = scheduleAccessibilityFocus(
      () => heading.current,
      () => !!latest.current.sheet && !latest.current.navigation.suspended,
    );
  };
  const restoreFocus = () => {
    cancelRestoreFocus.current?.();
    const saved = origin.current;
    cancelRestoreFocus.current = scheduleAccessibilityFocus(
      () => saved?.target,
      () =>
        !latest.current.sheet &&
        !latest.current.navigation.suspended &&
        saved?.routeKey === latest.current.navigation.routeKey,
    );
  };
  useEffect(
    () => () => {
      cancelHeadingFocus.current?.();
      cancelRestoreFocus.current?.();
    },
    [],
  );
  useEffect(() => {
    if (sheet) {
      const opening = !previous.current;
      if (opening) origin.current = navigation.origin.current;
      previous.current = true;
      // Initial focus waits for Modal.onShow, after its focus trap and entrance
      // animation are ready. A replacement sheet still needs a new heading.
      if (!opening) focusHeading();
      return () => cancelHeadingFocus.current?.();
    }
    if (!previous.current) return;
    previous.current = false;
    restoreFocus();
    return () => cancelRestoreFocus.current?.();
  }, [sheet, navigation.suspended, navigation.routeKey]);
  // Remove a dismissed dialog and its focus trap in the same render. Keeping a
  // hidden fade-out portal races destination focus and changing motion settings.
  if (!sheet) return null;
  return (
    <Modal
      visible
      transparent
      animationType={reducedMotion ? "none" : "fade"}
      onShow={() => {
        focusHeading();
      }}
      onDismiss={() => {
        if (!latest.current.sheet) restoreFocus();
      }}
      onRequestClose={onClose}
    >
      <View
        style={{
          flex: 1,
          backgroundColor: "#071B25AA",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <View
          role="dialog"
          aria-modal
          accessibilityLabel={sheet?.title}
          accessibilityViewIsModal
          style={{
            maxWidth: 500,
            width: "100%",
            alignSelf: "center",
            backgroundColor: c.surface,
            padding: 25,
            borderRadius: 24,
            gap: 18,
          }}
        >
          <Title ref={heading} focusable small>
            {sheet?.title}
          </Title>
          <Paragraph>{sheet?.text}</Paragraph>
          <Button
            title={sheet?.confirm ?? "Continue"}
            danger={sheet?.danger}
            busy={busy}
            onPress={onConfirm}
          />
          {sheet?.secondary && (
            <Button
              title={sheet.secondary.title}
              secondary
              disabled={busy}
              onPress={onSecondary}
            />
          )}
          <Button title="Cancel" secondary disabled={busy} onPress={onClose} />
        </View>
      </View>
    </Modal>
  );
}
export const layout = StyleSheet.create({
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 16 },
  column: { flexGrow: 1, flexBasis: 280, gap: 18 },
  divider: { height: 1 },
});
