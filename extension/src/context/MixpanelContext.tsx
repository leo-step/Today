import React, { createContext, useContext, ReactNode } from "react";
import { StorageKeys, useStorage } from "./StorageContext";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";

export enum EventTypes {
  PAGE_LOAD = "pageLoad",
  FETCH_DATA = "fetchData",
  NEWS_CLICK = "newsClick",
  LINKS_CLICK = "linksClick",
  DHALL_CHANGE = "dhallChange",
  CAROUSEL_CHANGE = "carouselChange",
  NAME_CHANGE = "nameChange",
  OPENED_CHAT = "openedChat"
}

type EventData = {
  uuid: string;
  event: string;
  properties?: any;
};

type Mixpanel = {
  // TODO: enum for events
  trackEvent: (eventType: EventTypes, properties: any) => void;
  // trackPageLoad: () => void;
  // trackNewsClick: (article: Article) => void;
  // trackLinksClick: (link: string) => void;
  // trackDhallChange: (dhall: string) => void;
  // trackCarouselChange: (widget: string) => void;
  // trackNameChange: (name: string) => void;
};

// Create context with a default value of null
const MixpanelContext = createContext<Mixpanel | null>(null);

const sendEvent = async (event: EventData) => {
  try {
    await axios.post("https://today-fastapi-nujm46x7ta-uc.a.run.app/api/track", event);
  } catch {}
};

const MixpanelProvider = ({ children }: { children: ReactNode }) => {
  const storage = useStorage();

  const getUuid = () => {
    let uuid = storage.getLocalStorage(StorageKeys.UUID);
    if (!uuid) {
      uuid = uuidv4();
      storage.setLocalStorage(StorageKeys.UUID, uuid);
    }
    return uuid;
  };

  const mixpanelContext: Mixpanel = {
    trackEvent: async (eventType: EventTypes, properties: any) => {
      const uuid = getUuid();
      if (typeof properties === "string") {
        properties = { property: properties };
      }
      const event: EventData = {
        uuid,
        event: eventType,
        properties,
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
