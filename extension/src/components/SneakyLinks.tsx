import Table from "react-bootstrap/Table";
import Canvas from "../images/canvas.png";
import Docs from "../images/google-docs.png";
import Gmail from "../images/gmail.png";
import GCal from "../images/gcal.png";
import React from "react";
import WidgetHeader from "./widget/WidgetHeader";
import { EventTypes, useMixpanel } from "../context/MixpanelContext";

type SneakyLink = {
  href: string;
  id: string;
  alt: string;
  src: string;
  style?: React.CSSProperties;
};

const sneakyLinks: SneakyLink[] = [
  {
    href: "https://canvas.princeton.edu/",
    id: "canvas",
    alt: "Canvas",
    src: Canvas,
  },
  {
    href: "https://mail.google.com/",
    id: "gmail",
    alt: "Gmail",
    src: Gmail,
    style: { paddingTop: "8px" },
  },
  {
    href: "https://calendar.google.com/",
    id: "gcal",
    alt: "GCal",
    src: GCal,
  },
  {
    href: "https://docs.google.com/",
    id: "docs",
    alt: "Docs",
    src: Docs,
  },
];

function SneakyLinksTable() {
  const mixpanel = useMixpanel();

  return (
    <div className="sneaky-links">
      <Table variant="dark" borderless>
        <tbody>
          <WidgetHeader title={"Sneaky Links"} />
          <tr>
            {sneakyLinks.map((link) => (
              <td key={link.id} className="centered">
                <a
                  href={link.href}
                  onClick={() =>
                    mixpanel.trackEvent(EventTypes.LINKS_CLICK, link.id)
                  }
                >
                  <img
                    id={link.id}
                    alt={link.alt}
                    className="link-icon"
                    src={link.src}
                    style={link.style}
                  />
                </a>
              </td>
            ))}
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default SneakyLinksTable;
