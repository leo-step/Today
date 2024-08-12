import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import config from "../config";
import { StorageKeys, useStorage } from "./StorageContext";
import { useTime } from "./TimeContext";
import { EventTypes, useMixpanel } from "./MixpanelContext";

const TICK_INTERVAL = 5000

const DataContext = createContext<any>(null);

type IntervalRef = {
  current: NodeJS.Timer | undefined
}

const DataProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState();
  const storage = useStorage();
  const mixpanel = useMixpanel();
  const time = useTime();

  const requestAndSetData = async () => {
    await axios.get(config.URL + "/extension/widget-data").then((res) => {
      storage.setLocalStorage(StorageKeys.DATA, JSON.stringify(res.data));
      setData(res.data);
    });
    mixpanel.trackEvent(EventTypes.FETCH_DATA, time.getUTC().toString())
  };

  const fetchData = async (intervalRef: any) => {
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
    } catch {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }
  };

  useEffect(() => {
    const intervalRef: IntervalRef = { current: undefined };
    fetchData(intervalRef);
    intervalRef.current = setInterval(() => fetchData(intervalRef), TICK_INTERVAL);
    return () => clearInterval(intervalRef.current);
  }, []);

  return <DataContext.Provider value={data}>{children}</DataContext.Provider>;
};

const useData = () => {
  return useContext(DataContext);
};

export { DataProvider, useData };
