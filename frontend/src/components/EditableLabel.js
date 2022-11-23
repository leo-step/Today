import { useState, useEffect } from "react";

function EditableLabel(props) {
  const [text, setText] = useState(props.value);
  const [editing, setEditing] = useState(false);
  const [editor, setEditor] = useState(null);

  useEffect(() => {
    setEditor(
      <input
        type="text"
        size="8"
        onKeyPress={(event) => {
          console.log(event);
          if (event.key === "Enter") {
            // enter key
            console.log("pressed enter");
            setText(event.target.value);
            setEditing(false);
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
