import "./App.css";
import WeatherTable from "./components/WeatherTable";
import "bootstrap/dist/css/bootstrap.min.css";
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from "./components/PrinceNews";
import DHallTable from "./components/DHallTable";
import EditableLabel from "./components/EditableLabel";
import axios from "axios";
import React, { useState, useEffect } from "react";
import moment from "moment";
import { Container, Row, Col } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const [data, setData] = useState(null);

  // console.log(window.innerWidth);

  // useEffect(() => {
  //   function handleResize() {
  //     const viewport = document.getElementById("viewport-meta");
  //     viewport.setAttribute("content", "width=" + window.outerWidth + ", initial-scale=1");
  //     // // eslint-disable-next-line no-restricted-globals

  //     // document.body.setAttribute("style", "transform: scale(" + screen.width/1728 + "); transform-origin: top;")
  //   }
  //   window.addEventListener('resize', handleResize);
  //   handleResize();
  // }, [])

  // var backgrounds = [
  //   "https://media.npr.org/assets/img/2021/08/11/gettyimages-1279899488_wide-f3860ceb0ef19643c335cb34df3fa1de166e2761.jpg",
  //   "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cat_August_2010-4.jpg/2880px-Cat_August_2010-4.jpg",
  //   "https://st1.latestly.com/wp-content/uploads/2021/08/31-6.jpg"
  // ]

  // var i = 1;
  // setInterval(function() {
  //       document.body.setAttribute("style", `background:url(${i}.jpeg) !important`);
  //       i = i + 1;
  //       if (i > 5) {
  //       	i =  1;
  //       }
  // }, 1000);

  useEffect(() => {
    const numBackgrounds = 5
    const currentTime = moment.utc();
    console.log(currentTime.day())
    const i = currentTime.day() % numBackgrounds;
    document.body.setAttribute("style", `background:url(backgrounds/${i}.jpeg) !important`);
  }, []);

  useEffect(() => {
    const data = window.localStorage.getItem("data");
    if (data) {
      setData(JSON.parse(data));
      const currentTime = moment.utc();
      const requestTime = moment.utc(JSON.parse(data).timestamp);
      if (
        currentTime.hour() !== requestTime.hour() ||
        !currentTime.isSame(requestTime, "date")
      ) {
        axios.get("https://today-nujm46x7ta-ue.a.run.app").then((res) => {
          window.localStorage.setItem("data", JSON.stringify(res.data));
          setData(res.data);
        });
      }
    } else {
      axios.get("https://today-nujm46x7ta-ue.a.run.app").then((res) => {
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
      <div className="App" style={{marginLeft: "2.5%", marginRight: "2.5%"}}>
        <Row style={{marginTop: "5%", marginBottom: "7%"}}>
          <Col>
            <h1
              className="centered"
              style={{ color: "white", fontSize: "90px" }}
            >
              <b>
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
