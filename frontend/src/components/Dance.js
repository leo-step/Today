import Table from "react-bootstrap/Table";
import Canvas from "../images/canvas.png";
import Docs from "../images/google-docs.png";
import Gmail from "../images/gmail.png";
import GCal from "../images/gcal.png";
import Disiac from "../images/disiac.png";

function Dance() {
  return (
    <div class="dance">
      <Table variant="dark" borderless>
        <tbody>
          <tr>
            <td colSpan={3}>
              {" "}
              <h3 style={{ fontWeight: "bold" }}></h3>
            </td>
            <td></td>
          </tr>
          <tr>
            <td style={{textAlign: "center"}}>
              <a href="https://docs.google.com/">
                <img alt="Disiac" style={{ width: 560 }} src={Disiac} />
              </a>
            </td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default Dance;
