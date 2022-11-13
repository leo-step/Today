import Table from 'react-bootstrap/Table';

function WeatherTable() {

  const weather = [[ 68,  "6 pm",  "☀️" ],  [ 65, "9 pm", "☀️"], [62, "12 am", "⛅️"], [54, "3 am", "🌧"], [50, "6 am", "🌧"]]

  return (
      <div style={{"padding-left": "50px", "padding-right": "50px", "padding-top": "10px", "padding-bottom": "10px", "border-radius": "25px", "background-color": "#212529"}}>
    <Table variant="dark" borderless>
      <tbody>
        <tr>
          <td colSpan={3}> Weather</td>
          <td> H 50 </td>
           <td> L 30 </td>
        </tr>
        <tr className = "centered">

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
        <tr className = "centered">
          <td> {weather[0][0]}</td>
          <td>{weather[1][0]}</td>
          <td>{weather[2][0]}</td>
          <td>{weather[3][0]}</td>
          <td>{weather[4][0]}</td>
        </tr>
      </tbody>
    </Table>
        </div>
  );
}

export default WeatherTable;