import React, { useState, useEffect } from "react";
import PrinceNewsTable from "./carousel/PrinceNews";
import StreetWeek from "./carousel/StreetWeek";
import { useStorage } from "../context/StorageContext";
import { Button } from "react-bootstrap";

type Key = {
  label: string;
  go: () => void;
};

export type CarouselWidgetProps = {
  left?: Key;
  right?: Key;
};

type CarouselWidgetsDict = { [key: string]: React.ReactElement };

function Carousel() {
  const storage = useStorage();

  const [selectedWidget, setSelectedWidget] = useState(
    // TODO: how do we assert that the options we retrieve are valid?
    // e.g. if we delete a widget from the carousel, but then someone was set on it,
    // the app will break because the key will not be found. need some defensive
    // behavior implemented.
    storage.getLocalStorageDefault("campusWidget", "prince")
  );

  useEffect(() => {
    storage.setLocalStorage("campusWidget", selectedWidget);
  }, [selectedWidget]);

  const key = (key: string, label: string): Key => {
    return { label, go: () => setSelectedWidget(key) };
  };

  const carouselWidgets: CarouselWidgetsDict = {
    prince: <PrinceNewsTable left={key("street", "Street")} />,
    street: <StreetWeek right={key("prince", "Prince")} />,
  };

  return carouselWidgets[selectedWidget];
}

export default Carousel;

type HeaderProps = {
  children: React.ReactNode;
  props: CarouselWidgetProps;
};

export const CarouselHeader: React.FC<HeaderProps> = ({ children, props }) => {
  return (
    <tr className="centered mediumfont">
      <td style={{ width: "20%" }}>
        <ButtonLeft {...props} />
      </td>
      <td style={{ width: "60%" }}>
        <h3 style={{ fontWeight: "bold" }}>{children}</h3>
      </td>
      <td style={{ width: "20%" }}>
        <ButtonRight {...props} />
      </td>
    </tr>
  );
};

function ButtonLeft(props: CarouselWidgetProps) {
  return (
    <Button
      style={{
        paddingLeft: "8px",
        paddingRight: "8px",
        visibility: props.left ? "visible" : "hidden",
      }}
      onClick={props.left?.go}
    >
      &lsaquo;&nbsp;{props.left?.label}
    </Button>
  );
}

function ButtonRight(props: CarouselWidgetProps) {
  return (
    <Button
      style={{
        paddingLeft: "8px",
        paddingRight: "8px",
        visibility: props.right ? "visible" : "hidden",
      }}
      onClick={props.right?.go}
    >
      {props.right?.label}&nbsp;&rsaquo;
    </Button>
  );
}
