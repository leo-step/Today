import Table from "react-bootstrap/Table";

function WeatherTable(props) {
  // const weather = [[ 68,  "6 pm",  "☀️" ],  [ 65, "9 pm", "☀️"], [62, "12 am", "⛅️"], [54, "3 am", "🌧"], [50, "6 am", "🌧"]]

  const weather = props.data;
    console.log(weather)
  return (
    <div
      style={{
        paddingLeft: "10px",
        paddingRight: "10px",
        paddingTop: "10px",
        paddingBottom: "10px",
        borderRadius: "25px",
        backgroundColor: "#212529",
        width: "500px",
        margin: "50px",
      }}
    >
      <Table variant="dark" borderless>
        <tbody>
          <tr>
            <td colSpan={2}>
              {" "}
              <h3 style={{ fontWeight: "bold" }}>Weather</h3>{" "}
            </td>
            <td colSpan={3} className="centered">
              {" "}
            {weather.length !== 0 &&
              <p style={{ fontWeight: "bold", fontSize: 18 }}> Now: {weather[5]['current']}˚   H {weather[5]['max']}˚  L {weather[5]['min']}˚</p>}
            </td>
          </tr>
          {weather.length !== 0 && (
            <tr
              className="centered"
              style={{ fontWeight: "bold", fontSize: 18 }}
            >
              <td> {weather[0][1]}</td>
              <td>{weather[1][1]}</td>
              <td>{weather[2][1]}</td>
              <td>{weather[3][1]}</td>
              <td>{weather[4][1]}</td>
            </tr>
          )}

          {weather.length !== 0 && (
            <tr className="centered emoji">
              <td> {weather[0][2]}</td>
              <td>{weather[1][2]}</td>
              <td>{weather[2][2]}</td>
              <td>{weather[3][2]}</td>
              <td>{weather[4][2]}</td>
            </tr>
          )}

          {weather.length !== 0 && (
            <tr
              className="centered"
              style={{ fontWeight: "bold", fontSize: 15 }}
            >
              <td> {weather[0][0]}˚</td>
              <td>{weather[1][0]}˚</td>
              <td>{weather[2][0]}˚</td>
              <td>{weather[3][0]}˚</td>
              <td>{weather[4][0]}˚</td>
            </tr>
          )}
        </tbody>
      </Table>
    </div>
  );
}

export default WeatherTable;
