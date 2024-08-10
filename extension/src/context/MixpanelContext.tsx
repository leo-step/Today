import React, { createContext, useContext, ReactNode } from "react";
import { useStorage } from "./StorageContext";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";
import config from "../config";
import { Article } from "../components/carousel/PrinceNews";

type EventData = {
  uuid: string;
  event: string;
  properties?: any;
};

type Mixpanel = {
  trackPageLoad: () => void;
  trackNewsClick: (article: Article) => void;
  trackLinksClick: (link: string) => void;
  trackDhallChange: (dhall: string) => void;
  trackCarouselChange: (widget: string) => void;
  trackNameChange: (name: string) => void;
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
    trackNewsClick: async (article: Article) => {
      const uuid = getUuid();
      const event: EventData = {
        uuid,
        event: "newsClick",
        properties: article,
      };
      await sendEvent(event);
    },
    trackLinksClick: async (link: string) => {
      const uuid = getUuid();
      const event: EventData = {
        uuid,
        event: "linksClick",
        properties: {
          link,
        },
      };
      await sendEvent(event);
    },
    trackDhallChange: async (dhall: string) => {
      const uuid = getUuid();
      const event: EventData = {
        uuid,
        event: "dhallChange",
        properties: {
          dhall
        },
      };
      await sendEvent(event);
    },
    trackCarouselChange: async (widget: string) => {
      const uuid = getUuid();
      const event: EventData = {
        uuid,
        event: "carouselChange",
        properties: {
          widget
        },
      };
      await sendEvent(event);
    },
    trackNameChange: async (name: string) => {
      const uuid = getUuid();
      const event: EventData = {
        uuid,
        event: "nameChange",
        properties: {
          name
        },
      };
      await sendEvent(event);
    }
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
