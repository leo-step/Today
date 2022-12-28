import { useState, useEffect } from "react";

function EditableLabel() {
  const [text, setText] = useState(window.localStorage.getItem("name") || "_______");
  const [editing, setEditing] = useState(false);
  const [editor, setEditor] = useState(null);

  useEffect(() => {
    const result = {name: window.localStorage.getItem("name")};
    if (result.name) {
      setText(result.name);
    }
    setEditor(
      <input
        type="text"
        size="8"
        defaultValue={result.name}
        onKeyPress={(event) => {
          if (event.key === "Enter") {
            let enteredValue = event.target.value;
            setText(enteredValue ? enteredValue : "_______");
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
