import Table from "react-bootstrap/Table";
import Canvas from "../images/canvas.png";
import Docs from "../images/google-docs.png";
import Gmail from "../images/gmail.png";
import GCal from "../images/gcal.png";

function SneakyLinksTable() {
  return (
    <div class="sneaky-links">
      <Table variant="dark" borderless>
        <tbody>
          <tr>
            <td colSpan={3}>
              {" "}
              <h3 style={{ fontWeight: "bold" }}>Sneaky Links</h3>
            </td>
            <td></td>
          </tr>
          <tr>
            <td>
              <a href="https://canvas.princeton.edu/">
                <img alt="Canvas" style={{ width: 60 }} src={Canvas} />
              </a>
            </td>
            <td>
              <a href="https://mail.google.com/">
                <img alt="Gmail" style={{ width: 60, paddingTop: "8px" }} src={Gmail} />
              </a>
            </td>
            <td>
              <a href="https://calendar.google.com/">
                <img alt="GCal" style={{ width: 60 }} src={GCal} />
              </a>
            </td>
            <td>
              <a href="https://docs.google.com/">
                <img alt="Docs" style={{ width: 60 }} src={Docs} />
              </a>
            </td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default SneakyLinksTable;
