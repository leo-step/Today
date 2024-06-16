import React, { createContext, useContext, ReactNode } from "react";
import moment from "moment";

type Time = {
  getCurrentHour: () => number;
  getTimeOfDay: () => string;
};

const timeContext: Time = {
  getCurrentHour: () => {
    return moment().hour();
  },
  getTimeOfDay: () => {
    const currentHour = timeContext.getCurrentHour();
    let timeOfDay = "night";
    if (currentHour >= 12 && currentHour < 17) {
      timeOfDay = "afternoon";
    } else if (currentHour >= 17 && currentHour < 21) {
      timeOfDay = "evening";
    } else if (currentHour >= 5 && currentHour < 12) {
      timeOfDay = "morning";
    }
    return timeOfDay;
  },
};

const TimeContext = createContext<Time>(timeContext);

const TimeProvider = ({ children }: { children: ReactNode }) => {
  return (
    <TimeContext.Provider value={timeContext}>{children}</TimeContext.Provider>
  );
};

const useTime = () => {
  return useContext(TimeContext);
};

export { TimeProvider, useTime };
