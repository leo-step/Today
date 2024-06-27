import Table from "react-bootstrap/Table";
import React from "react";
import { useData } from "../context/DataContext";
import WidgetHeader from "./widget/WidgetHeader";

type WeatherPoint = {
  temp: number;
  time: string;
  symbol: string;
};

function WeatherTable() {
  const data = useData();
  const weather: WeatherPoint[] = data?.weather || [];

  const temps: number[] = [];
  const times: string[] = [];
  const symbols: string[] = [];

  for (let i = 0; i < weather.length; i++) {
    const { temp, time, symbol } = weather[i];
    temps.push(temp);
    times.push(time);
    symbols.push(symbol);
  }

  return (
    <div className={"weather"}>
      <Table variant="dark" borderless>
        <tbody>
          <WidgetHeader title={"Weather"} />
          <tr className="centered weather">
            {times.map((time, i) => (
              <td key={i}>{time}</td>
            ))}
          </tr>
          <tr className="centered emoji">
            {symbols.map((symbol, i) => (
              <td key={i}>{symbol}</td>
            ))}
          </tr>
          <tr className="centered" style={{ fontSize: 15 }}>
            {temps.map((temp, i) => (
              <td key={i}>{temp}˚</td>
            ))}
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default WeatherTable;
