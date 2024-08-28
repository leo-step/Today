import Table from "react-bootstrap/Table";
import React from "react";
import Tay from "../images/tay.png"
import { useState } from "react";
import SlidingPane from "react-sliding-pane";
// import Typewriter from 'typewriter-effect';
import { StorageKeys, useStorage } from "../context/StorageContext";
// import { Button } from "react-bootstrap";

function Chat() {
  const [isPaneOpen, setPaneOpen] = useState(false)
  const storage = useStorage()

  return (
    <div className={"weather"}>
      <Table variant="dark" borderless style={{marginBottom: 16}}>
        <tbody>
          <tr>
            <th style={{width: "25%"}}></th>
            <th></th>
            <th></th>
            <th></th>
          </tr>
          <tr>
            <td colSpan={1}>
              <img src={Tay} width={120}/>
            </td>
            <td colSpan={3}>
              Hello world
            </td>
          </tr>
          {/* <Button onClick={() => setPaneOpen(!isPaneOpen)}>Open</Button> */}
        </tbody>
      </Table>
      <SlidingPane
        isOpen={isPaneOpen}
        onRequestClose={() => {
          setPaneOpen(false);
        }}
        width="640px"
      >
        <iframe 
          src={`http://localhost:5173?uuid=${storage.getLocalStorage(StorageKeys.UUID)}`}
          width="100%" 
          height="100%" 
          style={{ border: 'none' }} 
        />
      </SlidingPane>
    </div>
  );
}

export default Chat;
