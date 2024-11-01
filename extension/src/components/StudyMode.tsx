import React, { useState, useRef, useEffect } from "react";
import StudyModeTimer from "./StudyModeTimer";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGear , faMusic , faExpand, faCalculator , faKiwiBird } from "@fortawesome/free-solid-svg-icons"; // faBookOpen, faHouse,
import background1 from "../images/study/catandbook.jpeg"
import background2 from "../images/study/catseat.jpeg"
import background3 from "../images/study/flowerfield.jpeg"
import background4 from "../images/study/forestfield.jpeg"
import background5 from "../images/study/layinginsun.jpeg"
import duckgif from "../images/walkingduck.gif"
import { EventTypes, useMixpanel } from "../context/MixpanelContext";
// import { useStorage } from "../context/StorageContext";

import Table from "react-bootstrap/Table";
// import WidgetHeader from "./widget/WidgetHeader";


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
  const [showDuck, setShowDuck] = useState(false);
  // const [playlistUrl, setPlaylistUrl] = useState("https://open.spotify.com/embed/playlist/37i9dQZF1DX8Uebhn9wzrS?utm_source=generator&theme=0");


  const popupRef = useRef<HTMLDivElement>(null);
  const settingsButtonRef = useRef<HTMLButtonElement>(null);
  const [isImageLoaded, setIsImageLoaded] = useState(false);


  // List of background images
  const backgrounds = [
    [background1, "#5f5b69"],
    [background2, "#b2293d"],
    [background3, "#fee594"],
    [background4, "#8dae35"],
    [background5, "#e6c2a0"]
  ];

  // const storage = useStorage()
  const mixpanel = useMixpanel()


  // Preload all images once on component mount
  useEffect(() => {
    backgrounds.forEach((background) => {
      const img = new Image();
      img.src = background[0];
    });
  },[]);

  useEffect(() => {
    if (isStudyMode) {
      const img = new Image();
      img.src = overlayBG;
      img.onload = () => setIsImageLoaded(true);
    } else {
      setIsImageLoaded(false);
    }
  }, [isStudyMode, overlayBG]);

  const toggleDuck = () => {
    setShowDuck((prev) => !prev);
    if (!showDuck) {
      mixpanel.trackEvent(EventTypes.SHOW_DUCK, "duck")
    }
  };

  const toggleFullScreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
    setIsFullScreen(!isFullScreen);
    if (!isFullScreen) {
      mixpanel.trackEvent(EventTypes.FULL_SCREEN, "full screen")
    }
  };

  const toggleCalculator = () => {
    setShowCalculator((prev) => !prev);
    if (!showCalculator) {
      mixpanel.trackEvent(EventTypes.SHOW_CALC, "calculator")
    }
  }

  const handleToggle = () => {
    const newMode = !isStudyMode;
    setIsStudyMode(newMode);
    toggleWidgets(newMode);
    setShowSettings(false);
    mixpanel.trackEvent(EventTypes.OPENED_STUDYMODE, "studymode")
  };

  const toggleSettingsPopup = () => {
    // Close the popup if it’s already open, otherwise open it
    setShowSettings((prev) => !prev);
  };

  const toggleSpotify = () => {
    setShowSpotify((prev) => !prev); 
    if (!showSpotify) {
      mixpanel.trackEvent(EventTypes.SHOW_SPOTIFY, "spotify")
    }
  };

  const handleBackgroundChange = (background: string) => {
    setIsImageLoaded(false); // Set loading state
    const img = new Image();
    img.src = background;
    img.onload = () => {
      setOverlayBG(background); // Update background once loaded
      setIsImageLoaded(true); // Reset loading state
    };
    mixpanel.trackEvent(EventTypes.CHANGED_STUDYBG, background)
  };

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
          alignContent:"center",
          justifyItems:"center"
        }}
      >

        <StudyModeTimer />
      </div>
      )}

      {/* Main content with widgets */}
      <div style={{ position: "relative", zIndex: 1 }}>
        {isStudyMode && (
          <>
            <button onClick={toggleDuck} className="study-mode-button">
                <FontAwesomeIcon icon={faKiwiBird} size="2x" />
            </button>
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
                <div className ="color-options">
                {backgrounds.map(([bg, color]) => (
                   <button
                     className="color-btn"
                     style={{ backgroundColor: color }}
                     onClick={(event) => handleBackgroundChange(bg)}
                   />
                 ))}
                </div>
              </div>
            )}
          </>
        )}

<div className="sneaky-links">

      <Table variant="dark" borderless>
        <tbody>
          {/* Main Study Mode Toggle Button */}
        <button onClick={handleToggle} className="study-mode-button">
          {/* <FontAwesomeIcon icon={isStudyMode ? faHouse : faBookOpen} size="2x" /> */}
          <h2>study mode</h2>
        </button>
          
        </tbody>
      </Table>
        </div>



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
      
      {(isStudyMode && showDuck) && (
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
         <img src={duckgif} alt="Moving Duck" width="50" />
       </div>
      )}
      {/* {(isStudyMode) && ()} */}
    </>
  );
}

export default StudyMode;
