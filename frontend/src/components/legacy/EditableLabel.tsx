import { useState, useEffect } from "react";
import React from "react";

function EditableLabel() {
  const [text, setText] = useState(
    window.localStorage.getItem("name") || "[enter name]"
  );
  const [editing, setEditing] = useState(false);
  const [editor, setEditor] = useState<React.ReactNode>(null);

  useEffect(() => {
    const result = { name: window.localStorage.getItem("name") };
    if (result.name) {
      setText(result.name);
    }
    setEditor(
      <input
        type="text"
        size={8}
        defaultValue={result.name as any}
        onKeyPress={(event) => {
          if (event.key === "Enter") {
            let enteredValue = (event.target as any).value;
            setText(enteredValue ? enteredValue : "[enter name]");
            setEditing(false);
            window.localStorage.setItem("name", enteredValue);
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
