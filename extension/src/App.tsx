import Chat from "./components/Chat";
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

import { CountdownCircleTimer } from "react-countdown-circle-timer";



function App() {
  const time = useTime();
  const storage = useStorage()
  const mixpanel = useMixpanel()

  const [showWidgets, setShowWidgets] = useState(true); // Show widgets initially
  const [timer] = useState(25); // Timer duration in minutes
  const [key, setKey] = useState(0); // Key to force re-render timer
  const [animate, setAnimate] = useState(false); // Control animation

  useEffect(() => {
    const state = storage.getLocalStorageObject()
    mixpanel.trackEvent(EventTypes.PAGE_LOAD, state)
  }, [])

  const toggleWidgets = (show: boolean) => {
    setShowWidgets(show);

    if (!show) {
      // When entering study mode, reset the timer and start animation
      setAnimate(true);
      setKey(prevKey => prevKey + 1); // Reset timer
    } else {
      // When exiting study mode, stop the timer
      setAnimate(false);
    }
  };

  const stopAnimate = () => {
    setAnimate(false);
    setShowWidgets(true); // Re-enable the widgets when timer completes
  };

  return (
    <Container fluid className="m-0">
      <div className="App">
        <Row className="header">
          <StudyMode toggleWidgets={toggleWidgets} />
        </Row>
        <Row className="name-row">
          <Col>
            <h1 className="centered greeting">
              Good {time.timeOfDay} <Name />
            </h1>
            <h1 className="centered date">{time.dateString}</h1>
          </Col>
        </Row>
       {/* Conditionally render widgets based on the 'showWidgets' state */}
       {showWidgets && (
          <Row className="gx-5">
            <Col>
              <DHallTable />
            </Col>
            <Col>
              <Row className="my-4">
                <Chat />
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
        {/* Render CountdownCircleTimer when widgets are hidden */}
        {!showWidgets && (
          <CountdownCircleTimer
            key={key}
            isPlaying={animate}
            duration={timer * 60} // Convert minutes to seconds
            colors={[
              ["#FE6F6B", 0.33],
              ["#FE6F6B", 0.33],
              ["#FE6F6B", 0.33],
            ]}
            strokeWidth={6}
            size={220}
            trailColor="#151932"
            onComplete={() => {
              stopAnimate(); // Stop animation when timer completes
            }}
          >
            {({ remainingTime }: { remainingTime: number }) => (
              <div>
                {Math.floor(remainingTime / 60)}:{remainingTime % 60 < 10 ? `0${remainingTime % 60}` : remainingTime % 60}
              </div>
            )}
          </CountdownCircleTimer>

        )}
      </div>
    </Container>
  );
}

export default App;
