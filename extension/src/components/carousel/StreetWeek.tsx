import Table from "react-bootstrap/Table";
import { useState, useEffect } from "react";
import Dropdown from "react-bootstrap/Dropdown";
import React from "react";
import { StorageKeys, useStorage } from "../../context/StorageContext";
import { CarouselWidgetProps, CarouselHeader } from "../Carousel";
import { WidgetRow } from "../widget/WidgetRow";

function StreetWeek(props: CarouselWidgetProps) {
  const storage = useStorage();

  const clubData: any = {
    Cap: [
      {
        event: "Monday, 1/29 @ 8pm: Friendship Bracelets with Queer and Gown",
        rsvp: null,
      },
      {
        event: "Tuesday 1/30 @ 8pm: Paint and sip with Cap and Gals",
        rsvp: null,
      },
      {
        event: "Friday 2/2 @ 8pm: Affinity Group Mixer night",
        rvsp: null,
      },
      {
        event: "Saturday, 2/3 @ 11pm: SOPH PUID night out",
        rvsp: null,
      },
    ],

    Charter: [
      {
        event: "Sunday, 1/28, 11am-2pm: S'mores & More",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLScQpg6QZ0xjaKcHvRThu688wyfaXmMUhW7toeGbPAzt9OzV4Q/viewform",
      },
      {
        event: "Monday, 1/29, 8:30-10:30pm: Scavenger Hunt House Tours",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSewd3JStTExizDFOZNgeHbcQGVxoPnj7NC8wjVUU__PYen8TQ/viewform",
      },
      {
        event: "Tuesday, 1/30, 8:30-10:30pm: Speed Friending",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSf8CzVsHL66X8Ji6AUAEbZW25F2YGnsZNhDco57Gs7QMmuLhA/viewform",
      },
      {
        event: "Wednesday, 1/31, 8:30-10:30pm: Trivia",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSfoZaq0XOOpzwVkcMJOIjPi8ndQuRv1bFsb-EH9e9OOs1959A/viewform",
      },
      {
        event: "Thursday, 2/1 8:30-10:30pm: Presentation Night",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLScB-BCdvDdyuQgyajmvHLHrMt4tDI5f74OCg2-5sW9YxZNv5w/viewform",
      },
      {
        event: "Friday, 2/2, 8:00-9:30pm: Game Night",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSebxLK8OvdvlqN-Y8iqe_1FiVKdI1fJzyR5g6W421wi70dVtw/viewform",
      },
      {
        event: "Saturday, 2/3, 2:30-4:00pm via Zoom: Financial Aid Q&A",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSdUWd6Nj99TLxf34qQfWC1hoWkS5M_cYIhSuYGgWiMPtmfELw/viewform",
      },
      {
        event: "Wednesday, 2/7, 8:30-10:30pm: Cookie Decorating",
        rsvp: "https://forms.gle/MZj82jLyd1ZVGWa8A",
      },
    ],

    Colonial: [
      {
        event: "Sunday, January 28th - Graffiti on The Street (11am - 2pm)",
        rsvp: null,
      },

      {
        event: "Monday, January 29th -  Sopht Launch  (11:45am-1:45pm):",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSeuXvL1acywlsFjqFZfK4ob4PCrpOY4huAGpEZD2p6eLqGH5w/viewform",
      },

      {
        event: "Tuesday, January 30th -  GUESS WHO? Mixer  (8-10pm):",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSf2bSef2gPis7JA4KWjD4e4sf-EFiPnsGAYImW66hA6FA38pA/viewform",
      },

      {
        event: "Wednesday, January 31st -  McCOLO’S EXTRAVAGANZA  (8:30-10pm):",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLScQd8-N14gTcP0biUt2JIRgfTp3hCBJe_bppTwWib7clW5Eag/viewform",
      },

      {
        event: "Thursday, February 1st -  Arcade Night  (9pm - 11pm): RSVP ",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSfxLVHCwaBTU1ZT9_aKMEQ2MjTtWnnjaUGB5ds3Iqy6dQuQLQ/viewform",
      },

      {
        event: "Friday, February 2nd -  TCIF: WHITE LIES  (11pm - 2am)",
        rsvp: null,
      },

      {
        event: "Saturday, February 3rd -  Gourmet Dinner  (5:45-7:45pm): RSVP",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLScZBysGQ2triA_izx0ebEVQ_nigOkK71ofLv8atiaEJ_Un6pw/viewform",
      },

      {
        event: "Wednesday, February 7th -  Hot Ones: Colo Edition  (8:30-10pm)",
        rsvp: null,
      },
    ],

    Tower: [
      {
        event: "Sunday 1/28: Mechanical Bull (11 AM - 2 PM)",
        rsvp: null,
      },
      {
        event: "All Week, Starting Monday 1/29: Sophomore Meals",
        rsvp: "https://docs.google.com/spreadsheets/d/1ohqecSWgtGytpeqqYh4C3IOaNtSr7H8c7Fa8M0YOHZI/edit#gid=0",
      },
      {
        event:
          "Tuesday, 1/30: Open House and Q&A Session (8:00 PM to 10:00 PM)",
        rsvp: null,
      },
      {
        event: "Saturday, 2/3: Tower Underground (11:00 PM to 2:00 AM)",
        rsvp: null,
      },
    ],

    "Tiger Inn": [
      {
        event: "Sunday 1/28 11AM-2PM: Wintersession Truck Fest Carnival",
        rsvp: null,
      },
    ],

    Terrace: [
      {
        event: "Tuesday, 1/30 4:30-5:30pm: Financial Aid Info Session ‼️🤑",
        rsvp: null,
      },
      {
        event: "Wednesday, 1/31 5:30pm-7:30pm: Dinner and Trivia 💜💚",
        rsvp: null,
      },
      {
        event: "Thursday, 2/1 10:00-12:00pm: REEEEECCCEEESSSSSSSSSS 🛝",
        rsvp: "https://forms.gle/4jui3Gi25e8KsdDr6",
      },
      {
        event: "Saturday, 2/3, 11pm: Punk's Not Dead",
        rsvp: null,
      },
      {
        event: "Sunday, 2/4 2:30-4:30: Art!!! Market!!! 🎨",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSdlpOCddWSWzyyqaG5iR-P_4779be1plEM5BhJWkap81H2jCg/viewform?usp=sf_link",
      },
    ],

    Cloister: [
      {
        event: "Monday, 1/29 4:30-6:30pm - Hot Choccy, Scones, and Club Tours!",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
      {
        event: "Tuesday, 1/30 7:30-9:30pm - Game Night Tuesday",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
      {
        event: "Wednesday, 1/31 7:30-9:30pm - Mock Bicker and S'mores",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
      {
        event: "Thursday 2/1 6-7:45pm - Burgers and Bevs Pub Night + Trivia",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
      {
        event: "Thursday 9:30pm-12am - Sink or Swim Night Out",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
      {
        event: "Friday, 2/2 7:30pm-9:30pm - Halo Pub Ice Cream Social",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
      {
        event: "Saturday, 2/3 7:30pm-8:30pm - Virtual DEI Panel",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
      {
        event: "Wednesday, 2/7 7:30pm-9:30pm - Paint & Sip Ladies' Night",
        rsvp: "https://forms.gle/95t6nwTxZdDVD6Dr7",
      },
    ],

    Ivy: [
      {
        event: "Check back soon!",
        rsvp: null,
      },
    ],

    Cottage: [
      {
        event: "Quottage - Queer Students Monday January 22 - 8 pm (EST)",
        rsvp: "https://princeton.zoom.us/j/99565837398",
      },

      {
        event: "Women/Femme Students Tuesday January 23 - 8 pm (EST)",
        rsvp: "https://princeton.zoom.us/j/97036364271",
      },

      {
        event: "BIPOC Students Wednesday January 24 - 8 pm (EST)",
        rsvp: "https://princeton.zoom.us/j/95978402416",
      },

      {
        event:
          "International Students Coffee chats deadline to sign up is Sunday 3 pm EST:",
        rsvp: "https://docs.google.com/forms/d/e/1FAIpQLSct2IP1kicg-pfJ0B9KCdv4eh66Rz3cPgANLKfDOHK3cZMgnA/viewform?usp=sf_link",
      },
    ],

    Quad: [
      {
        event: "Sunday, 1/28, 11am: House Tours & Jousting",
        rsvp: null,
      },
      {
        event: "Monday, 1/29, 8pm: Milkshake Monday",
        rsvp: "https://forms.gle/fvTPLfyhysKHcduS8",
      },
      {
        event: "Tuesday, 1/30, 8pm: Murder Mystery",
        rsvp: "https://forms.gle/RSTTvnjnsFeeDViz6",
      },
      {
        event: "Wednesday, 1/31, 9:30pm: Lazer Capture the Flag",
        rsvp: "https://forms.gle/zWc8XrQ45Y4isZcDA",
      },
      {
        event: "Thursday, 2/1, 5:30pm: Pub Night + Fin Aid Info Session",
        rsvp: "https://forms.gle/2G4ZEtL5tGCgHoVw5",
      },
      {
        event: "Friday, 2/2, 4pm: Quad Quick Pick-Me-Ups",
        rsvp: "https://forms.gle/vqgniNkJtZJf9CMp6",
      },
      {
        event: "Saturday, 2/3, 11pm: 7 Deadly Sins",
        rsvp: null,
      },
      {
        event: "Sunday, 2/4, 4pm: Pawsitive Perspectives",
        rsvp: null,
      },
    ],

    Cannon: [
      {
        event: "Check back soon!",
        rsvp: null,
      },
    ],
  };
  const validResults = Object.keys(clubData);

  const [club, setClub] = useState(
    storage.getLocalStorageDefault(StorageKeys.CLUB, "Cap", validResults)
  );

  useEffect(() => {
    storage.setLocalStorage(StorageKeys.CLUB, club);
  }, [club]);

  const rows = clubData[club].map((event: any, i: any) => {
    return (
      <WidgetRow key={i} props={{ index: i, data: clubData[club] }}>
        <h5>
          {event["event"]} {event["rsvp"] && "-"}{" "}
          {event["rsvp"] && (
            <a href={event["rsvp"]} className="prince-a">
              RSVP
            </a>
          )}
        </h5>
      </WidgetRow>
    );
  });

  return (
    <div className="street-week">
      <Table variant="dark" borderless style={{ width: "100%" }}>
        <tbody>
          <CarouselHeader props={props}>Street Week!</CarouselHeader>
          <tr className="centered">
            <td colSpan={3}>
              <Dropdown
                onSelect={(e: any) => {
                  setClub(e);
                }}
              >
                <Dropdown.Toggle className="dropdown">{club}</Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="Cap">Cap</Dropdown.Item>
                  <Dropdown.Item eventKey="Charter">Charter</Dropdown.Item>
                  <Dropdown.Item eventKey="Cloister">Cloister</Dropdown.Item>
                  <Dropdown.Item eventKey="Colonial">Colonial</Dropdown.Item>
                  <Dropdown.Item eventKey="Tower">Tower</Dropdown.Item>
                  <Dropdown.Item eventKey="Tiger Inn">Tiger Inn</Dropdown.Item>
                  <Dropdown.Item eventKey="Quad">Quad</Dropdown.Item>
                  <Dropdown.Item eventKey="Terrace">Terrace</Dropdown.Item>
                  <Dropdown.Item eventKey="Ivy">Ivy</Dropdown.Item>
                  <Dropdown.Item eventKey="Cannon">Cannon</Dropdown.Item>
                  <Dropdown.Item eventKey="Cottage">Cottage</Dropdown.Item>
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

export default StreetWeek;
