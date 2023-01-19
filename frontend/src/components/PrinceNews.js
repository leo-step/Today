import Table from "react-bootstrap/Table";

function PrinceNewsTable(props) {
  const articles = props.data["articles"];

  return (
    <div class="prince">
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered mediumfont">
            <td>
              <h3 style={{ fontWeight: "bold" }}>The Prince 🗞️</h3>
            </td>
          </tr>
          <div class="divider divider-red">
            <tr>
              {articles.length !== 0 && (
                <td>
                  {" "}
                  <a href={articles[0].link}>
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
                  <a href={articles[1].link}>
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
                  <a href={articles[2].link}>
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
