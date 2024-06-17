import "./App.css";
import WeatherTable from "./components/Weather";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import DHallTable from "./components/DiningHalls";
import Name from "./components/Name";
import React, { useEffect } from "react";
import { Container, Row, Col } from "react-bootstrap";
import { useTheme } from "./context/ThemeContext";
import { useTime } from "./context/TimeContext";
import "bootstrap/dist/css/bootstrap.min.css";
import Carousel from "./components/Carousel";

function App() {
  const theme = useTheme();
  const time = useTime();

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
          <Col>
            <Carousel />
          </Col>
        </Row>
      </div>
    </Container>
  );
}

export default App;
