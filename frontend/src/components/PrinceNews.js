import Table from "react-bootstrap/Table";

function PrinceNewsTable(props) {

    const articles = props.data["articles"]

  return (
    <div
      style={{
        "paddingLeft": "20px",
        "paddingRight": "20px",
        "paddingTop": "10px",
        "paddingBottom": "10px",
        "borderRadius": "25px",
        "backgroundColor": "#212529",
        width: "700px",
      }}
    >
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered">
            <td>
              <h1 style={{"fontWeight": "bold"}}>The Prince 🗞️</h1>
            </td>
          </tr>
          <div
            style={{
              "paddingTop": "10px",
              "paddingBottom": "10px",
              "borderBottomStyle": "solid",
              "borderBottomColor": "#FF2A0D",
              "borderBottomWidth": "thin",
                "color" : "white"
            }}
          >
            <tr>
              <td> <a href = {articles[0].link} ><b>{articles[0].title}</b> </a> </td>
            </tr>
          </div>
          <div
            style={{
              "paddingTop": "10px",
              "paddingBottom": "10px",
              "borderBottomStyle": "solid",
              "borderBottomColor": "#41EAEA",
              "borderBottomWidth": "thin",
            }}
          >
            <tr>
                <td  > <a href = {articles[1].link} ><b>{articles[1].title}</b> </a> </td>
            </tr>
          </div>
          <div style={{ "paddingTop": "10px", "paddingBottom": "10px" }}>
            <tr>
                <td  > <a href = {articles[2].link} ><b>{articles[2].title}</b> </a> </td>
            </tr>
          </div>
        </tbody>
      </Table>
    </div>
  );
}

export default PrinceNewsTable;
