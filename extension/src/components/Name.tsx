import { useState } from "react";
import React from "react";
import { StorageKeys, useStorage } from "../context/StorageContext";
import { EventTypes, useMixpanel } from "../context/MixpanelContext";
import { Button, Form, Modal } from "react-bootstrap";
import ConfettiExplosion from 'react-confetti-explosion';

function Name() {
  const storage = useStorage();
  const mixpanel = useMixpanel();

  const [text, setText] = useState(
    storage.getLocalStorageDefault(StorageKeys.NAME, "")
  );
  const [inputValue, setInputValue] = useState(
    storage.getLocalStorageDefault(StorageKeys.NAME, "")
  );
  const [showPopup, setShowPopup] = useState(text === "");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const name = inputValue;
    if (name !== "") {
      storage.setLocalStorage(StorageKeys.NAME, name);
      setText(name);
      setShowPopup(false);
      mixpanel.trackEvent(EventTypes.NAME_CHANGE, name);
    }
  };

  return (
    <span>
      <span className="name" onClick={() => setShowPopup(true)}>
        {text}
      </span>
      <Modal show={showPopup} onHide={() => setShowPopup(false)} centered>
        <Modal.Header>
          <Modal.Title>🎉 Thank you for downloading Today!</Modal.Title>
          {showPopup && <ConfettiExplosion zIndex={1200}/>}
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formName">
              <Form.Label>To get started, please enter your name:</Form.Label>
              <Form.Control
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                placeholder="Enter your name"
              />
              {showPopup && <ConfettiExplosion zIndex={1200}/>}
            </Form.Group>
            <Button
              variant="primary"
              type="submit"
              className="mt-3"
              disabled={!inputValue}
            >
              Submit
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </span>
  );
}

export default Name;
