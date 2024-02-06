/* global _gaq */
import Table from "react-bootstrap/Table";
import Canvas from "../images/canvas.png";
import Docs from "../images/google-docs.png";
import Gmail from "../images/gmail.png";
import GCal from "../images/gcal.png";

function SneakyLinksTable() {
  function trackClick(e) {
    _gaq.push(['_trackEvent', e.target.id, 'clicked']);
  };

  return (
    <div className="sneaky-links">
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
            <td style={{textAlign: "center"}}>
              <a href="https://canvas.princeton.edu/" onClick={trackClick}>
                <img id="canvas" alt="Canvas" style={{ width: 56 }} src={Canvas} />
              </a>
            </td>
            <td style={{textAlign: "center"}}>
              <a href="https://mail.google.com/" onClick={trackClick}>
                <img id="gmail" alt="Gmail" style={{ width: 56, paddingTop: "8px" }} src={Gmail} />
              </a>
            </td>
            <td style={{textAlign: "center"}}>
              <a href="https://calendar.google.com/" onClick={trackClick}>
                <img id="gcal" alt="GCal" style={{ width: 56 }} src={GCal} />
              </a>
            </td>
            <td style={{textAlign: "center"}}>
              <a href="https://docs.google.com/" onClick={trackClick}>
                <img id="docs" alt="Docs" style={{ width: 56 }} src={Docs} />
              </a>
            </td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default SneakyLinksTable;
