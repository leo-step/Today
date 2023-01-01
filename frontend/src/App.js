import "./App.css";
import WeatherTable from "./components/WeatherTable";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from "./components/PrinceNews";
import DHallTable from "./components/DHallTable";
import EditableLabel from "./components/EditableLabel";
import axios from "axios";
import React, { useState, useEffect } from "react";
import moment from "moment";
import Container from "react-bootstrap/Container";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const data = window.localStorage.getItem("data");
    if (data) {
      setData(JSON.parse(data))
      const currentTime = moment.utc();
      const requestTime = moment.utc(JSON.parse(data).timestamp);
      if (currentTime.hour() !== requestTime.hour() || !currentTime.isSame(requestTime, "date")) {
        axios.get("https://today-nujm46x7ta-ue.a.run.app").then((res) => {
          window.localStorage.setItem("data", JSON.stringify(res.data));
          setData(res.data);
        });
      }
    }
    else {
      axios.get("https://today-nujm46x7ta-ue.a.run.app").then((res) => {
        window.localStorage.setItem("data", JSON.stringify(res.data));
        setData(res.data);
      });
    }
  }, []);

  const currentDate = new Date();
  const currentHour = currentDate.getHours();

  let timeOfDay = "night";
  if (currentHour >= 12 && currentHour < 17) {
    timeOfDay = "afternoon";
  } else if (currentHour >= 17 && currentHour < 21) {
    timeOfDay = "evening";
  } else if (currentHour >= 5 && currentHour < 12) {
    timeOfDay = "morning";
  }
  return (
    <div className="App">
      <div style={{ margin: "100px" }}>
        <h1 className="centered" style={{ color: "white", fontSize: "90px" }}>
          <b>
            Good {timeOfDay} <EditableLabel />
          </b>
        </h1>
        <h1 className="centered" style={{ color: "white", fontSize: "50px" }}>
          <b>{moment().format("dddd") + ", " + moment().format("LL")}</b>
        </h1>
      </div>

      <header className="App-header">
        <DHallTable data={data ? data["dhall"] : null}></DHallTable>

        <Container
          className="App-body"
          style={{ alignItems: "center", maxWidth: "600px" }}
        >
          <WeatherTable data={data ? data["weather"] : []}></WeatherTable>
          <SneakyLinksTable></SneakyLinksTable>
        </Container>
        <PrinceNewsTable
          data={data ? data["prince"] : { articles: [] }}
        ></PrinceNewsTable>
      </header>
    </div>
  );
}

export default App;
