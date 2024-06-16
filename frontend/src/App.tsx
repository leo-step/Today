import "./App.css";
import WeatherTable from "./components/WeatherTable";
import StreetWeek from "./components/StreetWeek";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from "./components/PrinceNews";
import DHallTable from "./components/DHallTable";
import Name from "./components/Name";
import axios from "axios";
import React, { useState, useEffect } from "react";
import moment from "moment";
import { Container, Row, Col } from "react-bootstrap";
import config from "./config";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
import { TimeProvider, useTime } from "./context/TimeContext";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const [data, setData] = useState(null);
  const [selectedWidget, setSelectedWidget] = useState(
    window.localStorage.getItem("campusWidget") || "prince"
  );
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

  /* TODO: this whole thing should be put into data storage useContext thing */
  useEffect(() => {
    const fetchData = async () => {
      const data = window.localStorage.getItem("data");
      if (data) {
        setData(JSON.parse(data));
        const currentTime = moment.utc();
        const requestTime = moment.utc(JSON.parse(data).timestamp);
        if (
          config.URL === config.DEV ||
          currentTime.hour() !== requestTime.hour() ||
          !currentTime.isSame(requestTime, "date")
        ) {
          try {
            await axios.get(config.URL).then((res) => {
              window.localStorage.setItem("data", JSON.stringify(res.data));
              setData(res.data);
            });
          } catch {
            // any
          }
        }
      } else {
        try {
          await axios.get(config.URL).then((res) => {
            window.localStorage.setItem("data", JSON.stringify(res.data));
            setData(res.data);
          });
        } catch {
          // any
        }
      }
    };
    fetchData();

    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    /* TODO: all these styles need to go into css file */
    <ThemeProvider>
      <TimeProvider>
        <Container fluid className="m-0">
          <div
            className="App"
            style={{ marginLeft: "2.5%", marginRight: "2.5%" }}
          >
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
                  <b>
                    {moment().format("dddd") + ", " + moment().format("LL")}
                  </b>
                </h1>
              </Col>
            </Row>
            <Row className="gx-5">
              <Col>
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
      </TimeProvider>
    </ThemeProvider>
  );
}

export default App;
