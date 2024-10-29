import React, { useState, useRef, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBookOpen, faHouse, faGear , faMusic , faExpand, faCalculator} from "@fortawesome/free-solid-svg-icons";
import background1 from "../images/study/catandbook.jpeg"
import background2 from "../images/study/catseat.jpeg"
import background3 from "../images/study/flowerfield.jpeg"
import background4 from "../images/study/forestfield.jpeg"
import background5 from "../images/study/layinginsun.jpeg"


interface StudyModeProps {
  toggleWidgets: (show: boolean) => void;
}

function StudyMode({ toggleWidgets }: StudyModeProps) {
  const [isStudyMode, setIsStudyMode] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [overlayBG, setOverlayBG] = useState(background1); // Default pastel orange
  const [showSpotify, setShowSpotify] = useState(true);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [duckPosition, setDuckPosition] = useState(0);
  const [movingRight, setMovingRight] = useState(true);
  const [showCalculator, setShowCalculator] = useState(false);


  const popupRef = useRef<HTMLDivElement>(null);
  const settingsButtonRef = useRef<HTMLButtonElement>(null);

  const [isImageLoaded, setIsImageLoaded] = useState(false);

  useEffect(() => {
    if (isStudyMode) {
      const img = new Image();
      img.src = overlayBG;
      img.onload = () => setIsImageLoaded(true);
    } else {
      setIsImageLoaded(false);
    }
  }, [isStudyMode, overlayBG]);


  const toggleFullScreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
    setIsFullScreen(!isFullScreen);
  };

  const toggleCalculator = () => {
    setShowCalculator((prev) => !prev);
  }

  const handleToggle = () => {
    const newMode = !isStudyMode;
    setIsStudyMode(newMode);
    toggleWidgets(newMode);
    setShowSettings(false); // Reset settings popup on toggle
  };

  const toggleSettingsPopup = () => {
    // Close the popup if it’s already open, otherwise open it
    setShowSettings((prev) => !prev);
  };

  const toggleSpotify = () => {
    setShowSpotify((prev) => !prev); // Toggle Spotify visibility
  };

  const handleBackgroundChange = (background: string) => {
    setOverlayBG(background);
  }


  useEffect(() => {
    if (isStudyMode) {
      const screenWidth = window.innerWidth;
      const duckWidth = 50; // Set the width of the duck in pixels
      const interval = setInterval(() => {
        setDuckPosition((prev) => {
          const movementSpeed = 0.6;  // HOW FAST THE DUCK GOES
          let newPosition = movingRight ? prev + movementSpeed : prev - movementSpeed;
  
          if (newPosition >= screenWidth - duckWidth) {
            setMovingRight(false);
          } else if (newPosition <= 0) {
            setMovingRight(true);
          }

          return newPosition;
        });
      }, 20);

      return () => clearInterval(interval);
    }
  }, [isStudyMode, movingRight]);
  
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
      {isStudyMode && (
        <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          backgroundImage: `url(${overlayBG})`,
          backgroundColor: isImageLoaded ? "transparent" : "#f0f0f0", // Placeholder color
          backgroundSize: "cover",
          backgroundPosition: "center",
          transition: "opacity 0.5s ease",
          opacity: isImageLoaded ? 1 : 0,
          zIndex: 0,
          pointerEvents: "none",
        }}
      ></div>
      )}

      {/* Main content with widgets */}
      <div style={{ position: "relative", zIndex: 1 }}>
        {isStudyMode && (
          <>
            {/* Full screen button */}
            <button onClick={toggleCalculator} className="study-mode-button">
                <FontAwesomeIcon icon={faCalculator} size="2x" />
            </button>
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
                    onClick={(event) => handleBackgroundChange(background1)}
                  />
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#ffd1dc" }} // Pastel Pink
                    onClick={(event) => handleBackgroundChange(background2)}
                  />
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#C1CFA1" }} // Pastel green
                    onClick={(event) => handleBackgroundChange(background3)}
                  />
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#FFDAB9" }} // Pastel Orange
                    onClick={(event) => handleBackgroundChange(background4)}
                  />
                  <button
                    className="color-btn"
                    style={{ backgroundColor: "#D3D3D3" }} // Soft Black
                    onClick={(event) => handleBackgroundChange(background5)}
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
      {isStudyMode && (
      <div className="calc-container">
        <div className={`calc-widget ${showCalculator ? "show" : ""}`}>
          <iframe
            src="https://www.desmos.com/scientific"
            name="calcIFrame"
            width="100%"
            height="100%"
            style={{ border: "none" }}
          ></iframe>
        </div>
      </div>
      )}
      
      {isStudyMode && (
         <div
         className="moving-duck"
         style={{
           position: "fixed",
           bottom: 0,
           left: `${duckPosition}px`,
           transform: movingRight ? "scaleX(1)" : "scaleX(-1)",
           transition: "left 0.02s linear",
         }}
       >
         <img src="https://cdn.discordapp.com/attachments/1278115008504533115/1300285590956282018/duck.gif?ex=672048d3&is=671ef753&hm=0c2045524d34f8017e68c9d9d27f119292720c81e407792269df43c4c775ca5f&" alt="Moving Duck" width="50" />
       </div>
      )}
    </>
  );
}

export default StudyMode;
