import React, { createContext, useContext, useMemo, useRef } from "react";
import {
  AccessibilityInfo,
  findNodeHandle,
  InteractionManager,
  Platform,
} from "react-native";

// Native accessibility focus and browser keyboard/AT focus use different APIs.
// Delaying until interactions/layout settle avoids addressing an unmounted title.
export function scheduleAccessibilityFocus(
  target: () => unknown,
  isCurrent: () => boolean = () => true,
  onFocused?: () => void,
) {
  const documentAtSchedule =
    Platform.OS === "web" && typeof document !== "undefined" ? document : null;
  const initialFocus = documentAtSchedule?.activeElement;
  let cancelled = false;
  let frame: ReturnType<typeof requestAnimationFrame> | undefined;
  const interaction = InteractionManager.runAfterInteractions(() => {
    if (cancelled) return;
    frame = requestAnimationFrame(() => {
      if (cancelled || !isCurrent()) return;
      const node = target();
      if (!node) return;
      if (Platform.OS === "web") {
        const element = node as {
          isConnected?: boolean;
          focus?: (options: { preventScroll: boolean }) => void;
        };
        if (element.isConnected === false || !element.focus) return;
        // A user can Tab or click while the destination is settling. Their newer
        // explicit focus takes precedence over this deferred route handoff.
        if (
          documentAtSchedule &&
          documentAtSchedule.activeElement !== initialFocus &&
          documentAtSchedule.activeElement !== documentAtSchedule.body &&
          documentAtSchedule.activeElement !== node
        )
          return;
        element.focus({ preventScroll: true });
      } else {
        const handle = findNodeHandle(
          node as Parameters<typeof findNodeHandle>[0],
        );
        if (handle === null) return;
        AccessibilityInfo.setAccessibilityFocus(handle);
      }
      onFocused?.();
    });
  });
  return () => {
    cancelled = true;
    interaction.cancel();
    if (frame !== undefined) cancelAnimationFrame(frame);
  };
}

type FocusOrigin = { target: unknown; routeKey: string };
const AccessibilityNavigation = createContext({
  routeKey: "standalone",
  backgroundBlocked: false,
  suspended: false,
  origin: { current: null as FocusOrigin | null },
});
export function NavigationAccessibilityProvider({
  routeKey,
  backgroundBlocked,
  suspended,
  children,
}: {
  routeKey: string;
  backgroundBlocked: boolean;
  suspended: boolean;
  children: React.ReactNode;
}) {
  const origin = useRef<FocusOrigin | null>(null);
  const value = useMemo(
    () => ({ routeKey, backgroundBlocked, suspended, origin }),
    [routeKey, backgroundBlocked, suspended],
  );
  return (
    <AccessibilityNavigation.Provider value={value}>
      {children}
    </AccessibilityNavigation.Provider>
  );
}
export const useAccessibilityNavigation = () =>
  useContext(AccessibilityNavigation);
