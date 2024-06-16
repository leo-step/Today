import "./App.css";
import WeatherTable from "./components/WeatherTable";
import StreetWeek from "./components/StreetWeek";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from "./components/PrinceNews";
import DHallTable from "./components/DHallTable";
import Name from "./components/Name";
import React, { useState, useEffect } from "react";
import moment from "moment";
import { Container, Row, Col } from "react-bootstrap";
import { useTheme } from "./context/ThemeContext";
import { useTime } from "./context/TimeContext";
import { useData } from "./context/DataContext";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const [selectedWidget, setSelectedWidget] = useState(
    window.localStorage.getItem("campusWidget") || "prince"
  );
  const data = useData();
  const theme = useTheme();
  const timeOfDay = useTime();

  /* TODO: need to refactor this into a its own component that isn't manual */
  useEffect(() => {
    window.localStorage.setItem("campusWidget", selectedWidget);
  }, [selectedWidget]);

  const campusWidgets: { [key: string]: React.ReactElement } = {
    prince: (
      <PrinceNewsTable
        data={data ? data["prince"] : { articles: [] }}
        switchTo={setSelectedWidget}
      />
    ),
    street: (
      <StreetWeek
        data={data ? data["dhall"] : null}
        switchTo={setSelectedWidget}
      />
    ),
  };

  /* TODO: confirm this is working */
  useEffect(() => {
    document.body.setAttribute(
      "style",
      `background-image:url(backgrounds/${theme.background}) !important;`
    );
  });

  return (
    /* TODO: all these styles need to go into css file */
    <Container fluid className="m-0">
      <div className="App" style={{ marginLeft: "2.5%", marginRight: "2.5%" }}>
        <Row style={{ marginTop: "5%", marginBottom: "6%" }}>
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
            {/* TODO: shouldn't need to pass data in as props at all */}
            <DHallTable data={data ? data["dhall"] : null} />
          </Col>
          <Col>
            <Row className="my-4">
              <WeatherTable data={data ? data["weather"] : []} />
            </Row>
            <Row className="my-4">
              <SneakyLinksTable />
            </Row>
          </Col>
          <Col>{campusWidgets[selectedWidget]}</Col>
        </Row>
      </div>
    </Container>
  );
}

export default App;
