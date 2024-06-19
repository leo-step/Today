import Table from "react-bootstrap/Table";
import { useState, useEffect } from "react";
import Dropdown from "react-bootstrap/Dropdown";
import React from "react";
import { useStorage } from "../context/StorageContext";
import { useTime } from "../context/TimeContext";
import { useData } from "../context/DataContext";
import { WidgetRow } from "./widget/WidgetRow";

type MealSession = "Breakfast" | "Lunch" | "Dinner";
type MealItem = {
  cat: string;
  items: string;
};

const DEFAULT_COLLEGE = "Yeh/NCW";

function DHallTable() {
  const storage = useStorage();
  const time = useTime();
  const data = useData();

  const [college, setCollege] = useState(
    storage.getLocalStorageDefault("dhall", DEFAULT_COLLEGE)
  );

  useEffect(() => {
    storage.setLocalStorage("dhall", college);
  }, [college]);

  const currentDay = time.dayPrinceton;
  const currentHour = time.currentHourPrinceton;

  let meal: MealSession = "Breakfast";
  if (currentDay === 0 || currentDay === 6) {
    // TODO: use enums to replace the numbers with legible stuff
    meal = "Lunch";
  } else if (11 <= currentHour && currentHour < 14) {
    meal = "Lunch";
  } else if (14 <= currentHour && currentHour < 24) {
    meal = "Dinner";
  }

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
    "Salads",
  ];

  const dhallData = data?.dhall?.[college]?.[meal] || null;
  const orderedData: MealItem[] = [];

  if (dhallData) {
    for (let i = 0; i < priority.length; i += 1) {
      if (orderedData.length === 3) break;
      if (!(priority[i] in dhallData)) continue;
      orderedData.push({
        cat: priority[i],
        items: dhallData[priority[i]].slice(0, 3).join(", "),
      });
    }
  }

  const rows = orderedData.map((item, i) => {
    return (
      <WidgetRow key={i} props={{ index: i, data: orderedData }}>
        <h4 className="bold">{item.cat}</h4> {item.items}
      </WidgetRow>
    );
  });
  // TODO: make better behavior when dining hall has no food
  return (
    <div className="dining-hall">
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered">
            <td>
              <h3 className="bold">
                What's for <mark>{meal}</mark>?
              </h3>
              <Dropdown
                onSelect={(e) => {
                  setCollege(e || DEFAULT_COLLEGE);
                }}
              >
                <Dropdown.Toggle className="dropdown">
                  {college}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="Center for Jewish Life">
                    CJL
                  </Dropdown.Item>
                  <Dropdown.Item eventKey="Forbes">Forbes</Dropdown.Item>
                  <Dropdown.Item eventKey="Roma">Roma</Dropdown.Item>
                  <Dropdown.Item eventKey="Whitman">Whitman</Dropdown.Item>
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
