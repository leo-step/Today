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

  if (dhallData) {
    firstSectionKey = "Main Entree";
    firstSection = dhallData[firstSectionKey];
    const other = Object.keys(dhallData).filter((val) => val !== "Main Entree");
    if (firstSection) {
      if (other.length > 0) secondSectionKey = other[0];
      secondSection = dhallData[secondSectionKey];
      if (other.length > 1) thirdSectionKey = other[1];
      thirdSection = dhallData[thirdSectionKey];
    } else {
      if (other.length > 0) firstSectionKey = other[0];
      firstSection = dhallData[firstSectionKey];
      if (other.length > 1) secondSectionKey = other[1];
      secondSection = dhallData[secondSectionKey];
      if (other.length > 2) thirdSectionKey = other[2];
      thirdSection = dhallData[thirdSectionKey];
    }
  }

  return (
    <div class="dining-hall">
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
                <Dropdown.Toggle id="dropdown">{college}</Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="Center for Jewish Life">
                    CJL
                  </Dropdown.Item>
                  <Dropdown.Item eventKey="Forbes">Forbes</Dropdown.Item>
                  <Dropdown.Item eventKey="Roma">Roma</Dropdown.Item>
                  <Dropdown.Item eventKey="Whitman">Whitman</Dropdown.Item>
                  <Dropdown.Item eventKey="Wucox">Wucox</Dropdown.Item>
                  <Dropdown.Item eventKey="Yeh/NCW">Yeh/NCW</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </td>
          </tr>
          <div class="divider divider-green">
            {firstSectionKey && (
              <tr>
                <td>
                  {" "}
                  <h4 style={{ fontWeight: "bold" }}>{firstSectionKey}</h4>{" "}
                </td>
              </tr>
            )}
            {firstSection && (
              <tr>
                <td> {firstSection.slice(0, 3).join(", ")} </td>
              </tr>
            )}
          </div>
          <div class="divider divider-pink">
            {secondSectionKey && (
              <tr>
                <td>
                  {" "}
                  <h4 style={{ fontWeight: "bold" }}>
                    {secondSectionKey}
                  </h4>{" "}
                </td>
              </tr>
            )}
            {secondSection && (
              <tr>
                <td> {secondSection.slice(0, 3).join(", ")} </td>
              </tr>
            )}
          </div>
          <div class="divider no-divider">
            {thirdSectionKey && (
              <tr>
                <td>
                  {" "}
                  <h4 style={{ fontWeight: "bold" }}>{thirdSectionKey}</h4>{" "}
                </td>
              </tr>
            )}
            {thirdSection && (
              <tr>
                <td> {thirdSection.slice(0, 3).join(", ")} </td>
              </tr>
            )}
          </div>
        </tbody>
      </Table>
    </div>
  );
}

export default DHallTable;
