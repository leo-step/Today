import logo from './logo.svg';
import './App.css';
import WeatherTable from './components/WeatherTable';
import 'bootstrap/dist/css/bootstrap.min.css';
import SneakyLinksTable from "./components/SneakyLinks";
import PrinceNewsTable from './components/PrinceNews';
import DHallTable from "./components/DHallTable";
import axios from "axios";
import React, { useState, useEffect } from 'react';



function App() {

    const [data, setData] = useState(null);


    useEffect(() => {

    // Update the document title using the browser API
       axios.get('http://127.0.0.1:5000')
           .then((res) => {
               setData(res.data)

           })

  }, []);

    if (data) {
        return (
        <div className="App">
          <header className="App-header">

            <WeatherTable data = {data['weather']} ></WeatherTable>
            <SneakyLinksTable></SneakyLinksTable>
            <PrinceNewsTable data = {data['prince']}></PrinceNewsTable>
            <DHallTable data = {data['dhall']}></DHallTable>
          </header>
        </div>
      );
          }

return <div></div>

}

export default App;
