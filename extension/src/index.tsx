import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { DataProvider } from "./context/DataContext";
import { ThemeProvider } from "./context/ThemeContext";
import { TimeProvider } from "./context/TimeContext";
import { StorageProvider } from "./context/StorageContext";
import { MixpanelProvider } from "./context/MixpanelContext";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <TimeProvider>
    <StorageProvider>
      <MixpanelProvider>
        <DataProvider>
          <ThemeProvider>
            <App />
          </ThemeProvider>
        </DataProvider>
      </MixpanelProvider>
    </StorageProvider>
  </TimeProvider>
);
