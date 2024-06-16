/* global _gaq */
import Table from "react-bootstrap/Table";
import Disiac from "../images/disiac.jpg";

function Dance() {
  function trackClick(e) {
    _gaq.push(['_trackEvent', e.target.id, 'clicked']);
  };

  return (
    <div class="dance">
      <Table variant="dark" borderless>
        <tbody>
          <tr>
            <td style={{textAlign: "center"}}>
              <a href="https://tickets.princeton.edu/" onClick={trackClick}>
                <img id="disiac" className="promo" alt="disiac" src={Disiac} />
              </a>
            </td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default Dance;
