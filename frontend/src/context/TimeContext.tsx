import React, { createContext, useContext, ReactNode } from "react";
import moment from "moment";

/* TODO: doesn't seem like this is working or updating properly. Also, timezone handling?
should lock into Princeton's timezone probably, how does moment behave? 

Probably need a arguments for the functions for whether you want Princeton timezone or local */

type Time = {
  getCurrentHour: () => number;
  getTimeOfDay: () => TimeOfDay;
  getUTC: () => moment.Moment;
  parseUTC: (timestamp: string) => moment.Moment;
  getDateString: () => string;
  getDay: () => number;
};

type TimeOfDay = "morning" | "afternoon" | "evening" | "night";

/* TODO: not sure if this is good, because time won't update unless 
 component refreshes and calls method */
const timeContext: Time = {
  getCurrentHour: () => {
    return moment().hour();
  },
  getTimeOfDay: () => {
    const currentHour = timeContext.getCurrentHour();
    let timeOfDay: TimeOfDay = "night";
    if (currentHour >= 12 && currentHour < 17) {
      timeOfDay = "afternoon";
    } else if (currentHour >= 17 && currentHour < 21) {
      timeOfDay = "evening";
    } else if (currentHour >= 5 && currentHour < 12) {
      timeOfDay = "morning";
    }
    return timeOfDay;
  },
  getUTC: () => {
    return moment.utc();
  },
  parseUTC: (timestamp: string) => {
    return moment.utc(timestamp);
  },
  getDateString: () => {
    return moment().format("dddd") + ", " + moment().format("LL");
  },
  getDay: () => {
    return moment().day();
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
