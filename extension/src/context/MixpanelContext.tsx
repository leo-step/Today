import React, { createContext, useContext, ReactNode } from "react";
import { useStorage } from "./StorageContext";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";
import config from "../config";

type EventData = {
  uuid: string;
  event: string;
  properties?: any;
};

type Mixpanel = {
  trackPageLoad: () => void;
};

// Create context with a default value of null
const MixpanelContext = createContext<Mixpanel | null>(null);

const sendEvent = async (event: EventData) => {
  try {
    await axios.post(config.URL + "/track", event);
  } catch (error) {
    console.error("Failed to send event", error);
  }
};

const MixpanelProvider = ({ children }: { children: ReactNode }) => {
  const storage = useStorage();

  const getUuid = () => {
    let uuid = storage.getLocalStorage("uuid");
    if (!uuid) {
      uuid = uuidv4();
      storage.setLocalStorage("uuid", uuid);
    }
    return uuid;
  };

  const mixpanelContext: Mixpanel = {
    trackPageLoad: async () => {
      const uuid = getUuid();
      const event: EventData = {
        uuid,
        event: "pageLoad",
        properties: storage.getLocalStorageObject(),
      };
      await sendEvent(event);
    },
  };

  return (
    <MixpanelContext.Provider value={mixpanelContext}>
      {children}
    </MixpanelContext.Provider>
  );
};

// Custom hook to use Mixpanel
const useMixpanel = () => {
  const context = useContext(MixpanelContext);
  if (!context) {
    throw new Error("useMixpanel must be used within a MixpanelProvider");
  }
  return context;
};

export { MixpanelProvider, useMixpanel };
