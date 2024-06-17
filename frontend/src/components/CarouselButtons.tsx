import React from "react";
import { Button } from "react-bootstrap";
import { CarouselWidgetProps } from "./Carousel";

// TODO: combine this with Carousel file
// TODO: make a component for a widget header that already includes both buttons
export function ButtonLeft(props: CarouselWidgetProps) {
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

export function ButtonRight(props: CarouselWidgetProps) {
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
