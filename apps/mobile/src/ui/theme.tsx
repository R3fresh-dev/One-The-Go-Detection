import React, { createContext, useContext } from 'react';
import { useColorScheme } from 'react-native';
export const light = { background: '#F5F6F2', surface: '#FFFFFF', surfaceMuted: '#EDF1ED', ink: '#122B35', secondary: '#49606A', line: '#D8E1DC', accent: '#126557', accentSoft: '#E0F0E8', onAccent: '#FFFFFF', navy: '#12343D', warning: '#8A4A13', warningSoft: '#FFF0D8', danger: '#A72F35', dangerSoft: '#FCE9E8', white: '#FFFFFF' };
export const dark: typeof light = { background: '#0D2027', surface: '#18323B', surfaceMuted: '#223F48', ink: '#F3F6F1', secondary: '#BDCDC9', line: '#35535B', accent: '#8BD3B7', accentSoft: '#244E43', onAccent: '#0D2C22', navy: '#183C45', warning: '#F2BF83', warningSoft: '#473921', danger: '#FFB6BA', dangerSoft: '#482C33', white: '#FFFFFF' };
const Theme = createContext(light);
export function ThemeProvider({ mode, children }: { mode: 'system' | 'light' | 'dark'; children: React.ReactNode }) { const system = useColorScheme(); return <Theme.Provider value={mode === 'dark' || mode === 'system' && system === 'dark' ? dark : light}>{children}</Theme.Provider>; }
export const useTheme = () => useContext(Theme);
