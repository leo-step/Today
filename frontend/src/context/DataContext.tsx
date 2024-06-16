import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import moment from "moment";
import config from "../config";
import { useStorage } from "./StorageContext";

const DataContext = createContext<any>(null);

const DataProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState();
  const storage = useStorage();

  // TODO: handle error?
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

      const currentTime = moment.utc();
      const requestTime = moment.utc(JSON.parse(data).timestamp);
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
  }, []); // eslint-disable-line

  return <DataContext.Provider value={data}>{children}</DataContext.Provider>;
};

const useData = () => {
  return useContext(DataContext);
};

export { DataProvider, useData };
