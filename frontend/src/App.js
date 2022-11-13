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

        let timeOfDay = "night";
        if (currentHour >= 12 && currentHour < 17) {
          timeOfDay = "afternoon";
        }
        else if (currentHour >= 17 && currentHour < 21) {
          timeOfDay = "evening"
        }
        else if (currentHour >= 5 && currentHour < 12) {
          timeOfDay = "morning"
        }

        return (
          <div className="App">
            <div style={{"margin": "100px"}}>
              <h1 className="centered" style={{"color": "white", "fontSize": "90px"}}><b>Good {timeOfDay} Aaliyah</b></h1>
              <h1 className="centered" style={{"color": "white", "fontSize": "50px"}}><b>{moment().format('dddd') + ", " + moment().format('LL')}</b></h1>
            </div>

     
            <header className="App-header">
            
          
                  <DHallTable data = {data['dhall']}></DHallTable>
          
                  <Container className="App-body" style={{"alignItems": "center", "maxWidth": "600px"}}>
              <WeatherTable data = {data['weather']} ></WeatherTable>
              <SneakyLinksTable></SneakyLinksTable>
              </Container>
             <PrinceNewsTable data = {data['prince']}></PrinceNewsTable>
            
         
          </header>
          </div>
        
      );
          }

return <div></div>

}

export default App;
