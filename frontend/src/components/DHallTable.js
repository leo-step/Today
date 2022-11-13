import Table from "react-bootstrap/Table";
import {useState} from "react";
import Dropdown from 'react-bootstrap/Dropdown';

function DHallTable(props) {
    const [college, setCollege] = useState("Yeh West College");

    const currentDate = new Date();
    const currentDay = currentDate.getDay();
    const currentHour = currentDate.getHours();

    let meal = "Breakfast";
    if (currentDay == 0 || currentDay == 6) {
        meal = "Lunch"
    }

    if (11 <= currentHour && currentHour < 14) {
        meal = "Lunch";
    }
    else if (14 <= currentHour && currentHour < 24) {
        meal = "Dinner";
    }

    const dhallData = props.data[college][meal]

  return (
    <div
      style={{
        "paddingLeft": "10px",
        "paddingRight": "10px",
        "paddingTop": "5px",
        "paddingBottom": "5px",
        "borderRadius": "25px",
        "backgroundColor": "#212529",
        width: "500px",
        "margin-left": "100px"
      }}
    >
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered">
            <td>
              <h3 style={{
              "fontWeight": "bold"
            }}>What's for <mark>Lunch</mark>?</h3>
                <Dropdown onSelect={(e) => {setCollege(e)}}>
                  <Dropdown.Toggle id="dropdown">
                      {college}
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                      <Dropdown.Item eventKey="Center for Jewish Life">CJL</Dropdown.Item>
                      <Dropdown.Item eventKey="Forbes College">Forbes</Dropdown.Item>
                      <Dropdown.Item eventKey="Rockefeller and Mathey Colleges">Roma</Dropdown.Item>
                      <Dropdown.Item eventKey="Whitman College">Whitman</Dropdown.Item>
                    <Dropdown.Item eventKey="Butler College">Wucox</Dropdown.Item>
                      <Dropdown.Item eventKey="Yeh West College">Yeh/New College West</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
            </td>
          </tr>
          <div
            style={{
              "paddingTop": "10px",
              "paddingBottom": "10px",
              "borderBottomStyle": "solid",
              "borderBottomColor": "#00FF00",
              "borderBottomWidth": "thin",
              "color" : "white",
              "fontSize": 22
              
            }}
          ><tr>
              <td> <h4 style={{"fontWeight": "bold"}}>Main Entree</h4> </td>
            </tr>
            <tr>
              <td> {dhallData["Main Entree"].join(", ")} </td>
            </tr>
          </div>
          <div
            style={{
              "paddingTop": "10px",
              "paddingBottom": "10px",
              "borderBottomStyle": "solid",
              "borderBottomColor": "#FF00DD",
              "borderBottomWidth": "thin",
              "fontSize": 22
            }}
          >
            <tr>
              <td> <h4 style={{"fontWeight": "bold"}}>{Object.keys(dhallData).filter((val) => val != "Main Entree")[0]}</h4> </td>
            </tr>
            <tr>
              <td> {dhallData[Object.keys(dhallData).filter((val) => val != "Main Entree")[0]].slice(0,3).join(", ")} </td>
            </tr>
          </div>
          <div style={{ "paddingTop": "10px", "paddingBottom": "10px",  "fontSize": 22 }}>
            <tr>
              <td> <h4 style={{"fontWeight": "bold"}}>{Object.keys(dhallData).filter((val) => val != "Main Entree")[1]}</h4> </td>
            </tr>
            <tr>
              <td> {dhallData[Object.keys(dhallData).filter((val) => val != "Main Entree")[1]].slice(0,3).join(", ")} </td>
            </tr>
          </div>
        </tbody>
      </Table>
    </div>
  );
}

export default DHallTable;
