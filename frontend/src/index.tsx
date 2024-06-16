import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { DataProvider } from "./context/DataContext";
import { ThemeProvider } from "./context/ThemeContext";
import { TimeProvider } from "./context/TimeContext";
import { StorageProvider } from "./context/StorageContext";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
// TODO: time provider above storage and data?
root.render(
  <TimeProvider>
    <StorageProvider>
      <DataProvider>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </DataProvider>
    </StorageProvider>
  </TimeProvider>
);
