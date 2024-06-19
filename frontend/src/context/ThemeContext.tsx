import React, { createContext, useContext, ReactNode } from "react";
import { useTime } from "./TimeContext";

type Theme = {
  main: string;
  accent: string;
  background: string;
};

const themes: Theme[] = [
  { main: "#4c8300", accent: "#d86c0d", background: "0.jpeg" },
  { main: "#ffa84b", accent: "#978cff", background: "1.jpeg" },
  { main: "#1aa5ae", accent: "#ffa84b", background: "2.jpeg" },
  { main: "#f67205", accent: "#77c7fb", background: "3.jpeg" },
];

let theme = themes[0];

const ThemeContext = createContext<Theme>(theme);

const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const time = useTime();

  theme = themes[time.day % themes.length];

  document.body.setAttribute(
    "style",
    `background-image:url(backgrounds/${theme.background}) !important;`
  );

  return (
    <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
  );
};

const useTheme = () => {
  return useContext(ThemeContext);
};

export { ThemeProvider, useTheme };
