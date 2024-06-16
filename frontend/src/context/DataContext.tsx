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

const DataContext = createContext<any>(null);

const DataProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState();

  const fetchData = async () => {
    const data = window.localStorage.getItem("data");
    if (data) {
      setData(JSON.parse(data));
      const currentTime = moment.utc();
      const requestTime = moment.utc(JSON.parse(data).timestamp);
      if (
        config.URL === config.PROD ||
        currentTime.hour() !== requestTime.hour() ||
        !currentTime.isSame(requestTime, "date")
      ) {
        try {
          await axios.get(config.URL).then((res) => {
            window.localStorage.setItem("data", JSON.stringify(res.data));
            setData(res.data);
          });
        } catch {
          // any
        }
      }
    } else {
      try {
        await axios.get(config.URL).then((res) => {
          window.localStorage.setItem("data", JSON.stringify(res.data));
          setData(res.data);
        });
      } catch {
        // any
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
