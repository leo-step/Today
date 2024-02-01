import Table from "react-bootstrap/Table";
import PrinceLogo from "../images/prince.png"

function PrinceNewsTable(props) {
  const articles = props.data["articles"];

  return (
    <div class="prince">
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered mediumfont">
            <td>
              <h3 style={{ fontWeight: "bold" }}>The Prince <img alt="Prince" style={{ width: 40, marginLeft: 5, marginBottom: 5}} src={PrinceLogo} /> </h3>
            </td>
          </tr>
          <div class="divider" style = {{ borderBottomColor: props.colors.accent }}>
            <tr>
              {articles.length !== 0 && (
                <td>
                  {" "}
                  <a href={articles[0].link} style={{textDecoration: "none"}}>
                    <b>{articles[0].title}</b>{" "}
                  </a>{" "}
                </td>
              )}
            </tr>
          </div>
          <div class="divider" style = {{ borderBottomColor: props.colors.main }}>
            <tr>
              {articles.length !== 0 && (
                <td>
                  {" "}
                  <a href={articles[1].link} style={{textDecoration: "none"}}>
                    <b>{articles[1].title}</b>{" "}
                  </a>{" "}
                </td>
              )}
            </tr>
          </div>
          <div class="divider no-divider">
            <tr>
              {articles.length !== 0 && (
                <td>
                  {" "}
                  <a href={articles[2].link} style={{textDecoration: "none"}}>
                    <b>{articles[2].title}</b>{" "}
                  </a>{" "}
                </td>
              )}
            </tr>
          </div>
        </tbody>
      </Table>
    </div>
  );
}

export default PrinceNewsTable;
