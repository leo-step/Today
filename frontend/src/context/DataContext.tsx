import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import config from "../config";
import { useStorage } from "./StorageContext";
import { useTime } from "./TimeContext";

const DataContext = createContext<any>(null);

type Backoff = {
  ticks: number;
  retries: number;
};

const MAX_BACKOFF_TICKS = 32;
const TICK_INTERVAL = 5000;

const DataProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState(); // TODO: is data updating while tab is open for a while?
  const storage = useStorage();
  const time = useTime();
  let backoff: Backoff = { ticks: 0, retries: 0 };

  const requestAndSetData = async () => {
    await axios.get(config.URL).then((res) => {
      storage.setLocalStorage("data", JSON.stringify(res.data));
      setData(res.data);
      backoff = { ticks: 0, retries: 0 };
    });
  };

  const fetchData = async () => {
    time.refresh?.();
    if (backoff.ticks > 0) {
      backoff.ticks -= 1;
      return;
    }
    try {
      const data = storage.getLocalStorage("data");
      if (!data) {
        await requestAndSetData();
      } else {
        const parsedData = JSON.parse(data);
        setData(parsedData);

        const currentTime = time.getUTC();
        const requestTime = time.parseUTC(parsedData.timestamp);
        if (
          config.URL === config.DEV ||
          currentTime.hour() !== requestTime.hour() ||
          !currentTime.isSame(requestTime, "date")
        ) {
          await requestAndSetData();
        }
      }
    } catch {
      backoff = {
        ticks: Math.min(2 ** backoff.retries, MAX_BACKOFF_TICKS),
        retries: backoff.retries + 1,
      };
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, TICK_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  return <DataContext.Provider value={data}>{children}</DataContext.Provider>;
};

const useData = () => {
  return useContext(DataContext);
};

export { DataProvider, useData };
