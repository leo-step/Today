/* global chrome */

import { useState, useEffect } from "react";

function EditableLabel(props) {
  const [text, setText] = useState(props.value);
  const [editing, setEditing] = useState(false);
  const [editor, setEditor] = useState(null);

  useEffect(() => {
    chrome.storage.sync.get(["name"], (result) => {
      if (result.name) {
        setText(result.name);
      }
      else {
        setText("_______");
      }
      setEditor(
        <input
          type="text"
          size="8"
          defaultValue={result.name}
          onKeyPress={(event) => {
            if (event.key === "Enter") {
              // enter key
              let enteredValue = event.target.value;
              if (enteredValue === "") {
                enteredValue = props.value;
              }
              console.log("name:", enteredValue);
              
              setText(enteredValue);
              setEditing(false);
              chrome.storage.sync.set({name: enteredValue}, function() {
                console.log('Name is set to ' + enteredValue);
              });
            }
          }}
          autoFocus={true}
          style={{
            backgroundColor: "transparent",
            color: "white",
            fontWeight: "bold",
          }}
        />
      );
    });
  }, []);

  return editing ? (
    editor
  ) : (
    <span
      onClick={() => {
        setEditing(true);
      }}
    >
      {text}
    </span>
  );
}

export default EditableLabel;
