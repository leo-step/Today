import Table from "react-bootstrap/Table";
import PrinceLogo from "../images/prince.png";
import React from "react";
import { useTheme } from "../context/ThemeContext";
import { useData } from "../context/DataContext";
import { CarouselWidgetProps, CarouselHeader } from "./Carousel";

type Article = {
  title: string;
  link: string;
};

function PrinceNewsTable(props: CarouselWidgetProps) {
  const data = useData();
  const theme = useTheme();

  const articles: Article[] = data?.prince?.articles || [];

  const rows = articles.map((article, i) => {
    return (
      <tr
        className={i === articles.length - 1 ? "divider no-divider" : "divider"}
        style={{ borderBottomColor: theme.accent }}
        key={i}
      >
        <td colSpan={3}>
          <div className="row-content">
            <a
              href={article.link}
              className="prince-a"
              style={{ textDecoration: "none" }}
            >
              <b>{article.title}</b>{" "}
            </a>
          </div>
        </td>
      </tr>
    );
  });

  // TODO: header title not centered with new carousel buttons
  return (
    <div className="prince">
      <Table variant="dark" borderless>
        <tbody>
          <CarouselHeader props={props}>
            The Prince{" "}
            <img
              alt="Prince"
              style={{ width: 40, marginLeft: 5, marginBottom: 5 }}
              src={PrinceLogo}
            />{" "}
          </CarouselHeader>
          {rows}
        </tbody>
      </Table>
    </div>
  );
}

export default PrinceNewsTable;
