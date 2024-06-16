import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { DataProvider } from "./context/DataContext";
import { ThemeProvider } from "./context/ThemeContext";
import { TimeProvider } from "./context/TimeContext";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
root.render(
  <DataProvider>
    <ThemeProvider>
      <TimeProvider>
        <App />
      </TimeProvider>
    </ThemeProvider>
  </DataProvider>
);
