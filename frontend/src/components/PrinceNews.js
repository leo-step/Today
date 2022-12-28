import Table from "react-bootstrap/Table";

function PrinceNewsTable(props) {
  const articles = props.data["articles"];

  return (
    <div
      style={{
        paddingLeft: "20px",
        paddingRight: "20px",
        paddingTop: "10px",
        paddingBottom: "10px",
        borderRadius: "25px",
        backgroundColor: "#212529",
        width: "500px",
        marginRight: "100px",
      }}
    >
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered mediumfont">
            <td>
              <h3 style={{ fontWeight: "bold" }}>The Prince 🗞️</h3>
            </td>
          </tr>
          <div
            style={{
              paddingTop: "10px",
              paddingBottom: "20px",
              borderBottomStyle: "solid",
              borderBottomColor: "#FF2A0D",
              borderBottomWidth: "thin",
              color: "white",
              fontSize: 22,
            }}
          >
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
          <div
            style={{
              paddingTop: "20px",
              paddingBottom: "20px",
              borderBottomStyle: "solid",
              borderBottomColor: "#41EAEA",
              borderBottomWidth: "thin",
              fontSize: 22,
            }}
          >
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
          <div
            style={{
              paddingTop: "20px",
              paddingBottom: "10px",
              fontSize: 22,
            }}
          >
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
