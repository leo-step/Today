import Table from "react-bootstrap/Table";
import { Button } from "react-bootstrap";
import PrinceLogo from "../images/prince.png";
import React from "react";

function PrinceNewsTable(props) {
  const articles = props.data["articles"];

  const rows = articles.map((article, i) => {
    return (
      <tr
        className={i === articles.length - 1 ? "divider no-divider" : "divider"}
        style={{ borderBottomColor: props.colors.accent }}
        key={i}
      >
        {articles.length !== 0 && (
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
        )}
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
          {/* <tr className="divider" style = {{ borderBottomColor: props.colors.main }}>
            {articles.length !== 0 && (
              <td>
                <div className="row-content">
                  <a href={articles[1].link} style={{textDecoration: "none"}}>
                    <b>{articles[1].title}</b>{" "}
                  </a>
                </div> 
              </td>
            )}
          </tr>
          <tr className="divider no-divider">
            {articles.length !== 0 && (
              <td>
                <div className="row-content">
                  <a href={articles[2].link} style={{textDecoration: "none"}}>
                    <b>{articles[2].title}</b>{" "}
                  </a>
                </div>
              </td>
            )}
          </tr> */}
        </tbody>
      </Table>
    </div>
  );
}

export default PrinceNewsTable;
