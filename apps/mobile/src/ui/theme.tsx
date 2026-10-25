import React, { createContext, useContext, useEffect, useState } from "react";
import { AccessibilityInfo, useColorScheme } from "react-native";
import type { Preferences } from "../core/types";
export const light = {
  background: "#F5F6F2",
  surface: "#FFFFFF",
  surfaceMuted: "#EDF1ED",
  ink: "#122B35",
  secondary: "#49606A",
  line: "#D8E1DC",
  accent: "#126557",
  accentSoft: "#E0F0E8",
  onAccent: "#FFFFFF",
  navy: "#12343D",
  warning: "#8A4A13",
  warningSoft: "#FFF0D8",
  danger: "#A72F35",
  onDanger: "#FFFFFF",
  dangerSoft: "#FCE9E8",
  white: "#FFFFFF",
};
export const dark: typeof light = {
  background: "#0D2027",
  surface: "#18323B",
  surfaceMuted: "#223F48",
  ink: "#F3F6F1",
  secondary: "#BDCDC9",
  line: "#35535B",
  accent: "#8BD3B7",
  accentSoft: "#244E43",
  onAccent: "#0D2C22",
  navy: "#183C45",
  warning: "#F2BF83",
  warningSoft: "#473921",
  danger: "#FFB6BA",
  onDanger: "#3A1015",
  dangerSoft: "#482C33",
  white: "#FFFFFF",
};
const Theme = createContext(light);
const ReducedMotion = createContext(true);
export function ThemeProvider({
  mode,
  reducedMotion = "system",
  children,
}: {
  mode: "system" | "light" | "dark";
  reducedMotion?: Preferences["reducedMotion"];
  children: React.ReactNode;
}) {
  const system = useColorScheme();
  // Avoid decorative motion until the initial system setting is known.
  const [systemReducedMotion, setSystemReducedMotion] = useState(true);
  useEffect(() => {
    let active = true,
      changed = false;
    const subscription = AccessibilityInfo.addEventListener(
      "reduceMotionChanged",
      (value) => {
        changed = true;
        if (active) setSystemReducedMotion(value);
      },
    );
    void AccessibilityInfo.isReduceMotionEnabled()
      .then((value) => {
        if (active && !changed) setSystemReducedMotion(value);
      })
      .catch(() => {
        /* Keep reduced motion if the OS setting is unavailable. */
      });
    return () => {
      active = false;
      subscription.remove();
    };
  }, []);
  // Older persisted booleans are explicit choices; missing/unknown legacy values
  // follow the system without rewriting or discarding an existing workspace.
  const effective =
    typeof reducedMotion === "boolean" ? reducedMotion : systemReducedMotion;
  return (
    <Theme.Provider
      value={
        mode === "dark" || (mode === "system" && system === "dark")
          ? dark
          : light
      }
    >
      <ReducedMotion.Provider value={effective}>
        {children}
      </ReducedMotion.Provider>
    </Theme.Provider>
  );
}
export const useTheme = () => useContext(Theme);
export const useReducedMotion = () => useContext(ReducedMotion);
