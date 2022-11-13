import './App.css';
import WeatherTable from './components/WeatherTable';
import 'bootstrap/dist/css/bootstrap.min.css';
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from './components/PrinceNews';
import DHallTable from "./components/DHallTable";
import axios from "axios";
import React, { useState, useEffect } from 'react';
import moment from 'moment';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';



function App() {

    const [data, setData] = useState(null);



    useEffect(() => {

    // Update the document title using the browser API
       axios.get('http://127.0.0.1:5000')
           .then((res) => {
               setData(res.data)
           })

  }, [])

    if (data) {
        const currentDate = new Date();
        const currentHour = currentDate.getHours();

        let timeOfDay = "morning";
        if (currentHour >= 12 && currentHour < 17) {
          timeOfDay = "afternoon";
        }
        else if (currentHour >= 17 && currentHour < 21) {
          timeOfDay = "evening"
        }
        else {
          timeOfDay = "night"
        }

        return (
          <div className="App">
          <header className="App-header">
            <h1 style={{"color": "white", "fontSize": "84px"}}><b>Good {timeOfDay} Aaliyah</b></h1>
            <h1 style={{"color": "white"}}><b>{moment().format('LL')}</b></h1>
            <Container>
              <Row>
                <Col>
                  <DHallTable data = {data['dhall']}></DHallTable>
                </Col>
              <Col>
              <WeatherTable data = {data['weather']} ></WeatherTable>
              <SneakyLinksTable></SneakyLinksTable>
              </Col>
              <Col><PrinceNewsTable data = {data['prince']}></PrinceNewsTable></Col>
              </Row>
            </Container>
          </header>
        </div>
        
      );
          }

return <div></div>

}

export default App;
