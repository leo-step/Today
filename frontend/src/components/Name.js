import { useState } from "react";

function Name() {
  const [text, setText] = useState(window.localStorage.getItem("name") || "[name]");
  
  window.onload = () => {
    if (window.localStorage.getItem("cancelCount") == null) {
        window.localStorage.setItem("cancelCount", 0)
    }
    let cancelCount = parseInt(window.localStorage.getItem("cancelCount"));
    let currentName = window.localStorage.getItem("name");
    if ((currentName == null || currentName === "") && cancelCount < 2) {
        const name = prompt("Please enter your name:");
        if (name == null || name === "") {
            cancelCount += 1
            window.localStorage.setItem("cancelCount", cancelCount);
        } else {
            window.localStorage.setItem("name", name);
            window.localStorage.setItem("cancelCount", 0);
            setText(name);
        }
    }
    if (cancelCount >= 2) {
        window.localStorage.setItem("name", "");
        setText("");
    }
  };

  return (
    <span>
      {text}
    </span>
  );
}

export default Name;
