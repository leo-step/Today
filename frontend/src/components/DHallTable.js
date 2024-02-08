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

  let firstSectionKey = null;
  let firstSection = null;
  let secondSectionKey = null;
  let secondSection = null;
  let thirdSectionKey = null;
  let thirdSection = null;

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

  if (dhallData) {
    const data = Array(6).fill(null);
    let i = 0;
    for (let j = 0; j < priority.length; j += 1) {
      if (data[data.length-1] != null) break; // all data full
      if (!(priority[j] in dhallData)) continue; // key not in menu
      data[i] = priority[j]
      data[i+1] = dhallData[priority[j]]
      i += 2
    }
    [firstSectionKey, firstSection, 
     secondSectionKey, secondSection,
     thirdSectionKey, thirdSection] = data;
  }

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
            {firstSectionKey && firstSection && (
              <tr className={"divider"} style = {{ borderBottomColor: props.colors.accent }}>
                <td>
                  {" "}
                  <div className="row-content">
                    <h4 style={{ fontWeight: "bold" }}>{firstSectionKey}</h4>{" "}
                    {firstSection.slice(0, 3).join(", ")}
                  </div>
                </td>
              </tr>
            )}
            {secondSectionKey && secondSection && (
              <tr className={"divider"} style = {{ borderBottomColor: props.colors.accent }}>
                <td>
                  <div className="row-content">
                    <h4 style={{ fontWeight: "bold" }}>
                      {secondSectionKey}
                    </h4>
                    {secondSection.slice(0, 3).join(", ")}
                  </div>
                </td>
              </tr>
            )}
            {thirdSectionKey && thirdSection &&  (
              <tr className={"divider no-divider"}>
                <td>
                  <div className="row-content">
                    <h4 style={{ fontWeight: "bold" }}>{thirdSectionKey}</h4>
                    {thirdSection.slice(0, 3).join(", ")}
                  </div>   
                </td>
              </tr>
            )}
        </tbody>
      </Table>
    </div>
  );
}

export default DHallTable;
