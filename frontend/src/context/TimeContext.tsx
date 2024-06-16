import React, { createContext, useContext, ReactNode } from "react";
import moment from "moment";

// const currentDate = new Date();
// const currentHour = currentDate.getHours();
/* either use moment or .Date() */
// TODO: will this update properly throughout the day?
// TODO: make this into object with multiple properties

const currentHour = moment().hour();

let timeOfDay = "night";
if (currentHour >= 12 && currentHour < 17) {
  timeOfDay = "afternoon";
} else if (currentHour >= 17 && currentHour < 21) {
  timeOfDay = "evening";
} else if (currentHour >= 5 && currentHour < 12) {
  timeOfDay = "morning";
}

const TimeContext = createContext<string>(timeOfDay);

const TimeProvider = ({ children }: { children: ReactNode }) => {
  return (
    <TimeContext.Provider value={timeOfDay}>{children}</TimeContext.Provider>
  );
};

const useTime = () => {
  return useContext(TimeContext);
};

export { TimeProvider, useTime };
