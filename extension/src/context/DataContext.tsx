import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import { StorageKeys, useStorage } from "./StorageContext";
import { useTime } from "./TimeContext";
import { EventTypes, useMixpanel } from "./MixpanelContext";

const TICK_INTERVAL = 60000;

const DataContext = createContext<any>(null);

const DataProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState();
  const storage = useStorage();
  const mixpanel = useMixpanel();
  const time = useTime();

  const requestAndSetData = async () => {
    await axios.get("https://today-fastapi-nujm46x7ta-uc.a.run.app/api/extension/widget-data").then((res) => {
      storage.setLocalStorage(StorageKeys.DATA, JSON.stringify(res.data));
      setData(res.data);
    });
    mixpanel.trackEvent(EventTypes.FETCH_DATA, time.getUTC().toString());
  };

  const fetchData = async () => {
    time.refresh?.();
    try {
      const data = storage.getLocalStorage(StorageKeys.DATA);
      if (!data) {
        await requestAndSetData();
      } else {
        const parsedData = JSON.parse(data);
        setData(parsedData);

        const currentTime = time.getUTC();
        const requestTime = time.parseUTC(parsedData.timestamp);
        if (
          currentTime.hour() !== requestTime.hour() ||
          !currentTime.isSame(requestTime, "date")
        ) {
          await requestAndSetData();
        }
      }
    } catch {}
  };

  useEffect(() => {
    fetchData();
    const intervalRef: NodeJS.Timer = setInterval(fetchData, TICK_INTERVAL);
    return () => clearInterval(intervalRef);
  }, []);

  return <DataContext.Provider value={data}>{children}</DataContext.Provider>;
};

const useData = () => {
  return useContext(DataContext);
};

export { DataProvider, useData };
