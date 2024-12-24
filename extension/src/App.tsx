// import Chat from "./components/Chat";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import DHallTable from "./components/DiningHalls";
import Name from "./components/Name";
import StudyMode from "./components/StudyMode";
import React, { useEffect, useState } from "react";
import { Container, Row, Col } from "react-bootstrap";
import { useTime } from "./context/TimeContext";
import "bootstrap/dist/css/bootstrap.min.css";
import Carousel from "./components/Carousel";
import { EventTypes, useMixpanel } from "./context/MixpanelContext";
import { useStorage } from "./context/StorageContext";
import "react-sliding-pane/dist/react-sliding-pane.css";
import "./App.css";
import WeatherTable from "./components/Weather";

function App() {
  const time = useTime();
  const storage = useStorage();
  const mixpanel = useMixpanel();

  const [showWidgets, setShowWidgets] = useState(true); // Show widgets initially

  useEffect(() => {
    const state = storage.getLocalStorageObject();
    mixpanel.trackEvent(EventTypes.PAGE_LOAD, state);
  }, []);

  const toggleWidgets = () => {
    setShowWidgets((prevShowWidgets) => !prevShowWidgets);
  };

  return (
    <Container fluid className="m-0">
      <div className="App">
        {/* Top-right StudyMode Button */}
        <div className="study-mode-top-right">
          <StudyMode toggleWidgets={toggleWidgets} />
        </div>

        {showWidgets && (
          <Row className="name-row">
            <Col>
              <h1 className="centered greeting">
                Good {time.timeOfDay} <Name />
              </h1>
              <h1 className="centered date">{time.dateString}</h1>
            </Col>
          </Row>
        )}

        {showWidgets && (
          <Row className="gx-5">
            <Col>
              <DHallTable />
            </Col>
            <Col>
              <Row className="my-4">
                <WeatherTable />
                {/* <Chat /> */}
              </Row>
              <Row className="my-4">
                <SneakyLinksTable />
              </Row>
            </Col>
            <Col>
              <Carousel />
            </Col>
          </Row>
        )}
      </div>
    </Container>
  );
}

export default App;
