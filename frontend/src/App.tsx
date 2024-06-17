import "./App.css";
import WeatherTable from "./components/Weather";
import StreetWeek from "./components/StreetWeek";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from "./components/PrinceNews";
import DHallTable from "./components/DiningHalls";
import Name from "./components/Name";
import React, { useState, useEffect } from "react";
import { Container, Row, Col } from "react-bootstrap";
import { useTheme } from "./context/ThemeContext";
import { useTime } from "./context/TimeContext";
import { useStorage } from "./context/StorageContext";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const theme = useTheme();
  const time = useTime();
  const storage = useStorage();

  const [selectedWidget, setSelectedWidget] = useState(
    storage.getLocalStorageDefault("campusWidget", "prince")
  );

  /* TODO: need to refactor this into a its own component that isn't manual */
  useEffect(() => {
    storage.setLocalStorage("campusWidget", selectedWidget);
  }, [selectedWidget]);

  const campusWidgets: { [key: string]: React.ReactElement } = {
    prince: <PrinceNewsTable switchTo={setSelectedWidget} />,
    street: <StreetWeek switchTo={setSelectedWidget} />,
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
                Good {time.getTimeOfDay()} <Name />
              </b>
            </h1>
            <h1
              className="centered"
              style={{ color: "white", fontSize: "50px" }}
            >
              <b>{time.getDateString()}</b>
            </h1>
          </Col>
        </Row>
        <Row className="gx-5">
          <Col>
            <DHallTable />
          </Col>
          <Col>
            <Row className="my-4">
              <WeatherTable />
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
