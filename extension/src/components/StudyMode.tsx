// TODO: MAKE IT SO THAT WHEN YOU SET A TIME, THEN IT RESETS
import React, { useState, useRef, useEffect } from "react";
import StudyModeTimer from "./StudyModeTimer";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGear , faMusic , faExpand, faCalculator , faKiwiBird , faHouse } from "@fortawesome/free-solid-svg-icons"; // faBookOpen, faHouse,
import background1 from "../images/study/catandbook.jpeg"
import background2 from "../images/study/catseat.jpeg"
import background3 from "../images/study/flowerfield.jpeg"
import background4 from "../images/study/forestfield.jpeg"
import background5 from "../images/study/layinginsun.jpeg"
import duckgif from "../images/walkingduck.gif"
import { EventTypes, useMixpanel } from "../context/MixpanelContext";
import { useAtom } from "jotai";
import { timerState, timerReset} from "./study_mode_state";
// import { useStorage } from "../context/StorageContext";

// import WidgetHeader from "./widget/WidgetHeader";
import Button from 'react-bootstrap/Button';
// import { ToggleButton } from "react-bootstrap";


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
  const [showColors, setShowColors] = useState(true);
  const popupRef = useRef<HTMLDivElement>(null);
  const settingsButtonRef = useRef<HTMLButtonElement>(null);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [timerNumber, setTimerNumber] = useAtom(timerState);
  const [hours, setHours] = useState<number | string>(Math.floor(timerNumber / 3600));
  const [minutes, setMinutes] = useState<number | string>((timerNumber / 60) % 60);
  const [timerResetState, setTimerReset] = useAtom(timerReset);
  // List of background images
  const backgrounds = [
    [background1, "#5f5b69", "Cat on lawn"],
    [background2, "#b2293d", "Cat in the city"],
    [background3, "#ADD8E6", "Flower field"],
    [background4, "#8dae35", "Enchanted forest"],
    [background5, "#e6c2a0", "Lakeside view"]
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
  const showBackgroundColors = () => {
    setShowColors(true);
  }
  const showTimerSettings = () => {
    setShowColors(false);
  }
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

  // const handleBlur = (
  //   value: string | number,
  //   setValue: React.Dispatch<React.SetStateAction<number | string>>
  // ) => {
  //   if (value === "" || value === "-" || value === 0) {
  //     setValue(""); // Reset to 0 if empty or invalid
  //   }
  // };

  // const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  //   e.preventDefault();
  //   const totalTime = Number(hours) * 3600 + Number(minutes) * 60;
  //   setTimerNumber(totalTime);
  //   console.log(totalTime);
  // };
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Convert hours and minutes to seconds and save to the atom
    const totalTime = Number(hours) * 3600 + Number(minutes) * 60;
    setTimerNumber(totalTime);
    console.log(timerResetState); // Update the atom
    setTimerReset(true);
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

  // useEffect(() => {
  //   // Sync local `hours` and `minutes` state with `timerNumber` when it changes
  //   setHours(Math.floor(timerNumber / 3600));
  //   setMinutes((timerNumber % 3600) / 60);
  // }, [timerNumber]);

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

  const handleFocus = (
    setValue: React.Dispatch<React.SetStateAction<number | string>>
  ) => {
    setValue(""); // Clear the field when focused
  };
  
  const handleBlur = (
    value: string | number,
    setValue: React.Dispatch<React.SetStateAction<number | string>>
  ) => {
    if (value === "" || isNaN(Number(value))) {
      setValue(0); // Reset to 0 if empty or invalid
    }
  };
  return (
    <div style={{height:"90vh", width:"100vw"}}>
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
      </div>
      )}

      {/* Main content with widgets */}
      {/* Popup for background color selection */}
      <div style={{ position: "relative", zIndex: 1, justifySelf:"right"}}>
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
            {/* Turn off study mode */}
            <button onClick={handleToggle} className="study-mode-button">
                <FontAwesomeIcon icon={faHouse} size="2x" />
            </button>
          </>
        )}
          {/* Main Study Mode Toggle Button */}
          { !isStudyMode && (
            <Button variant="outline-light" className="study-mode-toggle" onClick={handleToggle}>
              <b>study mode</b>
            </Button>
          )}
          
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
      {(isStudyMode) && 
      (
        <div style={{position: "fixed", top:"25%", right:"25%", zIndex: 0, justifySelf:"center", alignSelf:"center", alignContent:"center", justifyItems:"center"}}>
        <StudyModeTimer />
      </div>
      )}
      {showSettings && (
        <div ref={popupRef} className="settings-popup">
          <button 
            className="settings-close-button" 
            onClick={() => setShowSettings(false)}
          >
            &times;
          </button>
          <div className = "settings-sidebar">
          <button className = "settings-side-button" onClick={showBackgroundColors}>Backgrounds</button>
          <button className = "settings-side-button" onClick={showTimerSettings}>Set Timer</button>
          </div>
          <div className = "settings-box">
            {showColors && <div className="color-options">
              {backgrounds.map(([bg, color, desc], index) => (
                <button
                  key={index}
                  className="color-btn-rect"
                  style={{
                    backgroundColor: color,
                    color: "#ffffff", // Ensure text is readable
                    width: "200px",
                    height: "50px",
                    margin: "10px 0", // Add spacing between buttons
                    fontSize: "16px",
                    border: "1px solid #000",
                    borderRadius: "8px",
                    cursor: "pointer",
                    textAlign: "center",
                  }}
                  onClick={() => handleBackgroundChange(bg)}
                >
                  {desc} {/* Placeholder text */}
                </button>
              ))}
            </div>}
            {!showColors && <div className ="timer-settings">
              <br/>
              <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", maxWidth: "300px" }}>
                <label>
                  Hours:
                  <input
                    type="text" // Use text for full control over input
                    value={hours}
                    onChange={(e) => {
                      const value = e.target.value;
                      // Remove any non-numeric characters (including negative signs)
                      const sanitizedValue = value.replace(/[^0-9]/g, "");
                      // Ensure the value is at most 2 digits
                      if (sanitizedValue.length <= 2 && Number(sanitizedValue) <= 59) {
                        setHours(sanitizedValue);
                      }
                    }}
                    onFocus={() => handleFocus(setHours)}
                    onBlur={() => handleBlur(hours, setHours)}
                  />
                </label>
                <label>
                  Minutes:
                  <input
                    type="text" // Use text for full control over input
                    value={minutes}
                    onChange={(e) => {
                      const value = e.target.value;
                      // Remove any non-numeric characters (including negative signs)
                      const sanitizedValue = value.replace(/[^0-9]/g, "");
                      // Ensure the value is at most 2 digits
                      if (sanitizedValue.length <= 2 && Number(sanitizedValue) <= 59) {
                        setMinutes(sanitizedValue);
                      }
                    }}
                    onFocus={() => handleFocus(setMinutes)}
                    onBlur={() => handleBlur(minutes, setMinutes)}
                  />
                </label>
                <button type="submit" className="settings-submit">Save</button>
              </form>


            </div>}
          </div>
        </div>
      )}

    </div>
    
  );
}

export default StudyMode;
