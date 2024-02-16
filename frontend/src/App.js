import "./App.css";
import WeatherTable from "./components/WeatherTable";
import StreetWeek from "./components/StreetWeek";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import Dance from "./components/Dance";
import PrinceNewsTable from "./components/PrinceNews";
import DHallTable from "./components/DHallTable";
import Name from "./components/Name";
import EditableLabel from "./components/EditableLabel";
import axios from "axios";
import React, { useState, useEffect } from "react";
import moment from "moment";
import { Container, Row, Col } from "react-bootstrap";
import config from "./config";
import "bootstrap/dist/css/bootstrap.min.css";
import Valentines from "./components/Valentines";

function App() {
  const colorCodes = {0: {'main': '#4c8300', 'accent': '#d86c0d'},
                      1: {'main': '#ffa84b', 'accent': '#978cff'},
                      2: {'main': '#1aa5ae', 'accent': '#ffa84b'},
                      3: {'main': '#f67205', 'accent': '#77c7fb'} }


  const [data, setData] = useState(null);
  const [colors, setColors] = useState(colorCodes[0]);
  const [selectedWidget, setSelectedWidget] = useState(
    window.localStorage.getItem("campusWidget") || "prince"
  );

  useEffect(() => {
    window.localStorage.setItem("campusWidget", selectedWidget);
  }, [selectedWidget]);

  const campusWidgets = {
    "prince": <PrinceNewsTable colors = {colors} data={data ? data["prince"] : { articles: [] }} switchTo={setSelectedWidget}/>,
    "street": <StreetWeek colors = {colors} data={data ? data["dhall"] : null} switchTo={setSelectedWidget} />
  }

  useEffect(() => {
    const numBackgrounds = 4;
    const currentTime = moment();
    const i = currentTime.day() % numBackgrounds;

    document.body.setAttribute(
      "style",
      `background-image:url(backgrounds/${i}.jpeg) !important;`
    );

     setColors(colorCodes[i])
  }, [data]);

  useEffect(() => {
    const fetchData = async () => {
      const data = window.localStorage.getItem("data");
      if (data) {
        setData(JSON.parse(data));
        const currentTime = moment.utc();
        const requestTime = moment.utc(JSON.parse(data).timestamp);
        if (
          config.URL === config.DEV || currentTime.hour() !== requestTime.hour() ||
          !currentTime.isSame(requestTime, "date")
        ) {
          axios.get(config.URL).then((res) => {
            window.localStorage.setItem("data", JSON.stringify(res.data));
            setData(res.data);
          });
        }
      } else {
        axios.get(config.URL).then((res) => {
          window.localStorage.setItem("data", JSON.stringify(res.data));
          setData(res.data);
        });
      }
    };
    fetchData();

    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
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
  } // style={{ margin: "100px" }}

  return (
    <Container fluid className="m-0">
      <div className="App" style={{ marginLeft: "2.5%", marginRight: "2.5%" }}>
        <Row style={{ marginTop: "5%", marginBottom: "7%"}}>
          <Col>
            <h1
              className="centered"
              style={{ color: "white", fontSize: "90px" }}
            >
              <b>
                {/* Good {timeOfDay} <Name /> */}
                Good {timeOfDay} <EditableLabel />
              </b>
            </h1>
            <h1
              className="centered"
              style={{ color: "white", fontSize: "50px" }}
            >
              <b>{moment().format("dddd") + ", " + moment().format("LL")}</b>
            </h1>
          </Col>
        </Row>
        <Row className="gx-5">
          <Col>
            <DHallTable colors = {colors} data={data ? data["dhall"] : null} />
          </Col>
          <Col>
            {/* <StreetWeek colors = {colors} data={data ? data["dhall"] : null} /> */}
            <Row className="my-4">
              <WeatherTable data={data ? data["weather"] : []} />
            </Row>

              {/* <Row className="my-4">
              <Dance />
            </Row> */}

            <Row className="my-4">
              <SneakyLinksTable />
              {/* <Valentines /> */}
            </Row>
          </Col>
          <Col>
            {campusWidgets[selectedWidget]}
          </Col>
        </Row>
        {/* <Row>
          <Col>
            <div class="banner">
              <h4>🎉 Thank you for downloading the extension! 🎉</h4>
            </div>
          </Col>
        </Row> */}
      </div>
    </Container>
  );
}

export default App;
