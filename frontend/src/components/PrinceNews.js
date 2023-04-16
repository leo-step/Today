/* global _gaq */
import Table from "react-bootstrap/Table";
import PrinceLogo from "../images/prince.png"

function PrinceNewsTable(props) {
  const articles = props.data["articles"];

  function trackClick(e) {
    _gaq.push(['_trackEvent', 'princeArticle', 'clicked']);
  };

  return (
    <div class="prince">
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered mediumfont">
            <td>
              <h3 style={{ fontWeight: "bold" }}>The ‘Prince’ <img alt="Prince" style={{ width: 40, marginLeft: 5, marginBottom: 5}} src={PrinceLogo} /> </h3>
            </td>
          </tr>
          <div class="divider divider-red">
            <tr>
              {articles.length !== 0 && (
                <td>
                  {" "}
                  <a href={articles[0].link} onClick={trackClick}>
                    <b>{articles[0].title}</b>{" "}
                  </a>{" "}
                </td>
              )}
            </tr>
          </div>
          <div class="divider divider-blue">
            <tr>
              {articles.length !== 0 && (
                <td>
                  {" "}
                  <a href={articles[1].link} onClick={trackClick}>
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
                  <a href={articles[2].link} onClick={trackClick}>
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
