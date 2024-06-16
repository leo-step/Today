import Table from "react-bootstrap/Table";
import React from "react";
import Disiac from "../images/disiac.jpg";

function Dance() {
  return (
    <div className="dance">
      <Table variant="dark" borderless>
        <tbody>
          <tr>
            <td style={{ textAlign: "center" }}>
              <a href="https://tickets.princeton.edu/">
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
