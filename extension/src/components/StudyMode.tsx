import React, { useState, useRef, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBookOpen, faHouse, faGear , faMusic , faExpand} from "@fortawesome/free-solid-svg-icons";

interface StudyModeProps {
  toggleWidgets: (show: boolean) => void;
}

function StudyMode({ toggleWidgets }: StudyModeProps) {
  const [isStudyMode, setIsStudyMode] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [overlayColor, setOverlayColor] = useState("#FFDAB9"); // Default pastel orange
  const [showSpotify, setShowSpotify] = useState(true);
  const [isFullScreen, setIsFullScreen] = useState(false);

  const popupRef = useRef<HTMLDivElement>(null);
  const settingsButtonRef = useRef<HTMLButtonElement>(null);

  const toggleFullScreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
    setIsFullScreen(!isFullScreen);
  };

  const handleToggle = () => {
    const newMode = !isStudyMode;
    setIsStudyMode(newMode);
    toggleWidgets(newMode);
  };

  const toggleSettingsPopup = () => {
    // Close the popup if it’s already open, otherwise open it
    setShowSettings((prev) => !prev);
  };

  const toggleSpotify = () => {
    setShowSpotify((prev) => !prev); // Toggle Spotify visibility
  };

  const handleColorChange = (color: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setOverlayColor(color);
    // setShowSettings(false);
  };


  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        showSettings &&
        popupRef.current &&
        !popupRef.current.contains(event.target as Node) &&
        settingsButtonRef.current &&
        !settingsButtonRef.current.contains(event.target as Node)
      ) {
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
            {/* Full screen button */}
            <button onClick={toggleFullScreen} className="study-mode-button">
                <FontAwesomeIcon icon={faExpand} size="2x" />
            </button>
            {/* Toggle Button for Spotify Widget */}
            <button onClick={toggleSpotify} className="study-mode-button">
              <FontAwesomeIcon icon={faMusic} size="2x" />
            </button>
            {/* Settings Icon */}
            <button ref={settingsButtonRef} onClick={toggleSettingsPopup} className="study-mode-button">
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
        {/* Spotify Lofi Music Widget */}
      {isStudyMode && (
      <div className="spotify-widget" style={{ display: showSpotify ? "block" : "none" }}>
      <iframe
        style={{ borderRadius: "12px" }}
        src="https://open.spotify.com/embed/playlist/37i9dQZF1DX8Uebhn9wzrS?utm_source=generator&theme=0"
        width="100%"
        height="152"
        frameBorder="0"
        allowFullScreen={true}
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
        loading="lazy"
        title="Spotify Lofi Playlist"
      ></iframe>
    </div>
      )}
      </div>
      
    </>
  );
}

export default StudyMode;
