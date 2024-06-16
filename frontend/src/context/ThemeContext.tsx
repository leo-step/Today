import React, { createContext, useContext, ReactNode } from "react";
import moment from "moment";

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

const theme = themes[moment().day() % themes.length];

const ThemeContext = createContext<Theme>(theme);

const ThemeProvider = ({ children }: { children: ReactNode }) => {
  return (
    <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
  );
};

const useTheme = () => {
  return useContext(ThemeContext);
};

export { ThemeProvider, useTheme };
