import Table from "react-bootstrap/Table";
import { useState, useEffect } from "react";
import Dropdown from "react-bootstrap/Dropdown";
import React from "react";
import { StorageKeys, useStorage } from "../context/StorageContext";
import { useTime, Hours, Days } from "../context/TimeContext";
import { useData } from "../context/DataContext";
import { WidgetRow } from "./widget/WidgetRow";
import { EventTypes, useMixpanel } from "../context/MixpanelContext";

type MealSession = "Breakfast" | "Lunch" | "Dinner";

type MealItem = {
  cat: string;
  items: string;
};

type DiningHall = {
  key: string;
  label: string;
};

const DINING_HALLS: DiningHall[] = [
  { key: "Yeh/NCW", label: "Yeh/NCW" },
  { key: "Forbes", label: "Forbes" },
  { key: "Roma", label: "Roma" },
  { key: "Whitman", label: "Whitman" },
  { key: "Center for Jewish Life", label: "CJL" },
];
const DEFAULT_DHALL = DINING_HALLS[0].key;

function DHallTable() {
  const storage = useStorage();
  const time = useTime();
  const data = useData();
  const mixpanel = useMixpanel();
  const validResults = DINING_HALLS.map((diningHall) => diningHall.key);

  const [college, setCollege] = useState(
    storage.getLocalStorageDefault(
      StorageKeys.DHALL,
      DEFAULT_DHALL,
      validResults
    )
  );

  useEffect(() => {
    storage.setLocalStorage(StorageKeys.DHALL, college);
  }, [college]);

  const currentDay = time.dayPrinceton;
  const currentHour = time.currentHourPrinceton;

  let meal: MealSession = "Breakfast";
  if (currentDay === Days.Saturday || currentDay === Days.Sunday) {
    meal = "Lunch";
  } else if (Hours._10AM <= currentHour && currentHour < Hours._2PM) {
    meal = "Lunch";
  } else if (Hours._2PM <= currentHour && currentHour < Hours._12AM) {
    meal = "Dinner";
  }

  const priority = [
    "Entree",
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

  if (rows.length === 0) {
    rows.push(
      <WidgetRow key={0} props={{ index: 0, data: [] }}>
        <h4 style={{ textAlign: "center", marginTop: 36 }}>
          Dining Hall Closed
        </h4>
      </WidgetRow>
    );
  }

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
                  const dhall = e || DEFAULT_DHALL
                  setCollege(dhall);
                  mixpanel.trackEvent(EventTypes.DHALL_CHANGE, dhall)
                }}
              >
                <Dropdown.Toggle className="dropdown">
                  {college}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  {DINING_HALLS.map((diningHall) => (
                    <Dropdown.Item
                      key={diningHall.key}
                      eventKey={diningHall.key}
                    >
                      {diningHall.label}
                    </Dropdown.Item>
                  ))}
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
