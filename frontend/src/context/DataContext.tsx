import React, { createContext, useContext, ReactNode } from "react";
import moment from "moment";

type Theme = {
  main: string;
  accent: string;
  background: string;
};

const themes: Theme[] = [
  { main: "#4c8300", accent: "#d86c0d", background: "0.jpeg" },
  { main: "#ffa84b", accent: "#978cff", background: "1.jpeg" },
  { main: "#1aa5ae", accent: "#ffa84b", background: "2.jpeg" },
  { main: "#f67205", accent: "#77c7fb", background: "3.jpeg" },
];

const theme = themes[moment().day() % themes.length];

const ThemeContext = createContext<Theme>(theme);

const ThemeProvider = ({ children }: { children: ReactNode }) => {
  return (
    <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
  );
};

const useTheme = () => {
  return useContext(ThemeContext);
};

export { ThemeProvider, useTheme };

/* TODO: this whole thing should be put into data storage useContext thing */
// useEffect(() => {
//     const fetchData = async () => {
//       const data = window.localStorage.getItem("data");
//       if (data) {
//         setData(JSON.parse(data));
//         const currentTime = moment.utc();
//         const requestTime = moment.utc(JSON.parse(data).timestamp);
//         if (
//           config.URL === config.DEV ||
//           currentTime.hour() !== requestTime.hour() ||
//           !currentTime.isSame(requestTime, "date")
//         ) {
//           try {
//             await axios.get(config.URL).then((res) => {
//               window.localStorage.setItem("data", JSON.stringify(res.data));
//               setData(res.data);
//             });
//           } catch {
//             // any
//           }
//         }
//       } else {
//         try {
//           await axios.get(config.URL).then((res) => {
//             window.localStorage.setItem("data", JSON.stringify(res.data));
//             setData(res.data);
//           });
//         } catch {
//           // any
//         }
//       }
//     };
//     fetchData();

//     const interval = setInterval(fetchData, 60000);
//     return () => clearInterval(interval);
//   }, []);
