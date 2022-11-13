import Table from 'react-bootstrap/Table';

function WeatherTable(props) {

  // const weather = [[ 68,  "6 pm",  "☀️" ],  [ 65, "9 pm", "☀️"], [62, "12 am", "⛅️"], [54, "3 am", "🌧"], [50, "6 am", "🌧"]]

  const weather = props.data

  return (
      <div style={{"paddingLeft": "20px", "paddingRight": "20px", "paddingTop": "10px", "paddingBottom": "10px", "borderRadius": "25px", "backgroundColor": "#212529"}}>
    <Table variant="dark" borderless>
      <tbody>
        <tr>
          <td colSpan={3}> <h1 style={{"fontWeight": "bold"}}>Weather</h1> </td>
          <td style={{"fontWeight": "bold"}}> H 51° </td>
           <td style={{"fontWeight": "bold"}}> L 30° </td>
        </tr>
        <tr className = "centered" style={{"fontWeight": "bold"}}>

          <td> {weather[0][1]}</td>
          <td>{weather[1][1]}</td>
          <td>{weather[2][1]}</td>
          <td>{weather[3][1]}</td>
          <td>{weather[4][1]}</td>
        </tr>

        <tr className = "centered emoji">
          <td> {weather[0][2]}</td>
          <td>{weather[1][2]}</td>
          <td>{weather[2][2]}</td>
          <td>{weather[3][2]}</td>
          <td>{weather[4][2]}</td>
        </tr>
        <tr className = "centered" style={{"fontWeight": "bold"}}>
          <td> {weather[0][0]}°</td>
          <td>{weather[1][0]}°</td>
          <td>{weather[2][0]}°</td>
          <td>{weather[3][0]}°</td>
          <td>{weather[4][0]}°</td>
        </tr>
      </tbody>
    </Table>
        </div>
  );
}

export default WeatherTable;