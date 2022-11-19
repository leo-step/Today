import Table from 'react-bootstrap/Table';
import Canvas  from '../images/canvas.png';
import EdStem  from '../images/edstem.png';
import Gmail  from '../images/gmail.png';
import GCal  from '../images/gcal.png';

function SneakyLinksTable() {

  return (
      <div style={{"paddingLeft": "10px", 
      "paddingRight": "10px",
       "paddingTop": "10px", 
       "paddingBottom": "10px",
        "borderRadius": "25px", 
        "backgroundColor": "#212529",
        width: "500px"
        }}>

    <Table variant="dark" borderless>
        <tbody>
            <tr>
                <td colSpan={3}> <h3 style={{"fontWeight": "bold"}}>Sneaky Links</h3></td>
                <td></td>
            </tr>
            <tr>
                <td><a href = "https://canvas.princeton.edu/"><img style={{"width": 60}} src={Canvas}/></a></td>
                <td><a href = "https://mail.google.com/"><img style={{"width": 60, "paddingTop": "8px"}} src={Gmail}/></a></td>
                <td><a href = "https://calendar.google.com/"><img style={{"width": 60}} src={GCal}/></a></td>
                <td><a href = "https://edstem.org/us/"><img style={{"width": 60}} src={EdStem}/></a></td>
            </tr>
        </tbody>
      {/*<tbody>*/}
      {/*  <tr>*/}
      {/*    <td colSpan={3}> Weather</td>*/}
      {/*    <td> H 50 </td>*/}
      {/*     <td> L 30 </td>*/}
      {/*  </tr>*/}
      {/*  <tr className = "centered">*/}

      {/*    <td> {weather[0][1]}</td>*/}
      {/*    <td>{weather[1][1]}</td>*/}
      {/*    <td>{weather[2][1]}</td>*/}
      {/*    <td>{weather[3][1]}</td>*/}
      {/*    <td>{weather[4][1]}</td>*/}
      {/*  </tr>*/}

      {/*  <tr className = "centered emoji">*/}
      {/*    <td> {weather[0][2]}</td>*/}
      {/*    <td>{weather[1][2]}</td>*/}
      {/*    <td>{weather[2][2]}</td>*/}
      {/*    <td>{weather[3][2]}</td>*/}
      {/*    <td>{weather[4][2]}</td>*/}
      {/*  </tr>*/}
      {/*  <tr className = "centered">*/}
      {/*    <td> {weather[0][0]}</td>*/}
      {/*    <td>{weather[1][0]}</td>*/}
      {/*    <td>{weather[2][0]}</td>*/}
      {/*    <td>{weather[3][0]}</td>*/}
      {/*    <td>{weather[4][0]}</td>*/}
      {/*  </tr>*/}
      {/*</tbody>*/}
    </Table>
        </div>
  );
}

export default SneakyLinksTable;