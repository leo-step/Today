import React, { createContext, useContext, useState, ReactNode } from "react";
import moment from "moment-timezone";

type TimeOfDay = "morning" | "afternoon" | "evening" | "night";

type Time = {
  currentHour: number;
  currentHourPrinceton: number;
  timeOfDay: TimeOfDay;
  getUTC: () => moment.Moment;
  parseUTC: (timestamp: string) => moment.Moment;
  dateString: string;
  day: number;
  dayPrinceton: number;
  refresh?: () => void;
};

const PRINCETON_TZ = "America/New_York";

const getCurrentHour = (timezone?: string) => {
  if (timezone) {
    return moment().tz(timezone).hour();
  }
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
const getDay = (timezone?: string) => {
  if (timezone) {
    return moment().tz(timezone).day();
  }
  return moment().day();
};

const createTimeContext = (): Time => ({
  currentHour: getCurrentHour(),
  currentHourPrinceton: getCurrentHour(PRINCETON_TZ),
  timeOfDay: getTimeOfDay(),
  getUTC: getUTC,
  parseUTC: parseUTC,
  dateString: getDateString(),
  day: getDay(),
  dayPrinceton: getDay(PRINCETON_TZ),
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
