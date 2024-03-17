import Table from "react-bootstrap/Table";
import Form from 'react-bootstrap/Form';
import Tay from "../images/tay.png"
import Button from "react-bootstrap/Button"

function Chatbot() {
  return (
    <div className={"tay"}>
      <Table variant="dark" borderless>
        <tbody>
          {/* <tr>
            <td colSpan={3}>
              {" "}
              <h3 style={{fontWeight: "bold"}}>Weather</h3>{" "}
            </td>
            <td colSpan={2} className="centered">
              {" "}
            </td>
          </tr> */}
          
          <tr>
            <td colSpan={1} style={{ width: 160}}>
              <img alt="Tay" style={{ width: 160}} src={Tay} />
            </td>
            <td colSpan={2}>
              <Form>
                <Form.Group className="m-2" style={{ width: 320}}>
                  <Form.Label style={{fontSize: 36, marginBottom: 12}}>Chat with Tay</Form.Label>
                  <div>
                    <Form.Control type="text" placeholder="What's on your mind today?" style={{width: 280, float: "left", 
                      borderTopRightRadius: 0, borderBottomRightRadius: 0}}/>
                    <Button style={{float: "right", borderTopLeftRadius: 0, borderBottomLeftRadius: 0}}>↑</Button>
                  </div>
                  
                </Form.Group>
              </Form>
            </td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default Chatbot;
