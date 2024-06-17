import React, { useState, useEffect } from "react";
import PrinceNewsTable from "./PrinceNews";
import StreetWeek from "./StreetWeek";
import { useStorage } from "../context/StorageContext";

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
