import Table from "react-bootstrap/Table";
import React from "react";
import Tay from "../images/tay.png";
import { useState } from "react";
import SlidingPane from "react-sliding-pane";
// import Typewriter from 'typewriter-effect';
import { StorageKeys, useStorage } from "../context/StorageContext";
import { Form } from "react-bootstrap";
import { Button } from "react-bootstrap";
import { FiSend } from "react-icons/fi";
import config from "../config";

function Chat() {
  const storage = useStorage();

  const [isPaneOpen, setPaneOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [query, setQuery] = useState('');

  const handleSubmit = (e: any) => {
    e.preventDefault();
    setQuery(inputValue);
    setInputValue('');
    setPaneOpen(true);
  };

  return (
    <div className={"weather flow-border"}>
      <Table variant="dark" borderless style={{ marginBottom: 24 }}>
        <tbody>
          <tr>
            <th style={{ width: "30%" }}></th>
            <th></th>
            <th></th>
            <th></th>
          </tr>
          <tr>
            <td colSpan={1} style={{ verticalAlign: "middle" }}>
              <img
                id="tay-img"
                src={Tay}
                style={{ width: "100%" }}
                onClick={() => setPaneOpen(true)}
              />
            </td>
            <td colSpan={3} id="chat-cell">
              <Form
                onSubmit={handleSubmit}
              >
                <Form.Group>
                  <Form.Label>
                    Hey! My name is Tay, and I'm an AI assistant.
                  </Form.Label>
                  <Form.Control
                    type="text"
                    id="chat-input"
                    placeholder="Ask me anything about Princeton"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                  />
                  <Button
                    variant="primary"
                    id="chat-button"
                    type="submit"
                  >
                    <FiSend />
                  </Button>
                </Form.Group>
              </Form>
            </td>
          </tr>
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
          src={config.URL + `?uuid=${storage.getLocalStorage(
            StorageKeys.UUID
          )}&query=${query}`}
          width="100%"
          height="100%"
          style={{ border: "none" }}
        />
      </SlidingPane>
    </div>
  );
}

export default Chat;
