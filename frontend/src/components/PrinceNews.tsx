import Table from "react-bootstrap/Table";
import { Button } from "react-bootstrap";
import PrinceLogo from "../images/prince.png";
import React from "react";
import { useTheme } from "../context/ThemeContext";
import { useData } from "../context/DataContext";

type Article = {
  title: string;
  link: string;
};

function PrinceNewsTable(props: any) {
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

  return (
    <div className="prince">
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered mediumfont">
            <td>
              <Button
                style={{
                  paddingLeft: "8px",
                  paddingRight: "8px",
                }}
                onClick={() => {
                  props.switchTo("street");
                }}
              >
                &lsaquo;&nbsp;Street
              </Button>
            </td>
            <td style={{ width: "100%" }}>
              <h3 style={{ fontWeight: "bold" }}>
                The Prince{" "}
                <img
                  alt="Prince"
                  style={{ width: 40, marginLeft: 5, marginBottom: 5 }}
                  src={PrinceLogo}
                />{" "}
              </h3>
            </td>
            <td>
              <Button
                style={{
                  paddingLeft: "8px",
                  paddingRight: "8px",
                  visibility: "hidden",
                }}
                onClick={() => {
                  props.switchTo("street");
                }}
              >
                Street&nbsp;&rsaquo;
              </Button>
            </td>
          </tr>
          {rows}
        </tbody>
      </Table>
    </div>
  );
}

export default PrinceNewsTable;
