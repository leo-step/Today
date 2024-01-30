import "./App.css";
import WeatherTable from "./components/WeatherTable";
import StreetWeek from "./components/StreetWeek";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import Dance from "./components/Dance";
import PrinceNewsTable from "./components/PrinceNews";
import DHallTable from "./components/DHallTable";
import Name from "./components/Name";
import axios from "axios";
import React, { useState, useEffect } from "react";
import moment from "moment";
import { Container, Row, Col } from "react-bootstrap";
import config from "./config";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const numBackgrounds = 6;
    const currentTime = moment();
    const i = currentTime.day() % numBackgrounds;
    document.body.setAttribute(
      "style",
      `background:url(backgrounds/${i}.jpeg) !important; background-size: cover !important; background-repeat: no-repeat !important;`
    );
  }, []);

  useEffect(() => {
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
        <Row style={{ marginTop: "5%", marginBottom: "7%" }}>
          <Col>
            <h1
              className="centered"
              style={{ color: "white", fontSize: "90px" }}
            >
              <b>
                Good {timeOfDay} <Name />
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
            <DHallTable data={data ? data["dhall"] : null} />
          </Col>
          <Col>
            <StreetWeek data={data ? data["dhall"] : null} />
            {/* <Row className="my-4">
              <WeatherTable data={data ? data["weather"] : []} />
            </Row> */}

              {/* <Row className="my-4">
              <Dance />
            </Row> */}

            {/* <Row className="my-4">
              <SneakyLinksTable />
            </Row> */}
          </Col>
          <Col>
            <PrinceNewsTable data={data ? data["prince"] : { articles: [] }} />
          </Col>
        </Row>
      </div>
    </Container>
    //     <div className="App">

    //       <header className="App-header">
    //         <DHallTable data={data ? data["dhall"] : null}></DHallTable>

    //         <Container
    //           className="App-body"
    //           style={{ alignItems: "center", maxWidth: "600px" }}
    //         >
    //           <WeatherTable data={data ? data["weather"] : []}></WeatherTable>
    //           <SneakyLinksTable></SneakyLinksTable>
    //         </Container>
    //         <PrinceNewsTable
    //           data={data ? data["prince"] : { articles: [] }}
    //         ></PrinceNewsTable>

    //       </header>
    //  </div>
    //     </div>
  );
}

export default App;
