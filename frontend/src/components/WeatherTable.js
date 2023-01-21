import Table from "react-bootstrap/Table";

function WeatherTable(props) {
  // const weather = [[ 68,  "6 pm",  "☀️" ],  [ 65, "9 pm", "☀️"], [62, "12 am", "⛅️"], [54, "3 am", "🌧"], [50, "6 am", "🌧"]]

  const weather = props.data;

  return (
    <div class="weather">
      <Table variant="dark" borderless>
        <tbody>
          <tr>
            <td colSpan={3}>
              {" "}
              <h3 style={{fontWeight: "bold"}}>Weather</h3>{" "}
            </td>
            <td colSpan={2} className="centered">
              {" "}
              {/* {weather.length !== 0 && (
                <p style={{ fontSize: 18 }}>Now: {weather[5]["current"]}˚</p>
              )} */}
            </td>
          </tr>
          {weather.length !== 0 && (
            <tr className="centered" style={{ fontSize: 17 }}>
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
            <tr className="centered" style={{ fontSize: 15 }}>
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
