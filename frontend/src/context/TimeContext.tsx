import React, { createContext, useContext, useState, ReactNode } from "react";
import moment from "moment-timezone";

enum Hours {
  _1AM = 1,
  _2AM,
  _3AM,
  _4AM,
  _5AM,
  _6AM,
  _7AM,
  _8AM,
  _9AM,
  _10AM,
  _11AM,
  _12PM,
  _1PM,
  _2PM,
  _3PM,
  _4PM,
  _5PM,
  _6PM,
  _7PM,
  _8PM,
  _9PM,
  _10PM,
  _11PM,
  _12AM,
}

enum Days {
  Sunday = 0,
  Monday,
  Tuesday,
  Wednesday,
  Thursday,
  Friday,
  Saturday,
}

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

export { TimeProvider, useTime, Hours, Days };
