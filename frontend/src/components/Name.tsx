import { useState } from "react";
import React from "react";

function Name() {
  const [text, setText] = useState(
    window.localStorage.getItem("name") || "[name]"
  );
  const [inputValue, setInputValue] = useState(
    window.localStorage.getItem("name")
  );
  const [showPopup, setShowPopup] = useState(false);

  window.onload = () => {
    let currentName = window.localStorage.getItem("name");
    if (currentName == null || currentName === "") {
      setShowPopup(true);
    }
  };

  const handleInputChange = (e: any) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e: any) => {
    e.preventDefault();
    const name = inputValue;
    if (!(name == null || name === "")) {
      window.localStorage.setItem("name", name);
      setText(name);
      setShowPopup(false);
    }
  };

  return (
    <span>
      <span
        style={{
          textDecoration: "underline white",
          textDecorationThickness: 3,
          textUnderlineOffset: 8,
        }}
        onClick={() => setShowPopup(true)}
      >
        {text}
      </span>
      {/* <img alt="" style={{ width: 24, marginLeft: 4, marginTop: 54}} src={Pencil} /> */}
      {/* <span style={{fontSize: 24, marginLeft: 8}}>✏️</span> */}
      {showPopup && (
        <div className="popup">
          <form onSubmit={handleSubmit}>
            <label>Please enter your name:&nbsp;&nbsp;</label>
            <input
              type="text"
              value={inputValue as any}
              onChange={handleInputChange}
            />
            <button type="submit">Submit</button>
          </form>
        </div>
      )}
    </span>
  );
}

export default Name;
