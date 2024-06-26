import Table from "react-bootstrap/Table";
import Canvas from "../images/canvas.png";
import Docs from "../images/google-docs.png";
import Gmail from "../images/gmail.png";
import GCal from "../images/gcal.png";
import React from "react";
import WidgetHeader from "./widget/WidgetHeader";

function SneakyLinksTable() {
  return (
    <div className="sneaky-links">
      <Table variant="dark" borderless>
        <tbody>
          <WidgetHeader title={"Sneaky Links"} />
          <tr>
            <td className="centered">
              <a href="https://canvas.princeton.edu/">
                <img
                  id="canvas"
                  alt="Canvas"
                  className="link-icon"
                  src={Canvas}
                />
              </a>
            </td>
            <td className="centered">
              <a href="https://mail.google.com/">
                <img
                  id="gmail"
                  alt="Gmail"
                  className="link-icon"
                  style={{ paddingTop: "8px" }}
                  src={Gmail}
                />
              </a>
            </td>
            <td className="centered">
              <a href="https://calendar.google.com/">
                <img id="gcal" alt="GCal" className="link-icon" src={GCal} />
              </a>
            </td>
            <td className="centered">
              <a href="https://docs.google.com/">
                <img id="docs" alt="Docs" className="link-icon" src={Docs} />
              </a>
            </td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default SneakyLinksTable;
