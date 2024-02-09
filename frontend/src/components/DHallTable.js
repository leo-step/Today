import Table from "react-bootstrap/Table";
import { useState, useEffect } from "react";
import Dropdown from "react-bootstrap/Dropdown";


function DHallTable(props) {
  const [college, setCollege] = useState(
    window.localStorage.getItem("dhall") || "Yeh/NCW"
  );

  useEffect(() => {
    window.localStorage.setItem("dhall", college);
  }, [college]);

  const currentDate = new Date();
  const currentDay = currentDate.getDay();
  const currentHour = currentDate.getHours();

  let meal = "Breakfast";
  if (currentDay === 0 || currentDay === 6) {
    meal = "Lunch";
  }

  if (11 <= currentHour && currentHour < 14) {
    meal = "Lunch";
  } else if (14 <= currentHour && currentHour < 24) {
    meal = "Dinner";
  }

  const dhallData = props.data ? props.data[college][meal] : null;

  const priority = [
    "Main Entree",
    "Early Entree",
    "Vegetarian & Vegan Entree",
    "Vegan/Vegetarian",
    "Pasta",
    "Specialty Bars",
    "Breakfast Bars",
    "On the Side",
    "Sides",
    "Grill",
    "Action Station",
    "Pasta Station",
    "Desserts",
    "Breakfast Cereal",
    "Composed Salads",
    "Soup of the Day",
    "Soups",
    "Salads"
  ]

  const data = [];
  if (dhallData) {
    for (let i = 0; i < priority.length; i += 1) {
      if (data.length === 3) break;
      if (!(priority[i] in dhallData)) continue; // key not in menu
      data.push({cat: priority[i], items: dhallData[priority[i]].slice(0, 3).join(", ")})
    }
  }

  const rows = data.map((item, i) => {
    return <tr className={i === data.length-1 ? 'divider no-divider' : 'divider'} 
          style = {{ borderBottomColor: props.colors.accent }} key={i}>
          <td>
            <div className="row-content">
              <h4 style={{ fontWeight: "bold" }}>{item.cat}</h4>{" "}
              {item.items}
            </div>
          </td>
      </tr>
  });

  return (
    <div className={"dining-hall"}>
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered">
            <td>
              <h3
                style={{
                  fontWeight: "bold",
                }}
              >
                What's for <mark>{meal}</mark>?
              </h3>
              <Dropdown
                onSelect={(e) => {
                  setCollege(e);
                }}
              >
                <Dropdown.Toggle className="dropdown">{college}</Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="Center for Jewish Life">
                    CJL
                  </Dropdown.Item>
                  <Dropdown.Item eventKey="Forbes">Forbes</Dropdown.Item>
                  <Dropdown.Item eventKey="Roma">Roma</Dropdown.Item>
                  <Dropdown.Item eventKey="Whitman">Whitman</Dropdown.Item>
                  {/* <Dropdown.Item eventKey="Wucox">Wucox</Dropdown.Item> */}
                  <Dropdown.Item eventKey="Yeh/NCW">Yeh/NCW</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </td>
          </tr>
          {rows}
        </tbody>
      </Table>
    </div>
  );
}

export default DHallTable;
