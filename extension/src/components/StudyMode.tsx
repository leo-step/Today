import React, { useState, useRef, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBookOpen, faHouse, faGear } from "@fortawesome/free-solid-svg-icons";

interface StudyModeProps {
  toggleWidgets: (show: boolean) => void;
}

function StudyMode({ toggleWidgets }: StudyModeProps) {
  const [isStudyMode, setIsStudyMode] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [overlayColor, setOverlayColor] = useState("#FFDAB9"); // Default pastel orange
  const popupRef = useRef<HTMLDivElement>(null);

  const handleToggle = () => {
    const newMode = !isStudyMode;
    setIsStudyMode(newMode);
    toggleWidgets(newMode);
  };

  const toggleSettingsPopup = () => {
    setShowSettings((prev) => !prev);
  };

  const handleColorChange = (color: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setOverlayColor(color);
    setShowSettings(false);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(event.target as Node)) {
        setShowSettings(false);
      }
    };

    if (showSettings) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }

    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showSettings]);

  return (
    <>
      {/* Overlay with smooth transition */}
      <div className={`overlay ${isStudyMode ? "overlay-visible" : ""}`} style={{ backgroundColor: overlayColor }}></div>

      {/* Main content with widgets */}
      <div style={{ position: "relative", zIndex: 1 }}>
        {isStudyMode && (
          <>
            {/* Settings Icon */}
            <button onClick={toggleSettingsPopup} className="study-mode-button">
              <FontAwesomeIcon icon={faGear} size="2x" />
            </button>

            {/* Popup for background color selection */}
            {showSettings && (
              <div ref={popupRef} className="settings-popup">
                <div className="color-options">
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#AEC6CF" }} // Pastel Blue
                    onClick={(event) => handleColorChange("#AEC6CF", event)}
                  />
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#FFB6C1" }} // Pastel Pink
                    onClick={(event) => handleColorChange("#FFB6C1", event)}
                  />
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#FFDAB9" }} // Pastel Orange
                    onClick={(event) => handleColorChange("#FFDAB9", event)}
                  />
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#D3D3D3" }} // Soft Black
                    onClick={(event) => handleColorChange("#D3D3D3", event)}
                  />
                </div>
              </div>
            )}
          </>
        )}

        {/* Main Study Mode Toggle Button */}
        <button onClick={handleToggle} className="study-mode-button">
          <FontAwesomeIcon icon={isStudyMode ? faHouse : faBookOpen} size="2x" />
        </button>
      </div>
    </>
  );
}

export default StudyMode;
