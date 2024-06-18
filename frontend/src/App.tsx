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
      <div className="App">
        <Row className="name-row">
          <Col>
            <h1 className="centered greeting">
              Good {time.getTimeOfDay()} <Name />
            </h1>
            <h1 className="centered date">{time.getDateString()}</h1>
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
