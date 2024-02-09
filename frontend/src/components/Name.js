import { useState } from "react";

function Name() {
  const [text, setText] = useState(window.localStorage.getItem("name") || "[name]");
  const [inputValue, setInputValue] = useState(window.localStorage.getItem("name"));
  const [showPopup, setShowPopup] = useState(false);
  
  window.onload = () => {
    if (window.localStorage.getItem("cancelCount") == null) {
        window.localStorage.setItem("cancelCount", 0)
    }
    let cancelCount = parseInt(window.localStorage.getItem("cancelCount"));
    let currentName = window.localStorage.getItem("name");
    if ((currentName == null || currentName === "") && cancelCount < 2) {
        setShowPopup(true);
        
    }
    if (cancelCount >= 2) {
        window.localStorage.setItem("name", "");
        setText("");
    }
  };

  const handleInputChange = (e) => {
      setInputValue(e.target.value);
  };

  const handleSubmit = (e) => {
      e.preventDefault();
      const name = inputValue;
      let cancelCount = window.localStorage.getItem("cancelCount") || 0
      if (name == null || name === "") {
          cancelCount += 1
          window.localStorage.setItem("cancelCount", cancelCount);
      } else {
          window.localStorage.setItem("name", name);
          window.localStorage.setItem("cancelCount", 0);
          setText(name);
          setShowPopup(false);
      }
  };

  return (
    <span>
      <span style={{textDecoration: "underline white", 
                  textDecorationThickness: 3, textUnderlineOffset: 8}}
        onClick={() => setShowPopup(true)}
      >
          {text}
      </span>
      {/* <img alt="" style={{ width: 24, marginLeft: 4, marginTop: 54}} src={Pencil} /> */}
      {/* <span style={{fontSize: 24, marginLeft: 8}}>✏️</span> */}
      {showPopup && <div className="popup">
        <form onSubmit={handleSubmit}>
          <label>Please enter your name:&nbsp;&nbsp;</label>
          <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
          />
          <button type="submit">Submit</button>
        </form>
      </div>}
    </span>
  );
}

export default Name;
