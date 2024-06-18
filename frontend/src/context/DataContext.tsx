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

const DataProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState();
  const storage = useStorage();
  const time = useTime();

  // TODO: handle error?
  // TODO: data has any type. is that a problem?
  const requestAndSetData = async () => {
    await axios.get(config.URL).then((res) => {
      storage.setLocalStorage("data", JSON.stringify(res.data));
      setData(res.data);
    });
  };

  const fetchData = async () => {
    const data = storage.getLocalStorage("data");
    if (!data) {
      await requestAndSetData();
    } else {
      const parsedData = JSON.parse(data);
      setData(parsedData);

      const currentTime = time.getUTC();
      const requestTime = time.parseUTC(parsedData.timestamp);
      if (
        config.URL === config.PROD || // TODO: change to DEV
        currentTime.hour() !== requestTime.hour() ||
        !currentTime.isSame(requestTime, "date")
      ) {
        await requestAndSetData();
      }
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  return <DataContext.Provider value={data}>{children}</DataContext.Provider>;
};

const useData = () => {
  return useContext(DataContext);
};

export { DataProvider, useData };
