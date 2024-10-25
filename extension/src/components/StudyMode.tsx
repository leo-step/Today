import React, { useState } from "react";
import Button from 'react-bootstrap/Button';

interface StudyModeProps {
  toggleWidgets: (show: boolean) => void;
}

function StudyMode({ toggleWidgets }: StudyModeProps) {
  const [isStudyMode, setIsStudyMode] = useState(false);

  const handleToggleStudyMode = () => {
    setIsStudyMode(!isStudyMode);
    toggleWidgets(!isStudyMode); // Toggle widget visibility
  };

  return (
    <>
      <Button variant="outline-light" onClick={handleToggleStudyMode}>
        <strong>{isStudyMode ? "Exit Study Mode" : "Enter Study Mode"}</strong>
      </Button>
    </>
  );
}

export default StudyMode;
