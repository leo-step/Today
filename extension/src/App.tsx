import Chat from "./components/Chat";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import DHallTable from "./components/DiningHalls";
import Name from "./components/Name";
import React, { useEffect } from "react";
import { Container, Row, Col } from "react-bootstrap";
import { useTime } from "./context/TimeContext";
import "bootstrap/dist/css/bootstrap.min.css";
import Carousel from "./components/Carousel";
import { EventTypes, useMixpanel } from "./context/MixpanelContext";
import { useStorage } from "./context/StorageContext";
import "react-sliding-pane/dist/react-sliding-pane.css";
import "./App.css";

function App() {
  const time = useTime();
  const storage = useStorage()
  const mixpanel = useMixpanel()

  useEffect(() => {
    const state = storage.getLocalStorageObject()
    mixpanel.trackEvent(EventTypes.PAGE_LOAD, state)
  }, [])

  return (
    <Container fluid className="m-0">
      <div className="App">
        <Row className="name-row">
          <Col>
            <h1 className="centered greeting">
              Good {time.timeOfDay} <Name />
            </h1>
            <h1 className="centered date">{time.dateString}</h1>
          </Col>
        </Row>
        <Row className="gx-5">
          <Col>
            <DHallTable />
          </Col>
          <Col>
            <Row className="my-4">
              <Chat />
              {/* <WeatherTable /> */}
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
