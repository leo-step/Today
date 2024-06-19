import React, { createContext, useContext, useState, ReactNode } from "react";
import moment from "moment";

/* TODO: doesn't seem like this is working or updating properly. Also, timezone handling?
should lock into Princeton's timezone probably, how does moment behave? 

Probably need a arguments for the functions for whether you want Princeton timezone or local */

// type Time = {
//   getCurrentHour: () => number;
//   getTimeOfDay: () => TimeOfDay;
//   getUTC: () => moment.Moment;
//   parseUTC: (timestamp: string) => moment.Moment;
//   getDateString: () => string;
//   getDay: () => number;
// };

type TimeOfDay = "morning" | "afternoon" | "evening" | "night";

type Time = {
  currentHour: number;
  timeOfDay: TimeOfDay;
  getUTC: () => moment.Moment;
  parseUTC: (timestamp: string) => moment.Moment;
  dateString: string;
  day: number;
  refresh?: () => void;
};

/* TODO: not sure if this is good, because time won't update unless 
 component refreshes and calls method */
const getCurrentHour = () => {
  return moment().hour();
};
const getTimeOfDay = () => {
  const currentHour = getCurrentHour();
  let timeOfDay: TimeOfDay = "night";
  if (currentHour >= 12 && currentHour < 17) {
    timeOfDay = "afternoon";
  } else if (currentHour >= 17 && currentHour < 21) {
    timeOfDay = "evening";
  } else if (currentHour >= 5 && currentHour < 12) {
    timeOfDay = "morning";
  }
  return timeOfDay;
};
const getUTC = () => {
  return moment.utc();
};
const parseUTC = (timestamp: string) => {
  return moment.utc(timestamp);
};
const getDateString = () => {
  return moment().format("dddd") + ", " + moment().format("LL");
};
const getDay = () => {
  return moment().day();
};

const createTimeContext = (): Time => ({
  currentHour: getCurrentHour(),
  timeOfDay: getTimeOfDay(),
  getUTC: getUTC,
  parseUTC: parseUTC,
  dateString: getDateString(),
  day: getDay(),
});

const TimeContext = createContext<Time>(createTimeContext());

const TimeProvider = ({ children }: { children: ReactNode }) => {
  const [time, setTime] = useState<Time>(createTimeContext());
  const refreshTime = () => setTime(createTimeContext());
  time.refresh = refreshTime;

  return <TimeContext.Provider value={time}>{children}</TimeContext.Provider>;
};

const useTime = () => {
  return useContext(TimeContext);
};

export { TimeProvider, useTime };
